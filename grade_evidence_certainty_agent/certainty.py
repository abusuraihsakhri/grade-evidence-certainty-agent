"""Transparent, reviewer-entered GRADE certainty ratings for intervention outcomes.

This calculator does not infer domain judgments from effect estimates and does not
produce treatment recommendations. The starting levels implement the conventional
high-start RCT / low-start non-randomized intervention approach, not ROBINS-I.
"""
from dataclasses import dataclass
from typing import Dict

DOWNGRADE_DOMAINS = ("risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias")
UPGRADE_DOMAINS = ("large_effect", "dose_response", "plausible_confounding")
LEVELS = {1: "VERY_LOW", 2: "LOW", 3: "MODERATE", 4: "HIGH"}


@dataclass(frozen=True)
class CertaintyAssessment:
    study_design: str
    risk_of_bias: int = 0
    inconsistency: int = 0
    indirectness: int = 0
    imprecision: int = 0
    publication_bias: int = 0
    large_effect: int = 0
    dose_response: int = 0
    plausible_confounding: int = 0


def assess_certainty(assessment: CertaintyAssessment) -> Dict[str, object]:
    """Calculate a per-outcome GRADE rating from explicit assessor judgments.

    Downgrades: 0=no concern, 1=serious, 2=very serious.
    Upgrades: large effect 0-2; credible dose-response and opposing residual
    confounding 0-1. Upgrades are accepted only in the conventional low-start
    non-randomized approach without any downgrades.
    """
    if assessment.study_design not in ("randomized", "observational"):
        raise ValueError("study_design must be 'randomized' or 'observational'")

    ratings = {key: getattr(assessment, key) for key in DOWNGRADE_DOMAINS + UPGRADE_DOMAINS}
    for name, value in ratings.items():
        maximum = 2 if name in DOWNGRADE_DOMAINS or name == "large_effect" else 1
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError(f"{name} must be an integer between 0 and {maximum}")

    downgrades = sum(ratings[k] for k in DOWNGRADE_DOMAINS)
    upgrades = sum(ratings[k] for k in UPGRADE_DOMAINS)
    if upgrades and (assessment.study_design != "observational" or downgrades):
        raise ValueError("Upgrades require low-start observational evidence without downgrades")

    starting_score = 4 if assessment.study_design == "randomized" else 2
    final_score = max(1, min(4, starting_score - downgrades + upgrades))
    return {
        "study_design": assessment.study_design,
        "starting_certainty": LEVELS[starting_score],
        "certainty": LEVELS[final_score],
        "score": final_score,
        "downgrade_points": downgrades,
        "upgrade_points": upgrades,
        "judgments": ratings,
        "method": "Conventional GRADE for intervention outcomes; assessor-entered judgments",
        "caution": "Requires methodological review; not a validated automatic evidence appraisal or treatment recommendation.",
    }
