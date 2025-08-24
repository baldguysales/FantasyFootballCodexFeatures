import contextlib
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker
)
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import NullPool

# Add the main project to the Python path
main_project_path = str(Path.home() / "Documents" / "ff-codex-gdm-v1" / "backend")
if main_project_path not in sys.path:
    sys.path.append(main_project_path)

from app.core.config import settings

# Create database engines
async_engine = create_async_engine(
    str(settings.DATABASE_URI).replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=settings.DB_POOL_SIZE if hasattr(settings, "DB_POOL_SIZE") else 5,
    max_overflow=settings.DB_MAX_OVERFLOW if hasattr(settings, "DB_MAX_OVERFLOW") else 10,
    pool_timeout=30,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create sync engine for migrations and testing
sync_engine = create_engine(
    str(settings.DATABASE_URI).replace("postgresql+asyncpg://", "postgresql://"),
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create sync session factory
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """
    Get a synchronous database session.
    
    This is primarily used for migrations and testing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an asynchronous database session.
    
    This is the main dependency for FastAPI route handlers.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# For use with FastAPI's Depends
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get an async database session.
    
    Example:
        @app.get("/items/{item_id}")
        async def read_item(
            item_id: int, 
            db: AsyncSession = Depends(get_db_session)
        ):
            result = await db.execute(select(Item).filter(Item.id == item_id))
            return result.scalars().first()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# For use with FastAPI's lifespan
def create_db_and_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=sync_engine)

# For use with FastAPI's startup event
async def init_db():
    """Initialize database."""
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

# For use with FastAPI's shutdown event
async def close_db_connection():
    """Close database connection."""
    await async_engine.dispose()

# Add event listeners for connection management
@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraint for SQLite."""
    if "sqlite" in str(dbapi_connection.engine.url):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# For use in FastAPI's lifespan
@contextlib.asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for FastAPI app."""
    # Startup: Initialize database
    await init_db()
    
    yield
    
    # Shutdown: Close database connection
    await close_db_connection()
