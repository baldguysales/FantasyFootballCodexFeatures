from datetime import datetime, timezone
from typing import Optional, List, ClassVar, Tuple
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint, Index
from pydantic import validator

class WeeklyRosterBase(SQLModel):
    """Base model for weekly roster information.
    
    This model tracks a player's roster status for a specific week and game type.
    """
    player_id: str = Field(
        foreign_key="player.player_id", 
        index=True,
        description="Reference to the player"
    )
    team: str = Field(
        ...,
        description="Team abbreviation for this roster entry"
    )
    position: str = Field(
        ...,
        description="Player's position for this roster entry"
    )
    depth_chart_pos: Optional[str] = Field(
        None,
        description="Player's depth chart position for this week"
    )
    jersey_number: Optional[int] = Field(
        None,
        ge=0,
        le=99,
        description="Jersey number for this week"
    )
    status: Optional[str] = Field(
        None,
        description="Player's status (e.g., ACT, INJ, SUS, etc.)"
    )
    status_abbr: Optional[str] = Field(
        None,
        description="Abbreviated status description"
    )
    game_type: Optional[str] = Field(
        None,
        description="Type of game (REG, POST, PRE)"
    )
    ngs_position: Optional[str] = Field(
        None,
        description="Next Gen Stats position for this week"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this roster entry was last updated"
    )


class WeeklyRoster(WeeklyRosterBase, table=True):
    """Weekly roster information for players.
    
    This table tracks player roster status on a weekly basis, including
    position, status, and other roster-specific information.
    """
    __tablename__ = "weekly_roster"
    
    # Table constraints and indexes
    __table_args__: ClassVar[Tuple] = (
        # Ensure we don't have duplicate entries for the same player/team/game type
        UniqueConstraint(
            'player_id', 'team', 'game_type', 
            name='uix_player_team_game_type'
        ),
        # Indexes for common query patterns
        Index('ix_weekly_roster_team_week', 'team', 'game_type'),
        Index('ix_weekly_roster_player_week', 'player_id', 'game_type'),
    )
    
    # Primary key
    id: Optional[int] = Field(
        default=None, 
        primary_key=True,
        description="Primary key"
    )
    
    # Timestamp
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="When this roster entry was created"
    )
    
    # Relationships
    player: "Player" = Relationship(
        back_populates="roster_entries",
        sa_relationship_kwargs={"lazy": "selectin"}
    )