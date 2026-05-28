import logging
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from models import PredictionResponse
from prediction import predictor
from fastf1_client import sync_historical_data

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (Jolpica structure)
    init_db()
    
    # Create cache dir for fastf1
    if not os.path.exists("fastf1_cache"):
        os.makedirs("fastf1_cache")
        
    # Kick off async data sync for 2024 (as our historical baseline)
    asyncio.create_task(asyncio.to_thread(sync_historical_data, 2024))
    
    # Train prediction model
    predictor.train()
    yield

app = FastAPI(title="THE GRID v2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}

@app.get("/api/predict/{year}/{round_num}", response_model=PredictionResponse)
def get_prediction(year: int, round_num: int):
    # ML Prediction endpoint using 2025_f1_predictions approach
    res = predictor.predict_winner(year, round_num)
    return PredictionResponse(
        year=year,
        round=round_num,
        predicted_winner_code=res["predicted_winner_code"],
        predicted_time_seconds=res["predicted_time_seconds"],
        mae_error=res["mae_error"],
        confidence=res["confidence"]
    )

@app.get("/api/timing/{year}/{round_num}")
def get_timing(year: int, round_num: int):
    from fastf1_client import get_timing_data
    return get_timing_data(year, round_num)

import asyncio
import json
from fastapi.responses import StreamingResponse

@app.get("/api/stream/timing/{year}/{round_num}")
async def stream_timing(year: int, round_num: int):
    """Server-Sent Events (SSE) endpoint for 'live' timing updates"""
    async def event_generator():
        from fastf1_client import get_timing_data
        while True:
            # In a real race, this pulls live timing. 
            # For replay, it fetches the snapshot.
            data = get_timing_data(year, round_num)
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(15) # Poll interval
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/telemetry/{year}/{round_num}")
def get_telemetry(year: int, round_num: int, driver1: str = 'LEC', driver2: str = 'NOR'):
    from fastf1_client import get_telemetry_data
    return get_telemetry_data(year, round_num, driver1, driver2)

