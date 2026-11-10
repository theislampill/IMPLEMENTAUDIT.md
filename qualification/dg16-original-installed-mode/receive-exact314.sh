#!/usr/bin/env bash
# Root-only targeted receiving helper; does not dispatch or provision a runtime.
set -eu
if [ "$#" -ne 3 ]; then
  printf 'usage: %s PRISTINE_REPO_ROOT CANDIDATE_REPO_ROOT EVIDENCE_DIR\n' "$0" >&2
  exit 2
fi
original=$1
candidate=$2
output=$3
python -c 'import sys; assert sys.version_info[:3] == (3, 14, 4), sys.version'
mkdir -p "$output"
python -c 'import platform,sys; print(sys.version); print(platform.platform())' > "$output/environment.txt"
set +e
python -B "$original/fixtures/package-contract/installed_modes_test.py" --repo-root "$original" --json-output "$output/red.json" > "$output/red.log" 2>&1
red_status=$?
python -B "$candidate/fixtures/package-contract/installed_modes_test.py" --repo-root "$candidate" --json-output "$output/green.json" > "$output/green.log" 2>&1
green_status=$?
set -e
python - "$output" "$red_status" "$green_status" <<'PY'
import json, pathlib, sys
root=pathlib.Path(sys.argv[1])
red=json.loads((root/'red.json').read_text())
green=json.loads((root/'green.json').read_text())
assert sys.argv[2:] == ['1','0'], sys.argv[2:]
assert any(r['owner']=='package-contract.py' and r['platform_model']=='nt' and r['mutation']=='positive-control' and not r['passed'] and r['message'].startswith('installed plugin member mode mismatch:') for r in red['cases'])
assert green['passed']==green['total']==45
assert all(r['passed'] and r['accepted']==r['expected_accept'] for r in green['cases'])
assert sum(not r['expected_accept'] for r in green['cases'])==39
print('Targeted exact Python3.14.4 source+modeled-metadata receiving: RED then45/45GREEN; no nativeWindows qualification')
PY