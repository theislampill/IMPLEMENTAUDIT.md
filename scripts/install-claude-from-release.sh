#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'install-claude-from-release: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  scripts/install-claude-from-release.sh --asset PATH --claude-skills-dir PATH [--checksum PATH] [--allow-downgrade]
  scripts/install-claude-from-release.sh --url URL --claude-skills-dir PATH [--checksum-url URL] [--allow-downgrade]
  scripts/install-claude-from-release.sh --tag vX.Y.Z.W --claude-skills-dir PATH [--repo OWNER/REPO] [--allow-downgrade]

FILE-COPY WORKAROUND — NOT Claude import proof.

This script copies IMPLEMENTAUDIT.skill payload files into a Claude session skill
directory by extracting the archive and copying files directly. It bypasses
Claude Desktop's normal skill import/install path and does NOT constitute proof
that Claude Desktop can import the .skill file.

To test actual Claude import, use Claude Desktop's built-in skill import/install UI.

Finding the Claude skills directory:
  Claude Desktop stores session-managed skills under a session-specific path.
  On Windows:   %APPDATA%\Claude\local-agent-mode-sessions\skills-plugin\
  On macOS:     ~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/
  On Linux:     ~/.config/Claude/local-agent-mode-sessions/skills-plugin/

  Under that root, look for a subtree containing skills/implementaudit/.
  Pass the full path to the implementaudit skill directory as --claude-skills-dir.

  Example (Windows):
    --claude-skills-dir "%APPDATA%\Claude\local-agent-mode-sessions\skills-plugin\<id>\<id>\skills\implementaudit"

This script does not prove marketplace behavior, passive auto-update,
Claude Desktop import, or Claude runtime loading.
No import proof is made by this script.
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
allow_downgrade="0"

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
    --allow-downgrade)
      allow_downgrade="1"
      shift
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

bash scripts/check-package-contract.sh --verify-artifact \
  standalone_compatibility "$asset"

"${py_cmd[@]}" - "$asset" "$checksum" "$claude_skills_dir" "$allow_downgrade" <<'PY'
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

asset = Path(sys.argv[1]).expanduser()
checksum = Path(sys.argv[2]).expanduser() if sys.argv[2] else None
target_dir = Path(sys.argv[3]).expanduser()
allow_downgrade = sys.argv[4] == "1"

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


def numeric_version(value):
    text = str(value)
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", text):
        raise SystemExit(f"runtime version is not numeric dotted form: {text!r}")
    return tuple(int(part) for part in text.split("."))


def read_installed_standalone(root):
    if root.is_symlink() or not root.is_dir():
        raise SystemExit("installed standalone target must be a real directory")
    try:
        package = json.loads(
            (root / "IMPLEMENTAUDIT_PACKAGE.json").read_text(encoding="utf-8")
        )
        inventory = json.loads(
            (root / "IMPLEMENTAUDIT_INVENTORY.json").read_text(encoding="utf-8")
        )
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise SystemExit(f"installed standalone identity is missing or malformed: {exc}") from exc
    if inventory.get("schema") != "implementaudit.package-inventory.v1":
        raise SystemExit("installed standalone inventory schema is invalid")
    if inventory.get("artifact_role") != "standalone_compatibility":
        raise SystemExit("installed target is not the standalone compatibility role")
    if package.get("package_name") != "implementaudit":
        raise SystemExit("installed standalone package name is invalid")
    if package.get("public_governor") != "implementaudit":
        raise SystemExit("installed standalone public governor is invalid")
    if package.get("required_skills") != expected_required:
        raise SystemExit("installed standalone required skill population is invalid")
    if package.get("internal_skills") != expected_internal:
        raise SystemExit("installed standalone internal skill population is invalid")
    for field in (
        "package_name", "runtime_version", "release_family", "public_governor",
        "required_skills", "internal_skills",
    ):
        if inventory.get(field) != package.get(field):
            raise SystemExit(f"installed standalone package/inventory disagree on {field}")
    source = inventory.get("source")
    if not isinstance(source, dict) or set(source) != {"commit", "tree", "worktree_state"}:
        raise SystemExit("installed standalone source binding is incomplete")
    if not re.fullmatch(r"[0-9a-f]{40}", str(source["commit"])) or not re.fullmatch(
        r"[0-9a-f]{40}", str(source["tree"])
    ):
        raise SystemExit("installed standalone source identity is malformed")
    if source["worktree_state"] not in {"clean", "dirty"}:
        raise SystemExit("installed standalone source state is invalid")
    members = inventory.get("members")
    if not isinstance(members, list):
        raise SystemExit("installed standalone inventory members must be a list")
    expected_paths = {"IMPLEMENTAUDIT_INVENTORY.json"}
    for member in members:
        if not isinstance(member, dict) or set(member) != {"path", "bytes", "sha256"}:
            raise SystemExit("installed standalone inventory member shape is invalid")
        relative = PurePosixPath(str(member["path"]))
        if relative.is_absolute() or ".." in relative.parts or "\\" in str(member["path"]):
            raise SystemExit(f"unsafe installed standalone inventory path: {relative}")
        expected_paths.add(relative.as_posix())
        path = root.joinpath(*relative.parts)
        if path.is_symlink() or not path.is_file():
            raise SystemExit(f"installed standalone member missing or non-regular: {relative}")
        data = path.read_bytes()
        if len(data) != member["bytes"] or hashlib.sha256(data).hexdigest() != member["sha256"]:
            raise SystemExit(f"installed standalone member identity mismatch: {relative}")
    observed_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    if observed_paths != expected_paths:
        extra = sorted(observed_paths - expected_paths)
        missing = sorted(expected_paths - observed_paths)
        raise SystemExit(
            f"installed standalone population mismatch: missing={missing} extra={extra}"
        )
    return package, inventory

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
    "scripts/resolve-internal-skill.py",
    "scripts/summarize-repo.sh",
    "scripts/validate-audit-spec.sh",
    "scripts/validate-phase.sh",
    "scripts/validate-run-root.sh",
    "scripts/custody-append.sh",
    "scripts/lane-survivor-inventory.sh",
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
    "IMPLEMENTAUDIT_PACKAGE.json",
    "IMPLEMENTAUDIT_INVENTORY.json",
    "internal-procedures/audit-state.md",
    "internal-procedures/audit-assess.md",
    "internal-procedures/audit-implement.md",
    "internal-procedures/audit-andon.md",
}

with zipfile.ZipFile(asset) as zf:
    name_list = zf.namelist()
    names = set(name_list)
    if len(name_list) != len(names):
        raise SystemExit("archive contains duplicate member paths")

    # Regression guard: wrong-shape archive must be rejected.
    if "skills/implementaudit/SKILL.md" in names:
        raise SystemExit(
            "archive has skills/implementaudit/SKILL.md at nested path; "
            "SKILL.md must be at archive root. "
            "This archive cannot be imported by Claude Desktop."
        )

    missing = sorted(required_archive - names)
    if missing:
        raise SystemExit("asset missing required entries: " + ", ".join(missing))

    # Only allowed top-level entries may appear.
    allowed_top_level = {
        "SKILL.md", "references", "scripts", "templates", "internal-procedures",
        "IMPLEMENTAUDIT_PACKAGE.json", "IMPLEMENTAUDIT_INVENTORY.json",
    }
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
        package = json.loads((root / "IMPLEMENTAUDIT_PACKAGE.json").read_text(encoding="utf-8"))
        inventory = json.loads((root / "IMPLEMENTAUDIT_INVENTORY.json").read_text(encoding="utf-8"))
        expected_required = ["implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon"]
        expected_internal = [
            {"name": "audit-state", "maintainer_only": False, "directly_invocable": False},
            {"name": "audit-assess", "maintainer_only": False, "directly_invocable": False},
            {"name": "audit-implement", "maintainer_only": True, "directly_invocable": False},
            {"name": "audit-andon", "maintainer_only": False, "directly_invocable": True},
        ]
        if package.get("package_name") != "implementaudit":
            raise SystemExit("package name must be implementaudit")
        if package.get("public_governor") != "implementaudit":
            raise SystemExit("standalone public governor must be implementaudit")
        if package.get("required_skills") != expected_required:
            raise SystemExit("standalone package must bind the exact five-skill population")
        if package.get("internal_skills") != expected_internal:
            raise SystemExit("standalone package must bind the exact four-child population")
        if inventory.get("artifact_role") != "standalone_compatibility":
            raise SystemExit("standalone inventory role is invalid")
        for field in (
            "package_name", "runtime_version", "release_family", "public_governor",
            "required_skills", "internal_skills",
        ):
            if inventory.get(field) != package.get(field):
                raise SystemExit(f"standalone package/inventory disagree on {field}")
        members = inventory.get("members")
        if not isinstance(members, list):
            raise SystemExit("standalone inventory members must be a list")
        expected_paths = {"IMPLEMENTAUDIT_INVENTORY.json"}
        for member in members:
            if not isinstance(member, dict) or set(member) != {"path", "bytes", "sha256"}:
                raise SystemExit("standalone inventory member shape is invalid")
            relative = PurePosixPath(str(member["path"]))
            if relative.is_absolute() or ".." in relative.parts or "\\" in str(member["path"]):
                raise SystemExit(f"unsafe standalone inventory path: {relative}")
            expected_paths.add(relative.as_posix())
            data = root.joinpath(*relative.parts).read_bytes()
            if len(data) != member["bytes"] or hashlib.sha256(data).hexdigest() != member["sha256"]:
                raise SystemExit(f"standalone inventory member identity mismatch: {relative}")
        if names != expected_paths:
            raise SystemExit("standalone archive population differs from exact inventory")
        if (root / "IMPLEMENTAUDIT.md").exists():
            raise SystemExit("root IMPLEMENTAUDIT.md must be absent")
        if not (root / "SKILL.md").is_file():
            raise SystemExit("SKILL.md must be at archive root")
        if (root / "skills").exists():
            raise SystemExit(
                "skills/ subdirectory must not exist at archive root; "
                "this archive is malformed for Claude import"
            )
        procedure_names = sorted(
            path.relative_to(root).as_posix()
            for path in (root / "internal-procedures").glob("*.md")
            if path.is_file()
        )
        expected_procedures = sorted(
            f"internal-procedures/{name}.md" for name in expected_required[1:]
        )
        if procedure_names != expected_procedures:
            raise SystemExit("standalone internal procedure population is not exact")
        for procedure in procedure_names:
            if (root / procedure).read_bytes().startswith(b"---\n"):
                raise SystemExit("standalone internal procedure retains discoverable skill frontmatter")
        skill_documents = [path for path in root.rglob("SKILL.md") if path.is_file()]
        if skill_documents != [root / "SKILL.md"]:
            raise SystemExit("standalone projection must expose only the governor SKILL.md")

        if target_dir.parent.name == "skills":
            plugin_target = target_dir.parent.parent / "plugins" / "implementaudit"
            if plugin_target.exists() or plugin_target.is_symlink():
                raise SystemExit("ambiguous same-identity plugin and standalone co-install is forbidden")

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        stage = target_dir.parent / f".implementaudit-stage-{os.getpid()}"
        backup = target_dir.parent / f".implementaudit-backup-{os.getpid()}"
        for transient in (stage, backup):
            if transient.exists() or transient.is_symlink():
                raise SystemExit(f"stale standalone install transaction path exists: {transient.name}")

        idempotent = False
        if target_dir.exists() or target_dir.is_symlink():
            prior_package, _prior_inventory = read_installed_standalone(target_dir)
            prior_version = numeric_version(prior_package.get("runtime_version"))
            next_version = numeric_version(package.get("runtime_version"))
            prior_digest = hashlib.sha256(
                (target_dir / "IMPLEMENTAUDIT_INVENTORY.json").read_bytes()
            ).hexdigest()
            incoming_digest = hashlib.sha256(
                (root / "IMPLEMENTAUDIT_INVENTORY.json").read_bytes()
            ).hexdigest()
            if prior_digest == incoming_digest:
                idempotent = True
            elif prior_version == next_version:
                raise SystemExit(
                    "same-version standalone source/package identity differs "
                    "from the installed predecessor"
                )
            elif prior_version > next_version and not allow_downgrade:
                raise SystemExit(
                    f"unauthorized downgrade rejected: {prior_package.get('runtime_version')} "
                    f"-> {package.get('runtime_version')}"
                )

        required_installed = [
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
            "scripts/resolve-internal-skill.py",
            "scripts/summarize-repo.sh",
            "scripts/validate-audit-spec.sh",
            "scripts/validate-phase.sh",
            "scripts/validate-run-root.sh",
            "scripts/custody-append.sh",
            "scripts/lane-survivor-inventory.sh",
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
            "internal-procedures/audit-state.md",
            "internal-procedures/audit-assess.md",
            "internal-procedures/audit-implement.md",
            "internal-procedures/audit-andon.md",
        ]

        if not idempotent:
            fault = os.environ.get("IMPLEMENTAUDIT_CLAUDE_INSTALL_FAULT", "")
            if fault not in {
                "", "remove-staged-member", "before-swap", "during-swap", "post-readback",
            }:
                raise SystemExit(f"unknown standalone install fault injection: {fault}")

            moved_predecessor = False
            installed_new = False
            try:
                stage.mkdir()
                # Copy the standalone projection including package identity/inventory.
                for child in root.iterdir():
                    dest = stage / child.name
                    if child.is_file():
                        shutil.copy2(child, dest)
                    elif child.is_dir():
                        shutil.copytree(child, dest)

                if fault == "remove-staged-member":
                    (stage / "SKILL.md").unlink()
                staged_package, staged_inventory = read_installed_standalone(stage)
                if staged_package != package or staged_inventory != inventory:
                    raise SystemExit("staged standalone package/inventory readback mismatch")
                for rel in required_installed:
                    if not (stage / rel).is_file():
                        raise SystemExit(f"staging skill missing required file: {rel}")
                if fault == "before-swap":
                    raise SystemExit("injected standalone before-swap failure")
                if target_dir.exists() or target_dir.is_symlink():
                    target_dir.rename(backup)
                    moved_predecessor = True
                if fault == "during-swap":
                    raise SystemExit("injected standalone during-swap failure")
                stage.rename(target_dir)
                installed_new = True
                installed_package, installed_inventory = read_installed_standalone(target_dir)
                if installed_package != package or installed_inventory != inventory:
                    raise SystemExit("post-swap standalone package/inventory readback mismatch")
                if fault == "post-readback":
                    raise SystemExit("injected standalone post-readback failure")
            except BaseException:
                if installed_new and (target_dir.exists() or target_dir.is_symlink()):
                    shutil.rmtree(target_dir)
                if moved_predecessor and backup.exists():
                    backup.rename(target_dir)
                if stage.exists():
                    shutil.rmtree(stage)
                raise
            if backup.exists():
                shutil.rmtree(backup)

sys.stdout.write("install-claude-from-release: FILE-COPY WORKAROUND.\n")
if idempotent:
    sys.stdout.write(
        f"install-claude-from-release: exact package already present in {target_dir}\n"
    )
else:
    sys.stdout.write(f"install-claude-from-release: copied {asset.name} files into {target_dir}\n")
sys.stdout.write(f"install-claude-from-release: sha256 {digest}\n")
sys.stdout.write(
    "install-claude-from-release: NOTICE: This is a file-copy workaround only.\n"
)
sys.stdout.write(
    "install-claude-from-release: NOTICE: It is NOT proof that Claude Desktop can import the .skill.\n"
)
sys.stdout.write(
    "install-claude-from-release: NOTICE: To test actual import, use Claude Desktop import UI.\n"
)
sys.stdout.write(
    "install-claude-from-release: NOTICE: After file-copy, restart Claude Desktop to reload.\n"
)
PY
