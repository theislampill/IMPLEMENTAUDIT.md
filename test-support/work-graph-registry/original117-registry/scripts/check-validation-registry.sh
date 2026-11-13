#!/usr/bin/env bash
set -euo pipefail

# Validation-registry reachability meta-gate. scripts/verify-package.sh is the
# one hand-edited test registry. CI must invoke that canonical registry once,
# without maintaining a second direct-test list that can drift or duplicate
# work (the former dual-registry defect was proven at v0.2.9.0).
#
# Usage: check-validation-registry.sh [--repo-root <dir>]

fail() {
  printf 'check-validation-registry: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "${1:-}" = "--repo-root" ]; then
  [ "$#" -ge 2 ] || fail "--repo-root requires a directory argument"
  repo_root="$2"
fi
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

"${py_cmd[@]}" - <<'PY'
import re
import sys
from pathlib import Path

tests = sorted(p.name for p in Path("tests").glob("*.test.sh"))
if not tests:
    sys.stderr.write("no tests/*.test.sh found\n")
    raise SystemExit(1)

verify_pkg = Path("scripts/verify-package.sh").read_text(encoding="utf-8")
ci = Path(".github/workflows/validate.yml").read_text(encoding="utf-8")

def invocation_count(text: str, ref: str) -> int:
    pattern = re.compile(
        rf"(?m)^\s*(?:-\s*)?(?:run:\s*)?(?:bash|sh)\s+{re.escape(ref)}(?:\s|$)"
    )
    return len(pattern.findall(text))

failures = []
for name in tests:
    ref = f"tests/{name}"
    if invocation_count(verify_pkg, ref) != 1:
        failures.append(f"{ref} is not invoked by scripts/verify-package.sh")

canonical_route = invocation_count(ci, "scripts/verify-package.sh")
if canonical_route != 1:
    failures.append(
        ".github/workflows/validate.yml must invoke scripts/verify-package.sh exactly once"
    )
for name in tests:
    ref = f"tests/{name}"
    if invocation_count(ci, ref):
        failures.append(
            f"{ref} is directly invoked by .github/workflows/validate.yml; use the canonical registry"
        )

if failures:
    sys.stderr.write("\n".join(failures) + "\n")
    raise SystemExit(1)

sys.stdout.write(
    f"check-validation-registry: ok ({len(tests)} tests; one canonical CI route)\n"
)
PY
