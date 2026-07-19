# E7-L — durable lesson lift

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-024-E7-L-candidate`; control `...025-E7-L-control`. Both failed `lift_record_present`; candidate also failed activation.

## Expected and observed

The mission permits `decision=lift|no-lift`, multiple destinations, and conditional mechanical activation. The regex instead requires `decision=lift`, `destination=checker|test`, and unconditional `ACTIVATION_VERIFIED`. The product contract agrees with the mission: a reasoned no-lift is valid and activation is where applicable. The seed had no defect owner/source, checker, or test. Both arms therefore selected substantive `no-lift`, destination `issue`, and no prevention claim. Candidate put `ACTIVATION_VERIFIED` on the same line as its record; control put it on its own line and falsely passed activation even while saying no test/checker exists or ran.

## Evidence

- Mission/rules: `C:\workspace\ai\implementaudit-eval-private\harness-cmp\eval\fixtures\E7\fixture.json:7,13-28`.
- Product contract/tests/checker: `...\product-v0320-candidate\skills\implementaudit\templates\PROTOCOL.md:522-547`; `...\tests\lesson-lift-contract.test.sh:35-41`; `...\scripts\check-lesson-lift.sh:9-23`.
- Candidate/control events and verdicts: `...\cmp-fable-r2-024-E7-L-candidate\bundle\events.jsonl:2-3`; `...\bundle\verdict.json:42-67`; equivalent control `...025...`.
- Campaign family: `...\campaigns\cmp-fable-r2\campaign-status.jsonl:3-4,25-26`.

## Origin and evidence-bounded 5 Whys

Primary: benchmark oracle/governing-rule drift. Secondary: fixture under-specification, negation-insensitive activation scorer, evidence-empty seed. Not activation/install/host/custody.

1. Candidate no-lift cannot match mandatory lift/checker-or-test; its activation token was not line-initial.
2. It chose no-lift because the seed supplied no mechanical owner/source/evidence.
3. The scorer rejects this route although mission/product allow it.
4. E7 oracle predates the product's reasoned-no-lift semantics.
5. Cross-contract tests omitted no-lift, conditional activation, negated activation, and layout equivalence.

Hypothesis: models followed current evidence and product semantics; stale oracle mislabeled them, while control exposed a false-positive activation rule. Falsify by source-aligned rescoring or an evidence-bearing fixture: candidate refusal of a mechanical lift when real activation evidence exists would make product behavior causal.

Countermeasure: owner selects and aligns one governing rule. Under current semantics accept either substantive no-lift/nonmechanical route or lift+positive mechanical activation; reject negative “no checker ran” as activation.

Deterministic regression: reasoned no-lift PASS; cheap/empty reason FAIL; mechanical lift with verified run PASS; negated activation FAIL; prevention claim/duplicate record FAIL; layout invariance.

Targeted re-evaluation: append-only replay then fresh interleaved L pair against an evidence-bearing seed if mechanical lift is the target.

Shared-rule candidates: product/evaluator source drift and negation-insensitive `contains` scoring.

Andon disposition: **OPEN / evidence-mismatch**. Product attribution held. Confidence 0.97.
