# NFL Fantasy Football Database

This repository contains the database models and ETL pipelines for the NFL Fantasy Football application. It's built using SQLAlchemy with async support and follows a modular, type-hinted architecture.

## Features

- **Player Management**: Comprehensive player data with detailed attributes and statistics
- **Team Management**: Complete team information including logos, colors, and conference/division data
- **Injury Tracking**: Integration with social media for real-time injury reports
- **Data Validation**: Robust data validation using Pydantic models
- **Async Support**: Built with async SQLAlchemy for high-performance database operations

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL 13+
- Poetry (for dependency management)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Set up your environment variables (copy `.env.example` to `.env` and update values)
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
│   ├── teams_players.py       # Team and Player models
│   ├── social_media_injury.py # Injury tracking from social media
│   ├── betting.py            # Betting odds and related data
│   ├── fantasy.py            # Fantasy football specific models
│   ├── intelligence.py       # AI/ML features and intelligence
│   ├── ml.py                 # Machine learning models
│   ├── roster.py             # Team roster management
│   ├── sql_functions.py      # Database functions and procedures
│   ├── stats.py              # Player and team statistics
│   └── user.py               # User accounts and authentication
├── scripts/                  # Database scripts and ETL
│   ├── recreate_*.py         # Table recreation scripts
│   └── utilities/            # Helper scripts
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── alembic/                  # Database migrations
│   ├── versions/             # Migration scripts
│   ├── env.py               # Migration environment
│   └── script.py.mako       # Migration template
└── docs/                     # Documentation
    ├── SCHEMA.md            # Database schema documentation
    └── examples/            # Code examples
```

## Documentation

- [Integration Guide](./INTEGRATION_GUIDE.md) - How to integrate with this service
- [Development Notes](./DEVELOPMENT_NOTES.md) - Internal development documentation
- [Database Schema](./docs/SCHEMA.md) - Detailed database schema documentation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
