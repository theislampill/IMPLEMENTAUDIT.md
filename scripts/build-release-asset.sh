#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'build-release-asset: %s\n' "$*" >&2
  exit 1
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
  fail "python, python3, or py -3 is required to build the release asset"
fi

asset_name="IMPLEMENTAUDIT.skill"
cleanup_dir=""

if [ "${1:-}" = "--check" ]; then
  out_dir="$(mktemp -d)"
  cleanup_dir="$out_dir"
else
  out_dir="${1:-dist}"
fi

trap 'if [ -n "${cleanup_dir:-}" ]; then rm -rf "$cleanup_dir"; fi' EXIT

mkdir -p "$out_dir"
asset_path="$out_dir/$asset_name"
rm -f "$asset_path"

"${py_cmd[@]}" - "$asset_path" <<'PY'
import json
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

repo = Path.cwd()
asset = Path(sys.argv[1]).resolve()

# Source files that must exist in the repo before building.
# These use repo-relative paths (skills/ prefix included).
required_source = [
    "skills/SKILL.md",
    "skills/references/planning-depth.md",
    "skills/references/phase-design.md",
    "skills/references/goal-format.md",
    "skills/references/transcript-contract.md",
    "skills/references/routing.md",
    "skills/references/repo-state-comparison.md",
    "skills/references/child-agents.md",
    "skills/scripts/claim-run.sh",
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
]

for rel in required_source:
    if not (repo / rel).is_file():
        raise SystemExit(f"missing required asset input: {rel}")

# Archive entries that must be present in the built .skill file.
# Skill content is at archive root (no skills/ prefix) so Claude Desktop
# can import the .skill directly — SKILL.md at root, references/ at root, etc.
required_archive = [
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
]

blocked_parts = {
    ".git",
    ".IMPLEMENTAUDIT",
    ".github",
    "docs",
    "fixtures",
    "tests",
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
blocked_suffixes = (".log", ".tmp", ".db", ".sqlite", ".sqlite3", ".jsonl")


def blocked(rel: Path) -> bool:
    text = rel.as_posix()
    if any(part in blocked_parts for part in rel.parts):
        return True
    if rel.name in blocked_names:
        return True
    if text.startswith(".env"):
        return True
    return text.endswith(blocked_suffixes)


# Build entries as (archive_path, source_path) pairs.
# Skill files: archive path strips skills/ prefix so SKILL.md is at root.
# Plugin files: archive path is .claude-plugin/... (unchanged).
entries = []

skills_dir = repo / "skills"
for child in sorted(skills_dir.rglob("*")):
    if child.is_file():
        archive_rel = child.relative_to(skills_dir)
        if blocked(archive_rel):
            raise SystemExit(f"blocked file selected for asset: {archive_rel.as_posix()}")
        entries.append((archive_rel, child))

for plugin_rel_str in [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]:
    plugin_rel = Path(plugin_rel_str)
    plugin_path = repo / plugin_rel
    if blocked(plugin_rel):
        raise SystemExit(f"blocked plugin file: {plugin_rel}")
    entries.append((plugin_rel, plugin_path))

seen = set()
deduped = []
for archive_rel, src_path in entries:
    key = archive_rel.as_posix()
    if key not in seen:
        seen.add(key)
        deduped.append((archive_rel, src_path))

TEXT_SUFFIXES = {".md", ".txt", ".sh", ".json", ".yaml", ".yml"}


def read_normalized(path: Path) -> bytes:
    """Read file, normalizing CRLF → LF for text files.

    Claude Desktop and YAML parsers expect LF line endings.
    Windows git checkouts produce CRLF; normalize here so the
    archive is portable and YAML frontmatter parses correctly.
    """
    if path.suffix.lower() in TEXT_SUFFIXES:
        raw = path.read_bytes()
        return raw.replace(b"\r\n", b"\n")
    return path.read_bytes()


asset.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(asset, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for archive_rel, src_path in deduped:
        info = zipfile.ZipInfo(archive_rel.as_posix())
        mode = 0o755 if archive_rel.as_posix().startswith("scripts/") else 0o644
        info.external_attr = (stat.S_IFREG | mode) << 16
        # Explicitly set compress_type on the ZipInfo object.
        # When writestr() receives a ZipInfo, the ZipInfo.compress_type overrides
        # the ZipFile-level default, and ZipInfo defaults to ZIP_STORED (0).
        # Without this line all entries are stored uncompressed even though the
        # ZipFile was opened with compression=ZIP_DEFLATED.
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, read_normalized(src_path))

with zipfile.ZipFile(asset) as zf:
    names = set(zf.namelist())

    # Regression guard: skills/SKILL.md must NOT be in the archive.
    # The archive root must contain SKILL.md directly for Claude import.
    if "skills/SKILL.md" in names:
        raise SystemExit(
            "archive has skills/SKILL.md at nested path; SKILL.md must be at archive root"
        )

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
        if blocked(rel):
            raise SystemExit(f"blocked file found in asset: {name}")

    missing = [name for name in required_archive if name not in names]
    if missing:
        raise SystemExit(f"asset missing required files: {', '.join(missing)}")

    with tempfile.TemporaryDirectory() as tmp:
        zf.extractall(tmp)
        extracted = Path(tmp)
        plugin = json.loads((extracted / ".claude-plugin/plugin.json").read_text())
        marketplace = json.loads((extracted / ".claude-plugin/marketplace.json").read_text())
        if plugin.get("name") != "implementaudit":
            raise SystemExit("extracted plugin name must be implementaudit")
        if plugin.get("version") != "0.2.8":
            raise SystemExit("extracted plugin version must be 0.2.8")
        if plugin.get("skills") != "./":
            raise SystemExit(
                "extracted plugin skills path must be ./ "
                "(SKILL.md at archive root for Claude import)"
            )
        if not marketplace.get("plugins"):
            raise SystemExit("extracted marketplace plugins list is required")
        if (extracted / "IMPLEMENTAUDIT.md").exists():
            raise SystemExit("extracted root IMPLEMENTAUDIT.md must be absent")
        # Verify SKILL.md is at root, not nested under skills/
        if not (extracted / "SKILL.md").is_file():
            raise SystemExit("SKILL.md must be at archive root")
        # Verify SKILL.md has no CRLF (Claude Desktop YAML parser requires LF).
        skill_md_bytes = (extracted / "SKILL.md").read_bytes()
        if b"\r\n" in skill_md_bytes:
            raise SystemExit(
                "SKILL.md contains CRLF line endings; archive must use LF for Claude import"
            )
        if (extracted / "skills").exists():
            raise SystemExit(
                "skills/ subdirectory must not exist at archive root; "
                "skill content must be at archive root for Claude import"
            )

print(f"build-release-asset: wrote {asset}")
print("build-release-asset: extraction validation ok")
PY
