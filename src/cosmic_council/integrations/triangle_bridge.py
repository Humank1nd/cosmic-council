"""
Triangle Bridge - Connects Agent Orchestrator Agents to Service Mesh Hub Triangle Contracts.

This module provides the glue between the ROYGBV agent outputs and the
Six-Seven Triangle Cycle orchestration in the Service Mesh Hub.

Each agent's results are transformed into the appropriate triangle contract
format and reported to the orchestrator.
"""

import httpx
import structlog
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = structlog.get_logger()


@dataclass
class TriangleBridgeConfig:
    """Configuration for the triangle bridge."""
    integration_hub_url: str = "http://localhost:8888"
    timeout_seconds: float = 30.0
    retry_attempts: int = 3


class TriangleBridge:
    """
    Bridges Agent Orchestrator agent outputs to Service Mesh Hub triangle contracts.

    Usage:
        bridge = TriangleBridge()

        # Start a new cycle
        cycle_id = await bridge.start_cycle("problem-123", "How do we improve retention?")

        # After Red Owl completes
        await bridge.report_why_from_red_owl(cycle_id, red_owl_result)

        # After Orange Orangutan completes
        await bridge.report_how_from_orangutan(cycle_id, orangutan_result)

        # ... etc for all agents
    """

    def __init__(self, config: Optional[TriangleBridgeConfig] = None):
        self.config = config or TriangleBridgeConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._active_cycle_id: Optional[str] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.integration_hub_url,
                timeout=self.config.timeout_seconds,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def start_cycle(
        self,
        problem_id: str,
        problem_statement: str,
    ) -> str:
        """
        Start a new triangle cycle for a problem.

        Returns the cycle_id for subsequent triangle reports.
        """
        client = await self._get_client()

        try:
            response = await client.post(
                "/api/v1/triangle/cycle/start",
                json={
                    "problem_id": problem_id,
                    "problem_statement": problem_statement,
                }
            )
            response.raise_for_status()
            result = response.json()
            self._active_cycle_id = result.get("cycle_id")

            logger.info(
                "triangle_cycle_started",
                cycle_id=self._active_cycle_id,
                problem_id=problem_id,
            )
            return self._active_cycle_id

        except Exception as e:
            logger.error("triangle_cycle_start_failed", error=str(e))
            raise

    async def report_why_from_red_owl(
        self,
        cycle_id: str,
        red_owl_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Transform Red Owl research findings into WHY triangle report.

        Red Owl focuses on: research, discovery, root cause analysis
        WHY triangle asks: What is the root cause? What is the purpose?
        """
        # Extract relevant data from Red Owl's output
        research = red_owl_result.get("research_findings", {})
        insights = red_owl_result.get("insights", [])
        questions = red_owl_result.get("prioritized_questions", [])

        # Build WHY payload
        why_payload = {
            "root_cause": self._extract_root_cause(research, insights),
            "purpose": self._extract_purpose(research),
            "assumptions": self._extract_assumptions(research),
            "constraints": self._extract_constraints(research),
            "confidence": red_owl_result.get("confidence_score", 0.8),
            "model_version": red_owl_result.get("model_version", "unknown"),
            "tokens_used": red_owl_result.get("tokens_used", 0),
            "knowledge_sources": self._extract_sources(research),
        }

        return await self._report_triangle(cycle_id, "why", why_payload)

    async def report_how_from_orangutan(
        self,
        cycle_id: str,
        orangutan_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Transform Orange Orangutan planning into HOW triangle report.

        Orangutan focuses on: action planning, dependencies, risk
        HOW triangle asks: What methods? What resources? What barriers?
        """
        action_plan = orangutan_result.get("action_plan", {})
        dependencies = orangutan_result.get("dependencies", [])
        risks = orangutan_result.get("risk_assessment", {})

        how_payload = {
            "methods": self._extract_methods(action_plan),
            "resources": self._extract_resources(action_plan, dependencies),
            "barriers": self._extract_barriers(risks),
            "logistics": {
                "dependencies": dependencies,
                "risk_level": risks.get("overall_risk", "medium"),
            },
            "confidence": orangutan_result.get("confidence_score", 0.8),
        }

        return await self._report_triangle(cycle_id, "how", how_payload)

    async def report_what_from_honeybee(
        self,
        cycle_id: str,
        honeybee_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Transform Yellow Honeybee development into WHAT triangle report.

        Honeybee focuses on: prototypes, testing, implementation
        WHAT triangle asks: What prototypes? What specs? What alternatives?
        """
        prototypes = honeybee_result.get("prototypes", [])
        testing = honeybee_result.get("testing_results", {})
        recommendations = honeybee_result.get("implementation_recommendations", [])

        what_payload = {
            "prototypes": prototypes if isinstance(prototypes, list) else [prototypes],
            "specifications": {
                "testing_status": testing.get("status", "pending"),
                "coverage": testing.get("coverage", 0),
                "recommendations": recommendations,
            },
            "alternatives": honeybee_result.get("creative_notes", []),
            "innovations": self._extract_innovations(honeybee_result),
            "confidence": honeybee_result.get("confidence_score", 0.8),
        }

        return await self._report_triangle(cycle_id, "what", what_payload)

    async def report_when_from_tortoise(
        self,
        cycle_id: str,
        tortoise_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Transform Green Tortoise budget/timeline into WHEN triangle report.

        Tortoise focuses on: budget, resources, ROI
        WHEN triangle asks: What timeline? What milestones? What dependencies?
        """
        budget = tortoise_result.get("budget_allocation", {})
        roi = tortoise_result.get("roi_projection", {})

        when_payload = {
            "timeline": {
                "budget_period": budget.get("period", "quarterly"),
                "total_budget": budget.get("total", 0),
                "roi_timeline": roi.get("payback_period", "unknown"),
            },
            "milestones": self._extract_milestones(budget, roi),
            "dependencies": tortoise_result.get("resource_inventory", {}).get("dependencies", []),
            "critical_path": self._extract_critical_path(budget),
            "confidence": tortoise_result.get("confidence_score", 0.8),
        }

        return await self._report_triangle(cycle_id, "when", when_payload)

    async def report_where_from_dolphin(
        self,
        cycle_id: str,
        dolphin_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Transform Blue Dolphin market analysis into WHERE triangle report.

        Dolphin focuses on: market, communication, go-to-market
        WHERE triangle asks: What locations? What deployment targets? What reach?
        """
        market = dolphin_result.get("market_insights", {})
        gtm = dolphin_result.get("go_to_market_strategy", {})

        where_payload = {
            "locations": self._extract_locations(market, gtm),
            "deployment_targets": gtm.get("channels", []),
            "reach": {
                "target_audience": dolphin_result.get("target_audience", "unknown"),
                "market_size": market.get("size", "unknown"),
                "segments": market.get("segments", []),
            },
            "channels": dolphin_result.get("communication_strategy", {}).get("channels", []),
            "confidence": dolphin_result.get("confidence_score", 0.8),
        }

        return await self._report_triangle(cycle_id, "where", where_payload)

    async def report_who_from_elephant(
        self,
        cycle_id: str,
        elephant_result: Dict[str, Any],
        is_solved: bool = True,
        recursion_reason: str = "",
    ) -> Dict[str, Any]:
        """
        Transform Purple Elephant feedback into WHO triangle report.

        Elephant focuses on: feedback, assessment, improvement
        WHO triangle asks: Who are stakeholders? Is it solved? Final decision?

        This is the critical decision point - Elephant decides if cycle completes
        or recurses back to Red Owl.
        """
        feedback = elephant_result.get("user_feedback_analysis", {})
        assessment = elephant_result.get("performance_assessment", {})
        improvements = elephant_result.get("continuous_improvement", {})

        who_payload = {
            "stakeholders": self._extract_stakeholders(feedback),
            "impact_assessment": {
                "performance": assessment,
                "improvements_needed": improvements.get("action_items", []),
            },
            "affected_parties": feedback.get("user_segments", []),
            "solved": is_solved,
            "resolution": elephant_result.get("support_recommendations", {}).get("summary", ""),
            "recursion_reason": recursion_reason if not is_solved else "",
            "confidence": elephant_result.get("confidence_score", 0.8),
        }

        return await self._report_triangle(cycle_id, "who", who_payload)

    async def _report_triangle(
        self,
        cycle_id: str,
        role: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send triangle report to Service Mesh Hub."""
        client = await self._get_client()

        try:
            response = await client.post(
                f"/api/v1/triangle/cycle/{cycle_id}/report/{role}",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                "triangle_reported",
                cycle_id=cycle_id,
                role=role,
                confidence=payload.get("confidence"),
            )
            return result

        except httpx.HTTPStatusError as e:
            # If endpoint doesn't exist yet, log and continue
            if e.response.status_code == 404:
                logger.warning(
                    "triangle_endpoint_not_found",
                    cycle_id=cycle_id,
                    role=role,
                    message="Service Mesh Hub endpoint not yet implemented",
                )
                return {"status": "pending", "role": role}
            raise
        except Exception as e:
            logger.error(
                "triangle_report_failed",
                cycle_id=cycle_id,
                role=role,
                error=str(e),
            )
            raise

    # =========================================================================
    # Extraction helpers - Transform agent outputs to triangle formats
    # =========================================================================

    def _extract_root_cause(
        self,
        research: Dict[str, Any],
        insights: List[Any],
    ) -> str:
        """Extract root cause from research findings."""
        if "root_cause" in research:
            return research["root_cause"]
        if "findings" in research and research["findings"]:
            return research["findings"][0] if isinstance(research["findings"], list) else str(research["findings"])
        if insights:
            return insights[0] if isinstance(insights[0], str) else str(insights[0])
        return "Root cause analysis pending"

    def _extract_purpose(self, research: Dict[str, Any]) -> str:
        """Extract purpose from research."""
        if "purpose" in research:
            return research["purpose"]
        if "objectives" in research:
            obj = research["objectives"]
            return obj[0] if isinstance(obj, list) else str(obj)
        return "Purpose to be determined"

    def _extract_assumptions(self, research: Dict[str, Any]) -> List[str]:
        """Extract assumptions from research."""
        if "assumptions" in research:
            return research["assumptions"] if isinstance(research["assumptions"], list) else [research["assumptions"]]
        return []

    def _extract_constraints(self, research: Dict[str, Any]) -> List[str]:
        """Extract constraints from research."""
        if "constraints" in research:
            return research["constraints"] if isinstance(research["constraints"], list) else [research["constraints"]]
        if "limitations" in research:
            return research["limitations"] if isinstance(research["limitations"], list) else [research["limitations"]]
        return []

    def _extract_sources(self, research: Dict[str, Any]) -> List[str]:
        """Extract knowledge sources used."""
        if "sources" in research:
            return research["sources"]
        if "references" in research:
            return research["references"]
        return []

    def _extract_methods(self, action_plan: Dict[str, Any]) -> List[str]:
        """Extract methods from action plan."""
        if "methods" in action_plan:
            return action_plan["methods"]
        if "actions" in action_plan:
            return action_plan["actions"]
        if "steps" in action_plan:
            return [step.get("name", str(step)) for step in action_plan["steps"]]
        return []

    def _extract_resources(
        self,
        action_plan: Dict[str, Any],
        dependencies: List[Any],
    ) -> List[str]:
        """Extract required resources."""
        resources = []
        if "resources" in action_plan:
            resources.extend(action_plan["resources"])
        if dependencies:
            for dep in dependencies:
                if isinstance(dep, dict):
                    resources.append(dep.get("name", str(dep)))
                else:
                    resources.append(str(dep))
        return resources

    def _extract_barriers(self, risks: Dict[str, Any]) -> List[str]:
        """Extract barriers from risk assessment."""
        barriers = []
        if "risks" in risks:
            for risk in risks["risks"]:
                if isinstance(risk, dict):
                    barriers.append(risk.get("description", str(risk)))
                else:
                    barriers.append(str(risk))
        if "blockers" in risks:
            barriers.extend(risks["blockers"])
        return barriers

    def _extract_innovations(self, honeybee_result: Dict[str, Any]) -> List[str]:
        """Extract innovative approaches."""
        innovations = []
        if "creative_notes" in honeybee_result:
            notes = honeybee_result["creative_notes"]
            if isinstance(notes, list):
                innovations.extend(notes)
            elif isinstance(notes, str):
                innovations.append(notes)
        return innovations

    def _extract_milestones(
        self,
        budget: Dict[str, Any],
        roi: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Extract milestones from budget/ROI data."""
        milestones = []
        if "milestones" in budget:
            milestones.extend(budget["milestones"])
        if "checkpoints" in roi:
            for cp in roi["checkpoints"]:
                if isinstance(cp, dict):
                    milestones.append(cp)
                else:
                    milestones.append({"name": str(cp)})
        return milestones

    def _extract_critical_path(self, budget: Dict[str, Any]) -> List[str]:
        """Extract critical path items."""
        if "critical_items" in budget:
            return budget["critical_items"]
        if "priorities" in budget:
            return budget["priorities"]
        return []

    def _extract_locations(
        self,
        market: Dict[str, Any],
        gtm: Dict[str, Any],
    ) -> List[str]:
        """Extract deployment locations."""
        locations = []
        if "regions" in market:
            locations.extend(market["regions"])
        if "markets" in gtm:
            locations.extend(gtm["markets"])
        if "geographies" in market:
            locations.extend(market["geographies"])
        return locations or ["global"]

    def _extract_stakeholders(
        self,
        feedback: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """Extract stakeholders from feedback analysis."""
        stakeholders = []
        if "stakeholders" in feedback:
            for s in feedback["stakeholders"]:
                if isinstance(s, dict):
                    stakeholders.append(s)
                else:
                    stakeholders.append({"name": str(s), "role": "participant"})
        if "users" in feedback:
            for u in feedback["users"]:
                stakeholders.append({"name": str(u), "role": "user"})
        return stakeholders or [{"name": "Unknown", "role": "primary"}]


# Convenience function for quick integration
async def run_cycle_with_triangles(
    problem_id: str,
    problem_statement: str,
    agent_results: Dict[str, Dict[str, Any]],
    config: Optional[TriangleBridgeConfig] = None,
) -> Dict[str, Any]:
    """
    Run a complete triangle cycle with pre-computed agent results.

    Args:
        problem_id: Unique problem identifier
        problem_statement: Description of the problem
        agent_results: Dict with keys: red_owl, orangutan, honeybee, tortoise, dolphin, elephant
        config: Optional bridge configuration

    Returns:
        Complete cycle results with triangle validations
    """
    bridge = TriangleBridge(config)

    try:
        cycle_id = await bridge.start_cycle(problem_id, problem_statement)

        results = {"cycle_id": cycle_id, "triangles": {}}

        if "red_owl" in agent_results:
            results["triangles"]["why"] = await bridge.report_why_from_red_owl(
                cycle_id, agent_results["red_owl"]
            )

        if "orangutan" in agent_results:
            results["triangles"]["how"] = await bridge.report_how_from_orangutan(
                cycle_id, agent_results["orangutan"]
            )

        if "honeybee" in agent_results:
            results["triangles"]["what"] = await bridge.report_what_from_honeybee(
                cycle_id, agent_results["honeybee"]
            )

        if "tortoise" in agent_results:
            results["triangles"]["when"] = await bridge.report_when_from_tortoise(
                cycle_id, agent_results["tortoise"]
            )

        if "dolphin" in agent_results:
            results["triangles"]["where"] = await bridge.report_where_from_dolphin(
                cycle_id, agent_results["dolphin"]
            )

        if "elephant" in agent_results:
            results["triangles"]["who"] = await bridge.report_who_from_elephant(
                cycle_id,
                agent_results["elephant"],
                is_solved=agent_results["elephant"].get("is_solved", True),
            )

        return results

    finally:
        await bridge.close()
