#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-safeguard-restoration.sh

if bash scripts/check-safeguard-restoration.sh \
  --final-report fixtures/safeguards/negative-missing-final-report.md \
  >"$tmp/missing-final.out" 2>&1; then
  printf 'safeguard-restoration.test: missing final report fixture unexpectedly passed\n' >&2
  exit 1
fi
grep -F "missing required substance" "$tmp/missing-final.out" >/dev/null || {
  printf 'safeguard-restoration.test: expected missing final-report diagnostic\n' >&2
  cat "$tmp/missing-final.out" >&2
  exit 1
}

if bash scripts/check-safeguard-restoration.sh \
  --lean-ref fixtures/safeguards/negative-missing-5whys-exit.md \
  >"$tmp/missing-5whys.out" 2>&1; then
  printf 'safeguard-restoration.test: missing 5-Whys fixture unexpectedly passed\n' >&2
  exit 1
fi
grep -F "5 Whys Loop-Exit Protocol" "$tmp/missing-5whys.out" >/dev/null || {
  printf 'safeguard-restoration.test: expected 5-Whys diagnostic\n' >&2
  cat "$tmp/missing-5whys.out" >&2
  exit 1
}

if bash scripts/check-safeguard-restoration.sh \
  --source-label-file fixtures/safeguards/negative-unlabeled-source-only-checker.md \
  >"$tmp/source-label.out" 2>&1; then
  printf 'safeguard-restoration.test: unlabeled source-only fixture unexpectedly passed\n' >&2
  exit 1
fi
grep -F "source-only checker reference lacks label" "$tmp/source-label.out" >/dev/null || {
  printf 'safeguard-restoration.test: expected source-only label diagnostic\n' >&2
  cat "$tmp/source-label.out" >&2
  exit 1
}

printf 'safeguard-restoration.test: ok\n'
