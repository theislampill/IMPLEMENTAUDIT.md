"""Output custody guards (#9 harness).

Raw transcripts and results default OUTSIDE the repository. An in-repo result
root is allowed only under an ignored directory with explicit opt-in. Output
path resolution is fail-closed: absolute paths outside the approved root,
`..` traversal, symlink/junction/reparse escape, and pre-existing destination
collisions are rejected. Never commit private prompts, transcripts,
credentials, or provider receipts.
"""
from __future__ import annotations

import os


class CustodyError(Exception):
    """Requested output location violates the custody policy."""


def resolve_output_dir(approved_root, requested):
    """Resolve `requested` strictly inside `approved_root` or raise.

    - `..` segments are rejected before resolution (no normalization tricks).
    - The final real path (symlinks/junctions resolved) must remain inside
      the approved root's real path.
    - A pre-existing destination is a collision and is rejected.
    """
    if requested is None or requested == "":
        raise CustodyError("empty output path")
    parts = requested.replace("\\", "/").split("/")
    if any(p == ".." for p in parts):
        raise CustodyError(f"path traversal rejected: {requested!r}")
    approved_real = os.path.realpath(approved_root)
    candidate = requested if os.path.isabs(requested) \
        else os.path.join(approved_root, requested)
    real = os.path.realpath(candidate)
    if real != approved_real and \
            not real.startswith(approved_real + os.sep):
        raise CustodyError(
            f"output escapes approved root: {requested!r} -> {real!r}")
    if os.path.exists(real):
        raise CustodyError(f"destination already exists: {real!r}")
    return real
