"""Prospective evidence-only codec for a fixed ordinary public report."""

import hashlib
import json
import re


WIRE_SCHEMA = "g132.selected-public-static-compact-observation.v2-draft"
DERIVED = ("expected_provider", "layout", "cache", "graph", "pin_comparisons", "counters")
DELIVERY_CAP = 2097152
ENCODER = json.JSONEncoder(sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)


def require(condition, code):
    if not condition:
        raise ValueError(code)


def descriptor(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def bounded_canonical(value, maximum, refusal):
    """Encode the original canonical representation with a hard output ceiling."""
    encoded = bytearray()
    for chunk in ENCODER.iterencode(value):
        raw = chunk.encode("ascii")
        require(len(encoded) + len(raw) < maximum, refusal)
        encoded.extend(raw)
    encoded.append(10)
    return bytes(encoded)


def wire_limits(owner, contract, maximum):
    legacy = owner.bounded_limits(contract)["report_bytes"]
    require(type(maximum) is int and 256 <= maximum <= legacy <= DELIVERY_CAP, "WIRE_LIMIT")
    return legacy


def pack(legacy, owner, contract, wheel, cache, maximum):
    """Encode only an exact canonical report accepted by the existing receiver."""
    legacy_limit = wire_limits(owner, contract, maximum)
    require(type(legacy) is bytes and len(legacy) <= legacy_limit, "LEGACY_BOUND")
    owner.receive(legacy, contract, wheel, cache)
    report = owner.strict_json(legacy)
    require(bounded_canonical(report, legacy_limit, "LEGACY_BOUND") == legacy, "NONCANONICAL_LEGACY")
    derived = {}
    for name in DERIVED:
        raw = bounded_canonical(report.pop(name), legacy_limit, "SECTION_BOUND")
        derived[name] = descriptor(raw)
    wire = {"schema": WIRE_SCHEMA, "report": report, "derived": derived, "legacy": descriptor(legacy)}
    return bounded_canonical(wire, maximum, "WIRE_BOUND")


def valid_descriptor(row, limit):
    return (type(row) is dict and set(row) == {"bytes", "sha256"}
            and type(row["bytes"]) is int and 0 < row["bytes"] <= limit
            and type(row["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None)


def check_observed(owner, report, contract):
    owner.validate_export_shapes(report, contract)
    limits = owner.bounded_limits(contract)
    counts = owner.budget_counts(report, contract)
    for key in ("entries", "total_bytes", "unique_bytes", "mounted_bytes", "read_bytes"):
        require(type(counts[key]) is int and 0 <= counts[key] <= limits[key], "OBSERVATION_BOUND")


def expand(raw, owner, contract, wheel, cache, maximum):
    """Decode and run the independent existing receiver over the exact v1 bytes."""
    legacy_limit = wire_limits(owner, contract, maximum)
    require(type(raw) is bytes and len(raw) <= maximum, "WIRE_BOUND")
    wire = owner.strict_json(raw)
    require(type(wire) is dict and set(wire) == {"schema", "report", "derived", "legacy"}
            and wire["schema"] == WIRE_SCHEMA, "WIRE_SCHEMA")
    require(bounded_canonical(wire, maximum, "WIRE_BOUND") == raw, "NONCANONICAL_WIRE")
    derived, report = wire["derived"], wire["report"]
    require(type(derived) is dict and set(derived) == set(DERIVED)
            and type(report) is dict and not set(report).intersection(DERIVED)
            and report.get("schema") == owner.SCHEMA, "DERIVED_POPULATION")
    legacy_pin = wire["legacy"]
    require(valid_descriptor(legacy_pin, legacy_limit), "DESCRIPTOR_BOUND")
    require(all(valid_descriptor(row, legacy_pin["bytes"]) for row in derived.values()),
            "DESCRIPTOR_BOUND")
    require(sum(row["bytes"] for row in derived.values()) <= legacy_pin["bytes"], "SECTION_BOUND")
    report.update(dict.fromkeys(DERIVED))
    check_observed(owner, report, contract)
    report["expected_provider"] = owner.expected_layer(contract, wheel, report["objects"])
    report["layout"] = owner.make_layout(report, contract)
    report["cache"] = owner.cache_join(report, contract, cache)
    report["graph"] = owner.join_graph(report, contract, cache)
    report["pin_comparisons"] = owner.compare_pins(report, contract)
    report["counters"] = dict(owner.budget_counts(report, contract), edges=len(report["graph"]["edges"]))
    for name, want in derived.items():
        section = bounded_canonical(report[name], want["bytes"], "DERIVED_COMMITMENT")
        require(descriptor(section) == want, "DERIVED_COMMITMENT")
    legacy = bounded_canonical(report, legacy_pin["bytes"], "LEGACY_BOUND")
    require(descriptor(legacy) == legacy_pin, "LEGACY_COMMITMENT")
    return legacy, owner.receive(legacy, contract, wheel, cache)


def delivery_manifest(payloads, maximum):
    """Bind exact ordinary fixture members under the uncompressed delivery cap."""
    require(type(maximum) is int and 0 < maximum <= DELIVERY_CAP, "DELIVERY_LIMIT")
    require(type(payloads) is dict and payloads and "manifest.json" not in payloads
            and all(type(name) is str and type(raw) is bytes for name, raw in payloads.items()),
            "DELIVERY_MEMBERS")
    aggregate = sum(map(len, payloads.values()))
    require(aggregate < maximum, "DELIVERY_BOUND")
    manifest = {
        "schema": "g132.public-compact-delivery-fixture.v1",
        "files": {name: descriptor(raw) for name, raw in payloads.items()},
        "aggregate_bytes": aggregate,
    }
    return bounded_canonical(manifest, maximum - aggregate, "DELIVERY_BOUND")
