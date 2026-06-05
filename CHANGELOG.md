# Changelog

All notable changes to this project are recorded here.

This project follows Keep a Changelog style. Manifest versions are package
metadata only until a tag or release is explicitly authorized and evidenced.

## [Unreleased]

### Added

- Added the flat packaged skill layout at `skills/SKILL.md`, synchronized with
  `IMPLEMENTAUDIT.md` as the compatibility root.
- Added `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` as
  package metadata. These files are JSON-validated, but no install,
  marketplace, release, or publication behavior is claimed as verified.
- Added progressive-disclosure references for planning depth, phase design, and
  `/goal` handoff format.
- Added `.IMPLEMENTAUDIT` templates for roadmaps, state, phase goals, and the
  execution protocol.
- Added dependency-light validation and orientation scripts under `skills/scripts`
  plus root package validation in `scripts/verify-package.sh`.
- Added a simple audit fixture and expected ledger shape.
- Added `CLAUDE.md`, `CONTRIBUTING.md`, and `.gitignore`.

### Changed

- Reconciled repository documentation around the flat package contract,
  optional Graphify/ActiveGraph boundaries, and local trace discipline.

### Safety

- Preserved the default stance: no commit, push, tag, release, publication,
  provenance, Graphify indexing, or ActiveGraph setup/export without separate
  explicit authorization.
- Preserved evidence boundaries: Graphify is orientation only, ActiveGraph
  custody is not correctness proof, and live files remain source of truth.

### Deferred

- LICENSE remains an owner decision; no license file is added without selected
  license evidence.
- Host install flows are documented as unverified unless tested during a
  separately authorized install/release gate.
