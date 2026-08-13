# Phase Design

Use phases when a supplied audit or synthesized goal is too large, risky, or
dependent to close as one atomic implementation pass. Execution continues
phase-by-phase until terminal audit closure (`AUDIT_COMPLETE`) or an explicit
audited handoff (`AUDIT_HANDOFF`); the run does not stop at a partial phase
boundary unless the handoff is explicit and recorded.

## Native integration support reference

Phase design supports native audit-object integration by preserving read-only audit-object
closure boundaries, repo-content-as-data security handling,
branch/diff classification, execute/review isolation, and reconciliation inside the run root. The primary
behavioral contracts live in `audit-category-matrix.md` and
`plan-lifecycle.md`; `terminology-integration.md` supplies only route/field/checker
terms that strengthen those native contracts. Phases carry those contracts into
executable specs.

## Phase rules

- Each phase must close one coherent slice of audit risk.
- Each phase mutates or verifies against the same `tdqyq-audit-object` unless an
  owner decision explicitly splits the work into a new audit object.
- Release-affecting or package-boundary phases must first update the audit
  object with the finding and allowed scope, then use `ydqyq-audit-action`
  operations to implement against that object, then verify the object's terminal
  state.
- Each phase needs an owner/source, acceptance criteria, Smoke A, Smoke B, and
  a rollback or deferral path.
- If an external term is used, each phase needs its native parent, runtime
  phase, route or lens, owner/source, evidence boundary, Andon trigger,
  fixture/checker or justified non-mechanical boundary, and final-audit check.
- Stage 4 derives the phase count from dependencies, risk, and evidence shape;
  do not merge unrelated work to fit an artificial count.
- Stage 5 writes a namespaced run root under
  `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/` when phase planning is selected:
  `ROADMAP.md`, `STATE.md`, `THINKING.md`, `PROTOCOL.md`, `context.md`,
  `tools.md`, `sidecars.md`, `applied-context.md` or
  `applied-memories.md`, `repo-map.md` for brownfield work, and one
  `phases/phase-N.md` file per phase.
- Final audit and cleanliness checks use complete working-tree comparison
  against the phase baseline when available.
- `P0` work precedes `P1`; `P1` precedes `P2` unless a dependency demands a
  different order.
- Generated artifacts follow generator-first policy.
- Scope creep is logged instead of silently absorbed.
- A blocked dependency defers dependents; it does not license guesswork.
- There is no artificial phase-count cap. Use as many phases as evidence and
  rollback safety require.
- Namespaced planning artifacts prevent run artifact clobbering. They do not
  make simultaneous source edits safe; use separate git worktrees for true
  parallel implementation, nor do they make source edits safe while a
  verification is reading the same tree; see the verification-window rule in
  `templates/PROTOCOL.md`.

## Owner/source discipline

Patch the place that owns the behavior. A failing rendered doc, generated file,
or downstream checklist may identify the symptom, but the owner/source is the
canonical file, generator, manifest, policy, or runbook that controls it.

## Broad Rewrite Threshold

A broad rewrite is any patch that touches more than one logical unit not named
in the audit, restructures surrounding code or docs unrelated to the finding,
changes public contract shape, migrates layout, deletes legacy behavior, or
mixes source, checker, runtime, docs, package, and release/provenance lanes
without separate evidence boundaries.

Rule phrase: more than one logical unit not named in the audit.

### Re-spec completeness

The Broad Rewrite Threshold limits what a patch may touch; a named constant,
range, identifier scheme, or path change has the reciprocal risk of reaching
too few carriers. Before propagation, record `<run-root>/respec-impact-set.md`.
Use the two-method census in `repo-state-comparison.md`: preserve separate
literal and stem/dirname outputs and counts, deduplicate them, then disposition
every repo, generated, run-root, continuity, external, and distribution
carrier. Enumeration does not grant mutation authority. Replacing a file also
records the validator- and harness-enforced invariants carried forward.

Owner decision is required before a broad rewrite unless the audit explicitly
authorizes that scope. Prefer a strangler/mixed route when new behavior must
wrap or replace old behavior: preserve the legacy validation path, add the new
route behind a clear boundary, prove Smoke B, then retire the old path only
when evidence supports it. Split phases when rollback, package boundary,
generated artifacts, or owner/source evidence differ. Reject scope creep when
the broader work is not necessary to close the current audit item.

## Phase closure markers

Every executing phase must emit:

```text
IMPLEMENTAUDIT_PHASE_START
IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION
IMPLEMENTAUDIT_PHASE_DONE
```

Andon escalation uses:

```text
ANDON_PROBE
ANDON_ESCALATE
ANDON_HANDOFF
```

Final audit uses:

```text
AUDIT_START
AUDIT_VERIFY
AUDIT_GAPS
AUDIT_COMPLETE
IMPLEMENTAUDIT_RUN_COMPLETE
```

`AUDIT_COMPLETE` means the audit object reached terminal verified closure, not
merely that an auditing operation was attempted. `IMPLEMENTAUDIT_RUN_COMPLETE`
may appear only after `AUDIT_COMPLETE`.
`AUDIT_HANDOFF` is a handoff path only when gaps, blockers, or handoff-required caveats remain; do not print it with `IMPLEMENTAUDIT_RUN_COMPLETE`.

Use `"${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/repo-state.sh` for deliverable and added-line checks when a
baseline is available. If the baseline is missing or invalid, mark the evidence
as weaker rather than claiming full release proof.

## Phase shape requirements

These rules apply to any plan that covers a full product, feature, or
operational-hardening objective. Single-surface or hotfix changes (one file,
one checker, one config tweak) may bypass them when the final audit documents
the decision.

**Rule P4-1 — Hardening phase required for full plans.**
Any plan that implements a new feature, migration, or multi-surface change must
include a final hardening phase (or operational-parity phase) unless the final
audit explicitly explains why none is needed and what covers each hardening
concern (cleanliness, error handling, fallback, identity hygiene, observability).
Absence without documentation is a gap, not a savings.

**Rule P4-2 — Rendered-consumer evidence requirement.**
For material representation-dependent output, require rendered-consumer
evidence and preserve governed detail; source/unit green cannot close.
Ordinary prose stays cheap (public/release: R29 in `audit-playbook.md`).

**Rule P4-3 — Brownfield safety-net before risky mutation.**
Before any risky brownfield mutation — schema migration, public API change,
deletion of actively-used code, filesystem restructuring — a characterization
phase must run first. The characterization phase captures: current behavior
snapshot, coverage baseline, known-failing test catalog, and rollback proof
(`git stash pop` or `git checkout HEAD -- <paths>` tested dry). Only after that
baseline is recorded may the mutation phase proceed.

**Rule P4-4 — Package and release phases must be separate.**
Phases that *build* artifacts (compile, zip, sign) must not be merged with
phases that *publish* them (push to registry, create GitHub release, deploy).
Each has a distinct evidence boundary:
- Package evidence: locally-produced file + checksum
- Release evidence: live-registry confirmation or live-URL response
Merging these hides whether the release step actually ran.

**Rule P4-5 — Provenance boundary crossing requires fresh Smoke Before Claim.**
When work crosses a provenance boundary (local → package, package → release,
release → deployment), the receiving phase must run its own Smoke Before Claim.
It may not inherit the prior phase's evidence as proof of the new boundary.
Each boundary adds a "Remaining risk" entry if the live check is blocked.

**Rule P4-6 — Hardening phase scope restriction.**
A hardening phase must address operational concerns: cleanliness, identity
hygiene, error handling, fallback paths, monitoring hooks, or
operational-parity gaps. It must not introduce new features. If new feature
work is discovered during hardening, log it as scope creep and open a follow-up
finding. Merging feature work into a hardening phase breaks the risk boundary.

**Rule P4-7 — Skip documentation.**
Any plan that omits one of the above phase categories (hardening, safety-net,
visual polish, package/release split) must document the omission in the final
audit ledger with: category omitted, reason, and what alternative coverage
(or deliberate owner decision) justifies the skip. Undocumented omissions are
treated as unverified gaps.

**Rule P4-8 — Polish & Harden phase (optional terminal phase shape).**
A "Polish & Harden" phase is a native optional terminal phase shape in
IMPLEMENTAUDIT. It is default-recommended for:
- full plans covering a new feature, migration, or multi-surface change
- any run that produces public docs, UI, or generated artifacts
- package-boundary or release-adjacent work
- high-risk runs with many acceptance criteria

Polish & Harden phases must:
- address operational concerns only: cleanliness, generated artifact freshness,
  stale docs, dead/debug debris, UX/accessibility where relevant, proof-boundary
  wording, identity hygiene
- not introduce new feature scope (new features discovered during this phase are
  logged as scope creep and deferred)
- verify that no extra command branding, slash-command variant, or marker
  appears in tracked surfaces
- run all smoke checks and mandatory commands from earlier phases

Skippable with explicit rationale in the final audit ledger documenting: what
was skipped, why, and what alternative coverage (or owner decision) justifies
the skip. Undocumented omission is treated as a gap per Rule P4-7.

Use `Type: polish-harden` in the `IMPLEMENTAUDIT_PHASE_START` block of a phase
spec to indicate this phase shape (see `references/goal-format.md`).

**Rule P4-9 — Terminology cannot be orphaned.**
External method terms may appear only when attached to a native parent, phase,
route or lens, evidence boundary, Andon condition, and fixture/checker or
explicit non-mechanical boundary. Existing references own their concepts:
Lean owns A3/Poka-yoke/Standard Work/Jidoka/Andon, routing owns DMAIC/DMADV,
Plan Closure owns sustainment, and final audit owns proof. Orphan terms,
glossary-only lists, generic "apply SOLID" advice, numeric RPN theater, and
separate term lanes are phase-design defects and trigger Andon.

**Rule P4-10 — Executor reconstructibility (#50).**
A phase spec is an executor-facing artifact: a fresh, weaker-context executor
must be able to reconstruct the intended change from disk alone. Newly
authored specs carry an ordered `## Implementation steps` section in which
each step names its exact target — file path, plus symbol when symbol
precision is material (a path alone that leaves plausible wrong-but-compiling
candidates is a defect; counter-example:
`fixtures/phase-design/negative-paths-without-symbols.md`, source repo only) —
states the change precisely, and carries its own verify command with expected
success shape. Specs also carry `## Scope boundaries` with an explicit
`Out of scope:` line and plan-specific `## STOP conditions` tied to this
phase's actual risks; boilerplate STOPs fail validation. Step granularity
stays proportional to dependency, risk, and executor needs — a single-owner
hotfix keeps one step; structural completeness never substitutes for
operational specificity. The read-only handoff lane
(`templates/read-only-plan.md`) and the executing phase bar align on this
requirement where their contexts overlap. `validate-phase.sh` enforces the
mechanical parts; cold review owns materiality judgments.

**Rule P4-11 — Scarce-resource launch rehearsal (#84).**
Before a scarce or irreversible resource is spent, rehearse the exact production
wrapper, argv, environment-key names, transport, and terminal path with the
producer stubbed and zero metered calls; a strict receipt/hash binds them.
Environment values are never captured or inherited.
`IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB` gives the wrapper only a checker-owned
mediator bridge, never producer/proof/terminal; its zero substitute exit lets
the checker publish the terminal. Interposed stubs yield `PASS_WITH_SCOPE_GAP`
and `Residual risk:` names each. A second apparatus remains a cold review
judgment. Failure blocks launch: manual repair and re-run only; no automatic
retry may consume the resource.

**Rule P4-12 — Paired controls on free-text acceptance.**
Any acceptance criterion that matches free text ships with two named controls
recorded beside it: one legitimate paraphrase that must PASS, and one
polarity-inverted restatement that must FAIL. Both are evaluated by the
predicate under test. A predicate that fails either control is defective at
authoring time and is replaced, not widened.

**Rule P4-13 — Prompt independence.**
Scored evidence must not be derivable from the instruction that requested it.
Declare `forbidden_instruction_phrases` alongside the scored property; a scored
answer string appearing verbatim in the stimulus is a fixture defect, not a
passing result. This generalizes the candidate Matrix
`matrix_instruction_contract.forbidden_mission_phrases` control.

**Rule P4-14 — Instrument parity.**
A verdict produced by any path other than the one that will adjudicate the
terminal claim requires a parity witness: one canned input, both paths, and an
identical verdict, recorded before any verdict from the secondary path may be
cited in a causal report or drive a repair. Without the witness the secondary
path is diagnostics only.

**Rule P4-15 — Instrument liveness.**
Any command that can emit a negative verdict includes a positive control that
fails loudly if the instrument is broken, such as hashing a known-good member
first and asserting a non-null actual value. A verdict of "all N failed" with
missing or null actuals is an Andon row — class `evidence-mismatch`,
`Blocker: instrument-suspect` — not a finding.

**Rule P4-16: Post-failure evaluator mutation (#164).**
Activate only when candidate `C` fails evaluator `E` and `E` or another
judgement surface for that claim then changes. Product repair with unchanged
`E`, unrelated tests, and pre-candidate red-first authoring remain ordinary.
Reuse the finding/repair row; retain the failure; classify `PRODUCT_DEFECT`,
`EVALUATOR_DEFECT`, `COUPLED_CHANGE`, or `UNRESOLVED`; and record owner/consumer,
product/evaluator/stimulus/population/contract deltas, independent contract
evidence, proof level, population before/after, held-out
positive/negative/boundary/adjacent results, residual, rollback, and stop or
reclassification. Changed evaluators need the old/new product × old/new
evaluator matrix or an authoritative independent instrument; unisolated effects
remain `UNRESOLVED` or owner-decided.

Evaluator repair may PASS only when authoritative property evidence disproves
the old evaluator, retains its witness, rejects a known bad where feasible, and
held-outs discriminate. Changed contracts retain history and state effective
boundary plus migration/population effects. Representation preserves property
equivalence and held-outs. `STIMULUS`, prompt, mock, and secondary-instrument
changes still require independence, parity, liveness, and proof level; prompt
records separate before/after missions, answers, forbidden phrases, distractors,
and held-outs without exposing answers/distractors. Easing assertions, goldens,
answers, tolerances, denominators, populations, bypasses, skips, mocks, or prompts
does not prove an unchanged candidate. Neither literal retention nor a complete
form defeats a lost property or failing held-out negative. Stop after owner,
repair class, original/held-out discrimination, and coupled residual resolve;
absorb the evidence and retire the row—no permanent evaluator registry/worksheet.

**Rule P4-17 — Triggered state-synthesis acceptance.**
For material currentness, receiver, evaluator, proof, consequence, or recovery
risk, record only decision-changing fields: decision/consumer, required function
(not health proxy), current authority/state, evaluator fitness, evidence limits,
independent basis where self-confirmation matters, and recovery/reopen. Keep
conformance, translation, correspondence/environment, tool/result class, and
replay/currentness distinct; one green leg promotes no other. Counts of
reviewers, replicas, runs, or scores are not independence. One authoritative
deterministic discriminator keeps a small reversible task on
inspect → act → verify → done. Use existing surfaces, not modes, worksheets, or
another audit object.

The same row's `CANDIDATE_CONTROLLED_VALIDATION_POLICY` surface activates only
when candidate semantics intersect validation authority judging that candidate;
path/name/support changes alone and product-only work stay ordinary.

Classify `PRODUCT_ONLY`, `POLICY_STRENGTHENING`, `AUTHORISED_POLICY_CHANGE`,
`CANDIDATE_CONTROLLED_POLICY_WEAKENING`, `NEW_POLICY_NO_BASELINE_EQUIVALENT`, or
`COUPLED_OR_UNRESOLVED` without replacing product/evaluator class. Candidate
deletion, skip, config, narrowing, bypass, registry removal, or unreachable owner
cannot self-authenticate green. Strengthening supplements the required baseline;
authorised repair retains witness, contract, and four held-outs; genuinely new
policy also needs external owner authority and independent discrimination.

Moved validation owners remain normally discoverable; otherwise FAIL unless
authoritative migration proves route and equivalent-or-stronger property (R30
owns reachability). In R35 record full candidate/parent identities, exact changed
versus invoked owners, independent owner/contract/effective boundary and distinct
authority identity, retained witness in the complete evidence population,
classification, four baseline/candidate verdicts, discovery/migration, residual
coupling, rollback/reclassification. Derive—not assert with bare Booleans—
activation, authority, retention, and equivalence. Add no universal ledger,
test-path trigger, model call, helper, marker, or parallel lifecycle.

---

## Phase shape examples

See `fixtures/phase-design/` in the IMPLEMENTAUDIT source repo (repo-side;
not shipped in the installed package) for concrete multi-phase plan outlines:

| Fixture | Shape | Phases |
|---------|-------|--------|
| `simple-greenfield.md` | New isolated feature, no UI, no release | 3 |
| `brownfield-mutation.md` | Risky mutation of existing code | 4 |
| `ui-feature.md` | Feature with visible user output | 4 |
| `package-release.md` | Artifact build + registry publish | 4 |
| `full-hardening-run.md` | Operational parity / multi-gap hardening | 5 |

---

## Stage 6 self-critique

Before handoff or mutation through a generated phase plan, print
`Self-critique:` and check at least:

- falsifiable acceptance criteria
- phase atomicity
- weakest dependency
- owner/source clarity
- rollback/deferral path
- mandatory checks and evidence type
- generated-artifact ownership
- optional sidecar boundaries
- completion markers and final-audit path

Patch the phase artifacts before proceeding when the critique finds a gap.
Show the owner a concrete review menu before Stage 7: Start now; Adjust
assumption; Tweak a phase; Restructure phases; Abort / handoff. Do not print the
ready-to-paste handoff until Start now is explicitly selected.

## Stage 6.ii pre-flight

Deduplicate mandatory commands across phase specs and run the safe baseline set
once before Stage 7 handoff or phase-plan mutation. Print `PREFLIGHT_GREEN` or
`PREFLIGHT_RED`. Red pre-flight must classify failures as target, unrelated, or
unclear; unrelated or unclear failures require Andon or OWNER DECISION. Failed,
timed-out, hung, or substituted commands must be recorded as Andons before any
rerun/substitute is used as evidence.
