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
