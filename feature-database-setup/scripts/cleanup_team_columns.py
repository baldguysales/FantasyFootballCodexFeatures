"""Script to clean up remaining team-related columns from the database."""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def get_db_connection():
    """Create and return a database connection."""
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    return create_engine(db_url)

def drop_team_columns(engine):
    """Drop team-related columns from all tables."""
    with engine.connect() as conn:
        with conn.begin():
            # Drop columns from player table
            conn.execute(text("""
                ALTER TABLE IF EXISTS player 
                DROP COLUMN IF EXISTS draft_club,
                DROP COLUMN IF EXISTS status_description_abbr,
                DROP COLUMN IF EXISTS headshot_url;
            
                -- Drop columns from weekly_roster
                ALTER TABLE IF EXISTS weekly_roster 
                DROP COLUMN IF EXISTS team_id;
                
                -- Drop columns from usersettings
                ALTER TABLE IF EXISTS usersettings 
                DROP COLUMN IF EXISTS nfl_team_colors;
                
                -- Drop teamstats table if it exists
                DROP TABLE IF EXISTS teamstats CASCADE;
            
                -- Drop game table columns
                ALTER TABLE IF EXISTS game 
                DROP COLUMN IF EXISTS home_team_id,
                DROP COLUMN IF EXISTS away_team_id;
            
                -- Drop any remaining team-related constraints
                DO $$
                BEGIN
                    -- Drop any remaining foreign key constraints
                    FOR r IN (
                        SELECT conname, conrelid::regclass AS table_name
                        FROM pg_constraint
                        WHERE conname LIKE '%team%' 
                        AND contype = 'f'
                    ) LOOP
                        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT IF EXISTS %s', 
                                     r.table_name, r.conname);
                    END LOOP;
                    
                    -- Drop any remaining team-related indexes
                    FOR r IN (
                        SELECT indexname, tablename
                        FROM pg_indexes
                        WHERE indexname LIKE '%team%' 
                           OR indexname LIKE '%club%'
                    ) LOOP
                        EXECUTE format('DROP INDEX IF EXISTS %s CASCADE', r.indexname);
                    END LOOP;
                END $$;
            
                -- Drop any remaining team-related sequences
                DO $$
                BEGIN
                    FOR r IN (
                        SELECT sequence_name
                        FROM information_schema.sequences
                        WHERE sequence_name LIKE '%team%' 
                           OR sequence_name LIKE '%club%'
                    ) LOOP
                        EXECUTE format('DROP SEQUENCE IF EXISTS %s CASCADE', r.sequence_name);
                    END LOOP;
                END $$;
            
                -- Drop any remaining team-related views
                DO $$
                BEGIN
                    FOR r IN (
                        SELECT table_name
                        FROM information_schema.views
                        WHERE table_name LIKE '%team%' 
                           OR table_name LIKE '%club%'
                    ) LOOP
                        EXECUTE format('DROP VIEW IF EXISTS %s CASCADE', r.table_name);
                    END LOOP;
                END $$;
            
                -- Drop any remaining team-related functions
                DO $$
                BEGIN
                    FOR r IN (
                        SELECT proname
                        FROM pg_proc
                        WHERE proname LIKE '%team%' 
                           OR proname LIKE '%club%'
                    ) LOOP
                        EXECUTE format('DROP FUNCTION IF EXISTS %s CASCADE', r.proname);
                    END LOOP;
                END $$;
            """))
            print("✅ Successfully cleaned up team-related database objects")

def main():
    """Main function to clean up team-related columns."""
    print("Starting cleanup of team-related columns...")
    engine = get_db_connection()
    drop_team_columns(engine)
    print("✅ Cleanup complete")

if __name__ == "__main__":
    main()
