"""Script to check the database schema."""
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, text

def main():
    # Load environment variables
    load_dotenv()
    
    # Create database engine
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Check team table columns
        print("=== Team Table Columns ===")
        result = conn.execute(text("""
            SELECT column_name, data_type, udt_name, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'team'
        """))
        for row in result:
            print(f"{row[0]}: {row[1]} ({row[2]}){' max_len=' + str(row[3]) if row[3] else ''}")
        
        # Check enums
        print("\n=== Enum Types ===")
        result = conn.execute(text("""
            SELECT t.typname, e.enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            ORDER BY t.typname, e.enumsortorder
        """))
        current_type = None
        for row in result:
            if current_type != row[0]:
                current_type = row[0]
                print(f"\n{current_type}:")
            print(f"  - {row[1]}")
        
        # Check constraints
        print("\n=== Table Constraints ===")
        result = conn.execute(text("""
            SELECT conname, conrelid::regclass, pg_get_constraintdef(oid)
            FROM pg_constraint 
            WHERE conrelid = 'team'::regclass
        """))
        for row in result:
            print(f"{row[0]}: {row[2]}")

if __name__ == "__main__":
    main()
