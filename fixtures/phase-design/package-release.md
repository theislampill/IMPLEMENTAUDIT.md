# Phase shape: package + release

**Shape:** Build a distributable artifact and publish it to a live registry or release surface.
**Phases:** 4
**P4-1 hardening:** included (Phase 4 as post-release verification + hardening)
**P4-2 visual polish:** N/A (CLI artifact, no UI — documented skip)
**P4-3 brownfield safety-net:** N/A (no risky brownfield mutation — documented skip)
**P4-4 package/release split:** enforced (Phase 2 = package, Phase 3 = release)
**P4-5 provenance boundary:** enforced (Phase 3 re-runs Smoke Before Claim against live surface)

---

## Phase 1 — Implement + test

Owner/source: src/, package.json
Work: Implement all features in scope; all tests pass; changelog updated.
Acceptance criteria:
- Full test suite passes
- Changelog entry for release version written
- No debug prints or session markers (check-added-lines-clean exits 0)
Mandatory commands: npm test, bash scripts/verify-package.sh
Rollback: git checkout HEAD -- src/
Depends on: none

## Phase 2 — Package (local artifact)

Owner/source: scripts/build-release-asset.sh (or equivalent build script)
Work: Build distributable artifact; compute checksum; validate locally.
Acceptance criteria:
- Artifact file exists at expected path with correct name
- Checksum written to CHECKSUMS.txt
- Artifact unpacks cleanly (extraction validation passes)
- Artifact SHA256 matches CHECKSUMS.txt
Evidence type: locally-produced file + checksum (NOT live-registry proof)
Mandatory commands: bash scripts/build-release-asset.sh, bash scripts/write-release-checksums.sh
Rollback: rm <artifact>; re-run build
Depends on: Phase 1

## Phase 3 — Release (publish to registry/surface)

Owner/source: release surface (GitHub releases, npm registry, etc.)
Work: Publish artifact; confirm live availability.
Acceptance criteria:
- Release tag created at correct version
- Artifact available at live URL (HTTP 200 / registry lookup confirms)
- Checksum on live artifact matches locally-built CHECKSUMS.txt
Evidence type: live-registry confirmation (NOT package-phase evidence)
Smoke Before Claim: fresh live-URL fetch after publish; do not reuse Phase 2 evidence
Mandatory commands: gh release create ..., curl -sI <release-url> (or equivalent)
Rollback: gh release delete <tag> --yes; git tag -d <tag>; git push origin :refs/tags/<tag>
Depends on: Phase 2

## Phase 4 — Post-release hardening

Owner/source: docs/, CHANGELOG.md, release notes
Work: Confirm live artifact installs correctly; update post-release docs.
Acceptance criteria:
- Live artifact installs into a clean target without error
- Install smoke exits 0
- Release notes finalized
- CHANGELOG.md committed with correct version
Mandatory commands: bash scripts/install-from-release.sh (or equivalent), bash scripts/verify-package.sh
Rollback: N/A (read-only verification + docs)
Depends on: Phase 3

---

P4-2 skip rationale: CLI/package artifact has no visible user-facing UI output.
P4-3 skip rationale: No existing risky brownfield source is mutated in this plan.
