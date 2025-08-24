"""
Script to recreate the playerweekstats table with a new schema focused on detailed player statistics.
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
                COMMENT ON COLUMN {backup_table}.id IS 'Original table structure before recreation';
            
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
                
                -- Create the new playerweekstats table with comprehensive statistics
                CREATE TABLE playerweekstats (
                    -- Core identifiers
                    id SERIAL PRIMARY KEY,
                    player_id VARCHAR NOT NULL,
                    
                    -- Player information
                    player_name VARCHAR,
                    player_display_name VARCHAR,
                    position VARCHAR,
                    position_group VARCHAR,
                    headshot_url VARCHAR,
                    recent_team VARCHAR,
                    
                    -- Game context
                    season INTEGER NOT NULL,
                    week INTEGER NOT NULL,
                    season_type VARCHAR,
                    opponent_team VARCHAR,
                    
                    -- Passing statistics
                    completions INTEGER,
                    attempts INTEGER,
                    passing_yards FLOAT,
                    passing_tds INTEGER,
                    interceptions FLOAT,
                    sacks FLOAT,
                    sack_yards FLOAT,
                    sack_fumbles INTEGER,
                    sack_fumbles_lost INTEGER,
                    passing_air_yards FLOAT,
                    passing_yards_after_catch FLOAT,
                    passing_first_downs FLOAT,
                    passing_epa FLOAT,
                    passing_2pt_conversions INTEGER,
                    pacr FLOAT,
                    dakota FLOAT,
                    
                    -- Rushing statistics
                    carries INTEGER,
                    rushing_yards FLOAT,
                    rushing_tds INTEGER,
                    rushing_fumbles FLOAT,
                    rushing_fumbles_lost FLOAT,
                    rushing_first_downs FLOAT,
                    rushing_epa FLOAT,
                    rushing_2pt_conversions INTEGER,
                    
                    -- Receiving statistics
                    receptions INTEGER,
                    targets INTEGER,
                    receiving_yards FLOAT,
                    receiving_tds INTEGER,
                    receiving_fumbles FLOAT,
                    receiving_fumbles_lost FLOAT,
                    receiving_air_yards FLOAT,
                    receiving_yards_after_catch FLOAT,
                    receiving_first_downs FLOAT,
                    receiving_epa FLOAT,
                    receiving_2pt_conversions INTEGER,
                    
                    -- Advanced metrics
                    racr FLOAT,
                    target_share FLOAT,
                    air_yards_share FLOAT,
                    wopr FLOAT,
                    
                    -- Special teams
                    special_teams_tds FLOAT,
                    
                    -- Fantasy points
                    fantasy_points FLOAT,
                    fantasy_points_ppr FLOAT,
                    
                    -- Timestamps
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Constraints
                    CONSTRAINT uq_player_season_week UNIQUE (player_id, season, week)
                );
                
                -- Create indexes for better query performance
                CREATE INDEX IF NOT EXISTS idx_pws_player_id ON playerweekstats(player_id);
                CREATE INDEX IF NOT EXISTS idx_pws_season_week ON playerweekstats(season, week);
                CREATE INDEX IF NOT EXISTS idx_pws_team ON playerweekstats(recent_team);
                CREATE INDEX IF NOT EXISTS idx_pws_position ON playerweekstats(position);
                
                -- Add comments for documentation
                COMMENT ON TABLE playerweekstats IS 'Weekly statistics for players with detailed offensive metrics';
                COMMENT ON COLUMN playerweekstats.player_id IS 'Unique identifier for the player';
                COMMENT ON COLUMN playerweekstats.season IS 'NFL season year';
                COMMENT ON COLUMN playerweekstats.week IS 'Week of the season';
                COMMENT ON COLUMN playerweekstats.season_type IS 'Type of season (REG, POST, PRE)';
                COMMENT ON COLUMN playerweekstats.fantasy_points IS 'Standard fantasy points';
                COMMENT ON COLUMN playerweekstats.fantasy_points_ppr IS 'PPR fantasy points';
            
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
        
        # Check the structure of the new table
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_columns,
                SUM(CASE WHEN column_name = 'player_id' THEN 1 ELSE 0 END) as has_player_id,
                SUM(CASE WHEN column_name = 'season' THEN 1 ELSE 0 END) as has_season,
                SUM(CASE WHEN column_name = 'week' THEN 1 ELSE 0 END) as has_week,
                SUM(CASE WHEN column_name = 'fantasy_points' THEN 1 ELSE 0 END) as has_fantasy_points,
                SUM(CASE WHEN column_name = 'fantasy_points_ppr' THEN 1 ELSE 0 END) as has_fantasy_points_ppr
            FROM information_schema.columns 
            WHERE table_name = 'playerweekstats';
        """))
        
        if result:
            stats = result.fetchone()
            logger.info("\nNew Table Structure:")
            logger.info(f"Total columns: {stats[0]}")
            logger.info(f"Has player_id: {'✅' if stats[1] else '❌'}")
            logger.info(f"Has season: {'✅' if stats[2] else '❌'}")
            logger.info(f"Has week: {'✅' if stats[3] else '❌'}")
            logger.info(f"Has fantasy_points: {'✅' if stats[4] else '❌'}")
            logger.info(f"Has fantasy_points_ppr: {'✅' if stats[5] else '❌'}")

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
