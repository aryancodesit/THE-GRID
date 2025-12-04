import fastf1
import os

# Create cache directory if it doesn't exist
if not os.path.exists('cache'):
    os.makedirs('cache')

print("Enabling FastF1 Cache...")
fastf1.Cache.enable_cache('cache')

print("Fetching 2025 Bahrain Grand Prix (Race)...")
try:
    # Get the session
    # Note: 2025 data might not be fully available yet in reality, 
    # but FastF1 v3.4+ supports the season structure.
    # If 2025 fails (because it's in the future), we might need to fallback to 2024 for testing 
    # as we did in the main app, but the user specifically asked for 2025.
    # Let's try 2025 first as requested.
    session = fastf1.get_session(2025, 'Bahrain', 'R')
    
    print("Loading session data (this may take a while)...")
    session.load()
    
    print("SUCCESS: 2025 Bahrain GP data cached successfully!")
    
except Exception as e:
    print(f"Error fetching 2025 data: {e}")
    print("Attempting fallback to 2024 Bahrain GP for development purposes...")
    try:
        session = fastf1.get_session(2024, 'Bahrain', 'R')
        session.load()
        print("SUCCESS: 2024 Bahrain GP data cached (Fallback)!")
    except Exception as e2:
        print(f"Critical Error: Could not fetch 2024 data either: {e2}")
