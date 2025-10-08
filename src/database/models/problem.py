"""
Problem database models.
"""

from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

# Association tables for many-to-many relationships
problem_stakeholders = Table(
    'problem_stakeholders',
    BaseModel.metadata,
    Column('problem_id', UUID(as_uuid=True), ForeignKey('problems.id'), primary_key=True),
    Column('stakeholder_id', UUID(as_uuid=True), ForeignKey('stakeholders.id'), primary_key=True),
    Column('role', String(100)),
    Column('influence_level', String(20))
)

problem_constraints = Table(
    'problem_constraints',
    BaseModel.metadata,
    Column('problem_id', UUID(as_uuid=True), ForeignKey('problems.id'), primary_key=True),
    Column('constraint_id', UUID(as_uuid=True), ForeignKey('constraints.id'), primary_key=True),
    Column('constraint_value', Text)
)

problem_success_criteria = Table(
    'problem_success_criteria',
    BaseModel.metadata,
    Column('problem_id', UUID(as_uuid=True), ForeignKey('problems.id'), primary_key=True),
    Column('criterion_id', UUID(as_uuid=True), ForeignKey('success_criteria.id'), primary_key=True),
    Column('target_value', String(255)),
    Column('measurement_method', Text)
)


class Problem(BaseModel):
    """Problems to be solved by the Cosmic Council"""
    __tablename__ = 'problems'
    
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    domain = Column(String(200), nullable=False, index=True)
    complexity = Column(String(20), nullable=False)  # 'simple', 'moderate', 'complex', 'systemic'
    status = Column(String(20), default='active')  # 'active', 'in_progress', 'completed', 'archived'
    priority = Column(String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    
    # Foreign keys
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    due_date = Column(String(50))  # Store as string for flexibility
    
    # Relationships
    stakeholders = relationship("Stakeholder", secondary=problem_stakeholders, back_populates="problems")
    constraints = relationship("Constraint", secondary=problem_constraints, back_populates="problems")
    success_criteria = relationship("SuccessCriterion", secondary=problem_success_criteria, back_populates="problems")
    solutions = relationship("Solution", back_populates="problem")
    cycles = relationship("Cycle", back_populates="problem")


class ProblemStatement(BaseModel):
    """Problem statements for analysis"""
    __tablename__ = 'problem_statements'
    
    problem_id = Column(UUID(as_uuid=True), ForeignKey('problems.id'), nullable=False)
    statement = Column(Text, nullable=False)
    context = Column(Text)
    assumptions = Column(Text)
    questions = Column(Text)
    analysis_notes = Column(Text)
    
    # Relationships
    problem = relationship("Problem", backref="statements")
