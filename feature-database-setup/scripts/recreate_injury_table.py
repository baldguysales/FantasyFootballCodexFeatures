#!/usr/bin/env python3
"""
Script to recreate the injuryreport table with a new schema.

This script will:
1. Drop the existing injuryreport table if it exists
2. Create a new injuryreport table with the specified schema
"""
import asyncio
import logging
import os
from typing import List

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ff_codex_gdm_v1.db")

# Create async SQLAlchemy engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def drop_injury_table():
    """Drop the injuryreport table if it exists."""
    async with async_session() as session:
        try:
            await session.execute(text("DROP TABLE IF EXISTS injuryreport CASCADE"))
            await session.commit()
            logger.info("Dropped injuryreport table if it existed")
        except Exception as e:
            logger.error(f"Error dropping injuryreport table: {e}")
            await session.rollback()
            raise

async def create_injury_table():
    """Create the injuryreport table with the new schema."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS injuryreport (
        id SERIAL PRIMARY KEY,
        season INTEGER NOT NULL,
        game_type VARCHAR(10) NOT NULL,
        team VARCHAR(10) NOT NULL,
        week INTEGER NOT NULL,
        gsis_id VARCHAR(50) NOT NULL,
        position VARCHAR(10) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        report_primary_injury VARCHAR(100),
        report_secondary_injury VARCHAR(100),
        report_status VARCHAR(50),
        practice_primary_injury VARCHAR(100),
        practice_secondary_injury VARCHAR(100),
        practice_status VARCHAR(50),
        date_modified TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Add indexes for common query patterns
    index_sql = [
        "CREATE INDEX IF NOT EXISTS idx_injuryreport_gsis_id ON injuryreport (gsis_id)",
        "CREATE INDEX IF NOT EXISTS idx_injuryreport_team_week ON injuryreport (team, week)",
        "CREATE INDEX IF NOT EXISTS idx_injuryreport_season_week ON injuryreport (season, week)",
        "CREATE INDEX IF NOT EXISTS idx_injuryreport_status ON injuryreport (report_status)"
    ]
    
    async with async_session() as session:
        try:
            # Create the table
            await session.execute(text(create_table_sql))
            
            # Create indexes
            for sql in index_sql:
                await session.execute(text(sql))
                
            await session.commit()
            logger.info("Successfully created injuryreport table with new schema")
        except Exception as e:
            logger.error(f"Error creating injuryreport table: {e}")
            await session.rollback()
            raise

async def verify_table_schema():
    """Verify the table was created with the correct schema."""
    expected_columns = {
        'season': 'integer',
        'game_type': 'character varying',
        'team': 'character varying',
        'week': 'integer',
        'gsis_id': 'character varying',
        'position': 'character varying',
        'full_name': 'character varying',
        'first_name': 'character varying',
        'last_name': 'character varying',
        'report_primary_injury': 'character varying',
        'report_secondary_injury': 'character varying',
        'report_status': 'character varying',
        'practice_primary_injury': 'character varying',
        'practice_secondary_injury': 'character varying',
        'practice_status': 'character varying',
        'date_modified': 'timestamp with time zone',
        'created_at': 'timestamp without time zone',
        'updated_at': 'timestamp without time zone'
    }
    
    async with async_session() as session:
        try:
            result = await session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'injuryreport'
            """))
            
            actual_columns = {row[0]: row[1] for row in result}
            actual_columns.pop('id', None)  # Remove id from actual columns
            
            if actual_columns == expected_columns:
                logger.info("Table schema verification passed!")
                return True
            
            logger.error("Table schema verification failed!")
            logger.error(f"Expected: {expected_columns}")
            logger.error(f"Actual: {actual_columns}")
            return False
                
        except Exception as e:
            logger.error(f"Error verifying table schema: {e}")
            return False

async def main():
    """Main function to execute the table recreation."""
    logger.info("Starting injuryreport table recreation...")
    
    try:
        # Drop existing table
        await drop_injury_table()
        
        # Create new table
        await create_injury_table()
        
        # Verify the table was created correctly
        if await verify_table_schema():
            logger.info("Successfully recreated injuryreport table with the correct schema!")
        else:
            logger.error("Failed to verify injuryreport table schema")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return 1
    finally:
        # Dispose of the engine
        await engine.dispose()

if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    exit(exit_code)
