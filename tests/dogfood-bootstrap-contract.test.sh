#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-dogfood-bootstrap-contract.sh

if ! bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/positive/host-activation-before-baseline-transcript.jsonl \
  >/tmp/dogfood-bootstrap-host-activation.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: qualified host activation before runner baseline was rejected\n' >&2
  cat /tmp/dogfood-bootstrap-host-activation.out >&2
  exit 1
fi

if ! bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/positive/similarly-named-path-before-baseline-transcript.jsonl \
  >"$tmp/similar-path.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: similarly named non-root path was treated as installed payload\n' >&2
  cat "$tmp/similar-path.out" >&2
  exit 1
fi

if ! bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/positive/echo-installed-path-before-baseline-transcript.jsonl \
  >"$tmp/echo-path.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: harmless path echo was treated as installed payload readback\n' >&2
  cat "$tmp/echo-path.out" >&2
  exit 1
fi

if ! bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/positive/rg-pattern-installed-path-before-baseline-transcript.jsonl \
  >"$tmp/rg-pattern.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: rg search pattern was treated as a filesystem read target\n' >&2
  cat "$tmp/rg-pattern.out" >&2
  exit 1
fi

for baseline_case in \
  status-only-before-readback-transcript.jsonl \
  failed-baseline-before-readback-transcript.jsonl
do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --transcript-file "fixtures/dogfood-bootstrap/negative/$baseline_case" \
    >"$tmp/$baseline_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: incomplete or failed baseline unexpectedly passed: %s\n' "$baseline_case" >&2
    exit 1
  fi

  grep -F "missing successful baseline command completion" "$tmp/$baseline_case.out" >/dev/null || {
    printf 'dogfood-bootstrap-contract.test: expected successful-baseline diagnostic: %s\n' "$baseline_case" >&2
    cat "$tmp/$baseline_case.out" >&2
    exit 1
  }
done

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/narrated-temp-home-before-real-home-activation-transcript.jsonl \
  >"$tmp/narrated-temp-home.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: narrated temp-home token laundered real-home activation\n' >&2
  exit 1
fi

grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" "$tmp/narrated-temp-home.out" >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected structured temp-home evidence diagnostic\n' >&2
  cat "$tmp/narrated-temp-home.out" >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/uppercase-windows-readback-before-baseline-transcript.jsonl \
  >"$tmp/uppercase-readback.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: uppercase Windows readback bypassed baseline order\n' >&2
  exit 1
fi

grep -F "installed skill readback occurred before baseline" "$tmp/uppercase-readback.out" >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected casefolded readback diagnostic\n' >&2
  cat "$tmp/uppercase-readback.out" >&2
  exit 1
}

for payload_case in \
  bash-lc-installed-readback-before-baseline-transcript.jsonl \
  tight-pwsh-scriptblock-installed-readback-before-baseline-transcript.jsonl \
  env-prefixed-installed-readback-before-baseline-transcript.jsonl \
  rg-attached-pattern-installed-target-before-baseline-transcript.jsonl \
  rg-files-installed-root-before-baseline-transcript.jsonl \
  grep-recursive-installed-target-before-baseline-transcript.jsonl \
  select-string-explicit-pattern-installed-target-before-baseline-transcript.jsonl \
  installed-reference-before-baseline-transcript.jsonl \
  powershell-wrapped-installed-readback-before-baseline-transcript.jsonl \
  powershell-scriptblock-installed-readback-before-baseline-transcript.jsonl \
  compound-installed-readback-before-baseline-transcript.jsonl \
  posix-absolute-installed-readback-before-baseline-transcript.jsonl \
  rg-text-mode-installed-target-before-baseline-transcript.jsonl \
  mixed-separator-readback-before-baseline-transcript.jsonl \
  dot-segment-installed-readback-before-baseline-transcript.jsonl \
  dotdot-segment-installed-readback-before-baseline-transcript.jsonl \
  installed-root-listing-before-baseline-transcript.jsonl
do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --transcript-file "fixtures/dogfood-bootstrap/negative/$payload_case" \
    >"$tmp/$payload_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: installed payload path unexpectedly passed: %s\n' "$payload_case" >&2
    exit 1
  fi

  grep -F "installed skill readback occurred before baseline" "$tmp/$payload_case.out" >/dev/null || {
    printf 'dogfood-bootstrap-contract.test: expected installed-root readback diagnostic: %s\n' "$payload_case" >&2
    cat "$tmp/$payload_case.out" >&2
    exit 1
  }
done

for real_home_case in \
  host-purpose-temp-launders-real-home-transcript.jsonl \
  spaced-profile-real-home-activation-transcript.jsonl
do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --transcript-file "fixtures/dogfood-bootstrap/negative/$real_home_case" \
    >"$tmp/$real_home_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: real-home field/path held-out unexpectedly passed: %s\n' "$real_home_case" >&2
    exit 1
  fi

  grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" "$tmp/$real_home_case.out" >/dev/null || {
    printf 'dogfood-bootstrap-contract.test: expected field-scoped real-home diagnostic: %s\n' "$real_home_case" >&2
    cat "$tmp/$real_home_case.out" >&2
    exit 1
  }
done

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

grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" /tmp/dogfood-bootstrap-real-home.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected real-home contamination diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-real-home.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/real-home-readback-generic-user-before-temp-home-transcript.jsonl \
  >/tmp/dogfood-bootstrap-real-home-generic.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: generic-user real-home transcript unexpectedly passed\n' >&2
  exit 1
fi

grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" /tmp/dogfood-bootstrap-real-home-generic.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected generic-user real-home contamination diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-real-home-generic.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/real-home-host-activation-generic-user-transcript.jsonl \
  >/tmp/dogfood-bootstrap-real-home-host.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: generic-user real-home host activation unexpectedly passed\n' >&2
  exit 1
fi

grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" /tmp/dogfood-bootstrap-real-home-host.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected real-home host-activation diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-real-home-host.out >&2
  exit 1
}

printf 'dogfood-bootstrap-contract.test: ok\n'
