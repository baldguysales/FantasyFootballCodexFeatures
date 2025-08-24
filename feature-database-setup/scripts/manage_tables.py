"""Script to manage database tables."""
import os
from sqlmodel import create_engine, text
from dotenv import load_dotenv

def get_engine():
    """Create and return a database engine."""
    load_dotenv()
    db_url = os.getenv('DATABASE_URL', '').replace('+asyncpg', '')
    return create_engine(db_url)

def drop_team_table():
    """Drop the team table from the database."""
    engine = get_engine()
    with engine.connect() as conn:
        # Check if team table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'team'
            )
        """)).scalar()
        
        if result:
            # Drop foreign key constraints first
            conn.execute(text("""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.table_constraints 
                        WHERE constraint_name = 'player_team_id_fkey'
                    ) THEN
                        ALTER TABLE player DROP CONSTRAINT IF EXISTS player_team_id_fkey;
                    END IF;
                END $$;
            """))
            
            # Drop the team table
            conn.execute(text("DROP TABLE IF EXISTS team CASCADE"))
            conn.commit()
            print("✅ Team table dropped successfully")
        else:
            print("ℹ️  Team table does not exist")

def show_database_schema():
    """Display all tables and their columns in the database."""
    engine = get_engine()
    with engine.connect() as conn:
        # Get all tables
        tables = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)).fetchall()
        
        print("\n=== DATABASE SCHEMA ===\n")
        
        for table in tables:
            table_name = table[0]
            print(f"📋 TABLE: {table_name}")
            
            # Get columns for this table
            columns = conn.execute(text(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)).fetchall()
            
            # Get primary key columns
            pk_columns = conn.execute(text(f"""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = '{table_name}'::regclass
                AND i.indisprimary;
            """)).fetchall()
            pk_columns = [col[0] for col in pk_columns]
            
            # Get foreign key constraints
            fk_constraints = conn.execute(text(f"""
                SELECT
                    kcu.column_name, 
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
                    AND tc.table_name = '{table_name}'
            """)).fetchall()
            
            # Print columns
            print("\n  COLUMNS:")
            for col in columns:
                col_name, data_type, is_nullable, col_default = col
                col_info = f"    • {col_name} ({data_type})"
                
                # Add PK/FK indicators
                if col_name in pk_columns:
                    col_info += " 🔑"
                
                # Add NULL/NOT NULL
                col_info += " NULL" if is_nullable == 'YES' else " NOT NULL"
                
                # Add default if exists
                if col_default:
                    col_info += f" DEFAULT {col_default}"
                
                print(col_info)
            
            # Print foreign key constraints
            if fk_constraints:
                print("\n  FOREIGN KEYS:")
                for fk in fk_constraints:
                    col, fk_table, fk_col = fk
                    print(f"    • {col} → {fk_table}.{fk_col}")
            
            print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage database tables')
    parser.add_argument('--drop-team', action='store_true', help='Drop the team table')
    parser.add_argument('--show-schema', action='store_true', help='Show database schema')
    
    args = parser.parse_args()
    
    if args.drop_team:
        drop_team_table()
    
    if args.show_schema or not (args.drop_team or args.show_schema):
        show_database_schema()
