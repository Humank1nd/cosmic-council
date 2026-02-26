#!/usr/bin/env python3
"""
Test script to prove Blue Dolphin works.

Demonstrates the three falsifiable criteria:
1. Location resolution - every action has a specific execution target
2. Environment matching - actions matched to appropriate environments
3. Connectivity validation - all targets are reachable
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_dir))

from cosmic_council.agents.blue_dolphin import (
    BlueDolphinEngine,
    locate_execution,
    BlueDolphinConfig,
)


async def main():
    print("=" * 60)
    print("BLUE DOLPHIN - Location Test")
    print("=" * 60)
    print()

    # Scheduled slots from Green Turtle (simulated)
    slots = [
        {
            "id": "slot-1",
            "action_id": "backup-db",
            "action_title": "Backup database before changes",
            "category": "database",
            "risk_level": "LOW",
        },
        {
            "id": "slot-2",
            "action_id": "scale-pool",
            "action_title": "Scale database connection pool",
            "category": "scaling",
            "risk_level": "MEDIUM",
        },
        {
            "id": "slot-3",
            "action_id": "restart-pods",
            "action_title": "Restart user-service pods",
            "category": "deployment",
            "risk_level": "HIGH",
        },
        {
            "id": "slot-4",
            "action_id": "verify-health",
            "action_title": "Verify service health",
            "category": "monitoring",
            "risk_level": "LOW",
        },
        {
            "id": "slot-5",
            "action_id": "notify-team",
            "action_title": "Notify operations team",
            "category": "notification",
            "risk_level": "NEGLIGIBLE",
        },
    ]

    print(f"Input: {len(slots)} scheduled slots")
    for slot in slots:
        print(f"  - {slot['action_title']} ({slot['category']}, {slot['risk_level']})")
    print()

    # Run Blue Dolphin
    engine = BlueDolphinEngine(
        config=BlueDolphinConfig(
            require_connectivity_check=True,
            fallback_enabled=True,
            prefer_same_region=True,
        ),
    )

    result = await engine.locate(
        schedule_id="test-schedule-001",
        slots=slots,
        context={"team": "platform"},
    )

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms}ms")
    print()

    plan = result.location_plan

    # Criterion 1: Location Resolution
    print("-" * 40)
    print("CRITERION 1: Location Resolution")
    print("-" * 40)
    print(f"Targets resolved: {plan.targets_resolved}/{len(plan.targets)}")
    print(f"Resolution rate: {result.location_resolution:.1%}")
    print()

    for target in plan.targets:
        loc_name = target.location.name if target.location else "UNRESOLVED"
        status = "RESOLVED" if target.is_resolved else "UNRESOLVED"
        print(f"  [{status}] {target.action_id}")
        print(f"    Location: {loc_name}")
        print(f"    Namespace: {target.namespace}")
        print()

    # Criterion 2: Environment Matching
    print("-" * 40)
    print("CRITERION 2: Environment Matching")
    print("-" * 40)
    print(f"Environments matched: {len(plan.environments)}")
    print(f"Matching rate: {result.environment_matching:.1%}")
    print()

    for env in plan.environments:
        prod_tag = " [PRODUCTION]" if env.is_production else ""
        print(f"  - {env.name} ({env.type.value}){prod_tag}")
    print()

    # Show environment analysis details
    print("Environment analysis:")
    for env_result in result.environment_results[:3]:
        if env_result.recommended_environment:
            print(f"  {env_result.action_id} -> {env_result.recommended_environment.name}")
            for reason in env_result.reasoning[:2]:
                print(f"    {reason}")
    print()

    # Criterion 3: Connectivity Validation
    print("-" * 40)
    print("CRITERION 3: Connectivity Validation")
    print("-" * 40)
    print(f"Targets reachable: {plan.targets_reachable}/{len(plan.targets)}")
    print(f"Targets unreachable: {plan.targets_unreachable}")
    print(f"Validation rate: {result.connectivity_validation:.1%}")
    print()

    if result.routing_result:
        for decision in result.routing_result.decisions[:3]:
            status = "REACHABLE" if decision.connectivity_verified else "UNREACHABLE"
            loc = decision.primary_location.name if decision.primary_location else "N/A"
            print(f"  [{status}] {decision.action_id}")
            print(f"    Primary: {loc}")
            if decision.fallback_location:
                print(f"    Fallback: {decision.fallback_location.name}")
            print(f"    Path: {' -> '.join(decision.routing_path)}")
    print()

    # Location Plan Summary
    print("-" * 40)
    print("LOCATION PLAN SUMMARY")
    print("-" * 40)
    print(f"Valid: {plan.is_valid}")
    print(f"Locations used: {len(plan.locations)}")
    for loc in plan.locations:
        region = loc.region or "local"
        print(f"  - {loc.name} ({region})")
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

    c1_pass = result.location_resolution >= 0.8
    c2_pass = result.environment_matching >= 0.8
    c3_pass = result.connectivity_validation >= 0.8

    print(f"1. Location resolution: {'PASS' if c1_pass else 'FAIL'}")
    print(f"   - {plan.targets_resolved}/{len(plan.targets)} targets resolved")
    print(f"   - {result.location_resolution:.0%} resolution rate")
    print()

    print(f"2. Environment matching: {'PASS' if c2_pass else 'FAIL'}")
    print(f"   - {len(plan.environments)} environments used")
    print(f"   - {result.environment_matching:.0%} matching rate")
    print()

    print(f"3. Connectivity validation: {'PASS' if c3_pass else 'FAIL'}")
    print(f"   - {plan.targets_reachable}/{len(plan.targets)} reachable")
    print(f"   - {result.connectivity_validation:.0%} validation rate")
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
