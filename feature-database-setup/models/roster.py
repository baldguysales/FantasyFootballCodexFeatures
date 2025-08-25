from datetime import datetime, timezone
from typing import Optional, List, ClassVar, Tuple
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint, Index
from pydantic import validator

class PlayerWeekRosterBase(SQLModel):
    """Base model for weekly roster information from playerweekroster table.
    
    This model tracks a player's roster status for a specific week and season.
    """
    # Core identifiers matching the database schema
    player_id: str = Field(
        foreign_key="player.gsis_id", 
        index=True,
        description="Reference to the player (GSIS ID)"
    )
    season: int = Field(
        ge=1920,
        description="NFL season year"
    )
    week: int = Field(
        ge=1, le=22,
        description="Week of the season"
    )
    
    # Player identification fields from database
    pff_id: Optional[str] = Field(None, description="Pro Football Focus ID")
    pfr_id: Optional[str] = Field(None, description="Pro Football Reference ID")
    fantasy_data_id: Optional[str] = Field(None, description="Fantasy Data ID")
    sleeper_id: Optional[str] = Field(None, description="Sleeper ID")
    esb_id: Optional[str] = Field(None, description="ESB ID")
    gsis_it_id: Optional[str] = Field(None, description="GSIS IT ID")
    smart_id: Optional[str] = Field(None, description="SMART ID")
    espn_id: Optional[str] = Field(None, description="ESPN ID")
    sportradar_id: Optional[str] = Field(None, description="SportRadar ID")
    yahoo_id: Optional[str] = Field(None, description="Yahoo ID")
    rotowire_id: Optional[str] = Field(None, description="Rotowire ID")
    
    # Player basic info
    player_name: str = Field(..., description="Player's full name")
    first_name: Optional[str] = Field(None, description="Player's first name")
    last_name: Optional[str] = Field(None, description="Player's last name")
    football_name: Optional[str] = Field(None, description="Player's football name")
    
    # Physical attributes
    birth_date: Optional[datetime] = Field(None, description="Player's birth date")
    age: Optional[float] = Field(None, description="Player's age")
    height: Optional[float] = Field(None, description="Player's height in inches")
    weight: Optional[int] = Field(None, description="Player's weight in pounds")
    
    # Team and position information
    team: str = Field(..., description="Team abbreviation")
    position: str = Field(..., description="Player's position")
    depth_chart_position: Optional[str] = Field(None, description="Depth chart position")
    ngs_position: Optional[str] = Field(None, description="Next Gen Stats position")
    
    # Jersey and status
    jersey_number: Optional[float] = Field(None, description="Player's jersey number")
    status: Optional[str] = Field(None, description="Player status (ACT, SUS, etc.)")
    status_description_abbr: Optional[str] = Field(None, description="Status abbreviation")
    game_type: Optional[str] = Field(None, description="Game type (REG, POST, PRE)")
    
    # Career information
    years_exp: Optional[int] = Field(None, description="Years of experience")
    entry_year: Optional[int] = Field(None, description="Entry year to NFL")
    rookie_year: Optional[float] = Field(None, description="Rookie year")
    college: Optional[str] = Field(None, description="College attended")
    
    # Draft information
    draft_number: Optional[float] = Field(None, description="Draft number")
    draft_club: Optional[str] = Field(None, description="Drafting team")
    
    # Media
    headshot_url: Optional[str] = Field(None, description="Headshot URL")


class PlayerWeekRoster(PlayerWeekRosterBase, table=True):
    """Weekly roster information for players from playerweekroster table.
    
    This table tracks player roster status on a weekly basis.
    """
    __tablename__ = "playerweekroster"
    
    # Table constraints and indexes
    __table_args__: ClassVar[Tuple] = (
        # Ensure we don't have duplicate entries for the same player/season/week
        UniqueConstraint(
            'player_id', 'season', 'week', 
            name='uix_player_season_week_roster'
        ),
        # Indexes for common query patterns
        Index('ix_roster_team_season_week', 'team', 'season', 'week'),
        Index('ix_roster_player_season', 'player_id', 'season'),
        Index('ix_roster_position_season_week', 'position', 'season', 'week'),
    )
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="When this roster entry was created"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False,
        description="When this roster entry was last updated"
    )
    
    # Relationships
    player: "Player" = Relationship(
        back_populates="roster_entries",
        sa_relationship_kwargs={"lazy": "selectin"}
    )