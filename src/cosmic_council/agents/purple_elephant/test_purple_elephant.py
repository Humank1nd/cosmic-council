#!/usr/bin/env python3
"""
Test script to prove Purple Elephant works.

Demonstrates the three falsifiable criteria:
1. Responsibility assignment - every action has a designated executor
2. Stakeholder identification - all relevant stakeholders identified
3. Notification routing - all parties properly notified
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_dir))

from cosmic_council.agents.purple_elephant import (
    PurpleElephantEngine,
    assign_responsibilities,
    PurpleElephantConfig,
)


async def main():
    print("=" * 60)
    print("PURPLE ELEPHANT - Responsibility Test")
    print("=" * 60)
    print()

    # Located targets from Blue Dolphin (simulated)
    targets = [
        {
            "id": "target-1",
            "action_id": "backup-db",
            "action_title": "Backup database before changes",
            "category": "database",
            "risk_level": "LOW",
            "service_name": "primary-db",
            "environment": "production",
        },
        {
            "id": "target-2",
            "action_id": "scale-pool",
            "action_title": "Scale database connection pool",
            "category": "scaling",
            "risk_level": "MEDIUM",
            "service_name": "api-gateway",
            "environment": "production",
        },
        {
            "id": "target-3",
            "action_id": "restart-pods",
            "action_title": "Restart user-service pods",
            "category": "deployment",
            "risk_level": "HIGH",
            "service_name": "user-service",
            "environment": "staging",
        },
        {
            "id": "target-4",
            "action_id": "verify-health",
            "action_title": "Verify service health",
            "category": "monitoring",
            "risk_level": "LOW",
            "service_name": "health-checker",
            "environment": "production",
        },
        {
            "id": "target-5",
            "action_id": "notify-team",
            "action_title": "Notify operations team",
            "category": "notification",
            "risk_level": "NEGLIGIBLE",
            "service_name": "notification-service",
            "environment": "production",
        },
    ]

    print(f"Input: {len(targets)} located targets")
    for target in targets:
        print(f"  - {target['action_title']} ({target['category']}, {target['risk_level']})")
    print()

    # Run Purple Elephant
    engine = PurpleElephantEngine(
        config=PurpleElephantConfig(
            send_notifications=True,
            require_approver_for_high_risk=True,
            auto_assign_service_owners=True,
        ),
    )

    result = await engine.assign(
        location_plan_id="test-location-001",
        targets=targets,
        context={"team": "platform"},
    )

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms}ms")
    print()

    plan = result.responsibility_plan

    # Criterion 1: Responsibility Assignment
    print("-" * 40)
    print("CRITERION 1: Responsibility Assignment")
    print("-" * 40)
    print(f"Assignments made: {plan.assignments_made}/{len(plan.assignments)}")
    print(f"Assignment rate: {result.responsibility_assignment:.1%}")
    print()

    for assignment in plan.assignments:
        stakeholder_name = assignment.stakeholder.name if assignment.stakeholder else "UNASSIGNED"
        status = "ASSIGNED" if assignment.is_assigned else "PENDING"
        print(f"  [{status}] {assignment.action_id}")
        print(f"    Executor: {stakeholder_name}")
        print(f"    Type: {assignment.responsibility_type.value}")
        if assignment.reason:
            print(f"    Reason: {assignment.reason}")
        print()

    # Criterion 2: Stakeholder Identification
    print("-" * 40)
    print("CRITERION 2: Stakeholder Identification")
    print("-" * 40)
    print(f"Stakeholders identified: {plan.stakeholders_identified}")
    print(f"Identification rate: {result.stakeholder_identification:.1%}")
    print()

    print("Unique stakeholders:")
    for stakeholder in plan.stakeholders:
        type_tag = f" [{stakeholder.type.value}]"
        print(f"  - {stakeholder.name}{type_tag}")
        if stakeholder.team:
            print(f"    Team: {stakeholder.team}")
        if stakeholder.capabilities:
            print(f"    Capabilities: {', '.join(list(stakeholder.capabilities)[:3])}")
    print()

    # Show stakeholder analysis details
    print("Stakeholder analysis:")
    for s_result in result.stakeholder_results[:3]:
        if s_result.executor:
            print(f"  {s_result.action_id}:")
            print(f"    Executor: {s_result.executor.name}")
            if s_result.approver:
                print(f"    Approver: {s_result.approver.name}")
            if s_result.observers:
                obs_names = [o.name for o in s_result.observers[:2]]
                print(f"    Observers: {', '.join(obs_names)}")
    print()

    # Criterion 3: Notification Routing
    print("-" * 40)
    print("CRITERION 3: Notification Routing")
    print("-" * 40)
    print(f"Notifications sent: {plan.notifications_sent}")
    print(f"Routing rate: {result.notification_routing:.1%}")
    print()

    if result.notification_result:
        print(f"Channels used: {result.notification_result.total_channels_used}")
        print()

        for record in plan.notifications[:3]:
            status = "SENT" if record.is_sent else "FAILED"
            channel = record.channel.value if record.channel else "N/A"
            print(f"  [{status}] {record.action_id}")
            print(f"    Channel: {channel}")
            print(f"    Priority: {record.priority.value if record.priority else 'N/A'}")
    print()

    # Responsibility Plan Summary
    print("-" * 40)
    print("RESPONSIBILITY PLAN SUMMARY")
    print("-" * 40)
    print(f"Valid: {plan.is_valid}")
    print(f"Total assignments: {len(plan.assignments)}")
    print(f"Unique stakeholders: {plan.stakeholders_identified}")
    print(f"Notifications sent: {plan.notifications_sent}")
    print()

    if plan.validation_errors:
        print("Validation errors:")
        for error in plan.validation_errors:
            print(f"  ! {error}")
        print()

    # Criterion verification
    print("=" * 60)
    print("CRITERION VERIFICATION")
    print("=" * 60)
    print()

    c1_pass = result.responsibility_assignment >= 0.8
    c2_pass = result.stakeholder_identification >= 0.8
    c3_pass = result.notification_routing >= 0.8

    print(f"1. Responsibility assignment: {'PASS' if c1_pass else 'FAIL'}")
    print(f"   - {plan.assignments_made}/{len(plan.assignments)} assigned")
    print(f"   - {result.responsibility_assignment:.0%} assignment rate")
    print()

    print(f"2. Stakeholder identification: {'PASS' if c2_pass else 'FAIL'}")
    print(f"   - {plan.stakeholders_identified} stakeholders identified")
    print(f"   - {result.stakeholder_identification:.0%} identification rate")
    print()

    print(f"3. Notification routing: {'PASS' if c3_pass else 'FAIL'}")
    print(f"   - {plan.notifications_sent} notifications sent")
    print(f"   - {result.notification_routing:.0%} routing rate")
    print()

    all_pass = c1_pass and c2_pass and c3_pass
    print("=" * 60)
    print(f"OVERALL: {'ALL CRITERIA PASSED' if all_pass else 'SOME CRITERIA FAILED'}")
    print("=" * 60)

    # Reasoning
    if result.reasoning:
        print()
        print("Reasoning:")
        for reason in result.reasoning:
            print(f"  - {reason}")

    if result.warnings:
        print()
        print("Warnings:")
        for warning in result.warnings:
            print(f"  ! {warning}")

    return all_pass


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
