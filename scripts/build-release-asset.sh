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

check_release_identity() {
  local mode="${1:-}" previous_version="${2:-}" release_commit="${3:-}" check_root="${4:-$repo_root}"
  local candidate_asset="${5:-$check_root/$asset_name}"
  [ -n "$mode" ] && [ -n "$previous_version" ] && [ -n "$release_commit" ] \
    || fail "--check-release-identity requires <forward|republish> <previous-version> <release-commit> [repo-root] [candidate-asset]"
  "${py_cmd[@]}" - "$mode" "$previous_version" "$release_commit" "$check_root" "$candidate_asset" <<'PY'
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

mode, previous_version, release_commit, root_arg, candidate_arg = sys.argv[1:]
root = Path(root_arg).resolve()
if mode not in {"forward", "republish"}:
    raise SystemExit("prospective release identity mode must be forward or republish")

plugin_path = root / ".claude-plugin" / "plugin.json"
skill_path = root / "skills" / "implementaudit" / "SKILL.md"
changelog_path = root / "CHANGELOG.md"
for path in (plugin_path, skill_path, changelog_path):
    if not path.is_file():
        raise SystemExit(f"release identity owner is missing: {path}")

plugin_version = str(json.loads(plugin_path.read_text(encoding="utf-8")).get("version", "")).strip()
skill_text = skill_path.read_text(encoding="utf-8")
match = re.search(r'(?m)^\s+version:\s*["\']?([^"\'\n]+)["\']?\s*$', skill_text)
if not match:
    raise SystemExit("SKILL.md metadata.version is missing")
skill_version = match.group(1).strip()
if not plugin_version or plugin_version != skill_version:
    raise SystemExit(
        f"release identity version owners disagree: plugin={plugin_version!r} skill={skill_version!r}"
    )
if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", plugin_version):
    raise SystemExit("release identity version must use three numeric components")


def normalized_heading(value: str) -> str:
    parts = value.split(".")
    if len(parts) == 4 and parts[-1] == "0":
        parts = parts[:-1]
    return ".".join(parts)


headings = [
    normalized_heading(value)
    for value in re.findall(
        r"(?m)^## \[v?([0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?)(?: [^\]]+)?\]",
        changelog_path.read_text(encoding="utf-8"),
    )
]
distinct_headings = list(dict.fromkeys(headings))
if not distinct_headings:
    raise SystemExit("CHANGELOG.md has no published version heading")
if mode == "forward":
    candidates = [value for value in distinct_headings if value != plugin_version]
    authoritative_previous = candidates[0] if candidates else ""
else:
    authoritative_previous = distinct_headings[0]
if previous_version != authoritative_previous:
    raise SystemExit(
        f"declared previous version {previous_version!r} != CHANGELOG authority {authoritative_previous!r}"
    )

resolved = subprocess.run(
    ["git", "-C", str(root), "rev-parse", "--verify", f"{release_commit}^{{commit}}"],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
if resolved.returncode != 0:
    raise SystemExit("release identity commit does not resolve")
commit_sha = resolved.stdout.strip()
commit_tree = subprocess.run(
    ["git", "-C", str(root), "rev-parse", f"{commit_sha}^{{tree}}"],
    check=True,
    text=True,
    stdout=subprocess.PIPE,
).stdout.strip()
head_tree = subprocess.run(
    ["git", "-C", str(root), "rev-parse", "HEAD^{tree}"],
    check=True,
    text=True,
    stdout=subprocess.PIPE,
).stdout.strip()
ancestor = subprocess.run(
    ["git", "-C", str(root), "merge-base", "--is-ancestor", commit_sha, "HEAD"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
if ancestor.returncode != 0:
    raise SystemExit("release identity commit must be an ancestor of current HEAD")
if commit_tree != head_tree:
    raise SystemExit("release identity commit tree must equal current HEAD tree")

if mode == "forward":
    if plugin_version == previous_version:
        raise SystemExit("forward release must change the prior published version")
    print(f"build-release-asset: release identity forward {previous_version} -> {plugin_version} at {commit_sha}")
    raise SystemExit(0)

if plugin_version != previous_version:
    raise SystemExit("same-version republication must retain the prior published version")

candidate_path = Path(candidate_arg)
if not candidate_path.is_absolute():
    candidate_path = root / candidate_path
if candidate_path.name != "IMPLEMENTAUDIT.skill":
    raise SystemExit("same-version republication candidate must be named IMPLEMENTAUDIT.skill")
if candidate_path.is_symlink() or not candidate_path.is_file():
    raise SystemExit("same-version republication candidate must be a regular non-symlink file")
candidate_digest = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
candidate_bytes = candidate_path.stat().st_size

shown = subprocess.run(
    ["git", "-C", str(root), "show", "--format=", "--unified=0", commit_sha, "--", "CHANGELOG.md"],
    encoding="utf-8",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
if shown.returncode != 0:
    raise SystemExit("release identity CHANGELOG commit cannot be inspected")
added = "\n".join(
    line[1:]
    for line in shown.stdout.splitlines()
    if line.startswith("+") and not line.startswith("+++")
)
pairs = re.findall(
    r"(?ims)^[ \t]*-\s+`IMPLEMENTAUDIT\.skill`:\s+superseded\s+"
    r"`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*(?:→|->)\s*"
    r"superseding\s+`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*\.?\s*$",
    added,
)
if len(pairs) != 1:
    raise SystemExit("same-version republication commit must add exactly one IMPLEMENTAUDIT.skill digest-and-byte pair")
superseded_digest, _, superseding_digest, superseding_bytes_text = pairs[0]
if superseded_digest == superseding_digest:
    raise SystemExit("same-version republication digest pair must name distinct payloads")
superseding_bytes = int(superseding_bytes_text.replace(",", ""))
if superseding_digest != candidate_digest or superseding_bytes != candidate_bytes:
    raise SystemExit(
        "same-version republication record does not match the built IMPLEMENTAUDIT.skill digest and byte count"
    )
print(f"build-release-asset: release identity {mode} {plugin_version} at {commit_sha}")
PY
}

check_historical_release_record() {
  local check_root="${1:-$repo_root}"
  "${py_cmd[@]}" - "$check_root" <<'PY'
import re
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
changelog = root / "CHANGELOG.md"
if not changelog.is_file():
    raise SystemExit(f"historical release record owner is missing: {changelog}")

marker = "This entry is the one retroactive application"
text = changelog.read_text(encoding="utf-8")
if text.count(marker) != 1:
    raise SystemExit("historical #96 marker must occur exactly once")
marker_commit = subprocess.run(
    ["git", "-C", str(root), "log", "-1", "--format=%H", "-S", marker, "--", "CHANGELOG.md"],
    check=True,
    text=True,
    stdout=subprocess.PIPE,
).stdout.strip()
expected_commit = "4df5c0067d97fa20e86c98df5569a5314b6ec66c"
if marker_commit != expected_commit:
    raise SystemExit("historical #96 marker does not resolve to its pinned commit")
shown = subprocess.run(
    ["git", "-C", str(root), "show", f"{marker_commit}:CHANGELOG.md"],
    check=True,
    encoding="utf-8",
    stdout=subprocess.PIPE,
).stdout
pair = re.search(
    r"(?ims)^[ \t]*-\s+`IMPLEMENTAUDIT\.skill`:\s+superseded\s+"
    r"`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*(?:→|->)\s*"
    r"superseding\s+`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)",
    shown,
)
expected = (
    "a04165198a208ecc231d769783400c4610c58dbd0ca338682be481d7515319f4",
    "131,329",
    "884ab409842b863b003e9d405972f33ba71d194f77572738002a42e73d1b6b14",
    "132,117",
)
if pair is None or pair.groups() != expected:
    raise SystemExit("historical #96 IMPLEMENTAUDIT.skill identity record does not match its pinned evidence")
print(f"build-release-asset: nonqualifying historical #96 record ok at {marker_commit}")
PY
}

check_stale_artifact() {
  local surface="${1:-}" artifact="${2:-}" changelog="${3:-}"
  [ -n "$surface" ] && [ -n "$artifact" ] && [ -n "$changelog" ] \
    || fail "--check-stale-artifact requires <source|package|release> <artifact> <changelog>"
  case "$surface" in
    source) printf 'build-release-asset: source surface adds no stale package-artifact obligation\n'; return 0 ;;
    package|release) : ;;
    *) fail "stale artifact surface must be source, package, or release" ;;
  esac
  [ -e "$artifact" ] || return 0
  [ -f "$artifact" ] && [ ! -L "$artifact" ] || fail "stale artifact target must be a regular non-symlink file"
  [ -f "$changelog" ] && [ ! -L "$changelog" ] || fail "stale artifact CHANGELOG must be a regular non-symlink file"
  "${py_cmd[@]}" - "$artifact" "$changelog" <<'PY'
import hashlib
import re
import sys
from pathlib import Path

artifact = Path(sys.argv[1])
changelog = Path(sys.argv[2])
digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
text = changelog.read_text(encoding="utf-8")
superseded = set(re.findall(r"(?is)\bsuperseded\b\s+`?([0-9a-f]{64})`?", text))
if digest in superseded:
    raise SystemExit(
        f"ignored build artifact matches withdrawn/superseded publication digest {digest}; remove, rename, or rebuild it"
    )
print(f"build-release-asset: ignored build artifact is not superseded ({digest})")
PY
}

case "${1:-}" in
  --check-release-identity)
    shift
    check_release_identity "$@"
    exit $?
    ;;
  --check-historical-release-record)
    shift
    check_historical_release_record "$@"
    exit $?
    ;;
  --check-stale-artifact)
    shift
    check_stale_artifact "$@"
    exit $?
    ;;
esac

if [ "${1:-}" = "--check" ]; then
  check_stale_artifact package "$repo_root/dist/$asset_name" "$repo_root/CHANGELOG.md"
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
import os
import stat
import sys
import tempfile
import time
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
    "skills/implementaudit/scripts/check-duplication-parity.sh",
    "skills/implementaudit/scripts/check-respec-impact-set.sh",
    "skills/implementaudit/scripts/check-lesson-lift.sh",
    "skills/implementaudit/scripts/check-handoff-packet.sh",
    "skills/implementaudit/scripts/check-closure-surface.sh",
    "skills/implementaudit/scripts/check-authorization-binding.sh",
    "skills/implementaudit/scripts/claim-run.sh",
    "skills/implementaudit/scripts/detect-env.sh",
    "skills/implementaudit/scripts/detect-stack.sh",
    "skills/implementaudit/scripts/map-pin-chain.sh",
    "skills/implementaudit/scripts/repo-state.sh",
    "skills/implementaudit/scripts/summarize-repo.sh",
    "skills/implementaudit/scripts/validate-audit-spec.sh",
    "skills/implementaudit/scripts/validate-phase.sh",
    "skills/implementaudit/scripts/validate-run-root.sh",
    "skills/implementaudit/scripts/custody-append.sh",
    "skills/implementaudit/scripts/lane-survivor-inventory.sh",
    "skills/implementaudit/templates/ROADMAP.md",
    "skills/implementaudit/templates/STATE.md",
    "skills/implementaudit/templates/THINKING.md",
    "skills/implementaudit/templates/phase-goal.txt",
    "skills/implementaudit/templates/child-agent-report.md",
    "skills/implementaudit/templates/final-report.md",
    "skills/implementaudit/templates/read-only-plan.md",
    "skills/implementaudit/templates/PROTOCOL.md",
    "skills/implementaudit/templates/respec-impact-set.md",
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
    "scripts/check-duplication-parity.sh",
    "scripts/check-respec-impact-set.sh",
    "scripts/check-lesson-lift.sh",
    "scripts/check-handoff-packet.sh",
    "scripts/check-closure-surface.sh",
    "scripts/check-authorization-binding.sh",
    "scripts/claim-run.sh",
    "scripts/detect-env.sh",
    "scripts/detect-stack.sh",
    "scripts/map-pin-chain.sh",
    "scripts/repo-state.sh",
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
    "templates/respec-impact-set.md",
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


# ZIP metadata is part of the public asset identity. Pin every field that can
# vary by checkout host, locale, timezone, umask, or directory traversal. The
# default is the earliest ZIP timestamp; release jobs may supply another fixed
# SOURCE_DATE_EPOCH, which is always interpreted as UTC.
try:
    source_date_epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "315532800"))
except ValueError as exc:
    raise SystemExit("SOURCE_DATE_EPOCH must be an integer") from exc
archive_timestamp = time.gmtime(source_date_epoch)[:6]
if not 1980 <= archive_timestamp[0] <= 2107:
    raise SystemExit("SOURCE_DATE_EPOCH is outside the ZIP timestamp range")


def zip_info(archive_rel: Path, mode: int) -> zipfile.ZipInfo:
    """Return platform-independent metadata for one regular-file entry."""
    info = zipfile.ZipInfo(
        archive_rel.as_posix(), date_time=archive_timestamp)
    info.create_system = 3          # Unix, regardless of build host.
    info.create_version = 20        # ZIP 2.0 / DEFLATE.
    info.extract_version = 20
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.internal_attr = 0
    info.compress_type = zipfile.ZIP_DEFLATED
    info.flag_bits = 0
    info.extra = b""
    info.comment = b""
    return info


# Materialize bytes before writing and sort the COMPLETE archive, including
# generated metadata entries, by the portable archive path. pathlib.Path sort
# order is host-dependent because native separators differ.
payload_entries = [
    (archive_rel, read_normalized(src_path),
     0o755 if archive_rel.as_posix().startswith("scripts/") else 0o644)
    for archive_rel, src_path in deduped
]
payload_entries.extend(
    (archive_rel, data, 0o644) for archive_rel, data in generated_entries)
payload_entries.sort(key=lambda item: item[0].as_posix())


asset.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(
        asset, "w", compression=zipfile.ZIP_DEFLATED,
        compresslevel=9, strict_timestamps=True) as zf:
    for archive_rel, data, mode in payload_entries:
        info = zip_info(archive_rel, mode)
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
