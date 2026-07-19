"""Mechanical repository state snapshots (#9 harness).

`git status` alone is insufficient: a run can commit an unauthorized change
and present a clean working tree. Snapshots record commit and tree identities
so before/after comparison detects committed changes too.

Hardening (Phase C):
- Git output is captured as BYTES; the tracked diff uses
  `git diff --binary --full-index --no-ext-diff --no-color HEAD` so the diff
  identity is byte-stable for binary and encoding-sensitive content.
- `git status --porcelain=v2 -z --untracked-files=all` is parsed by record
  type with documented field counts, so paths containing spaces, renames
  (with the second NUL-delimited original path), deletions, staged-only and
  unstaged-only changes, and untracked nested files are all represented.
- Untracked entries are examined with lstat and NEVER followed: symlinks are
  recorded as {"type": "symlink", "target_sha256": ...}; directories and
  special files are represented explicitly.
- Every snapshot carries `snapshot_sha256` over its canonical JSON; loaders
  must call `verify_snapshot` before trusting one.
- `changed_files` is COMPUTED from immutable before/after state by the
  compare functions; it is never accepted from model prose or an arbitrary
  adjacent summary.

Unparseable state raises SnapshotInvalid (scored INVALID); an unauthorized
change is a product FAIL, decided by the scorer.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat as statmod
import subprocess

SCHEMA = "implementaudit-repo-snapshot-v2"


class SnapshotInvalid(Exception):
    """Repository state could not be read or verified mechanically."""


def _git_bytes(repo_dir, *args):
    proc = subprocess.run(["git", "-C", repo_dir, *args],
                          capture_output=True)
    if proc.returncode != 0:
        raise SnapshotInvalid(
            f"git {' '.join(args)} failed: "
            f"{proc.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return proc.stdout


def _git_text(repo_dir, *args):
    return _git_bytes(repo_dir, *args).decode("utf-8", "replace").strip()


def _hash_regular_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _untracked_entry(repo_dir, rel_path):
    """Represent an untracked path WITHOUT following links."""
    full = os.path.join(repo_dir, rel_path)
    try:
        st = os.lstat(full)
    except OSError as exc:
        raise SnapshotInvalid(f"cannot lstat untracked {rel_path!r}: {exc}")
    reparse = getattr(st, "st_file_attributes", 0) & getattr(
        statmod, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if statmod.S_ISLNK(st.st_mode) or reparse:
        try:
            target = os.readlink(full)
        except OSError:
            target = "<unreadable>"
        return {"type": "symlink",
                "target_sha256": hashlib.sha256(
                    target.encode("utf-8", "replace")).hexdigest()}
    if statmod.S_ISDIR(st.st_mode):
        return {"type": "dir"}
    if not statmod.S_ISREG(st.st_mode):
        return {"type": "special"}
    return {"type": "file", "sha256": _hash_regular_file(full)}


def _worktree_entry(path):
    """Describe one worktree leaf without following links or junctions."""
    try:
        st = os.lstat(path)
    except OSError as exc:
        raise SnapshotInvalid(f"cannot lstat worktree path {path!r}: {exc}")
    reparse = getattr(st, "st_file_attributes", 0) & getattr(
        statmod, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if statmod.S_ISLNK(st.st_mode) or reparse:
        try:
            target = os.readlink(path)
        except OSError:
            target = "<unreadable>"
        return {"type": "symlink",
                "target_sha256": hashlib.sha256(
                    target.encode("utf-8", "replace")).hexdigest()}
    if statmod.S_ISREG(st.st_mode):
        return {"type": "file", "sha256": _hash_regular_file(path)}
    return {"type": "special"}


def _worktree_file_map(repo_dir):
    """Hash every repository worktree leaf, excluding Git's own metadata.

    This complete map lets an offline scorer bind retained host-check input
    bytes to the exact after-state rather than trusting an adapter Boolean.
    Directory links/junctions are recorded but never traversed.
    """
    out = {}
    root_abs = os.path.abspath(repo_dir)
    for root, dirs, files in os.walk(root_abs, topdown=True,
                                     followlinks=False):
        dirs.sort()
        files.sort()
        if os.path.abspath(root) == root_abs:
            # A normal checkout exposes .git as a directory; a linked
            # worktree exposes it as an administrative pointer file. Neither
            # is repository content and neither may influence evidence hashes.
            dirs[:] = [name for name in dirs
                       if os.path.normcase(name) != os.path.normcase(".git")]
            files = [name for name in files
                     if os.path.normcase(name) != os.path.normcase(".git")]
        for name in list(dirs):
            path = os.path.join(root, name)
            entry = _worktree_entry(path)
            if entry["type"] != "special":
                if entry["type"] == "symlink":
                    rel = os.path.relpath(path, root_abs).replace("\\", "/")
                    out[rel] = entry
                    dirs.remove(name)
            elif not os.path.isdir(path):
                rel = os.path.relpath(path, root_abs).replace("\\", "/")
                out[rel] = entry
                dirs.remove(name)
        for name in files:
            path = os.path.join(root, name)
            rel = os.path.relpath(path, root_abs).replace("\\", "/")
            out[rel] = _worktree_entry(path)
    return out


def _parse_status_z(raw):
    """Parse `git status --porcelain=v2 -z --untracked-files=all` bytes.

    Returns (staged, unstaged, renames, untracked_paths).
    Record types (documented fixed field counts before the path):
      '1 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <path>'          (8 fields)
      '2 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <X><score> <path>' + NUL + <orig>
      'u <XY> <sub> <m1> <m2> <m3> <mW> <h1> <h2> <h3> <path>' (10 fields)
      '? <path>'    '! <path>'
    """
    staged, unstaged, renames, untracked = [], [], {}, []
    tokens = raw.split(b"\0")
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        if not tok:
            continue
        kind = tok[:1]
        try:
            if kind == b"1":
                parts = tok.split(b" ", 8)
                xy = parts[1].decode("ascii", "replace")
                path = parts[8].decode("utf-8", "replace")
                if xy[0] != ".":
                    staged.append(path)
                if xy[1] != ".":
                    unstaged.append(path)
            elif kind == b"2":
                parts = tok.split(b" ", 9)
                xy = parts[1].decode("ascii", "replace")
                path = parts[9].decode("utf-8", "replace")
                if i >= len(tokens):
                    raise SnapshotInvalid("rename record missing orig path")
                orig = tokens[i].decode("utf-8", "replace")
                i += 1
                renames[path] = orig
                if xy[0] != ".":
                    staged.append(path)
                if xy[1] != ".":
                    unstaged.append(path)
            elif kind == b"u":
                parts = tok.split(b" ", 10)
                path = parts[10].decode("utf-8", "replace")
                staged.append(path)
                unstaged.append(path)
            elif kind == b"?":
                untracked.append(tok[2:].decode("utf-8", "replace"))
            elif kind == b"!":
                continue
            else:
                raise SnapshotInvalid(
                    f"unknown status record type: {tok[:20]!r}")
        except (IndexError, UnicodeDecodeError) as exc:
            raise SnapshotInvalid(f"malformed status record {tok[:40]!r}: {exc}")
    return sorted(set(staged)), sorted(set(unstaged)), renames, untracked


def snapshot(repo_dir):
    """Return a verified mechanical snapshot dict of the repository state."""
    head_commit = _git_text(repo_dir, "rev-parse", "HEAD")
    head_tree = _git_text(repo_dir, "rev-parse", "HEAD^{tree}")
    index_tree = _git_text(repo_dir, "write-tree")
    raw = _git_bytes(repo_dir, "status", "--porcelain=v2", "-z",
                     "--untracked-files=all")
    staged, unstaged, renames, untracked_paths = _parse_status_z(raw)
    untracked = {p: _untracked_entry(repo_dir, p) for p in untracked_paths}
    diff = _git_bytes(repo_dir, "diff", "--binary", "--full-index",
                      "--no-ext-diff", "--no-color", "HEAD")
    snap = {
        "schema": SCHEMA,
        "head_commit": head_commit,
        "head_tree": head_tree,
        "index_tree": index_tree,
        "staged": staged,
        "unstaged": unstaged,
        "renames": renames,
        "untracked": untracked,
        "worktree_files": _worktree_file_map(repo_dir),
        "tracked_diff_sha256": hashlib.sha256(diff).hexdigest(),
    }
    snap["snapshot_sha256"] = _canonical_hash(snap)
    return snap


def _canonical_hash(snap):
    body = {k: v for k, v in snap.items() if k not in
            ("snapshot_sha256", "changed_files", "unauthorized")}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()


def verify_snapshot(snap):
    """Validate structure and internal hash; raise SnapshotInvalid."""
    if not isinstance(snap, dict) or snap.get("schema") != SCHEMA:
        raise SnapshotInvalid(
            f"malformed repository snapshot (schema {snap.get('schema') if isinstance(snap, dict) else type(snap)!r})")
    for field in ("head_commit", "head_tree", "index_tree", "staged",
                  "unstaged", "untracked", "tracked_diff_sha256",
                  "snapshot_sha256"):
        if field not in snap:
            raise SnapshotInvalid(f"snapshot missing field {field!r}")
    if _canonical_hash(snap) != snap["snapshot_sha256"]:
        raise SnapshotInvalid("snapshot_sha256 does not match content")
    worktree_files = snap.get("worktree_files")
    if worktree_files is not None:
        if not isinstance(worktree_files, dict):
            raise SnapshotInvalid("snapshot worktree_files is not an object")
        for rel, entry in worktree_files.items():
            norm = str(rel).replace("\\", "/")
            if (not isinstance(rel, str) or not rel or
                    norm.startswith("/") or ".." in norm.split("/") or
                    not isinstance(entry, dict)):
                raise SnapshotInvalid(
                    f"snapshot worktree file identity invalid: {rel!r}")
            kind = entry.get("type")
            if kind == "file":
                digest = entry.get("sha256")
            elif kind == "symlink":
                digest = entry.get("target_sha256")
            elif kind == "special":
                digest = None
            else:
                raise SnapshotInvalid(
                    f"snapshot worktree file type invalid: {kind!r}")
            if digest is not None and (not isinstance(digest, str) or
                    len(digest) != 64 or
                    any(c not in "0123456789abcdef" for c in digest)):
                raise SnapshotInvalid(
                    f"snapshot worktree digest invalid: {rel!r}")


def _norm_globs(globs):
    out = []
    for g in globs:
        g = g.replace("\\", "/")
        if g.startswith("/") or ".." in g.split("/"):
            raise SnapshotInvalid(f"allowed path glob rejected: {g!r}")
        out.append(g)
    return out


def compare_pure(before, after):
    """Worktree/untracked/staged delta computed purely from two verified
    snapshots (no repository access). Committed changes are FLAGGED (head
    mismatch) but their file list needs repo access or a bound comparison
    record — see compare_with_repo.
    """
    verify_snapshot(before)
    verify_snapshot(after)
    changed = set(after.get("staged", [])) | set(after.get("unstaged", []))
    before_untracked = before.get("untracked", {})
    for path, entry in after.get("untracked", {}).items():
        if before_untracked.get(path) != entry:
            changed.add(path)
    committed_change = before["head_commit"] != after["head_commit"]
    return {"schema": "implementaudit-repo-comparison-v1",
            "changed_files": sorted(changed),
            "committed_change": committed_change,
            "committed_files_known": not committed_change,
            "committed_files": []}


def compare_with_repo(repo_dir, before, after):
    """Full comparison: pure delta plus committed file enumeration."""
    cmp_ = compare_pure(before, after)
    if cmp_["committed_change"]:
        names = _git_bytes(repo_dir, "diff", "--name-only", "-z",
                           before["head_commit"], after["head_commit"])
        files = sorted(p.decode("utf-8", "replace")
                       for p in names.split(b"\0") if p)
        cmp_["committed_files"] = files
        cmp_["committed_files_known"] = True
        cmp_["changed_files"] = sorted(set(cmp_["changed_files"]) | set(files))
    return cmp_


def unauthorized_paths(changed_files, allowed_globs):
    """Scorer-side authorization decision from a computed change set."""
    import fnmatch
    allowed = _norm_globs(allowed_globs)
    out = []
    for p in changed_files:
        norm = p.replace("\\", "/")
        if not any(fnmatch.fnmatch(norm, g) for g in allowed):
            out.append(p)
    return sorted(out)
