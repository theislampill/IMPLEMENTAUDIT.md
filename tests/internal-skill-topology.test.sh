#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

expected_population="audit-andon audit-assess audit-implement audit-state implementaudit"
actual_population="$({
  find skills -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print
} | sed -E 's#^skills/([^/]+)/SKILL\.md$#\1#' | LC_ALL=C sort | paste -sd' ' -)"

if [ "$actual_population" != "$expected_population" ]; then
  printf 'internal-skill-topology.test: source population mismatch\n' >&2
  printf 'expected: %s\n' "$expected_population" >&2
  printf 'actual:   %s\n' "$actual_population" >&2
  exit 1
fi

python - <<'PY'
import json
from pathlib import Path

contract = json.loads(Path("package/implementaudit-package.json").read_text(encoding="utf-8"))
expected_required = ["implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon"]
expected_internal = [
    {"name": "audit-state", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-assess", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-implement", "maintainer_only": True, "directly_invocable": False},
    {"name": "audit-andon", "maintainer_only": False, "directly_invocable": True},
]

assert contract.get("public_governor") == "implementaudit", contract.get("public_governor")
assert contract.get("required_skills") == expected_required, contract.get("required_skills")
assert contract.get("internal_skills") == expected_internal, contract.get("internal_skills")
PY

printf 'internal-skill-topology.test: ok\n'
