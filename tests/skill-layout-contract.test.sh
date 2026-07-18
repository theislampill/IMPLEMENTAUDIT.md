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
    "$dir/skills/implementaudit/references" \
    "$dir/skills/implementaudit/scripts" \
    "$dir/skills/implementaudit/templates" \
    "$dir/.claude-plugin" \
    "$dir/scripts" \
    "$dir/docs/audits"

  cat >"$dir/skills/implementaudit/SKILL.md" <<'EOF'
# /implementaudit

Source checkout layout is conventional and name-matched:
`skills/implementaudit/SKILL.md`. Release archives flatten that directory only as a build artifact.
Runtime paths use `references/routing.md`,
`scripts/claim-run.sh`, and `templates/PROTOCOL.md`.
EOF
  cat >"$dir/.claude-plugin/plugin.json" <<'EOF'
{"name":"implementaudit","version":"0.3.2","skills":"./skills/"}
EOF
  cat >"$dir/.claude-plugin/marketplace.json" <<'EOF'
{"plugins":[{"name":"implementaudit","source":"./"}]}
EOF
  cat >"$dir/scripts/build-release-asset.sh" <<'EOF'
source_skill_dir = repo / "skills" / "implementaudit"
archive_plugin["skills"] = "./"
plugin["path"] = ".."
if "skills/implementaudit/SKILL.md" in names:
EOF
  cat >"$dir/README.md" <<'EOF'
# README

Source layout vs release archive layout: source is
`skills/implementaudit/SKILL.md`; the release archive keeps SKILL.md at archive root.
EOF
  cat >"$dir/AGENTS.md" <<'EOF'
Use `skills/implementaudit/SKILL.md`. The release archive keeps SKILL.md at
archive root.
EOF
  cat >"$dir/CONTRIBUTING.md" <<'EOF'
No stale flat layout references.
EOF
}

positive="$tmp/positive"
make_minimal_repo "$positive"
bash scripts/check-skill-layout-contract.sh --repo-root "$positive"

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
Use `skills/implementaudit/SKILL.md`. The release archive keeps SKILL.md at
archive root.

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
