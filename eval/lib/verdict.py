"""Per-run verdict envelope (#9 harness).

Four-valued status — do not collapse categories:
  PASS    valid run proved all required invariants
  FAIL    valid run violated a product invariant
  INVALID identity/schema/transcript/fixture/evidence/custody malformed or
          insufficient for adjudication
  ERROR   harness/host/infrastructure failure prevented adjudication
"""
from __future__ import annotations

import json
import os

VERDICT_SCHEMA = "implementaudit-eval-verdict-v1"
STATUSES = ("PASS", "FAIL", "INVALID", "ERROR")

_MANIFEST_COPY_FIELDS = (
    "run_id", "fixture_id", "fixture_sha256", "prompt_sha256",
    "events_sha256", "product_tag", "product_commit", "product_tree",
    "installed_payload_sha256", "harness_commit", "adapter_name",
    "adapter_version", "adapter_sha256", "model_requested",
    "model_resolved", "host", "started_at", "ended_at",
)


def build_verdict(status, manifest=None, properties=None,
                  failed_invariant=None, evidence=None, reason=None):
    if status not in STATUSES:
        raise ValueError(f"unknown status: {status!r}")
    verdict = {"schema": VERDICT_SCHEMA, "status": status}
    manifest = manifest or {}
    for field in _MANIFEST_COPY_FIELDS:
        verdict[field] = manifest.get(field)
    verdict["properties"] = properties or {}
    verdict["failed_invariant"] = failed_invariant
    verdict["evidence"] = evidence or []
    verdict["reason"] = reason
    return verdict


def write_verdict(bundle_root, verdict):
    path = os.path.join(bundle_root, "verdict.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1, sort_keys=True)
    return path
