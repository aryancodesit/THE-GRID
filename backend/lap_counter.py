import fastf1
import pandas as pd

# Enable caching to speed up repeated data fetching
fastf1.Cache.enable_cache('./cache')

# Define the session you want to analyze
# Example: 2024 Bahrain Grand Prix, Race session
year = 2024
grand_prix = 'Bahrain'
session_type = 'R' # 'R' for Race, 'Q' for Qualifying, 'FP1', 'FP2', 'FP3' for practice

session = fastf1.get_session(year, grand_prix, session_type)
session.load()

# The 'session.laps' object contains data for every lap completed by every driver
print(f"Total number of recorded laps: {len(session.laps)}")

# You can also see the laps completed by a specific driver, for example 'VER' (Max Verstappen)
verstappen_laps = session.laps.loc[session.laps['Driver'] == 'VER']
print(f"Laps completed by VER: {len(verstappen_laps)}")

# To get unique drivers in the session
drivers = session.laps['Driver'].unique()
print(f"Drivers in this session: {drivers}")
