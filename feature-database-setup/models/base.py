from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, func

Base = declarative_base()

class BaseModel:
    """Base model class with common columns and methods"""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                      onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}