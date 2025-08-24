from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, Numeric

class BettingOddsBase(SQLModel):
    game_id: int = Field(foreign_key="game.id", index=True)
    bet_type: str = Field(max_length=50)
    line: Optional[str] = None
    odds: Optional[str] = None
    book: Optional[str] = Field(max_length=100)

class BettingOdds(BettingOddsBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PlayerPropBase(SQLModel):
    player_id: int = Field(foreign_key="player.id", index=True)
    game_id: int = Field(foreign_key="game.id", index=True)
    prop_type: str = Field(max_length=100)
    line: Optional[str] = None
    book: Optional[str] = Field(max_length=100)

class PlayerProp(PlayerPropBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    over_odds: Optional[str] = None
    under_odds: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# API schemas
class BettingOddsCreate(BettingOddsBase):
    pass

class BettingOddsRead(BettingOddsBase):
    id: int
    updated_at: datetime

class PlayerPropCreate(PlayerPropBase):
    pass

class PlayerPropRead(PlayerPropBase):
    id: int
    over_odds: Optional[str] = None
    under_odds: Optional[str] = None
    updated_at: datetime
