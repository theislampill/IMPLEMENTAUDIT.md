#!/usr/bin/env python3
"""Repository-only acquired image for one original composed verifier prefix.

Loaded only by the qualifier's explicit prefix route. The compiler remains the
sole graph/source-slice authority. This module owns a finite execution image,
not a second graph, a persistent cache, or successor shell/effect admission.
"""
import configparser
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
try:
    import fcntl
    import resource
except ImportError:
    fcntl = resource = None

PROFILE = "COMPOSED_SOURCE_PREFIX_23_V1"
REGISTRY_SHA256 = "77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698"
RENDERER_SHA256 = "0e8649272536497816b05993f488e741cadb911906cdfc16719d9dba0ba7b2b1"
LAST = "COMMAND:scripts/check-terminology-integration.sh:0"
NEXT = "COMMAND:scripts/check-added-lines-clean.sh:0"
RESERVED = ".IMPLEMENTAUDIT"
ENVIRONMENT = dict(PATH="/usr/bin:/bin", LANG="C", LC_ALL="C", TZ="UTC",
    PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1", PYTHONSAFEPATH="1", PYTHONNOUSERSITE="1", GIT_CONFIG_NOSYSTEM="1",
    GIT_CONFIG_GLOBAL="/dev/null", GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1",
    GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0", GIT_EXEC_PATH="/nonexistent")
SOURCE_BOUNDS = dict(file_bytes=128 * 1024**2, total_bytes=256 * 1024**2,
                     entries=4096, depth=40)
RUNTIME_BOUNDS = dict(file_bytes=32 * 1024**2, total_bytes=128 * 1024**2,
                      entries=4096, depth=40, mounted_bytes=128 * 1024**2,
                      unique_bytes=128 * 1024**2)
ARCHIVE_BOUND = 272 * 1024**2
MANIFEST_BOUND = 4 * 1024**2
NORMALIZATION = dict(uid=0, gid=0, uname="", gname="", mtime=0,
                     links="ORDINARY_PRIVATE_FILES_NLINK_ONE", source_modes="PRESERVED")
TOOLS = ("bash", "dirname", "git", "grep", "cat", "rm", "mktemp", "head", "sed",
         "sort", "uniq", "cut", "tr", "wc", "find", "xargs", "printf", "test", "sh",
         "mkdir", "rmdir", "cp", "mv", "chmod", "readlink", "realpath", "cmp", "tail",
         "basename", "env", "true", "false", "date", "stat", "awk", "touch", "python3.12")
# The inspected system Python 3.12 / Unix tools closure; absence refuses. No
# ldd of candidate executables, host loader cache, Git helper, browser or network.
LIBRARIES = ("libacl.so.1", "libattr.so.1", "libbrotlicommon.so.1", "libbrotlidec.so.1",
    "libbz2.so.1.0", "libc.so.6", "libcom_err.so.2", "libcrypt.so.1", "libcrypto.so.3",
    "libcurl-gnutls.so.4", "libdb-5.3.so", "libexpat.so.1", "libffi.so.8", "libgmp.so.10",
    "libgnutls.so.30", "libgssapi_krb5.so.2", "libhogweed.so.6", "libidn2.so.0",
    "libk5crypto.so.3", "libkeyutils.so.1", "libkrb5.so.3", "libkrb5support.so.0",
    "liblber.so.2", "libldap.so.2", "liblzma.so.5", "libm.so.6", "libncursesw.so.6",
    "libnettle.so.8", "libnghttp2.so.14", "libp11-kit.so.0", "libpanelw.so.6",
    "libpcre2-8.so.0", "libpsl.so.5", "libreadline.so.8", "libresolv.so.2", "librtmp.so.1",
    "libsasl2.so.2", "libselinux.so.1", "libsqlite3.so.0", "libssh.so.4", "libssl.so.3",
    "libtasn1.so.6", "libtinfo.so.6", "libunistring.so.5", "libz.so.1", "libzstd.so.1")
# Original entrypoints plus their three transitive repository executables.
# These are execution-admission pins, not alternate checker outcomes.
PROGRAM_PINS = {
    'fixtures/semantic-preservation/evaluate.py': 'e0dbc9006ff8be8cb312e3f0cd9eeba6507a73cba2a4011112f860b2381cb895',
    'scripts/check-agents-bootstrap-budget.sh': 'be6cb923382263f35b87a0b65f42fc57fd438fd091dc4fa2baf3533d0eb4e078',
    'scripts/check-audit-object-routing-contract.sh': 'def461d7fea840fcbed399b3c278fcae3307c5013ea14e47539e6744dde39a50',
    'scripts/check-audit-retention.sh': '386d7475f7111a5e5349672b01e9c68f5fa0f15cfcf100930d8dae187370937e',
    'scripts/check-capability-parity-contract.sh': '5dbca0e81a79e65b95c4d9a532bb893b5405fedb34ddbc360b3acc70f291d871',
    'scripts/check-dogfood-bootstrap-contract.sh': '347881570f449370cb1d18e831c978b0e55db702b8120248cdb683214af1074d',
    'scripts/check-installed-payload-self-contained.sh': '228ab1ed29c50d7916cca4e82b0696d42314c6a4efb3b2a7bdd43b5a3bfd70b8',
    'scripts/check-lean-discipline.sh': 'eff43d8768b019c1dfcd369df84e864de5decea62cb664a3854f62dabc9b003f',
    'scripts/check-marker-order.sh': '9764979aa3e1324e217828684e45ef67f40f14427537502a62ce3d66b6872b31',
    'scripts/check-native-integration.sh': '63dc104b9d242de2118327d99cdf01d7e2bed95c17f2e8c1fb52a89831740e36',
    'scripts/check-package-contract.sh': '3d9a6f36c609ae2731e790f82658fdbab6bbc15f1e8cd20b6fdaced1051d9dfc',
    'scripts/check-package-shape-claims.sh': '8cf31dfa733650ad2359121036d640bb35486d79736dbea965315def6c8a3136',
    'scripts/check-plan-quality-contract.sh': 'f89b9ba3e6f7d9a003238b1efc398e3b78aba9a84a9e4fc19cab5dc81c70f8df',
    'scripts/check-planner-stages.sh': '78d3735a5af7b83f76bafd48feac2af23868e6a8c668f7c579367f627c0a5825',
    'scripts/check-public-claim-boundaries.sh': '7187805b0d8be133244dda1057339b828de41a2799fa4bb3f8a045e75438c9ee',
    'scripts/check-readme-toc.sh': '9b8cc45e887b29ffb904b17643ef0e0564db8fb7eb475685e294dbcc2dea8638',
    'scripts/check-routing.sh': '6bddc813e29f13e63ac0f88474fd32418c38bef4110360a2ae6a451a69e36974',
    'scripts/check-safeguard-restoration.sh': 'b6237e29e9f9e73b910ef5b23b75df2421ebd1d0688a5ab90f5072ca9b67a17f',
    'scripts/check-sidecar-boundaries.sh': '3b3e02ceb6b8f28359654960fb1d0872466aee3ad94c3da9381a3ede3aa36ad1',
    'scripts/check-skill-bootstrap-budget.sh': '966af6e57de7f056de40944ad64f6ce1f1c86d038cdbdf2b65d7f61d52d28c67',
    'scripts/check-skill-layout-contract.sh': 'b73e014aa4727d064108515fd959f1d9efb799b2afa1d02f0e7677bd51d02988',
    'scripts/check-terminology-integration.sh': 'dc5269818c3719a7a4c1fcb9ec8bc8076d4edbf37d07a5d3ce60cb73e0e7bc93',
    'scripts/generate-readme-diagrams.sh': '607bc8c367989af45dedefcf3a3720af89d88c72d2cf58c0e779b27fade949f5',
    'scripts/package-contract.py': 'f3fa90f6c1e7b75527eddd988a6977f27db669bec337f65ff9c2b1ceae50621f',
    'scripts/verify-readme-diagrams-rendered.sh': RENDERER_SHA256,
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def identity(info):
    """Exact stat vector: decimal uint64 device/inode, then integer metadata.

    Filesystem identifiers can exceed signed64 JSON integers. Their canonical
    decimal strings preserve the full unsigned domain without float conversion.
    Mode, link count, byte size and nanosecond timestamps remain integers.
    """
    identifiers = (info.st_dev, info.st_ino)
    if any(type(value) is not int or not 0 <= value < 2**64 for value in identifiers):
        raise ValueError("filesystem device/inode must be unsigned 64-bit integers")
    return [str(info.st_dev), str(info.st_ino), info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns]


def safe_name(name):
    if not name or name.startswith("/") or any(p in {"", ".", ".."} for p in name.split("/")):
        raise ValueError("unsupported image path")
    name.encode("utf-8", "strict")
    if any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ValueError("unsupported image path character")
    return name


def open_directory(path):
    """Open every absolute ancestor without following any symlink."""
    path = Path(os.path.abspath(path))
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in path.parts[1:]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_regular(path, limit=ARCHIVE_BOUND, *, single_link=True):
    path = Path(path)
    parent = open_directory(path.parent)
    fd = None
    try:
        before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or (single_link and before.st_nlink != 1):
            raise ValueError("input must be an ordinary single-link file")
        if before.st_size > limit:
            raise ValueError("input file byte bound exceeded")
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        if identity(os.fstat(fd)) != identity(before) or os.listxattr(fd):
            raise ValueError("input changed or extended metadata is unsupported")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(limit + 1)
        if len(data) > limit or identity(os.fstat(fd)) != identity(before) or identity(os.stat(path.name, dir_fd=parent, follow_symlinks=False)) != identity(before):
            raise ValueError("input changed during bounded acquisition")
        return dict(kind="FILE", mode=stat.S_IMODE(before.st_mode), size=len(data), sha256=digest(data), identity=identity(before)), data
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent)


def snapshot_tree(root, objects, bounds, *, excluded=()):
    """Bounded closed namespace; source contents never come from Git HEAD."""
    root = Path(os.path.abspath(root))
    state, stamps = dict(files={}, directories={}), {}
    count = total = 0
    def walk(fd, relative, depth):
        nonlocal count, total
        info = os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode) or os.listxattr(fd) or info.st_mode & 0o6000:
            raise ValueError("unsupported directory metadata")
        count += 1
        if count > bounds["entries"] or depth > bounds["depth"]:
            raise ValueError("namespace entry/depth bound exceeded")
        state["directories"][relative] = stat.S_IMODE(info.st_mode)
        stamps[relative] = identity(info)
        names = []
        with os.scandir(fd) as entries:
            for entry in entries:
                if entry.name in excluded:
                    continue
                if len(names) + count >= bounds["entries"]:
                    raise ValueError("namespace entry bound exceeded")
                names.append(entry.name)
        for component in sorted(names):
            name = component if relative == "." else relative + "/" + component
            safe_name(name)
            before = os.stat(component, dir_fd=fd, follow_symlinks=False)
            if depth + 1 > bounds["depth"]:
                raise ValueError("namespace depth bound exceeded")
            if stat.S_ISDIR(before.st_mode):
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    if identity(os.fstat(child)) != identity(before):
                        raise ValueError("directory changed during acquisition")
                    walk(child, name, depth + 1)
                finally:
                    os.close(child)
            elif stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and not before.st_mode & 0o6000:
                count += 1
                total += before.st_size
                if count > bounds["entries"] or before.st_size > bounds["file_bytes"] or total > bounds["total_bytes"]:
                    raise ValueError("source input byte/entry bound exceeded")
                child = os.open(component, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
                try:
                    if identity(os.fstat(child)) != identity(before) or os.listxattr(child):
                        raise ValueError("file changed or extended metadata is unsupported")
                    with os.fdopen(child, "rb", closefd=False) as stream:
                        data = stream.read(bounds["file_bytes"] + 1)
                    if len(data) != before.st_size or identity(os.fstat(child)) != identity(before):
                        raise ValueError("file changed during bounded acquisition")
                    key = digest(data)
                    objects.setdefault(key, data)
                    state["files"][name] = dict(mode=stat.S_IMODE(before.st_mode), bytes=len(data), sha256=key)
                    stamps[name] = identity(before)
                finally:
                    os.close(child)
            else:
                raise ValueError("source requires ordinary directories and single-link files")
            if identity(os.stat(component, dir_fd=fd, follow_symlinks=False)) != identity(before):
                raise ValueError("namespace member changed during acquisition")
        if identity(os.fstat(fd)) != identity(info):
            raise ValueError("directory membership changed during acquisition")
    fd = open_directory(root)
    try:
        walk(fd, ".", 0)
        check = open_directory(root)
        try:
            if identity(os.fstat(check)) != stamps["."]:
                raise ValueError("source root changed during acquisition")
        finally:
            os.close(check)
    finally:
        os.close(fd)
    return state, stamps


def select_prefix(compiler, registry, environment):
    if digest(registry) != REGISTRY_SHA256:
        raise ValueError("unsupported composed-prefix registry source")
    graph = compiler.compile_verifier_graph_v1(registry, compiler.verifier_registered_tests_v1(registry), environment)
    compiler.verifier_command_stream_v1(graph, registry)
    nodes = graph["nodes"]
    if len(nodes) != 117 or nodes[0]["id"] != "PRELUDE" or nodes[22]["id"] != LAST or nodes[23]["id"] != NEXT:
        raise ValueError("unsupported composed-prefix registry mapping")
    data = registry[:nodes[22]["byte_end"]]
    if data != b"".join(n["source"].encode() for n in nodes[:23]):
        raise ValueError("compiler prefix source slice differs")
    return graph, dict(profile=PROFILE, graph_digest=graph["digest"], nodes=[n["id"] for n in nodes[:23]],
        stop_before=NEXT, omitted_nodes=[n["id"] for n in nodes[23:]], source_sha256=digest(data),
        source_bytes=len(data), composition="ONE_ORIGINAL_SHELL_GROUP_NO_SUCCESSOR_SUBSTITUTION"), data


def source_archive(state, objects):
    if any(name == RESERVED or name.startswith(RESERVED + "/") for group in state.values() for name in group):
        raise ValueError("reserved bootstrap namespace collision")
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:", format=tarfile.GNU_FORMAT) as archive:
        for name, mode in sorted(state["directories"].items(), key=lambda row: (row[0].count("/"), row[0])):
            item = tarfile.TarInfo(name)
            item.type, item.mode = tarfile.DIRTYPE, mode
            archive.addfile(item)
        for name, observed in sorted(state["files"].items()):
            item = tarfile.TarInfo(safe_name(name))
            item.mode, item.size = observed["mode"], observed["bytes"]
            data = objects[observed["sha256"]]
            if len(data) != item.size or digest(data) != observed["sha256"]:
                raise ValueError("archive input object differs")
            archive.addfile(item, io.BytesIO(data))
    data = buffer.getvalue()
    if len(data) > ARCHIVE_BOUND:
        raise ValueError("source archive byte bound exceeded")
    return data


def materialize_archive(data, expected, target):
    """Validate the entire generated archive before any private source write."""
    if len(data) > ARCHIVE_BOUND or set(expected) != {"files", "directories"}:
        raise ValueError("invalid or oversized source archive")
    target = Path(target)
    if list(target.iterdir()):
        raise ValueError("materialization destination is not empty")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
        seen = set()
        for item in archive:
            name = item.name
            if name != ".":
                safe_name(name)
            if name in seen or len(seen) >= SOURCE_BOUNDS["entries"]:
                raise ValueError("duplicate or excess archive member")
            seen.add(name)
            if item.uid or item.gid or item.uname or item.gname or item.mtime or item.pax_headers or item.linkname:
                raise ValueError("archive metadata differs from normalized image")
            if item.isdir():
                if name not in expected["directories"] or item.mode != expected["directories"][name] or item.size:
                    raise ValueError("archive directory differs")
            elif item.isreg():
                record = expected["files"].get(name)
                if record is None or item.mode != record["mode"] or item.size != record["bytes"] or item.size > SOURCE_BOUNDS["file_bytes"]:
                    raise ValueError("archive file differs")
                with archive.extractfile(item) as stream:
                    hashed = hashlib.sha256()
                    for chunk in iter(lambda: stream.read(1024**2), b""):
                        hashed.update(chunk)
                if hashed.hexdigest() != record["sha256"]:
                    raise ValueError("archive file bytes differ")
            else:
                raise ValueError("archive contains unsupported member kind")
        if seen != set(expected["files"]) | set(expected["directories"]):
            raise ValueError("archive member census differs")
        # Every target starts empty, and every admitted member is an ordinary
        # directory/file with no repeated name. No extractall/link handling.
        for name in sorted(expected["directories"], key=lambda p: (p.count("/"), p)):
            if name != ".":
                (target / name).mkdir(mode=0o700)
        for name, record in sorted(expected["files"].items()):
            with archive.extractfile(name) as source, (target / name).open("xb") as dest:
                for chunk in iter(lambda: source.read(1024**2), b""):
                    dest.write(chunk)
            os.chmod(target / name, record["mode"])
            os.utime(target / name, ns=(0, 0))
        for name, mode in sorted(expected["directories"].items(), key=lambda row: (-row[0].count("/"), row[0])):
            os.chmod(target / name, mode)
            os.utime(target / name, ns=(0, 0))


def validate_git_namespace(state, objects):
    if ".git" not in state["directories"] or ".git/config" not in state["files"] or ".git/objects" not in state["directories"]:
        raise ValueError("standalone acquired Git directory is required")
    names = set(state["files"]) | set(state["directories"])
    forbidden = {".git/commondir", ".git/gitdir", ".git/shallow", ".git/config.worktree",
                 ".git/objects/info/alternates", ".git/objects/info/http-alternates", ".git/info/grafts"}
    if names & forbidden or any(n.endswith((".lock", ".promisor")) or any(n == p or n.startswith(p + "/") for p in
        (".git/worktrees", ".git/modules", ".git/refs/replace")) or ".git" in Path(n).parts[1:] for n in names):
        raise ValueError("unsupported external, partial or mutable Git storage")
    config = configparser.RawConfigParser(strict=True)
    try:
        raw = objects[state["files"][".git/config"]["sha256"]]
        if len(raw) > 65536:
            raise ValueError("Git config byte bound exceeded")
        config.read_string(raw.decode("utf-8", "strict"))
        allowed = {"core": {"repositoryformatversion", "filemode", "bare", "logallrefupdates"},
                   'remote "origin"': {"url", "fetch"}}
        if config.defaults() or any(s not in allowed or set(config[s]) - allowed[s] for s in config.sections()):
            raise ValueError("unsupported Git config entry")
        if config.get("core", "repositoryformatversion") != "0" or config.get("core", "bare") != "false":
            raise ValueError("unsupported Git repository format")
        if any(len(value) > 4096 or "\n" in value for section in config.sections() for value in config[section].values()):
            raise ValueError("unsupported Git config value")
        for key in ("filemode", "logallrefupdates"):
            if config.has_option("core", key) and config.get("core", key) not in {"true", "false"}:
                raise ValueError("unsupported Git config boolean")
    except (configparser.Error, UnicodeError) as exc:
        raise ValueError("unsupported Git config syntax") from exc


def runtime_budget(entries, bounds):
    unique = {}
    for entry in entries.values():
        if entry["sha256"] in unique and unique[entry["sha256"]] != entry["bytes"]:
            raise ValueError("inconsistent runtime object")
        unique[entry["sha256"]] = entry["bytes"]
    totals = dict(entries=len(entries), mounted_bytes=sum(e["bytes"] for e in entries.values()), unique_bytes=sum(unique.values()))
    if any(totals[k] > bounds[k] for k in totals):
        raise ValueError("runtime image bound exceeded")
    return totals


def validate_programs(state):
    if any(state["files"].get(name, {}).get("sha256") != pin for name, pin in PROGRAM_PINS.items()):
        raise ValueError("unsupported composed-prefix executable source")


def acquire_runtime(objects):
    """A bounded system runtime, with every allowed alias resolved into bytes."""
    names = {"/usr/bin/" + n for n in TOOLS}
    names.update("/lib/x86_64-linux-gnu/" + n for n in LIBRARIES)
    names.update(("/lib64/ld-linux-x86-64.so.2", "/bin/bash", "/bin/sh"))
    stdlib = Path("/usr/lib/python3.12")
    pending = [(stdlib, 0)]
    directory_stamps = {}
    visited = 0
    while pending:
        directory, depth = pending.pop()
        if depth > RUNTIME_BOUNDS["depth"]:
            raise ValueError("runtime depth bound exceeded")
        fd = open_directory(directory)
        try:
            directory_stamps[str(directory)] = identity(os.fstat(fd))
            with os.scandir(fd) as entries:
                for entry in entries:
                    if entry.name in {"__pycache__", "sitecustomize.py", "site-packages", "dist-packages"}:
                        continue
                    visited += 1
                    if visited + len(TOOLS) + len(LIBRARIES) > RUNTIME_BOUNDS["entries"]:
                        raise ValueError("runtime entry bound exceeded")
                    path = directory / entry.name
                    safe_name(str(path).lstrip("/"))
                    info = os.stat(entry.name, dir_fd=fd, follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        pending.append((path, depth + 1))
                    elif stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
                        names.add(str(path))
                    else:
                        raise ValueError("unsupported runtime member kind")
        finally:
            os.close(fd)
    files, observations = {}, {}
    for name in sorted(names):
        original = Path(name)
        resolved = original.resolve(strict=True)
        if not (str(resolved).startswith("/usr/bin/") or str(resolved).startswith("/usr/lib/")):
            raise ValueError("runtime alias escapes the finite system roots")
        meta, data = read_regular(resolved, RUNTIME_BOUNDS["file_bytes"], single_link=False)
        if original.resolve(strict=True) != resolved:
            raise ValueError("runtime alias changed during acquisition")
        key = digest(data)
        files[name] = dict(mode=0o555 if meta["mode"] & 0o111 else 0o444, bytes=len(data), sha256=key)
        runtime_budget(files, RUNTIME_BOUNDS)
        objects.setdefault(key, data)
        observations[name] = dict(resolved=str(resolved), mode=meta["mode"], bytes=len(data), sha256=key, identity=meta["identity"])
    for name, observed in observations.items():
        if str(Path(name).resolve(strict=True)) != observed["resolved"] or identity(Path(observed["resolved"]).stat()) != observed["identity"]:
            raise ValueError("runtime changed during complete acquisition")
    for name, observed in directory_stamps.items():
        fd = open_directory(name)
        try:
            if identity(os.fstat(fd)) != observed:
                raise ValueError("runtime namespace changed during acquisition")
        finally:
            os.close(fd)
    wrapper = b'#!/usr/bin/bash\nexec /usr/bin/python3.12 -P -S -B "$@"\n'
    key = digest(wrapper)
    objects.setdefault(key, wrapper)
    for name in ("/usr/bin/python", "/usr/bin/python3"):
        files[name] = dict(mode=0o555, bytes=len(wrapper), sha256=key)
    totals = runtime_budget(files, RUNTIME_BOUNDS)
    return dict(files=files, observations=observations, directory_observations=directory_stamps, totals=totals,
        directories=sorted({str(p) for n in files for p in Path(n).parents if str(p) != "/"}),
        startup="PYTHON_3_12_WRAPPERS_P_S_B_ALL_CHILDREN_SAFE_PATH_NO_USER_SITE_NO_BYTECODE_FIXED_HASHSEED",
        git="CAPTURED_BUILTINS_ONLY_NO_EXEC_PATH_NO_GLOBAL_CONFIG_NO_NETWORK",
        absent="HOST_ROOT_PROC_ETC_LOADER_CACHE_USER_SITE_BROWSER_AND_OTHER_RUNTIME")


def git_identity(source, state, objects, scratch=None):
    """Read only admitted local Git storage; mirror the pinned renderer branch."""
    validate_git_namespace(state, objects)
    renderer = state["files"].get("scripts/verify-readme-diagrams-rendered.sh", {})
    if renderer.get("sha256") != RENDERER_SHA256:
        raise ValueError("unsupported renderer source for no-browser prefix")
    records = []
    def git(*args, allowed=(0,)):
        command = ["/usr/bin/git", "-c", "safe.directory=" + str(source), "-c", "core.hooksPath=/dev/null", *args]
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
            resource.setrlimit(resource.RLIMIT_FSIZE, (MANIFEST_BOUND,) * 2)
        with tempfile.TemporaryFile(dir=scratch) as stdout, tempfile.TemporaryFile(dir=scratch) as stderr:
            proc = subprocess.run(command, cwd=source, env=ENVIRONMENT, stdout=stdout,
                                  stderr=stderr, timeout=30, preexec_fn=limits)
            stdout.seek(0)
            stderr.seek(0)
            proc.stdout, proc.stderr = stdout.read(MANIFEST_BOUND + 1), stderr.read(MANIFEST_BOUND + 1)
        if len(proc.stdout) + len(proc.stderr) > MANIFEST_BOUND or proc.returncode not in allowed:
            raise ValueError("bounded local Git admission failed: " + args[0])
        records.append(dict(argv=list(args), exit=proc.returncode, stdout_sha256=digest(proc.stdout), stderr_sha256=digest(proc.stderr)))
        return proc
    head = git("rev-parse", "--verify", "HEAD").stdout.decode().strip()
    tree = git("rev-parse", "HEAD^{tree}").stdout.decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head) or not re.fullmatch(r"[0-9a-f]{40}", tree):
        raise ValueError("unsupported Git object format")
    if Path(git("rev-parse", "--show-toplevel").stdout.decode().strip()) != source:
        raise ValueError("Git worktree differs from acquired source root")
    if Path(git("rev-parse", "--absolute-git-dir").stdout.decode().strip()) != source / ".git":
        raise ValueError("Git storage differs from acquired standalone directory")
    stages = git("ls-files", "--stage", "-z").stdout.split(b"\0")
    if any(line.startswith(b"160000 ") for line in stages):
        raise ValueError("Git submodule storage is unsupported")
    # Connectivity is local only. Complete object files, refs, index, config,
    # attributes and ignored/untracked source membership are already acquired.
    git("fsck", "--connectivity-only", "--no-reflogs")
    paths = ["docs/diagrams/tooling-architecture.mmd", "docs/diagrams/invocation-modes.mmd",
             "docs/diagrams/execution-spine.mmd", "scripts/generate-readme-diagrams.sh",
             "scripts/verify-readme-diagrams-rendered.sh"]
    if git("diff", "--quiet", "--", *paths, allowed=(0, 1)).returncode:
        raise ValueError("rendered diagram branch requires an unacquired browser contract")
    comparison = None
    if git("rev-parse", "--verify", "origin/main", allowed=(0, 128)).returncode == 0:
        comparison = git("merge-base", "HEAD", "origin/main").stdout.decode().strip()
    elif git("rev-parse", "--verify", "HEAD^", allowed=(0, 128)).returncode == 0:
        comparison = "HEAD^"
    if comparison is not None and git("diff", "--quiet", comparison, "HEAD", "--", *paths, allowed=(0, 1)).returncode:
        raise ValueError("rendered diagram branch requires an unacquired browser contract")
    return dict(head=head, tree=tree, renderer_comparison=comparison,
                renderer_branch="ORIGINAL_NOT_APPLICABLE_BRANCH", observations=records)


def bind_session(base, compiler, engine_root, loaded_helper):
    """Attach the finite image to the existing qualifier's live custody owner."""
    class ComposedPrefixSession(base):
        SCOPE = PROFILE
        ENVIRONMENT = ENVIRONMENT
        LIMITS = dict(cpu_seconds=90, address_bytes=1024**3, file_bytes=16 * 1024**2,
            staging_file_bytes=ARCHIVE_BOUND, descriptors=4096, work_bytes=512 * 1024**2,
            scratch_bytes=32 * 1024**2, wall_seconds=120, stream_bytes=16 * 1024**2,
            retained_object_bytes=1024**3, evidence_bytes=2 * 1024**3)

        def __init__(self, source_root, output, *, max_age=3600):
            # Validate the caller's actual path before the inherited convenience
            # resolution. No symlink-selected candidate or evidence directory.
            if fcntl is None or not hasattr(fcntl, "F_GET_SEALS"):
                raise compiler.WorkGraphError("composed prefix requires observable Linux memfd seals")
            fd = open_directory(source_root)
            os.close(fd)
            parent = Path(os.path.abspath(output)).parent
            fd = open_directory(parent)
            os.close(fd)
            self._helper = loaded_helper
            self._object_bytes = 0
            self._object_keys = set()
            self._attempted = False
            self._consumption_lock = threading.Lock()
            super().__init__(source_root, output, max_age=max_age)
            self._output_identity = identity(self.output.stat())[:2]
            self._session_bytes = read_regular(self.output / "session.json")[1]
            (self.output / "session.json").chmod(0o400)

        @staticmethod
        def _regular(path, missing=False):
            try:
                return read_regular(path)
            except FileNotFoundError:
                if missing:
                    return dict(kind="MISSING"), None
                raise

        def _engine_binding(self):
            result = super()._engine_binding()
            name = "scripts/qualify-work-graph-prefix.py"
            current = read_regular(engine_root / name)[1]
            if current != self._helper:
                raise compiler.WorkGraphError("loaded prefix helper differs from current source")
            result[name] = digest(current)
            return result

        def _object(self, data):
            key = digest(data)
            directory = self.output / "objects"
            directory.mkdir(mode=0o700, exist_ok=True)
            if stat.S_IMODE(directory.stat().st_mode) != 0o700 or directory.is_symlink():
                raise compiler.WorkGraphError("object custody directory changed")
            path = directory / key
            if path.exists():
                metadata, current = read_regular(path)
                if current != data or metadata["mode"] != 0o400:
                    raise compiler.WorkGraphError("retained object changed")
            else:
                if key in self._object_keys:
                    raise compiler.WorkGraphError("previously acquired retained object is missing")
                if self._object_bytes + len(data) > self.LIMITS["retained_object_bytes"]:
                    raise compiler.WorkGraphError("retained object byte bound exceeded")
                self._write(path, data)
                path.chmod(0o400)
                self._object_bytes += len(data)
                self._object_keys.add(key)
            return key

        def _custody(self):
            if os.getpid() != self.producer_pid:
                raise compiler.WorkGraphError("producer process changed; receipt import is unsupported")
            if self.environment != self.ENVIRONMENT or self._engine_binding() != self._engine:
                raise compiler.WorkGraphError("producer source or environment changed")
            info = self.output.lstat()
            if not stat.S_ISDIR(info.st_mode) or identity(info)[:2] != self._output_identity or stat.S_IMODE(info.st_mode) != 0o700:
                raise compiler.WorkGraphError("private evidence custody changed")
            metadata, data = read_regular(self.output / "session.json")
            if metadata["mode"] != 0o400 or data != self._session_bytes:
                raise compiler.WorkGraphError("session record changed")

        def _observer(self):
            null = Path("/dev/null").lstat()
            if not stat.S_ISCHR(null.st_mode) or (os.major(null.st_rdev), os.minor(null.st_rdev)) != (1, 3):
                raise compiler.WorkGraphError("unsupported null device")
            binaries = {}
            for name in ("/usr/bin/bwrap", "/usr/bin/git", sys.executable):
                path = Path(name).resolve(strict=True)
                metadata, data = read_regular(path, single_link=False)
                if Path(name).resolve(strict=True) != path:
                    raise compiler.WorkGraphError("observer executable alias changed")
                binaries[name] = dict(resolved=str(path), sha256=digest(data), identity=metadata["identity"])
            return dict(binaries=binaries, kernel=list(platform.uname()),
                process=[self.producer_pid, os.geteuid(), os.getegid()],
                python=dict(version=sys.version, flags=repr(sys.flags), executable=sys.executable),
                observer_environment_sha256=digest(encode(dict(os.environ))),
                inherited_limits={n: list(resource.getrlimit(getattr(resource, n))) for n in dir(resource) if n.startswith("RLIMIT_")},
                null_device=[null.st_rdev, stat.S_IMODE(null.st_mode)])

        def _acquire(self):
            self._custody()
            objects = {}
            before_observer = self._observer()
            source, stamps = snapshot_tree(self.source, objects, SOURCE_BOUNDS)
            validate_programs(source)
            registry = objects[source["files"]["scripts/verify-package.sh"]["sha256"]]
            graph, scope, prefix = select_prefix(compiler, registry, self.environment)
            git = git_identity(self.source, source, objects, self.output)
            runtime = acquire_runtime(objects)
            archive = source_archive(source, objects)
            current, final_stamps = snapshot_tree(self.source, {}, SOURCE_BOUNDS)
            if source != current or stamps != final_stamps or before_observer != self._observer():
                raise compiler.WorkGraphError("source or observer changed during acquisition")
            self._custody()
            for data in objects.values():
                self._object(data)
            archive_key = self._object(archive)
            source_key = self._object(encode(source))
            runtime_key = self._object(encode(runtime))
            graph_key = self._object(self._encode(graph))
            scope_key = self._object(encode(scope))
            prefix_key = self._object(prefix)
            seccomp_key = self._object(self.SECCOMP)
            helper_key = self._object(self._helper)
            acquired = dict(schema="implementaudit.verifier-prefix-acquisition.v1", scope=scope,
                producer=self.producer, source_root=[str(self.source), *stamps["."][:2]], git=git,
                source=source_key, archive=archive_key, runtime=runtime_key, graph=graph_key,
                scope_object=scope_key, prefix=prefix_key, seccomp=seccomp_key, helper=helper_key,
                engine=self._engine, observer=before_observer, environment=self.environment,
                limits=self.LIMITS, source_bounds=SOURCE_BOUNDS, runtime_bounds=RUNTIME_BOUNDS,
                normalization=NORMALIZATION, stdin="EMPTY", logical_cwd="/work",
                bootstrap_overlay=dict(path="/work/.IMPLEMENTAUDIT/verify-package.sh", source=prefix_key, source_collision="REFUSE"),
                namespace="UNSHARE_ALL_NO_PROC_NO_GENERAL_DEV_NO_HOST_ROOT",
                mutable_resources=["private bounded source/Git copy", "private bounded /tmp", "/dev/null", "observer stdout/stderr"],
                effects="PRIVATE_WRITES_DISCARDED_NO_SUCCESSOR_SPLICE", authority="NONE")
            key = self._object(encode(acquired))
            required = set(objects) | {archive_key, source_key, runtime_key, graph_key, scope_key, prefix_key, seccomp_key, helper_key, key}
            return dict(acquired=acquired, key=key, source=source, stamps=stamps, graph=graph,
                        runtime=runtime, prefix=prefix, archive=archive, objects=objects,
                        required_objects=sorted(required))

        def _issued_keys(self):
            self._custody()
            keys, refused = super()._issued_keys()
            for node, retained in self._issued.items():
                try:
                    for path in [retained["directory"] / n for n in retained["retained"]] + [self.output / "objects" / n for n in retained["required_objects"]]:
                        if read_regular(path)[0]["mode"] != 0o400:
                            raise compiler.WorkGraphError("issued evidence mode changed")
                except (OSError, ValueError) as exc:
                    keys.pop(node, None)
                    refused[node] = str(exc)
            return keys, refused

        def _verify_new_result(self, retained):
            if time.monotonic() - retained["observed_at"] > self.max_age:
                raise compiler.WorkGraphError("new issued result expired before consumption")
            for name, expected in retained["retained"].items():
                metadata, data = read_regular(retained["directory"] / name)
                if data != expected or metadata["mode"] != 0o400:
                    raise compiler.WorkGraphError("new issued evidence changed before consumption")
            for key in retained["required_objects"]:
                metadata, data = read_regular(self.output / "objects" / key)
                if digest(data) != key or metadata["mode"] != 0o400:
                    raise compiler.WorkGraphError("new issued input object changed before consumption")

        def _same(self, before, after, directory, phase):
            if before["key"] != after["key"] or before["stamps"] != after["stamps"]:
                self._write(directory / (phase + "-refusal.json"), dict(before=before["key"], after=after["key"], phase=phase,
                    source_identity_changed=before["stamps"] != after["stamps"], authority="NONE"))
                raise compiler.WorkGraphError("current source/runtime/observer changed " + phase)

        def _execute_group(self, acquired, directory):
            directory.mkdir(mode=0o700)
            fds = []
            code, complete, process = None, False, None
            try:
                args = ["--unshare-all", "--unshare-user", "--die-with-parent", "--new-session", "--clearenv", "--cap-drop", "ALL"]
                for name, value in sorted(self.environment.items()):
                    args += ["--setenv", name, value]
                directories = set(acquired["runtime"]["directories"]) | {"/work", "/tmp", "/dev", "/profile"}
                for name in sorted(directories, key=lambda p: (p.count("/"), p)):
                    args += ["--perms", "0755", "--dir", name]
                files = {name: (acquired["objects"][entry["sha256"]], entry["mode"]) for name, entry in acquired["runtime"]["files"].items()}
                files.update({"/profile/source.tar": (acquired["archive"], 0o444),
                    "/profile/source.json": (encode(acquired["source"]), 0o444),
                    "/profile/prefix.sh": (acquired["prefix"], 0o444),
                    "/profile/bootstrap.py": (self._helper, 0o444)})
                for name, (data, mode) in sorted(files.items()):
                    fd = self._sealed(data)
                    fds.append(fd)
                    if fcntl.fcntl(fd, fcntl.F_GET_SEALS) != 15:
                        raise compiler.WorkGraphError("sealed input verification failed")
                    args += ["--perms", oct(mode)[2:], "--ro-bind-data", str(fd), name]
                seccomp = self._sealed(self.SECCOMP)
                fds.append(seccomp)
                args += ["--dev-bind", "/dev/null", "/dev/null", "--size", str(self.LIMITS["work_bytes"]), "--tmpfs", "/work",
                    "--size", str(self.LIMITS["scratch_bytes"]), "--tmpfs", "/tmp", "--remount-ro", "/", "--chdir", "/work", "--seccomp", str(seccomp)]
                argfd = self._sealed(b"\0".join(a.encode() for a in args) + b"\0")
                fds.append(argfd)
                if len(args) >= 8500 or max(fds) >= self.LIMITS["descriptors"]:
                    raise compiler.WorkGraphError("image argument/descriptor bound exceeded")
                command = ["/usr/bin/bwrap", "--args", str(argfd), "/usr/bin/python3.12", "-P", "-S", "-B", "/profile/bootstrap.py", "--materialize"]
                self._write(directory / "dispatch.json", dict(argv=command, input_key=acquired["key"], scope=acquired["acquired"]["scope"],
                    descriptor_count=len(fds), seals=15, descriptor_custody="SEALED_INPUTS_CLOSED_BEFORE_BOOTSTRAP",
                    descendant_lifecycle="FRESH_PID_NAMESPACE_INIT_EXIT_KILLS_MEMBERS", authority="NONE"))
                def limits():
                    resource.setrlimit(resource.RLIMIT_CPU, (self.LIMITS["cpu_seconds"],) * 2)
                    resource.setrlimit(resource.RLIMIT_AS, (self.LIMITS["address_bytes"],) * 2)
                    resource.setrlimit(resource.RLIMIT_FSIZE, (self.LIMITS["staging_file_bytes"],) * 2)
                    resource.setrlimit(resource.RLIMIT_NOFILE, (self.LIMITS["descriptors"],) * 2)
                with (directory / "stdout.log").open("xb") as stdout, (directory / "stderr.log").open("xb") as stderr:
                    try:
                        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                            env=self.environment, close_fds=True, pass_fds=tuple(fds), preexec_fn=limits, start_new_session=True)
                    except (OSError, subprocess.SubprocessError) as exc:
                        self._write(directory / "launch-error.json", dict(phase="POPEN_DID_NOT_RETURN", actual_exit="UNOBSERVED", error=str(exc)))
                        raise
                    self.dispatch_count += 1
                    try:
                        code = process.wait(timeout=self.LIMITS["wall_seconds"])
                        complete = True
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            # Exit may win the race with termination. Always
                            # collect its status; a timeout stays incomplete.
                            pass
                        code = process.wait()
                    except BaseException:
                        if process.poll() is None:
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        code = process.wait()
                        raise
                    finally:
                        # A completed process is never hidden by a later observer
                        # exception, KeyboardInterrupt, archive or receipt error.
                        if code is not None:
                            self._write(directory / "exit-code.txt", (str(code) + "\n").encode())
                    stdout.flush()
                    stderr.flush()
                    os.fsync(stdout.fileno())
                    os.fsync(stderr.fileno())
            finally:
                for fd in fds:
                    os.close(fd)
            raw = {name: read_regular(directory / name)[1] for name in ("stdout.log", "stderr.log", "exit-code.txt", "dispatch.json")}
            if any(len(raw[n]) > self.LIMITS["stream_bytes"] for n in ("stdout.log", "stderr.log")):
                raise compiler.WorkGraphError("raw stream byte bound exceeded; actual exit retained")
            receipt = dict(schema="implementaudit.verifier-prefix-issued.v1", scope=PROFILE, producer=self.producer,
                key=acquired["key"], exit=code, complete=complete, dispatch=self.dispatch_count,
                stdout_sha256=digest(raw["stdout.log"]), stderr_sha256=digest(raw["stderr.log"]),
                prefix_sha256=digest(acquired["prefix"]), group=acquired["acquired"]["scope"],
                semantic_artifacts=[], effects="PRIVATE_WRITES_DISCARDED_NO_SUCCESSOR_SPLICE",
                canonical_acceptance="UNQUALIFIED", authority="NONE")
            raw["receipt.json"] = encode(receipt)
            self._write(directory / "receipt.json", raw["receipt.json"])
            for name in raw:
                (directory / name).chmod(0o400)
            return receipt, dict(key=acquired["key"], directory=directory, retained=raw,
                required_objects=acquired["required_objects"], observed_at=time.monotonic())

        def run(self):
            if os.getpid() != self.producer_pid:
                raise compiler.WorkGraphError("producer process changed; receipt import is unsupported")
            if not self._consumption_lock.acquire(blocking=False):
                raise compiler.WorkGraphError("concurrent prefix consumption is unsupported")
            try:
                return self._consume()
            finally:
                self._consumption_lock.release()

        def _consume(self):
            self._custody()
            if self.generation >= 64:
                raise compiler.WorkGraphError("finite session consumption capacity exhausted")
            self.generation += 1
            directory = self.output / ("generation-%06d" % self.generation)
            directory.mkdir(mode=0o700)
            keys, refused = self._issued_keys()
            if refused:
                self._write(directory / "refusal.json", dict(reason="ISSUED_EVIDENCE_INVALID", details=refused))
                raise compiler.WorkGraphError("prior issued evidence refused: " + str(refused))
            if self._attempted and not self._issued:
                raise compiler.WorkGraphError("failed or interrupted execution has no reusable issued result")
            start = self._acquire()
            self._write(directory / "acquisition.json", start["acquired"])
            self._write(directory / "mapping.json", start["graph"])
            if PROFILE in keys:
                if keys[PROFILE] != start["key"]:
                    self._write(directory / "refusal.json", dict(reason="CURRENT_INPUTS_CHANGED", issued_key=keys[PROFILE], current_key=start["key"]))
                    raise compiler.WorkGraphError("current source/runtime/observer changed; prior receipt refused")
                retained = self._issued[PROFILE]
                receipt = compiler.decode_strict_json_bytes(retained["retained"]["receipt.json"], "issued prefix result")
                disposition = "REUSED"
            else:
                self._attempted = True
                receipt, retained = self._execute_group(start, directory / "execution")
                disposition = "EXECUTED"
            after = self._acquire()
            self._same(start, after, directory, "during-consumption")
            # Integrity is checked again after reacquisition, before the result
            # is consumed. Callers can neither supply nor reseal an issuer.
            if disposition == "REUSED" and self._issued_keys()[0].get(PROFILE) != start["key"]:
                raise compiler.WorkGraphError("issued evidence changed during consumption")
            if disposition == "EXECUTED":
                self._verify_new_result(retained)
            if receipt["exit"] == 0 and receipt["complete"]:
                self._issued[PROFILE] = retained
            result = dict(schema="implementaudit.verifier-prefix-consumption.v1", scope=PROFILE,
                producer=self.producer, generation=self.generation, key=start["key"],
                disposition=disposition, receipt_digest=digest(retained["retained"]["receipt.json"]),
                evidence_directory=str(retained["directory"]), exit=receipt["exit"], complete=receipt["complete"],
                dispatch_count=self.dispatch_count, group=start["acquired"]["scope"],
                canonical_acceptance="UNQUALIFIED", authority="NONE")
            self._write(directory / "result.json", result)
            return copy.deepcopy(result)
    return ComposedPrefixSession


def bootstrap():
    if sys.argv[1:] != ["--materialize"]:
        raise ValueError("prefix helper is only a qualifier-owned bootstrap")
    os.closerange(3, 4096)
    os.umask(0o022)
    data = read_regular(Path("/profile/source.tar"), single_link=False)[1]
    raw = read_regular(Path("/profile/source.json"), MANIFEST_BOUND, single_link=False)[1]
    expected = json.loads(raw)
    materialize_archive(data, expected, Path("/work"))
    # This name was absent from the complete acquired source. Its location
    # preserves the original registry's dirname-parent root calculation; source
    # scanners already exclude the native task directory. No source is replaced.
    Path("/work/" + RESERVED).mkdir(mode=0o700)
    prefix = read_regular(Path("/profile/prefix.sh"), MANIFEST_BOUND, single_link=False)[1]
    path = Path("/work/" + RESERVED + "/verify-package.sh")
    with path.open("xb") as stream:
        stream.write(prefix)
    path.chmod(0o400)
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024**2,) * 2)
    os.execv("/usr/bin/bash", ["/usr/bin/bash", "--noprofile", "--norc", str(path)])


if __name__ == "__main__":
    bootstrap()
