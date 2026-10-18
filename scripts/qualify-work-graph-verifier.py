#!/usr/bin/env python3
"""Capture an optional legacy/DAG verifier run without changing its registry.

This transport imports the single graph compiler. It does not own a second
registry, choose parallel tests, supply release authority, or install anything.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
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
LOADED_DRIVER = Path(__file__).read_bytes()
SPEC = importlib.util.spec_from_file_location("work_graph", ROOT / "skills/implementaudit/scripts/compile-work-graph.py")
WG = importlib.util.module_from_spec(SPEC)
LOADED_COMPILER = Path(SPEC.origin).read_bytes()
exec(compile(LOADED_COMPILER, SPEC.origin, "exec"), WG.__dict__)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_identity():
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT)
    names = git("ls-files", "-z").split(b"\0")
    files = []
    for name in names:
        if not name:
            continue
        path = ROOT / os.fsdecode(name)
        data = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes() if path.is_file() else b"MISSING"
        files.append([os.fsdecode(name), sha(data)])
    return dict(head=git("rev-parse", "HEAD").decode().strip(), tree=git("rev-parse", "HEAD^{tree}").decode().strip(),
                tracked_source_digest=sha(WG.canonical_json_v1(files)),
                status_digest=sha(git("status", "--porcelain=v1", "-z", "--untracked-files=all")))


def verified_record(directory):
    """Check retained record integrity, not execution authenticity or artifacts."""
    def read_json(name):
        return WG.decode_strict_json_bytes((directory / name).read_bytes(), name)
    result, mapping = read_json("result.json"), read_json("mapping.json")
    registry = b"".join(n["source"].encode() for n in mapping["nodes"])
    WG.verifier_command_stream_v1(mapping, registry)
    names = [n["id"] for n in mapping["nodes"]]
    exit_bytes = (directory / "exit-code.txt").read_bytes()
    valid = (result["schema"] == "implementaudit.verifier-run.v1" and
             result["mode"] in {"legacy", "dag"} and
             result["graph_digest"] == mapping["digest"] and
             result["registry_sha256"] == mapping["registry_sha256"] and
             result["environment"] == mapping["environment"] and
             type(result["mapped_nodes"]) is int and result["mapped_nodes"] == len(names) and
             type(result["registered_tests"]) is int and result["registered_tests"] == len(mapping["test_nodes"]) and
             [n["node"] for n in result["nodes"]] == names and
             type(result["exit"]) is int and re.fullmatch(rb"-?(?:0|[1-9][0-9]*)\n", exit_bytes) is not None and
             int(exit_bytes) == result["exit"] and
             all(result[stream + "_sha256"] == sha((directory / (stream + ".log")).read_bytes()) for stream in ("stdout", "stderr")))
    if not valid:
        raise WG.WorkGraphError("inconsistent verifier result, mapping, raw streams or durable exit")
    return result


def compare(left, right, out):
    a, b = (verified_record(p) for p in (left, right))
    checks = dict(same_source=a["before"] == b["before"] == a["after"] == b["after"],
                  same_registry=a["registry_sha256"] == b["registry_sha256"],
                  same_environment=a["environment"] == b["environment"],
                  same_exit=a["exit"] == b["exit"],
                  same_stdout=(left / "stdout.log").read_bytes() == (right / "stdout.log").read_bytes(),
                  same_stderr=(left / "stderr.log").read_bytes() == (right / "stderr.log").read_bytes(),
                  route_pair={a["mode"], b["mode"]} == {"legacy", "dag"})
    result = dict(schema="implementaudit.verifier-correspondence.v1", checks=checks,
                  raw_observables_equal=all(checks.values()), normalization="NONE_RAW_BYTES",
                  evidence_semantics="NODE_AND_WHOLE_PROCESS_ONLY; TRANSITIVE_OUTPUT_ARTIFACT_SEMANTICS_UNQUALIFIED",
                  canonical_conversion="NOT_PERFORMED", retirement="NOT_PERFORMED", authority="NONE")
    out.write_bytes(WG.canonical_json_v1(result) + b"\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if all(checks.values()) else 1


def run(mode, output):
    output.mkdir(parents=True, exist_ok=False)
    before = source_identity()
    environment = dict(platform=platform.platform(), python=sys.version,
                       python_executable=sys.executable,
                       bash=subprocess.check_output(["bash", "--version"]).decode().splitlines()[0],
                       git=subprocess.check_output(["git", "--version"]).decode().strip(),
                       selected_environment={k: os.environ.get(k) for k in ("PATH", "LANG", "LC_ALL", "TZ", "PYTHONDONTWRITEBYTECODE")})
    registry = (ROOT / "scripts/verify-package.sh").read_bytes()
    tests = WG.verifier_registered_tests_v1(registry)
    graph = WG.compile_verifier_graph_v1(registry, tests, environment)
    actual_tests = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("*.test.sh"))
    registration_complete = actual_tests == tests
    (output / "mapping.json").write_bytes(WG.canonical_json_v1(graph) + b"\n")
    with tempfile.TemporaryDirectory(prefix="r0035-verifier-stream-") as temporary:
        stream = Path(temporary) / "commands.bin"
        stream.write_bytes(WG.verifier_command_stream_v1(graph, registry))
        if mode == "legacy":
            command = ["bash", "scripts/verify-package.sh"]
        else:
            command = ["bash", "scripts/run-work-graph-verifier.sh", str(stream), str(output / "nodes.tsv"), str(len(graph["nodes"])), sha(stream.read_bytes())]
        started = time.monotonic()
        with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
            process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr)
            # Retain the actual nested exit before any source/trace/JSON work.
            # A later wrapper error cannot silently erase a completed verdict.
            with (output / "exit-code.txt").open("w") as terminal:
                terminal.write(str(process.returncode) + "\n")
                terminal.flush()
                os.fsync(terminal.fileno())
    after = source_identity()
    observed = {}
    if mode == "dag":
        for line in (output / "nodes.tsv").read_text().splitlines():
            name, state = line.split("\t")
            observed[name] = state
    node_results = []
    for n in graph["nodes"]:
        state = observed.get(n["id"])
        status = "PASS" if state == "PASS" else ("INTERRUPTED" if process.returncode < 0 else "FAIL") if state == "START" else "UNSETTLED"
        node_results.append(dict(node=n["id"], status=status, terminal=state is not None))
    result = dict(schema="implementaudit.verifier-run.v1", mode=mode, command=command[:2],
                  before=before, after=after, environment=environment,
                  registry_sha256=sha(registry), graph_digest=graph["digest"],
                  mapped_nodes=len(graph["nodes"]), registered_tests=len(tests),
                  registration_complete=registration_complete,
                  exit=process.returncode, elapsed_ms=int((time.monotonic() - started) * 1000),
                  stdout_sha256=sha((output / "stdout.log").read_bytes()), stderr_sha256=sha((output / "stderr.log").read_bytes()),
                  nodes=node_results, authority="NONE")
    (output / "result.json").write_bytes(WG.canonical_json_v1(result) + b"\n")
    print(json.dumps({k: result[k] for k in ("mode", "exit", "elapsed_ms", "mapped_nodes", "registered_tests", "registration_complete", "stdout_sha256", "stderr_sha256")}, sort_keys=True))
    return process.returncode if process.returncode >= 0 else 128 - process.returncode


class VerifierTaskSession:
    """Live producer custody for a finite, isolated two-real-checker scope.

    No imported execution receipts, persistent cache admission, canonical
    predecessor substitution, native currentness or campaign qualification.
    The trusted task process/kernel observe execution. Candidate and runtime
    bytes are captured, mounted from sealed descriptors and rechecked at each
    consumption boundary; arbitrary concurrent host/producer compromise is
    outside this portable scope.
    """
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
                    scope="CONTROLLED_TASK_LEAVES_V1", producer=self.producer, source=str(self.source),
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

    def _image(self, files, source_observations):
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
        return manifest, self._object(self._encode(manifest))

    def _acquire(self):
        if os.getpid() != self.producer_pid:
            raise WG.WorkGraphError("producer process changed; receipt import is unsupported")
        if self.environment != self.ENVIRONMENT or self._engine_binding() != self._engine:
            raise WG.WorkGraphError("producer source or environment changed")
        state, contents = self._source_state()
        registry = contents.get("scripts/verify-package.sh")
        if registry is None:
            raise WG.WorkGraphError("missing tracked verifier registry")
        graph = WG.compile_verifier_graph_v1(registry, WG.verifier_registered_tests_v1(registry), self.environment)
        runtime = self._runtime()
        runtime_manifest, runtime_digest = self._image(runtime, {})
        inputs, images = {}, {}
        projected = {p for c in WG.VERIFIER_LEAF_CONTRACTS_V1.values() for p in c["reads"] + c["probes"]}
        for program, contract in WG.VERIFIER_LEAF_CONTRACTS_V1.items():
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
            manifest, digest = self._image(files, observations)
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
        binding = dict(producer=self.producer, root=[str(self.source), root_stat.st_dev, root_stat.st_ino],
                       engine=self._engine, observer=observer, kernel=list(platform.uname()),
                       runtime=runtime_digest, environment=self.environment, limits=self.LIMITS,
                       inherited_resource_limits=inherited_limits,
                       directory_modes=state["directories"], process_identity=[self.producer_pid, os.geteuid(), os.getegid()],
                       null_device=[null.st_rdev, stat.S_IMODE(null.st_mode)],
                       source_guard=sha(WG.canonical_json_v1({n: v for n, v in state["files"].items() if n not in projected})))
        acquired = dict(schema="implementaudit.verifier-acquisition.v1", scope="CONTROLLED_TASK_LEAVES_V1",
                        binding=binding, inputs=inputs)
        # Validate completeness and exact executable profiles before any dispatch.
        WG.compile_verifier_reuse_v1(graph, registry, acquired, {})
        return dict(state=state, acquired=acquired, graph=graph, registry=registry, images=images)

    def _issued_keys(self):
        keys, refused = {}, {}
        for node, receipt in self._issued.items():
            try:
                if time.monotonic() - receipt["observed_at"] > self.max_age:
                    raise WG.WorkGraphError("expired issued result")
                for name, data in receipt["retained"].items():
                    if self._regular(receipt["directory"] / name)[1] != data:
                        raise WG.WorkGraphError("issued output or receipt changed")
                for digest in receipt["required_objects"]:
                    if sha(self._regular(self.output / "objects" / digest)[1]) != digest:
                        raise WG.WorkGraphError("required execution input object changed")
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
            complete = True
            with (directory / "stdout.log").open("xb") as stdout, (directory / "stderr.log").open("xb") as stderr:
                try:
                    process = subprocess.Popen(["/usr/bin/bwrap", "--args", str(args_fd), *command], stdin=subprocess.DEVNULL,
                                stdout=stdout, stderr=stderr, env=self.environment, close_fds=True, pass_fds=tuple(fds),
                                preexec_fn=limits, start_new_session=True)
                except (OSError, subprocess.SubprocessError) as exc:
                    self._write(directory / "launch-error.json", dict(error=type(exc).__name__, detail=str(exc),
                                child_started=False, actual_exit="UNOBSERVED"))
                    raise
                self.dispatch_count += 1
                try:
                    code = process.wait(timeout=self.LIMITS["wall_seconds"])
                except subprocess.TimeoutExpired:
                    complete = False
                    os.killpg(process.pid, signal.SIGKILL)
                    code = process.wait()
                # The actual process exit survives any later recording error.
                self._write(directory / "exit-code.txt", (str(code) + "\n").encode())
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
        nodes, aggregate_stdout, aggregate_stderr = [], b"", b""
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
        result = dict(schema="implementaudit.verifier-task-consumption.v1", scope="CONTROLLED_TASK_LEAVES_V1",
                      producer=self.producer, generation=self.generation, source_digest=source_digest,
                      initial_plan_digest=plan["digest"], nodes=nodes, exit=code, dispatch_count=self.dispatch_count,
                      refused_cached_outputs=refused, omitted_canonical_nodes=plan["omitted_canonical_nodes"],
                      canonical_acceptance="UNQUALIFIED", authority="NONE")
        self._write(directory / "result.json", result)
        return copy.deepcopy(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["legacy", "dag", "compare", "scoped"])
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        if args.mode == "scoped" and len(args.paths) == 2:
            session = VerifierTaskSession(args.paths[0], args.paths[1])
            # A caller may request another current-source consumption, never
            # inject a receipt, plan, mutation command or claimed process exit.
            status = 0
            for line in sys.stdin.buffer:
                if WG.decode_strict_json_bytes(line, "scope request") != {"operation": "run"}:
                    raise WG.WorkGraphError("only a current-source run request is supported")
                result = session.run()
                status = max(status, result["exit"])
                print(json.dumps(result, sort_keys=True), flush=True)
            return status
        if args.mode == "compare" and len(args.paths) == 3:
            return compare(*args.paths)
        if args.mode in {"legacy", "dag"} and len(args.paths) == 1:
            return run(args.mode, args.paths[0].resolve())
        parser.error("run takes one fresh output directory; compare takes two run directories and a fresh result path")
    except (OSError, ValueError, KeyError, TypeError, WG.WorkGraphError, subprocess.SubprocessError) as exc:
        print("work-graph-verifier: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
