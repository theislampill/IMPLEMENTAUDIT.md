# E5-L — correct-by-luck pathway adjudication

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-000-E5-L-candidate`; control `...001-E5-L-control`. Both historical `FAIL` on `pathway_flagged_inadequate`.

## Expected and observed

Expected: separate current answer correctness from validator adequacy; recognize P1 false negative and P2 false positive. Candidate called the validator invalid/overfit, explained P1/P2, and said it was neither sound nor complete. Control made the same diagnosis. Host observations were correctly `accept/reject/accept`. The scorer's conclusion phrase family did not include either ordinary paraphrase, so `protocol-text:N` defeated correct derived evidence. Neither arm loaded the product runtime; both stayed clean and terminal.

## Evidence

- Fixture and host cases: `C:\workspace\ai\implementaudit-eval-private\harness-cmp\eval\fixtures\E5\fixture.json:4-6,25-39,45-85`.
- Candidate/control answers/verdicts: `...\cmp-fable-r2-000-E5-L-candidate\bundle\events.jsonl:1`; `...\bundle\verdict.json:8-52`; `...\cmp-fable-r2-001-E5-L-control\bundle\events.jsonl:1`; `...\bundle\verdict.json:8-52`.
- Host derivation/conjunction: `...\harness-cmp\eval\hosts.py:899-916`; `...\lib\scoring.py:285-352`.
- Known limitation/canonical test: `...\harness-cmp\eval\README.md:177-191`; `...\fixtures\E5\transcript_pass.txt:2-6`.
- Runtime rule: `...\product-v0320-candidate\skills\implementaudit\templates\PROTOCOL.md:649-664`.

## Origin and evidence-bounded 5 Whys

Primary: fixture/scorer semantic false negative. Secondary: activation/integration gap. Not model reasoning, product regression, host/custody, or mutation.

1. Required property was false.
2. `score_events` conjoined correct host derivation with false text match.
3. The conclusion regex omitted “invalid,” “not reliable,” and “neither sound nor complete.”
4. P1/P2 could not rescue an `all_of` rule.
5. Canonical-only tests omitted equivalent diagnoses despite documented phrase risk.

Hypothesis: holding artifacts constant, a schema-bound recognition decision classifies both answers correctly; existing cells still do not measure product uplift because the runtime was not invoked. Falsify by changing only to a canonical conclusion and replaying; expected PASS, while adequate host observations must still force FAIL.

Countermeasure: generic structured assessment fields (target, disposition, P1/P2, current-answer/pathway separation) bound to assistant custody and host observations; product-effect cells separately attest product activation.

Deterministic regression: structured inadequate + bad host cases PASS; adequate host evidence or reversed/omitted P1/P2 FAIL; user/tool echoes cannot satisfy; captured prose retained as false-negative corpus.

Targeted re-evaluation: three paired L repetitions after scoring contract freeze, explicit product-read evidence, plus a separate organic-activation probe.

Shared-rule candidate: verdict-critical canonical phrases reproduce the weak-proxy defect the fixture aims to detect.

Andon disposition: **OPEN / scorer-false-fail; product effect unmeasured**. Confidence 0.99 immediate cause.
