# IMPLEMENTAUDIT.md

IMPLEMENTAUDIT is an audit-governed implementation method for repo-changing agent work. Every mutation is bounded by an audit contract.

Source file for the docs portal. Generated into _site/index.html by
scripts/build-docs-portal.py. Do not hand-edit the generated output; edit this file
and re-run the generator.

## Overview

**IMPLEMENTAUDIT** is an audit-governed implementation method for repo-changing agent work. It transforms intent, findings, handoffs, checklists, reviews, goals, tasks, gaps, and implementation plans into bounded repository mutations by first constructing or binding a `tdqyq-audit-object`, then acting through `ydqyq-audit-action` operations until terminal audit closure (`AUDIT_COMPLETE`) or an explicit audited handoff (`AUDIT_HANDOFF` / `ANDON_HANDOFF`).

**The bottleneck it addresses.** AI agents can produce repository changes faster than humans can review evidence of ownership, rollback viability, generated-artifact freshness, CI state, and public-claim accuracy. IMPLEMENTAUDIT moves that review discipline into the implementation loop rather than leaving it only at the final review step. Review is not post-hoc; it is per-gate.

:::info
**Design invariant.** Every finding closes. No orphan items. No unsafe actions. No proof claim without evidence. `IMPLEMENTAUDIT_RUN_COMPLETE` is invalid before `AUDIT_COMPLETE`.
:::

IMPLEMENTAUDIT is not a release bot, a package publisher, a provenance system, or a generic autonomous build loop. It is a runtime that binds implementation to evidence-bearing audit closure for every run, in every invocation shape.

## Quick Start

### 1. What governs a run

Every run first constructs or binds a `tdqyq-audit-object` before any mutation. The object tracks scope, findings, owner/source decisions, evidence type, and closure state. `ydqyq-audit-action` operations read and mutate this object. Implementation is only permitted through the object.

### 2. Try a simple invocation

With the skill installed:

    /implementaudit implement these findings
    /implementaudit < audit-findings.md
    /goal using /implementaudit, close the findings in AUDIT.md

### 3. Default authorization stance

:::warning
**No commit. No push. No tag. No release. No publication. No provenance.** Each action requires separate explicit authorization. No invocation shape implies any downstream action.
:::

### 4. Navigate by concern

- New to IMPLEMENTAUDIT? Start at [Mental Model](#mental-model).
- Invoking from an agent? See [Invocation Model](#invocation-model).
- Reviewing a completed run? See [What AUDIT_COMPLETE Means](#what-audit-complete-means) and [Evidence and Audit Trail](#evidence-and-audit-trail).
- Auditing gate behavior? See [Audit Gate Model](#audit-gate-model).
- Understanding run artifacts? See [State and Artifact Model](#state-and-artifact-model).

## Install

### Codex

Manual copy from a repo checkout:

    mkdir -p ~/.codex/skills/implementaudit
    cp -R skills/* ~/.codex/skills/implementaudit/

From the v0.2.9.0 release asset with checksum verification:

    bash scripts/build-release-asset.sh
    bash scripts/install-codex-from-release.sh \
      --asset dist/IMPLEMENTAUDIT.skill \
      --checksum dist/CHECKSUMS.txt \
      --codex-home "$HOME/.codex" \
      --version 0.2.9

### Claude Code

Use the host's current plugin instructions with `.claude-plugin/plugin.json` as package metadata. For public clone/plugin setup, an HTTPS repo URL is the simplest path.

For a release-asset Claude Desktop path, `bash scripts/install-claude-from-release.sh --claude-skills-dir <path>` extracts and checksum-verifies the asset into a Claude skill directory. That proof covers extraction and integrity only — verify the skill loads in the host after restart.

### Release state

Release `v0.2.9.0` is live (verified against the GitHub release list at the 2026-06-10 release gate). Tag at commit `23f67b5` (the CI-green pushed head). The release asset `IMPLEMENTAUDIT.skill` includes a `CHECKSUMS.txt` — a SHA-256 checksum manifest for local integrity verification only. No signatures, attestations, SBOMs, or provenance chains are claimed. Pages docs are live and CI-verified (deploy workflow success at the pushed head plus a live HTTP 200, verified 2026-06-10). External claims in this section carry their evidence basis; re-verify on each release gate.

:::info
**No auto-update mechanism exists.** A locally installed skill does not update automatically when the GitHub repo has a new release. Repeat the install step on each release.
:::

## For New Users

You have just discovered IMPLEMENTAUDIT.md. Start here.

### card: What is it?

An audit-governed implementation skill. Every repo change must pass audit gates before the run can complete. Read the Mental Model first to understand the execution chain.

- [-> Mental Model](#mental-model)
- [-> Overview](#overview)

### card: How do I invoke it?

Four invocation shapes: direct governance, embedded governance, goal synthesis, governed casual-build intake. All four bind an audit object before mutation.

- [-> Invocation Model](#invocation-model)
- [-> Quick Start](#quick-start)

### card: How do I verify a run succeeded?

AUDIT_COMPLETE is the terminal marker. Read what it means and — critically — what it does not mean.

- [-> What AUDIT_COMPLETE Means](#what-audit-complete-means)
- [-> Evidence and Audit Trail](#evidence-and-audit-trail)

## For Agents and Operators

You are invoking `/implementaudit` from a coding agent or CI pipeline.

### card: Which invocation shape applies?

Your invocation shape determines how the audit object is sourced and when mutation is permitted. Direct governance, embedded governance, goal synthesis, and governed casual-build intake each have different mutation conditions.

- [-> Invocation Model](#invocation-model)
- [-> Usage Examples](#usage-examples)

### card: What are the non-skippable gates?

Ten gates form the execution spine. Each must pass before the next. If a gate cannot pass honestly — Andon. Do not advance past a failing gate.

- [-> Audit Gate Model](#audit-gate-model)
- [-> Operating Method](#operating-method)

### card: What sidecars are available?

Graphify (terrain/orientation) and ActiveGraph (custody/events) are both optional. Sidecar absence is not a blocker for ordinary user runs. Neither proves correctness.

- [-> Continuity and Sidecars](#continuity-and-sidecars)
- [-> Optional Tooling](#optional-tooling)

## For Auditors and Maintainers

You are reviewing a completed run or maintaining the IMPLEMENTAUDIT repo itself.

### card: Where is the evidence?

Every run must record a Smoke A/B comparison, owner/source mapping, and closure state. Dogfood audit ledgers link to specific run evidence for each release.

- [-> Evidence and Audit Trail](#evidence-and-audit-trail)
- [-> What AUDIT_COMPLETE Means](#what-audit-complete-means)

### card: What is the artifact model?

Run artifacts live under `.IMPLEMENTAUDIT/runs/<slug-id>/`. The state model defines what each artifact is responsible for proving — and what it is not.

- [-> State and Artifact Model](#state-and-artifact-model)
- [-> Repo Layout](#repo-layout)

### card: Intra vs inter maintenance?

IMPLEMENTAUDIT maintaining itself (intra-run) differs from IMPLEMENTAUDIT applied to another repo (inter-run) in sidecar authorization scope, ownership boundary, and continuity preload authority.

- [-> Continuity and Sidecars](#continuity-and-sidecars)
- [-> Safety and Boundaries](#safety-and-boundaries)

## Mental Model

The execution chain for every IMPLEMENTAUDIT run, regardless of invocation shape:

    Input / intent
      -> audit-object binding or synthesis
      -> route classification (greenfield / brownfield / mixed)
      -> Gemba (live-file inspection, not summaries)
      -> Smoke A (baseline verification before mutation)
      -> owner/source patch (not nearest symptom)
      -> generated-artifact refresh (follow generator policy)
      -> Smoke B (post-mutation comparison against Smoke A)
      -> trace / custody (commit body, ledger, AGENTS.md decision)
      -> final audit (terminal verification of all claims)
      -> AUDIT_COMPLETE
      -> IMPLEMENTAUDIT_RUN_COMPLETE

:::info
**Casual-build intake is not ungated autonomy.** Governed casual-build intake is an entry route that synthesizes a bounded `tdqyq-audit-object` from the user's natural-language intent *before* any mutation. The same gates apply as in direct governance. The difference is only how the audit object is constructed — not whether gates are enforced.
:::

**Two audit senses — keep them distinct.**

`tdqyq-audit-object` is the audit-as-noun: the evidence-bearing record for the run. It contains scope, findings, owner/source decisions, claims, changed files, checks, and closure state. Everything the run claims is bounded by what this object contains.

`ydqyq-audit-action` is the audit-as-verb: a runtime operation performed against the audit object — inspecting, classifying, verifying, authorizing or rejecting mutation, closing findings, handing off. Patching owner/source is an `ydqyq-audit-action`; a passing CI check is evidence but does not itself mutate the audit object.

`AUDIT_COMPLETE` is a terminal `ydqyq-audit-action` verdict over the `tdqyq-audit-object`. It is not a progress label. `IMPLEMENTAUDIT_RUN_COMPLETE` is invalid before it.

## Invocation Model

`/implementaudit` has four invocation shapes. Each determines how the audit object is sourced, whether a `/goal` is emitted, and when mutation is permitted.

| Shape | Input | Audit-object source | `/goal` emitted? | Mutation allowed when | Failure / handoff |
|---|---|---|---|---|---|
| **Direct governance** | Concrete audit, handoff, checklist, review, or bounded plan | Bound from the supplied artifact | No | Audit object is live, gates pass | `AUDIT_HANDOFF` or `ANDON_HANDOFF` |
| **Embedded governance** | Host `/goal` or active task already in flight | Inherited from the outer goal/task/plan | Never — would create an illegal nesting | Outer object is live, inner gates pass | Andon inside the outer audit object; no nested `/goal` |
| **Goal synthesis** | Idea, gap, incomplete target, or ambiguous request | Synthesized through Gemba and phase planning | Yes, once at Stage 7 (never if already embedded) | After the emitted `/goal` is accepted | Emits a bounded handoff; does not itself mutate |
| **Governed casual-build intake** | Natural-language repo-build intent | Synthesized from intent before routing | No | Synthesized object passes the input gate, then routes as greenfield / brownfield / mixed | `AUDIT_HANDOFF` if synthesis fails or scope is unbounded |

:::warning
**Embedded governance must never nest.** If the run is already inside a `/goal`, emitting a second `/goal` is a protocol violation. Embedded governance governs the active object in place.
:::

No invocation shape bypasses the audit gates. Governed casual-build intake is not an escape hatch; it is a front-end that produces the same type of audit object that direct governance starts with.

## Audit Gate Model

Ten gates form the non-skippable execution spine. Each gate must pass before the next. If a gate cannot pass honestly, stop and emit an **Andon** — do not pretend the run is complete.

| Gate | Purpose | Owner / source | Evidence | Halt condition |
|---|---|---|---|---|
| **0. Safety / read policy** | Read `AGENTS.md`, `CONTRIBUTING.md`, CI config, repo policy. Classify authorization level. | `AGENTS.md`, `CONTRIBUTING.md` | Static read and classification recorded | STOP if the requested action is unsafe, unauthorized, or contradicts repo policy without an explicit owner decision. |
| **1. Input / audit-object gate** | Confirm the input is a recognizable audit artifact, or synthesize a `tdqyq-audit-object` from intent. | The supplied artifact or the user's intent | `AUDIT_START` marker; bound or synthesized object | STOP if input is empty, malformed, not an audit artifact, and not synthesizable via governed casual-build intake. |
| **2. Context / continuity preload** | Load prior run state, `AGENTS.md` rules, optional notes, optional sidecar orientation. Priority: live files first; sidecar context is orientation only. | `.IMPLEMENTAUDIT/runs/<slug>/`, `AGENTS.md`, optional notes | Applied-context log; priority-order record | Block only if a required pre-flight item is absent. Missing optional tooling is not a failure. |
| **3. Route gate** | Classify work as greenfield, brownfield, or mixed. Determine applicable methodology: DMADV or DMAIC. | Repo state, file inventory | Route classification in `THINKING.md` | Block mutation if route is unclear and risk is non-trivial. |
| **4. Gemba gate** | Inspect actual files — not summaries, not memory. Identify owner/source, existing tests, generator policies, regression surface. | Live repo files | File reads and documented inspection | Do not mutate until live Gemba is recorded. |
| **5. Smoke A gate** | Run baseline verification before any mutation. Classify pre-existing failures: target, unrelated, or unclear. | Test suite, CI-equivalent checks | Smoke A output; pre-existing failure classification | Do not mutate until baseline is recorded. Unrelated failures require Andon if risk is non-trivial. |
| **6. Patch gate** | Apply P0 to P1 to P2 priority. Patch owner/source — not nearest symptom. Refresh generated artifacts per generator policy. Guard scope creep. | Owner/source files identified in Gemba | Changed files; scope-creep register | Andon if owner/source is unclear, generator policy is unresolved, or a dependency blocks. |
| **7. Smoke B gate** | Compare post-mutation checks against Smoke A. Any Smoke-A-passing check that now fails triggers the regression protocol. | Same checks as Smoke A | Smoke B output; Smoke A/B comparison | Regression protocol if any passing check now fails. Do not advance without recorded comparison. |
| **8. Trace / custody gate** | Preserve the causal chain: commit body (if authorized), audit ledger, durable `AGENTS.md` rule (if warranted), optional ActiveGraph custody event. | Commit body draft, ledger, `AGENTS.md` decision | Proposed commit message; ledger entries; `AGENTS_UPDATE_DECISION` | Do not finalize until all authorization boundaries are explicit. Local commit is not push; push is not tag; tag is not release; release is not provenance. |
| **9. Final audit gate** | Terminal `ydqyq-audit-action` over the complete `tdqyq-audit-object`. Every item reaches a terminal status. Claims are verified against evidence. | All changed files, generated artifacts, release assets if in scope | `AUDIT_VERIFY` marker; `AUDIT_COMPLETE` marker | Fix, revert, defer, block, or mark unverified before `AUDIT_COMPLETE`. `IMPLEMENTAUDIT_RUN_COMPLETE` is invalid before `AUDIT_COMPLETE`. |

### How this maps to SKILL.md's execution spine

`skills/SKILL.md` presents the same run as an **8-row execution spine** (gates 0–7). The two decompositions describe one contract: this portal model splits the spine's pre-flight row into separate context/continuity-preload and routing gates for teaching purposes (10 = 8 + 2 split-outs). When in doubt, the SKILL.md spine is canonical; this table is the annotated tour.

## Shipped Scripts Reference

The installed payload carries nine bash helpers under `scripts/`. They are the consumer's hands; each is read-only or side-effect-bounded, and all resolve via `"${IMPLEMENTAUDIT_SKILL_DIR:-skills}"/scripts/<helper>`:

| Helper | Loop | What it does |
|---|---|---|
| `detect-env.sh` | L1 planning | Environment recon: runtimes, tools, helper-layer availability, skill-dir resolution, native variables |
| `detect-stack.sh` | L1 planning (brownfield) | Target-repo stack profile: languages, frameworks, layout, configs |
| `summarize-repo.sh` | L1 planning (brownfield) | Owner/regression map; discovers the target repo's own checkers as mandatory-command candidates |
| `claim-run.sh` | L2 run | Atomically claims a namespaced run root; advises (never writes) a local gitignore entry for run artifacts |
| `validate-audit-spec.sh` | L1→L2 | Rejects malformed audit/goal/slice specs before they govern work |
| `validate-phase.sh` | L3 phase | Rejects malformed phase specs before execution; errors name the expected shape |
| `validate-run-root.sh` | L2 resume | Structural conformance of a live run root (Status enum, Andon log columns, ROADMAP↔phase completeness) — run before resuming an interrupted run |
| `repo-state.sh` | L3/L5 evidence | Complete working-tree-vs-baseline evidence (changed files, added lines, deliverables); run-root artifacts excluded visibly |
| `custody-append.sh` | any (sidecar) | One-command, absent-safe ActiveGraph custody event emission |

Shared contract across all nine: every helper degrades honestly — absence, missing baseline, or failure produces a recorded weaker-evidence note, never a silent pass.

## Abnormality Handling (Andon Escalation)

When any gate cannot pass honestly, the run does not retry blindly and does not stop on a counter. It enters the Andon escalation sequence — the Jidoka loop: abnormality, stop, understand why, countermeasure, rerun evidence.

| Marker | Fires when | Must record |
|---|---|---|
| `ANDON_PROBE` | The **first** abnormality of any class | The abnormality and its class; failing criterion, command, or artifact; owner/source; containment decision; a 5 Whys drill proportional to the issue; Hansei (gap, cause, countermeasure, follow-up evidence); the selected countermeasure; the rerun evidence required. A fix must follow from the probe, never from the visible symptom alone. |
| `ANDON_ESCALATE` | The first countermeasure fails, the **same-class** abnormality recurs, the root cause stays unclear, the fix would expand scope, or the owner/source is disputed | Prior probe history; why the countermeasure failed; a deeper 5 Whys; `New evidence:` and/or `Changed approach:` — if neither can be truthfully filled, the run evaluates handoff conditions instead of escalating; the chosen path (split, reframe, rollback, owner decision, or a bounded fix-spec). A recurrence claim must cite the prior same-class Andon log rows by number. |
| `ANDON_HANDOFF` | Closure is blocked by an owner decision, unsafe scope, missing authorization, an external dependency, irreproducibility, missing tooling or access, or no bounded countermeasure remains | Full probe and escalation history, the blocking condition, the remaining blocker, and the smallest next concrete action for a human owner. It is never "third try failed" — a try count alone cannot trigger handoff. |

Every event is one classed row in the run-root STATE.md `## Andon log` (in a non-phased run, the findings ledger serves as the log). The ten abnormality classes are: failed-criterion, regression, hung-command, substituted-command, owner-unclear, generated-artifact-mismatch, stale-sidecar, policy-conflict, impossible-criterion, evidence-mismatch.

:::info
There is no arbitrary attempt cap and no capped audit-round count anywhere in the runtime. Escalation is driven by same-class recurrence with new evidence; handoff is driven by genuine blocking conditions. A transcript containing `ANDON_HANDOFF` must never also contain `IMPLEMENTAUDIT_RUN_COMPLETE`.
:::

## What AUDIT_COMPLETE Means

`AUDIT_COMPLETE` is a verifiable terminal state, not a sentiment. It means all of the following are true simultaneously:

1. **All ledger items are terminally classified.** Each item is `done`, `changed`, `blocked`, `deferred`, or `unverified`. Zero items remain `open`.
2. **Claims do not exceed evidence.** Every behavioral claim is tagged with its evidence type: live runtime, local generated-runtime, package-bound, unit test, integration test, static checker, manual inspection, visual/browser, or unverified. Static evidence is never upgraded to live proof.
3. **Changed files map to owner/source.** Each patch traces to a ledger item and to the owner/source identified in Gemba. No unexplained mutations exist in the changeset.
4. **Generated outputs follow generator policy.** If a source generator exists for an artifact, the generator was updated rather than the generated artifact being hand-edited directly.
5. **Smoke A/B comparison is recorded.** The pre-mutation baseline (Smoke A) and post-mutation state (Smoke B) are both recorded. Any regression was handled by the regression protocol or classified as pre-existing.
6. **Release / publication / provenance boundaries are explicit.** Local commit is not push. Push is not tag. Tag is not release. Release is not provenance. None implies another. Each is a separate explicit gate.
7. **`IMPLEMENTAUDIT_RUN_COMPLETE` follows `AUDIT_COMPLETE`.** The run-complete marker is invalid before the audit-complete marker. An agent that emits run-complete before audit-complete has violated the terminal protocol.

`AUDIT_COMPLETE` does **not** mean:

- Marketplace verification — no listing or publication has been verified.
- Universal install proof — host-specific install must be verified on the target host with that host's tooling.
- Provenance — no signing, attestation, SBOM, or checksum chain is produced unless a dedicated gate authorizes it.
- Graphify proof — Graphify is orientation evidence; the run does not inherit Graphify output as proof of correctness.
- ActiveGraph correctness proof — ActiveGraph records custody/event evidence; it proves gate passages were recorded, not that the implementation was correct.
- A felt sense of completion — evidence determines terminal state, not the agent's confidence.

:::danger
**The most common protocol violation is emitting `IMPLEMENTAUDIT_RUN_COMPLETE` before `AUDIT_COMPLETE`.** All run invariants and gate conditions must be verified before the run is declared complete.
:::

## State and Artifact Model

A run's persistent state lives under `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/`. This table defines the artifact model — what each artifact owns and what it cannot prove.

| Artifact | Owner | Purpose | Proof boundary |
|---|---|---|---|
| `tdqyq-audit-object` | The run | Evidence-bearing record: scope, findings, owner/source, claims, changed files, checks, closure state. | Everything the run claims is bounded by this object's contents. |
| `ydqyq-audit-action` | Runtime | Operations that read or mutate the audit object: inspect, classify, verify, authorize or reject mutation, close, hand off. | Not a file; a runtime operation category. |
| `ROADMAP.md` | Planner | High-level phase plan: goals, phases, dependencies, milestone. | Orientation only — not a commitment to immutable scope. |
| `STATE.md` | Runtime | Live run state: Status enum token, current phase, findings ledger, classed Andon log, authorization stance. | Run-state record; custody events live in the run root's `custody.db`, not here. |
| `tools.md` | Runtime | Stage 0 detection record: skill-dir resolution, helper-layer availability, runtimes, sidecar status. | Detection evidence only. |
| `context.md` | Runtime | Stage 0 operating context: baseline ref, working-tree state, invocation shape, route, repo instructions read. | Intake record; live files win on conflict. |
| `THINKING.md` | Runtime | Per-phase live reasoning: Gemba notes, Smoke A/B results, 5-Whys drill, route classification, Muda/Mura/Muri register, DMAIC/DMADV fields. | Internal reasoning record; not a public claim. |
| `PROTOCOL.md` | Runtime | Step-by-step execution log; gate completions; `CONTINUITY_DECISION`; `AGENTS_UPDATE_DECISION`; 5S_CHECK results; Jidoka stop-the-line events. | Protocol execution record. |
| `sidecars.md` | Runtime | Sidecar tool availability, authorization state, output summaries (Graphify node count, ActiveGraph event count). | Orientation and custody evidence — not correctness proof. |
| `applied-context.md` / `applied-memories.md` | Runtime | Loaded continuity state from prior runs, personal notes, or project notes. | Orientation only — live files and `AGENTS.md` take priority. |
| `repo-map.md` | Runtime | Graphify-assisted or manual repo structure map: owner/source candidates, dependency density, stale assumptions. | Orientation — not a substitute for live-file inspection. |
| `phases/phase-N.md` | Planner / runtime | Per-phase spec: goal, acceptance criteria, rollback plan, Quality route (DMAIC/DMADV/PDCA), evidence plan. | Phase-scoped claim boundary. |
| `AGENTS_UPDATE_DECISION` | Owner | Decision record for whether to add a durable anti-repeat rule to `AGENTS.md`. | Documents the decision; does not auto-apply it. |
| `CONTINUITY_DECISION` | Runtime | Per-phase continuity writeback decision: none / repo-local `AGENTS.md` rule / run-local applied-context / optional personal note / optional ActiveGraph event. | Documents the boundary for continuity writes. |
| `IMPLEMENTAUDIT_CONTINUITY_SAVED` | Runtime | Six-field marker recording a completed continuity writeback: `Target`, `Reason`, `Evidence`, `Boundary`, `Authorization`, `Not saved`. | Records that writeback occurred and its boundary — not that the content is correct. |
| Final audit ledger | Runtime | Closure table: all audit items with terminal status, evidence type, and reference. | The primary evidence surface for `AUDIT_COMPLETE`. |

## Continuity and Sidecars

### Continuity preload priority order

When IMPLEMENTAUDIT loads context for a run, it follows this priority order. Higher-priority sources override lower-priority sources on conflicts:

1. **Live repo files and `AGENTS.md`** — authoritative. Always consulted first. Never overridden by any sidecar or memory.
2. **Run-root applied-context** (`applied-context.md`, `applied-memories.md`) — prior run state for this task.
3. **Optional personal or project notes** — human-curated guidance; used when available and authorized.
4. **Graphify terrain** — orientation evidence about repo structure and link density. Not proof; absence is not a failure.
5. **ActiveGraph custody events** — chain-of-custody evidence for prior gate passages. Not correctness proof; absence is not a failure.

### Two-tier sidecar policy

Optional everywhere; canonical only for maintaining IMPLEMENTAUDIT itself. Users running the skill on their own repos never need either sidecar — absence blocks nothing. Maintenance and dogfood rounds on the IMPLEMENTAUDIT repo are expected to use both (owner decision, recorded in `AGENTS.md`).

### Sidecar conventions

When the sidecars are present and authorized, their placement is concrete, not decorative. Graphify terrain is agent-extracted to `graphify-out/graph.json` (gitignored, never packaged) and queried for orientation — owner/source candidates by degree, dependency paths, artifact classification — with every result confirmed against live files before action. ActiveGraph custody uses one store per run root (`custody.db`), written with the packaged absent-safe `custody-append.sh` helper; Andon escalation mirrors into custody as classed `andon.probe.recorded` / `andon.escalated` / `andon.handoff.recorded` events, so the failure-handling chain survives session boundaries. Later runs preload prior stores read-only. Reconstructed history must carry `custody_mode: historical_backfill` with its source and evidence boundary — live and backfilled custody never blur. Run-level status lives in `sidecars.md`, instantiated from the packaged template.

:::warning
**Continuity context is orientation, not authority.** No continuity source overrides live files or `AGENTS.md`. If a memory or sidecar suggests an action that contradicts live `AGENTS.md`, `AGENTS.md` wins.
:::

### Sidecar model

| Sidecar | Evidence type | Canonical use | Ordinary user runs | Intra-maintenance runs |
|---|---|---|---|---|
| **Graphify** | Terrain / orientation | Gemba orientation: find owner/source candidates, dependency paths, stale assumptions. | Optional — absent is not an error. | Canonical when available and authorized. |
| **ActiveGraph** | Custody / events | Gate-passage record; Capability Ledger source material. | Optional — absent is not an error. | Canonical when available and authorized. |

Neither sidecar proves correctness. Live files remain source of truth regardless of sidecar output.

### Intra vs inter distinction

| Dimension | Intra-run (IMPLEMENTAUDIT maintaining itself) | Inter-run (IMPLEMENTAUDIT applied to another repo) |
|---|---|---|
| **Sidecar authorization scope** | Sidecars may be canonical when already configured and authorized in `.claude-plugin/plugin.json` or `AGENTS.md`. | Sidecars are optional unless explicitly authorized by the target repo's `AGENTS.md` or owner. |
| **Ownership scope** | The IMPLEMENTAUDIT repo's own files are owner/source. | The target repo's files are owner/source. IMPLEMENTAUDIT does not impose its own policies. |
| **Continuity preload authority** | Prior intra-run `STATE.md` and `PROTOCOL.md` are first-class inputs. | Prior inter-run context may be loaded but must not override the target repo's `AGENTS.md`. |
| **Generator policy** | Changes to `build-docs-portal.py` must be reflected in the generated portal before claiming it is current. | Target repo's generator policy applies; IMPLEMENTAUDIT does not impose its own generator policy on the target. |

### No install, index, or export without authorization

Tool installation, Graphify indexing, ActiveGraph event-store setup, and sidecar export are all separate explicit gates. They are never implied by an audit run.

## Operating Method

IMPLEMENTAUDIT integrates Lean and quality-management disciplines as auditable runtime behavior, not as decorative labels.

### PDCA

Plan the smallest safe change with explicit owner/source and verification command. Do it. Check the evidence against the Smoke A baseline. Act — standardize if successful, revise or revert if failed. Update the closure ledger.

### Gemba

Go to the real place of work. Inspect actual files, not summaries or memory. For non-code artifacts (skills, prompts, config, markdown), Gemba means reading the artifact directly and identifying structural, logical, or semantic issues.

### Smoke Before Claim

Every behavior claim must be tagged with its evidence type (live runtime / local generated-runtime / package-bound / unit test / integration test / static checker / manual inspection / visual/browser / unverified). Static evidence is never upgraded to live proof. If a live check cannot run, state the evidence type and remaining risk explicitly.

### Andon

Surface blockers, failures, unclear ownership, or unsafe conditions immediately. Do not hide failure. Do not mark "mostly done." Do not advance to the next gate while the current gate cannot honestly pass.

### Hansei

Structured reflection after any failure, regression, false pass, or gap: name the gap, the cause, the countermeasure, and the follow-up evidence. Used with 5 Whys.

### 5 Whys

Trace symptoms to root cause: why did the symptom occur, why did that condition exist, why did the system allow it, why was it not caught earlier, what prevents recurrence? If the root cause is out of scope or requires an OWNER DECISION, log to the scope-creep register and defer.

### Plan Closure

Every item maps to exactly one terminal status: `done`, `changed`, `blocked`, `deferred`, or `unverified`. No item may remain `open` at `AUDIT_COMPLETE`.

## Routing

IMPLEMENTAUDIT classifies work before mutation. The classification determines the applicable methodology and intake process.

| Route | What it means | Methodology | Intake |
|---|---|---|---|
| **Greenfield** | New artifact with no prior owner/source, tests, or regression surface. | DMADV: Define, Measure, Analyze, Design, Verify | Define scope, acceptance criteria, rollback plan, and evidence plan before first mutation. |
| **Brownfield** | Existing repo surface with established owner/source, tests, and regression surface. | DMAIC: Define, Measure, Analyze, Improve, Control | Inspect owner/source, tests, generator policies, regression surface before mutation. |
| **Mixed** | New artifact introduced inside an established repo. | Brownfield shell (DMAIC) + greenfield sub-artifact (DMADV) | Brownfield outer inspection first, then greenfield intake for the new artifact only. |
| **Governed casual-build** | Natural-language intent is the starting point; no audit object yet exists. | Synthesis then greenfield, brownfield, or mixed | Synthesize a bounded `tdqyq-audit-object` from intent, then route the synthesized object. |

### Counterexamples

- Adding a function to an existing file that has tests: **brownfield** (not mixed — no new top-level artifact is created).
- Creating a new configuration file in an established repo: **mixed** (the file is greenfield; the surrounding repo is brownfield).
- Interpreting "make the docs portal better" as a direct mutation request: **not valid** — this is governed casual-build intake; it requires audit-object synthesis before any mutation.
- Running a fix on a brand-new empty repo: **greenfield** (no brownfield surface to protect).

## Comparison

The following table compares tool categories based on published behavior. No external tool is named.

| Approach | Audit object | Gates | Mutation discipline | Continuity | Polish / harden |
|---|---|---|---|---|---|
| **Normal prompt** | None | None | Ungated; agent decides | None | None |
| **Normal `/goal`** | Implicit (the goal state) | Implicit; depends on host | Agent-discretion with phases | Optional; host-managed | None |
| **Low-friction staged-goal runner** | Implicit (staged goal state) | Phase-gated; runner-managed | Gated per phase | Per-phase writeback (runner-managed) | Typically none |
| **IMPLEMENTAUDIT** | Explicit `tdqyq-audit-object`, constructed or bound before mutation | Ten explicit gates with documented halt conditions | Requires Gemba, owner/source, Smoke A/B, evidence type | Bounded five-source priority preload and per-phase `CONTINUITY_DECISION` | Optional Polish and Harden phase (Rule P4-8) |

### Behaviors shared with staged-goal runners

These behaviors are common in low-friction staged-goal runners. IMPLEMENTAUDIT includes them as native audit-governed runtime discipline:

- **Casual invocation:** governed casual-build intake synthesizes the audit object from natural-language intent.
- **Continuity preload:** five-source priority order, loaded before any mutation, orientation only.
- **Per-phase continuity writeback:** `CONTINUITY_DECISION` in every phase's `PROTOCOL.md`, with five bounded options including `IMPLEMENTAUDIT_CONTINUITY_SAVED`.
- **Optional polish/harden:** Rule P4-8 — an optional terminal phase covering cleanliness, identity hygiene, generated-artifact freshness, and proof-boundary wording.

### What IMPLEMENTAUDIT refuses

These behaviors are absent by design:

- **Ungated mutation:** no change happens outside an audit object with at least one passing gate check.
- **Unbounded autonomy:** every scope-expanding action requires either an owner decision or explicit re-authorization.
- **Proof without evidence:** every claim must cite an evidence type and remaining risk.
- **Hidden publication / release / provenance:** local commit authorization does not imply any downstream action.

## Usage Examples

### Basic invocations

    /implementaudit implement these findings
    /implementaudit < audit.md
    /implementaudit --onboard-tools
    /goal using /implementaudit, close the findings in AUDIT.md
    /implementaudit make the CI workflow generate and deploy the docs portal

Natural-language requests such as *implement these findings*, *act on this audit*, *close these items*, or *work through this handoff* are valid direct-governance invocations.

### Governed casual-build intake example

User says: *"Make the docs portal generated by CI and prove it is fresh."*

1. IMPLEMENTAUDIT detects governed casual-build intake: natural-language intent, no supplied audit object.
2. It synthesizes a `tdqyq-audit-object`: scope = CI-generated docs portal with freshness proof; acceptance = CI workflow runs build and validate; portal accessible at Pages URL; metadata contains current commit SHA.
3. Routes as mixed: new CI workflow file is greenfield; existing repo is brownfield.
4. Proceeds through all ten gates — Gemba, Smoke A, Patch, Smoke B, trace, final audit.
5. `AUDIT_COMPLETE` only after CI run is verified and portal is live.

### Worked trace

    Finding: README describes behavior that no longer matches skills/SKILL.md.

    Owner/source: skills/SKILL.md defines the behavior.
                  README.md is derived public documentation.

    Smoke A: Read skills/SKILL.md and README.md.
             Run git diff --check.

    Countermeasure: Patch README.md to match current skills/SKILL.md.

    Smoke B: Run git diff --check -- README.md.
             Inspect evidence wording in the changed lines.

    Closure: Status changed. Commit only if explicitly authorized.

## Default Behavior

The default small-audit mode operates on one artifact at a time. It:

- Validates the input is a recognizable audit artifact, or synthesizes one for governed casual-build intake.
- Normalizes findings into a ledger with priority classification: **P0** (blocks goal or safety), **P1** (named in audit), **P2** (nice-to-have), **OWNER DECISION**, **DEFERRED**, **OUT OF SCOPE**.
- Processes in P0 to P1 to P2 order.
- Patches owner/source, not nearest symptom.
- Requires evidence for every claim.
- Runs Smoke B after implementation and records the A/B comparison.
- Closes every item terminally — zero open items at `AUDIT_COMPLETE`.

## Terminology

| Term | Meaning |
|---|---|
| `tdqyq-audit-object` | Audit-as-noun: the evidence-bearing record for a run — scope, findings, owner/source, claims, changed files, checks, closure state. |
| `ydqyq-audit-action` | Audit-as-verb: a runtime operation against the audit object — inspect, classify, verify, authorize or reject mutation, close, hand off. |
| `AUDIT_START` | Opens, inherits, or normalizes the `tdqyq-audit-object` at the start of a run or phase. |
| `AUDIT_COMPLETE` | Terminal verified closure. All items classified. Claims do not exceed evidence. |
| `IMPLEMENTAUDIT_RUN_COMPLETE` | Run-level completion marker. Invalid before `AUDIT_COMPLETE`. |
| `IMPLEMENTAUDIT_CONTINUITY_SAVED` | Six-field writeback marker: `run_id`, `phase`, `target`, `content_hash`, `boundary`, `timestamp`. |
| Owner/source | The canonical file, schema, script, fixture, or doc that owns a claim or behavior. Patch this, not the nearest symptom. |
| Gemba | Go to the real place of work. Inspect actual files, not summaries. |
| Smoke A / Smoke B | Pre-mutation baseline verification (A) and post-mutation comparison (B). Any regression triggers the regression protocol. |
| Andon | Visible blocker signal. Surface immediately — do not hide failure or advance past a failing gate. |
| Hansei | Structured reflection: gap, cause, countermeasure, follow-up evidence. |
| 5 Whys | Root-cause drill: symptom, condition, system gap, prevention gap, recurrence countermeasure. |
| DMAIC | Brownfield methodology: Define, Measure, Analyze, Improve, Control. |
| DMADV | Greenfield methodology: Define, Measure, Analyze, Design, Verify. |
| Graphify | Optional terrain/orientation sidecar. Not proof; absence is not an error. |
| ActiveGraph | Optional custody/event sidecar. Not correctness proof; absence is not an error. |
| Continuity preload | Loading prior run state and orientation context before any mutation. Priority order: live files and `AGENTS.md` → run-root applied-context → optional personal/project notes → Graphify terrain → ActiveGraph custody events. |
| Continuity writeback | Recording run findings for future runs via `CONTINUITY_DECISION`. Five options: none / repo-local `AGENTS.md` rule / run-local applied-context / optional personal note / optional ActiveGraph event. A completed writeback is stamped with `IMPLEMENTAUDIT_CONTINUITY_SAVED`. |
| `CHECKSUMS.txt` | SHA-256 checksum manifest for local integrity verification of the release asset. Not a signature, attestation, SBOM, or provenance chain. |

## Repo Layout

| Path | Role |
|---|---|
| `AGENTS.md` | Authoritative project doc. Gate 0 reads this first. |
| `README.md` | Public-facing overview and install guide. |
| `CHANGELOG.md` | Milestone notes (Keep a Changelog). Evidence for claimed milestones. |
| `skills/SKILL.md` | Canonical method definition. Source of truth for all gate behavior. |
| `skills/references/` | Progressive-disclosure reference docs: `routing.md`, `goal-format.md`, `planning-depth.md`, `phase-design.md`, `lean-operating-discipline.md`. |
| `skills/scripts/` | Planner-executed bash helpers: `claim-run.sh`, `repo-state.sh`. |
| `skills/templates/` | Run artifact templates: `PROTOCOL.md`, `THINKING.md`, `phase-goal.txt`, `STATE.md`. |
| `scripts/` | Repo validation tools: release, docs portal generator and checker, workflow structure checker. |
| `tests/` | Shell test suites: continuity, routing, lean-discipline, docs-portal, phase-validation, and more. |
| `fixtures/` | Test fixtures for behavioral claims including casual-build, continuity, and routing scenarios. |
| `docs/portal_old/onboarding.md` | This file. Portal content source. |
| `docs/audits/` | Dogfood audit ledgers by version. |
| `docs/diagrams/` | Mermaid source for execution spine and tooling diagrams. |
| `.claude-plugin/plugin.json` | Plugin manifest. Version 0.2.9. |
| `.github/workflows/pages.yml` | Docs portal build and deploy. `workflow_dispatch` enabled. |
| `.github/workflows/validate.yml` | Full test and check suite. |

## Optional Tooling

IMPLEMENTAUDIT integrates with two optional external tools. Neither is required for ordinary user runs.

**Graphify** provides terrain and orientation evidence. Use it during Gemba to identify likely owner/source candidates, trace dependency paths, and surface stale assumptions. It is orientation evidence — not proof. Live files remain source of truth regardless of Graphify output. Graphify absence is not an error.

**ActiveGraph** provides chain-of-custody evidence for audit gate passages. Use it to record gate events and derive Capability Ledger entries. It is custody evidence — not correctness proof. ActiveGraph absence is not an error.

For ordinary user runs, both sidecars are optional. For IMPLEMENTAUDIT self-maintenance (intra-runs), both are canonical when available and authorized — their outputs support faster Gemba and richer custody evidence, but they still cannot override live files or `AGENTS.md`.

:::success
**Markdown fallback is first-class.** When Graphify and ActiveGraph are absent, IMPLEMENTAUDIT uses ordinary Gemba, ordinary ledgers, and ordinary final reporting. This is not a degraded mode.
:::

:::warning
**No install without authorization.** Tool installation, Graphify indexing, ActiveGraph event-store setup, and sidecar exports are separate explicit gates — never implied by a run.
:::

## Safety and Boundaries

These actions require **explicit authorization** — a direct imperative in the chat interface. References to CI, deployment, release plans, or implied workflows do not count as authorization.

- Commit
- Push
- Tag
- Publish
- Create or update releases
- Delete data
- Alter credentials or secrets
- Rewrite history
- Commit raw diagnostic outputs
- Hand-edit generated artifacts when a source generator exists
- Claim proof without evidence

Authorization is **per-action and non-transitive**:

- Local commit authorization is not push authorization.
- Push authorization is not tag, release, or publication authorization.
- Release authorization is not provenance authorization.
- No combination of the above implies any other action.

:::danger
**`AGENTS.md` conflicts are OWNER DECISION.** If an audit finding contradicts `AGENTS.md`, the agent must surface the conflict as a human decision — not silently choose which instruction wins.
:::

## What It Does Not Do

`/implementaudit` is not:

- **A release bot.** It does not push, tag, or publish without explicit per-action authorization.
- **A provenance system.** `CHECKSUMS.txt` is a SHA-256 integrity manifest — not a signature, attestation, SBOM, or provenance chain.
- **A package publisher.** Release assets require separate authorization per action.
- **A generic autonomous-build loop.** Every mutation happens under an audit contract with explicit gates.
- **A framework-specific tool.** It is repo-generic and does not assume language, CI system, or release conventions.
- **A marketplace lister.** No marketplace publication or update has occurred.
- **A universal install verifier.** Install proof on a specific host requires running the install on that host.

:::info
**The authoritative reference is always `skills/SKILL.md` and `AGENTS.md`.** When in doubt, go to Gemba — read the source.
:::

## Evidence and Audit Trail

The v0.2.8.0 adaptation lane closed G1-G7 comparator-advantage gaps. G5 (per-phase continuity writeback) is classified **STRENGTHENED**: the v0.2.6.0 PROTOCOL loop was the base; v0.2.8.0 added the `IMPLEMENTAUDIT_CONTINUITY_SAVED` marker with six required fields, a bounded writeback options table (five options), an ActiveGraph custody path, a Graphify terrain-update request, and a 34-check continuity test suite (+9 new checks).

- `docs/audits/INDEX.md` — full dogfood history index
- `docs/audits/v0.2.8.0-adaptation.md` — v0.2.8.0 gap closure ledger (G1-G7)
- `docs/audits/v0.2.8.0-docs-portal-ci-onboarding.md` — docs portal CI and onboarding audit
- `docs/audits/v0.2.8.0-docs-portal-coherence-polish.md` — docs portal coherence and prose quality audit
- `docs/diagrams/` — Mermaid source for execution spine, invocation modes, and tooling diagrams

## Audit Status

Current release and deployment facts.

- **Version:** v0.2.8.0
- **Plugin manifest:** 0.2.8
- **Release:** Live. Tag `v0.2.8.0` at commit `d2829a4`. Release asset `IMPLEMENTAUDIT.skill` with `CHECKSUMS.txt` (SHA-256 checksum manifest only — no signatures, attestations, SBOMs, or provenance chains claimed).
- **Pages docs:** Live and CI-verified. `workflow_dispatch` enabled on `pages.yml` for manual rebuild.
- **G5 status:** STRENGTHENED — v0.2.6.0 PROTOCOL loop base; v0.2.8.0 added `IMPLEMENTAUDIT_CONTINUITY_SAVED` marker, bounded writeback options, and 34-check continuity test suite.
- **Graphify:** Optional sidecar for user runs; canonical for intra-maintenance when available and authorized. Orientation evidence only — not proof.
- **ActiveGraph:** Optional sidecar for user runs; canonical for intra-maintenance when available and authorized. Custody evidence only — not correctness proof.
- **Marketplace:** No marketplace publication or update has occurred.
- **Methodology scope:** The comparison table covers methodology dimensions only. No all-domain obsolescence claim is made.
