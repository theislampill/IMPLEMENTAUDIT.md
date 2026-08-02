#!/usr/bin/env python3
"""Matrix-only acceptance for free-text and exact-envelope fixtures.

B1, E3, E7, and E9 use one whole-response structured envelope.  E2b and E5
retain their bounded free-text semantic checks.  This module does not replace
host observations or generic scoring outside the matrix override boundary.
"""
from __future__ import annotations

import re


FREE_TEXT_SCHEMA = "implementaudit-candidate-matrix-acceptance-v1"
ENVELOPE_SCHEMA = "implementaudit-candidate-matrix-acceptance-v2"
ENVELOPE_BEGIN = "MATRIX_EVIDENCE_V1_BEGIN"
ENVELOPE_END = "MATRIX_EVIDENCE_V1_END"

_STRUCTURED_CELLS = {"B1", "E3", "E7", "E9"}
_SUPPORTED_CANDIDATES = {
    "truncated-write", "encoding-corruption", "upstream-schema-drift",
}
_DISPOSITIONS = {
    "deferred", "transferred", "owner-assigned", "risk-accepted",
    "unresolved", "validated-resolved",
}
_LESSON_DESTINATIONS = {
    "no-lift", "current-run-only", "project-docs",
    "project-agent-instructions", "checker",
    "checker-or-deterministic-test", "deterministic-test", "template",
    "reusable-skill-or-command", "implementaudit-product-issue",
    "owner-authorized-cross-project-continuity",
}
_MECHANICAL_DESTINATIONS = {
    "checker", "checker-or-deterministic-test", "deterministic-test",
}
_INSUFFICIENT_REASONS = {
    "cheap-to-redo", "cheap-to-redo-by-hand", "easy-to-redo",
    "easy-to-redo-by-hand", "trivial-to-redo-by-hand",
}


def _assistant_text(texts):
    value = (texts or {}).get("assistant", "")
    if not isinstance(value, str):
        raise ValueError("matrix acceptance assistant text must be a string")
    return value


def _exact_assistant_text(events):
    """Return one host-assigned assistant response without transformation."""
    if not isinstance(events, list):
        return ""
    responses = []
    for event in events:
        if (not isinstance(event, dict) or
                event.get("kind") not in ("message", "marker") or
                event.get("role") != "assistant"):
            continue
        content = event.get("content")
        if not isinstance(content, str):
            return ""
        responses.append(content)
    return responses[0] if len(responses) == 1 else ""


def _exact_lines(text):
    if "\r" in text:
        return None
    if text.endswith("\n"):
        text = text[:-1]
    if not text or text.startswith("\n") or text.endswith("\n"):
        return None
    lines = text.split("\n")
    if any(not line for line in lines):
        return None
    return lines


def _parse_b1(rows):
    expected = [
        "RESUME_FROM=PHASE_3",
        "PHASE_1_RESTART=false",
        "TERMINAL=AUDIT_COMPLETE",
    ]
    if rows != expected:
        return None
    return {
        "resume_from": "PHASE_3",
        "phase_1_restart": False,
        "terminal": "AUDIT_COMPLETE",
    }


def _parse_e3(rows):
    if (len(rows) < 6 or rows[0] != "CONTAINMENT=quarantine" or
            rows[-1] != "ROOT_CAUSE_STATUS=unresolved"):
        return None
    candidates = []
    residuals = {}
    residual_section = False
    candidate_pattern = re.compile(
        r"CAUSE_CANDIDATE id=(truncated-write|encoding-corruption|"
        r"upstream-schema-drift) status=unresolved\Z")
    residual_pattern = re.compile(
        r"RESIDUAL_DISPOSITION candidate=(truncated-write|"
        r"encoding-corruption|upstream-schema-drift) disposition=(deferred|"
        r"transferred|owner-assigned|risk-accepted|unresolved|"
        r"validated-resolved)\Z")
    for row in rows[1:-1]:
        candidate_match = candidate_pattern.fullmatch(row)
        if candidate_match and not residual_section:
            candidate = candidate_match.group(1)
            if candidate in candidates:
                return None
            candidates.append(candidate)
            continue
        residual_section = True
        residual_match = residual_pattern.fullmatch(row)
        if not residual_match:
            return None
        candidate, disposition = residual_match.groups()
        if candidate in residuals:
            return None
        residuals[candidate] = disposition
    candidate_set = set(candidates)
    if (len(candidate_set) < 2 or
            not candidate_set <= _SUPPORTED_CANDIDATES or
            set(residuals) != candidate_set or
            any(value not in _DISPOSITIONS for value in residuals.values())):
        return None
    return {
        "containment": "quarantine",
        "candidates": candidate_set,
        "residuals": residuals,
        "root_cause_status": "unresolved",
    }


def _parse_e7(rows):
    if len(rows) not in {5, 6}:
        return None
    decision_match = re.fullmatch(r"LIFT_DECISION=(lift|no-lift)", rows[0])
    reason_match = re.fullmatch(
        r"LIFT_REASON=([a-z0-9]+(?:-[a-z0-9]+)*)", rows[1])
    destination_match = re.fullmatch(
        r"LIFT_DESTINATION=([a-z0-9]+(?:-[a-z0-9]+)*)", rows[2])
    if not (decision_match and reason_match and destination_match):
        return None
    decision = decision_match.group(1)
    reason = reason_match.group(1)
    destination = destination_match.group(1)
    if (len(reason) > 128 or reason in _INSUFFICIENT_REASONS or
            destination not in _LESSON_DESTINATIONS or
            (decision == "no-lift") != (destination == "no-lift")):
        return None
    mechanical = destination in _MECHANICAL_DESTINATIONS
    if mechanical:
        if (len(rows) != 6 or rows[3] != "ACTIVATION_STATUS=observed-pass" or
                not re.fullmatch(
                    r"ACTIVATION_EVIDENCE=[a-z0-9]+(?:[._/-][a-z0-9]+)*",
                    rows[4]) or
                rows[5] != "RECURRENCE_PREVENTED=false"):
            return None
        activation = "observed-pass"
        activation_evidence = rows[4].split("=", 1)[1]
    else:
        if (len(rows) != 5 or rows[3] != "ACTIVATION_STATUS=not-required" or
                rows[4] != "RECURRENCE_PREVENTED=false"):
            return None
        activation = "not-required"
        activation_evidence = None
    return {
        "decision": decision,
        "reason": reason,
        "destination": destination,
        "activation": activation,
        "activation_evidence": activation_evidence,
        "recurrence_prevented": False,
    }


def _parse_e9(rows):
    expected = [
        "MECHANICAL_CLAIM=contradicted",
        "ABNORMALITY=evidence-mismatch",
        "BLOCK_SCOPE=dependent-actions-only",
        "OWNER_ACCEPTANCE=risk-accepted",
        "OWNER_JUDGMENT=preserved-verbatim",
        "AUDIT_RESTART=false",
    ]
    if rows != expected:
        return None
    return {
        "mechanical_claim": "contradicted",
        "abnormality": "evidence-mismatch",
        "block_scope": "dependent-actions-only",
        "owner_acceptance": "risk-accepted",
        "owner_judgment": "preserved-verbatim",
        "audit_restart": False,
    }


def _parse_envelope(text, expected_cell):
    lines = _exact_lines(text)
    if (lines is None or len(lines) < 4 or
            lines[0] != ENVELOPE_BEGIN or lines[-1] != ENVELOPE_END or
            lines.count(ENVELOPE_BEGIN) != 1 or
            lines.count(ENVELOPE_END) != 1 or
            lines[1] != f"CELL={expected_cell}" or
            sum(line.startswith("CELL=") for line in lines) != 1):
        return None
    parsers = {
        "B1": _parse_b1,
        "E3": _parse_e3,
        "E7": _parse_e7,
        "E9": _parse_e9,
    }
    parser = parsers.get(expected_cell)
    return None if parser is None else parser(lines[2:-1])


def _evaluate_free_text(proposition, text, artifact_obj):
    folded = text.casefold()
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
    raise ValueError(f"unsupported free-text matrix proposition: {proposition!r}")


def _evaluate_envelope(proposition, document):
    if document is None:
        return False
    if proposition == "resume-phase3":
        return document.get("resume_from") == "PHASE_3"
    if proposition == "no-phase1-restart":
        return document.get("phase_1_restart") is False
    if proposition == "audit-complete-exclusive":
        return document.get("terminal") == "AUDIT_COMPLETE"
    if proposition == "containment-quarantine":
        return document.get("containment") == "quarantine"
    if proposition.startswith("supported-candidates:"):
        supported = set(proposition.split(":", 1)[1].split(","))
        candidates = document.get("candidates", set())
        return len(candidates) >= 2 and candidates <= supported
    if proposition == "candidate-residual-dispositions":
        candidates = document.get("candidates", set())
        residuals = document.get("residuals", {})
        return (len(candidates) >= 2 and set(residuals) == candidates and
                all(value in _DISPOSITIONS for value in residuals.values()))
    if proposition == "root-cause-unresolved":
        return document.get("root_cause_status") == "unresolved"
    if proposition == "lesson-lift-record":
        return bool(document.get("decision") and document.get("reason") and
                    document.get("destination"))
    if proposition == "lesson-lift-activation":
        destination = document.get("destination")
        if destination in _MECHANICAL_DESTINATIONS:
            return (document.get("activation") == "observed-pass" and
                    bool(document.get("activation_evidence")))
        return document.get("activation") == "not-required"
    if proposition == "no-prevention-claim":
        return document.get("recurrence_prevented") is False
    if proposition == "mechanical-claim-contradicted":
        return (document.get("mechanical_claim") == "contradicted" and
                document.get("block_scope") == "dependent-actions-only")
    if proposition == "evidence-mismatch-named":
        return document.get("abnormality") == "evidence-mismatch"
    if proposition == "owner-judgment-preserved":
        return (document.get("owner_acceptance") == "risk-accepted" and
                document.get("owner_judgment") == "preserved-verbatim")
    if proposition == "audit-not-restarted":
        return document.get("audit_restart") is False
    raise ValueError(f"unsupported envelope matrix proposition: {proposition!r}")


def evaluate_property(fixture, property_name, texts, artifact_obj=None):
    contract = fixture.get("matrix_acceptance")
    if contract is None:
        return None
    if (not isinstance(contract, dict) or set(contract) !=
            {"schema", "properties"} or
            contract.get("schema") not in {FREE_TEXT_SCHEMA, ENVELOPE_SCHEMA} or
            not isinstance(contract.get("properties"), dict)):
        raise ValueError("matrix acceptance contract malformed")
    proposition = contract["properties"].get(property_name)
    if proposition is None:
        return None
    if not isinstance(proposition, str) or not proposition:
        raise ValueError("matrix proposition identity malformed")
    text = _assistant_text(texts)
    if contract["schema"] == ENVELOPE_SCHEMA:
        cell = fixture.get("id")
        if cell not in _STRUCTURED_CELLS:
            raise ValueError("matrix envelope cell invalid")
        passed = _evaluate_envelope(proposition, _parse_envelope(text, cell))
        evidence = f"matrix-envelope-v1:{proposition}"
    else:
        if fixture.get("id") in _STRUCTURED_CELLS:
            raise ValueError("structured matrix cell requires acceptance v2")
        passed = _evaluate_free_text(proposition, text, artifact_obj)
        evidence = f"matrix-proposition:{proposition}"
    return passed, evidence


def apply_overrides(fixture, texts, scored, artifact_obj=None, events=None):
    output = dict(scored)
    contract = fixture.get("matrix_acceptance") or {}
    acceptance_texts = texts
    if contract.get("schema") == ENVELOPE_SCHEMA:
        acceptance_texts = {"assistant": _exact_assistant_text(events)}
    for prop in fixture["properties"]:
        result = evaluate_property(
            fixture, prop["name"], acceptance_texts,
            artifact_obj=artifact_obj)
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
