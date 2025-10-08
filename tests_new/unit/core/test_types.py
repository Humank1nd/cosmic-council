"""
Unit tests for core types and enums.
"""

import pytest
from src.core.types import (
    EnterpriseType, ProblemComplexity, CycleStatus, CosmicCouncilRule
)


class TestEnterpriseType:
    """Test EnterpriseType enum."""
    
    def test_enterprise_type_values(self):
        """Test enterprise type enum values."""
        assert EnterpriseType.RED_OWL == "red_owl"
        assert EnterpriseType.ORANGE_ORANGUTAN == "orange_orangutan"
        assert EnterpriseType.YELLOW_HONEYBEE == "yellow_honeybee"
        assert EnterpriseType.GREEN_TORTOISE == "green_tortoise"
        assert EnterpriseType.BLUE_DOLPHIN == "blue_dolphin"
        assert EnterpriseType.PURPLE_ELEPHANT == "purple_elephant"


class TestProblemComplexity:
    """Test ProblemComplexity enum."""
    
    def test_problem_complexity_values(self):
        """Test problem complexity enum values."""
        assert ProblemComplexity.SIMPLE == "simple"
        assert ProblemComplexity.MODERATE == "moderate"
        assert ProblemComplexity.COMPLEX == "complex"
        assert ProblemComplexity.SYSTEMIC == "systemic"


class TestCycleStatus:
    """Test CycleStatus enum."""
    
    def test_cycle_status_values(self):
        """Test cycle status enum values."""
        assert CycleStatus.PENDING == "pending"
        assert CycleStatus.RUNNING == "running"
        assert CycleStatus.COMPLETED == "completed"
        assert CycleStatus.FAILED == "failed"
        assert CycleStatus.PAUSED == "paused"


class TestCosmicCouncilRule:
    """Test CosmicCouncilRule enum."""
    
    def test_cosmic_council_rule_values(self):
        """Test cosmic council rule enum values."""
        assert CosmicCouncilRule.ROYGBV_WORKFLOW == "roygbv_workflow"
        assert CosmicCouncilRule.PERPETUAL_THINKING == "perpetual_thinking"
        assert CosmicCouncilRule.FRACTAL_RECURSION == "fractal_recursion"
