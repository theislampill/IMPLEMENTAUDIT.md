#!/usr/bin/env python3
"""Repository-only finite acquisition of explicit original verifier nodes.

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
TOPOLOGY_PROFILE = "CONTROLLED_TASK_INTERNAL_SKILL_TOPOLOGY_V1"
CAPABILITY_PROFILE = "CONTROLLED_TASK_CAPABILITY_LEDGER_V1"
ISSUES_PROFILE = "CONTROLLED_TASK_ISSUES_DEFERRED_V1"
TERMINAL_PROFILE = "CONTROLLED_TASK_NO_TERMINAL_CAP_V1"
BACKGROUND_PROFILE = "CONTROLLED_TASK_BACKGROUND_CHAIN_V1"
LIFECYCLE_PROFILE = "CONTROLLED_TASK_PLAN_LIFECYCLE_V1"
# Output-allocation upper bound only. The pinned original checker still decides
# acceptance. Ignore its negation exemptions and overcount every possible
# strike/ladder line; a small bound never constitutes a successful scan.
_TERMINAL_BOUND_TERMS = (
    "no subsequent phases execute", "recovery ladder", "failure ladder",
    "up to 3 rounds", "maximum 3 rounds", "max 2", "max-2", "two revisions",
    "max 3", "max-3", "max retry", "max retries", "retry cap", "retry limit",
    "revision limit", "round limit", "capped round", "capped rounds", "try cap",
    "attempt cap", "failure_probe", "failure_escalate", "failure_handoff")
_RECURSIVE_BOUNDS = dict(file_bytes=1024 * 1024, total_bytes=8 * 1024**2,
                         entries=2048, depth=40, path_bytes=2048)
# Inspected exact GNU paste ELF: PT_INTERP is this loader and its only
# DT_NEEDED member is libc.so.6; libc's loader dependency is already captured.
# Unknown tool/runtime bytes refuse; no host-path executable is dispatched.
_TOPOLOGY_RUNTIME_PINS = {
    "/usr/bin/paste": "82077c51bf5add756668fef163556942f01083100d378e3bf860466a83fd6dcb",
    "/lib/x86_64-linux-gnu/libc.so.6": "511f825ee075610ac9c0f7f91e2c13de2000d0f7b859f6461137e809a0a009d0",
    "/lib64/ld-linux-x86-64.so.2": "6222a16be7f2d458d6870efe6e715fc0c8d45766fb79cf7dcc3125538d703e28",
}
_TOPOLOGY_NAMESPACE_BOUNDS = dict(entries=128, name_bytes=32 * 1024)
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
LIFECYCLE_INPUTS = (
    "skills/implementaudit/SKILL.md", "skills/implementaudit/templates/THINKING.md",
    "skills/implementaudit/templates/ROADMAP.md", "skills/implementaudit/templates/STATE.md",
    "skills/implementaudit/templates/PROTOCOL.md", "skills/implementaudit/templates/phase-goal.txt",
    "skills/implementaudit/scripts/claim-run.sh", "skills/implementaudit/references/planning-depth.md",
    "skills/implementaudit/references/goal-format.md", "skills/implementaudit/references/phase-design.md",
    "skills/implementaudit/references/transcript-contract.md",
    "skills/implementaudit/references/audit-category-matrix.md",
    "skills/implementaudit/references/plan-lifecycle.md", "docs/diagrams/execution-spine.mmd",
    "docs/portal/pages/planning-and-phases.html", "fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md",
    "fixtures/audit-object-routing/plan-lifecycle.md",
)
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
    TOPOLOGY_PROFILE: dict(label="internal-skill-topology", index=77, program="tests/internal-skill-topology.test.sh",
        programs={"tests/internal-skill-topology.test.sh": "6d4a1f2e06f85096fb1680529997ef70ffdf17947c2c24534429d984fa16c97c"},
        data=("package/implementaudit-package.json",),
        bounds=dict(file_bytes=64 * 1024, total_bytes=256 * 1024, files=3),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="PINNED_ORIGINAL_PROGRAM_PACKAGE_JSON_AND_COMPLETE_DEPTH_TWO_TYPED_SKILLS_NAMESPACE_NO_CONTENT_READS_OR_GIT"),
    CAPABILITY_PROFILE: dict(label="capability-ledger", index=69, program="tests/capability-ledger.test.sh",
        programs={"tests/capability-ledger.test.sh": "14e7ce6f591c9dfe1bafdcdb955093e36ebf61a10ec3fb72552849fa6eab8010"},
        data=("README.md", "AGENTS.md"),
        bounds=dict(file_bytes=1024 * 1024, total_bytes=8 * 1024**2, files=4),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="PINNED_ORIGINAL_PROGRAM_README_AGENTS_AND_COMPLETE_RECURSIVE_SKILLS_BYTES_NO_GIT",
        recursive=dict(roots=("skills",), optional=False, bounds=_RECURSIVE_BOUNDS,
            required_members=("skills/implementaudit/SKILL.md", "skills/implementaudit/templates/PROTOCOL.md",
                "skills/implementaudit/templates/STATE.md", "skills/implementaudit/references/lean-operating-discipline.md")),
        temporary_sizes=(), temporary_directories=0),
    ISSUES_PROFILE: dict(label="issues-deferred", index=72, program="tests/issues-deferred-gate.test.sh",
        programs={"tests/issues-deferred-gate.test.sh": "a1b1fee495d90a6c8d3c9def8fa27d6c06bd4fa362ef311659e7170904466487"},
        data=("README.md",),
        bounds=dict(file_bytes=1024 * 1024, total_bytes=8 * 1024**2, files=3),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="PINNED_ORIGINAL_PROGRAM_README_AND_THREE_COMPLETE_RECURSIVE_SCAN_ROOTS_NO_GIT",
        recursive=dict(roots=("skills", "docs/portal", "fixtures/audit-object-routing"), optional=False, bounds=_RECURSIVE_BOUNDS,
            required_members=("skills/implementaudit/references/plan-lifecycle.md", "skills/implementaudit/templates/PROTOCOL.md",
                "skills/implementaudit/templates/phase-goal.txt", "fixtures/audit-object-routing/issues-deferred.md"))),
    TERMINAL_PROFILE: dict(label="no-terminal-cap", index=97, program="tests/no-terminal-cap.test.sh",
        programs={
            "tests/no-terminal-cap.test.sh": "95628b0498d8868ec8988620a7022b0b979247cb760d89bd6e5bcbed339e3755",
            "scripts/check-no-terminal-cap.sh": "0868f60de64c71d3d1139931bbaaf6b0927574769c0415f5b9884a5fc03e65b9"},
        data=(), bounds=dict(file_bytes=1024 * 1024, total_bytes=8 * 1024**2, files=3),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="TWO_PINNED_PROGRAMS_FOUR_COMPLETE_OPTIONAL_RECURSIVE_ROOTS_AND_TWO_OPTIONAL_FILES_NO_READ_OMISSIONS",
        recursive=dict(roots=("skills", "docs/diagrams", "docs/portal", "fixtures"), optional=True,
            optional_files=("README.md", "AGENTS.md"), bounds=_RECURSIVE_BOUNDS),
        # 26 literal fixture files + nine wrapper here-doc spools +25 checker
        # spools. Each is smaller than8KiB; include all simultaneously and every
        # mkdir ancestor even though actual sequential Bash may use pipes.
        temporary_sizes=(8192,) * 60, temporary_directories=98),
    BACKGROUND_PROFILE: dict(label="background-chain", index=40, program="tests/background-chain-contract.test.sh",
        programs={"tests/background-chain-contract.test.sh": "d42aeb580876e310b7a988291159c7c33c8bf2e53d19a746bcff07244b3bd2ea"},
        data=("skills/implementaudit/templates/PROTOCOL.md", "skills/implementaudit/SKILL.md",
              "eval/fixtures/B5-wait-contract/fixture.json"),
        bounds=dict(file_bytes=128 * 1024, total_bytes=256 * 1024, files=5),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="PINNED_BACKGROUND_PROGRAM_THREE_LITERAL_INPUTS_EIGHT_PRIVATE_FIXTURES_ORIGINAL_PIPEFAIL_NO_BACKGROUND_LAUNCH",
        # Eight launch records, eight maximum status records, two empty markers,
        # original/scrubbed diagnostics concurrently, and one possible Bash
        # spool for the fixed Python here-document. No source-visible effect.
        temporary_sizes=(4,) * 8 + (15, 15, 40, 8, 45, 61, 15, 55, 0, 0, 84, 56, 840),
        temporary_directories=9),
    LIFECYCLE_PROFILE: dict(label="plan-lifecycle", index=71, program="tests/audit-object-plan-lifecycle.test.sh",
        programs={
            "tests/audit-object-plan-lifecycle.test.sh": "9fb536fdb0966dfc6f8764bf0e482d794afc42ef151ce0a3918a2acc7ac03b3e",
            "scripts/check-planner-stages.sh": "78d3735a5af7b83f76bafd48feac2af23868e6a8c668f7c579367f627c0a5825"},
        data=LIFECYCLE_INPUTS, bounds=dict(file_bytes=128 * 1024, total_bytes=512 * 1024, files=20),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="TWO_PINNED_PROGRAMS_SEVENTEEN_LITERAL_DATA_OR_PRESENCE_INPUTS_ORIGINAL_PIPEFAIL_CLAIM_RUN_NEVER_EXECUTED",
        temporary_sizes=(), temporary_directories=0),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def contract_for(profile):
    if type(profile) is not str or profile not in (PROFILE, ANDON_PROFILE, REGISTRY_PROFILE, MARKER_PROFILE,
                                                     COMMIT_PROFILE, AGENTS_PROFILE, ESCALATION_PROFILE, TOPOLOGY_PROFILE,
                                                     CAPABILITY_PROFILE, ISSUES_PROFILE, TERMINAL_PROFILE,
                                                     BACKGROUND_PROFILE, LIFECYCLE_PROFILE):
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


def snapshot_skill_namespace(prefix, root):
    """Closed depth-two find namespace; no document contents are observed.

    Hold every ancestor and observed directory until the closing census. All
    names and ordinary types count, including dot and nonmatching members.
    Unknown metadata/types refuse instead of becoming an absent placeholder.
    """
    if ".." in Path(root).parts:
        raise ValueError("skill namespace parent traversal is unqualified")
    root = Path(os.path.abspath(root))
    if len(root.parts) > 129 or len(str(root).encode("utf-8", "strict")) > 4096:
        raise ValueError("skill namespace root path bound exceeded")
    chain, opened, members, censuses, stamps = [], {}, {}, {}, {}
    count = name_bytes = 0
    def ancestor(info):
        return prefix.identity(info)[:3] + [info.st_uid, info.st_gid]
    def census(fd):
        names = []
        with os.scandir(fd) as entries:
            for entry in entries:
                prefix.safe_name(entry.name)
                names.append(entry.name)
                if len(names) > _TOPOLOGY_NAMESPACE_BOUNDS["entries"]:
                    raise ValueError("skill namespace entry bound exceeded")
        return sorted(names)
    def visit(fd, relative, depth):
        nonlocal count, name_bytes
        info = os.fstat(fd)
        if stat.S_IMODE(info.st_mode) != 0o755 or os.listxattr(fd):
            raise ValueError("skill namespace directory mode or metadata is unsupported")
        stamps[relative] = prefix.identity(info)
        opened[relative] = fd
        if depth == 2:
            return
        names = census(fd)
        censuses[relative] = names
        for component in names:
            name = relative + "/" + component
            count += 1
            name_bytes += len(name.encode("utf-8", "strict")) + 1
            if count > _TOPOLOGY_NAMESPACE_BOUNDS["entries"] or name_bytes > _TOPOLOGY_NAMESPACE_BOUNDS["name_bytes"]:
                raise ValueError("skill namespace entry/name byte bound exceeded")
            before = os.stat(component, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISDIR(before.st_mode):
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                chain.append((child, fd, component, ancestor(before)))
                if prefix.identity(os.fstat(child)) != prefix.identity(before):
                    raise ValueError("skill namespace directory changed during acquisition")
                members[name] = "DIRECTORY"
                visit(child, name, depth + 1)
            elif stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) in (0o644, 0o755):
                child = os.open(component, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
                try:
                    if prefix.identity(os.fstat(child)) != prefix.identity(before) or os.listxattr(child):
                        raise ValueError("skill namespace file changed or metadata is unsupported")
                    members[name] = "FILE"
                    stamps[name] = prefix.identity(before)
                finally:
                    os.close(child)
            else:
                raise ValueError("skill namespace requires ordinary single-link files and directories")
            if prefix.identity(os.stat(component, dir_fd=fd, follow_symlinks=False)) != prefix.identity(before):
                raise ValueError("skill namespace member changed during acquisition")
    try:
        fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        chain.append((fd, None, None, ancestor(os.fstat(fd))))
        for component in (*root.parts[1:], "skills"):
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            chain.append((child, fd, component, ancestor(os.fstat(child))))
            fd = child
        visit(fd, "skills", 0)
        for name, expected in censuses.items():
            if census(opened[name]) != expected:
                raise ValueError("skill namespace population changed during acquisition")
        for name, expected in stamps.items():
            if name == "skills":
                current = os.fstat(opened[name])
            else:
                current = os.stat(Path(name).name, dir_fd=opened[str(Path(name).parent)], follow_symlinks=False)
            if prefix.identity(current) != expected:
                raise ValueError("skill namespace member changed during complete acquisition")
        for descriptor, parent, component, expected in chain:
            if ancestor(os.fstat(descriptor)) != expected or (parent is not None and
                    ancestor(os.stat(component, dir_fd=parent, follow_symlinks=False)) != expected):
                raise ValueError("skill namespace ancestor changed during acquisition")
        projection = dict(path="skills", min_depth=2, max_depth=2, entries=members,
            observation="COMPLETE_DEPTH_TWO_NAMES_AND_TYPES_NO_CONTENT_READS", bounds=dict(_TOPOLOGY_NAMESPACE_BOUNDS))
        currentness = dict(ancestors=[row[3] for row in chain], census=censuses, members=stamps)
        return projection, currentness
    finally:
        for descriptor, _, _, _ in reversed(chain):
            os.close(descriptor)


def snapshot_recursive_inputs(prefix, root, objects, contract):
    """One complete bounded byte/namespace acquirer for fixed catalog roots.

    The established tree reader acquires every ordinary byte and name. Held
    physical ancestors, explicit absent probes and a complete closing tree read
    prevent caught reader errors or omitted members from becoming clean scans.
    This function never supplies a command, result or acceptance decision.
    """
    if ".." in Path(root).parts:
        raise ValueError("recursive source parent traversal is unqualified")
    root = Path(os.path.abspath(root))
    if len(root.parts) > 129 or len(str(root).encode("utf-8", "strict")) > 4096:
        raise ValueError("recursive source root path bound exceeded")
    bounds = contract["bounds"]
    chain, directories, directory_stamps, guards = [], {}, {}, []
    files, modes, stamps, probes, trees = {}, {}, {}, {}, {}
    def node(info):
        return prefix.identity(info)[:3] + [info.st_uid, info.st_gid]
    def opened_directory(parent, component, relative, before):
        fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        chain.append((fd, parent, component, node(before)))
        if prefix.identity(os.fstat(fd)) != prefix.identity(before):
            raise ValueError("recursive source ancestor changed during opening")
        if stat.S_IMODE(before.st_mode) != 0o755 or os.listxattr(fd):
            raise ValueError("recursive source directory mode or metadata is unsupported")
        directories[relative] = fd
        directory_stamps[relative] = prefix.identity(before)
        modes[relative] = 0o755
        return fd
    def probe(name, kind, optional):
        prefix.safe_name(name)
        parent, relative = directories["."], ""
        parts = Path(name).parts
        for index, component in enumerate(parts):
            relative = component if not relative else relative + "/" + component
            final = index == len(parts) - 1
            try:
                before = os.stat(component, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                if not optional:
                    raise ValueError("required recursive input is absent: " + name) from None
                guards.append((parent, component, None))
                probes[name] = dict(kind="MISSING", missing_at=relative)
                return
            if not final or kind == "DIRECTORY":
                if not stat.S_ISDIR(before.st_mode):
                    raise ValueError("recursive source directory has an unsupported type")
                if relative in directories:
                    child = directories[relative]
                    if prefix.identity(os.fstat(child)) != prefix.identity(before):
                        raise ValueError("recursive source ancestor changed during acquisition")
                else:
                    child = opened_directory(parent, component, relative, before)
                if not final:
                    parent = child
                    continue
                state, observed = prefix.snapshot_tree(root / name, objects, bounds)
                if prefix.identity(os.fstat(child)) != observed["."]:
                    raise ValueError("recursive source root changed during acquisition")
                trees[name] = (state, observed)
                for path, value in state["files"].items():
                    if value["mode"] not in (0o644, 0o755):
                        raise ValueError("recursive source file mode is unsupported")
                    files[name + "/" + path] = value
                for path, value in state["directories"].items():
                    if value != 0o755:
                        raise ValueError("recursive source directory mode is unsupported")
                    modes[name if path == "." else name + "/" + path] = value
                stamps[name] = observed
                probes[name] = dict(kind="DIRECTORY")
            else:
                metadata, data = prefix.read_regular(root / name, bounds["file_bytes"])
                if metadata["identity"] != prefix.identity(before) or metadata["mode"] not in (0o644, 0o755):
                    raise ValueError("recursive optional file changed or mode is unsupported")
                key = digest(data)
                objects.setdefault(key, data)
                files[name] = dict(mode=metadata["mode"], bytes=len(data), sha256=key)
                stamps[name] = metadata["identity"]
                probes[name] = dict(kind="FILE")
            guards.append((parent, component, prefix.identity(before)))
    try:
        fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        chain.append((fd, None, None, node(os.fstat(fd))))
        for component in root.parts[1:]:
            before = os.stat(component, dir_fd=fd, follow_symlinks=False)
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            chain.append((child, fd, component, node(before)))
            if prefix.identity(os.fstat(child)) != prefix.identity(before):
                raise ValueError("recursive source ancestor changed during opening")
            fd = child
        directories["."] = fd
        directory_stamps["."] = prefix.identity(os.fstat(fd))
        modes["."] = stat.S_IMODE(os.fstat(fd).st_mode)
        for name in contract["roots"]:
            probe(name, "DIRECTORY", contract["optional"])
        for name in contract.get("optional_files", ()):
            probe(name, "FILE", True)
        if any(name not in files for name in contract.get("required_members", ())):
            raise ValueError("required original positive operand is absent from complete recursive source")
        if len(files) + len(modes) > bounds["entries"] or sum(v["bytes"] for v in files.values()) > bounds["total_bytes"]:
            raise ValueError("combined recursive source entry/byte bound exceeded")
        if any(len(name.encode("utf-8")) > bounds["path_bytes"] for name in (*files, *modes)):
            raise ValueError("recursive source image path bound exceeded")
        # Reobserve the complete namespace/bytes, not only the initially found
        # names. This closes omissions/additions and changes in earlier siblings.
        for name, expected in trees.items():
            if prefix.snapshot_tree(root / name, {}, bounds) != expected:
                raise ValueError("recursive source changed during complete acquisition")
        for parent, component, expected in guards:
            try:
                observed = prefix.identity(os.stat(component, dir_fd=parent, follow_symlinks=False))
            except FileNotFoundError:
                observed = None
            if observed != expected:
                raise ValueError("recursive source presence or identity changed during acquisition")
        for name, expected in directory_stamps.items():
            if prefix.identity(os.fstat(directories[name])) != expected:
                raise ValueError("recursive source ancestor changed during acquisition")
        for descriptor, parent, component, expected in chain:
            if node(os.fstat(descriptor)) != expected or (parent is not None and
                    node(os.stat(component, dir_fd=parent, follow_symlinks=False)) != expected):
                raise ValueError("recursive source physical ancestor changed during acquisition")
        projection = dict(roots=list(contract["roots"]), probes=probes,
            observation="COMPLETE_RECURSIVE_ORDINARY_BYTES_NAMES_TYPES_AND_EMPTY_DIRECTORIES", bounds=dict(bounds))
        currentness = dict(ancestors=[row[3] for row in chain], directories=directory_stamps, members=stamps)
        return dict(files=files, directories=modes), dict(projection=projection, currentness=currentness)
    finally:
        for descriptor, _, _, _ in reversed(chain):
            os.close(descriptor)


def recursive_output_bounds(state, objects, contract, *, profile):
    """Conservative output sizes from complete actual acquired input bytes."""
    names = sorted(set(state["files"]) - {REGISTRY, *contract["programs"]})
    grep_bytes = diagnostics = terminal_bytes = terminal_messages = 0
    for name in names:
        raw = objects[state["files"][name]["sha256"]]
        path_bytes = len(name.encode("utf-8"))
        lines = raw.count(b"\n") + int(bool(raw) and not raw.endswith(b"\n"))
        # Every line may match, with filename, both separators, the longest
        # possible decimal line number and an extra newline. Downstream grep
        # filters cannot increase this stream. Include binary diagnostics too.
        grep_bytes += len(raw) + lines * (path_bytes + len(str(max(lines, 1))) + 3)
        diagnostics += path_bytes + 128
        if profile == TERMINAL_PROFILE:
            try:
                text = raw.decode("utf-8", "strict")
            except UnicodeDecodeError:
                # The original checker intentionally skips undecodable bytes.
                # They remain fully captured/retained; acquisition never skips.
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                lowered = line.lower()
                possible = sum(term in lowered for term in _TERMINAL_BOUND_TERMS)
                possible += int("strike" in lowered) + int("ladder" in lowered)
                # Bound UTF-8 and an ASCII stderr backslash fallback. The
                # constant margin exceeds every fixed original message suffix.
                width = max(path_bytes, len(name.encode("ascii", "backslashreplace"))) + len(str(lineno)) + 132
                terminal_messages += possible
                terminal_bytes += possible * width
    return dict(read_files=len(names), read_bytes=sum(state["files"][name]["bytes"] for name in names),
        all_lines_grep_report_bytes=grep_bytes, binary_diagnostic_bytes=diagnostics,
        terminal_possible_messages=terminal_messages, terminal_diagnostic_bytes=terminal_bytes,
        basis="OUTPUT_ALLOCATION_UPPER_BOUND_NOT_AN_ACCEPTANCE_DECISION")


def snapshot_source(prefix, root, objects, *, profile=PROFILE, registry_snapshot=None):
    """Acquire the literal closure and the profile's complete typed namespace.

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
    if profile == TOPOLOGY_PROFILE:
        membership, currentness = snapshot_skill_namespace(prefix, root)
        state["skill_namespace"] = dict(projection=membership, currentness=currentness)
        stamps["skill_namespace"] = currentness
    if "recursive" in contract:
        recursive, currentness = snapshot_recursive_inputs(prefix, root, objects, contract["recursive"])
        state["files"].update(recursive["files"])
        state["directories"].update(recursive["directories"])
        state["recursive_inputs"] = currentness
        stamps["recursive_inputs"] = currentness
        if sum(value["bytes"] for value in state["files"].values()) > bounds["total_bytes"]:
            raise ValueError("complete finite recursive byte bound exceeded")
        state["recursive_inputs"]["resources"] = recursive_output_bounds(state, objects, contract, profile=profile)
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
    extra = {}
    if profile == ISSUES_PROFILE:
        bound = state["recursive_inputs"]["resources"]
        content = bound["all_lines_grep_report_bytes"]
        copies, files, directories, allocated = 0, 1, 0, rounded(content)
        extra = dict(largest_file_bytes=content, max_stdout_bytes=512,
            max_stderr_bytes=content + bound["binary_diagnostic_bytes"] + 512)
    elif profile == TOPOLOGY_PROFILE:
        entries = state["skill_namespace"]["projection"]["entries"]
        matching = [name for name, kind in entries.items()
                    if kind == "FILE" and name.count("/") == 2 and name.endswith("/SKILL.md")]
        stream = sum(len(name.encode("utf-8")) + 1 for name in matching)
        # At most one sort run per input record; allow both all old and all new
        # runs simultaneously. Each run fits one 64 KiB granule under the name
        # bound. Include the original fixed Python here-document's possible
        # anonymous spool, even when Bash uses a pipe. No semantic file writes.
        copies, files, directories = 0, 2 * len(matching) + 1, 0
        content, allocated = 2 * stream + 2048, files * granule
    elif profile in (REGISTRY_PROFILE, MARKER_PROFILE, COMMIT_PROFILE, AGENTS_PROFILE, ESCALATION_PROFILE,
                     CAPABILITY_PROFILE, TERMINAL_PROFILE, BACKGROUND_PROFILE, LIFECYCLE_PROFILE):
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
    if profile == CAPABILITY_PROFILE:
        extra = dict(largest_file_bytes=0, max_stdout_bytes=512,
            max_stderr_bytes=state["recursive_inputs"]["resources"]["binary_diagnostic_bytes"] + 512)
    elif profile == TERMINAL_PROFILE:
        extra = dict(largest_file_bytes=8192, max_stdout_bytes=1024,
            max_stderr_bytes=state["recursive_inputs"]["resources"]["terminal_diagnostic_bytes"] + 8192)
    overhead = (files + directories) * granule
    result = dict(copies=copies, files=files, directories=directories, content_bytes=content,
        allocation_granule=granule, observed_page_bytes=page, overhead_bytes=overhead,
        required_bytes=allocated + overhead, basis="PINNED_PROGRAM_LITERAL_TEMPORARY_WRITE_SET")
    result.update(extra)
    if "recursive" in contract:
        result["basis"] = "COMPLETE_ACQUIRED_INPUT_OUTPUT_BOUND_AND_FIXED_PRIVATE_WRITE_SET"
    return result


def require_resource_capacity(reservation, limits):
    if reservation["required_bytes"] > limits["scratch_bytes"]:
        raise ValueError("finite-leaf temporary write set exceeds scratch capacity")
    stream = min(limits["file_bytes"], limits.get("stream_bytes", limits["file_bytes"]))
    for field, limit in (("largest_file_bytes", limits["file_bytes"]),
                         ("max_stdout_bytes", stream), ("max_stderr_bytes", stream)):
        if field in reservation and reservation[field] > limit:
            raise ValueError("finite-leaf " + field + " exceeds original file/stream capacity")


def _capture_topology_runtime(prefix, runtime, objects):
    """Extend the existing captured runtime with one inspected fixed ELF."""
    dependencies = ("/lib/x86_64-linux-gnu/libc.so.6", "/lib64/ld-linux-x86-64.so.2")
    if any(name not in runtime["files"] or name not in runtime["observations"] for name in dependencies):
        raise ValueError("unsupported paste loader/libc closure")
    path = Path("/usr/bin/paste")
    metadata, raw = prefix.read_regular(path, prefix.RUNTIME_BOUNDS["file_bytes"])
    key = digest(raw)
    if key != _TOPOLOGY_RUNTIME_PINS[str(path)] or metadata["mode"] != 0o755:
        raise ValueError("unsupported captured paste executable")
    for name, pin in _TOPOLOGY_RUNTIME_PINS.items():
        if name == str(path):
            continue
        observed = runtime["observations"].get(name)
        entry = runtime["files"].get(name)
        if observed is None or entry is None or entry["sha256"] != pin or digest(objects.get(pin, b"")) != pin:
            raise ValueError("unsupported paste loader/libc closure")
        original = Path(name)
        resolved = original.resolve(strict=True)
        if str(resolved) != observed["resolved"]:
            raise ValueError("paste runtime closure alias changed")
        current, captured = prefix.read_regular(resolved, prefix.RUNTIME_BOUNDS["file_bytes"], single_link=False)
        if current["identity"] != observed["identity"] or digest(captured) != pin or original.resolve(strict=True) != resolved:
            raise ValueError("paste runtime closure changed during acquisition")
    again, current = prefix.read_regular(path, prefix.RUNTIME_BOUNDS["file_bytes"])
    if metadata != again or raw != current:
        raise ValueError("paste executable changed during acquisition")
    objects.setdefault(key, raw)
    runtime["files"][str(path)] = dict(mode=0o555, bytes=len(raw), sha256=key)
    runtime["observations"][str(path)] = dict(resolved=str(path), mode=metadata["mode"],
        bytes=len(raw), sha256=key, identity=metadata["identity"])
    runtime["topology_tool_closure"] = dict(_TOPOLOGY_RUNTIME_PINS)


def finite_runtime(prefix, objects, *, profile=PROFILE):
    contract_for(profile)
    runtime = prefix.acquire_runtime(objects)
    if profile == TOPOLOGY_PROFILE:
        _capture_topology_runtime(prefix, runtime, objects)
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
            require_resource_capacity(temporary, self.LIMITS)
            runtime = finite_runtime(prefix, objects, profile=profile)
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
            if profile == TOPOLOGY_PROFILE:
                membership = source["skill_namespace"]["projection"]
                for name, kind in membership["entries"].items():
                    if kind == "FILE":
                        files["/work/" + name] = (b"", 0o444)
                subject["directory:skills"] = membership
            manifest, image_key = self._image(files, subject,
                membership if profile == REGISTRY_PROFILE else None)
            if profile == TOPOLOGY_PROFILE:
                # Preserve actual empty directories without introducing a file
                # the original find would observe. The existing executor alone
                # creates these manifest directories and sealed ordinary files.
                manifest["directories"] = sorted(set(manifest["directories"]) | {"/work/skills"} |
                    {"/work/" + name for name, kind in membership["entries"].items() if kind == "DIRECTORY"})
                manifest["directory_membership"] = membership
                manifest["source_projection"] = "READ_BYTES_AND_COMPLETE_DEPTH_TWO_TYPED_NAME_PLACEHOLDERS"
                image_key = self._object(self._encode(manifest))
            if "recursive" in contract:
                image_bytes = sum(len(data) for data, _ in files.values())
                descriptors = len(files) + 2 + 64  # existing launch descriptors plus observer margin
                if descriptors > self.LIMITS["descriptors"] or image_bytes > self.LIMITS["address_bytes"] // 4:
                    raise compiler.WorkGraphError("complete recursive image exceeds finite descriptor/memory reservation")
                temporary["image_reservation"] = dict(descriptors=descriptors, observer_descriptor_margin=64,
                    mounted_bytes=image_bytes, address_reservation_bytes=self.LIMITS["address_bytes"] // 4)
                manifest["directories"] = sorted(set(manifest["directories"]) |
                    {"/work/" + name for name in source["directories"] if name != "."})
                manifest["directory_membership"] = source["recursive_inputs"]["projection"]
                manifest["source_projection"] = "COMPLETE_RECURSIVE_READ_BYTES_AND_EXPLICIT_OPTIONAL_PRESENCE"
                image_key = self._object(self._encode(manifest))
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
