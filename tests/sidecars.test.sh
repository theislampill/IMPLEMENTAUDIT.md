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

check_contains() {
  local label="$1"
  local path="$2"
  local literal="$3"
  grep -Fq -- "$literal" "$path" \
    && check_pass "$label" 0 \
    || check_pass "$label" 1
}

check_not_contains() {
  local label="$1"
  local path="$2"
  local literal="$3"
  if grep -Fq -- "$literal" "$path"; then
    check_pass "$label" 1
  else
    check_pass "$label" 0
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

cp -R skills README.md AGENTS.md CONTRIBUTING.md docs scripts tests "$tmp/"
mkdir -p "$tmp/scripts"
cp scripts/check-sidecar-boundaries.sh "$tmp/scripts/check-sidecar-boundaries.sh"

perl -0pi -e 's/Graphify output is orientation evidence, not proof/Graphify output proves correctness/g' \
  "$tmp/skills/implementaudit/SKILL.md"
set +e
mutation_output="$(cd "$tmp" && bash scripts/check-sidecar-boundaries.sh 2>&1)"
mutation_status=$?
set -e
if [ "$mutation_status" -ne 0 ] && printf '%s' "$mutation_output" | grep -Fq "Graphify orientation-only boundary is missing"; then
  check_pass "Graphify overclaim rejected by boundary check" 0
else
  printf 'sidecars.test: Graphify mutation output: %s\n' "$mutation_output" >&2
  check_pass "Graphify overclaim rejected by boundary check" 1
fi

# The post-#105 one-line spine compression is pinned as a whole. Mutating the
# authorization half must fail even while the D5/D9 substrings still exist in
# other carriers.
tmp_spine="$(mktemp -d)"
trap 'rm -rf "$tmp" "$tmp_spine"' EXIT
cp -R skills README.md AGENTS.md CONTRIBUTING.md docs scripts tests "$tmp_spine/"
perl -0pi -e 's/their presence authorizes no install/their presence permits install/g' \
  "$tmp_spine/skills/implementaudit/SKILL.md"
set +e
spine_output="$(cd "$tmp_spine" && bash scripts/check-sidecar-boundaries.sh 2>&1)"
spine_status=$?
set -e
if [ "$spine_status" -ne 0 ] && printf '%s' "$spine_output" | grep -Fq "compressed spine sidecar boundary is missing"; then
  check_pass "compressed spine sidecar mutation rejected" 0
else
  printf 'sidecars.test: compressed spine mutation output: %s\n' "$spine_output" >&2
  check_pass "compressed spine sidecar mutation rejected" 1
fi

tmp_promote="$(mktemp -d)"
trap 'rm -rf "$tmp" "$tmp_spine" "$tmp_promote"' EXIT
cp -R skills README.md AGENTS.md CONTRIBUTING.md docs scripts tests "$tmp_promote/"
printf '\nNeither sidecar is canonical proof unless the repo promotes it.\n' >> \
  "$tmp_promote/skills/implementaudit/references/routing.md"
set +e
promote_output="$(cd "$tmp_promote" && bash scripts/check-sidecar-boundaries.sh 2>&1)"
promote_status=$?
set -e
if [ "$promote_status" -ne 0 ] && printf '%s' "$promote_output" | grep -Fq "sidecar proof-promotion wording is present"; then
  check_pass "sidecar proof-promotion wording rejected" 0
else
  printf 'sidecars.test: proof-promotion mutation output: %s\n' "$promote_output" >&2
  check_pass "sidecar proof-promotion wording rejected" 1
fi

tmp_contract="$(mktemp -d)"
trap 'rm -rf "$tmp" "$tmp_promote" "$tmp_contract"' EXIT
cp -R skills README.md AGENTS.md CONTRIBUTING.md docs scripts tests "$tmp_contract/"
perl -0pi -e 's/owner-named backend/auto-selected backend/g' \
  "$tmp_contract/skills/implementaudit/references/sidecars.md"
set +e
backend_output="$(cd "$tmp_contract" && bash scripts/check-sidecar-boundaries.sh 2>&1)"
backend_status=$?
set -e
if [ "$backend_status" -ne 0 ] && printf '%s' "$backend_output" | grep -Fq "owner-named-backend rule is missing"; then
  check_pass "owner-named-backend mutation rejected" 0
else
  printf 'sidecars.test: backend mutation output: %s\n' "$backend_output" >&2
  check_pass "owner-named-backend mutation rejected" 1
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
grep -Fq "Graphify output is orientation evidence, not proof" skills/implementaudit/SKILL.md \
  && check_pass "scenario7: Graphify boundary phrase in live SKILL.md" 0 \
  || check_pass "scenario7: Graphify boundary phrase in live SKILL.md" 1

grep -Fq "ActiveGraph custody is not correctness proof" skills/implementaudit/SKILL.md \
  && check_pass "scenario7: ActiveGraph boundary phrase in live SKILL.md" 0 \
  || check_pass "scenario7: ActiveGraph boundary phrase in live SKILL.md" 1

# ---------------------------------------------------------------------------
# Scenario 8: executable graph freshness comparison
# ---------------------------------------------------------------------------
freshness_helper="skills/implementaudit/scripts/validate-run-root.sh"
stale_graph="fixtures/sidecar-contract/stale-graph/graph.json"

set +e
stale_output="$(bash "$freshness_helper" --graph-freshness "$stale_graph" . 2>&1)"
stale_status=$?
set -e
if [ "$stale_status" -ne 0 ] && printf '%s' "$stale_output" | grep -Fq "stale-sidecar"; then
  check_pass "scenario8: stale built_at_commit fires stale-sidecar" 0
else
  printf 'sidecars.test: stale freshness output: %s\n' "$stale_output" >&2
  check_pass "scenario8: stale built_at_commit fires stale-sidecar" 1
fi

fresh_graph="$tmp/fresh-graph.json"
current_head="$(git rev-parse HEAD)"
sed "s/__CURRENT_HEAD__/$current_head/" \
  fixtures/sidecar-contract/fresh-graph/graph.json > "$fresh_graph"
set +e
fresh_output="$(bash "$freshness_helper" --graph-freshness "$fresh_graph" . 2>&1)"
fresh_status=$?
set -e
if [ "$fresh_status" -eq 0 ] && [ -z "$fresh_output" ]; then
  check_pass "scenario8: matching built_at_commit passes silently" 0
else
  printf 'sidecars.test: fresh freshness output: %s\n' "$fresh_output" >&2
  check_pass "scenario8: matching built_at_commit passes silently" 1
fi

# ---------------------------------------------------------------------------
# Scenario 9: narrowed carrier contract is present on every owning surface
# ---------------------------------------------------------------------------
sidecar_ref="skills/implementaudit/references/sidecars.md"
lean_ref="skills/implementaudit/references/lean-operating-discipline.md"
routing_ref="skills/implementaudit/references/routing.md"
sidecar_template="skills/implementaudit/templates/sidecars.md"
protocol_template="skills/implementaudit/templates/PROTOCOL.md"
thinking_template="skills/implementaudit/templates/THINKING.md"

check_contains "scenario9: observable terrain trigger recorded" "$sidecar_ref" "terrain-shaped"
check_contains "scenario9: anti-trigger routes reference questions to grep" "$routing_ref" "reference-shaped"
check_contains "scenario9: built_at_commit comparison documented" "$sidecar_ref" "built_at_commit"
check_contains "scenario9: freshness command recorded in run artifact" "$sidecar_template" "git rev-parse HEAD"
check_not_contains "scenario9: hand-filled Freshness column retired" "$sidecar_template" "| Freshness |"
check_contains "scenario9: privacy and spend disclosure present" "$sidecar_ref" "## Privacy and spend"
check_contains "scenario9: filename heuristic limitation disclosed" "$sidecar_ref" "filename heuristic"
check_contains "scenario9: unmeasurable spend disclosed" "$sidecar_ref" "unmeasurable"
check_contains "scenario9: owner-named backend required" "$sidecar_ref" "owner-named backend"
check_contains "scenario9: Ollama explicitly unauthorized" "$sidecar_ref" "Ollama is explicitly unauthorized"
check_contains "scenario9: dated Codex-not-Ollama precedent cited" "$sidecar_ref" "owner said Codex, not Ollama"
check_contains "scenario9: dogfood-only scope qualified as tested" "$lean_ref" "dogfood-only"
check_contains "scenario9: third-party broadening gate recorded" "$sidecar_ref" "unfamiliar third-party repo"
check_contains "scenario9: Graphify known limitations recorded" "$lean_ref" "module-level constants"
check_contains "scenario9: ActiveGraph mirror is non-authoritative" "$lean_ref" "non-authoritative mirror"
check_contains "scenario9: run root remains authority" "$protocol_template" "run root remains the sole authority"
check_contains "scenario9: fork/diff checkpoint use survives" "$sidecar_template" "fork / diff"
check_contains "scenario9: THINKING carries narrowed trigger decision" "$thinking_template" "Graphify trigger decision"
check_contains "scenario9: missed-use goal retired" "$sidecar_ref" "missed-use-detection goal is retired"
check_contains "scenario9: auditor portal carries non-authoritative mirror" \
  docs/portal/pages/for-auditors-and-maintainers.html "optional non-authoritative mirror"
check_contains "scenario9: state portal carries executable freshness" \
  docs/portal/pages/state-and-artifacts.html "Graphify trigger/freshness evidence"
check_contains "scenario9: package portal carries checkpoint/mirror state" \
  docs/portal/pages/package-contents.html "ActiveGraph checkpoint/mirror state"
check_contains "scenario9: completion portal rejects lifecycle proof" \
  docs/portal/pages/completion-semantics.html "ActiveGraph correctness or lifecycle proof"
check_contains "scenario9: terminology portal uses narrowed sidecar handle" \
  docs/portal/pages/terminology.html "optional terrain/checkpoint context"
check_contains "scenario9: audit gate portal keeps mirror non-authoritative" \
  docs/portal/pages/audit-gate-model.html "checkpoint assistance or an optional mirror"
check_contains "scenario9: evidence portal carries qualified orientation" \
  docs/portal/pages/evidence-boundaries.html "qualified first-contact orientation"
check_contains "scenario9: reference index carries checkpoint/mirror boundary" \
  docs/portal/pages/reference-index.html "ActiveGraph checkpoint/mirror boundaries"
check_contains "scenario9: routing portal carries anti-trigger decision" \
  docs/portal/pages/routing.html "Which anti-trigger, stale signal"
check_contains "scenario9: overview portal carries checkpoint/mirror boundary" \
  docs/portal/pages/what-it-is.html "fork/diff checkpoints or mirror run-root events"

# Static fixtures lock the refusal and broadening decisions without running a
# model, installing Graphify, or relying on a live backend.
check_contains "scenario9: auto-detected Ollama fixture refuses dispatch" \
  fixtures/sidecar-contract/auto-backend-refusal.md "OLLAMA_HOST | set | none | refused"
check_contains "scenario9: Gemini auto-detection fixture refuses dispatch" \
  fixtures/sidecar-contract/auto-backend-refusal.md "GEMINI_API_KEY | set | none | refused"
set +e
anti_trigger_output="$(bash scripts/check-sidecar-boundaries.sh --evaluate-fixture \
  fixtures/sidecar-contract/anti-trigger-routing.md 2>&1)"
anti_trigger_status=$?
set -e
if [ "$anti_trigger_status" -ne 0 ] && printf '%s' "$anti_trigger_output" | grep -Fq "terrain-shaped trigger is missing"; then
  check_pass "scenario9: data-file consumer proposal is rejected" 0
else
  printf 'sidecars.test: anti-trigger fixture output: %s\n' "$anti_trigger_output" >&2
  check_pass "scenario9: data-file consumer proposal is rejected" 1
fi

check_pass "scenario9: terrain-shaped proposal survives narrowing" \
  "$(bash scripts/check-sidecar-boundaries.sh --evaluate-fixture \
    fixtures/sidecar-contract/terrain-trigger-routing.md >/dev/null 2>&1; printf '%s' "$?")"

set +e
footprint_output="$(bash scripts/check-sidecar-boundaries.sh --evaluate-fixture \
  fixtures/sidecar-contract/footprint-default.md 2>&1)"
footprint_status=$?
set -e
if [ "$footprint_status" -ne 0 ] && printf '%s' "$footprint_output" | grep -Fq "outside-repo output rule is missing"; then
  check_pass "scenario9: in-repo footprint proposal is rejected" 0
else
  printf 'sidecars.test: footprint fixture output: %s\n' "$footprint_output" >&2
  check_pass "scenario9: in-repo footprint proposal is rejected" 1
fi
check_contains "scenario9: external-validity fixture blocks broadening" \
  fixtures/sidecar-contract/external-validity.md "precondition for broadening"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'sidecars.test: FAIL — %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'sidecars.test: ok (%d/%d)\n' "$pass" "$total"
