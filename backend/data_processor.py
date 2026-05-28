import logging
from datetime import datetime
from typing import Dict, Any

import fastf1
import numpy as np
import pandas as pd

logger = logging.getLogger("the-grid")

TYRE_COLOURS = {
    "SOFT": "#E8002D",
    "MEDIUM": "#FFF200",
    "HARD": "#FFFFFF",
    "INTERMEDIATE": "#39B54A",
    "WET": "#0067FF",
}

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


def _get_driver_laps(session_laps, driver_abbr: str):
    """Return laps for a single driver using the current FastF1 3.x API."""
    return session_laps.pick_drivers(driver_abbr)


def check_session_available(year: int, race: str, session_type: str) -> bool:
    """
    Verify if a session has finished and is likely available on FastF1.
    Usually data is available 2-3 hours after the session starts.
    """
    try:
        event = fastf1.get_event(year, race)
        session_name = event.get_session_name(session_type)
        session_date = event.get_session_date(session_name)
        # If the current time is 3 hours past the session start time, it should be available
        if session_date and session_date < pd.Timestamp.utcnow() - pd.Timedelta(hours=3):
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking session availability: {e}")
        return False


def process_session(year: int, race: str, session_type: str) -> Dict[str, Any]:
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
            drv_laps = _get_driver_laps(laps, abbr)

            lap_records = []
            for _, lap in drv_laps.iterrows():
                lap_num = _safe_val(lap.get("LapNumber"))
                if lap_num is None:
                    continue

                # Telemetry for this lap
                tel = {}
                try:
                    car_data = lap.get_telemetry()
                    if not car_data.empty:
                        tel = {
                            "time":     [_safe_val(v) for v in car_data["Time"].dt.total_seconds().tolist()],
                            "x":        [_safe_val(v) for v in car_data["X"].tolist()],
                            "y":        [_safe_val(v) for v in car_data["Y"].tolist()],
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
