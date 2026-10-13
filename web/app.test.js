"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { calculateGRADE } = require("./app.js");

test("RCT starts high and one downgrade becomes moderate", () => {
  assert.equal(calculateGRADE({study_design: "randomized"}).certainty, "HIGH");
  assert.equal(calculateGRADE({study_design: "randomized", risk_of_bias: 1}).certainty, "MODERATE");
});

test("observational starts low and upgrading capped high", () => {
  assert.equal(calculateGRADE({study_design: "observational"}).certainty, "LOW");
  const result = calculateGRADE({study_design: "observational", large_effect: 2, dose_response: 1});
  assert.equal(result.certainty, "HIGH");
  assert.equal(result.upgrade_points, 3);
});

test("downgrading cannot go below very low", () => {
  assert.equal(calculateGRADE({
    study_design: "randomized", inconsistency: 2, imprecision: 2, risk_of_bias: 2
  }).certainty, "VERY_LOW");
});

test("reject invalid or ineligible ratings", () => {
  for (const payload of [
    {study_design: "other"},
    {study_design: "randomized", large_effect: 1},
    {study_design: "observational", risk_of_bias: 1, dose_response: 1},
    {study_design: "randomized", risk_of_bias: 3},
    {study_design: "randomized", risk_of_bias: -1},
    {study_design: "observational", plausible_confounding: 2},
    {study_design: "randomized", imprecision: 0.5},
    {study_design: "randomized", imprecision: true}
  ]) {
    assert.throws(() => calculateGRADE(payload));
  }
});

test("output is JSON-safe and uses explicit judgments", () => {
  const result = calculateGRADE({study_design: "randomized", publication_bias: 1});
  assert.equal(JSON.parse(JSON.stringify(result)).judgments.publication_bias, 1);
  assert.equal(result.downgrade_points, 1);
});
