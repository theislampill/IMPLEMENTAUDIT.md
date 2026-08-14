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
  local mode="${1:-}" previous_identity="${2:-}" candidate_identity="" current_public_receipt="" release_commit="" check_root="" candidate_asset=""
  if [ "$mode" = "family-forward" ] || [ "$mode" = "cross-family-forward" ]; then
    candidate_identity="${3:-}"
    release_commit="${4:-}"
    check_root="${5:-$repo_root}"
    candidate_asset="${6:-$check_root/$asset_name}"
    [ -n "$previous_identity" ] && [ -n "$candidate_identity" ] && [ -n "$release_commit" ] \
      || fail "--check-release-identity $mode requires <previous-tag> <candidate-tag> <release-commit> [repo-root] [candidate-asset]"
  elif [ "$mode" = "same-tag-correction" ]; then
    candidate_identity="$previous_identity"
    current_public_receipt="${3:-}"
    release_commit="${4:-}"
    check_root="${5:-$repo_root}"
    candidate_asset="${6:-$check_root/$asset_name}"
    [ -n "$candidate_identity" ] && [ -n "$current_public_receipt" ] && [ -n "$release_commit" ] \
      || fail "--check-release-identity same-tag-correction requires <public-tag> <current-public-receipt> <release-commit> [repo-root] [candidate-asset]"
  else
    release_commit="${3:-}"
    check_root="${4:-$repo_root}"
    candidate_asset="${5:-$check_root/$asset_name}"
    [ -n "$mode" ] && [ -n "$previous_identity" ] && [ -n "$release_commit" ] \
      || fail "--check-release-identity requires <forward|republish> <previous-version> <release-commit> [repo-root] [candidate-asset]"
  fi
  "${py_cmd[@]}" - "$mode" "$previous_identity" "$candidate_identity" "$current_public_receipt" "$release_commit" "$check_root" "$candidate_asset" <<'PY'
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

mode, previous_identity, candidate_identity, receipt_arg, release_commit, root_arg, candidate_arg = sys.argv[1:]
root = Path(root_arg).resolve()
if mode not in {"forward", "republish", "family-forward", "cross-family-forward", "same-tag-correction"}:
    raise SystemExit(
        "prospective release identity mode must be forward, republish, "
        "family-forward, cross-family-forward, or same-tag-correction"
    )

plugin_path = root / ".claude-plugin" / "plugin.json"
skill_path = root / "skills" / "implementaudit" / "SKILL.md"
changelog_path = root / "CHANGELOG.md"
for path in (plugin_path, skill_path, changelog_path):
    if not path.is_file():
        raise SystemExit(f"release identity owner is missing: {path}")
portal_path = root / "docs" / "portal" / "site.json"

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


heading_values = re.findall(
    r"(?m)^## \[v?([0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?)(?: [^\]]+)?\]",
    changelog_path.read_text(encoding="utf-8"),
)
headings = [
    normalized_heading(value)
    for value in heading_values
]
distinct_headings = list(dict.fromkeys(headings))
if not distinct_headings:
    raise SystemExit("CHANGELOG.md has no published version heading")
if mode in {"family-forward", "cross-family-forward", "same-tag-correction"}:
    if not portal_path.is_file():
        raise SystemExit(f"release identity owner is missing: {portal_path}")
    portal_release = json.loads(portal_path.read_text(encoding="utf-8")).get("release", {})
    portal_milestone = str(portal_release.get("milestone", "")).strip()
    if candidate_identity != portal_milestone:
        raise SystemExit(
            f"{mode} candidate tag {candidate_identity!r} != "
            f"docs/portal/site.json milestone {portal_milestone!r}"
        )
    portal_ledger = str(portal_release.get("audit_ledger_url", "")).strip()
    ledger_name = portal_ledger.rstrip("/").rsplit("/", 1)[-1]
    expected_ledger_name = f"{candidate_identity}-release-report.md"
    if ledger_name != expected_ledger_name:
        raise SystemExit(
            f"docs/portal/site.json audit ledger must name a non-placeholder "
            f"{candidate_identity} markdown ledger"
        )
    changelog_text = changelog_path.read_text(encoding="utf-8")
    candidate_heading = re.compile(
        rf"(?m)^## \[{re.escape(candidate_identity)}\](?:\s+-\s+[^\n]+)?\s*$"
    )
    if not candidate_heading.search(changelog_text):
        raise SystemExit("CHANGELOG.md does not contain exact candidate release heading")
    public_headings = list(dict.fromkeys(f"v{value}" for value in heading_values if value.count(".") == 3))
    if not public_headings or public_headings[0] != candidate_identity:
        raise SystemExit(f"{mode} candidate tag must be the first public CHANGELOG heading")

if mode in {"family-forward", "cross-family-forward"}:
    public_tag_pattern = re.compile(r"v([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)")
    previous_match = public_tag_pattern.fullmatch(previous_identity)
    candidate_match = public_tag_pattern.fullmatch(candidate_identity)
    if not previous_match or not candidate_match:
        raise SystemExit("family-forward release identities must be v-prefixed with four numeric components")
    previous_family = ".".join(previous_match.groups()[:3])
    candidate_family = ".".join(candidate_match.groups()[:3])
    if mode == "family-forward" and (
            previous_family != plugin_version or candidate_family != plugin_version):
        raise SystemExit(
            f"family-forward tags must remain in runtime family {plugin_version}: "
            f"previous={previous_identity!r} candidate={candidate_identity!r}"
        )
    if mode == "cross-family-forward" and candidate_family != plugin_version:
        raise SystemExit(
            f"cross-family-forward candidate tag must project runtime {plugin_version}: "
            f"candidate={candidate_identity!r}"
        )
    if mode == "cross-family-forward" and previous_family == candidate_family:
        raise SystemExit("cross-family-forward must change the runtime family")
    if candidate_identity == previous_identity:
        raise SystemExit("family-forward candidate tag must differ from the previous public tag")
    if mode == "family-forward" and candidate_match.group(4) == "0":
        raise SystemExit("family-forward candidate tag must use a non-zero fourth component")
    if mode == "family-forward" and int(candidate_match.group(4)) <= int(previous_match.group(4)):
        raise SystemExit("family-forward candidate fourth component must be greater than the previous tag")
    if mode == "cross-family-forward":
        previous_runtime = tuple(int(value) for value in previous_match.groups()[:3])
        candidate_runtime = tuple(int(value) for value in candidate_match.groups()[:3])
        if candidate_runtime <= previous_runtime:
            raise SystemExit("cross-family-forward candidate runtime family must be greater than the predecessor")
        if candidate_match.group(4) != "0":
            raise SystemExit("cross-family-forward candidate tag must start the runtime family at fourth component zero")
    prior_public_headings = [value for value in public_headings if value != candidate_identity]
    authoritative_previous = prior_public_headings[0] if prior_public_headings else ""
elif mode == "same-tag-correction":
    if candidate_identity != "v0.3.3.3":
        raise SystemExit("same-tag correction is bounded to public tag v0.3.3.3")
    if plugin_version != "0.3.3":
        raise SystemExit("same-tag correction is bounded to runtime 0.3.3")
    authoritative_previous = ""
elif mode == "forward":
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", previous_identity):
        raise SystemExit("forward previous version must use three numeric components")
    candidates = [value for value in distinct_headings if value != plugin_version]
    authoritative_previous = candidates[0] if candidates else ""
else:
    authoritative_previous = distinct_headings[0]
if mode != "same-tag-correction" and previous_identity != authoritative_previous:
    raise SystemExit(
        f"declared previous identity {previous_identity!r} != CHANGELOG authority {authoritative_previous!r}"
    )

current_public_digest = ""
current_public_bytes = 0
if mode == "same-tag-correction":
    receipt_path = Path(receipt_arg)
    if not receipt_path.is_absolute():
        receipt_path = root / receipt_path
    canonical_receipt_relpath = (
        "fixtures/release-identity/current-public-v0.3.3.3.json"
    )
    canonical_receipt_path = root / canonical_receipt_relpath
    if receipt_path.resolve() != canonical_receipt_path.resolve():
        raise SystemExit(
            "same-tag correction current-public receipt must use canonical "
            f"repository custody at {canonical_receipt_relpath}"
        )
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise SystemExit("same-tag correction current-public receipt must be a regular non-symlink JSON file")

    def reject_duplicate_key(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate object key {key!r}")
            result[key] = value
        return result

    try:
        receipt = json.loads(
            receipt_path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_key,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-standard constant {value!r}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"same-tag correction current-public receipt is invalid: {exc}") from exc

    expected_receipt_keys = {
        "schema_version",
        "kind",
        "release_tag",
        "release_id",
        "asset_name",
        "asset_id",
        "api_bytes",
        "api_digest",
        "download_bytes",
        "download_sha256",
    }
    if not isinstance(receipt, dict) or set(receipt) != expected_receipt_keys:
        raise SystemExit("same-tag correction current-public receipt has the wrong schema")
    if (
        isinstance(receipt["schema_version"], bool)
        or receipt["schema_version"] != 1
        or receipt["kind"] != "implementaudit-public-release-asset-readback"
    ):
        raise SystemExit("same-tag correction current-public receipt has the wrong schema identity")
    if receipt["release_tag"] != candidate_identity:
        raise SystemExit("same-tag correction current-public receipt names the wrong release tag")
    if receipt["asset_name"] != "IMPLEMENTAUDIT.skill":
        raise SystemExit("same-tag correction current-public receipt names the wrong asset")
    for field in ("release_id", "asset_id", "api_bytes", "download_bytes"):
        value = receipt[field]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise SystemExit(f"same-tag correction current-public receipt field {field} must be a positive integer")
    api_digest = receipt["api_digest"]
    download_digest = receipt["download_sha256"]
    api_match = re.fullmatch(r"sha256:([0-9a-f]{64})", api_digest) if isinstance(api_digest, str) else None
    if not api_match or not isinstance(download_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", download_digest):
        raise SystemExit("same-tag correction current-public receipt has an invalid digest")
    current_public_digest = api_match.group(1)
    current_public_bytes = receipt["api_bytes"]
    if current_public_digest != download_digest or current_public_bytes != receipt["download_bytes"]:
        raise SystemExit("same-tag correction current-public API and download readbacks disagree")

resolved = subprocess.run(
    ["git", "-C", str(root), "rev-parse", "--verify", f"{release_commit}^{{commit}}"],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
if resolved.returncode != 0:
    raise SystemExit("release identity commit does not resolve")
commit_sha = resolved.stdout.strip()
parent_sha = ""
if mode in {"same-tag-correction", "cross-family-forward"}:
    resolved_parent = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", f"{commit_sha}^1^{{commit}}"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if resolved_parent.returncode != 0:
        raise SystemExit(f"{mode} release commit must have a first parent")
    parent_sha = resolved_parent.stdout.strip()
owner_relpaths = [
    ".claude-plugin/plugin.json",
    "skills/implementaudit/SKILL.md",
    "CHANGELOG.md",
]
if mode in {"family-forward", "cross-family-forward", "same-tag-correction"}:
    owner_relpaths.append("docs/portal/site.json")
if mode == "same-tag-correction":
    owner_relpaths.append(canonical_receipt_relpath)
for owner_relpath in owner_relpaths:
    committed_owner = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit_sha}:{owner_relpath}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if committed_owner.returncode != 0:
        raise SystemExit(
            f"release identity owner {owner_relpath} is missing from release commit {commit_sha}"
        )
    if (root / owner_relpath).read_bytes() != committed_owner.stdout:
        raise SystemExit(
            f"release identity owner {owner_relpath} does not match release commit {commit_sha}"
        )
if mode == "same-tag-correction":
    parent_receipt = subprocess.run(
        ["git", "-C", str(root), "show", f"{parent_sha}:{canonical_receipt_relpath}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if parent_receipt.returncode != 0:
        raise SystemExit(
            "same-tag correction current-public receipt must be retained in the "
            "release commit first parent"
        )
    if parent_receipt.stdout != receipt_path.read_bytes():
        raise SystemExit(
            "same-tag correction current-public receipt must remain byte-identical "
            "from the release commit first parent"
        )
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
if mode in {"same-tag-correction", "cross-family-forward"}:
    head_commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD^{commit}"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    if commit_sha != head_commit:
        raise SystemExit(f"{mode} release commit must equal current HEAD")

if mode == "cross-family-forward":
    parent_versions = []
    for owner_relpath in (".claude-plugin/plugin.json", "skills/implementaudit/SKILL.md"):
        parent_owner = subprocess.run(
            ["git", "-C", str(root), "show", f"{parent_sha}:{owner_relpath}"],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")
        if owner_relpath.endswith("plugin.json"):
            parent_versions.append(str(json.loads(parent_owner).get("version", "")).strip())
        else:
            parent_match = re.search(
                r'(?m)^\s+version:\s*["\']?([^"\'\n]+)["\']?\s*$', parent_owner)
            if not parent_match:
                raise SystemExit("cross-family-forward predecessor SKILL.md metadata.version is missing")
            parent_versions.append(parent_match.group(1).strip())
    if parent_versions != [previous_family, previous_family]:
        raise SystemExit(
            "cross-family-forward predecessor plugin/SKILL runtime does not "
            f"match public family {previous_family!r}: {parent_versions!r}"
        )
    print(
        f"build-release-asset: release identity cross-family-forward "
        f"{previous_identity}/{previous_family} -> "
        f"{candidate_identity}/{plugin_version} at {commit_sha}"
    )
    raise SystemExit(0)

if mode == "family-forward":
    shown = subprocess.run(
        ["git", "-C", str(root), "show", "--first-parent", "--format=", "--unified=0", commit_sha, "--", "CHANGELOG.md"],
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
    same_tag_receipt = re.compile(
        r"(?im)^[ \t]*-\s+same-tag\s+correction\s+for\s+`v0\.3\.3\.3`\s+"
        r"`IMPLEMENTAUDIT\.skill`\s*:"
    )
    if same_tag_receipt.search(added):
        raise SystemExit(
            "family-forward cannot qualify a commit-added v0.3.3.3 same-tag "
            "correction receipt; use same-tag-correction"
        )
    print(
        f"build-release-asset: release identity family-forward "
        f"{previous_identity} -> {candidate_identity} (runtime {plugin_version}) at {commit_sha}"
    )
    raise SystemExit(0)

if mode == "forward":
    if plugin_version == previous_identity:
        raise SystemExit("forward release must change the prior published version")
    print(f"build-release-asset: release identity forward {previous_identity} -> {plugin_version} at {commit_sha}")
    raise SystemExit(0)

if mode == "republish" and plugin_version != previous_identity:
    raise SystemExit("same-version republication must retain the prior published version")

candidate_path = Path(candidate_arg)
if not candidate_path.is_absolute():
    candidate_path = root / candidate_path
if candidate_path.name != "IMPLEMENTAUDIT.skill":
    raise SystemExit(f"{mode} candidate must be named IMPLEMENTAUDIT.skill")
if candidate_path.is_symlink() or not candidate_path.is_file():
    raise SystemExit(f"{mode} candidate must be a regular non-symlink file")
candidate_digest = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
candidate_bytes = candidate_path.stat().st_size

shown = subprocess.run(
    ["git", "-C", str(root), "show", "--first-parent", "--format=", "--unified=0", commit_sha, "--", "CHANGELOG.md"],
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
if mode == "same-tag-correction":
    pair_patterns = {
        "historical": re.compile(
            r"^[ \t]*-\s+same-tag\s+correction\s+for\s+`v0\.3\.3\.3`\s+"
            r"`IMPLEMENTAUDIT\.skill`:\s+prematurely\s+published\s+"
            r"`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*(?:→|->)\s*"
            r"final\s+`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*\.?\s*$",
            re.IGNORECASE,
        ),
        "current": re.compile(
            r"^[ \t]*-\s+same-tag\s+correction\s+for\s+`v0\.3\.3\.3`\s+"
            r"`IMPLEMENTAUDIT\.skill`:\s+current\s+public\s+"
            r"`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*(?:→|->)\s*"
            r"candidate\s+`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*\.?\s*$",
            re.IGNORECASE,
        ),
    }

    def committed_changelog(commit):
        shown_changelog = subprocess.run(
            ["git", "-C", str(root), "show", f"{commit}:CHANGELOG.md"],
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if shown_changelog.returncode != 0:
            raise SystemExit(
                f"same-tag correction CHANGELOG.md is missing from commit {commit}"
            )
        return shown_changelog.stdout

    def correction_rows(text):
        rows = []
        for line in text.splitlines():
            for grammar, pattern in pair_patterns.items():
                match = pattern.fullmatch(line)
                if match:
                    rows.append((grammar, line, match.groups()))
                    break
        return rows

    parent_rows = correction_rows(committed_changelog(parent_sha))
    current_rows = correction_rows(committed_changelog(commit_sha))
    if (
        len(current_rows) != len(parent_rows) + 1
        or current_rows[: len(parent_rows)] != parent_rows
    ):
        raise SystemExit(
            "same-tag correction must preserve every historical correction pair "
            "and append exactly one new pair"
        )
    new_grammar, new_pair_line, new_pair = current_rows[-1]
    required_grammar = "historical" if not parent_rows else "current"
    if new_grammar != required_grammar:
        raise SystemExit(
            "same-tag correction must use prematurely-published-to-final grammar "
            "only for the first correction and current-public-to-candidate grammar "
            "for every repeated correction"
        )
    if added.splitlines().count(new_pair_line) != 1:
        raise SystemExit(
            "same-tag correction release commit must add its new canonical "
            "IMPLEMENTAUDIT.skill pair"
        )
    pairs = [new_pair]
else:
    pairs = re.findall(
        r"(?ims)^[ \t]*-\s+`IMPLEMENTAUDIT\.skill`:\s+superseded\s+"
        r"`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*(?:→|->)\s*"
        r"superseding\s+`?([0-9a-f]{64})`?\s*\(([0-9][0-9,]*)\s+bytes?\)\s*\.?\s*$",
        added,
    )
if len(pairs) != 1:
    raise SystemExit(f"{mode} commit must add exactly one IMPLEMENTAUDIT.skill digest-and-byte pair")
superseded_digest, superseded_bytes_text, superseding_digest, superseding_bytes_text = pairs[0]
if superseded_digest == superseding_digest:
    raise SystemExit(f"{mode} digest pair must name distinct payloads")
if mode == "same-tag-correction":
    superseded_bytes = int(superseded_bytes_text.replace(",", ""))
    if superseded_digest != current_public_digest or superseded_bytes != current_public_bytes:
        raise SystemExit(
            "same-tag correction pair does not match the retained current-public receipt"
        )
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
bash scripts/check-package-contract.sh
"${py_cmd[@]}" scripts/package-contract.py --build "$out_dir"
bash scripts/write-release-checksums.sh --all "$out_dir" "$out_dir/CHECKSUMS.txt"
