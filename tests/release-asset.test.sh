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

# Skill content must be at archive root (no skills/ prefix) for Claude import.
required = {
    "SKILL.md",
    "references/planning-depth.md",
    "references/phase-design.md",
    "references/goal-format.md",
    "references/transcript-contract.md",
    "references/routing.md",
    "references/repo-state-comparison.md",
    "references/child-agents.md",
    "scripts/claim-run.sh",
    "scripts/detect-env.sh",
    "scripts/detect-stack.sh",
    "scripts/repo-state.sh",
    "scripts/summarize-repo.sh",
    "scripts/validate-audit-spec.sh",
    "scripts/validate-phase.sh",
    "templates/ROADMAP.md",
    "templates/STATE.md",
    "templates/THINKING.md",
    "templates/phase-goal.txt",
    "templates/child-agent-report.md",
    "templates/PROTOCOL.md",
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
# Positive whitelist: only these top-level names are allowed at archive root.
# Anything else (repo scripts/, docs/, fixtures/, tests/, README.md, etc.) is rejected.
allowed_top_level = {"SKILL.md", "references", "scripts", "templates", ".claude-plugin"}

with zipfile.ZipFile(asset) as zf:
    names = set(zf.namelist())

    # Regression guard: skills/SKILL.md must NOT be in the archive.
    # Claude import requires SKILL.md at archive root.
    if "skills/SKILL.md" in names:
        raise SystemExit(
            "REGRESSION: archive has skills/SKILL.md at nested path; "
            "SKILL.md must be at archive root for Claude import"
        )

    missing = sorted(required - names)
    if missing:
        raise SystemExit("missing asset entries: " + ", ".join(missing))

    top_level = {Path(name).parts[0] for name in names if Path(name).parts}
    unexpected = sorted(top_level - allowed_top_level)
    if unexpected:
        raise SystemExit("unexpected top-level paths in archive: " + ", ".join(unexpected))

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

        # SKILL.md must be at archive root.
        if not (root / "SKILL.md").is_file():
            raise SystemExit("SKILL.md must be at archive root")

        # skills/ subdirectory must not exist at archive root.
        if (root / "skills").exists():
            raise SystemExit(
                "REGRESSION: skills/ subdirectory at archive root; "
                "skill content must be at archive root for Claude import"
            )

        plugin = json.loads((root / ".claude-plugin/plugin.json").read_text())
        if plugin.get("version") != "0.2.5":
            raise SystemExit("expected plugin version 0.2.5")
        if plugin.get("skills") != "./":
            raise SystemExit(
                "expected plugin skills path ./ "
                "(SKILL.md at archive root for Claude import)"
            )
        if (root / "IMPLEMENTAUDIT.md").exists():
            raise SystemExit("root IMPLEMENTAUDIT.md must not be included")

print("release-asset.test: ok")
PY
