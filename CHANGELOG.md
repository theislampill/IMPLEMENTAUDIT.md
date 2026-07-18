# Changelog

All notable changes to this project are recorded here.

This project follows Keep a Changelog style. Historical entries marked
`Reconstructed` are reconstructed from repo history and conversation context,
not from verified tags, releases, publication, marketplace verification, or
provenance.

Plugin manifest versions are host-facing package metadata. The `v0.3.1.0`
source milestone maps to plugin manifest version `0.3.1` because no local
schema evidence proved four-component plugin manifest versions are accepted.

## [Unreleased]

### Added

- Proof-level taxonomy and claim discipline (#53, `IA-PROOF-LEVELS`):
  PL1-PL7 taxonomy defined in `docs/audits/RETENTION.md` (prose presence,
  runtime instruction, template requirement, structural validation,
  fixture demonstration, observed live behavior, fresh-executor proof),
  composing with the per-command structural/behavioral/provenance evidence
  properties rather than replacing them. Active surfaces using
  verdict-class wording now require a same-line proof-level qualification —
  enforced by an extended `check-public-claim-boundaries.sh`; archives stay
  exempt history and are never rewritten. `docs/audits/INDEX.md` now
  surfaces the three archived proof ledgers with their qualifications; the
  final-report template gains proof-level Claim Rows; the eval A-series is
  explicitly labeled PL4/PL5 pending owner-approved runs. New
  claim-boundary fixtures (one positive, two path-exempt negatives) and
  registered test `tests/claim-boundary-proof-levels.test.sh` with probe
  negative controls.

- Ordinary-invocation behavioral evaluation campaign (#52,
  `IA-EVAL-ACTION-SELECTION`): new SUPPLEMENTARY A-series fixtures A1–A5 in
  the eval harness — factor-derived action selection (A1), actual bounded
  fanout (A2), reconstructible phase specs with host-observed
  validate-phase and cold-executor-replay verdict flags (A3), independent
  cold review gating handoff (A4), STOP compliance and honest terminal
  classification (A5). Every mission is ordinary and task-shaped with no
  activation keywords; every fail transcript encodes one of the issue's
  negative traps (keyword-gated depth, table-only coverage,
  unreconstructible spec, self-critique-only handoff, closure overclaim).
  Separately versioned like B3; never folded into the frozen primary
  campaign; validated by the selftest (21 fixtures); real model runs remain
  owner-approved under the #9 posture in disposable repos — until then the
  campaign is structural capability, feeding proof-level discipline (#53).
  No harness safety-posture change: no default networked baseline, no
  provider client, four-valued verdicts preserved.

- Independent cold-review gate and derivative execution index (#51,
  `IA-ACTION-COLD-REVIEW`): new Stage 6.2 — whenever the run produces a
  handoff or executor-ready phase artifact, an independent cold review runs
  before preflight, dispatch, or handoff. Independence is structural: a
  separate fresh-context child agent where the host supports subagents,
  otherwise a bounded serial fresh-context pass that excludes the authoring
  context. Disposition PASS / GAP-REVISE / BLOCKED / OWNER DECISION is
  recorded in the audit object (THINKING field; ROADMAP Review column);
  Stage 6 self-critique is preserved, not replaced; no "review" keyword and
  no review-plan mode. The roadmap gains an `Execution index (projection)`
  section documented as derivative, never canonical. New reviewer lane in
  `child-agents.md`; contract text in `plan-lifecycle.md`; two positive and
  four negative fixtures under `fixtures/cold-review/`; new gate
  `scripts/check-cold-review-contract.sh` + registered test
  `tests/cold-review-contract.test.sh` with embedded negative controls.

- Binding specialist-fanout coverage contract (#49, `IA-ACTION-FANOUT`):
  materially broad audits trigger actual bounded specialist lanes — parallel
  when the host supports subagents, serialized as separate bounded written
  review passes carrying the same per-lane contract when it does not; a
  coverage table documents executed lanes and never substitutes for them;
  warranted lanes are never silently dropped (skipped lanes carry reason +
  residual risk into the final audit). Coverage-lane records added to the
  THINKING template; per-lane prompt contract (audit-playbook headings incl.
  Finding Row Contract, recon facts, risk hints,
  findings-only/no-dumps/read-confirmation) enforced on child prompts by
  `check-plan-quality-contract.sh`; exemplar auditor prompts upgraded; new
  positive fixtures (broad-scope four lanes, low-concurrency serialization)
  and negative fixtures (table-only coverage, silent lane drop, generic
  single pass, fanout-free child prompt); new gate
  `scripts/check-fanout-coverage-contract.sh` + registered test
  `tests/fanout-coverage-contract.test.sh` with embedded negative controls.

- Phase reconstructibility contract (#50, `IA-PHASE-RECONSTRUCTIBILITY`):
  newly authored phase specs carry an ordered `## Implementation steps`
  section (exact file/symbol targets, per-step verify command with expected
  success shape), `## Scope boundaries` with an explicit `Out of scope:`
  line, and plan-specific `## STOP conditions`. `validate-phase.sh` rejects
  vague step language ("update the relevant files", "make it work"),
  per-step-verification gaps on multi-step work, and boilerplate STOPs —
  legacy specs without ordered steps pass with a warning (same precedent as
  evidence-property tags). New Rule P4-10 in `phase-design.md`; read-only
  handoff lane aligned (`## Ordered Steps` in `read-only-plan.md`); four
  canonical phase fixtures upgraded to the new shape; three mechanical
  negative fixtures plus a review-lane counter-example
  (`fixtures/phase-design/negative-paths-without-symbols.md`); source-gate
  pins in `check-plan-quality-contract.sh`.

- Action-selection contract (#48, `IA-ACTION-DEPTH`): ordinary task-shaped
  invocations derive the warranted `ydqyq-audit-action` set from scope,
  uncertainty, risk, dependencies, evidence gaps, authorization state, and
  intended executor — recorded both ways (selected and omitted-with-reason),
  never keyword-activated. New contract section in
  `skills/implementaudit/references/planning-depth.md`, Stage-1 derivation line
  in `SKILL.md`, `## Action selection` blocks in the THINKING/ROADMAP
  templates, fixture family `fixtures/audit-action-selection/` (two positive,
  three negative), checker `scripts/check-action-selection-contract.sh` with
  `--repo-root` support, and registered test
  `tests/action-selection-contract.test.sh` with embedded negative controls.

### Fixed

- Payload scorer robustness (post-merge, Fable re-audit of #13/#12/#15):
  `check-handoff-packet.sh` and `check-authorization-binding.sh` used a
  `grep | head | sed` field helper that, under `set -euo pipefail`,
  aborted the whole script whenever a queried field was ABSENT — so the
  contradiction/drift logic was silently skipped and the checker exited
  without naming the abnormality (fail-closed but for the wrong reason).
  Field lookups now swallow grep no-match to empty; a minimal-field
  contradicted packet and a no-`binds:` authorization now reach and emit
  their intended verdicts (regression tests added). `check-lesson-lift.sh`
  hardened the same way. Removed a stray empty `fixtures/governing-rule/`
  fixture left over during the suspect turn (unreferenced).

### Added

- B3 supplementary eval fixture (#35, context-epoch continuity): a
  stale-steer-replay-after-context-boundary fixture that scores whether a
  resume records the continuity boundary with honest provenance, rereads
  live STATE/ROADMAP before mutation, classifies a satisfied one-shot
  ('fix ANDON 150') as satisfied/superseded, refuses to replay it, and
  continues from the active item. Validated by the selftest (PASS/FAIL
  transcripts) but deliberately NOT part of the frozen 14-fixture primary
  campaign — it runs as a separately versioned supplementary baseline
  (1 fixture x 2 configs x 3 reps).

- Governed state-space convergence mode (#11, EXPERIMENTAL/optional): a
  new references/convergence-mode.md loaded ONLY when its trigger fires
  (two same-family review rejections, or a #7 under-specified-state-space
  judgment) — bounded read-only discovery -> enumeration artifact ->
  generated RED fixtures -> one coherent repair -> exactly one outer
  qualification. NOT core protocol and NOT in the bootloader path; core
  adoption is gated on a #9 model-in-the-loop evaluation of the two
  adoption-gate fixtures (3-dimension under-specified machine + single-
  fault negative control), which has not been run. Zero burden on
  ordinary runs.
- Parameter-bound authorization (#12): an authorization enumerates the
  consequential parameters it binds (values or ranges), not just the
  action. A runtime parameter that affects the authorized action and is
  absent from or conflicts with the record is AUTHORITY DRIFT — classify
  (owner-unclear/authority), stop the governed action, request an owner
  decision; source/tool defaults are never implicitly adopted for a
  governed parameter. Ordinary small authorizations stay one line. New
  payload check-authorization-binding.sh; match/drift fixture pair.
- Final-audit success-surface indexing (#14): each closure claim is a row
  indexed to the surface that establishes it (source / generated /
  package / installed / running-local / deployed / api / user-visible /
  publication); a claim closes only with evidence FROM that surface —
  lower-layer evidence is never promoted. Verification status (verified /
  failed / unverified / not-applicable) stays separate from residual
  disposition (#6). Uninspectable authorized surface routes to
  unverified/deferred, never a fabricated substitute, and never triggers
  an unauthorized network/deploy check. Source/docs/library-only work
  keeps a single source row. New payload check-closure-surface.sh; five
  fixtures.
- Receiving-side handoff inspection (#15): before accepting a handoff
  packet from another run, the receiver verifies packet identity and
  three claim classes — mechanically recomputable state (receiver
  re-derivation wins), evidence references (rebound via #4 anchors), and
  owner/authorization claims (preserved verbatim, only the issuing
  authority may amend). A contradicted Class-1/2 claim raises a named
  abnormality and blocks ONLY dependent execution (never restarts the
  audit, never silently normalizes). New payload check-handoff-packet.sh;
  four fixtures (contradicted-blocks, matching-proceeds,
  owner-carried-verbatim, no-claims control).
- Lesson-lift routing record (#13): a qualifying lesson produces ONE
  canonical lift record that unifies AGENTS_UPDATE_DECISION and
  CONTINUITY_DECISION (nine fields: lesson, lift/no-lift + reason,
  destination, authority, encoding written, mechanically active,
  installed current, recurrence class, later prevention evidence).
  Bounded trigger — one-off fixes record at most a single No-lift line.
  Closure may claim only encoding-written / mechanically-active /
  installed-current; 'recurrence prevented' is future evidence and fails.
  New payload scorer scripts/check-lesson-lift.sh; seven fixtures in
  tests/lesson-lift-contract.test.sh.
- Second-order recurrence review (#7): ANDON_ESCALATE now evaluates
  whether the GOVERNING rule (class / evidence standard / validator /
  route) produced or concealed the defect — triggered by same-class
  recurrence, first-occurrence direct evidence of a mis-scoped or
  correct-by-luck check, or cross-class shared invariants.
  Neighboring-perturbation probes are admissible even when the answer was
  correct; answer-correctness and pathway-adequacy stay separate
  judgments; rejecting suspicion requires a recorded reason (bare 'no'
  fails). New Hansei governing-rule-suspicion field; five scored
  fixtures in tests/andon-escalation-judgment.test.sh.
- Route-sufficient decision rule (#6): three never-merged
  representations — occurrence-resolution state (unresolved /
  partially-resolved / resolved), audit-completion state (markers,
  unchanged), and per-residual dispositions (unresolved / deferred /
  transferred / owner-assigned / risk-accepted / validated-resolved;
  owner/policy-assigned, never automated). Established hazard + admissible
  safe route => contain BEFORE root cause; partially-resolved with named
  residual rows is partial-by-design — not a failure, not closure.
  AUDIT_COMPLETE now requires every consequential residual non-unresolved
  and audit-scoped completion language (full-resolution claims over
  unresolved residuals are false-closure). STATE.md section + validator
  token checks + five fixtures.
- Andon occurrence linkage (#5): the Andon log gains an `Occ` column —
  one class per row, one or more linked rows per occurrence — so plural
  co-occurring defects keep their linkage while per-class recurrence
  citation (ANDON_ESCALATE) is unchanged. Legacy tables without `Occ`
  remain valid and resume safely; validate-run-root.sh detects the table
  generation, requires a non-empty Occ id on new-format rows only.
  Fixtures: legacy-accepted, linked-plural-accepted, missing-occ-rejected.

- Evidence property tags (#3): every mandatory command in a phase spec
  declares `property: structural|behavioral|provenance` plus a
  plain-language scope (authorization stays a separate gate, never a
  property). validate-phase.sh rejects invalid tags and mixed
  tagged/untagged specs, and warns (without failing) on fully untagged
  legacy specs; the final audit may not claim a property class no
  command exercised; ANDON_ESCALATE asks whether the check tests the
  property the claim needs. Shipped fixtures migrated; three new
  validator fixtures in tests/phase-validation.test.sh.

- Long-running/background command contract (#2): new PROTOCOL section —
  detached launch with `launch-intent.md`, append-only
  `chain-status.txt`, `chain.done` completion marker; state model
  running / succeeded / failed / aborted / terminal-state-unverified /
  contaminated / infrastructure-failed; a missing completion record is
  never a failure verdict; aborts kill only the owned tree and record
  possible sibling contamination; infrastructure signatures ground
  SUSPICION only — producer countermeasures are prohibited until origin
  is classified. SKILL.md pointer added; six state-transition fixtures
  in `tests/background-chain-contract.test.sh`.

- Evidence-version anchoring (#4): `detect-env.sh` Stage-0 output now
  names `head=<short-sha> (<committer-date>)`, `upstream=<ref>
  behind_ahead=<L/R>` or `upstream=none`, and
  `remote_freshness=not_checked` (read-only; local tracking-ref
  divergence never implies remote freshness). Smoke A/B and Andon
  rerun-evidence rows record an Anchor (full 40-hex commit SHA at
  capture; legacy rows stay valid); new payload consumer check
  `scripts/check-evidence-anchor.sh` refuses a verdict artifact anchored
  to a different tree than the one it is offered for, and
  `validate-run-root.sh` fails short-sha anchors. Pinned by
  `tests/evidence-anchoring.test.sh`.

- Andon taxonomy (#1): three new official abnormality classes —
  `transport-infrastructure` (environment-level failure incl. blocked
  review channels, with a normative preserve-and-reissue disposition),
  `misplacement` (right layer, wrong instance/copy), and `false-closure`
  (closure-state accounting collapses non-resolved states) — with
  normative boundary definitions against `hung-command`,
  `generated-artifact-mismatch`, and `evidence-mismatch`, and seven
  boundary fixtures in the transcript contract. The three duplicated
  class enumerations (SKILL.md, templates/PROTOCOL.md,
  references/transcript-contract.md) are now pinned to each other by
  `tests/andon-class-contract.test.sh` (set equality + required
  membership; no fixed-total assertion).

## [v0.3.1.0] - 2026-06-14

### Added

- Moved the skill source to the conventional `skills/implementaudit/` layout
  while keeping the release archive flat and self-contained for installation.
- Kept the runtime bootloader concise and moved detailed operating guidance
  into progressive references and templates.
- Added a read-only plans lane for audit, review, and planning tasks that
  should not mutate source.
- Added source-evidence packaging so validators and fixtures can be inspected
  and run outside the installed skill payload.
- Added package-boundary, validation-registry, audit-retention, docs-portal,
  dogfood-bootstrap, and bootloader-budget checks.

### Changed

- Strengthened final-report, sidecar-boundary, no-secret planning,
  repo-content-as-data, Andon/Hansei, and 5-Whys loop-exit guidance without
  expanding the always-loaded runtime surface.
- Kept generated/local artifacts, sidecar outputs, raw transcripts, run roots,
  tests, and fixtures out of the shipped `.skill` package.
- Bumped host-facing plugin metadata from `0.3.0` to `0.3.1` for this source
  and package milestone.

### Boundaries

- No license decision, issue publication, provenance claim, marketplace claim,
  or real-home installation is included in this release.
- Source evidence remains source-repo evidence only; it is not shipped in the
  runtime `.skill` payload.

## [v0.3.0.0] - 2026-06-13

### Added

- **Finding:** IMPLEMENTAUDIT did not yet route the full source-inventory set:
  audit-object-grounded category pressure, deep/security analysis,
  direction planning, branch/diff scoping, self-contained handoff-plan quality,
  plan review, execute/review dispatch semantics, reconciliation, and explicit
  issue-publication deferral.
- **Countermeasure:** added shipped references
  `skills/implementaudit/references/audit-category-matrix.md` and
  `skills/implementaudit/references/plan-lifecycle.md`; wired the category/deep/security/
  direction and plan lifecycle contracts into `skills/implementaudit/SKILL.md`,
  `skills/implementaudit/templates/THINKING.md`, `skills/implementaudit/templates/PROTOCOL.md`, and
  `skills/implementaudit/templates/phase-goal.txt`; added audit-object-routing fixtures and focused
  tests; extended routing/planner/lean/package validators and CI wiring; updated
  README, CONTRIBUTING, portal source, audit index, AGENTS.md, manifest, and
  package/install allowlists for manifest `0.3.0`.
- **Rejected/deferred behavior:** external command identity is not copied; root
  `plans/` is not made canonical; read-only audit-object closure identity is not adopted as
  IMPLEMENTAUDIT's default; arbitrary review/revision caps remain forbidden;
  issue publication stays deferred behind a future explicit publication gate.
- **Evidence / poka-yoke:** new fixtures in `fixtures/audit-object-routing/` and tests
  `tests/audit-object-routing.test.sh`,
  `tests/audit-object-plan-lifecycle.test.sh`, and
  `tests/issues-deferred-gate.test.sh`, plus
  `tests/audit-object-routing-contract.test.sh`; validators now require the new
  shipped references, package entries, manifest version, and issue-deferred
  behavior.
- **Runtime terminology KISS reduction:** a broad 195-line draft terminology
  reference was rejected by Andon/KISS review and replaced with the shipped
  thin cross-reference contract `skills/implementaudit/references/terminology-integration.md`.
  Term-specific behavior is owned by existing routing, Lean, phase-design,
  plan-lifecycle, and category/security references; compact fixtures in
  `fixtures/terminology-integration/`, `scripts/check-terminology-integration.sh`,
  and `tests/terminology-integration.test.sh` guard against orphan terms,
  glossary theater, duplicate authorities, generic SOLID/FMEA/STRIDE advice,
  active C4 adoption without a fixture, and a recreated second glossary.
- **Boundary (source milestone):** the milestone / runtime-integration work above
  was authored as a source milestone and local package-validation target;
  authoring it claimed no commit, push, tag, GitHub release, publication,
  provenance, issue creation, or installed-host update. The release actually
  performed at the v0.3.0.0 release gate is recorded under **Released** below.

### Fixed

- **Finding (local-package dogfood):** `scripts/verify-package.sh` failed on a
  Windows + ActiveGraph machine with `sqlite3.OperationalError: unable to open
  database file`, traced to `tests/custody-append.test.sh` — the only failing
  gate. Linux CI never saw it (ActiveGraph absent → the helper's absent-safe
  path).
- **Root cause:** the test normalized POSIX→Windows store paths only when the
  detected `activegraph` command name ended in `.exe` / lived under `/mnt`. On
  Git Bash `command -v activegraph` resolves to a bare shim name, so
  normalization was skipped and an MSYS path (`/c/...`) was interpolated into the
  `sqlite:///` inspect/export-trace URL; MSYS auto-converts standalone path
  arguments but not paths embedded mid-string, so native `activegraph.exe` could
  not open it.
- **Countermeasure:** detect the conversion need from the shell environment
  (`uname -s` ∈ `MINGW*|MSYS*|CYGWIN*`) as well as the command name, applied to
  both URL paths. Additive and platform-safe (no-op on plain Linux; prior
  `.exe`/`/mnt` triggers preserved). The shipped `custody-append.sh` was not
  changed — its write path is a standalone arg MSYS auto-converts.
- **Evidence / poka-yoke:** `tests/custody-append.test.sh` and
  `scripts/verify-package.sh` now pass on the dogfood machine; anti-repeat rule
  `V0300-MSYS-URL-PATH-NORMALIZATION` added to AGENTS.md. Closure ledger:
  `docs/audits/archive/v0.3.0.0-local-package-dogfood-audit.md`.
- **Remaining risk:** none for shipped runtime (test-only change; payload
  unchanged, `.skill` byte-identical).

### Released

- Tagged `v0.3.0.0` and published the GitHub release on 2026-06-13 under explicit
  per-action release-gate authorization, after the local-package dogfood
  (`docs/audits/archive/v0.3.0.0-local-package-dogfood-audit.md`) and all local, package,
  and remote gates passed.
- Release asset `IMPLEMENTAUDIT.skill` (deterministic committed-tree build):
  SHA-256 `25e978dd305706af956be0f65f3ab4b3ba882768790c9b0da92fe4bedd0e57b4`,
  112509 bytes, 33 entries. Plugin manifest version `0.3.0`.
- Provenance is a checksum manifest only — not a signature, attestation, SBOM,
  license, or marketplace verification. No issues were published. Codex installs
  remain a manual copy; no passive installed-host refresh is claimed.

## [v0.2.9.0] - 2026-06-10

### Fixed

- **Finding:** the shipped skill package contradicted its own Lean/Jidoka identity. `skills/implementaudit/SKILL.md` correctly required execution "until terminal audit closure or an explicit audited handoff" with no artificial caps, but `skills/implementaudit/references/transcript-contract.md` (shipped in the package payload) defined a terminal three-strike failure sequence whose third strike set STATE.md to BLOCKED, stopped the run, and prevented subsequent phases; `skills/implementaudit/templates/PROTOCOL.md` shipped the same strike ladder plus a hard cap of three final-audit rounds; the README execution-spine diagram advertised both.
- **Root cause:** the v0.2.6.0 hardening round adapted an external staged-goal reference's exact strike-count recovery and capped audit-fix loop as an anti-skip countermeasure, overcorrecting an ordering rule (do not jump straight to handoff) into arbitrary terminal try/round caps — a Jidoka contradiction (handoff driven by a counter, not by a blocking condition).
- **Countermeasure:** replaced the strike ladder with Jidoka Andon escalation. New markers `ANDON_PROBE` → `ANDON_ESCALATE` → `ANDON_HANDOFF` (legacy FAILURE-prefixed spellings retired; the marker-order checker still rejects legacy handoff+completion transcripts). `ANDON_PROBE` fires on the first abnormality of any class (failed criterion, regression, hung/substituted command, unclear owner/source, generated-artifact mismatch, stale sidecar, policy conflict, evidence mismatch) and records abnormality, failing criterion/command/artifact, owner/source, containment, proportional 5 Whys, Hansei, selected countermeasure, and required rerun evidence; a fix must follow from the probe, not the symptom. `ANDON_ESCALATE` fires on countermeasure failure / same-class recurrence / unclear root cause / scope-expanding fix / disputed owner, and records prior probe history, why the first countermeasure failed, deeper 5 Whys, and the chosen path (split, reframe, rollback, owner decision, or bounded fix-spec). `ANDON_HANDOFF` fires only when closure is blocked by owner decision, unsafe scope, missing authorization, external dependency, irreproducibility, missing required tool/access, or no bounded countermeasure remaining — never by a try count. Final-audit audit-fix rounds now loop until closure or audited handoff with no fixed round cap.
- Updated surfaces: `skills/implementaudit/references/transcript-contract.md`, `skills/implementaudit/templates/PROTOCOL.md` (Jidoka chain, Andon escalation protocol, final-audit rounds), `skills/implementaudit/SKILL.md`, `skills/implementaudit/references/goal-format.md`, `skills/implementaudit/references/phase-design.md`, `skills/implementaudit/references/lean-operating-discipline.md`, `docs/diagrams/execution-spine.mmd` + regenerated README diagram block, `docs/portal/onboarding.md`, `fixtures/phase-design/full-hardening-run.md`, `AGENTS.md` (marker contract; amended V0_2_6_0_FAILURE_RECOVERY_ORDERED), `scripts/check-marker-order.sh` (ANDON exclusivity, probe-first, ordering; legacy spelling still rejected), `tests/marker-order.test.sh`, `scripts/verify-package.sh` (marker set, version pin), `scripts/check-lean-discipline.sh` (Jidoka needle).
- **Evidence / poka-yoke:** new `scripts/check-no-terminal-cap.sh` forbids terminal-cap wording (strike counters, capped audit rounds, run-stopping phrasing, legacy marker spellings) in runtime-shaping surfaces (skills/, docs/diagrams/, docs/portal/, fixtures/, README.md, AGENTS.md), with CHANGELOG.md and docs/audits/ exempt as legacy history; `tests/no-terminal-cap.test.sh` proves the gate and the exemption. Closure ledger: `docs/audits/archive/v0.2.9.0-andon-escalation-jidoka-repair.md`.
- **Remaining risk:** hosts parsing the retired FAILURE-prefixed markers from new transcripts will not see them; legacy transcripts remain readable and the exclusivity rule still applies to them.

- **Audit-fix round G1–G3 (2026-06-10), from the self-dogfood audit:** (G1) repaired the residual try-counter wording in `skills/implementaudit/templates/PROTOCOL.md` Jidoka chain ("after any probe, escalation, substitution, regression, or evidence mismatch") and tightened `scripts/check-no-terminal-cap.sh` to forbid the bare counter token, with a new negative test case — the prior numbered-phrase list was the blind spot that let the residual ship; AGENTS.md rule wording adjusted to "try counters" accordingly. (G2) added the `## Andon log` substrate to `skills/implementaudit/templates/STATE.md` (`# | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome`), repointed all three PROTOCOL.md references that previously targeted a nonexistent `## Failure log` section, promoted ten official abnormality classes into `skills/implementaudit/references/transcript-contract.md` (failed-criterion, regression, hung-command, substituted-command, owner-unclear, generated-artifact-mismatch, stale-sidecar, policy-conflict, impossible-criterion, evidence-mismatch), required ANDON_ESCALATE to cite prior same-class Andon log rows by `#` before claiming recurrence, and required `New evidence:` and/or `Changed approach:` on every escalation — if neither can be truthfully filled, the run evaluates ANDON_HANDOFF conditions instead of escalating; no row limit, no try cap. `check-lean-discipline.sh` now enforces the Andon log substrate in both PROTOCOL.md and STATE.md. (G3) added tracked Andon-path transcript fixtures `fixtures/simple-audit/EXPECTED-ANDON-RECOVERY-SKELETON.md` (probe → proportional 5 Whys/Hansei → countermeasure → rerun evidence → resume → terminal closure) and `EXPECTED-ANDON-HANDOFF-SKELETON.md` (probe → escalate with same-class citation and new evidence → blocking condition → handoff, no completion marker), wired into `check-marker-order.sh` default arguments and `verify-package.sh`.

- **Hardening round P5–P6 (2026-06-10):** (P5) the `New evidence:` / `Changed approach:` escalation-progress requirement was prose/fixture convention only; `scripts/check-marker-order.sh` now rejects any `ANDON_ESCALATE` block in validated fixtures that contains neither field (lightweight marker-to-marker segmentation, not a transcript parser), with positive and negative cases in `tests/marker-order.test.sh`. No try cap recreated: the rule demands progress evidence, never counts attempts. (P6) added `fixtures/agent-eval/` — five adversarial identity-misread eval fixtures (terminal-cap-request, autonomous-build-runner, audit-only-reviewer, release-bot-overreach, lean-glossary-theater), each with Input, Expected behavior, Forbidden behavior, Owner/source, Evidence boundary, and Minimal passing transcript properties — made load-bearing by `scripts/check-agent-eval-fixtures.sh` (existence, required sections, non-empty bodies, mandatory not-live-proof disclaimer) and `tests/agent-eval-fixtures.test.sh` (4 cases), wired into `verify-package.sh` require_file set, the AGENTS.md validation list, and CI. Fixtures are eval inputs and expected transcript properties, not proof of live model behavior.

- **Hardening round N1–N3/C4/N5 (2026-06-10), from the round-2 self-dogfood audit:** (N1) package parity — `skills/implementaudit/references/lean-operating-discipline.md` shipped while absent from both build manifests, so its deletion would not have failed the gate; added it to `required_source`/`required_archive`, and the builder now requires exact set equality between archive entries and the manifest (extras fail, not just absences), with a stray-file negative case in `tests/release-asset.test.sh`. (N2) shipped-path integrity — payload files referenced repo-only paths that dangle for installed consumers (`transcript-contract.md` Machine check, `SKILL.md`/`phase-design.md` fixture pointers, hardcoded checker lists in `summarize-repo.sh`); repo-side references now carry a "source repo" label, `summarize-repo.sh` discovers mandatory-command candidates from the target repo via existence-guarded globs instead of hardcoding IMPLEMENTAUDIT paths, and a new path-integrity gate in `verify-package.sh` forbids unlabeled `fixtures/`, `tests/`, or `scripts/check-*` references in the payload. (N3) Andon class unification — the core `Andon:` block in `SKILL.md` now carries a `Class:` field with the ten official abnormality classes, and the transcript contract states the markers/classes apply to any governed run: with no run root, the findings ledger is the Andon log substrate; enforced by new `check-lean-discipline.sh` needles. (C4) dogfood version skew — Stage 0 now detects installed-payload vs repo-manifest version skew when operating on IMPLEMENTAUDIT itself, records an orientation Andon, and treats live repo files as the contract of record (PROTOCOL.md version-skew rule; AGENTS.md V0290-DOGFOOD-VERSION-SKEW). (N5) transcript grader — each agent-eval fixture gained a machine-readable `## Graded properties` block (require-marker / require-phrase / require-any / forbid-phrase / marker-order / no-terminal-cap directives); new `scripts/grade-agent-eval-transcript.sh` grades a transcript against a fixture deterministically, delegating structural checks to the existing marker-order and no-terminal-cap gates; `tests/agent-eval-grader.test.sh` proves one passing and one failing synthetic transcript per fixture. A grader PASS is a properties check, not a holistic run judgment.

- **Truth/coherence round R1–R5 (2026-06-10), from the round-3 self-dogfood audit:** (R1) README publicly claimed milestone v0.2.8.0 / manifest 0.2.8 against the live 0.2.9 manifest; corrected, and `verify-package.sh` now derives the README "Current project milestone:" claim check from plugin.json instead of leaving it the only unpinned version surface. (R2) the two validation registries had drifted in both directions — three newest tests absent from `verify-package.sh`'s internal suite, `lean-discipline.test.sh` absent from CI's explicit list; both wired, and new `scripts/check-validation-registry.sh` (+ focused test) enforces that every `tests/*.test.sh` is invoked by both registries, with a reasoned exemption for docs-portal.test.sh (must not nest inside verify-package). (R3) `IMPLEMENTAUDIT_PAUSE` and `IMPLEMENTAUDIT_CONTINUITY_SAVED` were emitted by the runtime but undeclared in the host-facing transcript contract; both documented (fields, position rules, non-completion semantics), added to AGENTS.md marker sections, and `check-marker-order.sh` now requires a preceding `IMPLEMENTAUDIT_PHASE_START` for any PAUSE. (R4) `AUDIT_GAPS` added to the final-audit ordering chain (a transcript printing it after `AUDIT_COMPLETE` now fails), with a negative test. (R5) AGENTS.md repo-layout tree updated to list the three simple-audit transcript skeletons it previously omitted.

- **Hygiene round S1–S3 (2026-06-10), from the round-4 self-dogfood audit:** (S1) `skills/implementaudit/templates/STATE.md` now enumerates the legal Status vocabulary (`open` / `READY_TO_DISPATCH` / `IN_PHASE` / `PAUSED` / `BLOCKED` / `INTERRUPTED` / `DONE`), checker-backed by a `check-lean-discipline.sh` needle — executors previously had to reverse-engineer statuses from scattered PROTOCOL.md mentions. (S2) the AGENTS.md required-readback grep list gained the three ANDON marker greps it lacked since the marker rename. (S3) new `tests/summarize-repo.test.sh` behaviorally tests the shipped recon helper in synthetic bare and checker-rich repos — and immediately caught two real defects in `skills/implementaudit/scripts/summarize-repo.sh`: compound `[ -e ] && printf` conditions made the helper exit non-zero in any repo lacking `.github/workflows` (and similar tails), and `git log` aborted it in commitless repos. All compound conditions converted to if-form; recent-churn now degrades to `no-commits-yet`. The helper's own header promises `side_effects=none`; it now also fails none.

- **User-journey round F1–F4 (2026-06-10), from the round-5 self-dogfood audit:** (F1) all 17 payload references to `skills/implementaudit/scripts/...` resolved nowhere for installed consumers (the archive strips the prefix); every packaged helper invocation now resolves through `"${IMPLEMENTAUDIT_BASE:-skills}"/scripts/...`, SKILL.md Stage 0 defines the resolution rule (hosts supply the base directory; the default keeps commands working verbatim in the source repo; unresolvable base → helper recorded unavailable, weaker-evidence fallback), and the verify-package path-integrity gate now forbids bare `skills/implementaudit/scripts/` in the payload. (F2) README §Loopability gained a "Nested loop model" subsection naming the five concentric loops (planner, run, phase, Andon, audit-fix) with each loop's exit condition and marker currency. (F3) the docs portal gained an "Abnormality Handling (Andon Escalation)" section teaching the probe/escalate/handoff contract, the ten abnormality classes, and the no-cap invariant — previously the portal never mentioned `ANDON_PROBE` or `ANDON_ESCALATE`. (F4) `docs/diagrams/invocation-modes.mmd` gained the fourth invocation shape (governed casual-build intake), repairing the README/portal disagreement about how many invocation shapes exist; README diagram block regenerated.

- **Target-repo evidence round R6-A + variable-collision repair (2026-06-10), from the round-6 self-dogfood audit:** (R6-A) in target repos that do not gitignore `.IMPLEMENTAUDIT/`, the run's own artifacts appeared as untracked changes in every `repo-state.sh` evidence scan, contaminating cleanliness and deliverable checks; `changed-files` and `added-lines` now exclude run-root paths with a visible stderr count (never silently, per the no-silent-caps doctrine), explicit `deliverable` queries remain honest for any path, and `claim-run.sh` prints a local-only `.git/info/exclude` notice (stderr; no repo mutation) when the run-root base is not ignored; behavioral test case added. (Collision repair) implementing R6-A exposed that the round-5 helper-path fix had redefined `IMPLEMENTAUDIT_BASE` — a variable `claim-run.sh` and `detect-env.sh` already consumed as the run-root base — as the skill directory, which would have created run roots inside the installed payload; the skill-directory variable is now `IMPLEMENTAUDIT_SKILL_DIR` (18 payload sites renamed), Stage 0 defines both variables explicitly and warns against confusing them, and `IMPLEMENTAUDIT_BASE` keeps its original run-base meaning.

- **Shipped-script class sweep (2026-06-10), round-7 escalation:** the round-7 live smoke found `detect-stack.sh` exiting 1 in clean target repos — the same compound-condition class repaired in `summarize-repo.sh` during round 4. Escalated with a changed approach instead of another single-file fix: all three remaining `[ test ] && printf` compounds in `detect-stack.sh` converted to if-form, and new `tests/shipped-scripts-smoke.test.sh` runs **every** shipped helper in a minimal target repo (recon helpers must exit 0; claim-run must keep stdout path-only and fire its ignore notice; repo-state enumeration must succeed; validators must still reject malformed specs), wired into both validation registries so the class cannot return in any shipped script.

- **Round 9 — M1–M5 + sidecar recovery and leverage maximization (2026-06-10):** (M1) `validate-phase.sh` diagnostics now name the expected shape (list-item requirements, the literal `Markdown fallback:` field) and the error summary points at `templates/phase-goal.txt` — the round-8 dogfood lost two iterations to messages that misnamed their own requirements. (M2) new shipped `skills/implementaudit/scripts/validate-run-root.sh` validates live run-root structure (Status enum token, Andon log columns, ROADMAP↔phase-spec completeness); the PROTOCOL resume contract now validates the run root before resuming (a corrupted root is an ANDON_PROBE, not something to resume through); package manifests updated. (M3) `AUDIT_START` carries `Skill version:` from the payload manifest so every transcript is attributable to its contract version. (M4) `fixtures/agent-eval/RUNBOOK.md` standardizes the first live eval run. (M5) Stage 0 detects bash availability for the helper layer. **Sidecars (owner-authorized this round):** graphify 0.8.37 + activegraph 1.1.0 installed; prior custody recovered read-only (v0.2.7.0/v0.2.8.0 stores: 18+9 JSONL, 8+19 SQLite events); v0.2.9.0 rounds 1–9 backfilled as 15 `historical_backfill` events per V0260 labeling plus 7 live events in `<run-root>/custody.db`, readback verified via `activegraph export-trace`/`inspect`; Graphify terrain re-extracted (144 nodes, 901 links) and queried live. **Leverage audit gaps closed:** Andon escalation custody events (`andon.probe.recorded`/`andon.escalated`/`andon.handoff.recorded` with abnormality class) added to SKILL.md §12a, the lean custody table, and the PROTOCOL Andon protocol; canonical store convention + cross-run read-only discovery + backfill labeling documented in PROTOCOL; Stage 0 detects prior per-run stores; terrain extraction ownership and node schema documented; lean checker enforces the new rows. `check-sidecar-boundaries.sh` corrected to its own documented boundary (tracked source / package / ignore-cover — not local existence, which canonical dogfood sidecars now require).

- **Round 11 — sidecar tooling completion N1–N4 (2026-06-10), from the round-10 double-dogfood:** (N1) `skills/implementaudit/templates/sidecars.md` now ships — the one mandated run-root artifact with a contract-specified shape (status table, Graphify query log per the lean reference, custody store fields, backfill labeling, evidence boundaries) that every run previously hand-invented; `validate-run-root.sh` now requires it for dispatched runs; lean checker enforces the template's contract content. (N2) `skills/implementaudit/scripts/custody-append.sh` ships — one-command, absent-safe custody emission (activegraph missing → exit 0 with a Markdown-fallback note; never blocks), closing the gap between the PROTOCOL's "mirror Andon events into the store" mandate and the hand-rolled API plumbing it previously required; PROTOCOL names the helper; focused test covers usage errors, invalid JSON, both present/absent paths, and duplicate-id safety. (N3) `detect-env.sh` reports `implementaudit_skill_dir` resolution and an explicit `helper_layer=available/unavailable` line. (N4) README §Optional tooling and the portal's Continuity/Sidecars section now surface the round-9 conventions (per-run store, Andon custody events, read-only prior-store preload, backfill labeling, packaged template). Package manifests grew deliberately to 27 entries under the set-equality gate.

- **Round 13 — README/docs truth + onboarding completion (2026-06-10), from the round-12 audit:** (R1) README ToC completed (19 → 27 entries) and `check-readme-toc.sh` now enforces two-way parity (every H2 must be listed). (R2→corrected) the planned release-staleness disclosure exposed a deeper truth defect when written: README pinned `v0.2.5.0` as the live public release while the portal claimed `v0.2.8.0` — **live GitHub verification (release list + tags) confirmed v0.2.8.0 is the latest public release**; seven stale README pins corrected, the disclosure now states the verified fact (v0.2.8.0 still predates the v0.2.9.0 contract — the onboarding hazard stands, one milestone narrower), and `tests/docs-portal.test.sh` gained a README↔portal parity check on install scripts and the live-release version so the two hand-maintained surfaces cannot drift silently again. (R3) Quick start section at the top of README. (R4) the two-tier sidecar policy (optional everywhere; canonical for maintaining IMPLEMENTAUDIT itself) stated in README and portal. (D1) portal "Shipped Scripts Reference": all nine helpers × loop × purpose, with the shared honest-degradation contract. (D2) portal gate-model mapping note (10 teaching gates = 8-row SKILL.md spine + two split-outs; spine canonical). (D3) portal gained the Claude release-install path it omitted. (D4) audits INDEX now summarizes the thirteen-round v0.2.9.0 arc. (K1) `custody-append.sh` enforces V0260 labeling at write time — `custody_mode` required; `historical_backfill` requires source/backfilled_at/original_event_time/evidence_boundary — before the activegraph import, so the contract holds even where events can't be recorded. (K2) `templates/tools.md` + `templates/context.md` ship, completing the Stage-5 substrate (manifests at 29 entries). (K3) tracked exemplar run root at `fixtures/run-root-example/` passing both validators, wired into the run-root test.

- **Round 15 — refinement set + phrase-level truth sweep (2026-06-10):** implemented the round-14 proposals — (K-a) `custody-append.sh` takes an optional caused-by event id so escalations chain to their probes and replay reconstructs causality; (K-c) tracked DMADV greenfield phase exemplar (`fixtures/phase-design/dmadv-greenfield-phase.md`, validator-passing) pairing the brownfield run-root exemplar; (K-d) `validate-phase.sh --explain` prints the full required-structure checklist with pointers to both exemplars; (R-a) install-source delta table (public v0.2.8.0 vs source v0.2.9.0 contract features); (R-b) §What-it-is sidecar paragraphs deduplicated into the single two-tier statement; (R-c) Quick-start cross-links; (D-a) CONTRIBUTING gained the current-contract essentials (four shapes, Andon escalation, two-tier sidecars, portal/RUNBOOK pointers); (D-b) portal release-state claims now carry their evidence basis (release-list/tag-API/CI-run/HTTP-200 verifications, dated); (D-c) tooling-architecture diagram annotated with the concrete conventions. **Deeper sweep findings (phrase-level staleness the token gate missed), all fixed:** PROTOCOL.md and phase-goal.txt still said "failure recovery ladder"; AGENTS.md's Working-state line and templates/scripts/fixtures trees were stale (missing the six new payload files and current fixture families); `check-no-terminal-cap.sh` now forbids the "recovery ladder"/"failure ladder" phrase class. **AGENTS.md's 130-line validation block was executed verbatim end-to-end for the first time: PASS.**

- **Round 16 — output-truth audit + substrate completion (2026-06-10):** deeper Gemba targets nothing had read before: the AGENTS readback block executed verbatim (PASS, 26 lines), the **generated portal output read for content truth** — which exposed two real defects in the portal's State and Artifact Model: `IMPLEMENTAUDIT_CONTINUITY_SAVED` was documented with six **invented** fields (run_id/content_hash/timestamp…) instead of the contract's Target/Reason/Evidence/Boundary/Authorization/Not-saved, and `STATE.md` was described as custody storage (custody lives in `custody.db`); both corrected, and the artifact table gained the missing `tools.md`/`context.md` rows. README §Artifacts and outputs updated from a vague "such as roadmaps, state files" to the full ten-artifact substrate with the validator and the continuity marker's six fields (README previously never mentioned `IMPLEMENTAUDIT_CONTINUITY_SAVED` at all). `validate-run-root.sh` now requires the complete planning substrate (tools.md, context.md added; exemplar + test fixtures updated). `tests/shipped-scripts-smoke.test.sh` extended to the round-9+ helpers it predated (validate-run-root non-root rejection, custody-append arity/exit-0 contracts, detect-env skill-dir report). THINKING.md custody plan synced to the current conventions (Andon events with caused-by chaining, per-run store path, packaged helper). README usage examples gained the casual-build and goal-synthesis shapes.

### Changed

- Plugin manifest version `0.2.8` → `0.2.9` (shipped package behavior change: failure-recovery contract in references/templates payload).

### Known issue

- Installed host payloads remain on the pre-repair contract until this milestone is committed, pushed, and the plugin updated (cache refreshes only on a version-field change). Documented as handoff G4 in `docs/audits/archive/v0.2.9.0-andon-escalation-jidoka-repair.md`; no install/update action performed or claimed.

## [v0.2.8.0] - 2026-06-08

### Added

- `docs/portal/onboarding.md`: portal content source with 10 onboarding sections (What is IMPLEMENTAUDIT; When to use; When not to use; Normal prompt vs /goal vs IMPLEMENTAUDIT chooser table; Three invocation modes; Compared with a generic staged-goal runner; What Graphify and ActiveGraph do; What completion means; Install and update; Easy invocation examples). Neutral reference-language only. No all-domain obsolescence claim.
- `scripts/build-docs-portal.py`: stdlib-only docs portal generator. Reads onboarding.md, README.md, CHANGELOG.md, INDEX.md, plugin.json. Generates `dist/docs-portal/index.html` + `docs-metadata.json`. Dark theme, skip link, sidebar nav, IntersectionObserver active-section tracking, 9 required section anchors, `rough_draft_used: false`. Usage: `python scripts/build-docs-portal.py [--out <dir>]`.
- `scripts/check-docs-portal.py`: 12-check validator for generated portal output. Checks index.html non-empty; metadata fields; source sha256s; manifest version; milestone; rough_draft_used=false; no file:///; no Windows paths; nav anchors unique+ordered; 9 required section anchors; no unsupported claims; skip link; semantic headings. Usage: `python scripts/check-docs-portal.py <output-dir>`.
- `tests/docs-portal.test.sh`: 26-check test suite (generator exits 0; check-docs-portal passes; metadata fields; no file:///; no Windows paths; nav anchors; 9 required section anchors; verify-package still passes; negative test).
- `fixtures/casual-build/accepted-intent.md`: documents governed casual-build intake — natural-language intent accepted and normalized into tdqyq-audit-object; Classification: governed casual-build intake; Stage 1 synthesized audit object.
- `fixtures/casual-build/rejected-intent.md`: 4 rejection cases (empty input STOP; unsafe input STOP; non-repo input STOP; unbounded impossible input → request clarification).
- `fixtures/phase-design/polish-harden.md`: two variants (Polish & Harden included with default-recommended rationale; Polish & Harden skipped with documented rationale).
- `.github/workflows/pages.yml`: GitHub Pages deployment pipeline (build+validate+deploy) with OIDC permissions, concurrency guard, and OWNER DECISION note — Pages source must be set to "GitHub Actions" in repo settings before the deploy job can succeed.
- `scripts/check-workflow-structure.py`: stdlib-only structural checker for GitHub Actions YAML (no external deps). Checks: name/on/jobs keys, steps: key, actions/checkout reference, no tab indentation. Explicitly notes full schema validation is pending CI. Replaces `bash -n` as workflow evidence. Usage: `python scripts/check-workflow-structure.py <workflow-file> [...]`.
- Added `docs/audits/archive/v0.2.8.0-adaptation.md`: G1-G7 gap closure ledger, phase-by-phase evidence, Graphify authorization boundary, reference-language check, formal public-claim boundary hygiene check result, Smoke B results (including structural workflow check), audit-fix round record (5 items), remaining risk, terminal closure table. G5 classified as STRENGTHENED (not ALREADY COVERED).
- Updated `docs/audits/INDEX.md`: v0.2.8.0 entry (G5 STRENGTHENED; audit-fix round summary).

### Changed

- `skills/implementaudit/SKILL.md` §2: added 4th invocation shape bullet — `governed casual-build intake`; added governed casual-build intake bullet to canonical audit terminology; added governed casual-build intake paragraph to §2a invocation boundary; added Bounded continuity preload block to Stage 0 (5-source priority order: AGENTS.md first; run-root applied-context; optional personal/project notes; Graphify terrain; ActiveGraph custody) + IMPLEMENTAUDIT_CONTINUITY_SAVED marker template with all 6 required fields.
- `skills/implementaudit/templates/PROTOCOL.md` Steps 14/15: CONTINUITY_DECISION options expanded to 5 options (none; repo-local AGENTS.md rule; run-local applied-context note; optional personal/project note; optional ActiveGraph event); override-prevention statement; IMPLEMENTAUDIT_CONTINUITY_SAVED reference.
- `skills/implementaudit/templates/THINKING.md`: invocation shape line updated: adds `governed casual-build intake`.
- `skills/implementaudit/templates/phase-goal.txt`: Polish & Harden variant comment block added at end (Type: polish-harden; work bullets; acceptance criteria).
- `skills/implementaudit/references/routing.md`: Governed casual-build intake definition in Definitions; Governed Casual-Build Intake section (5-step process); updated Positive Identity section.
- `skills/implementaudit/references/goal-format.md`: chooser table (4 rows: normal prompt / /goal / /implementaudit / governed casual-build intake); easy invocation examples; IMPLEMENTAUDIT_CONTINUITY_SAVED format block; Optional Polish & Harden phase type note.
- `skills/implementaudit/references/planning-depth.md`: Governed casual-build intake subsection under Invocation shapes; casual-build planning bar definition.
- `skills/implementaudit/references/phase-design.md`: Rule P4-8 — Polish & Harden phase (optional terminal phase shape; default-recommended for full plans/public surfaces/package boundaries; skippable with rationale; no new features; covers cleanliness, identity hygiene, generated artifact freshness, proof-boundary wording).
- `scripts/check-planner-stages.sh`: 2 new require_in_file checks for governed casual-build intake.
- `scripts/check-routing.sh`: "governed casual-build intake" added to routing definitions check.
- `tests/continuity.test.sh`: extended to 34/34 (was 25/25; +7 IMPLEMENTAUDIT_CONTINUITY_SAVED/override-prevention checks; +2 scenario 3 checks).
- `fixtures/continuity/safe-note-write.md`: CONTINUITY_DECISION updated to run-local applied-context note; full IMPLEMENTAUDIT_CONTINUITY_SAVED marker block added.
- `scripts/build-docs-portal.py`, `scripts/check-docs-portal.py`: all user-facing CLI output uses `sys.stdout.write`/`sys.stderr.write` instead of the built-in print function, keeping the debug-print cleanliness gate applicable to `.py` files without a global exemption.
- `.gitignore`: `_site/` entry added.
- `.github/workflows/validate.yml`: `bash tests/docs-portal.test.sh` added to focused behavior tests.
- Plugin manifest: `0.2.7` → `0.2.8`.

### Post-Release Repair (2026-06-08): Docs Portal Coherence and Prose Quality

- `scripts/build-docs-portal.py`: fixed `render_callout` — callout titles now use `inline_md()` (not bare `esc()`) so backtick code spans render as `<code>` elements; trailing period stripped before appending the canonical period, eliminating double-period rendering (`..`) on all callout titles. Swapped Default Behavior and Usage Examples in SIDEBAR_GROUPS Method group (examples now precede abstract behavior spec for operator readers).
- `docs/portal/onboarding.md`: 8 coherence fixes — (1) "does not mean" list reformatted from redundant "Not ..." prefix to `Term — explanation` pattern; (2) Comparison subheading "absorbs" changed to "Behaviors shared with staged-goal runners"; (3) Usage Examples swapped to precede Default Behavior; (4) Terminology table: added continuity preload (5-source priority order) and continuity writeback (`CONTINUITY_DECISION` five options, `IMPLEMENTAUDIT_CONTINUITY_SAVED`); (5) ydqyq-audit-action example clarified: "patching owner/source is a ydqyq-audit-action; a passing CI check is evidence but does not itself mutate the audit object"; (6) Evidence and Audit Trail: added coherence-polish ledger reference and corrected diagrams line to name all three Mermaid files; (7) Audit Status: "Methodology scope" replaced with "Methodology scope" wording; (8) source cleanup only (no callout double-period in source; generator fix handles all cases).
- `docs/audits/archive/v0.2.8.0-docs-portal-coherence-polish.md` (new): 8-finding coherence and prose quality ledger. Records what was found, changed, and intentionally left alone. Remaining visual risks: install-section ambiguity (deferred), table density on narrow viewports (deferred), screenshot proof (unverified — no browser tooling).
- `docs/audits/INDEX.md`: updated with coherence-polish audit paragraph.

### Post-Release Repair (2026-06-08): Docs Portal Academic/Content-Model

- `docs/portal/onboarding.md` (rewritten, 24 sections): complete academic/content-model repair. Overview now leads with formal thesis statement and bottleneck framing ("AI agents can produce repo changes faster than humans can review evidence..."). Six new Concepts sections: Mental Model (execution chain diagram with intra/inter distinction), Invocation Model (5-column formal table × 4 shapes), Audit Gate Model (10-gate × 4-attribute table with halt conditions), What AUDIT_COMPLETE Means (7 pass items + 6 does-not-mean items), State and Artifact Model (14-artifact × 4-column table including tdqyq-audit-object and ydqyq-audit-action), Continuity and Sidecars (5-source priority order, sidecar model table, intra/inter distinction table). Comparison section: neutral 4-row × 5-column table with "absorbs" and "refuses" subsections. Routing section updated with DMADV/DMAIC methodology, counterexamples. Evidence section updated with G5 STRENGTHENED detail. Total: 24 sections (was 19; added 6 Concepts + Comparison; removed Execution Spine; renamed Invocation Modes → Invocation Model).
- `scripts/build-docs-portal.py`: SIDEBAR_GROUPS updated to Start/Concepts/Method/Reference (was Start/Method/Reference/Evidence). Concepts group (6): Mental Model, Invocation Model, Audit Gate Model, AUDIT_COMPLETE, State and Artifacts, Continuity and Sidecars. Method group (5): Operating Method, Routing, Comparison, Default Behavior, Examples. Reference group (7): Terminology, Repo Layout, Optional Tooling, Safety and Boundaries, What It Doesn't Do, Evidence and Audit Trail, Audit Status. Hero subtitle updated to academic tone. sys.stdout.write/sys.stderr.write throughout.
- `scripts/check-docs-portal.py` (30 checks): REQUIRED_CONTENT_ANCHORS updated to 24 academic-model anchors. REQUIRED_SIDEBAR_GROUPS updated to ["Start", "Concepts", "Method", "Reference"]. New academic content checks: bottleneck framing ("review discipline" or "faster than"), tdqyq-audit-object and ydqyq-audit-action identifiers, AUDIT_COMPLETE and IMPLEMENTAUDIT_RUN_COMPLETE markers, DMADV and DMAIC methodology terms, G5 STRENGTHENED status, no stale "--version 0.2.4" install command, all required section id anchors. Stale check "three invocation modes" updated to "four invocation shapes" language.
- `tests/docs-portal.test.sh` (72 checks): updated required anchors list to 24 academic-model anchors. Test 14 updated: sidebar groups now Start/Concepts/Method/Reference. Tests 27-32 added: bottleneck framing, tdqyq/ydqyq identifiers, AUDIT_COMPLETE/RUN_COMPLETE markers, DMADV/DMAIC terms, G5 STRENGTHENED, no stale v0.2.4 install.

### Post-Release Repair (2026-06-08): Docs Portal UX

- `docs/portal/onboarding.md` (rewritten): comprehensive 19-section content source replacing the original 10-section thin version. Sections: Overview, Quick Start, Install, For New Users, For Agents and Operators, For Auditors and Maintainers, Terminology, Invocation Modes (**four** modes: direct governance, embedded governance, goal synthesis, governed casual-build intake), Execution Spine, Operating Method, Usage Examples, Default Behavior, Routing (including Governed casual-build row), Repo Layout, Optional Tooling, Safety and Boundaries, What It Does Not Do, Evidence and Audit Trail, Audit Status. v0.2.8.0 truth throughout: release live, manifest 0.2.8, G5 STRENGTHENED, no marketplace publication, CHECKSUMS.txt is checksum manifest only. Custom conventions: `:::type` callout blocks, `### card: Title` audience card sections.
- `scripts/build-docs-portal.py` (rewritten): rich portal generator. Dark-navy themed with: fixed collapsible sidebar (Start/Method/Reference/Evidence groups using `<details>`), gradient h1 hero zone, process flow (Input → Gemba → Smoke A → Patch → Smoke B → Final Audit), mobile TOC, audience card grids from `### card:` sections, callout divs from `:::type` blocks, scrollspy JS (requestAnimationFrame), skip link. stdlib only; uses sys.stdout.write/sys.stderr.write throughout.
- `scripts/check-docs-portal.py` (rewritten, 20 checks): updated required section anchors to 19 v0.2.8.0 anchors. Added checks for: h1 page title, hero zone, process flow steps, grouped sidebar labels (Start/Method/Reference/Evidence), mobile TOC, audience cards, four invocation mode phrases, governed casual-build intake text, no stale "three invocation modes", no stale "release pending", no empty inline code, no affirmative marketplace/provenance overclaims. Nav-anchor regex updated for `class="nav-section"` structure.
- `tests/docs-portal.test.sh` (rewritten, 58 checks): SC-2 fixed — Test 7 now uses correct nav-section regex (no longer shows "1 found"). Tests 11-26 added: h1, hero zone, all six process flow steps, sidebar groups, mobile TOC, audience cards, four invocation modes, governed casual-build intake, no stale three-modes claim, no stale release-pending text, no empty inline code, no forbidden claims, skip link, rough_draft_used boolean checks, nav order.
- `.github/workflows/pages.yml`: `workflow_dispatch:` trigger added — SC-1 fix from v0.2.8.0 docs-portal-ci-onboarding audit. Enables manual portal rebuild from GitHub Actions UI.

## [v0.2.7.0] - 2026-06-07

### Added

- `skills/implementaudit/references/lean-operating-discipline.md` (ships in package): Lean/TPS concept-to-behavior mapping table for 20 concepts (5S, Kaizen, Hansei, Jidoka, Gemba, Nemawashi, Muda/Mura/Muri, DMAIC, DMADV, Poka-yoke, etc.). Each concept maps to auditable IMPLEMENTAUDIT runtime behavior with owner/source and evidence check. Evidence boundaries section: no sigma-level, DPMO, or certification claims. Lean terms are not decorative labels.
- `skills/implementaudit/templates/PROTOCOL.md`: added 5S_CHECK gate to Step 9 (Seiri/Seiton/Seiso/Seiketsu/Shitsuke, all five pillars recorded as clean/deferred/blocked); added Jidoka stop-the-line chain (8-step: Andon → FAILURE_PROBE → Hansei → 5 Whys → countermeasure → Kaizen standardization → re-run evidence → close/block/defer/handoff); added Nemawashi owner-decision gate (surface consequential assumptions before Stage 7 or phase dispatch).
- `skills/implementaudit/templates/THINKING.md`: added Lean quality route section (DMAIC/DMADV structured fields); added Muda/Mura/Muri register (Items + Disposition per waste type).
- `skills/implementaudit/templates/phase-goal.txt`: added `Quality route:` field (DMAIC / DMADV / PDCA / 5S / mixed / not applicable).
- `skills/implementaudit/references/routing.md`: added DMAIC brownfield routing (Define→Measure→Analyze→Improve→Control with evidence boundaries); DMADV greenfield routing (Define→Measure→Analyze→Design→Verify with evidence boundaries); mixed DMAIC+DMADV pattern; DMAIC/DMADV routing decision table.
- `scripts/check-lean-discipline.sh`: poka-yoke checker (10 structural requirements): lean-operating-discipline.md exists and is load-bearing, 5S in PROTOCOL.md, Jidoka chain in PROTOCOL.md, Nemawashi in PROTOCOL.md, Muda/Mura/Muri in THINKING.md, DMAIC/DMADV in THINKING.md and routing.md, Quality route in phase-goal.txt, no certification overclaims, required fixtures exist, no general Lean essays in skills/.
- `tests/lean-discipline.test.sh`: 9 test cases (1 positive + 8 negative) verifying the poka-yoke checker catches each missing structural requirement.
- `fixtures/lean/brownfield-dmaic-release-repair.md`: DMAIC fixture (ZIP_STORED compression bug: Define→Measure→Analyze→Improve→Control).
- `fixtures/lean/brownfield-dmaic-stale-docs.md`: DMAIC fixture (stale README Mermaid diagrams).
- `fixtures/lean/greenfield-dmadv-new-runtime-helper.md`: DMADV fixture (check-lean-discipline.sh as new governed artifact).
- `fixtures/lean/mixed-dmaic-dmadv-package-boundary.md`: mixed DMAIC+DMADV fixture (package boundary repair + new audit doc).
- `docs/audits/archive/v0.2.7.0-lean-operating-discipline.md`: audit ledger classifying 20 Lean concepts: 5 already-covered, 2 strengthened, 11 adapted, 0 intentionally-rejected, 0 deferred.
- `skills/implementaudit/references/lean-operating-discipline.md` extended with `## Graphify terrain leverage` section (Seiri/Seiton/Seiso/Muda/DMAIC/DMADV → Graphify query use + live-file confirmation required) and `## ActiveGraph custody events` section (full event table for IMPLEMENTAUDIT-defined custom events, custody boundary rules, and Capability Ledger narrow-entry requirements).
- `skills/implementaudit/templates/THINKING.md`: extended `## Optional sidecars` with Lean-specific Graphify terrain plan fields (Seiri/Seiton/Seiso/Muda/DMAIC/DMADV queries) and ActiveGraph custody plan fields (events list, custody store location, Capability Ledger format).
- `skills/implementaudit/templates/PROTOCOL.md`: added `## Sidecars and continuity` Graphify Lean leverage rules and ActiveGraph Lean custody rules (Graphify cannot close criteria without live-file confirmation; ActiveGraph custody cannot close correctness criteria without Smoke B; sidecar absence non-blocking).
- `skills/implementaudit/templates/phase-goal.txt`: expanded Graphify/ActiveGraph fields to include terrain used/skipped/absent/stale/unauthorized, live-file confirmation required, custody used/skipped/absent, evidence boundary, and sidecar outputs exclusion assertions.
- `scripts/check-lean-discipline.sh`: extended with 2 new structural requirements (11. Graphify terrain leverage section, 12. ActiveGraph custody events section) — sidecar leverage cannot remain prose-only.
- `tests/lean-discipline.test.sh`: extended to 11/11 with 2 new negative cases (Graphify terrain section missing, ActiveGraph custody events section missing).
- `fixtures/lean/sidecar-graphify-absent-markdown-fallback.md`: sidecar-absent scenario — Markdown/Gemba fallback remains valid; AUDIT_COMPLETE not blocked.
- `fixtures/lean/sidecar-graphify-dmaic-analyze.md`: sidecar-present scenario — Graphify used in DMAIC Analyze, 3 owner/source candidates confirmed against live files.
- `fixtures/lean/sidecar-activegraph-dmaic-custody.md`: sidecar-present scenario — ActiveGraph custody events emitted and read back; narrow Capability Ledger entry derived.
- AGENTS.md: 3 additional durable anti-repeat sidecar rules (V0270-SIDECAR-LEVERAGE-NOT-PROSE, V0270-SIDECAR-OUTPUTS-EXCLUDED); 3 sidecar fixtures added to validation checklist.
- README.md: added Lean operating discipline bullet to Operating method section; version updated to v0.2.7.0 / 0.2.7.

### Changed

- `skills/implementaudit/SKILL.md`: updated `description` frontmatter and opening body to make deep planning and phase-by-phase execution until terminal audit closure or audited handoff explicit in the canonical skill identity. Added the sentence: "IMPLEMENTAUDIT plans deeply and executes repo work phase-by-phase until terminal audit closure or an explicit audited handoff. It makes repo changes that are auditable, bounded, owner/source-grounded, reversible, and not overclaimed."
- `README.md`: updated opening paragraph and "What it is" section to match SKILL.md identity; added "Blocked work ends in an explicit audited handoff, not fake completion" boundary statement; preserved "not a generic autonomous build runner" distinction.
- `AGENTS.md`: extended routing rule to include deep-planning and phase-execution identity; guards against regression to "audit-only" or "generic autonomous builder" framing.
- `skills/implementaudit/references/planning-depth.md`: added one-line terminal closure alignment to Depth rule section.
- `skills/implementaudit/references/phase-design.md`: added one-line phase execution continuity statement to opening paragraph.
- Plugin manifest: `0.2.6` → `0.2.7`.

## [v0.2.6.0] - 2026-06-07

### Added

- Added `skills/implementaudit/scripts/validate-phase.sh` 19-failure-mode checks: IMPLEMENTAUDIT_PHASE_START/VERIFY/DONE, AGENTS_UPDATE_DECISION, CONTINUITY_DECISION, Run root, Baseline ref, Owner/source, Task, Type, Depends on phases, Work section, Acceptance criteria (non-placeholder), Mandatory commands section (non-placeholder), Evidence required section (non-placeholder), Rollback/defer path, Markdown fallback status. `tests/phase-validation.test.sh` updated to 20/20 (1 positive + 19 failure modes). `fixtures/phase-validation/valid-full-spec.md` added as positive test fixture.
- Added `scripts/public-claim boundary check`: generic forbidden-string checker accepting caller-supplied terms at runtime (never embedded in source). Wired into AGENTS.md identity hygiene release-gate instructions.
- Added `skills/implementaudit/references/phase-design.md` §"Phase shape requirements" with 7 rules: P4-1 hardening-phase requirement, P4-2 visual polish evidence, P4-3 brownfield safety-net, P4-4 package/release split, P4-5 provenance boundary fresh Smoke Before Claim, P4-6 hardening scope restriction, P4-7 skip documentation.
- Added 5 phase-shape fixture outlines at `fixtures/phase-design/`: simple-greenfield, brownfield-mutation, ui-feature, package-release, full-hardening-run.
- Added concrete 16-step per-phase execution loop to `skills/implementaudit/templates/PROTOCOL.md`.
- Added exact 3-strike failure recovery (FAILURE_PROBE / FAILURE_ESCALATE / FAILURE_HANDOFF) with step-by-step protocol to `PROTOCOL.md`; updated `skills/implementaudit/references/transcript-contract.md`.
- Added final audit exactness to `PROTOCOL.md`: AUDIT_START (round/criteria/command), phase completeness check, mandatory command re-run, coverage math `re_verified/(re_verified+trust_prior)`, trust-prior > 30% warning, 3-round audit-fix loop, AUDIT_HANDOFF path, ordering rules.
- Added mid-run interruption handling to `PROTOCOL.md`: IMPLEMENTAUDIT_PAUSE marker, 4-option menu (Resume/Revise spec/Skip phase/Stop), resume contract (5 steps), STATE.md INTERRUPTED state.
- Added 8 dispatch-prep steps to `SKILL.md` Stage 5: STATE.md READY_TO_DISPATCH, baseline ref from git, PROTOCOL.md copy, repo-state.sh evidence, phase-spec existence check, validate-phase.sh on all specs, command dedup, handoff gated on Stage 6.5 PREFLIGHT_GREEN.
- Added 7 Phase 4 shape rules to `SKILL.md` Stage 4 bullet list (P4-1..P4-7) + fixture reference.
- Added Stage 7 gating clause: handoff only after Stage 5 dispatch-prep and Stage 6.5 PREFLIGHT_GREEN.
- Added behavioral continuity tests to `tests/continuity.test.sh` (25/25): 6 scenarios covering memory-absent run, no-write-warranted, safe-note frontmatter, unsafe-content rejection, final-project ordering, no-boundary-crossing. 6 fixtures at `fixtures/continuity/`.
- Added behavioral sidecar tests to `tests/sidecars.test.sh` (24/24): 7 scenarios covering Graphify absent/fresh/stale, ActiveGraph absent/unauthorized/authorized, sidecar-overclaim-rejected. 7 fixtures at `fixtures/sidecars/`.
- Deepened `skills/implementaudit/scripts/detect-stack.sh`: package-scripts (npm script enumeration), python-hints (pyproject.toml/requirements.txt), language/framework hints (extension counts, framework config files), source/test directory layout, config/infra inventory.
- Deepened `skills/implementaudit/scripts/summarize-repo.sh`: test-surface-summary, file-extension-counts, recently-churned-files, largest-tracked-files, likely-generated-outputs, mandatory-command-candidates from detected scripts.
- Added AGENTS.md §"Identity hygiene release-gate" with anti-repeat rule (v0.2.6.0), public-claim boundary check usage, and release-gate protocol.
- Added `docs/audits/archive/v0.2.6.0-operational-parity-hardening.md`: 12 gap classes (G1-G12), all ADAPTED or INTENTIONALLY REJECTED with documented alternative, identity hygiene check section.
- Updated `docs/audits/INDEX.md` with v0.2.6.0 entry.
- Updated CI (`validate.yml`): removed "Validate phase template" step (template has placeholder content by design; install-copy-smoke.test.sh covers validator execution).

### Changed

- `skills/implementaudit/templates/phase-goal.txt` expanded from thin mnemonic skeleton to full executable spec with all required structural sections (Phase N/TOTAL, Task, Type, Run root, Baseline ref, Owner/source, Audit object, Auditing operation, Terminal object state, Thinking ref, Mandatory commands, Acceptance criteria, Evidence required, Depends on phases, Why, Work, Acceptance criteria block, Mandatory commands block, Evidence required block, Rollback, Graphify/ActiveGraph/Markdown fallback, Cleanliness override, Notes, IMPLEMENTAUDIT_PHASE_VERIFY full block, AGENTS_UPDATE_DECISION, CONTINUITY_DECISION, IMPLEMENTAUDIT_PHASE_DONE).
- `tests/install-copy-smoke.test.sh`: replaced `validate-phase.sh` call against template with inline filled smoke spec (template has placeholder content by design).
- Plugin manifest metadata: `0.2.5` → `0.2.6` (pending release authorization after dogfood gate).

### Safety

- Reference evidence used as read-only reference only; the external staged-goal reference's proper name, slash command, marker names, artifact paths, and memory markers were not imported into any tracked repo file, commit message, branch name, tag name, PR title, or release note.
- All 12 gap classes resolved without importing external identity.
- `public-claim boundary check` uses caller-supplied terms at runtime; the public-claim boundary term is never embedded in source.

## [v0.2.5.0] - 2026-06-07

### Added

- Added a neutral v0.2.5.0 reference gap-closure audit ledger at
  `docs/audits/archive/v0.2.5.0-external-staged-goal-runtime-gap-closure.md`.
- Added native namespaced run-root claiming with `skills/implementaudit/scripts/claim-run.sh`
  and `tests/claim-run.test.sh`.
- Added focused tests for bounded continuity, sidecar boundaries, Capability
  Ledger evidence boundaries, and placeholder-only phase validation:
  `tests/continuity.test.sh`, `tests/sidecars.test.sh`,
  `tests/capability-ledger.test.sh`, and `tests/phase-validation.test.sh`.
- Added `scripts/check-sidecar-boundaries.sh` to keep Graphify and ActiveGraph
  optional, noncanonical, absent-safe, and excluded from package debris.
- Added routing fixtures for full greenfield category intake, batched
  greenfield questions, and brownfield 0-2 true-gap question behavior.

### Changed

- Strengthened native Stage 0 context detection, memory/continuity discovery,
  optional sidecar detection, baseline/ref capture, and available tool/session
  reporting.
- Strengthened Stage 1 routing so greenfield work walks material intake
  categories in batches of up to four, while brownfield work runs recon first
  and asks only 0-2 true-gap questions.
- Strengthened Stage 2/3 recon and thinking artifacts with repo maps,
  mandatory-command candidates, top three risks, weakest dependency, optional
  lookup status, sidecar boundaries, and Markdown fallback.
- Moved the preferred planned-run artifact layout to
  `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/` with `ROADMAP.md`, `STATE.md`,
  `THINKING.md`, `PROTOCOL.md`, `context.md`, `tools.md`, `sidecars.md`,
  applied-context/memory files, repo-map files, phase specs, fix specs, and
  audit-fix specs.
- Clarified that flat `.IMPLEMENTAUDIT/*` files remain legacy resume/audit
  compatibility, not the preferred target for new planned runs.
- Strengthened Stage 6 self-critique with an explicit review menu and blocked
  Stage 7 handoff until Start now is explicitly selected.
- Strengthened Stage 6.5 red preflight discipline so failed, timed-out, hung, or
  substituted commands require Andon evidence and unrelated/unclear red
  baselines cannot silently dispatch.
- Strengthened phase templates and validation so placeholder-only acceptance
  criteria cannot validate as real phase specs.
- Bumped plugin manifest metadata from `0.2.4` to `0.2.5` for shipped runtime
  behavior in the `v0.2.5.0` project milestone.

### Safety

- Preserved IMPLEMENTAUDIT identity and native marker vocabulary; external
  reference package identity, artifact paths, marker names, and memory markers
  are not imported into tracked repo files.
- Preserved Graphify as optional terrain/orientation evidence only and
  ActiveGraph as optional custody/event evidence only.
- Preserved Markdown audit objects, transcript markers, fixtures, checkers,
  package manifests, and final audit closure as canonical.
- Preserved package minimality: repo audit ledgers, release notes, fixtures,
  tests, CI config, `.IMPLEMENTAUDIT/` run roots, Graphify outputs, ActiveGraph
  stores/exports, and local smoke debris remain out of the `.skill` payload.
- Did not claim marketplace verification, universal host support, signature,
  attestation, SBOM, license, or passive update automation.

### Repair (post-release, 2026-06-07)

**Primary root cause:** The original `.skill` archive had skill content nested under
`skills/implementaudit/SKILL.md` (wrong root shape). Claude Desktop's import contract requires
`SKILL.md` at archive root. The archive was accepted by the Codex installer
(which reads from `skills/` explicitly) but rejected by Claude Desktop import with
"malformed at root." No live Claude import was ever tested before release.

**Structural fix (archive root shape):**
- `scripts/build-release-asset.sh` rebuilt to strip the `skills/` prefix so
  archive entries are `SKILL.md`, `references/`, `scripts/`, `templates/`
  at root — not nested under `skills/`.
- `.claude-plugin/plugin.json` `skills` field changed from `"./skills/"` to `"./"`.
- `scripts/install-codex-from-release.sh` updated for new root shape.
- `scripts/install-claude-from-release.sh` updated for new root shape; usage
  relabeled as "file-copy workaround only — NOT Claude import proof."
- `tests/release-asset.test.sh` updated; added regression guard: `skills/implementaudit/SKILL.md`
  in archive is now a hard failure.
- `tests/release-asset-install.test.sh`,
  `tests/release-asset-install-claude.test.sh`: sidecar test paths updated.
- `scripts/verify-package.sh`: plugin `skills` path check updated.

**Secondary root cause:** No live Claude Desktop import was run in the release gate.
- Added `scripts/install-claude-from-release.sh` (file-copy workaround, not import proof).
- Added `tests/release-asset-install-claude.test.sh` for archive shape smoke.
- Added Claude Desktop install path and boundaries to README §Install notes.
- Added anti-repeat rule `LIVE_V0_2_5_0_CLAUDE_INSTALL_BROKEN` to AGENTS.md.
- Added `docs/audits/archive/v0.2.5.0-claude-install-repair.md` audit ledger.

**Tag and asset repair:**
- Tag `v0.2.5.0` moved from pre-repair commit `8df3c07c`
  (old tag object `411389558c`) to repair HEAD so GitHub source archives
  contain the fixed builder and tests.
- `IMPLEMENTAUDIT.skill` rebuilt with corrected root shape.
  Archive SHA256: `53b56a5dba67263ef9648289980982b75d0b037acc6ece41811346e9fe425566`
  (changed from original `a4d953d...` due to structural fix + platform ZIP ordering).
- `CHECKSUMS.txt` regenerated.
- Live `v0.2.5.0` release assets replaced with `--clobber`.

## [v0.2.4.5] - 2026-06-06

### Added

- Added a v0.2.4.5 audit ledger at
  `docs/audits/archive/v0.2.4.5-graphify-activegraph-honesty.md`.
- Installed Graphify and ActiveGraph into an isolated temporary Python
  environment for release-lane evidence:
  - Graphify CLI `0.8.32` from PyPI package `graphifyy`.
  - ActiveGraph CLI/package `1.0.5.post2`.
- Recorded a project-shaped ActiveGraph custody smoke in a temporary SQLite
  store outside the repo, then inspected and exported it through the
  ActiveGraph CLI.

### Changed

- Audited Graphify and ActiveGraph as optional external sidecars, installed and
  used them against the project or project-shaped evidence, reconciled findings
  into the canonical audit object, and preserved package minimality so sidecar
  outputs do not ship in the `.skill` asset.
- Hardened release-asset builder, installer, and tests so sidecar outputs such
  as `graph.json`, SQLite event stores, and JSONL trace files are rejected even
  when they appear under otherwise allowed package paths.
- Updated repo-facing milestone text from `v0.2.4.0` to `v0.2.4.5` while
  preserving manifest version `0.2.4`.

### Safety

- Preserved Graphify as optional terrain/orientation evidence only.
- Preserved ActiveGraph as optional custody/event evidence only.
- Preserved Markdown/transcript/package-governed audit objects as canonical.
- Did not vendor Graphify or ActiveGraph dependencies into this repo.
- Did not make sidecar install, indexing, event-store setup, export, public
  install verification, or sidecar-backed correctness mandatory for ordinary
  runtime/package use.

## [v0.2.4.0] - 2026-06-06

### Added

- Added native Stage 0-7 planner semantics to `skills/implementaudit/SKILL.md` for goal
  synthesis and phased audit closure: context/repo-state detection, audit
  intake/routing, Recon/Gemba, risk/dependency thinking, phase decomposition,
  runtime artifact writing, self-critique, pre-flight smoke, and one
  ready-to-paste handoff when not already embedded.
- Added `skills/implementaudit/templates/THINKING.md` as a reviewable runtime planning artifact
  for route, owner/source, risks, dependencies, rollback, evidence strategy,
  generated artifacts, optional sidecar boundaries, and pre-flight caveats.
- Added `scripts/check-planner-stages.sh` and `tests/planner-stages.test.sh`
  to enforce the native planner-stage contract, `THINKING.md` coverage, and
  repo-facing identity boundaries in tracked files.
- Added `scripts/install-codex-from-release.sh` and
  `tests/release-asset-install.test.sh` so a local `IMPLEMENTAUDIT.skill`
  release asset can be checksum-verified and installed into a temporary
  Codex-style skill home during validation.
- Added a v0.2.4.0 audit ledger at
  `docs/audits/archive/v0.2.4.0-planner-stage-hardening.md`.
- Added `scripts/check-readme-toc.sh` and wired it into package validation so
  README Contents anchors are checker-validated.

### Changed

- Clarified README newcomer navigation, compact terminology, `AUDIT.md` run
  flow, loopability/re-entry, post-release correction framing, artifacts, and
  validation/release-evidence boundaries after the `v0.2.3.0` release.
- Carried forward the existing post-release README/onboarding audit ledger at
  `docs/audits/archive/readme-audit_202606052026.md` as prior evidence for the
  v0.2.4.0 onboarding polish, without claiming that v0.2.4.0 added that file.
- Refined source-generated README Mermaid diagrams after screenshot review so
  they use standard GitHub-renderable Mermaid without custom init/theme
  directives, keep release/provenance as a dashed separate gate, and label
  Graphify/ActiveGraph as optional non-proof sidecars.
- Tightened README onboarding navigation by adding `Runtime at a glance` to the
  Contents list and avoiding unexplained Gemba terminology before the
  Terminology section.
- Refined the source-generated invocation-mode Mermaid diagram so direct
  governance, embedded governance, and goal synthesis/phased handoff show
  distinct input shapes, control loops, artifacts, completion conditions, and
  second-`/goal` boundaries.
- Strengthened README onboarding with clearer Codex install/update guidance,
  Claude Code/plugin wording, SSH-vs-HTTPS clone caveat, local release-asset
  install commands, and the native explanation for one `/goal` rather than a
  fragile command chain.
- Updated planner references, runtime templates, package validation, release
  asset validation, install-copy smoke, and GitHub Actions so `THINKING.md` and
  Stage 0-7 planner behavior are part of the package contract.
- Updated package validation and CI so the release-asset install smoke verifies
  path-with-spaces handling and proves a stale checksum manifest fails.
- Clarified audit noun/action terminology so the runtime distinguishes
  evidence-bearing audit objects from auditing operations across direct,
  embedded, and goal-synthesis modes.
- Added stable internal mnemonics `tdqyq-audit-object` and
  `ydqyq-audit-action` to keep the noun/action distinction explicit in runtime
  contracts, templates, fixtures, and validators.
- Updated canonical runtime references, phase templates, checker coverage, and
  the transcript skeleton so `AUDIT_COMPLETE` means terminal verified closure of
  the audit object, not merely that an audit operation was attempted.
- Dogfooded the audit noun/action distinction by requiring release-affecting
  runs to produce an audit object, act against it, and verify terminal closure
  before release completion.
- Audited the `.skill` release asset boundary so installed packages include
  only runtime-load-bearing skill docs, templates, scripts, host metadata, and
  package-shape validation surfaces.
- Hardened release-asset installation so a checksummed archive is still rejected
  when it contains repo-only top-level paths outside the runtime payload.
- Bumped plugin manifest metadata from `0.2.3` to `0.2.4` for the
  `v0.2.4.0` project milestone.

### Safety

- Preserved IMPLEMENTAUDIT identity as audit-governed implementation, not a
  generic autonomous build runner.
- Preserved canonical behavior source in `skills/implementaudit/SKILL.md`; root
  `IMPLEMENTAUDIT.md` remains intentionally absent.
- Preserved optional Graphify terrain and optional ActiveGraph custody
  boundaries; no install, indexing, quickstart, config, event store, or export
  is claimed.
- Preserved separate gates for commit, push, tag, release, publication, and
  checksum-manifest provenance.
- Preserved repo audit ledgers, release notes, dogfood evidence, CI config,
  fixtures, and validation history as repo-side evidence rather than installed
  `.skill` payload.
- Preserved checksum-manifest provenance as bounded artifact-integrity evidence
  only. No signature, attestation, SBOM, license, marketplace verification,
  host install verification, package publication, or broader provenance claim is
  made by this changelog entry.
- Public GitHub release download-to-install verification was performed as a
  release-gate check for the cleaned `v0.2.4.0` same-version repair by
  installing the tagged release asset into a temporary Codex-style skill home.

## [v0.2.3.0] - 2026-06-05

### Added

- Added a native harness adaptation matrix at
  `docs/audits/archive/v0.2.3.0-harness-adaptation-matrix.md`, grounded in a fresh
  read-only inventory of an external staged-goal reference at commit
  `86f1b0095ed1f6f9dc99f550a6053c931a4f96f4`.
- Added `skills/implementaudit/scripts/repo-state.sh` and
  `skills/implementaudit/references/repo-state-comparison.md` so final audit, deliverable,
  release-readiness, and cleanliness checks compare the baseline to the
  complete working tree, including committed-after-baseline, staged, unstaged,
  deleted, and untracked work.
- Added `skills/implementaudit/scripts/validate-audit-spec.sh` plus valid/invalid audit-spec
  fixtures to check classification, owner/source, scope, constraints,
  acceptance, rollback, evidence, generated-surface, sidecar, and
  release/provenance boundary fields.
- Added `scripts/check-added-lines-clean.sh` to scan added/new lines for debug
  prints, session task markers, unsupported host/release/license claims,
  and repo-facing identity drift.
- Added focused tests for repo-state behavior, audit-spec validation, and
  added-line cleanliness/overclaim scanning.

### Changed

- Bumped plugin manifest metadata from `0.2.2` to `0.2.3` for the
  `v0.2.3.0` project milestone.
- Expanded environment, repo-contract, and brownfield summary helpers so they
  identify package metadata, canonical owners, generated surfaces, fixtures,
  validators, CI, release/provenance surfaces, optional sidecar roots, and
  likely regression surfaces.
- Updated `AGENTS.md` with durable harness-adaptation rules: external staged
  skills are reference inputs only, useful concepts must be classified before
  adaptation, and final audit evidence must include the complete working tree
  when a baseline is available.
- Updated the execution-spine Mermaid source and regenerated README so the
  lifecycle is readable as invocation/intake -> greenfield/brownfield/mixed
  routing -> owner/source patch -> generated refresh -> Smoke A/B -> complete
  working-tree check -> final audit -> terminal marker, with release/provenance
  visibly gated after ordinary run completion.
- Expanded child-agent report templates and examples so v0.2.3.0 dogfood
  evidence can record read-only and adversarial audit coverage across all three
  audit inputs with verdicts, inspected files, commands, required patches,
  canaries, closure, remaining risk, and next action.
- Extended package verification, release-asset validation, and CI workflow
  coverage for the new helpers, references, fixtures, and tests.

### Safety

- Preserved IMPLEMENTAUDIT identity as audit-governed implementation, not a
  generic runner.
- Preserved generated-source discipline: README Mermaid remains generated from
  `docs/diagrams/*.mmd`; canonical skill behavior lives in `skills/implementaudit/SKILL.md`.
- Removed the tracked root `IMPLEMENTAUDIT.md` behavior file by owner decision
  to avoid repo-name/file-name confusion. Prior mirror/pointer compatibility was
  intentionally replaced with a validator-enforced absence rule.
- Preserved Graphify as optional terrain only and ActiveGraph as optional
  custody only; no install, indexing, quickstart, config, event store, or export
  is claimed.
- Preserved separate gates for commit, push, tag, release, publication, and
  checksum-manifest provenance.
- No license, marketplace verification, host install verification, signing,
  attestation, SBOM, package publication, or broader provenance claim is made by
  this changelog entry.

### Provenance notes

- When release/provenance is separately authorized, the repo-supported
  provenance surface remains the generated checksum manifest for
  `IMPLEMENTAUDIT.skill`. A checksum manifest is not a signature, attestation,
  SBOM, license, marketplace verification, or install verification.

## [v0.2.2.0] - 2026-06-05

### Added

- Added canonical greenfield, brownfield, and mixed-mode routing semantics in
  `skills/implementaudit/references/routing.md`.
- Added greenfield intake requirements for owner/source, scope, non-scope,
  constraints, acceptance criteria, rollback/removal path, evidence plan,
  generated-artifact plan, sidecar status, and canonical-vs-sidecar boundaries.
- Added brownfield inspection requirements for existing owner/source, contracts,
  tests, smokes, checkers, generated artifacts, sidecars, regression surface,
  and rollback path before mutation.
- Added routing fixtures for `greenfield-goal-synthesis`,
  `brownfield-audit-closure`, and `mixed-greenfield-in-brownfield`.
- Added `scripts/check-routing.sh` and `tests/routing.test.sh` so valid routing
  examples pass, invalid examples fail, sidecar boundaries remain optional, and
  README/reference identity cannot drift into endorsed generic runner framing.
- Added `docs/audits/INDEX.md` as a compact dogfood-history index grounded in
  repo commits, changelog entries, and fixtures.

### Changed

- Bumped plugin manifest metadata from `0.2.1` to `0.2.2` for the
  `v0.2.2.0` project milestone.
- Updated `AGENTS.md` with durable routing rules for greenfield, brownfield,
  and mixed work.
- Updated README with positive audit-governed identity language and routing
  intake/inspection boundaries.
- Extended package validation, release asset validation, install-copy smoke,
  and CI workflow coverage for the routing reference and tests.

### Safety

- Preserved generated-source discipline for the then-current package contract:
  README Mermaid freshness remains checked by
  `scripts/generate-readme-diagrams.sh --check`.
- Preserved Graphify as optional terrain only and ActiveGraph as optional
  custody only; neither sidecar is canonical proof for routing decisions.
- Preserved Markdown ledgers and final reports as valid fallback.
- Preserved separate gates for commit, push, tag, release, publication, and
  checksum-manifest provenance.
- No license, marketplace verification, host install verification, signing,
  attestation, SBOM, package publication, or broader provenance claim is made by
  this changelog entry.

### Dogfood evidence

- This entry closes the greenfield/brownfield routing dogfood audit by adding
  executable validation and fixtures rather than prose-only claims.
- `docs/audits/INDEX.md` records the prior v0.2.1.0 dogfood evidence found in
  current repo history and states what remains unverified.

## [v0.2.1.0] - 2026-06-05

### Added

- Added a standalone transcript contract reference for planner, phase, failure,
  final-audit, handoff, and completion markers.
- Added marker-order validation for transcript skeletons so
  `AUDIT_COMPLETE` must precede `IMPLEMENTAUDIT_RUN_COMPLETE`, and handoff or
  failure transcripts cannot also claim run completion.
- Added a zero-optional-tool worked example showing complete Markdown fallback
  behavior when Graphify and ActiveGraph are absent.
- Added generated README Mermaid diagram sources under `docs/diagrams/` plus a
  generator/check script to prevent hand-maintained diagram drift.
- Added focused shell tests for marker ordering, release asset reproducibility,
  checksum generation, blocked-path exclusion, package contract drift, and
  manual skill copy smoke behavior.
- Added a GitHub Actions validation workflow that mirrors the local package
  checks on pushes and pull requests.
- Added host-claim validation to guard unsupported install, marketplace,
  license, publication, and provenance claims.

### Changed

- Bumped plugin manifest metadata from `0.2.0` to `0.2.1` for the
  `v0.2.1.0` project milestone.
- Tightened `scripts/verify-package.sh` to enforce the new transcript,
  diagram, fixture, test, host-claim, and release-asset checks.
- Extended release asset validation to include diagram sources and the
  transcript contract reference while preserving the `skills/` payload contract.
- Updated `AGENTS.md`, README, and package docs so the durable repo contract
  names v0.2.1.0 as the current milestone and keeps checksums separate from
  signatures, attestations, SBOMs, licenses, marketplace verification, and host
  install verification.

### Upgrade notes

- After a release, reinstall or update the skill in the host you use. Do not
  assume a local copied skill has updated just because the GitHub repo has a new
  release.
- Codex manual installs do not have a marketplace auto-update path documented in
  this repo. Repeat the README's flat-layout copy step after each release:
  `cp -R skills/* ~/.codex/skills/implementaudit/` or the documented PowerShell
  `Copy-Item -Recurse -Force .\skills\* "$env:USERPROFILE\.codex\skills\implementaudit\"`.
- Claude Code/plugin users should use the host's documented plugin update or
  reload flow when available. This changelog does not claim that plugin update,
  marketplace refresh, install, publication, or provenance behavior has been
  verified by host execution.

### Safety

- Preserved the default stance that commit, push, tag, release, publication,
  provenance, Graphify indexing, and ActiveGraph setup/export require separate
  explicit authorization.
- Preserved Graphify as optional orientation evidence only and ActiveGraph as
  optional custody evidence only.
- Added checksum-manifest provenance support only for release gates where the
  checksum file is actually generated, validated, and attached.
- Kept LICENSE as an owner decision because no `LICENSE` file is present.

## [v0.2.0.0] - 2026-06-05

### Added

- Added the flat packaged skill layout at `skills/implementaudit/SKILL.md`; the package
  migration originally synchronized it with a root compatibility file, which was
  later removed by owner decision in `v0.2.3.0`.
- Added `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` as
  package metadata. These files are JSON-validated, but no install,
  marketplace, release, publication, or provenance behavior is claimed as
  verified.
- Added progressive-disclosure references for planning depth, phase design,
  `/goal` handoff format, and child/subagent review loops.
- Added `.IMPLEMENTAUDIT` templates for roadmaps, state, phase goals, child-agent
  reports, and the execution protocol.
- Added dependency-light validation and orientation scripts under
  `skills/scripts` plus root package validation in `scripts/verify-package.sh`.
- Added `scripts/build-release-asset.sh` to build and extraction-validate the
  repo-defined `IMPLEMENTAUDIT.skill` GitHub release asset without uploading it.
- Added simple audit fixtures and child-agent review fixtures.
- Added `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and `.gitignore`.

### Changed

- Reconciled repository documentation around the flat package contract,
  optional Graphify/ActiveGraph boundaries, local trace discipline, and
  repo-local learning through `AGENTS_UPDATE_DECISION`.
- Hardened final-audit marker semantics so `AUDIT_COMPLETE` precedes
  `IMPLEMENTAUDIT_RUN_COMPLETE` and `AUDIT_HANDOFF` is handoff-only.
- Hardened authorization boundary wording across templates and references.
- Hardened child/subagent guidance so root `AGENTS.md` owns durable rules and
  packaged reference material remains explanatory.
- Hardened validation coverage for planner markers, child-agent artifacts,
  evidence boundaries, version/milestone wording, and repo-facing identity hygiene.
- Documented that `.skill` is not claimed as a universal host-standard archive
  format by local evidence; `IMPLEMENTAUDIT.skill` is this repo's release asset
  name unless host evidence later proves a stricter format.

### Upgrade notes

- After a release, reinstall or update the skill in the host you use. Do not
  assume a local copied skill has updated just because the GitHub repo has a new
  release.
- Codex manual installs do not have a marketplace auto-update path documented in
  this repo. Repeat the README's flat-layout copy step after each release:
  `cp -R skills/* ~/.codex/skills/implementaudit/` or the documented PowerShell
  `Copy-Item -Recurse -Force .\skills\* "$env:USERPROFILE\.codex\skills\implementaudit\"`.
- Claude Code/plugin users should use the host's documented plugin update or
  reload flow when available. This changelog does not claim that plugin update,
  marketplace refresh, install, release, publication, or provenance behavior has
  been verified.
- The GitHub release for `v0.2.0.0` includes the `IMPLEMENTAUDIT.skill` release
  asset. No checksum manifest, attestation, signing, SBOM, license, install
  verification, marketplace verification, or provenance beyond the release
  asset upload is claimed for that milestone.

### Safety

- Preserved the default stance: no commit, push, tag, release, publication,
  provenance, Graphify indexing, or ActiveGraph setup/export without separate
  explicit authorization.
- Preserved evidence boundaries: Graphify is orientation only, ActiveGraph
  custody is not correctness proof, Markdown fallback remains valid, and live
  files remain source of truth.
- Preserved ImplementAudit identity: audit closure, owner/source patching,
  Smoke A/B, local git trace discipline, final audit before completion, and
  repo-local anti-repeat rules.

### Deferred

- LICENSE remains an owner decision; no license file is added without selected
  license evidence.
- Host install, marketplace, tag, release, publication, and provenance behavior
  remain unverified and separately gated.
- Uploading `IMPLEMENTAUDIT.skill` remains blocked until an explicit GitHub
  release gate authorizes asset attachment.

## [v0.1.0.0] - Reconstructed pre-package baseline

This is the polished single-file `/implementaudit` baseline before the
`v0.2.0.0` package migration. The historical tag target is reconstructed from
`origin/main` at commit `bb3aa37`. A GitHub release for `v0.1.0.0` exists as a
pre-package baseline and does not include `IMPLEMENTAUDIT.skill`, package
publication, marketplace verification, host install verification, or provenance.

### Added

- Polished the single-file `/implementaudit` method before package migration.
- Added the execution spine and run invariants.
- Added local git trace discipline with verbose commit bodies.
- Added commit granularity rules.
- Added `AGENTS.md` standardization discipline.
- Added optional first-run Graphify/ActiveGraph onboarding.
- Added ActiveGraph-backed Capability Ledger / Officer CV behavior.
- Added Graphify-assisted Gemba.
- Added Graphify/ActiveGraph interop contract compliance clarifications.
- Refreshed README for the then-current architecture.

### Safety

- Separated local commit, push, tag, release, publication, and provenance gates.
- Preserved no proof claim without evidence.
- Preserved Graphify as optional terrain context and ActiveGraph as optional
  custody context, not proof.

### Notes

- Reconstructed from repo history, including the 2026-05-31 documentation
  commits `7d2119b`, `455f410`, `ec640db`, `e8b1bbe`, `62ea480`, and
  `bb3aa37`.
- No package asset, marketplace verification, package publication, host install
  verification, or provenance is claimed for this reconstructed entry.

## [v0.0.1] - Reconstructed rough draft

### Added

- Established the initial rough `/implementaudit` method.
- Converted audit findings into bounded repository changes.
- Introduced PDCA, Gemba, Smoke Before Claim, Andon, Hansei, 5 Whys, and Plan
  Closure.
- Introduced P0/P1/P2 ledger closure.
- Introduced owner/source patching.
- Introduced the basic no unsafe actions / no proof without evidence stance.

### Notes

- Reconstructed from early repo history, including 2026-05-19 commits `a809d10`,
  `4b09b95`, `ea584d3`, `2035c80`, and `92ef58c`.
- Any earlier public availability is not verified by current repo evidence and
  is not claimed as a release.
