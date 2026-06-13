#!/usr/bin/env bash
set -euo pipefail

# Validation-registry parity meta-gate. The repo maintains two hand-edited
# suite registries: the internal run block in scripts/verify-package.sh and
# the CI test list in .github/workflows/validate.yml. They drift
# independently (proven at v0.2.9.0 in both directions). This gate asserts
# every tests/*.test.sh on disk is invoked in BOTH registries, with an
# explicit, reasoned exemption list.
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

# Exemptions from the verify-package registry only. Each entry needs a reason.
VERIFY_PACKAGE_EXEMPT = {
    # docs-portal.test.sh invokes verify-package.sh internally; nesting it
    # inside verify-package.sh would recurse (documented in AGENTS.md).
    "docs-portal.test.sh": "invokes verify-package.sh; must not nest",
}

tests = sorted(p.name for p in Path("tests").glob("*.test.sh"))
if not tests:
    sys.stderr.write("no tests/*.test.sh found\n")
    raise SystemExit(1)

verify_pkg = Path("scripts/verify-package.sh").read_text(encoding="utf-8")
ci = Path(".github/workflows/validate.yml").read_text(encoding="utf-8")

def invokes(text: str, ref: str) -> bool:
    pattern = re.compile(
        rf"(?m)^\s*(?:-\s*)?(?:run:\s*)?(?:bash|sh)\s+{re.escape(ref)}(?:\s|$)"
    )
    return bool(pattern.search(text))

failures = []
for name in tests:
    ref = f"tests/{name}"
    if not invokes(verify_pkg, ref) and name not in VERIFY_PACKAGE_EXEMPT:
        failures.append(f"{ref} is not invoked by scripts/verify-package.sh")
    if not invokes(ci, ref):
        failures.append(f"{ref} is not invoked by .github/workflows/validate.yml")

for name in VERIFY_PACKAGE_EXEMPT:
    if not (Path("tests") / name).is_file():
        failures.append(f"stale exemption for nonexistent test: {name}")

if failures:
    sys.stderr.write("\n".join(failures) + "\n")
    raise SystemExit(1)

sys.stdout.write(f"check-validation-registry: ok ({len(tests)} tests in both registries)\n")
PY
