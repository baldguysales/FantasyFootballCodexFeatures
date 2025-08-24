from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.auth import UserCreate
from app.utils.auth_utils import hash_password
from typing import Optional

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with hashed password
        """
        try:
            # Hash the password
            hashed_password = hash_password(user_data.password)
            
            # Create user instance
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=True,  # Default to active
                role="user"  # Default role
            )
            
            # Add to database
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            return db_user
            
        except IntegrityError as e:
            self.db.rollback()
            # Check if it's a duplicate username or email
            if "username" in str(e.orig):
                raise ValueError("Username already exists")
            elif "email" in str(e.orig):
                raise ValueError("Email already exists")
            else:
                raise ValueError("User creation failed due to data conflict")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"User creation failed: {str(e)}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update user with provided fields
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Update only provided fields
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"User update failed: {str(e)}")
    
    def delete_user(self, user_id: int) -> bool:
        """
        Delete user by ID
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            self.db.delete(user)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"User deletion failed: {str(e)}")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        """
        from app.utils.auth_utils import verify_password
        
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
