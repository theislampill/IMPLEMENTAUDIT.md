#!/usr/bin/env bash
set -euo pipefail

target="${1:-}"
shift 2>/dev/null || true
expect=""
if [ "${1:-}" = "--expect-hops" ]; then
  expect="${2:-}"
  shift 2
fi
[ -n "$target" ] && [ "$#" -eq 0 ] || {
  printf 'map-pin-chain: usage: <relative-path> [--expect-hops N]\n' >&2
  exit 2
}

if command -v python >/dev/null 2>&1; then py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then py_cmd=(py -3)
else printf 'map-pin-chain: python is required\n' >&2; exit 2
fi

"${py_cmd[@]}" - "$target" "$expect" <<'PY'
import os
import pathlib
import re
import sys

root = pathlib.Path.cwd().resolve()
target = sys.argv[1].replace("\\", "/")
expected = sys.argv[2]
if target.startswith("/") or any(part in ("", ".", "..") for part in target.split("/")):
    raise SystemExit("map-pin-chain: target must be a safe relative path")
if not (root / target).is_file():
    raise SystemExit(f"map-pin-chain: target not found: {target}")
if expected and not re.fullmatch(r"[0-9]+", expected):
    raise SystemExit("map-pin-chain: --expect-hops requires a nonnegative integer")

signals = ("sha256", "--check", "manifest", "byte-identical", "regenerat")
files = []
for base, dirs, names in os.walk(root):
    dirs[:] = sorted(d for d in dirs if d not in {".git", ".IMPLEMENTAUDIT", "graphify-out", ".activegraph"})
    for name in sorted(names):
        path = pathlib.Path(base, name)
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        files.append((rel, text))

queue = [target]
seen_nodes = {target}
hops = []
while queue:
    current = queue.pop(0)
    for rel, text in files:
        if rel in seen_nodes:
            continue
        matching_lines = [line for line in text.splitlines() if current in line]
        signal = next((item for line in matching_lines for item in signals
                       if item in line.casefold()), None)
        if signal is None:
            continue
        hops.append((len(hops) + 1, current, rel, signal))
        seen_nodes.add(rel)
        queue.append(rel)

for number, source, consumer, signal in hops:
    print(f"hop: {number} | source: {source} | consumer: {consumer} | signal: {signal}")
if expected and len(hops) != int(expected):
    print(f"map-pin-chain: observed {len(hops)} hops, expected {expected}", file=sys.stderr)
    raise SystemExit(1)
print(f"map-pin-chain: advisory-only; hops={len(hops)}")
PY
