# FF Codex Authentication Service - Development Notes

## Architecture Overview

The authentication service is built on FastAPI and integrates with the main FF Codex project's User model. It provides JWT-based authentication with access and refresh tokens.

## Key Components

### Core Components
- **main.py**: Application entry point with FastAPI setup
- **app/core/**: Core configuration and utilities
  - `config.py`: Application configuration
  - `auth_dependencies.py`: Authentication dependencies and utilities

### Models
- **app/models/**: Data models
  - `user.py`: Integration with main User model
  - `user_integration.py`: Integration layer for User model

### Routers
- **app/routers/**: API endpoints
  - `auth.py`: Authentication routes (login, register, refresh, etc.)

### Schemas
- **app/schemas/**: Pydantic models for request/response validation
  - `auth.py`: Authentication schemas
  - `user.py`: User-related schemas

## Development Setup

1. **Prerequisites**
   - Python 3.8+
   - PostgreSQL 12+
   - Main FF Codex project (for User model)

2. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -e .
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Running the Service**
   ```bash
   # Start the development server
   uvicorn main:app --reload
   ```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## Key Implementation Details

1. **Authentication Flow**
   - JWT tokens with configurable expiration
   - Refresh token mechanism
   - Password hashing with bcrypt and per-user salt

2. **Integration with Main Project**
   - Extends the main User model
   - Maintains compatibility with existing database schema
   - Reuses core models and configurations

3. **Security**
   - Secure password handling
   - Token-based authentication
   - Role-based access control

## Common Issues and Solutions

1. **Import Errors**
   - Ensure the main FF Codex project is in your Python path
   - Check that all dependencies are installed

2. **Database Connection**
   - Verify PostgreSQL is running
   - Check database URL in .env file
   - Ensure the database and user exist and have proper permissions

3. **Authentication**
   - Verify JWT secret key is set
   - Check token expiration settings
   - Ensure proper headers in API requests

## Best Practices

- Use dependency injection for database sessions
- Follow RESTful API design principles
- Implement proper error handling and logging
- Write unit tests for new features
- Keep dependencies up to date
