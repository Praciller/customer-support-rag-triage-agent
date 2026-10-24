# Hugging Face live-Space preflight — October 23, 2026

This is a **non-deploying, public-surface observation** of the existing
[CPU-basic Docker Space](https://huggingface.co/spaces/Pracill/customer-support-rag-triage-agent).
It is **not a claim** that the current GitHub `main` commit is deployed.

## Observed live revision and runtime

| Check | Observed result |
| --- | --- |
| Hub repo | `Pracill/customer-support-rag-triage-agent` |
| Space Git SHA | `a2661562ff1a2a7b7f15e4b9145cb007c98444a5` |
| Runtime | `RUNNING`, `cpu-basic` |
| GitHub `main` at inspection | `e3be748541b8d6b86af664a233134ecd9e069d6b` |
| Current-source deployment | **Not performed**, revision/source mapping still missing |

These SHAs are different repositories; **do not compare SHAs for equality**
to establish build provenance. The Space revision corresponds to the
September 2026 deployment documented in `docs/deployment.md`.
Do not substitute a current GitHub CI pass for a Space release attestation.

## Synthetic live smoke evidence

- `GET /ready`: HTTP 200, ready, 27/27 bounded records indexed.
- `GET /provider-health`: HTTP 200, demo/mock enabled, public ingestion disabled.
- `GET /eval/results`: HTTP 200, deterministic mock evaluation, 8 labeled
  fixture tickets, Precision@5 `0.375`. These are **not live support-policy metrics**.
- `POST /triage`: HTTP 200 for a fixed synthetic delayed-card message; seven
  trace nodes, `ask_for_order_id`, grounded. No real customer data used.
- An **explicitly unauthenticated** `POST /ingest` returned HTTP 403 in this
  one manual test, after the public provider-health route reported ingestion
  disabled. The repeatable script deliberately does **not** attempt ingestion:
  a misconfigured endpoint must never be mutated by an automated preflight.

## Reproduce safely

Requires only Python standard library and public internet access:

```powershell
python scripts/verify_live_space.py
python scripts/verify_live_space.py --triage --expected-space-sha a2661562ff1a2a7b7f15e4b9145cb007c98444a5
```

The first command makes only GET requests. The second additionally sends
one **fixed synthetic** triage request and confirms the supplied Space
revision is stable before and after testing. Both fail closed on unexpected
index count, provider/ingestion mode, evaluation mode, or revision drift.
Output includes exact Space revision, never a GitHub release-mapping claim.
The script cannot prove a source-bundle checksum, image digest, WCAG coverage,
secrets safety, or user-facing UI identity.

## Remaining owner-gated release checks

1. Obtain authorized write-capable Space deployment access; never assume
   the connected read-only OAuth scope permits pushing a release.
2. Obtain explicit approval for [PR #97](https://github.com/Praciller/customer-support-rag-triage-agent/pull/97)
   screenshot baseline candidates and complete its exact-head CI gate
   before considering a merge.
3. Resolve or explicitly review [Pillow/FastEmbed risk #93](https://github.com/Praciller/customer-support-rag-triage-agent/issues/93).
   A green frontend audit and reporting-only Python scan are not an all-clear.
4. Record immutable reviewed GitHub SHA, reproducible source bundle checksum,
   resulting Space SHA/image revision, deploy time and tested rollback target.
5. After the actual deployment, repeat live API smoke, **verify UI identity**
   at 390/768/1440 pixels, keyboard flow, console health, real zoom and
   screen-reader accessibility, then update screenshots and portfolio evidence.

[Slice F tracking issue #89](https://github.com/Praciller/customer-support-rag-triage-agent/issues/89)
remains open. No Space deployment, secrets mutation or paid resource was made.


## Reverification — October 24, 2026 (no deployment)

The existing read-only Hub metadata and public demo endpoints were queried
again using `python scripts/verify_live_space.py --triage
--expected-space-sha a2661562ff1a2a7b7f15e4b9145cb007c98444a5`.
Result: **PASS** for the historical Space SHA `a2661562...`, `RUNNING`
on `cpu-basic`, demo/mock provider with FastEmbed BGE-small, 27/27
indexed synthetic records, deterministic eight-ticket evaluation, and a
single synthetic `ask_for_order_id` triage. The synthetic response had
exactly the seven ordered, completed workflow nodes, `grounded=true`,
`citation_integrity=true`, and `fallback_used=false`/
`degraded_mode=false`. No `/ingest` mutation or privileged call was sent.

The hardened preflight uses no ambient proxy and refuses HTTP redirects.
It verifies explicit FastEmbed/model/local-Qdrant/mock/no-live-provider
settings before running the optional synthetic triage. The opt-in triage
path additionally checks ordered stage names/status and evidence grounding,
not merely trace length; four additional offline regression cases cover
fail-closed behavior and a two-server redirect probe.

**Release boundary unchanged:** this is a read of the older Space only.
GitHub `main` is a **different Git repository**, and no source-bundle/
image-digest mapping, new Space deployment, security waiver, manual
screen-reader review, or rollback rehearsal is attested. The Python
FastEmbed/Pillow 13 version conflict remains unresolved; owner closure of
Issue #93 does not repair the transitive vulnerability findings.
