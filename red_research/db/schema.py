"""
Legacy red_research schema compatibility shim.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CoreProblem:
    title: str
    description: str
    status: str = "draft"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ResearchFinding:
    problem_id: str
    summary: str
    evidence: Dict[str, Any]
    confidence: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class PrioritizedQuestion:
    finding_id: str
    question: str
    priority: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
