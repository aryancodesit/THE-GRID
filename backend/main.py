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
app = FastAPI(title="THE GRID API", version="2.0.0")

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


def _safe_val(val):
    """Convert numpy / pandas types to JSON-serialisable Python types."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, pd.Timedelta):
        return val.total_seconds()
    if isinstance(val, pd.Timestamp):
        return val.isoformat()
    return val


# ─────────────────────────────────────────────────────────────────────────────
# Core data-processing logic
# ─────────────────────────────────────────────────────────────────────────────

TYRE_COLOURS = {
    "SOFT": "#E8002D",
    "MEDIUM": "#FFF200",
    "HARD": "#FFFFFF",
    "INTERMEDIATE": "#39B54A",
    "WET": "#0067FF",
}

# FIX 3 — pick_driver is deprecated in FastF1 3.x; use pick_drivers instead.
# Wrapped in a helper so the fix is in one place and the rest of the code is clean.
def _get_driver_laps(session_laps, driver_abbr: str):
    """Return laps for a single driver using the current FastF1 3.x API."""
    return session_laps.pick_drivers(driver_abbr)


def _process_session(year: int, race: str, session_type: str) -> dict:
    """
    Load a FastF1 session and produce the processed JSON payload.
    Called only when there is no valid cache file.
    """
    logger.info("Loading %s %s %s from FastF1...", year, race, session_type)

    event = fastf1.get_event(year, race)
    session = event.get_session(session_type)
    session.load(
        telemetry=True,
        weather=True,
        messages=True,
        laps=True,
    )

    laps = session.laps
    total_laps = int(laps["LapNumber"].max()) if not laps.empty else 0

    logger.info(
        "Loaded %d laps for %d drivers",
        len(laps),
        laps["Driver"].nunique() if not laps.empty else 0,
    )

    drivers_out = []
    for abbr in session.drivers:
        try:
            drv_info = session.get_driver(abbr)
            # FIX 3 — pick_drivers (plural) not pick_driver
            drv_laps = _get_driver_laps(laps, abbr)

            lap_records = []
            for _, lap in drv_laps.iterrows():
                lap_num = _safe_val(lap.get("LapNumber"))
                if lap_num is None:
                    continue

                # Telemetry for this lap
                tel = {}
                try:
                    car_data = lap.get_car_data().add_distance()
                    if not car_data.empty:
                        tel = {
                            "speed":    [_safe_val(v) for v in car_data["Speed"].tolist()],
                            "gear":     [_safe_val(v) for v in car_data["nGear"].tolist()],
                            "throttle": [_safe_val(v) for v in car_data["Throttle"].tolist()],
                            "brake":    [_safe_val(v) for v in car_data["Brake"].tolist()],
                            "drs":      [_safe_val(v) for v in car_data["DRS"].tolist()],
                            "distance": [_safe_val(v) for v in car_data["Distance"].tolist()],
                        }
                except Exception:
                    pass  # Telemetry unavailable for this lap — skip silently

                compound = str(lap.get("Compound", "UNKNOWN")).upper()
                lap_records.append({
                    "lapNumber":   int(lap_num),
                    "lapTime":     _safe_val(lap.get("LapTime")),
                    "sector1":     _safe_val(lap.get("Sector1Time")),
                    "sector2":     _safe_val(lap.get("Sector2Time")),
                    "sector3":     _safe_val(lap.get("Sector3Time")),
                    "compound":    compound,
                    "tyreColour":  TYRE_COLOURS.get(compound, "#888888"),
                    "tyreLife":    _safe_val(lap.get("TyreLife")),
                    "pitIn":       bool(lap.get("PitInTime") is not pd.NaT and lap.get("PitInTime") is not None),
                    "pitOut":      bool(lap.get("PitOutTime") is not pd.NaT and lap.get("PitOutTime") is not None),
                    "position":    _safe_val(lap.get("Position")),
                    "isAccurate":  bool(lap.get("IsAccurate", True)),
                    "telemetry":   tel,
                })

            # Race distance calculation (used for pro-leaderboard ordering)
            race_dist = 0
            if lap_records:
                last_lap = lap_records[-1]
                laps_completed = last_lap["lapNumber"]
                dist_in_lap = 0
                if last_lap["telemetry"] and last_lap["telemetry"].get("distance"):
                    dist_in_lap = max(last_lap["telemetry"]["distance"])
                # Approximate: full laps × circuit length + partial
                circuit_len = float(event.get("EventName", {}) or 0) or 5000  # fallback 5 km
                race_dist = laps_completed * circuit_len + dist_in_lap

            drivers_out.append({
                "abbr":          abbr,
                "fullName":      drv_info.get("FullName", abbr),
                "teamName":      drv_info.get("TeamName", ""),
                "teamColour":    "#" + str(drv_info.get("TeamColor", "888888")),
                "number":        str(drv_info.get("DriverNumber", "")),
                "countryCode":   drv_info.get("CountryCode", ""),
                "headshotUrl":   drv_info.get("HeadshotUrl", None),
                "laps":          lap_records,
                "totalLaps":     total_laps,
                "raceDist":      race_dist,
            })

        except Exception as exc:
            logger.warning("Skipping driver %s: %s", abbr, exc)

    # Race-control messages (flags, SC, VSC)
    messages = []
    try:
        for _, msg in session.race_control_messages.iterrows():
            messages.append({
                "time":       _safe_val(msg.get("Time")),
                "category":   str(msg.get("Category", "")),
                "message":    str(msg.get("Message", "")),
                "flag":       str(msg.get("Flag", "")),
                "scope":      str(msg.get("Scope", "")),
                "sector":     _safe_val(msg.get("Sector")),
                "lapNumber":  _safe_val(msg.get("Lap")),
            })
    except Exception:
        pass

    # Weather snapshots
    weather = []
    try:
        for _, row in session.weather_data.iterrows():
            weather.append({
                "time":        _safe_val(row.get("Time")),
                "airTemp":     _safe_val(row.get("AirTemp")),
                "trackTemp":   _safe_val(row.get("TrackTemp")),
                "humidity":    _safe_val(row.get("Humidity")),
                "rainfall":    bool(row.get("Rainfall", False)),
                "windSpeed":   _safe_val(row.get("WindSpeed")),
            })
    except Exception:
        pass

    return {
        "meta": {
            "year":         year,
            "race":         race,
            "sessionType":  session_type,
            "eventName":    str(event.get("EventName", race)),
            "circuitName":  str(event.get("Location", "")),
            "country":      str(event.get("Country", "")),
            "processedAt":  datetime.utcnow().isoformat() + "Z",
        },
        "totalLaps":     total_laps,
        "drivers":       drivers_out,
        "raceControl":   messages,
        "weather":       weather,
    }


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
        data = _process_session(year, race, session)
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

            # Check which sessions already have cached data
            cached_sessions = {
                s: _cache_path(year, name, s).exists()
                for s in (["R", "Q", "S", "SQ"] if "sprint" in fmt.lower() else ["R", "Q"])
            }

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
            })
        return {"year": year, "races": races}
    except Exception as exc:
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
