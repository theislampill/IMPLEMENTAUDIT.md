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
- Temporary directory (proposed candidate, not adopted): the composing
  validator's `run` gives every owner, on Windows and POSIX, one private
  directory as `TMPDIR`/`TMP`/`TEMP` and removes it after the owner on every
  path, for at most two seconds. A killed owner cannot clean up: before this,
  the inner validator's `mktemp -d` directory stayed after `OWNER_TIMEOUT` when
  the command ran without the Stop interlock. Same rules as the interlock's
  directory below: removed only while it is the same non-reparse directory,
  never through a link or a replaced directory; links inside are unlinked. A
  completed owner whose directory remains refuses as `OUT_OF_PROFILE`
  (`unsupported owner temporary directory`); `OWNER_TIMEOUT` and every other
  outcome is kept. The ten-second owner bound is unchanged and the removal adds
  no execution budget. Control: `forced-owner-timeout` in
  `owner_timeout_controls` now runs with a private temporary lease and requires
  it to be empty afterwards.
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

## DG17-STOP-INTERLOCK-OWNER-CONTAINMENT

- Scope/owner: `windows_owner` in
  `skills/implementaudit/scripts/host-stop-interlock.py`; the selected Stop
  dispatch owns its private job, suspended record owner and temporary output.
  It is a second containment owner beside the validator's inner one above.
- Why: `subprocess.run` with pipes killed only the direct child on timeout and
  then read the pipes without a bound, so a surviving pipe holder delayed or
  prevented the return. The outcome stayed blocking; the bound did not hold.
- Allowed sequence: create job -> set kill-on-close -> create suspended owner
  with file output -> assign -> resume -> owner exits and the job is empty
  inside `policy["timeout_seconds"]` -> return -> terminate and close the job.
- Guards: job creation, configuration and assignment must succeed before the
  owner runs; failure raises `InterlockUnavailable` and the Stop blocks. Overrun
  raises `TimeoutExpired` with the captured bytes and keeps the existing
  owner-timeout block reason. Non-Windows callers keep `subprocess.run`.
- Invariants: no uncontained start; a timely parent exit is not completion
  while the job has members; no breakaway; the job is terminated and its handle
  closed on every path. The two-second reap wait adds no execution budget.
- Differences from the validator's owner: no live-cleanup registry (one owner
  per hook process); a failed handle close is not converted to a refusal.
- Source controls: `interlock_containment_controls` in
  `tests/nonterminal-yield-cases.py` (real local Windows processes, bounded
  Win32 failure injection) and the dispatch-seam test in
  `tests/composite-source-cases.py`. These are not native Stop acceptance.
- Budget: budget revision 5 lets the canonical plugin keep a 1240 B reserve
  instead of 2000 B (usable limit 588584 B) for this correction only; the cap
  and the standalone reserve are unchanged. The margin is a few bytes, so any
  further packaged byte must be re-measured and may need a new owner decision.
- Temporary directory (proposed candidate, not adopted): a terminated job cannot
  run its members' exit handlers, so every temporary directory a member made
  stayed in TMP after an owner timeout. The owner now creates one private
  directory, passes it as `TMPDIR`/`TMP`/`TEMP` to the job only, and removes it
  after the job handle is closed, for at most two seconds. Dimensions: created
  / identity recorded / identity unchanged / link or replaced / removed / owner
  outcome. It is removed only while it is still the same non-reparse directory;
  links inside it are unlinked, never followed. An owner that completed while
  the directory remains is refused with `InterlockUnavailable`; an owner that
  already failed or timed out keeps its own outcome even when the removal does
  not finish. If the directory cannot be read during removal (it vanished, or
  `lstat` fails) or its identity was never recorded, the loop ends without
  deleting and the same two outcome rules apply; no other exception replaces
  them. The two seconds follow the owner bound and add no execution budget.
  Controls: the three `temporary-*` cases of `interlock_containment_controls`.
  The job limits are passed as a raw buffer with the same bytes and size as
  the former structures (144 B on 64-bit, 112 B on 32-bit, flags at offset 16).
  Budget: the whole correction (this owner, the validator's owner and the pin
  closure) measures 588538 B at the 8754 identity, 46 B below the usable limit
  of 588584 B; cap and reserves are unchanged. The bytes were recovered by the raw
  limit buffers and by shortening comments whose original wording is kept in
  DG17-RELOCATED-SOURCE-COMMENTS.
- Status: source-qualified on one Windows host. Native Stop, original14 and
  host behaviour on hook overrun remain unreceived. Abrupt external termination
  between suspended creation and assignment is outside these controls; this is
  not a universal no-orphan certificate.

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
- Owner temporary-directory generation (proposed candidate, not adopted): the
  validator change above forces one more additive generation of this closure.
  New profile `composite-20261114-dg17-owner-temporary-v1-core`, pair
  `_WINDOWS_DG17_OWNER_TEMPORARY_CORE8_PAIR_V1`, one retained-predecessor row in
  the route peer, one route-producer row in both compilers, and
  `dg17_owner_temporary_preimage` entries in the route-graph manifest. Every
  earlier profile, pair, row and preimage is unchanged. The changed compiler has
  its own C5 source revision, V11 (see C5-EXPLICIT-CURRENT-VERSUS-FROZEN-SOURCE).

## DG17-RELOCATED-SOURCE-COMMENTS

- Why: the canonical plugin budget left no room for the owner temporary-directory
  correction. Packaged comments were shortened in place instead of raising a cap
  or a reserve. The original wording is kept here, byte for byte, so that no
  statement is lost. Each short form states the same rule; where the two differ
  in detail, this text is the full statement. Neither form grants authority.
- Source: `skills/implementaudit/scripts/host-stop-interlock.py`. Original comment
  lines, by enclosing function:
  - `plugin_store`:

        # Same owner mapping as codex-recovery-prompt-input.py. Native scratch
        # names may collide; the physical marketplace/plugin pair cannot be
        # inferred from that flattened string and remains the H0 authority key.

  - `optional_directory`:

        # An ordinary session need not have created plugin data. Validate the
        # physical existing ancestor without creating or enumerating anything.

  - `emit`:

        # Codex StopCommandOutputWire denies unknown fields. Proof metadata
        # belongs in private receipts, never in the native control response.

  - `main`:

        # No supported issuer/grant verifier is selected for this host. Readable
        # attribution, purpose labels, reentry flags and historical receipts
        # cannot authorize a current dependent effect. Do not call route,
        # compiler, disposition, consumption or lifecycle owners here.

  - `selected_codex_stop`:

        # Failure is still an observation. Do not lose the selected event and
        # validator diagnostics by escaping before the receipt is durable. The
        # exception message/command may contain unrelated sensitive arguments;
        # retain its type and bounded partial streams instead.

  - `block_reason`:

        # Both outcomes block. Only the instruction differs: nothing in a record
        # can be corrected when its owner never completed the bounded read.

  - `windows_owner`:

        # Private kill-on-close job, file output: a killed direct child can leave
        # descendants holding output pipes past the bound. As the validator's own
        # owner: never start uncontained; complete only when the job is empty.
        # The job's temporary directory is removed after it, never through a link
        # or a replaced directory; a completed owner that leaves one is refused.

- Source: `_NATIVE_ROUTE_PRODUCER_PROFILES_V1` in both copies of
  `compile-work-graph.py`. Four row comments were replaced by one pointer line
  (`# Row provenance: SOURCE_MANIFEST.json; no native credit.`). Their wording is
  kept under `route_producer_profile_provenance` in
  `source-peers/route-graph/SOURCE_MANIFEST.json` and here, keyed by the row each
  comment preceded:
  - `1bf45fa3104dcde045fcd528d57b601323e9476dcb735afdd88b1c27dde8e9ca`:

        # Exact retained-source-map receiving delta from R0033 donor79316011.

  - `d060782e690d163e2b0db014be429c64cf976e7b1e8d554113ee8f4843a3b1bb`:

        # Exact nonblocking delivery capture received from R0033 donor899d32f8.

  - `87bce990c85c7db9134c788eb14d9d5d5b38c55091fa47b256396ffc99316bbe`:

        # DG07 exact original14 recovery receiving and safe binder source pair.

  - `f43f27cf176a16ea4b1f24b3639313ade487f9a1cab77ad4cd1b8543987feb9e`:

        # Exact DG08 source-only predecessor binding; no native credit.

- Not changed: code, docstrings, messages, and every comment not listed here.
- Guard: `STATEMENT_MAP.md` of the candidate return lists each old and new line.
  A later edit of a short form must keep this section true or update it.

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
- Successors (proposed candidate, not adopted): V10
  (`R5_BUDGET5_BUILDER_SOURCE_REVISION`) names the actual package builder
  through its own base member; V9 keeps its original base. V11
  (`R5_DG17_OWNER_TEMPORARY_SOURCE_REVISION`) differs from V10 only in the
  compiler pin and is what the held loader pin now selects. V9 and V10 keep the
  8754 compiler through the explicit member in
  `test-support/r5-dg17-composed-compiler-history/` (its `MANIFEST.json` also
  fixes the V1-V10 tables). Dimensions: revision / compiler pin / physical
  compiler member / held loader pair. Current compiler bytes at the retained
  member, retained bytes at the current path, and a V10 loader facing the
  current compiler all refuse; none is searched for or substituted.
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

## G2-REPORT-SLOT-POPULATION

- Scope: DG16 full-G2 candidate (`qualification/dg16-r5-full-g2/`) on frozen product
  `e76a07b2`. One declared profile, `REPORT_SLOTS.json`, against the unittest reports
  that the frozen registry actually writes to stderr in each route.
- Sources: `scripts/verify-package.sh` (91 `bash tests/*.test.sh` lines) -> each wrapper
  -> every program ending in `unittest.main` or `TextTestRunner`; receiver
  `full_output_relation.report_elapsed_relation`, called on the whole stderr of the
  legacy and the DAG route by `full_relation.whole_projection`.
- Dimensions: declared slots (static derivation) / emitted framed reports (runtime) /
  timer lines / per-slot test count, order and identities. They are independent: a
  correct per-slot profile still refuses when the two populations differ by one.
- Guard: `len(reports) == len(slots) == timer lines`, else `REPORT_SLOT_MULTIPLICITY`,
  before any per-slot check. It refuses only at receiving, after both legs have run.
- Observed (static, 2026-11-13): `verify-package.sh:762` runs
  `tests/eval-harness.test.sh`; its line 14 runs `eval/test_process_identity.py`
  (`unittest.main(verbosity=2)`, 11 tests, stderr not redirected). The profile declared
  110 slots / 2057 tests and no `eval/` member in `source_closure`. Of 119 emitters
  outside `test-support/`, this was the only undeclared one named by a wrapper.
- Populations: 110 / 2057 is the original derivation and stays in historical records.
  111 / 2068 is the corrected current population (owner-approved), with the new slot
  at ordinal 80. The literals also live in `full_relation.py`, `POLICY.json` and
  `receiver/BINDING_TEMPLATE.json`.
- Retained exception: `CAPTURE_DIAGNOSTIC_CATALOG.json` belongs to the witnessed
  transport component and was left byte-identical. Its `report_slots_sha256` names the
  110-slot profile and no source reads it; failure diagnostics lack the 11 added
  identities and index slots 80 and above one too low.
- Unknown: the cause of G212 (run 43169134057) `REPORT_SLOT_MULTIPLICITY`. Its stream
  was not retained; the recorded private-message digest is the hash of the code string.
  This entry describes current source and does not explain that run.
- Hypothesis, not observed: no actual stream has yet shown 111 reports in either route.
- Gap: no automated emitter census exists. The derivation is hand-maintained, so any
  wrapper or `eval/` change that adds, removes or redirects a unittest program can
  break the equality silently until a full run. Evidence of the manual census and the
  fixture control is in the review return (`g2_emitter_reach`, `g2_slot_RED_GREEN`).
- Failure/recovery: a refusal here cannot be repaired in place. Correct the profile and
  its literals, re-pin (see G2-CANDIDATE-PIN-FIXPOINT), reseal and re-review before
  another pair. Never infer a missing count from a later run.

## G2-CANDIDATE-PIN-FIXPOINT

- Scope: plain SHA-256 file pins among the 63-member full-G2 candidate. No generator
  owns them; each correction so far was propagated by its author.
- Sources and edges: `REPORT_SLOTS.json` -> `RELATION_INPUTS.json` (digest and bytes)
  -> `POLICY.json` (`receiver_inputs_sha256`; `full_receiver_sha256` for
  `full_relation.py`) -> `pair_driver.py` (`POLICY_SHA`, `RELATION_INPUTS_SHA`,
  `FULL_RELATION_SHA`) -> `run.py` (`PAIR_DRIVER_SHA` and the same three) ->
  `.github/workflows/dg16-r5-full-g2.yml` (20 `run.py` pins) -> `receiver/BINDING_TEMPLATE.json`
  and `receiver/ROOT_BINDING_TEMPLATE.json`.
- Dimensions: member bytes / every pin literal naming that member. A member can be
  correct while a host still names an earlier body of it.
- Invariant: for every pair where the base host held the digest of the base member, the
  final host holds the digest of the final member. The graph is acyclic, so a fixpoint
  exists.
- Transition rule: after any member edit, replace every digest that member has ever had
  (base and each intermediate) by the digest of its final bytes, in every other text
  member, and repeat until nothing changes. Replacing only the base digest is wrong:
  hosts re-pinned in an earlier round keep an intermediate that later rounds no longer
  recognise.
- Guards at run time: `run.py` (`PAIR_DRIVER_DIGEST_REFUSED`), `pair_driver.py`
  (`FULL_POLICY_OR_INPUT_BINDING`, which also requires the policy and input files to be
  byte-equal to their canonical encoding), and the workflow adapter pins. They refuse a
  stale pin before either leg, so the failure is early but costs the single-use ref.
- Named exceptions: `SEAL.json` is the Root seal over the candidate and is reissued,
  never rewritten by propagation. The `report_slots_sha256` field of
  `CAPTURE_DIAGNOSTIC_CATALOG.json` is retained provenance (see G2-REPORT-SLOT-POPULATION).
- Retained finding OG2-1 (2026-11-13): the first 111-slot patch pinned six members to
  intermediate bodies and would have refused its own pins. Opus found it by review; the
  re-pinned set converged in four rounds and changed only 64-hex literals.
- Verification: the review tools `pinforward.py` (every base pin forwarded to the final
  digest) and `newliterals.py` (a census of new digests), kept with the Opus return.
  The latter's two reported external digests were independently matched to the actual
  product's `eval/reconcile.py` and `eval/test_process_identity.py`; its raw two-item
  failure is not relabelled as a pass. Neither tool is in the repository. Unknown: whether any pin of
  these members exists in a non-plain form (normalized or AST digest). None was found.
- Failure/recovery: a failed check holds the candidate. Re-run propagation from the
  immutable base plus the semantic edit; do not hand-edit single literals.

## G2-SEALED-RECEIVER-AND-LIVE-OUTPUT

- Scope/owner: Root's full-G2 public receiver installation and live/terminal
  acquisition. The maintained owners are `root_operator.py:OperationalSession`,
  `public_operator_v2.py:control_source`, and
  `prepare_live_control.py:verify_seal` in the DG16 receiving source.
- Dimensions: the seven immutable receiver files and seal; runtime output root;
  per-role write-once journal; actual acquisition; independent live review;
  later Root control preparation. Source verification alone proves no live step.
- Original guards: each role requires a fresh journal directory; the later
  control consumer requires the receiver directory's complete file population
  to equal its sealed members plus `SEAL.json`.
- Invariant: runtime output must be disjoint from the sealed receiver source.
  If `receiver_output_root` names that source directory, successful acquisition
  writes `live/*` beneath it and necessarily causes the later seal check to fail.
- Observed source defect: an unlaunched successor binding selected the same
  directory for both roles. It was retained unchanged; no native effect or
  original acceptance is attributed to that binding.
- Correction: a fresh binding uses a separate `public-acquisition` sibling for
  role outputs. The hosted source, report profile, recipient and witnessed
  component are unaffected. Refresh only the local runtime, composition,
  receiver and dependent operator bindings and their independent receiving.
- Failure/recovery: preserve the defective sealed view and any actual effects;
  never ignore extra seal members, move a live journal, or replay an uncertain
  role to make a source check pass. Current operation records own the actual
  paths, review identities and effect state.

## DG16-TOOL-RESULT-AND-NATIVE-LOG-PROJECTION

- Scope/owners: Root's first-party GitHub calls, the actual returned tool value,
  the native `McpToolCall` event projection, and the selected receiving protocol.
  `root_native_history.py:receive` requires the complete original byte count and
  digest; the G1 framed role retains actual complete results supplied by Root.
- Independent dimensions: call completion; complete returned value; native-log
  representation; authenticated custody; receiver disposition. A completed call
  does not establish that its native-log projection contains the complete value.
- Observed boundary: a G124 workflow response was 80,067 bytes, while its native
  log contained a 65,521-byte text projection without `structuredContent`.
  The strict history reader refused the mismatch. Root retained the complete
  actual first-party response directly, and the original G1 framed role received
  its exact bytes; the truncated log was not credited as complete history.
- Relevant control: the exact G213 workflow response was 49,617 bytes and matched
  its complete native event. This is evidence for that response, not a universal
  transport limit or a promise about future source changes.
- Invariants: never reconstruct missing native bytes, substitute a text projection
  for the original result, or infer authenticity from matching labels. Preserve
  the selected protocol's actual provenance requirements. G2's exact history
  comparison remains unchanged; incomplete history must still refuse.
- Failure/recovery: reconcile the actual call and retained carriers before any
  further operation. Ordinary read-only preflight observations and protected
  one-shot role effects are distinct; a lost protected frame is not replayable.
