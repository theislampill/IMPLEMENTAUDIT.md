#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'install-claude-from-release: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  scripts/install-claude-from-release.sh --asset PATH --claude-skills-dir PATH [--checksum PATH]
  scripts/install-claude-from-release.sh --url URL --claude-skills-dir PATH [--checksum-url URL]
  scripts/install-claude-from-release.sh --tag vX.Y.Z.W --claude-skills-dir PATH [--repo OWNER/REPO]

Copies IMPLEMENTAUDIT.skill skill payload into a Claude skill directory:
  <CLAUDE_SKILLS_DIR>/

This script validates archive shape and checksum when a manifest is supplied.
It does not install Graphify, install ActiveGraph, index, configure event stores,
push, tag, release, or publish provenance.

Finding the Claude skills directory:
  Claude Desktop stores session-managed skills under a session-specific path.
  On Windows:   %APPDATA%\Claude\local-agent-mode-sessions\skills-plugin\
  On macOS:     ~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/
  On Linux:     ~/.config/Claude/local-agent-mode-sessions/skills-plugin/

  Under that root, look for a subtree containing skills/implementaudit/.
  Pass the full path to the implementaudit skill directory as --claude-skills-dir.

  Example (Windows):
    --claude-skills-dir "%APPDATA%\Claude\local-agent-mode-sessions\skills-plugin\<id>\<id>\skills\implementaudit"

  After install, Claude Desktop must reload or restart to pick up the changes.
  If a skill was previously installed via Claude Desktop UI, the UI-managed
  update path (if available in your Claude version) is preferred over this script.

This script does not prove marketplace behavior, passive auto-update,
or that Claude Desktop will load the skill. It copies files only.
No install proof is made by this script; use Claude Desktop to confirm the skill runs.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

asset=""
asset_url=""
checksum=""
checksum_url=""
tag=""
repo="theislampill/IMPLEMENTAUDIT.md"
claude_skills_dir=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --asset)
      [ "$#" -ge 2 ] || fail "--asset requires a path"
      asset="$2"
      shift 2
      ;;
    --url)
      [ "$#" -ge 2 ] || fail "--url requires a URL"
      asset_url="$2"
      shift 2
      ;;
    --checksum)
      [ "$#" -ge 2 ] || fail "--checksum requires a path"
      checksum="$2"
      shift 2
      ;;
    --checksum-url)
      [ "$#" -ge 2 ] || fail "--checksum-url requires a URL"
      checksum_url="$2"
      shift 2
      ;;
    --tag)
      [ "$#" -ge 2 ] || fail "--tag requires a tag"
      tag="$2"
      shift 2
      ;;
    --repo)
      [ "$#" -ge 2 ] || fail "--repo requires OWNER/REPO"
      repo="$2"
      shift 2
      ;;
    --claude-skills-dir)
      [ "$#" -ge 2 ] || fail "--claude-skills-dir requires a path"
      claude_skills_dir="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

if [ -n "$tag" ]; then
  [ -z "$asset" ] || fail "use either --tag or --asset, not both"
  [ -z "$asset_url" ] || fail "use either --tag or --url, not both"
  asset_url="https://github.com/${repo}/releases/download/${tag}/IMPLEMENTAUDIT.skill"
  checksum_url="https://github.com/${repo}/releases/download/${tag}/CHECKSUMS.txt"
fi

if [ -n "$asset_url" ] && [ -n "$asset" ]; then
  fail "use either --asset or --url, not both"
fi

if [ -z "$asset" ] && [ -z "$asset_url" ]; then
  fail "provide --asset PATH, --url URL, or --tag TAG"
fi

if [ -z "$claude_skills_dir" ]; then
  fail "--claude-skills-dir is required; see --help for how to find the Claude skill directory"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if [ -n "$asset_url" ]; then
  command -v curl >/dev/null 2>&1 || fail "curl is required for --url/--tag"
  asset="$tmp/IMPLEMENTAUDIT.skill"
  curl --fail --location --show-error --silent "$asset_url" --output "$asset"
fi

if [ -n "$checksum_url" ]; then
  command -v curl >/dev/null 2>&1 || fail "curl is required for --checksum-url/--tag"
  checksum="$tmp/CHECKSUMS.txt"
  curl --fail --location --show-error --silent "$checksum_url" --output "$checksum"
fi

"${py_cmd[@]}" - "$asset" "$checksum" "$claude_skills_dir" <<'PY'
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

asset = Path(sys.argv[1]).expanduser()
checksum = Path(sys.argv[2]).expanduser() if sys.argv[2] else None
target_dir = Path(sys.argv[3]).expanduser()

if not asset.is_file():
    raise SystemExit(f"missing asset: {asset}")

if asset.name != "IMPLEMENTAUDIT.skill":
    raise SystemExit("asset must be named IMPLEMENTAUDIT.skill")

digest = hashlib.sha256(asset.read_bytes()).hexdigest()
if checksum:
    if not checksum.is_file():
        raise SystemExit(f"missing checksum manifest: {checksum}")
    text = checksum.read_text(encoding="utf-8").strip().splitlines()
    matches = []
    for line in text:
        parts = line.split()
        if len(parts) == 3 and parts[0].lower() == "sha256" and parts[2] == asset.name:
            matches.append(parts[1].lower())
    if not matches:
        raise SystemExit(f"checksum manifest does not name {asset.name}")
    if digest.lower() not in matches:
        raise SystemExit("checksum manifest is stale or mismatched")

blocked_parts = {
    ".git",
    ".IMPLEMENTAUDIT",
    "graphify-out",
    ".graphify",
    ".activegraph",
    "dist",
    "tmp",
    "temp",
}
blocked_names = {
    "graph.json",
    "quickstart_demo_run.db",
}
blocked_suffixes = (".log", ".tmp", ".db", ".sqlite", ".sqlite3", ".jsonl")

required_archive = {
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
}

with zipfile.ZipFile(asset) as zf:
    names = set(zf.namelist())
    missing = sorted(required_archive - names)
    if missing:
        raise SystemExit("asset missing required entries: " + ", ".join(missing))
    allowed_top_level = {"skills", ".claude-plugin"}
    top_level = {Path(name).parts[0] for name in names if Path(name).parts}
    extra_top_level = sorted(top_level - allowed_top_level)
    if extra_top_level:
        raise SystemExit(
            "asset contains repo-only top-level paths: " + ", ".join(extra_top_level)
        )
    for name in names:
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts:
            raise SystemExit(f"unsafe archive path: {name}")
        if set(rel.parts) & blocked_parts:
            raise SystemExit(f"blocked archive path: {name}")
        if rel.name in blocked_names:
            raise SystemExit(f"blocked archive entry: {name}")
        if name.endswith(blocked_suffixes) or name.startswith(".env"):
            raise SystemExit(f"blocked archive entry: {name}")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        zf.extractall(root)
        plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        if plugin.get("name") != "implementaudit":
            raise SystemExit("plugin name must be implementaudit")
        if plugin.get("skills") != "./skills/":
            raise SystemExit("plugin skills path must be ./skills/")
        if (root / "IMPLEMENTAUDIT.md").exists():
            raise SystemExit("root IMPLEMENTAUDIT.md must be absent")

        skills_root = root / "skills"
        target_dir.mkdir(parents=True, exist_ok=True)
        tmp_target = target_dir.parent / f".implementaudit-claude-install-{os.getpid()}"
        if tmp_target.exists():
            shutil.rmtree(tmp_target)
        shutil.copytree(skills_root, tmp_target)

        for rel in [
            "SKILL.md",
            "references/planning-depth.md",
            "references/phase-design.md",
            "references/goal-format.md",
            "references/transcript-contract.md",
            "references/routing.md",
            "references/repo-state-comparison.md",
            "references/child-agents.md",
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
        ]:
            if not (tmp_target / rel).is_file():
                raise SystemExit(f"staging skill missing required file: {rel}")

        if target_dir.exists():
            shutil.rmtree(target_dir)
        tmp_target.rename(target_dir)

sys.stdout.write(f"install-claude-from-release: installed {asset.name} into {target_dir}\n")
sys.stdout.write(f"install-claude-from-release: sha256 {digest}\n")
sys.stdout.write(
    "install-claude-from-release: NOTICE: restart Claude Desktop to reload the skill.\n"
)
sys.stdout.write(
    "install-claude-from-release: NOTICE: this copies files only. "
    "No install proof is made by this script. Verify in Claude Desktop after restart.\n"
)
PY
