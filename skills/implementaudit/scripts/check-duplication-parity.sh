#!/usr/bin/env bash
set -euo pipefail

manifest="${1:-}"
[ "$#" -eq 1 ] && [ -f "$manifest" ] && [ ! -L "$manifest" ] || {
  printf 'check-duplication-parity: usage: <manifest-file>\n' >&2
  exit 2
}

if command -v python >/dev/null 2>&1; then py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
else printf 'check-duplication-parity: python is required\n' >&2; exit 2
fi

"${py_cmd[@]}" - "$manifest" <<'PY'
import os
import pathlib
import re
import sys

manifest = pathlib.Path(sys.argv[1])
root = pathlib.Path.cwd().resolve(strict=True)

def fail(message):
    print(f"check-duplication-parity: {message}", file=sys.stderr)
    raise SystemExit(1)

seen = set()
rows = [line for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")]
if not rows:
    fail("manifest contains no duplication sets")
for row_no, row in enumerate(rows, 1):
    if ":" not in row:
        fail(f"row {row_no}: expected <name>: <path>::<anchor>, ...")
    name, encoded = row.split(":", 1)
    name = name.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or name in seen:
        fail(f"row {row_no}: invalid or duplicate set name")
    seen.add(name)
    members = [item.strip() for item in encoded.split(",") if item.strip()]
    if len(members) < 2:
        fail(f"{name}: requires at least two members")
    observations = []
    member_ids = set()
    member_files = set()
    physical_files = set()
    for member in members:
        if "::" not in member:
            fail(f"{name}: member requires <path>::<line-anchor>")
        raw_path, anchor = (part.strip() for part in member.split("::", 1))
        if not raw_path or not anchor:
            fail(f"{name}: invalid member")
        normalized_path = raw_path.replace("\\", "/")
        if (normalized_path.startswith("/") or
                re.match(r"^[A-Za-z]:", normalized_path) or
                any(part in ("", ".", "..") for part in normalized_path.split("/"))):
            fail(f"{name}: member path must be safe and repository-relative: {raw_path}")
        lexical = root.joinpath(*normalized_path.split("/"))
        cursor = root
        for part in normalized_path.split("/"):
            cursor = cursor / part
            if cursor.is_symlink():
                fail(f"{name}: member path contains a symlink: {raw_path}")
        try:
            path = lexical.resolve(strict=True)
            path.relative_to(root)
        except (OSError, ValueError):
            fail(f"{name}: member resolves outside the repository: {raw_path}")
        if path.is_symlink() or not path.is_file():
            fail(f"{name}: member is not a regular non-symlink file: {raw_path}")
        lexical_absolute = os.path.normcase(os.path.abspath(str(lexical)))
        real_path = os.path.normcase(os.path.realpath(str(lexical)))
        if lexical_absolute != real_path:
            fail(f"{name}: member path traverses a symlink or reparse point: {raw_path}")
        canonical_path = os.path.normcase(str(path))
        stat = path.stat()
        physical_identity = (stat.st_dev, stat.st_ino)
        canonical_member = (canonical_path, anchor)
        if canonical_member in member_ids:
            fail(f"{name}: duplicate canonical member: {raw_path}::{anchor}")
        member_ids.add(canonical_member)
        member_files.add(canonical_path)
        if physical_identity in physical_files:
            fail(f"{name}: one physical file is declared more than once: {raw_path}")
        physical_files.add(physical_identity)
        lines = path.read_text(encoding="utf-8").splitlines()
        hits = [index for index, line in enumerate(lines) if anchor in line]
        if len(hits) != 1:
            fail(f"{name}: anchor {anchor!r} in {raw_path} matched {len(hits)} lines")
        index = hits[0]
        line = lines[index]
        if "=" not in line:
            fail(f"{name}: anchored line in {raw_path} has no '=' value boundary")
        value = line.split("=", 1)[1].strip()
        comments = []
        cursor = index - 1
        while cursor >= 0:
            stripped = lines[cursor].strip()
            match = re.match(r"^(?:#|//|/\*+|\*|<!--)\s*(.*?)\s*(?:\*/|-->)?$", stripped)
            if not match:
                break
            comments.append(match.group(1).strip())
            cursor -= 1
        comments.reverse()
        if not comments:
            fail(f"{name}: {raw_path} has no immediately adjacent comment block")
        observations.append((value, "\n".join(comments), raw_path))
    if len(member_files) < 2:
        fail(f"{name}: requires at least two distinct canonical files")
    values = {item[0] for item in observations}
    comments = {item[1] for item in observations}
    if len(values) != 1:
        fail(f"{name}: value divergence: {[(p, v) for v, _, p in observations]!r}")
    if len(comments) != 1:
        fail(f"{name}: adjacent-comment divergence: {[(p, c) for _, c, p in observations]!r}")
    print(f"set: {name} | members: {len(observations)} | parity: value+comment")
print(f"check-duplication-parity: ok ({len(rows)} sets)")
PY
