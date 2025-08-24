"""Test script to check the structure of nfl_data_py.import_weekly_rosters()."""
import nfl_data_py as nfl
import pandas as pd

# Get roster data for week 1 of the 2024 season
df = nfl.import_weekly_rosters([2024], [1])

# Print the structure
print("=== Roster Data Structure ===")
print(f"Columns: {df.columns.tolist()}")
print(f"Number of rows: {len(df)}")

# Show the first row as a dictionary
if not df.empty:
    print("\nFirst row as dictionary:")
    print(df.iloc[0].to_dict())

# Save sample data to CSV for reference
df.head(10).to_csv("sample_nfl_roster_data.csv", index=False)
print("\nSaved sample data to sample_nfl_roster_data.csv")
