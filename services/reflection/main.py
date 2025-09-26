#!/usr/bin/env python3
"""
🟣 Purple Reflection Service
Purple's feedback & policy evolution service for continuous improvement
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import shared utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.utils.database import get_database_manager, DatabaseManager
from shared.logging.logger import setup_logging, get_enterprise_logger

# Configure logging
logger = setup_logging(enterprise="reflection")
reflection_logger = get_enterprise_logger("reflection", "main")

# Pydantic models
class FeedbackItem(BaseModel):
    """Feedback item model"""
    id: Optional[str] = None
    cycle_id: str
    stage: str
    feedback_type: str  # "positive", "negative", "suggestion", "bug"
    content: str
    sentiment: str  # "positive", "neutral", "negative"
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    source: str  # "user", "system", "enterprise"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

class ImprovementRecommendation(BaseModel):
    """Improvement recommendation model"""
    id: Optional[str] = None
    feedback_id: str
    category: str  # "process", "technology", "policy", "training"
    priority: int = Field(ge=1, le=10)
    title: str
    description: str
    expected_impact: str  # "low", "medium", "high", "critical"
    implementation_effort: str  # "low", "medium", "high"
    status: str = Field(default="pending")  # "pending", "in_progress", "completed", "rejected"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

class PolicyEvolutionRequest(BaseModel):
    """Policy evolution request model"""
    current_policy: str
    feedback_summary: str
    suggested_changes: List[str]
    rationale: str
    impact_assessment: str
    proposed_by: str

class ReflectionSession(BaseModel):
    """Reflection session model"""
    id: Optional[str] = None
    cycle_id: str
    session_type: str  # "cycle_completion", "periodic", "incident_response"
    insights: List[str]
    lessons_learned: List[str]
    action_items: List[str]
    next_cycle_recommendations: List[str]
    facilitator: str
    participants: List[str]
    duration_minutes: int
    created_at: Optional[datetime] = None

class ContinuousImprovementMetrics(BaseModel):
    """Continuous improvement metrics model"""
    period: str
    total_feedback_items: int
    positive_feedback_rate: float
    improvement_recommendations: int
    implemented_improvements: int
    policy_evolutions: int
    reflection_sessions: int
    overall_improvement_score: float
    trend: str  # "improving", "stable", "declining"

# Global variables
db_manager: Optional[DatabaseManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db_manager
    
    # Startup
    reflection_logger.info("🟣 Starting Purple Reflection Service")
    
    try:
        # Initialize database manager
        db_manager = await get_database_manager()
        reflection_logger.info("✅ Database manager initialized")
        
        reflection_logger.info("🟣 Reflection service startup complete")
        
    except Exception as e:
        reflection_logger.error(f"❌ Reflection startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    reflection_logger.info("🟣 Shutting down Reflection service")
    if db_manager:
        await db_manager.close_pool()
    reflection_logger.info("🟣 Reflection service shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Cosmic Council Reflection Service",
    description="Purple's feedback & policy evolution service for continuous improvement",
    version="1.0.0",
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

# Dependency injection
async def get_db_manager() -> DatabaseManager:
    """Get database manager instance"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "service": "reflection"
    }

@app.post("/v1/feedback", response_model=FeedbackItem)
async def submit_feedback(
    feedback: FeedbackItem,
    background_tasks: BackgroundTasks,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Submit feedback for a cycle or stage"""
    try:
        reflection_logger.info(f"Submitting feedback for cycle {feedback.cycle_id}")
        
        # Create feedback item
        query = """
        INSERT INTO feedback_collection (
            strategy_id, feedback_text, sentiment, sentiment_score, 
            source, source_type, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, created_at
        """
        
        # For now, use cycle_id as strategy_id (would need proper mapping in production)
        result = await db.execute_query(
            query,
            (
                feedback.cycle_id,
                feedback.content,
                feedback.sentiment,
                feedback.sentiment_score,
                feedback.source,
                feedback.feedback_type,
                datetime.now(timezone.utc)
            )
        )
        
        feedback_id = result[0]['id']
        created_at = result[0]['created_at']
        
        # Process feedback in background
        background_tasks.add_task(process_feedback, db, feedback_id, feedback)
        
        # Log feedback submission
        background_tasks.add_task(log_feedback_submission, db, feedback_id, feedback)
        
        return FeedbackItem(
            id=feedback_id,
            cycle_id=feedback.cycle_id,
            stage=feedback.stage,
            feedback_type=feedback.feedback_type,
            content=feedback.content,
            sentiment=feedback.sentiment,
            sentiment_score=feedback.sentiment_score,
            source=feedback.source,
            metadata=feedback.metadata,
            created_at=created_at
        )
        
    except Exception as e:
        reflection_logger.error(f"❌ Submit feedback failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@app.get("/v1/feedback", response_model=List[FeedbackItem])
async def get_feedback(
    cycle_id: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get feedback with filtering"""
    try:
        reflection_logger.info(f"Getting feedback: cycle_id={cycle_id}, stage={stage}")
        
        # Build query
        query = """
        SELECT id, strategy_id as cycle_id, feedback_text as content, 
               sentiment, sentiment_score, source, source_type as feedback_type,
               created_at
        FROM feedback_collection
        WHERE 1=1
        """
        
        params = []
        param_count = 0
        
        if cycle_id:
            param_count += 1
            query += f" AND strategy_id = ${param_count}"
            params.append(cycle_id)
        
        if sentiment:
            param_count += 1
            query += f" AND sentiment = ${param_count}"
            params.append(sentiment)
        
        query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])
        
        # Execute query
        results = await db.execute_query(query, tuple(params))
        
        # Process results
        feedback_items = []
        for row in results:
            feedback_items.append(FeedbackItem(
                id=row['id'],
                cycle_id=row['cycle_id'],
                stage=stage or "unknown",  # Would need proper mapping
                feedback_type=row['feedback_type'],
                content=row['content'],
                sentiment=row['sentiment'],
                sentiment_score=row['sentiment_score'],
                source=row['source'],
                metadata={},
                created_at=row['created_at']
            ))
        
        return feedback_items
        
    except Exception as e:
        reflection_logger.error(f"❌ Get feedback failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@app.post("/v1/improvements", response_model=ImprovementRecommendation)
async def create_improvement_recommendation(
    recommendation: ImprovementRecommendation,
    background_tasks: BackgroundTasks,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Create an improvement recommendation"""
    try:
        reflection_logger.info(f"Creating improvement recommendation: {recommendation.title}")
        
        # Create improvement recommendation
        query = """
        INSERT INTO improvement_recommendations (
            assessment_id, recommendation_text, priority, status,
            created_at
        ) VALUES ($1, $2, $3, $4, $5)
        RETURNING id, created_at
        """
        
        # For now, use feedback_id as assessment_id (would need proper mapping)
        result = await db.execute_query(
            query,
            (
                recommendation.feedback_id,
                recommendation.description,
                recommendation.priority,
                recommendation.status,
                datetime.now(timezone.utc)
            )
        )
        
        recommendation_id = result[0]['id']
        created_at = result[0]['created_at']
        
        # Log recommendation creation
        background_tasks.add_task(log_recommendation_creation, db, recommendation_id, recommendation)
        
        return ImprovementRecommendation(
            id=recommendation_id,
            feedback_id=recommendation.feedback_id,
            category=recommendation.category,
            priority=recommendation.priority,
            title=recommendation.title,
            description=recommendation.description,
            expected_impact=recommendation.expected_impact,
            implementation_effort=recommendation.implementation_effort,
            status=recommendation.status,
            assigned_to=recommendation.assigned_to,
            due_date=recommendation.due_date,
            created_at=created_at
        )
        
    except Exception as e:
        reflection_logger.error(f"❌ Create improvement recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create improvement recommendation: {str(e)}")

@app.get("/v1/improvements", response_model=List[ImprovementRecommendation])
async def get_improvement_recommendations(
    status: Optional[str] = Query(None),
    priority_min: Optional[int] = Query(None, ge=1, le=10),
    category: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get improvement recommendations with filtering"""
    try:
        reflection_logger.info(f"Getting improvement recommendations: status={status}")
        
        # Build query
        query = """
        SELECT id, assessment_id as feedback_id, recommendation_text as description,
               priority, status, created_at
        FROM improvement_recommendations
        WHERE 1=1
        """
        
        params = []
        param_count = 0
        
        if status:
            param_count += 1
            query += f" AND status = ${param_count}"
            params.append(status)
        
        if priority_min:
            param_count += 1
            query += f" AND priority >= ${param_count}"
            params.append(priority_min)
        
        query += f" ORDER BY priority DESC, created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])
        
        # Execute query
        results = await db.execute_query(query, tuple(params))
        
        # Process results
        recommendations = []
        for row in results:
            recommendations.append(ImprovementRecommendation(
                id=row['id'],
                feedback_id=row['feedback_id'],
                category=category or "general",  # Would need proper mapping
                priority=row['priority'],
                title=f"Improvement {row['id']}",  # Would need proper title
                description=row['description'],
                expected_impact="medium",  # Would need proper mapping
                implementation_effort="medium",  # Would need proper mapping
                status=row['status'],
                created_at=row['created_at']
            ))
        
        return recommendations
        
    except Exception as e:
        reflection_logger.error(f"❌ Get improvement recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get improvement recommendations: {str(e)}")

@app.post("/v1/reflection-sessions", response_model=ReflectionSession)
async def create_reflection_session(
    session: ReflectionSession,
    background_tasks: BackgroundTasks,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Create a reflection session"""
    try:
        reflection_logger.info(f"Creating reflection session for cycle {session.cycle_id}")
        
        # Create reflection session (would need proper table in production)
        # For now, log it in audit log
        background_tasks.add_task(log_reflection_session, db, session)
        
        return ReflectionSession(
            id="session_" + str(int(datetime.now().timestamp())),
            cycle_id=session.cycle_id,
            session_type=session.session_type,
            insights=session.insights,
            lessons_learned=session.lessons_learned,
            action_items=session.action_items,
            next_cycle_recommendations=session.next_cycle_recommendations,
            facilitator=session.facilitator,
            participants=session.participants,
            duration_minutes=session.duration_minutes,
            created_at=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        reflection_logger.error(f"❌ Create reflection session failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create reflection session: {str(e)}")

@app.get("/v1/continuous-improvement/metrics", response_model=ContinuousImprovementMetrics)
async def get_continuous_improvement_metrics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get continuous improvement metrics"""
    try:
        reflection_logger.info(f"Getting continuous improvement metrics for period: {period}")
        
        # Calculate time period
        end_date = datetime.now(timezone.utc)
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        else:  # 1y
            start_date = end_date - timedelta(days=365)
        
        # Get feedback metrics
        feedback_query = """
        SELECT 
            COUNT(*) as total_feedback,
            AVG(CASE WHEN sentiment = 'positive' THEN 1.0 ELSE 0.0 END) as positive_rate
        FROM feedback_collection
        WHERE created_at >= $1 AND created_at <= $2
        """
        
        feedback_result = await db.execute_query(feedback_query, (start_date, end_date))
        total_feedback = feedback_result[0]['total_feedback'] or 0
        positive_feedback_rate = float(feedback_result[0]['positive_rate'] or 0)
        
        # Get improvement recommendations
        improvements_query = """
        SELECT COUNT(*) as total_improvements
        FROM improvement_recommendations
        WHERE created_at >= $1 AND created_at <= $2
        """
        
        improvements_result = await db.execute_query(improvements_query, (start_date, end_date))
        improvement_recommendations = improvements_result[0]['total_improvements'] or 0
        
        # Calculate overall improvement score
        overall_improvement_score = (positive_feedback_rate * 0.4 + 
                                   (improvement_recommendations / max(total_feedback, 1)) * 0.6)
        
        # Determine trend (simplified)
        trend = "improving" if overall_improvement_score > 0.7 else "stable" if overall_improvement_score > 0.5 else "declining"
        
        return ContinuousImprovementMetrics(
            period=period,
            total_feedback_items=total_feedback,
            positive_feedback_rate=positive_feedback_rate,
            improvement_recommendations=improvement_recommendations,
            implemented_improvements=0,  # Would need proper tracking
            policy_evolutions=0,  # Would need proper tracking
            reflection_sessions=0,  # Would need proper tracking
            overall_improvement_score=overall_improvement_score,
            trend=trend
        )
        
    except Exception as e:
        reflection_logger.error(f"❌ Get continuous improvement metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get continuous improvement metrics: {str(e)}")

# Background tasks
async def process_feedback(db: DatabaseManager, feedback_id: str, feedback: FeedbackItem):
    """Process feedback and generate insights"""
    try:
        reflection_logger.info(f"Processing feedback {feedback_id}")
        
        # Analyze sentiment and generate insights
        if feedback.sentiment_score < -0.5:
            # Negative feedback - might need immediate attention
            reflection_logger.warning(f"Negative feedback detected: {feedback.content}")
        
        # Generate improvement recommendations if needed
        if feedback.sentiment_score < 0 or feedback.feedback_type == "suggestion":
            # Create improvement recommendation
            recommendation_query = """
            INSERT INTO improvement_recommendations (
                assessment_id, recommendation_text, priority, status, created_at
            ) VALUES ($1, $2, $3, $4, $5)
            """
            
            await db.execute_command(
                recommendation_query,
                (
                    feedback_id,
                    f"Address feedback: {feedback.content[:100]}...",
                    5,  # Medium priority
                    "pending",
                    datetime.now(timezone.utc)
                )
            )
        
    except Exception as e:
        reflection_logger.error(f"Failed to process feedback {feedback_id}: {e}")

async def log_feedback_submission(db: DatabaseManager, feedback_id: str, feedback: FeedbackItem):
    """Log feedback submission in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json)
        VALUES ('feedback', $1, 'create', 'reflection_service', $2)
        """
        
        details = {
            "cycle_id": feedback.cycle_id,
            "stage": feedback.stage,
            "feedback_type": feedback.feedback_type,
            "sentiment": feedback.sentiment,
            "sentiment_score": feedback.sentiment_score,
            "source": feedback.source
        }
        
        await db.execute_command(query, (feedback_id, details))
        
    except Exception as e:
        reflection_logger.error(f"Failed to log feedback submission: {e}")

async def log_recommendation_creation(db: DatabaseManager, recommendation_id: str, recommendation: ImprovementRecommendation):
    """Log recommendation creation in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json)
        VALUES ('improvement_recommendation', $1, 'create', 'reflection_service', $2)
        """
        
        details = {
            "feedback_id": recommendation.feedback_id,
            "category": recommendation.category,
            "priority": recommendation.priority,
            "title": recommendation.title,
            "expected_impact": recommendation.expected_impact,
            "implementation_effort": recommendation.implementation_effort
        }
        
        await db.execute_command(query, (recommendation_id, details))
        
    except Exception as e:
        reflection_logger.error(f"Failed to log recommendation creation: {e}")

async def log_reflection_session(db: DatabaseManager, session: ReflectionSession):
    """Log reflection session in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json)
        VALUES ('reflection_session', $1, 'create', 'reflection_service', $2)
        """
        
        details = {
            "cycle_id": session.cycle_id,
            "session_type": session.session_type,
            "insights_count": len(session.insights),
            "lessons_learned_count": len(session.lessons_learned),
            "action_items_count": len(session.action_items),
            "facilitator": session.facilitator,
            "participants_count": len(session.participants),
            "duration_minutes": session.duration_minutes
        }
        
        session_id = f"session_{session.cycle_id}_{int(datetime.now().timestamp())}"
        await db.execute_command(query, (session_id, details))
        
    except Exception as e:
        reflection_logger.error(f"Failed to log reflection session: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
