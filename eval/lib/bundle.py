"""Run-bundle loading and validation (#9 harness trust boundary).

TRUST MODEL
-----------
The scorer trusts ONLY fields assigned out-of-band by the host adapter or the
trusted replay-bundle builder (`write_bundle`). Role labels, run IDs, and
sequence numbers inside a bundle are authoritative because the bundle is
produced in a location the evaluated model cannot write — NOT because any
string says so. A string inside model/user content such as "ASSISTANT:" or a
JSON-looking role object is data, never authority. A `"source"` field is not
proof by itself and is deliberately not consulted for trust decisions.

Bundle layout:

    <run-root>/
      manifest.json        identity + hashes binding everything below
      events.jsonl         one validated host event per line
      repo-before.json     mechanical repository snapshot (reposnapshot.py)
      repo-after.json
      artifacts/           optional model-produced result artifacts
      verdict.json         written by the scorer (verdict.py)

Validation is fail-closed: anything malformed, truncated, mixed, duplicated,
or unbound raises BundleInvalid, which the runner reports as status INVALID —
never FAIL and never PASS.
"""
from __future__ import annotations

import hashlib
import json
import os

EVENT_SCHEMA = "implementaudit-eval-event-v1"
MANIFEST_SCHEMA = "implementaudit-eval-manifest-v1"
ALLOWED_ROLES = ("system", "user", "assistant", "tool")
ALLOWED_KINDS = ("message", "marker", "action", "artifact")
REQUIRED_MANIFEST_FIELDS = (
    "schema", "run_id", "fixture_id", "fixture_sha256", "prompt_sha256",
    "product_tag", "product_commit", "product_tree",
    "installed_payload_sha256", "harness_commit",
    "adapter_name", "adapter_version", "adapter_sha256",
    "model_requested", "model_resolved", "host",
    "started_at", "ended_at", "events_sha256",
    "repo_before_sha256", "repo_after_sha256",
)
REQUIRED_EVENT_FIELDS = ("schema", "run_id", "fixture_id", "seq", "role",
                         "kind", "content", "recorded_at")


class BundleInvalid(Exception):
    """The bundle cannot be adjudicated; scorer must report INVALID."""


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    with open(path, "rb") as fh:
        return _sha256_bytes(fh.read())


def load_bundle(root, expected_fixture=None):
    """Validate and return (manifest, events). Raises BundleInvalid."""
    manifest_path = os.path.join(root, "manifest.json")
    events_path = os.path.join(root, "events.jsonl")
    if not os.path.isfile(manifest_path):
        raise BundleInvalid("manifest.json missing")
    if not os.path.isfile(events_path):
        raise BundleInvalid("events.jsonl missing")
    try:
        manifest = json.load(open(manifest_path, encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BundleInvalid(f"manifest.json malformed: {exc}")
    if not isinstance(manifest, dict):
        raise BundleInvalid("manifest.json is not an object")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise BundleInvalid(f"unknown manifest schema: {manifest.get('schema')!r}")
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest or manifest[field] in (None, ""):
            raise BundleInvalid(f"manifest field missing/empty: {field}")
    if expected_fixture is not None and manifest["fixture_id"] != expected_fixture:
        raise BundleInvalid(
            f"fixture mismatch: manifest={manifest['fixture_id']!r} "
            f"expected={expected_fixture!r}")

    raw = open(events_path, "rb").read()
    if _sha256_bytes(raw) != manifest["events_sha256"]:
        raise BundleInvalid("events.jsonl hash does not match manifest binding")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BundleInvalid(f"events.jsonl not valid UTF-8: {exc}")

    events = []
    last_seq = 0
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    for lineno, line in enumerate(lines, 1):
        try:
            ev = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BundleInvalid(
                f"events.jsonl line {lineno} malformed/truncated: {exc}")
        if not isinstance(ev, dict):
            raise BundleInvalid(f"events.jsonl line {lineno} is not an object")
        for field in REQUIRED_EVENT_FIELDS:
            if field not in ev:
                raise BundleInvalid(
                    f"event {lineno}: missing field {field!r}")
        if ev["schema"] != EVENT_SCHEMA:
            raise BundleInvalid(f"event {lineno}: unknown schema {ev['schema']!r}")
        if ev["run_id"] != manifest["run_id"]:
            raise BundleInvalid(
                f"event {lineno}: run_id {ev['run_id']!r} does not match "
                f"manifest run_id {manifest['run_id']!r} (mixed runs)")
        if ev["fixture_id"] != manifest["fixture_id"]:
            raise BundleInvalid(
                f"event {lineno}: fixture_id mismatch (mixed fixtures)")
        seq = ev["seq"]
        if not isinstance(seq, int) or isinstance(seq, bool) or seq <= last_seq:
            raise BundleInvalid(
                f"event {lineno}: seq must be a strictly increasing int "
                f"(got {seq!r} after {last_seq})")
        last_seq = seq
        role = ev["role"]
        if not isinstance(role, str) or role not in ALLOWED_ROLES:
            # exact ASCII enum: Unicode confusables and unknown roles are
            # INVALID, never coerced.
            raise BundleInvalid(f"event {lineno}: role {role!r} not allowed")
        if ev["kind"] not in ALLOWED_KINDS:
            raise BundleInvalid(f"event {lineno}: kind {ev['kind']!r} not allowed")
        if not isinstance(ev["content"], str):
            raise BundleInvalid(f"event {lineno}: content must be a string")
        events.append(ev)
    if not events:
        raise BundleInvalid("no events: a zero-event run is not adjudicable")

    # Bind the repository snapshots when present.
    for name, key in (("repo-before.json", "repo_before_sha256"),
                      ("repo-after.json", "repo_after_sha256")):
        path = os.path.join(root, name)
        if os.path.isfile(path):
            if sha256_file(path) != manifest[key]:
                raise BundleInvalid(f"{name} hash does not match manifest binding")
    return manifest, events


def write_bundle(root, manifest_fields, events, repo_before=None,
                 repo_after=None):
    """Trusted replay-bundle builder: constructs identity fields and hash
    bindings itself, independent of raw content. For host adapters and tests.
    """
    os.makedirs(root, exist_ok=True)
    lines = []
    for ev in events:
        lines.append(json.dumps(ev, sort_keys=True))
    events_bytes = ("\n".join(lines) + "\n").encode("utf-8")
    with open(os.path.join(root, "events.jsonl"), "wb") as fh:
        fh.write(events_bytes)

    def _write_json(name, obj):
        data = json.dumps(obj, indent=1, sort_keys=True).encode("utf-8")
        with open(os.path.join(root, name), "wb") as fh:
            fh.write(data)
        return _sha256_bytes(data)

    manifest = dict(manifest_fields)
    manifest["schema"] = MANIFEST_SCHEMA
    manifest["events_sha256"] = _sha256_bytes(events_bytes)
    manifest["repo_before_sha256"] = (
        _write_json("repo-before.json", repo_before) if repo_before is not None
        else manifest.get("repo_before_sha256", "absent"))
    manifest["repo_after_sha256"] = (
        _write_json("repo-after.json", repo_after) if repo_after is not None
        else manifest.get("repo_after_sha256", "absent"))
    _write_json("manifest.json", manifest)
    return manifest


def make_event(run_id, fixture_id, seq, role, content, kind="message",
               recorded_at="1970-01-01T00:00:00Z"):
    return {"schema": EVENT_SCHEMA, "run_id": run_id, "fixture_id": fixture_id,
            "seq": seq, "role": role, "kind": kind, "content": content,
            "recorded_at": recorded_at}
