# Plan 001: Verify the read-only plans lane

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the next
> step. If a STOP condition occurs, stop and report.
>
> **Drift check (run first)**: `git diff --stat c86acfe6a255a492a4cf125fdb05a31d08cb5cc3..HEAD -- scripts tests fixtures docs/audits README.md CHANGELOG.md .claude-plugin skills/implementaudit/SKILL.md`
> If any in-scope file changed since this plan was written, compare the current
> state excerpts below against the live files before proceeding; on mismatch,
> stop and report.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MED
- **Depends on**: none
- **Category**: tests / docs / package
- **Planned at**: commit `c86acfe6a255a492a4cf125fdb05a31d08cb5cc3`, 2026-06-13

## Why this matters

The read-only planning lane must produce self-contained handoffs without
silently authorizing source mutation. The executor needs exact files, expected
commands, and release boundaries so a smaller agent can continue without
importing context from the planning session.

## Current state

- `scripts/verify-package.sh` owns package and test-registry validation.
- `.claude-plugin/plugin.json` currently carries the manifest version used by
  source-built assets.
- `docs/audits/INDEX.md` is the tracked dogfood-history index.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Contract | `bash scripts/check-capability-parity-contract.sh` | exit 0, generic capability parity accepted |
| Plan quality | `bash scripts/check-plan-quality-contract.sh` | exit 0, valid fixtures accepted |
| Package | `bash scripts/verify-package.sh` | exit 0, prints `verify-package: ok` |

## Scope

**In scope**

- `scripts/check-capability-parity-contract.sh`
- `scripts/check-plan-quality-contract.sh`
- `fixtures/read-only-plans/**`
- `fixtures/secret-hygiene/**`
- `docs/audits/INDEX.md`

**Out of scope**

- Any commit, push, tag, release, publication, provenance, issue creation, or
  install into a real user home.
- Adding a LICENSE file; license remains an owner decision.

## Steps

### Step 1: Verify capability parity fixtures

Verify that the active fixture roots cover read-only plans, secret hygiene,
dogfood bootstrap, and source-evidence pack checks without carrying product
comparison names into active validation.

**Verify**: `bash scripts/check-capability-parity-contract.sh` exits 0.

### Step 2: Add plan quality validation

Make plan examples fail on weak phrases, missing drift checks, missing STOP
conditions, missing out-of-scope lists, or commands without expected results.

**Verify**: `bash scripts/check-plan-quality-contract.sh` exits 0.

## Test plan

- Add shell tests under `tests/` that call the new checkers and include at
  least one negative fixture created in a temp directory.
- Run `bash scripts/check-validation-registry.sh`; expected: every new
  `tests/*.test.sh` appears in both local and CI registries.

## Done criteria

- [ ] `bash scripts/check-capability-parity-contract.sh` exits 0
- [ ] `bash scripts/check-plan-quality-contract.sh` exits 0
- [ ] `bash scripts/verify-package.sh` exits 0
- [ ] No files outside the in-scope source milestone are modified

## STOP conditions

Stop and report back if:

- A capability claim cannot be tied to an active owner/source file.
- The change requires creating issues, publishing a release, or installing into
  a real home directory.
- A validation command fails twice with different root causes.

## Maintenance notes

- Future capability checks should update fixtures and checkers together so proof
  rows cannot drift into prose-only claims.
- Keep public-release state separate from source-built package state.
