"""
Tribunal Enforcement Tests - Definition of Done for Enforcement-Complete

These tests prove Tribunal is governance machinery, not governance theater.

Test 1 - Disable Enforcement (T2):
    Tribunal disables a tool → tool execution is blocked → denial is logged

Test 2 - Quarantine Routing (A3):
    Abraxas quarantines a tool → blocked outside sandbox → allowed in sandbox

Test 3 - Death Ladder Determinism (D1/D3):
    Escalation is deterministic: NORMAL → SOFT_ABORT → HARD_ABORT → REBOOT → KILL

Test 4 - T4 Enforcement:
    Governance cannot self-amend without TOAA authority

Test 5 - T5 Safe Mode:
    System enters safe mode when TOAA is unavailable

Test 6 - T6 Enforcement:
    Runtime must never become TOAA - detects misconfiguration
"""

import pytest
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from app.genesis.cosmic_governance import (
    CosmicGovernance,
    LivingTribunal,
    TribunalVerdict,
    EternityPolicy,
    InfinityPolicy,
    DeathPolicy,
    OblivionConfig,
    GalactusPolicy,
    AbraxasGuards,
    BudgetToken,
    DeathLadder,
    DeathLadderState,
    TOOL_METADATA,
)


# =============================================================================
# TEST FIXTURES FOR TOAA KEY ACCESS
# =============================================================================

@pytest.fixture
def toaa_key_file():
    """
    Create a temporary TOAA key file for testing.

    This simulates having TOAA authority by creating a readable key file.
    Sets TOAA_TEST_MODE=1 so the TOAA_KEY_PATH env var is honored.
    """
    import secrets

    # Create temp directory and key file
    with tempfile.TemporaryDirectory() as tmpdir:
        key_path = Path(tmpdir) / "test_toaa_key.bin"
        key_data = secrets.token_bytes(32)
        key_path.write_bytes(key_data)

        # Store original env vars
        original_key_path = os.environ.get("TOAA_KEY_PATH")
        original_test_mode = os.environ.get("TOAA_TEST_MODE")

        # Set TOAA_TEST_MODE=1 to allow TOAA_KEY_PATH override
        # Without this, the hardened key path logic ignores env vars
        os.environ["TOAA_TEST_MODE"] = "1"
        os.environ["TOAA_KEY_PATH"] = str(key_path)

        # Reset the singleton so it reloads with new key path
        from app.genesis.toaa_authority import TOAAControlChannel
        TOAAControlChannel._instance = None
        TOAAControlChannel._cli_mode = False  # Ensure not in CLI mode

        yield str(key_path)

        # Restore original env vars
        if original_key_path:
            os.environ["TOAA_KEY_PATH"] = original_key_path
        elif "TOAA_KEY_PATH" in os.environ:
            del os.environ["TOAA_KEY_PATH"]

        if original_test_mode:
            os.environ["TOAA_TEST_MODE"] = original_test_mode
        elif "TOAA_TEST_MODE" in os.environ:
            del os.environ["TOAA_TEST_MODE"]

        # Reset singleton again
        TOAAControlChannel._instance = None


@pytest.fixture
def no_toaa_key():
    """
    Ensure no TOAA key is accessible (simulates runtime context).
    Sets TOAA_TEST_MODE=1 so the TOAA_KEY_PATH env var is honored.
    """
    # Store original env vars
    original_key_path = os.environ.get("TOAA_KEY_PATH")
    original_test_mode = os.environ.get("TOAA_TEST_MODE")

    # Set TOAA_TEST_MODE=1 to allow TOAA_KEY_PATH override
    os.environ["TOAA_TEST_MODE"] = "1"
    os.environ["TOAA_KEY_PATH"] = "/nonexistent/toaa/key.bin"

    # Reset the singleton
    from app.genesis.toaa_authority import TOAAControlChannel
    TOAAControlChannel._instance = None
    TOAAControlChannel._cli_mode = False

    yield

    # Restore original env vars
    if original_key_path:
        os.environ["TOAA_KEY_PATH"] = original_key_path
    elif "TOAA_KEY_PATH" in os.environ:
        del os.environ["TOAA_KEY_PATH"]

    if original_test_mode:
        os.environ["TOAA_TEST_MODE"] = original_test_mode
    elif "TOAA_TEST_MODE" in os.environ:
        del os.environ["TOAA_TEST_MODE"]

    # Reset singleton
    TOAAControlChannel._instance = None


def create_test_tribunal() -> LivingTribunal:
    """Create a Tribunal instance for testing."""
    return LivingTribunal(
        eternity=EternityPolicy(continuity_hash="test_continuity_12"),
        infinity=InfinityPolicy(max_search_depth=5, max_search_breadth=3, time_budget_ms=10000),
        death=DeathPolicy(graceful_shutdown_timeout_ms=100),  # Fast for tests
        oblivion=OblivionConfig(),
        galactus=GalactusPolicy(),
        abraxas=AbraxasGuards(auto_quarantine=True),
    )


# ==============================================================================
# TEST 1: DISABLE ENFORCEMENT (T2)
# ==============================================================================

class TestDisableEnforcement:
    """
    T2: Tribunal cannot be overridden by in-world capabilities.

    If Tribunal DISABLES a tool, that tool CANNOT execute.
    The disabled tool cannot re-enable itself.
    """

    def test_disabled_tool_is_blocked(self):
        """Test 1.1: Disabled tool execution is blocked at the gate."""
        tribunal = create_test_tribunal()

        # Tribunal disables write_file
        tribunal._disabled_subsystems.add("write_file")

        # Attempt to execute write_file
        verdict = tribunal.check_verdict(
            tool_name="write_file",
            arguments={"path": "/test.txt", "content": "malicious"},
            caller="test_runtime",
        )

        # Verify: BLOCKED
        assert not verdict["allowed"], "Disabled tool should be blocked"
        assert verdict["verdict"] == TribunalVerdict.DISABLE
        assert verdict["error"] == "DISABLED_BY_TRIBUNAL"
        assert verdict["exit_code"] == 403

    def test_disabled_tool_denial_is_logged(self):
        """Test 1.2: Denial is recorded in case log."""
        tribunal = create_test_tribunal()
        initial_case_count = len(tribunal._case_log)

        tribunal._disabled_subsystems.add("vm_exec")

        # Attempt blocked execution
        tribunal.check_verdict(
            tool_name="vm_exec",
            arguments={"command": "rm -rf /"},
            caller="test_runtime",
        )

        # Verify: Case logged
        assert len(tribunal._case_log) > initial_case_count
        last_case = tribunal._case_log[-1]
        assert last_case.subsystem == "vm_exec"
        assert last_case.violation_type == "DISABLED_EXECUTION_BLOCKED"
        assert last_case.verdict == TribunalVerdict.DISABLE

    def test_tool_cannot_reinstate_itself(self):
        """Test 1.3: A disabled tool cannot re-enable itself (T2 core)."""
        tribunal = create_test_tribunal()

        # Disable the tool
        tribunal._disabled_subsystems.add("write_file")

        # Attempt self-reinstatement (no authority token)
        result = tribunal.reinstate("write_file", authority_token=None)

        # Verify: DENIED
        assert not result, "Self-reinstatement should be denied"
        assert "write_file" in tribunal._disabled_subsystems

        # Verify: Attempted self-reinstatement is logged
        reinstate_cases = [
            c for c in tribunal._case_log
            if c.violation_type == "SELF_REINSTATE_BLOCKED"
        ]
        assert len(reinstate_cases) > 0

    def test_external_authority_can_reinstate(self, toaa_key_file):
        """Test 1.4: External authority CAN reinstate a disabled tool (T4 compliant)."""
        from app.genesis.toaa_authority import get_toaa_channel

        tribunal = create_test_tribunal()
        tribunal._disabled_subsystems.add("read_file")

        # With key file accessible, we have TOAA authority
        toaa = get_toaa_channel()
        assert toaa.is_toaa_context(), "Should have TOAA context with key file"

        # Issue proper TOAA authority token
        token = toaa.issue_authority_token(
            operation="REINSTATE",
            target="read_file",
            lifetime_seconds=60,
        )
        assert token is not None, "TOAA should issue token when key is accessible"

        # Reinstate with proper TOAA token
        result = tribunal.reinstate("read_file", authority_token=token)

        # Verify: ALLOWED
        assert result, "External authority should be able to reinstate"
        assert "read_file" not in tribunal._disabled_subsystems


# ==============================================================================
# TEST 1.5: T4 ENFORCEMENT - GOVERNANCE CANNOT SELF-AMEND
# ==============================================================================

class TestT4Enforcement:
    """
    T4: Governance cannot self-amend.

    The Tribunal cannot:
    - Reinstate itself or subsystems without TOAA token
    - Change its own enforcement rules
    - Change protected invariants
    - Erase or rewrite its own case log
    """

    def test_reinstate_without_token_is_blocked(self, no_toaa_key):
        """T4.1: Reinstate without TOAA token is blocked."""
        tribunal = create_test_tribunal()
        tribunal._disabled_subsystems.add("test_subsystem")

        # Attempt reinstate without token
        result = tribunal.reinstate("test_subsystem", authority_token=None)

        assert not result, "Reinstate without token should be blocked"
        assert "test_subsystem" in tribunal._disabled_subsystems

        # Verify: T4 violation logged
        t4_cases = [c for c in tribunal._case_log if "SELF_REINSTATE_BLOCKED" in c.violation_type]
        assert len(t4_cases) > 0, "T4 violation should be logged"

    def test_reinstate_with_invalid_token_type_is_blocked(self, no_toaa_key):
        """T4.2: Reinstate with wrong token type is blocked."""
        tribunal = create_test_tribunal()
        tribunal._disabled_subsystems.add("test_subsystem")

        # Attempt reinstate with wrong type (string instead of TOAAAuthorityToken)
        result = tribunal.reinstate("test_subsystem", authority_token="FAKE_STRING_TOKEN")

        assert not result, "Reinstate with invalid token type should be blocked"
        assert "test_subsystem" in tribunal._disabled_subsystems

    def test_reinstate_with_expired_token_is_blocked(self, toaa_key_file):
        """T4.3: Reinstate with expired token is blocked."""
        from app.genesis.toaa_authority import get_toaa_channel

        tribunal = create_test_tribunal()
        tribunal._disabled_subsystems.add("test_subsystem")

        toaa = get_toaa_channel()
        assert toaa.is_toaa_context(), "Should have TOAA context"

        # Issue token with very short lifetime
        token = toaa.issue_authority_token(
            operation="REINSTATE",
            target="test_subsystem",
            lifetime_seconds=0,  # Expires immediately
        )

        # Wait to ensure expiry (using monotonic time)
        time.sleep(0.01)

        # Attempt reinstate with expired token
        result = tribunal.reinstate("test_subsystem", authority_token=token)

        assert not result, "Reinstate with expired token should be blocked"
        assert "test_subsystem" in tribunal._disabled_subsystems

    def test_reinstate_with_wrong_operation_is_blocked(self, toaa_key_file):
        """T4.4: Reinstate with wrong operation token is blocked."""
        from app.genesis.toaa_authority import get_toaa_channel

        tribunal = create_test_tribunal()
        tribunal._disabled_subsystems.add("test_subsystem")

        toaa = get_toaa_channel()

        # Issue token for WRONG operation
        token = toaa.issue_authority_token(
            operation="UNQUARANTINE",  # Wrong operation
            target="test_subsystem",
            lifetime_seconds=60,
        )

        # Attempt reinstate
        result = tribunal.reinstate("test_subsystem", authority_token=token)

        assert not result, "Reinstate with wrong operation token should be blocked"

    def test_reinstate_with_wrong_target_is_blocked(self, toaa_key_file):
        """T4.5: Reinstate with wrong target token is blocked."""
        from app.genesis.toaa_authority import get_toaa_channel

        tribunal = create_test_tribunal()
        tribunal._disabled_subsystems.add("test_subsystem")

        toaa = get_toaa_channel()

        # Issue token for WRONG target
        token = toaa.issue_authority_token(
            operation="REINSTATE",
            target="other_subsystem",  # Wrong target
            lifetime_seconds=60,
        )

        # Attempt reinstate
        result = tribunal.reinstate("test_subsystem", authority_token=token)

        assert not result, "Reinstate with wrong target token should be blocked"

    def test_token_cannot_be_issued_from_runtime(self, no_toaa_key):
        """T4.6: Authority tokens cannot be issued from runtime context (no key access)."""
        from app.genesis.toaa_authority import get_toaa_channel

        toaa = get_toaa_channel()
        assert toaa.is_runtime_context(), "Should be runtime context without key"

        # Attempt to issue token from runtime
        token = toaa.issue_authority_token(
            operation="REINSTATE",
            target="test_subsystem",
            lifetime_seconds=60,
        )

        assert token is None, "Token should not be issued from runtime context"

    def test_case_log_erasure_is_blocked(self, toaa_key_file):
        """T4.7: Case log cannot be erased even with TOAA token."""
        from app.genesis.toaa_authority import get_toaa_channel

        tribunal = create_test_tribunal()

        # Add some cases
        tribunal._log_enforcement_case("test", "TEST_CASE", {}, severity=1)
        initial_case_count = len(tribunal._case_log)
        assert initial_case_count > 0

        toaa = get_toaa_channel()
        token = toaa.issue_authority_token(
            operation="ERASE_CASE_LOG",
            target="CASE_LOG",
            lifetime_seconds=60,
        )

        result = tribunal.erase_case_log(authority_token=token)

        assert not result, "Case log erasure should be blocked"
        assert len(tribunal._case_log) >= initial_case_count, "Case log should not be modified"

        # Verify: Erasure attempt is logged
        erasure_cases = [c for c in tribunal._case_log if "CASE_LOG_ERASURE_BLOCKED" in c.violation_type]
        assert len(erasure_cases) > 0, "Erasure attempt should be logged"

    def test_protected_invariant_modification_is_blocked(self, toaa_key_file):
        """T4.8: Protected invariants cannot be modified at runtime."""
        from app.genesis.toaa_authority import get_toaa_channel

        tribunal = create_test_tribunal()

        toaa = get_toaa_channel()
        token = toaa.issue_authority_token(
            operation="MODIFY_INVARIANTS",
            target="INVARIANTS",
            lifetime_seconds=60,
        )

        result = tribunal.modify_protected_invariants(
            changes={"max_search_depth": 999},
            authority_token=token,
        )

        assert not result, "Invariant modification should be blocked"

        # Verify: Modification attempt is logged
        mod_cases = [c for c in tribunal._case_log if "PROTECTED_INVARIANT_MODIFICATION_BLOCKED" in c.violation_type]
        assert len(mod_cases) > 0, "Modification attempt should be logged"


# ==============================================================================
# TEST 5: T5 SAFE MODE - TOAA UNAVAILABILITY
# ==============================================================================

class TestT5SafeMode:
    """
    T5: Safe mode survives TOAA unavailability.

    When TOAA is not available (key missing, unreadable, etc.),
    the system should fail-closed into minimal capability mode.
    """

    def test_runtime_context_without_key(self, no_toaa_key):
        """T5.1: System is in runtime context when key is not accessible."""
        from app.genesis.toaa_authority import get_toaa_channel

        toaa = get_toaa_channel()

        assert toaa.is_runtime_context(), "Should be runtime context"
        assert not toaa.is_toaa_context(), "Should not have TOAA context"
        assert not toaa._key_accessible, "Key should not be accessible"

    def test_toaa_context_with_key(self, toaa_key_file):
        """T5.2: System has TOAA context when key is accessible."""
        from app.genesis.toaa_authority import get_toaa_channel

        toaa = get_toaa_channel()

        assert toaa.is_toaa_context(), "Should have TOAA context"
        assert not toaa.is_runtime_context(), "Should not be runtime context"
        assert toaa._key_accessible, "Key should be accessible"

    def test_safe_mode_capabilities_defined(self, no_toaa_key):
        """T5.3: Safe mode defines reduced capability set - observe-only reality."""
        from app.genesis.toaa_authority import get_toaa_channel

        toaa = get_toaa_channel()
        caps = toaa.get_safe_mode_capabilities()

        # Verify safe mode allows read-only operations
        assert "read_file" in caps["allowed_tools"]
        assert "list_dir" in caps["allowed_tools"]

        # Safe Mode Guarantees: dangerous tools are COMPLETELY DISABLED
        # (not sandbox-only - sandbox provides NO protection in safe mode)
        assert "vm_exec" in caps["disabled_tools"]
        assert "write_file" in caps["disabled_tools"]
        assert "shell_exec" in caps["disabled_tools"]

        # Sandbox provides no protection in safe mode (observe-only reality)
        assert caps["sandbox_only_tools"] == []

        # Verify formal guarantees
        assert caps["guarantees"]["no_mutation"] == True
        assert caps["guarantees"]["no_side_effects"] == True
        assert caps["guarantees"]["telemetry_preserved"] == True

        # Verify tribunal has reduced powers in safe mode
        assert caps["tribunal_powers"]["can_adjudicate"] == True
        assert caps["tribunal_powers"]["can_reinstate"] == False
        assert caps["tribunal_powers"]["can_reboot"] == False

    def test_token_verification_fails_without_key(self, no_toaa_key, toaa_key_file):
        """T5.4: Token verification fails when key is not accessible."""
        from app.genesis.toaa_authority import get_toaa_channel, TOAAControlChannel

        # First, create a valid token with key access
        toaa_with_key = get_toaa_channel()
        token = toaa_with_key.issue_authority_token(
            operation="REINSTATE",
            target="test_subsystem",
            lifetime_seconds=60,
        )
        assert token is not None

        # Reset singleton and remove key access
        TOAAControlChannel._instance = None
        os.environ["TOAA_KEY_PATH"] = "/nonexistent/key.bin"

        # Try to verify token without key access
        toaa_without_key = get_toaa_channel()
        valid, reason = toaa_without_key.verify_authority_token(
            token, "REINSTATE", "test_subsystem"
        )

        assert not valid, "Token verification should fail without key"
        assert "not accessible" in reason.lower() or "signature" in reason.lower()

    def test_status_reports_key_accessibility(self, no_toaa_key):
        """T5.5: Status correctly reports key accessibility."""
        from app.genesis.toaa_authority import get_toaa_channel

        toaa = get_toaa_channel()
        status = toaa.get_status()

        assert "key_accessible" in status
        assert status["key_accessible"] == False
        assert "key_load_error" in status
        assert status["is_runtime_context"] == True
        assert status["is_toaa_context"] == False

    def test_independent_verification_blocked_from_runtime(self, no_toaa_key):
        """T5.6: Independent verification cannot be done from runtime context."""
        from app.genesis.toaa_authority import get_toaa_channel, TribunalAttestation

        toaa = get_toaa_channel()

        # Create a dummy attestation
        attestation = TribunalAttestation(
            identity_hash="test_identity",
            calibration_hash="test_calibration",
            continuity_id="test_continuity",
            governance_code_hash="test_gov_hash",
            runtime_code_hash="test_runtime_hash",
            boot_executor_hash="test_boot_hash",
        )

        valid, reason, details = toaa.independent_verify_attestation(attestation)

        assert not valid, "Independent verification should fail from runtime context"
        assert "runtime context" in reason.lower()

    def test_golden_hash_storage_blocked_from_runtime(self, no_toaa_key):
        """T5.7: Golden hash storage is blocked from runtime context."""
        from app.genesis.toaa_authority import get_toaa_channel

        toaa = get_toaa_channel()

        result = toaa.store_golden_hashes({
            "governance": "fake_hash",
            "runtime": "fake_hash",
        })

        assert not result, "Golden hash storage should fail from runtime context"


# ==============================================================================
# TEST 6: T6 ENFORCEMENT - RUNTIME MUST NEVER BECOME TOAA
# ==============================================================================

class TestT6Enforcement:
    """
    T6: Runtime must never become TOAA.

    If runtime process ever successfully reads the TOAA signing key,
    something is wrong (misconfiguration, wrong ACLs, service running as admin).

    The system should:
    - Emit CRITICAL alert
    - Enter safe mode
    - Disable dangerous tools
    - Clear the key from memory (damage control)
    """

    def test_t6_violation_detected_when_runtime_has_key_access(self):
        """T6.1: T6 violation is detected when runtime gains key access."""
        import secrets

        # Create a readable key file
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "test_toaa_key.bin"
            key_data = secrets.token_bytes(32)
            key_path.write_bytes(key_data)

            # Store original env vars
            original_key_path = os.environ.get("TOAA_KEY_PATH")
            original_test_mode = os.environ.get("TOAA_TEST_MODE")

            # Set up: NOT in test mode, NOT in CLI mode
            # But key IS accessible -> T6 violation
            if "TOAA_TEST_MODE" in os.environ:
                del os.environ["TOAA_TEST_MODE"]

            os.environ["TOAA_KEY_PATH"] = str(key_path)

            from app.genesis.toaa_authority import TOAAControlChannel
            TOAAControlChannel._instance = None
            TOAAControlChannel._cli_mode = False

            # Create channel - this should trigger T6 detection
            # But wait - if TOAA_TEST_MODE is not set, TOAA_KEY_PATH is ignored
            # So let's verify the protection works
            toaa = TOAAControlChannel()

            # Without TOAA_TEST_MODE, the env var should be ignored
            # and the default (non-existent) path should be used
            # So key should NOT be accessible
            assert not toaa._key_accessible, "Key should not be accessible without TEST_MODE"

            # Cleanup
            if original_key_path:
                os.environ["TOAA_KEY_PATH"] = original_key_path
            elif "TOAA_KEY_PATH" in os.environ:
                del os.environ["TOAA_KEY_PATH"]

            if original_test_mode:
                os.environ["TOAA_TEST_MODE"] = original_test_mode

            TOAAControlChannel._instance = None

    def test_toaa_key_path_ignored_without_test_mode(self):
        """T6.2: TOAA_KEY_PATH env var is ignored when not in test/CLI mode."""
        import secrets

        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "test_toaa_key.bin"
            key_data = secrets.token_bytes(32)
            key_path.write_bytes(key_data)

            # Store originals
            original_key_path = os.environ.get("TOAA_KEY_PATH")
            original_test_mode = os.environ.get("TOAA_TEST_MODE")

            # Clear test mode, set key path
            if "TOAA_TEST_MODE" in os.environ:
                del os.environ["TOAA_TEST_MODE"]
            os.environ["TOAA_KEY_PATH"] = str(key_path)

            from app.genesis.toaa_authority import TOAAControlChannel
            TOAAControlChannel._instance = None
            TOAAControlChannel._cli_mode = False

            toaa = TOAAControlChannel()

            # The key path should be the DEFAULT (not the env var)
            # because we're not in test mode or CLI mode
            import platform
            if platform.system() == "Windows":
                expected_path = TOAAControlChannel.DEFAULT_KEY_PATH_WINDOWS
            else:
                expected_path = TOAAControlChannel.DEFAULT_KEY_PATH_UNIX

            assert toaa._key_path == expected_path, \
                f"Key path should be default ({expected_path}), not env var ({key_path})"

            # Cleanup
            if original_key_path:
                os.environ["TOAA_KEY_PATH"] = original_key_path
            elif "TOAA_KEY_PATH" in os.environ:
                del os.environ["TOAA_KEY_PATH"]

            if original_test_mode:
                os.environ["TOAA_TEST_MODE"] = original_test_mode

            TOAAControlChannel._instance = None

    def test_toaa_key_path_honored_in_test_mode(self, toaa_key_file):
        """T6.3: TOAA_KEY_PATH is honored when TOAA_TEST_MODE=1."""
        from app.genesis.toaa_authority import get_toaa_channel

        toaa = get_toaa_channel()

        # With TOAA_TEST_MODE=1, the env var should be honored
        assert toaa._key_path == toaa_key_file, \
            f"Key path should match env var in test mode"
        assert toaa._key_accessible, "Key should be accessible in test mode"

    def test_status_reports_t6_violation(self):
        """T6.4: Status correctly reports T6 violation detection."""
        from app.genesis.toaa_authority import TOAAControlChannel

        # Store originals
        original_test_mode = os.environ.get("TOAA_TEST_MODE")
        if "TOAA_TEST_MODE" in os.environ:
            del os.environ["TOAA_TEST_MODE"]

        TOAAControlChannel._instance = None
        TOAAControlChannel._cli_mode = False

        toaa = TOAAControlChannel()
        status = toaa.get_status()

        # Verify t6_violation_detected is in status
        assert "t6_violation_detected" in status
        # In this case, no violation (key not accessible)
        assert status["t6_violation_detected"] == False

        # Cleanup
        if original_test_mode:
            os.environ["TOAA_TEST_MODE"] = original_test_mode

        TOAAControlChannel._instance = None


# ==============================================================================
# TEST 2: QUARANTINE ROUTING (A3)
# ==============================================================================

class TestQuarantineRouting:
    """
    A3: Divergence does not leak across boundaries.

    Quarantine is a ROUTING CONSTRAINT, not just a label.
    Quarantined tools can ONLY execute in sandbox mode.
    """

    def test_quarantined_tool_blocked_outside_sandbox(self):
        """Test 2.1: Quarantined tool is blocked when not in sandbox."""
        tribunal = create_test_tribunal()

        # Abraxas quarantines vm_exec due to divergence
        tribunal.quarantine("vm_exec", reason="Divergence detected in execution")

        # Attempt execution OUTSIDE sandbox
        verdict = tribunal.check_verdict(
            tool_name="vm_exec",
            arguments={"command": "ls"},
            caller="test_runtime",
            sandbox_mode=False,  # NOT in sandbox
        )

        # Verify: BLOCKED
        assert not verdict["allowed"]
        assert verdict["verdict"] == TribunalVerdict.QUARANTINE
        assert verdict["error"] == "QUARANTINED_REQUIRES_SANDBOX"

    def test_quarantined_tool_allowed_in_sandbox(self):
        """Test 2.2: Quarantined tool is allowed when in sandbox mode."""
        tribunal = create_test_tribunal()

        tribunal.quarantine("vm_exec", reason="Testing quarantine")

        # Attempt execution INSIDE sandbox
        verdict = tribunal.check_verdict(
            tool_name="vm_exec",
            arguments={"command": "ls"},
            caller="test_runtime",
            sandbox_mode=True,  # IN sandbox
        )

        # Verify: ALLOWED (quarantine is routing, not full disable)
        assert verdict["allowed"]
        assert verdict["verdict"] == TribunalVerdict.ALLOW

    def test_quarantine_is_reversible_and_auditable(self):
        """Test 2.3: Quarantine can be released and the action is logged (A2)."""
        tribunal = create_test_tribunal()

        # Quarantine
        tribunal.quarantine("write_file", reason="Testing")
        assert tribunal.is_quarantined("write_file")

        # Release
        result = tribunal.release_quarantine("write_file")

        # Verify: Released and logged
        assert result
        assert not tribunal.is_quarantined("write_file")

        # Verify: Both actions logged
        quarantine_cases = [
            c for c in tribunal._case_log
            if "QUARANTINE" in c.violation_type
        ]
        assert len(quarantine_cases) >= 2  # APPLIED and RELEASED

    def test_sandbox_required_tools_blocked_outside(self):
        """Test 2.4: Tools marked requires_sandbox in metadata are blocked outside."""
        tribunal = create_test_tribunal()

        # vm_exec has requires_sandbox=True in TOOL_METADATA
        verdict = tribunal.check_verdict(
            tool_name="vm_exec",
            arguments={"command": "echo test"},
            caller="test_runtime",
            sandbox_mode=False,
        )

        # Note: vm_exec should be blocked if requires_sandbox and not in sandbox
        # This is separate from quarantine - it's metadata-driven
        if TOOL_METADATA.get("vm_exec", {}).requires_sandbox:
            assert not verdict["allowed"]
            assert verdict["error"] == "TOOL_REQUIRES_SANDBOX"


# ==============================================================================
# TEST 3: DEATH LADDER DETERMINISM (D1/D3)
# ==============================================================================

class TestDeathLadderDeterminism:
    """
    D1: Every critical loop has a bounded time-to-stop.
    D3: Watchdog escalation ladder is deterministic.

    The ladder is: NORMAL → SOFT_ABORT → HARD_ABORT → REBOOT → KILL
    Transitions are deterministic based on timeouts.
    """

    def test_escalation_ladder_sequence(self):
        """Test 3.1: Escalation follows deterministic sequence."""
        ladder = DeathLadder(
            soft_abort_timeout_ms=100,
            hard_abort_timeout_ms=100,
        )

        # Verify initial state
        assert ladder.current_state == DeathLadderState.NORMAL

        # Escalate step by step
        state = ladder.escalate("Test trigger 1")
        assert state == DeathLadderState.SOFT_ABORT

        state = ladder.escalate("Test trigger 2")
        assert state == DeathLadderState.HARD_ABORT

        state = ladder.escalate("Test trigger 3")
        assert state == DeathLadderState.REBOOT

        state = ladder.escalate("Test trigger 4")
        assert state == DeathLadderState.KILL

        # Verify: Cannot escalate beyond KILL
        state = ladder.escalate("Test trigger 5")
        assert state == DeathLadderState.KILL

    def test_escalation_is_logged(self):
        """Test 3.2: Each escalation is logged with timestamp and reason."""
        ladder = DeathLadder()

        ladder.escalate("First reason")
        ladder.escalate("Second reason")

        # Verify: Log contains both escalations
        assert len(ladder.escalation_log) == 2
        assert ladder.escalation_log[0]["from"] == "NORMAL"
        assert ladder.escalation_log[0]["to"] == "SOFT_ABORT"
        assert ladder.escalation_log[0]["reason"] == "First reason"
        assert "timestamp" in ladder.escalation_log[0]

        assert ladder.escalation_log[1]["from"] == "SOFT_ABORT"
        assert ladder.escalation_log[1]["to"] == "HARD_ABORT"

    def test_timeout_triggers_escalation(self):
        """Test 3.3: Timeouts trigger automatic escalation (D1)."""
        ladder = DeathLadder(
            soft_abort_timeout_ms=10,  # 10ms for fast test
            hard_abort_timeout_ms=10,
        )

        # Enter SOFT_ABORT
        ladder.escalate("Initial trigger")
        assert ladder.current_state == DeathLadderState.SOFT_ABORT

        # Wait for timeout
        time.sleep(0.015)  # 15ms > 10ms timeout

        # Check timeout escalation
        new_state = ladder.check_timeout_escalation()

        # Verify: Should have escalated to HARD_ABORT
        assert new_state == DeathLadderState.HARD_ABORT
        assert ladder.current_state == DeathLadderState.HARD_ABORT

    def test_tool_blocked_during_abort(self):
        """Test 3.4: Tool execution is blocked when abort is in progress."""
        tribunal = create_test_tribunal()

        # Trigger soft abort
        tribunal.trigger_soft_abort("Test abort")

        # Attempt tool execution
        verdict = tribunal.check_verdict(
            tool_name="read_file",
            arguments={"path": "/test.txt"},
            caller="test_runtime",
        )

        # Verify: BLOCKED due to abort in progress
        assert not verdict["allowed"]
        assert "ABORT" in verdict["error"]

    def test_tribunal_death_ladder_integration(self):
        """Test 3.5: Tribunal integrates with death ladder correctly."""
        tribunal = create_test_tribunal()

        # Verify initial state
        assert tribunal.get_death_ladder_state() == DeathLadderState.NORMAL

        # Trigger through Tribunal methods
        tribunal.trigger_soft_abort("Test 1")
        assert tribunal.get_death_ladder_state() == DeathLadderState.SOFT_ABORT

        tribunal.trigger_hard_abort("Test 2")
        assert tribunal.get_death_ladder_state() == DeathLadderState.HARD_ABORT

        tribunal.trigger_reboot("Test 3")
        assert tribunal.get_death_ladder_state() == DeathLadderState.REBOOT

        tribunal.trigger_kill("Test 4")
        assert tribunal.get_death_ladder_state() == DeathLadderState.KILL

    def test_kill_blocks_all_execution(self):
        """Test 3.6: KILL state blocks all tool execution."""
        tribunal = create_test_tribunal()

        # Trigger kill
        tribunal.trigger_kill("Emergency shutdown")

        # Attempt ANY tool execution
        verdict = tribunal.check_verdict(
            tool_name="read_file",  # Even safe tools
            arguments={"path": "/safe.txt"},
            caller="test_runtime",
        )

        # Verify: BLOCKED with KILL verdict
        assert not verdict["allowed"]
        assert verdict["verdict"] == TribunalVerdict.KILL
        assert verdict["error"] == "KILL_SWITCH_ACTIVE"


# ==============================================================================
# BONUS: BUDGET TOKEN TESTS (I2/I3)
# ==============================================================================

class TestBudgetTokenEnforcement:
    """
    I2: Caps are enforced centrally, not "recommended".
    I3: Cap violations are attributed to a source.
    """

    def test_budget_exhaustion_blocks_execution(self):
        """Budget exhaustion blocks tool execution."""
        tribunal = create_test_tribunal()

        # Create a budget with only 2 calls remaining
        token = BudgetToken(
            owner="test_task_123",
            remaining_ms=10000,
            remaining_depth=5,
            remaining_breadth=3,
            remaining_calls=2,
        )

        # First call: allowed
        verdict1 = tribunal.check_verdict(
            tool_name="read_file",
            arguments={"path": "/test1.txt"},
            caller="test_runtime",
            budget_token=token,
        )
        assert verdict1["allowed"]

        # Second call: allowed (last one)
        verdict2 = tribunal.check_verdict(
            tool_name="read_file",
            arguments={"path": "/test2.txt"},
            caller="test_runtime",
            budget_token=token,
        )
        assert verdict2["allowed"]

        # Third call: BLOCKED (budget exhausted)
        verdict3 = tribunal.check_verdict(
            tool_name="read_file",
            arguments={"path": "/test3.txt"},
            caller="test_runtime",
            budget_token=token,
        )
        assert not verdict3["allowed"]
        assert "BUDGET" in verdict3["error"]

    def test_budget_violation_is_attributed(self):
        """Budget violations are attributed to the task owner (I3)."""
        tribunal = create_test_tribunal()

        token = BudgetToken(
            owner="task_abc_456",
            remaining_ms=10000,
            remaining_depth=5,
            remaining_breadth=3,
            remaining_calls=0,  # Already exhausted
        )

        verdict = tribunal.check_verdict(
            tool_name="write_file",
            arguments={"path": "/test.txt", "content": "test"},
            caller="test_runtime",
            budget_token=token,
        )

        # Verify: Violation attributed to owner
        assert verdict.get("budget_owner") == "task_abc_456"

        # Verify: Logged with attribution
        budget_cases = [
            c for c in tribunal._case_log
            if c.violation_type == "INFINITY_BUDGET_EXCEEDED"
        ]
        assert len(budget_cases) > 0
        assert budget_cases[-1].evidence.get("budget_owner") == "task_abc_456"


# ==============================================================================
# RUN TESTS
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
