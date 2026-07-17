"""Output custody guards (#9 harness).

Raw transcripts and results default OUTSIDE the repository. An in-repo result
root is allowed only under an ignored directory with explicit opt-in.

Hardening (Phase C) — the check/use gap is closed as far as the platform
permits:
- every EXISTING parent component between the approved root and the target is
  lstat-verified and must not be a symlink/junction/reparse point;
- the final directory is created with EXCLUSIVE `os.mkdir` (collision ⇒
  error, never reuse);
- the path is re-resolved AFTER creation and must still be inside the
  approved root;
- restrictive permissions are applied where the platform supports them;
- `..` traversal and absolute paths outside the root are rejected before any
  filesystem access.
"""
from __future__ import annotations

import os
import stat as statmod


class CustodyError(Exception):
    """Requested output location violates the custody policy."""


def _reject_link(path):
    try:
        st = os.lstat(path)
    except OSError as exc:
        raise CustodyError(f"cannot inspect parent {path!r}: {exc}")
    reparse = getattr(st, "st_file_attributes", 0) & getattr(
        statmod, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if statmod.S_ISLNK(st.st_mode) or reparse:
        raise CustodyError(f"symlink/junction/reparse parent rejected: {path!r}")


def resolve_and_create_output_dir(approved_root, requested):
    """Validate `requested` strictly inside `approved_root`, then CREATE it
    exclusively and re-verify. Returns the real path. Raises CustodyError."""
    if not requested:
        raise CustodyError("empty output path")
    parts = requested.replace("\\", "/").split("/")
    if any(p == ".." for p in parts):
        raise CustodyError(f"path traversal rejected: {requested!r}")
    approved_real = os.path.realpath(approved_root)
    if not os.path.isdir(approved_real):
        raise CustodyError(f"approved root missing: {approved_root!r}")
    candidate = requested if os.path.isabs(requested) \
        else os.path.join(approved_root, requested)
    real = os.path.realpath(candidate)
    if real != approved_real and not real.startswith(approved_real + os.sep):
        raise CustodyError(
            f"output escapes approved root: {requested!r} -> {real!r}")
    # verify every EXISTING component between root and target
    walk = approved_real
    rel = os.path.relpath(real, approved_real)
    for component in rel.split(os.sep):
        if component in (".", ""):
            continue
        walk = os.path.join(walk, component)
        if os.path.lexists(walk) and walk != real:
            _reject_link(walk)
    if os.path.lexists(real):
        raise CustodyError(f"destination already exists: {real!r}")
    parent = os.path.dirname(real)
    os.makedirs(parent, exist_ok=True)
    try:
        os.mkdir(real)  # exclusive: fails if created concurrently
    except FileExistsError:
        raise CustodyError(f"destination collision on create: {real!r}")
    try:
        os.chmod(real, 0o700)
    except OSError:
        pass  # best-effort on platforms without POSIX modes
    # post-creation revalidation
    post = os.path.realpath(real)
    if post != approved_real and not post.startswith(approved_real + os.sep):
        raise CustodyError(f"post-creation escape detected: {post!r}")
    return real


# Backwards-compatible check-only variant (used by validation paths that must
# not create). Callers that will WRITE must use resolve_and_create_output_dir.
def resolve_output_dir(approved_root, requested):
    if not requested:
        raise CustodyError("empty output path")
    parts = requested.replace("\\", "/").split("/")
    if any(p == ".." for p in parts):
        raise CustodyError(f"path traversal rejected: {requested!r}")
    approved_real = os.path.realpath(approved_root)
    candidate = requested if os.path.isabs(requested) \
        else os.path.join(approved_root, requested)
    real = os.path.realpath(candidate)
    if real != approved_real and not real.startswith(approved_real + os.sep):
        raise CustodyError(
            f"output escapes approved root: {requested!r} -> {real!r}")
    if os.path.exists(real):
        raise CustodyError(f"destination already exists: {real!r}")
    return real
