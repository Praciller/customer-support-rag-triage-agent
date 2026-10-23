# Local FastEmbed release-image smoke — October 24, 2026

**Scope:** Tested the local canonical Hugging Face Dockerfile.hf with actual FastEmbed/ONNX CPU rather than the hashing CI shortcut. This is **not** a live Hugging Face deployment or vulnerability exception.

## Reproduce (Docker Desktop and public synthetic fixtures only)

    docker build -f Dockerfile.hf -t csrta-fastembed-audit:local .
    docker run --detach --rm --name csrta-fastembed-audit --publish 127.0.0.1:17860:7860 --memory 3g --cpus 2 csrta-fastembed-audit:local
    # After bounded model download and startup:
    python scripts/verify_local_fastembed.py
    docker exec csrta-fastembed-audit python -m pip check
    docker rm --force csrta-fastembed-audit
    docker image rm csrta-fastembed-audit:local

The new script permits only loopback HTTP origins (127.0.0.1 or localhost). It reads /ready, /provider-health, /dataset-info and /eval/results; sends one *fixed synthetic* /triage request; and only after checking the public ingestion setting is explicitly false, sends an unauthenticated /ingest probe requiring HTTP 403. No token, real ticket, arbitrary remote URL, model-provider bill, or ingestion write.

Eight offline regression tests in tests/test_local_fastembed_smoke.py verify correct behavior and failure on hashing mode, enabled public ingestion, missing records, incomplete trace, unexpected ingest success, evaluation drift, and non-loopback URLs. Automated GitHub docker-smoke still uses hashing: this optional local test is deliberately distinct and downloads public FastEmbed model files.

## Observed evidence on Windows pracill

- Exact GitHub source baseline: 6f7ba9c016b0babb64fbf0dfb8bfa8e7aeafbb06. No source edits were required to build and run the canonical Dockerfile.
- **Local** image ID: sha256:6c7ed9bd9776bd324e0beeb02138fa81d594bd2d99afca6955c259e0af66c7c6. This is not a Space or registry digest.
- Resolved: fastembed 0.9.0, Pillow 12.3.0, onnxruntime 1.31.0, datasets 5.1.0, fsspec 2026.7.0.
- pip check: No broken requirements found. Non-root runtime: uid 1000. Bound resources: 2 CPUs, 3 GiB limit; one sampled idle memory usage approximately 357 MiB (not a peak benchmark).
- Five public model files downloaded with no Hugging Face token. Application startup completed. Frontend GET / returned HTTP 200.
- Local smoke: **PASS**; 27/27 indexed, embedding_provider fastembed, model BAAI/bge-small-en-v1.5, mock inference, seven triage trace stages, grounded true, citation_integrity true, next_action ask_for_order_id, eight synthetic evaluation records, and unauthorized /ingest HTTP 403.
- Eight new offline regression cases passed.

## Unsatisfied release/security gates

**Pillow 12.3.0 is still installed** and has outstanding advisories; pip check checks dependency metadata, **not CVEs**. This proof of runtime functionality is not proof of safe Pillow image-decoding reachability or a strict clean vulnerability audit. Issue #93 remains open until a **released, supported** FastEmbed dependency graph is available and audited.

The Space is still an independent repository. A local Docker image cannot establish reviewed GitHub-to-Space source provenance, deployed image identity, live accessibility, owner-authorized rollback, or permission to deploy. Issue #89 remains open. No production deployment, paid service, or secrets change was performed.
