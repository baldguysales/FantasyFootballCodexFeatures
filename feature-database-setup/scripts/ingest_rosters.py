"""Script to ingest roster data into the database using nfl_data_py.

Example usage:
    # Ingest rosters for the 2024 season
    python -m scripts.ingest_rosters --season 2024
"""
import logging
import sys
import argparse
import traceback
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional, Set, Tuple

# Add the project root to the Python path
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from sqlmodel import Session, SQLModel, create_engine, select, or_, Field, Column, JSON, text
from enums import Status

# Import data cleaning functions
from data_cleaning import clean_roster_data, clean_nfl_data

# Try to import nfl_data_py
try:
    import nfl_data_py as nfl
    NFL_DATA_AVAILABLE = True
except ImportError:
    NFL_DATA_AVAILABLE = False
    print("Warning: nfl_data_py not installed. Install with: pip install nfl-data-py")

# Simplified models to avoid circular imports
class TeamBase(SQLModel):
    id: int = Field(default=None, primary_key=True)
    abbreviation: str = Field(unique=True, index=True, max_length=3)
    full_name: str = Field(index=True)
    
class Team(TeamBase, table=True):
    __tablename__ = "team"
    
class PlayerBase(SQLModel):
    # Player identification
    player_id: str = Field(default=None, index=True, unique=True, max_length=20)
    espn_id: Optional[str] = Field(default=None, max_length=20)
    sportradar_id: Optional[str] = Field(default=None)
    yahoo_id: Optional[str] = Field(default=None, max_length=20)
    rotowire_id: Optional[str] = Field(default=None, max_length=20)
    pff_id: Optional[str] = Field(default=None, max_length=20)
    pfr_id: Optional[str] = Field(default=None, max_length=20)
    fantasy_data_id: Optional[str] = Field(default=None, max_length=20)
    sleeper_id: Optional[str] = Field(default=None, max_length=20)
    esb_id: Optional[str] = Field(default=None, max_length=20)
    gsis_it_id: Optional[str] = Field(default=None, max_length=20)
    smart_id: Optional[str] = Field(default=None)
    
    # Player information
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    player_name: str = Field(index=True)
    birth_date: Optional[date] = Field(default=None)
    height: Optional[int] = Field(default=None)  # in inches
    weight: Optional[int] = Field(default=None)  # in pounds
    college: Optional[str] = Field(default=None, max_length=100)
    
    # Position information
    position: Optional[str] = Field(default=None, max_length=5)
    depth_chart_position: Optional[str] = Field(default=None, max_length=5)
    ngs_position: Optional[str] = Field(default=None, max_length=5)
    
    # Team information
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team_abbr: Optional[str] = Field(default=None, max_length=3)
    jersey_number: Optional[str] = Field(default=None, max_length=10)
    
    # Career information
    years_exp: Optional[int] = Field(default=None)
    entry_year: Optional[int] = Field(default=None)
    rookie_year: Optional[int] = Field(default=None)
    draft_club: Optional[str] = Field(default=None, max_length=3)
    draft_number: Optional[int] = Field(default=None)
    
    # Status information
    status: Optional[str] = Field(default=None, max_length=20)
    status_description_abbr: Optional[str] = Field(default=None, max_length=10)
    
    # Media
    headshot_url: Optional[str] = Field(default=None)
    status: str = Field(
        default="ACTIVE",
        sa_column_kwargs={"name": "status"}
    )
    # Using nfl_id for both nfl_id and gsis_id since the database only has nfl_id
    
class Player(PlayerBase, table=True):
    __tablename__ = "player"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"name": "created_at"}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "name": "updated_at",
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )
    
class WeeklyRosterBase(SQLModel):
    player_id: int = Field(foreign_key="player.id", primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", index=True)
    season: int = Field(ge=1920, primary_key=True)
    week: int = Field(ge=1, le=22, primary_key=True)
    jersey_number: Optional[str] = None
    status: str = Status.ACTIVE
    
class WeeklyRoster(WeeklyRosterBase, table=True):
    __tablename__ = "weekly_roster"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment and create engine
DATABASE_URL = os.getenv("DATABASE_URL").replace('+asyncpg', '')
engine = create_engine(DATABASE_URL)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_or_create_player(session: Session, player_data: Dict[str, Any]) -> Player:
    """Find an existing player or create a new one based on roster data."""
    # Get player identifiers
    player_id = str(player_data.get('player_id', ''))
    first_name = player_data.get('first_name', '')
    last_name = player_data.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip()
    
    # Try to find by player_id first (most reliable)
    if player_id:
        stmt = select(Player).where(Player.player_id == player_id)
        player = session.exec(stmt).first()
        if player:
            return player
    
    # Fallback to name
    if full_name:
        stmt = select(Player).where(Player.player_name == full_name)
        player = session.exec(stmt).first()
        if player:
            # Update player_id if it wasn't set
            if player_id and not player.player_id:
                player.player_id = player_id
                session.add(player)
                session.commit()
            return player
    
    # Create a new player if not found
    player_attrs = {
        'player_id': player_id,
        'player_name': full_name,
        'first_name': first_name,
        'last_name': last_name,
        'position': player_data.get('position'),
        'depth_chart_position': player_data.get('depth_chart_position'),
        'jersey_number': str(player_data.get('jersey_number', '')).replace('.0', '') if player_data.get('jersey_number') else None,
        'status': player_data.get('status', 'ACTIVE'),
        'birth_date': player_data.get('birth_date'),
        'height': player_data.get('height'),
        'weight': player_data.get('weight'),
        'college': player_data.get('college'),
        'years_exp': player_data.get('years_exp'),
        'headshot_url': player_data.get('headshot_url'),
        'ngs_position': player_data.get('ngs_position'),
        'team_abbr': player_data.get('team'),
        'espn_id': player_data.get('espn_id'),
        'sportradar_id': player_data.get('sportradar_id'),
        'yahoo_id': player_data.get('yahoo_id'),
        'rotowire_id': player_data.get('rotowire_id'),
        'pff_id': player_data.get('pff_id'),
        'pfr_id': player_data.get('pfr_id'),
        'fantasy_data_id': player_data.get('fantasy_data_id'),
        'sleeper_id': player_data.get('sleeper_id'),
        'esb_id': player_data.get('esb_id'),
        'gsis_it_id': player_data.get('gsis_it_id'),
        'smart_id': player_data.get('smart_id'),
        'entry_year': player_data.get('entry_year'),
        'rookie_year': player_data.get('rookie_year'),
        'draft_club': player_data.get('draft_club'),
        'draft_number': player_data.get('draft_number'),
        'status_description_abbr': player_data.get('status_description_abbr')
    }
    
    # Set team_id if team abbreviation is provided
    team_abbr = player_data.get('team')
    if team_abbr and team_abbr != 'UNK':
        team = session.exec(select(Team).where(Team.abbreviation == team_abbr)).first()
        if team:
            player_attrs['team_id'] = team.id
    
    # Create the player
    player = Player(**player_attrs)
    session.add(player)
    session.commit()
    session.refresh(player)
    logger.info(f"Created new player: {player.player_name} ({player.position}), ID: {player.id}")
    return player

def update_team_assignment(session: Session, player: Player, team_abbr: str) -> None:
    """Update a player's team assignment if it has changed.
    
    Args:
        session: Database session
        player: Player object
        team_abbr: Team abbreviation (e.g., 'KC', 'SF')
    """
    if not team_abbr:
        return
        
    # Normalize team abbreviations
    team_abbr = team_abbr.upper().strip()
    
    # Map team abbreviations to standard NFL format
    team_mapping = {
        'LA': 'LAR',  # Rams
        'LAC': 'LAC', # Chargers
        'OAK': 'LV',  # Raiders
        'SD': 'LAC',  # Old Chargers
        'STL': 'LAR', # Old Rams
        'WAS': 'WAS', # Washington
        'WSH': 'WAS', # Alternate Washington
    }
    
    # Apply mapping if needed
    team_abbr = team_mapping.get(team_abbr, team_abbr)
    
    # Find the team by abbreviation
    stmt = select(Team).where(Team.abbreviation == team_abbr)
    team = session.exec(stmt).first()
    
    if not team:
        logger.warning(f"Team with abbreviation {team_abbr} not found in database")
        return
        
    if not player.team_id or player.team_id != team.id:
        logger.info(f"Updating team for {player.name} to {team_abbr} (ID: {team.id})")
        player.team_id = team.id
        session.add(player)
        session.commit()

def process_roster_data(roster_data: List[Dict[str, Any]], weekly_data: List[Dict[str, Any]], season: int) -> None:
    """Process roster data and insert into the database.
    
    Args:
        roster_data: List of dictionaries containing player details
        weekly_data: List of dictionaries containing weekly roster status
        season: The season the roster is for
    """
    engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))
    
    with Session(engine) as session:
        # Process each player in the roster data
        for player_data in roster_data:
            try:
                # Convert pandas Timestamp to datetime.date if needed
                if 'birth_date' in player_data and hasattr(player_data['birth_date'], 'date'):
                    player_data['birth_date'] = player_data['birth_date'].date()
                
                # Truncate ngs_position if it's too long
                if 'ngs_position' in player_data and player_data['ngs_position'] and len(str(player_data['ngs_position'])) > 5:
                    player_data['ngs_position'] = str(player_data['ngs_position'])[:5]
                
                # Find or create the player
                player = find_or_create_player(session, player_data)
                
                # Update team assignment if needed
                team_abbr = player_data.get('team')
                if team_abbr and team_abbr != 'UNK':
                    update_team_assignment(session, player, team_abbr)
                
                # Commit changes for this player
                session.commit()
                
            except Exception as e:
                player_name = player_data.get('player_name', player_data.get('name', 'Unknown'))
                logger.error(f"Error processing player {player_name}: {str(e)}")
                logger.exception("Full traceback:")
                session.rollback()
                continue

def load_roster_data(season: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Load roster data using nfl_data_py.
    
    Args:
        season: The NFL season to load rosters for
        
    Returns:
        Tuple of (roster_data, weekly_roster_data)
    """
    if not NFL_DATA_AVAILABLE:
        raise ImportError("nfl_data_py is required but not installed. Install with: pip install nfl-data-py")
    
    try:
        logger.info(f"Loading roster data for {season} season...")
        
        # Get team rosters (contains player details)
        rosters = nfl.import_seasonal_rosters([season])
        logger.info(f"Found {len(rosters)} players in roster data")
        
        if rosters.empty:
            raise ValueError(f"No roster data found for season {season}")
            
        # Get weekly rosters (contains weekly status)
        weekly_rosters = nfl.import_weekly_rosters([season])
        logger.info(f"Found {len(weekly_rosters)} weekly roster entries")
        
        # Filter for just week 1 for initial roster
        weekly_rosters = weekly_rosters[weekly_rosters['week'] == 1].copy()
        logger.info(f"Filtered to {len(weekly_rosters)} week 1 roster entries")
        
        # Clean the data using our cleaning functions
        roster_records = clean_roster_data(rosters)
        weekly_records = clean_roster_data(weekly_rosters)
        
        logger.info(f"Cleaned {len(roster_records)} roster records and {len(weekly_records)} weekly records")
        
        return roster_records, weekly_records
        
    except Exception as e:
        logger.error(f"Error loading roster data for season {season}: {e}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise

def create_tables():
    """Create database tables if they don't exist."""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created/verified")

def main():
    """Main function to handle command line arguments and orchestrate the ingestion."""
    parser = argparse.ArgumentParser(description='Ingest NFL roster data into the database')
    parser.add_argument('--season', type=int, required=True, help='NFL season (e.g., 2024)')
    
    args = parser.parse_args()
    
    if not NFL_DATA_AVAILABLE:
        logger.error("nfl_data_py is required but not installed. Install with: pip install nfl_data_py")
        sys.exit(1)
    
    try:
        # Create tables if they don't exist
        create_tables()
        
        # Load roster data from nfl_data_py
        logger.info(f"Loading roster data for {args.season} season...")
        roster_data, weekly_data = load_roster_data(args.season)
        
        if not roster_data:
            logger.warning("No roster data to process.")
            return
            
        # Process and insert data
        logger.info(f"Processing {len(roster_data)} roster entries...")
        process_roster_data(roster_data, weekly_data, args.season)
        
        logger.info("Roster data ingestion completed successfully.")
        
    except Exception as e:
        logger.error(f"Error during roster ingestion: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
