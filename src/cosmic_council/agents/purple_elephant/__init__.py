"""
PURPLE ELEPHANT - Responsibility Agent.

Purple Elephant is the PURPLE Enterprise (Level 7) in the Cosmic Council ROYGBV hierarchy.
It answers the fundamental question: WHO should execute each action?

This module implements genuine responsibility assignment with:
- Responsibility assignment (every action has an executor)
- Stakeholder identification (all relevant stakeholders)
- Notification routing (all parties properly notified)

The Three Falsifiable Criteria:
1. Responsibility assignment - every action has a designated executor
2. Stakeholder identification - all relevant stakeholders identified
3. Notification routing - all parties properly notified

Usage:
    from cosmic_council.agents.purple_elephant import PurpleElephantEngine, assign_responsibilities

    # Quick assignment
    result = await assign_responsibilities(location_plan_id, targets)
    print(result.responsibility_plan.assignments)

    # Full control
    engine = PurpleElephantEngine(
        config=PurpleElephantConfig(send_notifications=True),
    )
    result = await engine.assign(
        location_plan_id="location-123",
        targets=targets,
    )

    # As a Cosmic Council Agent
    agent = create_purple_elephant_agent()
    result = await agent.process_task(context)
"""

# Core models
from .models import (
    # Enums
    ResponsibilityType,
    StakeholderType,
    NotificationChannel,
    NotificationPriority,
    AssignmentStatus,
    # Data classes
    ContactInfo,
    Stakeholder,
    ResponsibilityAssignment,
    NotificationRecord,
    EscalationRule,
    ResponsibilityPlan,
    # Configuration
    PurpleElephantConfig,
    # Constants
    STANDARD_STAKEHOLDERS,
    DEFAULT_ESCALATION_RULES,
)

# Components
from .responsibility_resolver import (
    ResponsibilityResolver,
    AssignmentRule,
    ResolutionResult,
    BatchResolutionResult,
    create_responsibility_resolver,
)

from .stakeholder_analyzer import (
    StakeholderAnalyzer,
    StakeholderRequirement,
    StakeholderMatch,
    StakeholderAnalysisResult,
    create_stakeholder_analyzer,
)

from .notification_engine import (
    NotificationEngine,
    NotificationTemplate,
    NotificationRequest,
    NotificationResult,
    BatchNotificationResult,
    create_notification_engine,
)

# Main engine
from .engine import (
    PurpleElephantEngine,
    PurpleElephantResult,
    create_purple_elephant,
    get_purple_elephant,
    assign_responsibilities,
)

# Cosmic Council Agent Integration
from .agent import (
    PurpleElephantAgent,
    create_purple_elephant_agent,
    get_responsibility_agent,
)

__all__ = [
    # Enums
    "ResponsibilityType",
    "StakeholderType",
    "NotificationChannel",
    "NotificationPriority",
    "AssignmentStatus",
    # Core data classes
    "ContactInfo",
    "Stakeholder",
    "ResponsibilityAssignment",
    "NotificationRecord",
    "EscalationRule",
    "ResponsibilityPlan",
    # Configuration
    "PurpleElephantConfig",
    # Constants
    "STANDARD_STAKEHOLDERS",
    "DEFAULT_ESCALATION_RULES",
    # Component classes
    "ResponsibilityResolver",
    "AssignmentRule",
    "ResolutionResult",
    "BatchResolutionResult",
    "StakeholderAnalyzer",
    "StakeholderRequirement",
    "StakeholderMatch",
    "StakeholderAnalysisResult",
    "NotificationEngine",
    "NotificationTemplate",
    "NotificationRequest",
    "NotificationResult",
    "BatchNotificationResult",
    # Engine
    "PurpleElephantEngine",
    "PurpleElephantResult",
    # Factory functions
    "create_responsibility_resolver",
    "create_stakeholder_analyzer",
    "create_notification_engine",
    "create_purple_elephant",
    "get_purple_elephant",
    # Convenience functions
    "assign_responsibilities",
    # Cosmic Council Agent
    "PurpleElephantAgent",
    "create_purple_elephant_agent",
    "get_responsibility_agent",
]

__version__ = "0.1.0"
