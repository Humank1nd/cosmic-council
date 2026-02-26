"""
Legacy Red Research service compatibility shim.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List


class _DefaultDBManager:
    async def execute_query(self, _query: str, *_args, **_kwargs):
        return [{"id": str(uuid.uuid4())}]

    async def execute_command(self, _query: str, *_args, **_kwargs):
        return "OK"


def get_database_manager():
    return _DefaultDBManager()


class RedResearchService:
    async def create_core_problem(self, title: str, description: str, objective_ref: str) -> Dict[str, Any]:
        db = get_database_manager()
        rows = await db.execute_query("INSERT_CORE_PROBLEM", title, description, objective_ref)
        return rows[0] if rows else {"id": str(uuid.uuid4())}

    async def create_research_finding(
        self, problem_id: str, summary: str, evidence: Dict[str, Any], confidence: float
    ) -> Dict[str, Any]:
        db = get_database_manager()
        rows = await db.execute_query("INSERT_RESEARCH_FINDING", problem_id, summary, evidence, confidence)
        return rows[0] if rows else {"id": str(uuid.uuid4())}

    async def prioritize_questions(self, finding_id: str, questions: List[str]) -> List[Dict[str, Any]]:
        db = get_database_manager()
        rows = await db.execute_query("INSERT_QUESTIONS", finding_id, questions)
        if rows:
            return rows
        return [{"id": str(uuid.uuid4()), "question": q, "priority": i + 1} for i, q in enumerate(questions)]

    async def process_research_workflow(
        self, title: str, description: str, objective_ref: str
    ) -> Dict[str, Any]:
        problem = await self.create_core_problem(title=title, description=description, objective_ref=objective_ref)
        finding = await self.create_research_finding(
            problem_id=problem["id"],
            summary=f"Finding for {title}",
            evidence={"source": "compatibility-shim"},
            confidence=0.8,
        )
        questions = await self.prioritize_questions(
            finding_id=finding["id"],
            questions=["What is the root cause?", "Who are stakeholders?", "What are constraints?"],
        )
        return {"problem_id": problem["id"], "findings": [finding], "questions": questions}

    async def get_prioritized_questions_for_handoff(self) -> List[Dict[str, Any]]:
        db = get_database_manager()
        rows = await db.execute_query("SELECT_PRIORITIZED_QUESTIONS")
        return [r for r in rows if int(r.get("priority", 0)) >= 7]

    async def complete_cycle(self, cycle_id: str) -> bool:
        db = get_database_manager()
        result = await db.execute_command("UPDATE_CYCLE_COMPLETE", cycle_id)
        return bool(result)
