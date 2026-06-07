#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-sidecar-boundaries: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

require_file() {
  [ -f "$1" ] || fail "missing required file: $1"
}

require_file skills/SKILL.md
require_file skills/templates/THINKING.md
require_file skills/templates/PROTOCOL.md
require_file skills/templates/phase-goal.txt
require_file scripts/build-release-asset.sh
require_file tests/release-asset-install.test.sh

grep -R "Graphify output is orientation evidence, not proof" -n skills/SKILL.md skills/references skills/templates >/dev/null ||
  fail "Graphify orientation-only boundary is missing"
grep -R "ActiveGraph custody is not correctness proof" -n skills/SKILL.md skills/references skills/templates >/dev/null ||
  fail "ActiveGraph custody-only boundary is missing"
grep -R "Markdown fallback" -n skills README.md AGENTS.md >/dev/null ||
  fail "Markdown fallback boundary is missing"
grep -R "no install, indexing, setup, config, export" -in skills README.md AGENTS.md >/dev/null ||
  fail "sidecar authorization boundary is missing"
grep -R "Graphify status" -n skills/templates/THINKING.md skills/templates/STATE.md >/dev/null ||
  fail "Graphify runtime status field is missing"
grep -R "ActiveGraph status" -n skills/templates/THINKING.md skills/templates/STATE.md >/dev/null ||
  fail "ActiveGraph runtime status field is missing"
grep -R "sidecars.md" -n skills/SKILL.md skills/templates README.md AGENTS.md >/dev/null ||
  fail "sidecars.md runtime artifact is missing"
grep -R "graph.json" -n scripts/build-release-asset.sh tests/release-asset-install.test.sh >/dev/null ||
  fail "release asset sidecar debris rejection is missing"
grep -R "quickstart_demo_run.db" -n scripts/build-release-asset.sh tests/release-asset-install.test.sh >/dev/null ||
  fail "ActiveGraph store rejection is missing"

if [ -d graphify-out ] || [ -d .graphify ] || [ -d .activegraph ]; then
  fail "repo-local sidecar output/store directory exists"
fi

printf 'check-sidecar-boundaries: ok\n'
