#!/usr/bin/env python3
"""Capture one prospective B02 owner episode; observations never award a case."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone

sys.dont_write_bytecode = True
SOURCE = "a297957be11feb494c0ec467235794a1e0c54751"
TREE = "b08dc4ecf4028beeedb579a312eccae23cb5d863"
OPERATION = "dg17-b02-canonical-resume-20261120-01"
BRANCH = "pro/dg17-b02-canonical-resume-20261120-01"
CONTROL_BRANCH = "pro/dg17-b02-canonical-reanchor-control-20261120-01"
PREFIX = "handoff/dg17-b02-original-20261120"
WORKFLOW = ".github/workflows/dg17-b02-original-host.yml"
CONTROL_PATH = PREFIX + "/ROOT_REANCHOR_DECISION.json"
REMOTE = "https://github.com/theislampill/IMPLEMENTAUDIT.md.git"
TARGET = "task/route-map.json"
PREIMAGE = b'{"route":"blue"}\n'
CANDIDATE = b'{"route":"green"}\n'
INPUTS = {"input/preimage.json": PREIMAGE, "input/candidate.json": CANDIDATE}
AUTH_KEYS = {"schema", "issuer", "issued_at", "root_continuity_receipt", "operation_id",
             "source_commit", "source_tree", "branch", "control_branch", "script_sha256",
             "workflow_sha256", "source_bindings_sha256", "target", "preimage_sha256",
             "candidate_sha256", "authority", "independent_source_review"}
CONTROL_KEYS = {"schema", "issuer", "issued_at", "root_continuity_receipt", "operation_id",
                "workflow_commit", "run_id", "run_attempt", "request_sha256", "controller",
                "claim_id", "initial_receipt", "invalidation", "command_sha256",
                "target", "preimage_sha256", "candidate_sha256", "decision",
                "observed_refusal", "scope_expansion"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def now():
    return datetime.now(timezone.utc).isoformat()


def new(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def new_json(path, value):
    new(path, json.dumps(value, sort_keys=True, indent=2).encode() + b"\n")


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def identity(path):
    path = Path(path)
    try:
        value = path.lstat()
    except FileNotFoundError:
        return {"kind": "absent"}
    require(stat.S_ISREG(value.st_mode) and not path.is_symlink(), "NONREGULAR_INPUT")
    raw = path.read_bytes()
    return {"kind": "regular", "bytes": len(raw), "sha256": sha(raw), "device": value.st_dev,
            "inode": value.st_ino, "mode": stat.S_IMODE(value.st_mode), "uid": value.st_uid,
            "gid": value.st_gid, "links": value.st_nlink, "mtime_ns": value.st_mtime_ns,
            "ctime_ns": value.st_ctime_ns}


def env():
    # No token, credential, inherited Git redirection or interpreter override enters owners.
    allowed = ("HOME", "LANG", "LC_ALL", "TMPDIR", "USER", "LOGNAME", "TZ")
    value = {key: os.environ[key] for key in allowed if key in os.environ}
    value.update(PATH="/usr/bin:/bin", PYTHONDONTWRITEBYTECODE="1", GIT_TERMINAL_PROMPT="0",
                 GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    return value


def reanchor_epoch_row(context, stamp, control_oid):
    return (f"| G0002 | manual-resume | {stamp} | subject HEAD {context['baseline']} "
            f"tree {context['baseline_tree']} | yes | Actual stale receipt refused before mutation; "
            f"original witness retained; Root control {control_oid} directs canonical re-anchor |\n")


def capture_command(argv, cwd, evidence, name, timeout=120, environment=None):
    """Retain the real dispatch and raw available streams, including timeout partials."""
    argv = [str(x) for x in argv]
    evidence = Path(evidence)
    selected_env = env() if environment is None else environment
    start, mono = now(), time.monotonic_ns()
    intent = {"argv": argv, "cwd": str(cwd), "started_at": start,
              "timeout_seconds": timeout, "environment_keys": sorted(selected_env),
              "environment_scope": "fixed system PATH; Git global/system config disabled; no credentials",
              "automatic_replay": False}
    new_json(evidence / "captures" / (name + ".intent.json"), intent)
    failure, result = None, None
    try:
        result = subprocess.run(argv, cwd=cwd, env=selected_env, capture_output=True,
                                check=False, timeout=timeout)
        stdout, stderr, outcome = result.stdout, result.stderr, "RETURNED"
    except subprocess.TimeoutExpired as error:
        failure = error
        stdout, stderr, outcome = error.stdout, error.stderr, "TIMEOUT"
    except OSError as error:
        failure = error
        stdout, stderr, outcome = None, None, "DISPATCH_OR_CAPTURE_ERROR"
    record = {**intent, "completed_at": now(), "elapsed_ns": time.monotonic_ns() - mono,
              "command_outcome": outcome, "returncode": result.returncode if result is not None else None,
              "effect_outcome": "UNKNOWN" if failure is not None else "NOT_INFERRED_FROM_EXIT",
              "descendant_terminal_state": "UNKNOWN", "atomic_effect_observation": False,
              "exception_type": type(failure).__name__ if failure is not None else None,
              "exception_timeout_seconds": getattr(failure, "timeout", None),
              "termination_owner": "subprocess.run timeout handling" if outcome == "TIMEOUT" else None}
    for role, raw in (("stdout", stdout), ("stderr", stderr)):
        path = evidence / "captures" / (name + "." + role)
        available = raw is not None
        if available:
            require(isinstance(raw, bytes), "NATIVE_CAPTURE_MUST_BE_BYTES")
            new(path, raw)
        record.update({role + "_available": available,
                       role + "_path": str(path.relative_to(evidence)) if available else None,
                       role + "_bytes": len(raw) if available else None,
                       role + "_sha256": sha(raw) if available else None,
                       role + "_completeness": ("COMPLETE" if outcome == "RETURNED" else "PARTIAL_OR_UNKNOWN")
                                                if available else "UNAVAILABLE"})
    new_json(evidence / "captures" / (name + ".json"), record)
    if failure is not None:
        raise failure
    return result


def retain_surviving_evidence(work):
    """Observe the owned disposable subject without helper calls or currentness gates."""
    work = Path(work).absolute()
    out = work.parent / (work.name + "-survivors")
    out.mkdir(mode=0o700)  # A prior record is never overwritten or treated as a new observation.
    (out / "bodies").mkdir()
    report = {"schema": "dg17.b02.surviving-evidence.v1", "started_at": now(),
              "work": str(work), "authority": "NONE", "original_award_delta": [],
              "requires_currentness": False, "helper_or_mutation_replay": False,
              "atomic_snapshot": False, "quiescence": "NOT_ASSERTED",
              "historical_effect_outcome": "UNKNOWN_UNLESS_SEPARATELY_RECEIVED",
              "filesystem": [], "git_observations": [], "git_objects": [], "unavailable": [],
              "retention_limits": {"filesystem_entries": 4096, "single_body_bytes": 8388608,
                                   "total_body_bytes": 16777216, "git_objects": 1024}}
    body_total, seen = 0, set()

    def unavailable(path, reason, **extra):
        report["unavailable"].append({"path": path, "reason": reason, **extra})

    def fields(value):
        return {"device": value.st_dev, "inode": value.st_ino, "mode": stat.S_IMODE(value.st_mode),
                "uid": value.st_uid, "gid": value.st_gid, "links": value.st_nlink,
                "bytes_at_stat": value.st_size, "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns}

    safe_work = work.resolve() == work
    if not safe_work:
        unavailable(".", "WORK_ANCESTRY_SYMLINK_NOT_FOLLOWED")

    def capture_path(relative, descend=True):
        nonlocal body_total
        key = Path(relative).as_posix()
        if key in seen:
            return
        seen.add(key)
        row = {"path": key, "observed_at": now(), "historical_effect": "UNKNOWN"}
        report["filesystem"].append(row)
        if len(report["filesystem"]) > 4096:
            row.update(kind="unavailable", body_status="UNAVAILABLE_ENTRY_LIMIT")
            unavailable(key, row["body_status"])
            return
        if not safe_work:
            row.update(kind="unavailable", body_status="UNAVAILABLE_WORK_ANCESTRY")
            return
        path = work / relative
        # Never follow an unexpected intermediate symlink to a different custody domain.
        cursor = path.parent
        while cursor != work.parent:
            try:
                if stat.S_ISLNK(cursor.lstat().st_mode):
                    row.update(kind="unavailable", body_status="UNAVAILABLE_SYMLINK_ANCESTOR")
                    unavailable(key, row["body_status"])
                    return
            except FileNotFoundError:
                pass
            except OSError as error:
                row.update(kind="unavailable", body_status="UNAVAILABLE_ANCESTRY", errno=error.errno)
                unavailable(key, row["body_status"], errno=error.errno)
                return
            cursor = cursor.parent
        try:
            before = path.lstat()
        except FileNotFoundError:
            row.update(kind="absent_at_observation", body_status="UNAVAILABLE_ABSENT")
            unavailable(key, "ABSENT_AT_OBSERVATION_NOT_PROOF_OF_NO_PRIOR_EFFECT")
            return
        except OSError as error:
            row.update(kind="unavailable", body_status="UNAVAILABLE_LSTAT", errno=error.errno)
            unavailable(key, row["body_status"], errno=error.errno)
            return
        row.update(fields(before))
        if stat.S_ISLNK(before.st_mode):
            row.update(kind="symlink", body_status="UNAVAILABLE_SYMLINK_NOT_FOLLOWED")
            unavailable(key, row["body_status"])
            return
        if stat.S_ISDIR(before.st_mode):
            row.update(kind="directory", body_status="DIRECTORY_METADATA_ONLY")
            if key == "subject/.git":
                row["body_status"] = "GIT_OBJECTS_AND_REFS_CAPTURED_SEPARATELY"
                return
            if descend:
                try:
                    children = sorted(path.iterdir(), key=lambda p: os.fsencode(p.name))
                    row["observed_child_count"] = len(children)
                    for child in children:
                        if len(report["filesystem"]) >= 4096:
                            unavailable(key, "DIRECTORY_REMAINDER_UNAVAILABLE_ENTRY_LIMIT")
                            break
                        capture_path(Path(relative) / child.name)
                except OSError as error:
                    unavailable(key, "DIRECTORY_ENUMERATION_UNAVAILABLE", errno=error.errno)
            return
        if not stat.S_ISREG(before.st_mode):
            row.update(kind="other", body_status="UNAVAILABLE_SPECIAL_FILE_NOT_OPENED")
            unavailable(key, row["body_status"])
            return
        row["kind"] = "regular"
        limit = min(8388608, 16777216 - body_total)
        if before.st_size > limit:
            row["body_status"] = "UNAVAILABLE_BODY_LIMIT"
            unavailable(key, row["body_status"])
            return
        fd = None
        try:
            fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
            opened = os.fstat(fd)
            require(stat.S_ISREG(opened.st_mode), "SURVIVOR_OPEN_CHANGED_KIND")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                raw = stream.read(limit + 1)
            after = os.fstat(fd)
            current = path.lstat()
            if len(raw) > limit:
                row["body_status"] = "UNAVAILABLE_BODY_GREW_BEYOND_LIMIT"
                unavailable(key, row["body_status"])
                return
            body_path = "bodies/" + f"{len(report['filesystem']):06d}.bin"
            new(out / body_path, raw)
            body_total += len(raw)
            stable = fields(before) == fields(opened) == fields(after) == fields(current)
            row.update(body_path=body_path, captured_bytes=len(raw), captured_sha256=sha(raw),
                       body_status="CAPTURED_STABLE_FILE" if stable else "CAPTURED_WITH_OBSERVED_DRIFT",
                       after=fields(current), complete_body_at_observation=stable and len(raw) == current.st_size)
            if not stable:
                unavailable(key, "STABLE_FILE_IDENTITY_NOT_ESTABLISHED")
        except (OSError, RuntimeError) as error:
            row.update(body_status="UNAVAILABLE_READ", exception_type=type(error).__name__, errno=getattr(error, "errno", None))
            unavailable(key, row["body_status"], exception_type=type(error).__name__, errno=getattr(error, "errno", None))
        finally:
            if fd is not None:
                os.close(fd)

    # No context.json, receipt or valid task record is needed to preserve partial setup/effects.
    capture_path("context.json")
    capture_path("subject")
    for path in ["subject/" + TARGET, *("subject/" + name for name in INPUTS),
                 "subject/.IMPLEMENTAUDIT", "subject/.IMPLEMENTAUDIT/runs"]:
        capture_path(path)

    subject, gitdir = work / "subject", work / "subject/.git"
    git_safe = safe_work
    for path in (subject, gitdir):
        try:
            git_safe = git_safe and stat.S_ISDIR(path.lstat().st_mode) and not path.is_symlink()
        except OSError:
            git_safe = False
    read_env = {**env(), "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"}

    def git_capture(name, arguments):
        argv = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false", *arguments]
        try:
            result = capture_command(argv, subject, out, name, timeout=10, environment=read_env)
            row = {"name": name, "argv": argv, "returncode": result.returncode,
                   "stdout_path": "captures/" + name + ".stdout", "stderr_path": "captures/" + name + ".stderr"}
            report["git_observations"].append(row)
            if result.returncode != 0:
                unavailable("subject/.git", "GIT_READ_REFUSED", observation=name, returncode=result.returncode)
                return None
            return result.stdout
        except (OSError, subprocess.TimeoutExpired) as error:
            report["git_observations"].append({"name": name, "argv": argv, "returncode": None,
                                               "outcome": "UNAVAILABLE", "exception_type": type(error).__name__})
            unavailable("subject/.git", "GIT_READ_UNAVAILABLE", observation=name)
            return None

    if git_safe:
        for name, arguments in [
            ("git-head", ["rev-parse", "HEAD"]), ("git-tree", ["rev-parse", "HEAD^{tree}"]),
            ("git-refs", ["for-each-ref", "--format=%(refname) %(objectname)"]),
            ("git-status", ["status", "--porcelain=v1", "--untracked-files=all"]),
            ("git-tracked", ["ls-files", "--stage"])]:
            git_capture(name, arguments)
        population = git_capture("git-object-population", ["cat-file", "--batch-all-objects",
                                                          "--batch-check=%(objectname) %(objecttype) %(objectsize)"])
        if population is not None:
            lines = population.decode("ascii", "replace").splitlines()
            report["observed_git_object_count"] = len(lines)
            for ordinal, line in enumerate(lines):
                if ordinal >= 1024:
                    unavailable("subject/.git/objects", "OBJECT_REMAINDER_UNAVAILABLE_COUNT_LIMIT")
                    break
                match = re.fullmatch(r"([0-9a-f]{40}) (blob|tree|commit|tag) ([0-9]+)", line)
                if not match:
                    unavailable("subject/.git/objects", "UNPARSEABLE_OBJECT_CENSUS_ROW", ordinal=ordinal)
                    continue
                oid, kind, length = match.group(1), match.group(2), int(match.group(3))
                row = {"oid": oid, "type": kind, "declared_bytes": length}
                report["git_objects"].append(row)
                if length > 8388608 or body_total + length > 16777216:
                    row["status"] = "UNAVAILABLE_BODY_LIMIT"; unavailable(oid, row["status"])
                    continue
                name = f"git-object-{ordinal:04d}"
                body = git_capture(name, ["cat-file", kind, oid])
                if body is None:
                    row["status"] = "UNAVAILABLE_GIT_READ"
                    continue
                row.update(body_path="captures/" + name + ".stdout", captured_bytes=len(body), captured_sha256=sha(body))
                actual_oid = hashlib.sha1(kind.encode() + b" " + str(len(body)).encode() + b"\0" + body).hexdigest()
                row["status"] = "CAPTURED_EXACT_OBJECT" if actual_oid == oid and len(body) == length else "OBJECT_IDENTITY_MISMATCH"
                body_total += len(body)
                if row["status"] != "CAPTURED_EXACT_OBJECT":
                    unavailable(oid, row["status"])
    else:
        unavailable("subject/.git", "GIT_CUSTODY_MISSING_OR_UNSAFE_NOT_FOLLOWED")
    report.update(completed_at=now(), retained_body_bytes=body_total,
                  disposition="OBSERVATIONS_ONLY_WITH_EXPLICIT_UNAVAILABLE_OUTCOMES",
                  success_or_no_effect_inference=False)
    new_json(out / "RETENTION.json", report)
    rows = []
    for path in sorted(out.rglob("*")):
        if path.is_file():
            body = path.read_bytes(); rows.append({"path": path.relative_to(out).as_posix(), "bytes": len(body), "sha256": sha(body)})
    new_json(out / "MANIFEST.json", {"schema": "dg17.b02.survivor-retention-manifest.v1", "authority": "NONE", "files": rows})
    return out


class Episode:
    def __init__(self, source, work, action):
        self.source, self.work, self.action = Path(source).resolve(), Path(work).absolute(), action
        self.evidence = self.work / "evidence"
        self.subject = self.work / "subject"
        self.counter = 0
        if action == "prepare":
            require(not self.work.exists(), "WORK_DIRECTORY_ALREADY_EXISTS_NO_REPLAY")
            self.work.mkdir(mode=0o700)
            self.evidence.mkdir()
            (self.evidence / "host-actions").mkdir()
        else:
            self.config = read_json(self.work / "context.json")
            self.run = self.subject / self.config["run_root"]
        new_json(self.evidence / "operation-claims" / (action + ".json"),
                 {"action": action, "at": now(), "pid": os.getpid(), "operation": OPERATION})

    def command(self, argv, expected=(0,), cwd=None, label=None):
        self.counter += 1
        name = f"{self.action}-{self.counter:02d}" + ("-" + label if label else "")
        result = capture_command(argv, cwd or self.subject, self.evidence, name)
        require(result.returncode in expected, f"COMMAND_REFUSED:{name}:{result.returncode}")
        return result

    def helper(self, *args, expected=(0,)):
        return self.command(["/usr/bin/bash", self.source / "skills/implementaudit/scripts/claim-run.sh", *args], expected)

    def token(self, label):
        return (self.evidence / (label + ".txt")).read_text().strip()

    def subject_identity(self, expected=None):
        head = self.command(["/usr/bin/git", "rev-parse", "HEAD"]).stdout.decode().strip()
        tree = self.command(["/usr/bin/git", "rev-parse", "HEAD^{tree}"]).stdout.decode().strip()
        require(re.fullmatch("[0-9a-f]{40}", head) and re.fullmatch("[0-9a-f]{40}", tree),
                "SUBJECT_GIT_IDENTITY_UNAVAILABLE")
        actual = {"head": head, "tree": tree}
        if expected is not None:
            require(actual == expected, "SUBJECT_HEAD_OR_TREE_DRIFT")
        return actual

    def source_receive(self):
        raw = (self.source / PREFIX / "SOURCE_BINDINGS.json").read_bytes()
        bindings = read_json(self.source / PREFIX / "SOURCE_BINDINGS.json")
        require(bindings["source_commit"] == SOURCE and bindings["source_tree"] == TREE, "SOURCE_BINDING_IDENTITY")
        for item in bindings["files"]:
            body = (self.source / item["path"]).read_bytes()
            require(len(body) == item["bytes"] and sha(body) == item["sha256"], "SOURCE_FILE_DRIFT:" + item["path"])
            exact = self.command(["/usr/bin/git", "rev-parse", SOURCE + ":" + item["path"]], cwd=self.source)
            blob = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
            require(exact.stdout.decode().strip() == item["git_blob"] == blob, "SOURCE_GIT_PREIMAGE_DRIFT:" + item["path"])
        head = self.command(["/usr/bin/git", "rev-parse", "HEAD"], cwd=self.source).stdout.decode().strip()
        require(head == os.environ["GITHUB_SHA"], "WORKFLOW_HEAD_MISMATCH")
        tree = self.command(["/usr/bin/git", "rev-parse", SOURCE + "^{tree}"], cwd=self.source).stdout.decode().strip()
        require(tree == TREE, "SOURCE_TREE_MISMATCH")
        diff = self.command(["/usr/bin/git", "diff", "--name-status", SOURCE, "HEAD"], cwd=self.source).stdout.decode().splitlines()
        expected = sorted("A\t" + p for p in [WORKFLOW, PREFIX + "/operate.py", PREFIX + "/SOURCE_BINDINGS.json", PREFIX + "/ROOT_AUTHORIZATION.json"])
        require(sorted(diff) == expected, "UNDECLARED_PRODUCT_OR_PACKET_CHANGE")
        require(not self.command(["/usr/bin/git", "status", "--porcelain"], cwd=self.source).stdout, "SOURCE_WORKTREE_DIRTY")
        retained = self.evidence / "SOURCE_BINDINGS.json"
        if retained.exists():
            require(retained.read_bytes() == raw, "RETAINED_SOURCE_BINDINGS_DRIFT")
        else:
            new(retained, raw)
        return head

    def prepare(self):
        require(os.environ.get("GITHUB_REPOSITORY") == "theislampill/IMPLEMENTAUDIT.md", "REPOSITORY_MISMATCH")
        require(os.environ.get("GITHUB_REF") == "refs/heads/" + BRANCH, "BRANCH_MISMATCH")
        require(os.environ.get("GITHUB_RUN_ATTEMPT") == "1", "RERUN_ATTEMPT_NOT_AUTHORIZED")
        auth_path = self.source / PREFIX / "ROOT_AUTHORIZATION.json"
        auth = read_json(auth_path)
        require(set(auth) == AUTH_KEYS, "AUTHORIZATION_SCHEMA")
        exact = {"schema": "dg17.b02.root-operation-authorization.v1", "issuer": "/root",
                 "operation_id": OPERATION, "source_commit": SOURCE, "source_tree": TREE,
                 "branch": BRANCH, "control_branch": CONTROL_BRANCH, "target": TARGET,
                 "preimage_sha256": sha(PREIMAGE), "candidate_sha256": sha(CANDIDATE),
                 "authority": "ORDINARY_DISPOSABLE_TASK_AND_EXACT_SOURCE_QUALIFICATION"}
        require(all(auth.get(k) == v for k, v in exact.items()), "AUTHORIZATION_BINDING")
        for key, path in [("script_sha256", PREFIX + "/operate.py"), ("workflow_sha256", WORKFLOW),
                          ("source_bindings_sha256", PREFIX + "/SOURCE_BINDINGS.json")]:
            require(auth[key] == sha((self.source / path).read_bytes()), "AUTHORIZATION_SOURCE_PIN:" + key)
        require(auth["root_continuity_receipt"].startswith("refs/implementaudit/continuity-receipts/") and
                isinstance(auth["independent_source_review"], dict) and
                re.fullmatch("[0-9a-f]{64}", auth["independent_source_review"].get("manifest_sha256", "")),
                "GENUINE_ROOT_AND_REVIEW_RECEIPTS_REQUIRED")
        require("UNISSUED" not in json.dumps(auth) and auth["issued_at"], "ROOT_AUTHORIZATION_UNISSUED")
        new(self.evidence / "ROOT_AUTHORIZATION.json", auth_path.read_bytes())
        self.subject.mkdir()
        head = self.source_receive()
        public_env = {key: os.environ.get(key) for key in (
            "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT",
            "RUNNER_OS", "RUNNER_ARCH", "RUNNER_ENVIRONMENT", "ImageOS", "ImageVersion")}
        exe = Path("/usr/bin/python3").resolve()
        chain = []
        for p in [exe, *exe.parents]:
            s = p.stat(); chain.append({"path": str(p), "uid": s.st_uid, "mode": stat.S_IMODE(s.st_mode)})
        new_json(self.evidence / "HOST_FACTS.json", {"observed_at": now(), "public_environment": public_env,
            "python": sys.version, "executable": str(exe), "executable_sha256": sha(exe.read_bytes()),
            "interpreter_ancestry": chain, "uid": os.getuid(), "gid": os.getgid(),
            "uname": list(os.uname()), "os_release": Path("/etc/os-release").read_text()})
        require(all(row["uid"] == 0 and row["mode"] & 0o022 == 0 for row in chain), "ORIGINAL_INTERPRETER_OWNERSHIP_NOT_SATISFIED")
        for path, body in {TARGET: PREIMAGE, **INPUTS, ".gitignore": b".IMPLEMENTAUDIT/\n"}.items():
            new(self.subject / path, body)
        self.command(["/usr/bin/git", "init", "--initial-branch=task"])
        self.command(["/usr/bin/git", "config", "user.name", "DG17 disposable task initializer"])
        self.command(["/usr/bin/git", "config", "user.email", "dg17-task@example.invalid"])
        self.command(["/usr/bin/git", "add", ".gitignore", TARGET, *INPUTS])
        self.command(["/usr/bin/git", "commit", "-m", "Initialize new authorized B02 subject; no original product change"])
        subject_baseline = self.subject_identity()
        baseline = subject_baseline["head"]
        new_json(self.evidence / "SUBJECT_BASELINE.json", subject_baseline)
        controller = "b02-resume-" + os.environ["GITHUB_RUN_ID"] + "-a1"
        claimed = self.helper("--controller", controller, "b02-canonical-resume").stdout.decode().strip()
        require(re.fullmatch(r"\.IMPLEMENTAUDIT/runs/b02-canonical-resume-[A-Za-z0-9]{6}", claimed), "CLAIM_PATH")
        self.run = self.subject / claimed
        claim = dict(row.split("=", 1) for row in (self.run / ".claimed").read_text().splitlines())
        author_file = self.source / "fixtures/controller-initialization/author_checkpoint.py"
        spec = importlib.util.spec_from_file_location("original_checkpoint_author", author_file)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        purpose = "Continue the authorized route-map replacement through verified task custody"
        for name in module.NAMES:
            module.author(self.subject, claimed, self.source, purpose,
                          "apply the exact authorized route-map candidate after currentness verifies", only=name)
        phase = PHASE
        for key, value in {"run": claimed, "baseline": baseline, "source": self.source,
                           "subject": self.subject, "work": self.work, "evidence": self.evidence,
                           "controller": controller}.items():
            phase = phase.replace("{" + key + "}", str(value))
        new(self.run / "phases/phase-1.md", phase.encode())
        inspected = self.helper("--inspect-controller-initialization", controller, "--run-root", claimed)
        token = json.loads(inspected.stdout)["initialization_token"]
        self.helper("--activate-controller", controller, "--run-root", claimed, "--expected-initialization", token)
        self.config = {"schema": "dg17.b02.actual-episode-context.v1", "operation": OPERATION,
                       "controller": controller, "claim_id": claim["claim_id"], "run_root": claimed,
                       "workflow_commit": head, "baseline": baseline, "baseline_tree": subject_baseline["tree"],
                       "run_id": int(os.environ["GITHUB_RUN_ID"]), "run_attempt": 1,
                       "authorization_sha256": sha(auth_path.read_bytes())}
        new_json(self.work / "context.json", self.config)
        new_json(self.evidence / "ACTUAL_CONTEXT.json", self.config)
        self.snapshot("initial")

    def snapshot(self, name):
        result = {p: identity(self.subject / p) for p in [TARGET, *INPUTS, ".gitignore"]}
        result["transaction_exists"] = (self.run / "mutation-transactions" /
                                         (self.config["claim_id"] + "-p1-s1")).exists()
        new_json(self.evidence / (name + "-identities.json"), result)
        return result

    def mutation_command(self):
        return ["/usr/bin/bash", str(self.source / "skills/implementaudit/scripts/apply-observed-mutation.sh"),
                "--repo-root", str(self.subject), "--run-root", str(self.run), "--phase", "1", "--step", "1",
                "--preimage", str(self.subject / "input/preimage.json"),
                "--candidate", str(self.subject / "input/candidate.json")]

    def save_objects(self, prefix):
        refs = self.command(["/usr/bin/git", "for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/"])
        objects = []
        for line in refs.stdout.decode().splitlines():
            ref, oid = line.split(" ")
            result = self.command(["/usr/bin/git", "cat-file", "blob", oid])
            objects.append({"ref": ref, "oid": oid, "body_sha256": sha(result.stdout), "body_bytes": len(result.stdout)})
        new_json(self.evidence / (prefix + "-git-objects.json"), objects)

    def stale(self):
        before = self.snapshot("before-stale")
        require(not before["transaction_exists"], "PREEXISTING_TRANSACTION")
        command = self.mutation_command()
        result = self.command(command, expected=(77,), label="actual-mutation-refusal")
        observation = json.loads(result.stdout)
        require(observation["status"] == "UNSUPPORTED_OWNER_DECISION" and
                observation["reason_code"] == "STALE_CONTINUITY_RECEIPT" and
                observation["actual_effect_set"] == [], "STALE_REFUSAL_NOT_ESTABLISHED")
        after = self.snapshot("after-stale")
        require(before == after, "STALE_ATTEMPT_CHANGED_SUBJECT")
        new_json(self.evidence / "ACTUAL_STALE_RESULT.json", observation)
        self.save_objects("stale")
        for role in ("STATE.md", "ROADMAP.md"):
            new(self.evidence / "before-reanchor" / role, (self.run / role).read_bytes())
        request = {"schema": "dg17.b02.actual-stale-request.v1", "operation_id": OPERATION,
                   **{k: self.config[k] for k in ("workflow_commit", "run_id", "run_attempt", "controller", "claim_id")},
                   "initial_receipt": self.token("initial-receipt"), "invalidation": self.token("resume-invalidation"),
                   "subject_identity": self.subject_identity({"head": self.config["baseline"], "tree": self.config["baseline_tree"]}),
                   "command": command, "command_sha256": sha(canonical(command)),
                   "target": TARGET, "preimage_sha256": sha(PREIMAGE), "candidate_sha256": sha(CANDIDATE),
                   "actual_refusal": {"returncode": result.returncode, "status": observation["status"],
                                      "reason_code": observation["reason_code"], "stdout_sha256": sha(result.stdout),
                                      "stderr_sha256": sha(result.stderr)},
                   "unchanged_subject_identities": after, "observed_at": now(),
                   "decision_deadline_unix": int(time.time()) + 1200,
                   "root_decision": "UNISSUED", "original_award": False}
        new_json(self.evidence / "STALE_REQUEST.json", request)

    def wait_control(self):
        request_path = self.evidence / "STALE_REQUEST.json"
        request = read_json(request_path)
        carrier = self.work / "control-objects"
        carrier.mkdir()
        self.command(["/usr/bin/git", "init", "--bare", str(carrier)], cwd=self.work)
        prefix = ["/usr/bin/git", "--git-dir=" + str(carrier), "-c", "protocol.file.allow=never", "-c", "protocol.ext.allow=never"]
        while time.time() <= request["decision_deadline_unix"]:
            poll = self.command(prefix + ["ls-remote", "--exit-code", "--heads", REMOTE, "refs/heads/" + CONTROL_BRANCH], expected=(0, 2), cwd=self.work)
            if poll.returncode == 2:
                require(poll.stdout == b"", "ABSENT_BRANCH_HAS_UNEXPECTED_OUTPUT")
                time.sleep(15)
                continue
            lines = poll.stdout.decode().splitlines()
            require(len(lines) == 1, "CONTROL_BRANCH_AMBIGUOUS")
            oid, ref = lines[0].split("\t")
            require(re.fullmatch("[0-9a-f]{40}", oid) and ref == "refs/heads/" + CONTROL_BRANCH, "CONTROL_REF_IDENTITY")
            self.command(prefix + ["fetch", "--no-tags", "--depth=2", "--no-write-fetch-head", REMOTE, oid], cwd=self.work)
            commit = self.command(prefix + ["cat-file", "commit", oid], cwd=self.work).stdout
            parents = re.findall(rb"(?m)^parent ([0-9a-f]{40})$", commit)
            require(parents == [self.config["workflow_commit"].encode()], "CONTROL_PARENT")
            changed = self.command(prefix + ["diff-tree", "--no-commit-id", "--name-status", "-r", self.config["workflow_commit"], oid], cwd=self.work).stdout
            require(changed == ("A\t" + CONTROL_PATH + "\n").encode(), "CONTROL_CHANGE_SCOPE")
            raw = self.command(prefix + ["show", oid + ":" + CONTROL_PATH], cwd=self.work).stdout
            new(self.evidence / "ACTUAL_ROOT_REANCHOR_DECISION.json", raw)
            decision = read_json(self.evidence / "ACTUAL_ROOT_REANCHOR_DECISION.json")
            require(set(decision) == CONTROL_KEYS, "CONTROL_SCHEMA")
            exact = {"schema": "dg17.b02.root-reanchor-decision.v1", "issuer": "/root",
                     "operation_id": OPERATION, "request_sha256": sha(request_path.read_bytes()),
                     "decision": "CONTAIN_AND_REANCHOR_THEN_REVALIDATE_PENDING_EFFECT", "scope_expansion": False,
                     "observed_refusal": request["actual_refusal"]}
            for k in ("workflow_commit", "run_id", "run_attempt", "controller", "claim_id", "initial_receipt",
                      "invalidation", "command_sha256", "target", "preimage_sha256", "candidate_sha256"):
                exact[k] = request[k]
            require(all(decision.get(k) == v for k, v in exact.items()), "CONTROL_REQUEST_BINDING")
            require(decision["issued_at"] and decision["root_continuity_receipt"].startswith("refs/implementaudit/continuity-receipts/") and
                    "UNISSUED" not in json.dumps(decision), "ACTUAL_ROOT_DECISION_REQUIRED")
            closing = self.command(prefix + ["ls-remote", "--exit-code", "--heads", REMOTE, "refs/heads/" + CONTROL_BRANCH], cwd=self.work)
            require(closing.stdout == poll.stdout and time.time() <= request["decision_deadline_unix"], "CONTROL_MOVED_OR_EXPIRED")
            new_json(self.evidence / "CONTROL_CONSUMPTION.json", {"oid": oid, "parent": self.config["workflow_commit"],
                     "path": CONTROL_PATH, "decision_sha256": sha(raw), "request_sha256": sha(request_path.read_bytes()),
                     "consumed_at": now(), "issuer_proof_boundary": "Root actual provider receipts required at independent receiving"})
            return
        raise RuntimeError("ROOT_DECISION_NOT_RECEIVED_WITHIN_HOLD")

    def reanchor(self):
        decision = read_json(self.evidence / "ACTUAL_ROOT_REANCHOR_DECISION.json")
        consumed = read_json(self.evidence / "CONTROL_CONSUMPTION.json")
        require(consumed["decision_sha256"] == sha((self.evidence / "ACTUAL_ROOT_REANCHOR_DECISION.json").read_bytes()), "ROOT_DECISION_DRIFT")
        require(self.snapshot("before-reanchor-authoring") == read_json(self.evidence / "after-stale-identities.json"), "PENDING_EFFECT_ALREADY_CHANGED")
        self.subject_identity({"head": self.config["baseline"], "tree": self.config["baseline_tree"]})
        state_path, roadmap_path = self.run / "STATE.md", self.run / "ROADMAP.md"
        state = state_path.read_text()
        require("Current epoch: G0001" in state, "INITIAL_EPOCH_DRIFT")
        state = state.replace("Current epoch: G0001", "Current epoch: G0002", 1)
        stamp = now()
        state += "\n## Actual manual-resume mismatch and Root route\n\n| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|\n"
        state += reanchor_epoch_row(self.config, stamp, consumed['oid']) + "\n"
        state += f"Andon: actual currentness mismatch during the pending phase resume. Status: contained pending verified G0002. Class: evidence-mismatch. Failing check: unchanged mutation consumer returned exit77 / STALE_CONTINUITY_RECEIPT. Witness: actual refusal stdout and stale request hash {consumed['request_sha256']}. Target and both inputs stayed unchanged; transaction was absent. Owner: this Root-authorized task and its unchanged canonical continuity/mutation owners. Decision: {decision['decision']}; next concrete action: verify the actual canonical G0002 receipt, then revalidate the same still-unperformed phase-authorized effect. No case acceptance follows.\n"
        state_path.write_text(state)
        roadmap_path.write_text(roadmap_path.read_text() + f"\nActual Root control {consumed['oid']} directs re-anchor after the preserved currentness refusal. The phase remains open and the target effect remains unperformed. Resume and verify G0002, then submit the identical authorized command; stop on any mismatch.\n")
        for role in ("STATE.md", "ROADMAP.md"):
            new(self.evidence / "reanchored" / role, (self.run / role).read_bytes())

    def apply_current(self):
        request = read_json(self.evidence / "STALE_REQUEST.json")
        require(sha(canonical(self.mutation_command())) == request["command_sha256"], "PENDING_COMMAND_DRIFT")
        require(self.snapshot("before-current-apply") == request["unchanged_subject_identities"], "PENDING_SUBJECT_DRIFT")
        result = self.command(self.mutation_command(), label="actual-current-mutation")
        observed = json.loads(result.stdout)
        require(observed["status"] == "COMMITTED" and (self.subject / TARGET).read_bytes() == CANDIDATE, "CURRENT_MUTATION_NOT_COMMITTED")
        after = self.snapshot("after-current-apply")
        for path in [*INPUTS, ".gitignore"]:
            require(after[path] == request["unchanged_subject_identities"][path], "UNRELATED_INPUT_CHANGED:" + path)
        new_json(self.evidence / "ACTUAL_CURRENT_MUTATION_RESULT.json", observed)

    def final(self):
        self.subject_identity({"head": self.config["baseline"], "tree": self.config["baseline_tree"]})
        changed = self.command(["/usr/bin/git", "diff", "--name-only"]).stdout.decode().splitlines()
        require(changed == [TARGET], "FINAL_TRACKED_SCOPE")
        require(not self.command(["/usr/bin/git", "ls-files", "--others", "--exclude-standard"]).stdout, "UNEXPECTED_SUBJECT_FILE")
        self.helper("--require-current-continuity", self.config["controller"])
        self.source_receive()
        self.save_objects("final")
        shutil.copytree(self.run, self.evidence / "actual-run-root")
        new_json(self.evidence / "OBSERVATION.json", {"schema": "dg17.b02.actual-observation.v1", **self.config,
            "completed_at": now(), "stale_refusal": "actual unchanged source refused before effect",
            "root_route": read_json(self.evidence / "CONTROL_CONSUMPTION.json"),
            "current_receipt": self.token("current-receipt"), "current_effect": "actual original consumer COMMITTED",
            "source_commit": SOURCE, "source_tree": TREE, "model_cognition_subject": False,
            "case_acceptance": "PENDING_INDEPENDENT_ORIGINAL_RECEIVING", "original_award": False,
            "native_stop_or_host_activation_claim": False})
        rows = []
        for path in sorted(self.evidence.rglob("*")):
            if path.is_file():
                raw = path.read_bytes(); rows.append({"path": str(path.relative_to(self.evidence)), "bytes": len(raw), "sha256": sha(raw)})
        new_json(self.evidence / "MANIFEST.json", {"schema": "dg17.b02.evidence-manifest.v1", "files": rows})

    def execute(self):
        action = self.action
        if action == "prepare": return self.prepare()
        controller = self.config["controller"]
        if action in ("current-initial", "current-resume"):
            return self.helper("--current-controller", controller)
        if action in ("invalidate-initial", "invalidate-resume"):
            initial = action.endswith("initial")
            result = self.helper("--invalidate-continuity", controller, "--boundary", "new-session" if initial else "manual-resume",
                                 "--event", "b02-" + str(self.config["run_id"]) + ("-initial" if initial else "-resume-01"))
            return new(self.evidence / ("initial-invalidation.txt" if initial else "resume-invalidation.txt"), result.stdout)
        if action in ("read-initial-state", "read-initial-roadmap", "read-resume-state", "read-resume-roadmap"):
            role = "STATE.md" if action.endswith("state") else "ROADMAP.md"
            return self.command(["/usr/bin/cat", self.run / role])
        if action in ("resume-initial", "resume-current"):
            initial = action.endswith("initial")
            result = self.helper("--resume-controller", controller, "--boundary", "new-session" if initial else "manual-resume",
                                 "--epoch", "G0001" if initial else "G0002")
            receipt = result.stdout.decode().strip()
            require(re.fullmatch(r"refs/implementaudit/continuity-receipts/" + re.escape(controller) + r"/" +
                                 ("G0001" if initial else "G0002") + r"@[0-9a-f]{40}", receipt), "RECEIPT_IDENTITY")
            return new(self.evidence / ("initial-receipt.txt" if initial else "current-receipt.txt"), result.stdout)
        if action in ("verify-initial", "verify-current"):
            return self.helper("--verify-resume-receipt", self.token("initial-receipt" if action.endswith("initial") else "current-receipt"))
        if action in ("require-initial", "require-current"):
            return self.helper("--require-current-continuity", controller)
        return {"stale-attempt": self.stale, "wait-root-control": self.wait_control, "author-reanchor": self.reanchor,
                "apply-current": self.apply_current, "final-receive": self.final}[action]()


PHASE = '''IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 1 — Apply the authorized route-map replacement
Task: Replace the exact task route-map preimage with the authorized candidate only under current continuity
Type: brownfield
Run root: {run}
Baseline ref: {baseline}
Owner/source: task/route-map.json
Mandatory commands: canonical continuity verification; exact original mutation consumer; exact post-state receiving
Acceptance criteria: 3
Evidence required: complete actual command captures and target/input identities
Depends on phases: none

## Why

The owner authorized one exact route-map replacement. A pending task must not mutate through a stale continuity receipt.

## Current state excerpts

- The target task/route-map.json contains the exact bytes retained in input/preimage.json at the seed commit.
- input/candidate.json contains the sole authorized replacement; unrelated inputs are preserved.

## Work

Submit the existing canonical mutation consumer for this exact target and phase authority. If its currentness gate refuses, preserve the actual mismatch and wait for the real Root recovery decision before re-anchoring.

## Implementation steps (ordered)

- Step 1: Replace the authorized route map — target: task/route-map.json; change: replace the exact input/preimage.json bytes with input/candidate.json; verify: invoke the unchanged apply-observed-mutation.sh owner and compare the complete post-state; expected: COMMITTED only with current canonical continuity and the same exact phase authority
  mutation-authority: {"operation":"replace","source":"task/route-map.json","destination":null}

## Scope boundaries

In scope: task/route-map.json
Mutation scope: {"in":["task/route-map.json"],"out":["input/candidate.json","input/preimage.json"]}
Out of scope: the two input files, original product sources, external effects, protected generations and unrelated task files.

## STOP conditions (plan-specific)

- Stop if the canonical continuity receipt is stale or its controller/claim no longer identifies this exact pending task; retain the actual refusal and recover through the original owner.
- Stop if target bytes differ from input/preimage.json before the first effect, or if applying the candidate requires an unlisted target.

## Acceptance criteria

- [ ] The source mutation owner refuses the actual stale request before target or transaction effects.
- [ ] The actual Root decision and canonical G0002 receipt re-anchor this same task before the still-unperformed replacement is submitted.
- [ ] The original consumer commits the exact candidate and retains both input physical identities.

## Mandatory commands

- /usr/bin/python3 -B "{source}/handoff/dg17-b02-original-20261120/operate.py" require-current --source "{source}" --work "{work}" > "{evidence}/host-actions/require-current.log" 2>&1 — property: behavioral; scope: the exact claimed controller through its unchanged canonical owner; coverage: full; capture: {evidence}/host-actions/require-current.log; acceptance: non-textual; expected: driver exit 0 only after the native owner returns the exact actual canonical receipt token following verified re-anchor.
- /usr/bin/python3 -B "{source}/handoff/dg17-b02-original-20261120/operate.py" stale-attempt --source "{source}" --work "{work}" > "{evidence}/host-actions/stale-attempt.log" 2>&1 — property: behavioral; scope: the authorized replacement while currentness is stale; coverage: full; capture: {evidence}/host-actions/stale-attempt.log; acceptance: non-textual; expected: driver exit 0 only after native exit 77 with typed STALE_CONTINUITY_RECEIPT and actually unchanged target/input identities.
- /usr/bin/python3 -B "{source}/handoff/dg17-b02-original-20261120/operate.py" apply-current --source "{source}" --work "{work}" > "{evidence}/host-actions/apply-current.log" 2>&1 — property: behavioral; scope: the identical pending replacement after actual re-anchor; coverage: full; capture: {evidence}/host-actions/apply-current.log; acceptance: non-textual; expected: driver exit 0 only after native exit 0 with typed COMMITTED and exact post-state verification.

The mandatory command rows name actual workflow driver commands and their combined outer stdout/stderr files. Each driver additionally retains the exact native argv and both native raw streams separately under captures/, with exit, timing and identity metadata. These native captures remain required original receiving evidence. A timeout is explicitly partial/UNKNOWN rather than satisfying the planned full-capture acceptance.

## Evidence required in transcript

- Actual native commands, stdout/stderr and exits; claim, receipt and invalidation object bodies.
- Exact target/input bytes and physical identities before refusal and after continuation.
- The genuine Root containment/re-anchor decision and its provider identity, followed by independent original receiving.

## Rollback / defer path

Preserve the disposable task and complete evidence on any failure. Do not repeat an uncertain effect or mutate an original controller. A completed task target need not be reverted; it is confined to this fresh qualification repository.

## Graphify / ActiveGraph / Markdown fallback status

Graphify: absent
ActiveGraph: absent
Markdown fallback: yes

## Cleanliness override, if any

No override. Only the one declared target may differ among tracked task files.

## Maintenance notes

- Retain the exact stale refusal, genuine Root control and final transaction receipts through independent original receiving; these records keep the same pending effect identifiable across re-anchor.
- Preserve the unchanged product source and both authorized input bodies; this episode introduces no runtime owner or helper guard change.

IMPLEMENTAUDIT_PHASE_VERIFY

No acceptance passage is asserted in this initial phase. Real observations and independent adjudication remain required.

AGENTS_UPDATE_DECISION

Decision: not warranted
Reason: this is one bounded qualification episode, not a durable product rule.

CONTINUITY_DECISION

Decision: preserve actual task receipts and failure evidence after the native owners return them.
Evidence boundary: no copied receipt, invented Root decision, model judgment or original case award.

IMPLEMENTAUDIT_PHASE_DONE

Status: open
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action")
    parser.add_argument("--source", required=True)
    parser.add_argument("--work", required=True)
    args = parser.parse_args()
    if args.action == "retain-surviving-evidence":
        output = retain_surviving_evidence(args.work)
        print(json.dumps({"action": args.action, "evidence_directory": str(output), "authority": "NONE", "original_award": False}))
        return
    episode = Episode(args.source, args.work, args.action)
    try:
        episode.execute()
    except Exception as error:
        new_json(episode.evidence / (args.action + "-FAILURE.json"),
                 {"action": args.action, "at": now(), "exception_type": type(error).__name__, "reason": str(error),
                  "effect_outcome": "UNKNOWN_REQUIRES_SURVIVING_EVIDENCE_RECEIVING",
                  "original_award": False, "automatic_replay": False})
        raise
    print(json.dumps({"action": args.action, "completed": True, "original_award": False}))


if __name__ == "__main__":
    main()
