#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'sidecars.test: python, python3, or py -3 is required\n' >&2
  exit 2
fi

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
  "$tmp/skills/implementaudit/SKILL.md" \
  "$tmp/skills/implementaudit/references/sidecars.md" \
  "$tmp/skills/implementaudit/templates/sidecars.md"
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
trap 'rm -rf "$tmp" "$tmp_spine" "$tmp_promote" "$tmp_contract" "${scope_tmp:-}"' EXIT
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
check_contains "scenario9: smallest scope selector documented" "$sidecar_ref" "--graph-scope"
check_contains "scenario9: declared parent broadening documented" "$sidecar_ref" "--graph-parent"
check_contains "scenario9: no-LLM catalogue boundary documented" "$sidecar_ref" "llm: false"
check_contains "scenario9: relation omission classification documented" "$sidecar_ref" "extractor/relation-model omission"
check_contains "scenario9: graph source population binding documented" "$sidecar_ref" 'source_file'
check_contains "scenario9: installed manifest row schema documented" "$sidecar_ref" 'mtime,ast_hash,semantic_hash'
check_contains "scenario9: JSON canonicalisation is byte-exact" "$sidecar_ref" 'ensure_ascii=True'
for failure_class in stale-graph wrong-or-overbroad-scope cross-scope extractor-relation-omission semantic-LLM-not-retained; do
  check_contains "scenario9: failure class $failure_class is explicit" "$thinking_template" "$failure_class"
done
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
# Scenario 10: scoped catalogue selection and scope-local freshness
# ---------------------------------------------------------------------------
scope_tmp="$(mktemp -d)"
scope_repo="$scope_tmp/repo"
mkdir -p "$scope_repo/runtime" "$scope_repo/release" "$scope_repo/docs" \
  "$scope_tmp/graphs"
printf 'ignored/\n' >"$scope_repo/.gitignore"
printf '#!/usr/bin/env bash\nprintf runtime\\n' >"$scope_repo/runtime/runner.sh"
printf '#!/usr/bin/env bash\nprintf release\\n' >"$scope_repo/release/build.sh"
printf 'public docs\n' >"$scope_repo/docs/readme.md"
printf '{"nodes":[{"id":"runtime","source_file":"runner.sh"}],"links":[]}\n' >"$scope_tmp/graphs/runtime.json"
printf '{"nodes":[{"id":"release","source_file":"build.sh"}],"links":[]}\n' >"$scope_tmp/graphs/release.json"
printf '{"nodes":[{"id":"ignore","source_file":".gitignore"},{"id":"docs","source_file":"docs/readme.md"},{"id":"release","source_file":"release/build.sh"},{"id":"runtime","source_file":"runtime/runner.sh"}],"links":[]}\n' >"$scope_tmp/graphs/root.json"
git -C "$scope_repo" init -q
git -C "$scope_repo" config user.name fixture
git -C "$scope_repo" config user.email fixture@example.invalid
git -C "$scope_repo" add .
git -C "$scope_repo" commit -qm fixture

"${py_cmd[@]}" - "$scope_repo" "$scope_tmp" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path

repo, out = map(Path, sys.argv[1:])
head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
tracked = subprocess.check_output(["git", "-C", str(repo), "ls-files"], text=True).splitlines()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def config(root):
    parts = () if root == "." else Path(root).parts
    dirs = [repo.joinpath(*parts[:i]) for i in range(len(parts) + 1)]
    return {str((d / n).relative_to(repo)).replace("\\", "/"): digest(d / n) if (d / n).is_file() else None
            for d in dirs for n in (".graphifyignore", ".gitignore", ".graphifyinclude")}

def scope(name, root, include, files, graph, parent=None):
    exclude = []
    return {
        "name": name,
        "graph": str((out / "graphs" / graph).resolve()),
        "graph_sha256": digest(out / "graphs" / graph),
        "parent": parent,
        "root": root,
        "include": include,
        "exclude": exclude,
        "file_count": len(files),
        "files": {p: digest(repo / p) for p in sorted(files)},
        "config": dict(sorted(config(root).items())),
        "build": {
            "commit": head,
            "tool": "graphify",
            "version": "0.8.37",
            "mode": "clustered-no-llm",
            "llm": False,
            "rules_sha256": hashlib.sha256(json.dumps(
                [sorted(include), sorted(exclude)], separators=(",", ":")).encode()).hexdigest(),
        },
    }

payload = {
    "schema": 1,
    "scopes": [
        scope("runtime", "runtime", ["runtime/**"], ["runtime/runner.sh"], "runtime.json", "root"),
        scope("release", "release", ["release/**"], ["release/build.sh"], "release.json", "root"),
        scope("root", ".", ["**"], tracked, "root.json"),
    ],
}
(out / "catalog.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

scope_helper="skills/implementaudit/scripts/validate-run-root.sh"
scope_catalog="$scope_tmp/catalog.json"

scope_expect_pass() {
  local label="$1" expected="$2"
  shift 2
  local output status
  set +e
  output="$(bash "$scope_helper" "$@" 2>&1)"
  status=$?
  set -e
  if [ "$status" -eq 0 ] && printf '%s' "$output" | grep -Fq "graph-scope: $expected "; then
    check_pass "$label" 0
  else
    printf 'sidecars.test: %s output: %s\n' "$label" "$output" >&2
    check_pass "$label" 1
  fi
}

scope_expect_fail() {
  local label="$1" expected="$2"
  shift 2
  local output status
  set +e
  output="$(bash "$scope_helper" "$@" 2>&1)"
  status=$?
  set -e
  if [ "$status" -ne 0 ] && printf '%s' "$output" | grep -Fq "$expected"; then
    check_pass "$label" 0
  else
    printf 'sidecars.test: %s output: %s\n' "$label" "$output" >&2
    check_pass "$label" 1
  fi
}

scope_rebind() {
  "${py_cmd[@]}" - "$1" <<'PY'
import hashlib, json, sys
from pathlib import Path

catalog = Path(sys.argv[1])
payload = json.loads(catalog.read_text(encoding="utf-8"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def binding(row):
    build = {k: row["build"][k] for k in (
        "commit", "tool", "version", "mode", "llm", "rules_sha256")}
    contract = {
        "name": row["name"],
        "parent": row.get("parent"),
        "root": row["root"],
        "include": row["include"],
        "exclude": row["exclude"],
        "file_count": row["file_count"],
        "files": row["files"],
        "config": row["config"],
        "build": build,
    }
    return hashlib.sha256(json.dumps(
        contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

for row in payload["scopes"]:
    row["files"] = {k: row["files"][k] for k in sorted(row["files"])}
    row["file_count"] = len(row["files"])
    scope_sha = binding(row)
    row["build"]["scope_sha256"] = scope_sha
    source = Path(row["graph"])
    graph = json.loads(source.read_text(encoding="utf-8"))
    graph.setdefault("graph", {})["implementaudit_scope_sha256"] = scope_sha
    target = catalog.parent / "graphs" / f"{catalog.stem}-{row['name']}.json"
    target.write_text(json.dumps(graph, separators=(",", ":")) + "\n", encoding="utf-8")
    row["graph"] = str(target.resolve())
    row["graph_sha256"] = digest(target)

catalog.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
}

scope_rehash_catalog_only() {
  "${py_cmd[@]}" - "$1" <<'PY'
import hashlib, json, sys
from pathlib import Path

catalog = Path(sys.argv[1])
payload = json.loads(catalog.read_text(encoding="utf-8"))
for row in payload["scopes"]:
    row["files"] = {k: row["files"][k] for k in sorted(row["files"])}
    row["file_count"] = len(row["files"])
    build = {k: row["build"][k] for k in (
        "commit", "tool", "version", "mode", "llm", "rules_sha256")}
    contract = {
        "name": row["name"],
        "parent": row.get("parent"),
        "root": row["root"],
        "include": row["include"],
        "exclude": row["exclude"],
        "file_count": row["file_count"],
        "files": row["files"],
        "config": row["config"],
        "build": build,
    }
    row["build"]["scope_sha256"] = hashlib.sha256(json.dumps(
        contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
catalog.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
}

scope_rebind "$scope_catalog"

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/non-ascii-canonical.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
next(row for row in p["scopes"] if row["name"] == "runtime")["build"]["mode"] = "café"
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False))
PY
scope_rebind "$scope_tmp/non-ascii-canonical.json"
scope_expect_pass "scenario10: documented ASCII JSON canonicalisation is reproducible" runtime \
  --graph-scope "$scope_tmp/non-ascii-canonical.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_tmp/non-ascii-canonical.json" \
  "$scope_tmp/non-ascii-wrong-canonical.json" <<'PY'
import hashlib, json, sys
from pathlib import Path
p = json.load(open(sys.argv[1], encoding="utf-8"))
row = next(row for row in p["scopes"] if row["name"] == "runtime")
build = {k: row["build"][k] for k in (
    "commit", "tool", "version", "mode", "llm", "rules_sha256")}
contract = {k: row[k] for k in (
    "name", "parent", "root", "include", "exclude", "file_count", "files", "config")}
contract["build"] = build
wrong = hashlib.sha256(json.dumps(
    contract, sort_keys=True, separators=(",", ":"), ensure_ascii=False
).encode()).hexdigest()
row["build"]["scope_sha256"] = wrong
graph = json.load(open(row["graph"], encoding="utf-8"))
graph["graph"]["implementaudit_scope_sha256"] = wrong
target = Path(sys.argv[2]).with_suffix(".graph.json")
target.write_text(json.dumps(graph, separators=(",", ":")) + "\n", encoding="utf-8")
row["graph"] = str(target.resolve())
row["graph_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False))
PY
scope_expect_fail "scenario10: non-ASCII alternate canonicalisation fails closed" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/non-ascii-wrong-canonical.json" "$scope_repo" runtime/runner.sh

scope_expect_pass "scenario10: unchanged child is selected" runtime \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: uncovered query names wrong or overbroad scope" \
  "graph-route: wrong/overbroad-scope" \
  --graph-scope "$scope_catalog" "$scope_repo" outside/path.sh
scope_expect_fail "scenario10: covered but unindexed path is rejected" \
  "graph-route: wrong/overbroad-scope" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/missing.sh

printf 'unrelated dirty docs\n' >>"$scope_repo/docs/readme.md"
scope_expect_pass "scenario10: unrelated change does not stale child" runtime \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
git -C "$scope_repo" checkout -q -- docs/readme.md

printf 'changed\n' >>"$scope_repo/runtime/runner.sh"
scope_expect_fail "scenario10: indexed change stales child" \
  "stale-sidecar: changed runtime/runner.sh" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
git -C "$scope_repo" checkout -q -- runtime/runner.sh

mv "$scope_repo/runtime/runner.sh" "$scope_tmp/runner.saved"
scope_expect_fail "scenario10: indexed deletion stales child" \
  "stale-sidecar: deleted runtime/runner.sh" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
mv "$scope_tmp/runner.saved" "$scope_repo/runtime/runner.sh"

printf '#!/usr/bin/env bash\n' >"$scope_repo/runtime/new.sh"
scope_expect_fail "scenario10: new in-scope file stales child" \
  "stale-sidecar: new runtime/new.sh" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: a new queried path is classified as stale" \
  "stale-sidecar: new runtime/new.sh" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/new.sh
rm "$scope_repo/runtime/new.sh"

printf '#!/usr/bin/env bash\n' >"$scope_repo/runtime/rules-hidden.sh"
"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/narrowed-rules.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
p["scopes"][0]["include"] = ["runtime/runner.sh"]
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_expect_fail "scenario10: post-build scope-rule narrowing is rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/narrowed-rules.json" "$scope_repo" runtime/runner.sh
rm "$scope_repo/runtime/rules-hidden.sh"

printf '#!/usr/bin/env bash\n' >"$scope_repo/runtime/info-hidden.sh"
printf 'runtime/info-hidden.sh\n' >>"$scope_repo/.git/info/exclude"
scope_expect_fail "scenario10: info-excluded in-scope file still stales child" \
  "stale-sidecar: new runtime/info-hidden.sh" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
rm "$scope_repo/runtime/info-hidden.sh"

printf 'runtime/global-hidden.sh\n' >"$scope_tmp/global-excludes"
git -C "$scope_repo" config core.excludesFile "$scope_tmp/global-excludes"
printf '#!/usr/bin/env bash\n' >"$scope_repo/runtime/global-hidden.sh"
scope_expect_fail "scenario10: global-excluded in-scope file still stales child" \
  "stale-sidecar: new runtime/global-hidden.sh" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
rm "$scope_repo/runtime/global-hidden.sh"
git -C "$scope_repo" config --unset core.excludesFile

printf 'runtime/ignore-*.sh\n' >>"$scope_repo/.gitignore"
printf '#!/usr/bin/env bash\n' >"$scope_repo/runtime/ignore-fallback.sh"
"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/fallback-ignore.json" "$scope_repo" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
digest = hashlib.sha256(open(sys.argv[3] + "/.gitignore", "rb").read()).hexdigest()
for row in p["scopes"]:
    row["config"][".gitignore"] = digest
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rebind "$scope_tmp/fallback-ignore.json"
scope_expect_pass "scenario10: gitignore is the fallback when graphifyignore is absent" runtime \
  --graph-scope "$scope_tmp/fallback-ignore.json" "$scope_repo" runtime/runner.sh

printf 'unrelated-graphify-ignore/\n' >"$scope_repo/.graphifyignore"
printf '#!/usr/bin/env bash\n' >"$scope_repo/runtime/ignore-both.sh"
"${py_cmd[@]}" - "$scope_tmp/fallback-ignore.json" "$scope_tmp/preferred-ignore.json" \
  "$scope_repo" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
p["scopes"][0]["config"][".graphifyignore"] = hashlib.sha256(
    open(sys.argv[3] + "/.graphifyignore", "rb").read()).hexdigest()
for row in p["scopes"][1:]:
    row["config"][".graphifyignore"] = p["scopes"][0]["config"][".graphifyignore"]
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rebind "$scope_tmp/preferred-ignore.json"
scope_expect_fail "scenario10: graphifyignore replaces gitignore when both exist" \
  "stale-sidecar: new runtime/ignore-both.sh" \
  --graph-scope "$scope_tmp/preferred-ignore.json" "$scope_repo" runtime/runner.sh
rm "$scope_repo/.graphifyignore" "$scope_repo/runtime/ignore-fallback.sh" \
  "$scope_repo/runtime/ignore-both.sh"
git -C "$scope_repo" checkout -q -- .gitignore

printf 'runtime/tracked-drop.sh\n' >"$scope_repo/.graphifyignore"
printf '#!/usr/bin/env bash\n' >"$scope_repo/runtime/tracked-drop.sh"
git -C "$scope_repo" add .graphifyignore runtime/tracked-drop.sh
git -C "$scope_repo" commit -qm 'tracked ignored fixture'
"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/tracked-ignore.json" "$scope_repo" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
digest = hashlib.sha256(open(sys.argv[3] + "/.graphifyignore", "rb").read()).hexdigest()
for row in p["scopes"]:
    row["config"][".graphifyignore"] = digest
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rebind "$scope_tmp/tracked-ignore.json"
scope_expect_pass "scenario10: graphify-ignored tracked file stays outside population" runtime \
  --graph-scope "$scope_tmp/tracked-ignore.json" "$scope_repo" runtime/runner.sh
git -C "$scope_repo" rm -q .graphifyignore runtime/tracked-drop.sh
git -C "$scope_repo" commit -qm 'remove tracked ignored fixture'

printf '**/*.py\n' >"$scope_repo/.graphifyignore"
printf 'root level python\n' >"$scope_repo/new.py"
"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/unsupported-ignore.json" "$scope_repo" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
digest = hashlib.sha256(open(sys.argv[3] + "/.graphifyignore", "rb").read()).hexdigest()
for row in p["scopes"]:
    row["config"][".graphifyignore"] = digest
p["scopes"][2]["exclude"].append(".graphifyignore")
row = p["scopes"][2]
row["build"]["rules_sha256"] = hashlib.sha256(json.dumps(
    [sorted(row["include"]), sorted(row["exclude"])], separators=(",", ":")).encode()).hexdigest()
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rebind "$scope_tmp/unsupported-ignore.json"
scope_expect_fail "scenario10: divergent positive double-star ignore fails closed" \
  "stale-sidecar: unsupported-ignore-pattern" \
  --graph-scope "$scope_tmp/unsupported-ignore.json" "$scope_repo" \
  runtime/runner.sh release/build.sh
rm "$scope_repo/.graphifyignore" "$scope_repo/new.py"

mkdir -p "$scope_repo/ignored"
printf '#!/usr/bin/env bash\n' >"$scope_repo/ignored/ignored.sh"
scope_expect_pass "scenario10: ignored new file does not stale child" runtime \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh

printf 'other-ignore/\n' >>"$scope_repo/.gitignore"
scope_expect_fail "scenario10: ignore drift stales child" \
  "stale-sidecar: config-drift .gitignore" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
git -C "$scope_repo" checkout -q -- .gitignore

printf 'runner.sh\n' >"$scope_repo/runtime/.graphifyignore"
"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/scan-root-config.json" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
row = next(row for row in p["scopes"] if row["name"] == "runtime")
row["exclude"].extend(sorted(("runtime/.graphifyignore", "runtime/.gitignore",
                              "runtime/.graphifyinclude")))
row["build"]["rules_sha256"] = hashlib.sha256(json.dumps(
    [row["include"], row["exclude"]], separators=(",", ":")).encode()).hexdigest()
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rebind "$scope_tmp/scan-root-config.json"
scope_expect_fail "scenario10: scan-root ignore drift stales child" \
  "stale-sidecar: config-drift runtime/.graphifyignore" \
  --graph-scope "$scope_tmp/scan-root-config.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_tmp/scan-root-config.json" \
  "$scope_tmp/matching-nested-ignore.json" "$scope_repo/runtime/.graphifyignore" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
row = next(row for row in p["scopes"] if row["name"] == "runtime")
row["config"]["runtime/.graphifyignore"] = hashlib.sha256(open(sys.argv[3], "rb").read()).hexdigest()
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rebind "$scope_tmp/matching-nested-ignore.json"
scope_expect_fail "scenario10: unsupported nested ignore semantics fail closed" \
  "stale-sidecar: unsupported-config runtime/.graphifyignore" \
  --graph-scope "$scope_tmp/matching-nested-ignore.json" "$scope_repo" runtime/runner.sh
rm "$scope_repo/runtime/.graphifyignore"

printf 'runner.sh\n' >"$scope_repo/runtime/.gitignore"
scope_expect_fail "scenario10: scan-root gitignore drift stales child" \
  "stale-sidecar: config-drift runtime/.gitignore" \
  --graph-scope "$scope_tmp/scan-root-config.json" "$scope_repo" runtime/runner.sh
rm "$scope_repo/runtime/.gitignore"

printf '.*\n' >"$scope_repo/runtime/.graphifyinclude"
scope_expect_fail "scenario10: scan-root include drift stales child" \
  "stale-sidecar: config-drift runtime/.graphifyinclude" \
  --graph-scope "$scope_tmp/scan-root-config.json" "$scope_repo" runtime/runner.sh
rm "$scope_repo/runtime/.graphifyinclude"

mkdir "$scope_repo/runtime/.graphifyignore"
scope_expect_fail "scenario10: non-file config carrier fails closed" \
  "stale-sidecar: config-drift runtime/.graphifyignore" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
rmdir "$scope_repo/runtime/.graphifyignore"

scope_expect_pass "scenario10: cross-scope paths select root" root \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh release/build.sh

printf 'parent-only drift\n' >>"$scope_repo/docs/readme.md"
scope_expect_pass "scenario10: fresh child remains usable with stale parent" runtime \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: declared broadening rejects stale parent" \
  "stale-sidecar: changed docs/readme.md" \
  --graph-parent "$scope_catalog" "$scope_repo" runtime cross-scope
git -C "$scope_repo" checkout -q -- docs/readme.md
scope_expect_pass "scenario10: declared parent broadening is ordered" root \
  --graph-parent "$scope_catalog" "$scope_repo" runtime miss

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/restricted-live-parent.json" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
root = next(row for row in p["scopes"] if row["name"] == "root")
root["include"] = [".gitignore", "docs/**", "release/**", "runtime/runner.sh"]
root["build"]["rules_sha256"] = hashlib.sha256(json.dumps(
    [root["include"], root["exclude"]], separators=(",", ":")).encode()).hexdigest()
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rebind "$scope_tmp/restricted-live-parent.json"
printf '#!/usr/bin/env bash\n' >"$scope_repo/runtime/new-parent.sh"
scope_expect_fail "scenario10: broadening revalidates the live child first" \
  "stale-sidecar: new runtime/new-parent.sh" \
  --graph-parent "$scope_tmp/restricted-live-parent.json" "$scope_repo" runtime miss
rm "$scope_repo/runtime/new-parent.sh"

scope_expect_fail "scenario10: undeclared broadening reason rejected" \
  "invalid broadening reason" \
  --graph-parent "$scope_catalog" "$scope_repo" runtime convenience

runtime_graph="$("${py_cmd[@]}" - "$scope_catalog" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
print(next(row for row in p["scopes"] if row["name"] == "runtime")["graph"])
PY
)"
cp "$runtime_graph" "$scope_tmp/runtime-graph.saved"
printf 'corrupt\n' >>"$runtime_graph"
scope_expect_fail "scenario10: selected graph digest mismatch rejected" \
  "stale-sidecar: graph-digest runtime" \
  --graph-scope "$scope_catalog" "$scope_repo" runtime/runner.sh
mv "$scope_tmp/runtime-graph.saved" "$runtime_graph"

printf 'changed but self-reported\n' >>"$scope_repo/runtime/runner.sh"
"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/catalog-file-rehash.json" "$scope_repo" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
row = next(row for row in p["scopes"] if row["name"] == "runtime")
row["files"]["runtime/runner.sh"] = hashlib.sha256(open(
    sys.argv[3] + "/runtime/runner.sh", "rb").read()).hexdigest()
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rehash_catalog_only "$scope_tmp/catalog-file-rehash.json"
scope_expect_fail "scenario10: catalogue file rehash cannot bless an unchanged graph" \
  "stale-sidecar: graph-scope-binding runtime" \
  --graph-scope "$scope_tmp/catalog-file-rehash.json" "$scope_repo" runtime/runner.sh
git -C "$scope_repo" checkout -q -- runtime/runner.sh

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/catalog-version-drift.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
next(row for row in p["scopes"] if row["name"] == "runtime")["build"]["version"] = "9.9.9"
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rehash_catalog_only "$scope_tmp/catalog-version-drift.json"
scope_expect_fail "scenario10: extractor-version drift cannot bless an unchanged graph" \
  "stale-sidecar: graph-scope-binding runtime" \
  --graph-scope "$scope_tmp/catalog-version-drift.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/catalog-root-drift.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
row = next(row for row in p["scopes"] if row["name"] == "runtime")
row["root"] = "."
row["config"] = {k: v for k, v in row["config"].items() if "/" not in k}
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_rehash_catalog_only "$scope_tmp/catalog-root-drift.json"
scope_expect_fail "scenario10: scan-root drift cannot bless an unchanged graph" \
  "stale-sidecar: graph-scope-binding runtime" \
  --graph-scope "$scope_tmp/catalog-root-drift.json" "$scope_repo" runtime/runner.sh

printf 'digest-matching but not Graphify JSON\n' >"$scope_tmp/graphs/not-graph.txt"
"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/non-graph.json" "$scope_tmp/graphs/not-graph.txt" <<'PY'
import hashlib, json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
p["scopes"][0]["graph"] = sys.argv[3]
p["scopes"][0]["graph_sha256"] = hashlib.sha256(open(sys.argv[3], "rb").read()).hexdigest()
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_expect_fail "scenario10: digest-matching non-Graphify graph is rejected" \
  "stale-sidecar: invalid graph runtime" \
  --graph-scope "$scope_tmp/non-graph.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/foreign-source-catalog.json" <<'PY'
import hashlib, json, sys
from pathlib import Path
p = json.load(open(sys.argv[1], encoding="utf-8"))
row = next(row for row in p["scopes"] if row["name"] == "runtime")
graph = json.load(open(row["graph"], encoding="utf-8"))
graph["nodes"][0]["source_file"] = "../docs/private.py"
target = Path(sys.argv[2]).with_suffix(".graph.json")
target.write_text(json.dumps(graph, separators=(",", ":")) + "\n", encoding="utf-8")
row["graph"] = str(target.resolve())
row["graph_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_expect_fail "scenario10: graph source population must equal declared manifest" \
  "stale-sidecar: graph-population runtime" \
  --graph-scope "$scope_tmp/foreign-source-catalog.json" "$scope_repo" runtime/runner.sh

printf '{' >"$scope_tmp/corrupt-catalog.json"
scope_expect_fail "scenario10: corrupt catalogue rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/corrupt-catalog.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp" <<'PY'
import json, sys
source, out = sys.argv[1:]
for name, path in (("top-level", ()), ("scope", ("scopes", 0)),
                   ("config", ("scopes", 0, "config")),
                   ("build", ("scopes", 0, "build"))):
    payload = json.load(open(source, encoding="utf-8"))
    target = payload
    for part in path:
        target = target[part]
    target["unexpected"] = True
    open(f"{out}/unknown-{name}-member.json", "w", encoding="utf-8").write(json.dumps(payload))
PY
for unknown_catalog in top-level scope config build; do
  scope_expect_fail "scenario10: unknown catalogue member $unknown_catalog is rejected" \
    "invalid graph catalogue" \
    --graph-scope "$scope_tmp/unknown-$unknown_catalog-member.json" "$scope_repo" runtime/runner.sh
done

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp" <<'PY'
import hashlib, json, sys
from pathlib import Path

source, out = Path(sys.argv[1]), Path(sys.argv[2])
raw = source.read_text(encoding="utf-8")
payload = json.loads(raw)
runtime = next(row for row in payload["scopes"] if row["name"] == "runtime")

def write(name, old, new):
    if old not in raw:
        raise SystemExit(f"missing duplicate-member fixture token: {old}")
    (out / name).write_text(raw.replace(old, new, 1), encoding="utf-8")

write("duplicate-schema.json", '"schema": 1', '"schema": 2, "schema": 1')
file_digest = runtime["files"]["runtime/runner.sh"]
write("duplicate-files.json",
      f'"runtime/runner.sh": "{file_digest}"',
      f'"runtime/runner.sh": "{"0" * 64}", "runtime/runner.sh": "{file_digest}"')
config_digest = runtime["config"][".gitignore"]
write("duplicate-config.json", f'".gitignore": "{config_digest}"',
      f'".gitignore": "{"0" * 64}", ".gitignore": "{config_digest}"')
write("duplicate-build.json", '"version": "0.8.37"',
      '"version": "9.9.9", "version": "0.8.37"')

graph_path = Path(runtime["graph"])
graph_raw = graph_path.read_text(encoding="utf-8")
scope_sha = runtime["build"]["scope_sha256"]
needle = f'"implementaudit_scope_sha256":"{scope_sha}"'
duplicate = f'"implementaudit_scope_sha256":"{"0" * 64}",{needle}'
if needle not in graph_raw:
    raise SystemExit("missing graph duplicate-member fixture token")
graph_out = out / "graphs" / "duplicate-member-graph.json"
graph_out.write_text(graph_raw.replace(needle, duplicate, 1), encoding="utf-8")
runtime["graph"] = str(graph_out.resolve())
runtime["graph_sha256"] = hashlib.sha256(graph_out.read_bytes()).hexdigest()
(out / "duplicate-graph-catalog.json").write_text(json.dumps(payload), encoding="utf-8")
PY
for duplicate_catalog in schema files config build; do
  scope_expect_fail "scenario10: duplicate JSON member $duplicate_catalog is rejected" \
    "invalid graph catalogue" \
    --graph-scope "$scope_tmp/duplicate-$duplicate_catalog.json" "$scope_repo" runtime/runner.sh
done
scope_expect_fail "scenario10: duplicate nested graph member is rejected" \
  "stale-sidecar: invalid graph runtime" \
  --graph-scope "$scope_tmp/duplicate-graph-catalog.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/partial-catalog.json" \
  "$scope_tmp/partial-root-catalog.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
del p["scopes"][0]["files"]
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
p = json.load(open(sys.argv[1], encoding="utf-8"))
del p["scopes"][0]["root"]
open(sys.argv[3], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_expect_fail "scenario10: partial catalogue rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/partial-catalog.json" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: missing scan root rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/partial-root-catalog.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/wrong-type-catalog.json" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
p["scopes"][0]["files"] = []
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_expect_fail "scenario10: wrong catalogue type rejected without traceback" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/wrong-type-catalog.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/schema-bool.json" \
  "$scope_tmp/schema-float.json" "$scope_tmp/unordered-files.json" \
  "$scope_tmp/duplicate-rules.json" <<'PY'
import hashlib, json, sys
source, bool_out, float_out, order_out, duplicate_out = sys.argv[1:]

def load():
    return json.load(open(source, encoding="utf-8"))

p = load()
p["schema"] = True
open(bool_out, "w", encoding="utf-8").write(json.dumps(p))

p = load()
p["schema"] = 1.0
open(float_out, "w", encoding="utf-8").write(json.dumps(p))

p = load()
root = next(row for row in p["scopes"] if row["name"] == "root")
root["files"] = dict(reversed(list(root["files"].items())))
open(order_out, "w", encoding="utf-8").write(json.dumps(p))

p = load()
runtime = next(row for row in p["scopes"] if row["name"] == "runtime")
runtime["include"].append(runtime["include"][0])
runtime["build"]["rules_sha256"] = hashlib.sha256(json.dumps(
    [sorted(runtime["include"]), sorted(runtime["exclude"])],
    separators=(",", ":")).encode()).hexdigest()
open(duplicate_out, "w", encoding="utf-8").write(json.dumps(p))
PY
scope_expect_fail "scenario10: boolean schema is rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/schema-bool.json" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: float schema is rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/schema-float.json" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: noncanonical file ordering is rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/unordered-files.json" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: duplicate scope rules are rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/duplicate-rules.json" "$scope_repo" runtime/runner.sh

"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/file-count-bool.json" \
  "$scope_tmp/disjoint-parent.json" "$scope_tmp/uncovered-parent.json" \
  "$scope_tmp/bad-build.json" <<'PY'
import json, sys
source, bool_out, disjoint_out, uncovered_out, build_out = sys.argv[1:]

def load():
    return json.load(open(source, encoding="utf-8"))

p = load()
p["scopes"][0]["file_count"] = True
open(bool_out, "w", encoding="utf-8").write(json.dumps(p))

p = load()
p["scopes"][0]["parent"] = "release"
open(disjoint_out, "w", encoding="utf-8").write(json.dumps(p))

p = load()
p["scopes"][2]["include"] = ["docs/**"]
open(uncovered_out, "w", encoding="utf-8").write(json.dumps(p))

p = load()
p["scopes"][0]["build"]["commit"] = "0" * 40
open(build_out, "w", encoding="utf-8").write(json.dumps(p))
PY
scope_expect_fail "scenario10: boolean file count is rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/file-count-bool.json" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: disjoint declared parent is rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/disjoint-parent.json" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: parent must cover every child file" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/uncovered-parent.json" "$scope_repo" runtime/runner.sh
scope_expect_fail "scenario10: missing build commit is rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/bad-build.json" "$scope_repo" runtime/runner.sh

empty_tree="$(git -C "$scope_repo" mktree </dev/null)"
foreign_commit="$(printf 'disconnected fixture\n' | git -C "$scope_repo" commit-tree "$empty_tree")"
"${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/disconnected-build.json" "$foreign_commit" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
for row in p["scopes"]:
    row["build"]["commit"] = sys.argv[3]
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
scope_expect_fail "scenario10: disconnected build provenance is rejected" \
  "invalid graph catalogue" \
  --graph-scope "$scope_tmp/disconnected-build.json" "$scope_repo" runtime/runner.sh

cp "$scope_catalog" "$scope_repo/catalog.json"
scope_expect_fail "scenario10: in-repo catalogue is rejected" \
  "catalogue path is inside repo" \
  --graph-scope "$scope_repo/catalog.json" "$scope_repo" runtime/runner.sh
rm "$scope_repo/catalog.json"

if "${py_cmd[@]}" - "$scope_catalog" "$scope_repo/catalog-link.json" <<'PY'
import os, sys
try:
    os.symlink(sys.argv[1], sys.argv[2])
except (OSError, NotImplementedError):
    raise SystemExit(1)
PY
then
  scope_expect_fail "scenario10: in-repo catalogue symlink is rejected" \
    "catalogue path is inside repo" \
    --graph-scope "$scope_repo/catalog-link.json" "$scope_repo" runtime/runner.sh
  rm "$scope_repo/catalog-link.json"

  "${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/graph-link-catalog.json" \
    "$scope_repo/graph-link.json" "$scope_tmp/graphs/runtime.json" <<'PY'
import json, os, sys
os.symlink(sys.argv[4], sys.argv[3])
p = json.load(open(sys.argv[1], encoding="utf-8"))
p["scopes"][0]["graph"] = sys.argv[3]
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(p))
PY
  scope_expect_fail "scenario10: in-repo graph symlink is rejected" \
    "graph path is inside repo" \
    --graph-scope "$scope_tmp/graph-link-catalog.json" "$scope_repo" runtime/runner.sh
  rm "$scope_repo/graph-link.json"

  printf 'outside indexed content\n' >"$scope_tmp/outside-indexed.txt"
  "${py_cmd[@]}" - "$scope_tmp/outside-indexed.txt" "$scope_repo/runtime/indexed-link.txt" <<'PY'
import os, sys
os.symlink(sys.argv[1], sys.argv[2])
PY
  git -C "$scope_repo" add runtime/indexed-link.txt
  git -C "$scope_repo" commit -qm 'indexed symlink fixture'
  "${py_cmd[@]}" - "$scope_catalog" "$scope_tmp/indexed-symlink.json" \
    "$scope_repo" "$scope_tmp/outside-indexed.txt" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path
source, target, repo, outside = sys.argv[1:]
p = json.load(open(source, encoding="utf-8"))
head = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()
digest = hashlib.sha256(open(outside, "rb").read()).hexdigest()
for row in p["scopes"]:
    row["build"]["commit"] = head
    if row["name"] in {"runtime", "root"}:
        row["files"]["runtime/indexed-link.txt"] = digest
        row["file_count"] += 1
        graph = json.load(open(row["graph"], encoding="utf-8"))
        graph["nodes"].append({
            "id": f"{row['name']}-indexed-link",
            "source_file": "indexed-link.txt" if row["name"] == "runtime" else "runtime/indexed-link.txt",
        })
        graph_path = Path(target).parent / "graphs" / f"indexed-symlink-{row['name']}.json"
        graph_path.write_text(json.dumps(graph), encoding="utf-8")
        row["graph"] = str(graph_path.resolve())
        row["graph_sha256"] = hashlib.sha256(graph_path.read_bytes()).hexdigest()
open(target, "w", encoding="utf-8").write(json.dumps(p))
PY
  scope_rebind "$scope_tmp/indexed-symlink.json"
  scope_expect_fail "scenario10: indexed symlink escape is rejected before hashing" \
    "stale-sidecar: unsafe-path runtime/indexed-link.txt" \
    --graph-scope "$scope_tmp/indexed-symlink.json" "$scope_repo" runtime/runner.sh
  git -C "$scope_repo" rm -q runtime/indexed-link.txt
else
  check_pass "scenario10: symlink controls unavailable on this host" 0
fi

runtime_graph="$("${py_cmd[@]}" - "$scope_catalog" <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
print(next(row for row in p["scopes"] if row["name"] == "runtime")["graph"])
PY
)"
mv "$runtime_graph" "$scope_tmp/relation-graph.saved"
scope_expect_fail "scenario10: relation omission validates child freshness first" \
  "stale-sidecar: missing graph runtime" \
  --graph-parent "$scope_catalog" "$scope_repo" runtime relation-omission
mv "$scope_tmp/relation-graph.saved" "$runtime_graph"

set +e
relation_output="$(bash "$scope_helper" --graph-parent "$scope_catalog" \
  "$scope_repo" runtime relation-omission 2>&1)"
relation_status=$?
set -e
if [ "$relation_status" -eq 0 ] && \
   printf '%s' "$relation_output" | grep -Fq \
     "extractor/relation-model omission fallback=deterministic-live-file-census broaden=false llm=false"; then
  check_pass "scenario10: relation omission executes deterministic no-model fallback" 0
else
  printf 'sidecars.test: relation omission output: %s\n' "$relation_output" >&2
  check_pass "scenario10: relation omission executes deterministic no-model fallback" 1
fi

"${py_cmd[@]}" - fixtures/sidecar-contract/scoped-catalog/cases.json <<'PY'
import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))
rows = [row for row in p.get("cases", []) if row.get("id") == "missing-invocation-relation"]
expected = {
    "id": "missing-invocation-relation",
    "expect": "extractor/relation-model omission",
    "fallback": "deterministic live-file census",
    "broaden": False,
    "llm": False,
}
if rows != [expected]:
    raise SystemExit("missing relation control is not exact")
PY
check_pass "scenario10: relation-omission fixture is parsed exactly" "$?"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'sidecars.test: FAIL — %d/%d checks failed\n' "$fail" "$total" >&2
  exit 1
fi

printf 'sidecars.test: ok (%d/%d)\n' "$pass" "$total"
