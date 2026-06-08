# Greenfield / Brownfield Routing

Use this reference when an ImplementAudit run needs to decide whether work is
new governed surface, existing repo repair, or both.

Routing is part of audit governance. It does not authorize mutation, commit,
push, release, publication, provenance, Graphify indexing, or ActiveGraph
export.

## Definitions

**Greenfield audit-governed work** introduces a new governed artifact, fixture
family, checker, reference doc, sidecar contract, workflow, runtime capability,
or validation surface where no established repo owner/source/contract exists
yet.

**Brownfield audit-governed work** mutates, repairs, verifies, or closes findings
against existing repo artifacts, owners, tests, generated outputs, sidecars,
fixtures, contracts, or documented invariants.

**Mixed-mode work** occurs when a new artifact is introduced inside an
established repo. The outer shell is brownfield: inspect existing owners,
contracts, tests, generated artifacts, sidecars, and regression surface first.
The new artifact then receives greenfield intake before creation.

Default to brownfield when an existing repo is present. Do not use "new file" as
an excuse to skip existing repo contracts.

## Greenfield Intake

Before creating a new governed artifact, define:

- owner/source of truth
- scope and non-scope
- constraints and invariants
- acceptance criteria
- rollback or removal path
- evidence plan
- generated artifact plan: source-owned vs derived
- Graphify / ActiveGraph sidecar status: applicable, optional, not applicable,
  or forbidden
- canonical-vs-sidecar statement: Markdown, docs, checkers, fixtures, and live
  repo files remain canonical unless repo contract explicitly promotes a
  sidecar

Greenfield question batches may contain at most four material questions at a
time. Continue only until these categories are answered, assumed with evidence,
or terminally classified:

- target platform / runtime surface
- stack / framework / language preference
- design direction / UX / public-facing shape
- integrations and external dependencies
- scope and non-scope cut-line
- audience / user role / primary use case
- performance / scale / reliability constraints
- data model / persistence / schema anchors
- deployment / hosting / environment assumptions
- security / privacy / compliance constraints when material
- accessibility / i18n / content constraints when material
- acceptance criteria and proof shape

If any field is unknown, resolve it from repo files or mark the item
`blocked`, `deferred`, or `unverified`. Do not silently implement.

## Brownfield Inspection

Before mutating existing repo behavior, inspect:

- existing owner/source
- documented contracts and invariants
- tests, smokes, and checkers
- generated artifacts and whether they are source-owned or derived
- Graphify / ActiveGraph sidecars if present
- regression surface
- rollback path

Brownfield asks 0-2 true-gap questions after recon. Ask zero when repo files,
user prompt, applied context, and Gemba already answer the structural gaps. Ask
one or two only when a material owner decision remains. Convert micro-details
into explicit assumptions for Stage 6 review instead of blocking intake.

Patch the owner/source, regenerate derived surfaces, and run the smallest
relevant checks before claiming closure. Stale, missing, ambiguous, or
unsupported evidence is an Andon or `unverified` caveat, not success.

## Mixed-Mode Rule

For greenfield-inside-brownfield work:

1. Run brownfield inspection across the existing repo, package, contracts,
   generated surfaces, and validation checks.
2. Identify the new artifact as greenfield and complete greenfield intake for
   that artifact.
3. Add or update fixtures/checkers so the new behavior is not prose-only.
4. Re-run generated freshness checks when derived surfaces change.
5. Close the ledger with Smoke A/B evidence.

## Sidecar Boundary

Graphify may aid brownfield terrain inspection before owner/source selection.
Absent, stale, or unauthorized Graphify falls back to ordinary Gemba and live
file inspection.

ActiveGraph may preserve sidecar custody for proof events when authorized.
Absent ActiveGraph falls back to Markdown ledgers and final reports.

Neither sidecar replaces repo-local owners, checkers, fixtures, smoke output,
audit ledgers, or live-file inspection. Neither is canonical proof unless the
repo explicitly promotes it with its own evidence and gates.

## DMAIC — Brownfield improvement routing

Use DMAIC when work is an existing repo defect, regression, release repair,
package-bloat issue, stale docs, or broken checker.

- **Define**: state the defect/gap, owner/source, scope, user/consumer impact,
  and acceptance target.
- **Measure**: capture baseline evidence (Smoke A), current behavior, failure
  rate or count when available, and complete working-tree state.
- **Analyze**: identify root cause, dependency surface, generated-artifact owner,
  Muda/Mura/Muri class, and regression risk.
- **Improve**: patch owner/source, regenerate derived artifacts, run checks,
  and record countermeasure.
- **Control**: add or verify sustain mechanism — tests, templates, AGENTS.md
  rules, CI gate, or package gate — so the defect cannot regress silently.

Evidence boundary: DMAIC is a routing and evidence-shaping pattern for
audit-governed repo work. Do not claim sigma level, DPMO, statistical process
control, or Six Sigma certification unless those values are actually measured
and verified in the run.

## DMADV — Greenfield / replacement routing

Use DMADV when work introduces a new governed artifact, new workflow, new
runtime capability, new package surface, or is a replacement design.

- **Define**: define the new capability or artifact, users, constraints,
  non-scope, owner/source of truth, and success boundary.
- **Measure**: define Critical-to-Quality-style acceptance measures, evidence
  types, baseline absence or starting state, and risk measures.
- **Analyze**: compare design alternatives, dependencies, package/runtime
  boundaries, rollback/removal path, and sidecar status.
- **Design**: create the bounded implementation plan, phase specs, templates,
  fixtures, and validation path.
- **Verify**: run Smoke B, final audit, deliverable checks, package/sidecar
  boundary checks, and obtain owner acceptance where needed.

Evidence boundary: same as DMAIC — routing pattern only, no statistical claim.

## Mixed DMAIC/DMADV

Mixed work runs DMAIC for the brownfield outer shell and DMADV for any new
governed artifact introduced inside it. Run brownfield inspection first, then
greenfield intake for the new artifact.

## DMAIC/DMADV routing decision

| Trigger | Route |
|---|---|
| Existing defect, regression, release repair, broken checker, stale doc | DMAIC |
| New governed artifact, new runtime capability, new workflow, replacement design | DMADV |
| Both (brownfield + new artifact) | Mixed |
| None of the above / simple single-owner fix | PDCA |

## Positive Identity

IMPLEMENTAUDIT is an audit-governed implementation skill. It routes work through
repo-local owner/source discovery, acceptance criteria, rollback/evidence
planning, fixtures/checkers, and smoke-before-claim closure. It can help
implement changes, but only through the audit contract; it is not a generic
autonomous build runner.
