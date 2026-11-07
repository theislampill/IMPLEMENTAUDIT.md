"""Emit closed D0 wire schemas from the independent receiver definitions.

This generator imports only the inert local modules. It does not invoke a
receiver, observer, native adapter, controller, producer, or host census.
"""
from pathlib import Path
import copy
import hashlib
import json
import d0_wire as w
import d0_receiver as r

HERE = Path(__file__).parent
DRAFT = "https://json-schema.org/draft/2020-12/schema"


def full_string_schema(value):
    value = copy.deepcopy(value)
    if isinstance(value, dict):
        for key, child in list(value.items()):
            value[key] = full_string_schema(child)
        if "pattern" in value:
            value["pattern"] = "^(?:" + value["pattern"] + ")(?![\\s\\S])"
    elif isinstance(value, list):
        value = [full_string_schema(child) for child in value]
    return value


def schemas():
    result = {
        "D0_OPERATION_BINDING.schema.json": {"$schema": DRAFT, **w.BINDING},
        "D0_PRIVATE_RECEIPT.schema.json": w.PRIVATE_SCHEMA,
        "D0_INDEPENDENT_RECEIVER_RECEIPT.schema.json": r.RECUT_SCHEMA,
        "D0_ELIGIBILITY.schema.json": r.DECISION_SCHEMA,
    }
    for name, source in result.items():
        schema = full_string_schema(source)
        schema["$comment"] = (
            "Closed structural schema. Patterns use absolute start/end matching, including final newlines. "
            "The canonical byte codec, exact JSON types, cross-field relations, identity equality, "
            "population completeness, path policy, byte limits and independent recut relation in "
            "d0_wire.py/d0_receiver.py remain mandatory. This schema is not an authorization token."
        )
        yield name, schema


if __name__ == "__main__":
    records = []
    for name, schema in schemas():
        raw = w.codec(schema)
        (HERE / name).write_bytes(raw)
        records.append({"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    print(json.dumps({"emitted": records, "actual_host_observation": False}, sort_keys=True))
