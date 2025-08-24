import bcrypt
import secrets
import string
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import os
import sys
from pathlib import Path

# Add the main project to the Python path
main_project_path = str(Path.home() / "Documents" / "ff-codex-gdm-v1" / "backend")
if main_project_path not in sys.path:
    sys.path.append(main_project_path)

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)

def generate_salt() -> str:
    """
    Generate a cryptographically secure random salt.
    
    Returns:
        str: A URL-safe base64-encoded string of 32 random bytes (43-44 characters)
    """
    return secrets.token_urlsafe(32)

def hash_password(password: str, salt: str) -> str:
    """
    Hash a password with a salt using bcrypt.
    
    Args:
        password: The plain text password to hash
        salt: The salt to use for hashing
        
    Returns:
        str: The hashed password
        
    Raises:
        ValueError: If password or salt is empty/None
    """
    if not password:
        raise ValueError("Password cannot be empty")
    if not salt:
        raise ValueError("Salt cannot be empty")
    
    try:
        # Combine password and salt before hashing
        salted_password = f"{password}{salt}"
        return pwd_context.hash(salted_password)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise

def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The password to verify
        salt: The salt that was used during hashing
        hashed_password: The stored hashed password
        
    Returns:
        bool: True if password matches, False otherwise
        
    Raises:
        ValueError: If any parameter is empty/None
    """
    if not plain_password or not salt or not hashed_password:
        return False
    
    try:
        # Combine password and salt in the same way as during hashing
        salted_password = f"{plain_password}{salt}".encode('utf-8')
        
        # Verify the password using the same salt
        return pwd_context.verify(salted_password, hashed_password)
    except (ValueError, bcrypt.exceptions.BCryptError) as e:
        logger.warning(f"Password verification failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in verify_password: {str(e)}")
        return False

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing the claims to encode in the token
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        str: Encoded JWT token
        
    Raises:
        JWTError: If there's an error encoding the token
    """
    if not data:
        raise ValueError("Token data cannot be empty")
        
    to_encode = data.copy()
    now = datetime.utcnow()
    
    # Set expiration time
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard claims
    to_encode.update({
        "exp": expire,
        "iat": now,
        "iss": settings.JWT_ISSUER,
        "jti": secrets.token_urlsafe(16)  # Unique token ID
    })
    
    try:
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise JWTError("Failed to create access token")

def verify_token(token: str) -> bool:
    """
    Verify if a JWT token is valid.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    if not token:
        return False
        
    try:
        payload = decode_jwt(token)
        return payload is not None
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in verify_token: {str(e)}")
        return False

def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        JWTError: If the token is invalid, expired, or tampered with
    """
    if not token:
        raise JWTError("Token cannot be empty")
        
    try:
        # Decode the token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require_exp": True,
                "verify_aud": False,
                "verify_iss": bool(settings.JWT_ISSUER)
            },
            issuer=settings.JWT_ISSUER if settings.JWT_ISSUER else None
        )
        
        # Additional custom validations can be added here
        if "sub" not in payload:
            raise JWTError("Missing required claim: sub")
            
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        raise JWTError("Invalid token") from e
    except Exception as e:
        logger.error(f"Unexpected error in decode_jwt: {str(e)}")
        raise JWTError("Failed to decode token") from e
