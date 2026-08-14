#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-package-shape-claims.sh

make_fixture() {
  local root="$1"
  mkdir -p \
    "$root/package" "$root/.codex-plugin" "$root/.claude-plugin" \
    "$root/skills/implementaudit" "$root/docs/portal/pages"
  cp package/implementaudit-package.json "$root/package/implementaudit-package.json"
  cp .codex-plugin/plugin.json "$root/.codex-plugin/plugin.json"
  cp .claude-plugin/plugin.json "$root/.claude-plugin/plugin.json"
  printf '%s\n' '---' 'name: implementaudit' '---' > "$root/skills/implementaudit/SKILL.md"
  cat > "$root/AGENTS.md" <<'EOF'
The normal release/install unit is one atomic dual-host plugin package.
The canonical generated artifact is IMPLEMENTAUDIT.plugin.zip.
IMPLEMENTAUDIT.skill is the standalone compatibility projection.
/implementaudit is the sole stable public/default governor and v0.4 has zero child skills.
Local staged-copy evidence is not native host-discovery proof.
EOF
  cat > "$root/README.md" <<'EOF'
This is one atomic dual-host plugin. IMPLEMENTAUDIT.plugin.zip is canonical.
IMPLEMENTAUDIT.skill is compatibility-only. /implementaudit is the sole stable public/default governor.
The package has zero child skills and is owned by package/implementaudit-package.json.
EOF
  cat > "$root/CONTRIBUTING.md" <<'EOF'
Package owner: package/implementaudit-package.json.
Host manifests: .codex-plugin/plugin.json and .claude-plugin/plugin.json.
Verify with --check --all dist dist/CHECKSUMS.txt.
EOF
  cat > "$root/docs/portal/site.json" <<'EOF'
{"status":"candidate; native host and marketplace behavior remain unverified"}
EOF
  cat > "$root/docs/portal/pages/package-contents.html" <<'EOF'
One atomic package, two generated projections.
IMPLEMENTAUDIT.plugin.zip is canonical; IMPLEMENTAUDIT.skill is compatibility-only.
The governor has zero child skills. Manifest presence is not evidence that marketplace discovery works.
EOF
}

expect_fail() {
  local root="$1" label="$2"
  if bash scripts/check-package-shape-claims.sh --scan-root "$root" >/dev/null 2>&1; then
    printf 'package-shape-claims.test: expected failure: %s\n' "$label" >&2
    exit 1
  fi
}

good="$tmp/good"
make_fixture "$good"
bash scripts/check-package-shape-claims.sh --scan-root "$good" >/dev/null

bad_manifest="$tmp/bad-manifest"
cp -R "$good" "$bad_manifest"
python - "$bad_manifest/.codex-plugin/plugin.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1]); d = json.loads(p.read_text()); d["skills"] = "./"; p.write_text(json.dumps(d) + "\n")
PY
expect_fail "$bad_manifest" "Codex manifest topology drift"

bad_version="$tmp/bad-version"
cp -R "$good" "$bad_version"
python - "$bad_version/.claude-plugin/plugin.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1]); d = json.loads(p.read_text()); d["version"] = "9.9.9"; p.write_text(json.dumps(d) + "\n")
PY
expect_fail "$bad_version" "dual-host version disagreement"

bad_projection="$tmp/bad-projection"
cp -R "$good" "$bad_projection"
python - "$bad_projection/package/implementaudit-package.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1]); d = json.loads(p.read_text()); d["generated_projections"]["canonical_plugin"]["layout"] = "flattened-skill"; p.write_text(json.dumps(d) + "\n")
PY
expect_fail "$bad_projection" "canonical projection flattened"

bad_child="$tmp/bad-child"
cp -R "$good" "$bad_child"
mkdir -p "$bad_child/skills/audit-review"
printf '%s\n' '---' 'name: audit-review' '---' > "$bad_child/skills/audit-review/SKILL.md"
expect_fail "$bad_child" "undeclared child skill"

bad_primary="$tmp/bad-primary"
cp -R "$good" "$bad_primary"
printf '%s\n' 'IMPLEMENTAUDIT.skill is the primary release package.' >> "$bad_primary/AGENTS.md"
expect_fail "$bad_primary" "compatibility artifact promoted to primary"

bad_host_claim="$tmp/bad-host-claim"
cp -R "$good" "$bad_host_claim"
printf '%s\n' 'Codex natively discovers the plugin.' >> "$bad_host_claim/docs/portal/pages/package-contents.html"
expect_fail "$bad_host_claim" "native host overclaim"

# Historical standalone-skill evidence is append-only and intentionally not a
# current topology owner, so it must not make the current-shape gate fail.
mkdir -p "$good/docs/audits/archive"
printf '%s\n' 'IMPLEMENTAUDIT.skill is the primary release artifact for v0.3.3.3.' \
  > "$good/docs/audits/archive/v0.3.3.3-release-report.md"
bash scripts/check-package-shape-claims.sh --scan-root "$good" >/dev/null

printf 'package-shape-claims.test: ok\n'
