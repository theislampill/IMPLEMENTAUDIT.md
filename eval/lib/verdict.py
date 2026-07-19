"""Per-run verdict envelope (#9 harness).

Four-valued status — do not collapse categories:
  PASS    valid run proved all required invariants
  FAIL    valid run violated a product invariant
  INVALID identity/schema/transcript/fixture/evidence/custody malformed or
          insufficient for adjudication
  ERROR   harness/host/infrastructure failure prevented adjudication

Custody (Phase C): verdicts are CREATE-ONCE adjudication records. Raw bundle
evidence is never mutated. A second adjudication of the same bundle creates a
separately identified record (verdict-2.json, verdict-3.json, …); it never
silently rewrites the first. Each verdict binds the canonical hash of the
complete input bundle and records the scorer/harness identity, the identity
attestation split (verified vs adapter-attested), any model substitution,
the first failing invariant, and bound evidence references.
"""
from __future__ import annotations

import json
import os

VERDICT_SCHEMA = "implementaudit-eval-verdict-v3"
HOST_SAFETY_SCHEMA = "implementaudit-host-safety-v1"
ADJUDICATION_SCHEMA = "implementaudit-eval-adjudication-v1"
STATUSES = ("PASS", "FAIL", "INVALID", "ERROR")
HOST_STATUSES = ("PASS", "FAIL", "INVALID", "ERROR")

_MANIFEST_COPY_FIELDS = (
    "run_id", "fixture_id", "fixture_sha256", "prompt_sha256",
    "events_sha256", "product_tag", "product_commit", "product_tree",
    "installed_payload_sha256", "harness_commit", "adapter_name",
    "adapter_version", "adapter_sha256", "model_requested",
    "model_resolved", "host", "started_at", "ended_at",
)

# Identity fields the scorer VERIFIES in replay (hash/recompute) vs fields
# that are adapter-attested at capture time and only format-validated here.
VERIFIED_IN_REPLAY = (
    "fixture_sha256 (bytes + canonical-library authenticity)",
    "prompt_sha256 (bytes + mission consistency)",
    "events_sha256", "repo_before/after snapshot integrity",
    "artifact hashes via artifact-manifest",
)
ATTESTED_ONLY = (
    "product_tag/commit/tree", "installed_payload_sha256",
    "adapter_name/version/sha256", "host",
    "harness_commit (cross-checked when the scoring checkout is available)",
)


def materialize_properties(fixture, scored=None, incomplete_reason=None):
    """Persist one result for every declared property.

    Available scorer results retain the legacy boolean ``pass`` field and add
    an explicit PASS/FAIL state. When authentic evidence cannot be scored, the
    declared property remains visible as INCOMPLETE with ``pass: null``. An
    empty map therefore never means a ceiling result.
    """
    if not fixture:
        return {}
    scored = scored or {}
    out = {}
    for spec in fixture.get("properties", []):
        name = spec["name"]
        result = scored.get(name)
        if result is None:
            out[name] = {
                "state": "INCOMPLETE",
                "pass": None,
                "evidence": incomplete_reason or "property was not scored",
                "describes": spec.get("describes", ""),
                "basis": "incomplete",
            }
            continue
        item = dict(result)
        value = item.get("pass")
        if not isinstance(value, bool):
            item["state"] = "INCOMPLETE"
            item["pass"] = None
            item["evidence"] = (
                incomplete_reason or "scorer returned a non-boolean result")
        else:
            item["state"] = "PASS" if value else "FAIL"
        out[name] = item
    # Preserve non-scoring notes without letting them affect completeness.
    for name, result in scored.items():
        if name not in out:
            out[name] = dict(result)
    return out


def host_finding(gate, status, evidence=None, reason=None):
    if status not in HOST_STATUSES:
        raise ValueError(f"unknown host-safety status: {status!r}")
    return {"gate": gate, "status": status, "evidence": evidence or [],
            "reason": reason}


def compose_adjudication(fixture, scored=None, host_findings=None,
                         incomplete_reason=None):
    """Derive product, host, and overall results without collapsing layers."""
    properties = materialize_properties(
        fixture, scored=scored, incomplete_reason=incomplete_reason)
    required = [p["name"] for p in (fixture or {}).get("properties", [])
                if p.get("required", True)]
    # A fixture with no required properties cannot prove a product ceiling.
    # Treat the matrix as incomplete instead of accepting ``all([])``.
    complete = bool(required) and all(
        name in properties and properties[name].get("state") in ("PASS", "FAIL")
        for name in required)
    all_true = (all(properties[name].get("pass") is True for name in required)
                if complete else None)
    product_status = ("PASS" if all_true else "FAIL") if complete else \
        "INCOMPLETE"

    findings = list(host_findings or [])
    severity = {"PASS": 0, "FAIL": 1, "INVALID": 2, "ERROR": 3}
    host_status = max((f["status"] for f in findings),
                      key=lambda s: severity[s], default="PASS")
    if host_status == "ERROR":
        overall = "ERROR"
    elif host_status == "INVALID" or product_status == "INCOMPLETE":
        overall = "INVALID"
    elif host_status == "FAIL" or product_status == "FAIL":
        overall = "FAIL"
    else:
        overall = "PASS"

    product_failed = next(
        (name for name in required
         if properties.get(name, {}).get("state") == "FAIL"), None)
    first_host_failed = next(
        (f for f in findings if f.get("status") != "PASS"), None)
    host_failed = next(
        (f for f in findings if f["status"] == host_status), None)
    if overall in ("INVALID", "ERROR"):
        failed_domain = ("infrastructure" if overall == "ERROR"
                         else "identity-custody-or-evidence")
        failed_invariant = (host_failed or {}).get("gate") or \
            "property-evidence-incomplete"
    elif product_failed:
        failed_domain = "product-property"
        failed_invariant = product_failed
    elif host_failed:
        failed_domain = "host-safety"
        failed_invariant = host_failed.get("gate")
    else:
        failed_domain = None
        failed_invariant = None

    adjudication = {
        "schema": ADJUDICATION_SCHEMA,
        "product_status": product_status,
        "host_status": host_status,
        "overall_status": overall,
        "property_evidence_complete": complete,
        "all_required_properties_true": all_true,
        "product_failed_invariant": product_failed,
        "host_failed_invariant": (first_host_failed or {}).get("gate"),
        "host_failed_status": (first_host_failed or {}).get("status"),
        "failed_domain": failed_domain,
        "failed_invariant": failed_invariant,
    }
    host_safety = {"schema": HOST_SAFETY_SCHEMA, "status": host_status,
                   "failed_invariant": (first_host_failed or {}).get("gate"),
                   "failed_status": (first_host_failed or {}).get("status"),
                   "findings": findings}
    return overall, properties, host_safety, adjudication


def build_verdict(status, manifest=None, properties=None,
                  failed_invariant=None, evidence=None, reason=None,
                  bundle_sha256=None, scorer_commit=None, host_safety=None,
                  adjudication=None, failed_domain=None):
    if status not in STATUSES:
        raise ValueError(f"unknown status: {status!r}")
    verdict = {"schema": VERDICT_SCHEMA, "status": status}
    manifest = manifest or {}
    for field in _MANIFEST_COPY_FIELDS:
        verdict[field] = manifest.get(field)
    substitution = (manifest.get("model_requested") is not None
                    and manifest.get("model_requested") !=
                    manifest.get("model_resolved"))
    verdict["model_substitution"] = substitution
    if substitution:
        verdict["model_substitution_note"] = (
            f"requested {manifest.get('model_requested')!r} but resolved "
            f"{manifest.get('model_resolved')!r} — recorded honestly; "
            "the owner decides whether this run counts")
    verdict["identity_attestation"] = {
        "verified_in_replay": list(VERIFIED_IN_REPLAY),
        "adapter_attested_only": list(ATTESTED_ONLY),
    }
    verdict["bundle_sha256"] = bundle_sha256
    verdict["scorer_commit"] = scorer_commit
    verdict["properties"] = properties or {}
    verdict["host_safety"] = host_safety or {
        "schema": HOST_SAFETY_SCHEMA,
        "status": "PASS" if status == "PASS" else status,
        "failed_invariant": None,
        "failed_status": None,
        "findings": [],
    }
    verdict["adjudication"] = adjudication or {
        "schema": ADJUDICATION_SCHEMA,
        "product_status": "INCOMPLETE",
        "host_status": verdict["host_safety"]["status"],
        "overall_status": status,
        "property_evidence_complete": False,
        "all_required_properties_true": None,
        "product_failed_invariant": None,
        "host_failed_invariant": verdict["host_safety"].get(
            "failed_invariant"),
        "host_failed_status": verdict["host_safety"].get("failed_status"),
        "failed_domain": failed_domain,
        "failed_invariant": failed_invariant,
    }
    verdict["failed_domain"] = (
        failed_domain if failed_domain is not None
        else verdict["adjudication"].get("failed_domain"))
    verdict["failed_invariant"] = failed_invariant
    verdict["evidence"] = evidence or []
    verdict["reason"] = reason
    return verdict


def write_verdict(bundle_root, verdict):
    """Create-once: never overwrite an existing adjudication record."""
    base = os.path.join(bundle_root, "verdict.json")
    path, n = base, 1
    while True:
        try:
            with open(path, "x", encoding="utf-8") as fh:
                json.dump(verdict, fh, indent=1, sort_keys=True)
            return path
        except FileExistsError:
            n += 1
            if n > 50:
                raise
            path = os.path.join(bundle_root, f"verdict-{n}.json")
