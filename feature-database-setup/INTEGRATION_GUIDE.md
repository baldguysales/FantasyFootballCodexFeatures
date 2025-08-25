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

### Importing Models (UPDATED)
```python
from models.teams_players import Team, Player
from models.roster import PlayerWeekRoster  # NEW MODEL
from models.social_media_injury import SocialMediaInjury, SocialMediaInjuryMatch
```

### Example Queries

#### Get All Teams
```python
async with get_db() as session:
    result = await session.execute(select(Team))
    teams = result.scalars().all()
```

#### Get Players by Team (UPDATED - Uses new relationships)
```python
async with get_db() as session:
    # Option 1: Query core player data
    result = await session.execute(
        select(Player).where(Player.latest_team == "NE")
    )
    patriots_players = result.scalars().all()
    
    # Option 2: Query current roster (specific week/season)
    result = await session.execute(
        select(PlayerWeekRoster)
        .where(PlayerWeekRoster.team == "NE")
        .where(PlayerWeekRoster.season == 2024)
        .where(PlayerWeekRoster.week == 16)
    )
    current_roster = result.scalars().all()
```
#### Get Player with Roster History (NEW EXAMPLE)
```python
async with get_db() as session:
    result = await session.execute(
        select(Player)
        .options(selectinload(Player.roster_entries))
        .where(Player.gsis_id == "00-0036355")
    )
    player_with_history = result.scalar_one()
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

### Creating Records (UPDATED)
```python
async def create_player(player_data: dict):
    async with get_db() as session:
        player = Player(**player_data)
        session.add(player)
        await session.commit()
        await session.refresh(player)
        return player

async def create_roster_entry(roster_data: dict):
    async with get_db() as session:
        roster_entry = PlayerWeekRoster(**roster_data)
        session.add(roster_entry)
        await session.commit()
        await session.refresh(roster_entry)
        return roster_entry
```

### Updating Records (CRITICAL - Primary Key Changed)
```python
async def update_player(gsis_id: str, update_data: dict):  # Changed from player_id
    async with get_db() as session:
        result = await session.execute(
            select(Player).where(Player.gsis_id == gsis_id)  # Updated field
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
