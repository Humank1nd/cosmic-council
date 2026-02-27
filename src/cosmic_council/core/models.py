"""
Unified Database Models for Agent Orchestrator System
Integrates core models, detailed ROYGBV workflow models, and perpetual thinking system models.

This is the primary and only database models file - all other model files
should import from this unified implementation.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    ForeignKey, Table, Index, UniqueConstraint, CheckConstraint, DECIMAL, DATE
)
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime, timezone
from enum import Enum
import uuid

Base = declarative_base()

# Use a generic JSON type that works with various backends
try:
    from sqlalchemy.types import JSON as GenericJSON
except ImportError:
    # Fallback for older SQLAlchemy
    from sqlalchemy.dialects.postgresql import JSON as GenericJSON

# ============================================================================
# ASSOCIATION TABLES FOR MANY-TO-MANY RELATIONSHIPS
# ============================================================================

problem_stakeholders = Table(
    'problem_stakeholders',
    Base.metadata,
    Column('problem_id', UUID(as_uuid=True), ForeignKey('problems.id'), primary_key=True),
    Column('stakeholder_id', UUID(as_uuid=True), ForeignKey('stakeholders.id'), primary_key=True),
    Column('role', String(100)),  # e.g., 'primary', 'secondary', 'affected'
    Column('influence_level', String(20)),  # e.g., 'high', 'medium', 'low'
    Column('created_at', DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
)

problem_constraints = Table(
    'problem_constraints',
    Base.metadata,
    Column('problem_id', UUID(as_uuid=True), ForeignKey('problems.id'), primary_key=True),
    Column('constraint_id', UUID(as_uuid=True), ForeignKey('constraints.id'), primary_key=True),
    Column('constraint_value', Text),
    Column('created_at', DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
)

problem_success_criteria = Table(
    'problem_success_criteria',
    Base.metadata,
    Column('problem_id', UUID(as_uuid=True), ForeignKey('problems.id'), primary_key=True),
    Column('criterion_id', UUID(as_uuid=True), ForeignKey('success_criteria.id'), primary_key=True),
    Column('target_value', String(255)),
    Column('measurement_method', Text),
    Column('created_at', DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
)

cycle_enterprises = Table(
    'cycle_enterprises',
    Base.metadata,
    Column('cycle_id', UUID(as_uuid=True), ForeignKey('cycles.id'), primary_key=True),
    Column('enterprise_id', UUID(as_uuid=True), ForeignKey('enterprises.id'), primary_key=True),
    Column('execution_order', Integer),
    Column('status', String(20)),  # 'pending', 'in_progress', 'completed', 'failed'
    Column('started_at', DateTime(timezone=True)),
    Column('completed_at', DateTime(timezone=True)),
    Column('created_at', DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
)

solution_component_relationships = Table(
    'solution_component_relationships',
    Base.metadata,
    Column('solution_id', UUID(as_uuid=True), ForeignKey('solutions.id'), primary_key=True),
    Column('component_id', UUID(as_uuid=True), ForeignKey('solution_components.id'), primary_key=True),
    Column('relationship_type', String(50)),  # 'depends_on', 'conflicts_with', 'enhances'
    Column('created_at', DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
)

# ============================================================================
# CORE DOMAIN MODELS
# ============================================================================

class Problem(Base):
    """Problems to be solved by the Agent Orchestrator"""
    __tablename__ = 'problems'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    domain = Column(String(200), nullable=False, index=True)
    complexity = Column(String(20), nullable=False)  # 'simple', 'moderate', 'complex', 'systemic'
    status = Column(String(20), default='active')  # 'active', 'in_progress', 'completed', 'archived'
    priority = Column(String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    impact = Column(String(20), default='medium') # 'low', 'medium', 'high'
    urgency = Column(String(20), default='cyclical') # 'immediate', 'delayed', 'cyclical'
    priority_score = Column(Float, default=0.0) # Numerical score for ranking
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime(timezone=True))
    
    # Relationships
    stakeholders = relationship("Stakeholder", secondary=problem_stakeholders, back_populates="problems")
    constraints = relationship("Constraint", secondary=problem_constraints, back_populates="problems")
    success_criteria = relationship("SuccessCriterion", secondary=problem_success_criteria, back_populates="problems")
    cycles = relationship("Cycle", back_populates="problem", cascade="all, delete-orphan")
    solutions = relationship("Solution", back_populates="problem", cascade="all, delete-orphan")
    workflow_sessions = relationship("WorkflowSession", back_populates="problem", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_problem_domain_complexity', 'domain', 'complexity'),
        Index('idx_problem_status_priority', 'status', 'priority'),
        Index('idx_problem_created_by', 'created_by'),
    )

class Solution(Base):
    """Solutions generated by the Agent Orchestrator"""
    __tablename__ = 'solutions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey('problems.id'), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    solution_type = Column(String(50), nullable=False)  # 'primary', 'alternative', 'hybrid'
    status = Column(String(20), default='draft')  # 'draft', 'review', 'approved', 'implemented'
    confidence_score = Column(Float, default=0.0)
    feasibility_score = Column(Float, default=0.0)
    impact_score = Column(Float, default=0.0)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    problem = relationship("Problem", back_populates="solutions")
    components = relationship("SolutionComponent", back_populates="solution", cascade="all, delete-orphan")
    implementation_tracking = relationship("ImplementationTracking", back_populates="solution", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_solution_problem', 'problem_id'),
        Index('idx_solution_status', 'status'),
        Index('idx_solution_scores', 'confidence_score', 'feasibility_score', 'impact_score'),
    )

class Cycle(Base):
    """Problem-solving cycles executed by the Agent Orchestrator"""
    __tablename__ = 'cycles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey('problems.id'), nullable=False)
    cycle_number = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')  # 'pending', 'running', 'completed', 'failed'
    
    # Cycle metadata
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    total_duration = Column(Float)  # Duration in seconds
    overall_confidence = Column(Float, default=0.0)
    
    # Relationships
    problem = relationship("Problem", back_populates="cycles")
    enterprises = relationship("Enterprise", secondary=cycle_enterprises, back_populates="cycles")
    enterprise_results = relationship("EnterpriseResult", back_populates="cycle", cascade="all, delete-orphan")
    analytics = relationship("CycleAnalytics", back_populates="cycle", cascade="all, delete-orphan")
    ethical_assessment = relationship("EthicalImpactAssessment", back_populates="cycle", uselist=False, cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_cycle_problem', 'problem_id'),
        Index('idx_cycle_number', 'cycle_number'),
        Index('idx_cycle_status', 'status'),
        UniqueConstraint('problem_id', 'cycle_number', name='uq_problem_cycle_number'),
    )

class EthicalImpactAssessment(Base):
    """Ethical Impact Assessment for every cycle iteration"""
    __tablename__ = 'ethical_impact_assessments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('cycles.id'), nullable=False)
    
    # Assessment metrics
    bias_risk_score = Column(Float, default=0.0) # 0.0 to 1.0
    equity_score = Column(Float, default=0.0)    # 0.0 to 1.0
    accessibility_rating = Column(String(20))    # 'low', 'medium', 'high'
    
    # Analysis details
    ideological_bias_checks = Column(GenericJSON) # Detailed check results
    exclusionary_risks = Column(GenericJSON)
    mitigation_recommendations = Column(GenericJSON)
    
    # Review Board Status
    requires_human_review = Column(Boolean, default=False)
    review_status = Column(String(20), default='pending') # 'pending', 'approved', 'flagged'
    reviewer_notes = Column(Text)
    reviewed_at = Column(DateTime(timezone=True))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    cycle = relationship("Cycle", back_populates="ethical_assessment")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    alerts = relationship("EthicalAlert", back_populates="assessment")
    
    # Indexes
    __table_args__ = (
        Index('idx_ethical_assessment_cycle', 'cycle_id'),
        Index('idx_ethical_assessment_status', 'review_status'),
    )

class EthicalAlert(Base):
    """Real-Time Ethical Monitoring System (RTEMS) Alerts"""
    __tablename__ = 'ethical_alerts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey('ethical_impact_assessments.id'))
    alert_level = Column(String(20)) # 'info', 'warning', 'critical'
    description = Column(Text, nullable=False)
    status = Column(String(20), default='active') # 'active', 'resolved', 'escalated'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    assessment = relationship("EthicalImpactAssessment", back_populates="alerts")

class EthicalAuditLog(Base):
    """Immutable blockchain-inspired ethical audit logs"""
    __tablename__ = 'ethical_audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    hash_checksum = Column(String(64)) # Integrity check
    actor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    payload = Column(GenericJSON)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class EthicalPolicy(Base):
    """Dynamic Ethical Recalibration (DER) Policies"""
    __tablename__ = 'ethical_policies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    rules = Column(GenericJSON, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ExternalEthicalAudit(Base):
    """Formal reports from Independent Ethical Audit & Governance Panels"""
    __tablename__ = 'external_ethical_audits'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auditor_name = Column(String(200), nullable=False)
    organization = Column(String(200))
    audit_scope = Column(String(500)) # e.g., 'Cycle 108-112', 'Blue Dolphin Marketing'
    findings_summary = Column(Text, nullable=False)
    recommendations = Column(GenericJSON)
    integrity_verification_hash = Column(String(64)) # Links to audit trail hash
    
    # Audit outcome
    compliance_rating = Column(Float) # 0.0 to 1.0
    status = Column(String(20), default='certified') # 'certified', 'conditional', 'failed'
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    verified_at = Column(DateTime(timezone=True))

class BiasAuditReport(Base):
    """Automated Bias Auditing & Algorithmic Fairness Reports"""
    __tablename__ = 'bias_audit_reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type = Column(String(50)) # 'agent', 'cycle', 'solution'
    resource_id = Column(UUID(as_uuid=True))
    
    # Fairness Metrics
    fairness_score = Column(Float, default=0.0) # 0.0 to 1.0
    bias_detected = Column(Boolean, default=False)
    bias_types = Column(GenericJSON) # ['gender', 'cultural', 'socioeconomic']
    
    # Adversarial Testing
    adversarial_vulnerabilities = Column(GenericJSON) # List of blind spots discovered
    stress_test_payload = Column(Text) # The input that challenged the AI
    
    # Correction status
    is_self_corrected = Column(Boolean, default=False)
    correction_details = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Enterprise(Base):
    """The six enterprises of the Agent Orchestrator"""
    __tablename__ = 'enterprises'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    enterprise_type = Column(String(50), nullable=False, unique=True)  # 'red_owl', 'orange_orangutan', etc.
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    principle = Column(String(100))  # Core principle
    
    # Relationships
    cycles = relationship("Cycle", secondary=cycle_enterprises, back_populates="enterprises")
    enterprise_results = relationship("EnterpriseResult", back_populates="enterprise", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_enterprise_type', 'enterprise_type'),
    )

class EnterpriseResult(Base):
    """Results from enterprise processing within a cycle"""
    __tablename__ = 'enterprise_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('cycles.id'), nullable=False)
    enterprise_id = Column(UUID(as_uuid=True), ForeignKey('enterprises.id'), nullable=False)
    
    # Result data
    status = Column(String(20), nullable=False)  # 'completed', 'failed', 'partial'
    insights = Column(JSON)
    recommendations = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)
    next_actions = Column(JSON)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    cycle = relationship("Cycle", back_populates="enterprise_results")
    enterprise = relationship("Enterprise", back_populates="enterprise_results")
    
    # Indexes
    __table_args__ = (
        Index('idx_enterprise_result_cycle', 'cycle_id'),
        Index('idx_enterprise_result_enterprise', 'enterprise_id'),
        Index('idx_enterprise_result_status', 'status'),
    )

# ============================================================================
# RESEARCH DATABASE MODELS (Red Owl - Research & Inquiry)
# ============================================================================

class ResearchCoreProblem(Base):
    """Core Problem Table - Captures the main problem statement and context"""
    __tablename__ = 'research_core_problems'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_reference_id = Column(String(50), unique=True, nullable=False)
    main_problem_statement = Column(Text, nullable=False)
    context = Column(Text)
    initial_observations = Column(Text)
    date_identified = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    submitted_by = Column(String(100))
    associated_themes = Column(JSON)
    severity_priority_rating = Column(String(20))
    problem_status = Column(String(20), default='active')
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    research_findings = relationship("ResearchFinding", back_populates="core_problem", cascade="all, delete-orphan")
    prioritized_questions = relationship("ResearchPrioritizedQuestion", back_populates="core_problem", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_research_core_problems_reference', 'problem_reference_id'),
        Index('idx_research_core_problems_status', 'problem_status'),
        Index('idx_research_core_problems_severity', 'severity_priority_rating'),
    )

class ResearchFinding(Base):
    """Research Findings Table - Repository for detailed research entries"""
    __tablename__ = 'research_findings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    core_problem_id = Column(UUID(as_uuid=True), ForeignKey('research_core_problems.id', ondelete='CASCADE'), nullable=False)
    
    # Finding details
    source = Column(String(500))
    author = Column(String(200))
    date_of_publication = Column(DATE)
    summary = Column(Text, nullable=False)
    relevance_to_problem = Column(Text)
    keywords_tags = Column(JSON)
    date_added = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Ratings
    credibility_rating = Column(Integer)
    relevance_rating = Column(Integer)
    impact_rating = Column(Integer)
    
    # Additional data
    notes = Column(Text)
    attachments = Column(JSON)  # Store file references and metadata
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    core_problem = relationship("ResearchCoreProblem", back_populates="research_findings")
    
    # Indexes
    __table_args__ = (
        Index('idx_research_findings_core_problem_id', 'core_problem_id'),
        Index('idx_research_findings_relevance_rating', 'relevance_rating'),
    )

class ResearchPrioritizedQuestion(Base):
    """Prioritized Questions Table - Critical questions for Planning stage"""
    __tablename__ = 'research_prioritized_questions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    core_problem_id = Column(UUID(as_uuid=True), ForeignKey('research_core_problems.id', ondelete='CASCADE'), nullable=False)
    
    # Question details
    question_text = Column(Text, nullable=False)
    supporting_research_links = Column(JSON, default=[])  # Array of research_findings IDs
    importance_rating = Column(Integer)
    relevance_to_core_problem = Column(Text)
    date_added = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    category_theme = Column(String(100))
    
    # Status tracking
    status = Column(String(20), default='pending')
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    core_problem = relationship("ResearchCoreProblem", back_populates="prioritized_questions")
    planning_questions = relationship("PlanningRelatedQuestion", back_populates="research_question", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_research_prioritized_questions_core_problem_id', 'core_problem_id'),
        Index('idx_research_prioritized_questions_importance', 'importance_rating'),
    )

# ============================================================================
# PLANNING DATABASE MODELS (Orange Orangutan - Planning & Logistics)
# ============================================================================

class PlanningRelatedQuestion(Base):
    """Related Questions Table - Pulls prioritized questions from Research"""
    __tablename__ = 'planning_related_questions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    research_question_id = Column(UUID(as_uuid=True), ForeignKey('research_prioritized_questions.id', ondelete='CASCADE'), nullable=False)
    
    # Question details (copied from research)
    question_text = Column(Text, nullable=False)
    importance_rating = Column(Integer)
    category_theme = Column(String(100))
    
    # Planning status
    planning_status = Column(String(20), default='pending')
    assigned_to = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    research_question = relationship("ResearchPrioritizedQuestion", back_populates="planning_questions")
    action_plans = relationship("PlanningActionPlan", back_populates="related_question", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_planning_related_questions_research_id', 'research_question_id'),
    )

class PlanningActionPlan(Base):
    """Action Plan Table - High-level objectives and detailed steps"""
    __tablename__ = 'planning_action_plans'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    related_question_id = Column(UUID(as_uuid=True), ForeignKey('planning_related_questions.id', ondelete='CASCADE'), nullable=False)
    
    # Plan details
    high_level_objective = Column(Text, nullable=False)
    detailed_steps = Column(JSON, nullable=False)  # Array of step objects
    timeline_estimate = Column(Integer)  # Days
    priority_level = Column(String(20))
    
    # Status tracking
    plan_status = Column(String(20), default='draft')
    completion_percentage = Column(DECIMAL(5, 2), default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    related_question = relationship("PlanningRelatedQuestion", back_populates="action_plans")
    dependencies = relationship("PlanningDependency", back_populates="action_plan", cascade="all, delete-orphan")
    prototypes = relationship("DevelopmentPrototype", back_populates="action_plan", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_planning_action_plans_question_id', 'related_question_id'),
    )

class PlanningDependency(Base):
    """Dependencies Identified Table - Critical resources and knowledge areas"""
    __tablename__ = 'planning_dependencies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_plan_id = Column(UUID(as_uuid=True), ForeignKey('planning_action_plans.id', ondelete='CASCADE'), nullable=False)
    
    # Dependency details
    dependency_type = Column(String(50))
    dependency_description = Column(Text, nullable=False)
    criticality_level = Column(String(20))
    estimated_cost = Column(DECIMAL(12, 2))
    estimated_time_days = Column(Integer)
    
    # Status tracking
    dependency_status = Column(String(20), default='identified')
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    action_plan = relationship("PlanningActionPlan", back_populates="dependencies")
    
    # Indexes
    __table_args__ = (
        Index('idx_planning_dependencies_action_plan_id', 'action_plan_id'),
    )

# ============================================================================
# DEVELOPMENT DATABASE MODELS (Yellow Honeybee - Development & Creativity)
# ============================================================================

class DevelopmentPrototype(Base):
    """Prototype Table - Designs and initial concepts"""
    __tablename__ = 'development_prototypes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_plan_id = Column(UUID(as_uuid=True), ForeignKey('planning_action_plans.id', ondelete='CASCADE'), nullable=False)
    
    # Prototype details
    prototype_name = Column(String(200), nullable=False)
    prototype_description = Column(Text, nullable=False)
    design_specifications = Column(JSON)
    technical_requirements = Column(JSON)
    creative_concepts = Column(JSON)
    
    # Status tracking
    prototype_status = Column(String(20), default='concept')
    development_stage = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    action_plan = relationship("PlanningActionPlan", back_populates="prototypes")
    internal_testing = relationship("DevelopmentInternalTesting", back_populates="prototype", cascade="all, delete-orphan")
    creative_notes = relationship("DevelopmentCreativeNote", back_populates="prototype", cascade="all, delete-orphan")
    budget_allocations = relationship("BudgetAllocation", back_populates="prototype", cascade="all, delete-orphan")
    market_insights = relationship("MarketInsight", back_populates="prototype", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_development_prototypes_action_plan_id', 'action_plan_id'),
    )

class DevelopmentInternalTesting(Base):
    """Internal Testing Table - Evaluates prototypes against criteria"""
    __tablename__ = 'development_internal_testing'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prototype_id = Column(UUID(as_uuid=True), ForeignKey('development_prototypes.id', ondelete='CASCADE'), nullable=False)
    
    # Testing details
    test_name = Column(String(200), nullable=False)
    test_type = Column(String(50))
    test_criteria = Column(JSON, nullable=False)
    test_results = Column(JSON)
    pass_fail_status = Column(String(10))
    
    # Performance metrics
    performance_score = Column(DECIMAL(5, 2))
    efficiency_rating = Column(Integer)
    
    # Metadata
    test_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tested_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    prototype = relationship("DevelopmentPrototype", back_populates="internal_testing")
    creative_notes = relationship("DevelopmentCreativeNote", back_populates="testing", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_development_internal_testing_prototype_id', 'prototype_id'),
    )

class DevelopmentCreativeNote(Base):
    """Creative Notes Table - Brainstorming and refinement ideas"""
    __tablename__ = 'development_creative_notes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prototype_id = Column(UUID(as_uuid=True), ForeignKey('development_prototypes.id', ondelete='CASCADE'))
    testing_id = Column(UUID(as_uuid=True), ForeignKey('development_internal_testing.id', ondelete='CASCADE'))
    
    # Note details
    note_type = Column(String(50))
    note_content = Column(Text, nullable=False)
    inspiration_source = Column(String(200))
    feasibility_rating = Column(Integer)
    
    # Status
    implementation_status = Column(String(20), default='idea')
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_by = Column(String(100))
    
    # Relationships
    prototype = relationship("DevelopmentPrototype", back_populates="creative_notes")
    testing = relationship("DevelopmentInternalTesting", back_populates="creative_notes")
    
    # Indexes
    __table_args__ = (
        Index('idx_development_creative_notes_prototype_id', 'prototype_id'),
    )

# ============================================================================
# BUDGET DATABASE MODELS (Green Tortoise - Budget & Resources)
# ============================================================================

class BudgetResourceInventory(Base):
    """Resource Inventory Table - Tracks available resources"""
    __tablename__ = 'budget_resource_inventory'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Resource details
    resource_name = Column(String(200), nullable=False)
    resource_type = Column(String(50))
    resource_description = Column(Text)
    current_availability = Column(String(20))
    quantity_available = Column(Integer)
    unit_cost = Column(DECIMAL(12, 2))
    
    # Metadata
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class BudgetAllocation(Base):
    """Budget Allocation Table - Allocates funding for projects"""
    __tablename__ = 'budget_allocations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prototype_id = Column(UUID(as_uuid=True), ForeignKey('development_prototypes.id', ondelete='CASCADE'), nullable=False)
    
    # Allocation details
    allocation_name = Column(String(200), nullable=False)
    allocated_amount = Column(DECIMAL(12, 2), nullable=False)
    allocation_category = Column(String(50))
    approved_by = Column(String(100))
    approval_date = Column(DateTime(timezone=True))
    
    # Status tracking
    allocation_status = Column(String(20), default='pending')
    spent_amount = Column(DECIMAL(12, 2), default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    prototype = relationship("DevelopmentPrototype", back_populates="budget_allocations")
    time_cost_analysis = relationship("BudgetTimeCostAnalysis", back_populates="budget_allocation", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_budget_allocations_prototype_id', 'prototype_id'),
    )

class BudgetTimeCostAnalysis(Base):
    """Time and Cost Analysis Table - Cost-effectiveness assessment"""
    __tablename__ = 'budget_time_cost_analysis'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_allocation_id = Column(UUID(as_uuid=True), ForeignKey('budget_allocations.id', ondelete='CASCADE'), nullable=False)
    
    # Analysis details
    analysis_type = Column(String(50))
    estimated_cost = Column(DECIMAL(12, 2))
    actual_cost = Column(DECIMAL(12, 2))
    estimated_time_days = Column(Integer)
    actual_time_days = Column(Integer)
    cost_effectiveness_rating = Column(Integer)
    
    # Analysis results
    variance_analysis = Column(Text)
    recommendations = Column(Text)
    
    # Metadata
    analysis_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    analyzed_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    budget_allocation = relationship("BudgetAllocation", back_populates="time_cost_analysis")
    
    # Indexes
    __table_args__ = (
        Index('idx_budget_time_cost_analysis_allocation_id', 'budget_allocation_id'),
    )

# ============================================================================
# MARKET DATABASE MODELS (Blue Dolphin - Market & Communication)
# ============================================================================

class MarketInsight(Base):
    """Market Insights Table - Trends, consumer behavior, competitor analysis"""
    __tablename__ = 'market_insights'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prototype_id = Column(UUID(as_uuid=True), ForeignKey('development_prototypes.id', ondelete='CASCADE'), nullable=False)
    
    # Insight details
    insight_type = Column(String(50))
    insight_title = Column(String(200), nullable=False)
    insight_description = Column(Text, nullable=False)
    data_source = Column(String(200))
    confidence_level = Column(Integer)
    
    # Market data
    target_audience = Column(JSON)
    market_size_estimate = Column(DECIMAL(15, 2))
    growth_potential = Column(String(20))
    
    # Metadata
    insight_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    prototype = relationship("DevelopmentPrototype", back_populates="market_insights")
    communication_strategies = relationship("MarketCommunicationStrategy", back_populates="market_insight", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_market_insights_prototype_id', 'prototype_id'),
    )

class MarketCommunicationStrategy(Base):
    """Communication Strategy Table - Engagement plans based on market insights"""
    __tablename__ = 'market_communication_strategies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_insight_id = Column(UUID(as_uuid=True), ForeignKey('market_insights.id', ondelete='CASCADE'), nullable=False)
    
    # Strategy details
    strategy_name = Column(String(200), nullable=False)
    target_audience = Column(JSON, nullable=False)
    communication_channels = Column(JSON)
    key_messages = Column(JSON)
    engagement_approach = Column(Text)
    
    # Implementation details
    implementation_timeline = Column(Integer)  # Days
    estimated_reach = Column(Integer)
    budget_required = Column(DECIMAL(12, 2))
    
    # Status tracking
    strategy_status = Column(String(20), default='draft')
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    market_insight = relationship("MarketInsight", back_populates="communication_strategies")
    performance_metrics = relationship("MarketPerformanceMetric", back_populates="communication_strategy", cascade="all, delete-orphan")
    user_feedback = relationship("SupportUserFeedback", back_populates="communication_strategy", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_market_communication_strategies_insight_id', 'market_insight_id'),
    )

class MarketPerformanceMetric(Base):
    """Performance Metrics Table - Measures communication effectiveness"""
    __tablename__ = 'market_performance_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    communication_strategy_id = Column(UUID(as_uuid=True), ForeignKey('market_communication_strategies.id', ondelete='CASCADE'), nullable=False)
    
    # Metric details
    metric_name = Column(String(200), nullable=False)
    metric_type = Column(String(50))
    metric_value = Column(DECIMAL(15, 2))
    metric_unit = Column(String(50))
    target_value = Column(DECIMAL(15, 2))
    
    # Performance data
    measurement_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    performance_rating = Column(Integer)
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    communication_strategy = relationship("MarketCommunicationStrategy", back_populates="performance_metrics")
    
    # Indexes
    __table_args__ = (
        Index('idx_market_performance_metrics_strategy_id', 'communication_strategy_id'),
    )

# ============================================================================
# SUPPORT DATABASE MODELS (Violet Elephant - Support & Feedback)
# ============================================================================

class SupportUserFeedback(Base):
    """User Feedback Table - Input from users and stakeholders"""
    __tablename__ = 'support_user_feedback'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    communication_strategy_id = Column(UUID(as_uuid=True), ForeignKey('market_communication_strategies.id', ondelete='CASCADE'))
    
    # Feedback details
    feedback_type = Column(String(50))
    feedback_content = Column(Text, nullable=False)
    user_type = Column(String(50))
    user_identifier = Column(String(200))  # Anonymous or identified user
    
    # Feedback ratings
    satisfaction_rating = Column(Integer)
    priority_level = Column(String(20))
    
    # Status tracking
    feedback_status = Column(String(20), default='received')
    
    # Metadata
    feedback_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    communication_strategy = relationship("MarketCommunicationStrategy", back_populates="user_feedback")
    performance_assessments = relationship("SupportPerformanceAssessment", back_populates="user_feedback", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_support_user_feedback_strategy_id', 'communication_strategy_id'),
    )

class SupportPerformanceAssessment(Base):
    """Performance Assessment Table - Reviews feedback against objectives"""
    __tablename__ = 'support_performance_assessments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_feedback_id = Column(UUID(as_uuid=True), ForeignKey('support_user_feedback.id', ondelete='CASCADE'))
    
    # Assessment details
    assessment_type = Column(String(50))
    assessment_criteria = Column(JSON, nullable=False)
    assessment_results = Column(JSON)
    performance_score = Column(DECIMAL(5, 2))
    
    # Analysis
    strengths_identified = Column(JSON)
    areas_for_improvement = Column(JSON)
    recommendations = Column(Text)
    
    # Status
    assessment_status = Column(String(20), default='in_progress')
    
    # Metadata
    assessment_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    assessed_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user_feedback = relationship("SupportUserFeedback", back_populates="performance_assessments")
    continuous_improvements = relationship("SupportContinuousImprovement", back_populates="performance_assessment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_support_performance_assessments_feedback_id', 'user_feedback_id'),
    )

class SupportContinuousImprovement(Base):
    """Continuous Improvement Table - Actionable recommendations for future cycles"""
    __tablename__ = 'support_continuous_improvements'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    performance_assessment_id = Column(UUID(as_uuid=True), ForeignKey('support_performance_assessments.id', ondelete='CASCADE'))
    
    # Improvement details
    improvement_title = Column(String(200), nullable=False)
    improvement_description = Column(Text, nullable=False)
    improvement_category = Column(String(50))
    priority_level = Column(String(20))
    
    # Implementation details
    estimated_effort = Column(String(50))
    estimated_impact = Column(String(50))
    implementation_timeline = Column(Integer)  # Days
    
    # Status tracking
    improvement_status = Column(String(20), default='identified')
    
    # Next cycle linkage
    next_cycle_focus = Column(Boolean, default=False)
    research_priority = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    performance_assessment = relationship("SupportPerformanceAssessment", back_populates="continuous_improvements")
    
    # Indexes
    __table_args__ = (
        Index('idx_support_continuous_improvements_assessment_id', 'performance_assessment_id'),
        Index('idx_support_continuous_improvements_next_cycle', 'next_cycle_focus'),
    )

# ============================================================================
# ADDITIONAL CORE MODELS (from database_models.py)
# ============================================================================

class User(Base):
    """Users of the Agent Orchestrator system"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(255))
    role = Column(String(50), default='user')  # 'admin', 'user', 'viewer'
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    created_problems = relationship("Problem", back_populates="creator", foreign_keys="Problem.created_by")
    created_solutions = relationship("Solution", back_populates="creator", foreign_keys="Solution.created_by")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
        Index('idx_user_role', 'role'),
    )

class Stakeholder(Base):
    """Stakeholders involved in problems"""
    __tablename__ = 'stakeholders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    organization = Column(String(255))
    role = Column(String(100))
    influence_level = Column(String(20))  # 'high', 'medium', 'low'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    problems = relationship("Problem", secondary=problem_stakeholders, back_populates="stakeholders")
    
    # Indexes
    __table_args__ = (
        Index('idx_stakeholder_name', 'name'),
        Index('idx_stakeholder_organization', 'organization'),
    )

class Constraint(Base):
    """Constraints that affect problem solving"""
    __tablename__ = 'constraints'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    constraint_type = Column(String(50))  # 'budget', 'time', 'resource', 'technical', 'legal'
    severity = Column(String(20))  # 'low', 'medium', 'high', 'critical'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    problems = relationship("Problem", secondary=problem_constraints, back_populates="constraints")
    
    # Indexes
    __table_args__ = (
        Index('idx_constraint_type', 'constraint_type'),
        Index('idx_constraint_severity', 'severity'),
    )

class SuccessCriterion(Base):
    """Success criteria for problems"""
    __tablename__ = 'success_criteria'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    measurement_type = Column(String(50))  # 'quantitative', 'qualitative', 'binary'
    target_value = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    problems = relationship("Problem", secondary=problem_success_criteria, back_populates="success_criteria")
    
    # Indexes
    __table_args__ = (
        Index('idx_success_criterion_name', 'name'),
        Index('idx_success_criterion_measurement', 'measurement_type'),
    )

class SolutionComponent(Base):
    """Components of solutions"""
    __tablename__ = 'solution_components'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution_id = Column(UUID(as_uuid=True), ForeignKey('solutions.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    component_type = Column(String(50))  # 'feature', 'process', 'resource', 'constraint'
    priority = Column(String(20))  # 'low', 'medium', 'high', 'critical'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    solution = relationship("Solution", back_populates="components")
    
    # Indexes
    __table_args__ = (
        Index('idx_solution_component_solution', 'solution_id'),
        Index('idx_solution_component_type', 'component_type'),
    )

class ImplementationTracking(Base):
    """Tracking implementation progress of solutions"""
    __tablename__ = 'implementation_tracking'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution_id = Column(UUID(as_uuid=True), ForeignKey('solutions.id'), nullable=False)
    status = Column(String(20), default='not_started')  # 'not_started', 'in_progress', 'completed', 'paused', 'cancelled'
    progress_percentage = Column(Float, default=0.0)
    notes = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    solution = relationship("Solution", back_populates="implementation_tracking")
    
    # Indexes
    __table_args__ = (
        Index('idx_implementation_tracking_solution', 'solution_id'),
        Index('idx_implementation_tracking_status', 'status'),
    )

class CycleAnalytics(Base):
    """Analytics data for cycles"""
    __tablename__ = 'cycle_analytics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('cycles.id'), nullable=False)
    
    # Analytics data
    total_processing_time = Column(Float)
    avg_confidence_score = Column(Float)
    enterprise_success_rate = Column(Float)
    insights_generated = Column(Integer)
    recommendations_generated = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    cycle = relationship("Cycle", back_populates="analytics")
    
    # Indexes
    __table_args__ = (
        Index('idx_cycle_analytics_cycle', 'cycle_id'),
    )

class SystemMetrics(Base):
    """System-wide metrics and analytics"""
    __tablename__ = 'system_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metrics data
    total_problems = Column(Integer, default=0)
    total_solutions = Column(Integer, default=0)
    total_cycles = Column(Integer, default=0)
    avg_cycle_duration = Column(Float, default=0.0)
    avg_solution_confidence = Column(Float, default=0.0)
    system_uptime = Column(Float, default=0.0)
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_system_metrics_recorded', 'recorded_at'),
    )

class AuditLog(Base):
    """Audit log for system activities"""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))  # 'problem', 'solution', 'cycle', etc.
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_log_user', 'user_id'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_log_created', 'created_at'),
    )

class WorkflowSession(Base):
    """Workflow sessions for step-by-step problem solving"""
    __tablename__ = 'workflow_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey('problems.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Session data
    session_type = Column(String(50), default='standard')  # 'standard', 'ai_enhanced', 'collaborative'
    status = Column(String(20), default='active')  # 'active', 'completed', 'paused', 'cancelled'
    current_step = Column(String(50))  # Current workflow step
    
    # Session metadata
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    total_duration = Column(Integer)  # Duration in seconds
    
    # AI enhancement data
    ai_enhanced = Column(Boolean, default=False)
    ai_confidence_threshold = Column(Float, default=0.7)
    conversation_id = Column(String(255))  # AI conversation ID
    
    # Session data
    session_data = Column(JSON)  # General session data
    user_preferences = Column(JSON)  # User preferences and settings
    session_notes = Column(JSON)  # Session notes and observations (changed from ARRAY to JSON)
    
    # Relationships
    problem = relationship("Problem", back_populates="workflow_sessions")
    user = relationship("User")
    workflow_steps = relationship("WorkflowStep", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_workflow_session_problem', 'problem_id'),
        Index('idx_workflow_session_user', 'user_id'),
        Index('idx_workflow_session_status', 'status'),
        Index('idx_workflow_session_started', 'started_at'),
    )

class WorkflowStep(Base):
    """Individual steps within a workflow session"""
    __tablename__ = 'workflow_steps'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('workflow_sessions.id'), nullable=False)
    
    # Step data
    step_name = Column(String(100), nullable=False)
    step_type = Column(String(50), nullable=False)  # 'research', 'planning', 'development', etc.
    step_order = Column(Integer, nullable=False)
    
    # Step status
    status = Column(String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'skipped'
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration = Column(Integer)  # Duration in seconds
    
    # Step data
    input_data = Column(JSON)  # Input data for the step
    output_data = Column(JSON)  # Output data from the step
    step_notes = Column(Text)  # Step-specific notes
    
    # AI enhancement data
    ai_enhanced = Column(Boolean, default=False)
    ai_confidence_score = Column(Float)
    ai_suggestions = Column(JSON)  # AI suggestions for this step
    
    # Relationships
    session = relationship("WorkflowSession", back_populates="workflow_steps")
    
    # Indexes
    __table_args__ = (
        Index('idx_workflow_step_session', 'session_id'),
        Index('idx_workflow_step_order', 'step_order'),
        Index('idx_workflow_step_status', 'status'),
        Index('idx_workflow_step_type', 'step_type'),
    )

# ============================================================================
# PERPETUAL THINKING SYSTEM MODELS (from perpetual_database_models.py)
# ============================================================================

class PerpetualSessionStatus(Enum):
    """Status of perpetual thinking sessions"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    TERMINATED = "terminated"

class CycleType(Enum):
    """Types of perpetual cycles"""
    EXPLORATION = "exploration"
    CONVERGENCE = "convergence"
    SYNTHESIS = "synthesis"
    META_REFLECTION = "meta_reflection"
    BREAKTHROUGH = "breakthrough"
    ADAPTATION = "adaptation"

class PatternType(Enum):
    """Types of emergent patterns"""
    CONVERGENCE = "convergence"
    DIVERGENCE = "divergence"
    OSCILLATION = "oscillation"
    BREAKTHROUGH = "breakthrough"
    STAGNATION = "stagnation"
    EVOLUTION = "evolution"

class MetaCycleType(Enum):
    """Types of meta-cycles"""
    OPTIMIZATION = "optimization"
    ADAPTATION = "adaptation"
    INNOVATION = "innovation"
    REFLECTION = "reflection"
    EVOLUTION = "evolution"

class OrchestrationMode(Enum):
    """Modes of orchestration"""
    AUTONOMOUS = "autonomous"
    COLLABORATIVE = "collaborative"
    GUIDED = "guided"
    HYBRID = "hybrid"

class PerpetualThinkingSession(Base):
    """Represents an ongoing perpetual thinking session"""
    __tablename__ = 'perpetual_thinking_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_name = Column(String(255), nullable=False)
    initial_input = Column(Text, nullable=False)
    current_input = Column(Text)
    
    # Session metadata
    current_cycle_number = Column(Integer, default=0)
    status = Column(String(20), default='active')
    mode = Column(String(20), default='collaborative')  # OrchestrationMode
    
    # Goals and criteria
    goals = Column(JSON)  # List of strings
    success_criteria = Column(JSON)  # List of strings
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True))
    
    # Session data
    session_data = Column(JSON)  # General session data
    summary_metrics = Column(JSON)  # Summary metrics for the session
    
    # Relationships
    perpetual_cycles = relationship("PerpetualCycle", back_populates="session", cascade="all, delete-orphan")
    breakthrough_moments = relationship("BreakthroughMoment", back_populates="session", cascade="all, delete-orphan")
    human_feedback_points = relationship("HumanFeedbackPoint", back_populates="session", cascade="all, delete-orphan")
    meta_cycles = relationship("MetaCycle", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_perpetual_session_status', 'status'),
        Index('idx_perpetual_session_created', 'created_at'),
        Index('idx_perpetual_session_mode', 'mode'),
    )

class PerpetualCycle(Base):
    """Represents a single cycle within a perpetual thinking session"""
    __tablename__ = 'perpetual_cycles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_thinking_sessions.id'), nullable=False)
    cycle_number = Column(Integer, nullable=False)
    
    # Cycle metadata
    cycle_type = Column(String(20), nullable=False)  # CycleType
    status = Column(String(20), default='running')
    
    # Input/Output
    input_text = Column(Text, nullable=False)
    output_text = Column(Text)
    input_hash = Column(String(64))
    output_hash = Column(String(64))
    
    # Metrics
    new_questions_generated = Column(Integer, default=0)
    insights_count = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    effectiveness_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    
    # Pattern detection
    pattern_detected = Column(String(20))  # PatternType
    meta_insights = Column(JSON)  # List of strings
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    duration = Column(Float)  # Duration in seconds
    
    # Relationships
    session = relationship("PerpetualThinkingSession", back_populates="perpetual_cycles")
    think_tank_results = relationship("PerpetualThinkTankResult", back_populates="cycle", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_perpetual_cycle_session', 'session_id'),
        Index('idx_perpetual_cycle_number', 'cycle_number'),
        Index('idx_perpetual_cycle_type', 'cycle_type'),
        Index('idx_perpetual_cycle_pattern', 'pattern_detected'),
        Index('idx_perpetual_cycle_started', 'started_at'),
        UniqueConstraint('session_id', 'cycle_number', name='uq_perpetual_session_cycle_number'),
    )

class PerpetualThinkTankResult(Base):
    """Results from Think Tank processing within a perpetual cycle"""
    __tablename__ = 'perpetual_think_tank_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_cycles.id'), nullable=False)
    
    # Think Tank identification
    think_tank_name = Column(String(50), nullable=False)
    phase = Column(String(50), nullable=False)
    
    # Processing results
    input_processed = Column(Text)
    output_generated = Column(Text)
    insights = Column(JSON)  # List of insights
    questions_generated = Column(JSON)  # List of questions
    confidence_score = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    cycle = relationship("PerpetualCycle", back_populates="think_tank_results")
    
    # Indexes
    __table_args__ = (
        Index('idx_perpetual_think_tank_cycle', 'cycle_id'),
        Index('idx_perpetual_think_tank_name', 'think_tank_name'),
        Index('idx_perpetual_think_tank_phase', 'phase'),
    )

class BreakthroughMoment(Base):
    """Records breakthrough moments in perpetual thinking"""
    __tablename__ = 'breakthrough_moments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_thinking_sessions.id'), nullable=False)
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_cycles.id'))
    
    # Breakthrough details
    breakthrough_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    significance_score = Column(Float, default=0.0)
    insights = Column(JSON)  # List of insights
    implications = Column(JSON)  # List of implications
    
    # Timestamps
    occurred_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    session = relationship("PerpetualThinkingSession", back_populates="breakthrough_moments")
    
    # Indexes
    __table_args__ = (
        Index('idx_breakthrough_session', 'session_id'),
        Index('idx_breakthrough_cycle', 'cycle_id'),
        Index('idx_breakthrough_type', 'breakthrough_type'),
        Index('idx_breakthrough_occurred', 'occurred_at'),
    )

class HumanFeedbackPoint(Base):
    """Records human feedback points in perpetual thinking"""
    __tablename__ = 'human_feedback_points'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_thinking_sessions.id'), nullable=False)
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_cycles.id'))
    
    # Feedback details
    feedback_type = Column(String(50), nullable=False)  # 'guidance', 'correction', 'validation', 'inspiration'
    feedback_content = Column(Text, nullable=False)
    human_identifier = Column(String(255))  # Optional human identifier
    impact_score = Column(Float, default=0.0)
    
    # Timestamps
    provided_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    session = relationship("PerpetualThinkingSession", back_populates="human_feedback_points")
    
    # Indexes
    __table_args__ = (
        Index('idx_human_feedback_session', 'session_id'),
        Index('idx_human_feedback_cycle', 'cycle_id'),
        Index('idx_human_feedback_type', 'feedback_type'),
        Index('idx_human_feedback_provided', 'provided_at'),
    )

class MetaCycle(Base):
    """Represents meta-cycles for system evolution"""
    __tablename__ = 'meta_cycles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_thinking_sessions.id'), nullable=False)
    
    # Meta-cycle details
    meta_cycle_type = Column(String(50), nullable=False)  # MetaCycleType
    status = Column(String(20), default='running')
    analysis_scope = Column(String(50))  # 'recent', 'session', 'global'
    
    # Analysis results
    patterns_identified = Column(JSON)  # List of patterns
    optimizations_suggested = Column(JSON)  # List of optimizations
    adaptations_made = Column(JSON)  # List of adaptations
    evolution_insights = Column(JSON)  # List of evolution insights
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    duration = Column(Float)  # Duration in seconds
    
    # Relationships
    session = relationship("PerpetualThinkingSession", back_populates="meta_cycles")
    
    # Indexes
    __table_args__ = (
        Index('idx_meta_cycle_session', 'session_id'),
        Index('idx_meta_cycle_type', 'meta_cycle_type'),
        Index('idx_meta_cycle_status', 'status'),
        Index('idx_meta_cycle_started', 'started_at'),
    )

class PerpetualSystemMetrics(Base):
    """System-wide metrics for perpetual thinking"""
    __tablename__ = 'perpetual_system_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metrics data
    total_sessions = Column(Integer, default=0)
    total_cycles = Column(Integer, default=0)
    total_breakthroughs = Column(Integer, default=0)
    avg_cycle_duration = Column(Float, default=0.0)
    avg_confidence_score = Column(Float, default=0.0)
    system_uptime = Column(Float, default=0.0)
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_perpetual_system_metrics_recorded', 'recorded_at'),
    )

class PerpetualPatternHistory(Base):
    """History of patterns detected in perpetual thinking"""
    __tablename__ = 'perpetual_pattern_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_thinking_sessions.id'))
    cycle_id = Column(UUID(as_uuid=True), ForeignKey('perpetual_cycles.id'))
    
    # Pattern details
    pattern_type = Column(String(50), nullable=False)  # PatternType
    pattern_description = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.0)
    frequency = Column(Integer, default=1)
    
    # Timestamps
    first_detected = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_detected = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    session = relationship("PerpetualThinkingSession")
    
    # Indexes
    __table_args__ = (
        Index('idx_perpetual_pattern_session', 'session_id'),
        Index('idx_perpetual_pattern_cycle', 'cycle_id'),
        Index('idx_perpetual_pattern_type', 'pattern_type'),
        Index('idx_perpetual_pattern_first', 'first_detected'),
    )
