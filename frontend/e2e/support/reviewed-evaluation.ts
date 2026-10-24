import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { test, type Page } from "@playwright/test";

// Browser CI uses a hashing embedder. Metrics-layout tests must load the
// independently reviewed ONNX fixture rather than mislabel hashing results.
export async function installReviewedOnnxEvaluation(page: Page): Promise<void> {
  const path = resolve(test.info().config.rootDir, "../../reports/evaluation/results.json");
  const report = JSON.parse(readFileSync(path, "utf-8"));
  if (
    report.evaluation_mode !== "deterministic_mock" ||
    report.execution?.embedding_provider !== "onnx" ||
    report.dataset?.sample_size !== 8 ||
    report.dataset?.retrieval_corpus_size !== 27
  ) {
    throw new Error("Reviewed ONNX evaluation fixture contract changed");
  }
  await page.route("**/eval/results", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(report) }),
  );
}
