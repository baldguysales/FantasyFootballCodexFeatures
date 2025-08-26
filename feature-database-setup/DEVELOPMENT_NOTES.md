# Development Notes

This document contains internal development notes, architecture decisions, and implementation details for the NFL Fantasy Football database.

## Table of Contents

- [Database Schema](#database-schema)
- [Model Architecture](#model-architecture)
- [Betting System Architecture](#betting-system-architecture)
- [Async Implementation](#async-implementation)
- [Testing Strategy](#testing-strategy)
- [Performance Considerations](#performance-considerations)
- [Known Issues](#known-issues)
- [Future Improvements](#future-improvements)

## Database Schema

### Team Table
- Primary Key: `team_abbr` (VARCHAR(10))
- Unique Constraint: `team_id` (BIGINT)
- Indexes on: `team_conf`, `team_division`
- Contains team metadata, colors, and logo URLs

### Player Table
- Primary Key: `gsis_id` (VARCHAR(50)) - CHANGED from player_id
- Contains core player identification and attributes only
- Removed weekly roster data (now in separate table)
- Links to betting system via foreign key relationships

### PlayerWeekRoster Table
- Primary Key: `id` (INTEGER, auto-increment)
- Foreign Key: `player_id` references Player.gsis_id
- Contains weekly roster status, position, team assignments
- Unique constraint on (player_id, season, week)
- Indexes on: player_id, team, season, week combinations

### Social Media Injury Tables
- `social_media_injury`: Stores injury reports from social media
- `social_media_injury_matches`: Tracks manual matches between reports and players
- Foreign keys updated to reference Player.gsis_id

### Schedule Table (NEW)
- `schedule`: Historical game results and schedule information
- Primary Key: `game_id` (VARCHAR) - Unique game identifier
- Contains game results, betting lines, team matchups, and timing data
- Used for historical performance analysis against specific opponents
- Includes rest days, overtime indicators, and external service IDs

### Betting System Tables (NEW)
- `nfl_game`: Complete game information for betting purposes
- `bookmaker`: Sportsbook information (FanDuel, DraftKings, etc.)
- `gameodds`: Market-level odds (moneyline, spreads, totals)
- `bettingoutcome`: Individual betting lines within each market
- `playerproptype`: Defines player proposition bet types
- `playerprop`: Player proposition bets with over/under lines
- `oddssnapshot`: Historical odds snapshots for analysis
- `oddsmovement`: Line movement tracking over time
- `consensusodds`: Best odds calculations across bookmakers

## Model Architecture

### Base Models
- `BaseModel`: Common fields and methods for all models
- `Base`: SQLAlchemy declarative base

### Team and Player Models
- `TeamBase`: Base fields for teams (unchanged)
- `Team`: Table model with relationships (unchanged)
- `PlayerBase`: Base fields for core player data only (simplified)
- `Player`: Core player identification model with gsis_id primary key
- `PlayerWeekRosterBase`: Base fields for weekly roster data
- `PlayerWeekRoster`: Weekly roster tracking model

### Statistics and Analysis Models
- `PlayerWeekStatsBase/PlayerWeekStats`: Weekly player performance statistics
- `PlayerWeekPointsBase/PlayerWeekPoints`: Precomputed fantasy points
- `ScheduleBase/Schedule`: Historical game results and schedule data (NEW)
  - Used for analyzing player/team performance against specific opponents
  - Contains historical betting lines and game metadata
  - Enables matchup analysis and rest day considerations

### Betting Models (NEW)
- `BookmakerBase/Bookmaker`: Sportsbook information and capabilities
- `NFLGameBase/NFLGame`: Complete game data with Odds API integration
- `GameOddsBase/GameOdds`: Market-level odds storage
- `BettingOutcomeBase/BettingOutcome`: Individual betting lines
- `PlayerPropTypeBase/PlayerPropType`: Player prop categories
- `PlayerPropBase/PlayerProp`: Player proposition bets
- `OddsSnapshotBase/OddsSnapshot`: Historical odds data
- `OddsMovementBase/OddsMovement`: Line movement tracking
- `ConsensusOddsBase/ConsensusOdds`: Cross-bookmaker analysis

### Breaking Changes
- All foreign key references to Player must use gsis_id instead of player_id
- Player model no longer contains weekly roster data
- New PlayerWeekRoster model handles all season/week-specific data
- Comprehensive betting system with its own game management

### Social Media Models
- `SocialMediaInjury`: Stores injury reports (FK updated to gsis_id)
- `SocialMediaInjuryMatch`: Tracks report-player matches (FK updated to gsis_id)

## Betting System Architecture

### The Odds API Integration
- **Sport Key**: `americanfootball_nfl` for NFL data
- **Market Support**: h2h (moneyline), spreads, totals, player props
- **Bookmaker Coverage**: 12+ major US sportsbooks
- **Rate Limiting**: Built-in compliance with API rate limits
- **Historical Data**: Comprehensive odds snapshots and movement tracking

### Data Flow
1. **Collection**: ETL processes fetch odds from The Odds API
2. **Processing**: Market data parsed and validated
3. **Storage**: Odds stored with relationships to games/players/bookmakers
4. **Analysis**: Consensus calculations and movement detection
5. **API Access**: RESTful endpoints for application consumption

### Key Features
- **Line Shopping**: Find best odds across all bookmakers
- **Movement Tracking**: Automatic detection of line changes
- **Player Props**: Comprehensive player proposition bet support
- **Historical Analysis**: Complete odds history for trend analysis
- **Consensus Odds**: Calculate best available odds across markets

### Database Views
- `current_betting_odds`: Latest odds with JSON outcomes
- `current_player_props`: Player props with player information
- `recent_odds_movements`: Line movements for alerts
- `best_odds_available`: Consensus best odds by market
- `weekly_betting_summary`: Reporting analytics
- `bookmaker_coverage`: Coverage analysis
- `prop_popularity`: Player prop trends

## Async Implementation

### Database Session Management
- Uses SQLAlchemy 2.0 async API
- Session factory with proper cleanup
- Context managers for session handling

### Transaction Management
- Automatic transaction handling with context managers
- Proper error handling and rollback
- Nested transaction support

## Testing Strategy

### Unit Tests
- Test individual model methods
- Test validation logic
- Test helper functions
- Test betting odds calculations and conversions

### Integration Tests
- Test database operations
- Test model relationships
- Test transaction handling
- Test betting system API integration

### Fixtures
- Database setup/teardown
- Test data generation
- Mock services
- Sample betting data for testing

## Performance Considerations

### Indexing Strategy
- Indexes on frequently queried columns
- Composite indexes for common query patterns
- Partial indexes for filtered queries
- Betting-specific indexes for odds queries

### Query Optimization
- Eager loading for related data
- Select only required columns
- Batch operations for bulk data
- Optimized betting queries with proper joins

### Caching
- Consider adding Redis for caching
- Cache invalidation strategy
- Query result caching
- Betting odds caching with TTL

## Known Issues

1. **Circular Imports**
   - Currently managed with `TYPE_CHECKING`
   - Consider refactoring to avoid circular dependencies

2. **Async Session Management**
   - Need to ensure proper session cleanup
   - Potential for session leaks in error cases

3. **Betting Data Volume**
   - Large volume of odds updates during game days
   - Need efficient cleanup strategies for historical data
   - Monitor database size growth

## Future Improvements

### Schema Changes
1. Add more detailed player statistics
2. Implement historical data tracking
3. Add support for multiple seasons
4. Enhanced betting market support (futures, parlays)

### Performance
1. Implement connection pooling
2. Add query caching
3. Optimize bulk operations
4. Betting-specific performance optimizations

### Features
1. Add data validation middleware
2. Implement change tracking
3. Add audit logging
4. Real-time odds notifications
5. Advanced betting analytics

### Betting Enhancements
1. **Additional Markets**: Futures, parlays, live betting
2. **More Sportsbooks**: International bookmakers
3. **Advanced Analytics**: Sharp vs public money tracking
4. **Arbitrage Detection**: Cross-bookmaker arbitrage opportunities
5. **Machine Learning**: Predictive line movement models

## Development Workflow

### Code Style
- Follow PEP 8
- Use type hints
- Document public APIs
- Betting-specific documentation standards

### Version Control
- Feature branches
- Meaningful commit messages
- Pull request reviews
- Betting system integration testing

### Dependencies
- Manage with Poetry
- Pin all dependencies
- Regular updates
- The Odds API client management

## Troubleshooting

### Common Issues

#### Database Connection Issues
- Verify database is running
- Check connection string
- Verify user permissions

#### Session Management
- Ensure sessions are properly closed
- Watch for session leaks
- Handle transaction isolation levels

#### Performance Problems
- Check for N+1 queries
- Review query plans
- Monitor database metrics

#### Betting System Issues
- **API Rate Limits**: Monitor The Odds API usage
- **Data Freshness**: Ensure timely odds updates
- **Missing Markets**: Handle unavailable betting markets gracefully
- **Bookmaker Coverage**: Monitor active bookmaker status

## Deployment

### Environment Variables
Required environment variables:
- `DATABASE_URL`: Database connection string
- `ENV`: Environment (dev, test, prod)
- `LOG_LEVEL`: Logging level
- `ODDS_API_KEY`: The Odds API key (NEW)
- `ODDS_API_BASE_URL`: API base URL (NEW)

### Database Migrations
- Use Alembic for migrations
- Always test migrations in development first
- Create rollback scripts
- Betting system migration validation

### Monitoring
- Set up database monitoring
- Configure alerts
- Log slow queries
- Monitor betting data freshness
- Track API usage and costs

## Contributing

### Code Review Process
1. Create feature branch
2. Write tests
3. Submit pull request
4. Address review comments
5. Merge after approval

### Documentation
- Update relevant documentation
- Add docstrings
- Include examples
- Betting system integration examples

### Testing
- Write unit tests
- Update integration tests
- Test edge cases
- Validate betting calculations