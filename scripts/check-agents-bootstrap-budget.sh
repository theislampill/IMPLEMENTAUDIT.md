#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-agents-bootstrap-budget: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
agents_file="AGENTS.md"
max_lines=450
max_bytes=25000

while [ "$#" -gt 0 ]; do
  case "$1" in
    --agents-file)
      [ "$#" -ge 2 ] || fail "--agents-file requires a path"
      agents_file="$2"
      shift 2
      ;;
    --max-lines)
      [ "$#" -ge 2 ] || fail "--max-lines requires a value"
      max_lines="$2"
      shift 2
      ;;
    --max-bytes)
      [ "$#" -ge 2 ] || fail "--max-bytes requires a value"
      max_bytes="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

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

"${py_cmd[@]}" - "$agents_file" "$max_lines" "$max_bytes" <<'PY'
import sys
from pathlib import Path

agents_path = Path(sys.argv[1])
max_lines = int(sys.argv[2])
max_bytes = int(sys.argv[3])

if not agents_path.is_file():
    raise SystemExit(f"missing AGENTS file: {agents_path}")

data = agents_path.read_bytes()
text = data.decode("utf-8")
line_count = len(text.splitlines())
byte_count = len(data)

if line_count > max_lines:
    raise SystemExit(
        f"{agents_path}: line budget exceeded: {line_count} > {max_lines}"
    )
if byte_count > max_bytes:
    raise SystemExit(
        f"{agents_path}: byte budget exceeded: {byte_count} > {max_bytes}"
    )

required_tokens = [
    "# AGENTS.md",
    "Concise maintainer bootloader",
    "## Project Identity",
    "## Canonical Paths",
    "## Authorization Gates",
    "## Source And Package Layout",
    "## Validation Map",
    "## Release And Dogfood Boundaries",
    "## Active Anti-Repeat Rules",
    "## History And Retention",
    "skills/implementaudit/SKILL.md",
    "docs/maintenance/AGENTS-HISTORY.md",
    "docs/audits/RETENTION.md",
    "No commit. No push. No tag. No release. No publication. No provenance.",
    "temporary `CODEX_HOME`",
    "installed skill path under that temp home",
    "installed `SKILL.md` line/byte count",
    "exact command proving Codex used that temp home",
    "Real-home installed skill readback",
    "NON-EVIDENCE",
    "stale-installed-skill /",
    "real-home-contamination",
    "scripts/check-agents-bootstrap-budget.sh",
    "tests/agents-bootstrap-budget.test.sh",
    "scripts/check-dogfood-bootstrap-contract.sh",
    "scripts/check-validation-registry.sh",
    "scripts/verify-package.sh",
    "LIVE_V0_2_5_0_CLAUDE_INSTALL_BROKEN",
    "tests/release-asset-install-claude.test.sh",
    "Graphify output is orientation evidence, not proof",
    "ActiveGraph custody is not",
]
for token in required_tokens:
    if token not in text:
        raise SystemExit(f"{agents_path}: missing required bootloader token: {token}")

for required_file in [
    Path("docs/audits/RETENTION.md"),
    Path("scripts/check-agents-bootstrap-budget.sh"),
    Path("tests/agents-bootstrap-budget.test.sh"),
]:
    if agents_path.name == "AGENTS.md" and not required_file.is_file():
        raise SystemExit(f"missing referenced file: {required_file.as_posix()}")

history_like = [
    "## Release asset gate",
    "## Identity hygiene release-gate",
    "### Other v0.x state",
    "**Using check-public-claim-boundaries.sh:**",
]
for token in history_like:
    if token in text:
        raise SystemExit(
            f"{agents_path}: historical section belongs in docs/maintenance/AGENTS-HISTORY.md: {token}"
        )

if text.count("**Anti-repeat rule (") > 8:
    raise SystemExit(
        f"{agents_path}: embeds too many historical anti-repeat entries; move detail to history"
    )
if text.count("Rationale:") > 3:
    raise SystemExit(
        f"{agents_path}: embeds too much historical rationale; move detail to history"
    )

sys.stdout.write(
    f"check-agents-bootstrap-budget: ok ({line_count} lines, {byte_count} bytes)\n"
)
PY
