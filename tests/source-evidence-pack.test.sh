#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'source-evidence-pack.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

pack="$tmp/IMPLEMENTAUDIT-SOURCE-EVIDENCE.zip"
bash scripts/build-source-evidence-pack.sh "$pack"

"${py_cmd[@]}" - "$pack" "$tmp/extract" <<'PY'
import sys
import zipfile
from pathlib import Path

pack = Path(sys.argv[1])
extract = Path(sys.argv[2])
with zipfile.ZipFile(pack) as zf:
    names = set(zf.namelist())
    required = {
        "RUN-VALIDATION.md",
        "skills/implementaudit/SKILL.md",
        "skills/implementaudit/references/sidecars.md",
        "skills/implementaudit/templates/final-report.md",
        "skills/implementaudit/templates/read-only-plan.md",
        "scripts/check-safeguard-restoration.sh",
        "scripts/check-agents-bootstrap-budget.sh",
        "tests/safeguard-restoration.test.sh",
        "tests/agents-bootstrap-budget.test.sh",
        "fixtures/safeguards/negative-missing-final-report.md",
        "docs/audits/RETENTION.md",
    }
    missing = sorted(required - names)
    if missing:
        raise SystemExit("source evidence pack missing: " + ", ".join(missing))
    forbidden_prefixes = [".git/", ".IMPLEMENTAUDIT/", "plans/", "graphify-out/", "docs/audits/archive/"]
    for prefix in forbidden_prefixes:
        if any(name.startswith(prefix) for name in names):
            raise SystemExit(f"forbidden source evidence prefix included: {prefix}")
    forbidden_exact = {"custody.db"}
    for exact in forbidden_exact:
        if exact in {Path(name).name for name in names}:
            raise SystemExit(f"forbidden source evidence file included: {exact}")
    forbidden_raw_local = [
        "codex-exec-transcript",
        "raw-local-diagnostic",
        "local-diagnostics",
    ]
    for needle in forbidden_raw_local:
        if any(needle in name.lower() for name in names):
            raise SystemExit(f"raw local evidence included in source pack: {needle}")
    zf.extractall(extract)

for path in extract.rglob("*.sh"):
    data = path.read_bytes()
    if b"\r\n" in data:
        rel = path.relative_to(extract).as_posix()
        raise SystemExit(f"CRLF shell script in source evidence pack: {rel}")
PY

(
  cd "$tmp/extract"
  bash scripts/check-safeguard-restoration.sh
  bash tests/safeguard-restoration.test.sh
  bash scripts/check-skill-bootstrap-budget.sh
  bash tests/plan-quality-contract.test.sh
  bash tests/agents-bootstrap-budget.test.sh
  bash scripts/check-audit-retention.sh
  bash tests/audit-retention.test.sh
  bash scripts/check-validation-registry.sh
) >"$tmp/source-pack-smoke.out" 2>&1

grep -F "check-safeguard-restoration: ok" "$tmp/source-pack-smoke.out" >/dev/null
grep -F "safeguard-restoration.test: ok" "$tmp/source-pack-smoke.out" >/dev/null
grep -F "check-skill-bootstrap-budget: ok" "$tmp/source-pack-smoke.out" >/dev/null
grep -F "plan-quality-contract.test: ok" "$tmp/source-pack-smoke.out" >/dev/null
grep -F "agents-bootstrap-budget.test: ok" "$tmp/source-pack-smoke.out" >/dev/null
grep -F "check-audit-retention: ok" "$tmp/source-pack-smoke.out" >/dev/null
grep -F "audit-retention.test: ok" "$tmp/source-pack-smoke.out" >/dev/null
grep -F "check-validation-registry: ok" "$tmp/source-pack-smoke.out" >/dev/null

printf 'source-evidence-pack.test: ok\n'
