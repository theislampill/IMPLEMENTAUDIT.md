#!/usr/bin/env bash
set -euo pipefail

test_name="plugin-install.test"

fail() {
  printf '%s: %s\n' "$test_name" "$*" >&2
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
  fail "python, python3, or py -3 is required"
fi

tmp_parent="$(mktemp -d)"
trap 'rm -rf "$tmp_parent"' EXIT

out_dir="$tmp_parent/release asset with spaces"
mkdir -p "$out_dir"
bash scripts/build-release-asset.sh "$out_dir"

asset="$out_dir/IMPLEMENTAUDIT.plugin.zip"
checksums="$out_dir/CHECKSUMS.txt"
[ -f "$asset" ] || fail "canonical plugin asset was not built"
[ -f "$checksums" ] || fail "release checksum manifest was not built"

# Poison default-home discovery with temp canaries after the source-bound build,
# so Git can retain its configured trust while installers cannot discover homes.
export HOME="$(mktemp -d "$tmp_parent/default-home.XXXXXX")"
export CODEX_HOME="$(mktemp -d "$tmp_parent/default-codex-home.XXXXXX")"
export CLAUDE_HOME="$(mktemp -d "$tmp_parent/default-claude-home.XXXXXX")"

new_host_root() {
  local root
  root="$(mktemp -d "$tmp_parent/isolated-host-root.XXXXXX")"
  : > "$root/.implementaudit-isolated-host-root"
  printf '%s\n' "$root"
}

install_plugin() {
  local host="$1"
  local root="$2"
  local install_asset="$3"
  local install_checksums="$4"
  shift 4
  bash scripts/install-plugin-from-release.sh \
    --asset "$install_asset" \
    --checksum "$install_checksums" \
    --host "$host" \
    --host-root "$root" \
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

assert_exact_archive_tree() {
  "${py_cmd[@]}" - "$1" "$2" <<'PY'
import hashlib
import sys
import zipfile
from pathlib import Path, PurePosixPath

asset = Path(sys.argv[1])
target = Path(sys.argv[2])
if not target.is_dir():
    raise SystemExit(f"installed target is not a directory: {target}")

with zipfile.ZipFile(asset) as archive:
    expected = {}
    for info in archive.infolist():
        if info.is_dir():
            continue
        relative = PurePosixPath(info.filename)
        if relative.is_absolute() or ".." in relative.parts or "\\" in info.filename:
            raise SystemExit(f"unsafe member in test asset: {info.filename}")
        expected[relative.as_posix()] = (
            len(archive.read(info.filename)),
            hashlib.sha256(archive.read(info.filename)).hexdigest(),
        )

observed = {}
for path in target.rglob("*"):
    if path.is_symlink() or (path.exists() and not path.is_dir() and not path.is_file()):
        raise SystemExit(f"installed target contains a non-regular member: {path}")
    if path.is_file():
        data = path.read_bytes()
        observed[path.relative_to(target).as_posix()] = (
            len(data),
            hashlib.sha256(data).hexdigest(),
        )

if observed != expected:
    missing = sorted(set(expected) - set(observed))
    extra = sorted(set(observed) - set(expected))
    drift = sorted(
        name for name in set(expected) & set(observed) if expected[name] != observed[name]
    )
    raise SystemExit(
        f"installed member mismatch: missing={missing}, extra={extra}, hash_or_size_drift={drift}"
    )
PY
}

write_checksum() {
  "${py_cmd[@]}" - "$1" "$2" <<'PY'
import hashlib
import sys
from pathlib import Path

asset = Path(sys.argv[1])
manifest = Path(sys.argv[2])
manifest.write_text(
    f"sha256  {hashlib.sha256(asset.read_bytes()).hexdigest()}  {asset.name}\n",
    encoding="utf-8",
    newline="\n",
)
PY
}

rewrite_valid_predecessor() {
  local target="$1" version="$2" witness="${3:-}" source_commit="${4:-}"
  "${py_cmd[@]}" - "$target" "$version" "$witness" "$source_commit" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

target = Path(sys.argv[1])
version = sys.argv[2]
witness = sys.argv[3]
source_commit = sys.argv[4]
package_path = target / "IMPLEMENTAUDIT_PACKAGE.json"
inventory_path = target / "IMPLEMENTAUDIT_INVENTORY.json"
package = json.loads(package_path.read_text(encoding="utf-8"))
inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
package["runtime_version"] = version
inventory["runtime_version"] = version
if source_commit:
    inventory["source"]["commit"] = source_commit
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

mutate_archive() {
  "${py_cmd[@]}" - "$1" "$2" "$3" <<'PY'
import sys
import zipfile
from pathlib import Path

mode = sys.argv[1]
source = Path(sys.argv[2])
target = Path(sys.argv[3])
changed_member = "skills/implementaudit/SKILL.md"

with zipfile.ZipFile(source) as src, zipfile.ZipFile(
    target, "w", compression=zipfile.ZIP_DEFLATED
) as dst:
    for info in src.infolist():
        if mode == "missing" and info.filename == changed_member:
            continue
        data = src.read(info.filename)
        if mode == "drift" and info.filename == changed_member:
            data += b"\n# test-only archive hash drift\n"
        dst.writestr(info, data)
    if mode == "extra":
        info = zipfile.ZipInfo("zz-unexpected-test-member.txt", src.infolist()[0].date_time)
        info.create_system = 3
        info.external_attr = (0o100644 << 16)
        info.compress_type = zipfile.ZIP_DEFLATED
        dst.writestr(info, b"unexpected\n")
PY
}

assert_no_default_home_install() {
  local path
  for path in \
    "$HOME/plugins/implementaudit" \
    "$HOME/skills/implementaudit" \
    "$CODEX_HOME/plugins/implementaudit" \
    "$CODEX_HOME/skills/implementaudit" \
    "$CLAUDE_HOME/plugins/implementaudit" \
    "$CLAUDE_HOME/skills/implementaudit"
  do
    [ ! -e "$path" ] || fail "installer touched a default-home canary: $path"
  done
}

# A directory at the sentinel path is not the required regular sentinel file.
bad_sentinel_root="$(mktemp -d "$tmp_parent/bad-sentinel-root.XXXXXX")"
mkdir "$bad_sentinel_root/.implementaudit-isolated-host-root"
expect_install_failure "non-regular host-root sentinel" \
  install_plugin codex "$bad_sentinel_root" "$asset" "$checksums" --version 0.4.0
[ ! -e "$bad_sentinel_root/plugins/implementaudit" ] \
  || fail "sentinel rejection created a plugin target"

# The transaction root itself must not escape the isolated host through a
# directory alias. Exercise this where the checkout host permits symlinks.
aliased_root="$(new_host_root)"
alias_target="$(mktemp -d "$tmp_parent/aliased-plugins-target.XXXXXX")"
if ln -s "$alias_target" "$aliased_root/plugins" 2>/dev/null; then
  expect_install_failure "aliased plugins transaction root" \
    install_plugin codex "$aliased_root" "$asset" "$checksums" --version 0.4.0
  [ ! -e "$alias_target/implementaudit" ] \
    || fail "aliased plugins root escaped the isolated host"
fi

# Both host selectors install the same canonical plugin tree. Reinstalling the
# exact version must be idempotent, and the host-visible claim stays staged-copy.
for host in codex claude; do
  root="$(new_host_root)"
  output="$tmp_parent/clean-$host.out"
  install_plugin "$host" "$root" "$asset" "$checksums" --version 0.4.0 >"$output"
  grep -Eiq 'staged[- ]copy' "$output" \
    || fail "$host install did not identify its result as staged-copy proof"
  target="$root/plugins/implementaudit"
  assert_exact_archive_tree "$asset" "$target"
  before="$(tree_digest "$target")"
  install_plugin "$host" "$root" "$asset" "$checksums" --version 0.4.0 \
    >"$tmp_parent/idempotent-$host.out"
  after="$(tree_digest "$target")"
  [ "$after" = "$before" ] || fail "$host same-version reinstall was not idempotent"
  assert_exact_archive_tree "$asset" "$target"
done

stale_checksum="$tmp_parent/STALE-CHECKSUMS.txt"
printf 'sha256  %064d  IMPLEMENTAUDIT.plugin.zip\n' 0 > "$stale_checksum"
root="$(new_host_root)"
expect_install_failure "stale checksum" \
  install_plugin codex "$root" "$asset" "$stale_checksum" --version 0.4.0
[ ! -e "$root/plugins/implementaudit" ] || fail "stale checksum created a plugin target"

for mutation in missing extra drift; do
  mutation_dir="$(mktemp -d "$tmp_parent/$mutation-archive.XXXXXX")"
  mutated_asset="$mutation_dir/IMPLEMENTAUDIT.plugin.zip"
  mutated_checksums="$mutation_dir/CHECKSUMS.txt"
  mutate_archive "$mutation" "$asset" "$mutated_asset"
  write_checksum "$mutated_asset" "$mutated_checksums"
  root="$(new_host_root)"
  expect_install_failure "$mutation archive" \
    install_plugin codex "$root" "$mutated_asset" "$mutated_checksums" --version 0.4.0
  [ ! -e "$root/plugins/implementaudit" ] \
    || fail "$mutation archive created a plugin target"
done

# A standalone skill and canonical plugin in the same host root are ambiguous.
root="$(new_host_root)"
standalone="$root/skills/implementaudit"
mkdir -p "$standalone"
printf '%s\n' 'standalone predecessor' > "$standalone/SKILL.md"
standalone_before="$(tree_digest "$standalone")"
expect_install_failure "ambiguous standalone co-install" \
  install_plugin claude "$root" "$asset" "$checksums" --version 0.4.0
[ "$(tree_digest "$standalone")" = "$standalone_before" ] \
  || fail "co-install rejection changed the standalone predecessor"
[ ! -e "$root/plugins/implementaudit" ] \
  || fail "co-install rejection created a plugin target"

# A stale partial target may be atomically replaced or rejected unchanged.
root="$(new_host_root)"
target="$root/plugins/implementaudit"
mkdir -p "$target/nested"
printf '%s\n' 'stale partial predecessor' > "$target/nested/witness.txt"
partial_before="$(tree_digest "$target")"
if install_plugin codex "$root" "$asset" "$checksums" --version 0.4.0 \
  >"$tmp_parent/stale-partial.out" 2>&1; then
  assert_exact_archive_tree "$asset" "$target"
else
  [ "$(tree_digest "$target")" = "$partial_before" ] \
    || fail "rejected stale partial target was not preserved exactly"
fi

# Fabricate a self-consistent installed predecessor inventory at a later version
# to exercise the downgrade decision without accepting a second release asset.
root="$(new_host_root)"
install_plugin codex "$root" "$asset" "$checksums" --version 0.4.0 \
  >"$tmp_parent/downgrade-setup.out"
target="$root/plugins/implementaudit"
rewrite_valid_predecessor "$target" 0.5.0
downgrade_before="$(tree_digest "$target")"
expect_install_failure "unauthorized downgrade" \
  install_plugin codex "$root" "$asset" "$checksums" --version 0.4.0
[ "$(tree_digest "$target")" = "$downgrade_before" ] \
  || fail "unauthorized downgrade changed its predecessor"

# The same runtime label with a different source identity is not an idempotent
# reinstall and must not silently replace the current exact package.
root="$(new_host_root)"
install_plugin codex "$root" "$asset" "$checksums" --version 0.4.0 \
  >"$tmp_parent/same-label-setup.out"
target="$root/plugins/implementaudit"
rewrite_valid_predecessor "$target" 0.4.0 "" ffffffffffffffffffffffffffffffffffffffff
same_label_before="$(tree_digest "$target")"
expect_install_failure "same-label changed source" \
  install_plugin codex "$root" "$asset" "$checksums" --version 0.4.0
[ "$(tree_digest "$target")" = "$same_label_before" ] \
  || fail "same-label rejection changed its predecessor"

for fault in before-swap during-swap remove-staged-member; do
  root="$(new_host_root)"
  install_plugin codex "$root" "$asset" "$checksums" --version 0.4.0 \
    >"$tmp_parent/fault-setup-$fault.out"
  target="$root/plugins/implementaudit"
  rewrite_valid_predecessor "$target" 0.3.9 "$fault predecessor witness"
  predecessor="$(tree_digest "$target")"
  if IMPLEMENTAUDIT_INSTALL_FAULT="$fault" \
    install_plugin codex "$root" "$asset" "$checksums" --version 0.4.0 \
      >"$tmp_parent/fault-$fault.out" 2>&1; then
    fail "fault injection $fault unexpectedly passed"
  fi
  [ "$(tree_digest "$target")" = "$predecessor" ] \
    || fail "fault injection $fault did not restore the exact predecessor"
  sibling_count="$(find "$root/plugins" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d '[:space:]')"
  [ "$sibling_count" -eq 1 ] \
    || fail "fault injection $fault left a staging or backup directory"
done

assert_no_default_home_install
printf '%s: ok (staged-copy proof only; no native host discovery/import claim)\n' "$test_name"
