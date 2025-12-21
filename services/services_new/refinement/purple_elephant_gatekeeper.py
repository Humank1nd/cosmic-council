"""
Purple Elephant - Reflection & Gatekeeping Agent
The Purple Elephant serves dual roles:
1. Reflector Agent: Synthesizes outputs and applies human-centered lenses
2. Gatekeeper Agent: Evaluates solution sufficiency and routes decisions
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

try:
    from .database import DatabaseManager
    from .ai_integrations import AIIntegrationManager
    from .monitoring import MetricsCollector
    from .purple_elephant_database import PurpleElephantDatabase
    from .mcp_system import MCPManager, SectorType, LayerType
except ImportError:
    # For testing
    from database import DatabaseManager
    from ai_integrations import AIIntegrationManager
    from monitoring import MetricsCollector
    from purple_elephant_database import PurpleElephantDatabase
    from mcp_system import MCPManager, SectorType, LayerType


class SolutionStatus(Enum):
    """Solution evaluation status."""
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"
    NEEDS_REFINEMENT = "needs_refinement"
    CONTRADICTORY = "contradictory"


class RoutingDecision(Enum):
    """Routing decisions for the gatekeeper."""
    EXIT_UPWARD = "exit_upward"
    DESCEND_SECTOR = "descend_sector"
    RETRY_CYCLE = "retry_cycle"
    ESCALATE_HUMAN = "escalate_human"


@dataclass
class ReflectionReport:
    """Report from the Reflector Agent."""
    report_id: str
    cycle_id: str
    summary: str
    contradictions: List[str]
    empathy_insights: Dict[str, Any]
    sector_analysis: Dict[str, Any]
    confidence_indicators: Dict[str, float]
    created_at: datetime


@dataclass
class GatekeeperDecision:
    """Decision from the Gatekeeper Agent."""
    decision_id: str
    report_id: str
    status: SolutionStatus
    confidence_score: float
    completeness_score: float
    alignment_score: float
    failing_sectors: List[str]
    routing_decision: RoutingDecision
    routing_target: Optional[str]
    rationale: str
    created_at: datetime


class ReflectorAgent:
    """Purple Elephant's Reflection sub-agent."""
    
    def __init__(self, ai_manager: AIIntegrationManager, db_manager: DatabaseManager):
        self.ai_manager = ai_manager
        self.db_manager = db_manager
        self.purple_db = PurpleElephantDatabase(db_manager)
        self.mcp_manager = MCPManager()
    
    async def synthesize_cycle_outputs(self, cycle_id: str) -> ReflectionReport:
        """Synthesize outputs from all sectors in the cycle."""
        
        # Get cycle data using real database
        cycle_data = await self.purple_db.get_cycle_data(cycle_id)
        sector_outputs = await self.purple_db.get_sector_outputs(cycle_id)
        
        # Analyze each sector's contribution
        sector_analysis = {}
        contradictions = []
        empathy_insights = {}
        confidence_indicators = {}
        
        # Red Owl Analysis (Research & Inquiry)
        red_output = sector_outputs.get("red", {})
        sector_analysis["red"] = await self._analyze_research_quality(red_output)
        if sector_analysis["red"]["gaps"]:
            contradictions.extend([f"Research gap: {gap}" for gap in sector_analysis["red"]["gaps"]])
        
        # Orange Orangutan Analysis (Planning & Logistics)
        orange_output = sector_outputs.get("orange", {})
        sector_analysis["orange"] = await self._analyze_plan_quality(orange_output)
        if sector_analysis["orange"]["inconsistencies"]:
            contradictions.extend([f"Plan inconsistency: {inc}" for inc in sector_analysis["orange"]["inconsistencies"]])
        
        # Yellow Honeybee Analysis (Development & Creativity)
        yellow_output = sector_outputs.get("yellow", {})
        sector_analysis["yellow"] = await self._analyze_creativity_quality(yellow_output)
        if sector_analysis["yellow"]["risks"]:
            empathy_insights["innovation_risks"] = sector_analysis["yellow"]["risks"]
        
        # Green Tortoise Analysis (Budget & Sustainability)
        green_output = sector_outputs.get("green", {})
        sector_analysis["green"] = await self._analyze_sustainability_quality(green_output)
        if sector_analysis["green"]["budget_violations"]:
            contradictions.extend([f"Budget violation: {violation}" for violation in sector_analysis["green"]["budget_violations"]])
        
        # Blue Dolphin Analysis (Communication & Marketing)
        blue_output = sector_outputs.get("blue", {})
        sector_analysis["blue"] = await self._analyze_communication_quality(blue_output)
        if sector_analysis["blue"]["stakeholder_concerns"]:
            empathy_insights["stakeholder_concerns"] = sector_analysis["blue"]["stakeholder_concerns"]
        
        # Calculate confidence indicators
        confidence_indicators = await self._calculate_confidence_indicators(sector_analysis)
        
        # Generate summary
        summary = await self._generate_reflection_summary(sector_analysis, contradictions, empathy_insights)
        
        # Create reflection report
        report = ReflectionReport(
            report_id=str(uuid.uuid4()),
            cycle_id=cycle_id,
            summary=summary,
            contradictions=contradictions,
            empathy_insights=empathy_insights,
            sector_analysis=sector_analysis,
            confidence_indicators=confidence_indicators,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store in database
        await self.purple_db.create_reflection_report(report)
        
        return report
    
    async def _analyze_research_quality(self, red_output: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of research from Red Owl."""
        analysis = {
            "completeness": 0.0,
            "reliability": 0.0,
            "relevance": 0.0,
            "gaps": [],
            "strengths": []
        }
        
        # Check for evidence quality
        evidence_refs = red_output.get("evidence_refs", [])
        if len(evidence_refs) < 3:
            analysis["gaps"].append("Insufficient evidence sources")
        else:
            analysis["strengths"].append("Multiple evidence sources")
        
        # Check for stakeholder input
        stakeholders = red_output.get("stakeholders", [])
        if len(stakeholders) < 2:
            analysis["gaps"].append("Limited stakeholder perspective")
        else:
            analysis["strengths"].append("Diverse stakeholder input")
        
        # Calculate scores
        analysis["completeness"] = min(1.0, len(evidence_refs) / 5.0)
        analysis["reliability"] = red_output.get("confidence", 0.0)
        analysis["relevance"] = red_output.get("relevance_score", 0.0)
        
        return analysis
    
    async def _analyze_plan_quality(self, orange_output: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of planning from Orange Orangutan."""
        analysis = {
            "structure": 0.0,
            "feasibility": 0.0,
            "completeness": 0.0,
            "inconsistencies": [],
            "strengths": []
        }
        
        # Check plan structure
        plan_steps = orange_output.get("plan_steps", [])
        if len(plan_steps) < 3:
            analysis["inconsistencies"].append("Insufficient plan steps")
        else:
            analysis["strengths"].append("Detailed plan structure")
        
        # Check resource allocation
        resources = orange_output.get("resources", {})
        if not resources:
            analysis["inconsistencies"].append("Missing resource allocation")
        else:
            analysis["strengths"].append("Resource allocation defined")
        
        # Check dependencies
        dependencies = orange_output.get("dependencies", [])
        if not dependencies:
            analysis["inconsistencies"].append("Missing dependency analysis")
        else:
            analysis["strengths"].append("Dependency mapping complete")
        
        # Calculate scores
        analysis["structure"] = min(1.0, len(plan_steps) / 5.0)
        analysis["feasibility"] = orange_output.get("feasibility_score", 0.0)
        analysis["completeness"] = orange_output.get("completeness_score", 0.0)
        
        return analysis
    
    async def _analyze_creativity_quality(self, yellow_output: Dict[str, Any]) -> Dict[str, Any]:
        """Actually analyze creativity quality using real metrics."""
        analysis = {
            "quality_score": 0.0,
            "innovation": 0.0,
            "feasibility": 0.0,
            "novelty": 0.0,
            "completeness": 0.0,
            "risks": [],
            "strengths": [],
            "detailed_analysis": ""
        }
        
        # Get actual solutions, not just count them
        solutions = yellow_output.get("solutions", [])
        prototypes = yellow_output.get("prototypes", [])
        
        if not solutions:
            analysis["risks"].append("No solutions provided")
            analysis["detailed_analysis"] = "Yellow Honeybee failed to generate any solutions"
            return analysis
        
        # Analyze each solution for actual quality
        quality_scores = []
        innovation_scores = []
        feasibility_scores = []
        
        for i, solution in enumerate(solutions):
            # Check for innovation (novel approaches)
            innovation_score = await self._measure_innovation(solution)
            innovation_scores.append(innovation_score)
            
            # Check for feasibility (can it actually work?)
            feasibility_score = await self._measure_feasibility(solution)
            feasibility_scores.append(feasibility_score)
            
            # Check for completeness (does it address the problem?)
            completeness_score = await self._measure_solution_completeness(solution)
            
            # Weighted quality score
            quality = (innovation_score * 0.3 + feasibility_score * 0.4 + completeness_score * 0.3)
            quality_scores.append(quality)
        
        # Calculate overall quality metrics
        avg_quality = sum(quality_scores) / len(quality_scores)
        quality_variance = self._calculate_variance(quality_scores)
        best_solution_quality = max(quality_scores)
        worst_solution_quality = min(quality_scores)
        
        # Analyze prototype quality
        prototype_quality = 0.0
        if prototypes:
            prototype_quality = await self._analyze_prototype_quality(prototypes)
        else:
            analysis["risks"].append("No prototype validation provided")
        
        # Determine strengths and risks based on actual analysis
        if avg_quality >= 0.8:
            analysis["strengths"].append("High-quality solutions generated")
        elif avg_quality >= 0.6:
            analysis["strengths"].append("Moderate-quality solutions generated")
        else:
            analysis["risks"].append("Low-quality solutions generated")
        
        if quality_variance < 0.1:
            analysis["strengths"].append("Consistent solution quality")
        elif quality_variance > 0.3:
            analysis["risks"].append("Inconsistent solution quality")
        
        if best_solution_quality >= 0.9:
            analysis["strengths"].append("At least one excellent solution found")
        
        if worst_solution_quality < 0.3:
            analysis["risks"].append("Some solutions are very poor quality")
        
        # Calculate final scores
        analysis["quality_score"] = avg_quality
        analysis["innovation"] = sum(innovation_scores) / len(innovation_scores)
        analysis["feasibility"] = sum(feasibility_scores) / len(feasibility_scores)
        analysis["novelty"] = analysis["innovation"]  # Novelty is part of innovation
        analysis["completeness"] = avg_quality  # Completeness is reflected in overall quality
        
        analysis["detailed_analysis"] = (
            f"Analyzed {len(solutions)} solutions. Average quality: {avg_quality:.2f}, "
            f"Variance: {quality_variance:.2f}, Best: {best_solution_quality:.2f}, "
            f"Worst: {worst_solution_quality:.2f}. Prototype quality: {prototype_quality:.2f}"
        )
        
        return analysis
    
    async def _measure_innovation(self, solution: Dict[str, Any]) -> float:
        """Measure the innovation level of a solution."""
        innovation_score = 0.0
        
        # Check for novel approaches
        approach = solution.get("approach", "")
        if approach:
            # Use AI to assess novelty
            prompt = f"""
            Rate the innovation level of this solution approach on a scale of 0-1:
            
            Approach: {approach}
            
            Consider:
            - Novelty compared to standard approaches
            - Creative problem-solving elements
            - Unconventional thinking
            - Breakthrough potential
            
            Return only a number between 0 and 1.
            """
            
            try:
                response = await self.ai_manager.process_with_llm(prompt, provider="openai")
                innovation_score = float(response.content.strip())
            except:
                # Fallback: simple heuristic
                innovation_score = min(1.0, len(approach.split()) / 50.0)  # Rough heuristic
        
        return innovation_score
    
    async def _measure_feasibility(self, solution: Dict[str, Any]) -> float:
        """Measure the feasibility of a solution."""
        feasibility_score = 0.0
        
        # Check for implementation details
        implementation = solution.get("implementation", {})
        resources = implementation.get("resources", [])
        timeline = implementation.get("timeline", "")
        risks = implementation.get("risks", [])
        
        # Score based on implementation completeness
        if resources and timeline:
            feasibility_score += 0.4
        if risks:
            feasibility_score += 0.2  # Risk awareness is good
        
        # Check for technical feasibility
        technical_details = solution.get("technical_details", "")
        if technical_details:
            # Use AI to assess technical feasibility
            prompt = f"""
            Rate the technical feasibility of this solution on a scale of 0-1:
            
            Technical Details: {technical_details}
            
            Consider:
            - Current technology availability
            - Implementation complexity
            - Resource requirements
            - Technical risks
            
            Return only a number between 0 and 1.
            """
            
            try:
                response = await self.ai_manager.process_with_llm(prompt, provider="openai")
                tech_feasibility = float(response.content.strip())
                feasibility_score += tech_feasibility * 0.4
            except:
                # Fallback: simple heuristic
                feasibility_score += min(0.4, len(technical_details.split()) / 100.0)
        
        return min(1.0, feasibility_score)
    
    async def _measure_solution_completeness(self, solution: Dict[str, Any]) -> float:
        """Measure how completely a solution addresses the problem."""
        completeness_score = 0.0
        
        # Check for problem coverage
        problem_areas = solution.get("problem_areas_addressed", [])
        if problem_areas:
            completeness_score += min(0.5, len(problem_areas) * 0.1)
        
        # Check for solution components
        components = solution.get("components", [])
        if components:
            completeness_score += min(0.3, len(components) * 0.05)
        
        # Check for success metrics
        success_metrics = solution.get("success_metrics", [])
        if success_metrics:
            completeness_score += min(0.2, len(success_metrics) * 0.05)
        
        return min(1.0, completeness_score)
    
    def _calculate_variance(self, scores: List[float]) -> float:
        """Calculate variance of a list of scores."""
        if len(scores) <= 1:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance
    
    async def _analyze_prototype_quality(self, prototypes: List[Dict[str, Any]]) -> float:
        """Analyze the quality of prototypes."""
        if not prototypes:
            return 0.0
        
        total_quality = 0.0
        for prototype in prototypes:
            # Check prototype completeness
            completeness = 0.0
            if prototype.get("design"):
                completeness += 0.3
            if prototype.get("implementation"):
                completeness += 0.3
            if prototype.get("testing"):
                completeness += 0.2
            if prototype.get("results"):
                completeness += 0.2
            
            total_quality += completeness
        
        return total_quality / len(prototypes)
    
    async def _analyze_sustainability_quality(self, green_output: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of sustainability from Green Tortoise."""
        analysis = {
            "budget_compliance": 0.0,
            "sustainability": 0.0,
            "risk_mitigation": 0.0,
            "budget_violations": [],
            "strengths": []
        }
        
        # Check budget compliance
        budget = green_output.get("budget", {})
        budget_limit = green_output.get("budget_limit", 0)
        total_cost = budget.get("total_cost", 0)
        
        if total_cost > budget_limit:
            analysis["budget_violations"].append(f"Budget exceeded: ${total_cost} > ${budget_limit}")
        else:
            analysis["strengths"].append("Budget within limits")
        
        # Check sustainability metrics
        sustainability = green_output.get("sustainability", {})
        if not sustainability:
            analysis["budget_violations"].append("Missing sustainability analysis")
        else:
            analysis["strengths"].append("Sustainability metrics included")
        
        # Calculate scores
        analysis["budget_compliance"] = min(1.0, budget_limit / max(total_cost, 1))
        analysis["sustainability"] = green_output.get("sustainability_score", 0.0)
        analysis["risk_mitigation"] = green_output.get("risk_mitigation_score", 0.0)
        
        return analysis
    
    async def _analyze_communication_quality(self, blue_output: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of communication from Blue Dolphin."""
        analysis = {
            "clarity": 0.0,
            "persuasiveness": 0.0,
            "stakeholder_alignment": 0.0,
            "stakeholder_concerns": [],
            "strengths": []
        }
        
        # Check message clarity
        messages = blue_output.get("messages", [])
        if not messages:
            analysis["stakeholder_concerns"].append("No communication strategy")
        else:
            analysis["strengths"].append("Communication strategy defined")
        
        # Check stakeholder feedback
        feedback = blue_output.get("stakeholder_feedback", {})
        concerns = feedback.get("concerns", [])
        if concerns:
            analysis["stakeholder_concerns"].extend(concerns)
        else:
            analysis["strengths"].append("No stakeholder concerns raised")
        
        # Calculate scores
        analysis["clarity"] = blue_output.get("clarity_score", 0.0)
        analysis["persuasiveness"] = blue_output.get("persuasiveness_score", 0.0)
        analysis["stakeholder_alignment"] = blue_output.get("stakeholder_alignment_score", 0.0)
        
        return analysis
    
    async def _calculate_confidence_indicators(self, sector_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall confidence indicators."""
        indicators = {
            "overall_confidence": 0.0,
            "completeness": 0.0,
            "consistency": 0.0,
            "feasibility": 0.0,
            "stakeholder_satisfaction": 0.0
        }
        
        # Calculate overall confidence
        sector_scores = []
        for sector, analysis in sector_analysis.items():
            if isinstance(analysis, dict):
                sector_score = sum(analysis.get(key, 0.0) for key in analysis if isinstance(analysis[key], (int, float)))
                sector_scores.append(sector_score / len([k for k in analysis if isinstance(analysis[k], (int, float))]))
        
        indicators["overall_confidence"] = sum(sector_scores) / len(sector_scores) if sector_scores else 0.0
        
        # Calculate completeness
        completeness_scores = [
            sector_analysis.get("red", {}).get("completeness", 0.0),
            sector_analysis.get("orange", {}).get("completeness", 0.0),
            sector_analysis.get("yellow", {}).get("feasibility", 0.0),
            sector_analysis.get("green", {}).get("budget_compliance", 0.0),
            sector_analysis.get("blue", {}).get("stakeholder_alignment", 0.0)
        ]
        indicators["completeness"] = sum(completeness_scores) / len(completeness_scores)
        
        # Calculate consistency (inverse of contradictions)
        contradiction_count = sum(len(analysis.get("contradictions", [])) for analysis in sector_analysis.values() if isinstance(analysis, dict))
        indicators["consistency"] = max(0.0, 1.0 - (contradiction_count / 10.0))
        
        # Calculate feasibility
        feasibility_scores = [
            sector_analysis.get("orange", {}).get("feasibility", 0.0),
            sector_analysis.get("yellow", {}).get("feasibility", 0.0),
            sector_analysis.get("green", {}).get("risk_mitigation", 0.0)
        ]
        indicators["feasibility"] = sum(feasibility_scores) / len(feasibility_scores)
        
        # Calculate stakeholder satisfaction
        indicators["stakeholder_satisfaction"] = sector_analysis.get("blue", {}).get("stakeholder_alignment", 0.0)
        
        return indicators
    
    async def _generate_reflection_summary(self, sector_analysis: Dict[str, Any], contradictions: List[str], empathy_insights: Dict[str, Any]) -> str:
        """Generate a comprehensive reflection summary."""
        
        # Use AI to generate empathetic summary
        prompt = f"""
        As the Purple Elephant, provide a compassionate and wise reflection on this problem-solving cycle.
        
        Sector Analysis:
        {json.dumps(sector_analysis, indent=2)}
        
        Contradictions Found:
        {contradictions}
        
        Empathy Insights:
        {json.dumps(empathy_insights, indent=2)}
        
        Please provide a summary that:
        1. Acknowledges the effort and insights from each sector
        2. Identifies areas of strength and concern
        3. Offers compassionate guidance for improvement
        4. Maintains hope and wisdom in the face of challenges
        """
        
        try:
            response = await self.ai_manager.process_with_llm(prompt, provider="anthropic")
            return response.content
        except Exception as e:
            # Fallback to template-based summary
            return self._generate_fallback_summary(sector_analysis, contradictions, empathy_insights)
    
    def _generate_fallback_summary(self, sector_analysis: Dict[str, Any], contradictions: List[str], empathy_insights: Dict[str, Any]) -> str:
        """Generate a fallback summary without AI."""
        summary_parts = []
        
        summary_parts.append("The Council has completed a cycle of deep reflection and synthesis.")
        
        if contradictions:
            summary_parts.append(f"Several contradictions were identified: {', '.join(contradictions[:3])}")
        else:
            summary_parts.append("No major contradictions were found in the analysis.")
        
        if empathy_insights:
            summary_parts.append("Key empathy insights were gathered about stakeholder needs and concerns.")
        
        summary_parts.append("The Gatekeeper will now evaluate whether this cycle has produced a sufficient solution.")
        
        return " ".join(summary_parts)
    
    async def _detect_real_contradictions(self, sector_outputs: Dict[str, Any]) -> List[str]:
        """Actually detect contradictions between sectors."""
        contradictions = []
        
        # Check Red vs Orange: Does the research support the plan?
        red_evidence = sector_outputs.get("red", {}).get("evidence", [])
        orange_plan = sector_outputs.get("orange", {}).get("plan_steps", [])
        
        for plan_step in orange_plan:
            supporting_evidence = await self._find_supporting_evidence(plan_step, red_evidence)
            if not supporting_evidence:
                contradictions.append(f"Plan step '{plan_step}' lacks supporting evidence from research")
        
        # Check Orange vs Green: Does the plan fit the budget?
        orange_resources = sector_outputs.get("orange", {}).get("resource_requirements", {})
        green_budget = sector_outputs.get("green", {}).get("budget", {})
        
        total_required = sum(orange_resources.values()) if orange_resources else 0
        total_available = green_budget.get("total_budget", 0)
        
        if total_required > total_available:
            contradictions.append(f"Resource requirements (${total_required}) exceed budget (${total_available})")
        
        # Check Yellow vs Green: Are the prototypes sustainable?
        yellow_prototypes = sector_outputs.get("yellow", {}).get("prototypes", [])
        green_sustainability = sector_outputs.get("green", {}).get("sustainability_metrics", {})
        
        for prototype in yellow_prototypes:
            if not await self._is_prototype_sustainable(prototype, green_sustainability):
                prototype_name = prototype.get("name", "Unnamed prototype")
                contradictions.append(f"Prototype '{prototype_name}' fails sustainability requirements")
        
        # Check Blue vs All: Does communication align with reality?
        blue_messages = sector_outputs.get("blue", {}).get("messages", [])
        for message in blue_messages:
            if not await self._verify_message_accuracy(message, sector_outputs):
                contradictions.append(f"Communication message contains inaccuracies: {message.get('content', '')[:50]}...")
        
        # Check for temporal contradictions
        temporal_contradictions = await self._check_temporal_consistency(sector_outputs)
        contradictions.extend(temporal_contradictions)
        
        return contradictions
    
    async def _find_supporting_evidence(self, plan_step: str, evidence_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find evidence that supports a specific plan step."""
        supporting_evidence = []
        
        for evidence in evidence_list:
            # Use AI to check if evidence supports the plan step
            prompt = f"""
            Does this evidence support the following plan step?
            
            Plan Step: {plan_step}
            Evidence: {evidence.get('content', '')}
            
            Answer with only: YES or NO
            """
            
            try:
                response = await self.ai_manager.process_with_llm(prompt, provider="openai")
                if response.content.strip().upper() == "YES":
                    supporting_evidence.append(evidence)
            except:
                # Fallback: simple keyword matching
                if any(keyword in plan_step.lower() for keyword in evidence.get('keywords', [])):
                    supporting_evidence.append(evidence)
        
        return supporting_evidence
    
    async def _is_prototype_sustainable(self, prototype: Dict[str, Any], sustainability_metrics: Dict[str, Any]) -> bool:
        """Check if a prototype meets sustainability requirements."""
        prototype_impact = prototype.get("environmental_impact", {})
        sustainability_requirements = sustainability_metrics.get("requirements", {})
        
        # Check carbon footprint
        prototype_carbon = prototype_impact.get("carbon_footprint", 0)
        max_carbon = sustainability_requirements.get("max_carbon_footprint", float('inf'))
        
        if prototype_carbon > max_carbon:
            return False
        
        # Check resource usage
        prototype_resources = prototype_impact.get("resource_usage", {})
        max_resources = sustainability_requirements.get("max_resource_usage", {})
        
        for resource, usage in prototype_resources.items():
            max_usage = max_resources.get(resource, float('inf'))
            if usage > max_usage:
                return False
        
        return True
    
    async def _verify_message_accuracy(self, message: Dict[str, Any], sector_outputs: Dict[str, Any]) -> bool:
        """Verify that a communication message is accurate based on sector outputs."""
        message_content = message.get("content", "")
        
        # Check against research findings
        red_evidence = sector_outputs.get("red", {}).get("evidence", [])
        for evidence in red_evidence:
            if not await self._check_message_against_evidence(message_content, evidence):
                return False
        
        # Check against plan details
        orange_plan = sector_outputs.get("orange", {}).get("plan_steps", [])
        for plan_step in orange_plan:
            if not await self._check_message_against_plan(message_content, plan_step):
                return False
        
        return True
    
    async def _check_message_against_evidence(self, message: str, evidence: Dict[str, Any]) -> bool:
        """Check if message is consistent with evidence."""
        evidence_content = evidence.get("content", "")
        
        prompt = f"""
        Is this message consistent with this evidence?
        
        Message: {message}
        Evidence: {evidence_content}
        
        Answer with only: CONSISTENT or INCONSISTENT
        """
        
        try:
            response = await self.ai_manager.process_with_llm(prompt, provider="openai")
            return response.content.strip().upper() == "CONSISTENT"
        except:
            # Fallback: simple keyword checking
            return True  # Assume consistent if we can't verify
    
    async def _check_message_against_plan(self, message: str, plan_step: str) -> bool:
        """Check if message is consistent with plan step."""
        prompt = f"""
        Is this message consistent with this plan step?
        
        Message: {message}
        Plan Step: {plan_step}
        
        Answer with only: CONSISTENT or INCONSISTENT
        """
        
        try:
            response = await self.ai_manager.process_with_llm(prompt, provider="openai")
            return response.content.strip().upper() == "CONSISTENT"
        except:
            # Fallback: simple keyword checking
            return True  # Assume consistent if we can't verify
    
    async def _check_temporal_consistency(self, sector_outputs: Dict[str, Any]) -> List[str]:
        """Check for temporal contradictions between sectors."""
        contradictions = []
        
        # Check timeline consistency
        orange_timeline = sector_outputs.get("orange", {}).get("timeline", {})
        yellow_timeline = sector_outputs.get("yellow", {}).get("development_timeline", {})
        green_timeline = sector_outputs.get("green", {}).get("implementation_timeline", {})
        
        # Check if development timeline fits within implementation timeline
        if orange_timeline and yellow_timeline:
            orange_end = orange_timeline.get("end_date")
            yellow_start = yellow_timeline.get("start_date")
            
            if orange_end and yellow_start and orange_end > yellow_start:
                contradictions.append("Development timeline conflicts with planning timeline")
        
        # Check if implementation timeline fits within budget timeline
        if yellow_timeline and green_timeline:
            yellow_end = yellow_timeline.get("end_date")
            green_start = green_timeline.get("start_date")
            
            if yellow_end and green_start and yellow_end > green_start:
                contradictions.append("Implementation timeline conflicts with development timeline")
        
        return contradictions
    
    async def _make_mcp_routing_decision(self, status: SolutionStatus, failing_sectors: List[str], 
                                       current_layer: str, cycle_count: int, 
                                       reflection_report: ReflectionReport) -> Tuple[RoutingDecision, Optional[str]]:
        """Make routing decision using MCP context analysis."""
        
        # Convert string layer to LayerType enum
        try:
            current_layer_enum = LayerType(current_layer.lower())
        except ValueError:
            current_layer_enum = LayerType.DECI  # Default fallback
        
        if status == SolutionStatus.SUFFICIENT:
            return RoutingDecision.EXIT_UPWARD, None
        
        elif status == SolutionStatus.CONTRADICTORY:
            # Contradictions detected - need to resolve at current layer first
            if cycle_count < self.max_cycles_per_layer:
                return RoutingDecision.RETRY_CYCLE, None
            else:
                # Too many cycles, escalate to human
                return RoutingDecision.ESCALATE_HUMAN, None
        
        elif status in [SolutionStatus.INSUFFICIENT, SolutionStatus.NEEDS_REFINEMENT]:
            # Solution insufficient - determine if we should descend or retry
            
            if cycle_count >= self.max_cycles_per_layer:
                # Max cycles reached at current layer
                if current_layer_enum == LayerType.QUECTO:
                    # Already at deepest layer
                    return RoutingDecision.ESCALATE_HUMAN, None
                else:
                    # Force descent to next layer
                    next_layer = self._get_next_layer(current_layer_enum)
                    return RoutingDecision.DESCEND_SECTOR, f"descend:all:{next_layer.value}"
            
            # Analyze which sector is the bottleneck using MCP context
            bottleneck_sector = await self._identify_mcp_bottleneck(reflection_report.sector_analysis, failing_sectors)
            
            if bottleneck_sector:
                # Descend one layer deeper into the failing sector
                next_layer = self._get_next_layer(current_layer_enum)
                return RoutingDecision.DESCEND_SECTOR, f"descend:{bottleneck_sector}:{next_layer.value}"
            else:
                # No clear bottleneck, retry current cycle
                return RoutingDecision.RETRY_CYCLE, None
        
        else:
            # Unknown status, default to retry
            return RoutingDecision.RETRY_CYCLE, None
    
    async def _identify_mcp_bottleneck(self, sector_analysis: Dict[str, Any], failing_sectors: List[str]) -> Optional[str]:
        """Identify the bottleneck sector using MCP context analysis."""
        
        if not failing_sectors:
            return None
        
        # Analyze each failing sector's MCP context quality
        sector_scores = {}
        
        for sector in failing_sectors:
            analysis = sector_analysis.get(sector, {})
            
            # Get MCP definition for this sector
            try:
                sector_enum = SectorType(sector.lower())
                # Use current layer (could be improved to track actual layer)
                mcp_def = self.mcp_manager.get_mcp_definition(sector_enum, LayerType.DECI)
                
                if mcp_def:
                    # Analyze context quality against MCP constraints
                    context_quality = await self._analyze_mcp_context_quality(analysis, mcp_def)
                    sector_scores[sector] = context_quality
                else:
                    # Fallback to simple quality score
                    sector_scores[sector] = analysis.get("quality_score", 0.0)
                    
            except ValueError:
                # Invalid sector, use fallback
                sector_scores[sector] = analysis.get("quality_score", 0.0)
        
        # Return the sector with the lowest quality score (biggest bottleneck)
        if sector_scores:
            return min(sector_scores.keys(), key=lambda k: sector_scores[k])
        
        return None
    
    async def _analyze_mcp_context_quality(self, sector_analysis: Dict[str, Any], mcp_def) -> float:
        """Analyze sector context quality against MCP constraints."""
        
        quality_score = 0.0
        
        # Check against MCP quality thresholds
        thresholds = mcp_def.constraints.get("quality_thresholds", {})
        min_confidence = thresholds.get("min_confidence", 0.5)
        min_completeness = thresholds.get("min_completeness", 0.5)
        min_accuracy = thresholds.get("min_accuracy", 0.7)
        
        # Get sector scores
        confidence = sector_analysis.get("confidence", 0.0)
        completeness = sector_analysis.get("completeness", 0.0)
        accuracy = sector_analysis.get("accuracy", 0.0)
        
        # Calculate quality based on threshold compliance
        confidence_score = min(1.0, confidence / min_confidence) if min_confidence > 0 else 0.0
        completeness_score = min(1.0, completeness / min_completeness) if min_completeness > 0 else 0.0
        accuracy_score = min(1.0, accuracy / min_accuracy) if min_accuracy > 0 else 0.0
        
        # Weighted average
        quality_score = (confidence_score * 0.4 + completeness_score * 0.4 + accuracy_score * 0.2)
        
        # Check for context size violations
        max_context_size = mcp_def.constraints.get("max_context_size", 1000)
        context_size = len(str(sector_analysis))
        if context_size > max_context_size:
            # Penalize for oversized context
            quality_score *= 0.8
        
        # Check for processing time violations
        processing_time = sector_analysis.get("processing_time_ms", 0)
        time_limit = mcp_def.constraints.get("processing_time_limit", 60) * 1000  # Convert to ms
        if processing_time > time_limit:
            # Penalize for slow processing
            quality_score *= 0.9
        
        return quality_score
    
    def _get_next_layer(self, current_layer: LayerType) -> LayerType:
        """Get the next deeper layer."""
        layer_order = [
            LayerType.DECI, LayerType.CENTI, LayerType.MILLI, LayerType.MICRO,
            LayerType.NANO, LayerType.PICO, LayerType.FEMTO, LayerType.ATTO,
            LayerType.ZEPTO, LayerType.YOCTO, LayerType.RONTO, LayerType.QUECTO
        ]
        
        try:
            current_index = layer_order.index(current_layer)
            if current_index < len(layer_order) - 1:
                return layer_order[current_index + 1]
            else:
                return LayerType.QUECTO  # Already at deepest
        except ValueError:
            return LayerType.CENTI  # Default fallback


class AdaptiveThresholds:
    """Adaptive thresholds that learn from outcomes."""
    
    def __init__(self):
        self.confidence_threshold = 0.5  # Start conservative
        self.completeness_threshold = 0.5
        self.alignment_threshold = 0.5
        self.learning_rate = 0.01
        self.success_history = []
        self.min_threshold = 0.3
        self.max_threshold = 0.95
    
    async def update_thresholds(self, decision_outcome: str, actual_quality: float, confidence: float, completeness: float, alignment: float):
        """Learn from actual outcomes to adjust thresholds."""
        
        # Store the outcome for analysis
        self.success_history.append({
            "threshold_confidence": self.confidence_threshold,
            "threshold_completeness": self.completeness_threshold,
            "threshold_alignment": self.alignment_threshold,
            "actual_confidence": confidence,
            "actual_completeness": completeness,
            "actual_alignment": alignment,
            "outcome": decision_outcome,
            "quality": actual_quality,
            "timestamp": datetime.now(timezone.utc)
        })
        
        # Adjust thresholds based on outcome
        if decision_outcome == "success":
            # If we succeeded, maybe we can be more aggressive
            self.confidence_threshold = min(self.max_threshold, self.confidence_threshold + self.learning_rate)
            self.completeness_threshold = min(self.max_threshold, self.completeness_threshold + self.learning_rate)
            self.alignment_threshold = min(self.max_threshold, self.alignment_threshold + self.learning_rate)
        elif decision_outcome == "failure":
            # If we failed, be more conservative
            self.confidence_threshold = max(self.min_threshold, self.confidence_threshold - self.learning_rate)
            self.completeness_threshold = max(self.min_threshold, self.completeness_threshold - self.learning_rate)
            self.alignment_threshold = max(self.min_threshold, self.alignment_threshold - self.learning_rate)
        
        # Analyze recent performance
        await self._analyze_recent_performance()
    
    async def _analyze_recent_performance(self):
        """Analyze recent performance to adjust learning rate."""
        if len(self.success_history) < 10:
            return
        
        # Get recent outcomes
        recent_outcomes = self.success_history[-10:]
        success_rate = sum(1 for outcome in recent_outcomes if outcome["outcome"] == "success") / len(recent_outcomes)
        
        # Adjust learning rate based on success rate
        if success_rate > 0.8:
            # High success rate, can be more aggressive
            self.learning_rate = min(0.05, self.learning_rate * 1.1)
        elif success_rate < 0.5:
            # Low success rate, be more conservative
            self.learning_rate = max(0.005, self.learning_rate * 0.9)
    
    def get_current_thresholds(self) -> Dict[str, float]:
        """Get current threshold values."""
        return {
            "confidence": self.confidence_threshold,
            "completeness": self.completeness_threshold,
            "alignment": self.alignment_threshold
        }


class GatekeeperAgent:
    """Purple Elephant's Gatekeeping sub-agent."""
    
    def __init__(self, ai_manager: AIIntegrationManager, db_manager: DatabaseManager, metrics_collector: MetricsCollector):
        self.ai_manager = ai_manager
        self.db_manager = db_manager
        self.metrics_collector = metrics_collector
        self.purple_db = PurpleElephantDatabase(db_manager)
        self.mcp_manager = MCPManager()
        
        # Adaptive thresholds that learn from outcomes
        self.adaptive_thresholds = AdaptiveThresholds()
        
        # Fixed operational limits
        self.max_cycles_per_layer = 3
        self.max_total_cycles = 10
    
    async def evaluate_solution_sufficiency(self, reflection_report: ReflectionReport) -> GatekeeperDecision:
        """Evaluate whether the solution is sufficient and route accordingly."""
        
        # Get problem context using real database
        problem_data = await self.purple_db.get_problem(reflection_report.cycle_id)
        current_layer = problem_data.get("current_layer", "deci")
        cycle_count = problem_data.get("cycle_count", 0)
        
        # Calculate evaluation scores
        confidence_score = reflection_report.confidence_indicators.get("overall_confidence", 0.0)
        completeness_score = reflection_report.confidence_indicators.get("completeness", 0.0)
        alignment_score = reflection_report.confidence_indicators.get("stakeholder_satisfaction", 0.0)
        
        # Get current adaptive thresholds
        thresholds = self.adaptive_thresholds.get_current_thresholds()
        
        # Identify failing sectors using real analysis
        failing_sectors = await self._identify_failing_sectors_real(reflection_report.sector_analysis)
        
        # Detect real contradictions
        real_contradictions = await self._detect_real_contradictions(reflection_report.sector_analysis)
        
        # Determine solution status using adaptive thresholds
        status = self._determine_solution_status_adaptive(
            confidence_score, completeness_score, alignment_score, 
            real_contradictions, failing_sectors, thresholds
        )
        
        # Make MCP-aware routing decision
        routing_decision, routing_target = await self._make_mcp_routing_decision(
            status, failing_sectors, current_layer, cycle_count, reflection_report
        )
        
        # Generate rationale
        rationale = await self._generate_rationale(
            status, routing_decision, confidence_score, completeness_score, 
            alignment_score, failing_sectors, reflection_report
        )
        
        decision = GatekeeperDecision(
            decision_id=str(uuid.uuid4()),
            report_id=reflection_report.report_id,
            status=status,
            confidence_score=confidence_score,
            completeness_score=completeness_score,
            alignment_score=alignment_score,
            failing_sectors=failing_sectors,
            routing_decision=routing_decision,
            routing_target=routing_target,
            rationale=rationale,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store decision in database using real database integration
        await self.purple_db.create_gatekeeper_decision(decision)
        
        # Log decision
        await self._log_decision(decision)
        
        # Update metrics
        await self._update_metrics(decision)
        
        return decision
    
    async def update_thresholds_from_outcome(self, decision: GatekeeperDecision, actual_outcome: str, actual_quality: float):
        """Update adaptive thresholds based on actual outcome."""
        await self.adaptive_thresholds.update_thresholds(
            decision_outcome=actual_outcome,
            actual_quality=actual_quality,
            confidence=decision.confidence_score,
            completeness=decision.completeness_score,
            alignment=decision.alignment_score
        )
        
        # Log the threshold update
        await self.metrics_collector.record_threshold_update(
            decision_id=decision.decision_id,
            new_thresholds=self.adaptive_thresholds.get_current_thresholds(),
            outcome=actual_outcome,
            quality=actual_quality
        )
    
    def _identify_failing_sectors(self, sector_analysis: Dict[str, Any]) -> List[str]:
        """Identify which sectors are failing to meet quality standards."""
        failing_sectors = []
        
        for sector, analysis in sector_analysis.items():
            if not isinstance(analysis, dict):
                continue
            
            # Check for critical gaps
            gaps = analysis.get("gaps", [])
            inconsistencies = analysis.get("inconsistencies", [])
            violations = analysis.get("budget_violations", [])
            
            if gaps or inconsistencies or violations:
                failing_sectors.append(sector)
            
            # Check for low scores
            scores = [v for v in analysis.values() if isinstance(v, (int, float))]
            if scores and sum(scores) / len(scores) < 0.6:
                failing_sectors.append(sector)
        
        return list(set(failing_sectors))
    
    async def _identify_failing_sectors_real(self, sector_analysis: Dict[str, Any]) -> List[str]:
        """Identify failing sectors using real quality analysis."""
        failing_sectors = []
        
        for sector, analysis in sector_analysis.items():
            if not isinstance(analysis, dict):
                continue
            
            # Check for actual quality issues
            quality_score = analysis.get("quality_score", 0.0)
            if quality_score < 0.6:
                failing_sectors.append(sector)
                continue
            
            # Check for specific quality metrics
            innovation = analysis.get("innovation", 0.0)
            feasibility = analysis.get("feasibility", 0.0)
            completeness = analysis.get("completeness", 0.0)
            
            # A sector fails if any critical metric is too low
            if innovation < 0.4 or feasibility < 0.4 or completeness < 0.4:
                failing_sectors.append(sector)
                continue
            
            # Check for risks that indicate failure
            risks = analysis.get("risks", [])
            if len(risks) > 2:  # Too many risks
                failing_sectors.append(sector)
                continue
            
            # Check for critical risks
            critical_risks = [risk for risk in risks if "critical" in risk.lower() or "failed" in risk.lower()]
            if critical_risks:
                failing_sectors.append(sector)
        
        return failing_sectors
    
    def _determine_solution_status_adaptive(self, confidence: float, completeness: float, alignment: float, 
                                          contradictions: List[str], failing_sectors: List[str], 
                                          thresholds: Dict[str, float]) -> SolutionStatus:
        """Determine solution status using adaptive thresholds."""
        
        # Check for critical contradictions
        if contradictions and len(contradictions) > 2:
            return SolutionStatus.CONTRADICTORY
        
        # Check if all adaptive thresholds are met
        if (confidence >= thresholds["confidence"] and 
            completeness >= thresholds["completeness"] and 
            alignment >= thresholds["alignment"] and 
            not failing_sectors):
            return SolutionStatus.SUFFICIENT
        
        # Check if close to thresholds (within 10%)
        threshold_tolerance = 0.1
        if (confidence >= thresholds["confidence"] - threshold_tolerance and 
            completeness >= thresholds["completeness"] - threshold_tolerance and 
            alignment >= thresholds["alignment"] - threshold_tolerance):
            return SolutionStatus.NEEDS_REFINEMENT
        
        return SolutionStatus.INSUFFICIENT
    
    def _determine_solution_status(self, confidence: float, completeness: float, alignment: float, 
                                 contradictions: List[str], failing_sectors: List[str]) -> SolutionStatus:
        """Determine the overall solution status."""
        
        # Check for critical contradictions
        if contradictions and len(contradictions) > 2:
            return SolutionStatus.CONTRADICTORY
        
        # Check if all thresholds are met
        if (confidence >= self.confidence_threshold and 
            completeness >= self.completeness_threshold and 
            alignment >= self.alignment_threshold and 
            not failing_sectors):
            return SolutionStatus.SUFFICIENT
        
        # Check if close to thresholds
        if (confidence >= 0.6 and completeness >= 0.6 and alignment >= 0.6):
            return SolutionStatus.NEEDS_REFINEMENT
        
        return SolutionStatus.INSUFFICIENT
    
    async def _make_routing_decision(self, status: SolutionStatus, failing_sectors: List[str], 
                                   current_layer: str, cycle_count: int, 
                                   reflection_report: ReflectionReport) -> Tuple[RoutingDecision, Optional[str]]:
        """Make the routing decision based on evaluation."""
        
        if status == SolutionStatus.SUFFICIENT:
            return RoutingDecision.EXIT_UPWARD, None
        
        if status == SolutionStatus.CONTRADICTORY:
            return RoutingDecision.ESCALATE_HUMAN, "Contradictory requirements detected"
        
        # Check cycle limits
        if cycle_count >= self.max_total_cycles:
            return RoutingDecision.ESCALATE_HUMAN, "Maximum cycles reached"
        
        # Check layer cycle limits
        layer_cycles = await self.db_manager.get_layer_cycle_count(reflection_report.cycle_id, current_layer)
        if layer_cycles >= self.max_cycles_per_layer:
            # Force descent to next layer
            next_layer = self._get_next_layer(current_layer)
            if next_layer:
                return RoutingDecision.DESCEND_SECTOR, f"descend:{failing_sectors[0] if failing_sectors else 'red'}:{next_layer}"
            else:
                return RoutingDecision.ESCALATE_HUMAN, "Maximum depth reached"
        
        # If we have failing sectors, descend into the weakest one
        if failing_sectors:
            weakest_sector = self._identify_weakest_sector(failing_sectors, reflection_report.sector_analysis)
            return RoutingDecision.DESCEND_SECTOR, f"descend:{weakest_sector}:{current_layer}"
        
        # Otherwise, retry the current cycle
        return RoutingDecision.RETRY_CYCLE, current_layer
    
    def _get_next_layer(self, current_layer: str) -> Optional[str]:
        """Get the next layer in the refinement sequence."""
        layer_sequence = ["deci", "centi", "milli", "micro", "nano", "pico", 
                         "femto", "atto", "zepto", "yocto", "ronto", "quecto"]
        
        try:
            current_index = layer_sequence.index(current_layer)
            if current_index < len(layer_sequence) - 1:
                return layer_sequence[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _identify_weakest_sector(self, failing_sectors: List[str], sector_analysis: Dict[str, Any]) -> str:
        """Identify the weakest sector among the failing ones."""
        weakest_sector = failing_sectors[0]
        lowest_score = float('inf')
        
        for sector in failing_sectors:
            analysis = sector_analysis.get(sector, {})
            if isinstance(analysis, dict):
                scores = [v for v in analysis.values() if isinstance(v, (int, float))]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    if avg_score < lowest_score:
                        lowest_score = avg_score
                        weakest_sector = sector
        
        return weakest_sector
    
    async def _generate_rationale(self, status: SolutionStatus, routing_decision: RoutingDecision,
                                confidence: float, completeness: float, alignment: float,
                                failing_sectors: List[str], reflection_report: ReflectionReport) -> str:
        """Generate a rationale for the decision."""
        
        rationale_parts = []
        
        # Status explanation
        if status == SolutionStatus.SUFFICIENT:
            rationale_parts.append("Solution meets all quality thresholds and is ready for delivery.")
        elif status == SolutionStatus.NEEDS_REFINEMENT:
            rationale_parts.append("Solution is close to quality thresholds but needs refinement.")
        elif status == SolutionStatus.INSUFFICIENT:
            rationale_parts.append("Solution does not meet quality thresholds and requires significant improvement.")
        elif status == SolutionStatus.CONTRADICTORY:
            rationale_parts.append("Solution contains contradictory requirements that need human intervention.")
        
        # Score breakdown
        rationale_parts.append(f"Confidence: {confidence:.2f}, Completeness: {completeness:.2f}, Alignment: {alignment:.2f}")
        
        # Failing sectors
        if failing_sectors:
            rationale_parts.append(f"Failing sectors: {', '.join(failing_sectors)}")
        
        # Routing explanation
        if routing_decision == RoutingDecision.EXIT_UPWARD:
            rationale_parts.append("Routing: Solution approved for delivery.")
        elif routing_decision == RoutingDecision.DESCEND_SECTOR:
            target = reflection_report.cycle_id  # This would be the routing target
            rationale_parts.append(f"Routing: Descending into sector-specific refinement at {target}")
        elif routing_decision == RoutingDecision.RETRY_CYCLE:
            rationale_parts.append("Routing: Retrying current cycle with improvements.")
        elif routing_decision == RoutingDecision.ESCALATE_HUMAN:
            rationale_parts.append("Routing: Escalating to human intervention.")
        
        return " ".join(rationale_parts)
    
    async def _log_decision(self, decision: GatekeeperDecision):
        """Log the gatekeeper decision to the database."""
        await self.db_manager.create_gatekeeper_decision(
            decision_id=decision.decision_id,
            report_id=decision.report_id,
            sufficient=decision.status == SolutionStatus.SUFFICIENT,
            failing_sector=decision.failing_sectors[0] if decision.failing_sectors else None,
            confidence_score=decision.confidence_score,
            routed_to=decision.routing_target or "exit"
        )
    
    async def _update_metrics(self, decision: GatekeeperDecision):
        """Update metrics based on the decision."""
        await self.metrics_collector.record_gatekeeper_decision(
            decision.status.value,
            decision.confidence_score,
            decision.completeness_score,
            decision.alignment_score,
            len(decision.failing_sectors)
        )


class PurpleElephant:
    """Purple Elephant - Reflection & Gatekeeping Agent."""
    
    def __init__(self, ai_manager: AIIntegrationManager, db_manager: DatabaseManager, metrics_collector: MetricsCollector):
        self.reflector = ReflectorAgent(ai_manager, db_manager)
        self.gatekeeper = GatekeeperAgent(ai_manager, db_manager, metrics_collector)
        self.ai_manager = ai_manager
        self.db_manager = db_manager
        self.metrics_collector = metrics_collector
    
    async def process_cycle_reflection(self, cycle_id: str) -> Tuple[ReflectionReport, GatekeeperDecision]:
        """Process a complete cycle reflection and gatekeeping decision."""
        
        # Step 1: Reflect on the cycle
        reflection_report = await self.reflector.synthesize_cycle_outputs(cycle_id)
        
        # Step 2: Evaluate and route
        gatekeeper_decision = await self.gatekeeper.evaluate_solution_sufficiency(reflection_report)
        
        # Step 3: Execute routing decision
        await self._execute_routing_decision(gatekeeper_decision, cycle_id)
        
        return reflection_report, gatekeeper_decision
    
    async def _execute_routing_decision(self, decision: GatekeeperDecision, cycle_id: str):
        """Execute the routing decision."""
        
        if decision.routing_decision == RoutingDecision.EXIT_UPWARD:
            await self._exit_upward(cycle_id, decision)
        elif decision.routing_decision == RoutingDecision.DESCEND_SECTOR:
            await self._descend_sector(cycle_id, decision)
        elif decision.routing_decision == RoutingDecision.RETRY_CYCLE:
            await self._retry_cycle(cycle_id, decision)
        elif decision.routing_decision == RoutingDecision.ESCALATE_HUMAN:
            await self._escalate_human(cycle_id, decision)
    
    async def _exit_upward(self, cycle_id: str, decision: GatekeeperDecision):
        """Exit upward with the solution."""
        await self.db_manager.mark_problem_resolved(cycle_id, decision.confidence_score)
        await self.metrics_collector.record_solution_delivery(cycle_id, decision.confidence_score)
    
    async def _descend_sector(self, cycle_id: str, decision: GatekeeperDecision):
        """Descend into sector-specific refinement."""
        if decision.routing_target and decision.routing_target.startswith("descend:"):
            parts = decision.routing_target.split(":")
            if len(parts) >= 3:
                sector = parts[1]
                layer = parts[2]
                await self.db_manager.create_sector_refinement(cycle_id, sector, layer)
    
    async def _retry_cycle(self, cycle_id: str, decision: GatekeeperDecision):
        """Retry the current cycle."""
        await self.db_manager.increment_cycle_count(cycle_id)
    
    async def _escalate_human(self, cycle_id: str, decision: GatekeeperDecision):
        """Escalate to human intervention."""
        await self.db_manager.mark_problem_escalated(cycle_id, decision.rationale)
        await self.metrics_collector.record_human_escalation(cycle_id, decision.rationale)
