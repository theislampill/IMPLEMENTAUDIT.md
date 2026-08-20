#!/usr/bin/env python3
"""Strict canonical loader for the R0038 operational-evidence substrate."""
from __future__ import annotations

import argparse
import decimal
import hashlib
import json
import math
import pathlib
import sys
from collections import Counter


RECORD_SCHEMA = "implementaudit-operational-evidence-v1"
VALIDATION_SCHEMA = "implementaudit-operational-evidence-validation-v1"
SCHEMA_DEFINITION = "implementaudit-operational-evidence-schema-v1"
FAMILIES = (
    "CODE", "OWNERSHIP", "EXECUTION", "EVIDENCE", "FAILURE", "RELEASE")
STATES = (
    "CURRENT", "UNKNOWN", "UNSUPPORTED", "STALE", "UNVERIFIED",
    "CONTRADICTORY", "PARSER_ERROR", "INVALID")
AGGREGATES = ("COMPLETE", "DEGRADED", "STALE", "INVALID", "SUPERSEDED")
LAYERS = (
    "repository", "git", "planning", "controller", "execution",
    "evidence", "failure", "package", "install", "host", "ci",
    "release", "external", "public")
ENTITY_FAMILIES = {
    "Repository": "CODE", "Commit": "CODE", "Tree": "CODE",
    "Worktree": "CODE", "File": "CODE", "Symbol": "CODE",
    "Package": "CODE", "GeneratedArtifact": "CODE",
    "Writer": "OWNERSHIP", "Resource": "OWNERSHIP",
    "Controller": "EXECUTION", "CustodyClaim": "EXECUTION",
    "Receipt": "EXECUTION", "Run": "EXECUTION", "Phase": "EXECUTION",
    "WorkItem": "EXECUTION", "Claim": "EVIDENCE",
    "Criterion": "EVIDENCE", "Evidence": "EVIDENCE", "Check": "EVIDENCE",
    "Review": "EVIDENCE", "Andon": "FAILURE", "Residual": "FAILURE",
    "Countermeasure": "FAILURE", "Issue": "RELEASE",
    "PullRequest": "RELEASE", "WorkflowRun": "RELEASE",
    "Release": "RELEASE", "Tag": "RELEASE", "Asset": "RELEASE",
    "Install": "RELEASE", "PublicSurface": "RELEASE",
}
RELATION_TYPES = (
    "OWNS", "WRITES", "GENERATES", "PACKAGES", "INSTALLS", "CONSUMES",
    "DEPENDS_ON", "BLOCKS", "READY_WHEN", "SERIALISES_WITH", "JOINS",
    "CLAIMS", "EVIDENCES", "CONTRADICTS", "INVALIDATES", "SUPERSEDES",
    "FAILED_AT", "CONTAINED_BY", "REPAIRED_BY", "VERIFIED_BY",
    "RECOVERED_TO", "QUALIFIES", "MERGES_TO", "TAGS", "PUBLISHES",
    "READ_BACK_AS")
TOP_LEVEL_KEYS = {
    "schema", "aggregate", "families", "affected_families",
    "capability_declarations", "currentness_predicates", "entities",
    "relations", "payload_records"}
COMMON_KEYS = {
    "id", "family", "native_owner_identity", "source_identity",
    "evidence_layer", "currentness"}
HEX = frozenset("0123456789abcdef")


class OperationalEvidenceError(ValueError):
    """A stable typed refusal for unsupported or invalid evidence input."""

    def __init__(self, code: str, path: str, message: str):
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message

    def receipt(self) -> dict[str, str]:
        return {
            "schema": "implementaudit-operational-evidence-error-v1",
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }


def _error(code: str, path: str, message: str) -> None:
    raise OperationalEvidenceError(code, path, message)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _error("OE_JSON_DUPLICATE_KEY", "$", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(token):
    _error("OE_JSON_NONFINITE", "$", f"non-finite JSON number: {token}")


def _strict_int(token):
    try:
        return int(token)
    except ValueError:
        _error("OE_JSON_NUMBER_LIMIT", "$",
               "JSON integer exceeds the runtime conversion limit")


def _lossless_float(token):
    try:
        source = decimal.Decimal(token)
        value = float(source)
        round_trip = decimal.Decimal(repr(value)) if math.isfinite(value) else None
    except decimal.DecimalException:
        _error("OE_JSON_NUMBER_LOSS", "$", f"invalid JSON number: {token}")
    if round_trip is None:
        _error("OE_JSON_NONFINITE", "$", f"non-finite JSON number: {token}")
    sign_changed = (source.is_zero() and
                    source.is_signed() != (math.copysign(1.0, value) < 0.0))
    if round_trip != source or sign_changed:
        _error("OE_JSON_NUMBER_LOSS", "$", f"lossy JSON number: {token}")
    return value


def decode_strict_json_bytes(data: bytes, owner: str):
    if data.startswith(b"\xef\xbb\xbf"):
        _error("OE_UTF8_BOM", "$", f"{owner} must not contain a UTF-8 BOM")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        _error("OE_UTF8_INVALID", "$", f"{owner} must be valid UTF-8")
    try:
        return json.loads(
            text, object_pairs_hook=_unique_object,
            parse_constant=_nonfinite, parse_float=_lossless_float,
            parse_int=_strict_int)
    except OperationalEvidenceError:
        raise
    except (json.JSONDecodeError, RecursionError):
        _error("OE_JSON_MALFORMED", "$", f"{owner} is malformed JSON")


def canonical_json_v1(value) -> bytes:
    """UTF-8 JSON, sorted object keys, declared array order, no whitespace."""
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        _error("OE_JSON_MODEL_INVALID", "$", "value is not strict JSON")


def canonical_payload_text(value: str) -> str:
    """Normalize only line endings, then remove all trailing LF characters."""
    if type(value) is not str:
        _error("OE_SCHEMA_INVALID", "$.payload_records[].payload",
               "payload must be a string")
    return value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def _object(value, path, *, exact_keys=None, required=()):
    if type(value) is not dict:
        _error("OE_SCHEMA_INVALID", path, "must be an object")
    missing = set(required) - set(value)
    extra = set(value) - set(exact_keys) if exact_keys is not None else set()
    if missing:
        _error("OE_SCHEMA_INVALID", path,
               f"missing keys: {','.join(sorted(missing))}")
    if extra:
        _error("OE_SCHEMA_INVALID", path,
               f"unknown keys: {','.join(sorted(extra))}")
    return value


def _text(value, path):
    if type(value) is not str or not value:
        _error("OE_SCHEMA_INVALID", path, "must be a non-empty string")
    return value


def _string_list(value, path, *, allowed=None, unique=True):
    if type(value) is not list:
        _error("OE_SCHEMA_INVALID", path, "must be an array")
    for index, item in enumerate(value):
        _text(item, f"{path}[{index}]")
        if allowed is not None and item not in allowed:
            _error("OE_SCHEMA_INVALID", f"{path}[{index}]", "unsupported value")
    if unique and len(set(value)) != len(value):
        _error("OE_SCHEMA_INVALID", path, "must not contain duplicates")
    return value


def _currentness(value, path):
    _object(value, path, exact_keys={"state", "invalidators"},
            required={"state", "invalidators"})
    state = value["state"]
    if state not in STATES:
        _error("OE_SCHEMA_INVALID", f"{path}.state", "unsupported state")
    invalidators = _string_list(value["invalidators"], f"{path}.invalidators")
    if state == "CURRENT" and invalidators:
        _error("OE_STALE_RECORD", path,
               "CURRENT record cannot retain an invalidator")
    if state == "STALE" and not invalidators:
        _error("OE_STALE_RECORD", path,
               "STALE record must name an invalidator")
    return state


def _common_record(value, path, *, exact_keys, required_extra=()):
    required = COMMON_KEYS | set(required_extra)
    _object(value, path, exact_keys=COMMON_KEYS | set(exact_keys), required=required)
    _text(value["id"], f"{path}.id")
    if value["family"] not in FAMILIES:
        _error("OE_SCHEMA_INVALID", f"{path}.family", "unsupported family")
    _text(value["native_owner_identity"], f"{path}.native_owner_identity")
    source = _object(
        value["source_identity"], f"{path}.source_identity",
        exact_keys={"id", "layer"}, required={"id", "layer"})
    _text(source["id"], f"{path}.source_identity.id")
    if source["layer"] not in LAYERS or value["evidence_layer"] not in LAYERS:
        _error("OE_SCHEMA_INVALID", path, "unsupported evidence layer")
    if source["layer"] != value["evidence_layer"]:
        _error("OE_CROSS_LAYER", path,
               "source layer and evidence layer must identify the same native leg")
    state = _currentness(value["currentness"], f"{path}.currentness")
    return state


def _validate_schema_definition(schema):
    try:
        expected = schema["properties"]["schema"]["const"]
        aggregates = tuple(schema["properties"]["aggregate"]["enum"])
        families = tuple(schema["properties"]["families"]["prefixItems"])
        family_values = tuple(item["const"] for item in families)
        states = tuple(schema["$defs"]["state"]["enum"])
        layers = tuple(schema["$defs"]["layer"]["enum"])
        entity_types = set(schema["$defs"]["entity"]["properties"]
                           ["record_type"]["enum"])
        relation_types = tuple(schema["$defs"]["relation"]["properties"]
                               ["relation_type"]["enum"])
        canonicalisation = schema["x-canonicalisation"]
        payload_normalisation = schema["x-payload-normalisation"]
    except (KeyError, TypeError):
        _error("OE_SCHEMA_DEFINITION_INVALID", "$schema",
               "schema definition is incomplete")
    if (schema.get("x-implementaudit-schema") != SCHEMA_DEFINITION or
            expected != RECORD_SCHEMA or aggregates != AGGREGATES or
            family_values != FAMILIES or states != STATES or layers != LAYERS or
            entity_types != set(ENTITY_FAMILIES) or
            relation_types != RELATION_TYPES or
            canonicalisation != {
                "identity": "canonical_json_v1", "encoding": "UTF-8",
                "bom": False, "object_keys": "recursive_lexicographic",
                "array_order": "declared_semantic_order",
                "insignificant_whitespace": False, "string_rewriting": False,
            } or payload_normalisation != {
                "identity": "canonical_payload_text_v1",
                "line_endings": "CRLF_and_CR_to_LF",
                "trailing_lf": "remove_all",
                "other_whitespace": "preserve", "unicode": "preserve",
            }):
        _error("OE_SCHEMA_DEFINITION_INVALID", "$schema",
               "schema definition does not match the loader contract")


def _digest(value, path):
    if (type(value) is not str or len(value) != 64 or
            any(character not in HEX for character in value)):
        _error("OE_SCHEMA_INVALID", path, "must be 64 lowercase hexadecimal")


def _validate_record(value):
    if type(value) is not dict:
        _error("OE_SCHEMA_INVALID", "$", "must be an object")
    if value.get("schema") != RECORD_SCHEMA:
        _error("OE_SCHEMA_UNSUPPORTED", "$.schema",
               f"unsupported operational-evidence schema: {value.get('schema')!r}")
    _object(value, "$", exact_keys=TOP_LEVEL_KEYS, required=TOP_LEVEL_KEYS)
    if value["aggregate"] not in AGGREGATES:
        _error("OE_SCHEMA_INVALID", "$.aggregate", "unsupported aggregate")
    if type(value["families"]) is not list or tuple(value["families"]) != FAMILIES:
        _error("OE_SCHEMA_INVALID", "$.families",
               "must preserve the six frozen families in canonical order")
    affected = _string_list(
        value["affected_families"], "$.affected_families", allowed=FAMILIES)
    if value["aggregate"] == "COMPLETE" and affected:
        _error("OE_SCHEMA_INVALID", "$.affected_families",
               "COMPLETE cannot name affected families")
    if value["aggregate"] != "COMPLETE" and not affected:
        _error("OE_SCHEMA_INVALID", "$.affected_families",
               "non-COMPLETE aggregate must name affected families")

    collections = (
        ("capability_declarations", {"supported", "reason_code"},
         {"supported", "reason_code"}),
        ("currentness_predicates", {"predicate", "input_sha256"},
         {"predicate", "input_sha256"}),
        ("entities", {"record_type", "required"},
         {"record_type", "required"}),
        ("relations", {"relation_type", "source_entity_id",
                       "target_entity_id", "confidence", "inference_rule"},
         {"relation_type", "source_entity_id", "target_entity_id",
          "confidence", "inference_rule"}),
        ("payload_records", {"media_type", "payload", "payload_sha256"},
         {"media_type", "payload", "payload_sha256"}),
    )
    all_ids = set()
    entities = set()
    required_current_families = set()
    for name, keys, required in collections:
        rows = value[name]
        if type(rows) is not list:
            _error("OE_SCHEMA_INVALID", f"$.{name}", "must be an array")
        for index, row in enumerate(rows):
            path = f"$.{name}[{index}]"
            state = _common_record(
                row, path, exact_keys=keys, required_extra=required)
            if row["id"] in all_ids:
                _error("OE_SCHEMA_INVALID", path, "record id must be unique")
            all_ids.add(row["id"])
            if name == "capability_declarations":
                if type(row["supported"]) is not bool:
                    _error("OE_SCHEMA_INVALID", f"{path}.supported",
                           "must be a boolean")
                _text(row["reason_code"], f"{path}.reason_code")
            elif name == "currentness_predicates":
                _text(row["predicate"], f"{path}.predicate")
                _digest(row["input_sha256"], f"{path}.input_sha256")
            elif name == "entities":
                record_type = row["record_type"]
                if type(record_type) is not str:
                    _error("OE_SCHEMA_INVALID", f"{path}.record_type",
                           "must be a string")
                expected_family = ENTITY_FAMILIES.get(record_type)
                if expected_family is None:
                    _error("OE_SCHEMA_INVALID", f"{path}.record_type",
                           "unsupported entity type")
                if expected_family != row["family"]:
                    _error("OE_CROSS_LAYER", path,
                           "entity type crossed its frozen projection family")
                if type(row["required"]) is not bool:
                    _error("OE_SCHEMA_INVALID", f"{path}.required",
                           "must be a boolean")
                entities.add(row["id"])
                if row["required"] and state == "CURRENT":
                    required_current_families.add(row["family"])
                if (value["aggregate"] == "COMPLETE" and row["required"] and
                        state != "CURRENT"):
                    _error("OE_STALE_RECORD", path,
                           "COMPLETE requires every required entity CURRENT")
            elif name == "relations":
                if row["relation_type"] not in RELATION_TYPES:
                    _error("OE_SCHEMA_INVALID", f"{path}.relation_type",
                           "unsupported relation type")
                _text(row["source_entity_id"], f"{path}.source_entity_id")
                _text(row["target_entity_id"], f"{path}.target_entity_id")
                if row["confidence"] not in ("mechanical", "declared", "inferred"):
                    _error("OE_SCHEMA_INVALID", f"{path}.confidence",
                           "unsupported confidence")
                if row["confidence"] == "inferred":
                    _text(row["inference_rule"], f"{path}.inference_rule")
                elif row["inference_rule"] is not None:
                    _error("OE_SCHEMA_INVALID", f"{path}.inference_rule",
                           "only inferred relations name an inference rule")
            elif name == "payload_records":
                _text(row["media_type"], f"{path}.media_type")
                normalized = canonical_payload_text(row["payload"])
                digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
                _digest(row["payload_sha256"], f"{path}.payload_sha256")
                if digest != row["payload_sha256"]:
                    _error("OE_PAYLOAD_DIGEST", f"{path}.payload_sha256",
                           "payload digest does not match canonical payload bytes")
                row["payload"] = normalized

    for index, relation in enumerate(value["relations"]):
        if (relation["source_entity_id"] not in entities or
                relation["target_entity_id"] not in entities):
            _error("OE_SCHEMA_INVALID", f"$.relations[{index}]",
                   "relation endpoint is not a retained entity")
    if (value["aggregate"] == "COMPLETE" and
            required_current_families != set(FAMILIES)):
        _error("OE_SCHEMA_INVALID", "$.entities",
               "COMPLETE must retain a required CURRENT entity for every family")
    return value


def load_operational_evidence(path: pathlib.Path):
    script_root = pathlib.Path(__file__).resolve().parent.parent
    schema_path = script_root / "references" / "operational-evidence-schema.json"
    try:
        schema_bytes = schema_path.read_bytes()
        input_bytes = path.read_bytes()
    except OSError:
        _error("OE_INPUT_UNREADABLE", "$", "input or schema cannot be read")
    schema = decode_strict_json_bytes(schema_bytes, "operational-evidence schema")
    _validate_schema_definition(schema)
    value = decode_strict_json_bytes(input_bytes, "operational-evidence input")
    return _validate_record(value), hashlib.sha256(
        canonical_json_v1(schema)).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="validate and canonicalize R0038 operational evidence")
    parser.add_argument("command", choices=("validate", "canonicalize"))
    parser.add_argument("input", type=pathlib.Path)
    args = parser.parse_args()
    try:
        value, schema_sha256 = load_operational_evidence(args.input)
        canonical = canonical_json_v1(value)
        if args.command == "canonicalize":
            sys.stdout.buffer.write(canonical)
        else:
            census = Counter(
                row["currentness"]["state"]
                for name in ("capability_declarations", "currentness_predicates",
                             "entities", "relations", "payload_records")
                for row in value[name])
            receipt = {
                "schema": VALIDATION_SCHEMA,
                "record_schema": RECORD_SCHEMA,
                "aggregate": value["aggregate"],
                "families": list(FAMILIES),
                "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
                "schema_sha256": schema_sha256,
                "fact_state_census": dict(sorted(census.items())),
            }
            sys.stdout.buffer.write(canonical_json_v1(receipt))
        return 0
    except OperationalEvidenceError as exc:
        sys.stderr.buffer.write(canonical_json_v1(exc.receipt()))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
