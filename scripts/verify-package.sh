#!/usr/bin/env bash
set -euo pipefail

export PYTHONDONTWRITEBYTECODE=1

fail() {
  printf 'verify-package: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

release_identity_args=()
release_identity_tmp=""
trap 'if [ -n "${release_identity_tmp:-}" ]; then rm -rf "$release_identity_tmp"; fi' EXIT
if [ "${1:-}" = "--release-identity" ]; then
  case "$2" in
    family-forward|cross-family-forward)
      [ "$#" -eq 5 ] \
        || fail "--release-identity $2 requires <previous-tag> <candidate-tag> <release-commit>"
      release_identity_args=("$2" "$3" "$4" "$5")
      shift 5
      ;;
    same-tag-correction)
      [ "$#" -eq 5 ] \
        || fail "--release-identity same-tag-correction requires <public-tag> <current-public-receipt> <release-commit>"
      release_identity_args=("$2" "$3" "$4" "$5")
      shift 5
      ;;
    forward|republish)
      [ "$#" -eq 4 ] \
        || fail "--release-identity requires <forward|republish> <previous-version> <release-commit>"
      release_identity_args=("$2" "$3" "$4")
      shift 4
      ;;
    *) fail "--release-identity mode must be forward, republish, family-forward, cross-family-forward, or same-tag-correction" ;;
  esac
fi
[ "$#" -eq 0 ] || fail "unknown argument: $1"

require_file() {
  [ -f "$1" ] || fail "missing required file: $1"
}

if [ -e IMPLEMENTAUDIT.md ]; then
  fail "root IMPLEMENTAUDIT.md must be absent; canonical behavior lives in skills/implementaudit/SKILL.md"
fi
require_file AGENTS.md
require_file README.md
require_file CHANGELOG.md
require_file CLAUDE.md
require_file CONTRIBUTING.md
require_file .gitattributes
require_file .gitignore
require_file .codex-plugin/plugin.json
require_file .claude-plugin/plugin.json
require_file .claude-plugin/marketplace.json
require_file package/implementaudit-package.json
require_file scripts/build-release-asset.sh
require_file scripts/package-contract.py
require_file scripts/check-package-contract.sh
require_file scripts/install-plugin-from-release.sh
if [ "${#release_identity_args[@]}" -gt 0 ]; then
  release_identity_tmp="$(mktemp -d)"
  bash scripts/build-release-asset.sh "$release_identity_tmp"
  bash scripts/build-release-asset.sh --check-release-identity \
    "${release_identity_args[@]}" "$repo_root" "$release_identity_tmp/IMPLEMENTAUDIT.skill"
fi
require_file scripts/check-public-claim-boundaries.sh
require_file scripts/check-added-lines-clean.sh
require_file scripts/check-audit-retention.sh
require_file scripts/check-agents-bootstrap-budget.sh
require_file scripts/check-audit-object-routing-contract.sh
require_file scripts/check-capability-parity-contract.sh
require_file scripts/check-dogfood-bootstrap-contract.sh
require_file scripts/dogfood-evidence-broker.py
require_file scripts/check-marker-order.sh
require_file scripts/check-installed-payload-self-contained.sh
require_file scripts/check-native-integration.sh
require_file scripts/check-package-shape-claims.sh
require_file scripts/check-planner-stages.sh
require_file scripts/check-plan-quality-contract.sh
require_file scripts/check-safeguard-restoration.sh
require_file scripts/check-readme-toc.sh
require_file scripts/check-routing.sh
require_file scripts/check-skill-layout-contract.sh
require_file scripts/check-skill-bootstrap-budget.sh
require_file scripts/check-sidecar-boundaries.sh
require_file scripts/check-terminology-integration.sh
require_file scripts/build-source-evidence-pack.sh
require_file scripts/generate-readme-diagrams.sh
require_file scripts/verify-readme-diagrams-rendered.sh
require_file scripts/install-claude-from-release.sh
require_file scripts/install-codex-from-release.sh
require_file scripts/install-plugin-from-release.sh
require_file scripts/write-release-checksums.sh
require_file skills/implementaudit/SKILL.md
require_file skills/implementaudit/references/planning-depth.md
require_file skills/implementaudit/references/phase-design.md
require_file skills/implementaudit/references/goal-format.md
require_file skills/implementaudit/references/transcript-contract.md
require_file skills/implementaudit/references/continuity.md
require_file skills/implementaudit/references/routing.md
require_file skills/implementaudit/references/repo-state-comparison.md
require_file skills/implementaudit/references/sidecars.md
require_file skills/implementaudit/references/child-agents.md
require_file skills/implementaudit/references/audit-category-matrix.md
require_file skills/implementaudit/references/audit-playbook.md
require_file skills/implementaudit/references/plan-lifecycle.md
require_file skills/implementaudit/references/terminology-integration.md
require_file skills/implementaudit/references/convergence-mode.md
require_file skills/implementaudit/scripts/check-evidence-anchor.sh
require_file skills/implementaudit/scripts/apply-observed-mutation.sh
require_file skills/implementaudit/scripts/check-duplication-parity.sh
require_file skills/implementaudit/scripts/check-respec-impact-set.sh
require_file skills/implementaudit/scripts/check-lesson-lift.sh
require_file skills/implementaudit/scripts/check-handoff-packet.sh
require_file skills/implementaudit/scripts/check-closure-surface.sh
require_file skills/implementaudit/scripts/check-authorization-binding.sh
require_file skills/implementaudit/scripts/claim-run.sh
require_file skills/implementaudit/scripts/detect-env.sh
require_file skills/implementaudit/scripts/detect-stack.sh
require_file skills/implementaudit/scripts/map-pin-chain.sh
require_file skills/implementaudit/scripts/repo-state.sh
require_file skills/implementaudit/scripts/summarize-repo.sh
require_file skills/implementaudit/scripts/validate-audit-spec.sh
require_file skills/implementaudit/scripts/validate-phase.sh
require_file skills/implementaudit/scripts/lane-survivor-inventory.sh
require_file skills/implementaudit/templates/ROADMAP.md
require_file skills/implementaudit/templates/STATE.md
require_file skills/implementaudit/templates/THINKING.md
require_file skills/implementaudit/templates/phase-goal.txt
require_file skills/implementaudit/templates/child-agent-report.md
require_file skills/implementaudit/templates/final-report.md
require_file skills/implementaudit/templates/read-only-plan.md
require_file skills/implementaudit/templates/PROTOCOL.md
require_file skills/implementaudit/templates/host-notes.md
require_file skills/implementaudit/templates/respec-impact-set.md
require_file fixtures/simple-audit/AUDIT.md
require_file fixtures/simple-audit/EXPECTED-LEDGER.md
require_file fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md
require_file fixtures/simple-audit/EXPECTED-ANDON-RECOVERY-SKELETON.md
require_file fixtures/simple-audit/EXPECTED-ANDON-HANDOFF-SKELETON.md
require_file fixtures/audit-retention/negative-missing-artifact-boundary.md
require_file fixtures/audit-retention/negative-stale-root-reference.md
require_file fixtures/zero-optional-tool/COMPLETE-RUN.md
require_file fixtures/routing/greenfield-goal-synthesis/INPUT.md
require_file fixtures/routing/greenfield-goal-synthesis/EXPECTED.md
require_file fixtures/routing/greenfield-goal-synthesis/INVALID-MISSING-INTAKE.md
require_file fixtures/routing/greenfield-full-category-intake/EXPECTED.md
require_file fixtures/routing/greenfield-batched-questions/EXPECTED.md
require_file fixtures/routing/brownfield-audit-closure/INPUT.md
require_file fixtures/routing/brownfield-audit-closure/EXPECTED.md
require_file fixtures/routing/brownfield-audit-closure/INVALID-MUTATION-FIRST.md
require_file fixtures/routing/brownfield-zero-question-recon/EXPECTED.md
require_file fixtures/routing/brownfield-one-question-true-gap/EXPECTED.md
require_file fixtures/routing/brownfield-two-question-true-gap/EXPECTED.md
require_file fixtures/routing/mixed-greenfield-in-brownfield/INPUT.md
require_file fixtures/routing/mixed-greenfield-in-brownfield/EXPECTED.md
require_file fixtures/audit-spec/valid-mixed.md
require_file fixtures/audit-spec/invalid-missing-owner.md
require_file fixtures/audit-spec/invalid-missing-rollback.md
require_file fixtures/audit-spec/invalid-missing-evidence.md
require_file fixtures/audit-spec/invalid-missing-generated-plan.md
require_file fixtures/audit-spec/invalid-missing-release-boundary.md
require_file fixtures/child-agents/AGENTS.md
require_file fixtures/child-agents/README.md
require_file fixtures/child-agents/read-only-contract-auditor.md
require_file fixtures/child-agents/adversarial-behavioral-auditor.md
require_file fixtures/child-agents/read-only-contract-auditor-report.md
require_file fixtures/child-agents/adversarial-behavioral-auditor-report.md
require_file fixtures/child-agents/normalized-findings-ledger.md
require_file fixtures/audit-object-routing/category-matrix.md
require_file fixtures/audit-object-routing/plan-lifecycle.md
require_file fixtures/audit-object-routing/issues-deferred.md
require_file fixtures/audit-object-routing/quick-bounded-audit.md
require_file fixtures/audit-object-routing/deep-pressure-disclosure.md
require_file fixtures/audit-object-routing/dmadv-what-next.md
require_file fixtures/audit-object-routing/branch-diff-classification.md
require_file fixtures/audit-object-routing/reconcile-statuses.md
require_file fixtures/audit-object-routing/execute-dispatch-isolation.md
require_file fixtures/audit-object-routing/finding-format-contract.md
require_file fixtures/audit-object-routing/repo-content-as-data.md
require_file fixtures/audit-object-routing/intent-doc-recon.md
require_file fixtures/audit-object-routing/read-only-audit-object-closure.md
require_file fixtures/audit-object-routing/transcripts/quick-bounded-audit-transcript.md
require_file fixtures/audit-object-routing/transcripts/deep-pressure-disclosure-transcript.md
require_file fixtures/audit-object-routing/transcripts/dmadv-what-next-transcript.md
require_file fixtures/audit-object-routing/transcripts/branch-diff-classification-transcript.md
require_file fixtures/audit-object-routing/transcripts/execute-dispatch-isolation-transcript.md
require_file fixtures/audit-object-routing/transcripts/execute-preflight-contract-transcript.md
require_file fixtures/audit-object-routing/transcripts/reconcile-statuses-transcript.md
require_file fixtures/audit-object-routing/transcripts/finding-format-contract-transcript.md
require_file fixtures/audit-object-routing/transcripts/repo-content-as-data-transcript.md
require_file fixtures/audit-object-routing/transcripts/intent-doc-recon-transcript.md
require_file fixtures/audit-object-routing/transcripts/read-only-audit-object-closure-transcript.md
require_file fixtures/native-integration/p0-correctness-native-route.md
require_file fixtures/native-integration/p0-security-native-route.md
require_file fixtures/native-integration/p0-performance-native-route.md
require_file fixtures/native-integration/p0-test-coverage-native-route.md
require_file fixtures/native-integration/p0-architecture-native-route.md
require_file fixtures/native-integration/p0-dependencies-native-route.md
require_file fixtures/native-integration/p0-dx-tooling-native-route.md
require_file fixtures/native-integration/p0-docs-handoff-native-route.md
require_file fixtures/native-integration/p0-direction-native-route.md
require_file fixtures/native-integration/negative-generic-roadmap.md
require_file fixtures/native-integration/single-plan-native-route.md
require_file fixtures/native-integration/transcripts/audit-object-route-canary-transcript.md
require_file fixtures/read-only-plans/valid-handoff-plan.md
require_file fixtures/read-only-plans/read-only-zero-mutation.status
require_file fixtures/read-only-plans/read-only-audit-ledger.status
require_file fixtures/read-only-plans/negative-read-only-source-mutation.status
require_file fixtures/secret-hygiene/repo-ignore-previous-instructions.md
require_file fixtures/secret-hygiene/repo-print-env.md
require_file fixtures/secret-hygiene/repo-fake-secret.txt
require_file fixtures/secret-hygiene/negative-plan-reproduces-fake-secret.md
require_file fixtures/secret-hygiene/negative-child-prompt-missing-security-rules.md
require_file fixtures/e2e-mini-audit-loop/phase-1.md
require_file fixtures/e2e-mini-audit-loop/EXPECTED-TRANSCRIPT.md
require_file fixtures/safeguards/negative-missing-final-report.md
require_file fixtures/safeguards/negative-missing-5whys-exit.md
require_file fixtures/safeguards/negative-unlabeled-source-only-checker.md
require_file docs/diagrams/tooling-architecture.mmd
require_file docs/diagrams/invocation-modes.mmd
require_file docs/diagrams/execution-spine.mmd
require_file docs/audits/INDEX.md
require_file docs/audits/RETENTION.md
require_file docs/maintenance/AGENTS-HISTORY.md
require_file docs/portal/site.json
require_file docs/portal/pages/overview.html
require_file docs/portal/pages/installation.html
require_file docs/portal/pages/audit-trail.html
require_file docs/portal/assets/draft-v2.css
require_file docs/portal/assets/draft-v2.js
require_file docs/research/genealogy/CORPUS_SOURCE_LOCK.json
require_file docs/research/genealogy/CORPUS_MANIFEST.json
require_file docs/research/genealogy/PROPERTY_MASTER_INDEX.json
require_file docs/research/implementaudit/historical-absorption-baseline/HISTORICAL_ABSORPTION_BASELINE.json
require_file scripts/build-docs-portal.py
require_file scripts/check-docs-portal.py
require_file scripts/build-genealogy-corpus.py
require_file scripts/check-genealogy-corpus.py
require_file scripts/check-historical-absorption-baseline.py
require_file tests/docs-portal.test.sh
require_file tests/genealogy-corpus.test.sh
require_file tests/eval-harness.test.sh
require_file eval/campaign_freeze_preflight.py
require_file eval/test_campaign_freeze_preflight.py
require_file eval/qualification_evidence_producer.py
require_file eval/test_qualification_evidence_producer.py
require_file eval/historical_readjudicate.py
require_file eval/test_historical_readjudicate.py
require_file tests/payload-path-hygiene.test.sh
require_file scripts/check-helper-reachability.sh
require_file tests/helper-reachability.test.sh
require_file tests/issue-ready-work-orders.test.sh
require_file fixtures/casual-build/accepted-intent.md
require_file fixtures/casual-build/rejected-intent.md
require_file fixtures/phase-design/polish-harden.md
require_file fixtures/acceptance-instrument-discipline/cases.json
require_file fixtures/acceptance-instrument-discipline/F7-vacuous-invariant.md
require_file fixtures/census-discipline/cases.json
require_file fixtures/verification-window/cases.json
require_file fixtures/respec-impact-set/cases.json
require_file eval/fixtures/E5d-census-discipline/fixture.json
require_file eval/fixtures/E5d-census-discipline/controls.json
require_file eval/fixtures/E5d-census-discipline/transcript_pass.txt
require_file eval/fixtures/E5d-census-discipline/transcript_fail.txt
require_file eval/fixtures/R001D-public-projection/fixture.json
require_file eval/fixtures/R001D-public-projection/controls.json
require_file eval/fixtures/R001D-public-projection/transcript_pass.txt
require_file eval/fixtures/R001D-public-projection/transcript_fail.txt
require_file eval/fixtures/B6-verification-window-freeze/fixture.json
require_file eval/fixtures/B6-verification-window-freeze/transcript_pass.txt
require_file eval/fixtures/B6-verification-window-freeze/transcript_pass.summary.json
require_file eval/fixtures/B6-verification-window-freeze/transcript_fail.txt
require_file eval/fixtures/B4-quirk-memo/fixture.json
require_file eval/fixtures/B4-quirk-memo/transcript_pass.txt
require_file eval/fixtures/B4-quirk-memo/transcript_pass.summary.json
require_file eval/fixtures/B4-quirk-memo/transcript_fail.txt
require_file eval/fixtures/B4-quirk-memo/transcript_fail.summary.json
require_file eval/fixtures/E5e-respec-impact-set/fixture.json
require_file eval/fixtures/E5e-respec-impact-set/transcript_pass.txt
require_file eval/fixtures/E5e-respec-impact-set/transcript_pass.summary.json
require_file eval/fixtures/E5e-respec-impact-set/transcript_fail.txt
require_file .github/workflows/pages.yml
require_file skills/implementaudit/references/lean-operating-discipline.md
require_file scripts/check-lean-discipline.sh
require_file scripts/check-acceptance-instrument-discipline.sh
require_file scripts/check-census-discipline.sh
require_file tests/lean-discipline.test.sh
require_file fixtures/lean/brownfield-dmaic-release-repair.md
require_file fixtures/lean/brownfield-dmaic-stale-docs.md
require_file fixtures/lean/greenfield-dmadv-new-runtime-helper.md
require_file fixtures/lean/mixed-dmaic-dmadv-package-boundary.md
require_file fixtures/lean/sidecar-graphify-absent-markdown-fallback.md
require_file fixtures/lean/sidecar-graphify-dmaic-analyze.md
require_file fixtures/lean/sidecar-activegraph-dmaic-custody.md
require_file fixtures/sidecar-contract/stale-graph/graph.json
require_file fixtures/sidecar-contract/fresh-graph/graph.json
require_file fixtures/sidecar-contract/auto-backend-refusal.md
require_file fixtures/sidecar-contract/anti-trigger-routing.md
require_file fixtures/sidecar-contract/terrain-trigger-routing.md
require_file fixtures/sidecar-contract/footprint-default.md
require_file fixtures/sidecar-contract/external-validity.md
require_file tests/andon-class-contract.test.sh
require_file tests/continuity-contract.test.sh
require_file tests/codex-compact-interlock.test.sh
require_file tests/host-session-binding.test.sh
require_file fixtures/host-session-binding/disabled-owner.json
require_file fixtures/host-session-binding/untrusted-owner.json
require_file fixtures/host-session-binding/malformed-binding.json
require_file skills/implementaudit/references/host-session-binding.md
require_file skills/implementaudit/scripts/host-session-binding.py
require_file tests/route-obligation-contract.test.sh
require_file tests/route-history-capacity.test.sh
require_file skills/implementaudit/references/route-obligations.md
require_file skills/implementaudit/scripts/route-transaction.py
require_file skills/implementaudit/scripts/codex-recovery-prompt-input.py
require_file skills/implementaudit/scripts/codex-recovery-native-reader.py
require_file skills/implementaudit/scripts/codex-native-desktop-binding.py
require_file skills/implementaudit/references/codex-recovery-observer-profile.json
require_file tests/interruption-durability.test.sh
require_file tests/lesson-lift-contract.test.sh
require_file tests/handoff-packet-contract.test.sh
require_file tests/closure-surface-contract.test.sh
require_file tests/authorization-binding-contract.test.sh
require_file tests/scarce-resource-rehearsal-contract.test.sh
require_file tests/R000B-R001E-review-heldouts.test.sh
require_file scripts/check-durable-identities.py
require_file tests/durable-identity-contract.test.sh
require_file skills/implementaudit/references/identity-namespaces.json
require_file skills/implementaudit/scripts/resolve-durable-identity.py
require_file fixtures/scarce-resource-rehearsal/cases.json
require_file tests/convergence-mode-contract.test.sh
require_file tests/andon-escalation-judgment.test.sh
require_file tests/background-chain-contract.test.sh
require_file tests/evidence-anchoring.test.sh
require_file tests/verification-window-contract.test.sh
require_file tests/observation-bound-mutation-integrity.test.sh
require_file tests/respec-impact-set-contract.test.sh
require_file tests/marker-order.test.sh
require_file tests/planner-stages.test.sh
require_file tests/release-asset.test.sh
require_file tests/reproducible-release-asset.test.sh
require_file tests/release-asset-install.test.sh
require_file tests/release-asset-install-claude.test.sh
require_file tests/plugin-release-asset.test.sh
require_file tests/plugin-install.test.sh
require_file tests/install-copy-smoke.test.sh
require_file tests/routing.test.sh
require_file tests/repo-state.test.sh
require_file tests/commit-message-contract.test.sh
require_file tests/audit-spec.test.sh
require_file tests/audit-retention.test.sh
require_file tests/agents-bootstrap-budget.test.sh
require_file tests/added-lines-clean.test.sh
require_file tests/claim-run.test.sh
require_file tests/claim-run-unknown-option.test.sh
require_file tests/continuity.test.sh
require_file tests/phase-validation.test.sh
require_file tests/acceptance-instrument-discipline.test.sh
require_file tests/lossless-evidence-capture.test.sh
require_file tests/census-discipline.test.sh
require_file fixtures/public-projection/cases.json
require_file fixtures/public-projection/semantic-preservation.json
require_file fixtures/public-projection/installed-dogfood-input.json
require_file tests/sidecars.test.sh
require_file tests/capability-ledger.test.sh
require_file tests/audit-object-routing.test.sh
require_file tests/audit-object-plan-lifecycle.test.sh
require_file tests/issues-deferred-gate.test.sh
require_file tests/audit-object-routing-contract.test.sh
require_file tests/native-integration.test.sh
require_file tests/package-shape-claims.test.sh
require_file tests/package-contract.test.sh
require_file tests/internal-skill-topology.test.sh
require_file tests/internal-skill-routing.test.sh
require_file tests/post-compaction-contract.py
require_file tests/terminology-integration.test.sh
require_file tests/read-only-plans-lane.test.sh
require_file tests/source-evidence-pack-runnable.test.sh
require_file tests/dogfood-bootstrap-contract.test.sh
require_file tests/safeguard-restoration.test.sh
require_file tests/plan-quality-contract.test.sh
require_file tests/installed-payload-self-contained.test.sh
require_file tests/skill-layout-contract.test.sh
require_file tests/e2e-mini-audit-loop.test.sh
require_file tests/skill-bootstrap-budget.test.sh
require_file tests/source-evidence-pack.test.sh
require_file tests/action-selection-contract.test.sh
require_file fixtures/a-to-g/dependency-types.json
require_file fixtures/a-to-g/semantic-invalidation-radius.json
require_file fixtures/a-to-g/transaction-concurrency.json
require_file fixtures/a-to-g/holon-lifecycle.json
require_file fixtures/a-to-g/post-compaction-isolation.json
require_file fixtures/a-to-g/andon-trigger-routing.json
require_file fixtures/a-to-g/execution-owner.json
require_file tests/a-to-g-a-fixture.test.sh
require_file tests/a-to-g-b-fixture.test.sh
require_file tests/a-to-g-c-fixture.test.sh
require_file tests/a-to-g-df-fixture.test.sh
require_file tests/a-to-g-e-fixture.test.sh
require_file tests/a-to-g-g-fixture.test.sh
require_file tests/fanout-coverage-contract.test.sh
require_file tests/cold-review-contract.test.sh
require_file tests/claim-boundary-proof-levels.test.sh
require_file fixtures/claim-boundaries/allowed-proof-wording.md
require_file fixtures/claim-boundaries/negative-unqualified-proven.md
require_file fixtures/claim-boundaries/negative-archived-verdict-unqualified.md
require_file fixtures/cold-review/independent-review-confirms-handoff.md
require_file fixtures/cold-review/projection-index-derivative.md
require_file fixtures/cold-review/negative-self-critique-only-preflight.md
require_file fixtures/cold-review/negative-same-context-review.md
require_file fixtures/cold-review/negative-projection-contradicts-object.md
require_file fixtures/cold-review/negative-review-keyword-gate.md
require_file fixtures/child-agents/broad-scope-four-lanes.md
require_file fixtures/child-agents/low-concurrency-serialized-lanes.md
require_file fixtures/child-agents/negative-coverage-table-only.md
require_file fixtures/child-agents/negative-silent-lane-drop.md
require_file fixtures/child-agents/negative-generic-single-pass.md
require_file fixtures/child-agents/negative-child-prompt-missing-fanout-contract.md
require_file fixtures/audit-action-selection/ordinary-task-deepens.md
require_file fixtures/audit-action-selection/narrow-direct-stays-shallow.md
require_file fixtures/audit-action-selection/negative-keyword-gated-depth.md
require_file fixtures/audit-action-selection/negative-size-only-deepening.md
require_file fixtures/audit-action-selection/negative-missing-selection-record.md
require_file fixtures/dogfood-bootstrap/positive/baseline-first-transcript.jsonl
require_file fixtures/dogfood-bootstrap/negative/installed-readback-before-baseline-transcript.jsonl
require_file fixtures/dogfood-bootstrap/negative/chunking-readback-before-baseline-transcript.jsonl
require_file fixtures/dogfood-bootstrap/negative/real-home-readback-before-temp-home-transcript.jsonl
require_file fixtures/dogfood-bootstrap/typed-event.schema.json
require_file fixtures/dogfood-bootstrap/typed/ordinary-control-activation.jsonl
require_file fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl
require_file fixtures/dogfood-bootstrap/typed/self-dogfood-contradiction.jsonl
require_file fixtures/skill-bootstrap-budget/negative-full-read-installed-payload.md
require_file fixtures/terminology-integration/full-stack-integration.md
require_file fixtures/terminology-integration/negative-glossary-orphan.md
require_file fixtures/terminology-integration/negative-generic-advice.md
require_file .github/workflows/validate.yml

for child_report in \
  skills/implementaudit/templates/child-agent-report.md \
  fixtures/child-agents/read-only-contract-auditor.md \
  fixtures/child-agents/adversarial-behavioral-auditor.md \
  fixtures/child-agents/read-only-contract-auditor-report.md \
  fixtures/child-agents/adversarial-behavioral-auditor-report.md
do
  grep -q "Verdict:" "$child_report" || fail "child-agent report missing Verdict section: $child_report"
  grep -q "Files inspected:" "$child_report" || fail "child-agent report missing Files inspected section: $child_report"
  grep -q "Commands run:" "$child_report" || fail "child-agent report missing Commands run section: $child_report"
  grep -q "Andon registration check:" "$child_report" || fail "child-agent report missing Andon registration check section: $child_report"
  grep -q "Required patches" "$child_report" || fail "child-agent report missing Required patches section: $child_report"
  grep -q "Required fixtures / canaries" "$child_report" || fail "child-agent report missing Required fixtures / canaries section: $child_report"
  grep -q "What closes" "$child_report" || fail "child-agent report missing What closes section: $child_report"
  grep -q "What remains" "$child_report" || fail "child-agent report missing What remains section: $child_report"
  grep -q "Next smallest safe action" "$child_report" || fail "child-agent report missing Next smallest safe action section: $child_report"
  for field in "Finding title" "Category" "Evidence" "Impact" "Effort" "Risk" "Confidence" "Fix sketch / implementation route" "Owner/source" "Verification" "Rejected/deferred rationale" "Remaining risk" "Route"; do
    grep -q "$field" "$child_report" || fail "child-agent report missing finding-format field '$field': $child_report"
  done
done

grep -q "Andon registration invariant" skills/implementaudit/references/child-agents.md || fail "child-agent Andon registration invariant is missing"
grep -q "superseded for release proof" skills/implementaudit/references/child-agents.md || fail "child-agent false-green rerun rule is missing"

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required for JSON validation"
fi

native_a_g_python="${PYTHON_BIN:-}"
if [ -z "$native_a_g_python" ]; then
  native_a_g_python="$("${py_cmd[@]}" -c 'import pathlib, sys; print(pathlib.Path(sys.executable).as_posix())')"
fi
"$native_a_g_python" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)' \
  || fail "native A-G fixture controls require an explicit Python 3.11 executable"

"${py_cmd[@]}" -m json.tool .claude-plugin/plugin.json >/dev/null
"${py_cmd[@]}" -m json.tool .claude-plugin/marketplace.json >/dev/null

"${py_cmd[@]}" - <<'PY'
import subprocess
from pathlib import Path

tracked_sh = subprocess.check_output(
    ["git", "ls-files", "*.sh"], text=True, encoding="utf-8"
).splitlines()
bad = [
    path
    for path in tracked_sh
    if Path(path).is_file() and b"\r\n" in Path(path).read_bytes()
]
if bad:
    raise SystemExit(
        "tracked shell scripts must use LF line endings: " + ", ".join(bad)
    )
PY

"${py_cmd[@]}" - <<'PY'
import json
import re
from pathlib import Path

plugin = json.loads(Path(".claude-plugin/plugin.json").read_text(encoding="utf-8"))
skill_text = Path("skills/implementaudit/SKILL.md").read_text(encoding="utf-8")
match = re.match(r"---\n(?P<frontmatter>.*?)\n---\n", skill_text, re.S)
if not match:
    raise SystemExit("SKILL.md must have YAML frontmatter")
frontmatter = match.group("frontmatter")
version_match = re.search(r'(?m)^\s+version:\s*["\']?([^"\'\n]+)["\']?\s*$', frontmatter)
if not version_match:
    raise SystemExit("SKILL.md metadata.version is missing")
skill_version = version_match.group(1).strip()
plugin_version = str(plugin.get("version", "")).strip()
if skill_version != plugin_version:
    raise SystemExit(
        f"SKILL.md metadata.version {skill_version!r} != plugin.json version {plugin_version!r}"
    )
PY

"${py_cmd[@]}" - <<'PY'
import json
import re
from pathlib import Path

plugin = json.loads(Path(".claude-plugin/plugin.json").read_text())
if plugin.get("name") != "implementaudit":
    raise SystemExit("plugin name must be implementaudit")
if plugin.get("skills") != "./skills/":
    raise SystemExit(
        "source plugin skills path must be ./skills/ "
        "(builder flattens skills/implementaudit into archive root)"
    )
if not plugin.get("version"):
    raise SystemExit("plugin version is required")
if plugin.get("version") != "0.4.1":
    raise SystemExit("plugin version must be 0.4.1 for the v0.4.1 runtime family")

marketplace = json.loads(Path(".claude-plugin/marketplace.json").read_text())
plugins = marketplace.get("plugins")
if not isinstance(plugins, list) or not plugins:
    raise SystemExit("marketplace plugins list is required")
if plugins[0].get("source") != "./":
    raise SystemExit("source marketplace entry should point at plugin source root")
if "path" in plugins[0]:
    raise SystemExit("source marketplace entry must not use archive-only path")

# Public version-claim truth: the portal site owns the four-component project
# milestone while the plugin manifest owns the three-component runtime family.
# README must project both identities without synthesising the public tag from
# the runtime version.
readme = Path("README.md").read_text(encoding="utf-8")
version = plugin["version"]
site = json.loads(Path("docs/portal/site.json").read_text(encoding="utf-8"))
milestone = str(site.get("release", {}).get("milestone", "")).strip()
milestone_match = re.fullmatch(r"v([0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+)", milestone)
if not milestone_match:
    raise SystemExit("docs/portal/site.json release milestone must be v-prefixed with four numeric components")
if milestone_match.group(1) != version:
    raise SystemExit(
        f"docs/portal/site.json release milestone {milestone!r} does not belong to runtime family {version}"
    )
claim_lines = [l for l in readme.splitlines() if "Current project milestone:" in l]
if not claim_lines:
    raise SystemExit("README must state 'Current project milestone:' in Version and release notes")
for line in claim_lines:
    if f"`{milestone}`" not in line or f"`{version}`" not in line:
        raise SystemExit(
            f"README version claim does not match milestone {milestone} and manifest {version}: {line.strip()}"
        )
PY

# Shipped-payload path integrity: use the maintained scanner so canonical
# verification and focused controls share identical namespace/path semantics.
bash scripts/check-installed-payload-self-contained.sh

for marker in \
  Self-critique: \
  PREFLIGHT_GREEN \
  PREFLIGHT_RED \
  IMPLEMENTAUDIT_PHASE_START \
  IMPLEMENTAUDIT_PHASE_VERIFY \
  AGENTS_UPDATE_DECISION \
  IMPLEMENTAUDIT_PHASE_DONE \
  ANDON_PROBE \
  ANDON_ESCALATE \
  ANDON_HANDOFF \
  AUDIT_START \
  AUDIT_VERIFY \
  AUDIT_GAPS \
  AUDIT_COMPLETE \
  AUDIT_HANDOFF \
  IMPLEMENTAUDIT_RUN_COMPLETE
do
  grep -R "$marker" -n skills >/dev/null || fail "missing transcript marker: $marker"
done

grep -R "\.IMPLEMENTAUDIT/runs" -n skills README.md AGENTS.md >/dev/null || fail ".IMPLEMENTAUDIT runs runtime path is not documented"
grep -R "child-agent reports are review evidence only" -in skills README.md AGENTS.md fixtures >/dev/null || fail "child-agent evidence boundary is missing"
grep -R "AUDIT_HANDOFF.*conditional\|AUDIT_HANDOFF.*handoff path" -in skills AGENTS.md >/dev/null || fail "AUDIT_HANDOFF conditional boundary is missing"
grep -R "AGENTS_UPDATE_DECISION" -n skills/implementaudit/templates/phase-goal.txt skills/implementaudit/templates/STATE.md >/dev/null || fail "AGENTS_UPDATE_DECISION template coverage is missing"
grep -R "Stage 0 - Context/tool/repo-state detection" -n skills/implementaudit/SKILL.md >/dev/null || fail "native Stage 0 planner contract is missing from skills/implementaudit/SKILL.md"
grep -R "Stage 6.ii - Pre-flight smoke" -n skills/implementaudit/SKILL.md >/dev/null || fail "native Stage 6.ii planner contract is missing from skills/implementaudit/SKILL.md"
if grep -F "Read STATE.md then ROADMAP.md" skills/implementaudit/SKILL.md >/dev/null; then
  fail "host-compaction bootstrap must not governor-read STATE/ROADMAP before audit-state OPEN"
fi
grep -F "implementaudit.post-compaction-recovery.v2" skills/implementaudit/SKILL.md >/dev/null || fail "host-compaction v2 recovery capsule is missing from the governor bootloader"
grep -F "OPEN_AUDIT_STATE" skills/implementaudit/SKILL.md >/dev/null || fail "host-compaction audit-state OPEN is missing from the governor bootloader"
grep -F "compile-work-graph.py --native-a-g" skills/implementaudit/references/child-agents.md >/dev/null || fail "native A-G compiler join is missing from child-agents.md"
grep -F "admit-transaction" skills/implementaudit/references/child-agents.md >/dev/null || fail "native A-G transaction admission join is missing from child-agents.md"
grep -F "implementaudit.holon-execution-evidence.v1" skills/implementaudit/references/child-agents.md >/dev/null || fail "native A-G lifecycle evidence ceiling is missing from child-agents.md"
"$native_a_g_python" - <<'PY' || fail "native S3 semantic/order contract is missing or its negative controls false-green"
from pathlib import Path
import re

skill = Path("skills/implementaudit/SKILL.md").read_text(encoding="utf-8")
children = Path("skills/implementaudit/references/child-agents.md").read_text(encoding="utf-8")

def bounded(text, start, end=None):
    begin = text.index(start)
    finish = text.find(end, begin + len(start)) if end else len(text)
    if finish < 0:
        finish = len(text)
    return text[begin:finish]

def ordered(text, markers):
    cursor = 0
    for marker in markers:
        position = text.find(marker, cursor)
        if position < 0:
            return False
        cursor = position + len(marker)
    return True

def swap_once(text, left, right):
    left_at = text.index(left)
    right_at = text.index(right, left_at + len(left))
    return (
        text[:left_at]
        + right
        + text[left_at + len(left):right_at]
        + left
        + text[right_at + len(right):]
    )

def inject_before_once(text, boundary, addition):
    at = text.index(boundary)
    return text[:at] + addition + text[at:]

def contradicts(text, patterns):
    return any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in patterns)

def valid(skill_text, child_text):
    runtime = bounded(skill_text, "## Runtime Loop")
    join = bounded(child_text, "#### Native A-G governor join", "#### Preparation and qualified-product projections")
    dispatch = bounded(child_text, "#### Root-governor dispatch-context classifier", "Compile the bounded frontier projection")
    return (
        ordered(runtime, [
            "NATIVE_AUTHORITATIVE_RECOVERY",
            "Genuine host-reported-compaction",
            "MECHANICAL_CURRENTNESS",
            "never substantively reads STATE/ROADMAP/WORK_GRAPH before OPEN",
            "fresh host worker context",
            "OPEN_AUDIT_STATE",
            "minimum frontier",
            "RETURN",
            "DISPOSE",
            "RECONCILE",
            "post-return currentness",
            "exact typed edge",
        ])
        and ordered(join, [
            "implementaudit.native-a-g.request.v1",
            "dependency, write",
            "effect",
            "compile-work-graph.py --native-a-g",
            "typed writer/dependency keys",
            "typed effect keys",
            "admit-transaction",
            "disjoint transactions",
            "MAX_CHILD_PER_ROUTE_TRANSACTION_1",
            "controller-wide",
            "implementaudit.holon-execution-evidence.v1",
            "RETURN is buffered evidence only",
            "fresh host worker context",
            "same or any previously used context",
            "route transaction identity",
        ])
        and not contradicts(join, [
            r"same or any previously used context.{0,96}(?:eligible|permitted|allowed)",
            r"admit-transaction.{0,96}(?:accepts|admits).{0,96}typed effect keys",
            r"MAX_CHILD_PER_ROUTE_TRANSACTION_1.{0,96}controller-wide child maximum",
            r"RETURN is buffered evidence only.{0,128}(?:creates|grants).{0,96}canonical credit",
        ])
        and "post-compaction audit-state is NEW_TASK_DISPATCH" in dispatch
        and "fresh context" in dispatch
    )

if not valid(skill, children):
    raise SystemExit(1)

negative_cases = [
    (skill.replace("fresh host worker context", "host worker context"), children),
    (skill.replace("OPEN_AUDIT_STATE", "AUDIT_STATE_OPEN_REMOVED"), children),
    (skill, children.replace("typed effect keys", "effect facts")),
    (skill, children.replace("MAX_CHILD_PER_ROUTE_TRANSACTION_1", "MAX_CHILD_REMOVED")),
    (skill, children.replace("implementaudit.holon-execution-evidence.v1", "holon evidence")),
    (skill, children.replace("same or any previously used context", "ambiguous context")),
    (
        swap_once(skill, "fresh host worker context", "OPEN_AUDIT_STATE"),
        children,
    ),
    (
        skill,
        inject_before_once(
            children,
            "#### Preparation and qualified-product projections",
            "The same or any previously used context remains eligible for OPEN.\n\n",
        ),
    ),
    (
        skill,
        inject_before_once(
            children,
            "#### Preparation and qualified-product projections",
            "The admit-transaction command accepts typed effect keys as admission facts.\n\n",
        ),
    ),
    (
        skill,
        inject_before_once(
            children,
            "#### Preparation and qualified-product projections",
            "MAX_CHILD_PER_ROUTE_TRANSACTION_1 is a controller-wide child maximum.\n\n",
        ),
    ),
    (
        skill,
        inject_before_once(
            children,
            "#### Preparation and qualified-product projections",
            "RETURN is buffered evidence only but creates canonical credit before RECONCILE.\n\n",
        ),
    ),
]
if any(valid(candidate_skill, candidate_children) for candidate_skill, candidate_children in negative_cases):
    raise SystemExit(1)
PY
grep -R "<run-root>/THINKING.md" -n skills/implementaudit/templates/THINKING.md skills/implementaudit/templates/PROTOCOL.md skills/implementaudit/templates/phase-goal.txt >/dev/null || fail "THINKING runtime artifact coverage is missing"
grep -R "install-codex-from-release.sh" -n README.md AGENTS.md scripts tests >/dev/null || fail "release-asset Codex install path is not documented/validated"
grep -R "install-claude-from-release.sh" -n README.md AGENTS.md scripts tests >/dev/null || fail "release-asset Claude install path is not documented/validated"
grep -R "install-plugin-from-release.sh" -n README.md AGENTS.md scripts tests >/dev/null || fail "canonical plugin staged-install path is not documented/validated"
grep -R "LIVE_V0_2_5_0_CLAUDE_INSTALL_BROKEN" -n AGENTS.md >/dev/null || fail "Claude install anti-repeat rule LIVE_V0_2_5_0_CLAUDE_INSTALL_BROKEN is missing from AGENTS.md"
grep -R "release-asset-install-claude.test.sh" -n AGENTS.md scripts >/dev/null || fail "Claude install smoke test is not referenced in AGENTS.md or scripts"
grep -R "stale checksum" -in tests/release-asset-install.test.sh scripts/install-codex-from-release.sh >/dev/null || fail "stale checksum install failure coverage is missing"
grep -R "auto-update" -in README.md CHANGELOG.md AGENTS.md | grep -i "no marketplace auto-update\|does not auto-update\|do not assume\|do not claim" >/dev/null || fail "auto-update boundary must remain explicit"
grep -n "bash scripts/write-release-checksums.sh --all dist dist/CHECKSUMS.txt" CONTRIBUTING.md >/dev/null || fail "CONTRIBUTING release validation must write the dual-asset CHECKSUMS.txt before --check"
grep -n "bash scripts/write-release-checksums.sh --check --all dist dist/CHECKSUMS.txt" CONTRIBUTING.md >/dev/null || fail "CONTRIBUTING release validation must check the dual-asset checksum manifest"
grep -R "v0.2.4.5" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.4.5 is not documented"
grep -R "v0.2.8.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.8.0 is not documented"
grep -R "v0.2.7.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.7.0 is not documented"
grep -R "v0.2.6.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.6.0 is not documented"
grep -R "v0.2.5.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.5.0 is not documented"
grep -R "v0.2.4.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.4.0 history is not documented"
grep -R "v0.2.3.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.3.0 is not documented"
grep -R "v0.2.2.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.2.0 history is not documented"
grep -R "v0.2.1.0" -n README.md CHANGELOG.md AGENTS.md >/dev/null || fail "project milestone v0.2.1.0 history is not documented"
grep -R "v0.2.0.0" -n CHANGELOG.md README.md AGENTS.md >/dev/null || fail "project milestone v0.2.0.0 history is not documented"
grep -R "v0.1.0" -n CHANGELOG.md >/dev/null || fail "reconstructed v0.1.0 changelog entry missing"
grep -R "v0.0.1" -n CHANGELOG.md >/dev/null || fail "reconstructed v0.0.1 changelog entry missing"

if grep -R -n -I --exclude-dir=.git --exclude-dir=.IMPLEMENTAUDIT --exclude-dir=graphify-out \
  --exclude-dir=.graphify --exclude-dir=.activegraph --exclude=verify-package.sh \
  -e "read root IMPLEMENTAUDIT.md" \
  -e "read .*IMPLEMENTAUDIT.md.*behavior source" \
  -e "IMPLEMENTAUDIT.md remains the root behavior file" \
  -e "IMPLEMENTAUDIT.md and skills/implementaudit/SKILL.md" \
  -e "IMPLEMENTAUDIT.md remains synced" \
  . >/tmp/implementaudit-root-file-claim.txt; then
  cat /tmp/implementaudit-root-file-claim.txt >&2
  rm -f /tmp/implementaudit-root-file-claim.txt
  fail "repo docs/checkers must not direct agents to root IMPLEMENTAUDIT.md as a behavior source"
fi
rm -f /tmp/implementaudit-root-file-claim.txt

grep -R "skills/implementaudit/SKILL.md" -n README.md AGENTS.md CHANGELOG.md >/dev/null || fail "canonical skills/implementaudit/SKILL.md behavior source is not documented"

child_upper_a="CHILD"
child_upper_b="AGENTS"
child_lower_a="child"
child_lower_b="agents"
child_upper_name="${child_upper_a}_${child_upper_b}"
child_lower_name="${child_lower_a}_${child_lower_b}"
if grep -R -n -I --exclude-dir=.git --exclude-dir=.IMPLEMENTAUDIT --exclude-dir=graphify-out \
  --exclude-dir=.graphify --exclude-dir=.activegraph \
  -e "$child_upper_name" -e "$child_lower_name" . >/tmp/implementaudit-child-agents-grep.txt; then
  cat /tmp/implementaudit-child-agents-grep.txt >&2
  rm -f /tmp/implementaudit-child-agents-grep.txt
  fail "nonstandard child-agent instruction filename claim appears in repo files"
fi
rm -f /tmp/implementaudit-child-agents-grep.txt

grep -R "Graphify output is orientation evidence, not proof" -n skills README.md AGENTS.md >/dev/null || fail "Graphify proof boundary is missing"
grep -R "ActiveGraph custody is not correctness proof" -n skills README.md AGENTS.md >/dev/null || fail "ActiveGraph proof boundary is missing"
grep -R "Native Audit Category Routing Matrix" -n skills/implementaudit/references/audit-category-matrix.md >/dev/null || fail "native audit category routing matrix is missing"
grep -R "Audit Playbook" -n skills/implementaudit/references/audit-playbook.md >/dev/null || fail "audit-object-routing audit playbook is missing"
grep -R "Plan Lifecycle And Dispatch Semantics" -n skills/implementaudit/references/plan-lifecycle.md >/dev/null || fail "audit-object-routing plan lifecycle reference is missing"
grep -R "Terminology Integration" -n skills/implementaudit/references/terminology-integration.md >/dev/null || fail "terminology integration reference is missing"
grep -R "Issue Publication Deferred" -n skills/implementaudit/references/plan-lifecycle.md >/dev/null || fail "--issues deferred boundary is missing"
grep -Ri 'Do not add command identities for quick, deep, security, next' -n skills/implementaudit/references/audit-category-matrix.md >/dev/null || fail "foreign command identity rejection is missing"

bash scripts/generate-readme-diagrams.sh --check
bash scripts/verify-readme-diagrams-rendered.sh
bash scripts/check-readme-toc.sh
bash scripts/check-audit-retention.sh
bash scripts/check-agents-bootstrap-budget.sh
bash scripts/check-planner-stages.sh
bash scripts/check-marker-order.sh \
  fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md \
  fixtures/simple-audit/EXPECTED-ANDON-RECOVERY-SKELETON.md \
  fixtures/simple-audit/EXPECTED-ANDON-HANDOFF-SKELETON.md \
  fixtures/zero-optional-tool/COMPLETE-RUN.md
bash scripts/check-routing.sh
bash scripts/check-audit-object-routing-contract.sh
bash scripts/check-capability-parity-contract.sh
bash scripts/check-dogfood-bootstrap-contract.sh
bash scripts/check-safeguard-restoration.sh
bash scripts/check-native-integration.sh
bash scripts/check-installed-payload-self-contained.sh
bash scripts/check-sidecar-boundaries.sh
bash scripts/check-public-claim-boundaries.sh
bash scripts/check-package-shape-claims.sh
bash scripts/check-package-contract.sh
bash scripts/check-plan-quality-contract.sh
bash scripts/check-skill-layout-contract.sh
bash scripts/check-skill-bootstrap-budget.sh
bash scripts/check-lean-discipline.sh
bash scripts/check-terminology-integration.sh
bash scripts/check-added-lines-clean.sh HEAD
bash tests/lean-discipline.test.sh
bash tests/andon-class-contract.test.sh
bash tests/distributed-runtime-contract.test.sh
bash tests/continuity-contract.test.sh
bash tests/codex-compact-interlock.test.sh
bash tests/compaction-result-member-preflight.test.sh
bash tests/compaction-hold-persistent-refusal.test.sh
bash tests/host-session-binding.test.sh
bash tests/route-obligation-contract.test.sh
bash tests/route-history-capacity.test.sh
bash tests/canonical-state-rotation.test.sh
bash tests/operational-evidence-contract.test.sh
bash tests/subagent-provenance-sensor.test.sh
bash tests/turn-disposition.test.sh
bash tests/interruption-durability.test.sh
bash tests/lesson-lift-contract.test.sh
bash tests/handoff-packet-contract.test.sh
bash tests/closure-surface-contract.test.sh
bash tests/authorization-binding-contract.test.sh
bash tests/scarce-resource-rehearsal-contract.test.sh
bash tests/R000B-R001E-review-heldouts.test.sh
bash tests/durable-identity-contract.test.sh
bash tests/convergence-mode-contract.test.sh
bash tests/andon-escalation-judgment.test.sh
bash tests/background-chain-contract.test.sh
bash tests/evidence-anchoring.test.sh
bash tests/verification-window-contract.test.sh
bash tests/observation-bound-mutation-integrity.test.sh
bash tests/respec-impact-set-contract.test.sh
bash tests/marker-order.test.sh
bash tests/planner-stages.test.sh
bash tests/release-asset.test.sh
bash tests/reproducible-release-asset.test.sh
bash tests/release-asset-install.test.sh
bash tests/release-asset-install-claude.test.sh
bash tests/plugin-release-asset.test.sh
bash tests/plugin-install.test.sh
bash tests/install-copy-smoke.test.sh
bash tests/routing.test.sh
bash tests/repo-state.test.sh
bash tests/commit-message-contract.test.sh
bash tests/audit-spec.test.sh
bash tests/audit-retention.test.sh
bash tests/agents-bootstrap-budget.test.sh
bash tests/added-lines-clean.test.sh
bash tests/claim-run.test.sh
bash tests/claim-run-unknown-option.test.sh
bash tests/continuity.test.sh
bash tests/phase-validation.test.sh
bash tests/acceptance-instrument-discipline.test.sh
bash tests/lossless-evidence-capture.test.sh
bash tests/census-discipline.test.sh
bash tests/sidecars.test.sh
bash tests/capability-ledger.test.sh
bash tests/audit-object-routing.test.sh
bash tests/audit-object-plan-lifecycle.test.sh
bash tests/issues-deferred-gate.test.sh
bash tests/audit-object-routing-contract.test.sh
bash tests/native-integration.test.sh
bash tests/package-shape-claims.test.sh
bash tests/package-contract.test.sh
bash tests/internal-skill-topology.test.sh
bash tests/internal-skill-routing.test.sh
bash tests/terminology-integration.test.sh
bash tests/read-only-plans-lane.test.sh
bash tests/source-evidence-pack-runnable.test.sh
bash tests/dogfood-bootstrap-contract.test.sh
bash tests/safeguard-restoration.test.sh
bash tests/plan-quality-contract.test.sh
bash tests/installed-payload-self-contained.test.sh
bash tests/skill-layout-contract.test.sh
bash tests/e2e-mini-audit-loop.test.sh
bash tests/skill-bootstrap-budget.test.sh
bash tests/source-evidence-pack.test.sh
bash tests/action-selection-contract.test.sh
bash tests/work-graph-compiler.test.sh
PYTHON_BIN="$native_a_g_python" \
  bash tests/a-to-g-a-fixture.test.sh
PYTHON_BIN="$native_a_g_python" \
  bash tests/a-to-g-b-fixture.test.sh
PYTHON_BIN="$native_a_g_python" \
  bash tests/a-to-g-c-fixture.test.sh
PYTHON_BIN="$native_a_g_python" \
  bash tests/a-to-g-df-fixture.test.sh
PYTHON_BIN="$native_a_g_python" \
  bash tests/a-to-g-e-fixture.test.sh
PYTHON_BIN="$native_a_g_python" \
  bash tests/a-to-g-g-fixture.test.sh
bash tests/fanout-coverage-contract.test.sh
bash tests/cold-review-contract.test.sh
bash tests/claim-boundary-proof-levels.test.sh
bash tests/no-terminal-cap.test.sh
bash tests/eval-harness.test.sh
bash tests/payload-path-hygiene.test.sh
bash tests/helper-reachability.test.sh
bash tests/issue-ready-work-orders.test.sh
bash tests/summarize-repo.test.sh
bash tests/shipped-scripts-smoke.test.sh
bash tests/run-root-validation.test.sh
bash tests/custody-append.test.sh
bash tests/docs-portal.test.sh
bash tests/genealogy-corpus.test.sh
bash scripts/check-validation-registry.sh
bash tests/validation-registry.test.sh
bash scripts/build-release-asset.sh --check

git diff --check

printf 'verify-package: ok\n'
