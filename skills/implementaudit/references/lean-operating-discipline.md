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
| 5S — Seiton (Set in order) | Every artifact has a canonical place: owner/source, run root, docs, tests, package payload, release asset. Enforced by the package contract and source repo only `verify-package.sh` (not shipped in runtime payload). | `package/implementaudit-package.json`, source repo only `scripts/verify-package.sh` | source repo only `verify-package.sh` |
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

Trigger: unfamiliar majority-code terrain with no targeted answer;
orientation only, not proof; live-file confirmation is mandatory. `sidecars.md` owns
authorised extraction, freshness, `llm: false`, fallback.

Seiri/Seiton orient code/owners; Seiso/DMAIC/DMADV gain no proof.
Anti-triggers: data consumers, module-level constants/literals, prose census,
Git topology:
- embedded-language code (such as heredoc Python) is not extracted;

dogfood-only: Windows, graphifyy 0.8.37 (2026-08-09); 14-file scope beat root;
both missed a variable-bound call. Semantic/Luna/partitions unproved.

## ActiveGraph custody events

Authorised `fork` / `diff` or a non-authoritative mirror; run-root authority;
`replay` cannot reconstruct. IMPLEMENTAUDIT-defined custom events (non-required):
`implementaudit.run.opened`, `gemba.graphify.queried`,
`dmaic.define.recorded`, `poka_yoke.check.recorded`,
`implementaudit.run.finalized`, `andon.probe.recorded`, `andon.escalated`,
`andon.handoff.recorded`. Custody stores/graphs/`custody.db`: separate authority;
never committed/packaged; no Markdown repair; narrow claims.

## Evidence boundaries

- No Lean/TPS/Six Sigma certification, sigma/DPMO/SPC or physical 5S/Obeya
  claim; DMAIC/DMADV shape evidence only.
- Graphify needs live files; ActiveGraph is no lifecycle/correctness proof.
- Capability Ledger entries remain narrow.
- Non-mutation is proved only when post-state was compared.

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

## Engineering-value admission, retention, and retirement

Apply the action-selection invariant and compact record defined in
`planning-depth.md` throughout a process control's lifecycle; reuse an existing
audit, action-selection, Muda/Mura/Muri, countermeasure, or closure surface. The
record supports a decision but does not prove the protected property.
Protective slack, sustainable capacity, feedback cadence, temporary options,
and control depth share that decision: require a live consumer and consequence,
actionable information, bounded cost, and an exit. Retain an option only while
information value exceeds carrying cost and its exit condition remains current.
No trigger means no new record, ceremony, or runtime mode.

Use these lifecycle dispositions:

- **Retain** while the consumer and consequence remain live and no cheaper
  equivalent is proved. A demonstrated defect-catching gate qualifies.
- **Cheapen** only with proved equivalent protection and lower marginal cost.
- **Merge** only when one authority preserves every consumer and evidence need.
- Make **conditional** only what depends on a trigger absent from ordinary work.
- **Retire** only after the failure mode, consumer, and consequence end and
  rollback evidence exposes no hidden dependency.
- **Reclassify** when risk, scope, authority, or external consequence changes.
Disposition labels never self-authorise:

- **Defer** only an incomplete mutation while its controlling gate remains intact.
- Use **Unresolved** only when mechanical evidence cannot distinguish at least
  two supported alternatives; it is not deliberate deferral.
- Use **owner decision** only for a non-mechanical expected-risk and permanent-cost trade-off. Low frequency does not defeat a defensible high-consequence control.

Human-readable handoffs, authorisations, work orders, and review or release
receipts can be essential. Ask who consumes one, which decision or recovery
changes, what becomes unsafe or unknowable without it, whether another authority
owns it, and when it can retire. Machine consumption alone establishes no value;
a duplicate status artefact without a distinct consumer is a merge or retirement candidate.

Without a prior exact PASS, run qualification. After PASS, repeat only for a new
residual or mutation family. Reuse only when exact bytes, other relevant state,
consumer identity, authoritative consumer, and evidence scope are unchanged;
changed scope or consumer requires a fresh run. Keep producer, scope, and
residual visible; command identity cannot make changed-state evidence reusable.

Parallelism follows `child-agents.md`: one shared owner does not serialise disjoint cells; no shared owner or shared write remains parallel-safe. Known independence is not activation. Serialise only a conflicting
cell, keep all boundaries closed, and name the join. Reconsider the ready frontier after a material scheduling-state change; dispatch is value-bearing work, not a concurrency or utilisation target.

Process volume is not value evidence. A consumer without a protected consequence,
a form without the property, optional-by-whim relabelling, or a split that does
not lower real cost fails. Add no mandatory control ledger, numerical ceremony
threshold, per-command defence, or large worksheet. Use the progressive path in
`planning-depth.md`; when no factor fires, create no R0022 record or model call.

## Package semantic preservation

A package or footprint failure is not closed by a smaller artefact alone. Use
the existing package finding/evidence row when the repair changes shipped
content, moves an owner or required consumer, changes package membership or an
installed path, follows the change into generated/public material, or changes
a checker, fixture, threshold, golden, prompt, or expected answer because the
candidate failed. Do not create a package-only lifecycle, ledger, or marker.

The R0022 admission rule still governs cost. Record the smallest evidence that
names the live driver, authoritative owner and consumer, protected consequence,
cheapest sufficient discriminator, expected evidence, marginal cost, non-trigger
path, and exit/retirement condition. If those fields do not support a permanent
control, defer or omit it while leaving the package failure and existing gates
truthful.

No semantic-preservation record is needed for ordinary non-package work.
Exact extracted-member and metadata-policy equality is sufficient for an archive or
compression-algorithm change when no shipped owner or consumer predicate
changes. Harmless whitespace/deduplication stays cheap when owner-backed
predicates and required consumers are equivalent. These mechanical paths make
no model call.

For a triggered change, record exact before/after package identity, size,
members, headroom and changed blobs; classify the change; state the behaviours
at risk as owner-backed predicates; distinguish exact literals whose bytes are
owned by a parser, checker, public promise, canonical event token, or
interoperability contract; enumerate every required runtime, checker,
installed, generated, and public consumer; and prove reachability/parity.
Retaining a phrase while breaking its consumer is a failure. Changing a phrase
is neither an automatic PASS nor an automatic failure when no exact-byte owner
exists.

Closure is one of: harmless compression with extracted consumers unchanged;
equivalent refactor with predicates and consumers proved equivalent; a
progressive split whose owner is shipped, same-run reachable, tested, and
publicly projected where required; an authorised architecture change with
migration and rollback; or a visible calibration/owner decision. Content in an
unshipped or unreachable owner, a failed held-out consumer, or unresolved
headroom conflict cannot become PASS.

R0023 governs every post-failure evaluator mutation. Preserve the original witness
and complete mutation record, and require independent property evidence
before accepting a changed checker, fixture, threshold, golden, prompt, or
expected answer. Weakening the measurement surface, leaking the expected answer,
or retaining a proxy while the governed property fails is not semantic closure.

Rollback restores the last semantically complete owner and consumer routes and
reruns the unchanged byte gate. If restored semantics do not fit, keep the
package failure visible and route to architecture, evidence-derived calibration,
or owner decision; never recover headroom by deleting governed behaviour.

## Environment-quirk memoization

When the same normalized host or tool error reaches a second distinct linked
occurrence, keep the official `transport-infrastructure` class and add the
`Blocker: environment-quirk (...)` discriminator. Record either a
`Workaround:` or a reasoned `Not memoized:` disposition in the existing Andon
row. A workaround produces exactly one append-only machine-local row in
`.IMPLEMENTAUDIT/host-notes.md` at the repository-family root (the parent of
Git's common directory), shared by linked sibling worktrees; a documented
refusal produces no row. A first occurrence and two distinct signatures create
no memoization obligation.

At phase start and after a continuity boundary, consult host notes before
repeating a workaround. Keep host facts on that machine-local surface. If a
lesson is portable, route it through the existing `AGENTS_UPDATE_DECISION`
governance decision; do not copy host-specific trivia into the skill payload.
