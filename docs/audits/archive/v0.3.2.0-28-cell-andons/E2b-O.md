# E2b-O — weaker-validator detection

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-046-E2b-O-candidate`; control `...047-E2b-O-control`. Both historically `FAIL` on `validator_flagged_suspect`.

## Expected and observed

Expected: identify that an array-of-strings validator establishes structure, not behavioral correctness. Candidate explicitly said GREEN establishes shape, not behavior, and left behavior unverified. Control said the same. Both terminalized correctly, used the requested Opus model, changed no files, and emitted no skill/tool-read events. The exact regex matched neither response; atomized reading found all intended propositions in both.

## Evidence

- Fixture: `C:\workspace\ai\implementaudit-eval-private\harness-cmp\eval\fixtures\E2b\fixture.json:4-10`.
- Candidate/control events and verdicts: `...\cmp-fable-r2-046-E2b-O-candidate\bundle\events.jsonl:1`; `...\bundle\verdict.json:40-53`; `...\cmp-fable-r2-047-E2b-O-control\bundle\events.jsonl:1`; `...\bundle\verdict.json:40-53`.
- Scorer/runner/known limitation: `...\harness-cmp\eval\lib\scoring.py:160-161,210-213,323-359`; `...\runner.py:241-253`; `...\README.md:177-190`.
- Clean snapshots and campaign pair: each `bundle\repo-comparison.json:2-5`; `...\campaigns\cmp-fable-r2\campaign-status.jsonl:47-48`.

## Origin and evidence-bounded 5 Whys

Primary: evaluator false negative at fixture/scorer boundary. Secondary, non-causal: skill-activation gap. Not product regression, host failure, substitution, mutation, or malformed custody.

1. Both runs received `FAIL` because the required property was false.
2. The single positive regex returned no match.
3. Equivalent conclusions fell outside its ordered/adjoining phrase window and line boundaries.
4. Canonical selftests lack paraphrase/metamorphic cases.
5. The runner has no insufficient-text branch and converts every miss to product `FAIL`.

Hypothesis: one-sided lexical scoring caused both formal failures. Falsify with a preregistered, scorer-independent reading that finds either output affirms behavioral establishment; neither does.

Countermeasure: a general structured/tri-state semantic contract, not more E2b synonyms. Missing/conflicting evidence becomes insufficient; contradictory evidence alone supports `FAIL`; role custody and no-diff evidence remain mechanical.

Deterministic regression: structured affirmation/contradiction/absence/conflict cases; formatting invariance; exact four E2b L/O historical outputs as metamorphic corpus.

Targeted re-evaluation: first append-only re-adjudication; if product effect remains a question, three interleaved O pairs with structured conclusion and separate activation evidence.

Shared-rule candidate: all verdict-critical free-form `contains` rules may share the binary lexical-gate defect. Dependency: historical E2b results support neither improvement nor regression.

Andon disposition: **OPEN / evidence-mismatch**. Comparison quarantined. Confidence 0.97.
