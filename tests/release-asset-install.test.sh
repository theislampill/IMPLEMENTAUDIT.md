#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

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
  --version 0.2.4

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
  --version 0.2.4 >/dev/null 2>&1; then
  printf 'release-asset-install.test: stale checksum unexpectedly passed\n' >&2
  exit 1
fi

printf 'release-asset-install.test: ok\n'
