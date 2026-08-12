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

if [ "${1:-}" = "--evaluate-activegraph-claims" ]; then
  [ "$#" -eq 2 ] || fail "usage: check-sidecar-boundaries.sh --evaluate-activegraph-claims <cases.json>"
  fixture="$2"
  require_file "$fixture"
  if command -v python >/dev/null 2>&1; then
    py_cmd=(python)
  elif command -v python3 >/dev/null 2>&1; then
    py_cmd=(python3)
  elif command -v py >/dev/null 2>&1; then
    py_cmd=(py -3)
  else
    fail "python, python3, or py -3 is required for ActiveGraph claim fixtures"
  fi
  "${py_cmd[@]}" - "$fixture" <<'PY'
import json
import sys

path = sys.argv[1]

TOP_KEYS = {"schema", "cases"}
CASE_KEYS = {
    "id", "operation", "subject", "coverage", "lineage", "readback",
    "independent_acceptance", "owner_authority", "host_evidence",
    "writer_model", "prior_failure", "claim", "expected",
}
EXPECTED_KEYS = {"classification", "verdict"}
OPERATIONS = {
    "no-activegraph", "event", "replay", "fork", "diff", "trial",
    "promote", "context-read", "authority-ceiling", "idle", "snapshot",
    "schedule",
}
SUBJECTS = {
    "none", "recorded-graph", "trace-metadata", "external-state",
    "semantic-property", "owner-authority", "security-boundary",
    "engineering-closure",
}
COVERAGE = {"none", "complete-recorded", "full", "partial", "untraced", "truncated", "unknown"}
LINEAGE = {"none", "same-trace", "shared-prefix", "independent-source"}
READBACK = {"none", "graph-local", "same-actor-external", "independent-external"}
WRITERS = {"none", "single-cooperative", "multi-cooperative", "uncontrolled"}
CLAIMS = {
    "no-activegraph", "recorded-state", "external-effect", "lineage",
    "independent-evidence", "structural-divergence", "semantic-correctness",
    "structural-promotion", "authorised-adoption", "observation-completeness",
    "declared-process-isolation", "host-security-isolation", "owner-authority",
    "engineering-closure", "snapshot-integrity", "causal-completeness",
    "cooperative-ordering", "distributed-correctness",
}


def exact_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{label}: keys must be exactly {sorted(expected)}")


def result(classification, verdict):
    return {"classification": classification, "verdict": verdict}


def classify(case):
    operation = case["operation"]
    claim = case["claim"]
    coverage = case["coverage"]
    readback = case["readback"]

    if operation == "no-activegraph" and claim == "no-activegraph":
        return result("NO_ACTIVEGRAPH", "PASS_CHEAP")
    if operation == "replay" and claim == "recorded-state":
        if (case["subject"] == "recorded-graph" and
                coverage == "complete-recorded" and readback == "graph-local"):
            return result("RECORDED_STATE_ESTABLISHED", "PASS_BOUNDED")
    if operation in {"event", "replay"} and claim == "external-effect":
        if readback == "independent-external" and coverage == "full":
            return result("EXTERNAL_EFFECT_ESTABLISHED", "PASS_BOUNDED")
        return result("EXTERNAL_WORLD_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "fork" and claim == "lineage":
        if case["lineage"] == "shared-prefix":
            return result("SHARED_LINEAGE_ESTABLISHED", "PASS_BOUNDED")
    if operation == "fork" and claim == "independent-evidence":
        if case["lineage"] == "independent-source" and case["independent_acceptance"]:
            return result("INDEPENDENT_EVIDENCE_ESTABLISHED", "PASS_BOUNDED")
        return result("INDEPENDENCE_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "diff" and claim == "structural-divergence":
        if (case["subject"] == "recorded-graph" and
                coverage == "complete-recorded" and readback == "graph-local"):
            return result("STRUCTURAL_DIVERGENCE_ESTABLISHED", "PASS_BOUNDED")
    if operation == "diff" and claim == "semantic-correctness":
        if case["independent_acceptance"]:
            return result("SEMANTIC_ACCEPTANCE_ESTABLISHED", "PASS_BOUNDED")
        return result("SEMANTIC_CORRECTNESS_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "promote" and claim == "structural-promotion":
        return result("STRUCTURAL_PROMOTION_ESTABLISHED", "PASS_BOUNDED")
    if operation == "promote" and claim == "authorised-adoption":
        if (case["independent_acceptance"] and case["owner_authority"] and
                readback == "independent-external"):
            return result("AUTHORISED_ADOPTION_ESTABLISHED", "PASS_BOUNDED")
        return result("ADOPTION_AUTHORITY_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "context-read" and claim == "observation-completeness":
        if coverage == "full":
            return result("OBSERVATION_COVERAGE_ESTABLISHED", "PASS_BOUNDED")
        return result("OBSERVATION_COMPLETENESS_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "trial" and claim == "declared-process-isolation":
        return result("DECLARED_PROCESS_BOUNDARY_ESTABLISHED", "PASS_BOUNDED")
    if operation == "trial" and claim == "host-security-isolation":
        if case["host_evidence"]:
            return result("HOST_SECURITY_BOUNDARY_ESTABLISHED", "PASS_BOUNDED")
        return result("HOST_SECURITY_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "authority-ceiling" and claim == "owner-authority":
        return result("OWNER_AUTHORITY_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "idle" and claim == "engineering-closure":
        return result("ENGINEERING_CLOSURE_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "snapshot" and claim == "snapshot-integrity":
        if (case["subject"] == "recorded-graph" and
                coverage == "complete-recorded" and readback == "graph-local"):
            return result("SNAPSHOT_INTEGRITY_ESTABLISHED", "PASS_BOUNDED")
    if operation == "snapshot" and claim == "causal-completeness":
        return result("CAUSAL_COMPLETENESS_UNPROVED", "REJECT_OVERCLAIM")
    if operation == "schedule" and claim == "cooperative-ordering":
        if case["writer_model"] == "single-cooperative":
            return result("COOPERATIVE_ORDERING_ESTABLISHED", "PASS_BOUNDED")
    if operation == "schedule" and claim == "distributed-correctness":
        return result("DISTRIBUTED_CORRECTNESS_UNPROVED", "REJECT_OVERCLAIM")
    raise ValueError(f"{case['id']}: unsupported operation/claim combination {operation}/{claim}")


try:
    with open(path, encoding="utf-8") as handle:
        fixture = json.load(handle)
    exact_keys(fixture, TOP_KEYS, "fixture")
    if fixture["schema"] != "implementaudit.activegraph_claims.v1":
        raise ValueError("fixture schema invalid")
    cases = fixture["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("fixture cases must be a non-empty list")
    seen = set()
    for index, case in enumerate(cases):
        exact_keys(case, CASE_KEYS, f"case {index}")
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"case {index}: id invalid")
        if case_id in seen:
            raise ValueError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if case["operation"] not in OPERATIONS or case["subject"] not in SUBJECTS:
            raise ValueError(f"{case_id}: operation or subject invalid")
        if case["coverage"] not in COVERAGE or case["lineage"] not in LINEAGE:
            raise ValueError(f"{case_id}: coverage or lineage invalid")
        if case["readback"] not in READBACK or case["writer_model"] not in WRITERS:
            raise ValueError(f"{case_id}: readback or writer model invalid")
        if case["claim"] not in CLAIMS:
            raise ValueError(f"{case_id}: claim invalid")
        for key in ("independent_acceptance", "owner_authority", "host_evidence", "prior_failure"):
            if type(case[key]) is not bool:
                raise ValueError(f"{case_id}: {key} must be boolean")
        exact_keys(case["expected"], EXPECTED_KEYS, f"{case_id} expected")
        actual = classify(case)
        if actual != case["expected"]:
            raise ValueError(
                f"{case_id}: expected {json.dumps(case['expected'], sort_keys=True)} "
                f"got {json.dumps(actual, sort_keys=True)}")
except (OSError, ValueError, json.JSONDecodeError) as exc:
    raise SystemExit(f"activegraph-claim: {exc}")

print(f"activegraph-claim: ok ({len(cases)}/{len(cases)})")
PY
  exit 0
fi

if [ "${1:-}" = "--evaluate-tokensave-claims" ]; then
  if [ "$#" -eq 2 ]; then
    tokensave_adapter=""
  elif [ "$#" -eq 4 ] && [ "$3" = "--tokensave-freshness-adapter" ]; then
    tokensave_adapter="$4"
  else
    fail "usage: check-sidecar-boundaries.sh --evaluate-tokensave-claims <cases.json> [--tokensave-freshness-adapter <absolute-operator-path>]"
  fi
  fixture="$2"
  require_file "$fixture"
  if command -v python >/dev/null 2>&1; then
    py_cmd=(python)
  elif command -v python3 >/dev/null 2>&1; then
    py_cmd=(python3)
  elif command -v py >/dev/null 2>&1; then
    py_cmd=(py -3)
  else
    fail "python, python3, or py -3 is required for TokenSave claim fixtures"
  fi
  checkout_root="$(git rev-parse --show-toplevel 2>/dev/null)" || \
    fail "TokenSave claim evaluation requires a live Git checkout"
  checkout_head="$(git rev-parse HEAD 2>/dev/null)" || \
    fail "TokenSave claim evaluation requires a readable checkout HEAD"
  "${py_cmd[@]}" - \
    "$fixture" "$checkout_root" "$checkout_head" "$tokensave_adapter" <<'PY'
import json
import os
import re
import signal
import subprocess
import sys

path, current_checkout_root, current_checkout_head, adapter_path = sys.argv[1:]
TOP_KEYS = {"schema", "cases"}
CASE_KEYS = {
    "id", "query_shape", "index_state", "coverage", "result_state",
    "freshness_expectation", "live_readback", "requested_use",
    "evidence_sources", "expected",
}
EXPECTED_KEYS = {"classification", "verdict"}
ADAPTER_RESULT_KEYS = {
    "schema", "checkout_root", "checkout_head", "database_identity",
    "database_fingerprint", "command", "exit_status", "readback_state",
    "readback_checkout_root", "readback_checkout_head",
    "readback_database_identity", "readback_database_fingerprint",
}
QUERY_SHAPES = {
    "supported-code-relation", "documentation", "policy",
    "public-projection", "exact-file", "tiny-task", "installation",
}
INDEX_STATES = {"current", "stale", "missing", "branch-unknown"}
COVERAGE = {"full-represented", "partial", "unsupported", "failed", "unknown"}
RESULT_STATES = {"consistent", "conflicting", "none"}
REQUESTED_USES = {
    "navigation", "complete-proof", "mutation-authority",
    "complete-acceptance", "independent-corroboration", "silent-setup",
}
EVIDENCE_SOURCES = {"none", "tokensave", "tokensave+graphify"}
ANTI_TRIGGERS = {"documentation", "policy", "public-projection", "exact-file", "tiny-task"}
SUPPORTED_SYNC_RECONNECT_COMMANDS = {"sync", "reconnect"}
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
FINGERPRINT_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
ADAPTER_SCHEMA = "implementaudit.tokensave_freshness_adapter.v1"
ADAPTER_TIMEOUT_SECONDS = 2
PROCESS_TREE_TERM_GRACE_SECONDS = 1
PROCESS_TREE_WAIT_SECONDS = 5


def exact_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{label}: keys must be exactly {sorted(expected)}")


def result(classification, verdict):
    return {"classification": classification, "verdict": verdict}


def normalized_root(value):
    if not isinstance(value, str) or not value or value.lower() in {
            "unknown", "missing", "unverified"}:
        return None
    return os.path.normcase(os.path.realpath(value))


def reject_duplicate_keys(pairs):
    value = {}
    for key, member in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = member
    return value


def adapter_result_is_current(value):
    if not isinstance(value, dict) or set(value) != ADAPTER_RESULT_KEYS:
        return False
    checkout_root = normalized_root(value["checkout_root"])
    readback_root = normalized_root(value["readback_checkout_root"])
    live_root = normalized_root(current_checkout_root)
    checkout_head = value["checkout_head"]
    database_identity = value["database_identity"]
    database_fingerprint = value["database_fingerprint"]
    valid_head = (
        isinstance(checkout_head, str) and
        SHA_PATTERN.fullmatch(checkout_head) is not None)
    valid_identity = (
        isinstance(database_identity, str) and bool(database_identity) and
        database_identity.lower() not in {"unknown", "missing", "unverified"})
    valid_fingerprint = (
        isinstance(database_fingerprint, str) and
        FINGERPRINT_PATTERN.fullmatch(database_fingerprint) is not None)
    valid_command = (
        isinstance(value["command"], str) and
        value["command"] in SUPPORTED_SYNC_RECONNECT_COMMANDS)

    return all((
        value["schema"] == ADAPTER_SCHEMA,
        checkout_root is not None,
        checkout_root == live_root,
        readback_root == live_root,
        valid_head,
        checkout_head == current_checkout_head,
        value["readback_checkout_head"] == current_checkout_head,
        valid_identity,
        valid_fingerprint,
        value["readback_database_identity"] == database_identity,
        value["readback_database_fingerprint"] == database_fingerprint,
        valid_command,
        type(value["exit_status"]) is int,
        value["exit_status"] == 0,
        value["readback_state"] == "current",
    ))


def run_authority_adapter():
    if not adapter_path:
        return None
    if not os.path.isabs(adapter_path):
        raise ValueError("adapter path must be absolute")
    resolved_adapter = os.path.normcase(os.path.realpath(adapter_path))
    resolved_checkout = os.path.normcase(os.path.realpath(current_checkout_root))
    if not os.path.isfile(resolved_adapter):
        raise ValueError("adapter path is not a readable file")
    try:
        common = os.path.commonpath((resolved_checkout, resolved_adapter))
    except ValueError:
        common = ""
    if common == resolved_checkout:
        raise ValueError("adapter must be outside the evaluated checkout")

    argv = [
        sys.executable, resolved_adapter,
        "freshness", "--json",
        "--checkout-root", current_checkout_root,
        "--checkout-head", current_checkout_head,
    ]
    popen_options = {
        "cwd": current_checkout_root,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if os.name == "nt":
        popen_options["creationflags"] = getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        popen_options["start_new_session"] = True
    try:
        process = subprocess.Popen(argv, **popen_options)
    except OSError:
        return None

    try:
        stdout, _stderr = process.communicate(timeout=ADAPTER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        owned_pid = process.pid
        if os.name == "nt":
            system_root = os.environ.get("SystemRoot", r"C:\Windows")
            taskkill = os.path.join(system_root, "System32", "taskkill.exe")
            try:
                subprocess.run(
                    [taskkill, "/PID", str(owned_pid), "/T", "/F"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=PROCESS_TREE_WAIT_SECONDS,
                    check=False,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
        else:
            try:
                os.killpg(owned_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=PROCESS_TREE_TERM_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                pass
            try:
                os.killpg(owned_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            process.wait(timeout=PROCESS_TREE_WAIT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=PROCESS_TREE_WAIT_SECONDS)
        return None

    if process.returncode != 0:
        return None
    try:
        result_value = json.loads(stdout, object_pairs_hook=reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError):
        return None
    if not adapter_result_is_current(result_value):
        return None
    return result_value


actual_freshness = None


def freshness_is_current(case):
    expectation = case["freshness_expectation"]
    return (
        actual_freshness is not None and
        isinstance(expectation, dict) and
        expectation == actual_freshness)


def classify(case):
    use = case["requested_use"]
    shape = case["query_shape"]
    if use == "silent-setup":
        return result("SETUP_AUTHORITY_UNPROVED", "REJECT_OVERCLAIM")
    if use == "mutation-authority":
        return result("MUTATION_AUTHORITY_UNPROVED", "REJECT_OVERCLAIM")
    if use == "complete-acceptance":
        return result("ACCEPTANCE_UNPROVED", "REJECT_OVERCLAIM")
    if use == "independent-corroboration":
        return result("INDEPENDENCE_UNPROVED", "REJECT_OVERCLAIM")
    if use == "complete-proof":
        return result("PROGRAM_COMPLETENESS_UNPROVED", "REJECT_OVERCLAIM")
    if shape in ANTI_TRIGGERS and use == "navigation":
        return result("NO_TOKENSAVE", "PASS_CHEAP")
    if shape != "supported-code-relation" or use != "navigation":
        raise ValueError(f"{case['id']}: unsupported query/use combination {shape}/{use}")
    if case["index_state"] == "missing":
        return result("NO_TOKENSAVE", "PASS_CHEAP")
    if case["index_state"] in {"stale", "branch-unknown"}:
        return result("TOKENSAVE_STALE", "REJECT_OVERCLAIM")
    if case["index_state"] == "current" and not freshness_is_current(case):
        return result("TOKENSAVE_FRESHNESS_UNVERIFIED", "REJECT_OVERCLAIM")
    if case["coverage"] in {"unsupported", "failed"}:
        return result("TOKENSAVE_UNSUPPORTED", "REJECT_OVERCLAIM")
    if case["result_state"] == "conflicting":
        return result("TOKENSAVE_UNRESOLVED", "REJECT_OVERCLAIM")
    if case["coverage"] == "unknown":
        return result("TOKENSAVE_UNRESOLVED", "REJECT_OVERCLAIM")
    if not case["live_readback"]:
        return result("LIVE_SOURCE_UNVERIFIED", "REJECT_OVERCLAIM")
    if (case["index_state"] == "current" and
            case["result_state"] == "consistent" and
            case["evidence_sources"] == "tokensave"):
        if case["coverage"] == "full-represented":
            return result("TOKENSAVE_DERIVED_FACT", "PASS_BOUNDED")
        if case["coverage"] == "partial":
            return result("TOKENSAVE_PARTIAL_FACT", "PASS_BOUNDED")
    raise ValueError(f"{case['id']}: unsupported state combination")


try:
    with open(path, encoding="utf-8") as handle:
        fixture = json.load(handle)
    exact_keys(fixture, TOP_KEYS, "fixture")
    if fixture["schema"] != "implementaudit.tokensave_claims.v3":
        raise ValueError("fixture schema invalid")
    actual_freshness = run_authority_adapter()
    cases = fixture["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("fixture cases must be a non-empty list")
    seen = set()
    for index, case in enumerate(cases):
        if isinstance(case, dict) and case.get("index_state") == "current":
            if "freshness_expectation" not in case:
                case_id = case.get("id", f"case {index}")
                raise ValueError(f"{case_id}: current freshness expectation missing")
        exact_keys(case, CASE_KEYS, f"case {index}")
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"case {index}: id invalid")
        if case_id in seen:
            raise ValueError(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if case["query_shape"] not in QUERY_SHAPES or case["index_state"] not in INDEX_STATES:
            raise ValueError(f"{case_id}: query shape or index state invalid")
        freshness = case["freshness_expectation"]
        if freshness is not None:
            exact_keys(
                freshness, ADAPTER_RESULT_KEYS,
                f"{case_id} freshness expectation")
        if case["coverage"] not in COVERAGE or case["result_state"] not in RESULT_STATES:
            raise ValueError(f"{case_id}: coverage or result state invalid")
        if case["requested_use"] not in REQUESTED_USES or case["evidence_sources"] not in EVIDENCE_SOURCES:
            raise ValueError(f"{case_id}: requested use or evidence sources invalid")
        if type(case["live_readback"]) is not bool:
            raise ValueError(f"{case_id}: live_readback must be boolean")
        exact_keys(case["expected"], EXPECTED_KEYS, f"{case_id} expected")
        actual = classify(case)
        if actual != case["expected"]:
            raise ValueError(
                f"{case_id}: expected {json.dumps(case['expected'], sort_keys=True)} "
                f"got {json.dumps(actual, sort_keys=True)}")
except (OSError, ValueError, json.JSONDecodeError) as exc:
    raise SystemExit(f"tokensave-claim: {exc}")

print(f"tokensave-claim: ok ({len(cases)}/{len(cases)})")
PY
  exit 0
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
require_file docs/portal/site.json
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
require_literal skills/implementaudit/references/sidecars.md \
  "independent evidence at that owner" "ActiveGraph evidence ceiling"
require_literal skills/implementaudit/templates/PROTOCOL.md \
  "With no durable causal/counterfactual need," "ActiveGraph cheap-path consumer"
require_literal skills/implementaudit/references/sidecars.md "missed-use-detection goal is retired" "missed-use retirement"
require_literal skills/implementaudit/references/sidecars.md "TokenSave-derived" "TokenSave evidence ceiling"
require_literal skills/implementaudit/references/sidecars.md "NO TOKENSAVE" "TokenSave cheap path"
require_literal skills/implementaudit/references/sidecars.md "function bodies and rendered-source cache" "TokenSave local source-retention disclosure"
require_literal skills/implementaudit/references/sidecars.md \
  "representation-specific exception" \
  "TokenSave storage exception"
require_literal skills/implementaudit/references/sidecars.md \
  "Only an operator/checker-controlled adapter" \
  "TokenSave authority-executed freshness mechanism"
require_literal skills/implementaudit/references/sidecars.md \
  "claim fields alone never" "TokenSave self-attestation rejection"
require_literal skills/implementaudit/references/sidecars.md \
  "TOKENSAVE_FRESHNESS_UNVERIFIED" "TokenSave unverified freshness route"
require_literal skills/implementaudit/references/sidecars.md \
  "remains explicit/on-demand" "TokenSave explicit runtime route"
require_literal skills/implementaudit/references/sidecars.md "Editing, test-running, session" "TokenSave mutation firewall"
require_literal skills/implementaudit/templates/PROTOCOL.md "TokenSave code-navigation rules" "TokenSave runtime route"
require_literal skills/implementaudit/templates/PROTOCOL.md \
  "checkout/database" "TokenSave protocol freshness binding"
require_literal skills/implementaudit/templates/PROTOCOL.md \
  "operator/checker-controlled" "TokenSave protocol adapter authority"
require_literal skills/implementaudit/templates/PROTOCOL.md \
  "outside candidate authority" "TokenSave protocol candidate boundary"
require_literal skills/implementaudit/templates/PROTOCOL.md \
  "claim fields" "TokenSave protocol claim boundary"
require_literal skills/implementaudit/templates/PROTOCOL.md \
  "alone never do" "TokenSave protocol self-attestation rejection"
require_literal skills/implementaudit/templates/PROTOCOL.md \
  "TOKENSAVE_FRESHNESS_UNVERIFIED" "TokenSave protocol unverified route"
require_literal README.md "### TokenSave-assisted code navigation" "TokenSave README projection"
require_literal README.md "TokenSave is explicit, on-demand optional tooling" "TokenSave explicit public route"
require_literal README.md "operator/checker-controlled" "TokenSave README adapter authority"
require_literal README.md "outside candidate" "TokenSave README candidate boundary"
require_literal README.md "claim fields alone" "TokenSave README self-attestation rejection"
require_literal README.md "TOKENSAVE_FRESHNESS_UNVERIFIED" "TokenSave README unverified route"
forbid_literal README.md "may detect Graphify, TokenSave, and ActiveGraph" "TokenSave automatic detection"
require_literal docs/diagrams/tooling-architecture.mmd "optional supported-code navigation" "TokenSave tooling-diagram projection"
require_literal docs/portal/pages/optional-tooling.html "id=\"tokensave\"" "TokenSave portal projection"
require_literal docs/portal/pages/optional-tooling.html "explicit, on-demand" "TokenSave explicit portal route"
require_literal docs/portal/pages/optional-tooling.html \
  "operator/checker-controlled" "TokenSave portal adapter authority"
require_literal docs/portal/pages/optional-tooling.html \
  "outside candidate authority" "TokenSave portal candidate boundary"
require_literal docs/portal/pages/optional-tooling.html \
  "claim fields alone" "TokenSave portal self-attestation rejection"
require_literal docs/portal/pages/optional-tooling.html \
  "TOKENSAVE_FRESHNESS_UNVERIFIED" "TokenSave portal unverified route"
require_literal docs/portal/pages/optional-tooling.html \
  "skills/implementaudit/references/sidecars.md" "TokenSave portal sidecar owner source"
require_literal docs/portal/pages/optional-tooling.html \
  "skills/implementaudit/templates/PROTOCOL.md" "TokenSave portal protocol owner source"
if command -v python >/dev/null 2>&1; then
  portal_py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  portal_py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  portal_py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required for portal source validation"
fi
"${portal_py_cmd[@]}" - docs/portal/site.json <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as handle:
        site = json.load(handle)
    sources = set(site["pages"]["optional-tooling"]["sources"])
except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"check-sidecar-boundaries: TokenSave portal source population is unreadable: {exc}")
required = {
    "skills/implementaudit/references/sidecars.md",
    "skills/implementaudit/templates/PROTOCOL.md",
}
if not required.issubset(sources):
    raise SystemExit("check-sidecar-boundaries: TokenSave portal source population is missing packaged owners")
PY
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
