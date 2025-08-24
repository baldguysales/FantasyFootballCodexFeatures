"""
User model integration with the main FF Codex project.

This module provides a clean way to extend the main project's User model
with authentication-specific functionality without circular imports.
"""
from typing import Optional, Type, Any, Dict, TypeVar, Generic, Type, cast, TYPE_CHECKING
import sys
from pathlib import Path

# Add the main project to the Python path
main_project_path = str(Path.home() / "Documents" / "ff-codex-gdm-v1" / "backend")
if main_project_path not in sys.path:
    sys.path.insert(0, main_project_path)

try:
    # Import the main project's User model
    from app.models.user import User as MainUser
    from app.schemas.user import UserCreate as MainUserCreate
    from app.schemas.user import UserUpdate as MainUserUpdate
    
    # Import successful, we can proceed with the integration
    HAS_MAIN_PROJECT = True
except ImportError as e:
    # Main project not available, create mock classes for development
    HAS_MAIN_PROJECT = False
    
    class MockBase:
        pass
    
    class MockUser:
        def __init__(self):
            self.salt = None
            self.hashed_password = None
        
        def set_password(self, password: str) -> None:
            """Mock password hashing for testing."""
            self.salt = "mocksalt"
            self.hashed_password = f"mockhash_{password}"
        
        def verify_password(self, password: str) -> bool:
            """Mock password verification for testing."""
            return self.hashed_password == f"mockhash_{password}"
    
    class MockUserCreate:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        
        def dict(self):
            return self.__dict__
    
    class MockUserUpdate(MockUserCreate):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
    
    MainUser = MockUser
    MainUserCreate = MockUserCreate
    MainUserUpdate = MockUserUpdate

# Authentication methods
def set_password(self, password: str) -> None:
    """Hash and salt the password using bcrypt."""
    from ..utils.auth_utils import generate_salt, hash_password
    self.salt = generate_salt()
    self.hashed_password = hash_password(password, self.salt)

def verify_password(self, password: str) -> bool:
    """Verify a password against the stored hash."""
    from ..utils.auth_utils import verify_password
    return verify_password(password, self.salt, self.hashed_password)

# Add methods to the User class if they don't exist
if not hasattr(MainUser, 'set_password'):
    setattr(MainUser, 'set_password', set_password)
if not hasattr(MainUser, 'verify_password'):
    setattr(MainUser, 'verify_password', verify_password)

# Create a UserUpdate class that extends the main project's UserUpdate
class UserUpdate(MainUserUpdate):
    """Extends the main project's UserUpdate with auth-specific fields."""
    current_password: Optional[str] = None
    new_password: Optional[str] = None

# Re-export the models with their original names
User = MainUser
UserCreate = MainUserCreate
UserUpdate = UserUpdate  # Use our extended version

# Add type hints for IDE support
__all__ = ['User', 'UserCreate', 'UserUpdate']

# Add a flag to check if we're using the real or mock implementation
__is_mock__ = not HAS_MAIN_PROJECT
