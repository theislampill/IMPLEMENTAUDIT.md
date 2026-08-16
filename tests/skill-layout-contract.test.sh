#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-skill-layout-contract.sh

make_minimal_repo() {
  local dir="$1"
  mkdir -p \
    "$dir/skills/audit-state" \
    "$dir/skills/audit-assess" \
    "$dir/skills/audit-implement" \
    "$dir/skills/audit-andon" \
    "$dir/skills/implementaudit/references" \
    "$dir/skills/implementaudit/scripts" \
    "$dir/skills/implementaudit/templates" \
    "$dir/.codex-plugin" \
    "$dir/.claude-plugin" \
    "$dir/scripts" \
    "$dir/docs/audits"

  cat >"$dir/skills/implementaudit/SKILL.md" <<'EOF'
---
name: implementaudit
description: Fixture governor.
metadata:
  version: "0.4.0"
---

# /implementaudit

Source checkout layout is conventional and name-matched:
`skills/implementaudit/SKILL.md`. Release archives flatten that directory only as a build artifact.
Runtime paths use `references/routing.md`,
`scripts/claim-run.sh`, and `templates/PROTOCOL.md`.
EOF
  cat >"$dir/skills/audit-state/SKILL.md" <<'EOF'
---
name: audit-state
description: Internal bounded state-recovery cognition routed by /implementaudit.
metadata:
  version: "0.4.0"
---
EOF
  cat >"$dir/skills/audit-assess/SKILL.md" <<'EOF'
---
name: audit-assess
description: Internal bounded independent assessment routed by /implementaudit.
metadata:
  version: "0.4.0"
---
EOF
  cat >"$dir/skills/audit-implement/SKILL.md" <<'EOF'
---
name: audit-implement
description: Internal maintainer qualification cognition routed by /implementaudit.
metadata:
  version: "0.4.0"
---
EOF
  cat >"$dir/skills/audit-andon/SKILL.md" <<'EOF'
---
name: audit-andon
description: Bounded Andon-response cognition.
metadata:
  version: "0.4.0"
---
EOF
  cat >"$dir/.claude-plugin/plugin.json" <<'EOF'
{"name":"implementaudit","version":"0.3.2","skills":"./skills/","author":{"name":"theislampill"}}
EOF
  cp "$dir/.claude-plugin/plugin.json" "$dir/.codex-plugin/plugin.json"
  cat >"$dir/.claude-plugin/marketplace.json" <<'EOF'
{"name":"implementaudit","owner":{"name":"theislampill"},"description":"Audit package.","plugins":[{"name":"implementaudit","source":"./"}]}
EOF
  cat >"$dir/scripts/build-release-asset.sh" <<'EOF'
scripts/package-contract.py --build "$out_dir"
EOF
  cat >"$dir/README.md" <<'EOF'
# README

Source layout vs release package projections: source is
`skills/implementaudit/SKILL.md`; `IMPLEMENTAUDIT.plugin.zip` preserves the
source tree and `IMPLEMENTAUDIT.skill` flattens it to archive-root `SKILL.md`.
EOF
  cat >"$dir/AGENTS.md" <<'EOF'
Use `skills/implementaudit/SKILL.md`. `IMPLEMENTAUDIT.plugin.zip` preserves the
source tree; `IMPLEMENTAUDIT.skill` flattens it to archive root as `SKILL.md`.
EOF
  cat >"$dir/CONTRIBUTING.md" <<'EOF'
No stale flat layout references.
EOF
}

positive="$tmp/positive"
make_minimal_repo "$positive"
bash scripts/check-skill-layout-contract.sh --repo-root "$positive"

missing_child="$tmp/missing-child"
make_minimal_repo "$missing_child"
rm "$missing_child/skills/audit-andon/SKILL.md"
if bash scripts/check-skill-layout-contract.sh --repo-root "$missing_child" \
    >"$tmp/missing-child.out" 2>&1; then
  printf 'skill-layout-contract.test: missing child unexpectedly passed\n' >&2
  exit 1
fi
grep -F "expected exact source skill population" "$tmp/missing-child.out" >/dev/null || {
  printf 'skill-layout-contract.test: expected missing-child population diagnostic\n' >&2
  cat "$tmp/missing-child.out" >&2
  exit 1
}

extra_child="$tmp/extra-child"
make_minimal_repo "$extra_child"
mkdir -p "$extra_child/skills/invented-child"
cp "$extra_child/skills/audit-state/SKILL.md" "$extra_child/skills/invented-child/SKILL.md"
if bash scripts/check-skill-layout-contract.sh --repo-root "$extra_child" \
    >"$tmp/extra-child.out" 2>&1; then
  printf 'skill-layout-contract.test: extra child unexpectedly passed\n' >&2
  exit 1
fi
grep -F "expected exact source skill population" "$tmp/extra-child.out" >/dev/null || {
  printf 'skill-layout-contract.test: expected extra-child population diagnostic\n' >&2
  cat "$tmp/extra-child.out" >&2
  exit 1
}

flat="$tmp/flat"
make_minimal_repo "$flat"
cat >"$flat/skills/SKILL.md" <<'EOF'
# stale flat source
EOF
if bash scripts/check-skill-layout-contract.sh --repo-root "$flat" >"$tmp/flat.out" 2>&1; then
  printf 'skill-layout-contract.test: stale flat source unexpectedly passed\n' >&2
  exit 1
fi
grep -F "flat canonical source skill file must not exist" "$tmp/flat.out" >/dev/null || {
  printf 'skill-layout-contract.test: expected flat-layout diagnostic\n' >&2
  cat "$tmp/flat.out" >&2
  exit 1
}

source_manifest="$tmp/source-manifest"
make_minimal_repo "$source_manifest"
cat >"$source_manifest/.claude-plugin/plugin.json" <<'EOF'
{"name":"implementaudit","version":"0.3.2","skills":"./"}
EOF
if bash scripts/check-skill-layout-contract.sh --repo-root "$source_manifest" >"$tmp/source-manifest.out" 2>&1; then
  printf 'skill-layout-contract.test: archive-shaped source manifest unexpectedly passed\n' >&2
  exit 1
fi
grep -F "must point source plugin discovery at ./skills/" "$tmp/source-manifest.out" >/dev/null || {
  printf 'skill-layout-contract.test: expected source-manifest diagnostic\n' >&2
  cat "$tmp/source-manifest.out" >&2
  exit 1
}

marketplace_owner="$tmp/marketplace-owner"
make_minimal_repo "$marketplace_owner"
python - "$marketplace_owner/.claude-plugin/marketplace.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["owner"] = {"name": "unbound-owner"}
path.write_text(json.dumps(data) + "\n", encoding="utf-8")
PY
if bash scripts/check-skill-layout-contract.sh --repo-root "$marketplace_owner" \
    >"$tmp/marketplace-owner.out" 2>&1; then
  printf 'skill-layout-contract.test: unbound marketplace owner unexpectedly passed\n' >&2
  exit 1
fi
grep -F "marketplace owner must be theislampill" "$tmp/marketplace-owner.out" >/dev/null || {
  printf 'skill-layout-contract.test: expected marketplace-owner diagnostic\n' >&2
  cat "$tmp/marketplace-owner.out" >&2
  exit 1
}

payload="$tmp/payload"
make_minimal_repo "$payload"
printf '\\nBad installed path: skills/implementaudit/references/routing.md\\n' >>"$payload/skills/implementaudit/SKILL.md"
if bash scripts/check-skill-layout-contract.sh --repo-root "$payload" >"$tmp/payload.out" 2>&1; then
  printf 'skill-layout-contract.test: source-relative payload path unexpectedly passed\n' >&2
  exit 1
fi
grep -F "must use installed-relative payload paths" "$tmp/payload.out" >/dev/null || {
  printf 'skill-layout-contract.test: expected payload-path diagnostic\n' >&2
  cat "$tmp/payload.out" >&2
  exit 1
}

tree="$tmp/tree"
make_minimal_repo "$tree"
cat >"$tree/AGENTS.md" <<'EOF'
Use `skills/implementaudit/SKILL.md`. `IMPLEMENTAUDIT.plugin.zip` preserves the
source tree; `IMPLEMENTAUDIT.skill` flattens it to archive root as `SKILL.md`.

## Repo layout

```
/
└── skills/
    ├── SKILL.md                Canonical skill source.
    ├── references/             Progressive-disclosure docs.
    ├── scripts/                Runtime helpers.
    └── templates/              Runtime templates.
```
EOF
if bash scripts/check-skill-layout-contract.sh --repo-root "$tree" >"$tmp/tree.out" 2>&1; then
  printf 'skill-layout-contract.test: flat repo-layout tree unexpectedly passed\n' >&2
  exit 1
fi
grep -F "repo layout tree shows flat skill payload directly under skills/" "$tmp/tree.out" >/dev/null || {
  printf 'skill-layout-contract.test: expected flat repo-layout tree diagnostic\n' >&2
  cat "$tmp/tree.out" >&2
  exit 1
}

printf 'skill-layout-contract.test: ok\n'
