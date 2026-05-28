from pydantic import BaseModel
from typing import List, Optional

class PredictionResponse(BaseModel):
    year: int
    round: int
    predicted_winner_code: str
    predicted_time_seconds: float
    mae_error: float
    confidence: float

class DriverH2H(BaseModel):
    driver_a: str
    driver_b: str
    gap_delta_history: List[float]
    laps: List[int]
