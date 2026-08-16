# Engineering Genealogy Retention Design

## Status and boundary

This design defines a bounded pre-v0.4.1 preparation tranche. It preserves the repository-neutral research genealogy and creates a read-only historical IMPLEMENTAUDIT absorption baseline. It does not perform current-v0.4 reabsorption, assign current native/RXX owners, change runtime or package behaviour, alter child-skill architecture, start a v0.4.1 release campaign, open a pull request, or merge anything.

Anything that requires the exact released v0.4.0.0 baseline is recorded as `DEFER_TO_V0410_BASELINE`.

## Source authority and preservation decision

The twelve supplied frozen packet ZIPs and their packet/member manifests are the research-content authority. The selected preservation form is:

- `PRESERVE_EXACT_PACKET_ZIPS=YES`
- `PRESERVE_EXTRACTED_CORPUS=YES`

Both representations are committed. Raw delivered ZIP SHA-256 values and embedded packet/content digests remain distinct identity kinds. Where a packet has no embedded manifest, the lineage manifest records `NOT_PRESENT_IN_PACKET` rather than inventing one.

The complete denominator is four trifectas, twelve lineages, and 658 lineage-scoped properties:

| Trifecta | Lineages | Properties |
|---|---:|---:|
| LAW | Evolved Lean, Evolved Agile, Evolved Waterfall | 106 |
| CSS | Cognitive Systems Engineering, Statistical Engineering, Systems Safety | 195 |
| SSD | Systems Engineering, Systems Security Engineering, Decision and Operations Engineering | 198 |
| DRF | Distributed Systems Engineering, Reliability and Maintainability Engineering, Formal Methods and Verification Engineering | 159 |
| **Total** | **12** | **658** |

## Repository topology

The repository-neutral corpus lives under `docs/research/genealogy/`:

```text
docs/research/genealogy/
├── README.md
├── RESEARCH_METHOD.md
├── REPLICATION_GUIDE.md
├── CORPUS_MANIFEST.json
├── PROPERTY_MASTER_INDEX.json
├── method/
│   ├── SOURCE_PROMPT_MANIFEST.json
│   ├── source-prompts/
│   └── templates/
├── law/
├── css/
├── ssd/
└── drf/
```

Each trifecta directory contains a neutral README and exactly three lineage directories. Each lineage contains:

- `README.md`: neutral scope, packet identity, property denominator, and source-schema notes;
- `LINEAGE_MANIFEST.json`: raw packet identity, embedded-manifest identity/scope when present, exact member inventory, property-ledger locator/root, and expected property count;
- `packet/`: the exact delivered ZIP;
- `corpus/`: exact extracted packet members with archive-relative paths preserved.

`CORPUS_MANIFEST.json` is the deterministic repository-level file inventory and digest projection. `PROPERTY_MASTER_INDEX.json` is a navigational projection over all 658 source rows. Its global key is `<SOURCE_LINEAGE_ID>::<SOURCE_PROPERTY_ID>`; the original source row, terminology, status, and heterogeneous schema remain authoritative in the preserved corpus.

The three exact supplied DRF source prompts and their manifest are preserved under `method/source-prompts/`. Generalised templates are derived method aids, clearly labelled as candidates rather than historical source prompts.

## Historical absorption baseline

IMPLEMENTAUDIT-specific evidence remains outside the neutral corpus at:

```text
docs/research/implementaudit/historical-absorption-baseline/
├── README.md
└── HISTORICAL_ABSORPTION_BASELINE.json
```

The baseline consumes the exact frozen pre/post-implementation crosswalk occurrence from the v0.4 audit run as read-only input. It records the source file bytes/SHA-256, row-level historical locator, original disposition, one normalised historical class, and zero or more evidence-tagged historical constraint indicators. It does not copy current v0.4 post-implementation verdicts into the baseline.

The exhaustive normalisation is:

- `HISTORICALLY_ABSORBED_COMPLETE`: `ALREADY_STRICTLY_STRONGER`, `STRONGER_BY_NATIVE_COMPOSITION`, `EQUIVALENT`, LAW `ASC`, or LAW `AEDF`;
- `HISTORICALLY_ABSORBED_PARTIAL`: `PUBLIC_DOCUMENTATION_ONLY` or `UNIMPLEMENTED_OR_BOUNDED__NO_NEW_PROOF_CLAIM`;
- `HISTORICALLY_EXISTING_OWNER_NEEDS_AMENDMENT`: `EXISTING_RXX_NEEDS_AMENDMENT` or LAW `PC`;
- `HISTORICALLY_LINEAGE_NATIVE_RESIDUAL`: `LINEAGE_RXX_NATIVE_RESIDUAL`;
- `HISTORICALLY_IMPLEMENTATION_OR_REACHABILITY_GAP`: `IMPLEMENTATION_OR_REACHABILITY_REPAIR`;
- `HISTORICALLY_BEHAVIOURAL_PROOF_GAP`: `BEHAVIOURAL_PROOF_GAP` or `UNRESOLVED_BOUNDED_BEHAVIOURAL_PROOF_GAP`;
- `HISTORICALLY_ASSUMPTION_BOUND`: `ASSUMPTION_BOUND`;
- `HISTORICALLY_DOMAIN_BOUND`: `DOMAIN_OR_HIGH_CONSEQUENCE_BOUND` or LAW `CSO`;
- `HISTORICALLY_REJECTED_OR_SUPERSEDED`: `REJECTED_SOURCE_CEREMONY_OR_WEAKER_FORM`, `SUPERSEDED_BY_STRONGER_NATIVE_FORM`, LAW `REE`, or LAW `CNA`;
- `HISTORICALLY_UNRESOLVED`: `UNRESOLVED`, `UNRESOLVED_DETERMINISTIC_FIXTURE_GAP`, or `UNRESOLVED_SOURCE_STATIC_PROOF_GAP`.

Constraint indicators are evidence indices, not counterfactual reabsorption decisions. A row receives an indicator only when an explicit historical gap/disposition field matches a documented rule and the matching field/value is retained as evidence. The requested indicator vocabulary is:

- `MONOLITHIC_CONTEXT_COST`
- `ABSENT_PROGRESSIVE_DISCLOSURE_ROUTE`
- `ABSENT_STATE_REPRESENTATION`
- `ABSENT_DETERMINISTIC_DISCRIMINATOR`
- `ABSENT_AUTHORITY_OR_CURRENTNESS_MECHANISM`
- `ABSENT_COMPOSABLE_COGNITIVE_OWNER`
- `EXCESSIVE_CEREMONY_OR_COST`

Every row carries `V0400_CHANGE_DISPOSITION=DEFER_TO_V0410_BASELINE`.

## Deterministic tooling

The source-lock file declares the twelve packet inputs, lineage topology, raw hashes, property-ledger members/roots, and prompt inputs. A generator:

1. verifies each raw source ZIP before copying;
2. copies exact ZIP bytes into the selected lineage;
3. extracts members without normalising bytes;
4. writes lineage manifests, root corpus manifest, source-prompt manifest, and the 658-row property index deterministically;
5. builds the historical absorption baseline from the exact frozen crosswalk occurrence without importing current-v0.4 verdicts.

A separate checker recomputes and validates topology, packet and member hashes, extracted-byte parity, unique global property keys, 658-row coverage, source locators, prompt identities, neutral-corpus boundaries, and package exclusion. The test mutates disposable copies to prove fail-closed behaviour for missing lineages, changed packet bytes, missing/duplicate properties, dangling locators, absolute local paths, current IMPLEMENTAUDIT disposition claims in neutral README files, and genealogy inclusion in the release package.

The scripts use only Python's standard library plus the repository's existing shell-test harness. JSON is UTF-8, sorted, indented, newline-terminated, and timestamp-free so regeneration is byte-stable.

## Authority and no-drift rules

- Frozen packet members remain byte-exact; generated indexes do not rewrite research conclusions.
- Neutral lineage documentation contains no current RXX/native-owner/release assertions.
- Historical absorption rows preserve frozen prior classifications and evidence locators; they do not claim present implementation truth.
- Generated files are rebuilt from source locks and exact inputs, not hand-edited.
- The genealogy tree remains documentation/research data and must stay outside `IMPLEMENTAUDIT.skill` and plugin package payloads.
- No pull request or merge is part of this tranche. The dedicated branch is pushed only for reviewability.

## Acceptance

The tranche is complete when:

1. the branch is isolated from the active v0.4 worktree and based on a recorded `origin/main` SHA;
2. all 12 raw ZIP hashes and extracted member hashes verify;
3. all four trifectas and twelve lineage directories are present;
4. `PROPERTY_MASTER_INDEX.json` has 658 unique lineage-scoped rows and exact source locators;
5. the historical baseline has 658 rows, an exhaustive class count of 658, evidence-backed constraint-indicator counts, and only deferred v0.4-change claims;
6. deterministic regeneration is byte-identical;
7. focused negative controls and the repository verification suite pass;
8. the bounded diff is reviewed, committed, and pushed to the dedicated branch without a PR.
