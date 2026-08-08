#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-planner-stages.sh

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

cp -R skills "$tmp/skills"
cp -R fixtures "$tmp/fixtures"
cp scripts/check-planner-stages.sh "$tmp/check-planner-stages.sh"
cp README.md "$tmp/README.md"
mkdir -p "$tmp/docs/diagrams" "$tmp/docs/portal/pages"
cp docs/diagrams/execution-spine.mmd "$tmp/docs/diagrams/execution-spine.mmd"
cp docs/portal/pages/planning-and-phases.html \
  "$tmp/docs/portal/pages/planning-and-phases.html"

if ! grep -Fq "Stage 6.ii - Pre-flight smoke" "$tmp/skills/implementaudit/SKILL.md"; then
  printf 'planner-stages.test: fixture setup failed\n' >&2
  exit 1
fi

perl -0pi -e 's/Stage 6\.ii - Pre-flight smoke/Stage 6.ii - missing/' "$tmp/skills/implementaudit/SKILL.md"

(
  cd "$tmp"
  mkdir scripts
  mv check-planner-stages.sh scripts/check-planner-stages.sh
  if bash scripts/check-planner-stages.sh >/dev/null 2>&1; then
    printf 'planner-stages.test: expected missing Stage 6.ii check to fail\n' >&2
    exit 1
  fi
)

cp -R skills "$tmp/skills-order"
cp -R fixtures "$tmp/fixtures-order"
cp scripts/check-planner-stages.sh "$tmp/check-planner-stages-order.sh"
perl -0pi -e 's/(Stage 6\.i - Independent cold review)\n(Stage 6\.ii - Pre-flight smoke)/$2\n$1/' \
  "$tmp/skills-order/implementaudit/references/planning-depth.md"
(
  cd "$tmp"
  rm -rf skills fixtures
  mv skills-order skills
  mv fixtures-order fixtures
  mkdir -p scripts
  mv check-planner-stages-order.sh scripts/check-planner-stages.sh
  if bash scripts/check-planner-stages.sh >/dev/null 2>&1; then
    printf 'planner-stages.test: expected out-of-order substages to fail\n' >&2
    exit 1
  fi
)

cp -R skills "$tmp/skills-routing"
cp -R fixtures "$tmp/fixtures-routing"
cp scripts/check-planner-stages.sh "$tmp/check-planner-stages-routing.sh"
perl -0pi -e 's/distinct supported candidate causes/distinct hidden candidate causes/' \
  "$tmp/skills-routing/implementaudit/SKILL.md"
(
  cd "$tmp"
  rm -rf skills fixtures
  mv skills-routing skills
  mv fixtures-routing fixtures
  mkdir -p scripts
  mv check-planner-stages-routing.sh scripts/check-planner-stages.sh
  if bash scripts/check-planner-stages.sh >/dev/null 2>&1; then
    printf 'planner-stages.test: expected missing uncertainty route to fail\n' >&2
    exit 1
  fi
)

printf 'planner-stages.test: ok\n'
