"""
Decision Explainability Engine
Provides human and agent-readable explanations for policy decisions
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from .schemas import DecisionExplanation, ViolationCode, Agent, Resource
from .storage import engine
from sqlalchemy import text

class DecisionExplainer:
    """
    Generates explainable summaries of policy decisions
    """
    
    def __init__(self):
        self.violation_codes = {
            "BRAND_HATE_SPEECH": {
                "description": "Content contains hate speech or discriminatory language",
                "severity": "high",
                "suggested_remediation": "Remove flagged content or escalate to Purple Elephant for review"
            },
            "BRAND_TOXICITY": {
                "description": "Content shows high toxicity levels",
                "severity": "medium", 
                "suggested_remediation": "Revise content to reduce toxicity or add content warnings"
            },
            "BUDGET_EXCEEDED": {
                "description": "Request exceeds allocated budget cap",
                "severity": "medium",
                "suggested_remediation": "Reduce resource requirements or request budget increase from Green Turtle"
            },
            "HIGH_RISK": {
                "description": "Request poses high risk based on context analysis",
                "severity": "high",
                "suggested_remediation": "Mitigate risks or escalate to Purple Elephant for ethical review"
            },
            "UNAUTHORIZED_ACCESS": {
                "description": "Agent lacks required permissions for resource",
                "severity": "high",
                "suggested_remediation": "Request access from appropriate enterprise or use different agent"
            }
        }
    
    async def explain_decision(self, decision_id: str) -> Optional[DecisionExplanation]:
        """
        Generate explanation for a specific decision
        """
        try:
            # Fetch decision from database
            decision_data = await self._fetch_decision(decision_id)
            if not decision_data:
                return None
            
            # Parse decision data
            agent_data = decision_data.get('agent', {})
            resource_data = decision_data.get('resource', {})
            
            agent = Agent(
                id=agent_data.get('id', ''),
                enterprise=agent_data.get('enterprise', ''),
                squad=agent_data.get('squad', '')
            )
            
            resource = Resource(
                service=resource_data.get('service', ''),
                action=resource_data.get('action', '')
            )
            
            # Generate violations
            violations = self._generate_violations(decision_data)
            
            # Generate explanation text
            explanation_text = self._generate_explanation_text(
                agent, resource, decision_data, violations
            )
            
            return DecisionExplanation(
                decision_id=decision_id,
                agent=agent,
                resource=resource,
                allow=decision_data.get('allow', False),
                policies_applied=decision_data.get('policy_refs', []),
                violations=violations,
                obligations=decision_data.get('obligations', []),
                explanation_text=explanation_text,
                timestamp=decision_data.get('time', datetime.utcnow()),
                latency_ms=decision_data.get('latency_ms', 0)
            )
            
        except Exception as e:
            print(f"Failed to explain decision {decision_id}: {e}")
            return None
    
    async def _fetch_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Fetch decision data from database"""
        try:
            e = engine()
            with e.begin() as conn:
                result = conn.execute(text("""
                    SELECT decision_id, time, agent_id, request, allow, policy_refs, explanation, latency_ms
                    FROM decisions 
                    WHERE decision_id = :decision_id
                """), {"decision_id": decision_id})
                
                row = result.fetchone()
                if row:
                    return {
                        'decision_id': row[0],
                        'time': row[1],
                        'agent_id': row[2],
                        'request': row[3],
                        'allow': row[4],
                        'policy_refs': row[5] or [],
                        'explanation': row[6] or {},
                        'latency_ms': row[7] or 0,
                        'agent': row[3].get('agent', {}) if row[3] else {},
                        'resource': row[3].get('resource', {}) if row[3] else {},
                        'obligations': row[6].get('obligations', []) if row[6] else []
                    }
                return None
        except Exception as e:
            print(f"Database error fetching decision: {e}")
            return None
    
    def _generate_violations(self, decision_data: Dict[str, Any]) -> List[ViolationCode]:
        """Generate violation codes based on decision context"""
        violations = []
        request = decision_data.get('request', {})
        context = request.get('context', {})
        
        # Check for brand safety violations
        brand_safety = context.get('brand_safety', {})
        if brand_safety.get('flags'):
            for flag in brand_safety['flags']:
                if flag == 'hate_speech':
                    violations.append(ViolationCode(
                        code="BRAND_HATE_SPEECH",
                        description=self.violation_codes["BRAND_HATE_SPEECH"]["description"],
                        severity=self.violation_codes["BRAND_HATE_SPEECH"]["severity"],
                        suggested_remediation=self.violation_codes["BRAND_HATE_SPEECH"]["suggested_remediation"]
                    ))
                elif flag == 'toxicity':
                    violations.append(ViolationCode(
                        code="BRAND_TOXICITY",
                        description=self.violation_codes["BRAND_TOXICITY"]["description"],
                        severity=self.violation_codes["BRAND_TOXICITY"]["severity"],
                        suggested_remediation=self.violation_codes["BRAND_TOXICITY"]["suggested_remediation"]
                    ))
        
        # Check for budget violations
        if context.get('estimated_cost', 0) > context.get('budget_cap', float('inf')):
            violations.append(ViolationCode(
                code="BUDGET_EXCEEDED",
                description=self.violation_codes["BUDGET_EXCEEDED"]["description"],
                severity=self.violation_codes["BUDGET_EXCEEDED"]["severity"],
                suggested_remediation=self.violation_codes["BUDGET_EXCEEDED"]["suggested_remediation"]
            ))
        
        # Check for high risk
        if context.get('risk', 0) >= 0.7:
            violations.append(ViolationCode(
                code="HIGH_RISK",
                description=self.violation_codes["HIGH_RISK"]["description"],
                severity=self.violation_codes["HIGH_RISK"]["severity"],
                suggested_remediation=self.violation_codes["HIGH_RISK"]["suggested_remediation"]
            ))
        
        # Check for unauthorized access
        if not decision_data.get('allow', False) and not violations:
            violations.append(ViolationCode(
                code="UNAUTHORIZED_ACCESS",
                description=self.violation_codes["UNAUTHORIZED_ACCESS"]["description"],
                severity=self.violation_codes["UNAUTHORIZED_ACCESS"]["severity"],
                suggested_remediation=self.violation_codes["UNAUTHORIZED_ACCESS"]["suggested_remediation"]
            ))
        
        return violations
    
    def _generate_explanation_text(self, agent: Agent, resource: Resource, 
                                 decision_data: Dict[str, Any], 
                                 violations: List[ViolationCode]) -> str:
        """Generate human-readable explanation text"""
        allow = decision_data.get('allow', False)
        enterprise_names = {
            'red': 'Red Owl (Research & Inquiry)',
            'orange': 'Orange Orangutan (Logistics & Strategy)', 
            'yellow': 'Yellow Honeybee (Development & Prototyping)',
            'green': 'Green Turtle (Budget & Resources)',
            'blue': 'Blue Dolphin (Communication & Marketing)',
            'purple': 'Purple Elephant (Support & Feedback)'
        }
        
        enterprise_name = enterprise_names.get(agent.enterprise, agent.enterprise)
        
        if allow:
            explanation = f"✅ APPROVED: {enterprise_name} agent '{agent.squad}' is authorized to {resource.action} the {resource.service} resource."
            
            obligations = decision_data.get('obligations', [])
            if obligations:
                explanation += f" Required obligations: {', '.join(obligations)}."
        else:
            explanation = f"❌ DENIED: {enterprise_name} agent '{agent.squad}' is not authorized to {resource.action} the {resource.service} resource."
            
            if violations:
                violation_descriptions = [v.description for v in violations]
                explanation += f" Violations detected: {'; '.join(violation_descriptions)}."
        
        # Add context information
        context = decision_data.get('request', {}).get('context', {})
        if context.get('risk'):
            explanation += f" Risk level: {context['risk']:.2f}."
        if context.get('estimated_cost'):
            explanation += f" Estimated cost: ${context['estimated_cost']:.2f}."
        
        return explanation

# Global instance
explainer = DecisionExplainer()
