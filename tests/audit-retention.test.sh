#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-audit-retention.sh

if bash scripts/check-audit-retention.sh \
  --retention-file fixtures/audit-retention/negative-missing-artifact-boundary.md \
  >/tmp/audit-retention-policy.out 2>&1; then
  printf 'audit-retention.test: incomplete retention policy unexpectedly passed\n' >&2
  exit 1
fi
grep -F "missing retention token" /tmp/audit-retention-policy.out >/dev/null || {
  printf 'audit-retention.test: expected retention token diagnostic\n' >&2
  cat /tmp/audit-retention-policy.out >&2
  exit 1
}

if bash scripts/check-audit-retention.sh \
  --stale-ref-file fixtures/audit-retention/negative-stale-root-reference.md \
  >/tmp/audit-retention-stale.out 2>&1; then
  printf 'audit-retention.test: stale root reference unexpectedly passed\n' >&2
  exit 1
fi
grep -F "stale active root audit reference" /tmp/audit-retention-stale.out >/dev/null || {
  printf 'audit-retention.test: expected stale-reference diagnostic\n' >&2
  cat /tmp/audit-retention-stale.out >&2
  exit 1
}

cat >"$tmp/bad-run-root.md" <<'BAD'
# Bad proof wording

The run passed because `.IMPLEMENTAUDIT/runs/demo` exists.
BAD
if bash scripts/check-audit-retention.sh \
  --stale-ref-file "$tmp/bad-run-root.md" \
  >/tmp/audit-retention-run-root.out 2>&1; then
  printf 'audit-retention.test: stale run-root claim unexpectedly passed\n' >&2
  exit 1
fi
grep -F "run-root proof claim must be labelled" /tmp/audit-retention-run-root.out >/dev/null || {
  printf 'audit-retention.test: expected run-root claim diagnostic\n' >&2
  cat /tmp/audit-retention-run-root.out >&2
  exit 1
}

printf 'audit-retention.test: ok\n'
