# FF Codex Authentication Integration Guide

This guide provides essential information for integrating the FF Codex Authentication service with other components of the FF Codex platform.

## Authentication Flow

The authentication service provides the following endpoints:

- `POST /auth/register` - Register a new user
- `POST /auth/token` - Login and get access/refresh tokens
- `POST /auth/refresh` - Refresh access token using refresh token
- `GET /auth/me` - Get current user's profile
- `PUT /auth/me` - Update current user's profile
- `DELETE /auth/me` - Delete current user

## Integration Patterns

### 1. Protecting Routes

To protect a route, use the `get_current_active_user` dependency:

```python
from fastapi import Depends, APIRouter
from app.core.auth_dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}"}
```

### 2. Role-Based Access Control

For admin-only routes, use the `get_current_active_superuser` dependency:

```python
@router.get("/admin-only")
async def admin_route(
    current_user: User = Depends(get_current_active_superuser)
):
    return {"message": "Admin access granted"}
```

### 3. Making Authenticated Requests

Include the JWT token in the Authorization header:
```
Authorization: Bearer your.jwt.token.here
```

## Error Handling

Common error responses:

- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found

## Configuration

The following environment variables must be set:

```env
# JWT Configuration
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ff_codex
```

## Dependencies

The authentication service depends on:

- Main FF Codex User model
- PostgreSQL database
- Python 3.8+
- FastAPI
- SQLAlchemy
- Pydantic v2
    
    class Config:
        env_file = ".env"
4. Service Layer Pattern
✅ Use this UserService pattern for all services:

python
class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        # Implementation with proper error handling
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        # Implementation
📁 Working File Structure
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              ✅ Working
│   │   ├── database.py            ✅ Working  
│   │   └── auth_dependencies.py   ✅ Working
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py               ✅ Working
│   │   └── [25+ other models]    ✅ Working
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── auth.py               ✅ Working
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py               ✅ Working
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py       ✅ Working
│   └── utils/
│       ├── __init__.py
│       └── auth_utils.py         ✅ Working
├── main.py                       ✅ Working
└── pyproject.toml               ✅ Working
🚨 Common Integration Issues to Avoid
1. Don't Recreate Existing Models
✅ Use existing User model from app/models/user.py
❌ Don't create new user tables or models
2. Database Connection
✅ Use existing get_db() from app/core/database.py
✅ PostgreSQL connection string format
❌ Don't switch back to SQLite
3. Dependencies
Required packages already added:

toml
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
pydantic-settings = "^2.0.0"
4. Environment Variables
Required in .env:

bash
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://username:password@localhost/ff_codex_v2
🎯 Integration Success Checklist
When adding new features, ensure:

 Uses existing database models (don't recreate)
 Follows Pydantic v2 syntax (from_attributes, pattern)
 Imports from correct paths (app.models.user, not recreated models)
 Uses existing get_db() dependency
 Follows service layer pattern
 Includes proper error handling
 Works with PostgreSQL (not SQLite)
🚀 Next Feature Development
For NFL data integration or other features:

Start from this working foundation
Use existing User model for relationships
Follow the service layer pattern
Test integration before committing
📝 Git Tags Reference
v0.1.0-database - Complete PostgreSQL schema foundation
v0.2.0-auth - Working authentication system
v0.3.0-nfl-data - (Next: NFL data integration)
🎯 Key Takeaway: This foundation is battle-tested and working. Future Windsurf features should build ON this foundation, not recreate it.


