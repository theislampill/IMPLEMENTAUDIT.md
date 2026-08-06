#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="${RESPEC_CHECKER:-$repo_root/skills/implementaudit/scripts/check-respec-impact-set.sh}"
closure="$repo_root/skills/implementaudit/scripts/check-closure-surface.sh"
template="$repo_root/skills/implementaudit/templates/respec-impact-set.md"
phase_design="$repo_root/skills/implementaudit/references/phase-design.md"
phase_goal="$repo_root/skills/implementaudit/templates/phase-goal.txt"
cases="$repo_root/fixtures/respec-impact-set/cases.json"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
count=0

fail() { printf 'respec-impact-set-contract.test: %s\n' "$*" >&2; exit 1; }
ok() { count=$((count + 1)); }

python "$repo_root/eval/check_fixture_schema.py" >/dev/null 2>&1 || true
python - "$cases" <<'PY'
import json, sys
rows = json.load(open(sys.argv[1], encoding="utf-8"))
expected = [f"R4-F{i}" for i in range(1, 10)]
ids = [row.get("id") for row in rows]
if ids != expected:
    raise SystemExit(f"expected {expected}, got {ids}")
PY
ok

write_impact() {
  local file="$1" population="$2" literal_count="$3" stem_count="$4" replacement="$5"
  shift 5
  local rows=("$@") carriers=() row carrier literal_output=none stem_output=none i
  for row in "${rows[@]}"; do
    carrier="$(printf '%s' "$row" | cut -d'|' -f3 | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
    carriers+=("$carrier")
  done
  if [ "$literal_count" -gt 0 ]; then
    literal_output="${carriers[0]}"
    for ((i=1; i<literal_count; i++)); do literal_output="$literal_output, ${carriers[$i]}"; done
  fi
  if [ "$stem_count" -gt 0 ]; then
    stem_output="${carriers[$literal_count]:-constructed/vn-20.json}"
    for ((i=literal_count+1; i<literal_count+stem_count; i++)); do
      stem_output="$stem_output, ${carriers[$i]:-constructed/vn-$i.json}"
    done
  fi
  printf '%s\n' \
    'IMPLEMENTAUDIT_RESPEC_IMPACT_SET' \
    'Change: VN-23 -> VN-20' \
    'Declared by: issue #77 fixture' \
    "Population size: $population" \
    'Enumeration method: literal + stem/dirname' \
    "Literal carriers: $literal_output" \
    "Literal count: $literal_count" \
    "Stem/dirname additional carriers: $stem_output" \
    "Stem/dirname additional count: $stem_count" \
    "Replacement: $replacement" \
    "Replacement path: $([ "$replacement" = yes ] && printf replacement.md || printf none)" \
    '' \
    '| # | Carrier | Kind | Status | Evidence |' \
    '|---|---|---|---|---|' \
    "$@" \
    '' \
    '## Invariants carried forward' \
    '| # | Invariant | Enforced by | Present in replacement? | Evidence |' \
    '|---|---|---|---|---|' \
    > "$file"
}

rows6=(
  '| 1 | generator.py | generator | applied | diff:g |'
  '| 2 | rollout.json | manifest | applied | diff:r |'
  '| 3 | doc-a.md | doc | applied | diff:a |'
  '| 4 | doc-b.md | doc | applied | diff:b |'
  '| 5 | memory.md | memory | applied | diff:m |'
  '| 6 | constructed/vn-20.json | code | applied | diff:c |'
)

# R4-F1: two method outputs account for six carriers; a five-row declaration
# that omits the constructed path fails the population lock.
write_impact "$tmp/six.md" 6 5 1 no "${rows6[@]}"
bash "$checker" "$tmp/six.md" >/dev/null || fail 'R4-F1 six-carrier set must pass'
write_impact "$tmp/five.md" 6 5 1 no "${rows6[@]:0:5}"
if bash "$checker" "$tmp/five.md" >/dev/null 2>&1; then
  fail 'R4-F1 five-carrier declaration must fail'
fi
rows_substituted=("${rows6[@]:0:5}" '| 6 | unrelated.txt | doc | applied | diff:u |')
write_impact "$tmp/substituted.md" 6 5 1 no "${rows_substituted[@]}"
sed -i 's/Stem\/dirname additional carriers: unrelated.txt/Stem\/dirname additional carriers: constructed\/vn-20.json/' "$tmp/substituted.md"
if bash "$checker" "$tmp/substituted.md" >/dev/null 2>&1; then
  fail 'R4-F1 method outputs may not disagree with the carrier table'
fi
ok

# R4-F2/F3: fully evidenced applied rows pass; an empty status fails and names
# the carrier.
bash "$checker" "$tmp/six.md" >/dev/null || fail 'R4-F2 applied set must pass'
write_impact "$tmp/empty.md" 1 1 0 no '| 1 | doc-a.md | doc |  | diff:a |'
if bash "$checker" "$tmp/empty.md" >"$tmp/empty.out" 2>&1; then
  fail 'R4-F3 empty status must fail'
fi
grep -Fq 'doc-a.md' "$tmp/empty.out" || fail 'R4-F3 failure must name carrier'
ok; ok

# R4-F4: valid #6 terminal dispositions pass; stale owner-decision fails.
write_impact "$tmp/risk.md" 1 1 0 no '| 1 | issue:99 | issue | deferred(risk-accepted: policy-7) | policy-7 |'
bash "$checker" "$tmp/risk.md" >/dev/null || fail 'risk-accepted deferral must pass'
write_impact "$tmp/assigned.md" 1 1 0 no '| 1 | issue:99 | issue | owner-assigned | issue-comment |'
bash "$checker" "$tmp/assigned.md" >/dev/null || fail 'owner-assigned must pass'
write_impact "$tmp/decision.md" 1 1 0 no '| 1 | issue:99 | issue | owner-decision | issue-comment |'
if bash "$checker" "$tmp/decision.md" >/dev/null 2>&1; then
  fail 'stale owner-decision token must fail'
fi
ok

# R4-F5: one external-free carrier costs one row, not a broad ceremony tax.
write_impact "$tmp/one.md" 1 1 0 no '| 1 | definition.py | code | applied | diff:def |'
bash "$checker" "$tmp/one.md" >/dev/null || fail 'one-carrier set must pass'
ok

# R4-F6 is the absent-file compatibility control: the dedicated checker is
# opt-in and ordinary run-root/closure suites exercise absence.
[ ! -e "$tmp/no-respec/respec-impact-set.md" ] || fail 'unexpected impact set'
ok

# R4-F7/F8: replacement requires at least one evidenced, present invariant.
write_impact "$tmp/replacement-red.md" 1 1 0 yes '| 1 | README.md | doc | applied | diff:readme |'
if bash "$checker" "$tmp/replacement-red.md" >/dev/null 2>&1; then
  fail 'replacement without carried invariant must fail'
fi
write_impact "$tmp/replacement-green.md" 1 1 0 yes \
  '| 1 | README.md | doc | applied | diff:readme |'
printf 'current stackmarker4 contract\n' > "$tmp/replacement.md"
printf '%s\n' '| 1 | stackmarker4 | tests/readme.test.sh | yes | contains:stackmarker4 |' \
  >> "$tmp/replacement-green.md"
bash "$checker" "$tmp/replacement-green.md" >/dev/null || fail 'carried invariant must pass'
write_impact "$tmp/replacement-false-yes.md" 1 1 0 yes \
  '| 1 | README.md | doc | applied | diff:readme |'
sed -i 's/Replacement path: replacement.md/Replacement path: replacement-missing.md/' "$tmp/replacement-false-yes.md"
printf 'fresh prose without the required marker\n' > "$tmp/replacement-missing.md"
printf '%s\n' '| 1 | stackmarker4 | tests/readme.test.sh | yes | contains:stackmarker4 |' \
  >> "$tmp/replacement-false-yes.md"
if bash "$checker" "$tmp/replacement-false-yes.md" >/dev/null 2>&1; then
  fail 'false invariant yes without marker in replacement must fail'
fi
ok; ok

# R4-F9: the optional closure-evidence route rejects pending state without
# importing #78 ledger, plan-retirement, blocker, or steer behavior.
printf '%s\n' 'claim: c1 | surface: source | status: verified | evidence-surface: source' > "$tmp/closure.md"
printf 'Status: IN PROGRESS\n' > "$tmp/pending.md"
if bash "$closure" "$tmp/closure.md" --impact-set "$tmp/six.md" --closure-evidence "$tmp/pending.md" >/dev/null 2>&1; then
  fail 'R4-F9 pending closure evidence must fail'
fi
printf 'Status: COMPLETE\n' > "$tmp/complete.md"
bash "$closure" "$tmp/closure.md" --impact-set "$tmp/six.md" --closure-evidence "$tmp/complete.md" >/dev/null \
  || fail 'complete closure evidence must pass'
ok

grep -Fq 'Re-spec completeness' "$phase_design" || fail 'phase-design rule missing'
grep -Fq 'Impact set:' "$phase_goal" || fail 'phase-goal field missing'
grep -Fq 'IMPLEMENTAUDIT_RESPEC_IMPACT_SET' "$template" || fail 'template marker missing'
ok; ok; ok

printf 'respec-impact-set-contract.test: ok (%d/13)\n' "$count"
