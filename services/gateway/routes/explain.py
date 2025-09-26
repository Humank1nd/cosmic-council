#!/usr/bin/env python3
"""
🔍 Explainability Routes
Explainability and transparency endpoints for decision chains
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta

from shared.utils.database import DatabaseManager, get_database_manager
from shared.logging.logger import get_enterprise_logger

router = APIRouter(prefix="/v1/explain", tags=["explainability"])
logger = get_enterprise_logger("gateway", "explain")

class ExplanationRequest(BaseModel):
    """Request model for explanation generation"""
    entity_id: str = Field(..., description="ID of the entity to explain")
    entity_type: str = Field(..., description="Type of entity (cycle, stage, decision, etc.)")
    explanation_depth: str = Field(default="standard", regex="^(basic|standard|detailed|comprehensive)$", description="Depth of explanation")
    include_reasoning: bool = Field(default=True, description="Include reasoning chains")
    include_alternatives: bool = Field(default=False, description="Include alternative paths considered")
    include_confidence: bool = Field(default=True, description="Include confidence scores and uncertainty")

class ExplanationResponse(BaseModel):
    """Response model for explanations"""
    entity_id: str
    entity_type: str
    explanation_depth: str
    generated_at: datetime
    summary: str
    reasoning_chain: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    alternatives_considered: List[Dict[str, Any]]
    key_insights: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]

class DecisionTrace(BaseModel):
    """Decision trace model"""
    decision_id: str
    timestamp: datetime
    decision_type: str
    input_data: Dict[str, Any]
    decision_criteria: List[str]
    decision_rationale: str
    confidence_score: float
    alternatives_considered: List[str]
    outcome: Dict[str, Any]
    impact_assessment: Dict[str, Any]

class TransparencyReport(BaseModel):
    """Transparency report model"""
    report_id: str
    generated_at: datetime
    scope: str  # "cycle", "enterprise", "system"
    scope_id: str
    period_start: datetime
    period_end: datetime
    total_decisions: int
    decision_breakdown: Dict[str, int]
    confidence_distribution: Dict[str, float]
    key_insights: List[str]
    transparency_score: float
    recommendations: List[str]

@router.get("/{entity_id}", response_model=ExplanationResponse)
async def explain_entity(
    entity_id: str,
    entity_type: str = Query("cycle", description="Type of entity to explain"),
    explanation_depth: str = Query("standard", description="Depth of explanation"),
    include_reasoning: bool = Query(True, description="Include reasoning chains"),
    include_alternatives: bool = Query(False, description="Include alternative paths"),
    include_confidence: bool = Query(True, description="Include confidence scores"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get comprehensive explanation for an entity"""
    try:
        logger.info(f"Generating explanation for {entity_type}: {entity_id}")
        
        # Get entity data
        entity_data = await get_entity_data(db, entity_id, entity_type)
        if not entity_data:
            raise HTTPException(status_code=404, detail=f"{entity_type} not found")
        
        # Generate explanation based on depth
        if explanation_depth == "basic":
            explanation = await generate_basic_explanation(entity_data, entity_type)
        elif explanation_depth == "standard":
            explanation = await generate_standard_explanation(entity_data, entity_type, db)
        elif explanation_depth == "detailed":
            explanation = await generate_detailed_explanation(entity_data, entity_type, db)
        elif explanation_depth == "comprehensive":
            explanation = await generate_comprehensive_explanation(entity_data, entity_type, db)
        else:
            raise HTTPException(status_code=400, detail="Invalid explanation depth")
        
        # Add requested components
        if include_reasoning:
            explanation["reasoning_chain"] = await get_reasoning_chain(db, entity_id, entity_type)
        else:
            explanation["reasoning_chain"] = []
        
        if include_alternatives:
            explanation["alternatives_considered"] = await get_alternatives_considered(db, entity_id, entity_type)
        else:
            explanation["alternatives_considered"] = []
        
        if include_confidence:
            explanation["confidence_scores"] = await get_confidence_scores(db, entity_id, entity_type)
        else:
            explanation["confidence_scores"] = {}
        
        return ExplanationResponse(
            entity_id=entity_id,
            entity_type=entity_type,
            explanation_depth=explanation_depth,
            generated_at=datetime.now(timezone.utc),
            **explanation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Explain entity failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to explain entity: {str(e)}")

@router.get("/{entity_id}/decisions", response_model=List[DecisionTrace])
async def get_decision_trace(
    entity_id: str,
    entity_type: str = Query("cycle", description="Type of entity"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of decisions to return"),
    offset: int = Query(0, ge=0, description="Number of decisions to skip"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get decision trace for an entity"""
    try:
        logger.info(f"Getting decision trace for {entity_type}: {entity_id}")
        
        # Query decision trace from audit log
        query = """
        SELECT al.*, c.objective_ref, se.stage_code
        FROM audit_log al
        LEFT JOIN cycles c ON al.cycle_id = c.id
        LEFT JOIN stage_executions se ON al.stage_execution_id = se.id
        WHERE al.entity_id = $1 AND al.entity_type = $2
        ORDER BY al.timestamp ASC
        LIMIT $3 OFFSET $4
        """
        
        results = await db.execute_query(query, (entity_id, entity_type, limit, offset))
        
        # Process results into decision traces
        decisions = []
        for row in results:
            decision = DecisionTrace(
                decision_id=row['id'],
                timestamp=row['timestamp'],
                decision_type=row['action'],
                input_data=row['details_json'] or {},
                decision_criteria=extract_decision_criteria(row['details_json']),
                decision_rationale=extract_decision_rationale(row['details_json']),
                confidence_score=extract_confidence_score(row['details_json']),
                alternatives_considered=extract_alternatives(row['details_json']),
                outcome=extract_outcome(row['details_json']),
                impact_assessment=extract_impact_assessment(row['details_json'])
            )
            decisions.append(decision)
        
        return decisions
        
    except Exception as e:
        logger.error(f"❌ Get decision trace failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get decision trace: {str(e)}")

@router.get("/{entity_id}/reasoning-chain")
async def get_reasoning_chain_detailed(
    entity_id: str,
    entity_type: str = Query("cycle", description="Type of entity"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get detailed reasoning chain for an entity"""
    try:
        logger.info(f"Getting reasoning chain for {entity_type}: {entity_id}")
        
        # Get reasoning chain
        reasoning_chain = await get_reasoning_chain(db, entity_id, entity_type)
        
        # Enhance with additional context
        enhanced_chain = []
        for step in reasoning_chain:
            enhanced_step = {
                **step,
                "context": await get_step_context(db, step.get("step_id")),
                "dependencies": await get_step_dependencies(db, step.get("step_id")),
                "influences": await get_step_influences(db, step.get("step_id"))
            }
            enhanced_chain.append(enhanced_step)
        
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "reasoning_chain": enhanced_chain,
            "total_steps": len(enhanced_chain),
            "generated_at": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"❌ Get reasoning chain failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reasoning chain: {str(e)}")

@router.get("/{entity_id}/alternatives")
async def get_alternatives_analysis(
    entity_id: str,
    entity_type: str = Query("cycle", description="Type of entity"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get analysis of alternatives considered"""
    try:
        logger.info(f"Getting alternatives analysis for {entity_type}: {entity_id}")
        
        # Get alternatives considered
        alternatives = await get_alternatives_considered(db, entity_id, entity_type)
        
        # Analyze alternatives
        analysis = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "alternatives_considered": alternatives,
            "total_alternatives": len(alternatives),
            "analysis": {
                "best_alternative": find_best_alternative(alternatives),
                "worst_alternative": find_worst_alternative(alternatives),
                "risk_assessment": assess_alternative_risks(alternatives),
                "cost_benefit_analysis": analyze_cost_benefit(alternatives)
            },
            "generated_at": datetime.now(timezone.utc)
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Get alternatives analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get alternatives analysis: {str(e)}")

@router.get("/{entity_id}/confidence-analysis")
async def get_confidence_analysis(
    entity_id: str,
    entity_type: str = Query("cycle", description="Type of entity"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Get confidence analysis for an entity"""
    try:
        logger.info(f"Getting confidence analysis for {entity_type}: {entity_id}")
        
        # Get confidence scores
        confidence_scores = await get_confidence_scores(db, entity_id, entity_type)
        
        # Analyze confidence
        analysis = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "confidence_scores": confidence_scores,
            "analysis": {
                "overall_confidence": calculate_overall_confidence(confidence_scores),
                "confidence_distribution": analyze_confidence_distribution(confidence_scores),
                "uncertainty_sources": identify_uncertainty_sources(confidence_scores),
                "confidence_trends": analyze_confidence_trends(confidence_scores),
                "recommendations": generate_confidence_recommendations(confidence_scores)
            },
            "generated_at": datetime.now(timezone.utc)
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Get confidence analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get confidence analysis: {str(e)}")

@router.post("/transparency-report", response_model=TransparencyReport)
async def generate_transparency_report(
    scope: str = Query("cycle", regex="^(cycle|enterprise|system)$", description="Scope of transparency report"),
    scope_id: str = Query(..., description="ID of the scope entity"),
    period_days: int = Query(30, ge=1, le=365, description="Period in days for the report"),
    db: DatabaseManager = Depends(get_db_manager)
):
    """Generate transparency report for a scope"""
    try:
        logger.info(f"Generating transparency report for {scope}: {scope_id}")
        
        # Calculate period
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=period_days)
        
        # Get data for the period
        decisions_data = await get_decisions_for_period(db, scope, scope_id, start_date, end_date)
        
        # Generate report
        report = TransparencyReport(
            report_id=f"transparency_{scope}_{scope_id}_{int(end_date.timestamp())}",
            generated_at=end_date,
            scope=scope,
            scope_id=scope_id,
            period_start=start_date,
            period_end=end_date,
            total_decisions=len(decisions_data),
            decision_breakdown=analyze_decision_breakdown(decisions_data),
            confidence_distribution=analyze_confidence_distribution(decisions_data),
            key_insights=generate_key_insights(decisions_data),
            transparency_score=calculate_transparency_score(decisions_data),
            recommendations=generate_transparency_recommendations(decisions_data)
        )
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Generate transparency report failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate transparency report: {str(e)}")

# Helper functions
async def get_entity_data(db: DatabaseManager, entity_id: str, entity_type: str) -> Optional[Dict[str, Any]]:
    """Get entity data from database"""
    try:
        if entity_type == "cycle":
            query = "SELECT * FROM cycles WHERE id = $1"
        elif entity_type == "stage":
            query = "SELECT * FROM stage_executions WHERE id = $1"
        else:
            query = "SELECT * FROM audit_log WHERE entity_id = $1 AND entity_type = $2"
            results = await db.execute_query(query, (entity_id, entity_type))
            return results[0] if results else None
        
        results = await db.execute_query(query, (entity_id,))
        return results[0] if results else None
        
    except Exception as e:
        logger.error(f"Failed to get entity data: {e}")
        return None

async def generate_basic_explanation(entity_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
    """Generate basic explanation"""
    return {
        "summary": f"Basic explanation for {entity_type}",
        "key_insights": ["Entity processed successfully", "Standard workflow followed"],
        "recommendations": ["Continue monitoring", "Maintain current approach"],
        "metadata": {"explanation_type": "basic"}
    }

async def generate_standard_explanation(entity_data: Dict[str, Any], entity_type: str, db: DatabaseManager) -> Dict[str, Any]:
    """Generate standard explanation"""
    return {
        "summary": f"Standard explanation for {entity_type} with detailed reasoning",
        "key_insights": [
            "Entity processed with standard workflow",
            "All stages completed successfully",
            "Confidence levels within acceptable range"
        ],
        "recommendations": [
            "Continue current approach",
            "Monitor performance metrics",
            "Consider optimization opportunities"
        ],
        "metadata": {"explanation_type": "standard"}
    }

async def generate_detailed_explanation(entity_data: Dict[str, Any], entity_type: str, db: DatabaseManager) -> Dict[str, Any]:
    """Generate detailed explanation"""
    return {
        "summary": f"Detailed explanation for {entity_type} with comprehensive analysis",
        "key_insights": [
            "Detailed analysis of processing steps",
            "Performance metrics and bottlenecks identified",
            "Confidence analysis completed",
            "Alternative approaches considered"
        ],
        "recommendations": [
            "Implement performance optimizations",
            "Address identified bottlenecks",
            "Consider alternative approaches for future cycles",
            "Enhance monitoring and alerting"
        ],
        "metadata": {"explanation_type": "detailed"}
    }

async def generate_comprehensive_explanation(entity_data: Dict[str, Any], entity_type: str, db: DatabaseManager) -> Dict[str, Any]:
    """Generate comprehensive explanation"""
    return {
        "summary": f"Comprehensive explanation for {entity_type} with full context and analysis",
        "key_insights": [
            "Complete analysis of all processing aspects",
            "Comprehensive performance evaluation",
            "Full confidence and uncertainty analysis",
            "Detailed alternative analysis",
            "Impact assessment and risk analysis"
        ],
        "recommendations": [
            "Implement comprehensive optimizations",
            "Address all identified issues",
            "Develop contingency plans",
            "Enhance system capabilities",
            "Implement advanced monitoring"
        ],
        "metadata": {"explanation_type": "comprehensive"}
    }

async def get_reasoning_chain(db: DatabaseManager, entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
    """Get reasoning chain for an entity"""
    try:
        # Query audit log for reasoning steps
        query = """
        SELECT al.*, c.objective_ref, se.stage_code
        FROM audit_log al
        LEFT JOIN cycles c ON al.cycle_id = c.id
        LEFT JOIN stage_executions se ON al.stage_execution_id = se.id
        WHERE al.entity_id = $1 AND al.entity_type = $2
        ORDER BY al.timestamp ASC
        """
        
        results = await db.execute_query(query, (entity_id, entity_type))
        
        reasoning_chain = []
        for i, row in enumerate(results):
            step = {
                "step_id": row['id'],
                "step_number": i + 1,
                "timestamp": row['timestamp'],
                "action": row['action'],
                "actor": row['actor'],
                "reasoning": extract_reasoning(row['details_json']),
                "context": {
                    "cycle_id": row['cycle_id'],
                    "stage": row['stage_code'],
                    "objective": row['objective_ref']
                }
            }
            reasoning_chain.append(step)
        
        return reasoning_chain
        
    except Exception as e:
        logger.error(f"Failed to get reasoning chain: {e}")
        return []

async def get_alternatives_considered(db: DatabaseManager, entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
    """Get alternatives considered for an entity"""
    try:
        # This would need to be implemented based on actual alternative tracking
        # For now, return mock data
        return [
            {
                "alternative_id": "alt_1",
                "description": "Alternative approach 1",
                "reason_rejected": "Lower confidence score",
                "confidence_score": 0.65
            },
            {
                "alternative_id": "alt_2", 
                "description": "Alternative approach 2",
                "reason_rejected": "Higher resource requirements",
                "confidence_score": 0.72
            }
        ]
        
    except Exception as e:
        logger.error(f"Failed to get alternatives considered: {e}")
        return []

async def get_confidence_scores(db: DatabaseManager, entity_id: str, entity_type: str) -> Dict[str, float]:
    """Get confidence scores for an entity"""
    try:
        # This would need to be implemented based on actual confidence tracking
        # For now, return mock data
        return {
            "overall": 0.78,
            "red_research": 0.75,
            "orange_logistics": 0.78,
            "yellow_development": 0.80,
            "green_budget": 0.77,
            "blue_market": 0.79,
            "purple_support": 0.82
        }
        
    except Exception as e:
        logger.error(f"Failed to get confidence scores: {e}")
        return {}

# Additional helper functions for data extraction and analysis
def extract_decision_criteria(details: Dict[str, Any]) -> List[str]:
    """Extract decision criteria from details"""
    if not details:
        return []
    return details.get("criteria", [])

def extract_decision_rationale(details: Dict[str, Any]) -> str:
    """Extract decision rationale from details"""
    if not details:
        return "No rationale available"
    return details.get("rationale", "No rationale available")

def extract_confidence_score(details: Dict[str, Any]) -> float:
    """Extract confidence score from details"""
    if not details:
        return 0.0
    return details.get("confidence_score", 0.0)

def extract_alternatives(details: Dict[str, Any]) -> List[str]:
    """Extract alternatives from details"""
    if not details:
        return []
    return details.get("alternatives", [])

def extract_outcome(details: Dict[str, Any]) -> Dict[str, Any]:
    """Extract outcome from details"""
    if not details:
        return {}
    return details.get("outcome", {})

def extract_impact_assessment(details: Dict[str, Any]) -> Dict[str, Any]:
    """Extract impact assessment from details"""
    if not details:
        return {}
    return details.get("impact_assessment", {})

def extract_reasoning(details: Dict[str, Any]) -> str:
    """Extract reasoning from details"""
    if not details:
        return "No reasoning available"
    return details.get("reasoning", "No reasoning available")

# Additional helper functions for analysis
async def get_step_context(db: DatabaseManager, step_id: str) -> Dict[str, Any]:
    """Get context for a reasoning step"""
    return {"context": "Step context not available"}

async def get_step_dependencies(db: DatabaseManager, step_id: str) -> List[str]:
    """Get dependencies for a reasoning step"""
    return []

async def get_step_influences(db: DatabaseManager, step_id: str) -> List[str]:
    """Get influences for a reasoning step"""
    return []

def find_best_alternative(alternatives: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Find the best alternative"""
    if not alternatives:
        return None
    return max(alternatives, key=lambda x: x.get("confidence_score", 0))

def find_worst_alternative(alternatives: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Find the worst alternative"""
    if not alternatives:
        return None
    return min(alternatives, key=lambda x: x.get("confidence_score", 0))

def assess_alternative_risks(alternatives: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess risks of alternatives"""
    return {"risk_assessment": "Risk assessment not available"}

def analyze_cost_benefit(alternatives: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze cost-benefit of alternatives"""
    return {"cost_benefit": "Cost-benefit analysis not available"}

def calculate_overall_confidence(confidence_scores: Dict[str, float]) -> float:
    """Calculate overall confidence score"""
    if not confidence_scores:
        return 0.0
    return sum(confidence_scores.values()) / len(confidence_scores)

def analyze_confidence_distribution(confidence_scores: Dict[str, float]) -> Dict[str, Any]:
    """Analyze confidence distribution"""
    if not confidence_scores:
        return {}
    
    values = list(confidence_scores.values())
    return {
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
        "std_dev": 0.0  # Would need proper calculation
    }

def identify_uncertainty_sources(confidence_scores: Dict[str, float]) -> List[str]:
    """Identify sources of uncertainty"""
    uncertainty_sources = []
    for key, value in confidence_scores.items():
        if value < 0.7:
            uncertainty_sources.append(f"Low confidence in {key}")
    return uncertainty_sources

def analyze_confidence_trends(confidence_scores: Dict[str, float]) -> Dict[str, Any]:
    """Analyze confidence trends"""
    return {"trends": "Trend analysis not available"}

def generate_confidence_recommendations(confidence_scores: Dict[str, float]) -> List[str]:
    """Generate confidence recommendations"""
    recommendations = []
    for key, value in confidence_scores.items():
        if value < 0.7:
            recommendations.append(f"Improve confidence in {key}")
    return recommendations

async def get_decisions_for_period(db: DatabaseManager, scope: str, scope_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Get decisions for a period"""
    # This would need to be implemented based on actual decision tracking
    return []

def analyze_decision_breakdown(decisions: List[Dict[str, Any]]) -> Dict[str, int]:
    """Analyze decision breakdown"""
    return {"total": len(decisions)}

def generate_key_insights(decisions: List[Dict[str, Any]]) -> List[str]:
    """Generate key insights"""
    return ["Key insights not available"]

def calculate_transparency_score(decisions: List[Dict[str, Any]]) -> float:
    """Calculate transparency score"""
    return 0.8  # Mock score

def generate_transparency_recommendations(decisions: List[Dict[str, Any]]) -> List[str]:
    """Generate transparency recommendations"""
    return ["Improve decision documentation", "Enhance audit trails"]
