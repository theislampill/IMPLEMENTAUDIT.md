# Fable review of PR #21 — Evaluation custody, process identity, termination, and formal event authority

## Provenance statement

This review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) in a single main session on 2026-07-17. The harness reported
Fable 5 at session start and no model substitution was observed at any point
before or during the mutations on this branch. The original PR #21 is treated
as mixed-provenance work (the owner reports the implementation turn was
substituted from Fable to Opus partway through); every conclusion below was
re-derived from live GitHub state, exact Git objects, current source, and
executed tests — no claim is inherited from the original PR body or comments
without independent verification.

## Identity proof (exact objects)

| Object | SHA |
|---|---|
| PR #21 head (`feat/eval-custody-hardening`) | `5100336928c59da53038670e5e4048730a51aa95` |
| Merge commit on `main` | `6931e2b2187d09677921aeea004625df9350dece` |
| Merge base (parent 1) | `147ccabf8fda6016d8a91046d8b25228d84649f5` |
| `origin/main` at review time | `82297b0683e6b1379bfeee7568c965c143a358d4` |

Verified with local Git objects and authenticated `gh`:

- `git cat-file -e` succeeds for both head and merge commits.
- `git diff --exit-code 5100336 6931e2b2^2` — empty: the merged second parent
  is exactly the reviewed head.
- `git diff --exit-code 5100336 6931e2b2` — empty: the merged tree is
  byte-identical to the head tree (no evaluation-relevant merge drift).
- `git diff --check 6931e2b2^1 6931e2b2` — clean.
- Changed files (`--name-status`): `eval/hosts.py` (+361/−26),
  `eval/reconcile.py` (+183/−4), `eval/test_hosts.py` (+262/−4);
  total +806/−34, matching the GitHub file list exactly.

Discrepancy noted (cosmetic): the PR body claims “+612/−34”; the merged diff
is +806/−34. The body predates the adjudication commit `511d15b3` →
`5100336` and was not updated.

## Issue #20 and closure review

- Issue #20 (milestone v0.3.2.0) defines six test-locked scope items:
  process identity beyond pid (H30/H31/H31b/H32), process-tree termination
  (H35), orphan run-root elimination via atomic claim (H33), attested product
  checkout for formal runs (H34), structured-event authority (H37), and
  custody-record integrity (H36).
- The issue has zero comments; it was closed 2026-07-17T13:08:37Z by the
  merge linkage of PR #21 (`Closes #20`), not by a close comment, so no
  close-comment overclaim exists.
- CI (`validate` workflow) runs only whitespace, plugin-JSON, and
  `verify-package.sh` — it does **not** run the eval suites. Closure therefore
  rested on the PR body’s local-test claims. This review independently
  re-executed every deterministic suite on current `main` and confirms those
  claims were true (all green: `selftest`, `test_adapters`, `adversarial`,
  `test_hosts` H1–H39b).
- Supersession check: no commit after merge `6931e2b2` touched
  `eval/hosts.py`, `eval/reconcile.py`, `eval/runner.py`, or
  `eval/test_hosts.py` (only `eval/README.md` and the B3 fixtures changed,
  PRs #34/#36). PR #21’s bytes are the effective current behavior. No PR
  above #36 exists.

## What was executed (evidence)

On current `main` (`82297b0`), Windows 11 host, Python 3.11:

1. `python eval/test_hosts.py` — 49/49 checks OK (H1–H39b).
2. `python eval/selftest.py` — OK (16 fixtures, no model calls).
3. `python eval/test_adapters.py` — OK.
4. `python eval/adversarial.py` — OK (10 rule + 29 bundle/identity/snapshot cases).
5. A disposable Fable adversarial script driving the **production**
   `reconcile.py` CLI, `hosts._spawn_once`, and `runner.score_bundle`
   against forged inputs (never the test harness shims):
   - A1 hard-killed wrapper with a real spawned+killed process and a real
     `process_identity()` record → `terminal-state-unverified`, never RUNNING. OK.
   - A2 PID-reuse simulation: live pid, recorded creation time offset +2 s
     (past the 1.0 s tolerance) → refused as recycled. OK.
   - A3 crash between intent write and atomic rename (`<id>.claiming`
     containing `run-intent.json`) → `orphan-claim-swept`, terminal written. OK.
   - A5 identity-less record with a live pid → never RUNNING. OK.
   - A8 live matching identity → stays RUNNING, no terminal written. OK.
   - P2 `process-started.json` replaced with a JSON array → truthful
     `terminal-state-unverified`. OK.
   - P5 Windows normal-exit path: a grandchild with detached stdio survives
     its parent’s clean exit and is provably reaped when the Job Object
     handle closes (KILL_ON_JOB_CLOSE). OK.
   - P1 `process-started.json` replaced with non-UTF-8 garbage → **defect
     found** (Finding 1).
   - P3 parent `terminal.json` replaced with non-UTF-8 garbage → **defense
     bypass found** (Finding 2).

## Invariant adjudication

1. **Process identity binds lane, host OS/boot, pid, creation time** —
   CONFIRMED. `process_identity()` captures all fields at spawn
   (`hosts.py` `_on_started`); `original_process_alive()` refuses recycled
   pids (1.0 s creation-time tolerance), foreign-lane pids, rebooted hosts,
   and identity-less records. Locked by H30–H32 and re-proven against the
   production CLI (A1/A2/A5/A8).
2. **Tree termination before terminalization** — CONFIRMED on Windows
   (Job Object, kill-on-close, TerminateJobObject + `ActiveProcesses==0`
   verification; job-assignment failure fails closed). POSIX: timeout path
   killpg-verified (H35 analogue); normal-exit path has no group reap —
   recorded as a residual (Nonclaims below), not fixed here.
3. **Atomic claim / orphan handling** — CONFIRMED. Intent written inside a
   create-once `<id>.claiming` staging dir, atomically renamed; postcondition
   asserted; reconciler terminally sweeps orphan claim dirs with and without
   intents (H33 + A3). The documented rename-TOCTOU residual is acceptable
   under single-orchestrator serialized-lane custody.
4. **Attested checkout + nonempty payload before spawn** — CONFIRMED.
   Formal runs without a checkout are INVALID pre-spawn (H34); the payload
   hash is pinned pre-spawn into create-once `product-attestation.json`
   with an empty-tree refusal (H39/H39b); staging hashes the staged copy and
   fails closed on mismatch (H21).
5. **Structured-event authority** — CONFIRMED. A real Codex lane whose host
   session recorded no agent messages refuses to score raw stdout (H37);
   stdout events must be corroborated by the bound session (H23); session
   binding is cwd+time, exactly-one-match (H22, H27). Claude events are
   transcript-corroborated by exact session id.
6. **Custody-record integrity** — CONFIRMED WITH FIXES. Records are
   create-once, hashed at write, re-read via a bounded lstat-guarded reader,
   re-verified on every exit path (H36), and mission-planted run-root
   entries are quarantined (H38). Two narrow gaps found and fixed
   (Findings 1–2).
7. **Raw evidence retention** — CONFIRMED. Raw host stdout/stderr are
   preserved at the run root on error/timeout paths (H5, H19); credential
   scrubbing quarantines rather than deletes; reconciled terminals never
   promote to formal evidence (scorer parent-terminal gate, re-proven by A7).

## Findings by severity

**Finding 1 — MEDIUM (defect in PR #21 code; fixed).**
`eval/reconcile.py` caught only `(OSError, json.JSONDecodeError)` when
loading `process-started.json`. A record rewritten with non-UTF-8 bytes
raises `UnicodeDecodeError` (a `ValueError` sibling of `JSONDecodeError`,
caught by neither), so adjudication fell to the per-directory crash guard:
disposition `reconcile-error`, `write: none`, **no terminal record — on
every future pass, forever**. This contradicts the module’s own contract
(“a rewritten/garbage record must yield a truthful terminal disposition”)
and issue #20’s truthful-terminalization requirement. Demonstrated against
the production CLI before the fix; regression-locked by H40.

**Finding 2 — MEDIUM (defense bypass in effective behavior; fixed).**
The scorer’s parent-terminal gate (`eval/runner.py`, introduced in PR #19,
load-bearing for PR #21’s forged-custody threat model) failed open: an
unreadable/garbage `terminal.json` was treated as `{}`, and `kind=None`
passed the `not in (None, "ok")` test — so a mission that planted a bundle
and wrote a garbage or kind-less `terminal.json` (then had its wrapper
hard-killed before the post-exit sweep) would fare **better** than one that
wrote nothing (which yields `forensic-import-candidate` and refusal). This
is exactly the “forged or replaced terminal record” robustness case required
for this invariant. Fixed fail-closed; regression-locked by H40b/H40c.

**Finding 3 — LOW (documented; no code change).**
When the run-root credential scrub quarantines the raw host output, it also
moves the (clean) custody records into `quarantine-raw`; the exit-path hash
re-verification then reports “custody record … modified during the mission”
in `terminal.json`, misattributing the adapter’s own scrub as mission tamper.
The run is already INVALID for the credential hit either way; kind is
unaffected. Cosmetic truthfulness wobble in the terminal detail only.

**Finding 4 — LOW (documented; no code change).**
Exit-path integrity downgrades in the `finally` block rebind the local
`result` after `return` has already fixed the caller’s return value, so the
in-memory `HostRunResult` can be stale relative to `terminal.json`. Harmless
in effective behavior because `terminal.json` is the custody authority and
the scorer re-reads it (parent-terminal gate) before any formal scoring.

**Finding 5 — INFO.** PR body diff-stat understates the merged diff
(+612/−34 vs actual +806/−34); body predates the adjudication commit.

## Corrections made (this branch)

Product bytes changed: **yes** (two files, minimal diffs), plus tests.

1. `eval/reconcile.py` — catch `(OSError, ValueError)` so undecodable
   `process-started.json` reaches the truthful-terminal path
   (`terminal-state-unverified`, terminal written, `reconciled: true`).
2. `eval/runner.py` — parent-terminal gate fails closed: an unreadable or
   non-dict terminal refuses scoring; only `kind == "ok"` and
   `reconciled != True` admits a bundle.
3. `eval/test_hosts.py` — new deterministic regressions H40 (garbage
   `process-started.json` terminalized), H40b (garbage terminal fails
   closed), H40c (kind-less `{}` terminal fails closed). All three were
   verified RED against unfixed code, then GREEN after the fixes.

## Tests after fixes (Smoke B)

- `python eval/test_hosts.py` — 52/52 OK (H1–H40c).
- `python eval/selftest.py` — OK.
- `python eval/test_adapters.py` — OK.
- `python eval/adversarial.py` — OK.
- `git diff --check` — clean; `bash scripts/verify-package.sh` — ok.

## Residual risks and nonclaims

- **POSIX normal-exit group reap**: `_kill_tree` runs only on timeout /
  custody-write failure. On a clean child exit on POSIX, no `killpg` sweep
  occurs, so a descendant that detached its stdio (with or without
  `setsid`) survives terminalization. On Windows — the OS of both formal
  configurations L and O — the Job Object’s kill-on-close provably reaps
  such survivors (executed evidence, P5). Adjacent to the already-documented
  setsid/cgroup residual (v0.3.3.0); no POSIX lane exists in this program
  and no reachable CI executes the eval suites, so a POSIX-only regression
  could not be executed anywhere from this session — left as a documented
  residual rather than an untested fix.
- **Sub-millisecond Windows job-assignment window** (spawn → assign):
  documented residual carried from the PR; assignment *failure* fails
  closed.
- **Rename-claim TOCTOU** on POSIX (empty-dst replacement): accepted under
  single-orchestrator serialized custody, as documented in-source.
- **Post-terminalization filesystem tampering** by later processes (after
  the adapter exits) is outside the threat model; in-run tampering is
  hash-verified, and the scorer now refuses non-`ok`/unreadable terminals.
- This review executed no live model missions, no metered/API calls, and
  did not run the terminology study, publish any release, or modify DAEE.
- No claim is made about Codex/Claude live-lane behavior beyond what the
  mock-driven suites and production-path probes exercise.

## Verdict

**CONFIRMED_WITH_FIXES.**

The core custody architecture of PR #21 — process identity, Windows tree
termination, atomic claim, pre-spawn attestation, structured-event
authority, custody-record hashing, forged-custody quarantine — is genuine,
test-locked, and held up under independent adversarial re-execution against
production code paths. Two narrow custody-integrity gaps (perpetually
unterminated garbage records; fail-open scorer gate on forged terminals)
were found, fixed minimally, and regression-locked on this branch.

Integrator notes: this branch touches `eval/reconcile.py`, `eval/runner.py`,
`eval/test_hosts.py`, and adds this report. No other review session’s files
overlap is expected; if a later session also patches `eval/runner.py`, merge
this gate change first (it only tightens refusal).
