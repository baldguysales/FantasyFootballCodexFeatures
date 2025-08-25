from datetime import datetime, timezone
from typing import Optional, List, Dict, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, ForeignKey, Index
from pydantic import validator
from typing import ClassVar, Tuple

if TYPE_CHECKING:
    from .social_media_injury import SocialMediaInjury

class PlayerBase(SQLModel):
    """Base model for core NFL player data from player table.
    
    This model contains the essential player identification and attributes.
    """
    # Primary identifier - GSIS ID
    gsis_id: str = Field(primary_key=True, index=True, description="Primary GSIS identifier")
    
    # Names
    display_name: str = Field(..., description="Player's display name")
    common_first_name: Optional[str] = Field(None, description="Common first name")
    first_name: Optional[str] = Field(None, description="Legal first name")
    last_name: Optional[str] = Field(None, description="Last name")
    short_name: Optional[str] = Field(None, description="Short name")
    football_name: Optional[str] = Field(None, description="Football name/nickname")
    suffix: Optional[str] = Field(None, description="Name suffix")
    
    # External IDs
    esb_id: Optional[str] = Field(None, index=True, description="ESB ID")
    nfl_id: Optional[str] = Field(None, index=True, description="NFL ID")
    pfr_id: Optional[str] = Field(None, index=True, description="Pro Football Reference ID")
    pff_id: Optional[str] = Field(None, index=True, description="Pro Football Focus ID")
    otc_id: Optional[str] = Field(None, index=True, description="Over The Cap ID")
    espn_id: Optional[str] = Field(None, index=True, description="ESPN ID")
    smart_id: Optional[str] = Field(None, index=True, description="SMART ID")
    
    # Physical attributes
    birth_date: Optional[datetime] = Field(None, description="Birth date")
    height: Optional[float] = Field(None, description="Height in inches")
    weight: Optional[float] = Field(None, description="Weight in pounds")
    headshot: Optional[str] = Field(None, description="Headshot URL")
    
    # Position information
    position_group: Optional[str] = Field(None, description="Position group")
    position: Optional[str] = Field(None, description="Primary position")
    ngs_position_group: Optional[str] = Field(None, description="NGS position group")
    ngs_position: Optional[str] = Field(None, description="NGS position")
    
    # College and education
    college_name: Optional[str] = Field(None, description="College name")
    college_conference: Optional[str] = Field(None, description="College conference")
    
    # Career information
    jersey_number: Optional[int] = Field(None, description="Jersey number")
    rookie_season: Optional[int] = Field(None, description="Rookie season")
    last_season: Optional[int] = Field(None, description="Last active season")
    years_of_experience: Optional[int] = Field(None, description="Years of NFL experience")
    
    # Current team and status
    latest_team: Optional[str] = Field(None, description="Most recent team")
    status: Optional[str] = Field(None, description="Player status")
    ngs_status: Optional[str] = Field(None, description="NGS status")
    ngs_status_short_description: Optional[str] = Field(None, description="NGS status description")
    
    # PFF specific
    pff_position: Optional[str] = Field(None, description="PFF position")
    pff_status: Optional[str] = Field(None, description="PFF status")
    
    # Draft information
    draft_year: Optional[float] = Field(None, description="Draft year")
    draft_round: Optional[float] = Field(None, description="Draft round")
    draft_pick: Optional[float] = Field(None, description="Draft pick number")
    draft_team: Optional[str] = Field(None, description="Team that drafted player")


class Player(PlayerBase, table=True):
    """Player model for core NFL player information."""
    __tablename__ = "player"
    
    # Relationships - Updated to use new roster model
    roster_entries: List["PlayerWeekRoster"] = Relationship(back_populates="player")
    week_stats: List["PlayerWeekStats"] = Relationship(back_populates="player")
    week_points: List["PlayerWeekPoints"] = Relationship(back_populates="player")
    injury_reports: List["InjuryReport"] = Relationship(back_populates="player")
    social_media_posts: List["SocialMediaPost"] = Relationship(back_populates="player")
    social_media_injuries: List["SocialMediaInjury"] = Relationship(back_populates="player")
    ai_summaries: List["AISummary"] = Relationship(back_populates="player")
    fantasy_rosters: List["FantasyRoster"] = Relationship(back_populates="players")
    props: List["PlayerProp"] = Relationship(back_populates="player")
    decisions: List["UserDecision"] = Relationship(back_populates="player")
    
    # Indexes for better query performance
    __table_args__: ClassVar[Tuple] = (
        Index('ix_player_latest_team', 'latest_team'),
        Index('ix_player_position', 'position'),
        Index('ix_player_status', 'status'),
        Index('ix_player_rookie_season', 'rookie_season'),
        Index('ix_player_last_season', 'last_season'),
    )
    
    @validator('jersey_number', 'height', 'rookie_year', 'draft_number', 'age', pre=True)
    def convert_to_float(cls, v):
        """Convert numeric fields to float to match database schema."""
        if v is None or isinstance(v, float):
            return v
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

# Game model has been removed as per user request
