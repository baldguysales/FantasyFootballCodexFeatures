"""Script to clean up the teamstats table and all its references."""
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

def drop_teamstats_table(engine):
    """Drop the teamstats table and clean up references."""
    with engine.connect() as conn:
        with conn.begin():
            # Check if the teamstats table exists first
            inspector = inspect(engine)
            table_names = [t.lower() for t in inspector.get_table_names()]
            
            if 'teamstats' not in table_names:
                logger.info("ℹ️  teamstats table does not exist, nothing to drop")
                return
                
            # Drop foreign key constraints first
            logger.info("Dropping foreign key constraints...")
            conn.execute(text("""
                -- Drop any foreign keys referencing the teamstats table
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    -- Drop foreign key constraints
                    FOR r IN (SELECT conname, conrelid::regclass AS table_name
                             FROM pg_constraint
                             WHERE confrelid = 'teamstats'::regclass
                             AND contype = 'f')
                    LOOP
                        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %s', 
                                     r.table_name, r.conname);
                        RAISE NOTICE 'Dropped constraint % on table %', r.conname, r.table_name;
                    END LOOP;
                END $$;
                
                -- Drop the teamstats table
                DROP TABLE IF EXISTS teamstats CASCADE;
                
                -- Clean up any remaining references in other tables
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    -- Drop any remaining indexes on teamstats
                    FOR r IN (SELECT indexname
                             FROM pg_indexes
                             WHERE indexname LIKE '%%teamstats%%')
                    LOOP
                        EXECUTE format('DROP INDEX IF EXISTS %s CASCADE', r.indexname);
                        RAISE NOTICE 'Dropped index %', r.indexname;
                    END LOOP;
                END $$;
                
                -- Update any views that might reference teamstats
                DO $$
                DECLARE
                    view_rec RECORD;
                BEGIN
                    -- Drop any views that reference teamstats
                    FOR view_rec IN 
                        SELECT viewname as table_name 
                        FROM pg_views 
                        WHERE definition LIKE '%%teamstats%%' 
                        OR viewname LIKE '%%teamstats%%'
                    LOOP
                        EXECUTE format('DROP VIEW IF EXISTS %s CASCADE', view_rec.table_name);
                        RAISE NOTICE 'Dropped view %', view_rec.table_name;
                    END LOOP;
                END $$;
            """))
            logger.info("✅ Successfully dropped teamstats table and cleaned up references")

def update_models():
    """Update model files to remove TeamStats related code."""
    model_file = "models/stats.py"
    
    try:
        with open(model_file, 'r') as f:
            content = f.read()
        
        # Find the TeamStats class and its base class
        start_idx = content.find('class TeamStatsBase')
        if start_idx != -1:
            # Find the end of the TeamStats class
            end_idx = content.find('class ', start_idx + 1)
            if end_idx == -1:
                end_idx = len(content)
            
            # Remove the classes and any extra whitespace
            new_content = content[:start_idx] + content[end_idx:]
            
            # Remove any extra blank lines
            new_content = '\n'.join([line for line in new_content.split('\n') if line.strip() != ''])
            
            with open(model_file, 'w') as f:
                f.write(new_content)
            logger.info(f"✅ Updated {model_file}")
        else:
            logger.info(f"ℹ️  No TeamStats classes found in {model_file}")
    
    except Exception as e:
        logger.error(f"❌ Error updating {model_file}: {e}")

def main():
    """Main function to clean up the teamstats table."""
    logger.info("Starting cleanup of teamstats table...")
    
    # Update database
    engine = get_db_connection()
    drop_teamstats_table(engine)
    
    # Update model files
    update_models()
    
    logger.info("✅ Cleanup complete")

if __name__ == "__main__":
    main()
