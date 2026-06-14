# Fixture: mixed DMAIC/DMADV package boundary

Route: mixed — DMAIC for brownfield package boundary repair + DMADV for new boundary manifest

## DMAIC shell (brownfield — package boundary defect)

### Define
Defect: `.skill` asset includes files outside runtime skill payload (e.g., CHANGELOG.md, tests/).
Owner/source: `scripts/build-release-asset.sh` (include list).
Scope: remove non-runtime entries; add explicit exclusion list.
Non-scope: content of included files.
Acceptance target: `bash scripts/verify-package.sh` confirms 23-entry boundary manifest.

### Measure
Smoke A: `bash tests/release-asset.test.sh` — asset entries enumerated; stale entries found.
Failure: asset contains repo-only files (docs, tests, CHANGELOG) that are not runtime payload.

### Analyze
Root cause: include glob in build script too broad; no explicit manifest enforcing boundary.
Muda: repo-only files in asset (wasted bytes, boundary confusion).
Mura: manifest not verified across releases.

### Improve
Narrow include list in `scripts/build-release-asset.sh` to `skills/` + `.claude-plugin/`.
Add extraction validation step (already in build script).
Run `bash tests/release-asset.test.sh` → ok.

### Control
Sustain: `tests/release-asset.test.sh` + `scripts/verify-package.sh` in CI.

## DMADV artifact (greenfield — package boundary manifest)

### Define
New artifact: package boundary manifest in `scripts/build-release-asset.sh`
and package verification in `scripts/verify-package.sh`.
Scope: manifest proving what is and is not in the `.skill` package.
Owner/source of truth: `scripts/build-release-asset.sh` (builder) and
`scripts/verify-package.sh` (current gate).

### Measure
CtQ: manifest accurately lists all 23 entries; 14 proven-excluded categories documented.

### Analyze
Design: Markdown table of included entries + separate table of excluded categories.
Rollback: remove audit doc (repo-only, not shipped).

### Design
Phase spec: single phase; write audit doc after build-script repair.

### Verify
Smoke B: `bash tests/release-asset.test.sh` ok; package manifest gate is non-empty.
Package check: `bash scripts/verify-package.sh` ok.
