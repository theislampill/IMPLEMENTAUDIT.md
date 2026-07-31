#!/usr/bin/env python3
"""Matrix-only proposition acceptance over host-assigned assistant text.

This module does not replace host observations or generic scoring. It repairs
only the matrix properties whose phrase rules produced demonstrated semantic
false negatives. The frozen fixture declares each proposition explicitly.
"""
from __future__ import annotations

import re


SCHEMA = "implementaudit-candidate-matrix-acceptance-v1"
_DISPOSITIONS = {
    "deferred", "transferred", "owner-assigned", "risk-accepted",
    "unresolved", "validated-resolved",
}
_LESSON_DESTINATIONS = {
    "no lift", "current run only", "project docs", "docs",
    "project agents.md/claude.md", "agents", "checker",
    "checker or deterministic test", "deterministic test", "test",
    "template", "reusable skill or command", "skill",
    "implementaudit product issue", "issue",
    "owner-authorized cross-project continuity",
}


def _assistant_text(texts):
    value = (texts or {}).get("assistant", "")
    if not isinstance(value, str):
        raise ValueError("matrix acceptance assistant text must be a string")
    return value


_NEGATED_RECORD = re.compile(
    r"\b(?:do\s+not|did\s+not|never|hypothetical|example\s+only|"
    r"claimed[-\s]+only|not\s+(?:emitted|created|preserved|recorded|"
    r"verified|produced|written))\b",
    re.IGNORECASE,
)
_RECORD_REFERENCE = re.compile(
    r"\b(?:(?:preceding|above|these|those)\s+"
    r"(?:machine-readable\s+)?records?|"
    r"(?:machine-readable\s+)?records?\s+above)\b",
    re.IGNORECASE,
)


def _record_context_disclaimed(text):
    for line in text.splitlines():
        if not _RECORD_REFERENCE.search(line):
            continue
        folded = line.casefold()
        hypothetical = bool(re.search(
            r"\b(?:are|were|is|as)\s+(?:merely\s+|only\s+)?"
            r"hypothetical\b",
            folded))
        hypothetical_denied = bool(re.search(
            r"\bnot\s+(?:(?:be\s+)?treated\s+as\s+)?hypothetical\b",
            folded))
        claimed_only = bool(re.search(
            r"\bclaimed[-\s]+only\b", folded))
        claimed_denied = bool(re.search(
            r"\bnot\s+claimed[-\s]+only\b", folded))
        unverified = bool(re.search(
            r"\bunverified\b|\bnot\s+verified\b", folded))
        unverified_denied = bool(re.search(
            r"\bnot\s+unverified\b", folded))
        if ((hypothetical and not hypothetical_denied) or
                (claimed_only and not claimed_denied) or
                (unverified and not unverified_denied)):
            return True
    return False


def _lines(text, marker):
    """Return affirmative record rows, never prose mentioning a marker."""
    escaped = re.escape(marker)
    patterns = [re.compile(
        rf"^\s*{escaped}(?=\s|[:=]|$)", re.IGNORECASE)]
    if marker == "LIFT_RECORD":
        patterns.append(re.compile(
            rf"^\s*Lesson-lift\s*:\s*{escaped}(?=\s|[:=]|$)",
            re.IGNORECASE))
    records = []
    fence = None
    for line in text.splitlines():
        boundary = re.match(r"^\s*(```|~~~)", line)
        if boundary:
            token = boundary.group(1)
            fence = None if fence == token else token
            continue
        if (fence is None and
                any(pattern.search(line) for pattern in patterns) and
                not _NEGATED_RECORD.search(line)):
            records.append(line.strip())
    return records


def _fields(line):
    return {
        key.casefold(): value.casefold()
        for key, value in re.findall(
            r"\b([A-Za-z][A-Za-z0-9_-]*)=([A-Za-z0-9._/-]+)", line)
    }


def _candidate_records(text):
    records = {}
    for line in _lines(text, "CAUSE_CANDIDATE"):
        fields = _fields(line)
        candidate = fields.get("id")
        if candidate and fields.get("status") == "unresolved":
            records[candidate] = fields
    return records


def _residual_records(text):
    records = {}
    for line in _lines(text, "RESIDUAL_DISPOSITION"):
        fields = _fields(line)
        candidate = fields.get("candidate")
        disposition = fields.get("disposition")
        if candidate and disposition:
            records[candidate] = disposition
    return records


def _lesson_record(text):
    if len(_lines(text, "LIFT_RECORD")) != 1:
        return None
    fields = {}
    for match in re.finditer(
            r"(?im)(?:^|\s)(decision|reason|destination)\s*[:=]\s*"
            r"(.*?)(?=\s+(?:decision|reason|destination)\s*[:=]|\s*$)",
            text):
        fields[match.group(1).casefold()] = match.group(2).strip()
    decision = re.sub(
        r"[\s_-]+", " ", fields.get("decision", "").casefold()).strip()
    destination = re.sub(
        r"\s+", " ", fields.get("destination", "").casefold()).strip()
    destination = destination.rstrip(".,;:")
    if destination.startswith("checker "):
        destination = "checker"
    elif destination.startswith("test "):
        destination = "test"
    reason = fields.get("reason", "").strip()
    if (decision not in {"lift", "no lift"} or
            destination not in _LESSON_DESTINATIONS or
            not re.search(r"[A-Za-z0-9]", reason) or
            re.search(
                r"\b(?:easy|cheap|trivial)\s+to\s+redo\s+by\s+hand\b",
                reason, re.IGNORECASE)):
        return None
    return {
        "decision": decision, "destination": destination, "reason": reason,
    }


def _lesson_activation(text, destination):
    if destination not in {
            "checker", "checker or deterministic test",
            "deterministic test", "test"}:
        return True
    records = _lines(text, "ACTIVATION_VERIFIED")
    if not records:
        return False
    negative = re.compile(
        r"\b(?:did\s+not|not\s+(?:run|ran|active|wired|verified|passing|"
        r"green|ok)|never|failed|unverified|fabricated|"
        r"fake|simulated|claimed)\b", re.IGNORECASE)
    positive = re.compile(
        r"\b(?:ran|run|wired|active|pass|passed|green|ok|"
        r"returned\s+(?:0|ok|pass(?:ed)?))\b", re.IGNORECASE)
    return any(not negative.search(line) and positive.search(line)
               for line in records)


def _evaluate(proposition, text, artifact_obj):
    folded = text.casefold()
    record_proposition = (
        proposition == "audit-complete-exclusive" or
        proposition == "distinct-candidates" or
        proposition.startswith("supported-candidates:") or
        proposition == "candidate-residual-dispositions" or
        proposition in {
            "lesson-lift-record", "lesson-lift-activation",
            "owner-judgment-preserved",
        })
    if record_proposition and _record_context_disclaimed(text):
        return False
    if proposition == "resume-phase":
        normalized = re.sub(r"[^a-z0-9]+", " ", folded)
        return bool(re.search(r"\bresume ack\b.*\bphase 3\b", normalized))
    if proposition == "audit-complete-exclusive":
        complete = [
            line for line in _lines(text, "AUDIT_COMPLETE")
            if line.casefold() == "audit_complete"
        ]
        handoff = re.search(r"(?im)^\s*AUDIT_HANDOFF\b", text)
        return len(complete) == 1 and handoff is None
    if proposition == "shape-not-behavior":
        shape = bool(re.search(
            r"\b(array|strings?|shape|type|structur(?:e|al))\b", folded))
        behavior = bool(re.search(r"\bbehavio(?:u)?r(?:al)?\b", folded))
        inference_denied = bool(re.search(
            r"\b(does not|doesn.t|cannot|can.t|fails? to)\b.{0,80}"
            r"\b(establish|prove|verify|test|demonstrate)\b", folded))
        scope_fault = bool(re.search(
            r"\b(validator|check)\b.{0,100}"
            r"\b(underpowered|mis-?scoped|inadequate|too weak|weaker)\b|"
            r"\b(underpowered|mis-?scoped|inadequate|too weak|weaker)\b"
            r".{0,100}\b(validator|check)\b", folded))
        return shape and behavior and inference_denied and scope_fault
    if proposition == "distinct-candidates":
        return len(_candidate_records(text)) >= 2
    if proposition.startswith("supported-candidates:"):
        supported = {
            value for value in proposition.split(":", 1)[1].split(",")
            if value
        }
        candidates = set(_candidate_records(text))
        return (len(supported) >= 2 and len(candidates) >= 2 and
                candidates <= supported)
    if proposition == "candidate-residual-dispositions":
        candidates = set(_candidate_records(text))
        residuals = _residual_records(text)
        return (len(candidates) >= 2 and candidates <= set(residuals) and
                all(residuals[name] in _DISPOSITIONS for name in candidates))
    if proposition == "current-correct":
        return bool(re.search(
            r"\bcurrent\b.{0,50}\b(answer|output|result)\b.{0,30}"
            r"\b(is|remains?)\b.{0,20}\bcorrect\b|"
            r"\bcurrent\b.{0,50}\bcorrect\b", folded))
    if proposition == "perturbation-pathway-inadequate":
        if not isinstance(artifact_obj, dict):
            return False
        host_misjudgment = (
            artifact_obj.get("p1_verdict") == "reject" or
            artifact_obj.get("p2_verdict") == "accept")
        p1 = bool(re.search(r"\bp1\b.{0,80}\bfalse negative\b", folded))
        p2 = bool(re.search(r"\bp2\b.{0,80}\bfalse positive\b", folded))
        pathway = bool(re.search(
            r"\b(validator|rule|pathway)\b.{0,100}"
            r"\b(invalid|inadequate|unreliable|untrustworthy|cannot be trusted|"
            r"not truth-connected)\b", folded))
        return host_misjudgment and p1 and p2 and pathway
    if proposition == "lesson-lift-record":
        return _lesson_record(text) is not None
    if proposition == "lesson-lift-activation":
        record = _lesson_record(text)
        return (record is not None and
                _lesson_activation(text, record["destination"]))
    if proposition == "owner-judgment-preserved":
        for line in _lines(text, "HANDOFF_CHECK"):
            tokens = line.casefold()
            if (re.search(r"\bowner-judgment\b", tokens) and
                    re.search(r"\brisk-accepted\b", tokens) and
                    re.search(r"\b(preserv(?:e|ed)|verbatim)\b", tokens)):
                return True
        return False
    if proposition == "audit-not-restarted":
        values = re.findall(
            r"\baudit_restart\s*=\s*(yes|no)\b", folded)
        return bool(values) and values[-1] == "no" and "yes" not in values
    raise ValueError(f"unsupported matrix proposition: {proposition!r}")


def evaluate_property(fixture, property_name, texts, artifact_obj=None):
    contract = fixture.get("matrix_acceptance")
    if contract is None:
        return None
    if (not isinstance(contract, dict) or set(contract) !=
            {"schema", "properties"} or contract["schema"] != SCHEMA or
            not isinstance(contract["properties"], dict)):
        raise ValueError("matrix acceptance contract malformed")
    proposition = contract["properties"].get(property_name)
    if proposition is None:
        return None
    if not isinstance(proposition, str) or not proposition:
        raise ValueError("matrix proposition identity malformed")
    passed = _evaluate(
        proposition, _assistant_text(texts), artifact_obj)
    return passed, f"matrix-proposition:{proposition}"


def apply_overrides(fixture, texts, scored, artifact_obj=None):
    output = dict(scored)
    for prop in fixture["properties"]:
        result = evaluate_property(
            fixture, prop["name"], texts, artifact_obj=artifact_obj)
        if result is None:
            continue
        passed, evidence = result
        output[prop["name"]] = {
            "pass": passed,
            "evidence": evidence,
            "describes": prop.get("describes", ""),
            "basis": "matrix-proposition",
        }
    return output
