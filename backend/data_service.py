import pandas as pd
import fastf1
import os

# Constants for Data Paths
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_2020_2024 = os.path.join(DATA_DIR, "../F1 Races 2020-2024.csv")
CSV_2025 = os.path.join(DATA_DIR, "../F1_2025_RaceResults.csv")

def get_race_results(year: int):
    """
    Fetches race results for a given year.
    Tries to load from CSVs first, then falls back to FastF1 (optional/future).
    """
    try:
        df = None
        if 2020 <= year <= 2024:
            if os.path.exists(CSV_2020_2024):
                df = pd.read_csv(CSV_2020_2024)
                df = df[df['year'] == year]
        elif year == 2025:
            if os.path.exists(CSV_2025):
                df = pd.read_csv(CSV_2025)
        
        if df is not None and not df.empty:
            # Process and return standard format
            # Assuming CSV columns: round, raceName, date, winner, team, etc.
            # This mapping depends on the actual CSV structure. 
            # For now, returning raw dict to see structure or generic list.
            return df.to_dict('records')
            
    except Exception as e:
        print(f"Error reading CSV for {year}: {e}")

    # Fallback: Use FastF1 to get the schedule/results if CSV fails
    try:
        schedule = fastf1.get_event_schedule(year)
        results = []
        for i, row in schedule.iterrows():
            if row['Session5Date'] < pd.Timestamp.now(): # Race has happened
                results.append({
                    "round": row['RoundNumber'],
                    "raceName": row['EventName'],
                    "date": row['EventDate'].strftime('%Y-%m-%d'),
                    "location": row['Location'],
                    "winner": "TBD" # FastF1 schedule doesn't have winner directly without loading session
                })
        return results
    except Exception as e:
        print(f"Error fetching schedule from FastF1: {e}")
        return []

def get_standings(year: int):
    """
    Returns driver and constructor standings.
    Currently mocked or calculated from results if available.
    """
    # TODO: Implement calculation from CSV results
    return {
        "drivers": [],
        "constructors": []
    }
