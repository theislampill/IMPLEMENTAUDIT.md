#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'install-codex-from-release: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  scripts/install-codex-from-release.sh --asset PATH [--checksum PATH] [--codex-home PATH] [--version 0.3.1]
  scripts/install-codex-from-release.sh --url URL [--checksum-url URL] [--codex-home PATH] [--version 0.3.1]
  scripts/install-codex-from-release.sh --tag vX.Y.Z.W [--repo OWNER/REPO] [--codex-home PATH] [--version 0.3.1]

Installs IMPLEMENTAUDIT.skill into a Codex-style skill directory:
  $CODEX_HOME/skills/implementaudit

This script validates archive shape and checksum when a manifest is supplied.
It does not install Graphify, install ActiveGraph, index, configure event stores,
push, tag, release, or publish provenance.
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
codex_home="${CODEX_HOME:-$HOME/.codex}"
expected_version="0.3.1"

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
    --codex-home)
      [ "$#" -ge 2 ] || fail "--codex-home requires a path"
      codex_home="$2"
      shift 2
      ;;
    --version)
      [ "$#" -ge 2 ] || fail "--version requires a version"
      expected_version="$2"
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

"${py_cmd[@]}" - "$asset" "$checksum" "$codex_home" "$expected_version" <<'PY'
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
codex_home = Path(sys.argv[3]).expanduser()
expected_version = sys.argv[4]

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

# Required archive entries — skill content at root (no skills/ prefix).
required_archive = {
    "SKILL.md",
    "references/planning-depth.md",
    "references/phase-design.md",
    "references/goal-format.md",
    "references/transcript-contract.md",
    "references/continuity.md",
    "references/routing.md",
    "references/repo-state-comparison.md",
    "references/sidecars.md",
    "references/child-agents.md",
    "references/lean-operating-discipline.md",
    "references/audit-category-matrix.md",
    "references/audit-playbook.md",
    "references/plan-lifecycle.md",
    "scripts/claim-run.sh",
    "scripts/detect-env.sh",
    "scripts/detect-stack.sh",
    "scripts/repo-state.sh",
    "scripts/summarize-repo.sh",
    "scripts/validate-audit-spec.sh",
    "scripts/validate-phase.sh",
    "scripts/validate-run-root.sh",
    "scripts/custody-append.sh",
    "templates/ROADMAP.md",
    "templates/STATE.md",
    "templates/THINKING.md",
    "templates/phase-goal.txt",
    "templates/child-agent-report.md",
    "templates/final-report.md",
    "templates/read-only-plan.md",
    "templates/PROTOCOL.md",
    "templates/sidecars.md",
    "templates/tools.md",
    "templates/context.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
}

with zipfile.ZipFile(asset) as zf:
    names = set(zf.namelist())

    # Regression guard: wrong-shape archive must be rejected.
    if "skills/implementaudit/SKILL.md" in names:
        raise SystemExit(
            "archive has skills/implementaudit/SKILL.md at nested path; "
            "SKILL.md must be at archive root for Claude import"
        )

    missing = sorted(required_archive - names)
    if missing:
        raise SystemExit("asset missing required entries: " + ", ".join(missing))

    # Only allowed top-level entries may appear.
    allowed_top_level = {"SKILL.md", "references", "scripts", "templates", ".claude-plugin"}
    top_level = {Path(name).parts[0] for name in names if Path(name).parts}
    extra_top_level = sorted(top_level - allowed_top_level)
    if extra_top_level:
        raise SystemExit(
            "asset contains unexpected top-level paths: " + ", ".join(extra_top_level)
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
        if plugin.get("version") != expected_version:
            raise SystemExit(
                f"plugin version must be {expected_version}, got {plugin.get('version')}"
            )
        if plugin.get("skills") != "./":
            raise SystemExit("plugin skills path must be ./ (SKILL.md at archive root)")
        if (root / "IMPLEMENTAUDIT.md").exists():
            raise SystemExit("root IMPLEMENTAUDIT.md must be absent")
        if not (root / "SKILL.md").is_file():
            raise SystemExit("SKILL.md must be at archive root")
        if (root / "skills").exists():
            raise SystemExit(
                "skills/ subdirectory must not exist at archive root; "
                "skill content must be at archive root"
            )

        target = codex_home / "skills" / "implementaudit"
        resolved_home = codex_home.resolve(strict=False)
        resolved_target = target.resolve(strict=False)
        if not str(resolved_target).startswith(str(resolved_home)):
            raise SystemExit("target path escapes codex home")

        target.parent.mkdir(parents=True, exist_ok=True)
        tmp_target = target.parent / f".implementaudit-install-{os.getpid()}"
        if tmp_target.exists():
            shutil.rmtree(tmp_target)
        tmp_target.mkdir(parents=True)

        # Copy skill content from archive root to tmp_target (skip .claude-plugin/).
        for child in root.iterdir():
            if child.name == ".claude-plugin":
                continue
            dest = tmp_target / child.name
            if child.is_file():
                shutil.copy2(child, dest)
            elif child.is_dir():
                shutil.copytree(child, dest)

        for rel in [
            "SKILL.md",
            "references/planning-depth.md",
            "references/phase-design.md",
            "references/goal-format.md",
            "references/transcript-contract.md",
            "references/continuity.md",
            "references/routing.md",
            "references/repo-state-comparison.md",
            "references/sidecars.md",
            "references/child-agents.md",
            "references/lean-operating-discipline.md",
            "references/audit-category-matrix.md",
            "references/audit-playbook.md",
            "references/plan-lifecycle.md",
            "scripts/claim-run.sh",
            "scripts/detect-env.sh",
            "scripts/detect-stack.sh",
            "scripts/repo-state.sh",
            "scripts/summarize-repo.sh",
            "scripts/validate-audit-spec.sh",
            "scripts/validate-phase.sh",
            "scripts/validate-run-root.sh",
            "scripts/custody-append.sh",
            "templates/ROADMAP.md",
            "templates/STATE.md",
            "templates/THINKING.md",
            "templates/phase-goal.txt",
            "templates/child-agent-report.md",
            "templates/final-report.md",
            "templates/read-only-plan.md",
            "templates/PROTOCOL.md",
            "templates/sidecars.md",
            "templates/tools.md",
            "templates/context.md",
        ]:
            if not (tmp_target / rel).is_file():
                raise SystemExit(f"installed skill missing required file: {rel}")

        if target.exists():
            shutil.rmtree(target)
        tmp_target.rename(target)

sys.stdout.write(f"install-codex-from-release: installed {asset.name} into {target}\n")
sys.stdout.write(f"install-codex-from-release: sha256 {digest}\n")
PY
