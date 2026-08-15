#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python - <<'PY'
from pathlib import Path
import re


def fail(message: str) -> None:
    raise SystemExit(f"internal-skill-routing.test: {message}")


def require(text: str, token: str, owner: str) -> None:
    if token not in text:
        fail(f"{owner}: missing contract token: {token}")


def frontmatter(path: Path) -> tuple[dict[str, str], str]:
    if not path.is_file():
        fail(f"missing skill: {path.as_posix()}")
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail(f"{path.as_posix()}: missing YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line.startswith("  ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    version = re.search(r'^\s+version:\s*"([^"]+)"\s*$', match.group(1), re.MULTILINE)
    if not version:
        fail(f"{path.as_posix()}: missing metadata.version")
    fields["version"] = version.group(1)
    return fields, text


governor_path = Path("skills/implementaudit/SKILL.md")
governor_meta, governor = frontmatter(governor_path)
if governor_meta.get("name") != "implementaudit" or governor_meta.get("version") != "0.4.0":
    fail("governor identity/version drift")

governor_tokens = [
    "/implementaudit remains the sole stable public/default governor",
    "INTERNAL_SKILL_POPULATION=audit-state,audit-assess,audit-implement,audit-andon",
    "INTERNAL_SKILL_ROUTE_MAX=1",
    "CHILD_TO_CHILD_ROUTING=FORBIDDEN",
    "CHILD_RETURN=GOVERNOR_REQUIRED",
    "DIRECT_CHILD_ENTRY=CAPABILITY_SPECIFIC",
    "DIRECT_ENTRY_DEFAULT=REFUSE_OR_RETURN_TO_GOVERNOR",
    "AUDIT_ANDON_DIRECT_ENTRY=ALLOWED_BOUNDED_CORD_PULL",
    "GOVERNOR_ROUTE_ENVELOPE=REQUIRED",
    "EXECUTING_PACKAGE_IDENTITY=VERIFIED",
    "PACKAGE_PRECEDENCE=UNAMBIGUOUS",
    "AUDIT_OBJECT=BOUND",
    "AUTHORITY_CEILING=BOUND",
    "SELECTED_CHILD=EXACTLY_ONE",
    "PACKAGE_GATE_SUBJECT=EXECUTING_IMPLEMENTAUDIT_PACKAGE",
    "TARGET_UNDER_AUDIT_FAILURE=BOUND_GATE_FAILURE_NOT_EXECUTING_PACKAGE_FAILURE",
    "ORDINARY_CHEAP_PATH=GOVERNOR_ONLY",
    "PLANNING_COGNITION=GOVERNOR_PROGRESSIVE_REFERENCE",
    "EXECUTION_REPAIR_COGNITION=GOVERNOR_PROGRESSIVE_REFERENCE",
    "STATE_ROUTE_CURRENTNESS=MECHANICALLY_VERIFIED_REQUIRED",
    "REVIEW_ROUTE_PACKET=IMMUTABLE_DIGEST_BOUND_REQUIRED",
    "REVIEW_ROUTE_INDEPENDENCE=GOVERNOR_PROVED_REQUIRED",
    "MAINTAINER_ROUTE_CURRENTNESS=MECHANICALLY_VERIFIED_REQUIRED",
    "MAINTAINER_ROUTE_NOT_APPLICABLE_CURRENTNESS=REJECTED",
    "STALE_OR_ABSENT_CURRENTNESS=FAIL_CLOSED",
    "AMBIGUOUS_PLUGIN_STANDALONE_PRECEDENCE=FAIL_CLOSED",
    "INCOMPLETE_EXECUTING_PACKAGE=FAIL_CLOSED",
    "CHILD_AUTHORITY_OR_CLOSURE_OUTPUT=REJECTED",
    "CHILD_RESULT_AUTHORITY=NONE",
    "CHILD_RESULT_CLOSURE=NONE",
    "references/planning-depth.md",
    "references/plan-lifecycle.md",
]
for token in governor_tokens:
    require(governor, token, governor_path.as_posix())

children = {
    "audit-state": {
        "description": "post-boundary state-recovery cognition",
        "tokens": [
            "TRIGGER=POST_BOUNDARY_AFTER_GOVERNOR_MECHANICAL_CURRENTNESS",
            "CURRENTNESS_DISPOSITION=VERIFIED_REQUIRED",
            "CURRENTNESS_NOT_APPLICABLE=REJECTED",
            "GOVERNOR_ROUTE_ENVELOPE=REQUIRED",
            "RETURN_TO_GOVERNOR=REQUIRED",
            "references/continuity.md",
            "decision-usable rehydration record",
        ],
    },
    "audit-assess": {
        "description": "independent/adversarial assessment",
        "tokens": [
            "TRIGGER=IMMUTABLE_PACKET_AND_GOVERNOR_PROVED_INDEPENDENCE",
            "PACKET_DIGEST=REQUIRED",
            "PROSE_ONLY_REVIEW=REJECTED",
            "GOVERNOR_ROUTE_ENVELOPE=REQUIRED",
            "RETURN_TO_GOVERNOR=REQUIRED",
            "references/plan-lifecycle.md",
            "PASS / NEEDS_REVISION / NONVERDICT",
        ],
    },
    "audit-implement": {
        "description": "maintainer-side realised-implementation qualification",
        "tokens": [
            "TRIGGER=MAINTAINER_EXACT_CANDIDATE_AFTER_VERIFIED_RELEASE_CURRENTNESS",
            "RELEASE_CURRENTNESS=VERIFIED_REQUIRED",
            "RELEASE_CURRENTNESS_NOT_APPLICABLE=REJECTED",
            "PACKAGE_GATE_SUBJECT=EXECUTING_IMPLEMENTAUDIT_PACKAGE",
            "GOVERNOR_ROUTE_ENVELOPE=REQUIRED",
            "RETURN_TO_GOVERNOR=REQUIRED",
            "references/transcript-contract.md",
            "observed evidence -> bounded realised implement",
            "DIRECT_ENTRY=REFUSE_OR_RETURN_TO_GOVERNOR",
        ],
    },
    "audit-andon": {
        "description": "bounded abnormality-response cognition",
        "tokens": [
            "TRIGGER=ESTABLISHED_NONTRIVIAL_ANDON_OR_EXPLICIT_CORD_PULL",
            "GOVERNED_ROUTE=L4_TO_AUDIT_ANDON_TO_L4_OR_GOVERNOR",
            "GOVERNOR_ROUTE_ENVELOPE=REQUIRED_FOR_GOVERNED_ROUTE",
            "RETURN_TO_GOVERNOR=REQUIRED_FOR_GOVERNED_ROUTE",
            "DIRECT_ENTRY=ALLOWED_BOUNDED_CORD_PULL",
            "DIRECT_RETURN=ACTUAL_CALLER",
            "DETERMINISTIC_ANDON_CHEAP_PATH=BYPASS",
            "local-vs-systemic",
            "escalation recommendation",
        ],
    },
}

common_child_tokens = [
    "ROUTING_OWNER=/implementaudit",
    "CHILD_ROUTING=FORBIDDEN",
    "AUTHORITY_OWNERSHIP=NONE",
    "CURRENTNESS_OWNERSHIP=NONE",
    "LIFECYCLE_OWNERSHIP=NONE",
    "STATE_MUTATION_OWNERSHIP=NONE",
    "RELEASE_OWNERSHIP=NONE",
    "CLOSURE_OWNERSHIP=NONE",
    "CAN_ESTABLISH_AUDIT_COMPLETE=NO",
]

for name, contract in children.items():
    path = Path("skills") / name / "SKILL.md"
    meta, text = frontmatter(path)
    if meta.get("name") != name:
        fail(f"{path.as_posix()}: frontmatter name mismatch")
    if meta.get("version") != "0.4.0":
        fail(f"{path.as_posix()}: runtime version must be 0.4.0")
    if contract["description"] not in meta.get("description", ""):
        fail(f"{path.as_posix()}: trigger-accurate description missing")
    direct_entry = (
        "DIRECT_ENTRY=ALLOWED_BOUNDED_CORD_PULL"
        if name == "audit-andon"
        else "DIRECT_ENTRY=REFUSE_OR_RETURN_TO_GOVERNOR"
    )
    for token in common_child_tokens + [direct_entry] + contract["tokens"]:
        require(text, token, path.as_posix())

print("internal-skill-routing.test: ok")
PY
