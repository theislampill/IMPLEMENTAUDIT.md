#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1. The tracked fixture pack must pass.
bash scripts/check-agent-eval-fixtures.sh

# 2. A missing fixture must fail.
mkdir -p "$tmp/missing"
cp fixtures/agent-eval/terminal-cap-request.md "$tmp/missing/"
if bash scripts/check-agent-eval-fixtures.sh "$tmp/missing" >/dev/null 2>&1; then
  printf 'agent-eval-fixtures.test: expected missing fixtures to fail\n' >&2
  exit 1
fi

# 3. A fixture missing a required section must fail.
mkdir -p "$tmp/broken"
cp fixtures/agent-eval/*.md "$tmp/broken/"
python - "$tmp/broken/release-bot-overreach.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
p.write_text(p.read_text(encoding="utf-8").replace("## Forbidden behavior", "## Renamed"), encoding="utf-8")
PY
if bash scripts/check-agent-eval-fixtures.sh "$tmp/broken" >/dev/null 2>&1; then
  printf 'agent-eval-fixtures.test: expected missing section to fail\n' >&2
  exit 1
fi

# 4. A fixture without the evidence-boundary disclaimer must fail.
mkdir -p "$tmp/overclaim"
cp fixtures/agent-eval/*.md "$tmp/overclaim/"
python - "$tmp/overclaim/lean-glossary-theater.md" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
mutated = text.replace("proof of live model behavior", "fully proven behavior")
if mutated == text:
    raise SystemExit("test setup error: disclaimer fragment not found to mutate")
p.write_text(mutated, encoding="utf-8")
PY
if bash scripts/check-agent-eval-fixtures.sh "$tmp/overclaim" >/dev/null 2>&1; then
  printf 'agent-eval-fixtures.test: expected missing disclaimer to fail\n' >&2
  exit 1
fi

printf 'agent-eval-fixtures.test: ok\n'
