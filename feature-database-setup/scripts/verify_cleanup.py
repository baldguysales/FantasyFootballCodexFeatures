"""Script to verify the cleanup of team-related tables and references."""
import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

def get_db_connection():
    """Create and return a database connection."""
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    return create_engine(db_url)

def check_table_exists(engine, table_name):
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def check_columns(engine, table_name, expected_columns):
    """Check if a table has the expected columns."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    
    print(f"\nTable: {table_name}")
    print("-" * 50)
    
    # Check for unexpected columns
    unexpected = [col for col in columns if col not in expected_columns]
    if unexpected:
        print(f"⚠️  Unexpected columns: {', '.join(unexpected)}")
    
    # Check for missing columns
    missing = [col for col in expected_columns if col not in columns]
    if missing:
        print(f"⚠️  Missing columns: {', '.join(missing)}")
    
    print("Current columns:", ", ".join(columns))
    return not (unexpected or missing)

def check_team_columns(engine, table_name):
    """Check for any team-related columns in a table."""
    inspector = inspect(engine)
    columns = [col['name'].lower() for col in inspector.get_columns(table_name)]
    team_columns = [col for col in columns if 'team' in col or 'club' in col]
    
    if team_columns:
        print(f"⚠️  Found team-related columns in {table_name}: {', '.join(team_columns)}")
        return False
    return True

def verify_cleanup():
    """Verify that all team-related tables and references have been removed."""
    engine = get_db_connection()
    
    print("🔍 Verifying database cleanup...")
    
    # Check for team-related tables (case-insensitive)
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    team_tables = [name for name in all_tables if 'team' in name.lower()]
    
    if team_tables:
        print(f"⚠️  Found potential team-related tables: {', '.join(team_tables)}")
    else:
        print("✅ No team-related tables found")
    
    # Check all tables for team-related columns
    print("\n🔎 Checking for team-related columns in all tables...")
    all_clean = True
    for table in all_tables:
        if not check_team_columns(engine, table):
            all_clean = False
    
    if all_clean:
        print("✅ No team-related columns found in any tables")
    
    # Check player table columns
    if check_table_exists(engine, 'player'):
        expected_columns = [
            'id', 'player_id', 'espn_id', 'sportradar_id', 'yahoo_id', 
            'rotowire_id', 'pff_id', 'pfr_id', 'fantasy_data_id', 'sleeper_id',
            'esb_id', 'gsis_it_id', 'smart_id', 'first_name', 'last_name',
            'player_name', 'birth_date', 'height', 'weight', 'college',
            'position', 'years_exp', 'entry_year', 'rookie_year', 'draft_club',
            'draft_number', 'created_at', 'updated_at'
        ]
        check_columns(engine, 'player', expected_columns)
    else:
        print("ℹ️  Player table does not exist")
    
    # Check for any remaining foreign keys to team
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                tc.table_schema, 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE 
                tc.constraint_type = 'FOREIGN KEY' 
                AND ccu.table_name = 'team';
        """))
        
        foreign_keys = result.fetchall()
        if foreign_keys:
            print("\n❌ Found foreign keys referencing team table:")
            for fk in foreign_keys:
                print(f"- {fk[1]}.{fk[2]} references {fk[4]}.{fk[5]}")
        else:
            print("\n✅ No foreign keys reference the team table")
    
    print("\n✅ Verification complete")

if __name__ == "__main__":
    verify_cleanup()
