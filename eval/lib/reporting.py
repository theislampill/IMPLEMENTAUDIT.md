"""Fail-closed reconstruction of public claims from stored eval verdicts."""
from __future__ import annotations


class ClaimNotReconstructible(ValueError):
    """The requested claim is absent from or contradicted by stored data."""


def _required_names(fixture):
    return [p["name"] for p in fixture.get("properties", [])
            if p.get("required", True)]


def reconstruct_required_matrix(verdict, fixture):
    """Return required property booleans or refuse incomplete/inconsistent data."""
    required = _required_names(fixture)
    if not required:
        raise ClaimNotReconstructible(
            "fixture declares no required properties; ceiling is undefined")
    props = verdict.get("properties")
    adj = verdict.get("adjudication")
    if not isinstance(props, dict) or not isinstance(adj, dict):
        raise ClaimNotReconstructible(
            "verdict lacks layered properties/adjudication")
    if adj.get("property_evidence_complete") is not True:
        raise ClaimNotReconstructible("property evidence is incomplete")

    matrix = {}
    for name in required:
        item = props.get(name)
        if not isinstance(item, dict):
            raise ClaimNotReconstructible(
                f"required property {name!r} is missing")
        value = item.get("pass")
        state = item.get("state")
        if not isinstance(value, bool) or state not in ("PASS", "FAIL"):
            raise ClaimNotReconstructible(
                f"required property {name!r} is incomplete")
        if (state == "PASS") != value:
            raise ClaimNotReconstructible(
                f"required property {name!r} state contradicts pass value")
        if not item.get("evidence"):
            raise ClaimNotReconstructible(
                f"required property {name!r} has no evidence reference")
        matrix[name] = value

    computed = all(matrix.values())
    if adj.get("all_required_properties_true") is not computed:
        raise ClaimNotReconstructible(
            "adjudication contradicts the stored property matrix")
    return matrix


def require_all_required_true(verdicts, fixture, claim):
    """Admit a ceiling-style claim only when every verdict reconstructs TRUE."""
    if not verdicts:
        raise ClaimNotReconstructible(f"{claim}: no verdicts")
    matrices = []
    for index, verdict in enumerate(verdicts):
        matrix = reconstruct_required_matrix(verdict, fixture)
        if not all(matrix.values()):
            failed = sorted(k for k, value in matrix.items() if not value)
            raise ClaimNotReconstructible(
                f"{claim}: verdict {index} has failed properties {failed}")
        matrices.append(matrix)
    return matrices


def assert_replay_matches(verdict, rescored, fixture):
    """Require independent event rescoring to match the recorded matrix."""
    recorded = reconstruct_required_matrix(verdict, fixture)
    replay = {}
    for name in _required_names(fixture):
        item = rescored.get(name)
        if not isinstance(item, dict) or not isinstance(item.get("pass"), bool):
            raise ClaimNotReconstructible(
                f"replay lacks boolean result for {name!r}")
        replay[name] = item["pass"]
    if replay != recorded:
        raise ClaimNotReconstructible(
            f"independent replay mismatch: recorded={recorded} replay={replay}")
    return recorded
