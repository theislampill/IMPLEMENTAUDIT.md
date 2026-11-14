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
import re
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

# Reject counted/capped strike policies without banning a proper noun or an
# ordinary English use of "strike". The architecture forbids finite-count
# termination semantics, not the token itself.
COUNTED_STRIKE = (
    r"\b(?:single|double|triple|quad|quadruple|one|two|three|four|five|n|[1-9][0-9]*)[ -]strikes?\b"
    r"|\b(?:first|second|third|fourth|fifth)\s+strikes?\b"
    r"|\bstrikes?\s+(?:number\s*|#\s*)?(?:one|two|three|four|five|n|first|second|third|fourth|fifth|[1-9][0-9]*)\b"
)
STRIKE_POLICY_CONTEXT = (
    r"\b(?:policy|rule|sequence|ladder|counter|count|cap|limit|attack\s+count|termination)\b"
    r"|\b(?:stop|stops|block|blocks|terminate|terminates)\s+(?:the\s+)?(?:run|work|loop|audit|closure|progress)\b"
    r"|\b(?:handoff|hands\s+off)\b"
)
DIRECT_STRIKE_CAP_PATTERNS = [
    r"\bstrikes?\s+(?:counter|count|cap|limit)\b",
    r"\bafter\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|n|[1-9][0-9]*)\s+strikes?\b.*\b(?:stop|stops|block|blocks|handoff|hands\s+off|terminate|terminates|fail|fails|close|closes)\b",
]
DIRECT_RETRY_CAP_PATTERNS = [
    r"\bafter\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|n|[1-9][0-9]*)\s+(?:retry|retries)\b.*\b(?:stop|stops|block|blocks|handoff|hand\s+off|hands\s+off|terminate|terminates|fail|fails|close|closes)\b",
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
        counted_strike_policy = re.search(COUNTED_STRIKE, lowered) and re.search(
            STRIKE_POLICY_CONTEXT, lowered
        )
        direct_strike_cap = any(re.search(pattern, lowered) for pattern in DIRECT_STRIKE_CAP_PATTERNS)
        direct_retry_cap = any(re.search(pattern, lowered) for pattern in DIRECT_RETRY_CAP_PATTERNS)
        if (counted_strike_policy or direct_strike_cap or direct_retry_cap) and not any(
            context in lowered for context in NEGATED_CONTEXT
        ):
            violations.append(
                f"{path.as_posix()}:{lineno}: disallowed public-claim terminal-cap wording: counted/capped retry or strike policy"
            )
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
