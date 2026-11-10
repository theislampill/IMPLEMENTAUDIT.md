"""Thin same-host no-load canary. Import is inert; runtime requires an exact grant.

The caller reuses preparation02 and preparation05 freeze03 without edits. It
never executes bwrap, a model, a policy writer, or a policy-namespace operation.
The proposal is not issued authority: root receives the actual owner decision
and DG16 Pro resource concurrence before the one approved publication.
"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import time
import types

IDENTITY = "dg17-9077-codex20-preparation-canary06"
DIRECTORY = "qualification/dg17-codex-preparation-canary06"
PREP = "qualification/dg17-codex-apparmor-preparation05"
HOST = "qualification/dg17-codex-host-preparation02"
REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg17-isolated-episode-01-20261106"
BASE = "b3aa58580b2c22ef61e5432531f62adc1f562fda"
FREEZE_SHA = "b1e0474308bee81532f8bb0777f4ebbf0f423cd07bbd6cf8c9847436cad63fdc"
BRIDGE_SHA = "2a4320fb9765e06c498962e7ad893060678cd365c7428997816f2888518e66d9"
PREPARER_SHA = "03afcc3f26311249459d019d15dd55fd835e99b9cc2b6f3ff9f748cf44436488"
B64_SHA = "06cf45cd324bdaab73c9f38def8288af80bdd395bf926c2a08c10e2a28625f65"
PROFILE_SHA = "11d39094f044f0cda0febb3ad517b830301da6b2ce929664af09ee9e4dd264f9"
HELPER_SHA = "e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71"
SOURCE_LIMIT = 4194304
FAILURE_CODES = frozenset({
    "CALLER_OPERATION_REFUSED", "CURRENT_PARENT_HOST_JOIN", "EXTERNAL_SOURCE_PIN",
    "FROZEN_RECEIPT_REGENERATION", "FROZEN_RECEIPT_STATUS", "HELPER_PREPARATION_FAILED",
    "HELPER_PUBLIC_BINDING", "HELPER_PUBLIC_BOUND", "HELPER_PUBLIC_CUSTODY", "HELPER_PUBLIC_SCOPE",
    "HELPER_PUBLIC_SHAPE", "HELPER_PUBLIC_STATUS", "INPUT_BOUND", "INPUT_DRIFT", "JSON_BOUND",
    "JSON_DUPLICATE", "JSON_ENCODING", "JSON_NONFINITE", "JSON_SYNTAX", "OWNED_FROZEN_DOCUMENT_JOIN",
    "PHYSICAL_INPUT", "QUALIFIED_SOURCE_REUSE", "RUNNING_CALLER_PIN", "SOURCE_AGGREGATE",
    "SOURCE_BODY_PIN", "SOURCE_MANIFEST", "SOURCE_PATH", "SOURCE_PATHSET", "SOURCE_POPULATION",
    "SOURCE_ROOT", "SOURCE_ROW", "SOURCE_VALUE",
})
GRANT_FIXED = {
    "schema": "dg17.apparmor.preparation-canary-owner-grant.v1",
    "repository": REPOSITORY, "branch": BRANCH, "job_name": "dg17-bounded", "attempt": 1,
    "base_commit": BASE, "preparation_manifest_sha256": FREEZE_SHA,
    "profile_bytes": 1936, "profile_sha256": PROFILE_SHA,
    "helper_bytes": 72160, "helper_sha256": HELPER_SHA,
    "authorized_effects": ["CONDITIONAL_EXCLUSIVE_HELPER_PLACEMENT", "EXACT_FREEZE03_NO_LOAD_PREPARATION"],
    "host_attempt_limit": 1, "helper_attempt_limit": 0, "model_calls": 0,
    "policy_mutations": 0, "new_policy_namespaces": 0, "max_host_hold_seconds": 1200,
    "resource_concurrence_required_before_publication": True,
}


class Refusal(ValueError):
    pass


def need(ok, code):
    if ok is not True:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def enc(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def strict(raw, bound):
    need(type(raw) is bytes and 0 < len(raw) <= bound, "JSON_BOUND")
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON_DUPLICATE")
            result[key] = value
        return result
    def reject(_):
        raise Refusal("JSON_NONFINITE")
    try:
        value = json.loads(raw.decode("ascii"), object_pairs_hook=pairs, parse_constant=reject)
    except (UnicodeError, json.JSONDecodeError):
        raise Refusal("JSON_SYNTAX") from None
    need(enc(value) == raw, "JSON_ENCODING")
    return value


def context(value):
    need(type(value) is dict and set(value) ==
         {"repository", "branch", "job_name", "attempt", "run_id", "workflow_commit"}, "CONTEXT")
    need(value["repository"] == REPOSITORY and value["branch"] == BRANCH and
         value["job_name"] == "dg17-bounded" and type(value["attempt"]) is int and value["attempt"] == 1,
         "CONTEXT")
    need(type(value["run_id"]) is str and re.fullmatch(r"[1-9][0-9]{0,18}", value["run_id"]) is not None and
         type(value["workflow_commit"]) is str and re.fullmatch(r"[0-9a-f]{40}", value["workflow_commit"]) is not None,
         "CONTEXT")


def receive_grant(raw, expected_sha, source_sha, expected_context):
    context(expected_context)
    need(type(expected_sha) is str and re.fullmatch(r"[0-9a-f]{64}", expected_sha) is not None and
         type(source_sha) is str and re.fullmatch(r"[0-9a-f]{64}", source_sha) is not None and
         type(raw) is bytes and sha(raw) == expected_sha, "EXTERNAL_OWNER_GRANT_PIN")
    value = strict(raw, 4096)
    need(type(value) is dict and set(value) == set(GRANT_FIXED) | {"decision_id", "source_manifest_sha256"},
         "OWNER_GRANT_FIELDS")
    need(all(value[key] == fixed and type(value[key]) is type(fixed) for key, fixed in GRANT_FIXED.items()),
         "OWNER_GRANT_SCOPE")
    need(value["source_manifest_sha256"] == source_sha and type(value["decision_id"]) is str and
         re.fullmatch(r"[ -~]{1,128}", value["decision_id"]) is not None, "OWNER_GRANT_BINDING")
    return value


def identity(info):
    return tuple(getattr(info, "st_" + key) for key in
                 ("dev", "ino", "mode", "uid", "gid", "nlink", "size", "mtime_ns", "ctime_ns"))


def read(path, bound):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, "PHYSICAL_INPUT")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 < before.st_size <= bound,
             "INPUT_BOUND")
        with os.fdopen(os.dup(fd), "rb") as stream:
            raw = stream.read(bound + 1)
        need(len(raw) == before.st_size and identity(before) == identity(os.fstat(fd)) == identity(path.lstat()),
             "INPUT_DRIFT")
        return raw
    finally:
        os.close(fd)


def receive_source(source, expected_sha):
    source = Path(source)
    need(source.is_absolute() and source.resolve(strict=True) == source, "SOURCE_ROOT")
    raw = read(source / DIRECTORY / "INPUT_PINS.json", 16384)
    need(type(expected_sha) is str and re.fullmatch(r"[0-9a-f]{64}", expected_sha) is not None and
         sha(raw) == expected_sha, "EXTERNAL_SOURCE_PIN")
    manifest = strict(raw, 16384)
    need(type(manifest) is dict and set(manifest) == {"schema", "files"} and
         manifest["schema"] == "dg17.apparmor.preparation-canary-source.v1", "SOURCE_MANIFEST")
    rows = manifest["files"]
    need(type(rows) is list and 11 <= len(rows) <= 64, "SOURCE_POPULATION")
    bodies, paths, total = {}, [], len(raw)
    for row in rows:
        need(type(row) is dict and set(row) == {"path", "bytes", "sha256"}, "SOURCE_ROW")
        path = row["path"]
        need(type(path) is str and 0 < len(path) <= 512 and path.isascii() and not path.startswith("/") and
             "\\" not in path and all(part not in ("", ".", "..") for part in path.split("/")) and
             str(PurePosixPath(path)) == path and path != DIRECTORY + "/INPUT_PINS.json", "SOURCE_PATH")
        need(type(row["bytes"]) is int and 0 < row["bytes"] <= SOURCE_LIMIT and type(row["sha256"]) is str and
             re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None, "SOURCE_VALUE")
        paths.append(path); total += row["bytes"]
        need(total <= SOURCE_LIMIT, "SOURCE_AGGREGATE")
        body = read(source / path, row["bytes"])
        need(len(body) == row["bytes"] and sha(body) == row["sha256"], "SOURCE_BODY_PIN")
        bodies[path] = body
    need(paths == sorted(set(paths)), "SOURCE_PATHSET")
    pins = {PREP + "/INPUT_PINS.json": FREEZE_SHA, PREP + "/bridge.py": BRIDGE_SHA,
            HOST + "/prepare.py": PREPARER_SHA, HOST + "/BWRAP_INPUT.b64": B64_SHA}
    need(all(path in bodies and sha(bodies[path]) == pin for path, pin in pins.items()), "QUALIFIED_SOURCE_REUSE")
    need(DIRECTORY + "/caller.py" in bodies and Path(__file__).absolute() == source / DIRECTORY / "caller.py" and
         read(Path(__file__).absolute(), 65536) == bodies[DIRECTORY + "/caller.py"] and
         globals().get("_RECEIVED_CALLER_BYTES", bodies[DIRECTORY + "/caller.py"]) == bodies[DIRECTORY + "/caller.py"],
         "RUNNING_CALLER_PIN")
    return bodies


def loaded(raw, path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), value.__dict__)
    return value


def load_components(source, bodies):
    bridge = loaded(bodies[PREP + "/bridge.py"], source / PREP / "bridge.py", "canary_frozen_bridge")
    admission, utility, episode, _, receiver, binding, _, _ = bridge.load(source, FREEZE_SHA)
    # prepare.main and bridge.load require their actual qualified __file__ paths.
    preparer = loaded(bodies[HOST + "/prepare.py"], source / HOST / "prepare.py", "canary_qualified_preparer")
    return bridge, admission, episode, preparer, receiver, binding


class PublicCapture(io.StringIO):
    def write(self, text):
        need(type(text) is str and text.isascii() and self.tell() + len(text) <= 16640, "HELPER_PUBLIC_BOUND")
        return super().write(text)


def helper_document(preparer, status, text, expected_context):
    need(type(status) is int and status in (0, 1) and type(text) is str and text.startswith(preparer.PREFIX),
         "HELPER_PUBLIC_SHAPE")
    raw = text[len(preparer.PREFIX):].encode("ascii")
    value = strict(raw, 16384)
    fields = {"schema", "status", "context", "package_sha256", "member_sha256", "member_bytes",
              "source_sha256", "root_source_sha256", "input_transport_sha256", "before", "after",
              "root_capture", "root_ready", "root_created", "root_tools", "host_identity",
              "member_decoded", "root_calls", "failure", "native_execution", "security_policy_changed",
              "package_scripts_executed", "package_companions_applied", "existing_helper_modified",
              "host_teardown_observed", "authority", "original_awards"}
    need(type(value) is dict and set(value) == fields and value.get("schema") == "dg17.codex20.host-preparation.v2" and
         value.get("context") in (None, expected_context) and value.get("source_sha256") in (None, PREPARER_SHA) and
         value.get("member_sha256") == HELPER_SHA and value.get("member_bytes") == 72160 and
         value.get("package_sha256") == preparer.PACKAGE_SHA256 and
         value.get("root_source_sha256") == preparer.ROOT_SOURCE_SHA256 and
         value.get("input_transport_sha256") == B64_SHA and
         value.get("authority") == "NONE" and value.get("original_awards") == [] and
         value.get("host_teardown_observed") is False, "HELPER_PUBLIC_BINDING")
    for name in ("native_execution", "security_policy_changed", "package_scripts_executed",
                 "package_companions_applied", "existing_helper_modified"):
        need(value.get(name) is False, "HELPER_PUBLIC_SCOPE")
    success = value.get("status") in ("EXISTING_VALID_UNCHANGED", "CREATED_EXACT_MEMBER_AND_CUSTODY_RECEIVED")
    need((status == 0) is success and (success or value.get("status") == "FAILED_OR_UNRECEIVED"), "HELPER_PUBLIC_STATUS")
    if success:
        after = value.get("after")
        need(value.get("context") == expected_context and value.get("source_sha256") == PREPARER_SHA and
             value.get("failure") is None and type(after) is dict and after.get("status") == "PHYSICAL_HELPER_ADMITTED" and
             after.get("bytes") == 72160 and after.get("sha256") == HELPER_SHA, "HELPER_PUBLIC_CUSTODY")
    return value


def receive_frozen(source, source_sha, expected_context, returned, components):
    bridge, admission, episode, _, receiver, binding = components
    public = Path(os.environ["RUNNER_TEMP"]) / ("dg17-apparmor-" + expected_context["run_id"] + "-a1") / "public"
    result_raw, receipt_raw = read(public / "RESULT.json", 65536), read(public / "RECEIPT.json", 65536)
    result, receipt = strict(result_raw, 65536), strict(receipt_raw, 65536)
    need(type(returned) is dict and returned == receipt and enc(returned) == receipt_raw and
         receipt.get("observation_sha256") == sha(result_raw), "OWNED_FROZEN_DOCUMENT_JOIN")
    receive_source(source, source_sha)
    bridge.actual_context(expected_context)
    current_host_sha = None
    if receipt.get("status") == "RECEIVED_OWNED_NO_LOAD_PREPARATION":
        current_host = admission.PhysicalIO(time.monotonic() + 2).host_binding()
        need(result.get("parent_host") == current_host, "CURRENT_PARENT_HOST_JOIN")
        current_host_sha = sha(enc(current_host))
        now = time.monotonic_ns()
        received = bridge.receive_result(result, expected_context, binding, episode, receiver, now)
    elif receipt.get("status") == "RECEIVED_BOUNDED_FAILURE_ONLY":
        now = time.monotonic_ns()
        received = bridge.receive_failure(result, expected_context, binding, receiver)
    else:
        raise Refusal("FROZEN_RECEIPT_STATUS")
    need(received == receipt, "FROZEN_RECEIPT_REGENERATION")
    return {"state": "RECEIVED", "status": receipt["status"],
            "result": {"bytes": len(result_raw), "sha256": sha(result_raw)},
            "receipt": {"bytes": len(receipt_raw), "sha256": sha(receipt_raw)},
            "received_at_ns": now, "current_parent_host_sha256": current_host_sha}


def unreceived_frozen_facts(expected_context):
    public = Path(os.environ["RUNNER_TEMP"]) / ("dg17-apparmor-" + expected_context["run_id"] + "-a1") / "public"
    result = {"state": "UNAVAILABLE", "status": None, "result": None, "receipt": None,
              "received_at_ns": None, "current_parent_host_sha256": None}
    for key, name in (("result", "RESULT.json"), ("receipt", "RECEIPT.json")):
        try:
            raw = read(public / name, 65536)
        except (OSError, Refusal):
            continue
        result[key] = {"bytes": len(raw), "sha256": sha(raw)}
        result["state"] = "UNRECEIVED"
    return result


def receive_public(canary_raw, frozen_result_raw, frozen_receipt_raw, expected_context,
                   expected_manifest_sha256, owner_grant_raw, expected_owner_grant_sha256, source_root):
    """Archive validation only; uses the recorded on-host time, never this host's clock."""
    receive_grant(owner_grant_raw, expected_owner_grant_sha256, expected_manifest_sha256, expected_context)
    source = Path(source_root)
    bodies = receive_source(source, expected_manifest_sha256)
    bridge, _, episode, preparer, receiver, binding = load_components(source, bodies)
    value = strict(canary_raw, 32768)
    fields = {"schema", "candidate_identity", "status", "stage", "failure", "context", "source_manifest_sha256",
              "owner_grant_sha256", "preparation_manifest_sha256", "host_preparation", "frozen",
              "source_bookends_equal", "helper_attempts", "model_calls", "policy_mutations",
              "new_policy_namespaces", "native_execution", "authority", "original14",
              "uses_transferable_readiness", "original_awards"}
    need(type(value) is dict and set(value) == fields and value["schema"] == "dg17.apparmor.preparation-canary.v1" and
         value["candidate_identity"] == IDENTITY and value["context"] == expected_context and
         value["source_manifest_sha256"] == expected_manifest_sha256 and
         value["owner_grant_sha256"] == expected_owner_grant_sha256 and value["preparation_manifest_sha256"] == FREEZE_SHA,
         "CANARY_FIELDS")
    for key in ("helper_attempts", "model_calls", "policy_mutations", "new_policy_namespaces"):
        need(type(value[key]) is int and value[key] == 0, "CANARY_SCOPE")
    need(value["native_execution"] is False and value["uses_transferable_readiness"] is False and
         value["authority"] == "NONE" and value["original14"] == "REQUIRED_UNMET_UNWAIVED_UNRETIRED" and
         value["original_awards"] == [] and type(value["source_bookends_equal"]) is bool, "CANARY_SCOPE")
    host = value["host_preparation"]
    need(type(host) is dict and set(host) == {"state", "returncode", "document"}, "CANARY_HELPER_FIELDS")
    if host["state"] == "RECEIVED":
        helper_document(preparer, host["returncode"], preparer.PREFIX + enc(host["document"]).decode("ascii"), expected_context)
    else:
        need(host == {"state": "UNAVAILABLE", "returncode": None, "document": None}, "CANARY_HELPER_UNAVAILABLE")
    frozen = value["frozen"]
    need(type(frozen) is dict and set(frozen) == {"state", "status", "result", "receipt", "received_at_ns",
                                                "current_parent_host_sha256"}, "CANARY_FROZEN_FIELDS")
    for key, raw in (("result", frozen_result_raw), ("receipt", frozen_receipt_raw)):
        fact = frozen[key]
        if fact is None:
            need(raw is None, "CANARY_ARTIFACT_POPULATION")
        else:
            need(type(fact) is dict and set(fact) == {"bytes", "sha256"} and type(raw) is bytes and
                 0 < len(raw) <= 65536 and type(fact["bytes"]) is int and fact["bytes"] == len(raw) and
                 fact["sha256"] == sha(raw), "CANARY_ARTIFACT_JOIN")
    if frozen["state"] == "RECEIVED":
        need(value["stage"] == "FROZEN_RECEIVING" and value["source_bookends_equal"] is True and
             value["failure"] is None and
             host["state"] == "RECEIVED" and host["returncode"] == 0 and type(frozen["received_at_ns"]) is int and
             0 <= frozen["received_at_ns"] <= 9223372036854775807, "CANARY_RECEIVING")
        result, receipt = strict(frozen_result_raw, 65536), strict(frozen_receipt_raw, 65536)
        if frozen["status"] == "RECEIVED_OWNED_NO_LOAD_PREPARATION":
            need(value["status"] == "CANARY_PREPARATION_RECEIVED" and
                 frozen["current_parent_host_sha256"] == sha(enc(result.get("parent_host"))), "CANARY_PARENT_JOIN")
            received = bridge.receive_result(result, expected_context, binding, episode, receiver, frozen["received_at_ns"])
        else:
            need(frozen["status"] == "RECEIVED_BOUNDED_FAILURE_ONLY" and
                 value["status"] == "CANARY_BOUNDED_FAILURE_RECEIVED" and
                 frozen["current_parent_host_sha256"] is None, "CANARY_FAILURE_JOIN")
            received = bridge.receive_failure(result, expected_context, binding, receiver)
        need(received == receipt and receipt["observation_sha256"] == sha(frozen_result_raw), "CANARY_FROZEN_REGENERATION")
    else:
        need(value["status"] == "CANARY_PREPARATION_UNRECEIVED" and value["source_bookends_equal"] is False and
             value["stage"] in ("HOST_PREPARATION", "NO_LOAD_PREPARATION", "FROZEN_RECEIVING") and
             frozen["status"] is None and frozen["received_at_ns"] is None and
             frozen["current_parent_host_sha256"] is None and
             frozen["state"] == ("UNAVAILABLE" if frozen["result"] is None and frozen["receipt"] is None else "UNRECEIVED"),
             "CANARY_UNRECEIVED")
        failure = value["failure"]
        need(type(failure) is dict and set(failure) == {"code"} and type(failure["code"]) is str and
             failure["code"] in FAILURE_CODES, "CANARY_CALLER_FAILURE")
        if value["stage"] != "HOST_PREPARATION":
            need(host["state"] == "RECEIVED" and host["returncode"] == 0, "CANARY_STAGE_ORDER")
    return {"schema": "dg17.apparmor.preparation-canary-receipt.v1",
            "status": "RECEIVED_CANARY_SOURCE_AND_ARTIFACT_BINDINGS_ONLY", "canary_status": value["status"],
            "candidate_identity": IDENTITY, "canary_sha256": sha(canary_raw), "context": dict(expected_context),
            "source_manifest_sha256": expected_manifest_sha256, "owner_grant_sha256": expected_owner_grant_sha256,
            "new_host_observation": False, "authority": "NONE", "original14": value["original14"]}


def run_parent(source_root, expected_manifest_sha256, expected_context, owner_grant_raw, expected_owner_grant_sha256):
    source = Path(source_root)
    receive_grant(owner_grant_raw, expected_owner_grant_sha256, expected_manifest_sha256, expected_context)
    need(source == Path(os.environ["GITHUB_WORKSPACE"]) / "packet", "HOSTED_SOURCE_PATH")
    bodies = receive_source(source, expected_manifest_sha256)
    components = load_components(source, bodies)
    bridge, _, _, preparer, _, _ = components
    bridge.actual_context(expected_context)
    runner = Path(os.environ["RUNNER_TEMP"])
    need(runner.is_absolute() and runner.resolve(strict=True) == runner, "HOSTED_OUTPUT_PATH")
    output = runner / ("dg17-preparation-canary-" + expected_context["run_id"] + "-a1")
    output.mkdir(mode=0o700); (output / "public").mkdir(mode=0o700)
    value = {
        "schema": "dg17.apparmor.preparation-canary.v1", "candidate_identity": IDENTITY,
        "status": "CANARY_PREPARATION_UNRECEIVED", "stage": "HOST_PREPARATION", "failure": None,
        "context": dict(expected_context), "source_manifest_sha256": expected_manifest_sha256,
        "owner_grant_sha256": expected_owner_grant_sha256, "preparation_manifest_sha256": FREEZE_SHA,
        "host_preparation": {"state": "UNAVAILABLE", "returncode": None, "document": None},
        "frozen": {"state": "UNAVAILABLE", "status": None, "result": None, "receipt": None,
                   "received_at_ns": None, "current_parent_host_sha256": None},
        "source_bookends_equal": False, "helper_attempts": 0, "model_calls": 0,
        "policy_mutations": 0, "new_policy_namespaces": 0, "native_execution": False,
        "authority": "NONE", "original14": "REQUIRED_UNMET_UNWAIVED_UNRETIRED",
        "uses_transferable_readiness": False, "original_awards": [],
    }
    try:
        capture = PublicCapture()
        with contextlib.redirect_stdout(capture):
            status = preparer.main()
        document = helper_document(preparer, status, capture.getvalue(), expected_context)
        value["host_preparation"] = {"state": "RECEIVED", "returncode": status, "document": document}
        need(status == 0, "HELPER_PREPARATION_FAILED")
        value["stage"] = "NO_LOAD_PREPARATION"
        receive_source(source, expected_manifest_sha256)
        returned = bridge.run_parent(source, FREEZE_SHA, expected_context)
        value["stage"] = "FROZEN_RECEIVING"
        value["frozen"] = receive_frozen(source, expected_manifest_sha256, expected_context, returned, components)
        value["source_bookends_equal"] = True
        value["status"] = ("CANARY_PREPARATION_RECEIVED" if value["frozen"]["status"] ==
                           "RECEIVED_OWNED_NO_LOAD_PREPARATION" else "CANARY_BOUNDED_FAILURE_RECEIVED")
    except Exception as exc:
        # Exact component receipts retain their existing bounded failure evidence.
        # No exception text or private stream is made public by this caller.
        code = exc.args[0] if type(exc) is Refusal and len(exc.args) == 1 else None
        value["failure"] = {"code": code if type(code) is str and code in FAILURE_CODES else "CALLER_OPERATION_REFUSED"}
        value["frozen"] = unreceived_frozen_facts(expected_context)
    raw = enc(value)
    need(len(raw) <= 32768, "CANARY_PUBLIC_BOUND")
    bridge.write(output / "public" / "CANARY.json", raw, 32768)
    return value
