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
├── .gitignore                  Editor/OS junk + .IMPLEMENTAUDIT/ artifact dirs
├── AGENTS.md                   This file. Authoritative project doc.
├── CLAUDE.md                   Claude Code-specific tips. Points at this file.
├── CHANGELOG.md                Per-version release notes. Keep-a-Changelog format, SemVer.
├── README.md                   Public-facing: what it is, install, use, Mermaid flow charts.
├── CONTRIBUTING.md             Short onboarding: what ImplementAudit is/is not, minimum method, worked flow.
├── fixtures/
│   └── simple-audit/
│       ├── AUDIT.md
│       └── EXPECTED-LEDGER.md
├── scripts/
│   └── verify-package.sh       Repo/package validation.
└── skills/
    ├── SKILL.md                Canonical skill source.
    ├── references/             Progressive-disclosure docs the agent reads when needed.
    │   ├── planning-depth.md   What makes a plan deserve ...
    │   ├── phase-design.md     How to slice phases (adaptive count, no cap).
    │   └── goal-format.md      /goal mechanics ...
    ├── scripts/                Bash scripts the planner executes during stages.
    │   ├── detect-env.sh       Greenfield env recon.
    │   ├── detect-stack.sh     Brownfield stack/framework detection.
    │   ├── summarize-repo.sh   Compressed repo map.
    │   └── validate-phase.sh   Sanity-checks a phase spec has required markers.
    └── templates/              Files the planner copies into a user's `.IMPLEMENTAUDIT/` dir.
        ├── ROADMAP.md          Phase plan with dependencies.
        ├── STATE.md            Live progress file.
        ├── phase-goal.txt      Phase spec skeleton (work, criteria, evidence, commands).
        └── PROTOCOL.md         Execution loop + failure recovery + final audit protocol.
```

## What ships vs what doesn't

- **Ships to consumers**: everything under `skills/`. The plugin manifest declares `skills: "./skills/"`.
- **Repo-only**: `README.md`, `CHANGELOG.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, fixtures, root scripts, and `.gitignore`.
- **Marketplace entry**: `.claude-plugin/marketplace.json` points at the plugin root. Do not claim marketplace behavior was verified unless actually tested.
- **License**: no `LICENSE` file is present until the owner selects a license and supplies license evidence.

## How the skill works

ImplementAudit first identifies the invocation shape: embedded governance, direct governance, or goal synthesis.

In embedded governance mode, ImplementAudit is already inside a supplied host goal/task/plan, such as `/goal using /implementaudit ...`. It does not print a second `/goal`. It governs the active target with safety read, input normalization, Gemba, Smoke A/B, owner/source patching, evidence boundaries, final audit, and terminal ledger closure.

In direct governance mode, ImplementAudit receives a concrete audit, handoff, checklist, review, or bounded plan. It applies audit-closure hygiene to that artifact. It may decompose the work into phases when the artifact is large, risky, or multi-step, but it should not invent a new high-level objective when the objective is already clear.

In goal-synthesis mode, ImplementAudit receives only an idea, gap, ambiguous audit target, or request for the next best implementation prompt. It performs enough Gemba and Hoshin Kanri to produce a bounded, evidence-aware Kaizen handoff. If execution should continue under a host goal runner, it prints a ready-to-paste `/goal Using /implementaudit ...` command.

All modes preserve the same method:

- validate the input or synthesize a bounded target
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

When phase planning is needed, planner stages are:

```text
0. Context/tool/memory detection
1. Intake
2. Recon / Gemba
3. Deep think
4. Phase decomposition
5. Write .IMPLEMENTAUDIT roadmap/state/phase specs
6. Plan review + self-critique
6.5 Pre-flight smoke check
7. Print one ready-to-paste /goal, only if not already inside a /goal run
```

Runtime artifacts:

```text
.IMPLEMENTAUDIT/ROADMAP.md
.IMPLEMENTAUDIT/STATE.md
.IMPLEMENTAUDIT/THINKING.md
.IMPLEMENTAUDIT/PROTOCOL.md
.IMPLEMENTAUDIT/phases/phase-N.md
```

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
AUDIT_HANDOFF
```

Completion:

```text
IMPLEMENTAUDIT_RUN_COMPLETE
```

`IMPLEMENTAUDIT_RUN_COMPLETE` may appear only after `AUDIT_COMPLETE`.
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

- re-read `.IMPLEMENTAUDIT/ROADMAP.md` when phase planning was used
- write `.IMPLEMENTAUDIT/phases/audit-fix-<round>.md` for gaps when phase planning was used
- re-run deduplicated mandatory commands
- spot-check deterministic acceptance criteria
- diff-check deliverables against `Baseline ref`
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

## CHANGELOG / README / CLAUDE

CHANGELOG:

- Keep-a-Changelog style.
- Keep `[Unreleased]` at top.
- Match manifest version if one exists.
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
test -f IMPLEMENTAUDIT.md
test -f AGENTS.md
test -f CHANGELOG.md
test -f skills/SKILL.md
test -f skills/templates/PROTOCOL.md
test -f skills/templates/ROADMAP.md
test -f skills/templates/STATE.md
test -f skills/templates/phase-goal.txt
test -f skills/scripts/validate-phase.sh
python -m json.tool .claude-plugin/plugin.json >/dev/null
python -m json.tool .claude-plugin/marketplace.json >/dev/null
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
grep -R "IMPLEMENTAUDIT_PHASE_START" -n skills IMPLEMENTAUDIT.md
grep -R "IMPLEMENTAUDIT_PHASE_VERIFY" -n skills IMPLEMENTAUDIT.md
grep -R "IMPLEMENTAUDIT_PHASE_DONE" -n skills IMPLEMENTAUDIT.md
grep -R "AGENTS_UPDATE_DECISION" -n skills IMPLEMENTAUDIT.md
grep -R "AUDIT_COMPLETE" -n skills IMPLEMENTAUDIT.md
grep -R "IMPLEMENTAUDIT_RUN_COMPLETE" -n skills IMPLEMENTAUDIT.md
grep -R ".IMPLEMENTAUDIT" -n skills IMPLEMENTAUDIT.md README.md AGENTS.md
```

Check that no legacy external planner names or artifact directories appear in repo files.

---

## Working state target

```text
Canonical skill: skills/SKILL.md
Compatibility root: IMPLEMENTAUDIT.md
Runtime dir: .IMPLEMENTAUDIT/
Planner: Stage 0 through Stage 7 when goal synthesis or phase planning is needed
Executor: supplied target or one-paste /goal, phase loop when needed, failure recovery, final audit
Optional tooling: Graphify orientation, ActiveGraph custody, Markdown fallback
```

## Install flows

README owns exact public install commands.

Do not label an install flow “verified working” unless it was tested in the relevant host during the current release gate.

Codex has no marketplace auto-update path. Manual skill copy must be repeated when the package changes.

## Transcript markers (load-bearing)

### Inside the `/goal` session

Named blocks the executing agent must print into the transcript. The host's `/goal` evaluator + the user both read them.

- `IMPLEMENTAUDIT_PHASE_START` — once per phase, at the start. Metadata only.
- `IMPLEMENTAUDIT_PHASE_VERIFY` — once per phase, before DONE. Each criterion pass/fail with evidence; engineering checks; **`Cleanliness:` section** with grep counts vs `Baseline ref` (debug prints, session TODO/FIXME, dead imports).
- `AGENTS_UPDATE_DECISION` — once per phase or final audit. States whether a durable repo-local rule was added, not warranted, or requires owner decision. If updated, identify scope: root `AGENTS.md`, nearest scoped `AGENTS.md`, or specialist/subagent guidance.
- `IMPLEMENTAUDIT_PHASE_DONE` — once per phase, final block.
- `FAILURE_PROBE` / `FAILURE_ESCALATE` / `FAILURE_HANDOFF` — 3-strike phase-criterion recovery.
- `AUDIT_START` / `AUDIT_VERIFY` (includes a `Deliverables:` block from the diff-based check vs `Baseline ref) / `AUDIT_GAPS` / `AUDIT_COMPLETE` (includes `Audit coverage:`) / `AUDIT_HANDOFF` — final audit pass.
- `IMPLEMENTAUDIT_RUN_COMPLETE` — only after `AUDIT_COMPLETE`. Run is done. Prepends a `⚠ Audit coverage: …` warning banner when trust-prior is > 30% of total checks.

The `/goal` end-state requires `IMPLEMENTAUDIT_RUN_COMPLETE` preceded by `AUDIT_COMPLETE` and one `IMPLEMENTAUDIT_PHASE_DONE` per phase, with no `FAILURE_HANDOFF` or `AUDIT_HANDOFF`.

### Inside the planner session

Before the user pastes `/goal`, the planner emits two additional named blocks the user sees in Stage 6/6.5:

- `Self-critique:` — printed inside the Stage 6 plan-review summary (Stage 6a). 1–3 findings (falsifiability of criteria, phase atomicity, weakest dependency) or `clean`. Falsifiability issues are rewritten in place in the phase specs before the summary prints — so the user sees the post-critique version.
- `PREFLIGHT_GREEN` / `PREFLIGHT_RED` — Stage 6.5 output after running the deduplicated mandatory commands once. `PREFLIGHT_RED` re-enters Stage 6 with a "Skip pre-flight, dispatch anyway" option for cases where the broken baseline is exactly what phase 1 will fix.

These are not part of the `/goal` end-state — the `/goal` session hasn't started yet at this point — but they're load-bearing for plan quality.

### Other v0.x state

Full format spec: `skills/references/goal-format.md`.

## Gotchas

- **Slash commands fire only from user input.** Agent text containing `/goal "..."` is *not* parsed as a command. Stage 7 is a one-paste handoff — the planner prints the line, the user pastes it. Never frame this as "automatic dispatch."
- **Plugin cache only refreshes on version-field change.** If you push a code change without bumping `plugin.json` version, `claude plugin update` reports "already at latest" and the cache stays stale. Always bump on shipped changes.
- **`.gitignore` extension filter**: the file has no extension, so `find -name "*.md"` etc. skip it. When doing mass renames, include the gitignore separately.
- **Codex install is a one-way copy**. There is no marketplace auto-update path. Repeat the README-documented manual copy command when the package changes, and keep that command aligned with the actual `skills/` package layout.
- **Durable repo-specific learning belongs in AGENTS.md, not user memory.** The agent emits `AGENTS_UPDATE_DECISION` to state whether a durable rule was added, not warranted, or requires owner decision.
- **Do not print a second `/goal` when already operating inside a `/goal using /implementaudit ...` run.**
- **Mermaid renders natively in GitHub README** but not always in every external markdown viewer. Stick to standard Mermaid syntax (flowchart TD / LR, subgraphs, classDef styling).

## Reference docs

The package migration is not just file movement. The method is split into reference docs so future maintainers do not need to understand one monolithic skill file.

Required reference set:

- `planning-depth.md` — when ImplementAudit should synthesize a goal vs govern a supplied one.
- `phase-design.md` — how to slice audit closure into verifiable phases.
- `goal-format.md` — `/goal` handoff shape, transcript markers, final audit end-state.

Optional later references:

- `activegraph-graphify.md`
- `agents-standardization.md`
- `kaizen-hansei-hoshin-nemawashi.md` — operating vocabulary and when each method applies.
- `evidence-boundaries.md` — proof levels, trust-prior, Graphify/ActiveGraph limits, and no-provenance-without-evidence.

## Related

- Repo: https://github.com/theIslampill/IMPLEMENTAUDIT.md
