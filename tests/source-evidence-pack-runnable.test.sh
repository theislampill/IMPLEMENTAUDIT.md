#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-capability-parity-contract.sh
bash tests/source-evidence-pack.test.sh

pack_tmp="$(mktemp -d)"
pack_path="$pack_tmp/source-evidence.zip"
if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'source-evidence-pack-runnable.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

bash scripts/build-source-evidence-pack.sh "$pack_path" >/dev/null
"${py_cmd[@]}" - "$pack_path" "$pack_tmp/extracted" <<'PY'
import sys
import zipfile
from pathlib import Path

pack = Path(sys.argv[1])
extract = Path(sys.argv[2])
with zipfile.ZipFile(pack) as zf:
    zf.extractall(extract)
PY
(
  cd "$pack_tmp/extracted"
  bash scripts/check-safeguard-restoration.sh
) >/dev/null

rm -rf "$pack_tmp"

printf 'source-evidence-pack-runnable.test: ok\n'
