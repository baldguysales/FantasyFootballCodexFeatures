"""
Social Media Injury models for the NFL fantasy football application.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from .base import Base, BaseModel

if TYPE_CHECKING:
    from .teams_players import Player, Team

class SocialMediaInjury(Base, BaseModel):
    """Model for injury reports from social media sources."""
    
    __tablename__ = "social_media_injury"
    
    # Primary key - Twitter tweet ID
    tweet_id = Column(BigInteger, primary_key=True)
    
    # Tweet metadata
    author_name = Column(String(100), nullable=False)
    author_username = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False)
    tweet_text = Column(Text, nullable=False)
    tweet_url = Column(String(500))
    
    # Extracted injury information
    player_name = Column(String(100))  # Raw extracted name
    team_abbr = Column(String(3))      # Raw extracted team abbreviation
    injury_status = Column(String(50))
    body_part = Column(String(50))
    timeline = Column(String(100))
    confidence_score = Column(Integer, default=0)
    
    # Foreign keys to link with existing tables
    player_id = Column(String(50), ForeignKey('player.gsis_id'), nullable=True)
    team_abbr = Column(String(10), ForeignKey('team.team_abbr'), nullable=True)
    
    # Engagement metrics
    retweet_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    
    # Processing metadata
    scraped_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    processed_at = Column(DateTime, nullable=True)
    is_verified = Column(String(20), default='unverified')  # unverified, verified, false_positive
    
    # Relationships
    player = relationship("Player", back_populates="social_media_injuries", foreign_keys=[player_id])
    team = relationship("Team", back_populates="social_media_injuries", foreign_keys=[team_abbr])
    
    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            'tweet_id': str(self.tweet_id),
            'author_name': self.author_name,
            'author_username': self.author_username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tweet_text': self.tweet_text,
            'tweet_url': self.tweet_url,
            'player_name': self.player_name,
            'team_abbr': self.team_abbr,
            'injury_status': self.injury_status,
            'body_part': self.body_part,
            'timeline': self.timeline,
            'confidence_score': self.confidence_score,
            'is_verified': self.is_verified,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'player_id': self.player_id,
            'team_id': self.team_id
        }


class SocialMediaInjuryMatch(Base, BaseModel):
    """Model to track manual matches between social media reports and players."""
    
    __tablename__ = "social_media_injury_matches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(BigInteger, ForeignKey('social_media_injury.tweet_id'), nullable=False)
    player_id = Column(String(50), ForeignKey('player.player_id'), nullable=False)
    match_confidence = Column(Float, default=1.0)
    match_method = Column(String(50), default='manual')
    matched_by = Column(String(100))
    matched_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    
    # Relationships
    injury_report = relationship("SocialMediaInjury", foreign_keys=[tweet_id])
    player = relationship("Player", foreign_keys=[player_id])
    
    def __repr__(self):
        return f"<SocialMediaInjuryMatch(tweet_id={self.tweet_id}, player_id='{self.player_id}', method='{self.match_method}')>"