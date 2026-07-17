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
  without an explicit, separate opt-in.** There is no network code and no
  provider client in this directory.
- A real baseline run requires the owner approval packet described in issue #9
  and in `docs/` of the audit workspace, not a code default.
- Future model evaluations run in **isolated disposable fixture
  repositories/worktrees**; the repository snapshots (below) verify the
  canonical checkout received zero writes.

## Trust boundary (the core of this foundation)

The scorer trusts **only fields assigned out-of-band by the host adapter or
the trusted replay-bundle builder** (`lib/bundle.py`). Role labels, run IDs,
and sequence numbers are authoritative because the bundle is produced in a
location the evaluated model cannot write — never because a string says so.
A `"source": "host-adapter"` field is not proof and is not consulted.

- A string such as `ASSISTANT:` or a JSON-looking role object inside
  model/user content is **data, never authority**. (The earlier free-text
  `ROLE:` parser was demonstrably forgeable — a user message containing a
  forged `ASSISTANT:` line passed E5. That parser is no longer an accepted
  input path for evaluation.)
- Marker-like strings in user/system/tool events remain data.
- Natural-language assistant claims are not proof of repository mutation:
  repository verdicts come from mechanical before/after snapshots
  (`lib/reposnapshot.py`), which detect committed changes even when the
  final working tree is clean. `git status` alone is never sufficient.
- Legacy free text is rejected as `INVALID` by default.
  `--trusted-synthetic-roles` exists only for the bundled synthetic unit
  fixtures (whose role tags we authored) and is **prohibited for real
  evaluation output**.

### Run bundle

```
<run-root>/
  manifest.json      identity + sha256 bindings (run, fixture, prompt,
                     product tag/commit/tree, installed payload, harness,
                     adapter, model requested/resolved, host, events hash,
                     snapshot hashes, timestamps)
  events.jsonl       one host event per line: schema/run_id/fixture_id/seq/
                     role/kind/content/recorded_at — strict JSON, exact
                     schema version, strictly increasing unique seq,
                     enumerated roles and kinds
  repo-before.json   mechanical repository snapshots; changed_files is
  repo-after.json    COMPUTED from immutable before/after identities by
                     reposnapshot.compare at capture time
  artifacts/         optional machine-readable result artifacts
  verdict.json       written by the scorer (lib/verdict.py)
```

Malformed/truncated records, mixed run or fixture IDs, duplicate sequence
numbers, unknown roles (including Unicode confusables), or hash-binding
mismatches ⇒ **INVALID**, never FAIL and never PASS.

### Four-valued status

| Status | Meaning |
|---|---|
| `PASS` | valid run proved all required invariants |
| `FAIL` | valid run violated a product invariant |
| `INVALID` | identity/schema/transcript/fixture/evidence/custody malformed or insufficient |
| `ERROR` | harness/host/infrastructure failure prevented adjudication |

INVALID and ERROR are never collapsed into product FAIL.

### Output custody

Raw transcripts and results default **outside the repository**. An in-repo
result root is allowed only under an ignored directory (`results/`,
`raw-runs/` — see `.gitignore`) with explicit opt-in. Path resolution
(`lib/custody.py`) rejects `..` traversal, absolute paths outside the
approved root, symlink/junction escape, and pre-existing destination
collisions. Never commit private prompts, transcripts, credentials, or
provider receipts; a sanitized summary may be checked in only after explicit
review. Retention: raw bundles are kept only as long as the analysis needs
them and are deleted on request.

## Layout

- `fixtures/` — one directory per fixture (E1, E2a, E2b, E2c, E3, E5), each
  with `fixture.json` (the mission, the planted defect, the deterministic
  scoring rule) and, where needed, seed files.
- `lib/bundle.py` — run-bundle validation (the trust boundary) + the trusted
  replay-bundle builder.
- `lib/reposnapshot.py` — mechanical repository snapshots and comparison.
- `lib/custody.py` — output-path custody guards.
- `lib/verdict.py` — the versioned verdict envelope.
- `lib/scoring.py` — the deterministic rule engine. `score_events` (bundle
  path) reads host-assigned roles; the legacy free-text path exists only for
  the synthetic unit fixtures.
- `runner.py` — `--bundle <run-root>` scores a host-produced bundle and
  writes `verdict.json`; `--dry-run` (default) proves rule semantics on the
  bundled synthetics; it never invokes a model.
- `selftest.py` — per-fixture accept/reject unit tests + dry-run smoke.
- `adversarial.py` — 10 rule-semantics attack cases + 15 bundle
  validity/authority cases (forged roles, nested pastes, JSON role dumps,
  tool/system markers, confusable roles, truncation, duplicate/mixed
  sequence and run IDs, wrong fixture/run binding, committed-unauthorized-
  change-with-clean-tree, malformed snapshots, custody escapes, one genuine
  PASS). Wired into CI via `tests/eval-harness.test.sh`.

### Scoring source: artifacts first, phrases second

Where a fixture declares `artifact_rules`, the machine-readable result
artifact (`artifacts/result.json`) is the **primary** basis for those
properties; transcript text rules serve as protocol/order checks. E5 keeps
three separate artifact fields: `current_answer_correct`,
`rule_adequate`, `perturbation_evidence`. **Known limitation:** phrase-family
text matching may false-fail semantically correct answers phrased outside
the pattern list; it errs in the safe direction for gating but can mask real
improvements in before/after comparisons, so it cannot be the final
comparison method — artifact-based scoring is.

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
