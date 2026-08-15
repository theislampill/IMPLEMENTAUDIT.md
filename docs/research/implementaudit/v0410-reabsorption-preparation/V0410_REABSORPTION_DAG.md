# V0.4.1 Current-Capability Reabsorption DAG

STATUS=`PREPARATION_ONLY`

BASELINE_RELEASE=`DEFER_TO_V0410_BASELINE`

PROPERTY_DENOMINATOR=`658`

RXX_ID_ALLOCATION=`PROHIBITED_DURING_PREPARATION`

This graph becomes executable only after exact public v0.4.0.0 readback. It
describes evidence and decision dependencies, not a static backlog and not a
promise that every node will produce source work or an RXX.

## Node contract

Every node records:

```text
NODE_ID
OBJECTIVE
CONSUMES
PRODUCES
READ_OWNER
WRITE_OWNER
DEPENDENCIES
ACCEPTANCE
FAILURE_CONTAINMENT
RECOMPUTE_TRIGGER
```

The controller derives `DONE`, `ACTIVE`, `READY` and `BLOCKED` from completed
evidence and dependencies. A prose plan does not establish READY.

## Dependency graph

```text
A00 PUBLIC_V0400_READBACK_GATE
  |
  +--> A01 EXACT_BASELINE_IDENTITY
  |      |
  |      +--> A04 SOURCE_PACKAGE_HOST_CENSUS --------+
  |      +--> A05 RELEASE_EVIDENCE_CENSUS -----------+
  |      +--> A06 RXX_LIVE_GENEALOGY_CENSUS ---------+
  |      +--> A07 CURRENT_RUNTIME_OWNER_CENSUS ------+
  |
  +--> A02 RETAINED_CORPUS_REVERIFY -----------------+
  +--> A03 HISTORICAL_658_BASELINE_REVERIFY ---------+
                                                       |
       A02 + A03 + A04 + A05 + A06 + A07              |
                         |                             |
                         v                             |
               B00 RECONCILIATION_INPUT_JOIN <--------+
                         |
           +-------------+--------------+
           |                            |
           v                            v
 B01 PROPERTY_FAMILY_PARTITION   B02 RXX_REVERSE_INDEX
           |                            |
           +-------------+--------------+
                         |
                         v
                 B03 658_ROW_CURRENT_CENSUS
                         |
           +-------------+--------------+
           |                            |
           v                            v
 C01 REJECTION_REOPEN_SCAN       C02 REACHABILITY_PROOF_SCAN
 C03 STATE_DAG_HYPOTHESIS        C04 COGNITIVE_COMPOSITION_SCAN
 C05 COST_CEREMONY_RECHECK       C06 DETERMINISTIC_PROOF_SCAN
           |                            |
           +-------------+--------------+
                         |
                         v
                D00 CURRENT_DISPOSITION_JOIN
                         |
           +-------------+--------------+
           |                            |
           v                            v
 D01 EXISTING_OWNER_ACTIONS      D02 UNOWNED_RESIDUAL_CANDIDATES
           |                            |
           |                            +--> D03 CHILD_SKILL_ADMISSION
           |                            +--> D04 RXX_ADMISSION
           |                            +--> D05 NO_ACTION_OR_DEFERRAL
           +-------------+--------------+
                         |
                         v
                 E00 SET_LEVEL_COLD_REVIEW
                         |
                 GAP? ---+--- YES --> repair affected rows --> D00
                         |
                        NO
                         v
                 E01 GENEALOGY_RECONCILIATION_FREEZE
                         |
                         v
                 E02 TRACKER_OR_IMPLEMENTATION_INTAKE
```

`E02` is outside this preparation tranche. It may still produce no RXX and no
source delta.

## Node specifications

### A00 — PUBLIC_V0400_READBACK_GATE

- Objective: prove exact public `v0.4.0.0` exists and is terminally readable.
- Consumes: tag, release object, assets, checksums, public download, release
  report, final-main identity and public-installed evidence.
- Produces: one baseline receipt binding commit, tree, tag object, package hash,
  member count and public URLs.
- Write owner: v0.4.1 controller only.
- Dependencies: none.
- Acceptance: independent public readback; local RC evidence is insufficient.
- Failure containment: corpus retention may be inspected read-only, but no
  current disposition, RXX admission, source mutation or tracker mutation.
- Current preparation state: `BLOCKED=DEFER_TO_V0410_BASELINE`.

### A01 — EXACT_BASELINE_IDENTITY

- Objective: bind every later check to one released source/package/runtime
  identity.
- Produces: baseline identity object and invalidation rules.
- Acceptance: source, package, installed and public identities remain distinct.
- Recompute trigger: any post-release source, package, install or public change.

### A02 — RETAINED_CORPUS_REVERIFY

- Objective: re-run 4/4, 12/12 and 658/658 corpus identity checks.
- Write owner: none unless exact retained-source drift is found.
- Acceptance: exact packet/member/index hashes and zero dangling locators.
- This node may execute concurrently with A03–A07 after A00.

### A03 — HISTORICAL_658_BASELINE_REVERIFY

- Objective: preserve each historical disposition, owner and non-adoption basis.
- Acceptance: 658 unique joins against the master index; no historical row is
  rewritten as current evidence.

### A04 — SOURCE_PACKAGE_HOST_CENSUS

- Objective: inventory exact released source, canonical package projection,
  generated compatibility projection, isolated installs and claimed hosts.
- Acceptance: source presence, package presence, installation, discovery,
  routing and behavioural activation are separate fields.

### A05 — RELEASE_EVIDENCE_CENSUS

- Objective: index exact v0.4 terminal review, self-dogfood, hosted and public
  readback evidence without inferring claims beyond each instrument.

### A06 — RXX_LIVE_GENEALOGY_CENSUS

- Objective: read every RXX through the actual post-v0.4 high-water mark,
  including body, all comments, state, relations and acceptance evidence.
- Required pressure owners: R31, R34, R42, R51, R53, R54 and R55; these are a
  minimum search set, not an exclusive owner list.
- Acceptance: every RXX has a current row and every identifier gap is explained.

### A07 — CURRENT_RUNTIME_OWNER_CENSUS

- Objective: map native source, deterministic, cognitive, state, package,
  routing, DAG, agent, L1–L5 and public owners from exact released bytes.
- Acceptance: no owner is inferred only from an RXX title or research label.

### B00 — RECONCILIATION_INPUT_JOIN

- Objective: prove all current-disposition inputs share the exact baseline.
- Single writer: reconciliation controller.
- Acceptance: corpus/index, historical baseline, released identity, RXX census
  and runtime census hashes are bound in one receipt.

### B01 — PROPERTY_FAMILY_PARTITION

- Objective: partition 658 rows by shared native-owner/failure mechanism for
  work economy while preserving every individual row.
- Anti-gaming: family membership never supplies a copied disposition.

### B02 — RXX_REVERSE_INDEX

- Objective: map every RXX back to primary, supporting, negative and bounded
  properties.
- Acceptance: no dangling property or RXX reference.

### B03 — 658_ROW_CURRENT_CENSUS

- Objective: fill every field in `V0410_CURRENT_DISPOSITION_SCHEMA.json`.
- Single writer per property row; disjoint lineage/family lanes may work in
  parallel.
- Acceptance: exactly 658 unique rows; release-dependent deferrals reduced to
  zero only through evidence-bound values.

### C01 — REJECTION_REOPEN_SCAN

- Objective: compare original rejection/deferral basis with current capability.
- Non-trigger: interest, maturity slogans or architectural possibility alone.

### C02 — REACHABILITY_PROOF_SCAN

- Objective: distinguish reference existence, trigger reachability, package
  presence, installation, host discovery and behavioural activation.

### C03 — STATE_DAG_HYPOTHESIS

- Objective: test whether state-derived work orchestration toward an
  evidence-backed terminal condition is complete, partial, composed or unowned.
- Required discriminators: automatic DAG derivation/recomputation;
  state-plan divergence; unresolved-obligation derivation;
  `DONE/ACTIVE/READY/BLOCKED`; JOIN/writer/authority/resource edges;
  progressive child routing; currentness invalidation; recovery/re-entry.
- Candidate-owner search: at minimum R31, R34, R42, R51, R53, R54 and R55.
- Acceptance: one claim-level matrix; no RXX conclusion is allowed at this node.

### C04 — COGNITIVE_COMPOSITION_SCAN

- Objective: determine whether model-facing judgement belongs to governor,
  existing child, reference, deterministic substrate or a candidate new child.
- Acceptance: any new-child candidate passes the separate admission schema.

### C05 — COST_CEREMONY_RECHECK

- Objective: compare current implementation/reasoning payoff against discovery,
  routing, package, maintenance, context and ordinary cheap-path cost.

### C06 — DETERMINISTIC_PROOF_SCAN

- Objective: locate existing discriminators and determine whether gaps are
  implementation, reachability or behavioural-proof-only.

### D00 — CURRENT_DISPOSITION_JOIN

- Objective: choose the smallest truthful destination for every property.
- Single writer: canonical disposition ledger.
- Acceptance: 658/658, complete evidence limits, no copied-current status.

### D01 — EXISTING_OWNER_ACTIONS

- Objective: group no-change, existing-owner amendment, reference, schema,
  checker, package and proof-only actions.
- No source work is manufactured when current implementation already satisfies
  the admitted contract.

### D02 — UNOWNED_RESIDUAL_CANDIDATES

- Objective: collect only rows still marked `GENUINE_UNOWNED_RESIDUAL` after
  owner composition and amendment checks.
- No candidate number allocation occurs here.

### D03 — CHILD_SKILL_ADMISSION

- Objective: apply `V0410_CHILD_SKILL_ADMISSION_SCHEMA.json` without skill-count
  quotas or lineage-name routing.

### D04 — RXX_ADMISSION

- Objective: apply `V0410_RXX_ADMISSION_SCHEMA.json` and set-level anti-split,
  anti-conflation and genealogy review.
- Output remains unallocated until reviewed admission passes and the live
  namespace is freshly censused.

### D05 — NO_ACTION_OR_DEFERRAL

- Objective: preserve still-rejected, domain-bound, assumption-bound,
  superseded, evidence-only and unresolved results without runtime inflation.

### E00 — SET_LEVEL_COLD_REVIEW

- Objective: challenge duplicate ownership, predecided conclusions, quotas,
  child proliferation, split/monolith reward hacking, stale-plan bias and
  research-to-runtime overtransfer.
- Acceptance: exact frozen packet, reviewer has no mutation authority, all
  findings reconciled before freeze.

### E01 — GENEALOGY_RECONCILIATION_FREEZE

- Objective: freeze 658 current rows, full RXX genealogy, candidate/amendment
  set, evidence identities and unresolved items.
- Acceptance: coverage receipts and exact hashes independently verified.

## Work-conserving rules

1. After A00, A02–A07 are independently READY subject to disjoint writers.
2. B01 and B02 may run concurrently only after B00.
3. C01–C06 may run by disjoint property families after B03 rows have complete
   input evidence; they must not concurrently write the same row.
4. D03 and D04 may review distinct candidate sets after D00, but final semantic
   owner allocation joins serially.
5. Shared schema, property ledger, RXX genealogy, package registry, governor and
   final report each have one writer.
6. Every JOIN rejects stale lane results whose input identities differ from the
   current baseline or whose graph dependencies changed.
7. Recompute the closed READY frontier after every material result, Andon,
   baseline change or JOIN.

## Initial frontier at preparation time

```text
DONE
  retention corpus 4/4, 12/12, 658/658 preparation
  historical absorption baseline 658/658 preparation
  executor schemas, held-out plan and provisional work-order preparation

ACTIVE
  none after this preparation branch is frozen

READY
  none of the current-disposition nodes

BLOCKED
  A00 PUBLIC_V0400_READBACK_GATE = DEFER_TO_V0410_BASELINE
  all descendants of A00
```
