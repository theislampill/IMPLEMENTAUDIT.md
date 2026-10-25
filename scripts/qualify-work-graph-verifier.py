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

# The fixed README receiver supplies only source data from its complete,
# physically checked closure. No result/authority credential is accepted here.
_EFFECT_CAPTURE = globals().pop("_R0035_EFFECT_SOURCE_CAPTURE", None)
if _EFFECT_CAPTURE is None:
    ROOT = Path(__file__).resolve().parents[1]
    LOADED_DRIVER_PATH = Path(__file__).resolve()
    LOADED_DRIVER = LOADED_DRIVER_PATH.read_bytes()
    DRIVER_SOURCE_IDENTITY = "CURRENT_FILE_OBSERVATION_NOT_CAPTURE_ATTESTATION"
    LOADED_COMPILER_PATH = ROOT / "skills/implementaudit/scripts/compile-work-graph.py"
    LOADED_COMPILER = LOADED_COMPILER_PATH.read_bytes()
    LOADED_COMPILER_PATH = LOADED_COMPILER_PATH.resolve()
else:
    if (type(_EFFECT_CAPTURE) is not dict
            or set(_EFFECT_CAPTURE) != {"driver", "compiler", "expected_compiler_sha256"}
            or any(type(_EFFECT_CAPTURE[name]) is not bytes or not 0 < len(_EFFECT_CAPTURE[name]) <= 1024**2
                   for name in ("driver", "compiler"))
            or type(_EFFECT_CAPTURE["expected_compiler_sha256"]) is not str
            or re.fullmatch(r"[0-9a-f]{64}", _EFFECT_CAPTURE["expected_compiler_sha256"]) is None
            or hashlib.sha256(_EFFECT_CAPTURE["compiler"]).hexdigest()
               != _EFFECT_CAPTURE["expected_compiler_sha256"]):
        raise ValueError("invalid fixed-loader compiler source capture")
    LOADED_DRIVER_PATH = Path(__file__).absolute()
    ROOT = LOADED_DRIVER_PATH.parents[1]
    LOADED_DRIVER = _EFFECT_CAPTURE["driver"]
    DRIVER_SOURCE_IDENTITY = "CAPTURED_EXECUTED_BUFFER"
    LOADED_COMPILER_PATH = ROOT / "skills/implementaudit/scripts/compile-work-graph.py"
    LOADED_COMPILER = _EFFECT_CAPTURE["compiler"]
SPEC = importlib.util.spec_from_file_location("work_graph", ROOT / "skills/implementaudit/scripts/compile-work-graph.py")
WG = importlib.util.module_from_spec(SPEC)
exec(compile(LOADED_COMPILER, SPEC.origin, "exec"), WG.__dict__)
del _EFFECT_CAPTURE
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
# Aggregate retention bounds include the existing 64-event portal and two
# dist snapshots. These are additional opt-in custody bounds, not raw-oracle
# normalization or a claim that every possible capture fits them.
CAPTURE_RETENTION_LIMITS = dict(file_bytes=128 * 1024 * 1024, total_bytes=2 * 1024**3,
    entries=68 * 4096, depth=64, manifest_bytes=128 * 1024 * 1024)


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


class _CaptureChildren:
    """Linux child custody within this dedicated run owner, never a governor.

    Proc listings are cleanup discovery only. Only kernel all-child
    ECHILD establishes quiescence. No process-group or numeric-PID signal is
    used, including on the refusal path.
    """
    WALL = 0x40000000
    PR_SET_CHILD_SUBREAPER = 36
    PR_GET_CHILD_SUBREAPER = 37
    SCOPE = "DEDICATED_SINGLE_THREAD_LINUX_SUBREAPER; NO_FOREIGN_SAME_UID_WRITER_AUTHORITY"

    def __init__(self):
        # Keep the optional Linux owner out of ordinary and finite acquired
        # loader startup. Its libraries are needed only for this explicit path.
        try:
            import ctypes
            import threading
        except ImportError as exc:
            raise WG.WorkGraphError("capture retention's optional Linux owner libraries are unavailable") from exc
        self.ctypes, self.threading = ctypes, threading
        needed = ("waitid", "waitpid", "P_ALL", "P_PIDFD", "WNOWAIT", "WEXITED",
                  "WNOHANG", "pidfd_open", "waitstatus_to_exitcode", "fork", "pipe2",
                  "O_CLOEXEC", "CLD_EXITED", "CLD_KILLED", "CLD_DUMPED")
        if (sys.platform != "linux" or any(not hasattr(os, name) for name in needed) or
                not hasattr(signal, "pidfd_send_signal") or threading.current_thread() is not threading.main_thread()):
            raise WG.WorkGraphError("capture retention requires a Linux main-thread child/pidfd owner")
        self.pid = os.getpid()
        self.status = dict(owner_pid=self.pid, primary_pid=None, primary_exit=None,
            other_child_exits=[], owned_pidfd_signals=0, live_children_refused=False,
            quiescence="UNPROVED", flag_restored=False,
            scope=self.SCOPE)
        self.previous_handlers = {}
        self.active = False
        self.primary_fd = None
        self.primary_wait_missing = False
        self.exec_error = None
        self._scope()
        if signal.getsignal(signal.SIGCHLD) != signal.SIG_DFL:
            raise WG.WorkGraphError("capture retention requires default SIGCHLD and no competing reaper")
        # WNOWAIT does not consume a preexisting child's status. Any returned
        # result (including None for a live child) refuses this dedicated owner.
        try:
            os.waitid(os.P_ALL, 0, os.WEXITED | os.WNOHANG | os.WNOWAIT | self.WALL)
        except ChildProcessError:
            pass
        else:
            raise WG.WorkGraphError("capture retention refuses preexisting children")
        # Establish the required pidfd interfaces before a subject dispatch.
        # The descriptor refers to this owner; signal 0 has no signal effect.
        fd = os.pidfd_open(self.pid, 0)
        try:
            signal.pidfd_send_signal(fd, 0, None, 0)
            try:
                os.waitid(os.P_PIDFD, fd, os.WEXITED | os.WNOHANG | os.WNOWAIT | self.WALL)
            except ChildProcessError:
                pass  # This owner is not its own child.
            else:
                raise WG.WorkGraphError("capture pidfd child-wait semantics unavailable")
        finally:
            os.close(fd)
        self.libc = ctypes.CDLL(None, use_errno=True)
        self.prctl = getattr(self.libc, "prctl", None)
        if self.prctl is None:
            raise WG.WorkGraphError("capture child-subreaper interface unavailable")
        self.prctl.argtypes = [ctypes.c_int]  # prctl's remaining arguments are variadic.
        self.prctl.restype = ctypes.c_int
        self.previous_flag = self._get_flag()
        self.status["previous_subreaper"] = self.previous_flag
        try:
            self._set_flag(1)
        except BaseException:
            # No child has been created during entry. Restore even if SET
            # succeeded but its immediate GET observation failed.
            self._set_flag(self.previous_flag)
            raise
        self.active = True
        try:
            self._assert_owner()
            for name in (signal.SIGINT, signal.SIGTERM):
                self.previous_handlers[name] = signal.getsignal(name)
                signal.signal(name, self._interrupted)
        except BaseException:
            self.close()
            raise

    def _scope(self):
        # Fail closed rather than interpret a proc mount from a different PID
        # namespace as candidate task IDs in pidfd_open's calling namespace.
        if os.getpid() != self.pid or self.threading.current_thread() is not self.threading.main_thread():
            raise WG.WorkGraphError("capture child owner process/thread changed")
        status = Path("/proc/self/status").read_text()
        fields = {line.split(":", 1)[0]: line.split(":", 1)[1].split()
                  for line in status.splitlines() if ":" in line}
        if (Path("/proc/self/stat").read_text().split(" ", 1)[0] != str(self.pid) or
                fields.get("NSpid") != [str(self.pid)] or fields.get("NStgid") != [str(self.pid)] or
                fields.get("Threads") != ["1"] or os.listdir("/proc/self/task") != [str(self.pid)]):
            raise WG.WorkGraphError("capture retention requires one thread and a consistent single proc PID view")

    def _get_flag(self):
        ctypes = self.ctypes
        value = ctypes.c_int(-1)
        if self.prctl(ctypes.c_int(self.PR_GET_CHILD_SUBREAPER), ctypes.byref(value),
                      ctypes.c_ulong(0), ctypes.c_ulong(0), ctypes.c_ulong(0)) != 0 or value.value not in (0, 1):
            raise WG.WorkGraphError("capture child-subreaper readback unavailable")
        return value.value

    def _set_flag(self, value):
        ctypes = self.ctypes
        if (self.prctl(ctypes.c_int(self.PR_SET_CHILD_SUBREAPER), ctypes.c_ulong(value),
                       ctypes.c_ulong(0), ctypes.c_ulong(0), ctypes.c_ulong(0)) != 0 or self._get_flag() != value):
            raise WG.WorkGraphError("capture child-subreaper capability unavailable")

    def _assert_owner(self):
        self._scope()
        if self._get_flag() != 1 or signal.getsignal(signal.SIGCHLD) != signal.SIG_DFL:
            raise WG.WorkGraphError("capture child-wait ownership changed")

    def _interrupted(self, signum, frame):
        raise WG.WorkGraphError("capture run interrupted before sealing")

    def quiescent(self):
        self._assert_owner()
        if self.primary_fd is not None and self.status["primary_exit"] is None and not self.primary_wait_missing:
            try:
                primary = os.waitid(os.P_PIDFD, self.primary_fd, os.WEXITED | os.WNOHANG | self.WALL)
            except ChildProcessError:
                self.primary_wait_missing = True
            else:
                if primary is None:
                    self.status["quiescence"] = "LIVE_CHILDREN"
                    return False
                self._primary_terminal(primary)
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG | self.WALL)
            except ChildProcessError:
                self.status["quiescence"] = "ECHILD_ALL_CHILDREN"
                return True
            if pid == 0:
                self.status["quiescence"] = "LIVE_CHILDREN"
                return False
            if not (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                raise WG.WorkGraphError("capture child wait returned a nonterminal status")
            if len(self.status["other_child_exits"]) >= 4096:
                raise WG.WorkGraphError("capture adopted-child status bound exceeded")
            self.status["other_child_exits"].append(dict(pid=pid, exit=os.waitstatus_to_exitcode(status)))

    def require_quiescent(self):
        if not self.quiescent():
            self.status["live_children_refused"] = True
            raise WG.WorkGraphError("capture sealing refused: live owned descendants remain")

    def _primary_terminal(self, state):
        if state.si_pid != self.status["primary_pid"]:
            raise WG.WorkGraphError("capture primary pidfd wait identity changed")
        if state.si_code == os.CLD_EXITED:
            code = state.si_status
        elif state.si_code in (os.CLD_KILLED, os.CLD_DUMPED):
            code = -state.si_status
        else:
            raise WG.WorkGraphError("capture primary terminal wait status unavailable")
        self.status["primary_exit"] = code
        return code

    def launch(self, command, *, stdout, stderr, environment, base_environment, stdin_bytes):
        self.require_quiescent()
        if dict(os.environ) != base_environment:
            raise WG.WorkGraphError("capture currentness: actual base environment changed at dispatch")
        descriptors = []
        def pipe():
            pair = os.pipe2(os.O_CLOEXEC)
            descriptors.extend(pair)
            return pair

        def close(fd):
            if fd is not None and fd in descriptors:
                os.close(fd)
                descriptors.remove(fd)

        try:
            gate_read, gate_write = pipe()
            error_read, error_write = pipe()
            input_read, input_write = (None, None) if stdin_bytes is None else pipe()
            pid = os.fork()
            if pid == 0:
                try:
                    close(gate_write)
                    close(error_read)
                    close(input_write)
                    for name in ("SIGINT", "SIGTERM", "SIGPIPE", "SIGXFZ", "SIGXFSZ"):
                        if hasattr(signal, name):
                            signal.signal(getattr(signal, name), signal.SIG_DFL)
                    if os.read(gate_read, 1) != b"R":
                        os._exit(125)
                    close(gate_read)
                    os.chdir(ROOT)
                    if input_read is not None:
                        os.dup2(input_read, 0)
                        os.set_inheritable(0, True)
                    os.dup2(stdout.fileno(), 1)
                    os.dup2(stderr.fileno(), 2)
                    os.set_inheritable(1, True)
                    os.set_inheritable(2, True)
                    # The single-threaded child performs no Python teardown.
                    # Close inherited descriptors as the ordinary Popen route
                    # does, retaining only the close-on-exec error pipe.
                    fds = []
                    with os.scandir("/proc/self/fd") as entries:
                        for entry in entries:
                            if len(fds) >= 4096 or not entry.name.isdigit():
                                raise WG.WorkGraphError("capture child descriptor population is unsupported")
                            fds.append(int(entry.name))
                    for fd in fds:
                        if fd > 2 and fd != error_write:
                            try:
                                os.close(fd)
                            except OSError as exc:
                                if exc.errno != errno.EBADF:
                                    raise
                    os.execvpe(command[0], command, environment)
                except BaseException as exc:
                    number = exc.errno if isinstance(exc, OSError) and exc.errno is not None else errno.EINVAL
                    try:
                        os.write(error_write, (str(number) + "\n").encode("ascii"))
                    finally:
                        os._exit(126)
            self.status["primary_pid"] = pid
            self.status["quiescence"] = "UNPROVED"
            close(gate_read)
            close(error_write)
            close(input_read)
            # The real child is blocked before exec and cannot fork. Confirm
            # its stable descriptor and kernel child ownership before release;
            # no signal-disposition/PID-reuse assumption stands in for identity.
            self.primary_fd = os.pidfd_open(pid, 0)
            initial = os.waitid(os.P_PIDFD, self.primary_fd,
                os.WEXITED | os.WNOHANG | os.WNOWAIT | self.WALL)
            if initial is not None:
                raise WG.WorkGraphError("capture primary terminated before dispatch acquisition")
            if dict(os.environ) != base_environment:
                raise WG.WorkGraphError("capture currentness: actual base environment changed before child release")
            if os.write(gate_write, b"R") != 1:
                raise WG.WorkGraphError("capture primary dispatch gate failed")
            close(gate_write)
            error = os.read(error_read, 64)
            close(error_read)
            if error:
                if re.fullmatch(rb"[0-9]{1,5}\n", error) is None:
                    raise WG.WorkGraphError("capture primary exec observation is invalid")
                self.exec_error = int(error)
            if stdin_bytes is not None and not error:
                try:
                    remaining = memoryview(stdin_bytes)
                    while remaining:
                        written = os.write(input_write, remaining[:65536])
                        if written <= 0:
                            raise WG.WorkGraphError("capture stdin pipe stopped accepting acquired bytes")
                        remaining = remaining[written:]
                except BrokenPipeError:
                    pass
            close(input_write)
            # This actual kernel terminal status belongs to the acquired task
            # descriptor. ECHILD never becomes a synthetic exit 0.
            return self._primary_terminal(os.waitid(os.P_PIDFD, self.primary_fd, os.WEXITED | self.WALL))
        except ChildProcessError as exc:
            self.primary_wait_missing = True
            raise WG.WorkGraphError("capture primary terminal wait status unavailable") from exc
        finally:
            for fd in tuple(descriptors):
                close(fd)

    def _signal_owned_child(self, fd):
        try:
            state = os.waitid(os.P_PIDFD, fd, os.WEXITED | os.WNOHANG | os.WNOWAIT | self.WALL)
        except ChildProcessError:
            return  # Reused/nonchild discovery candidate: never signal it.
        if state is None:
            try:
                signal.pidfd_send_signal(fd, signal.SIGKILL, None, 0)
                self.status["owned_pidfd_signals"] += 1
            except ProcessLookupError:
                pass

    def _cleanup_candidates(self, deadline):
        """Bound discovery only; neither a proc entry nor its absence is proof."""
        self._scope()
        try:
            with Path("/proc/self/task/%d/children" % self.pid).open("rb") as discovery:
                raw = discovery.read(65537)
        except FileNotFoundError:
            # CONFIG_PROC_CHILDREN is optional. The coherent proc population
            # can supply candidate numbers, never ownership or quiescence.
            # Every returned candidate still requires a stable pidfd and the
            # kernel child-wait proof immediately before any signal.
            candidates = []
            count = size = 0
            with os.scandir("/proc") as entries:
                for entry in entries:
                    if time.monotonic() >= deadline:
                        break
                    item = os.fsencode(entry.name)
                    if not item.isdigit():
                        continue
                    count += 1
                    size += len(item) + 1
                    if count > 4096 or size > 65536:
                        raise WG.WorkGraphError("capture proc cleanup discovery exceeds bound")
                    pid = int(item)
                    if pid > 0 and pid != self.pid:
                        candidates.append(item)
        else:
            if len(raw) > 65536:
                raise WG.WorkGraphError("capture child cleanup discovery exceeds bound")
            candidates = raw.split()
            if len(candidates) > 4096 or any(not item.isdigit() for item in candidates):
                raise WG.WorkGraphError("capture child cleanup discovery is unsupported")
        self._scope()
        return candidates

    def close(self):
        if not self.active:
            return
        # Interrupts during a finite refusal cleanup do not create a second
        # cleanup owner. Uncatchable termination leaves an unsealed intent.
        for name in self.previous_handlers:
            signal.signal(name, signal.SIG_IGN)
        try:
            deadline = time.monotonic() + 3.0
            while not self.quiescent():
                self.status["live_children_refused"] = True
                if time.monotonic() >= deadline:
                    raise WG.WorkGraphError("capture cleanup incomplete; children remain, subreaper retained")
                self._scope()
                if self.primary_fd is not None and self.status["primary_exit"] is None:
                    self._signal_owned_child(self.primary_fd)
                candidates = self._cleanup_candidates(deadline)
                for item in candidates:
                    if time.monotonic() >= deadline:
                        break
                    pid = int(item)
                    if pid <= 0 or pid == self.pid:
                        raise WG.WorkGraphError("capture child cleanup candidate is invalid")
                    try:
                        fd = os.pidfd_open(pid, 0)
                    except ProcessLookupError:
                        continue
                    try:
                        self._signal_owned_child(fd)
                    finally:
                        os.close(fd)
                time.sleep(0.01)
            self._set_flag(self.previous_flag)
            self.status["flag_restored"] = True
            self.active = False
        finally:
            # Preserve the subreaper flag if ECHILD was not obtained. Signal
            # handlers can be restored without claiming successful cleanup.
            for name, handler in self.previous_handlers.items():
                signal.signal(name, handler)
            if self.primary_fd is not None:
                os.close(self.primary_fd)
                self.primary_fd = None


def _capture_stamp(value):
    return dict(device=value.st_dev, inode=value.st_ino, mode=value.st_mode, bytes=value.st_size,
        mtime_ns=value.st_mtime_ns, ctime_ns=value.st_ctime_ns, uid=value.st_uid,
        gid=value.st_gid, links=value.st_nlink)


def _capture_directory(path):
    """Acquire every absolute ancestor without resolving a symlink away."""
    path = _preflight_path(str(path), "capture directory")
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for name in path.parts[1:]:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        if (os.fstat(fd).st_dev, os.fstat(fd).st_ino) != (path.lstat().st_dev, path.lstat().st_ino):
            raise WG.WorkGraphError("capture directory changed during acquisition")
        return fd
    except BaseException:
        os.close(fd)
        raise


def _capture_private(fd):
    value = os.fstat(fd)
    if not stat.S_ISDIR(value.st_mode) or value.st_uid != os.geteuid() or stat.S_IMODE(value.st_mode) != 0o700:
        raise WG.WorkGraphError("capture retention requires an owned private 0700 directory")
    return value


def _capture_parent_population(fd, workspace, sinks):
    if set(_capture_names(fd, 3)) - {path.name for path in [workspace, *sinks]}:
        raise WG.WorkGraphError("unexpected capture retention parent members")


def _capture_names(fd, limit):
    names = []
    with os.scandir(fd) as entries:
        for entry in entries:
            if len(names) >= limit:
                raise WG.WorkGraphError("retained capture membership exceeds bound")
            names.append(entry.name)
    return sorted(names)


def _capture_census(path, *, durable=False):
    """Complete bounded no-follow typed byte/mode/identity census."""
    root = _capture_directory(path)
    entries, total = {}, 0
    limits = CAPTURE_RETENTION_LIMITS

    def visit(fd, relative, depth):
        nonlocal total
        if depth > limits["depth"] or len(entries) >= limits["entries"]:
            raise WG.WorkGraphError("retained capture census exceeds namespace bound")
        before = os.fstat(fd)
        if before.st_uid != os.geteuid():
            raise WG.WorkGraphError("retained capture census has foreign ownership")
        names = _capture_names(fd, limits["entries"] - len(entries))
        entries[relative] = dict(kind="DIRECTORY", stamp=_capture_stamp(before), members=names)
        for name in names:
            child_name = name if relative == "." else relative + "/" + name
            if len(os.fsencode(child_name)) > 4096 or len(entries) >= limits["entries"]:
                raise WG.WorkGraphError("retained capture census exceeds namespace bound")
            before_child = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISDIR(before_child.st_mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    if _capture_stamp(before_child) != _capture_stamp(os.fstat(child)):
                        raise WG.WorkGraphError("retained capture directory changed during census")
                    visit(child, child_name, depth + 1)
                finally:
                    os.close(child)
            elif stat.S_ISREG(before_child.st_mode) and before_child.st_nlink == 1 and before_child.st_uid == os.geteuid():
                total += before_child.st_size
                if before_child.st_size > limits["file_bytes"] or total > limits["total_bytes"]:
                    raise WG.WorkGraphError("retained capture census exceeds byte bound")
                child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
                try:
                    opened = os.fstat(child)
                    if _capture_stamp(before_child) != _capture_stamp(opened):
                        raise WG.WorkGraphError("retained capture file changed during census")
                    digest, acquired = hashlib.sha256(), 0
                    with os.fdopen(child, "rb", closefd=False) as stream:
                        while acquired <= opened.st_size:
                            chunk = stream.read(min(1024 * 1024, opened.st_size + 1 - acquired))
                            if not chunk:
                                break
                            digest.update(chunk)
                            acquired += len(chunk)
                    if acquired != opened.st_size:
                        raise WG.WorkGraphError("retained capture file size changed during census")
                    if durable:
                        os.fsync(child)
                    if _capture_stamp(opened) != _capture_stamp(os.fstat(child)):
                        raise WG.WorkGraphError("retained capture file changed during census")
                    entries[child_name] = dict(kind="FILE", stamp=_capture_stamp(opened), sha256=digest.hexdigest())
                finally:
                    os.close(child)
            else:
                raise WG.WorkGraphError("retained capture refuses symlinks, hardlinks, special files or foreign ownership")
            if _capture_stamp(before_child) != _capture_stamp(os.stat(name, dir_fd=fd, follow_symlinks=False)):
                raise WG.WorkGraphError("retained capture member changed during census")
        if durable:
            os.fsync(fd)
        if names != _capture_names(fd, limits["entries"]) or _capture_stamp(before) != _capture_stamp(os.fstat(fd)):
            raise WG.WorkGraphError("retained capture directory changed during census")
    try:
        _capture_private(root)
        visit(root, ".", 0)
        if _capture_stamp(os.fstat(root)) != _capture_stamp(path.lstat()):
            raise WG.WorkGraphError("retained capture root changed during census")
        result = dict(entries=entries, total_bytes=total, limits=limits)
        if len(WG.canonical_json_v1(result)) > limits["manifest_bytes"]:
            raise WG.WorkGraphError("retained capture census exceeds manifest bound")
        return result
    finally:
        os.close(root)


def _capture_population(path, record):
    expected = {"result.json", "mapping.json", "commands.bin", "stdout.log", "stderr.log", "exit-code.txt"}
    if record["mode"] == "dag":
        expected.add("nodes.tsv")
    if "child_environment" in record:
        expected.add("child-environment.json")
    for key, names in (("stdin", {"stdin.bin", "stdin.json"}),
                       ("dist_namespace", {"dist-before", "dist-after", "dist-namespace.json"}),
                       ("repro_artifacts", {"repro-assets", "repro-artifacts.json"}),
                       ("portal_events", {"portal-events"}), ("repro_events", {"repro-events"})):
        if record.get(key) is not None:
            expected |= names
    if set(os.listdir(path)) != expected:
        raise WG.WorkGraphError("unexpected capture namespace members")


def _capture_sidecar(fd, name, value):
    data = WG.canonical_json_v1(value) + b"\n"
    if len(data) > CAPTURE_RETENTION_LIMITS["manifest_bytes"]:
        raise WG.WorkGraphError("capture custody sidecar exceeds byte bound")
    member = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    with os.fdopen(member, "wb") as stream:
        metadata = os.fstat(stream.fileno())
        if metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) != 0o600 or metadata.st_nlink != 1:
            raise WG.WorkGraphError("capture custody sidecar requires owned mode 0600")
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.fsync(fd)


def _capture_read_sidecar(path, name):
    value = source_member(name, root=path, with_bytes=True,
                          byte_limit=CAPTURE_RETENTION_LIMITS["manifest_bytes"])
    if value.get("kind") != "FILE" or value.get("mode") != 0o600:
        raise WG.WorkGraphError("retained capture sidecar is missing or unsupported")
    st = (path / name).lstat()
    if st.st_uid != os.geteuid() or st.st_nlink != 1:
        raise WG.WorkGraphError("retained capture sidecar has foreign ownership or aliases")
    decoded = WG.decode_strict_json_bytes(value["_acquired_bytes"], "capture custody sidecar")
    if value["_acquired_bytes"] != WG.canonical_json_v1(decoded) + b"\n":
        raise WG.WorkGraphError("retained capture sidecar bytes differ from their canonical binding")
    return decoded


def _capture_record_contract(path, route, expected):
    record = verified_record(path)
    identity = _preflight_capture_identity_v1(route, expected["base_environment_sha256"])
    if (record["mode"] != route["mode"] or record["schema"] != identity["schema"] or
            record["execution_context"] != dict(cwd=str(ROOT), output=route["output"]) or
            record["engine_binding"] != expected["engine_binding"] or
            any(sha(WG.canonical_json_v1(record[phase])) != expected["source_sha256"] for phase in ("before", "after")) or
            record["environment"] != record["environment_after"] or
            record["environment"]["inherited_environment_sha256"] != identity["environment_sha256"]):
        raise WG.WorkGraphError("retained capture differs from actual bound source, environment or original workspace")
    capture = route["capture"]
    for key, enabled in (("stdin", capture["empty_stdin"] or capture["stdin_file"] is not None),
                         ("dist_namespace", capture["capture_dist"]),
                         ("repro_artifacts", capture["retain_repro_assets"]),
                         ("portal_events", capture["capture_portal_events"]),
                         ("repro_events", capture["retain_repro_events"])):
        if (record.get(key) is not None) != enabled:
            raise WG.WorkGraphError("retained capture acquisition differs from the bound plan")
    if identity["extended"]:
        child = dict(record["child_environment"])
        if child.pop("schema") != "implementaudit.verifier-child-environment.v1" or child != identity["child_environment"]:
            raise WG.WorkGraphError("retained capture child environment differs from actual acquired base")
    _capture_population(path, record)
    return record


def _read_sealed_capture(sink, plan, file_digest, plan_digest):
    route = next((route for route in plan["runs"] if route["retention"] == str(sink)), None)
    if route is None:
        raise WG.WorkGraphError("retained capture destination is not declared by the plan")
    directory = _capture_directory(sink)
    try:
        _capture_private(directory)
        if set(os.listdir(directory)) != {"intent.json", "capture", "custody.json"}:
            raise WG.WorkGraphError("retained capture is unsealed or has unexpected envelope members")
        intent = _capture_read_sidecar(sink, "intent.json")
        custody = _capture_read_sidecar(sink, "custody.json")
        expected_intent = dict(schema="implementaudit.capture-retention-intent.v1",
            plan_file_sha256=file_digest, plan_canonical_sha256=plan_digest, route=route,
            expected_currentness=plan["expected_currentness"], authority="NONE")
        fields = {"schema", "status", "intent_sha256", "original_workspace", "retention",
            "dispatch_currentness", "sealing_currentness", "acquired_base_environment_sha256",
            "primary_exit", "process_custody", "before_rename_root", "capture", "prior_retention",
            "normalization", "authority"}
        if (intent != expected_intent or type(custody) is not dict or set(custody) != fields or
                custody["schema"] != "implementaudit.capture-retention-custody.v1" or custody["status"] != "SEALED" or
                custody["intent_sha256"] != sha(WG.canonical_json_v1(intent) + b"\n") or
                custody["original_workspace"] != route["output"] or custody["retention"] != str(sink) or
                custody["dispatch_currentness"] != plan["expected_currentness"] or
                custody["sealing_currentness"] != plan["expected_currentness"] or
                custody["acquired_base_environment_sha256"] != plan["expected_currentness"]["base_environment_sha256"] or
                custody["normalization"] != "NONE_RAW_BYTES" or custody["authority"] != "NONE"):
            raise WG.WorkGraphError("retained capture custody/plan binding is inconsistent")
        process = custody["process_custody"]
        process_fields = {"owner_pid", "primary_pid", "primary_exit", "other_child_exits", "owned_pidfd_signals",
            "live_children_refused", "quiescence", "flag_restored", "scope", "previous_subreaper"}
        if (type(process) is not dict or set(process) != process_fields or
                process.get("quiescence") != "ECHILD_ALL_CHILDREN" or process.get("scope") != _CaptureChildren.SCOPE or
                process.get("flag_restored") is not True or process.get("live_children_refused") is not False or
                type(process.get("primary_exit")) is not int or process["primary_exit"] != custody["primary_exit"] or
                any(type(process.get(key)) is not int or process[key] <= 0 for key in ("primary_pid", "owner_pid")) or
                process["primary_pid"] == process["owner_pid"] or
                type(process["previous_subreaper"]) is not int or process["previous_subreaper"] not in (0, 1) or
                type(process["owned_pidfd_signals"]) is not int or process["owned_pidfd_signals"] != 0 or
                type(process["other_child_exits"]) is not list or len(process["other_child_exits"]) > 4096 or
                any(type(item) is not dict or set(item) != {"pid", "exit"} or
                    type(item["pid"]) is not int or item["pid"] <= 0 or type(item["exit"]) is not int
                    for item in process["other_child_exits"])):
            raise WG.WorkGraphError("retained capture lacks declared completed owned-child custody")
        prior = custody["prior_retention"]
        allowed_prior = {other["retention"] for other in plan["runs"] if other != route}
        if (type(prior) is not dict or set(prior) - allowed_prior or
                any(type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None for value in prior.values())):
            raise WG.WorkGraphError("retained capture prior-destination binding is invalid")
        capture = sink / "capture"
        before = _capture_census(capture)
        if before != custody["capture"]:
            raise WG.WorkGraphError("retained capture bytes, membership, modes or identities changed after sealing")
        previous_root, moved_root = custody["before_rename_root"], before["entries"]["."]
        if (type(previous_root) is not dict or set(previous_root) != set(moved_root) or
                previous_root["kind"] != moved_root["kind"] or previous_root["members"] != moved_root["members"] or
                type(previous_root["stamp"]) is not dict or set(previous_root["stamp"]) != set(moved_root["stamp"]) or
                any(type(value) is not int for value in previous_root["stamp"].values()) or
                any(previous_root["stamp"][key] != moved_root["stamp"][key]
                    for key in moved_root["stamp"] if key != "ctime_ns")):
            raise WG.WorkGraphError("retained capture moved-root observations are inconsistent")
        record = _capture_record_contract(capture, route, plan["expected_currentness"])
        if record["exit"] != custody["primary_exit"] or _capture_census(capture) != before:
            raise WG.WorkGraphError("retained capture changed during original-record validation")
        if (set(os.listdir(directory)) != {"intent.json", "capture", "custody.json"} or
                _capture_read_sidecar(sink, "intent.json") != intent or
                _capture_read_sidecar(sink, "custody.json") != custody):
            raise WG.WorkGraphError("retained capture envelope changed during readback")
        return capture, before
    finally:
        os.close(directory)


class _CaptureRetention:
    """One actual run's owned workspace and sealed destination, within run()."""
    def __init__(self, plan_path, mode, output, capture):
        self.parent_fd = self.sink_fd = self.workspace_fd = None
        self.children = None
        self.cleanup_attempted = False
        self.workspace_identity = None
        self.renamed = False
        self.rename_attempted = False
        self.prior_sinks = {}
        try:
            if fcntl is None:
                raise WG.WorkGraphError("capture retention requires an owned directory lock")
            self.plan, self.file_digest, self.plan_digest = _read_verifier_pair_plan_file(plan_path)
            self.workspace, self.sinks = _capture_plan_paths(self.plan)
            self.route = next(route for route in self.plan["runs"] if route["mode"] == mode)
            self.sink = Path(self.route["retention"])
            self.expected = self.plan["expected_currentness"]
            if (str(output) != str(self.workspace) or self.route["capture"] != capture or
                    any(route["base_environment_sha256"] != self.expected["base_environment_sha256"] or
                        route["capture"] != capture for route in self.plan["runs"])):
                raise WG.WorkGraphError("capture retention actual route/options differ from the bound paired plan")
            self.parent_fd = _capture_directory(self.workspace.parent)
            self.parent_identity = _capture_stamp(_capture_private(self.parent_fd))
            fcntl.flock(self.parent_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._namespace()
            if os.path.lexists(self.workspace) or os.path.lexists(self.sink):
                raise WG.WorkGraphError("capture workspace or retention destination already exists")
            self.base_environment = dict(os.environ)
            self.children = _CaptureChildren()
            self.renameat2 = getattr(self.children.libc, "renameat2", None)
            if self.renameat2 is None:
                raise WG.WorkGraphError("capture retention requires renameat2 with no-replace support")
            types = self.children.ctypes
            self.renameat2.argtypes = [types.c_int, types.c_char_p, types.c_int, types.c_char_p, types.c_uint]
            self.renameat2.restype = types.c_int
            self._currentness()
            for sink in self.sinks:
                if sink != self.sink and os.path.lexists(sink):
                    _read_sealed_capture(sink, self.plan, self.file_digest, self.plan_digest)
                    if _capture_read_sidecar(sink, "custody.json")["prior_retention"]:
                        raise WG.WorkGraphError("capture retention refuses an incomplete previously sealed pair")
                    self.prior_sinks[sink] = _capture_census(sink)
            self.children.require_quiescent()
            self._namespace()
            os.mkdir(self.sink.name, 0o700, dir_fd=self.parent_fd)
            self.sink_fd = os.open(self.sink.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.parent_fd)
            self.sink_identity = _capture_stamp(_capture_private(self.sink_fd))
            if self.sink_identity["device"] != self.parent_identity["device"]:
                raise WG.WorkGraphError("capture retention refuses cross-filesystem destinations")
            self.intent = dict(schema="implementaudit.capture-retention-intent.v1",
                plan_file_sha256=self.file_digest, plan_canonical_sha256=self.plan_digest,
                route=self.route, expected_currentness=self.expected, authority="NONE")
            _capture_sidecar(self.sink_fd, "intent.json", self.intent)
            os.fsync(self.parent_fd)
        except BaseException:
            self.close()
            raise

    def _namespace(self):
        current = _capture_stamp(_capture_private(self.parent_fd))
        path_fd = _capture_directory(self.workspace.parent)
        try:
            actual = _capture_stamp(_capture_private(path_fd))
        finally:
            os.close(path_fd)
        stable = ("device", "inode", "mode", "uid", "gid")
        if any(current[key] != self.parent_identity[key] or actual[key] != current[key] for key in stable):
            raise WG.WorkGraphError("capture parent identity changed")
        _capture_parent_population(self.parent_fd, self.workspace, self.sinks)
        if self.sink_fd is not None:
            current = _capture_stamp(_capture_private(self.sink_fd))
            actual = _capture_stamp(os.stat(self.sink.name, dir_fd=self.parent_fd, follow_symlinks=False))
            if any(current[key] != self.sink_identity[key] or actual[key] != current[key] for key in stable):
                raise WG.WorkGraphError("capture retention destination identity changed")

    def _currentness(self):
        if dict(os.environ) != self.base_environment or environment_digest(self.base_environment) != self.expected["base_environment_sha256"]:
            raise WG.WorkGraphError("capture currentness: complete actual base environment changed")
        current = verifier_preflight_currentness_v1()
        if current != self.expected or dict(os.environ) != self.base_environment:
            raise WG.WorkGraphError("capture currentness differs from the bound paired plan")
        self.children.require_quiescent()
        return current

    def create_workspace(self):
        self._namespace()
        if os.path.lexists(self.workspace):
            raise WG.WorkGraphError("capture actual workspace is occupied")
        os.mkdir(self.workspace.name, 0o700, dir_fd=self.parent_fd)
        self.workspace_fd = os.open(self.workspace.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                    dir_fd=self.parent_fd)
        self.workspace_identity = _capture_stamp(_capture_private(self.workspace_fd))
        if self.workspace_identity["device"] != self.sink_identity["device"]:
            raise WG.WorkGraphError("capture retention refuses cross-filesystem rename")

    def open_stream(self, name, *, mode=0o666, terminal=False):
        if not terminal:
            self.check_workspace()
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     mode, dir_fd=self.workspace_fd)
        return os.fdopen(fd, "wb")

    def write_workspace(self, name, data, *, mode=0o666, terminal=False):
        with self.open_stream(name, mode=mode, terminal=terminal) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())

    def check_workspace(self):
        self._namespace()
        current = _capture_stamp(self.workspace.lstat())
        held = _capture_stamp(_capture_private(self.workspace_fd))
        if any(current[key] != self.workspace_identity[key] or held[key] != current[key]
               for key in ("device", "inode", "mode", "uid", "gid")):
            raise WG.WorkGraphError("capture actual workspace identity changed")

    def dispatch_currentness(self, child_environment, overrides):
        self.check_workspace()
        if child_environment != dict(self.base_environment, **overrides):
            raise WG.WorkGraphError("capture actual child environment differs from acquired base and declared overrides")
        self.dispatch = self._currentness()

    def _prior_unchanged(self):
        for sink, original in self.prior_sinks.items():
            if _capture_census(sink) != original:
                raise WG.WorkGraphError("previously retained capture changed during the next actual run")

    def seal(self):
        self.children.require_quiescent()
        self._namespace()
        sealing = self._currentness()
        self._prior_unchanged()
        before = _capture_census(self.workspace, durable=True)
        if any(before["entries"]["."]["stamp"][key] != self.workspace_identity[key]
               for key in ("device", "inode", "mode", "uid", "gid")):
            raise WG.WorkGraphError("capture actual workspace changed before sealing")
        record = _capture_record_contract(self.workspace, self.route, self.expected)
        if _capture_census(self.workspace) != before:
            raise WG.WorkGraphError("capture census changed before sealing")
        self.children.require_quiescent()
        self._namespace()
        if set(os.listdir(self.sink_fd)) != {"intent.json"} or _capture_read_sidecar(self.sink, "intent.json") != self.intent:
            raise WG.WorkGraphError("capture retention destination changed before rename")
        # The fresh private envelope has no capture member. No copy, chmod,
        # record rewriting, destination replacement or cross-device fallback.
        self.rename_attempted = True
        ctypes = self.children.ctypes
        # Linux RENAME_NOREPLACE = 1. Unsupported kernels/filesystems and EXDEV
        # refuse; there is no replacing rename or copy fallback.
        if self.renameat2(ctypes.c_int(self.parent_fd), ctypes.c_char_p(os.fsencode(self.workspace.name)),
                ctypes.c_int(self.sink_fd), ctypes.c_char_p(b"capture"), ctypes.c_uint(1)) != 0:
            raise OSError(ctypes.get_errno(), "capture owned no-replace rename refused")
        self.renamed = True
        os.fsync(self.parent_fd)
        os.fsync(self.sink_fd)
        capture = self.sink / "capture"
        after = _capture_census(capture)
        previous_root = before["entries"]["."]
        moved_root = after["entries"]["."]
        previous = dict(before["entries"])
        moved = dict(after["entries"])
        previous.pop(".")
        moved.pop(".")
        # Rename legitimately changes the moved directory's ctime. Both actual
        # stamps are retained; all inner members must be exactly unchanged.
        if (previous != moved or before["total_bytes"] != after["total_bytes"] or
                previous_root["members"] != moved_root["members"] or
                any(previous_root["stamp"][key] != moved_root["stamp"][key]
                    for key in previous_root["stamp"] if key != "ctime_ns")):
            raise WG.WorkGraphError("retained capture changed across the owned rename")
        _capture_record_contract(capture, self.route, self.expected)
        if _capture_census(capture) != after or self._currentness() != sealing:
            raise WG.WorkGraphError("retained capture or currentness changed before custody sealing")
        self._prior_unchanged()
        self.children.require_quiescent()
        self.cleanup_attempted = True
        self.children.close()
        self._namespace()
        if os.path.lexists(self.workspace) or set(os.listdir(self.sink_fd)) != {"intent.json", "capture"}:
            raise WG.WorkGraphError("capture namespace changed before custody sealing")
        custody = dict(schema="implementaudit.capture-retention-custody.v1", status="SEALED",
            intent_sha256=sha(WG.canonical_json_v1(self.intent) + b"\n"),
            original_workspace=str(self.workspace), retention=str(self.sink),
            dispatch_currentness=self.dispatch, sealing_currentness=sealing,
            acquired_base_environment_sha256=environment_digest(self.base_environment),
            primary_exit=record["exit"], process_custody=self.children.status,
            before_rename_root=previous_root, capture=after,
            prior_retention={str(path): sha(WG.canonical_json_v1(value)) for path, value in self.prior_sinks.items()},
            normalization="NONE_RAW_BYTES", authority="NONE")
        _capture_sidecar(self.sink_fd, "custody.json", custody)
        print(json.dumps(dict(mode=record["mode"], exit=record["exit"], retention=str(self.sink),
            status="SEALED", authority="NONE", normalization="NONE_RAW_BYTES"), sort_keys=True))

    def refuse(self, error):
        cleanup_error = None
        if self.children is not None and not self.cleanup_attempted:
            self.cleanup_attempted = True
            try:
                self.children.close()
            except BaseException as exc:
                cleanup_error = type(exc).__name__ + ": " + str(exc)
        if self.sink_fd is not None:
            self._namespace()
            # A launch interrupted before its ordinary terminal write can
            # still yield an actual primary wait status during owned cleanup.
            # Preserve that status without replacing any earlier observation.
            if (not self.renamed and self.workspace_identity is not None and self.children is not None and
                    self.children.status["primary_exit"] is not None and os.path.lexists(self.workspace)):
                root = _capture_directory(self.workspace)
                try:
                    current = _capture_stamp(_capture_private(root))
                    if any(current[key] != self.workspace_identity[key] for key in ("device", "inode", "mode", "uid", "gid")):
                        raise WG.WorkGraphError("capture workspace changed before refusal exit retention")
                    if "exit-code.txt" not in os.listdir(root):
                        fd = os.open("exit-code.txt", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                     0o600, dir_fd=root)
                        with os.fdopen(fd, "wb") as terminal:
                            terminal.write((str(self.children.status["primary_exit"]) + "\n").encode())
                            terminal.flush()
                            os.fsync(terminal.fileno())
                        os.fsync(root)
                finally:
                    os.close(root)
            _capture_sidecar(self.sink_fd, "refusal.json", dict(
                schema="implementaudit.capture-retention-refusal.v1", status="UNSEALED",
                reason=type(error).__name__ + ": " + str(error), cleanup_error=cleanup_error,
                primary_exit=None if self.children is None else self.children.status["primary_exit"],
                process_custody=None if self.children is None else self.children.status,
                original_workspace=str(self.workspace), retention=str(self.sink),
                renamed=True if self.renamed else None if self.rename_attempted else False,
                authority="NONE", normalization="NONE_RAW_BYTES"))

    def close(self):
        try:
            if self.children is not None and not self.cleanup_attempted:
                self.cleanup_attempted = True
                self.children.close()
        finally:
            if self.workspace_fd is not None:
                os.close(self.workspace_fd)
                self.workspace_fd = None
            if self.sink_fd is not None:
                os.close(self.sink_fd)
                self.sink_fd = None
            if self.parent_fd is not None:
                os.close(self.parent_fd)
                self.parent_fd = None


def _compare_sealed_captures(left, right, out, plan_path):
    plan, file_digest, plan_digest = _read_verifier_pair_plan_file(plan_path)
    workspace, sinks = _capture_plan_paths(plan)
    if {str(left), str(right)} != {str(path) for path in sinks}:
        raise WG.WorkGraphError("retained comparison requires the exact two declared envelopes")
    _preflight_path(str(out), "comparison output")
    if (out == workspace.parent or workspace.parent in out.parents or out == ROOT or ROOT in out.parents):
        raise WG.WorkGraphError("retained comparison output must be outside source and capture namespaces")
    if fcntl is None:
        raise WG.WorkGraphError("retained comparison requires an owned directory lock")
    parent = _capture_directory(workspace.parent)
    try:
        _capture_private(parent)
        fcntl.flock(parent, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _capture_parent_population(parent, workspace, sinks)
        if os.path.lexists(workspace) or verifier_preflight_currentness_v1() != plan["expected_currentness"]:
            raise WG.WorkGraphError("retained capture currentness changed or actual workspace is occupied")
        a, a_census = _read_sealed_capture(left, plan, file_digest, plan_digest)
        b, b_census = _read_sealed_capture(right, plan, file_digest, plan_digest)
        for sink in (left, right):
            prior = _capture_read_sidecar(sink, "custody.json")["prior_retention"]
            for path, digest in prior.items():
                if sha(WG.canonical_json_v1(_capture_census(Path(path)))) != digest:
                    raise WG.WorkGraphError("retained capture changed since the next run's prior-destination binding")
        # Finish all mandatory custody checks before asking the unchanged raw
        # comparator to write its ordinary correspondence result.
        if (_capture_census(a) != a_census or _capture_census(b) != b_census or
                verifier_preflight_currentness_v1() != plan["expected_currentness"]):
            raise WG.WorkGraphError("retained capture changed before raw comparison")
        if os.path.lexists(out):
            raise WG.WorkGraphError("retained comparison requires a fresh result path")
        return compare(a, b, out)
    finally:
        os.close(parent)


def run(mode, output, *, retain_repro_assets=False, stdin_file=None, empty_stdin=False, capture_dist=False,
        capture_portal_events=False, retain_repro_events=False, retention_plan=None):
    capture = dict(retain_repro_assets=retain_repro_assets, stdin_file=stdin_file, empty_stdin=empty_stdin,
        capture_dist=capture_dist, capture_portal_events=capture_portal_events, retain_repro_events=retain_repro_events)
    if retention_plan is None:
        return _run_capture(mode, output, **capture)
    retention = _CaptureRetention(retention_plan, mode, output, capture)
    try:
        code = _run_capture(mode, output, **capture, retention=retention)
        retention.seal()
        return code
    except BaseException as exc:
        retention.refuse(exc)
        raise
    finally:
        retention.close()


def _run_capture(mode, output, *, retain_repro_assets=False, stdin_file=None, empty_stdin=False, capture_dist=False,
        capture_portal_events=False, retain_repro_events=False, retention=None):
    def write_capture(name, data, *, durable=False):
        if retention is not None:
            retention.write_workspace(name, data, mode=0o600 if durable else 0o666)
        elif durable:
            durable_bytes(output / name, data)
        else:
            (output / name).write_bytes(data)

    def open_capture_stream(name):
        return (output / name).open("wb") if retention is None else retention.open_stream(name)

    if stdin_file is not None and empty_stdin:
        raise WG.WorkGraphError("stdin-file and empty-stdin are mutually exclusive")
    events = capture_portal_events or retain_repro_events
    extended = retain_repro_assets or stdin_file is not None or empty_stdin or capture_dist or events
    if extended and (output == ROOT or ROOT in output.parents):
        raise WG.WorkGraphError("extended capture evidence must be outside the candidate")
    if retention is None:
        output.mkdir(parents=True, exist_ok=False)
    else:
        retention.create_workspace()
    engine = full_engine_binding()
    before = source_identity()
    if REPRO_EVENT_ENV in os.environ:
        raise WG.WorkGraphError("ambiguous inherited repro event capture directory")
    child_environment = dict(retention.base_environment) if retention is not None else dict(os.environ) if extended else None
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
                             base_environment_sha256=environment_digest(os.environ if retention is None else retention.base_environment),
                             actual_environment_sha256=environment_digest(child_environment), overrides=overrides)
        write_capture("child-environment.json", WG.canonical_json_v1(child_binding) + b"\n", durable=True)
    if stdin_file is not None or empty_stdin:
        stdin_binding, stdin_bytes = acquire_stdin(output, stdin_file, empty_stdin)
    dist_before = dist_inventory(ROOT, snapshot=output / "dist-before") if capture_dist else None
    actual_tests = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("*.test.sh"))
    registration_complete = actual_tests == tests
    write_capture("mapping.json", WG.canonical_json_v1(graph) + b"\n")
    stream = output / "commands.bin"
    compiled_stream = WG.verifier_command_stream_v1(graph, registry)
    write_capture("commands.bin", compiled_stream)
    if mode == "legacy":
        command = ["bash", "scripts/verify-package.sh"]
    else:
        command = ["bash", "scripts/run-work-graph-verifier.sh", str(stream), str(output / "nodes.tsv"), str(len(graph["nodes"])), sha(compiled_stream)]
        # Empty means no node start was observed, including a prestart
        # failure before the runner opens its trace descriptor.
        write_capture("nodes.tsv", b"")
    full_engine_binding()
    started = time.monotonic()
    launch = {} if not extended else dict(env=child_environment)
    if stdin_binding is not None:
        launch["input"] = stdin_bytes
    with open_capture_stream("stdout.log") as stdout, open_capture_stream("stderr.log") as stderr:
        if retention is None:
            process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, **launch)
            code = process.returncode
        else:
            retention.dispatch_currentness(child_environment, overrides)
            code = retention.children.launch(command, stdout=stdout, stderr=stderr,
                environment=child_environment, base_environment=retention.base_environment, stdin_bytes=stdin_bytes)
        # Retain the actual nested exit before any source/trace/JSON work.
        # A later wrapper error cannot silently erase a completed verdict.
        if retention is None:
            with (output / "exit-code.txt").open("w") as terminal:
                terminal.write(str(code) + "\n")
                terminal.flush()
                os.fsync(terminal.fileno())
        else:
            retention.write_workspace("exit-code.txt", (str(code) + "\n").encode(), terminal=True)
        if retention is not None:
            stdout.flush()
            stderr.flush()
            os.fsync(stdout.fileno())
            os.fsync(stderr.fileno())
            if retention.children.exec_error is not None:
                raise WG.WorkGraphError("capture primary exec failed with errno " + str(retention.children.exec_error))
            retention.children.require_quiescent()
            retention.check_workspace()
            # Fence types, aliases and bounds before the original post-run
            # readers open raw streams or artifact paths by name.
            _capture_census(output)
    full_engine_binding()
    if stream.read_bytes() != compiled_stream:
        raise WG.WorkGraphError("retained verifier command stream differs from launched input")
    after = source_identity()
    environment_after = environment_identity(dict(os.environ, **overrides) if extended else None, child_resolution=extended)
    trace = (output / "nodes.tsv").read_bytes() if mode == "dag" else None
    node_results = trace_nodes(graph, mode, code, trace)
    namespace = None
    if capture_dist:
        namespace = dist_binding(output, dist_before, dist_inventory(ROOT, snapshot=output / "dist-after"))
        write_capture("dist-namespace.json", WG.canonical_json_v1(namespace) + b"\n", durable=True)
    artifacts = None
    if retain_repro_assets:
        artifacts = observe_repro_artifacts(output, str(output), graph, before, after, code)
        write_capture("repro-artifacts.json", WG.canonical_json_v1(artifacts) + b"\n", durable=True)
        if code == 0 and (not artifacts["complete"] or not artifacts["source_current"]):
            raise WG.WorkGraphError("successful repro capture has missing artifacts or changed source")
    portal = None
    if portal_request is not None:
        try:
            portal = portal_engine().verify(output / "portal-events", portal_request, require_complete=code == 0)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise WG.WorkGraphError("portal handoff refusal: " + str(exc)) from exc
    repro_events = observe_repro_events(output, str(output), graph, before, after, code,
                                       original_cwd=str(ROOT)) if retain_repro_events else None
    result = dict(schema="implementaudit.verifier-run.v4" if events else "implementaudit.verifier-run.v3" if extended else "implementaudit.verifier-run.v2", mode=mode, command=command[:2],
                  actual_argv=command, execution_context=dict(cwd=str(ROOT), output=str(output)),
                  command_stream=dict(sha256=sha(compiled_stream), bytes=len(compiled_stream)),
                  before=before, after=after, environment=environment, environment_after=environment_after,
                  engine_binding=engine,
                  registry_sha256=sha(registry), graph_digest=graph["digest"],
                  mapped_nodes=len(graph["nodes"]), registered_tests=len(tests),
                  registration_complete=registration_complete,
                  exit=code, elapsed_ms=int((time.monotonic() - started) * 1000),
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
    write_capture("result.json", WG.canonical_json_v1(result) + b"\n")
    if retention is None:
        print(json.dumps({k: result[k] for k in ("mode", "exit", "elapsed_ms", "mapped_nodes", "registered_tests", "registration_complete", "stdout_sha256", "stderr_sha256")}, sort_keys=True))
    return code if code >= 0 else 128 - code


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

    def _claim_overlay_configuration_v1(self, files, directories):
        """One fixed original96 image policy, derived only from acquired bytes."""
        if self.SCOPE == "CONTROLLED_TASK_CUSTODY_APPEND_V1":
            return self._custody_overlay_configuration_v1(files, directories)
        root, config_path = "/work/docs", "/profile/original96-overlay.json"
        source_directories = sorted(name for name in set(directories)
            if name == "/work" or name.startswith("/work/"))
        source_files = {name: dict(mode=mode, bytes=len(data), sha256=sha(data))
            for name, (data, mode) in sorted(files.items()) if name.startswith("/work/")}
        if root not in source_directories or root + "/claim-probe-proof-levels.md" in set(source_files) | set(source_directories):
            raise WG.WorkGraphError("original96 requires its docs parent and initially absent probe")
        readonly_subtrees = sorted(name for name in source_directories
            if name.startswith(root + "/") and name.count("/") == 3)
        baseline = dict(files={name[len(root)+1:]: entry for name, entry in source_files.items() if name.startswith(root + "/")},
            directories={"." if name == root else name[len(root)+1:]: 0o755 for name in source_directories
                         if name == root or name.startswith(root + "/")})
        config = dict(schema="implementaudit.original96-overlay-config.v1", policy="ORIGINAL96_PRIVATE_DOCS_V1",
            root=root, tmp_root="/tmp", probe="claim-probe-proof-levels.md", buffer_bytes=4 * 1024**2,
            entry_limit=4096, path_bytes=2048, file_bytes=self.LIMITS["file_bytes"],
            baseline=baseline, immutable_paths=sorted(set(source_files) | (set(source_directories) - {root}) | {"/"}))
        raw = self._encode(config)
        if len(raw) > 1024**2 or self.LIMITS["scratch_bytes"] != 32 * 1024**2:
            raise WG.WorkGraphError("original96 fixed overlay/configuration capacity refused")
        policy = dict(policy="ORIGINAL96_PRIVATE_DOCS_V1", root=root, overlay_bytes=1024**2,
            tmp_bytes=31 * 1024**2, census_buffer_bytes=4 * 1024**2,
            config_path=config_path, config_sha256=sha(raw), readonly_subtrees=readonly_subtrees,
            writable_namespace="NEW_NAMES_AND_NEW_DESCENDANTS_UNDER_DOCS_PARENT_EXISTING_MOUNTS_READ_ONLY",
            census="BEFORE_AND_AFTER_STATE_NOT_A_TEMPORAL_WRITE_TRACE")
        return config, raw, policy

    def _custody_overlay_configuration_v1(self, files, directories):
        """The same C3 owner, with a full-byte fixed private original105 root."""
        root, config_path = "/work", "/profile/original105-overlay.json"
        source_directories = sorted(name for name in set(directories)
            if name == root or name.startswith(root + "/"))
        source_files = {name: dict(mode=mode, bytes=len(data), sha256=sha(data))
            for name, (data, mode) in sorted(files.items()) if name.startswith(root + "/")}
        if root not in source_directories or any(entry["mode"] not in (0o444, 0o644, 0o755)
                for entry in source_files.values()):
            raise WG.WorkGraphError("original105 requires complete supported source modes")
        readonly_subtrees = sorted(name for name in source_directories
            if name.startswith(root + "/") and name.count("/") == 2)
        baseline = dict(files={name[len(root)+1:]: entry for name, entry in source_files.items()},
            directories={"." if name == root else name[len(root)+1:]: 0o755 for name in source_directories})
        config = dict(schema="implementaudit.original105-overlay-config.v1", policy="ORIGINAL105_PRIVATE_WORK_V1",
            root=root, tmp_root="/tmp", census_key="source", buffer_bytes=4 * 1024**2,
            entry_limit=4096, path_bytes=2048, file_bytes=self.LIMITS["file_bytes"],
            baseline=baseline, immutable_paths=sorted(set(source_files) | (set(source_directories) - {root}) | {"/"}))
        raw = self._encode(config)
        if len(raw) > 1024**2 or self.LIMITS["scratch_bytes"] != 32 * 1024**2:
            raise WG.WorkGraphError("original105 fixed overlay/configuration capacity refused")
        # Count the entire serialized baseline, two observations and worst-width
        # per-member metadata, without claiming any original execution.
        census = dict(files={name: dict(entry, nlink=2**63-1, read_only=False)
                            for name, entry in baseline["files"].items()},
            directories={name: dict(mode=mode, nlink=2**63-1, read_only=False)
                         for name, mode in baseline["directories"].items()})
        # store_record uses ensure_ascii=True. Charge that actual spelling,
        # including escaped non-ASCII source names, rather than UTF-8 size.
        census_encoding = lambda value: json.dumps(value, sort_keys=True,
            separators=(",", ":"), ensure_ascii=True).encode("ascii")
        census_bound = 2 * len(census_encoding(census)) + 2 * len(census_encoding(
            {name: False for name in config["immutable_paths"]})) + 65536
        if census_bound > config["buffer_bytes"] - 8:
            raise WG.WorkGraphError("original105 complete census exceeds its fixed buffer")
        policy = dict(policy="ORIGINAL105_PRIVATE_WORK_V1", root=root, overlay_bytes=2 * 1024**2,
            tmp_bytes=30 * 1024**2, census_buffer_bytes=4 * 1024**2,
            config_path=config_path, config_sha256=sha(raw), readonly_subtrees=readonly_subtrees,
            census_record_bound=census_bound,
            writable_namespace="NEW_NAMES_AND_NEW_DESCENDANTS_UNDER_PRIVATE_WORK_EXISTING_MEMBERS_READ_ONLY",
            census="BEFORE_AND_AFTER_STATE_NOT_A_TEMPORAL_WRITE_TRACE")
        return config, raw, policy

    def _claim_overlay_guard_v1(self, files, manifest, node):
        policy = manifest.get("private_source_overlay")
        if policy is None:
            if self.SCOPE in ("CONTROLLED_TASK_CLAIM_BOUNDARY_V1", "CONTROLLED_TASK_CUSTODY_APPEND_V1"):
                label = "original105" if self.SCOPE == "CONTROLLED_TASK_CUSTODY_APPEND_V1" else "original96"
                raise WG.WorkGraphError(label + " requires its fixed private source overlay")
            return None
        if self.SCOPE == "CONTROLLED_TASK_CUSTODY_APPEND_V1":
            if (manifest.get("root_read_only") is not True
                    or manifest.get("source_materialization") != "SINGLE_LINK_FILES_READ_ONLY_ROOT"
                    or manifest.get("source_permissions") != "PRESERVE_MODES_PRIVATE_ROOT_READ_ONLY_EXISTING_MEMBERS"
                    or manifest.get("copy_umask") != 0o022
                    or manifest.get("data_permissions") != "OWNER_0600_READ_ONLY_MOUNT"
                    or any(mode not in ((0o444, 0o644, 0o755) if name.startswith("/work/") else (0o600, 0o555))
                           for name, (_, mode) in files.items())
                    or node.get("id") != "COMMAND:tests/custody-append.test.sh:0"
                    or node.get("source") != "bash tests/custody-append.test.sh\n"):
                raise WG.WorkGraphError("unsupported fixed original105 private source overlay")
            config, raw, expected = self._claim_overlay_configuration_v1(files, manifest["directories"])
            if policy != expected or files.get(expected["config_path"]) != (raw, 0o600):
                raise WG.WorkGraphError("private source overlay differs from the acquired fixed configuration")
            return config
        if (self.SCOPE != "CONTROLLED_TASK_CLAIM_BOUNDARY_V1" or manifest.get("root_read_only") is not True
                or manifest.get("source_materialization") is not None
                or manifest.get("data_permissions") != "OWNER_0600_READ_ONLY_MOUNT"
                or any(mode not in (0o600, 0o555) for _, mode in files.values())
                or node.get("id") != "COMMAND:tests/claim-boundary-proof-levels.test.sh:0"
                or node.get("source") != "bash tests/claim-boundary-proof-levels.test.sh\n"):
            raise WG.WorkGraphError("unsupported fixed private source overlay")
        config, raw, expected = self._claim_overlay_configuration_v1(files, manifest["directories"])
        if policy != expected or files.get(expected["config_path"]) != (raw, 0o600):
            raise WG.WorkGraphError("private source overlay differs from the acquired fixed configuration")
        return config

    @staticmethod
    def _claim_census_buffer_v1():
        fd = os.memfd_create("r0035-private-source-census", os.MFD_ALLOW_SEALING | os.MFD_CLOEXEC)
        try:
            os.ftruncate(fd, 4 * 1024**2)
            fcntl.fcntl(fd, fcntl.F_ADD_SEALS, fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK)
            return fd
        except BaseException:
            os.close(fd)
            raise

    @staticmethod
    def _claim_effects_decode_v1(raw, config):
        """Decode bounded actual observations; never infer a missing phase."""
        policy = config.get("policy")
        custody = policy == "ORIGINAL105_PRIVATE_WORK_V1"
        source_key = "source" if custody else "docs"
        result = dict(schema=("implementaudit.original105-private-effects.v1" if custody
                              else "implementaudit.original96-private-effects.v1"), policy=policy,
            authority="NONE", observation="UNOBSERVED", buffer_sha256=sha(raw),
            original_started="UNOBSERVED", original_exit="UNOBSERVED", clean_private_namespace=False,
            protected_members_unchanged=False, census="BEFORE_AND_AFTER_STATE_NOT_A_TEMPORAL_WRITE_TRACE")
        try:
            if policy not in ("ORIGINAL96_PRIVATE_DOCS_V1", "ORIGINAL105_PRIVATE_WORK_V1"):
                raise ValueError("unsupported census policy")
            if len(raw) != config["buffer_bytes"]:
                raise ValueError("census buffer length changed")
            length = struct.unpack("!Q", raw[:8])[0]
            if not 0 < length <= len(raw) - 8:
                raise ValueError("no complete bounded census record")
            record = WG.decode_strict_json_bytes(raw[8:8+length], "private source census")
            if (type(record) is not dict or record.get("policy") != policy
                    or type(record.get("original_started")) is not bool):
                raise ValueError("unsupported census record")
            result.update(observation="PARTIAL", record=record, original_started=record["original_started"],
                          original_exit=record.get("original_exit", "UNOBSERVED"))

            def baseline_matches(census):
                return (set(census["files"]) == set(config["baseline"]["files"])
                    and {name: entry["mode"] for name, entry in census["directories"].items()} == config["baseline"]["directories"]
                    and all({key: census["files"][name][key] for key in ("mode", "bytes", "sha256")} == expected
                            for name, expected in config["baseline"]["files"].items()))

            def immutable_matches(phase):
                values = phase["immutable_mounts"]
                return set(values) == set(config["immutable_paths"]) and all(value is True for value in values.values())

            def empty_tmp(phase):
                return phase["tmp"]["files"] == {} and set(phase["tmp"]["directories"]) == {"."}

            before = record["before"]
            if (not baseline_matches(before[source_key]) or not empty_tmp(before) or not immutable_matches(before)
                    or before[source_key]["directories"]["."]["read_only"] is not False
                    or before["tmp"]["directories"]["."]["read_only"] is not False):
                raise ValueError("before census differs from the acquired protected namespace")
            if record.get("phase") != "AFTER" or not record["original_started"]:
                return result
            original_exit = record.get("original_exit")
            if type(original_exit) is not int or not -64 <= original_exit <= 255:
                raise ValueError("actual original exit is missing or malformed")
            after = record["after"]
            protected = immutable_matches(after) and all(
                {key: after[source_key]["files"].get(name, {}).get(key) for key in ("mode", "bytes", "sha256")} == expected
                for name, expected in config["baseline"]["files"].items())
            protected = protected and all(after[source_key]["directories"].get(name, {}).get("mode") == mode
                for name, mode in config["baseline"]["directories"].items())
            clean = (baseline_matches(after[source_key]) and empty_tmp(after)
                and after[source_key]["directories"]["."]["read_only"] is False
                and after["tmp"]["directories"]["."]["read_only"] is False
                and after["tmp"]["directories"]["."]["mode"] == before["tmp"]["directories"]["."]["mode"])
            result.update(observation="COMPLETE", protected_members_unchanged=protected, clean_private_namespace=clean)
            return result
        except (AttributeError, KeyError, TypeError, ValueError, struct.error) as error:
            result.update(observation="REFUSED", reason=str(error))
            return result

    @staticmethod
    def _mini_audit_entropy_device_v1():
        """Observe one fixed real kernel interface without opening or reading it.

        Entropy state is trusted live kernel state, like existing clocks and
        getrandom. This records device currentness, never a seed or byte image.
        A character-device bind is not generic device-write confinement.
        """
        path = Path("/dev/urandom")
        before = path.lstat()
        if (path.resolve(strict=True) != path or not stat.S_ISCHR(before.st_mode) or
                (os.major(before.st_rdev), os.minor(before.st_rdev)) != (1, 9) or
                stat.S_IMODE(before.st_mode) != 0o666 or before.st_nlink != 1 or
                (before.st_uid, before.st_gid, before.st_size) != (0, 0, 0)):
            raise WG.WorkGraphError("unsupported original87 kernel entropy device")
        def stamp(info):
            return [*VerifierTaskSession._root_identity(info), info.st_mode,
                    info.st_nlink, info.st_rdev, info.st_size, info.st_uid,
                    info.st_gid, info.st_mtime_ns, info.st_ctime_ns]
        identity = stamp(before)
        if path.resolve(strict=True) != path or stamp(path.lstat()) != identity:
            raise WG.WorkGraphError("original87 kernel entropy device changed during observation")
        return dict(schema="implementaudit.original87-kernel-entropy.v1",
            policy="ORIGINAL87_FIXED_REAL_URANDOM_V1", path="/dev/urandom",
            kind="CHARACTER", major=1, minor=9, mode=0o666, uid=0, gid=0,
            identity=identity, consumer="PINNED_CLOSED_GIT_CSPRNG_PATH_OPENS_O_RDONLY",
            state="LIVE_TRUSTED_KERNEL_NONDETERMINISM_NOT_SNAPSHOTTED",
            capability="EXACT_URANDOM_CHARACTER_DEVICE_IO_NOT_GENERIC_DEVICE_WRITE_CONFINEMENT",
            authority="NONE")

    def _mini_audit_entropy_guard_v1(self, acquired, node, files, manifest):
        """Admit the device only for the captured original87 closed call set."""
        field = "mini_audit_kernel_entropy"
        scope = "CONTROLLED_TASK_MINI_AUDIT_LOOP_V1"
        acquisition = acquired["acquired"]
        if self.SCOPE != scope:
            if field in manifest or field in acquisition:
                raise WG.WorkGraphError("original87 kernel entropy is forbidden for another profile")
            return None
        binding = manifest.get(field)
        command = "bash tests/e2e-mini-audit-loop.test.sh\n"
        node_id = "COMMAND:tests/e2e-mini-audit-loop.test.sh:0"
        program_pin = "8b4aff39b1da3c36d1ebc9e020923e214dec4926e5426ac4e322d59d444308f3"
        git_pin = "2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668"
        if (not isinstance(binding, dict) or acquisition.get(field) != binding or
                acquisition.get("scope") != scope or node.get("id") != node_id or
                node.get("source") != command or node.get("source_sha256") != sha(command.encode()) or
                set(acquisition.get("inputs", {})) != {node_id} or
                acquisition["inputs"][node_id].get("program_sha256") != program_pin or
                manifest.get("root_read_only") is not True or
                manifest.get("environment") != self.environment or acquisition.get("environment") != self.environment or
                manifest.get("limits") != self.LIMITS or acquisition.get("limits") != self.LIMITS or
                "private_source_overlay" in manifest):
            raise WG.WorkGraphError("unsupported original87 kernel entropy execution scope")
        required = {
            "/usr/bin/git": (git_pin, 0o555),
            "/work/tests/e2e-mini-audit-loop.test.sh": (program_pin, 0o644),
            "/work/skills/implementaudit/scripts/validate-phase.sh": (
                "07b2e04ba9aefffc572ac9cf60ecddf88654a26590aaa045dadf464da7bc7dab", 0o755),
            "/work/skills/implementaudit/scripts/repo-state.sh": (
                "b2220d0627c5e66d106bb3ce8a9daafb5310b87643b9281d63db5a5aa886df3b", 0o644),
            "/work/fixtures/e2e-mini-audit-loop/phase-1.md": (
                "44a48a1a22e8bb7a783aa0b4c3608e2d75afe4ad4d74ac720931f759b7cde06b", 0o644),
        }
        for name, (pin, mode) in required.items():
            entry = files.get(name)
            if (not isinstance(entry, tuple) or len(entry) != 2 or
                    entry[1] != mode or sha(entry[0]) != pin):
                raise WG.WorkGraphError("original87 kernel entropy requires pinned program and branch bytes")
        templates = manifest.get("mini_audit_git_templates", {})
        projection = templates.get("projection", {})
        root = "/usr/share/git-core/templates"
        if (templates.get("root") != root or
                sha(self._encode(projection)) != "c16f8f1efb821f6547999f092623ce26fa29604a19a78c9108e7470e052bfbfd" or
                templates.get("policy") != "ACTUAL_COMPLETE_DEFAULT_TEMPLATE_TREE_NO_FILTER_NO_OVERRIDE"):
            raise WG.WorkGraphError("original87 kernel entropy requires complete fixed templates")
        selected = {name: entry for name, entry in files.items() if name == root or name.startswith(root + "/")}
        expected = {root + "/" + name: row for name, row in projection["files"].items()}
        if set(selected) != set(expected) or any(
                (len(selected[name][0]), selected[name][1], sha(selected[name][0])) !=
                (row["bytes"], row["mode"], row["sha256"]) for name, row in expected.items()):
            raise WG.WorkGraphError("original87 kernel entropy template bytes or modes differ")
        directories = {root if name == "." else root + "/" + name for name in projection["directories"]}
        if {name for name in manifest["directories"] if name == root or name.startswith(root + "/")} != directories:
            raise WG.WorkGraphError("original87 kernel entropy template directories differ")
        git = manifest.get("git_startup", {})
        if (git.get("executable") != "/usr/bin/git" or git.get("template_default") != root or
                git.get("closure", {}).get("/usr/bin/git", {}).get("sha256") != git_pin or
                git.get("maintenance") != "ORIGINAL_DEFAULT_BUILTIN_AUTO_MAINTENANCE_UNCHANGED"):
            raise WG.WorkGraphError("original87 kernel entropy Git binding differs")
        if binding != self._mini_audit_entropy_device_v1():
            raise WG.WorkGraphError("original87 kernel entropy physical currentness differs")
        if (manifest.get("writable_resources") != ["fresh bounded /tmp", "/dev/null", "stdout", "stderr", binding["capability"]] or
                acquisition.get("mutable_resources") != ["private bounded /tmp", "/dev/null", "observer stdout/stderr", binding["capability"]] or
                acquisition.get("effects") != "PRIVATE_FILESYSTEM_WRITES_DISCARDED_TRUSTED_KERNEL_ENTROPY_NO_PREDECESSOR_OR_SUCCESSOR_SUBSTITUTION"):
            raise WG.WorkGraphError("original87 kernel entropy capability disclosure differs")
        return binding

    def _execute(self, acquired, node, decision, directory):
        files, manifest = acquired["images"][node["id"]]
        materialization = manifest.get("source_materialization")
        if materialization not in (None, "SINGLE_LINK_FILES_READ_ONLY_ROOT") or (
                materialization is not None and manifest.get("root_read_only") is not True):
            raise WG.WorkGraphError("unsupported source image materialization")
        data_permissions = manifest.get("data_permissions")
        if data_permissions not in (None, "OWNER_0600_READ_ONLY_MOUNT") or (
                data_permissions is not None and manifest.get("root_read_only") is not True) or (
                data_permissions is None and any(mode == 0o600 for _, mode in files.values())):
            raise WG.WorkGraphError("unsupported read-only data image permissions")
        source_permissions = manifest.get("source_permissions")
        copy_permissions = source_permissions == "COPY_0666_UMASK_022_READ_ONLY_ROOT"
        private_work_permissions = source_permissions == "PRESERVE_MODES_PRIVATE_ROOT_READ_ONLY_EXISTING_MEMBERS"
        if source_permissions not in (None, "COPY_0666_UMASK_022_READ_ONLY_ROOT",
                "PRESERVE_MODES_PRIVATE_ROOT_READ_ONLY_EXISTING_MEMBERS") or (
                copy_permissions and (materialization != "SINGLE_LINK_FILES_READ_ONLY_ROOT" or
                    data_permissions != "OWNER_0600_READ_ONLY_MOUNT" or manifest.get("copy_umask") != 0o022)) or (
                private_work_permissions and (self.SCOPE != "CONTROLLED_TASK_CUSTODY_APPEND_V1" or
                    materialization != "SINGLE_LINK_FILES_READ_ONLY_ROOT" or
                    data_permissions != "OWNER_0600_READ_ONLY_MOUNT" or manifest.get("copy_umask") != 0o022)) or (
                not copy_permissions and (any(mode == 0o666 for _, mode in files.values()) or
                    (not private_work_permissions and "copy_umask" in manifest))) or (
                any(mode == 0o666 and not name.startswith("/work/") for name, (_, mode) in files.items())):
            raise WG.WorkGraphError("unsupported read-only source image permissions")
        overlay_config = self._claim_overlay_guard_v1(files, manifest, node)
        overlay = manifest.get("private_source_overlay")
        entropy = self._mini_audit_entropy_guard_v1(acquired, node, files, manifest)
        directory.mkdir()
        self._write(directory / "image.json", manifest)
        fds = []
        census_fd, private_effects = None, None
        source_stage = None
        try:
            args = ["--unshare-all", "--unshare-user", "--die-with-parent", "--new-session", "--clearenv", "--cap-drop", "ALL"]
            for key, value in sorted(self.environment.items()):
                args += ["--setenv", key, value]
            if private_work_permissions:
                source_stage = self._custody_source_stage_v1(files, manifest["directories"], overlay, directory)
                self._write(directory / "source-stage.before.json", source_stage.check())
            launch_directories = [name for name in manifest["directories"]
                if not (private_work_permissions and name.startswith("/work/"))]
            for name in sorted(set(launch_directories) | {"/dev", "/tmp"}, key=lambda s: (s.count("/"), s)):
                if overlay is not None and name == overlay["root"]:
                    args += ["--perms", "0755", "--size", str(overlay["overlay_bytes"]), "--tmpfs", name]
                elif overlay is not None and name in overlay["readonly_subtrees"]:
                    args += ["--perms", "0755", "--tmpfs", name]
                else:
                    # --dir defaults to0755 and resets its one-operation modifier.
                    # The fixed copy policy can use that spelling for every directory.
                    args += (["--dir", name] if copy_permissions or private_work_permissions else ["--perms", "0755", "--dir", name])
            for name, (data, mode) in sorted(files.items()):
                if private_work_permissions and name.startswith("/work/"):
                    continue  # Exact linked bytes/modes are in the private input stage.
                fd = self._sealed(data)
                fds.append(fd)
                # --ro-bind-data unlinks its backing inode (st_nlink == 0).
                # Physical-file checkers need an ordinary linked source file.
                # Both routes copy the same sealed bytes; the existing final
                # root remount makes --file source members read-only as well.
                kind = "--file" if materialization is not None and name.startswith("/work/") else "--ro-bind-data"
                # Preserve the existing other-profile defaults. Fixed105 source
                # modes are physical staged modes, independent of bwrap's umask.
                default_mode = (kind == "--ro-bind-data" and mode == 0o600) or (
                    kind == "--file" and mode == 0o666 and copy_permissions)
                if not default_mode:
                    args += ["--perms", oct(mode)[2:]]
                args += [kind, str(fd), name]
            if source_stage is not None:
                for path, destination in source_stage.bindings:
                    args += ["--ro-bind", path, destination]
            seccomp_fd = self._sealed(self.SECCOMP)
            fds.append(seccomp_fd)
            if overlay is not None:
                if not private_work_permissions:
                    for name in overlay["readonly_subtrees"]:
                        args += ["--remount-ro", name]
                census_fd = self._claim_census_buffer_v1()
                fds.append(census_fd)
            if entropy is not None:
                # Only the fixed guarded original87 may expose this real kernel
                # interface. Read-only filesystem flags do not deny device I/O.
                args += ["--dev-bind", "/dev/urandom", "/dev/urandom"]
            args += ["--dev-bind", "/dev/null", "/dev/null", "--size", str(self.LIMITS["scratch_bytes"] if overlay is None else overlay["tmp_bytes"]), "--tmpfs", "/tmp",
                     "--remount-ro", "/", "--chdir", "/work", "--seccomp", str(seccomp_fd)]
            command = ["/usr/bin/bash", "--noprofile", "--norc", "/work/scripts/run-work-graph-verifier.sh",
                       "--isolated-leaf", node["id"], node["source"], node["source_sha256"]]
            if overlay is not None:
                command += [overlay["policy"], str(census_fd)]
            # --args is still counted by bubblewrap's9000-argument parser.
            # Include the outer --args/FD and checker argv, then keep margin.
            argument_count = len(args) + 2 + len(command)
            if argument_count > 8500:
                raise WG.WorkGraphError("snapshot exceeds supported launcher argument budget")
            if private_work_permissions and argument_count != manifest.get("image_reservation", {}).get("launcher_argument_count"):
                raise WG.WorkGraphError("original105 launcher differs from its exact acquired argument reservation")
            args_fd = self._sealed(b"\0".join(a.encode() for a in args) + b"\0")
            fds.append(args_fd)
            if max(fds) >= self.LIMITS["descriptors"]:
                raise WG.WorkGraphError("snapshot exceeds supported descriptor budget")
            self._write(directory / "dispatch.json", dict(node=node["id"], command=node["source"],
                        command_sha256=node["source_sha256"], input_key=decision["key"],
                        image_digest=acquired["acquired"]["inputs"][node["id"]]["image_digest"],
                        descriptor_count=len(fds), argument_count=argument_count, argument_limit=8500,
                        descriptor_custody=("SEALED_INPUTS_ONLY_CLOSED_BEFORE_CHECKER" if overlay is None
                            else "SEALED_INPUTS_CLOSED_BOOTSTRAP_CENSUS_FD_NOT_INHERITED_BY_ORIGINAL")))
            def limits():
                if private_work_permissions:
                    os.umask(0o022)
                resource.setrlimit(resource.RLIMIT_CPU, (self.LIMITS["cpu_seconds"],) * 2)
                resource.setrlimit(resource.RLIMIT_AS, (self.LIMITS["address_bytes"],) * 2)
                resource.setrlimit(resource.RLIMIT_FSIZE, (self.LIMITS["file_bytes"],) * 2)
                resource.setrlimit(resource.RLIMIT_NOFILE, (self.LIMITS["descriptors"],) * 2)
            code, complete, process = None, False, None
            with (directory / "stdout.log").open("xb") as stdout, (directory / "stderr.log").open("xb") as stderr:
                try:
                    try:
                        if entropy is not None and entropy != self._mini_audit_entropy_device_v1():
                            raise WG.WorkGraphError("original87 kernel entropy device changed before launch")
                        if source_stage is not None:
                            source_stage.check()
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
            try:
                if census_fd is not None:
                    fcntl.fcntl(census_fd, fcntl.F_ADD_SEALS, fcntl.F_SEAL_WRITE | fcntl.F_SEAL_SEAL)
                    census_raw = os.pread(census_fd, overlay["census_buffer_bytes"], 0)
                    self._write(directory / "source-effects.buffer", census_raw)
                    private_effects = self._claim_effects_decode_v1(census_raw, overlay_config)
                    self._write(directory / "source-effects.json", private_effects)
            finally:
                try:
                    if source_stage is not None:
                        try:
                            self._write(directory / "source-stage.after.json", source_stage.check())
                        except BaseException as exc:
                            self._write(directory / "source-stage.failure.json", dict(error=type(exc).__name__, detail=str(exc)))
                            raise
                        finally:
                            source_stage.close()
                finally:
                    for fd in fds:
                        os.close(fd)
        raw = {name: self._regular(directory / name)[1] for name in ("stdout.log", "stderr.log", "exit-code.txt", "image.json", "dispatch.json")}
        if private_work_permissions:
            raw.update({name: self._regular(directory / name)[1] for name in ("source-stage.before.json", "source-stage.after.json")})
        if overlay is not None:
            raw.update({name: self._regular(directory / name)[1] for name in ("source-effects.buffer", "source-effects.json")})
            if code == 0 and complete and (private_effects["observation"] != "COMPLETE"
                    or private_effects["original_exit"] != 0 or not private_effects["protected_members_unchanged"]
                    or not private_effects["clean_private_namespace"]):
                raise WG.WorkGraphError("actual successful exit lacks a complete matching private-source census")
        result = dict(schema="implementaudit.verifier-issued-result.v1", scope=acquired["acquired"]["scope"],
                      producer=self.producer, node=node["id"], key=decision["key"], dispatch=self.dispatch_count,
                      source_digest=self._object(self._encode(acquired["state"])), exit=code, complete=complete,
                      stdout_sha256=sha(raw["stdout.log"]), stderr_sha256=sha(raw["stderr.log"]),
                      semantic_artifacts=[], authority="NONE")
        if overlay is not None:
            result.update(semantic_artifacts=[dict(path="source-effects.json", sha256=sha(raw["source-effects.json"]))],
                private_source_effects=dict(policy=overlay["policy"], observation=private_effects["observation"],
                    original_started=private_effects["original_started"], original_exit=private_effects["original_exit"],
                    protected_members_unchanged=private_effects["protected_members_unchanged"],
                    clean_private_namespace=private_effects["clean_private_namespace"],
                    mutable_namespace=overlay["writable_namespace"], authority="NONE"))
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



_FINITE_LEAF = None
_FINITE_SESSIONS = {}
_FINITE_MODES = {
    "audit-spec": "CONTROLLED_TASK_AUDIT_SPEC_V1",
    "andon-class": "CONTROLLED_TASK_ANDON_CLASS_V1",
    "registry-wrapper": "CONTROLLED_TASK_REGISTRY_WRAPPER_V1",
    "marker-order": "CONTROLLED_TASK_MARKER_ORDER_V1",
    "commit-message": "CONTROLLED_TASK_COMMIT_MESSAGE_V1",
    "agents-bootstrap": "CONTROLLED_TASK_AGENTS_BOOTSTRAP_V1",
    "andon-escalation": "CONTROLLED_TASK_ANDON_ESCALATION_V1",
    "internal-skill-topology": "CONTROLLED_TASK_INTERNAL_SKILL_TOPOLOGY_V1",
    "capability-ledger": "CONTROLLED_TASK_CAPABILITY_LEDGER_V1",
    "issues-deferred": "CONTROLLED_TASK_ISSUES_DEFERRED_V1",
    "no-terminal-cap": "CONTROLLED_TASK_NO_TERMINAL_CAP_V1",
    "background-chain": "CONTROLLED_TASK_BACKGROUND_CHAIN_V1",
    "plan-lifecycle": "CONTROLLED_TASK_PLAN_LIFECYCLE_V1",
    "plan-quality": "CONTROLLED_TASK_PLAN_QUALITY_V1",
    "authorization-binding": "CONTROLLED_TASK_AUTHORIZATION_BINDING_V1",
    "read-only-plans": "CONTROLLED_TASK_READ_ONLY_PLANS_V1",
    "safeguard-restoration": "CONTROLLED_TASK_SAFEGUARD_RESTORATION_V1",
    "routing": "CONTROLLED_TASK_ROUTING_V1",
    "audit-object-routing": "CONTROLLED_TASK_AUDIT_OBJECT_ROUTING_V1",
    "installed-payload": "CONTROLLED_TASK_INSTALLED_PAYLOAD_V1",
    "planner-copy": "CONTROLLED_TASK_PLANNER_COPY_V1",
    "fanout-coverage": "CONTROLLED_TASK_FANOUT_COVERAGE_V1",
    "skill-layout": "CONTROLLED_TASK_SKILL_LAYOUT_V1",
    "native-integration": "CONTROLLED_TASK_NATIVE_INTEGRATION_V1",
    "audit-retention": "CONTROLLED_TASK_AUDIT_RETENTION_V1",
    "audit-object-contract": "CONTROLLED_TASK_AUDIT_OBJECT_CONTRACT_V1",
    "claim-boundary": "CONTROLLED_TASK_CLAIM_BOUNDARY_V1",
    "terminology-integration": "CONTROLLED_TASK_TERMINOLOGY_INTEGRATION_V1",
    "lean-discipline": "CONTROLLED_TASK_LEAN_DISCIPLINE_V1",
    "internal-skill-routing": "CONTROLLED_TASK_INTERNAL_SKILL_ROUTING_V1",
    "bootstrap-load-budget": "CONTROLLED_TASK_BOOTSTRAP_LOAD_BUDGET_V1",
    "respec-impact-set": "CONTROLLED_TASK_RESPEC_IMPACT_SET_V1",
    "package-shape-claims": "CONTROLLED_TASK_PACKAGE_SHAPE_CLAIMS_V1",
    "mini-audit-loop": "CONTROLLED_TASK_MINI_AUDIT_LOOP_V1",
    "action-selection-contract": "CONTROLLED_TASK_ACTION_SELECTION_CONTRACT_V1",
    "custody-append": "CONTROLLED_TASK_CUSTODY_APPEND_V1",
}


def create_finite_leaf_session(source_root, output, *, profile="CONTROLLED_TASK_AUDIT_SPEC_V1", max_age=3600):
    """Acquire one explicitly qualified original node through the existing runner."""
    global _FINITE_LEAF
    if _FINITE_LEAF is None:
        path = ROOT / "scripts/qualify-work-graph-finite-leaf.py"
        data = VerifierTaskSession._regular(path)[1]
        spec = importlib.util.spec_from_file_location("verifier_finite_leaf", path)
        module = importlib.util.module_from_spec(spec)
        exec(compile(data, str(path), "exec"), module.__dict__)
        _FINITE_LEAF = module, data
    module, data = _FINITE_LEAF
    module.contract_for(profile)
    if profile not in _FINITE_SESSIONS:
        _FINITE_SESSIONS[profile] = module.bind_session(VerifierTaskSession, WG, ROOT, data, profile=profile)
    return _FINITE_SESSIONS[profile](source_root, output, max_age=max_age)


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


def _preflight_git_index_v1(data, *, ordinary_only=False):
    """Admit inline SHA-1 indexes before Git can touch a shared-index file.

    Decode entry boundaries, not a substring search: ordinary filenames and
    object IDs may contain 'link'. This does not interpret split-index data.
    """
    if type(ordinary_only) is not bool:
        raise WG.WorkGraphError("preflight Git index profile must be explicit")
    error = "preflight Git observation refuses malformed or unsupported index structure"
    end = len(data) - 20
    if (end < 12 or data[:4] != b"DIRC" or
            hashlib.sha1(data[:end]).digest() != data[end:]):
        raise WG.WorkGraphError(error)
    version, entries = struct.unpack_from(">II", data, 4)
    if version not in {2, 3, 4} or entries > (end - 12) // 63:
        raise WG.WorkGraphError(error)
    if ordinary_only and (version != 2 or entries > 4096):
        raise WG.WorkGraphError("finite Git source requires a bounded ordinary version-2 index")
    ordinary_paths, previous_name = [], b""
    offset, previous_length = 12, 0
    for _ in range(entries):
        start = offset
        if offset + 62 > end:
            raise WG.WorkGraphError(error)
        flags = struct.unpack_from(">H", data, offset + 60)[0]
        if ordinary_only and (flags & 0xf000 or struct.unpack_from(">I", data, start + 24)[0] not in {0o100644, 0o100755}):
            raise WG.WorkGraphError("finite Git source refuses staged, extended, assumed-valid or nonregular index entries")
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
        if ordinary_only:
            raw_name = data[offset:nul]
            try:
                name = raw_name.decode("utf-8", "strict")
            except UnicodeDecodeError:
                raise WG.WorkGraphError("finite Git source requires UTF-8 index paths") from None
            if (not raw_name or len(raw_name) > 2048 or raw_name <= previous_name or
                    any(ord(character) < 32 or ord(character) == 127 for character in name) or
                    any(part in {"", ".", "..", ".git"} for part in name.split("/"))):
                raise WG.WorkGraphError("finite Git source refuses unsupported or repeated index paths")
            ordinary_paths.append(name)
            previous_name = raw_name
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
        if ordinary_only and signature != b"TREE":
            raise WG.WorkGraphError("finite Git source requires only the ordinary TREE index extension")
        if size > end - offset or signature.decode("ascii") in extensions:
            raise WG.WorkGraphError(error)
        extensions.append(signature.decode("ascii"))
        offset += size
    result = dict(profile="INLINE_SHA1_V2_V3_V4_TREE_REUC", version=version,
                  entries=entries, extensions=extensions)
    if ordinary_only:
        result.update(profile="INLINE_SHA1_V2_REGULAR_STAGE_ZERO_TREE", ordinary_paths=ordinary_paths)
    return result


def _preflight_git_context_v1(*, root=None, environment=None, finite_ls_files=False,
                              finite_skill_layout=False, finite_controller_population=False):
    """Admit the actual declared context; never silently discard Git config.

    The caller must already have excluded system/global config and system
    attributes in the intended run environment. Other selectors are refused.
    The finite local config subset and physical selections are digest-bound.
    """
    if (any(type(value) is not bool for value in
            (finite_ls_files, finite_skill_layout, finite_controller_population)) or
            sum((finite_ls_files, finite_skill_layout, finite_controller_population)) > 1):
        raise WG.WorkGraphError("preflight Git observation profile must be explicit; requires one fixed finite profile")
    finite_source = finite_ls_files or finite_skill_layout or finite_controller_population
    require_source_descriptor_api()
    if not finite_source:
        if root is not None or environment is not None:
            raise WG.WorkGraphError("preflight Git overrides require the fixed finite ls-files profile")
        root, environment = ROOT, dict(os.environ)
    else:
        if (root is None or not Path(root).is_absolute() or ".." in Path(root).parts or
                type(environment) is not dict or environment.get("HOME") != "/nonexistent" or
                "SUDO_UID" in environment or "SUDO_GID" in environment or "SUDO_USER" in environment):
            raise WG.WorkGraphError("finite Git source requires its declared root and closed owner/startup environment")
        root, environment = Path(root), dict(environment)
    required = dict(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_ATTR_NOSYSTEM="1")
    allowed = dict(required, GIT_OPTIONAL_LOCKS=None, GIT_PAGER=None)
    if finite_source:
        required.update(GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
                        GIT_TERMINAL_PROMPT="0", GIT_EXEC_PATH="/nonexistent")
        allowed.update(required)
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
    lookup = os.pathsep.join(str(Path(part) if Path(part).is_absolute() else root / part)
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
    controls, control_bytes = [], {}

    def acquire(path, **options):
        record, data = _preflight_git_file_v1(path, **options)
        if finite_source and data is not None:
            control_bytes[str(path)] = data
        controls.append(record)
        return data

    marker = root / ".git"
    state = marker.lstat()
    if stat.S_ISDIR(state.st_mode):
        gitdir = marker
        controls.append(dict(path=str(marker), kind="DIRECTORY", mode=stat.S_IMODE(state.st_mode)))
    elif stat.S_ISREG(state.st_mode):
        raw = acquire(marker, required=True)
        if re.fullmatch(rb"gitdir: [^\x00-\x1f\x7f]+\r?\n?", raw) is None:
            raise WG.WorkGraphError("preflight Git observation refuses unsupported Git directory selection")
        declared = Path(os.fsdecode(raw[8:].rstrip(b"\r\n")))
        gitdir = Path(os.path.abspath(declared if declared.is_absolute() else root / declared))
    else:
        raise WG.WorkGraphError("preflight Git observation refuses aliased Git directory selection")
    raw = acquire(gitdir / "commondir")
    common = gitdir
    if raw is not None:
        if re.fullmatch(rb"[^\x00-\x1f\x7f]+\r?\n?", raw) is None:
            raise WG.WorkGraphError("preflight Git observation refuses unsupported common directory selection")
        declared = Path(os.fsdecode(raw.rstrip(b"\r\n")))
        common = Path(os.path.abspath(declared if declared.is_absolute() else gitdir / declared))
    ownership = {}
    if finite_source:
        if gitdir != marker or common != marker:
            raise WG.WorkGraphError("finite Git source requires complete standalone local storage")
        for label, path in (("source", root), ("git", gitdir)):
            info = path.lstat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid():
                raise WG.WorkGraphError("finite Git source requires the actual producer-owned repository")
            ownership[label] = dict(uid=info.st_uid, gid=info.st_gid, mode=stat.S_IMODE(info.st_mode),
                                    identity=[str(value) for value in _file_identity(info)])
    config = _preflight_git_config_v1(acquire(common / "config", required=True))
    worktree_config = config.get("extensions.worktreeconfig") == "true"
    if worktree_config:
        raw = acquire(gitdir / "config.worktree")
        if raw is not None:
            config.update(_preflight_git_config_v1(raw))
    head = acquire(gitdir / "HEAD", required=True)
    if finite_source:
        if re.fullmatch(rb"(?:[0-9a-f]{40}|ref: refs/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*)\n", head) is None:
            raise WG.WorkGraphError("finite Git source refuses an unsupported discovery HEAD")
        for name in ("objects", "refs"):
            path = gitdir / name
            info = path.lstat()
            if not stat.S_ISDIR(info.st_mode) or not info.st_mode & 0o100 or info.st_uid != os.geteuid():
                raise WG.WorkGraphError("finite Git source requires actual owned searchable repository directories")
            controls.append(dict(path=str(path), kind="DIRECTORY", uid=info.st_uid, gid=info.st_gid,
                                 mode=stat.S_IMODE(info.st_mode), identity=[str(value) for value in _file_identity(info)]))
    index_format = _preflight_git_index_v1(acquire(gitdir / "index", required=True, byte_limit=EXPLICIT_FILE_LIMIT),
                                           ordinary_only=finite_source)
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
    result = dict(binding=binding, environment=dict(environment, GIT_OPTIONAL_LOCKS="0"))
    if finite_source:
        binding.update(read_profile="FINITE_ORIGINAL_LS_FILES_COMPLETE_STANDALONE_SOURCE", ownership=ownership,
                       owner_relation="ACTUAL_SOURCE_AND_GIT_UID_EQUALS_PRODUCER_NO_SAFE_DIRECTORY_OVERRIDE")
        selector = ({"finite_skill_layout": True} if finite_skill_layout else
                    {"finite_controller_population": True} if finite_controller_population else {"finite_ls_files": True})
        result.update(finite_request=dict(root=str(root), environment=environment, **selector),
                      captured_control_bytes=control_bytes)
        if finite_skill_layout:
            # The fixed pathspec can select indexed descendants too. Bound all
            # possible quoted names without predicting the original decision.
            stdout_bound = sum(4 * len(name.encode("utf-8")) + 3 for name in index_format["ordinary_paths"])
            if stdout_bound > 16 * 1024**2:
                raise WG.WorkGraphError("finite skill-layout Git observation exceeds stream capacity")
            binding.update(read_profile="FINITE_ORIGINAL86_SKILL_LAYOUT_TRACKED_PATH",
                           observation_bounds=dict(stdout_bytes=stdout_bound, stderr_bytes=64 * 1024))
    if finite_controller_population:
        binding.update(read_profile="FINITE_ORIGINAL73_LEGACY_CONTROLLER_POPULATION", ownership=ownership,
                       owner_relation="ACTUAL_SOURCE_AND_GIT_UID_EQUALS_PRODUCER_NO_SAFE_DIRECTORY_OVERRIDE")
        result.update(finite_request=dict(root=str(root), environment=environment, finite_controller_population=True),
                      captured_control_bytes=control_bytes)
    return result


def _preflight_git_capture_v1(context, args):
    allowed = {("ls-files", "-z"), ("ls-files", "--others", "--exclude-standard", "-z"),
               ("ls-files", "--stage", "-z"), ("rev-parse", "HEAD"), ("rev-parse", "HEAD^{tree}"),
               ("rev-parse", "--symbolic-full-name", "HEAD"),
               ("status", "--porcelain=v1", "-z", "--untracked-files=all"),
               ("for-each-ref", "--sort=refname", "--format=%(refname)%00%(objectname)%00%(*objectname)%00%(symref)")}
    request = context.get("finite_request", {})
    skill_layout = request.get("finite_skill_layout") is True
    if skill_layout:
        allowed = {("ls-files", "--error-unmatch", "skills/SKILL.md")}
    elif request.get("finite_controller_population") is True:
        allowed = {("rev-parse", "--show-toplevel"),
            ("for-each-ref", "--format=%(refname)%09%(symref)%09%(objecttype)",
             "refs/implementaudit/controllers/", "refs/implementaudit/current-generations/",
             "refs/implementaudit/current-generation-migrations/")}
    elif request:
        allowed = {("ls-files", "-z")}
    if (args not in allowed or
            _preflight_git_context_v1(**request) != context):
        raise WG.WorkGraphError("preflight Git observation context or fixed command changed")
    selected = context["binding"]["executable"]["resolved_path"]
    fd = os.open(selected, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        if [str(value) for value in _file_identity(os.fstat(fd))] != context["binding"]["executable_file_identity"]:
            raise WG.WorkGraphError("preflight Git observation executable changed")
        try:
            if skill_layout:
                observed = subprocess.run([selected, "--no-pager", *args], cwd=Path(request["root"]),
                    env=context["environment"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    executable="/proc/self/fd/" + str(fd), pass_fds=(fd,), timeout=15)
                bounds = context["binding"]["observation_bounds"]
                if (observed.returncode not in (0, 1) or len(observed.stdout) > bounds["stdout_bytes"] or
                        len(observed.stderr) > bounds["stderr_bytes"]):
                    raise WG.WorkGraphError("finite skill-layout Git observation has an unsupported result or stream")
                value = dict(exit=observed.returncode, stdout=observed.stdout, stderr=observed.stderr)
            elif request.get("finite_controller_population") is True:
                observed = subprocess.run([selected, "--no-pager", *args], cwd=Path(request["root"]),
                    env=context["environment"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    executable="/proc/self/fd/" + str(fd), pass_fds=(fd,), timeout=15)
                if observed.returncode != 0 or observed.stderr:
                    raise WG.WorkGraphError("preflight Git controller-population read refused its actual exit or stderr")
                value = observed.stdout
            else:
                value = subprocess.check_output([selected, "--no-pager", *args], cwd=Path(request["root"]) if request else ROOT,
                    env=context["environment"], stdin=subprocess.DEVNULL, stderr=subprocess.PIPE,
                    executable="/proc/self/fd/" + str(fd), pass_fds=(fd,), timeout=15)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            raise WG.WorkGraphError("preflight Git observation fixed read command failed") from None
    finally:
        os.close(fd)
    if _preflight_git_context_v1(**request) != context:
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


def _verifier_pair_plan_v1_or_v2(plan):
    """One strict parser for diagnostic plans and actual retention dispatch."""
    encoded = WG.canonical_json_v1(plan)
    if len(encoded) > 65536:
        raise WG.WorkGraphError("preflight plan exceeds byte limit")
    plan = WG.decode_strict_json_bytes(encoded, "preflight plan")
    _preflight_fields(plan, {"schema", "expected_currentness", "runs"}, "plan")
    if type(plan["schema"]) is not str or plan["schema"] not in {
            "implementaudit.verifier-pair-plan.v1", "implementaudit.verifier-pair-plan.v2"}:
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
        fields = {"mode", "output", "base_environment_sha256", "capture"}
        if plan["schema"].endswith(".v2"):
            fields.add("retention")
        _preflight_fields(route, fields, "route")
        if type(route["mode"]) is not str or route["mode"] not in {"legacy", "dag"}:
            raise WG.WorkGraphError("preflight route pair requires exactly legacy and dag")
        _preflight_path(route["output"], "output")
        if "retention" in route:
            _preflight_path(route["retention"], "retention")
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
    return plan, encoded


def _capture_plan_paths(plan):
    if plan["schema"] != "implementaudit.verifier-pair-plan.v2":
        raise WG.WorkGraphError("capture retention requires a v2 paired plan")
    routes = plan["runs"]
    workspace = Path(routes[0]["output"])
    sinks = [Path(route["retention"]) for route in routes]
    if (routes[1]["output"] != str(workspace) or len(set(sinks + [workspace])) != 3 or
            any(path.parent != workspace.parent for path in sinks) or
            workspace.parent == ROOT or ROOT in workspace.parent.parents):
        raise WG.WorkGraphError("capture retention requires one actual workspace and distinct sibling sinks outside source")
    return workspace, sinks


def preflight_verifier_pair_v1(plan):
    """Diagnose a bound paired plan; never execute, authorize, or claim equality."""
    plan, encoded = _verifier_pair_plan_v1_or_v2(plan)
    expected, routes = plan["expected_currentness"], plan["runs"]
    retained = plan["schema"].endswith(".v2")
    before = verifier_preflight_currentness_v1()
    reasons, false = set(), set()
    identities = {r["mode"]: _preflight_capture_identity_v1(r, before["base_environment_sha256"]) for r in routes}
    outputs = [Path(r["output"]) for r in routes]
    if not retained and (outputs[0] == outputs[1] or outputs[0] in outputs[1].parents or outputs[1] in outputs[0].parents):
        reasons.add("OUTPUT_NAMESPACE_COLLISION")
    if retained:
        workspace, sinks = _capture_plan_paths(plan)
        parent = _capture_directory(workspace.parent)
        try:
            _capture_private(parent)
            _capture_parent_population(parent, workspace, sinks)
        finally:
            os.close(parent)
        if any(os.path.lexists(path) for path in sinks):
            reasons.add("RETENTION_ALREADY_EXISTS")
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
    return dict(schema="implementaudit.verifier-pair-preflight.v2" if retained else "implementaudit.verifier-pair-preflight.v1",
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


def _read_verifier_pair_plan_file(path):
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
    plan, encoded = _verifier_pair_plan_v1_or_v2(WG.decode_strict_json_bytes(data, "preflight plan"))
    return plan, sha(data), sha(encoded)


def preflight_verifier_pair_file_v1(path):
    plan, file_digest, _ = _read_verifier_pair_plan_file(path)
    result = preflight_verifier_pair_v1(plan)
    result["plan_file_sha256"] = file_digest
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "BLOCKED" else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["legacy", "dag", "compare", "preflight", "scoped", "registry", "prefix", "prefix24", "composite-prefix", *_FINITE_MODES])
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--retain-repro-assets", action="store_true")
    parser.add_argument("--capture-dist", action="store_true")
    parser.add_argument("--retain-portal-events", "--capture-portal-events", dest="capture_portal_events", action="store_true")
    parser.add_argument("--retain-repro-events", action="store_true")
    parser.add_argument("--retention-plan", type=Path,
                        help="v2 paired plan: use one actual capture workspace and distinct sealed destinations")
    stdin = parser.add_mutually_exclusive_group()
    stdin.add_argument("--stdin-file")
    stdin.add_argument("--empty-stdin", action="store_true")
    args = parser.parse_args()
    try:
        if args.retention_plan is not None and args.mode not in {"legacy", "dag", "compare"}:
            raise WG.WorkGraphError("retention-plan requires a legacy, dag or sealed compare operation")
        if args.mode not in {"legacy", "dag"} and (args.retain_repro_assets or args.stdin_file is not None or args.empty_stdin or args.capture_dist or args.capture_portal_events or args.retain_repro_events):
            raise WG.WorkGraphError("explicit acquisition options require a legacy or dag capture")
        if args.mode == "preflight" and len(args.paths) == 1:
            return preflight_verifier_pair_file_v1(args.paths[0])
        if args.mode in {"scoped", "registry", "prefix", "prefix24", "composite-prefix", *_FINITE_MODES} and len(args.paths) == 2:
            prefix_mode = args.mode in {"prefix", "prefix24", "composite-prefix"}
            finite_mode = args.mode in _FINITE_MODES
            bounded_mode = prefix_mode or finite_mode
            if finite_mode:
                session = create_finite_leaf_session(*args.paths, profile=_FINITE_MODES[args.mode])
            elif prefix_mode:
                profile = {"prefix": "COMPOSED_SOURCE_PREFIX_23_V1", "prefix24": "COMPOSED_SOURCE_PREFIX_24_V1",
                           "composite-prefix": "COMPOSED_COMPOSITE_PREFIX_23_V1"}[args.mode]
                session = create_composed_prefix_session(*args.paths, profile=profile)
            else:
                session = {"scoped": VerifierTaskSession, "registry": RegistryVerifierTaskSession}[args.mode](*args.paths)
            # A caller may request another current-source consumption, never
            # inject a receipt, plan, mutation command or claimed process exit.
            status = 0
            requests = iter(lambda: sys.stdin.buffer.readline(4097), b"") if bounded_mode else sys.stdin.buffer
            for line in requests:
                if bounded_mode and len(line) > 4096:
                    raise WG.WorkGraphError(("prefix" if prefix_mode else "finite-leaf") + " request exceeds its byte bound")
                if WG.decode_strict_json_bytes(line, "scope request") != {"operation": "run"}:
                    raise WG.WorkGraphError("only a current-source run request is supported")
                result = session.run()
                code = result["exit"]
                if bounded_mode and (code < 0 or not result["complete"]):
                    code = 1
                status = max(status, code)
                print(json.dumps(result, sort_keys=True), flush=True)
            return status
        if args.mode == "compare" and len(args.paths) == 3:
            if args.retention_plan is not None:
                return _compare_sealed_captures(*(path.absolute() for path in args.paths), args.retention_plan)
            return compare(*args.paths)
        if args.mode in {"legacy", "dag"} and len(args.paths) == 1:
            return run(args.mode, args.paths[0].absolute() if args.retention_plan is not None else args.paths[0].resolve(), retain_repro_assets=args.retain_repro_assets,
                       stdin_file=args.stdin_file, empty_stdin=args.empty_stdin, capture_dist=args.capture_dist,
                       capture_portal_events=args.capture_portal_events, retain_repro_events=args.retain_repro_events,
                       retention_plan=args.retention_plan)
        parser.error("run takes one fresh output directory; compare takes two run directories and a fresh result path; preflight takes one plan file")
    except (OSError, ValueError, KeyError, TypeError, WG.WorkGraphError, subprocess.SubprocessError) as exc:
        print("work-graph-verifier: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
