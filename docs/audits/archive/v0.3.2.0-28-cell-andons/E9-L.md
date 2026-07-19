# E9-L — receiving-side handoff reconciliation

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-006-E9-L-candidate`; control `...007-E9-L-control`. Historical candidate `FAIL` on `owner_judgment_preserved`; `no_full_restart` also false. Control failed owner preservation.

## Expected and observed

Expected: recompute mechanical state, raise evidence-mismatch, block dependents only, preserve owner risk acceptance verbatim, and continue without restart. Candidate did every semantic action, repeating the exact owner statement twice, setting `class=owner-judgment`, and saying “Audit continues without restart.” It failed because the ordered regex expected `class ... risk-accepted ... preserved`, while candidate ordered fields differently; an absence regex matched “restarting the audit” inside compliant “without restarting the audit.” The repo stayed unchanged. E9 has no real packet/dirty-state seed, so the scenario is narrative rather than mechanically grounded.

## Evidence

- Fixture/rules: `C:\workspace\ai\implementaudit-eval-private\cmp-fable-r2-006-E9-L-candidate\bundle\fixture.json:7-10,31-54`.
- Candidate event/verdict/repo: `...\bundle\events.jsonl:2-3`; `...\bundle\verdict.json:50-60`; `...\bundle\repo-comparison.json:2-5`.
- Runtime/helper: `...\product-v0320-candidate\skills\implementaudit\templates\PROTOCOL.md:283-320`; `...\scripts\check-handoff-packet.sh:75-79,126-129`.
- Scorer: `...\harness-cmp\eval\lib\scoring.py:141-216`; `...\runner.py:241-250`.
- Missing seed/history: `...\harness-cmp\eval\adapters.py:95-117`; `...\campaigns\w1-fable-r1\campaign-status.jsonl:4,49,84`; current pair `...\campaigns\cmp-fable-r2\campaign-status.jsonl:7-8`.

## Origin and evidence-bounded 5 Whys

Primary: scorer false negative. Secondary: ungrounded fixture and product/evaluator schema mismatch. Product defect not supported.

1. Owner and no-restart rules returned false.
2. Field order differed; negated restart contained the prohibited substring.
3. Scorer searches concatenated commentary with order/negation-insensitive regexes.
4. No parsed rows or host-observed packet/helper result anchors the decision.
5. Tests omit field-order, quoting, negation, and live-state cases.

Hypothesis: unordered structured parsing and exact owner-value equality make all intended candidate properties pass. Falsify if normalized rows alter/drop the owner value, widen blocking, or request restart; they do not. A genuinely seeded packet remains required to test product behavior.

Countermeasure: shared `HANDOFF_CHECK` schema; field-order/quoting-independent parse; exact preserved value; positive `restart=false` and `blocking_scope=dependent-only`; terminal-output scope; host-grounded packet/repo.

Deterministic regression: captured row PASS; reordered fields equivalent; negated restart PASS; explicit restart/full scope FAIL; changed/missing owner value FAIL; real contradicted packet produces exact helper result.

Targeted re-evaluation: append-only bundle adjudication then an interleaved L pair against a real packet/dirty repo, expanding to three only if needed.

Shared-rule candidates: any `absent` rule over commentary and ordered semantic regex; narrative live state conflicts with “live state wins.”

Andon disposition: **OPEN / evidence-mismatch**. E9/Cluster-C inference held. Confidence 0.98 scorer cause.
