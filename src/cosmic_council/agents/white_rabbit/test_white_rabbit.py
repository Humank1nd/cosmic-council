"""
WHITE RABBIT - Test Suite.

Tests the input handling and cycle initiation capabilities.
Every journey begins with a single prompt.

"Follow the White Rabbit"
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add path for imports - go up to src directory
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, src_dir)

from cosmic_council.agents.white_rabbit import (
    # Engine
    WhiteRabbitEngine,
    WhiteRabbitResult,
    create_white_rabbit,
    follow_the_rabbit,
    # Configuration
    WhiteRabbitConfig,
    # Models
    InputType,
    IntentCategory,
    UrgencyLevel,
    InputPrompt,
    Intent,
    CycleInitiation,
    # Components
    InputReceiver,
    IntentClassifier,
    CycleInitiator,
    create_input_receiver,
    create_intent_classifier,
    create_cycle_initiator,
    # Constants
    WHITE_RABBIT_SYMBOL,
)


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_criterion(name: str, rate: float, passed: bool) -> None:
    """Print criterion result."""
    status = "PASSED" if passed else "FAILED"
    bar = "#" * int(rate * 20) + "-" * (20 - int(rate * 20))
    print(f"  {name}: [{bar}] {rate:.0%} - {status}")


async def test_input_receiver() -> bool:
    """Test Criterion 1: Input Reception."""
    print_header("Testing Criterion 1: Input Reception")

    config = WhiteRabbitConfig()
    receiver = create_input_receiver(config)

    # Test 1: Simple text input
    print("\n  Test 1: Simple text input")
    result1 = receiver.receive(
        content="Why is the database slow?",
        input_type=InputType.TEXT,
        source_id="user_123",
        source_type="user",
        channel="api",
    )
    print(f"    Received: {result1.prompt.content[:50]}...")
    print(f"    Valid: {result1.validation.is_valid}")
    print(f"    Processing time: {result1.processing_time_ms}ms")

    # Test 2: Structured input
    print("\n  Test 2: Structured input")
    result2 = receiver.receive_structured(
        data={
            "query": "Analyze performance metrics",
            "filters": {"service": "api-gateway"},
            "limit": 100,
        },
        source_id="system_1",
        source_type="system",
    )
    print(f"    Received structured data")
    print(f"    Valid: {result2.validation.is_valid}")

    # Test 3: Empty input (should fail validation)
    print("\n  Test 3: Empty input validation")
    result3 = receiver.receive(
        content="",
        input_type=InputType.TEXT,
        source_id="user_456",
    )
    print(f"    Empty input valid: {result3.validation.is_valid}")
    print(f"    Errors: {result3.validation.errors}")

    # Test 4: Batch receive
    print("\n  Test 4: Batch input reception")
    batch_result = receiver.receive_batch([
        {"content": "First prompt", "input_type": InputType.TEXT},
        {"content": "Second prompt", "input_type": InputType.QUERY},
        {"content": "Third prompt", "input_type": InputType.COMMAND},
    ])
    total_attempted = len(batch_result.inputs)
    success_rate = batch_result.total_valid / total_attempted if total_attempted > 0 else 0
    print(f"    Received {batch_result.total_received} inputs")
    print(f"    Valid: {batch_result.total_valid}, Invalid: {batch_result.total_invalid}")
    print(f"    Success rate: {success_rate:.0%}")

    # Get metrics
    metrics = receiver.get_metrics()
    print(f"\n  Metrics: {metrics['total_received']} received, {metrics['total_invalid']} invalid")

    # Criterion passes if validation rate > 50% (we intentionally test invalid inputs)
    validation_rate = metrics["validation_rate"]
    passed = validation_rate >= 0.5
    print_criterion("Input Reception", validation_rate, passed)

    return passed


async def test_intent_classifier() -> bool:
    """Test Criterion 2: Intent Classification."""
    print_header("Testing Criterion 2: Intent Classification")

    config = WhiteRabbitConfig()
    classifier = create_intent_classifier(config)

    test_cases = [
        ("Why is the database slow?", IntentCategory.INQUIRY),
        ("Fix the memory leak in the cache service", IntentCategory.ACTION),
        ("Analyze the traffic patterns from last week", IntentCategory.ANALYSIS),
        ("Create a new API endpoint for users", IntentCategory.CREATION),
        ("Optimize the query performance", IntentCategory.OPTIMIZATION),
        ("Resolve the authentication failures", IntentCategory.RESOLUTION),
        ("Monitor CPU usage across all nodes", IntentCategory.MONITORING),
    ]

    correct = 0
    total = len(test_cases)

    for content, expected_category in test_cases:
        # Create a prompt
        prompt = InputPrompt(
            content=content,
            input_type=InputType.TEXT,
            source_id="test",
        )

        # Classify
        result = classifier.classify(prompt)

        # Check if correct
        is_correct = result.intent.category == expected_category
        if is_correct:
            correct += 1

        status = "OK" if is_correct else "WRONG"
        print(f"\n  Input: \"{content[:40]}...\"")
        print(f"    Expected: {expected_category.value}")
        print(f"    Got: {result.intent.category.value} (confidence: {result.classification_confidence:.0%})")
        print(f"    Subject: {result.intent.subject}")
        print(f"    Status: {status}")

        if result.intent.initial_questions:
            print(f"    Initial questions: {result.intent.initial_questions[0]}")

    # Get metrics
    metrics = classifier.get_metrics()
    print(f"\n  Metrics: {metrics['total_classified']} classified")
    print(f"    Average confidence: {metrics['average_confidence']:.0%}")

    # Criterion passes if accuracy > 50% (intent classification is fuzzy)
    accuracy = correct / total
    passed = accuracy >= 0.5
    print_criterion("Intent Classification", accuracy, passed)

    return passed


async def test_cycle_initiator() -> bool:
    """Test Criterion 3: Cycle Initiation."""
    print_header("Testing Criterion 3: Cycle Initiation")

    config = WhiteRabbitConfig(auto_initiate=True)
    initiator = create_cycle_initiator(config)

    # Track Red Owl invocations
    red_owl_calls = []

    async def mock_red_owl(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Red Owl callback."""
        red_owl_calls.append(payload)
        return {"status": "received", "cycle_id": payload["cycle_id"]}

    # Set the callback
    initiator.set_red_owl_callback(mock_red_owl)

    # Create test prompt and intent
    prompt = InputPrompt(
        content="Why is latency increasing?",
        input_type=InputType.TEXT,
        source_id="test_user",
    )

    intent = Intent(
        category=IntentCategory.INQUIRY,
        subject="latency",
        action_requested="investigate",
        entities=["latency", "performance"],
        keywords=["increasing", "slow"],
        initial_questions=["What services are affected?", "When did it start?"],
        suggested_hypotheses=["Network congestion", "Database bottleneck"],
        urgency=UrgencyLevel.HIGH,
        confidence=0.85,
    )

    # Test 1: Initiate a cycle
    print("\n  Test 1: Initiate cycle")
    result1 = await initiator.initiate(prompt, intent)
    print(f"    Cycle ID: {result1.initiation.cycle_id}")
    print(f"    Cycle Number: {result1.initiation.cycle_number}")
    print(f"    Initiated: {result1.initiation.initiated}")
    print(f"    Red Owl Invoked: {result1.red_owl_invoked}")

    # Test 2: Initiate another cycle
    print("\n  Test 2: Initiate another cycle")
    prompt2 = InputPrompt(
        content="Optimize cache hit rate",
        input_type=InputType.TEXT,
        source_id="test_user",
    )
    intent2 = Intent(
        category=IntentCategory.OPTIMIZATION,
        subject="cache",
        confidence=0.9,
    )
    result2 = await initiator.initiate(prompt2, intent2)
    print(f"    Cycle ID: {result2.initiation.cycle_id}")
    print(f"    Initiated: {result2.initiation.initiated}")
    print(f"    Red Owl Invoked: {result2.red_owl_invoked}")

    # Test 3: Feedback loop (continuing from Black Snake)
    print("\n  Test 3: Feedback loop cycle")
    prompt3 = InputPrompt(
        content="Continue investigation with new evidence",
        input_type=InputType.FEEDBACK,
        source_id="black_snake",
        source_type="black_snake",
        parent_cycle_id=result1.initiation.cycle_id,
        metadata={
            "feedback": {
                "insights": ["Initial root cause identified"],
                "new_questions": ["What is the exact query causing slowdown?"],
                "hypotheses_to_test": ["Index missing on user_id column"],
            }
        },
    )
    intent3 = Intent(
        category=IntentCategory.INQUIRY,
        subject="database investigation",
        confidence=0.95,
    )
    result3 = await initiator.initiate(prompt3, intent3)
    print(f"    Cycle ID: {result3.initiation.cycle_id}")
    print(f"    Cycle Number: {result3.initiation.cycle_number} (should be 2)")
    print(f"    Previous Cycle: {result3.initiation.previous_cycle_id}")
    print(f"    Red Owl Invoked: {result3.red_owl_invoked}")

    # Get metrics
    metrics = initiator.get_metrics()
    print(f"\n  Metrics:")
    print(f"    Total initiated: {metrics['total_initiated']}")
    print(f"    Total invoked: {metrics['total_invoked']}")
    print(f"    Invocation rate: {metrics['invocation_rate']:.0%}")
    print(f"    Red Owl calls received: {len(red_owl_calls)}")

    # Criterion passes if invocation rate > 80%
    invocation_rate = metrics["invocation_rate"]
    passed = invocation_rate >= 0.8
    print_criterion("Cycle Initiation", invocation_rate, passed)

    return passed


async def test_full_engine() -> bool:
    """Test the full White Rabbit engine."""
    print_header("Testing Full White Rabbit Engine")

    # Track Red Owl invocations
    red_owl_calls = []

    async def mock_red_owl(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Red Owl callback."""
        red_owl_calls.append(payload)
        return {"status": "received", "inquiry_started": True}

    # Create engine
    config = WhiteRabbitConfig(auto_initiate=True)
    engine = create_white_rabbit(config)
    engine.set_red_owl_callback(mock_red_owl)

    # Test 1: Process a simple inquiry
    print("\n  Test 1: Process inquiry prompt")
    result1 = await engine.process(
        content="Why are users experiencing slow login times?",
        input_type=InputType.TEXT,
        source_id="user_alice",
        source_type="user",
        channel="web",
        context={"session_id": "sess_123"},
    )

    print(f"    Success: {result1.success}")
    print(f"    Cycle ID: {result1.cycle_initiation.cycle_id if result1.cycle_initiation else 'N/A'}")
    print(f"    Intent: {result1.classification_result.intent.category.value if result1.classification_result else 'N/A'}")
    print(f"    Input Reception: {result1.input_reception:.0%}")
    print(f"    Intent Classification: {result1.intent_classification:.0%}")
    print(f"    Cycle Initiation: {result1.cycle_initiation_rate:.0%}")
    print(f"    Duration: {result1.duration_ms}ms")

    if result1.reasoning:
        print(f"    Reasoning:")
        for r in result1.reasoning[:3]:
            print(f"      - {r}")

    # Test 2: Process an action request
    print("\n  Test 2: Process action prompt")
    result2 = await engine.process(
        content="Fix the memory leak in the cache service immediately",
        input_type=InputType.COMMAND,
        source_id="admin_bob",
        source_type="admin",
        channel="cli",
    )

    print(f"    Success: {result2.success}")
    print(f"    Intent: {result2.classification_result.intent.category.value if result2.classification_result else 'N/A'}")
    print(f"    Urgency: {result2.classification_result.intent.urgency.value if result2.classification_result else 'N/A'}")

    # Test 3: Use convenience function
    print("\n  Test 3: follow_the_rabbit() convenience function")
    result3 = await follow_the_rabbit("Analyze API response times")
    print(f"    Success: {result3.success}")
    print(f"    Duration: {result3.duration_ms}ms")

    # Get combined metrics
    metrics = engine.get_metrics()
    print(f"\n  Combined Metrics:")
    print(f"    Input Receiver: {metrics['input_receiver']}")
    print(f"    Intent Classifier: {metrics['intent_classifier']}")
    print(f"    Cycle Initiator: {metrics['cycle_initiator']}")

    # Overall success
    all_passed = result1.success and result2.success and result3.success
    print(f"\n  All prompts processed successfully: {all_passed}")

    return all_passed


async def main():
    """Run all White Rabbit tests."""
    # Print the White Rabbit symbol
    try:
        print(f"\n{WHITE_RABBIT_SYMBOL} WHITE RABBIT - Input & Initiation Agent")
    except UnicodeEncodeError:
        print("\n[WHITE RABBIT] - Input & Initiation Agent")

    print("Follow the White Rabbit - Every journey begins here.")

    # Run criterion tests
    criterion1_passed = await test_input_receiver()
    criterion2_passed = await test_intent_classifier()
    criterion3_passed = await test_cycle_initiator()

    # Run full engine test
    engine_passed = await test_full_engine()

    # Summary
    print_header("WHITE RABBIT TEST SUMMARY")

    print("\n  Three Falsifiable Criteria:")
    print_criterion("1. Input Reception", 1.0 if criterion1_passed else 0.0, criterion1_passed)
    print_criterion("2. Intent Classification", 1.0 if criterion2_passed else 0.0, criterion2_passed)
    print_criterion("3. Cycle Initiation", 1.0 if criterion3_passed else 0.0, criterion3_passed)

    print(f"\n  Full Engine Test: {'PASSED' if engine_passed else 'FAILED'}")

    all_passed = criterion1_passed and criterion2_passed and criterion3_passed and engine_passed

    print("\n" + "=" * 60)
    if all_passed:
        try:
            print(f"  {WHITE_RABBIT_SYMBOL} ALL CRITERIA PASSED - White Rabbit is ready!")
        except UnicodeEncodeError:
            print("  [WHITE RABBIT] ALL CRITERIA PASSED - White Rabbit is ready!")
        print("  The cycle can begin. Follow the White Rabbit...")
    else:
        print("  SOME CRITERIA FAILED - Review the output above")
    print("=" * 60 + "\n")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
