"""
Script to recreate the player table with the new schema.
This script will:
1. Create a backup of the current player table
2. Drop the existing player table
3. Create a new player table with the updated schema
4. Migrate data from the backup to the new table
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
    """Create a backup of the current player table."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_table = f"player_backup_{timestamp}"
    
    with engine.connect() as conn:
        with conn.begin():
            # Create backup table
            conn.execute(text(f"""
                DROP TABLE IF EXISTS {backup_table};
                CREATE TABLE {backup_table} AS TABLE player;
                
                -- Add a comment to indicate when the backup was created
                COMMENT ON TABLE {backup_table} IS 'Backup of player table created at {datetime.now()}';
            
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
    """Drop the existing player table and recreate it with the new schema."""
    with engine.connect() as conn:
        with conn.begin():
            # Drop the existing player table if it exists
            conn.execute(text("""
                DROP TABLE IF EXISTS player CASCADE;
                
                -- Create the new player table
                CREATE TABLE player (
                    -- Core identifiers
                    player_id VARCHAR PRIMARY KEY,
                    
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
                    
                    -- Season and game info
                    season INTEGER,
                    week INTEGER,
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create indexes for better query performance
                CREATE INDEX IF NOT EXISTS idx_player_team ON player(team);
                CREATE INDEX IF NOT EXISTS idx_player_position ON player(position);
                CREATE INDEX IF NOT EXISTS idx_player_season_week ON player(season, week);
                CREATE INDEX IF NOT EXISTS idx_player_name ON player(player_name);
                
                -- Add comments for documentation
                COMMENT ON TABLE player IS 'Player information table with detailed attributes';
                COMMENT ON COLUMN player.player_id IS 'Unique identifier for the player';
                COMMENT ON COLUMN player.season IS 'NFL season year';
                COMMENT ON COLUMN player.week IS 'Week of the season';
                
            
            """))
            logger.info("✅ Created new player table with updated schema")

def migrate_data(engine, backup_table):
    """Migrate data from the backup table to the new player table."""
    with engine.connect() as conn:
        with conn.begin():
            # Get column names from the backup table
            result = conn.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{backup_table}'
                ORDER BY ordinal_position;
            """))
            
            old_columns = [row[0] for row in result]
            
            # Create a mapping of old columns to new columns
            column_mapping = {
                # Map 'id' to 'player_id' if 'player_id' doesn't exist
                'id': 'player_id',
                # Only include player_id if it's different from 'id'
                **({'player_id': 'player_id'} if 'player_id' in old_columns and 'id' != 'player_id' else {}),
                # Other columns
                'espn_id': 'espn_id',
                'sportradar_id': 'sportradar_id',
                'yahoo_id': 'yahoo_id',
                'rotowire_id': 'rotowire_id',
                'pff_id': 'pff_id',
                'pfr_id': 'pfr_id',
                'fantasy_data_id': 'fantasy_data_id',
                'sleeper_id': 'sleeper_id',
                'esb_id': 'esb_id',
                'gsis_it_id': 'gsis_it_id',
                'smart_id': 'smart_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'player_name': 'player_name',
                'birth_date': 'birth_date',
                'height': 'height',
                'weight': 'weight',
                'college': 'college',
                'position': 'position',
                'years_exp': 'years_exp',
                'entry_year': 'entry_year',
                'rookie_year': 'rookie_year',
                'draft_club': 'draft_club',
                'draft_number': 'draft_number',
                'status_description_abbr': 'status_description_abbr',
                'headshot_url': 'headshot_url',
                'updated_at': 'updated_at',
                'created_at': 'created_at'
            }
            
            # Build the column lists for the INSERT statement
            source_columns = []
            target_columns = []
            
            # Track which columns we've already added to avoid duplicates
            added_columns = set()
            
            for old_col in old_columns:
                if old_col in column_mapping and column_mapping[old_col] not in added_columns:
                    source_columns.append(old_col)
                    target_columns.append(column_mapping[old_col])
                    added_columns.add(column_mapping[old_col])
            
            # Only proceed if we have columns to migrate
            if not source_columns:
                logger.warning("No matching columns found for migration")
                return
            
            # Build and execute the migration query
            source_cols = ", ".join(f'"{col}"' for col in source_columns)
            target_cols = ", ".join(f'"{col}"' for col in target_columns)
            
            # Remove created_at and updated_at from the column lists since we'll set them explicitly
            target_columns = [col for col in target_columns if col not in ['created_at', 'updated_at']]
            source_columns = [col for col in source_columns if col not in ['created_at', 'updated_at']]
            
            # Build the SELECT part of the query
            select_columns = []
            for col in source_columns:
                if col in old_columns:
                    select_columns.append(f'"{col}"')
                else:
                    select_columns.append('NULL')
            
            # Execute the migration query
            conn.execute(text(f"""
                INSERT INTO player ({', '.join(f'"{col}"' for col in target_columns)}, created_at, updated_at)
                SELECT 
                    {', '.join(select_columns)},
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                FROM {backup_table};
            """))
            
            # Verify the migration
            result = conn.execute(text("SELECT COUNT(*) FROM player;"))
            count = result.scalar()
            logger.info(f"✅ Migrated {count} rows to the new player table")

def verify_migration(engine, backup_table):
    """Verify the migration was successful."""
    with engine.connect() as conn:
        # Get counts from both tables
        result = conn.execute(text(f"""
            SELECT 
                (SELECT COUNT(*) FROM {backup_table}) as backup_count,
                (SELECT COUNT(*) FROM player) as player_count;
        """))
        
        backup_count, player_count = result.fetchone()
        
        logger.info("\nMigration Verification:")
        logger.info(f"Rows in backup: {backup_count}")
        logger.info(f"Rows in new table: {player_count}")
        
        if backup_count == player_count:
            logger.info("✅ Row counts match")
        else:
            logger.warning(f"⚠️  Row count mismatch: {backup_count} vs {player_count}")
        
        # Check for any data issues
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_players,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(NULLIF(TRIM(player_name), '')) as players_with_name,
                COUNT(NULLIF(TRIM(position), '')) as players_with_position,
                COUNT(NULLIF(TRIM(team), '')) as players_with_team
            FROM player;
        """))
        
        stats = result.fetchone()
        logger.info("\nData Quality Check:")
        logger.info(f"Total players: {stats[0]}")
        logger.info(f"Unique player IDs: {stats[1]}")
        logger.info(f"Players with name: {stats[2]} ({(stats[2]/stats[0])*100:.1f}%)" if stats[0] > 0 else "No players found")
        logger.info(f"Players with position: {stats[3]} ({(stats[3]/stats[0])*100:.1f}%)" if stats[0] > 0 else "No players found")
        logger.info(f"Players with team: {stats[4]} ({(stats[4]/stats[0])*100:.1f}%)" if stats[0] > 0 else "No players found")

def main():
    """Main function to execute the migration."""
    try:
        engine = get_db_connection()
        
        logger.info("Starting player table migration...")
        
        # Step 1: Create a backup of the current player table
        logger.info("\nStep 1: Creating backup of current player table...")
        backup_table = create_backup(engine)
        
        # Step 2: Drop and recreate the table with the new schema
        logger.info("\nStep 2: Recreating player table with new schema...")
        drop_and_recreate_table(engine)
        
        # Step 3: Migrate data from the backup
        logger.info("\nStep 3: Migrating data from backup...")
        migrate_data(engine, backup_table)
        
        # Step 4: Verify the migration
        logger.info("\nStep 4: Verifying migration...")
        verify_migration(engine, backup_table)
        
        logger.info("\n✅ Migration completed successfully!")
        logger.info("\nNext steps:")
        logger.info(f"1. Verify the data in the new player table")
        logger.info(f"2. The original data is available in the backup table: {backup_table}")
        logger.info("3. Update your application code to use the new schema")
        logger.info("4. Once you're confident everything is working, you can drop the backup table with:")
        logger.info(f"   DROP TABLE IF EXISTS {backup_table};")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
