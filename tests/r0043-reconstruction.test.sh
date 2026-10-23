#!/usr/bin/env bash
# R0043 is published, canonically unallocated. Repository documentary tooling only.
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$root/tests/r0043_reconstruction_tests.py" "$root"
