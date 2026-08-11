#!/usr/bin/env bash
# phase-validation.test.sh — comprehensive test for validate-phase.sh
#
# Covers all required failure modes plus a valid full-spec fixture.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'phase-validation.test: Python is required\n' >&2
  exit 1
fi

pass=0
fail=0

check_pass() {
  local label="$1"
  local file="$2"
  if bash skills/implementaudit/scripts/validate-phase.sh "$file" >/dev/null 2>&1; then
    pass=$((pass + 1))
  else
    printf 'phase-validation.test: UNEXPECTED FAIL for: %s\n' "$label" >&2
    fail=$((fail + 1))
  fi
}

check_fail() {
  local label="$1"
  local file="$2"
  if bash skills/implementaudit/scripts/validate-phase.sh "$file" >/dev/null 2>&1; then
    printf 'phase-validation.test: UNEXPECTED PASS for: %s\n' "$label" >&2
    fail=$((fail + 1))
  else
    pass=$((pass + 1))
  fi
}

check_fail_contains() {
  local label="$1"
  local file="$2"
  local expected="$3"
  local out="$tmp/${label//[^A-Za-z0-9_]/_}.out"
  if bash skills/implementaudit/scripts/validate-phase.sh "$file" >"$out" 2>&1; then
    printf 'phase-validation.test: UNEXPECTED PASS for: %s\n' "$label" >&2
    fail=$((fail + 1))
  elif grep -Fq "$expected" "$out"; then
    pass=$((pass + 1))
  else
    printf 'phase-validation.test: WRONG FAILURE for: %s\n' "$label" >&2
    printf 'phase-validation.test: expected diagnostic: %s\n' "$expected" >&2
    cat "$out" >&2
    fail=$((fail + 1))
  fi
}

# ------------------------------------------------------------------
# Helper: build a valid spec in a temp file
# ------------------------------------------------------------------
make_valid() {
  local dest="$1"
  cp fixtures/phase-validation/valid-full-spec.md "$dest"
}

# ------------------------------------------------------------------
# PASS: valid full spec fixture
# (The phase-goal.txt template contains placeholder content by design
#  and is not a filled-in spec; only validate filled-in fixtures.)
# ------------------------------------------------------------------
check_pass "valid-full-spec fixture" fixtures/phase-validation/valid-full-spec.md

# ------------------------------------------------------------------
# Unit independence and ceremony proportionality (#83)
# ------------------------------------------------------------------
f="$tmp/independent_units.md"
make_valid "$f"
sed -i '/^Depends on phases:/a unit_independence: independent\nchange_class: reversible-local-multi' "$f"
sed -i 's/^- Create src\//- Unit 1: Create src\//; s/^- Add tests\//- Unit 2: Add tests\//; s/^- Register route/- Unit 3: Register route/' "$f"
check_pass "three independent units with approved class" "$f"

f="$tmp/ordered_units.md"
make_valid "$f"
sed -i '/^Depends on phases:/a unit_independence: ordered(route registration depends on handler)\nchange_class: reversible-local-multi' "$f"
sed -i 's/^- Create src\//- Unit 1: Create src\//; s/^- Add tests\//- Unit 2: Add tests\//; s/^- Register route/- Unit 3: Register route/' "$f"
check_pass "ordered units carry a reason" "$f"

f="$tmp/independent_missing_declarations.md"
make_valid "$f"
sed -i 's/^- Create src\//- Unit 1: Create src\//; s/^- Add tests\//- Unit 2: Add tests\//; s/^- Register route/- Unit 3: Register route/' "$f"
check_fail_contains "new phase with three units needs declarations" "$f" \
  "3+ declared units require unit_independence and change_class"

f="$tmp/bad_independence.md"
make_valid "$f"
sed -i '/^Depends on phases:/a unit_independence: ordered\nchange_class: reversible-local-multi' "$f"
check_fail_contains "ordered declaration needs reason" "$f" \
  "unit_independence must be independent or ordered(<reason>)"

f="$tmp/bad_change_class.md"
make_valid "$f"
sed -i '/^Depends on phases:/a unit_independence: independent\nchange_class: low-risk' "$f"
check_fail_contains "change class must be approved" "$f" \
  "invalid change_class"

f="$tmp/class_laundering.md"
make_valid "$f"
sed -i '/^Depends on phases:/a unit_independence: independent\nchange_class: reversible-local' "$f"
sed -i '/^## Evidence required in transcript/i - gh release create v1.2.3 — property: provenance; scope: publishes an external release; expected: exit 0' "$f"
check_fail_contains "external mutation cannot be reversible-local" "$f" \
  "reversible-local cannot authorize external mutation commands"

f="$tmp/external_amortization.md"
make_valid "$f"
sed -i '/^Depends on phases:/a unit_independence: independent\nchange_class: irreversible-external' "$f"
sed -i '/^## Work/a - Unit 1: publish package A\n- Unit 2: publish package B\n- Unit 3: publish package C\n- Use one review per batch.' "$f"
check_fail_contains "irreversible external work cannot amortize ceremony" "$f" \
  "irreversible-external keeps full ceremony per unit"

f="$tmp/legacy_units.md"
make_valid "$f"
sed -i 's/^- Create src\//- Unit 1: Create src\//; s/^- Add tests\//- Unit 2: Add tests\//; s/^- Register route/- Unit 3: Register route/' "$f"
sed -i '/^## Implementation steps (ordered)$/,/^## Scope boundaries$/{/^## Scope boundaries$/!d}' "$f"
out="$tmp/legacy_units.out"
if bash skills/implementaudit/scripts/validate-phase.sh "$f" >"$out" 2>&1 \
    && grep -Fq "WARNING legacy spec" "$out" \
    && grep -Fq "unit declarations" "$out"; then
  pass=$((pass + 1))
else
  printf 'phase-validation.test: legacy unit declarations must pass WITH warning\n' >&2
  cat "$out" >&2
  fail=$((fail + 1))
fi

# ------------------------------------------------------------------
# FAIL: missing IMPLEMENTAUDIT_PHASE_START
# ------------------------------------------------------------------
f="$tmp/no_phase_start.md"
make_valid "$f"
sed -i 's/IMPLEMENTAUDIT_PHASE_START/REMOVED_MARKER/' "$f"
check_fail "missing IMPLEMENTAUDIT_PHASE_START" "$f"

# ------------------------------------------------------------------
# FAIL: missing IMPLEMENTAUDIT_PHASE_VERIFY
# ------------------------------------------------------------------
f="$tmp/no_phase_verify.md"
make_valid "$f"
sed -i 's/IMPLEMENTAUDIT_PHASE_VERIFY/REMOVED_MARKER/' "$f"
check_fail "missing IMPLEMENTAUDIT_PHASE_VERIFY" "$f"

# ------------------------------------------------------------------
# FAIL: missing AGENTS_UPDATE_DECISION
# ------------------------------------------------------------------
f="$tmp/no_agents.md"
make_valid "$f"
sed -i 's/AGENTS_UPDATE_DECISION/REMOVED_MARKER/' "$f"
check_fail "missing AGENTS_UPDATE_DECISION" "$f"

# ------------------------------------------------------------------
# FAIL: missing CONTINUITY_DECISION
# ------------------------------------------------------------------
f="$tmp/no_continuity.md"
make_valid "$f"
sed -i 's/CONTINUITY_DECISION/REMOVED_MARKER/' "$f"
check_fail "missing CONTINUITY_DECISION" "$f"

# ------------------------------------------------------------------
# FAIL: missing IMPLEMENTAUDIT_PHASE_DONE
# ------------------------------------------------------------------
f="$tmp/no_phase_done.md"
make_valid "$f"
sed -i 's/IMPLEMENTAUDIT_PHASE_DONE/REMOVED_MARKER/' "$f"
check_fail "missing IMPLEMENTAUDIT_PHASE_DONE" "$f"

# ------------------------------------------------------------------
# FAIL: missing Run root
# ------------------------------------------------------------------
f="$tmp/no_run_root.md"
make_valid "$f"
sed -i 's/^Run root:.*//' "$f"
check_fail "missing Run root" "$f"

# ------------------------------------------------------------------
# FAIL: missing Baseline ref
# ------------------------------------------------------------------
f="$tmp/no_baseline.md"
make_valid "$f"
sed -i 's/^Baseline ref:.*//' "$f"
check_fail "missing Baseline ref" "$f"

# ------------------------------------------------------------------
# FAIL: missing Owner/source
# ------------------------------------------------------------------
f="$tmp/no_owner.md"
make_valid "$f"
sed -i 's/^Owner\/source:.*//' "$f"
check_fail "missing Owner/source" "$f"

# ------------------------------------------------------------------
# FAIL: missing Task
# ------------------------------------------------------------------
f="$tmp/no_task.md"
make_valid "$f"
sed -i 's/^Task:.*//' "$f"
check_fail "missing Task" "$f"

# ------------------------------------------------------------------
# FAIL: missing Type
# ------------------------------------------------------------------
f="$tmp/no_type.md"
make_valid "$f"
sed -i 's/^Type:.*//' "$f"
check_fail "missing Type" "$f"

# ------------------------------------------------------------------
# FAIL: missing Depends on phases
# ------------------------------------------------------------------
f="$tmp/no_depends.md"
make_valid "$f"
sed -i 's/^Depends on phases:.*//' "$f"
check_fail "missing Depends on phases" "$f"

# ------------------------------------------------------------------
# FAIL: missing ## Work section
# ------------------------------------------------------------------
f="$tmp/no_work.md"
make_valid "$f"
sed -i 's/^## Work\r\{0,1\}$/## REMOVED/' "$f"
check_fail "missing ## Work section" "$f"

# ------------------------------------------------------------------
# FAIL: missing ## Acceptance criteria section
# ------------------------------------------------------------------
f="$tmp/no_ac_section.md"
make_valid "$f"
sed -i 's/^## Acceptance criteria.*/## REMOVED/' "$f"
check_fail "missing ## Acceptance criteria section" "$f"

# ------------------------------------------------------------------
# FAIL: placeholder-only acceptance criteria
# ------------------------------------------------------------------
f="$tmp/placeholder_ac.md"
make_valid "$f"
sed -i 's/^- `npm run build`.*/- {{CRITERION_1}}/' "$f"
sed -i 's/^- `npm test.*/- {{CRITERION_2}}/' "$f"
sed -i 's|^- GET /api/settings.*|- {{CRITERION_3}}|' "$f"
check_fail_contains "placeholder-only acceptance criteria" "$f" "## Acceptance criteria needs at least one non-placeholder"

# ------------------------------------------------------------------
# FAIL: missing ## Mandatory commands section
# ------------------------------------------------------------------
f="$tmp/no_mandatory.md"
make_valid "$f"
sed -i 's/^## Mandatory commands.*/## REMOVED/' "$f"
check_fail "missing ## Mandatory commands section" "$f"

# ------------------------------------------------------------------
# FAIL: mandatory commands without expected success shape
# ------------------------------------------------------------------
f="$tmp/no_command_expected.md"
make_valid "$f"
sed -i 's/^-[[:space:]]*npm run build.*/- npm run build/' "$f"
sed -i 's/^-[[:space:]]*npm test.*/- npm test -- --testPathPattern=settings/' "$f"
check_fail "mandatory commands without expected success shape" "$f"

# ------------------------------------------------------------------
# FAIL: placeholder-only mandatory commands
# ------------------------------------------------------------------
f="$tmp/placeholder_mc.md"
make_valid "$f"
sed -i 's/^- npm run build.*/- {{COMMAND_1}}/' "$f"
sed -i 's/^- npm test.*/- {{COMMAND_2}}/' "$f"
check_fail_contains "placeholder-only mandatory commands" "$f" "## Mandatory commands needs at least one non-placeholder"

# ------------------------------------------------------------------
# FAIL: missing ## Evidence required section
# ------------------------------------------------------------------
f="$tmp/no_evidence.md"
make_valid "$f"
sed -i 's/^## Evidence required in transcript\r\{0,1\}$/## REMOVED/' "$f"
check_fail "missing ## Evidence required section" "$f"

# ------------------------------------------------------------------
# FAIL: missing ## Rollback section
# ------------------------------------------------------------------
f="$tmp/no_rollback.md"
make_valid "$f"
sed -i 's/^## Rollback \/ defer path\r\{0,1\}$/## REMOVED/' "$f"
check_fail "missing ## Rollback section" "$f"

# ------------------------------------------------------------------
# FAIL: missing ## Current state excerpts section
# ------------------------------------------------------------------
f="$tmp/no_current_state.md"
make_valid "$f"
sed -i 's/^## Current state excerpts\r\{0,1\}$/## REMOVED/' "$f"
check_fail "missing ## Current state excerpts section" "$f"

# ------------------------------------------------------------------
# FAIL: missing ## Maintenance notes section
# ------------------------------------------------------------------
f="$tmp/no_maintenance_notes.md"
make_valid "$f"
sed -i 's/^## Maintenance notes\r\{0,1\}$/## REMOVED/' "$f"
check_fail "missing ## Maintenance notes section" "$f"

# ------------------------------------------------------------------
# FAIL: missing Markdown fallback status
# ------------------------------------------------------------------
f="$tmp/no_markdown_fallback.md"
make_valid "$f"
sed -i '/^Markdown fallback:/d' "$f"
check_fail "missing Markdown fallback status" "$f"

# ------------------------------------------------------------------
# Evidence property tags (#3)
# ------------------------------------------------------------------
# FAIL: mixed tagged/untagged mandatory commands (newly authored spec)
f="$tmp/mixed_property_tags.md"
make_valid "$f"
sed -i 's/- npm run build .* property: behavioral; scope: [^;]*; expected:/- npm run build - expected:/' "$f"
check_fail_contains "mixed property tags" "$f" "mixes tagged and untagged"

# FAIL: invalid property tag (authorization is not an evidence property)
f="$tmp/invalid_property_tag.md"
make_valid "$f"
sed -i 's/property: behavioral; scope: the app compiles from current sources;/property: authorization; scope: x;/' "$f"
check_fail_contains "invalid property tag" "$f" "invalid evidence property tag"

# PASS with warning: fully untagged legacy spec
f="$tmp/legacy_untagged.md"
make_valid "$f"
sed -i 's/property: behavioral; scope: [^;]*; expected:/expected:/g' "$f"
out="$tmp/legacy_untagged.out"
if bash skills/implementaudit/scripts/validate-phase.sh "$f" >"$out" 2>&1 \
    && grep -q "WARNING legacy spec" "$out"; then
  pass=$((pass + 1))
else
  printf 'phase-validation.test: legacy untagged spec must pass WITH warning\n' >&2
  cat "$out" >&2
  fail=$((fail + 1))
fi

# FAIL: prefix alias of a valid class is an INVALID tag, never a silent
# downgrade to legacy (Fable review of PR #25: "structurally" matched
# neither the tag nor the bad-tag regex and passed as legacy-with-warning).
f="$tmp/alias_property_tag.md"
make_valid "$f"
sed -i 's/property: behavioral/property: behaviorally/g' "$f"
check_fail_contains "prefix-alias property tag" "$f" "invalid evidence property tag"

# FAIL: property tag without scope — the tag alone cannot say what the
# check actually tests (issue #3 required property PLUS plain-language
# scope on new-format commands).
f="$tmp/tag_without_scope.md"
make_valid "$f"
sed -i 's/; scope: [^;]*;/;/g' "$f"
check_fail_contains "property tag without scope" "$f" "lacks \`scope:\`"

# ------------------------------------------------------------------
# Reconstructibility (#50): ordered steps, per-step verification,
# scope boundaries, plan-specific STOP conditions
# ------------------------------------------------------------------
# FAIL: vague step language (fixture counter-example)
check_fail_contains "vague step language" \
  fixtures/phase-validation/negative-vague-steps.md \
  "vague step language"

# FAIL: multi-step spec without per-step verification (fixture counter-example)
check_fail_contains "multi-step without per-step verify" \
  fixtures/phase-validation/negative-multistep-no-per-step-verify.md \
  "carries its own verify:"

# FAIL: boilerplate STOP conditions (fixture counter-example)
check_fail_contains "boilerplate STOP conditions" \
  fixtures/phase-validation/negative-boilerplate-stop.md \
  "boilerplate STOP conditions"

# FAIL: new-format spec missing Out of scope
f="$tmp/no_out_of_scope.md"
make_valid "$f"
sed -i 's/^Out of scope:.*$/Removed boundary line./' "$f"
check_fail_contains "new-format spec without Out of scope" "$f" \
  "Out of scope"

# FAIL: vague language injected into a valid spec's steps
f="$tmp/vague_injected.md"
make_valid "$f"
sed -i 's/- Step 3: Register the route.*/- Step 3: Register the route — target: src\/app.ts; change: update the relevant files as needed; verify: npm test; expected: exit 0/' "$f"
check_fail_contains "vague language injected into steps" "$f" \
  "vague step language"

# PASS with warning: legacy spec without ordered Implementation steps
f="$tmp/legacy_no_steps.md"
make_valid "$f"
sed -i '/^## Implementation steps (ordered)$/,/^## Scope boundaries$/{/^## Scope boundaries$/!d}' "$f"
out="$tmp/legacy_no_steps.out"
if bash skills/implementaudit/scripts/validate-phase.sh "$f" >"$out" 2>&1 \
    && grep -q "no ordered" "$out"; then
  pass=$((pass + 1))
else
  printf 'phase-validation.test: legacy spec without steps must pass WITH warning\n' >&2
  cat "$out" >&2
  fail=$((fail + 1))
fi

# Shipped phase-spec fixtures stay LF-only: PR #25's migration rewrote
# three fixtures with CRLF, hiding a 7-line substantive change inside a
# 221-line line-ending churn (Fable review of PR #25).
for spec in fixtures/phase-design/dmadv-greenfield-phase.md \
            fixtures/phase-validation/valid-full-spec.md \
            fixtures/phase-validation/negative-vague-steps.md \
            fixtures/phase-validation/negative-multistep-no-per-step-verify.md \
            fixtures/phase-validation/negative-boilerplate-stop.md \
            fixtures/run-root-example/phases/phase-1.md \
            fixtures/e2e-mini-audit-loop/phase-1.md; do
  if tr -dc '\r' < "$spec" | grep -q .; then
    printf 'phase-validation.test: CRLF found in shipped fixture %s\n' \
      "$spec" >&2
    fail=$((fail + 1))
  else
    pass=$((pass + 1))
  fi
done

# ------------------------------------------------------------------
# R36 phase-derived destructive authority. The authority projection is a
# deterministic receipt from the validated phase, not caller-selected paths.
# ------------------------------------------------------------------
authority_run="$repo_root/.IMPLEMENTAUDIT/runs/authority-Ab3Kx9"
authority_phase="$authority_run/phases/phase-1.md"
mkdir -p "$(dirname "$authority_phase")"
cp fixtures/phase-validation/valid-full-spec.md "$authority_phase"
printf 'claim_id=0123456789abcdef0123456789abcdef\n' > "$authority_run/.claimed"
printf '| 1 | mutation authority fixture |\n' > "$authority_run/ROADMAP.md"
"${py_cmd[@]}" - "$authority_phase" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); text=p.read_text(encoding='utf-8')
text=text.replace('Run root: .IMPLEMENTAUDIT/runs/add-settings-Xy9Zq1',
                  'Run root: .IMPLEMENTAUDIT/runs/authority-Ab3Kx9')
text=text.replace(
    '- Step 1: Create the settings route — target: src/routes/settings.ts (registerSettingsRoutes); change: add GET /api/settings handler behind requireAuth from src/middleware/auth.ts; verify: npm run build; expected: exit 0 with no errors',
    '- Step 1: Create the settings route — target: src/routes/settings.ts (registerSettingsRoutes); change: add GET /api/settings handler behind requireAuth from src/middleware/auth.ts; verify: npm run build; expected: exit 0 with no errors\n  mutation-authority: {"operation":"replace","source":"src/routes/settings.ts","destination":null}')
text=text.replace('In scope: src/routes/settings.ts, tests/settings.test.ts, src/app.ts',
                  'In scope: src/routes/settings.ts, tests/settings.test.ts, src/app.ts\nMutation scope: {"in":["src/routes/settings.ts"],"out":["README.md"]}')
p.write_text(text,encoding='utf-8')
PY
authority_out="$tmp/authority.out"
if bash skills/implementaudit/scripts/validate-phase.sh --mutation-authority "$authority_phase" --step 1 --repo-root "$repo_root" --run-root "$authority_run" >"$authority_out" 2>"$tmp/authority.err" \
  && "${py_cmd[@]}" - "$authority_out" <<'PY'
import json,re,sys
r=json.loads(open(sys.argv[1],encoding='utf-8').read())
want={'schema':'implementaudit.phase-mutation-authority.v1','phase':1,'step':1,
      'run_root':'.IMPLEMENTAUDIT/runs/authority-Ab3Kx9','operation':'replace',
      'source':'src/routes/settings.ts','destination':None,
      'mutation_scope':{'in':['src/routes/settings.ts'],'out':['README.md']}}
for k,v in want.items():
 if r.get(k)!=v: raise SystemExit(f'{k}: {r.get(k)!r} != {v!r}')
if not re.fullmatch(r'[0-9a-f]{64}',r.get('authority_binding_sha256','')): raise SystemExit('binding digest')
PY
then
  pass=$((pass + 1))
else
  printf 'phase-validation.test: mutation authority projection must be exact JSON\n' >&2
  cat "$authority_out" "$tmp/authority.err" >&2
  fail=$((fail + 1))
fi

bad_authority="$tmp/authority-outside.md"
cp "$authority_phase" "$bad_authority"
sed -i 's|"src/routes/settings.ts"],"out"|"tests/settings.test.ts"],"out"|' "$bad_authority"
if bash skills/implementaudit/scripts/validate-phase.sh --mutation-authority "$bad_authority" --step 1 --repo-root "$repo_root" --run-root "$authority_run" >/dev/null 2>&1; then
  printf 'phase-validation.test: out-of-scope mutation authority must fail\n' >&2
  fail=$((fail + 1))
else
  pass=$((pass + 1))
fi
rm -rf "$authority_run"

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'phase-validation.test: FAIL — %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'phase-validation.test: ok (%d/%d)\n' "$pass" "$total"
