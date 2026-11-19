#!/usr/bin/env python3
"""Prospective ordinary hosted helper qualification; never original acceptance.

Source-author controls may execute only the isolated command-capture boundary.
Do not execute either stage before Root has received the exact candidate and
a genuine nonauthor review. Original helper/controller source remains unexecuted.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time

SOURCE = "a297957be11feb494c0ec467235794a1e0c54751"
SOURCE_TREE = "b08dc4ecf4028beeedb579a312eccae23cb5d863"
REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "refs/heads/qualification/dg17-exact-a297-host-20261118"
PREFIX = "handoff/dg17-exact-host-substrate/"
ADDITIONS = sorted([
    ".github/workflows/dg17-exact-host-substrate.yml",
    PREFIX + "README.md", PREFIX + "SOURCE_MANIFEST.json", PREFIX + "run.py",
])
CONTROLLER = "dg17-exact-host-fixture"
LIMITATIONS = [
    "Helper-substrate evidence only; neither P04 nor B02 is awarded as a whole case.",
    "The scripted driver is not the implementaudit governor or model cognition.",
    "No audit-state/audit-andon/model actor or authenticated native callback is invoked.",
    "Fresh new-session and deliberate manual-resume are fixture boundaries, not native compaction or Stop.",
    "Fixture HEAD/tree are disposable task data, distinct from audited source a297 and workflow candidate.",
    "No original controller, private/protected input or original G2 execution is involved.",
    "No package release, host discovery, model control, original receiving or closure is established.",
]


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def regular(path, limit=2_000_000):
    path = Path(path).absolute()
    for node in (path, *path.parents):
        check(not node.is_symlink(), "symlink in selected physical path: " + str(node))
    before = path.lstat()
    check(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit,
          "nonregular, aliased or oversized selected file: " + str(path))
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(limit + 1)
        closed = os.fstat(stream.fileno())
    after = path.lstat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_uid,
                          s.st_gid, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    check(identity(before) == identity(opened) == identity(closed) == identity(after)
          and len(raw) == before.st_size, "selected file changed during capture")
    return raw


def root_chain(path, consumer_readonly=False):
    rows = []
    for node in (path, *path.parents):
        info = node.lstat()
        check(not stat.S_ISLNK(info.st_mode) and info.st_uid == 0
              and not info.st_mode & 0o022, "UID0/nonwritable ancestry gate: " + str(node))
        if node != path:
            check(stat.S_ISDIR(info.st_mode), "non-directory ancestor")
        if consumer_readonly:
            check(not os.access(node, os.W_OK), "source writable to consuming UID: " + str(node))
        rows.append(dict(path=str(node), uid=info.st_uid, gid=info.st_gid,
                         mode=oct(stat.S_IMODE(info.st_mode)), device=info.st_dev,
                         inode=info.st_ino, links=info.st_nlink))
    return rows


class Episode:
    def __init__(self, stage):
        self.stage = stage
        self.sequence = 0
        self.calls = []
        self.helper_calls = []
        self.helper_attempts = []
        self.result = dict(schema="dg17.exact-host-substrate-result.v1", status="NOT_RUN",
                           audited_source_commit=SOURCE, audited_source_tree=SOURCE_TREE,
                           limitations=LIMITATIONS, whole_P04=False, whole_B02=False,
                           native_activation=False, original_acceptance=False,
                           model_actor_invocations=0, native_callback_invocations=0,
                           existing_controller_effects=0, original_G2_executions=0)
        run_id, attempt = os.environ.get("GITHUB_RUN_ID", ""), os.environ.get("GITHUB_RUN_ATTEMPT", "")
        check(re.fullmatch(r"[1-9][0-9]*", run_id) and attempt == "1", "one fresh attempt required")
        self.identity = "dg17-exact-a297-" + run_id + "-" + attempt
        self.base = Path("/opt") / self.identity
        self.workspace = Path(os.environ["GITHUB_WORKSPACE"]).absolute()
        runner_temp = Path(os.environ["RUNNER_TEMP"]).absolute()
        check(runner_temp.is_dir() and runner_temp.resolve() == runner_temp, "runner temp is aliased")
        self.output = runner_temp / self.identity
        if stage == "prepare":
            self.output.mkdir(mode=0o700)
        else:
            check(self.output.is_dir() and not self.output.is_symlink(), "prepared evidence missing")
        self.logs = self.output / stage
        self.logs.mkdir(mode=0o700)
        self.source = self.base / "source"
        self.fixture = self.base / "fixture"
        self.env = dict(PATH="/usr/bin:/bin", LC_ALL="C", LANG="C",
                        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_SYSTEM="/dev/null",
                        GIT_CONFIG_GLOBAL="/dev/null", GIT_TERMINAL_PROMPT="0",
                        GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1",
                        IMPLEMENTAUDIT_PYTHON="/usr/bin/python3")

    def command(self, label, argv, *, cwd=None, input_bytes=None, allowed=(0,)):
        self.sequence += 1
        stem = f"{self.sequence:03d}-{label}"
        start = time.monotonic()
        record = dict(sequence=self.sequence, label=label, argv=[str(x) for x in argv],
                      cwd=str(cwd or self.workspace), expected_exit_codes=list(allowed),
                      started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        write_json(self.logs / (stem + ".intent.json"), record)
        if record["argv"][:2] == ["/bin/bash", str(self.source / "skills/implementaudit/scripts/claim-run.sh")]:
            self.helper_attempts.append(dict(label=label, intent=self.stage + "/" + stem + ".intent.json"))
        process = subprocess.Popen(record["argv"], cwd=record["cwd"], env=self.env,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        stdout = stderr = None
        timed_out, output_complete, primary_timeout = False, False, None
        record.update(cleanup_errors=[], termination=dict(status="not_required"))

        def capture(suffix, out, err, complete):
            retained = {}
            for kind, raw in (("stdout", out), ("stderr", err)):
                known = raw is not None
                raw = b"" if raw is None else raw
                filename = stem + suffix + "." + kind
                with (self.logs / filename).open("xb") as stream:
                    stream.write(raw)
                    stream.flush()
                    os.fsync(stream.fileno())
                retained[kind] = dict(path=self.stage + "/" + filename,
                                      bytes=len(raw), sha256=digest(raw),
                                      capture_status="complete" if complete else
                                      ("partial" if known else "unknown"))
            return retained

        def secondary(operation, error):
            detail = dict(operation=operation, type=type(error).__name__, message=str(error))
            if isinstance(error, subprocess.TimeoutExpired):
                detail["timeout_seconds"] = error.timeout
            record["cleanup_errors"].append(detail)

        try:
            try:
                stdout, stderr = process.communicate(input_bytes, timeout=60)
                output_complete = True
            except subprocess.TimeoutExpired as error:
                timed_out, primary_timeout = True, error
                stdout, stderr = error.output, error.stderr
                record["primary_error"] = dict(type=type(error).__name__, message=str(error),
                                                timeout_seconds=error.timeout)
                record["timeout_capture"] = capture(".timeout", stdout, stderr, False)
                write_json(self.logs / (stem + ".timeout.json"), dict(
                    primary_error=record["primary_error"], output=record["timeout_capture"],
                    phase="before_owned_group_termination", output_complete=False,
                    returncode=process.returncode))
                record["termination"] = dict(status="attempting", process_group=process.pid,
                                             signal=int(signal.SIGKILL))
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                    record["termination"]["status"] = "signal_sent"
                except Exception as error:
                    record["termination"]["status"] = "failed"
                    secondary("killpg", error)
                try:
                    stdout, stderr = process.communicate(timeout=10)
                    output_complete = True
                except Exception as error:
                    secondary("communicate", error)
                    if isinstance(error, subprocess.TimeoutExpired):
                        if error.output is not None:
                            stdout = error.output
                        if error.stderr is not None:
                            stderr = error.stderr
        finally:
            record.update(capture("", stdout, stderr, output_complete))
            record.update(returncode=process.returncode, timed_out=timed_out,
                          exit_status="unknown" if process.returncode is None else "observed",
                          output_complete=output_complete,
                          status="FAILED_TIMEOUT" if timed_out else
                          ("COMPLETED" if output_complete else "INCOMPLETE"),
                          duration_seconds=round(time.monotonic() - start, 6))
            self.calls.append(record)
            write_json(self.logs / (stem + ".json"), record)
        if primary_timeout is not None:
            raise primary_timeout
        check(process.returncode in allowed, "unexpected command result: " + label)
        return stdout, process.returncode

    def git(self, label, *args, repo=None, input_bytes=None, allowed=(0,)):
        return self.command(label, ["/usr/bin/git", "--no-replace-objects", "-c",
                                   "core.hooksPath=/dev/null", *args],
                            cwd=repo or self.workspace, input_bytes=input_bytes, allowed=allowed)[0]

    def host_and_candidate(self):
        expected = dict(GITHUB_ACTIONS="true", RUNNER_ENVIRONMENT="github-hosted",
                        RUNNER_OS="Linux", RUNNER_ARCH="X64", GITHUB_REPOSITORY=REPOSITORY,
                        GITHUB_EVENT_NAME="push", GITHUB_REF=BRANCH, GITHUB_RUN_ATTEMPT="1")
        check(all(os.environ.get(k) == v for k, v in expected.items()), "host/event/ref qualification failed")
        check(os.name == "posix" and sys.platform == "linux" and os.geteuid() != 0,
              "ordinary unprivileged Linux consumer required")
        release_path = Path("/etc/os-release").resolve(strict=True)
        root_chain(release_path)
        release_raw = regular(release_path)
        release = dict(line.split("=", 1) for line in release_raw.decode().splitlines()
                       if "=" in line and not line.startswith("#"))
        check(release.get("ID", "").strip('"') == "ubuntu"
              and release.get("VERSION_ID", "").strip('"') == "24.04"
              and os.uname().machine == "x86_64", "actual OS/architecture differs from selected hosted class")
        check(self.workspace.resolve() == self.workspace, "checkout path is aliased")
        candidate = os.environ.get("GITHUB_SHA", "")
        check(re.fullmatch(r"[0-9a-f]{40}", candidate), "candidate SHA is malformed")
        event = json.loads(regular(Path(os.environ["GITHUB_EVENT_PATH"]), 2_000_000))
        check(event.get("created") is True and event.get("forced") is False
              and event.get("deleted") is False and event.get("before") == "0" * 40
              and event.get("after") == candidate and event.get("ref") == BRANCH
              and event.get("repository", {}).get("full_name") == REPOSITORY
              and event.get("repository", {}).get("private") is False,
              "only a newly created public qualification branch is admitted")
        head = self.git("candidate-head", "rev-parse", "HEAD").decode().strip()
        parent_row = self.git("candidate-parent", "rev-list", "--parents", "-n", "1", "HEAD").decode().split()
        tree = self.git("audited-source-tree", "rev-parse", SOURCE + "^{tree}").decode().strip()
        check(head == candidate and parent_row == [head, SOURCE] and tree == SOURCE_TREE,
              "candidate must have unchanged exact a297 as its sole parent")
        delta = self.git("candidate-additions", "diff-tree", "--no-commit-id", "--name-status", "-r", SOURCE, "HEAD").decode().splitlines()
        check(sorted(delta) == ["A\t" + p for p in ADDITIONS], "candidate has undeclared or modified source")
        check(not self.git("candidate-cleanliness", "status", "--porcelain=v1"), "candidate checkout is dirty")
        message = self.git("candidate-message", "show", "-s", "--format=%B", "HEAD").decode()
        bindings = {}
        for label in ("DG17-Source-Packet-SHA256", "DG17-Independent-Review-SHA256"):
            found = re.findall(r"^" + label + r": ([0-9a-f]{64})$", message, re.M)
            check(len(found) == 1, "missing or ambiguous Root receiving digest trailer: " + label)
            bindings[label] = found[0]
        python = Path("/usr/bin/python3").resolve(strict=True)
        check(Path(sys.executable).resolve(strict=True) == python and sys.implementation.name == "cpython",
              "driver is not executing the selected installed CPython")
        check(re.fullmatch(r"python3(?:\.[0-9]+)?[tdm]?", python.name), "not an installed Python identity")
        check(any(p.is_file() and os.path.samefile(python, p) for p in
                  (Path("/usr/bin") / python.name, Path("/usr/local/bin") / python.name,
                   Path("/bin") / python.name)), "Python lacks a native installed reference")
        check(regular(python, 64_000_000)[:4] == b"\x7fELF" and os.access(python, os.X_OK), "Python is not native executable ELF")
        ancestry = root_chain(python)
        manifest_path = self.workspace / PREFIX / "SOURCE_MANIFEST.json"
        self.manifest = json.loads(regular(manifest_path))
        check(self.manifest["audited_source_commit"] == SOURCE
              and self.manifest["audited_source_tree"] == SOURCE_TREE, "manifest source mismatch")
        rows = self.manifest["source_population"]
        check(len(rows) == 19 and len({r["path"] for r in rows}) == 19
              and sum(r["bytes"] for r in rows) == 944560, "selected source population changed")
        for row in rows:
            path = Path(row["path"])
            check(not path.is_absolute() and ".." not in path.parts, "manifest path escapes source")
            raw = regular(self.workspace / path)
            check(len(raw) == row["bytes"] and digest(raw) == row["sha256"], "original source digest mismatch: " + str(path))
            original = self.git("source-blob-" + str(rows.index(row)), "cat-file", "blob", SOURCE + ":" + str(path))
            check(original == raw, "working source differs from exact audited object")
        self.result.update(workflow_candidate_commit=head,
                           workflow_candidate_tree=self.git("candidate-tree", "rev-parse", "HEAD^{tree}").decode().strip(),
                           root_receiving_digest_trailers=bindings,
                           review_truth_is_external_root_gate=True,
                           source_manifest_sha256=digest(regular(manifest_path)),
                           interpreter=dict(path=str(python), version=sys.version,
                                            sha256=digest(regular(python, 64_000_000)), ancestry=ancestry),
                           actual_os=dict(release_sha256=digest(release_raw), id=release["ID"],
                                          version=release["VERSION_ID"], machine=os.uname().machine),
                           host_metadata={key: os.environ.get(key) for key in
                                          (*expected, "GITHUB_RUN_ID", "GITHUB_SHA", "ImageOS", "ImageVersion")},
                           consumer_uid=os.geteuid(), consumer_gid=os.getegid(), owned_root=str(self.base))

    def installed_source(self):
        check(self.base.is_dir() and not self.base.is_symlink(), "owned installation absent")
        rows = []
        for selected in self.manifest["source_population"]:
            path = self.source / selected["path"]
            raw = regular(path)
            check(len(raw) == selected["bytes"] and digest(raw) == selected["sha256"], "installed exact source changed")
            root_chain(path, consumer_readonly=True)
            info = path.stat()
            rows.append(dict(path=selected["path"], bytes=len(raw), sha256=digest(raw),
                             uid=info.st_uid, mode=oct(stat.S_IMODE(info.st_mode)),
                             device=info.st_dev, inode=info.st_ino, links=info.st_nlink,
                             mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns))
        for filename in ("run.py", "SOURCE_MANIFEST.json"):
            path = self.base / "driver" / filename
            check(regular(path) == regular(self.workspace / PREFIX / filename), "installed driver differs from candidate")
            root_chain(path, consumer_readonly=True)
        return rows

    def prepare(self):
        self.host_and_candidate()
        check(not os.path.lexists(self.base), "owned installation already exists; do not replay")
        root_chain(Path("/opt"))
        self.command("allocate-owned-root", ["/usr/bin/sudo", "-n", "--", "/usr/bin/mkdir", "-m", "0755", str(self.base)])
        for i, row in enumerate(self.manifest["source_population"]):
            mode = "0755" if row["git_mode"] == "100755" else "0644"
            self.command(f"install-original-{i:02d}", ["/usr/bin/sudo", "-n", "--", "/usr/bin/install", "-D", "-m", mode,
                         str(self.workspace / row["path"]), str(self.source / row["path"])])
        for filename in ("run.py", "SOURCE_MANIFEST.json"):
            self.command("install-driver-" + filename.replace(".", "-"),
                         ["/usr/bin/sudo", "-n", "--", "/usr/bin/install", "-D", "-m", "0444",
                          str(self.workspace / PREFIX / filename), str(self.base / "driver" / filename)])
        self.command("allocate-fixture", ["/usr/bin/sudo", "-n", "--", "/usr/bin/install", "-d", "-m", "0700",
                     "-o", str(os.geteuid()), "-g", str(os.getegid()), str(self.fixture)])
        self.result.update(status="PREPARED_NO_EXACT_HELPER_EXECUTED", installed_source=self.installed_source(),
                           fixture_directory_owner=os.geteuid(), exact_helper_public_calls=0)
        write_json(self.output / "PREPARED.json", self.result)

    def snapshot(self, label):
        rows = []
        for path in sorted(self.fixture.rglob("*")):
            check(not path.is_symlink(), "aliased fixture path")
            if path.is_dir():
                continue
            raw = regular(path)
            info = path.stat()
            rows.append(dict(path=path.relative_to(self.fixture).as_posix(), bytes=len(raw),
                             sha256=digest(raw), uid=info.st_uid, mode=oct(stat.S_IMODE(info.st_mode))))
        check(len(rows) < 512, "fixture unexpectedly exceeded its declared small population")
        write_json(self.logs / (label + ".snapshot.json"), rows)
        return rows

    def owner(self, label, args, *, expected=0, read_only=False):
        before = self.snapshot(label + "-before") if read_only else None
        out, rc = self.command(label, ["/bin/bash", str(self.source / "skills/implementaudit/scripts/claim-run.sh"), *args],
                               cwd=self.fixture, allowed=(0, 1))
        record = dict(label=label, args=args, returncode=rc, expected=expected,
                      stdout_sha256=digest(out), read_only=read_only)
        self.helper_calls.append(record)
        if read_only:
            after = self.snapshot(label + "-after")
            check(before == after, "read-only helper call changed fixture state: " + label)
        check(rc == expected, "exact owner returned unexpected status: " + label)
        return out.decode("utf-8", "strict").strip()

    def read_pair(self, label, root):
        # Separate completed subprocess actions; neither a pipeline nor a forged host event.
        self.command(label + "-STATE", ["/usr/bin/cat", str(root / "STATE.md")], cwd=self.fixture)
        self.command(label + "-ROADMAP", ["/usr/bin/cat", str(root / "ROADMAP.md")], cwd=self.fixture)

    def append_andon(self, root, occurrence, abnormality, countermeasure, evidence):
        path = root / "STATE.md"
        data = regular(path).decode()
        anchor = "| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |\n|---|---|---|---|---|---|---|---|"
        check(data.count(anchor) == 1, "Andon table identity changed")
        row = f"\n| {occurrence} | o{occurrence} | 1 | failed-criterion | {abnormality} | {countermeasure} | {evidence} | open (rerun pending) |"
        path.write_text(data.replace(anchor, anchor + row))

    def gated_effect(self, label, expected):
        before = self.snapshot(label + "-before")
        out, rc = self.command(label, ["/bin/bash", str(self.source / "skills/implementaudit/scripts/claim-run.sh"),
                                      "--require-current-continuity", CONTROLLER], cwd=self.fixture, allowed=(0, 1))
        after = self.snapshot(label + "-owner-after")
        check(before == after, "currentness check mutated its subject")
        self.helper_calls.append(dict(label=label, args=["--require-current-continuity", CONTROLLER],
                                      returncode=rc, expected=expected, read_only=True, stdout_sha256=digest(out)))
        effect = self.fixture / "effect-applied.txt"
        if rc == 0:
            with effect.open("xb") as stream:
                stream.write(b"Harmless fixture-only effect admitted by the actual exact helper.\n")
        check(rc == expected, "currentness gate gave the unexpected effect decision")
        check(effect.exists() == (expected == 0), "fixture effect violated currentness gate")
        return out.decode().strip()

    def exercise(self):
        self.host_and_candidate()
        check(Path(__file__).absolute() == self.base / "driver/run.py", "exercise requires installed reviewed driver")
        starting_source = self.installed_source()
        check(not any(self.fixture.iterdir()), "fixture is not fresh; no replay")
        self.git("fixture-init", "init", "--object-format=sha1", "--initial-branch=fixture", "--template=", repo=self.fixture)
        (self.fixture / "subject.txt").write_bytes(b"Disposable exact-helper substrate subject.\n")
        (self.fixture / ".gitignore").write_bytes(b".IMPLEMENTAUDIT/\neffect-applied.txt\n")
        self.git("fixture-add", "add", "--", "subject.txt", ".gitignore", repo=self.fixture)
        self.git("fixture-commit", "-c", "user.name=DG17 disposable fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--no-verify", "-m", "Disposable task baseline; not audited DG17 source", repo=self.fixture)
        fixture_head = self.git("fixture-head", "rev-parse", "HEAD", repo=self.fixture).decode().strip()
        fixture_tree = self.git("fixture-tree", "rev-parse", "HEAD^{tree}", repo=self.fixture).decode().strip()
        check(fixture_head not in {SOURCE, self.result["workflow_candidate_commit"]}, "fixture/source conflation")
        self.result.update(fixture_head=fixture_head, fixture_tree=fixture_tree,
                           fixture_head_is_audited_source=False)
        relative = self.owner("01-claim-pending", ["--controller", CONTROLLER, "dg17 exact hosted substrate"])
        check(re.fullmatch(r"\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}", relative), "unexpected claimed root")
        root = self.fixture / relative
        purpose = ("Qualify unchanged a297 exact helper substrate in a fresh disposable hosted task. "
                   "This task HEAD is fixture data, not audited source a297. No original governor/model/native award.")
        next_action = "Receive the exact helper currentness refusal and bounded manual re-anchor on this disposable fixture"
        self.command("author-original-fresh-checkpoint", ["/usr/bin/python3", "-I", "-B",
                     str(self.source / "fixtures/controller-initialization/author_checkpoint.py"),
                     "--repo", str(self.fixture), "--run-root", relative, "--source", str(self.source),
                     "--purpose", purpose, "--next-action", next_action], cwd=self.fixture)
        inspection = json.loads(self.owner("02-inspect-initialization", ["--inspect-controller-initialization", CONTROLLER,
                                             "--run-root", relative], read_only=True))
        check(inspection["current_controller_oid"] is None, "pending claim was promoted early")
        self.owner("03-activate-initialization", ["--activate-controller", CONTROLLER, "--run-root", relative,
                                                 "--expected-initialization", inspection["initialization_token"]])
        self.owner("04-current-controller", ["--current-controller", CONTROLLER], read_only=True)
        self.owner("05-no-receipt-refusal", ["--require-current-continuity", CONTROLLER], expected=1, read_only=True)
        self.append_andon(root, "1", "Controlled fresh-fixture currentness request has no receipt",
                          "Deterministic driver preserves refusal and follows the ordinary owner route; zero child calls",
                          "05-no-receipt-refusal captures; repair not yet claimed")
        self.owner("06-new-session-invalidation", ["--invalidate-continuity", CONTROLLER, "--boundary", "new-session",
                                                    "--event", self.identity + "-fresh-fixture-session"])
        self.read_pair("initial-reconciliation", root)
        first = self.owner("07-resume-G0001", ["--resume-controller", CONTROLLER, "--boundary", "new-session", "--epoch", "G0001"])
        self.owner("08-verify-G0001", ["--verify-resume-receipt", first], read_only=True)
        check(self.owner("09-require-G0001", ["--require-current-continuity", CONTROLLER], read_only=True) == first,
              "initial currentness did not return the exact receipt")
        self.owner("10-manual-invalidation", ["--invalidate-continuity", CONTROLLER, "--boundary", "manual-resume",
                                              "--event", self.identity + "-deliberate-manual-reanchor"])
        self.gated_effect("11-stale-withholds-effect", 1)
        self.owner("12-stale-receipt-refusal", ["--verify-resume-receipt", first], expected=1, read_only=True)
        self.append_andon(root, "2", "Deliberate manual boundary invalidated the prior fixture receipt; effect withheld",
                          "Preserve both actual refusals and author G0002 before separate STATE and ROADMAP reads",
                          "11-stale-withholds-effect and 12-stale-receipt-refusal captures; re-anchor pending")
        state = regular(root / "STATE.md").decode()
        check(state.count("Current epoch: G0001") == 1, "initial epoch identity changed")
        anchor = "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
        row = (f"\n| G0002 | manual-resume | {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} | "
               f"disposable fixture `{fixture_head}` / `{fixture_tree}` | yes | Deliberate manual re-anchor; "
               "actual prior refusal retained; no physical compaction or Stop claim |")
        check(state.count(anchor) == 1, "epoch table identity changed")
        (root / "STATE.md").write_text(state.replace("Current epoch: G0001", "Current epoch: G0002").replace(anchor, anchor + row))
        self.read_pair("manual-reconciliation", root)
        second = self.owner("13-resume-G0002", ["--resume-controller", CONTROLLER, "--boundary", "manual-resume", "--epoch", "G0002"])
        check(second != first, "manual boundary reused the predecessor receipt")
        self.owner("14-verify-G0002", ["--verify-resume-receipt", second], read_only=True)
        check(self.gated_effect("15-current-admits-fixture-effect", 0) == second, "effect used a different receipt")
        self.owner("16-predecessor-still-refused", ["--verify-resume-receipt", first], expected=1, read_only=True)
        final_source = self.installed_source()
        check(starting_source == final_source, "installed original source changed during episode")
        check(not self.git("fixture-final-cleanliness", "status", "--porcelain=v1", repo=self.fixture), "tracked fixture source changed")
        state = regular(root / "STATE.md").decode()
        check("| Status | open |" in state and "| Audit object state | open |" in state,
              "fixture must remain explicitly nonterminal")
        check(not re.search(r"^(?:AUDIT_COMPLETE|IMPLEMENTAUDIT_RUN_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF)$", state, re.M),
              "unexpected fixture terminal marker")
        final = self.snapshot("terminal")
        retained = self.output / "retained-fixture"
        retained.mkdir()
        # Public, constructed task files only; no .git/config, credentials or original records.
        file_map = []
        for path in sorted(root.rglob("*")):
            if path.is_file():
                relative_file = path.relative_to(root)
                if any(part.startswith(".") for part in relative_file.parts):
                    check(relative_file.as_posix() in {".claimed", ".controller"}, "unexpected hidden fixture record")
                    artifact_relative = Path("custody-records") / (relative_file.name[1:] + ".txt")
                else:
                    artifact_relative = relative_file
                target = retained / artifact_relative
                target.parent.mkdir(parents=True, exist_ok=True)
                raw = regular(path)
                target.write_bytes(raw)
                file_map.append(dict(fixture_path=relative_file.as_posix(),
                                     artifact_path=target.relative_to(self.output).as_posix(),
                                     bytes=len(raw), sha256=digest(raw)))
        write_json(self.output / "FIXTURE_FILE_MAP.json", file_map)
        refs = self.git("fixture-ref-census", "for-each-ref", "--format=%(refname) %(objectname)",
                        "refs/implementaudit/", repo=self.fixture).decode().splitlines()
        ref_records = []
        for i, line in enumerate(refs):
            ref, oid = line.split()
            raw = self.git(f"fixture-ref-blob-{i:02d}", "cat-file", "blob", oid, repo=self.fixture)
            ref_records.append(dict(ref=ref, oid=oid, bytes=len(raw), sha256=digest(raw), content=raw.decode()))
        write_json(self.output / "FIXTURE_REFS.json", ref_records)
        self.result.update(status="PASS_HELPER_SUBSTRATE_ONLY", exact_helper_public_calls=len(self.helper_calls),
                           helper_calls=self.helper_calls, installed_source_unchanged=True,
                           installed_source=final_source, first_fixture_receipt=first, second_fixture_receipt=second,
                           fixture_run_root=relative, final_fixture_snapshot_sha256=digest(json.dumps(final, sort_keys=True).encode()),
                           fixture_root_nonterminal=True, expected_refusals_preserved=True,
                           stale_effect_withheld=True, reanchored_fixture_effect_applied=True,
                           fixture_effect_sha256=digest(regular(self.fixture / "effect-applied.txt")),
                           B02_scope="Scripted deterministic handling of a real constructed helper refusal; no governor judgment claim",
                           P04_scope="Exact helper mismatch/refusal, withheld fixture effect and manual re-anchor; no whole L4/L2 claim",
                           unresolved_fixture_andon_rows="Remain historical open rows; success is recorded externally to avoid invalidating final receipt")

    def finish(self, error=None):
        if error is not None:
            self.result.update(status="FAIL_OR_INCOMPLETE_NO_ACCEPTANCE", failure_type=type(error).__name__,
                               failure=str(error), exact_helper_public_calls=len(self.helper_calls), helper_calls=self.helper_calls)
        self.result.update(exact_helper_public_call_attempts=len(self.helper_attempts),
                           helper_call_attempts=self.helper_attempts,
                           counted_public_calls_mean="Completed driver checks; intent-only or interrupted attempts remain separate")
        if self.stage == "exercise" or error is not None:
            write_json(self.output / ("RESULT.json" if self.stage == "exercise" else "PREPARATION_FAILURE.json"), self.result)
        if self.stage == "exercise" or error is not None:
            inventory = []
            for path in sorted(self.output.rglob("*")):
                if path.is_file():
                    raw = regular(path, 4_000_000)
                    inventory.append(dict(path=path.relative_to(self.output).as_posix(), bytes=len(raw), sha256=digest(raw)))
            write_json(self.output / "RESULT_INVENTORY.json", inventory)
            for path in sorted(self.output.rglob("*"), reverse=True):
                path.chmod(0o555 if path.is_dir() else 0o444)
            self.output.chmod(0o555)
        print(json.dumps(dict(stage=self.stage, status=self.result["status"], result_directory=str(self.output)), sort_keys=True))


def main():
    check(sys.argv[1:] in (["prepare"], ["exercise"]), "exact stage prepare or exercise required")
    episode = Episode(sys.argv[1])
    failure = None
    try:
        getattr(episode, episode.stage)()
    except Exception as exc:
        failure = exc
    episode.finish(failure)
    return 1 if failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
