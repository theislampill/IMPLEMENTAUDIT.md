#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'generate-readme-diagrams: %s\n' "$*" >&2
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

mode="${1:-}"
if [ -n "$mode" ] && [ "$mode" != "--check" ]; then
  fail "unknown argument: $mode"
fi

"${py_cmd[@]}" - "$mode" <<'PY'
import re
import sys
from pathlib import Path

mode = sys.argv[1]
readme = Path("README.md")
diagrams = {
    "tooling-architecture": Path("docs/diagrams/tooling-architecture.mmd"),
    "invocation-modes": Path("docs/diagrams/invocation-modes.mmd"),
    "execution-spine": Path("docs/diagrams/execution-spine.mmd"),
}

text = readme.read_text()

for key, source in diagrams.items():
    if not source.is_file():
        raise SystemExit(f"missing diagram source: {source}")

    begin = f"<!-- BEGIN: implementaudit-diagram:{key} -->"
    end = f"<!-- END: implementaudit-diagram:{key} -->"
    body = source.read_text().strip()
    for banned in ("%%{init", "themeCSS", "htmlLabels"):
        if banned in body:
            raise SystemExit(
                f"{source} uses Mermaid init/theme syntax that failed GitHub README rendering: {banned}"
            )
    replacement = f"{begin}\n\n```mermaid\n{body}\n```\n\n{end}"
    pattern = re.compile(
        re.escape(begin) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    text, count = pattern.subn(replacement, text)
    if count != 1:
        raise SystemExit(f"expected exactly one README diagram block for {key}, found {count}")

if mode == "--check":
    if text != readme.read_text():
        raise SystemExit("README.md diagrams are stale; run bash scripts/generate-readme-diagrams.sh")
    print("generate-readme-diagrams: check ok")
else:
    readme.write_text(text)
    print("generate-readme-diagrams: updated README.md")
PY
