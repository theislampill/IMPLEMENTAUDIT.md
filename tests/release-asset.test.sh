#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp_parent="$(mktemp -d)"
stray_file="skills/implementaudit/zz-package-parity-stray-test.txt"
trap 'rm -rf "$tmp_parent"; rm -f "$stray_file"' EXIT

# Package parity: a stray file under skills/implementaudit/ must fail the build, because it
# would otherwise ship without a deliberate manifest update.
printf 'stray payload parity probe\n' > "$stray_file"
if bash scripts/build-release-asset.sh --check >/dev/null 2>&1; then
  printf 'release-asset.test: expected stray skills/implementaudit/ file to fail package parity\n' >&2
  exit 1
fi
rm -f "$stray_file"

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
    "references/sidecars.md",
    "references/child-agents.md",
    "references/lean-operating-discipline.md",
    "references/audit-category-matrix.md",
    "references/audit-playbook.md",
    "references/plan-lifecycle.md",
    "references/terminology-integration.md",
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

    # Regression guard: skills/implementaudit/SKILL.md must NOT be in the archive.
    # Claude import requires SKILL.md at archive root.
    if "skills/implementaudit/SKILL.md" in names:
        raise SystemExit(
            "REGRESSION: archive has skills/implementaudit/SKILL.md at nested path; "
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

    # Compression regression guard: every non-empty entry must be ZIP_DEFLATED.
    # ZipInfo defaults to compress_type=ZIP_STORED (0), which silently overrides
    # the ZipFile-level ZIP_DEFLATED default when writestr() receives a ZipInfo
    # object.  If build-release-asset.sh ever loses the explicit
    # `info.compress_type = zipfile.ZIP_DEFLATED` assignment, all entries revert
    # to stored and the asset bloats from ~60 KB to ~155 KB with no error raised.
    stored_entries = [
        info.filename
        for info in zf.infolist()
        if info.compress_type == zipfile.ZIP_STORED and info.file_size > 0
    ]
    if stored_entries:
        sample = ", ".join(stored_entries[:5])
        tail = " ..." if len(stored_entries) > 5 else ""
        raise SystemExit(
            f"compression regression: {len(stored_entries)} non-empty entries are "
            "ZIP_STORED (uncompressed). build-release-asset.sh must set "
            "info.compress_type = zipfile.ZIP_DEFLATED on each ZipInfo before "
            f"calling writestr(). Stored: {sample}{tail}"
        )

    # Total asset size guard: uncompressed asset is ~155 KB; properly deflated
    # is ~60 KB for the current payload.  120 KB provides ~2x headroom for
    # legitimate payload growth while still catching accidental ZIP_STORED
    # regressions.  Update this threshold only after confirming entries remain
    # ZIP_DEFLATED (the check above) and the payload growth is intentional.
    asset_bytes = asset.stat().st_size
    MAX_ASSET_BYTES = 120_000
    if asset_bytes > MAX_ASSET_BYTES:
        raise SystemExit(
            f"asset size {asset_bytes:,} bytes exceeds the {MAX_ASSET_BYTES:,}-byte "
            "threshold. Verify ZIP_DEFLATED compression is applied (the check above), "
            "then update MAX_ASSET_BYTES in tests/release-asset.test.sh if the payload "
            "growth is intentional."
        )

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
        if plugin.get("version") != "0.3.1":
            raise SystemExit("expected plugin version 0.3.1")
        if plugin.get("skills") != "./":
            raise SystemExit(
                "expected plugin skills path ./ "
                "(SKILL.md at archive root for Claude import)"
            )
        if (root / "IMPLEMENTAUDIT.md").exists():
            raise SystemExit("root IMPLEMENTAUDIT.md must not be included")

print("release-asset.test: ok")
PY
