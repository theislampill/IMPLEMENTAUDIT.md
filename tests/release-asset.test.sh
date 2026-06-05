#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_parent="$(mktemp -d)"
trap 'rm -rf "$tmp_parent"' EXIT

out_dir="$tmp_parent/path with spaces"
mkdir -p "$out_dir"

bash scripts/build-release-asset.sh "$out_dir"

asset="$out_dir/IMPLEMENTAUDIT.skill"
[ -f "$asset" ] || {
  printf 'release-asset.test: missing asset\n' >&2
  exit 1
}

bash scripts/write-release-checksums.sh "$asset" "$out_dir/CHECKSUMS.txt"
bash scripts/write-release-checksums.sh --check "$asset" "$out_dir/CHECKSUMS.txt"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'release-asset.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

"${py_cmd[@]}" - "$asset" <<'PY'
import json
import sys
import tempfile
import zipfile
from pathlib import Path

asset = Path(sys.argv[1])
required = {
    "skills/SKILL.md",
    "skills/references/planning-depth.md",
    "skills/references/phase-design.md",
    "skills/references/goal-format.md",
    "skills/references/transcript-contract.md",
    "skills/references/routing.md",
    "skills/references/child-agents.md",
    "skills/scripts/detect-env.sh",
    "skills/scripts/detect-stack.sh",
    "skills/scripts/summarize-repo.sh",
    "skills/scripts/validate-phase.sh",
    "skills/templates/ROADMAP.md",
    "skills/templates/STATE.md",
    "skills/templates/phase-goal.txt",
    "skills/templates/child-agent-report.md",
    "skills/templates/PROTOCOL.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "IMPLEMENTAUDIT.md",
    "README.md",
    "CHANGELOG.md",
    "docs/audits/INDEX.md",
}
blocked_parts = {
    ".git",
    ".IMPLEMENTAUDIT",
    "graphify-out",
    ".graphify",
    ".activegraph",
    "tmp",
    "temp",
    "dist",
}

with zipfile.ZipFile(asset) as zf:
    names = set(zf.namelist())
    missing = sorted(required - names)
    if missing:
        raise SystemExit("missing asset entries: " + ", ".join(missing))
    for name in names:
        parts = set(Path(name).parts)
        if parts & blocked_parts:
            raise SystemExit(f"blocked path included: {name}")
        if name.endswith((".log", ".tmp", ".activegraph.db")):
            raise SystemExit(f"blocked suffix included: {name}")
        if name.startswith(".env"):
            raise SystemExit(f"environment file included: {name}")
    with tempfile.TemporaryDirectory() as temp_dir:
        zf.extractall(temp_dir)
        root = Path(temp_dir)
        plugin = json.loads((root / ".claude-plugin/plugin.json").read_text())
        if plugin.get("version") != "0.2.2":
            raise SystemExit("expected plugin version 0.2.2")
        if (root / "IMPLEMENTAUDIT.md").read_bytes() != (root / "skills/SKILL.md").read_bytes():
            raise SystemExit("extracted mirror files drifted")

print("release-asset.test: ok")
PY
