"""Script to clear all data from the player table."""
import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_players():
    """Delete all records from the player and weekly_roster tables."""
    # Load environment variables
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL").replace('+asyncpg', '')
    
    # Create engine and connect to database
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # First delete from weekly_roster (child table)
            result = conn.execute(text("DELETE FROM weekly_roster"))
            logger.info(f"Deleted {result.rowcount} records from weekly_roster table.")
            
            # Then delete from player table
            result = conn.execute(text("DELETE FROM player"))
            conn.commit()
            logger.info(f"Successfully deleted {result.rowcount} players from the database.")
            return True
    except Exception as e:
        logger.error(f"Error clearing player table: {e}")
        return False

if __name__ == "__main__":
    if clear_players():
        logger.info("Player table cleared successfully.")
    else:
        logger.error("Failed to clear player table.")
