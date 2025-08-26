"""
SQLModel definitions for betting-related tables.
Updated to match the comprehensive betting database schema.
"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Text, Index, UniqueConstraint
from enum import Enum


class BettingMarketType(str, Enum):
    """Enum for betting market types from The Odds API"""
    H2H = "h2h"  # Head to head / moneyline
    SPREADS = "spreads"  # Point spreads
    TOTALS = "totals"  # Over/under totals
    H2H_LAY = "h2h_lay"  # Lay betting for exchanges
    OUTRIGHTS = "outrights"  # Futures markets
    # Player props
    PLAYER_PASS_TDS = "player_pass_tds"
    PLAYER_PASS_YARDS = "player_pass_yards"
    PLAYER_RUSH_YARDS = "player_rush_yards"
    PLAYER_RECEIVING_YARDS = "player_receiving_yards"
    PLAYER_ANYTIME_TD = "player_anytime_td"
    PLAYER_FIRST_TD = "player_first_td"
    PLAYER_LAST_TD = "player_last_td"
    # Alternate markets
    ALTERNATE_SPREADS = "alternate_spreads"
    ALTERNATE_TOTALS = "alternate_totals"
    # Period markets
    H2H_Q1 = "h2h_q1"
    H2H_Q2 = "h2h_q2"
    H2H_H1 = "h2h_h1"  # First half
    SPREADS_Q1 = "spreads_q1"
    TOTALS_Q1 = "totals_q1"


class OddsFormat(str, Enum):
    """Format of odds values"""
    AMERICAN = "american"
    DECIMAL = "decimal"


class BookmakerRegion(str, Enum):
    """Bookmaker regions from The Odds API"""
    US = "us"
    US2 = "us2"
    UK = "uk"
    AU = "au"
    EU = "eu"


# ========== CORE TABLES ==========

class BookmakerBase(SQLModel):
    """Base model for bookmakers/sportsbooks"""
    key: str = Field(max_length=50, unique=True, index=True)  # e.g., "fanduel", "draftkings"
    title: str = Field(max_length=100)  # Display name
    region: BookmakerRegion
    is_active: bool = Field(default=True)
    has_player_props: bool = Field(default=False)
    has_live_betting: bool = Field(default=False)


class Bookmaker(BookmakerBase, table=True):
    """Bookmaker/sportsbook information"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    game_odds: List["GameOdds"] = Relationship(back_populates="bookmaker")


class NFLGameBase(SQLModel):
    """Complete NFL game information for betting purposes"""
    # The Odds API identifiers
    odds_api_id: str = Field(max_length=100, unique=True, index=True)  # The Odds API game ID
    sport_key: str = Field(default="americanfootball_nfl", max_length=50)
    sport_title: str = Field(default="NFL", max_length=50)
    
    # Game details
    season: int = Field(ge=1920, description="NFL season year")
    week: Optional[int] = Field(ge=1, le=22, description="Week of season", nullable=True)
    season_type: str = Field(default="REG", max_length=10)  # REG, POST, PRE
    game_type: Optional[str] = Field(max_length=10, nullable=True)
    
    # Game timing
    commence_time: datetime = Field(index=True, description="Game start time")
    game_date: Optional[datetime] = Field(nullable=True, description="Game date")
    
    # Teams (store as strings to match The Odds API format)
    home_team: str = Field(max_length=100, index=True, description="Home team name")
    away_team: str = Field(max_length=100, index=True, description="Away team name")
    home_team_abbr: Optional[str] = Field(max_length=5, nullable=True)
    away_team_abbr: Optional[str] = Field(max_length=5, nullable=True)
    
    # Game status
    is_completed: bool = Field(default=False)
    is_live: bool = Field(default=False)
    game_status: Optional[str] = Field(max_length=20, nullable=True)
    
    # Betting-specific fields
    last_odds_update: Optional[datetime] = None
    has_live_odds: bool = Field(default=False)
    has_player_props: bool = Field(default=False)
    
    # Scores (if available)
    home_score: Optional[int] = Field(nullable=True)
    away_score: Optional[int] = Field(nullable=True)


class NFLGame(NFLGameBase, table=True):
    """Complete NFL game information for betting purposes"""
    __tablename__ = "nfl_game"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    game_odds: List["GameOdds"] = Relationship(back_populates="nfl_game")
    player_props: List["PlayerProp"] = Relationship(back_populates="nfl_game")
    odds_snapshots: List["OddsSnapshot"] = Relationship(back_populates="nfl_game")
    odds_movements: List["OddsMovement"] = Relationship(back_populates="nfl_game")
    consensus_odds: List["ConsensusOdds"] = Relationship(back_populates="nfl_game")


class GameOddsBase(SQLModel):
    """Base model for game-level odds data"""
    nfl_game_id: int = Field(foreign_key="nfl_game.id", index=True)
    bookmaker_id: int = Field(foreign_key="bookmaker.id", index=True)
    market_type: BettingMarketType = Field(index=True)
    odds_format: OddsFormat = Field(default=OddsFormat.AMERICAN)
    bookmaker_last_update: datetime  # When bookmaker last updated these odds
    # Store raw market data as JSON for flexibility with different market types
    raw_market_data: Optional[str] = Field(sa_column=Text, nullable=True)


class GameOdds(GameOddsBase, table=True):
    """Game-level odds for different markets"""
    __tablename__ = "gameodds"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    nfl_game: NFLGame = Relationship(back_populates="game_odds")
    bookmaker: Bookmaker = Relationship(back_populates="game_odds")
    outcomes: List["BettingOutcome"] = Relationship(back_populates="game_odds")


class BettingOutcomeBase(SQLModel):
    """Individual betting outcome/line"""
    game_odds_id: int = Field(foreign_key="gameodds.id", index=True)
    name: str = Field(max_length=100)  # Team name, "Over", "Under", etc.
    price: Optional[str] = Field(max_length=20)  # Odds value (can be +150, -200, 2.50, etc.)
    point: Optional[float] = None  # Point spread or total value
    # For player props - links to your existing Player table
    description: Optional[str] = Field(max_length=200)  # Player name for player props
    player_id: Optional[str] = Field(foreign_key="player.gsis_id", nullable=True)


class BettingOutcome(BettingOutcomeBase, table=True):
    """Individual betting outcomes within a market"""
    __tablename__ = "bettingoutcome"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    game_odds: GameOdds = Relationship(back_populates="outcomes")


# ========== PLAYER PROPS SPECIALIZED TABLES ==========

class PlayerPropTypeBase(SQLModel):
    """Types of player proposition bets"""
    key: str = Field(max_length=50, unique=True)  # e.g., "player_pass_tds"
    display_name: str = Field(max_length=100)  # e.g., "Passing Touchdowns"
    category: str = Field(max_length=50)  # "passing", "rushing", "receiving", "defense"
    stat_type: str = Field(max_length=50)  # "yards", "touchdowns", "receptions", etc.
    is_active: bool = Field(default=True)


class PlayerPropType(PlayerPropTypeBase, table=True):
    """Player proposition bet types"""
    __tablename__ = "playerproptype"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    player_props: List["PlayerProp"] = Relationship(back_populates="prop_type")


class PlayerPropBase(SQLModel):
    """Player proposition bets"""
    nfl_game_id: int = Field(foreign_key="nfl_game.id", index=True)
    player_id: str = Field(foreign_key="player.gsis_id", index=True)  # Links to your Player table
    bookmaker_id: int = Field(foreign_key="bookmaker.id", index=True)
    prop_type_id: int = Field(foreign_key="playerproptype.id", index=True)
    line: Optional[float] = None  # The prop line (e.g., 250.5 passing yards)
    over_price: Optional[str] = Field(max_length=20)  # Odds for over
    under_price: Optional[str] = Field(max_length=20)  # Odds for under
    # Alternative lines (DraftKings often has multiple lines for same prop)
    is_main_line: bool = Field(default=True)  # False for alternate lines
    bookmaker_last_update: datetime


class PlayerProp(PlayerPropBase, table=True):
    """Player proposition bets"""
    __tablename__ = "playerprop"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    nfl_game: NFLGame = Relationship(back_populates="player_props")
    prop_type: PlayerPropType = Relationship(back_populates="player_props")


# ========== HISTORICAL TRACKING ==========

class OddsSnapshotBase(SQLModel):
    """Historical odds snapshots for analysis and line movement tracking"""
    nfl_game_id: int = Field(foreign_key="nfl_game.id", index=True)
    snapshot_timestamp: datetime = Field(index=True)  # When snapshot was taken
    api_timestamp: Optional[datetime] = None  # Timestamp from The Odds API response
    source: str = Field(default="odds_api", max_length=50)
    # Store complete API response for historical analysis
    raw_odds_data: str = Field(sa_column=Text)  # JSON of full API response
    request_cost: Optional[int] = None  # API request cost for this snapshot


class OddsSnapshot(OddsSnapshotBase, table=True):
    """Historical odds snapshots for trend analysis"""
    __tablename__ = "oddssnapshot"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    nfl_game: NFLGame = Relationship(back_populates="odds_snapshots")


class OddsMovementBase(SQLModel):
    """Track odds movements over time for line shopping and trend analysis"""
    nfl_game_id: int = Field(foreign_key="nfl_game.id", index=True)
    bookmaker_id: int = Field(foreign_key="bookmaker.id", index=True)
    market_type: BettingMarketType = Field(index=True)
    outcome_name: str = Field(max_length=100)  # Team name, "Over", "Under", player name
    # Previous values
    previous_price: Optional[str] = Field(max_length=20)
    previous_point: Optional[float] = None
    # New values
    new_price: Optional[str] = Field(max_length=20)
    new_point: Optional[float] = None
    # Movement calculations
    price_movement_cents: Optional[int] = None  # Movement in cents (for American odds)
    point_movement: Optional[float] = None  # Point spread/total movement
    movement_direction: Optional[str] = Field(max_length=10)  # "up", "down", "neutral"
    movement_timestamp: datetime = Field(index=True)


class OddsMovement(OddsMovementBase, table=True):
    """Historical odds movements for trend analysis and alerts"""
    __tablename__ = "oddsmovement"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    nfl_game: NFLGame = Relationship(back_populates="odds_movements")


class ConsensusOddsBase(SQLModel):
    """Consensus/average odds across bookmakers for line shopping"""
    nfl_game_id: int = Field(foreign_key="nfl_game.id", index=True)
    market_type: BettingMarketType = Field(index=True)
    outcome_name: str = Field(max_length=100)
    # Consensus calculations
    avg_american_odds: Optional[float] = None
    median_american_odds: Optional[float] = None
    best_odds: Optional[str] = Field(max_length=20)  # Best odds available
    best_odds_bookmaker: Optional[str] = Field(max_length=50)  # Which book has best odds
    worst_odds: Optional[str] = Field(max_length=20)  # Worst odds available
    # For spreads and totals
    consensus_point: Optional[float] = None  # Most common point spread/total
    point_spread_range: Optional[float] = None  # Difference between highest/lowest line
    # Market depth
    bookmaker_count: int = Field(default=0)  # Number of books offering this market
    total_handle_estimate: Optional[float] = None  # Estimated betting volume
    last_calculated: datetime


class ConsensusOdds(ConsensusOddsBase, table=True):
    """Consensus odds calculations for line shopping and market analysis"""
    __tablename__ = "consensusodds"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    nfl_game: NFLGame = Relationship(back_populates="consensus_odds")


# ========== API SCHEMAS FOR FRONTEND/API CONSUMPTION ==========

class BookmakerRead(BookmakerBase):
    id: int
    created_at: datetime
    updated_at: datetime


class NFLGameRead(NFLGameBase):
    id: int
    created_at: datetime
    updated_at: datetime


class GameOddsRead(GameOddsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    bookmaker: BookmakerRead
    outcomes: List["BettingOutcomeRead"]


class BettingOutcomeRead(BettingOutcomeBase):
    id: int
    created_at: datetime


class PlayerPropRead(PlayerPropBase):
    id: int
    created_at: datetime
    updated_at: datetime
    prop_type: PlayerPropType


class ConsensusOddsRead(ConsensusOddsBase):
    id: int


class OddsMovementRead(OddsMovementBase):
    id: int


# ========== UTILITY FUNCTIONS ==========

def get_market_display_name(market_type: BettingMarketType) -> str:
    """Convert market type to display name"""
    market_names = {
        BettingMarketType.H2H: "Moneyline",
        BettingMarketType.SPREADS: "Point Spread", 
        BettingMarketType.TOTALS: "Over/Under",
        BettingMarketType.PLAYER_PASS_TDS: "Passing Touchdowns",
        BettingMarketType.PLAYER_PASS_YARDS: "Passing Yards",
        BettingMarketType.PLAYER_RUSH_YARDS: "Rushing Yards",
        BettingMarketType.PLAYER_RECEIVING_YARDS: "Receiving Yards",
        BettingMarketType.PLAYER_ANYTIME_TD: "Anytime Touchdown",
        # Add more mappings as needed
    }
    return market_names.get(market_type, market_type.value.replace("_", " ").title())


def convert_odds_format(price: str, from_format: OddsFormat, to_format: OddsFormat) -> str:
    """Convert between American and decimal odds formats"""
    if from_format == to_format:
        return price
        
    if from_format == OddsFormat.AMERICAN and to_format == OddsFormat.DECIMAL:
        american_odds = int(price)
        if american_odds > 0:
            decimal = (american_odds / 100) + 1
        else:
            decimal = (100 / abs(american_odds)) + 1
        return f"{decimal:.2f}"
    
    elif from_format == OddsFormat.DECIMAL and to_format == OddsFormat.AMERICAN:
        decimal_odds = float(price)
        if decimal_odds >= 2.0:
            american = int((decimal_odds - 1) * 100)
            return f"+{american}"
        else:
            american = int(-100 / (decimal_odds - 1))
            return str(american)
    
    return price
