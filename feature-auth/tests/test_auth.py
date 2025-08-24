import pytest
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.schemas.auth import Token

# Test registration
def test_register_user(client, test_user, db_session: Session):
    """Test user registration with valid data."""
    # Test successful registration
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]
    assert "hashed_password" not in data
    assert "salt" not in data
    
    # Test duplicate email
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "username": "anotheruser",
            "password": "AnotherPass123!"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.text
    
    # Test duplicate username
    response = client.post(
        "/api/auth/register",
        json={
            "email": "another@example.com",
            "username": test_user["username"],
            "password": "AnotherPass123!"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already taken" in response.text

# Test login
def test_login_user(client, test_user, db_session: Session):
    """Test user login with valid and invalid credentials."""
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    
    # Test successful login with username
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    # Test successful login with email
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Test invalid password
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test non-existent user
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test token refresh
def test_refresh_token(client, test_user, db_session: Session):
    """Test token refresh flow."""
    # Register and login to get tokens
    client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Test successful token refresh
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    # Test invalid refresh token
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": "invalid-token"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# Test protected endpoints
def test_protected_endpoints(client, test_user, db_session: Session):
    """Test access to protected endpoints."""
    # Register and login to get tokens
    client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    access_token = login_response.json()["access_token"]
    
    # Test accessing protected endpoint with valid token
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    
    # Test accessing protected endpoint without token
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test accessing protected endpoint with invalid token
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test user update
def test_update_user(client, test_user, db_session: Session):
    """Test updating user information."""
    # Register and login to get tokens
    client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    access_token = login_response.json()["access_token"]
    
    # Test updating email
    response = client.put(
        "/api/auth/me",
        json={"email": "newemail@example.com"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "newemail@example.com"
    
    # Test updating password
    response = client.put(
        "/api/auth/me",
        json={
            "current_password": test_user["password"],
            "new_password": "NewPass123!"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify new password works
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": "NewPass123!"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == status.HTTP_200_OK

# Test admin endpoints
def test_admin_endpoints(client, test_user, test_admin, db_session: Session):
    """Test admin-only endpoints."""
    # Create a regular user
    client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    
    # Create an admin user directly in the database
    from app.services.user_service import UserService
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        admin_salt = "test-salt"
        admin_hashed_password = UserService.hash_password(test_admin["password"], admin_salt)
        admin_user = User(
            email=test_admin["email"],
            username=test_admin["username"],
            hashed_password=admin_hashed_password,
            salt=admin_salt,
            is_superuser=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Login as admin
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": test_admin["username"],
                "password": test_admin["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == status.HTTP_200_OK
        admin_token = login_response.json()["access_token"]
        
        # Test getting all users (admin only)
        response = client.get(
            "/api/auth/users/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert len(users) >= 2  # At least admin and test user
        
        # Test deactivating a user (admin only)
        test_user_id = next(u["id"] for u in users if u["username"] == test_user["username"])
        response = client.patch(
            f"/api/auth/users/{test_user_id}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_active"] is False
        
        # Test reactivating a user (admin only)
        response = client.patch(
            f"/api/auth/users/{test_user_id}/activate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_active"] is True
        
    finally:
        db.close()

# Test user deletion
def test_delete_user(client, test_user, db_session: Session):
    """Test user self-deletion."""
    # Register and login to get tokens
    client.post(
        "/api/auth/register",
        json={
            "email": test_user["email"],
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    access_token = login_response.json()["access_token"]
    
    # Delete the user
    response = client.delete(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the user is deleted
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
