from enum import Enum
from typing import Optional
from pydantic import BaseModel

class PlayerPosition(str, Enum):
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"
    K = "K"
    DEF = "DEF"
    FLEX = "FLEX"
    SUPER_FLEX = "SUPER_FLEX"

class Status(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    INJURED = "INJURED"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"
    PRACTICE_SQUAD = "PRACTICE_SQUAD"

class GameStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    FINAL = "FINAL"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"

class Platform(str, Enum):
    ESPN = "ESPN"
    SLEEPER = "SLEEPER"
    YAHOO = "YAHOO"
    NFL = "NFL"
    FANTRAX = "FANTRAX"
    MYFANTASYLEAGUE = "MYFANTASYLEAGUE"

class Conference(str, Enum):
    AFC = "AFC"
    NFC = "NFC"

class Division(str, Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"

class PropType(str, Enum):
    PASSING_YARDS = "PASSING_YARDS"
    PASSING_TDS = "PASSING_TDS"
    PASSING_INTS = "PASSING_INTS"
    RUSHING_YARDS = "RUSHING_YARDS"
    RUSHING_ATTEMPTS = "RUSHING_ATTEMPTS"
    RUSHING_TDS = "RUSHING_TDS"
    RECEIVING_YARDS = "RECEIVING_YARDS"
    RECEPTIONS = "RECEPTIONS"
    RECEIVING_TDS = "RECEIVING_TDS"
    FANTASY_POINTS = "FANTASY_POINTS"

class DecisionType(str, Enum):
    START = "START"
    SIT = "SIT"
    ADD = "ADD"
    DROP = "DROP"
    TRADE = "TRADE"
    WAIVER_ADD = "WAIVER_ADD"
    WAIVER_DROP = "WAIVER_DROP"

class SocialMediaPlatform(str, Enum):
    TWITTER = "TWITTER"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    TIKTOK = "TIKTOK"

class SentimentScore(float, Enum):
    VERY_NEGATIVE = -1.0
    NEGATIVE = -0.5
    NEUTRAL = 0.0
    POSITIVE = 0.5
    VERY_POSITIVE = 1.0

class BetType(str, Enum):
    SPREAD = "SPREAD"
    MONEYLINE = "MONEYLINE"
    TOTAL = "TOTAL"
    PLAYER_PROP = "PLAYER_PROP"
    TEAM_TOTAL = "TEAM_TOTAL"
