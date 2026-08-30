#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

printf 'composite inline preflight\n'

bash scripts/alpha.sh
bash scripts/bravo.sh \
  --flag value
bash tests/charlie.test.sh
