# Integration Guide

This guide provides information on how to integrate with the NFL Fantasy Football database service, including the new comprehensive betting system.

## Table of Contents

- [Database Connection](#database-connection)
- [Model Usage](#model-usage)
- [Betting System Integration](#betting-system-integration)
- [Common Operations](#common-operations)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Database Connection

### Connection String

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/ff_codex"

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
from models.roster import PlayerWeekRoster
from models.social_media_injury import SocialMediaInjury, SocialMediaInjuryMatch
from models.stats import PlayerWeekStats, PlayerWeekPoints, Schedule  # Added Schedule
from models.betting import (
    Bookmaker, NFLGame, GameOdds, BettingOutcome,
    PlayerPropType, PlayerProp, OddsSnapshot, 
    OddsMovement, ConsensusOdds
)
```

### Example Queries

#### Get All Teams
```python
async with get_db() as session:
    result = await session.execute(select(Team))
    teams = result.scalars().all()
```

#### Get Players by Team (Updated - Uses new relationships)
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

#### Get Player with Roster History
```python
async with get_db() as session:
    result = await session.execute(
        select(Player)
        .options(selectinload(Player.roster_entries))
        .where(Player.gsis_id == "00-0036355")
    )
    player_with_history = result.scalar_one()
```

### Historical Performance Analysis

#### Get Player Performance Against Specific Teams
```python
from models.stats import Schedule, get_team_performance_vs_opponent

async with get_db() as session:
    # Analyze how Patriots perform against Bills in last 3 seasons
    performance = get_team_performance_vs_opponent(session, "NE", "BUF", seasons=3)
    
    print(f"Record: {performance['wins']}-{performance['losses']}")
    print(f"Win percentage: {performance['win_percentage']:.2%}")
    print(f"Average points for: {performance['avg_points_for']:.1f}")
    print(f"Average points against: {performance['avg_points_against']:.1f}")
```

#### Get Head-to-Head Game History
```python
from models.stats import get_head_to_head_history

async with get_db() as session:
    # Get Chiefs vs Raiders history for last 5 seasons
    result = get_head_to_head_history(session, "KC", "LV", seasons=5)
    games = result.scalars().all()
    
    for game in games:
        kc_score = game.get_team_score("KC")
        lv_score = game.get_team_score("LV")
        winner = "KC" if game.did_team_win("KC") else "LV"
        print(f"Week {game.week} {game.season}: KC {kc_score} - LV {lv_score} (Winner: {winner})")
```

#### Analyze Rest Days Impact
```python
async with get_db() as session:
    # Find teams playing on short rest
    result = await session.execute(
        select(Schedule)
        .where(Schedule.season == 2024)
        .where(or_(Schedule.home_rest <= 4, Schedule.away_rest <= 4))
        .order_by(Schedule.week)
    )
    short_rest_games = result.scalars().all()
    
    # Analyze performance difference
    for game in short_rest_games:
        if game.home_rest <= 4:
            print(f"{game.home_team} playing at home with {game.home_rest} days rest")
        if game.away_rest <= 4:
            print(f"{game.away_team} playing away with {game.away_rest} days rest")

## Betting System Integration

### Get Current Odds for a Game
```python
async with get_db() as session:
    # Get all current odds for a specific game
    result = await session.execute(
        select(GameOdds)
        .options(
            selectinload(GameOdds.bookmaker),
            selectinload(GameOdds.outcomes),
            selectinload(GameOdds.nfl_game)
        )
        .join(NFLGame)
        .where(NFLGame.odds_api_id == "game_id_from_odds_api")
        .where(GameOdds.market_type == "h2h")  # Moneyline
    )
    current_odds = result.scalars().all()
```

### Get Player Props for a Player
```python
async with get_db() as session:
    # Get all current player props for a specific player
    result = await session.execute(
        select(PlayerProp)
        .options(
            selectinload(PlayerProp.prop_type),
            selectinload(PlayerProp.nfl_game)
        )
        .where(PlayerProp.player_id == "00-0036355")  # Josh Allen's gsis_id
        .where(PlayerProp.bookmaker_last_update >= datetime.utcnow() - timedelta(hours=24))
    )
    player_props = result.scalars().all()
```

### Get Best Odds Across Bookmakers
```python
async with get_db() as session:
    # Use the consensus odds view
    result = await session.execute(
        text("""
        SELECT * FROM best_odds_available 
        WHERE game_id = :game_id 
          AND market_type = :market_type 
          AND outcome_name = :team_name
        """),
        {
            "game_id": 1,
            "market_type": "h2h",
            "team_name": "Kansas City Chiefs"
        }
    )
    best_odds = result.fetchone()
```

### Track Line Movements
```python
async with get_db() as session:
    # Get recent line movements for spreads
    result = await session.execute(
        select(OddsMovement)
        .where(OddsMovement.market_type == "spreads")
        .where(OddsMovement.movement_timestamp >= datetime.utcnow() - timedelta(hours=24))
        .where(OddsMovement.point_movement != None)
        .order_by(OddsMovement.movement_timestamp.desc())
    )
    line_movements = result.scalars().all()
```

### Using Database Views
```python
# The betting system includes several helpful views
async with get_db() as session:
    # Get current betting odds with outcomes as JSON
    result = await session.execute(
        text("SELECT * FROM current_betting_odds WHERE game_id = :game_id"),
        {"game_id": 1}
    )
    current_odds = result.fetchall()
    
    # Get current player props with player information
    result = await session.execute(
        text("SELECT * FROM current_player_props WHERE player_name LIKE :name"),
        {"name": "%Josh Allen%"}
    )
    josh_allen_props = result.fetchall()
    
    # Get recent odds movements
    result = await session.execute(
        text("SELECT * FROM recent_odds_movements WHERE market_type = 'spreads'")
    )
    recent_movements = result.fetchall()
```

## Common Operations

### Creating Records (Updated)
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

async def create_game_odds(odds_data: dict):
    async with get_db() as session:
        game_odds = GameOdds(**odds_data)
        session.add(game_odds)
        await session.commit()
        await session.refresh(game_odds)
        return game_odds
```

### Updating Records (Primary Key Changed)
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

async def update_odds(odds_id: int, update_data: dict):
    async with get_db() as session:
        result = await session.execute(
            select(GameOdds).where(GameOdds.id == odds_id)
        )
        odds = result.scalar_one_or_none()
        if odds:
            for key, value in update_data.items():
                setattr(odds, key, value)
            await session.commit()
            await session.refresh(odds)
        return odds
```

### Batch Operations for Betting Data
```python
async def bulk_create_odds(odds_list: List[dict]):
    """Efficiently create multiple odds records"""
    async with get_db() as session:
        odds_objects = [GameOdds(**odds_data) for odds_data in odds_list]
        session.add_all(odds_objects)
        await session.commit()
        return odds_objects

async def bulk_create_outcomes(outcomes_list: List[dict]):
    """Efficiently create multiple betting outcomes"""
    async with get_db() as session:
        outcome_objects = [BettingOutcome(**outcome_data) for outcome_data in outcomes_list]
        session.add_all(outcome_objects)
        await session.commit()
        return outcome_objects
```

## Error Handling

### Handling Database Errors
```python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

try:
    # Database operations
    pass
except IntegrityError as e:
    logger.error(f"Integrity constraint violation: {e}")
    # Handle duplicate entries, foreign key violations, etc.
    raise HTTPException(status_code=400, detail="Data integrity error")
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error occurred")
```

### Betting System Specific Error Handling
```python
async def safe_create_game_odds(odds_data: dict):
    """Safely create game odds with proper error handling"""
    try:
        async with get_db() as session:
            # Check if odds already exist
            existing = await session.execute(
                select(GameOdds).where(
                    GameOdds.nfl_game_id == odds_data["nfl_game_id"],
                    GameOdds.bookmaker_id == odds_data["bookmaker_id"],
                    GameOdds.market_type == odds_data["market_type"]
                )
            )
            if existing.scalar_one_or_none():
                logger.info("Odds already exist, updating instead")
                return await update_existing_odds(odds_data)
            
            # Create new odds
            game_odds = GameOdds(**odds_data)
            session.add(game_odds)
            await session.commit()
            return game_odds
            
    except IntegrityError as e:
        if "uq_game_book_market" in str(e):
            logger.warning("Duplicate odds constraint violation")
            return await update_existing_odds(odds_data)
        raise
```

## Best Practices

1. **Use Async Everywhere**: Always use async/await when working with the database
2. **Session Management**: Always use context managers or try/finally blocks to ensure sessions are properly closed
3. **Batch Operations**: For bulk inserts/updates, use appropriate batching techniques
4. **Indexing**: Be mindful of query patterns and ensure proper indexes are in place
5. **Connection Pooling**: Configure connection pooling based on your application's needs
6. **Logging**: Implement comprehensive logging for database operations
7. **Migrations**: Always use Alembic for database schema migrations

### Betting System Best Practices

8. **Data Freshness**: Always check `bookmaker_last_update` timestamps for odds data
9. **Rate Limiting**: Respect The Odds API rate limits when fetching data
10. **Cleanup**: Regularly clean up old historical data to manage database size
11. **Consensus Calculations**: Use the provided database functions for consensus odds
12. **Error Handling**: Handle missing markets/bookmakers gracefully
13. **Caching**: Cache frequently accessed betting data with appropriate TTL

### Example Configuration
```python
# Betting system configuration
BETTING_CONFIG = {
    "odds_freshness_threshold": timedelta(hours=1),  # Consider odds stale after 1 hour
    "cleanup_days": 30,  # Keep historical data for 30 days
    "min_bookmaker_count": 3,  # Minimum bookmakers for consensus calculation
    "supported_markets": ["h2h", "spreads", "totals"],
    "cache_ttl": 300,  # Cache betting data for 5 minutes
}
```

## Testing

### Test Setup with Betting Data
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_ff_codex"

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

@pytest.fixture
async def sample_betting_data():
    """Create sample betting data for testing"""
    return {
        "bookmaker": {
            "key": "fanduel",
            "title": "FanDuel",
            "region": "us",
            "has_player_props": True
        },
        "nfl_game": {
            "odds_api_id": "test_game_123",
            "season": 2024,
            "week": 1,
            "home_team": "Kansas City Chiefs",
            "away_team": "Buffalo Bills",
            "commence_time": datetime.utcnow() + timedelta(days=1)
        },
        "game_odds": {
            "market_type": "h2h",
            "bookmaker_last_update": datetime.utcnow()
        }
    }
```

### Integration Testing
```python
async def test_betting_integration(test_db, sample_betting_data):
    """Test complete betting data integration"""
    # Create bookmaker
    bookmaker = Bookmaker(**sample_betting_data["bookmaker"])
    test_db.add(bookmaker)
    await test_db.commit()
    
    # Create game
    nfl_game = NFLGame(**sample_betting_data["nfl_game"])
    test_db.add(nfl_game)
    await test_db.commit()
    
    # Create odds
    odds_data = sample_betting_data["game_odds"]
    odds_data.update({
        "nfl_game_id": nfl_game.id,
        "bookmaker_id": bookmaker.id
    })
    game_odds = GameOdds(**odds_data)
    test_db.add(game_odds)
    await test_db.commit()
    
    # Test relationships
    assert game_odds.nfl_game == nfl_game
    assert game_odds.bookmaker == bookmaker
    assert nfl_game.game_odds[0] == game_odds
```