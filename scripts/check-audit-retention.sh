#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-audit-retention: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
retention_file="docs/audits/RETENTION.md"
stale_ref_file=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-root)
      [ "$#" -ge 2 ] || fail "--repo-root requires a directory"
      repo_root="$2"
      shift 2
      ;;
    --retention-file)
      [ "$#" -ge 2 ] || fail "--retention-file requires a path"
      retention_file="$2"
      shift 2
      ;;
    --stale-ref-file)
      [ "$#" -ge 2 ] || fail "--stale-ref-file requires a path"
      stale_ref_file="$2"
      shift 2
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

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

"${py_cmd[@]}" - "$retention_file" "$stale_ref_file" <<'PY'
import subprocess
import sys
from pathlib import Path

retention_file = Path(sys.argv[1])
stale_ref_file = Path(sys.argv[2]) if sys.argv[2] else None

root_allowed = {
    "INDEX.md",
    "RETENTION.md",
}


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing required file: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


retention_text = read(retention_file)
run_root_labels = [
    "historical",
    "non-current",
    "source-only",
    "source milestone",
    "gitignored",
    "custody",
    "orientation",
    "not proof",
    "not current",
    "validated",
    "validator",
    "run root",
    "runtime path",
    "template",
    "example",
    "fallback",
    "source repo",
]


def check_run_root_claims(path: Path, text: str) -> None:
    for lineno, line in enumerate(text.splitlines(), 1):
        if ".IMPLEMENTAUDIT/runs" not in line:
            continue
        lower = line.lower()
        if any(label in lower for label in run_root_labels):
            continue
        raise SystemExit(
            f"{path.as_posix()}:{lineno}: run-root proof claim must be labelled "
            "historical/non-current/validated/source-only: "
            + line.strip()[:160]
        )


check_run_root_claims(retention_file, retention_text)
for token in [
    "Active Root",
    "Archive",
    "Deletion Rule",
    "Generated And Local Evidence Boundary",
    ".IMPLEMENTAUDIT/",
    "dist/",
    "graphify-out/",
    "custody.db",
    "RC `.skill` files",
    "RC source evidence zip files",
    "plans/",
    "docs/maintenance/AGENTS-HISTORY.md",
    "baseline-first bootloader",
]:
    if token not in retention_text:
        raise SystemExit(f"{retention_file.as_posix()}: missing retention token: {token}")

root = Path("docs/audits")
archive = root / "archive"

for name in root_allowed:
    if not (root / name).is_file():
        raise SystemExit(f"docs/audits root missing required file: {name}")
for path in root.glob("*.md"):
    if path.name not in root_allowed:
        raise SystemExit(f"historical audit file remains in active root: {path.as_posix()}")

index_text = read(root / "INDEX.md")
check_run_root_claims(root / "INDEX.md", index_text)

archive_entries = []
fixture_dirs = []
if archive.is_dir():
    archive_entries = sorted(
        p for p in archive.rglob("*.md")
        if p.is_file() and "/fixtures/" not in p.as_posix()
    )
    fixture_dirs = sorted(
        {p.parent for p in archive.rglob("*") if p.is_file() and "/fixtures/" in p.as_posix()}
    )
    # Archive history is allowed when retained, but it is not a source-evidence
    # dependency. INDEX may summarize classes of archived evidence instead of
    # listing every historical file path.
    if archive_entries and "archive" not in index_text.lower():
        raise SystemExit("INDEX.md must summarize retained archive history when docs/audits/archive exists")

stale_refs = [f"docs/audits/{path.name}" for path in archive_entries]
stale_root_ref_patterns = [
    "docs/audits/v",
    "docs/audits/readme-audit_",
]
if stale_ref_file:
    text = read(stale_ref_file)
    check_run_root_claims(stale_ref_file, text)
    for stale in stale_root_ref_patterns:
        if stale in text and "docs/audits/archive/" not in text:
            raise SystemExit(f"{stale_ref_file.as_posix()}: stale active root audit reference: {stale}")
    for stale in stale_refs:
        if stale in text:
            raise SystemExit(f"{stale_ref_file.as_posix()}: stale active root audit reference: {stale}")
else:
    try:
        tracked_raw = subprocess.check_output(
            ["git", "ls-files", "-z"], text=False, stderr=subprocess.DEVNULL
        )
        tracked = [p.decode("utf-8") for p in tracked_raw.split(b"\0") if p]
    except Exception:
        tracked = [
            path.as_posix()
            for path in Path(".").rglob("*")
            if path.is_file() and ".git" not in path.parts
        ]
    forbidden_tracked = []
    for path in tracked:
        lowered = path.lower()
        name = Path(path).name.lower()
        if lowered.startswith((".implementaudit/", "dist/", "graphify-out/", ".graphify/", ".activegraph/", "plans/")):
            forbidden_tracked.append(path)
        if name == "custody.db" or name.endswith(".skill"):
            forbidden_tracked.append(path)
        if ("implementaudit-v0.3.1.0-rc" in name or "implementaudit-v0.3.2.0-rc" in name) and (name.endswith(".zip") or name.endswith(".checksums.txt") or name.endswith(".archive-list.txt")):
            forbidden_tracked.append(path)
        if "codex-exec-transcript" in name and not lowered.startswith("fixtures/"):
            forbidden_tracked.append(path)
    if forbidden_tracked:
        raise SystemExit("forbidden generated/local evidence tracked:\n" + "\n".join(sorted(set(forbidden_tracked))))

    active_files = []
    for path in tracked:
        if path.startswith("docs/audits/archive/"):
            continue
        if path == "docs/maintenance/AGENTS-HISTORY.md":
            continue
        if path == "CHANGELOG.md":
            continue
        if path.startswith("fixtures/audit-retention/"):
            continue
        if not any(
            path.startswith(prefix) or path == exact
            for prefix, exact in [
                ("docs/", ""),
                ("scripts/", ""),
                (".github/", ""),
                ("", "AGENTS.md"),
                ("", "README.md"),
                ("", "CHANGELOG.md"),
            ]
        ):
            continue
        p = Path(path)
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for stale in stale_refs:
            if stale in text:
                active_files.append(f"{path}: stale active root audit reference: {stale}")
        for stale in stale_root_ref_patterns:
            if stale in text and "docs/audits/archive/" not in text:
                active_files.append(f"{path}: stale active root audit reference: {stale}")
        if path.startswith("docs/audits/"):
            try:
                check_run_root_claims(p, text)
            except SystemExit as exc:
                active_files.append(str(exc))
    if active_files:
        raise SystemExit("\n".join(active_files))

sys.stdout.write("check-audit-retention: ok\n")
PY
