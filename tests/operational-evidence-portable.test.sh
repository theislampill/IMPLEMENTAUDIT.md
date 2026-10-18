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
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-routes.py" --consumer "$repo_root/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-occurrences.py" --target "$repo_root/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-route-repairs.py" --consumer "$repo_root/scripts/operational_query_policy.py" --occurrence "$repo_root/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-preparation.py" --target "$repo_root/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-integration.py" "$repo_root"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-route-bindings.py" --target "$repo_root/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/captured-product-bindings.py" --target "$repo_root/scripts/operational_query_policy.py"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/windows-reader.py" "$repo_root"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/windows-export.py" "$repo_root"
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/native-route-projection.py" "$repo_root"
"${py_cmd[@]}" -I -S -B "$repo_root/fixtures/operational-evidence/native-episode-projection.py" "$repo_root"
"${py_cmd[@]}" -I -S -B "$repo_root/fixtures/operational-evidence/native-episode-controls/run_native_source_regressions.py" --repo-root "$repo_root"
"${py_cmd[@]}" -I -S -B "$repo_root/fixtures/operational-evidence/native-peer-controls.py" --repo-root "$repo_root" --suite route
"${py_cmd[@]}" -I -S -B "$repo_root/fixtures/operational-evidence/native-peer-controls.py" --repo-root "$repo_root" --suite security
"${py_cmd[@]}" -I -S -B "$repo_root/fixtures/operational-evidence/native-peer-controls.py" --repo-root "$repo_root" --suite directory --case test_multiple_pages_unicode_names_and_population_bound
"${py_cmd[@]}" -I -S -B "$repo_root/fixtures/operational-evidence/native-peer-controls.py" --repo-root "$repo_root" --suite directory-race
"${py_cmd[@]}" -B "$repo_root/fixtures/operational-evidence/review-regressions.py" "$repo_root"
