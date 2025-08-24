"""Script to clean up the weekly_roster table and all its references."""
import os
import logging
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection."""
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    return create_engine(db_url)

def drop_weekly_roster_table(engine):
    """Drop the weekly_roster table and clean up references."""
    with engine.connect() as conn:
        with conn.begin():
            # Check if the weekly_roster table exists first
            inspector = inspect(engine)
            table_names = [t.lower() for t in inspector.get_table_names()]
            
            if 'weekly_roster' not in table_names:
                logger.info("ℹ️  weekly_roster table does not exist, nothing to drop")
                return
                
            # Drop foreign key constraints first
            logger.info("Dropping foreign key constraints...")
            conn.execute(text("""
                -- Drop any foreign keys referencing the weekly_roster table
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    -- Drop foreign key constraints
                    FOR r IN (SELECT conname, conrelid::regclass AS table_name
                             FROM pg_constraint
                             WHERE confrelid = 'weekly_roster'::regclass
                             AND contype = 'f')
                    LOOP
                        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %s', 
                                     r.table_name, r.conname);
                        RAISE NOTICE 'Dropped constraint % on table %', r.conname, r.table_name;
                    END LOOP;
                END $$;
                
                -- Drop the weekly_roster table
                DROP TABLE IF EXISTS weekly_roster CASCADE;
                
                -- Drop any remaining objects related to weekly_roster
                DROP SEQUENCE IF EXISTS weekly_roster_id_seq CASCADE;
                
                -- Clean up any remaining references in other tables
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    -- Drop any columns that reference weekly_roster
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'player' 
                        AND column_name = 'weekly_roster_id'
                    ) THEN
                        ALTER TABLE player DROP COLUMN IF EXISTS weekly_roster_id;
                        RAISE NOTICE 'Dropped column weekly_roster_id from player table';
                    END IF;
                    
                    -- Drop any remaining indexes on weekly_roster
                    FOR r IN (SELECT indexname
                             FROM pg_indexes
                             WHERE indexname LIKE '%%weekly_roster%%')
                    LOOP
                        EXECUTE format('DROP INDEX IF EXISTS %s CASCADE', r.indexname);
                        RAISE NOTICE 'Dropped index %', r.indexname;
                    END LOOP;
                END $$;
            
                -- Update any views that might reference weekly_roster
                DO $$
                DECLARE
                    view_rec RECORD;
                BEGIN
                    -- Drop any views that reference weekly_roster
                    FOR view_rec IN 
                        SELECT viewname as table_name 
                        FROM pg_views 
                        WHERE definition LIKE '%%weekly_roster%%' 
                        OR viewname LIKE '%%weekly_roster%%'
                    LOOP
                        EXECUTE format('DROP VIEW IF EXISTS %s CASCADE', view_rec.table_name);
                        RAISE NOTICE 'Dropped view %', view_rec.table_name;
                    END LOOP;
                END $$;
            """))
            logger.info("✅ Successfully dropped weekly_roster table and cleaned up references")

def update_models():
    """Update model files to remove WeeklyRoster related code."""
    model_files = [
        "models/roster.py",
        "models/nfl.py"
    ]
    
    for file_path in model_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Remove WeeklyRoster related code
            if 'roster.py' in file_path:
                # Find the start and end of the WeeklyRoster class
                start_idx = content.find('class WeeklyRoster')
                if start_idx != -1:
                    end_idx = content.find('class WeeklyRosterCreate', start_idx)
                    if end_idx == -1:
                        end_idx = content.find('class ', start_idx + 1)
                    if end_idx == -1:
                        end_idx = len(content)
                    
                    # Remove the class and any extra whitespace
                    new_content = content[:start_idx] + content[end_idx:]
                    # Remove any extra blank lines
                    new_content = '\n'.join([line for line in new_content.split('\n') if line.strip() != ''])
                    
                    # Remove imports if they're no longer needed
                    if 'WeeklyRoster' not in new_content:
                        new_content = new_content.replace('from typing import List, Optional, Dict, Any, Union\n', '')
                        new_content = new_content.replace('from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint\n', '')
                        new_content = new_content.replace('from sqlalchemy.orm import Relationship\n', '')
                        new_content = new_content.replace('from datetime import datetime\n', '')
                        new_content = new_content.replace('from pydantic import Field\n', '')
                        new_content = new_content.replace('from .base import Base, BaseModel\n', '')
                    
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                    logger.info(f"✅ Updated {file_path}")
            
            elif 'nfl.py' in file_path:
                # Remove the relationship to WeeklyRoster
                if 'weekly_rosters: List["WeeklyRoster"] = Relationship(back_populates="player")' in content:
                    content = content.replace(
                        '    weekly_rosters: List["WeeklyRoster"] = Relationship(back_populates="player")',
                        ''
                    )
                    with open(file_path, 'w') as f:
                        f.write(content)
                    logger.info(f"✅ Updated {file_path}")
        
        except Exception as e:
            logger.error(f"❌ Error updating {file_path}: {e}")

def main():
    """Main function to clean up the weekly_roster table."""
    logger.info("Starting cleanup of weekly_roster table...")
    
    # Update database
    engine = get_db_connection()
    drop_weekly_roster_table(engine)
    
    # Update model files
    update_models()
    
    logger.info("✅ Cleanup complete")

if __name__ == "__main__":
    main()
