# Development Notes

This document contains internal development notes, architecture decisions, and implementation details for the NFL Fantasy Football database.

## Table of Contents

- [Database Schema](#database-schema)
- [Model Architecture](#model-architecture)
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

### PlayerWeekRoster Table (NEW)
- Primary Key: `id` (INTEGER, auto-increment)
- Foreign Key: `player_id` references Player.gsis_id
- Contains weekly roster status, position, team assignments
- Unique constraint on (player_id, season, week)
- Indexes on: player_id, team, season, week combinations

### Social Media Injury Tables
- `social_media_injury`: Stores injury reports from social media
- `social_media_injury_matches`: Tracks manual matches between reports and players

### Social Media Injury Tables (FOREIGN KEY UPDATED)
- `social_media_injury`: Foreign key now references Player.gsis_id
- `social_media_injury_matches`: Foreign key now references Player.gsis_id

## Model Architecture

### Base Models
- `BaseModel`: Common fields and methods for all models
- `Base`: SQLAlchemy declarative base

### Team and Player Models (UPDATED)
- `TeamBase`: Base fields for teams (unchanged)
- `Team`: Table model with relationships (unchanged)
- `PlayerBase`: Base fields for core player data only (simplified)
- `Player`: Core player identification model with gsis_id primary key
- `PlayerWeekRosterBase`: Base fields for weekly roster data (NEW)
- `PlayerWeekRoster`: Weekly roster tracking model (NEW)

### Breaking Changes
- All foreign key references to Player must use gsis_id instead of player_id
- Player model no longer contains weekly roster data
- New PlayerWeekRoster model handles all season/week-specific data

### Social Media Models
- `SocialMediaInjury`: Stores injury reports
- `SocialMediaInjuryMatch`: Tracks report-player matches

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

### Integration Tests
- Test database operations
- Test model relationships
- Test transaction handling

### Fixtures
- Database setup/teardown
- Test data generation
- Mock services

## Performance Considerations

### Indexing Strategy
- Indexes on frequently queried columns
- Composite indexes for common query patterns
- Partial indexes for filtered queries

### Query Optimization
- Eager loading for related data
- Select only required columns
- Batch operations for bulk data

### Caching
- Consider adding Redis for caching
- Cache invalidation strategy
- Query result caching

## Known Issues

1. **Circular Imports**
   - Currently managed with `TYPE_CHECKING`
   - Consider refactoring to avoid circular dependencies

2. **Async Session Management**
   - Need to ensure proper session cleanup
   - Potential for session leaks in error cases

## Future Improvements

### Schema Changes
1. Add more detailed player statistics
2. Implement historical data tracking
3. Add support for multiple seasons

### Performance
1. Implement connection pooling
2. Add query caching
3. Optimize bulk operations

### Features
1. Add data validation middleware
2. Implement change tracking
3. Add audit logging

## Development Workflow

### Code Style
- Follow PEP 8
- Use type hints
- Document public APIs

### Version Control
- Feature branches
- Meaningful commit messages
- Pull request reviews

### Dependencies
- Manage with Poetry
- Pin all dependencies
- Regular updates

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

## Deployment

### Environment Variables
Required environment variables:
- `DATABASE_URL`: Database connection string
- `ENV`: Environment (dev, test, prod)
- `LOG_LEVEL`: Logging level

### Database Migrations
- Use Alembic for migrations
- Always test migrations in development first
- Create rollback scripts

### Monitoring
- Set up database monitoring
- Configure alerts
- Log slow queries

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

### Testing
- Write unit tests
- Update integration tests
- Test edge cases
