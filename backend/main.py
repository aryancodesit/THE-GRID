from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fastf1
import pandas as pd
import numpy as np
import os
import json
try:
    import data_service
except ImportError:
    from . import data_service

# Create cache directory
if not os.path.exists('cache'):
    os.makedirs('cache')

fastf1.Cache.enable_cache('cache')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "F1 Race Replay API"}

@app.get("/api/race-data/{year}/{location}/{session}")
def get_race_data(year: int, location: str, session: str):
    # Check for cached processed data
    cache_file = f"cache/processed_{year}_{location}_{session}.json"
    if os.path.exists(cache_file):
        print(f"Serving from cache: {cache_file}")
        # We need to load it. But we return a dict, FastAPI handles JSON.
        # Let's just read it and return.
        import json
        with open(cache_file, 'r') as f:
            return json.load(f)

    try:
        # Load the session
        # FastF1 handles 'Australia', 'Monaco' etc. automatically
        race = fastf1.get_session(year, location, session)
        race.load()
        
        # Get the list of drivers
        drivers = race.drivers
        
        # --- INTEGRATED LAP COUNTER LOGIC ---
        print(f"Total number of recorded laps: {len(race.laps)}")
        unique_drivers = race.laps['Driver'].unique()
        print(f"Drivers in this session: {unique_drivers}")
        # ------------------------------------
        
        # Prepare data structure
        total_laps = 0
        try:
            if session == 'R' or session == 'S':
                total_laps = race.total_laps
                if pd.isna(total_laps):
                    total_laps = int(race.laps['LapNumber'].max())
            else:
                total_laps = 0 # Practice/Quali
        except:
            total_laps = int(race.laps['LapNumber'].max()) if not race.laps.empty else 0

        race_data = {
            "track_name": race.event.EventName,
            "session_name": race.name,
            "session_type": session,
            "total_laps": int(total_laps) if total_laps else 0,
            "drivers": {}
        }
        
        # 1. Collect all telemetry first to determine common time bounds
        driver_telemetry = {}
        max_time = 0
        
        # 0. Generate Reference Telemetry (Ideal Lap) for Charts
        print("📊 Generating Reference Telemetry...")
        chart_data = []
        circuit_length = 5000 # Default fallback
        try:
            fastest_lap = race.laps.pick_fastest()
            if not fastest_lap.empty:
                # Calculate circuit length from fastest lap distance
                pos_data = fastest_lap.get_pos_data()
                circuit_length = pos_data['Distance'].max()
                
                ref_tel = fastest_lap.get_telemetry()
                ref_tel['Distance'] = ref_tel['Distance'].astype(int)
                # Downsample: 1 point every 20 rows
                chart_data = ref_tel.iloc[::20][['Distance', 'Speed', 'nGear', 'RPM']].to_dict('records')
        except Exception as e:
            print(f"Error generating chart data: {e}")
            
        race_data["chart_data"] = chart_data

        # 1. Collect all telemetry first to determine common time bounds
        driver_telemetry = {}
        max_time = 0
        

        for driver_id in drivers:
            try:
                driver = race.get_driver(driver_id)
                identifier = driver['Abbreviation']
                if not identifier: continue
                
                laps = race.laps.pick_driver(driver_id)
                if laps.empty: continue
                
                # Get telemetry for the whole session
                telemetry = laps.get_telemetry()
                
                if telemetry.empty: continue
                
                telemetry['TimeSec'] = telemetry['Time'].dt.total_seconds()
                
                # Update max time
                t_end = telemetry['TimeSec'].max()
                if t_end > max_time:
                    max_time = t_end
                
                # Ensure we have Compound and LapNumber
                # FastF1 telemetry usually has 'Compound' if loaded correctly, but sometimes it's in laps.
                # Let's merge lap data (Compound, LapNumber) onto telemetry if missing.
                # Check if LapNumber is missing OR if it's all 0/NaN
                needs_lap_merge = 'LapNumber' not in telemetry.columns
                if not needs_lap_merge:
                    # Check if valid
                    if telemetry['LapNumber'].isna().all() or (telemetry['LapNumber'] == 0).all():
                        needs_lap_merge = True
                        
                if needs_lap_merge:
                    try:
                        # Vectorized approach to assign LapNumber
                        conditions = []
                        choices = []
                        
                        # Sort laps by start time to ensure correct order
                        sorted_laps = laps.sort_values('LapStartTime')
                        
                        for _, lap in sorted_laps.iterrows():
                            # Handle NaT
                            t_start = lap['LapStartTime'].total_seconds() if pd.notnull(lap['LapStartTime']) else 0.0
                            t_end = lap['Time'].total_seconds() if pd.notnull(lap['Time']) else t_start + 10000.0
                            
                            # Create condition for this lap
                            conditions.append((telemetry['TimeSec'] >= t_start) & (telemetry['TimeSec'] < t_end))
                            choices.append(lap['LapNumber'])
                        
                        if conditions:
                            # Apply conditions. Default to 0 if no match (e.g. before start)
                            telemetry['LapNumber'] = np.select(conditions, choices, default=0)
                            
                            # Also try to merge Compound using the same logic if missing
                            # Also try to merge Compound using the same logic if missing
                            if 'Compound' not in telemetry.columns or telemetry['Compound'].isna().all() or (telemetry['Compound'] == 'UNKNOWN').all():
                                # Get compound choices, defaulting to 'SOFT' if missing/NaN
                                compound_choices = []
                                for _, lap in sorted_laps.iterrows():
                                    comp = lap['Compound'] if 'Compound' in lap and pd.notnull(lap['Compound']) and lap['Compound'] != 'UNKNOWN' else 'SOFT'
                                    compound_choices.append(comp)
                                
                                telemetry['Compound'] = np.select(conditions, compound_choices, default='SOFT')

                    except Exception as e:
                        print(f"Error merging lap info for driver {identifier}: {e}")
                
                # Select columns. If Compound/LapNumber missing, they will be NaN/KeyError.
                # Let's check columns first.
                cols = ['TimeSec', 'X', 'Y', 'Speed', 'nGear', 'DRS', 'Distance']
                if 'Compound' in telemetry.columns:
                    cols.append('Compound')
                if 'LapNumber' in telemetry.columns:
                    cols.append('LapNumber')
                
                driver_telemetry[identifier] = telemetry[cols]
                
            except Exception as e:
                print(f"Skipping driver {driver_id}: {e}")
                continue

        # 2. Create a common time index (4Hz = 0.25s intervals)
        freq = 0.25
        common_index = np.arange(0, max_time + freq, freq)
        
        print(f"Resampling data to {len(common_index)} points (4Hz)...")
        
        # 3. Resample and Interpolate each driver
        for identifier, df in driver_telemetry.items():
            try:
                # Convert to numeric
                df['X'] = pd.to_numeric(df['X'], errors='coerce')
                df['Y'] = pd.to_numeric(df['Y'], errors='coerce')
                df['Speed'] = pd.to_numeric(df['Speed'], errors='coerce')
                df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')
                
                # Set index to TimeSec
                df = df.set_index('TimeSec')
                
                # Remove duplicate indices if any
                df = df[~df.index.duplicated(keep='first')]
                
                new_data = {}
                original_time = df.index.values
                
                # Interpolate X, Y, Speed, Distance
                new_data['X'] = np.interp(common_index, original_time, df['X'].values, left=np.nan, right=np.nan)
                new_data['Y'] = np.interp(common_index, original_time, df['Y'].values, left=np.nan, right=np.nan)
                new_data['Speed'] = np.interp(common_index, original_time, df['Speed'].values, left=np.nan, right=np.nan)
                new_data['Distance'] = np.interp(common_index, original_time, df['Distance'].values, left=np.nan, right=np.nan)
                
                # Create DF
                df_resampled = pd.DataFrame(index=common_index)
                df_resampled.index.name = 'TimeSec'
                
                # Reconstruct DF from numpy arrays
                final_df = pd.DataFrame({
                    'TimeSec': common_index,
                    'X': new_data['X'],
                    'Y': new_data['Y'],
                    'Speed': new_data['Speed'],
                    'Distance': new_data['Distance']
                })
                
                # For Gear and DRS, we need nearest/ffill
                # We can use searchsorted to find indices
                idx = np.searchsorted(original_time, common_index, side='right') - 1
                idx = np.clip(idx, 0, len(original_time) - 1)
                
                final_df['nGear'] = df['nGear'].values[idx]
                final_df['DRS'] = df['DRS'].values[idx]
                
                # Handle Compound and LapNumber if they exist
                if 'Compound' in df.columns:
                    final_df['Compound'] = df['Compound'].values[idx]
                if 'LapNumber' in df.columns:
                    final_df['LapNumber'] = df['LapNumber'].values[idx]
                
                try:
                    # --- NEW: Calculate Total Race Distance ---
                    # Ensure LapNumber is int and Distance is float
                    # Fill NaNs with 0 to avoid errors
                    laps_val = final_df['LapNumber'].fillna(0).astype(int)
                    dist_val = final_df['Distance'].fillna(0)
                    
                    # Laps completed = LapNumber - 1 (if Lap 1, completed 0)
                    laps_completed = (laps_val - 1).clip(lower=0)
                    
                    # Total Distance = (Laps Completed * Circuit Length) + Current Distance
                    final_df['race_dist'] = (laps_completed * circuit_length) + dist_val
                    final_df['race_dist'] = final_df['race_dist'].fillna(0).astype(int)
                    
                except Exception as e:
                    print(f"Error calculating race_dist for {identifier}: {e}")
                    final_df['race_dist'] = 0 # Fallback
                
                # Round values
                final_df['X'] = final_df['X'].round(1)
                final_df['Y'] = final_df['Y'].round(1)
                final_df['Speed'] = final_df['Speed'].round(0)
                final_df['Distance'] = final_df['Distance'].round(0)
                final_df['TimeSec'] = final_df['TimeSec'].round(2)
                
                # Replace NaNs with None for JSON compatibility
                # Must cast to object to hold None instead of NaN
                final_df = final_df.astype(object).where(pd.notnull(final_df), None)
                
                race_data["drivers"][identifier] = final_df.to_dict('records')
                
            except Exception as e:
                print(f"Error resampling driver {identifier}: {e}")
                continue
        
        # 4. Get Track Status (Flags)
        print("🏁 Fetching Track Status...")
        track_status_data = []
        try:
            # session.track_status returns a DataFrame with 'Time', 'Status', 'Message'
            ts = race.track_status
            if not ts.empty:
                ts['TimeSec'] = ts['Time'].dt.total_seconds()
                # We want to map this to our common_index
                # We can use 'pad' (forward fill) interpolation because status persists until changed
                
                # Create a Series indexed by TimeSec
                ts_series = ts.set_index('TimeSec')['Status']
                
                # Reindex to common_index with ffill
                # We need to handle the start (0 to first status) - usually '1' (Green)
                ts_resampled = ts_series.reindex(ts_series.index.union(common_index)).sort_index().ffill().reindex(common_index).fillna('1')
                
                # Convert to list of dicts or just a list of values?
                # List of values is more efficient: [Status, Status, ...] corresponding to common_index
                track_status_data = ts_resampled.astype(str).tolist()
                
        except Exception as e:
            print(f"Error fetching track status: {e}")
            # Fallback: All Green
            track_status_data = ['1'] * len(common_index)

        race_data["track_status"] = track_status_data
        
        # Save to cache
        import json
        with open(cache_file, 'w') as f:
            json.dump(race_data, f)
            
        return race_data

    except Exception as e:
        print(f"Error loading race: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/results/{year}")
def get_results(year: int):
    return data_service.get_race_results(year)

@app.get("/api/standings/{year}")
def get_standings(year: int):
    return data_service.get_standings(year)

@app.get("/api/seasons")
def get_seasons():
    # Return available seasons. FastF1 supports quite a few, let's limit to recent era for now
    return list(range(2018, 2026))

@app.get("/api/schedule/{year}")
def get_schedule(year: int):
    try:
        schedule = fastf1.get_event_schedule(year)
        # Convert to list of dicts
        events = []
        for i, row in schedule.iterrows():
            events.append({
                "RoundNumber": row["RoundNumber"],
                "Country": row["Country"],
                "Location": row["Location"],
                "EventName": row["EventName"],
                "EventDate": row["EventDate"].isoformat() if pd.notnull(row["EventDate"]) else None,
                "Session1": row["Session1"],
                "Session1Date": row["Session1Date"].isoformat() if pd.notnull(row["Session1Date"]) else None,
                "Session2": row["Session2"],
                "Session2Date": row["Session2Date"].isoformat() if pd.notnull(row["Session2Date"]) else None,
                "Session3": row["Session3"],
                "Session3Date": row["Session3Date"].isoformat() if pd.notnull(row["Session3Date"]) else None,
                "Session4": row["Session4"],
                "Session4Date": row["Session4Date"].isoformat() if pd.notnull(row["Session4Date"]) else None,
                "Session5": row["Session5"],
                "Session5Date": row["Session5Date"].isoformat() if pd.notnull(row["Session5Date"]) else None,
            })
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
