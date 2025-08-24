from datetime import datetime
from typing import Optional, Dict, List
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from pydantic import EmailStr, validator
import secrets
import string
import hashlib

from .enums import *

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    preferences: Dict = Field(default_factory=dict, sa_column=Column(JSON))

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[Dict] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    salt: str = Field(nullable=False)
    
    # Relationships
    settings: Optional["UserSettings"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    fantasy_rosters: List["FantasyRoster"] = Relationship(back_populates="user")
    # favorite_players relationship removed - favorite player functionality deprecated
    decisions: List["UserDecision"] = Relationship(back_populates="user")

    def set_password(self, password: str):
        """Hash and salt the password."""
        self.salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        salted_password = password + self.salt
        self.hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        salted_password = password + self.salt
        return self.hashed_password == hashlib.sha256(salted_password.encode()).hexdigest()

class UserSettingsBase(SQLModel):
    nfl_team_colors: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    data_weights: Dict = Field(
        default_factory=lambda: {"expert_rankings": 0.3, "projections": 0.4, "matchup": 0.3},
        sa_column=Column(JSON)
    )
    twitter_accounts: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    dark_mode: bool = Field(default=True)
    notifications_enabled: bool = Field(default=True)
    email_notifications: bool = Field(default=True)
    push_notifications: bool = Field(default=False)
    default_league_id: Optional[int] = None

class UserSettings(UserSettingsBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: User = Relationship(back_populates="settings")

class UserSettingsUpdate(SQLModel):
    nfl_team_colors: Optional[Dict] = None
    data_weights: Optional[Dict] = None
    twitter_accounts: Optional[List[str]] = None
    dark_mode: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    default_league_id: Optional[int] = None

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class TokenData(SQLModel):
    username: Optional[str] = None
