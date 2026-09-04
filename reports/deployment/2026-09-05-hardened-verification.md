# Hardened deployment verification

Verified 2026-09-05 ICT against `https://pracill-customer-support-rag-triage-agent.hf.space/`.

- Source GitHub SHA: `11df5035e3f4f96b78b21f5c1d993bb6d6deaaba`
- Space SHA: `a2661562ff1a2a7b7f15e4b9145cb007c98444a5`
- Previous healthy rollback SHA: `255b7272544c9222e1fde5351598779049615162`
- Bundle SHA256: `86eeb7f69fede2be2d2f7ba3cf65a98feb24e18e3fb6b0f484737ed8de9ab123`
- Runtime: RUNNING/READY on `cpu-basic`, 27 indexed records; root/health/ready HTTP 200
- Unauthenticated ingestion: HTTP 403

`Card not arrived` returned HTTP 200 with `delivery_issue`, `medium`,
`ask_for_order_id`, grounded true (score 0.86), citation integrity true, and
3 retrieved cases. Provider/model were `mock`/`deterministic-small`; fallback
and degraded mode were false. The exact seven-node order was normalize_message,
classify_intent, detect_urgency, retrieve_similar_cases,
generate_support_response, grounding_check, suggest_next_action.

Evaluation reported deterministic_mock, sample 8, corpus 27, top_k 5,
Precision@5 0.375, Recall@5 0.625, MRR 0.770833333333333, nDCG@5
0.610682485196436, intent accuracy/macro F1 1.0/1.0, urgency accuracy/macro
F1 1.0/1.0, and workflow success 1.0. The artifact states the fixture is
small/deterministic and not a production SLA.

Direct-live Playwright evidence passed at 1440x1000 and 390x844: no page
overflow, mobile decision → evidence → trace ordering, three-column desktop
Evaluation grid, and zero console errors, warnings, page errors, or failed
requests. Screenshots: `overview.png`, `triage-result.png`, `workflow-trace.png`,
`evaluation.png`, `mobile-triage.png`.

Screenshots were captured after verifying the Space SHA above, directly from
the live HF URL, with no localhost, Storybook, route interception, or fixture
injection.

Rollback target: `255b7272544c9222e1fde5351598779049615162`. In the Space repo:

```text
git revert a2661562ff1a2a7b7f15e4b9145cb007c98444a5
git push origin main
```

This preserves history and requires no force-push. This is not a production
support-quality or semantic prompt-injection-immunity claim.
