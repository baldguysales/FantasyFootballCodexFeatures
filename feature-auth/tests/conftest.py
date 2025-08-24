import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables before importing app
os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["JWT_REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

from app.main import app
from app.core.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override the get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the database dependency in the app
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def db_session():
    """Create a new database session for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@pytest.fixture(scope="module")
def test_user():
    """Create test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!"
    }

@pytest.fixture(scope="module")
def test_admin():
    """Create test admin user data."""
    return {
        "email": "admin@example.com",
        "username": "admin",
        "password": "AdminPass123!"
    }
