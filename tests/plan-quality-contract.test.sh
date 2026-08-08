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

cp fixtures/read-only-plans/valid-handoff-plan.md "$tmp/single-issue-campaign.md"
printf '\ncampaign-issues: #142\n' >> "$tmp/single-issue-campaign.md"
bash scripts/check-plan-quality-contract.sh \
  --campaign-plan-file "$tmp/single-issue-campaign.md" >/dev/null 2>&1 || {
    printf 'plan-quality-contract.test: single-issue campaign gained topology ceremony\n' >&2
    exit 1
  }

cp fixtures/read-only-plans/valid-handoff-plan.md "$tmp/multi-issue-missing-topology.md"
printf '\ncampaign-issues: #141, #142\n' >> "$tmp/multi-issue-missing-topology.md"
if bash scripts/check-plan-quality-contract.sh \
    --campaign-plan-file "$tmp/multi-issue-missing-topology.md" \
    >/tmp/plan-quality-topology.out 2>&1; then
  printf 'plan-quality-contract.test: multi-issue plan without topology unexpectedly passed\n' >&2
  exit 1
fi
grep -F 'multi-issue campaign requires integration-topology' \
  /tmp/plan-quality-topology.out >/dev/null || {
    printf 'plan-quality-contract.test: expected missing-topology diagnostic\n' >&2
    cat /tmp/plan-quality-topology.out >&2
    exit 1
  }

for topology in independent stacked-cumulative justified:release-train; do
  plan="$tmp/multi-issue-${topology//:/-}.md"
  cp fixtures/read-only-plans/valid-handoff-plan.md "$plan"
  printf '\ncampaign-issues: #141, #142\nintegration-topology: %s\n' \
    "$topology" >> "$plan"
  bash scripts/check-plan-quality-contract.sh \
    --campaign-plan-file "$plan" >/dev/null 2>&1 || {
      printf 'plan-quality-contract.test: valid %s topology was rejected\n' "$topology" >&2
      exit 1
    }
done

cp fixtures/read-only-plans/valid-handoff-plan.md "$tmp/multi-issue-single-topology.md"
printf '\ncampaign-issues: #141, #142\nintegration-topology: single-issue\n' \
  >> "$tmp/multi-issue-single-topology.md"
if bash scripts/check-plan-quality-contract.sh \
    --campaign-plan-file "$tmp/multi-issue-single-topology.md" \
    >/tmp/plan-quality-topology.out 2>&1; then
  printf 'plan-quality-contract.test: multi-issue campaign accepted single-issue topology\n' >&2
  exit 1
fi

cp fixtures/read-only-plans/valid-handoff-plan.md "$tmp/malformed-campaign-duplicate.md"
printf '\ncampaign-issues: #141, #142\nintegration-topology: stacked-cumulative\ncampaign-issues: malformed\n' \
  >> "$tmp/malformed-campaign-duplicate.md"
if bash scripts/check-plan-quality-contract.sh \
    --campaign-plan-file "$tmp/malformed-campaign-duplicate.md" \
    >/tmp/plan-quality-topology.out 2>&1; then
  printf 'plan-quality-contract.test: malformed duplicate campaign row was ignored\n' >&2
  exit 1
fi

cp fixtures/read-only-plans/valid-handoff-plan.md "$tmp/empty-topology-duplicate.md"
printf '\ncampaign-issues: #141, #142\nintegration-topology: stacked-cumulative\nintegration-topology:\n' \
  >> "$tmp/empty-topology-duplicate.md"
if bash scripts/check-plan-quality-contract.sh \
    --campaign-plan-file "$tmp/empty-topology-duplicate.md" \
    >/tmp/plan-quality-topology.out 2>&1; then
  printf 'plan-quality-contract.test: empty duplicate topology row was ignored\n' >&2
  exit 1
fi

cp fixtures/read-only-plans/valid-handoff-plan.md "$tmp/split-campaign-declaration.md"
printf '\ncampaign-issues\n: #141, #142\nintegration-topology: stacked-cumulative\n' \
  >> "$tmp/split-campaign-declaration.md"
if bash scripts/check-plan-quality-contract.sh \
    --campaign-plan-file "$tmp/split-campaign-declaration.md" \
    >/tmp/plan-quality-topology.out 2>&1; then
  printf 'plan-quality-contract.test: split campaign declaration was accepted\n' >&2
  exit 1
fi

for keyword in Closes Fixes Resolves; do
  body="$tmp/pr-body-$keyword.md"
  printf '## Summary\n\n%s #141\n' "$keyword" > "$body"
  if bash scripts/check-plan-quality-contract.sh \
      --pr-body-file "$body" >/tmp/plan-quality-auto-close.out 2>&1; then
    printf 'plan-quality-contract.test: %s tracked-issue reference unexpectedly passed\n' "$keyword" >&2
    exit 1
  fi
  grep -F 'auto-closing tracked-issue reference is forbidden' \
    /tmp/plan-quality-auto-close.out >/dev/null || {
      printf 'plan-quality-contract.test: expected auto-close diagnostic for %s\n' "$keyword" >&2
      cat /tmp/plan-quality-auto-close.out >&2
      exit 1
    }
done

printf '## Summary\n\nImplements #141\n' > "$tmp/pr-body-implements.md"
bash scripts/check-plan-quality-contract.sh \
  --pr-body-file "$tmp/pr-body-implements.md" >/dev/null 2>&1 || {
    printf 'plan-quality-contract.test: non-closing Implements reference was rejected\n' >&2
    exit 1
  }

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
