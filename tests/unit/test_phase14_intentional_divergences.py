"""
Regression tests that lock intentional divergences from the mirror.
"""

from __future__ import annotations

from sqlalchemy import JSON, Column, String
from sqlalchemy.sql.schema import MetaData

from src.cosmic_council.agents.agent_registry_36 import AgentRole, BaseTotemAgent
from src.cosmic_council.agents.hierarchical_enterprise import AgentSpecialization
from src.cosmic_council.core.types import ProblemComplexity, ProblemDomain, ProblemStatement
from src.database.models.base import BaseModel


class _TestBaseModel(BaseModel):
    __tablename__ = "phase14_test_base_model"

    name = Column(String(50), nullable=False)
    details = Column(JSON, default=dict)


def test_agent_registry_keeps_process_mapper_mapping() -> None:
    assert not hasattr(AgentRole, "TASK_DECOMPOSER")
    specialization = BaseTotemAgent._map_role_to_specialization(None, AgentRole.PROCESS_MAPPER)
    assert specialization == AgentSpecialization.TASK_DECOMPOSER


def test_problem_statement_normalizes_enum_domain_to_string() -> None:
    from_string = ProblemStatement(
        title="t",
        description="d",
        complexity=ProblemComplexity.SIMPLE,
        domain="business",
    )
    from_enum = ProblemStatement(
        title="t2",
        description="d2",
        complexity=ProblemComplexity.SIMPLE,
        domain=ProblemDomain.BUSINESS,
    )

    assert isinstance(from_string.domain, str)
    assert isinstance(from_enum.domain, str)
    assert from_string.domain == "business"
    assert from_enum.domain == "business"


def test_base_model_preserves_metadata_roundtrip_without_collision() -> None:
    row = _TestBaseModel(name="example")
    row.update_from_dict({"metadata": {"source": "test"}, "details": {"ok": True}})

    payload = row.to_dict()

    assert isinstance(_TestBaseModel.metadata, MetaData)
    assert row.extra_data == {"source": "test"}
    assert payload["metadata"] == {"source": "test"}
    assert payload["details"] == {"ok": True}
