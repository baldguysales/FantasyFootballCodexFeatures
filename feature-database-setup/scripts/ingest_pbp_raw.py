"""Script to ingest play-by-play data and update player stats and fantasy points.

Example usage:
    python -m scripts.ingest_pbp_raw --season 2023 --week 1 pbp_data.json
"""
import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select, text

from models.roster import PbpRaw
from database import engine

# Import data cleaning functions
from data_cleaning import clean_pbp_data, clean_nfl_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_pbp_data(pbp_data: List[Dict[str, Any]], season: int, week: int) -> None:
    """Process PBP data and save to database."""
    if not pbp_data:
        logger.warning("No PBP data provided")
        return
    
    try:
        # Clean the PBP data
        cleaned_data = clean_pbp_data(pd.DataFrame(pbp_data))
        logger.info(f"Cleaned {len(cleaned_data)} PBP records")
        
        with Session(engine) as session:
            # Prepare batch insert with cleaned data
            insert_stmt = insert(PbpRaw).values([
                {
                    'season': season,
                    'week': week,
                    'game_id': str(play.get('game_id', '')),
                    'play_id': str(play.get('play_id', '')),
                    'raw': play,  # Store the cleaned data
                    'created_at': datetime.now(timezone.utc)
                }
                for play in cleaned_data
                if play.get('game_id') and play.get('play_id')
            ])
            
            # Skip duplicates
            on_conflict_stmt = insert_stmt.on_conflict_do_nothing(
                index_elements=['game_id', 'play_id']
            )
            
            try:
                result = session.execute(on_conflict_stmt)
                session.commit()
                rowcount = result.rowcount
                logger.info(f"Inserted {rowcount} new plays")
                
                # Only proceed if we have new data
                if rowcount > 0:
                    # Update player stats
                    logger.info("Updating player week stats...")
                    session.execute(
                        text("SELECT public.recalc_player_week_stats(:season, :week)"),
                        {'season': season, 'week': week}
                    )
                    
                    # Update team stats
                    logger.info("Updating team week stats...")
                    session.execute(
                        text("SELECT public.recalc_team_week_stats(:season, :week)"),
                        {'season': season, 'week': week}
                    )
                    
                    session.commit()
                    logger.info("Successfully updated all stats")
                else:
                    logger.info("No new plays to process")
                    
                return rowcount
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error processing plays: {e}")
                logger.error(f"Full traceback:\n{traceback.format_exc()}")
                raise
                
    except Exception as e:
        logger.error(f"Error processing PBP data: {e}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest play-by-play data')
    parser.add_argument('input_file', help='Path to JSON file containing PBP data')
    parser.add_argument('--season', type=int, required=True, help='Season (e.g., 2023)')
    parser.add_argument('--week', type=int, required=True, help='Week number (1-22)')
    
    args = parser.parse_args()
    
    # Load PBP data
    try:
        with open(args.input_file, 'r') as f:
            pbp_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading PBP data: {str(e)}")
        return
    
    # Process PBP data
    logger.info(f"Processing PBP data for {args.season} week {args.week}")
    process_pbp_data(pbp_data, args.season, args.week)
    logger.info("PBP ingestion complete")

if __name__ == "__main__":
    main()
