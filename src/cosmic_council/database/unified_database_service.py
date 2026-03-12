"""
Unified Database Service for Cosmic Council System
Handles all database operations for the entire system including perpetual thinking, ROYGBV workflow, and core functionality.

This is the primary and only database service file - all other database service files
should import from this unified implementation.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from sqlalchemy import create_engine, select, update, delete, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging
import uuid

# Import the unified database models
from ..core.models import (
    Base,
    # Core models
    Problem, Solution, Cycle, Enterprise, EnterpriseResult, User, Stakeholder, 
    Constraint, SuccessCriterion, SolutionComponent, ImplementationTracking,
    CycleAnalytics, SystemMetrics, AuditLog,
    # ROYGBV workflow models (detailed)
    ResearchCoreProblem, ResearchFinding, ResearchPrioritizedQuestion,
    PlanningRelatedQuestion, PlanningActionPlan, PlanningDependency,
    DevelopmentPrototype, DevelopmentInternalTesting, DevelopmentCreativeNote,
    BudgetResourceInventory, BudgetAllocation, BudgetTimeCostAnalysis,
    MarketInsight, MarketCommunicationStrategy, MarketPerformanceMetric,
    SupportUserFeedback, SupportPerformanceAssessment, SupportContinuousImprovement,
    # Perpetual thinking models
    PerpetualThinkingSession, PerpetualCycle, PerpetualThinkTankResult,
    BreakthroughMoment, HumanFeedbackPoint, MetaCycle, 
    PerpetualSystemMetrics, PerpetualPatternHistory,
    PerpetualSessionStatus, CycleType, PatternType, MetaCycleType, OrchestrationMode
)

logger = logging.getLogger(__name__)


def _coerce_uuid_if_possible(value: Any) -> Any:
    """Accept UUID objects or UUID-like strings for UUID-typed model columns."""
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except Exception:
        return value

class UnifiedDatabaseService:
    """Unified database service for the entire Cosmic Council system"""
    
    def __init__(self, database_url: str):
        """Initialize the unified database service"""
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        logger.info("🗄️ Unified Database Service initialized")
    
    async def create_tables(self):
        """Create all database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ All database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating database tables: {e}")
            raise
    
    async def drop_tables(self):
        """Drop all database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("✅ All database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"❌ Error dropping database tables: {e}")
            raise
    
    # ============================================================================
    # CORE DATABASE OPERATIONS
    # ============================================================================
    
    async def create_problem(self, problem_data: Dict[str, Any]) -> str:
        """Create a new problem"""
        try:
            async with self.async_session() as session:
                problem = Problem(**problem_data)
                session.add(problem)
                await session.commit()
                await session.refresh(problem)
                logger.info(f"✅ Problem created: {problem.id}")
                return str(problem.id)
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating problem: {e}")
            raise
    
    async def get_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get a problem by ID"""
        try:
            async with self.async_session() as session:
                # Coerce to UUID if necessary
                lookup_id = problem_id
                try:
                    lookup_id = uuid.UUID(problem_id)
                except Exception:
                    pass
                result = await session.execute(
                    select(Problem).where(Problem.id == lookup_id)
                )
                problem = result.scalar_one_or_none()
                if problem:
                    return {
                        'id': str(problem.id),
                        'title': problem.title,
                        'description': problem.description,
                        'domain': problem.domain,
                        'complexity': problem.complexity,
                        'status': problem.status,
                        'created_at': problem.created_at,
                        'updated_at': problem.updated_at
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting problem: {e}")
            raise
    
    async def create_solution(self, solution_data: Dict[str, Any]) -> str:
        """Create a new solution"""
        try:
            async with self.async_session() as session:
                solution = Solution(**solution_data)
                session.add(solution)
                await session.commit()
                await session.refresh(solution)
                logger.info(f"✅ Solution created: {solution.id}")
                return str(solution.id)
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating solution: {e}")
            raise
    
    async def get_solution(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """Get a solution by ID"""
        try:
            lookup_id = _coerce_uuid_if_possible(solution_id)
            async with self.async_session() as session:
                result = await session.execute(
                    select(Solution).where(Solution.id == lookup_id)
                )
                solution = result.scalar_one_or_none()
                if solution:
                    return {
                        'id': str(solution.id),
                        'problem_id': str(solution.problem_id),
                        'title': solution.title,
                        'description': solution.description,
                        'confidence_score': solution.confidence_score,
                        'status': solution.status,
                        'created_at': solution.created_at,
                        'updated_at': solution.updated_at
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting solution: {e}")
            raise
    
    # ============================================================================
    # PERPETUAL THINKING SYSTEM OPERATIONS
    # ============================================================================
    
    async def create_perpetual_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new perpetual thinking session"""
        try:
            async with self.async_session() as session:
                perpetual_session = PerpetualThinkingSession(**session_data)
                session.add(perpetual_session)
                await session.commit()
                await session.refresh(perpetual_session)
                logger.info(f"✅ Perpetual session created: {perpetual_session.id}")
                return str(perpetual_session.id)
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating perpetual session: {e}")
            raise
    
    async def get_perpetual_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a perpetual thinking session by ID"""
        try:
            async with self.async_session() as session:
                lookup_id = session_id
                try:
                    lookup_id = uuid.UUID(session_id)
                except Exception:
                    pass
                result = await session.execute(
                    select(PerpetualThinkingSession)
                    .where(PerpetualThinkingSession.id == lookup_id)
                    .options(selectinload(PerpetualThinkingSession.perpetual_cycles))
                )
                perpetual_session = result.scalar_one_or_none()
                if perpetual_session:
                    return {
                        'id': str(perpetual_session.id),
                        'session_name': perpetual_session.session_name,
                        'initial_input': perpetual_session.initial_input,
                        'current_input': perpetual_session.current_input,
                        'current_cycle_number': perpetual_session.current_cycle_number,
                        'status': perpetual_session.status,
                        'mode': perpetual_session.mode,
                        'goals': perpetual_session.goals,
                        'success_criteria': perpetual_session.success_criteria,
                        'created_at': perpetual_session.created_at,
                        'updated_at': perpetual_session.updated_at,
                        'ended_at': perpetual_session.ended_at,
                        'session_data': perpetual_session.session_data,
                        'summary_metrics': perpetual_session.summary_metrics,
                        'cycles': [
                            {
                                'id': str(cycle.id),
                                'cycle_number': cycle.cycle_number,
                                'cycle_type': cycle.cycle_type,
                                'status': cycle.status,
                                'input_text': cycle.input_text,
                                'output_text': cycle.output_text,
                                'confidence_score': cycle.confidence_score,
                                'started_at': cycle.started_at,
                                'completed_at': cycle.completed_at
                            }
                            for cycle in perpetual_session.perpetual_cycles
                        ]
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting perpetual session: {e}")
            raise
    
    async def update_perpetual_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a perpetual thinking session"""
        try:
            lookup_id = _coerce_uuid_if_possible(session_id)
            async with self.async_session() as session:
                result = await session.execute(
                    update(PerpetualThinkingSession)
                    .where(PerpetualThinkingSession.id == lookup_id)
                    .values(**update_data)
                )
                await session.commit()
                if result.rowcount > 0:
                    logger.info(f"✅ Perpetual session updated: {session_id}")
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"❌ Error updating perpetual session: {e}")
            raise
    
    async def create_perpetual_cycle(self, cycle_data: Dict[str, Any]) -> str:
        """Create a new perpetual cycle"""
        try:
            async with self.async_session() as session:
                perpetual_cycle = PerpetualCycle(**cycle_data)
                session.add(perpetual_cycle)
                await session.commit()
                await session.refresh(perpetual_cycle)
                logger.info(f"✅ Perpetual cycle created: {perpetual_cycle.id}")
                return str(perpetual_cycle.id)
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating perpetual cycle: {e}")
            raise
    
    async def get_perpetual_cycle(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get a perpetual cycle by ID"""
        try:
            async with self.async_session() as session:
                lookup_id = cycle_id
                try:
                    lookup_id = uuid.UUID(cycle_id)
                except Exception:
                    pass
                result = await session.execute(
                    select(PerpetualCycle)
                    .where(PerpetualCycle.id == lookup_id)
                    .options(selectinload(PerpetualCycle.think_tank_results))
                )
                perpetual_cycle = result.scalar_one_or_none()
                if perpetual_cycle:
                    return {
                        'id': str(perpetual_cycle.id),
                        'session_id': str(perpetual_cycle.session_id),
                        'cycle_number': perpetual_cycle.cycle_number,
                        'cycle_type': perpetual_cycle.cycle_type,
                        'status': perpetual_cycle.status,
                        'input_text': perpetual_cycle.input_text,
                        'output_text': perpetual_cycle.output_text,
                        'input_hash': perpetual_cycle.input_hash,
                        'output_hash': perpetual_cycle.output_hash,
                        'new_questions_generated': perpetual_cycle.new_questions_generated,
                        'insights_count': perpetual_cycle.insights_count,
                        'confidence_score': perpetual_cycle.confidence_score,
                        'effectiveness_score': perpetual_cycle.effectiveness_score,
                        'relevance_score': perpetual_cycle.relevance_score,
                        'pattern_detected': perpetual_cycle.pattern_detected,
                        'meta_insights': perpetual_cycle.meta_insights,
                        'started_at': perpetual_cycle.started_at,
                        'completed_at': perpetual_cycle.completed_at,
                        'duration': perpetual_cycle.duration,
                        'think_tank_results': [
                            {
                                'id': str(result.id),
                                'think_tank_name': result.think_tank_name,
                                'phase': result.phase,
                                'input_processed': result.input_processed,
                                'output_generated': result.output_generated,
                                'insights': result.insights,
                                'questions_generated': result.questions_generated,
                                'confidence_score': result.confidence_score,
                                'processing_time': result.processing_time,
                                'started_at': result.started_at,
                                'completed_at': result.completed_at
                            }
                            for result in perpetual_cycle.think_tank_results
                        ]
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting perpetual cycle: {e}")
            raise
    
    async def update_perpetual_cycle(self, cycle_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a perpetual cycle"""
        try:
            lookup_id = _coerce_uuid_if_possible(cycle_id)
            async with self.async_session() as session:
                result = await session.execute(
                    update(PerpetualCycle)
                    .where(PerpetualCycle.id == lookup_id)
                    .values(**update_data)
                )
                await session.commit()
                if result.rowcount > 0:
                    logger.info(f"✅ Perpetual cycle updated: {cycle_id}")
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"❌ Error updating perpetual cycle: {e}")
            raise
    
    async def create_breakthrough_moment(self, breakthrough_data: Dict[str, Any]) -> str:
        """Create a new breakthrough moment"""
        try:
            async with self.async_session() as session:
                breakthrough = BreakthroughMoment(**breakthrough_data)
                session.add(breakthrough)
                await session.commit()
                await session.refresh(breakthrough)
                logger.info(f"✅ Breakthrough moment created: {breakthrough.id}")
                return str(breakthrough.id)
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating breakthrough moment: {e}")
            raise
    
    async def get_breakthrough_moments(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all breakthrough moments for a session"""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(BreakthroughMoment)
                    .where(BreakthroughMoment.session_id == session_id)
                    .order_by(BreakthroughMoment.occurred_at.desc())
                )
                breakthroughs = result.scalars().all()
                return [
                    {
                        'id': str(breakthrough.id),
                        'session_id': str(breakthrough.session_id),
                        'cycle_id': str(breakthrough.cycle_id) if breakthrough.cycle_id else None,
                        'breakthrough_type': breakthrough.breakthrough_type,
                        'description': breakthrough.description,
                        'significance_score': breakthrough.significance_score,
                        'insights': breakthrough.insights,
                        'implications': breakthrough.implications,
                        'occurred_at': breakthrough.occurred_at,
                        'created_at': breakthrough.created_at
                    }
                    for breakthrough in breakthroughs
                ]
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting breakthrough moments: {e}")
            raise
    
    async def create_human_feedback_point(self, feedback_data: Dict[str, Any]) -> str:
        """Create a new human feedback point"""
        try:
            async with self.async_session() as session:
                feedback = HumanFeedbackPoint(**feedback_data)
                session.add(feedback)
                await session.commit()
                await session.refresh(feedback)
                logger.info(f"✅ Human feedback point created: {feedback.id}")
                return str(feedback.id)
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating human feedback point: {e}")
            raise
    
    async def get_human_feedback_points(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all human feedback points for a session"""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(HumanFeedbackPoint)
                    .where(HumanFeedbackPoint.session_id == session_id)
                    .order_by(HumanFeedbackPoint.provided_at.desc())
                )
                feedback_points = result.scalars().all()
                return [
                    {
                        'id': str(feedback.id),
                        'session_id': str(feedback.session_id),
                        'cycle_id': str(feedback.cycle_id) if feedback.cycle_id else None,
                        'feedback_type': feedback.feedback_type,
                        'feedback_content': feedback.feedback_content,
                        'human_identifier': feedback.human_identifier,
                        'impact_score': feedback.impact_score,
                        'provided_at': feedback.provided_at,
                        'created_at': feedback.created_at
                    }
                    for feedback in feedback_points
                ]
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting human feedback points: {e}")
            raise
    
    # ============================================================================
    # ROYGBV WORKFLOW OPERATIONS
    # ============================================================================
    
    async def create_red_owl_genesis(self, genesis_data: Dict[str, Any]) -> str:
        """Create a new Red Owl Genesis record"""
        try:
            async with self.async_session() as session:
                genesis = RedOwlGenesis(**genesis_data)
                session.add(genesis)
                await session.commit()
                await session.refresh(genesis)
                logger.info(f"✅ Red Owl Genesis created: {genesis.id}")
                return str(genesis.id)
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating Red Owl Genesis: {e}")
            raise
    
    async def get_red_owl_genesis(self, genesis_id: str) -> Optional[Dict[str, Any]]:
        """Get a Red Owl Genesis record by ID"""
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(RedOwlGenesis).where(RedOwlGenesis.id == genesis_id)
                )
                genesis = result.scalar_one_or_none()
                if genesis:
                    return {
                        'id': str(genesis.id),
                        'cycle_id': str(genesis.cycle_id),
                        'problem_analysis': genesis.problem_analysis,
                        'stakeholder_identification': genesis.stakeholder_identification,
                        'context_mapping': genesis.context_mapping,
                        'initial_insights': genesis.initial_insights,
                        'confidence_score': genesis.confidence_score,
                        'processing_time': genesis.processing_time,
                        'created_at': genesis.created_at,
                        'updated_at': genesis.updated_at
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting Red Owl Genesis: {e}")
            raise
    
    # Similar methods for other ROYGBV enterprises...
    # (OrangeOrangutanLogistics, YellowHoneybeeInnovation, etc.)
    
    # ============================================================================
    # ANALYTICS AND METRICS OPERATIONS
    # ============================================================================
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        try:
            async with self.async_session() as session:
                # Get core system metrics
                core_metrics_result = await session.execute(
                    select(SystemMetrics).order_by(SystemMetrics.recorded_at.desc()).limit(1)
                )
                core_metrics = core_metrics_result.scalar_one_or_none()
                
                # Get perpetual system metrics
                perpetual_metrics_result = await session.execute(
                    select(PerpetualSystemMetrics).order_by(PerpetualSystemMetrics.recorded_at.desc()).limit(1)
                )
                perpetual_metrics = perpetual_metrics_result.scalar_one_or_none()
                
                # Get counts
                problems_count = await session.execute(select(func.count(Problem.id)))
                solutions_count = await session.execute(select(func.count(Solution.id)))
                cycles_count = await session.execute(select(func.count(Cycle.id)))
                perpetual_sessions_count = await session.execute(select(func.count(PerpetualThinkingSession.id)))
                
                return {
                    'core_metrics': {
                        'total_problems': problems_count.scalar() or 0,
                        'total_solutions': solutions_count.scalar() or 0,
                        'total_cycles': cycles_count.scalar() or 0,
                        'avg_cycle_duration': core_metrics.avg_cycle_duration if core_metrics else 0.0,
                        'avg_solution_confidence': core_metrics.avg_solution_confidence if core_metrics else 0.0,
                        'system_uptime': core_metrics.system_uptime if core_metrics else 0.0
                    },
                    'perpetual_metrics': {
                        'total_sessions': perpetual_sessions_count.scalar() or 0,
                        'total_cycles': perpetual_metrics.total_cycles if perpetual_metrics else 0,
                        'total_breakthroughs': perpetual_metrics.total_breakthroughs if perpetual_metrics else 0,
                        'avg_cycle_duration': perpetual_metrics.avg_cycle_duration if perpetual_metrics else 0.0,
                        'avg_confidence_score': perpetual_metrics.avg_confidence_score if perpetual_metrics else 0.0,
                        'system_uptime': perpetual_metrics.system_uptime if perpetual_metrics else 0.0
                    }
                }
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting system metrics: {e}")
            raise
    
    async def record_system_metrics(self, metrics_data: Dict[str, Any]) -> str:
        """Record new system metrics"""
        try:
            async with self.async_session() as session:
                metrics = SystemMetrics(**metrics_data)
                session.add(metrics)
                await session.commit()
                await session.refresh(metrics)
                logger.info(f"✅ System metrics recorded: {metrics.id}")
                return str(metrics.id)
        except SQLAlchemyError as e:
            logger.error(f"❌ Error recording system metrics: {e}")
            raise
    
    # ============================================================================
    # UTILITY OPERATIONS
    # ============================================================================
    
    async def close(self):
        """Close the database connection"""
        try:
            await self.engine.dispose()
            logger.info("✅ Database connection closed")
        except SQLAlchemyError as e:
            logger.error(f"❌ Error closing database connection: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the database"""
        try:
            async with self.async_session() as session:
                # Test basic connectivity
                result = await session.execute(select(func.now()))
                current_time = result.scalar()
                
                # Test table access
                problems_count = await session.execute(select(func.count(Problem.id)))
                problems_total = problems_count.scalar() or 0
                
                return {
                    'status': 'healthy',
                    'database_time': current_time.isoformat() if current_time else None,
                    'problems_count': problems_total,
                    'connection_status': 'active'
                }
        except SQLAlchemyError as e:
            logger.error(f"❌ Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection_status': 'failed'
            }

# Backward-compatible alias used by older imports
class DatabaseService(UnifiedDatabaseService):
    """Compatibility wrapper for legacy DatabaseService imports."""

# ============================================================================
# BACKWARD COMPATIBILITY WRAPPERS
# ============================================================================

class PerpetualDatabaseService:
    """
    Backward compatibility wrapper for the original PerpetualDatabaseService.
    This class provides the same interface as the original but uses the unified implementation.
    """
    
    def __init__(self, database_url: str):
        """Initialize with backward compatibility"""
        self.unified_service = UnifiedDatabaseService(database_url)
        self.database_url = database_url
        self.engine = self.unified_service.engine
        self.async_session = self.unified_service.async_session
        logger.info("🗄️ Perpetual Database Service (backward compatibility) initialized")
    
    async def create_tables(self):
        """Create all database tables"""
        return await self.unified_service.create_tables()
    
    async def create_perpetual_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new perpetual thinking session"""
        return await self.unified_service.create_perpetual_session(session_data)

    async def save_perpetual_session(self, session_data: Dict[str, Any]) -> str:
        """Save a perpetual session payload with compatibility mapping"""
        allowed_fields = {
            "id",
            "session_name",
            "initial_input",
            "current_input",
            "current_cycle_number",
            "status",
            "mode",
            "goals",
            "success_criteria",
            "created_at",
            "updated_at",
            "ended_at",
            "session_data",
            "summary_metrics",
        }
        payload = {k: session_data[k] for k in allowed_fields if k in session_data}
        if "session_id" in session_data and "id" not in payload:
            try:
                payload["id"] = uuid.UUID(session_data["session_id"])
            except Exception:
                payload["id"] = uuid.uuid4()
        extras = {
            k: v for k, v in session_data.items()
            if k not in allowed_fields and k != "session_id"
        }
        if extras:
            base_data = payload.get("session_data") or {}
            payload["session_data"] = {**base_data, **extras}
        return await self.unified_service.create_perpetual_session(payload)

    async def get_perpetual_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a perpetual thinking session by ID"""
        return await self.unified_service.get_perpetual_session(session_id)

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Compatibility alias for get_perpetual_session"""
        session = await self.get_perpetual_session(session_id)
        if session and "session_id" not in session and "id" in session:
            session = dict(session)
            session["session_id"] = session["id"]
        return session

    async def get_all_sessions(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List perpetual sessions for API endpoints"""
        try:
            async with self.async_session() as session:
                query = select(PerpetualThinkingSession)
                if status:
                    query = query.where(PerpetualThinkingSession.status == status)
                query = query.order_by(PerpetualThinkingSession.created_at.desc()).limit(limit)
                result = await session.execute(query)
                sessions = result.scalars().all()
                return [
                    {
                        "session_id": str(record.id),
                        "session_name": record.session_name,
                        "status": record.status,
                        "current_cycle_number": record.current_cycle_number,
                        "created_at": record.created_at,
                        "updated_at": record.updated_at,
                        "summary_metrics": record.summary_metrics
                    }
                    for record in sessions
                ]
        except SQLAlchemyError as e:
            logger.error(f"ƒ?O Error listing perpetual sessions: {e}")
            return []
    
    async def update_perpetual_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a perpetual thinking session"""
        return await self.unified_service.update_perpetual_session(session_id, update_data)
    
    async def create_perpetual_cycle(self, cycle_data: Dict[str, Any]) -> str:
        """Create a new perpetual cycle"""
        return await self.unified_service.create_perpetual_cycle(cycle_data)
    
    async def get_perpetual_cycle(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get a perpetual cycle by ID"""
        return await self.unified_service.get_perpetual_cycle(cycle_id)

    async def get_session_cycles(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get cycles for a perpetual session"""
        try:
            async with self.async_session() as session:
                lookup_id = session_id
                try:
                    lookup_id = uuid.UUID(session_id)
                except Exception:
                    pass
                result = await session.execute(
                    select(PerpetualCycle)
                    .where(PerpetualCycle.session_id == lookup_id)
                    .order_by(PerpetualCycle.started_at.desc())
                    .limit(limit)
                )
                cycles = result.scalars().all()
                return [
                    {
                        "cycle_id": str(cycle.id),
                        "session_id": str(cycle.session_id),
                        "cycle_number": cycle.cycle_number,
                        "cycle_type": cycle.cycle_type,
                        "status": cycle.status,
                        "input_text": cycle.input_text,
                        "output_text": cycle.output_text,
                        "confidence_score": cycle.confidence_score,
                        "effectiveness_score": cycle.effectiveness_score,
                        "relevance_score": cycle.relevance_score,
                        "started_at": cycle.started_at,
                        "completed_at": cycle.completed_at,
                        "duration": cycle.duration
                    }
                    for cycle in cycles
                ]
        except SQLAlchemyError as e:
            logger.error(f"ƒ?O Error getting session cycles: {e}")
            return []
    
    async def update_perpetual_cycle(self, cycle_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a perpetual cycle"""
        return await self.unified_service.update_perpetual_cycle(cycle_id, update_data)
    
    async def create_breakthrough_moment(self, breakthrough_data: Dict[str, Any]) -> str:
        """Create a new breakthrough moment"""
        return await self.unified_service.create_breakthrough_moment(breakthrough_data)
    
    async def get_breakthrough_moments(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all breakthrough moments for a session"""
        return await self.unified_service.get_breakthrough_moments(session_id)
    
    async def create_human_feedback_point(self, feedback_data: Dict[str, Any]) -> str:
        """Create a new human feedback point"""
        return await self.unified_service.create_human_feedback_point(feedback_data)
    
    async def get_human_feedback_points(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all human feedback points for a session"""
        return await self.unified_service.get_human_feedback_points(session_id)

    async def get_system_metrics(self, metric_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get system metrics for the perpetual subsystem"""
        try:
            async with self.async_session() as session:
                query = select(PerpetualSystemMetrics).order_by(PerpetualSystemMetrics.recorded_at.desc()).limit(limit)
                result = await session.execute(query)
                metrics = result.scalars().all()
                return [
                    {
                        "id": str(metric.id),
                        "total_sessions": metric.total_sessions,
                        "total_cycles": metric.total_cycles,
                        "total_breakthroughs": metric.total_breakthroughs,
                        "avg_cycle_duration": metric.avg_cycle_duration,
                        "avg_confidence_score": metric.avg_confidence_score,
                        "system_uptime": metric.system_uptime,
                        "recorded_at": metric.recorded_at
                    }
                    for metric in metrics
                ]
        except SQLAlchemyError as e:
            logger.error(f"ƒ?O Error getting system metrics: {e}")
            return []
    
    async def close(self):
        """Close the database connection"""
        return await self.unified_service.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the database"""
        return await self.unified_service.health_check()

# ============================================================================
# EXPORT ALL CLASSES AND FUNCTIONS
# ============================================================================

__all__ = [
    'DatabaseService',
    'UnifiedDatabaseService',
    'PerpetualDatabaseService',  # Backward compatibility
    'Base',  # For table creation
    # Core models
    'Problem', 'Solution', 'Cycle', 'Enterprise', 'EnterpriseResult', 'User', 'Stakeholder',
    'Constraint', 'SuccessCriterion', 'SolutionComponent', 'ImplementationTracking',
    'CycleAnalytics', 'SystemMetrics', 'AuditLog',
    # ROYGBV workflow models (detailed)
    'ResearchCoreProblem', 'ResearchFinding', 'ResearchPrioritizedQuestion',
    'PlanningRelatedQuestion', 'PlanningActionPlan', 'PlanningDependency',
    'DevelopmentPrototype', 'DevelopmentInternalTesting', 'DevelopmentCreativeNote',
    'BudgetResourceInventory', 'BudgetAllocation', 'BudgetTimeCostAnalysis',
    'MarketInsight', 'MarketCommunicationStrategy', 'MarketPerformanceMetric',
    'SupportUserFeedback', 'SupportPerformanceAssessment', 'SupportContinuousImprovement',
    # Perpetual thinking models
    'PerpetualThinkingSession', 'PerpetualCycle', 'PerpetualThinkTankResult',
    'BreakthroughMoment', 'HumanFeedbackPoint', 'MetaCycle',
    'PerpetualSystemMetrics', 'PerpetualPatternHistory',
    'PerpetualSessionStatus', 'CycleType', 'PatternType', 'MetaCycleType', 'OrchestrationMode'
]
