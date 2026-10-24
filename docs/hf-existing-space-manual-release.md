# Manual release to the existing Hugging Face Space

**Status: manual dry-run available; no automatic deployment.**

This applies only to the EXISTING free-hardware Space
[Pracill/customer-support-rag-triage-agent](https://huggingface.co/spaces/Pracill/customer-support-rag-triage-agent).
Do **not** create, duplicate, move, upgrade or delete a Space. Do not
assume an existing Docker Space is entitled to rebuild simply because
CPU Basic costs $0/hour: official documentation now requires PRO for
creating most compute-based Docker Spaces. The historical free-account
Space is currently grandfathered/running, but its future ability to
rebuild without a subscription is **not verified**.

## One-time, owner-only setup

1. Open the **existing Space → Settings → Trusted Publishers**
   at [Space settings](https://huggingface.co/spaces/Pracill/customer-support-rag-triage-agent/settings).
   Only the authenticated owner with Write access may configure it.
2. Add **GitHub Actions** repository publisher; restrict these exact claims:
   - GitHub repository: `Praciller/customer-support-rag-triage-agent`
   - Branch: `main`
   - Workflow: `manual-hf-space-release.yml`
   - Resource: `spaces/Pracill/customer-support-rag-triage-agent`
3. Do **not** use the account-wide CI/CD identity: it is read-only.
   Do **not** create or paste an unrestricted `HF_TOKEN` in workflow
   YAML, GitHub logs, or user-visible chats.
4. Verify with Hugging Face billing/account support or explicit Space
   interface confirmation that **updating/rebuilding this EXISTING Space**
   remains allowed without subscribing or payment. If uncertain, **HOLD**.
   The current OAuth app has read-only scopes and cannot attest this.

The repo-specific publisher exchanges GitHub OIDC for a one-hour,
Space-scoped write token only when the **deploy** path is invoked.
The workflow cannot configure the publisher for the owner.

## Run the dry-run (recommended first)

From [Actions](https://github.com/Praciller/customer-support-rag-triage-agent/actions):
choose **Manual existing Hugging Face Space release → Run workflow**,
branch `main`, mode `dry-run`, and the independently verified current
40-character Space revision (was
`a2661562ff1a2a7b7f15e4b9145cb007c98444a5` as of 2026-10-24).

The workflow checks exact Space identity/SHA, `RUNNING`, Docker,
`cpu-basic`, and no requested paid hardware. It packages only
git-tracked source, the review Dockerfile, and a public provenance
manifest into a **deterministic bundle**; builds the exact release image,
audits installed package vulnerabilities, then runs the synthetic
27-record / 8-evaluation / 7-node grounding and ingestion-denial
smoke test. In `dry-run`, **no Hugging Face write or paid job occurs**.

A dry-run pass is not permission to deploy and does not prove existing
Space rebuild entitlement or human accessibility sign-off.

## Owner-approved deploy (only after free-tier check)

From the same workflow on `main`, choose `deploy`, supply the
current exact Space SHA, and type this entire phrase:

`CONFIRM_EXISTING_CPU_BASIC_NO_CHARGE`

All of the following are mandatory before the write step:

- Verified no-charge existing-Space rebuild eligibility
- Repo-scoped Hugging Face Trusted Publisher configured
- Exact current Space SHA and reviewed GitHub `main`
- All five repository CI checks passed on exact source SHA
- Review that intended release has only synthetic demo data and no
  public ingestion

The workflow invokes `HfApi.create_commit` for an **already existing**
Space, with `parent_commit` equal to the independently supplied
previous SHA. It is exactly **one commit**, only changing `Dockerfile`,
`README.md`, `app.tar.gz`, and `release-manifest.json`.
The existing `.gitattributes` is preserved.

After the commit, it checks the new immutable Space revision, public
release manifest (GitHub source SHA and bundle digest), `RUNNING` on
`cpu-basic`, and a synthetic live ONNX triage smoke. Any failure should
be treated as an **incomplete release** requiring owner review; no
automatic rollback or hardware change is performed.

The downloadable (nonsecret) GitHub Actions evidence artifact includes
the source manifest and, for deployed runs, the previous/new Space SHA.
Do **not** expose authorization tokens.

## Rollback and accessibility sign-off

The previous Space revision is saved in the deployment evidence. To
restore a previous state, an authorized owner must review and explicitly
approve a rollback that restores the prior `Dockerfile`,
`README.md`, and `app.tar.gz` from that immutable revision. Delete
`release-manifest.json` when rolling back to the original 3-file
bundle; preserve `.gitattributes`. The rollback must be a new,
parent-locked commit, followed by live health tests. **Do not merely
switch the GitHub source SHA**: Hub Space history and deployed image
are separate. Be aware that restoring the old FastEmbed image would
also restore its *historically vulnerable Pillow dependency*.

Before publicly calling this release production-ready, have a human
check the live app with keyboard-only navigation, NVDA or Narrator,
200% browser zoom, layouts at 390/768/1440 widths, real focus order,
dialog/validation announcements, loading/error/degraded states, contrast
and no overlapping/overflowing text. Automated Storybook/axe tests
do **not** replace that review. Record signed evidence in
[Issue #89](https://github.com/Praciller/customer-support-rag-triage-agent/issues/89).

## Official references

- [Hugging Face Trusted Publishers](https://huggingface.co/docs/hub/trusted-publishers)
- [CPU Basic and compute Space creation policy](https://huggingface.co/docs/hub/spaces-overview)
- [Parent-locked Hub commits](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api)
