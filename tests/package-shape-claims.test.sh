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
    "$root/skills/implementaudit" "$root/skills/audit-state" \
    "$root/skills/audit-assess" "$root/skills/audit-implement" \
    "$root/skills/audit-andon" \
    "$root/docs/portal/pages"
  cp package/implementaudit-package.json "$root/package/implementaudit-package.json"
  cp .codex-plugin/plugin.json "$root/.codex-plugin/plugin.json"
  cp .claude-plugin/plugin.json "$root/.claude-plugin/plugin.json"
  printf '%s\n' '---' 'name: implementaudit' '---' > "$root/skills/implementaudit/SKILL.md"
  printf '%s\n' '---' 'name: audit-state' '---' > "$root/skills/audit-state/SKILL.md"
  printf '%s\n' '---' 'name: audit-assess' '---' > "$root/skills/audit-assess/SKILL.md"
  printf '%s\n' '---' 'name: audit-implement' '---' > "$root/skills/audit-implement/SKILL.md"
  printf '%s\n' '---' 'name: audit-andon' '---' > "$root/skills/audit-andon/SKILL.md"
  cat > "$root/AGENTS.md" <<'EOF'
The normal release/install unit is one atomic dual-host plugin package.
The canonical generated artifact is IMPLEMENTAUDIT.plugin.zip.
IMPLEMENTAUDIT.skill is the standalone compatibility projection.
/implementaudit is the sole stable public/default governor with exactly four model-facing child skills.
They are audit-state, audit-assess, audit-implement, and audit-andon.
Local staged-copy evidence is not native host-discovery proof.
EOF
  cat > "$root/README.md" <<'EOF'
This is one atomic dual-host plugin. IMPLEMENTAUDIT.plugin.zip is canonical.
IMPLEMENTAUDIT.skill is compatibility-only. /implementaudit is the sole stable public/default governor.
The package has exactly four child skills: audit-state, audit-assess, audit-implement, and audit-andon.
It is owned by package/implementaudit-package.json.
The children are cross-cutting cognitive capabilities, not L1-L5 stages.
DAG agents provide horizontal, dependency-correct work lanes; children provide vertical progressive cognitive disclosure.
The standalone governor resolves internal-procedures/ and package structure and routing checks do not by themselves prove host activation.
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
The governor routes exactly four child skills: audit-state, audit-assess, audit-implement, and audit-andon.
Manifest presence is not evidence that marketplace discovery works.
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

for readme_case in stale-three-child wrong-child-name child-chain one-skill-per-loop standalone-direct-route child-authority; do
  root="$tmp/readme-$readme_case"
  cp -R "$good" "$root"
  case "$readme_case" in
    stale-three-child)
      printf '%s\n' 'The current package has three child skills.' >> "$root/README.md" ;;
    wrong-child-name)
      printf '%s\n' 'The current children are audit-state, audit-assess, and audit-trace.' >> "$root/README.md" ;;
    child-chain)
      printf '%s\n' 'Children route directly from audit-state -> audit-assess -> audit-implement.' >> "$root/README.md" ;;
    one-skill-per-loop)
      printf '%s\n' 'The architecture assigns one skill per L1-L5 loop.' >> "$root/README.md" ;;
    standalone-direct-route)
      printf '%s\n' 'The standalone projection directly exposes audit-andon as a discoverable child command.' >> "$root/README.md" ;;
    child-authority)
      printf '%s\n' 'A child skill may grant PASS and advance lifecycle state.' >> "$root/README.md" ;;
  esac
  expect_fail "$root" "README public-contract regression: $readme_case"
done

# Historical standalone-skill evidence is append-only and intentionally not a
# current topology owner, so it must not make the current-shape gate fail.
mkdir -p "$good/docs/audits/archive"
printf '%s\n' 'IMPLEMENTAUDIT.skill is the primary release artifact for v0.3.3.3.' \
  > "$good/docs/audits/archive/v0.3.3.3-release-report.md"
bash scripts/check-package-shape-claims.sh --scan-root "$good" >/dev/null

printf 'package-shape-claims.test: ok\n'
