#!/usr/bin/env bash
set -euo pipefail

# Proof-level claim-boundary test (#53, IA-PROOF-LEVELS): the taxonomy is
# defined, active surfaces are qualified, and the extended checker fails
# unqualified verdict-class wording on active surfaces (embedded negative
# controls via a trap-removed probe file).

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'claim-boundary-proof-levels.test: %s\n' "$*" >&2
  exit 1
}

probe="docs/claim-probe-proof-levels.md"
cleanup() { rm -f "$probe"; }
trap cleanup EXIT

require() {
  local file="$1"
  local text="$2"
  grep -Fqi -e "$text" "$file" || fail "missing in $file: $text"
}

# 1. Taxonomy defined with all seven levels.
ret="docs/audits/RETENTION.md"
require "$ret" "Proof-Level Taxonomy (PL1-PL7)"
require "$ret" "prose presence"
require "$ret" "authoritative runtime instruction"
require "$ret" "template requirement"
require "$ret" "structural validation"
require "$ret" "fixture/example/transcript demonstration"
require "$ret" "observed live behavior"
require "$ret" "fresh-executor proof"
require "$ret" "composes with the per-command evidence properties"
require "$ret" "never rewritten"

# 2. Active index qualifies the surfaced archived verdicts.
idx="docs/audits/INDEX.md"
require "$idx" "Archived Proof Ledgers (qualified"
require "$idx" "not PL6 behaviorally observed"

# 3. Final-report template carries claim rows composed with command properties.
frt="skills/implementaudit/templates/final-report.md"
require "$frt" "Claim Rows (proof-level discipline)"
require "$frt" "| Claim | Scope | Proof level | Evidence basis | Freshness | Upgrade condition |"
require "$frt" "structural"
require "$frt" "provenance"

# 4. Positive fixture passes as an active surface (checker green on live tree).
[ -f fixtures/claim-boundaries/allowed-proof-wording.md ] \
  || fail "missing allowed-proof-wording fixture"
bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1 \
  || fail "checker fails on the live tree (positive fixture should be legal)"

# 5. Negative control: unqualified verdict wording on an active surface fails.
printf 'Capability parity is PROVEN.\n' >"$probe"
out="/tmp/claim-proof-levels-neg1.out"
if bash scripts/check-public-claim-boundaries.sh >"$out" 2>&1; then
  fail "unqualified PROVEN on an active surface unexpectedly passed"
fi
grep -Fq "proof-level qualification" "$out" \
  || { cat "$out" >&2; fail "expected proof-level diagnostic"; }
rm -f "$probe"

# 6. Negative control: active summary quoting an archived verdict bare fails.
printf 'Per the archived rerun audit, the capability set is SURPASSED and settled.\n' >"$probe"
if bash scripts/check-public-claim-boundaries.sh >"$out" 2>&1; then
  fail "bare archived-verdict quote on an active surface unexpectedly passed"
fi
grep -Fq "proof-level qualification" "$out" \
  || { cat "$out" >&2; fail "expected proof-level diagnostic"; }
rm -f "$probe"

# 7. Qualified and negated wording stays legal on active surfaces.
printf 'The milestone is PROVEN [proof level: PL4 structural validation; not PL6/PL7].\n' >"$probe"
bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1 \
  || fail "qualified verdict wording unexpectedly failed"
printf 'This capability is not PROVEN and must not be described as such.\n' >"$probe"
bash scripts/check-public-claim-boundaries.sh >/dev/null 2>&1 \
  || fail "negated verdict wording unexpectedly failed"
rm -f "$probe" "$out"

# 8. Negative fixtures exist and declare their failing disposition.
for negative in \
  fixtures/claim-boundaries/negative-unqualified-proven.md \
  fixtures/claim-boundaries/negative-archived-verdict-unqualified.md
do
  require "$negative" "NEGATIVE FIXTURE"
  require "$negative" "must fail"
  require "$negative" "Expected disposition when checked: FAIL"
done

printf 'claim-boundary-proof-levels.test: ok\n'
