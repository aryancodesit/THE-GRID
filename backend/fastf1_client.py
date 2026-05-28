import fastf1
import pandas as pd
import logging
from database import SessionLocal, RaceResult, Driver

logger = logging.getLogger("the-grid-fastf1")

# Enable FastF1 cache
fastf1.Cache.enable_cache('fastf1_cache') 

def sync_historical_data(year: int):
    """
    Fetches historical race results for a given year using FastF1
    and populates our local SQLite DB (Jolpica structure).
    """
    logger.info(f"Syncing historical data for {year}...")
    db = SessionLocal()
    
    try:
        schedule = fastf1.get_event_schedule(year)
        
        for index, event in schedule.iterrows():
            if event['EventFormat'] == 'testing':
                continue
                
            try:
                session = fastf1.get_session(year, event['RoundNumber'], 'R')
                session.load(telemetry=False, weather=False, messages=False)
                
                results = session.results
                
                for _, row in results.iterrows():
                    driver_code = row['Abbreviation']
                    
                    # Ensure driver exists
                    driver = db.query(Driver).filter(Driver.code == driver_code).first()
                    if not driver:
                        driver = Driver(
                            driver_id_str=row['DriverId'].lower() if pd.notna(row.get('DriverId')) else driver_code.lower(),
                            code=driver_code,
                            first_name=row['FirstName'],
                            last_name=row['LastName'],
                            nationality=row['CountryCode']
                        )
                        db.add(driver)
                        db.commit()
                        db.refresh(driver)
                    
                    # Add Race Result
                    existing_result = db.query(RaceResult).filter(
                        RaceResult.year == year,
                        RaceResult.round == event['RoundNumber'],
                        RaceResult.driver_id == driver.id
                    ).first()
                    
                    if not existing_result:
                        time_ms = row.get('Time')
                        time_seconds = time_ms.total_seconds() if pd.notna(time_ms) else 0.0
                        
                        result = RaceResult(
                            year=year,
                            round=event['RoundNumber'],
                            driver_id=driver.id,
                            position=int(row['Position']) if pd.notna(row['Position']) else 0,
                            points=float(row['Points']),
                            time_seconds=time_seconds
                        )
                        db.add(result)
                        
                db.commit()
                logger.info(f"Synced Round {event['RoundNumber']} for {year}.")
            except Exception as e:
                logger.warning(f"Could not load session {year} Round {event['RoundNumber']}: {e}")
                
    except Exception as e:
        logger.error(f"Failed to sync {year} schedule: {e}")
    finally:
        db.close()

def get_timing_data(year: int, round_num: int):
    try:
        session = fastf1.get_session(year, round_num, 'R')
        session.load(telemetry=False, weather=False, messages=False)
        laps = session.laps
        results = session.results

        timing = []
        for i, row in results.iterrows():
            code = row.get('Abbreviation', '')
            fastest_lap = '-'
            tyre = 'Unknown'
            
            driver_laps = laps.pick_driver(code)
            if not driver_laps.empty:
                fastest = driver_laps.pick_fastest()
                if pd.notna(fastest['LapTime']):
                    # format laptime mm:ss.ms
                    ms = int(fastest['LapTime'].total_seconds() * 1000)
                    mins = ms // 60000
                    secs = (ms % 60000) // 1000
                    mills = ms % 1000
                    fastest_lap = f"{mins}:{secs:02d}.{mills:03d}"
                
                # Format Sectors
                def format_sector(td):
                    if pd.notna(td):
                        s = int(td.total_seconds() * 1000)
                        return f"{(s // 1000):02d}.{(s % 1000):03d}"
                    return "-"

                s1 = format_sector(fastest.get('Sector1Time'))
                s2 = format_sector(fastest.get('Sector2Time'))
                s3 = format_sector(fastest.get('Sector3Time'))
                
                # Get last stint tyre
                last_lap = driver_laps.iloc[-1]
                tyre = str(last_lap.get('Compound', 'Unknown'))[0] # S, M, H, W, I

            timing.append({
                "pos": int(row.get('Position', 0)) if pd.notna(row.get('Position')) else 0,
                "no": str(row.get('DriverNumber', '')),
                "code": code,
                "gap": str(row.get('Time', 'OUT')),
                "fastest_lap": fastest_lap,
                "s1": s1,
                "s2": s2,
                "s3": s3,
                "tyre": tyre
            })
        # sort by pos
        timing.sort(key=lambda x: x['pos'] if x['pos'] > 0 else 999)
        return timing
    except Exception as e:
        logger.error(f"Error fetching timing data: {e}")
        return []

def get_telemetry_data(year: int, round_num: int, driver1: str = 'LEC', driver2: str = 'NOR'):
    try:
        session = fastf1.get_session(year, round_num, 'R')
        session.load(telemetry=True, weather=False, messages=False)
        laps = session.laps
        
        # We get the fastest lap telemetry for both drivers to compare
        d1_laps = laps.pick_driver(driver1)
        d2_laps = laps.pick_driver(driver2)
        
        if d1_laps.empty or d2_laps.empty:
            return []
            
        d1_fastest = d1_laps.pick_fastest()
        d2_fastest = d2_laps.pick_fastest()
        
        d1_tel = d1_fastest.get_telemetry()
        d2_tel = d2_fastest.get_telemetry()
        
        # Dynamic Color Extraction (Crucial for 2026 Audi/Cadillac)
        try:
            c1 = "#" + str(session.get_driver(driver1).get('TeamColor', 'FFFFFF'))
            c2 = "#" + str(session.get_driver(driver2).get('TeamColor', 'FFFFFF'))
        except:
            c1, c2 = "#E10600", "#FF8700" # fallback
        
        # Downsample for UI performance
        d1_tel = d1_tel.iloc[::10]
        d2_tel = d2_tel.iloc[::10]
        
        data_points = []
        max_dist = min(d1_tel['Distance'].max(), d2_tel['Distance'].max())
        
        for dist in range(0, int(max_dist), 100):
            d1_point = d1_tel.iloc[(d1_tel['Distance'] - dist).abs().argsort()[:1]]
            d2_point = d2_tel.iloc[(d2_tel['Distance'] - dist).abs().argsort()[:1]]
            
            if not d1_point.empty and not d2_point.empty:
                data_points.append({
                    "distance": dist,
                    "speed1": float(d1_point['Speed'].values[0]),
                    "speed2": float(d2_point['Speed'].values[0])
                })
                
        return {
            "driver1": {"code": driver1, "color": c1},
            "driver2": {"code": driver2, "color": c2},
            "data": data_points
        }
    except Exception as e:
        logger.error(f"Error fetching telemetry: {e}")
        return {"driver1": {}, "driver2": {}, "data": []}
