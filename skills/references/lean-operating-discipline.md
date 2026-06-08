# Lean Operating Discipline

IMPLEMENTAUDIT implements Lean/TPS concepts as runtime behavior, template fields,
checkers, and final-audit rules. Lean terms are not decorative labels. Every term
below maps to a concrete runtime behavior or gate.

## Concept mapping table

| Lean term | IMPLEMENTAUDIT behavior | Owner/source | Evidence/check |
|---|---|---|---|
| Gemba / Genchi Genbutsu | Inspect live files/artifacts/outputs before any claim. Gemba is a non-skippable execution-spine gate. Do not diagnose from summaries when the live artifact exists. | `skills/SKILL.md` §Gemba | `check-planner-stages.sh` |
| A3 thinking | Maps to the `tdqyq-audit-object`: problem, current condition, target condition, root cause (5 Whys), countermeasure, acceptance criteria, owner/source, evidence, follow-up, sustainment. Must be concise and evidence-bearing, not a private reasoning dump. | `skills/SKILL.md` §Canonical audit terminology | `check-planner-stages.sh` |
| Kaizen | Standardize countermeasures when durable: fold into templates, AGENTS.md anti-repeat rules, checkers, or CI gates. CONTINUITY_DECISION at every phase boundary decides whether to standardize. | `AGENTS.md`, `skills/templates/phase-goal.txt` | `check-planner-stages.sh` |
| Hansei | Required structured reflection after: false pass, regression, abnormal release-gate command, substituted command, stale generated artifact, or owner intervention. Record: gap, cause, countermeasure, follow-up evidence. | `skills/SKILL.md` §Hansei | `check-planner-stages.sh` |
| Jidoka | Stop-the-line when evidence fails. Trigger: any proof failure, regression, hidden rerun, substituted command, package-boundary violation, or release-asset mismatch. Chain: Andon → FAILURE_PROBE → Hansei → 5 Whys (when warranted) → countermeasure → Kaizen standardization decision → re-run evidence → close/block/defer/handoff. | `skills/templates/PROTOCOL.md` §Jidoka stop-the-line | `check-planner-stages.sh` |
| Andon | Visible abnormality signal. Print Andon block with: status, blocker, failing check, owner/source, next concrete action. Do not hide failure. Do not mark "mostly done." | `skills/SKILL.md` §Andon | `check-planner-stages.sh` |
| Nemawashi | Surface consequential assumptions before dispatch. Tie to Stage 6 plan review: release/package/AGENTS.md/sidecar-status changes require explicit owner-aware review before Stage 7 handoff. | `skills/SKILL.md` §Nemawashi, `skills/templates/PROTOCOL.md` | Stage 6 Self-critique |
| 5S — Seiri (Sort) | Classify necessary vs unnecessary artifacts. Log scope creep and debris as new findings rather than absorbing them. Sort package payload (skills/) from repo-only material. | `skills/templates/PROTOCOL.md` §5S, `skills/templates/phase-goal.txt` | `check-lean-discipline.sh` |
| 5S — Seiton (Set in order) | Every artifact has a canonical place: owner/source, run root, docs, tests, package payload, release asset. Enforced by package manifest and `verify-package.sh`. | `.claude-plugin/plugin.json`, `scripts/verify-package.sh` | `verify-package.sh` |
| 5S — Seiso (Shine) | Clean generated docs, debug prints, session markers, sidecar debris, run-root debris, package bloat, stale outputs. Per-phase cleanliness check (Step 9 of phase loop). | `scripts/check-added-lines-clean.sh`, `skills/templates/PROTOCOL.md` | `check-added-lines-clean.sh` |
| 5S — Seiketsu (Standardize) | AGENTS_UPDATE_DECISION at every phase: does the countermeasure belong in template/checker/AGENTS.md/CI? Kaizen standardization decision in Jidoka chain. | `skills/templates/phase-goal.txt` §AGENTS_UPDATE_DECISION | `check-lean-discipline.sh` |
| 5S — Shitsuke (Sustain) | Add or verify a sustain check so the issue does not regress: test, checker, CI gate, or AGENTS.md rule. Sustain evidence required in phase transcript. | `scripts/check-lean-discipline.sh`, `tests/lean-discipline.test.sh` | `tests/lean-discipline.test.sh` |
| Muda (waste) | Unnecessary files, redundant checks, overbroad scope, dead artifacts, duplicate docs. Log in THINKING.md §Muda/Mura/Muri register. Muda is removed or logged as scope-creep; it is not silently absorbed. | `skills/templates/THINKING.md` | `check-lean-discipline.sh` |
| Mura (unevenness) | Phase-size imbalance, inconsistent evidence levels, stale generated docs. Log in THINKING.md. Mura triggers phase rebalance or Stage 6 review. | `skills/templates/THINKING.md` | Stage 6 Self-critique |
| Muri (overburden) | Too much in one phase, too many manual checks, unsafe owner assumptions, overloaded release gate. Log in THINKING.md. Muri triggers split/defer/owner decision. | `skills/templates/THINKING.md` | OWNER DECISION gate |
| Poka-yoke | Structural mistake-proofing via: `validate-phase.sh` (19 failure modes), `check-forbidden-terms.sh`, `check-lean-discipline.sh`, `check-routing.sh`, `check-host-claims.sh`, `check-planner-stages.sh`. Gates prevent wrong-state or invalid-spec execution. | `scripts/check-lean-discipline.sh`, `skills/scripts/validate-phase.sh` | `verify-package.sh` |
| Obeya / visual control | README Mermaid diagrams provide visual runtime overview (execution-spine, invocation-modes, tooling-architecture). `generate-readme-diagrams.sh --check` enforces freshness. ROADMAP.md provides phased visual plan. | `docs/diagrams/`, `scripts/generate-readme-diagrams.sh` | `generate-readme-diagrams.sh --check` |
| DMAIC | Brownfield improvement routing: Define (defect/gap/scope/target) → Measure (Smoke A/baseline) → Analyze (root cause/Muda/Mura/Muri class) → Improve (owner/source patch/regenerate/checks) → Control (sustain via tests/AGENTS/CI/package gates). Use for existing defects, regressions, release repairs, stale docs, broken checkers. | `skills/references/routing.md` §DMAIC | `check-routing.sh` |
| DMADV | Greenfield/replacement routing: Define (new capability/users/constraints) → Measure (CtQ acceptance measures/evidence/risk) → Analyze (design alternatives/dependencies/rollback) → Design (phase specs/templates/fixtures/validation) → Verify (Smoke B/final audit/package boundary/owner acceptance). Use for new governed artifacts, new runtime capabilities, replacement designs. | `skills/references/routing.md` §DMADV | `check-routing.sh` |
| Standard Work | Repeated countermeasures become templates, checkers, fixtures, AGENTS.md rules, or CI gates only when stable and repo-specific. PROTOCOL.md per-phase loop is the standard work template for governed execution. | `skills/templates/PROTOCOL.md`, `skills/templates/phase-goal.txt` | `verify-package.sh` |

## Graphify terrain leverage

Graphify is optional terrain/orientation. When available and authorized, use it in Lean steps as described
below. Graphify output must be confirmed against live files before any mutation or closure claim. Graphify
absence is not a blocker — fall back to live-file Gemba and repo-state.sh for all artifact classification.

| Lean step | Graphify terrain use | Live-file confirmation required |
|---|---|---|
| Seiri / Sort | Query node and link counts by artifact class (skills/, scripts/, tests/, fixtures/, docs/). Classify necessary vs unnecessary artifact surfaces. Identify possible debris or scope-creep candidates. | Confirm each candidate class against git ls-files and verify-package.sh require_file list before acting. |
| Seiton / Set in order | Query out-degree by file to identify highest-coupling owner/source candidates. Map package boundary (skills/ ships; scripts/, tests/, docs/ repo-only). Find unresolved or ambiguous graph relations. | Confirm top candidates by reading file content and cross-referencing verify-package.sh. Record INFERRED nodes as `unverified`. |
| Seiso / Shine | Query for isolated low-degree nodes (possible stale/dead surfaces), Graphify-untracked file types (e.g., .txt not parsed), and unexpected files in skills/ payload. | Confirm each stale/dead candidate by reading the live file. Do not delete or defer on Graphify result alone. |
| Muda / Mura / Muri | Use Graphify to surface redundant nodes, uneven degree clusters (phase imbalance), and high-degree overburdened owners. Log candidates in THINKING.md §Muda/Mura/Muri register. | Confirm each entry against live files and check output before adding to the register. |
| DMAIC — Measure / Analyze | Use Graphify to identify defect surface (owner files, dependency paths, generated outputs, likely regression files) and design alternatives for the Improve step. | Confirm every Graphify-derived owner/source and dependency candidate against live files and Smoke A before patching. |
| DMADV — Analyze / Design | Use Graphify to compare package/integration boundaries, dependency paths, test/checker placement, and anchor points for new artifacts. | Confirm package boundary placement against verify-package.sh and build-release-asset.sh before designing the new artifact. |

Query results recorded in `<run-root>/sidecars.md`:
- Query purpose
- Nodes / links at time of query
- Result summary (top candidates)
- Freshness (cached vs. fresh extraction)
- Evidence boundary: orientation only, not proof
- Live-file follow-up: what was confirmed and how

Graphify terrain limitation note: `.txt` files (e.g., `skills/templates/phase-goal.txt`) are not parsed as
code nodes. Always cross-reference the Graphify artifact list against `verify-package.sh require_file` for
complete package payload coverage.

## ActiveGraph custody events

ActiveGraph is optional custody/event evidence. When available and authorized, record these events for
Lean-governed runs. All event names below are IMPLEMENTAUDIT-defined custom events unless explicitly proven
upstream ActiveGraph built-ins. Events must be derived from real gate passages, checks, Andons, and final
audit evidence — not invented after the fact.

| Event | When to emit | Payload (minimum) |
|---|---|---|
| `implementaudit.run.opened` | At run start, when ActiveGraph is authorized | `run`, `milestone`, `host`, `purpose` |
| `gemba.graphify.queried` | When Graphify terrain is queried for this run | `graph_nodes`, `graph_links`, `queries_run`, `evidence: orientation only` |
| `lean.5s.sort.recorded` | After Seiri classification at phase boundary | `artifact classes classified`, `live_file_confirmation`, `muda_flagged` |
| `lean.5s.set_in_order.recorded` | After Seiton owner/source mapping | `top candidates by degree`, `seiton_gap if any`, `confirmed` |
| `lean.5s.shine.recorded` | After Seiso cleanliness check | `gitignored dirs confirmed`, `sidecar_debris_in_tracked_source: false` |
| `lean.standard_work.updated` | When Kaizen standardizes a countermeasure into templates/checkers | `artifact`, `change`, `evidence` |
| `lean.sustain_check.verified` | When a sustain check (test/checker/CI gate) passes | `check`, `result` |
| `dmaic.define.recorded` | At DMAIC Define step | `defect`, `owner_source`, `scope`, `acceptance_target` |
| `dmaic.measure.recorded` | At DMAIC Measure step | `smoke_a`, `gap`, `evidence_type` |
| `dmaic.analyze.recorded` | At DMAIC Analyze step | `root_cause`, `muda_class`, `regression_risk` |
| `dmaic.improve.recorded` | At DMAIC Improve step | `countermeasure`, `owner_source_patched` |
| `dmaic.control.recorded` | At DMAIC Control step | `sustain` (test/AGENTS.md/CI gate) |
| `dmadv.define.recorded` | At DMADV Define step | `new_capability`, `users`, `constraints`, `owner_source` |
| `dmadv.measure.recorded` | At DMADV Measure step | `ctq_acceptance`, `baseline_absence`, `risk` |
| `dmadv.analyze.recorded` | At DMADV Analyze step | `design_alternatives`, `selected`, `rollback` |
| `dmadv.design.recorded` | At DMADV Design step | `phase_specs`, `templates`, `fixtures`, `validation` |
| `dmadv.verify.recorded` | At DMADV Verify step | `smoke_b`, `package_check`, `owner_acceptance` |
| `jidoka.stop.recorded` | When Jidoka stop-the-line is triggered | `trigger_type`, `failing_check`, `owner_source` |
| `hansei.recorded` | After Hansei reflection | `gap`, `cause`, `countermeasure`, `follow_up` |
| `kaizen.countermeasure.standardized` | When countermeasure folded into template/checker/AGENTS | `artifact`, `rule_added` |
| `nemawashi.owner_decision.recorded` | At Nemawashi gate | `assumption`, `decision`, `boundary` |
| `muda_mura_muri.register.updated` | When THINKING.md register updated | `muda`, `mura`, `muri` |
| `poka_yoke.check.recorded` | After poka-yoke checker runs | `checker`, `requirements_verified`, `result` |
| `obeya.run_state.updated` | When STATE.md or ROADMAP.md updated at phase boundary | `phase`, `status` |
| `smoke.baseline.recorded` | At Smoke A | `checks`, `evidence_type` |
| `audit.verify.recorded` | At AUDIT_VERIFY | `graphify_terrain_used`, `activegraph_custody_used`, `sidecar_in_tracked_source` |
| `implementaudit.run.finalized` | At AUDIT_COMPLETE | `verdict`, `graphify_live`, `activegraph_live` |

Custody boundaries:
- ActiveGraph custody stores are written to `.IMPLEMENTAUDIT/` (gitignored) or an authorized temp path outside tracked source.
- Custody stores, event logs, graph exports, and `.db` files are never committed, pushed, or included in the `.skill` package.
- ActiveGraph absence is not a blocker. Markdown ledger and final report remain first-class fallback.
- Capability Ledger entries derived from ActiveGraph readback must be narrow: repo, run id, owner/source, quality route, Lean principles applied, Graphify terrain used (yes/no), ActiveGraph event ids, checks run, final status, remaining risk. No broad competence claims.

## Evidence boundaries

- No Lean/TPS certification is claimed.
- No sigma level, DPMO, or statistical process control values are claimed.
- DMAIC/DMADV are routing and evidence-shaping patterns for audit-governed repo work, not Six Sigma certification claims.
- 5S applies to run-root hygiene, package payloads, and generated artifact cleanliness, not physical workplaces.
- Obeya maps to visual diagrams and ROADMAP.md, not a physical coordination room.
- Graphify terrain is orientation evidence, not proof. All Graphify-derived candidates require live-file confirmation.
- ActiveGraph custody is evidence of gate passages, not correctness proof. Capability Ledger entries remain narrow.
- All claims are bounded by local repo checks, smoke evidence, and IMPLEMENTAUDIT runtime behavior.
