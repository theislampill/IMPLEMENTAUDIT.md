#!/usr/bin/env bash
set -euo pipefail

# Poka-yoke gate: shipped runtime docs must not reintroduce terminal-cap
# failure semantics (strike counters, capped audit rounds, run-stopping
# wording) or the legacy FAILURE-prefixed marker spellings. Jidoka escalation
# is driven by repeated same-class failure and blocked closure, not a try
# counter. Legacy history (CHANGELOG.md, docs/audits/) is exempt and is not
# scanned.
#
# Usage: check-no-terminal-cap.sh [--scan-root <dir>]

fail() {
  printf 'check-no-terminal-cap: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scan_root="$repo_root"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --scan-root)
      [ "$#" -ge 2 ] || fail "--scan-root requires a directory argument"
      scan_root="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

cd "$scan_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - <<'PY'
import sys
from pathlib import Path

# Runtime-shaping surfaces: the shipped package payload plus the repo docs,
# fixtures, and generated-diagram sources that model expected runtime behavior.
SCAN_DIRS = ["skills", "docs/diagrams", "docs/portal", "fixtures"]
SCAN_FILES = ["README.md", "AGENTS.md"]

# Bare "strike" is forbidden: any strike-counter teaching in a runtime
# surface is cap semantics, regardless of the number attached. Historical
# mentions stay valid only in the exempt surfaces (CHANGELOG.md and
# docs/audits/ are never scanned).
FORBIDDEN = [
    "strike",
    "recovery ladder",
    "failure ladder",
    "up to 3 rounds",
    "maximum 3 rounds",
    "no subsequent phases execute",
    "failure_probe",
    "failure_escalate",
    "failure_handoff",
]

paths = []
for d in SCAN_DIRS:
    base = Path(d)
    if base.is_dir():
        paths.extend(p for p in sorted(base.rglob("*")) if p.is_file())
for f in SCAN_FILES:
    p = Path(f)
    if p.is_file():
        paths.append(p)

violations = []
for path in paths:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for lineno, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        for term in FORBIDDEN:
            if term in lowered:
                violations.append(f"{path.as_posix()}:{lineno}: forbidden terminal-cap wording: {term!r}")

if violations:
    sys.stderr.write("\n".join(violations) + "\n")
    raise SystemExit(1)

sys.stdout.write("check-no-terminal-cap: ok\n")
PY
