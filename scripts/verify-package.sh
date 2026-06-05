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

require_file IMPLEMENTAUDIT.md
require_file AGENTS.md
require_file README.md
require_file CHANGELOG.md
require_file CLAUDE.md
require_file CONTRIBUTING.md
require_file .gitignore
require_file .claude-plugin/plugin.json
require_file .claude-plugin/marketplace.json
require_file skills/SKILL.md
require_file skills/references/planning-depth.md
require_file skills/references/phase-design.md
require_file skills/references/goal-format.md
require_file skills/references/child-agents.md
require_file skills/scripts/detect-env.sh
require_file skills/scripts/detect-stack.sh
require_file skills/scripts/summarize-repo.sh
require_file skills/scripts/validate-phase.sh
require_file skills/templates/ROADMAP.md
require_file skills/templates/STATE.md
require_file skills/templates/phase-goal.txt
require_file skills/templates/child-agent-report.md
require_file skills/templates/PROTOCOL.md
require_file fixtures/simple-audit/AUDIT.md
require_file fixtures/simple-audit/EXPECTED-LEDGER.md
require_file fixtures/child-agents/AGENTS.md
require_file fixtures/child-agents/read-only-contract-auditor-report.md
require_file fixtures/child-agents/adversarial-behavioral-auditor-report.md
require_file fixtures/child-agents/normalized-findings-ledger.md

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
if plugin.get("version") != "0.2.0":
    raise SystemExit("plugin version must be 0.2.0 for project milestone v0.2.0.0")

marketplace = json.loads(Path(".claude-plugin/marketplace.json").read_text())
plugins = marketplace.get("plugins")
if not isinstance(plugins, list) or not plugins:
    raise SystemExit("marketplace plugins list is required")
if plugins[0].get("path") != "..":
    raise SystemExit("marketplace path should point at plugin root")
PY

cmp -s IMPLEMENTAUDIT.md skills/SKILL.md || fail "IMPLEMENTAUDIT.md and skills/SKILL.md are out of sync"

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
  grep -R "$marker" -n skills IMPLEMENTAUDIT.md >/dev/null || fail "missing transcript marker: $marker"
done

grep -R "\.IMPLEMENTAUDIT" -n skills IMPLEMENTAUDIT.md README.md AGENTS.md >/dev/null || fail ".IMPLEMENTAUDIT runtime path is not documented"
grep -R "child-agent reports are review evidence only" -in skills README.md AGENTS.md fixtures >/dev/null || fail "child-agent evidence boundary is missing"
grep -R "AUDIT_HANDOFF.*conditional\|AUDIT_HANDOFF.*handoff path" -in skills IMPLEMENTAUDIT.md AGENTS.md >/dev/null || fail "AUDIT_HANDOFF conditional boundary is missing"
grep -R "AGENTS_UPDATE_DECISION" -n skills/templates/phase-goal.txt skills/templates/STATE.md >/dev/null || fail "AGENTS_UPDATE_DECISION template coverage is missing"
grep -R "v0.2.0.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.0.0 is not documented"
grep -R "v0.1.0" -n CHANGELOG.md >/dev/null || fail "reconstructed v0.1.0 changelog entry missing"
grep -R "v0.0.1" -n CHANGELOG.md >/dev/null || fail "reconstructed v0.0.1 changelog entry missing"
if grep -n -i -E "verified release|released on|tagged v|published package|package publication verified|marketplace verified|provenance generated" CHANGELOG.md >/tmp/implementaudit-changelog-claims.txt; then
  cat /tmp/implementaudit-changelog-claims.txt >&2
  rm -f /tmp/implementaudit-changelog-claims.txt
  fail "CHANGELOG.md contains an unsupported release/publication/provenance claim"
fi
rm -f /tmp/implementaudit-changelog-claims.txt

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

grep -R "Graphify output is orientation evidence, not proof" -n skills IMPLEMENTAUDIT.md README.md AGENTS.md >/dev/null || fail "Graphify proof boundary is missing"
grep -R "ActiveGraph custody is not correctness proof" -n skills IMPLEMENTAUDIT.md README.md AGENTS.md >/dev/null || fail "ActiveGraph proof boundary is missing"

git diff --check

printf 'verify-package: ok\n'
