# AGENTS.md

Authoritative project doc. Any agent (Claude, Codex, or other) opening this repo should be able to read this file alone and understand the project, where to make changes, and what conventions to follow.

---

## What this repo is

**IMPLEMENTAUDIT** is a Claude Code / Codex skill for turning audit findings, handoffs, checklists, reviews, goals, tasks, gaps, and implementation plans into bounded, verified repo changes.
IMPLEMENTAUDIT’s primary model is audit closure and repo hygiene. It can use a staged planner when no sufficient goal exists, but when a goal/task/plan already exists, it should govern that target rather than inventing a second planning layer.

Core invariant:

```text
Every finding closes. No orphan items. No unsafe actions. No proof claim without evidence.
```


Default authorization stance:

```text
No commit. No push. No tag. No release. No publication. No provenance.
```

Each action needs separate explicit authorization.

---

## Operating vocabulary

Kaizen — Continuous improvement
Apply Kaizen: improve the smallest repeatable part of the process, measure it, and fold it into the standard.

Hansei — Structured reflection
Use Hansei after failure: name the gap, cause, countermeasure, and follow-up evidence.

Hoshin Kanri — Policy deployment / alignment
Use Hoshin Kanri lightly: align projects, metrics, owners, and review cadence to the top objective.

Nemawashi — Laying groundwork / consensus before change
Use Nemawashi: surface the proposed change, affected owners, tradeoffs, and rollback before forcing the decision.

---

- Slash command: `/implementaudit <audit | handoff | checklist | review | goal | task | plan | gap>`
- Central mechanism: audit-closure governance for a supplied or synthesized work target.
  - If a goal/task/plan is already supplied, including `/goal using /implementaudit ...`, ImplementAudit wraps that work in its gates: safety read, input normalization, owner/source patching, Smoke A/B, evidence boundaries, final ledger closure, and repo-local anti-repeat learning.
  - If only an idea, gap, audit artifact, or incomplete plan is supplied, ImplementAudit may first synthesize the bounded plan and return a ready-to-paste `/goal Using /implementaudit ...`.
- Works on: Claude Code and Codex when the packaged skill is installed or copied into the host skill directory.
- Public install: see `README.md`; do not claim install flows are verified unless tested in that host.

## Invocation modes

ImplementAudit has three valid invocation shapes.

### 1. Embedded governance mode

Used when the user has already supplied a host goal/task/plan, especially inside a `/goal` runner.

Examples:

```text
/goal using /implementaudit, close the findings in AUDIT.md
/goal using /implementaudit, apply this migration plan safely
```

In this mode, ImplementAudit does **not** print a second `/goal`. It treats the supplied goal/task/plan as the active work target and applies its gates inside that run.

### 2. Direct governance mode

Used when the user invokes `/implementaudit` with a concrete audit, handoff, checklist, review, or sufficiently bounded plan.

Examples:

```text
/implementaudit implement this handoff
/implementaudit close the findings in this review
/implementaudit work through this checklist
```

In this mode, ImplementAudit applies audit-closure hygiene to the supplied artifact. It may decompose the work into phases when the artifact is large, risky, or multi-step, but it should not invent a new high-level objective when the objective is already clear.

### 3. Goal-synthesis mode

Used when the user gives only an idea, gap, ambiguous audit target, or request for the next best implementation prompt.

Examples:

```text
/implementaudit for this package-structure gap
/implementaudit audit this repo state and give me the next best goal
/implementaudit turn this idea into the right implementation goal
```

In this mode, ImplementAudit performs enough Gemba and Hoshin Kanri to produce a bounded, evidence-aware Kaizen handoff. If execution should continue under a host goal runner, it prints a ready-to-paste `/goal Using /implementaudit ...` command.

---

## Repo layout

```
/
├── .claude-plugin/
│   ├── marketplace.json        Catalog Claude Code reads when added as a marketplace
│   └── plugin.json             Plugin manifest (name, version, description, skills path)
├── .gitattributes              Keeps shell scripts LF for Git Bash/WSL.
├── .gitignore                  Editor/OS junk + .IMPLEMENTAUDIT/ artifact dirs
├── AGENTS.md                   This file. Authoritative project doc.
├── CLAUDE.md                   Claude Code-specific tips. Points at this file.
├── CHANGELOG.md                Project milestone notes. Keep-a-Changelog style.
├── README.md                   Public-facing: what it is, install, use, Mermaid flow charts.
├── CONTRIBUTING.md             Short onboarding: what ImplementAudit is/is not, minimum method, worked flow.
├── .github/workflows/
│   ├── validate.yml            GitHub Actions validation mirror of local package checks.
│   └── pages.yml               GitHub Pages deployment (build + validate + deploy).
├── docs/diagrams/              Mermaid sources generated into README.md.
│   ├── tooling-architecture.mmd
│   ├── invocation-modes.mmd
│   └── execution-spine.mmd
├── docs/audits/
│   ├── INDEX.md                Compact dogfood-history evidence index.
│   └── v0.2.3.0-harness-adaptation-matrix.md
│                                Generic external-comparator adaptation matrix.
├── docs/portal/
│   └── onboarding.md           Portal content source; generated into dist/docs-portal/ by build-docs-portal.py.
├── fixtures/
│   ├── agent-eval/             Adversarial identity-misread eval inputs + expected transcript properties.
│   ├── child-agents/           Scoped AGENTS hierarchy and reviewer fixtures.
│   ├── lean/                   DMAIC/DMADV/mixed routing fixtures for Lean discipline.
│   ├── zero-optional-tool/     Complete Markdown fallback example.
│   ├── run-root-example/       Tracked exemplar run root (validator-passing, brownfield).
│   ├── phase-design/           Multi-phase plan outlines + DMADV greenfield phase exemplar.
│   ├── casual-build/           Governed casual-build intake accepted/rejected fixtures.
│   ├── routing/                Greenfield/brownfield/mixed routing EXPECTED fixtures.
│   ├── audit-spec/             Audit/goal/slice spec validation fixtures.
│   ├── sidecars/               Sidecar presence/absence/staleness fixtures.
│   └── simple-audit/
│       ├── AUDIT.md
│       ├── EXPECTED-LEDGER.md
│       ├── EXPECTED-TRANSCRIPT-SKELETON.md
│       ├── EXPECTED-ANDON-RECOVERY-SKELETON.md
│       └── EXPECTED-ANDON-HANDOFF-SKELETON.md
├── scripts/
│   ├── build-release-asset.sh  Build/extract-check IMPLEMENTAUDIT.skill.
│   ├── check-host-claims.sh    Guard unsupported host/release/license claims.
│   ├── check-added-lines-clean.sh Guard added-line debug/task-marker/overclaim drift.
│   ├── check-marker-order.sh   Guard final-audit transcript marker order.
│   ├── check-planner-stages.sh Guard native Stage 0-7 planner contract.
│   ├── check-readme-toc.sh     Guard README Contents anchors.
│   ├── generate-readme-diagrams.sh Generate/check README Mermaid blocks.
│   ├── check-routing.sh     Validate greenfield/brownfield routing fixtures.
│   ├── check-lean-discipline.sh  Poka-yoke gate: Lean terms implemented as behavior, not glossary.
│   ├── check-no-terminal-cap.sh  Poka-yoke gate: no terminal-cap failure wording in runtime docs.
│   ├── check-agent-eval-fixtures.sh  Structural gate for the agent-eval misread fixture pack.
│   ├── grade-agent-eval-transcript.sh  Grade a transcript against a fixture's Graded properties.
│   ├── check-validation-registry.sh  Meta-gate: every test is wired into verify-package and CI.
│   ├── build-docs-portal.py    Stdlib-only docs portal generator (reads docs/portal/onboarding.md).
│   ├── check-docs-portal.py    12-check validator for generated portal output.
│   ├── install-codex-from-release.sh Install a validated release asset into a Codex-style skill home.
│   ├── verify-package.sh       Repo/package validation.
│   └── write-release-checksums.sh Create/check release checksum manifest.
├── tests/                      Focused shell tests for package behavior.
└── skills/
    ├── SKILL.md                Canonical skill source.
    ├── references/             Progressive-disclosure docs the agent reads when needed.
    │   ├── planning-depth.md   What makes a plan deserve ...
    │   ├── phase-design.md     How to slice phases (adaptive count, no cap).
    │   ├── goal-format.md      /goal mechanics ...
    │   ├── transcript-contract.md Host/wrapper transcript marker contract.
    │   ├── routing.md          Greenfield/brownfield/mixed routing gates + DMAIC/DMADV.
    │   ├── repo-state-comparison.md Baseline-to-working-tree audit comparison.
    │   ├── lean-operating-discipline.md  Lean/TPS → IMPLEMENTAUDIT behavior mapping (ships in package).
    │   └── child-agents.md     Bounded review loops and non-authority boundaries.
    ├── scripts/                Bash scripts the planner executes during stages.
    │   ├── claim-run.sh        Atomic namespaced run-root claim helper.
    │   ├── detect-env.sh       Greenfield env recon.
    │   ├── detect-stack.sh     Brownfield repo contract/source detection.
    │   ├── repo-state.sh       Complete baseline-vs-working-tree helper.
    │   ├── summarize-repo.sh   Brownfield owner/regression map.
    │   ├── validate-audit-spec.sh Validate audit/goal/slice specs.
    │   ├── validate-phase.sh   Sanity-checks a phase spec (--explain prints the checklist).
    │   ├── validate-run-root.sh Structural conformance of a live run root (resume gate).
    │   └── custody-append.sh   One-command absent-safe ActiveGraph custody emission.
    └── templates/              Files the planner copies into a user's `.IMPLEMENTAUDIT/` dir.
        ├── ROADMAP.md          Phase plan with dependencies.
        ├── STATE.md            Live progress file (status enum, Andon log, ledger).
        ├── THINKING.md         Reviewable risk/dependency/evidence plan.
        ├── sidecars.md         Sidecar status, Graphify query log, custody store fields.
        ├── tools.md            Stage 0 tool/skill-dir/helper-layer detection record.
        ├── context.md          Stage 0 operating-context record.
        ├── phase-goal.txt      Phase spec skeleton (work, criteria, evidence, commands).
        ├── child-agent-report.md Read-only reviewer report shape.
        └── PROTOCOL.md         Execution loop + Andon escalation + final audit protocol.
```

## What ships vs what doesn't

- **Ships to consumers**: everything under `skills/`. The plugin manifest declares `skills: "./skills/"`.
- **Repo-only**: `README.md`, `CHANGELOG.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, fixtures, root scripts, and `.gitignore`.
- **Marketplace entry**: `.claude-plugin/marketplace.json` points at the plugin root. Do not claim marketplace behavior was verified unless actually tested.
- **License**: no `LICENSE` file is present until the owner selects a license and supplies license evidence.
- **Versioning**: project milestone `v0.2.9.0` maps to plugin manifest version
  `0.2.9`. The manifest uses
  host-conservative package metadata; project milestones are not tags,
  releases, publication, or provenance claims until the separate
  release/provenance gate actually performs and verifies those actions.
- **Root behavior file**: there is intentionally no tracked root
  `IMPLEMENTAUDIT.md` file. The repo name is the project name; canonical
  behavior lives in `skills/SKILL.md` and supporting references/scripts/templates.
  Do not recreate a mirror or pointer stub. Audit inputs named `AUDIT.md`
  remain valid run artifacts.

## How the skill works

ImplementAudit first identifies the invocation shape: embedded governance, direct governance, or goal synthesis.

In embedded governance mode, ImplementAudit is already inside a supplied host goal/task/plan, such as `/goal using /implementaudit ...`. It does not print a second `/goal`. It governs the active target with safety read, input normalization, Gemba, Smoke A/B, owner/source patching, evidence boundaries, final audit, and terminal ledger closure.

In direct governance mode, ImplementAudit receives a concrete audit, handoff, checklist, review, or bounded plan. It applies audit-closure hygiene to that artifact. It may decompose the work into phases when the artifact is large, risky, or multi-step, but it should not invent a new high-level objective when the objective is already clear.

In goal-synthesis mode, ImplementAudit receives only an idea, gap, ambiguous audit target, or request for the next best implementation prompt. It performs enough Gemba and Hoshin Kanri to produce a bounded, evidence-aware Kaizen handoff. If execution should continue under a host goal runner, it prints a ready-to-paste `/goal Using /implementaudit ...` command.

All modes preserve the same method:

- validate the input or synthesize a bounded target
- classify work as greenfield, brownfield, or mixed before planning or mutation
- inspect the real repo before making claims
- patch owner/source, not nearest symptom
- run Smoke A before mutation
- run Smoke B after mutation
- use Nemawashi before forcing owner decisions
- use Hansei after failure or false-pass
- apply Kaizen to fold repeatable improvements into the standard
- use Hoshin Kanri lightly to align phases, metrics, owners, and review cadence to the top objective
- classify regressions honestly
- close every ledger item terminally
- write durable repo-local anti-repeat rules to AGENTS.md when warranted
- keep CHANGELOG entries tied to the causal chain of the run
- do not commit, push, tag, release, publish, install tools, index Graphify, export ActiveGraph, or claim provenance without explicit authorization

Routing rule:

- Default to brownfield when an existing repo is present.
- Greenfield work introduces a new governed artifact or validation surface and
  must define owner/source, scope, constraints, acceptance criteria, rollback,
  evidence plan, generated-artifact plan, sidecar status, and canonical-vs-
  sidecar boundaries before implementation.
- Brownfield work mutates or verifies existing repo behavior and must inspect
  existing owner/source, contracts, tests/smokes/checkers, generated artifacts,
  sidecars, regression surface, and rollback path before mutation.
- Mixed work is greenfield inside brownfield: inspect the existing repo first,
  then run greenfield intake for the new artifact.
- Generated artifacts are not independent owners.
- Graphify is optional terrain, not proof. ActiveGraph is optional custody, not
  canonical proof. Markdown ledgers and final reports remain valid fallback.
- ADHLBS may discipline an audit as reference input, but it is not a runtime
  source, package dependency, or acronym list for skill output.
- IMPLEMENTAUDIT is audit-governed implementation: it plans deeply and executes
  repo work phase-by-phase until terminal audit closure or an explicit audited
  handoff. It is not a generic autonomous build runner (execution without audit
  governance) and not "audit-only" (inspection without execution). Blocked work
  ends in an explicit audited handoff, not fake completion.
- External staged-goal skills are comparator inputs only. If a comparator
  exposes useful harness discipline, classify each concept as adapted,
  already-covered, intentionally-rejected, blocked, or deferred in an audit
  matrix, then re-implement useful behavior through native IMPLEMENTAUDIT
  helpers, references, templates, fixtures, or checkers. Do not import external
  package identity, markers, artifact paths, or autonomous-runner framing.
- Use bounded continuity only when a phase or final audit surfaces a stable,
  non-obvious, future-useful learning. Record `CONTINUITY_DECISION`; keep
  transient logs, private diagnostics, secrets, local-only failures, and
  unsupported claims out of AGENTS.md and memory.
- Final audits, deliverable checks, release-readiness checks, and cleanliness
  scans use baseline-to-working-tree evidence, including committed,
  staged, unstaged, deleted, and untracked work. Do not rely on a commit range
  that can miss local working-tree changes.

When phase planning is needed, planner stages are:

```text
0. Context/tool/memory detection
1. Intake
2. Recon / Gemba
3. Deep think
4. Phase decomposition
5. Write .IMPLEMENTAUDIT/runs/<task-slug>-<id> runtime artifacts
6. Plan review + self-critique
6.5 Pre-flight smoke check
7. Print one ready-to-paste /goal, only if not already inside a /goal run
```

Runtime artifacts:

```text
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/ROADMAP.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/STATE.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/THINKING.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/PROTOCOL.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/context.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/tools.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/sidecars.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/applied-context.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/repo-map.md
.IMPLEMENTAUDIT/runs/<task-slug>-<id>/phases/phase-N.md
```

Flat `.IMPLEMENTAUDIT/*` files remain legacy resume/audit compatibility, not
the preferred target for new run artifacts. `skills/scripts/claim-run.sh`
atomically claims new run roots. Namespaced planning artifacts prevent
artifact clobbering; true parallel source editing still requires separate git
worktrees.

`THINKING.md` is reviewable planning evidence for top objective, route,
owner/source, risks, dependencies, rollback, evidence strategy, generated
artifacts, sidecar boundaries, and owner decisions. It is not private
chain-of-thought or proof by itself.

Slash commands fire only from user input. Agent text containing `/goal ...` is not automatic dispatch.

Inside a `/goal` session, completion requires final audit first:

```text
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
```
`IMPLEMENTAUDIT_RUN_COMPLETE` may appear only after `AUDIT_COMPLETE`.


---

## Required transcript markers

Planner:

```text
Self-critique:
PREFLIGHT_GREEN
PREFLIGHT_RED
```

Phase loop:

```text
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
```

Andon escalation (Jidoka):

```text
ANDON_PROBE
ANDON_ESCALATE
ANDON_HANDOFF
```

Interruption / continuity (conditional):

```text
IMPLEMENTAUDIT_PAUSE
IMPLEMENTAUDIT_CONTINUITY_SAVED
```

Final audit:

```text
AUDIT_START
AUDIT_VERIFY
AUDIT_GAPS
AUDIT_COMPLETE
```

Handoff path:

```text
AUDIT_HANDOFF
```

Completion:

```text
IMPLEMENTAUDIT_RUN_COMPLETE
```

`IMPLEMENTAUDIT_RUN_COMPLETE` may appear only after `AUDIT_COMPLETE`.
`AUDIT_HANDOFF` appears only when gaps, blockers, or handoff-required caveats remain. Do not print `AUDIT_HANDOFF` with `IMPLEMENTAUDIT_RUN_COMPLETE`.
`AGENTS_UPDATE_DECISION` states whether a durable repo-local rule was added, not warranted, or requires owner decision. If updated, identify the scope: root `AGENTS.md`, nearest scoped `AGENTS.md`, or specialist/subagent guidance.

---

## Preserve existing ImplementAudit discipline

The older gate-based method is still load-bearing. Fold it into phase execution and final audit.

Required gates/invariants:

- safety read
- input gate
- pre-flight
- Smoke A before mutation
- implement P0 -> P1 -> P2
- patch owner/source, not nearest symptom
- generator-first for generated artifacts
- Smoke B after mutation
- regression protocol
- trace/proposed commit body when commit is unauthorized
- final quality self-check
- every ledger item terminally closed

Terminal statuses:

```text
done
changed
blocked
deferred
unverified
```

No `open` items at final.

---

## Final audit rules

The final audit must re-check the final repo state against the original roadmap or supplied work target.

It must:

- re-read the run-root `ROADMAP.md` when phase planning was used
- write `<run-root>/phases/audit-fix-<round>.md` for gaps when phase planning was used
- re-run deduplicated mandatory commands
- spot-check deterministic acceptance criteria
- diff-check deliverables against `Baseline ref`
- use `skills/scripts/repo-state.sh` or equivalent complete working-tree
  comparison for deliverables and added-line cleanliness when available
- print `AUDIT_COMPLETE` before `IMPLEMENTAUDIT_RUN_COMPLETE`
- warn when more than 30% of checks are `trust-prior-verify`

---

## Graphify and ActiveGraph

Optional pipeline model:

```text
Graphify = catalog / terrain map
ActiveGraph = evidence locker / custody substrate
ImplementAudit = officer / method
Capability Ledger = ImplementAudit-derived when ActiveGraph is configured
```

Rules:

- Graphify is optional.
- ActiveGraph is optional.
- Missing tools do not block `/implementaudit`.
- Do not install, index, configure, or export without explicit authorization.
- Graphify output is orientation evidence, not proof.
- ActiveGraph custody is not correctness proof.
- Live files beat graph output.
- Markdown ledger/final report fallback remains first-class.
- Distinguish upstream behavior from ImplementAudit custom extensions and repo-local heuristics.
- **V0260-ACTIVEGRAPH-CUSTODY-MODE**: When writing ActiveGraph events during a live release-gate
  run, include `custody_mode: live_release_gate` in event payloads at write time. Retroactive
  relabeling via a `custody.run.labeled` append event is valid fallback but not preferred.
  Transcript-derived historical backfill events must use `custody_mode: historical_backfill` and
  must carry `source`, `backfilled_at`, `original_event_time`, and `evidence_boundary` fields.
  This keeps live and backfilled custody unambiguous at the event level, not only at the run_id
  level. Rationale: v0.2.6.0 backfill gate (2026-06-07).

---

## AGENTS.md use

Repo-specific specialist or subagent protocols belong in AGENTS.md scope when they are durable.

Examples:

- Graphify terrain reviewer rules
- ActiveGraph custody/verifier rules
- docs-auditor rules
- release/provenance reviewer rules
- adversarial or red-team review loops
- generated-artifact checker rules

If the rule applies to the whole repo, put it in root `AGENTS.md`.
If it applies only to a subtree, put it in the nearest scoped `AGENTS.md`.
If it is only a user preference across projects, it may belong in user memory instead.

Good AGENTS.md content:

- source-of-truth rules
- package sync rules
- proof/evidence boundaries
- release/provenance gates
- Graphify/ActiveGraph boundaries
- generated-artifact policy
- known durable harness failure modes

Bad AGENTS.md content:

- raw logs
- transient dirty state
- private diagnostics
- one-off local failures
- long hash tables
- release claims without release gates
- evidence better suited for audit ledgers, final reports, commit bodies, or ActiveGraph custody

If an audit finding contradicts AGENTS.md, treat it as `OWNER DECISION` unless the current task explicitly authorizes changing AGENTS.md.

---

## Child/subagent review rules

Use child agents or subagents as bounded review loops, not as independent authorization authorities.

Repo-wide child/subagent rules live in this root `AGENTS.md`. Subtree-specific routines belong in the nearest scoped `AGENTS.md`, or `AGENTS.override.md` when that host/repo convention is available and appropriate. Packaged references such as `skills/references/child-agents.md` are explanatory material and do not change instruction precedence.

Child/subagent review loops:

- are read-only unless the user explicitly authorizes a disjoint write scope
- do not authorize edits, commits, pushes, installs, indexing, exports, releases, publication, provenance, or `AGENTS.md` changes
- do not replace live-file inspection
- become `/implementaudit` ledger items only after the main agent normalizes them with owner/source, evidence, risk, and status
- may include read-only contract auditor, adversarial behavioral auditor, Graphify terrain reviewer, ActiveGraph custody verifier, docs auditor, release/provenance reviewer, generated-artifact checker, or red-team reviewer roles

Durable child/subagent lessons should flow into the nearest applicable `AGENTS.md` only when they are stable repo-specific anti-repeat rules. Detailed reviewer evidence belongs in audit ledgers, final reports, commit bodies, or configured custody systems.

---

## CHANGELOG / README / CLAUDE

CHANGELOG:

- Keep-a-Changelog style.
- Keep the current project milestone at top, e.g. `[v0.2.6.0] - Unreleased` before release or `[v0.2.6.0] - <date>` only when the date is grounded.
- Match manifest version if one exists.
- Current project milestone is `v0.2.9.0`; plugin manifest version is `0.2.9` unless host evidence supports a four-component manifest version.
- Do not claim tags, releases, provenance, publication, or verified install without evidence.
- Behavior/package changes should be produced by running `/implementaudit` on this repo itself.
- Changelog entries should preserve the causal chain: finding/gap, root cause when known, countermeasure, evidence, and remaining risk.

README:

- Public-facing explanation derived from the canonical skill.
- May explain install, staged planner, `/goal`, optional tools, and safety boundaries.
- Must not claim unverified host/package behavior.

CLAUDE.md:

- Thin pointer only.
- Should tell Claude agents to read AGENTS.md first.
- Do not duplicate policy there.

---

## Validation

Minimum checks after package work:

```bash
git status --short
git diff --check
test ! -e IMPLEMENTAUDIT.md
test -f AGENTS.md
test -f CHANGELOG.md
test -f skills/SKILL.md
test -f .gitattributes
test -f skills/references/child-agents.md
test -f skills/references/transcript-contract.md
test -f skills/references/routing.md
test -f skills/references/repo-state-comparison.md
test -f skills/templates/PROTOCOL.md
test -f skills/templates/ROADMAP.md
test -f skills/templates/STATE.md
test -f skills/templates/THINKING.md
test -f skills/templates/phase-goal.txt
test -f skills/templates/child-agent-report.md
test -f skills/scripts/claim-run.sh
test -f skills/scripts/repo-state.sh
test -f skills/scripts/validate-audit-spec.sh
test -f skills/scripts/validate-phase.sh
test -f fixtures/audit-spec/valid-mixed.md
test -f fixtures/child-agents/AGENTS.md
test -f fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md
test -f fixtures/simple-audit/EXPECTED-ANDON-RECOVERY-SKELETON.md
test -f fixtures/simple-audit/EXPECTED-ANDON-HANDOFF-SKELETON.md
test -f fixtures/zero-optional-tool/COMPLETE-RUN.md
test -f fixtures/routing/greenfield-goal-synthesis/EXPECTED.md
test -f fixtures/routing/greenfield-full-category-intake/EXPECTED.md
test -f fixtures/routing/greenfield-batched-questions/EXPECTED.md
test -f fixtures/routing/brownfield-audit-closure/EXPECTED.md
test -f fixtures/routing/brownfield-zero-question-recon/EXPECTED.md
test -f fixtures/routing/brownfield-one-question-true-gap/EXPECTED.md
test -f fixtures/routing/brownfield-two-question-true-gap/EXPECTED.md
test -f fixtures/routing/mixed-greenfield-in-brownfield/EXPECTED.md
test -f docs/diagrams/tooling-architecture.mmd
test -f docs/diagrams/invocation-modes.mmd
test -f docs/diagrams/execution-spine.mmd
test -f docs/audits/v0.2.3.0-harness-adaptation-matrix.md
test -f docs/audits/v0.2.4.0-planner-stage-hardening.md
test -f docs/audits/v0.2.4.5-graphify-activegraph-honesty.md
test -f docs/audits/v0.2.5.0-external-staged-goal-runtime-gap-closure.md
test -f docs/audits/v0.2.5.0-claude-install-repair.md
test -f docs/audits/v0.2.7.0-lean-operating-discipline.md
test -f docs/audits/v0.2.8.0-adaptation.md
test -f docs/audits/v0.2.9.0-andon-escalation-jidoka-repair.md
test -f scripts/check-no-terminal-cap.sh
test -f tests/no-terminal-cap.test.sh
test -f fixtures/agent-eval/terminal-cap-request.md
test -f fixtures/agent-eval/autonomous-build-runner.md
test -f fixtures/agent-eval/audit-only-reviewer.md
test -f fixtures/agent-eval/release-bot-overreach.md
test -f fixtures/agent-eval/lean-glossary-theater.md
test -f scripts/check-agent-eval-fixtures.sh
test -f tests/agent-eval-fixtures.test.sh
test -f scripts/grade-agent-eval-transcript.sh
test -f tests/agent-eval-grader.test.sh
test -f scripts/check-validation-registry.sh
test -f tests/validation-registry.test.sh
test -f tests/summarize-repo.test.sh
test -f tests/shipped-scripts-smoke.test.sh
test -f skills/scripts/validate-run-root.sh
test -f tests/run-root-validation.test.sh
test -f skills/templates/sidecars.md
test -f skills/templates/tools.md
test -f skills/templates/context.md
test -f skills/scripts/custody-append.sh
test -f tests/custody-append.test.sh
test -f fixtures/run-root-example/STATE.md
test -f fixtures/run-root-example/phases/phase-1.md
test -f fixtures/phase-design/dmadv-greenfield-phase.md
test -f fixtures/agent-eval/RUNBOOK.md
test -f docs/portal/onboarding.md
test -f scripts/build-docs-portal.py
test -f scripts/check-docs-portal.py
test -f tests/docs-portal.test.sh
test -f fixtures/casual-build/accepted-intent.md
test -f fixtures/casual-build/rejected-intent.md
test -f fixtures/phase-design/polish-harden.md
test -f .github/workflows/pages.yml
test -f skills/references/lean-operating-discipline.md
test -f scripts/check-lean-discipline.sh
test -f tests/lean-discipline.test.sh
test -f fixtures/lean/brownfield-dmaic-release-repair.md
test -f fixtures/lean/brownfield-dmaic-stale-docs.md
test -f fixtures/lean/greenfield-dmadv-new-runtime-helper.md
test -f fixtures/lean/mixed-dmaic-dmadv-package-boundary.md
test -f fixtures/lean/sidecar-graphify-absent-markdown-fallback.md
test -f fixtures/lean/sidecar-graphify-dmaic-analyze.md
test -f fixtures/lean/sidecar-activegraph-dmaic-custody.md
test -f scripts/check-sidecar-boundaries.sh
test -f scripts/install-claude-from-release.sh
test -f scripts/install-codex-from-release.sh
test -f tests/release-asset-install.test.sh
test -f tests/release-asset-install-claude.test.sh
python -m json.tool .claude-plugin/plugin.json >/dev/null
python -m json.tool .claude-plugin/marketplace.json >/dev/null
bash scripts/generate-readme-diagrams.sh --check
bash scripts/check-readme-toc.sh
bash scripts/check-planner-stages.sh
bash scripts/check-marker-order.sh
bash scripts/check-routing.sh
bash scripts/check-sidecar-boundaries.sh
bash scripts/check-host-claims.sh
bash scripts/check-added-lines-clean.sh HEAD
bash tests/marker-order.test.sh
bash tests/planner-stages.test.sh
bash tests/release-asset.test.sh
bash tests/release-asset-install.test.sh
bash tests/release-asset-install-claude.test.sh
bash tests/install-copy-smoke.test.sh
bash tests/routing.test.sh
bash tests/repo-state.test.sh
bash tests/audit-spec.test.sh
bash tests/added-lines-clean.test.sh
bash tests/claim-run.test.sh
bash tests/continuity.test.sh
bash tests/phase-validation.test.sh
bash tests/sidecars.test.sh
bash tests/capability-ledger.test.sh
bash scripts/check-lean-discipline.sh
bash tests/lean-discipline.test.sh
bash scripts/check-no-terminal-cap.sh
bash tests/no-terminal-cap.test.sh
bash scripts/check-agent-eval-fixtures.sh
bash tests/agent-eval-fixtures.test.sh
bash tests/agent-eval-grader.test.sh
bash scripts/check-validation-registry.sh
bash tests/validation-registry.test.sh
```

Run docs-portal separately (it calls verify-package.sh internally; do not nest it inside verify-package.sh):

```bash
bash tests/docs-portal.test.sh
```

## Editing rules

After editing skill behavior:

1. Validate any manifests touched.
2. Validate phase templates and transcript markers.
3. Run `scripts/verify-package.sh` if present.
4. Bump manifest version only for shipped behavior/package changes.
5. Add or update CHANGELOG.
6. Commit only if explicitly authorized.
7. Push only if separately authorized.
8. Tag/release/publish/provenance only if separately authorized.
9. Re-sync Codex copies only when explicitly requested or documented as a local test step.

Docs-only edits do not require a version bump unless package/install behavior changes. Commit/push still require explicit authorization.

If present:

```bash
bash scripts/verify-package.sh
```

Required readback checks:

```bash
grep -R "Self-critique:" -n skills
grep -R "PREFLIGHT_GREEN" -n skills
grep -R "PREFLIGHT_RED" -n skills
grep -R "ANDON_PROBE" -n skills
grep -R "ANDON_ESCALATE" -n skills
grep -R "ANDON_HANDOFF" -n skills
grep -R "IMPLEMENTAUDIT_PHASE_START" -n skills
grep -R "IMPLEMENTAUDIT_PHASE_VERIFY" -n skills
grep -R "IMPLEMENTAUDIT_PHASE_DONE" -n skills
grep -R "AGENTS_UPDATE_DECISION" -n skills
grep -R "AUDIT_COMPLETE" -n skills
grep -R "IMPLEMENTAUDIT_RUN_COMPLETE" -n skills
grep -R ".IMPLEMENTAUDIT" -n skills README.md AGENTS.md
grep -R "v0.2.9.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.8.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.7.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.6.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.5.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.4.5" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.4.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.3.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.2.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.1.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.2.0.0" -n README.md CHANGELOG.md AGENTS.md
grep -R "v0.1.0" -n CHANGELOG.md
grep -R "v0.0.1" -n CHANGELOG.md
```

Check that no legacy external planner names or artifact directories appear in repo files.

---

## Working state target

```text
Canonical skill: skills/SKILL.md
Root behavior file: absent by owner decision
Runtime dir: .IMPLEMENTAUDIT/
Planner: Stage 0 through Stage 7 when goal synthesis or phase planning is needed
Executor: supplied target or one-paste /goal, phase loop when needed, Andon escalation, final audit
Optional tooling: Graphify orientation, ActiveGraph custody, Markdown fallback
```

## Install flows

README owns exact public install commands.

Do not label an install flow “verified working” unless it was tested in the relevant host during the current release gate.

Codex has no marketplace auto-update path. Manual skill copy must be repeated when the package changes.

The repo may validate a release-asset-to-Codex-install path with
`scripts/install-codex-from-release.sh` into a temporary `CODEX_HOME` or
`--codex-home`. That proof means the named local asset can be extracted,
checksum-checked when a manifest is supplied, and copied into a Codex-style
skill directory. It does not prove passive auto-update, marketplace distribution, universal host support, public release download, Graphify setup, or ActiveGraph setup.

The repo may validate a release-asset-to-Claude-Desktop-install path with
`scripts/install-claude-from-release.sh --claude-skills-dir <path>`. That proof
means the named local or public asset can be extracted, checksum-checked when a
manifest is supplied, and the `skills/` contents copied into the target Claude
skill directory. It does not prove the skill loads, runs, or is discovered by
Claude Desktop. No install proof is made by the script alone. Verify in
Claude Desktop after restart.

**Claude Desktop install proof requires the `claude` CLI or Claude Desktop host to
be available in the release gate environment.** If the `claude` CLI is absent,
treat Claude install proof as BLOCKED for that gate. Record the blocker explicitly;
do not claim Claude install verification without live host evidence.

**Anti-repeat rule (V0_2_6_0_TEMPLATE_NOT_A_FILLED_SPEC):** The phase-goal.txt
template has placeholder content by design. Do not run `validate-phase.sh`
against the template as if it were a filled phase spec. Validate only filled-in
phase specs in fixtures/ or run-root phases/. The CI step "Validate phase
template" was removed in v0.2.6.0 for this reason.

**Anti-repeat rule (V0_2_6_0_FORBIDDEN_TERM_RUNTIME_ONLY):** The
`check-forbidden-terms.sh` script never embeds the forbidden term in source.
Always supply the term at runtime via `--term "$FORBIDDEN_TERM"`. Never write the
forbidden term into a tracked file or commit message to facilitate the check.

**Anti-repeat rule (V0_2_6_0_PROTOCOL_LOOP_MUST_BE_COMPLETE):** Phase loop steps
must follow the 16-step sequence in PROTOCOL.md. Do not skip validate-phase.sh
(Step 3), cleanliness check (Step 9), or STATE.md update (Step 16). Each of
these steps was absent in v0.2.5.0's PROTOCOL.md and caused verifiable gaps.

**Anti-repeat rule (V0_2_6_0_FAILURE_RECOVERY_ORDERED, amended v0.2.9.0):** The
Andon escalation sequence (ANDON_PROBE → ANDON_ESCALATE → ANDON_HANDOFF) is
ordered. Do not skip to ANDON_HANDOFF on the first criterion failure; that was
the v0.2.5.0 gap. The v0.2.6.0 fix overcorrected into a fixed try counter that
contradicted Jidoka; v0.2.9.0 removed every terminal try/round cap. Escalation
is driven by repeated same-class failure, and ANDON_HANDOFF fires only when
closure is blocked by owner decision, unsafe scope, missing authorization,
external dependency, irreproducibility, missing required tool/access, or no
bounded countermeasure remaining.

**Anti-repeat rule (V0290-README-VERSION-CLAIM-PINNED):** README's "Current
project milestone:" claim is derived evidence, not free prose. It must match
the live plugin manifest version; `scripts/verify-package.sh` enforces this by
reading plugin.json rather than pinning a literal. Rationale: the claim
drifted silently at the v0.2.9.0 bump because every other version pin was
checker-enforced and this one was not (2026-06-10).

**Anti-repeat rule (V0290-VALIDATION-REGISTRY-PARITY):** Every
`tests/*.test.sh` must be invoked by BOTH `scripts/verify-package.sh` and
`.github/workflows/validate.yml`; `scripts/check-validation-registry.sh`
enforces parity with a reasoned exemption list (docs-portal.test.sh is exempt
from verify-package because it invokes verify-package and must not nest).
Rationale: both registries drifted independently at v0.2.9.0 — three new
tests missing from verify-package, one test missing from CI (2026-06-10).

**Anti-repeat rule (V0290-PACKAGE-PARITY):** The built `.skill` archive must
equal the `required_archive` manifest in `scripts/build-release-asset.sh`
exactly — no missing entries, no extras. Adding payload requires a deliberate
manifest update (both `required_source` and `required_archive`) plus the
mirrored set in `tests/release-asset.test.sh`. Rationale: v0.2.9.0 — the lean
reference shipped while absent from both allowlists, so its deletion would not
have failed the gate (2026-06-10).

**Anti-repeat rule (V0290-HELPER-PATHS-RESOLVE-VIA-SKILL-DIR):** Packaged
helper invocations in the payload must resolve through
`"${IMPLEMENTAUDIT_SKILL_DIR:-skills}"/scripts/<helper>` — never a bare
`skills/scripts/` path, which resolves nowhere for installed consumers (the
archive strips the `skills/` prefix). The default keeps the same command
working verbatim in the source repo. Enforced by the path-integrity gate in
`scripts/verify-package.sh`. Do not reuse `IMPLEMENTAUDIT_BASE` for this: that
variable is the run-root base (default `.IMPLEMENTAUDIT/runs`) consumed by
`claim-run.sh`, and the round-5 fix initially collided with it — redefining an
existing variable without checking its consumers is the anti-pattern this rule
records. Rationale: v0.2.9.0 rounds 5–7 (2026-06-10).

**Anti-repeat rule (V0290-RUN-ROOT-IS-NOT-EVIDENCE):** `.IMPLEMENTAUDIT/`
run-root artifacts are the audit substrate, never deliverables or cleanliness
evidence. `skills/scripts/repo-state.sh` excludes them from `changed-files`
and `added-lines` enumeration with a visible stderr count (never silently),
while explicit `deliverable <path>` queries stay honest for any path.
`claim-run.sh` prints an advisory (stderr, no repo mutation) when the run-root
base is not gitignored in the target repo, suggesting a local-only
`.git/info/exclude` entry. Rationale: v0.2.9.0 round-6 audit — in target repos
without the dogfood gitignore, run roots contaminated the run's own evidence
(2026-06-10).

**Anti-repeat rule (V0290-NO-DANGLING-SHIPPED-PATHS):** Files under `skills/`
ship to consumers who do not receive `fixtures/`, `tests/`, or repo-side
`scripts/check-*`. Any payload line referencing such a path must carry a
"source repo" label, enforced by the path-integrity gate in
`scripts/verify-package.sh`. Shipped helper scripts must discover repo
surfaces at runtime (globs + existence checks), not hardcode IMPLEMENTAUDIT
repo paths. Rationale: v0.2.9.0 (2026-06-10).

**Anti-repeat rule (V0290-DOGFOOD-VERSION-SKEW):** When the working repo is
IMPLEMENTAUDIT itself, Stage 0 must compare the installed/running payload
version against the repo `.claude-plugin/plugin.json`; on mismatch, record an
orientation Andon (class: evidence-mismatch) and treat live repo files as the
contract of record. Live evidence: the 2026-06-10 dogfood session ran on a
pre-repair installed payload while auditing the repaired repo. Rationale:
v0.2.9.0 G4.

**Anti-repeat rule (V0290-NO-TERMINAL-CAP-WORDING):** Shipped runtime docs and
runtime-shaping surfaces (skills/, docs/diagrams/, docs/portal/, fixtures/,
README.md, AGENTS.md) must not contain terminal-cap failure wording (try
counters, capped audit rounds, run-stopping phrasing) or the legacy
FAILURE-prefixed marker spellings. `scripts/check-no-terminal-cap.sh` enforces
the gate; `tests/no-terminal-cap.test.sh` proves both the gate and the
legacy-history exemption (CHANGELOG.md and docs/audits/ are not scanned).
Rationale: v0.2.9.0 Jidoka contradiction repair (2026-06-10).

**Anti-repeat rule (V0_2_6_0_DISPATCH_NEEDS_PREFLIGHT):** Stage 7 handoff must
not be printed before: (a) all 8 dispatch-prep steps in Stage 5 complete, and
(b) Stage 6.5 prints PREFLIGHT_GREEN or OWNER DECISION accepts PREFLIGHT_RED.
Printing the handoff before these gates passes was a v0.2.5.0 gap.

**Anti-repeat rule (LIVE_V0_2_5_0_CLAUDE_INSTALL_BROKEN):** v0.2.5.0 shipped with
Codex-only install smoke coverage. The Claude Desktop install path was not
documented or tested. Future release gates must run both
`tests/release-asset-install.test.sh` (Codex) and
`tests/release-asset-install-claude.test.sh` (Claude archive smoke) before
closing the release gate. If the live Claude host is available, also run
`scripts/install-claude-from-release.sh` against a real Claude skill directory
and verify in Claude Desktop.

The docs portal generator (`scripts/build-docs-portal.py`) provides the
quickstart/onboarding docs page. It is generated from `docs/portal/onboarding.md`
and deployed to GitHub Pages via `.github/workflows/pages.yml`. See v0.2.8.0
adaptation ledger for evidence.

**Anti-repeat rule (V0270-LEAN-TERMS-ARE-BEHAVIOR):** Lean/TPS terms (5S,
Kaizen, Hansei, Jidoka, Gemba, Nemawashi, Muda/Mura/Muri, DMAIC, DMADV,
Poka-yoke) are not decorative labels. Each maps to a specific auditable runtime
behavior documented in `skills/references/lean-operating-discipline.md`. Do not
add Lean terms to prompts, templates, or docs without a matching behavioral
anchor. `scripts/check-lean-discipline.sh` verifies the structural requirements.
Rationale: v0.2.7.0 Lean operating discipline (2026-06-07).

**Anti-repeat rule (V0270-DMAIC-DMADV-ROUTING):** Brownfield improvement work
routes through DMAIC (Define→Measure→Analyze→Improve→Control). Greenfield or
replacement work routes through DMADV (Define→Measure→Analyze→Design→Verify).
Mixed work uses both in sequence: DMAIC shell for the brownfield repair + DMADV
for the new artifact. The quality route is declared in each phase spec. Routing
fixtures live at `fixtures/lean/`. Rationale: v0.2.7.0.

**Anti-repeat rule (V0270-5S-APPLIES-TO-RUN-ROOTS):** 5S (Sort, Set-in-order,
Shine, Standardize, Sustain) applies to run roots, package payloads, generated
artifacts, sidecars, and release assets. Each phase records a 5S_CHECK with all
five pillars as clean/deferred/blocked. Rationale: v0.2.7.0.

**Anti-repeat rule (V0270-HANSEI-AFTER-FALSE-PASS):** Hansei is required after
a false pass (a check that passed but should have failed), a regression, an
abnormal release-gate command, a substitution that wasn't planned, or an owner
intervention. Record the gap, cause, countermeasure, and follow-up evidence.
Rationale: v0.2.7.0.

**Anti-repeat rule (V0270-KAIZEN-DURABLE-ONLY):** Kaizen countermeasures belong
in templates, checkers, or AGENTS.md anti-repeat rules only when they are
durable (stable, non-obvious, future-useful, and repo-specific). Transient
countermeasures belong in audit ledgers, final reports, or phase notes, not in
AGENTS.md or templates. Rationale: v0.2.7.0.

**Anti-repeat rule (V0270-SIDECAR-LEVERAGE-NOT-PROSE):** Graphify terrain
leverage and ActiveGraph custody event routing must be implemented as behavioral
rules in `skills/references/lean-operating-discipline.md` (Graphify terrain
leverage table + ActiveGraph custody events table), `skills/templates/THINKING.md`
(Graphify terrain plan + ActiveGraph custody plan fields), and
`skills/templates/PROTOCOL.md` (Graphify/ActiveGraph Lean leverage rules). Sidecar
leverage must not remain prose-only. `scripts/check-lean-discipline.sh` verifies
both sections exist. Fixtures in `fixtures/lean/sidecar-*` prove sidecar-absent
fallback and sidecar-present paths. Rationale: v0.2.7.0 Graphify/ActiveGraph
leverage gate (2026-06-07).

**Anti-repeat rule (V0290-SIDECARS-CANONICAL-FOR-DOGFOOD):** Graphify and
ActiveGraph are canonical for dogfooding this repo (owner decision,
2026-06-10): terrain lives at `graphify-out/graph.json` (agent-extracted;
nodes need `id`+`label`, optional `type`; links need `source`/`target`),
custody lives per-run at `.IMPLEMENTAUDIT/runs/<run>/custody.db` (SQLite) or
`custody-trace.jsonl`. Prior-run stores are read-only continuity inputs;
recovery/backfill follows V0260-ACTIVEGRAPH-CUSTODY-MODE labeling
(`historical_backfill` + source/backfilled_at/original_event_time/
evidence_boundary). Local persistence of these gitignored outputs is expected,
not a violation: the boundary is tracked source and the `.skill` package —
`check-sidecar-boundaries.sh` enforces tracked-status and ignore-cover, not
existence. Terrain is orientation, custody is chain-of-custody; neither is
proof.

**Anti-repeat rule (V0270-SIDECAR-OUTPUTS-EXCLUDED):** Graphify outputs
(`graphify-out/`, `graph.json`), ActiveGraph stores (`.activegraph/`, `*.activegraph.db`,
`custody*.jsonl`, `custody.db`), and run-root artifacts (`.IMPLEMENTAUDIT/`) are
gitignored and must never appear in tracked source, commit messages, or the `.skill`
package. `scripts/check-sidecar-boundaries.sh` and `scripts/verify-package.sh`
enforce this boundary. Rationale: v0.2.7.0.

**Anti-repeat rule (V0280-CASUAL-BUILD-INTAKE-MUST-BE-GOVERNED):** Natural-language
repo-build intent is a valid 4th invocation shape (governed casual-build intake),
but it must always synthesize a bounded `tdqyq-audit-object` before any mutation.
The 5-step intake process in `skills/references/routing.md` (Governed Casual-Build
Intake section) is mandatory. Reject unbounded, unsafe, empty, or non-repo inputs
with an explicit STOP. Never route casual intent directly to mutation without owner/source,
acceptance criteria, and rollback path. `scripts/check-routing.sh` verifies the routing
definition exists. Rationale: v0.2.8.0 G3 gap closure (2026-06-08).

**Anti-repeat rule (V0280-CONTINUITY-PRELOAD-PRIORITY-ORDER):** Bounded continuity
preload follows the 5-source priority order defined in `skills/SKILL.md` Stage 0
(AGENTS.md first; run-root applied-context; optional personal/project notes;
Graphify terrain; ActiveGraph custody). Loaded continuity may never override
safety defaults, authorization boundaries, AGENTS.md rules, or repo policy. When
continuity changes scope or evidence, write `IMPLEMENTAUDIT_CONTINUITY_SAVED`
with all 6 required fields (Target, Reason, Evidence, Boundary, Authorization,
Not saved). Rationale: v0.2.8.0 G4 gap closure (2026-06-08).

**Anti-repeat rule (V0280-DOCS-PORTAL-GENERATOR-FIRST):** `dist/docs-portal/` is
generated output. Never hand-edit `dist/docs-portal/index.html` or
`dist/docs-portal/docs-metadata.json`. Always regenerate from source:
`python scripts/build-docs-portal.py`. Validate with:
`python scripts/check-docs-portal.py dist/docs-portal`. The portal content
source is `docs/portal/onboarding.md`; edit that file, then regenerate.
`dist/` is gitignored. `tests/docs-portal.test.sh` runs the full build+validate cycle.
Rationale: v0.2.8.0 G7 gap closure (2026-06-08).

**Anti-repeat rule (V0280-PAGES-DEPLOYMENT-UNVERIFIED):** GitHub Pages deployment
is unverified until `.github/workflows/pages.yml` actually succeeds in CI with the
repository Pages source set to "GitHub Actions" (Settings → Pages). Do not claim
Pages is live, deployed, or publicly accessible without live CI evidence of a
successful deploy job. OWNER DECISION required before first deployment. The build
and validate jobs run independently of the deploy job and may pass even when deploy
is blocked. Rationale: v0.2.8.0 (2026-06-08).

**Anti-repeat rule (V0280-POLISH-HARDEN-OPTIONAL-TERMINAL):** Polish & Harden is
an optional terminal phase shape (Rule P4-8 in `skills/references/phase-design.md`).
It must not introduce new features, only cover: cleanliness, identity hygiene,
generated artifact freshness, and proof-boundary wording. It is default-recommended
for full plans, public surfaces, and package boundaries, but skippable with
documented rationale. Fixtures for both variants live in
`fixtures/phase-design/polish-harden.md`. Rationale: v0.2.8.0 G6 gap closure (2026-06-08).

**Anti-repeat rule (V0280-PY-USE-STDOUT-WRITE):** Python CLI scripts under
`scripts/` must use `sys.stdout.write(...)` and `sys.stderr.write(...)` for all
user-facing output instead of the built-in print function, so the
`check-added-lines-clean.sh` debug-print gate remains applicable to `.py` files
without a global exemption. There is no `*.py` exclusion in `is_skipped_path()`.
If a new Python script needs console output, use sys.stdout.write/sys.stderr.write
with explicit `\n`. Rationale: v0.2.8.0 audit-fix (2026-06-08).

## Release asset gate

For package release gates, including `v0.2.5.0`, the GitHub release asset name is
`IMPLEMENTAUDIT.skill`.

No local repo evidence proves `.skill` is a universal host-standard archive
format. Until host evidence says otherwise, treat `IMPLEMENTAUDIT.skill` as this
repo's GitHub release artifact name. The artifact is a ZIP-format archive built
by:

```bash
bash scripts/build-release-asset.sh
```

The artifact contains only the packaged skill payload required for installation:
`skills/` plus `.claude-plugin/` metadata. It must include the `skills/` layout,
references, scripts, and templates. Repo-maintenance material such as README
generation sources, audit ledgers, release-candidate notes, fixtures, tests, CI
config, Git metadata, root validation scripts, and changelog/release-history
evidence stays repo-side unless a future owner decision proves a file is
load-bearing for installed runtime behavior. The artifact must not include a
root `IMPLEMENTAUDIT.md` behavior file.

The artifact must not include `.IMPLEMENTAUDIT/` run artifacts, local smoke
debris, Graphify outputs, ActiveGraph stores, secrets, git metadata, or
untracked diagnostics. Validate it by extracting it to a temporary directory and
checking package shape before upload. `scripts/verify-package.sh` runs the
release-asset builder in `--check` mode for this purpose.

Attach `IMPLEMENTAUDIT.skill` to GitHub Releases only during an explicitly
authorized release gate. Do not upload the asset during ordinary audit, local
commit, or push-only gates. Building or validating the local asset is not a
release, publication, marketplace verification, or provenance claim.

If provenance is explicitly authorized, publish only the provenance artifacts
that were actually generated and validated. For `v0.2.5.0`, the repo-supported
provenance surface is a checksum manifest produced by:

```bash
bash scripts/write-release-checksums.sh
```

Do not call a checksum manifest a signature, attestation, SBOM, license,
marketplace verification, or install verification.

**Anti-repeat rule (V0260-ZIPINFO-COMPRESSION):** When building the `.skill`
ZIP archive with `zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED)`,
the ZipFile-level `compression` default does NOT apply when entries are written
via `zf.writestr(ZipInfo_object, data)`. The `ZipInfo.compress_type` attribute
(which defaults to `ZIP_STORED = 0`) overrides the ZipFile-level default.
Always set `info.compress_type = zipfile.ZIP_DEFLATED` explicitly on each
`ZipInfo` before calling `writestr()`. Omitting this line silently stores all
entries uncompressed (~155 KB) even though the `ZipFile` was opened with
`ZIP_DEFLATED`. `tests/release-asset.test.sh` now catches this regression
automatically via a per-entry `compress_type` check and a 120 KB total-size
guard. Rationale: v0.2.6.0 compression repair (2026-06-07).

## Identity hygiene release-gate

Before any release, run the generic forbidden-terms checker to confirm that
no externally-sourced identity string appears in tracked source files.

The forbidden term(s) are supplied by the release author at runtime — they are
NOT embedded in the checker source. This prevents the forbidden term from
appearing in tracked files even via the checker itself.

```bash
bash scripts/check-forbidden-terms.sh --term "<FORBIDDEN_TERM>" --scan-path skills/
bash scripts/check-forbidden-terms.sh --term "<FORBIDDEN_TERM>"
```

**Anti-repeat rule (v0.2.6.0 identity hygiene):** The external staged-goal
comparator referenced during the v0.2.6.0 hardening run must never have its
proper name appear in tracked source files, commit messages, branch names, tag
names, PR/issue titles, or release notes. Use only: "external staged-goal
comparator", "staged-goal comparator", "external comparator", or "comparator
package" in any repo-facing surface.

Run the identity hygiene check at every release gate. The final audit ledger
must record the result as: "tracked files contain forbidden comparator identity
string: PASS/FAIL".

**Using check-forbidden-terms.sh:**

```bash
# Supply the forbidden term at runtime; do not write it into a tracked file.
bash scripts/check-forbidden-terms.sh --term "$FORBIDDEN_TERM" --scan-path skills/
bash scripts/check-forbidden-terms.sh --term "$FORBIDDEN_TERM"
```

Exit code 0: no forbidden occurrences. Exit code 1: occurrences found (list
printed to stderr with file:line:content). Either fix the occurrences or file
an Andon explaining why the occurrence is intentional before closing the gate.

## Transcript markers (load-bearing)

### Inside the `/goal` session

Named blocks the executing agent must print into the transcript. The host's `/goal` evaluator + the user both read them.

- `IMPLEMENTAUDIT_PHASE_START` — once per phase, at the start. Metadata only.
- `IMPLEMENTAUDIT_PHASE_VERIFY` — once per phase, before DONE. Each criterion pass/fail with evidence; engineering checks; **`Cleanliness:` section** with grep counts vs `Baseline ref` (debug prints, session task markers, dead imports).
- `AGENTS_UPDATE_DECISION` — once per phase or final audit. States whether a durable repo-local rule was added, not warranted, or requires owner decision. If updated, identify scope: root `AGENTS.md`, nearest scoped `AGENTS.md`, or specialist/subagent guidance.
- `IMPLEMENTAUDIT_PHASE_DONE` — once per phase, final block.
- `ANDON_PROBE` / `ANDON_ESCALATE` / `ANDON_HANDOFF` — Jidoka escalation on any abnormality (failed criterion, regression, bad evidence, unclear owner, stale sidecar, policy conflict). Ordered; no arbitrary try or round cap; `ANDON_HANDOFF` only on a genuine blocking condition, never "third try failed."
- `IMPLEMENTAUDIT_PAUSE` — emitted when a user message interrupts a phase in progress; requires a preceding `IMPLEMENTAUDIT_PHASE_START`; resume follows the run-root PROTOCOL.md resume contract.
- `IMPLEMENTAUDIT_CONTINUITY_SAVED` — emitted only on an actual bounded continuity writeback, with all six fields (Target, Reason, Evidence, Boundary, Authorization, Not saved).
- `AUDIT_START` / `AUDIT_VERIFY` (includes a `Deliverables:` block from the diff-based check vs `Baseline ref) / `AUDIT_GAPS` / `AUDIT_COMPLETE` (includes `Audit coverage:`) — final audit pass.
- `AUDIT_HANDOFF` — handoff path only when gaps, blockers, or handoff-required caveats remain. Never print with `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `IMPLEMENTAUDIT_RUN_COMPLETE` — only after `AUDIT_COMPLETE`. Run is done. Prepends a `⚠ Audit coverage: …` warning banner when trust-prior is > 30% of total checks.

The `/goal` end-state requires `IMPLEMENTAUDIT_RUN_COMPLETE` preceded by `AUDIT_COMPLETE` and one `IMPLEMENTAUDIT_PHASE_DONE` per phase, with no `ANDON_HANDOFF` or `AUDIT_HANDOFF`.

### Inside the planner session

Before the user pastes `/goal`, the planner emits two additional named blocks the user sees in Stage 6/6.5:

- `Self-critique:` — printed inside the Stage 6 plan-review summary (Stage 6a). 1–3 findings (falsifiability of criteria, phase atomicity, weakest dependency) or `clean`. Falsifiability issues are rewritten in place in the phase specs before the summary prints — so the user sees the post-critique version.
- `PREFLIGHT_GREEN` / `PREFLIGHT_RED` — Stage 6.5 output after running the deduplicated mandatory commands once. `PREFLIGHT_RED` re-enters Stage 6 and may dispatch only when the broken baseline is classified as the phase target and the owner accepts that risk; unrelated or unclear baseline failures require Andon or OWNER DECISION.

These are not part of the `/goal` end-state — the `/goal` session hasn't started yet at this point — but they're load-bearing for plan quality.

### Other v0.x state

Full format specs: `skills/references/goal-format.md` and
`skills/references/transcript-contract.md`.

## Gotchas

- **Slash commands fire only from user input.** Agent text containing `/goal "..."` is *not* parsed as a command. Stage 7 is a one-paste handoff — the planner prints the line, the user pastes it. Never frame this as "automatic dispatch."
- **Plugin cache only refreshes on version-field change.** If you push a code change without bumping `plugin.json` version, `claude plugin update` reports "already at latest" and the cache stays stale. Always bump on shipped changes.
- **`.gitignore` extension filter**: the file has no extension, so `find -name "*.md"` etc. skip it. When doing mass renames, include the gitignore separately.
- **Codex install is a one-way copy**. There is no marketplace auto-update path. Repeat the README-documented manual copy command when the package changes, and keep that command aligned with the actual `skills/` package layout.
- **Durable repo-specific learning belongs in AGENTS.md, not user memory.** The agent emits `AGENTS_UPDATE_DECISION` to state whether a durable rule was added, not warranted, or requires owner decision.
- **Child/subagent guidance follows the AGENTS hierarchy.** Use root `AGENTS.md` for repo-wide rules and scoped `AGENTS.md` or `AGENTS.override.md` only for subtree-specific routines when supported. Reference docs do not change instruction precedence.
- **Do not print a second `/goal` when already operating inside a `/goal using /implementaudit ...` run.**
- **Mermaid renders natively in GitHub README** but not always in every external markdown viewer. Stick to standard Mermaid syntax (flowchart TD / LR, subgraphs, classDef styling).

## Reference docs

The package migration is not just file movement. The method is split into reference docs so future maintainers do not need to understand one monolithic skill file.

Required reference set:

- `planning-depth.md` — when ImplementAudit should synthesize a goal vs govern a supplied one.
- `phase-design.md` — how to slice audit closure into verifiable phases.
- `goal-format.md` — `/goal` handoff shape, transcript markers, final audit end-state.
- `transcript-contract.md` — marker ordering, handoff/completion exclusivity, and host/wrapper end-state checks.
- `routing.md` — greenfield, brownfield, and mixed-mode intake/inspection gates.
- `repo-state-comparison.md` — baseline-to-working-tree comparison for final audit, deliverable, and cleanliness evidence.
- `child-agents.md` — bounded child/subagent review loops and non-authority boundaries.

Optional later references:

- `activegraph-graphify.md`
- `agents-standardization.md`
- `kaizen-hansei-hoshin-nemawashi.md` — operating vocabulary and when each method applies.
- `evidence-boundaries.md` — proof levels, trust-prior, Graphify/ActiveGraph limits, and no-provenance-without-evidence.

## Related

- Repo: https://github.com/theIslampill/IMPLEMENTAUDIT.md
