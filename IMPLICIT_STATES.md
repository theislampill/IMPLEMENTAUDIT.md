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
- Historical fixture populations must use their exact retained physical members.
  CI680 found two historical Windows profiles falling through to today's validator
  after it changed. Their unchanged hashes now select the explicit prior member in
  `test-support/dg17-validator-history/pre-composed-owner-20261112/`; the historical
  profile tests still reject current bytes as substitutes. This retains the old
  source relation rather than rebasing historical evidence onto the new owner.

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

## CI-FIXED-RUNTIME-IMAGE

- Sources: `.github/workflows/validate.yml`,
  `scripts/qualify-work-graph-c5-setup.py`, and
  `scripts/check-validation-registry.sh`.
- Requested runner label, actual image, interpreter availability, attempted
  provisioning, program entry and qualified prerequisites are separate states.
  A moving image alias can lose the fixed `/usr/bin/python3.12` prerequisite
  before any qualification program runs.
- Guard: the canonical validation job pins `ubuntu-24.04` while using that fixed
  interpreter. Existing observation/provision/receiving/finalization commands,
  privilege scope and timeouts remain unchanged. The actual image still needs
  the existing prerequisite observations; a label is not host qualification.
- Evidence: CI run 43324726224 selected Ubuntu26 and refused missing Python3.12
  before the scoped provisioning program. The registry's positive and negative
  workflow controls prevent this known label/runtime mismatch from recurring.
- Failure/recovery: retain the failed run; correct source and publish a reviewed
  increment through the same guarded route. No manual campaign or privilege
  broadening follows from this source correction.

## CI-PREREQUISITE-RECEIVING-OUTCOME

- Sources: `.github/workflows/validate.yml` and `hosted_current_owner` in
  `scripts/qualify-work-graph-c5-setup.py`.
- Step conclusion, process exit, structured observation, current source binding
  and prerequisite qualification are independent dimensions. `continue-on-error`
  can leave a successful step conclusion after the receiving program exits one.
- CI680 did that when the selected current loader was absent from the held-source
  pin table. The step label did not qualify the prerequisite; the refusal and
  subsequent composite test failures remain evidence.
- Guard: receive the actual process result and scoped observation against exact
  source pins before claiming qualification. Missing/stale source refuses; source
  repair does not authorize a manual privileged retry or a broader host profile.
- `test_hosted_current_reader_loads_actual_source_without_dispatch` in
  `tests/composite-source-cases.py` loads the actual current source while forbidding
  producer dispatch. A stale loader pin fails this canonical regression even when
  the observational workflow step continues after an error.
- The retained-policy finalizer is read/record only. Its success is a snapshot of
  retained policy and receipt state, not policy removal or physical VM disposal.

## C5-EXPLICIT-CURRENT-VERSUS-FROZEN-SOURCE

- Sources: `scripts/load-work-graph-c5-executor.py`,
  `scripts/qualify-work-graph-c5-setup.py`, and
  `tests/c5-selected-source-fixture.py`; exact retained compiler identity lives in
  `test-support/r5-continuity-compiler-history/MANIFEST.json`.
- Logical revision, physical source member, executed loader bytes, captured
  compiler, producer/payload census and native admission are separate dimensions.
  An unchanged historical tuple cannot acquire current compiler bytes merely
  because both occupied the same repository path at different times.
- The C5 source owners define exact selection; Root receives and publishes the
  reviewed source. The held loader pin selects V9 with its current compiler.
  Frozen V3-V8 tuples retain their original compiler through explicit physical
  history. V3/V4 fixture logical inputs use that same frozen compiler.
- Unknown, mixed, drifted or wrong-profile inputs refuse. Capture and closing
  identity/hash checks remain required; no hash search or current/historical
  wildcard is introduced. Repair uses a separate source revision and preserves
  old tuples and failures; source receiving never grants native dispatch.
- `tests/c5-current-source-receiving.py`, invoked by the canonical composite
  test, covers current/frozen loading, captured and fresh drift refusal, exact
  producer/payload rejection and preservation of prior pin/revision tables.
  These source controls do not qualify original C5 execution or JOIN.

## FINITE-REGISTRY-HISTORICAL-INPUTS

- Sources: `tests/work-graph-historical-fixture.py`,
  `tests/work-graph-historical-fixture-cases.py`, and
  `tests/work-graph-finite-batch-cases.py`; original pins remain owned by
  `scripts/qualify-work-graph-finite-leaf.py`.
- Current checker/wrapper bytes, a frozen profile's required hashes, explicit
  retained specimens, fixture construction, acquisition and live execution are
  separate states. CI681 exposed formerly identical paths after the current CI
  image guard changed the checker and wrapper.
- Root owns this fixture repair. The supplemental catalog retains exact
  `cbb616cc` preimages for both registry files. Only fixture construction selects
  them; acquisition never repairs a subject or accepts current substitution.
  Historical image assertions use the original contract, not current path bytes.
- The closed changed-profile census includes the registry wrapper. Source controls
  require its positive snapshot and reject current substitutions before runtime,
  dispatch or receipts; same-size retained-specimen corruption also refuses.
- Original contracts and the original117 manifest remain unchanged. Source
  regression checks grant no historical bank replay or original live-leaf credit;
  the corresponding live assertions remain separately unexecuted here.
