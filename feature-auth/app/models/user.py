"""
User model integration with the main FF Codex project.

This module provides integration with the existing User model from the main project,
extending it with authentication-specific functionality.
"""
from typing import Optional, Type, Any, Dict, TypeVar, Generic, Type, cast, TYPE_CHECKING
import sys
from pathlib import Path

# Add the main project to the Python path
main_project_path = str(Path.home() / "Documents" / "ff-codex-gdm-v1" / "backend")
if main_project_path not in sys.path:
    sys.path.insert(0, main_project_path)

# Import SQLAlchemy base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base

# Create a base class that will be used by all models
Base = declarative_base()

# Import the main project's User model using a direct path to avoid circular imports
main_user_module = __import__('app.models.user', fromlist=['User'])
MainUser = main_user_module.User

# Import schema models
main_schemas = __import__('app.schemas.user', fromlist=['UserCreate', 'UserUpdate'])
MainUserCreate = main_schemas.UserCreate
MainUserUpdate = main_schemas.UserUpdate

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

# Add methods to the User class
setattr(MainUser, 'set_password', set_password)
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
__all__ = ['Base', 'User', 'UserCreate', 'UserUpdate']
