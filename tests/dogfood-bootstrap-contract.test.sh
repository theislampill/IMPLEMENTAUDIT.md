#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-dogfood-bootstrap-contract.sh

cat >"$tmp/skill-missing-bootstrap.md" <<'BAD'
# /implementaudit

This synthetic skill fixture intentionally omits the dogfood bootstrap section.
BAD

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --skill-file "$tmp/skill-missing-bootstrap.md" \
  >/tmp/dogfood-bootstrap.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: missing bootstrap unexpectedly passed\n' >&2
  exit 1
fi

grep -F "missing ## Dogfood Bootstrap / Read Map" /tmp/dogfood-bootstrap.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected missing-bootstrap diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/installed-readback-before-baseline-transcript.jsonl \
  >/tmp/dogfood-bootstrap-transcript.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: readback-before-baseline transcript unexpectedly passed\n' >&2
  exit 1
fi

grep -F "installed skill readback occurred before baseline" /tmp/dogfood-bootstrap-transcript.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected transcript-order diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-transcript.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/chunking-readback-before-baseline-transcript.jsonl \
  >/tmp/dogfood-bootstrap-chunking.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: chunking-readback transcript unexpectedly passed\n' >&2
  exit 1
fi

grep -F "installed skill readback occurred before baseline" /tmp/dogfood-bootstrap-chunking.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected chunking-readback diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-chunking.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/real-home-readback-before-temp-home-transcript.jsonl \
  >/tmp/dogfood-bootstrap-real-home.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: real-home-readback transcript unexpectedly passed\n' >&2
  exit 1
fi

grep -F "real-home skill readback occurred before temp CODEX_HOME install path" /tmp/dogfood-bootstrap-real-home.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected real-home contamination diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-real-home.out >&2
  exit 1
}

printf 'dogfood-bootstrap-contract.test: ok\n'
