#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

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

fail() {
  printf 'release-asset-install-claude.test: %s\n' "$*" >&2
  exit 1
}

install_claude() {
  local install_target="$1"
  shift
  bash scripts/install-claude-from-release.sh \
    --asset "$asset" \
    --checksum "$checksums" \
    --claude-skills-dir "$install_target" \
    "$@"
}

expect_install_failure() {
  local label="$1"
  shift
  if "$@" >"$tmp_parent/rejected.out" 2>&1; then
    fail "$label unexpectedly passed"
  fi
}

tree_digest() {
  "${py_cmd[@]}" - "$1" <<'PY'
import hashlib
import os
import stat
import sys
from pathlib import Path

root = Path(sys.argv[1])
digest = hashlib.sha256()
if not root.exists():
    digest.update(b"<absent>\0")
else:
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        metadata = path.lstat()
        digest.update(relative + b"\0")
        digest.update(f"{stat.S_IMODE(metadata.st_mode):04o}".encode("ascii") + b"\0")
        if path.is_symlink():
            digest.update(b"L\0" + os.readlink(path).encode("utf-8") + b"\0")
        elif path.is_dir():
            digest.update(b"D\0")
        elif path.is_file():
            digest.update(b"F\0" + hashlib.sha256(path.read_bytes()).digest())
        else:
            digest.update(b"O\0")
print(digest.hexdigest())
PY
}

path_identity() {
  "${py_cmd[@]}" - "$1" <<'PY'
import sys
from pathlib import Path

metadata = Path(sys.argv[1]).stat()
print(f"{metadata.st_dev}:{metadata.st_ino}:{metadata.st_ctime_ns}")
PY
}

rewrite_valid_predecessor() {
  local target="$1" version="$2" witness="${3:-}" source_commit="${4:-}" package_name="${5:-}"
  "${py_cmd[@]}" - "$target" "$version" "$witness" "$source_commit" "$package_name" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

target = Path(sys.argv[1])
version = sys.argv[2]
witness = sys.argv[3]
source_commit = sys.argv[4]
package_name = sys.argv[5]
package_path = target / "IMPLEMENTAUDIT_PACKAGE.json"
inventory_path = target / "IMPLEMENTAUDIT_INVENTORY.json"
package = json.loads(package_path.read_text(encoding="utf-8"))
inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
package["runtime_version"] = version
inventory["runtime_version"] = version
if source_commit:
    inventory["source"]["commit"] = source_commit
if package_name:
    package["package_name"] = package_name
    inventory["package_name"] = package_name
package_path.write_text(
    json.dumps(package, indent=2) + "\n", encoding="utf-8", newline="\n"
)
if witness:
    (target / "PREDECESSOR-WITNESS.txt").write_text(
        witness + "\n", encoding="utf-8", newline="\n"
    )
members = []
for path in sorted(target.rglob("*"), key=lambda item: item.relative_to(target).as_posix()):
    if not path.is_file() or path == inventory_path:
        continue
    data = path.read_bytes()
    members.append({
        "path": path.relative_to(target).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    })
inventory["members"] = members
inventory_path.write_text(
    json.dumps(inventory, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
PY
}

assert_no_transaction_residue() {
  "${py_cmd[@]}" - "$1" <<'PY'
import sys
from pathlib import Path

target = Path(sys.argv[1])
residue = sorted(
    path.name
    for pattern in (".implementaudit-stage-*", ".implementaudit-backup-*")
    for path in target.parent.glob(pattern)
)
if residue:
    raise SystemExit(f"stale Claude standalone install transaction residue: {residue}")
PY
}

tmp_parent="$(mktemp -d)"
trap 'rm -rf "$tmp_parent"' EXIT

out_dir="$tmp_parent/release asset with spaces"
claude_host_root="$tmp_parent/claude host root with spaces"
claude_skills_dir="$claude_host_root/skills/implementaudit"
mkdir -p "$out_dir" "$claude_host_root/skills"

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
  scripts/resolve-internal-skill.py \
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

# An existing standalone target is an update predecessor, not disposable
# staging. It must be exact before any transaction path is created.
partial_target="$tmp_parent/partial predecessor/skills/implementaudit"
mkdir -p "$partial_target/nested"
printf '%s\n' 'stale partial predecessor' > "$partial_target/nested/witness.txt"
partial_before="$(tree_digest "$partial_target")"
expect_install_failure "stale partial predecessor" install_claude "$partial_target"
[ "$(tree_digest "$partial_target")" = "$partial_before" ] \
  || fail "rejected stale partial predecessor was not preserved exactly"
assert_no_transaction_residue "$partial_target"

# A self-consistent inventory for another package is not an admissible
# predecessor and must be rejected before update policy or staging begins.
foreign_target="$tmp_parent/foreign package predecessor/skills/implementaudit"
install_claude "$foreign_target" >"$tmp_parent/foreign-setup.out"
rewrite_valid_predecessor "$foreign_target" 0.3.9 "" "" not-implementaudit
foreign_before="$(tree_digest "$foreign_target")"
expect_install_failure "foreign package predecessor" install_claude "$foreign_target"
[ "$(tree_digest "$foreign_target")" = "$foreign_before" ] \
  || fail "foreign package rejection changed its predecessor"
assert_no_transaction_residue "$foreign_target"

# Reinstalling the exact package is a no-op: content and filesystem identity
# remain unchanged, proving the target was not deleted and recopied.
idempotent_before="$(tree_digest "$claude_skills_dir")"
idempotent_path_before="$(path_identity "$claude_skills_dir")"
install_claude "$claude_skills_dir" >"$tmp_parent/idempotent.out"
[ "$(tree_digest "$claude_skills_dir")" = "$idempotent_before" ] \
  || fail "exact reinstall changed installed content"
[ "$(path_identity "$claude_skills_dir")" = "$idempotent_path_before" ] \
  || fail "exact reinstall churned the installed target"
assert_no_transaction_residue "$claude_skills_dir"

# The same runtime label with a different exact package identity is neither a
# no-op nor an authorized replacement.
same_version_target="$tmp_parent/same version changed identity/skills/implementaudit"
install_claude "$same_version_target" >"$tmp_parent/same-version-setup.out"
rewrite_valid_predecessor \
  "$same_version_target" 0.4.0 "" ffffffffffffffffffffffffffffffffffffffff
same_version_before="$(tree_digest "$same_version_target")"
expect_install_failure \
  "same-version changed identity" install_claude "$same_version_target"
[ "$(tree_digest "$same_version_target")" = "$same_version_before" ] \
  || fail "same-version identity rejection changed its predecessor"
assert_no_transaction_residue "$same_version_target"

# Downgrades are rejected by default and require the explicit reviewed flag.
downgrade_target="$tmp_parent/downgrade/skills/implementaudit"
install_claude "$downgrade_target" >"$tmp_parent/downgrade-setup.out"
rewrite_valid_predecessor "$downgrade_target" 0.5.0 "later predecessor witness"
downgrade_before="$(tree_digest "$downgrade_target")"
expect_install_failure "unauthorized downgrade" install_claude "$downgrade_target"
[ "$(tree_digest "$downgrade_target")" = "$downgrade_before" ] \
  || fail "unauthorized downgrade changed its predecessor"
install_claude "$downgrade_target" --allow-downgrade \
  >"$tmp_parent/downgrade-approved.out"
[ "$(tree_digest "$downgrade_target")" = "$idempotent_before" ] \
  || fail "reviewed downgrade did not install the exact incoming package"
assert_no_transaction_residue "$downgrade_target"

# Each scoped failure point must preserve the exact validated predecessor,
# including the shared internal-skill resolver, and remove owned transaction
# paths. remove-staged-member proves staged validation precedes swapping;
# post-readback proves rollback after the incoming target is visible.
for fault in remove-staged-member before-swap during-swap post-readback; do
  fault_target="$tmp_parent/fault $fault/skills/implementaudit"
  install_claude "$fault_target" >"$tmp_parent/fault-setup-$fault.out"
  rewrite_valid_predecessor "$fault_target" 0.3.9 "$fault predecessor witness"
  fault_before="$(tree_digest "$fault_target")"
  if IMPLEMENTAUDIT_CLAUDE_INSTALL_FAULT="$fault" \
    install_claude "$fault_target" >"$tmp_parent/fault-$fault.out" 2>&1; then
    fail "fault injection $fault unexpectedly passed"
  fi
  [ "$(tree_digest "$fault_target")" = "$fault_before" ] \
    || fail "fault injection $fault did not restore the exact predecessor"
  [ -f "$fault_target/scripts/resolve-internal-skill.py" ] \
    || fail "fault injection $fault lost the predecessor resolver helper"
  assert_no_transaction_residue "$fault_target"
done

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
