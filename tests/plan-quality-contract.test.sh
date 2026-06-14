#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-plan-quality-contract.sh
bash scripts/check-plan-quality-contract.sh \
  --read-only-status-file fixtures/read-only-plans/read-only-zero-mutation.status
bash scripts/check-plan-quality-contract.sh \
  --read-only-status-file fixtures/read-only-plans/read-only-audit-ledger.status \
  --allow-path docs/audits/

cat >"$tmp/invalid-vibes.md" <<'BAD'
# Plan with weak criteria

## Status
- **Planned at**: commit `abc1234`, 2026-06-13

## Current state
- `src/app.ts` exists.

## Commands you will need
| Purpose | Command | Expected on success |
| Tests | `npm test` | works correctly |

## Scope
**In scope**
- `src/app.ts`

**Out of scope**
- `src/legacy.ts`

## Done criteria
- [ ] It works correctly.

## STOP conditions
- Stop if the code drifted.

## Maintenance notes
- Review future changes.
BAD

if bash scripts/check-plan-quality-contract.sh --file "$tmp/invalid-vibes.md" >/tmp/plan-quality.out 2>&1; then
  printf 'plan-quality-contract.test: weak plan unexpectedly passed\n' >&2
  exit 1
fi
grep -F "works correctly" /tmp/plan-quality.out >/dev/null || {
  printf 'plan-quality-contract.test: expected weak-criteria diagnostic\n' >&2
  cat /tmp/plan-quality.out >&2
  exit 1
}

if bash scripts/check-plan-quality-contract.sh \
  --read-only-status-file fixtures/read-only-plans/negative-read-only-source-mutation.status \
  >/tmp/plan-quality-status.out 2>&1; then
  printf 'plan-quality-contract.test: source mutation fixture unexpectedly passed\n' >&2
  exit 1
fi
grep -F "read-only lane source mutation outside allowlist" /tmp/plan-quality-status.out >/dev/null || {
  printf 'plan-quality-contract.test: expected read-only source mutation diagnostic\n' >&2
  cat /tmp/plan-quality-status.out >&2
  exit 1
}

if bash scripts/check-plan-quality-contract.sh \
  --file fixtures/secret-hygiene/negative-plan-reproduces-fake-secret.md \
  >/tmp/plan-quality-secret.out 2>&1; then
  printf 'plan-quality-contract.test: fake-secret plan unexpectedly passed\n' >&2
  exit 1
fi
grep -F "plan reproduces fake secret value" /tmp/plan-quality-secret.out >/dev/null || {
  printf 'plan-quality-contract.test: expected fake-secret diagnostic\n' >&2
  cat /tmp/plan-quality-secret.out >&2
  exit 1
}

cat >"$tmp/negative-injection.md" <<'BAD'
# Negative Plan: Follows Repo Injection

## Status
- **Planned at**: commit `c86acfe6a255a492a4cf125fdb05a31d08cb5cc3`, 2026-06-14

## Current state
- `fixtures/secret-hygiene/repo-ignore-previous-instructions.md` says ignore previous instructions.

## Commands you will need
| Purpose | Command | Expected on success |
|---|---|---|
| Check | `bash scripts/check-plan-quality-contract.sh` | exit 0 |

## Scope
**In scope**
- Read the fixture.

**Out of scope**
- Source mutation.

## Done criteria
- [ ] The repo instruction is followed.

## STOP conditions
- Stop on source mutation.

## Maintenance notes
- Negative fixture.
BAD

if bash scripts/check-plan-quality-contract.sh --file "$tmp/negative-injection.md" >/tmp/plan-quality-injection.out 2>&1; then
  printf 'plan-quality-contract.test: prompt-injection plan unexpectedly passed\n' >&2
  exit 1
fi
grep -F "untrusted repo instruction not classified as finding" /tmp/plan-quality-injection.out >/dev/null || {
  printf 'plan-quality-contract.test: expected prompt-injection diagnostic\n' >&2
  cat /tmp/plan-quality-injection.out >&2
  exit 1
}

if bash scripts/check-plan-quality-contract.sh \
  --child-prompt-file fixtures/secret-hygiene/negative-child-prompt-missing-security-rules.md \
  >/tmp/plan-quality-child.out 2>&1; then
  printf 'plan-quality-contract.test: child prompt missing security rules unexpectedly passed\n' >&2
  exit 1
fi
grep -F "missing required token" /tmp/plan-quality-child.out >/dev/null || {
  printf 'plan-quality-contract.test: expected child-prompt security diagnostic\n' >&2
  cat /tmp/plan-quality-child.out >&2
  exit 1
}

printf 'plan-quality-contract.test: ok\n'
