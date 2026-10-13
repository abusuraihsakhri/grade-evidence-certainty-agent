import pytest
from grade_master import RiskOfBiasSynthesizerAgent, HeterogeneityImprecisionAgent, CertaintyGradeAggregatorAgent, GRADEMasterCoordinator, main


def test_sub_agents():
    a1 = RiskOfBiasSynthesizerAgent()
    alerts1 = a1.evaluate({"metric_primary": 35.0})
    assert len(alerts1) == 1

    a2 = HeterogeneityImprecisionAgent()
    alerts2 = a2.evaluate({"critical_flag": True})
    assert len(alerts2) == 1

    a3 = CertaintyGradeAggregatorAgent()
    alerts3 = a3.evaluate({"status_text": "DISCORDANT_FINDING"})
    assert len(alerts3) == 1


def test_coordinator():
    coord = GRADEMasterCoordinator()
    dossier = coord.audit_case({"case_id": "TEST-100", "metric_primary": 10.0, "metric_secondary": 2.0})
    assert dossier["overall_status"] == "CONCORDANT_NORMAL"
    assert dossier["total_alerts"] == 0

    ans = coord.query_assistant("What are the guidelines?")
    assert "internal example thresholds" in ans


def test_cli():
    assert main(["audit", "--case-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_domain_registry():
    from grade_master import DomainKnowledgeRegistry
    assert DomainKnowledgeRegistry.ZERO_PHI_COMPLIANCE is False
    assert "PRO" in DomainKnowledgeRegistry.SYSTEM_VERSION

def test_advisory_is_not_reported_as_normal():
    coord = GRADEMasterCoordinator()
    dossier = coord.audit_case({"metric_primary": 5, "metric_secondary": 5, "status_text": "DISCORDANT"})
    assert dossier["overall_status"] == "ADVISORY_ACTIVE"


def test_csv_false_does_not_escalate_and_nonfinite_rejected():
    coord = GRADEMasterCoordinator()
    dossier = coord.audit_case({"metric_primary": "1", "metric_secondary": "2", "critical_flag": "False"})
    assert dossier["critical_count"] == 0
    with pytest.raises(ValueError):
        coord.audit_case({"metric_primary": float("nan")})
