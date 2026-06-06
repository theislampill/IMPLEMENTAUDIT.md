#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'verify-package: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

require_file() {
  [ -f "$1" ] || fail "missing required file: $1"
}

if [ -e IMPLEMENTAUDIT.md ]; then
  fail "root IMPLEMENTAUDIT.md must be absent; canonical behavior lives in skills/SKILL.md"
fi
require_file AGENTS.md
require_file README.md
require_file CHANGELOG.md
require_file CLAUDE.md
require_file CONTRIBUTING.md
require_file .gitattributes
require_file .gitignore
require_file .claude-plugin/plugin.json
require_file .claude-plugin/marketplace.json
require_file scripts/build-release-asset.sh
require_file scripts/check-host-claims.sh
require_file scripts/check-added-lines-clean.sh
require_file scripts/check-marker-order.sh
require_file scripts/check-planner-stages.sh
require_file scripts/check-readme-toc.sh
require_file scripts/check-routing.sh
require_file scripts/generate-readme-diagrams.sh
require_file scripts/install-codex-from-release.sh
require_file scripts/write-release-checksums.sh
require_file skills/SKILL.md
require_file skills/references/planning-depth.md
require_file skills/references/phase-design.md
require_file skills/references/goal-format.md
require_file skills/references/transcript-contract.md
require_file skills/references/routing.md
require_file skills/references/repo-state-comparison.md
require_file skills/references/child-agents.md
require_file skills/scripts/detect-env.sh
require_file skills/scripts/detect-stack.sh
require_file skills/scripts/repo-state.sh
require_file skills/scripts/summarize-repo.sh
require_file skills/scripts/validate-audit-spec.sh
require_file skills/scripts/validate-phase.sh
require_file skills/templates/ROADMAP.md
require_file skills/templates/STATE.md
require_file skills/templates/THINKING.md
require_file skills/templates/phase-goal.txt
require_file skills/templates/child-agent-report.md
require_file skills/templates/PROTOCOL.md
require_file fixtures/simple-audit/AUDIT.md
require_file fixtures/simple-audit/EXPECTED-LEDGER.md
require_file fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md
require_file fixtures/zero-optional-tool/COMPLETE-RUN.md
require_file fixtures/routing/greenfield-goal-synthesis/INPUT.md
require_file fixtures/routing/greenfield-goal-synthesis/EXPECTED.md
require_file fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md
require_file fixtures/routing/brownfield-audit-closure/INPUT.md
require_file fixtures/routing/brownfield-audit-closure/EXPECTED.md
require_file fixtures/routing/brownfield-audit-closure/INVALID-MUTATION-FIRST.md
require_file fixtures/routing/mixed-greenfield-in-brownfield/INPUT.md
require_file fixtures/routing/mixed-greenfield-in-brownfield/EXPECTED.md
require_file fixtures/audit-spec/valid-mixed.md
require_file fixtures/audit-spec/invalid-missing-owner.md
require_file fixtures/audit-spec/invalid-missing-rollback.md
require_file fixtures/audit-spec/invalid-missing-evidence.md
require_file fixtures/audit-spec/invalid-missing-generated-plan.md
require_file fixtures/audit-spec/invalid-missing-release-boundary.md
require_file fixtures/child-agents/AGENTS.md
require_file fixtures/child-agents/README.md
require_file fixtures/child-agents/read-only-contract-auditor.md
require_file fixtures/child-agents/adversarial-behavioral-auditor.md
require_file fixtures/child-agents/read-only-contract-auditor-report.md
require_file fixtures/child-agents/adversarial-behavioral-auditor-report.md
require_file fixtures/child-agents/normalized-findings-ledger.md
require_file docs/diagrams/tooling-architecture.mmd
require_file docs/diagrams/invocation-modes.mmd
require_file docs/diagrams/execution-spine.mmd
require_file docs/audits/INDEX.md
require_file docs/audits/v0.2.3.0-harness-adaptation-matrix.md
require_file docs/audits/v0.2.4.0-planner-stage-hardening.md
require_file tests/marker-order.test.sh
require_file tests/planner-stages.test.sh
require_file tests/release-asset.test.sh
require_file tests/release-asset-install.test.sh
require_file tests/install-copy-smoke.test.sh
require_file tests/routing.test.sh
require_file tests/repo-state.test.sh
require_file tests/audit-spec.test.sh
require_file tests/added-lines-clean.test.sh
require_file .github/workflows/validate.yml

for child_report in \
  skills/templates/child-agent-report.md \
  fixtures/child-agents/read-only-contract-auditor.md \
  fixtures/child-agents/adversarial-behavioral-auditor.md \
  fixtures/child-agents/read-only-contract-auditor-report.md \
  fixtures/child-agents/adversarial-behavioral-auditor-report.md
do
  grep -q "Verdict:" "$child_report" || fail "child-agent report missing Verdict section: $child_report"
  grep -q "Files inspected:" "$child_report" || fail "child-agent report missing Files inspected section: $child_report"
  grep -q "Commands run:" "$child_report" || fail "child-agent report missing Commands run section: $child_report"
  grep -q "Andon registration check:" "$child_report" || fail "child-agent report missing Andon registration check section: $child_report"
  grep -q "Required patches" "$child_report" || fail "child-agent report missing Required patches section: $child_report"
  grep -q "Required fixtures / canaries" "$child_report" || fail "child-agent report missing Required fixtures / canaries section: $child_report"
  grep -q "What closes" "$child_report" || fail "child-agent report missing What closes section: $child_report"
  grep -q "What remains" "$child_report" || fail "child-agent report missing What remains section: $child_report"
  grep -q "Next smallest safe action" "$child_report" || fail "child-agent report missing Next smallest safe action section: $child_report"
done

grep -q "Andon registration invariant" skills/references/child-agents.md || fail "child-agent Andon registration invariant is missing"
grep -q "superseded for release proof" skills/references/child-agents.md || fail "child-agent false-green rerun rule is missing"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required for JSON validation"
fi

"${py_cmd[@]}" -m json.tool .claude-plugin/plugin.json >/dev/null
"${py_cmd[@]}" -m json.tool .claude-plugin/marketplace.json >/dev/null

"${py_cmd[@]}" - <<'PY'
import json
from pathlib import Path

plugin = json.loads(Path(".claude-plugin/plugin.json").read_text())
if plugin.get("name") != "implementaudit":
    raise SystemExit("plugin name must be implementaudit")
if plugin.get("skills") != "./skills/":
    raise SystemExit("plugin skills path must be ./skills/")
if not plugin.get("version"):
    raise SystemExit("plugin version is required")
if plugin.get("version") != "0.2.4":
    raise SystemExit("plugin version must be 0.2.4 for project milestone v0.2.4.0")

marketplace = json.loads(Path(".claude-plugin/marketplace.json").read_text())
plugins = marketplace.get("plugins")
if not isinstance(plugins, list) or not plugins:
    raise SystemExit("marketplace plugins list is required")
if plugins[0].get("path") != "..":
    raise SystemExit("marketplace path should point at plugin root")
PY

for marker in \
  Self-critique: \
  PREFLIGHT_GREEN \
  PREFLIGHT_RED \
  IMPLEMENTAUDIT_PHASE_START \
  IMPLEMENTAUDIT_PHASE_VERIFY \
  AGENTS_UPDATE_DECISION \
  IMPLEMENTAUDIT_PHASE_DONE \
  FAILURE_PROBE \
  FAILURE_ESCALATE \
  FAILURE_HANDOFF \
  AUDIT_START \
  AUDIT_VERIFY \
  AUDIT_GAPS \
  AUDIT_COMPLETE \
  AUDIT_HANDOFF \
  IMPLEMENTAUDIT_RUN_COMPLETE
do
  grep -R "$marker" -n skills >/dev/null || fail "missing transcript marker: $marker"
done

grep -R "\.IMPLEMENTAUDIT" -n skills README.md AGENTS.md >/dev/null || fail ".IMPLEMENTAUDIT runtime path is not documented"
grep -R "child-agent reports are review evidence only" -in skills README.md AGENTS.md fixtures >/dev/null || fail "child-agent evidence boundary is missing"
grep -R "AUDIT_HANDOFF.*conditional\|AUDIT_HANDOFF.*handoff path" -in skills AGENTS.md >/dev/null || fail "AUDIT_HANDOFF conditional boundary is missing"
grep -R "AGENTS_UPDATE_DECISION" -n skills/templates/phase-goal.txt skills/templates/STATE.md >/dev/null || fail "AGENTS_UPDATE_DECISION template coverage is missing"
grep -R "Stage 0 - Context/tool/repo-state detection" -n skills/SKILL.md >/dev/null || fail "native Stage 0 planner contract is missing from skills/SKILL.md"
grep -R "Stage 6.5 - Pre-flight smoke" -n skills/SKILL.md >/dev/null || fail "native Stage 6.5 planner contract is missing from skills/SKILL.md"
grep -R ".IMPLEMENTAUDIT/THINKING.md" -n skills/SKILL.md skills/templates/THINKING.md skills/templates/PROTOCOL.md >/dev/null || fail "THINKING runtime artifact coverage is missing"
grep -R "install-codex-from-release.sh" -n README.md AGENTS.md scripts tests >/dev/null || fail "release-asset Codex install path is not documented/validated"
grep -R "stale checksum" -in tests/release-asset-install.test.sh scripts/install-codex-from-release.sh >/dev/null || fail "stale checksum install failure coverage is missing"
grep -R "auto-update" -in README.md CHANGELOG.md AGENTS.md | grep -i "no marketplace auto-update\|does not auto-update\|do not assume\|do not claim" >/dev/null || fail "auto-update boundary must remain explicit"
grep -R "v0.2.4.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.4.0 is not documented"
grep -R "v0.2.3.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.3.0 is not documented"
grep -R "v0.2.2.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.2.0 history is not documented"
grep -R "v0.2.1.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.1.0 history is not documented"
grep -R "v0.2.0.0" -n CHANGELOG.md README.md AGENTS.md >/dev/null || fail "project milestone v0.2.0.0 history is not documented"
grep -R "v0.1.0" -n CHANGELOG.md >/dev/null || fail "reconstructed v0.1.0 changelog entry missing"
grep -R "v0.0.1" -n CHANGELOG.md >/dev/null || fail "reconstructed v0.0.1 changelog entry missing"

if grep -R -n -I --exclude-dir=.git --exclude=verify-package.sh \
  -e "read root IMPLEMENTAUDIT.md" \
  -e "read .*IMPLEMENTAUDIT.md.*behavior source" \
  -e "IMPLEMENTAUDIT.md remains the compatibility root" \
  -e "IMPLEMENTAUDIT.md and skills/SKILL.md" \
  -e "IMPLEMENTAUDIT.md remains synced" \
  . >/tmp/implementaudit-root-file-claim.txt; then
  cat /tmp/implementaudit-root-file-claim.txt >&2
  rm -f /tmp/implementaudit-root-file-claim.txt
  fail "repo docs/checkers must not direct agents to root IMPLEMENTAUDIT.md as a behavior source"
fi
rm -f /tmp/implementaudit-root-file-claim.txt

grep -R "skills/SKILL.md" -n README.md AGENTS.md CHANGELOG.md >/dev/null || fail "canonical skills/SKILL.md behavior source is not documented"

legacy_a="Super"
legacy_b="goal"
legacy_name="${legacy_a}${legacy_b}"
legacy_dir=".${legacy_name,,}"
if grep -R -n -I --exclude-dir=.git -e "$legacy_name" -e "$legacy_dir" . >/tmp/implementaudit-forbidden-grep.txt; then
  cat /tmp/implementaudit-forbidden-grep.txt >&2
  rm -f /tmp/implementaudit-forbidden-grep.txt
  fail "forbidden legacy planner name appears in repo files"
fi
rm -f /tmp/implementaudit-forbidden-grep.txt

child_upper_a="CHILD"
child_upper_b="AGENTS"
child_lower_a="child"
child_lower_b="agents"
child_upper_name="${child_upper_a}_${child_upper_b}"
child_lower_name="${child_lower_a}_${child_lower_b}"
if grep -R -n -I --exclude-dir=.git -e "$child_upper_name" -e "$child_lower_name" . >/tmp/implementaudit-child-agents-grep.txt; then
  cat /tmp/implementaudit-child-agents-grep.txt >&2
  rm -f /tmp/implementaudit-child-agents-grep.txt
  fail "nonstandard child-agent instruction filename claim appears in repo files"
fi
rm -f /tmp/implementaudit-child-agents-grep.txt

grep -R "Graphify output is orientation evidence, not proof" -n skills README.md AGENTS.md >/dev/null || fail "Graphify proof boundary is missing"
grep -R "ActiveGraph custody is not correctness proof" -n skills README.md AGENTS.md >/dev/null || fail "ActiveGraph proof boundary is missing"

bash scripts/generate-readme-diagrams.sh --check
bash scripts/check-readme-toc.sh
bash scripts/check-planner-stages.sh
bash scripts/check-marker-order.sh fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md fixtures/zero-optional-tool/COMPLETE-RUN.md
bash scripts/check-routing.sh
bash scripts/check-host-claims.sh
bash scripts/check-added-lines-clean.sh HEAD
bash tests/marker-order.test.sh
bash tests/planner-stages.test.sh
bash tests/release-asset.test.sh
bash tests/release-asset-install.test.sh
bash tests/install-copy-smoke.test.sh
bash tests/routing.test.sh
bash tests/repo-state.test.sh
bash tests/audit-spec.test.sh
bash tests/added-lines-clean.test.sh
bash scripts/build-release-asset.sh --check

git diff --check

printf 'verify-package: ok\n'
