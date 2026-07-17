"""Mechanical repository state snapshots (#9 harness).

`git status` alone is insufficient: a run can commit an unauthorized change
and present a clean working tree. Snapshots therefore record commit and tree
identities so before/after comparison detects committed changes too.

`changed_files` is COMPUTED from immutable before/after state by `compare`;
it is never accepted from model prose or an arbitrary adjacent summary file.
Unparseable repository state raises SnapshotInvalid (scored INVALID);
an unauthorized change is a product FAIL, decided by the scorer.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess


class SnapshotInvalid(Exception):
    """Repository state could not be read mechanically."""


def _git(repo_dir, *args):
    proc = subprocess.run(["git", "-C", repo_dir, *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise SnapshotInvalid(
            f"git {' '.join(args)} failed: {proc.stderr.strip()[:200]}")
    return proc.stdout


def _hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError as exc:
        raise SnapshotInvalid(f"cannot hash untracked file {path}: {exc}")
    return h.hexdigest()


def snapshot(repo_dir):
    """Return a mechanical snapshot dict of the repository state."""
    head_commit = _git(repo_dir, "rev-parse", "HEAD").strip()
    head_tree = _git(repo_dir, "rev-parse", "HEAD^{tree}").strip()
    index_tree = _git(repo_dir, "write-tree").strip()
    status = _git(repo_dir, "status", "--porcelain=v2", "-z")
    worktree_changed = []
    untracked = {}
    for entry in status.split("\0"):
        if not entry:
            continue
        code = entry.split(" ", 1)[0]
        if code in ("1", "2"):
            # ordinary/renamed change record: path is the last field
            worktree_changed.append(entry.split(" ")[-1])
        elif code == "?":
            path = entry[2:]
            untracked[path] = _hash_file(f"{repo_dir}/{path}")
    diff_patch = _git(repo_dir, "diff", "HEAD")
    snap = {
        "schema": "implementaudit-repo-snapshot-v1",
        "head_commit": head_commit,
        "head_tree": head_tree,
        "index_tree": index_tree,
        "worktree_changed": sorted(worktree_changed),
        "untracked": untracked,
        "tracked_diff_sha256": hashlib.sha256(
            diff_patch.encode("utf-8")).hexdigest(),
    }
    snap["snapshot_sha256"] = hashlib.sha256(
        json.dumps(snap, sort_keys=True).encode("utf-8")).hexdigest()
    return snap


def compare(repo_dir, before, after, allowed_paths=()):
    """Compute changed files from immutable before/after identities.

    Returns {changed_files, unauthorized, committed_change}. Requires repo
    access to enumerate a committed range; detects committed changes even
    when the final working tree is clean (head/tree identity comparison).
    """
    for snap in (before, after):
        if not isinstance(snap, dict) or \
                snap.get("schema") != "implementaudit-repo-snapshot-v1" or \
                "head_commit" not in snap or "head_tree" not in snap:
            raise SnapshotInvalid("malformed repository snapshot")
    changed = set(after.get("worktree_changed", []))
    before_untracked = set(before.get("untracked", {}))
    for path, digest in after.get("untracked", {}).items():
        if path not in before_untracked or \
                before["untracked"].get(path) != digest:
            changed.add(path)
    committed_change = before["head_commit"] != after["head_commit"]
    if committed_change:
        names = _git(repo_dir, "diff", "--name-only",
                     before["head_commit"], after["head_commit"])
        changed.update(n for n in names.splitlines() if n)
    unauthorized = sorted(
        p for p in changed
        if not any(fnmatch.fnmatch(p, g) for g in allowed_paths))
    return {"changed_files": sorted(changed),
            "unauthorized": unauthorized,
            "committed_change": committed_change}
