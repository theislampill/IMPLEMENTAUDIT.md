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
│   └── validate.yml            GitHub Actions validation mirror of local package checks.
├── docs/diagrams/              Mermaid sources generated into README.md.
│   ├── tooling-architecture.mmd
│   ├── invocation-modes.mmd
│   └── execution-spine.mmd
├── docs/audits/
│   ├── INDEX.md                Compact dogfood-history evidence index.
│   └── v0.2.3.0-harness-adaptation-matrix.md
│                                Generic external-comparator adaptation matrix.
├── fixtures/
│   ├── child-agents/           Scoped AGENTS hierarchy and reviewer fixtures.
│   ├── zero-optional-tool/     Complete Markdown fallback example.
│   └── simple-audit/
│       ├── AUDIT.md
│       └── EXPECTED-LEDGER.md
├── scripts/
│   ├── build-release-asset.sh  Build/extract-check IMPLEMENTAUDIT.skill.
│   ├── check-host-claims.sh    Guard unsupported host/release/license claims.
│   ├── check-added-lines-clean.sh Guard added-line debug/task-marker/overclaim drift.
│   ├── check-marker-order.sh   Guard final-audit transcript marker order.
│   ├── check-planner-stages.sh Guard native Stage 0-7 planner contract.
│   ├── check-readme-toc.sh     Guard README Contents anchors.
│   ├── generate-readme-diagrams.sh Generate/check README Mermaid blocks.
│   ├── check-routing.sh     Validate greenfield/brownfield routing fixtures.
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
    │   ├── routing.md          Greenfield/brownfield/mixed routing gates.
    │   ├── repo-state-comparison.md Baseline-to-working-tree audit comparison.
    │   └── child-agents.md     Bounded review loops and non-authority boundaries.
    ├── scripts/                Bash scripts the planner executes during stages.
    │   ├── claim-run.sh        Atomic namespaced run-root claim helper.
    │   ├── detect-env.sh       Greenfield env recon.
    │   ├── detect-stack.sh     Brownfield repo contract/source detection.
    │   ├── repo-state.sh       Complete baseline-vs-working-tree helper.
    │   ├── summarize-repo.sh   Brownfield owner/regression map.
    │   ├── validate-audit-spec.sh Validate audit/goal/slice specs.
    │   └── validate-phase.sh   Sanity-checks a phase spec has required markers.
    └── templates/              Files the planner copies into a user's `.IMPLEMENTAUDIT/` dir.
        ├── ROADMAP.md          Phase plan with dependencies.
        ├── STATE.md            Live progress file.
        ├── THINKING.md         Reviewable risk/dependency/evidence plan.
        ├── phase-goal.txt      Phase spec skeleton (work, criteria, evidence, commands).
        ├── child-agent-report.md Read-only reviewer report shape.
        └── PROTOCOL.md         Execution loop + failure recovery + final audit protocol.
```

## What ships vs what doesn't

- **Ships to consumers**: everything under `skills/`. The plugin manifest declares `skills: "./skills/"`.
- **Repo-only**: `README.md`, `CHANGELOG.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, fixtures, root scripts, and `.gitignore`.
- **Marketplace entry**: `.claude-plugin/marketplace.json` points at the plugin root. Do not claim marketplace behavior was verified unless actually tested.
- **License**: no `LICENSE` file is present until the owner selects a license and supplies license evidence.
- **Versioning**: project milestone `v0.2.5.0` maps to plugin manifest version
  `0.2.5`. The manifest uses
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
- IMPLEMENTAUDIT is audit-governed implementation, not a generic autonomous
  build runner.
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

Failure recovery:

```text
FAILURE_PROBE
FAILURE_ESCALATE
FAILURE_HANDOFF
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
- Keep the current project milestone at top, e.g. `[v0.2.5.0] - Unreleased` before release or `[v0.2.5.0] - <date>` only when the date is grounded.
- Match manifest version if one exists.
- Current project milestone is `v0.2.5.0`; plugin manifest version is `0.2.5` unless host evidence supports a four-component manifest version.
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
bash scripts/check-marker-order.sh fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md
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
grep -R "IMPLEMENTAUDIT_PHASE_START" -n skills
grep -R "IMPLEMENTAUDIT_PHASE_VERIFY" -n skills
grep -R "IMPLEMENTAUDIT_PHASE_DONE" -n skills
grep -R "AGENTS_UPDATE_DECISION" -n skills
grep -R "AUDIT_COMPLETE" -n skills
grep -R "IMPLEMENTAUDIT_RUN_COMPLETE" -n skills
grep -R ".IMPLEMENTAUDIT" -n skills README.md AGENTS.md
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
Executor: supplied target or one-paste /goal, phase loop when needed, failure recovery, final audit
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

**Anti-repeat rule (V0_2_6_0_FAILURE_RECOVERY_ORDERED):** The 3-strike failure
recovery ladder (FAILURE_PROBE → FAILURE_ESCALATE → FAILURE_HANDOFF) is
sequential. Do not skip to FAILURE_HANDOFF on the first criterion failure; that
was the v0.2.5.0 gap. Strike 1 requires an inline fix attempt; Strike 2 requires
a phase-N.fix.md; only Strike 3 yields FAILURE_HANDOFF.

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

Future work: reduce first-time user cognitive load with a dedicated
quickstart/onboarding docs page. Keep this as future work; it is not a
`v0.2.4.0` release blocker unless README/install claims become misleading.
Focus later on clearer first-run path, examples, and decision trees without
weakening audit-governed truthfulness.

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
- `FAILURE_PROBE` / `FAILURE_ESCALATE` / `FAILURE_HANDOFF` — 3-strike phase-criterion recovery.
- `AUDIT_START` / `AUDIT_VERIFY` (includes a `Deliverables:` block from the diff-based check vs `Baseline ref) / `AUDIT_GAPS` / `AUDIT_COMPLETE` (includes `Audit coverage:`) — final audit pass.
- `AUDIT_HANDOFF` — handoff path only when gaps, blockers, or handoff-required caveats remain. Never print with `IMPLEMENTAUDIT_RUN_COMPLETE`.
- `IMPLEMENTAUDIT_RUN_COMPLETE` — only after `AUDIT_COMPLETE`. Run is done. Prepends a `⚠ Audit coverage: …` warning banner when trust-prior is > 30% of total checks.

The `/goal` end-state requires `IMPLEMENTAUDIT_RUN_COMPLETE` preceded by `AUDIT_COMPLETE` and one `IMPLEMENTAUDIT_PHASE_DONE` per phase, with no `FAILURE_HANDOFF` or `AUDIT_HANDOFF`.

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
