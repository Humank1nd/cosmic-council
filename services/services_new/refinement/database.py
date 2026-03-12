"""
Cosmic Council Refinement Engine - Real Database Integration
Implements actual PostgreSQL integration with proper connection pooling,
transactions, and data persistence.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
import uuid
import json
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

try:
    from .layers import LayerDefinitions
except ImportError:
    # For testing
    from layers import LayerDefinitions
try:
    from .escalator import EscalatorAction
    from .sector_engine import SectorType
except ImportError:
    # For testing
    from escalator import EscalatorAction
    from sector_engine import SectorType


# SQLAlchemy Models
Base = declarative_base()


class ProblemModel(Base):
    """Database model for problems."""
    __tablename__ = "problems"
    
    problem_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    current_layer_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(20), default='open', nullable=False)
    confidence_threshold = Column(Float, default=0.85)
    completeness_threshold = Column(Float, default=0.80)
    max_revolutions_per_layer = Column(Integer, default=3)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    layer_runs = relationship("LayerRunModel", back_populates="problem", cascade="all, delete-orphan")
    refinements = relationship("RefinementModel", back_populates="problem", cascade="all, delete-orphan")
    answers = relationship("AnswerModel", back_populates="problem", cascade="all, delete-orphan")


class LayerRunModel(Base):
    """Database model for layer runs."""
    __tablename__ = "layer_runs"
    
    layer_run_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.problem_id"), nullable=False)
    layer_id = Column(UUID(as_uuid=True), nullable=False)
    revolution = Column(Integer, nullable=False, default=1)
    status = Column(String(20), default='pending', nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    total_cost_usd = Column(Float, default=0.0)
    total_latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    problem = relationship("ProblemModel", back_populates="layer_runs")
    sector_runs = relationship("SectorRunModel", back_populates="layer_run", cascade="all, delete-orphan")


class SectorRunModel(Base):
    """Database model for sector runs."""
    __tablename__ = "sector_runs"
    
    sector_run_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    layer_run_id = Column(UUID(as_uuid=True), ForeignKey("layer_runs.layer_run_id"), nullable=False)
    sector = Column(String(20), nullable=False)
    sector_order = Column(Integer, nullable=False)
    status = Column(String(20), default='pending', nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    output_json = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    layer_run = relationship("LayerRunModel", back_populates="sector_runs")


class RefinementModel(Base):
    """Database model for refinements."""
    __tablename__ = "refinements"
    
    refinement_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.problem_id"), nullable=False)
    from_layer_id = Column(UUID(as_uuid=True), nullable=False)
    to_layer_id = Column(UUID(as_uuid=True), nullable=False)
    rationale = Column(Text, nullable=False)
    refined_question = Column(Text, nullable=False)
    escalator_decision = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    problem = relationship("ProblemModel", back_populates="refinements")


class AnswerModel(Base):
    """Database model for answers."""
    __tablename__ = "answers"
    
    answer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.problem_id"), nullable=False)
    layer_id = Column(UUID(as_uuid=True), nullable=False)
    solution_json = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False)
    completeness_score = Column(Float, nullable=False)
    novelty_score = Column(Float, default=0.0)
    alignment_score = Column(Float, default=1.0)
    net_benefit_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    problem = relationship("ProblemModel", back_populates="answers")


class LayerModel(Base):
    """Database model for layers."""
    __tablename__ = "layers"
    
    layer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(20), unique=True, nullable=False)
    order_idx = Column(Integer, unique=True, nullable=False)
    scale_exponent = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    purpose = Column(Text, nullable=True)
    example_reframing = Column(Text, nullable=True)
    toolchain_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DatabaseManager:
    """
    Real database manager with proper connection pooling and transaction handling.
    """
    
    def __init__(self, database_url: str, pool_size: int = 10, max_overflow: int = 20):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL (PostgreSQL or SQLite)
            pool_size: Connection pool size (PostgreSQL only)
            max_overflow: Maximum overflow connections (PostgreSQL only)
        """
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)
        
        # Check if it's SQLite or PostgreSQL
        is_sqlite = "sqlite" in database_url.lower()
        
        if is_sqlite:
            # SQLite doesn't support connection pooling
            self.engine = create_async_engine(
                database_url,
                echo=False
            )
        else:
            # PostgreSQL with connection pooling
            self.engine = create_async_engine(
                database_url,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
        
        # Create session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Initialize layers if not exists
        asyncio.create_task(self._initialize_layers())
    
    async def _initialize_layers(self):
        """Initialize layer definitions in database."""
        try:
            async with self.async_session() as session:
                # Check if layers exist
                from sqlalchemy import select
                result = await session.execute(select(LayerModel).limit(1))
                if result.scalar_one_or_none() is None:
                    # Insert layer definitions
                    for layer_name in LayerDefinitions.get_layer_order():
                        layer_info = LayerDefinitions.get_layer_summary(layer_name)
                        
                        layer = LayerModel(
                            name=layer_name,
                            order_idx=layer_info["order_index"],
                            scale_exponent=layer_info["scale_exponent"],
                            description=layer_info["description"],
                            purpose=layer_info["purpose"],
                            example_reframing=layer_info["example_reframing"],
                            toolchain_type=layer_info["toolchain_type"]
                        )
                        session.add(layer)
                    
                    await session.commit()
                    self.logger.info("Initialized layer definitions in database")
        except Exception as e:
            self.logger.error(f"Error initializing layers: {e}")
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with proper transaction handling."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Database transaction failed: {e}")
                raise
            finally:
                await session.close()
    
    async def create_problem(
        self,
        title: str,
        description: str,
        initial_layer: str = "deci",
        confidence_threshold: float = 0.85,
        completeness_threshold: float = 0.80,
        max_revolutions_per_layer: int = 3
    ) -> str:
        """
        Create a new problem in the database.
        
        Args:
            title: Problem title
            description: Problem description
            initial_layer: Initial layer name
            confidence_threshold: Confidence threshold
            completeness_threshold: Completeness threshold
            max_revolutions_per_layer: Max revolutions per layer
            
        Returns:
            Problem ID
        """
        async with self.get_session() as session:
            # Get layer ID
            from sqlalchemy import select
            layer_result = await session.execute(
                select(LayerModel.layer_id).where(LayerModel.name == initial_layer)
            )
            layer_id = layer_result.scalar_one_or_none()
            
            if not layer_id:
                raise ValueError(f"Layer {initial_layer} not found")
            
            # Create problem
            problem = ProblemModel(
                title=title,
                description=description,
                current_layer_id=layer_id,
                confidence_threshold=confidence_threshold,
                completeness_threshold=completeness_threshold,
                max_revolutions_per_layer=max_revolutions_per_layer
            )
            
            session.add(problem)
            await session.flush()  # Get the ID
            
            problem_id = str(problem.problem_id)
            self.logger.info(f"Created problem {problem_id} in database")
            
            return problem_id
    
    async def get_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """
        Get problem by ID.
        
        Args:
            problem_id: Problem ID
            
        Returns:
            Problem data or None
        """
        async with self.get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(ProblemModel).where(ProblemModel.problem_id == problem_id)
            )
            problem = result.scalar_one_or_none()
            
            if not problem:
                return None
            
            return {
                "problem_id": str(problem.problem_id),
                "title": problem.title,
                "description": problem.description,
                "current_layer_id": str(problem.current_layer_id) if problem.current_layer_id else None,
                "status": problem.status,
                "confidence_threshold": problem.confidence_threshold,
                "completeness_threshold": problem.completeness_threshold,
                "max_revolutions_per_layer": problem.max_revolutions_per_layer,
                "created_at": problem.created_at.isoformat(),
                "updated_at": problem.updated_at.isoformat()
            }
    
    async def create_layer_run(
        self,
        problem_id: str,
        layer: str,
        revolution: int
    ) -> str:
        """
        Create a new layer run.
        
        Args:
            problem_id: Problem ID
            layer: Layer name
            revolution: Revolution number
            
        Returns:
            Layer run ID
        """
        async with self.get_session() as session:
            # Get layer ID
            from sqlalchemy import select
            layer_result = await session.execute(
                select(LayerModel.layer_id).where(LayerModel.name == layer)
            )
            layer_id = layer_result.scalar_one_or_none()
            
            if not layer_id:
                raise ValueError(f"Layer {layer} not found")
            
            # Create layer run
            layer_run = LayerRunModel(
                problem_id=problem_id,
                layer_id=layer_id,
                revolution=revolution
            )
            
            session.add(layer_run)
            await session.flush()
            
            layer_run_id = str(layer_run.layer_run_id)
            self.logger.info(f"Created layer run {layer_run_id} for problem {problem_id}")
            
            return layer_run_id
    
    async def update_layer_run(
        self,
        layer_run_id: str,
        status: str,
        started_at: Optional[datetime] = None,
        finished_at: Optional[datetime] = None,
        total_cost_usd: float = 0.0,
        total_latency_ms: int = 0,
        metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Update layer run with completion data.
        
        Args:
            layer_run_id: Layer run ID
            status: New status
            started_at: Start timestamp
            finished_at: Finish timestamp
            total_cost_usd: Total cost
            total_latency_ms: Total latency
            metrics: Performance metrics
        """
        async with self.get_session() as session:
            from sqlalchemy import select, update
            await session.execute(
                update(LayerRunModel)
                .where(LayerRunModel.layer_run_id == layer_run_id)
                .values(
                    status=status,
                    started_at=started_at,
                    finished_at=finished_at,
                    total_cost_usd=total_cost_usd,
                    total_latency_ms=total_latency_ms
                )
            )
            
            self.logger.info(f"Updated layer run {layer_run_id} with status {status}")
    
    async def create_sector_run(
        self,
        layer_run_id: str,
        sector: str,
        sector_order: int,
        output_json: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> str:
        """
        Create a sector run record.
        
        Args:
            layer_run_id: Layer run ID
            sector: Sector name
            sector_order: Sector order
            output_json: Output data
            metrics: Performance metrics
            error_message: Error message if failed
            
        Returns:
            Sector run ID
        """
        async with self.get_session() as session:
            sector_run = SectorRunModel(
                layer_run_id=layer_run_id,
                sector=sector,
                sector_order=sector_order,
                output_json=output_json,
                metrics=metrics,
                error_message=error_message
            )
            
            session.add(sector_run)
            await session.flush()
            
            sector_run_id = str(sector_run.sector_run_id)
            self.logger.info(f"Created sector run {sector_run_id} for {sector} sector")
            
            return sector_run_id
    
    async def create_refinement(
        self,
        problem_id: str,
        from_layer: str,
        to_layer: str,
        rationale: str,
        refined_question: str,
        escalator_decision: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a refinement record.
        
        Args:
            problem_id: Problem ID
            from_layer: Source layer name
            to_layer: Target layer name
            rationale: Refinement rationale
            refined_question: Refined question
            escalator_decision: Escalator decision data
            
        Returns:
            Refinement ID
        """
        async with self.get_session() as session:
            # Get layer IDs
            from sqlalchemy import select
            from_layer_result = await session.execute(
                select(LayerModel.layer_id).where(LayerModel.name == from_layer)
            )
            from_layer_id = from_layer_result.scalar_one_or_none()
            
            to_layer_result = await session.execute(
                select(LayerModel.layer_id).where(LayerModel.name == to_layer)
            )
            to_layer_id = to_layer_result.scalar_one_or_none()
            
            if not from_layer_id or not to_layer_id:
                raise ValueError(f"Layers {from_layer} or {to_layer} not found")
            
            # Create refinement
            refinement = RefinementModel(
                problem_id=problem_id,
                from_layer_id=from_layer_id,
                to_layer_id=to_layer_id,
                rationale=rationale,
                refined_question=refined_question,
                escalator_decision=escalator_decision
            )
            
            session.add(refinement)
            await session.flush()
            
            refinement_id = str(refinement.refinement_id)
            self.logger.info(f"Created refinement {refinement_id} from {from_layer} to {to_layer}")
            
            return refinement_id
    
    async def create_answer(
        self,
        problem_id: str,
        layer: str,
        solution_json: Dict[str, Any],
        confidence_score: float,
        completeness_score: float,
        novelty_score: float = 0.0,
        alignment_score: float = 1.0,
        net_benefit_score: float = 0.0
    ) -> str:
        """
        Create an answer record.
        
        Args:
            problem_id: Problem ID
            layer: Layer name
            solution_json: Solution data
            confidence_score: Confidence score
            completeness_score: Completeness score
            novelty_score: Novelty score
            alignment_score: Alignment score
            net_benefit_score: Net benefit score
            
        Returns:
            Answer ID
        """
        async with self.get_session() as session:
            # Get layer ID
            from sqlalchemy import select
            layer_result = await session.execute(
                select(LayerModel.layer_id).where(LayerModel.name == layer)
            )
            layer_id = layer_result.scalar_one_or_none()
            
            if not layer_id:
                raise ValueError(f"Layer {layer} not found")
            
            # Create answer
            answer = AnswerModel(
                problem_id=problem_id,
                layer_id=layer_id,
                solution_json=solution_json,
                confidence_score=confidence_score,
                completeness_score=completeness_score,
                novelty_score=novelty_score,
                alignment_score=alignment_score,
                net_benefit_score=net_benefit_score
            )
            
            session.add(answer)
            await session.flush()
            
            answer_id = str(answer.answer_id)
            self.logger.info(f"Created answer {answer_id} for problem {problem_id}")
            
            return answer_id
    
    async def get_problem_genealogy(self, problem_id: str) -> Dict[str, Any]:
        """
        Get complete problem genealogy from database.
        
        Args:
            problem_id: Problem ID
            
        Returns:
            Genealogy data
        """
        async with self.get_session() as session:
            from sqlalchemy import select
            
            # Get problem
            problem_result = await session.execute(
                select(ProblemModel).where(ProblemModel.problem_id == problem_id)
            )
            problem = problem_result.scalar_one_or_none()
            
            if not problem:
                return {"error": "Problem not found"}
            
            # Get layer runs
            layer_runs_result = await session.execute(
                select(LayerRunModel).where(LayerRunModel.problem_id == problem_id)
            )
            layer_runs = layer_runs_result.scalars().all()
            
            # Get refinements
            refinements_result = await session.execute(
                select(RefinementModel).where(RefinementModel.problem_id == problem_id)
            )
            refinements = refinements_result.scalars().all()
            
            # Get answers
            answers_result = await session.execute(
                select(AnswerModel).where(AnswerModel.problem_id == problem_id)
            )
            answers = answers_result.scalars().all()
            
            return {
                "problem_id": str(problem.problem_id),
                "title": problem.title,
                "description": problem.description,
                "status": problem.status,
                "layer_runs": [
                    {
                        "layer_run_id": str(lr.layer_run_id),
                        "layer_id": str(lr.layer_id),
                        "revolution": lr.revolution,
                        "status": lr.status,
                        "started_at": lr.started_at.isoformat() if lr.started_at else None,
                        "finished_at": lr.finished_at.isoformat() if lr.finished_at else None,
                        "total_cost_usd": lr.total_cost_usd,
                        "total_latency_ms": lr.total_latency_ms
                    }
                    for lr in layer_runs
                ],
                "refinements": [
                    {
                        "refinement_id": str(r.refinement_id),
                        "from_layer_id": str(r.from_layer_id),
                        "to_layer_id": str(r.to_layer_id),
                        "rationale": r.rationale,
                        "refined_question": r.refined_question,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in refinements
                ],
                "answers": [
                    {
                        "answer_id": str(a.answer_id),
                        "layer_id": str(a.layer_id),
                        "confidence_score": a.confidence_score,
                        "completeness_score": a.completeness_score,
                        "created_at": a.created_at.isoformat()
                    }
                    for a in answers
                ]
            }
    
    async def close(self):
        """Close database connections."""
        await self.engine.dispose()
        self.logger.info("Database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized. Call initialize_database() first.")
    return _db_manager


def initialize_database(database_url: str, pool_size: int = 10, max_overflow: int = 20) -> DatabaseManager:
    """
    Initialize the global database manager.
    
    Args:
        database_url: PostgreSQL connection URL
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections
        
    Returns:
        Database manager instance
    """
    global _db_manager
    _db_manager = DatabaseManager(database_url, pool_size, max_overflow)
    return _db_manager


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_database():
        print("=== Database Integration Test ===")
        
        # Initialize database (you'll need to set up PostgreSQL first)
        db_url = "postgresql+asyncpg://user:password@localhost/dream_caesar"
        db_manager = initialize_database(db_url)
        
        try:
            # Create a test problem
            problem_id = await db_manager.create_problem(
                title="Test Problem",
                description="How can we reduce global carbon emissions?",
                initial_layer="deci"
            )
            print(f"Created problem: {problem_id}")
            
            # Get problem
            problem = await db_manager.get_problem(problem_id)
            print(f"Retrieved problem: {problem['title']}")
            
            # Create layer run
            layer_run_id = await db_manager.create_layer_run(problem_id, "deci", 1)
            print(f"Created layer run: {layer_run_id}")
            
            # Update layer run
            await db_manager.update_layer_run(
                layer_run_id,
                status="completed",
                started_at=datetime.now(timezone.utc),
                finished_at=datetime.now(timezone.utc),
                total_cost_usd=50.0,
                total_latency_ms=30000
            )
            print("Updated layer run")
            
            # Get genealogy
            genealogy = await db_manager.get_problem_genealogy(problem_id)
            print(f"Genealogy: {len(genealogy['layer_runs'])} layer runs")
            
        except Exception as e:
            print(f"Database test failed: {e}")
        finally:
            await db_manager.close()
    
    # Run the test
    asyncio.run(test_database())
