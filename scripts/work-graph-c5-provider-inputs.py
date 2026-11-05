#!/usr/bin/env python3
"""Fixed genuine-venv data capture for C5; no provider import or executor."""
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import types

PROFILE = "ORIGINAL48_FIXED_PACKAGE_VENV_PYTHON312_DATA_ONLY_V1"
FIXTURE = "fixtures/work-graph-c5-inputs/package-venv-python312.json"
MODULE = "scripts/work-graph-c5-provider-inputs.py"
_CAPTURE = globals().pop("_R0035_C5_PROVIDER_CAPTURE", None)
if not isinstance(_CAPTURE, dict) or set(_CAPTURE) != {"prefix", "base", "sources", "check"}:
    raise RuntimeError("C5 provider inputs require the separate fixed captured-source loader")
P, B, _CHECK = _CAPTURE["prefix"], _CAPTURE["base"], _CAPTURE["check"]
SPEC = json.loads(_CAPTURE["sources"][FIXTURE][0])
if (SPEC.get("schema") != "implementaudit.c5-provider-selection.v1"
        or SPEC.get("profile") not in (PROFILE, "CURRENT_COMPOSITE_FIXED_PACKAGE_VENV_PYTHON312_DATA_ONLY_20261027_V1", "SOL_TASK_FIXED_PACKAGE_VENV_PYTHON312_DATA_ONLY_20261029_V1", "R4_OWNED_FIXED_PACKAGE_VENV_PYTHON312_DATA_ONLY_20261104_V1", 'R5_HOSTED_UBUNTU24_SINGLE_COPY_PYTHON312_DATA_ONLY_20261105_V1')):
    raise ValueError("unsupported fixed C5 provider selection")
PROFILE = SPEC["profile"]
VENV = Path(SPEC["provider_root"])
if not VENV.is_absolute() or ".." in VENV.parts:
    raise ValueError("fixed provider root must be absolute without traversal")
SITE = str(VENV / "lib/python3.12/site-packages")
_ENVIRONMENT = dict(P.ENVIRONMENT, PATH=str(VENV / "bin") + ":/usr/bin:/bin")
_ALIASES = tuple(str(VENV / "bin" / name) for name in ("python", "python3", "python3.12")) + B._PYTHON_ALIASES
_SEARCH = ("/usr/lib/python3.12", "/usr/lib/python3.12/lib-dynload", SITE)
_ABSENT = B._ABSENT + tuple(str(VENV / "bin" / name) for name in
    ("pyvenv.cfg", "python._pth", "python3._pth", "python3.12._pth")) + ("/etc/ld.so.preload",)
_RECORD = "lib/python3.12/site-packages/zopfli-0.2.3.post1.dist-info/RECORD"


# Only this prospective linked-image profile changes the counting unit.
# Legacy prefix and C5 profiles keep their exact logical-file accounting.
HOSTED_PROFILE = "R5_HOSTED_UBUNTU24_SINGLE_COPY_PYTHON312_DATA_ONLY_20261105_V1"
HOSTED_RUNTIME_POLICY = dict(schema="implementaudit.c5-linked-runtime-budget.v1",
    counting_unit="ONE_FILE_PER_CLOSED_RESOLVED_PATH", mounted_bytes=134217728,
    unique_bytes=134217728, total_bytes=134217728, entries=4096, file_bytes=33554432, depth=40,
    aliases="ALL_LOGICAL_SELECTORS_AND_COMPLETE_TOPOLOGY_RETAINED")


def runtime_budget_v1(entries, bounds):
    if PROFILE != HOSTED_PROFILE:
        return P.runtime_budget(entries, bounds)
    if SPEC.get("runtime_accounting") != HOSTED_RUNTIME_POLICY:
        raise ValueError("C5 hosted runtime accounting policy is not selected")
    for key in ("mounted_bytes", "unique_bytes", "total_bytes", "entries", "file_bytes", "depth"):
        if bounds.get(key) != HOSTED_RUNTIME_POLICY[key]:
            raise ValueError("C5 hosted runtime bound changed")
    if len(entries) > bounds["entries"]:
        raise ValueError("C5 hosted logical selector population exceeded")
    canonical, unique = {}, {}
    for name, row in entries.items():
        target = row.get("resolved")
        for path in (name, target):
            if (type(path) is not str or not path.startswith("/") or path.startswith("//")
                    or str(Path(path)) != path or ".." in Path(path).parts):
                raise ValueError("C5 hosted runtime path is not canonical absolute")
        size, digest, mode = (row.get(key) for key in ("bytes", "sha256", "mode"))
        if (row.get("kind", "FILE") != "FILE" or type(size) is not int or not 0 <= size <= bounds["file_bytes"]
                or type(digest) is not str or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
                or type(mode) is not int or not 0 <= mode <= 0o777):
            raise ValueError("C5 hosted runtime file descriptor differs")
        if digest in unique and unique[digest] != size:
            raise ValueError("C5 hosted runtime object length conflict")
        unique[digest] = size
        value = dict(bytes=size, sha256=digest, mode=mode)
        if target in canonical and canonical[target] != value:
            raise ValueError("C5 hosted resolved file bytes or mode conflict")
        canonical[target] = value
    totals = P.runtime_budget(canonical, bounds)
    totals.update(entries=len(entries), canonical_files=len(canonical),
        logical_bytes=sum(row["bytes"] for row in entries.values()),
        accounting="CLOSED_RESOLVED_FILES_WITH_ALL_LOGICAL_SELECTORS_RETAINED")
    return totals


def _validate_hosted_file_alias(row, root, name, target, copied):
    path = str(Path(root) / name)
    wanted = str(Path(root) / "bin/python3.12")
    alias = row.get("aliases", {}).get(path, {})
    identity = alias.get("identity", ())
    if (name not in ("bin/python", "bin/python3") or target != "python3.12"
            or row.get("kind") != "FILE" or row.get("resolved") != wanted or row.get("link") != target
            or alias.get("link") != target or len(identity) != 7 or not stat.S_ISLNK(identity[2])
            or identity[3] != 1 or row.get("link_owner") != [0, 0]
            or any(row.get(k) != copied.get(k) for k in ("bytes", "sha256", "mode", "uid", "gid"))):
        raise ValueError("C5 hosted interpreter alias differs from its owned copy")


def _capture_hosted_file_alias(root, name, target, copied, objects):
    path = Path(root) / name
    before = path.lstat()
    row = B.capture_selector(path, objects)
    if row.get("aliases", {}).get(str(path), {}).get("identity") != P.identity(before):
        raise ValueError("C5 hosted alias changed before owner capture")
    row["link_owner"] = [before.st_uid, before.st_gid]
    _validate_hosted_file_alias(row, root, name, target, copied)
    if os.listxattr(path, follow_symlinks=False):
        raise ValueError("C5 hosted file alias has extended metadata")
    after = path.lstat()
    if (P.identity(before), before.st_uid, before.st_gid) != (P.identity(after), after.st_uid, after.st_gid):
        raise ValueError("C5 hosted alias owner changed during capture")
    return row


def _directories(root):
    result = {}
    B._ancestors(root)
    for name, expected in SPEC["venv_directories"].items():
        path = root / name
        observed = B.capture_selector(path, {})
        if observed["kind"] != "DIRECTORY" or observed["resolved"] != str(path):
            raise ValueError("C5 provider directory alias is unsupported")
        fd = P.open_directory(path)
        try:
            info = os.fstat(fd)
            if stat.S_IMODE(info.st_mode) != 0o755 or os.listxattr(fd):
                raise ValueError("C5 provider directory metadata is unsupported")
            if PROFILE == HOSTED_PROFILE:
                if (info.st_uid, info.st_gid) != (0, 0) or any(
                        value[3:] != [0, 0] or stat.S_IMODE(value[2]) & 0o022
                        for value in observed["ancestors"].values()):
                    raise ValueError("C5 hosted provider ancestry is not trusted")
            before = P.identity(info)
            names, total = {}, 0
            with os.scandir(fd) as entries:
                for entry in entries:
                    P.safe_name(entry.name)
                    total += len(os.fsencode(entry.name))
                    if len(names) >= P.RUNTIME_BOUNDS["entries"] or total > 128 * 1024:
                        raise ValueError("C5 provider namespace exceeds fixed bound")
                    names[entry.name] = P.identity(os.stat(entry.name, dir_fd=fd, follow_symlinks=False))
            B.require_same(before, P.identity(os.fstat(fd)), "provider directory")
        finally:
            os.close(fd)
        if sorted(names) != expected:
            raise ValueError("C5 provider namespace differs from fixed installed population")
        B.require_same(observed, B.capture_selector(path, {}), "provider directory path")
        result[name] = dict(observation=observed, names=names)
    return result


def _capture_tree(root, objects):
    """The private reader also supports real, test-owned copies of fixed bytes."""
    root = Path(root)
    directories = _directories(root)
    files, links = {}, {}
    for name, pin in SPEC["venv_files"].items():
        row = B.capture_selector(root / name, objects, limit=P.RUNTIME_BOUNDS["file_bytes"])
        if (row["kind"] != "FILE" or row["resolved"] != str(root / name) or row["link"] is not None
                or row["identity"][3] != 1
                or any(row[key] != pin[key] for key in ("bytes", "sha256", "mode", "uid", "gid"))):
            raise ValueError("C5 provider file differs from fixed installed bytes: " + name)
        files[name] = row
    for name, expected in SPEC["venv_links"].items():
        row = B.capture_selector(root / name, objects)
        if (row["kind"] != "DIRECTORY" or row["link"] != expected or row["resolved"] != str(root / expected)
                or row["aliases"][str(root / name)]["identity"][3] != 1 or os.listxattr(root / name, follow_symlinks=False)):
            raise ValueError("C5 provider directory link changed")
        links[name] = row
    B.require_same(directories, _directories(root), "provider namespace")
    if PROFILE == HOSTED_PROFILE:
        file_aliases = {}
        if SPEC.get("venv_file_aliases") != {"bin/python":"python3.12", "bin/python3":"python3.12"}:
            raise ValueError("C5 hosted file alias population changed")
        for name, target in SPEC["venv_file_aliases"].items():
            row = _capture_hosted_file_alias(root, name, target, files["bin/python3.12"], objects)
            file_aliases[name] = row
        B.require_same(directories, _directories(root), "hosted provider namespace")
        return dict(root=str(root), files=files, directories=directories, links=links, file_aliases=file_aliases)
    return dict(root=str(root), files=files, directories=directories, links=links)


def _require_tree_current(root, captured):
    B.require_same(captured, _capture_tree(root, {}), "provider bytes/namespace/ancestors")


def _validate_record(provider, objects):
    prefix = "lib/python3.12/site-packages/"
    installed = {name[len(prefix):]: row for name, row in provider["files"].items() if name.startswith(prefix)}
    record = objects[provider["files"][_RECORD]["sha256"]]
    seen = set()
    for row in csv.reader(io.StringIO(record.decode("utf-8", "strict"))):
        if len(row) != 3:
            raise ValueError("C5 installed RECORD syntax changed")
        name, encoded, size = row
        if name in seen or name not in installed:
            raise ValueError("C5 installed RECORD population changed")
        seen.add(name)
        descriptor = installed[name]
        raw = objects[descriptor["sha256"]]
        if len(raw) != descriptor["bytes"] or B.digest(raw) != descriptor["sha256"]:
            raise ValueError("C5 installed object bytes unavailable")
        if encoded:
            expected = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip("=")
            if encoded != expected or size != str(len(raw)):
                raise ValueError("C5 installed RECORD digest/length mismatch")
        elif size or name not in SPEC["record_unhashed_rows"]:
            raise ValueError("C5 installed RECORD has an unsupported unhashed row")
    if seen != set(installed):
        raise ValueError("C5 installed RECORD omits an actual member")
    metadata = objects[installed["zopfli-0.2.3.post1.dist-info/METADATA"]["sha256"]].decode("utf-8", "strict").splitlines()
    if metadata.count("Name: zopfli") != 1 or metadata.count("Version: 0.2.3.post1") != 1:
        raise ValueError("C5 genuine provider metadata differs")


def _namespace(name, objects):
    observed = B.capture_selector(name, objects)
    if observed["kind"] != "DIRECTORY":
        raise ValueError("C5 provider import-search directory is absent")
    fd = P.open_directory(observed["resolved"])
    names, pth = {}, {}
    try:
        before = P.identity(os.fstat(fd))
        name_bytes = startup_bytes = 0
        with os.scandir(fd) as entries:
            for entry in entries:
                P.safe_name(entry.name)
                name_bytes += len(os.fsencode(entry.name))
                if len(names) >= 4096 or name_bytes > 128 * 1024:
                    raise ValueError("C5 provider import namespace exceeds fixed bound")
                names[entry.name] = P.identity(os.stat(entry.name, dir_fd=fd, follow_symlinks=False))
                if name == SITE and entry.name.endswith(".pth") and not entry.name.startswith("."):
                    row = B.capture_selector(Path(name) / entry.name, objects, limit=65536)
                    if row["kind"] != "FILE":
                        raise ValueError("C5 provider .pth is not an ordinary file")
                    startup_bytes += row["bytes"]
                    if len(pth) >= 128 or startup_bytes > 1024**2:
                        raise ValueError("C5 provider startup bytes exceed fixed bound")
                    pth[entry.name] = row
        B.require_same(before, P.identity(os.fstat(fd)), "provider import namespace")
    finally:
        os.close(fd)
    B.require_same(observed, B.capture_selector(name, {}), "provider import namespace path")
    return dict(observation=observed, names=names, pth=pth)


def _validate_nss(observed, objects):
    for name in ("/etc/passwd", "/etc/nsswitch.conf"):
        row = observed["files"][name]
        raw = objects[row["sha256"]]
        if row["kind"] != "FILE" or row["resolved"] != name or row["mode"] != 0o644 or not 0 < len(raw) <= 65536 or b"\0" in raw:
            raise ValueError("C5 provider actual NSS input is unsupported")
        raw.decode("ascii", "strict")
    config = objects[observed["files"]["/etc/nsswitch.conf"]["sha256"]].decode("ascii")
    rows = [line.split("#", 1)[0].strip() for line in config.splitlines()]
    rows = [line for line in rows if line.partition(":")[0].strip() == "passwd"]
    if len(rows) != 1 or rows[0].partition(":")[2].split() != ["files"]:
        raise ValueError("C5 provider actual passwd NSS is not files-only")
    matches = []
    for line in objects[observed["files"]["/etc/passwd"]["sha256"]].decode("ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split(":")
        if len(fields) != 7 or not fields[2].isdigit() or not fields[3].isdigit():
            raise ValueError("C5 provider passwd syntax is unsupported")
        if int(fields[2]) == 0:
            matches.append(fields)
    if len(matches) != 1 or not matches[0][5].startswith("/"):
        raise ValueError("C5 provider actual UID0 passwd home is unqualified")
    if set(observed["nscd"]) != set(B._NSCD) or any(row["kind"] != "MISSING" for row in observed["nscd"].values()):
        raise ValueError("C5 provider NSCD selector is not closed")


def _startup(objects):
    files = {}
    for name, pin in SPEC["startup_pins"].items():
        row = B.capture_selector(name, objects)
        if row["kind"] != "FILE" or any(row[key] != pin[key] for key in ("bytes", "sha256", "mode", "resolved", "link")):
            raise ValueError("C5 provider startup/native pin changed: " + name)
        files[name] = row
    for name in ("/etc/passwd", "/etc/nsswitch.conf"):
        files[name] = B.capture_selector(name, objects, limit=65536)
    aliases = {name: B.capture_selector(name, objects) for name in _ALIASES}
    for name in ("python", "python3", "python3.12"):
        path = str(VENV / "bin" / name)
        row = aliases[path]
        if PROFILE == HOSTED_PROFILE and name != "python3.12":
            copied = aliases[str(VENV / "bin/python3.12")]
            row = _capture_hosted_file_alias(VENV, "bin/" + name, "python3.12", copied, objects)
            aliases[path] = row
            continue
        pin = SPEC["venv_files"]["bin/" + name]
        if row["kind"] != "FILE" or row["resolved"] != path or row["link"] is not None or any(row[k] != pin[k] for k in ("bytes", "sha256", "mode")):
            raise ValueError("C5 genuine copied interpreter differs")
    system_pin = B.SPEC["runtime_pins"][B.SPEC["python_target"]]
    for name in B._PYTHON_ALIASES:
        row = aliases[name]
        if row["kind"] != "MISSING" and (row["kind"] != "FILE" or row["resolved"] != B.SPEC["python_target"] or row["sha256"] != system_pin["sha256"] or row["mode"] != 0o755):
            raise ValueError("C5 provider fallback interpreter selector changed")
    selected_absent = _ABSENT + (tuple(B.SPEC["runtime_absences"]) if PROFILE == HOSTED_PROFILE else ())
    absent = {name: B.capture_selector(name, objects) for name in selected_absent}
    if any(row["kind"] != "MISSING" for row in absent.values()):
        raise ValueError("C5 provider added bootstrap/loader selector requires separate closure")
    namespaces = {name: _namespace(name, objects) for name in _SEARCH}
    for root, namespace in namespaces.items():
        for name in namespace["names"]:
            if name == "apport_python_hook" or name.startswith("apport_python_hook."):
                raise ValueError("C5 provider apport startup is not closed")
            if any(name == stem or name.startswith(stem + ".") for stem in ("sitecustomize", "usercustomize")):
                if root + "/" + name != B._SITE or files.get(B._SITE, {}).get("kind") != "FILE":
                    raise ValueError("C5 provider added customizer is not closed")
        if namespace["pth"]:
            raise ValueError("C5 fixed genuine venv has no admitted .pth input")
    if sorted(namespaces[SITE]["names"]) != SPEC["venv_directories"]["lib/python3.12/site-packages"]:
        raise ValueError("C5 provider site namespace differs")
    identity = dict(uid=os.getuid(), euid=os.geteuid(), gid=os.getgid(), egid=os.getegid())
    if identity != dict(uid=0, euid=0, gid=0, egid=0):
        raise ValueError("C5 provider selected NSS profile requires actual observer UID/GID zero")
    result = dict(environment=dict(_ENVIRONMENT), identity=identity, files=files, aliases=aliases,
        absent=absent, namespaces=namespaces, nscd={name: B.capture_selector(name, objects) for name in B._NSCD},
        selected_command="python", selected_path=str(VENV / "bin/python"), selected_target=str(VENV / "bin/python"),
        site_config="ACTUAL_PYVENV_CFG_SYSTEM_SITE_FALSE_NORMAL_SITE_NO_WRAPPER",
        normal_startup_executed=False, child_identity_qualified=False)
    if PROFILE == HOSTED_PROFILE:
        result["selected_target"] = str(VENV / "bin/python3.12")
    _validate_nss(result, objects)
    return result


def _provider_inputs(objects):
    provider = _capture_tree(VENV, objects)
    _validate_record(provider, objects)
    native = {}
    for name, pin in SPEC["native_pins"].items():
        row = B.capture_selector(name, objects, limit=P.RUNTIME_BOUNDS["file_bytes"])
        if row["kind"] != "FILE" or any(row[k] != pin[k] for k in ("bytes", "sha256", "mode", "resolved", "link")):
            raise ValueError("C5 additional provider native input differs: " + name)
        native[name] = row
    _require_tree_current(VENV, provider)
    return dict(installation=provider, native=native, distribution="zopfli", version="0.2.3.post1",
        wheel_sha256=SPEC["wheel_sha256"], status="GENUINE_PROVIDER_INPUTS_CAPTURED",
        provider_imports=0, provider_execution=False, native_load_qualified=False)


def _runtime_inputs(objects):
    """Capture actual file data; never use the finite owner's Python wrapper."""
    names = {"/usr/bin/" + name for name in P.TOOLS}
    names.update("/lib/x86_64-linux-gnu/" + name for name in P.LIBRARIES)
    names.update(("/lib64/ld-linux-x86-64.so.2", "/bin/bash", "/bin/sh"))
    pending, directories = [(Path("/usr/lib/python3.12"), 0)], {}
    while pending:
        path, depth = pending.pop()
        if depth > P.RUNTIME_BOUNDS["depth"]:
            raise ValueError("C5 provider runtime depth bound exceeded")
        fd = P.open_directory(path)
        try:
            before = P.identity(os.fstat(fd))
            rows = {}
            with os.scandir(fd) as entries:
                for entry in entries:
                    P.safe_name(entry.name)
                    info = os.stat(entry.name, dir_fd=fd, follow_symlinks=False)
                    rows[entry.name] = P.identity(info)
                    if entry.name in {"site-packages", "dist-packages", "sitecustomize.py"}:
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        pending.append((path / entry.name, depth + 1))
                    elif stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
                        names.add(str(path / entry.name))
                    else:
                        raise ValueError("C5 provider runtime contains unsupported member")
                    if len(names) + len(directories) + len(pending) > P.RUNTIME_BOUNDS["entries"]:
                        raise ValueError("C5 provider runtime population bound exceeded")
            B.require_same(before, P.identity(os.fstat(fd)), "provider runtime directory")
            directories[str(path)] = dict(identity=before, ancestors=B._ancestors(path), names=rows)
        finally:
            os.close(fd)
    files = {}
    for name in sorted(names):
        row = B.capture_selector(name, objects, limit=P.RUNTIME_BOUNDS["file_bytes"])
        if row["kind"] != "FILE":
            raise ValueError("C5 required provider base runtime file is absent")
        files[name] = row
        runtime_budget_v1(files, P.RUNTIME_BOUNDS)
    provider, startup = _provider_inputs(objects), _startup(objects)
    files.update({str(VENV / name): row for name, row in provider["installation"]["files"].items()})
    files.update(provider["native"])
    files.update({name: row for name, row in startup["aliases"].items() if row["kind"] == "FILE"})
    files.update(startup["files"])
    for root, namespace in startup["namespaces"].items():
        files.update({root + "/" + name: row for name, row in namespace["pth"].items()})
    if len(files) + len(directories) + len(provider["installation"]["directories"]) > P.RUNTIME_BOUNDS["entries"]:
        raise ValueError("C5 complete provider runtime population bound exceeded")
    totals = runtime_budget_v1(files, P.RUNTIME_BOUNDS)
    return dict(files=files, directories=directories, provider=provider, startup=startup, totals=totals,
        execution_image="NOT_CONSTRUCTED", bytecode="ACTUAL_STDLIB_AND_PROVIDER_CACHE_BYTES_INCLUDED")


class C5ProviderInputs:
    """Data-only observer: no run, receipt, provider import, or native launch."""
    def __init__(self, source_root):
        self.source = Path(source_root)
        B._ancestors(self.source)
        _CHECK()

    def acquire(self):
        _CHECK()
        objects = {}
        source = B.complete_source(self.source, objects)
        contract = B._producer_contract(source["state"])
        blockers = ["PROVIDER_NATIVE_EXECUTION_CUSTODY_UNQUALIFIED", "LIVE_PRODUCER_CUSTODY_UNIMPLEMENTED",
            "BEFORE_CONSUMER_JOIN_UNIMPLEMENTED", "GIT_CLONE_EXECUTION_RUNTIME_UNQUALIFIED",
            "ACTUAL_C5_RESOURCE_PROFILE_UNQUALIFIED", "ACTUAL_CHILD_IDENTITY_UNQUALIFIED"]
        if ".git" in source["state"]["directories"]:
            P.validate_git_namespace(source["state"], objects)
            git = "COMPLETE_PRESENT_GIT_BYTES_CAPTURED_NO_GIT_COMMAND"
        else:
            blockers.append("STANDALONE_GIT_INPUT_MISSING")
            git = "MISSING_NO_SYNTHETIC_GIT_OBJECTS"
        runtime = _runtime_inputs(objects)
        B.require_same(source, B.complete_source(self.source, {}), "complete provider source")
        B.require_same(runtime, _runtime_inputs({}), "complete provider/runtime/startup")
        _CHECK()
        record = dict(schema="implementaudit.c5-provider-observation.v1", profile=PROFILE,
            source_root=str(self.source), source=source, runtime=runtime, git=git, producer_contract=contract,
            actual_source_files=len(source["state"]["files"]), actual_source_bytes=sum(row["bytes"] for row in source["state"]["files"].values()),
            historical_resource_observation=B.SPEC["historical_resource_observation"],
            input_population="COMPLETE_SELECTED_PROVIDER_INPUTS_WITH_OPEN_EXECUTION_GATES", runtime_complete=False,
            blockers=blockers, dispatch_count=0, provider_imports=0, original_results=0,
            canonical_acceptance="UNQUALIFIED", live_producer_custody=False, before_consumer_join=False, authority="NONE")
        record["observation_sha256"] = B.digest(P.encode(record))
        return dict(record=record, objects=types.MappingProxyType(objects))
