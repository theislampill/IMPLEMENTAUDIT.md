# Audit Dogfood History

This index records repo-local evidence that ImplementAudit changes are being
dogfooded through audit closure. It is not a release log, provenance manifest,
or raw smoke-output dump.

| Evidence | What it proves | What remains unverified |
|---|---|---|
| Commit `9acc1b9` (`docs: harden v0.2.1.0 package governance`) | Prior package hardening used verbose local trace, Smoke A/B language, generated README diagram checks, marker-order checks, host-claim checks, and release asset validation. | The original external audit file for that run is not tracked in this repo. |
| `CHANGELOG.md` v0.2.1.0 entry | Causal history is recorded for transcript contract, marker-order, fixture, generated diagram, host-claim, and checksum-boundary hardening. | Changelog is summary evidence, not a raw transcript. |
| `fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md` | Final audit markers require `AUDIT_COMPLETE` before `IMPLEMENTAUDIT_RUN_COMPLETE`. | It is a fixture, not a full historical run transcript. |

The v0.2.2.0 lane carried the same convention forward: read-only Gemba first,
owner/source patching, fixtures/checkers for behavioral claims, Smoke A/B before
closure, and explicit release/provenance boundaries.

The v0.2.3.0 lane adds a native harness adaptation matrix plus executable
helpers/checkers for complete repo-state comparison, audit-spec validation, and
added-line cleanliness/overclaim scans. The detailed matrix lives in
`docs/audits/v0.2.3.0-harness-adaptation-matrix.md`.

Post-release README/onboarding audit evidence lives in
`docs/audits/readme-audit_202606052026.md`. That audit patches forward newcomer
navigation, terminology, loopability, and README ToC validation after the
`v0.2.3.0` release; it is not part of the original release gate.

The v0.2.4.0 lane adds native planner-stage hardening and user-facing
onboarding/install-pipeline proof. The detailed ledger lives in
`docs/audits/v0.2.4.0-planner-stage-hardening.md` and covers Stage 0-7 planner
semantics, `THINKING.md`, pre-flight/self-critique, one-goal handoff, generated
README diagram readability, and local release-asset-to-Codex-install validation.

The v0.2.4.5 lane audits real optional-sidecar use. The detailed ledger lives
in `docs/audits/v0.2.4.5-graphify-activegraph-honesty.md` and covers isolated
Graphify/ActiveGraph installation, project terrain/custody evidence, sidecar
claim boundaries, package-minimality hardening, and the release gates still to
be closed by that ledger.

The v0.2.5.0 lane closes the external staged-goal comparator runtime gap in
native IMPLEMENTAUDIT terms. The detailed ledger lives in
`docs/audits/v0.2.5.0-external-staged-goal-runtime-gap-closure.md` and covers
Stage 0 context detection, greenfield/brownfield intake rules, namespaced run
roots, `claim-run.sh`, Stage 6/6.5 review and preflight discipline,
self-healing/final-audit loops, bounded continuity, sidecar boundaries,
package minimality, and external identity hygiene without importing comparator
identity or runtime markers.

A post-release repair for v0.2.5.0 closes the Claude Desktop install gap. The
detailed ledger lives in `docs/audits/v0.2.5.0-claude-install-repair.md` and
covers the root cause (Codex-only install coverage), the added Claude install
script and smoke test, README and AGENTS.md updates, and the explicit BLOCKED
boundary for live Claude Desktop install proof.

The v0.2.6.0 lane closes 12 operational-parity gap classes (G1-G12) identified
by comparing v0.2.5.0 against a read-only external staged-goal comparator package.
The detailed ledger lives in
`docs/audits/v0.2.6.0-operational-parity-hardening.md` and covers:
phase-spec structure (full executable spec with all 16 required fields/sections),
validate-phase.sh strengthened to 19 failure modes,
7 phase-design shape rules (hardening/safety-net/visual-polish/provenance/scope),
8 dispatch-prep steps in Stage 5,
concrete 16-step per-phase PROTOCOL loop,
exact 3-strike failure recovery protocol,
final audit protocol (AUDIT_START, coverage math, 3-round audit-fix),
mid-run interruption handling (IMPLEMENTAUDIT_PAUSE, 4-option menu),
deepened detect-stack.sh and summarize-repo.sh recon helpers,
behavioral continuity tests (25/25) with 6 fixtures,
behavioral sidecar tests (24/24) with 7 fixtures,
generic check-forbidden-terms.sh (caller-supplied runtime terms, not source-embedded),
identity hygiene release-gate instructions in AGENTS.md.
All 12 gap classes adapted or intentionally rejected with documentation.
External comparator identity not imported into any tracked surface.

A pre-release proof-gap closure and package-boundary repair for v0.2.6.0
is recorded in
`docs/audits/v0.2.6.0-final-runtime-and-package-boundary-audit.md`.
It terminally classifies all 25 behavior classes from the external
staged-goal comparator (16 `native-owner-covered`, 9
`covered-with-stronger-implementaudit-boundary`, 0 open), proves the
`.skill` package boundary against an explicit 23-entry manifest, and
documents the ZIP_STORED → ZIP_DEFLATED compression repair
(154,750 bytes → 59,551 bytes;
SHA256: `f37f6356b3a342510512e57c3f2785b6be4ea044a5b312d59d40d8ce4eade947`).
Compression regression is now caught automatically by
`tests/release-asset.test.sh`.

The v0.2.7.0 lane implements Lean/TPS operating discipline in native
IMPLEMENTAUDIT runtime behavior. The detailed ledger lives in
`docs/audits/v0.2.7.0-lean-operating-discipline.md` and classifies 20
Lean/TPS concepts: 5 already-covered, 2 strengthened, 11 adapted, 0
intentionally-rejected, 0 deferred. The lane adds DMAIC brownfield routing,
DMADV greenfield routing, 5S_CHECK per-phase gate (all five pillars),
Jidoka stop-the-line chain, Nemawashi owner-decision gate, Muda/Mura/Muri
register in THINKING.md, Quality route field in phase-goal.txt, four Lean
routing fixtures, and `scripts/check-lean-discipline.sh` poka-yoke checker
(12 structural requirements, verified by `tests/lean-discipline.test.sh` 11/11).
Lean terms are runtime behavior, not decorative labels. No sigma-level,
DPMO, or certification claims.

The v0.2.8.0 adaptation lane closes G1-G7 comparator-advantage gaps identified
against a read-only external staged-goal comparator package. The detailed ledger
lives in `docs/audits/v0.2.8.0-adaptation.md` and covers: chooser table in
goal-format.md (G1); neutral comparator language in docs portal with formal
forbidden-term check (G2); governed casual-build intake as a 4th invocation shape in
SKILL.md §2/§2a/Stage 0, routing.md, planning-depth.md, and casual-build fixtures (G3);
bounded continuity preload with 5-source priority order and IMPLEMENTAUDIT_CONTINUITY_SAVED
marker in SKILL.md Stage 0 and PROTOCOL.md (G4); G5 (per-phase continuity writeback)
STRENGTHENED — v0.2.6.0 PROTOCOL loop was the base, but v0.2.8.0 added
IMPLEMENTAUDIT_CONTINUITY_SAVED marker with 6 required fields, bounded writeback options
table, ActiveGraph custody path, Graphify terrain-update request, and 34-check continuity
test suite (+9 new); optional Polish & Harden phase type in phase-design.md Rule P4-8 with
fixtures (G6); docs portal generator (build-docs-portal.py), check script
(check-docs-portal.py), 26/26 test suite, and easy invocation examples in
docs/portal/onboarding.md (G7); GitHub Pages CI (pages.yml) with OWNER DECISION note
for Pages source setting; docs-portal.test.sh wired into validate.yml.
A bounded audit-fix round (5 items) was executed before AUDIT_COMPLETE: Graphify
authorization boundary reconciled (terrain reads authorized as self-maintenance; no new
indexing); G5 reclassified to STRENGTHENED; Python print() replaced with
sys.stdout.write/sys.stderr.write; bash -n YAML evidence replaced with stdlib structural
checker; formal forbidden-term identity hygiene check executed.
External comparator identity not imported into any tracked surface.

A Graphify+ActiveGraph maximal-leverage gate for v0.2.7.0 is closed in the same
lane. Live sidecar smoke was run using installed tools (graphify 0.8.35,
activegraph 1.0.5.post2) in isolated temp environments. Graphify terrain extraction
produced 794 nodes, 724 links over the repo; 5 queries were run; 3 owner/source
candidates (skills/SKILL.md 49 links, skills/templates/PROTOCOL.md 25 links,
skills/templates/THINKING.md 12 links) were confirmed against live files.
ActiveGraph custody was written to a gitignored run root
(.IMPLEMENTAUDIT/runs/v0270-sidecar-smoke/) with 18 events (v7-001..v7-018),
read back successfully, and used to derive one narrow Capability Ledger entry.
Sidecar outputs remain excluded from tracked source and the .skill package.
Graphify terrain leverage and ActiveGraph custody event sections were added to
lean-operating-discipline.md; check-lean-discipline.sh extended to 12 structural
requirements; three sidecar fixtures added; tests extended to 11/11.
