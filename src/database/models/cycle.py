"""
Cycle database models.
"""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

# Association table for cycle enterprises
cycle_enterprises = Table(
    'cycle_enterprises',
    BaseModel.metadata,
    Column('cycle_id', UUID(as_uuid=True), ForeignKey('cycles.id'), primary_key=True),
    Column('enterprise_id', UUID(as_uuid=True), ForeignKey('enterprises.id'), primary_key=True),
    Column('execution_order', String(10)),
    Column('status', String(20)),  # 'pending', 'in_progress', 'completed', 'failed'
    Column('started_at', DateTime),
    Column('completed_at', DateTime)
)


class Cycle(BaseModel):
    """Problem-solving cycles"""
    __tablename__ = 'cycles'
    
    problem_id = Column(UUID(as_uuid=True), ForeignKey('problems.id'), nullable=False)
    status = Column(String(20), default='pending')  # 'pending', 'running', 'completed', 'failed', 'paused'
    current_enterprise = Column(String(50))  # Current executing enterprise
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Foreign keys
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    problem = relationship("Problem", back_populates="cycles")
    enterprises = relationship("Enterprise", secondary=cycle_enterprises, back_populates="cycles")
    results = relationship("CycleResult", back_populates="cycle")


class CycleResult(BaseModel):
    """Results of cycle execution"""
    __tablename__ = 'cycle_results'
    
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('cycles.id'), nullable=False)
    enterprise_type = Column(String(50), nullable=False)
    result_data = Column(Text)  # JSON string
    success = Column(String(10), default='false')  # 'true' or 'false'
    error_message = Column(Text)
    execution_time = Column(String(20), default='0.0')  # Store as string for flexibility
    metrics = Column(Text)  # JSON string
    
    # Relationships
    cycle = relationship("Cycle", back_populates="results")
