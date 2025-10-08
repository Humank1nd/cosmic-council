"""
Enterprise database models.
"""

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Enterprise(BaseModel):
    """Enterprises in the Cosmic Council"""
    __tablename__ = 'enterprises'
    
    enterprise_type = Column(String(50), nullable=False, unique=True)  # 'red_owl', 'orange_orangutan', etc.
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default='active')  # 'active', 'inactive', 'maintenance'
    configuration = Column(Text)  # JSON string
    performance_metrics = Column(Text)  # JSON string
    
    # Relationships
    cycles = relationship("Cycle", secondary="cycle_enterprises", back_populates="enterprises")
    results = relationship("EnterpriseResult", back_populates="enterprise")


class EnterpriseResult(BaseModel):
    """Results of enterprise execution"""
    __tablename__ = 'enterprise_results'
    
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('cycles.id'), nullable=False)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey('enterprises.id'), nullable=False)
    enterprise_type = Column(String(50), nullable=False)
    input_data = Column(Text)  # JSON string
    output_data = Column(Text)  # JSON string
    success = Column(String(10), default='false')  # 'true' or 'false'
    error_message = Column(Text)
    execution_time = Column(String(20), default='0.0')  # Store as string for flexibility
    resources_used = Column(Text)  # JSON string
    quality_score = Column(String(10), default='0.0')  # Store as string for flexibility
    
    # Relationships
    cycle = relationship("Cycle")
    enterprise = relationship("Enterprise", back_populates="results")
