"""Cosmic Council - The six enterprises working together."""
import asyncio
import logging
from typing import Dict, List, Any, Optional
import httpx

from .models import (
    Enterprise, ENTERPRISE_INFO, Problem, EnterpriseResponse,
    CycleResult, Solution
)

logger = logging.getLogger("CosmicCouncil")


class CosmicCouncil:
    """
    The Cosmic Council - Six enterprises solving problems together.

    Flow: Red -> Orange -> Yellow -> Green -> Blue -> Purple -> Synthesis

    Each enterprise asks a fundamental question:
    - Red Owl: WHY? (Research & Knowledge)
    - Orange Orangutan: HOW? (Logistics & Planning)
    - Yellow Honeybee: WHAT? (Prototyping & Development)
    - Green Tortoise: WHEN? (Resources & Timing)
    - Blue Dolphin: WHERE? (Communication & Distribution)
    - Purple Elephant: WHO? (Empathy & Stakeholders)
    """

    def __init__(self, supra_gptr_url: str = "http://localhost:8005"):
        self.supra_gptr_url = supra_gptr_url
        self.problems: Dict[str, Problem] = {}
        self.cycles: Dict[str, CycleResult] = {}
        self.solutions: Dict[str, Solution] = {}
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        await self.client.aclose()

    async def _call_llm(self, messages: List[Dict], boost_profile: str = "sport") -> str:
        """Call Supra GPTR for LLM response."""
        try:
            response = await self.client.post(
                f"{self.supra_gptr_url}/v1/chat/completions",
                json={
                    "messages": messages,
                    "boost_profile": boost_profile,
                    "firebase_project": "dreamcaesar1"  # Use DreamCaesar for creative work
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                logger.warning(f"LLM call failed: {response.status_code}")
                return self._generate_mock_response()
        except Exception as e:
            logger.warning(f"LLM call error: {e}, using mock response")
            return self._generate_mock_response()

    def _generate_mock_response(self) -> str:
        """Generate mock response when LLM is unavailable."""
        return "Analysis pending - LLM service unavailable. Please retry."

    async def create_problem(self, title: str, description: str, context: Dict = None) -> Problem:
        """Create a new problem for the council to solve."""
        problem = Problem(
            title=title,
            description=description,
            context=context or {}
        )
        self.problems[problem.id] = problem
        logger.info(f"Created problem {problem.id}: {title}")
        return problem

    async def run_enterprise(
        self,
        enterprise: Enterprise,
        problem: Problem,
        previous_responses: List[EnterpriseResponse] = None
    ) -> EnterpriseResponse:
        """Run a single enterprise's analysis."""
        info = ENTERPRISE_INFO[enterprise]
        previous_responses = previous_responses or []

        # Build context from previous responses
        context_text = ""
        if previous_responses:
            context_text = "\n\nPrevious enterprise analyses:\n"
            for resp in previous_responses:
                ent_info = ENTERPRISE_INFO[resp.enterprise]
                context_text += f"\n{ent_info['name']} ({resp.question}):\n{resp.analysis}\n"

        prompt = f"""You are the {info['name']}, part of the Cosmic Council.

Your role: {info['role']}
Your guiding principle: {info['principle']}
Your core question: {info['question']}?

PROBLEM TO ANALYZE:
Title: {problem.title}
Description: {problem.description}
{f"Context: {problem.context}" if problem.context else ""}
{context_text}

As the {info['name']}, analyze this problem through your unique lens.
Focus on answering: {info['question']} should we approach this?

Provide:
1. Your analysis (2-3 paragraphs)
2. 3-5 specific recommendations
3. Your confidence level (0-100%)

Format your response as:
ANALYSIS:
[Your analysis]

RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
- [etc.]

CONFIDENCE: [X]%"""

        messages = [
            {"role": "system", "content": f"You are {info['name']}, the {info['animal']} of the Cosmic Council."},
            {"role": "user", "content": prompt}
        ]

        response_text = await self._call_llm(messages)

        # Parse response
        analysis = ""
        recommendations = []
        confidence = 0.7

        if "ANALYSIS:" in response_text:
            parts = response_text.split("ANALYSIS:", 1)[1]
            if "RECOMMENDATIONS:" in parts:
                analysis = parts.split("RECOMMENDATIONS:")[0].strip()
                rec_part = parts.split("RECOMMENDATIONS:")[1]
                if "CONFIDENCE:" in rec_part:
                    rec_text = rec_part.split("CONFIDENCE:")[0]
                    conf_text = rec_part.split("CONFIDENCE:")[1].strip()
                    try:
                        confidence = float(conf_text.replace("%", "").strip()) / 100
                    except:
                        pass
                else:
                    rec_text = rec_part

                for line in rec_text.strip().split("\n"):
                    line = line.strip()
                    if line.startswith("-"):
                        recommendations.append(line[1:].strip())
        else:
            analysis = response_text

        return EnterpriseResponse(
            enterprise=enterprise,
            question=info['question'],
            analysis=analysis or response_text,
            recommendations=recommendations or ["Further analysis needed"],
            confidence=confidence,
            metadata={"enterprise_info": info}
        )

    async def run_cycle(self, problem_id: str) -> CycleResult:
        """Run a full ROYGBV cycle on a problem."""
        if problem_id not in self.problems:
            raise ValueError(f"Problem {problem_id} not found")

        problem = self.problems[problem_id]
        problem.status = "in_cycle"

        cycle = CycleResult(problem_id=problem_id)
        self.cycles[cycle.id] = cycle

        # Run through all enterprises in order
        enterprise_order = [
            Enterprise.RED_OWL,
            Enterprise.ORANGE_ORANGUTAN,
            Enterprise.YELLOW_HONEYBEE,
            Enterprise.GREEN_TORTOISE,
            Enterprise.BLUE_DOLPHIN,
            Enterprise.PURPLE_ELEPHANT
        ]

        responses = []
        for enterprise in enterprise_order:
            logger.info(f"Running {ENTERPRISE_INFO[enterprise]['name']} analysis...")
            response = await self.run_enterprise(enterprise, problem, responses)
            responses.append(response)
            cycle.responses = responses

        # Synthesize final response
        cycle.synthesis = await self._synthesize(problem, responses)
        cycle.action_items = self._extract_action_items(responses)
        cycle.completed_at = asyncio.get_event_loop().time()
        cycle.status = "completed"

        # Create solution
        solution = Solution(
            problem_id=problem_id,
            cycle_id=cycle.id,
            title=f"Solution for: {problem.title}",
            description=cycle.synthesis,
            action_items=cycle.action_items,
            confidence=sum(r.confidence for r in responses) / len(responses)
        )
        self.solutions[solution.id] = solution

        problem.status = "resolved"
        logger.info(f"Cycle {cycle.id} completed for problem {problem_id}")

        return cycle

    async def _synthesize(self, problem: Problem, responses: List[EnterpriseResponse]) -> str:
        """Synthesize all enterprise responses into a unified solution."""
        summary = "Enterprise Analyses Summary:\n\n"
        for resp in responses:
            info = ENTERPRISE_INFO[resp.enterprise]
            summary += f"{info['name']} ({resp.question}):\n{resp.analysis[:500]}...\n\n"

        prompt = f"""As the Cosmic Council Synthesizer, combine the wisdom of all six enterprises.

PROBLEM: {problem.title}
{problem.description}

{summary}

Create a unified synthesis that:
1. Integrates insights from all six perspectives
2. Resolves any contradictions
3. Provides a clear path forward
4. Lists concrete next steps

Keep the synthesis concise but comprehensive (3-4 paragraphs)."""

        messages = [
            {"role": "system", "content": "You are the Cosmic Council Synthesizer, unifying the wisdom of all six enterprises."},
            {"role": "user", "content": prompt}
        ]

        return await self._call_llm(messages, boost_profile="sport+")

    def _extract_action_items(self, responses: List[EnterpriseResponse]) -> List[str]:
        """Extract action items from all responses."""
        items = []
        for resp in responses:
            info = ENTERPRISE_INFO[resp.enterprise]
            for rec in resp.recommendations[:2]:  # Top 2 from each
                items.append(f"[{info['name']}] {rec}")
        return items

    def get_problem(self, problem_id: str) -> Optional[Problem]:
        return self.problems.get(problem_id)

    def get_cycle(self, cycle_id: str) -> Optional[CycleResult]:
        return self.cycles.get(cycle_id)

    def get_solutions(self, problem_id: str = None) -> List[Solution]:
        if problem_id:
            return [s for s in self.solutions.values() if s.problem_id == problem_id]
        return list(self.solutions.values())

    def list_problems(self) -> List[Problem]:
        return list(self.problems.values())

    def list_cycles(self) -> List[CycleResult]:
        return list(self.cycles.values())


# Singleton instance
council = CosmicCouncil()
