#!/usr/bin/env python3
"""Repository-only finite acquisition of seven explicit original verifier nodes.

The compiler remains the node/source owner. Execution uses the qualifier's
existing isolated-leaf launcher; this helper adds no executor or native authority.
"""
import copy
import hashlib
import importlib.util
import os
from pathlib import Path
import stat


PROFILE = "CONTROLLED_TASK_AUDIT_SPEC_V1"
ANDON_PROFILE = "CONTROLLED_TASK_ANDON_CLASS_V1"
REGISTRY_PROFILE = "CONTROLLED_TASK_REGISTRY_WRAPPER_V1"
MARKER_PROFILE = "CONTROLLED_TASK_MARKER_ORDER_V1"
COMMIT_PROFILE = "CONTROLLED_TASK_COMMIT_MESSAGE_V1"
AGENTS_PROFILE = "CONTROLLED_TASK_AGENTS_BOOTSTRAP_V1"
ESCALATION_PROFILE = "CONTROLLED_TASK_ANDON_ESCALATION_V1"
NODE = "COMMAND:tests/audit-spec.test.sh:0"
REGISTRY = "scripts/verify-package.sh"
REGISTRY_SHA256 = "77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698"
PREFIX_HELPER = "scripts/qualify-work-graph-prefix.py"
PREFIX_HELPER_SHA256 = "86f4e02dbf7b25ee3a4dab2fb90ef4dd3e21cfe350e8ce38470e36c4f4733016"
HELPER = "scripts/qualify-work-graph-finite-leaf.py"
RUNNER = "scripts/run-work-graph-verifier.sh"
PROGRAM_PINS = {
    "tests/audit-spec.test.sh": "eef97a07f531e002a752264848d38697a636041b574385828a9b364fe20bcee3",
    "skills/implementaudit/scripts/validate-audit-spec.sh": "f0b88b4b2d2745eb2df1f339b5daaa1bf7d20a148b4ecccb3de7d9c0de0074d7",
}
FIXTURES = tuple("fixtures/audit-spec/" + name for name in (
    "valid-mixed.md", "invalid-missing-owner.md", "invalid-missing-rollback.md",
    "invalid-missing-evidence.md", "invalid-missing-generated-plan.md",
    "invalid-missing-release-boundary.md"))
SOURCE_PATHS = (REGISTRY, *PROGRAM_PINS, *FIXTURES)
SOURCE_BOUNDS = dict(file_bytes=64 * 1024, total_bytes=256 * 1024, files=9)
COMMIT_FIXTURES = tuple("fixtures/commit-message/" + name for name in (
    'andon-not-applicable-linkage-FAIL.md',
    'bare-count-not-anchor-FAIL.md',
    'behavior-change-empty-body-FAIL.md',
    'behavior-change-three-line-body-PASS.md',
    'breaking-body-no-anchor-FAIL.md',
    'breaking-subject-empty-body-FAIL.md',
    'codename-unexpanded-PASS.md',
    'decision-record-PASS.md',
    'decision-record-empty-body-FAIL.md',
    'docs-typo-slim-PASS.md',
    'external-url-not-anchor-FAIL.md',
    'finding-close-no-anchor-FAIL.md',
    'hunk-anchor-PASS.md',
    'landed-placeholder-not-anchor-FAIL.md',
    'ledger-linked-no-linkage-FAIL.md',
    'linkage-andon-PASS.md',
    'linkage-ledger-row-PASS.md',
    'mechanical-regen-slim-PASS.md',
    'mechanical-with-long-body-PASS.md',
    'named-anchor-PASS.md',
    'occurrences-anchor-PASS.md',
    'occurrences-ratio-not-anchor-FAIL.md',
    'ordinary-hex-word-not-anchor-FAIL.md',
    'placeholder-anchor-FAIL.md',
    'real-window-best-body-PASS.md',
    'reviewer-slots-unscored-PASS.md',
    'test-placeholder-not-anchor-FAIL.md',
    'unparseable-subject-slim-FAIL.md',
))
ESCALATION_FIXTURES = tuple("fixtures/andon-escalation/" + name for name in (
    'same-class-recurrence.md',
    'first-occurrence-misscoped-validator.md',
    'cross-class-shared-invariant.md',
    'correct-by-luck-perturbation.md',
    'reasoned-rejection.md',
))
_CONTRACTS = {
    PROFILE: dict(label="audit-spec", index=57, program="tests/audit-spec.test.sh",
        programs=PROGRAM_PINS, data=FIXTURES, bounds=SOURCE_BOUNDS,
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="EIGHT_LITERAL_READ_FILES_REGISTRY_SELECTION_ONLY_NO_GIT_OR_ENUMERATION"),
    ANDON_PROFILE: dict(label="andon-class", index=25, program="tests/andon-class-contract.test.sh",
        programs={"tests/andon-class-contract.test.sh": "0f23ef7bbe233c33d7c2a7417e25daeccc82475a2a95a85f9bd1b4301a3cb3eb"},
        data=("skills/implementaudit/SKILL.md", "skills/implementaudit/templates/PROTOCOL.md",
              "skills/implementaudit/references/transcript-contract.md"),
        bounds=dict(file_bytes=256 * 1024, total_bytes=1024 * 1024, files=5),
        source_modes="PRESERVE_READ_ONLY_MOUNT",
        projection="FOUR_LITERAL_READ_FILES_REGISTRY_SELECTION_ONLY_NO_GIT_OR_ENUMERATION"),
    REGISTRY_PROFILE: dict(label="registry-wrapper", index=113, program="tests/validation-registry.test.sh",
        programs={
            "tests/validation-registry.test.sh": "ac9459ec5485ae550251924f0e2365dec0ff86859e2b74fca44bebdcd752250e",
            "scripts/check-validation-registry.sh": "c7c6b0f26111c44c4caaf5e1ffc20979e48cc15ca83600f3fea16514e9d02fee"},
        data=(".github/workflows/validate.yml",),
        bounds=dict(file_bytes=64 * 1024, total_bytes=256 * 1024, files=4),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="FOUR_LITERAL_READ_FILES_AND_COMPLETE_IMMEDIATE_TYPED_TEST_NAMES_NO_GIT",
        # Maximum size of each of the fourteen literal private output files,
        # over all overwrites in the pinned wrapper's three fixed trees.
        temporary_sizes=(25, 25, 25, 84, 68, 25, 25, 25, 92, 36, 25, 25, 27, 68),
        temporary_directories=16),
    MARKER_PROFILE: dict(label="marker-order", index=45, program="tests/marker-order.test.sh",
        programs={
            "tests/marker-order.test.sh": "1736083571f60936b1fbddf3c038a75c4b866432f7fe242161e0939b13182691",
            "scripts/check-marker-order.sh": "9764979aa3e1324e217828684e45ef67f40f14427537502a62ce3d66b6872b31"},
        data=(), bounds=dict(file_bytes=64 * 1024, total_bytes=256 * 1024, files=3),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="TWO_LITERAL_PROGRAMS_REGISTRY_SELECTION_ONLY_GENERATED_TRANSCRIPTS_NO_GIT_OR_ENUMERATION",
        # Exact bytes of the thirteen literal here-documents in the wrapper.
        temporary_sizes=(172, 159, 82, 59, 69, 41, 27, 259, 95, 119, 84, 30, 51),
        temporary_directories=1),
    COMMIT_PROFILE: dict(label="commit-message", index=56, program="tests/commit-message-contract.test.sh",
        programs={
            "tests/commit-message-contract.test.sh": "1ae951cc68bac704d5771e5d91bece6fab0f8793b1f0b79956f403ef03e27c7c",
            "skills/implementaudit/scripts/repo-state.sh": "b2220d0627c5e66d106bb3ce8a9daafb5310b87643b9281d63db5a5aa886df3b"},
        data=COMMIT_FIXTURES, bounds=dict(file_bytes=64 * 1024, total_bytes=512 * 1024, files=31),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="TWO_PINNED_PROGRAMS_FIXED_COMMIT_MESSAGE_BRANCH_AND_28_LITERAL_FIXTURES_NO_GIT_OR_ENUMERATION",
        # Reserve every possible anonymous Bash here-document spool even when
        # this kernel uses a pipe; all28 fixed calls are conservatively counted.
        temporary_sizes=(3092,) * 28, temporary_directories=0),
    AGENTS_PROFILE: dict(label="agents-bootstrap", index=59, program="tests/agents-bootstrap-budget.test.sh",
        programs={
            "tests/agents-bootstrap-budget.test.sh": "82d5413a6a67943cfb13d1ed70068ccacbea5c090491b5fac991697a870cf051",
            "scripts/check-agents-bootstrap-budget.sh": "be6cb923382263f35b87a0b65f42fc57fd438fd091dc4fa2baf3533d0eb4e078"},
        data=("AGENTS.md", "docs/audits/RETENTION.md"),
        bounds=dict(file_bytes=64 * 1024, total_bytes=256 * 1024, files=5),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="TWO_PINNED_PROGRAMS_AGENT_BYTES_AND_CONSERVATIVELY_CAPTURED_REGULAR_RETENTION_PROBE_NO_GIT",
        # Three generated documents, three diagnostics, and every possible
        # Bash here-document spool (three in the wrapper, four checker calls).
        temporary_sizes=(5412, 788, 1034, 65536, 65536, 65536, 124, 788, 1034, 3073, 3073, 3073, 3073), temporary_directories=1),
    ESCALATION_PROFILE: dict(label="andon-escalation", index=39, program="tests/andon-escalation-judgment.test.sh",
        programs={"tests/andon-escalation-judgment.test.sh": "48f3b279836a60f03bfc573203f47d1cdd323dbbbbe68047e158d398d1ef2f84"},
        data=("skills/implementaudit/templates/PROTOCOL.md", *ESCALATION_FIXTURES),
        bounds=dict(file_bytes=256 * 1024, total_bytes=1024 * 1024, files=8),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="PINNED_PROGRAM_PROTOCOL_AND_FIVE_LITERAL_FIXTURES_ORIGINAL_PIPEFAIL_NO_GIT_OR_ENUMERATION",
        temporary_sizes=(), temporary_directories=0),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def contract_for(profile):
    if type(profile) is not str or profile not in (PROFILE, ANDON_PROFILE, REGISTRY_PROFILE, MARKER_PROFILE,
                                                     COMMIT_PROFILE, AGENTS_PROFILE, ESCALATION_PROFILE):
        raise ValueError("unsupported finite-leaf profile")
    return copy.deepcopy(_CONTRACTS[profile])


def source_paths(profile=PROFILE):
    contract = contract_for(profile)
    return (REGISTRY, *contract["programs"], *contract["data"])


def select_node(compiler, registry, environment, *, profile=PROFILE):
    contract = contract_for(profile)
    if digest(registry) != REGISTRY_SHA256:
        raise ValueError("unsupported finite-leaf registry source")
    graph = compiler.compile_verifier_graph_v1(registry, compiler.verifier_registered_tests_v1(registry), environment)
    compiler.verifier_command_stream_v1(graph, registry)
    nodes = graph["nodes"]
    node_id = "COMMAND:" + contract["program"] + ":0"
    if len(nodes) != 117 or nodes[contract["index"]]["id"] != node_id or nodes[contract["index"]]["source"] != "bash " + contract["program"] + "\n":
        raise ValueError("unsupported finite-leaf registry mapping")
    node = nodes[contract["index"]]
    return graph, dict(profile=profile, graph_digest=graph["digest"], nodes=[node_id],
        omitted_nodes=[n["id"] for n in nodes if n["id"] != node_id],
        source_sha256=node["source_sha256"], source_bytes=len(node["source"].encode()),
        composition="ONE_INDEPENDENT_ORIGINAL_NODE_NO_PREDECESSOR_SUBSTITUTION"), node


def snapshot_source(prefix, root, objects, *, profile=PROFILE, registry_snapshot=None):
    """Acquire the literal closure and the one known name-only namespace.

    The live factory supplies the existing captured qualifier's registry owner;
    a receiving request cannot supply this internal acquisition dependency.
    """
    contract = contract_for(profile)
    paths = source_paths(profile)
    bounds = contract["bounds"]
    root = Path(os.path.abspath(root))
    directories = {"."} | {str(p) for name in paths for p in Path(name).parents}
    state, stamps = dict(files={}, directories={}), {}
    def directory(name):
        fd = prefix.open_directory(root / name)
        try:
            info = os.fstat(fd)
            if os.listxattr(fd) or info.st_mode & 0o6000:
                raise ValueError("unsupported finite-leaf source directory")
            return info
        finally:
            os.close(fd)
    for name in sorted(directories):
        info = directory(name)
        state["directories"][name] = stat.S_IMODE(info.st_mode)
        stamps[name] = prefix.identity(info)
    total = 0
    for name in paths:
        metadata, data = prefix.read_regular(root / name, bounds["file_bytes"])
        total += len(data)
        if total > bounds["total_bytes"] or metadata["mode"] not in (0o644, 0o755):
            raise ValueError("unsupported finite-leaf source mode or byte bound")
        key = digest(data)
        objects.setdefault(key, data)
        state["files"][name] = dict(mode=metadata["mode"], bytes=len(data), sha256=key)
        stamps[name] = metadata["identity"]
    if profile == REGISTRY_PROFILE:
        if registry_snapshot is None:
            raise ValueError("registry-wrapper requires the captured membership owner")
        membership, currentness = registry_snapshot(root)
        state["registry_membership"] = dict(projection=membership, currentness=currentness)
        stamps["registry_membership"] = currentness
    for name in sorted(directories):
        if prefix.identity(directory(name)) != stamps[name]:
            raise ValueError("finite-leaf source ancestor changed during acquisition")
    for name, pin in dict(contract["programs"], **{REGISTRY: REGISTRY_SHA256}).items():
        if state["files"][name]["sha256"] != pin:
            raise ValueError("unsupported finite-leaf executable or registry source")
    return state, stamps


def temporary_requirements(state, *, profile=PROFILE):
    """Conservative allocation bounds for the explicit temporary-write sets."""
    contract = contract_for(profile)
    granule = 64 * 1024
    page = os.sysconf("SC_PAGE_SIZE")
    if type(page) is not int or page <= 0 or page > granule or granule % page:
        raise ValueError("unsupported temporary allocation granule")
    sizes = [state["files"][name]["bytes"] for name in contract["data"]]
    rounded = lambda size: ((size + granule - 1) // granule) * granule
    if profile in (REGISTRY_PROFILE, MARKER_PROFILE, COMMIT_PROFILE, AGENTS_PROFILE, ESCALATION_PROFILE):
        sizes = contract["temporary_sizes"]
        copies, files, directories = 0, len(sizes), contract["temporary_directories"]
        content, allocated = sum(sizes), sum(map(rounded, sizes))
    elif profile == ANDON_PROFILE:
        # Three retained trees, each with three files and five directories;
        # the single enclosing mktemp directory is the sixteenth directory.
        copies, files, directories = 3, 9, 16
        content, allocated = 3 * sum(sizes), 3 * sum(map(rounded, sizes))
    else:
        copies, files, directories = 0, 1, 0
        content, allocated = max(sizes), rounded(max(sizes))
    overhead = (files + directories) * granule
    return dict(copies=copies, files=files, directories=directories, content_bytes=content,
        allocation_granule=granule, observed_page_bytes=page, overhead_bytes=overhead,
        required_bytes=allocated + overhead, basis="PINNED_PROGRAM_LITERAL_TEMPORARY_WRITE_SET")


def finite_runtime(prefix, objects):
    runtime = prefix.acquire_runtime(objects)
    # The existing isolated-leaf bootstrap necessarily execs this wrapper before
    # the original shell. Fix its descendants' umask without changing the
    # observer process or introducing another executor.
    wrapper = b'#!/usr/bin/bash\numask 022\nexec /usr/bin/python3.12 -P -S -B "$@"\n'
    key = digest(wrapper)
    objects.setdefault(key, wrapper)
    for name in ("/usr/bin/python", "/usr/bin/python3"):
        runtime["files"][name] = dict(mode=0o555, bytes=len(wrapper), sha256=key)
    runtime["totals"] = prefix.runtime_budget(runtime["files"], prefix.RUNTIME_BOUNDS)
    runtime["startup"] += "_UMASK_022_BEFORE_ISOLATED_LEAF_BOOTSTRAP"
    runtime["umask"] = 0o022
    return runtime


def bind_session(base, compiler, engine_root, loaded_helper, *, profile=PROFILE):
    """Bind a fixed acquirer to existing custody, image and isolated-leaf owners."""
    contract = contract_for(profile)
    label = contract["label"]
    path = engine_root / PREFIX_HELPER
    data = base._regular(path)[1]
    if digest(data) != PREFIX_HELPER_SHA256:
        raise compiler.WorkGraphError("unsupported captured prefix helper source")
    spec = importlib.util.spec_from_file_location("audit_spec_prefix", path)
    prefix = importlib.util.module_from_spec(spec)
    exec(compile(data, str(path), "exec"), prefix.__dict__)
    parent = prefix.bind_session(base, compiler, engine_root, data)
    # Reuse the exact established namespace owner from the captured qualifier;
    # do not fork the census algorithm or accept a receiving callback policy.
    registry_snapshot = (base._acquire.__globals__["_registry_membership_snapshot_v1"]
                         if profile == REGISTRY_PROFILE else None)

    class FiniteVerifierSession(parent):
        SCOPE = profile

        def __init__(self, source_root, output, *, max_age=3600):
            # Preserve the namespace owner's raw-path refusal before inherited
            # convenience resolution can erase a parent-traversal component.
            if any(".." in Path(path).parts for path in (source_root, output)):
                raise compiler.WorkGraphError("finite-leaf parent traversal is unqualified")
            super().__init__(source_root, output, max_age=max_age)

        def _engine_binding(self):
            result = super()._engine_binding()
            current = prefix.read_regular(engine_root / HELPER)[1]
            if current != loaded_helper:
                raise compiler.WorkGraphError("loaded finite-leaf helper differs from current source")
            result[HELPER] = digest(current)
            return result

        def _acquire(self):
            self._custody()
            objects = {}
            observer = self._observer()
            source, stamps = snapshot_source(prefix, self.source, objects,
                profile=profile, registry_snapshot=registry_snapshot)
            registry = objects[source["files"][REGISTRY]["sha256"]]
            graph, scope, node = select_node(compiler, registry, self.environment, profile=profile)
            temporary = temporary_requirements(source, profile=profile)
            if temporary["required_bytes"] > self.LIMITS["scratch_bytes"]:
                raise compiler.WorkGraphError("finite-leaf temporary write set exceeds scratch capacity")
            runtime = finite_runtime(prefix, objects)
            engine_objects = {}
            for name, expected in self._engine.items():
                captured = prefix.read_regular(engine_root / name)[1]
                if digest(captured) != expected:
                    raise compiler.WorkGraphError("finite-leaf engine source changed during acquisition")
                objects.setdefault(expected, captured)
                engine_objects[name] = expected
            current, final_stamps = snapshot_source(prefix, self.source, {},
                profile=profile, registry_snapshot=registry_snapshot)
            if source != current or stamps != final_stamps or observer != self._observer():
                raise compiler.WorkGraphError("finite-leaf source/runtime observer changed during acquisition")
            self._custody()
            for captured in objects.values():
                self._object(captured)
            runtime_files = {name: (objects[entry["sha256"]], entry["mode"]) for name, entry in runtime["files"].items()}
            _, runtime_key = self._image(runtime_files, {})
            files = dict(runtime_files)
            subject = {name: value for name, value in source["files"].items()
                       if name != REGISTRY or profile == REGISTRY_PROFILE}
            files.update({"/work/" + name: (objects[value["sha256"]],
                value["mode"] if contract["source_modes"] == "PRESERVE_READ_ONLY_MOUNT" else 0o444)
                for name, value in subject.items()})
            files["/work/" + RUNNER] = (objects[self._engine[RUNNER]], 0o555)
            membership = None
            if profile == REGISTRY_PROFILE:
                membership = source["registry_membership"]["projection"]
                for name in membership["entries"]:
                    # The original wrapper is executable input, not a type-only
                    # placeholder. The checker never reads other test contents.
                    files.setdefault("/work/tests/" + name, (b"", 0o444))
                subject["directory:tests"] = membership
            manifest, image_key = self._image(files, subject, membership)
            source_key = self._object(prefix.encode(source))
            graph_key = self._object(self._encode(graph))
            runtime_observation_key = self._object(prefix.encode(runtime))
            acquired = dict(schema="implementaudit.verifier-" + label + "-acquisition.v1", scope=profile,
                group=scope, producer=self.producer, source_root=[str(self.source), *stamps["."][:2]],
                source=source_key, graph=graph_key, engine=self._engine, engine_objects=engine_objects,
                runtime=runtime_key, runtime_observations=runtime_observation_key,
                inputs={node["id"]: dict(program_sha256=contract["programs"][contract["program"]], image_digest=image_key)},
                environment=self.environment, observer=observer, limits=self.LIMITS, source_bounds=contract["bounds"],
                source_projection=contract["projection"], temporary_reservation=temporary, startup_umask=0o022,
                directory_modes="NORMALIZED_0755_READ_ONLY", source_files=contract["source_modes"],
                namespace="UNSHARE_ALL_NO_PROC_NO_GENERAL_DEV_NO_HOST_ROOT", stdin="EMPTY",
                mutable_resources=["private bounded /tmp", "/dev/null", "observer stdout/stderr"],
                effects="PRIVATE_WRITES_DISCARDED_NO_PREDECESSOR_OR_SUCCESSOR_SUBSTITUTION", authority="NONE")
            key = self._object(prefix.encode(acquired))
            required = set(objects) | {source_key, graph_key, runtime_key, runtime_observation_key,
                image_key, manifest["seccomp_sha256"], key}
            return dict(acquired=acquired, key=key, state=source, stamps=stamps, graph=graph, node=node,
                images={node["id"]: (files, manifest)}, required_objects=sorted(required))

        def _execute_group(self, acquired, directory):
            # This is the unchanged qualifier launcher, not another executor.
            receipt, retained = base._execute(self, acquired, acquired["node"], {"key": acquired["key"]}, directory)
            retained["required_objects"] = sorted(set(retained["required_objects"]) | set(acquired["required_objects"]))
            for name in retained["retained"]:
                (directory / name).chmod(0o400)
            return receipt, retained

        def _consume(self):
            self._custody()
            if self.generation >= 64:
                raise compiler.WorkGraphError("finite-leaf consumption capacity exhausted")
            self.generation += 1
            directory = self.output / ("generation-%06d" % self.generation)
            directory.mkdir(mode=0o700)
            keys, refused = self._issued_keys()
            if refused:
                self._write(directory / "refusal.json", dict(reason="ISSUED_EVIDENCE_INVALID", details=refused))
                raise compiler.WorkGraphError("prior finite-leaf evidence refused: " + str(refused))
            if self._attempted and not self._issued:
                raise compiler.WorkGraphError("failed or interrupted finite-leaf execution has no reusable result")
            start = self._acquire()
            self._write(directory / "acquisition.json", start["acquired"])
            self._write(directory / "mapping.json", start["graph"])
            if profile in keys:
                if keys[profile] != start["key"]:
                    self._write(directory / "refusal.json", dict(reason="CURRENT_INPUTS_CHANGED",
                        issued_key=keys[profile], current_key=start["key"]))
                    raise compiler.WorkGraphError("current finite-leaf input changed; prior receipt refused")
                retained = self._issued[profile]
                receipt = compiler.decode_strict_json_bytes(retained["retained"]["receipt.json"], "issued finite-leaf result")
                disposition = "REUSED"
            else:
                self._attempted = True
                receipt, retained = self._execute_group(start, directory / "execution")
                disposition = "EXECUTED"
            after = self._acquire()
            self._same(start, after, directory, "during-consumption")
            if disposition == "REUSED" and self._issued_keys()[0].get(profile) != start["key"]:
                raise compiler.WorkGraphError("finite-leaf issued evidence changed during consumption")
            if disposition == "EXECUTED":
                self._verify_new_result(retained)
            if receipt["exit"] == 0 and receipt["complete"]:
                self._issued[profile] = retained
            result = dict(schema="implementaudit.verifier-" + label + "-consumption.v1", scope=profile,
                producer=self.producer, generation=self.generation, key=start["key"], group=start["acquired"]["group"],
                disposition=disposition, receipt_digest=digest(retained["retained"]["receipt.json"]),
                evidence_directory=str(retained["directory"]), exit=receipt["exit"], complete=receipt["complete"],
                dispatch_count=self.dispatch_count, canonical_acceptance="UNQUALIFIED", authority="NONE")
            self._write(directory / "result.json", result)
            return copy.deepcopy(result)

    return FiniteVerifierSession
