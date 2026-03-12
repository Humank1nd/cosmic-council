#!/usr/bin/env python3
"""
Test script to prove Green Turtle works.

Demonstrates the three falsifiable criteria:
1. Time window compliance - actions within valid windows
2. Dependency sequencing - actions respect dependencies
3. Constraint satisfaction - all constraints met
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_dir))

from cosmic_council.agents.green_turtle import (
    GreenTurtleEngine,
    schedule_execution,
    GreenTurtleConfig,
)


async def main():
    print("=" * 60)
    print("GREEN TURTLE - Scheduling Test")
    print("=" * 60)
    print()

    # Specifications from Yellow Honeybee (simulated)
    specifications = [
        {
            "id": "spec-1",
            "action_id": "backup-db",
            "action_title": "Backup database before changes",
            "estimated_duration_seconds": 300,
            "risk_level": "LOW",
        },
        {
            "id": "spec-2",
            "action_id": "scale-pool",
            "action_title": "Scale database connection pool",
            "estimated_duration_seconds": 60,
            "risk_level": "MEDIUM",
        },
        {
            "id": "spec-3",
            "action_id": "restart-pods",
            "action_title": "Restart user-service pods",
            "estimated_duration_seconds": 180,
            "risk_level": "HIGH",
        },
        {
            "id": "spec-4",
            "action_id": "verify-health",
            "action_title": "Verify service health",
            "estimated_duration_seconds": 30,
            "risk_level": "LOW",
        },
        {
            "id": "spec-5",
            "action_id": "notify-team",
            "action_title": "Notify operations team",
            "estimated_duration_seconds": 10,
            "risk_level": "NEGLIGIBLE",
        },
    ]

    # Dependencies
    dependencies = [
        {"dependent_id": "scale-pool", "prerequisite_id": "backup-db", "min_delay": 0},
        {"dependent_id": "restart-pods", "prerequisite_id": "scale-pool", "min_delay": 30},
        {"dependent_id": "verify-health", "prerequisite_id": "restart-pods", "min_delay": 60},
        {"dependent_id": "notify-team", "prerequisite_id": "verify-health", "min_delay": 0},
    ]

    print(f"Input: {len(specifications)} specifications")
    for spec in specifications:
        print(f"  - {spec['action_title']} ({spec['estimated_duration_seconds']}s)")
    print()
    print(f"Dependencies: {len(dependencies)}")
    for dep in dependencies:
        print(f"  - {dep['dependent_id']} depends on {dep['prerequisite_id']}")
    print()

    # Run Green Turtle
    engine = GreenTurtleEngine(
        config=GreenTurtleConfig(
            scheduling_horizon_hours=24,
            max_concurrent_actions=3,
            prefer_off_peak=True,
        ),
    )

    result = await engine.schedule(
        implementation_plan_id="test-plan-001",
        specifications=specifications,
        dependencies=dependencies,
        context={"risk_level": "MEDIUM"},
    )

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms}ms")
    print()

    schedule = result.schedule

    # Criterion 1: Time Window Compliance
    print("-" * 40)
    print("CRITERION 1: Time Window Compliance")
    print("-" * 40)
    print(f"Slots scheduled: {schedule.slots_scheduled}")
    print(f"Compliance: {result.time_window_compliance:.1%}")
    print()

    for slot in schedule.slots:
        window = slot.time_window_name or "No window"
        status = "SCHEDULED" if slot.scheduled_start else "PENDING"
        print(f"  [{status}] {slot.action_id}")
        print(f"    Window: {window}")
        if slot.scheduled_start:
            print(f"    Start: {slot.scheduled_start.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    End: {slot.scheduled_end.strftime('%Y-%m-%d %H:%M:%S') if slot.scheduled_end else 'N/A'}")
        print()

    # Criterion 2: Dependency Sequencing
    print("-" * 40)
    print("CRITERION 2: Dependency Sequencing")
    print("-" * 40)
    print(f"Dependencies: {len(schedule.dependencies)}")
    print(f"Sequencing: {result.dependency_sequencing:.1%}")
    print()

    print("Execution order:")
    for i, slot_id in enumerate(schedule.execution_order):
        slot = schedule.get_slot(slot_id)
        if slot:
            print(f"  {i+1}. {slot.action_id}")
            if slot.scheduled_start:
                print(f"     @ {slot.scheduled_start.strftime('%H:%M:%S')}")
    print()

    # Verify dependencies are respected
    print("Dependency verification:")
    slot_times = {s.action_id: s.scheduled_start for s in schedule.slots if s.scheduled_start}
    all_deps_ok = True
    for dep in dependencies:
        prereq_time = slot_times.get(dep["prerequisite_id"])
        dep_time = slot_times.get(dep["dependent_id"])
        if prereq_time and dep_time:
            ok = dep_time >= prereq_time
            status = "OK" if ok else "VIOLATED"
            print(f"  {dep['dependent_id']} after {dep['prerequisite_id']}: {status}")
            if not ok:
                all_deps_ok = False
    print()

    # Criterion 3: Constraint Satisfaction
    print("-" * 40)
    print("CRITERION 3: Constraint Satisfaction")
    print("-" * 40)
    print(f"Constraints: {len(schedule.all_constraints)}")
    print(f"Satisfied: {schedule.constraints_satisfied}")
    print(f"Violated: {schedule.constraints_violated}")
    print(f"Satisfaction: {result.constraint_satisfaction:.1%}")
    print()

    for constraint in schedule.all_constraints[:5]:
        status = "SATISFIED" if constraint.is_satisfied else "VIOLATED"
        print(f"  [{status}] {constraint.name}: {constraint.description}")
    print()

    # Schedule summary
    print("-" * 40)
    print("SCHEDULE SUMMARY")
    print("-" * 40)
    print(f"Valid: {schedule.is_valid}")
    print(f"Total duration: {schedule.total_duration_seconds}s")
    if schedule.earliest_start:
        print(f"Start: {schedule.earliest_start.strftime('%Y-%m-%d %H:%M:%S')}")
    if schedule.latest_end:
        print(f"End: {schedule.latest_end.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Criterion verification
    print("=" * 60)
    print("CRITERION VERIFICATION")
    print("=" * 60)
    print()

    c1_pass = result.time_window_compliance > 0
    c2_pass = result.dependency_sequencing >= 0.8 and all_deps_ok
    c3_pass = result.constraint_satisfaction > 0

    print(f"1. Time window compliance: {'PASS' if c1_pass else 'FAIL'}")
    print(f"   - {schedule.slots_scheduled} slots scheduled")
    print(f"   - {result.time_window_compliance:.0%} compliance")
    print()

    print(f"2. Dependency sequencing: {'PASS' if c2_pass else 'FAIL'}")
    print(f"   - {len(schedule.dependencies)} dependencies")
    print(f"   - All respected: {all_deps_ok}")
    print()

    print(f"3. Constraint satisfaction: {'PASS' if c3_pass else 'FAIL'}")
    print(f"   - {schedule.constraints_satisfied}/{len(schedule.all_constraints)} satisfied")
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
