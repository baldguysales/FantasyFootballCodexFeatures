"""
Script to recreate the playerweekstats table with a new schema.
This script will:
1. Create a backup of the current playerweekstats table
2. Drop the existing playerweekstats table
3. Create a new playerweekstats table with the updated schema
"""
import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a database connection."""
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    return create_engine(db_url)

def create_backup(engine):
    """Create a backup of the current playerweekstats table."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_table = f"playerweekstats_backup_{timestamp}"
    
    with engine.connect() as conn:
        with conn.begin():
            # Check if table exists before creating backup
            inspector = inspect(engine)
            if 'playerweekstats' not in [t.lower() for t in inspector.get_table_names()]:
                logger.info("ℹ️  playerweekstats table does not exist, no backup needed")
                return None
                
            # Create backup table
            conn.execute(text(f"""
                DROP TABLE IF EXISTS {backup_table};
                CREATE TABLE {backup_table} AS TABLE playerweekstats;
                
                -- Add a comment to indicate when the backup was created
                COMMENT ON TABLE {backup_table} IS 'Backup of playerweekstats table created at {datetime.now()}';
            
            
            
            """))
            logger.info(f"✅ Created backup table: {backup_table}")
            
            # Verify backup was created
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM {backup_table};
            """))
            count = result.scalar()
            logger.info(f"✅ Backup contains {count} rows")
            
    return backup_table

def drop_and_recreate_table(engine):
    """Drop the existing playerweekstats table and recreate it with the new schema."""
    with engine.connect() as conn:
        with conn.begin():
            # Drop the existing playerweekstats table if it exists
            conn.execute(text("""
                DROP TABLE IF EXISTS playerweekstats CASCADE;
                
                -- Create the new playerweekstats table
                CREATE TABLE playerweekstats (
                    -- Core identifiers
                    id SERIAL PRIMARY KEY,
                    player_id VARCHAR NOT NULL,
                    
                    -- Basic info
                    player_name VARCHAR,
                    first_name VARCHAR,
                    last_name VARCHAR,
                    birth_date TIMESTAMP,
                    height FLOAT,
                    weight INTEGER,
                    college VARCHAR,
                    
                    -- Team and position info
                    team VARCHAR,
                    position VARCHAR,
                    depth_chart_position VARCHAR,
                    jersey_number FLOAT,
                    status VARCHAR,
                    
                    -- Season and week info
                    season INTEGER NOT NULL,
                    week INTEGER NOT NULL,
                    game_type VARCHAR,
                    
                    -- External IDs
                    espn_id VARCHAR,
                    sportradar_id VARCHAR,
                    yahoo_id VARCHAR,
                    rotowire_id VARCHAR,
                    pff_id VARCHAR,
                    pfr_id VARCHAR,
                    fantasy_data_id VARCHAR,
                    sleeper_id VARCHAR,
                    esb_id VARCHAR,
                    gsis_it_id VARCHAR,
                    smart_id VARCHAR,
                    
                    -- Additional info
                    years_exp INTEGER,
                    headshot_url VARCHAR,
                    ngs_position VARCHAR,
                    status_description_abbr VARCHAR,
                    football_name VARCHAR,
                    entry_year INTEGER,
                    rookie_year FLOAT,
                    draft_club VARCHAR,
                    draft_number FLOAT,
                    age FLOAT,
                    
                    -- Timestamps
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Constraints
                    CONSTRAINT uq_player_season_week UNIQUE (player_id, season, week)
                );
                
                -- Create indexes for better query performance
                CREATE INDEX IF NOT EXISTS idx_pws_player_id ON playerweekstats(player_id);
                CREATE INDEX IF NOT EXISTS idx_pws_season_week ON playerweekstats(season, week);
                CREATE INDEX IF NOT EXISTS idx_pws_team ON playerweekstats(team);
                CREATE INDEX IF NOT EXISTS idx_pws_position ON playerweekstats(position);
                
                -- Add comments for documentation
                COMMENT ON TABLE playerweekstats IS 'Weekly statistics for players with detailed attributes';
                COMMENT ON COLUMN playerweekstats.player_id IS 'Unique identifier for the player';
                COMMENT ON COLUMN playerweekstats.season IS 'NFL season year';
                COMMENT ON COLUMN playerweekstats.week IS 'Week of the season';
            
            
            """))
            logger.info("✅ Created new playerweekstats table with updated schema")

def verify_migration(engine, backup_table):
    """Verify the migration was successful."""
    with engine.connect() as conn:
        # Get counts from both tables if backup exists
        if backup_table:
            result = conn.execute(text(f"""
                SELECT 
                    (SELECT COUNT(*) FROM {backup_table}) as backup_count,
                    (SELECT COUNT(*) FROM playerweekstats) as playerweekstats_count;
            """))
            
            backup_count, new_count = result.fetchone()
            
            logger.info("\nMigration Verification:")
            logger.info(f"Rows in backup: {backup_count}")
            logger.info(f"Rows in new table: {new_count}")
            
            if backup_count == new_count:
                logger.info("✅ Row counts match")
            else:
                logger.warning(f"⚠️  Row count mismatch: {backup_count} vs {new_count}")
        else:
            logger.info("\nNo backup table to verify against")
        
        # Check for any data issues in the new table
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT season) as seasons,
                COUNT(DISTINCT week) as weeks,
                COUNT(NULLIF(TRIM(player_name), '')) as players_with_name,
                COUNT(NULLIF(TRIM(position), '')) as players_with_position,
                COUNT(NULLIF(TRIM(team), '')) as players_with_team
            FROM playerweekstats;
        """))
        
        if result:
            stats = result.fetchone()
            logger.info("\nNew Table Statistics:")
            logger.info(f"Total rows: {stats[0]}")
            logger.info(f"Unique players: {stats[1]}")
            logger.info(f"Seasons: {stats[2]}")
            logger.info(f"Weeks: {stats[3]}")
            if stats[0] > 0:
                logger.info(f"Players with name: {stats[4]} ({(stats[4]/stats[0])*100:.1f}%)")
                logger.info(f"Players with position: {stats[5]} ({(stats[5]/stats[0])*100:.1f}%)")
                logger.info(f"Players with team: {stats[6]} ({(stats[6]/stats[0])*100:.1f}%)")

def main():
    """Main function to execute the migration."""
    try:
        engine = get_db_connection()
        
        logger.info("Starting playerweekstats table recreation...")
        
        # Step 1: Create a backup of the current playerweekstats table
        logger.info("\nStep 1: Creating backup of current playerweekstats table...")
        backup_table = create_backup(engine)
        
        # Step 2: Drop and recreate the table with the new schema
        logger.info("\nStep 2: Recreating playerweekstats table with new schema...")
        drop_and_recreate_table(engine)
        
        # Step 3: Verify the migration
        logger.info("\nStep 3: Verifying migration...")
        verify_migration(engine, backup_table)
        
        logger.info("\n✅ Table recreation completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Verify the new playerweekstats table structure")
        if backup_table:
            logger.info(f"2. The original data is available in the backup table: {backup_table}")
            logger.info("3. Once you're confident everything is working, you can drop the backup table with:")
            logger.info(f"   DROP TABLE IF EXISTS {backup_table};")
        
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
