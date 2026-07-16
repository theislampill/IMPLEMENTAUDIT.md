# implementaudit evaluation harness — deterministic scorer, fixtures, foundation

**Status: foundation for issue #9, not a complete model-in-the-loop harness.**
This directory implements the deterministic transcript **scorer**, the E1–E5
**fixtures**, and **dry-run** infrastructure. It does **not** yet implement
model execution (host adapter, execution-plan machinery, transcript capture).
It therefore does **not close #9** on its own — #9 is closed only when the
execution half lands and a baseline is produced under owner approval.

The 42 shipped tests are structural shell tests; nothing there exercises a
model following the skill. This scorer is the part that will judge such runs
once they exist.

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
  dry-run smoke.
- `adversarial.py` — scorer-integrity suite: 10 attack transcripts (user-echo,
  quoted transcript, wrong-role markers, wrong order, duplicate markers,
  action-claim-without-artifact, pasted nested transcript, wrong-fixture,
  correct-but-lucky E5, and one genuine pass) that the scorer must classify
  correctly. Both are wired into CI via `tests/eval-harness.test.sh`.

### Scorer integrity (role awareness)

Transcripts are role-tagged (`USER:` / `ASSISTANT:` / `TOOL:` / `SYSTEM:`).
By default a text rule matches **only assistant-authored, current-turn**
content: quoted lines (`>`), fenced code blocks, and anything after a
`----- BEGIN QUOTED TRANSCRIPT -----` sentinel are non-authoritative. Rules
whose verdict depends on a repository action (`no_diff`) read a mechanical
working-tree `summary`, never prose — so an assistant that *claims* an action
it did not perform fails. `count_distinct_at_least` rejects duplicate markers
standing in for distinct items. This closes the "put the expected words
anywhere in the text" class of false pass.

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
