# FF Codex Authentication Service

Authentication and user management service for the FF Codex fantasy football platform. This service provides JWT-based authentication and integrates with the main FF Codex project's User model.

## Features

- 🔐 JWT-based authentication with access and refresh tokens
- 👤 User registration and profile management
- 🔒 Password hashing with bcrypt and per-user salt
- 🏷️ Role-based access control (user/admin)
- 🔄 Token refresh functionality
- ✅ Integration with existing FF Codex User model
- 🚦 Input validation with Pydantic
- 🛡️ Secure password handling

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Main FF Codex project (for User model integration)

## Installation

1. Ensure you have the main FF Codex project cloned and set up at `~/Documents/ff-codex-gdm-v1/backend`

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

Copy `.env.example` to `.env` and update the following variables:

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ff_codex

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

```env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database
DATABASE_URI=postgresql+asyncpg://user:password@localhost:5432/ff_codex_auth

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://your-frontend-domain.com"]

# Email (for password reset, etc.)
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.example.com
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=no-reply@ffcodex.com
EMAILS_FROM_NAME="FF Codex"
```

## Running the Application

### Development

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Production

For production, use a production-ready ASGI server like Uvicorn with Gunicorn:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Code Style

We use `black` for code formatting and `isort` for import sorting:

```bash
black .
isort .
```

### Testing

Run tests with pytest:

```bash
pytest
```

### Linting

```bash
pylint app/
```

### Type Checking

```bash
mypy app/
```

## Deployment

### Docker

Build the Docker image:

```bash
docker build -t ff-codex-auth .
```

Run the container:

```bash
docker run -d --name ff-codex-auth -p 8000:8000 --env-file .env ff-codex-auth
```

### Kubernetes

Example deployment files are provided in the `k8s/` directory.

## Environment Variables

See `.env.example` for all available configuration options.

## License

MIT
