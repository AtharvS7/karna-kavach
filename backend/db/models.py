"""
Database models for attack taxonomy, transactions, and metrics.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from db.database import Base


class Attack(Base):
    """Attack taxonomy model."""
    __tablename__ = "attacks"

    id = Column(Integer, primary_key=True, index=True)
    attack_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    genai_amplification = Column(Text, nullable=False)
    attack_steps = Column(JSON, nullable=False)
    target_channel = Column(String(100), nullable=False)
    detection_challenges = Column(JSON, nullable=False)
    transaction_features = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Transaction(Base):
    """Synthetic transaction model."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    card_number = Column(String(19), nullable=False)
    merchant_name = Column(String(255), nullable=False)
    merchant_category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    timestamp = Column(DateTime(timezone=True), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    country = Column(String(100), nullable=False)
    is_fraud = Column(Boolean, nullable=False, default=False)
    attack_id = Column(String(100), nullable=True)
    fraud_probability = Column(Float, nullable=True)
    features = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelMetric(Base):
    """Model performance metrics."""
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    dataset_type = Column(String(50), nullable=False)  # train, test, validation
    iteration = Column(Integer, default=0)
    meta_data = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
