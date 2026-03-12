#!/usr/bin/env python3
"""
Test script to prove Black Snake works.

Demonstrates the three falsifiable criteria:
1. Execution completion - all assigned actions are executed
2. Outcome capture - results are properly recorded
3. Cycle recursion - insights feed back to initiate new inquiry
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_dir))

from cosmic_council.agents.black_snake import (
    BlackSnakeEngine,
    execute_and_recurse,
    BlackSnakeConfig,
    OUROBOROS_SYMBOL,
)


async def main():
    print("=" * 60)
    print("BLACK SNAKE - Execution & Recursion Test")
    print("=" * 60)
    print()
    # Skip symbol on Windows due to encoding issues
    try:
        print(OUROBOROS_SYMBOL)
    except UnicodeEncodeError:
        print("    The Ouroboros - the serpent consuming its tail.")
        print("    Each ending is a new beginning.")
    print()

    # Assignments from Purple Elephant (simulated)
    assignments = [
        {
            "id": "assign-1",
            "action_id": "backup-db",
            "action_type": "backup",
            "category": "database",
            "target_id": "target-1",
            "parameters": {"retention_days": 30},
            "environment": "production",
            "executor_id": "dba-bot",
            "executor_type": "automation",
        },
        {
            "id": "assign-2",
            "action_id": "scale-pool",
            "action_type": "scaling",
            "category": "scaling",
            "target_id": "target-2",
            "parameters": {"min_replicas": 3, "max_replicas": 10},
            "environment": "production",
            "executor_id": "autoscaler",
            "executor_type": "automation",
        },
        {
            "id": "assign-3",
            "action_id": "restart-pods",
            "action_type": "restart",
            "category": "deployment",
            "target_id": "target-3",
            "parameters": {"strategy": "rolling"},
            "environment": "staging",
            "executor_id": "k8s-operator",
            "executor_type": "automation",
        },
        {
            "id": "assign-4",
            "action_id": "verify-health",
            "action_type": "monitoring",
            "category": "monitoring",
            "target_id": "target-4",
            "parameters": {"endpoints": ["/health", "/ready"]},
            "environment": "production",
            "executor_id": "health-checker",
            "executor_type": "automation",
        },
        {
            "id": "assign-5",
            "action_id": "notify-team",
            "action_type": "notification",
            "category": "notification",
            "target_id": "target-5",
            "parameters": {"channels": ["slack", "email"]},
            "environment": "production",
            "executor_id": "notifier",
            "executor_type": "automation",
        },
    ]

    print(f"Input: {len(assignments)} assignments from Purple Elephant")
    for assign in assignments:
        print(f"  - {assign['action_id']} ({assign['action_type']})")
    print()

    # Run Black Snake
    engine = BlackSnakeEngine(
        config=BlackSnakeConfig(
            parallel_execution=True,
            capture_all_outputs=True,
            generate_insights=True,
            auto_feed_forward=False,  # Don't auto-feed for test
        ),
    )

    result = await engine.execute(
        responsibility_plan_id="test-responsibility-001",
        assignments=assignments,
        context={
            "cycle_id": "test-cycle-001",
            "inquiry_id": "test-inquiry-001",
            "root_cause": "Connection pool exhaustion",
        },
    )

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms}ms")
    print()

    plan = result.execution_plan

    # Criterion 1: Execution Completion
    print("-" * 40)
    print("CRITERION 1: Execution Completion")
    print("-" * 40)
    print(f"Actions executed: {plan.executions_completed + plan.executions_failed}/{len(plan.executions)}")
    print(f"Execution rate: {result.execution_completion:.1%}")
    print()

    for exec_result in result.execution_results:
        status = "SUCCESS" if exec_result.success else "FAILED"
        print(f"  [{status}] {exec_result.record.action_id}")
        if exec_result.output:
            for key, value in list(exec_result.output.items())[:2]:
                print(f"    {key}: {value}")
    print()

    # Criterion 2: Outcome Capture
    print("-" * 40)
    print("CRITERION 2: Outcome Capture")
    print("-" * 40)
    print(f"Outcomes captured: {result.outcome_result.total_captured}")
    print(f"Capture rate: {result.outcome_capture:.1%}")
    print(f"Surprises detected: {result.outcome_result.surprises_detected}")
    print()

    for outcome in plan.outcomes[:3]:
        print(f"  - {outcome.action_id}: {outcome.outcome_type.value}")
        print(f"    Impact: {outcome.impact_score:.2f}")
        if outcome.observations:
            print(f"    Observations: {outcome.observations[0]}")
    print()

    # Criterion 3: Cycle Recursion
    print("-" * 40)
    print("CRITERION 3: Cycle Recursion")
    print("-" * 40)
    print(f"Insights generated: {plan.insights_generated}")
    print(f"Recursion readiness: {result.cycle_recursion:.1%}")
    print()

    if result.cycle_result:
        feedback = result.cycle_result.feedback
        print(f"New questions for Red Owl: {len(feedback.new_questions)}")
        for q in feedback.new_questions[:3]:
            print(f"  ? {q}")
        print()

        print(f"Hypotheses to test: {len(feedback.hypotheses_to_test)}")
        for h in feedback.hypotheses_to_test[:2]:
            print(f"  ~ {h}")
        print()

        print(f"Should continue cycle: {feedback.should_continue}")
        print(f"Priority: {feedback.priority}")
        print(f"Urgency: {feedback.urgency}")
    print()

    # Insights detail
    if plan.insights:
        print("-" * 40)
        print("GENERATED INSIGHTS")
        print("-" * 40)
        for insight in plan.insights[:3]:
            print(f"  [{insight.insight_type.value}] {insight.title}")
            print(f"    Confidence: {insight.confidence:.1%}")
            print(f"    Priority: {insight.priority}")
        print()

    # Execution Plan Summary
    print("-" * 40)
    print("EXECUTION PLAN SUMMARY")
    print("-" * 40)
    print(f"Valid: {plan.is_valid}")
    print(f"Executions: {len(plan.executions)}")
    print(f"  - Completed: {plan.executions_completed}")
    print(f"  - Failed: {plan.executions_failed}")
    print(f"Outcomes captured: {plan.outcomes_captured}")
    print(f"Insights generated: {plan.insights_generated}")
    print()

    if plan.validation_errors:
        print("Validation errors:")
        for error in plan.validation_errors:
            print(f"  ! {error}")
        print()

    if plan.next_cycle_seed:
        print("Next cycle seed prepared:")
        print(f"  Questions: {len(plan.next_cycle_seed.get('questions', []))}")
        print(f"  Hypotheses: {len(plan.next_cycle_seed.get('hypotheses', []))}")
        print()

    # Criterion verification
    print("=" * 60)
    print("CRITERION VERIFICATION")
    print("=" * 60)
    print()

    c1_pass = result.execution_completion >= 0.8
    c2_pass = result.outcome_capture >= 0.8
    c3_pass = result.cycle_recursion >= 0.5  # Lower threshold since we didn't auto-feed

    print(f"1. Execution completion: {'PASS' if c1_pass else 'FAIL'}")
    print(f"   - {plan.executions_completed + plan.executions_failed}/{len(plan.executions)} actions executed")
    print(f"   - {result.execution_completion:.0%} execution rate")
    print()

    print(f"2. Outcome capture: {'PASS' if c2_pass else 'FAIL'}")
    print(f"   - {plan.outcomes_captured} outcomes captured")
    print(f"   - {result.outcome_capture:.0%} capture rate")
    print()

    print(f"3. Cycle recursion: {'PASS' if c3_pass else 'FAIL'}")
    print(f"   - {plan.insights_generated} insights generated")
    print(f"   - {result.cycle_recursion:.0%} recursion readiness")
    if result.cycle_result:
        print(f"   - {len(result.cycle_result.feedback.new_questions)} questions for next cycle")
    print()

    all_pass = c1_pass and c2_pass and c3_pass
    print("=" * 60)
    print(f"OVERALL: {'ALL CRITERIA PASSED' if all_pass else 'SOME CRITERIA FAILED'}")
    print("=" * 60)

    # The Ouroboros completes
    if all_pass:
        print()
        print("The Ouroboros completes its cycle.")
        print("Each ending is a new beginning.")
        print("Black Snake feeds wisdom back to Red Owl.")

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
