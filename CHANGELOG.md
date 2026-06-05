# Changelog

All notable changes to this project are recorded here.

This project follows Keep a Changelog style. Historical entries marked
`Reconstructed` are reconstructed from repo history and conversation context,
not from verified tags, releases, publication, marketplace verification, or
provenance.

Plugin manifest versions are host-facing package metadata. Project milestone
`v0.2.0.0` maps to plugin manifest version `0.2.0` because no local schema
evidence proved four-component plugin manifest versions are accepted.

## [v0.2.0.0] - Unreleased

### Added

- Added the flat packaged skill layout at `skills/SKILL.md`, synchronized with
  `IMPLEMENTAUDIT.md` as the compatibility root.
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
- Future `v0.2.0.0` GitHub release notes should include this same upgrade
  guidance if an explicit release gate authorizes publishing them. This
  changelog entry is not itself a release note, release, publication, or
  provenance claim.

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
`v0.2.0.0` package migration. The historical local tag target is reconstructed
from `origin/main` at commit `bb3aa37`; it is not a GitHub release, package
publication, marketplace verification, pushed tag, or provenance claim.

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
- No pushed tag, GitHub release, marketplace verification, package publication,
  or provenance is claimed for this reconstructed entry.

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
