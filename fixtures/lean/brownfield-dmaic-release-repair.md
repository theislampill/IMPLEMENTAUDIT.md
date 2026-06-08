# Fixture: DMAIC brownfield release repair

Route: DMAIC (brownfield — existing defect/release repair)

## Define
Defect: Release asset built with ZIP_STORED instead of ZIP_DEFLATED; 23 entries uncompressed.
Owner/source: `scripts/build-release-asset.sh` (ZipInfo.compress_type not set per entry).
Scope: asset compression fix + compression regression test.
Non-scope: feature additions, other release scripts.
User/consumer impact: asset 2.6× larger than necessary; no functional difference.
Acceptance target: all 23 entries ZIP_DEFLATED; asset ≤120,000 bytes; SHA256 confirmed.

## Measure
Smoke A: `bash tests/release-asset.test.sh` → FAIL (stored entries found).
Current behavior: `zipfile.ZipInfo` defaults to `compress_type=0` (ZIP_STORED); ZipFile-level
default does not override per-entry ZipInfo.
Failure rate: 100% of entries (23/23 ZIP_STORED when the bug is present).
Working-tree state: `git status --short` shows build-release-asset.sh modified.

## Analyze
Root cause: `writestr(ZipInfo_obj, data)` uses `ZipInfo.compress_type`, not the ZipFile-level
default. ZipInfo defaults to ZIP_STORED (0). Developer set `zipfile.ZIP_DEFLATED` on ZipFile
but not on each ZipInfo.
Muda: extra asset size (95,199 bytes wasted); no functional value.
Mura: none (consistent bug across all entries).
Muri: none (fix is a one-liner per entry).
Regression risk: low — ZipInfo default is stable CPython behavior.

## Improve
Patch `scripts/build-release-asset.sh`: add `info.compress_type = zipfile.ZIP_DEFLATED` after
each `ZipInfo` construction.
Regenerate asset: `bash scripts/build-release-asset.sh dist/IMPLEMENTAUDIT.skill`.
Add regression test: `tests/release-asset.test.sh` gains a stored-entry check.
Run checks: `bash tests/release-asset.test.sh` → ok.

## Control
Sustain: `tests/release-asset.test.sh` compression check + `MAX_ASSET_BYTES = 120_000` guard.
AGENTS.md anti-repeat rule: V0260-ZIPINFO-COMPRESSION.
CI: validate.yml runs `release-asset.test.sh`.
