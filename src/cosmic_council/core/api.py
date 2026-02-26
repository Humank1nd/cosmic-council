"""
Cosmic Council REST API Server
Comprehensive API endpoints for problem submission, cycle execution, and result retrieval
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from contextlib import asynccontextmanager
import os
import inspect
from types import SimpleNamespace

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
from pydantic import BaseModel, Field, field_validator
import uvicorn
import time
import json

# Import our existing components
from .core import ProblemStatement, ProblemComplexity, EnterpriseType
from ..workflows.problem_solving_workflow import ProblemSolvingWorkflow, WorkflowStep
from ..agents.unified_ai_agent_system import LLMConfig, LLMProvider, LLMModel, UnifiedCosmicCouncilAgent, AgentType
from ..workflows.ai_enhanced_workflow import AIEnhancedProblemSolvingWorkflow, AIWorkflowConfig
from ..database.unified_database_service import (
    UnifiedDatabaseService,
    Problem, Solution, Cycle, Enterprise, EnterpriseResult, User, Stakeholder,
    Constraint, SuccessCriterion, SolutionComponent, ImplementationTracking,
    CycleAnalytics, SystemMetrics, AuditLog,
    # ROYGBV workflow models (detailed)
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement
)
from ..database.unified_database_manager import get_database_manager
# Import SQLAlchemy models from core.models for repository operations
from ..core.models import (
    Problem as ProblemModel, 
    Cycle as CycleModel,
    Solution as SolutionModel,
    WorkflowSession as WorkflowSessionModel,
    WorkflowStep as WorkflowStepModel,
    AuditLog as AuditLogModel, 
    SystemMetrics as SystemMetricsModel,
    Base
)
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

# Configure comprehensive logging
from ..utils.logging_config import setup_logging, get_logger, log_request, log_response, log_performance, log_error, log_audit

# Setup logging with file rotation
setup_logging(
    log_level="INFO",
    log_file="logs/cosmic_council.log",
    use_json=False,  # Use structured format for readability
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5
)

logger = get_logger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Simple repository wrappers for backward compatibility
class ProblemRepository:
    """Simple repository wrapper for problem operations"""
    
    @staticmethod
    def create_problem(title: str, description: str, domain: str, complexity: str, 
                      priority: str = "medium", due_date: Optional[datetime] = None) -> ProblemModel:
        """Create a new problem"""
        db_manager = get_database_manager()
        # Use sync session for now
        try:
            with db_manager.get_session() as session:
                problem = ProblemModel(
                    id=uuid.uuid4(),
                    title=title,
                    description=description,
                    domain=domain,
                    complexity=complexity,
                    priority=priority,
                    status="active",
                    due_date=due_date,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                session.add(problem)
                session.commit()
                # Refresh before returning (while still in session context)
                session.refresh(problem)
                # Expunge to detach from session so it can be used outside
                session.expunge(problem)
                return problem
        except Exception as e:
            # If table doesn't exist, log error and raise
            if "no such table" in str(e).lower():
                logger.error("Problem table not found. Tables need to be created on server startup.")
                raise HTTPException(
                    status_code=500,
                    detail="Database tables not initialized. Please restart the server to create tables."
                )
            raise
    
    @staticmethod
    def get_problems(domain: Optional[str] = None, complexity: Optional[str] = None,
                    status: Optional[str] = None, limit: int = 100, offset: int = 0,
                    sort_by: Optional[str] = None, sort_order: str = "desc") -> Tuple[List[ProblemModel], int]:
        """Get problems with filtering"""
        db_manager = get_database_manager()
        with db_manager.get_session() as session:
            base_query = session.query(ProblemModel)
            if domain:
                base_query = base_query.filter(ProblemModel.domain == domain)
            if complexity:
                base_query = base_query.filter(ProblemModel.complexity == complexity)
            if status:
                base_query = base_query.filter(ProblemModel.status == status)

            total_count = base_query.count()

            query = base_query.options(
                selectinload(ProblemModel.stakeholders),
                selectinload(ProblemModel.constraints),
                selectinload(ProblemModel.success_criteria),
                selectinload(ProblemModel.cycles),
                selectinload(ProblemModel.solutions)
            )

            sort_fields = {
                "title": ProblemModel.title,
                "created_at": ProblemModel.created_at,
                "updated_at": ProblemModel.updated_at,
                "domain": ProblemModel.domain,
                "complexity": ProblemModel.complexity,
                "status": ProblemModel.status,
                "priority": ProblemModel.priority,
            }
            if sort_by:
                sort_column = sort_fields.get(sort_by)
                if sort_column is not None:
                    sort_order_value = (sort_order or "").lower()
                    if sort_order_value == "asc":
                        query = query.order_by(sort_column.asc())
                    else:
                        query = query.order_by(sort_column.desc())

            problems = query.limit(limit).offset(offset).all()
            for problem in problems:
                session.expunge(problem)
            return problems, total_count

    @staticmethod
    def get_problem(problem_id: uuid.UUID) -> Optional[ProblemModel]:
        """Get a problem by ID"""
        db_manager = get_database_manager()
        with db_manager.get_session() as session:
            problem = (
                session.query(ProblemModel)
                .options(
                    selectinload(ProblemModel.stakeholders),
                    selectinload(ProblemModel.constraints),
                    selectinload(ProblemModel.success_criteria),
                    selectinload(ProblemModel.cycles),
                    selectinload(ProblemModel.solutions)
                )
                .filter(ProblemModel.id == problem_id)
                .first()
            )
            if problem:
                session.expunge(problem)
            return problem
    
    @staticmethod
    def update_problem(problem_id: uuid.UUID, **kwargs) -> Optional[ProblemModel]:
        """Update a problem"""
        db_manager = get_database_manager()
        with db_manager.get_session() as session:
            problem = session.query(ProblemModel).filter(ProblemModel.id == problem_id).first()
            if problem:
                for key, value in kwargs.items():
                    if hasattr(problem, key) and value is not None:
                        setattr(problem, key, value)
                problem.updated_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(problem)
                session.expunge(problem)
            return problem

class CycleRepository:
    """Simple repository wrapper for cycle operations"""

    @staticmethod
    def create_cycle(problem_id: uuid.UUID, cycle_number: int, max_iterations: int = 3,
                     status: str = "pending") -> CycleModel:
        """Create a new cycle"""
        db_manager = get_database_manager()
        with db_manager.get_session() as session:
            cycle = CycleModel(
                id=uuid.uuid4(),
                problem_id=problem_id,
                cycle_number=cycle_number,
                status=status,
                started_at=datetime.now(timezone.utc),
                overall_confidence=0.0,
                total_duration=0.0
            )
            session.add(cycle)
            session.commit()
            session.refresh(cycle)
            session.expunge(cycle)
            return cycle

    @staticmethod
    def get_cycle(cycle_id: uuid.UUID) -> Optional[CycleModel]:
        """Get a cycle by ID"""
        db_manager = get_database_manager()
        with db_manager.get_session() as session:
            cycle = (
                session.query(CycleModel)
                .options(selectinload(CycleModel.enterprise_results))
                .filter(CycleModel.id == cycle_id)
                .first()
            )
            if cycle:
                session.expunge(cycle)
            return cycle

    @staticmethod
    def update_cycle_status(cycle_id: uuid.UUID, status: str, **kwargs) -> Optional[CycleModel]:
        """Update cycle status and optional metadata"""
        db_manager = get_database_manager()
        with db_manager.get_session() as session:
            cycle = session.query(CycleModel).filter(CycleModel.id == cycle_id).first()
            if not cycle:
                return None
            cycle.status = status
            # Optional metadata updates
            for key, value in kwargs.items():
                if value is None:
                    continue
                if hasattr(cycle, key):
                    setattr(cycle, key, value)
            if status == "completed" and not cycle.completed_at:
                cycle.completed_at = kwargs.get("completed_at", datetime.now(timezone.utc))
            session.commit()
            session.refresh(cycle)
            session.expunge(cycle)
            return cycle

class AuditLogRepository:
    """Simple repository wrapper for audit log operations"""
    
    @staticmethod
    def log_action(action: str, resource_type: str, resource_id: Any, 
                  user_id: str, old_values: Optional[Dict] = None, 
                  new_values: Optional[Dict] = None):
        """Log an audit action"""
        def _coerce_uuid(value: Any) -> Optional[uuid.UUID]:
            if isinstance(value, uuid.UUID):
                return value
            if value in (None, "", "anonymous"):
                return None
            try:
                return uuid.UUID(str(value))
            except Exception:
                return None

        def _json_safe(value: Any) -> Any:
            try:
                return json.loads(json.dumps(value, default=str))
            except Exception:
                return {"repr": repr(value)}

        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                parsed_user_id = _coerce_uuid(user_id)
                parsed_resource_id = _coerce_uuid(resource_id)
                audit_log = AuditLogModel(
                    id=uuid.uuid4(),
                    action=action,
                    resource_type=resource_type,
                    resource_id=parsed_resource_id,
                    user_id=parsed_user_id,
                    details={
                        "old_values": _json_safe(old_values or {}),
                        "new_values": _json_safe(new_values or {}),
                        "raw_resource_id": str(resource_id) if resource_id is not None else None,
                        "raw_user_id": str(user_id) if user_id is not None else None,
                    },
                    created_at=datetime.now(timezone.utc),
                )
                session.add(audit_log)
                session.commit()
        except Exception as e:
            logger.warning(f"Failed to log audit action: {e}")

class SystemMetricsRepository:
    """Simple repository wrapper for system metrics"""
    
    @staticmethod
    def record_metric(metric_name: str, metric_type: str, metric_value: float, tags: List[str]):
        """Record a system metric"""
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                metric = SystemMetricsModel(
                    id=uuid.uuid4(),
                    metric_name=metric_name,
                    metric_type=metric_type,
                    metric_value=metric_value,
                    tags=tags,
                    timestamp=datetime.now(timezone.utc)
                )
                session.add(metric)
                session.commit()
        except Exception as e:
            logger.warning(f"Failed to record metric: {e}")

class EnterpriseRepository:
    """Simple repository wrapper for enterprise operations"""
    
    @staticmethod
    def get_all_enterprises() -> List[SimpleNamespace]:
        """Get all enterprises"""
        enterprise_definitions = [
            ("Red Owl", EnterpriseType.RED_OWL, "Research and discovery enterprise", "#FF0000", "owl", "Curiosity", ["research", "analysis"]),
            ("Orange Orangutan", EnterpriseType.ORANGE_ORANGUTAN, "Planning and strategy enterprise", "#FFA500", "orangutan", "Planning", ["planning", "strategy"]),
            ("Yellow Honeybee", EnterpriseType.YELLOW_HONEYBEE, "Development and innovation enterprise", "#FFFF00", "honeybee", "Creativity", ["development", "innovation"]),
            ("Green Tortoise", EnterpriseType.GREEN_TORTOISE, "Testing and sustainability enterprise", "#008000", "tortoise", "Sustainability", ["testing", "stability"]),
            ("Blue Dolphin", EnterpriseType.BLUE_DOLPHIN, "Communication and delivery enterprise", "#0000FF", "dolphin", "Clarity", ["communication", "delivery"]),
            ("Purple Elephant", EnterpriseType.PURPLE_ELEPHANT, "Support and improvement enterprise", "#4B0082", "elephant", "Empathy", ["support", "improvement"]),
        ]

        enterprises = []
        for index, (name, enterprise_type, description, color, symbol, core_principle, expertise_areas) in enumerate(enterprise_definitions):
            enterprises.append(SimpleNamespace(
                id=enterprise_type.value,
                name=name,
                type=enterprise_type.value,
                description=description,
                color=color,
                symbol=symbol,
                core_principle=core_principle,
                expertise_areas=expertise_areas,
                processing_order=index,
                is_active=True
            ))
        return enterprises

class EnterpriseResultRepository:
    """Simple repository wrapper for enterprise result operations"""
    
    @staticmethod
    def create_enterprise_result(cycle_id: uuid.UUID, enterprise_id: str, status: str, **kwargs) -> Dict[str, Any]:
        """Create an enterprise result"""
        # This is a stub - implement with actual database query if needed
        result = {
            "id": uuid.uuid4(),
            "cycle_id": cycle_id,
            "enterprise_id": enterprise_id,
            "status": status,
            **kwargs
        }
        return result
    
    @staticmethod
    def update_enterprise_result(result_id: uuid.UUID, **kwargs) -> None:
        """Update an enterprise result"""
        # This is a stub - implement with actual database query if needed
        logger.debug(f"Updating enterprise result {result_id} with {kwargs}")

class SolutionRepository:
    """Simple repository wrapper for solution operations"""

    @staticmethod
    def create_solution(problem_id: uuid.UUID, cycle_id: uuid.UUID, title: str,
                       description: str, status: str = "draft", solution_type: str = "primary",
                       confidence_score: Optional[float] = None, feasibility_score: Optional[float] = None,
                       impact_score: Optional[float] = None, **kwargs) -> SolutionModel:
        """Create a solution record"""
        db_manager = get_database_manager()
        with db_manager.get_session() as session:
            solution = SolutionModel(
                id=uuid.uuid4(),
                problem_id=problem_id,
                title=title,
                description=description,
                solution_type=solution_type,
                status=status,
                confidence_score=confidence_score or 0.0,
                feasibility_score=feasibility_score or 0.0,
                impact_score=impact_score or 0.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(solution)
            session.commit()
            session.refresh(solution)
            session.expunge(solution)
            return solution

    @staticmethod
    def get_solutions_for_problem(problem_id: uuid.UUID) -> List[SolutionModel]:
        """Get all solutions for a problem"""
        db_manager = get_database_manager()
        with db_manager.get_session() as session:
            solutions = session.query(SolutionModel).filter(SolutionModel.problem_id == problem_id).all()
            for solution in solutions:
                session.expunge(solution)
            return solutions

class AnalyticsRepository:
    """Simple repository wrapper for analytics"""
    
    @staticmethod
    def get_problem_statistics() -> Dict[str, Any]:
        """Get problem statistics"""
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                total = session.query(ProblemModel).count()
                # Status counts
                status_counts = session.query(
                    ProblemModel.status,
                    func.count(ProblemModel.id).label("count")
                ).group_by(ProblemModel.status).all()
                by_status = {status if status else "unknown": count for status, count in status_counts}

                # Complexity counts
                complexity_counts = session.query(
                    ProblemModel.complexity,
                    func.count(ProblemModel.id).label("count")
                ).group_by(ProblemModel.complexity).all()
                by_complexity = {complexity if complexity else "unknown": count for complexity, count in complexity_counts}

                # Domain counts
                domain_counts = session.query(
                    ProblemModel.domain,
                    func.count(ProblemModel.id).label("count")
                ).group_by(ProblemModel.domain).all()
                by_domain = {domain if domain else "unknown": count for domain, count in domain_counts}

                completed_count = session.query(ProblemModel).filter(ProblemModel.status == "completed").count()
                success_rate = round((completed_count / total * 100) if total > 0 else 0.0, 2)

                return {
                    "total_problems": total,
                    "by_status": by_status,
                    "by_complexity": by_complexity,
                    "by_domain": by_domain,
                    "success_rate": success_rate
                }
        except Exception as e:
            logger.warning(f"Failed to get problem statistics: {e}")
        return {
            "total_problems": 0,
            "by_status": {},
            "by_complexity": {},
            "by_domain": {},
            "success_rate": 0.0
        }
    
    @staticmethod
    def get_solution_statistics() -> Dict[str, Any]:
        """Get solution statistics and analytics"""
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                # Total solutions
                total = session.query(SolutionModel).count()

                # Solutions by status
                status_counts = session.query(
                    SolutionModel.status,
                    func.count(SolutionModel.id).label('count')
                ).group_by(SolutionModel.status).all()
                by_status = {status if status else "unknown": count for status, count in status_counts}

                # Average scores
                avg_confidence = session.query(func.avg(SolutionModel.confidence_score)).scalar() or 0.0
                avg_feasibility = session.query(func.avg(SolutionModel.feasibility_score)).scalar() or 0.0
                avg_impact = session.query(func.avg(SolutionModel.impact_score)).scalar() or 0.0

                # Solutions by type
                type_counts = session.query(
                    SolutionModel.solution_type,
                    func.count(SolutionModel.id).label('count')
                ).group_by(SolutionModel.solution_type).all()
                by_type = {sol_type if sol_type else "unknown": count for sol_type, count in type_counts}

                # Recent solutions (last 30 days)
                from datetime import timedelta
                thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
                recent_count = session.query(SolutionModel).filter(
                    SolutionModel.created_at >= thirty_days_ago
                ).count()

                # High confidence solutions (confidence > 0.7)
                high_confidence_count = session.query(SolutionModel).filter(
                    SolutionModel.confidence_score > 0.7
                ).count()

                return {
                    "total_solutions": total,
                    "by_status": by_status,
                    "by_type": by_type,
                    "average_scores": {
                        "confidence": round(float(avg_confidence), 2),
                        "feasibility": round(float(avg_feasibility), 2),
                        "impact": round(float(avg_impact), 2)
                    },
                    # Duplicate flat fields for callers that expect non-nested averages
                    "average_confidence": round(float(avg_confidence), 2),
                    "average_feasibility": round(float(avg_feasibility), 2),
                    "average_impact": round(float(avg_impact), 2),
                    "recent_solutions_30_days": recent_count,
                    "high_confidence_solutions": high_confidence_count,
                    "high_confidence_percentage": round((high_confidence_count / total * 100) if total > 0 else 0, 2)
                }
        except Exception as e:
            logger.warning(f"Failed to get solution statistics: {e}")
            return {
                "total_solutions": 0,
                "by_status": {},
                "by_type": {},
                "average_scores": {
                    "confidence": 0.0,
                    "feasibility": 0.0,
                    "impact": 0.0
                },
                "recent_solutions_30_days": 0,
                "high_confidence_solutions": 0,
                "high_confidence_percentage": 0.0,
                "average_confidence": 0.0,
                "average_feasibility": 0.0,
                "average_impact": 0.0
            }

    @staticmethod
    def get_cycle_statistics() -> Dict[str, Any]:
        """Get cycle statistics and analytics"""
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                total = session.query(CycleModel).count()
                status_counts = session.query(
                    CycleModel.status,
                    func.count(CycleModel.id).label("count")
                ).group_by(CycleModel.status).all()
                by_status = {status if status else "unknown": count for status, count in status_counts}

                avg_duration = session.query(func.avg(CycleModel.total_duration)).scalar() or 0.0
                avg_confidence = session.query(func.avg(CycleModel.overall_confidence)).scalar() or 0.0
                completed_count = session.query(CycleModel).filter(CycleModel.status == "completed").count()
                success_rate = round((completed_count / total * 100) if total > 0 else 0.0, 2)

                from datetime import timedelta
                recent_threshold = datetime.now(timezone.utc) - timedelta(days=30)
                recent_cycles = session.query(CycleModel).filter(CycleModel.started_at >= recent_threshold).count()

                return {
                    "total_cycles": total,
                    "by_status": by_status,
                    "average_duration": round(float(avg_duration), 2),
                    "average_confidence": round(float(avg_confidence), 2),
                    "success_rate": success_rate,
                    "recent_cycles_30_days": recent_cycles
                }
        except Exception as e:
            logger.warning(f"Failed to get cycle statistics: {e}")
            return {
                "total_cycles": 0,
                "by_status": {},
                "average_duration": 0.0,
                "average_confidence": 0.0,
                "success_rate": 0.0,
                "recent_cycles_30_days": 0
            }
    
    @staticmethod
    def get_time_series_analytics(
        resource_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "day"
    ) -> Dict[str, Any]:
        """Get time-series analytics for problems, cycles, or solutions"""
        from datetime import timedelta
        from sqlalchemy import extract, case
        
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                # Default to last 30 days if not specified
                if not end_date:
                    end_date = datetime.now(timezone.utc)
                if not start_date:
                    start_date = end_date - timedelta(days=30)
                
                # Determine which model to query
                if resource_type == "problems":
                    model = ProblemModel
                    date_field = ProblemModel.created_at
                elif resource_type == "cycles":
                    model = CycleModel
                    date_field = CycleModel.started_at
                elif resource_type == "solutions":
                    model = SolutionModel
                    date_field = SolutionModel.created_at
                else:
                    return {"error": f"Invalid resource_type: {resource_type}"}
                
                # Build query based on interval (SQLite compatible)
                if interval == "day":
                    date_expr = func.date(date_field)
                elif interval == "week":
                    # SQLite: use strftime to get year-week
                    date_expr = func.strftime('%Y-W%W', date_field)
                elif interval == "month":
                    # SQLite: use strftime to get year-month
                    date_expr = func.strftime('%Y-%m', date_field)
                else:
                    date_expr = func.date(date_field)
                
                # Query time-series data
                time_series = session.query(
                    date_expr.label("period"),
                    func.count(model.id).label("count")
                ).filter(
                    date_field >= start_date,
                    date_field <= end_date
                ).group_by(date_expr).order_by(date_expr).all()
                
                # Format results
                series_data = [
                    {
                        "period": period.isoformat() if hasattr(period, 'isoformat') else str(period),
                        "count": count
                    }
                    for period, count in time_series
                ]
                
                return {
                    "resource_type": resource_type,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "interval": interval,
                    "data": series_data,
                    "total": sum(count for _, count in time_series)
                }
        except Exception as e:
            logger.warning(f"Failed to get time-series analytics: {e}")
            return {
                "resource_type": resource_type,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "interval": interval,
                "data": [],
                "total": 0
            }
    
    @staticmethod
    def get_comparative_analytics(
        resource_type: str,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime
    ) -> Dict[str, Any]:
        """Get comparative analytics between two periods"""
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                # Determine which model to query
                if resource_type == "problems":
                    model = ProblemModel
                    date_field = ProblemModel.created_at
                elif resource_type == "cycles":
                    model = CycleModel
                    date_field = CycleModel.started_at
                elif resource_type == "solutions":
                    model = SolutionModel
                    date_field = SolutionModel.created_at
                else:
                    return {"error": f"Invalid resource_type: {resource_type}"}
                
                # Period 1 stats
                period1_count = session.query(model).filter(
                    date_field >= period1_start,
                    date_field <= period1_end
                ).count()
                
                # Period 2 stats
                period2_count = session.query(model).filter(
                    date_field >= period2_start,
                    date_field <= period2_end
                ).count()
                
                # Calculate change
                change = period2_count - period1_count
                change_percentage = round((change / period1_count * 100) if period1_count > 0 else 0, 2)
                
                return {
                    "resource_type": resource_type,
                    "period1": {
                        "start": period1_start.isoformat(),
                        "end": period1_end.isoformat(),
                        "count": period1_count
                    },
                    "period2": {
                        "start": period2_start.isoformat(),
                        "end": period2_end.isoformat(),
                        "count": period2_count
                    },
                    "comparison": {
                        "change": change,
                        "change_percentage": change_percentage,
                        "trend": "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
                    }
                }
        except Exception as e:
            logger.warning(f"Failed to get comparative analytics: {e}")
            return {
                "resource_type": resource_type,
                "period1": {"count": 0},
                "period2": {"count": 0},
                "comparison": {"change": 0, "change_percentage": 0, "trend": "stable"}
            }
    
    @staticmethod
    def get_aggregated_analytics(
        resource_type: str,
        group_by: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get aggregated analytics grouped by specified field"""
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                # Determine which model to query
                if resource_type == "problems":
                    model = ProblemModel
                elif resource_type == "cycles":
                    model = CycleModel
                elif resource_type == "solutions":
                    model = SolutionModel
                else:
                    return {"error": f"Invalid resource_type: {resource_type}"}
                
                # Build query
                query = session.query(model)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if hasattr(model, key):
                            query = query.filter(getattr(model, key) == value)
                
                # Group by specified field
                if hasattr(model, group_by):
                    group_field = getattr(model, group_by)
                    aggregated = session.query(
                        group_field,
                        func.count(model.id).label("count")
                    )
                    
                    # Apply same filters
                    if filters:
                        for key, value in filters.items():
                            if hasattr(model, key):
                                aggregated = aggregated.filter(getattr(model, key) == value)
                    
                    results = aggregated.group_by(group_field).all()
                    
                    return {
                        "resource_type": resource_type,
                        "group_by": group_by,
                        "filters": filters or {},
                        "data": [
                            {
                                "key": str(key) if key else "unknown",
                                "count": count
                            }
                            for key, count in results
                        ],
                        "total": sum(count for _, count in results)
                    }
                else:
                    return {"error": f"Invalid group_by field: {group_by}"}
        except Exception as e:
            logger.warning(f"Failed to get aggregated analytics: {e}")
            return {
                "resource_type": resource_type,
                "group_by": group_by,
                "filters": filters or {},
                "data": [],
                "total": 0
            }
    
    @staticmethod
    def get_visualization_data(
        resource_type: str,
        chart_type: str = "bar"
    ) -> Dict[str, Any]:
        """Get data formatted for visualization"""
        try:
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                if resource_type == "problems":
                    model = ProblemModel
                    # Get status distribution
                    status_data = session.query(
                        ProblemModel.status,
                        func.count(ProblemModel.id).label("count")
                    ).group_by(ProblemModel.status).all()
                    
                    # Get complexity distribution
                    complexity_data = session.query(
                        ProblemModel.complexity,
                        func.count(ProblemModel.id).label("count")
                    ).group_by(ProblemModel.complexity).all()
                    
                    return {
                        "chart_type": chart_type,
                        "datasets": [
                            {
                                "label": "Status Distribution",
                                "data": [{"x": status or "unknown", "y": count} for status, count in status_data]
                            },
                            {
                                "label": "Complexity Distribution",
                                "data": [{"x": complexity or "unknown", "y": count} for complexity, count in complexity_data]
                            }
                        ]
                    }
                elif resource_type == "solutions":
                    model = SolutionModel
                    # Get score distributions
                    score_ranges = [
                        (0.0, 0.2, "0-0.2"),
                        (0.2, 0.4, "0.2-0.4"),
                        (0.4, 0.6, "0.4-0.6"),
                        (0.6, 0.8, "0.6-0.8"),
                        (0.8, 1.0, "0.8-1.0")
                    ]
                    
                    confidence_data = []
                    for min_val, max_val, label in score_ranges:
                        count = session.query(SolutionModel).filter(
                            SolutionModel.confidence_score >= min_val,
                            SolutionModel.confidence_score < max_val
                        ).count()
                        confidence_data.append({"x": label, "y": count})
                    
                    return {
                        "chart_type": chart_type,
                        "datasets": [
                            {
                                "label": "Confidence Score Distribution",
                                "data": confidence_data
                            }
                        ]
                    }
                elif resource_type == "cycles":
                    model = CycleModel
                    # Get status distribution
                    status_data = session.query(
                        CycleModel.status,
                        func.count(CycleModel.id).label("count")
                    ).group_by(CycleModel.status).all()
                    
                    return {
                        "chart_type": chart_type,
                        "datasets": [
                            {
                                "label": "Cycle Status Distribution",
                                "data": [{"x": status or "unknown", "y": count} for status, count in status_data]
                            }
                        ]
                    }
                else:
                    return {"error": f"Invalid resource_type: {resource_type}"}
        except Exception as e:
            logger.warning(f"Failed to get visualization data: {e}")
            return {
                "chart_type": chart_type,
                "datasets": []
            }


class SimplePerpetualEngine:
    """Lightweight session tracker backing the perpetual thinking endpoints"""

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.breakthroughs: Dict[str, List[Dict[str, Any]]] = {}
        self.metrics: Dict[str, int] = {
            "total_sessions": 0,
            "active_sessions": 0,
            "completed_sessions": 0,
            "total_cycles": 0
        }

    def create_session_record(
        self,
        session_id: str,
        session_name: str,
        initial_input: str,
        mode: str,
        goals: List[str],
        success_criteria: List[str],
        ai_enhancement_level: "AIEnhancementLevel",
        ai_learning_enabled: bool,
        ai_adaptation_enabled: bool,
        ai_breakthrough_detection: bool
    ) -> Dict[str, Any]:
        """Create or refresh a session record"""
        session = {
            "session_id": session_id,
            "session_name": session_name,
            "initial_input": initial_input,
            "current_input": initial_input,
            "current_cycle_number": 1,
            "status": "active",
            "mode": mode,
            "goals": goals,
            "success_criteria": success_criteria,
            "ai_enhancement_level": ai_enhancement_level.value,
            "ai_learning_enabled": ai_learning_enabled,
            "ai_adaptation_enabled": ai_adaptation_enabled,
            "ai_breakthrough_detection": ai_breakthrough_detection,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "summary_metrics": {
                "cycles": 1,
                "breakthroughs": 0,
                "confidence_score": 0.0
            },
            "cycles": [],
            "breakthroughs": [],
            "notes": []
        }
        self.sessions[session_id] = session
        self.metrics["total_sessions"] = len(self.sessions)
        self.metrics["active_sessions"] = len(
            [acct for acct in self.sessions.values() if acct["status"] == "active"]
        )
        return session

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def add_cycle(self, session_id: str, cycle_payload: Dict[str, Any]):
        session = self.sessions.get(session_id)
        if not session:
            return
        session["cycles"].append(cycle_payload)
        session["current_cycle_number"] = len(session["cycles"]) + 1
        session["summary_metrics"]["cycles"] = len(session["cycles"])
        self.metrics["total_cycles"] = sum(len(s["cycles"]) for s in self.sessions.values())

    def add_breakthrough(self, session_id: str, result: Dict[str, Any]):
        self.breakthroughs.setdefault(session_id, []).append(result)
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session["breakthroughs"].append(result)
            session["summary_metrics"]["breakthroughs"] = len(session["breakthroughs"])

    def update_status(self, session_id: str, status: str):
        session = self.sessions.get(session_id)
        if not session:
            return
        session["status"] = status
        session["updated_at"] = datetime.now(timezone.utc)
        if status == "completed":
            self.metrics["completed_sessions"] += 1

    def get_breakthrough_moments(self, session_id: str) -> List[Dict[str, Any]]:
        return self.breakthroughs.get(session_id, [])

    def get_system_metrics(self) -> Dict[str, Any]:
        return {
            "total_sessions": self.metrics["total_sessions"],
            "active_sessions": self.metrics["active_sessions"],
            "completed_sessions": self.metrics["completed_sessions"],
            "total_cycles": self.metrics["total_cycles"]
        }


class SimpleAIEnhancedPerpetualEngine:
    """Minimal AI-enhanced engine to meet API expectations"""

    def __init__(self, session_engine: SimplePerpetualEngine, orchestration_system: 'SimpleOrchestrationSystem'):
        self.session_engine = session_engine
        self.orchestration_system = orchestration_system
        self.ai_sessions: Dict[str, Dict[str, Any]] = {}

    async def start_ai_enhanced_perpetual_cycle(
        self,
        session_name: str,
        initial_input: str,
        mode: str,
        goals: List[str],
        success_criteria: List[str],
        ai_enhancement_level: "AIEnhancementLevel",
        ai_learning_enabled: bool,
        ai_adaptation_enabled: bool,
        ai_breakthrough_detection: bool,
        cycle_type: "CycleType",
        max_cycles: Optional[int] = None
    ) -> str:
        session_id = str(uuid.uuid4())
        session_record = self.session_engine.create_session_record(
            session_id=session_id,
            session_name=session_name,
            initial_input=initial_input,
            mode=mode,
            goals=goals,
            success_criteria=success_criteria,
            ai_enhancement_level=ai_enhancement_level,
            ai_learning_enabled=ai_learning_enabled,
            ai_adaptation_enabled=ai_adaptation_enabled,
            ai_breakthrough_detection=ai_breakthrough_detection
        )

        self.ai_sessions[session_id] = {
            "session_id": session_id,
            "session_name": session_name,
            "initial_input": initial_input,
            "status": "active",
            "mode": mode,
            "current_cycle_number": 1,
            "ai_enhancement_level": ai_enhancement_level.value,
            "cycle_type": cycle_type.value,
            "max_cycles": max_cycles,
            "created_at": session_record["created_at"],
            "updated_at": session_record["updated_at"],
            "last_cycle_result": {},
            "insights": [],
            "confidence_score": 0.0
        }

        await self.orchestration_system.register_session(
            session_id=session_id,
            session_name=session_name,
            initial_input=initial_input,
            mode=mode,
            goals=goals,
            success_criteria=success_criteria,
            current_perpetual_session_id=session_id
        )

        return session_id

    async def get_ai_session_analytics(self, session_id: str) -> Dict[str, Any]:
        session = self.ai_sessions.get(session_id)
        if not session:
            return None
        return {
            "session_id": session_id,
            "ai_enhancement_level": session["ai_enhancement_level"],
            "current_cycle_number": session["current_cycle_number"],
            "confidence_score": session["confidence_score"],
            "insights": session["insights"],
            "last_cycle_result": session["last_cycle_result"]
        }

    async def get_ai_enhanced_cycle_status(self, session_id: str) -> Dict[str, Any]:
        session = self.ai_sessions.get(session_id)
        if not session:
            return None
        return {
            "session_id": session_id,
            "status": session["status"],
            "cycle_type": session["cycle_type"],
            "current_cycle_number": session["current_cycle_number"],
            "ai_enhancement_level": session["ai_enhancement_level"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }


class SimpleOrchestrationSystem:
    """Basic orchestration session tracker used by perpetual endpoints"""

    def __init__(self, perpetual_engine: SimplePerpetualEngine):
        self.perpetual_engine = perpetual_engine
        self.orchestration_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_history: List[Dict[str, Any]] = []

    async def register_session(
        self,
        session_id: str,
        session_name: str,
        initial_input: str,
        mode: str,
        goals: List[str],
        success_criteria: List[str],
        current_perpetual_session_id: str
    ):
        session = {
            "session_id": session_id,
            "session_name": session_name,
            "initial_input": initial_input,
            "current_input": initial_input,
            "current_cycle_number": 1,
            "status": "active",
            "mode": mode,
            "goals": goals,
            "success_criteria": success_criteria,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "summary_metrics": {
                "cycles": 1,
                "breakthroughs": 0
            },
            "current_perpetual_session_id": current_perpetual_session_id
        }
        self.orchestration_sessions[session_id] = session
        self.session_history.append(session)
        return session

    def get_orchestration_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.orchestration_sessions.get(session_id)

    async def pause_orchestration_session(self, session_id: str):
        session = self.orchestration_sessions.get(session_id)
        if session:
            session["status"] = "paused"
            session["updated_at"] = datetime.now(timezone.utc)

    async def resume_orchestration_session(self, session_id: str):
        session = self.orchestration_sessions.get(session_id)
        if session:
            session["status"] = "active"
            session["updated_at"] = datetime.now(timezone.utc)

    async def stop_orchestration_session(self, session_id: str):
        session = self.orchestration_sessions.get(session_id)
        if session:
            session["status"] = "completed"
            session["updated_at"] = datetime.now(timezone.utc)


class SimpleFractalSessionResult:
    """Minimal result container for fractal-perpetual sessions"""

    def __init__(
        self,
        session_id: str,
        fractal_result: Dict[str, Any],
        perpetual_result: Dict[str, Any],
        integration_insights: Dict[str, Any],
        cross_system_patterns: List[Dict[str, Any]],
        performance_metrics: Dict[str, Any],
        execution_time: float,
        success: bool,
        errors: List[str]
    ):
        self.session_id = session_id
        self.fractal_result = fractal_result
        self.perpetual_result = perpetual_result
        self.integration_insights = integration_insights
        self.cross_system_patterns = cross_system_patterns
        self.performance_metrics = performance_metrics
        self.execution_time = execution_time
        self.success = success
        self.errors = errors


class SimpleFractalPerpetualIntegration:
    """Lightweight fractal-perpetual integration helper"""

    def __init__(self):
        self.sessions: Dict[str, SimpleFractalSessionResult] = {}

    async def execute_integrated_session(self, session_name: str, initial_input: str, integration_mode: "PerpetualFractalMode", context: Dict[str, Any]):
        session_id = str(uuid.uuid4())
        result = SimpleFractalSessionResult(
            session_id=session_id,
            fractal_result={"session": session_name, "mode": integration_mode.value},
            perpetual_result={"initial_input": initial_input},
            integration_insights={"context": context},
            cross_system_patterns=[],
            performance_metrics={"execution_time": 0.0},
            execution_time=0.0,
            success=True,
            errors=[]
        )
        self.sessions[session_id] = result
        return result

    def get_integration_analytics(self) -> Dict[str, Any]:
        return {
            "total_sessions": len(self.sessions),
            "success_rate": (sum(1 for s in self.sessions.values() if s.success) / len(self.sessions)) if self.sessions else 0.0
        }

    def get_cross_system_insights(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        return session.integration_insights if session else None

    def get_integration_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if not session:
            return None
        return {
            "session_id": session_id,
            "status": "completed" if session.success else "failed",
            "execution_time": session.execution_time,
            "updated_at": datetime.now(timezone.utc)
        }


# Global variables for application state
workflow_engine: Optional[ProblemSolvingWorkflow] = None
ai_workflow_engine: Optional[AIEnhancedProblemSolvingWorkflow] = None
ai_integration: Optional[UnifiedCosmicCouncilAgent] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global workflow_engine, ai_workflow_engine, ai_integration
    global perpetual_engine, perpetual_ai_engine, orchestration_system, perpetual_db_service
    global perpetual_guardrail_integration, perpetual_policy_enforcer
    global fractal_108_cycle_system, perpetual_108_cycle_integration
    
    # Startup
    logger.info("Starting Cosmic Council API Server...")
    
    try:
        # Initialize database
        db_manager = get_database_manager()
        # Ensure tables are created
        try:
            await db_manager.create_tables()
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.warning(f"Could not create tables (may already exist): {e}")
        logger.info("Database initialized successfully")
        
        # Initialize workflow engine
        workflow_engine = ProblemSolvingWorkflow()
        logger.info("Workflow engine initialized")
        
        # Initialize agent interactions API
        try:
            from ..api.agent_interactions import initialize_agents, pre_warm_agent_list_cache
            from ..core.hexagon import CosmicCouncilHexagon
            council_instance = CosmicCouncilHexagon()
            initialize_agents(council_instance)
            logger.info("Agent interactions API initialized")
            
            # Pre-warm agent list cache for better performance
            try:
                pre_warm_agent_list_cache()
                logger.info("Agent list cache pre-warmed")
            except Exception as e:
                logger.warning(f"Failed to pre-warm agent list cache: {e}")
        except Exception as e:
            logger.warning(f"Failed to initialize agent interactions API: {e}")
        
        # Initialize AI integration
        ai_llm_config = LLMConfig(
            provider=LLMProvider.MOCK,
            model=LLMModel.GPT_4,
            temperature=0.7,
            max_tokens=2000
        )
        ai_workflow_config = AIWorkflowConfig(llm_config=ai_llm_config)
        ai_workflow_engine = AIEnhancedProblemSolvingWorkflow(ai_workflow_config)
        ai_integration = UnifiedCosmicCouncilAgent(AgentType.RED_OWL)
        logger.info("AI integration initialized")
        
        # Initialize perpetual thinking system
        try:
            # Initialize database service for perpetual system
            perpetual_db_service = PerpetualDatabaseService("sqlite+aiosqlite:///perpetual_thinking.db")
            await perpetual_db_service.create_tables()
            logger.info("Persistent perpetual thinking database prepared")

            # Initialize helper components for perpetual thinking
            perpetual_engine = SimplePerpetualEngine()
            orchestration_system = SimpleOrchestrationSystem(perpetual_engine)
            perpetual_ai_engine = SimpleAIEnhancedPerpetualEngine(perpetual_engine, orchestration_system)

            guardrail_policy_engine = PolicyEngine()
            perpetual_guardrail_integration = PerpetualGuardrailIntegration(
                policy_engine=guardrail_policy_engine,
                enable_audit_logging=True,
                enable_simulation_mode=True
            )
            perpetual_policy_enforcer = None

            fractal_108_cycle_system = Fractal108CycleSystem()
            perpetual_108_cycle_integration = SimpleFractalPerpetualIntegration()
            
            logger.info("AI-enhanced perpetual thinking system initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize perpetual thinking system: {e}")
            # Set to None to indicate system is not available
            perpetual_engine = None
            perpetual_ai_engine = None
            orchestration_system = None
            perpetual_db_service = None
            perpetual_guardrail_integration = None
            perpetual_policy_enforcer = None
            fractal_108_cycle_system = None
            perpetual_108_cycle_integration = None
        
        logger.info("AI integration and enhanced workflow initialized")
        logger.info("Cosmic Council API Server started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API server: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Cosmic Council API Server...")

# Create FastAPI application
app = FastAPI(
    title="Cosmic Council API",
    description="REST API for the Cosmic Council problem-solving framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Performance monitoring middleware
class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance with comprehensive logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        log_request(
            logger,
            request.method,
            str(request.url.path),
            query_params=dict(request.query_params),
            client_host=request.client.host if request.client else None
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error with context
            log_error(
                logger,
                e,
                context={
                    "method": request.method,
                    "path": str(request.url.path),
                    "client_host": request.client.host if request.client else None
                }
            )
            raise
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
        response.headers["X-Process-Time"] = f"{duration*1000:.2f}ms"
        
        # Log response and performance
        log_response(
            logger,
            request.method,
            str(request.url.path),
            response.status_code,
            duration
        )
        log_performance(
            logger,
            f"{request.method} {request.url.path}",
            duration
        )
        
        return response

app.add_middleware(PerformanceMonitoringMiddleware)

@app.options("/{path:path}")
async def options_handler(path: str) -> Response:
    """Handle generic CORS preflight requests."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

# Include agent interactions API router
try:
    from ..api.agent_interactions import router as agent_router
    app.include_router(agent_router)
    logger.info("Agent interactions API router included")
except Exception as e:
    logger.warning(f"Failed to include agent interactions router: {e}")

# Include visual identity API router
try:
    from ..api.visual_identity import router as visual_router
    app.include_router(visual_router)
    logger.info("Visual identity API router included")
except Exception as e:
    logger.warning(f"Failed to include visual identity router: {e}")

# Pydantic Models for API

class ProblemCreateRequest(BaseModel):
    """Request model for creating a problem"""
    title: str = Field(..., min_length=1, max_length=500, description="Problem title")
    description: str = Field(..., min_length=1, description="Problem description")
    domain: str = Field(..., min_length=1, max_length=200, description="Problem domain")
    complexity: str = Field(..., description="Problem complexity level")
    priority: str = Field(default="medium", description="Problem priority")
    stakeholders: List[str] = Field(default=[], description="List of stakeholders")
    constraints: Dict[str, Any] = Field(default={}, description="Problem constraints")
    success_criteria: List[str] = Field(default=[], description="Success criteria")
    due_date: Optional[datetime] = Field(default=None, description="Due date")
    
    @field_validator('complexity')
    def validate_complexity(cls, v):
        valid_complexities = ['simple', 'moderate', 'complex', 'systemic']
        if v not in valid_complexities:
            raise ValueError(f'Complexity must be one of: {valid_complexities}')
        return v

    @field_validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v

class ProblemUpdateRequest(BaseModel):
    """Request model for updating a problem"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    domain: Optional[str] = Field(None, min_length=1, max_length=200)
    complexity: Optional[str] = Field(None)
    priority: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    due_date: Optional[datetime] = Field(None)
    
    @field_validator('complexity')
    def validate_complexity(cls, v):
        if v is not None:
            valid_complexities = ['simple', 'moderate', 'complex', 'systemic']
            if v not in valid_complexities:
                raise ValueError(f'Complexity must be one of: {valid_complexities}')
        return v

    @field_validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            valid_priorities = ['low', 'medium', 'high', 'critical']
            if v not in valid_priorities:
                raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v

    @field_validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['active', 'in_progress', 'completed', 'archived']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {valid_statuses}')
        return v

class CycleCreateRequest(BaseModel):
    """Request model for creating a cycle"""
    problem_id: str = Field(..., description="Problem ID")
    cycle_number: int = Field(..., ge=1, description="Cycle number")
    max_iterations: int = Field(default=3, ge=1, le=10, description="Maximum iterations")

class WorkflowCreateRequest(BaseModel):
    """Request model for creating a workflow session"""
    problem_id: str = Field(..., description="Problem ID")
    session_type: str = Field(default="standard", description="Session type: standard, ai_enhanced, collaborative")
    user_preferences: Optional[Dict[str, Any]] = Field(default={}, description="User preferences")

class WorkflowStepRequest(BaseModel):
    """Request model for workflow step execution"""
    step_name: str = Field(..., description="Step name")
    user_inputs: Dict[str, Any] = Field(default={}, description="User inputs for the step")

class SolutionCreateRequest(BaseModel):
    """Request model for creating a solution"""
    problem_id: str = Field(..., description="Problem ID")
    cycle_id: str = Field(..., description="Cycle ID")
    title: str = Field(..., min_length=1, max_length=500, description="Solution title")
    description: str = Field(..., min_length=1, description="Solution description")
    approach: Optional[str] = Field(None, description="Solution approach")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    feasibility_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Feasibility score")
    impact_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Impact score")
    estimated_cost: Optional[float] = Field(None, ge=0.0, description="Estimated cost")
    estimated_duration: Optional[int] = Field(None, ge=1, description="Estimated duration in days")
    risk_level: Optional[str] = Field(None, description="Risk level")
    
class SolutionCreateWithCycleRequest(BaseModel):
    """Request model for creating a solution with automatic cycle execution"""
    problem_id: str = Field(..., description="Problem ID")
    title: str = Field(..., min_length=1, max_length=500, description="Solution title")
    description: str = Field(..., min_length=1, description="Solution description")
    approach: Optional[str] = Field(None, description="Solution approach")
    max_iterations: int = Field(default=1, ge=1, le=10, description="Maximum cycle iterations")
    def validate_risk_level(cls, v):
        if v is not None:
            valid_risk_levels = ['low', 'medium', 'high', 'critical']
            if v not in valid_risk_levels:
                raise ValueError(f'Risk level must be one of: {valid_risk_levels}')
        return v

class ResponseModel(BaseModel):
    """Standard response model"""
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProblemResponse(BaseModel):
    """Problem response model"""
    id: str
    title: str
    description: str
    domain: str
    complexity: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    stakeholder_count: int
    constraint_count: int
    success_criteria_count: int
    cycle_count: int
    solution_count: int

class CycleResponse(BaseModel):
    """Cycle response model"""
    id: str
    problem_id: str
    cycle_number: int
    status: str
    phase: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_duration: Optional[int]
    confidence_score: Optional[float]
    max_iterations: int
    current_iteration: int
    enterprise_results_count: int

class SolutionResponse(BaseModel):
    """Solution response model"""
    id: str
    problem_id: str
    cycle_id: str
    title: str
    description: str
    status: str
    confidence_score: Optional[float]
    feasibility_score: Optional[float]
    impact_score: Optional[float]
    estimated_cost: Optional[float]
    estimated_duration: Optional[int]
    risk_level: Optional[str]
    created_at: datetime
    updated_at: datetime

# Dependency functions

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """Get current user from authorization token"""
    try:
        # Check if credentials are provided
        if not credentials:
            if os.environ.get("ALLOW_ANONYMOUS", "false").lower() == "true":
                return "anonymous"
            logger.debug("No credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate token format (Bearer token)
        token = credentials.credentials
        if not token or not token.strip():
            logger.debug("Empty token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # For demo/testing: accept "test" token, reject others
        # In production, this would validate JWT token
        if token == "test":
            logger.debug("Valid test token accepted")
            return "demo_user"
        
        # Reject invalid tokens
        logger.debug(f"Invalid token rejected: {token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors but still raise HTTPException
        logger.error(f"Unexpected error in get_current_user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_workflow_engine() -> ProblemSolvingWorkflow:
    """Get the workflow engine instance"""
    if workflow_engine is None:
        raise HTTPException(status_code=500, detail="Workflow engine not initialized")
    return workflow_engine

async def get_ai_workflow_engine() -> AIEnhancedProblemSolvingWorkflow:
    """Get the AI-enhanced workflow engine instance"""
    if ai_workflow_engine is None:
        raise HTTPException(status_code=500, detail="AI workflow engine not initialized")
    return ai_workflow_engine

# API Endpoints

def _safe_len(value: Any) -> int:
    try:
        return len(value)
    except TypeError:
        return 0


async def _maybe_await(result: Any) -> Any:
    if inspect.isawaitable(result):
        return await result
    return result


def _normalize_session_payload(payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not payload:
        return payload
    if "session_id" not in payload and "id" in payload:
        normalized = dict(payload)
        normalized["session_id"] = normalized["id"]
        return normalized
    return payload


def _get_session_value(session: Any, key: str, default: Any = None) -> Any:
    if isinstance(session, dict):
        return session.get(key, default)
    return getattr(session, key, default)

@app.get("/", response_model=ResponseModel)
async def root():
    """Root endpoint with API information and Cosmic Council visual identity"""
    # Import visual identity
    try:
        from ..api.cosmic_identity import CosmicCouncilIdentity
        visual_identity = CosmicCouncilIdentity.get_complete_identity()
    except Exception:
        visual_identity = None
    
    return ResponseModel(
        success=True,
        message="Cosmic Council API is running",
        data={
            "version": "1.0.0",
            "description": "REST API for the Cosmic Council problem-solving framework",
            "cosmic_council": {
                "name": "Cosmic Council",
                "structure": "Hexagonal (ROYGBV)",
                "philosophy": "Six perspectives, one solution",
                "visual_identity": visual_identity if visual_identity else "Available at /api/v1/cosmic/identity"
            },
            "endpoints": {
                "problems": "/api/v1/problems",
                "cycles": "/api/v1/cycles",
                "solutions": "/api/v1/solutions",
                "workflows": "/api/v1/workflows",
                "analytics": "/api/v1/analytics",
                "analytics_problems": "/api/v1/analytics/problems",
                "analytics_cycles": "/api/v1/analytics/cycles",
                "analytics_solutions": "/api/v1/analytics/solutions",
                "analytics_time_series": "/api/v1/analytics/time-series",
                "analytics_comparative": "/api/v1/analytics/comparative",
                "analytics_aggregated": "/api/v1/analytics/aggregated",
                "analytics_visualization": "/api/v1/analytics/visualization",
                "analytics_export": "/api/v1/analytics/export",
                "enterprises": "/api/v1/supra_enterprise",
                "agents": "/api/v1/agents",
                "agents_list": "/api/v1/agents/",
                "agent_info": "/api/v1/agents/{enterprise}",
                "agent_process": "/api/v1/agents/{enterprise}/process",
                "agent_sequence": "/api/v1/agents/sequence",
                "agent_collaborate": "/api/v1/agents/collaborate",
                "agent_roygbv_cycle": "/api/v1/agents/roygbv/cycle",
                "agent_status": "/api/v1/agents/{enterprise}/status",
                "cosmic_identity": "/api/v1/cosmic/identity",
                "cosmic_hexagon": "/api/v1/cosmic/hexagon",
                "cosmic_colors": "/api/v1/cosmic/colors",
                "cosmic_animals": "/api/v1/cosmic/animals",
                "cosmic_enterprise_visual": "/api/v1/cosmic/supra_enterprise/{enterprise}/visual",
                "perpetual_sessions": "/api/v1/perpetual/sessions",
                "perpetual_metrics": "/api/v1/perpetual/metrics",
                "perpetual_status": "/api/v1/perpetual/status",
                "perpetual_audit_logs": "/api/v1/perpetual/audit/logs",
                "perpetual_violations": "/api/v1/perpetual/audit/violations",
                "perpetual_risk_summary": "/api/v1/perpetual/audit/risk-summary",
                "perpetual_policy_evaluate": "/api/v1/perpetual/policy/evaluate",
                "ai_session_analytics": "/api/v1/perpetual/ai/sessions/{session_id}/analytics",
                "ai_enhanced_cycle_status": "/api/v1/perpetual/ai/sessions/{session_id}/status",
                "ai_sessions_list": "/api/v1/perpetual/ai/sessions",
                "fractal_perpetual_sessions": "/api/v1/fractal-perpetual/sessions",
                "fractal_perpetual_analytics": "/api/v1/fractal-perpetual/analytics",
                "fractal_perpetual_insights": "/api/v1/fractal-perpetual/insights",
                "fractal_perpetual_status": "/api/v1/fractal-perpetual/status"
            }
        }
    )

@app.get("/health", response_model=ResponseModel)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_manager = get_database_manager()
        db_healthy = db_manager.check_connection()
        
        # Check workflow engine
        workflow_healthy = workflow_engine is not None
        
        # Check AI integration
        ai_healthy = ai_integration is not None
        
        # Check perpetual thinking system
        perpetual_healthy = (perpetual_engine is not None and 
                           perpetual_ai_engine is not None and
                           orchestration_system is not None and
                           perpetual_guardrail_integration is not None and
                           fractal_108_cycle_system is not None and
                           perpetual_108_cycle_integration is not None)
        
        overall_health = db_healthy and workflow_healthy and ai_healthy
        
        return ResponseModel(
            success=overall_health,
            message="Health check completed",
            data={
                "database": db_healthy,
                "workflow_engine": workflow_healthy,
                "ai_integration": ai_healthy,
                "perpetual_thinking_system": perpetual_healthy,
                "ai_enhanced_perpetual_system": perpetual_ai_engine is not None,
                "overall_status": "healthy" if overall_health else "unhealthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return ResponseModel(
            success=False,
            message="Health check failed",
            data={"error": str(e)}
        )

# Problem Management Endpoints

@app.post("/api/v1/problems", response_model=ResponseModel)
async def create_problem(
    request: ProblemCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create a new problem"""
    try:
        # Convert to ProblemStatement
        problem_statement = ProblemStatement(
            title=request.title,
            description=request.description,
            domain=request.domain,
            complexity=ProblemComplexity(request.complexity),
            stakeholders=request.stakeholders,
            constraints=request.constraints,
            success_criteria=request.success_criteria
        )
        
        # Create problem in database
        problem = ProblemRepository.create_problem(
            title=request.title,
            description=request.description,
            domain=request.domain,
            complexity=request.complexity,
            priority=request.priority,
            due_date=request.due_date
        )
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="create",
            resource_type="problem",
            resource_id=problem.id,
            user_id=current_user,
            new_values=request.model_dump()
        )
        
        # Record system metric
        background_tasks.add_task(
            SystemMetricsRepository.record_metric,
            metric_name="problems_created",
            metric_type="counter",
            metric_value=1.0,
            tags=["api", "problem"]
        )
        
        return ResponseModel(
            success=True,
            message="Problem created successfully",
            data={
                "problem_id": str(problem.id),
                "title": problem.title,
                "domain": problem.domain,
                "complexity": problem.complexity
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create problem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create problem: {str(e)}")

@app.get("/api/v1/problems", response_model=ResponseModel)
async def get_problems(
    domain: Optional[str] = None,
    complexity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    current_user: str = Depends(get_current_user)
):
    """Get problems with filtering"""
    try:
        problems, total_count = ProblemRepository.get_problems(
            domain=domain,
            complexity=complexity,
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        problem_responses = []
        for problem in problems:
            problem_responses.append(ProblemResponse(
                id=str(problem.id),
                title=problem.title,
                description=problem.description,
                domain=problem.domain,
                complexity=problem.complexity,
                priority=problem.priority,
                status=problem.status,
                created_at=problem.created_at,
                updated_at=problem.updated_at,
                due_date=problem.due_date,
                stakeholder_count=len(problem.stakeholders),
                constraint_count=len(problem.constraints),
                success_criteria_count=len(problem.success_criteria),
                cycle_count=len(problem.cycles),
                solution_count=len(problem.solutions)
            ))
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(problem_responses)} problems",
            data={
                "problems": [p.model_dump() for p in problem_responses],
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get problems: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get problems: {str(e)}")

@app.get("/api/v1/problems/{problem_id}", response_model=ResponseModel)
async def get_problem(
    problem_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific problem by ID"""
    try:
        problem_uuid = uuid.UUID(problem_id)
        problem = ProblemRepository.get_problem(problem_uuid)
        
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        return ResponseModel(
            success=True,
            message="Problem retrieved successfully",
            data={
                "problem": ProblemResponse(
                    id=str(problem.id),
                    title=problem.title,
                    description=problem.description,
                    domain=problem.domain,
                    complexity=problem.complexity,
                    priority=problem.priority,
                    status=problem.status,
                    created_at=problem.created_at,
                    updated_at=problem.updated_at,
                    due_date=problem.due_date,
                    stakeholder_count=len(problem.stakeholders),
                    constraint_count=len(problem.constraints),
                    success_criteria_count=len(problem.success_criteria),
                    cycle_count=len(problem.cycles),
                    solution_count=len(problem.solutions)
                ).model_dump()
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid problem ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get problem: {str(e)}")

@app.put("/api/v1/problems/{problem_id}", response_model=ResponseModel)
async def update_problem(
    problem_id: str,
    request: ProblemUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Update a problem"""
    try:
        problem_uuid = uuid.UUID(problem_id)
        
        # Get current problem for audit
        current_problem = ProblemRepository.get_problem(problem_uuid)
        if not current_problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Update problem
        updated_problem = ProblemRepository.update_problem(
            problem_uuid,
            **request.model_dump(exclude_unset=True)
        )
        
        if not updated_problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="update",
            resource_type="problem",
            resource_id=problem_uuid,
            user_id=current_user,
            old_values={
                "title": current_problem.title,
                "status": current_problem.status,
                "priority": current_problem.priority
            },
            new_values=request.model_dump(exclude_unset=True)
        )
        
        return ResponseModel(
            success=True,
            message="Problem updated successfully",
            data={
                "problem_id": str(updated_problem.id),
                "title": updated_problem.title,
                "status": updated_problem.status,
                "updated_at": updated_problem.updated_at
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid problem ID format")
    except Exception as e:
        logger.error(f"Failed to update problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update problem: {str(e)}")

# Cycle Management Endpoints

@app.post("/api/v1/cycles", response_model=ResponseModel)
async def create_cycle(
    request: CycleCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create a new cycle for a problem"""
    try:
        problem_uuid = uuid.UUID(request.problem_id)
        
        # Verify problem exists
        problem = ProblemRepository.get_problem(problem_uuid)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Create cycle
        cycle = CycleRepository.create_cycle(
            problem_id=problem_uuid,
            cycle_number=request.cycle_number,
            max_iterations=request.max_iterations,
            status="pending"
        )
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="create",
            resource_type="cycle",
            resource_id=cycle.id,
            user_id=current_user,
            new_values=request.model_dump()
        )
        
        return ResponseModel(
            success=True,
            message="Cycle created successfully",
            data={
                "cycle_id": str(cycle.id),
                "problem_id": str(cycle.problem_id),
                "cycle_number": cycle.cycle_number,
                "status": cycle.status
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid problem ID format")
    except Exception as e:
        logger.error(f"Failed to create cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create cycle: {str(e)}")

@app.get("/api/v1/cycles/{cycle_id}", response_model=ResponseModel)
async def get_cycle(
    cycle_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific cycle by ID"""
    try:
        cycle_uuid = uuid.UUID(cycle_id)
        cycle = CycleRepository.get_cycle(cycle_uuid)
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        return ResponseModel(
            success=True,
            message="Cycle retrieved successfully",
            data={
                "cycle": CycleResponse(
                    id=str(cycle.id),
                    problem_id=str(cycle.problem_id),
                    cycle_number=cycle.cycle_number,
                    status=cycle.status,
                    phase=getattr(cycle, "phase", None),
                    started_at=cycle.started_at,
                    completed_at=cycle.completed_at,
                    total_duration=cycle.total_duration,
                    confidence_score=getattr(
                        cycle,
                        "confidence_score",
                        getattr(cycle, "overall_confidence", 0.0)
                    ),
                    max_iterations=getattr(cycle, "max_iterations", 3),
                    current_iteration=getattr(cycle, "current_iteration", 0),
                    enterprise_results_count=len(cycle.enterprise_results)
                ).model_dump()
            }
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cycle ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cycle {cycle_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cycle: {str(e)}")

@app.post("/api/v1/cycles/{cycle_id}/execute", response_model=ResponseModel)
async def execute_cycle(
    cycle_id: str,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Execute a cycle (start the problem-solving process)"""
    try:
        cycle_uuid = uuid.UUID(cycle_id)
        cycle = CycleRepository.get_cycle(cycle_uuid)
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        if cycle.status != "pending":
            raise HTTPException(status_code=400, detail="Cycle is not in pending status")
        
        # Update cycle status to in_progress
        CycleRepository.update_cycle_status(cycle_uuid, "in_progress")
        
        # Start cycle execution in background
        background_tasks.add_task(execute_cycle_background, cycle_uuid, current_user)
        
        return ResponseModel(
            success=True,
            message="Cycle execution started",
            data={
                "cycle_id": str(cycle_uuid),
                "status": "in_progress",
                "message": "Cycle execution is running in the background"
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid cycle ID format")
    except Exception as e:
        logger.error(f"Failed to execute cycle {cycle_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute cycle: {str(e)}")

async def execute_cycle_background(cycle_id: uuid.UUID, user_id: str):
    """Background task to execute a cycle with WebSocket updates"""
    from ..api.websocket_manager import websocket_manager, SectorState
    from ..core.core import EnterpriseType
        
    try:
        logger.info(f"Starting background execution of cycle {cycle_id}")
        
        # Notify WebSocket clients that cycle has started
        await websocket_manager.notify_cycle_start(str(cycle_id), str(cycle.problem_id))
        
        # Get cycle and problem
        cycle = CycleRepository.get_cycle(cycle_id)
        if not cycle:
            logger.error(f"Cycle {cycle_id} not found")
            return
        
        problem = ProblemRepository.get_problem(cycle.problem_id)
        if not problem:
            logger.error(f"Problem {cycle.problem_id} not found")
            return
        
        # Convert to ProblemStatement
        problem_statement = ProblemStatement(
            title=problem.title,
            description=problem.description,
            domain=problem.domain,
            complexity=ProblemComplexity(problem.complexity),
            stakeholders=[s.name for s in problem.stakeholders],
            constraints=problem.constraints,
            success_criteria=[c.name for c in problem.success_criteria]
        )
        
        # Update hexagon state with problem
        websocket_manager.update_hexagon_state({
            "problem": {
                "id": str(problem.id),
                "title": problem.title,
                "description": problem.description
            }
        })
        
        # Execute cycle using AI-enhanced workflow
        session = await ai_workflow_engine.start_ai_enhanced_session(problem_statement, user_id)
        
        # Process through all enterprises in ROYGBV order
        enterprise_order = [
            EnterpriseType.RED_OWL,
            EnterpriseType.ORANGE_ORANGUTAN,
            EnterpriseType.YELLOW_HONEYBEE,
            EnterpriseType.GREEN_TORTOISE,
            EnterpriseType.BLUE_DOLPHIN,
            EnterpriseType.PURPLE_ELEPHANT
        ]
        
        total_enterprises = len(enterprise_order)
        for idx, enterprise_type in enumerate(enterprise_order):
            enterprise_name = enterprise_type.value
            progress = (idx + 1) / total_enterprises
            
            # Update sector to processing
            await websocket_manager.update_sector(
                enterprise=enterprise_name,
                state=SectorState.PROCESSING,
                progress=0.0,
                confidence=0.0
            )
            
            # Notify cycle progress
            await websocket_manager.notify_cycle_progress(
                cycle_id=str(cycle_id),
                enterprise=enterprise_name,
                progress=progress,
                confidence=0.0
            )
            
            # Simulate enterprise processing (replace with actual processing)
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Update sector to completed
            await websocket_manager.update_sector(
                enterprise=enterprise_name,
                state=SectorState.COMPLETED,
                progress=1.0,
                confidence=0.8  # Example confidence
            )
            
            # Update cycle progress
            await websocket_manager.notify_cycle_progress(
                cycle_id=str(cycle_id),
                enterprise=enterprise_name,
                progress=progress,
                confidence=0.8
            )
        
        # Get enterprises for actual processing (if needed)
        enterprises = EnterpriseRepository.get_all_enterprises()
        for enterprise in enterprises:
            # Create enterprise result
            result = EnterpriseResultRepository.create_enterprise_result(
                cycle_id=cycle_id,
                enterprise_id=enterprise.id,
                status="in_progress",
                started_at=datetime.now(timezone.utc)
            )
            
            # Simulate enterprise processing (in real implementation, this would call the actual enterprise)
            await asyncio.sleep(1)  # Simulate processing time
            
            # Update result
            EnterpriseResultRepository.update_enterprise_result(
                result.id,
                status="completed",
                confidence_score=0.85,
                processing_time=1.0,
                specialized_analysis={"approach": f"{enterprise.name} analysis"},
                recommendations=[f"Recommendation from {enterprise.name}"],
                reasoning=f"Analysis reasoning from {enterprise.name}",
                key_insights=[f"Key insight from {enterprise.name}"],
                ai_enhanced=True,
                ai_model_used="gpt-4",
                ai_tokens_used=500,
                ai_processing_time=0.8
            )
        
        # Complete the cycle
        CycleRepository.update_cycle_status(cycle_id, "completed")
        
        # Notify WebSocket clients that cycle has completed
        await websocket_manager.notify_cycle_complete(
            cycle_id=str(cycle_id),
            result={
                "status": "completed",
                "enterprises_processed": len(enterprises),
                "confidence": 0.85  # Example - calculate from actual results
            }
        )
        
        # Reset all sectors to inactive
        for enterprise_type in enterprise_order:
            await websocket_manager.update_sector(
                enterprise=enterprise_type.value,
                state=SectorState.INACTIVE,
                progress=0.0,
                confidence=0.0
            )
        
        logger.info(f"Cycle {cycle_id} execution completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to execute cycle {cycle_id} in background: {str(e)}")
        CycleRepository.update_cycle_status(cycle_id, "failed")
        
        # Notify WebSocket clients of cycle failure
        try:
            from ..api.websocket_manager import websocket_manager
            await websocket_manager.notify_cycle_complete(
                cycle_id=str(cycle_id),
                result={
                    "status": "failed",
                    "error": str(e)
                }
            )
        except Exception as ws_error:
            logger.error(f"Failed to send WebSocket notification: {ws_error}")

# Solution Management Endpoints

@app.post("/api/v1/solutions", response_model=ResponseModel)
async def create_solution(
    request: SolutionCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create a new solution"""
    try:
        problem_uuid = uuid.UUID(request.problem_id)
        cycle_uuid = uuid.UUID(request.cycle_id)
        
        # Verify problem and cycle exist
        problem = ProblemRepository.get_problem(problem_uuid)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        cycle = CycleRepository.get_cycle(cycle_uuid)
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")
        
        # Create solution
        solution = SolutionRepository.create_solution(
            problem_id=problem_uuid,
            cycle_id=cycle_uuid,
            title=request.title,
            description=request.description,
            created_by=current_user,
            approach=request.approach,
            confidence_score=request.confidence_score,
            feasibility_score=request.feasibility_score,
            impact_score=request.impact_score,
            estimated_cost=request.estimated_cost,
            estimated_duration=request.estimated_duration,
            risk_level=request.risk_level
        )
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="create",
            resource_type="solution",
            resource_id=solution.id,
            user_id=current_user,
            new_values=request.model_dump()
        )
        
        return ResponseModel(
            success=True,
            message="Solution created successfully",
            data={
                "solution_id": str(solution.id),
                "title": solution.title,
                "confidence_score": solution.confidence_score,
                "feasibility_score": solution.feasibility_score
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        logger.error(f"Failed to create solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create solution: {str(e)}")

@app.post("/api/v1/solutions/create-with-cycle", response_model=ResponseModel)
async def create_solution_with_cycle(
    request: SolutionCreateWithCycleRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create a solution with automatic cycle creation and execution"""
    try:
        problem_uuid = uuid.UUID(request.problem_id)
        
        # Verify problem exists
        problem = ProblemRepository.get_problem(problem_uuid)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Create cycle
        cycle = CycleRepository.create_cycle(
            problem_id=problem_uuid,
            cycle_number=1,
            max_iterations=request.max_iterations,
            status="pending"
        )
        
        # Execute cycle in background
        background_tasks.add_task(
            execute_cycle_background,
            cycle.id,
            current_user
        )
        
        # Wait a moment for cycle to start (in production, you'd poll or use webhooks)
        import asyncio
        await asyncio.sleep(0.5)
        
        # Update cycle status to in_progress (simulated)
        CycleRepository.update_cycle_status(cycle.id, "in_progress")
        
        # Create solution linked to the cycle
        solution = SolutionRepository.create_solution(
            problem_id=problem_uuid,
            cycle_id=cycle.id,
            title=request.title,
            description=request.description,
            created_by=current_user,
            approach=request.approach,
            status="draft"
        )
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="create",
            resource_type="solution",
            resource_id=solution.id,
            user_id=current_user,
            new_values={"created_with_cycle": True, **request.model_dump()}
        )
        
        return ResponseModel(
            success=True,
            message="Solution created with cycle successfully",
            data={
                "solution_id": str(solution.id),
                "cycle_id": str(cycle.id),
                "problem_id": str(problem_uuid),
                "title": solution.title,
                "status": solution.status,
                "cycle_status": "in_progress",
                "progress": "Cycle execution started in background"
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid problem ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create solution with cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create solution with cycle: {str(e)}")

@app.get("/api/v1/solutions", response_model=ResponseModel)
async def get_solutions(
    problem_id: Optional[str] = None,
    cycle_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    """Get solutions with filtering"""
    try:
        if problem_id:
            problem_uuid = uuid.UUID(problem_id)
            solutions = SolutionRepository.get_solutions_for_problem(problem_uuid)
        else:
            # Get all solutions (implement this in repository if needed)
            solutions = []
        
        solution_responses = []
        for solution in solutions[offset:offset+limit]:
            solution_responses.append(SolutionResponse(
                id=str(solution.id),
                problem_id=str(solution.problem_id),
                cycle_id=str(solution.cycle_id),
                title=solution.title,
                description=solution.description,
                status=solution.status,
                confidence_score=solution.confidence_score,
                feasibility_score=solution.feasibility_score,
                impact_score=solution.impact_score,
                estimated_cost=getattr(solution, "estimated_cost", None),
                estimated_duration=getattr(solution, "estimated_duration", None),
                risk_level=getattr(solution, "risk_level", None),
                created_at=solution.created_at,
                updated_at=solution.updated_at
            ))
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(solution_responses)} solutions",
            data={
                "solutions": [s.model_dump() for s in solution_responses],
                "total_count": len(solution_responses),
                "limit": limit,
                "offset": offset
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        logger.error(f"Failed to get solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get solutions: {str(e)}")

# Analytics Endpoints

@app.get("/api/v1/analytics/problems", response_model=Dict[str, Any])
async def get_problem_analytics(current_user: str = Depends(get_current_user)):
    """Get problem analytics and statistics"""
    try:
        stats = AnalyticsRepository.get_problem_statistics()
        if os.environ.get("ALLOW_ANONYMOUS", "false").lower() == "true":
            return {"success": True, **stats, "data": stats}
        return ResponseModel(
            success=True,
            message="Problem analytics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get problem analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get problem analytics: {str(e)}")

@app.get("/api/v1/analytics/cycles", response_model=Dict[str, Any])
async def get_cycle_analytics(current_user: str = Depends(get_current_user)):
    """Get cycle analytics and statistics"""
    try:
        stats = AnalyticsRepository.get_cycle_statistics()
        if os.environ.get("ALLOW_ANONYMOUS", "false").lower() == "true":
            return {"success": True, **stats, "data": stats}
        return ResponseModel(
            success=True,
            message="Cycle analytics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get cycle analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cycle analytics: {str(e)}")

@app.get("/api/v1/analytics/solutions", response_model=Dict[str, Any])
async def get_solution_analytics(current_user: str = Depends(get_current_user)):
    """Get solution analytics and statistics"""
    try:
        stats = AnalyticsRepository.get_solution_statistics()
        if os.environ.get("ALLOW_ANONYMOUS", "false").lower() == "true":
            return {"success": True, **stats, "data": stats}
        return ResponseModel(
            success=True,
            message="Solution analytics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get solution analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get solution analytics: {str(e)}")

# Advanced Analytics Endpoints

@app.get("/api/v1/analytics/time-series", response_model=ResponseModel)
async def get_time_series_analytics(
    resource_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "day",
    current_user: str = Depends(get_current_user)
):
    """Get time-series analytics for problems, cycles, or solutions"""
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
        
        # Validate resource type
        if resource_type not in ["problems", "cycles", "solutions"]:
            raise HTTPException(status_code=400, detail="resource_type must be one of: problems, cycles, solutions")
        
        # Validate interval
        if interval not in ["day", "week", "month"]:
            raise HTTPException(status_code=400, detail="interval must be one of: day, week, month")
        
        stats = AnalyticsRepository.get_time_series_analytics(
            resource_type=resource_type,
            start_date=start,
            end_date=end,
            interval=interval
        )
        
        return ResponseModel(
            success=True,
            message=f"Time-series analytics retrieved successfully for {resource_type}",
            data=stats
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to get time-series analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get time-series analytics: {str(e)}")

@app.get("/api/v1/analytics/comparative", response_model=ResponseModel)
async def get_comparative_analytics(
    resource_type: str,
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
    current_user: str = Depends(get_current_user)
):
    """Get comparative analytics between two periods"""
    try:
        # Parse dates
        p1_start = datetime.fromisoformat(period1_start.replace('Z', '+00:00'))
        p1_end = datetime.fromisoformat(period1_end.replace('Z', '+00:00'))
        p2_start = datetime.fromisoformat(period2_start.replace('Z', '+00:00'))
        p2_end = datetime.fromisoformat(period2_end.replace('Z', '+00:00'))
        
        # Validate resource type
        if resource_type not in ["problems", "cycles", "solutions"]:
            raise HTTPException(status_code=400, detail="resource_type must be one of: problems, cycles, solutions")
        
        stats = AnalyticsRepository.get_comparative_analytics(
            resource_type=resource_type,
            period1_start=p1_start,
            period1_end=p1_end,
            period2_start=p2_start,
            period2_end=p2_end
        )
        
        return ResponseModel(
            success=True,
            message=f"Comparative analytics retrieved successfully for {resource_type}",
            data=stats
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to get comparative analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get comparative analytics: {str(e)}")

@app.get("/api/v1/analytics/aggregated", response_model=ResponseModel)
async def get_aggregated_analytics(
    resource_type: str,
    group_by: str,
    filters: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get aggregated analytics grouped by specified field"""
    try:
        # Parse filters if provided
        filter_dict = None
        if filters:
            try:
                filter_dict = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filters JSON format")
        
        # Validate resource type
        if resource_type not in ["problems", "cycles", "solutions"]:
            raise HTTPException(status_code=400, detail="resource_type must be one of: problems, cycles, solutions")
        
        stats = AnalyticsRepository.get_aggregated_analytics(
            resource_type=resource_type,
            group_by=group_by,
            filters=filter_dict
        )
        
        return ResponseModel(
            success=True,
            message=f"Aggregated analytics retrieved successfully for {resource_type}",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Failed to get aggregated analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get aggregated analytics: {str(e)}")

@app.get("/api/v1/analytics/visualization", response_model=ResponseModel)
async def get_visualization_data(
    resource_type: str,
    chart_type: str = "bar",
    current_user: str = Depends(get_current_user)
):
    """Get data formatted for visualization"""
    try:
        # Validate resource type
        if resource_type not in ["problems", "cycles", "solutions"]:
            raise HTTPException(status_code=400, detail="resource_type must be one of: problems, cycles, solutions")
        
        # Validate chart type
        if chart_type not in ["bar", "line", "pie", "scatter"]:
            raise HTTPException(status_code=400, detail="chart_type must be one of: bar, line, pie, scatter")
        
        data = AnalyticsRepository.get_visualization_data(
            resource_type=resource_type,
            chart_type=chart_type
        )
        
        return ResponseModel(
            success=True,
            message=f"Visualization data retrieved successfully for {resource_type}",
            data=data
        )
        
    except Exception as e:
        logger.error(f"Failed to get visualization data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get visualization data: {str(e)}")

@app.get("/api/v1/analytics/export", response_model=ResponseModel)
async def export_analytics(
    resource_type: str,
    format: str = "json",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Export analytics data in various formats"""
    from fastapi.responses import Response
    import csv
    import io
    
    try:
        # Validate resource type
        if resource_type not in ["problems", "cycles", "solutions"]:
            raise HTTPException(status_code=400, detail="resource_type must be one of: problems, cycles, solutions")
        
        # Validate format
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="format must be one of: json, csv")
        
        # Get time-series data
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
        
        data = AnalyticsRepository.get_time_series_analytics(
            resource_type=resource_type,
            start_date=start,
            end_date=end,
            interval="day"
        )
        
        if format == "json":
            return ResponseModel(
                success=True,
                message=f"Analytics data exported successfully for {resource_type}",
                data=data
            )
        elif format == "csv":
            # Convert to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["period", "count"])
            for item in data.get("data", []):
                writer.writerow([item["period"], item["count"]])
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={resource_type}_analytics_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
                }
            )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to export analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export analytics: {str(e)}")

# Workflow Session Endpoints

class WorkflowRepository:
    """Repository for workflow session operations"""
    
    @staticmethod
    def create_workflow_session(problem_id: uuid.UUID, user_id: Optional[uuid.UUID],
                               session_type: str = "standard",
                               user_preferences: Optional[Dict[str, Any]] = None) -> WorkflowSessionModel:
        """Create a new workflow session"""
        db_manager = get_database_manager()
        try:
            with db_manager.get_session() as session:
                workflow_session = WorkflowSessionModel(
                    id=uuid.uuid4(),
                    problem_id=problem_id,
                    user_id=user_id,
                    session_type=session_type,
                    status="active",
                    current_step="problem_definition",
                    started_at=datetime.now(timezone.utc),
                    user_preferences=user_preferences or {},
                    session_data={}
                )
                session.add(workflow_session)

                # Pre-create canonical workflow steps so progress calculations reflect remaining work
                step_models = []
                for order, wf_step in enumerate(WorkflowStep, start=1):
                    step_models.append(
                        WorkflowStepModel(
                            id=uuid.uuid4(),
                            session_id=workflow_session.id,
                            step_name=wf_step.value,
                            step_type=wf_step.value.split("_")[0],
                            step_order=order,
                            status="pending",
                            input_data={},
                            output_data={}
                        )
                    )
                if step_models:
                    session.add_all(step_models)

                session.commit()
                session.refresh(workflow_session)
                session.expunge(workflow_session)
                return workflow_session
        except Exception as e:
            logger.error(f"Failed to create workflow session: {e}")
            raise
    
    @staticmethod
    def get_workflow_session(session_id: uuid.UUID) -> Optional[WorkflowSessionModel]:
        """Get workflow session by ID"""
        db_manager = get_database_manager()
        try:
            with db_manager.get_session() as session:
                workflow_session = session.query(WorkflowSessionModel).filter(
                    WorkflowSessionModel.id == session_id
                ).first()
                if workflow_session:
                    # Access attributes before expunging
                    _ = workflow_session.id
                    _ = workflow_session.problem_id
                    _ = workflow_session.status
                    session.expunge(workflow_session)
                return workflow_session
        except Exception as e:
            logger.error(f"Failed to get workflow session: {e}")
            return None
    
    @staticmethod
    def update_workflow_session(session_id: uuid.UUID, **kwargs) -> Optional[WorkflowSessionModel]:
        """Update workflow session"""
        db_manager = get_database_manager()
        try:
            with db_manager.get_session() as session:
                workflow_session = session.query(WorkflowSessionModel).filter(
                    WorkflowSessionModel.id == session_id
                ).first()
                if workflow_session:
                    for key, value in kwargs.items():
                        if hasattr(workflow_session, key):
                            setattr(workflow_session, key, value)
                    workflow_session.updated_at = datetime.now(timezone.utc)
                    session.commit()
                    session.refresh(workflow_session)
                    session.expunge(workflow_session)
                    return workflow_session
                return None
        except Exception as e:
            logger.error(f"Failed to update workflow session: {e}")
            return None
    
    @staticmethod
    def create_workflow_step(session_id: uuid.UUID, step_name: str, step_type: str,
                            step_order: int, input_data: Optional[Dict[str, Any]] = None) -> WorkflowStepModel:
        """Create a workflow step"""
        db_manager = get_database_manager()
        try:
            with db_manager.get_session() as session:
                workflow_step = WorkflowStepModel(
                    id=uuid.uuid4(),
                    session_id=session_id,
                    step_name=step_name,
                    step_type=step_type,
                    step_order=step_order,
                    status="pending",
                    input_data=input_data or {}
                )
                session.add(workflow_step)
                session.commit()
                session.refresh(workflow_step)
                session.expunge(workflow_step)
                return workflow_step
        except Exception as e:
            logger.error(f"Failed to create workflow step: {e}")
            raise
    
    @staticmethod
    def get_workflow_steps(session_id: uuid.UUID) -> List[WorkflowStepModel]:
        """Get all steps for a workflow session"""
        db_manager = get_database_manager()
        try:
            with db_manager.get_session() as session:
                steps = session.query(WorkflowStepModel).filter(
                    WorkflowStepModel.session_id == session_id
                ).order_by(WorkflowStepModel.step_order).all()
                # Expunge all steps
                for step in steps:
                    session.expunge(step)
                return steps
        except Exception as e:
            logger.error(f"Failed to get workflow steps: {e}")
            return []
    
    @staticmethod
    def update_workflow_step(step_id: uuid.UUID, **kwargs) -> Optional[WorkflowStepModel]:
        """Update workflow step"""
        db_manager = get_database_manager()
        try:
            with db_manager.get_session() as session:
                step = session.query(WorkflowStepModel).filter(
                    WorkflowStepModel.id == step_id
                ).first()
                if step:
                    for key, value in kwargs.items():
                        if hasattr(step, key):
                            setattr(step, key, value)
                    session.commit()
                    session.refresh(step)
                    session.expunge(step)
                    return step
                return None
        except Exception as e:
            logger.error(f"Failed to update workflow step: {e}")
            return None

@app.post("/api/v1/workflows", response_model=ResponseModel)
async def create_workflow_session(
    request: WorkflowCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create a new workflow session"""
    try:
        problem_uuid = uuid.UUID(request.problem_id)
        
        # Verify problem exists
        problem = ProblemRepository.get_problem(problem_uuid)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        # Create workflow session
        user_uuid: Optional[uuid.UUID] = None
        try:
            if current_user and current_user != "anonymous":
                user_uuid = uuid.UUID(str(current_user))
        except Exception:
            # Ignore parsing errors and treat as anonymous
            user_uuid = None

        workflow_session = WorkflowRepository.create_workflow_session(
            problem_id=problem_uuid,
            user_id=user_uuid,
            session_type=request.session_type,
            user_preferences=request.user_preferences
        )
        
        # Log audit action
        background_tasks.add_task(
            AuditLogRepository.log_action,
            action="create",
            resource_type="workflow_session",
            resource_id=workflow_session.id,
            user_id=current_user,
            new_values=request.model_dump()
        )
        
        return ResponseModel(
            success=True,
            message="Workflow session created successfully",
            data={
                "session_id": str(workflow_session.id),
                "problem_id": str(workflow_session.problem_id),
                "session_type": workflow_session.session_type,
                "status": workflow_session.status,
                "current_step": workflow_session.current_step,
                "started_at": workflow_session.started_at.isoformat() if workflow_session.started_at else None,
                "total_steps": len(WorkflowStep)
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid problem ID format")
    except Exception as e:
        logger.error(f"Failed to create workflow session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create workflow session: {str(e)}")

@app.get("/api/v1/workflows/{session_id}", response_model=ResponseModel)
async def get_workflow_session(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get workflow session details"""
    try:
        session_uuid = uuid.UUID(session_id)
        workflow_session = WorkflowRepository.get_workflow_session(session_uuid)
        
        if not workflow_session:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        # Get workflow steps
        steps = WorkflowRepository.get_workflow_steps(session_uuid)
        steps_data = []
        for step in steps:
            steps_data.append({
                "id": str(step.id),
                "step_name": step.step_name,
                "step_type": step.step_type,
                "step_order": step.step_order,
                "status": step.status,
                "started_at": step.started_at.isoformat() if step.started_at else None,
                "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                "duration": step.duration
            })
        
        return ResponseModel(
            success=True,
            message="Workflow session retrieved successfully",
            data={
                "session_id": str(workflow_session.id),
                "problem_id": str(workflow_session.problem_id),
                "session_type": workflow_session.session_type,
                "status": workflow_session.status,
                "current_step": workflow_session.current_step,
                "started_at": workflow_session.started_at.isoformat() if workflow_session.started_at else None,
                "completed_at": workflow_session.completed_at.isoformat() if workflow_session.completed_at else None,
                "total_duration": workflow_session.total_duration,
                "steps": steps_data,
                "steps_count": len(steps_data)
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow session: {str(e)}")

@app.post("/api/v1/workflows/{session_id}/step/{step_number}", response_model=ResponseModel)
async def execute_workflow_step(
    session_id: str,
    step_number: int,
    request: WorkflowStepRequest,
    current_user: str = Depends(get_current_user)
):
    """Execute a workflow step"""
    try:
        session_uuid = uuid.UUID(session_id)
        workflow_session = WorkflowRepository.get_workflow_session(session_uuid)
        
        if not workflow_session:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        if workflow_session.status not in ["active", "paused"]:
            raise HTTPException(status_code=400, detail=f"Cannot execute step for session with status: {workflow_session.status}")

        # Determine canonical workflow ordering
        canonical_steps = list(WorkflowStep)
        if step_number < 1 or step_number > len(canonical_steps):
            raise HTTPException(status_code=400, detail="Invalid step number")

        expected_step = canonical_steps[step_number - 1]

        # Get workflow steps
        steps = WorkflowRepository.get_workflow_steps(session_uuid)
        step = next((s for s in steps if s.step_order == step_number), None)

        if step and step.status == "completed":
            raise HTTPException(status_code=400, detail=f"Step {step_number} already completed")

        if not step:
            # Create new step if prepopulation failed for some reason
            step = WorkflowRepository.create_workflow_step(
                session_id=session_uuid,
                step_name=expected_step.value,
                step_type=expected_step.value.split("_")[0],
                step_order=step_number,
                input_data=request.user_inputs
            )
        
        # Update step status
        step_start_time = datetime.now(timezone.utc)
        step = WorkflowRepository.update_workflow_step(
            step.id,
            status="in_progress",
            started_at=step_start_time,
            input_data=request.user_inputs
        )

        if not step:
            raise HTTPException(status_code=500, detail="Failed to update workflow step")

        # Update session current step
        WorkflowRepository.update_workflow_session(
            session_uuid,
            current_step=expected_step.value,
            status="active"
        )
        
        # Simulate step execution (in production, this would call the actual workflow engine)
        # For now, we'll mark it as completed with mock output
        import asyncio
        await asyncio.sleep(0.1)  # Simulate processing
        
        step_end_time = datetime.now(timezone.utc)
        duration = int((step_end_time - step_start_time).total_seconds())

        step = WorkflowRepository.update_workflow_step(
            step.id,
            status="completed",
            completed_at=step_end_time,
            duration=duration,
            output_data={
                "result": "Step executed successfully",
                "inputs": request.user_inputs,
                "step_type": expected_step.value.split("_")[0]
            }
        )

        if not step:
            raise HTTPException(status_code=500, detail="Failed to complete workflow step")

        # Determine the next step (if any) to surface to clients
        next_step_value = None
        if step_number < len(canonical_steps):
            next_step_value = canonical_steps[step_number].value
            WorkflowRepository.update_workflow_session(
                session_uuid,
                current_step=next_step_value,
                status="active"
            )

        return ResponseModel(
            success=True,
            message=f"Workflow step {step_number} executed successfully",
            data={
                "step_id": str(step.id),
                "step_name": step.step_name,
                "step_order": step.step_order,
                "status": step.status,
                "output_data": step.output_data,
                "duration": step.duration,
                "next_step": next_step_value
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID or step number format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute workflow step: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow step: {str(e)}")

@app.get("/api/v1/workflows/{session_id}/progress", response_model=ResponseModel)
async def get_workflow_progress(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get workflow session progress"""
    try:
        session_uuid = uuid.UUID(session_id)
        workflow_session = WorkflowRepository.get_workflow_session(session_uuid)
        
        if not workflow_session:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        # Get all steps
        steps = WorkflowRepository.get_workflow_steps(session_uuid)

        # Calculate progress
        total_steps = len(WorkflowStep)
        completed_steps = sum(1 for s in steps if s.status == "completed")
        in_progress_steps = sum(1 for s in steps if s.status == "in_progress")
        pending_steps = max(total_steps - completed_steps - in_progress_steps, 0)
        
        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return ResponseModel(
            success=True,
            message="Workflow progress retrieved successfully",
            data={
                "session_id": str(workflow_session.id),
                "status": workflow_session.status,
                "current_step": workflow_session.current_step,
                "progress": {
                    "total_steps": total_steps,
                    "completed_steps": completed_steps,
                    "in_progress_steps": in_progress_steps,
                    "pending_steps": pending_steps,
                    "progress_percentage": round(progress_percentage, 2)
                },
                "started_at": workflow_session.started_at.isoformat() if workflow_session.started_at else None,
                "total_duration": workflow_session.total_duration
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow progress: {str(e)}")

@app.post("/api/v1/workflows/{session_id}/synthesize", response_model=ResponseModel)
async def synthesize_workflow_results(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    """Synthesize workflow session results"""
    try:
        session_uuid = uuid.UUID(session_id)
        workflow_session = WorkflowRepository.get_workflow_session(session_uuid)
        
        if not workflow_session:
            raise HTTPException(status_code=404, detail="Workflow session not found")
        
        # Get all completed steps
        steps = WorkflowRepository.get_workflow_steps(session_uuid)
        completed_steps = [s for s in steps if s.status == "completed"]
        
        # Synthesize results from all steps
        synthesis = {
            "session_id": str(workflow_session.id),
            "problem_id": str(workflow_session.problem_id),
            "total_steps_completed": len(completed_steps),
            "step_results": [
                {
                    "step_name": step.step_name,
                    "step_type": step.step_type,
                    "output_data": step.output_data,
                    "duration": step.duration
                }
                for step in completed_steps
            ],
            "synthesized_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update session with synthesis
        now_utc = datetime.now(timezone.utc)
        start_time = workflow_session.started_at
        if start_time and start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        total_duration = 0
        if start_time:
            try:
                total_duration = int((now_utc - start_time).total_seconds())
            except Exception:
                total_duration = 0

        WorkflowRepository.update_workflow_session(
            session_uuid,
            status="completed",
            completed_at=now_utc,
            total_duration=total_duration,
            session_data={"synthesis": synthesis}
        )
        
        return ResponseModel(
            success=True,
            message="Workflow results synthesized successfully",
            data=synthesis
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to synthesize workflow results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to synthesize workflow results: {str(e)}")

# Enterprise Endpoints

@app.get("/api/v1/supra_enterprise", response_model=ResponseModel)
async def get_enterprises(current_user: str = Depends(get_current_user)):
    """Get all enterprises"""
    try:
        enterprises = EnterpriseRepository.get_all_enterprises()
        
        enterprise_data = []
        for enterprise in enterprises:
            enterprise_data.append({
                "id": str(enterprise.id),
                "name": enterprise.name,
                "type": enterprise.type,
                "description": enterprise.description,
                "color": enterprise.color,
                "symbol": enterprise.symbol,
                "core_principle": enterprise.core_principle,
                "expertise_areas": enterprise.expertise_areas,
                "processing_order": enterprise.processing_order,
                "is_active": enterprise.is_active
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(enterprise_data)} enterprises",
            data={
                "enterprises": enterprise_data
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get enterprises: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get enterprises: {str(e)}")

# ============================================================================
# PERPETUAL THINKING SYSTEM API ENDPOINTS
# ============================================================================

# Import perpetual thinking system components
try:
    from ..integrations.unified_perpetual_thinking_system import (
        CycleType,
        AIEnhancementLevel
    )
    from ..database.unified_database_service import DatabaseService, PerpetualDatabaseService
    from ..integrations.perpetual_guardrail_integration import (
        PolicyEngine,
        PerpetualGuardrailIntegration,
        PerpetualPolicyType,
        PerpetualActionType,
        PerpetualPolicyContext
    )
    from ..integrations.perpetual_108_cycle_integration import PerpetualFractalMode
    from ..integrations.unified_fractal_system import Fractal108CycleSystem
    PERPETUAL_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Perpetual thinking system not available: {e}")
    PERPETUAL_SYSTEM_AVAILABLE = False

# Global perpetual system components
perpetual_engine = None
perpetual_ai_engine = None
orchestration_system = None
perpetual_db_service = None
perpetual_guardrail_integration = None
perpetual_policy_enforcer = None
fractal_108_cycle_system = None
perpetual_108_cycle_integration = None

# Pydantic models for perpetual thinking system
class PolicyEvaluateRequest(BaseModel):
    """Request model for policy evaluation"""
    operation_type: str = Field(..., description="Type of operation (e.g., 'perpetual_session_creation')")
    action_type: str = Field(..., description="Type of action (e.g., 'create', 'read', 'execute')")
    agent_id: str = Field(..., description="ID of the agent performing the operation")
    context: Dict[str, Any] = Field(default={}, description="Context information for policy evaluation")

class PerpetualSessionCreateRequest(BaseModel):
    """Request model for creating a perpetual thinking session"""
    session_name: str = Field(..., min_length=1, max_length=255, description="Session name")
    initial_input: str = Field(..., min_length=1, description="Initial input for the session")
    mode: str = Field(default="collaborative", description="Orchestration mode")
    goals: List[str] = Field(default=[], description="Session goals")
    success_criteria: List[str] = Field(default=[], description="Success criteria")
    ai_enhancement_level: str = Field(default="enhanced", description="AI enhancement level")
    ai_learning_enabled: bool = Field(default=True, description="Enable AI learning")
    ai_adaptation_enabled: bool = Field(default=True, description="Enable AI adaptation")
    ai_breakthrough_detection: bool = Field(default=True, description="Enable AI breakthrough detection")

class PerpetualSessionResponse(BaseModel):
    """Response model for perpetual thinking session"""
    session_id: str
    session_name: str
    initial_input: str
    current_input: str
    current_cycle_number: int
    status: str
    mode: str
    goals: List[str]
    success_criteria: List[str]
    created_at: datetime
    updated_at: datetime
    summary_metrics: Optional[Dict[str, Any]] = None

class PerpetualCycleResponse(BaseModel):
    """Response model for perpetual cycle"""
    cycle_id: str
    session_id: str
    cycle_number: int
    cycle_type: str
    status: str
    input_text: str
    output_text: Optional[str] = None
    confidence_score: float
    effectiveness_score: float
    relevance_score: float
    pattern_detected: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None

class BreakthroughResponse(BaseModel):
    """Response model for breakthrough moments"""
    breakthrough_id: str
    session_id: str
    cycle_id: str
    breakthrough_type: str
    insight_description: str
    impact_score: float
    occurred_at: datetime

class MetaCycleResponse(BaseModel):
    """Response model for meta-cycles"""
    meta_cycle_id: str
    session_id: str
    meta_cycle_type: str
    target_metric: str
    initial_value: float
    final_value: float
    improvement: float
    confidence_in_changes: float
    started_at: datetime
    completed_at: Optional[datetime] = None

# Perpetual Thinking System Endpoints

@app.post("/api/v1/perpetual/sessions", response_model=ResponseModel)
async def create_perpetual_session(
    request: PerpetualSessionCreateRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new AI-enhanced perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_ai_engine:
        raise HTTPException(status_code=503, detail="AI-enhanced perpetual thinking system not available")
    
    try:
        # Convert AI enhancement level string to enum
        try:
            ai_enhancement_level = AIEnhancementLevel(request.ai_enhancement_level)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid AI enhancement level: {request.ai_enhancement_level}")
        
        # Use policy enforcer to create session with policy enforcement
        if perpetual_policy_enforcer:
            allow, session_id, policy_meta = await _maybe_await(perpetual_policy_enforcer.create_session_with_policy(
                session_name=request.session_name,
                initial_input=request.initial_input,
                user_id=credentials.credentials  # Use token as user ID for demo
            ))
            
            if not allow:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Session creation denied by policy: {policy_meta}"
                )
        else:
            # Fallback to direct AI-enhanced perpetual cycle creation
            session_id = await _maybe_await(perpetual_ai_engine.start_ai_enhanced_perpetual_cycle(
                session_name=request.session_name,
                initial_input=request.initial_input,
                mode=request.mode,
                goals=request.goals,
                success_criteria=request.success_criteria,
                ai_enhancement_level=ai_enhancement_level,
                ai_learning_enabled=request.ai_learning_enabled,
                ai_adaptation_enabled=request.ai_adaptation_enabled,
                ai_breakthrough_detection=request.ai_breakthrough_detection,
                cycle_type=CycleType.EXPLORATION,
                max_cycles=None  # No limit for perpetual sessions
            ))
        
        # Save to database
        if perpetual_db_service:
            session_data = {
                'session_id': session_id,
                'session_name': request.session_name,
                'initial_input': request.initial_input,
                'current_input': request.initial_input,
                'current_cycle_number': 0,
                'status': 'active',
                'mode': request.mode,
                'goals': request.goals,
                'success_criteria': request.success_criteria,
                'ai_enhancement_level': request.ai_enhancement_level,
                'ai_learning_enabled': request.ai_learning_enabled,
                'ai_adaptation_enabled': request.ai_adaptation_enabled,
                'ai_breakthrough_detection': request.ai_breakthrough_detection,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'ended_at': None,
                'session_data': {},
                'summary_metrics': {}
            }
            if hasattr(perpetual_db_service, "save_perpetual_session"):
                await _maybe_await(perpetual_db_service.save_perpetual_session(session_data))
            elif hasattr(perpetual_db_service, "create_perpetual_session"):
                mapped = dict(session_data)
                if "session_id" in mapped and "id" not in mapped:
                    try:
                        mapped["id"] = uuid.UUID(mapped["session_id"])
                    except Exception:
                        mapped["id"] = uuid.uuid4()
                await _maybe_await(perpetual_db_service.create_perpetual_session(mapped))
            elif hasattr(perpetual_db_service, "create_session"):
                await _maybe_await(perpetual_db_service.create_session(session_data))
        
        return ResponseModel(
            success=True,
            message=f"AI-enhanced perpetual thinking session '{request.session_name}' created successfully",
            data={
                "session_id": session_id,
                "session_name": request.session_name,
                "status": "active",
                "ai_enhancement_level": request.ai_enhancement_level,
                "ai_learning_enabled": request.ai_learning_enabled,
                "ai_adaptation_enabled": request.ai_adaptation_enabled,
                "ai_breakthrough_detection": request.ai_breakthrough_detection
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create AI-enhanced perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create AI-enhanced perpetual session: {str(e)}")

@app.get("/api/v1/perpetual/sessions/{session_id}", response_model=ResponseModel)
async def get_perpetual_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        orchestration_session = orchestration_system.get_orchestration_session_status(session_id)

        db_session = None
        if perpetual_db_service:
            if hasattr(perpetual_db_service, "get_session"):
                db_session = await _maybe_await(perpetual_db_service.get_session(session_id))
            elif hasattr(perpetual_db_service, "get_perpetual_session"):
                db_session = await _maybe_await(perpetual_db_service.get_perpetual_session(session_id))
            db_session = _normalize_session_payload(db_session)

        if not orchestration_session:
            if db_session:
                return ResponseModel(
                    success=True,
                    message="Perpetual session retrieved successfully",
                    data=db_session
                )
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = {
            "session_id": session_id,
            "session_name": _get_session_value(orchestration_session, "session_name"),
            "initial_input": _get_session_value(orchestration_session, "initial_input"),
            "current_input": _get_session_value(orchestration_session, "current_input"),
            "current_cycle_number": _get_session_value(orchestration_session, "current_cycle_number"),
            "status": _get_session_value(orchestration_session, "status"),
            "mode": _get_session_value(orchestration_session, "mode"),
            "goals": _get_session_value(orchestration_session, "goals", []),
            "success_criteria": _get_session_value(orchestration_session, "success_criteria", []),
            "created_at": _get_session_value(orchestration_session, "created_at"),
            "updated_at": _get_session_value(orchestration_session, "updated_at"),
            "summary_metrics": _get_session_value(orchestration_session, "summary_metrics")
        }
        if hasattr(session_data["mode"], "value"):
            session_data["mode"] = session_data["mode"].value
        session_data = _normalize_session_payload(session_data)
        
        return ResponseModel(
            success=True,
            message="Perpetual session retrieved successfully",
            data=session_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get perpetual session: {str(e)}")

@app.get("/api/v1/perpetual/sessions", response_model=ResponseModel)
async def list_perpetual_sessions(
    status: Optional[str] = None,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """List perpetual thinking sessions"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        sessions_data = []
        if perpetual_db_service and hasattr(perpetual_db_service, "get_all_sessions"):
            db_sessions = await _maybe_await(perpetual_db_service.get_all_sessions(status=status, limit=limit))
            for session in db_sessions:
                normalized = _normalize_session_payload(session)
                if normalized:
                    sessions_data.append(normalized)
        else:
            active_sessions = list(orchestration_system.orchestration_sessions.values())
            if status:
                active_sessions = [s for s in active_sessions if _get_session_value(s, "status") == status]
            active_sessions = active_sessions[:limit]
            for session in active_sessions:
                mode_value = _get_session_value(session, "mode")
                if hasattr(mode_value, "value"):
                    mode_value = mode_value.value
                sessions_data.append({
                    "session_id": _get_session_value(session, "session_id"),
                    "session_name": _get_session_value(session, "session_name"),
                    "status": _get_session_value(session, "status"),
                    "mode": mode_value,
                    "current_cycle_number": _get_session_value(session, "current_cycle_number"),
                    "created_at": _get_session_value(session, "created_at"),
                    "updated_at": _get_session_value(session, "updated_at"),
                    "summary_metrics": _get_session_value(session, "summary_metrics")
                })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(sessions_data)} perpetual sessions",
            data={
                "sessions": sessions_data,
                "total_count": len(sessions_data)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list perpetual sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list perpetual sessions: {str(e)}")

@app.get("/api/v1/perpetual/sessions/{session_id}/cycles", response_model=ResponseModel)
async def get_perpetual_session_cycles(
    session_id: str,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get cycles for a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        cycles = []
        if perpetual_db_service and hasattr(perpetual_db_service, "get_session_cycles"):
            cycles = await _maybe_await(perpetual_db_service.get_session_cycles(session_id, limit))
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(cycles)} cycles for session {session_id}",
            data={
                "session_id": session_id,
                "cycles": cycles,
                "total_count": len(cycles)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get session cycles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session cycles: {str(e)}")

@app.get("/api/v1/perpetual/sessions/{session_id}/breakthroughs", response_model=ResponseModel)
async def get_perpetual_session_breakthroughs(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get breakthrough moments for a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        # Get breakthroughs from orchestration system
        orchestration_session = orchestration_system.get_orchestration_session_status(session_id)
        
        if not orchestration_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get breakthroughs from perpetual engine
        perpetual_session = perpetual_engine.get_session_status(orchestration_session.current_perpetual_session_id)
        
        breakthroughs = []
        if perpetual_session:
            breakthroughs = perpetual_session.breakthrough_moments
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(breakthroughs)} breakthrough moments",
            data={
                "session_id": session_id,
                "breakthroughs": breakthroughs,
                "total_count": len(breakthroughs)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session breakthroughs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session breakthroughs: {str(e)}")

@app.post("/api/v1/perpetual/sessions/{session_id}/pause", response_model=ResponseModel)
async def pause_perpetual_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Pause a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        await orchestration_system.pause_orchestration_session(session_id)
        
        return ResponseModel(
            success=True,
            message=f"Perpetual session {session_id} paused successfully",
            data={"session_id": session_id, "status": "paused"}
        )
        
    except Exception as e:
        logger.error(f"Failed to pause perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pause perpetual session: {str(e)}")

@app.post("/api/v1/perpetual/sessions/{session_id}/resume", response_model=ResponseModel)
async def resume_perpetual_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Resume a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        await orchestration_system.resume_orchestration_session(session_id)
        
        return ResponseModel(
            success=True,
            message=f"Perpetual session {session_id} resumed successfully",
            data={"session_id": session_id, "status": "active"}
        )
        
    except Exception as e:
        logger.error(f"Failed to resume perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume perpetual session: {str(e)}")

@app.post("/api/v1/perpetual/sessions/{session_id}/stop", response_model=ResponseModel)
async def stop_perpetual_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Stop a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        await orchestration_system.stop_orchestration_session(session_id)
        
        return ResponseModel(
            success=True,
            message=f"Perpetual session {session_id} stopped successfully",
            data={"session_id": session_id, "status": "completed"}
        )
        
    except Exception as e:
        logger.error(f"Failed to stop perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop perpetual session: {str(e)}")

@app.get("/api/v1/perpetual/metrics", response_model=ResponseModel)
async def get_perpetual_system_metrics(
    metric_name: Optional[str] = None,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get perpetual thinking system metrics"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        metrics = []
        if perpetual_db_service and hasattr(perpetual_db_service, "get_system_metrics"):
            metrics = await _maybe_await(perpetual_db_service.get_system_metrics(metric_name, limit))
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(metrics)} system metrics",
            data={
                "metrics": metrics,
                "total_count": len(metrics)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")

@app.get("/api/v1/perpetual/status", response_model=ResponseModel)
async def get_perpetual_system_status(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI-enhanced perpetual thinking system status"""
    if not PERPETUAL_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Perpetual thinking system not available")
    
    try:
        active_sessions = 0
        total_sessions = 0
        if perpetual_db_service and hasattr(perpetual_db_service, "get_all_sessions"):
            sessions = await _maybe_await(perpetual_db_service.get_all_sessions())
            total_sessions = _safe_len(sessions)
            active_sessions = sum(
                1 for session in sessions
                if _get_session_value(session, "status") == "active"
            )
        elif orchestration_system:
            active_sessions = _safe_len(getattr(orchestration_system, "orchestration_sessions", []))
            total_sessions = _safe_len(getattr(orchestration_system, "session_history", [])) or active_sessions

        active_ai_sessions = _safe_len(getattr(perpetual_ai_engine, "ai_sessions", [])) if perpetual_ai_engine else 0
        
        status_data = {
            "system_available": True,
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "active_ai_sessions": active_ai_sessions,
            "database_available": perpetual_db_service is not None,
            "perpetual_engine_available": perpetual_engine is not None,
            "perpetual_ai_engine_available": perpetual_ai_engine is not None,
            "orchestration_system_available": orchestration_system is not None,
            "guardrail_integration_available": perpetual_guardrail_integration is not None,
            "policy_enforcer_available": perpetual_policy_enforcer is not None,
            "ai_enhancement_available": perpetual_ai_engine is not None
        }
        
        return ResponseModel(
            success=True,
            message="AI-enhanced perpetual thinking system status retrieved successfully",
            data=status_data
        )
        
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

# AI-Enhanced Perpetual Thinking Endpoints

@app.get("/api/v1/perpetual/ai/sessions/{session_id}/analytics", response_model=ResponseModel)
async def get_ai_session_analytics(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI session analytics for a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_ai_engine:
        raise HTTPException(status_code=503, detail="AI-enhanced perpetual thinking system not available")
    
    try:
        analytics = await _maybe_await(perpetual_ai_engine.get_ai_session_analytics(session_id))
        
        if analytics is None:
            raise HTTPException(status_code=404, detail="AI session not found")
        
        return ResponseModel(
            success=True,
            message="AI session analytics retrieved successfully",
            data=analytics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get AI session analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI session analytics: {str(e)}")

@app.get("/api/v1/perpetual/ai/sessions/{session_id}/status", response_model=ResponseModel)
async def get_ai_enhanced_cycle_status(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI-enhanced cycle status for a perpetual thinking session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_ai_engine:
        raise HTTPException(status_code=503, detail="AI-enhanced perpetual thinking system not available")
    
    try:
        # Get AI-enhanced cycle status
        status = await _maybe_await(perpetual_ai_engine.get_ai_enhanced_cycle_status(session_id))
        
        if status is None:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return ResponseModel(
            success=True,
            message="AI-enhanced cycle status retrieved successfully",
            data=status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get AI-enhanced cycle status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI-enhanced cycle status: {str(e)}")

@app.get("/api/v1/perpetual/ai/sessions", response_model=ResponseModel)
async def list_ai_sessions(
    ai_enhancement_level: Optional[str] = None,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """List AI-enhanced perpetual thinking sessions"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_ai_engine:
        raise HTTPException(status_code=503, detail="AI-enhanced perpetual thinking system not available")
    
    try:
        # Get AI sessions
        ai_sessions = list(perpetual_ai_engine.ai_sessions.values())
        
        # Filter by AI enhancement level if provided
        if ai_enhancement_level:
            try:
                enhancement_level = AIEnhancementLevel(ai_enhancement_level)
                target_level = enhancement_level.value
                ai_sessions = [
                    s for s in ai_sessions
                    if (_get_session_value(s, "ai_enhancement_level") and (
                        _get_session_value(s, "ai_enhancement_level").value
                        if hasattr(_get_session_value(s, "ai_enhancement_level"), "value")
                        else str(_get_session_value(s, "ai_enhancement_level"))
                    )) == target_level
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid AI enhancement level: {ai_enhancement_level}")
        
        # Limit results
        ai_sessions = ai_sessions[:limit]
        
        sessions_data = []
        for session in ai_sessions:
            session_level = _get_session_value(session, "ai_enhancement_level")
            session_level_value = session_level.value if hasattr(session_level, "value") else session_level
            created_at = _get_session_value(session, "created_at")
            updated_at = _get_session_value(session, "updated_at")
            metrics = _get_session_value(session, "ai_collaborative_metrics")
            metrics_payload = {}
            if isinstance(metrics, dict):
                metrics_payload = {
                    "ai_contribution_score": metrics.get("ai_contribution_score", 0.0),
                    "human_contribution_score": metrics.get("human_contribution_score", 0.0),
                    "synergy_score": metrics.get("synergy_score", 0.0),
                    "wisdom_density": metrics.get("wisdom_density", 0.0),
                    "creative_potential": metrics.get("creative_potential", 0.0),
                    "learning_velocity": metrics.get("learning_velocity", 0.0),
                    "adaptation_rate": metrics.get("adaptation_rate", 0.0)
                }
            elif metrics:
                metrics_payload = {
                    "ai_contribution_score": getattr(metrics, "ai_contribution_score", 0.0),
                    "human_contribution_score": getattr(metrics, "human_contribution_score", 0.0),
                    "synergy_score": getattr(metrics, "synergy_score", 0.0),
                    "wisdom_density": getattr(metrics, "wisdom_density", 0.0),
                    "creative_potential": getattr(metrics, "creative_potential", 0.0),
                    "learning_velocity": getattr(metrics, "learning_velocity", 0.0),
                    "adaptation_rate": getattr(metrics, "adaptation_rate", 0.0)
                }
            sessions_data.append({
                "session_id": _get_session_value(session, "session_id"),
                "ai_enhancement_level": session_level_value,
                "ai_learning_enabled": _get_session_value(session, "ai_learning_enabled"),
                "ai_adaptation_enabled": _get_session_value(session, "ai_adaptation_enabled"),
                "ai_breakthrough_detection": _get_session_value(session, "ai_breakthrough_detection"),
                "ai_cycle_enhancements_count": _safe_len(_get_session_value(session, "ai_cycle_enhancements", [])),
                "ai_session_insights_count": _safe_len(_get_session_value(session, "ai_session_insights", [])),
                "ai_learning_history_count": _safe_len(_get_session_value(session, "ai_learning_history", [])),
                "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else created_at,
                "updated_at": updated_at.isoformat() if hasattr(updated_at, "isoformat") else updated_at,
                "ai_collaborative_metrics": metrics_payload
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(sessions_data)} AI-enhanced sessions",
            data={
                "sessions": sessions_data,
                "total_count": len(sessions_data),
                "filters": {
                    "ai_enhancement_level": ai_enhancement_level,
                    "limit": limit
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list AI sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list AI sessions: {str(e)}")

# Policy Enforcement and Audit Logging Endpoints

@app.get("/api/v1/perpetual/audit/logs", response_model=ResponseModel)
async def get_perpetual_audit_logs(
    session_id: Optional[str] = None,
    operation_type: Optional[str] = None,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get audit logs for perpetual thinking operations"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_guardrail_integration:
        raise HTTPException(status_code=503, detail="Perpetual guardrail integration not available")
    
    try:
        logs = perpetual_guardrail_integration.get_audit_logs(
            session_id=session_id,
            operation_type=operation_type,
            limit=limit
        )
        
        # Convert logs to dict format for JSON serialization
        logs_data = []
        for log in logs:
            logs_data.append({
                "log_id": log.log_id,
                "timestamp": log.timestamp.isoformat(),
                "operation_type": log.operation_type,
                "agent_id": log.agent_id,
                "resource_service": log.resource_service,
                "resource_action": log.resource_action,
                "policy_decision": log.policy_decision,
                "policy_packages": log.policy_packages,
                "obligations": log.obligations,
                "context": log.context,
                "explanation": log.explanation,
                "latency_ms": log.latency_ms,
                "session_id": log.session_id,
                "cycle_id": log.cycle_id,
                "user_id": log.user_id,
                "violations": log.violations,
                "risk_score": log.risk_score
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(logs_data)} audit logs",
            data={
                "logs": logs_data,
                "total_count": len(logs_data),
                "filters": {
                    "session_id": session_id,
                    "operation_type": operation_type,
                    "limit": limit
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {str(e)}")

@app.get("/api/v1/perpetual/audit/violations", response_model=ResponseModel)
async def get_perpetual_policy_violations(
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get policy violations (denied operations)"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_guardrail_integration:
        raise HTTPException(status_code=503, detail="Perpetual guardrail integration not available")
    
    try:
        violations = perpetual_guardrail_integration.get_policy_violations(limit=limit)
        
        # Convert violations to dict format
        violations_data = []
        for violation in violations:
            violations_data.append({
                "log_id": violation.log_id,
                "timestamp": violation.timestamp.isoformat(),
                "operation_type": violation.operation_type,
                "agent_id": violation.agent_id,
                "resource_service": violation.resource_service,
                "resource_action": violation.resource_action,
                "policy_packages": violation.policy_packages,
                "obligations": violation.obligations,
                "context": violation.context,
                "explanation": violation.explanation,
                "session_id": violation.session_id,
                "cycle_id": violation.cycle_id,
                "user_id": violation.user_id,
                "violations": violation.violations,
                "risk_score": violation.risk_score
            })
        
        return ResponseModel(
            success=True,
            message=f"Retrieved {len(violations_data)} policy violations",
            data={
                "violations": violations_data,
                "total_count": len(violations_data),
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get policy violations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get policy violations: {str(e)}")

@app.get("/api/v1/perpetual/audit/risk-summary", response_model=ResponseModel)
async def get_perpetual_risk_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get risk summary for perpetual thinking operations"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_guardrail_integration:
        raise HTTPException(status_code=503, detail="Perpetual guardrail integration not available")
    
    try:
        risk_summary = perpetual_guardrail_integration.get_risk_summary()
        
        return ResponseModel(
            success=True,
            message="Risk summary retrieved successfully",
            data=risk_summary
        )
        
    except Exception as e:
        logger.error(f"Failed to get risk summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get risk summary: {str(e)}")

@app.post("/api/v1/perpetual/policy/evaluate", response_model=ResponseModel)
async def evaluate_perpetual_policy(
    request: PolicyEvaluateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Evaluate a perpetual thinking operation against policies"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_guardrail_integration:
        raise HTTPException(status_code=503, detail="Perpetual guardrail integration not available")
    
    try:
        # Convert string enums to enum objects
        try:
            op_type = PerpetualPolicyType(request.operation_type)
            act_type = PerpetualActionType(request.action_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid operation or action type: {e}. Valid operation types: {[t.value for t in PerpetualPolicyType]}. Valid action types: {[a.value for a in PerpetualActionType]}")
        
        # Create policy context with defaults for missing fields
        policy_context = PerpetualPolicyContext(**request.context)
        
        # Evaluate policy
        allow, meta = await perpetual_guardrail_integration.evaluate_perpetual_operation(
            operation_type=op_type,
            action_type=act_type,
            agent_id=request.agent_id,
            context=policy_context
        )
        
        return ResponseModel(
            success=True,
            message="Policy evaluation completed",
            data={
                "decision": "allow" if allow else "deny",
                "allow": allow,
                "metadata": meta,
                "operation_type": request.operation_type,
                "action_type": request.action_type,
                "agent_id": request.agent_id,
                "policy_id": meta.get("policy_id", "default"),
                "rationale": meta.get("explanation", {}).get("reasoning", "Policy evaluation completed")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate policy: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to evaluate policy: {str(e)}")

# 108-Cycle Fractal Integration Endpoints

class FractalPerpetualSessionRequest(BaseModel):
    """Request model for creating a fractal-perpetual integrated session"""
    session_name: str = Field(..., min_length=1, max_length=255, description="Session name")
    initial_input: str = Field(..., min_length=1, description="Initial input for the session")
    integration_mode: str = Field(default="integrated", description="Integration mode")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")

class FractalPerpetualSessionResponse(BaseModel):
    """Response model for fractal-perpetual integrated session"""
    session_id: str
    session_name: str
    integration_mode: str
    fractal_result: Dict[str, Any]
    perpetual_result: Dict[str, Any]
    integration_insights: Dict[str, Any]
    cross_system_patterns: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    execution_time: float
    success: bool
    errors: List[str] = []

@app.post("/api/v1/fractal-perpetual/sessions", response_model=ResponseModel)
async def create_fractal_perpetual_session(
    request: FractalPerpetualSessionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new fractal-perpetual integrated session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_108_cycle_integration:
        raise HTTPException(status_code=503, detail="Fractal-perpetual integration not available")
    
    try:
        # Convert integration mode string to enum
        try:
            integration_mode = PerpetualFractalMode(request.integration_mode)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid integration mode: {request.integration_mode}")
        
        # Execute integrated session
        result = await perpetual_108_cycle_integration.execute_integrated_session(
            session_name=request.session_name,
            initial_input=request.initial_input,
            integration_mode=integration_mode,
            context=request.context
        )
        
        return ResponseModel(
            success=result.success,
            message=f"Fractal-perpetual session '{request.session_name}' executed successfully",
            data={
                "session_id": str(uuid.uuid4()),
                "session_name": request.session_name,
                "integration_mode": request.integration_mode,
                "fractal_result": result.fractal_result,
                "perpetual_result": result.perpetual_result,
                "integration_insights": result.integration_insights,
                "cross_system_patterns": result.cross_system_patterns,
                "performance_metrics": result.performance_metrics,
                "execution_time": result.execution_time,
                "success": result.success,
                "errors": result.errors
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to create fractal-perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create fractal-perpetual session: {str(e)}")

@app.get("/api/v1/fractal-perpetual/analytics", response_model=ResponseModel)
async def get_fractal_perpetual_analytics(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get analytics for fractal-perpetual integration"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_108_cycle_integration:
        raise HTTPException(status_code=503, detail="Fractal-perpetual integration not available")
    
    try:
        analytics = perpetual_108_cycle_integration.get_integration_analytics()
        
        return ResponseModel(
            success=True,
            message="Fractal-perpetual analytics retrieved successfully",
            data=analytics
        )
        
    except Exception as e:
        logger.error(f"Failed to get fractal-perpetual analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get fractal-perpetual analytics: {str(e)}")

@app.get("/api/v1/fractal-perpetual/insights/{session_id}", response_model=ResponseModel)
async def get_fractal_perpetual_insights(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get cross-system insights for a fractal-perpetual session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_108_cycle_integration:
        raise HTTPException(status_code=503, detail="Fractal-perpetual integration not available")
    
    try:
        insights = perpetual_108_cycle_integration.get_cross_system_insights(session_id)
        
        if insights is None:
            raise HTTPException(status_code=404, detail="Session insights not found")
        
        return ResponseModel(
            success=True,
            message="Cross-system insights retrieved successfully",
            data={
                "session_id": session_id,
                "insights": insights
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cross-system insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cross-system insights: {str(e)}")

@app.get("/api/v1/fractal-perpetual/status/{session_id}", response_model=ResponseModel)
async def get_fractal_perpetual_status(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get status of a fractal-perpetual integration session"""
    if not PERPETUAL_SYSTEM_AVAILABLE or not perpetual_108_cycle_integration:
        raise HTTPException(status_code=503, detail="Fractal-perpetual integration not available")
    
    try:
        status = perpetual_108_cycle_integration.get_integration_status(session_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Session status not found")
        
        return ResponseModel(
            success=True,
            message="Integration session status retrieved successfully",
            data=status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get integration status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with enhanced error format"""
    try:
        # Check if detail is already a dict (enhanced error format)
        if isinstance(exc.detail, dict):
            error_data = exc.detail
        else:
            # Convert simple string detail to enhanced format
            error_data = {
                "error_code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "status_code": exc.status_code
            }

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": error_data.get("message", "An error occurred"),
                "data": error_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            headers=exc.headers,
        )
    except Exception as e:
        # Fallback if ResponseModel fails
        logger.error(f"Error in HTTP exception handler: {e}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail) if not isinstance(exc.detail, dict) else exc.detail.get("message", "An error occurred"),
                "data": exc.detail if isinstance(exc.detail, dict) else {"status_code": exc.status_code},
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            headers=exc.headers,
        )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ResponseModel(
            success=False,
            message="Internal server error",
            data={"error": str(exc)}
        ).model_dump()
    )

# WebSocket Endpoints

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time hexagon visualization updates"""
    from ..api.websocket_manager import websocket_manager
    
    client_id = None
    try:
        client_id = await websocket_manager.connect(websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "ping":
                # Respond to ping with pong
                await websocket_manager.send_personal_message(websocket, {
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            elif message_type == "subscribe":
                # Subscribe to a topic
                topic = message.get("topic", "all")
                await websocket_manager.subscribe(websocket, topic)
                await websocket_manager.send_personal_message(websocket, {
                    "type": "subscribed",
                    "topic": topic,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            elif message_type == "unsubscribe":
                # Unsubscribe from a topic
                topic = message.get("topic", "all")
                await websocket_manager.unsubscribe(websocket, topic)
                await websocket_manager.send_personal_message(websocket, {
                    "type": "unsubscribed",
                    "topic": topic,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            else:
                # Unknown message type
                await websocket_manager.send_personal_message(websocket, {
                    "type": "error",
                    "error": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, client_id)
        logger.info(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        websocket_manager.disconnect(websocket, client_id)

# Main execution
def main():
    """Main function to start the API server"""
    uvicorn.run(
        "src.cosmic_council.core.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
