# IMPLEMENTAUDIT.md

`IMPLEMENTAUDIT.md` names this repo and workflow: audited implementation driven
by an `AUDIT.md`-style evidence/input artifact. The `.md` in the repo name is
branding and lineage, not a required root behavior file.

`skills/SKILL.md` defines `/implementaudit`: a repo-generic method for turning
audit findings, handoffs, checklists, reviews, goals, tasks, gaps, and
implementation plans into bounded, verified repository changes.

It is for audit closure and repo hygiene: read the real repo, find the
owner/source, make the smallest warranted change, prove only what the evidence
supports, and close the ledger. It is not a release bot, package publisher,
provenance system, or generic autonomous-build loop.

It does not assume a framework, language, CI system, release convention, package
host, or optional toolchain. Its default authorization stance is:

```text
No commit. No push. No tag. No release. No publication. No provenance.
```

Each action requires separate explicit authorization.

## Contents

- [Runtime at a glance](#runtime-at-a-glance)
- [What it is](#what-it-is)
- [Terminology](#terminology)
- [How an audit input drives a run](#how-an-audit-input-drives-a-run)
- [How IMPLEMENTAUDIT audits](#how-implementaudit-audits)
- [Invocation modes](#invocation-modes)
- [Native planner stages](#native-planner-stages)
- [Greenfield / brownfield routing](#greenfield--brownfield-routing)
- [Execution gates](#execution-gates)
- [Loopability, Andon, and handoff states](#loopability-andon-and-handoff-states)
- [Optional tooling](#optional-tooling)
- [Usage examples](#usage-examples)
- [Install notes](#install-notes)
- [Upgrade / reinstall](#upgrade--reinstall)
- [Artifacts and outputs](#artifacts-and-outputs)
- [Skill internals / repository layout](#skill-internals--repository-layout)
- [Validation and release evidence](#validation-and-release-evidence)
- [Version and release notes](#version-and-release-notes)
- [What this does not do](#what-this-does-not-do)

## Runtime at a glance

```text
Input artifact -> live repo inspection -> owner/source patch -> Smoke A/B -> trace -> final audit
```

The small loop closes one supplied audit/handoff/checklist/review/plan. The
larger package loop can synthesize a bounded `/goal` handoff when the user gives
only an idea, gap, or incomplete target.

## What it is

`/implementaudit` is the officer/method layer for audit closure and repo hygiene.
It is an audit-governed implementation skill: it routes work through repo-local
owner/source discovery, acceptance criteria, rollback/evidence planning,
fixtures/checkers, and smoke-before-claim closure. It can help implement
changes, but only through the audit contract; it is not a generic autonomous
build runner.

Current optional-tooling architecture:

<!-- BEGIN: implementaudit-diagram:tooling-architecture -->

```mermaid
flowchart LR
  I["ImplementAudit<br/>officer / method / standard"]
  G["Graphify<br/>optional terrain / repo map<br/>orientation, not proof"]
  A["ActiveGraph<br/>optional custody / event evidence<br/>not correctness proof"]
  C["Capability Ledger<br/>derived work history"]
  M["Markdown fallback<br/>always valid when optional tools are absent"]
  L["Live files<br/>source of truth"]

  G -->|where to look| I
  I -->|must confirm in| L
  I -->|gate passages, smokes, Andons, closures| A
  A -->|what happened, not proof by itself| C
  I -->|competence standard| C
  I -->|when tools are absent| M
```

<!-- END: implementaudit-diagram:tooling-architecture -->

Graphify and ActiveGraph are optional. `/implementaudit` remains fully usable
when neither tool is installed.

Graphify and ActiveGraph are optional but strategically important: Graphify
improves orientation before mutation, while ActiveGraph preserves custody after
evidence is produced. Neither replaces ImplementAudit's gates; both strengthen
the audit trail when available.

## Terminology

- `AUDIT.md`: an audit input or evidence-implementation artifact that drives a
  dogfooded run. It may be a file, attachment, pasted audit, handoff, checklist,
  review, goal, task, gap, or implementation plan.
- Greenfield: a new governed artifact or capability where owner/source,
  contract, acceptance, rollback, and evidence must be defined before
  implementation.
- Brownfield: mutation or verification of an existing repo surface where
  owner/source, contracts, tests, generated artifacts, and regression surface
  must be inspected before change.
- Mixed mode: brownfield outer repo work that creates a greenfield subartifact.
- Owner/source: the canonical file, schema, script, fixture, or doc that owns a
  claim or behavior.
- Generated artifact: derived output that must be regenerated from source, not
  hand-edited.
- Smoke A / Smoke B: baseline or pre-change verification, then post-change
  verification compared against that baseline.
- Andon: a visible abnormality or blocker signal. Failed, hung, substituted, or
  rerun release-gate commands count even if later contained.
- 5 Whys: a root-cause drill for why an abnormality happened and what
  countermeasure prevents recurrence.
- Hansei: structured reflection: gap, cause, countermeasure, and follow-up
  evidence.
- Kaizen: durable process improvement folded back into the standard.
- Gemba / Genchi Genbutsu: inspect the real repo artifact, output, or path; do
  not rely on memory or summaries when the live surface exists.
- Graphify: optional terrain/orientation aid; not canonical proof.
- ActiveGraph: optional custody/sidecar evidence substrate; not canonical proof.
- Provenance/checksum manifest: bounded artifact integrity evidence. A checksum
  manifest is not a signature, SBOM, attestation, marketplace verification, or
  install proof.

## How an audit input drives a run

An `AUDIT.md`-style input names the work to close and the evidence expected for
closure. `/implementaudit` normalizes that input into ledger items, classifies
priority, finds owner/source, records Smoke A, patches only warranted surfaces,
records Smoke B, and closes each item as `done`, `changed`, `blocked`,
`deferred`, or `unverified`.

The input does not authorize hidden side effects. Tool install, indexing,
event-store setup, local commit, push, tag, release, publication, and provenance
remain separate gates even when the audit asks for implementation.

## How IMPLEMENTAUDIT audits

IMPLEMENTAUDIT uses `audit` in two linked senses:

- `tdqyq-audit-object`: the audit-as-noun surface. It is the evidence-bearing
  record or state for the run: scope, owner/source, claims, changed files,
  checks, marker state, unresolved gaps, and terminal closure. In a real run it
  may be represented by `.IMPLEMENTAUDIT/PROTOCOL.md`,
  `.IMPLEMENTAUDIT/STATE.md`, `.IMPLEMENTAUDIT/THINKING.md`,
  `.IMPLEMENTAUDIT/ROADMAP.md`, `.IMPLEMENTAUDIT/phases/*`, transcript markers,
  release/package evidence, and closure tables.
- `ydqyq-audit-action`: the audit-as-verb operation. It inspects, classifies,
  verifies, authorizes or rejects mutation, closes findings, or produces a
  handoff against the live `tdqyq-audit-object`.

Implementation is allowed only against a live `tdqyq-audit-object`.
`AUDIT_COMPLETE` means that object reached terminal verified closure.
`IMPLEMENTAUDIT_RUN_COMPLETE` is invalid before that closure.

The double-audit loop is: first `ydqyq-audit-action` inspects and produces or
updates the `tdqyq-audit-object`; second `ydqyq-audit-action` acts against that
object to close findings; final `ydqyq-audit-action` verifies terminal closure
of the object.

## Invocation modes

`/implementaudit` has three invocation shapes:

<!-- BEGIN: implementaudit-diagram:invocation-modes -->

```mermaid
flowchart TB
  Final["Terminal audit-object closure<br/>AUDIT_COMPLETE before<br/>IMPLEMENTAUDIT_RUN_COMPLETE"]:::success

  subgraph Direct["Direct governance"]
    DIn["Input<br/>/implementaudit + bounded audit<br/>handoff / checklist / review"]:::input
    DObj["tdqyq-audit-object<br/>user supplies or implies it"]:::artifact
    DLoop["ydqyq-audit-action<br/>inspect -> classify -> patch -> verify"]:::loop
    DArt["Artifacts<br/>findings ledger<br/>source patches<br/>Smoke A/B evidence"]:::artifact
    DGoal["Second /goal<br/>not needed"]:::boundary
    DIn --> DObj --> DLoop --> DArt --> DGoal
  end

  subgraph Embedded["Embedded governance"]
    EIn["Input<br/>/goal already owns the run<br/>using /implementaudit"]:::input
    EObj["tdqyq-audit-object<br/>owned by outer /goal"]:::artifact
    ELoop["ydqyq-audit-action<br/>govern inside supplied target"]:::loop
    EArt["Artifacts<br/>active goal evidence<br/>ledger updates<br/>repo-local checks"]:::artifact
    EGoal["Second /goal<br/>forbidden"]:::blocker
    EIn --> EObj --> ELoop --> EArt --> EGoal
  end

  subgraph Synthesis["Goal synthesis / phased handoff"]
    SIn["Input<br/>idea / gap / incomplete target"]:::input
    SObj["tdqyq-audit-object<br/>created or normalized first"]:::artifact
    SLoop["ydqyq-audit-action<br/>Gemba + route + Stage 0-7 planning"]:::loop
    SArt["Artifacts<br/>.IMPLEMENTAUDIT roadmap/state<br/>thinking/protocol/phase specs"]:::artifact
    SGoal["Second /goal<br/>produced once when not embedded"]:::handoff
    SIn --> SObj --> SLoop --> SArt --> SGoal
  end

  DGoal --> Final
  EGoal --> Final
  SGoal --> Final

  classDef input fill:#eff6ff,stroke:#2563eb,color:#111827
  classDef loop fill:#ecfdf5,stroke:#059669,color:#111827
  classDef artifact fill:#f5f3ff,stroke:#7c3aed,color:#111827
  classDef boundary fill:#f8fafc,stroke:#64748b,color:#111827
  classDef handoff fill:#fff7ed,stroke:#ea580c,color:#111827
  classDef blocker fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
  classDef success fill:#d1fae5,stroke:#059669,color:#064e3b
```

<!-- END: implementaudit-diagram:invocation-modes -->

- **Embedded governance mode**: a host goal/task/plan already exists, such as
  `/goal using /implementaudit ...`. The outer goal owns the
  `tdqyq-audit-object`; ImplementAudit performs `ydqyq-audit-action` inside
  that object and does not print a second `/goal`.
- **Direct governance mode**: the user supplies a concrete audit, handoff,
  checklist, review, or bounded implementation plan. The user supplies or
  implies the `tdqyq-audit-object`; ImplementAudit performs
  `ydqyq-audit-action` and implementation against it.
- **Goal-synthesis mode**: the user supplies an idea, gap, incomplete target, or
  request for the next best implementation prompt. ImplementAudit creates or
  normalizes the `tdqyq-audit-object`, writes phase artifacts, and may print one
  ready-to-paste `/goal Using /implementaudit ...` line only when not already
  embedded.

## Native planner stages

When goal synthesis or phased audit closure is needed, `skills/SKILL.md` defines
a native Stage 0-7 planner contract:

```text
Stage 0 - Context/tool/repo-state detection
Stage 1 - Audit-governed intake and routing
Stage 2 - Recon / Gemba
Stage 3 - Deep think / risk and dependency analysis
Stage 4 - Phase decomposition
Stage 5 - Write .IMPLEMENTAUDIT roadmap/state/thinking/protocol/phase specs
Stage 6 - Plan review and self-critique
Stage 6.5 - Pre-flight smoke
Stage 7 - One ready-to-paste /goal handoff when not already embedded
```

The stage contract is audit-governed: it preserves owner/source patching,
Smoke A/B, generated-artifact discipline, final audit before completion, and
the separate commit/push/tag/release/provenance gates. It does not turn
IMPLEMENTAUDIT into open-ended software-builder automation.

When phased planning is selected, the runtime artifacts live under
`.IMPLEMENTAUDIT/`: `ROADMAP.md`, `STATE.md`, `THINKING.md`, `PROTOCOL.md`, and
`phases/phase-N.md`. `THINKING.md` is reviewable planning evidence for route,
risks, dependencies, rollback, and evidence strategy; it is not proof by itself.

### Why one `/goal`, not a chain

A generated `/goal` should carry the bounded end-state and audit completion
condition. Phase specs live in `.IMPLEMENTAUDIT/*`; the run progresses through
files, checks, and markers rather than a fragile sequence of user-pasted
commands. Final completion still requires `AUDIT_COMPLETE` before
`IMPLEMENTAUDIT_RUN_COMPLETE`.

Inside embedded governance, another `/goal` already owns the run, so
`/implementaudit` must not emit a nested goal. In goal-synthesis mode, it may
produce one ready-to-paste `/goal Using /implementaudit ...` handoff after
Gemba, phase planning, self-critique, and pre-flight.

## Default behavior

The default small audit implementer mode works on one audit, handoff, checklist,
review, or implementation plan.

It:

- validates that the input is a recognizable audit artifact
- normalizes findings into a ledger
- classifies items as `P0`, `P1`, `P2`, `OWNER DECISION`, `DEFERRED`, or
  `OUT OF SCOPE`
- processes work in `P0 -> P1 -> P2` order
- patches owner/source, not nearest symptom
- requires evidence for every claim
- closes every item as `done`, `changed`, `blocked`, `deferred`, or
  `unverified`

No ledger item may remain open at final response.

## Greenfield / brownfield routing

ImplementAudit classifies work before planning or mutation:

- **Greenfield**: a new governed artifact, fixture family, checker, reference,
  workflow, runtime capability, sidecar contract, or validation surface is being
  introduced and has no established repo owner/source yet.
- **Brownfield**: an existing repo artifact, owner/source, generated output,
  fixture, checker, contract, or documented invariant is being repaired,
  verified, or closed.
- **Mixed**: a new artifact is introduced inside an established repo. The outer
  shell is brownfield; the new artifact receives greenfield intake after the
  existing repo surface is inspected.

Greenfield work must define owner/source, scope and non-scope, constraints,
acceptance criteria, rollback/removal path, evidence plan, generated-artifact
plan, sidecar status, and canonical-vs-sidecar boundaries before implementation.

Brownfield work must inspect existing owner/source, contracts, tests, smokes,
checkers, generated artifacts, optional sidecars, regression surface, and
rollback path before mutation.

Graphify may orient brownfield terrain when available and fresh, but live files
remain source of truth. ActiveGraph may preserve custody when configured, but
Markdown ledgers and final reports remain valid fallback. Neither optional
sidecar replaces repo-local owners, fixtures, checkers, smoke output, or audit
ledgers.

## Operating method

The method combines:

- **PDCA**: plan the smallest safe change, do it, check evidence, then
  standardize or revise.
- **Gemba**: inspect the real place of work, not summaries when live artifacts
  exist.
- **Smoke Before Claim**: tag every behavior claim with the smallest meaningful
  evidence.
- **Smoke A / Smoke B**: capture the pre-change baseline, then compare
  post-change checks to detect regressions.
- **Andon**: surface blockers, failures, unclear ownership, or unsafe
  conditions immediately.
- **Hansei**: reflect after gaps, regressions, false passes, or failures.
- **5 Whys**: trace symptoms to root cause when the situation warrants it.
- **Plan Closure**: map every item to a terminal status.

Static checks, local generated-runtime evidence, manual inspection, browser
evidence, package-bound checks, unit tests, and live runtime checks are not
interchangeable. Proof claims must not exceed the evidence type.

## Execution gates

The gate diagram shows the normal path and the places where the method must
stop, recover, or hand off instead of pretending the run is complete.

<!-- BEGIN: implementaudit-diagram:execution-spine -->

```mermaid
flowchart TD
  Input(["Audit-style input / handoff / goal / gap"]):::human
  Route["Route before mutation<br/>greenfield / brownfield / mixed<br/>brownfield recon is read-only"]:::audit
  OwnerDecision(["OWNER DECISION<br/>unsafe request or AGENTS/policy conflict"]):::blocker

  Graphify["Graphify optional terrain<br/>orientation only, not proof"]:::optional
  Gemba["Live-file Gemba<br/>confirm owner/source before mutation"]:::source
  SmokeA["Smoke A<br/>baseline before change"]:::checker
  Patch["Patch owner/source<br/>bounded P0 -> P1 -> P2"]:::source
  Generated["Refresh generated artifacts<br/>from source/generator"]:::generated
  SmokeB["Smoke B + complete<br/>working-tree-vs-baseline check"]:::checker

  ActiveGraph["ActiveGraph optional custody<br/>after evidence exists<br/>not correctness proof"]:::optional
  Ledger["Capability Ledger or<br/>Markdown final report fallback"]:::audit

  Andon["Andon / handoff loop<br/>abnormality -> 5 Whys -> Hansei<br/>countermeasure -> rerun"]:::blocker
  Final["Final audit<br/>criteria, boundaries, evidence"]:::audit
  AuditDone(["AUDIT_COMPLETE"]):::success
  RunDone(["IMPLEMENTAUDIT_RUN_COMPLETE"]):::success
  NoRelease["Ordinary completion default<br/>No tag, release, publication, or provenance"]:::audit
  ReleaseGate{"Separate release/provenance gate<br/>explicitly authorized?"}:::release
  Release["Tag / release / asset<br/>checksum manifest only if produced and verified"]:::release
  Legend["Legend: amber human/owner; blue owner/source; purple generated;<br/>green checks; dashed green optional; red blocker; orange release"]:::audit

  Input --> Route
  Route -->|unsafe / conflict| OwnerDecision
  Route -->|authorized scope| Gemba
  Graphify -. optional query before touching scene .-> Gemba
  Gemba --> SmokeA --> Patch --> Generated --> SmokeB
  SmokeB -. custody sidecar .-> ActiveGraph --> Ledger
  SmokeB --> Final
  SmokeA -->|unclear baseline| Andon
  SmokeB -->|regression / failed gate| Andon
  Final -->|gap remains| Andon
  Andon -->|fixable rerun| Gemba
  Final -->|all findings closed| AuditDone --> RunDone --> NoRelease
  RunDone -. separate explicit gate only .-> ReleaseGate
  ReleaseGate -->|authorized + evidence| Release
  ReleaseGate -->|not authorized| NoRelease
  Legend -. explains classes .-> Route

  classDef human fill:#fef3c7,stroke:#d97706,color:#111827
  classDef source fill:#e0f2fe,stroke:#0284c7,color:#111827
  classDef generated fill:#ede9fe,stroke:#7c3aed,color:#111827
  classDef checker fill:#dcfce7,stroke:#16a34a,color:#111827
  classDef audit fill:#f1f5f9,stroke:#475569,color:#111827
  classDef optional fill:#f0fdf4,stroke:#65a30d,color:#111827,stroke-dasharray: 4 3
  classDef release fill:#fff7ed,stroke:#ea580c,color:#111827
  classDef success fill:#d1fae5,stroke:#059669,color:#064e3b
  classDef blocker fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
```

<!-- END: implementaudit-diagram:execution-spine -->

| Gate | Purpose |
|---|---|
| Safety read | Read repo instructions, safety defaults, authorization gates, and `AGENTS.md` conflict rules. |
| Input gate | Confirm the input is a valid audit artifact. |
| Pre-flight | Detect optional tooling, confirm write access, source/generator ownership, authorization chain, repo constraints, and prior run state. |
| Smoke A | Run and classify baseline checks before mutation. |
| Implement | Patch items atomically in priority order and guard scope creep. |
| Smoke B | Compare post-change checks against Smoke A and trigger regression protocol when needed. |
| Trace | Preserve causal history in commit body or proposed commit body, ledger, optional Capability Ledger, and `AGENTS.md` only when warranted. |
| Self-check | Verify quality-bar invariants before final response. |

If an audit finding contradicts repo-local `AGENTS.md` or policy, the conflict
becomes `OWNER DECISION`. The agent does not silently choose which instruction
wins.

## Loopability, Andon, and handoff states

An IMPLEMENTAUDIT run is loopable. It can end in `AUDIT_COMPLETE` plus
`IMPLEMENTAUDIT_RUN_COMPLETE`, or it can end in `AUDIT_HANDOFF`, `blocked`,
`deferred`, or `unverified` states with enough evidence for a later agent to
resume, audit, or repair the work.

Completion is not "deliverables exist." Completion means owner/source changes,
generated outputs, smoke/check evidence, final audit, ledger closure, and
terminal markers all align.

Andons are loop points, not just errors:

```text
record abnormality -> 5 Whys -> Hansei -> countermeasure -> rerun relevant checks -> close/defer/block with evidence
```

If a checker, shell command, diagram generator, package validator, release-gate
command, or provenance command fails, hangs, shell-errors, or is replaced by a
rerun/substitute path, record the abnormal path as an Andon before closing it as
blocking or non-blocking.

Post-release corrections patch forward. If a release is already out, do not
pretend the gate is still pre-release; record the post-release audit status,
make a follow-up source-owned correction when warranted, and propose any release
notes correction before editing release metadata.

Release and checksum-manifest provenance are a separate gated loop after
ordinary audit completion. Ordinary success does not imply tag, release,
publication, asset upload, checksum publication, signature, attestation, SBOM,
marketplace verification, or install verification.

## Artifacts and outputs

Typical run outputs are a normalized findings ledger, changed owner/source files
when authorized by the audit, regenerated artifacts when their source changed,
Smoke A/B evidence, an AGENTS update decision, a final report, and terminal
markers. Large or phased runs may also create `.IMPLEMENTAUDIT/` local runtime
artifacts such as roadmaps, state files, phase specs, or protocol files; those
are run artifacts, not package source.

The packaged skill payload lives under `skills/`. GitHub release assets, when
separately authorized, are built from the repo-supported release-asset script
and validated by extraction. Release artifacts and checksum manifests are not
ordinary audit outputs.

## Skill internals / repository layout

This repo uses the flat package layout declared by `AGENTS.md`:

```text
skills/SKILL.md
skills/references/
skills/scripts/
skills/templates/
```

`skills/SKILL.md` is the canonical behavior source and packaged skill entry.
There is intentionally no tracked root `IMPLEMENTAUDIT.md` file; validators fail
if one is recreated. Audit handoff inputs named `AUDIT.md` remain valid.

Package metadata lives under `.claude-plugin/`:

```text
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
```

The manifest JSON is validated by `scripts/verify-package.sh`. This README does
not claim that Claude Code marketplace behavior, Codex installation, release,
publication, or provenance has been verified.

## Version and release notes

Current project milestone: `v0.2.4.0`. Plugin manifest version: `0.2.4`.
No local schema evidence proved four-component plugin manifest versions are
accepted, so the manifest uses host-conservative package metadata while the
project milestone is recorded in docs and changelog. This is not a tag, release,
publication, or provenance claim by itself.

See `CHANGELOG.md` and the GitHub Releases page for release notes. Release notes
may document release assets and checksum manifests only after those artifacts
exist and are verified.

There is no `LICENSE` file in this repo yet. License selection remains an owner
decision.

## Child-agent review loops

`/implementaudit` may use child agents or subagents as bounded review loops when
the host supports them, or may simulate the same pattern as separate written
read-only audit passes.

The package includes `skills/references/child-agents.md` and
`skills/templates/child-agent-report.md` as explanatory/reference material.
Instruction precedence remains with the repo's `AGENTS.md` hierarchy. Root
`AGENTS.md` holds repo-wide child/subagent rules; scoped `AGENTS.md` or
`AGENTS.override.md` is used only for subtree-specific guidance when that
host/repo convention is available.

Child-agent reports do not prove correctness and do not authorize edits,
commits, pushes, installs, indexing, exports, releases, publication, or
provenance. The main `/implementaudit` agent must normalize reviewer findings
into the ledger and inspect live files before patching or closing them.

## Optional tooling

Optional tooling can improve orientation and custody, but it does not change
`/implementaudit` safety rules.

Tool installation, Graphify indexing, ActiveGraph event-store setup,
ActiveGraph export, local commit, push, tag, release, publication, and
provenance are separate gates. Installing a tool does not authorize any later
action.

### First-run onboarding

On first runs, `/implementaudit` may detect Graphify and ActiveGraph
availability. Missing tools are not errors.

Default behavior:

- detect and record availability
- continue safely without optional tooling when absent
- print install/configure commands as documentation when useful
- install or configure tools only with explicit authorization such as
  `/implementaudit --onboard-tools` or a direct user instruction

Documented onboarding commands:

```bash
uv tool install graphifyy
graphify install --platform codex
graphify install --project --platform codex

pip install activegraph
activegraph quickstart
```

These commands are documentation only in this repo state. Running them requires
explicit authorization. Installation does not authorize indexing, event-store
setup, export, commit, push, tag, release, publication, or provenance.

### Graphify-assisted Gemba

Graphify is the optional catalog / terrain map. When available and fresh, or
when indexing/querying is explicitly authorized, `/implementaudit` can query it
before touching the scene.

Graphify can help identify:

- owner/source candidates
- dependency paths
- generated-artifact hints
- impact surfaces
- smoke/test candidates
- scope-creep signals
- stale assumptions
- source/generated output relationships

Graphify output is orientation evidence, not proof. It does not prove
correctness, decide closure, authorize mutation, replace live-file inspection,
override repo instructions, or weaken `AGENTS.md`.

Graphify terrain tagged `INFERRED` or `AMBIGUOUS` requires live-file
confirmation before implementation, closure, or proof claims. Live files win
over graph output. If Graphify is absent or stale, `/implementaudit` falls back
to ordinary Gemba.

### ActiveGraph-backed Capability Ledger

ActiveGraph is the optional evidence locker / custody substrate. When
configured, ActiveGraph-backed `/implementaudit` runs may derive Capability
Ledger entries as the natural custody-backed output of the run.

The Capability Ledger / Officer CV is ImplementAudit-derived. It is not an
upstream ActiveGraph built-in feature. ActiveGraph provides the event custody
substrate; ImplementAudit derives capability entries from recorded gate passages
and evidence.

Entries may include:

- run id
- repo identity
- finding class
- owner/source
- countermeasure
- Graphify terrain context, if available
- ActiveGraph custody events, if available
- authorization gates respected
- Smoke A and Smoke B
- regression / Andon / Hansei trail, if any
- final status
- remaining risk

When ActiveGraph is absent, the ordinary Markdown ledger and final report remain
first-class fallback. The run is not blocked merely because ActiveGraph is
unavailable.

## Evidence boundaries

Interop boundaries are explicit:

- Graphify-supported behavior must be distinguished from ImplementAudit
  heuristics.
- Graphify summaries and graph output are not proof.
- ActiveGraph custody is not correctness proof.
- ImplementAudit custom adapter events are not upstream ActiveGraph built-ins
  unless explicitly identified as such.
- ActiveGraph policies gate graph object proposals, graph patches, and wrapped
  behaviors/tools/proposals.
- ActiveGraph does not inherently gate shell commands, git commit, git push,
  tag, release, publication, or provenance unless those actions are modeled
  through wrapped ActiveGraph behavior/tool/proposal semantics.
- Object/relation mappings are ImplementAudit-specific or Diligence-style
  adapter mappings, not upstream ActiveGraph base types.
- Release and provenance claims require separate authorization and evidence.

## Usage examples

```text
/implementaudit < audit.md
/implementaudit implement these findings
/implementaudit --onboard-tools
/goal using /implementaudit, close the findings in AUDIT.md
```

Natural-language requests such as "implement these findings", "act on this
audit", "close these items", or "work through this handoff" also invoke the
method when the input is a valid audit artifact.

## Install notes

Install flows are evidence-bounded. This repo can locally validate the release
asset-to-Codex-install path into a temporary Codex home. It does not claim passive auto-update, universal host support, marketplace verification, or public GitHub release download verification unless those checks are run and recorded.

### Install / update for Codex

Codex manual installs copy the packaged skill payload into a Codex-style skill
directory. A public GitHub release by itself cannot update a local copied skill.

From a repo checkout, the simplest manual copy is:


```bash
mkdir -p ~/.codex/skills/implementaudit
cp -R skills/* ~/.codex/skills/implementaudit/
```

PowerShell equivalent:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills\implementaudit" | Out-Null
Copy-Item -Recurse -Force .\skills\* "$env:USERPROFILE\.codex\skills\implementaudit\"
```

For a local release asset, build the asset, write checksums, and install with
checksum verification:

```bash
bash scripts/build-release-asset.sh
bash scripts/write-release-checksums.sh dist/IMPLEMENTAUDIT.skill dist/CHECKSUMS.txt
bash scripts/install-codex-from-release.sh \
  --asset dist/IMPLEMENTAUDIT.skill \
  --checksum dist/CHECKSUMS.txt \
  --codex-home "$HOME/.codex" \
  --version 0.2.4
```

After a public release exists, the same installer can be pointed at an explicit
tag or asset URL from a source checkout:

```bash
bash scripts/install-codex-from-release.sh --tag v0.2.4.0 --version 0.2.4
```

That public-download path is a claim only after the release exists and the
download/checksum/install smoke is actually run. If it cannot be run, treat it
as unverified or handoff evidence, not as install proof.

### Install / update for Claude Code

Claude Code/plugin consumers should use the host's current plugin instructions
with `.claude-plugin/plugin.json` as package metadata. This repo validates the
JSON shape only; it does not claim host install or marketplace behavior was
tested.

For public clone/plugin setup, an HTTPS repository URL is usually the simplest
path because it does not require local SSH key configuration. SSH URLs are fine
when the user already has working GitHub SSH authentication in that host.

## Upgrade / reinstall

After a release, reinstall or update the skill in the host you use. Do not
assume a local copied skill has updated just because the GitHub repo has a new
release.

For Codex manual installs, there is no marketplace auto-update path documented
in this repo. Repeat the documented copy step or release-asset install step
after each release:

```bash
mkdir -p ~/.codex/skills/implementaudit
cp -R skills/* ~/.codex/skills/implementaudit/
```

PowerShell:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills\implementaudit" | Out-Null
Copy-Item -Recurse -Force .\skills\* "$env:USERPROFILE\.codex\skills\implementaudit\"
```

Claude Code/plugin users should use the host's documented plugin update or
reload flow when available. This repo does not claim that plugin update,
marketplace refresh, install, release, publication, or provenance behavior has
been verified.

## Release asset notes

For package release gates, including `v0.2.4.0`, the GitHub release asset name is
`IMPLEMENTAUDIT.skill`.

No local evidence proves `.skill` is a universal host-standard archive format.
In this repo, `IMPLEMENTAUDIT.skill` is the GitHub release artifact name. It is
a ZIP-format archive containing the installable skill payload:

```text
skills/
.claude-plugin/
```

The release asset intentionally excludes repo-maintenance material such as
README generation sources, audit ledgers, release-candidate notes, fixtures,
tests, CI config, Git metadata, and root validation scripts. Those remain
repo-side evidence and maintenance surfaces, not installed runtime payload.

Build and validate it locally with:

```bash
bash scripts/build-release-asset.sh
```

`scripts/verify-package.sh` also runs the builder in `--check` mode and validates
the extracted package shape.

When provenance is explicitly authorized for a release gate, this repo may
publish a checksum manifest such as `CHECKSUMS.txt` for `IMPLEMENTAUDIT.skill`.
A checksum manifest is not a signature, attestation, SBOM, license, marketplace
verification, or install verification.

The artifact must not include `.IMPLEMENTAUDIT/` run artifacts, local smoke
debris, Graphify outputs, ActiveGraph stores, secrets, git metadata, or
untracked diagnostics. Attaching `IMPLEMENTAUDIT.skill` to GitHub Releases is a
separate release-gate action. Ordinary audits, local commits, and push-only
gates do not authorize upload, release, publication, marketplace verification,
or provenance claims.

## Validation and release evidence

Repo-native validation includes README diagram freshness, ToC anchor checks,
host-claim and forbidden-claim scans, root behavior-file absence, package
contract validation, routing fixtures, marker-order checks, repo-state checks,
audit-spec checks, release-asset extraction checks, release-asset Codex install
smoke, stale-checksum failure smoke, and checksum-manifest checks.

Run the package validator before local commit or release-gate claims:

```bash
bash scripts/verify-package.sh
```

When release assets are mentioned, validate the release asset locally:

```bash
bash scripts/build-release-asset.sh
bash scripts/write-release-checksums.sh dist/IMPLEMENTAUDIT.skill dist/CHECKSUMS.txt
bash scripts/write-release-checksums.sh --check
bash tests/release-asset-install.test.sh
```

For `v0.2.4.0`, the intended GitHub release assets are `IMPLEMENTAUDIT.skill` and
`CHECKSUMS.txt`. The checksum manifest is bounded artifact-integrity evidence
only; it is not a signature, attestation, SBOM, marketplace verification,
license claim, or install proof.

## Safety defaults

Never do these unless explicitly authorized and allowed by repo policy:

- commit
- push
- tag
- publish
- create or update releases
- delete data
- alter credentials or secrets
- rewrite history
- commit raw diagnostic outputs
- hand-edit generated artifacts when a source generator exists
- claim proof without evidence

Local commit authorization does not imply push authorization. Push authorization
does not imply tag, release, publication, or provenance authorization.

If local commits are authorized, commit bodies carry the causal trace: finding,
owner/source, root cause when relevant, Andon/Hansei/5 Whys when triggered,
countermeasure, changed files, Smoke A/B, boundaries preserved, and deferred
follow-up.

If local commits are not authorized, the final report includes a proposed commit
message/body instead.

## What this does not do

`/implementaudit` does not:

- make Graphify or ActiveGraph hard dependencies
- silently install tools
- silently run indexing
- silently create ActiveGraph config or event stores
- silently export custody events
- treat install success as audit proof
- treat Graphify output as correctness proof
- treat ActiveGraph custody as correctness proof
- push, tag, release, publish, or make provenance claims without explicit
  authorization
- resolve audit-vs-`AGENTS.md` conflicts by agent judgment
- use `AGENTS.md` as a raw evidence dump

## Development / maintenance notes

`AGENTS.md` is the authoritative repository contract. `skills/SKILL.md` is the
canonical skill behavior source under the current flat package contract.

README Mermaid diagrams are generated from `docs/diagrams/*.mmd`; do not edit
diagram blocks by hand. Refresh or check them with:

```bash
bash scripts/generate-readme-diagrams.sh
bash scripts/generate-readme-diagrams.sh --check
```

Validation scripts are POSIX shell scripts. On Windows, run them from Git Bash
or WSL. The repo pins `*.sh` files to LF line endings for shell portability.

Before committing package changes, run:

```bash
git diff --check
python -m json.tool .claude-plugin/plugin.json
python -m json.tool .claude-plugin/marketplace.json
bash scripts/verify-package.sh
```

Also run:

```bash
bash skills/scripts/validate-phase.sh skills/templates/phase-goal.txt
```

Preserve the distinction between:

- upstream-supported behavior
- ImplementAudit custom extension
- repo-local heuristic
- unsupported or uncertain behavior

Detailed evidence belongs in commit bodies, orchestrator/audit ledgers,
ActiveGraph custody events when configured, or final reports. Durable
anti-repeat rules may belong in repo-local `AGENTS.md` when they would prevent
future agents from repeating the same mistake.

Native harness discipline now includes helpers/checkers for environment and
repo-contract discovery, brownfield repo summaries, complete baseline-vs-working
tree evidence, structural audit-spec validation, transcript marker order,
routing fixtures, release-asset checks, and added-line cleanliness/overclaim
scans. Complete repo-state checks compare the baseline to the working tree so
staged, unstaged, deleted, and untracked work cannot disappear from final audit
evidence.
