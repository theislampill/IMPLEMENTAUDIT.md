#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'verify-readme-diagrams-rendered: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

force=false
if [ "${1:-}" = "--force" ]; then
  force=true
  shift
fi
[ "$#" -eq 0 ] || fail "usage: verify-readme-diagrams-rendered.sh [--force]"

diagram_paths=(
  docs/diagrams/tooling-architecture.mmd
  docs/diagrams/invocation-modes.mmd
  docs/diagrams/execution-spine.mmd
  scripts/generate-readme-diagrams.sh
  scripts/verify-readme-diagrams-rendered.sh
)

# Generated parity is cheap and catches a hand-edited README block. The
# renderer remains progressive and activates only when its canonical inputs or
# its own acceptance instrument changed.
bash scripts/generate-readme-diagrams.sh --check

comparison=""
if ! git diff --quiet -- "${diagram_paths[@]}"; then
  comparison="HEAD"
elif [ -n "${GITHUB_BASE_REF:-}" ] &&
     git rev-parse --verify "origin/${GITHUB_BASE_REF}" >/dev/null 2>&1; then
  comparison="$(git merge-base HEAD "origin/${GITHUB_BASE_REF}")"
elif git rev-parse --verify origin/main >/dev/null 2>&1; then
  comparison="$(git merge-base HEAD origin/main)"
elif git rev-parse --verify HEAD^ >/dev/null 2>&1; then
  comparison="HEAD^"
fi

triggered=$force
if [ "$triggered" = false ] && ! git diff --quiet -- "${diagram_paths[@]}"; then
  triggered=true
fi

if [ "$triggered" = false ]; then
  if [ -n "$comparison" ] &&
     ! git diff --quiet "$comparison" HEAD -- "${diagram_paths[@]}"; then
    triggered=true
  fi
fi

if [ "$triggered" = false ]; then
  printf 'verify-readme-diagrams-rendered: NOT_APPLICABLE (no diagram projection change)\n'
  exit 0
fi

command -v npx >/dev/null 2>&1 || fail "npx is required for a rendered diagram check"
if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
[ -n "$comparison" ] || fail "a baseline commit is required for semantic preservation"
for name in tooling-architecture invocation-modes execution-spine; do
  git show "$comparison:docs/diagrams/$name.mmd" >"$tmp/$name.before.mmd" ||
    fail "could not read pre-change diagram from $comparison: $name"
done

"${py_cmd[@]}" - "$tmp" <<'PY'
import re
import sys
from pathlib import Path


def normalise_label(value):
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = value.strip().strip("`")
    return re.sub(r"\s+", " ", value).strip()


def inventory(text):
    lines = text.splitlines()
    nodes = {}
    groups = {}
    edges = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        group = re.match(r'^subgraph\s+(\w+)\["(.*)"\]$', stripped)
        if group:
            groups[group.group(1)] = normalise_label(group.group(2))
            index += 1
            continue
        node = re.match(r'^(\w+)\s*(?:\(\[|\[|\{)"', stripped)
        if node:
            block = stripped
            while block.count('"') < 2 and index + 1 < len(lines):
                index += 1
                block += "\n" + lines[index].strip()
            first = block.find('"')
            last = block.rfind('"')
            if first < 0 or last <= first:
                raise SystemExit(f"could not parse Mermaid node: {block!r}")
            nodes[node.group(1)] = normalise_label(block[first + 1:last])
            index += 1
            continue
        if any(token in stripped for token in ("-->", "-.->", "-. ")):
            edges.append(re.sub(r"\s+", " ", stripped))
        index += 1
    return nodes, groups, sorted(edges)


root = Path(sys.argv[1])
expected_populations = {
    "tooling-architecture": (7, 0, 6, 6),
    "invocation-modes": (21, 4, 8, 20),
    "execution-spine": (28, 1, 23, 33),
}
for name in ("tooling-architecture", "invocation-modes", "execution-spine"):
    before = inventory((root / f"{name}.before.mmd").read_text(encoding="utf-8"))
    current = inventory(Path(f"docs/diagrams/{name}.mmd").read_text(encoding="utf-8"))
    labels = ("node population/labels", "subgraph population/labels", "edge topology/labels")
    for label, old, new in zip(labels, before, current):
        if old != new:
            raise SystemExit(f"{name}: {label} changed without an authoritative correction")
    nodes, groups, edge_statements = current
    graph_edges = sum(
        len(re.findall(r"-->|-\.->|-\..*?\.->", statement))
        for statement in edge_statements)
    population = (len(nodes), len(groups), len(edge_statements), graph_edges)
    if population != expected_populations[name]:
        raise SystemExit(
            f"{name}: semantic population changed: expected "
            f"{expected_populations[name]}, got {population}")

print("verify-readme-diagrams-rendered: SEMANTIC_DETAIL_PRESERVATION=PASS")
PY

renderer='@mermaid-js/mermaid-cli@11.16.0'
for name in tooling-architecture invocation-modes execution-spine; do
  npx --yes "$renderer" \
    -i "docs/diagrams/$name.mmd" \
    -o "$tmp/$name.svg" \
    -b transparent >/dev/null
done

"${py_cmd[@]}" - "$tmp" <<'PY'
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

root = Path(sys.argv[1])
anchors = {
    "tooling-architecture": (
        "Graphify", "IMPLEMENTAUDIT", "Live repository files",
        "Run root and evidence", "Markdown evidence", "ActiveGraph",
        "Capability Ledger"),
    "invocation-modes": (
        "Direct governance", "Embedded governance",
        "Goal synthesis / phased handoff", "Governed casual-build intake",
        "tdqyq-audit-object", "ydqyq-audit-action", "Artifacts",
        "One /goal handoff", "Terminal audit-object closure"),
    "execution-spine": (
        "Route before mutation", "Smoke A", "Smoke B", "AUDIT_COMPLETE",
        "IMPLEMENTAUDIT_RUN_COMPLETE", "Separate release/provenance gate"),
}

for name, required in anchors.items():
    path = root / f"{name}.svg"
    if not path.is_file():
        raise SystemExit(f"missing rendered SVG: {path}")
    tree = ElementTree.parse(path)
    svg = tree.getroot()
    view_box = svg.attrib.get("viewBox", "").split()
    if len(view_box) != 4:
        raise SystemExit(f"{name}: rendered SVG has no four-value viewBox")
    width, height = map(float, view_box[2:])
    if width <= 0 or height <= 0:
        raise SystemExit(f"{name}: rendered SVG has a non-positive extent")
    ratio = width / height
    if ratio > 2.5:
        raise SystemExit(
            f"{name}: rendered aspect ratio {ratio:.2f}:1 is too wide for the GitHub README")
    text = re.sub(r"\s+", " ", " ".join(svg.itertext())).strip()
    for anchor in required:
        if anchor not in text:
            raise SystemExit(f"{name}: rendered SVG lost public label {anchor!r}")

print("verify-readme-diagrams-rendered: RENDERED_CONSUMER_READABILITY=PASS "
      "(3/3 labels preserved, aspect ratios <= 2.5:1)")
PY
