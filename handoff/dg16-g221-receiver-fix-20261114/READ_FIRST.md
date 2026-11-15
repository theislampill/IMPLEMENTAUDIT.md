# DG16 G221 receiver correction: read first

**Authority: NONE.** This branch is source-only engineering. It contains no recipient, Root decision, review selection, seal issuance, hosted dispatch, key use, decryption, acceptance, merge or issue action. G220's own branch and failed evidence are untouched.

## Locators
| Item | Value |
|---|---|
| Branch | `engineering/dg16-g221-receiver-fix-20261114`. It triggers no workflow: `pages` and `validate` run on `main`/PR only, and the G2 workflow filters on the G220 host-20 branch. |
| **Correction commit** (the candidate source) | `82f4c3d1a5ca85d88f8cb73672d7244dba4f3316`, tree `a7a17de3675fdbce11cc258b9bdc4aab49e8cded` |
| Parent (G220 workflow commit) | `ce144b1d06f81bda3225b48d3bab32374515cff5`, tree `bbc3669b2167548a5a8b9ec0986b1e8b18e720eb`; its parent is product `205aeab7` / tree `9ffbaf95` |
| Handoff commit | This folder only. It is on top of the correction commit and is not part of the candidate tree. |
| G220 failure (preserved) | run 43640583300, attempt 1, conclusion failure; public FAILURE.json: `FULL_PAIR_NOT_COMPLETELY_RECEIVED` |

## The defect, and the change in the correction commit (7 files, 110+/35−)
In `qualification/dg16-r5-full-g2/pending_relation.py` (`948b4b21…` → `b73adbc6…`), each of two receiver predicates refused every genuine run:
1. **PENDING_CONTROL_POPULATION.** The predicate accepted only lowercase names. The real producer `tests/cognition-pending-durability.py` (`9f0f3adc…`) emits `unreserved-JOIN-refuses-without-state-change`. **Now:** exact ordered equality with `CONTROL_NAMES` (58 durability names, 54 loader names).
2. **PENDING_COMMAND_SHAPE.** The predicate required argv[0] to be `<runtime-bin>/python`. The producers are launched as `python3` (`tests/internal-skill-routing.test.sh:284–286`). **Now:** exactly `<runtime-bin>/python3`.

Pins propagated, sha256 before → after:

| File | Before | After |
|---|---|---|
| `RELATION_INPUTS.json` | 51733af1 | 41bdfe0f |
| `POLICY.json` | 86cdb96f | 21afa772 |
| `pair_driver.py` | 1967e1cc | 3bf4d21e |
| `run.py` | 383bec62 | 68816607 |
| `qualification/dg16-r5-full-g2-decisions/CURRENT_HOST_QUALIFICATION_REQUEST.json` | 51712275 | 74c652e8 |
| `.github/workflows/dg16-r5-full-g2.yml` (20 adapter-digest literals only; the branch filter is still host-20) | 4589fc30 | 2cb37274 |

`SOURCE_MANIFEST.json` is unchanged (1766 files / 167023692 bytes).

## Custody files that are not repository files (proposals in `prospective-custody/`)
| File | Before | After |
|---|---|---|
| candidate `SEAL.json` | 50f694f0 | 1d2ef960 |
| `receiver/BINDING_TEMPLATE.json` | adfcf7b0 | 692546f1 |
| `receiver/ROOT_BINDING_TEMPLATE.json` | 7e09a5c7 | ab439ba2 |
| `author/bind_public_successor.py` | a6545228 | 9e52c046 |
| `author/compose-candidate-bound.py` | bfbce571 | 9b1e7dda |
| `author/compose-final-bound.py` | b4c20048 (G220 stage) | c3498090 |

These are regenerated on the **G220** base. A real G221 successor (new host-21 branch, new recipient) changes run.py, the request, the workflow, the templates and the seal again. Only `pending_relation`, `RELATION_INPUTS`, `POLICY` and `pair_driver` are independent of the branch.

## Verification

**Fable 5.2 (author):** see `evidence/FABLE_AUTHOR_REPORT.md`.
- Through the original consumers on real producer output (CPython 3.14.4):

| Receiver | Result |
|---|---|
| G220 | 11 pass / 4 refused |
| G220 with only the name fix | 4 refused (PENDING_COMMAND_SHAPE) |
| G221 | **17 / 17 pass**, both scopes compare equal |

- Mutations: 24 unit mutations per role and 10 end-to-end tampers, all refused.

**Opus 5.5 (independent):**
- Preimages: all 7 before-images equal `ce144b1d`'s files, and each committed blob is byte-exact.
- Re-derived populations: Opus ran both real producers from a clean checkout of 205aeab7 (tree 9ffbaf95, python3.12). Their outputs equal `CONTROL_NAMES` exactly: 58 and 54 names, ordered (`evidence/OPUS_PRODUCER_*.json`).
- Adverse controls on those outputs (`evidence/OPUS_ADVERSE_CONTROLS.txt`):
  - G220 refuses the real durability output and the real `python3`.
  - G221 accepts both, and refuses missing, extra, reordered, renamed, case-changed and other-role names, and the `python` alias.
  - G220 *accepted* most of those mutations, so G221 is also stricter.
- Pin chain: the structural chain check gives 17/17 on the G220 base and 17/17 on G221 (`evidence/OPUS_CHAIN_CHECK_*.json`).

**Not covered:**
- No full 119-node pair was run locally. The DAG-route projections have never run on any host.
- The pinned lists come from local runs (3.12.3 and 3.14.4 agree). The hosted stdout is private.

## What G221 still needs (not included here)
1. Root or an appointed successor adopts the correction and chooses the pinned-list approach (an alternative regex approach is in Fable's report and is not proposed).
2. A new host branch (host-21) and workflow branch filter, with the pins regenerated on that base (`tools/regen_chain.py` in the author's scratch).
3. A **fresh recipient**. The current one is bound to host-20 and expires 2026-11-15T14:51:46Z, and its replacement sequence is already used. The private key stays with the owner.
4. Root reissues the four decision bodies, the candidate and review seals, the composition (the final composer stage), the public leaf index, the receiver binding and the operator static source.
5. A pre-launch check that neither host-21 nor control-21 exists. Publish once.
6. The independent live review and Root consumption, pushed to control-21 within about 270 s of `prepare-review`. The control branch must not exist beforehand. A single fetch failure is terminal.
7. Terminal receiving, then Root acceptance. G132 (G1) and G3 follow separately.
