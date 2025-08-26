# NFL Fantasy Football Database

This repository contains the database models and ETL pipelines for the NFL Fantasy Football application. It's built using SQLAlchemy with async support and follows a modular, type-hinted architecture with comprehensive betting data integration.

## Features

- **Player Management**: Core player identification with gsis_id as primary key
- **Roster Tracking**: Separate weekly roster data with PlayerWeekRoster model
- **Team Management**: Complete team information including logos, colors, and conference/division data
- **Injury Tracking**: Integration with social media for real-time injury reports
- **Historical Analysis**: Complete game schedule and results for matchup analysis (NEW)
- **Betting System**: Comprehensive NFL betting odds integration with The Odds API
- **Line Shopping**: Find best odds across 12+ major sportsbooks
- **Player Props**: Complete player proposition bet tracking and analysis
- **Historical Analysis**: Odds movement tracking and consensus calculations
- **Data Validation**: Robust data validation using Pydantic models
- **Async Support**: Built with async SQLAlchemy for high-performance database operations

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL 13+
- Poetry (for dependency management)
- The Odds API key (for betting data)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Set up your environment variables (copy `.env.example` to `.env` and update values):
   ```bash
   # Database
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ff_codex
   
   # Betting System (NEW)
   ODDS_API_KEY=your_odds_api_key_here
   ODDS_API_BASE_URL=https://api.the-odds-api.com/v4
   ```
4. Run the database migrations:
   ```bash
   alembic upgrade head
   ```

## Project Structure

```
feature-database-setup/
├── models/                     # Database models
│   ├── __init__.py            # Package initialization
│   ├── base.py                # Base model classes and mixins
│   ├── teams_players.py       # Team and core Player models
│   ├── roster.py              # Weekly roster tracking (PlayerWeekRoster)
│   ├── social_media_injury.py # Injury tracking from social media (FK updated to gsis_id)
│   ├── betting.py             # Comprehensive betting system (NEW)
│   │                          # - NFL games, bookmakers, odds, player props
│   │                          # - Historical tracking and consensus analysis
│   ├── fantasy.py             # Fantasy football specific models
│   ├── intelligence.py        # AI/ML features and intelligence (FK updated)
│   ├── ml.py                  # Machine learning models (FK updated)
│   ├── stats.py               # Player statistics and historical game data (UPDATED)
│   │                          # - Weekly player statistics and fantasy points
│   │                          # - Historical schedule and game results (NEW)
│   │                          # - Matchup analysis and performance tracking
│   └── user.py                # User accounts and authentication
├── scripts/                   # Database scripts and ETL
│   ├── recreate_*.py          # Table recreation scripts
│   └── utilities/             # Helper scripts
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── alembic/                   # Database migrations
│   ├── versions/              # Migration scripts
│   ├── env.py                # Migration environment
│   └── script.py.mako        # Migration template
└── docs/                      # Documentation
    ├── SCHEMA.md             # Database schema documentation
    └── examples/             # Code examples
```

## Betting System Architecture

### Core Tables
- **nfl_game**: Complete game information with Odds API integration
- **bookmaker**: Sportsbook information (FanDuel, DraftKings, etc.)
- **gameodds**: Market-level odds (moneyline, spreads, totals)
- **bettingoutcome**: Individual betting lines within each market
- **playerproptype**: Player proposition bet categories
- **playerprop**: Player proposition bets with over/under lines

### Analytics Tables
- **oddssnapshot**: Historical odds snapshots for trend analysis
- **oddsmovement**: Line movement tracking over time
- **consensusodds**: Best odds calculations across bookmakers

### Supported Markets
- **Main Markets**: Moneyline (h2h), Point Spreads, Over/Under Totals
- **Player Props**: Passing yards/TDs, rushing yards, receiving yards/TDs, and more
- **Period Markets**: Quarter and half-time betting lines
- **Alternative Markets**: Alternate spreads and totals

### Database Views
Ready-to-use views for common queries:
- `current_betting_odds` - Latest odds with JSON outcomes
- `current_player_props` - Player props with player information
- `recent_odds_movements` - Line movements for alerts
- `best_odds_available` - Consensus best odds by market
- `weekly_betting_summary` - Reporting analytics

## Quick Start Examples

### Basic Player Query
```python
from models.teams_players import Player
from models.betting import PlayerProp

# Get player with betting props
async with get_db() as session:
    result = await session.execute(
        select(Player).where(Player.gsis_id == "00-0036355")
    )
    josh_allen = result.scalar_one()
    
    # Get his current props
    props_result = await session.execute(
        select(PlayerProp)
        .where(PlayerProp.player_id == josh_allen.gsis_id)
        .where(PlayerProp.bookmaker_last_update >= datetime.utcnow() - timedelta(hours=24))
    )
    current_props = props_result.scalars().all()
```

### Betting Odds Query
```python
from models.betting import NFLGame, GameOdds

# Get current moneyline odds for a game
async with get_db() as session:
    result = await session.execute(
        text("SELECT * FROM current_betting_odds WHERE market_type = 'h2h' AND game_id = 1")
    )
    moneyline_odds = result.fetchall()
```

### Historical Performance Analysis
```python
from models.stats import Schedule, get_team_performance_vs_opponent

# Analyze team performance against specific opponents
async with get_db() as session:
    performance = get_team_performance_vs_opponent(session, "NE", "BUF", seasons=3)
    print(f"Patriots vs Bills: {performance['wins']}-{performance['losses']} record")
    print(f"Average points: {performance['avg_points_for']:.1f} for, {performance['avg_points_against']:.1f} against")
```

## API Integration

### The Odds API
The betting system integrates with [The Odds API](https://the-odds-api.com) to provide:
- Real-time odds from 12+ major US sportsbooks
- Player proposition bets
- Historical odds data
- Line movement tracking

### Supported Bookmakers
- FanDuel
- DraftKings
- BetMGM
- Caesars
- PointsBet (US)
- BetRivers
- Unibet
- Barstool Sportsbook
- Bovada
- BetOnline.ag
- William Hill (US)
- SugarHouse

## Database Functions

The betting system includes utility functions:
- `cleanup_old_odds_data(days_to_keep)` - Clean up historical data
- `calculate_odds_movement(...)` - Track line movements
- `get_latest_odds(odds_api_id, market_type)` - Get latest odds for a game
- `calculate_consensus_odds(game_id, market_type)` - Calculate consensus across books

## Documentation

- [Integration Guide](./INTEGRATION_GUIDE.md) - How to integrate with this service
- [Development Notes](./DEVELOPMENT_NOTES.md) - Internal development documentation
- [Database Schema](./docs/SCHEMA.md) - Detailed database schema documentation

## Key Architecture Changes

### Database Schema Updates
- **Player Primary Key**: Changed from `player_id` to `gsis_id`
- **Roster Separation**: Weekly roster data moved to `PlayerWeekRoster` table
- **Betting Integration**: Complete betting system with game management
- **Foreign Key Updates**: All player references updated to use `gsis_id`

### Breaking Changes
- All foreign key references to Player must use `gsis_id` instead of `player_id`
- Player model no longer contains weekly roster data
- New PlayerWeekRoster model handles all season/week-specific data
- Betting system provides its own game management (no dependency on external game table)

## Performance Considerations

### Indexing
- Comprehensive indexing for betting queries
- Player and roster lookup optimization
- Foreign key relationship indexes

### Caching Strategy
- Betting odds caching with TTL
- Consensus calculations caching
- Database view performance optimization

### Data Management
- Automatic cleanup of historical betting data
- Efficient bulk operations for odds updates
- Rate limiting compliance with The Odds API

## Testing

The project includes comprehensive testing:

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/unit/test_betting.py
pytest tests/integration/test_betting_integration.py

# Test with coverage
pytest --cov=models tests/
```

### Test Data
Sample test data is provided for:
- Player records with roster history
- Complete betting scenarios
- Historical odds data
- Line movement tracking

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for your changes
4. Ensure all tests pass
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

### Betting System Contributions
When contributing to the betting system:
- Ensure compliance with The Odds API terms of service
- Test with multiple bookmakers and market types
- Validate odds calculations and conversions
- Update relevant database views and functions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [The Odds API](https://the-odds-api.com) for comprehensive betting data
- NFL Data community for player and game information
- SQLAlchemy team for excellent async ORM support