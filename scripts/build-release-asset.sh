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
source_skill_dir = repo / "skills" / "implementaudit"

# Source files that must exist in the repo before building.
# These use repo-relative paths (skills/ prefix included).
required_source = [
    "skills/implementaudit/SKILL.md",
    "skills/implementaudit/references/planning-depth.md",
    "skills/implementaudit/references/phase-design.md",
    "skills/implementaudit/references/goal-format.md",
    "skills/implementaudit/references/transcript-contract.md",
    "skills/implementaudit/references/continuity.md",
    "skills/implementaudit/references/routing.md",
    "skills/implementaudit/references/repo-state-comparison.md",
    "skills/implementaudit/references/sidecars.md",
    "skills/implementaudit/references/child-agents.md",
    "skills/implementaudit/references/lean-operating-discipline.md",
    "skills/implementaudit/references/audit-category-matrix.md",
    "skills/implementaudit/references/audit-playbook.md",
    "skills/implementaudit/references/plan-lifecycle.md",
    "skills/implementaudit/references/terminology-integration.md",
    "skills/implementaudit/references/convergence-mode.md",
    "skills/implementaudit/scripts/check-evidence-anchor.sh",
    "skills/implementaudit/scripts/check-lesson-lift.sh",
    "skills/implementaudit/scripts/check-handoff-packet.sh",
    "skills/implementaudit/scripts/check-closure-surface.sh",
    "skills/implementaudit/scripts/check-authorization-binding.sh",
    "skills/implementaudit/scripts/claim-run.sh",
    "skills/implementaudit/scripts/detect-env.sh",
    "skills/implementaudit/scripts/detect-stack.sh",
    "skills/implementaudit/scripts/repo-state.sh",
    "skills/implementaudit/scripts/summarize-repo.sh",
    "skills/implementaudit/scripts/validate-audit-spec.sh",
    "skills/implementaudit/scripts/validate-phase.sh",
    "skills/implementaudit/scripts/validate-run-root.sh",
    "skills/implementaudit/scripts/custody-append.sh",
    "skills/implementaudit/templates/ROADMAP.md",
    "skills/implementaudit/templates/STATE.md",
    "skills/implementaudit/templates/THINKING.md",
    "skills/implementaudit/templates/phase-goal.txt",
    "skills/implementaudit/templates/child-agent-report.md",
    "skills/implementaudit/templates/final-report.md",
    "skills/implementaudit/templates/read-only-plan.md",
    "skills/implementaudit/templates/PROTOCOL.md",
    "skills/implementaudit/templates/sidecars.md",
    "skills/implementaudit/templates/tools.md",
    "skills/implementaudit/templates/context.md",
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
    "references/continuity.md",
    "references/routing.md",
    "references/repo-state-comparison.md",
    "references/sidecars.md",
    "references/child-agents.md",
    "references/lean-operating-discipline.md",
    "references/audit-category-matrix.md",
    "references/audit-playbook.md",
    "references/plan-lifecycle.md",
    "references/terminology-integration.md",
    "references/convergence-mode.md",
    "scripts/check-evidence-anchor.sh",
    "scripts/check-lesson-lift.sh",
    "scripts/check-handoff-packet.sh",
    "scripts/check-closure-surface.sh",
    "scripts/check-authorization-binding.sh",
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
# Skill files: archive path strips skills/implementaudit/ so SKILL.md is at root.
# Plugin files are generated below because source metadata uses ./skills/ while
# the release archive intentionally flattens the skill payload to archive root.
entries = []

for child in sorted(source_skill_dir.rglob("*")):
    if child.is_file():
        archive_rel = child.relative_to(source_skill_dir)
        if blocked(archive_rel):
            raise SystemExit(f"blocked file selected for asset: {archive_rel.as_posix()}")
        entries.append((archive_rel, child))

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


def normalized_text_bytes(text: str) -> bytes:
    return text.replace("\r\n", "\n").encode("utf-8")


source_plugin = json.loads((repo / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
archive_plugin = dict(source_plugin)
archive_plugin["skills"] = "./"

source_marketplace = json.loads(
    (repo / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
)
archive_marketplace = json.loads(json.dumps(source_marketplace))
for plugin in archive_marketplace.get("plugins", []):
    if plugin.get("name") == "implementaudit":
        plugin.pop("source", None)
        plugin["path"] = ".."

generated_entries = [
    (
        Path(".claude-plugin/plugin.json"),
        normalized_text_bytes(json.dumps(archive_plugin, indent=2) + "\n"),
    ),
    (
        Path(".claude-plugin/marketplace.json"),
        normalized_text_bytes(json.dumps(archive_marketplace, indent=2) + "\n"),
    ),
]


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
    for archive_rel, data in generated_entries:
        info = zipfile.ZipInfo(archive_rel.as_posix())
        info.external_attr = (stat.S_IFREG | 0o644) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, data)

with zipfile.ZipFile(asset) as zf:
    names = set(zf.namelist())

    # Regression guard: skills/implementaudit/SKILL.md must NOT be in the archive.
    # The archive root must contain SKILL.md directly for Claude import.
    if "skills/implementaudit/SKILL.md" in names:
        raise SystemExit(
            "archive has skills/implementaudit/SKILL.md at nested path; SKILL.md must be at archive root"
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
        if name.endswith(".sh") and b"\r\n" in zf.read(name):
            raise SystemExit(
                f"shell script contains CRLF line endings in asset: {name}"
            )

    missing = [name for name in required_archive if name not in names]
    if missing:
        raise SystemExit(f"asset missing required files: {', '.join(missing)}")

    # Package parity: the archive must equal the manifest exactly. A file
    # under skills/ that is not in required_archive ships silently otherwise;
    # adding payload requires a deliberate manifest update here.
    extra = sorted(names - set(required_archive))
    if extra:
        raise SystemExit(
            "asset contains entries not in the required_archive manifest "
            "(update the manifest deliberately or remove the file): "
            + ", ".join(extra)
        )

    with tempfile.TemporaryDirectory() as tmp:
        zf.extractall(tmp)
        extracted = Path(tmp)
        plugin = json.loads((extracted / ".claude-plugin/plugin.json").read_text())
        marketplace = json.loads((extracted / ".claude-plugin/marketplace.json").read_text())
        if plugin.get("name") != "implementaudit":
            raise SystemExit("extracted plugin name must be implementaudit")
        if plugin.get("version") != "0.3.2":
            raise SystemExit("extracted plugin version must be 0.3.2")
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
