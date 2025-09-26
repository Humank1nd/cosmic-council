#!/usr/bin/env python3
"""
🔍 Policy Evaluation Routes
OPA/Rego policy evaluation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from shared.utils.database import DatabaseManager, get_database_manager
from shared.logging.logger import get_enterprise_logger

router = APIRouter(prefix="/v1/policies", tags=["policies"])
logger = get_enterprise_logger("gateway", "evaluate")

class PolicyRule(BaseModel):
    """Policy rule definition"""
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    conditions: List[str] = Field(..., description="Rule conditions")
    action: str = Field(..., description="Action to take if conditions are met")
    priority: int = Field(default=0, description="Rule priority")

class PolicyEvaluationRequest(BaseModel):
    """Request model for policy evaluation"""
    action: str = Field(..., description="Action to evaluate")
    resource: str = Field(..., description="Resource being accessed")
    subject: str = Field(..., description="Subject performing the action")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

class PolicyEvaluationResponse(BaseModel):
    """Response model for policy evaluation"""
    allowed: bool
    reason: str
    conditions: List[str] = Field(default_factory=list)
    rules_applied: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PolicySimulationRequest(BaseModel):
    """Request model for policy simulation"""
    scenarios: List[PolicyEvaluationRequest] = Field(..., description="Scenarios to simulate")
    include_reasons: bool = Field(default=True, description="Include detailed reasons")

class PolicySimulationResponse(BaseModel):
    """Response model for policy simulation"""
    results: List[PolicyEvaluationResponse]
    summary: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@router.post("/evaluate", response_model=PolicyEvaluationResponse)
async def evaluate_policy(
    request: PolicyEvaluationRequest,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Evaluate a single policy request"""
    try:
        logger.info(f"Evaluating policy for action: {request.action}, resource: {request.resource}")
        
        # Get applicable rules from database
        rules = await get_applicable_rules(db, request.action, request.resource)
        
        # Evaluate rules
        result = await evaluate_rules(rules, request)
        
        # Log evaluation
        await log_policy_evaluation(db, request, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Policy evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Policy evaluation failed: {str(e)}")

@router.post("/simulate", response_model=PolicySimulationResponse)
async def simulate_policies(
    request: PolicySimulationRequest,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Simulate multiple policy scenarios"""
    try:
        logger.info(f"Simulating {len(request.scenarios)} policy scenarios")
        
        results = []
        allowed_count = 0
        denied_count = 0
        
        for scenario in request.scenarios:
            # Get applicable rules
            rules = await get_applicable_rules(db, scenario.action, scenario.resource)
            
            # Evaluate rules
            result = await evaluate_rules(rules, scenario)
            results.append(result)
            
            if result.allowed:
                allowed_count += 1
            else:
                denied_count += 1
        
        summary = {
            "total_scenarios": len(request.scenarios),
            "allowed": allowed_count,
            "denied": denied_count,
            "allow_rate": allowed_count / len(request.scenarios) if request.scenarios else 0
        }
        
        return PolicySimulationResponse(
            results=results,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Policy simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Policy simulation failed: {str(e)}")

@router.get("/rules")
async def get_policy_rules(
    action: str = None,
    resource: str = None,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Get policy rules with optional filtering"""
    try:
        query = "SELECT * FROM policy_rules WHERE 1=1"
        params = []
        
        if action:
            query += " AND action = $" + str(len(params) + 1)
            params.append(action)
        
        if resource:
            query += " AND resource_pattern LIKE $" + str(len(params) + 1)
            params.append(f"%{resource}%")
        
        query += " ORDER BY priority DESC, name ASC"
        
        results = await db.execute_query(query, tuple(params))
        
        rules = []
        for row in results:
            rules.append({
                "id": row['id'],
                "name": row['name'],
                "description": row['description'],
                "action": row['action'],
                "resource_pattern": row['resource_pattern'],
                "conditions": row['conditions'],
                "priority": row['priority'],
                "is_active": row['is_active'],
                "created_at": row['created_at']
            })
        
        return {"rules": rules, "count": len(rules)}
        
    except Exception as e:
        logger.error(f"Get policy rules failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get policy rules: {str(e)}")

@router.post("/rules")
async def create_policy_rule(
    rule: PolicyRule,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Create a new policy rule"""
    try:
        logger.info(f"Creating policy rule: {rule.name}")
        
        query = """
        INSERT INTO policy_rules (name, description, action, resource_pattern, conditions, priority, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
        """
        
        # For now, use a generic resource pattern
        resource_pattern = "*"
        
        result = await db.execute_query(
            query, 
            (rule.name, rule.description, rule.action, resource_pattern, rule.conditions, rule.priority, True)
        )
        
        rule_id = result[0]['id']
        
        # Log rule creation
        await log_rule_creation(db, rule_id, rule)
        
        return {"rule_id": rule_id, "message": "Policy rule created successfully"}
        
    except Exception as e:
        logger.error(f"Create policy rule failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create policy rule: {str(e)}")

async def get_applicable_rules(db: DatabaseManager, action: str, resource: str) -> List[Dict[str, Any]]:
    """Get applicable policy rules for the given action and resource"""
    try:
        query = """
        SELECT * FROM policy_rules 
        WHERE is_active = true 
        AND (action = $1 OR action = '*')
        AND (resource_pattern = '*' OR $2 LIKE resource_pattern)
        ORDER BY priority DESC
        """
        
        results = await db.execute_query(query, (action, resource))
        return results
        
    except Exception as e:
        logger.error(f"Failed to get applicable rules: {e}")
        return []

async def evaluate_rules(rules: List[Dict[str, Any]], request: PolicyEvaluationRequest) -> PolicyEvaluationResponse:
    """Evaluate rules against the request"""
    try:
        conditions = []
        rules_applied = []
        
        # Default to allow if no rules found
        allowed = True
        reason = "No applicable rules found"
        
        for rule in rules:
            rules_applied.append(rule['name'])
            
            # Check if rule conditions are met
            rule_allowed = await check_rule_conditions(rule, request)
            
            if not rule_allowed:
                allowed = False
                reason = f"Rule '{rule['name']}' denied the request"
                conditions.append(f"rule_{rule['name']}_denied")
                break
            else:
                conditions.append(f"rule_{rule['name']}_passed")
        
        if allowed and rules_applied:
            reason = f"All applicable rules passed: {', '.join(rules_applied)}"
        
        return PolicyEvaluationResponse(
            allowed=allowed,
            reason=reason,
            conditions=conditions,
            rules_applied=rules_applied
        )
        
    except Exception as e:
        logger.error(f"Rule evaluation failed: {e}")
        return PolicyEvaluationResponse(
            allowed=False,
            reason=f"Rule evaluation error: {str(e)}",
            conditions=["evaluation_error"]
        )

async def check_rule_conditions(rule: Dict[str, Any], request: PolicyEvaluationRequest) -> bool:
    """Check if rule conditions are met"""
    try:
        # Basic condition checking
        # In production, this would be more sophisticated
        
        conditions = rule.get('conditions', [])
        
        for condition in conditions:
            if condition == "user_authenticated":
                # Check if user is authenticated (simplified)
                if not request.subject or request.subject == "anonymous":
                    return False
            
            elif condition == "resource_owner":
                # Check if user owns the resource (simplified)
                if request.resource.startswith("cycles/") and request.subject != "admin":
                    return False
            
            elif condition == "admin_only":
                # Check if user is admin
                if request.subject != "admin":
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Condition checking failed: {e}")
        return False

async def log_policy_evaluation(
    db: DatabaseManager, 
    request: PolicyEvaluationRequest, 
    result: PolicyEvaluationResponse
):
    """Log policy evaluation in audit log"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json)
        VALUES ('policy', $1, 'evaluate', 'gateway', $2)
        """
        
        details = {
            "action": request.action,
            "resource": request.resource,
            "subject": request.subject,
            "context": request.context,
            "result": {
                "allowed": result.allowed,
                "reason": result.reason,
                "conditions": result.conditions,
                "rules_applied": result.rules_applied
            }
        }
        
        await db.execute_command(query, (request.resource, details))
        
    except Exception as e:
        logger.error(f"Failed to log policy evaluation: {e}")

async def log_rule_creation(db: DatabaseManager, rule_id: str, rule: PolicyRule):
    """Log policy rule creation"""
    try:
        query = """
        INSERT INTO audit_log (entity_type, entity_id, action, actor, details_json)
        VALUES ('policy_rule', $1, 'create', 'gateway', $2)
        """
        
        details = {
            "name": rule.name,
            "description": rule.description,
            "action": rule.action,
            "conditions": rule.conditions,
            "priority": rule.priority
        }
        
        await db.execute_command(query, (rule_id, details))
        
    except Exception as e:
        logger.error(f"Failed to log rule creation: {e}")
