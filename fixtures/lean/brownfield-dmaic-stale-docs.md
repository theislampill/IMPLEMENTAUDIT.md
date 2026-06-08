# Fixture: DMAIC brownfield stale docs

Route: DMAIC (brownfield — stale generated artifact)

## Define
Defect: README.md Mermaid diagram blocks out of date after `.mmd` source changes.
Owner/source: `docs/diagrams/*.mmd` (source); `scripts/generate-readme-diagrams.sh` (generator).
Scope: regenerate README blocks; enforce freshness check in CI.
Non-scope: diagram content changes (separate finding if content is wrong).
User/consumer impact: README shows stale diagram; users see incorrect runtime model.
Acceptance target: `bash scripts/generate-readme-diagrams.sh --check` exits 0.

## Measure
Smoke A: `bash scripts/generate-readme-diagrams.sh --check` → FAIL (blocks differ from source).
Current behavior: diagrams embedded in README.md do not match current `.mmd` source files.
Failure: content delta found between README blocks and source files.
Working-tree state: `git diff docs/diagrams/` shows changed source, README unchanged.

## Analyze
Root cause: `.mmd` source changed but `generate-readme-diagrams.sh` not re-run.
Muda: stale README content (no value, misleads users).
Mura: documentation surface inconsistent with behavior source.
Muri: none.
Regression risk: low — `--check` mode is idempotent.

## Improve
Run `bash scripts/generate-readme-diagrams.sh` to embed fresh diagram content.
Verify: `bash scripts/generate-readme-diagrams.sh --check` → ok.

## Control
Sustain: `validate.yml` runs `generate-readme-diagrams.sh --check` in CI.
Standard check in `scripts/verify-package.sh`.
