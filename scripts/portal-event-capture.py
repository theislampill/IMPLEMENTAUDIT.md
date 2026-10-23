#!/usr/bin/env python3
"""Repo-only, opt-in custody for the finite docs portal invocation profile.

The live supervisor forks the two actual entrypoints from acquired source bytes.
Stored records are declared consistency evidence, never execution credentials.
There is no arbitrary command/callback interface or native lifecycle authority.
"""
import contextlib
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import signal
import stat
import sys
import time
import traceback

ENV = "IMPLEMENTAUDIT_PORTAL_CAPTURE"
PROFILE = "DOCS_PORTAL_TEST_V1"
NODE = "COMMAND:tests/docs-portal.test.sh:0"
SOURCES = ("scripts/build-docs-portal.py", "scripts/check-docs-portal.py",
           "tests/docs-portal.test.sh", "scripts/verify-docs-portal.sh")
# These inspected source contracts deliberately refuse unreviewed successors.
SOURCE_PINS = {'scripts/build-docs-portal.py': 'e7d38cd1a44b7a435e67de6e5bfae2f96c1be5968b7237e2deaf8681935cfd9a', 'scripts/check-docs-portal.py': '83fc7248cba28f6c2e0db63da6ea453c8ada628e3ab371b78d9be1b209aeaf84', 'tests/docs-portal.test.sh': 'e4e2bdcf01a0e9a64bd18e4abcdbd0d6b48806f014c6750824a437fa371908d7', 'scripts/verify-docs-portal.sh': '8dee1bbb3aeab177c261fa6fcfe1f79b6a2d9b277068a11eddf9b144540b3ecb'}
LIMITS = dict(events=64, entries=4096, depth=32, file_bytes=16 * 1024 * 1024,
              tree_bytes=64 * 1024 * 1024, stream_bytes=8 * 1024 * 1024,
              session_bytes=512 * 1024 * 1024, runtime_bytes=128 * 1024 * 1024, wall_seconds=120)
LOADED_SOURCE = globals().get("_CAPTURE_SOURCE")
if LOADED_SOURCE is None:
    LOADED_SOURCE = Path(__file__).read_bytes()


class CaptureError(ValueError):
    pass


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise CaptureError("duplicate portal JSON member")
            result[key] = value
        return result
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(CaptureError("nonfinite portal JSON")))
    except RecursionError as exc:
        raise CaptureError("portal JSON nesting exceeds the parser bound") from exc


def identity(st):
    return [st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns]


def absolute(path):
    # No resolve(): a supplied symlink must be refused, not canonicalized away.
    return Path(os.path.abspath(path))


@contextlib.contextmanager
def directory(path):
    path = absolute(path)
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for name in path.parts[1:]:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def read(path, limit=None):
    limit = LIMITS["file_bytes"] if limit is None else limit
    path = absolute(path)
    with directory(path.parent) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise CaptureError("portal member requires a bounded regular file")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                data = stream.read(limit + 1)
            if (len(data) != before.st_size or identity(before) != identity(os.fstat(fd)) or
                    identity(before) != identity(os.stat(path.name, dir_fd=parent, follow_symlinks=False))):
                raise CaptureError("portal member changed during acquisition")
            return data, dict(mode=stat.S_IMODE(before.st_mode), bytes=len(data), sha256=digest(data))
        finally:
            os.close(fd)


def write(path, data):
    path = absolute(path)
    with directory(path.parent) as parent:
        fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())


def write_json(path, value):
    write(path, encode(value))


def load(path):
    return strict_json(read(path)[0])


def bounded_names(fd):
    result = []
    with os.scandir(fd) as entries:
        for entry in entries:
            if len(result) >= LIMITS["entries"]:
                raise CaptureError("portal directory exceeds entry limit")
            result.append(entry.name)
    return sorted(result)


def tree(path, target=None, *, byte_budget=None):
    """Complete ordinary membership/bytes/modes and separate live race stamps."""
    path = absolute(path)
    entries, stamps, total = {}, {}, 0
    if target is not None:
        target.mkdir(mode=0o700)
    def walk(parent, name, rel, depth):
        nonlocal total
        if depth > LIMITS["depth"] or len(entries) >= LIMITS["entries"]:
            raise CaptureError("portal tree exceeds entry/depth limit")
        before = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if not (stat.S_ISREG(before.st_mode) or stat.S_ISDIR(before.st_mode)):
            raise CaptureError("portal artifact requires ordinary files/directories without symlinks")
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK |
                     (os.O_DIRECTORY if stat.S_ISDIR(before.st_mode) else 0), dir_fd=parent)
        try:
            st = os.fstat(fd)
            if identity(st) != identity(before):
                raise CaptureError("portal artifact replaced during acquisition")
            mode = stat.S_IMODE(st.st_mode)
            dest = None if target is None else target if rel == "." else target / rel
            if stat.S_ISDIR(st.st_mode):
                members = bounded_names(fd)
                entries[rel] = dict(kind="DIRECTORY", mode=mode, members=members)
                if dest is not None and rel != ".":
                    dest.mkdir(mode=0o700)
                for member in members:
                    walk(fd, member, member if rel == "." else rel + "/" + member, depth + 1)
                if bounded_names(fd) != members:
                    raise CaptureError("portal artifact membership changed during acquisition")
                if dest is not None:
                    dest.chmod(mode)
            else:
                total += st.st_size
                if (st.st_size > LIMITS["file_bytes"] or total > LIMITS["tree_bytes"] or
                        (byte_budget is not None and total > byte_budget)):
                    raise CaptureError("portal artifact exceeds byte limit")
                with os.fdopen(fd, "rb", closefd=False) as stream:
                    data = stream.read(LIMITS["file_bytes"] + 1)
                if len(data) != st.st_size:
                    raise CaptureError("portal artifact length changed during acquisition")
                entries[rel] = dict(kind="FILE", mode=mode, bytes=len(data), sha256=digest(data))
                if dest is not None:
                    write(dest, data)
                    dest.chmod(mode)
            if (identity(st) != identity(os.fstat(fd)) or
                    identity(st) != identity(os.stat(name, dir_fd=parent, follow_symlinks=False))):
                raise CaptureError("portal artifact changed during acquisition")
            stamps[rel] = identity(st)
        finally:
            os.close(fd)
    with directory(path.parent) as parent:
        walk(parent, path.name, ".", 0)
    if entries["."]["kind"] != "DIRECTORY":
        raise CaptureError("portal artifact root must be a directory")
    return entries, stamps


def process_identity(pid=None):
    base = Path("/proc") / ("self" if pid is None else str(pid))
    # Linux proc identity is an observation of our live lineage, not a token.
    data = (base / "stat").read_text()
    fields = data[data.rindex(")") + 2:].split()
    status = (base / "status").read_text().splitlines()
    namespace = next(line.split()[1:] for line in status if line.startswith("NSpid:"))
    return dict(pid=int(data.split(" ", 1)[0]), namespace_pid=int(namespace[-1]),
                ppid=int(fields[1]), start_ticks=int(fields[19]), uid=base.stat().st_uid)


def lineage(ancestor):
    result, pid = [], None
    for _ in range(64):
        item = process_identity(pid)
        result.append(item)
        if item == ancestor:
            return result
        if item["pid"] <= 1 or item["ppid"] == item["pid"]:
            break
        pid = item["ppid"]
    raise CaptureError("portal invocation is outside the live qualifier/node lineage")


def validate_process(value):
    fields = {"pid", "namespace_pid", "ppid", "start_ticks", "uid"}
    if (type(value) is not dict or set(value) != fields or
            any(type(v) is not int or v < 0 for v in value.values()) or
            value["pid"] == 0 or value["namespace_pid"] == 0):
        raise CaptureError("invalid declared portal process observation")


def validate_lineage(values, ancestor):
    validate_process(ancestor)
    if type(values) is not list or not 1 <= len(values) <= 64:
        raise CaptureError("invalid declared portal process lineage")
    for value in values:
        validate_process(value)
    if (values[-1] != ancestor or len({p["pid"] for p in values}) != len(values) or
            any(child["ppid"] != parent["pid"] for child, parent in zip(values, values[1:]))):
        raise CaptureError("inconsistent declared portal process lineage")


def bounded_integer(value, minimum, maximum):
    return type(value) is int and minimum <= value <= maximum


def bounded_text(value, maximum):
    if type(value) is not str or not value or "\0" in value:
        return False
    try:
        return len(value.encode("utf-8")) <= maximum
    except UnicodeError:
        return False


def declared_digest(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def declared_relative_path(value, *, root=False):
    if root and value == ".":
        return True
    return (bounded_text(value, 4096) and len(value.split("/")) <= LIMITS["depth"] and
            all(part not in {"", ".", ".."} and bounded_text(part, 255) for part in value.split("/")))


def validate_file_observation(value, label, *, byte_limit, kind=False):
    fields = {"mode", "bytes", "sha256"} | ({"kind"} if kind else set())
    if (type(value) is not dict or set(value) != fields or
            (kind and value["kind"] != "FILE") or
            not bounded_integer(value["mode"], 0, 0o7777) or
            not bounded_integer(value["bytes"], 0, byte_limit) or
            not declared_digest(value["sha256"])):
        raise CaptureError("invalid bounded " + label + " file observation")


def validate_tree_observation(value, label):
    """Validate a declared ordinary tree without consulting its claimed root."""
    if type(value) is not dict or not 1 <= len(value) <= LIMITS["entries"] or "." not in value:
        raise CaptureError("invalid " + label + " tree population")
    children, total = {}, 0
    for name, member in value.items():
        if not declared_relative_path(name, root=True) or type(member) is not dict:
            raise CaptureError("invalid " + label + " tree path/member")
        if member.get("kind") == "DIRECTORY":
            if (set(member) != {"kind", "mode", "members"} or
                    not bounded_integer(member["mode"], 0, 0o7777) or
                    type(member["members"]) is not list or len(member["members"]) > LIMITS["entries"] or
                    any(not bounded_text(n, 255) or "/" in n or n in {".", ".."} for n in member["members"]) or
                    member["members"] != sorted(set(member["members"]))):
                raise CaptureError("invalid " + label + " directory observation")
            children[name] = []
        else:
            validate_file_observation(member, label, byte_limit=LIMITS["file_bytes"], kind=True)
            total += member["bytes"]
    if "." not in children or total > LIMITS["tree_bytes"]:
        raise CaptureError("invalid or oversized " + label + " tree")
    for name in value:
        if name != ".":
            parent, _, leaf = name.rpartition("/")
            parent = parent or "."
            if parent not in children:
                raise CaptureError("missing " + label + " parent directory")
            children[parent].append(leaf)
    if any(value[name]["members"] != sorted(members) for name, members in children.items()):
        raise CaptureError("inconsistent " + label + " directory membership")
    return total


def validate_source_context(value, expected_root):
    fields = {"root", "portal", "declared_files", "coverage"}
    if (type(value) is not dict or set(value) != fields or value["root"] != expected_root or
            not bounded_text(value["root"], 4096) or str(absolute(value["root"])) != value["root"] or
            value["coverage"] != "PORTAL_DECLARED_SOURCE_OBSERVATION_NOT_TRANSITIVE_READ_CLOSURE"):
        raise CaptureError("invalid portal source observation schema/context")
    total = validate_tree_observation(value["portal"], "portal source")
    if value["portal"].get("site.json", {}).get("kind") != "FILE":
        raise CaptureError("missing portal site source observation")
    files = value["declared_files"]
    required = {"package/implementaudit-package.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"}
    if type(files) is not dict or not 1 <= len(files) <= LIMITS["entries"] or not required <= set(files):
        raise CaptureError("invalid portal declared source population")
    for name, member in files.items():
        if not declared_relative_path(name):
            raise CaptureError("invalid portal declared source path")
        validate_file_observation(member, "portal declared source", byte_limit=LIMITS["file_bytes"])
        total += member["bytes"]
        if name.startswith("docs/portal/"):
            relative = name[len("docs/portal/"):]
            if value["portal"].get(relative) != dict(kind="FILE", **member):
                raise CaptureError("contradictory repeated portal source observation")
    if total > LIMITS["tree_bytes"]:
        raise CaptureError("portal declared source bytes exceed limit")


def validate_runtime_observation(value, parent):
    fields = {"runtime", "process", "actual_environment_sha256"}
    if type(value) is not dict or set(value) != fields or not declared_digest(value["actual_environment_sha256"]):
        raise CaptureError("invalid portal actual runtime/environment observation")
    validate_process(value["process"])
    if value["process"]["ppid"] != parent["pid"]:
        raise CaptureError("foreign portal actual-child process observation")
    runtime = value["runtime"]
    fields = {"executable", "observation", "version", "implementation", "flags", "environment_sha256", "coverage"}
    if (type(runtime) is not dict or set(runtime) != fields or
            not bounded_text(runtime["executable"], 4096) or str(absolute(runtime["executable"])) != runtime["executable"] or
            not bounded_text(runtime["version"], 4096) or not bounded_text(runtime["implementation"], 64) or
            not declared_digest(runtime["environment_sha256"]) or
            runtime["coverage"] != "ACTUAL_FORKED_PYTHON_NOT_TOOLCHAIN_CLOSURE" or
            type(runtime["flags"]) is not list or not 1 <= len(runtime["flags"]) <= 64 or
            any(type(flag) is not bool and not bounded_integer(flag, -(2 ** 31), 2 ** 31 - 1)
                for flag in runtime["flags"])):
        raise CaptureError("invalid portal nested runtime observation")
    validate_file_observation(runtime["observation"], "portal runtime", byte_limit=LIMITS["runtime_bytes"])
    if runtime["observation"]["bytes"] == 0:
        raise CaptureError("empty portal runtime executable observation")


def validate_input_stamps(value, artifact):
    if type(value) is not dict or set(value) != set(artifact):
        raise CaptureError("incomplete checker input observation window")
    for name, stamp in value.items():
        if (type(stamp) is not list or len(stamp) != 6 or
                not bounded_integer(stamp[0], 0, 2 ** 64 - 1) or
                not bounded_integer(stamp[1], 1, 2 ** 64 - 1) or
                not bounded_integer(stamp[2], 0, 0o177777) or
                not bounded_integer(stamp[3], 0, 2 ** 63 - 1) or
                any(not bounded_integer(v, -(2 ** 63), 2 ** 63 - 1) for v in stamp[4:])):
            raise CaptureError("invalid bounded checker input identity stamp")
        member = artifact[name]
        kind = stat.S_IFDIR if member["kind"] == "DIRECTORY" else stat.S_IFREG
        if (stat.S_IFMT(stamp[2]) != kind or stat.S_IMODE(stamp[2]) != member["mode"] or
                (member["kind"] == "FILE" and stamp[3] != member["bytes"])):
            raise CaptureError("checker input stamp contradicts retained artifact kind/mode/bytes")


def profile():
    def slot(op, code, context, target):
        return dict(operation=op, exit=code, context=context, target=target)
    result = [slot("BUILD", 0, "CANONICAL", "portal-out"), slot("CHECK", 0, "CANONICAL", "portal-out")]
    result += [slot(op, code, "FIXTURE", "docs-portal") for op, code in
               [("BUILD", 0), ("BUILD", 0), ("CHECK", 0), ("BUILD", 0), ("CHECK", 0)] + [("BUILD", 1)] * 8]
    result += [slot("BUILD", 0, "CANONICAL", "portal-out-2")]
    result += [slot("CHECK", 1, "CANONICAL", name) for name in (
        "bad-portal", "bad-single-quoted", "bad-unquoted", "bad-raw-command", "bad-table-classes",
        "bad-footer-proof", "bad-release-label", "bad-overview-release", "bad-marker-taxonomy",
        "bad-stage-sequence", "bad-sidecar-freshness", "bad-slash-boundary", "bad-helper-path-boundary",
        "bad-comparison-spotlight", "bad-magnet-contract", "bad-card-glass", "bad-card-shimmer",
        "bad-top-tabs", "bad-sidebar-tree", "bad-nav", "bad-extra-output", "bad-meta", "bad-meta-extra")]
    result += [slot("BUILD", 1, "CANONICAL", ".")]
    result += [slot(op, code, "CANONICAL", "portal-custody") for op, code in
               [("BUILD", 0), ("CHECK", 0), ("CHECK", 1), ("CHECK", 1), ("CHECK", 0), ("BUILD", 0), ("CHECK", 0)]]
    result += [slot("BUILD", 0, "NESTED_VERIFY", "docs-portal"), slot("CHECK", 0, "NESTED_VERIFY", "docs-portal")]
    return result


def observed_sources(root):
    result = {}
    for name in SOURCES:
        data, member = read(root / name)
        if digest(data) != SOURCE_PINS.get(name):
            raise CaptureError("unsupported portal source contract: " + name)
        result[name] = member
    helper, member = read(root / "scripts/portal-event-capture.py")
    if helper != LOADED_SOURCE:
        raise CaptureError("loaded portal helper differs from current source")
    result["scripts/portal-event-capture.py"] = member
    return result


def prepare(path, source_root, mapping, source):
    if sys.platform != "linux" or not hasattr(os, "fork"):
        raise CaptureError("portal capture requires Linux process lineage and POSIX no-follow descriptors")
    node = [n for n in mapping["nodes"] if n["id"] == NODE]
    if (len(node) != 1 or node[0]["source"].strip() != "bash tests/docs-portal.test.sh" or
            node[0]["kind"] != "TEST"):
        raise CaptureError("portal capture requires the exact registered zero-argument docs test")
    sources = observed_sources(source_root)
    for name, member in sources.items():
        actual = source.get("members", {}).get(name, {})
        if actual.get("sha256") != member["sha256"] or actual.get("kind") != "FILE":
            raise CaptureError("portal source is absent from the qualifier acquisition")
    path.mkdir(mode=0o700)
    (path / "loaded").mkdir(mode=0o700)
    for name in sources:
        write(path / "loaded" / Path(name).name, read(source_root / name)[0])
    request = dict(schema="implementaudit.portal-request.v1", profile=PROFILE, run_id=os.urandom(16).hex(),
                   source_root=str(source_root), output=str(path),
                   source_binding={key: source[key] for key in ("head", "tree", "tracked_source_digest", "status_digest")},
                   mapping=dict(graph_digest=mapping["digest"], registry_sha256=mapping["registry_sha256"],
                                node={key: node[0][key] for key in ("id", "source", "source_sha256", "command")}),
                   sources=sources, plan=profile(), limits=LIMITS,
                   qualifier=process_identity(), authority="NONE")
    write_json(path / "request.json", request)
    write(path / "lock", b"")
    return request


def validate_request(request):
    fields = {"schema", "profile", "run_id", "source_root", "output", "source_binding", "mapping",
              "sources", "plan", "limits", "qualifier", "authority"}
    if (type(request) is not dict or set(request) != fields or
            request["schema"] != "implementaudit.portal-request.v1" or request["profile"] != PROFILE or
            encode(request["plan"]) != encode(profile()) or request["limits"] != LIMITS or request["authority"] != "NONE" or
            type(request["run_id"]) is not str or len(request["run_id"]) != 32 or
            any(c not in "0123456789abcdef" for c in request["run_id"]) or
            any(type(request[k]) is not str or str(absolute(request[k])) != request[k] for k in ("source_root", "output")) or
            set(request["sources"]) != set(SOURCES) | {"scripts/portal-event-capture.py"} or
            request["mapping"]["node"]["id"] != NODE or
            request["mapping"]["node"]["source"].strip() != "bash tests/docs-portal.test.sh"):
        raise CaptureError("unsupported portal request/profile")
    for name in SOURCES:
        if request["sources"][name]["sha256"] != SOURCE_PINS.get(name):
            raise CaptureError("stale portal producer/checker/test contract")
    validate_process(request["qualifier"])
    source, output = Path(request["source_root"]), Path(request["output"])
    if source == output or source in output.parents:
        raise CaptureError("portal evidence must be outside the candidate source")
    return request


@contextlib.contextmanager
def live_request():
    value = os.environ.get(ENV)
    if not value or not Path(value).is_absolute() or Path(value).name != "request.json":
        raise CaptureError("portal capture needs an explicit absolute request path")
    request = validate_request(load(Path(value)))
    path = Path(request["output"])
    if Path(value) != path / "request.json":
        raise CaptureError("foreign portal request destination")
    lineage(request["qualifier"])
    with directory(path) as parent:
        fd = os.open("lock", os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise CaptureError("unsupported portal capture lock")
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield path, request
        finally:
            os.close(fd)


def begin_node(temporary_root):
    with live_request() as (path, request):
        root = Path(request["source_root"])
        if Path.cwd() != root or observed_sources(root) != request["sources"]:
            raise CaptureError("foreign portal node source/cwd")
        owner = process_identity(process_identity()["ppid"])
        args = (Path("/proc") / str(owner["pid"]) / "cmdline").read_bytes().split(b"\0")[:-1]
        if args != [b"bash", b"tests/docs-portal.test.sh"]:
            raise CaptureError("portal node must be the registered actual test process")
        temporary_root = absolute(temporary_root)
        with directory(temporary_root) as fd:
            if stat.S_IMODE(os.fstat(fd).st_mode) != 0o700 or os.listdir(fd):
                raise CaptureError("portal test requires its fresh private temporary root")
        if root == temporary_root or root in temporary_root.parents or path in temporary_root.parents:
            raise CaptureError("unsupported portal test temporary root")
        write_json(path / "node.json", dict(schema="implementaudit.portal-node.v1", run_id=request["run_id"],
                   node=NODE, owner=owner, qualifier_lineage=lineage(request["qualifier"]),
                   temporary_root=str(temporary_root), cwd=str(root), source=request["sources"]["tests/docs-portal.test.sh"]))


def registered_node(path, request):
    node = load(path / "node.json")
    if node["run_id"] != request["run_id"] or node["node"] != NODE or node["cwd"] != request["source_root"]:
        raise CaptureError("foreign portal node registration")
    lineage(node["owner"])
    return node


def register_fixture(fixture):
    with live_request() as (path, request):
        node = registered_node(path, request)
        fixture = absolute(fixture)
        if fixture != Path(node["temporary_root"]) / "portal-release-identity":
            raise CaptureError("foreign portal fixture root")
        for name in (SOURCES[0], SOURCES[1], "scripts/portal-event-capture.py"):
            if read(fixture / name)[1] != request["sources"][name]:
                raise CaptureError("stale portal fixture executable")
        write_json(path / "fixture.json", dict(root=str(fixture), run_id=request["run_id"], node=NODE,
                   owner=node["owner"], registration_lineage=lineage(node["owner"])))


def source_context(root):
    portal, _ = tree(root / "docs/portal")
    site = load(root / "docs/portal/site.json")
    files = set(site.get("semantic_sources", []))
    for page in site["pages"].values():
        files.update(page.get("sources", []))
    files.update(("package/implementaudit-package.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"))
    if len(files) > LIMITS["entries"]:
        raise CaptureError("portal declared source count exceeds limit")
    members, total = {}, sum(v.get("bytes", 0) for v in portal.values())
    for name in sorted(files):
        p = Path(name)
        if p.is_absolute() or ".." in p.parts or not p.parts:
            raise CaptureError("unsupported portal declared source path")
        members[name] = read(root / p)[1]
        total += members[name]["bytes"]
        if total > LIMITS["tree_bytes"]:
            raise CaptureError("portal declared source bytes exceed limit")
    return dict(root=str(root), portal=portal, declared_files=members,
                coverage="PORTAL_DECLARED_SOURCE_OBSERVATION_NOT_TRANSITIVE_READ_CLOSURE")


def invocation(path, request, node, operation, script, ordinal):
    if ordinal >= len(request["plan"]):
        raise CaptureError("extra portal invocation")
    slot = request["plan"][ordinal]
    if operation != slot["operation"] or Path.cwd() != Path(request["source_root"]):
        raise CaptureError("reordered or foreign portal invocation")
    script = absolute(script)
    root = script.parents[1]
    expected_root = Path(request["source_root"])
    if slot["context"] == "FIXTURE":
        registered = load(path / "fixture.json")
        if registered["run_id"] != request["run_id"] or registered["node"] != NODE or registered["owner"] != node["owner"]:
            raise CaptureError("foreign portal fixture registration")
        expected_root = Path(registered["root"])
    name = "scripts/build-docs-portal.py" if operation == "BUILD" else "scripts/check-docs-portal.py"
    if script != expected_root / name:
        raise CaptureError("foreign portal producer source root")
    engines = {}
    for source in (SOURCES[0], SOURCES[1], "scripts/portal-event-capture.py"):
        data, member = read(root / source)
        if member != request["sources"][source]:
            raise CaptureError("stale portal producer/checker/helper bytes")
        engines[source] = data
    if engines["scripts/portal-event-capture.py"] != LOADED_SOURCE:
        raise CaptureError("portal helper loaded source drift")
    args = sys.argv[1:]
    if operation == "BUILD":
        if len(args) != 2 or args[0] != "--out":
            raise CaptureError("unsupported captured portal build argv")
        literal = args[1]
        target = absolute(root / literal)
    else:
        if len(args) != 1:
            raise CaptureError("unsupported captured portal checker argv")
        literal = args[0]
        target = absolute(literal)
    if slot["context"] == "FIXTURE":
        expected = root / "dist/docs-portal"
    elif slot["context"] == "NESTED_VERIFY":
        if ordinal == len(request["plan"]) - 2:
            if target.name != "docs-portal" or target.parent == root or root in target.parents or path in target.parents:
                raise CaptureError("foreign nested portal output")
            write_json(path / "nested.json", dict(path=str(target), run_id=request["run_id"]))
        expected = Path(load(path / "nested.json")["path"])
    else:
        expected = root if slot["target"] == "." else Path(node["temporary_root"]) / slot["target"]
    if target != expected:
        raise CaptureError("reordered or foreign portal artifact path")
    result = dict(operation=operation, ordinal=ordinal, node=NODE, run_id=request["run_id"],
                  cwd=str(Path.cwd()), source_root=str(root), script=str(script),
                  argv=list(sys.argv), process_argv=list(sys.orig_argv), artifact_path=str(target),
                  source_context=source_context(root), lineage=lineage(node["owner"]),
                  request_sha256=digest(encode(request)), sources=request["sources"])
    return result, engines[name], target


def runtime_observation():
    executable = Path("/proc/self/exe").resolve(strict=True)
    return dict(executable=str(executable), observation=read(executable, LIMITS["runtime_bytes"])[1], version=sys.version,
                implementation=sys.implementation.name, flags=list(sys.flags),
                environment_sha256=digest(b"\0".join(os.fsencode(k) + b"=" + os.fsencode(v)
                                            for k, v in sorted(os.environ.items()))),
                coverage="ACTUAL_FORKED_PYTHON_NOT_TOOLCHAIN_CLOSURE")


def execute(source, script, event, stream_budget):
    """Fork the actual Python state, then compile exactly the acquired entrypoint."""
    stdout = os.open(event / "stdout.log", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    stderr = os.open(event / "stderr.log", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    sys.stdout.flush()
    sys.stderr.flush()
    runtime = runtime_observation()
    pid, status, timed_out = None, None, False
    open_streams = [stdout, stderr]
    def terminate():
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            # The forked child may not have called setsid yet. Its unreaped
            # owned PID cannot be reused, so terminate that PID before waiting.
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        return os.waitpid(pid, 0)[1]
    try:
        pid = os.fork()
        if pid == 0:
            code = 0
            try:
                os.setsid()
                os.dup2(stdout, 1)
                os.dup2(stderr, 2)
                os.close(stdout)
                os.close(stderr)
                stream_limit = min(LIMITS["stream_bytes"], stream_budget // 2)
                resource.setrlimit(resource.RLIMIT_FSIZE, (stream_limit, stream_limit))
                os.environ.pop(ENV, None)
                write_json(event / "runtime.json", dict(runtime=runtime, process=process_identity(),
                           actual_environment_sha256=digest(b"\0".join(os.fsencode(k) + b"=" + os.fsencode(v)
                                                  for k, v in sorted(os.environ.items())))))
                namespace = dict(__name__="__main__", __file__=str(script), __package__=None, __cached__=None)
                exec(compile(source, str(script), "exec"), namespace)
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 0 if exc.code is None else 1
                if exc.code is not None and not isinstance(exc.code, int):
                    print(exc.code, file=sys.stderr)
            except BaseException as exc:
                code = 1
                sys.excepthook(type(exc), exc, exc.__traceback__.tb_next)
            finally:
                sys.stdout.flush()
                sys.stderr.flush()
            os._exit(code & 255)
        while open_streams:
            os.close(open_streams[-1])
            open_streams.pop()
        started = time.monotonic()
        while True:
            waited, observed = os.waitpid(pid, os.WNOHANG)
            if waited:
                status = observed
                break
            if time.monotonic() - started > LIMITS["wall_seconds"]:
                timed_out = True
                status = terminate()
                break
            time.sleep(0.01)
    except BaseException:
        if pid is not None and pid > 0 and status is None:
            status = terminate()
        raise
    finally:
        if pid != 0:
            for fd in open_streams:
                with contextlib.suppress(OSError):
                    os.close(fd)
            if status is not None:
                # Actual exit survives interruption and every later capture failure.
                write(event / "exit-code.txt", (str(os.waitstatus_to_exitcode(status)) + "\n").encode())
    code = os.waitstatus_to_exitcode(status)
    return code, runtime, timed_out


def event_names(path):
    with directory(path) as fd:
        names = [name for name in bounded_names(fd) if name.startswith("event-")]
    if names != ["event-%04d" % i for i in range(len(names))] or len(names) > LIMITS["events"]:
        raise CaptureError("missing, duplicate or reordered portal event population")
    return names


def capture(operation, script):
    event = None
    try:
        with live_request() as (path, request):
            node = registered_node(path, request)
            names = event_names(path)
            used = 0
            for name in names:
                previous = load(path / name / "event.json")
                if previous["capture_status"] != "COMPLETE":
                    raise CaptureError("preceding portal invocation did not complete capture")
                used += previous["stdout"]["bytes"] + previous["stderr"]["bytes"]
                used += sum(v.get("bytes", 0) for v in (previous["artifact"] or {}).values())
            remaining = LIMITS["session_bytes"] - used
            if remaining < 2 * LIMITS["stream_bytes"]:
                raise CaptureError("portal session exceeds remaining byte budget")
            inv, source, target = invocation(path, request, node, operation, script, len(names))
            event = path / ("event-%04d" % len(names))
            event.mkdir(mode=0o700)
            write_json(event / "invocation.json", inv)
            artifact = stamps = None
            if operation == "CHECK":
                artifact, stamps = tree(target, event / "artifact", byte_budget=remaining - 2 * LIMITS["stream_bytes"])
                remaining -= sum(v.get("bytes", 0) for v in artifact.values())
            write_json(event / "started.json", dict(operation=operation, ordinal=len(names), input_acquired=True))
            code, runtime, timed_out = execute(source, absolute(script), event, remaining)
            result = dict(schema="implementaudit.portal-event.v1", invocation=inv, operation=operation,
                          ordinal=len(names), exit=code, status="SUCCESS" if code == 0 else "INTERRUPTED" if code < 0 else "FAILURE",
                          expected_exit=request["plan"][len(names)]["exit"], capture_status="COMPLETE",
                          runtime=load(event / "runtime.json"), artifact=None, generation=None,
                          consumed_generation=None, input_stamps=stamps, after_stamps=None,
                          source_after=source_context(Path(inv["source_root"])),
                          previous_event_sha256=None if not names else digest(read(path / names[-1] / "event.json")[0]),
                          stdout=read(event / "stdout.log", LIMITS["stream_bytes"])[1],
                          stderr=read(event / "stderr.log", LIMITS["stream_bytes"])[1], timed_out=timed_out)
            if timed_out or runtime_observation() != runtime or result["source_after"] != inv["source_context"]:
                result["capture_status"] = "SOURCE_RUNTIME_OR_TIMEOUT_REFUSAL"
            if operation == "BUILD" and code == 0:
                artifact, _ = tree(target, event / "artifact", byte_budget=remaining - result["stdout"]["bytes"] - result["stderr"]["bytes"])
                result["generation"] = request["run_id"] + ":" + event.name
            if operation == "CHECK":
                after, after_stamps = tree(target)
                result["after_stamps"] = after_stamps
                if after != artifact or after_stamps != stamps:
                    result["capture_status"] = "CHECKER_INPUT_DRIFT"
                    write_json(event / "input-after.json", dict(artifact=after, stamps=after_stamps))
                for name in reversed(names):
                    previous = load(path / name / "event.json")
                    if previous["operation"] == "BUILD" and previous["exit"] == 0 and previous["invocation"]["artifact_path"] == str(target):
                        if previous["artifact"] == artifact and previous["invocation"]["source_root"] == inv["source_root"]:
                            result["consumed_generation"] = previous["generation"]
                        break
            result["artifact"] = artifact
            # Failed builds do not turn a pre-existing tree (or --out .) into a generation.
            write_json(event / "event.json", result)
            if result["capture_status"] != "COMPLETE":
                raise CaptureError(result["capture_status"])
            return code
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if event is not None:
            with contextlib.suppress(OSError):
                write_json(event / "capture-error.json", dict(type=type(exc).__name__, message=str(exc)))
        print("portal-event-capture: " + str(exc), file=sys.stderr)
        return 2
    finally:
        if event is not None:
            for name, destination in (("stdout", sys.stdout.buffer), ("stderr", sys.stderr.buffer)):
                with contextlib.suppress(OSError, ValueError):
                    data = read(event / (name + ".log"), LIMITS["stream_bytes"])[0]
                    destination.write(data)
                    destination.flush()


def finish_node(code):
    with live_request() as (path, request):
        node = registered_node(path, request)
        names = event_names(path)
        write_json(path / "node-return.json", dict(run_id=request["run_id"], node=NODE,
                   owner=node["owner"], shell_exit_at_cleanup=code, events=names,
                   complete=len(names) == len(request["plan"])))
        if code == 0 and len(names) != len(request["plan"]):
            raise CaptureError("omitted required portal invocation")


def exit_result(code):
    # Preserve the caller's signal result as well as ordinary integer exits.
    # The signal targets only this supervisor, after its own child has settled.
    if code < 0:
        signal.signal(-code, signal.SIG_DFL)
        os.kill(os.getpid(), -code)
    raise SystemExit(code)


def verify(path, request, *, require_complete):
    """Validate restored declarations and all retained bytes; no live authentication."""
    validate_request(request)
    if read(path / "request.json")[0] != encode(request):
        raise CaptureError("portal request differs from original qualifier binding")
    lock, lock_member = read(path / "lock")
    if lock or lock_member["mode"] != 0o600:
        raise CaptureError("invalid retained portal capture lock")
    for name, member in request["sources"].items():
        data, retained = read(path / "loaded" / Path(name).name)
        if retained["mode"] != 0o600 or len(data) != member["bytes"] or digest(data) != member["sha256"]:
            raise CaptureError("stale or corrupt retained portal executable")
    with directory(path / "loaded") as fd:
        if sorted(os.listdir(fd)) != sorted(Path(n).name for n in request["sources"]):
            raise CaptureError("foreign retained portal executable population")
    names = event_names(path)
    if len(names) > len(request["plan"]):
        raise CaptureError("duplicate or extra portal invocation exceeds the finite profile")
    node = load(path / "node.json") if (path / "node.json").exists() else None
    if node is None:
        if require_complete or names:
            raise CaptureError("missing portal node registration")
        with directory(path) as fd:
            if set(os.listdir(fd)) != {"request.json", "lock", "loaded"}:
                raise CaptureError("foreign incomplete portal handoff population")
        return dict(schema="implementaudit.portal-handoff.v1", request=request, records={}, events={}, complete=False,
                    coverage="INCOMPLETE_OR_FAILED_PORTAL_INVOCATIONS", authority="NONE")
    if (set(node) != {"schema", "run_id", "node", "owner", "qualifier_lineage", "temporary_root", "cwd", "source"} or
            node["schema"] != "implementaudit.portal-node.v1" or
            node["run_id"] != request["run_id"] or node["node"] != NODE or node["cwd"] != request["source_root"] or
            node["source"] != request["sources"]["tests/docs-portal.test.sh"]):
        raise CaptureError("foreign portal node/source binding")
    validate_lineage(node["qualifier_lineage"], request["qualifier"])
    if len(node["qualifier_lineage"]) < 2 or node["qualifier_lineage"][1] != node["owner"]:
        raise CaptureError("inconsistent portal node owner observation")
    temporary = Path(node["temporary_root"])
    if (str(absolute(temporary)) != str(temporary) or temporary == Path(request["source_root"]) or
            Path(request["source_root"]) in temporary.parents or Path(request["output"]) in temporary.parents):
        raise CaptureError("foreign portal temporary root")
    events, previous, total = {}, None, 0
    for index, name in enumerate(names):
        event = path / name
        record = load(event / "event.json")
        inv = record["invocation"]
        slot = request["plan"][index]
        required = {"schema", "invocation", "operation", "ordinal", "exit", "status", "expected_exit", "capture_status",
                    "runtime", "artifact", "generation", "consumed_generation", "input_stamps", "after_stamps", "source_after",
                    "previous_event_sha256", "stdout", "stderr", "timed_out"}
        invocation_fields = {"operation", "ordinal", "node", "run_id", "cwd", "source_root", "script", "argv",
                             "process_argv", "artifact_path", "source_context", "lineage", "request_sha256", "sources"}
        if (set(record) != required or set(inv) != invocation_fields or record["schema"] != "implementaudit.portal-event.v1" or
                type(record["ordinal"]) is not int or record["ordinal"] != index or type(inv["ordinal"]) is not int or inv["ordinal"] != index or
                record["operation"] != slot["operation"] or inv["operation"] != slot["operation"] or
                inv["run_id"] != request["run_id"] or inv["node"] != NODE or inv["cwd"] != request["source_root"] or
                inv["request_sha256"] != digest(encode(request)) or inv["sources"] != request["sources"] or
                encode(record["source_after"]) != encode(inv["source_context"]) or
                record["previous_event_sha256"] != previous or type(record["exit"]) is not int or
                type(record["expected_exit"]) is not int or record["expected_exit"] != slot["exit"] or
                record["status"] != ("SUCCESS" if record["exit"] == 0 else "INTERRUPTED" if record["exit"] < 0 else "FAILURE") or
                record["capture_status"] != "COMPLETE" or record["timed_out"] is not False or
                read(event / "exit-code.txt")[0] != (str(record["exit"]) + "\n").encode() or
                read(event / "invocation.json")[0] != encode(inv) or
                read(event / "runtime.json")[0] != encode(record["runtime"])):
            raise CaptureError("inconsistent portal event/source/result/order")
        validate_lineage(inv["lineage"], node["owner"])
        validate_runtime_observation(record["runtime"], inv["lineage"][0])
        if require_complete and record["exit"] != slot["exit"]:
            raise CaptureError("portal actual result does not satisfy the finite test expectation")
        expected_root = request["source_root"]
        if slot["context"] == "FIXTURE":
            fixture = load(path / "fixture.json")
            expected_root = str(Path(node["temporary_root"]) / "portal-release-identity")
            if (set(fixture) != {"root", "run_id", "node", "owner", "registration_lineage"} or
                    fixture["root"] != expected_root or fixture["run_id"] != request["run_id"] or fixture["node"] != NODE or fixture["owner"] != node["owner"]):
                raise CaptureError("foreign portal fixture source binding")
            validate_lineage(fixture["registration_lineage"], node["owner"])
        script_name = SOURCES[0] if slot["operation"] == "BUILD" else SOURCES[1]
        if inv["source_root"] != expected_root or inv["script"] != expected_root + "/" + script_name:
            raise CaptureError("foreign portal source root")
        validate_source_context(inv["source_context"], expected_root)
        validate_source_context(record["source_after"], expected_root)
        if slot["context"] == "FIXTURE":
            target = expected_root + "/dist/docs-portal"
        elif slot["context"] == "NESTED_VERIFY":
            nested = load(path / "nested.json")
            target = nested["path"]
            if (set(nested) != {"path", "run_id"} or nested["run_id"] != request["run_id"] or
                    str(absolute(target)) != target or Path(target).name != "docs-portal" or
                    Path(request["source_root"]) in Path(target).parents or Path(request["output"]) in Path(target).parents):
                raise CaptureError("foreign nested portal target")
        else:
            target = expected_root if slot["target"] == "." else str(Path(node["temporary_root"]) / slot["target"])
        argv = inv["argv"]
        if (inv["artifact_path"] != target or type(argv) is not list or not argv or
                any(type(arg) is not str for arg in argv) or
                type(inv["process_argv"]) is not list or len(inv["process_argv"]) <= len(argv) or
                any(type(arg) is not str for arg in inv["process_argv"]) or inv["process_argv"][-len(argv):] != argv or
                absolute(Path(inv["cwd"]) / argv[0]) != Path(inv["script"]) or
                (slot["operation"] == "BUILD" and (len(argv) != 3 or argv[1] != "--out" or absolute(Path(expected_root) / argv[2]) != Path(target))) or
                (slot["operation"] == "CHECK" and (len(argv) != 2 or absolute(Path(inv["cwd"]) / argv[1]) != Path(target)))):
            raise CaptureError("inconsistent portal original argv/artifact path")
        for stream in ("stdout", "stderr"):
            data, member = read(event / (stream + ".log"), LIMITS["stream_bytes"])
            if record[stream] != member or member["mode"] != 0o600:
                raise CaptureError("corrupt portal original raw process stream")
            total += len(data)
        artifact = record["artifact"]
        if artifact is not None:
            validate_tree_observation(artifact, "retained portal artifact")
            retained, _ = tree(event / "artifact")
            if retained != artifact:
                raise CaptureError("missing/extra/corrupt portal artifact bytes or modes")
            total += sum(v.get("bytes", 0) for v in retained.values())
        is_build = record["operation"] == "BUILD"
        if is_build:
            generation = request["run_id"] + ":" + name if record["exit"] == 0 else None
            if (record["generation"] != generation or record["consumed_generation"] is not None or
                    (artifact is not None) != (record["exit"] == 0) or
                    record["input_stamps"] is not None or record["after_stamps"] is not None):
                raise CaptureError("invalid portal generation or failed-build artifact")
        else:
            if artifact is None or record["generation"] is not None or record["input_stamps"] != record["after_stamps"]:
                raise CaptureError("changed checker input or false generation")
            validate_input_stamps(record["input_stamps"], artifact)
            validate_input_stamps(record["after_stamps"], artifact)
            expected_generation = None
            for old in reversed(list(events.values())):
                if old["operation"] == "BUILD" and old["exit"] == 0 and old["invocation"]["artifact_path"] == target:
                    if old["artifact"] == artifact and old["invocation"]["source_root"] == inv["source_root"]:
                        expected_generation = old["generation"]
                    break
            if record["consumed_generation"] != expected_generation:
                raise CaptureError("stale or false portal produced/consumed generation link")
        members = {"invocation.json", "started.json", "runtime.json", "stdout.log", "stderr.log", "exit-code.txt", "event.json"}
        if artifact is not None:
            members.add("artifact")
        with directory(event) as fd:
            if set(os.listdir(fd)) != members:
                raise CaptureError("foreign portal event member population")
        if load(event / "started.json") != dict(operation=record["operation"], ordinal=index, input_acquired=True):
            raise CaptureError("inconsistent portal event start")
        events[name] = record
        previous = digest(read(event / "event.json")[0])
    returned = load(path / "node-return.json") if (path / "node-return.json").exists() else None
    if returned is not None and (set(returned) != {"run_id", "node", "owner", "shell_exit_at_cleanup", "events", "complete"} or
            returned["run_id"] != request["run_id"] or returned["node"] != NODE or returned["owner"] != node["owner"] or
            type(returned["shell_exit_at_cleanup"]) is not int or not 0 <= returned["shell_exit_at_cleanup"] <= 255 or
            returned["events"] != names or returned["complete"] is not (len(names) == len(request["plan"]))):
        raise CaptureError("inconsistent declared portal node return")
    complete = (len(names) == len(request["plan"]) and returned is not None and
                returned == dict(run_id=request["run_id"], node=NODE, owner=node["owner"], shell_exit_at_cleanup=0,
                                 events=names, complete=True))
    if require_complete and not complete:
        raise CaptureError("omitted required portal invocation or incomplete node return")
    allowed = {"request.json", "lock", "loaded", "node.json"} | set(names)
    if returned is not None:
        allowed.add("node-return.json")
    if any(request["plan"][i]["context"] == "FIXTURE" for i in range(len(names))):
        allowed.add("fixture.json")
    if any(request["plan"][i]["context"] == "NESTED_VERIFY" for i in range(len(names))):
        allowed.add("nested.json")
    with directory(path) as fd:
        if set(os.listdir(fd)) != allowed:
            raise CaptureError("foreign portal handoff member population")
    if total > LIMITS["session_bytes"]:
        raise CaptureError("portal session exceeds byte limit")
    records = {}
    for name in sorted(allowed - set(names) - {"request.json", "lock", "loaded"}):
        records[name] = read(path / name)[1]
        if records[name]["mode"] != 0o600:
            raise CaptureError("changed portal lifecycle record mode")
    return dict(schema="implementaudit.portal-handoff.v1", request=request,
                records=records, events={name: digest(read(path / name / "event.json")[0]) for name in names}, complete=complete,
                coverage="FINITE_PORTAL_INVOCATIONS_COMPLETE" if complete else "INCOMPLETE_OR_FAILED_PORTAL_INVOCATIONS",
                authority="NONE")


def main():
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "begin-node":
            begin_node(sys.argv[2])
        elif len(sys.argv) == 3 and sys.argv[1] == "register-fixture":
            register_fixture(sys.argv[2])
        elif len(sys.argv) == 3 and sys.argv[1] == "finish-node" and sys.argv[2].isdigit():
            finish_node(int(sys.argv[2]))
        else:
            raise CaptureError("only finite portal node/fixture lifecycle hooks are supported")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("portal-event-capture: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
