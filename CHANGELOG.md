# Changelog

All notable changes to this project are recorded here.

This project follows Keep a Changelog style. Historical entries marked
`Reconstructed` are reconstructed from repo history and conversation context,
not from verified tags, releases, publication, marketplace verification, or
provenance.

Plugin manifest versions are host-facing package metadata. The `v0.2.5.0`
project milestone maps to plugin manifest version `0.2.5` because no local
schema evidence proved four-component plugin manifest versions are accepted.

## [Unreleased]

### Changed

- `skills/SKILL.md`: updated `description` frontmatter and opening body to make deep planning and phase-by-phase execution until terminal audit closure or audited handoff explicit in the canonical skill identity. Added the sentence: "IMPLEMENTAUDIT plans deeply and executes repo work phase-by-phase until terminal audit closure or an explicit audited handoff. It makes repo changes that are auditable, bounded, owner/source-grounded, reversible, and not overclaimed."
- `README.md`: updated opening paragraph and "What it is" section to match SKILL.md identity; added "Blocked work ends in an explicit audited handoff, not fake completion" boundary statement; preserved "not a generic autonomous build runner" distinction.
- `AGENTS.md`: extended routing rule to include deep-planning and phase-execution identity; guards against regression to "audit-only" or "generic autonomous builder" framing.
- `skills/references/planning-depth.md`: added one-line terminal closure alignment to Depth rule section.
- `skills/references/phase-design.md`: added one-line phase execution continuity statement to opening paragraph.

## [v0.2.6.0] - 2026-06-07

### Added

- Added `skills/scripts/validate-phase.sh` 19-failure-mode checks: IMPLEMENTAUDIT_PHASE_START/VERIFY/DONE, AGENTS_UPDATE_DECISION, CONTINUITY_DECISION, Run root, Baseline ref, Owner/source, Task, Type, Depends on phases, Work section, Acceptance criteria (non-placeholder), Mandatory commands section (non-placeholder), Evidence required section (non-placeholder), Rollback/defer path, Markdown fallback status. `tests/phase-validation.test.sh` updated to 20/20 (1 positive + 19 failure modes). `fixtures/phase-validation/valid-full-spec.md` added as positive test fixture.
- Added `scripts/check-forbidden-terms.sh`: generic forbidden-string checker accepting caller-supplied terms at runtime (never embedded in source). Wired into AGENTS.md identity hygiene release-gate instructions.
- Added `skills/references/phase-design.md` §"Phase shape requirements" with 7 rules: P4-1 hardening-phase requirement, P4-2 visual polish evidence, P4-3 brownfield safety-net, P4-4 package/release split, P4-5 provenance boundary fresh Smoke Before Claim, P4-6 hardening scope restriction, P4-7 skip documentation.
- Added 5 phase-shape fixture outlines at `fixtures/phase-design/`: simple-greenfield, brownfield-mutation, ui-feature, package-release, full-hardening-run.
- Added concrete 16-step per-phase execution loop to `skills/templates/PROTOCOL.md`.
- Added exact 3-strike failure recovery (FAILURE_PROBE / FAILURE_ESCALATE / FAILURE_HANDOFF) with step-by-step protocol to `PROTOCOL.md`; updated `skills/references/transcript-contract.md`.
- Added final audit exactness to `PROTOCOL.md`: AUDIT_START (round/criteria/command), phase completeness check, mandatory command re-run, coverage math `re_verified/(re_verified+trust_prior)`, trust-prior > 30% warning, 3-round audit-fix loop, AUDIT_HANDOFF path, ordering rules.
- Added mid-run interruption handling to `PROTOCOL.md`: IMPLEMENTAUDIT_PAUSE marker, 4-option menu (Resume/Revise spec/Skip phase/Stop), resume contract (5 steps), STATE.md INTERRUPTED state.
- Added 8 dispatch-prep steps to `SKILL.md` Stage 5: STATE.md READY_TO_DISPATCH, baseline ref from git, PROTOCOL.md copy, repo-state.sh evidence, phase-spec existence check, validate-phase.sh on all specs, command dedup, handoff gated on Stage 6.5 PREFLIGHT_GREEN.
- Added 7 Phase 4 shape rules to `SKILL.md` Stage 4 bullet list (P4-1..P4-7) + fixture reference.
- Added Stage 7 gating clause: handoff only after Stage 5 dispatch-prep and Stage 6.5 PREFLIGHT_GREEN.
- Added behavioral continuity tests to `tests/continuity.test.sh` (25/25): 6 scenarios covering memory-absent run, no-write-warranted, safe-note frontmatter, unsafe-content rejection, final-project ordering, no-boundary-crossing. 6 fixtures at `fixtures/continuity/`.
- Added behavioral sidecar tests to `tests/sidecars.test.sh` (24/24): 7 scenarios covering Graphify absent/fresh/stale, ActiveGraph absent/unauthorized/authorized, sidecar-overclaim-rejected. 7 fixtures at `fixtures/sidecars/`.
- Deepened `skills/scripts/detect-stack.sh`: package-scripts (npm script enumeration), python-hints (pyproject.toml/requirements.txt), language/framework hints (extension counts, framework config files), source/test directory layout, config/infra inventory.
- Deepened `skills/scripts/summarize-repo.sh`: test-surface-summary, file-extension-counts, recently-churned-files, largest-tracked-files, likely-generated-outputs, mandatory-command-candidates from detected scripts.
- Added AGENTS.md §"Identity hygiene release-gate" with anti-repeat rule (v0.2.6.0), check-forbidden-terms.sh usage, and release-gate protocol.
- Added `docs/audits/v0.2.6.0-operational-parity-hardening.md`: 12 gap classes (G1-G12), all ADAPTED or INTENTIONALLY REJECTED with documented alternative, identity hygiene check section.
- Updated `docs/audits/INDEX.md` with v0.2.6.0 entry.
- Updated CI (`validate.yml`): removed "Validate phase template" step (template has placeholder content by design; install-copy-smoke.test.sh covers validator execution).

### Changed

- `skills/templates/phase-goal.txt` expanded from thin mnemonic skeleton to full executable spec with all required structural sections (Phase N/TOTAL, Task, Type, Run root, Baseline ref, Owner/source, Audit object, Auditing operation, Terminal object state, Thinking ref, Mandatory commands, Acceptance criteria, Evidence required, Depends on phases, Why, Work, Acceptance criteria block, Mandatory commands block, Evidence required block, Rollback, Graphify/ActiveGraph/Markdown fallback, Cleanliness override, Notes, IMPLEMENTAUDIT_PHASE_VERIFY full block, AGENTS_UPDATE_DECISION, CONTINUITY_DECISION, IMPLEMENTAUDIT_PHASE_DONE).
- `tests/install-copy-smoke.test.sh`: replaced `validate-phase.sh` call against template with inline filled smoke spec (template has placeholder content by design).
- Plugin manifest metadata: `0.2.5` → `0.2.6` (pending release authorization after dogfood gate).

### Safety

- Comparator evidence used as read-only reference only; the external staged-goal comparator's proper name, slash command, marker names, artifact paths, and memory markers were not imported into any tracked repo file, commit message, branch name, tag name, PR title, or release note.
- All 12 gap classes resolved without importing external identity.
- `check-forbidden-terms.sh` uses caller-supplied terms at runtime; the forbidden term is never embedded in source.

## [v0.2.5.0] - 2026-06-07

### Added

- Added a neutral v0.2.5.0 comparator gap-closure audit ledger at
  `docs/audits/v0.2.5.0-external-staged-goal-runtime-gap-closure.md`.
- Added native namespaced run-root claiming with `skills/scripts/claim-run.sh`
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
  comparator package identity, artifact paths, marker names, and memory markers
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
`skills/SKILL.md` (wrong root shape). Claude Desktop's import contract requires
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
- `tests/release-asset.test.sh` updated; added regression guard: `skills/SKILL.md`
  in archive is now a hard failure.
- `tests/release-asset-install.test.sh`,
  `tests/release-asset-install-claude.test.sh`: sidecar test paths updated.
- `scripts/verify-package.sh`: plugin `skills` path check updated.

**Secondary root cause:** No live Claude Desktop import was run in the release gate.
- Added `scripts/install-claude-from-release.sh` (file-copy workaround, not import proof).
- Added `tests/release-asset-install-claude.test.sh` for archive shape smoke.
- Added Claude Desktop install path and boundaries to README §Install notes.
- Added anti-repeat rule `LIVE_V0_2_5_0_CLAUDE_INSTALL_BROKEN` to AGENTS.md.
- Added `docs/audits/v0.2.5.0-claude-install-repair.md` audit ledger.

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
  `docs/audits/v0.2.4.5-graphify-activegraph-honesty.md`.
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

- Added native Stage 0-7 planner semantics to `skills/SKILL.md` for goal
  synthesis and phased audit closure: context/repo-state detection, audit
  intake/routing, Recon/Gemba, risk/dependency thinking, phase decomposition,
  runtime artifact writing, self-critique, pre-flight smoke, and one
  ready-to-paste handoff when not already embedded.
- Added `skills/templates/THINKING.md` as a reviewable runtime planning artifact
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
  `docs/audits/v0.2.4.0-planner-stage-hardening.md`.
- Added `scripts/check-readme-toc.sh` and wired it into package validation so
  README Contents anchors are checker-validated.

### Changed

- Clarified README newcomer navigation, compact terminology, `AUDIT.md` run
  flow, loopability/re-entry, post-release correction framing, artifacts, and
  validation/release-evidence boundaries after the `v0.2.3.0` release.
- Carried forward the existing post-release README/onboarding audit ledger at
  `docs/audits/readme-audit_202606052026.md` as prior evidence for the
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
- Preserved canonical behavior source in `skills/SKILL.md`; root
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
  `docs/audits/v0.2.3.0-harness-adaptation-matrix.md`, grounded in a fresh
  read-only inventory of an external staged-goal comparator at commit
  `86f1b0095ed1f6f9dc99f550a6053c931a4f96f4`.
- Added `skills/scripts/repo-state.sh` and
  `skills/references/repo-state-comparison.md` so final audit, deliverable,
  release-readiness, and cleanliness checks compare the baseline to the
  complete working tree, including committed-after-baseline, staged, unstaged,
  deleted, and untracked work.
- Added `skills/scripts/validate-audit-spec.sh` plus valid/invalid audit-spec
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
  skills are comparator inputs only, useful concepts must be classified before
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
  `docs/diagrams/*.mmd`; canonical skill behavior lives in `skills/SKILL.md`.
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
  `skills/references/routing.md`.
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

- Added the flat packaged skill layout at `skills/SKILL.md`; the package
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
