#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'check-skill-layout-contract: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-root)
      [ "$#" -ge 2 ] || fail "--repo-root requires a directory"
      repo_root="$2"
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

"${py_cmd[@]}" - <<'PY'
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path.cwd()


def require_file(path: str) -> None:
    if not (root / path).is_file():
        raise SystemExit(f"missing required file: {path}")


def require_dir(path: str) -> None:
    if not (root / path).is_dir():
        raise SystemExit(f"missing required directory: {path}")


for path in [
    "skills/implementaudit/SKILL.md",
    "skills/implementaudit/references",
    "skills/implementaudit/scripts",
    "skills/implementaudit/templates",
]:
    (require_dir if path.endswith(("references", "scripts", "templates")) else require_file)(path)

flat = root / "skills" / "SKILL.md"
if flat.exists():
    raise SystemExit("flat canonical source skill file must not exist: skills/SKILL.md")

if (root / ".git").exists():
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "skills/SKILL.md"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if tracked.returncode == 0:
        raise SystemExit("flat canonical source skill file must not be tracked: skills/SKILL.md")

skill_files = sorted(p.relative_to(root).as_posix() for p in (root / "skills").glob("*/SKILL.md"))
if skill_files != ["skills/implementaudit/SKILL.md"]:
    raise SystemExit(
        "expected exactly one name-matched source skill: "
        + ", ".join(skill_files or ["<none>"])
    )

plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
if plugin.get("name") != "implementaudit":
    raise SystemExit(".claude-plugin/plugin.json name must be implementaudit")
if plugin.get("skills") != "./skills/":
    raise SystemExit(
        ".claude-plugin/plugin.json must point source plugin discovery at ./skills/"
    )

marketplace = json.loads(
    (root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
)
plugins = marketplace.get("plugins")
if not isinstance(plugins, list) or not plugins:
    raise SystemExit(".claude-plugin/marketplace.json plugins list is required")
entry = plugins[0]
if entry.get("name") != "implementaudit":
    raise SystemExit("marketplace entry name must be implementaudit")
if entry.get("source") != "./":
    raise SystemExit("source marketplace entry must use source: ./")
if "path" in entry:
    raise SystemExit("source marketplace entry must not keep archive-only path: ..")

builder = (root / "scripts/build-release-asset.sh").read_text(encoding="utf-8")
for token in [
    'source_skill_dir = repo / "skills" / "implementaudit"',
    'archive_plugin["skills"] = "./"',
    'plugin["path"] = ".."',
    'if "skills/implementaudit/SKILL.md" in names:',
]:
    if token not in builder:
        raise SystemExit(f"scripts/build-release-asset.sh missing layout token: {token}")

skill_text = (root / "skills/implementaudit/SKILL.md").read_text(encoding="utf-8")
for token in [
    "Source checkout layout is conventional and name-matched",
    "skills/implementaudit/SKILL.md",
    "Release archives flatten that directory only as a build artifact",
    "references/routing.md",
    "scripts/claim-run.sh",
    "templates/PROTOCOL.md",
]:
    if token not in skill_text:
        raise SystemExit(f"skills/implementaudit/SKILL.md missing layout token: {token}")

for forbidden in [
    "skills/implementaudit/references/",
    "skills/implementaudit/scripts/",
    "skills/implementaudit/templates/",
]:
    if forbidden in skill_text:
        raise SystemExit(
            f"skills/implementaudit/SKILL.md must use installed-relative payload paths, not {forbidden}"
        )

docs = {
    "README.md": [
        "Source layout vs release archive layout",
        "skills/implementaudit/SKILL.md",
        "release archive",
        "SKILL.md at archive root",
    ],
    "AGENTS.md": [
        "skills/implementaudit/SKILL.md",
        "release archive",
        "archive root",
    ],
}
for path, tokens in docs.items():
    require_file(path)
    text = (root / path).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            raise SystemExit(f"{path} missing layout audit token: {token}")


def tree_entry(line: str) -> tuple[int, str] | None:
    markers = [pos for pos in (line.find("├"), line.find("└")) if pos >= 0]
    if not markers:
        return None
    marker = min(markers)
    rest = line[marker + 1 :].lstrip()
    if not rest.startswith("──"):
        return None
    name = rest[2:].strip().split(maxsplit=1)[0].strip("`")
    return marker, name


active_roots = [
    ".claude-plugin",
    ".github",
    "scripts",
    "tests",
    "docs/portal",
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
]
stale = re.compile(r"skills/(?:SKILL\.md|references/|scripts/|templates/)")
violations: list[str] = []
for item in active_roots:
    path = root / item
    candidates = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    for file in candidates:
        try:
            lines = file.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(lines, 1):
            if stale.search(line):
                lower = line.lower()
                if (
                    "must not" in lower
                    or "do not recreate" in lower
                    or "reject" in lower
                    or "flat canonical" in lower
                    or "ls-files" in lower
                    or file.name == "skill-layout-contract.test.sh"
                ):
                    continue
                violations.append(f"{file.relative_to(root).as_posix()}:{lineno}: {line.strip()}")
        if file.name != "skill-layout-contract.test.sh":
            for lineno, line in enumerate(lines, 1):
                entry = tree_entry(line)
                if entry is None:
                    continue
                root_indent, name = entry
                if name != "skills/":
                    continue
                entries: list[tuple[int, str]] = []
                for child in lines[lineno:]:
                    child_entry = tree_entry(child)
                    if child_entry is None:
                        continue
                    child_indent, child_name = child_entry
                    if child_indent <= root_indent:
                        break
                    entries.append((child_indent, child_name))
                child_indents = [indent for indent, _ in entries if indent > root_indent]
                if not child_indents:
                    continue
                direct_indent = min(child_indents)
                direct_children = {
                    child_name for indent, child_name in entries if indent == direct_indent
                }
                flat_payload_children = {
                    "SKILL.md",
                    "references/",
                    "scripts/",
                    "templates/",
                } & direct_children
                if flat_payload_children:
                    violations.append(
                        f"{file.relative_to(root).as_posix()}:{lineno}: "
                        "repo layout tree shows flat skill payload directly under skills/"
                    )

if violations:
    sys.stderr.write("\n".join(violations) + "\n")
    raise SystemExit("active source/checker/docs reference stale flat skill layout")

sys.stdout.write("check-skill-layout-contract: ok\n")
PY

# Payload path hygiene: the shipped payload must not contain user-home
# absolute paths (Windows C:\Users\<name>, macOS /Users/<name>, Linux
# /home/<name>). Placeholder forms like <user> or $HOME are permitted.
"${py_cmd[@]}" - <<'PY'
import re
import sys
from pathlib import Path

root = Path.cwd()
payload = root / "skills" / "implementaudit"
backslash = chr(92)
# One-or-more separators so JSON-escaped Windows paths (double backslash)
# and forward-slash Windows paths are both caught.
# Windows arm is case-insensitive: the OS is, so c:\users\ leaks identically.
# POSIX arm stays case-SENSITIVE: a case-insensitive /users/ would
# false-positive on URL paths such as api.github.com/users/<name>/.
sep = "[" + re.escape(backslash) + "/]+"
pattern = re.compile(
    "(?i:[A-Za-z]:" + sep + "Users" + sep + "[A-Za-z0-9_.-]+)"
    "|/(?:Users|home)/[A-Za-z0-9_.-]+/"
)
bad = []
for path in sorted(payload.rglob("*")):
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for lineno, line in enumerate(text.splitlines(), 1):
        match = pattern.search(line)
        if match:
            bad.append(f"{path.relative_to(root).as_posix()}:{lineno}: {match.group(0)}")
if bad:
    print("check-skill-layout-contract: user-home absolute path(s) in payload:", file=sys.stderr)
    for item in bad:
        print(f"  {item}", file=sys.stderr)
    raise SystemExit(1)
print("payload path hygiene: ok")
PY
