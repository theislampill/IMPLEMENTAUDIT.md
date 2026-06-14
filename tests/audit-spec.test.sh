#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash skills/implementaudit/scripts/validate-audit-spec.sh fixtures/audit-spec/valid-mixed.md

for invalid in \
  fixtures/audit-spec/invalid-missing-owner.md \
  fixtures/audit-spec/invalid-missing-rollback.md \
  fixtures/audit-spec/invalid-missing-evidence.md \
  fixtures/audit-spec/invalid-missing-generated-plan.md \
  fixtures/audit-spec/invalid-missing-release-boundary.md
do
  if bash skills/implementaudit/scripts/validate-audit-spec.sh "$invalid" >/dev/null 2>&1; then
    printf 'audit-spec.test: expected invalid fixture to fail: %s\n' "$invalid" >&2
    exit 1
  fi
done

printf 'audit-spec.test: ok\n'
