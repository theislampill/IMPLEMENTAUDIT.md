#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'package-contract.test: %s\n' "$*" >&2
  exit 1
}

checker="scripts/check-package-contract.sh"
[ -x "$checker" ] || fail "canonical package-contract checker is absent"

bash "$checker"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

make_fixture() {
  local target="$1"
  mkdir -p "$target/package" "$target/.codex-plugin" \
    "$target/.claude-plugin" "$target/skills/implementaudit/references" \
    "$target/skills/implementaudit/scripts" "$target/skills/implementaudit/templates"
  cp package/implementaudit-package.json "$target/package/"
  cp .codex-plugin/plugin.json "$target/.codex-plugin/"
  cp .claude-plugin/plugin.json "$target/.claude-plugin/"
  cp .claude-plugin/marketplace.json "$target/.claude-plugin/"
  cp skills/implementaudit/SKILL.md "$target/skills/implementaudit/"
}

expect_reject() {
  local label="$1" fixture="$2"
  if bash "$checker" --repo-root "$fixture" >/dev/null 2>&1; then
    fail "accepted negative fixture: $label"
  fi
}

valid="$tmp/valid"
make_fixture "$valid"
bash "$checker" --repo-root "$valid"

python - "$valid/package/implementaudit-package.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["required_skills"].append("invented-child")
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject child-population "$valid"

wrong_version="$tmp/wrong-version"
make_fixture "$wrong_version"
python - "$wrong_version/.codex-plugin/plugin.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["version"] = "9.9.9"
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject manifest-version-drift "$wrong_version"

missing_manifest="$tmp/missing-manifest"
make_fixture "$missing_manifest"
rm "$missing_manifest/.codex-plugin/plugin.json"
expect_reject missing-codex-manifest "$missing_manifest"

missing_author="$tmp/missing-author"
make_fixture "$missing_author"
python - "$missing_author/.codex-plugin/plugin.json" \
  "$missing_author/.claude-plugin/plugin.json" <<'PY'
import json
import pathlib
import sys

for raw_path in sys.argv[1:]:
    path = pathlib.Path(raw_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data.pop("author", None)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject missing-publisher-author "$missing_author"

wrong_owner="$tmp/wrong-marketplace-owner"
make_fixture "$wrong_owner"
python - "$wrong_owner/.claude-plugin/marketplace.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["owner"] = {"name": "unbound-owner"}
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject wrong-marketplace-owner "$wrong_owner"

changed_cap="$tmp/changed-cap"
make_fixture "$changed_cap"
python - "$changed_cap/package/implementaudit-package.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["budgets"]["canonical_plugin"]["cap_bytes"] = 400000
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject post-review-cap-edit "$changed_cap"

bash "$checker" --check-budget-size canonical_plugin 327680
bash "$checker" --check-budget-size standalone_compatibility 327680
if bash "$checker" --check-budget-size canonical_plugin 327681 >/dev/null 2>&1; then
  fail "canonical plugin overrun was accepted"
fi
if bash "$checker" --check-budget-size standalone_compatibility 327681 >/dev/null 2>&1; then
  fail "standalone compatibility overrun was accepted"
fi

printf 'package-contract.test: ok\n'
