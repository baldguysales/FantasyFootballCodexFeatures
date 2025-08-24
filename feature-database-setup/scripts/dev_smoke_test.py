"""Smoke test for the roster and PBP ingestion pipeline.

This script demonstrates the end-to-end flow of ingesting roster data and PBP data,
then verifying the results.
"""
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, select

from models.teams_players import Player, Team
from models.roster import WeeklyRoster, PlayerWeekStats, PlayerWeekPoints
from database import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_data(output_dir: Path) -> None:
    """Create test data files for the smoke test."""
    # Create test roster data
    test_roster = [
        {
            "player_id": "00-0033873",
            "name": "Patrick Mahomes",
            "first_name": "Patrick",
            "last_name": "Mahomes",
            "football_name": "P. Mahomes",
            "position": "QB",
            "team": "KC",
            "jersey_number": 15,
            "status": "ACT",
            "birth_date": "1995-09-17",
            "height_inches": 75,
            "weight_lbs": 225,
            "college": "Texas Tech",
            "years_exp": 6,
            "entry_year": 2017,
            "rookie_year": 2017,
            "draft_club": "KC",
            "draft_number": 10,
            "age": 28,
            "espn_id": "3139477",
            "sportradar_id": "eaf629d8-1f22-4e93-9f4e-aa33880a8213",
            "status_abbr": "ACT",
            "game_type": "REG",
            "ngs_position": "QB"
        },
        {
            "player_id": "00-0033874",
            "name": "Travis Kelce",
            "first_name": "Travis",
            "last_name": "Kelce",
            "football_name": "T. Kelce",
            "position": "TE",
            "team": "KC",
            "jersey_number": 87,
            "status": "ACT",
            "birth_date": "1989-10-05",
            "height_inches": 77,
            "weight_lbs": 250,
            "college": "Cincinnati",
            "years_exp": 10,
            "entry_year": 2013,
            "rookie_year": 2013,
            "draft_club": "KC",
            "draft_number": 63,
            "age": 33,
            "espn_id": "15825",
            "sportradar_id": "eaf629d8-1f22-4e93-9f4e-aa33880a8214",
            "status_abbr": "ACT",
            "game_type": "REG",
            "ngs_position": "TE"
        }
    ]
    
    # Create test PBP data
    test_pbp = [
        {
            "game_id": "2023090700",
            "play_id": "1",
            "posteam": "KC",
            "defteam": "DET",
            "qtr": 1,
            "time": "15:00",
            "down": 1,
            "ydstogo": 10,
            "yrdln": "KC 25",
            "play_type": "pass",
            "passer_player_id": "00-0033873",
            "receiver_player_id": "00-0033874",
            "pass_length": 12,
            "pass_location": "left",
            "yards_after_catch": 5,
            "complete_pass": 1,
            "passing_yards": 12,
            "receiving_yards": 17,
            "first_down": 1,
            "play_id_nfl": "20230907001"
        },
        {
            "game_id": "2023090700",
            "play_id": "2",
            "posteam": "KC",
            "defteam": "DET",
            "qtr": 1,
            "time": "14:15",
            "down": 1,
            "ydstogo": 10,
            "yrdln": "KC 42",
            "play_type": "pass",
            "passer_player_id": "00-0033873",
            "receiver_player_id": "00-0033874",
            "pass_length": 18,
            "pass_location": "middle",
            "yards_after_catch": 10,
            "complete_pass": 1,
            "pass_touchdown": 1,
            "passing_yards": 18,
            "receiving_yards": 28,
            "touchdown": 1,
            "play_id_nfl": "20230907002"
        }
    ]
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write test data to files
    roster_file = output_dir / "test_roster.json"
    pbp_file = output_dir / "test_pbp.json"
    
    with open(roster_file, 'w') as f:
        json.dump(test_roster, f, indent=2)
    
    with open(pbp_file, 'w') as f:
        json.dump(test_pbp, f, indent=2)
    
    logger.info(f"Created test data in {output_dir}")
    return roster_file, pbp_file

def run_smoke_test():
    """Run the smoke test."""
    logger.info("Starting smoke test...")
    
    # Create a directory for test data
    test_data_dir = Path("test_data")
    
    # Create test data files
    roster_file, pbp_file = create_test_data(test_data_dir)
    
    # Import the ingest scripts
    from scripts.ingest_rosters import process_roster_data
    from scripts.ingest_pbp_raw import process_pbp_data
    
    # Test parameters
    season = 2023
    week = 1
    
    # Load test data
    with open(roster_file, 'r') as f:
        roster_data = json.load(f)
    
    with open(pbp_file, 'r') as f:
        pbp_data = json.load(f)
    
    # Ingest roster data
    logger.info("Ingesting roster data...")
    process_roster_data(roster_data, season, week)
    
    # Ingest PBP data
    logger.info("Ingesting PBP data...")
    process_pbp_data(pbp_data, season, week)
    
    # Verify results
    logger.info("Verifying results...")
    with Session(engine) as session:
        # Check players were created
        stmt = select(Player).where(Player.nfl_player_id.in_(["00-0033873", "00-0033874"]))
        players = session.exec(stmt).all()
        logger.info(f"Found {len(players)} players in database")
        
        # Check weekly rosters
        stmt = select(WeeklyRoster).where(WeeklyRoster.season == season, WeeklyRoster.week == week)
        rosters = session.exec(stmt).all()
        logger.info(f"Found {len(rosters)} weekly roster entries")
        
        # Check player stats
        stmt = select(PlayerWeekStats).where(PlayerWeekStats.season == season, PlayerWeekStats.week == week)
        stats = session.exec(stmt).all()
        logger.info(f"Found {len(stats)} player week stats entries")
        
        # Check player points
        stmt = select(PlayerWeekPoints).where(PlayerWeekPoints.season == season, PlayerWeekPoints.week == week)
        points = session.exec(stmt).all()
        logger.info(f"Found {len(points)} player week points entries")
        
        # Print summary
        print("\n=== Smoke Test Results ===")
        print(f"Players: {len(players)}/2")
        print(f"Weekly Rosters: {len(rosters)}/2")
        print(f"Player Week Stats: {len(stats)}/2")
        print(f"Player Week Points: {len(points)}/2")
        
        if len(players) == 2 and len(rosters) == 2 and len(stats) == 2 and len(points) == 2:
            print("\n✅ Smoke test passed!")
        else:
            print("\n❌ Smoke test failed!")

if __name__ == "__main__":
    run_smoke_test()
