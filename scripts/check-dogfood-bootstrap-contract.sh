#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-dogfood-bootstrap-contract: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skill_file="skills/implementaudit/SKILL.md"
audit_file=""
transcript_file="fixtures/dogfood-bootstrap/positive/baseline-first-transcript.jsonl"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skill-file)
      [ "$#" -ge 2 ] || fail "--skill-file requires a path"
      skill_file="$2"
      shift 2
      ;;
    --audit-file)
      [ "$#" -ge 2 ] || fail "--audit-file requires a path"
      audit_file="$2"
      shift 2
      ;;
    --transcript-file)
      [ "$#" -ge 2 ] || fail "--transcript-file requires a path"
      transcript_file="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

"${py_cmd[@]}" - "$skill_file" "$audit_file" "$transcript_file" <<'PY'
import sys
from pathlib import Path

skill_path = Path(sys.argv[1])
audit_path = Path(sys.argv[2])
transcript_path = Path(sys.argv[3])

if not skill_path.is_file():
    raise SystemExit(f"missing skill file: {skill_path}")
if str(audit_path) != "." and not audit_path.is_file():
    raise SystemExit(f"missing audit file: {audit_path}")
if not transcript_path.is_file():
    raise SystemExit(f"missing transcript fixture: {transcript_path}")

skill = skill_path.read_text(encoding="utf-8")
audit = audit_path.read_text(encoding="utf-8") if str(audit_path) != "." else ""
transcript = transcript_path.read_text(encoding="utf-8")

heading = "## Dogfood Bootstrap / Read Map"
if heading not in skill:
    raise SystemExit(f"{skill_path}: missing {heading}")

line_no = skill[: skill.index(heading)].count("\n") + 1
if line_no > 40:
    raise SystemExit(f"{skill_path}: dogfood bootstrap must appear before line 40")

required_skill_tokens = [
    "First executable dogfood rule: Do not read this entire skill or installed",
    "Do not read this entire installed `SKILL.md` before acting",
    "do not chunk",
    "Baseline the target repo first",
    "progressive disclosure",
    "owner/source sections",
    "targeted `rg`/grep",
    "Package proof uses deterministic checks",
    "not model-visible full-file",
    "Full installed-payload readback is non-evidence",
    "### Dogfood Runner Contract",
    "Baseline/read-only checks first",
    "Repo-local validation after the read map is satisfied",
    "`--ask-for-approval never` is valid only when every required command is already",
    "`--ask-for-approval on-request` with `--sandbox workspace-write`",
    "Do not use `--dangerously-bypass-approvals-and-sandbox`",
    "Real-home installed skill readback is non-evidence",
    "temp `CODEX_HOME`",
    "installed skill path under that temp home",
    "installed `SKILL.md` line/byte count",
    "exact command proving Codex used that temp home",
    "stale-installed-skill /",
    "real-home-contamination",
]
for token in required_skill_tokens:
    if token not in skill:
        raise SystemExit(f"{skill_path}: missing dogfood bootstrap token: {token}")

if audit:
    for token in [
        "temp",
        "Dogfood",
        "baseline",
    ]:
        if token not in audit:
            raise SystemExit(f"{audit_path}: missing optional dogfood token: {token}")

builder = Path("scripts/build-release-asset.sh").read_text(encoding="utf-8")
for token in ['"skills/implementaudit/SKILL.md"', '"SKILL.md"']:
    if token not in builder:
        raise SystemExit(f"scripts/build-release-asset.sh: missing archive token: {token}")

baseline_tokens = [
    "git status --short --branch --untracked-files=all",
    "git rev-parse HEAD",
]
readback_tokens = [
    "skills\\\\implementaudit\\\\SKILL.md",
    "skills/implementaudit/SKILL.md",
    "installed skill is long, chunking remaining readback before baseline",
    "The installed skill file is long and the first read was truncated by the tool display",
]
real_home_tokens = [
    r"C:\\Users\\theis\\.codex\\skills\\implementaudit",
    r"C:\Users\theis\.codex\skills\implementaudit",
    "/c/Users/theis/.codex/skills/implementaudit",
]
temp_home_tokens = [
    "CODEX_HOME",
    "codex-home",
    "install-codex-from-release.sh",
    "installed skill path",
    "installed `SKILL.md` line/byte count",
]

baseline_positions = [transcript.find(token) for token in baseline_tokens if token in transcript]
if not baseline_positions:
    raise SystemExit(f"{transcript_path}: missing baseline command token")
first_baseline = min(pos for pos in baseline_positions if pos >= 0)

readback_positions = [
    transcript.find(token)
    for token in readback_tokens
    if token in transcript
]
if readback_positions:
    first_readback = min(pos for pos in readback_positions if pos >= 0)
    if first_readback < first_baseline:
        raise SystemExit(
            f"{transcript_path}: installed skill readback occurred before baseline"
        )

real_home_positions = [
    transcript.find(token)
    for token in real_home_tokens
    if token in transcript
]
if real_home_positions:
    first_real_home = min(pos for pos in real_home_positions if pos >= 0)
    temp_positions = [
        transcript.find(token)
        for token in temp_home_tokens
        if token in transcript
    ]
    if not temp_positions or min(pos for pos in temp_positions if pos >= 0) > first_real_home:
        raise SystemExit(
            f"{transcript_path}: real-home skill readback occurred before temp CODEX_HOME install path"
        )

sys.stdout.write("check-dogfood-bootstrap-contract: ok\n")
PY
