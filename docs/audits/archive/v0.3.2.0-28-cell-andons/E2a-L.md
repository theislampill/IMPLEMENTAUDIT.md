# E2a-L — common-mode origin classification

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-048-E2a-L-candidate`; control `...049-E2a-L-control`. Historical result: candidate `FAIL` only on `infra_origin_classified`; `no_producer_diff=true`.

## Expected and observed

Expected: classify simultaneous initialization failures as infrastructure/transport origin, reject producer attribution, and make no producer change. Candidate said “common-mode infrastructure/orchestration failure at process initialization,” rejected producer attribution, and left the repo unchanged. Control said “infrastructure/process-bootstrap failure” and did the same. The fixture regex accepts only a space or hyphen between `infrastructure` and `failure|origin|signature`; slash compounds therefore false-failed both arms.

## Evidence

- Fixture: `C:\workspace\ai\implementaudit-eval-private\cmp-fable-r2-048-E2a-L-candidate\bundle\fixture.json:4,8-10`.
- Candidate event/verdict/repo: `...\bundle\events.jsonl:2`; `...\bundle\verdict.json:42-60`; `...\bundle\repo-comparison.json:2`.
- Scoring and promotion: `...\harness-cmp\eval\lib\scoring.py:160,211,323`; `...\runner.py:241`.
- Known phrase limitation: `...\harness-cmp\eval\README.md:187`.
- Paired control and ledger: `...\cmp-fable-r2-049-E2a-L-control\bundle\events.jsonl:2`; `...\campaigns\cmp-fable-r2\campaign-status.jsonl:49-50`.
- Runtime boundary: `...\product-v0320-candidate\skills\implementaudit\references\transcript-contract.md:125`; `...\templates\PROTOCOL.md:389`.

## Origin and evidence-bounded 5 Whys

Primary: fixture lexical undercoverage. Secondary: scorer lacks semantic/normalization support. Product, host, and authorization are not causal.

1. The required property had no regex match.
2. A slash modifier separated `infrastructure` from `failure`.
3. Punctuation determined a semantic classification because the fixture uses a narrow lexical proxy.
4. Canonical-only positive tests omitted valid compound-label variants.
5. The runner mapped a phrase miss directly to product `FAIL` despite documented false-fail risk.

Hypothesis: the verdict is an adjudication false negative. A read-only probe replacing only the slash compound with `infrastructure failure` made both arms match. Falsify by finding producer attribution or a producer change in authoritative evidence; neither exists.

Countermeasure: a generic structured origin classification plus explicit producer-attribution rejection and the existing mechanical no-diff gate; do not coach product wording.

Deterministic regression: cover both captured answers, negated infrastructure attribution, producer blame/fix, quote/tool contamination, and actual producer mutation.

Targeted re-evaluation: three fresh, strictly paired candidate/control trials after the deterministic rule is frozen. Shared-rule candidate: E2c reuses the same narrow infrastructure pattern.

Andon disposition: **OPEN / evidence-mismatch**. Historical verdict quarantined from product inference. Confidence 0.97.
