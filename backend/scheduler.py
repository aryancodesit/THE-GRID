import asyncio
import logging
import fastf1
import json
from datetime import datetime
from data_processor import check_session_available, process_session
from pathlib import Path

logger = logging.getLogger("the-grid")

async def cache_refresh_loop():
    """
    Background task that runs every 6 hours.
    Checks if there are newly completed races in the current year that haven't been cached yet.
    """
    while True:
        try:
            year = datetime.utcnow().year
            logger.info(f"Running background cache refresh for year {year}...")
            
            schedule = fastf1.get_event_schedule(year, include_testing=False)
            
            for _, event in schedule.iterrows():
                name = str(event.get("EventName", ""))
                date = event.get("EventDate")
                fmt = str(event.get("EventFormat", "conventional"))
                
                if hasattr(date, "date") and date.date() <= datetime.utcnow().date():
                    sessions = ["R", "Q", "S", "SQ"] if "sprint" in fmt.lower() else ["R", "Q"]
                    
                    for session_type in sessions:
                        safe_race = name.replace(" ", "_").replace("/", "-")
                        cache_path = Path("cache") / f"processed_{year}_{safe_race}_{session_type}.json"
                        
                        if not cache_path.exists():
                            # Check if available
                            if check_session_available(year, name, session_type):
                                logger.info(f"New session data available: {year} {name} {session_type}. Processing...")
                                try:
                                    # run blocking code in an executor to avoid blocking the event loop
                                    data = await asyncio.to_thread(process_session, year, name, session_type)
                                    with cache_path.open("w", encoding="utf-8") as fh:
                                        json.dump(data, fh, ensure_ascii=False)
                                    logger.info(f"Successfully cached {year} {name} {session_type}")
                                except Exception as e:
                                    logger.error(f"Failed to cache {year} {name} {session_type}: {e}")
        except Exception as e:
            logger.error(f"Error in cache refresh loop: {e}")
        
        # Sleep for 6 hours
        await asyncio.sleep(6 * 3600)

def start_scheduler():
    logger.info("Starting background scheduler...")
    asyncio.create_task(cache_refresh_loop())
