"""Regression tests for explicit GRADE certainty calculations."""
import pytest

from grade_evidence_certainty_agent.certainty import CertaintyAssessment, assess_certainty


def test_randomized_starts_high():
    result = assess_certainty(CertaintyAssessment("randomized"))
    assert result["certainty"] == "HIGH"
    assert result["score"] == 4


def test_observational_starts_low():
    assert assess_certainty(CertaintyAssessment("observational"))["certainty"] == "LOW"


def test_downgrades_and_floor():
    moderate = assess_certainty(CertaintyAssessment("randomized", risk_of_bias=1))
    assert moderate["certainty"] == "MODERATE"
    assert assess_certainty(CertaintyAssessment(
        "randomized", risk_of_bias=2, inconsistency=2, imprecision=2
    ))["certainty"] == "VERY_LOW"


def test_upgrades_and_ceiling():
    result = assess_certainty(CertaintyAssessment(
        "observational", large_effect=2, dose_response=1
    ))
    assert result["certainty"] == "HIGH"
    assert result["upgrade_points"] == 3


@pytest.mark.parametrize("assessment", [
    CertaintyAssessment("unknown"),
    CertaintyAssessment("randomized", large_effect=1),
    CertaintyAssessment("observational", imprecision=1, large_effect=1),
    CertaintyAssessment("randomized", imprecision=-1),
    CertaintyAssessment("randomized", risk_of_bias=3),
    CertaintyAssessment("observational", dose_response=2),
    CertaintyAssessment("randomized", risk_of_bias=True),
    CertaintyAssessment("randomized", inconsistency=1.0),
])
def test_invalid_judgments_rejected(assessment):
    with pytest.raises(ValueError):
        assess_certainty(assessment)

def test_package_cli_grade(capsys):
    import json
    from grade_evidence_certainty_agent.cli import main
    assert main(["grade", "--design", "randomized", "--risk-of-bias", "1"]) == 0
    assert json.loads(capsys.readouterr().out)["certainty"] == "MODERATE"
    assert main(["grade", "--design", "randomized", "--large-effect", "1"]) == 2


def test_legacy_csv_boolean_parsing():
    from grade_evidence_certainty_agent.cli import _csv_bool
    assert _csv_bool("False") is False
    assert _csv_bool("TRUE") is True
    assert _csv_bool("0") is False
    with pytest.raises(ValueError):
        _csv_bool("maybe")


def test_legacy_model_rejects_nonfinite_and_nonboolean():
    from grade_evidence_certainty_agent.models import ClinicalCasePayload
    template = dict(case_id="a", patient_synthetic_id="synthetic", primary_metric=1.0,
                    secondary_metric=0.0, status_flag="NOMINAL")
    with pytest.raises(ValueError):
        ClinicalCasePayload(**{**template, "primary_metric": float("nan")})
    with pytest.raises(ValueError):
        ClinicalCasePayload(**{**template, "is_stat": "False"})


def test_grade_api_validates_upgrade_rules():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    assert client.post("/api/grade", json={"study_design": "randomized"}).json()["certainty"] == "HIGH"
    assert client.post("/api/grade", json={"study_design": "randomized", "large_effect": 1}).status_code == 422
    assert client.post("/api/grade", json={"study_design": "observational", "risk_of_bias": -1}).status_code == 422
