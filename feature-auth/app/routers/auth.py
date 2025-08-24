from datetime import timedelta, datetime
from typing import Any, Optional, Dict, List
import sys
from pathlib import Path

# Add the main project to the Python path
main_project_path = str(Path.home() / "Documents" / "ff-codex-gdm-v1" / "backend")
if main_project_path not in sys.path:
    sys.path.append(main_project_path)

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ..core.config import settings
from ..models.database import get_session as get_db
from ..core.auth_dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    oauth2_scheme,
    credentials_exception
)

# Import the main project's models
from app.models.user import User as MainUser, UserCreate as MainUserCreate, UserUpdate as MainUserUpdate

# Import local models and schemas
from ..models.user import User, UserCreate, UserUpdate
from ..schemas.auth import (
    Token,
    UserResponse,
    UserPublic,
    TokenRefresh
)
from ..services.user_service import UserService
from ..utils.auth_utils import create_access_token, verify_password, decode_jwt

router = APIRouter(prefix="/auth", tags=["authentication"])

def create_tokens(user: User) -> Dict[str, Any]:
    """Create access and refresh tokens for a user.
    
    Args:
        user: The user to create tokens for
        
    Returns:
        Dictionary containing access_token, refresh_token, and token metadata
    """
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Create access token with user claims
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "scopes": ["admin"] if user.is_superuser else ["user"]
        },
        expires_delta=access_token_expires
    )
    
    # Create refresh token (longer expiration)
    refresh_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "refresh": True  # Mark as refresh token
        },
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user."""
    try:
        user = UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    This endpoint accepts a username/email and password and returns JWT tokens
    for authentication.
    """
    try:
        # Authenticate user
        user = UserService.authenticate_user(
            db, 
            username_or_email=form_data.username,
            password=form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Generate and return tokens
        return create_tokens(user)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """Refresh an access token using a refresh token."""
    try:
        from jose import jwt
        from jose.exceptions import JWTError
        
        # Verify refresh token
        try:
            payload = jwt.decode(
                refresh_data.refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check if token is a refresh token
            if not payload.get("refresh"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token type"
                )
                
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if not username or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token"
                )
                
            # Get user from database
            user = UserService.get_user_by_id(db, user_id)
            if not user or user.username != username or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found or inactive"
                )
                
            # Generate new access token
            return create_tokens(user)
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired refresh token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's profile.
    
    Returns the profile of the currently authenticated user.
    """
    # Convert SQLAlchemy model to Pydantic model
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user's information.
    
    This endpoint allows users to update their profile information.
    Password updates require the current password for verification.
    """
    try:
        # Convert Pydantic model to dict and remove None values
        update_data = user_update.dict(exclude_unset=True)
        
        # Create a new UserUpdate instance with the filtered data
        filtered_update = UserUpdate(**update_data)
        
        # Update the user
        updated_user = UserService.update_user(
            db,
            user_id=current_user.id,
            user_data=filtered_update,
            current_password=user_update.current_password if hasattr(user_update, 'current_password') else None
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return UserResponse.from_orm(updated_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user"
        )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> None:
    """Delete current user."""
    success = UserService.delete_user(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None

# Admin-only endpoints
@router.get("/users/", response_model=list[UserPublic])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """Retrieve users (admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserPublic)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific user by ID (admin only)."""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.patch("/users/{user_id}/deactivate", response_model=UserPublic)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """Deactivate a user (admin only)."""
    user = UserService.set_user_active_status(db, user_id, False)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.patch("/users/{user_id}/activate", response_model=UserPublic)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """Activate a user (admin only)."""
    user = UserService.set_user_active_status(db, user_id, True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
