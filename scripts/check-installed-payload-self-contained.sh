#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-installed-payload-self-contained: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scan_root="$repo_root"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --scan-root)
      [ "$#" -ge 2 ] || fail "--scan-root requires a directory"
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

root = Path.cwd()
skills = root / "skills"
if not skills.is_dir():
    raise SystemExit("skills/ directory is required")

repo_only_pattern = re.compile(
    r"(fixtures/[\w./-]+|tests/[\w./-]+|scripts/check-[\w./-]+|skills/implementaudit/scripts/[\w./-]+)"
)

violations: list[str] = []
for path in sorted(skills.rglob("*")):
    if not path.is_file():
        continue
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        continue
    for lineno, line in enumerate(lines, 1):
        if not repo_only_pattern.search(line):
            continue
        lower = line.lower()
        if "skills/implementaudit/scripts/" in line:
            if "source repo" not in lower:
                violations.append(
                    f"{path.as_posix()}:{lineno}: repo-only path reference "
                    f"without 'source repo' label: {line.strip()[:120]}"
                )
            if "installed payload" in lower:
                violations.append(
                    f"{path.as_posix()}:{lineno}: installed payload must not "
                    f"use source repo skills/scripts path: {line.strip()[:120]}"
                )
            continue
        if "source repo" not in lower and "repo-side" not in lower:
            violations.append(
                f"{path.as_posix()}:{lineno}: repo-only path reference "
                f"without 'source repo' label: {line.strip()[:120]}"
            )

if violations:
    sys.stderr.write("\n".join(violations) + "\n")
    raise SystemExit(1)

sys.stdout.write("check-installed-payload-self-contained: ok\n")
PY
