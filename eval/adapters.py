#!/usr/bin/env python3
"""Host-adapter framework for #9 — INERT: no code path here invokes a model.

An adapter's job is everything AROUND the model call:
  prepare : disposable fixture repository (fresh git repo seeded from the
            fixture), fresh temporary model home, immutable product install,
            capture-time identity computation (product tag/commit/tree,
            installed-payload hash, adapter self-hash), BEFORE snapshot, and
            a custody-approved run root the evaluated model cannot write.
  (model call happens here — NOT IMPLEMENTED; gated on the owner-approved
   baseline packet. There is deliberately no function that spawns a model.)
  finalize: AFTER snapshot, recomputed comparison, host-assigned events, and
            a CREATE-ONCE bundle via bundle.write_bundle.

Execution gating: real per-host adapters (codex/claude CLIs) are Phase-2b of
issue #9 and must call `require_owner_approval()` before ANY model spawn.
That gate fails closed: it refuses in CI unconditionally and otherwise
requires an owner-created approval token file. This module ships only the
framework, the identity helpers, the REPLAY adapter (builds bundles from
already-captured raw event records — fully testable without a model), and a
--plan mode that prints exactly what a real run would do.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import bundle as bundlelib  # noqa: E402
import custody  # noqa: E402
import reposnapshot  # noqa: E402


class AdapterError(Exception):
    pass


def require_owner_approval():
    """Fail-closed gate for any future model-spawning adapter."""
    if os.environ.get("CI"):
        raise AdapterError(
            "model execution is unconditionally refused in CI")
    token = os.environ.get("IMPLEMENTAUDIT_BASELINE_APPROVAL")
    if not token or not os.path.isfile(token):
        raise AdapterError(
            "no owner approval token: real runs require the owner-approved "
            "baseline packet (issue #9); set IMPLEMENTAUDIT_BASELINE_APPROVAL "
            "to the packet acknowledgement file the owner created")
    return token


def _git(cwd, *args):
    proc = subprocess.run(["git", "-C", cwd, *args], capture_output=True,
                          text=True)
    if proc.returncode != 0:
        raise AdapterError(f"git {' '.join(args)}: {proc.stderr.strip()[:200]}")
    return proc.stdout.strip()


def product_identity(product_checkout, expected_tag="v0.3.1.0"):
    """Capture-time verification the replay scorer cannot do: the product
    tag/commit/tree are read from the ACTUAL evaluation checkout."""
    commit = _git(product_checkout, "rev-parse", f"{expected_tag}^{{commit}}")
    tree = _git(product_checkout, "rev-parse", f"{expected_tag}^{{tree}}")
    head = _git(product_checkout, "rev-parse", "HEAD")
    if head != commit:
        raise AdapterError(
            f"evaluation checkout HEAD {head[:12]} is not the immutable "
            f"{expected_tag} commit {commit[:12]} — refuse to attest")
    return {"product_tag": expected_tag, "product_commit": commit,
            "product_tree": tree}


def payload_hash(installed_dir):
    """Deterministic hash of an installed payload directory."""
    h = hashlib.sha256()
    for root, dirs, files in os.walk(installed_dir):
        dirs.sort()
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, installed_dir).replace("\\", "/")
            h.update(rel.encode())
            h.update(open(path, "rb").read())
    return h.hexdigest()


def adapter_self_hash():
    return bundlelib.sha256_file(os.path.abspath(__file__))


def seed_fixture_repo(fixture_id, work_root):
    """Create the disposable evaluation repository for a fixture: a fresh
    git repo populated from eval/fixtures/<id>/seed/ when present."""
    repo = os.path.join(work_root, f"fixture-repo-{fixture_id}")
    os.makedirs(repo, exist_ok=False)
    subprocess.run(["git", "init", "-q", repo], check=True)
    _git(repo, "config", "user.email", "eval@implementaudit")
    _git(repo, "config", "user.name", "eval-harness")
    seed = os.path.join(HERE, "fixtures", fixture_id, "seed")
    if os.path.isdir(seed):
        for root, _dirs, files in os.walk(seed):
            for name in files:
                src = os.path.join(root, name)
                rel = os.path.relpath(src, seed)
                dst = os.path.join(repo, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(src, "rb") as s, open(dst, "xb") as d:
                    d.write(s.read())
    else:
        open(os.path.join(repo, "README.md"), "x").write(
            f"seeded fixture repo for {fixture_id}\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", f"seed {fixture_id}")
    return repo


class ReplayAdapter:
    """Builds a scoreable bundle from ALREADY-CAPTURED raw host records —
    no model call. Raw records are a JSON list of {role, kind, content};
    this trusted builder assigns run/fixture/seq identity itself (the
    evaluated model never writes here)."""

    name = "replay"
    version = "1"

    def build(self, fixture_id, raw_events, run_id, custody_root,
              identities=None, repo_before=None, repo_after=None,
              repo_dir=None, artifacts=None):
        fixture_path = os.path.join(HERE, "fixtures", fixture_id,
                                    "fixture.json")
        fixture_bytes = open(fixture_path, "rb").read()
        mission = json.loads(fixture_bytes.decode())["mission"]
        run_root = custody.resolve_and_create_output_dir(custody_root, run_id)
        # the run root was created exclusively; hand bundle.write_bundle a
        # child directory so IT also creates exclusively
        bundle_root = os.path.join(run_root, "bundle")
        events = []
        for i, rec in enumerate(raw_events, 1):
            events.append(bundlelib.make_event(
                run_id, fixture_id, i, rec["role"], rec["content"],
                kind=rec.get("kind", "message")))
        fields = {
            "run_id": run_id, "fixture_id": fixture_id,
            "product_tag": "unattested", "product_commit": "0" * 40,
            "product_tree": "0" * 40,
            "installed_payload_sha256": "0" * 64,
            "harness_commit": "0" * 40,
            "adapter_name": self.name, "adapter_version": self.version,
            "adapter_sha256": adapter_self_hash(),
            "model_requested": "replay", "model_resolved": "replay",
            "host": "replay",
            "started_at": "1970-01-01T00:00:00Z",
            "ended_at": "1970-01-01T00:00:01Z",
        }
        fields.update(identities or {})
        repo_comparison = None
        if repo_before is not None and repo_after is not None and repo_dir:
            repo_comparison = reposnapshot.compare_with_repo(
                repo_dir, repo_before, repo_after)
        return bundlelib.write_bundle(
            bundle_root, fields, events, fixture_bytes,
            ("MISSION:\n" + mission).encode(),
            repo_before=repo_before, repo_after=repo_after,
            repo_comparison=repo_comparison, artifacts=artifacts), bundle_root


def cmd_plan(fixture_id):
    fixture = json.load(open(os.path.join(HERE, "fixtures", fixture_id,
                                          "fixture.json"), encoding="utf-8"))
    print(f"PLAN for {fixture_id} (nothing is executed):")
    print("  1. work_root = custody-approved directory OUTSIDE the repo")
    print("  2. seed_fixture_repo() -> disposable git repo")
    print("  3. fresh temp model home; install immutable v0.3.1.0 payload;")
    print("     product_identity(checkout) + payload_hash(install)")
    print("  4. repo-before snapshot (reposnapshot.snapshot)")
    print("  5. [MODEL CALL — NOT IMPLEMENTED; require_owner_approval()]")
    print(f"     mission: {fixture['mission'][:100]}...")
    print("  6. repo-after snapshot + compare_with_repo")
    print("  7. host-assigned events + artifacts -> bundle.write_bundle")
    print("  8. runner.py --bundle <root>/bundle --repo <fixture repo>")
    print("NO MODEL WAS CALLED.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--plan":
        raise SystemExit(cmd_plan(sys.argv[2]))
    print(__doc__)
    raise SystemExit(0)
