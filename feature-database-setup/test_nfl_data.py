"""Test script to verify nfl_data_py installation and basic functionality."""
import nfl_data_py as nfl

def main():
    print("Testing nfl_data_py installation...")
    
    # Get the current year for testing
    current_year = 2024  # Using a fixed year for testing
    print(f"Testing with season: {current_year}")
    
    try:
        # Try to get roster data for the current season
        print(f"Fetching roster data for {current_year}...")
        rosters = nfl.import_seasonal_rosters([current_year])
        print(f"Fetched {len(rosters)} roster entries")
        
        if not rosters.empty:
            print("\nFirst few players:")
            print(rosters[['player_name', 'position', 'team']].head())
    except Exception as e:
        print(f"Error: {e}")
        
        if not rosters.empty:
            print("\nSample roster data:")
            print(rosters.head())

if __name__ == "__main__":
    main()
