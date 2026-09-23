"""Exact recovery-consumer source comparison; no install or recovery authority.

The caller must obtain the expected receipt digest from its actual reviewed,
controlled-custody composition/install subject. A self-asserted digest or PASS
field is not independent review, native observation, or permission to install.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

class Refusal(RuntimeError):
    pass

SCRIPTS = "skills/implementaudit/scripts/"
CONSUMER_PATHS = frozenset(SCRIPTS + name for name in (
    "codex-recovery-native-reader.py", "route-transaction.py",
    "codex-recovery-source-transition.py", "codex-recovery-config-transition.py"))
# Exact prospective admission semantics remain independently reviewed source.
ADMISSION_CONTRACT_PATHS = frozenset(("skills/audit-state/SKILL.md",
    "skills/implementaudit/SKILL.md",
    "skills/implementaudit/references/continuity.md",
    "skills/implementaudit/references/route-obligations.md"))
# Exact visibility/dispatch contract carriers, not approval of arbitrary edits.
# Full reviewed receipt/inventories and actual source/native custody still apply.
VISIBILITY_CONTRACT_PATHS = frozenset((
    "skills/implementaudit/references/child-agents.md",
    "skills/implementaudit/references/transcript-contract.md"))
# One explicit supported runtime closure. This category is not content approval:
# every member still needs exact reviewed/physical/native source custody.
VISIBILITY_RUNTIME_PATHS = frozenset(SCRIPTS + name for name in (
    "native-worker-capture.py", "child-parent-visibility.py", "child-load-visibility.py",
    "native-capture-adapter/canary_protocol.py", "native-capture-adapter/capture.py",
    "native-capture-adapter/load_visibility.py", "native-capture-adapter/notification_policy.py",
    "native-capture-adapter/process_owner.py", "native-capture-adapter/worker_profile.py",
    "native-capture-adapter/worker_runtime.py"))
# Exact reviewed native binding carriers; no native compatibility approval.
NATIVE_BINDING_PATHS = frozenset((
    SCRIPTS + "codex-native-desktop-binding.py",
    "skills/implementaudit/references/codex-recovery-observer-profile.json"))
METADATA_PATHS = frozenset((".codex-plugin/plugin.json",))
# Exact reviewed regression support; complete source/review bindings still apply.
TEST_SUPPORT_PATHS = frozenset(("tests/route-obligation-contract.test.sh",  # source repo only: exact regression-support identity
    "scripts/verify-package.sh", "tests/claim-run-unknown-option.test.sh",  # source repo only: exact regression-support identity
    "tests/codex-recovery/test_initial_epoch.py",  # source repo only: exact regression-support identity
    "tests/codex-recovery/test_affected_helper.py",  # source repo only: exact regression-support identity
    "tests/codex-recovery/test_native_launch_diagnostics.py",  # source repo only: exact regression-support identity
    "tests/codex-recovery/test_isolated_qualification_relay.py",  # source repo only: exact regression-support identity
    "tests/codex-recovery/test_mcp_cli_overrides.py",  # source repo only: exact regression-support identity
    "tests/codex-recovery/test_effective_config.py",  # source repo only: exact regression-support identity
    "tests/codex-recovery/test_native_load_contract.py"))  # source repo only: exact regression-support identity

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def digest(value):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise Refusal("invalid exact source digest")
    return value

def relative(value):
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or "\x00" in value or any(part in ("", ".", "..") for part in value.split("/"))
            or PurePosixPath(value).is_absolute()):
        raise Refusal("source member path is not a closed relative path")
    return value

def manifest(rows):
    if not isinstance(rows, list) or not rows or len(rows) > 10000:
        raise Refusal("source inventory missing or oversized")
    result = {}
    folded = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise Refusal("source inventory member schema differs")
        name = relative(row["path"])
        if name.casefold() in folded:
            raise Refusal("source membership collision")
        if type(row["bytes"]) is not int or row["bytes"] < 0:
            raise Refusal("source byte count invalid")
        digest(row["sha256"])
        result[name] = {"bytes": row["bytes"], "sha256": row["sha256"]}
        folded.add(name.casefold())
    return result

def observed(rows, root):
    if not isinstance(rows, list):
        raise Refusal("source observation is not a list")
    members = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "exists", "bytes", "sha256", "mtime_ns"}:
            raise Refusal("physical source observation schema differs")
        if row["exists"] is not True or type(row["mtime_ns"]) is not int:
            raise Refusal("physical source member absent or malformed")
        try:
            path = Path(row["path"])
            if not path.is_absolute():
                raise ValueError("relative observation")
            name = path.relative_to(root).as_posix()
        except (TypeError, ValueError):
            raise Refusal("physical source member is outside exact root") from None
        members.append({"path": name, "bytes": row["bytes"], "sha256": row["sha256"]})
    return manifest(members)

def epoch_pins(rows):
    if not isinstance(rows, list) or len(rows) != 3:
        raise Refusal("exact three original epoch files required")
    for row, stage in zip(rows, ("before", "stopped", "restarted")):
        if (not isinstance(row, dict) or set(row) != {"stage", "bytes", "sha256"}
                or row["stage"] != stage or type(row["bytes"]) is not int or row["bytes"] <= 0):
            raise Refusal("original epoch file identity differs")
        digest(row["sha256"])
    return rows

def validate_source_transition(previous_files, current_files, receipt, *, expected_receipt_sha256, epoch_files):
    keys = {"schema", "predecessor_root", "successor_root", "epoch_files",
            "predecessor_files", "successor_files", "review_subject_sha256"}
    if (not isinstance(receipt, dict) or set(receipt) != keys
            or receipt["schema"] != "implementaudit.recovery-consumer-source-transition.v1"):
        raise Refusal("source transition receipt schema differs")
    if sha(receipt) != digest(expected_receipt_sha256):
        raise Refusal("review-bound source transition digest differs")
    digest(receipt["review_subject_sha256"])
    if epoch_pins(receipt["epoch_files"]) != epoch_pins(epoch_files):
        raise Refusal("original epoch bytes differ")
    try:
        old_root, new_root = (Path(receipt[key]) for key in ("predecessor_root", "successor_root"))
        if (not old_root.is_absolute() or not new_root.is_absolute() or old_root == new_root
                or old_root.is_relative_to(new_root) or new_root.is_relative_to(old_root)
                or ".." in old_root.parts or ".." in new_root.parts):
            raise ValueError("source root")
    except (TypeError, ValueError):
        raise Refusal("exact disjoint source roots required") from None
    previous, current = manifest(receipt["predecessor_files"]), manifest(receipt["successor_files"])
    if previous != observed(previous_files, old_root) or current != observed(current_files, new_root):
        raise Refusal("complete physical source inventory differs from reviewed transition")
    removed = set(previous) - set(current)
    changed = {name for name in current if previous.get(name) != current[name]}
    if removed or not changed or changed - CONSUMER_PATHS - METADATA_PATHS - TEST_SUPPORT_PATHS - ADMISSION_CONTRACT_PATHS - VISIBILITY_CONTRACT_PATHS - VISIBILITY_RUNTIME_PATHS - NATIVE_BINDING_PATHS:
        raise Refusal("source transition changes unqualified producer or unrelated source")
    if changed & VISIBILITY_RUNTIME_PATHS and not VISIBILITY_RUNTIME_PATHS <= set(current):
        raise Refusal("changed visibility runtime requires its complete explicit source closure")
    if SCRIPTS + "codex-recovery-native-reader.py" not in changed or SCRIPTS + "route-transaction.py" not in changed:
        raise Refusal("reader and its exact route pin must change together")
    # No metadata-content equivalence is asserted here. A changed manifest is a
    # separately reviewed exact subject; native selection and unchanged hook
    # trust/producer readbacks remain required after actual supported install.
    return {"schema": "implementaudit.recovery-consumer-source-comparison.v1",
            "receipt_sha256": expected_receipt_sha256,
            "review_subject_sha256": receipt["review_subject_sha256"],
            "predecessor_root": str(old_root), "successor_root": str(new_root),
            "predecessor_count": len(previous), "successor_count": len(current),
            "changed_paths": sorted(changed), "epoch_files": epoch_files,
            "native_producer_observed": False, "currentness_restored": False,
            "ordinary_effect_authority": "NONE"}
