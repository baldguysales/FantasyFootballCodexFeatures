"""Script to clean up all remaining references to the teams table and Team class."""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create database engine
db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
engine = create_engine(db_url)

def update_player_schema():
    """Update the player schema to remove team_id foreign key."""
    with engine.connect() as conn:
        with conn.begin():
            # Check if the player table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'player'
                );
            """)).scalar()
            
            if not result:
                print("ℹ️  Player table does not exist, skipping schema update")
                return
                
            # Check if the team_id column exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'player' AND column_name = 'team_id'
                );
            """)).scalar()
            
            if result:
                # Drop the foreign key constraint
                conn.execute(text("""
                    ALTER TABLE player 
                    DROP CONSTRAINT IF EXISTS player_team_id_fkey;
                    
                    ALTER TABLE player 
                    DROP COLUMN IF EXISTS team_id;
                
                    ALTER TABLE player 
                    DROP COLUMN IF EXISTS team_abbr;
                
                    ALTER TABLE player 
                    DROP COLUMN IF EXISTS jersey_number;
                
                    ALTER TABLE player 
                    DROP COLUMN IF EXISTS status;
                
                    ALTER TABLE player 
                    DROP COLUMN IF EXISTS depth_chart_position;
                
                    ALTER TABLE player 
                    DROP COLUMN IF EXISTS ngs_position;
                """))
                print("✅ Updated player table schema")
            else:
                print("ℹ️  No team-related columns found in player table")

def update_sql_files():
    """Update SQL files to remove references to the team table."""
    sql_files = [
        "scripts/update_player_schema.sql"
    ]
    
    base_path = Path(__file__).parent.parent
    
    for file_path in sql_files:
        full_path = base_path / file_path
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Remove team-related SQL
            new_content = []
            skip = False
            for line in content.splitlines():
                if '-- Team information' in line:
                    skip = True
                    continue
                if skip and line.strip() == '':  # Stop skipping at the next empty line
                    skip = False
                    continue
                if not skip:
                    new_content.append(line + '\n')
            
            # Write the updated content back to the file
            with open(full_path, 'w') as f:
                f.writelines(new_content)
                
            print(f"✅ Updated {file_path}")
            
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")

if __name__ == "__main__":
    print("Starting cleanup of team table references...")
    
    # Update database schema
    print("\nUpdating database schema...")
    update_player_schema()
    
    # Clean up SQL files
    print("\nUpdating SQL files...")
    update_sql_files()
    
    print("\n✅ Cleanup complete. Please verify the changes and commit them to version control.")
