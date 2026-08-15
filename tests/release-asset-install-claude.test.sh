#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'release-asset-install-claude.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

tmp_parent="$(mktemp -d)"
trap 'rm -rf "$tmp_parent"' EXIT

out_dir="$tmp_parent/release asset with spaces"
claude_host_root="$tmp_parent/claude host root with spaces"
claude_skills_dir="$claude_host_root/skills/implementaudit"
mkdir -p "$out_dir" "$claude_skills_dir"

bash scripts/build-release-asset.sh "$out_dir"
asset="$out_dir/IMPLEMENTAUDIT.skill"
checksums="$out_dir/CHECKSUMS.txt"

bash scripts/write-release-checksums.sh --check --all "$out_dir" "$checksums"
bash scripts/install-claude-from-release.sh \
  --asset "$asset" \
  --checksum "$checksums" \
  --claude-skills-dir "$claude_skills_dir"

for file in \
  SKILL.md \
  references/planning-depth.md \
  references/phase-design.md \
  references/goal-format.md \
  references/transcript-contract.md \
  references/routing.md \
  references/repo-state-comparison.md \
  references/sidecars.md \
  references/child-agents.md \
  references/lean-operating-discipline.md \
  references/audit-category-matrix.md \
  references/audit-playbook.md \
  references/plan-lifecycle.md \
  scripts/claim-run.sh \
  scripts/detect-env.sh \
  scripts/detect-stack.sh \
  scripts/repo-state.sh \
  scripts/summarize-repo.sh \
  scripts/validate-audit-spec.sh \
  scripts/validate-phase.sh \
  scripts/validate-run-root.sh \
  scripts/custody-append.sh \
  scripts/lane-survivor-inventory.sh \
  templates/ROADMAP.md \
  templates/STATE.md \
  templates/THINKING.md \
  templates/phase-goal.txt \
  templates/child-agent-report.md \
  templates/final-report.md \
  templates/read-only-plan.md \
  templates/PROTOCOL.md \
  templates/host-notes.md \
  templates/sidecars.md \
  templates/tools.md \
  templates/context.md \
  internal-procedures/audit-state.md \
  internal-procedures/audit-assess.md \
  internal-procedures/audit-implement.md \
  internal-procedures/audit-andon.md
do
  [ -f "$claude_skills_dir/$file" ] || {
    printf 'release-asset-install-claude.test: missing installed file: %s\n' "$file" >&2
    exit 1
  }
done

if [ -e "$claude_skills_dir/IMPLEMENTAUDIT.md" ]; then
  printf 'release-asset-install-claude.test: root behavior file must not be installed\n' >&2
  exit 1
fi

[ -f "$claude_skills_dir/IMPLEMENTAUDIT_PACKAGE.json" ] \
  && [ -f "$claude_skills_dir/IMPLEMENTAUDIT_INVENTORY.json" ] || {
  printf 'release-asset-install-claude.test: package identity/inventory not installed\n' >&2
  exit 1
}

"${py_cmd[@]}" - "$claude_skills_dir" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
package = json.loads((root / "IMPLEMENTAUDIT_PACKAGE.json").read_text(encoding="utf-8"))
inventory = json.loads((root / "IMPLEMENTAUDIT_INVENTORY.json").read_text(encoding="utf-8"))
expected_required = ["implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon"]
expected_internal = [
    {"name": "audit-state", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-assess", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-implement", "maintainer_only": True, "directly_invocable": False},
    {"name": "audit-andon", "maintainer_only": False, "directly_invocable": True},
]
for owner in (package, inventory):
    if owner.get("public_governor") != "implementaudit":
        raise SystemExit("standalone public governor identity mismatch")
    if owner.get("required_skills") != expected_required:
        raise SystemExit("standalone required skill population mismatch")
    if owner.get("internal_skills") != expected_internal:
        raise SystemExit("standalone internal skill population mismatch")
expected_paths = {"IMPLEMENTAUDIT_INVENTORY.json"}
for member in inventory.get("members", []):
    path = root / member["path"]
    data = path.read_bytes()
    if len(data) != member["bytes"] or hashlib.sha256(data).hexdigest() != member["sha256"]:
        raise SystemExit(f"installed inventory mismatch: {member['path']}")
    expected_paths.add(member["path"])
observed_paths = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
if observed_paths != expected_paths:
    raise SystemExit("installed standalone population differs from exact inventory")
skill_docs = [path for path in root.rglob("SKILL.md") if path.is_file()]
if skill_docs != [root / "SKILL.md"]:
    raise SystemExit("standalone install exposed a discoverable child skill")
PY

# The standalone direction rejects a same-identity canonical plugin sibling.
ambiguous_root="$tmp_parent/ambiguous claude host"
mkdir -p "$ambiguous_root/plugins/implementaudit" "$ambiguous_root/skills"
printf '%s\n' 'plugin predecessor' > "$ambiguous_root/plugins/implementaudit/WITNESS.txt"
if bash scripts/install-claude-from-release.sh \
  --asset "$asset" \
  --checksum "$checksums" \
  --claude-skills-dir "$ambiguous_root/skills/implementaudit" >/dev/null 2>&1; then
  printf 'release-asset-install-claude.test: ambiguous plugin plus standalone unexpectedly passed\n' >&2
  exit 1
fi
[ -f "$ambiguous_root/plugins/implementaudit/WITNESS.txt" ] \
  || { printf 'release-asset-install-claude.test: ambiguity rejection changed plugin predecessor\n' >&2; exit 1; }
[ ! -e "$ambiguous_root/skills/implementaudit" ] \
  || { printf 'release-asset-install-claude.test: ambiguity rejection created standalone target\n' >&2; exit 1; }

stale="$out_dir/STALE-CHECKSUMS.txt"
printf 'sha256  %064d  IMPLEMENTAUDIT.skill\n' 0 > "$stale"

if bash scripts/install-claude-from-release.sh \
  --asset "$asset" \
  --checksum "$stale" \
  --claude-skills-dir "$tmp_parent/stale claude skill dir/implementaudit" >/dev/null 2>&1; then
  printf 'release-asset-install-claude.test: stale checksum unexpectedly passed\n' >&2
  exit 1
fi

overbroad_dir="$tmp_parent/overbroad asset"
mkdir -p "$overbroad_dir"
overbroad="$overbroad_dir/IMPLEMENTAUDIT.skill"
overbroad_checksums="$overbroad_dir/OVERBROAD-CHECKSUMS.txt"
"${py_cmd[@]}" - "$asset" "$overbroad" <<'PY'
import sys
import zipfile
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])

with zipfile.ZipFile(source) as src, zipfile.ZipFile(
    target, "w", compression=zipfile.ZIP_DEFLATED
) as dst:
    for info in src.infolist():
        dst.writestr(info, src.read(info.filename))
    dst.writestr("README.md", "repo-only doc must not be accepted in skill asset\n")
PY

bash scripts/write-release-checksums.sh "$overbroad" "$overbroad_checksums"
if bash scripts/install-claude-from-release.sh \
  --asset "$overbroad" \
  --checksum "$overbroad_checksums" \
  --claude-skills-dir "$tmp_parent/overbroad claude skill dir/implementaudit" >/dev/null 2>&1; then
  printf 'release-asset-install-claude.test: overbroad archive unexpectedly passed\n' >&2
  exit 1
fi

sidecar_dir="$tmp_parent/sidecar asset"
mkdir -p "$sidecar_dir"
sidecar="$sidecar_dir/IMPLEMENTAUDIT.skill"
sidecar_checksums="$sidecar_dir/SIDECAR-CHECKSUMS.txt"
"${py_cmd[@]}" - "$asset" "$sidecar" <<'PY'
import sys
import zipfile
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])

with zipfile.ZipFile(source) as src, zipfile.ZipFile(
    target, "w", compression=zipfile.ZIP_DEFLATED
) as dst:
    for info in src.infolist():
        dst.writestr(info, src.read(info.filename))
    dst.writestr("references/graph.json", "{}\n")
PY

bash scripts/write-release-checksums.sh "$sidecar" "$sidecar_checksums"
if bash scripts/install-claude-from-release.sh \
  --asset "$sidecar" \
  --checksum "$sidecar_checksums" \
  --claude-skills-dir "$tmp_parent/sidecar claude skill dir/implementaudit" >/dev/null 2>&1; then
  printf 'release-asset-install-claude.test: sidecar artifact unexpectedly passed\n' >&2
  exit 1
fi

printf 'release-asset-install-claude.test: ok\n'
