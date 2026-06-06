#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-forbidden-terms: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

root="."
label="externally supplied forbidden term"
allow_empty=0
terms=()
terms_files=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --root)
      [ "$#" -ge 2 ] || fail "--root requires a path"
      root="$2"
      shift 2
      ;;
    --term)
      [ "$#" -ge 2 ] || fail "--term requires a value"
      terms+=("$2")
      shift 2
      ;;
    --terms-file)
      [ "$#" -ge 2 ] || fail "--terms-file requires a path"
      terms_files+=("$2")
      shift 2
      ;;
    --label)
      [ "$#" -ge 2 ] || fail "--label requires a value"
      label="$2"
      shift 2
      ;;
    --allow-empty)
      allow_empty=1
      shift
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

if [ -n "${IMPLEMENTAUDIT_FORBIDDEN_TERMS_FILE:-}" ]; then
  terms_files+=("$IMPLEMENTAUDIT_FORBIDDEN_TERMS_FILE")
fi

"${py_cmd[@]}" - "$root" "$label" "$allow_empty" "${terms[@]}" -- "${terms_files[@]}" <<'PY'
import base64
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

args = sys.argv[1:]
root = Path(args[0])
label = args[1]
allow_empty = args[2] == "1"
separator = args.index("--")
terms = args[3:separator]
term_files = args[separator + 1 :]

env_terms = os.environ.get("IMPLEMENTAUDIT_FORBIDDEN_TERMS", "")
if env_terms:
    terms.extend(env_terms.splitlines())

for term_file in term_files:
    path = Path(term_file).expanduser()
    if not path.is_file():
        raise SystemExit(f"terms file does not exist: {path}")
    terms.extend(path.read_text(encoding="utf-8").splitlines())

terms = [term.strip() for term in terms if term.strip()]
if not terms:
    if allow_empty:
        sys.stdout.write("check-forbidden-terms: ok (no terms supplied)\n")
        raise SystemExit(0)
    raise SystemExit("no forbidden terms supplied")

blocked_dirs = {
    ".git",
    ".IMPLEMENTAUDIT",
    "dist",
    "graphify-out",
    ".graphify",
    ".activegraph",
    "tmp",
    "temp",
}
binary_suffixes = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".zip",
    ".skill",
    ".ico",
    ".pdf",
    ".db",
}


def term_variants(term: str) -> set[str]:
    values = {term, term.lower(), term.upper()}
    if term:
        values.add("." + term.lower())
    encoded_inputs = {term, term.lower(), term.upper()}
    for value in encoded_inputs:
        raw = value.encode("utf-8")
        values.add(base64.b64encode(raw).decode("ascii"))
        values.add(raw.hex())
        values.add(quote(value))
    return {value for value in values if value}


def compact(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "", value)


def iter_files(path: Path):
    if path.is_file():
        yield path
        return
    for child in sorted(path.rglob("*")):
        if child.is_file():
            yield child


hits: list[str] = []
for path in iter_files(root):
    try:
        rel_path = path.relative_to(root) if root.is_dir() else Path(path.name)
    except ValueError:
        rel_path = path
    rel = path if not path.is_absolute() else path
    parts = set(rel_path.parts)
    if root.is_dir() and parts & blocked_dirs:
        continue
    if path.suffix.lower() in binary_suffixes:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    lowered_lines = [line.lower() for line in text.splitlines()]
    compact_text = compact(text).lower()

    for term in terms:
        variants = term_variants(term)
        for line_no, line in enumerate(lowered_lines, start=1):
            if any(variant.lower() in line for variant in variants):
                hits.append(f"{rel}:{line_no}: {label}: direct or encoded match")
                break
        compact_variants = {compact(variant).lower() for variant in variants}
        if any(variant and variant in compact_text for variant in compact_variants):
            hits.append(f"{rel}: {label}: compact/assembled match")

if hits:
    raise SystemExit("\n".join(dict.fromkeys(hits)))

sys.stdout.write("check-forbidden-terms: ok\n")
PY
