#!/usr/bin/env python3
"""Validate one audit-implement return against exact governor bindings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any
import unicodedata


SCHEMA_ID = "implementaudit.audit-implement.evidential-support.v2"
OUTPUT_SCHEMA = "implementaudit.audit-implement.return-validation.v1"
FIELDS = (
    "schema",
    "audit_object",
    "proposition_domain",
    "proposition",
    "evidence_id",
    "evidence_sha256",
    "evidence_kind",
    "support",
    "authority_ceiling",
)
SUPPORT_STATES = {
    "established",
    "contradicted",
    "insufficient",
    "not-applicable",
}
EVIDENCE_KINDS = {
    "absence",
    "attempt",
    "exact-observation",
    "nearby-release-claim",
    "package-membership",
    "receipt",
}
LEGACY_NEUTRAL_TOKENS = {
    "established",
    "contradicted",
    "insufficient",
    "stale",
    "identity mismatch",
    "qualification gap",
    "unresolved",
    "boundary not supportable",
}
PROHIBITED_PROPOSITION = re.compile(
    r"^(?:release|currentness|lifecycle):",
    re.IGNORECASE | re.ASCII,
)


class ParsedPairs(list[tuple[str, Any]]):
    """Preserve object pairs so duplicate keys cannot collapse silently."""


def reject(reason: str) -> int:
    sys.stderr.buffer.write(f"validate-audit-implement-return: {reason}\n".encode("utf-8"))
    return 1


def emit(route: str, support: str) -> int:
    payload = {
        "schema": OUTPUT_SCHEMA,
        "route": route,
        "support": support,
    }
    sys.stdout.buffer.write(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("ascii") + b"\n"
    )
    return 0


def canonical_pairs(pairs: ParsedPairs) -> str:
    encoded: list[str] = []
    for key, value in pairs:
        encoded.append(
            json.dumps(key, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
            + ":"
            + json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        )
    return "{" + ",".join(encoded) + "}"


def has_decoded_control(value: Any) -> bool:
    if isinstance(value, str):
        return any(
            ord(character) <= 0x1F
            or ord(character) == 0x7F
            or unicodedata.category(character) in {"Cc", "Cf"}
            for character in value
        )
    if isinstance(value, ParsedPairs):
        return any(
            has_decoded_control(key) or has_decoded_control(item)
            for key, item in value
        )
    if isinstance(value, list):
        return any(has_decoded_control(item) for item in value)
    return False


def proposition_has_lexical_normal_form(proposition: str) -> bool:
    return (
        unicodedata.normalize("NFC", proposition) == proposition
        and not proposition[0].isspace()
        and not proposition[-1].isspace()
    )


def validate(raw: bytes, expected: argparse.Namespace) -> int:
    if not raw:
        return reject("empty")
    if any(byte < 0x20 or byte == 0x7F for byte in raw):
        return reject("control-byte")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return reject("utf8")

    if text in LEGACY_NEUTRAL_TOKENS:
        return emit("legacy-neutral-verification-only", "neutral")
    if text[:1] not in "{[":
        return reject("legacy-token")

    try:
        parsed = json.loads(text, object_pairs_hook=ParsedPairs)
    except (json.JSONDecodeError, UnicodeError, ValueError):
        return reject("json")
    if not isinstance(parsed, ParsedPairs):
        return reject("object")

    keys = [key for key, _value in parsed]
    duplicates = {key for key in keys if keys.count(key) > 1}
    if duplicates:
        return reject("duplicate-field")
    if has_decoded_control(parsed):
        return reject("decoded-control")
    record = dict(parsed)
    if set(record) != set(FIELDS):
        return reject("field-population")
    if tuple(record) != FIELDS:
        return reject("noncanonical")
    if not all(isinstance(record[field], str) and record[field] for field in FIELDS):
        return reject("field-type")
    if text != canonical_pairs(parsed):
        return reject("noncanonical")
    if record["schema"] != SCHEMA_ID:
        return reject("schema")
    if record["proposition_domain"] != "non-release":
        return reject("proposition-domain")
    if record["support"] not in SUPPORT_STATES:
        return reject("support")
    if record["evidence_kind"] not in EVIDENCE_KINDS:
        return reject("evidence-kind")
    if record["authority_ceiling"] != "none":
        return reject("authority-ceiling")
    if not re.fullmatch(r"[0-9a-f]{64}", record["evidence_sha256"]):
        return reject("evidence-sha256")
    if not proposition_has_lexical_normal_form(record["proposition"]):
        return reject("proposition-normal-form")

    bindings = {
        "audit_object": expected.expect_audit_object,
        "proposition_domain": expected.expect_proposition_domain,
        "proposition": expected.expect_proposition,
        "evidence_id": expected.expect_evidence_id,
        "evidence_sha256": expected.expect_evidence_sha256,
        "evidence_kind": expected.expect_evidence_kind,
    }
    for field, value in bindings.items():
        if record[field] != value:
            return reject(f"binding-{field}")

    if record["support"] == "established":
        if record["evidence_kind"] != "exact-observation":
            return reject("established-evidence-kind")
        if (
            record["proposition_domain"] != "non-release"
            or PROHIBITED_PROPOSITION.search(record["proposition"])
        ):
            return reject("established-proposition-domain")

    return emit("v2-evidence-input", record["support"])


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--expect-audit-object", required=True)
    parser.add_argument("--expect-proposition-domain", required=True)
    parser.add_argument("--expect-proposition", required=True)
    parser.add_argument("--expect-evidence-id", required=True)
    parser.add_argument("--expect-evidence-sha256", required=True)
    parser.add_argument("--expect-evidence-kind", required=True)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        raw = args.input.read_bytes() if args.input is not None else sys.stdin.buffer.read()
    except OSError as exc:
        sys.stderr.buffer.write(f"validate-audit-implement-return: input: {exc}\n".encode("utf-8"))
        return 2
    return validate(raw, args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
