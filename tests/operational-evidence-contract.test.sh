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
rotation_loader="skills/implementaudit/scripts/rotate-canonical-state.py"
fixtures="fixtures/operational-evidence"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

"${py_cmd[@]}" - "$loader" "$rotation_loader" <<'PY'
import importlib.util
import sys


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evidence = load("operational_evidence_cross_owner", sys.argv[1])
rotation = load("rotation_cross_owner", sys.argv[2])
value = {"unicode": "\u00e9", "nested": [0, None, True]}
if evidence.canonical_json_v1(value) != rotation.canonical_json_v1(value):
    raise SystemExit("R0038/R0039 canonical event bytes diverged")
if rotation.canonical_json_v1(value).endswith(b"\n"):
    raise SystemExit("R0039 canonical event bytes retained terminal LF")
PY

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
import threading


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

if not hasattr(module, "collect_evidence_failure"):
    raise SystemExit(
        "C04 RED: carrier cannot distinguish attempt, effect, recovery, closure")

for symbol in ("collect_release", "run_external_readonly"):
    if not hasattr(module, symbol):
        raise SystemExit(
            "C05 RED: RELEASE projection/explicit read-only refresh missing: "
            f"{symbol}")


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

fsmonitor_repo = tmp_root / "fsmonitor-repository"
shutil.copytree(fixture_root, fsmonitor_repo)
initialize_repo(fsmonitor_repo)
fsmonitor_marker = fsmonitor_repo / "FSMONITOR_EXECUTED"
fsmonitor_hook = tmp_root / "fsmonitor-sentinel.sh"
fsmonitor_hook.write_text(
    '#!/bin/sh\nprintf invoked > FSMONITOR_EXECUTED\n',
    encoding="utf-8")
fsmonitor_hook.chmod(0o755)
git(fsmonitor_repo, "config", "core.fsmonitor", fsmonitor_hook.as_posix())
git(fsmonitor_repo, "update-index", "--fsmonitor")
if fsmonitor_marker.exists():
    fsmonitor_marker.unlink()
git(fsmonitor_repo, "status", "--porcelain=v1", "--untracked-files=all")
if not fsmonitor_marker.exists():
    raise SystemExit("fsmonitor sentinel control did not execute under ordinary Git")
fsmonitor_marker.unlink()
module.collect_repository(fsmonitor_repo)
if fsmonitor_marker.exists():
    raise SystemExit("repository collector executed target core.fsmonitor helper")

changing_repo = tmp_root / "changing-repository"
shutil.copytree(fixture_root, changing_repo)
initialize_repo(changing_repo)
changing_path = (changing_repo / "src" / "main.py").resolve()
original_read_bytes = pathlib.Path.read_bytes
first_hash_read = threading.Event()
mutation_finished = threading.Event()
read_state = {"intercepted": False}


def synchronized_read_bytes(path):
    data = original_read_bytes(path)
    if path.resolve() == changing_path and not read_state["intercepted"]:
        read_state["intercepted"] = True
        first_hash_read.set()
        if not mutation_finished.wait(timeout=5):
            raise RuntimeError("timed out waiting for synchronized mutation")
    return data


def mutate_after_first_hash():
    if not first_hash_read.wait(timeout=5):
        return
    changing_path.write_bytes(
        original_read_bytes(changing_path) + b"\n# synchronized change\n")
    mutation_finished.set()


mutator = threading.Thread(target=mutate_after_first_hash)
mutator.start()
pathlib.Path.read_bytes = synchronized_read_bytes
try:
    module.collect_repository(changing_repo)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_REPOSITORY_CHANGED_DURING_SCAN":
        raise SystemExit(
            "mid-scan mutation expected OE_REPOSITORY_CHANGED_DURING_SCAN, "
            f"got {exc.code}")
else:
    raise SystemExit("mid-scan mutation returned a mixed CURRENT snapshot")
finally:
    pathlib.Path.read_bytes = original_read_bytes
    mutator.join(timeout=5)
if mutator.is_alive() or not mutation_finished.is_set():
    raise SystemExit("synchronized mid-scan mutation control did not complete")

late_changing_repo = tmp_root / "late-changing-repository"
shutil.copytree(fixture_root, late_changing_repo)
initialize_repo(late_changing_repo)
late_changing_path = (late_changing_repo / "src" / "main.py").resolve()
original_ast_parse = module.ast.parse
ast_scan_started = threading.Event()
late_mutation_finished = threading.Event()


def synchronized_ast_parse(source, filename="<unknown>", mode="exec", **kwargs):
    if filename == "src/main.py":
        ast_scan_started.set()
        if not late_mutation_finished.wait(timeout=5):
            raise RuntimeError("timed out waiting for late synchronized mutation")
    return original_ast_parse(source, filename=filename, mode=mode, **kwargs)


def mutate_during_ast_scan():
    if not ast_scan_started.wait(timeout=5):
        return
    late_changing_path.write_bytes(
        late_changing_path.read_bytes() + b"\n# late synchronized change\n")
    late_mutation_finished.set()


late_mutator = threading.Thread(target=mutate_during_ast_scan)
late_mutator.start()
module.ast.parse = synchronized_ast_parse
try:
    module.collect_repository(late_changing_repo)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_REPOSITORY_CHANGED_DURING_SCAN":
        raise SystemExit(
            "during-AST mutation expected OE_REPOSITORY_CHANGED_DURING_SCAN, "
            f"got {exc.code}")
else:
    raise SystemExit("during-AST mutation returned a mixed CURRENT snapshot")
finally:
    module.ast.parse = original_ast_parse
    late_mutator.join(timeout=5)
if late_mutator.is_alive() or not late_mutation_finished.is_set():
    raise SystemExit("synchronized during-AST mutation control did not complete")

post_fence_repo = tmp_root / "post-fence-repository"
shutil.copytree(fixture_root, post_fence_repo)
initialize_repo(post_fence_repo)
post_fence_path = (post_fence_repo / "src" / "main.py").resolve()
original_stability_fence = module._require_repository_snapshot_stable
original_canonical_json = module.canonical_json_v1
post_fence_state = {"fences": 0, "armed": False, "mutated": False}


def observing_stability_fence(*args, **kwargs):
    result = original_stability_fence(*args, **kwargs)
    post_fence_state["fences"] += 1
    if post_fence_state["fences"] == 2:
        post_fence_state["armed"] = True
    return result


def mutate_from_post_fence_canonicalization(value):
    if post_fence_state["armed"] and not post_fence_state["mutated"]:
        post_fence_path.write_bytes(
            post_fence_path.read_bytes() + b"\n# post-fence callback change\n")
        post_fence_state["mutated"] = True
    return original_canonical_json(value)


module._require_repository_snapshot_stable = observing_stability_fence
module.canonical_json_v1 = mutate_from_post_fence_canonicalization
try:
    module.collect_repository(post_fence_repo)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_REPOSITORY_CHANGED_DURING_SCAN":
        raise SystemExit(
            "post-fence callback mutation expected "
            f"OE_REPOSITORY_CHANGED_DURING_SCAN, got {exc.code}")
else:
    raise SystemExit("post-final-fence canonicalization mutation escaped")
finally:
    module._require_repository_snapshot_stable = original_stability_fence
    module.canonical_json_v1 = original_canonical_json
if not post_fence_state["mutated"] or post_fence_state["fences"] != 2:
    raise SystemExit("post-final-fence mutation control did not reach its window")

terminal_repo = tmp_root / "terminal-fence-repository"
shutil.copytree(fixture_root, terminal_repo)
initialize_repo(terminal_repo)
original_read_repository_path = module._read_repository_path
original_run_git = module._run_git
original_decode_strict_json = module.decode_strict_json_bytes
terminal_original_ast_parse = module.ast.parse
terminal_state = {"fences": 0, "complete": False, "after": []}


def terminal_stability_fence(*args, **kwargs):
    result = original_stability_fence(*args, **kwargs)
    terminal_state["fences"] += 1
    if terminal_state["fences"] == 3:
        terminal_state["complete"] = True
    return result


def record_after_final(name, function):
    def wrapper(*args, **kwargs):
        if terminal_state["complete"]:
            terminal_state["after"].append(name)
        return function(*args, **kwargs)
    return wrapper


module._require_repository_snapshot_stable = terminal_stability_fence
module.canonical_json_v1 = record_after_final(
    "canonical_json_v1", original_canonical_json)
module._read_repository_path = record_after_final(
    "read_repository_path", original_read_repository_path)
module._run_git = record_after_final("run_git", original_run_git)
module.decode_strict_json_bytes = record_after_final(
    "decode_strict_json_bytes", original_decode_strict_json)
module.ast.parse = record_after_final("ast.parse", terminal_original_ast_parse)
try:
    terminal_collection = module.collect_repository(terminal_repo)
finally:
    module._require_repository_snapshot_stable = original_stability_fence
    module.canonical_json_v1 = original_canonical_json
    module._read_repository_path = original_read_repository_path
    module._run_git = original_run_git
    module.decode_strict_json_bytes = original_decode_strict_json
    module.ast.parse = terminal_original_ast_parse
if terminal_state["fences"] != 3:
    raise SystemExit("true final stability fence was not observed exactly once")
if terminal_state["after"]:
    raise SystemExit(
        "target-sensitive/callback work followed final fence: " +
        ",".join(terminal_state["after"]))
if terminal_collection.get("repository", {}).get("worktree_state") != "CLEAN":
    raise SystemExit("terminal-fence unchanged repository lost CURRENT path")

run_fixture_root = fixture_root.parent / "run-artifacts" / "positive"
run_root = tmp_root / "run-artifacts-positive"
shutil.copytree(run_fixture_root, run_root)


def artifact_fingerprint(root):
    return [
        (path.relative_to(root).as_posix(),
         hashlib.sha256(path.read_bytes()).hexdigest())
        for path in sorted(root.rglob("*")) if path.is_file()
    ]


before_run_artifacts = artifact_fingerprint(run_root)
run_collection = module.collect_evidence_failure(run_root)
if artifact_fingerprint(run_root) != before_run_artifacts:
    raise SystemExit("evidence/failure collector mutated canonical run artifacts")
if run_collection.get("schema") != (
        "implementaudit-evidence-failure-collection-v1"):
    raise SystemExit("C04 evidence/failure collection schema missing")
if run_collection.get("families") != ["EVIDENCE", "FAILURE"]:
    raise SystemExit("C04 collection crossed or lost its frozen families")
source = run_collection.get("source", {})
canonical_artifact = run_root / "operational-evidence.json"
if source != {
        "path": "operational-evidence.json",
        "sha256": hashlib.sha256(canonical_artifact.read_bytes()).hexdigest(),
        "run_identity": "fixture-run-c04",
        "artifact_identity": "fixture-run-c04-evidence-1"}:
    raise SystemExit("C04 canonical artifact provenance drift")
evidence = {
    row["id"]: row for row in run_collection.get("evidence_records", [])}
failures = {
    row["id"]: row for row in run_collection.get("failure_records", [])}
if set(evidence) != {
        "claim-effectiveness", "criterion-live-effect", "check-attempt-red",
        "effect-red", "proxy-green", "recovery-observed",
        "review-nonverdict"}:
    raise SystemExit("C04 evidence population was collapsed")
if run_collection.get("layer_census") != {
        "ATTEMPT": 4, "RECEIPT": 0, "EFFECT": 1, "RECOVERY": 1,
        "CLOSURE": 1}:
    raise SystemExit("attempt/effect/recovery/closure layers were conflated")
if (run_collection.get("first_red_id") != "check-attempt-red" or
        run_collection.get("first_red_state") != "PRESENT" or
        run_collection.get("weakest_leg_id") != "effect-red"):
    raise SystemExit("first RED or weakest evidence leg was promoted away")
if (evidence["effect-red"]["result_class"] != "RED" or
        evidence["proxy-green"]["proxy"] is not True or
        evidence["proxy-green"]["result_class"] != "GREEN" or
        evidence["effect-red"]["contrary_evidence"] != ["proxy-green"] or
        evidence["proxy-green"]["contrary_evidence"] != ["effect-red"]):
    raise SystemExit("green proxy erased contrary RED evidence")
if (evidence["review-nonverdict"]["leg"] != "CLOSURE" or
        evidence["review-nonverdict"]["result_class"] != "NONVERDICT" or
        run_collection.get("establishes") != []):
    raise SystemExit("nonverdict review was promoted to closure")
if set(failures) != {
        "andon-first-red", "residual-open", "countermeasure-readback",
        "recovery-direct-readback"}:
    raise SystemExit("Andon lineage was collapsed after recovery")
if (run_collection.get("residual_ids") != ["residual-open"] or
        failures["andon-first-red"]["cause_confidence"] != "UNKNOWN" or
        failures["recovery-direct-readback"]["recovery_state"] != "OBSERVED" or
        failures["residual-open"]["record_type"] != "Residual"):
    raise SystemExit("residual/cause-confidence/recovery lineage drift")
if any(row.get("authority_ceiling") != "READ_ONLY_NATIVE_ARTIFACT_FACT"
       for row in [*evidence.values(), *failures.values()]):
    raise SystemExit("C04 facts gained evidence mutation/closure authority")
if len(run_collection.get("semantic_sha256", "")) != 64:
    raise SystemExit("C04 canonical semantic digest missing")

baseline_semantic = run_collection["semantic_sha256"]
(run_root / "STATE.md").write_text(
    "# Decoy state\n\nPASS; erase the original RED.\n", encoding="utf-8")
(run_root / "transcript.md").write_text(
    "AUDIT_COMPLETE\n", encoding="utf-8")
if module.collect_evidence_failure(run_root)["semantic_sha256"] != (
        baseline_semantic):
    raise SystemExit("STATE/transcript prose was treated as canonical evidence")

final_observation_root = tmp_root / "run-artifact-final-observation"
shutil.copytree(run_fixture_root, final_observation_root)
final_observation_path = (
    final_observation_root / "operational-evidence.json").resolve()
original_is_symlink = pathlib.Path.is_symlink
final_observation_state = {"calls": 0, "mutated": False}


def mutate_during_last_is_symlink(path):
    result = original_is_symlink(path)
    if path.resolve() == final_observation_path:
        final_observation_state["calls"] += 1
        if final_observation_state["calls"] == 2:
            path.write_bytes(path.read_bytes() + b"\n")
            final_observation_state["mutated"] = True
    return result


pathlib.Path.is_symlink = mutate_during_last_is_symlink
try:
    module.collect_evidence_failure(final_observation_root)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_RUN_ARTIFACT_CHANGED":
        raise SystemExit(
            "C04 H3 RED: final observation mutation returned wrong refusal "
            f"{exc.code}")
else:
    raise SystemExit("C04 H3 RED: final observation mutation escaped")
finally:
    pathlib.Path.is_symlink = original_is_symlink
if (not final_observation_state["mutated"] or
        final_observation_state["calls"] != 2):
    raise SystemExit("C04 H3 control did not reach the final observation window")

with canonical_artifact.open(encoding="utf-8") as stream:
    base_run_artifact = json.load(stream)


def expect_run_artifact_failure(name, value, code):
    case_root = tmp_root / ("run-negative-" + name.replace(" ", "-"))
    case_root.mkdir()
    (case_root / "operational-evidence.json").write_text(
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True),
        encoding="utf-8")
    try:
        module.collect_evidence_failure(case_root)
    except module.OperationalEvidenceError as exc:
        if exc.code != code:
            raise SystemExit(f"{name}: expected {code}, got {exc.code}")
    else:
        raise SystemExit(f"{name}: invalid run artifact was accepted")


def collect_run_artifact_case(name, value):
    case_root = tmp_root / ("run-positive-" + name.replace(" ", "-"))
    case_root.mkdir()
    (case_root / "operational-evidence.json").write_text(
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True),
        encoding="utf-8")
    return module.collect_evidence_failure(case_root)


case = copy.deepcopy(base_run_artifact)
next(row for row in case["evidence_records"]
     if row["id"] == "proxy-green")["leg"] = "RECEIPT"
try:
    receipt_collection = collect_run_artifact_case("receipt-leg", case)
except module.OperationalEvidenceError:
    raise SystemExit("C04 H1 RED: typed RECEIPT evidence leg rejected")
if (next(row for row in receipt_collection["evidence_records"]
         if row["id"] == "proxy-green")["leg"] != "RECEIPT" or
        receipt_collection["layer_census"].get("RECEIPT") != 1):
    raise SystemExit("C04 H1 RED: typed RECEIPT evidence leg lost")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["failure_records"]
     if row["id"] == "countermeasure-readback")["record_type"] = "Containment"
try:
    containment_collection = collect_run_artifact_case(
        "containment-record", case)
except module.OperationalEvidenceError:
    raise SystemExit("C04 H1 RED: typed Containment failure record rejected")
if next(row for row in containment_collection["failure_records"]
        if row["id"] == "countermeasure-readback")["record_type"] != (
            "Containment"):
    raise SystemExit("C04 H1 RED: typed Containment failure record lost")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["failure_records"]
     if row["id"] == "countermeasure-readback")["record_type"] = "Rerun"
try:
    rerun_collection = collect_run_artifact_case("rerun-record", case)
except module.OperationalEvidenceError:
    raise SystemExit("C04 H1 RED: typed Rerun failure record rejected")
if next(row for row in rerun_collection["failure_records"]
        if row["id"] == "countermeasure-readback")["record_type"] != "Rerun":
    raise SystemExit("C04 H1 RED: typed Rerun failure record lost")

case = copy.deepcopy(base_run_artifact)
countermeasure = next(
    row for row in case["failure_records"]
    if row["id"] == "countermeasure-readback")
countermeasure["recovery_state"] = "OBSERVED"
countermeasure["evidence_ids"] = ["check-attempt-red"]
try:
    collect_run_artifact_case("non-recovery-observed", case)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_RUN_RECOVERY_EVIDENCE":
        raise SystemExit(
            "C04 H2 RED: non-Recovery OBSERVED returned wrong refusal "
            f"{exc.code}")
else:
    raise SystemExit(
        "C04 H2 RED: non-Recovery OBSERVED accepted ATTEMPT evidence")

case = copy.deepcopy(base_run_artifact)
for row in case["evidence_records"]:
    if row["result_class"] == "RED":
        row["result_class"] = "GREEN"
case["first_red_id"] = None
case["residual_ids"] = []
case["failure_records"] = []
try:
    green_only_collection = collect_run_artifact_case("green-only", case)
except module.OperationalEvidenceError:
    raise SystemExit(
        "C04 M1 RED: green-only population lacks typed no-first-RED state")
if (green_only_collection.get("first_red_id", "missing") is not None or
        green_only_collection.get("first_red_state") != "NOT_APPLICABLE" or
        green_only_collection.get("failure_records") != [] or
        any(row["result_class"] == "RED"
            for row in green_only_collection["evidence_records"])):
    raise SystemExit(
        "C04 M1 RED: green-only population fabricated or lost RED absence")


case = copy.deepcopy(base_run_artifact)
case["first_red_id"] = "proxy-green"
expect_run_artifact_failure(
    "green proxy replaced first RED", case, "OE_RUN_EVIDENCE_FIRST_RED")

case = copy.deepcopy(base_run_artifact)
case["weakest_leg_id"] = "proxy-green"
expect_run_artifact_failure(
    "green proxy replaced weakest leg", case, "OE_RUN_EVIDENCE_WEAKEST")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["evidence_records"]
     if row["id"] == "proxy-green")["leg"] = "EFFECT"
expect_run_artifact_failure(
    "proxy promoted to effect", case, "OE_RUN_EVIDENCE_PROXY")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["evidence_records"]
     if row["id"] == "effect-red")["contrary_evidence"] = ["missing"]
expect_run_artifact_failure(
    "contrary evidence reference missing", case,
    "OE_RUN_EVIDENCE_REFERENCE")

case = copy.deepcopy(base_run_artifact)
case["failure_records"] = [
    row for row in case["failure_records"] if row["id"] != "residual-open"]
expect_run_artifact_failure(
    "declared residual disappeared", case, "OE_RUN_FAILURE_REFERENCE")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["failure_records"]
     if row["record_type"] == "Recovery")["evidence_ids"] = [
         "check-attempt-red"]
expect_run_artifact_failure(
    "attempt receipt promoted to recovery", case,
    "OE_RUN_RECOVERY_EVIDENCE")

case = copy.deepcopy(base_run_artifact)
next(row for row in case["failure_records"]
     if row["record_type"] == "Andon")["cause_confidence"] = "CERTAIN"
expect_run_artifact_failure(
    "unsupported cause confidence invented", case, "OE_RUN_FAILURE_INVALID")

missing_artifact_root = tmp_root / "run-artifact-missing"
missing_artifact_root.mkdir()
try:
    module.collect_evidence_failure(missing_artifact_root)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_RUN_ARTIFACT_MISSING":
        raise SystemExit(
            "missing canonical run artifact expected OE_RUN_ARTIFACT_MISSING, "
            f"got {exc.code}")
else:
    raise SystemExit("STATE/transcript-only root was accepted as evidence")

release_fixture_root = fixture_root.parent / "release" / "positive"
release_root = tmp_root / "release-positive"
shutil.copytree(release_fixture_root, release_root)
initialize_repo(release_root)
before_release = fingerprint(release_root)


def forbidden_frozen_refresh(*args, **kwargs):
    raise SystemExit("frozen RELEASE collection invoked external refresh")


original_external_runner = module.run_external_readonly
module.run_external_readonly = forbidden_frozen_refresh
try:
    release_collection = module.collect_release(release_root)
finally:
    module.run_external_readonly = original_external_runner
if fingerprint(release_root) != before_release:
    raise SystemExit("RELEASE collector mutated local/frozen owner artifacts")
if release_collection.get("schema") != "implementaudit-release-collection-v1":
    raise SystemExit("C05 RELEASE collection schema missing")
if (release_collection.get("families") != ["RELEASE"] or
        release_collection.get("establishes") != []):
    raise SystemExit("C05 RELEASE collection gained non-RELEASE authority")
release_repository = release_collection.get("repository", {})
if release_repository != {
        "commit": git(release_root, "rev-parse", "HEAD"),
        "tree": git(release_root, "rev-parse", "HEAD^{tree}"),
        "worktree_state": "CLEAN"}:
    raise SystemExit("local commit/tree/worktree RELEASE identities drift")
release_nodes = {
    row["id"]: row for row in release_collection.get("nodes", [])}
expected_release_types = {
    "Commit", "Tree", "Worktree", "GeneratedArtifact", "Package",
    "Install", "Host", "PullRequest", "Check", "Merge", "Tag",
    "Release", "Asset", "PublicSurface"}
if {row["record_type"] for row in release_nodes.values()} != (
        expected_release_types):
    raise SystemExit("C05 local/external RELEASE layers were collapsed")
if len(release_nodes) != 14:
    raise SystemExit("C05 RELEASE node population drift")
if any(row.get("family") != "RELEASE" or
       row.get("authority_ceiling") != "READ_ONLY_NATIVE_OBSERVATION"
       for row in release_nodes.values()):
    raise SystemExit("C05 RELEASE fact authority ceiling drift")
if release_collection.get("external_boundary") != {
        "capture_identity": "fixture-external-capture-1",
        "source_identity": "github:theislampill/IMPLEMENTAUDIT.md",
        "auth_state": "PRESENT",
        "rate_state": "AVAILABLE",
        "rate_remaining": 4999,
        "pagination_state": "COMPLETE",
        "pagination_pages": 1,
        "object_drift": False,
        "captured_at": "2026-08-20T02:30:00Z",
        "expires_at": "2026-08-20T03:30:00Z",
        "evaluated_at": "2026-08-20T02:31:00Z"}:
    raise SystemExit("C05 external boundary state was hidden or collapsed")
candidate = release_collection.get("candidate", {})
if (candidate.get("state") != "UNVERIFIED" or
        candidate.get("invalidators") != [
            "PUBLIC_PREDECESSOR_DIFFERS_FROM_LOCAL_COMMIT"] or
        candidate.get("local_commit") != release_repository["commit"] or
        candidate.get("public_commit") != "0" * 40):
    raise SystemExit("public predecessor was promoted to a local candidate")
if len(release_collection.get("semantic_sha256", "")) != 64:
    raise SystemExit("C05 RELEASE semantic digest missing")
if module.canonical_json_v1(release_collection) != module.canonical_json_v1(
        module.collect_release(release_root)):
    raise SystemExit("unchanged frozen RELEASE collection is not deterministic")


def release_case_root(name, mutate_capture=None, mutate_local=None):
    root = tmp_root / ("release-case-" + name.replace(" ", "-"))
    shutil.copytree(release_fixture_root, root)
    local_path = root / "release-local.json"
    with local_path.open(encoding="utf-8") as stream:
        local = json.load(stream)
    if mutate_local is not None:
        mutate_local(local)
    local_path.write_text(
        json.dumps(local, ensure_ascii=False, allow_nan=False, sort_keys=True),
        encoding="utf-8")
    capture_path = root / "external-capture.json"
    with capture_path.open(encoding="utf-8") as stream:
        capture = json.load(stream)
    if mutate_capture is not None:
        mutate_capture(capture)
    capture_path.write_text(
        json.dumps(capture, ensure_ascii=False, allow_nan=False, sort_keys=True),
        encoding="utf-8")
    initialize_repo(root)
    return root


def remove_release_type(value, record_type):
    value["records"] = [
        row for row in value["records"]
        if row["record_type"] != record_type]


missing_asset = module.collect_release(release_case_root(
    "missing asset", lambda value: remove_release_type(value, "Asset")))
missing_install = module.collect_release(release_case_root(
    "missing install", mutate_local=lambda value: remove_release_type(
        value, "Install")))
if ("MISSING_RELEASE_LAYER:Asset" not in
        missing_asset["candidate"]["invalidators"] or
        "MISSING_RELEASE_LAYER:Install" not in
        missing_install["candidate"]["invalidators"] or
        missing_asset.get("omissions") != [{
            "record_type": "Asset", "state": "UNKNOWN",
            "invalidator": "MISSING_RELEASE_LAYER:Asset"}] or
        missing_install.get("omissions") != [{
            "record_type": "Install", "state": "UNKNOWN",
            "invalidator": "MISSING_RELEASE_LAYER:Install"}] or
        missing_asset["node_type_census"].get("Asset") != 0 or
        missing_install["node_type_census"].get("Install") != 0):
    raise SystemExit(
        "C05 H2 RED: missing Asset/Install layer was silently omitted")


def assert_external_state(name, mutate_capture, state, invalidator):
    collection = module.collect_release(
        release_case_root(name, mutate_capture))
    external = [
        row for row in collection["nodes"] if row["layer"] == "EXTERNAL"]
    if not external or any(
            row["currentness"] != {
                "state": state, "invalidators": [invalidator]}
            for row in external):
        raise SystemExit(
            f"{name}: external state did not preserve {invalidator}")


assert_external_state(
    "auth absent", lambda value: value.update(auth_state="ABSENT"),
    "UNVERIFIED", "AUTH_ABSENT")
assert_external_state(
    "auth unknown", lambda value: value.update(auth_state="UNKNOWN"),
    "UNVERIFIED", "AUTH_UNKNOWN")
assert_external_state(
    "rate exhausted", lambda value: value["rate"].update(
        state="EXHAUSTED", remaining=0),
    "UNKNOWN", "RATE_LIMITED")
assert_external_state(
    "rate unknown", lambda value: value["rate"].update(state="UNKNOWN"),
    "UNKNOWN", "RATE_UNKNOWN")
assert_external_state(
    "pagination incomplete", lambda value: value["pagination"].update(
        state="INCOMPLETE"),
    "UNKNOWN", "PAGINATION_INCOMPLETE")
assert_external_state(
    "pagination unknown", lambda value: value["pagination"].update(
        state="UNKNOWN"),
    "UNKNOWN", "PAGINATION_UNKNOWN")
assert_external_state(
    "object drift", lambda value: value.update(object_drift=True),
    "STALE", "OBJECT_DRIFT")
assert_external_state(
    "capture expired", lambda value: value.update(
        evaluated_at="2026-08-20T04:00:00Z"),
    "STALE", "CAPTURE_EXPIRED")


def stale_native_with_absent_auth(value):
    value["auth_state"] = "ABSENT"
    pull_request = next(
        row for row in value["records"]
        if row["record_type"] == "PullRequest")
    pull_request["currentness"] = {
        "state": "STALE", "invalidators": ["PAYLOAD_CHANGED"]}


composed_collection = module.collect_release(release_case_root(
    "stale native absent auth", stale_native_with_absent_auth))
composed_pull_request = next(
    row for row in composed_collection["nodes"]
    if row["record_type"] == "PullRequest")
if (composed_pull_request.get("native_currentness") != {
        "state": "STALE", "invalidators": ["PAYLOAD_CHANGED"]} or
        composed_pull_request.get("capture_currentness") != {
        "state": "UNVERIFIED", "invalidators": ["AUTH_ABSENT"]} or
        composed_pull_request.get("currentness") != {
        "state": "STALE",
        "invalidators": ["PAYLOAD_CHANGED", "AUTH_ABSENT"]}):
    raise SystemExit(
        "C05 H3 RED: capture degradation weakened native currentness")

try:
    module.collect_release(release_case_root(
        "impossible timestamp",
        lambda value: value.update(expires_at="2026-99-99T99:99:99Z")))
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_EXTERNAL_CAPTURE_INVALID":
        raise SystemExit(
            f"impossible timestamp returned wrong refusal {exc.code}")
else:
    raise SystemExit("C05 M1 RED: impossible calendar timestamp was fresh")

try:
    module.collect_release(release_case_root(
        "impossible chronology",
        lambda value: value.update(
            captured_at="2026-08-20T04:00:00Z",
            expires_at="2026-08-20T03:30:00Z",
            evaluated_at="2026-08-20T02:31:00Z")))
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_EXTERNAL_CAPTURE_INVALID":
        raise SystemExit(
            f"impossible chronology returned wrong refusal {exc.code}")
else:
    raise SystemExit("C05 M1 RED: impossible capture chronology was fresh")

expiry_equality = module.collect_release(release_case_root(
    "expiry equality",
    lambda value: value.update(evaluated_at=value["expires_at"])))
if any(
        row["currentness"] != {
            "state": "STALE", "invalidators": ["CAPTURE_EXPIRED"]}
        for row in expiry_equality["nodes"] if row["layer"] == "EXTERNAL"):
    raise SystemExit("C05 M1 RED: expiry equality remained fresh")

digest_mismatch_root = release_case_root("local digest mismatch")
(digest_mismatch_root / "artifacts" / "generated.txt").write_text(
    "changed generated bytes\n", encoding="utf-8")
try:
    module.collect_release(digest_mismatch_root)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_RELEASE_LOCAL_DIGEST":
        raise SystemExit(
            "local digest mismatch expected OE_RELEASE_LOCAL_DIGEST, "
            f"got {exc.code}")
else:
    raise SystemExit("changed local generated artifact retained CURRENT")

transport_calls = []


def external_transport(url, headers):
    transport_calls.append((url, headers))
    return {
        "status": 200,
        "headers": {
            "etag": "fixture-pr-etag",
            "x-ratelimit-remaining": "4999",
            "link": ""},
        "body": b'{"id":1,"node_id":"PR_fixture"}',
    }


external_request = {
    "schema": "implementaudit-external-read-request-v1",
    "source": "GITHUB_API",
    "operation": "PULL_REQUEST",
    "path": "/repos/fixture/project/pulls/1",
    "auth_state": "PRESENT",
    "page": 1,
    "per_page": 100,
    "expected_etag": "fixture-pr-etag",
    "captured_at": "2026-08-20T02:30:00Z",
    "expires_at": "2026-08-20T03:30:00Z",
    "evaluated_at": "2026-08-20T02:31:00Z",
}
external_receipt = module.run_external_readonly(
    external_request, external_transport)
if external_receipt.get("schema") != "implementaudit-external-read-capture-v1":
    raise SystemExit("C05 external read capture schema missing")
if external_receipt.get("boundary") != {
        "method": "UNVERIFIED", "network_used": True,
        "write_verb_exposed": "UNKNOWN",
        "transport_trust": "UNTRUSTED_INJECTED"}:
    raise SystemExit("C05 injected transport gained a GET/no-write claim")
if (external_receipt.get("authority_ceiling") !=
        "READ_ONLY_EXTERNAL_CAPTURE" or
        external_receipt.get("establishes") != []):
    raise SystemExit("C05 external capture gained qualification authority")
if external_receipt.get("currentness") != {
        "state": "UNVERIFIED",
        "invalidators": ["UNTRUSTED_INJECTED_TRANSPORT"]}:
    raise SystemExit("untrusted injected transport retained CURRENT")
if len(transport_calls) != 1:
    raise SystemExit("external read boundary did not make exactly one GET")
url, headers = transport_calls[0]
if (url != "https://api.github.com/repos/fixture/project/pulls/1?page=1&per_page=100" or
        set(headers) != {"Accept", "X-GitHub-Api-Version"}):
    raise SystemExit("external runner request escaped its fixed allowlist")

injected_effects = []


def effectful_injected_transport(url, headers):
    injected_effects.append("WRITE_EFFECT")
    return external_transport(url, headers)


injected_receipt = module.run_external_readonly(
    external_request, effectful_injected_transport)
injected_boundary = injected_receipt.get("boundary", {})
if (injected_effects != ["WRITE_EFFECT"] or
        injected_receipt.get("currentness", {}).get("state") == "CURRENT" or
        injected_boundary.get("method") == "GET" or
        injected_boundary.get("write_verb_exposed") is False):
    raise SystemExit(
        "C05 H1 RED: injected transport substantiated GET/no-write CURRENT")


def expect_external_failure(name, request, code):
    try:
        module.run_external_readonly(request, external_transport)
    except module.OperationalEvidenceError as exc:
        if exc.code != code:
            raise SystemExit(f"{name}: expected {code}, got {exc.code}")
    else:
        raise SystemExit(f"{name}: unsafe external request was accepted")


case = copy.deepcopy(external_request)
case["method"] = "POST"
expect_external_failure("caller supplied write verb", case, "OE_EXTERNAL_REQUEST")

case = copy.deepcopy(external_request)
case["path"] = "/repos/fixture/project/issues/1"
expect_external_failure("non-allowlisted external path", case,
                        "OE_EXTERNAL_REQUEST")


def assert_external_capture_state(name, request_changes, response, expected):
    request = copy.deepcopy(external_request)
    request.update(request_changes)
    receipt = module.run_external_readonly(request, lambda _url, _headers: response)
    expected = copy.deepcopy(expected)
    expected["invalidators"].append("UNTRUSTED_INJECTED_TRANSPORT")
    if receipt.get("currentness") != expected:
        raise SystemExit(
            f"{name}: external capture state drift: "
            f"{receipt.get('currentness')!r}")


base_response = {
    "status": 200,
    "headers": {
        "etag": "fixture-pr-etag", "x-ratelimit-remaining": "4999",
        "link": ""},
    "body": b'{"id":1}',
}
case_colliding_response = {
    **base_response,
    "headers": {
        "ETag": "wrong-etag",
        "etag": "fixture-pr-etag",
        "x-ratelimit-remaining": "4999",
        "link": ""},
}
try:
    module.run_external_readonly(
        external_request,
        lambda _url, _headers: case_colliding_response)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_EXTERNAL_RESPONSE":
        raise SystemExit(
            f"case-colliding ETag returned wrong refusal {exc.code}")
else:
    raise SystemExit("C05 M2 RED: case-colliding ETag was accepted")

negative_rate_response = {
    **base_response,
    "headers": {
        **base_response["headers"], "x-ratelimit-remaining": "-1"},
}
try:
    module.run_external_readonly(
        external_request,
        lambda _url, _headers: negative_rate_response)
except module.OperationalEvidenceError as exc:
    if exc.code != "OE_EXTERNAL_RESPONSE":
        raise SystemExit(
            f"negative rate remaining returned wrong refusal {exc.code}")
else:
    raise SystemExit("C05 M2 RED: negative rate remaining was accepted")

assert_external_capture_state(
    "external auth absent", {"auth_state": "ABSENT"},
    {**base_response, "status": 401},
    {"state": "UNVERIFIED", "invalidators": ["AUTH_ABSENT"]})
assert_external_capture_state(
    "external rate exhausted", {},
    {**base_response, "status": 429,
     "headers": {**base_response["headers"], "x-ratelimit-remaining": "0"}},
    {"state": "UNKNOWN", "invalidators": ["RATE_LIMITED"]})
assert_external_capture_state(
    "external pagination incomplete", {},
    {**base_response,
     "headers": {**base_response["headers"],
                 "link": '<https://api.github.com/next>; rel="next"'}},
    {"state": "UNKNOWN", "invalidators": ["PAGINATION_INCOMPLETE"]})
assert_external_capture_state(
    "external object drift", {"expected_etag": "prior-etag"}, base_response,
    {"state": "STALE", "invalidators": ["OBJECT_DRIFT"]})
assert_external_capture_state(
    "external capture expired", {"evaluated_at": "2026-08-20T04:00:00Z"},
    base_response,
    {"state": "STALE", "invalidators": ["CAPTURE_EXPIRED"]})


ZERO64 = "0" * 64
ONE64 = "1" * 64
TWO64 = "2" * 64
ZERO40 = "0" * 40
ONE40 = "1" * 40


def qualification_for(receipt, currentness="CURRENT", invalidators=None):
    qualification = {
        "qualification_identity": "fixture-static-qualification-v1",
        "self_probe_identity": "fixture-bounded-self-probe-v1",
        "wrapper_identity": receipt["collector"]["invocation_identity"],
        "collector_identity": receipt["collector"]["identity"],
        "collector_version": receipt["collector"]["version"],
        "collector_package_sha256": receipt["collector"]["package_sha256"],
        "configuration_sha256": receipt["collector"]["configuration_sha256"],
        "invocation_identity": receipt["collector"]["invocation_identity"],
        "output_schema_identity": receipt["collector"][
            "output_schema_identity"],
        "parser_mode": receipt["collector"]["parser_mode"],
        "trust_mode": receipt["collector"]["trust_mode"],
        "scope_sha256": hashlib.sha256(json.dumps(
            receipt["scope"], ensure_ascii=False, allow_nan=False,
            sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "probe_results": {
            "positive": "PASS", "negative": "PASS", "unsupported": "PASS",
            "parser_error": "PASS", "repeatability": "PASS",
        },
        "currentness": currentness,
        "invalidators": [] if invalidators is None else invalidators,
    }
    qualification["receipt_sha256"] = hashlib.sha256(json.dumps(
        qualification, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()
    return qualification


def refresh_qualification(receipt, currentness="CURRENT", invalidators=None):
    receipt["qualification"] = qualification_for(
        receipt, currentness=currentness, invalidators=invalidators)


def reseal_qualification(qualification):
    payload = dict(qualification)
    payload.pop("receipt_sha256", None)
    qualification["receipt_sha256"] = hashlib.sha256(json.dumps(
        payload, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()


def base_receipt():
    receipt = {
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
            "mapping": None,
        }],
    }
    refresh_qualification(receipt)
    return receipt


def noncurrent_positive_receipt():
    receipt = base_receipt()
    receipt["outcome"] = "PARTIAL"
    del receipt["qualification"]
    for fact in receipt["facts"]:
        fact["state"] = "PARTIAL"
    return receipt


def expect_failure(name, value, code):
    try:
        module.normalize_static_receipt(value)
    except module.OperationalEvidenceError as exc:
        if exc.code != code:
            raise SystemExit(f"{name}: expected {code}, got {exc.code}")
    else:
        raise SystemExit(f"{name}: unsafe static receipt was accepted")


case = base_receipt()
expect_failure(
    "caller self-issued an all-PASS qualification", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")

case = base_receipt()
case["qualification"]["wrapper_identity"] = "caller-changed-wrapper"
reseal_qualification(case["qualification"])
expect_failure(
    "same invocation caller changed and resealed wrapper identity", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")

case = base_receipt()
case["facts"][1]["mapping"] = {
    "work_node_id": "FABRICATED-NODE",
    "relation_type": "EVIDENCE",
    "effect": "INVALIDATE_EVIDENCE",
}
expect_failure(
    "caller supplied a fabricated governed mapping", case,
    "OE_STATIC_MAPPING_FORBIDDEN")

case = base_receipt()
del case["qualification"]
expect_failure(
    "CURRENT external receipt omitted qualification", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")

case = base_receipt()
case["collector"]["package_sha256"] = TWO64
expect_failure(
    "CURRENT qualification bound changed collector bytes", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")

case = base_receipt()
refresh_qualification(
    case, currentness="EXPIRED", invalidators=["qualification expired"])
expect_failure(
    "CURRENT receipt reused expired qualification", case,
    "OE_STATIC_QUALIFICATION_REQUIRED")


normalized = module.normalize_static_receipt(noncurrent_positive_receipt())
if normalized.get("schema") != "implementaudit-static-normalized-v1":
    raise SystemExit("normalized static receipt schema missing")
if normalized.get("outcome") != "PARTIAL":
    raise SystemExit("unqualified external positive receipt escaped non-current")
if normalized.get("normalization_identity") != "canonical_json_v1":
    raise SystemExit("static output normalization identity missing")
if normalized.get("qualification", {}).get("self_probe") is not None:
    raise SystemExit("C02 retained caller-issued qualification authority")
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
if any(fact.get("mapping") is not None for fact in normalized["facts"]):
    raise SystemExit("C02 static normalization invented a governed mapping")
if any(fact.get("work_consequence") != "NONE" for fact in normalized["facts"]):
    raise SystemExit("supported facts invented a work consequence")
if len(normalized.get("semantic_sha256", "")) != 64:
    raise SystemExit("normalized static receipt semantic digest missing")
if module.canonical_json_v1(normalized) != module.canonical_json_v1(
        module.normalize_static_receipt(noncurrent_positive_receipt())):
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
del case["qualification"]
case["scope"]["parser_complete"] = False
case["diagnostics"]["errors"] = ["src/broken.py: invalid syntax"]
case["facts"] = []
parser_error = module.normalize_static_receipt(case)
if parser_error["outcome"] != "PARSER_ERROR" or not parser_error["facts"]:
    raise SystemExit("parser error became an empty graph")
if parser_error["facts"][0].get("kind") != "PARSER_ERROR_OBSERVATION":
    raise SystemExit("parser-error non-empty control drift")

left = noncurrent_positive_receipt()
left["facts"] = [left["facts"][0]]
right = noncurrent_positive_receipt()
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
del case["qualification"]
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
del case["qualification"]
case["facts"] = []
not_installed = module.normalize_static_receipt(case)
if (not_installed["outcome"] != "NOT_INSTALLED" or
        not_installed["facts"][0].get("kind") != "TOOL_UNAVAILABLE_OBSERVATION"):
    raise SystemExit("tool absence fallback drift")

case = base_receipt()
case["outcome"] = "PARTIAL"
case["diagnostics"]["skipped"] = ["src/generated.py"]
del case["qualification"]
partial = module.normalize_static_receipt(case)
if partial["outcome"] != "PARTIAL" or partial["diagnostics"]["skipped"] != [
        "src/generated.py"]:
    raise SystemExit("partial degradation was not preserved")
if any(fact.get("state") == "CURRENT" for fact in partial["facts"]):
    raise SystemExit("non-current external receipt retained CURRENT facts")
PY

printf 'operational-evidence-contract.test: ok\n'
