import fastf1
import pandas as pd
import numpy as np

# Enable caching
fastf1.Cache.enable_cache('./cache')

# Try to load the session
year = 2024
gp = 'Bahrain'
session_type = 'R'

print(f"Loading {year} {gp} {session_type}...")
session = fastf1.get_session(year, gp, session_type)
session.load()

drivers = session.drivers
print(f"Drivers: {drivers}")

# Pick a driver to test (e.g. HUL, PIA)
test_drivers = ['HUL', 'PIA', 'VER']

for driver_id in drivers:
    driver = session.get_driver(driver_id)
    identifier = driver['Abbreviation']
    
    if identifier not in test_drivers:
        continue
        
    print(f"Processing {identifier}...")
    
    laps = session.laps.pick_driver(driver_id)
    telemetry = laps.get_telemetry()
    
    if telemetry.empty:
        print("Telemetry empty.")
        continue
        
    telemetry['TimeSec'] = telemetry['Time'].dt.total_seconds()
    
    # 1. LapNumber Merge Logic
    needs_lap_merge = 'LapNumber' not in telemetry.columns
    if not needs_lap_merge:
        if telemetry['LapNumber'].isna().all() or (telemetry['LapNumber'] == 0).all():
            needs_lap_merge = True
            
    if needs_lap_merge:
        print("Merging LapNumber...")
        try:
            conditions = []
            choices = []
            sorted_laps = laps.sort_values('LapStartTime')
            
            for _, lap in sorted_laps.iterrows():
                t_start = lap['LapStartTime'].total_seconds() if pd.notnull(lap['LapStartTime']) else 0.0
                t_end = lap['Time'].total_seconds() if pd.notnull(lap['Time']) else t_start + 10000.0
                conditions.append((telemetry['TimeSec'] >= t_start) & (telemetry['TimeSec'] < t_end))
                choices.append(lap['LapNumber'])
            
            if conditions:
                telemetry['LapNumber'] = np.select(conditions, choices, default=0)
        except Exception as e:
            print(f"Merge failed: {e}")

    # 2. Resampling (Simplified)
    # Just take the last row for testing
    final_df = telemetry.iloc[[-1]].copy()
    
    # 3. Race Dist Logic
    circuit_length = 5412 # Bahrain approx
    
    try:
        print("Calculating race_dist...")
        # Ensure LapNumber is int and Distance is float
        laps_val = final_df['LapNumber'].fillna(0).astype(int)
        dist_val = final_df['Distance'].fillna(0)
        
        laps_completed = (laps_val - 1).clip(lower=0)
        
        final_df['race_dist'] = (laps_completed * circuit_length) + dist_val
        final_df['race_dist'] = final_df['race_dist'].fillna(0).astype(int)
        
        print(f"Result: {identifier} - Lap: {laps_val.iloc[-1]}, Dist: {dist_val.iloc[-1]}, RaceDist: {final_df['race_dist'].iloc[-1]}")
        
    except Exception as e:
        print(f"Race dist failed: {e}")
