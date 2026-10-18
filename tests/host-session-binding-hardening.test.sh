#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 -B "$repo_root/tests/host_session_binding_hardening.py" "$@"
elif command -v python >/dev/null 2>&1; then
  python -B "$repo_root/tests/host_session_binding_hardening.py" "$@"
elif command -v py >/dev/null 2>&1; then
  py -3 -B "$repo_root/tests/host_session_binding_hardening.py" "$@"
else
  printf 'host-session-binding-hardening.test: Python 3 is required\n' >&2
  exit 1
fi
