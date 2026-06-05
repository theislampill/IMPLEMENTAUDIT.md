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

include_roots = [
    Path("skills"),
    Path("docs/diagrams"),
    Path("docs/audits"),
    Path(".claude-plugin/plugin.json"),
    Path(".claude-plugin/marketplace.json"),
    Path("IMPLEMENTAUDIT.md"),
    Path("README.md"),
    Path("CHANGELOG.md"),
]

required_files = [
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
    "docs/diagrams/tooling-architecture.mmd",
    "docs/diagrams/invocation-modes.mmd",
    "docs/diagrams/execution-spine.mmd",
    "docs/audits/INDEX.md",
    "IMPLEMENTAUDIT.md",
    "README.md",
    "CHANGELOG.md",
]

for rel in required_files:
    if not (repo / rel).is_file():
        raise SystemExit(f"missing required asset input: {rel}")

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
blocked_suffixes = (".log", ".tmp", ".activegraph.db")


def blocked(rel: Path) -> bool:
    text = rel.as_posix()
    if any(part in blocked_parts for part in rel.parts):
        return True
    if text.startswith(".env"):
        return True
    return text.endswith(blocked_suffixes)


def iter_files(root: Path):
    path = repo / root
    if path.is_file():
        yield root
        return
    for child in sorted(path.rglob("*")):
        if child.is_file():
            yield child.relative_to(repo)


entries = []
for root in include_roots:
    for rel in iter_files(root):
        if blocked(rel):
            raise SystemExit(f"blocked file selected for asset: {rel.as_posix()}")
        entries.append(rel)

seen = set()
deduped = []
for rel in entries:
    key = rel.as_posix()
    if key not in seen:
        seen.add(key)
        deduped.append(rel)

asset.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(asset, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for rel in deduped:
        info = zipfile.ZipInfo(rel.as_posix())
        mode = 0o755 if rel.as_posix().startswith("skills/scripts/") else 0o644
        info.external_attr = (stat.S_IFREG | mode) << 16
        zf.writestr(info, (repo / rel).read_bytes())

with zipfile.ZipFile(asset) as zf:
    names = zf.namelist()
    for name in names:
        rel = Path(name)
        if blocked(rel):
            raise SystemExit(f"blocked file found in asset: {name}")
    missing = [name for name in required_files if name not in names]
    if missing:
        raise SystemExit(f"asset missing required files: {', '.join(missing)}")

    with tempfile.TemporaryDirectory() as tmp:
        zf.extractall(tmp)
        extracted = Path(tmp)
        plugin = json.loads((extracted / ".claude-plugin/plugin.json").read_text())
        marketplace = json.loads((extracted / ".claude-plugin/marketplace.json").read_text())
        if plugin.get("name") != "implementaudit":
            raise SystemExit("extracted plugin name must be implementaudit")
        if plugin.get("version") != "0.2.2":
            raise SystemExit("extracted plugin version must be 0.2.2")
        if plugin.get("skills") != "./skills/":
            raise SystemExit("extracted plugin skills path must be ./skills/")
        if not marketplace.get("plugins"):
            raise SystemExit("extracted marketplace plugins list is required")
        if (extracted / "IMPLEMENTAUDIT.md").read_bytes() != (extracted / "skills/SKILL.md").read_bytes():
            raise SystemExit("extracted IMPLEMENTAUDIT.md and skills/SKILL.md are out of sync")

print(f"build-release-asset: wrote {asset}")
print("build-release-asset: extraction validation ok")
PY
