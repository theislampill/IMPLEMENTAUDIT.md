# E2b-L — weaker-validator detection

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-054-E2b-L-candidate`; control `...055-E2b-L-control`. Historical candidate `FAIL`, control `PASS`, on `validator_flagged_suspect`.

## Expected and observed

Both answers say GREEN establishes only array/string shape, not behavioral correctness. Candidate used “It does not establish”; control happened to repeat “validator ... does not establish” inside the fixture's 40-character ordered window. Exact replay returned candidate false/control true; replacing only candidate “It” with “The validator” flipped the score without altering meaning. Both runs were terminal, same model/prompt/fixture, mutation-free, and neither recorded a product-skill read.

## Evidence

- Fixture intent/regex: `C:\workspace\ai\implementaudit-eval-private\harness-cmp\eval\fixtures\E2b\fixture.json:4-10`.
- Candidate/control text and verdicts: `...\cmp-fable-r2-054-E2b-L-candidate\bundle\events.jsonl:1`; `...\bundle\verdict.json:40-53`; `...\cmp-fable-r2-055-E2b-L-control\bundle\events.jsonl:1`; `...\bundle\verdict.json:40-53`.
- Scorer/runner: `...\harness-cmp\eval\lib\scoring.py:160-161,210-213,323-359`; `...\runner.py:241-252`.
- Candidate governing rule: `...\product-v0320-candidate\skills\implementaudit\templates\PROTOCOL.md:639-660`.
- Related E2c pattern: `...\harness-cmp\eval\fixtures\E2c\fixture.json:10-11`.

## Origin and evidence-bounded 5 Whys

Primary: scorer. Secondary: fixture and canonical-only selftests. Not product/host/authorization.

1. Candidate FAIL came from a false property.
2. The ordered regex did not match.
3. It required the subject token and selected conclusion phrase within 40 characters.
4. Tests covered one canonical positive and one obvious negative, not semantic paraphrases.
5. Every required text miss becomes product `FAIL` without scorer-adequacy classification.

Hypothesis: harmless lexical form created the entire candidate/control delta. Falsify with an independently declared rubric showing candidate affirms behavioral establishment; its text says the opposite.

Countermeasure: general structured semantic evidence/tri-state adjudication; `PASS` needs affirmative evidence, `FAIL` contradictory evidence, and insufficient/ambiguous evidence is not product failure. Preserve old verdicts; append revised adjudication.

Deterministic regression: captured candidate/control both receive semantic parity; pronouns, clause order, wrapping, and contractions cannot flip outcomes; affirmative behavior-proof claims fail; E2c equivalent cases run too.

Targeted re-evaluation: append-only bundle replay, then interleaved L candidate/control repetitions with activation evidence separately measured.

Shared-rule candidate: one-positive/one-negative regex selftests validate vocabulary, not behavior. Dependency: Cluster B comparison cannot consume the historical delta.

Andon disposition: **OPEN / evidence-mismatch**. Candidate-vs-control delta invalid. Confidence 0.99.
