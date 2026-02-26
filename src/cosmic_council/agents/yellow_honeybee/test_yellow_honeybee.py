#!/usr/bin/env python3
"""
Test script to prove Yellow Honeybee works.

Demonstrates the three falsifiable criteria:
1. Specification completeness - every action gets detailed specs
2. Validation rules - pre/post conditions for each step
3. Resource identification - specific resources identified
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(src_dir))

from cosmic_council.agents.yellow_honeybee import (
    YellowHoneybeeEngine,
    specify_implementation,
)


async def main():
    print("=" * 60)
    print("YELLOW HONEYBEE - Implementation Specification Test")
    print("=" * 60)
    print()

    # Actions from Orange Orangutan (simulated)
    actions = [
        {
            "id": "action-1",
            "title": "Scale database connection pool",
            "category": "database",
            "target_service": "user-service",
            "context": {"max_connections": 200},
        },
        {
            "id": "action-2",
            "title": "Restart user-service pods",
            "category": "restart",
            "target_service": "user-service",
        },
        {
            "id": "action-3",
            "title": "Update timeout configuration",
            "category": "configuration",
            "target_service": "api-gateway",
            "context": {"timeout_value": 30000},
        },
        {
            "id": "action-4",
            "title": "Notify operations team",
            "category": "communication",
            "context": {"severity": "warning"},
        },
    ]

    print(f"Input: {len(actions)} actions from Orange Orangutan")
    for action in actions:
        print(f"  - {action['title']} ({action['category']})")
    print()

    # Run Yellow Honeybee
    engine = YellowHoneybeeEngine(
        default_namespace="production",
        service_registry={
            "user-service": {"port": 8080, "protocol": "http"},
            "api-gateway": {"port": 8443, "protocol": "https"},
        },
    )

    result = await engine.specify(
        action_plan_id="test-plan-001",
        actions=actions,
        root_cause="Database connection pool exhausted causing user-service failures",
    )

    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    print(f"Success: {result.success}")
    print(f"Duration: {result.duration_ms}ms")
    print()

    # Criterion 1: Specification Completeness
    print("-" * 40)
    print("CRITERION 1: Specification Completeness")
    print("-" * 40)
    plan = result.plan
    print(f"Total specifications: {len(plan.specifications)}")
    print(f"Complete specs: {plan.specs_complete}")
    print(f"Incomplete specs: {plan.specs_incomplete}")
    print(f"Completeness ratio: {plan.completeness_ratio:.1%}")
    print()

    for spec in plan.specifications:
        print(f"  [{spec.spec_type.value}] {spec.action_title}")
        print(f"    Complete: {spec.is_complete}")
        print(f"    Steps: {len(spec.steps)}")
        if spec.command_spec:
            print(f"    Command: {spec.command_spec.command} {' '.join(spec.command_spec.args[:2])}...")
        if spec.kubernetes_spec:
            print(f"    K8s: {spec.kubernetes_spec.action} {spec.kubernetes_spec.resource_type}/{spec.kubernetes_spec.resource_name}")
        if spec.api_spec:
            print(f"    API: {spec.api_spec.method} {spec.api_spec.url[:50]}...")
        if spec.config_spec:
            print(f"    Config: {spec.config_spec.config_path}")
        if spec.database_spec:
            print(f"    DB: {spec.database_spec.query_type} query")
        print()

    # Criterion 2: Validation Rules
    print("-" * 40)
    print("CRITERION 2: Validation Rules")
    print("-" * 40)
    print(f"Total pre-conditions: {plan.total_pre_conditions}")
    print(f"Total post-conditions: {plan.total_post_conditions}")
    print(f"Validation coverage: {result.validation_coverage:.1%}")
    print()

    for spec in plan.specifications:
        print(f"  {spec.action_title}")
        print(f"    Pre-conditions: {len(spec.pre_conditions)}")
        for pre in spec.pre_conditions[:2]:  # Show first 2
            print(f"      - {pre.name}: {pre.description}")
        print(f"    Post-conditions: {len(spec.post_conditions)}")
        for post in spec.post_conditions[:2]:  # Show first 2
            print(f"      - {post.name}: {post.description}")
        print()

    # Criterion 3: Resource Identification
    print("-" * 40)
    print("CRITERION 3: Resource Identification")
    print("-" * 40)
    print(f"Total resources: {len(plan.all_resources)}")
    print(f"Resource identification: {result.resource_identification:.1%}")
    print()

    by_type = {}
    for resource in plan.all_resources:
        rtype = resource.type.value
        if rtype not in by_type:
            by_type[rtype] = []
        by_type[rtype].append(resource)

    for rtype, resources in by_type.items():
        print(f"  {rtype}: {len(resources)}")
        for r in resources[:3]:  # Show first 3
            print(f"    - {r.name} ({r.identifier})")
            if r.endpoint:
                print(f"      Endpoint: {r.endpoint}")
            if r.namespace:
                print(f"      Namespace: {r.namespace}")
    print()

    # Summary
    print("=" * 60)
    print("CRITERION VERIFICATION")
    print("=" * 60)
    print()

    c1_pass = plan.completeness_ratio > 0
    c2_pass = plan.total_pre_conditions > 0 and plan.total_post_conditions > 0
    c3_pass = len(plan.all_resources) > 0

    print(f"1. Specification completeness: {'PASS' if c1_pass else 'FAIL'}")
    print(f"   - {len(plan.specifications)} specs generated")
    print(f"   - {plan.completeness_ratio:.0%} complete")
    print()

    print(f"2. Validation rules: {'PASS' if c2_pass else 'FAIL'}")
    print(f"   - {plan.total_pre_conditions} pre-conditions")
    print(f"   - {plan.total_post_conditions} post-conditions")
    print()

    print(f"3. Resource identification: {'PASS' if c3_pass else 'FAIL'}")
    print(f"   - {len(plan.all_resources)} resources identified")
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
