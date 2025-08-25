from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, ForeignKey, UniqueConstraint, Float
from pydantic import validator, HttpUrl

from .enums import DecisionType

class UserDecisionBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", index=True)
    player_id: str = Field(foreign_key="player.gsis_id", index=True)
    decision_type: DecisionType
    week: int = Field(ge=1, le=22)
    season: int = Field(ge=1920)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    notes: Optional[str] = None
    metadata_: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    decision_made_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserDecision(UserDecisionBase, table=True):
    __table_args__ = (
        UniqueConstraint('user_id', 'player_id', 'decision_type', 'week', 'season', name='uix_user_decision'),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user: "User" = Relationship(back_populates="decisions")
    player: "Player" = Relationship(back_populates="decisions")
    actual_outcome: Optional["DecisionOutcome"] = Relationship(
        back_populates="decision",
        sa_relationship_kwargs={"uselist": False}
    )

class UserDecisionCreate(UserDecisionBase):
    pass

class UserDecisionUpdate(SQLModel):
    confidence: Optional[float] = None
    notes: Optional[str] = None
    metadata_: Optional[Dict] = None

class DecisionOutcomeBase(SQLModel):
    decision_id: int = Field(foreign_key="userdecision.id", index=True, unique=True)
    was_correct: bool
    actual_points: Optional[float] = None
    projected_points: Optional[float] = None
    variance: Optional[float] = None
    impact_score: Optional[float] = Field(
        default=None,
        description="A score from -1 to 1 indicating how much this decision impacted the user's team"
    )
    notes: Optional[str] = None
    metadata_: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)

class DecisionOutcome(DecisionOutcomeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    decision: UserDecision = Relationship(back_populates="actual_outcome")

class ModelPerformanceBase(SQLModel):
    model_name: str
    model_version: str
    model_type: str  # e.g., 'projection', 'classification', 'regression'
    training_date: datetime
    evaluation_metrics: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    feature_importance: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    test_set_size: int
    train_set_size: int
    cross_validation_scores: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    hyperparameters: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    is_active: bool = True
    notes: Optional[str] = None
    deployed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ModelPerformance(ModelPerformanceBase, table=True):
    __table_args__ = (
        UniqueConstraint('model_name', 'model_version', name='uix_model_name_version'),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrainingRunBase(SQLModel):
    model_name: str
    model_version: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    status: str = "started"  # 'started', 'completed', 'failed'
    dataset_size: Optional[int] = None
    features_used: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    hyperparameters: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    metrics: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    error_message: Optional[str] = None
    training_logs: Optional[str] = None
    metadata_: Dict = Field(default_factory=dict, sa_column=Column(JSON))

class TrainingRun(TrainingRunBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FeatureImportanceBase(SQLModel):
    model_name: str
    model_version: str
    feature_name: str
    importance_score: float
    importance_rank: int
    data_type: str  # 'numerical', 'categorical', 'datetime', etc.
    metadata_: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FeatureImportance(FeatureImportanceBase, table=True):
    __table_args__ = (
        UniqueConstraint('model_name', 'model_version', 'feature_name', name='uix_feature_importance'),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PredictionBase(SQLModel):
    model_name: str
    model_version: str
    entity_type: str  # 'player', 'team', 'game', etc.
    entity_id: int
    prediction_type: str  # 'projection', 'classification', 'regression', etc.
    prediction_value: float
    prediction_confidence: Optional[float] = None
    prediction_interval_lower: Optional[float] = None
    prediction_interval_upper: Optional[float] = None
    context_week: Optional[int] = Field(ge=1, le=22, default=None)
    context_season: Optional[int] = Field(ge=1920, default=None)
    features_used: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    metadata_: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    predicted_at: datetime = Field(default_factory=datetime.utcnow)

class Prediction(PredictionBase, table=True):
    __table_args__ = (
        UniqueConstraint('model_name', 'model_version', 'entity_type', 'entity_id', 
                        'prediction_type', 'context_week', 'context_season', 
                        name='uix_prediction'),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PredictionOutcomeBase(SQLModel):
    prediction_id: int = Field(foreign_key="prediction.id", index=True)
    actual_value: Optional[float] = None
    error: Optional[float] = None
    absolute_error: Optional[float] = None
    squared_error: Optional[float] = None
    was_correct: Optional[bool] = None
    confidence_interval_hit: Optional[bool] = None
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    metadata_: Dict = Field(default_factory=dict, sa_column=Column(JSON))

class PredictionOutcome(PredictionOutcomeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    prediction: Prediction = Relationship()
