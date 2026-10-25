#!/usr/bin/env python3
"""Opt-in, repo-only owner of the finite reproduction C5 event profile.

R0035_REPRO_EVENT_CAPTURE_DIR is a fresh absolute directory outside the product
and temporary worktrees. The reproduction shell calls init, event, close, and
finish. Each event launches the original argv in the original cwd/environment;
inline Python receives the original heredoc bytes. stdout/stderr are separately
teed without normalization. Original comparison operands and successful output
generations are retained before the shell's existing EXIT cleanup.
The v2 envelope binds a durable raw process receipt to each completed event.
Post-child acquisition failure keeps the receipt and an explicit failed handoff;
it cannot produce a complete profile. Observed unsupported input kinds are
refused before dispatch, while missing ordinary operands keep the child's exit.

verify_record(directory, *, expected_source=None, expected_run_id=None,
              require_complete=True) checks the complete finite profile derived
here, not a captured event count. expected_source is an exact subset of source:
source_commit/source_tree and producer/capture_owner identities, each identity
being {path, bytes, sha256, mode}. The returned envelope is declared consistency
only. An imported/resealed envelope is NOT authenticated original-event custody.
The live helper observes its own children; no external protected custodian,
acquired runtime image, whole-shell effects, or full canonical reuse is claimed.

File custody checks include inode/device, mode, link count, size, mtime and ctime
at ordinary before/after boundaries. They detect ordinary drift and byte/mtime
restoration; they are not a guarantee against privileged or concurrent attacks.
Bounds are fail-closed capture limits, not changes to default reproduction.
"""

import argparse
import base64
import binascii
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
import uuid
import zipfile


SCHEMA = "implementaudit.repro-events.v2"
PROFILE = "REPRODUCIBLE_RELEASE_ASSET_C5_V1"
PRODUCER = "tests/reproducible-release-asset.test.sh"
OWNER = "scripts/repro-event-capture.py"
BUILD = "scripts/build-release-asset.sh"
CHECKSUM = "scripts/write-release-checksums.sh"
MEMBERS = ("IMPLEMENTAUDIT.plugin.zip", "IMPLEMENTAUDIT.skill", "CHECKSUMS.txt")
HASH_PROGRAM = 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())'
MAX_FILE = 16 * 1024 * 1024
MAX_STREAM = 8 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_MEMBERS = 128
MAX_JSON = 4 * 1024 * 1024
# A process receipt embeds both raw streams before post-child acquisition can
# fail. Its bound must accommodate two complete MAX_STREAM base64 payloads.
MAX_PROCESS_JSON = 2 * (4 * ((MAX_STREAM + 2) // 3)) + MAX_JSON
PROCESS_COMMON = ("schema profile run_id index event_id role source_sha256 argv cwd "
                  "environment_sha256 environment_projection stdin exit_code capture_errors "
                  "start_monotonic_ns end_monotonic_ns")
EVENT_FIELDS = (PROCESS_COMMON + " stdout stderr inputs_before inputs_after outputs_before outputs_after "
                "source_before source_after clone_before clone_after executable_before executable_after generation_id")
HEX = re.compile(r"[0-9a-f]{64}\Z")
SEMANTICS = "OWN_CHILD_PROCESS_OBSERVATIONS; IMPORTED_READBACK_DECLARED_CONSISTENCY_ONLY"


class ReproCaptureError(ValueError):
    pass


def demand(condition, message):
    if not condition:
        raise ReproCaptureError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def integer(value):
    return type(value) is int


def fields(value, names, what):
    demand(type(value) is dict and set(value) == set(names.split()),
           "invalid " + what + " fields")


def metadata(value):
    return dict(device=value.st_dev, inode=value.st_ino, mode=stat.S_IMODE(value.st_mode),
                links=value.st_nlink, size=value.st_size,
                mtime_ns=value.st_mtime_ns, ctime_ns=value.st_ctime_ns)


def reparse(value):
    return bool(getattr(value, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def no_alias(path, *, missing=False):
    path = Path(path)
    demand(path.is_absolute() and str(path) == os.path.normpath(str(path)),
           "absolute normalized path required")
    for item in [*reversed(path.parents), path]:
        try:
            observed = item.lstat()
        except FileNotFoundError:
            if missing and item == path:
                break
            raise ReproCaptureError("missing path ancestor: " + str(item))
        demand(not stat.S_ISLNK(observed.st_mode) and not reparse(observed),
               "link/reparse path forbidden: " + str(item))
    return path


def read_regular(path, limit=MAX_FILE):
    path = no_alias(path)
    before = path.lstat()
    demand(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
           "ordinary single-link file required: " + str(path))
    demand(before.st_size <= limit, "file exceeds capture bound")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        demand(metadata(os.fstat(fd)) == metadata(before), "file changed at open")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(limit + 1)
        demand(len(data) <= limit and metadata(os.fstat(fd)) == metadata(before),
               "file changed during read or exceeds bound")
    finally:
        os.close(fd)
    demand(metadata(path.lstat()) == metadata(before), "file changed after read")
    return data, metadata(before)


def json_read(path, limit=MAX_JSON):
    data, observed = read_regular(path, limit)
    demand(observed["mode"] == 0o600, "retained JSON mode changed")
    def pairs(items):
        result = {}
        for key, value in items:
            demand(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=pairs,
                          parse_constant=lambda value: demand(False, "nonfinite JSON"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReproCaptureError("invalid JSON") from exc


def write_new(path, data, *, sync_parent=False):
    no_alias(path.parent)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(fd)
    if sync_parent:
        fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                     getattr(os, "O_NOFOLLOW", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def put_blob(directory, data):
    demand(len(data) <= MAX_FILE, "blob exceeds capture bound")
    sha = digest(data)
    path = directory / "blobs" / sha
    if path.exists() or path.is_symlink():
        old, _ = read_regular(path)
        demand(old == data, "retained blob changed")
    else:
        write_new(path, data)
    return dict(bytes=len(data), sha256=sha)


class Readback:
    def __init__(self, directory):
        self.directory = no_alias(Path(directory))
        demand(self.directory.is_dir(), "capture root must be a directory")
        self.used = set()
        self.process_used = set()
        self.total = 0

    def process_bytes(self, path, data):
        if path not in self.process_used:
            self.process_used.add(path)
            self.total += len(data)
        demand(self.total <= MAX_TOTAL, "capture namespace exceeds bound")

    def blob(self, descriptor):
        fields(descriptor, "bytes sha256", "blob")
        demand(integer(descriptor["bytes"]) and 0 <= descriptor["bytes"] <= MAX_FILE
               and type(descriptor["sha256"]) is str and HEX.fullmatch(descriptor["sha256"]),
               "invalid blob identity")
        name = descriptor["sha256"]
        data, observed = read_regular(self.directory / "blobs" / name)
        demand(observed["mode"] == 0o600, "retained blob mode changed")
        demand(len(data) == descriptor["bytes"] and digest(data) == name,
               "retained blob identity mismatch")
        if name not in self.used:
            self.used.add(name)
            self.total += len(data)
        demand(len(self.used) <= MAX_MEMBERS and self.total <= MAX_TOTAL,
               "capture namespace exceeds bound")
        return data


def observe(directory, path):
    """A flat bounded namespace observation; no recursive traversal or symlinks."""
    path = Path(path)
    try:
        no_alias(path.parent)
        value = path.lstat()
    except FileNotFoundError:
        return dict(path=str(path), kind="MISSING")
    except ReproCaptureError:
        return dict(path=str(path), kind="UNSAFE_PARENT")
    result = dict(path=str(path), stat=metadata(value))
    if stat.S_ISLNK(value.st_mode) or reparse(value):
        return dict(result, kind="LINK")
    if stat.S_ISREG(value.st_mode):
        if value.st_nlink != 1:
            return dict(result, kind="HARDLINK")
        if value.st_size > MAX_FILE:
            return dict(result, kind="OVERSIZE")
        data, current = read_regular(path)
        return dict(path=str(path), kind="FILE", stat=current,
                    blob=put_blob(directory, data))
    if stat.S_ISDIR(value.st_mode):
        names = sorted(os.listdir(path))
        if len(names) > MAX_MEMBERS:
            return dict(result, kind="OVERSIZE_DIRECTORY")
        members = []
        for name in names:
            child = path / name
            child_stat = child.lstat()
            if stat.S_ISDIR(child_stat.st_mode) and not reparse(child_stat):
                members.append(dict(path=str(child), kind="NESTED_DIRECTORY",
                                    stat=metadata(child_stat)))
            else:
                members.append(observe(directory, child))
        demand(metadata(path.lstat()) == metadata(value), "directory changed during capture")
        return dict(result, kind="DIRECTORY", members=members)
    return dict(result, kind="SPECIAL")


def observation(reader, item, expected_path):
    demand(type(item) is dict and item.get("path") == str(expected_path),
           "observation path mismatch")
    kind = item.get("kind")
    if kind in {"MISSING", "UNSAFE_PARENT"}:
        fields(item, "path kind", "missing observation")
        return
    known = {"FILE", "DIRECTORY", "LINK", "HARDLINK", "OVERSIZE",
             "OVERSIZE_DIRECTORY", "NESTED_DIRECTORY", "SPECIAL"}
    demand(kind in known, "unknown observation kind")
    keys = "path kind stat" + (" blob" if kind == "FILE" else " members" if kind == "DIRECTORY" else "")
    fields(item, keys, "observation")
    fields(item["stat"], "device inode mode links size mtime_ns ctime_ns", "stat")
    demand(all(integer(v) for v in item["stat"].values()) and
           all(item["stat"][key] >= 0 for key in ("device", "inode", "mode", "links", "size"))
           and item["stat"]["mode"] <= 0o7777, "invalid stat observation")
    if kind == "FILE":
        demand(item["stat"]["links"] == 1, "invalid retained file links")
        data = reader.blob(item["blob"])
        demand(len(data) == item["stat"]["size"], "file size mismatch")
    if kind == "DIRECTORY":
        members = item["members"]
        demand(type(members) is list and len(members) <= MAX_MEMBERS,
               "invalid namespace members")
        names = []
        for member in members:
            demand(type(member) is dict and type(member.get("path")) is str,
                   "invalid namespace member")
            path = Path(member["path"])
            demand(path.parent == Path(expected_path), "foreign namespace member")
            names.append(path.name)
            observation(reader, member, path)
            demand(member["kind"] != "DIRECTORY", "recursive namespace forbidden")
        demand(names == sorted(set(names)), "duplicate or reordered namespace member")


def identity(path, data, mode):
    return dict(path=path, bytes=len(data), sha256=digest(data), mode=mode)


def source_now(directory, session):
    repo = Path(session["context"]["repository"])
    return {name: observe(directory, repo / path)
            for name, path in (("producer", PRODUCER), ("capture_owner", OWNER))}


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    demand(result.returncode == 0, "source Git read failed")
    return result.stdout


def init(directory, repository, work_root, source_commit, python_command):
    directory = no_alias(Path(directory), missing=True)
    repo, work = no_alias(Path(repository)), no_alias(Path(work_root))
    demand(not directory.exists(), "capture destination already exists")
    demand(repo.is_dir() and work.is_dir(), "real source and work directories required")
    for other in (repo, work):
        demand(not directory.is_relative_to(other) and not other.is_relative_to(directory),
               "capture must be outside source and temporary worktrees")
    demand(python_command in {"python", "python3"}, "unsupported Python command")
    demand(re.fullmatch(r"[0-9a-f]{40}", source_commit), "invalid source commit")
    tree = git(repo, "rev-parse", source_commit + "^{tree}").decode().strip()
    demand(re.fullmatch(r"[0-9a-f]{40}", tree), "invalid source tree")
    directory.mkdir(mode=0o700)
    (directory / "blobs").mkdir(mode=0o700)
    (directory / "events").mkdir(mode=0o700)
    (directory / "processes").mkdir(mode=0o700)
    session = dict(schema=SCHEMA, profile=PROFILE, run_id=uuid.uuid4().hex,
                   context=dict(repository=str(repo), work_root=str(work), cwd=os.getcwd(),
                                python_command=python_command),
                   source=dict(source_commit=source_commit, source_tree=tree),
                   source_custody={}, source_scripts={}, semantics=SEMANTICS)
    session["source_custody"] = source_now(directory, session)
    for name, observed in session["source_custody"].items():
        demand(observed["kind"] == "FILE", "ordinary source owner required")
        data = Readback(directory).blob(observed["blob"])
        session["source"][name] = identity(PRODUCER if name == "producer" else OWNER,
                                            data, observed["stat"]["mode"])
    for role, path in (("build", BUILD), ("checksum", CHECKSUM)):
        data = git(repo, "show", source_commit + ":" + path)
        mode = git(repo, "ls-tree", source_commit, "--", path).split(b" ", 1)[0]
        demand(mode in {b"100644", b"100755"}, "unsupported source script mode")
        session["source_scripts"][role] = dict(path=path, mode=int(mode, 8) & 0o777,
                                                blob=put_blob(directory, data))
    write_new(directory / "session.json", canonical(session))
    return session


def profile(session):
    """The source contract, including the original interleaved manifest cmps."""
    root = Path(session["context"]["work_root"])
    py = session["context"]["python_command"]
    rows = []
    def add(role, argv, inputs=(), outputs=(), inline=False, lane=None):
        rows.append(dict(role=role, argv=list(map(str, argv)),
                         inputs=list(map(str, inputs)), outputs=list(map(str, outputs)),
                         inline=inline, lane=lane))
    for lane in "ab":
        add("build:" + lane, ["bash", root / ("checkout-" + lane) / BUILD, root / ("out-" + lane)],
            outputs=[root / ("out-" + lane)], lane=lane)
    for member in MEMBERS:
        paths = [root / ("out-" + lane) / member for lane in "ab"]
        add("cmp:" + member, ["cmp", "-s", *paths], paths)
    for lane in "ab":
        out = root / ("out-" + lane)
        add("checksum:" + lane,
            ["bash", root / ("checkout-" + lane) / CHECKSUM, "--check", "--all", out, out / "CHECKSUMS.txt"],
            [out], lane=lane)
    for role, member in (("plugin", MEMBERS[0]), ("skill", MEMBERS[1])):
        for lane in "ab":
            archive = root / ("out-" + lane) / member
            add("manifest:" + role + ":" + lane, [py, "-", archive], [archive],
                [root / (role + "-manifest-" + lane + ".json")], inline=True)
        paths = [root / (role + "-manifest-" + lane + ".json") for lane in "ab"]
        add("manifest-cmp:" + role, ["cmp", "-s", *paths], paths)
    for role, member in (("skill", MEMBERS[1]), ("plugin", MEMBERS[0]), ("checksums", MEMBERS[2])):
        for lane in "ab":
            path = root / ("out-" + lane) / member
            add("hash:" + role + ":" + lane, [py, "-c", HASH_PROGRAM, path], [path])
    return rows


def manifest_program(reader, session):
    source = reader.blob(session["source_custody"]["producer"]["blob"])
    bodies = re.findall(rb"<<'PY'\n(.*?)\nPY\n", source, re.S)
    selected = [body + b"\n" for body in bodies if b"with zipfile.ZipFile(asset) as archive:" in body]
    demand(len(selected) == 1, "source manifest producer is not uniquely identified")
    return selected[0]


def load_session(directory, reader):
    session = json_read(directory / "session.json")
    fields(session, "schema profile run_id context source source_custody source_scripts semantics", "session")
    demand(session["schema"] == SCHEMA and session["profile"] == PROFILE and
           session["semantics"] == SEMANTICS, "unsupported C5 profile")
    demand(type(session["run_id"]) is str and re.fullmatch(r"[0-9a-f]{32}", session["run_id"]),
           "invalid run identity")
    fields(session["context"], "repository work_root cwd python_command", "context")
    for key in ("repository", "work_root", "cwd"):
        value = session["context"][key]
        demand(type(value) is str and Path(value).is_absolute() and os.path.normpath(value) == value,
               "invalid context path")
    demand(session["context"]["python_command"] in {"python", "python3"}, "invalid Python command")
    fields(session["source"], "source_commit source_tree producer capture_owner", "source")
    for key in ("source_commit", "source_tree"):
        demand(type(session["source"][key]) is str and re.fullmatch(r"[0-9a-f]{40}", session["source"][key]),
               "invalid source identity")
    fields(session["source_custody"], "producer capture_owner", "source custody")
    for name, path in (("producer", PRODUCER), ("capture_owner", OWNER)):
        item = session["source_custody"][name]
        observation(reader, item, Path(session["context"]["repository"]) / path)
        demand(item["kind"] == "FILE", "non-file source owner")
        fields(session["source"][name], "path bytes sha256 mode", "source owner identity")
        demand(session["source"][name] == identity(path, reader.blob(item["blob"]), item["stat"]["mode"]),
               "source owner identity mismatch")
    fields(session["source_scripts"], "build checksum", "source scripts")
    for role, path in (("build", BUILD), ("checksum", CHECKSUM)):
        item = session["source_scripts"][role]
        fields(item, "path mode blob", "source script")
        demand(item["path"] == path and type(item["mode"]) is int and item["mode"] in {0o644, 0o755},
               "invalid source script")
        reader.blob(item["blob"])
    manifest_program(reader, session)
    return session


def clone_observation(directory, session, lane):
    if lane is None:
        return None
    root = Path(session["context"]["work_root"]) / ("checkout-" + lane)
    try:
        head = git(root, "rev-parse", "HEAD").decode().strip()
        tree = git(root, "rev-parse", "HEAD^{tree}").decode().strip()
        status = put_blob(directory, git(root, "status", "--porcelain", "--untracked-files=all"))
    except ReproCaptureError:
        return dict(head=None, tree=None, status=None, scripts={})
    return dict(head=head, tree=tree, status=status,
                scripts={name: observe(directory, root / value["path"])
                         for name, value in session["source_scripts"].items()})


def executable(directory, argv):
    resolved = shutil.which(argv[0])
    if resolved is None:
        return None
    return observe(directory, Path(resolved).resolve(strict=True))


def capture_process(argv, inline):
    """Own-child launch. No result is inferred from a later comparison."""
    raw = {"stdout": bytearray(), "stderr": bytearray()}
    errors = []
    try:
        process = subprocess.Popen(argv, stdin=subprocess.PIPE if inline is not None else None,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as exc:
        return None, b"", b"", ["LAUNCH_FAILED:" + str(exc.errno)]
    def drain(name, source, target):
        try:
            while True:
                chunk = source.read(65536)
                if not chunk:
                    break
                if len(raw[name]) + len(chunk) > MAX_STREAM:
                    errors.append("RAW_STREAM_BOUND:" + name)
                    process.kill()
                    break
                raw[name].extend(chunk)
                target.write(chunk)
                target.flush()
        except (OSError, ValueError) as exc:
            errors.append("STREAM_HANDOFF_FAILED:" + name + ":" + type(exc).__name__)
            process.kill()
        finally:
            source.close()
    threads = [threading.Thread(target=drain, args=(name, getattr(process, name),
                                                   getattr(sys, name).buffer))
               for name in ("stdout", "stderr")]
    for thread in threads:
        thread.start()
    if inline is not None:
        try:
            process.stdin.write(inline)
            process.stdin.close()
        except BrokenPipeError:
            errors.append("INLINE_STDIN_PIPE_CLOSED")
    code = process.wait()
    for thread in threads:
        thread.join()
    return code, bytes(raw["stdout"]), bytes(raw["stderr"]), sorted(errors)


def event_files(directory):
    no_alias(directory / "events")
    names = sorted(os.listdir(directory / "events"))
    demand(len(names) <= 19, "event namespace exceeds finite profile")
    demand(names == [f"{index:02d}.json" for index in range(len(names))],
           "missing, reordered, or foreign event file")
    return [directory / "events" / name for name in names]


def unsupported_inputs(spec, observations):
    """Refuse observed special/alias inputs before the original child launches.

    MISSING is allowed: ordinary commands retain their actual missing-file exit.
    Only the checksum consumer accepts a flat directory as its input namespace.
    This is an ordinary observation boundary, not a race-free acquired image.
    """
    errors = []
    for item in observations:
        kind = item["kind"]
        if spec["role"].startswith("checksum:") and kind == "DIRECTORY":
            for member in item["members"]:
                if member["kind"] not in {"FILE", "MISSING"}:
                    errors.append("UNSUPPORTED_INPUT_KIND:" + member["path"] + ":" + member["kind"])
        elif kind not in {"FILE", "MISSING"}:
            errors.append("UNSUPPORTED_INPUT_KIND:" + item["path"] + ":" + kind)
    return sorted(errors)


def invocation(reader, session, item, spec, index, last_end):
    event_id = session["run_id"] + ":" + f"{index:02d}" + ":" + spec["role"]
    demand(item["schema"] == SCHEMA and item["profile"] == PROFILE and
           item["run_id"] == session["run_id"] and integer(item["index"]) and
           item["index"] == index and item["event_id"] == event_id and item["role"] == spec["role"],
           "missing, duplicate, reordered, or foreign invocation")
    demand(item["source_sha256"] == digest(canonical(session["source"])), "foreign invocation source")
    demand(item["argv"] == spec["argv"] and item["cwd"] == session["context"]["cwd"],
           "invocation mismatch")
    demand(type(item["environment_sha256"]) is str and HEX.fullmatch(item["environment_sha256"]),
           "invalid child environment digest")
    fields(item["environment_projection"], "SOURCE_DATE_EPOCH TZ LC_ALL", "environment projection")
    demand(all(value is None or type(value) is str for value in item["environment_projection"].values()),
           "invalid child environment projection")
    if spec["role"].startswith("build:"):
        wanted = dict(SOURCE_DATE_EPOCH="315532800", TZ="UTC" if spec["lane"] == "a" else "America/New_York", LC_ALL="C")
        demand(item["environment_projection"] == wanted, "build environment mismatch")
    demand(integer(item["start_monotonic_ns"]) and integer(item["end_monotonic_ns"]) and
           last_end <= item["start_monotonic_ns"] <= item["end_monotonic_ns"], "invocation temporal order mismatch")
    if spec["inline"]:
        fields(item["stdin"], "mode blob", "inline stdin")
        demand(item["stdin"]["mode"] == "INLINE_BYTES" and
               reader.blob(item["stdin"]["blob"]) == manifest_program(reader, session),
               "inline stdin mismatch")
    else:
        demand(item["stdin"] == dict(mode="INHERITED_UNQUALIFIED"), "unexpected stdin capture")
    code = item["exit_code"]
    demand(code is None or integer(code) and -255 <= code <= 255, "invalid child exit code")
    demand(type(item["capture_errors"]) is list and all(type(error) is str for error in item["capture_errors"]),
           "invalid capture errors")
    return item["end_monotonic_ns"]


def event(directory, role, argv):
    directory = no_alias(Path(directory))
    demand(not (directory / "close.json").exists(), "capture already closed")
    lock = directory / "lock"
    lock.mkdir(mode=0o700)
    try:
        reader = Readback(directory)
        session = load_session(directory, reader)
        paths = event_files(directory)
        expected = profile(session)
        demand(len(paths) < len(expected), "extra event")
        spec = expected[len(paths)]
        demand(role == spec["role"] and argv == spec["argv"], "foreign or reordered invocation")
        demand(os.getcwd() == session["context"]["cwd"], "event cwd changed")
        previous = [json_read(path) for path in paths]
        process_names = sorted(os.listdir(no_alias(directory / "processes")))
        demand(process_names == [f"{index:02d}.json" for index in range(len(paths))],
               "event after missing process receipt or failed handoff")
        if previous:
            demand(previous[-1]["exit_code"] == 0 and not previous[-1]["capture_errors"],
                   "event after failed child/handoff")
        before_inputs = [observe(directory, Path(path)) for path in spec["inputs"]]
        before_outputs = [observe(directory, Path(path)) for path in spec["outputs"]]
        before_source = source_now(directory, session)
        before_clone = clone_observation(directory, session, spec["lane"])
        before_executable = executable(directory, argv)
        inline = sys.stdin.buffer.read(MAX_FILE + 1) if spec["inline"] else None
        demand(inline is None or inline == manifest_program(reader, session),
               "inline producer stdin differs from bound source")
        env = dict(os.environ)
        event_id = session["run_id"] + ":" + f"{len(paths):02d}" + ":" + role
        common = dict(schema=SCHEMA, profile=PROFILE, run_id=session["run_id"],
                      index=len(paths), event_id=event_id, role=role,
                      source_sha256=digest(canonical(session["source"])),
                      argv=argv, cwd=os.getcwd(),
                      environment_sha256=digest(canonical(env)),
                      environment_projection={key: env.get(key) for key in ("SOURCE_DATE_EPOCH", "TZ", "LC_ALL")},
                      stdin=dict(mode="INLINE_BYTES", blob=put_blob(directory, inline)) if inline is not None
                      else dict(mode="INHERITED_UNQUALIFIED"))
        demand(len(canonical(common)) <= MAX_JSON - 1024, "process metadata exceeds capture bound")
        start = time.monotonic_ns()
        unsupported = unsupported_inputs(spec, before_inputs)
        if unsupported:
            code, stdout, stderr, errors = None, b"", b"", unsupported
            dispatch = "NOT_STARTED_UNSUPPORTED_INPUT"
        else:
            code, stdout, stderr, errors = capture_process(argv, inline)
            dispatch = "CHILD_RETURNED" if code is not None else "LAUNCH_FAILED"
        end = time.monotonic_ns()
        common.update(exit_code=code, capture_errors=errors,
                      start_monotonic_ns=start, end_monotonic_ns=end)
        receipt = dict(common, dispatch=dispatch, stdout_base64=base64.b64encode(stdout).decode("ascii"),
                       stderr_base64=base64.b64encode(stderr).decode("ascii"))
        raw_receipt = canonical(receipt)
        # No product/source/output read, including CAS deduplication, precedes
        # this durable write after capture_process returns the actual outcome.
        write_new(directory / "processes" / f"{len(paths):02d}.json", raw_receipt, sync_parent=True)
        try:
            item = dict(common, stdout=put_blob(directory, stdout), stderr=put_blob(directory, stderr),
                        inputs_before=before_inputs,
                        inputs_after=[observe(directory, Path(path)) for path in spec["inputs"]],
                        outputs_before=before_outputs,
                        outputs_after=[observe(directory, Path(path)) for path in spec["outputs"]],
                        source_before=before_source, source_after=source_now(directory, session),
                        clone_before=before_clone, clone_after=clone_observation(directory, session, spec["lane"]),
                        executable_before=before_executable, executable_after=executable(directory, argv),
                        generation_id=event_id + ":outputs" if code == 0 and spec["outputs"] else None)
            write_new(directory / "events" / f"{len(paths):02d}.json", canonical(item))
        except (OSError, ReproCaptureError) as exc:
            failure = dict(schema=SCHEMA, profile=PROFILE, run_id=session["run_id"], index=len(paths),
                           event_id=event_id, process_sha256=digest(raw_receipt),
                           error="POST_ACQUISITION_HANDOFF_FAILED",
                           error_type="OSError" if isinstance(exc, OSError) else "ReproCaptureError",
                           errno=exc.errno if isinstance(exc, OSError) else None)
            write_new(directory / "processes" / f"{len(paths):02d}.handoff.json", canonical(failure), sync_parent=True)
            return 125
        if code is None or errors:
            return 125
        # Preserve the actual child exit in the event. Shell signal convention is
        # only the wrapper's process return; it never replaces that integer.
        return code if code >= 0 else 128 - code
    finally:
        lock.rmdir()


def release_directory(item):
    return (item["kind"] == "DIRECTORY" and
            [Path(row["path"]).name for row in item["members"]] == sorted(MEMBERS) and
            all(row["kind"] == "FILE" for row in item["members"]))


def manifest_result_matches(reader, archive, stdout):
    """Imported result consistency against the original finite ZIP oracle.

    This does not replay an invocation or authenticate a retained event. The
    independent byte-derived check refuses a resealed but contradictory result.
    """
    if archive["kind"] != "FILE":
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(reader.blob(archive["blob"]))) as opened:
            infos = opened.infolist()
            names = opened.namelist()
            if (len(infos) > 4096 or names != sorted(set(names)) or
                    sum(info.file_size for info in infos) > MAX_TOTAL):
                return False
            manifest = []
            for info in infos:
                path = PurePosixPath(info.filename)
                mode = (info.external_attr >> 16) & 0o777
                wanted_mode = 0o755 if info.filename.startswith("scripts/") or "/scripts/" in info.filename else 0o644
                if ("\\" in info.filename or path.is_absolute() or ".." in path.parts or
                        info.date_time != (1980, 1, 1, 0, 0, 0) or info.create_system != 3 or
                        info.compress_type != zipfile.ZIP_DEFLATED or info.extra or info.comment or
                        mode != wanted_mode or info.file_size > MAX_FILE):
                    return False
                data = opened.read(info.filename)
                manifest.append(dict(path=info.filename, sha256=digest(data), size=len(data), mode=oct(mode),
                                     compression=info.compress_type, timestamp=info.date_time, creator=info.create_system))
        return stdout == canonical(manifest)
    except (OSError, RuntimeError, ValueError, zipfile.BadZipFile):
        return False


def validate_clone(reader, session, item, lane, issues, label):
    if lane is None:
        demand(item is None, "unexpected clone observation")
        return
    fields(item, "head tree status scripts", "clone")
    if item["head"] is None:
        demand(item == dict(head=None, tree=None, status=None, scripts={}), "invalid missing clone")
        issues.append(label + ":CLONE_UNAVAILABLE")
        return
    if item["head"] != session["source"]["source_commit"] or item["tree"] != session["source"]["source_tree"]:
        issues.append(label + ":CLONE_SOURCE_DRIFT")
    if reader.blob(item["status"]) != b"":
        issues.append(label + ":CLONE_DIRTY")
    fields(item["scripts"], "build checksum", "clone scripts")
    for name, wanted in session["source_scripts"].items():
        actual = item["scripts"][name]
        path = Path(session["context"]["work_root"]) / ("checkout-" + lane) / wanted["path"]
        observation(reader, actual, path)
        if actual["kind"] != "FILE" or actual.get("blob") != wanted["blob"] or actual["stat"]["mode"] != wanted["mode"]:
            issues.append(label + ":CLONE_SCRIPT_DRIFT:" + name)


def assess_events(reader, session, events):
    expected = profile(session)
    demand(len(events) <= len(expected), "extra event")
    issues, generations = [], {}
    last_end = 0
    failed = False
    for index, item in enumerate(events):
        spec = expected[index]
        fields(item, EVENT_FIELDS, "event")
        event_id = session["run_id"] + ":" + f"{index:02d}" + ":" + spec["role"]
        last_end = invocation(reader, session, item, spec, index, last_end)
        stdout, stderr = reader.blob(item["stdout"]), reader.blob(item["stderr"])
        demand(len(stdout) <= MAX_STREAM and len(stderr) <= MAX_STREAM, "raw stream exceeds bound")
        code = item["exit_code"]
        if failed:
            issues.append(spec["role"] + ":EVENT_AFTER_FAILURE")
        if code != 0 or item["capture_errors"]:
            issues.append(spec["role"] + ":CHILD_OR_CAPTURE_FAILED")
            failed = True
        for field, paths in (("inputs_before", spec["inputs"]), ("inputs_after", spec["inputs"]),
                             ("outputs_before", spec["outputs"]), ("outputs_after", spec["outputs"])):
            values = item[field]
            demand(type(values) is list and len(values) == len(paths), "omitted event artifact observation")
            for value, path in zip(values, paths):
                observation(reader, value, path)
        for when in ("before", "after"):
            observed = item["source_" + when]
            fields(observed, "producer capture_owner", "event source custody")
            for name, original in session["source_custody"].items():
                observation(reader, observed[name], original["path"])
            if observed != session["source_custody"]:
                issues.append(spec["role"] + ":SOURCE_CUSTODY_DRIFT:" + when)
            validate_clone(reader, session, item["clone_" + when], spec["lane"], issues, spec["role"] + ":" + when)
            executable_item = item["executable_" + when]
            if executable_item is not None:
                demand(type(executable_item) is dict and type(executable_item.get("path")) is str,
                       "invalid executable observation")
                observation(reader, executable_item, executable_item["path"])
        if item["executable_before"] is None or item["executable_before"] != item["executable_after"]:
            issues.append(spec["role"] + ":EXECUTABLE_CUSTODY_DRIFT")
        if item["inputs_before"] != item["inputs_after"]:
            issues.append(spec["role"] + ":INPUT_WINDOW_DRIFT")
        for before in item["inputs_before"]:
            if before != generations.get(before["path"]):
                issues.append(spec["role"] + ":INPUT_GENERATION_DRIFT:" + before["path"])
        if spec["outputs"]:
            wanted_id = event_id + ":outputs" if code == 0 else None
            demand(item["generation_id"] == wanted_id, "failed child relabeled as new generation")
            for before, after in zip(item["outputs_before"], item["outputs_after"]):
                if spec["role"].startswith("build:"):
                    if before["kind"] != "MISSING" or not release_directory(after):
                        issues.append(spec["role"] + ":INCOMPLETE_NEW_RELEASE_NAMESPACE")
                elif (before["kind"] != "FILE" or before["blob"]["bytes"] != 0 or
                      after["kind"] != "FILE" or after["blob"] != item["stdout"]):
                    issues.append(spec["role"] + ":MANIFEST_OUTPUT_HANDOFF_MISMATCH")
                if code == 0:
                    generations[after["path"]] = after
                    if after["kind"] == "DIRECTORY":
                        generations.update((member["path"], member) for member in after["members"])
        else:
            demand(item["generation_id"] is None, "consumer invented a generation")
        if code == 0 and (spec["role"].startswith("cmp:") or spec["role"].startswith("manifest-cmp:")):
            inputs = item["inputs_before"]
            if (len(inputs) != 2 or any(value["kind"] != "FILE" for value in inputs)
                    or inputs[0].get("blob") != inputs[1].get("blob") or stdout or stderr):
                issues.append(spec["role"] + ":CMP_RESULT_OPERAND_MISMATCH")
        if code == 0 and spec["role"].startswith("hash:"):
            operand = item["inputs_before"][0]
            if operand["kind"] != "FILE" or stdout != (operand["blob"]["sha256"] + "\n").encode() or stderr:
                issues.append(spec["role"] + ":HASH_RESULT_OPERAND_MISMATCH")
        if code == 0 and spec["role"].startswith("checksum:"):
            namespace = item["inputs_before"][0]
            consistent = release_directory(namespace)
            if consistent:
                members = {Path(row["path"]).name: row for row in namespace["members"]}
                wanted = "".join("sha256  " + members[name]["blob"]["sha256"] + "  " + name + "\n"
                                 for name in sorted(MEMBERS[:2])).encode()
                consistent = reader.blob(members["CHECKSUMS.txt"]["blob"]) == wanted
            if not consistent or stdout != b"write-release-checksums: check ok IMPLEMENTAUDIT.plugin.zip, IMPLEMENTAUDIT.skill\n" or stderr:
                issues.append(spec["role"] + ":CHECKSUM_RESULT_OPERAND_MISMATCH")
        if code == 0 and spec["role"].startswith("manifest:"):
            if not manifest_result_matches(reader, item["inputs_before"][0], stdout) or stderr:
                issues.append(spec["role"] + ":MANIFEST_RESULT_OPERAND_MISMATCH")
    if len(events) != len(expected):
        issues.append("INCOMPLETE_FINITE_PROFILE")
    return issues, generations


def close(directory, script_exit):
    directory = no_alias(Path(directory))
    reader = Readback(directory)
    session = load_session(directory, reader)
    events = [json_read(path) for path in event_files(directory)]
    _, generations = assess_events(reader, session, events)
    observations = [observe(directory, Path(path)) for path in sorted(generations)]
    data = dict(schema=SCHEMA, run_id=session["run_id"], script_exit=script_exit,
                source=source_now(directory, session), generations=observations)
    write_new(directory / "close.json", canonical(data))


def read_events(directory, reader, session, refs=None):
    paths = event_files(directory)
    if refs is not None:
        demand(type(refs) is list and len(refs) == len(paths), "event reference omission")
    events, derived = [], []
    for index, path in enumerate(paths):
        data, _ = read_regular(path, MAX_JSON)
        descriptor = dict(path="events/" + path.name, bytes=len(data), sha256=digest(data))
        if refs is not None:
            demand(refs[index] == descriptor, "event reference mismatch")
        item = json_read(path)
        fields(item, EVENT_FIELDS, "event")
        events.append(item)
        derived.append(descriptor)
    return events, derived


def read_process_results(directory, reader, session, events, refs=None, failure_refs=None):
    """Bind durable own-child outcomes to the subsequently acquired events."""
    names = sorted(os.listdir(no_alias(directory / "processes")))
    result_names = [name for name in names if re.fullmatch(r"[0-9]{2}\.json", name)]
    failure_names = [name for name in names if re.fullmatch(r"[0-9]{2}\.handoff\.json", name)]
    expected = profile(session)
    demand(names == sorted(result_names + failure_names) and len(result_names) <= len(expected),
           "foreign process receipt member")
    demand(result_names == [f"{index:02d}.json" for index in range(len(result_names))],
           "missing or reordered process receipt")
    demand(len(result_names) in {len(events), len(events) + 1}, "process/event handoff omission")
    wanted_failures = [f"{len(events):02d}.handoff.json"] if len(result_names) > len(events) else []
    demand(failure_names == wanted_failures, "unmatched completed process or handoff failure")
    if refs is not None:
        demand(type(refs) is list and len(refs) == len(result_names), "process reference omission")
    if failure_refs is not None:
        demand(type(failure_refs) is list and len(failure_refs) == len(failure_names), "handoff failure reference omission")
    derived, failures, issues = [], [], []
    last_end = 0
    for index, name in enumerate(result_names):
        path = directory / "processes" / name
        raw, _ = read_regular(path, MAX_PROCESS_JSON)
        reader.process_bytes("processes/" + name, raw)
        descriptor = dict(path="processes/" + name, bytes=len(raw), sha256=digest(raw))
        if refs is not None:
            demand(refs[index] == descriptor, "process reference mismatch")
        derived.append(descriptor)
        item = json_read(path, MAX_PROCESS_JSON)
        fields(item, PROCESS_COMMON + " dispatch stdout_base64 stderr_base64", "process receipt")
        spec = expected[index]
        last_end = invocation(reader, session, item, spec, index, last_end)
        streams = {}
        for stream in ("stdout", "stderr"):
            encoded = item[stream + "_base64"]
            demand(type(encoded) is str and len(encoded) <= 4 * ((MAX_STREAM + 2) // 3),
                   "invalid raw process stream")
            try:
                data = base64.b64decode(encoded, validate=True)
            except (ValueError, binascii.Error) as exc:
                raise ReproCaptureError("invalid raw process stream encoding") from exc
            demand(len(data) <= MAX_STREAM and base64.b64encode(data).decode("ascii") == encoded,
                   "noncanonical or oversized raw process stream")
            streams[stream] = data
        code, dispatch, errors = item["exit_code"], item["dispatch"], item["capture_errors"]
        if dispatch == "CHILD_RETURNED":
            demand(integer(code), "completed process lacks actual integer exit")
            demand(not any(error.startswith(("UNSUPPORTED_INPUT_KIND:", "LAUNCH_FAILED:")) for error in errors),
                   "completed process has non-dispatch errors")
        elif dispatch == "NOT_STARTED_UNSUPPORTED_INPUT":
            demand(code is None and errors and all(error.startswith("UNSUPPORTED_INPUT_KIND:") for error in errors)
                   and not any(streams.values()), "invalid unsupported-input refusal")
        elif dispatch == "LAUNCH_FAILED":
            demand(code is None and len(errors) == 1 and re.fullmatch(r"LAUNCH_FAILED:[0-9]+", errors[0])
                   and not any(streams.values()), "invalid launch failure")
        else:
            raise ReproCaptureError("unknown process dispatch outcome")
        if index < len(events):
            event = events[index]
            demand(all(item[key] == event.get(key) for key in PROCESS_COMMON.split()),
                   "process result differs from event invocation or raw exit")
            for stream, data in streams.items():
                demand(reader.blob(event[stream]) == data, "process result differs from event raw stream")
            inputs = event["inputs_before"]
            demand(type(inputs) is list and len(inputs) == len(spec["inputs"]), "omitted process input observation")
            for value, operand in zip(inputs, spec["inputs"]):
                observation(reader, value, operand)
            refused = unsupported_inputs(spec, event["inputs_before"])
            demand((dispatch == "NOT_STARTED_UNSUPPORTED_INPUT" and errors == refused) or
                   (dispatch != "NOT_STARTED_UNSUPPORTED_INPUT" and not refused),
                   "unsupported input was dispatched or refusal is not derived")
        else:
            failure_path = directory / "processes" / failure_names[0]
            failure_raw, _ = read_regular(failure_path, MAX_JSON)
            reader.process_bytes("processes/" + failure_path.name, failure_raw)
            failure = json_read(failure_path)
            fields(failure, "schema profile run_id index event_id process_sha256 error error_type errno", "handoff failure")
            demand(failure["schema"] == SCHEMA and failure["profile"] == PROFILE and
                   failure["run_id"] == session["run_id"] and integer(failure["index"]) and
                   failure["index"] == index and failure["event_id"] == item["event_id"] and
                   failure["process_sha256"] == descriptor["sha256"] and
                   failure["error"] == "POST_ACQUISITION_HANDOFF_FAILED", "foreign handoff failure")
            demand(failure["error_type"] in {"OSError", "ReproCaptureError"} and
                   (failure["errno"] is None or integer(failure["errno"]) and 0 < failure["errno"] <= 4095),
                   "invalid handoff failure outcome")
            demand(failure["error_type"] != "ReproCaptureError" or failure["errno"] is None,
                   "capture error has a foreign OS error number")
            failure_descriptor = dict(path="processes/" + failure_path.name,
                                      bytes=len(failure_raw), sha256=digest(failure_raw))
            if failure_refs is not None:
                demand(failure_refs[0] == failure_descriptor, "handoff failure reference mismatch")
            failures.append(failure_descriptor)
            issues.append(spec["role"] + ":POST_ACQUISITION_HANDOFF_FAILED")
        if dispatch != "CHILD_RETURNED" or code != 0 or errors:
            issues.append(spec["role"] + ":PROCESS_RESULT_INCOMPLETE")
            demand(index == len(result_names) - 1, "process after failed child or unsupported-input refusal")
    if len(result_names) != len(expected):
        issues.append("INCOMPLETE_PROCESS_PROFILE")
    return derived, failures, issues


def unhanded_blobs(directory, reader, failures, refs=None):
    """Retain partial acquisitions without promoting them to event evidence."""
    names = sorted(os.listdir(no_alias(directory / "blobs")))
    demand(len(names) <= MAX_MEMBERS, "capture namespace exceeds bound")
    extra = sorted(set(names) - reader.used)
    demand(not extra or failures, "omitted or foreign retained artifact blob")
    derived = []
    for name in extra:
        demand(HEX.fullmatch(name), "foreign partial acquisition blob")
        data, _ = read_regular(directory / "blobs" / name)
        descriptor = dict(bytes=len(data), sha256=name)
        reader.blob(descriptor)
        derived.append(descriptor)
    if refs is not None:
        demand(type(refs) is list and refs == derived, "unhanded acquisition inventory mismatch")
    demand(names == sorted(reader.used), "omitted retained artifact blob")
    return derived


def assessment(directory, reader, session, events, closing, cleanup, process_issues):
    issues, generations = assess_events(reader, session, events)
    fields(closing, "schema run_id script_exit source generations", "close")
    demand(closing["schema"] == SCHEMA and closing["run_id"] == session["run_id"] and
           integer(closing["script_exit"]) and 0 <= closing["script_exit"] <= 255, "invalid close identity")
    fields(closing["source"], "producer capture_owner", "close source")
    for name, original in session["source_custody"].items():
        observation(reader, closing["source"][name], original["path"])
    if closing["source"] != session["source_custody"]:
        issues.append("FINAL_SOURCE_CUSTODY_DRIFT")
    demand(type(closing["generations"]) is list and len(closing["generations"]) == len(generations),
           "close generation omission")
    for item, path in zip(closing["generations"], sorted(generations)):
        observation(reader, item, path)
        if item != generations[path]:
            issues.append("FINAL_GENERATION_DRIFT:" + path)
    fields(cleanup, "exit_code work_root_absent", "cleanup")
    demand(integer(cleanup["exit_code"]) and 0 <= cleanup["exit_code"] <= 255 and
           type(cleanup["work_root_absent"]) is bool, "invalid cleanup outcome")
    if closing["script_exit"] != 0:
        issues.append("PRODUCER_EXIT_NONZERO")
    if cleanup != dict(exit_code=0, work_root_absent=True):
        issues.append("ORIGINAL_WORK_ROOT_CLEANUP_INCOMPLETE")
    issues.extend(process_issues)
    return dict(complete=not issues, issues=issues)


def finish(directory, cleanup_exit):
    directory = no_alias(Path(directory))
    reader = Readback(directory)
    session = load_session(directory, reader)
    events, refs = read_events(directory, reader, session)
    results, failures, process_issues = read_process_results(directory, reader, session, events)
    closing = json_read(directory / "close.json")
    work = Path(session["context"]["work_root"])
    cleanup = dict(exit_code=cleanup_exit, work_root_absent=not (work.exists() or work.is_symlink()))
    verdict = assessment(directory, reader, session, events, closing, cleanup, process_issues)
    partial = unhanded_blobs(directory, reader, failures)
    record = dict(schema=SCHEMA, profile=PROFILE, semantics=SEMANTICS,
                  session_sha256=digest(canonical(session)), close_sha256=digest(canonical(closing)),
                  run_id=session["run_id"], source=session["source"], events=refs,
                  process_results=results, handoff_failures=failures, unhanded_blobs=partial,
                  cleanup=cleanup, assessment=verdict)
    write_new(directory / "record.json", canonical(record))
    verify_record(directory, require_complete=False)
    return 0 if verdict["complete"] or closing["script_exit"] != 0 else 125


def verify_record(directory, *, expected_source=None, expected_run_id=None, require_complete=True):
    """Strict imported consistency readback; caller supplies its own bindings."""
    directory = no_alias(Path(directory))
    demand(sorted(os.listdir(directory)) == ["blobs", "close.json", "events", "processes", "record.json", "session.json"],
           "unexpected or incomplete capture namespace")
    reader = Readback(directory)
    session = load_session(directory, reader)
    record = json_read(directory / "record.json")
    fields(record, "schema profile semantics session_sha256 close_sha256 run_id source events process_results "
           "handoff_failures unhanded_blobs cleanup assessment", "record")
    demand(record["schema"] == SCHEMA and record["profile"] == PROFILE and record["semantics"] == SEMANTICS and
           record["run_id"] == session["run_id"] and record["source"] == session["source"] and
           record["session_sha256"] == digest(canonical(session)), "envelope identity mismatch")
    if expected_source is not None:
        demand(type(expected_source) is dict and bool(expected_source) and
               set(expected_source) <= set(session["source"]), "invalid expected source binding")
        demand(all(session["source"][key] == value for key, value in expected_source.items()),
               "expected source binding mismatch")
    if expected_run_id is not None:
        demand(expected_run_id == session["run_id"], "expected run binding mismatch")
    events, _ = read_events(directory, reader, session, record["events"])
    _, failures, process_issues = read_process_results(directory, reader, session, events,
                                                      record["process_results"], record["handoff_failures"])
    closing = json_read(directory / "close.json")
    demand(record["close_sha256"] == digest(canonical(closing)), "close identity mismatch")
    actual = assessment(directory, reader, session, events, closing, record["cleanup"], process_issues)
    fields(record["assessment"], "complete issues", "assessment")
    demand(type(record["assessment"]["complete"]) is bool, "invalid completion type")
    demand(record["assessment"] == actual, "declared completion differs from derived finite profile")
    unhanded_blobs(directory, reader, failures, record["unhanded_blobs"])
    if require_complete:
        demand(actual["complete"], "incomplete C5 custody: " + "; ".join(actual["issues"]))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("init")
    start.add_argument("directory")
    start.add_argument("repository")
    start.add_argument("work_root")
    start.add_argument("source_commit")
    start.add_argument("python_command")
    invoke = commands.add_parser("event")
    invoke.add_argument("directory")
    invoke.add_argument("role")
    invoke.add_argument("argv", nargs=argparse.REMAINDER)
    end = commands.add_parser("close")
    end.add_argument("directory")
    end.add_argument("script_exit", type=int)
    final = commands.add_parser("finish")
    final.add_argument("directory")
    final.add_argument("cleanup_exit", type=int)
    check = commands.add_parser("verify")
    check.add_argument("directory")
    check.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "init":
            init(Path(args.directory), args.repository, args.work_root, args.source_commit, args.python_command)
            return 0
        if args.command == "event":
            argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
            return event(Path(args.directory), args.role, argv)
        if args.command == "close":
            close(Path(args.directory), args.script_exit)
            return 0
        if args.command == "finish":
            return finish(Path(args.directory), args.cleanup_exit)
        result = verify_record(Path(args.directory), require_complete=not args.allow_partial)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ReproCaptureError, OSError, KeyError, TypeError) as exc:
        print("repro-event-capture: " + str(exc), file=sys.stderr)
        return 125


if __name__ == "__main__":
    raise SystemExit(main())
