# Production Python dependency advisory gate

**Status (2026-10-24): Release blocked. No risk waiver.**

The project's FastEmbed 0.9.0 resolver currently requires Pillow below 13 on
Python 3.12. The available fixed Pillow 13 does **not** satisfy that upstream
constraint. Never use `--no-deps`, ignore the resolver, or silently replace
the embedding provider. The latest strict production audit yielded **37
advisory IDs in Pillow 12.3.0**, with no findings in other resolved packages
at the time of this scan. Advisory counts may increase as the database changes.

The tracked list in `security/python-advisory-baseline.json` is an **exact
identifier allowlist for CI regression detection only**, not an acceptance of
those vulnerabilities. GitHub CI now **fails** if another production package
acquires an advisory, if any **new** Pillow advisory ID appears, or if audit
output is missing/malformed. Old Pillow IDs are always printed as unresolved.
This check does not make CI or the deployed Space advisory-free.

**Reproduce with Python 3.12 and network access:**

```sh
python -m pip install pip-audit==2.10.1
python -m pip_audit --strict -r requirements.production.txt --format json --output python-audit.json
# pip-audit returns nonzero for vulnerabilities; do NOT ignore scan or parse failures.
python scripts/check_python_audit.py --report python-audit.json --baseline security/python-advisory-baseline.json
# Strict release gate: must return 0 with ZERO known or novel vulnerabilities.
python scripts/check_python_audit.py --report python-audit.json --baseline security/python-advisory-baseline.json --require-clean
```

**Before actual Hugging Face release:** first obtain a **published, supported**
FastEmbed / Pillow 13 dependency resolution or separately approved,
time-bounded security decision. Run a strict audit against the **exact image
packages**, run FastEmbed model/27-record/seven-node retrieval and citation
checks, and document image/source provenance, live Space revision, rollback,
and human accessibility review. Do not confuse the existing historical Space
smoke test with newly built release evidence.

See [Issue #89](https://github.com/Praciller/customer-support-rag-triage-agent/issues/89)
and [Issue #93](https://github.com/Praciller/customer-support-rag-triage-agent/issues/93).
