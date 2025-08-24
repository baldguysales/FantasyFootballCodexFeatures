"""Script to insert NFL team data into the database."""
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, text

# NFL team data with abbreviations and full names
NFL_TEAMS = [
    {"abbreviation": "ARI", "full_name": "Arizona Cardinals", "conference": "NFC", "division": "West"},
    {"abbreviation": "ATL", "full_name": "Atlanta Falcons", "conference": "NFC", "division": "South"},
    {"abbreviation": "BAL", "full_name": "Baltimore Ravens", "conference": "AFC", "division": "North"},
    {"abbreviation": "BUF", "full_name": "Buffalo Bills", "conference": "AFC", "division": "East"},
    {"abbreviation": "CAR", "full_name": "Carolina Panthers", "conference": "NFC", "division": "South"},
    {"abbreviation": "CHI", "full_name": "Chicago Bears", "conference": "NFC", "division": "North"},
    {"abbreviation": "CIN", "full_name": "Cincinnati Bengals", "conference": "AFC", "division": "North"},
    {"abbreviation": "CLE", "full_name": "Cleveland Browns", "conference": "AFC", "division": "North"},
    {"abbreviation": "DAL", "full_name": "Dallas Cowboys", "conference": "NFC", "division": "East"},
    {"abbreviation": "DEN", "full_name": "Denver Broncos", "conference": "AFC", "division": "West"},
    {"abbreviation": "DET", "full_name": "Detroit Lions", "conference": "NFC", "division": "North"},
    {"abbreviation": "GB", "full_name": "Green Bay Packers", "conference": "NFC", "division": "North"},
    {"abbreviation": "HOU", "full_name": "Houston Texans", "conference": "AFC", "division": "South"},
    {"abbreviation": "IND", "full_name": "Indianapolis Colts", "conference": "AFC", "division": "South"},
    {"abbreviation": "JAX", "full_name": "Jacksonville Jaguars", "conference": "AFC", "division": "South"},
    {"abbreviation": "KC", "full_name": "Kansas City Chiefs", "conference": "AFC", "division": "West"},
    {"abbreviation": "LV", "full_name": "Las Vegas Raiders", "conference": "AFC", "division": "West"},
    {"abbreviation": "LAC", "full_name": "Los Angeles Chargers", "conference": "AFC", "division": "West"},
    {"abbreviation": "LA", "full_name": "Los Angeles Rams", "conference": "NFC", "division": "West"},
    {"abbreviation": "MIA", "full_name": "Miami Dolphins", "conference": "AFC", "division": "East"},
    {"abbreviation": "MIN", "full_name": "Minnesota Vikings", "conference": "NFC", "division": "North"},
    {"abbreviation": "NE", "full_name": "New England Patriots", "conference": "AFC", "division": "East"},
    {"abbreviation": "NO", "full_name": "New Orleans Saints", "conference": "NFC", "division": "South"},
    {"abbreviation": "NYG", "full_name": "New York Giants", "conference": "NFC", "division": "East"},
    {"abbreviation": "NYJ", "full_name": "New York Jets", "conference": "AFC", "division": "East"},
    {"abbreviation": "PHI", "full_name": "Philadelphia Eagles", "conference": "NFC", "division": "East"},
    {"abbreviation": "PIT", "full_name": "Pittsburgh Steelers", "conference": "AFC", "division": "North"},
    {"abbreviation": "SF", "full_name": "San Francisco 49ers", "conference": "NFC", "division": "West"},
    {"abbreviation": "SEA", "full_name": "Seattle Seahawks", "conference": "NFC", "division": "West"},
    {"abbreviation": "TB", "full_name": "Tampa Bay Buccaneers", "conference": "NFC", "division": "South"},
    {"abbreviation": "TEN", "full_name": "Tennessee Titans", "conference": "AFC", "division": "South"},
    {"abbreviation": "WAS", "full_name": "Washington Commanders", "conference": "NFC", "division": "East"}
]

def main():
    # Load environment variables
    load_dotenv()
    
    # Create database engine
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    engine = create_engine(db_url)
    
    with Session(engine) as session:
        # Check if teams table exists
        result = session.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'team'
                )
            """)
        ).scalar()
        
        if not result:
            print("Error: 'team' table does not exist in the database.")
            print("Please make sure you've run the database migrations first.")
            return
        
        # Insert teams
        for team in NFL_TEAMS:
            # Check if team already exists
            exists = session.execute(
                text("SELECT 1 FROM team WHERE abbreviation = :abbr"),
                {"abbr": team["abbreviation"]}
            ).scalar()
            
            if not exists:
                session.execute(
                    text("""
                        INSERT INTO team (abbreviation, full_name, conference, division)
                        VALUES (:abbreviation, :full_name, :conference, :division)
                    """),
                    team
                )
                print(f"Added team: {team['full_name']} ({team['abbreviation']})")
            else:
                print(f"Team already exists: {team['full_name']} ({team['abbreviation']})")
        
        session.commit()
        print("\nTeam data insertion completed successfully!")

if __name__ == "__main__":
    main()
