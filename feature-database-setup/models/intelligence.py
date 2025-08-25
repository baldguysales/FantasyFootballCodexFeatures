from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text

class InjuryReportBase(SQLModel):
    player_id: str = Field(foreign_key="player.gsis_id", index=True)
    status: str = Field(max_length=50)  # Using string instead of enum
    description: Optional[str] = None
    severity: Optional[int] = Field(default=None, ge=1, le=10)
    source: Optional[str] = None

class InjuryReport(InjuryReportBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    estimated_return: Optional[datetime] = None
    reported_at: datetime = Field(default_factory=datetime.utcnow)

class SocialMediaPostBase(SQLModel):
    player_id: str = Field(foreign_key="player.gsis_id", index=True)
    platform: str = Field(max_length=50)  # Using string instead of enum
    content: str = Field(sa_column=Column(Text))
    author: Optional[str] = None

class SocialMediaPost(SocialMediaPostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sentiment_score: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

class AISummaryBase(SQLModel):
    player_id: str = Field(foreign_key="player.gsis_id", index=True)
    summary_type: str = Field(max_length=50)
    content: str = Field(sa_column=Column(Text))

class AISummary(AISummaryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# API schemas
class InjuryReportCreate(InjuryReportBase):
    pass

class InjuryReportRead(InjuryReportBase):
    id: int
    estimated_return: Optional[datetime] = None
    reported_at: datetime

class SocialMediaPostCreate(SocialMediaPostBase):
    pass

class SocialMediaPostRead(SocialMediaPostBase):
    id: int
    sentiment_score: Optional[float] = None
    posted_at: datetime
    scraped_at: datetime

class AISummaryCreate(AISummaryBase):
    pass

class AISummaryRead(AISummaryBase):
    id: int
    confidence_score: Optional[float] = None
    generated_at: datetime
