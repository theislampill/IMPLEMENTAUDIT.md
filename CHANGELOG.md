# Changelog

All notable changes to this project are recorded here.

This project follows Keep a Changelog style. Historical entries marked
`Reconstructed` are reconstructed from repo history and conversation context,
not from verified tags, releases, publication, marketplace verification, or
provenance.

Plugin manifest versions are host-facing package metadata. Project milestone
`v0.2.3.0` maps to plugin manifest version `0.2.3` because no local schema
evidence proved four-component plugin manifest versions are accepted.

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
  and external comparator identity drift.
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
  native harness/checker lane is visible before Graphify-assisted Gemba and
  final audit.
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
  evidence boundaries, version/milestone wording, and forbidden naming drift.
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
