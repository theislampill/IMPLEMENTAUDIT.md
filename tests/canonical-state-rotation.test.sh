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
fixture_output="$(bash "$checker" --fixture-self-check)"
printf '%s\n' "$fixture_output"
grep -Fq 'denominator=110 omission=110 mutation=110 owner-mutation=110 root-semantic-red=56' <<<"$fixture_output" \
  || fail 'protected denominator is not the exact reviewed four-part population'
grep -Fq 'partitions={"ARCHIVED_ONLY_HISTORY":14,"DERIVED_BINDINGS":29,"MONOTONIC_TRANSITION":18,"PRESERVED_PAYLOAD":49}' <<<"$fixture_output" \
  || fail 'protected denominator is not exactly four-part'
if grep -Fq 'TRIGGER_CALIBRATION' <<<"$fixture_output"; then
  fail 'trigger/calibration leaked into the protected-state partitions'
fi
trigger_output="$(bash "$checker" --trigger-self-check)"
printf '%s\n' "$trigger_output"
grep -Fq 'CANONICAL_STATE_ROTATION_TRIGGER_SELF_CHECK=PASS' <<<"$trigger_output" \
  || fail 'trigger/calibration self-check did not pass'
grep -Fq 'large-root=TRIGGER below-threshold=NO_TRIGGER archive=0 model=0 extra-ceremony=0' <<<"$trigger_output" \
  || fail 'trigger self-check did not preserve the positive and cheap-path outcomes'
grep -Fq 'population-sha256=b3df1ff07d18f8f5de145cf6d10f48a15f0a0416b392d0ca84567dce6d23e497 digest-mutations=55/55' <<<"$trigger_output" \
  || fail 'trigger self-check did not prove canonical population digest mutation coverage'
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
