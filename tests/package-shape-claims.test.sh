#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# 1. The live repo must pass the doc/package-shape gate.
bash scripts/check-package-shape-claims.sh

# 2. A source manifest that returns to archive-root skills="./" must fail.
mkdir -p "$tmp/bad-manifest/.claude-plugin" "$tmp/bad-manifest/skills"
printf '{"name":"implementaudit","version":"0.3.0","skills":"./"}\n' > "$tmp/bad-manifest/.claude-plugin/plugin.json"
cat > "$tmp/bad-manifest/AGENTS.md" <<'EOF'
Source plugin metadata declares `skills: "./skills/"`.
The builder emits archive-local metadata with `skills: "./"`.
The package is a flat archive with SKILL.md at archive root.
Source payload lives under skills/implementaudit/.
EOF
if bash scripts/check-package-shape-claims.sh --scan-root "$tmp/bad-manifest" >/dev/null 2>&1; then
  printf 'package-shape-claims.test: expected archive-shaped source manifest to fail\n' >&2
  exit 1
fi

# 3. Stale docs must fail even when the manifest is correct.
mkdir -p "$tmp/bad-docs/.claude-plugin" "$tmp/bad-docs/skills"
printf '{"name":"implementaudit","version":"0.3.0","skills":"./skills/"}\n' > "$tmp/bad-docs/.claude-plugin/plugin.json"
cat > "$tmp/bad-docs/AGENTS.md" <<'EOF'
Ships to consumers: everything under `skills/`.
The artifact contains only `skills/` plus `.claude-plugin/` metadata.
It must include the `skills/` layout.
EOF
if bash scripts/check-package-shape-claims.sh --scan-root "$tmp/bad-docs" >/dev/null 2>&1; then
  printf 'package-shape-claims.test: expected stale package docs to fail\n' >&2
  exit 1
fi

# 4. Split-line stale docs must also fail.
mkdir -p "$tmp/bad-split/.claude-plugin" "$tmp/bad-split/skills" "$tmp/bad-split/docs/portal/pages"
printf '{"name":"implementaudit","version":"0.3.0","skills":"./skills/"}\n' > "$tmp/bad-split/.claude-plugin/plugin.json"
cat > "$tmp/bad-split/AGENTS.md" <<'EOF'
Source plugin metadata declares `skills: "./skills/"`.
The builder emits archive-local metadata with `skills: "./"`.
The package is a flat archive with SKILL.md at archive root.
Source payload lives under skills/implementaudit/.
EOF
cat > "$tmp/bad-split/docs/portal/pages/package-contents.html" <<'EOF'
<p>The artifact contains only repository metadata and
the old skills/ directory layout.</p>
EOF
if bash scripts/check-package-shape-claims.sh --scan-root "$tmp/bad-split" >/dev/null 2>&1; then
  printf 'package-shape-claims.test: expected split-line stale package docs to fail\n' >&2
  exit 1
fi

# 5. Bare stale archive tree docs must fail.
mkdir -p "$tmp/bad-tree/.claude-plugin"
printf '{"name":"implementaudit","version":"0.3.0","skills":"./skills/"}\n' > "$tmp/bad-tree/.claude-plugin/plugin.json"
cat > "$tmp/bad-tree/AGENTS.md" <<'EOF'
Source plugin metadata declares `skills: "./skills/"`.
The builder emits archive-local metadata with `skills: "./"`.
The package is a flat archive with SKILL.md at archive root.
Source payload lives under skills/implementaudit/.
EOF
cat > "$tmp/bad-tree/README.md" <<'EOF'
A ZIP-format archive containing the installable skill payload:

```text
skills/
.claude-plugin/
```
EOF
if bash scripts/check-package-shape-claims.sh --scan-root "$tmp/bad-tree" >/dev/null 2>&1; then
  printf 'package-shape-claims.test: expected bare stale archive tree docs to fail\n' >&2
  exit 1
fi

# 6. Source-path wording must not be described as installed package shape.
mkdir -p "$tmp/bad-source-path/.claude-plugin"
printf '{"name":"implementaudit","version":"0.3.0","skills":"./skills/"}\n' > "$tmp/bad-source-path/.claude-plugin/plugin.json"
cat > "$tmp/bad-source-path/AGENTS.md" <<'EOF'
Source plugin metadata declares `skills: "./skills/"`.
The builder emits archive-local metadata with `skills: "./"`.
The package is a flat archive with SKILL.md at archive root.
Source payload lives under skills/implementaudit/.
EOF
cat > "$tmp/bad-source-path/README.md" <<'EOF'
The package includes `skills/implementaudit/references/child-agents.md`.
The package includes `skills/implementaudit/scripts/claim-run.sh`.
Use the packaged templates under `skills/implementaudit/templates/` when available.
EOF
if bash scripts/check-package-shape-claims.sh --scan-root "$tmp/bad-source-path" >/dev/null 2>&1; then
  printf 'package-shape-claims.test: expected source-prefixed package path claims to fail\n' >&2
  exit 1
fi

# 7. Correct package-shape claims should pass in isolation.
mkdir -p "$tmp/good/.claude-plugin" "$tmp/good/skills"
printf '{"name":"implementaudit","version":"0.3.0","skills":"./skills/"}\n' > "$tmp/good/.claude-plugin/plugin.json"
cat > "$tmp/good/AGENTS.md" <<'EOF'
Source plugin metadata declares `skills: "./skills/"`.
The builder emits archive-local metadata with `skills: "./"`.
The package is a flat archive with SKILL.md at archive root.
Source payload lives under skills/implementaudit/.
EOF
cat > "$tmp/good/README.md" <<'EOF'
Source layout vs release archive layout

```text
SKILL.md
references/
scripts/
templates/
.claude-plugin/
.claude-plugin/plugin.json  (skills: "./")
```
EOF
bash scripts/check-package-shape-claims.sh --scan-root "$tmp/good"

printf 'package-shape-claims.test: ok\n'
