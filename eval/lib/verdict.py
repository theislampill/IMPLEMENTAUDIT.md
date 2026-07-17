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

VERDICT_SCHEMA = "implementaudit-eval-verdict-v2"
STATUSES = ("PASS", "FAIL", "INVALID", "ERROR")

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


def build_verdict(status, manifest=None, properties=None,
                  failed_invariant=None, evidence=None, reason=None,
                  bundle_sha256=None, scorer_commit=None):
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
