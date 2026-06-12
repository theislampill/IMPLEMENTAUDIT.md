#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'release-asset-install-claude.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

tmp_parent="$(mktemp -d)"
trap 'rm -rf "$tmp_parent"' EXIT

out_dir="$tmp_parent/release asset with spaces"
claude_skills_dir="$tmp_parent/claude skill dir with spaces/implementaudit"
mkdir -p "$out_dir" "$claude_skills_dir"

bash scripts/build-release-asset.sh "$out_dir"
asset="$out_dir/IMPLEMENTAUDIT.skill"
checksums="$out_dir/CHECKSUMS.txt"

bash scripts/write-release-checksums.sh "$asset" "$checksums"
bash scripts/install-claude-from-release.sh \
  --asset "$asset" \
  --checksum "$checksums" \
  --claude-skills-dir "$claude_skills_dir"

for file in \
  SKILL.md \
  references/planning-depth.md \
  references/phase-design.md \
  references/goal-format.md \
  references/transcript-contract.md \
  references/routing.md \
  references/repo-state-comparison.md \
  references/child-agents.md \
  references/lean-operating-discipline.md \
  scripts/claim-run.sh \
  scripts/detect-env.sh \
  scripts/detect-stack.sh \
  scripts/repo-state.sh \
  scripts/summarize-repo.sh \
  scripts/validate-audit-spec.sh \
  scripts/validate-phase.sh \
  scripts/validate-run-root.sh \
  scripts/custody-append.sh \
  templates/ROADMAP.md \
  templates/STATE.md \
  templates/THINKING.md \
  templates/phase-goal.txt \
  templates/child-agent-report.md \
  templates/PROTOCOL.md \
  templates/sidecars.md \
  templates/tools.md \
  templates/context.md \
  .claude-plugin/plugin.json \
  .claude-plugin/marketplace.json
do
  [ -f "$claude_skills_dir/$file" ] || {
    printf 'release-asset-install-claude.test: missing installed file: %s\n' "$file" >&2
    exit 1
  }
done

if [ -e "$claude_skills_dir/IMPLEMENTAUDIT.md" ]; then
  printf 'release-asset-install-claude.test: root behavior file must not be installed\n' >&2
  exit 1
fi

stale="$out_dir/STALE-CHECKSUMS.txt"
printf 'sha256  %064d  IMPLEMENTAUDIT.skill\n' 0 > "$stale"

if bash scripts/install-claude-from-release.sh \
  --asset "$asset" \
  --checksum "$stale" \
  --claude-skills-dir "$tmp_parent/stale claude skill dir/implementaudit" >/dev/null 2>&1; then
  printf 'release-asset-install-claude.test: stale checksum unexpectedly passed\n' >&2
  exit 1
fi

overbroad_dir="$tmp_parent/overbroad asset"
mkdir -p "$overbroad_dir"
overbroad="$overbroad_dir/IMPLEMENTAUDIT.skill"
overbroad_checksums="$overbroad_dir/CHECKSUMS.txt"
"${py_cmd[@]}" - "$asset" "$overbroad" <<'PY'
import sys
import zipfile
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])

with zipfile.ZipFile(source) as src, zipfile.ZipFile(
    target, "w", compression=zipfile.ZIP_DEFLATED
) as dst:
    for info in src.infolist():
        dst.writestr(info, src.read(info.filename))
    dst.writestr("README.md", "repo-only doc must not be accepted in skill asset\n")
PY

bash scripts/write-release-checksums.sh "$overbroad" "$overbroad_checksums"
if bash scripts/install-claude-from-release.sh \
  --asset "$overbroad" \
  --checksum "$overbroad_checksums" \
  --claude-skills-dir "$tmp_parent/overbroad claude skill dir/implementaudit" >/dev/null 2>&1; then
  printf 'release-asset-install-claude.test: overbroad archive unexpectedly passed\n' >&2
  exit 1
fi

sidecar_dir="$tmp_parent/sidecar asset"
mkdir -p "$sidecar_dir"
sidecar="$sidecar_dir/IMPLEMENTAUDIT.skill"
sidecar_checksums="$sidecar_dir/CHECKSUMS.txt"
"${py_cmd[@]}" - "$asset" "$sidecar" <<'PY'
import sys
import zipfile
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])

with zipfile.ZipFile(source) as src, zipfile.ZipFile(
    target, "w", compression=zipfile.ZIP_DEFLATED
) as dst:
    for info in src.infolist():
        dst.writestr(info, src.read(info.filename))
    dst.writestr("references/graph.json", "{}\n")
PY

bash scripts/write-release-checksums.sh "$sidecar" "$sidecar_checksums"
if bash scripts/install-claude-from-release.sh \
  --asset "$sidecar" \
  --checksum "$sidecar_checksums" \
  --claude-skills-dir "$tmp_parent/sidecar claude skill dir/implementaudit" >/dev/null 2>&1; then
  printf 'release-asset-install-claude.test: sidecar artifact unexpectedly passed\n' >&2
  exit 1
fi

printf 'release-asset-install-claude.test: ok\n'
