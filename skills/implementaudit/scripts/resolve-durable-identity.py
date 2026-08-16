#!/usr/bin/env python3
"""Resolve IMPLEMENTAUDIT durable ordinal identities without allocating them."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REGISTRY = Path(__file__).resolve().parent.parent / "references" / "identity-namespaces.json"
CANONICAL_RE = re.compile(r"([RG])([0-9A-F]{4})")
LEGACY_ROCKSTAR_RE = re.compile(r"R([0-9]{2})")
LEGACY_GENERATION_RE = re.compile(r"e([1-9][0-9]*)")


def die(message: str) -> "NoReturn":
    raise SystemExit(f"resolve-durable-identity: {message}")


def load_registry() -> dict:
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        die(f"invalid registry: {exc}")
    expected_top = {"schema", "canonical", "namespaces", "non_namespaces"}
    if not isinstance(data, dict) or set(data) != expected_top:
        die("registry has the wrong top-level schema")
    if data["schema"] != "implementaudit.durable-identity-namespaces.v1":
        die("registry schema identity mismatch")
    canonical = data["canonical"]
    if canonical != {
        "form": "PREFIX_HEX4",
        "hex_digits": 4,
        "hex_case": "upper",
        "ordinal_min": 1,
        "ordinal_max": 65535,
    }:
        die("canonical format contract mismatch")
    namespaces = data["namespaces"]
    if not isinstance(namespaces, dict) or set(namespaces) != {"R", "G"}:
        die("registry must define exactly R and G")
    r = namespaces["R"]
    g = namespaces["G"]
    if (
        r.get("semantic_name") != "Rockstar"
        or r.get("meaning") != "durable governed-work identity"
        or r.get("allocation_owner") != "R0004"
        or r.get("allocated_ordinal_min") != 1
        or r.get("allocated_ordinal_max") != 55
        or r.get("next_unreserved_candidate") != "R0038"
        or r.get("legacy")
        != {
            "prefix": "R",
            "radix": 10,
            "digits": 2,
            "ordinal_min": 1,
            "ordinal_max": 55,
        }
    ):
        die("Rockstar namespace contract mismatch")
    if (
        g.get("semantic_name") != "continuity generation"
        or g.get("meaning") != "run-local continuity/currentness generation"
        or g.get("allocation_owner") != "controller and run-root state"
        or g.get("allocation_scope") != "run-local"
        or g.get("legacy")
        != {
            "prefix": "e",
            "radix": 10,
            "minimum_digits": 1,
            "ordinal_min": 1,
            "historical_alias_max_ordinal": 77,
        }
    ):
        die("continuity-generation namespace contract mismatch")
    if not isinstance(data["non_namespaces"], list) or not data["non_namespaces"]:
        die("non-namespace boundary is missing")
    return data


def format_identity(prefix: str, ordinal: int, registry: dict) -> str:
    canonical = registry["canonical"]
    if prefix not in registry["namespaces"]:
        die(f"unknown namespace prefix: {prefix}")
    if isinstance(ordinal, bool) or not canonical["ordinal_min"] <= ordinal <= canonical["ordinal_max"]:
        die(f"ordinal is outside HEX4 range: {ordinal}")
    return f"{prefix}{ordinal:04X}"


def canonicalize(value: str, registry: dict) -> tuple[str, int]:
    match = CANONICAL_RE.fullmatch(value)
    if match:
        prefix, payload = match.groups()
        ordinal = int(payload, 16)
        if ordinal < registry["canonical"]["ordinal_min"]:
            die("zero ordinal is not a durable identity")
        return prefix, ordinal
    match = LEGACY_ROCKSTAR_RE.fullmatch(value)
    if match:
        ordinal = int(match.group(1), 10)
        legacy = registry["namespaces"]["R"]["legacy"]
        if not legacy["ordinal_min"] <= ordinal <= legacy["ordinal_max"]:
            die(f"unknown legacy Rockstar alias: {value}")
        return "R", ordinal
    match = LEGACY_GENERATION_RE.fullmatch(value)
    if match:
        ordinal = int(match.group(1), 10)
        if ordinal > registry["canonical"]["ordinal_max"]:
            die(f"legacy generation exceeds HEX4 range: {value}")
        return "G", ordinal
    die(f"invalid durable identity: {value}")


def legacy_alias(prefix: str, ordinal: int, registry: dict) -> str:
    if prefix == "R":
        legacy = registry["namespaces"]["R"]["legacy"]
        if not legacy["ordinal_min"] <= ordinal <= legacy["ordinal_max"]:
            die("Rockstar has no allocated legacy alias")
        return f"R{ordinal:02d}"
    if prefix == "G":
        maximum = registry["namespaces"]["G"]["legacy"]["historical_alias_max_ordinal"]
        if ordinal > maximum:
            die("canonical-born generation has no historical eNN alias")
        return f"e{ordinal}"
    die(f"unknown namespace prefix: {prefix}")


def require_allocated(value: str, registry: dict) -> str:
    prefix, ordinal = canonicalize(value, registry)
    canonical = format_identity(prefix, ordinal, registry)
    if prefix == "R":
        namespace = registry["namespaces"]["R"]
        if not namespace["allocated_ordinal_min"] <= ordinal <= namespace["allocated_ordinal_max"]:
            die(f"Rockstar is not allocated: {canonical}")
    else:
        die("continuity allocation is run-local and cannot be asserted by the namespace resolver")
    return canonical


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true")
    group.add_argument("--canonical", metavar="IDENTITY")
    group.add_argument("--legacy", metavar="IDENTITY")
    group.add_argument("--ordinal", metavar="IDENTITY")
    group.add_argument("--require-allocated", metavar="IDENTITY")
    group.add_argument("--format", nargs=2, metavar=("PREFIX", "ORDINAL"))
    args = parser.parse_args()
    registry = load_registry()
    if args.validate:
        print("resolve-durable-identity: registry ok")
        return 0
    if args.format:
        prefix, raw_ordinal = args.format
        try:
            ordinal = int(raw_ordinal, 10)
        except ValueError:
            die(f"ordinal is not decimal input: {raw_ordinal}")
        print(format_identity(prefix, ordinal, registry))
        return 0
    value = args.canonical or args.legacy or args.ordinal or args.require_allocated
    assert value is not None
    if args.require_allocated:
        print(require_allocated(value, registry))
        return 0
    prefix, ordinal = canonicalize(value, registry)
    if args.canonical:
        print(format_identity(prefix, ordinal, registry))
    elif args.legacy:
        print(legacy_alias(prefix, ordinal, registry))
    else:
        print(ordinal)
    return 0


if __name__ == "__main__":
    sys.exit(main())
