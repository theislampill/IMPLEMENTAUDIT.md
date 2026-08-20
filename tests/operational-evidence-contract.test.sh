#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'operational-evidence-contract.test: %s\n' "$*" >&2
  exit 1
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

loader="skills/implementaudit/scripts/operational-evidence.py"
fixtures="fixtures/operational-evidence"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

expect_typed_failure() {
  local fixture="$1"
  local code="$2"
  local status
  set +e
  "${py_cmd[@]}" "$loader" validate "$fixtures/$fixture" \
    >"$tmp/stdout" 2>"$tmp/stderr"
  status=$?
  set -e
  [ "$status" -eq 2 ] \
    || fail "$fixture expected typed exit 2, got $status"
  "${py_cmd[@]}" - "$tmp/stderr" "$code" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    error = json.load(stream)
if error.get("schema") != "implementaudit-operational-evidence-error-v1":
    raise SystemExit("stable typed error schema missing")
if error.get("code") != sys.argv[2]:
    raise SystemExit(
        f"expected typed failure {sys.argv[2]}, got {error.get('code')!r}")
PY
}

"${py_cmd[@]}" "$loader" validate "$fixtures/valid-minimal.json" \
  >"$tmp/valid.json"
"${py_cmd[@]}" - "$tmp/valid.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    result = json.load(stream)
if result.get("schema") != "implementaudit-operational-evidence-validation-v1":
    raise SystemExit("validation receipt schema missing")
if result.get("aggregate") != "COMPLETE":
    raise SystemExit("valid COMPLETE fixture did not remain COMPLETE")
if result.get("families") != [
        "CODE", "OWNERSHIP", "EXECUTION", "EVIDENCE", "FAILURE", "RELEASE"]:
    raise SystemExit("six frozen families were not preserved in order")
PY

"${py_cmd[@]}" "$loader" validate "$fixtures/valid-unknown.json" \
  >"$tmp/unknown-receipt.json"
"${py_cmd[@]}" "$loader" canonicalize "$fixtures/valid-unknown.json" \
  >"$tmp/unknown-canonical.json"
"${py_cmd[@]}" - "$tmp/unknown-receipt.json" \
  "$tmp/unknown-canonical.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    receipt = json.load(stream)
with open(sys.argv[2], encoding="utf-8") as stream:
    canonical = json.load(stream)
if receipt.get("aggregate") != "DEGRADED":
    raise SystemExit("UNKNOWN receipt must preserve DEGRADED aggregate")
if receipt.get("fact_state_census") != {"UNKNOWN": 1}:
    raise SystemExit("UNKNOWN receipt state census drift")
if canonical["aggregate"] != "DEGRADED":
    raise SystemExit("UNKNOWN canonical aggregate drift")
if canonical["affected_families"] != ["CODE"]:
    raise SystemExit("UNKNOWN affected family drift")
if canonical["entities"][0]["currentness"] != {
        "state": "UNKNOWN", "invalidators": []}:
    raise SystemExit("UNKNOWN canonical state drift")
PY

expect_typed_failure duplicate-key.json OE_JSON_DUPLICATE_KEY
expect_typed_failure nonfinite.json OE_JSON_NONFINITE
expect_typed_failure malformed-record.json OE_SCHEMA_INVALID
expect_typed_failure record-type-array.json OE_SCHEMA_INVALID
expect_typed_failure integer-digit-limit.json OE_JSON_NUMBER_LIMIT
expect_typed_failure cross-layer.json OE_CROSS_LAYER
expect_typed_failure stale-current.json OE_STALE_RECORD
expect_typed_failure unsupported-schema.json OE_SCHEMA_UNSUPPORTED
expect_typed_failure duplicate-id.json OE_SCHEMA_INVALID
expect_typed_failure payload-digest-mismatch.json OE_PAYLOAD_DIGEST

"${py_cmd[@]}" "$loader" canonicalize "$fixtures/payload-lf.json" \
  >"$tmp/payload-lf.json"
"${py_cmd[@]}" "$loader" canonicalize "$fixtures/payload-crlf.json" \
  >"$tmp/payload-crlf.json"
cmp "$tmp/payload-lf.json" "$tmp/payload-crlf.json" \
  || fail "equivalent payload newline forms did not canonicalize byte-identically"
"${py_cmd[@]}" - "$tmp/payload-lf.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    value = json.load(stream)
payload = value["payload_records"][0]
if payload["payload"] != "line one\nline two":
    raise SystemExit("payload rule must normalize CRLF/CR to LF and strip trailing LF")
if payload["payload_sha256"] != (
        "b6858b03a6cae635deeaeab09a74e598979b72c917cbfff0bb3fe2cd05111dbc"):
    raise SystemExit("payload digest drift")
PY

"${py_cmd[@]}" - "$loader" "$fixtures/static-repository" "$tmp" <<'PY'
import ast
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys


loader_path = pathlib.Path(sys.argv[1])
fixture_root = pathlib.Path(sys.argv[2])
tmp_root = pathlib.Path(sys.argv[3])
spec = importlib.util.spec_from_file_location("operational_evidence", loader_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

for symbol in ("collect_repository", "normalize_static_receipt",
               "normalize_static_receipts"):
    if not hasattr(module, symbol):
        raise SystemExit(f"C02 RED: CODE collector/normalizer missing: {symbol}")


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", os.fspath(root), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()


def initialize_repo(root):
    git(root, "init", "-q")
    git(root, "config", "user.name", "Operational Evidence Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "add", "--all")
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_DATE": "2026-08-20T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-08-20T00:00:00Z",
    })
    subprocess.run(
        ["git", "-C", os.fspath(root), "commit", "-q", "-m", "fixture"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)


def fingerprint(root):
    rows = []
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or not path.is_file():
            continue
        rows.append((path.relative_to(root).as_posix(),
                     hashlib.sha256(path.read_bytes()).hexdigest()))
    return rows, git(root, "status", "--porcelain=v1", "--untracked-files=all")


repo = tmp_root / "static-repository"
shutil.copytree(fixture_root, repo)
initialize_repo(repo)
before = fingerprint(repo)
collection = module.collect_repository(repo)
after = fingerprint(repo)
if before != after:
    raise SystemExit("repository collector mutated target bytes or Git state")
if collection.get("schema") != "implementaudit-repository-collection-v1":
    raise SystemExit("repository collection schema missing")
repository = collection.get("repository", {})
if repository.get("commit") != git(repo, "rev-parse", "HEAD"):
    raise SystemExit("repository commit provenance drift")
if repository.get("tree") != git(repo, "rev-parse", "HEAD^{tree}"):
    raise SystemExit("repository tree provenance drift")
if repository.get("worktree_state") != "CLEAN":
    raise SystemExit("clean fixture repository did not remain CLEAN")

facts = collection.get("facts", [])
file_facts = {row.get("path"): row for row in facts if row.get("kind") == "FILE"}
expected_paths = {
    "README.weird", "package/implementaudit-package.json", "scripts/check.sh",
    "scripts/verify-package.sh", "src/broken.py", "src/helper.py",
    "src/main.py", "tests/example.test.sh",
}
if set(file_facts) != expected_paths:
    raise SystemExit("tracked file fact census drift")
if file_facts["src/main.py"].get("sha256") != (
        "46f4e61c6e13ed54aebb3dec432b98d712703106ba7292ac8a8419f7149d2bff"):
    raise SystemExit("file byte provenance drift")

edges = [row for row in facts if row.get("kind") == "PYTHON_IMPORT"]
if [(row.get("source"), row.get("target")) for row in edges] != [
        ("src/main.py", "src/helper.py")]:
    raise SystemExit("bounded Python-AST positive edge drift")
edge_provenance = edges[0].get("provenance", {})
if (edge_provenance.get("parser") != "python-ast-static-imports-v1" or
        edge_provenance.get("input_path") != "src/main.py" or
        edge_provenance.get("input_sha256") != file_facts["src/main.py"]["sha256"]):
    raise SystemExit("Python-AST edge lost parser/input provenance")
expected_ast_digest = hashlib.sha256(
    pathlib.Path(ast.__file__).read_bytes()).hexdigest()
if ({
        "collector_identity": edge_provenance.get("collector_identity"),
        "collector_version": edge_provenance.get("collector_version"),
        "collector_package_sha256": edge_provenance.get(
            "collector_package_sha256"),
        "invocation_identity": edge_provenance.get("invocation_identity"),
        "output_schema_identity": edge_provenance.get("output_schema_identity"),
    } != {
        "collector_identity": "python-stdlib-ast",
        "collector_version": (
            f"{platform.python_implementation()}-{platform.python_version()}"),
        "collector_package_sha256": expected_ast_digest,
        "invocation_identity": "ast.parse(mode=exec,type_comments=false)",
        "output_schema_identity": "implementaudit-repository-collection-v1",
    }):
    raise SystemExit("Python-AST edge lost exact collector provenance")
reverse = [row for row in facts if row.get("kind") == "PYTHON_REVERSE_DEPENDENT"]
if [(row.get("source"), row.get("target")) for row in reverse] != [
        ("src/helper.py", "src/main.py")]:
    raise SystemExit("reverse-dependent positive fact drift")
external = [row for row in facts
            if row.get("kind") == "UNSUPPORTED_IMPORT_OBSERVATION"]
if [(row.get("source"), row.get("target"), row.get("state"))
        for row in external] != [("src/main.py", "importlib", "UNSUPPORTED")]:
    raise SystemExit("unsupported external import became a missing edge")
if not any(value.startswith("computed-import:src/main.py:")
           for value in collection["diagnostics"]["unknown"]):
    raise SystemExit("computed import did not remain explicitly unknown")
if any(row.get("kind") in {"WORK_DEPENDENCY", "READY", "JOIN"}
       for row in facts):
    raise SystemExit("source topology invented work authority")
parser_errors = [row for row in facts
                 if row.get("kind") == "PARSER_ERROR_OBSERVATION"]
if len(parser_errors) != 1 or parser_errors[0].get("path") != "src/broken.py":
    raise SystemExit("parser failure became empty or lost its file identity")
if not any(row.get("kind") == "PACKAGE_ROOT" and row.get("path") == "src"
           for row in facts):
    raise SystemExit("positive package-root relation missing")
registry = [row for row in facts if row.get("kind") == "REGISTRY_FILE"]
if len(registry) != 1 or registry[0].get("path") != "scripts/verify-package.sh":
    raise SystemExit("registry file identity missing")
if any(row.get("kind") == "REGISTRY_ENTRY" for row in facts):
    raise SystemExit("unsupported shell registry inferred entries")
capabilities = {row["capability"]: row for row in collection["capabilities"]}
if capabilities["python_ast"]["state"] != "PARTIAL":
    raise SystemExit("parser error did not degrade Python-AST capability")
if capabilities["python_ast"].get("provenance") != {
        "collector_identity": "python-stdlib-ast",
        "collector_version": (
            f"{platform.python_implementation()}-{platform.python_version()}"),
        "collector_package_sha256": expected_ast_digest,
        "invocation_identity": "ast.parse(mode=exec,type_comments=false)",
        "output_schema_identity": "implementaudit-repository-collection-v1",
        "parser": "python-ast-static-imports-v1",
        "input_file_set_sha256": repository["input_file_set_sha256"],
    }:
    raise SystemExit("Python-AST capability lost exact degraded provenance")
if capabilities["validation_registry_entries"]["state"] != "UNSUPPORTED":
    raise SystemExit("shell registry extraction was not marked unsupported")
if module.canonical_json_v1(collection) != module.canonical_json_v1(
        module.collect_repository(repo)):
    raise SystemExit("repository collection is not semantically repeatable")

(repo / "README.weird").unlink()
missing_file = module.collect_repository(repo)
missing_caps = {
    row["capability"]: row for row in missing_file["capabilities"]}
if missing_caps["file_facts"]["state"] != "PARTIAL":
    raise SystemExit("unreadable tracked file did not degrade file capability")
missing_facts = [
    row for row in missing_file["facts"]
    if row.get("kind") == "FILE_UNREADABLE_OBSERVATION"]
if (len(missing_facts) != 1 or
        missing_facts[0].get("path") != "README.weird" or
        missing_facts[0].get("state") != "STALE"):
    raise SystemExit("unreadable tracked file became an empty fact gap")

non_applicable = tmp_root / "non-applicable"
non_applicable.mkdir()
(non_applicable / "package.json").write_text(
    '{"scripts":{"collect":"node target-controlled.js"}}\n', encoding="utf-8")
(non_applicable / "target-controlled.js").write_text(
    "require('fs').writeFileSync('EXECUTED', 'bad')\n", encoding="utf-8")
(non_applicable / "webpack.config.js").write_text(
    "throw new Error('must not execute')\n", encoding="utf-8")
initialize_repo(non_applicable)
cheap = module.collect_repository(non_applicable)
if (non_applicable / "EXECUTED").exists():
    raise SystemExit("non-applicable collection executed target code")
if cheap.get("static_collector_invocations") != []:
    raise SystemExit("non-applicable repository paid mandatory collector cost")
cheap_caps = {row["capability"]: row for row in cheap["capabilities"]}
if cheap_caps["python_ast"]["state"] != "NOT_APPLICABLE":
    raise SystemExit("non-applicable repository state drift")
if not [row for row in cheap["facts"] if row.get("kind") == "FILE"]:
    raise SystemExit("non-applicable repository lost exact file fallback")


ZERO64 = "0" * 64
ONE64 = "1" * 64
TWO64 = "2" * 64
ZERO40 = "0" * 40
ONE40 = "1" * 40


def base_receipt():
    return {
        "schema": "implementaudit-static-receipt-v1",
        "outcome": "CURRENT",
        "invalidators": [],
        "collector": {
            "identity": "fixture-python-ast",
            "version": "3.11",
            "package_sha256": ZERO64,
            "invocation_identity": "python-ast-static-imports-v1",
            "output_schema_identity": "fixture-static-output-v1",
            "parser_mode": "python-ast-static-imports-v1",
            "configuration_sha256": ONE64,
            "trust_mode": "UNTRUSTED_DATA_ONLY",
            "executes_target_code": False,
            "auto_installs": False,
            "network_access": False,
        },
        "target": {
            "repository_identity": "fixture/repository",
            "snapshot_identity": "fixture-snapshot",
            "commit": ZERO40,
            "tree": ONE40,
            "worktree_state": "CLEAN",
            "input_file_set_sha256": TWO64,
            "physical_change": False,
        },
        "scope": {
            "applicable": True,
            "supported": ["python:static-import"],
            "unsupported": ["python:computed-import"],
            "input_complete": True,
            "entrypoints_complete": True,
            "workspace_complete": True,
            "extension_resolution_complete": True,
            "dynamic_entrypoints_complete": False,
            "generated_policy_complete": True,
            "parser_complete": True,
        },
        "diagnostics": {
            "warnings": [], "errors": [], "skipped": [],
            "unknown": ["python:computed-import"],
        },
        "facts": [{
            "id": "edge-main-helper",
            "kind": "MODULE_EDGE",
            "polarity": "POSITIVE",
            "source": "src/main.py",
            "target": "src/helper.py",
            "resolution": "RESOLVED",
            "state": "CURRENT",
            "work_consequence": "NONE",
            "mapping": None,
        }, {
            "id": "reverse-helper-main",
            "kind": "REVERSE_DEPENDENT",
            "polarity": "POSITIVE",
            "source": "src/helper.py",
            "target": "src/main.py",
            "resolution": "RESOLVED",
            "state": "CURRENT",
            "work_consequence": "NONE",
            "mapping": {
                "work_node_id": "R38-C12",
                "relation_type": "EVIDENCE",
                "effect": "INVALIDATE_EVIDENCE",
            },
        }],
    }


def expect_failure(name, value, code):
    try:
        module.normalize_static_receipt(value)
    except module.OperationalEvidenceError as exc:
        if exc.code != code:
            raise SystemExit(f"{name}: expected {code}, got {exc.code}")
    else:
        raise SystemExit(f"{name}: unsafe static receipt was accepted")


normalized = module.normalize_static_receipt(base_receipt())
if normalized.get("schema") != "implementaudit-static-normalized-v1":
    raise SystemExit("normalized static receipt schema missing")
if normalized.get("outcome") != "CURRENT":
    raise SystemExit("supported static receipt lost CURRENT outcome")
if normalized.get("normalization_identity") != "canonical_json_v1":
    raise SystemExit("static output normalization identity missing")
if len(normalized.get("facts", [])) != 2:
    raise SystemExit("supported edge/reverse facts missing")
for fact in normalized["facts"]:
    if (fact.get("native_owner_identity") != "fixture/repository" or
            fact.get("authority_ceiling") != "READ_ONLY_STRUCTURAL_FACT"):
        raise SystemExit("static fact native owner/authority ceiling drift")
    provenance = fact.get("provenance", {})
    expected = {
        "collector_identity": "fixture-python-ast",
        "collector_version": "3.11",
        "collector_package_sha256": ZERO64,
        "invocation_identity": "python-ast-static-imports-v1",
        "output_schema_identity": "fixture-static-output-v1",
        "parser_mode": "python-ast-static-imports-v1",
        "configuration_sha256": ONE64,
        "target_snapshot_identity": "fixture-snapshot",
        "input_file_set_sha256": TWO64,
    }
    if provenance != expected:
        raise SystemExit("static fact provenance drift")
if normalized["facts"][1].get("mapping") != {
        "effect": "INVALIDATE_EVIDENCE", "relation_type": "EVIDENCE",
        "work_node_id": "R38-C12"}:
    raise SystemExit("explicit selective-invalidation mapping lost")
if any(fact.get("work_consequence") != "NONE" for fact in normalized["facts"]):
    raise SystemExit("supported facts invented a work consequence")
if len(normalized.get("semantic_sha256", "")) != 64:
    raise SystemExit("normalized static receipt semantic digest missing")
if module.canonical_json_v1(normalized) != module.canonical_json_v1(
        module.normalize_static_receipt(base_receipt())):
    raise SystemExit("static normalization is not semantically repeatable")

case = base_receipt()
case["facts"][0]["work_consequence"] = "WORK_DEPENDENCY"
expect_failure("module graph promoted to work DAG", case, "OE_STATIC_AUTHORITY")

case = base_receipt()
case["facts"] = [{
    "id": "missing-computed-edge", "kind": "NO_EDGE", "polarity": "NEGATIVE",
    "source": "src/main.py", "target": "src/dynamic.py",
    "resolution": "RESOLVED", "state": "CURRENT",
    "work_consequence": "NONE", "mapping": None,
}]
expect_failure(
    "unsupported computed edge treated absent", case,
    "OE_STATIC_NEGATIVE_UNQUALIFIED")

case = base_receipt()
case["facts"][0].update({"kind": "ORPHAN", "work_consequence": "DELETE"})
expect_failure(
    "orphan promoted to deletion", case, "OE_STATIC_AUTHORITY")

case = base_receipt()
case["target"]["physical_change"] = True
expect_failure("stale graph reused", case, "OE_STATIC_STALE")

case = base_receipt()
case["invalidators"] = ["collector configuration changed"]
expect_failure(
    "CURRENT receipt retained an invalidator", case, "OE_STATIC_CURRENTNESS")

case = base_receipt()
case["collector"]["executes_target_code"] = True
expect_failure(
    "untrusted target configuration executed", case, "OE_STATIC_TRUST")

case = base_receipt()
case["outcome"] = "PARSER_ERROR"
case["scope"]["parser_complete"] = False
case["diagnostics"]["errors"] = ["src/broken.py: invalid syntax"]
case["facts"] = []
parser_error = module.normalize_static_receipt(case)
if parser_error["outcome"] != "PARSER_ERROR" or not parser_error["facts"]:
    raise SystemExit("parser error became an empty graph")
if parser_error["facts"][0].get("kind") != "PARSER_ERROR_OBSERVATION":
    raise SystemExit("parser-error non-empty control drift")

left = base_receipt()
left["facts"] = [left["facts"][0]]
right = base_receipt()
right["collector"]["identity"] = "fixture-second-collector"
right["scope"]["unsupported"] = []
right["scope"]["dynamic_entrypoints_complete"] = True
right["facts"] = [{
    "id": "no-edge-main-helper", "kind": "NO_EDGE", "polarity": "NEGATIVE",
    "source": "src/main.py", "target": "src/helper.py",
    "resolution": "RESOLVED", "state": "CURRENT",
    "work_consequence": "NONE", "mapping": None,
}]
contradictory = module.normalize_static_receipts([left, right])
if contradictory.get("outcome") != "CONTRADICTORY":
    raise SystemExit("contradictory collectors were silently merged")
if len(contradictory.get("facts", [])) != 2:
    raise SystemExit("contradictory provenance was collapsed")
if len({fact["provenance"]["collector_identity"]
        for fact in contradictory["facts"]}) != 2:
    raise SystemExit("overlapping collector provenance was lost")

mismatched = copy.deepcopy(right)
mismatched["target"]["snapshot_identity"] = "different-snapshot"
try:
    module.normalize_static_receipts([left, mismatched])
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_STATIC_SET_MISMATCH":
        raise SystemExit(
            f"snapshot mismatch expected OE_STATIC_SET_MISMATCH, got {exc.code}")
else:
    raise SystemExit("collectors from different target snapshots were combined")

for forbidden in ("READY", "JOIN"):
    case = base_receipt()
    case["facts"][0]["work_consequence"] = forbidden
    expect_failure(
        f"R0038 output setting {forbidden}", case, "OE_STATIC_AUTHORITY")

case = base_receipt()
case["facts"][0].update({
    "kind": "SOURCE_CYCLE", "work_consequence": "WORK_DAG_CYCLE"})
expect_failure(
    "source cycle promoted to work-DAG cycle", case, "OE_STATIC_AUTHORITY")

case = base_receipt()
case["outcome"] = "UNSUPPORTED"
case["scope"]["applicable"] = False
case["scope"]["supported"] = []
case["facts"] = []
unsupported = module.normalize_static_receipt(case)
if unsupported["outcome"] != "UNSUPPORTED" or not unsupported["facts"]:
    raise SystemExit("unsupported collector became an empty graph")
if unsupported["facts"][0].get("kind") != "UNSUPPORTED_OBSERVATION":
    raise SystemExit("unsupported non-empty control drift")

case = base_receipt()
case["outcome"] = "NOT_INSTALLED"
case["facts"] = []
not_installed = module.normalize_static_receipt(case)
if (not_installed["outcome"] != "NOT_INSTALLED" or
        not_installed["facts"][0].get("kind") != "TOOL_UNAVAILABLE_OBSERVATION"):
    raise SystemExit("tool absence fallback drift")

case = base_receipt()
case["outcome"] = "PARTIAL"
case["diagnostics"]["skipped"] = ["src/generated.py"]
partial = module.normalize_static_receipt(case)
if partial["outcome"] != "PARTIAL" or partial["diagnostics"]["skipped"] != [
        "src/generated.py"]:
    raise SystemExit("partial degradation was not preserved")
PY

printf 'operational-evidence-contract.test: ok\n'
