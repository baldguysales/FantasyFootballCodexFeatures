"""Script to update the database schema to match nfl_data_py data structure."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env file")
    sys.exit(1)

# Create engine with psycopg2
engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))

def run_sql_file(filename):
    """Run SQL commands from a file."""
    with engine.connect() as conn:
        with open(filename, 'r') as f:
            sql = f.read()
            
        # Split SQL into individual statements
        statements = sql.split(';')
        
        # Execute each statement
        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
                
            try:
                print(f"Executing: {statement[:100]}...")
                conn.execute(text(statement))
                conn.commit()
            except Exception as e:
                print(f"Error executing statement: {e}")
                conn.rollback()

def check_table_exists(table_name):
    """Check if a table exists in the database."""
    with engine.connect() as conn:
        try:
            result = conn.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                );
                """),
                {'table_name': table_name}
            )
            return result.scalar()
        except Exception as e:
            print(f"Error checking if table {table_name} exists: {e}")
            return False

def create_team_table():
    """Create the team table if it doesn't exist."""
    if not check_table_exists('team'):
        print("Creating team table...")
        with engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE team (
                id SERIAL PRIMARY KEY,
                abbreviation VARCHAR(3) UNIQUE NOT NULL,
                full_name VARCHAR(50) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Add common NFL teams if they don't exist
            INSERT INTO team (abbreviation, full_name) VALUES 
            ('ARI', 'Arizona Cardinals'),
            ('ATL', 'Atlanta Falcons'),
            ('BAL', 'Baltimore Ravens'),
            ('BUF', 'Buffalo Bills'),
            ('CAR', 'Carolina Panthers'),
            ('CHI', 'Chicago Bears'),
            ('CIN', 'Cincinnati Bengals'),
            ('CLE', 'Cleveland Browns'),
            ('DAL', 'Dallas Cowboys'),
            ('DEN', 'Denver Broncos'),
            ('DET', 'Detroit Lions'),
            ('GB', 'Green Bay Packers'),
            ('HOU', 'Houston Texans'),
            ('IND', 'Indianapolis Colts'),
            ('JAX', 'Jacksonville Jaguars'),
            ('KC', 'Kansas City Chiefs'),
            ('LV', 'Las Vegas Raiders'),
            ('LAC', 'Los Angeles Chargers'),
            ('LAR', 'Los Angeles Rams'),
            ('MIA', 'Miami Dolphins'),
            ('MIN', 'Minnesota Vikings'),
            ('NE', 'New England Patriots'),
            ('NO', 'New Orleans Saints'),
            ('NYG', 'New York Giants'),
            ('NYJ', 'New York Jets'),
            ('PHI', 'Philadelphia Eagles'),
            ('PIT', 'Pittsburgh Steelers'),
            ('SF', 'San Francisco 49ers'),
            ('SEA', 'Seattle Seahawks'),
            ('TB', 'Tampa Bay Buccaneers'),
            ('TEN', 'Tennessee Titans'),
            ('WAS', 'Washington Commanders')
            ON CONFLICT (abbreviation) DO NOTHING;
            """))
            conn.commit()
        print("Team table created successfully.")
    else:
        print("Team table already exists.")

def main():
    """Main function to update the database schema."""
    print("Starting database schema update...")
    
    # Create team table if it doesn't exist
    create_team_table()
    
    # Run the SQL file to update the player table
    sql_file = os.path.join(os.path.dirname(__file__), 'update_player_schema.sql')
    print(f"Running SQL file: {sql_file}")
    run_sql_file(sql_file)
    
    print("Database schema update completed successfully!")

if __name__ == "__main__":
    main()
