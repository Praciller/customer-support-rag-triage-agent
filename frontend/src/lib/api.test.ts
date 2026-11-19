import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";
import { makeTriageResult } from "../test/fixtures";

afterEach(() => vi.unstubAllGlobals());

describe("triage release contract", () => {
  it("requests v2 explicitly and accepts a v2 decision", async () => {
    const result = makeTriageResult();
    const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(result)));
    vi.stubGlobal("fetch", fetch);
    expect(await api.triage("Synthetic test", 5)).toEqual(result);
    expect(fetch.mock.calls[0][1].headers["X-ResolveOps-API-Version"]).toBe("2");
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it.each([
    { grounded: true, grounding_score: 0.86 },
    null,
    {},
    { ...makeTriageResult(), grounded: true },
    { ...makeTriageResult(), proposal_checks: null },
  ])("rejects incompatible HTTP 200 payloads without retrying", async (payload) => {
    const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(payload)));
    vi.stubGlobal("fetch", fetch);
    await expect(api.triage("Synthetic test", 5)).rejects.toMatchObject({ status: 426 });
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("propagates a controlled upgrade response without retrying", async () => {
    const fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Reload the console" }), { status: 426 }),
    );
    vi.stubGlobal("fetch", fetch);
    await expect(api.triage("Synthetic test", 5)).rejects.toMatchObject({ status: 426 });
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("withholds a legacy evaluation report", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ groundedness_pass_rate: 1 })),
    ));
    await expect(api.evaluation()).rejects.toMatchObject({ status: 426 });
  });

  it("preserves an honest missing evaluation state", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: "not_evaluated" })),
    ));
    expect(await api.evaluation()).toEqual({ status: "not_evaluated" });
  });
});
