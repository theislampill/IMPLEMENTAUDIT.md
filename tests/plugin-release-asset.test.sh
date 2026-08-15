#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/scripts/check-package-contract.sh"

fail() {
  printf 'plugin-release-asset.test: %s\n' "$*" >&2
  exit 1
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

[ -f "$checker" ] || fail "package-contract checker is absent"

PYTHONDONTWRITEBYTECODE=1 "${py_cmd[@]}" - "$repo_root/scripts/package-contract.py" <<'PY' \
  || fail "standalone projection does not normalize plugin-relative separator variants"
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("package_contract", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

frontmatter = b"---\nname: audit-state\n---\n"
cases = {
    rb"`..\implementaudit\references\continuity.md`": b"`../references/continuity.md`",
    rb"`../implementaudit\scripts/claim-run.sh`": b"`../scripts/claim-run.sh`",
}
for source_path, expected_path in cases.items():
    rows = module.standalone_internal_procedure_entries(
        [("skills/audit-state/SKILL.md", frontmatter + source_path + b"\n", 0o644)]
    )
    if rows[0][1] != expected_path + b"\n":
        raise SystemExit(f"separator variant was not normalized: {source_path!r}")
PY

source_commit="$(git -C "$repo_root" rev-parse HEAD^{commit})"
source_tree="$(git -C "$repo_root" rev-parse "${source_commit}^{tree}")"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

clone_candidate() {
  local lane="$1"
  local target="$tmp/checkout-$lane"
  git clone --quiet --no-local --no-checkout "$repo_root" "$target"
  git -C "$target" checkout --quiet --detach "$source_commit"
  [ -z "$(git -C "$target" status --porcelain)" ] \
    || fail "$lane candidate is not clean"
}

build_candidate() {
  local lane="$1" timezone="$2"
  local root="$tmp/checkout-$lane" out="$tmp/out-$lane"
  mkdir -p "$out"
  if ! SOURCE_DATE_EPOCH=315532800 TZ="$timezone" LC_ALL=C \
      bash "$root/scripts/build-release-asset.sh" "$out" \
      >"$tmp/build-$lane.log" 2>&1; then
    tail -n 8 "$tmp/build-$lane.log" >&2
    fail "$lane build failed"
  fi
  [ -f "$out/IMPLEMENTAUDIT.plugin.zip" ] \
    || fail "$lane build did not produce IMPLEMENTAUDIT.plugin.zip"
  [ -f "$out/IMPLEMENTAUDIT.skill" ] \
    || fail "$lane build did not produce IMPLEMENTAUDIT.skill"
  [ -f "$out/CHECKSUMS.txt" ] \
    || fail "$lane build did not produce CHECKSUMS.txt"
  bash "$root/scripts/write-release-checksums.sh" --check --all \
    "$out" "$out/CHECKSUMS.txt" \
    || fail "$lane build produced a non-canonical checksum manifest"
  [ "$(wc -l < "$out/CHECKSUMS.txt" | tr -d '[:space:]')" -eq 2 ] \
    || fail "$lane checksum manifest does not contain exactly two entries"
  [ "$(awk '{print $3}' "$out/CHECKSUMS.txt")" = \
      "$(printf '%s\n' IMPLEMENTAUDIT.plugin.zip IMPLEMENTAUDIT.skill)" ] \
    || fail "$lane checksum manifest is not sorted by the exact artifact names"
}

validate_pair() {
  local root="$1" out="$2" expected_state="$3"
  "${py_cmd[@]}" - \
    "$root/package/implementaudit-package.json" \
    "$out/IMPLEMENTAUDIT.plugin.zip" \
    "$out/IMPLEMENTAUDIT.skill" \
    "$source_commit" "$source_tree" "$expected_state" <<'PY'
import hashlib
import json
import posixpath
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

(
    source_package_path,
    canonical_path,
    standalone_path,
    expected_commit,
    expected_tree,
    expected_state,
) = sys.argv[1:]

source_package = json.loads(
    Path(source_package_path).read_text(encoding="utf-8")
)
source_root = Path(source_package_path).resolve().parents[1]
expected_required_skills = [
    "implementaudit",
    "audit-state",
    "audit-assess",
    "audit-implement",
    "audit-andon",
]
expected_internal_skills = [
    {"name": "audit-state", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-assess", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-implement", "maintainer_only": True, "directly_invocable": False},
    {"name": "audit-andon", "maintainer_only": False, "directly_invocable": True},
]
if source_package.get("required_skills") != expected_required_skills:
    raise SystemExit("required_skills does not bind the exact five-skill population")
if source_package.get("internal_skills") != expected_internal_skills:
    raise SystemExit("internal_skills does not bind the exact four-child population")

expected_identity = {
    "logical_package": "IMPLEMENTAUDIT_PLUGIN",
    "package_name": "implementaudit",
    "runtime_version": "0.4.0",
    "release_family": "v0.4.0.0",
    "public_governor": "implementaudit",
    "required_skills": expected_required_skills,
    "internal_skills": expected_internal_skills,
}
observed_identity = {
    key: source_package.get(key) for key in expected_identity
}
if observed_identity != expected_identity:
    raise SystemExit("source package identity is not the admitted v0.4.0 identity")

expected_timestamp = (1980, 1, 1, 0, 0, 0)
inventory_name = "IMPLEMENTAUDIT_INVENTORY.json"
package_name = "IMPLEMENTAUDIT_PACKAGE.json"


def validate_archive(raw_path, role):
    path = Path(raw_path)
    cap = source_package["budgets"][role]["cap_bytes"]
    if cap != 327680:
        raise SystemExit(f"{role} cap is not the predeclared 327680 bytes")
    if path.stat().st_size > cap:
        raise SystemExit(f"{role} exceeds its predeclared size cap")

    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if names != sorted(names):
            raise SystemExit(f"{role} members are not in deterministic order")
        if len(names) != len(set(names)):
            raise SystemExit(f"{role} contains duplicate members")
        if archive.comment:
            raise SystemExit(f"{role} has an archive comment")

        payloads = {}
        for info in infos:
            member = PurePosixPath(info.filename)
            if (
                info.is_dir()
                or "\\" in info.filename
                or member.is_absolute()
                or ".." in member.parts
            ):
                raise SystemExit(f"{role} has a non-canonical member path")
            if info.date_time != expected_timestamp:
                raise SystemExit(f"{role} has an unpinned member timestamp")
            if info.create_system != 3 or info.create_version != 20:
                raise SystemExit(f"{role} has an unpinned ZIP creator")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise SystemExit(f"{role} has a non-DEFLATE member")
            if info.extra or info.comment:
                raise SystemExit(f"{role} has unexpected member metadata")
            mode = (info.external_attr >> 16) & 0o777
            executable = (
                info.filename.startswith("scripts/")
                or info.filename.startswith("skills/implementaudit/scripts/")
            )
            expected_mode = 0o755 if executable else 0o644
            if mode != expected_mode:
                raise SystemExit(f"{role} has an incorrect member mode")
            payloads[info.filename] = archive.read(info.filename)

    required_metadata = {package_name, inventory_name}
    missing_metadata = sorted(required_metadata - payloads.keys())
    if missing_metadata:
        raise SystemExit(f"{role} is missing embedded package metadata")

    embedded_package = json.loads(payloads[package_name].decode("utf-8"))
    if embedded_package != source_package:
        raise SystemExit(f"{role} embedded package identity differs from source")

    inventory = json.loads(payloads[inventory_name].decode("utf-8"))
    expected_format = source_package["inventory_contract"]["format"]
    if inventory.get("schema") != expected_format:
        raise SystemExit(f"{role} inventory format is incorrect")
    if inventory.get("artifact_role") != role:
        raise SystemExit(f"{role} inventory role is incorrect")
    for field in ("public_governor", "required_skills", "internal_skills"):
        if inventory.get(field) != source_package.get(field):
            raise SystemExit(f"{role} inventory {field} differs from package identity")

    binding = inventory.get("source")
    expected_binding = {
        "commit": expected_commit,
        "tree": expected_tree,
        "worktree_state": expected_state,
    }
    if binding != expected_binding:
        raise SystemExit(f"{role} source binding is incorrect")

    members = inventory.get("members")
    if not isinstance(members, list):
        raise SystemExit(f"{role} inventory members must be a list")
    expected_members = []
    for member_path in sorted(set(payloads) - {inventory_name}):
        data = payloads[member_path]
        expected_members.append({
            "path": member_path,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    if members != expected_members:
        raise SystemExit(f"{role} inventory does not match exact archive members")

    top_level = {PurePosixPath(name).parts[0] for name in payloads}
    if role == "canonical_plugin":
        expected_top_level = {
            ".codex-plugin",
            ".claude-plugin",
            "skills",
            package_name,
            inventory_name,
        }
        if top_level != expected_top_level:
            raise SystemExit("canonical plugin top-level layout is incorrect")
        required = {
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            "skills/implementaudit/SKILL.md",
            "skills/audit-state/SKILL.md",
            "skills/audit-assess/SKILL.md",
            "skills/audit-implement/SKILL.md",
            "skills/audit-andon/SKILL.md",
        }
        if not required.issubset(payloads):
            raise SystemExit("canonical plugin is missing required plugin-root members")
        observed_skills = sorted(
            PurePosixPath(name).parts[1]
            for name in payloads
            if len(PurePosixPath(name).parts) == 3
            and PurePosixPath(name).parts[0] == "skills"
            and PurePosixPath(name).name == "SKILL.md"
        )
        if observed_skills != sorted(expected_required_skills):
            raise SystemExit("canonical plugin skill population is not exact")
        child_prefixes = {
            f"skills/{name}/" for name in expected_required_skills if name != "implementaudit"
        }
        for name in payloads:
            if any(name.startswith(prefix) for prefix in child_prefixes) and not name.endswith("/SKILL.md"):
                raise SystemExit("canonical plugin child owns duplicated substrate")
        for prefix in (
            "skills/implementaudit/references/",
            "skills/implementaudit/scripts/",
            "skills/implementaudit/templates/",
        ):
            if not any(name.startswith(prefix) for name in payloads):
                raise SystemExit(f"canonical plugin is missing {prefix}")
        if any(
            name == "SKILL.md"
            or name.startswith(("references/", "scripts/", "templates/"))
            for name in payloads
        ):
            raise SystemExit("canonical plugin contains flattened skill payload")
    else:
        expected_top_level = {
            "SKILL.md",
            "references",
            "scripts",
            "templates",
            "internal-procedures",
            package_name,
            inventory_name,
        }
        if top_level != expected_top_level:
            raise SystemExit("standalone top-level layout is incorrect")
        if any(
            name.startswith(("skills/", ".codex-plugin/", ".claude-plugin/"))
            for name in payloads
        ):
            raise SystemExit("standalone contains nested skills or host manifests")
        for required in (
            "SKILL.md", "references/", "scripts/", "templates/",
            "internal-procedures/audit-state.md",
            "internal-procedures/audit-assess.md",
            "internal-procedures/audit-implement.md",
            "internal-procedures/audit-andon.md",
        ):
            if required.endswith("/"):
                present = any(name.startswith(required) for name in payloads)
            else:
                present = required in payloads
            if not present:
                raise SystemExit(f"standalone is missing {required}")
        skill_documents = [name for name in payloads if PurePosixPath(name).name == "SKILL.md"]
        if skill_documents != ["SKILL.md"]:
            raise SystemExit("standalone must expose exactly one discoverable governor SKILL.md")
        observed_procedures = sorted(
            name for name in payloads if name.startswith("internal-procedures/")
        )
        expected_procedures = sorted(
            f"internal-procedures/{name}.md" for name in expected_required_skills[1:]
        )
        if observed_procedures != expected_procedures:
            raise SystemExit("standalone internal procedure projection is not exact")
        for name in observed_procedures:
            procedure = payloads[name]
            if procedure.startswith(b"---\n"):
                raise SystemExit("standalone internal procedure must not retain skill frontmatter")
            if re.search(rb"\.\.[\\/]+implementaudit[\\/]+", procedure):
                raise SystemExit(
                    f"standalone internal procedure retains plugin-relative owner path: {name}"
                )
            skill_name = PurePosixPath(name).stem
            source_text = (
                source_root / "skills" / skill_name / "SKILL.md"
            ).read_text(encoding="utf-8").replace("\r\n", "\n")
            projected_text, count = re.subn(
                r"\A---\n.*?\n---\n+", "", source_text, count=1, flags=re.S
            )
            projected_text = re.sub(
                r"\.\.[\\/]+implementaudit[\\/]+"
                r"((?:references|scripts|templates)[\\/]+[^`\r\n]+)",
                lambda match: "../" + match.group(1).replace("\\", "/"),
                projected_text,
            )
            if count != 1 or procedure != projected_text.encode("utf-8"):
                raise SystemExit(f"standalone projection is stale or non-deterministic: {name}")
            for relative in re.findall(
                r"`(\.\./(?:references|scripts|templates)/[^`]+)`",
                procedure.decode("utf-8"),
            ):
                resolved = posixpath.normpath(
                    posixpath.join(PurePosixPath(name).parent.as_posix(), relative)
                )
                if resolved not in payloads:
                    raise SystemExit(
                        f"standalone internal procedure reference is unreachable: {name} -> {relative}"
                    )

    return embedded_package


canonical_package = validate_archive(canonical_path, "canonical_plugin")
standalone_package = validate_archive(
    standalone_path, "standalone_compatibility"
)
if canonical_package != standalone_package:
    raise SystemExit("embedded package identities disagree between artifacts")
PY
}

verify_artifact() {
  local role="$1" path="$2" clean="${3:-}"
  local args=(--verify-artifact "$role" "$path")
  [ "$clean" != clean ] || args+=(--require-clean-source)
  bash "$checker" "${args[@]}" \
    || fail "checker rejected clean $role artifact"
}

expect_reject() {
  local label="$1" role="$2" path="$3" clean="${4:-}"
  local args=(--verify-artifact "$role" "$path")
  [ "$clean" != clean ] || args+=(--require-clean-source)
  if bash "$checker" "${args[@]}" \
      >"$tmp/check-$label.log" 2>&1; then
    fail "checker accepted negative artifact: $label"
  fi
}

mutate_archive() {
  local operation="$1" source="$2" target="$3"
  "${py_cmd[@]}" - "$operation" "$source" "$target" <<'PY'
import hashlib
import json
import stat
import sys
import zipfile
from pathlib import Path

operation, source_arg, target_arg = sys.argv[1:]
source = Path(source_arg)
target = Path(target_arg)

with zipfile.ZipFile(source) as archive:
    rows = {
        info.filename: (info, archive.read(info.filename))
        for info in archive.infolist()
    }

if operation == "missing-member":
    del rows["skills/audit-state/SKILL.md"]
elif operation == "extra-member":
    rows["UNDECLARED.txt"] = (None, b"undeclared\n")
elif operation == "hash-mismatch":
    info, data = rows["SKILL.md"]
    rows["SKILL.md"] = (info, data + b"\nmutation\n")
elif operation == "changed-manifest":
    info, data = rows["IMPLEMENTAUDIT_PACKAGE.json"]
    rows["IMPLEMENTAUDIT_PACKAGE.json"] = (info, data + b"\n")
elif operation == "extra-child":
    rows["skills/invented/SKILL.md"] = (None, b"---\nname: invented\n---\n")
elif operation == "missing-projection":
    del rows["internal-procedures/audit-state.md"]
elif operation == "stale-projection":
    projection = "internal-procedures/audit-state.md"
    info, _data = rows[projection]
    replacement = rows["internal-procedures/audit-assess.md"][1]
    rows[projection] = (info, replacement)
    inventory_info, inventory_data = rows["IMPLEMENTAUDIT_INVENTORY.json"]
    inventory = json.loads(inventory_data.decode("utf-8"))
    for member in inventory["members"]:
        if member["path"] == projection:
            member["bytes"] = len(replacement)
            member["sha256"] = hashlib.sha256(replacement).hexdigest()
            break
    else:
        raise SystemExit("test fixture could not find projection inventory row")
    rows["IMPLEMENTAUDIT_INVENTORY.json"] = (
        inventory_info,
        (json.dumps(inventory, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
else:
    raise SystemExit(f"unknown mutation: {operation}")


def canonical_info(name, original):
    timestamp = original.date_time if original else (1980, 1, 1, 0, 0, 0)
    info = zipfile.ZipInfo(name, date_time=timestamp)
    info.create_system = 3
    info.create_version = 20
    info.extract_version = 20
    if original:
        info.external_attr = original.external_attr
    else:
        info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.internal_attr = 0
    info.compress_type = zipfile.ZIP_DEFLATED
    info.flag_bits = 0
    info.extra = b""
    info.comment = b""
    return info


with zipfile.ZipFile(
    target, "w", compression=zipfile.ZIP_DEFLATED, strict_timestamps=True
) as archive:
    for name in sorted(rows):
        original, data = rows[name]
        archive.writestr(canonical_info(name, original), data)
PY
}

clone_candidate clean-a
clone_candidate clean-b
build_candidate clean-a UTC
build_candidate clean-b America/New_York

validate_pair "$tmp/checkout-clean-a" "$tmp/out-clean-a" clean
validate_pair "$tmp/checkout-clean-b" "$tmp/out-clean-b" clean

for artifact in IMPLEMENTAUDIT.plugin.zip IMPLEMENTAUDIT.skill; do
  cmp -s "$tmp/out-clean-a/$artifact" "$tmp/out-clean-b/$artifact" \
    || fail "$artifact is not deterministic across clean builds"
done
cmp -s "$tmp/out-clean-a/CHECKSUMS.txt" "$tmp/out-clean-b/CHECKSUMS.txt" \
  || fail "CHECKSUMS.txt is not deterministic across clean builds"

for mutation in missing extra duplicate; do
  cp "$tmp/out-clean-a/CHECKSUMS.txt" "$tmp/CHECKSUMS-$mutation.txt"
  case "$mutation" in
    missing) sed -i '1d' "$tmp/CHECKSUMS-$mutation.txt" ;;
    extra) printf 'sha256  %064d  UNDECLARED.zip\n' 0 >> "$tmp/CHECKSUMS-$mutation.txt" ;;
    duplicate) head -n 1 "$tmp/CHECKSUMS-$mutation.txt" >> "$tmp/CHECKSUMS-$mutation.txt" ;;
  esac
  if bash "$tmp/checkout-clean-a/scripts/write-release-checksums.sh" \
      --check --all "$tmp/out-clean-a" "$tmp/CHECKSUMS-$mutation.txt" \
      >"$tmp/checksums-$mutation.log" 2>&1; then
    fail "checksum checker accepted a $mutation release-set row"
  fi
done

verify_artifact canonical_plugin \
  "$tmp/out-clean-a/IMPLEMENTAUDIT.plugin.zip"
verify_artifact standalone_compatibility \
  "$tmp/out-clean-a/IMPLEMENTAUDIT.skill"

clone_candidate dirty
printf '\n' >> "$tmp/checkout-dirty/skills/implementaudit/SKILL.md"
[ -n "$(git -C "$tmp/checkout-dirty" status --porcelain)" ] \
  || fail "dirty candidate was not marked dirty"
build_candidate dirty UTC
validate_pair "$tmp/checkout-dirty" "$tmp/out-dirty" dirty
expect_reject dirty-canonical canonical_plugin \
  "$tmp/out-dirty/IMPLEMENTAUDIT.plugin.zip" clean
expect_reject dirty-standalone standalone_compatibility \
  "$tmp/out-dirty/IMPLEMENTAUDIT.skill" clean

canonical="$tmp/out-clean-a/IMPLEMENTAUDIT.plugin.zip"
standalone="$tmp/out-clean-a/IMPLEMENTAUDIT.skill"

mkdir -p "$tmp/missing-member" "$tmp/extra-member" "$tmp/hash-mismatch" \
  "$tmp/changed-manifest" "$tmp/extra-child" "$tmp/missing-projection" \
  "$tmp/stale-projection"
mutate_archive missing-member "$canonical" \
  "$tmp/missing-member/IMPLEMENTAUDIT.plugin.zip"
expect_reject missing-member canonical_plugin \
  "$tmp/missing-member/IMPLEMENTAUDIT.plugin.zip"

mutate_archive extra-member "$standalone" \
  "$tmp/extra-member/IMPLEMENTAUDIT.skill"
expect_reject extra-member standalone_compatibility \
  "$tmp/extra-member/IMPLEMENTAUDIT.skill"

mutate_archive hash-mismatch "$standalone" \
  "$tmp/hash-mismatch/IMPLEMENTAUDIT.skill"
expect_reject hash-mismatch standalone_compatibility \
  "$tmp/hash-mismatch/IMPLEMENTAUDIT.skill"

mutate_archive changed-manifest "$canonical" \
  "$tmp/changed-manifest/IMPLEMENTAUDIT.plugin.zip"
expect_reject changed-manifest canonical_plugin \
  "$tmp/changed-manifest/IMPLEMENTAUDIT.plugin.zip"

mutate_archive extra-child "$canonical" \
  "$tmp/extra-child/IMPLEMENTAUDIT.plugin.zip"
expect_reject extra-child canonical_plugin \
  "$tmp/extra-child/IMPLEMENTAUDIT.plugin.zip"

mutate_archive missing-projection "$standalone" \
  "$tmp/missing-projection/IMPLEMENTAUDIT.skill"
expect_reject missing-projection standalone_compatibility \
  "$tmp/missing-projection/IMPLEMENTAUDIT.skill"

mutate_archive stale-projection "$standalone" \
  "$tmp/stale-projection/IMPLEMENTAUDIT.skill"
expect_reject stale-projection standalone_compatibility \
  "$tmp/stale-projection/IMPLEMENTAUDIT.skill"

printf 'plugin-release-asset.test: ok commit=%s tree=%s\n' \
  "$source_commit" "$source_tree"
