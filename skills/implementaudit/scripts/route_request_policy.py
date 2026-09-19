#!/usr/bin/env python3
"""Canonical route input values and typed refusals; no IO, dispatch or CAS.

This is producer-side request validation, not an independent verifier. The
controller translates RequestRefusal through its unchanged fail/receipt boundary.
"""
from __future__ import annotations
import json
import re
from typing import Any

class RequestRefusal(Exception):
    def __init__(self, message: str, *, decision: str = "PENDING"):
        super().__init__(message)
        self.message = message
        self.decision = decision

def _refuse(message: str, *, decision: str = "PENDING") -> None:
    raise RequestRefusal(message, decision=decision)

REQUEST_SCHEMA = "implementaudit.route-decision-request.v1"
PREDICATE_VERSION = "R0033.route-predicate.v1"
HEX_RE = re.compile(r"sha256:[0-9a-f]{64}")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON member")
    return value

def exact_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 1024 or any(ord(char) < 32 for char in value):
        _refuse(f"{label} is empty, oversized, or contains a control character")
    return value

def exact_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _refuse(f"{label} has the wrong shape")
    return value

def identity_record(value: Any, label: str) -> dict[str, str]:
    record = exact_keys(value, {"identity", "digest"}, label)
    exact_text(record["identity"], f"{label}.identity")
    if not isinstance(record["digest"], str) or not HEX_RE.fullmatch(record["digest"]):
        _refuse(f"{label}.digest is not a canonical sha256 identity")
    return record

def validate_presentation(value: Any) -> dict[str, str]:
    """Existing request/record custody for an actual no-child presentation."""
    presentation = exact_keys(value, {"parent_holon", "consuming_frontier"}, "route presentation")
    for key, text in presentation.items():
        if (not isinstance(text, str) or not 0 < len(text) <= 240 or text != text.strip()
                or "`" in text or any(ord(char) < 32 or ord(char) == 127 for char in text)):
            _refuse("route presentation has malformed " + key)
    return presentation

def validate_request(request: Any) -> dict[str, Any]:
    """Validate one already-observed canonical R0033 request value."""
    keys = {
        "schema",
        "predicate_version",
        "boundary",
        "scope",
        "action",
        "inputs",
    }
    if isinstance(request, dict) and "presentation" in request:
        keys.add("presentation")
        validate_presentation(request["presentation"])
    exact_keys(request, keys, "request")
    if request["schema"] != REQUEST_SCHEMA or request["predicate_version"] != PREDICATE_VERSION:
        _refuse("request schema or predicate version is stale")
    boundary = exact_keys(request["boundary"], {"kind", "event_id", "digest"}, "boundary")
    exact_text(boundary["kind"], "boundary.kind")
    exact_text(boundary["event_id"], "boundary.event_id")
    if not isinstance(boundary["digest"], str) or not HEX_RE.fullmatch(boundary["digest"]):
        _refuse("boundary identity is malformed")
    identity_record(request["scope"], "scope")
    action = exact_keys(request["action"], {"identity", "digest", "class", "argv"}, "action")
    exact_text(action["identity"], "action.identity")
    exact_text(action["class"], "action.class")
    if not isinstance(action["digest"], str) or not HEX_RE.fullmatch(action["digest"]):
        _refuse("action identity is malformed")
    if (
        not isinstance(action["argv"], list)
        or not action["argv"]
        or len(action["argv"]) > 64
        or any(not isinstance(item, str) or not item or len(item) > 4096 for item in action["argv"])
    ):
        _refuse("action argv is empty, oversized, or malformed")
    if not isinstance(request["inputs"], list) or not request["inputs"]:
        _refuse("inputs must be a non-empty complete identity set")
    identities: list[str] = []
    for index, item in enumerate(request["inputs"]):
        record = exact_keys(item, {"identity", "path", "digest"}, f"inputs[{index}]")
        identities.append(exact_text(record["identity"], f"inputs[{index}].identity"))
        exact_text(record["path"], f"inputs[{index}].path")
        if not isinstance(record["digest"], str) or not HEX_RE.fullmatch(record["digest"]):
            _refuse(f"inputs[{index}].digest is not canonical")
    if identities != sorted(identities) or len(identities) != len(set(identities)):
        _refuse("inputs are not uniquely ordered by identity")
    return request

def decoded_artifact(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        _refuse(f"{label} bytes are malformed: {exc}")
    if not isinstance(value, dict):
        _refuse(f"{label} bytes are not a JSON object")
    return value
