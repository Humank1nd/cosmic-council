"""
User and stakeholder database models.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    """Users in the Cosmic Council system"""
    __tablename__ = 'users'
    
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default='user')  # 'admin', 'user', 'viewer'
    permissions = Column(Text)  # JSON string
    preferences = Column(Text)  # JSON string
    last_login = Column(DateTime)
    is_active = Column(String(10), default='true')  # 'true' or 'false'
    
    # Relationships
    created_problems = relationship("Problem", foreign_keys="Problem.created_by", backref="creator")
    created_solutions = relationship("Solution", foreign_keys="Solution.created_by", backref="creator")
    created_cycles = relationship("Cycle", foreign_keys="Cycle.created_by", backref="creator")


class Stakeholder(BaseModel):
    """Stakeholders in problems"""
    __tablename__ = 'stakeholders'
    
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    role = Column(String(100))
    organization = Column(String(255))
    influence_level = Column(String(20), default='medium')  # 'low', 'medium', 'high'
    interest_level = Column(String(20), default='medium')  # 'low', 'medium', 'high'
    contact_info = Column(Text)  # JSON string
    notes = Column(Text)
    
    # Relationships
    problems = relationship("Problem", secondary="problem_stakeholders", back_populates="stakeholders")


class Constraint(BaseModel):
    """Constraints for problems"""
    __tablename__ = 'constraints'
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    constraint_type = Column(String(50), nullable=False)  # 'time', 'budget', 'resource', 'technical'
    priority = Column(String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    
    # Relationships
    problems = relationship("Problem", secondary="problem_constraints", back_populates="constraints")


class SuccessCriterion(BaseModel):
    """Success criteria for problems"""
    __tablename__ = 'success_criteria'
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    measurement_type = Column(String(50), nullable=False)  # 'quantitative', 'qualitative'
    target_value = Column(String(255))
    measurement_method = Column(Text)
    
    # Relationships
    problems = relationship("Problem", secondary="problem_success_criteria", back_populates="success_criteria")
