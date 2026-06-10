#!/usr/bin/env bash
set -euo pipefail

# Grade a run transcript against an agent-eval fixture's "## Graded
# properties" block. Deterministic, lightweight: phrase/marker assertions
# plus delegation to the existing marker-order and no-terminal-cap gates.
# A PASS means the transcript satisfies the fixture's machine-checkable
# properties; it is not a holistic judgment of run quality.
#
# Usage: grade-agent-eval-transcript.sh <fixture.md> <transcript-file>
#
# Directives (inside the fixture's ```text fence under ## Graded properties):
#   require-marker: X        exact string must appear in the transcript
#   require-phrase: x        case-insensitive phrase must appear
#   require-any: a | b | c   at least one alternative (case-insensitive)
#   forbid-phrase: x         case-insensitive phrase must NOT appear
#   marker-order: true       transcript must pass check-marker-order.sh
#   no-terminal-cap: true    transcript must pass check-no-terminal-cap.sh

fail() {
  printf 'grade-agent-eval-transcript: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

[ "$#" -eq 2 ] || fail "usage: grade-agent-eval-transcript.sh <fixture.md> <transcript-file>"
fixture="$1"
transcript="$2"
[ -f "$fixture" ] || fail "fixture not found: $fixture"
[ -f "$transcript" ] || fail "transcript not found: $transcript"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

needs="$("${py_cmd[@]}" - "$fixture" "$transcript" <<'PY'
import re
import sys
from pathlib import Path

fixture = Path(sys.argv[1])
transcript = Path(sys.argv[2])

ftext = fixture.read_text(encoding="utf-8")
if "## Graded properties" not in ftext:
    sys.stderr.write(f"{fixture.as_posix()}: missing '## Graded properties' section\n")
    raise SystemExit(1)
section = ftext.split("## Graded properties", 1)[1]
fence = re.search(r"```text\n(.*?)```", section, re.S)
if not fence:
    sys.stderr.write(f"{fixture.as_posix()}: Graded properties has no ```text fence\n")
    raise SystemExit(1)

text = transcript.read_text(encoding="utf-8")
lowered = text.lower()

violations = []
needs = []
for raw in fence.group(1).splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    key, _, value = line.partition(":")
    key, value = key.strip(), value.strip()
    if key == "require-marker":
        if value not in text:
            violations.append(f"missing required marker: {value}")
    elif key == "require-phrase":
        if value.lower() not in lowered:
            violations.append(f"missing required phrase: {value}")
    elif key == "require-any":
        alts = [a.strip() for a in value.split("|")]
        if not any(a.lower() in lowered for a in alts if a):
            violations.append(f"none of the alternatives present: {value}")
    elif key == "forbid-phrase":
        if value.lower() in lowered:
            violations.append(f"forbidden phrase present: {value}")
    elif key in ("marker-order", "no-terminal-cap") and value == "true":
        needs.append(key)
    else:
        violations.append(f"unknown directive: {line}")

if violations:
    sys.stderr.write("\n".join(violations) + "\n")
    raise SystemExit(1)
sys.stdout.write("\n".join(needs))
PY
)" || fail "transcript fails the fixture's graded properties (see above)"

while IFS= read -r need; do
  need="${need%$'\r'}"  # Windows python stdout may emit CRLF
  case "$need" in
    marker-order)
      bash scripts/check-marker-order.sh "$transcript" >/dev/null \
        || fail "transcript fails marker-order validation"
      ;;
    no-terminal-cap)
      scan_root="$(mktemp -d)"
      mkdir -p "$scan_root/skills"
      cp "$transcript" "$scan_root/skills/transcript.md"
      if ! bash scripts/check-no-terminal-cap.sh --scan-root "$scan_root" >/dev/null 2>&1; then
        rm -rf "$scan_root"
        fail "transcript contains terminal-cap wording"
      fi
      rm -rf "$scan_root"
      ;;
    "") ;;
    *) fail "internal error: unknown need '$need'" ;;
  esac
done <<EOF_NEEDS
$needs
EOF_NEEDS

printf 'grade-agent-eval-transcript: PASS (%s vs %s)\n' "$fixture" "$transcript"
