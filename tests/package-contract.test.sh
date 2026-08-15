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

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

make_fixture() {
  local target="$1"
  mkdir -p "$target/package" "$target/.codex-plugin" \
    "$target/.claude-plugin" "$target/skills/implementaudit/references" \
    "$target/skills/implementaudit/scripts" "$target/skills/implementaudit/templates" \
    "$target/skills/audit-state" "$target/skills/audit-assess" \
    "$target/skills/audit-implement" "$target/skills/audit-andon"
  cp package/implementaudit-package.json "$target/package/"
  cp .codex-plugin/plugin.json "$target/.codex-plugin/"
  cp .claude-plugin/plugin.json "$target/.claude-plugin/"
  cp .claude-plugin/marketplace.json "$target/.claude-plugin/"
  local skill
  for skill in implementaudit audit-state audit-assess audit-implement audit-andon; do
    printf '%s\n' \
      '---' \
      "name: $skill" \
      'description: Package-contract fixture.' \
      'metadata:' \
      '  version: "0.4.0"' \
      '---' \
      >"$target/skills/$skill/SKILL.md"
  done
}

expect_reject() {
  local label="$1" fixture="$2" expected="$3" output
  if output="$(bash "$checker" --repo-root "$fixture" 2>&1)"; then
    fail "accepted negative fixture: $label"
  fi
  case "$output" in
    *"$expected"*) ;;
    *) fail "wrong rejection for $label: $output" ;;
  esac
}

valid="$tmp/valid"
make_fixture "$valid"
bash "$checker" --repo-root "$valid"

missing_skill="$tmp/missing-skill"
make_fixture "$missing_skill"
rm "$missing_skill/skills/audit-assess/SKILL.md"
expect_reject missing-skill "$missing_skill" "model-facing skill population"

extra_skill="$tmp/extra-skill"
make_fixture "$extra_skill"
mkdir -p "$extra_skill/skills/invented-child"
cp "$extra_skill/skills/audit-state/SKILL.md" \
  "$extra_skill/skills/invented-child/SKILL.md"
expect_reject extra-skill "$extra_skill" "model-facing skill population"

renamed_skill="$tmp/renamed-skill"
make_fixture "$renamed_skill"
mv "$renamed_skill/skills/audit-state" "$renamed_skill/skills/audit-context"
expect_reject renamed-skill "$renamed_skill" "model-facing skill population"

duplicate_required="$tmp/duplicate-required"
make_fixture "$duplicate_required"
python - "$duplicate_required/package/implementaudit-package.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["required_skills"].append("audit-implement")
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject duplicate-required "$duplicate_required" "required_skills"

duplicate_internal="$tmp/duplicate-internal"
make_fixture "$duplicate_internal"
python - "$duplicate_internal/package/implementaudit-package.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["internal_skills"].append(dict(data["internal_skills"][-1]))
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject duplicate-internal "$duplicate_internal" "internal_skills"

partial_internal="$tmp/partial-internal"
make_fixture "$partial_internal"
python - "$partial_internal/package/implementaudit-package.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["internal_skills"] = data["internal_skills"][:-1]
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject partial-internal "$partial_internal" "internal_skills"

wrong_maintainer_flag="$tmp/wrong-maintainer-flag"
make_fixture "$wrong_maintainer_flag"
python - "$wrong_maintainer_flag/package/implementaudit-package.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["internal_skills"][0]["maintainer_only"] = True
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject wrong-maintainer-flag "$wrong_maintainer_flag" "internal_skills"

wrong_direct_entry="$tmp/wrong-direct-entry"
make_fixture "$wrong_direct_entry"
python - "$wrong_direct_entry/package/implementaudit-package.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["internal_skills"][-1]["directly_invocable"] = False
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
expect_reject wrong-direct-entry "$wrong_direct_entry" "internal_skills"

independent_version="$tmp/independent-version"
make_fixture "$independent_version"
python - "$independent_version/skills/audit-assess/SKILL.md" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
path.write_text(text.replace('version: "0.4.0"', 'version: "9.9.9"'), encoding="utf-8")
PY
expect_reject independent-version "$independent_version" "audit-assess runtime version"

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
expect_reject manifest-version-drift "$wrong_version" ".codex-plugin/plugin.json content"

missing_manifest="$tmp/missing-manifest"
make_fixture "$missing_manifest"
rm "$missing_manifest/.codex-plugin/plugin.json"
expect_reject missing-codex-manifest "$missing_manifest" "missing required JSON file"

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
expect_reject missing-publisher-author "$missing_author" ".codex-plugin/plugin.json content"

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
expect_reject wrong-marketplace-owner "$wrong_owner" ".claude-plugin/marketplace.json content"

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
expect_reject post-review-cap-edit "$changed_cap" "budgets"

bash "$checker" --check-budget-size canonical_plugin 327680
bash "$checker" --check-budget-size standalone_compatibility 327680
if bash "$checker" --check-budget-size canonical_plugin 327681 >/dev/null 2>&1; then
  fail "canonical plugin overrun was accepted"
fi
if bash "$checker" --check-budget-size standalone_compatibility 327681 >/dev/null 2>&1; then
  fail "standalone compatibility overrun was accepted"
fi

printf 'package-contract.test: ok\n'
