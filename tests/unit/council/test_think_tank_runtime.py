from cosmic_council.integrations.think_tank_runtime import (
    ThinkTankRuntime,
    build_red_inner_council_payload,
    run_outer_sentry_gate,
    run_sentry_a_recovery,
    run_sentry_b_recovery,
)
from cosmic_council.api.compat_council import build_bootstrap_orange_payload
from cosmic_council.core.models import Problem
from types import SimpleNamespace


def test_build_red_inner_council_payload_contains_recursive_children():
    payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the first true Think Tank runtime slice.",
        workflow_session_id="session-test-red",
        source="test",
    )

    assert payload["node_identity"]["node_address"] == "red"
    assert payload["node_identity"]["node_kind"] == "outer_seat"
    children = payload["think_tank"]["inner_council"]
    assert len(children) == 6
    assert {child["node_identity"]["node_address"] for child in children} == {
        "red.red",
        "red.orange",
        "red.yellow",
        "red.green",
        "red.blue",
        "red.purple",
    }


def test_outer_sentry_gate_passes_for_valid_red_payload():
    payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the first true Think Tank runtime slice.",
        workflow_session_id="session-test-red",
        source="test",
    )

    verdict = run_outer_sentry_gate(
        seat="red",
        output_payload=payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
        auto_recover_sentry_a=False,
    )

    assert verdict["overall_verdict"] == "pass"
    assert verdict["redirect_address"] is None
    assert verdict["verdict"]["final_verdict"] == "PASS"
    assert verdict["sentry_recursion"]["sentry_a"]["node_identity"]["node_address"] == "red.sentry_a"
    assert len(verdict["sentry_recursion"]["sentry_a"]["inner_hexagon"]) == 6
    assert len(verdict["sentry_recursion"]["sentry_a"]["recursive_validation"]) == 6
    assert verdict["sentry_recursion"]["sentry_a"]["observation_pass_count"] == 6
    assert verdict["sentry_recursion"]["sentry_a"]["observation_fail_count"] == 0
    assert len(verdict["sentry_recursion"]["sentry_b"]["recursive_validation"]) == 6
    assert verdict["sentry_recursion"]["sentry_b"]["analysis_pass_count"] == 6
    assert verdict["sentry_recursion"]["sentry_b"]["analysis_fail_count"] == 0
    assert len(verdict["sentry_recursion"]["sentry_c"]["recursive_validation"]) == 6
    assert verdict["sentry_recursion"]["sentry_c"]["conclusion_pass_count"] == 6
    assert verdict["sentry_recursion"]["sentry_c"]["conclusion_fail_count"] == 0
    assert verdict["recursive_gate"]["passed"] is True
    assert verdict["recursive_gate"]["redirect_address"] is None


def test_outer_sentry_gate_reports_recursive_child_failures():
    payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the first true Think Tank runtime slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    payload["think_tank"]["inner_council"][0].pop("contribution", None)

    verdict = run_outer_sentry_gate(
        seat="red",
        output_payload=payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
        auto_recover_sentry_a=False,
    )

    recursive = verdict["sentry_recursion"]["sentry_a"]["recursive_validation"]
    assert verdict["overall_verdict"] == "fail"
    assert verdict["redirect_address"] == "red.sentry_a"
    assert verdict["recursive_gate"]["passed"] is False
    assert verdict["recursive_gate"]["redirect_address"] == "red.sentry_a"
    assert verdict["recursive_gate"]["recovery_plan"]["owner"] == "red.sentry_a"
    assert verdict["recursive_gate"]["recovery_plan"]["mode"] == "recursive_observation_repair"
    assert verdict["recursive_gate"]["recovery_plan"]["steps"][0]["seat"] == "red"
    assert any(result["verdict"] == "fail" for result in recursive)
    assert verdict["sentry_recursion"]["sentry_a"]["observation_fail_count"] == 1
    assert verdict["sentry_recursion"]["sentry_b"]["analysis_fail_count"] == 1
    assert verdict["sentry_recursion"]["sentry_c"]["conclusion_fail_count"] == 1


def test_sentry_a_recovery_repairs_missing_child_output():
    payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the first true Think Tank runtime slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    payload["think_tank"]["inner_council"][0].pop("contribution", None)

    recovery = run_sentry_a_recovery(
        seat="red",
        output_payload=payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )

    repaired_payload = recovery["repaired_payload"]
    repaired_verdict = recovery["recovery_verdict"]
    assert repaired_payload["think_tank"]["inner_council"][0]["contribution"].startswith("Sentry A recovery restored")
    assert repaired_payload["sentry_recovery"]["sentry_a"]["repaired"] is True
    assert repaired_verdict["overall_verdict"] == "pass"
    assert repaired_verdict["recursive_gate"]["passed"] is True


def test_outer_sentry_gate_can_auto_recover_sentry_a_failure():
    payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the first true Think Tank runtime slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    payload["think_tank"]["inner_council"][0].pop("contribution", None)

    verdict = run_outer_sentry_gate(
        seat="red",
        output_payload=payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )

    assert verdict["overall_verdict"] == "pass"
    assert verdict["recursive_gate"]["passed"] is True
    assert verdict["recovery_attempt"]["triggered"] is True
    assert verdict["recovery_attempt"]["mode"] == "auto_sentry_a_recovery"
    assert verdict["recovery_attempt"]["result"] == "recovered"
    assert verdict["repaired_payload"]["sentry_recovery"]["sentry_a"]["repaired"] is True


def test_sentry_b_recovery_repairs_quantum_drift_and_revalidates():
    payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the first true Think Tank runtime slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    payload["think_tank"]["inner_council"][0]["contribution"] = "Use entanglement to bypass the normal reason trace."

    blocked_verdict = run_outer_sentry_gate(
        seat="red",
        output_payload=payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
        auto_recover_sentry_a=False,
        auto_recover_sentry_b=False,
    )

    assert blocked_verdict["overall_verdict"] == "fail"
    assert blocked_verdict["redirect_address"] == "red.sentry_b"

    recovery = run_sentry_b_recovery(
        seat="red",
        output_payload=payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )

    repaired_payload = recovery["repaired_payload"]
    repaired_verdict = recovery["recovery_verdict"]
    repaired_focus = repaired_payload["think_tank"]["inner_council"][0]["contribution"].lower()
    assert "entanglement" not in repaired_focus
    assert "reason" in repaired_focus
    assert repaired_payload["sentry_recovery"]["sentry_b"]["repaired"] is True
    assert repaired_verdict["overall_verdict"] == "pass"


def test_outer_sentry_gate_can_auto_recover_sentry_b_failure():
    payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the first true Think Tank runtime slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    payload["think_tank"]["inner_council"][0]["contribution"] = "Use entanglement to bypass the normal reason trace."

    verdict = run_outer_sentry_gate(
        seat="red",
        output_payload=payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
        auto_recover_sentry_a=False,
    )

    assert verdict["overall_verdict"] == "pass"
    assert verdict["recursive_gate"]["passed"] is True
    assert verdict["recovery_attempt"]["triggered"] is True
    assert verdict["recovery_attempt"]["mode"] == "auto_sentry_b_recovery"
    assert verdict["recovery_attempt"]["result"] == "recovered"
    assert verdict["repaired_payload"]["sentry_recovery"]["sentry_b"]["repaired"] is True


def test_orange_payload_uses_red_inner_council_threads():
    problem = Problem(title="Reduce runtime drift", description="Stabilize the Think Tank slice.", domain="compat_council")
    workflow_session = SimpleNamespace(id="session-test-red")
    red_payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    red_payload["sentry_tribunal"] = run_outer_sentry_gate(
        seat="red",
        output_payload=red_payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )

    orange_payload = build_bootstrap_orange_payload(problem, workflow_session, red_payload)

    assert orange_payload["research_threads"]
    assert "red.red" in orange_payload["inner_council_addresses"]
    assert orange_payload["sentry_observation_summary"]


def test_think_tank_runtime_runs_red_with_sentry_gate():
    runtime = ThinkTankRuntime(source="test.runtime")

    payload = runtime.run_seat(
        seat="red",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
    )

    assert payload["orchestrator"]["runtime"] == "ThinkTankRuntime"
    assert payload["orchestrator"]["seat"] == "red"
    assert payload["node_identity"]["node_address"] == "red"
    assert payload["sentry_tribunal"]["overall_verdict"] == "pass"


def test_think_tank_runtime_runs_orange_with_recursive_plan():
    runtime = ThinkTankRuntime(source="test.runtime")
    red_payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    red_payload["sentry_tribunal"] = run_outer_sentry_gate(
        seat="red",
        output_payload=red_payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )

    payload = runtime.run_seat(
        seat="orange",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=red_payload,
    )

    assert payload["orchestrator"]["seat"] == "orange"
    assert payload["node_identity"]["node_address"] == "orange"
    assert payload["research_threads"]
    assert payload["think_tank"]["inner_council"]
    assert payload["sentry_tribunal"]["overall_verdict"] == "pass"


def test_think_tank_runtime_runs_yellow_with_recursive_plan():
    runtime = ThinkTankRuntime(source="test.runtime")
    red_payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    red_payload["sentry_tribunal"] = run_outer_sentry_gate(
        seat="red",
        output_payload=red_payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )
    orange_payload = runtime.run_seat(
        seat="orange",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=red_payload,
    )

    payload = runtime.run_seat(
        seat="yellow",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=orange_payload,
    )

    assert payload["orchestrator"]["seat"] == "yellow"
    assert payload["node_identity"]["node_address"] == "yellow"
    assert payload["prototype_artifacts"]
    assert payload["think_tank"]["inner_council"]
    assert payload["sentry_tribunal"]["overall_verdict"] == "pass"


def test_think_tank_runtime_runs_green_with_recursive_plan():
    runtime = ThinkTankRuntime(source="test.runtime")
    red_payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    red_payload["sentry_tribunal"] = run_outer_sentry_gate(
        seat="red",
        output_payload=red_payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )
    orange_payload = runtime.run_seat(
        seat="orange",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=red_payload,
    )
    yellow_payload = runtime.run_seat(
        seat="yellow",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=orange_payload,
    )

    payload = runtime.run_seat(
        seat="green",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=yellow_payload,
    )

    assert payload["orchestrator"]["seat"] == "green"
    assert payload["node_identity"]["node_address"] == "green"
    assert payload["budget_focus"]
    assert payload["think_tank"]["inner_council"]
    assert payload["sentry_tribunal"]["overall_verdict"] == "pass"


def test_think_tank_runtime_runs_blue_with_recursive_plan():
    runtime = ThinkTankRuntime(source="test.runtime")
    red_payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    red_payload["sentry_tribunal"] = run_outer_sentry_gate(
        seat="red",
        output_payload=red_payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )
    orange_payload = runtime.run_seat(
        seat="orange",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=red_payload,
    )
    yellow_payload = runtime.run_seat(
        seat="yellow",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=orange_payload,
    )
    green_payload = runtime.run_seat(
        seat="green",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=yellow_payload,
    )

    payload = runtime.run_seat(
        seat="blue",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=green_payload,
    )

    assert payload["orchestrator"]["seat"] == "blue"
    assert payload["node_identity"]["node_address"] == "blue"
    assert payload["delivery_assets"]
    assert payload["think_tank"]["inner_council"]
    assert payload["sentry_tribunal"]["overall_verdict"] == "pass"


def test_think_tank_runtime_runs_purple_with_recursive_plan():
    runtime = ThinkTankRuntime(source="test.runtime")
    red_payload = build_red_inner_council_payload(
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        source="test",
    )
    red_payload["sentry_tribunal"] = run_outer_sentry_gate(
        seat="red",
        output_payload=red_payload,
        mission="Research why runtime drift occurs and hand off to Orange only when sufficient data exists.",
        workflow_session_id="session-test-red",
    )
    orange_payload = runtime.run_seat(
        seat="orange",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=red_payload,
    )
    yellow_payload = runtime.run_seat(
        seat="yellow",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=orange_payload,
    )
    green_payload = runtime.run_seat(
        seat="green",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=yellow_payload,
    )
    blue_payload = runtime.run_seat(
        seat="blue",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=green_payload,
    )

    payload = runtime.run_seat(
        seat="purple",
        problem_title="Reduce runtime drift",
        problem_description="Stabilize the Think Tank slice.",
        workflow_session_id="session-test-red",
        loopback_context=blue_payload,
    )

    assert payload["orchestrator"]["seat"] == "purple"
    assert payload["node_identity"]["node_address"] == "purple"
    assert payload["lessons_learned"]
    assert payload["think_tank"]["inner_council"]
    assert payload["sentry_tribunal"]["overall_verdict"] == "pass"
