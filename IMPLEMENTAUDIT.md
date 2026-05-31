---
name: implementaudit
description: >
  Implement audit findings from an input report safely and verifiably using
  PDCA, Gemba, Smoke Before Claim, Andon, Hansei, 5 Whys, and Plan Closure.
  Activate when the user invokes /implementaudit, pipes an audit into it,
  or asks to implement findings from a handoff,
  review, checklist, audit report, or implementation plan. Also activate when
  the user says "implement these findings", "act on this audit", "close these
  items", or "work through this handoff". Repo-generic: inspect the actual repo
  first; never assume framework, language, CI, build system, or release
  convention. Does not commit, push, tag, publish, or release unless the input
  explicitly authorizes that action and repo instructions allow it.
---

# /implementaudit

Convert audit findings, handoffs, reviews, or checklists into safe, verified repo changes.

Every finding closes. No orphan items. No unsafe actions. No proof claim without evidence.

Do not stop at "partial," "safe but unchanged," or "next countermeasure needed" while an obvious in-scope next action remains. Continue until every audit item is terminally closed as `done`, `changed`, `blocked`, `deferred`, or `unverified`.

---

## Execution spine (non-skippable gates)

This is not a table of contents. Treat each row as a gate: pass it before moving to the next gate, or STOP/Andon with owner/source, evidence, and the next concrete action.

| Gate | Decision | Halt condition |
|---|---|---|
| 0. Safety read | §0: read repo instructions, safety defaults, authorization gates, and `AGENTS.md` conflict rules. | STOP if the requested action is unsafe, unauthorized, unsupported, or contradicts repo policy without an owner decision. |
| 1. Input gate | §2: confirm the input is a valid audit artifact. | STOP and wait if input is empty, malformed, or not an audit artifact. Restart at Step 2 after corrected input. |
| 2. Pre-flight | §4a, §4b, and §5: detect optional tooling, use Graphify-assisted Gemba when available/fresh/authorized, confirm write access, generator/source ownership, authorization chain, repo constraints, and prior run state. | STOP unless every required pre-flight item passes or the failure is the audit target itself. Missing optional tooling is not a failure. |
| 3. Smoke A | §7: run the baseline before mutation. | Do not mutate until baseline checks are recorded and pre-existing failures are classified as target, unrelated, or unclear. |
| 4. Implement | §8: process P0 -> P1 -> P2, patch owner/source, keep changes atomic, and guard scope creep. | Andon if owner/source is unclear, generated-source policy is unresolved, a dependency blocks the item, or an AGENTS.md conflict needs an owner decision. |
| 5. Smoke B | §9: compare post-change checks against Smoke A. | If any Smoke A passing check now fails, follow the regression protocol before claiming success. |
| 6. Trace | §12-§14: preserve the causal chain in commit body, proposed commit body, audit ledger, ActiveGraph-backed Capability Ledger when configured, and durable `AGENTS.md` rule when warranted. | Do not final until local commit/push/tag/release/publication/provenance boundaries, Capability Ledger or Markdown fallback, and the `AGENTS.md` decision are explicit. |
| 7. Self-check | §16: run the quality bar before the final response. | Fix, revert, defer, block, or mark unverified before final if any required invariant is false. |

---

## Run invariants (must stay true)

These invariants shape the run; they are not just final checks.

- Every patch maps to a ledger item and owner/source.
- Owner/source is patched instead of the nearest symptom.
- Generated artifacts follow generator-first policy unless repo policy explicitly permits direct edits.
- Graphify and ActiveGraph remain optional; absence of either tool is not an error.
- ActiveGraph-backed runs derive Capability Ledger entries from custody events by default; Markdown ledger/final report fallback remains valid when ActiveGraph is absent.
- Local commit, push, tag, release, publication, and provenance remain separate explicit gates.
- No raw diagnostics, local smoke debris, secrets, build artifacts, or unrelated dirty files are staged or committed.
- No proof claim is stronger than its evidence type.
- Graphify output is orientation evidence, not proof; ActiveGraph events are chain-of-custody evidence, not proof by themselves.
- Graphify may orient Gemba when available, fresh, or explicitly authorized, but live files remain the source of truth.
- Smoke A happens before mutation; Smoke B happens after implementation; regressions trigger the regression protocol.
- Domain notation, schema keys, DSL tokens, public API names, paths, release asset names, and contract strings are preserved unless the audit explicitly changes them.
- Any audit-vs-`AGENTS.md` contradiction becomes `OWNER DECISION`, not an agent judgment call.
- `AGENTS.md` receives durable anti-repeat rules only, not raw evidence or transient local state.
- Every ledger item reaches `done`, `changed`, `blocked`, `deferred`, or `unverified` before final.
- If local commit is not authorized, the final report includes a proposed commit message/body.

---

## 0. Non-negotiable safety defaults

Before touching files, inspect repo instructions when present:

- `AGENTS.md`
- `CONTRIBUTING.md`
- `README.md`
- `docs/**`
- CI/workflow files
- existing handoff/audit docs
- package/build/test/release docs

Never do any of the following unless the input explicitly authorizes the action and repo docs allow it:

- push
- tag
- publish
- create or update releases
- delete data
- alter credentials or secrets
- rewrite history
- commit raw diagnostic outputs
- hand-edit generated artifacts when a source generator exists
- claim proof without running the smallest meaningful check

**Explicit authorization** means a direct imperative such as `commit changes`, `push to main`, `push this branch`, `tag vX.Y.Z`, or `update the release assets`. References to CI, deployment, release plans, or implied workflows do not count. Authorization is action-specific: local commit authorization is not push authorization, push authorization is not tag/release/publication authorization, and release authorization is not provenance authorization.

**Provenance** means signing, attestation, SBOM generation, checksum or manifest publication, or any other claim that an artifact, package, release, or deployment has a verifiable origin/integrity chain.

If the repo contains domain notation, schema keys, DSL tokens, public API names, file paths, release asset names, or exact contract strings, preserve them exactly unless the audit explicitly asks to change them. Do not rename, simplify, transliterate, ASCII-normalize, or "clean up" symbolic tokens just to improve prose, layout, or style.

Stop and report if any requested action is unsafe, unsupported, unauthorized, or blocked by repo policy:

```text
STOP:
Denied action:
Reason:
Owner/source:
Smallest passing check or next action:
```

Default stance unless explicitly authorized:

```text
No commit. No push. No tag. No release. No publication.
```

---

## 1. Core operating method

### PDCA — Plan, Do, Check, Act

| Phase | Discipline |
|---|---|
| Plan | Identify finding, owner/source, risk, smallest safe change, and verification command. |
| Do | Patch the owner/source, not the nearest symptom. Keep changes atomic. Avoid broad rewrites. |
| Check | Run the smallest meaningful check, relevant tests/smokes, and inspect generated output where applicable. |
| Act | Standardize if successful. Revise or revert if failed. Update the closure ledger. |

**Broad rewrite threshold:** A patch is broad if it touches more than one logical unit not named in the audit, or if it restructures surrounding code unrelated to the finding. When in doubt, make the narrowest change that closes the finding and log the rest to the scope-creep register.

### Gemba — Real place of work

Inspect the actual artifact where the error or value occurs: source file, generated file, browser page, package, smoke output, checker error, workflow, logs, release asset, prompt file, or skill file. Do not diagnose from summaries when the live artifact exists.

For non-code artifacts (skills, prompts, config files, markdown docs, data files with no test runner): Gemba means reading the artifact directly and identifying structural, logical, or semantic issues. The bash orientation commands below may produce nothing useful; read the file instead.

### Smoke Before Claim

Run the smallest meaningful check before claiming behavior.

Smoke Before Claim is per-claim evidence tagging. Smoke A/B is the broader baseline-vs-post-change comparison used to detect regressions across the implementation run.

```text
Smoke Before Claim:
Command:
Result:
Evidence type: [live runtime | local generated-runtime | package-bound | unit test | integration test | static checker | manual inspection | visual/browser | unverified]
Remaining risk:
```

Never upgrade static evidence into live proof. If a live check cannot run, label the evidence type and remaining risk explicitly.

For prompt/skill/non-executable artifacts: Smoke = trace the artifact against a known representative input, mentally or via a test invocation, and record what it produces.

### Andon — Visible problem signal

When work cannot honestly pass, surface it immediately:

```text
Andon:
Status:
Blocker:
Failing check:
Owner/source:
Next concrete action:
```

Do not hide failure. Do not mark "mostly done."

### Hansei — Structured reflection

After any failure or regression:

```text
Hansei:
Gap:
Cause:
Countermeasure:
Follow-up evidence:
```

### 5 Whys — Root-cause drill

Use 5 Whys carefully: symptom → systemic cause → countermeasure at the cause.

```text
5 Whys:
1. Why did the symptom occur?
2. Why did that condition exist?
3. Why did the system allow it?
4. Why was it not caught earlier?
5. What countermeasure prevents recurrence?
```

**Loop-exit protocol:** If 5 Whys identifies a root cause that is out of scope, requires an architectural change, or requires an OWNER DECISION, do not loop. Log it to the scope-creep register, close the current item as `deferred` with reason, and continue to the next item.

### Plan Closure

At the end, every plan item must be mapped to exactly one terminal status:

- `done`
- `changed`
- `blocked`
- `deferred`
- `unverified`

No item may remain `open`.

---

## 2. Validate input

Confirm the input is a recognizable audit artifact, such as:

- findings report
- handoff
- review checklist
- implementation plan
- explicit `/implementaudit` invocation
- user request to "implement these findings," "act on this audit," "close these items," or "work through this handoff"

If input is empty, malformed, or not an audit artifact:

```text
STOP:
Input is not a valid audit artifact.
Expected: findings report, handoff, checklist, implementation plan, or /implementaudit invocation.
Received:
Next action: request valid input from user.
```

Do not proceed until valid input is confirmed.

If the user supplies corrected input after this STOP, restart at Step 2 with the new input. Do not reuse a partially normalized ledger from malformed input.

---

## 3. Read and normalize input

Extract:

- findings
- blockers
- recommended patches
- verification commands
- release/safety constraints
- deferred items
- owner decisions
- required output format

Classify each finding:

| Class | Criterion |
|---|---|
| `P0` | Blocks the stated goal, breaks an existing passing check, or is a safety violation. |
| `P1` | Directly named in the audit, reduces risk, improves correctness, and is safely achievable now. |
| `P2` | Defensive hardening or nice-to-have not required for the current goal. |
| `OWNER DECISION` | Requires a human call before safe proceeding. |
| `DEFERRED` | Explicitly pushed out by input or owner. |
| `OUT OF SCOPE` | Outside the stated mandate. |

**Dependency note:** If item B cannot safely proceed without item A being closed first, record this in the ledger. If A is blocked, mark B as `deferred` with reason "depends on #A" rather than attempting B independently.

Initialize the implementation ledger. `open` is an initial state, not a terminal status.

| # | Finding | Priority | Owner/source | Risk | Verification | Status | Evidence | Depends on |
|---|---|---:|---|---|---|---|---|---|
| 1 | ... | P0 | ... | ... | `<command>` | open | — | — |

Initialize the scope-creep register.

| # | Issue found | Location | Recommendation |
|---|---|---|---|

Adjacent issues not in the ledger go into the scope-creep register and are not implemented.

**Exception:** If an adjacent issue is required to safely close a current ledger item, promote it into the ledger as a new row with status `changed`, name the owner/source, cite which ledger item requires it, and explain why it is necessary. Do not silently expand scope. If the promoted item itself surfaces a further adjacent issue, log that to the scope-creep register and stop — do not chain promotions.

---

## 4. Gemba inspection

Go to the real place of work. Inspect actual files, not summaries.

**Platform note:** Examples below are bash/Unix. On Windows, adapt using PowerShell, `dir`, `findstr`, `type`, or repo-standard commands.

```bash
# Repo type and root
ls -la && head -40 README.md 2>/dev/null

# Package/build config
find . -maxdepth 2 \( -name "package.json" -o -name "Makefile" \
  -o -name "pyproject.toml" -o -name "Cargo.toml" -o -name "go.mod" \) | head -10

# CI/workflow files
find . -maxdepth 4 \( -path "./.github/workflows/*.yml" \
  -o -name ".gitlab-ci.yml" -o -name "Jenkinsfile" \) | head -10

# Repo instructions and prior audits
find . -maxdepth 2 \( -name "AGENTS.md" -o -name "CONTRIBUTING.md" \
  -o -name "HANDOFF*" -o -name "AUDIT*" \) | head -10

# Current dirty state
git status && git diff --stat HEAD 2>/dev/null

# Detect generated artifacts (heuristic only)
grep -rl "DO NOT EDIT\|generated by\|auto-generated\|this file is generated" \
  --include="*.ts" --include="*.js" --include="*.py" --include="*.go" . 2>/dev/null | head -10
```

**Generated artifact rule:** A file is generated if repo policy says so; if it lives in `dist/`, `build/`, or `generated/`; if it carries a "do not edit" / "generated by" header; or if it is a known codegen output such as `.pb.go`, `.g.dart`, or `*.pb.ts`. Identify its source generator and edit the source, not the artifact.

**Generator-first protocol:** If the source generator encodes the same incorrect value as the generated artifact, fix the generator first, verify the generator, then regenerate the artifact. Do not regenerate before fixing the generator.

If repo policy explicitly permits direct artifact editing, cite that policy in the plan.

**Non-git VCS or no VCS:** If the repo uses a different VCS (SVN, Mercurial, Perforce) or none, adapt all git commands to the appropriate VCS equivalents. For non-VCS targets (zip archives, FTP deployments, CMS content), "rollback" means restoring from a saved backup or cached baseline taken before Step 7.

**Idempotency:** If a prior run exists (check for `HANDOFF.md`, `AUDIT.md`, or a prior ledger), review its closure state. Do not re-implement already-closed items unless a regression or explicit reason re-opens them.

---

## 4a. Optional first-run tooling onboarding

Run this after the safety read and valid input check, and before any optional Graphify-assisted Gemba or ActiveGraph export.

Graphify and ActiveGraph are optional. Absence of either tool is not an error and must not block `/implementaudit`. The default fallback is to detect availability, record the result, print onboarding commands if a tool is missing, and continue with ordinary Gemba, ordinary ledgers, and ordinary final reporting.

Do not install silently. Install only if the invocation explicitly authorizes onboarding/tool install, such as `/implementaudit --onboard-tools`, or the user directly says to install optional tools.

**Platform note:** Examples below are bash/Unix. On Windows, adapt using PowerShell, `where.exe`, `Test-Path`, or repo-standard commands.

### Detection

```bash
# Graphify CLI availability
command -v graphify >/dev/null 2>&1 && graphify --version || echo "GRAPHIFY_ABSENT"

# Graphify output presence
test -f graphify-out/graph.json && echo "GRAPHIFY_GRAPH_PRESENT" || echo "GRAPHIFY_GRAPH_ABSENT"

# Graphify stale-index heuristic: tracked files newer than graph output
if test -f graphify-out/graph.json; then
  git ls-files -z | xargs -0 -r sh -c \
    'for f do [ "$f" -nt graphify-out/graph.json ] && printf "%s\n" "$f"; done' sh | head -20
fi

# ActiveGraph Python package
python -c "import activegraph; print('ACTIVEGRAPH_IMPORTABLE')" 2>/dev/null || echo "ACTIVEGRAPH_ABSENT"

# ActiveGraph CLI availability
command -v activegraph >/dev/null 2>&1 && activegraph --version || echo "ACTIVEGRAPH_CLI_ABSENT"

# ActiveGraph repo configuration heuristic (repo-local only, not an upstream config contract)
find . -maxdepth 3 \( -name "activegraph.toml" -o -path "./.activegraph/*" \) | head -20

# First observed IMPLEMENTAUDIT run heuristic
find . -maxdepth 3 \( -iname "*implementaudit*" -o -name "HANDOFF*.md" -o -name "AUDIT*.md" \) | head -20
```

The `activegraph.toml` / `.activegraph/*` check is a repo-local heuristic only. It is not an upstream ActiveGraph configuration contract. Upstream ActiveGraph configuration may instead be represented through documented store URLs, runbooks, adapter config, or another repo-local convention.

### First-run ledger

| Tool | Status | Action | Authorization | Evidence | Remaining risk |
|---|---|---|---|---|---|
| Graphify | absent/present/stale | skipped/offered/installed/indexed | none/user-approved | command result | graph may be stale |
| ActiveGraph | absent/present/configured | skipped/offered/installed/export-enabled | none/user-approved | command result | event export is not proof |

### Missing-tool behavior

If Graphify or ActiveGraph is missing, continue without optional tooling by default and print the relevant onboarding commands.

Graphify install commands:

```bash
uv tool install graphifyy
graphify install --platform codex
graphify install --project --platform codex
```

ActiveGraph install commands:

```bash
pip install activegraph
activegraph quickstart
```

### Authorization boundaries

Tool installation does not authorize Graphify indexing, ActiveGraph event-store setup, ActiveGraph export, committing generated graph output, local commit, push, tag, release, publication, or provenance claims. Each remains a separate explicit gate.

Graphify indexing remains separately authorized. ActiveGraph export remains separately authorized. Project-scoped install or configuration requires explicit repo-mutation authorization.

### Evidence boundary

Installation confirms tool availability only. It does not prove audit correctness.

Graphify output is orientation evidence, not proof. ActiveGraph events are chain-of-custody evidence, not proof by themselves. Live repo files remain the source of truth when tool output conflicts with reality.

---

## 4b. Graphify-assisted Gemba

When Graphify is available and a graph exists, or when indexing/querying has been explicitly authorized, use Graphify as an optional catalog before choosing owner/source or impact scope.

Graphify is orientation evidence only. It does not decide closure, prove correctness, authorize mutation, replace live-file inspection, override repo instructions, weaken `AGENTS.md`, or hide stale graph risk.

Graphify terrain tagged `INFERRED` or `AMBIGUOUS` requires live-file confirmation before implementation, closure, or proof claims. Treat those tags as orientation signals, not evidence that the relationship is true.

Use Graphify to look for:

- owner/source candidates
- dependency paths
- generated-artifact hints
- impact surfaces
- test/smoke candidates
- scope-creep signals
- stale assumptions
- source/generated output relationships

Example query commands, adapted to the installed CLI or MCP:

```bash
graphify query "<finding subject>"
graphify path "<source>" "<dependent>"
graphify explain "<entity>"
graphify query "generated artifacts"
```

If Graphify is absent, continue with ordinary Gemba. Do not block the run and do not mark absence as a failure.

If graph output is stale, record stale risk. Use it only as weak orientation, or avoid graph use unless refresh/indexing is explicitly authorized.

If Graphify output conflicts with live files, live files win. Record the contradiction as an evidence-boundary caveat and do not make proof claims from graph output.

Record Graphify-assisted Gemba when used:

| Query | Purpose | Result | Evidence boundary | Follow-up |
|---|---|---|---|---|
| owner/source query | identify source candidates | candidates found/none/stale | orientation only | inspect live files |
| dependency path query | identify affected paths | paths found/none/stale | orientation only | verify source and tests |
| generated artifact query | find source/output relation | relation found/none/stale | orientation only | apply generator-first protocol |

If ActiveGraph is configured, Graphify queries/results may be recorded as terrain-context events such as `gemba.graphify.queried`. Capability Ledger entries may include `graphify_terrain_used`, but that field remains terrain context, not proof.

---

## 5. Pre-flight checklist

With targets known from Gemba, confirm all items before mutation. Any failed item triggers STOP unless the audit target itself is the failure.

- [ ] Write access confirmed on all target files.
- [ ] Source generator identified for generated artifacts in scope, or repo policy cited.
- [ ] Generator-first order confirmed: generators that embed the finding are fixed before regeneration.
- [ ] Optional first-run tooling onboarding completed or skipped: Graphify/ActiveGraph availability recorded, missing-tool commands printed when relevant, and no install/index/export/config action taken without explicit authorization.
- [ ] Graphify-assisted Gemba completed or skipped: graph output used only when available/fresh/authorized, stale risk recorded or avoided, and live files retained as source of truth.
- [ ] Local commit, push, tag, release, publication, and provenance authorization status resolved separately: not authorized by default, or explicitly cited from input.
- [ ] Repo safety constraints read and not violated by the plan.
- [ ] Prior run state checked: if a prior ledger/handoff exists, already-closed items are not re-implemented unless a regression or explicit reason re-opens them.
- [ ] Baseline smoke has not yet run; it comes next.

Write access check:

```bash
test -w <target_file> && echo "WRITABLE" || echo "NOT WRITABLE — stop"
```

---

## 6. Create working plan

Before mutation, write the working plan:

```text
Goal:
Top objective:
Owner/source of truth:
Audit items in scope, by ledger #:
Audit items out of scope, by ledger #:
Item dependencies (if any):
Risk:
Verification commands:
Rollback:
  Before commit (git)      -> git restore <file> | git checkout <file> | git stash
  After commit (git)       -> git revert <hash>  (preserves history; preferred)
  Unpushed commit (git)    -> git reset --hard HEAD  (destructive; use with care)
  Generated output         -> rerun source generator (after confirming generator is correct)
  Non-git / no VCS         -> restore from backup or cached baseline taken before Smoke A
```

Use the smallest patch that satisfies the audit.

---

## 7. Baseline smoke: Smoke A before mutation

Run all audit-named verification commands before touching files. This is Smoke A. Subsequent smokes are compared against it.

Smoke A is not a replacement for per-claim Smoke Before Claim entries; it is the run-level baseline that later checks compare against.

If baseline checks are failing, classify each failure before proceeding:

| Classification | Condition | Action |
|---|---|---|
| `target` | The failure is the audit finding itself | Proceed. Record as failing baseline evidence. |
| `unrelated` | The failure predates the audit and is not in scope | Stop unless explicitly authorized to proceed on a broken baseline. |
| `unclear` | Cannot determine | Andon → request owner decision before proceeding. |

Do not silently mix unrelated pre-existing failures with implementation regressions.

```text
Smoke A (baseline, pre-patch):
Commands run:
Results:
Pre-existing failures (classified as target / unrelated / unclear):
```

---

## 8. Implement item by item

Process items in P0 → P1 → P2 order. Skip items whose dependencies are blocked.

For each item:

1. Confirm source owner.
2. Patch owner/source, not nearest symptom.
3. If the fix changes a data type, format, algorithm, or API contract: flag downstream artifacts that encode assumptions about the old value (test expectations, dependent configs, generated outputs, documentation). Check each one and add to the ledger if promotion is warranted per Step 3 rules, or to the scope-creep register if not.
4. Rebuild generated outputs if needed, following generator-first protocol.
5. Run the smallest local check.
6. Update ledger status and evidence.
7. Continue to the next item.

Mid-item blocker protocol: if a blocker is hit mid-patch, restore clean state before reporting.

```bash
git restore <affected_file>
# or: git checkout <affected_file>
# non-git: restore from backup
```

Then use Andon, update the ledger as `blocked`, and continue if other items remain. Never leave files in a broken intermediate state.

Scope-creep guard remains active throughout this step.

---

## 9. Post-implementation smoke: Smoke B

Run the full verification suite after changes are complete. For P0 or high-risk changes, run an interim smoke after each patch set.

Smoke B is the run-level post-change comparison against Smoke A. Keep per-claim evidence labels when making narrower proof claims inside the implementation.

```text
Smoke B (post-patch):
Commands run:
Results:
```

Decision criteria:

| Outcome | Condition | Action |
|---|---|---|
| Resolved + preserved | Finding closed and all Smoke A passing checks still pass | Accept as `done` or `changed`. |
| Preserved only | No regression, but finding not fully closed | Continue if in scope; otherwise close as `blocked`, `deferred`, or `unverified` with reason. |
| Regression | Any Smoke A check that passed now fails | See regression protocol below. |

**Regression protocol:**

1. Identify whether the regression is in the fix itself or in a downstream dependency of the fix (e.g., a test encoding a stale assumption about the old behavior).
2. If the regression is in a downstream dependency: revise the dependency, not the fix. Do not revert the correct fix to restore a wrong baseline.
3. If the regression is in the fix itself: Andon → Hansei → 5 Whys → revert fix → revise → re-smoke.
4. After revision, re-run Smoke B. Do not claim resolution without a clean re-smoke.

Regression signals: fewer tests passing, new lint/type/build errors, unexpected schema/output changes, new runtime errors, expanded security surface, contract or API shape change not authorized by audit.

---

## 10. Validate

Run audit-named checks first. Then run repo-standard checks if discoverable.

At minimum:

```bash
git diff --check
```

Project checks may include unit tests, integration tests, lint, typecheck, build, docs build, package-shape check, smoke artifact check, schema validation, provenance checks, or visual/browser inspection.

Report exact commands and results.

---

## 11. Update handoff or audit doc

Create or update a tracked doc when appropriate. Do not rely on chat context alone.

```text
Goal:
Implemented:
Changed:
Blocked:
Deferred:
Unverified:
Found — not in scope (scope-creep register):
Smoke A (pre-patch baseline, with pre-existing failure classifications):
Smoke B (post-implementation, with regression protocol notes if triggered):
Checks run:
Next action:
```

If a root handoff file is ignored by tooling, mirror important status into a tracked audit/handoff doc.

---

## 12. Local git trace checkpoints only if explicitly authorized

If local commit is not explicitly authorized, do not stage or commit. Preserve the trace in the audit ledger and final report, and include a proposed commit message/body so a maintainer can create the checkpoint later.

If local commits are explicitly authorized for the `/implementaudit` run, use local git commits as durable trace checkpoints. A local commit records what changed, why it changed, what finding caused it, what root cause was identified, what Andon/Hansei/5 Whys occurred, which checks passed or failed, why the fix worked, what was not claimed, and what durable lesson may need to move into `AGENTS.md`.

Keep the gates separate:

- Local commit does not imply push.
- Push does not imply tag, release, upload, publication, or public provenance.
- Tag, release, publication, and provenance remain separate explicit gates.
- Release authorization is not implied by commit authorization or push authorization.
- Provenance claims require repo-defined release/provenance evidence, not merely local git history.

Commit flow when local commit is authorized:

1. Run Smoke B and final validation first.
2. Stage explicit paths only; do not use `git add .`.
3. Verify staged content with `git status --short` and `git diff --cached --stat`.
4. Verify raw diagnostics, local smoke debris, secrets, build artifacts, generated debris, and unrelated dirty files are not staged.
5. Commit only the paths that belong to the finding/fix checkpoint.
6. Do not push unless push is separately and explicitly authorized.

Use a short subject line. Put the trace in the commit body, not in an enormous subject.

Commit body fields may include, when relevant:

- `Finding`
- `Owner/source`
- `Root cause`
- `Andon`, if there was a failure or warning signal
- `Hansei`, if there was a gap, regression, or false-pass
- `5 Whys`, when used
- `Countermeasure`
- `Files changed`
- `Smoke A / baseline result`
- `Smoke B / post-change result`
- `Regression protocol`, if triggered
- `Boundaries preserved`
- `Follow-up / deferred items`

Use the abbreviated commit body only for ordinary small fixes: a narrow, non-regression fix with no failed/warning signal, no proof-scope gap, no release/provenance boundary, no repeated agent mistake, and no new or changed public contract. The abbreviated body must still state:

- `Finding`
- `Countermeasure`
- `Smoke B / checks run`
- `Boundaries preserved`

Require the fuller trace body, including Andon/Hansei/5 Whys detail, when the commit closes a failure, regression, false-pass, proof-scope gap, release-boundary issue, provenance-boundary issue, generated-artifact mistake, or repeated agent mistake.

Example:

```bash
git commit -m "fix: enforce hard-output scope floor" -m "
Finding:
- The hard-output path accepted audit output below the required scope floor.

Root cause:
- The checker validated presence of output but not the minimum auditable boundary.

Countermeasure:
- Enforced the scope floor in the owner checker and updated the focused fixture.

Smoke A:
- npm test -- hard-output-scope failed before the patch.

Smoke B:
- npm test -- hard-output-scope passed after the patch.

Boundaries:
- No push, no tag, no release.
"
```

For non-git VCS: adapt staging and commit steps to the appropriate VCS commands. For no VCS: record the set of changed files and their checksums as the local trace record, and still distinguish it from push, tag, release, publication, and provenance.

---

## 12a. ActiveGraph-backed Capability Ledger

When ActiveGraph is available and configured for the repo, `/implementaudit` should emit event-backed Capability Ledger entries as the natural default custody output. Do not require a separate "generate CV" mode for ordinary runs.

ActiveGraph remains optional. If ActiveGraph is absent or unconfigured, continue with the ordinary Markdown ledger, final report, and local git trace discipline. Markdown fallback is first-class and is not a degraded or blocked run.

Capability Ledger is an ImplementAudit-derived record. ActiveGraph provides the event custody substrate when configured; ImplementAudit derives capability entries from recorded gate passages, authorization decisions, smokes, Andons, regressions, ledger closures, boundary records, and evidence. Capability entries are not invented after the run, and ActiveGraph does not ship an Officer CV feature by default.

Graphify may enrich entries with terrain context only. ActiveGraph preserves custody only. ImplementAudit remains the competence standard. Capability claims must stay narrow and evidence-bound: this officer closed this class of finding, in this repo area, with these checks, under these boundaries.

Capability entries may include:

| Field | Meaning |
|---|---|
| `run_id` | Stable run identifier |
| `repo` | Repo identity/path/remote |
| `finding_class` | P0/P1/P2/OWNER DECISION/DEFERRED/OUT OF SCOPE |
| `owner_source` | File/module/artifact patched or inspected |
| `countermeasure` | What changed or was recommended |
| `graphify_terrain_used` | Graphify terrain context, if available |
| `activegraph_events` | Custody event ids, if available |
| `authorization_gates_respected` | Commit/push/tag/release/provenance/tooling gates |
| `smoke_a` | Baseline command/result/evidence type |
| `smoke_b` | Post-change command/result/evidence type |
| `regression_andon_hansei` | Any warning/failure/recovery trail |
| `final_status` | done/changed/blocked/deferred/unverified |
| `remaining_risk` | Explicit caveats |

ActiveGraph-backed runs may emit these ImplementAudit-defined custom pack/adapter event names unless a name is explicitly identified as an upstream ActiveGraph built-in. Do not imply ActiveGraph ships these ImplementAudit event names by default.

```text
implementaudit.run.opened
audit.input.normalized
gemba.graphify.queried
owner_source.candidate_identified
smoke.baseline.recorded
finding.claim.created
countermeasure.proposed
mutation.authorization.requested
mutation.authorization.granted
mutation.authorization.denied
repo.patch.applied
smoke.post.recorded
regression.detected
andon.triggered
hansei.recorded
ledger.item.closed
capability.entry.derived
implementaudit.run.finalized
```

If an ActiveGraph graph-object patch lifecycle is being recorded, upstream `patch.applied` remains the ActiveGraph built-in. For repo file patching, use a custom event such as `repo.patch.applied` so repo mutations are not confused with ActiveGraph graph-object patch events.

ActiveGraph policies gate graph object proposals, graph patches, and wrapped behaviors/tools/proposals. ActiveGraph does not inherently gate shell commands, git commit, git push, tag, release, publication, or provenance actions unless those actions are represented through wrapped ActiveGraph behavior/tool/proposal semantics. ImplementAudit's explicit authorization gates still apply regardless of any ActiveGraph policy record.

Object mapping is an ImplementAudit-specific ontology or adapter mapping. It is not a claim that ActiveGraph itself ships base object types; ActiveGraph object and relation vocabularies are developer-defined. Diligence-style names apply only when a compatible pack defines them.

| ImplementAudit concept | ImplementAudit / Diligence-style object |
|---|---|
| finding | claim, when a compatible pack defines it |
| smoke result | evidence, when a compatible pack defines it |
| countermeasure | mitigation/action, as an ImplementAudit-specific adapter object |
| blocker | risk, when a compatible pack defines it |
| final report | memo, when a compatible pack defines it |
| capability entry | derived summary object, as an ImplementAudit-specific adapter object |

Relations are likewise ImplementAudit-specific or Diligence-style adapter relations, not upstream base ActiveGraph relations:

```text
supports
contradicts
references
derived_from
mitigates
```

Evidence boundaries:

- Do not claim general competence from one run.
- Do not claim proof from Graphify summaries.
- Do not claim correctness from ActiveGraph custody alone.
- Do not claim authorization beyond recorded gates.
- Do not claim release/provenance unless separately authorized and evidenced.

---

## 13. Commit granularity rules

Prefer one logical finding/fix per commit. The commit should let a future maintainer map the patch to a ledger item, root cause, countermeasure, and verification result without reconstructing the whole run from chat context.

Do not squash unrelated findings into one vague commit. Do not split one atomic fix across many commits unless the repo's workflow calls for that.

Separate source, checker, runtime, documentation, release, and provenance lanes when they have different proof boundaries. If a source fix and a release/provenance update require different evidence gates, keep their commits and claims separate.

Keep generated artifacts tied to the source/generator change that produced them. If generated artifacts are committed, cite the generator command and the source change in the commit body.

Never commit raw diagnostic outputs, local smoke debris, secrets, build artifacts, unrelated dirty files, or files changed outside the authorized audit scope.

Before each authorized commit, inspect:

```bash
git status --short
git diff --cached --stat
git diff --cached --check
```

---

## 14. AGENTS.md standardization discipline

Update repo-local `AGENTS.md` only when an `/implementaudit` finding reveals a durable anti-repeat rule that would prevent future agents from making the same mistake. Do not update `AGENTS.md` on every commit, and do not use it as an evidence dump.

Good `AGENTS.md` content:

- proof/evidence boundaries
- release/provenance boundaries
- known harness failure modes
- generated-artifact rules
- repo-specific Andon patterns
- retained proof or smoke promotion rules
- checker/prose/visual proof distinctions
- pointers to canonical ledgers, manifests, or runbooks

Bad `AGENTS.md` content:

- raw smoke logs
- long hash tables
- transient dirty-worktree notes
- one-off local failures
- local-only release claims
- evidence that belongs in an audit ledger, manifest, release log, or commit body

Use this split:

```text
Commit body / orchestrator / audit ledger = detailed evidence.
AGENTS.md = durable anti-repeat rule.
Release notes = only public release claims after release gate.
```

When deciding whether to update `AGENTS.md`, ask:

- Is the lesson repo-specific rather than generic agent advice?
- Would the rule have prevented this finding or false-pass?
- Is it stable enough to guide future work after this run?
- Does it avoid raw logs, private diagnostics, release claims, and transient local state?
- Does it point to the canonical ledger, manifest, or runbook if details are needed?

If yes, add the smallest durable rule to the nearest applicable `AGENTS.md` and cite the finding in the ledger/final report. If no, leave `AGENTS.md` unchanged and state why in the final report.

Never weaken repo-local `AGENTS.md` safety rules while implementing an audit. If an existing `AGENTS.md` rule appears wrong or obsolete, treat that as an owner decision unless the audit explicitly authorizes the update and the repo evidence supports it.

If an audit finding directly contradicts an existing `AGENTS.md` rule, treat the conflict as `OWNER DECISION`. Andon immediately, quote the conflicting rule and finding, do not implement the contradictory change, and ask for an explicit owner decision.

---

## 15. Final response format

```md
# /implementaudit Result

## Verdict
<!-- Choose exactly one:
IMPLEMENTED AND VERIFIED        all P0+P1 done/changed; Smoke B checks pass; no unresolved blockers
IMPLEMENTED WITH DEFERRED       all P0 done; some P1/P2 deferred by design; Smoke B passes
PARTIAL; BLOCKERS REMAIN        at least one P0/P1 blocked/unverified; Smoke B partial or skipped
REGRESSION FOUND                any Smoke A passing check fails after patching
BLOCKED                         cannot safely proceed — all P0s blocked, or unsafe/unauthorized entry condition
-->

## Goal

## Input basis

## Findings ledger
| # | Finding | Priority | Action | Status | Evidence | Depends on | Follow-up |
|---|---|---:|---|---|---|---|---|

## Scope-creep register (found — not in scope)
| # | Issue | Location | Recommendation |
|---|---|---|---|
<!-- State "None found" explicitly if empty. -->

## Changes made

## Smoke A (baseline — pre-patch)
| Check | Command | Result | Evidence type | Classification (target/unrelated/unclear) |
|---|---|---|---|---|

## Smoke B (post-implementation)
| Check | Command | Result | Evidence type | Δ vs Smoke A | Remaining risk |
|---|---|---|---|---|---|

## Regression protocol triggered
<!-- Include only if a regression was detected during Smoke B.
State whether the regression was in the fix itself or a downstream dependency,
and which branch of the regression protocol was followed. -->

## Andon / Hansei / 5 Whys
<!-- Include only if failures or blockers occurred. -->

## Plan closure
| # | Item | Status | Evidence | Follow-up |
|---|---|---|---|---|

## Files changed

## Commands run

## Graphify-assisted Gemba
<!-- State:
- whether Graphify was available
- whether Graphify-assisted Gemba was used
- whether graph output was fresh, stale, absent, or avoided
- whether ordinary Gemba fallback was used
- any Graphify/live-file contradiction caveats
-->

## Local git trace
<!-- State:
- whether a local commit was performed
- commit hash, or "none"
- whether push was performed
- whether tag/release/publication/provenance was performed
- proposed commit message/body if commit was not authorized
-->

## Capability Ledger
<!-- State:
- whether ActiveGraph was configured
- whether Capability Ledger entries were derived
- whether Markdown fallback was used
- whether claims are upstream-supported behavior, ImplementAudit custom extension, repo-local heuristic, or unsupported/uncertain behavior
- what evidence boundaries apply
- that no broad competence claim is made from one run
-->

## AGENTS.md standardization
<!-- State:
- whether AGENTS.md was updated
- why it was or was not updated
- durable rule added, if any
- where detailed evidence lives instead, if not AGENTS.md
-->

## Remaining caveats
<!-- Items the implementer could not verify, risks not eliminated,
owner decisions deferred, or conditions that could invalidate the verdict. -->
```

---

## 16. Quality bar self-check

Run this internally before the final response. Any failing item must be fixed or marked `unverified` with reason.

- [ ] Every patch connects to a ledger item by number.
- [ ] Owner/source was patched, not nearest symptom.
- [ ] No broad rewrites outside audit scope (threshold: changes limited to the logical unit named in the finding).
- [ ] Meaningful check/evidence recorded for every changed item.
- [ ] Every ledger item has a terminal status; zero `open` items remain.
- [ ] Deferred items have explicit reasons.
- [ ] Items with dependencies: blocked dependencies caused dependents to be deferred, not attempted.
- [ ] Format/algorithm/contract-changing fixes: downstream assumptions (test expectations, dependent configs, generated outputs) were identified and handled.
- [ ] Generator-first protocol observed for generated artifacts.
- [ ] Scope-creep register is populated or says "None found."
- [ ] Promotion chains stopped at one level; no cascading scope expansions.
- [ ] Scope-creep loop-exit followed for 5 Whys cycles that hit out-of-scope root causes.
- [ ] Smoke A recorded before mutation, with pre-existing failure classifications.
- [ ] Smoke B recorded after implementation.
- [ ] Regression protocol branch identified and followed if triggered.
- [ ] Broken baseline failures classified as target / unrelated / unclear.
- [ ] Exact notation/API/schema/contract strings preserved unless explicitly changed by audit.
- [ ] Verdict chosen by rubric, not intuition.
- [ ] Provenance claims, if any, are backed by signing/attestation/SBOM/checksum/manifest evidence and explicit authorization.
- [ ] Local commit, push, tag, release, publication, and provenance stance stated explicitly.
- [ ] Capability claims do not exceed evidence.
- [ ] Graphify terrain context is not treated as proof.
- [ ] Graphify absence did not block the run.
- [ ] Stale graph output was recorded or avoided.
- [ ] Graphify/live-file contradictions were resolved in favor of live files.
- [ ] No proof claim was made from graph output.
- [ ] Graphify terrain context, if used, remained orientation evidence only.
- [ ] Refresh/indexing was not performed without explicit authorization.
- [ ] ActiveGraph custody is not treated as correctness proof.
- [ ] Authorization claims do not exceed recorded gates.
- [ ] Upstream-supported behavior, ImplementAudit custom extension, repo-local heuristic, and unsupported/uncertain behavior are distinguished in Graphify/ActiveGraph integration claims.
- [ ] ActiveGraph policy, Capability Ledger, and object/relation claims do not exceed upstream support plus recorded evidence.
- [ ] Markdown fallback remains valid when ActiveGraph is absent.
- [ ] No release/provenance capability is claimed without separate authorization and evidence.
- [ ] Proposed commit message/body included when local commit was not authorized.
- [ ] Authorized commit bodies include finding, countermeasure, checks run, and boundaries preserved.
- [ ] Full Andon/Hansei/5 Whys detail included when closing a failure, regression, false-pass, proof-scope gap, release-boundary issue, or repeated agent mistake.
- [ ] Commit granularity maps each commit to one logical finding/fix unless repo workflow requires otherwise.
- [ ] `AGENTS.md` update decision recorded, including why it was or was not appropriate.
- [ ] Any `AGENTS.md` update contains durable anti-repeat rules, not raw evidence or transient local state.
- [ ] Any audit-vs-`AGENTS.md` contradiction was treated as `OWNER DECISION`, not silently resolved by the agent.
- [ ] Repo left reviewable and non-broken.
