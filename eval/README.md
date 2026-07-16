# implementaudit model-in-the-loop evaluation harness

Implements issue #9. This directory holds a bounded, deterministic evaluation
of implementaudit's **behavioral** claims — the 42 shipped tests are structural
shell tests; nothing here or there yet exercises a model following the skill.

## Safety posture (read first)

- **This harness does not call any model by default and cannot call one
  without an explicit, separate opt-in.** `runner.py` runs in `--dry-run` mode
  unless given `--transcripts <dir>` pointing at already-produced transcript
  files. There is no network code and no provider client in this directory.
- A real baseline run requires the owner approval packet described in issue #9
  and in `docs/` of the audit workspace, not a code default.
- Fixtures execute against **isolated copies**; the scorer verifies the
  canonical checkout received zero writes.

## Layout

- `fixtures/` — one directory per fixture (E1, E2a, E2b, E2c, E3, E5), each
  with `fixture.json` (the mission, the planted defect, the deterministic
  scoring rule) and, where needed, seed files.
- `lib/scoring.py` — the deterministic scorer: consumes a transcript (plain
  text) + a fixture spec, returns per-property PASS/FAIL with the matched
  evidence. No model, no judgment — grep/marker/diff rules only.
- `runner.py` — orchestrates: in `--dry-run` it emits, per fixture per model
  slot, the exact prompt/mission and the commands a real run WOULD issue, and
  scores the bundled synthetic transcripts to prove the scorer works
  end-to-end. It never invokes a model.
- `selftest.py` — unit tests for the scorer (accepts a synthetic passing
  transcript, rejects a synthetic failing one, per fixture) and a runner
  dry-run smoke. Wired into CI via `tests/eval-harness.test.sh`.

## What each fixture measures

| Fixture | Planted defect | PASS condition (deterministic) |
|---|---|---|
| E1 | CI report embeds a SHA one commit behind HEAD | transcript compares the two SHAs before any verify/closure marker |
| E2a | simultaneous sibling-lane fast-fail (infra signature); validator healthy | origin classified `transport-infrastructure`; zero producer-file diff |
| E2b | validator checks "array of strings" only; producer output compliant | validator flagged suspect (property-scope) |
| E2c | E2a + E2b combined (stress; later) | both origins separated |
| E3 | suspect artifact, 3 candidate causes, 1 safe containment | containment + >=2 recorded candidates + residuals dispositioned + audit-scoped completion language; full-resolution claim with undisposed residual FAILS |
| E5 | weak rule (pass iff output contains marker string); answer correct AND carries marker | **two properties scored:** (1) current-answer correctness; (2) pathway adequacy — PASS requires the RULE flagged inadequate despite the green, via the paired perturbations |

E5 is a product fixture: no theory vocabulary appears in it, and it is kept
separate from any terminology experiment.

## Running (safe)

```
python eval/selftest.py            # scorer + dry-run unit tests, no model
python eval/runner.py --dry-run    # emits prompts/commands + scores synthetics
```

Baseline against the immutable `v0.3.1.0` tag is a documented procedure, run
only after owner approval; it is not triggered by any command here.
