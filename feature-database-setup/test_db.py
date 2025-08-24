"""Test database connection and basic operations."""
import os
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env file")
    exit(1)

# Create engine with psycopg2
engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))

def test_connection():
    """Test database connection."""
    try:
        # Test direct connection with psycopg2
        db_url = DATABASE_URL.replace('+asyncpg', '')
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            if result and result[0] == 1:
                print("✅ Database connection successful!")
                return True
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Testing database connection...")
    if test_connection():
        print("\nDatabase connection test completed successfully!")
    else:
        print("\nDatabase connection test failed.")
