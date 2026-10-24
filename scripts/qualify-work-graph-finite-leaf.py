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
PLAN_QUALITY_PROFILE = "CONTROLLED_TASK_PLAN_QUALITY_V1"
AUTHORIZATION_PROFILE = "CONTROLLED_TASK_AUTHORIZATION_BINDING_V1"
READ_ONLY_PROFILE = "CONTROLLED_TASK_READ_ONLY_PLANS_V1"
SAFEGUARD_PROFILE = "CONTROLLED_TASK_SAFEGUARD_RESTORATION_V1"
ROUTING_PROFILE = "CONTROLLED_TASK_ROUTING_V1"
AUDIT_OBJECT_PROFILE = "CONTROLLED_TASK_AUDIT_OBJECT_ROUTING_V1"
INSTALLED_PROFILE = "CONTROLLED_TASK_INSTALLED_PAYLOAD_V1"
PLANNER_COPY_PROFILE = "CONTROLLED_TASK_PLANNER_COPY_V1"
FANOUT_PROFILE = "CONTROLLED_TASK_FANOUT_COVERAGE_V1"
SKILL_LAYOUT_PROFILE = "CONTROLLED_TASK_SKILL_LAYOUT_V1"
NATIVE_INTEGRATION_PROFILE = "CONTROLLED_TASK_NATIVE_INTEGRATION_V1"
# Necessary anchors only: these deliberately overcount original diagnostics,
# including exempt examples. They bound allocation; the original decides truth.
_NATIVE_FORBIDDEN_BOUND_ANCHORS = (b"Foreign", b"foreign", b"Category", b"STATUS", b"non-native")
_NATIVE_HYGIENE_BOUND_ANCHORS = ("hunter2", "akia", "ghp_", "sk-", "password", "apikey", "api_key", "api-key")
RETENTION_PROFILE = "CONTROLLED_TASK_AUDIT_RETENTION_V1"
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
# Inspected Perl5.38.2 ELF and its complete DT_NEEDED/PT_INTERP closure. The
# three fixed original expressions import no module in the owned host probe.
# The finite image deliberately lacks the observed optional paths below;
# successful behavior in that image is a separate receiving gate, not a fact
# inferred from these pins or from a host-side copied-fixture positive.
_PLANNER_RUNTIME_PINS = {
    "/usr/bin/perl": "38d70f54fd18d614e9e6cc35c960b45f54e7b991894b8308e704ae9953c86ce4",
    "/lib/x86_64-linux-gnu/libm.so.6": "f06f2ce1f1833df5f41cf13b6447ff07bea993ad9b27297d3428c2f70ab3f0e7",
    "/lib/x86_64-linux-gnu/libc.so.6": "511f825ee075610ac9c0f7f91e2c13de2000d0f7b859f6461137e809a0a009d0",
    "/lib/x86_64-linux-gnu/libcrypt.so.1": "1502636e3be8232c9cf801dfb533694aea985d449904f3e1295db26d7b348946",
    "/lib64/ld-linux-x86-64.so.2": "6222a16be7f2d458d6870efe6e715fc0c8d45766fb79cf7dcc3125538d703e28",
}
_PLANNER_ABSENT_PROBES = (
    "/dev/urandom", "/proc/self/exe", "/etc/ld.so.preload", "/etc/ld.so.cache",
    "/usr/lib/x86_64-linux-gnu/perl-base/5.38.2/x86_64-linux-gnu-thread-multi",
    "/usr/lib/x86_64-linux-gnu/perl-base/5.38.2",
    "/usr/lib/x86_64-linux-gnu/perl-base/x86_64-linux-gnu-thread-multi",
    "/usr/local/lib/site_perl/5.38.2/x86_64-linux-gnu-thread-multi",
    "/usr/local/lib/site_perl/5.38.2",
    "/usr/local/lib/site_perl/x86_64-linux-gnu-thread-multi",
)
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
PLAN_QUALITY_COMMON_INPUTS = (
    "fixtures/read-only-plans/valid-handoff-plan.md", "fixtures/e2e-mini-audit-loop/phase-1.md",
    "skills/implementaudit/templates/phase-goal.txt",
    "fixtures/phase-design/negative-paths-without-symbols.md",
    "skills/implementaudit/references/plan-lifecycle.md",
    "skills/implementaudit/references/repo-state-comparison.md",
    "skills/implementaudit/templates/read-only-plan.md",
    "fixtures/child-agents/read-only-contract-auditor.md",
)
PLAN_QUALITY_INPUTS = (*PLAN_QUALITY_COMMON_INPUTS,
    "fixtures/read-only-plans/read-only-zero-mutation.status",
    "fixtures/read-only-plans/read-only-audit-ledger.status",
    "fixtures/read-only-plans/negative-read-only-source-mutation.status",
    "fixtures/secret-hygiene/negative-plan-reproduces-fake-secret.md",
    "fixtures/secret-hygiene/negative-child-prompt-missing-security-rules.md",
)
AUTHORIZATION_INPUTS = (
    "skills/implementaudit/templates/PROTOCOL.md", "skills/implementaudit/templates/STATE.md",
    *("fixtures/authorization-binding/" + name for name in (
        "intake-state-deny.md", "intake-state-grant.md", "authorization-record.txt",
        "authorization-record-missing-source.txt", "auth.txt", "invocation-match.txt", "invocation-drift.txt")),
)
READ_ONLY_INPUTS = tuple(dict.fromkeys((*PLAN_QUALITY_INPUTS,
    "docs/audits/INDEX.md", "docs/audits/RETENTION.md", "skills/implementaudit/SKILL.md",
    "skills/implementaudit/references/sidecars.md", "skills/implementaudit/references/transcript-contract.md",
    "skills/implementaudit/templates/final-report.md",
    # These programs are read as data by parity; none is executed by this node.
    "scripts/check-dogfood-bootstrap-contract.sh", "scripts/dogfood-evidence-broker.py",
    "scripts/check-installed-payload-self-contained.sh", "scripts/check-skill-bootstrap-budget.sh",
    "scripts/build-source-evidence-pack.sh", "tests/source-evidence-pack-runnable.test.sh",
    "tests/source-evidence-pack.test.sh",
    "fixtures/secret-hygiene/repo-ignore-previous-instructions.md",
    "fixtures/secret-hygiene/repo-print-env.md", "fixtures/secret-hygiene/repo-fake-secret.txt",
    *("fixtures/dogfood-bootstrap/" + name for name in (
        "positive/baseline-first-transcript.jsonl",
        "negative/installed-readback-before-baseline-transcript.jsonl",
        "negative/chunking-readback-before-baseline-transcript.jsonl",
        "negative/real-home-readback-before-temp-home-transcript.jsonl",
        "typed-event.schema.json", "typed/ordinary-control-activation.jsonl",
        "typed/self-dogfood-corroboration.jsonl", "typed/self-dogfood-contradiction.jsonl")),
)))
ROUTING_SCAN_INPUTS = (
    "README.md", "AGENTS.md", "skills/implementaudit/references/routing.md",
    "skills/implementaudit/references/planning-depth.md",
    "skills/implementaudit/references/goal-format.md",
    "skills/implementaudit/references/phase-design.md", "skills/implementaudit/SKILL.md",
)
ROUTING_INPUTS = (*ROUTING_SCAN_INPUTS,
    "skills/implementaudit/references/audit-category-matrix.md",
    "skills/implementaudit/references/plan-lifecycle.md",
    *("fixtures/routing/" + name + "/EXPECTED.md" for name in (
        "greenfield-goal-synthesis", "greenfield-full-category-intake", "greenfield-batched-questions",
        "brownfield-audit-closure", "brownfield-zero-question-recon", "brownfield-one-question-true-gap",
        "brownfield-two-question-true-gap", "mixed-greenfield-in-brownfield")),
    "fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md",
    "fixtures/routing/brownfield-audit-closure/INVALID-MUTATION-FIRST.md",
)
# Exact reads of the original routing checker. The lean checker additionally
# observes complete skills membership and the literal presence operands below.
AUDIT_ROUTING_FIXTURES = tuple("fixtures/routing/" + name for name in (
    "greenfield-goal-synthesis/EXPECTED.md", "brownfield-audit-closure/EXPECTED.md",
    "mixed-greenfield-in-brownfield/EXPECTED.md", "greenfield-full-category-intake/EXPECTED.md",
    "greenfield-batched-questions/EXPECTED.md", "brownfield-zero-question-recon/EXPECTED.md",
    "brownfield-one-question-true-gap/EXPECTED.md", "brownfield-two-question-true-gap/EXPECTED.md",
    "greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md",
    "brownfield-audit-closure/INVALID-MUTATION-FIRST.md"))
AUDIT_ROUTING_READS = ("README.md", "AGENTS.md", *AUDIT_ROUTING_FIXTURES,
    "skills/implementaudit/SKILL.md", *("skills/implementaudit/references/" + name for name in (
        "routing.md", "audit-category-matrix.md", "plan-lifecycle.md", "planning-depth.md",
        "goal-format.md", "phase-design.md")))
AUDIT_OBJECT_INPUTS = ("README.md", "AGENTS.md", *AUDIT_ROUTING_FIXTURES,
    *("fixtures/lean/" + name for name in (
        "brownfield-dmaic-release-repair.md", "brownfield-dmaic-stale-docs.md",
        "greenfield-dmadv-new-runtime-helper.md", "mixed-dmaic-dmadv-package-boundary.md",
        "sidecar-graphify-absent-markdown-fallback.md", "sidecar-graphify-dmaic-analyze.md",
        "sidecar-activegraph-dmaic-custody.md")),
    # Presence operands only: captured as data and never executed by this node.
    "fixtures/semantic-preservation/cases.json", "fixtures/semantic-preservation/evaluate.py",
    "fixtures/semantic-preservation/test-cases.sh")
FANOUT_COPY_INPUTS = (
    "skills/implementaudit/references/child-agents.md",
    "skills/implementaudit/references/audit-category-matrix.md",
    "skills/implementaudit/templates/THINKING.md",
)
FANOUT_INPUTS = (*FANOUT_COPY_INPUTS,
    # The default child prompt belongs to the complete recursive tree below.
    # Both plan defaults and every unconditional plan-quality read remain here.
    *(name for name in PLAN_QUALITY_COMMON_INPUTS if not name.startswith("fixtures/child-agents/")),
)
FANOUT_REQUIRED_MEMBERS = tuple("fixtures/child-agents/" + name for name in (
    "read-only-contract-auditor.md", "adversarial-behavioral-auditor.md",
    "broad-scope-four-lanes.md", "low-concurrency-serialized-lanes.md",
    "exploratory-discrimination-cases.md", "negative-coverage-table-only.md",
    "negative-silent-lane-drop.md", "negative-generic-single-pass.md",
    "negative-child-prompt-missing-fanout-contract.md",
))
SKILL_LAYOUT_ROOTS = ("skills", ".claude-plugin", ".github", "scripts", "tests", "docs/portal")
SKILL_LAYOUT_REQUIRED = (
    *("skills/" + name + "/SKILL.md" for name in
      ("implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon")),
    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "scripts/build-release-asset.sh",
)
_SKILL_LAYOUT_GIT_ARGS = ("ls-files", "--error-unmatch", "skills/SKILL.md")
_CONTRACTS = {
    NATIVE_INTEGRATION_PROFILE: dict(label="native-integration", index=74, program="tests/native-integration.test.sh",
        programs={
            "tests/native-integration.test.sh": "f9743dc224dafc38cc34e7b09acadb8bfff9ea900307db0a81f59ec8736201c8",
            "scripts/check-native-integration.sh": "63dc104b9d242de2118327d99cdf01d7e2bed95c17f2e8c1fb52a89831740e36"},
        data=(), bounds=dict(file_bytes=128 * 1024, total_bytes=8 * 1024**2, files=3),
        source_modes="PRESERVE_READ_ONLY_MOUNT",
        projection="TWO_PINNED_ORIGINAL_PROGRAMS_COMPLETE_SKILLS_ALL_FIXTURES_PORTAL_AND_OPTIONAL_ROOT_FILES_NO_NATIVE_HOST",
        recursive=dict(roots=("skills", "fixtures", "docs/portal"), optional=True,
            optional_files=("README.md", "AGENTS.md"), bounds=_RECURSIVE_BOUNDS,
            required_members=(
                "skills/implementaudit/references/audit-category-matrix.md",
                "skills/implementaudit/references/audit-playbook.md",
                "skills/implementaudit/templates/THINKING.md",
                "skills/implementaudit/templates/phase-goal.txt",
                "skills/implementaudit/templates/PROTOCOL.md",
                *("fixtures/native-integration/" + name for name in (
                    "p0-correctness-native-route.md", "p0-security-native-route.md",
                    "p0-performance-native-route.md", "p0-test-coverage-native-route.md",
                    "p0-architecture-native-route.md", "p0-dependencies-native-route.md",
                    "p0-dx-tooling-native-route.md", "p0-docs-handoff-native-route.md",
                    "p0-direction-native-route.md", "single-plan-native-route.md",
                    "negative-generic-roadmap.md", "transcripts/audit-object-route-canary-transcript.md"))))),
    SKILL_LAYOUT_PROFILE: dict(label="skill-layout", index=86, program="tests/skill-layout-contract.test.sh",
        programs={
            "tests/skill-layout-contract.test.sh": "1139d5406839aec5ebdfd82eb0ad63ec9f3c5404cabf3a6c377af0db4a546a7e",
            "scripts/check-skill-layout-contract.sh": "b73e014aa4727d064108515fd959f1d9efb799b2afa1d02f0e7677bd51d02988",
            # The original scans scripts as data. Pin the engine runner too:
            # its captured source must survive the existing launcher insertion.
            RUNNER: "345f51885abbeeda2e4ecd0de503febe50f30f853630a44c0c1277f414c1f9ae"},
        data=("README.md", "AGENTS.md", ".codex-plugin/plugin.json"),
        bounds=dict(file_bytes=128 * 1024, total_bytes=8 * 1024**2, files=7),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="TWO_ORIGINAL_PROGRAMS_PINNED_ENGINE_RUNNER_COMPLETE_ACTIVE_SCAN_AND_SKILL_TREES_OBSERVED_GIT_ABSENCE",
        present_git=dict(source_owner=RETENTION_PROFILE, original_args=_SKILL_LAYOUT_GIT_ARGS,
            source_modes="NORMALIZED_0600_READ_ONLY_MOUNT",
            projection="ORIGINAL_SKILL_LAYOUT_COMPLETE_READ_SET_AND_ACTUAL_STANDALONE_GIT_ORIGINAL_TRACKED_PATH_DECISION"),
        recursive=dict(roots=SKILL_LAYOUT_ROOTS, optional=True,
            optional_files=("CONTRIBUTING.md", ".git"), bounds=_RECURSIVE_BOUNDS,
            optional_directory_files=(".git",),
            required_members=SKILL_LAYOUT_REQUIRED)),
    RETENTION_PROFILE: dict(label="audit-retention", index=58, program="tests/audit-retention.test.sh",
        programs={
            "tests/audit-retention.test.sh": "9c06e2ddcc380d7a6eb5f73c620a32c90f99c6805a5195227e63f98a47028a2c",
            "scripts/check-audit-retention.sh": "386d7475f7111a5e5349672b01e9c68f5fa0f15cfcf100930d8dae187370937e"},
        data=("docs/audits/INDEX.md", "docs/audits/RETENTION.md",
              "fixtures/audit-retention/negative-missing-artifact-boundary.md",
              "fixtures/audit-retention/negative-stale-root-reference.md"),
        pinned_data={RUNNER: "345f51885abbeeda2e4ecd0de503febe50f30f853630a44c0c1277f414c1f9ae"},
        bounds=dict(file_bytes=128 * 1024, total_bytes=192 * 1024**2, files=7),
        source_modes="NORMALIZED_0600_READ_ONLY_MOUNT",
        projection="COMPLETE_ACTUAL_SOURCE_AND_STANDALONE_GIT_BYTES_C2_OWNED_STARTUP_ORIGINAL_GIT_AND_FALLBACK_BOTH_RETAINED",
        complete_git=dict(file_bytes=16 * 1024**2, total_bytes=192 * 1024**2,
                          entries=4096, depth=40, path_bytes=2048)),
    AUDIT_OBJECT_PROFILE: dict(label="audit-object-routing", index=70, program="tests/audit-object-routing.test.sh",
        programs={
            "tests/audit-object-routing.test.sh": "e32e07be7163d404a5bd88180ee630f4efc2d614ddae4a0555cbe2fab0744426",
            "scripts/check-routing.sh": "6bddc813e29f13e63ac0f88474fd32418c38bef4110360a2ae6a451a69e36974",
            "scripts/check-lean-discipline.sh": "eff43d8768b019c1dfcd369df84e864de5decea62cb664a3854f62dabc9b003f"},
        data=AUDIT_OBJECT_INPUTS,
        bounds=dict(file_bytes=1024 * 1024, total_bytes=8 * 1024**2, files=26),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="THREE_PINNED_ORIGINAL_PROGRAMS_LITERAL_READS_AND_PRESENCE_WITH_THREE_COMPLETE_RECURSIVE_SCAN_ROOTS_NO_GIT",
        recursive=dict(roots=("skills", "docs/portal", "fixtures/audit-object-routing"), optional=False,
            bounds=_RECURSIVE_BOUNDS, required_members=(
                *(name for name in AUDIT_ROUTING_READS if name.startswith("skills/")),
                "skills/implementaudit/references/lean-operating-discipline.md",
                "skills/implementaudit/templates/PROTOCOL.md", "skills/implementaudit/templates/STATE.md",
                "skills/implementaudit/templates/THINKING.md", "skills/implementaudit/templates/sidecars.md",
                "skills/implementaudit/templates/phase-goal.txt", "fixtures/audit-object-routing/category-matrix.md"))),
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
    PLAN_QUALITY_PROFILE: dict(label="plan-quality", index=84, program="tests/plan-quality-contract.test.sh",
        programs={
            "tests/plan-quality-contract.test.sh": "f0235682cac62a34cffcb5442ed191e6240991327f373fac10711e36ef78f45a",
            "scripts/check-plan-quality-contract.sh": "f89b9ba3e6f7d9a003238b1efc398e3b78aba9a84a9e4fc19cab5dc81c70f8df"},
        data=PLAN_QUALITY_INPUTS, bounds=dict(file_bytes=128 * 1024, total_bytes=1024 * 1024, files=16),
        # cp must preserve the original writable mode in its private copy so
        # the pinned wrapper can append campaign rows. The source mount stays
        # read-only; normalizing source bytes to 0444 would change that behavior.
        source_modes="PRESERVE_READ_ONLY_MOUNT",
        projection="TWO_PINNED_PROGRAMS_THIRTEEN_LITERAL_DEFAULT_AND_EXPLICIT_INPUTS_21_CHECKER_CALLS_PRIVATE_WRITES_ONLY"),
    AUTHORIZATION_PROFILE: dict(label="authorization-binding", index=31, program="tests/authorization-binding-contract.test.sh",
        programs={
            "tests/authorization-binding-contract.test.sh": "30d328e94d72f758328b4378f6c51df281d1d34f3dc784e70fd115ea99edba28",
            "skills/implementaudit/scripts/check-authorization-binding.sh": "e2ff72034bac8317b881dcbf1180a47f6d7b64119398af2b664c47e10cdba728"},
        data=AUTHORIZATION_INPUTS, bounds=dict(file_bytes=128 * 1024, total_bytes=1024 * 1024, files=12),
        # The original helper expands binds with an unquoted for loop. Pin all
        # source records feeding it: unknown glob syntax cannot silently gain a
        # namespace observation. The wrapper's seven private adversarial inputs
        # remain the exact pinned program's literals, including no-binds/dup.
        pinned_data={
            "fixtures/authorization-binding/auth.txt": "f22b0ba6c8dead168fbed2cf62d53d44a44cbf892c141eab4b797b3127ad990e",
            "fixtures/authorization-binding/authorization-record.txt": "913695054d4495db3f6e1e1fd4d7a61fd44ace0caf0d3fab75bb7bdb3528aa98",
            "fixtures/authorization-binding/authorization-record-missing-source.txt": "0a22219560d74fa81a836f6800451a3581c0071469048f2e278debbbb8dd08fc"},
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="TWO_WHOLE_PINNED_PROGRAMS_NINE_LITERAL_INPUTS_FIXED_STATE_AUTH_INVOCATION_BRANCH_NO_PHASE_OR_NATIVE_GRANT",
        temporary_sizes=(20, 28, 79, 28, 66, 21, 78), temporary_directories=1),
    READ_ONLY_PROFILE: dict(label="read-only-plans", index=80, program="tests/read-only-plans-lane.test.sh",
        programs={
            "tests/read-only-plans-lane.test.sh": "f76742263bb1eb06f6c2e531a2c46de943ba1371cc5d12db7c1b8480dc86c30c",
            "scripts/check-plan-quality-contract.sh": "f89b9ba3e6f7d9a003238b1efc398e3b78aba9a84a9e4fc19cab5dc81c70f8df",
            "scripts/check-capability-parity-contract.sh": "5dbca0e81a79e65b95c4d9a532bb893b5405fedb34ddbc360b3acc70f291d871"},
        data=READ_ONLY_INPUTS, bounds=dict(file_bytes=128 * 1024, total_bytes=1024 * 1024, files=41),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="THREE_PINNED_PROGRAMS_COMPLETE_PARITY_DATA_PLAN_DEFAULTS_AND_REQUIRED_DIRECTORY_PRESENCE_NO_ENUMERATION"),
    SAFEGUARD_PROFILE: dict(label="safeguard-restoration", index=83, program="tests/safeguard-restoration.test.sh",
        programs={
            "tests/safeguard-restoration.test.sh": "2da5dd4d059c94af4ffded1caee9456be03a1d1669675e870d64fea7b1b014b0",
            "scripts/check-safeguard-restoration.sh": "b6237e29e9f9e73b910ef5b23b75df2421ebd1d0688a5ab90f5072ca9b67a17f",
            "scripts/check-installed-payload-self-contained.sh": "228ab1ed29c50d7916cca4e82b0696d42314c6a4efb3b2a7bdd43b5a3bfd70b8"},
        data=tuple("fixtures/safeguards/" + name for name in (
            "negative-missing-final-report.md", "negative-missing-5whys-exit.md",
            "negative-unlabeled-source-only-checker.md")),
        bounds=dict(file_bytes=1024 * 1024, total_bytes=8 * 1024**2, files=7),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="THREE_PINNED_PROGRAMS_THREE_LITERAL_NEGATIVES_COMPLETE_SKILLS_BYTES_NAMES_TYPES_AND_PHYSICAL_HELPER_ROUTES",
        recursive=dict(roots=("skills",), optional=False, bounds=_RECURSIVE_BOUNDS,
            required_members=("skills/implementaudit/SKILL.md", "skills/implementaudit/templates/final-report.md",
                "skills/implementaudit/references/sidecars.md", "skills/implementaudit/references/lean-operating-discipline.md",
                "skills/implementaudit/references/repo-state-comparison.md", "skills/implementaudit/references/phase-design.md",
                "skills/implementaudit/references/plan-lifecycle.md", "skills/implementaudit/references/routing.md",
                "skills/implementaudit/templates/read-only-plan.md", "skills/implementaudit/scripts/validate-phase.sh",
                "skills/implementaudit/scripts/validate-run-root.sh", "skills/implementaudit/scripts/repo-state.sh",
                "skills/implementaudit/scripts/custody-append.sh"))),
    ROUTING_PROFILE: dict(label="routing", index=54, program="tests/routing.test.sh",
        programs={
            "tests/routing.test.sh": "77fdce7b44d893f4aa820c9ee913b1ffed37c976dc04a16a7a4c667eaf2ff2af",
            "scripts/check-routing.sh": "6bddc813e29f13e63ac0f88474fd32418c38bef4110360a2ae6a451a69e36974"},
        data=ROUTING_INPUTS, bounds=dict(file_bytes=128 * 1024, total_bytes=1024 * 1024, files=22),
        # The repaired original appends to its private README copy and replaces
        # an invalid fixture. Keep source modes behind the read-only mount so
        # cp preserves its ordinary writable-copy semantics; preserve both G2
        # negatives and all five original checker invocations byte for byte.
        source_modes="PRESERVE_READ_ONLY_MOUNT",
        projection="TWO_PINNED_PROGRAMS_NINETEEN_LITERAL_INPUTS_FIVE_CHECKER_CALLS_REPAIRED_G2_NEGATIVES_PRIVATE_COPIES_ONLY"),
    INSTALLED_PROFILE: dict(label="installed-payload", index=85, program="tests/installed-payload-self-contained.test.sh",
        programs={
            "tests/installed-payload-self-contained.test.sh": "842e9c7063a40fca12816feb0cbc5484b5954e913dac1af5cc767d517251f9a0",
            "scripts/check-installed-payload-self-contained.sh": "228ab1ed29c50d7916cca4e82b0696d42314c6a4efb3b2a7bdd43b5a3bfd70b8"},
        data=(), bounds=dict(file_bytes=1024 * 1024, total_bytes=8 * 1024**2, files=3),
        source_modes="NORMALIZED_0444_READ_ONLY",
        projection="TWO_PINNED_PROGRAMS_COMPLETE_SKILLS_BYTES_NAMES_TYPES_PHYSICAL_HELPER_ROUTES_26_CHECKER_CALLS_PRIVATE_WRITES_ONLY",
        recursive=dict(roots=("skills",), optional=False, bounds=_RECURSIVE_BOUNDS,
            required_members=("skills/implementaudit/SKILL.md",
                "skills/implementaudit/references/repo-state-comparison.md"))),
    PLANNER_COPY_PROFILE: dict(label="planner-copy", index=46, program="tests/planner-stages.test.sh",
        programs={
            "tests/planner-stages.test.sh": "cfa017b1a04886274c6bc6b969623ef6442d9674ee467c9ec251cdace7251bd7",
            "scripts/check-planner-stages.sh": "78d3735a5af7b83f76bafd48feac2af23868e6a8c668f7c579367f627c0a5825"},
        data=("README.md", "docs/diagrams/execution-spine.mmd", "docs/portal/pages/planning-and-phases.html"),
        bounds=dict(file_bytes=1024 * 1024, total_bytes=8 * 1024**2, files=6),
        # Two retained complete tree pairs exceed the prior 32 MiB contract.
        # This explicit original46-only bound keeps the existing conservative
        # allocation accounting and every inherited non-scratch limit.
        scratch_bytes=256 * 1024**2,
        # The original private cp -R and Perl -i operations require the copied
        # files' original writable owner modes. The source mount stays read-only.
        source_modes="PRESERVE_READ_ONLY_MOUNT",
        projection="TWO_PINNED_PROGRAMS_THREE_LITERAL_COPY_INPUTS_COMPLETE_SKILLS_FIXTURES_TREES_AND_THREE_ORIGINAL_PERL_MUTATIONS",
        recursive=dict(roots=("skills", "fixtures"), optional=False, bounds=_RECURSIVE_BOUNDS,
            required_members=tuple(name for name in LIFECYCLE_INPUTS
                if name.startswith(("skills/", "fixtures/simple-audit/"))))),
    FANOUT_PROFILE: dict(label="fanout-coverage", index=91, program="tests/fanout-coverage-contract.test.sh",
        programs={
            "tests/fanout-coverage-contract.test.sh": "1a3d5274e30d99d9f7e1f087086bf3c239228b2b890758736312253b7ca2c372",
            "scripts/check-fanout-coverage-contract.sh": "b3701a09bc7bdda184001e335f5762e5e57b1babc61ce733f91eb4fd3cd6c40b",
            "scripts/check-plan-quality-contract.sh": "f89b9ba3e6f7d9a003238b1efc398e3b78aba9a84a9e4fc19cab5dc81c70f8df"},
        data=FANOUT_INPUTS, bounds=dict(file_bytes=128 * 1024, total_bytes=8 * 1024**2, files=14),
        # The original cp glob is only one observation: grep -R also reads dot,
        # non-Markdown and nested files. Capture the entire typed tree, then
        # preserve modes behind the read-only mount for private append/write.
        source_modes="PRESERVE_READ_ONLY_MOUNT",
        projection="THREE_PINNED_PROGRAMS_PLAN_DEFAULTS_LITERAL_READS_COMPLETE_CHILD_FIXTURE_TREE_AND_GLOB_PRIVATE_MUTATIONS_ONLY",
        recursive=dict(roots=("fixtures/child-agents",), optional=False,
            bounds=_RECURSIVE_BOUNDS, required_members=FANOUT_REQUIRED_MEMBERS)),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def contract_for(profile):
    if type(profile) is not str or profile not in (PROFILE, ANDON_PROFILE, REGISTRY_PROFILE, MARKER_PROFILE,
                                                     COMMIT_PROFILE, AGENTS_PROFILE, ESCALATION_PROFILE, TOPOLOGY_PROFILE,
                                                     CAPABILITY_PROFILE, ISSUES_PROFILE, TERMINAL_PROFILE,
                                                     BACKGROUND_PROFILE, LIFECYCLE_PROFILE, PLAN_QUALITY_PROFILE,
                                                     AUTHORIZATION_PROFILE, READ_ONLY_PROFILE, ROUTING_PROFILE, AUDIT_OBJECT_PROFILE, SAFEGUARD_PROFILE, INSTALLED_PROFILE, PLANNER_COPY_PROFILE, FANOUT_PROFILE, SKILL_LAYOUT_PROFILE, NATIVE_INTEGRATION_PROFILE, RETENTION_PROFILE):
        raise ValueError("unsupported finite-leaf profile")
    return copy.deepcopy(_CONTRACTS[profile])


def source_paths(profile=PROFILE):
    contract = contract_for(profile)
    return (REGISTRY, *contract["programs"], *contract["data"])


def image_subject(state, *, profile=PROFILE):
    """Retain the registry bytes whenever the original actually reads them."""
    contract_for(profile)
    return {name: value for name, value in state["files"].items()
            if name != REGISTRY or profile in (REGISTRY_PROFILE, SKILL_LAYOUT_PROFILE, RETENTION_PROFILE)}


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
            if (final and kind == "FILE" and name in contract.get("optional_directory_files", ()) and
                    stat.S_ISDIR(before.st_mode)):
                # A typed marker only. Its content cannot be admitted by this
                # recursive projection; the fixed caller must close the whole
                # actual Git namespace through the established complete owner.
                opened_directory(parent, component, relative, before)
                stamps[name] = prefix.identity(before)
                probes[name] = dict(kind="DIRECTORY")
            elif not final or kind == "DIRECTORY":
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


def native_integration_output_bounds(state, objects, contract):
    """Bound complete original74 reports without evaluating its acceptance rules."""
    names = sorted(set(state["files"]) - {REGISTRY, *contract["programs"]})
    copied = [name for name in names if name.startswith(("skills/", "fixtures/native-integration/"))]
    first_roots = ("skills/", "fixtures/native-integration/", "fixtures/audit-object-routing/")
    def width(name):
        return 4 * len(name.encode("utf-8")) + 32
    def grep_bound(population, anchors):
        total = 0
        for name in population:
            raw = objects[state["files"][name]["sha256"]]
            # GNU grep records use LF, not Unicode/CR/VT/FF line boundaries.
            # A necessary anchor charges the entire raw line plus its prefix.
            for line in raw.split(b"\n"):
                if anchors is None or any(anchor in line for anchor in anchors):
                    total += len(line) + width(name) + 1
        return total
    def hygiene_bound(population):
        total = 0
        for name in population:
            # Original LF-line deletions can remove an invalid UTF-8 record
            # from a private copy, exposing valid retained diagnostic lines.
            # Replacement decoding preserves those lines and overcounts the
            # invalid portions; the original checker still decodes strictly.
            text = objects[state["files"][name]["sha256"]].decode("utf-8", "replace")
            for line in text.splitlines():
                # Python re.I also recognizes these four ASCII equivalents.
                # Ignore exemption markers and charge all six fixed labels.
                folded = line.translate(str.maketrans("İıſK", "iisk")).casefold()
                if any(anchor in folded for anchor in _NATIVE_HYGIENE_BOUND_ANCHORS):
                    total += 6 * (width(name) + 128)
        return total
    def diagnostic_margin(population):
        # Fixed shell failures, complete pathname errors and traceback/repr
        # expansion; acceptance tokens and semantic results are never inspected.
        return (64 * 1024 + 4 * max((state["files"][name]["bytes"] for name in population), default=0)
            + sum(width(name) + 128 for name in population))
    first = grep_bound([name for name in names if name.startswith(first_roots)], _NATIVE_FORBIDDEN_BOUND_ANCHORS)
    private_first = grep_bound(copied, _NATIVE_FORBIDDEN_BOUND_ANCHORS)
    command = grep_bound([name for name in copied if name.startswith("skills/")], (b"/implementaudit ",))
    hygiene, private_hygiene = hygiene_bound(names), hygiene_bound(copied)
    weak = "fixtures/native-integration/p0-correctness-native-route.md"
    # The original equal-length substitution can introduce Foreign on any
    # correctness-fixture line. Charge every such line, regardless of matching.
    private_first += grep_bound([weak], None)
    private_first += 128 + width("skills/implementaudit/templates/THINKING.md")
    private_hygiene += 12 * (width("fixtures/native-integration/p0-security-native-route.md") + 128)
    default_diagnostic = max(first, command, hygiene) + diagnostic_margin(names)
    private_diagnostic = max(private_first, command, private_hygiene) + diagnostic_margin(copied)
    return dict(read_files=len(names), read_bytes=sum(state["files"][name]["bytes"] for name in names),
        copied_source_files=len(copied), copied_source_bytes=sum(state["files"][name]["bytes"] for name in copied),
        default_first_grep_bytes=first, private_first_grep_bytes=private_first, command_grep_bytes=command,
        default_hygiene_bytes=hygiene, private_hygiene_bytes=private_hygiene,
        grep_report_file_bound=max(first, private_first, command),
        default_diagnostic_bound=default_diagnostic, private_diagnostic_bound=private_diagnostic,
        basis="NECESSARY_ANCHOR_OUTPUT_UPPER_BOUND_IGNORES_EXEMPTIONS_NOT_AN_ACCEPTANCE_DECISION")


def recursive_output_bounds(state, objects, contract, *, profile):
    """Conservative output sizes from complete actual acquired input bytes."""
    if profile == NATIVE_INTEGRATION_PROFILE:
        return native_integration_output_bounds(state, objects, contract)
    names = sorted(set(state["files"]) - {REGISTRY, *contract["programs"]})
    grep_bytes = diagnostics = terminal_bytes = terminal_messages = audit_checker_bytes = 0
    safeguard_bytes = safeguard_messages = 0
    installed_bytes = installed_messages = 0
    for name in names:
        raw = objects[state["files"][name]["sha256"]]
        path_bytes = len(name.encode("utf-8"))
        lines = raw.count(b"\n") + int(bool(raw) and not raw.endswith(b"\n"))
        # Every line may match, with filename, both separators, the longest
        # possible decimal line number and an extra newline. Downstream grep
        # filters cannot increase this stream. Include binary diagnostics too.
        grep_bytes += len(raw) + lines * (path_bytes + len(str(max(lines, 1))) + 3)
        diagnostics += path_bytes + 128
        if profile == SAFEGUARD_PROFILE:
            try:
                text = raw.decode("utf-8", "strict")
            except UnicodeDecodeError:
                # Installed-payload skips undecodable files; the stricter
                # label reader may instead stop with a bounded decode error.
                # Neither path permits acquisition to omit these actual bytes.
                continue
            display_path = max(path_bytes, len(name.encode("ascii", "backslashreplace"))) + len("/work/")
            for lineno, line in enumerate(text.splitlines(), 1):
                normalized = line.replace("\\", "/").lower()
                if not any(token in normalized for token in ("scripts/", "fixtures/", "tests/", "helper-route:")):
                    continue
                # At most two installed-payload reports and one strict-label
                # report per candidate line. Count labels/exemptions as if
                # they fail; this is allocation only, never checker acceptance.
                safeguard_messages += 3
                safeguard_bytes += 3 * (display_path + len(str(lineno)) + 256) + 4 * len(line.encode("utf-8"))
        if profile == AUDIT_OBJECT_PROFILE and name in AUDIT_ROUTING_READS:
            # Eight fixed phrases can each produce one diagnostic per decoded
            # line. Count every Unicode separator and every phrase regardless
            # of exemptions. The original checker alone decides acceptance.
            try:
                count = len(raw.decode("utf-8", "strict").lower().splitlines())
            except UnicodeDecodeError:
                count = 0  # The fixed margin covers decoder tracebacks.
            width = max(path_bytes, len(name.encode("ascii", "backslashreplace")))
            audit_checker_bytes += 8 * count * (width + len(str(max(count, 1))) + 256)
        if profile == INSTALLED_PROFILE:
            try:
                text = raw.decode("utf-8", "strict")
            except UnicodeDecodeError:
                # The original skips this text, while acquisition retains it.
                continue
            display_path = max(path_bytes, len(name.encode("ascii", "backslashreplace"))) + len("/work/")
            for lineno, line in enumerate(text.splitlines(), 1):
                normalized = line.replace("\\", "/").lower()
                if not any(token in normalized for token in ("scripts/", "fixtures/", "tests/", "helper-route:")):
                    continue
                # At most two reference reports, or one full invalid member,
                # per line. Include every label/exemption as a possible error.
                # Four-byte expansion also covers stderr's ASCII backslashes.
                installed_messages += 2
                installed_bytes += 2 * (display_path + len(str(lineno)) + 256) + 4 * len(line.encode("utf-8"))
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
    result = dict(read_files=len(names), read_bytes=sum(state["files"][name]["bytes"] for name in names),
        all_lines_grep_report_bytes=grep_bytes, binary_diagnostic_bytes=diagnostics,
        terminal_possible_messages=terminal_messages, terminal_diagnostic_bytes=terminal_bytes,
        basis="OUTPUT_ALLOCATION_UPPER_BOUND_NOT_AN_ACCEPTANCE_DECISION")
    if profile == SAFEGUARD_PROFILE:
        result.update(safeguard_possible_messages=safeguard_messages,
            safeguard_diagnostic_bytes=safeguard_bytes + 64 * 1024)
    if profile == AUDIT_OBJECT_PROFILE:
        # Fixed default requirements, complete type/name diagnostics and error
        # renderings are bounded without evaluating any acceptance predicate.
        result["audit_checker_diagnostic_bytes"] = (audit_checker_bytes + 1024 * 1024
            + 4 * max((state["files"][name]["bytes"] for name in names), default=0)
            + sum(2 * (len(name.encode("ascii", "backslashreplace")) + 256) for name in names))
    if profile == INSTALLED_PROFILE:
        result.update(installed_possible_messages=installed_messages,
            installed_diagnostic_bytes=installed_bytes + 64 * 1024)
    return result


def skill_layout_output_bounds(state, objects):
    """All possible original diagnostic lines, without an acceptance decision.

    Read_text's newline normalization and splitlines are bounded by decoded
    actual line boundaries. Account for UTF-8 or ASCII backslash replacement,
    every potential stale-line report and every structurally possible tree
    report. The original alone applies the forbidden patterns and exemptions.
    """
    width = lambda text: max(len(text.encode("utf-8")), len(text.encode("ascii", "backslashreplace")))
    active = (".claude-plugin/", ".github/", "scripts/", "tests/", "docs/portal/")
    scan = tree = payload = 0
    line_counts = {}
    for name, record in state["files"].items():
        scanned = name.startswith(active) or name in ("README.md", "AGENTS.md", "CONTRIBUTING.md")
        in_payload = name.startswith("skills/implementaudit/")
        if not scanned and not in_payload:
            continue
        try:
            lines = objects[record["sha256"]].decode("utf-8", "strict").splitlines()
        except UnicodeDecodeError:
            # Original recursive scans skip undecodable files. Their complete
            # bytes remain acquired; literal-read errors use the margin below.
            continue
        prefix = width(name) + len(str(max(len(lines), 1)))
        if scanned:
            line_counts[name] = len(lines)
            scan += sum(prefix + 4 + width(line.strip()) for line in lines)
            # tree_entry first requires a tree glyph; each such input line can
            # produce at most one extra fixed-shape tree diagnostic.
            tree += sum(prefix + 4 + 128 for line in lines if "├" in line or "└" in line)
        if in_payload:
            payload += sum(prefix + 8 + width(line) for line in lines)
    namespace = sum(4 * len(name.encode("utf-8")) + 512
                    for name in {*state["files"], *state["directories"]})
    decoder = 4 * max(value["bytes"] for value in state["files"].values())
    # The first checker stops on an accumulated scan failure; payload hygiene
    # runs only after that stage succeeds. Namespace/literal errors stop early.
    diagnostic = max(scan + tree, payload, namespace, decoder) + 64 * 1024
    return dict(scan_line_counts=line_counts, possible_scan_bytes=scan,
        possible_tree_bytes=tree, possible_payload_bytes=payload,
        namespace_diagnostic_bytes=namespace, decoder_bound=decoder,
        max_stderr_bytes=diagnostic,
        basis="ALL_POSSIBLE_DECODED_LINES_AND_STRUCTURAL_TREE_MARKERS_NOT_ACCEPTANCE")


def snapshot_complete_git_inputs(prefix, root, objects, contract, git_owner, environment):
    """Acquire a genuine complete standalone source through existing owners."""
    if git_owner is None or environment is None:
        raise ValueError("complete Git source requires the captured C2 owner and fixed environment")
    bounds = contract["complete_git"]
    state, stamps = prefix.snapshot_tree(root, objects, bounds)
    prefix.validate_git_namespace(state, objects)
    if any(value["mode"] not in (0o444, 0o644, 0o755) for value in state["files"].values()) or any(
            mode not in (0o700, 0o755) for mode in state["directories"].values()):
        raise ValueError("complete Git source has unsupported ordinary modes")
    if any(len(name.encode("utf-8", "strict")) > bounds["path_bytes"] for name in (*state["files"], *state["directories"])):
        raise ValueError("complete Git source path bound exceeded")
    context = git_owner["context"](root=root, environment=environment, finite_ls_files=True)
    for path, raw in context["captured_control_bytes"].items():
        try:
            name = Path(path).relative_to(root).as_posix()
        except ValueError:
            raise ValueError("complete Git source refuses external configuration bytes") from None
        if name not in state["files"] or objects[state["files"][name]["sha256"]] != raw:
            raise ValueError("C2 control differs from complete acquired Git bytes")
    observed = git_owner["capture"](context, ("ls-files", "-z"))
    paths = context["binding"]["index_format"]["ordinary_paths"]
    if observed.split(b"\0") != [*(name.encode("utf-8") for name in paths), b""]:
        raise ValueError("actual C2 Git observation differs from its supported ordinary index")
    key = digest(observed)
    objects.setdefault(key, observed)
    current, current_stamps = prefix.snapshot_tree(root, {}, bounds)
    if current != state or current_stamps != stamps:
        raise ValueError("complete source or Git bytes changed during acquisition")
    return state, dict(currentness=stamps, projection=dict(
        roots=["."], bounds=dict(bounds), observation="COMPLETE_SOURCE_GIT_BYTES_NAMES_TYPES_AND_EMPTY_DIRECTORIES",
        fallback="WHOLE_ORIGINAL_ROOT_NAMESPACE_RETAINED_INCLUDING_GIT_TRAVERSAL"),
        git=context["binding"], git_observation=dict(argv=["git", "--no-pager", "ls-files", "-z"],
            exit=0, bytes=len(observed), sha256=key, role="READ_ONLY_C2_OBSERVATION_NEVER_SUBSTITUTED_FOR_ORIGINAL_OUTPUT"))


def retention_output_bounds(state, objects):
    """Allocation only: retain the original all-file filter and its exemptions."""
    namespace = [name for name in state["files"] if ".git" not in Path(name).parts]
    tracked = state["complete_git_inputs"]["git"]["index_format"]["ordinary_paths"]
    selected = sorted(set(namespace) | set(tracked))
    archives = [name for name in namespace if name.startswith("docs/audits/archive/") and
                name.endswith(".md") and "/fixtures/" not in name]
    refs = ["docs/audits/" + Path(name).name for name in archives]
    width = lambda name: 4 * len(name.encode("utf-8")) + 32
    # The original empty-prefix tuples admit all selected files after these
    # explicit exclusions. Ignore its archive-text exemptions when allocating.
    active = [name for name in namespace if not name.startswith(("docs/audits/archive/", "fixtures/audit-retention/"))
              and name not in ("docs/maintenance/AGENTS-HISTORY.md", "CHANGELOG.md")]
    active_diagnostics = 0
    for name in active:
        raw = objects[state["files"][name]["sha256"]]
        if b"docs/audits/" in raw:
            active_diagnostics += sum(width(name) + width(ref) + 128 for ref in refs)
            active_diagnostics += 2 * (width(name) + 256)
        if name.startswith("docs/audits/") and b".IMPLEMENTAUDIT/runs" in raw:
            active_diagnostics += width(name) + 1024  # First 160 Unicode code points only.
    names_bytes = sum(len(name.encode("utf-8")) + 1 for name in selected)
    physical_names = set(state["files"]) | set(state["directories"]) | set(tracked)
    physical_name_bytes = sum(len(name.encode("utf-8")) + 1 for name in physical_names)
    forbidden = sum(width(name) + 1 for name in selected)
    margin = 64 * 1024 + max((width(name) for name in selected), default=0)
    diagnostic = margin + 4096  # Literal requirements, bounded line excerpts and tracebacks.
    stderr = max(active_diagnostics + margin, forbidden + margin, diagnostic) + 4096
    largest = max((state["files"][name]["bytes"] for name in active), default=0)
    audit_lines = max((state["files"][name]["bytes"] for name in active
                       if name.startswith("docs/audits/")), default=0)
    fixed_reads = sum(state["files"][name]["bytes"] for name in ("docs/audits/INDEX.md", "docs/audits/RETENTION.md"))
    # Charge decoding plus joined diagnostics separately from splitlines' many
    # small strings and Path/name containers. This is an allocation refusal,
    # never an answer about whether any original semantic check will pass.
    memory = (64 * 1024**2 + 8 * (largest + fixed_reads + stderr) + 32 * audit_lines +
              64 * physical_name_bytes + 512 * (len(physical_names) + len(selected) + len(archives)))
    return dict(namespace_files=len(namespace), tracked_files=len(tracked), fallback_and_tracked_union=len(selected),
        archive_markdown_files=len(archives), archive_stale_names=refs,
        source_read_files=len(active), source_read_bytes=sum(state["files"][name]["bytes"] for name in active),
        selected_name_bytes=names_bytes, complete_traversal_name_bytes=physical_name_bytes,
        diagnostic_file_bound=diagnostic, max_stderr_bytes=stderr,
        active_diagnostic_bound=active_diagnostics, forbidden_name_diagnostic_bound=forbidden,
        original_data_memory_reservation=memory,
        basis="COMPLETE_ROOT_AND_INDEX_NAMES_NECESSARY_REFERENCE_ANCHOR_BOUNDS_NOT_SEMANTIC_ACCEPTANCE")


def snapshot_skill_layout_git(prefix, root, objects, state, contract, git_owner, environment):
    """Extend the observed read set using the same captured C2/source owners."""
    complete_contract = contract_for(contract["present_git"]["source_owner"])
    complete, detail = snapshot_complete_git_inputs(prefix, root, objects, complete_contract, git_owner, environment)
    if (any(complete["files"].get(name) != value for name, value in state["files"].items()) or
            any(complete["directories"].get(name) != mode for name, mode in state["directories"].items())):
        raise ValueError("skill-layout read inputs changed before complete Git acquisition")
    context = git_owner["context"](root=root, environment=environment, finite_skill_layout=True)
    baseline = {key: value for key, value in detail["git"].items() if key != "read_profile"}
    scoped = {key: value for key, value in context["binding"].items()
              if key not in ("read_profile", "observation_bounds")}
    if baseline != scoped:
        raise ValueError("skill-layout Git command context differs from complete source custody")
    observed = git_owner["capture"](context, _SKILL_LAYOUT_GIT_ARGS)
    streams = {}
    for name in ("stdout", "stderr"):
        raw = observed[name]
        key = digest(raw)
        objects.setdefault(key, raw)
        streams[name] = dict(bytes=len(raw), sha256=key)
    # Reuse the exact recursive owner to close optional absence and complete
    # active memberships too; a newly added scan file cannot escape allocation.
    recursive, currentness = snapshot_recursive_inputs(prefix, root, {}, contract["recursive"])
    if (currentness != {key: value for key, value in state["recursive_inputs"].items() if key != "resources"} or
            any(complete["files"].get(name) != value for name, value in recursive["files"].items())):
        raise ValueError("skill-layout read population changed during Git acquisition")
    current, stamps = prefix.snapshot_tree(root, {}, complete_contract["complete_git"])
    if current != complete or stamps != detail["currentness"]:
        raise ValueError("complete skill-layout source or Git changed during acquisition")
    names = set(complete["files"]) | set(complete["directories"]) | set(detail["git"]["index_format"]["ordinary_paths"])
    name_bytes = sum(len(name.encode("utf-8")) + 1 for name in names)
    read_bytes = sum(value["bytes"] for value in state["files"].values())
    # Read-set limits stay at their original values. Opaque Git/research bytes
    # remain in custody, without pretending the original decodes those inputs.
    memory = (64 * 1024**2 + 64 * read_bytes + 8 * state["layout_resources"]["max_stderr_bytes"] +
              64 * name_bytes + 512 * (len(names) + detail["git"]["index_format"]["entries"]) +
              4 * complete["files"][".git/index"]["bytes"])
    feature = dict(branch="PRESENT_GIT", git=context["binding"],
        original_argv=["git", *_SKILL_LAYOUT_GIT_ARGS], observer_argv=["git", "--no-pager", *_SKILL_LAYOUT_GIT_ARGS],
        observed_exit=observed["exit"], streams=streams,
        role="ACTUAL_C2_OBSERVATION_NOT_ORIGINAL_RESULT_OR_SUBSTITUTE",
        read_files=len(state["files"]), read_bytes=read_bytes, read_bounds=dict(contract["bounds"]),
        complete_traversal_name_bytes=name_bytes, original_data_memory_reservation=memory)
    return complete, detail, feature


def snapshot_source(prefix, root, objects, *, profile=PROFILE, registry_snapshot=None, git_owner=None, environment=None):
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
    if "complete_git" in contract:
        complete, currentness = snapshot_complete_git_inputs(prefix, root, objects, contract, git_owner, environment)
        if any(complete["files"].get(name) != value for name, value in state["files"].items()):
            raise ValueError("literal inputs changed during complete Git source acquisition")
        state["files"].update(complete["files"])
        state["directories"].update(complete["directories"])
        state["complete_git_inputs"] = currentness
        stamps["complete_git_inputs"] = currentness
        state["complete_git_inputs"]["resources"] = retention_output_bounds(state, objects)
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
    for name, pin in contract.get("pinned_data", {}).items():
        if state["files"][name]["sha256"] != pin:
            raise ValueError("unsupported finite-leaf pinned branch input")
    if profile == SKILL_LAYOUT_PROFILE:
        kind = state["recursive_inputs"]["projection"]["probes"][".git"]["kind"]
        if kind not in ("MISSING", "DIRECTORY"):
            raise ValueError("skill-layout requires observed Git absence or complete standalone Git storage")
        if kind == "MISSING" and environment is not None and environment != prefix.ENVIRONMENT:
            raise ValueError("observed skill-layout Git branch changed from the selected startup environment")
        state["layout_resources"] = skill_layout_output_bounds(state, objects)
        if kind == "DIRECTORY":
            complete, currentness, feature = snapshot_skill_layout_git(
                prefix, root, objects, state, contract, git_owner, environment)
            state["files"].update(complete["files"])
            state["directories"].update(complete["directories"])
            state["complete_git_inputs"] = currentness
            stamps["complete_git_inputs"] = currentness
            state["skill_layout_git_inputs"] = feature
            stamps["skill_layout_git_inputs"] = feature
    if profile == ROUTING_PROFILE:
        # This checker accumulates every error. Bound all eight possible phrase
        # messages on every structurally observed line without inspecting any
        # acceptance token, phrase or negation. One extra line per file covers
        # the original private README append; invalid UTF-8 instead produces
        # a bounded decoder traceback. All fixed requirement messages and
        # decoder/repr expansion fit the independent margin below.
        lines = {name: 0 for name in ROUTING_SCAN_INPUTS}
        for name in lines:
            try:
                lines[name] = len(objects[state["files"][name]["sha256"]].decode("utf-8", "strict").splitlines()) + 1
            except UnicodeDecodeError:
                pass
        diagnostic = 64 * 1024 + 4 * max(state["files"][name]["bytes"] for name in contract["data"])
        diagnostic += sum(count * 8 * (len(name.encode("utf-8")) + 32 + 128) for name, count in lines.items())
        state["routing_resources"] = dict(line_upper_counts=lines, diagnostic_file_bound=diagnostic,
            basis="ALL_EIGHT_POSSIBLE_MESSAGES_PER_LINE_PLUS_FIXED_AND_DECODER_MARGIN_NOT_ACCEPTANCE")
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
    if profile == NATIVE_INTEGRATION_PROFILE:
        bound = state["recursive_inputs"]["resources"]
        copied = [entry["bytes"] + 128 for name, entry in state["files"].items()
                  if name.startswith(("skills/", "fixtures/native-integration/"))]
        copied_dirs = sum(name in ("skills", "fixtures/native-integration") or
            name.startswith(("skills/", "fixtures/native-integration/")) for name in state["directories"])
        diagnostic, report = bound["private_diagnostic_bound"], bound["grep_report_file_bound"]
        sed_sizes = tuple(state["files"]["fixtures/native-integration/" + name]["bytes"] + 128 for name in (
            "p0-correctness-native-route.md", "transcripts/audit-object-route-canary-transcript.md",
            "negative-generic-roadmap.md"))
        checker = state["files"]["scripts/check-native-integration.sh"]["bytes"]
        # Seven complete trees coexist until the wrapper's final trap. Two
        # removals only decrease use; both appends fit the per-file 128 margin.
        # Three non-growing sed temporaries, two grep reports, seven diagnostic
        # files and eight possible heredoc spools are all charged concurrently.
        sizes = (*copied * 7, *((diagnostic,) * 7), report, report, *sed_sizes, *((checker,) * 8))
        copies, files, directories = 7, len(sizes), 1 + 7 * (copied_dirs + 2)
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=4096,
            max_stderr_bytes=max(bound["default_diagnostic_bound"], diagnostic) + 4096,
            copied_files=7 * len(copied), copied_source_files=len(copied), copied_source_directories=copied_dirs,
            copied_source_bytes=bound["copied_source_bytes"], diagnostic_files=7, diagnostic_file_bound=diagnostic,
            grep_report_files=2, grep_report_file_bound=report, sed_temporary_files=3,
            sed_temporary_bytes=list(sed_sizes), checker_spools=8, checker_spool_bytes=8 * checker)
    elif profile == RETENTION_PROFILE:
        bound = state["complete_git_inputs"]["resources"]
        diagnostic = bound["diagnostic_file_bound"]
        checker = state["files"]["scripts/check-audit-retention.sh"]["bytes"]
        # The exact wrapper keeps three logs and one generated private file.
        # Charge all four checker spools and the wrapper spool simultaneously.
        sizes = (diagnostic,) * 3 + (checker,) * 4 + (128, 128)
        copies, files, directories = 0, len(sizes), 1
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=4096,
            max_stderr_bytes=bound["max_stderr_bytes"], diagnostic_files=3,
            diagnostic_file_bound=diagnostic, checker_spools=4, checker_spool_bytes=4 * checker,
            wrapper_spools=1, generated_files=1, original_data_memory_reservation=bound["original_data_memory_reservation"])
    elif profile in (PLAN_QUALITY_PROFILE, READ_ONLY_PROFILE):
        # Every original diagnostic includes at most one data-derived line,
        # plus bounded literal paths/tokens/traceback. Charge UTF-8 error/repr
        # expansion at four bytes per input byte and a 64 KiB fixed margin.
        # All diagnostic files and possible Bash here-doc spools are charged
        # simultaneously, even though the original overwrites/reuses them.
        plan_size = state["files"]["fixtures/read-only-plans/valid-handoff-plan.md"]["bytes"]
        diagnostic = 4 * max(max(sizes), plan_size + 128) + granule
        checker = state["files"]["scripts/check-plan-quality-contract.sh"]["bytes"]
        if profile == PLAN_QUALITY_PROFILE:
            # Nine copied plans with <=128 appended bytes, four generated PR
            # bodies, two generated plans, seven diagnostics, 21 checker spools
            # and two wrapper spools. The checker program bounds its own body.
            sizes = (plan_size + 128,) * 9 + (64,) * 4 + (1024,) * 2 + (diagnostic,) * 7 + (checker,) * 21 + (1024,) * 2
            directories = 1
        else:
            parity = state["files"]["scripts/check-capability-parity-contract.sh"]["bytes"]
            sizes = (diagnostic,) + (checker,) * 3 + (parity,)
            directories = 0
        copies, files = (9 if profile == PLAN_QUALITY_PROFILE else 0), len(sizes)
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=4096,
            max_stderr_bytes=diagnostic + 4096, diagnostic_file_bound=diagnostic)
    elif profile == SKILL_LAYOUT_PROFILE:
        # Nine complete fixtures coexist. Each creates twelve files and fifteen
        # directories; account for one removed child, one extra child/file,
        # one flat file, eight retained diagnostics, the outer mktemp directory
        # and three possible checker/wrapper here-document spools.
        wrapper = state["files"][contract["program"]]["bytes"]
        checker = state["files"]["scripts/check-skill-layout-contract.sh"]["bytes"]
        generated = 4 * wrapper + 4096
        diagnostic = 4 * wrapper + granule
        sizes = (generated,) * 109 + (diagnostic,) * 8 + (checker, checker, wrapper)
        copies, files, directories = 10, len(sizes), 137
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=4096,
            max_stderr_bytes=max(state["layout_resources"]["max_stderr_bytes"], diagnostic + granule),
            diagnostic_file_bound=diagnostic, generated_file_bound=generated,
            generated_private_files=109, private_fixture_trees=9)
        if "skill_layout_git_inputs" in state:
            extra["original_data_memory_reservation"] = state["skill_layout_git_inputs"]["original_data_memory_reservation"]
    elif profile == ROUTING_PROFILE:
        checker_name = "scripts/check-routing.sh"
        checker = state["files"][checker_name]["bytes"]
        # Nineteen data copies and the copied checker, two captured diagnostic
        # files, five possible checker here-doc spools, two wrapper spools.
        # Charge all simultaneously, although sequential execution reuses them.
        copies = [state["files"][name]["bytes"] for name in (*contract["data"], checker_name)]
        copies[contract["data"].index("README.md")] += 64
        invalid = contract["data"].index("fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md")
        copies[invalid] = max(copies[invalid], 128)
        diagnostic = state["routing_resources"]["diagnostic_file_bound"]
        sizes = (*copies, diagnostic, diagnostic, *((checker,) * 5), 128, 1024)
        copies, files, directories = len(copies), len(sizes), 15
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=4096,
            max_stderr_bytes=diagnostic + 4096, diagnostic_file_bound=diagnostic)
    elif profile == FANOUT_PROFILE:
        fixture_root = "fixtures/child-agents"
        copied = (*FANOUT_COPY_INPUTS, *(name for name in sorted(state["files"])
            if str(Path(name).parent) == fixture_root and not Path(name).name.startswith(".") and name.endswith(".md")))
        # Eleven reset_sandbox calls remove the previous complete private tree
        # before copying the next. Reserve one live tree, all three possible
        # transform outputs, both global diagnostics and all three Bash spools.
        # Appends fit128 bytes; ALLOW -> REJECT can grow once on every line,
        # so double that file's original byte count rather than assume one hit.
        discrimination = fixture_root + "/exploratory-discrimination-cases.md"
        copy_sizes = [state["files"][name]["bytes"] * (2 if name == discrimination else 1) + 128 for name in copied]
        child_ref, _, thinking = FANOUT_COPY_INPUTS
        transforms = [state["files"][name]["bytes"] * (2 if name == discrimination else 1) + 512
                      for name in (child_ref, thinking, discrimination)]
        bound = state["recursive_inputs"]["resources"]
        child_bytes = state["files"][child_ref]["bytes"]
        # Bound every grep line, binary diagnostic and quoted byte. Python's
        # private read_text/write_text can normalize every CR into a newline;
        # reserve even one new prefixed line per child-reference byte. The
        # pinned sed rewrite can add at most one byte per original input byte.
        report = 4 * bound["all_lines_grep_report_bytes"] + bound["binary_diagnostic_bytes"]
        report += child_bytes * (4 * len(child_ref.encode("utf-8")) + 32 + 8)
        report += state["files"][discrimination]["bytes"] + 4096
        data_sizes = [value["bytes"] for name, value in state["files"].items()
                      if name not in {REGISTRY, *contract["programs"]}]
        plan_diagnostic = 4 * max(data_sizes) + granule
        # Complete typed namespaces include glob-matching directories, which
        # the original cp may reject. Charge all possible operand diagnostics
        # without pretending that such a population has passed the original.
        namespace_diagnostic = sum(4 * len(name.encode("utf-8")) + 512
                                   for name in {*state["files"], *state["directories"]})
        checker = state["files"]["scripts/check-plan-quality-contract.sh"]["bytes"]
        wrapper = state["files"][contract["program"]]["bytes"]
        sizes = (*copy_sizes, *transforms, report, plan_diagnostic, checker, checker, wrapper)
        copies, files, directories = len(copied), len(sizes), 7
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=4096,
            max_stderr_bytes=report + plan_diagnostic + namespace_diagnostic + granule,
            diagnostic_file_bound=plan_diagnostic, recursive_report_bound=report,
            glob_files=list(copied[3:]), private_tree_incarnations=11)
    elif profile == AUTHORIZATION_PROFILE:
        data_bytes = sum(sizes)
        sizes = contract["temporary_sizes"]
        copies, files, directories = 0, len(sizes), contract["temporary_directories"]
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=4096,
            max_stderr_bytes=4 * data_bytes + granule)
    elif profile == PLANNER_COPY_PROFILE:
        copied = [value["bytes"] for name, value in state["files"].items()
                  if name.startswith(("skills/", "fixtures/"))]
        copied_directories = [name for name in state["directories"]
            if name in ("skills", "fixtures") or name.startswith(("skills/", "fixtures/"))]
        checker = state["files"]["scripts/check-planner-stages.sh"]["bytes"]
        inplace = max(state["files"][name]["bytes"] for name in (
            "skills/implementaudit/references/plan-lifecycle.md",
            "skills/implementaudit/references/planning-depth.md"))
        # Three serial copy phases peak at two retained tree pairs before the
        # preceding pair is removed. Include active/staged checker files, three
        # persistent literal copies, and the one Perl -i replacement file.
        # All three fixed substitutions preserve or shorten the original bytes.
        sizes = copied * 2 + [checker] * 2 + sizes + [inplace]
        copies, files, directories = 2, len(sizes), 2 * len(copied_directories) + 6
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        path_bytes = sum(len(name.encode("utf-8")) for name in state["files"])
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=512,
            max_stderr_bytes=4 * path_bytes + granule, original_copy_phases=3,
            copied_source_files=len(copied), copied_source_directories=len(copied_directories),
            copied_source_bytes=sum(copied), inplace_file_bytes=inplace,
            capacity_disposition="EXPLICIT_ORIGINAL46_256MIB_CONTRACT_NO_AUTOMATIC_EXPANSION")
    elif profile == SAFEGUARD_PROFILE:
        diagnostic = state["recursive_inputs"]["resources"]["safeguard_diagnostic_bytes"]
        checker = state["files"]["scripts/check-safeguard-restoration.sh"]["bytes"]
        installed = state["files"]["scripts/check-installed-payload-self-contained.sh"]["bytes"]
        # Three retained diagnostic files; all four calls traverse both pinned
        # Python here-documents. Charge eight possible spools simultaneously.
        sizes = (diagnostic,) * 3 + (checker,) * 4 + (installed,) * 4
        copies, files, directories = 0, len(sizes), 1
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=diagnostic, max_stdout_bytes=512,
            max_stderr_bytes=diagnostic + 1024)
    elif profile == AUDIT_OBJECT_PROFILE:
        bound = state["recursive_inputs"]["resources"]
        report = bound["all_lines_grep_report_bytes"]
        spools = tuple(state["files"][name]["bytes"] for name in (
            "scripts/check-routing.sh", "scripts/check-lean-discipline.sh"))
        sizes = (report, *spools)
        copies, files, directories = 0, 3, 0
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=1024,
            # set -e stops on either checker's diagnostic exit before the
            # wrapper's grep pipeline can run. These error streams cannot add.
            max_stderr_bytes=max(report + bound["binary_diagnostic_bytes"],
                bound["audit_checker_diagnostic_bytes"]) + 4096,
            report_file_bound=report, checker_spool_bytes=sum(spools))
    elif profile == INSTALLED_PROFILE:
        diagnostic = state["recursive_inputs"]["resources"]["installed_diagnostic_bytes"]
        wrapper = state["files"][contract["program"]]["bytes"]
        checker = state["files"]["scripts/check-installed-payload-self-contained.sh"]["bytes"]
        # All 21 ordinary routes, the hardlink route and three bad payloads
        # persist until the trap: 48 payload path entries and 121 directories.
        # Charge the hardlink's two names as independent storage. Every fixed
        # generated payload fits the pinned wrapper; root-only copies checker.
        # Three diagnostics include the separate /tmp/payload-self-contained.out.
        # Reserve both wrapper spools and all 26 checker spools simultaneously.
        sizes = (max(wrapper, checker),) * 48 + (diagnostic,) * 3 + (wrapper,) * 2 + (checker,) * 26
        copies, files, directories = 1, len(sizes), 121
        content, allocated = sum(sizes), sum(map(rounded, sizes))
        extra = dict(largest_file_bytes=max(sizes), max_stdout_bytes=4096,
            max_stderr_bytes=4 * diagnostic + granule, diagnostic_file_bound=diagnostic,
            original_checker_calls=26, private_payload_entries=48,
            private_payload_inodes=47, possible_heredoc_spools=28)
    elif profile == ISSUES_PROFILE:
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
    if "recursive" in contract or "complete_git" in contract:
        result["basis"] = "COMPLETE_ACQUIRED_INPUT_OUTPUT_BOUND_AND_FIXED_PRIVATE_WRITE_SET"
    elif profile in (PLAN_QUALITY_PROFILE, AUTHORIZATION_PROFILE, READ_ONLY_PROFILE, ROUTING_PROFILE):
        result["basis"] = "ACQUIRED_LITERAL_BYTES_AND_PINNED_BRANCH_PRIVATE_WRITE_SET"
    return result


def require_resource_capacity(reservation, limits):
    if reservation["required_bytes"] > limits["scratch_bytes"]:
        raise ValueError("finite-leaf temporary write set exceeds scratch capacity")
    stream = min(limits["file_bytes"], limits.get("stream_bytes", limits["file_bytes"]))
    for field, limit in (("largest_file_bytes", limits["file_bytes"]),
                         ("max_stdout_bytes", stream), ("max_stderr_bytes", stream)):
        if field in reservation and reservation[field] > limit:
            raise ValueError("finite-leaf " + field + " exceeds original file/stream capacity")
    if ("original_data_memory_reservation" in reservation and
            reservation["original_data_memory_reservation"] > limits["address_bytes"] * 3 // 4):
        raise ValueError("finite-leaf original data exceeds memory capacity")


def retention_image_reservation(files, limits):
    """The unchanged launcher materializes every member under RLIMIT_FSIZE."""
    member_limit = min(contract_for(RETENTION_PROFILE)["complete_git"]["file_bytes"], limits["file_bytes"])
    if any(len(raw) > member_limit for raw, _ in files.values()):
        raise ValueError("complete Git image member exceeds unchanged original file capacity")
    descriptors = len(files) + 2 + 64
    mounted = sum(len(raw) for raw, _ in files.values())
    if descriptors > limits["descriptors"] or mounted > limits["address_bytes"] // 4:
        raise ValueError("complete Git image exceeds finite descriptor/memory reservation")
    return dict(descriptors=descriptors, observer_descriptor_margin=64, mounted_bytes=mounted,
                address_reservation_bytes=limits["address_bytes"] // 4, image_member_limit=member_limit)


def retention_readonly_image(files):
    """Keep every captured member; use the RO data mount's compact0600 mode."""
    if any(mode not in (0o444, 0o555) for _, mode in files.values()):
        raise ValueError("retention compact image requires normalized data/executable modes")
    return {name: (raw, 0o600 if mode == 0o444 else mode) for name, (raw, mode) in files.items()}


def finite_image_permissions(files, source, *, profile=PROFILE):
    """Select fixed image permissions from the already acquired source branch."""
    contract = contract_for(profile)
    source_modes = contract["source_modes"]
    if profile == SKILL_LAYOUT_PROFILE and "skill_layout_git_inputs" in source:
        feature = source["skill_layout_git_inputs"]
        if (not isinstance(feature, dict) or feature.get("branch") != "PRESENT_GIT" or
                "complete_git_inputs" not in source):
            raise ValueError("unsupported acquired skill-layout image branch")
        source_modes = contract["present_git"]["source_modes"]
    if source_modes == "NORMALIZED_0600_READ_ONLY_MOUNT":
        if profile not in (RETENTION_PROFILE, SKILL_LAYOUT_PROFILE):
            raise ValueError("unsupported compact read-only image profile")
        return retention_readonly_image(files), dict(source_modes=source_modes,
            data_permissions="OWNER_0600_READ_ONLY_MOUNT")
    return files, dict(source_modes=source_modes)


def retention_runtime_binding(source, runtime, objects, *, profile=RETENTION_PROFILE):
    """Bind the real C2 observer to the same physical Git carried to /work."""
    if profile not in (RETENTION_PROFILE, SKILL_LAYOUT_PROFILE):
        raise ValueError("unsupported complete Git runtime command scope")
    binding = source["complete_git_inputs"]["git"]
    executable = binding["executable"]
    name = executable["selected_path"]
    observed = runtime["observations"].get(name)
    entry = runtime["files"].get(name)
    if (name != "/usr/bin/git" or executable["resolved_path"] != name or observed is None or entry is None or
            observed["resolved"] != name or any(observed[key] != executable[key] for key in ("sha256", "bytes", "mode")) or
            [str(observed["identity"][i]) for i in (0, 1, 2, 4, 5, 6)] != binding["executable_file_identity"] or
            entry["sha256"] != executable["sha256"] or digest(objects.get(entry["sha256"], b"")) != entry["sha256"]):
        raise ValueError("complete Git source observer differs from captured original runtime")
    args = _SKILL_LAYOUT_GIT_ARGS if profile == SKILL_LAYOUT_PROFILE else ("ls-files", "-z")
    return dict(executable=executable, original_argv=["git", *args],
                custody="ACTUAL_CAPTURED_SYSTEM_GIT_BYTES_ORIGINAL_COMMAND_OUTPUT_NEVER_SUBSTITUTED")


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


def _capture_planner_runtime(prefix, runtime, objects):
    """Capture one fixed Perl ELF, keeping optional image absences explicit."""
    for path in _PLANNER_ABSENT_PROBES:
        if any(name == path or name.startswith(path + "/") for name in runtime["files"]):
            raise ValueError("unsupported Perl optional input in finite runtime")
    dependencies = set(_PLANNER_RUNTIME_PINS) - {"/usr/bin/perl"}
    if any(name not in runtime["files"] or name not in runtime["observations"] for name in dependencies):
        raise ValueError("unsupported Perl loader/library closure")
    path = Path("/usr/bin/perl")
    # The inspected system Perl has two ordinary hardlinks. As with the
    # existing system runtime reader, capture its physical bytes/identity;
    # never dispatch this host path or propagate its aliases into the image.
    metadata, raw = prefix.read_regular(path, prefix.RUNTIME_BOUNDS["file_bytes"], single_link=False)
    key = digest(raw)
    if key != _PLANNER_RUNTIME_PINS[str(path)] or metadata["mode"] != 0o755:
        raise ValueError("unsupported captured Perl executable")
    for name in dependencies:
        pin = _PLANNER_RUNTIME_PINS[name]
        observed, entry = runtime["observations"][name], runtime["files"][name]
        if entry["sha256"] != pin or digest(objects.get(pin, b"")) != pin:
            raise ValueError("unsupported Perl loader/library closure")
        original = Path(name)
        resolved = original.resolve(strict=True)
        if str(resolved) != observed["resolved"]:
            raise ValueError("Perl runtime closure alias changed")
        current, captured = prefix.read_regular(resolved, prefix.RUNTIME_BOUNDS["file_bytes"], single_link=False)
        if current["identity"] != observed["identity"] or digest(captured) != pin or original.resolve(strict=True) != resolved:
            raise ValueError("Perl runtime closure changed during acquisition")
    again, current = prefix.read_regular(path, prefix.RUNTIME_BOUNDS["file_bytes"], single_link=False)
    if metadata != again or raw != current:
        raise ValueError("Perl executable changed during acquisition")
    objects.setdefault(key, raw)
    runtime["files"][str(path)] = dict(mode=0o555, bytes=len(raw), sha256=key)
    runtime["observations"][str(path)] = dict(resolved=str(path), mode=metadata["mode"],
        bytes=len(raw), sha256=key, identity=metadata["identity"])
    runtime["planner_perl_closure"] = dict(_PLANNER_RUNTIME_PINS)
    runtime["planner_perl_inputs"] = {name: "ABSENT_IN_FINITE_IMAGE_RUNTIME_BEHAVIOR_UNQUALIFIED"
                                     for name in _PLANNER_ABSENT_PROBES}


def finite_runtime(prefix, objects, *, profile=PROFILE):
    contract_for(profile)
    runtime = prefix.acquire_runtime(objects)
    if profile == TOPOLOGY_PROFILE:
        _capture_topology_runtime(prefix, runtime, objects)
    if profile == PLANNER_COPY_PROFILE:
        _capture_planner_runtime(prefix, runtime, objects)
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
    git_owner = ({"context": base._acquire.__globals__["_preflight_git_context_v1"],
                  "capture": base._acquire.__globals__["_preflight_git_capture_v1"]}
                 if profile in (RETENTION_PROFILE, SKILL_LAYOUT_PROFILE) else None)

    class FiniteVerifierSession(parent):
        SCOPE = profile
        LIMITS = dict(parent.LIMITS)
        if profile == PLANNER_COPY_PROFILE:
            # The inherited image, acquisition key, launcher and resource
            # checks all consume this same selected limits mapping.
            LIMITS["scratch_bytes"] = contract["scratch_bytes"]
        elif profile == NATIVE_INTEGRATION_PROFILE:
            # Original74 retains seven private trees; its fixed ceiling
            # enters the same existing acquisition/image/key owners.
            LIMITS["scratch_bytes"] = 128 * 1024**2
        ENVIRONMENT = (dict(parent.ENVIRONMENT, HOME="/nonexistent", GIT_ATTR_NOSYSTEM="1")
                       if profile == RETENTION_PROFILE else parent.ENVIRONMENT)

        def __init__(self, source_root, output, *, max_age=3600):
            # Preserve the namespace owner's raw-path refusal before inherited
            # convenience resolution can erase a parent-traversal component.
            if any(".." in Path(path).parts for path in (source_root, output)):
                raise compiler.WorkGraphError("finite-leaf parent traversal is unqualified")
            if profile == SKILL_LAYOUT_PROFILE:
                # Select only fixed startup environments from the physical
                # marker's presence. The established source owners reacquire
                # its type/currentness; unsupported markers still refuse there.
                fd = prefix.open_directory(source_root)
                try:
                    try:
                        os.stat(".git", dir_fd=fd, follow_symlinks=False)
                    except FileNotFoundError:
                        pass
                    else:
                        self.ENVIRONMENT = dict(parent.ENVIRONMENT, HOME="/nonexistent", GIT_ATTR_NOSYSTEM="1")
                finally:
                    os.close(fd)
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
                profile=profile, registry_snapshot=registry_snapshot, git_owner=git_owner, environment=self.environment)
            registry = objects[source["files"][REGISTRY]["sha256"]]
            graph, scope, node = select_node(compiler, registry, self.environment, profile=profile)
            temporary = temporary_requirements(source, profile=profile)
            require_resource_capacity(temporary, self.LIMITS)
            runtime = finite_runtime(prefix, objects, profile=profile)
            if "complete_git_inputs" in source:
                runtime["retention_git_binding"] = retention_runtime_binding(source, runtime, objects, profile=profile)
            engine_objects = {}
            for name, expected in self._engine.items():
                captured = prefix.read_regular(engine_root / name)[1]
                if digest(captured) != expected:
                    raise compiler.WorkGraphError("finite-leaf engine source changed during acquisition")
                objects.setdefault(expected, captured)
                engine_objects[name] = expected
            current, final_stamps = snapshot_source(prefix, self.source, {},
                profile=profile, registry_snapshot=registry_snapshot, git_owner=git_owner, environment=self.environment)
            if source != current or stamps != final_stamps or observer != self._observer():
                raise compiler.WorkGraphError("finite-leaf source/runtime observer changed during acquisition")
            self._custody()
            for captured in objects.values():
                self._object(captured)
            runtime_files = {name: (objects[entry["sha256"]], entry["mode"]) for name, entry in runtime["files"].items()}
            _, runtime_key = self._image(runtime_files, {})
            files = dict(runtime_files)
            subject = image_subject(source, profile=profile)
            files.update({"/work/" + name: (objects[value["sha256"]],
                value["mode"] if contract["source_modes"] == "PRESERVE_READ_ONLY_MOUNT" else 0o444)
                for name, value in subject.items()})
            if profile == SKILL_LAYOUT_PROFILE and files["/work/" + RUNNER][0] != objects[self._engine[RUNNER]]:
                raise compiler.WorkGraphError("observed skill-layout runner differs from fixed engine runner")
            if profile == RETENTION_PROFILE and source["files"][RUNNER]["sha256"] != self._engine[RUNNER]:
                raise compiler.WorkGraphError("original-readable runner differs from captured engine bytes")
            files["/work/" + RUNNER] = (objects[self._engine[RUNNER]], 0o555)
            files, image_permissions = finite_image_permissions(files, source, profile=profile)
            if "complete_git_inputs" in source:
                temporary["image_reservation"] = retention_image_reservation(files, self.LIMITS)
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
                temporary.setdefault("image_reservation", {}).update(dict(descriptors=descriptors, observer_descriptor_margin=64,
                    mounted_bytes=image_bytes, address_reservation_bytes=self.LIMITS["address_bytes"] // 4))
                manifest["directories"] = sorted(set(manifest["directories"]) |
                    {"/work/" + name for name in source["directories"] if name != "."})
                manifest["directory_membership"] = source["recursive_inputs"]["projection"]
                manifest["source_projection"] = "COMPLETE_RECURSIVE_READ_BYTES_AND_EXPLICIT_OPTIONAL_PRESENCE"
                image_key = self._object(self._encode(manifest))
            if "complete_git_inputs" in source:
                manifest["directories"] = sorted(set(manifest["directories"]) |
                    {"/work/" + name for name in source["directories"] if name != "."})
                manifest["directory_membership"] = source["complete_git_inputs"]["projection"]
                manifest["source_projection"] = (contract["present_git"]["projection"]
                    if profile == SKILL_LAYOUT_PROFILE else contract["projection"])
                manifest["git_startup"] = runtime["retention_git_binding"]
                manifest["image_reservation"] = temporary["image_reservation"]
                image_key = self._object(self._encode(manifest))
            if "data_permissions" in image_permissions:
                manifest["data_permissions"] = image_permissions["data_permissions"]
                image_key = self._object(self._encode(manifest))
            if profile in (SAFEGUARD_PROFILE, INSTALLED_PROFILE):
                # The original physical helper validator requires st_nlink=1.
                # Select this fixed policy in the acquired image, never from a
                # public argument. Its hash binds execution and retained reuse.
                manifest["source_materialization"] = "SINGLE_LINK_FILES_READ_ONLY_ROOT"
                image_key = self._object(self._encode(manifest))
            source_key = self._object(prefix.encode(source))
            graph_key = self._object(self._encode(graph))
            runtime_observation_key = self._object(prefix.encode(runtime))
            acquired = dict(schema="implementaudit.verifier-" + label + "-acquisition.v1", scope=profile,
                group=scope, producer=self.producer, source_root=[str(self.source), *stamps["."][:2]],
                source=source_key, graph=graph_key, engine=self._engine, engine_objects=engine_objects,
                runtime=runtime_key, runtime_observations=runtime_observation_key,
                inputs={node["id"]: dict(program_sha256=contract["programs"][contract["program"]], image_digest=image_key)},
                environment=self.environment, observer=observer, limits=self.LIMITS,
                source_bounds=(source["complete_git_inputs"]["projection"]["bounds"]
                    if "complete_git_inputs" in source else contract["bounds"]),
                source_projection=(contract["present_git"]["projection"]
                    if "skill_layout_git_inputs" in source else contract["projection"]),
                temporary_reservation=temporary, startup_umask=0o022,
                directory_modes="NORMALIZED_0755_READ_ONLY", source_files=image_permissions["source_modes"],
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
