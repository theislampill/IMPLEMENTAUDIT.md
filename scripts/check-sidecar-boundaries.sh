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

require_literal() {
  local path="$1"
  local literal="$2"
  local label="$3"
  grep -Fq -- "$literal" "$path" || fail "$label is missing from $path"
}

forbid_literal() {
  local path="$1"
  local literal="$2"
  local label="$3"
  if grep -Fq -- "$literal" "$path"; then
    fail "$label remains in $path"
  fi
}

if [ "${1:-}" = "--evaluate-fixture" ]; then
  [ "$#" -eq 2 ] || fail "usage: check-sidecar-boundaries.sh --evaluate-fixture <fixture>"
  fixture="$2"
  require_file "$fixture"
  if grep -Fq -- "Fixture kind: graphify-routing" "$fixture"; then
    require_literal "$fixture" "Proposed action: Graphify query" "Graphify proposal"
    require_literal "$fixture" "Repository: unfamiliar" "unfamiliar-repo trigger"
    require_literal "$fixture" "Repository shape: majority-code" "majority-code trigger"
    require_literal "$fixture" "Question shape: terrain-shaped" "terrain-shaped trigger"
    require_literal "$fixture" "One-search answer: no" "one-search anti-trigger"
    exit 0
  fi
  if grep -Fq -- "Fixture kind: graphify-footprint" "$fixture"; then
    require_literal "$fixture" "Output: outside-target-repo" "outside-repo output rule"
    require_literal "$fixture" "Tracked ignore edit: no" "no-ignore-edit rule"
    exit 0
  fi
  fail "unknown sidecar contract fixture: $fixture"
fi

require_file skills/implementaudit/SKILL.md
require_file skills/implementaudit/templates/THINKING.md
require_file skills/implementaudit/templates/PROTOCOL.md
require_file skills/implementaudit/templates/phase-goal.txt
require_file skills/implementaudit/templates/sidecars.md
require_file skills/implementaudit/references/sidecars.md
require_file skills/implementaudit/references/lean-operating-discipline.md
require_file skills/implementaudit/references/routing.md
require_file skills/implementaudit/scripts/validate-run-root.sh
require_file CONTRIBUTING.md
require_file docs/portal/pages/optional-tooling.html
require_file docs/portal/pages/continuity-and-sidecars.html
require_file docs/portal/pages/for-auditors-and-maintainers.html
require_file docs/portal/pages/state-and-artifacts.html
require_file docs/portal/pages/package-contents.html
require_file docs/portal/pages/completion-semantics.html
require_file docs/portal/pages/terminology.html
require_file docs/portal/pages/audit-gate-model.html
require_file docs/portal/pages/evidence-boundaries.html
require_file docs/portal/pages/reference-index.html
require_file docs/portal/pages/routing.html
require_file docs/portal/pages/what-it-is.html
require_file scripts/build-release-asset.sh
require_file tests/release-asset-install.test.sh

grep -R "Graphify output is orientation evidence, not proof" -n skills/implementaudit/SKILL.md skills/implementaudit/references skills/implementaudit/templates >/dev/null ||
  fail "Graphify orientation-only boundary is missing"
grep -R "ActiveGraph custody is not correctness proof" -n skills/implementaudit/SKILL.md skills/implementaudit/references skills/implementaudit/templates >/dev/null ||
  fail "ActiveGraph custody-only boundary is missing"
grep -R "Markdown fallback" -n skills README.md AGENTS.md >/dev/null ||
  fail "Markdown fallback boundary is missing"
require_literal skills/implementaudit/SKILL.md "Graphify output is orientation evidence, not proof. ActiveGraph custody is not correctness proof. Sidecars are optional unless a repo says otherwise; their presence authorizes no install, indexing, setup, config, export, or sidecar mutation." "compressed spine sidecar boundary"
grep -R "no install, indexing, setup, config, export" -in skills README.md AGENTS.md >/dev/null ||
  fail "sidecar authorization boundary is missing"
grep -R "Graphify status" -n skills/implementaudit/templates/THINKING.md skills/implementaudit/templates/STATE.md >/dev/null ||
  fail "Graphify runtime status field is missing"
grep -R "ActiveGraph status" -n skills/implementaudit/templates/THINKING.md skills/implementaudit/templates/STATE.md >/dev/null ||
  fail "ActiveGraph runtime status field is missing"
grep -R "sidecars.md" -n skills/implementaudit/SKILL.md skills/implementaudit/templates README.md AGENTS.md >/dev/null ||
  fail "sidecars.md runtime artifact is missing"

# R27 / #101: every narrowed carrier must preserve the same executable and
# evidence boundary. These exact literals are intentionally mutation-tested.
require_literal skills/implementaudit/references/sidecars.md "terrain-shaped" "Graphify observable trigger"
require_literal skills/implementaudit/references/sidecars.md "built_at_commit" "executable freshness contract"
require_literal skills/implementaudit/references/sidecars.md "--graph-scope" "scoped graph selector"
require_literal skills/implementaudit/references/sidecars.md "--graph-parent" "declared parent broadening"
require_literal skills/implementaudit/references/sidecars.md "extractor/relation-model omission" "relation-model failure class"
require_literal skills/implementaudit/references/sidecars.md "llm: false" "no-LLM scoped contract"
require_literal skills/implementaudit/references/sidecars.md "canonical repo-relative" "canonical scan-root contract"
require_literal skills/implementaudit/references/sidecars.md "manifest.json" "catalogue construction population"
require_literal skills/implementaudit/references/sidecars.md "mtime,ast_hash,semantic_hash" "installed Graphify manifest row schema"
require_literal skills/implementaudit/references/sidecars.md "source_file" "graph population binding"
require_literal skills/implementaudit/references/sidecars.md "ensure_ascii=True" "byte-exact JSON canonicalisation"
require_literal skills/implementaudit/references/sidecars.md "rules_sha256" "scope-rule fingerprint construction"
require_literal skills/implementaudit/references/sidecars.md "scope_sha256" "scope binding construction"
require_literal skills/implementaudit/references/sidecars.md "graph_sha256" "graph digest construction"
require_literal skills/implementaudit/references/sidecars.md "unsupported-config" "unsupported extractor configuration fallback"
require_literal skills/implementaudit/references/sidecars.md "## Privacy and spend" "LLM privacy/spend disclosure"
require_literal skills/implementaudit/references/sidecars.md "filename heuristic" "filename-only privacy limitation"
require_literal skills/implementaudit/references/sidecars.md "unmeasurable spend" "unmeasurable-spend disclosure"
require_literal skills/implementaudit/references/sidecars.md "owner-named backend" "owner-named-backend rule"
require_literal skills/implementaudit/references/sidecars.md "Ollama is explicitly unauthorized" "Ollama refusal"
require_literal skills/implementaudit/references/sidecars.md "owner said Codex, not Ollama" "dated backend precedent"
require_literal skills/implementaudit/references/sidecars.md "unfamiliar third-party repo" "external-validity broadening gate"
require_literal skills/implementaudit/references/sidecars.md "missed-use-detection goal is retired" "missed-use retirement"
require_literal skills/implementaudit/references/lean-operating-discipline.md "dogfood-only" "as-tested dogfood qualification"
require_literal skills/implementaudit/references/lean-operating-discipline.md "module-level constants" "known Graphify limitations"
require_literal skills/implementaudit/references/lean-operating-discipline.md "non-authoritative mirror" "ActiveGraph authority narrowing"
require_literal skills/implementaudit/references/routing.md "reference-shaped" "sidecar anti-trigger routing"
require_literal skills/implementaudit/templates/sidecars.md "git rev-parse HEAD" "sidecar freshness evidence fields"
require_literal skills/implementaudit/templates/sidecars.md "fork / diff" "ActiveGraph checkpoint scope"
require_literal skills/implementaudit/templates/PROTOCOL.md "run root remains the sole authority" "run-root lifecycle authority"
require_literal skills/implementaudit/templates/THINKING.md "Graphify trigger decision" "sidecar planning decision"
require_literal skills/implementaudit/templates/phase-goal.txt "executed SHA match" "phase sidecar freshness status"
require_literal skills/implementaudit/references/plan-lifecycle.md "reference-shaped" "plan diff instrument boundary"
require_literal skills/implementaudit/references/child-agents.md "fork/diff or non-authoritative-mirror" "child sidecar review scope"
require_literal skills/implementaudit/scripts/summarize-repo.sh "optional_checkpoint_or_non_authoritative_mirror" "repo summary sidecar scope"
require_literal skills/implementaudit/scripts/validate-run-root.sh "--graph-freshness" "freshness command"
require_literal skills/implementaudit/scripts/validate-run-root.sh "--graph-scope" "scoped selector command"
require_literal skills/implementaudit/scripts/validate-run-root.sh "--graph-parent" "parent broadening command"
require_literal skills/implementaudit/scripts/validate-run-root.sh "stale-sidecar" "freshness Andon signal"
require_literal README.md "Graphify output is orientation evidence, not proof" "README optional-tool authority summary"
require_literal README.md "ActiveGraph custody is not correctness proof" "README optional-tool custody summary"
require_literal skills/implementaudit/references/sidecars.md "Ollama is explicitly unauthorized" "progressive backend boundary"
require_literal skills/implementaudit/references/sidecars.md "selects smallest fresh" "progressive scoped selection"
require_literal AGENTS.md "non-authoritative mirror" "AGENTS sidecar anti-repeat rule"
require_literal CONTRIBUTING.md "Graphify first-contact terrain" "contributor sidecar summary"
require_literal docs/portal/pages/optional-tooling.html "owner-named backend" "portal privacy/backend disclosure"
require_literal docs/portal/pages/optional-tooling.html "--graph-scope" "portal scoped selector"
require_literal docs/portal/pages/optional-tooling.html "does not qualify semantic/Luna behaviour" "portal semantic boundary"
require_literal docs/portal/pages/continuity-and-sidecars.html "stale-sidecar" "portal freshness summary"
require_literal docs/portal/pages/continuity-and-sidecars.html "ActiveGraph mirror remains secondary" "portal continuity authority"
require_literal docs/portal/pages/for-auditors-and-maintainers.html "optional non-authoritative mirror" "auditor portal sidecar boundary"
require_literal docs/portal/pages/state-and-artifacts.html "Graphify trigger/freshness evidence" "state portal sidecar artifact"
require_literal docs/portal/pages/package-contents.html "ActiveGraph checkpoint/mirror state" "package portal sidecar artifact"
require_literal docs/portal/pages/completion-semantics.html "ActiveGraph correctness or lifecycle proof" "completion portal sidecar boundary"
require_literal docs/portal/pages/terminology.html "optional terrain/checkpoint context" "terminology portal sidecar boundary"
require_literal docs/portal/pages/audit-gate-model.html "checkpoint assistance or an optional mirror" "audit-gate portal sidecar boundary"
require_literal docs/portal/pages/evidence-boundaries.html "qualified first-contact orientation" "evidence portal Graphify boundary"
require_literal docs/portal/pages/reference-index.html "ActiveGraph checkpoint/mirror boundaries" "reference index sidecar boundary"
require_literal docs/portal/pages/routing.html "Which anti-trigger, stale signal" "routing portal sidecar boundary"
require_literal docs/portal/pages/what-it-is.html "fork/diff checkpoints or mirror run-root events" "overview portal sidecar boundary"

forbid_literal skills/implementaudit/references/sidecars.md "stale output triggers Andon or fallback" "unexecuted staleness promise"
forbid_literal skills/implementaudit/references/lean-operating-discipline.md "Stale output triggers Andon or fallback" "third staleness promise"
forbid_literal skills/implementaudit/templates/sidecars.md "| Freshness |" "hand-filled per-query freshness"
forbid_literal skills/implementaudit/references/lean-operating-discipline.md "record these events" "mandatory custody catalogue"
forbid_literal skills/implementaudit/templates/PROTOCOL.md "replay reconstructs causality" "unsupported replay claim"
if grep -R -Ei "canonical proof unless|promotes? .*proof|proof .*unless.*sidecar" \
  skills/implementaudit/SKILL.md skills/implementaudit/references skills/implementaudit/templates README.md AGENTS.md docs/portal/pages >/dev/null; then
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
