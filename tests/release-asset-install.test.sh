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
  printf 'release-asset-install.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

fail() {
  printf 'release-asset-install.test: %s\n' "$*" >&2
  exit 1
}

install_codex() {
  local install_home="$1"
  shift
  bash scripts/install-codex-from-release.sh \
    --asset "$asset" \
    --checksum "$checksums" \
    --codex-home "$install_home" \
    --version 0.4.0 \
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

skills_root = Path(sys.argv[1]) / "skills"
residue = sorted(
    path.name
    for pattern in (".implementaudit-stage-*", ".implementaudit-backup-*")
    for path in skills_root.glob(pattern)
)
if residue:
    raise SystemExit(f"stale standalone install transaction residue: {residue}")
PY
}

tmp_parent="$(mktemp -d)"
trap 'rm -rf "$tmp_parent"' EXIT

out_dir="$tmp_parent/release asset with spaces"
codex_home="$tmp_parent/codex home with spaces"
mkdir -p "$out_dir" "$codex_home"

bash scripts/build-release-asset.sh "$out_dir"
asset="$out_dir/IMPLEMENTAUDIT.skill"
checksums="$out_dir/CHECKSUMS.txt"

bash scripts/write-release-checksums.sh --check --all "$out_dir" "$checksums"
bash scripts/install-codex-from-release.sh \
  --asset "$asset" \
  --checksum "$checksums" \
  --codex-home "$codex_home"

installed="$codex_home/skills/implementaudit"
for file in \
  SKILL.md \
  references/planning-depth.md \
  references/phase-design.md \
  references/goal-format.md \
  references/transcript-contract.md \
  references/continuity.md \
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
  [ -f "$installed/$file" ] || {
    printf 'release-asset-install.test: missing installed file: %s\n' "$file" >&2
    exit 1
  }
done

"${py_cmd[@]}" - "$installed" <<'PY'
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
[ ! -e "$installed/.claude-plugin/plugin.json" ] && [ ! -e "$installed/.claude-plugin/marketplace.json" ] || {
  printf 'release-asset-install.test: Codex projection must exclude both plugin manifests\n' >&2
  exit 1
}
[ -f "$installed/IMPLEMENTAUDIT_PACKAGE.json" ] \
  && [ -f "$installed/IMPLEMENTAUDIT_INVENTORY.json" ] || {
  printf 'release-asset-install.test: package identity/inventory not installed\n' >&2
  exit 1
}

if [ -e "$installed/IMPLEMENTAUDIT.md" ]; then
  printf 'release-asset-install.test: root behavior file must not be installed\n' >&2
  exit 1
fi

# An existing standalone target is an update predecessor, not disposable
# staging. It must be exact before any transaction path is created.
partial_home="$tmp_parent/partial predecessor home"
partial_target="$partial_home/skills/implementaudit"
mkdir -p "$partial_target/nested"
printf '%s\n' 'stale partial predecessor' > "$partial_target/nested/witness.txt"
partial_before="$(tree_digest "$partial_target")"
expect_install_failure "stale partial predecessor" install_codex "$partial_home"
[ "$(tree_digest "$partial_target")" = "$partial_before" ] \
  || fail "rejected stale partial predecessor was not preserved exactly"
assert_no_transaction_residue "$partial_home"

# A self-consistent inventory for another package role is not an admissible
# predecessor and must be rejected before update policy or staging begins.
foreign_home="$tmp_parent/foreign package predecessor home"
install_codex "$foreign_home" >"$tmp_parent/foreign-setup.out"
foreign_target="$foreign_home/skills/implementaudit"
rewrite_valid_predecessor "$foreign_target" 0.3.9 "" "" not-implementaudit
foreign_before="$(tree_digest "$foreign_target")"
expect_install_failure "foreign package predecessor" install_codex "$foreign_home"
[ "$(tree_digest "$foreign_target")" = "$foreign_before" ] \
  || fail "foreign package rejection changed its predecessor"
assert_no_transaction_residue "$foreign_home"

# Reinstalling the exact package is a no-op: content and filesystem identity
# remain unchanged, proving the target was not deleted and recopied.
idempotent_before="$(tree_digest "$installed")"
idempotent_path_before="$(path_identity "$installed")"
install_codex "$codex_home" >"$tmp_parent/idempotent.out"
[ "$(tree_digest "$installed")" = "$idempotent_before" ] \
  || fail "exact reinstall changed installed content"
[ "$(path_identity "$installed")" = "$idempotent_path_before" ] \
  || fail "exact reinstall churned the installed target"
assert_no_transaction_residue "$codex_home"

# The same runtime label with a different exact package identity is neither a
# no-op nor an authorized replacement.
same_version_home="$tmp_parent/same version changed identity home"
install_codex "$same_version_home" >"$tmp_parent/same-version-setup.out"
same_version_target="$same_version_home/skills/implementaudit"
rewrite_valid_predecessor \
  "$same_version_target" 0.4.0 "" ffffffffffffffffffffffffffffffffffffffff
same_version_before="$(tree_digest "$same_version_target")"
expect_install_failure "same-version changed identity" install_codex "$same_version_home"
[ "$(tree_digest "$same_version_target")" = "$same_version_before" ] \
  || fail "same-version identity rejection changed its predecessor"
assert_no_transaction_residue "$same_version_home"

# Downgrades are rejected by default and require the explicit reviewed flag.
downgrade_home="$tmp_parent/downgrade home"
install_codex "$downgrade_home" >"$tmp_parent/downgrade-setup.out"
downgrade_target="$downgrade_home/skills/implementaudit"
rewrite_valid_predecessor "$downgrade_target" 0.5.0 "later predecessor witness"
downgrade_before="$(tree_digest "$downgrade_target")"
expect_install_failure "unauthorized downgrade" install_codex "$downgrade_home"
[ "$(tree_digest "$downgrade_target")" = "$downgrade_before" ] \
  || fail "unauthorized downgrade changed its predecessor"
install_codex "$downgrade_home" --allow-downgrade >"$tmp_parent/downgrade-approved.out"
[ "$(tree_digest "$downgrade_target")" = "$idempotent_before" ] \
  || fail "reviewed downgrade did not install the exact incoming package"
assert_no_transaction_residue "$downgrade_home"

# Each scoped failure point must preserve the exact validated predecessor,
# including the shared internal-skill resolver, and remove owned transaction
# paths. remove-staged-member specifically proves staged validation precedes
# swapping; post-readback proves rollback after the incoming target is visible.
for fault in remove-staged-member before-swap during-swap post-readback; do
  fault_home="$tmp_parent/fault $fault home"
  install_codex "$fault_home" >"$tmp_parent/fault-setup-$fault.out"
  fault_target="$fault_home/skills/implementaudit"
  rewrite_valid_predecessor "$fault_target" 0.3.9 "$fault predecessor witness"
  fault_before="$(tree_digest "$fault_target")"
  if IMPLEMENTAUDIT_CODEX_INSTALL_FAULT="$fault" \
    install_codex "$fault_home" >"$tmp_parent/fault-$fault.out" 2>&1; then
    fail "fault injection $fault unexpectedly passed"
  fi
  [ "$(tree_digest "$fault_target")" = "$fault_before" ] \
    || fail "fault injection $fault did not restore the exact predecessor"
  [ -f "$fault_target/scripts/resolve-internal-skill.py" ] \
    || fail "fault injection $fault lost the predecessor resolver helper"
  assert_no_transaction_residue "$fault_home"
done

# The standalone direction rejects a same-identity canonical plugin sibling.
ambiguous_home="$tmp_parent/ambiguous codex home"
mkdir -p "$ambiguous_home/plugins/implementaudit"
printf '%s\n' 'plugin predecessor' > "$ambiguous_home/plugins/implementaudit/WITNESS.txt"
if bash scripts/install-codex-from-release.sh \
  --asset "$asset" \
  --checksum "$checksums" \
  --codex-home "$ambiguous_home" \
  --version 0.4.0 >/dev/null 2>&1; then
  printf 'release-asset-install.test: ambiguous plugin plus standalone unexpectedly passed\n' >&2
  exit 1
fi
[ -f "$ambiguous_home/plugins/implementaudit/WITNESS.txt" ] \
  || { printf 'release-asset-install.test: ambiguity rejection changed plugin predecessor\n' >&2; exit 1; }
[ ! -e "$ambiguous_home/skills/implementaudit" ] \
  || { printf 'release-asset-install.test: ambiguity rejection created standalone target\n' >&2; exit 1; }

# The default follows the current runtime family. Stale and arbitrary caller
# values remain hard mismatches rather than overrides.
for mismatched_version in 0.3.3 9.9.9; do
  if bash scripts/install-codex-from-release.sh \
    --asset "$asset" \
    --checksum "$checksums" \
    --codex-home "$tmp_parent/wrong version $mismatched_version" \
    --version "$mismatched_version" >/dev/null 2>&1; then
    printf 'release-asset-install.test: mismatched runtime %s unexpectedly passed\n' "$mismatched_version" >&2
    exit 1
  fi
done

stale="$out_dir/STALE-CHECKSUMS.txt"
printf 'sha256  %064d  IMPLEMENTAUDIT.skill\n' 0 > "$stale"

if bash scripts/install-codex-from-release.sh \
  --asset "$asset" \
  --checksum "$stale" \
  --codex-home "$tmp_parent/stale codex home" \
  --version 0.4.0 >/dev/null 2>&1; then
  printf 'release-asset-install.test: stale checksum unexpectedly passed\n' >&2
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
if bash scripts/install-codex-from-release.sh \
  --asset "$overbroad" \
  --checksum "$overbroad_checksums" \
  --codex-home "$tmp_parent/overbroad codex home" \
  --version 0.4.0 >/dev/null 2>&1; then
  printf 'release-asset-install.test: overbroad archive unexpectedly passed\n' >&2
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
if bash scripts/install-codex-from-release.sh \
  --asset "$sidecar" \
  --checksum "$sidecar_checksums" \
  --codex-home "$tmp_parent/sidecar codex home" \
  --version 0.4.0 >/dev/null 2>&1; then
  printf 'release-asset-install.test: sidecar artifact unexpectedly passed\n' >&2
  exit 1
fi

printf 'release-asset-install.test: ok\n'
