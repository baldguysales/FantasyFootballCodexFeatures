from datetime import datetime, timezone
from typing import Optional, List, Dict, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, ForeignKey, Index
from pydantic import validator
from typing import ClassVar, Tuple

from enums import PlayerPosition, Status, Conference, Division

if TYPE_CHECKING:
    from .social_media_injury import SocialMediaInjury

class TeamBase(SQLModel):
    team_abbr: str = Field(primary_key=True, max_length=10, description="Team abbreviation (e.g., 'NE', 'GB')")
    team_name: str = Field(..., description="Official team name")
    team_id: int = Field(..., unique=True, description="NFL's team ID")
    team_nick: Optional[str] = Field(None, description="Team nickname or mascot")
    team_conf: str = Field(..., description="Conference (AFC or NFC)")
    team_division: str = Field(..., description="Division within conference")
    team_color: Optional[str] = Field(None, description="Primary team color")
    team_color2: Optional[str] = Field(None, description="Secondary team color")
    team_color3: Optional[str] = Field(None, description="Tertiary team color")
    team_color4: Optional[str] = Field(None, description="Quaternary team color")
    team_logo_wikipedia: Optional[str] = Field(None, description="URL to team logo on Wikipedia")
    team_logo_espn: Optional[str] = Field(None, description="URL to team logo on ESPN")
    team_wordmark: Optional[str] = Field(None, description="URL to team wordmark")
    team_conference_logo: Optional[str] = Field(None, description="URL to conference logo")
    team_league_logo: Optional[str] = Field(None, description="URL to NFL league logo")
    team_logo_squared: Optional[str] = Field(None, description="URL to squared team logo")

class Team(TeamBase, table=True):
    __tablename__ = "team"
    
    # Relationships
    players: List["Player"] = Relationship(back_populates="team_rel")
    social_media_injuries: List["SocialMediaInjury"] = Relationship(back_populates="team")
    
    # Indexes
    __table_args__ = (
        Index('idx_team_conference', 'team_conf'),
        Index('idx_team_division', 'team_division'),
    )

class PlayerBase(SQLModel):
    """Base model for NFL players with core identification and roster information.
    
    This model aligns with the database schema and includes all fields from the player table.
    """
    # Core identification
    player_id: str = Field(primary_key=True, index=True, description="Primary player identifier (GSIS ID)")
    player_name: str = Field(..., description="Player's full name")
    first_name: Optional[str] = Field(None, description="Player's first name")
    last_name: Optional[str] = Field(None, description="Player's last name")
    team: Optional[str] = Field(None, foreign_key="team.team_abbr", description="Team abbreviation")
    
    # Physical attributes
    height: Optional[float] = Field(None, description="Player's height in inches")
    weight: Optional[int] = Field(None, description="Player's weight in lbs")
    birth_date: Optional[datetime] = Field(None, description="Player's date of birth")
    
    # Team and position information
    position: str = Field(..., description="Player's primary position")
    depth_chart_position: Optional[str] = Field(None, description="Current depth chart position")
    ngs_position: Optional[str] = Field(None, description="Next Gen Stats position")
    
    # Status and game info
    status: Optional[str] = Field(None, description="Current player status (e.g., ACT, SUS, RES, etc.)")
    game_type: Optional[str] = Field(None, description="Type of game (REG, POST, PRE)")
    status_description_abbr: Optional[str] = Field(None, description="Abbreviated status description")
    
    # Player identification numbers
    jersey_number: Optional[float] = Field(None, description="Player's jersey number")
    
    # Career information
    years_exp: Optional[int] = Field(None, description="Years of NFL experience")
    entry_year: Optional[int] = Field(None, description="Year player entered the league")
    rookie_year: Optional[float] = Field(None, description="Player's rookie year")
    college: Optional[str] = Field(None, description="College attended")
    
    # Draft information
    draft_number: Optional[float] = Field(None, description="Draft pick number")
    draft_club: Optional[str] = Field(None, description="Team that drafted the player")
    
    # Age and season context
    age: Optional[float] = Field(None, description="Player's age")
    season: Optional[int] = Field(None, ge=1920, description="Current season year")
    week: Optional[int] = Field(None, ge=1, le=22, description="Current week of the season")
    
    # External IDs and references
    pff_id: Optional[str] = Field(None, index=True, description="Pro Football Focus ID")
    pfr_id: Optional[str] = Field(None, index=True, description="Pro Football Reference ID")
    fantasy_data_id: Optional[str] = Field(None, index=True, description="Fantasy Data ID")
    sleeper_id: Optional[str] = Field(None, index=True, description="Sleeper ID")
    espn_id: Optional[str] = Field(None, index=True, description="ESPN ID")
    sportradar_id: Optional[str] = Field(None, index=True, description="SportRadar ID")
    yahoo_id: Optional[str] = Field(None, index=True, description="Yahoo ID")
    rotowire_id: Optional[str] = Field(None, index=True, description="Rotowire ID")
    esb_id: Optional[str] = Field(None, index=True, description="ESB ID")
    gsis_it_id: Optional[str] = Field(None, index=True, description="GSIS ID")
    smart_id: Optional[str] = Field(None, index=True, description="SMART ID")
    
    # Player media
    headshot_url: Optional[str] = Field(None, description="URL to player's headshot")
    football_name: Optional[str] = Field(None, description="Player's nickname or preferred name")

class Player(PlayerBase, table=True):
    """Player model representing an NFL player with all roster and statistical information."""
    __tablename__ = "player"
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="Timestamp when the record was created"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False,
        description="Timestamp when the record was last updated"
    )
    
    # Relationships
    team_rel: Optional[Team] = Relationship(back_populates="players")
    week_stats: List["PlayerWeekStats"] = Relationship(back_populates="player")
    week_points: List["PlayerWeekPoints"] = Relationship(back_populates="player")
    injury_reports: List["InjuryReport"] = Relationship(back_populates="player")
    social_media_posts: List["SocialMediaPost"] = Relationship(back_populates="player")
    social_media_injuries: List["SocialMediaInjury"] = Relationship(back_populates="player")
    ai_summaries: List["AISummary"] = Relationship(back_populates="player")
    fantasy_rosters: List["FantasyRoster"] = Relationship(back_populates="players")
    props: List["PlayerProp"] = Relationship(back_populates="player")
    decisions: List["UserDecision"] = Relationship(back_populates="player")
    roster_entries: List["WeeklyRoster"] = Relationship(back_populates="player")
    
    # Indexes for better query performance
    __table_args__: ClassVar[Tuple] = (
        # Index on commonly filtered fields
        Index('ix_player_team', 'team_abbr'),
        Index('ix_player_position', 'position'),
        Index('ix_player_season_week', 'season', 'week'),
        # Partial index for active players
        Index('ix_active_players', 'status', postgresql_where="status = 'ACTIVE'"),
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
