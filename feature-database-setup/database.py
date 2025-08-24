from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ff_codex_gdm_v1.db")

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Set to False in production
        connect_args={"check_same_thread": False}  # SQLite specific
    )
else:
    # PostgreSQL configuration (no SQLite-specific args)
    engine = create_engine(
        DATABASE_URL,
        echo=True  # Set to False in production
    )

# Import all models at module level (not inside function)
from .user import *
from .nfl import *
from .fantasy import *
from .stats import *
from .intelligence import *
from .betting import *
from .ml import *

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")

def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session
