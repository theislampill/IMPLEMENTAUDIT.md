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
    "skills/references/repo-state-comparison.md",
    "skills/references/child-agents.md",
    "skills/scripts/detect-env.sh",
    "skills/scripts/detect-stack.sh",
    "skills/scripts/repo-state.sh",
    "skills/scripts/summarize-repo.sh",
    "skills/scripts/validate-audit-spec.sh",
    "skills/scripts/validate-phase.sh",
    "skills/templates/ROADMAP.md",
    "skills/templates/STATE.md",
    "skills/templates/THINKING.md",
    "skills/templates/phase-goal.txt",
    "skills/templates/child-agent-report.md",
    "skills/templates/PROTOCOL.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
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
blocked_names = {
    "graph.json",
    "quickstart_demo_run.db",
}
blocked_top_level = {
    ".github",
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "README.md",
    "docs",
    "fixtures",
    "scripts",
    "tests",
}

with zipfile.ZipFile(asset) as zf:
    names = set(zf.namelist())
    missing = sorted(required - names)
    if missing:
        raise SystemExit("missing asset entries: " + ", ".join(missing))
    top_level = {Path(name).parts[0] for name in names if Path(name).parts}
    unexpected = sorted(top_level & blocked_top_level)
    if unexpected:
        raise SystemExit("repo-only top-level paths included: " + ", ".join(unexpected))
    for name in names:
        parts = set(Path(name).parts)
        if parts & blocked_parts:
            raise SystemExit(f"blocked path included: {name}")
        if Path(name).name in blocked_names:
            raise SystemExit(f"blocked sidecar artifact included: {name}")
        if name.endswith((".log", ".tmp", ".db", ".sqlite", ".sqlite3", ".jsonl")):
            raise SystemExit(f"blocked suffix included: {name}")
        if name.startswith(".env"):
            raise SystemExit(f"environment file included: {name}")
    with tempfile.TemporaryDirectory() as temp_dir:
        zf.extractall(temp_dir)
        root = Path(temp_dir)
        plugin = json.loads((root / ".claude-plugin/plugin.json").read_text())
        if plugin.get("version") != "0.2.4":
            raise SystemExit("expected plugin version 0.2.4")
        if (root / "IMPLEMENTAUDIT.md").exists():
            raise SystemExit("root IMPLEMENTAUDIT.md must not be included")

print("release-asset.test: ok")
PY
