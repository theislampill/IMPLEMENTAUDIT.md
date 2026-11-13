#!/usr/bin/env python3
"""Fixed live README artifact consumer, repository-only portable evidence.

The qualifier owns execution; CompletionContract/compiler own readiness,
selection and required JOINs. No serialized result or artifact is admissible.
"""
import base64
import copy
import hashlib
import os
from pathlib import Path
import stat
import threading

ROOT = Path(__file__).absolute().parents[1]
HELPER = "scripts/work-graph-readme-effect.py"
BOOTSTRAP = "scripts/readme-effect-bootstrap.py"
PREFIX = "scripts/qualify-work-graph-prefix.py"
QUALIFIER = "scripts/qualify-work-graph-verifier.py"
COMPLETION = "scripts/work-graph-completion.py"
RUNNER = "scripts/run-work-graph-verifier.sh"
COMPILER = "skills/implementaudit/scripts/compile-work-graph.py"
REGISTRY = "scripts/verify-package.sh"
PROGRAM = "scripts/generate-readme-diagrams.sh"
PROFILE = "PORTABLE_README_EFFECT_CONTRACT_V1"
CHECK_NODE = "COMMAND:scripts/generate-readme-diagrams.sh:0"
GENERATE, OUTPUT, CHECK, FINAL = "README_GENERATE", "README_OUTPUT", "README_CHECK", "README_FINAL"
DIAGRAMS = tuple("docs/diagrams/" + name + ".mmd" for name in (
    "tooling-architecture", "invocation-modes", "execution-spine"))
SUBJECTS = (PROGRAM, "README.md", *DIAGRAMS)
SOURCE_PATHS = (REGISTRY, *SUBJECTS)
PROGRAM_SHA256 = "607bc8c367989af45dedefcf3a3720af89d88c72d2cf58c0e779b27fade949f5"
REGISTRY_SHA256 = "77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698"
MAX_ARTIFACT, MAX_STREAM, MAX_FRAME = 512 * 1024, 16 * 1024, 1024 * 1024
MAGIC = b"R0035_README_EFFECT_V1\n"
PRODUCER_COMMAND = "python /work/scripts/readme-effect-bootstrap.py --produce\n"
ORIGINAL_PRODUCER_COMMAND = "bash scripts/generate-readme-diagrams.sh\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


# The fixed receiving loader compiles this exact captured buffer. Direct import
# cannot infer its executed source by reopening __file__, and cannot load owners.
_CAPTURE = globals().pop("_R0035_EFFECT_OWNER_CAPTURE", None)
if (type(_CAPTURE) is not dict or set(_CAPTURE) != {"root", "sources", "pins", "ancestors", "modules"}
        or _CAPTURE["root"] != str(ROOT)
        or set(_CAPTURE["sources"]) != {HELPER, BOOTSTRAP, PREFIX, QUALIFIER, COMPLETION, RUNNER, COMPILER}
        or set(_CAPTURE["pins"]) != set(_CAPTURE["sources"])
        or set(_CAPTURE["modules"]) != {PREFIX, QUALIFIER, COMPLETION}):
    raise ValueError("fixed owning loader source capture is required")
ENGINE_PINS = _CAPTURE["pins"]
P, Q, C = (_CAPTURE["modules"][name] for name in (PREFIX, QUALIFIER, COMPLETION))
LOADED_HELPER = _CAPTURE["sources"][HELPER][0]
LOADED_BOOTSTRAP = _CAPTURE["sources"][BOOTSTRAP][0]
PREFIX_BYTES = _CAPTURE["sources"][PREFIX][0]
if (Q.DRIVER_SOURCE_IDENTITY != "CAPTURED_EXECUTED_BUFFER"
        or Q.LOADED_DRIVER != _CAPTURE["sources"][QUALIFIER][0]
        or Q.LOADED_COMPILER != _CAPTURE["sources"][COMPILER][0]):
    raise ValueError("qualifier did not execute its fixed captured source")


def _current_engine():
    """Currentness is checked against actual executed captures, never renamed."""
    for directory, expected in _CAPTURE["ancestors"].items():
        fd = P.open_directory(Path(directory))
        try:
            info = os.fstat(fd)
            current = (str(info.st_dev), str(info.st_ino), info.st_mode, info.st_uid, info.st_gid)
            if current != expected:
                raise ValueError("loaded effect source ancestor changed")
        finally:
            os.close(fd)
    for name, (captured, expected_identity) in _CAPTURE["sources"].items():
        metadata, current = P.read_regular(ROOT / name, 1024**2)
        if (current != captured or tuple(metadata["identity"]) != expected_identity
                or digest(captured) != ENGINE_PINS[name]):
            raise ValueError("loaded effect source changed: " + name)


_current_engine()
BASE = P.bind_session(Q.VerifierTaskSession, Q.WG, ROOT, PREFIX_BYTES)


def snapshot_source(root, objects):
    """Complete literal subject read set; data changes remain real input."""
    root = Path(os.path.abspath(root))
    directories = {"."} | {str(p) for name in SOURCE_PATHS for p in Path(name).parents}
    state, stamps = dict(files={}, directories={}), {}
    def directory(name):
        fd = P.open_directory(root / name)
        try:
            info = os.fstat(fd)
            if os.listxattr(fd) or info.st_mode & 0o6000:
                raise ValueError("unsupported subject directory")
            return info
        finally:
            os.close(fd)
    for name in sorted(directories):
        info = directory(name)
        state["directories"][name] = stat.S_IMODE(info.st_mode)
        stamps[name] = P.identity(info)
    total = 0
    for name in SOURCE_PATHS:
        maximum = 256 * 1024 if name == "README.md" else 64 * 1024
        metadata, data = P.read_regular(root / name, maximum)
        total += len(data)
        if total > 512 * 1024 or metadata["mode"] not in (0o644, 0o755):
            raise ValueError("subject mode or total byte bound exceeded")
        key = digest(data)
        objects.setdefault(key, data)
        state["files"][name] = dict(mode=metadata["mode"], bytes=len(data), sha256=key)
        stamps[name] = metadata["identity"]
    for name in sorted(directories):
        if P.identity(directory(name)) != stamps[name]:
            raise ValueError("subject ancestor changed during acquisition")
    for name, pin in ((PROGRAM, PROGRAM_SHA256), (REGISTRY, REGISTRY_SHA256)):
        if state["files"][name]["sha256"] != pin:
            raise ValueError("unsupported original program or registry source")
    markers = [f"<!-- {end}: implementaudit-diagram:{Path(name).stem} -->".encode()
               for name in DIAGRAMS for end in ("BEGIN", "END")]
    readme = objects[state["files"]["README.md"]["sha256"]]
    readme.decode("utf-8", "strict")
    if any(readme.count(marker) != 1 for marker in markers):
        raise ValueError("bounded profile requires one of each README marker")
    for name in DIAGRAMS:
        data = objects[state["files"][name]["sha256"]]
        data.decode("utf-8", "strict")
        if b"\\" in data or any(marker in data for marker in markers):
            raise ValueError("unsupported replacement expansion in diagram data")
    return state, stamps


def select_checker(registry, environment):
    if digest(registry) != REGISTRY_SHA256:
        raise ValueError("unsupported original registry source")
    graph = Q.WG.compile_verifier_graph_v1(registry, Q.WG.verifier_registered_tests_v1(registry), environment)
    Q.WG.verifier_command_stream_v1(graph, registry)
    node = graph["nodes"][1]
    if (len(graph["nodes"]) != 117 or node["id"] != CHECK_NODE
            or node["source"] != "bash scripts/generate-readme-diagrams.sh --check\n"):
        raise ValueError("unsupported original node1 mapping")
    return graph, node


def decode_frame(raw):
    if len(raw) > MAX_FRAME or not raw.startswith(MAGIC):
        raise ValueError("missing or oversized producer frame")
    frame = Q.WG.decode_strict_json_bytes(raw[len(MAGIC):], "original producer frame")
    if (type(frame) is not dict or set(frame) != {"schema", "command", "program_sha256",
            "exit", "complete", "stdout", "stderr", "artifact"}
            or P.encode(frame) != raw[len(MAGIC):]
            or frame["schema"] != "implementaudit.readme-effect-frame.v1"
            or frame["command"] != ORIGINAL_PRODUCER_COMMAND
            or frame["program_sha256"] != PROGRAM_SHA256
            or type(frame["exit"]) is not int or frame["complete"] is not True):
        raise ValueError("malformed original producer frame")
    streams = {}
    for name in ("stdout", "stderr"):
        if type(frame[name]) is not str:
            raise ValueError("malformed producer stream")
        streams[name] = base64.b64decode(frame[name], validate=True)
        if len(streams[name]) > MAX_STREAM:
            raise ValueError("producer stream byte bound exceeded")
    artifact, data = frame["artifact"], None
    if frame["exit"] == 0:
        if (type(artifact) is not dict or set(artifact) != {"path", "mode", "bytes", "sha256", "data"}
                or artifact["path"] != "README.md" or artifact["mode"] != 0o600
                or type(artifact["bytes"]) is not int or not 0 <= artifact["bytes"] <= MAX_ARTIFACT
                or type(artifact["data"]) is not str):
            raise ValueError("missing or malformed generated output")
        data = base64.b64decode(artifact["data"], validate=True)
        if len(data) != artifact["bytes"] or digest(data) != artifact["sha256"]:
            raise ValueError("generated output bytes differ from frame")
    elif artifact is not None:
        raise ValueError("failed producer cannot issue an artifact")
    return frame, streams, data


def _node(name, **changes):
    value = dict(id=name, parent="README_ROOT", kind="TASK", state="OPEN", requires=[],
                 optional=[], reads=["path:source.json"], writes=[], acceptance=[], resources=[],
                 authority=[], effect="READ_ONLY", authorization="PERMITTED", independence="KNOWN",
                 resource_demand=1, rank=0, route_scopes=[], logical_delivery=None, future_consumer=None,
                 invalidators=[], independent_results=False, done_evidence=None,
                 context=dict(locality="GOVERNOR", governor_cost=1, child_cost=2, return_cost=1, useful_value=5))
    value.update(changes)
    return value


class EffectSession(BASE):
    """One live producer's fixed pair; durable files cannot restore acceptance."""
    SCOPE = PROFILE

    def __init__(self, source_root, output, *, max_age=3600):
        _current_engine()
        self._contract = None
        self._artifact = self._artifact_record = self._source_key = self._source_stamps = None
        self._projection_files = {}
        self._step_lock = threading.Lock()
        self._failed = self._closed = False
        super().__init__(source_root, output, max_age=max_age)

    def _engine_binding(self):
        _current_engine()
        result = super()._engine_binding()
        result.update(ENGINE_PINS)
        return result

    def _acquire(self):
        self._custody()
        objects = {}
        observer = self._observer()
        source, stamps = snapshot_source(self.source, objects)
        graph, checker = select_checker(objects[source["files"][REGISTRY]["sha256"]], self.environment)
        runtime = P.acquire_runtime(objects)
        for name, expected in self._engine.items():
            data = P.read_regular(ROOT / name)[1]
            if digest(data) != expected:
                raise ValueError("effect engine changed during acquisition")
            objects.setdefault(expected, data)
        current, final_stamps = snapshot_source(self.source, {})
        if source != current or stamps != final_stamps or observer != self._observer():
            raise ValueError("subject or observer changed during acquisition")
        self._custody()
        for data in objects.values():
            self._object(data)
        acquired = dict(schema="implementaudit.readme-effect-acquisition.v1", scope=PROFILE,
                        producer=self.producer, source_root=[str(self.source), *stamps["."][:2]],
                        source=source, registry_graph=graph["digest"], original_node=checker["id"],
                        engine=self._engine, runtime=runtime, observer=observer,
                        environment=self.environment, limits=self.LIMITS,
                        namespace="UNSHARE_ALL_NO_PROC_NO_GENERAL_DEV_NO_HOST_ROOT", authority="NONE")
        key = self._object(P.encode(acquired))
        return dict(acquired=acquired, key=key, state=source, stamps=stamps, objects=objects,
                    runtime=runtime, graph=graph, checker=checker, required_objects=sorted(set(objects) | {key}))

    def _write_projection(self, relative, data):
        path = self.output / relative
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._write(path, data)
        path.chmod(0o400)
        self._projection_files[relative] = data

    def _initialize_contract(self, start):
        self._source_key, self._source_stamps = start["key"], start["stamps"]
        future = lambda name: dict(node=name, condition="exact live producer-owned observation")
        nodes = [_node("README_ROOT", parent=None, kind="PLAN", requires=[FINAL], reads=[]),
                 _node(GENERATE, effect="PREPARATION", writes=["path:artifact/README.md"], future_consumer=future(OUTPUT)),
                 _node(OUTPUT, kind="JOIN", requires=[GENERATE], reads=[], future_consumer=future(FINAL)),
                 _node(CHECK, requires=[OUTPUT], reads=["path:source.json", "path:artifact/README.md"], future_consumer=future(FINAL)),
                 _node(FINAL, kind="JOIN", requires=[OUTPUT, CHECK], reads=[])]
        state = dict(schema="implementaudit.native-state.v1", campaign=PROFILE, root="README_ROOT",
                     original_scope="fixed portable private README producer to original node1 consumer",
                     nodes=[n["id"] for n in nodes], event=dict(id="readme-effect", kind="RETURN", subject=GENERATE),
                     context=dict(host_capacity=1, operator_ceiling=None, reserve=0, route_facts=[], outstanding_deliveries=[]))
        documents = {"STATE.md": state, "ROADMAP.md": dict(schema="implementaudit.native-roadmap.v1", phases=[])}
        for node in nodes:
            path = ("plans/" if node["kind"] == "PLAN" else "tasks/") + node["id"] + ".md"
            documents[path] = dict(schema="implementaudit.native-spec.v1", nodes=[node])
        for name, value in documents.items():
            self._write_projection("contract/" + name, b"```implementaudit-work-graph\n" + P.encode(value) + b"```\n")
        self._write_projection("inputs/source.json", P.encode(dict(acquisition=start["key"], source=start["state"])))
        self._contract = C.CompletionContract(self.output / "contract", self.output / "journal",
                                              input_root=self.output / "inputs",
                                              compiler_sha256=ENGINE_PINS[COMPILER])

    def _check_projection(self):
        for name, expected in self._projection_files.items():
            metadata, data = P.read_regular(self.output / name, MAX_FRAME)
            if data != expected or metadata["mode"] != 0o400:
                raise ValueError("owned contract or artifact projection changed")
        if self._artifact is not None:
            if P.encode(self._artifact) != self._artifact_record:
                raise ValueError("live artifact identity changed")
            metadata, data = P.read_regular(self.output / "objects" / self._artifact["sha256"], MAX_ARTIFACT)
            if metadata["mode"] != 0o400 or digest(data) != self._artifact["sha256"]:
                raise ValueError("retained artifact changed")

    def _current(self, start):
        self._check_projection()
        if self._source_key is not None and (start["key"] != self._source_key or start["stamps"] != self._source_stamps):
            raise ValueError("current source/runtime changed; prior artifact and successor refused")
        keys, refused = self._issued_keys()
        if refused:
            raise ValueError("issued effect evidence refused: " + str(refused))
        return keys

    def _execution(self, start, stage, directory):
        runtime_files = {name: (start["objects"][entry["sha256"]], entry["mode"])
                         for name, entry in start["runtime"]["files"].items()}
        files = dict(runtime_files)
        for name in SUBJECTS:
            data = start["objects"][start["state"]["files"][name]["sha256"]]
            if stage == CHECK and name == "README.md":
                if self._artifact is None:
                    raise ValueError("successor requires an owned generated artifact")
                data = P.read_regular(self.output / "objects" / self._artifact["sha256"], MAX_ARTIFACT)[1]
            files["/work/" + name] = (data, 0o444)
        files["/work/" + RUNNER] = (start["objects"][self._engine[RUNNER]], 0o555)
        if stage == GENERATE:
            files["/work/" + BOOTSTRAP] = (LOADED_BOOTSTRAP, 0o444)
            node = dict(id=GENERATE, source=PRODUCER_COMMAND, source_sha256=digest(PRODUCER_COMMAND.encode()))
        else:
            node = start["checker"]
        manifest, image_key = self._image(files, start["state"])
        acquired = dict(start, images={node["id"]: (files, manifest)},
                        acquired=dict(start["acquired"], inputs={node["id"]: dict(image_digest=image_key)}))
        receipt, retained = Q.VerifierTaskSession._execute(self, acquired, node, {"key": start["key"]}, directory)
        retained["required_objects"] = sorted(set(retained["required_objects"]) | set(start["required_objects"]) | {image_key})
        for name in retained["retained"]:
            (directory / name).chmod(0o400)
        after = self._acquire()
        self._same(start, after, directory, "after-execution")
        self._verify_new_result(retained)
        self._current(after)
        return receipt, retained

    def _admit_artifact(self, start, receipt, retained):
        frame, streams, data = decode_frame(retained["retained"]["stdout.log"])
        if (receipt["exit"] != 0 or not receipt["complete"] or frame["exit"] != 0
                or data is None or retained["retained"]["stderr.log"]):
            raise ValueError("producer did not return a complete successful artifact")
        key = self._object(data)
        artifact = dict(schema="implementaudit.live-readme-artifact.v1", producer=self.producer,
                        generation=self.generation, acquisition=start["key"], sha256=key, bytes=len(data),
                        original_mode=frame["artifact"]["mode"], consumer_mount_mode=0o444,
                        command=ORIGINAL_PRODUCER_COMMAND, program_sha256=PROGRAM_SHA256,
                        outer_receipt=digest(retained["retained"]["receipt.json"]),
                        frame_sha256=digest(retained["retained"]["stdout.log"]),
                        original_consumer_node=CHECK_NODE, authority="NONE")
        for name, raw in (("producer.stdout.log", streams["stdout"]), ("producer.stderr.log", streams["stderr"]),
                          ("producer.exit-code.txt", (str(frame["exit"]) + "\n").encode()),
                          ("artifact.json", P.encode(artifact))):
            path = retained["directory"] / name
            self._write(path, raw)
            path.chmod(0o400)
            retained["retained"][name] = raw
        retained["required_objects"] = sorted(set(retained["required_objects"]) | {key})
        self._write_projection("inputs/artifact/README.md", data)
        self._artifact, self._artifact_record = artifact, P.encode(artifact)
        self._verify_new_result(retained)

    def _result(self, frontier, name, receipt, retained):
        return dict(schema="implementaudit.work-result.v1", node=name,
                    dispatch_id=frontier["dispatch_id"], graph_digest=frontier["graph_digest"],
                    input_digest=frontier["inputs"][name], status="PASS", terminal=True, exit_code=0,
                    evidence_digest=digest(P.encode(dict(receipt=digest(retained["retained"]["receipt.json"]),
                        artifact=self._artifact, original_node=receipt["node"]))),
                    independence_key=self.producer + "-" + name, scope=[name])

    def step(self):
        """Perform only the next action selected by the shared compiler."""
        if not self._step_lock.acquire(blocking=False):
            raise ValueError("concurrent effect consumption is unsupported")
        try:
            if self._closed or self._failed:
                raise ValueError("closed, failed or interrupted effect session cannot resume")
            self._custody()
            if self.generation >= 64:
                raise ValueError("finite live effect observation bound exceeded")
            self.generation += 1
            directory = self.output / ("generation-%06d" % self.generation)
            directory.mkdir(mode=0o700)
            start = self._acquire()
            self._current(start)
            if self._contract is None:
                self._initialize_contract(start)
            frontier = self._contract.frontier()
            self._write(directory / "frontier.json", frontier)
            self._write(directory / "acquisition.json", start["acquired"])
            selected = frontier["selected"]
            action = selected[0] if len(selected) == 1 else None
            if selected and action not in (GENERATE, OUTPUT, CHECK, FINAL):
                raise ValueError("unexpected shared compiler selection")
            if action in (GENERATE, CHECK):
                try:
                    receipt, retained = self._execution(start, action, directory / "execution")
                    if receipt["exit"] != 0 or not receipt["complete"]:
                        raise ValueError("actual task failed or was incomplete; no completion accepted")
                    if action == GENERATE:
                        self._admit_artifact(start, receipt, retained)
                    self._contract.accept(frontier, [self._result(frontier, action, receipt, retained)],
                                          OUTPUT if action == GENERATE else FINAL,
                                          expected_old=self._contract.history_digest)
                    self._issued[action] = retained
                except BaseException:
                    self._failed = True
                    raise
            elif action in (OUTPUT, FINAL):
                verdict = self._contract.join(action, expected_old=self._contract.history_digest)
                if verdict["status"] != "SATISFIED_AT_DECLARED_RESULT_CONTRACT":
                    raise ValueError("required JOIN is not satisfied")
                self._write(directory / "join.json", verdict)
            elif frontier["states"].get(FINAL) != "DONE":
                raise ValueError("shared compiler retained a source or completion hold")
            after = self._acquire()
            self._same(start, after, directory, "after-consumption")
            self._current(after)
            view = self._contract.frontier()
            result = dict(schema="implementaudit.readme-effect-consumption.v1", scope=PROFILE,
                          producer=self.producer, generation=self.generation, action=action,
                          disposition="REUSED" if action is None else "EXECUTED" if action in (GENERATE, CHECK) else "JOINED",
                          status="SATISFIED_AT_PORTABLE_EFFECT_CONTRACT" if view["states"].get(FINAL) == "DONE" else "PENDING",
                          selected=view["selected"], states=view["states"], dispatch_count=self.dispatch_count,
                          artifact_sha256=None if self._artifact is None else self._artifact["sha256"],
                          history_digest=self._contract.history_digest,
                          original_registry_nodes=117, original_consumer=CHECK_NODE,
                          evidence_scope="LIVE_PORTABLE_FIXED_PHYSICAL_EFFECT_CONTRACT",
                          canonical_acceptance="UNQUALIFIED", native_dispatch_authorized=False, authority="NONE")
            self._write(directory / "result.json", result)
            return copy.deepcopy(result)
        finally:
            self._step_lock.release()

    def run(self):
        """Drain this fixed compiler frontier without caller-supplied decisions."""
        while True:
            result = self.step()
            if result["status"] == "SATISFIED_AT_PORTABLE_EFFECT_CONTRACT":
                return result

    def artifact_bytes(self):
        self._custody()
        self._check_projection()
        if self._artifact is None:
            raise ValueError("no live producer artifact")
        return P.read_regular(self.output / "objects" / self._artifact["sha256"], MAX_ARTIFACT)[1]

    def close(self):
        if self._contract is not None:
            self._contract.close()
        self._closed = True
