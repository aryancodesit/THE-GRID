from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TelemetryData(BaseModel):
    time: List[Optional[float]]
    x: List[Optional[float]]
    y: List[Optional[float]]
    speed: List[Optional[float]]
    gear: List[Optional[int]]
    throttle: List[Optional[float]]
    brake: List[Optional[float]]
    drs: List[Optional[float]]
    distance: List[Optional[float]]

class LapRecord(BaseModel):
    lapNumber: int
    lapTime: Optional[float]
    sector1: Optional[float]
    sector2: Optional[float]
    sector3: Optional[float]
    compound: str
    tyreColour: str
    tyreLife: Optional[float]
    pitIn: bool
    pitOut: bool
    position: Optional[float]
    isAccurate: bool
    telemetry: Optional[TelemetryData] = None

class DriverData(BaseModel):
    abbr: str
    fullName: str
    teamName: str
    teamColour: str
    number: str
    countryCode: str
    headshotUrl: Optional[str]
    laps: List[LapRecord]
    totalLaps: int
    raceDist: float

class RaceControlMessage(BaseModel):
    time: Optional[float]
    category: str
    message: str
    flag: str
    scope: str
    sector: Optional[float]
    lapNumber: Optional[float]

class WeatherSnapshot(BaseModel):
    time: Optional[float]
    airTemp: Optional[float]
    trackTemp: Optional[float]
    humidity: Optional[float]
    rainfall: bool
    windSpeed: Optional[float]

class SessionMeta(BaseModel):
    year: int
    race: str
    sessionType: str
    eventName: str
    circuitName: str
    country: str
    processedAt: str

class RaceDataPayload(BaseModel):
    meta: SessionMeta
    totalLaps: int
    drivers: List[DriverData]
    raceControl: List[RaceControlMessage]
    weather: List[WeatherSnapshot]
