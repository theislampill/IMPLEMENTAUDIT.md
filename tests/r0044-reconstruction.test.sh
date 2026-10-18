#!/usr/bin/env bash
set -euo pipefail

# Issue-owned research reconstruction controls. Canonical registration is an
# explicit serial-integration patch; do not infer full corpus access from the
# default offline run. --custody-root additionally exercises pinned source.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
python "$repo_root/tests/r0044-reconstruction.py" "$@"
