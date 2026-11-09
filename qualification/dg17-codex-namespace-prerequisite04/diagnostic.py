"""DG17 hosted exact namespace diagnostic; imports are inert.

Only the fixed hosted push context may call main. It reuses the exact retained
physical-helper preparation/capsule primitives, never their old executable
mains. Native Codex, package installation, policy changes and model operations
are absent from this program.
"""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import sys
import time
import types

IDENTITY = "dg17-9077-codex20-namespace-prerequisite04"
SCHEMA = "dg17.codex20.namespace-prerequisite.v1"
PREFIX = "DG17_NAMESPACE_PREREQUISITE_V1 "
REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg17-isolated-episode-01-20261106"
PARENT_COMMIT = "5b144385995ac10c240d90774434cc884ecfd166"
PARENT_TREE = "9b5479424caf453050168ec478993f99fd1e1906"
WORKFLOW_PATH = ".github/workflows/dg17-codex-namespace-prerequisite04.yml"
DIRECTORY = "qualification/dg17-codex-namespace-prerequisite04"
INPUT_PINS_SHA256 = "c4cd036976e02fd134730941d3165a4184ca8ebe75ed6cc228d137a6432c1ae6"
PREPARER_SHA256 = "03afcc3f26311249459d019d15dd55fd835e99b9cc2b6f3ff9f748cf44436488"
EPISODE_SHA256 = "4dc7aacb793e1d65ed1fa51335800fbfaa7c9af777369877f2828113006a8466"
UTILITY_SHA256 = "429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c"
CAPSULE_SCRIPT_SHA256 = "e4f116003174fe1400960da43b32594157826760ca31c3781a6b765ade82ed0a"
CAPSULE_CODE_SHA256 = "fbc15a7cdb0ed37ceb87162b49400a18b8fd2ed2f80a124fb131c067a8d7cc93"
LOOPBACK_INITIALIZER_SHA256 = "e04d2c081998a08de53cf0f214cd1b9ae531fc5abc1d1bf79206b43c69570433"
UPSTREAM_SHA256 = "ec31c6bc4b844183ae3c6e5fcea5e97db95e6f26cfaeb4c9bedb37cdf01534ee"
LIMITS = {"probe_timeout_ms": 500, "poll_interval_ms": 50, "stderr_limit_bytes": 65536,
          "outer_stream_limit_bytes": 32768, "outer_timeout_seconds": 30,
          "root_watchdog_seconds": 20, "root_kill_after_seconds": 5,
          "owned_live_child_limit": 8, "owned_cleanup_seconds": 4,
          "worker_result_limit_bytes": 16384, "public_result_limit_bytes": 65536,
          "model_calls": 0, "helper_attempt_limit": 1}


class Refusal(ValueError):
    pass


def need(ok, code):
    if ok is not True: raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def read_regular(path, bound):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, "PHYSICAL_PATH")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(descriptor)
        identity = lambda v: (v.st_dev, v.st_ino, v.st_mode, v.st_uid, v.st_gid, v.st_nlink, v.st_size, v.st_mtime_ns, v.st_ctime_ns)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= bound, "READ_BOUND")
        raw = bytearray()
        while len(raw) <= bound:
            part = os.read(descriptor, min(65536, bound + 1 - len(raw)))
            if not part: break
            raw.extend(part)
        need(len(raw) == before.st_size and identity(before) == identity(os.fstat(descriptor)) == identity(path.lstat()), "READ_DRIFT")
        return bytes(raw)
    finally: os.close(descriptor)


def context_from_environment(env):
    expected = {"GITHUB_ACTIONS": "true", "RUNNER_ENVIRONMENT": "github-hosted", "GITHUB_REPOSITORY": REPOSITORY,
                "GITHUB_REF": "refs/heads/" + BRANCH, "GITHUB_EVENT_NAME": "push", "GITHUB_RUN_ATTEMPT": "1",
                "GITHUB_JOB": "dg17-bounded", "GITHUB_WORKFLOW_REF": REPOSITORY + "/" + WORKFLOW_PATH + "@refs/heads/" + BRANCH}
    need(all(env.get(key) == value for key, value in expected.items()), "HOSTED_CONTEXT")
    need(re.fullmatch("[1-9][0-9]{0,18}", env.get("GITHUB_RUN_ID", "")) is not None
         and re.fullmatch("[0-9a-f]{40}", env.get("GITHUB_SHA", "")) is not None
         and env["GITHUB_SHA"] != PARENT_COMMIT, "HOSTED_IDENTITY")
    return {"repository": REPOSITORY, "branch": BRANCH, "run_id": env["GITHUB_RUN_ID"], "attempt": 1,
            "workflow_commit": env["GITHUB_SHA"], "job_name": "dg17-bounded"}


def load_worker(source):
    raw = read_regular(source / DIRECTORY / "INPUT_PINS.json", 16384)
    need(sha(raw) == INPUT_PINS_SHA256, "INPUT_MANIFEST_PIN")
    # This manifest is already digest-bound by the reviewed outer caller. The
    # worker then performs its strict duplicate/population/body admission too.
    pins = json.loads(raw)
    rows = pins.get("files")
    need(type(rows) is list and len(rows) == 5, "INPUT_MANIFEST_POPULATION")
    matching = [row for row in rows if type(row) is dict and row.get("path") == DIRECTORY + "/worker.py"]
    need(len(matching) == 1 and type(matching[0].get("bytes")) is int and 0 < matching[0]["bytes"] <= 1048576, "WORKER_MANIFEST_ROW")
    body = read_regular(source / DIRECTORY / "worker.py", matching[0]["bytes"])
    need(len(body) == matching[0]["bytes"] and sha(body) == matching[0]["sha256"], "WORKER_PIN")
    module = types.ModuleType("dg17_namespace_worker")
    module.__file__ = str(source / DIRECTORY / "worker.py")
    exec(compile(body, module.__file__, "exec"), module.__dict__)
    return module


def source_snapshot(source, w):
    rows, bodies = w.input_sources(source, INPUT_PINS_SHA256)
    rows = [dict(row) for row in rows]
    for name, bound in ((DIRECTORY + "/INPUT_PINS.json", 16384), (DIRECTORY + "/diagnostic.py", 1048576), (WORKFLOW_PATH, 65536)):
        raw = read_regular(source / name, bound)
        rows.append({"path": name, "bytes": len(raw), "sha256": sha(raw)})
    rows.sort(key=lambda row: row["path"])
    need(len(rows) == 8 and sum(row["bytes"] for row in rows) <= 1048576, "SOURCE_AGGREGATE")
    need(sha(bodies[w.PREPARER_PATH]) == PREPARER_SHA256 and sha(bodies[w.EPISODE_PATH]) == EPISODE_SHA256
         and sha(bodies[w.UTILITY_PATH]) == UTILITY_SHA256, "REUSED_COMPONENT_PIN")
    return rows, bodies


def worker_arguments(source, output, uid, gid, host, context_sha):
    return ["--source", str(source), "--output", str(output), "--helper", "/usr/bin/bwrap",
            "--helper-sha256", "e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71",
            "--capsule-admission", str(output / "private/CAPSULE_ADMISSION.json"),
            "--expected-uid", str(uid), "--expected-gid", str(gid), "--parent-netns", host["parent_net_namespace"],
            "--parent-mntns", host["parent_mount_namespace"], "--source-pins-sha256", INPUT_PINS_SHA256,
            "--context-sha256", context_sha, "--upstream-sha256", UPSTREAM_SHA256]


def capsule_argv(source, output, uid, gid, host, args, e):
    need(len(args) == 24 and len([str(uid), str(gid), e.CAPSULE_CODE, str(output / "private/CAPSULE_ADMISSION.json"),
             str(output / "private/CAPSULE_RESULT.json"), host["parent_mount_namespace"], host["parent_net_namespace"],
             str(source / DIRECTORY / "worker.py"), *args]) == 32, "UNCHANGED_CAPSULE_ARGUMENTS")
    return ["/usr/bin/sudo", "-n", "/usr/bin/timeout", "--signal=TERM", "--kill-after=5s", "20s",
            "/usr/bin/unshare", "--mount", "--net", "--propagation", "private", "--",
            "/usr/bin/bash", "--noprofile", "--norc", "-c", e.CAPSULE_SCRIPT, "dg17-private-view",
            str(uid), str(gid), e.CAPSULE_CODE, str(output / "private/CAPSULE_ADMISSION.json"),
            str(output / "private/CAPSULE_RESULT.json"), host["parent_mount_namespace"], host["parent_net_namespace"],
            str(source / DIRECTORY / "worker.py"), *args]


def outer_projection(record, capture_failed, retained, w):
    """Fixed export; optional utility refusal code/census stay in private record."""
    cleanup = record.get("cleanup")
    if cleanup is not None:
        keys = ("echild", "pidfd_signals", "retained_status_count", "retained_statuses_sha256", "reaped_statuses", "reaped_statuses_truncated")
        cleanup = {key: cleanup[key] for key in keys}; w.validate_cleanup(cleanup)
    result = {"process_started": record.get("process_started") is True, "pidfd_acquired": record.get("pidfd_acquired") is True,
              "returncode": record.get("returncode"), "start_errno": record.get("start_errno"),
              "timeout": record.get("timeout") is True, "output_bound_exceeded": record.get("output_bound_exceeded") is True,
              "internal_failure": capture_failed or record.get("internal_failure") is not None,
              "streams_complete": record.get("streams_complete") is True, "private_streams_retained": retained,
              "stdout_bytes": record.get("stdout_bytes", 0), "stdout_sha256": record.get("stdout_sha256", sha(b"")),
              "stderr_bytes": record.get("stderr_bytes", 0), "stderr_sha256": record.get("stderr_sha256", sha(b"")), "cleanup": cleanup}
    need(result["returncode"] is None or w.integer(result["returncode"], -128, 255), "OUTER_RETURN")
    need(result["start_errno"] is None or w.integer(result["start_errno"], 0, 4096), "OUTER_ERRNO")
    for name in ("stdout", "stderr"):
        need(w.integer(result[name + "_bytes"], 0, 32768) and w.digest_value(result[name + "_sha256"]), "OUTER_STREAM")
    return result


def failure(result, stage, exc):
    need(stage in ("CONTEXT", "SOURCE", "OUTPUT", "HOST", "CAPSULE_SETUP", "CAPSULE_CAPTURE", "CAPSULE_PROOF", "WORKER_RESULT", "BOOKEND", "CLEANUP"), "FAILURE_STAGE")
    row = {"stage": stage, "code": stage + "_REFUSED", "errno": exc.errno if isinstance(exc, OSError) and type(exc.errno) is int and 0 <= exc.errno <= 4096 else None}
    if row not in result["failures"] and len(result["failures"]) < 8: result["failures"].append(row)
    result["status"] = "FAILED_OR_UNRECEIVED"


def main():
    result = {"schema": SCHEMA, "candidate_identity": IDENTITY, "status": "FAILED_OR_UNRECEIVED", "context": None,
              "parent_commit": PARENT_COMMIT, "parent_tree": PARENT_TREE,
              "source": {"input_pins_sha256": INPUT_PINS_SHA256, "adapter_sha256": None, "files": [], "bookends_equal": False},
              "limits": LIMITS, "host": None, "capsule": None, "outer_capture": None, "probe": None, "failures": [],
              "authority": "NONE", "original_awards": [], "native_execution": False, "model_inference": False,
              "security_policy_changed": False, "original_acceptance": False, "host_teardown_observed": False}
    stage, w, u, e, state, output, source, public = "CONTEXT", None, None, None, None, None, None, None
    try:
        context = context_from_environment(os.environ); result["context"] = context
        need(os.getuid() == os.geteuid() > 0 and os.getgid() == os.getegid() > 0, "ORDINARY_OWNER")
        workspace = Path(os.environ["GITHUB_WORKSPACE"]); temp = Path(os.environ["RUNNER_TEMP"])
        need(workspace.is_absolute() and workspace.resolve(strict=True) == workspace and temp.is_absolute() and temp.resolve(strict=True) == temp, "HOSTED_PATHS")
        source = workspace / "packet"; output = temp / ("dg17-namespace-" + context["run_id"] + "-a1")
        need(Path(__file__).absolute() == source / DIRECTORY / "diagnostic.py", "CALLER_PATH")
        stage = "SOURCE"; w = load_worker(source)
        event = w.strict(read_regular(Path(os.environ["GITHUB_EVENT_PATH"]), 1048576), 1048576)
        need(type(event) is dict and event.get("before") == PARENT_COMMIT and event.get("after") == context["workflow_commit"]
             and event.get("created") is False and event.get("deleted") is False and event.get("forced") is False
             and event.get("ref") == "refs/heads/" + BRANCH, "PUSH_BINDING")
        rows, bodies = source_snapshot(source, w)
        result["source"].update(files=rows, adapter_sha256=next(row["sha256"] for row in rows if row["path"] == DIRECTORY + "/diagnostic.py"))
        u = w.loaded(bodies[w.UTILITY_PATH], "dg17_namespace_outer_utility")
        p = w.loaded(bodies[w.PREPARER_PATH], "dg17_namespace_outer_preparer")
        e = w.loaded(bodies[w.EPISODE_PATH], "dg17_namespace_outer_capsule")
        need(p.environment() == context and sha(e.CAPSULE_SCRIPT.encode()) == CAPSULE_SCRIPT_SHA256
             and sha(e.CAPSULE_CODE.encode()) == CAPSULE_CODE_SHA256 and e.LOOPBACK_INITIALIZER_SHA == LOOPBACK_INITIALIZER_SHA256, "QUALIFIED_REUSE")
        stage = "OUTPUT"; output.mkdir(mode=0o700); public = output / "public"; public.mkdir(mode=0o700)
        private = output / "private"; private.mkdir(mode=0o700)
        context_raw = encoded(context); w.write_private(private / "CONTEXT.json", context_raw, 4096)
        w.write_private(private / "SOURCE_BEFORE.json", encoded(rows), 16384)
        stage = "HOST"
        lib = ctypes.CDLL(None, use_errno=True); need(lib.prctl(36, 1, 0, 0, 0) == 0, "SUBREAPER")
        w.quiescent(u)
        tools = {}
        for name in ("python3", "git", "bash", "env", "unshare", "setpriv", "timeout"):
            path, fact = u.trusted(name); need(path is not None, "HOST_TOOL")
            wanted = r"/usr/bin/python3(?:\.[0-9]{1,2})?" if name == "python3" else "/usr/bin/" + name
            need(re.fullmatch(wanted, path) is not None, "HOST_TOOL_CANONICAL_PROFILE")
            tools[name] = fact
        tools["mount"] = e.mount_role(); sudo = p.root_tools(u)["sudo"]
        tools["sudo"] = {"canonical": "/usr/bin/sudo", "bytes": sudo["bytes"], "sha256": sudo["sha256"],
                         "root_owned_nonwritable_chain": True, "mode": "04755",
                         "admitted_effect": "ROOT_WATCHDOG_PRIVATE_MOUNT_AND_NETWORK_NAMESPACES_FIXED_TMPFS_AND_EMPTY_READONLY_GITCONFIG_BIND_THEN_DROP_UID_GID_NO_NEW_PRIVILEGES"}
        kernel = platform.release()
        need(re.fullmatch(r"[A-Za-z0-9_.+-]{1,128}", kernel) is not None and platform.system() == "Linux", "HOST_PLATFORM")
        host = {"uid": os.getuid(), "gid": os.getgid(), "kernel": kernel, "python": list(sys.version_info[:3]),
                "boot_id_sha256": p.boot_identity(), "tools": tools,
                "system_helpers_before_sha256": None, "system_helpers_after_sha256": None, "system_helpers_unchanged": False}
        result["host"] = host; state = {"host": host, "failures": []}
        helper_before = e.content_system_helpers(u, state)
        host["system_helpers_before_sha256"] = sha(e.encoded(helper_before))
        w.write_private(private / "HELPERS_BEFORE.json", e.encoded(helper_before), 16384)
        helper = p.physical_helper()
        need(helper.get("status") == "PHYSICAL_HELPER_ADMITTED" and helper.get("bytes") == w.MEMBER_BYTES and helper.get("sha256") == w.MEMBER_SHA256, "EXACT_HELPER")
        stage = "CAPSULE_SETUP"
        capsule_host = e.capsule_host_snapshot(state, u)
        args = worker_arguments(source, output, os.getuid(), os.getgid(), capsule_host, sha(context_raw)); w.arguments(args)
        child = ["/usr/bin/python3", "-I", "-S", "-B", str(source / DIRECTORY / "worker.py"), *args]
        state["capsule_private"] = {"host_before": capsule_host, "child_argv_sha256": sha(e.encoded(child))}
        state["capsule"] = {"profile": "PRIVATE_READONLY_VIEW_AND_LOOPBACK_ONLY_V3", "status": "PREPARED_NOT_OBSERVED",
                            "qualification_scope": "CONSTRUCTED_PRIVATE_VIEW_NOT_STOCK_INSTALLATION_PATH_QUALIFICATION",
                            "targets": list(e.CAPSULE_TARGETS), "root_watchdog_seconds": 20, "root_kill_after_seconds": 5,
                            "root_script_sha256": CAPSULE_SCRIPT_SHA256, "inline_code_sha256": CAPSULE_CODE_SHA256,
                            "loopback_initializer_sha256": LOOPBACK_INITIALIZER_SHA256,
                            "outside_before_sha256": sha(e.encoded(capsule_host)), "outside_rechecks": {},
                            "outside_system_gitconfig": capsule_host["outside"]["/etc/gitconfig"], "admitted_before": False,
                            "before_after_equal": False, "admission_sha256": None, "result_sha256": None,
                            "before": None, "after": None, "child_returncode": None}
        result["capsule"] = state["capsule"]
        w.write_private(private / "CAPSULE_OWNER.json", e.encoded(state["capsule_private"]), 16384)
        argv = capsule_argv(source, output, os.getuid(), os.getgid(), capsule_host, args, e)
        # The qualified command wrapper uses the same HOME/CODEX_HOME/TMPDIR
        # assignments. Here only the three fixed environment assignments are
        # reused, without calling any native episode/controller entrypoint.
        home, temporary = output / "home", output / "tmp"; home.mkdir(mode=0o700); temporary.mkdir(mode=0o700)
        argv = ["/usr/bin/env", "HOME=" + str(home), "CODEX_HOME=" + str(home / "codex"), "TMPDIR=" + str(temporary), *argv]
        w.write_private(private / "CAPSULE_ARGV.json", e.encoded(argv), 32768)
        records, captured, capture_error = [], None, None
        stage = "CAPSULE_CAPTURE"
        try:
            rc, stdout, stderr = u.capture("namespace-prerequisite-capsule", argv, records, time.monotonic() + 35, seconds=30)
            captured = {"returncode": rc, "stdout": stdout, "stderr": stderr, "streams_complete": True}
        except BaseException as exc:
            capture_error = exc; captured = getattr(exc, "captured", None); failure(result, stage, exc)
        retained = False
        if captured is not None:
            for name in ("stdout", "stderr"):
                w.write_private(private / ("CAPSULE." + name), captured[name], 32768)
            retained = True
        w.write_private(private / "CAPTURE_RECORDS.json", e.encoded(records), 32768)
        if records:
            need(len(records) == 1, "OUTER_COMMAND_POPULATION")
            result["outer_capture"] = outer_projection(records[0], capture_error is not None, retained, w)
        for label, action in (
            ("BOOKEND", lambda: e.capsule_recheck(state, u, "after-command")),
            ("CAPSULE_PROOF", lambda: e.receive_capsule(state, output)),
        ):
            try: action()
            except BaseException as exc: failure(result, label, exc)
        stage = "WORKER_RESULT"
        worker_raw = w.read_regular(private / "WORKER_RESULT.json", 16384)
        worker = w.strict(worker_raw, 16384)
        need(w.encoded(worker) == worker_raw, "WORKER_CANONICAL_ENCODING")
        w.validate_result(worker, sha(context_raw), INPUT_PINS_SHA256, os.getuid(), os.getgid())
        result["probe"] = worker
        need(captured is not None and captured["stdout"] == worker_raw, "WORKER_CAPTURE_BINDING")
        need(worker["capsule_admission_sha256"] == result["capsule"]["admission_sha256"], "WORKER_CAPSULE_JOIN")
        stage = "BOOKEND"
        helper_after = e.content_system_helpers(u, state)
        host["system_helpers_after_sha256"] = sha(e.encoded(helper_after))
        host["system_helpers_unchanged"] = helper_before == helper_after
        w.write_private(private / "HELPERS_AFTER.json", e.encoded(helper_after), 16384)
        result["source"]["bookends_equal"] = source_snapshot(source, w)[0] == rows
        need(p.boot_identity() == host["boot_id_sha256"] and host["system_helpers_unchanged"]
             and result["source"]["bookends_equal"], "HOST_SOURCE_BOOKEND")
        stage = "CLEANUP"; w.quiescent(u)
        outer = result["outer_capture"]
        need(outer is not None and outer["process_started"] and outer["pidfd_acquired"] and outer["returncode"] == 0
             and not outer["timeout"] and not outer["output_bound_exceeded"] and not outer["internal_failure"]
             and outer["streams_complete"] and outer["private_streams_retained"] and outer["cleanup"]["echild"], "OUTER_CAPTURE_COMPLETE")
        need(not result["failures"] and worker["status"] == "OBSERVED_NAMESPACE_PREREQUISITE"
             and result["capsule"]["status"] == "OBSERVED_PRIVATE_VIEW_BEFORE_AFTER", "DIAGNOSTIC_COMPLETE")
        result["status"] = "OBSERVED_NAMESPACE_PREREQUISITE"
    except BaseException as exc: failure(result, stage, exc)
    finally:
        if u is not None and w is not None:
            try: w.quiescent(u)
            except BaseException as exc: failure(result, "CLEANUP", exc)
    raw = encoded(result); need(len(raw) <= 65536, "PUBLIC_RESULT_BOUND")
    if public is not None:
        need(w is not None, "OUTPUT_REQUIRES_WORKER")
        w.write_private(public / "RESULT.json", raw, 65536)
    print(PREFIX + raw.decode("ascii").rstrip("\n"), flush=True)
    return 0 if result["status"] == "OBSERVED_NAMESPACE_PREREQUISITE" else 1


if __name__ == "__main__":
    try: raise SystemExit(main())
    except SystemExit: raise
    except BaseException:
        sys.stderr.write("DG17_NAMESPACE_PUBLIC_OUTPUT_REFUSED\n")
        raise SystemExit(1)
