#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python "$ROOT/scripts/check-genealogy-corpus.py" --root "$ROOT"
