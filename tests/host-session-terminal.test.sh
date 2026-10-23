#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 -B "$repo_root/tests/host_session_terminal.py"
else
  python -B "$repo_root/tests/host_session_terminal.py"
fi
