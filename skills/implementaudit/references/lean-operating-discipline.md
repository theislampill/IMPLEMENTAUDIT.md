# Lean Operating Discipline

IMPLEMENTAUDIT implements Lean/TPS concepts as runtime behavior, template fields,
checkers, and final-audit rules. Lean terms are not decorative labels. Every term
below maps to a concrete runtime behavior or gate.

## Concept mapping table

| Lean term | IMPLEMENTAUDIT behavior | Owner/source | Evidence/check |
|---|---|---|---|
| Gemba / Genchi Genbutsu | Inspect live files/artifacts/outputs before any claim. Gemba is a non-skippable execution-spine gate. Do not diagnose from summaries when the live artifact exists. | `SKILL.md` §Gemba | `check-planner-stages.sh` |
| A3 thinking | Maps to the `tdqyq-audit-object`: problem, current condition, target condition, root cause (5 Whys), countermeasure, acceptance criteria, owner/source, evidence, follow-up, sustainment. Must be concise and evidence-bearing, not a private reasoning dump. | `SKILL.md` §Canonical audit terminology | `check-planner-stages.sh` |
| Kaizen | Standardize countermeasures when durable: fold into templates, AGENTS.md anti-repeat rules, checkers, or CI gates. CONTINUITY_DECISION at every phase boundary decides whether to standardize. A countermeasure declares its `scope` (targets / non_targets_checked / no_harm) before it is applied — see Countermeasure Scope And Verification Proportionality. | `AGENTS.md`, `templates/phase-goal.txt` | `check-planner-stages.sh` |
| Hansei | Required structured reflection after: false pass, regression, abnormal release-gate command, substituted command, stale generated artifact, or owner intervention. Record: gap, cause, countermeasure, follow-up evidence; the countermeasure field carries its declared `scope`. | `SKILL.md` §Hansei | `check-planner-stages.sh` |
| Jidoka | Stop-the-line when evidence fails. Trigger: any proof failure, regression, hidden rerun, substituted command, package-boundary violation, or release-asset mismatch. Chain: Andon → ANDON_PROBE → Hansei → 5 Whys (when warranted) → owner/source countermeasure → Kaizen standardization decision → re-run evidence → close/block/defer/handoff. No arbitrary try or round cap; ANDON_HANDOFF only on a genuine blocking condition. | `templates/PROTOCOL.md` §Jidoka stop-the-line | `check-planner-stages.sh` |
| Andon | Visible abnormality signal. Print Andon block with: status, blocker, failing check, owner/source, next concrete action. Do not hide failure. Do not mark "mostly done." | `SKILL.md` §Andon | `check-planner-stages.sh` |
| Nemawashi | Surface consequential assumptions before dispatch. Tie to Stage 6 plan review: release/package/AGENTS.md/sidecar-status changes require explicit owner-aware review before Stage 7 handoff. | `SKILL.md` §Nemawashi, `templates/PROTOCOL.md` | Stage 6 Self-critique |
| 5S — Seiri (Sort) | Classify necessary vs unnecessary artifacts. Log scope creep and debris as new findings rather than absorbing them. Sort package payload (skills/) from repo-only material. | `templates/PROTOCOL.md` §5S, `templates/phase-goal.txt` | `check-lean-discipline.sh` |
| 5S — Seiton (Set in order) | Every artifact has a canonical place: owner/source, run root, docs, tests, package payload, release asset. Enforced by package manifest and source repo only `verify-package.sh` (not shipped in runtime payload). | `.claude-plugin/plugin.json`, source repo only `scripts/verify-package.sh` | source repo only `verify-package.sh` |
| 5S — Seiso (Shine) | Clean generated docs, debug prints, session markers, sidecar debris, run-root debris, package bloat, stale outputs. Per-phase cleanliness check (Step 9 of phase loop). | `check-added-lines-clean.sh` (source repo), `templates/PROTOCOL.md` | `check-added-lines-clean.sh` |
| 5S — Seiketsu (Standardize) | AGENTS_UPDATE_DECISION at every phase: does the countermeasure belong in template/checker/AGENTS.md/CI? Kaizen standardization decision in Jidoka chain. | `templates/phase-goal.txt` §AGENTS_UPDATE_DECISION | `check-lean-discipline.sh` |
| 5S — Shitsuke (Sustain) | Add or verify a sustain check so the issue does not regress: test, checker, CI gate, or AGENTS.md rule. Sustain evidence required in phase transcript. | `check-lean-discipline.sh` and its focused test (source repo) | `lean-discipline.test.sh` |
| Muda (waste) | Unnecessary files, redundant checks, overbroad scope, dead artifacts, duplicate docs. Log in THINKING.md §Muda/Mura/Muri register. Muda is removed or logged as scope-creep; it is not silently absorbed. | `templates/THINKING.md` | `check-lean-discipline.sh` |
| Mura (unevenness) | Phase-size imbalance, inconsistent evidence levels, stale generated docs. Log in THINKING.md. Mura triggers phase rebalance or Stage 6 review. | `templates/THINKING.md` | Stage 6 Self-critique |
| Muri (overburden) | Too much in one phase, too many manual checks, unsafe owner assumptions, overloaded release gate. Log in THINKING.md. Muri triggers split/defer/owner decision. | `templates/THINKING.md` | OWNER DECISION gate |
| Poka-yoke | Structural mistake-proofing via: `validate-phase.sh` (19 failure modes), `check-public-claim-boundaries.sh`, `check-lean-discipline.sh`, `check-terminology-integration.sh`, `check-routing.sh`, `check-public-claim-boundaries.sh`, `check-planner-stages.sh`. Gates prevent wrong-state, invalid-spec, orphan-terminology, or glossary-theater execution. | `check-lean-discipline.sh` and `check-terminology-integration.sh` (source repo), packaged `validate-phase.sh` | `verify-package.sh` |
| Obeya / visual control | README Mermaid diagrams provide visual runtime overview (execution-spine, invocation-modes, tooling-architecture). Source repo only `generate-readme-diagrams.sh --check` enforces freshness. ROADMAP.md provides phased visual plan. | `docs/diagrams/`, source repo only `scripts/generate-readme-diagrams.sh` | source repo only `generate-readme-diagrams.sh --check` |
| DMAIC | Brownfield improvement routing: Define (defect/gap/scope/target) → Measure (Smoke A/baseline) → Analyze (root cause/Muda/Mura/Muri class) → Improve (owner/source patch/regenerate/checks) → Control (sustain via tests, AGENTS.md, CI, package gates). Use for existing defects, regressions, release repairs, stale docs, broken checkers. | `references/routing.md` §DMAIC | `check-routing.sh` |
| DMADV | Greenfield/replacement routing: Define (new capability/users/constraints) → Measure (CtQ acceptance measures/evidence/risk) → Analyze (design alternatives/dependencies/rollback) → Design (phase specs, templates, fixtures, validation) → Verify (Smoke B/final audit/package boundary/owner acceptance). Use for new governed artifacts, new runtime capabilities, replacement designs. | `references/routing.md` §DMADV | `check-routing.sh` |
| Standard Work | Repeated countermeasures become templates, checkers, fixtures, AGENTS.md rules, or CI gates only when stable and repo-specific. PROTOCOL.md per-phase loop is the standard work template for governed execution. | `templates/PROTOCOL.md`, `templates/phase-goal.txt` | `verify-package.sh` |
| Control Plan | Plan Closure names how the fix stays fixed: sustain owner/source, prevention check, validation cadence, package/CI gate, and explicit defer/handoff if no durable control can be safely added. | `references/plan-lifecycle.md`, `templates/phase-goal.txt` | `check-terminology-integration.sh` (source repo) |
| Terminology integration | External method terms must attach to native parent, runtime phase, route/lens, owner/source, evidence boundary, Andon trigger, and fixture/checker. Glossary-only additions are defects. | `references/terminology-integration.md` | `check-terminology-integration.sh` (source repo) |

## Graphify terrain leverage

Graphify is optional first-contact reconnaissance. All triggers must hold: the
repo is unfamiliar to this run, majority-code by file count, the question is
terrain-shaped, and one `rg`, `git grep`, or `git ls-tree` query cannot answer
it. Graphify is orientation only, not proof; live-file confirmation remains
mandatory. Absence, a failed trigger, or an anti-trigger falls back to ordinary
Gemba and `repo-state.sh` without blocking the run.

Before a query, execute `validate-run-root.sh --graph-freshness <graph.json>
<repo-root>`. It compares `built_at_commit` with `git rev-parse HEAD`; mismatch
fires `stale-sidecar` and makes the terrain unusable. Extraction/re-extraction
remains separately authorized, uses `--code-only --no-cluster` by default, and
places `--out` outside the target repo.

| Lean step | Narrowed terrain use | Live-file confirmation required |
|---|---|---|
| Seiri / Sort | On first contact, orient to broad code artifact classes and possible component boundaries. | Confirm every class with `git ls-files`, `git ls-tree`, or direct reads before recording it. |
| Seiton / Set in order | On first contact, locate the neighborhood of an already named code component and candidate owners. | Read the candidate owner/source and confirm links with deterministic searches before action. |

Seiso, Muda/Mura/Muri, DMAIC Measure/Analyze, and DMADV Analyze/Design do not
gain a Graphify capability claim. Use their ordinary live-file, checker, and
Git instruments. The known limitations as tested are citable anti-triggers:

- data-file consumers are not represented reliably;
- module-level constants and duplicated literals are not represented;
- embedded-language code (such as heredoc Python) is not extracted;
- prose/reference censuses and Git topology are outside the code graph.

This qualification is dogfood-only, as tested on two repos, one Windows host,
Python 3.11.9, graphifyy 0.9.33, ActiveGraph 1.10.0, on 2026-08-05. It is not a
universal tool claim. A read-only unfamiliar-third-party-repo trial is the
broadening gate.

## ActiveGraph custody events

ActiveGraph's evidenced use is authorized `fork` / `diff`
resume-from-checkpoint. The run root remains the sole authority for lifecycle
facts. A custody store and its IMPLEMENTAUDIT-defined custom events may be an
optional non-authoritative mirror; they are not required event work and cannot
repair a run root that was not maintained. `replay` does not reconstruct the
tested custody use case from custom event names.

The former catalogue is retained only as a compact compatibility sample for
existing stores: `implementaudit.run.opened`, `gemba.graphify.queried`,
`dmaic.define.recorded`, `poka_yoke.check.recorded`, and
`implementaudit.run.finalized`. The packaged helper also recognizes
`andon.probe.recorded`, `andon.escalated`, and `andon.handoff.recorded` for an
authorized optional mirror. Do not infer completeness, required emission, or
upstream schema support from these names.

Custody boundaries:
- ActiveGraph custody stores are optional mirrors written only after separate authorization.
- Custody stores, event logs, graph exports, and `.db` files are never committed, pushed, or included in the `.skill` package.
- ActiveGraph absence is not a blocker. Markdown ledger and final report remain first-class fallback.
- Capability Ledger entries, if configured, remain narrow derivatives of recorded run-root gate evidence; no broad competence claims.

## Evidence boundaries

- No Lean/TPS certification is claimed.
- No sigma level, DPMO, or statistical process control values are claimed.
- DMAIC/DMADV are routing and evidence-shaping patterns for audit-governed repo work, not Six Sigma certification claims.
- 5S applies to run-root hygiene, package payloads, and generated artifact cleanliness, not physical workplaces.
- Obeya maps to visual diagrams and ROADMAP.md, not a physical coordination room.
- Graphify terrain is orientation evidence, not proof. All Graphify-derived candidates require live-file confirmation.
- An ActiveGraph mirror may reflect gate passages but is not lifecycle authority or correctness proof. Capability Ledger entries remain narrow.
- All claims are bounded by local repo checks, smoke evidence, and IMPLEMENTAUDIT runtime behavior.
- A step described as read-only is evidence of non-mutation only when the
  post-state was compared; a command label or intent does not prove its effect.

## Verdict capture fidelity

A mandatory verification command captures its complete stdout and stderr in a
run-root evidence file before any excerpt is read. Transcript tails and heads
are excerpts from that completed capture, never a capture policy and never a
live pipe from the producer. Orientation-only tails remain valid when they are
not registered as verification evidence.

The producer process exit status is verdict authority. Do not infer success
from output text or from the exit status of `tail`, `head`, `Tee-Object`, or any
other downstream stage. Prefer no pipeline. If a pipeline is unavoidable, use
`set -o pipefail` or record the producer's `${PIPESTATUS[0]}` before any chained
gate. Never chain `&&` from an unqualified pipeline status.

On hosts that may re-encode native streams, record `command`, `exit_code`,
`started`, and `finished` in a structured file. PowerShell CLIXML and text
captured through `Tee-Object` are diagnostics only; they do not replace the
producer exit status or the structured record.

Declare `coverage: full|partial` on newly authored evidence rows. Mandatory
commands require `coverage: full`, a named capture file, and complete output.
`coverage: partial` records both the observed `range:` and the `omission:`. A
transport truncation marker forces `coverage: partial`; partial evidence cannot
establish completeness, absence, or terminal success.

## 5 Whys Loop-Exit Protocol

5 Whys is proportional, not infinite. Stop the loop when the root cause is
owner/source actionable and the countermeasure can be verified. Also stop when
the next why requires unavailable external information, when the next why would
expand scope beyond the audit object, or when the next why requires an owner
decision.

Rule phrase: requires an owner decision.

Escalate to Andon or handoff when blocked. Do not create arbitrary try caps,
retry counts, fixed-count ladders, audit-round ceilings, or fixed iteration limits.
The exit condition is evidence: actionable root cause, unavailable information,
scope expansion, owner decision, or no bounded countermeasure remaining.

## Countermeasure Scope And Verification Proportionality

**Countermeasure scope.** Every countermeasure recorded in a Hansei entry, a
Jidoka chain, or a Kaizen standardization decision declares its scope before
it is applied:

```text
scope:
  targets: <the surfaces the countermeasure is aimed at>
  non_targets_checked: <the surfaces it also reaches, and how they were checked>
  no_harm: <one line: why the non-targets are unaffected, or what changed for them>
```

When the countermeasure is text injected into a shared channel — a prompt, a
mission preamble, a template every unit renders, a global config — the
non-target set is *everything else in that channel*, and `no_harm` must say
how that was established. A global scope is permitted; an undeclared one is
not. If the information needed to partition targets from non-targets already
exists in the run, cite it; do not re-derive it and do not skip it.

A countermeasure that regresses a declared non-target is a `regression` Andon
against the countermeasure itself, not a new defect in the non-target.

**Verification proportionality.** A verification step proposed *after* a prior
verification of the same object already passed must state the specific
residual risk it retires and the cost of that risk if left unretired. If the
verification costs more than the risk, close instead and record the residual.
A declared scope gap in a passing verification (`PASS_WITH_SCOPE_GAP` and
equivalents) is an input to this judgment, not an automatic trigger to build a
larger verification apparatus.

This rule is judgment-shaped and deliberately not mechanical. It is not a cap:
it imposes no round, attempt, or audit-count ceiling (see `No Arbitrary
Revision Cap` in `plan-lifecycle.md` and the try-cap prohibition in
`SKILL.md`). Verification invented to occupy a wait, a quota window, or a
blocked interval retires no risk by construction and is Muda — log it in the
`THINKING.md` Muda/Mura/Muri register rather than running it.

## Environment-quirk memoization

When the same normalized host or tool error reaches a second distinct linked
occurrence, keep the official `transport-infrastructure` class and add the
`Blocker: environment-quirk (...)` discriminator. Record either a
`Workaround:` or a reasoned `Not memoized:` disposition in the existing Andon
row. A workaround produces exactly one append-only machine-local row in the
repo-level `.IMPLEMENTAUDIT/host-notes.md`; a documented refusal produces no
row. A first occurrence and two distinct signatures create no memoization
obligation.

At phase start and after a continuity boundary, consult host notes before
repeating a workaround. Keep host facts on that machine-local surface. If a
lesson is portable, route it through the existing `AGENTS_UPDATE_DECISION`
governance decision; do not copy host-specific trivia into the skill payload.
