# IMPLEMENTAUDIT.md

`IMPLEMENTAUDIT.md` defines `/implementaudit`: a repo-generic method for implementing audit findings, handoffs, checklists, reviews, and implementation plans safely.

It converts findings into bounded, verified repo changes. It does not assume a framework, language, CI system, release convention, or optional toolchain.

The default stance is:

```text
No commit. No push. No tag. No release. No publication. No provenance.
```

Each of those actions requires separate explicit authorization.

## What it is

`/implementaudit` is the officer/method layer for closing audit findings. It reads the actual repository, normalizes the input into an implementation ledger, patches the owner/source instead of the nearest symptom, and records evidence before making claims.

The current optional-tooling architecture is:

```text
Graphify = catalog / terrain map
ActiveGraph = evidence locker / custody substrate
ImplementAudit = officer / method
Capability Ledger = derived work history when ActiveGraph is configured
```

Graphify and ActiveGraph are optional. `/implementaudit` remains fully usable when neither is installed.

## Default behavior

The default small audit implementer mode works on one audit, handoff, checklist, review, or implementation plan.

It:

- validates that the input is a recognizable audit artifact
- normalizes findings into a ledger
- classifies items as `P0`, `P1`, `P2`, `OWNER DECISION`, `DEFERRED`, or `OUT OF SCOPE`
- processes work in `P0 -> P1 -> P2` order
- patches owner/source, not nearest symptom
- requires evidence for every claim
- closes every item as `done`, `changed`, `blocked`, `deferred`, or `unverified`

No ledger item may remain open at final response.

## Operating method

The method combines:

- **PDCA**: plan the smallest safe change, do it, check evidence, then standardize or revise.
- **Gemba**: inspect the real place of work, not summaries when live artifacts exist.
- **Smoke Before Claim**: tag every behavior claim with the smallest meaningful evidence.
- **Smoke A / Smoke B**: capture the pre-change baseline, then compare post-change checks to detect regressions.
- **Andon**: surface blockers, failures, unclear ownership, or unsafe conditions immediately.
- **Hansei**: reflect after gaps, regressions, false passes, or failures.
- **5 Whys**: trace symptoms to root cause when the situation warrants it.
- **Plan Closure**: map every item to a terminal status.

Static checks, local generated-runtime evidence, manual inspection, browser evidence, package-bound checks, unit tests, and live runtime checks are not interchangeable. Proof claims must not exceed the evidence type.

## Execution gates

The execution spine is a sequence of non-skippable gates:

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

If an audit finding contradicts repo-local `AGENTS.md` or policy, the conflict becomes `OWNER DECISION`. The agent does not silently choose which instruction wins.

## Optional tooling

Optional tooling can improve orientation and custody, but it does not change `/implementaudit` safety rules.

Tool installation, Graphify indexing, ActiveGraph event-store setup, ActiveGraph export, local commit, push, tag, release, publication, and provenance are separate gates. Installing a tool does not authorize any later action.

### First-run onboarding

On first runs, `/implementaudit` may detect Graphify and ActiveGraph availability. Missing tools are not errors.

Default behavior:

- detect and record availability
- continue safely without optional tooling when absent
- print install/configure commands as documentation when useful
- install or configure tools only with explicit authorization such as `/implementaudit --onboard-tools` or a direct user instruction

Documented onboarding commands include:

```bash
uv tool install graphifyy
graphify install --platform codex
graphify install --project --platform codex

pip install activegraph
activegraph quickstart
```

ActiveGraph repo configuration checks such as `activegraph.toml` or `.activegraph/*` are repo-local heuristics, not upstream ActiveGraph config contracts. A repo may instead document store URLs, runbooks, adapter config, or another convention.

### Graphify-assisted Gemba

Graphify is the optional catalog / terrain map. When available and fresh, or when indexing/querying is explicitly authorized, `/implementaudit` can query it before touching the scene.

Graphify can help identify:

- owner/source candidates
- dependency paths
- generated-artifact hints
- impact surfaces
- smoke/test candidates
- scope-creep signals
- stale assumptions
- source/generated output relationships

Graphify output is orientation evidence only. It does not prove correctness, decide closure, authorize mutation, replace live-file inspection, override repo instructions, or weaken `AGENTS.md`.

Graphify terrain tagged `INFERRED` or `AMBIGUOUS` requires live-file confirmation before implementation, closure, or proof claims. Live files win over graph output. If Graphify is absent or stale, `/implementaudit` falls back to ordinary Gemba.

### ActiveGraph-backed Capability Ledger

ActiveGraph is the optional evidence locker / custody substrate. When configured, ActiveGraph-backed `/implementaudit` runs may derive Capability Ledger entries as the natural custody-backed output of the run.

The Capability Ledger / Officer CV is ImplementAudit-derived. It is not an upstream ActiveGraph built-in feature. ActiveGraph provides the event custody substrate; ImplementAudit derives capability entries from recorded gate passages and evidence.

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

When ActiveGraph is absent, the ordinary Markdown ledger and final report remain first-class fallback. The run is not blocked or degraded merely because ActiveGraph is unavailable.

## Evidence boundaries

Interop boundaries are explicit:

- Graphify-supported behavior must be distinguished from ImplementAudit heuristics.
- Graphify summaries and graph output are not proof.
- ActiveGraph custody is not correctness proof.
- ImplementAudit custom adapter events are not upstream ActiveGraph built-ins unless explicitly identified as such.
- ActiveGraph policies gate graph object proposals, graph patches, and wrapped behaviors/tools/proposals.
- ActiveGraph does not inherently gate shell commands, git commit, git push, tag, release, publication, or provenance unless those actions are modeled through wrapped ActiveGraph behavior/tool/proposal semantics.
- Object/relation mappings are ImplementAudit-specific or Diligence-style adapter mappings, not upstream ActiveGraph base types.
- Release and provenance claims require separate authorization and evidence.

## Usage examples

```text
/implementaudit < audit.md
/implementaudit implement these findings
/implementaudit --onboard-tools
```

Natural-language requests such as "implement these findings", "act on this audit", "close these items", or "work through this handoff" also invoke the method when the input is a valid audit artifact.

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

Local commit authorization does not imply push authorization. Push authorization does not imply tag, release, publication, or provenance authorization.

If local commits are authorized, commit bodies carry the causal trace: finding, owner/source, root cause when relevant, Andon/Hansei/5 Whys when triggered, countermeasure, changed files, Smoke A/B, boundaries preserved, and deferred follow-up.

If local commits are not authorized, the final report includes a proposed commit message/body instead.

## What this does not do

`/implementaudit` does not:

- make Graphify or ActiveGraph hard dependencies
- silently install tools
- silently run indexing
- silently create ActiveGraph config or event stores
- treat install success as audit proof
- treat Graphify output as correctness proof
- treat ActiveGraph custody as correctness proof
- push, tag, release, publish, or make provenance claims without explicit authorization
- resolve audit-vs-`AGENTS.md` conflicts by agent judgment
- use `AGENTS.md` as a raw evidence dump

## Development / maintenance notes

`IMPLEMENTAUDIT.md` is the owner/source for this repository. Keep this README derived from it.

When the method changes, update README language only after reading the live local `IMPLEMENTAUDIT.md`, including unpushed local commits. Preserve the distinction between:

- upstream-supported behavior
- ImplementAudit custom extension
- repo-local heuristic
- unsupported or uncertain behavior

Detailed evidence belongs in commit bodies, orchestrator/audit ledgers, ActiveGraph custody events when configured, or final reports. Durable anti-repeat rules may belong in repo-local `AGENTS.md` when they would prevent future agents from repeating the same mistake.
