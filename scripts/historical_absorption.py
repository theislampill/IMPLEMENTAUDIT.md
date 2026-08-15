#!/usr/bin/env python3
"""Read-only historical absorption baseline over the frozen 658-row crosswalk."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


BASE = Path("docs/research/implementaudit/historical-absorption-baseline")
SOURCE_IDENTITY = BASE / "SOURCE_IDENTITY.json"
BASELINE = BASE / "HISTORICAL_ABSORPTION_BASELINE.json"
PROPERTY_INDEX = Path("docs/research/genealogy/PROPERTY_MASTER_INDEX.json")

LOGICAL_SOURCE_PATH = (
    ".IMPLEMENTAUDIT/runs/v0400-s3e-release-controller-KYxl3h/architecture/"
    "composable-skills-library-audit/"
    "V0400_CANONICAL_RESEARCH_PROPERTY_RXX_CROSSWALK.pre-post-implementation.json"
)

COMPLETE = "HISTORICALLY_ABSORBED_COMPLETE"
PARTIAL = "HISTORICALLY_ABSORBED_PARTIAL"
AMEND = "HISTORICALLY_EXISTING_OWNER_NEEDS_AMENDMENT"
RESIDUAL = "HISTORICALLY_LINEAGE_NATIVE_RESIDUAL"
REACHABILITY = "HISTORICALLY_IMPLEMENTATION_OR_REACHABILITY_GAP"
BEHAVIOURAL = "HISTORICALLY_BEHAVIOURAL_PROOF_GAP"
ASSUMPTION = "HISTORICALLY_ASSUMPTION_BOUND"
DOMAIN = "HISTORICALLY_DOMAIN_BOUND"
REJECTED = "HISTORICALLY_REJECTED_OR_SUPERSEDED"
UNRESOLVED = "HISTORICALLY_UNRESOLVED"

SOURCE_CLASS_MAP = {
    "ALREADY_STRICTLY_STRONGER": COMPLETE,
    "STRONGER_BY_NATIVE_COMPOSITION": COMPLETE,
    "EQUIVALENT": COMPLETE,
    "PUBLIC_DOCUMENTATION_ONLY": PARTIAL,
    "UNIMPLEMENTED_OR_BOUNDED__NO_NEW_PROOF_CLAIM": PARTIAL,
    "EXISTING_RXX_NEEDS_AMENDMENT": AMEND,
    "LINEAGE_RXX_NATIVE_RESIDUAL": RESIDUAL,
    "IMPLEMENTATION_OR_REACHABILITY_REPAIR": REACHABILITY,
    "BEHAVIOURAL_PROOF_GAP": BEHAVIOURAL,
    "UNRESOLVED_BOUNDED_BEHAVIOURAL_PROOF_GAP": BEHAVIOURAL,
    "ASSUMPTION_BOUND": ASSUMPTION,
    "DOMAIN_OR_HIGH_CONSEQUENCE_BOUND": DOMAIN,
    "REJECTED_SOURCE_CEREMONY_OR_WEAKER_FORM": REJECTED,
    "SUPERSEDED_BY_STRONGER_NATIVE_FORM": REJECTED,
    "UNRESOLVED": UNRESOLVED,
    "UNRESOLVED_DETERMINISTIC_FIXTURE_GAP": UNRESOLVED,
    "UNRESOLVED_SOURCE_STATIC_PROOF_GAP": UNRESOLVED,
}

LAW_CLASS_MAP = {
    "ASC": COMPLETE,
    "AEDF": COMPLETE,
    "PC": AMEND,
    "CSO": DOMAIN,
    "REE": REJECTED,
    "CNA": REJECTED,
}

EXPECTED_COUNTS = {
    COMPLETE: 221,
    PARTIAL: 41,
    AMEND: 114,
    RESIDUAL: 59,
    REACHABILITY: 2,
    BEHAVIOURAL: 8,
    ASSUMPTION: 40,
    DOMAIN: 77,
    REJECTED: 79,
    UNRESOLVED: 17,
}

LANE_TO_LINEAGE = {
    "CSS_COGNITIVE": "EVOLVED_COGNITIVE_SYSTEMS_ENGINEERING",
    "CSS_STATISTICAL": "EVOLVED_STATISTICAL_ENGINEERING",
    "CSS_SAFETY": "EVOLVED_SYSTEMS_SAFETY",
    "SSD_SYSTEMS": "EVOLVED_SYSTEMS_ENGINEERING",
    "SSD_SECURITY": "EVOLVED_SYSTEMS_SECURITY_ENGINEERING",
    "SSD_DECISION_OPERATIONS": "EVOLVED_DECISION_AND_OPERATIONS_ENGINEERING",
    "DRF_DISTRIBUTED": "EVOLVED_DISTRIBUTED_SYSTEMS_ENGINEERING",
    "DRF_RELIABILITY_MAINTAINABILITY": "EVOLVED_RELIABILITY_AND_MAINTAINABILITY_ENGINEERING",
    "DRF_FORMAL_VERIFICATION": "EVOLVED_FORMAL_METHODS_AND_VERIFICATION_ENGINEERING",
    "LAW_LEAN": "EVOLVED_LEAN",
    "LAW_AGILE": "EVOLVED_AGILE",
    "LAW_WATERFALL": "EVOLVED_WATERFALL",
}

INDICATOR_PATTERNS = {
    "MONOLITHIC_CONTEXT_COST": re.compile(
        r"(?i)(?:monolith(?:ic)?[^.;]{0,80}context|context[^.;]{0,80}monolith(?:ic)?|"
        r"context (?:cost|load|budget|overload)|large model context)"
    ),
    "ABSENT_PROGRESSIVE_DISCLOSURE_ROUTE": re.compile(
        r"(?i)(?:progressive disclosure|progressive load|progressive route|progressively loaded)"
    ),
    "ABSENT_STATE_REPRESENTATION": re.compile(
        r"(?i)(?:state (?:representation|field|model)[^.;]*(?:missing|absent|not)|"
        r"(?:missing|absent)[^.;]*state (?:representation|field|model)|mode representation[^.;]*(?:missing|absent|not))"
    ),
    "ABSENT_DETERMINISTIC_DISCRIMINATOR": re.compile(
        r"(?i)(?:deterministic (?:fixture|discriminator|checker|proof)[^.;]*(?:gap|missing|absent|not\b)|"
        r"(?:missing|absent) deterministic (?:fixture|discriminator|checker|proof|predicate)|UNRESOLVED_DETERMINISTIC_FIXTURE_GAP|"
        r"UNRESOLVED_SOURCE_STATIC_PROOF_GAP|missing native predicate)"
    ),
    "ABSENT_AUTHORITY_OR_CURRENTNESS_MECHANISM": re.compile(
        r"(?i)(?:authority[^.;]*(?:gap|missing|absent|not reestablished)|"
        r"currentness[^.;]*(?:gap|missing|absent|not reestablished)|"
        r"(?:missing|absent)[^.;]*currentness|stale authority)"
    ),
    "ABSENT_COMPOSABLE_COGNITIVE_OWNER": re.compile(
        r"(?i)(?:composable[^.;]*cognit|cognitive owner|model-facing[^.;]*owner|"
        r"cognit[^.;]*(?:missing|absent|not routed))"
    ),
    "EXCESSIVE_CEREMONY_OR_COST": re.compile(
        r"(?i)(?:excessive ceremony|ceremony[^.;]*(?:cost|overhead)|"
        r"cost[^.;]*(?:exceeds|outweighs)|not worth the cost)"
    ),
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


def _flatten(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            result.extend(_flatten(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.extend(_flatten(child, f"{prefix}[{index}]"))
    else:
        result.append((prefix, str(value)))
    return result


def _historical_record(row: dict[str, Any]) -> dict[str, Any]:
    source = row["SOURCE_RECORD"]
    lane = row["RESEARCH_LANE"]
    if "MASTER_PROPERTY_RECORD" in source:
        master = source["MASTER_PROPERTY_RECORD"]
        required = master["master_required_fields"]
        disposition = required["01_source_lineage_disposition"]["implementaudit_disposition"]
        if disposition not in SOURCE_CLASS_MAP:
            raise ValueError(f"unmapped source disposition: {disposition}")
        source_schema = master.get("source_schema", {})
        status = required["01_source_lineage_disposition"].get("source_status")
        owner = required.get("02_native_implementaudit_owner_composition", {})
        evidence_sections = {
            key: required[key]
            for key in (
                "03_implementation_state",
                "04_package_reachability_activation_state",
                "05_existing_rxx_amendment_disposition",
                "06_lineage_rxx_residual_disposition",
                "11_implementation_delta_or_no_change_justification",
            )
            if key in required
        }
        evidence_sections["source_status"] = status
        return {
            "source_disposition": disposition,
            "historical_classification": SOURCE_CLASS_MAP[disposition],
            "source_status": status,
            "historical_owner_evidence": owner,
            "evidence_sections": evidence_sections,
            "source_row_sha256": source.get("SOURCE_ROW_SHA256"),
            "source_lineage_id": master.get("source_lineage_id", LANE_TO_LINEAGE[lane]),
            "source_schema_status": source_schema.get("SOURCE_STATUS"),
        }

    original = source["ORIGINAL_ROW"]
    disposition = original["disposition"]
    if disposition not in LAW_CLASS_MAP:
        raise ValueError(f"unmapped LAW disposition: {disposition}")
    row_bytes = json.dumps(
        original, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return {
        "source_disposition": disposition,
        "historical_classification": LAW_CLASS_MAP[disposition],
        "source_status": original.get("status"),
        "historical_owner_evidence": original.get("owners"),
        "evidence_sections": {
            "status": original.get("status"),
            "disposition": disposition,
            "delta": original.get("delta"),
        },
        "source_row_sha256": _sha256(row_bytes),
        "source_lineage_id": LANE_TO_LINEAGE[lane],
        "source_schema_status": original.get("status"),
    }


def _constraint_indicators(record: dict[str, Any]) -> list[dict[str, Any]]:
    if record["historical_classification"] == COMPLETE:
        return []
    flattened = _flatten(record["evidence_sections"])
    indicators: list[dict[str, Any]] = []
    for indicator, pattern in INDICATOR_PATTERNS.items():
        matches = [
            {"field": field, "value": value}
            for field, value in flattened
            if pattern.search(value)
        ]
        if indicator == "EXCESSIVE_CEREMONY_OR_COST" and record["source_schema_status"] in {
            "CEREMONY_NOT_GENERAL_PROPERTY",
            "FROZEN_CEREMONY",
        }:
            matches.append(
                {
                    "field": "source_schema_status",
                    "value": str(record["source_schema_status"]),
                }
            )
        unique: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for match in matches:
            key = (match["field"], match["value"])
            if key not in seen:
                seen.add(key)
                unique.append(match)
        if unique:
            indicators.append(
                {
                    "indicator": indicator,
                    "basis": "EXPLICIT_HISTORICAL_GAP_OR_DISPOSITION_EVIDENCE",
                    "evidence": unique,
                }
            )
    return indicators


def build_baseline(root: Path, source_path: Path) -> dict[str, Any]:
    root = root.resolve()
    source_bytes = source_path.read_bytes()
    source_sha = _sha256(source_bytes)
    source = json.loads(source_bytes)
    if source.get("SCHEMA") != "implementaudit-v0400-canonical-research-rxx-crosswalk-v1":
        raise ValueError("historical crosswalk schema mismatch")
    source_rows = source.get("ROWS", [])
    if len(source_rows) != 658:
        raise ValueError(f"historical source denominator mismatch: {len(source_rows)}")

    index = json.loads((root / PROPERTY_INDEX).read_text(encoding="utf-8"))
    genealogy_keys = {row["global_property_key"] for row in index["properties"]}
    rows: list[dict[str, Any]] = []
    for index_value, source_row in enumerate(source_rows):
        record = _historical_record(source_row)
        key = f"{record['source_lineage_id']}::{source_row['PROPERTY_ID']}"
        if key not in genealogy_keys:
            raise ValueError(f"historical row does not resolve to genealogy index: {key}")
        indicators = _constraint_indicators(record)
        rows.append(
            {
                "global_property_key": key,
                "research_lane": source_row["RESEARCH_LANE"],
                "source_property_id": source_row["PROPERTY_ID"],
                "historical_property_name": source_row["PROPERTY_NAME"],
                "historical_source_disposition": record["source_disposition"],
                "historical_classification": record["historical_classification"],
                "historical_owner_evidence": record["historical_owner_evidence"],
                "constraint_indicators": indicators,
                "source_locator": {
                    "logical_path": LOGICAL_SOURCE_PATH,
                    "rows_index": index_value,
                    "source_row_sha256": record["source_row_sha256"],
                },
                "V0400_CHANGE_DISPOSITION": "DEFER_TO_V0410_BASELINE",
            }
        )

    class_counts = dict(sorted(Counter(row["historical_classification"] for row in rows).items()))
    if class_counts != dict(sorted(EXPECTED_COUNTS.items())):
        raise ValueError(f"historical classification census mismatch: {class_counts}")
    indicator_counts = Counter()
    for row in rows:
        indicator_counts.update(item["indicator"] for item in row["constraint_indicators"])
    for indicator in INDICATOR_PATTERNS:
        indicator_counts.setdefault(indicator, 0)

    source_identity = {
        "schema": "implementaudit-historical-absorption-source-identity-v1",
        "logical_path": LOGICAL_SOURCE_PATH,
        "bytes": len(source_bytes),
        "sha256": source_sha,
        "source_schema": source["SCHEMA"],
        "source_state": source.get("STATE"),
        "source_generated_at_utc": source.get("GENERATED_AT_UTC"),
        "rows": len(source_rows),
        "authority_boundary": (
            "Frozen historical crosswalk occurrence only; it is not present-v0.4 implementation or reabsorption authority."
        ),
    }
    _write_json(root / SOURCE_IDENTITY, source_identity)
    identity_bytes = (root / SOURCE_IDENTITY).read_bytes()
    baseline = {
        "schema": "implementaudit-historical-absorption-baseline-v1",
        "status": "READ_ONLY_HISTORICAL_VIABILITY_CENSUS",
        "authority_boundary": (
            "Preserves prior dispositions without changing them. Every claim about whether v0.4 changes a disposition is deferred."
        ),
        "source_identity": {
            "path": SOURCE_IDENTITY.as_posix(),
            "bytes": len(identity_bytes),
            "sha256": _sha256(identity_bytes),
        },
        "classification_rules": {
            "source_dispositions": SOURCE_CLASS_MAP,
            "law_codes": LAW_CLASS_MAP,
        },
        "constraint_indicator_rules": {
            "scope": (
                "Non-complete rows only; explicit historical implementation, reachability, amendment, residual, "
                "delta or source-status evidence. Indicators are not v0.4 counterfactual decisions."
            ),
            "patterns": {key: pattern.pattern for key, pattern in INDICATOR_PATTERNS.items()},
        },
        "counts": {
            "properties": len(rows),
            "unique_global_property_keys": len({row["global_property_key"] for row in rows}),
            "historical_classifications": class_counts,
            "constraint_indicators": dict(sorted(indicator_counts.items())),
        },
        "deferrals": [
            "Whether released v0.4.0.0 changes any historical disposition: DEFER_TO_V0410_BASELINE",
            "Current owner, reachability, activation and behavioural proof: DEFER_TO_V0410_BASELINE",
            "Reabsorption, amendment, residual and runtime decisions: DEFER_TO_V0410_BASELINE",
        ],
        "rows": rows,
    }
    _write_json(root / BASELINE, baseline)
    return baseline


def check_baseline(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    for relative in (SOURCE_IDENTITY, BASELINE, PROPERTY_INDEX, BASE / "README.md"):
        if not (root / relative).is_file():
            errors.append(f"missing historical baseline file: {relative.as_posix()}")
    if errors:
        return errors
    identity_bytes = (root / SOURCE_IDENTITY).read_bytes()
    identity = json.loads(identity_bytes)
    baseline = json.loads((root / BASELINE).read_text(encoding="utf-8"))
    if baseline.get("source_identity", {}).get("sha256") != _sha256(identity_bytes):
        errors.append("historical source-identity digest mismatch")
    rows = baseline.get("rows", [])
    if len(rows) != 658 or len({row.get("global_property_key") for row in rows}) != 658:
        errors.append("historical baseline property denominator mismatch")
    counts = Counter(row.get("historical_classification") for row in rows)
    if dict(counts) != EXPECTED_COUNTS:
        errors.append("historical baseline classification counts mismatch")
    genealogy = json.loads((root / PROPERTY_INDEX).read_text(encoding="utf-8"))
    genealogy_keys = {row["global_property_key"] for row in genealogy["properties"]}
    if {row.get("global_property_key") for row in rows} != genealogy_keys:
        errors.append("historical baseline keys do not match the 658-property genealogy index")
    for row in rows:
        if row.get("V0400_CHANGE_DISPOSITION") != "DEFER_TO_V0410_BASELINE":
            errors.append(f"non-deferred v0.4 disposition: {row.get('global_property_key')}")
        for indicator in row.get("constraint_indicators", []):
            if not indicator.get("evidence"):
                errors.append(f"constraint indicator lacks evidence: {row.get('global_property_key')}")
    if identity.get("logical_path") != LOGICAL_SOURCE_PATH or identity.get("rows") != 658:
        errors.append("historical source identity is incomplete")
    return sorted(set(errors))
