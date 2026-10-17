#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
else
  py_cmd=(python3)
fi
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/portable-regressions.py" "$repo_root"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-consumers.py" "$repo_root"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-routes.py" --consumer "$repo_root/skills/implementaudit/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-occurrences.py" --target "$repo_root/skills/implementaudit/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-route-repairs.py" --consumer "$repo_root/skills/implementaudit/scripts/operational_query_policy.py" --occurrence "$repo_root/skills/implementaudit/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-preparation.py" --target "$repo_root/skills/implementaudit/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-integration.py" "$repo_root"
