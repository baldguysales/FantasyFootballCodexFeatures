"""Script to clean up the favoriteplayer table and all its references."""
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

def drop_favoriteplayer_table():
    """Drop the favoriteplayer table and clean up references."""
    with engine.connect() as conn:
        # Start a transaction
        with conn.begin():
            # Drop foreign key constraints first
            conn.execute(text("""
                DO $$
                BEGIN
                    -- Drop foreign key from user table if it exists
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.table_constraints 
                        WHERE constraint_name = 'favoriteplayer_user_id_fkey'
                    ) THEN
                        ALTER TABLE favoriteplayer DROP CONSTRAINT IF EXISTS favoriteplayer_user_id_fkey;
                    END IF;
                    
                    -- Drop foreign key from player table if it exists
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.table_constraints 
                        WHERE constraint_name = 'favoriteplayer_player_id_fkey'
                    ) THEN
                        ALTER TABLE favoriteplayer DROP CONSTRAINT IF EXISTS favoriteplayer_player_id_fkey;
                    END IF;
                END $$;
            
                -- Drop the favoriteplayer table if it exists
                DROP TABLE IF EXISTS favoriteplayer CASCADE;
            """))
            
            # Verify the table was dropped
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'favoriteplayer'
                );
            """)).scalar()
            
            if not result:
                print("✅ Successfully dropped favoriteplayer table")
            else:
                print("❌ Failed to drop favoriteplayer table")

def remove_favoriteplayer_references():
    """Remove all code references to FavoritePlayer in the codebase."""
    # List of files to modify
    files_to_update = [
        "models/nfl.py",
        "models/user.py",
        "models/fantasy.py"
    ]
    
    base_path = Path(__file__).parent.parent
    
    for file_path in files_to_update:
        full_path = base_path / file_path
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Remove FavoritePlayer related code
            if file_path == "models/nfl.py":
                content = content.replace(
                    '    favorite_of: List["FavoritePlayer"] = Relationship(back_populates="player")',
                    '    # favorite_of relationship removed - favorite player functionality deprecated'
                )
            elif file_path == "models/user.py":
                content = content.replace(
                    '    favorite_players: List["FavoritePlayer"] = Relationship(back_populates="user")',
                    '    # favorite_players relationship removed - favorite player functionality deprecated'
                )
            elif file_path == "models/fantasy.py":
                # Remove FavoritePlayer related classes and imports
                content = ""
                with open(full_path, 'r') as f:
                    lines = f.readlines()
                
                new_lines = []
                skip = False
                for line in lines:
                    if "class FavoritePlayer" in line:
                        skip = True
                    elif skip and line.strip() == "":  # Stop skipping at the next empty line after the class
                        skip = False
                        continue
                    
                    if not skip:
                        new_lines.append(line)
                
                content = "".join(new_lines)
                
                # Remove any remaining references
                content = content.replace("from .fantasy import FantasyRoster, FavoritePlayer",
                                        "from .fantasy import FantasyRoster")
                content = content.replace("from .fantasy import FantasyRoster, FavoritePlayer, FavoritePlayerCreate, FavoritePlayerRead",
                                        "from .fantasy import FantasyRoster")
            
            # Write the updated content back to the file
            with open(full_path, 'w') as f:
                f.write(content)
                
            print(f"✅ Updated {file_path}")
            
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")

if __name__ == "__main__":
    print("Starting cleanup of favoriteplayer table and references...")
    
    # Drop the table first
    print("\nDropping favoriteplayer table...")
    drop_favoriteplayer_table()
    
    # Clean up code references
    print("\nRemoving code references...")
    remove_favoriteplayer_references()
    
    print("\n✅ Cleanup complete. Please verify the changes and commit them to version control.")
