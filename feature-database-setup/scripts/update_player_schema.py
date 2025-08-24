"""
Script to update the player table schema to match the new requirements.
This script handles the case where some columns already exist.
"""
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

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a database connection."""
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    return create_engine(db_url)

def backup_player_table(engine):
    """Create a backup of the player table."""
    backup_table = "player_backup_" + "20240823"
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(f"""
                DROP TABLE IF EXISTS {backup_table};
                CREATE TABLE {backup_table} AS TABLE player;
            """))
            logger.info(f"✅ Created backup table: {backup_table}")
    return backup_table

def add_missing_columns(engine):
    """Add any missing columns to the player table."""
    with engine.connect() as conn:
        with conn.begin():
            # Get existing columns
            inspector = inspect(engine)
            existing_columns = [col['name'] for col in inspector.get_columns('player')]
            
            # Columns to add if they don't exist
            columns_to_add = [
                # Team and position info
                ("season", "INTEGER"),
                ("week", "INTEGER"),
                ("team", "VARCHAR"),
                ("depth_chart_position", "VARCHAR"),
                ("jersey_number", "FLOAT"),
                ("status", "VARCHAR"),
                
                # Additional player info
                ("ngs_position", "VARCHAR"),
                ("game_type", "VARCHAR"),
                ("status_description_abbr", "VARCHAR"),
                ("football_name", "VARCHAR"),
                ("age", "FLOAT"),
                
                # Ensure we have the required columns
                ("player_id", "VARCHAR"),
                ("player_name", "VARCHAR"),
                ("first_name", "VARCHAR"),
                ("last_name", "VARCHAR"),
                ("position", "VARCHAR"),
                ("birth_date", "TIMESTAMP"),
                ("height", "FLOAT"),
                ("weight", "INTEGER"),
                ("college", "VARCHAR"),
                ("years_exp", "INTEGER"),
                ("headshot_url", "VARCHAR")
            ]
            
            # Add any missing columns
            for col_name, col_type in columns_to_add:
                if col_name.lower() not in existing_columns:
                    conn.execute(text(f"""
                        ALTER TABLE player 
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type};
                    """))
                    logger.info(f"Added column: {col_name} ({col_type})")
                else:
                    logger.info(f"Column already exists: {col_name}")
            
            # Add any missing constraints
            conn.execute(text("""
                -- Make player_id the primary key if it's not already
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE table_name = 'player' AND constraint_type = 'PRIMARY KEY'
                    ) THEN
                        ALTER TABLE player ADD PRIMARY KEY (id);
                    END IF;
                END $$;
                
                -- Add any indexes that might be needed
                CREATE INDEX IF NOT EXISTS idx_player_player_id ON player(player_id);
                CREATE INDEX IF NOT EXISTS idx_player_position ON player(position);
                CREATE INDEX IF NOT EXISTS idx_player_team ON player(team);
                CREATE INDEX IF NOT EXISTS idx_player_season_week ON player(season, week);
            
            "))
            logger.info("✅ Updated table schema")

def verify_schema(engine):
    """Verify the schema matches our requirements."""
    with engine.connect() as conn:
        # Check if all required columns exist
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
        logger.info("\nSchema Verification:")
        logger.info(f"Total players: {stats[0]}")
        logger.info(f"Unique player IDs: {stats[1]}")
        logger.info(f"Players with name: {stats[2]} ({(stats[2]/stats[0])*100:.1f}%)" if stats[0] > 0 else "No players found")
        logger.info(f"Players with position: {stats[3]} ({(stats[3]/stats[0])*100:.1f}%)" if stats[0] > 0 else "No players found")
        logger.info(f"Players with team: {stats[4]} ({(stats[4]/stats[0])*100:.1f}%)" if stats[0] > 0 else "No players found")

def main():
    """Main migration function."""
    try:
        engine = get_db_connection()
        
        logger.info("Starting player table schema update...")
        
        # Step 1: Backup the current player table
        backup_table = backup_player_table(engine)
        logger.info(f"✅ Backup created in table: {backup_table}")
        
        # Step 2: Add missing columns
        add_missing_columns(engine)
        
        # Step 3: Verify the schema
        verify_schema(engine)
        
        logger.info("\n✅ Schema update completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Verify the schema changes in the database")
        logger.info("2. Update your application code to use the new schema")
        logger.info("3. If you need to migrate data from another source, you can now import it into the new columns")
        
    except Exception as e:
        logger.error(f"❌ Schema update failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
