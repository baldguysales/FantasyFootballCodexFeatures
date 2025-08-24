# Integration Guide

This guide provides information on how to integrate with the NFL Fantasy Football database service.

## Table of Contents

- [Database Connection](#database-connection)
- [Model Usage](#model-usage)
- [Common Operations](#common-operations)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Database Connection

### Connection String

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/fantasy_football"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### Getting a Session

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
```

## Model Usage

### Importing Models

```python
from models.teams_players import Team, Player
from models.social_media_injury import SocialMediaInjury, SocialMediaInjuryMatch
```

### Example Queries

#### Get All Teams
```python
async with get_db() as session:
    result = await session.execute(select(Team))
    teams = result.scalars().all()
```

#### Get Players by Team
```python
async with get_db() as session:
    result = await session.execute(
        select(Player).where(Player.team == "NE")
    )
    patriots_players = result.scalars().all()
```

#### Get Recent Injuries
```python
from datetime import datetime, timedelta

async with get_db() as session:
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    result = await session.execute(
        select(SocialMediaInjury)
        .where(SocialMediaInjury.created_at >= one_week_ago)
        .order_by(SocialMediaInjury.created_at.desc())
    )
    recent_injuries = result.scalars().all()
```

## Common Operations

### Creating Records

```python
async def create_player(player_data: dict):
    async with get_db() as session:
        player = Player(**player_data)
        session.add(player)
        await session.commit()
        await session.refresh(player)
        return player
```

### Updating Records

```python
async def update_player(player_id: str, update_data: dict):
    async with get_db() as session:
        result = await session.execute(
            select(Player).where(Player.player_id == player_id)
        )
        player = result.scalar_one_or_none()
        if player:
            for key, value in update_data.items():
                setattr(player, key, value)
            await session.commit()
            await session.refresh(player)
        return player
```

## Error Handling

### Handling Database Errors

```python
from sqlalchemy.exc import SQLAlchemyError

try:
    # Database operations
    pass
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error occurred")
```

## Best Practices

1. **Use Async Everywhere**: Always use async/await when working with the database
2. **Session Management**: Always use context managers or try/finally blocks to ensure sessions are properly closed
3. **Batch Operations**: For bulk inserts/updates, use appropriate batching techniques
4. **Indexing**: Be mindful of query patterns and ensure proper indexes are in place
5. **Connection Pooling**: Configure connection pooling based on your application's needs
6. **Logging**: Implement comprehensive logging for database operations
7. **Migrations**: Always use Alembic for database schema migrations

## Testing

When writing tests:

1. Use a separate test database
2. Set up and tear down test data for each test case
3. Use transactions to ensure test isolation
4. Mock external services when testing database operations

Example test setup:

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_fantasy_football"

test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```
