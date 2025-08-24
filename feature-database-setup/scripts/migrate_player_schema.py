"""
Migration script to update the player table schema:
1. Adds new columns for player attributes
2. Migrates data from JSON stats to dedicated columns
3. Drops old columns after migration
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, text, Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection
def get_db_connection():
    """Create and return a database connection."""
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    return create_engine(db_url)

def backup_player_table(engine):
    """Create a backup of the player table."""
    backup_table = "player_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(f"""
                CREATE TABLE {backup_table} AS TABLE player;
            """))
            logger.info(f"✅ Created backup table: {backup_table}")
    return backup_table

def add_new_columns(engine):
    """Add new columns to the player table."""
    with engine.connect() as conn:
        with conn.begin():
            # Add new columns
            conn.execute(text("""
                -- Team and position info
                ALTER TABLE player ADD COLUMN IF NOT EXISTS team VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS position VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS depth_chart_position VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS jersey_number FLOAT;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS status VARCHAR;
                
                -- Player info
                ALTER TABLE player ADD COLUMN IF NOT EXISTS player_name VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS first_name VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS last_name VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS birth_date TIMESTAMP;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS height FLOAT;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS weight INTEGER;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS college VARCHAR;
                
                -- External IDs
                ALTER TABLE player ADD COLUMN IF NOT EXISTS espn_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS sportradar_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS yahoo_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS rotowire_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS pff_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS pfr_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS fantasy_data_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS sleeper_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS esb_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS gsis_it_id VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS smart_id VARCHAR;
                
                -- Additional info
                ALTER TABLE player ADD COLUMN IF NOT EXISTS years_exp INTEGER;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS headshot_url VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS ngs_position VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS game_type VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS status_description_abbr VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS football_name VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS entry_year INTEGER;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS rookie_year FLOAT;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS draft_club VARCHAR;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS draft_number FLOAT;
                ALTER TABLE player ADD COLUMN IF NOT EXISTS age FLOAT;
            
                -- Ensure required columns have proper constraints
                ALTER TABLE player ALTER COLUMN season SET NOT NULL;
                ALTER TABLE player ALTER COLUMN player_id SET NOT NULL;
            
            """))
            logger.info("✅ Added new columns to player table")

def migrate_data(engine):
    """Migrate data from JSON stats to the new columns."""
    with engine.connect() as conn:
        with conn.begin():
            # Get all player records with stats
            result = conn.execute(text("""
                SELECT id, stats FROM player WHERE stats IS NOT NULL;
            """))
            
            players = result.fetchall()
            logger.info(f"Found {len(players)} players with stats to migrate")
            
            for player_id, stats_json in players:
                try:
                    if not stats_json:
                        continue
                        
                    # Parse the JSON stats
                    stats = json.loads(stats_json) if isinstance(stats_json, str) else stats_json
                    
                    # Prepare the update query
                    update_data = {}
                    
                    # Map JSON fields to columns
                    field_mapping = {
                        'team': 'team',
                        'position': 'position',
                        'depth_chart_position': 'depth_chart_position',
                        'jersey_number': 'jersey_number',
                        'status': 'status',
                        'player_name': 'player_name',
                        'first_name': 'first_name',
                        'last_name': 'last_name',
                        'birth_date': 'birth_date',
                        'height': 'height',
                        'weight': 'weight',
                        'college': 'college',
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
                        'years_exp': 'years_exp',
                        'headshot_url': 'headshot_url',
                        'ngs_position': 'ngs_position',
                        'game_type': 'game_type',
                        'status_description_abbr': 'status_description_abbr',
                        'football_name': 'football_name',
                        'entry_year': 'entry_year',
                        'rookie_year': 'rookie_year',
                        'draft_club': 'draft_club',
                        'draft_number': 'draft_number',
                        'age': 'age'
                    }
                    
                    # Build the SET clause for the update
                    set_clauses = []
                    params = {}
                    
                    for json_field, column in field_mapping.items():
                        if json_field in stats and stats[json_field] is not None:
                            set_clauses.append(f"{column} = :{column}")
                            params[column] = stats[json_field]
                    
                    # Only update if we have fields to update
                    if set_clauses:
                        update_query = f"""
                            UPDATE player 
                            SET {set_clause} 
                            WHERE id = :player_id
                        """.format(set_clause=", ".join(set_clauses))
                        
                        params['player_id'] = player_id
                        conn.execute(text(update_query), params)
            
                except Exception as e:
                    logger.error(f"Error migrating player {player_id}: {e}")
                    continue
            
            logger.info("✅ Migrated player data to new columns")

def drop_old_columns(engine):
    """Drop the old columns after migration."""
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text("""
                -- Drop the old columns
                ALTER TABLE player 
                DROP COLUMN IF EXISTS stats,
                DROP COLUMN IF EXISTS created_at,
                DROP COLUMN IF EXISTS is_official,
                DROP COLUMN IF EXISTS last_updated,
                DROP COLUMN IF EXISTS source,
                DROP COLUMN IF EXISTS source_id;
            
                -- Rename id to player_id if needed
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='player' AND column_name='id') THEN
                        ALTER TABLE player RENAME COLUMN id TO player_id;
                    END IF;
                END $$;
            
            """))
            logger.info("✅ Dropped old columns")

def verify_migration(engine):
    """Verify the migration was successful."""
    with engine.connect() as conn:
        # Check if new columns exist and have data
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_players,
                COUNT(player_name) as players_with_name,
                COUNT(position) as players_with_position,
                COUNT(team) as players_with_team
            FROM player;
        """))
        
        stats = result.fetchone()
        logger.info("\nMigration Verification:")
        logger.info(f"Total players: {stats[0]}")
        logger.info(f"Players with name: {stats[1]} ({(stats[1]/stats[0])*100:.1f}%)")
        logger.info(f"Players with position: {stats[2]} ({(stats[2]/stats[0])*100:.1f}%)")
        logger.info(f"Players with team: {stats[3]} ({(stats[3]/stats[0])*100:.1f}%)")

def main():
    """Main migration function."""
    try:
        engine = get_db_connection()
        
        logger.info("Starting player table migration...")
        
        # Step 1: Backup the current player table
        backup_table = backup_player_table(engine)
        logger.info(f"✅ Backup created in table: {backup_table}")
        
        # Step 2: Add new columns
        add_new_columns(engine)
        
        # Step 3: Migrate data from JSON to new columns
        migrate_data(engine)
        
        # Step 4: Verify the migration
        verify_migration(engine)
        
        # Step 5: Drop old columns (uncomment when ready)
        # drop_old_columns(engine)
        
        logger.info("\n✅ Migration completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Verify the data in the new columns")
        logger.info("2. Test your application with the new schema")
        logger.info(f"3. If everything looks good, uncomment the 'drop_old_columns' call in the script")
        logger.info("4. Run the script again to drop the old columns")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
