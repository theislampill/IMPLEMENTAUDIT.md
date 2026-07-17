"""Run-bundle loading and validation (#9 harness trust boundary).

TRUST MODEL
-----------
The scorer trusts ONLY fields assigned out-of-band by the host adapter or the
trusted replay-bundle builder (`write_bundle`). Role labels, run IDs, and
sequence numbers inside a bundle are authoritative because the bundle is
produced in a location the evaluated model cannot write — NOT because any
string says so. A string inside model/user content such as "ASSISTANT:" or a
JSON-looking role object is data, never authority. A `"source"` field is not
proof and is deliberately not consulted.

IDENTITY BINDING (Phase C)
--------------------------
- Hash fields are strictly validated (64 lowercase hex; commits/trees 40).
- Timestamps must be RFC3339 UTC and `started_at <= ended_at`.
- The bundle CARRIES `fixture.json` and `prompt.txt`; both are hash-bound in
  the manifest. Integrity (bytes match the manifest hash) is verified here;
  AUTHENTICITY (the fixture is the canonical library fixture) is verified by
  the scorer against the local fixture file's hash. A nonempty string is
  never accepted as identity proof.
- Artifacts are enumerated in `artifact-manifest.json` (path -> sha256),
  itself hash-bound via `manifest.artifact_manifest_sha256`. A required
  artifact that is missing/malformed/hash-mismatched is INVALID — never a
  silent fallback.
- Product/payload/adapter/host identities are format-validated and RECORDED;
  they are adapter-attested at capture time and are marked "attested" (not
  independently re-verified) in replay verdicts. `model_requested` and
  `model_resolved` are both required; a mismatch is a SUBSTITUTION and is
  recorded honestly in the verdict rather than silently accepted or hidden.

CREATE-ONCE
-----------
`write_bundle` creates the run root exclusively and opens every file with
exclusive creation; it can never overwrite existing evidence. Scoring never
mutates a bundle (verdicts are separate create-once records — verdict.py).

Bundle layout:

    <run-root>/
      manifest.json          identity + hash bindings
      fixture.json           immutable copy of the fixture spec
      prompt.txt             immutable prompt/mission text
      events.jsonl           one validated host event per line
      repo-before.json       mechanical repository snapshots (reposnapshot)
      repo-after.json
      repo-comparison.json   optional bound comparison (when the scorer has
                             no repo access and heads differ)
      artifact-manifest.json path -> sha256 for everything under artifacts/
      artifacts/             result artifacts (model claims / host obs)
      verdict.json           written by the scorer (verdict.py, create-once)
"""
from __future__ import annotations

import hashlib
import json
import os
import re

EVENT_SCHEMA = "implementaudit-eval-event-v1"
MANIFEST_SCHEMA = "implementaudit-eval-manifest-v2"
ALLOWED_ROLES = ("system", "user", "assistant", "tool")
ALLOWED_KINDS = ("message", "marker", "action", "artifact")

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")

_HASH64_FIELDS = ("fixture_sha256", "prompt_sha256", "events_sha256",
                  "installed_payload_sha256", "adapter_sha256",
                  "repo_before_sha256", "repo_after_sha256")
_HASH40_FIELDS = ("product_commit", "product_tree", "harness_commit")

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


def _read_bound(root, name, expected_hash, required=True):
    path = os.path.join(root, name)
    if not os.path.isfile(path):
        if required:
            raise BundleInvalid(f"{name} missing")
        return None
    data = open(path, "rb").read()
    if _sha256_bytes(data) != expected_hash:
        raise BundleInvalid(f"{name} hash does not match manifest binding")
    return data


def _validate_manifest(manifest):
    if not isinstance(manifest, dict):
        raise BundleInvalid("manifest.json is not an object")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise BundleInvalid(f"unknown manifest schema: {manifest.get('schema')!r}")
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest or manifest[field] in (None, ""):
            raise BundleInvalid(f"manifest field missing/empty: {field}")
    for field in _HASH64_FIELDS:
        v = manifest[field]
        if v != "absent" and not (isinstance(v, str) and HEX64.match(v)):
            raise BundleInvalid(f"manifest {field} not 64 lowercase hex: {v!r}")
    for field in _HASH40_FIELDS:
        v = manifest[field]
        if not (isinstance(v, str) and HEX40.match(v)):
            raise BundleInvalid(f"manifest {field} not 40 lowercase hex: {v!r}")
    amh = manifest.get("artifact_manifest_sha256")
    if amh is not None and not (isinstance(amh, str) and HEX64.match(amh)):
        raise BundleInvalid("artifact_manifest_sha256 not 64 lowercase hex")
    for field in ("started_at", "ended_at"):
        v = manifest[field]
        if not (isinstance(v, str) and RFC3339.match(v)):
            raise BundleInvalid(f"manifest {field} not RFC3339: {v!r}")
    if manifest["started_at"] > manifest["ended_at"]:
        raise BundleInvalid("timestamp inversion: started_at > ended_at")


def load_bundle(root, expected_fixture=None):
    """Validate and return (manifest, events, fixture_obj, artifact_map).

    artifact_map: {relpath: verified bytes} for every artifact enumerated in
    artifact-manifest.json. Raises BundleInvalid on any defect.
    """
    manifest_path = os.path.join(root, "manifest.json")
    if not os.path.isfile(manifest_path):
        raise BundleInvalid("manifest.json missing")
    try:
        manifest = json.load(open(manifest_path, encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BundleInvalid(f"manifest.json malformed: {exc}")
    _validate_manifest(manifest)
    if expected_fixture is not None and manifest["fixture_id"] != expected_fixture:
        raise BundleInvalid(
            f"fixture mismatch: manifest={manifest['fixture_id']!r} "
            f"expected={expected_fixture!r}")

    fixture_bytes = _read_bound(root, "fixture.json",
                                manifest["fixture_sha256"])
    try:
        fixture_obj = json.loads(fixture_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BundleInvalid(f"bundled fixture.json malformed: {exc}")
    if fixture_obj.get("id") != manifest["fixture_id"]:
        raise BundleInvalid("bundled fixture id differs from manifest fixture_id")

    _read_bound(root, "prompt.txt", manifest["prompt_sha256"])

    raw = _read_bound(root, "events.jsonl", manifest["events_sha256"])
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
                raise BundleInvalid(f"event {lineno}: missing field {field!r}")
        if ev["schema"] != EVENT_SCHEMA:
            raise BundleInvalid(f"event {lineno}: unknown schema {ev['schema']!r}")
        if ev["run_id"] != manifest["run_id"]:
            raise BundleInvalid(
                f"event {lineno}: run_id mismatch (mixed runs)")
        if ev["fixture_id"] != manifest["fixture_id"]:
            raise BundleInvalid(f"event {lineno}: fixture_id mismatch")
        seq = ev["seq"]
        if not isinstance(seq, int) or isinstance(seq, bool) or seq <= last_seq:
            raise BundleInvalid(
                f"event {lineno}: seq must be strictly increasing int "
                f"(got {seq!r} after {last_seq})")
        last_seq = seq
        role = ev["role"]
        if not isinstance(role, str) or role not in ALLOWED_ROLES:
            raise BundleInvalid(f"event {lineno}: role {role!r} not allowed")
        if ev["kind"] not in ALLOWED_KINDS:
            raise BundleInvalid(f"event {lineno}: kind {ev['kind']!r} not allowed")
        if not isinstance(ev["content"], str):
            raise BundleInvalid(f"event {lineno}: content must be a string")
        events.append(ev)
    if not events:
        raise BundleInvalid("no events: a zero-event run is not adjudicable")

    for name, key in (("repo-before.json", "repo_before_sha256"),
                      ("repo-after.json", "repo_after_sha256")):
        if manifest[key] != "absent":
            _read_bound(root, name, manifest[key])
        elif os.path.isfile(os.path.join(root, name)):
            raise BundleInvalid(f"{name} present but not bound in manifest")

    artifact_map = {}
    amh = manifest.get("artifact_manifest_sha256")
    art_dir = os.path.join(root, "artifacts")
    if amh:
        am_bytes = _read_bound(root, "artifact-manifest.json", amh)
        try:
            am = json.loads(am_bytes.decode("utf-8"))
            files = am["files"]
            assert isinstance(files, dict)
        except Exception as exc:
            raise BundleInvalid(f"artifact-manifest.json malformed: {exc}")
        for rel, digest in files.items():
            if not (isinstance(digest, str) and HEX64.match(digest)):
                raise BundleInvalid(f"artifact hash malformed for {rel!r}")
            if ".." in rel.replace("\\", "/").split("/") or os.path.isabs(rel):
                raise BundleInvalid(f"artifact path rejected: {rel!r}")
            path = os.path.join(art_dir, rel)
            if not os.path.isfile(path):
                raise BundleInvalid(f"artifact missing: {rel!r}")
            data = open(path, "rb").read()
            if _sha256_bytes(data) != digest:
                raise BundleInvalid(f"artifact hash mismatch: {rel!r}")
            artifact_map[rel] = data
    elif os.path.isdir(art_dir) and any(os.scandir(art_dir)):
        raise BundleInvalid("artifacts present but no bound artifact-manifest")

    return manifest, events, fixture_obj, artifact_map


def bundle_content_hash(root, manifest):
    """Canonical hash over the complete verified input bundle, for verdict
    binding: manifest + events + snapshots + artifact manifest."""
    h = hashlib.sha256()
    for name in ("manifest.json", "fixture.json", "prompt.txt",
                 "events.jsonl", "repo-before.json", "repo-after.json",
                 "repo-comparison.json", "artifact-manifest.json"):
        path = os.path.join(root, name)
        if os.path.isfile(path):
            h.update(name.encode())
            h.update(open(path, "rb").read())
    return h.hexdigest()


def _write_exclusive(path, data):
    with open(path, "xb") as fh:
        fh.write(data)


def write_bundle(root, manifest_fields, events, fixture_bytes, prompt_bytes,
                 repo_before=None, repo_after=None, repo_comparison=None,
                 artifacts=None):
    """Trusted replay-bundle builder. CREATE-ONCE: the run root must not
    exist; every file is opened with exclusive creation; evidence is never
    overwritten. Hash bindings are computed here, independent of content.
    """
    try:
        os.makedirs(root, exist_ok=False)
    except FileExistsError:
        raise BundleInvalid(f"run root already exists (create-once): {root!r}")

    lines = [json.dumps(ev, sort_keys=True) for ev in events]
    events_bytes = ("\n".join(lines) + "\n").encode("utf-8")
    _write_exclusive(os.path.join(root, "events.jsonl"), events_bytes)
    _write_exclusive(os.path.join(root, "fixture.json"), fixture_bytes)
    _write_exclusive(os.path.join(root, "prompt.txt"), prompt_bytes)

    def _write_json(name, obj):
        data = json.dumps(obj, indent=1, sort_keys=True).encode("utf-8")
        _write_exclusive(os.path.join(root, name), data)
        return _sha256_bytes(data)

    manifest = dict(manifest_fields)
    manifest["schema"] = MANIFEST_SCHEMA
    manifest["events_sha256"] = _sha256_bytes(events_bytes)
    manifest["fixture_sha256"] = _sha256_bytes(fixture_bytes)
    manifest["prompt_sha256"] = _sha256_bytes(prompt_bytes)
    manifest["repo_before_sha256"] = (
        _write_json("repo-before.json", repo_before)
        if repo_before is not None else "absent")
    manifest["repo_after_sha256"] = (
        _write_json("repo-after.json", repo_after)
        if repo_after is not None else "absent")
    if repo_comparison is not None:
        manifest["repo_comparison_sha256"] = _write_json(
            "repo-comparison.json", repo_comparison)
    if artifacts:
        art_dir = os.path.join(root, "artifacts")
        os.makedirs(art_dir, exist_ok=False)
        files = {}
        for rel, data in sorted(artifacts.items()):
            path = os.path.join(art_dir, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            _write_exclusive(path, data)
            files[rel] = _sha256_bytes(data)
        manifest["artifact_manifest_sha256"] = _write_json(
            "artifact-manifest.json", {"files": files})
    _write_json("manifest.json", manifest)
    return manifest


def make_event(run_id, fixture_id, seq, role, content, kind="message",
               recorded_at="1970-01-01T00:00:00Z"):
    return {"schema": EVENT_SCHEMA, "run_id": run_id, "fixture_id": fixture_id,
            "seq": seq, "role": role, "kind": kind, "content": content,
            "recorded_at": recorded_at}
