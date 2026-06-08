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
    printf 'sidecars.test: FAIL: %s\n' "$label" >&2
    fail=$((fail + 1))
  fi
}

# ---------------------------------------------------------------------------
# Boundary check: check-sidecar-boundaries.sh must pass on the live repo
# ---------------------------------------------------------------------------
bash scripts/check-sidecar-boundaries.sh
check_pass "check-sidecar-boundaries passes on live repo" 0

# ---------------------------------------------------------------------------
# Negative test: mutating SKILL.md to claim Graphify "proves correctness"
# must cause check-sidecar-boundaries.sh to fail
# ---------------------------------------------------------------------------
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

cp -R skills README.md AGENTS.md scripts tests "$tmp/"
mkdir -p "$tmp/scripts"
cp scripts/check-sidecar-boundaries.sh "$tmp/scripts/check-sidecar-boundaries.sh"

perl -0pi -e 's/Graphify output is orientation evidence, not proof/Graphify output proves correctness/g' \
  "$tmp/skills/SKILL.md"
if (cd "$tmp" && bash scripts/check-sidecar-boundaries.sh >/dev/null 2>&1); then
  printf 'sidecars.test: expected Graphify overclaim to fail check-sidecar-boundaries\n' >&2
  check_pass "Graphify overclaim rejected by boundary check" 1
else
  check_pass "Graphify overclaim rejected by boundary check" 0
fi

# ---------------------------------------------------------------------------
# Scenario 1: Graphify absent — ordinary Gemba passes
# Fixture: documents expected sidecar block for absent Graphify
# ---------------------------------------------------------------------------
fixture="fixtures/sidecars/graphify-absent.md"
grep -Fq "Graphify absent" "$fixture" \
  && check_pass "scenario1: Graphify absent documented" 0 \
  || check_pass "scenario1: Graphify absent documented" 1

grep -Fq "Markdown fallback: yes" "$fixture" \
  && check_pass "scenario1: Markdown fallback yes when Graphify absent" 0 \
  || check_pass "scenario1: Markdown fallback yes when Graphify absent" 1

grep -Fq "non-blocking" "$fixture" \
  && check_pass "scenario1: Graphify absent is non-blocking" 0 \
  || check_pass "scenario1: Graphify absent is non-blocking" 1

# ---------------------------------------------------------------------------
# Scenario 2: Graphify present and fresh — orientation evidence only
# Fixture: documents required and forbidden language
# ---------------------------------------------------------------------------
fixture="fixtures/sidecars/graphify-present-fresh.md"
grep -Fq "orientation evidence" "$fixture" \
  && check_pass "scenario2: orientation evidence language present" 0 \
  || check_pass "scenario2: orientation evidence language present" 1

grep -Fq "orientation evidence" "$fixture" \
  && check_pass "scenario2: orientation evidence not proof" 0 \
  || check_pass "scenario2: orientation evidence not proof" 1

grep -Fq "Graphify does not provide proof" "$fixture" \
  && check_pass "scenario2: Graphify not proof language documented" 0 \
  || check_pass "scenario2: Graphify not proof language documented" 1

# ---------------------------------------------------------------------------
# Scenario 3: Graphify stale — record stale, require live confirmation
# Fixture: documents stale recording and live file confirmation requirement
# ---------------------------------------------------------------------------
fixture="fixtures/sidecars/graphify-stale.md"
grep -Fq "stale" "$fixture" \
  && check_pass "scenario3: stale recorded in fixture" 0 \
  || check_pass "scenario3: stale recorded in fixture" 1

grep -Fq "live file" "$fixture" \
  && check_pass "scenario3: live file confirmation required" 0 \
  || check_pass "scenario3: live file confirmation required" 1

grep -Fq "present-and-stale" "$fixture" \
  && check_pass "scenario3: present-and-stale marker documented" 0 \
  || check_pass "scenario3: present-and-stale marker documented" 1

# ---------------------------------------------------------------------------
# Scenario 4: ActiveGraph absent — Markdown fallback is first-class
# Fixture: documents first-class Markdown fallback
# ---------------------------------------------------------------------------
fixture="fixtures/sidecars/activegraph-absent.md"
grep -Fq "first-class" "$fixture" \
  && check_pass "scenario4: Markdown fallback is first-class" 0 \
  || check_pass "scenario4: Markdown fallback is first-class" 1

grep -Fq "ActiveGraph absent" "$fixture" \
  && check_pass "scenario4: ActiveGraph absent documented" 0 \
  || check_pass "scenario4: ActiveGraph absent documented" 1

grep -Fq "not block" "$fixture" \
  && check_pass "scenario4: absence does not block run" 0 \
  || check_pass "scenario4: absence does not block run" 1

# ---------------------------------------------------------------------------
# Scenario 5: ActiveGraph unauthorized — no event write
# Fixture: documents no-write rule when unauthorized
# ---------------------------------------------------------------------------
fixture="fixtures/sidecars/activegraph-unauthorized.md"
grep -Fq "no event write" "$fixture" \
  && check_pass "scenario5: no event write when unauthorized" 0 \
  || check_pass "scenario5: no event write when unauthorized" 1

grep -Fq "configured-not-authorized" "$fixture" \
  && check_pass "scenario5: configured-not-authorized documented" 0 \
  || check_pass "scenario5: configured-not-authorized documented" 1

grep -Fq "Configuration" "$fixture" \
  && check_pass "scenario5: configuration-not-authorization rule documented" 0 \
  || check_pass "scenario5: configuration-not-authorization rule documented" 1

# ---------------------------------------------------------------------------
# Scenario 6: ActiveGraph authorized — Capability Ledger from gates only
# Fixture: documents bounded entry requirement and forbidden broad claims
# ---------------------------------------------------------------------------
fixture="fixtures/sidecars/activegraph-custody.md"
grep -Fq "recorded gate passages" "$fixture" \
  && check_pass "scenario6: gate-passages requirement documented" 0 \
  || check_pass "scenario6: gate-passages requirement documented" 1

grep -Fq "bounded: true" "$fixture" \
  && check_pass "scenario6: bounded entry example present" 0 \
  || check_pass "scenario6: bounded entry example present" 1

grep -Fq "bounded: false" "$fixture" \
  && check_pass "scenario6: unbounded entry rejection example present" 0 \
  || check_pass "scenario6: unbounded entry rejection example present" 1

# ---------------------------------------------------------------------------
# Scenario 7: Sidecar boundary check — overclaim rejected
# Fixture: documents the required boundary language
# ---------------------------------------------------------------------------
fixture="fixtures/sidecars/sidecar-overclaim-rejected.md"
grep -Fq "Graphify output is orientation evidence, not proof" "$fixture" \
  && check_pass "scenario7: required Graphify boundary phrase documented" 0 \
  || check_pass "scenario7: required Graphify boundary phrase documented" 1

grep -Fq "ActiveGraph custody is not correctness proof" "$fixture" \
  && check_pass "scenario7: required ActiveGraph boundary phrase documented" 0 \
  || check_pass "scenario7: required ActiveGraph boundary phrase documented" 1

# The required boundary phrases must also exist in the live SKILL.md
grep -Fq "Graphify output is orientation evidence, not proof" skills/SKILL.md \
  && check_pass "scenario7: Graphify boundary phrase in live SKILL.md" 0 \
  || check_pass "scenario7: Graphify boundary phrase in live SKILL.md" 1

grep -Fq "ActiveGraph custody is not correctness proof" skills/SKILL.md \
  && check_pass "scenario7: ActiveGraph boundary phrase in live SKILL.md" 0 \
  || check_pass "scenario7: ActiveGraph boundary phrase in live SKILL.md" 1

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'sidecars.test: FAIL — %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'sidecars.test: ok (%d/%d)\n' "$pass" "$total"
