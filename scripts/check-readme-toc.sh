#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-readme-toc: %s\n' "$*" >&2
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

"${py_cmd[@]}" <<'PY'
import re
import sys
from pathlib import Path

readme = Path("README.md")
text = readme.read_text()

match = re.search(r"^## Contents\n(?P<body>.*?)(?=^## )", text, re.M | re.S)
if not match:
    raise SystemExit("missing compact ## Contents section")

toc_body = match.group("body")
links = re.findall(r"^\s*-\s+\[[^\]]+\]\(#([^)]+)\)\s*$", toc_body, re.M)
if len(links) < 8:
    raise SystemExit("README ToC is too sparse for newcomer navigation")

def slugify(heading: str) -> str:
    slug = heading.strip().lower()
    slug = re.sub(r"`([^`]*)`", r"\1", slug)
    slug = re.sub(r"<[^>]+>", "", slug)
    slug = re.sub(r"[^a-z0-9 _-]", "", slug)
    slug = re.sub(r"\s", "-", slug)
    slug = slug.strip("-")
    return slug

anchors = set()
for heading in re.findall(r"^##+ (.+)$", text, re.M):
    base = slugify(heading)
    candidate = base
    n = 1
    while candidate in anchors:
        n += 1
        candidate = f"{base}-{n}"
    anchors.add(candidate)

missing = [anchor for anchor in links if anchor not in anchors]
if missing:
    raise SystemExit("README ToC has unresolved anchors: " + ", ".join(missing))

required = {
    "what-it-is",
    "terminology",
    "how-an-audit-input-drives-a-run",
    "greenfield--brownfield-routing",
    "execution-gates",
    "loopability-andon-and-handoff-states",
    "install-notes",
    "upgrade--reinstall",
    "artifacts-and-outputs",
    "skill-internals--repository-layout",
    "validation-and-release-evidence",
    "version-and-release-notes",
}
missing_required = sorted(required.difference(links))
if missing_required:
    raise SystemExit("README ToC missing required anchors: " + ", ".join(missing_required))

sys.stdout.write("check-readme-toc: ok\n")
PY
