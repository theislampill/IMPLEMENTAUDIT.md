#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export PYTHONDONTWRITEBYTECODE=1
python -B tests/composite-source-cases.py
# Keep the frozen rotation peak-memory gate independent of the large research
# capsule comparison above. These are new disposable receiving controls.
python -B tests/cognition-original14-history.py
