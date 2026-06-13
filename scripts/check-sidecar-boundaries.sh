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
if grep -R -Ei "canonical proof unless|promotes? .*proof|proof .*unless.*sidecar" \
  skills/SKILL.md skills/references skills/templates README.md AGENTS.md docs/portal/pages >/dev/null; then
  fail "sidecar proof-promotion wording is present"
fi
grep -R "graph.json" -n scripts/build-release-asset.sh tests/release-asset-install.test.sh >/dev/null ||
  fail "release asset sidecar debris rejection is missing"
grep -R "quickstart_demo_run.db" -n scripts/build-release-asset.sh tests/release-asset-install.test.sh >/dev/null ||
  fail "ActiveGraph store rejection is missing"

# The boundary (V0270-SIDECAR-OUTPUTS-EXCLUDED) is tracked source and the
# .skill package — not local existence. Sidecars are canonical for dogfooding
# this repo, so gitignored local terrain/custody may persist; what must never
# happen is sidecar output becoming tracked or losing its ignore cover.
tracked_sidecar="$(git ls-files -- 'graphify-out/*' '.graphify/*' '.activegraph/*' '*custody*.jsonl' '*custody.db' '*.activegraph.db' 2>/dev/null | head -5 || true)"
if [ -n "$tracked_sidecar" ]; then
  fail "sidecar output is tracked by git: $tracked_sidecar"
fi
for d in graphify-out .graphify .activegraph; do
  if [ -d "$d" ] && ! git check-ignore -q "$d" 2>/dev/null; then
    fail "sidecar directory $d exists but is not gitignored"
  fi
done

printf 'check-sidecar-boundaries: ok\n'
