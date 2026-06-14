#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

pass=0
fail=0

check_pass() {
  local label="$1"
  local result="$2"
  if [ "$result" -eq 0 ]; then
    pass=$((pass + 1))
  else
    printf 'continuity.test: FAIL: %s\n' "$label" >&2
    fail=$((fail + 1))
  fi
}

check_fail() {
  local label="$1"
  local result="$2"
  if [ "$result" -ne 0 ]; then
    pass=$((pass + 1))
  else
    printf 'continuity.test: UNEXPECTED PASS (should have failed): %s\n' "$label" >&2
    fail=$((fail + 1))
  fi
}

# ---------------------------------------------------------------------------
# Phrase-presence checks (verify skills contain continuity contract language)
# ---------------------------------------------------------------------------
require() {
  local file="$1"
  local text="$2"
  grep -Fq "$text" "$file" && check_pass "phrase '$text' in $file" 0 || {
    printf 'continuity.test: missing in %s: %s\n' "$file" "$text" >&2
    check_pass "phrase '$text' in $file" 1
  }
}

require skills/implementaudit/SKILL.md "bounded continuity"
require skills/implementaudit/SKILL.md "CONTINUITY_DECISION"
require skills/implementaudit/SKILL.md "memory/continuity"
require skills/implementaudit/SKILL.md "IMPLEMENTAUDIT_CONTINUITY_SAVED"
require skills/implementaudit/SKILL.md "Bounded continuity preload"
require skills/implementaudit/SKILL.md "Continuity from any source never overrides"
require skills/implementaudit/templates/STATE.md "Continuity decision"
require skills/implementaudit/templates/PROTOCOL.md "CONTINUITY_DECISION"
require skills/implementaudit/templates/PROTOCOL.md "IMPLEMENTAUDIT_CONTINUITY_SAVED"
require skills/implementaudit/templates/PROTOCOL.md "run-local applied-context note"
require skills/implementaudit/templates/PROTOCOL.md "optional personal/project note"
require skills/implementaudit/templates/PROTOCOL.md "optional ActiveGraph event"
require skills/implementaudit/templates/THINKING.md "Applied context"
require AGENTS.md "bounded continuity"

# ---------------------------------------------------------------------------
# Scenario 1: memory absent — run valid
# Fixture: valid phase transcript with CONTINUITY_DECISION Decision: none
# ---------------------------------------------------------------------------
fixture="fixtures/continuity/no-memory-run.md"
grep -Fq "CONTINUITY_DECISION" "$fixture" \
  && check_pass "scenario1: CONTINUITY_DECISION present in no-memory-run" 0 \
  || check_pass "scenario1: CONTINUITY_DECISION present in no-memory-run" 1

grep -Fq "Decision: none" "$fixture" \
  && check_pass "scenario1: Decision: none in no-memory-run" 0 \
  || check_pass "scenario1: Decision: none in no-memory-run" 1

grep -qF "IMPLEMENTAUDIT_PHASE_DONE" "$fixture" \
  && check_pass "scenario1: IMPLEMENTAUDIT_PHASE_DONE present" 0 \
  || check_pass "scenario1: IMPLEMENTAUDIT_PHASE_DONE present" 1

# ---------------------------------------------------------------------------
# Scenario 2: memory present but no write warranted — CONTINUITY_DECISION none
# Fixture: valid phase with applied-memories read but no writeback
# ---------------------------------------------------------------------------
fixture="fixtures/continuity/no-write-warranted.md"
grep -Fq "Decision: none" "$fixture" \
  && check_pass "scenario2: Decision: none in no-write-warranted" 0 \
  || check_pass "scenario2: Decision: none in no-write-warranted" 1

grep -Fq "Applied memories" "$fixture" 2>/dev/null \
  || grep -Fq "applied-memories" "$fixture" \
  || grep -Fq "Applied memories were read" "$fixture" \
  && check_pass "scenario2: memory-read acknowledgment present" 0 \
  || check_pass "scenario2: memory-read acknowledgment present" 1

# ---------------------------------------------------------------------------
# Scenario 3: safe note write — correct frontmatter required
# Fixture: memory note with required frontmatter keys
# ---------------------------------------------------------------------------
fixture="fixtures/continuity/safe-note-write.md"
grep -Fq "secret: false" "$fixture" \
  && check_pass "scenario3: secret: false present in safe-note" 0 \
  || check_pass "scenario3: secret: false present in safe-note" 1

grep -Fq "diagnostic: false" "$fixture" \
  && check_pass "scenario3: diagnostic: false present in safe-note" 0 \
  || check_pass "scenario3: diagnostic: false present in safe-note" 1

grep -Fq "session: bounded" "$fixture" \
  && check_pass "scenario3: session: bounded present in safe-note" 0 \
  || check_pass "scenario3: session: bounded present in safe-note" 1

grep -Fq "evidence:" "$fixture" \
  && check_pass "scenario3: evidence field present in safe-note" 0 \
  || check_pass "scenario3: evidence field present in safe-note" 1

grep -Fq "IMPLEMENTAUDIT_CONTINUITY_SAVED" "$fixture" \
  && check_pass "scenario3: IMPLEMENTAUDIT_CONTINUITY_SAVED marker present when writeback performed" 0 \
  || check_pass "scenario3: IMPLEMENTAUDIT_CONTINUITY_SAVED marker present when writeback performed" 1

grep -Fq "Not saved:" "$fixture" \
  && check_pass "scenario3: Not saved field present in IMPLEMENTAUDIT_CONTINUITY_SAVED" 0 \
  || check_pass "scenario3: Not saved field present in IMPLEMENTAUDIT_CONTINUITY_SAVED" 1

# ---------------------------------------------------------------------------
# Scenario 4: unsafe content — rejected
# Fixture: documents rejection rules with examples of forbidden content.
# The fixture intentionally contains example forbidden strings to document
# what must be rejected; we verify the rejection rules are present.
# ---------------------------------------------------------------------------
fixture="fixtures/continuity/unsafe-content-rejected.md"

# The fixture must document the rejection reason
grep -Fq "Rejection reason" "$fixture" \
  && check_pass "scenario4: rejection reason documented" 0 \
  || check_pass "scenario4: rejection reason documented" 1

# The fixture must say must NOT write (documenting the rejection contract)
grep -Fq "Must NOT write" "$fixture" \
  && check_pass "scenario4: must-not-write rule present" 0 \
  || check_pass "scenario4: must-not-write rule present" 1

# The fixture must document the Andon fallback
grep -Fq "Andon" "$fixture" \
  && check_pass "scenario4: Andon fallback documented" 0 \
  || check_pass "scenario4: Andon fallback documented" 1

# ---------------------------------------------------------------------------
# Scenario 5: final project continuity — correct ordering
# Fixture: AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE
# CONTINUITY_DECISION must appear before IMPLEMENTAUDIT_RUN_COMPLETE
# ---------------------------------------------------------------------------
fixture="fixtures/continuity/final-project-decision.md"

# AUDIT_COMPLETE must appear in the file
grep -Fq "AUDIT_COMPLETE" "$fixture" \
  && check_pass "scenario5: AUDIT_COMPLETE present" 0 \
  || check_pass "scenario5: AUDIT_COMPLETE present" 1

# IMPLEMENTAUDIT_RUN_COMPLETE must appear after AUDIT_COMPLETE
# Use awk for robust line number extraction (avoids CRLF issues on Windows)
audit_line=$(awk '/^AUDIT_COMPLETE/{print NR; exit}' "$fixture")
run_complete_line=$(awk '/^IMPLEMENTAUDIT_RUN_COMPLETE/{print NR; exit}' "$fixture")
if [ -n "$audit_line" ] && [ -n "$run_complete_line" ] && [ "$audit_line" -lt "$run_complete_line" ]; then
  check_pass "scenario5: AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE" 0
else
  check_pass "scenario5: AUDIT_COMPLETE before IMPLEMENTAUDIT_RUN_COMPLETE" 1
fi

# CONTINUITY_DECISION must appear before IMPLEMENTAUDIT_RUN_COMPLETE
continuity_line=$(awk '/^CONTINUITY_DECISION/{print NR; exit}' "$fixture")
if [ -n "$continuity_line" ] && [ -n "$run_complete_line" ] && [ "$continuity_line" -lt "$run_complete_line" ]; then
  check_pass "scenario5: CONTINUITY_DECISION before IMPLEMENTAUDIT_RUN_COMPLETE" 0
else
  check_pass "scenario5: CONTINUITY_DECISION before IMPLEMENTAUDIT_RUN_COMPLETE" 1
fi

# ---------------------------------------------------------------------------
# Scenario 6: no boundary crossing — MEMORY_SAVED must not appear in
# native surfaces (skills/, README.md, AGENTS.md).
# The fixtures/ directory may contain documentation about the check and is
# not scanned here (fixtures are documentation, not native surfaces).
# ---------------------------------------------------------------------------
fixture="fixtures/continuity/no-boundary-crossing.md"

# The fixture must document the no-boundary-crossing rule
grep -Fq "MEMORY_SAVED" "$fixture" \
  && check_pass "scenario6: no-boundary-crossing fixture documents the MEMORY_SAVED check" 0 \
  || check_pass "scenario6: no-boundary-crossing fixture documents the MEMORY_SAVED check" 1

# The fixture must describe the no-boundary-crossing rule
grep -Fq "boundary-crossing failure" "$fixture" \
  && check_pass "scenario6: no-boundary-crossing rule documented" 0 \
  || check_pass "scenario6: no-boundary-crossing rule documented" 1

# Native surfaces must not contain MEMORY_SAVED
if grep -R "MEMORY_SAVED" -n skills README.md AGENTS.md >/dev/null 2>&1; then
  printf 'continuity.test: external memory marker leaked into native surfaces\n' >&2
  check_pass "no MEMORY_SAVED in native surfaces" 1
else
  check_pass "no MEMORY_SAVED in native surfaces" 0
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'continuity.test: FAIL — %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'continuity.test: ok (%d/%d)\n' "$pass" "$total"
