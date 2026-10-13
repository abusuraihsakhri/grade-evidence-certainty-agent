"use strict";

const DOWNGRADE_DOMAINS = ["risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias"];
const UPGRADE_DOMAINS = ["large_effect", "dose_response", "plausible_confounding"];
const CERTAINTY_LEVELS = ["", "Very low", "Low", "Moderate", "High"];

function calculateGRADE(input) {
  const design = input.study_design;
  if (!["randomized", "observational"].includes(design)) {
    throw new Error("Select a valid study design.");
  }
  const judgments = {};
  for (const key of [...DOWNGRADE_DOMAINS, ...UPGRADE_DOMAINS]) {
    const value = input[key] === undefined ? 0 : input[key];
    const max = (DOWNGRADE_DOMAINS.includes(key) || key === "large_effect") ? 2 : 1;
    if (!Number.isInteger(value) || value < 0 || value > max) {
      throw new Error(`${key.replaceAll("_", " ")} must be an integer from 0 to ${max}.`);
    }
    judgments[key] = value;
  }
  const downgrades = DOWNGRADE_DOMAINS.reduce((n, key) => n + judgments[key], 0);
  const upgrades = UPGRADE_DOMAINS.reduce((n, key) => n + judgments[key], 0);
  if (upgrades > 0 && (design !== "observational" || downgrades > 0)) {
    throw new Error("Upgrades require low-start observational evidence without downgrades.");
  }
  const startingScore = design === "randomized" ? 4 : 2;
  const score = Math.max(1, Math.min(4, startingScore - downgrades + upgrades));
  return {
    study_design: design,
    starting_certainty: CERTAINTY_LEVELS[startingScore].toUpperCase().replaceAll(" ", "_"),
    certainty: CERTAINTY_LEVELS[score].toUpperCase().replaceAll(" ", "_"),
    score,
    downgrade_points: downgrades,
    upgrade_points: upgrades,
    judgments,
    method: "Conventional GRADE for intervention outcomes; assessor-entered judgments",
    caution: "Requires methodological review; not a validated automatic evidence appraisal or treatment recommendation."
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { calculateGRADE };
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("assessment-form");
    const output = document.getElementById("result");
    const error = document.getElementById("error");
    const gradeTitle = document.getElementById("grade-title");
    const detail = document.getElementById("grade-detail");
    const eligibility = document.getElementById("upgrade-eligibility");
    const download = document.getElementById("download");
    const reset = document.getElementById("reset-form");
    let lastAssessment = null;

    function inputValues() {
      const values = { study_design: document.getElementById("study_design").value };
      for (const key of [...DOWNGRADE_DOMAINS, ...UPGRADE_DOMAINS]) {
        values[key] = Number(document.getElementById(key).value);
      }
      return values;
    }

    function updateUpgradeEligibility() {
      const data = inputValues();
      const totalDown = DOWNGRADE_DOMAINS.reduce((n, key) => n + data[key], 0);
      const enabled = data.study_design === "observational" && totalDown === 0;
      for (const key of UPGRADE_DOMAINS) {
        const control = document.getElementById(key);
        if (!enabled) control.value = "0";
        control.disabled = !enabled;
      }
      eligibility.textContent = enabled
        ? "Upgrading may be considered for credible, reviewer-justified factors."
        : "Upgrading is unavailable for randomized evidence or evidence already downgraded.";
    }

    form.addEventListener("change", () => {
      updateUpgradeEligibility();
      lastAssessment = null;
      download.disabled = true;
      output.hidden = true;
      error.textContent = "";
    });

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      error.textContent = "";
      try {
        const result = calculateGRADE(inputValues());
        const outcome = document.getElementById("outcome").value.trim();
        lastAssessment = { outcome, ...result };
        gradeTitle.textContent = CERTAINTY_LEVELS[result.score] + " certainty";
        detail.textContent = `Starting: ${result.starting_certainty.replaceAll("_", " ")} · Downgrade: −${result.downgrade_points} · Upgrade: +${result.upgrade_points} · Final: ${result.score}/4`;
        output.hidden = false;
        download.disabled = false;
      } catch (exc) {
        lastAssessment = null;
        output.hidden = true;
        download.disabled = true;
        error.textContent = exc.message;
      }
    });

    download.addEventListener("click", () => {
      if (!lastAssessment) return;
      const data = new Blob([JSON.stringify(lastAssessment, null, 2) + "\n"], { type: "application/json" });
      const url = URL.createObjectURL(data);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "grade-certainty-assessment.json";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    });

    reset.addEventListener("click", () => {
      form.reset();
      updateUpgradeEligibility();
      lastAssessment = null;
      error.textContent = "";
      output.hidden = true;
      download.disabled = true;
    });
    updateUpgradeEligibility();
  });
}
