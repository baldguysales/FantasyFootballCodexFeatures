from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text

from .enums import Platform

class FantasyRosterBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", index=True)
    platform: Platform

class FantasyRoster(FantasyRosterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    roster_data: Optional[str] = Field(default=None, sa_column=Column(Text))
    roster_metadata: Optional[str] = Field(default=None, sa_column=Column(Text))
    tags: Optional[str] = Field(default=None, sa_column=Column(Text))
    last_sync: Optional[datetime] = Field(default=None)
    
class FantasyRosterCreate(FantasyRosterBase):
    roster_data: Optional[Dict[str, Any]] = None
    roster_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class FantasyRosterRead(FantasyRosterBase):
    id: int
    roster_data: Optional[Dict[str, Any]] = None
    roster_metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    last_sync: Optional[datetime] = None

