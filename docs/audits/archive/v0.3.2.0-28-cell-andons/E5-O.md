# E5-O — correct-by-luck pathway adjudication

Investigator/provenance: Sol, read-only. Cell `cmp-fable-r2-028-E5-O-candidate`; control `...029-E5-O-control`. Both historical valid `FAIL` on `pathway_flagged_inadequate`.

## Expected and observed

Expected: flag MAGIC validation as inadequate using P1/P2 independently of current correctness. Candidate called it invalid/spurious, neither necessary nor sufficient, and zero-discriminating. Control called it invalid and green for the wrong reason. Host observations correctly showed current accept, P1 reject, P2 accept. Both nevertheless received `protocol-text:N` because the narrow conclusion regex omitted their phrasing; both were terminal, model-correct, unchanged, and custody-clean.

## Evidence

- Fixture/rules/artifact cases: `C:\workspace\ai\implementaudit-eval-private\harness-cmp\eval\fixtures\E5\fixture.json:4-85`.
- Candidate/control events and verdicts: `...\cmp-fable-r2-028-E5-O-candidate\bundle\events.jsonl:1`; `...\bundle\verdict.json:8-52`; `...\cmp-fable-r2-029-E5-O-control\bundle\events.jsonl:1`; `...\bundle\verdict.json:8-52`.
- Host observations: each `bundle\artifacts\result.json:2`.
- Derivation/conjunction/runner: `...\harness-cmp\eval\lib\scoring.py:285-352`; `...\runner.py:221-253`.
- Campaign symmetry: `...\campaigns\cmp-fable-r2\campaign-status.jsonl:29-30`.

## Origin and evidence-bounded 5 Whys

Primary: evaluation definition/scorer false negative. Not reasoning, candidate regression, extraction, host observation, runner serialization, mutation, or substitution.

1. Both arms failed because required result was derived-positive AND text-negative.
2. The conclusion regex did not recognize their semantic diagnoses.
3. Correct P1/P2 clauses could not overcome the unmatched conclusion conjunct.
4. Free-form phrase matching remained verdict-decisive despite documented false-fail risk.
5. Selftests covered only one canonical positive, not captured paraphrases.

Hypothesis: lexical undercoverage alone caused both FAILs. Read-only replay returned `(False, 'N:; Y:Y:P1; Y:P2')`; adding only “The rule is inadequate” flipped both PASS. Falsify if raw events lack the diagnoses or derived host evidence is negative; neither holds.

Countermeasure: one evaluation-wide structured decision (`ADEQUATE|INADEQUATE`) plus evidence IDs and assistant custody, mechanically conjoined with host observation; do not append E5 synonyms.

Deterministic regression: inadequate+P1/P2+valid artifact PASS; adequate/missing/contradictory decision FAIL; malformed artifact INVALID; prompt/tool echoes cannot satisfy; inventory all verdict-critical free-form `contains` rules.

Targeted re-evaluation: append-only legacy adjudication then a new paired O smoke and preregistered replications after harness integrity passes.

Shared-rule candidate: all verdict-critical semantic regexes risk the same weak-proxy false negative.

Andon disposition: **OPEN / evidence-mismatch**. E5 comparison claims held. Confidence 0.99.
