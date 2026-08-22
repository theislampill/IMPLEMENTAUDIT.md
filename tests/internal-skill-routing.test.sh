#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

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
    "CHILD_ROUTE=LOADED_ONLY_VISIBLE_REQUIRED",
    "INTERNAL_SKILL_RESOLVER=scripts/resolve-internal-skill.py",
    "CANONICAL_CHILD_PATH=../<child>/SKILL.md",
    "STANDALONE_CHILD_PATH=internal-procedures/<child>.md",
    "ROUTE_LAYOUT=SOURCE_OR_CANONICAL_PLUGIN_OR_STANDALONE",
    "ROUTE_POPULATION=EXACT_AND_COMPLETE",
    "references/planning-depth.md",
    "references/plan-lifecycle.md",
]
for token in governor_tokens:
    require(governor, token, governor_path.as_posix())

continuity_path = Path("skills/implementaudit/references/continuity.md")
continuity = continuity_path.read_text(encoding="utf-8")
for token in (
    "CHILD_SKILL_ROUTE=audit-state",
    "deterministic/governor-only recovery",
    "without an actual load",
):
    require(continuity, token, continuity_path.as_posix())

transcript_path = Path("skills/implementaudit/references/transcript-contract.md")
transcript = transcript_path.read_text(encoding="utf-8")
for token in (
    "## Child-skill routing observability",
    "CHILD_SKILL_ROUTE=<selected-child>",
    "actual child load",
    "governor-only cases emit no child announcement",
    "verified receipt precedes",
    "already-known cheap deterministic failure",
    "new constraint defeats the selected countermeasure",
    "fresh `audit-andon` route",
    "fresh `audit-implement` route",
):
    require(transcript, token, transcript_path.as_posix())

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

resolver="skills/implementaudit/scripts/resolve-internal-skill.py"
expected_source="$(python - <<'PY'
from pathlib import Path
print((Path('skills') / 'audit-state' / 'SKILL.md').resolve())
PY
)"
observed_source="$(python "$resolver" \
  --governor skills/implementaudit/SKILL.md \
  --child audit-state)"
[ "$observed_source" = "$expected_source" ] || {
  printf 'internal-skill-routing.test: source-layout resolution mismatch\n' >&2
  exit 1
}

standalone="$tmp/standalone-host/skills/implementaudit"
mkdir -p "$standalone/internal-procedures" "$standalone/scripts"
cp skills/implementaudit/SKILL.md "$standalone/SKILL.md"
cp "$resolver" "$standalone/scripts/resolve-internal-skill.py"
for child in audit-state audit-assess audit-implement audit-andon; do
  cp "skills/$child/SKILL.md" "$standalone/internal-procedures/$child.md"
done
mkdir -p "$tmp/standalone-host/skills/unrelated-skill"
printf '%s\n' '# unrelated installed skill' > "$tmp/standalone-host/skills/unrelated-skill/SKILL.md"
observed_standalone="$(python "$standalone/scripts/resolve-internal-skill.py" \
  --governor "$standalone/SKILL.md" \
  --child audit-andon)"
[ "$observed_standalone" = "$(python - "$standalone/internal-procedures/audit-andon.md" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve())
PY
)" ] || {
  printf 'internal-skill-routing.test: standalone-layout resolution mismatch\n' >&2
  exit 1
}

missing="$tmp/missing-host/skills/implementaudit"
mkdir -p "$(dirname "$missing")"
cp -R "$standalone" "$missing"
rm "$missing/internal-procedures/audit-state.md"
if python "$missing/scripts/resolve-internal-skill.py" \
  --governor "$missing/SKILL.md" \
  --child audit-assess >/dev/null 2>&1; then
  printf 'internal-skill-routing.test: incomplete standalone population unexpectedly resolved\n' >&2
  exit 1
fi

extra="$tmp/extra-host/skills/implementaudit"
mkdir -p "$(dirname "$extra")"
cp -R "$standalone" "$extra"
printf '%s\n' '# unexpected child' > "$extra/internal-procedures/audit-extra.md"
if python "$extra/scripts/resolve-internal-skill.py" \
  --governor "$extra/SKILL.md" \
  --child audit-assess >/dev/null 2>&1; then
  printf 'internal-skill-routing.test: extra standalone population unexpectedly resolved\n' >&2
  exit 1
fi

plugin="$tmp/ambiguous-host/plugins/implementaudit"
mkdir -p "$plugin/skills"
cp -R skills/implementaudit "$plugin/skills/implementaudit"
for child in audit-state audit-assess audit-implement audit-andon; do
  cp -R "skills/$child" "$plugin/skills/$child"
done
mkdir -p "$tmp/ambiguous-host/skills"
cp -R "$standalone" "$tmp/ambiguous-host/skills/implementaudit"
if python "$plugin/skills/implementaudit/scripts/resolve-internal-skill.py" \
  --governor "$plugin/skills/implementaudit/SKILL.md" \
  --child audit-state >/dev/null 2>&1; then
  printf 'internal-skill-routing.test: ambiguous plugin/standalone precedence unexpectedly resolved\n' >&2
  exit 1
fi

printf 'internal-skill-routing.test: resolver controls ok\n'

python - <<'PY'
from __future__ import annotations

from dataclasses import dataclass


CHILDREN = {"audit-state", "audit-assess", "audit-implement", "audit-andon"}


@dataclass(frozen=True)
class Event:
    kind: str
    value: str = ""
    message: int = 0


def accepts(events: list[Event]) -> bool:
    loads = [(index, event) for index, event in enumerate(events) if event.kind == "child-loaded"]
    announces = [(index, event) for index, event in enumerate(events) if event.kind == "route-announcement"]
    if not loads:
        return not announces
    if len(loads) != 1 or len(announces) != 1:
        return False
    load_index, load = loads[0]
    announce_index, announce = announces[0]
    if load.value not in CHILDREN or announce.value != load.value or announce_index <= load_index:
        return False
    if load.value == "audit-state":
        receipts = [(index, event) for index, event in enumerate(events) if event.kind == "verified-receipt"]
        if len(receipts) != 1 or receipts[0][0] >= load_index:
            return False
        first_permitted_message = min(
            (event.message for index, event in enumerate(events)
             if index > receipts[0][0] and event.kind == "assistant-narration"),
            default=announce.message,
        )
        if announce.message != first_permitted_message:
            return False
    return True


cases = {
    "state-route-after-receipt-visible": (
        True,
        [
            Event("verified-receipt"),
            Event("child-loaded", "audit-state"),
            Event("route-announcement", "audit-state", 1),
            Event("assistant-narration", message=1),
        ],
    ),
    "state-route-before-receipt": (
        False,
        [
            Event("child-loaded", "audit-state"),
            Event("route-announcement", "audit-state", 1),
            Event("verified-receipt"),
        ],
    ),
    "state-route-announced-late": (
        False,
        [
            Event("verified-receipt"),
            Event("child-loaded", "audit-state"),
            Event("assistant-narration", message=1),
            Event("route-announcement", "audit-state", 2),
        ],
    ),
    "governor-only-equivalent-reasoning": (
        True,
        [Event("verified-receipt"), Event("assistant-narration", "state-like", 1)],
    ),
    "false-route-announcement": (
        False,
        [Event("route-announcement", "audit-state", 1)],
    ),
    "loaded-child-missing-announcement": (
        False,
        [Event("child-loaded", "audit-assess"), Event("assistant-narration", message=1)],
    ),
    "wrong-child-announced": (
        False,
        [
            Event("child-loaded", "audit-assess"),
            Event("route-announcement", "audit-implement", 1),
        ],
    ),
    "assess-route-visible": (
        True,
        [Event("child-loaded", "audit-assess"), Event("route-announcement", "audit-assess", 1)],
    ),
    "implement-route-visible": (
        True,
        [Event("child-loaded", "audit-implement"), Event("route-announcement", "audit-implement", 1)],
    ),
    "andon-route-visible": (
        True,
        [Event("child-loaded", "audit-andon"), Event("route-announcement", "audit-andon", 1)],
    ),
}

for name, (expected, events) in cases.items():
    observed = accepts(events)
    if observed != expected:
        raise SystemExit(
            f"internal-skill-routing.test: observability case {name}: "
            f"expected {expected}, observed {observed}"
        )

print(f"internal-skill-routing.test: routing observability controls ok ({len(cases)}/{len(cases)})")


def accepts_secondary_abnormality(events: list[Event]) -> bool:
    active = ""
    last_kind = ""
    defeated = False
    andon_after_defeat = False
    repair_warranted = False
    implement_after_repair = False
    for index, event in enumerate(events):
        if event.kind == "governor-route":
            if active or event.value not in CHILDREN:
                return False
        elif event.kind == "child-loaded":
            if active or last_kind != "governor-route" or events[index - 1].value != event.value:
                return False
            active = event.value
            if defeated and event.value == "audit-andon":
                andon_after_defeat = True
            if repair_warranted and event.value == "audit-implement":
                implement_after_repair = True
        elif event.kind == "verification-result":
            if active != "audit-implement":
                return False
            defeated = event.value == "countermeasure-defeated"
        elif event.kind == "diagnosis":
            if active != "audit-andon":
                return False
            repair_warranted = event.value == "repair-warranted"
        elif event.kind == "child-return":
            if not active:
                return False
            active = ""
        elif event.kind == "governor-rederive":
            if active or last_kind != "child-return":
                return False
        elif event.kind == "consequential-action":
            if active or last_kind != "governor-rederive":
                return False
        else:
            return False
        last_kind = event.kind
    if active:
        return False
    if defeated and not andon_after_defeat:
        return False
    if repair_warranted and not implement_after_repair:
        return False
    return True


secondary_cases = {
    "known-cheap-report-needs-no-model-child": (
        True,
        [
            Event("governor-route", "audit-implement"),
            Event("child-loaded", "audit-implement"),
            Event("verification-result", "known-deterministic"),
            Event("child-return"),
            Event("governor-rederive"),
        ],
    ),
    "new-constraint-defeats-countermeasure-routes-andon": (
        True,
        [
            Event("governor-route", "audit-implement"),
            Event("child-loaded", "audit-implement"),
            Event("verification-result", "countermeasure-defeated"),
            Event("child-return"),
            Event("governor-rederive"),
            Event("governor-route", "audit-andon"),
            Event("child-loaded", "audit-andon"),
            Event("diagnosis", "no-repair"),
            Event("child-return"),
            Event("governor-rederive"),
        ],
    ),
    "andon-warrants-fresh-governor-routed-implement": (
        True,
        [
            Event("governor-route", "audit-implement"),
            Event("child-loaded", "audit-implement"),
            Event("verification-result", "countermeasure-defeated"),
            Event("child-return"),
            Event("governor-rederive"),
            Event("governor-route", "audit-andon"),
            Event("child-loaded", "audit-andon"),
            Event("diagnosis", "repair-warranted"),
            Event("child-return"),
            Event("governor-rederive"),
            Event("governor-route", "audit-implement"),
            Event("child-loaded", "audit-implement"),
            Event("child-return"),
            Event("governor-rederive"),
        ],
    ),
    "direct-child-to-child-is-red": (
        False,
        [
            Event("governor-route", "audit-implement"),
            Event("child-loaded", "audit-implement"),
            Event("verification-result", "countermeasure-defeated"),
            Event("child-loaded", "audit-andon"),
        ],
    ),
    "v2-return-cannot-authorize-action": (
        False,
        [
            Event("governor-route", "audit-implement"),
            Event("child-loaded", "audit-implement"),
            Event("verification-result", "evidential-support-v2"),
            Event("child-return"),
            Event("consequential-action"),
        ],
    ),
    "v2-return-followed-by-fresh-governor-decision": (
        True,
        [
            Event("governor-route", "audit-implement"),
            Event("child-loaded", "audit-implement"),
            Event("verification-result", "evidential-support-v2"),
            Event("child-return"),
            Event("governor-rederive"),
            Event("consequential-action"),
        ],
    ),
}

for name, (expected, events) in secondary_cases.items():
    observed = accepts_secondary_abnormality(events)
    if observed != expected:
        raise SystemExit(
            f"internal-skill-routing.test: secondary abnormality case {name}: "
            f"expected {expected}, observed {observed}"
        )

print(
    "internal-skill-routing.test: secondary abnormality controls ok "
    f"({len(secondary_cases)}/{len(secondary_cases)})"
)
PY

python - <<'PY'
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


SCHEMA_START = "<!-- AUDIT_IMPLEMENT_EVIDENTIAL_SUPPORT_V2_SCHEMA_START -->"
SCHEMA_END = "<!-- AUDIT_IMPLEMENT_EVIDENTIAL_SUPPORT_V2_SCHEMA_END -->"
SCHEMA_ID = "implementaudit.audit-implement.evidential-support.v2"
FIELDS = {
    "schema",
    "audit_object",
    "proposition",
    "evidence_id",
    "evidence_sha256",
    "evidence_kind",
    "support",
    "authority_ceiling",
}
SUPPORT_STATES = {
    "established",
    "contradicted",
    "insufficient",
    "not-applicable",
}
EVIDENCE_KINDS = {
    "exact-observation",
    "absence",
    "attempt",
    "receipt",
    "package-membership",
    "nearby-release-claim",
}


def fail(message: str) -> None:
    raise SystemExit(f"internal-skill-routing.test: evidential support: {message}")


def load_schema() -> dict[str, Any] | None:
    text = Path("skills/audit-implement/SKILL.md").read_text(encoding="utf-8")
    if SCHEMA_START not in text or SCHEMA_END not in text:
        return None
    block = text.split(SCHEMA_START, 1)[1].split(SCHEMA_END, 1)[0]
    match = re.fullmatch(r"\s*```json\s*\n(.*?)\n```\s*", block, re.DOTALL)
    if not match:
        fail("v2 schema block is not one JSON code fence")
    try:
        schema = json.loads(match.group(1))
    except (json.JSONDecodeError, UnicodeError) as exc:
        fail(f"v2 schema block is malformed: {exc}")
    if not isinstance(schema, dict):
        fail("v2 schema block is not an object")
    return schema


schema = load_schema()
observed_states = (
    set(schema.get("properties", {}).get("support", {}).get("enum", []))
    if schema is not None
    else {"neutral"}
)
if observed_states != SUPPORT_STATES:
    fail(
        "exact non-release proposition states collapse: "
        f"expected={sorted(SUPPORT_STATES)} observed={sorted(observed_states)}"
    )

if schema.get("$id") != SCHEMA_ID:
    fail("v2 schema identity drift")
if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
    fail("v2 schema must be a closed object")
if set(schema.get("required", [])) != FIELDS:
    fail("v2 required-field population drift")
properties = schema.get("properties")
if not isinstance(properties, dict) or set(properties) != FIELDS:
    fail("v2 property population drift")
if properties["schema"].get("const") != SCHEMA_ID:
    fail("v2 record schema discriminator drift")
if properties["evidence_kind"].get("enum") != sorted(EVIDENCE_KINDS):
    fail("v2 evidence-kind population drift")
if properties["authority_ceiling"].get("const") != "none":
    fail("v2 authority ceiling must remain none")

governor = Path("skills/implementaudit/SKILL.md").read_text(encoding="utf-8")
for token in (
    "CHILD_RESULT_AUTHORITY=NONE",
    "CHILD_RESULT_CLOSURE=NONE",
    "A child result returns here as evidence input",
    "governor re-derives current state before any later route or transition",
):
    if token not in governor:
        fail(f"governor envelope missing {token}")


@dataclass(frozen=True)
class BoundEvidence:
    audit_object: str
    proposition: str
    evidence_id: str
    evidence_sha256: str
    evidence_kind: str


def pairs_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate field: {key}")
        result[key] = value
    return result


def parse_return(raw: bytes, bound: BoundEvidence) -> tuple[str, str] | None:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return None
    if not text or "\x00" in text or "\x7f" in text:
        return None
    if text.lstrip()[:1] not in "{[":
        if any(ord(char) < 0x20 and char not in "\n\r\t" for char in text):
            return None
        return ("v1-neutral", text)
    try:
        record = json.loads(text, object_pairs_hook=pairs_without_duplicates)
    except (json.JSONDecodeError, UnicodeError, ValueError):
        return None
    if not isinstance(record, dict) or set(record) != FIELDS:
        return None
    if record.get("schema") != SCHEMA_ID:
        return None
    for field in FIELDS - {"schema"}:
        if not isinstance(record.get(field), str) or not record[field]:
            return None
    if record["authority_ceiling"] != "none":
        return None
    if record["support"] not in SUPPORT_STATES:
        return None
    if record["evidence_kind"] not in EVIDENCE_KINDS:
        return None
    if not re.fullmatch(r"[0-9a-f]{64}", record["evidence_sha256"]):
        return None
    if any(
        record[field] != getattr(bound, field)
        for field in (
            "audit_object",
            "proposition",
            "evidence_id",
            "evidence_sha256",
            "evidence_kind",
        )
    ):
        return None
    if record["support"] == "established" and record["evidence_kind"] != "exact-observation":
        return None
    return ("v2", record["support"])


bound = BoundEvidence(
    audit_object="tdqyq:run-v041:hc-h3",
    proposition="source:non-release:route-envelope-v2",
    evidence_id="evidence:hc-h3:exact-observation",
    evidence_sha256="5f" * 32,
    evidence_kind="exact-observation",
)
base = {
    "schema": SCHEMA_ID,
    "audit_object": bound.audit_object,
    "proposition": bound.proposition,
    "evidence_id": bound.evidence_id,
    "evidence_sha256": bound.evidence_sha256,
    "evidence_kind": bound.evidence_kind,
    "support": "insufficient",
    "authority_ceiling": "none",
}

for state in sorted(SUPPORT_STATES):
    record = dict(base, support=state)
    observed = parse_return(json.dumps(record, separators=(",", ":")).encode(), bound)
    if observed != ("v2", state):
        fail(f"v2 state {state} is not independently representable: {observed!r}")

negative_records: dict[str, dict[str, Any]] = {
    "unknown-field": dict(base, unexpected="value"),
    "missing-field": {key: value for key, value in base.items() if key != "proposition"},
    "wrong-schema": dict(base, schema="implementaudit.audit-implement.evidential-support.v1"),
    "wrong-audit-object": dict(base, audit_object="tdqyq:other"),
    "wrong-proposition": dict(base, proposition="release:nearby"),
    "wrong-evidence-id": dict(base, evidence_id="evidence:other"),
    "wrong-evidence-digest": dict(base, evidence_sha256="6a" * 32),
    "malformed-evidence-digest": dict(base, evidence_sha256="5F" * 32),
    "wrong-evidence-kind": dict(base, evidence_kind="receipt"),
    "unknown-support-state": dict(base, support="supported"),
    "authority-bearing-ceiling": dict(base, authority_ceiling="mutation"),
    "authority-bearing-output": dict(base, authorization="commit"),
}
for name, record in negative_records.items():
    raw = json.dumps(record, separators=(",", ":")).encode()
    if parse_return(raw, bound) is not None:
        fail(f"negative control accepted: {name}")

malformed_controls = {
    "invalid-utf8": b"\xff",
    "nul-byte": b'{"schema":"x"}\x00',
    "truncated-json": b'{"schema":',
    "json-array": b"[]",
    "duplicate-field": (
        b'{"schema":"' + SCHEMA_ID.encode() + b'","schema":"' + SCHEMA_ID.encode() + b'"}'
    ),
}
for name, raw in malformed_controls.items():
    if parse_return(raw, bound) is not None:
        fail(f"malformed control accepted: {name}")

neutral_kinds = {
    "absence",
    "attempt",
    "receipt",
    "package-membership",
    "nearby-release-claim",
}
for kind in sorted(neutral_kinds):
    kind_bound = BoundEvidence(
        audit_object=bound.audit_object,
        proposition=bound.proposition,
        evidence_id=f"evidence:hc-h3:{kind}",
        evidence_sha256=bound.evidence_sha256,
        evidence_kind=kind,
    )
    record = dict(
        base,
        evidence_id=kind_bound.evidence_id,
        evidence_kind=kind,
        support="established",
    )
    if parse_return(json.dumps(record, separators=(",", ":")).encode(), kind_bound) is not None:
        fail(f"neutral evidence kind became supported: {kind}")

legacy_controls = (
    "established",
    "attempt succeeded",
    "receipt=receipt:hc-h3",
    "package membership includes audit-implement",
    "nearby release claim passed",
)
for raw_text in legacy_controls:
    observed = parse_return(raw_text.encode(), bound)
    if observed != ("v1-neutral", raw_text):
        fail(f"v1 neutral compatibility drift: {raw_text!r} -> {observed!r}")

print(
    "internal-skill-routing.test: evidential support controls ok "
    f"({len(SUPPORT_STATES)} states, {len(negative_records)} bound negatives, "
    f"{len(malformed_controls)} malformed, {len(neutral_kinds)} neutral v2, "
    f"{len(legacy_controls)} v1 controls)"
)
PY
