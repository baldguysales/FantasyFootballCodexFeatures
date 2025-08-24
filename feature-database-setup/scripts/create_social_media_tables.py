"""
Script to create social media injury related tables in the database.
"""
import os
import sys
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Ensure asyncpg is used for PostgreSQL
if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

# Create async SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def create_social_media_tables():
    """Create social media injury related tables."""
    async with async_session() as session:
        try:
            # Create social_media_injury table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS social_media_injury (
                    tweet_id BIGINT PRIMARY KEY,
                    author_name VARCHAR(100) NOT NULL,
                    author_username VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    tweet_text TEXT NOT NULL,
                    tweet_url VARCHAR(500),
                    player_name VARCHAR(100),
                    team_abbr VARCHAR(3),
                    injury_status VARCHAR(50),
                    body_part VARCHAR(50),
                    timeline VARCHAR(100),
                    confidence_score INTEGER DEFAULT 0,
                    player_id VARCHAR(50),  -- Will add foreign key constraint later
                    team_id INTEGER,        -- Will add foreign key constraint later
                    retweet_count INTEGER DEFAULT 0,
                    favorite_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    quote_count INTEGER DEFAULT 0,
                    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP WITH TIME ZONE,
                    is_verified VARCHAR(20) DEFAULT 'unverified',
                    created_at_table TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes for social_media_injury
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_smi_player_id ON social_media_injury(player_id)
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_smi_team_id ON social_media_injury(team_id)
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_smi_created_at ON social_media_injury(created_at)
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_smi_is_verified ON social_media_injury(is_verified)
            """))
            
            # Create social_media_injury_matches table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS social_media_injury_matches (
                    id SERIAL PRIMARY KEY,
                    tweet_id BIGINT,  -- Will add foreign key constraint later
                    player_id VARCHAR(50),  -- Will add foreign key constraint later
                    match_confidence FLOAT DEFAULT 1.0,
                    match_method VARCHAR(50) DEFAULT 'manual',
                    matched_by VARCHAR(100),
                    matched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tweet_id, player_id)  -- Prevent duplicate matches
                )
            """))
            
            # Create indexes for social_media_injury_matches
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_smim_tweet_id ON social_media_injury_matches(tweet_id)
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_smim_player_id ON social_media_injury_matches(player_id)
            """))
            
            await session.commit()
            logger.info("Successfully created social media injury tables")
            return True
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating social media injury tables: {e}")
            raise

async def verify_tables():
    """Verify that the tables were created with the correct schema."""
    expected_tables = ['social_media_injury', 'social_media_injury_matches']
    missing_tables = []
    
    async with async_session() as session:
        for table in expected_tables:
            result = await session.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)").
                bindparams(table_name=table)
            )
            exists = result.scalar()
            
            if not exists:
                missing_tables.append(table)
    
    if missing_tables:
        logger.error(f"Missing tables: {', '.join(missing_tables)}")
        return False
    
    logger.info("All social media injury tables exist")
    return True

async def main():
    """Main function to execute the table creation."""
    logger.info("Starting social media injury tables creation...")
    
    try:
        # Create tables
        await create_social_media_tables()
        
        # Verify tables were created
        if await verify_tables():
            logger.info("Successfully created and verified social media injury tables")
        else:
            logger.error("Failed to verify social media injury tables")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return 1
    finally:
        await engine.dispose()

if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))
