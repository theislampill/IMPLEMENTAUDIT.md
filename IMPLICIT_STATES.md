# Relevant implicit states

This registry describes source contracts and unresolved transitions. It does not
establish current runtime state, grant authority, or certify a native episode.

## DG17-WINDOWS-OWNER-CONTAINMENT

- Scope/owner: `windows_owner` in
  `skills/implementaudit/scripts/validate-run-root.sh`; the composing validator
  owns its private job, suspended process, temporary output and live cleanup entry.
- Independent dimensions: job handle validity; kill-on-close configuration;
  process creation; job assignment; resumed state; parent exit; active job members;
  deadline; cleanup completion; record disposition.
- Allowed sequence: create/configure private job -> create suspended owner ->
  assign owner -> register cleanup -> resume -> parent exits and job becomes empty
  within the unchanged ten-second bound -> return -> close resources.
- Guards: job creation, configuration and assignment must succeed before execution.
  Failure refuses through `OUT_OF_PROFILE`, not a finding about the unread record.
  The two-second cleanup wait does not extend the owner's execution budget.
- Invariants: a successful parent exit is insufficient while the job has members;
  an unassigned owner is never resumed; no breakaway is admitted. After assignment,
  kill-on-close contains the process tree if the composing process is interrupted.
- Failure/recovery: the outer `finally` covers temporary-file, process-creation
  and assignment failures as well as normal/timeout paths. It removes only its
  own cleanup entry, terminates/reaps any created process and closes the job.
  An error or unknown cleanup result never supplies a successful disposition.
- Source controls: `windows_containment_controls` and `owner_timeout_controls`
  in `tests/nonterminal-yield-cases.py`. They exercise real local Windows processes
  with bounded Win32 failure injection; these are not native campaign acceptance.
- Retained findings: C4 accepted a timely parent with a live descendant; R1 fixed
  the owned path but retained an unowned fallback. Early setup failures also
  escaped job cleanup. Those historical failures are not regraded by this fix.
- Status: containment and setup paths hardened in source; original native Stop,
  currentness, ledger and campaign obligations remain separate. Abrupt external
  termination between suspended creation and assignment is outside these verified
  local controls; this is not a universal no-orphan certificate.

## DG17-SOURCE-PIN-CLOSURE

- Sources: validator -> initialization pins in `claim-run-rotation.py` -> companion
  pins in `claim-run.sh` -> transport/evidence source profiles -> route peer ->
  both compilers -> `source-peers/route-graph/SOURCE_MANIFEST.json` and package.
- Each new source profile is additive. Historical profiles, route identities and
  preimages retain their original meanings; recognition is not native admission.
- Retained route-map rows may share one dictionary initializer only when every
  key/value and insertion order is preserved. Runtime function bodies and guards
  are not changed by that representation reduction.
- Guards/tests: current bodies must match all derived byte/hash fields; preserve
  all preceding profiles and reject stale/substituted owners. Focused receiving
  lives in `tests/composite-source-cases.py`; package caps and mandatory reserve
  remain owned by `scripts/package-contract.py` and its tests.
- Failure/recovery: a partial generation or failed size check holds that candidate.
  Regenerate from its immutable base and reconcile actual output before retry;
  never promote a successful writer command into source or package acceptance.

## PR255-GUARDED-PUBLICATION

- Scope: `refs/heads/integration/active-rlgwo-composite-20261025`, with one accountable
  Root publisher. Mainline adoption, releases and issue closure are separate.
- Dimensions: reviewed candidate/tree; local qualification; owner authorization;
  observed remote head; transport result; remote post-state; subsequent CI result.
- Sequence: freeze candidate -> receive independent source review -> pass applicable
  checks -> reacquire the remote head -> publish exactly one ref with a guard binding
  repository, candidate and expected head, using non-force transport -> read back
  the actual remote commit/tree.
- Failure/recovery: an ambiguous push may have completed. Reconcile the exact ref
  before retrying; an already confirmed update is not replayed. Unexpected advancement
  requires a fresh source decision, never a forced overwrite. Compensation is a
  reviewed revert. A source publication does not itself establish native acceptance.
- Status/evidence: the publication owner maintains operation-specific guard tests
  and receipts. This registry is not a live publication ledger; consult actual
  branch state and those exact receipts before advancing the next transition.

## LOCAL-WINDOWS-SHELL-DISCOVERY

- Source: `fixtures/controller-initialization/author_checkpoint.py`; the fixture
  discovers Bash on PATH, then inspects/activates a disposable test controller.
- Discovery and execution are separate states. Windows executable search can run
  System32's WSL launcher for a bare `bash` even when PATH discovery found Git Bash.
- Guard: execute the discovered absolute path for both fixture operations, before
  changing child working directory. Missing Bash refuses; it never authorizes a
  different interpreter or promotes a failed inspection into activation.
- Evidence: the original bare invocation returned Linux while PATH selected Git
  Bash; `tests/continuity-contract.test.sh` passed after the fixture used that path.
  This is local fixture qualification, not programme controller recovery.
