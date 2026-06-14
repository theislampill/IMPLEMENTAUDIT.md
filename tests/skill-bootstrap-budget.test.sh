#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-skill-bootstrap-budget.sh

if bash scripts/check-skill-bootstrap-budget.sh \
  --skill-file fixtures/skill-bootstrap-budget/negative-full-read-installed-payload.md \
  --max-lines 450 \
  --max-bytes 22000 \
  >"$tmp/negative.out" 2>&1; then
  printf 'skill-bootstrap-budget.test: negative installed-payload fixture unexpectedly passed\n' >&2
  exit 1
fi

grep -F "forbidden installed-payload readback instruction" "$tmp/negative.out" >/dev/null || {
  printf 'skill-bootstrap-budget.test: expected installed-payload readback diagnostic\n' >&2
  cat "$tmp/negative.out" >&2
  exit 1
}

cp skills/implementaudit/SKILL.md "$tmp/oversized.md"
for _ in $(seq 1 500); do
  printf 'padding line for budget regression\n' >>"$tmp/oversized.md"
done

if bash scripts/check-skill-bootstrap-budget.sh \
  --skill-file "$tmp/oversized.md" \
  --max-lines 450 \
  --max-bytes 22000 \
  >"$tmp/oversized.out" 2>&1; then
  printf 'skill-bootstrap-budget.test: oversized fixture unexpectedly passed\n' >&2
  exit 1
fi

grep -F "bootloader too long" "$tmp/oversized.out" >/dev/null || {
  printf 'skill-bootstrap-budget.test: expected size budget diagnostic\n' >&2
  cat "$tmp/oversized.out" >&2
  exit 1
}

printf 'skill-bootstrap-budget.test: ok\n'
