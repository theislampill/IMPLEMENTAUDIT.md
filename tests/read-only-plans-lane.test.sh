#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-capability-parity-contract.sh
bash scripts/check-plan-quality-contract.sh \
  --file fixtures/read-only-plans/valid-handoff-plan.md \
  --read-only-status-file fixtures/read-only-plans/read-only-zero-mutation.status

grep -F "Read-Only \`plans/\` Output Lane" skills/implementaudit/references/plan-lifecycle.md >/dev/null
grep -F "templates/read-only-plan.md" skills/implementaudit/references/plan-lifecycle.md >/dev/null
grep -F "Read-Only Plan Template" skills/implementaudit/templates/read-only-plan.md >/dev/null

negative_output="$(mktemp)"
trap 'rm -f "$negative_output"' EXIT

if bash scripts/check-plan-quality-contract.sh \
  --read-only-status-file fixtures/read-only-plans/negative-read-only-source-mutation.status \
  >"$negative_output" 2>&1; then
  cat "$negative_output" >&2
  printf 'read-only-plans-lane.test: read-only source mutation fixture unexpectedly passed\n' >&2
  exit 1
fi

grep -F "read-only lane source mutation outside allowlist" "$negative_output" >/dev/null

if bash scripts/check-plan-quality-contract.sh \
  --file fixtures/secret-hygiene/negative-plan-reproduces-fake-secret.md \
  >"$negative_output" 2>&1; then
  cat "$negative_output" >&2
  printf 'read-only-plans-lane.test: fake-secret reproduction fixture unexpectedly passed\n' >&2
  exit 1
fi

grep -F "plan reproduces fake secret value" "$negative_output" >/dev/null

printf 'read-only-plans-lane.test: ok\n'
