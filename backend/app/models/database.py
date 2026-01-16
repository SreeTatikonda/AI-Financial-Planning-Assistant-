"""
Database models for financial data
Using SQLAlchemy ORM with SQLite
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Transaction(Base):
    """Financial transactions"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # For multi-user support later
    date = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    subcategory = Column(String, nullable=True)
    account = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Goal(Base):
    """Financial goals"""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime, nullable=True)
    priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    status = Column(String, default="active")  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to goal updates
    updates = relationship("GoalUpdate", back_populates="goal", cascade="all, delete-orphan")


class GoalUpdate(Base):
    """Track progress updates for goals"""
    __tablename__ = "goal_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    amount = Column(Float, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to goal
    goal = relationship("Goal", back_populates="updates")


class Budget(Base):
    """Monthly budgets by category"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    category = Column(String, nullable=False)
    monthly_limit = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FinancialSnapshot(Base):
    """Monthly financial health snapshots"""
    __tablename__ = "financial_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    
    # Calculated metrics
    total_income = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    total_savings = Column(Float, default=0.0)
    debt_to_income_ratio = Column(Float, nullable=True)
    savings_rate = Column(Float, nullable=True)
    emergency_fund_months = Column(Float, nullable=True)
    
    # Overall score
    health_score = Column(Integer, nullable=True)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    """User financial profile"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    
    # Personal info
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    
    # Financial info
    monthly_income = Column(Float, nullable=True)
    risk_tolerance = Column(String, nullable=True)  # conservative, moderate, aggressive
    
    # Preferences
    preferred_currency = Column(String, default="USD")
    notification_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
