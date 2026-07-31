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
    "validated-resolved",
}


def _assistant_text(texts):
    value = (texts or {}).get("assistant", "")
    if not isinstance(value, str):
        raise ValueError("matrix acceptance assistant text must be a string")
    return value


def _lines(text, marker):
    return [line.strip() for line in text.splitlines()
            if marker.casefold() in line.casefold()]


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
        if candidate:
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


def _evaluate(proposition, text, artifact_obj):
    folded = text.casefold()
    if proposition == "resume-phase":
        normalized = re.sub(r"[^a-z0-9]+", " ", folded)
        return bool(re.search(r"\bresume ack\b.*\bphase 3\b", normalized))
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
        records = _lines(text, "LIFT_RECORD")
        for line in records:
            fields = _fields(line)
            reason = fields.get("reason", "")
            if (fields.get("decision") == "lift" and reason and
                    reason != "cheap-to-redo-by-hand" and
                    fields.get("destination") in {
                        "checker", "test", "docs", "agents", "skill", "issue",
                    }):
                return True
        return False
    if proposition == "lesson-lift-activation":
        records = _lines(text, "ACTIVATION_VERIFIED")
        return any(
            re.search(r"\b(checker|test|script)\b", line, re.IGNORECASE) and
            re.search(
                r"\b(pass(?:ed)?|active|wired|runs?)\b", line,
                re.IGNORECASE)
            for line in records)
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
