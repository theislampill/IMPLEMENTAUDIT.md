#!/usr/bin/env python3
"""Data-only input observation for original48; no executor or receipt issuer.

Only the separate fixed loader supplies this module's executing buffers and
prefix owner. Missing compressor/runtime/custody gates remain explicit. The
result is not a canonical completion, live producer, or before-consumer JOIN.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import types

PROFILE = "ORIGINAL48_SYSTEM_PYTHON312_DATA_ONLY_V1"
FIXTURE = "fixtures/work-graph-c5-inputs/system-python312.json"
MODULE = "scripts/work-graph-c5-inputs.py"
_CAPTURE = globals().pop("_R0035_C5_INPUT_CAPTURE", None)
if not isinstance(_CAPTURE, dict) or set(_CAPTURE) != {"prefix", "sources", "check"}:
    raise RuntimeError("C5 inputs require the separate fixed captured-source loader")
P = _CAPTURE["prefix"]
_CHECK = _CAPTURE["check"]
SPEC = json.loads(_CAPTURE["sources"][FIXTURE][0])
if SPEC.get("schema") != "implementaudit.c5-input-selection.v1" or SPEC.get("profile") != PROFILE:
    raise ValueError("unsupported fixed C5 selection")
_ENVIRONMENT = dict(P.ENVIRONMENT)
_PYTHON_ALIASES = tuple(parent + "/" + name for parent in ("/usr/bin", "/bin")
                        for name in ("python", "python3"))
_SITE_ROOTS = tuple(SPEC["site_roots"])
_SEARCH_ROOTS = ("/usr/lib/python3.12", "/usr/lib/python3.12/lib-dynload", *_SITE_ROOTS)
_ABSENT = ("/usr/lib/python312.zip", "/usr/pyvenv.cfg", "/usr/bin/pyvenv.cfg", "/bin/pyvenv.cfg",
           "/pyvenv.cfg", "/usr/bin/python3.12._pth", "/usr/bin/python3._pth", "/usr/bin/python._pth",
           "/bin/python3.12._pth", "/bin/python3._pth", "/bin/python._pth")
_NSCD = ("/var/run/nscd/socket", "/run/nscd/socket", "/var/db/nscd/passwd", "/run/nscd/passwd", "/etc/nscd.conf")
_SITE = "/usr/lib/python3.12/sitecustomize.py"
_PTH = "/usr/lib/python3/dist-packages/coloredlogs.pth"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require_same(before, after, label):
    if before != after:
        raise ValueError("C5 " + label + " changed during data capture")


def _directory_identity(info):
    return [str(info.st_dev), str(info.st_ino), info.st_mode, info.st_uid, info.st_gid]


def _ancestors(path):
    """Return every actual no-follow absolute ancestor, not just a file stat."""
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("C5 absolute paths without traversal are required")
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    result, current = {"/": _directory_identity(os.fstat(fd))}, Path("/")
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
            current /= part
            result[str(current)] = _directory_identity(os.fstat(fd))
        return result
    finally:
        os.close(fd)


def _aliases(path):
    current, rows = Path("/"), {}
    for component in path.parts[1:]:
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError:
            break
        rows[str(current)] = dict(identity=P.identity(info),
            link=os.readlink(current) if stat.S_ISLNK(info.st_mode) else None)
    return rows


def capture_selector(path, objects, *, limit=32 * 1024**2):
    """Bound actual aliases, bytes and physical ancestors; never execute them."""
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("unsupported C5 selector path")
    aliases = _aliases(path)
    try:
        info = path.lstat()
    except FileNotFoundError:
        nearest, missing = path, []
        while not nearest.exists():
            if nearest.is_symlink():
                raise ValueError("broken C5 selector alias")
            missing.insert(0, nearest.name)
            nearest = nearest.parent
        resolved = nearest.resolve(strict=True)
        ancestors = _ancestors(resolved)
        result = dict(kind="MISSING", nearest=str(resolved), missing=missing,
                      aliases=aliases, ancestors=ancestors)
        require_same(aliases, _aliases(path), "missing selector aliases")
        require_same(ancestors, _ancestors(resolved), "missing selector ancestors")
        return result
    resolved = path.resolve(strict=True)
    target = resolved.lstat()
    ancestors = _ancestors(resolved.parent)
    result = dict(resolved=str(resolved), aliases=aliases, ancestors=ancestors,
                  link=os.readlink(path) if stat.S_ISLNK(info.st_mode) else None)
    if stat.S_ISDIR(target.st_mode):
        result.update(kind="DIRECTORY", identity=P.identity(target), mode=stat.S_IMODE(target.st_mode))
    elif stat.S_ISREG(target.st_mode):
        metadata, raw = P.read_regular(resolved, limit, single_link=False)
        owner = resolved.lstat()
        require_same(metadata["identity"], P.identity(owner), "file owner/identity")
        key = digest(raw)
        objects.setdefault(key, raw)
        result.update(kind="FILE", mode=metadata["mode"], bytes=len(raw), sha256=key,
                      identity=metadata["identity"], uid=owner.st_uid, gid=owner.st_gid)
    else:
        raise ValueError("unsupported C5 selector type")
    require_same(aliases, _aliases(path), "selector aliases")
    require_same(ancestors, _ancestors(resolved.parent), "selector ancestors")
    require_same(P.identity(target), P.identity(resolved.lstat()), "selector target")
    return result


def complete_source(root, objects):
    """All actual ordinary source/Git/hidden bytes and empty directories."""
    root = Path(root)
    ancestors = _ancestors(root)
    state, stamps = P.snapshot_tree(root, objects, P.SOURCE_BOUNDS)
    require_same(ancestors, _ancestors(root), "source ancestors")
    return dict(state=state, stamps=stamps, ancestors=ancestors,
                projection="ALL_ACTUAL_BYTES_NO_GIT_OR_HIDDEN_OMISSIONS")


def _namespace(name, objects):
    observed = capture_selector(name, objects)
    row = dict(observation=observed, names={}, pth={})
    if observed["kind"] == "MISSING":
        return row
    if observed["kind"] != "DIRECTORY":
        raise ValueError("C5 import-search root is not a directory")
    fd = P.open_directory(observed["resolved"])
    try:
        before = P.identity(os.fstat(fd))
        name_bytes = startup_bytes = 0
        with os.scandir(fd) as entries:
            for entry in entries:
                P.safe_name(entry.name)
                name_bytes += len(entry.name.encode())
                if len(row["names"]) >= 4096 or name_bytes > 128 * 1024:
                    raise ValueError("C5 import namespace exceeds fixed bounds")
                row["names"][entry.name] = P.identity(os.stat(entry.name, dir_fd=fd, follow_symlinks=False))
                if name in _SITE_ROOTS and entry.name.endswith(".pth") and not entry.name.startswith("."):
                    datum = capture_selector(Path(name) / entry.name, objects, limit=65536)
                    if datum["kind"] != "FILE":
                        raise ValueError("C5 .pth input is not an ordinary file")
                    startup_bytes += datum["bytes"]
                    if len(row["pth"]) >= 128 or startup_bytes > 1024**2:
                        raise ValueError("C5 startup files exceed fixed bounds")
                    row["pth"][entry.name] = datum
        require_same(before, P.identity(os.fstat(fd)), "import namespace")
    finally:
        os.close(fd)
    require_same(observed, capture_selector(name, {}), "import namespace path")
    return row


def validate_startup(observed, objects):
    if observed["environment"] != _ENVIRONMENT or any(k in observed["environment"] for k in ("HOME", "PYTHONUSERBASE", "COLOREDLOGS_AUTO_INSTALL")):
        raise ValueError("C5 normal startup environment changed")
    if observed["identity"] != dict(uid=0, euid=0, gid=0, egid=0):
        raise ValueError("C5 selected system NSS profile requires actual UID/GID zero")
    if set(observed["aliases"]) != set(_PYTHON_ALIASES) or set(observed["absent"]) != set(_ABSENT):
        raise ValueError("C5 interpreter selector coverage is incomplete")
    if any(row["kind"] != "MISSING" for row in observed["absent"].values()):
        raise ValueError("C5 added venv/zip/path selector requires a separate closure")
    expected = SPEC["runtime_pins"][SPEC["python_target"]]
    for row in observed["aliases"].values():
        if row["kind"] != "MISSING" and (row["kind"] != "FILE" or row["resolved"] != SPEC["python_target"] or row["sha256"] != expected["sha256"] or row["mode"] != 0o755):
            raise ValueError("C5 selected interpreter alias is outside the captured profile")
    if set(observed["namespaces"]) != set(_SEARCH_ROOTS):
        raise ValueError("C5 startup namespace coverage is incomplete")
    count = size = 0
    for root, namespace in observed["namespaces"].items():
        if namespace["observation"]["kind"] == "MISSING":
            if root not in _SITE_ROOTS or namespace["names"] or namespace["pth"]:
                raise ValueError("C5 required import root is absent")
            continue
        for name in namespace["names"]:
            if name == "apport_python_hook" or name.startswith("apport_python_hook."):
                raise ValueError("C5 apport startup provider is not closed")
            if any(name == stem or name.startswith(stem + ".") for stem in ("sitecustomize", "usercustomize")):
                if root + "/" + name != _SITE or observed["files"].get(_SITE, {}).get("kind") != "FILE":
                    raise ValueError("C5 added startup customizer is not closed")
        names = {n for n in namespace["names"] if root in _SITE_ROOTS and n.endswith(".pth") and not n.startswith(".")}
        if names != set(namespace["pth"]):
            raise ValueError("C5 .pth namespace coverage is incomplete")
        for name, row in namespace["pth"].items():
            raw = objects.get(row["sha256"], b"")
            if digest(raw) != row["sha256"] or len(raw) != row["bytes"]:
                raise ValueError("C5 startup bytes are unavailable")
            count += 1
            size += len(raw)
            if count > 128 or size > 1024**2:
                raise ValueError("C5 combined .pth input bound exceeded")
            if root + "/" + name == _PTH and row["sha256"] == SPEC["runtime_pins"][_PTH]["sha256"]:
                continue
            if any(line.strip() and not line.startswith("#") for line in raw.decode("ascii", "strict").splitlines()):
                raise ValueError("C5 added executable/path-extending .pth is not closed")
    for name in ("/etc/passwd", "/etc/nsswitch.conf"):
        row = observed["files"][name]
        raw = objects[row["sha256"]]
        if row["kind"] != "FILE" or row["resolved"] != name or row["mode"] != 0o644 or not 0 < len(raw) <= 65536 or b"\0" in raw:
            raise ValueError("C5 actual NSS input is unsupported")
        raw.decode("ascii", "strict")
    config = objects[observed["files"]["/etc/nsswitch.conf"]["sha256"]].decode("ascii")
    passwd = [line.split("#", 1)[0].strip() for line in config.splitlines()]
    passwd = [line for line in passwd if line.partition(":")[0].strip() == "passwd"]
    if len(passwd) != 1 or passwd[0].partition(":")[2].split() != ["files"]:
        raise ValueError("C5 actual passwd NSS selection is not files-only")
    matches = []
    for line in objects[observed["files"]["/etc/passwd"]["sha256"]].decode("ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split(":")
        if len(fields) != 7 or not fields[2].isdigit() or not fields[3].isdigit():
            raise ValueError("C5 passwd syntax is unsupported")
        if int(fields[2]) == 0:
            matches.append(fields)
    if len(matches) != 1 or not matches[0][5].startswith("/"):
        raise ValueError("C5 actual UID0 passwd home is unqualified")
    if set(observed["nscd"]) != set(_NSCD) or any(row["kind"] != "MISSING" for row in observed["nscd"].values()):
        raise ValueError("C5 NSCD selector is not closed")


def selected_startup(objects):
    """Actual supported system interpreter/normal site inputs, without imports."""
    files = {}
    for name, pin in SPEC["runtime_pins"].items():
        row = capture_selector(name, objects)
        if row["kind"] != "FILE" or any(row[key] != pin[key] for key in ("sha256", "bytes", "mode", "resolved", "link")):
            raise ValueError("C5 selected startup/native source differs: " + name)
        files[name] = row
    for name in ("/etc/nsswitch.conf", "/etc/passwd"):
        files[name] = capture_selector(name, objects, limit=65536)
    aliases = {name: capture_selector(name, objects) for name in _PYTHON_ALIASES}
    selected = next((name for command in ("python", "python3") for parent in ("/usr/bin", "/bin")
                     if aliases[name := parent + "/" + command]["kind"] == "FILE"), None)
    if selected is None:
        raise ValueError("C5 actual Python selector is absent")
    namespaces = {name: _namespace(name, objects) for name in _SEARCH_ROOTS}
    providers = {root: sorted(name for name in namespace["names"] if name.casefold().startswith("zopfli"))
                 for root, namespace in namespaces.items()}
    present = any(providers.values())
    result = dict(environment=dict(_ENVIRONMENT), identity=dict(uid=os.getuid(), euid=os.geteuid(), gid=os.getgid(), egid=os.getegid()),
        files=files, aliases=aliases, absent={name: capture_selector(name, objects) for name in _ABSENT},
        nscd={name: capture_selector(name, objects) for name in _NSCD}, namespaces=namespaces,
        selected_command=Path(selected).name, selected_path=selected, selected_target=aliases[selected]["resolved"],
        startup="NORMAL_SITE_NO_ORIGINAL_S_OR_I", compressor=dict(distribution="zopfli", required_version="0.2.3.post1",
            status="PRESENT_UNQUALIFIED_REQUIRES_EXACT_CLOSURE" if present else "MISSING_GENUINE_PROVIDER",
            providers=providers, provider_imports=0, runtime_complete=False))
    validate_startup(result, objects)
    return result


def _runtime_inputs(objects):
    """Actual file capture only: no generated Python wrapper enters the set."""
    names = {"/usr/bin/" + n for n in P.TOOLS}
    names.update("/lib/x86_64-linux-gnu/" + n for n in P.LIBRARIES)
    names.update(("/lib64/ld-linux-x86-64.so.2", "/bin/bash", "/bin/sh"))
    pending, directories = [(Path("/usr/lib/python3.12"), 0)], {}
    while pending:
        path, depth = pending.pop()
        if depth > P.RUNTIME_BOUNDS["depth"]:
            raise ValueError("C5 runtime depth bound exceeded")
        fd = P.open_directory(path)
        try:
            before = P.identity(os.fstat(fd))
            rows = {}
            with os.scandir(fd) as entries:
                for entry in entries:
                    P.safe_name(entry.name)
                    info = os.stat(entry.name, dir_fd=fd, follow_symlinks=False)
                    rows[entry.name] = P.identity(info)
                    # Site roots are separately closed, including every .pth.
                    if entry.name in {"site-packages", "dist-packages", "sitecustomize.py"}:
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        pending.append((path / entry.name, depth + 1))
                    elif stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
                        names.add(str(path / entry.name))
                    else:
                        raise ValueError("C5 runtime contains an unsupported member")
                    if len(names) + len(directories) + len(pending) > P.RUNTIME_BOUNDS["entries"]:
                        raise ValueError("C5 runtime population bound exceeded")
            require_same(before, P.identity(os.fstat(fd)), "runtime directory")
            directories[str(path)] = dict(identity=before, ancestors=_ancestors(path), names=rows)
        finally:
            os.close(fd)
    files = {name: capture_selector(name, objects) for name in sorted(names)}
    if any(row["kind"] != "FILE" for row in files.values()):
        raise ValueError("C5 required base runtime input is absent")
    if sum(row["bytes"] for row in files.values()) > P.RUNTIME_BOUNDS["mounted_bytes"]:
        raise ValueError("C5 runtime bytes exceed fixed acquisition bound")
    startup = selected_startup(objects)
    for name, row in startup["aliases"].items():
        if row["kind"] == "FILE":
            files[name] = row
    files.update(startup["files"])
    for root, namespace in startup["namespaces"].items():
        files.update({root + "/" + name: row for name, row in namespace["pth"].items()})
    P.runtime_budget(files, P.RUNTIME_BOUNDS)
    return dict(files=files, directories=directories, startup=startup,
                execution_image="NOT_CONSTRUCTED", bytecode="ACTUAL_STDLIB_CACHE_BYTES_INCLUDED")


def _producer_contract(state):
    for name, pin in SPEC["programs"].items():
        if state["files"].get(name, {}).get("sha256") != pin:
            raise ValueError("C5 original producer source differs: " + name)
    payload = {name for name in state["files"] if name.startswith("skills/implementaudit/")}
    expected = {name for name in SPEC["payload_sources"] if name.startswith("skills/implementaudit/")}
    if payload != expected or any(name not in state["files"] for name in SPEC["payload_sources"]):
        raise ValueError("C5 actual package source selector population differs")
    members = ("IMPLEMENTAUDIT.plugin.zip", "IMPLEMENTAUDIT.skill", "CHECKSUMS.txt")
    roles = ["build:a", "build:b", *("cmp:" + n for n in members), "checksum:a", "checksum:b",
             "manifest:plugin:a", "manifest:plugin:b", "manifest-cmp:plugin",
             "manifest:skill:a", "manifest:skill:b", "manifest-cmp:skill",
             "hash:skill:a", "hash:skill:b", "hash:plugin:a", "hash:plugin:b", "hash:checksums:a", "hash:checksums:b"]
    return dict(original_index=48, original_command=SPEC["original"]["command"],
        checkout=dict(clones=2, clone_flags=["--quiet", "--no-local", "--no-checkout"],
            checkout_flags=["--quiet", "--detach"], status="--porcelain", lifetime="BOTH_WORKTREES_RETAINED_UNTIL_ORIGINAL_EXIT"),
        expected_archive_members=SPEC["expected_archive_members"], roles=roles,
        release_producers=[dict(role="build:" + lane, path="out-" + lane + "/" + name) for lane in "ab" for name in members],
        compressor="GENUINE_ZOPFLI_0.2.3.post1_REQUIRED_NO_SUBSTITUTE", selected_programs=SPEC["programs"])


class C5Inputs:
    """Capture observations only; there is deliberately no run/receipt API."""
    def __init__(self, source_root):
        self.source = Path(source_root)
        _ancestors(self.source)
        _CHECK()

    def acquire(self):
        _CHECK()
        objects = {}
        source = complete_source(self.source, objects)
        contract = _producer_contract(source["state"])
        blockers = ["LIVE_PRODUCER_CUSTODY_UNIMPLEMENTED", "BEFORE_CONSUMER_JOIN_UNIMPLEMENTED",
                    "GIT_CLONE_EXECUTION_RUNTIME_UNQUALIFIED", "ACTUAL_C5_RESOURCE_PROFILE_UNQUALIFIED"]
        if ".git" in source["state"]["directories"]:
            P.validate_git_namespace(source["state"], objects)
            git = "COMPLETE_PRESENT_GIT_BYTES_CAPTURED_NO_GIT_COMMAND"
        else:
            blockers.append("STANDALONE_GIT_INPUT_MISSING")
            git = "MISSING_NO_SYNTHETIC_GIT_OBJECTS"
        runtime = _runtime_inputs(objects)
        status = runtime["startup"]["compressor"]["status"]
        blockers.append("ZOPFLI_PROVIDER_MISSING" if status == "MISSING_GENUINE_PROVIDER" else "PRESENT_ZOPFLI_PROVIDER_CLOSURE_UNQUALIFIED")
        require_same(source, complete_source(self.source, {}), "complete source")
        require_same(runtime, _runtime_inputs({}), "complete captured runtime/startup")
        _CHECK()
        record = dict(schema="implementaudit.c5-input-observation.v1", profile=PROFILE,
            source_root=str(self.source), source=source, runtime=runtime, git=git, producer_contract=contract,
            actual_source_files=len(source["state"]["files"]), actual_source_bytes=sum(row["bytes"] for row in source["state"]["files"].values()),
            historical_resource_observation=SPEC["historical_resource_observation"],
            input_population="CAPTURED_OBSERVATIONS_WITH_EXPLICIT_REMAINING_CLOSURE_GAPS", runtime_complete=False,
            blockers=blockers, dispatch_count=0, original_results=0, canonical_acceptance="UNQUALIFIED",
            live_producer_custody=False, before_consumer_join=False, authority="NONE")
        record["observation_sha256"] = digest(P.encode(record))
        return dict(record=record, objects=types.MappingProxyType(objects))
