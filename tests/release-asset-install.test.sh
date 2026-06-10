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
  printf 'release-asset-install.test: python, python3, or py -3 is required\n' >&2
  exit 1
fi

tmp_parent="$(mktemp -d)"
trap 'rm -rf "$tmp_parent"' EXIT

out_dir="$tmp_parent/release asset with spaces"
codex_home="$tmp_parent/codex home with spaces"
mkdir -p "$out_dir" "$codex_home"

bash scripts/build-release-asset.sh "$out_dir"
asset="$out_dir/IMPLEMENTAUDIT.skill"
checksums="$out_dir/CHECKSUMS.txt"

bash scripts/write-release-checksums.sh "$asset" "$checksums"
bash scripts/install-codex-from-release.sh \
  --asset "$asset" \
  --checksum "$checksums" \
  --codex-home "$codex_home" \
  --version 0.2.9

installed="$codex_home/skills/implementaudit"
for file in \
  SKILL.md \
  references/planning-depth.md \
  references/phase-design.md \
  references/goal-format.md \
  references/transcript-contract.md \
  references/routing.md \
  references/repo-state-comparison.md \
  references/child-agents.md \
  scripts/claim-run.sh \
  scripts/detect-env.sh \
  scripts/detect-stack.sh \
  scripts/repo-state.sh \
  scripts/summarize-repo.sh \
  scripts/validate-audit-spec.sh \
  scripts/validate-phase.sh \
  templates/ROADMAP.md \
  templates/STATE.md \
  templates/THINKING.md \
  templates/phase-goal.txt \
  templates/child-agent-report.md \
  templates/PROTOCOL.md
do
  [ -f "$installed/$file" ] || {
    printf 'release-asset-install.test: missing installed file: %s\n' "$file" >&2
    exit 1
  }
done

if [ -e "$installed/IMPLEMENTAUDIT.md" ]; then
  printf 'release-asset-install.test: root behavior file must not be installed\n' >&2
  exit 1
fi

stale="$out_dir/STALE-CHECKSUMS.txt"
printf 'sha256  %064d  IMPLEMENTAUDIT.skill\n' 0 > "$stale"

if bash scripts/install-codex-from-release.sh \
  --asset "$asset" \
  --checksum "$stale" \
  --codex-home "$tmp_parent/stale codex home" \
  --version 0.2.9 >/dev/null 2>&1; then
  printf 'release-asset-install.test: stale checksum unexpectedly passed\n' >&2
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
if bash scripts/install-codex-from-release.sh \
  --asset "$overbroad" \
  --checksum "$overbroad_checksums" \
  --codex-home "$tmp_parent/overbroad codex home" \
  --version 0.2.9 >/dev/null 2>&1; then
  printf 'release-asset-install.test: overbroad archive unexpectedly passed\n' >&2
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
if bash scripts/install-codex-from-release.sh \
  --asset "$sidecar" \
  --checksum "$sidecar_checksums" \
  --codex-home "$tmp_parent/sidecar codex home" \
  --version 0.2.9 >/dev/null 2>&1; then
  printf 'release-asset-install.test: sidecar artifact unexpectedly passed\n' >&2
  exit 1
fi

printf 'release-asset-install.test: ok\n'
