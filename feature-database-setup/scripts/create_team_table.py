"""Script to create the team table in the database."""
import logging
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql import text
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Ensure we're using asyncpg
if not DATABASE_URL.startswith('postgresql+asyncpg'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

async def create_team_table():
    """Create the team table with all specified columns."""
    async with AsyncSession(engine) as session:
        try:
            # Drop the table if it already exists
            await session.execute(text("DROP TABLE IF EXISTS team CASCADE"))
            await session.commit()
            
            # Create the team table
            create_table_sql = """
                CREATE TABLE team (
                    team_abbr VARCHAR(10) PRIMARY KEY,
                    team_name VARCHAR(100) NOT NULL,
                    team_id BIGINT UNIQUE NOT NULL,
                    team_nick VARCHAR(50),
                    team_conf VARCHAR(10),
                    team_division VARCHAR(20),
                    team_color VARCHAR(20),
                    team_color2 VARCHAR(20),
                    team_color3 VARCHAR(20),
                    team_color4 VARCHAR(20),
                    team_logo_wikipedia VARCHAR(255),
                    team_logo_espn VARCHAR(255),
                    team_wordmark VARCHAR(255),
                    team_conference_logo VARCHAR(255),
                    team_league_logo VARCHAR(255),
                    team_logo_squared VARCHAR(255)
                )
            """
            await session.execute(text(create_table_sql))
            
            # Create indexes separately
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_team_conference ON team(team_conf)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_team_division ON team(team_division)"))
            
            await session.commit()
            logger.info("Successfully created team table")
            return True
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating team table: {e}")
            raise

async def verify_team_table():
    """Verify that the team table was created with the correct schema."""
    async with AsyncSession(engine) as session:
        try:
            # Check if table exists
            result = await session.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'team')")
            )
            table_exists = result.scalar()
            
            if not table_exists:
                logger.error("Team table does not exist")
                return False
            
            # Check columns
            result = await session.execute(
                text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'team'")
            )
            
            # Expected columns and types
            expected_columns = {
                'team_abbr': 'character varying',
                'team_name': 'character varying',
                'team_id': 'bigint',
                'team_nick': 'character varying',
                'team_conf': 'character varying',
                'team_division': 'character varying',
                'team_color': 'character varying',
                'team_color2': 'character varying',
                'team_color3': 'character varying',
                'team_color4': 'character varying',
                'team_logo_wikipedia': 'character varying',
                'team_logo_espn': 'character varying',
                'team_wordmark': 'character varying',
                'team_conference_logo': 'character varying',
                'team_league_logo': 'character varying',
                'team_logo_squared': 'character varying'
            }
            
            actual_columns = {row[0]: row[1] for row in result.fetchall()}
            
            # Check if all expected columns exist with correct types
            missing_columns = set(expected_columns.keys()) - set(actual_columns.keys())
            type_mismatches = {
                col: (expected, actual_columns[col])
                for col, expected in expected_columns.items()
                if col in actual_columns and actual_columns[col] != expected
            }
            
            if missing_columns or type_mismatches:
                if missing_columns:
                    logger.error(f"Missing columns: {', '.join(missing_columns)}")
                if type_mismatches:
                    for col, (expected, actual) in type_mismatches.items():
                        logger.error(f"Type mismatch for column {col}: expected {expected}, got {actual}")
                return False
                
            logger.info("Team table schema verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying team table: {e}")
            raise

async def main():
    """Main function to create and verify the team table."""
    logger.info("Starting team table creation...")
    try:
        await create_team_table()
        success = await verify_team_table()
        
        if success:
            logger.info("Successfully created and verified team table")
        else:
            logger.error("Team table verification failed")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
    finally:
        # Properly close the engine
        if engine:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
