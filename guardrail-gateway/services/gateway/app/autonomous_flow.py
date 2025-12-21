"""
Autonomous Decision Flow Engine
Implements the clockwise processing cycle for the Cosmic Council
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from .schemas import EvalInput, EvalDecision
from .policy_engine import engine as policy_engine
from .storage import log_decision
from sqlalchemy import create_engine, text
from .settings import settings

class AutonomousFlowEngine:
    """
    Orchestrates the clockwise processing cycle:
    Red → Orange → Yellow → Green → Blue → Purple → Feedback Loop
    """
    
    def __init__(self):
        self.enterprises = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        self.enterprise_roles = {
            'red': 'knowledge_gathering',
            'orange': 'logistics_planning', 
            'yellow': 'prototype_development',
            'green': 'resource_allocation',
            'blue': 'communication',
            'purple': 'empathy_analysis'
        }
    
    async def process_autonomous_cycle(self, problem_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete autonomous decision cycle
        """
        cycle_id = str(uuid.uuid4())
        results = {
            'cycle_id': cycle_id,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'enterprises': {},
            'final_decision': None,
            'feedback_loop': None
        }
        
        # Phase 1: Clockwise Processing
        for enterprise in self.enterprises:
            enterprise_result = await self._process_enterprise(
                enterprise, problem_input, cycle_id
            )
            results['enterprises'][enterprise] = enterprise_result
            
            # Add delay to simulate processing time
            await asyncio.sleep(0.1)
        
        # Phase 2: Purple Feedback Loop
        feedback_result = await self._execute_feedback_loop(
            results['enterprises'], cycle_id
        )
        results['feedback_loop'] = feedback_result
        
        # Phase 3: Final Decision Synthesis
        final_decision = await self._synthesize_final_decision(
            results['enterprises'], feedback_result
        )
        results['final_decision'] = final_decision
        results['end_time'] = datetime.now(timezone.utc).isoformat()
        
        return results
    
    async def _process_enterprise(self, enterprise: str, problem_input: Dict[str, Any], cycle_id: str) -> Dict[str, Any]:
        """
        Process a single enterprise in the cycle
        """
        role = self.enterprise_roles[enterprise]
        
        # Create evaluation input for this enterprise
        eval_input = EvalInput(
            agent={
                'id': f"{enterprise}_agent_{uuid.uuid4()}",
                'enterprise': enterprise,
                'squad': role
            },
            resource={
                'service': f"{enterprise}_processing",
                'action': 'analyze'
            },
            context={
                'problem_input': problem_input,
                'cycle_id': cycle_id,
                'enterprise_role': role
            }
        )
        
        # Evaluate through Guardrail Gateway
        allow, meta = await policy_engine.evaluate(f"guard/{enterprise}", eval_input.model_dump())
        
        # Log decision
        try:
            log_decision({
                'agent': eval_input.agent.model_dump(),
                'request_json': eval_input.model_dump(),
                'allow': allow,
                'policy_refs': [f"guard/{enterprise}"],
                'explanation': meta,
                'latency_ms': meta.get('latency_ms', 0)
            })
        except Exception as e:
            print(f"Failed to log decision: {e}")
        
        # Enterprise-specific processing
        enterprise_result = await self._enterprise_specific_processing(
            enterprise, problem_input, allow, meta
        )
        
        return {
            'enterprise': enterprise,
            'role': role,
            'policy_decision': allow,
            'obligations': meta.get('obligations', []),
            'processing_result': enterprise_result,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def _enterprise_specific_processing(self, enterprise: str, problem_input: Dict[str, Any], 
                                            policy_allow: bool, meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enterprise-specific processing logic
        """
        if not policy_allow:
            return {'status': 'blocked', 'reason': 'Policy violation'}
        
        processing_results = {
            'red': self._red_owl_processing,
            'orange': self._orange_orangutan_processing,
            'yellow': self._yellow_honeybee_processing,
            'green': self._green_turtle_processing,
            'blue': self._blue_dolphin_processing,
            'purple': self._purple_elephant_processing
        }
        
        processor = processing_results.get(enterprise)
        if processor:
            return await processor(problem_input, meta)
        
        return {'status': 'unknown_enterprise'}
    
    async def _red_owl_processing(self, problem_input: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Red Owl: Knowledge gathering and research"""
        return {
            'status': 'completed',
            'knowledge_gathered': {
                'sources': ['internal_db', 'external_apis', 'vector_search'],
                'confidence': 0.85,
                'key_insights': ['Problem requires multi-domain expertise', 'High complexity detected']
            },
            'research_quality': 'high'
        }
    
    async def _orange_orangutan_processing(self, problem_input: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Orange Orangutan: Logistics and planning"""
        return {
            'status': 'completed',
            'logistics_plan': {
                'timeline': '2-4 weeks',
                'resources_needed': ['compute', 'storage', 'api_access'],
                'dependencies': ['red_knowledge', 'yellow_prototypes']
            },
            'planning_confidence': 0.90
        }
    
    async def _yellow_honeybee_processing(self, problem_input: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Yellow Honeybee: Prototype development"""
        return {
            'status': 'completed',
            'prototypes': {
                'count': 3,
                'approaches': ['algorithmic', 'heuristic', 'hybrid'],
                'success_probability': 0.75
            },
            'innovation_level': 'high'
        }
    
    async def _green_turtle_processing(self, problem_input: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Green Turtle: Resource allocation"""
        return {
            'status': 'completed',
            'resource_allocation': {
                'budget_allocated': 10000,
                'compute_hours': 500,
                'storage_gb': 1000,
                'sustainability_score': 0.95
            },
            'budget_efficiency': 'optimal'
        }
    
    async def _blue_dolphin_processing(self, problem_input: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Blue Dolphin: Communication and marketing"""
        return {
            'status': 'completed',
            'communication_plan': {
                'channels': ['internal', 'external', 'stakeholder'],
                'message_clarity': 0.92,
                'brand_safety_score': 0.98
            },
            'influence_potential': 'high'
        }
    
    async def _purple_elephant_processing(self, problem_input: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Purple Elephant: Empathy and ethics analysis"""
        return {
            'status': 'completed',
            'empathy_analysis': {
                'stakeholder_impact': 'positive',
                'ethical_score': 0.88,
                'sentiment_prediction': 'favorable',
                'risk_assessment': 'low'
            },
            'human_centered_design': 'excellent'
        }
    
    async def _execute_feedback_loop(self, enterprise_results: Dict[str, Any], cycle_id: str) -> Dict[str, Any]:
        """
        Purple Elephant feedback loop - continuous reflection and improvement
        """
        # Analyze all enterprise results
        overall_sentiment = self._calculate_overall_sentiment(enterprise_results)
        improvement_suggestions = self._generate_improvement_suggestions(enterprise_results)
        
        return {
            'cycle_id': cycle_id,
            'overall_sentiment': overall_sentiment,
            'improvement_suggestions': improvement_suggestions,
            'feedback_quality': 'high',
            'next_cycle_recommendations': {
                'focus_areas': ['optimization', 'efficiency', 'innovation'],
                'priority_adjustments': ['increase_yellow_creativity', 'enhance_purple_empathy']
            }
        }
    
    def _calculate_overall_sentiment(self, enterprise_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall sentiment from all enterprise results"""
        sentiments = []
        for enterprise, result in enterprise_results.items():
            if 'processing_result' in result:
                # Extract sentiment indicators from each enterprise
                if enterprise == 'purple':
                    sentiments.append(result['processing_result'].get('empathy_analysis', {}).get('sentiment_prediction', 'neutral'))
                else:
                    sentiments.append('positive')  # Simplified for demo
        
        return {
            'overall_score': 0.85,
            'confidence': 0.90,
            'trend': 'improving',
            'key_insights': ['Strong collaboration', 'High innovation potential', 'Ethical alignment']
        }
    
    def _generate_improvement_suggestions(self, enterprise_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement suggestions based on enterprise results"""
        return [
            {
                'enterprise': 'yellow',
                'suggestion': 'Increase prototype diversity',
                'priority': 'medium',
                'expected_impact': 'higher_innovation'
            },
            {
                'enterprise': 'purple',
                'suggestion': 'Enhance stakeholder empathy modeling',
                'priority': 'high',
                'expected_impact': 'better_human_alignment'
            }
        ]
    
    async def _synthesize_final_decision(self, enterprise_results: Dict[str, Any], 
                                       feedback_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize final decision from all enterprise inputs and feedback
        """
        # Aggregate insights from all enterprises
        aggregated_insights = []
        for enterprise, result in enterprise_results.items():
            if 'processing_result' in result:
                insights = result['processing_result']
                aggregated_insights.append({
                    'enterprise': enterprise,
                    'insights': insights,
                    'confidence': 0.85
                })
        
        # Create final decision
        final_decision = {
            'decision_id': str(uuid.uuid4()),
            'recommendation': 'proceed_with_implementation',
            'confidence': 0.88,
            'rationale': 'Strong multi-enterprise alignment with positive sentiment',
            'implementation_plan': {
                'phases': ['prototype', 'test', 'deploy', 'monitor'],
                'timeline': '4-6 weeks',
                'success_metrics': ['performance', 'adoption', 'satisfaction']
            },
            'risk_mitigation': {
                'identified_risks': ['technical_complexity', 'resource_constraints'],
                'mitigation_strategies': ['incremental_rollout', 'backup_plans']
            },
            'feedback_integration': feedback_result.get('next_cycle_recommendations', {})
        }
        
        return final_decision

# Global instance
autonomous_flow = AutonomousFlowEngine()
