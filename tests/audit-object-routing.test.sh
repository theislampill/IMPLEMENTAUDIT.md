#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bash scripts/check-routing.sh
bash scripts/check-lean-discipline.sh

require() {
  local file="$1"
  local text="$2"
  grep -Fqi "$text" "$file" || {
    printf 'audit-object-routing.test: missing in %s: %s\n' "$file" "$text" >&2
    exit 1
  }
}

fixture="fixtures/audit-object-routing/category-matrix.md"
reference="skills/implementaudit/references/audit-category-matrix.md"

for text in \
  "correctness / bugs" \
  "security / privacy" \
  "performance / scale" \
  "tests / validation" \
  "architecture / tech debt" \
  "dependencies / migrations" \
  "DX / tooling" \
  "docs / handoff" \
  "direction / design" \
  "Deep analysis is default pressure" \
  "Security review is default pressure" \
  "Direction analysis routes through DMADV"
do
  require "$fixture" "$text"
done

for text in \
  "Native route proof matrix" \
  "correctness / bugs | Native route exceeds baseline through DMAIC/PDCA defect closure" \
  "security / privacy | Native route exceeds baseline through default security pressure" \
  "performance / scale | Native route exceeds baseline through measurement-or-static-evidence distinction" \
  "tests / validation | Native route exceeds baseline through test/checker/fixture evidence" \
  "architecture / tech debt | Native route exceeds baseline through owner/source boundary decisions" \
  "dependencies / migrations | Native route exceeds baseline through manifest/lockfile readback" \
  "DX / tooling | Native route exceeds baseline through host-aware helper/runbook checks" \
  "docs / handoff | Native route exceeds baseline through public-claim truth checks" \
  "direction / design / next | Native route exceeds baseline through DMADV direction/design routing"
do
  require "$fixture" "$text"
done

for text in \
  "Native Category Route Contract" \
  "native IMPLEMENTAUDIT classifier" \
  "Performance / scale | DMAIC for brownfield performance repair" \
  "Tests / validation | DMAIC for brownfield validation repair" \
  "Architecture / tech debt | Owner/source and boundary decisions, DMAIC" \
  "Dependencies / migrations | DMAIC for brownfield dependency/migration repair" \
  "DX / tooling | DMAIC for brownfield tooling repair" \
  "Docs / handoff | DMAIC for brownfield docs/handoff truth repair" \
  "Direction / design / next | DMADV direction/design routing" \
  "Deep analysis is a default pressure" \
  "Security review is also a default pressure" \
  "Direction analysis routes through DMADV" \
  "Do not add command identities for quick, deep, security, next"
do
  require "$reference" "$text"
done

if grep -R -n -E '/implementaudit (quick|deep|security|next|features|roadmap)' \
  skills README.md docs/portal fixtures/audit-object-routing \
  | grep -v "Do not advertise" \
  | grep -v "Do not add" \
  >/tmp/implementaudit-audit-object-routing-command-mode-hit.txt; then
  cat /tmp/implementaudit-audit-object-routing-command-mode-hit.txt >&2
  rm -f /tmp/implementaudit-audit-object-routing-command-mode-hit.txt
  printf 'audit-object-routing.test: non-native command mode advertised\n' >&2
  exit 1
fi
rm -f /tmp/implementaudit-audit-object-routing-command-mode-hit.txt

printf 'audit-object-routing.test: ok\n'
