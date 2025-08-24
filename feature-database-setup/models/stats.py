from datetime import datetime, timezone
from typing import Optional, Dict, List, ClassVar, Tuple
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, ForeignKey, UniqueConstraint
from sqlalchemy import String, Index
from pydantic import validator, HttpUrl
class PlayerWeekStatsBase(SQLModel):
    """Base model for weekly player statistics.
    
    This model represents the core statistics for a player in a given week.
    All numeric fields are initialized to 0 by default.
    """
    # Core identifiers
    player_id: str = Field(foreign_key="player.player_id", index=True, description="Player identifier")
    player_name: str = Field(description="Player's full name")
    player_display_name: Optional[str] = Field(default=None, description="Player's display name")
    position: str = Field(description="Player's position")
    position_group: Optional[str] = Field(default=None, description="Player's position group")
    recent_team: Optional[str] = Field(default=None, description="Most recent team")
    opponent_team: Optional[str] = Field(default=None, description="Opponent team")
    season: int = Field(ge=1920, description="NFL season year")
    week: int = Field(ge=1, le=22, description="Week of the season")
    season_type: str = Field(default="REG", description="Type of season (PRE/REG/POST)")
    headshot_url: Optional[str] = Field(default=None, sa_type=String(500), description="URL to player's headshot")
    
    @validator('headshot_url', pre=True)
    def convert_http_url_to_str(cls, v):
        if v is None or isinstance(v, str):
            return v
        return str(v)
    
    # Passing statistics
    completions: int = 0
    attempts: int = 0
    passing_yards: float = 0.0
    passing_tds: int = 0
    interceptions: float = 0.0
    sacks: float = 0.0
    sack_yards: float = 0.0
    sack_fumbles: int = 0
    sack_fumbles_lost: int = 0
    passing_air_yards: float = 0.0
    passing_yards_after_catch: float = 0.0
    passing_first_downs: float = 0.0
    passing_epa: float = 0.0
    passing_2pt_conversions: int = 0
    pacr: float = 0.0  # Passing Air Conversion Ratio
    dakota: float = 0.0  # Defense-adjusted yards above replacement
    
    # Rushing statistics
    carries: int = 0
    rushing_yards: float = 0.0
    rushing_tds: int = 0
    rushing_fumbles: float = 0.0
    rushing_fumbles_lost: float = 0.0
    rushing_first_downs: float = 0.0
    rushing_epa: float = 0.0
    rushing_2pt_conversions: int = 0
    
    # Receiving statistics
    receptions: int = 0
    targets: int = 0
    receiving_yards: float = 0.0
    receiving_tds: int = 0
    receiving_fumbles: float = 0.0
    receiving_fumbles_lost: float = 0.0
    receiving_air_yards: float = 0.0
    receiving_yards_after_catch: float = 0.0
    receiving_first_downs: float = 0.0
    receiving_epa: float = 0.0
    receiving_2pt_conversions: int = 0
    
    # Advanced metrics
    racr: float = 0.0  # Receiver Air Conversion Ratio
    target_share: float = 0.0
    air_yards_share: float = 0.0
    wopr: float = 0.0  # Weighted Opportunity Rating
    
    # Special teams
    special_teams_tds: float = 0.0
    
    # Fantasy points
    fantasy_points: float = 0.0
    fantasy_points_ppr: float = 0.0
    
    # Metadata
    source: str = "nfl_data_py"  # Data source (nfl_data_py as per requirements)
    source_id: Optional[str] = None  # External ID from source
    is_official: bool = False  # Whether these are official stats
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
class PlayerWeekStats(PlayerWeekStatsBase, table=True):
    """Weekly statistics for NFL players.
    
    This table stores detailed weekly statistics for each player, including
    passing, rushing, receiving, and special teams performance.
    """
    __tablename__ = "player_week_stats"
    
    # Table constraints and indexes
    __table_args__: ClassVar[Tuple] = (
        # Ensure we don't have duplicate entries for the same player/week/source
        UniqueConstraint('player_id', 'season', 'week', 'source', 
                        name='uix_player_season_week_source'),
        # Indexes for common query patterns
        Index('ix_pws_player_season_week', 'player_id', 'season', 'week'),
        Index('ix_pws_team_week', 'recent_team', 'week'),
        Index('ix_pws_season_week', 'season', 'week'),
    )
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False
    )
    
    # Relationships
    player: "Player" = Relationship(back_populates="week_stats")
    
    # Helper methods
    def total_touchdowns(self) -> int:
        """Calculate total touchdowns (passing + rushing + receiving)."""
        return self.passing_tds + self.rushing_tds + self.receiving_tds
    
    def total_yards(self) -> float:
        """Calculate total yards from scrimmage."""
        return self.passing_yards + self.rushing_yards + self.receiving_yards
    
    def total_touches(self) -> int:
        """Calculate total touches (rushes + receptions)."""
        return self.carries + self.receptions

class PlayerWeekStatsCreate(PlayerWeekStatsBase):
    """Schema for creating a new player week stats record."""
    pass


class PlayerWeekStatsUpdate(SQLModel):
    """Schema for updating an existing player week stats record."""
    is_official: Optional[bool] = None
    last_updated: Optional[datetime] = None

class PlayerWeekPointsBase(SQLModel):
    """Base model for fantasy points from the NFL_Data_Py package.
    
    This model stores precomputed fantasy points that come directly from the data source.
    No calculations are performed here as the points are provided by the nfl_data_py package.
    """
    # Core identifiers
    player_id: str = Field(foreign_key="player.player_id", index=True, description="Player identifier")
    season: int = Field(ge=1920, description="NFL season year")
    week: int = Field(ge=1, le=22, description="Week of the season")
    
    # Fantasy points (provided by nfl_data_py)
    fantasy_points: float = 0.0  # Standard scoring (non-PPR)
    fantasy_points_ppr: float = 0.0  # Full PPR
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False
    )

class PlayerWeekPoints(PlayerWeekPointsBase, table=True):
    """Weekly fantasy points for players.
    
    This table stores precomputed fantasy points that come directly from the
    nfl_data_py package. No calculations are performed here as the points
    are provided by the data source.
    """
    __tablename__ = "player_week_points"
    
    # Table constraints and indexes
    __table_args__: ClassVar[Tuple] = (
        # Ensure we don't have duplicate entries for the same player/week
        UniqueConstraint('player_id', 'season', 'week', 
                        name='uix_points_player_season_week'),
        # Indexes for common query patterns
        Index('ix_pwp_player_season_week', 'player_id', 'season', 'week'),
        Index('ix_pwp_season_week_scoring', 'season', 'week', 'fantasy_points_ppr'),
    )
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    player: "Player" = Relationship(back_populates="week_points")