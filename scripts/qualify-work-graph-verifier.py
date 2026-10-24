#!/usr/bin/env python3
"""Capture an optional legacy/DAG verifier run without changing its registry.

This transport imports the single graph compiler. It does not own a second
registry, choose parallel tests, supply release authority, or install anything.
"""
import argparse
import copy
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import stat
import struct
import subprocess
import sys
import tempfile
import time
try:
    import fcntl
    import resource
except ImportError:
    fcntl = resource = None

ROOT = Path(__file__).resolve().parents[1]
LOADED_DRIVER_PATH = Path(__file__).resolve()
LOADED_DRIVER = LOADED_DRIVER_PATH.read_bytes()
SPEC = importlib.util.spec_from_file_location("work_graph", ROOT / "skills/implementaudit/scripts/compile-work-graph.py")
WG = importlib.util.module_from_spec(SPEC)
LOADED_COMPILER = Path(SPEC.origin).read_bytes()
LOADED_COMPILER_PATH = Path(SPEC.origin).resolve()
exec(compile(LOADED_COMPILER, SPEC.origin, "exec"), WG.__dict__)
REPRO_PRODUCER = "tests/reproducible-release-asset.test.sh"
REPRO_PRODUCER_SHA256 = "7c892c5e84a29bd33d6ed03c97a5610efde51b0d1ad0165f9e9ded0a3bdfb3ad"
REPRO_EVENT_PRODUCER_SHA256 = "a27521758cc71e312052d7eaa7c8b488dbbe2dcc5089d6054be0923455763310"
# Keep the original historical v3 producer. The additive profile has actual
# capture-off raw-stream/exit/export equivalence at the same build source.
REPRO_PRODUCER_PROFILES = {REPRO_PRODUCER_SHA256: 11460, REPRO_EVENT_PRODUCER_SHA256: 12799}
REPRO_FILES = dict(ASSET_A="IMPLEMENTAUDIT-A.skill", ASSET_B="IMPLEMENTAUDIT-B.skill",
                   PLUGIN_A="IMPLEMENTAUDIT-A.plugin.zip", PLUGIN_B="IMPLEMENTAUDIT-B.plugin.zip",
                   CHECKSUMS_A="CHECKSUMS-A.txt", CHECKSUMS_B="CHECKSUMS-B.txt")
EXPLICIT_FILE_LIMIT = 16 * 1024 * 1024
DIST_LIMITS = dict(file_bytes=EXPLICIT_FILE_LIMIT, total_bytes=64 * 1024 * 1024, entries=4096, depth=32)
PORTAL_ENV = "IMPLEMENTAUDIT_PORTAL_CAPTURE"
_PORTAL_ENGINE = None
REPRO_EVENT_ENV = "R0035_REPRO_EVENT_CAPTURE_DIR"
REPRO_EVENT_OWNER = "scripts/repro-event-capture.py"
_REPRO_EVENT_ENGINE = None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stream_sha(stream):
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def _file_identity(metadata):
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns)


def require_source_descriptor_api():
    if (not all(hasattr(os, flag) for flag in ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")) or
            not all(call in os.supports_dir_fd for call in (os.open, os.stat, os.readlink)) or
            os.stat not in os.supports_follow_symlinks):
        raise WG.WorkGraphError("full verifier source observation requires no-follow directory descriptors")


def source_member(name, *, root=None, with_bytes=False, byte_limit=None):
    """Observe declared Git members without following source symlink targets."""
    path = Path(name)
    if path.is_absolute() or not path.parts or any(p in {"", ".", ".."} for p in path.parts):
        raise WG.WorkGraphError("unsupported Git member path")
    require_source_descriptor_api()
    directory = os.open(ROOT if root is None else root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    directories = [(directory, stat.S_IMODE(os.fstat(directory).st_mode))]
    result = dict(ancestor_modes={".": directories[0][1]})
    try:
        for index, component in enumerate(path.parts[:-1]):
            try:
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=directory)
            except OSError as exc:
                if exc.errno not in {errno.ENOENT, errno.ENOTDIR, errno.ELOOP, errno.EACCES}:
                    raise
                return dict(result, kind="UNACQUIRED", reason="MISSING_OR_UNSUPPORTED_ANCESTOR")
            directory = child
            mode = stat.S_IMODE(os.fstat(directory).st_mode)
            directories.append((directory, mode))
            result["ancestor_modes"]["/".join(path.parts[:index + 1])] = mode
        try:
            before = os.stat(path.name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            return dict(result, kind="MISSING")
        result["mode"] = stat.S_IMODE(before.st_mode)
        if stat.S_ISLNK(before.st_mode):
            result.update(kind="SYMLINK", target_sha256=sha(os.fsencode(
                os.readlink(path.name, dir_fd=directory))), content="TARGET_NOT_FOLLOWED")
        elif stat.S_ISREG(before.st_mode):
            fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
            try:
                opened = os.fstat(fd)
                if not stat.S_ISREG(opened.st_mode) or _file_identity(before) != _file_identity(opened):
                    raise WG.WorkGraphError("source member changed during observation")
                if byte_limit is not None and opened.st_size > byte_limit:
                    raise WG.WorkGraphError("explicit member exceeds byte limit")
                with os.fdopen(fd, "rb", closefd=False) as stream:
                    if with_bytes:
                        result["_acquired_bytes"] = stream.read() if byte_limit is None else stream.read(byte_limit + 1)
                        if byte_limit is not None and len(result["_acquired_bytes"]) > byte_limit:
                            raise WG.WorkGraphError("explicit member exceeds byte limit")
                        digest = sha(result["_acquired_bytes"])
                    else:
                        digest = stream_sha(stream)
                if _file_identity(opened) != _file_identity(os.fstat(fd)):
                    raise WG.WorkGraphError("source member changed during observation")
                result.update(kind="FILE", bytes=opened.st_size, sha256=digest)
            finally:
                os.close(fd)
        elif stat.S_ISDIR(before.st_mode):
            result.update(kind="DIRECTORY", content="MEMBERSHIP_NOT_RECURSIVELY_ACQUIRED")
        else:
            result.update(kind="UNACQUIRED", reason="NONREGULAR_MEMBER")
        if _file_identity(before) != _file_identity(os.stat(path.name, dir_fd=directory, follow_symlinks=False)):
            raise WG.WorkGraphError("source member changed during observation")
        return result
    finally:
        changed = any(stat.S_IMODE(os.fstat(fd).st_mode) != mode for fd, mode in directories)
        for fd, _ in directories:
            os.close(fd)
        if changed:
            raise WG.WorkGraphError("source ancestor mode changed during observation")


def source_identity(*, read_only=False):
    require_source_descriptor_api()
    observation = _preflight_git_context_v1() if read_only else None
    def git(*args):
        if read_only:
            return _preflight_git_capture_v1(observation, args)
        return subprocess.check_output(["git", *args], cwd=ROOT)
    stage = git("ls-files", "--stage", "-z") if read_only else None
    if read_only and any(entry.split(b" ", 1)[0] not in {b"100644", b"100755", b"120000"}
                         for entry in stage.split(b"\0") if entry):
        raise WG.WorkGraphError("preflight Git observation refuses gitlinks or unsupported index modes")
    names = sorted(set(filter(None, git("ls-files", "-z").split(b"\0"))))
    untracked = sorted(set(filter(None, git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0"))))
    members = {}
    for raw in sorted(set(names) | set(untracked)):
        name = os.fsdecode(raw)
        members[name] = dict(tracked=raw in names, **source_member(name))
    files = [[os.fsdecode(raw), members[os.fsdecode(raw)].get("sha256",
              members[os.fsdecode(raw)].get("target_sha256", sha(b"MISSING")))] for raw in names]
    refs = git("for-each-ref", "--sort=refname",
               "--format=%(refname)%00%(objectname)%00%(*objectname)%00%(symref)")
    result = dict(head=git("rev-parse", "HEAD").decode().strip(), tree=git("rev-parse", "HEAD^{tree}").decode().strip(),
                head_reference=git("rev-parse", "--symbolic-full-name", "HEAD").decode().strip(),
                tracked_source_digest=sha(WG.canonical_json_v1(files)),
                status_digest=sha(git("status", "--porcelain=v1", "-z", "--untracked-files=all")),
                index_sha256=sha(stage if read_only else git("ls-files", "--stage", "-z")),
                git_refs=[os.fsdecode(line).split("\0") for line in refs.splitlines()],
                members=members,
                acquisition_coverage="PARTIAL_GIT_DECLARED_MEMBERS_NO_SYMLINK_DEREFERENCE; IGNORED_NAMESPACE_UNACQUIRED")
    if read_only:
        if _preflight_git_context_v1() != observation:
            raise WG.WorkGraphError("preflight Git observation context changed")
        result["_git_observation_sha256"] = sha(WG.canonical_json_v1(observation["binding"]))
    return result


def executable_identity(path):
    if path is None:
        return dict(available=False)
    if not all(hasattr(os, flag) for flag in ("O_NOFOLLOW", "O_NONBLOCK")):
        raise WG.WorkGraphError("full verifier executable observation requires a safe nonblocking open")
    resolved = Path(path).resolve(strict=True)
    fd = os.open(resolved, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise WG.WorkGraphError("unsupported executable member")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            digest = stream_sha(stream)
        if _file_identity(before) != _file_identity(os.fstat(fd)):
            raise WG.WorkGraphError("executable changed during observation")
    finally:
        os.close(fd)
    if _file_identity(before) != _file_identity(resolved.lstat()):
        raise WG.WorkGraphError("executable changed during observation")
    return dict(available=True, selected_path=str(path), resolved_path=str(resolved),
                mode=stat.S_IMODE(before.st_mode), bytes=before.st_size, sha256=digest)


def environment_identity(environment=None, *, child_resolution=False):
    # Digest all inherited values without retaining them. Only the established
    # safe projection and the two explicit CI branch/config inputs are printed.
    supplied = environment
    environment = os.environ if environment is None else environment
    inherited = b"\0".join(os.fsencode(k) + b"=" + os.fsencode(v)
                           for k, v in sorted(environment.items()))
    umask = None
    if platform.system() == "Linux":
        try:
            with Path("/proc/self/status").open() as stream:
                for line in stream:
                    if line.startswith("Umask:"):
                        umask = int(line.split()[1], 8)
                        break
        except OSError:
            pass
    identity = {name: getattr(os, name)() for name in ("getuid", "geteuid", "getgid", "getegid", "getgroups")
                if hasattr(os, name)}
    limits = None if resource is None else {
        name: list(resource.getrlimit(getattr(resource, name)))
        for name in dir(resource) if name.startswith("RLIMIT_")}
    names = ("bash", "git", "node", "npx") + (("python", "python3", "py") if child_resolution else ())
    lookup_path = environment.get("PATH", os.defpath)
    if child_resolution:
        # execvp resolves relative and empty PATH entries after the child's
        # chdir. Observe that context without changing the observer's cwd.
        lookup_path = os.pathsep.join(str(Path(part) if Path(part).is_absolute() else ROOT / part)
                                      for part in lookup_path.split(os.pathsep))
    executables = {"observer_python": executable_identity(sys.executable),
                   **{name: executable_identity(shutil.which(name, path=lookup_path)) for name in names}}
    options = {} if supplied is None else dict(env=supplied)
    if child_resolution:
        options["cwd"] = ROOT
    result = dict(platform=platform.platform(), python=sys.version, python_executable=sys.executable,
                bash=subprocess.check_output(["bash", "--version"], **options).decode().splitlines()[0],
                git=subprocess.check_output(["git", "--version"], **options).decode().strip(),
                selected_environment={k: environment.get(k) for k in
                    ("PATH", "LANG", "LC_ALL", "TZ", "PYTHONDONTWRITEBYTECODE", "GITHUB_BASE_REF", "GITHUB_ACTIONS")},
                inherited_environment_sha256=sha(inherited),
                executables=executables,
                process_identity=identity, inherited_resource_limits=limits, umask=umask,
                acquisition_coverage="PARTIAL_NOT_TOOLCHAIN_CLOSURE")
    if child_resolution:
        selected = next((name for name in ("python", "python3", "py") if executables[name]["available"]), None)
        result["child_python_resolution"] = dict(
            external_fallback_argv=None if selected is None else [selected] + (["-3"] if selected == "py" else []),
            coverage="PARTIAL_EXTERNAL_PATH_RESOLUTION_ONLY",
            startup_functions_aliases="UNQUALIFIED", launcher_interpreter="UNQUALIFIED")
    return result


def environment_digest(environment):
    return sha(b"\0".join(os.fsencode(k) + b"=" + os.fsencode(v) for k, v in sorted(environment.items())))


def durable_bytes(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def retained_bytes(directory, name):
    observed = source_member(name, root=directory, with_bytes=True, byte_limit=EXPLICIT_FILE_LIMIT)
    if observed.get("kind") != "FILE":
        raise WG.WorkGraphError("missing or unsupported retained input: " + name)
    return observed.pop("_acquired_bytes"), observed


def repro_overrides(original_output):
    return {"REPRO_RETAINED_" + role: original_output + "/repro-assets/" + name
            for role, name in REPRO_FILES.items()}


def repro_binding(mapping, source):
    node_id = "COMMAND:" + REPRO_PRODUCER + ":0"
    nodes = [n for n in mapping["nodes"] if n["id"] == node_id]
    member = source.get("members", {}).get(REPRO_PRODUCER)
    if (len(nodes) != 1 or nodes[0]["kind"] != "TEST" or
            nodes[0]["command"] != REPRO_PRODUCER or nodes[0]["source"].strip() != "bash " + REPRO_PRODUCER or
            type(member) is not dict or member.get("kind") != "FILE" or member.get("tracked") is not True or
            type(member.get("sha256")) is not str or member["sha256"] not in REPRO_PRODUCER_PROFILES or type(member.get("bytes")) is not int or
            member["bytes"] != REPRO_PRODUCER_PROFILES[member["sha256"]] or type(member.get("mode")) is not int or
            any(type(source.get(k)) is not str or not re.fullmatch(r"[0-9a-f]{40}", source[k]) for k in ("head", "tree"))):
        raise WG.WorkGraphError("repro retention requires the pinned registered zero-argument producer")
    node = nodes[0]
    return dict(path=REPRO_PRODUCER, sha256=member["sha256"], bytes=member["bytes"],
                node=node_id, source=node["source"], source_sha256=node["source_sha256"],
                source_ref="HEAD", source_commit=source["head"], source_tree=source["tree"])


def observe_repro_artifacts(directory, original_output, mapping, before, after, code):
    producer = repro_binding(mapping, before)
    if repro_binding(mapping, after) != producer:
        raise WG.WorkGraphError("repro producer source/currentness changed")
    parent = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fd = os.open("repro-assets", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            metadata = os.fstat(fd)
            members = sorted(os.listdir(fd))
            if _file_identity(metadata) != _file_identity(os.fstat(fd)):
                raise WG.WorkGraphError("repro artifact membership changed during observation")
        finally:
            os.close(fd)
    finally:
        os.close(parent)
    if set(members) - set(REPRO_FILES.values()):
        raise WG.WorkGraphError("foreign repro artifact population")
    files = {}
    for role, name in REPRO_FILES.items():
        relative = "repro-assets/" + name
        files[role] = dict(relative_path=relative, path=original_output + "/" + relative,
                           observation=source_member(relative, root=directory, byte_limit=EXPLICIT_FILE_LIMIT))
    complete = all(v["observation"]["kind"] == "FILE" for v in files.values())
    current = WG.canonical_json_v1(before) == WG.canonical_json_v1(after)
    return dict(scope="DECLARED_REPRO_RELEASE_SET_V1", producer=producer, files=files,
                members=members, complete=complete, source_current=current,
                coverage="COMPLETE_DECLARED_FILES_FROM_SUCCESSFUL_PROCESS" if complete and current and code == 0
                         else "UNQUALIFIED_INCOMPLETE_OR_FAILED_PROCESS")


def acquire_stdin(output, declared_path, empty):
    if declared_path is not None:
        path = Path(declared_path)
        path = path if path.is_absolute() else ROOT / path
        observed = source_member(path.relative_to("/").as_posix(), root=Path("/"), with_bytes=True,
                                 byte_limit=EXPLICIT_FILE_LIMIT)
        if observed.get("kind") != "FILE":
            raise WG.WorkGraphError("stdin requires a no-follow regular file")
        data = observed.pop("_acquired_bytes")
    else:
        data, observed = b"", None
    record = dict(schema="implementaudit.verifier-stdin.v1", mode="EMPTY_PIPE" if empty else "RETAINED_FILE_PIPE",
                  declared_path=declared_path, declaration_cwd=str(ROOT), source_observation=observed,
                  bytes=len(data), sha256=sha(data), retained_mode=0o600)
    durable_bytes(output / "stdin.bin", data)
    durable_bytes(output / "stdin.json", WG.canonical_json_v1(record) + b"\n")
    return record, data


def dist_inventory(root, *, snapshot=None, retained=False):
    """Acquire only fixed dist/, preserving ordinary bytes and directory modes.

    Descriptor checks bound each observation, not concurrent event history.
    The same walker rederives the complete retained snapshot at consumption.
    """
    require_source_descriptor_api()
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    root_mode = stat.S_IMODE(os.fstat(root_fd).st_mode)
    entries, total = {}, 0
    if snapshot is not None:
        snapshot.mkdir(mode=0o700)

    def names_at(fd, limit):
        names = []
        scan_fd = os.open(".", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
        try:
            with os.scandir(scan_fd) as scan:
                for entry in scan:
                    if len(names) >= limit:
                        raise WG.WorkGraphError("dist namespace exceeds entry limit")
                    names.append(entry.name)
        finally:
            os.close(scan_fd)
        return sorted(names)

    def walk(parent, name, relative, depth):
        nonlocal total
        if depth > DIST_LIMITS["depth"] or len(entries) >= DIST_LIMITS["entries"]:
            raise WG.WorkGraphError("dist namespace exceeds depth or entry limit")
        try:
            before = os.stat(name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            if relative != "dist":
                raise WG.WorkGraphError("dist member disappeared during observation")
            entries[relative] = dict(kind="MISSING")
            return
        if not (stat.S_ISDIR(before.st_mode) or stat.S_ISREG(before.st_mode)):
            raise WG.WorkGraphError("dist requires ordinary directories and regular files without symlinks")
        if relative == "dist" and not stat.S_ISDIR(before.st_mode):
            raise WG.WorkGraphError("dist root must be an ordinary directory or missing")
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        if stat.S_ISDIR(before.st_mode):
            flags |= os.O_DIRECTORY
        fd = os.open(name, flags, dir_fd=parent)
        try:
            opened = os.fstat(fd)
            if _file_identity(before) != _file_identity(opened):
                raise WG.WorkGraphError("dist member changed during observation")
            mode = stat.S_IMODE(opened.st_mode)
            target = None if snapshot is None else snapshot / relative
            if stat.S_ISDIR(opened.st_mode):
                members = names_at(fd, DIST_LIMITS["entries"] - len(entries))
                if len(members) + len(entries) > DIST_LIMITS["entries"]:
                    raise WG.WorkGraphError("dist namespace exceeds entry limit")
                entries[relative] = dict(kind="DIRECTORY", mode=mode, members=members)
                if target is not None:
                    target.mkdir(mode=0o700)
                for member in members:
                    walk(fd, member, relative + "/" + member, depth + 1)
                if names_at(fd, len(members) + 1) != members:
                    raise WG.WorkGraphError("dist membership changed during observation")
                if target is not None:
                    target.chmod(mode)
            else:
                total += opened.st_size
                if opened.st_size > DIST_LIMITS["file_bytes"] or total > DIST_LIMITS["total_bytes"]:
                    raise WG.WorkGraphError("dist namespace exceeds byte limit")
                with os.fdopen(fd, "rb", closefd=False) as stream:
                    data = stream.read(DIST_LIMITS["file_bytes"] + 1)
                if len(data) != opened.st_size:
                    raise WG.WorkGraphError("dist file changed during observation")
                entries[relative] = dict(kind="FILE", mode=mode, bytes=len(data), sha256=sha(data))
                if target is not None:
                    durable_bytes(target, data)
                    target.chmod(mode)
            if (_file_identity(opened) != _file_identity(os.fstat(fd)) or
                    _file_identity(before) != _file_identity(os.stat(name, dir_fd=parent, follow_symlinks=False))):
                raise WG.WorkGraphError("dist member changed during observation")
        finally:
            os.close(fd)

    try:
        walk(root_fd, "dist", "dist", 1)
        if entries["dist"]["kind"] == "MISSING":
            try:
                os.stat("dist", dir_fd=root_fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise WG.WorkGraphError("dist appeared during missing observation")
        if retained and names_at(root_fd, 2) != ([] if entries["dist"]["kind"] == "MISSING" else ["dist"]):
            raise WG.WorkGraphError("foreign retained dist snapshot population")
        if stat.S_IMODE(os.fstat(root_fd).st_mode) != root_mode:
            raise WG.WorkGraphError("dist source root mode changed during observation")
    finally:
        os.close(root_fd)
    if snapshot is not None:
        snapshot.chmod(root_mode)
    return dict(root_mode=root_mode, entries=entries)


def dist_binding(output, before, after):
    return dict(schema="implementaudit.verifier-dist.v1", source_path=str(ROOT / "dist"),
                before_path=str(output / "dist-before"), after_path=str(output / "dist-after"),
                before=before, after=after, limits=DIST_LIMITS,
                coverage="FINITE_DIST_PRE_POST_SNAPSHOTS_NO_EVENT_CUSTODY")


def validate_child_resolution(environment):
    names = {"observer_python", "bash", "git", "node", "npx", "python", "python3", "py"}
    executables = environment.get("executables")
    if type(executables) is not dict or set(executables) != names:
        raise WG.WorkGraphError("missing v3 external executable population")
    for value in executables.values():
        if type(value) is not dict or type(value.get("available")) is not bool:
            raise WG.WorkGraphError("invalid v3 executable observation")
        if not value["available"]:
            if value != {"available": False}:
                raise WG.WorkGraphError("invalid unavailable executable")
        elif (set(value) != {"available", "selected_path", "resolved_path", "mode", "bytes", "sha256"} or
              any(type(value[k]) is not str or not Path(value[k]).is_absolute() for k in ("selected_path", "resolved_path")) or
              type(value["mode"]) is not int or not 0 <= value["mode"] <= 0o7777 or
              type(value["bytes"]) is not int or value["bytes"] < 0 or
              type(value["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", value["sha256"])):
            raise WG.WorkGraphError("invalid acquired executable binding")
    selected = next((n for n in ("python", "python3", "py") if executables[n]["available"]), None)
    expected = dict(external_fallback_argv=None if selected is None else [selected] + (["-3"] if selected == "py" else []),
                    coverage="PARTIAL_EXTERNAL_PATH_RESOLUTION_ONLY", startup_functions_aliases="UNQUALIFIED",
                    launcher_interpreter="UNQUALIFIED")
    if environment.get("child_python_resolution") != expected:
        raise WG.WorkGraphError("inconsistent external Python resolution projection")


def verify_extended_record(directory, result, mapping):
    context = result["execution_context"]
    if (all(result[key] is None for key in ("repro_artifacts", "stdin", "dist_namespace"))
            and result.get("portal_events") is None and result.get("repro_events") is None):
        raise WG.WorkGraphError("v3 requires an explicit acquisition contract")
    validate_child_resolution(result["environment"])
    validate_child_resolution(result["environment_after"])
    environment = result["child_environment"]
    fields = {"schema", "base_environment_sha256", "actual_environment_sha256", "overrides"}
    if (type(environment) is not dict or set(environment) != fields or
            environment["schema"] != "implementaudit.verifier-child-environment.v1" or
            any(type(environment[k]) is not str or not re.fullmatch(r"[0-9a-f]{64}", environment[k])
                for k in ("base_environment_sha256", "actual_environment_sha256")) or
            type(environment["overrides"]) is not dict or
            environment["actual_environment_sha256"] != result["environment"].get("inherited_environment_sha256")):
        raise WG.WorkGraphError("invalid actual child environment binding")
    expected_overrides = repro_overrides(context["output"]) if result["repro_artifacts"] is not None else {}
    if result.get("portal_events") is not None:
        expected_overrides[PORTAL_ENV] = context["output"] + "/portal-events/request.json"
    if result.get("repro_events") is not None:
        expected_overrides[REPRO_EVENT_ENV] = context["output"] + "/repro-events"
    if (WG.canonical_json_v1(environment["overrides"]) != WG.canonical_json_v1(expected_overrides) or
            (not expected_overrides and environment["base_environment_sha256"] != environment["actual_environment_sha256"]) or
            retained_bytes(directory, "child-environment.json")[0] != WG.canonical_json_v1(environment) + b"\n"):
        raise WG.WorkGraphError("inconsistent retained child environment")
    stdin = result["stdin"]
    if stdin is not None:
        fields = {"schema", "mode", "declared_path", "declaration_cwd", "source_observation", "bytes", "sha256", "retained_mode"}
        if (type(stdin) is not dict or set(stdin) != fields or stdin["schema"] != "implementaudit.verifier-stdin.v1" or
                type(stdin["mode"]) is not str or stdin["mode"] not in {"EMPTY_PIPE", "RETAINED_FILE_PIPE"} or
                stdin["declaration_cwd"] != context["cwd"] or type(stdin["bytes"]) is not int or stdin["bytes"] < 0 or
                type(stdin["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", stdin["sha256"]) or
                type(stdin["retained_mode"]) is not int or stdin["retained_mode"] != 0o600):
            raise WG.WorkGraphError("invalid retained stdin binding")
        if stdin["mode"] == "EMPTY_PIPE":
            if stdin["declared_path"] is not None or stdin["source_observation"] is not None or stdin["bytes"] != 0:
                raise WG.WorkGraphError("invalid empty stdin contract")
        else:
            observed = stdin["source_observation"]
            if (type(stdin["declared_path"]) is not str or not stdin["declared_path"] or
                    type(observed) is not dict or set(observed) != {"kind", "mode", "bytes", "sha256", "ancestor_modes"} or
                    observed["kind"] != "FILE" or type(observed["mode"]) is not int or not 0 <= observed["mode"] <= 0o7777 or
                    type(observed["ancestor_modes"]) is not dict or "." not in observed["ancestor_modes"] or
                    any(type(k) is not str or type(v) is not int or not 0 <= v <= 0o7777
                        for k, v in observed["ancestor_modes"].items()) or
                    observed.get("sha256") != stdin["sha256"] or type(observed.get("bytes")) is not int or
                    observed["bytes"] != stdin["bytes"]):
                raise WG.WorkGraphError("invalid acquired stdin source")
        data, observed = retained_bytes(directory, "stdin.bin")
        if (len(data) != stdin["bytes"] or sha(data) != stdin["sha256"] or observed["mode"] != stdin["retained_mode"] or
                retained_bytes(directory, "stdin.json")[0] != WG.canonical_json_v1(stdin) + b"\n"):
            raise WG.WorkGraphError("inconsistent retained stdin bytes or declaration")
    if result["repro_artifacts"] is not None:
        artifacts = observe_repro_artifacts(directory, context["output"], mapping, result["before"], result["after"], result["exit"])
        if (WG.canonical_json_v1(artifacts) != WG.canonical_json_v1(result["repro_artifacts"]) or
                retained_bytes(directory, "repro-artifacts.json")[0] != WG.canonical_json_v1(artifacts) + b"\n" or
                (result["exit"] == 0 and (not artifacts["complete"] or not artifacts["source_current"]))):
            raise WG.WorkGraphError("inconsistent or incomplete retained repro artifacts")
    namespace = result["dist_namespace"]
    if namespace is not None:
        expected = dict(schema="implementaudit.verifier-dist.v1", source_path=context["cwd"] + "/dist",
                        before_path=context["output"] + "/dist-before", after_path=context["output"] + "/dist-after",
                        before=dist_inventory(directory / "dist-before", retained=True),
                        after=dist_inventory(directory / "dist-after", retained=True), limits=DIST_LIMITS,
                        coverage="FINITE_DIST_PRE_POST_SNAPSHOTS_NO_EVENT_CUSTODY")
        if (WG.canonical_json_v1(namespace) != WG.canonical_json_v1(expected) or
                retained_bytes(directory, "dist-namespace.json")[0] != WG.canonical_json_v1(expected) + b"\n"):
            raise WG.WorkGraphError("inconsistent retained dist inventory, modes or bytes")
        # Imported context text never authorizes a filesystem read. Retained
        # bytes can be restored, but live currentness needs this actual source.
        if context["cwd"] != str(ROOT):
            raise WG.WorkGraphError("retained dist integrity valid; current source context unavailable")
        if dist_inventory(ROOT) != expected["after"]:
            raise WG.WorkGraphError("current dist namespace differs from retained after observation")


def portal_engine():
    """Load the one repo-only portal owner only for an explicit v4 operation."""
    global _PORTAL_ENGINE
    path = LOADED_DRIVER_PATH.with_name("portal-event-capture.py")
    observed = source_member(path.name, root=path.parent, with_bytes=True, byte_limit=EXPLICIT_FILE_LIMIT)
    if observed.get("kind") != "FILE":
        raise WG.WorkGraphError("portal capture helper is unavailable")
    data = observed.pop("_acquired_bytes")
    if _PORTAL_ENGINE is None:
        spec = importlib.util.spec_from_file_location("portal_event_capture", path)
        _PORTAL_ENGINE = importlib.util.module_from_spec(spec)
        _PORTAL_ENGINE._CAPTURE_SOURCE = data
        exec(compile(data, str(path), "exec"), _PORTAL_ENGINE.__dict__)
    if _PORTAL_ENGINE.LOADED_SOURCE != data:
        raise WG.WorkGraphError("loaded portal capture helper differs from current source")
    return _PORTAL_ENGINE


def verify_portal_record(directory, result, mapping):
    portal = result["portal_events"]
    if portal is None:
        return
    try:
        request = portal["request"]
        context = result["execution_context"]
        node = [n for n in mapping["nodes"] if n["id"] == "COMMAND:tests/docs-portal.test.sh:0"]
        if (len(node) != 1 or request["source_root"] != context["cwd"] or
                request["output"] != context["output"] + "/portal-events" or
                request["source_binding"] != {key: result["before"][key] for key in
                    ("head", "tree", "tracked_source_digest", "status_digest")} or
                request["mapping"] != dict(graph_digest=mapping["digest"], registry_sha256=mapping["registry_sha256"],
                    node={key: node[0][key] for key in ("id", "source", "source_sha256", "command")})):
            raise WG.WorkGraphError("foreign portal qualifier source/run/node binding")
        for name, member in request["sources"].items():
            for source in (result["before"], result["after"]):
                acquired = source["members"].get(name, {})
                if acquired.get("kind") != "FILE" or any(acquired.get(key) != member[key] for key in ("mode", "bytes", "sha256")):
                    raise WG.WorkGraphError("stale portal producer/helper source binding")
        expected = portal_engine().verify(directory / "portal-events", request, require_complete=result["exit"] == 0)
        if WG.canonical_json_v1(expected) != WG.canonical_json_v1(portal):
            raise WG.WorkGraphError("portal event/generation handoff differs from original binding")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise WG.WorkGraphError("portal retained-record refusal: " + str(exc)) from exc


def repro_event_engine():
    """Execute acquired helper bytes, then retain their identity for readback."""
    global _REPRO_EVENT_ENGINE
    path = LOADED_DRIVER_PATH.with_name("repro-event-capture.py")
    member = source_member(path.name, root=path.parent, with_bytes=True, byte_limit=EXPLICIT_FILE_LIMIT)
    if member.get("kind") != "FILE":
        raise WG.WorkGraphError("repro event capture helper is unavailable")
    data = member.pop("_acquired_bytes")
    if _REPRO_EVENT_ENGINE is None:
        spec = importlib.util.spec_from_file_location("repro_event_capture", path)
        _REPRO_EVENT_ENGINE = importlib.util.module_from_spec(spec)
        exec(compile(data, str(path), "exec"), _REPRO_EVENT_ENGINE.__dict__)
        _REPRO_EVENT_ENGINE._QUALIFIER_LOADED_SOURCE = data
    if _REPRO_EVENT_ENGINE._QUALIFIER_LOADED_SOURCE != data:
        raise WG.WorkGraphError("loaded repro event helper differs from current source")
    return _REPRO_EVENT_ENGINE


def repro_event_binding(mapping, source, original_output):
    producer = repro_binding(mapping, source)
    if producer["sha256"] != REPRO_EVENT_PRODUCER_SHA256:
        raise WG.WorkGraphError("repro event capture requires its exact event-capable producer")
    identities = {}
    for role, name in (("producer", REPRO_PRODUCER), ("capture_owner", REPRO_EVENT_OWNER)):
        member = source.get("members", {}).get(name, {})
        if member.get("kind") != "FILE" or member.get("tracked") is not True:
            raise WG.WorkGraphError("repro event owner must be an acquired tracked file")
        identities[role] = dict(path=name, **{key: member[key] for key in ("bytes", "sha256", "mode")})
    return dict(output=original_output + "/repro-events",
        source=dict(source_commit=source["head"], source_tree=source["tree"], **identities),
        mapping=dict(graph_digest=mapping["digest"], registry_sha256=mapping["registry_sha256"],
                     node=producer["node"], source=producer["source"], source_sha256=producer["source_sha256"]))


def observe_repro_events(directory, original_output, mapping, before, after, code, *, original_cwd):
    binding = repro_event_binding(mapping, before, original_output)
    binding["repository"] = original_cwd
    if dict(repro_event_binding(mapping, after, original_output), repository=original_cwd) != binding:
        raise WG.WorkGraphError("repro event producer/helper source changed")
    target = directory / "repro-events"
    if not target.exists() and not target.is_symlink() and code != 0:
        record = None  # A failed outer process may not have reached this family.
    else:
        try:
            engine = repro_event_engine()
            loaded = engine._QUALIFIER_LOADED_SOURCE
            expected_owner = binding["source"]["capture_owner"]
            if len(loaded) != expected_owner["bytes"] or sha(loaded) != expected_owner["sha256"]:
                raise WG.WorkGraphError("repro event reader differs from the captured source owner")
            record = engine.verify_record(target,
                expected_source=binding["source"], require_complete=code == 0)
            session = engine.json_read(target / "session.json")
            if (engine.digest(engine.canonical(session)) != record["session_sha256"] or
                    session["context"]["repository"] != original_cwd or session["context"]["cwd"] != original_cwd):
                raise WG.WorkGraphError("repro event session crossed its original qualifier repository")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise WG.WorkGraphError("repro event handoff refusal: " + str(exc)) from exc
    complete = record is not None and record["assessment"]["complete"] and code == 0 and before == after
    return dict(schema="implementaudit.verifier-repro-events.v1", binding=binding, record=record,
                coverage="COMPLETE_FINITE_REPRO_CHILD_EVENTS" if complete else "UNQUALIFIED_PARTIAL_OR_FAILED_PROCESS",
                semantics="OWN_CHILD_PROCESS_OBSERVATIONS; IMPORTED_READBACK_DECLARED_CONSISTENCY_ONLY")


def verify_repro_event_record(directory, result, mapping):
    observed = result["repro_events"]
    if observed is None:
        return
    expected = observe_repro_events(directory, result["execution_context"]["output"], mapping,
                                   result["before"], result["after"], result["exit"],
                                   original_cwd=result["execution_context"]["cwd"])
    if WG.canonical_json_v1(expected) != WG.canonical_json_v1(observed):
        raise WG.WorkGraphError("repro event handoff differs from original source/run/node binding")


def full_engine_binding():
    # These are the actual loaded paths, not a candidate ROOT that a caller may
    # point at a small fixture. This is source currentness, not startup trust.
    result = {}
    engine_root = LOADED_DRIVER_PATH.parents[1]
    for name, path, loaded in (("driver_sha256", LOADED_DRIVER_PATH, LOADED_DRIVER),
                               ("compiler_sha256", LOADED_COMPILER_PATH, LOADED_COMPILER)):
        member = source_member(path.relative_to(engine_root).as_posix(), root=engine_root)
        if (member["kind"] != "FILE" or member["bytes"] != len(loaded) or
                member["sha256"] != sha(loaded)):
            raise WG.WorkGraphError("loaded verifier engine differs from current source")
        result[name] = sha(loaded)
    return result


def trace_nodes(mapping, mode, code, data):
    """Derive the only legal source-ordered START/PASS prefix; no attestation."""
    if type(mode) is not str or mode not in {"legacy", "dag"} or type(code) is not int:
        raise WG.WorkGraphError("invalid verifier node observation context")
    names = [n["id"] for n in mapping["nodes"]]
    if mode == "legacy":
        if data is not None:
            raise WG.WorkGraphError("legacy route has no original node trace")
        events = []
    else:
        if type(data) is not bytes or (data and not data.endswith(b"\n")):
            raise WG.WorkGraphError("invalid verifier node trace framing")
        events = data.split(b"\n")[:-1] if data else []
        expected = [name.encode() + b"\t" + state for name in names for state in (b"START", b"PASS")]
        if events != expected[:len(events)] or len(events) > len(expected):
            raise WG.WorkGraphError("invalid ordered verifier node trace")
        if code == 0 and len(events) != len(expected):
            raise WG.WorkGraphError("successful verifier has incomplete node trace")
    nodes = []
    for index, name in enumerate(names):
        state = "PASS" if len(events) >= 2 * index + 2 else (
            "INTERRUPTED" if code < 0 else "FAIL") if len(events) == 2 * index + 1 else "UNSETTLED"
        nodes.append(dict(node=name, status=state, terminal=state != "UNSETTLED"))
    return nodes


def valid_nodes(nodes, names, mode, code):
    if type(nodes) is not list or len(nodes) != len(names):
        return False
    for node, name in zip(nodes, names):
        if (type(node) is not dict or set(node) != {"node", "status", "terminal"} or
                type(node["node"]) is not str or node["node"] != name or
                type(node["status"]) is not str or node["status"] not in {"PASS", "FAIL", "INTERRUPTED", "UNSETTLED"} or
                type(node["terminal"]) is not bool or node["terminal"] != (node["status"] != "UNSETTLED") or
                (mode == "legacy" and node["status"] != "UNSETTLED") or
                (node["status"] == "FAIL" and code <= 0) or
                (node["status"] == "INTERRUPTED" and code >= 0)):
            return False
    return True


def verified_record(directory):
    """Check declared retained observations, not execution authenticity."""
    def read_json(name):
        return WG.decode_strict_json_bytes((directory / name).read_bytes(), name)
    result, mapping = read_json("result.json"), read_json("mapping.json")
    if (type(result) is not dict or type(result.get("schema")) is not str or
            result["schema"] not in {"implementaudit.verifier-run.v1", "implementaudit.verifier-run.v2", "implementaudit.verifier-run.v3", "implementaudit.verifier-run.v4"}):
        raise WG.WorkGraphError("invalid verifier result schema")
    fields = {"schema", "mode", "command", "before", "after", "environment", "registry_sha256",
              "graph_digest", "mapped_nodes", "registered_tests", "registration_complete", "exit",
              "elapsed_ms", "stdout_sha256", "stderr_sha256", "nodes", "authority"}
    if result["schema"] != "implementaudit.verifier-run.v1":
        fields |= {"environment_after", "engine_binding", "node_trace", "execution_context",
                   "actual_argv", "command_stream"}
    if result["schema"] in {"implementaudit.verifier-run.v3", "implementaudit.verifier-run.v4"}:
        fields |= {"repro_artifacts", "child_environment", "stdin", "dist_namespace"}
    if result["schema"] == "implementaudit.verifier-run.v4":
        fields |= {"portal_events", "repro_events"}
    if (set(result) != fields or type(result.get("mode")) is not str or
            result["mode"] not in {"legacy", "dag"} or result.get("authority") != "NONE" or
            type(result.get("command")) is not list or
            not all(type(value) is str for value in result["command"]) or
            not all(type(result.get(key)) is dict for key in ("before", "after", "environment")) or
            any(type(result.get(key)) is not str or not re.fullmatch(r"[0-9a-f]{64}", result[key])
                for key in ("registry_sha256", "graph_digest", "stdout_sha256", "stderr_sha256"))):
        raise WG.WorkGraphError("invalid verifier result members or types")
    registry = b"".join(n["source"].encode() for n in mapping["nodes"])
    compiled_stream = WG.verifier_command_stream_v1(mapping, registry)
    names = [n["id"] for n in mapping["nodes"]]
    exit_bytes = (directory / "exit-code.txt").read_bytes()
    valid = (result["command"] == ["bash", "scripts/verify-package.sh" if result["mode"] == "legacy"
                                   else "scripts/run-work-graph-verifier.sh"] and
             result["graph_digest"] == mapping["digest"] and
             result["registry_sha256"] == mapping["registry_sha256"] and
             result["environment"] == mapping["environment"] and
             type(result["mapped_nodes"]) is int and result["mapped_nodes"] == len(names) and
             type(result["registered_tests"]) is int and result["registered_tests"] == len(mapping["test_nodes"]) and
             type(result["exit"]) is int and re.fullmatch(rb"-?(?:0|[1-9][0-9]*)\n", exit_bytes) is not None and
             int(exit_bytes) == result["exit"] and
             type(result["registration_complete"]) is bool and
             type(result["elapsed_ms"]) is int and result["elapsed_ms"] >= 0 and
             valid_nodes(result["nodes"], names, result["mode"], result["exit"]) and
             all(result[stream + "_sha256"] == sha((directory / (stream + ".log")).read_bytes()) for stream in ("stdout", "stderr")))
    if not valid:
        raise WG.WorkGraphError("inconsistent verifier result, mapping, raw streams or durable exit")
    # All formats require an actual ordered DAG trace. Only v2/v3 originally
    # bound those bytes; reading v1 cannot retroactively create that binding.
    data = (directory / "nodes.tsv").read_bytes() if result["mode"] == "dag" else None
    if result["schema"] != "implementaudit.verifier-run.v1":
        if (type(result["environment_after"]) is not dict or
                type(result["engine_binding"]) is not dict or
                set(result["engine_binding"]) != {"driver_sha256", "compiler_sha256"} or
                any(type(value) is not str or not re.fullmatch(r"[0-9a-f]{64}", value)
                    for value in result["engine_binding"].values())):
            raise WG.WorkGraphError("invalid verifier observation binding")
        context, binding = result["execution_context"], result["command_stream"]
        if (type(context) is not dict or set(context) != {"cwd", "output"} or
                any(type(value) is not str or not Path(value).is_absolute() for value in context.values()) or
                type(result["actual_argv"]) is not list or
                not all(type(value) is str for value in result["actual_argv"]) or
                type(binding) is not dict or set(binding) != {"sha256", "bytes"} or
                type(binding["bytes"]) is not int or binding["bytes"] < 0 or
                type(binding["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", binding["sha256"])):
            raise WG.WorkGraphError("invalid verifier command input binding")
        retained_stream = (directory / "commands.bin").read_bytes()
        if (retained_stream != compiled_stream or len(retained_stream) != binding["bytes"] or
                sha(retained_stream) != binding["sha256"]):
            raise WG.WorkGraphError("inconsistent retained verifier command stream")
        # Validate the original literal execution paths, even when the retained
        # evidence is later restored elsewhere. This is not attestation.
        expected_argv = list(result["command"])
        if result["mode"] == "dag":
            original_output = context["output"]
            expected_argv += [original_output + "/commands.bin", original_output + "/nodes.tsv",
                              str(len(names)), binding["sha256"]]
        if result["actual_argv"] != expected_argv:
            raise WG.WorkGraphError("inconsistent verifier actual argv")
        trace = result["node_trace"]
        if result["mode"] == "dag":
            if (type(trace) is not dict or set(trace) != {"sha256", "bytes"} or
                    type(trace["bytes"]) is not int or trace["bytes"] < 0 or
                    type(trace["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", trace["sha256"])):
                raise WG.WorkGraphError("invalid verifier node trace binding")
            if len(data) != trace["bytes"] or sha(data) != trace["sha256"]:
                raise WG.WorkGraphError("inconsistent retained verifier node trace")
        else:
            if trace is not None:
                raise WG.WorkGraphError("legacy route has no original node trace")
    if result["nodes"] != trace_nodes(mapping, result["mode"], result["exit"], data):
        raise WG.WorkGraphError("inconsistent verifier nodes and ordered trace")
    if result["schema"] in {"implementaudit.verifier-run.v3", "implementaudit.verifier-run.v4"}:
        verify_extended_record(directory, result, mapping)
    if result["schema"] == "implementaudit.verifier-run.v4":
        verify_portal_record(directory, result, mapping)
        verify_repro_event_record(directory, result, mapping)
    return result


def compare(left, right, out):
    a, b = (verified_record(p) for p in (left, right))
    checks = dict(same_source=a["before"] == b["before"] == a["after"] == b["after"],
                  same_registry=a["registry_sha256"] == b["registry_sha256"],
                  same_environment=a["environment"] == a.get("environment_after", a["environment"]) ==
                                   b["environment"] == b.get("environment_after", b["environment"]),
                  same_record_schema=a["schema"] == b["schema"],
                  same_exit=a["exit"] == b["exit"],
                  same_stdout=(left / "stdout.log").read_bytes() == (right / "stdout.log").read_bytes(),
                  same_stderr=(left / "stderr.log").read_bytes() == (right / "stderr.log").read_bytes(),
                  route_pair={a["mode"], b["mode"]} == {"legacy", "dag"})
    if a["schema"] != "implementaudit.verifier-run.v1" and b["schema"] != "implementaudit.verifier-run.v1":
        checks.update(same_engine=a["engine_binding"] == b["engine_binding"],
                      same_execution_cwd=a["execution_context"]["cwd"] == b["execution_context"]["cwd"],
                      same_compiled_stream=(left / "commands.bin").read_bytes() == (right / "commands.bin").read_bytes())
    if a["schema"] == b["schema"] and a["schema"] in {"implementaudit.verifier-run.v3", "implementaudit.verifier-run.v4"}:
        same_artifacts = a["repro_artifacts"] == b["repro_artifacts"]
        if same_artifacts and a["repro_artifacts"] is not None:
            same_artifacts = all(retained_bytes(left, member["relative_path"])[0] == retained_bytes(right, member["relative_path"])[0]
                                 for member in a["repro_artifacts"]["files"].values() if member["observation"]["kind"] == "FILE")
        same_stdin = a["stdin"] == b["stdin"]
        if same_stdin and a["stdin"] is not None:
            same_stdin = retained_bytes(left, "stdin.bin")[0] == retained_bytes(right, "stdin.bin")[0]
        checks.update(same_child_environment=a["child_environment"] == b["child_environment"],
                      same_declared_repro_artifacts=same_artifacts, same_stdin=same_stdin)
        same_dist = a["dist_namespace"] == b["dist_namespace"]
        if same_dist and a["dist_namespace"] is not None:
            namespace = a["dist_namespace"]
            same_dist = namespace["before"] == namespace["after"] and all(
                retained_bytes(left / phase, name)[0] == retained_bytes(right / phase, name)[0]
                for phase in ("dist-before", "dist-after")
                for name, member in namespace["before"]["entries"].items() if member["kind"] == "FILE")
        checks["same_dist_namespace"] = same_dist
    if a["schema"] == b["schema"] == "implementaudit.verifier-run.v4":
        checks["same_portal_events"] = a["portal_events"] == b["portal_events"]
        checks["same_repro_events"] = a["repro_events"] == b["repro_events"]
    result = dict(schema="implementaudit.verifier-correspondence.v1", checks=checks,
                  record_coverage=["HISTORICAL_V1_RETAINED_TRACE_VALIDATED_NO_ORIGINAL_BINDING" if r["schema"].endswith(".v1") and r["mode"] == "dag"
                                   else "HISTORICAL_V1_WHOLE_PROCESS_ONLY" if r["schema"].endswith(".v1")
                                   else "DECLARED_INPUT_OUTPUT_OBSERVATIONS_V3" if r["schema"].endswith(".v3")
                                   else "FINITE_CHILD_INVOCATION_OBSERVATIONS_V4" if r["schema"].endswith(".v4")
                                   else "ORDERED_TRACE_BOUND_V2" if r["mode"] == "dag"
                                   else "WHOLE_PROCESS_ONLY_V2" for r in (a, b)],
                  raw_observables_equal=all(checks.values()), normalization="NONE_RAW_BYTES",
                  evidence_semantics="NODE_AND_WHOLE_PROCESS_ONLY; TRANSITIVE_OUTPUT_ARTIFACT_SEMANTICS_UNQUALIFIED",
                  canonical_conversion="NOT_PERFORMED", retirement="NOT_PERFORMED", authority="NONE")
    if a["schema"] == b["schema"] and a["schema"] in {"implementaudit.verifier-run.v3", "implementaudit.verifier-run.v4"}:
        result["repro_artifact_coverage"] = [r["repro_artifacts"]["coverage"] if r["repro_artifacts"] is not None
                                             else "NOT_REQUESTED" for r in (a, b)]
        result["stdin_coverage"] = [r["stdin"]["mode"] if r["stdin"] is not None else "INHERITED_UNQUALIFIED" for r in (a, b)]
        result["dist_coverage"] = [r["dist_namespace"]["coverage"] if r["dist_namespace"] is not None
                                   else "UNACQUIRED" for r in (a, b)]
        result["evidence_semantics"] += "; EXPLICIT_DECLARED_INPUT_OUTPUT_OBSERVATIONS_ONLY"
        if a["schema"] == "implementaudit.verifier-run.v3":
            result["evidence_semantics"] += "; NO_INTERNAL_EVENT_CUSTODY"
        else:
            result["portal_coverage"] = [r["portal_events"]["coverage"] if r["portal_events"] is not None
                                         else "NOT_REQUESTED" for r in (a, b)]
            result["repro_event_coverage"] = [r["repro_events"]["coverage"] if r["repro_events"] is not None
                                              else "NOT_REQUESTED" for r in (a, b)]
            result["evidence_semantics"] += "; FINITE_CHILD_EVENTS_DECLARED_CONSISTENCY; IMPORTED_EXECUTION_AUTHENTICATION_UNQUALIFIED"
    out.write_bytes(WG.canonical_json_v1(result) + b"\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if all(checks.values()) else 1


def run(mode, output, *, retain_repro_assets=False, stdin_file=None, empty_stdin=False, capture_dist=False,
        capture_portal_events=False, retain_repro_events=False):
    if stdin_file is not None and empty_stdin:
        raise WG.WorkGraphError("stdin-file and empty-stdin are mutually exclusive")
    events = capture_portal_events or retain_repro_events
    extended = retain_repro_assets or stdin_file is not None or empty_stdin or capture_dist or events
    if extended and (output == ROOT or ROOT in output.parents):
        raise WG.WorkGraphError("extended capture evidence must be outside the candidate")
    output.mkdir(parents=True, exist_ok=False)
    engine = full_engine_binding()
    before = source_identity()
    if REPRO_EVENT_ENV in os.environ:
        raise WG.WorkGraphError("ambiguous inherited repro event capture directory")
    child_environment = dict(os.environ) if extended else None
    overrides = {}
    if retain_repro_assets:
        if any(k == "REPRO_SOURCE_REF" or k.startswith("REPRO_RETAINED_") for k in os.environ):
            raise WG.WorkGraphError("ambiguous inherited repro retention/source-ref override")
        (output / "repro-assets").mkdir(mode=0o700)
        overrides = repro_overrides(str(output))
        child_environment.update(overrides)
    if capture_portal_events:
        if PORTAL_ENV in os.environ:
            raise WG.WorkGraphError("ambiguous inherited portal capture request")
        overrides[PORTAL_ENV] = str(output / "portal-events/request.json")
        child_environment.update(overrides)
    if retain_repro_events:
        if "REPRO_SOURCE_REF" in os.environ:
            raise WG.WorkGraphError("ambiguous inherited repro event source-ref override")
        overrides[REPRO_EVENT_ENV] = str(output / "repro-events")
        child_environment.update(overrides)
    environment = environment_identity(child_environment, child_resolution=extended)
    registry = (ROOT / "scripts/verify-package.sh").read_bytes()
    tests = WG.verifier_registered_tests_v1(registry)
    graph = WG.compile_verifier_graph_v1(registry, tests, environment)
    if retain_repro_assets:
        repro_binding(graph, before)
    if retain_repro_events:
        repro_event_binding(graph, before, str(output))
        repro_event_engine()
    portal_request = None
    if capture_portal_events:
        try:
            portal_request = portal_engine().prepare(output / "portal-events", ROOT, graph, before)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise WG.WorkGraphError("portal acquisition refusal: " + str(exc)) from exc
    child_binding = stdin_binding = stdin_bytes = None
    if extended:
        child_binding = dict(schema="implementaudit.verifier-child-environment.v1",
                             base_environment_sha256=environment_digest(os.environ),
                             actual_environment_sha256=environment_digest(child_environment), overrides=overrides)
        durable_bytes(output / "child-environment.json", WG.canonical_json_v1(child_binding) + b"\n")
    if stdin_file is not None or empty_stdin:
        stdin_binding, stdin_bytes = acquire_stdin(output, stdin_file, empty_stdin)
    dist_before = dist_inventory(ROOT, snapshot=output / "dist-before") if capture_dist else None
    actual_tests = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("*.test.sh"))
    registration_complete = actual_tests == tests
    (output / "mapping.json").write_bytes(WG.canonical_json_v1(graph) + b"\n")
    stream = output / "commands.bin"
    compiled_stream = WG.verifier_command_stream_v1(graph, registry)
    stream.write_bytes(compiled_stream)
    if mode == "legacy":
        command = ["bash", "scripts/verify-package.sh"]
    else:
        command = ["bash", "scripts/run-work-graph-verifier.sh", str(stream), str(output / "nodes.tsv"), str(len(graph["nodes"])), sha(compiled_stream)]
        # Empty means no node start was observed, including a prestart
        # failure before the runner opens its trace descriptor.
        (output / "nodes.tsv").write_bytes(b"")
    full_engine_binding()
    started = time.monotonic()
    launch = {} if not extended else dict(env=child_environment)
    if stdin_binding is not None:
        launch["input"] = stdin_bytes
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, **launch)
        # Retain the actual nested exit before any source/trace/JSON work.
        # A later wrapper error cannot silently erase a completed verdict.
        with (output / "exit-code.txt").open("w") as terminal:
            terminal.write(str(process.returncode) + "\n")
            terminal.flush()
            os.fsync(terminal.fileno())
    full_engine_binding()
    if stream.read_bytes() != compiled_stream:
        raise WG.WorkGraphError("retained verifier command stream differs from launched input")
    after = source_identity()
    environment_after = environment_identity(dict(os.environ, **overrides) if extended else None, child_resolution=extended)
    trace = (output / "nodes.tsv").read_bytes() if mode == "dag" else None
    node_results = trace_nodes(graph, mode, process.returncode, trace)
    namespace = None
    if capture_dist:
        namespace = dist_binding(output, dist_before, dist_inventory(ROOT, snapshot=output / "dist-after"))
        durable_bytes(output / "dist-namespace.json", WG.canonical_json_v1(namespace) + b"\n")
    artifacts = None
    if retain_repro_assets:
        artifacts = observe_repro_artifacts(output, str(output), graph, before, after, process.returncode)
        durable_bytes(output / "repro-artifacts.json", WG.canonical_json_v1(artifacts) + b"\n")
        if process.returncode == 0 and (not artifacts["complete"] or not artifacts["source_current"]):
            raise WG.WorkGraphError("successful repro capture has missing artifacts or changed source")
    portal = None
    if portal_request is not None:
        try:
            portal = portal_engine().verify(output / "portal-events", portal_request, require_complete=process.returncode == 0)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise WG.WorkGraphError("portal handoff refusal: " + str(exc)) from exc
    repro_events = observe_repro_events(output, str(output), graph, before, after, process.returncode,
                                       original_cwd=str(ROOT)) if retain_repro_events else None
    result = dict(schema="implementaudit.verifier-run.v4" if events else "implementaudit.verifier-run.v3" if extended else "implementaudit.verifier-run.v2", mode=mode, command=command[:2],
                  actual_argv=command, execution_context=dict(cwd=str(ROOT), output=str(output)),
                  command_stream=dict(sha256=sha(compiled_stream), bytes=len(compiled_stream)),
                  before=before, after=after, environment=environment, environment_after=environment_after,
                  engine_binding=engine,
                  registry_sha256=sha(registry), graph_digest=graph["digest"],
                  mapped_nodes=len(graph["nodes"]), registered_tests=len(tests),
                  registration_complete=registration_complete,
                  exit=process.returncode, elapsed_ms=int((time.monotonic() - started) * 1000),
                  stdout_sha256=sha((output / "stdout.log").read_bytes()), stderr_sha256=sha((output / "stderr.log").read_bytes()),
                  nodes=node_results, node_trace=None if trace is None else dict(sha256=sha(trace), bytes=len(trace)),
                  authority="NONE")
    if extended:
        result.update(repro_artifacts=artifacts, child_environment=child_binding, stdin=stdin_binding, dist_namespace=namespace)
        if events:
            result.update(portal_events=portal, repro_events=repro_events)
        verify_extended_record(output, result, graph)
        if events:
            verify_portal_record(output, result, graph)
            verify_repro_event_record(output, result, graph)
    (output / "result.json").write_bytes(WG.canonical_json_v1(result) + b"\n")
    print(json.dumps({k: result[k] for k in ("mode", "exit", "elapsed_ms", "mapped_nodes", "registered_tests", "registration_complete", "stdout_sha256", "stderr_sha256")}, sort_keys=True))
    return process.returncode if process.returncode >= 0 else 128 - process.returncode


def _registry_membership_snapshot_v1(root):
    """Acquire the original checker's immediate glob without reading contents.

    The fixed profile accepts ordinary matching files only. Python's glob also
    yields directories and links; these refuse rather than disappear from the
    projected namespace. Nonmatching names are observed for acquisition drift,
    but neither their types nor contents affect this name-only predicate.
    """
    if ".." in Path(root).parts:
        raise WG.WorkGraphError("registry source parent traversal is unqualified")
    source = Path(os.path.abspath(root))
    try:
        source_bytes = len(str(source).encode("utf-8", "strict"))
    except UnicodeError as exc:
        raise WG.WorkGraphError("registry source path is not UTF-8") from exc
    components = source.parts[1:]
    if len(components) > 128 or source_bytes > 4096:
        raise WG.WorkGraphError("registry source path bound exceeded")
    require_source_descriptor_api()
    chain = []
    def node_identity(info):
        return [str(info.st_dev), str(info.st_ino), info.st_mode]
    def stamp(info):
        return node_identity(info) + [info.st_size, info.st_mtime_ns, info.st_ctime_ns]
    try:
        fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        chain.append((fd, None, node_identity(os.fstat(fd))))
        for component in (*components, "tests"):
            fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            chain.append((fd, component, node_identity(os.fstat(fd))))
        before = stamp(os.fstat(fd))
        def census():
            names, total = [], 0
            with os.scandir(fd) as entries:
                for entry in entries:
                    try:
                        total += len(entry.name.encode("utf-8", "strict"))
                    except UnicodeError as exc:
                        raise WG.WorkGraphError("registry membership name is not UTF-8") from exc
                    names.append(entry.name)
                    if len(names) > 4096 or total > 1024 * 1024:
                        raise WG.WorkGraphError("registry membership name/entry bound exceeded")
            return sorted(names)
        names = census()
        members, identities = {}, {}
        for name in names:
            if not name.endswith(".test.sh"):
                continue
            info = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if not stat.S_ISREG(info.st_mode):
                raise WG.WorkGraphError("registry matching member must be an ordinary file")
            members[name], identities[name] = "FILE", stamp(info)
        if census() != names or stamp(os.fstat(fd)) != before:
            raise WG.WorkGraphError("registry membership changed during acquisition")
        for name, observed in identities.items():
            if stamp(os.stat(name, dir_fd=fd, follow_symlinks=False)) != observed:
                raise WG.WorkGraphError("registry member changed during acquisition")
        for index, (opened, component, observed) in enumerate(chain):
            if node_identity(os.fstat(opened)) != observed or (index and
                    node_identity(os.stat(component, dir_fd=chain[index - 1][0], follow_symlinks=False)) != observed):
                raise WG.WorkGraphError("registry directory chain changed during acquisition")
        projection = dict(path="tests", pattern="*.test.sh", entries=members,
            mode=stat.S_IMODE(os.fstat(fd).st_mode), observation="IMMEDIATE_GLOB_NAMES_ONLY_NO_CONTENT_READS")
        currentness = dict(directory=before, ancestors=[row[2] for row in chain],
                           census=names, members=identities)
        return projection, currentness
    finally:
        for fd, _, _ in reversed(chain):
            os.close(fd)


def registry_membership_v1(root):
    return _registry_membership_snapshot_v1(root)[0]


class VerifierTaskSession:
    """Live producer custody for a finite, isolated two-real-checker scope.

    No imported execution receipts, persistent cache admission, canonical
    predecessor substitution, native currentness or campaign qualification.
    The trusted task process/kernel observe execution. Candidate and runtime
    bytes are captured, mounted from sealed descriptors and rechecked at each
    consumption boundary; arbitrary concurrent host/producer compromise is
    outside this portable scope.
    """
    SCOPE = "CONTROLLED_TASK_LEAVES_V1"
    CONTRACTS = WG.VERIFIER_LEAF_CONTRACTS_V1
    ENVIRONMENT = dict(PATH="/usr/bin", LANG="C", LC_ALL="C", TZ="UTC", PYTHONHASHSEED="0")
    LIMITS = dict(cpu_seconds=30, address_bytes=1073741824, file_bytes=8388608,
                  descriptors=4096, scratch_bytes=8388608, wall_seconds=45)
    ENGINE_PATHS = ("scripts/qualify-work-graph-verifier.py", "scripts/run-work-graph-verifier.sh",
                    "skills/implementaudit/scripts/compile-work-graph.py")
    RUNTIME_FILES = ("/usr/bin/bash", "/usr/bin/dirname", "/usr/bin/python3.12",
                     "/lib/x86_64-linux-gnu/libtinfo.so.6", "/lib/x86_64-linux-gnu/libc.so.6",
                     "/lib/x86_64-linux-gnu/libm.so.6", "/lib/x86_64-linux-gnu/libz.so.1",
                     "/lib/x86_64-linux-gnu/libexpat.so.1", "/lib64/ld-linux-x86-64.so.2")
    # Linux x86_64 classic BPF: require the native ABI, deny unshare/setns and
    # CLONE_NEWUSER, and return ENOSYS for clone3/x32. Normal fork/clone remains
    # available. No host sysctl write is needed. Offsets/constants are from
    # linux/seccomp.h, audit.h, sched.h and asm/unistd_64.h.
    SECCOMP = b"".join(struct.pack("HBBI", *instruction) for instruction in (
        (0x20, 0, 0, 4), (0x15, 1, 0, 0xC000003E), (0x06, 0, 0, 0x80000000),
        (0x20, 0, 0, 0), (0x35, 9, 0, 0x40000000), (0x15, 7, 0, 272),
        (0x15, 6, 0, 308), (0x15, 6, 0, 435), (0x15, 1, 0, 56),
        (0x06, 0, 0, 0x7FFF0000), (0x20, 0, 0, 16), (0x45, 1, 0, 0x10000000),
        (0x06, 0, 0, 0x7FFF0000), (0x06, 0, 0, 0x00050001), (0x06, 0, 0, 0x00050026)))

    def __init__(self, source_root, output, *, runtime_root=Path("/"), environment=None, max_age=3600):
        if platform.system() != "Linux" or platform.machine() != "x86_64":
            raise WG.WorkGraphError("controlled leaf profile requires Linux x86_64")
        if resource is None or not hasattr(os, "memfd_create") or not all(hasattr(fcntl, n) for n in
                ("F_ADD_SEALS", "F_SEAL_WRITE", "F_SEAL_GROW", "F_SEAL_SHRINK", "F_SEAL_SEAL")):
            raise WG.WorkGraphError("controlled leaf profile requires Python with Linux memfd sealing support")
        self.source = Path(source_root).resolve(strict=True)
        self.output = Path(output).resolve()
        if self.output == self.source or self.source in self.output.parents:
            raise WG.WorkGraphError("evidence must be outside the candidate source")
        self.environment = dict(self.ENVIRONMENT if environment is None else environment)
        if self.environment != self.ENVIRONMENT or type(max_age) is not int or not 0 < max_age <= 3600:
            raise WG.WorkGraphError("unsupported environment or receipt lifetime")
        self.runtime_root = Path(runtime_root).resolve(strict=True)
        self.output.mkdir(parents=True, exist_ok=False)
        self.output.chmod(0o700)
        self.producer = os.urandom(16).hex()
        self.producer_pid = os.getpid()
        self.max_age = max_age
        self.dispatch_count = self.generation = 0
        self._issued = {}
        self._engine = self._engine_binding()
        self._write(self.output / "session.json", dict(schema="implementaudit.verifier-task-session.v1",
                    scope=self.SCOPE, producer=self.producer, source=str(self.source),
                    producer_pid=self.producer_pid,
                    engine=self._engine, receipt_custody="LIVE_PRODUCER_ONLY_NO_IMPORT", max_age_seconds=max_age,
                    canonical_acceptance="UNQUALIFIED", authority="NONE"))

    @staticmethod
    def _encode(value):
        return WG.canonical_json_v1(value) + b"\n"

    @staticmethod
    def _write(path, value):
        data = value if isinstance(value, bytes) else VerifierTaskSession._encode(value)
        with path.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())

    @staticmethod
    def _regular(path, missing=False):
        """No source symlinks or special files; retain one opened byte snapshot."""
        path = Path(path)
        for parent in path.parents:
            if parent.is_symlink():
                raise WG.WorkGraphError("unsupported source prefix symlink")
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except FileNotFoundError:
            if missing:
                return dict(kind="MISSING"), None
            raise
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > 33554432:
                raise WG.WorkGraphError("unsupported nonregular or oversized input")
            if os.listxattr(path):
                raise WG.WorkGraphError("extended input metadata is unqualified")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                data = stream.read()
            after = os.fstat(fd)
            observed = path.lstat()
            identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
            if identity(before) != identity(after) or identity(after) != identity(observed):
                raise WG.WorkGraphError("input changed during acquisition")
            return dict(kind="FILE", mode=stat.S_IMODE(after.st_mode), size=len(data), sha256=sha(data)), data
        finally:
            os.close(fd)

    def _engine_binding(self):
        result = {name: sha(self._regular(ROOT / name)[1]) for name in self.ENGINE_PATHS}
        if result[self.ENGINE_PATHS[0]] != sha(LOADED_DRIVER) or result[self.ENGINE_PATHS[2]] != sha(LOADED_COMPILER):
            raise WG.WorkGraphError("loaded producer code differs from current source")
        return result

    def _object(self, data):
        digest = sha(data)
        directory = self.output / "objects"
        directory.mkdir(exist_ok=True)
        path = directory / digest
        if path.exists():
            if self._regular(path)[1] != data:
                raise WG.WorkGraphError("retained object changed")
        else:
            self._write(path, data)
            path.chmod(0o400)
        return digest

    def _source_state(self):
        environment = dict(PATH="/usr/bin", LANG="C", LC_ALL="C", GIT_CONFIG_NOSYSTEM="1",
                           GIT_CONFIG_GLOBAL="/dev/null", GIT_OPTIONAL_LOCKS="0")
        def git(*args):
            return subprocess.check_output(["/usr/bin/git", *args], cwd=self.source, env=environment)
        paths = git("ls-files", "-z").split(b"\0")
        records, contents, directories = {}, {}, {}
        for raw in paths:
            if not raw:
                continue
            name = raw.decode("utf-8", "strict")
            if name.startswith("/") or any(p in {"", ".", ".."} for p in name.split("/")):
                raise WG.WorkGraphError("unsupported candidate path")
            records[name], contents[name] = self._regular(self.source / name, missing=True)
            for parent in (self.source / name).parents:
                if parent != self.source and self.source not in parent.parents:
                    break
                if parent.exists():
                    observed = parent.lstat()
                    if not stat.S_ISDIR(observed.st_mode) or os.listxattr(parent):
                        raise WG.WorkGraphError("unsupported source directory metadata")
                    directories[parent.relative_to(self.source).as_posix()] = stat.S_IMODE(observed.st_mode)
        state = dict(head=git("rev-parse", "HEAD").decode().strip(), tree=git("rev-parse", "HEAD^{tree}").decode().strip(),
                     files=records, directories=directories)
        return state, contents

    def _runtime(self):
        base = self.runtime_root
        names = set(self.RUNTIME_FILES)
        stdlib = base / "usr/lib/python3.12"
        for path in sorted(stdlib.rglob("*")):
            relative = path.relative_to(base).as_posix()
            # The finite image has no bytecode, site hook or site-packages.
            if "__pycache__" in path.parts or path.name == "sitecustomize.py":
                continue
            if path.is_file():
                names.add("/" + relative)
            elif not path.is_dir():
                raise WG.WorkGraphError("unsupported runtime member")
        files = {}
        for name in sorted(names):
            path = base / name.lstrip("/")
            resolved = path.resolve(strict=True)
            if base != Path("/") and base not in resolved.parents:
                raise WG.WorkGraphError("runtime symlink escapes captured root")
            metadata, data = self._regular(resolved)
            executable = bool(metadata["mode"] & 0o111)
            files[name] = (data, 0o555 if executable else 0o444)
        files["/usr/bin/python"] = (b'#!/usr/bin/bash\nexec /usr/bin/python3.12 -P -S -B "$@"\n', 0o555)
        return files

    def _image(self, files, source_observations, membership=None):
        members = [dict(path=name, mode=mode, bytes=len(data), sha256=self._object(data))
                   for name, (data, mode) in sorted(files.items())]
        directories = sorted({str(p) for name in files for p in Path(name).parents if str(p) != "/"})
        manifest = dict(schema="implementaudit.verifier-finite-image.v1", files=members,
                        directories=directories, directory_mode=0o755, root_read_only=True,
                        source_observations=source_observations, logical_cwd="/work",
                        environment=self.environment, limits=self.LIMITS,
                        seccomp_sha256=self._object(self.SECCOMP),
                        stdin="EMPTY", stdout_stderr="OBSERVER_FILES", semantic_artifacts=[],
                        writable_resources=["fresh bounded /tmp", "/dev/null", "stdout", "stderr"],
                        namespace="UNSHARE_ALL_NO_PROC_NO_GENERAL_DEV_NO_HOST_ROOT",
                        startup="PYTHON_3_12_P_S_B_FIXED_HASHSEED_NO_SITE_NO_BYTECODE",
                        source_projection="READ_BYTES_AND_TYPED_EXISTENCE_PLACEHOLDERS")
        if membership is not None:
            manifest["directories"] = sorted(set(directories) | {"/work/tests"})
            manifest["directory_membership"] = membership
            manifest["source_projection"] = "READ_BYTES_AND_TYPED_GLOB_NAME_PLACEHOLDERS"
        return manifest, self._object(self._encode(manifest))

    @staticmethod
    def _root_identity(info):
        """Canonical decimal uint64 device/inode for the acquired root binding."""
        identifiers = (info.st_dev, info.st_ino)
        if any(type(value) is not int or not 0 <= value < 2**64 for value in identifiers):
            raise WG.WorkGraphError("filesystem device/inode must be unsigned 64-bit integers")
        return [str(value) for value in identifiers]

    def _acquire(self):
        if os.getpid() != self.producer_pid:
            raise WG.WorkGraphError("producer process changed; receipt import is unsupported")
        if self.environment != self.ENVIRONMENT or self._engine_binding() != self._engine:
            raise WG.WorkGraphError("producer source or environment changed")
        state, contents = self._source_state()
        membership = None
        if self.SCOPE == "CONTROLLED_TASK_REGISTRY_V1":
            membership, membership_stamp = _registry_membership_snapshot_v1(self.source)
            state["registry_membership"] = dict(projection=membership, currentness=membership_stamp)
        registry = contents.get("scripts/verify-package.sh")
        if registry is None:
            raise WG.WorkGraphError("missing tracked verifier registry")
        graph = WG.compile_verifier_graph_v1(registry, WG.verifier_registered_tests_v1(registry), self.environment)
        runtime = self._runtime()
        runtime_manifest, runtime_digest = self._image(runtime, {})
        inputs, images = {}, {}
        projected = {p for c in self.CONTRACTS.values() for p in c["reads"] + c["probes"]}
        for program, contract in self.CONTRACTS.items():
            if contents.get(program) is None:
                raise WG.WorkGraphError("missing tracked checker contract")
            observations = {}
            files = dict(runtime)
            files["/work/" + program] = (contents[program], 0o555)
            observations[program] = state["files"][program]
            for name in contract["reads"] + contract["probes"]:
                if name not in state["files"]:
                    raise WG.WorkGraphError("untracked input dependency")
                observation = dict(state["files"][name])
                data = contents[name]
                if name in contract["probes"] and data is not None:
                    observation = {k: v for k, v in observation.items() if k in {"kind", "mode"}}
                    data = b""
                observations[name] = observation
                if data is not None:
                    files["/work/" + name] = (data, 0o444)
            files["/work/scripts/run-work-graph-verifier.sh"] = (self._regular(ROOT / "scripts/run-work-graph-verifier.sh")[1], 0o555)
            leaf_membership = membership if contract.get("membership") == "tests/*.test.sh" else None
            if leaf_membership is not None:
                for name in leaf_membership["entries"]:
                    files["/work/tests/" + name] = (b"", 0o444)
                observations["directory:tests"] = leaf_membership
            manifest, digest = (self._image(files, observations) if leaf_membership is None
                                else self._image(files, observations, leaf_membership))
            node = "COMMAND:" + program + ":0"
            inputs[node] = dict(program_sha256=sha(contents[program]), image_digest=digest)
            images[node] = (files, manifest)
        root_stat = self.source.stat()
        null = Path("/dev/null").lstat()
        if not stat.S_ISCHR(null.st_mode) or (os.major(null.st_rdev), os.minor(null.st_rdev)) != (1, 3):
            raise WG.WorkGraphError("unsupported null device")
        observer = {path: sha(self._regular(Path(path).resolve())[1]) for path in ("/usr/bin/bwrap", "/usr/bin/git", sys.executable)}
        inherited_limits = {name: list(resource.getrlimit(getattr(resource, name)))
                            for name in dir(resource) if name.startswith("RLIMIT_")}
        binding = dict(producer=self.producer, root=[str(self.source), *self._root_identity(root_stat)],
                       engine=self._engine, observer=observer, kernel=list(platform.uname()),
                       runtime=runtime_digest, environment=self.environment, limits=self.LIMITS,
                       inherited_resource_limits=inherited_limits,
                       directory_modes=state["directories"], process_identity=[self.producer_pid, os.geteuid(), os.getegid()],
                       null_device=[null.st_rdev, stat.S_IMODE(null.st_mode)],
                       source_guard=sha(WG.canonical_json_v1({n: v for n, v in state["files"].items() if n not in projected})))
        if membership is not None and _registry_membership_snapshot_v1(self.source) != (membership, membership_stamp):
            raise WG.WorkGraphError("registry namespace changed during complete acquisition")
        acquired = dict(schema="implementaudit.verifier-acquisition.v1", scope=self.SCOPE,
                        binding=binding, inputs=inputs)
        # Validate completeness and exact executable profiles before any dispatch.
        WG.compile_verifier_reuse_v1(graph, registry, acquired, {})
        return dict(state=state, acquired=acquired, graph=graph, registry=registry, images=images)

    def _verify_retained_result(self, receipt):
        if time.monotonic() - receipt["observed_at"] > self.max_age:
            raise WG.WorkGraphError("expired issued result")
        for name, data in receipt["retained"].items():
            if self._regular(receipt["directory"] / name)[1] != data:
                raise WG.WorkGraphError("issued output or receipt changed")
        for digest in receipt["required_objects"]:
            if sha(self._regular(self.output / "objects" / digest)[1]) != digest:
                raise WG.WorkGraphError("required execution input object changed")

    def _issued_keys(self):
        keys, refused = {}, {}
        for node, receipt in self._issued.items():
            try:
                self._verify_retained_result(receipt)
                keys[node] = receipt["key"]
            except (OSError, WG.WorkGraphError) as exc:
                refused[node] = str(exc)
        return keys, refused

    def _require_same(self, before, after, directory, phase):
        if any(before[key] != after[key] for key in ("state", "acquired")):
            # Preserve the disagreement before refusing. Do not normalize away
            # a concurrent candidate/runtime change or erase the old snapshot.
            self._write(directory / (phase + "-currentness-refusal.json"), dict(
                before={key: before[key] for key in ("state", "acquired")},
                after={key: after[key] for key in ("state", "acquired")}))
            raise WG.WorkGraphError("candidate changed " + phase)

    @staticmethod
    def _sealed(data):
        fd = os.memfd_create("r0035-retained-input", os.MFD_ALLOW_SEALING | os.MFD_CLOEXEC)
        try:
            with os.fdopen(fd, "wb", closefd=False) as stream:
                stream.write(data)
                stream.flush()
            os.lseek(fd, 0, os.SEEK_SET)
            fcntl.fcntl(fd, fcntl.F_ADD_SEALS, fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL)
            return fd
        except BaseException:
            os.close(fd)
            raise

    def _execute(self, acquired, node, decision, directory):
        files, manifest = acquired["images"][node["id"]]
        directory.mkdir()
        self._write(directory / "image.json", manifest)
        fds = []
        try:
            args = ["--unshare-all", "--unshare-user", "--die-with-parent", "--new-session", "--clearenv", "--cap-drop", "ALL"]
            for key, value in sorted(self.environment.items()):
                args += ["--setenv", key, value]
            for name in sorted(set(manifest["directories"]) | {"/dev", "/tmp"}, key=lambda s: (s.count("/"), s)):
                args += ["--perms", "0755", "--dir", name]
            for name, (data, mode) in sorted(files.items()):
                fd = self._sealed(data)
                fds.append(fd)
                args += ["--perms", oct(mode)[2:], "--ro-bind-data", str(fd), name]
            seccomp_fd = self._sealed(self.SECCOMP)
            fds.append(seccomp_fd)
            args += ["--dev-bind", "/dev/null", "/dev/null", "--size", str(self.LIMITS["scratch_bytes"]), "--tmpfs", "/tmp",
                     "--remount-ro", "/", "--chdir", "/work", "--seccomp", str(seccomp_fd)]
            command = ["/usr/bin/bash", "--noprofile", "--norc", "/work/scripts/run-work-graph-verifier.sh",
                       "--isolated-leaf", node["id"], node["source"], node["source_sha256"]]
            args_fd = self._sealed(b"\0".join(a.encode() for a in args) + b"\0")
            fds.append(args_fd)
            if max(fds) >= self.LIMITS["descriptors"]:
                raise WG.WorkGraphError("snapshot exceeds supported descriptor budget")
            self._write(directory / "dispatch.json", dict(node=node["id"], command=node["source"],
                        command_sha256=node["source_sha256"], input_key=decision["key"],
                        image_digest=acquired["acquired"]["inputs"][node["id"]]["image_digest"],
                        descriptor_count=len(fds), descriptor_custody="SEALED_INPUTS_ONLY_CLOSED_BEFORE_CHECKER"))
            def limits():
                resource.setrlimit(resource.RLIMIT_CPU, (self.LIMITS["cpu_seconds"],) * 2)
                resource.setrlimit(resource.RLIMIT_AS, (self.LIMITS["address_bytes"],) * 2)
                resource.setrlimit(resource.RLIMIT_FSIZE, (self.LIMITS["file_bytes"],) * 2)
                resource.setrlimit(resource.RLIMIT_NOFILE, (self.LIMITS["descriptors"],) * 2)
            code, complete, process = None, False, None
            with (directory / "stdout.log").open("xb") as stdout, (directory / "stderr.log").open("xb") as stderr:
                try:
                    try:
                        process = subprocess.Popen(["/usr/bin/bwrap", "--args", str(args_fd), *command], stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr, env=self.environment, close_fds=True, pass_fds=tuple(fds),
                                preexec_fn=limits, start_new_session=True)
                    except (OSError, subprocess.SubprocessError) as exc:
                        self._write(directory / "launch-error.json", dict(error=type(exc).__name__, detail=str(exc),
                                launch_phase="POPEN_DID_NOT_RETURN", checker_started="UNOBSERVED",
                                actual_exit="UNOBSERVED"))
                        raise
                    self.dispatch_count += 1
                    try:
                        code = process.wait(timeout=self.LIMITS["wall_seconds"])
                        complete = True
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # The child may already have exited; collect its actual status.
                        code = process.wait()
                except BaseException:
                    if process is not None:
                        if process.poll() is None:
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        code = process.wait()
                    raise
                finally:
                    # Preserve actual status even when interruption or a later
                    # observer failure prevents a receipt. Timeout stays incomplete.
                    if code is not None:
                        self._write(directory / "exit-code.txt", (str(code) + "\n").encode())
                    stdout.flush()
                    stderr.flush()
                    os.fsync(stdout.fileno())
                    os.fsync(stderr.fileno())
        finally:
            for fd in fds:
                os.close(fd)
        raw = {name: self._regular(directory / name)[1] for name in ("stdout.log", "stderr.log", "exit-code.txt", "image.json", "dispatch.json")}
        result = dict(schema="implementaudit.verifier-issued-result.v1", scope=acquired["acquired"]["scope"],
                      producer=self.producer, node=node["id"], key=decision["key"], dispatch=self.dispatch_count,
                      source_digest=self._object(self._encode(acquired["state"])), exit=code, complete=complete,
                      stdout_sha256=sha(raw["stdout.log"]), stderr_sha256=sha(raw["stderr.log"]),
                      semantic_artifacts=[], authority="NONE")
        raw["receipt.json"] = self._encode(result)
        self._write(directory / "receipt.json", raw["receipt.json"])
        required = [member["sha256"] for member in manifest["files"]] + [result["source_digest"], manifest["seccomp_sha256"]]
        if "directory_membership" in manifest:
            required.append(acquired["acquired"]["inputs"][node["id"]]["image_digest"])
        return result, dict(key=decision["key"], directory=directory, retained=raw,
                            required_objects=required, observed_at=time.monotonic())

    def run(self):
        """Acquire at consumption, execute or replay issued raw bytes, then join."""
        if os.getpid() != self.producer_pid:
            raise WG.WorkGraphError("producer process changed; receipt import is unsupported")
        self.generation += 1
        directory = self.output / ("generation-%06d" % self.generation)
        directory.mkdir()
        _, refused_at_entry = self._issued_keys()
        for node in refused_at_entry:
            self._issued.pop(node, None)
        start = self._acquire()
        source_digest = self._object(self._encode(start["state"]))
        self._write(directory / "acquisition.json", start["acquired"])
        self._write(directory / "mapping.json", start["graph"])
        issued, refused = self._issued_keys()
        refused.update(refused_at_entry)
        plan = WG.compile_verifier_reuse_v1(start["graph"], start["registry"], start["acquired"], issued)
        self._write(directory / "plan.json", plan)
        mapped = {n["id"]: n for n in start["graph"]["nodes"]}
        nodes, aggregate_stdout, aggregate_stderr, consumed = [], b"", b"", {}
        for index, decision in enumerate(plan["nodes"]):
            current = self._acquire()
            self._require_same(start, current, directory, "before-consumption-%02d" % index)
            keys, last_refusals = self._issued_keys()
            refused.update(last_refusals)
            refreshed = WG.compile_verifier_reuse_v1(current["graph"], current["registry"], current["acquired"], keys)
            self._write(directory / ("consumption-%02d-plan.json" % index), refreshed)
            decision = refreshed["nodes"][index]
            node = decision["node"]
            if decision["decision"] == "CONSUME_PRIOR_SUCCESS":
                retained = self._issued[node]
                result = WG.decode_strict_json_bytes(retained["retained"]["receipt.json"], "issued result")
                disposition = "REUSED"
            else:
                self._issued.pop(node, None)
                result, retained = self._execute(current, mapped[node], decision, directory / ("node-%02d" % index))
                disposition = "EXECUTED"
            after = self._acquire()
            self._require_same(current, after, directory, "during-consumption-%02d" % index)
            consumed[node] = retained
            evidence_refused = {}
            # Reacquisition can outlive or overlap changes to any result already
            # consumed in this join, including the newly executed result.
            for consumed_node, evidence in consumed.items():
                try:
                    self._verify_retained_result(evidence)
                except (OSError, WG.WorkGraphError) as exc:
                    self._issued.pop(consumed_node, None)
                    evidence_refused[consumed_node] = str(exc)
            if evidence_refused:
                self._write(directory / ("consumption-%02d-evidence-refusal.json" % index), evidence_refused)
                raise WG.WorkGraphError("issued evidence changed during consumption: " + str(evidence_refused))
            if result["exit"] == 0 and result["complete"]:
                self._issued[node] = retained
            aggregate_stdout += retained["retained"]["stdout.log"]
            aggregate_stderr += retained["retained"]["stderr.log"]
            nodes.append(dict(node=node, disposition=disposition, exit=result["exit"], complete=result["complete"],
                              consumed_plan_digest=refreshed["digest"],
                              key=decision["key"], original_source_digest=result["source_digest"],
                              receipt_digest=sha(retained["retained"]["receipt.json"]),
                              evidence_directory=str(retained["directory"])))
        code = 0 if all(n["exit"] == 0 and n["complete"] for n in nodes) else 1
        self._write(directory / "stdout.log", aggregate_stdout)
        self._write(directory / "stderr.log", aggregate_stderr)
        self._write(directory / "exit-code.txt", (str(code) + "\n").encode())
        result = dict(schema="implementaudit.verifier-task-consumption.v1", scope=self.SCOPE,
                      producer=self.producer, generation=self.generation, source_digest=source_digest,
                      initial_plan_digest=plan["digest"], nodes=nodes, exit=code, dispatch_count=self.dispatch_count,
                      refused_cached_outputs=refused, omitted_canonical_nodes=plan["omitted_canonical_nodes"],
                      canonical_acceptance="UNQUALIFIED", authority="NONE")
        self._write(directory / "result.json", result)
        return copy.deepcopy(result)


class RegistryVerifierTaskSession(VerifierTaskSession):
    """Explicit three-leaf scope; the historical two-leaf API is unchanged."""
    SCOPE = "CONTROLLED_TASK_REGISTRY_V1"
    CONTRACTS = WG.VERIFIER_REGISTRY_CONTRACTS_V1

    def __init__(self, source_root, output, **kwargs):
        registry_membership_v1(source_root)  # Refuse aliases before base resolution.
        super().__init__(source_root, output, **kwargs)


_PREFIX_PROFILES = {}


def create_composed_prefix_session(source_root, output, *, max_age=3600,
                                  profile="COMPOSED_SOURCE_PREFIX_23_V1"):
    """Explicit finite original prefix; live producer only, no imported receipts.

    Lazy loading keeps historical captures and the original scoped API free of
    this repository-only companion. The loaded bytes remain engine-bound at
    every acquisition and receiving boundary.
    """
    if type(profile) is not str:
        raise WG.WorkGraphError("unsupported composed-prefix profile")
    if profile not in _PREFIX_PROFILES:
        path = ROOT / "scripts/qualify-work-graph-prefix.py"
        data = VerifierTaskSession._regular(path)[1]
        spec = importlib.util.spec_from_file_location("verifier_prefix", path)
        module = importlib.util.module_from_spec(spec)
        exec(compile(data, str(path), "exec"), module.__dict__)
        _PREFIX_PROFILES[profile] = module.bind_session(VerifierTaskSession, WG, ROOT, data, profile=profile)
    return _PREFIX_PROFILES[profile](source_root, output, max_age=max_age)


def _preflight_git_file_v1(path, *, required=False, byte_limit=65536):
    """Acquire a selected control file before Git can interpret it."""
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise WG.WorkGraphError("preflight Git observation requires canonical control paths")
    for parent in reversed((path, *path.parents)):
        try:
            metadata = parent.lstat()
        except FileNotFoundError:
            if required:
                raise WG.WorkGraphError("preflight Git observation control file is unavailable") from None
            return dict(path=str(path), kind="MISSING", missing_at=str(parent)), None
        if stat.S_ISLNK(metadata.st_mode) or (parent != path and not stat.S_ISDIR(metadata.st_mode)):
            raise WG.WorkGraphError("preflight Git observation refuses aliased control paths")
    if not stat.S_ISREG(metadata.st_mode):
        raise WG.WorkGraphError("preflight Git observation requires regular control files")
    value = source_member(str(path.relative_to(path.anchor)), root=Path(path.anchor),
                          with_bytes=True, byte_limit=byte_limit)
    if value.get("kind") != "FILE":
        raise WG.WorkGraphError("preflight Git observation control file changed")
    data = value.pop("_acquired_bytes")
    return dict(path=str(path), **value), data


def _preflight_git_config_v1(data):
    """A deliberately finite Git-config subset, not a permissive Git parser.

    Includes, escaped/continued values, callbacks, external helpers and unknown
    keys are unsupported. No Git process is used to inspect unadmitted config.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise WG.WorkGraphError("preflight Git observation refuses unsupported configuration syntax") from None
    if "\\" in text or "\0" in text:
        raise WG.WorkGraphError("preflight Git observation refuses unsupported configuration syntax")
    choices = {
        "core.repositoryformatversion": {"0", "1"}, "core.bare": {"false"},
        "core.filemode": {"true", "false"}, "core.logallrefupdates": {"true", "false"},
        "core.ignorecase": {"true", "false"}, "core.precomposeunicode": {"true", "false"},
        "core.symlinks": {"true", "false"}, "core.trustctime": {"true", "false"},
        "core.checkstat": {"default", "minimal"}, "core.autocrlf": {"true", "false", "input"},
        "core.safecrlf": {"true", "false", "warn"}, "core.eol": {"lf", "crlf", "native"},
        "core.fsmonitor": {"false"}, "core.untrackedcache": {"false"},
        "core.hookspath": {"/dev/null"}, "core.attributesfile": {"/dev/null"},
        "core.excludesfile": {"/dev/null"}, "extensions.worktreeconfig": {"true", "false"},
        "commit.gpgsign": {"false"}}
    values, section, subsection = {}, None, None
    for line in text.split("\n"):
        line = line.removesuffix("\r")
        if not line.strip(" \t") or line.lstrip(" \t").startswith(("#", ";")):
            continue
        header = re.fullmatch(r'[ \t]*\[([A-Za-z][A-Za-z0-9-]*)(?: "([A-Za-z0-9][A-Za-z0-9._/-]{0,127})")?\][ \t]*(?:[#;].*)?', line)
        if header:
            section, subsection = header.group(1).lower(), header.group(2)
            continue
        entry = re.fullmatch(r'[ \t]*([A-Za-z][A-Za-z0-9-]*)[ \t]*=[ \t]*("[^"\\\x00-\x1f]*"|[^"\\#;\x00-\x1f]*?)[ \t]*(?:[#;].*)?', line)
        if entry is None or section is None:
            raise WG.WorkGraphError("preflight Git observation refuses unsupported configuration syntax")
        key, value = entry.group(1).lower(), entry.group(2).strip(" \t")
        if value.startswith('"'):
            value = value[1:-1]
        name = section + "." + key
        metadata = ((subsection is None and name in {"user.name", "user.email", "init.defaultbranch"}) or
                    (subsection is not None and ((section == "remote" and key in {"url", "fetch"}) or
                                                (section == "branch" and key in {"remote", "merge"}))))
        if not (metadata or (subsection is None and name in choices and value in choices[name])):
            raise WG.WorkGraphError("preflight Git observation refuses unsupported or effect-bearing configuration")
        values[name if subsection is None else section + "." + subsection + "." + key] = value
    return values


def _preflight_git_index_v1(data):
    """Admit inline SHA-1 indexes before Git can touch a shared-index file.

    Decode entry boundaries, not a substring search: ordinary filenames and
    object IDs may contain 'link'. This does not interpret split-index data.
    """
    error = "preflight Git observation refuses malformed or unsupported index structure"
    end = len(data) - 20
    if (end < 12 or data[:4] != b"DIRC" or
            hashlib.sha1(data[:end]).digest() != data[end:]):
        raise WG.WorkGraphError(error)
    version, entries = struct.unpack_from(">II", data, 4)
    if version not in {2, 3, 4} or entries > (end - 12) // 63:
        raise WG.WorkGraphError(error)
    offset, previous_length = 12, 0
    for _ in range(entries):
        start = offset
        if offset + 62 > end:
            raise WG.WorkGraphError(error)
        flags = struct.unpack_from(">H", data, offset + 60)[0]
        offset += 62
        if flags & 0x4000:
            if version == 2 or offset + 2 > end or struct.unpack_from(">H", data, offset)[0] & ~0x6000:
                raise WG.WorkGraphError(error)
            offset += 2
        removed = 0
        if version == 4:
            for position in range(5):
                if offset >= end:
                    raise WG.WorkGraphError(error)
                byte = data[offset]
                offset += 1
                removed = ((removed + 1) << 7 if position else 0) + (byte & 0x7f)
                if not byte & 0x80:
                    break
            else:
                raise WG.WorkGraphError(error)
            if removed > previous_length:
                raise WG.WorkGraphError(error)
        nul = data.find(b"\0", offset, end)
        if nul < 0:
            raise WG.WorkGraphError(error)
        length = nul - offset + (previous_length - removed if version == 4 else 0)
        if flags & 0xfff != min(length, 0xfff):
            raise WG.WorkGraphError(error)
        previous_length = length
        offset = nul + 1 if version == 4 else start + ((nul + 1 - start + 7) // 8) * 8
        if offset > end or any(data[nul:offset]):
            raise WG.WorkGraphError(error)
    extensions = []
    while offset < end:
        if offset + 8 > end:
            raise WG.WorkGraphError(error)
        signature = data[offset:offset + 4]
        size = struct.unpack_from(">I", data, offset + 4)[0]
        offset += 8
        if signature == b"link":
            raise WG.WorkGraphError("preflight Git observation refuses split-index indirection")
        if signature not in {b"TREE", b"REUC"}:
            raise WG.WorkGraphError("preflight Git observation refuses unsupported index extension")
        if size > end - offset or signature.decode("ascii") in extensions:
            raise WG.WorkGraphError(error)
        extensions.append(signature.decode("ascii"))
        offset += size
    return dict(profile="INLINE_SHA1_V2_V3_V4_TREE_REUC", version=version,
                entries=entries, extensions=extensions)


def _preflight_git_context_v1():
    """Admit the actual declared context; never silently discard Git config.

    The caller must already have excluded system/global config and system
    attributes in the intended run environment. Other selectors are refused.
    The finite local config subset and physical selections are digest-bound.
    """
    require_source_descriptor_api()
    environment = dict(os.environ)
    required = dict(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_ATTR_NOSYSTEM="1")
    allowed = dict(required, GIT_OPTIONAL_LOCKS=None, GIT_PAGER=None)
    if (platform.system() != "Linux" or not Path("/proc/self/fd").is_dir() or
            any(environment.get(key) != value for key, value in required.items()) or
            any(key.startswith("GIT_") and key not in allowed for key in environment) or
            any(key.startswith(("LD_", "DYLD_")) or key == "GCONV_PATH" for key in environment) or
            environment.get("GIT_OPTIONAL_LOCKS", "0") not in {"0", "1"} or
            any(environment.get(key, "") not in {"", "cat"} for key in ("GIT_PAGER", "PAGER"))):
        raise WG.WorkGraphError("preflight Git observation requires the declared isolated configuration/environment profile")
    null = Path("/dev/null").stat()
    if not stat.S_ISCHR(null.st_mode) or (os.major(null.st_rdev), os.minor(null.st_rdev)) != (1, 3):
        raise WG.WorkGraphError("preflight Git observation null device is unsupported")
    lookup = os.pathsep.join(str(Path(part) if Path(part).is_absolute() else ROOT / part)
                             for part in environment.get("PATH", os.defpath).split(os.pathsep))
    selected = shutil.which("git", path=lookup)
    if selected is None or str(Path(selected).resolve()) not in {"/usr/bin/git", "/usr/local/bin/git"}:
        raise WG.WorkGraphError("preflight Git observation refuses unsupported executable selection")
    executable = executable_identity(selected)
    binary = Path(executable["resolved_path"])
    metadata = binary.stat()
    if metadata.st_uid != 0 or stat.S_IMODE(metadata.st_mode) & 0o022:
        raise WG.WorkGraphError("preflight Git observation requires a system-owned Git executable")
    with binary.open("rb") as stream:
        if stream.read(4) != b"\x7fELF":
            raise WG.WorkGraphError("preflight Git observation refuses Git executable wrappers")
    controls = []

    def acquire(path, **options):
        record, data = _preflight_git_file_v1(path, **options)
        controls.append(record)
        return data

    marker = ROOT / ".git"
    state = marker.lstat()
    if stat.S_ISDIR(state.st_mode):
        gitdir = marker
        controls.append(dict(path=str(marker), kind="DIRECTORY", mode=stat.S_IMODE(state.st_mode)))
    elif stat.S_ISREG(state.st_mode):
        raw = acquire(marker, required=True)
        if re.fullmatch(rb"gitdir: [^\x00-\x1f\x7f]+\r?\n?", raw) is None:
            raise WG.WorkGraphError("preflight Git observation refuses unsupported Git directory selection")
        declared = Path(os.fsdecode(raw[8:].rstrip(b"\r\n")))
        gitdir = Path(os.path.abspath(declared if declared.is_absolute() else ROOT / declared))
    else:
        raise WG.WorkGraphError("preflight Git observation refuses aliased Git directory selection")
    raw = acquire(gitdir / "commondir")
    common = gitdir
    if raw is not None:
        if re.fullmatch(rb"[^\x00-\x1f\x7f]+\r?\n?", raw) is None:
            raise WG.WorkGraphError("preflight Git observation refuses unsupported common directory selection")
        declared = Path(os.fsdecode(raw.rstrip(b"\r\n")))
        common = Path(os.path.abspath(declared if declared.is_absolute() else gitdir / declared))
    config = _preflight_git_config_v1(acquire(common / "config", required=True))
    worktree_config = config.get("extensions.worktreeconfig") == "true"
    if worktree_config:
        raw = acquire(gitdir / "config.worktree")
        if raw is not None:
            config.update(_preflight_git_config_v1(raw))
    acquire(gitdir / "HEAD", required=True)
    index_format = _preflight_git_index_v1(acquire(gitdir / "index", required=True, byte_limit=EXPLICIT_FILE_LIMIT))
    for directory in sorted({gitdir, common}):
        for name in ("info/attributes", "info/exclude"):
            acquire(directory / name)
    home = Path(environment.get("HOME", ""))
    xdg = Path(environment.get("XDG_CONFIG_HOME") or home / ".config")
    if not home.is_absolute() or not xdg.is_absolute() or ".." in xdg.parts:
        raise WG.WorkGraphError("preflight Git observation refuses unsupported user attribute/exclude selection")
    for key, filename in (("core.attributesfile", "attributes"), ("core.excludesfile", "ignore")):
        if config.get(key) != "/dev/null":
            acquire(xdg / "git" / filename)
    binding = dict(policy="DECLARED_ISOLATED_GIT_CONFIG_V1", executable=executable,
                   executable_file_identity=[str(value) for value in _file_identity(metadata)],
                   git_directory=str(gitdir), common_directory=str(common), worktree_config=worktree_config,
                   index_format=index_format,
                   controls=controls, declared_environment_sha256=environment_digest(environment),
                   observation_overrides=dict(GIT_OPTIONAL_LOCKS="0"), pager="DISABLED_BY_EXPLICIT_ARGUMENT",
                   configuration_scope="NO_INCLUDES_NO_EXTERNAL_CALLBACKS_FINITE_KEYS",
                   continuity="PRE_POST_REACQUISITION_NOT_AN_ATOMIC_FILESYSTEM_LEASE")
    return dict(binding=binding, environment=dict(environment, GIT_OPTIONAL_LOCKS="0"))


def _preflight_git_capture_v1(context, args):
    allowed = {("ls-files", "-z"), ("ls-files", "--others", "--exclude-standard", "-z"),
               ("ls-files", "--stage", "-z"), ("rev-parse", "HEAD"), ("rev-parse", "HEAD^{tree}"),
               ("rev-parse", "--symbolic-full-name", "HEAD"),
               ("status", "--porcelain=v1", "-z", "--untracked-files=all"),
               ("for-each-ref", "--sort=refname", "--format=%(refname)%00%(objectname)%00%(*objectname)%00%(symref)")}
    if args not in allowed or _preflight_git_context_v1() != context:
        raise WG.WorkGraphError("preflight Git observation context or fixed command changed")
    selected = context["binding"]["executable"]["resolved_path"]
    fd = os.open(selected, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        if [str(value) for value in _file_identity(os.fstat(fd))] != context["binding"]["executable_file_identity"]:
            raise WG.WorkGraphError("preflight Git observation executable changed")
        try:
            value = subprocess.check_output([selected, "--no-pager", *args], cwd=ROOT,
                env=context["environment"], stdin=subprocess.DEVNULL, stderr=subprocess.PIPE,
                executable="/proc/self/fd/" + str(fd), pass_fds=(fd,), timeout=15)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            raise WG.WorkGraphError("preflight Git observation fixed read command failed") from None
    finally:
        os.close(fd)
    if _preflight_git_context_v1() != context:
        raise WG.WorkGraphError("preflight Git observation context changed during command")
    return value


def verifier_preflight_currentness_v1():
    """Read current bindings without launching a subject verifier command.

    Git observation commands may run. This snapshot is neither a launch lease
    nor a complete filesystem/toolchain acquisition.
    """
    engine = full_engine_binding()
    source = source_identity(read_only=True)
    git_observation = source.pop("_git_observation_sha256")
    environment = environment_digest(os.environ)
    if full_engine_binding() != engine:
        raise WG.WorkGraphError("preflight loaded engine changed during observation")
    return dict(source_sha256=sha(WG.canonical_json_v1(source)), engine_binding=engine,
                base_environment_sha256=environment, git_observation_sha256=git_observation)


def _preflight_fields(value, names, label):
    if type(value) is not dict or set(value) != set(names):
        raise WG.WorkGraphError("preflight " + label + " has missing or unsupported members")


def _preflight_path(value, label):
    if (type(value) is not str or len(value.encode("utf-8")) > 4096 or
            any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise WG.WorkGraphError("preflight " + label + " requires a bounded absolute path")
    path = Path(value)
    if (not path.is_absolute() or ".." in path.parts or str(path) != value or
            str(path.resolve()) != value):
        raise WG.WorkGraphError("preflight " + label + " requires a canonical absolute path without aliases")
    return path


def _preflight_capture_identity_v1(route, actual_base):
    capture, output = route["capture"], route["output"]
    events = capture["capture_portal_events"] or capture["retain_repro_events"]
    extended = events or any(capture[key] for key in
        ("retain_repro_assets", "stdin_file", "empty_stdin", "capture_dist"))
    overrides = repro_overrides(output) if capture["retain_repro_assets"] else {}
    if capture["capture_portal_events"]:
        overrides[PORTAL_ENV] = output + "/portal-events/request.json"
    if capture["retain_repro_events"]:
        overrides[REPRO_EVENT_ENV] = output + "/repro-events"
    base = route["base_environment_sha256"]
    # A different declared base is not acquired by this process. Only its
    # declared base identity (and no inferred override result) is comparable.
    actual = environment_digest(dict(os.environ, **overrides)) if base == actual_base else (
        base if not overrides else None)
    return dict(schema="implementaudit.verifier-run.v4" if events else
                "implementaudit.verifier-run.v3" if extended else "implementaudit.verifier-run.v2",
                extended=bool(extended), environment_sha256=actual,
                child_environment=dict(base_environment_sha256=base,
                    actual_environment_sha256=actual, overrides=overrides) if extended else None,
                repro_paths=repro_overrides(output) if capture["retain_repro_assets"] else None,
                dist_paths=[output + "/dist-before", output + "/dist-after"] if capture["capture_dist"] else None,
                stdin=None if not (capture["empty_stdin"] or capture["stdin_file"] is not None) else
                    dict(mode="EMPTY_PIPE" if capture["empty_stdin"] else "RETAINED_FILE_PIPE",
                         declared_path=capture["stdin_file"]),
                portal_requested=capture["capture_portal_events"], repro_requested=capture["retain_repro_events"])


def preflight_verifier_pair_v1(plan):
    """Diagnose a bound paired plan; never execute, authorize, or claim equality."""
    encoded = WG.canonical_json_v1(plan)
    if len(encoded) > 65536:
        raise WG.WorkGraphError("preflight plan exceeds byte limit")
    plan = WG.decode_strict_json_bytes(encoded, "preflight plan")
    _preflight_fields(plan, {"schema", "expected_currentness", "runs"}, "plan")
    if plan["schema"] != "implementaudit.verifier-pair-plan.v1":
        raise WG.WorkGraphError("preflight plan schema is unsupported")
    expected = plan["expected_currentness"]
    _preflight_fields(expected, {"source_sha256", "engine_binding", "base_environment_sha256",
                                "git_observation_sha256"}, "currentness")
    _preflight_fields(expected["engine_binding"], {"driver_sha256", "compiler_sha256"}, "engine binding")
    digests = [expected["source_sha256"], expected["base_environment_sha256"],
               expected["git_observation_sha256"], *expected["engine_binding"].values()]
    routes = plan["runs"]
    if type(routes) is not list or len(routes) != 2:
        raise WG.WorkGraphError("preflight route pair requires exactly legacy and dag")
    options = {"retain_repro_assets", "stdin_file", "empty_stdin", "capture_dist",
               "capture_portal_events", "retain_repro_events"}
    for route in routes:
        _preflight_fields(route, {"mode", "output", "base_environment_sha256", "capture"}, "route")
        if type(route["mode"]) is not str or route["mode"] not in {"legacy", "dag"}:
            raise WG.WorkGraphError("preflight route pair requires exactly legacy and dag")
        _preflight_path(route["output"], "output")
        digests.append(route["base_environment_sha256"])
        capture = route["capture"]
        _preflight_fields(capture, options, "capture")
        if any(type(capture[key]) is not bool for key in options - {"stdin_file"}):
            raise WG.WorkGraphError("preflight capture options require booleans")
        if capture["stdin_file"] is not None:
            _preflight_path(capture["stdin_file"], "stdin")
            if capture["empty_stdin"]:
                raise WG.WorkGraphError("preflight stdin-file and empty-stdin are mutually exclusive")
    if {r["mode"] for r in routes} != {"legacy", "dag"}:
        raise WG.WorkGraphError("preflight route pair requires exactly legacy and dag")
    if any(type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None for value in digests):
        raise WG.WorkGraphError("preflight currentness requires complete SHA-256 bindings")
    before = verifier_preflight_currentness_v1()
    reasons, false = set(), set()
    identities = {r["mode"]: _preflight_capture_identity_v1(r, before["base_environment_sha256"]) for r in routes}
    outputs = [Path(r["output"]) for r in routes]
    if outputs[0] == outputs[1] or outputs[0] in outputs[1].parents or outputs[1] in outputs[0].parents:
        reasons.add("OUTPUT_NAMESPACE_COLLISION")
    for route, output in zip(routes, outputs):
        capture, identity = route["capture"], identities[route["mode"]]
        if route["base_environment_sha256"] != before["base_environment_sha256"]:
            reasons.add("PLANNED_ENVIRONMENT_NOT_CURRENT")
        if os.path.lexists(output):
            reasons.add("OUTPUT_ALREADY_EXISTS")
        if identity["extended"] and (output == ROOT or ROOT in output.parents):
            reasons.add("EXTENDED_OUTPUT_INSIDE_SOURCE")
        if (REPRO_EVENT_ENV in os.environ or
                capture["retain_repro_assets"] and any(k == "REPRO_SOURCE_REF" or k.startswith("REPRO_RETAINED_") for k in os.environ) or
                capture["capture_portal_events"] and PORTAL_ENV in os.environ or
                capture["retain_repro_events"] and "REPRO_SOURCE_REF" in os.environ):
            reasons.add("AMBIGUOUS_INHERITED_CAPTURE_ENVIRONMENT")
    a, b = identities["legacy"], identities["dag"]
    if a["schema"] != b["schema"]:
        false.add("same_record_schema")
    if (a["environment_sha256"] is not None and b["environment_sha256"] is not None and
            a["environment_sha256"] != b["environment_sha256"]):
        false.add("same_environment")
    if a["schema"] == b["schema"] and a["extended"]:
        for predicate, field in (("same_child_environment", "child_environment"),
                ("same_declared_repro_artifacts", "repro_paths"), ("same_dist_namespace", "dist_paths"),
                ("same_stdin", "stdin")):
            if a[field] != b[field]:
                false.add(predicate)
        if a["schema"] == "implementaudit.verifier-run.v4":
            for predicate, field in (("same_portal_events", "portal_requested"), ("same_repro_events", "repro_requested")):
                if a[field] != b[field]:
                    false.add(predicate)
    after = verifier_preflight_currentness_v1()
    mismatches = sorted(key for key in expected if expected[key] != before[key] or expected[key] != after[key])
    if expected != before:
        reasons.add("EXPECTED_CURRENTNESS_MISMATCH")
    if before != after:
        reasons.add("CURRENTNESS_CHANGED_DURING_PREFLIGHT")
    if false:
        reasons.add("SELECTED_RAW_ORACLE_PRECONDITION_UNSATISFIED")
    predicates = {"same_source", "same_registry", "same_environment", "same_record_schema", "same_exit",
        "same_stdout", "same_stderr", "route_pair", "same_engine", "same_execution_cwd", "same_compiled_stream",
        "same_child_environment", "same_declared_repro_artifacts", "same_stdin", "same_dist_namespace",
        "same_portal_events", "same_repro_events"}
    return dict(schema="implementaudit.verifier-pair-preflight.v1",
        status="BLOCKED" if reasons else "NECESSARY_PRECONDITIONS_ONLY", subject_launches=0,
        plan_canonical_sha256=sha(encoded), currentness=dict(expected=expected, observed_before=before,
            observed_after=after, matches=expected == before == after, mismatches=mismatches,
            scope="PRE_POST_OBSERVATIONS_NOT_A_LAUNCH_LEASE",
            git_observation_policy="DECLARED_ISOLATED_GIT_CONFIG_V1"),
        blocking_reasons=sorted(reasons), guaranteed_false_predicates=sorted(false),
        planned_capture_identities=identities, unqualified_predicates=sorted(predicates - false),
        raw_observables_equal=None, normalization="NONE_RAW_BYTES", authority="NONE",
        evidence_scope="PLANNED_INPUTS_ONLY_NO_EXECUTION",
        remaining_identity_observations="DISTINCT_RUN_IDS_PROCESS_CLOCK_FILESYSTEM_AND_RAW_OUTPUTS_UNQUALIFIED")


def preflight_verifier_pair_file_v1(path):
    path = path.absolute()
    try:
        observed = source_member(path.relative_to("/").as_posix(), root=Path("/"), with_bytes=True, byte_limit=65536)
    except WG.WorkGraphError as exc:
        if str(exc) == "explicit member exceeds byte limit":
            raise WG.WorkGraphError("preflight plan exceeds byte limit") from exc
        raise
    if observed.get("kind") != "FILE":
        raise WG.WorkGraphError("preflight plan requires a no-follow regular file")
    data = observed["_acquired_bytes"]
    result = preflight_verifier_pair_v1(WG.decode_strict_json_bytes(data, "preflight plan"))
    result["plan_file_sha256"] = sha(data)
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "BLOCKED" else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["legacy", "dag", "compare", "preflight", "scoped", "registry", "prefix", "prefix24"])
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--retain-repro-assets", action="store_true")
    parser.add_argument("--capture-dist", action="store_true")
    parser.add_argument("--retain-portal-events", "--capture-portal-events", dest="capture_portal_events", action="store_true")
    parser.add_argument("--retain-repro-events", action="store_true")
    stdin = parser.add_mutually_exclusive_group()
    stdin.add_argument("--stdin-file")
    stdin.add_argument("--empty-stdin", action="store_true")
    args = parser.parse_args()
    try:
        if args.mode not in {"legacy", "dag"} and (args.retain_repro_assets or args.stdin_file is not None or args.empty_stdin or args.capture_dist or args.capture_portal_events or args.retain_repro_events):
            raise WG.WorkGraphError("explicit acquisition options require a legacy or dag capture")
        if args.mode == "preflight" and len(args.paths) == 1:
            return preflight_verifier_pair_file_v1(args.paths[0])
        if args.mode in {"scoped", "registry", "prefix", "prefix24"} and len(args.paths) == 2:
            prefix_mode = args.mode in {"prefix", "prefix24"}
            if prefix_mode:
                profile = "COMPOSED_SOURCE_PREFIX_24_V1" if args.mode == "prefix24" else "COMPOSED_SOURCE_PREFIX_23_V1"
                session = create_composed_prefix_session(*args.paths, profile=profile)
            else:
                session = {"scoped": VerifierTaskSession, "registry": RegistryVerifierTaskSession}[args.mode](*args.paths)
            # A caller may request another current-source consumption, never
            # inject a receipt, plan, mutation command or claimed process exit.
            status = 0
            requests = iter(lambda: sys.stdin.buffer.readline(4097), b"") if prefix_mode else sys.stdin.buffer
            for line in requests:
                if prefix_mode and len(line) > 4096:
                    raise WG.WorkGraphError("prefix request exceeds its byte bound")
                if WG.decode_strict_json_bytes(line, "scope request") != {"operation": "run"}:
                    raise WG.WorkGraphError("only a current-source run request is supported")
                result = session.run()
                code = result["exit"]
                if prefix_mode and (code < 0 or not result["complete"]):
                    code = 1
                status = max(status, code)
                print(json.dumps(result, sort_keys=True), flush=True)
            return status
        if args.mode == "compare" and len(args.paths) == 3:
            return compare(*args.paths)
        if args.mode in {"legacy", "dag"} and len(args.paths) == 1:
            return run(args.mode, args.paths[0].resolve(), retain_repro_assets=args.retain_repro_assets,
                       stdin_file=args.stdin_file, empty_stdin=args.empty_stdin, capture_dist=args.capture_dist,
                       capture_portal_events=args.capture_portal_events, retain_repro_events=args.retain_repro_events)
        parser.error("run takes one fresh output directory; compare takes two run directories and a fresh result path; preflight takes one plan file")
    except (OSError, ValueError, KeyError, TypeError, WG.WorkGraphError, subprocess.SubprocessError) as exc:
        print("work-graph-verifier: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
