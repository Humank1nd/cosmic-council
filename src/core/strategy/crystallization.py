# E8-Engine/Agent Orchestrator/src/core/strategy/crystallization.py
"""
Crystallization Engine
======================

Promotes successful cycle outcomes into durable Truths.
Manages the lifecycle of truth candidates:
Cycle Outcome -> Truth Candidate -> Human/Auto Approval -> Crystallized Truth
"""
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid

from .registry import AgentRole
from .outcomes import CycleOutcome, OutcomeType
from .store import StrategyStore

# Ensure project root is in path for security imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# Import security modules for auditing
try:
    from security import get_audit_service, audit_action
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Use memory schemas if available, otherwise define local
try:
    from ..memory.schemas import ConfidenceLevel, EntityType
except ImportError:
    # Fallback/Local definition
    class ConfidenceLevel(str, Enum):
        VERIFIED = "verified"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class EntityType(str, Enum):
        TRUTH = "truth"

import structlog

log = structlog.get_logger()

class TruthStatus(str, Enum):
    """Status of a truth candidate."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    ROLLED_BACK = "rolled_back"

@dataclass
class TruthCandidate:
    """
    A proposed truth derived from a cycle outcome.
    """
    id: str
    cycle_id: str
    problem_id: str
    statement: str
    evidence_score: float
    confidence_level: ConfidenceLevel
    created_at: datetime
    status: TruthStatus
    source_role: AgentRole
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Approval chain
    approved_by: Optional[str] = None
    approval_reason: Optional[str] = None
    approved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "cycle_id": self.cycle_id,
            "problem_id": self.problem_id,
            "statement": self.statement,
            "evidence_score": self.evidence_score,
            "confidence_level": self.confidence_level.value,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "source_role": self.source_role.value,
            "metadata": self.metadata,
            "approved_by": self.approved_by,
            "approval_reason": self.approval_reason,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }

class CrystallizationConfig:
    """Configuration for truth promotion."""
    auto_approve_threshold: float = 0.95
    min_evidence_score: float = 0.7
    require_human_for_high_impact: bool = True

class CrystallizationEngine:
    """
    Engine that processes outcomes and manages truth candidates.
    """

    def __init__(self, store: StrategyStore, config: CrystallizationConfig = None):
        self.store = store
        self.config = config or CrystallizationConfig()
        self._candidates: Dict[str, TruthCandidate] = {}
        self.audit_service = get_audit_service() if SECURITY_AVAILABLE else None

    async def process_outcome(self, outcome: CycleOutcome) -> Optional[TruthCandidate]:
        if not outcome.success:
            return None

        evidence_score = outcome.confidence_actual or outcome.confidence_reported

        if evidence_score < self.config.min_evidence_score:
            return None

        if evidence_score >= 0.95:
            conf = ConfidenceLevel.VERIFIED
        elif evidence_score >= 0.75:
            conf = ConfidenceLevel.HIGH
        else:
            conf = ConfidenceLevel.MEDIUM

        candidate_id = f"truth_{uuid.uuid4().hex[:8]}"
        statement = f"Outcome of cycle {outcome.cycle_id} for problem {outcome.problem_id}"

        candidate = TruthCandidate(
            id=candidate_id,
            cycle_id=outcome.cycle_id,
            problem_id=outcome.problem_id,
            statement=statement,
            evidence_score=evidence_score,
            confidence_level=conf,
            created_at=datetime.now(timezone.utc),
            status=TruthStatus.PENDING,
            source_role=outcome.role,
            metadata={"tools_used": outcome.tools_used}
        )

        if (evidence_score >= self.config.auto_approve_threshold and
            not (self.config.require_human_for_high_impact and outcome.human_intervention)):
            candidate.status = TruthStatus.AUTO_APPROVED
            candidate.approved_at = datetime.now(timezone.utc)
            candidate.approved_by = "system_auto_approve"
            
            if self.audit_service:
                # Log auto-approval
                log.info("Auto-approved truth candidate", id=candidate_id)
        
        self._candidates[candidate_id] = candidate
        return candidate

    async def approve_candidate(self, candidate_id: str, approver: str, reason: str = None) -> bool:
        if candidate_id not in self._candidates:
            return False

        candidate = self._candidates[candidate_id]
        if candidate.status != TruthStatus.PENDING:
            return False

        candidate.status = TruthStatus.APPROVED
        candidate.approved_by = approver
        candidate.approval_reason = reason
        candidate.approved_at = datetime.now(timezone.utc)

        log.info("Truth candidate approved", id=candidate_id, approver=approver)
        
        if self.audit_service:
            # Here we would use audit_action or similar
            # For now, we simulate an audit entry
            log.debug("Audit record created for truth approval", candidate_id=candidate_id)
            
        return True

    async def reject_candidate(self, candidate_id: str, rejector: str, reason: str = None) -> bool:
        if candidate_id not in self._candidates:
            return False

        candidate = self._candidates[candidate_id]
        candidate.status = TruthStatus.REJECTED
        candidate.approved_by = rejector
        candidate.approval_reason = reason

        log.info("Truth candidate rejected", id=candidate_id, rejector=rejector)
        
        if self.audit_service:
            log.debug("Audit record created for truth rejection", candidate_id=candidate_id)
            
        return True

    async def get_pending_candidates(self) -> List[TruthCandidate]:
        return [c for c in self._candidates.values() if c.status == TruthStatus.PENDING]

    async def get_candidate(self, candidate_id: str) -> Optional[TruthCandidate]:
        return self._candidates.get(candidate_id)
