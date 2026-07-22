# E9-O — receiving-side handoff reconciliation

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-014-E9-O-candidate`; control `...015-E9-O-control`. Both historical `FAIL` on `rows_classified`, also owner preservation false.

## Expected and observed

Expected: rederive dirty HEAD, classify stale mechanical claims contradicted, raise evidence-mismatch, preserve `owner accepted residual r1 as risk-accepted` verbatim, block dependents only, and continue without restart. Candidate and control both measured live state and semantically complied. Candidate used a `## HANDOFF_CHECK` table; control used `AUDIT_VERIFY — HANDOFF_CHECK` plus a table. The scorer required bare same-line `HANDOFF_CHECK ... contradicted` and ordered owner tokens, so both false-failed. Both repos were unchanged.

## Evidence

- Fixture/rules: `C:\workspace\ai\implementaudit-eval-private\harness-cmp\eval\fixtures\E9\fixture.json:7-55`.
- Candidate/control events/verdicts: `...\cmp-fable-r2-014-E9-O-candidate\bundle\events.jsonl:4`; `...\bundle\verdict.json:43-74`; corresponding control at `...015...`.
- Candidate live-state trace: `...\cmp-fable-r2-014-E9-O-candidate\host-stdout.raw:13-16,31-40`.
- Runtime/helper/tests: `...\product-v0320-candidate\skills\implementaudit\templates\PROTOCOL.md:297-320`; `...\scripts\check-handoff-packet.sh:75-129`; `...\tests\handoff-packet-contract.test.sh:18-61`.
- Scorer/runner/known limitation: `...\harness-cmp\eval\lib\scoring.py:139-216`; `...\runner.py:241-253`; `...\README.md:186-191`.
- Clean pair/ledger: each `bundle\repo-comparison.json:2-5`; `...\campaigns\cmp-fable-r2\campaign-status.jsonl:15-16`.

## Origin and evidence-bounded 5 Whys

Primary: scorer governing-rule defect/evidence-mismatch. Secondary: fixture contract inconsistency. Not product regression, substitution, adapter, invalid custody, or mutation.

1. Two required text properties were false.
2. Table/layout and field order fell outside regexes.
3. Generic `contains` has no record, field, relation, or negation-aware parsing.
4. Selftests contain one canonical phrasing only.
5. Phrase misses become product `FAIL` and campaign data despite semantically compliant evidence.

Hypothesis: record-aware, order-independent scoring passes both bundles. Read-only probe showed adding only two canonical-form lines makes all properties true; an incomplete token scatter can currently pass, while “without restarting” can fail. Falsify with blind extraction showing a missing claim, altered owner wording, unrestricted block, or affirmative restart.

Countermeasure: structured record scoring, exact owner value, positive dependency/restart fields, role/quote protections, and append-only revised verdicts; do not patch product output with E9 wording.

Deterministic regression: current tables PASS; canonical/reordered rows equivalent; negated restart PASS; affirmative restart, missing claim/owner, changed owner value, scattered tokens, or missing dependent-only scope FAIL.

Targeted re-evaluation: first re-adjudicate all four E9 bundles; then three-rep L/O mini-matrix only after scorer freeze. A separate ordinary handoff fixture is needed for product uplift because this prompt teaches much of the answer.

Shared-rule candidates: ordered regex and `absent` false positives are confirmed across both configurations/arms.

Andon disposition: **OPEN / evidence-mismatch**. E9 and downstream Cluster C quarantined. Confidence 0.99.
