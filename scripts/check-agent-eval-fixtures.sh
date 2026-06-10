#!/usr/bin/env bash
set -euo pipefail

# Structural gate for the adversarial agent-eval fixture pack. Each fixture
# defines an eval input and expected transcript properties for one identity
# misread of IMPLEMENTAUDIT. Passing this gate proves the eval surfaces exist
# with the required structure; it is not proof of live model behavior.
#
# Usage: check-agent-eval-fixtures.sh [<fixture-dir>]   (default fixtures/agent-eval)

fail() {
  printf 'check-agent-eval-fixtures: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fixture_dir="${1:-fixtures/agent-eval}"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$fixture_dir" <<'PY'
import sys
from pathlib import Path

base = Path(sys.argv[1])

REQUIRED_FIXTURES = [
    "terminal-cap-request.md",
    "autonomous-build-runner.md",
    "audit-only-reviewer.md",
    "release-bot-overreach.md",
    "lean-glossary-theater.md",
]

REQUIRED_SECTIONS = [
    "## Input",
    "## Expected behavior",
    "## Forbidden behavior",
    "## Owner/source",
    "## Evidence boundary",
    "## Minimal passing transcript properties",
    "## Graded properties",
]

failures = []
for name in REQUIRED_FIXTURES:
    path = base / name
    if not path.is_file():
        failures.append(f"missing fixture: {path.as_posix()}")
        continue
    text = path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"{path.as_posix()}: missing section: {section}")
            continue
        body = text.split(section, 1)[1].split("\n##", 1)[0].strip()
        if not body:
            failures.append(f"{path.as_posix()}: empty section: {section}")
    # Whitespace-normalized match: the disclaimer may wrap across lines.
    if "not proof of live model behavior" not in " ".join(text.split()):
        failures.append(f"{path.as_posix()}: missing evidence-boundary disclaimer")

if failures:
    sys.stderr.write("\n".join(failures) + "\n")
    raise SystemExit(1)

sys.stdout.write("check-agent-eval-fixtures: ok\n")
PY
