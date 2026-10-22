#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'durable-identity-contract.test: %s\n' "$*" >&2
  exit 1
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

registry="skills/implementaudit/references/identity-namespaces.json"
resolver="skills/implementaudit/scripts/resolve-durable-identity.py"
checker="scripts/check-durable-identities.py"

[ -f "$registry" ] || fail "missing canonical namespace registry"
[ -f "$resolver" ] || fail "missing packaged durable-identity resolver"
[ -f "$checker" ] || fail "missing maintained-source identity checker"

"${py_cmd[@]}" "$resolver" --validate

assert_eq() {
  local expected="$1"; shift
  local observed
  observed="$("${py_cmd[@]}" "$resolver" "$@")" || fail "resolver failed: $*"
  [ "$observed" = "$expected" ] || fail "$*: expected $expected, got $observed"
}

assert_eq R0001 --canonical R01
assert_eq R000A --canonical R10
assert_eq R001C --canonical R28
assert_eq R0032 --canonical R50
assert_eq R0037 --canonical R55
assert_eq G003D --canonical e61
assert_eq G003E --canonical e62
assert_eq G003F --canonical e63
assert_eq G0040 --canonical e64
assert_eq R28 --legacy R001C
assert_eq e61 --legacy G003D
assert_eq 28 --ordinal R001C
assert_eq 40 --ordinal R0028
assert_eq R0038 --format R 56

for invalid in R1 r28 R000a R00001 G040 e0 X0001; do
  if "${py_cmd[@]}" "$resolver" --canonical "$invalid" >/dev/null 2>&1; then
    fail "malformed identity accepted: $invalid"
  fi
done

assert_eq R0037 --require-allocated R0037
assert_eq R0038 --require-allocated R0038
assert_eq R0039 --require-allocated R0039
assert_eq R003A --require-allocated R003A
if "${py_cmd[@]}" "$resolver" --require-allocated R003B >/dev/null 2>&1; then
  fail "the next unreserved Rockstar was silently allocated"
fi

for canonical_born in R0038 R0039 R003A; do
  if "${py_cmd[@]}" "$resolver" --legacy "$canonical_born" >/dev/null 2>&1; then
    fail "canonical-born Rockstar gained a fabricated legacy alias: $canonical_born"
  fi
done

"${py_cmd[@]}" - "$resolver" <<'PY'
import subprocess
import sys

resolver = sys.argv[1]
seen = {}
for ordinal in range(1, 56):
    alias = f"R{ordinal:02d}"
    expected = f"R{ordinal:04X}"
    canonical = subprocess.check_output(
        [sys.executable, resolver, "--canonical", alias], text=True
    ).strip()
    if canonical != expected:
        raise SystemExit(f"wrong mapping: {alias} -> {canonical}, expected {expected}")
    if canonical in seen:
        raise SystemExit(f"duplicate canonical identity: {canonical}")
    seen[canonical] = alias
    reverse = subprocess.check_output(
        [sys.executable, resolver, "--legacy", canonical], text=True
    ).strip()
    if reverse != alias:
        raise SystemExit(f"wrong reverse mapping: {canonical} -> {reverse}")
if len(seen) != 55:
    raise SystemExit("Rockstar bijection lost or minted an identity")
PY

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git -C "$tmp" init -q
git -C "$tmp" config user.email identity-test@example.invalid
git -C "$tmp" config user.name identity-test
mkdir -p "$tmp/docs/audits/archive" "$tmp/docs"
printf '%s\n' 'Current owner R001C.' > "$tmp/README.md"
printf '%s\n' 'Legacy alias R28 maps to canonical R001C.' > "$tmp/docs/identity.md"
printf '%s\n' 'Historical R28 wording remains immutable.' > "$tmp/docs/audits/archive/legacy.md"
mkdir -p "$tmp/tests"
printf '%s\n' 'Fixture labels R35-F1, DOG-R01-combined-cell-timeout, and R36_TEST_GATE remain local identifiers.' > "$tmp/tests/local-labels.txt"
git -C "$tmp" add README.md docs tests
"${py_cmd[@]}" "$checker" --scan-root "$tmp" >/dev/null

printf '%s\n' 'Current owner R28.' > "$tmp/README.md"
if "${py_cmd[@]}" "$checker" --scan-root "$tmp" >/dev/null 2>&1; then
  fail "unmarked maintained legacy Rockstar spelling was accepted"
fi

printf '%s\n' 'Current owner R001C.' > "$tmp/README.md"
mkdir -p "$tmp/docs/R28"
printf '%s\n' 'current path owner' > "$tmp/docs/R28/index.md"
git -C "$tmp" add README.md docs/R28/index.md
if "${py_cmd[@]}" "$checker" --scan-root "$tmp" >/dev/null 2>&1; then
  fail "bare maintained legacy Rockstar path segment was accepted"
fi

"${py_cmd[@]}" "$checker"

printf 'durable-identity-contract.test: ok\n'
