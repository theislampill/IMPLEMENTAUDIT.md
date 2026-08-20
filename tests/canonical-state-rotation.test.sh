#!/usr/bin/env bash
# R0039 F1 is an immutable, nonmergeable semantic RED checkpoint.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/scripts/check-canonical-state-rotation.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() { printf 'canonical-state-rotation.test: %s\n' "$*" >&2; exit 2; }

[ -f "$checker" ] || fail "missing root checker: $checker"
bash -n "$checker" || fail "checker syntax is invalid"
bash "$checker" --fixture-self-check
bash "$checker" --assert-root-red

before_refs="$(git -C "$repo_root" for-each-ref --format='%(refname) %(objectname)' \
  refs/implementaudit/current-generations/ \
  refs/implementaudit/current-generation-migrations/ \
  refs/implementaudit/state-archives/)"

set +e
bash "$checker" >"$tmp/root-red.out" 2>&1
root_rc=$?
set -e
[ "$root_rc" -eq 1 ] || fail "root-only oracle exited $root_rc instead of semantic RED 1"

grep -Fq 'CANONICAL_STATE_ROTATION_RED=ROOT_ONLY_NOT_EQUIVALENT' "$tmp/root-red.out" \
  || fail 'root-only failure did not identify semantic non-equivalence'
grep -Fq 'preserved-payload=49/49' "$tmp/root-red.out" \
  || fail 'root-only RED did not prove preserved payload stayed complete'
grep -Fq 'missing-equivalence=transition,pointer+marker+v3,archive,rehydration' "$tmp/root-red.out" \
  || fail 'root-only RED did not name the missing semantic joins'
for anchor in \
  'M01-generation-successor:semantic-mutation' \
  'D05-pointer-ref:semantic-mutation' \
  'D23-rehydrate-identity:semantic-mutation' \
  'A01-state-preimage:semantic-mutation'; do
  grep -Fq "$anchor" "$tmp/root-red.out" || fail "root-only RED omitted anchor $anchor"
done

after_refs="$(git -C "$repo_root" for-each-ref --format='%(refname) %(objectname)' \
  refs/implementaudit/current-generations/ \
  refs/implementaudit/current-generation-migrations/ \
  refs/implementaudit/state-archives/)"
[ "$before_refs" = "$after_refs" ] || fail 'RED oracle mutated a protected Git-ref namespace'

cat "$tmp/root-red.out" >&2
printf '%s\n' \
  'canonical-state-rotation.test: INTENDED_RED root-only current state cannot satisfy deterministic rotation equivalence' >&2
exit 1
