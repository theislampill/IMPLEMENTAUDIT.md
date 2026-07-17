#!/usr/bin/env bash
# eval-harness.test.sh - the #9 evaluation harness self-test: scorer accepts
# synthetic passing transcripts and rejects failing ones for every fixture,
# and the runner dry-run completes without invoking any model.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v python >/dev/null 2>&1; then py=python
elif command -v python3 >/dev/null 2>&1; then py=python3
else echo "eval-harness.test: python required" >&2; exit 1; fi
"$py" "$repo_root/eval/selftest.py"
"$py" "$repo_root/eval/adversarial.py"
printf 'eval-harness.test: ok\n'
