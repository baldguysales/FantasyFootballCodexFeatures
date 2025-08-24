"""Script to check the contents of the database."""
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, select, func
from sqlalchemy.sql import text

def main():
    # Load environment variables
    load_dotenv()
    
    # Create database engine
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    engine = create_engine(db_url)
    
    with Session(engine) as session:
        # Get player count
        player_count = session.scalar(select(func.count('*')).select_from(text('player')))
        
        # Get team count
        team_count = session.scalar(select(func.count('*')).select_from(text('team')))
        
        # Get sample of players
        sample_players = session.execute(
            text('''
                SELECT player_name, position, team_abbr, jersey_number 
                FROM player 
                ORDER BY RANDOM() 
                LIMIT 5
            ''')
        ).fetchall()
        
        # Get team distribution
        team_dist = session.execute(
            text('''
                SELECT team_abbr, COUNT(*) as player_count 
                FROM player 
                WHERE team_abbr IS NOT NULL AND team_abbr != 'UNK'
                GROUP BY team_abbr 
                ORDER BY player_count DESC
            ''')
        ).fetchall()
        
        print(f"\n=== Database Summary ===")
        print(f"Total players: {player_count}")
        print(f"Total teams: {team_count}")
        
        print("\n=== Sample Players ===")
        for player in sample_players:
            print(f"{player[0]} - {player[1]} - {player[2]} #{player[3] if player[3] else 'N/A'}")
        
        print("\n=== Players per Team ===")
        for team in team_dist:
            print(f"{team[0]}: {team[1]} players")

if __name__ == "__main__":
    main()
