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
  printf 'phase-validation.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

pass=0
fail=0

check_pass() {
  local label="$1"
  local file="$2"
  if bash skills/scripts/validate-phase.sh "$file" >/dev/null 2>&1; then
    pass=$((pass + 1))
  else
    printf 'phase-validation.test: UNEXPECTED FAIL for: %s\n' "$label" >&2
    fail=$((fail + 1))
  fi
}

check_fail() {
  local label="$1"
  local file="$2"
  if bash skills/scripts/validate-phase.sh "$file" >/dev/null 2>&1; then
    printf 'phase-validation.test: UNEXPECTED PASS for: %s\n' "$label" >&2
    fail=$((fail + 1))
  else
    pass=$((pass + 1))
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
sed -i 's/^## Work$/## REMOVED/' "$f"
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
cat >"$f" <<'SPEC'
IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 — test
Task: do something real
Type: brownfield
Run root: .IMPLEMENTAUDIT/runs/test-abc
Baseline ref: abc123
Owner/source: src/foo.ts
Mandatory commands: npm test
Acceptance criteria: 1
Evidence required: test output
Depends on phases: none

## Why

Fix something real.

## Work

- Do the real thing

## Acceptance criteria (all must pass — verify each in transcript)

- {{CRITERION_1}}

## Mandatory commands (run each; surface last ~10 lines + exit code in transcript)

- npm test

## Evidence required in transcript

- npm test output

## Rollback / defer path

git checkout HEAD -- src/foo.ts

## Graphify / ActiveGraph / Markdown fallback status

Graphify: absent
ActiveGraph: absent
Markdown fallback: yes

## Notes

none

---

IMPLEMENTAUDIT_PHASE_VERIFY

Phase 1 acceptance criteria:
- [pass] placeholder: ok

Mandatory commands:
- npm test exit 0

Cleanliness:
- Debug prints added: 0
- Session debug-markers added (todo/fixme/xxx): 0
- Dead imports added: 0

Sidecar: Graphify skipped; ActiveGraph skipped; Markdown fallback yes
Remaining risk: none
Trust-prior count: 0
Re-verified count: 0

AGENTS_UPDATE_DECISION

Decision: not warranted
Reason: none
Scope: N/A
Evidence location: N/A
Conflict or owner-decision note: none

CONTINUITY_DECISION

Decision: none
Reason: N/A
Evidence boundary: N/A

IMPLEMENTAUDIT_PHASE_DONE

Status: done
Evidence: ok
Follow-up: none
SPEC
check_fail "placeholder-only acceptance criteria" "$f"

# ------------------------------------------------------------------
# FAIL: missing ## Mandatory commands section
# ------------------------------------------------------------------
f="$tmp/no_mandatory.md"
make_valid "$f"
sed -i 's/^## Mandatory commands.*/## REMOVED/' "$f"
check_fail "missing ## Mandatory commands section" "$f"

# ------------------------------------------------------------------
# FAIL: placeholder-only mandatory commands
# ------------------------------------------------------------------
f="$tmp/placeholder_mc.md"
make_valid "$f"
# Replace real command with placeholder
"${py_cmd[@]}" -c "
import re
from pathlib import Path
t = Path('$f').read_text(encoding='utf-8')
t = re.sub(r'(?m)^## Mandatory commands.*?\n(- npm run build\n- npm test.*?\n)',
           lambda m: m.group(0).replace('npm run build', '{{COMMAND_1}}').replace('npm test -- --testPathPattern=settings', '{{COMMAND_2}}'),
           t, count=1)
Path('$f').write_text(t, encoding='utf-8')
" 2>/dev/null || true
# Simpler approach: create a spec with placeholder commands
cat >"$f" <<'SPEC'
IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 — test
Task: do something
Type: brownfield
Run root: .IMPLEMENTAUDIT/runs/test-abc
Baseline ref: abc123
Owner/source: src/foo.ts
Mandatory commands: {{COMMAND_1}}
Acceptance criteria: 1
Evidence required: output
Depends on phases: none

## Why

Fix a real thing.

## Work

- Do the real thing

## Acceptance criteria (all must pass — verify each in transcript)

- The output file exists at dist/foo.js

## Mandatory commands (run each; surface last ~10 lines + exit code in transcript)

- {{COMMAND_1}}

## Evidence required in transcript

- command output

## Rollback / defer path

git checkout HEAD -- src/foo.ts

## Graphify / ActiveGraph / Markdown fallback status

Graphify: absent
ActiveGraph: absent
Markdown fallback: yes

## Notes

none

---

IMPLEMENTAUDIT_PHASE_VERIFY

Phase 1 acceptance criteria:
- [pass] file exists: ok

Mandatory commands:
- {{COMMAND_1}} exit 0

Cleanliness:
- Debug prints added: 0

Sidecar: Graphify skipped; ActiveGraph skipped; Markdown fallback yes
Remaining risk: none
Trust-prior count: 0
Re-verified count: 1

AGENTS_UPDATE_DECISION

Decision: not warranted
Reason: none
Scope: N/A
Evidence location: N/A
Conflict or owner-decision note: none

CONTINUITY_DECISION

Decision: none
Reason: N/A
Evidence boundary: N/A

IMPLEMENTAUDIT_PHASE_DONE

Status: done
Evidence: ok
Follow-up: none
SPEC
check_fail "placeholder-only mandatory commands" "$f"

# ------------------------------------------------------------------
# FAIL: missing ## Evidence required section
# ------------------------------------------------------------------
f="$tmp/no_evidence.md"
make_valid "$f"
sed -i 's/^## Evidence required in transcript$/## REMOVED/' "$f"
check_fail "missing ## Evidence required section" "$f"

# ------------------------------------------------------------------
# FAIL: missing ## Rollback section
# ------------------------------------------------------------------
f="$tmp/no_rollback.md"
make_valid "$f"
sed -i 's/^## Rollback \/ defer path$/## REMOVED/' "$f"
check_fail "missing ## Rollback section" "$f"

# ------------------------------------------------------------------
# FAIL: missing Markdown fallback status
# ------------------------------------------------------------------
f="$tmp/no_markdown_fallback.md"
make_valid "$f"
sed -i '/^Markdown fallback:/d' "$f"
check_fail "missing Markdown fallback status" "$f"

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'phase-validation.test: FAIL — %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'phase-validation.test: ok (%d/%d)\n' "$pass" "$total"
