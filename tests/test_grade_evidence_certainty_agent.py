"""
Automated Pytest Test Suite for Grade Evidence Certainty Agent.
Domain: Radiology & Neuroimaging Systems
Standard: ACR RADS / Fleischner Society / ASPECTS Guidelines
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


# ===========================================================================
# Security & Validation Tests (added for hardening)
# ===========================================================================

def test_audit_trail_requires_secret_key():
    """AuditTrail must not instantiate without a secret key."""
    # Clear any existing env var
    original = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        with pytest.raises(SecurityException, match="AUDIT_SECRET_KEY"):
            AuditTrail()
    finally:
        if original is not None:
            os.environ["AUDIT_SECRET_KEY"] = original


def test_audit_trail_rejects_short_key():
    """Keys shorter than 16 chars must be rejected."""
    with pytest.raises(SecurityException, match="at least 16 characters"):
        AuditTrail(secret_key="short")


def test_audit_trail_accepts_explicit_key():
    """Explicit key parameter must work."""
    trail = AuditTrail(secret_key="test-key-that-is-long-enough-12345")
    assert len(trail.get_trail()) == 0
    assert trail.verify_integrity() is True


def test_audit_trail_signature_verification():
    """Tampered entries must fail integrity verification."""
    trail = AuditTrail(secret_key="test-key-that-is-long-enough-12345")
    trail.log("test", "test_tier", "TEST_EVENT", {"data": "value1"})
    trail.log("test", "test_tier", "TEST_EVENT", {"data": "value2"})
    assert trail.verify_integrity() is True

    # Tamper with an entry
    trail.logs[0]["payload_hash"] = "tampered_hash"
    assert trail.verify_integrity() is False


def test_system_task_payload_rejects_nan():
    """NaN metric values must be rejected."""
    with pytest.raises(Exception):  # pydantic.ValidationError
        SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("nan"))


def test_system_task_payload_rejects_infinity():
    """Infinite metric values must be rejected."""
    with pytest.raises(Exception):  # pydantic.ValidationError
        SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("inf"))


def test_system_task_payload_rejects_negative_infinity():
    """Negative infinite metric values must be rejected."""
    with pytest.raises(Exception):  # pydantic.ValidationError
        SystemTaskPayload(task_id="T1", target_identifier="K1", secondary_metric=float("-inf"))


def test_phi_redaction():
    """PHIGuard.redact_phi should mask sensitive patterns."""
    redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567 or MRN-12345678")
    assert "555-123-4567" not in redacted
    assert "MRN-12345678" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted
