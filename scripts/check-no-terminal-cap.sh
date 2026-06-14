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

# Runtime-shaping surfaces may deny a cap, but they must not teach a terminal
# retry/revision/round/strike limit as behavior. Historical mentions stay valid
# only in exempt surfaces (CHANGELOG.md and docs/audits/ are never scanned).
FORBIDDEN = [
    "strike",
    "strikes",
    "three-strike",
    "recovery ladder",
    "failure ladder",
    "up to 3 rounds",
    "maximum 3 rounds",
    "max 2",
    "max-2",
    "two revisions",
    "max 3",
    "max-3",
    "max retry",
    "max retries",
    "retry cap",
    "retry limit",
    "revision limit",
    "round limit",
    "capped round",
    "capped rounds",
    "try cap",
    "attempt cap",
    "failure_probe",
    "failure_escalate",
    "failure_handoff",
]

ALWAYS_FORBIDDEN = [
    "no subsequent phases execute",
]

NEGATED_CONTEXT = [
    "no ",
    "not ",
    "never ",
    "without ",
    "do not ",
    "must not ",
    "forbid",
    "forbidden",
    "reject",
    "rejected",
    "anti-repeat",
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
        for term in ALWAYS_FORBIDDEN:
            if term in lowered:
                violations.append(f"{path.as_posix()}:{lineno}: disallowed public-claim terminal-cap wording: {term!r}")
        for term in FORBIDDEN:
            if term in lowered and not any(context in lowered for context in NEGATED_CONTEXT):
                violations.append(f"{path.as_posix()}:{lineno}: disallowed public-claim terminal-cap wording: {term!r}")
        if (
            "first" in lowered
            and "second" in lowered
            and "third" in lowered
            and "failure" in lowered
            and "ladder" in lowered
            and not any(context in lowered for context in NEGATED_CONTEXT)
        ):
            violations.append(
                f"{path.as_posix()}:{lineno}: disallowed public-claim terminal-cap wording: first/second/third failure ladder"
            )

if violations:
    sys.stderr.write("\n".join(violations) + "\n")
    raise SystemExit(1)

sys.stdout.write("check-no-terminal-cap: ok\n")
PY
