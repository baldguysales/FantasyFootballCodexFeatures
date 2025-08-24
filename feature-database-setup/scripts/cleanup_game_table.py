"""Script to clean up the game table and all its references."""
import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

def get_db_connection():
    """Create and return a database connection."""
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    return create_engine(db_url)

def drop_game_table(engine):
    """Drop the game table and clean up references."""
    with engine.connect() as conn:
        with conn.begin():
            # Check if the game table exists first
            inspector = inspect(engine)
            if 'game' not in [t.lower() for t in inspector.get_table_names()]:
                print("ℹ️  Game table does not exist, nothing to drop")
                return
                
            # Drop foreign key constraints first
            conn.execute(text("""
                -- Drop any foreign keys referencing the game table
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    -- Drop foreign key constraints
                    FOR r IN (SELECT conname, conrelid::regclass AS table_name
                             FROM pg_constraint
                             WHERE confrelid = 'game'::regclass
                             AND contype = 'f')
                    LOOP
                        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %s', 
                                     r.table_name, r.conname);
                    END LOOP;
                END $$;
                
                -- Drop the game table
                DROP TABLE IF EXISTS game CASCADE;
                
                -- Drop any remaining objects related to game
                DROP SEQUENCE IF EXISTS game_id_seq CASCADE;
                DROP TYPE IF EXISTS game_status CASCADE;
                DROP TYPE IF EXISTS game_type CASCADE;
            
                -- Clean up any remaining references in other tables
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    -- Drop any columns that reference the game table
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'pbp_raw' 
                        AND column_name = 'game_id'
                    ) THEN
                        ALTER TABLE pbp_raw DROP COLUMN IF EXISTS game_id;
                    END IF;
                    
                    -- Drop any remaining indexes on game_id
                    FOR r IN (SELECT indexname
                             FROM pg_indexes
                             WHERE indexname LIKE '%%game%%')
                    LOOP
                        EXECUTE format('DROP INDEX IF EXISTS %s CASCADE', r.indexname);
                    END LOOP;
                END $$;
            """))
            print("✅ Successfully dropped game table and cleaned up references")

def main():
    """Main function to clean up the game table."""
    print("Starting cleanup of game table...")
    engine = get_db_connection()
    drop_game_table(engine)
    print("✅ Cleanup complete")

if __name__ == "__main__":
    main()
