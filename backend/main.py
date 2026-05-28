# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 — Windows charmap crash
# FastF1 emits emoji (📊) in its log output. Windows stdout uses cp1252 by
# default, which can't encode them → every fresh data-load crashes with:
#   'charmap' codec can't encode character '\U0001f4ca'
# Fix: reconfigure stdout/stderr to UTF-8 BEFORE any imports that trigger
# logging. Also set PYTHONIOENCODING so child processes inherit it.
# ─────────────────────────────────────────────────────────────────────────────
import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────────────────
# Standard imports (after encoding fix so FastF1 logging is safe)
# ─────────────────────────────────────────────────────────────────────────────
import json
import logging
import socket
import traceback
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

import fastf1
import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 (continued) — UTF-8 logging handler
# The default StreamHandler also uses the system codec. Replace it with one
# that explicitly uses UTF-8 so FastF1's emoji log lines don't crash the
# handler either.
# ─────────────────────────────────────────────────────────────────────────────
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

_utf8_handler = logging.StreamHandler(stream=sys.stdout)
_utf8_handler.setFormatter(
    logging.Formatter("%(asctime)s  %(levelname)-8s  %(name)s — %(message)s")
)
logging.basicConfig(handlers=[_utf8_handler], level=logging.INFO)
logger = logging.getLogger("the-grid")

# ─────────────────────────────────────────────────────────────────────────────
# FastF1 cache setup
# ─────────────────────────────────────────────────────────────────────────────
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR / "fastf1_raw"))

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────────────────────────────────────
from contextlib import asynccontextmanager
from scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(title="THE GRID API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _cache_path(year: int, race: str, session: str) -> Path:
    safe_race = race.replace(" ", "_").replace("/", "-")
    return CACHE_DIR / f"processed_{year}_{safe_race}_{session}.json"


from data_processor import process_session, check_session_available
from models import RaceDataPayload


# ─────────────────────────────────────────────────────────────────────────────
# API routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/race-data/{year}/{race}/{session}")
async def get_race_data(year: int, race: str, session: str):
    """
    Return processed race data.  Serves from JSON cache when available;
    processes fresh from FastF1 otherwise and writes the result to cache.

    session values: R (Race), Q (Qualifying), S (Sprint), SQ (Sprint Qualifying)
    """
    cache_file = _cache_path(year, race, session)

    if cache_file.exists():
        logger.info("Serving from cache: %s", cache_file)
        with cache_file.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    try:
        data = process_session(year, race, session)
        with cache_file.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        logger.info("Cached processed data to %s", cache_file)
        return data

    except Exception as exc:
        logger.error("Error processing %s %s %s:\n%s", year, race, session, traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load race data: {exc}"
        )


@app.get("/api/schedule/{year}")
async def get_schedule(year: int):
    """
    Return the full race calendar for a given year.
    Each entry includes whether processed cache data already exists.
    """
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        races = []
        for _, event in schedule.iterrows():
            name    = str(event.get("EventName", ""))
            country = str(event.get("Country", ""))
            loc     = str(event.get("Location", ""))
            date    = event.get("EventDate")
            fmt     = str(event.get("EventFormat", "conventional"))

            cached_sessions = {
                s: _cache_path(year, name, s).exists()
                for s in (["R", "Q", "S", "SQ"] if "sprint" in fmt.lower() else ["R", "Q"])
            }

            available = cached_sessions.get("R", False) or check_session_available(year, name, "R")

            races.append({
                "round":          int(event.get("RoundNumber", 0)),
                "name":           name,
                "country":        country,
                "location":       loc,
                "date":           date.isoformat() if hasattr(date, "isoformat") else str(date),
                "format":         fmt,
                "cachedSessions": cached_sessions,
                "completed":      (
                    hasattr(date, "date") and date.date() < datetime.utcnow().date()
                ),
                "available":      available,
            })
        return {"year": year, "races": races}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/refresh/{year}/{race}/{session}")
async def force_refresh(year: int, race: str, session: str):
    """
    Manually trigger data processing for a session and overwrite the cache.
    Useful for getting race data immediately after it finishes instead of waiting for the 6h background job.
    """
    cache_file = _cache_path(year, race, session)
    try:
        # Check if FastF1 has it available yet
        if not check_session_available(year, race, session):
            raise HTTPException(status_code=404, detail="Data not yet available on OpenF1")
            
        data = await asyncio.to_thread(process_session, year, race, session)
        with cache_file.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        logger.info("Manually refreshed cache for %s", cache_file)
        return {"status": "success", "message": f"Successfully refreshed data for {year} {race} {session}"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error manual refresh %s %s %s:\n%s", year, race, session, traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────────────────────────────────────
# FIX 2 — Windows port binding (WinError 10048)
# When the server is killed and restarted quickly, Windows keeps the socket in
# TIME_WAIT and refuses to bind again.  Setting SO_REUSEADDR on the socket
# resolves this.  The cleanest way with uvicorn is to pass a pre-bound socket.
# ─────────────────────────────────────────────────────────────────────────────

def _make_socket(host: str = "0.0.0.0", port: int = 8000) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # On Windows, SO_EXCLUSIVEADDRUSE prevents another process stealing the port
    # while still allowing our own restarts.
    if sys.platform == "win32":
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)  # type: ignore[attr-defined]
    sock.bind((host, port))
    return sock


if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    try:
        bound_sock = _make_socket(HOST, PORT)
        logger.info("THE GRID backend starting on http://%s:%d", HOST, PORT)
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info",
            # Pass the pre-bound socket so uvicorn doesn't try to bind again
            fd=bound_sock.fileno(),
        )
    except OSError as e:
        logger.error(
            "Cannot bind to port %d — another process is using it.\n"
            "Run:  netstat -ano | findstr :%d   then kill that PID.",
            PORT, PORT,
        )
        sys.exit(1)
