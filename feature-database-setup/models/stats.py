from datetime import datetime, timezone
from typing import Optional, Dict, List, ClassVar, Tuple
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, ForeignKey, UniqueConstraint
from sqlalchemy import String, Index, select, or_, and_, desc  # Add the SQL functions if you want to use the helper functions I provided
from pydantic import validator, HttpUrl
class PlayerWeekStatsBase(SQLModel):
    """Base model for weekly player statistics.
    
    This model represents the core statistics for a player in a given week.
    All numeric fields are initialized to 0 by default.
    """
    # Core identifiers
    player_id: str = Field(foreign_key="player.gsis_id", index=True, description="Player identifier")
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
    player_id: str = Field(foreign_key="player.gsis_id", index=True, description="Player identifier")
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

class ScheduleBase(SQLModel):
    """Base model for NFL game schedule and results data.
    
    This model stores historical game information for performance analysis,
    including scores, betting lines, and game metadata.
    """
    # Game identification
    game_id: str = Field(primary_key=True, description="Unique game identifier")
    old_game_id: Optional[int] = Field(None, description="Legacy game ID")
    gsis: Optional[float] = Field(None, description="GSIS game identifier")
    pff: Optional[float] = Field(None, description="Pro Football Focus game ID")
    espn: Optional[float] = Field(None, description="ESPN game ID")
    ftn: Optional[float] = Field(None, description="FantasyPros game ID")
    pfr: Optional[str] = Field(None, description="Pro Football Reference game ID")
    nfl_detail_id: Optional[str] = Field(None, description="NFL detail ID")
    
    # Game timing and details
    season: int = Field(ge=1920, description="NFL season year")
    week: int = Field(ge=1, le=22, description="Week of the season")
    game_type: Optional[str] = Field(None, description="Game type (REG, POST, PRE)")
    gameday: Optional[str] = Field(None, description="Game day")
    weekday: Optional[str] = Field(None, description="Day of the week")
    gametime: Optional[str] = Field(None, description="Game time")
    location: Optional[str] = Field(None, description="Game location")
    
    # Teams
    home_team: str = Field(..., description="Home team abbreviation")
    away_team: str = Field(..., description="Away team abbreviation")
    
    # Game results
    home_score: Optional[float] = Field(None, description="Home team final score")
    away_score: Optional[float] = Field(None, description="Away team final score")
    result: Optional[float] = Field(None, description="Game result from home team perspective")
    overtime: Optional[float] = Field(None, description="Overtime indicator")
    
    # Betting information
    total: Optional[float] = Field(None, description="Total points line")
    away_moneyline: Optional[float] = Field(None, description="Away team moneyline")
    
    # Rest days
    home_rest: Optional[int] = Field(None, description="Days of rest for home team")
    away_rest: Optional[int] = Field(None, description="Days of rest for away team")


class Schedule(ScheduleBase, table=True):
    """NFL game schedule and historical results.
    
    This table stores comprehensive game information for historical analysis
    and player performance evaluation against specific teams.
    """
    __tablename__ = "schedule"
    
    # Table constraints and indexes
    __table_args__: ClassVar[Tuple] = (
        # Ensure unique games per season/week/teams combination
        UniqueConstraint('season', 'week', 'home_team', 'away_team', 
                        name='uq_schedule_season_week_teams'),
        # Indexes for common query patterns
        Index('ix_schedule_season_week', 'season', 'week'),
        Index('ix_schedule_home_team_season', 'home_team', 'season'),
        Index('ix_schedule_away_team_season', 'away_team', 'season'),
        Index('ix_schedule_teams', 'home_team', 'away_team'),
        Index('ix_schedule_gameday', 'gameday'),
    )
    
    # Timestamps for tracking
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this schedule entry was created"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        description="When this schedule entry was last updated"
    )
    
    # Helper methods for analysis
    def get_opponent(self, team: str) -> Optional[str]:
        """Get the opponent team for a given team."""
        if team == self.home_team:
            return self.away_team
        elif team == self.away_team:
            return self.home_team
        return None
    
    def is_home_game(self, team: str) -> Optional[bool]:
        """Check if the game was at home for the given team."""
        if team == self.home_team:
            return True
        elif team == self.away_team:
            return False
        return None
    
    def get_team_score(self, team: str) -> Optional[float]:
        """Get the score for a specific team."""
        if team == self.home_team:
            return self.home_score
        elif team == self.away_team:
            return self.away_score
        return None
    
    def get_opponent_score(self, team: str) -> Optional[float]:
        """Get the opponent's score for a given team."""
        if team == self.home_team:
            return self.away_score
        elif team == self.away_team:
            return self.home_score
        return None
    
    def did_team_win(self, team: str) -> Optional[bool]:
        """Check if the given team won the game."""
        team_score = self.get_team_score(team)
        opponent_score = self.get_opponent_score(team)
        
        if team_score is None or opponent_score is None:
            return None
            
        return team_score > opponent_score
    
    def get_point_differential(self, team: str) -> Optional[float]:
        """Get point differential for a team (positive = won by X, negative = lost by X)."""
        team_score = self.get_team_score(team)
        opponent_score = self.get_opponent_score(team)
        
        if team_score is None or opponent_score is None:
            return None
            
        return team_score - opponent_score


# API schemas for frontend/API consumption
class ScheduleRead(ScheduleBase):
    """Schema for reading schedule data via API"""
    created_at: datetime
    updated_at: datetime


class ScheduleCreate(ScheduleBase):
    """Schema for creating new schedule entries"""
    pass


class ScheduleUpdate(SQLModel):
    """Schema for updating schedule entries"""
    home_score: Optional[float] = None
    away_score: Optional[float] = None
    result: Optional[float] = None
    overtime: Optional[float] = None
    total: Optional[float] = None
    away_moneyline: Optional[float] = None


# Helper functions for schedule analysis
def get_team_schedule(session, team: str, season: int, week: Optional[int] = None):
    """Get schedule for a specific team and season."""
    from sqlalchemy import select, or_
    
    query = select(Schedule).where(
        or_(Schedule.home_team == team, Schedule.away_team == team),
        Schedule.season == season
    )
    
    if week:
        query = query.where(Schedule.week == week)
    
    return session.execute(query)


def get_head_to_head_history(session, team1: str, team2: str, seasons: Optional[int] = 5):
    """Get head-to-head history between two teams."""
    from sqlalchemy import select, or_, and_, desc
    
    query = select(Schedule).where(
        or_(
            and_(Schedule.home_team == team1, Schedule.away_team == team2),
            and_(Schedule.home_team == team2, Schedule.away_team == team1)
        )
    )
    
    if seasons:
        from datetime import datetime
        cutoff_season = datetime.now().year - seasons
        query = query.where(Schedule.season >= cutoff_season)
    
    query = query.order_by(desc(Schedule.season), desc(Schedule.week))
    
    return session.execute(query)


def get_team_performance_vs_opponent(session, team: str, opponent: str, seasons: int = 3):
    """Get detailed performance analysis for a team against a specific opponent."""
    from sqlalchemy import select, or_, and_
    
    query = select(Schedule).where(
        or_(
            and_(Schedule.home_team == team, Schedule.away_team == opponent),
            and_(Schedule.away_team == team, Schedule.home_team == opponent)
        ),
        Schedule.season >= (datetime.now().year - seasons),
        Schedule.home_score.isnot(None),  # Only completed games
        Schedule.away_score.isnot(None)
    ).order_by(Schedule.season.desc(), Schedule.week.desc())
    
    games = session.execute(query).scalars().all()
    
    # Calculate performance metrics
    wins = 0
    total_games = len(games)
    total_points_for = 0
    total_points_against = 0
    home_games = 0
    home_wins = 0
    
    for game in games:
        is_home = game.is_home_game(team)
        team_score = game.get_team_score(team)
        opponent_score = game.get_opponent_score(team)
        
        if game.did_team_win(team):
            wins += 1
            if is_home:
                home_wins += 1
        
        if is_home:
            home_games += 1
            
        total_points_for += team_score
        total_points_against += opponent_score
    
    return {
        "games": games,
        "total_games": total_games,
        "wins": wins,
        "losses": total_games - wins,
        "win_percentage": wins / total_games if total_games > 0 else 0,
        "avg_points_for": total_points_for / total_games if total_games > 0 else 0,
        "avg_points_against": total_points_against / total_games if total_games > 0 else 0,
        "home_record": f"{home_wins}-{home_games - home_wins}" if home_games > 0 else "0-0",
        "away_record": f"{wins - home_wins}-{(total_games - home_games) - (wins - home_wins)}"
    }