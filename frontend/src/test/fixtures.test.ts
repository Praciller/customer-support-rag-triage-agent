import { describe, expect, it } from "vitest";

import { makeEvaluation, makeTriageResult } from "./fixtures";

describe("deterministic Storybook fixtures", () => {
  it("accepts shallow typed triage overrides", () => {
    const result = makeTriageResult({ grounded: false, next_action: "manual_review" });

    expect(result.grounded).toBe(false);
    expect(result.next_action).toBe("manual_review");
    expect(result.trace).toHaveLength(7);
  });

  it("accepts shallow typed evaluation overrides", () => {
    const evaluation = makeEvaluation({ evaluation_mode: "deterministic_mock_story" });

    expect(evaluation.evaluation_mode).toBe("deterministic_mock_story");
    expect(evaluation.limitations).toEqual(["Small deterministic fixture; not a production SLA."]);
  });
});
