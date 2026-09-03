# Deployment and Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement repository-owned verification/doc work task-by-task. Owner-authenticated Hugging Face deployment is a stop-and-handoff step rather than a reason to expose credentials.

**Goal:** Verify the hardened revision on the existing free CPU deployment path, capture reproducible desktop/mobile evidence, and synchronize recruiter-facing documentation only from observed behavior.

**Architecture:** Prove the repository-defined single-container build locally first, then deploy the exact reviewed revision to the separate Hugging Face Space using its existing manual synchronization path. Record GitHub/Space revisions and smoke evidence before refreshing screenshots/README claims.

**Tech Stack:** Docker, FastAPI, React build, Hugging Face Spaces Docker CPU, Playwright/browser verification, Git/GitHub.

**Spec:** `docs/superpowers/specs/2026-09-03-sdlc-professional-hardening-design.md`

## Global Constraints

- `Dockerfile.hf` remains the canonical repository-side single-container production build unless a verified deployment failure requires a separately reviewed change.
- No external LLM secret is required for demo mode.
- Do not claim deployment success from image build alone.
- Do not place Hugging Face tokens or any credential in source, prompts, screenshots, logs, or issue/PR bodies.
- The Space is a separate Git repository; GitHub push alone does not prove Space synchronization.
- Metrics/grounding claims remain deterministic-fixture results, not production SLA/policy-quality claims.

---

### Task 1: Establish final candidate verification baseline

**Files:**
- No source changes.
- Read: `docs/deployment.md`, `docs/runbook.md`, `README.md`, `.github/workflows/ci.yml`.

**Interfaces:**
- Produces the candidate Git commit SHA used by every later verification record.

- [ ] **Step 1: Require clean candidate checkout**

```bash
git status --short
git rev-parse HEAD
```

Expected: no uncommitted runtime changes; save the full HEAD SHA in working notes.

- [ ] **Step 2: Run complete repository quality matrix**

Backend:

```bash
ruff check src tests
ruff format --check src tests
python -m pytest
python -m src.evaluation.evaluate_adversarial_retrieval --report-path /tmp/adversarial_retrieval.md
make demo
```

Frontend:

```bash
cd frontend
npm ci
npm run lint
npm test
npm run build
npm run build-storybook
npm run test:e2e
```

Expected: all PASS. If a command is unavailable because a prior phase was not merged, stop; do not weaken the matrix.

- [ ] **Step 3: Confirm GitHub Actions for the candidate**

After pushing the focused implementation PR, confirm backend/frontend/browser jobs all pass for the exact candidate SHA. Record job URLs/revision in PR evidence; do not substitute a local pass for CI evidence.

---

### Task 2: Prove the canonical Hugging Face container locally

**Files:**
- No expected source changes.

**Interfaces:**
- Container image tag: `support-rag-hf`.
- Local port: `7860`.

- [ ] **Step 1: Build canonical image**

```powershell
docker build -f Dockerfile.hf -t support-rag-hf .
```

Expected: image build succeeds from the candidate revision.

- [ ] **Step 2: Run container without external secrets**

```powershell
docker run --rm -p 7860:7860 support-rag-hf
```

Keep this terminal running for smoke verification.

- [ ] **Step 3: Verify readiness**

```powershell
Invoke-RestMethod http://localhost:7860/ready
```

Expected: HTTP 200/ready, demo mode active, bounded fixture indexed.

- [ ] **Step 4: Verify representative triage**

```powershell
Invoke-RestMethod http://localhost:7860/triage -Method Post `
  -ContentType application/json `
  -Body '{"message":"My card has not arrived","top_k":5}'
```

Required assertions from returned JSON:
- request succeeds;
- `trace.Count -eq 7`;
- retrieved cases are non-empty for the fixture;
- final result is not degraded;
- grounding/manual-review semantics match the returned evidence state.

Do not hard-code an old latency or grounding score as a deployment pass condition.

- [ ] **Step 5: Verify public ingestion remains protected**

Call the public ingestion route without admin credentials using the documented API shape. Expected: access denied (currently HTTP 403). If the endpoint contract changed intentionally, use the current security doc/API tests as source of truth.

- [ ] **Step 6: Stop container and record local proof**

Record candidate SHA, build PASS, readiness PASS, triage 7/7 trace PASS, ingestion protection PASS. Do not commit terminal logs containing local paths/environment dumps.

---

### Task 3: Prepare exact reviewed Space synchronization artifact

**Files:**
- Generate locally, do not commit: `app.tar.gz`.
- Read: `deploy/huggingface/Dockerfile.bundle`.

**Interfaces:**
- Artifact is built from exact reviewed GitHub HEAD.

- [ ] **Step 1: Generate reproducible archive from candidate**

```powershell
git archive --format=tar.gz --output=app.tar.gz HEAD src frontend prompts data/demo data/eval reports/evaluation requirements.production.txt
```

- [ ] **Step 2: Record archive checksum**

PowerShell:

```powershell
Get-FileHash .\app.tar.gz -Algorithm SHA256
```

Record checksum in deployment working notes/PR evidence; do not commit the bundle unless the existing deployment workflow specifically requires it.

- [ ] **Step 3: Verify bundle Dockerfile path**

Inspect `deploy/huggingface/Dockerfile.bundle`; confirm it consumes `app.tar.gz` and still represents the canonical `Dockerfile.hf` runtime behavior. If materially divergent, stop and reconcile in a separate reviewed deployment change.

- [ ] **Step 4: Owner-authenticated deployment handoff**

At this point, if Hugging Face authentication is not already available in the execution environment, stop and hand off these exact actions to the owner/Codex session with authorized credentials:
1. update the existing Space from the exact candidate archive or clone/copy path documented in `docs/deployment.md`;
2. never paste a token into source or chat output;
3. wait for Space build/runtime healthy state;
4. return the new Space revision SHA and public URL only.

No GitHub-side workaround substitutes for this authenticated Space operation.

---

### Task 4: Verify the live Space revision independently

**Files:**
- No source changes yet.

**Interfaces:**
- Public URL remains the Space URL documented in `docs/deployment.md` unless the owner explicitly changed it.

- [ ] **Step 1: Record exact synchronized revisions**

Record:
- GitHub candidate SHA;
- Hugging Face Space revision SHA returned after deployment;
- verification timestamp with timezone.

- [ ] **Step 2: Verify public readiness**

```powershell
Invoke-RestMethod https://pracill-customer-support-rag-triage-agent.hf.space/ready
```

Expected: ready response; no credential required.

- [ ] **Step 3: Verify live representative triage**

```powershell
Invoke-RestMethod https://pracill-customer-support-rag-triage-agent.hf.space/triage -Method Post `
  -ContentType application/json `
  -Body '{"message":"My card has not arrived","top_k":5}'
```

Assert seven trace nodes and reviewable decision/evidence semantics. Record observed retrieval count, grounding/manual-review state, next action, fallback/degraded flags. Treat latency as observation, not SLA.

- [ ] **Step 4: Verify evaluation endpoint/UI**

Confirm the deterministic evaluation view renders its methodology/limitations and values matching the committed evaluation artifact for the deployed candidate. If regenerated metrics changed, update claims from the new committed report before screenshots.

- [ ] **Step 5: Verify protected ingestion and provider-health secrecy**

Confirm unauthenticated public ingestion remains denied. Confirm provider-health/public UI exposes operational state but not endpoint credentials, API keys, raw environment values, or local paths.

---

### Task 5: Capture deployed desktop/mobile browser evidence

**Files:**
- Update only approved screenshots under `docs/screenshots/`.

**Interfaces:**
- Screenshots must come from the verified live Space revision from Task 4.

- [ ] **Step 1: Run deployed browser smoke at 1440px**

Use browser/Playwright against the public Space:
- load triage workspace;
- select `Card not arrived`;
- run triage;
- inspect decision, evidence, grounding, next action, seven-node trace;
- inspect browser console for errors/warnings attributable to the app.

- [ ] **Step 2: Run deployed browser smoke at 390px**

Viewport: 390x844. Assert no page-level horizontal overflow and decision appears before detailed evidence/trace. Repeat evaluation view overflow check.

- [ ] **Step 3: Capture high-signal screenshots**

At minimum refresh:
- triage result;
- workflow trace;
- evaluation;
- one representative mobile state if current documentation uses mobile evidence.

Do not capture account browser chrome, tokens, private bookmarks, local paths, or unrelated personal data.

- [ ] **Step 4: Compare screenshots to README references**

Ensure every image referenced by README exists and represents the current live revision. Remove stale screenshot references rather than preserving obsolete evidence.

- [ ] **Step 5: Commit evidence separately**

```bash
git add docs/screenshots
git commit -m "docs: refresh verified deployment screenshots"
```

---

### Task 6: Synchronize deployment docs, README, and portfolio claims

**Files:**
- Modify: `docs/deployment.md`
- Modify: `README.md`
- Modify: `PORTFOLIO_REVIEW.md` only if it contains stale implementation/deployment claims.
- Modify other docs only when a verified code/runtime change made them stale.

**Interfaces:**
- All numbers/revisions in public docs must be traceable to committed reports or Task 4 live observations.

- [ ] **Step 1: Replace old deployment verification block**

In `docs/deployment.md`, preserve historical context only if clearly labeled; add a new latest verification block containing candidate GitHub SHA, final Space SHA, timestamp, readiness, representative triage observations, evaluation artifact reference, desktop/mobile result, and known limitations.

- [ ] **Step 2: Update README recruiter path from actual final UI**

Keep the concise reviewer path. Update screenshot references and testing commands to include Storybook/Playwright. Do not inflate deterministic fixture metrics into production claims.

- [ ] **Step 3: Perform claim scan**

Run:

```bash
python - <<'PY'
from pathlib import Path
paths = [Path('README.md'), Path('PORTFOLIO_REVIEW.md'), Path('docs/deployment.md')]
text = '\n'.join(p.read_text(encoding='utf-8') for p in paths if p.exists()).lower()
for risky in ['production sla', 'prompt injection proof', 'fully autonomous support', 'guaranteed policy']:
    assert risky not in text, risky
print('public claim scan OK')
PY
```

Expected: `public claim scan OK`.

- [ ] **Step 4: Run complete regression after docs/evidence refresh**

```bash
ruff check src tests
ruff format --check src tests
python -m pytest
cd frontend
npm run lint
npm test
npm run build
npm run build-storybook
npm run test:e2e
```

Expected: PASS.

- [ ] **Step 5: Commit documentation**

```bash
git add README.md docs/deployment.md PORTFOLIO_REVIEW.md
git commit -m "docs: record verified hardened deployment"
```

---

### Task 7: Final security, QA, and rollback review

**Files:**
- Update: `docs/runbook.md` only if final deployment/recovery steps changed.
- Optional create: a concise final verification record only if the repository already has an appropriate reports/docs convention; do not add a vanity report solely to increase artifact count.

- [ ] **Step 1: Re-run adversarial evidence-boundary report**

```bash
python -m src.evaluation.evaluate_adversarial_retrieval --report-path reports/evaluation/adversarial_retrieval.md
```

Review resulting diff. Commit only if deterministic report legitimately changes for the final code.

- [ ] **Step 2: Security review**

Check:
- no frontend secrets;
- no raw prompts/evidence dumped to public trace;
- degraded/ungrounded paths remain manual-review-safe;
- citation integrity semantics preserved;
- public errors controlled;
- screenshots/docs contain no secret/private content.

- [ ] **Step 3: Rollback proof**

Record the immediately previous verified Space revision and the repository/Space procedure to restore it. Do not perform rollback unless verification finds a real regression.

- [ ] **Step 4: Final review matrix**

Produce PR summary evidence in this shape:

```text
Backend lint/format: PASS|FAIL
Backend pytest: PASS|FAIL
Adversarial evidence boundary: PASS|FAIL
Deterministic evaluation: PASS|FAIL
Frontend lint/unit/build: PASS|FAIL
Storybook static build: PASS|FAIL
Playwright E2E: PASS|FAIL
Visual regression: PASS|FAIL
GitHub Actions: PASS|FAIL
Local HF container: PASS|FAIL
Live /ready: PASS|FAIL
Live triage 7/7 trace: PASS|FAIL
Desktop 1440: PASS|FAIL
Mobile 390 overflow: PASS|FAIL
Security/claim review: PASS|FAIL
Known limitations: <evidence-based concise text>
```

Do not mark the program complete while any required line is FAIL or unverified without explicitly classifying the result as limited/blocked.

---

## Program completion gate

The hardening program is complete only when the focused implementation PRs are merged, final CI is green, the exact merged revision is deployed/verified on the Space, screenshots/docs match that revision, and the security/claim review has no unresolved high-severity finding.