# R0039 complete package reconciliation

**The complete package still exceeds the original cap and reserve. No shipped-source reduction is claimed.** The sealed complete artifacts are 361,173 bytes (plugin) and 356,938 bytes (standalone). The restored complete artifacts are 361,171 and 356,939 bytes. Exact comparison shows identical member population, modes and all non-inventory bytes; only the generated inventory `source.commit` differs. Its compressed effect is −2 plugin bytes and +1 standalone byte.

This repository-only evidence reconciles already-built packages. It does not change runtime `0.4.0`, release family `v0.4.0.0`, membership, caps, source or installer behavior, and it grants no native/currentness/full-verifier acceptance or engineering-exhaustion disposition. No recompression occurred in this reconciliation.

## Accounting and scope

Each role has cap **327,680 bytes**, with **2,000 bytes** required reserve: admissible maximum **325,680**. Archive bytes equal compressed member bytes plus local/central member headers plus the **22-byte ZIP end record**. Uncompressed raw bytes are reported separately. The complete exact map, SHA-256s, modes, owner/source mapping, all 12 subjects, and all deltas are in `PACKAGE_RECONCILIATION.json`, supplied with the focused return. Its normalized member observation arrays use the declared subject order; no member is omitted.

## Source identities

| Measured subject | Commit | Tree |
|---|---|---|
| main | `44117ccd5af275f24bed923da7ba282a829f42e9` | `cf695dc0befdc0cbaa6a92e43db512ce2eb504ad` |
| issue-only | `8934901bee6faf31b9e04bc228930ce8d7cf1c81` | `9455f747bb0eb59add868ee6d3c863987250cfe7` |
| P01 | `c2ab1ac133b4f49be352173cf97e033a3c16384c` | `9380454f95bf09292d8768b1eecb20632bb3a271` |
| P02 | `40e12db262c03738b2bcda1a1e321133d8073850` | `72a6806de517e74be9c04847cd9ec60170fc33d3` |
| P03 | `1fa6d5d885538eab41f2467e0af7b1ff09b2fbd2` | `6411ccd514b00dc182a2cff5036b22326c068e16` |
| P04 | `bc9b6efac135814c91cd66058826e9682d0aaf98` | `3d892ca88073a61ea5776271f714196702438e71` |
| P05 | `7b067ae451614bfe9da616c7ec8892baacaebdff` | `89266a8bf8f52eea1c2610641227fa1ceb56ce7e` |
| P06 | `8ffa45b2745d0ec5bc5a41c3a211da183670426a` | `473124fa97b6344ae4f57f0262976fa5f943d200` |
| P07 | `eebf916e5a78daf98e46cf3fde383affa32523bd` | `1c35e9c46b63f578b5dd66f3e6fac4c4e318969e` |
| P08 | `b171a7232dbaf3619280cda2a916ac273dfbaf30` | `ba6bfe1437770ec0cd7f1a18ebcfd0a62a740e4b` |
| restored complete | `685ef15f55f0a9ed33b8e82cbed93acb7c50ab47` | `ba6bfe1437770ec0cd7f1a18ebcfd0a62a740e4b` |
| sealed complete | `2bf58b1566538cab6134224c58ceac476d00c6a3` | `ba6bfe1437770ec0cd7f1a18ebcfd0a62a740e4b` |

All recorded worktree states are `clean`. Commit IDs are exact package inventory inputs, including local reconstructed measurements; this table makes no claim that reconstructed commits are published PR heads. Both complete subjects share the same source tree.

## All-stage archive totals

The delta columns compare each reconstructed row with its preceding reconstructed row; sealed complete is a separate original anchor. “Payload Δ” excludes generated inventory and includes the changed source-member headers. Inventory Δ is the compressed inventory stream change.

### IMPLEMENTAUDIT.plugin.zip

| Subject | Raw bytes | Compressed members | Member headers | End | Archive bytes | Archive Δ | Payload Δ | Inventory Δ | Required reduction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| main | 842,640 | 277,258 | 10,274 | 22 | 287,554 | — | — | — | 0 |
| issue-only | 1,000,041 | 314,764 | 10,846 | 22 | 325,632 | 38078 | 37910 | 168 | 0 |
| P01 | 1,096,255 | 333,645 | 11,024 | 22 | 344,691 | 19059 | 19024 | 35 | 19,011 |
| P02 | 1,147,671 | 349,363 | 11,416 | 22 | 360,801 | 16110 | 16010 | 100 | 35,121 |
| P03 | 1,147,671 | 349,362 | 11,416 | 22 | 360,800 | -1 | 0 | -1 | 35,120 |
| P04 | 1,148,535 | 349,544 | 11,416 | 22 | 360,982 | 182 | 181 | 1 | 35,302 |
| P05 | 1,149,357 | 349,742 | 11,416 | 22 | 361,180 | 198 | 189 | 9 | 35,500 |
| P06 | 1,149,357 | 349,734 | 11,416 | 22 | 361,172 | -8 | 0 | -8 | 35,492 |
| P07 | 1,149,357 | 349,734 | 11,416 | 22 | 361,172 | 0 | 0 | 0 | 35,492 |
| P08 | 1,149,357 | 349,730 | 11,416 | 22 | 361,168 | -4 | 0 | -4 | 35,488 |
| restored complete | 1,149,357 | 349,733 | 11,416 | 22 | 361,171 | 3 | 0 | 3 | 35,491 |
| sealed complete | 1,149,357 | 349,735 | 11,416 | 22 | 361,173 | — | — | — | 35,493 |

### IMPLEMENTAUDIT.skill

| Subject | Raw bytes | Compressed members | Member headers | End | Archive bytes | Archive Δ | Payload Δ | Inventory Δ | Required reduction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| main | 838,410 | 275,934 | 7,650 | 22 | 283,606 | — | — | — | 0 |
| issue-only | 995,745 | 313,425 | 8,090 | 22 | 321,537 | 37931 | 37778 | 153 | 0 |
| P01 | 1,091,937 | 332,318 | 8,224 | 22 | 340,564 | 19027 | 18980 | 47 | 14,884 |
| P02 | 1,143,229 | 348,010 | 8,528 | 22 | 356,560 | 15996 | 15905 | 91 | 30,880 |
| P03 | 1,143,229 | 348,009 | 8,528 | 22 | 356,559 | -1 | 0 | -1 | 30,879 |
| P04 | 1,144,093 | 348,202 | 8,528 | 22 | 356,752 | 193 | 181 | 12 | 31,072 |
| P05 | 1,144,915 | 348,388 | 8,528 | 22 | 356,938 | 186 | 189 | -3 | 31,258 |
| P06 | 1,144,915 | 348,390 | 8,528 | 22 | 356,940 | 2 | 0 | 2 | 31,260 |
| P07 | 1,144,915 | 348,388 | 8,528 | 22 | 356,938 | -2 | 0 | -2 | 31,258 |
| P08 | 1,144,915 | 348,388 | 8,528 | 22 | 356,938 | 0 | 0 | 0 | 31,258 |
| restored complete | 1,144,915 | 348,389 | 8,528 | 22 | 356,939 | 1 | 0 | 1 | 31,259 |
| sealed complete | 1,144,915 | 348,388 | 8,528 | 22 | 356,938 | — | — | — | 31,258 |

Main and issue-only meet this numerical budget. The complete runtime first exceeds it after shared P01. A cap check is only the recorded package-budget result; it does not imply the unreached full validation banks or native gates passed.

## Measured owning-component contributions

The table reports source-owner member contributions as **compressed bytes plus their ZIP member headers**, excluding generated inventory and the fixed end record. Raw, compressed and header totals for every individual owner at every stage are separately complete in the companion JSON. Unchanged baseline source components remain assigned to their actual source paths; the final row below only summarizes those unchanged rows for readability.

| Owning component | Main contribution P / S | Issue-only growth P / S | Shared growth P / S | Restored contribution P / S |
|---|---:|---:|---:|---:|
| Audit-state child under governor | 1,227 / 1,109 | 0 / 0 | 687 / 670 | 1,914 / 1,779 |
| Existing controller/archive namespace owners | 0 / 0 | 0 / 0 | 906 / 862 | 906 / 862 |
| Child evidence/continuity owner | 7,446 / 7,402 | 0 / 0 | 180 / 180 | 7,626 / 7,582 |
| Claim-run sole native authority | 4,628 / 4,584 | 0 / 0 | 19,024 / 18,980 | 23,652 / 23,564 |
| Continuity / R0033 owner | 3,496 / 3,452 | 0 / 0 | 3,377 / 3,377 | 6,873 / 6,829 |
| Implementaudit governor owner | 7,729 / 7,685 | 0 / 0 | 305 / 305 | 8,034 / 7,990 |
| Helper reachability registry owner | 10,671 / 10,627 | 0 / 0 | 973 / 973 | 11,644 / 11,600 |
| Native canonical-reader owner | 0 / 0 | 0 / 0 | 6,971 / 6,927 | 6,971 / 6,927 |
| Native phase/mutation validator owner | 11,899 / 11,855 | 0 / 0 | 285 / 285 | 12,184 / 12,140 |
| R0039 deterministic projection, algebra and archive owner | 0 / 0 | 37,910 / 37,778 | 0 / 0 | 37,910 / 37,778 |
| Native run-root validator owner | 16,080 / 16,036 | 0 / 0 | 840 / 840 | 16,920 / 16,876 |
| Run protocol owner | 23,639 / 23,595 | 0 / 0 | 565 / 565 | 24,204 / 24,160 |
| Native ROADMAP template owner | 1,317 / 1,273 | 0 / 0 | 438 / 438 | 1,755 / 1,711 |
| Native STATE template owner | 3,895 / 3,851 | 0 / 0 | 555 / 555 | 4,450 / 4,406 |
| Transcript/continuity owner | 8,195 / 8,151 | 0 / 0 | 298 / 298 | 8,493 / 8,449 |
| All remaining unchanged source components (individually mapped in JSON) | 183,564 / 180,373 | 0 / 0 | 0 / 0 | 183,564 / 180,373 |

Only three new shipped members distinguish main from issue-only: `canonical-state-rotation.md`, `canonical_hot_projection.py`, and `rotate-canonical-state.py`. The shared claim-run import and required reader/continuity integrations are distinct from that issue-only payload. Repository-only semantic bindings, fixture edits and installer fixes are retained source work but add no shipped runtime member bytes at P03/P06/P07/P08.

## Inventory identity effects

| Transition | Plugin inventory Δ | Standalone inventory Δ | Interpretation |
|---|---:|---:|---|
| main → issue-only | +168 | +153 | Member inventory and source identity both change; combined stream effect reported separately. |
| issue-only → P01 | +35 | +47 | Member inventory and source identity both change; combined stream effect reported separately. |
| P01 → P02 | +100 | +91 | Member inventory and source identity both change; combined stream effect reported separately. |
| P02 → P03 | -1 | -1 | Only source identity changes; zero runtime/member-content reduction. |
| P03 → P04 | +1 | +12 | Member inventory and source identity both change; combined stream effect reported separately. |
| P04 → P05 | +9 | -3 | Member inventory and source identity both change; combined stream effect reported separately. |
| P05 → P06 | -8 | +2 | Only source identity changes; zero runtime/member-content reduction. |
| P06 → P07 | +0 | -2 | Only source identity changes; zero runtime/member-content reduction. |
| P07 → P08 | -4 | +0 | Only source identity changes; zero runtime/member-content reduction. |
| P08 → restored complete | +3 | +1 | Only source identity changes; zero runtime/member-content reduction. |
| sealed complete → restored complete | -2 | +1 | Only source identity changes; zero runtime/member-content reduction. |

P03, P06, P07 and P08 have no changed shipped source members: their small archive changes arise entirely from generated inventory source commit/tree identities. Where actual source members also change, the inventory record hashes/lengths and source identity change together; compressed contributions are not additive, so this report does not invent a commit-only decomposition. Final restored-versus-sealed inventories are identical after removing `source`, with only `source.commit` changed.

## Exact original-to-restored parity

| Role | Members compared | Non-inventory members exactly equal | All modes/ZIP methods equal | Original bytes | Restored bytes | Archive Δ | Source payload reduction |
|---|---:|---:|---|---:|---:|---:|---:|
| canonical_plugin | 67 | 66 | yes | 361,173 | 361,171 | -2 | **0** |
| standalone_compatibility | 64 | 63 | yes | 356,938 | 356,939 | +1 | **0** |

Compared actual retained ZIP member bytes and modes directly, not just member names. Every non-inventory member also has identical compressed size. Only inventory metadata changes; the SHA and exact byte comparator details for every member appear in the companion JSON. The original 35,493/31,258-byte deficits remain retained evidence. The actual restored deficits are 35,491/31,259; neither is a repaired package.

## Complete final member map

Each row below is a restored complete member. Compressed sizes are canonical member DEFLATE bytes; header is the local plus central ZIP member header contribution. JSON additionally carries each SHA-256, each historical version, every owner declaration and all stage observations. Plugin paths are source paths except the generated inventory and package-contract copy. Standalone paths are explicitly mapped to their governor or child source below.

### IMPLEMENTAUDIT.plugin.zip

| Archive member | Source / projection | Owner component | Raw | Compressed | Header | Mode |
|---|---|---|---:|---:|---:|---|
| `.claude-plugin/marketplace.json` | same path | package_identity | 351 | 162 | 138 | `0644` |
| `.claude-plugin/plugin.json` | same path | package_identity | 217 | 149 | 128 | `0644` |
| `.codex-plugin/plugin.json` | same path | package_identity | 922 | 431 | 126 | `0644` |
| `IMPLEMENTAUDIT_INVENTORY.json` | scripts/package-contract.py::inventory_bytes | generated_inventory | 13,070 | 3,915 | 134 | `0644` |
| `IMPLEMENTAUDIT_PACKAGE.json` | package/implementaudit-package.json | package_identity | 2,941 | 912 | 130 | `0644` |
| `skills/audit-andon/SKILL.md` | same path | existing source owner | 2,812 | 1,362 | 130 | `0644` |
| `skills/audit-assess/SKILL.md` | same path | existing source owner | 2,039 | 1,047 | 132 | `0644` |
| `skills/audit-implement/SKILL.md` | same path | existing source owner | 2,579 | 1,230 | 138 | `0644` |
| `skills/audit-state/SKILL.md` | same path | audit_state | 3,858 | 1,784 | 130 | `0644` |
| `skills/implementaudit/SKILL.md` | same path | governor_bootloader | 20,244 | 7,898 | 136 | `0644` |
| `skills/implementaudit/references/audit-category-matrix.md` | same path | existing source owner | 14,156 | 5,406 | 190 | `0644` |
| `skills/implementaudit/references/audit-playbook.md` | same path | existing source owner | 20,140 | 8,329 | 176 | `0644` |
| `skills/implementaudit/references/canonical-state-ref-namespaces.json` | same path | canonical_ref_namespaces | 2,800 | 694 | 212 | `0644` |
| `skills/implementaudit/references/canonical-state-rotation.md` | same path | r0039_projection_archive | 16,389 | 6,456 | 196 | `0644` |
| `skills/implementaudit/references/child-agents.md` | same path | child_evidence_continuity | 18,419 | 7,454 | 172 | `0644` |
| `skills/implementaudit/references/continuity.md` | same path | continuity_contract | 17,175 | 6,705 | 168 | `0644` |
| `skills/implementaudit/references/convergence-mode.md` | same path | existing source owner | 8,668 | 3,509 | 180 | `0644` |
| `skills/implementaudit/references/goal-format.md` | same path | existing source owner | 6,895 | 2,880 | 170 | `0644` |
| `skills/implementaudit/references/identity-namespaces.json` | same path | existing source owner | 1,265 | 493 | 190 | `0644` |
| `skills/implementaudit/references/issue-ready-work-orders.md` | same path | existing source owner | 18,210 | 6,923 | 194 | `0644` |
| `skills/implementaudit/references/lean-operating-discipline.md` | same path | existing source owner | 21,792 | 8,465 | 198 | `0644` |
| `skills/implementaudit/references/phase-design.md` | same path | existing source owner | 20,396 | 8,311 | 172 | `0644` |
| `skills/implementaudit/references/plan-lifecycle.md` | same path | existing source owner | 30,905 | 11,357 | 176 | `0644` |
| `skills/implementaudit/references/planning-depth.md` | same path | existing source owner | 18,762 | 7,235 | 176 | `0644` |
| `skills/implementaudit/references/repo-state-comparison.md` | same path | helper_reachability | 33,366 | 11,454 | 190 | `0644` |
| `skills/implementaudit/references/routing.md` | same path | existing source owner | 14,323 | 5,614 | 162 | `0644` |
| `skills/implementaudit/references/sidecars.md` | same path | existing source owner | 5,673 | 2,773 | 164 | `0644` |
| `skills/implementaudit/references/terminology-integration.md` | same path | existing source owner | 4,877 | 2,093 | 194 | `0644` |
| `skills/implementaudit/references/transcript-contract.md` | same path | transcript_continuity | 21,584 | 8,307 | 186 | `0644` |
| `skills/implementaudit/scripts/apply-observed-mutation.sh` | same path | existing source owner | 56,144 | 11,405 | 188 | `0755` |
| `skills/implementaudit/scripts/canonical_hot_projection.py` | same path | r0039_projection_archive | 57,891 | 13,306 | 190 | `0755` |
| `skills/implementaudit/scripts/check-authorization-binding.sh` | same path | existing source owner | 17,469 | 6,010 | 196 | `0755` |
| `skills/implementaudit/scripts/check-closure-surface.sh` | same path | existing source owner | 94,842 | 21,941 | 184 | `0755` |
| `skills/implementaudit/scripts/check-duplication-parity.sh` | same path | existing source owner | 5,208 | 1,755 | 190 | `0755` |
| `skills/implementaudit/scripts/check-evidence-anchor.sh` | same path | existing source owner | 43,368 | 10,063 | 184 | `0755` |
| `skills/implementaudit/scripts/check-handoff-packet.sh` | same path | existing source owner | 8,912 | 3,072 | 182 | `0755` |
| `skills/implementaudit/scripts/check-lesson-lift.sh` | same path | existing source owner | 11,417 | 3,620 | 176 | `0755` |
| `skills/implementaudit/scripts/check-respec-impact-set.sh` | same path | existing source owner | 6,560 | 2,129 | 188 | `0755` |
| `skills/implementaudit/scripts/claim-run-rotation.py` | same path | claim_run_authority | 93,366 | 18,251 | 178 | `0755` |
| `skills/implementaudit/scripts/claim-run.sh` | same path | claim_run_authority | 17,368 | 5,063 | 160 | `0755` |
| `skills/implementaudit/scripts/custody-append.sh` | same path | existing source owner | 5,668 | 2,042 | 170 | `0755` |
| `skills/implementaudit/scripts/detect-env.sh` | same path | existing source owner | 7,221 | 2,563 | 162 | `0755` |
| `skills/implementaudit/scripts/detect-stack.sh` | same path | existing source owner | 3,601 | 1,369 | 166 | `0755` |
| `skills/implementaudit/scripts/lane-survivor-inventory.sh` | same path | existing source owner | 2,459 | 972 | 188 | `0755` |
| `skills/implementaudit/scripts/map-pin-chain.sh` | same path | existing source owner | 2,615 | 1,126 | 168 | `0755` |
| `skills/implementaudit/scripts/read-canonical-pair.py` | same path | native_canonical_reader | 23,183 | 6,791 | 180 | `0755` |
| `skills/implementaudit/scripts/repo-state.sh` | same path | existing source owner | 22,629 | 5,937 | 162 | `0755` |
| `skills/implementaudit/scripts/resolve-durable-identity.py` | same path | existing source owner | 6,787 | 1,999 | 190 | `0755` |
| `skills/implementaudit/scripts/resolve-internal-skill.py` | same path | existing source owner | 3,945 | 1,245 | 186 | `0755` |
| `skills/implementaudit/scripts/rotate-canonical-state.py` | same path | r0039_projection_archive | 82,541 | 17,576 | 186 | `0755` |
| `skills/implementaudit/scripts/summarize-repo.sh` | same path | existing source owner | 7,281 | 2,720 | 170 | `0755` |
| `skills/implementaudit/scripts/validate-audit-spec.sh` | same path | existing source owner | 1,673 | 689 | 180 | `0755` |
| `skills/implementaudit/scripts/validate-phase.sh` | same path | phase_mutation_validator | 45,816 | 12,014 | 170 | `0755` |
| `skills/implementaudit/scripts/validate-run-root.sh` | same path | run_root_validator | 61,001 | 16,744 | 176 | `0755` |
| `skills/implementaudit/templates/PROTOCOL.md` | same path | runtime_protocol | 66,769 | 24,042 | 162 | `0644` |
| `skills/implementaudit/templates/ROADMAP.md` | same path | runtime_roadmap_template | 3,512 | 1,595 | 160 | `0644` |
| `skills/implementaudit/templates/STATE.md` | same path | runtime_state_template | 10,089 | 4,294 | 156 | `0644` |
| `skills/implementaudit/templates/THINKING.md` | same path | existing source owner | 6,380 | 2,969 | 162 | `0644` |
| `skills/implementaudit/templates/child-agent-report.md` | same path | existing source owner | 4,461 | 1,816 | 182 | `0644` |
| `skills/implementaudit/templates/context.md` | same path | existing source owner | 740 | 458 | 160 | `0644` |
| `skills/implementaudit/templates/final-report.md` | same path | existing source owner | 4,250 | 2,018 | 170 | `0644` |
| `skills/implementaudit/templates/host-notes.md` | same path | existing source owner | 785 | 477 | 166 | `0644` |
| `skills/implementaudit/templates/phase-goal.txt` | same path | existing source owner | 12,501 | 5,201 | 168 | `0644` |
| `skills/implementaudit/templates/read-only-plan.md` | same path | existing source owner | 3,188 | 1,528 | 174 | `0644` |
| `skills/implementaudit/templates/respec-impact-set.md` | same path | existing source owner | 1,129 | 570 | 180 | `0644` |
| `skills/implementaudit/templates/sidecars.md` | same path | existing source owner | 763 | 469 | 162 | `0644` |
| `skills/implementaudit/templates/tools.md` | same path | existing source owner | 997 | 546 | 156 | `0644` |

### IMPLEMENTAUDIT.skill

| Archive member | Source / projection | Owner component | Raw | Compressed | Header | Mode |
|---|---|---|---:|---:|---:|---|
| `IMPLEMENTAUDIT_INVENTORY.json` | scripts/package-contract.py::inventory_bytes | generated_inventory | 11,346 | 3,757 | 134 | `0644` |
| `IMPLEMENTAUDIT_PACKAGE.json` | package/implementaudit-package.json | package_identity | 2,941 | 912 | 130 | `0644` |
| `SKILL.md` | skills/implementaudit/SKILL.md | governor_bootloader | 20,244 | 7,898 | 92 | `0644` |
| `internal-procedures/audit-andon.md` | skills/audit-andon/SKILL.md (internal-procedure projection) | existing source owner | 2,559 | 1,264 | 144 | `0644` |
| `internal-procedures/audit-assess.md` | skills/audit-assess/SKILL.md (internal-procedure projection) | existing source owner | 1,761 | 954 | 146 | `0644` |
| `internal-procedures/audit-implement.md` | skills/audit-implement/SKILL.md (internal-procedure projection) | existing source owner | 2,266 | 1,126 | 152 | `0644` |
| `internal-procedures/audit-state.md` | skills/audit-state/SKILL.md (internal-procedure projection) | audit_state | 3,474 | 1,635 | 144 | `0644` |
| `references/audit-category-matrix.md` | skills/implementaudit/references/audit-category-matrix.md | existing source owner | 14,156 | 5,406 | 146 | `0644` |
| `references/audit-playbook.md` | skills/implementaudit/references/audit-playbook.md | existing source owner | 20,140 | 8,329 | 132 | `0644` |
| `references/canonical-state-ref-namespaces.json` | skills/implementaudit/references/canonical-state-ref-namespaces.json | canonical_ref_namespaces | 2,800 | 694 | 168 | `0644` |
| `references/canonical-state-rotation.md` | skills/implementaudit/references/canonical-state-rotation.md | r0039_projection_archive | 16,389 | 6,456 | 152 | `0644` |
| `references/child-agents.md` | skills/implementaudit/references/child-agents.md | child_evidence_continuity | 18,419 | 7,454 | 128 | `0644` |
| `references/continuity.md` | skills/implementaudit/references/continuity.md | continuity_contract | 17,175 | 6,705 | 124 | `0644` |
| `references/convergence-mode.md` | skills/implementaudit/references/convergence-mode.md | existing source owner | 8,668 | 3,509 | 136 | `0644` |
| `references/goal-format.md` | skills/implementaudit/references/goal-format.md | existing source owner | 6,895 | 2,880 | 126 | `0644` |
| `references/identity-namespaces.json` | skills/implementaudit/references/identity-namespaces.json | existing source owner | 1,265 | 493 | 146 | `0644` |
| `references/issue-ready-work-orders.md` | skills/implementaudit/references/issue-ready-work-orders.md | existing source owner | 18,210 | 6,923 | 150 | `0644` |
| `references/lean-operating-discipline.md` | skills/implementaudit/references/lean-operating-discipline.md | existing source owner | 21,792 | 8,465 | 154 | `0644` |
| `references/phase-design.md` | skills/implementaudit/references/phase-design.md | existing source owner | 20,396 | 8,311 | 128 | `0644` |
| `references/plan-lifecycle.md` | skills/implementaudit/references/plan-lifecycle.md | existing source owner | 30,905 | 11,357 | 132 | `0644` |
| `references/planning-depth.md` | skills/implementaudit/references/planning-depth.md | existing source owner | 18,762 | 7,235 | 132 | `0644` |
| `references/repo-state-comparison.md` | skills/implementaudit/references/repo-state-comparison.md | helper_reachability | 33,366 | 11,454 | 146 | `0644` |
| `references/routing.md` | skills/implementaudit/references/routing.md | existing source owner | 14,323 | 5,614 | 118 | `0644` |
| `references/sidecars.md` | skills/implementaudit/references/sidecars.md | existing source owner | 5,673 | 2,773 | 120 | `0644` |
| `references/terminology-integration.md` | skills/implementaudit/references/terminology-integration.md | existing source owner | 4,877 | 2,093 | 150 | `0644` |
| `references/transcript-contract.md` | skills/implementaudit/references/transcript-contract.md | transcript_continuity | 21,584 | 8,307 | 142 | `0644` |
| `scripts/apply-observed-mutation.sh` | skills/implementaudit/scripts/apply-observed-mutation.sh | existing source owner | 56,144 | 11,405 | 144 | `0755` |
| `scripts/canonical_hot_projection.py` | skills/implementaudit/scripts/canonical_hot_projection.py | r0039_projection_archive | 57,891 | 13,306 | 146 | `0755` |
| `scripts/check-authorization-binding.sh` | skills/implementaudit/scripts/check-authorization-binding.sh | existing source owner | 17,469 | 6,010 | 152 | `0755` |
| `scripts/check-closure-surface.sh` | skills/implementaudit/scripts/check-closure-surface.sh | existing source owner | 94,842 | 21,941 | 140 | `0755` |
| `scripts/check-duplication-parity.sh` | skills/implementaudit/scripts/check-duplication-parity.sh | existing source owner | 5,208 | 1,755 | 146 | `0755` |
| `scripts/check-evidence-anchor.sh` | skills/implementaudit/scripts/check-evidence-anchor.sh | existing source owner | 43,368 | 10,063 | 140 | `0755` |
| `scripts/check-handoff-packet.sh` | skills/implementaudit/scripts/check-handoff-packet.sh | existing source owner | 8,912 | 3,072 | 138 | `0755` |
| `scripts/check-lesson-lift.sh` | skills/implementaudit/scripts/check-lesson-lift.sh | existing source owner | 11,417 | 3,620 | 132 | `0755` |
| `scripts/check-respec-impact-set.sh` | skills/implementaudit/scripts/check-respec-impact-set.sh | existing source owner | 6,560 | 2,129 | 144 | `0755` |
| `scripts/claim-run-rotation.py` | skills/implementaudit/scripts/claim-run-rotation.py | claim_run_authority | 93,366 | 18,251 | 134 | `0755` |
| `scripts/claim-run.sh` | skills/implementaudit/scripts/claim-run.sh | claim_run_authority | 17,368 | 5,063 | 116 | `0755` |
| `scripts/custody-append.sh` | skills/implementaudit/scripts/custody-append.sh | existing source owner | 5,668 | 2,042 | 126 | `0755` |
| `scripts/detect-env.sh` | skills/implementaudit/scripts/detect-env.sh | existing source owner | 7,221 | 2,563 | 118 | `0755` |
| `scripts/detect-stack.sh` | skills/implementaudit/scripts/detect-stack.sh | existing source owner | 3,601 | 1,369 | 122 | `0755` |
| `scripts/lane-survivor-inventory.sh` | skills/implementaudit/scripts/lane-survivor-inventory.sh | existing source owner | 2,459 | 972 | 144 | `0755` |
| `scripts/map-pin-chain.sh` | skills/implementaudit/scripts/map-pin-chain.sh | existing source owner | 2,615 | 1,126 | 124 | `0755` |
| `scripts/read-canonical-pair.py` | skills/implementaudit/scripts/read-canonical-pair.py | native_canonical_reader | 23,183 | 6,791 | 136 | `0755` |
| `scripts/repo-state.sh` | skills/implementaudit/scripts/repo-state.sh | existing source owner | 22,629 | 5,937 | 118 | `0755` |
| `scripts/resolve-durable-identity.py` | skills/implementaudit/scripts/resolve-durable-identity.py | existing source owner | 6,787 | 1,999 | 146 | `0755` |
| `scripts/resolve-internal-skill.py` | skills/implementaudit/scripts/resolve-internal-skill.py | existing source owner | 3,945 | 1,245 | 142 | `0755` |
| `scripts/rotate-canonical-state.py` | skills/implementaudit/scripts/rotate-canonical-state.py | r0039_projection_archive | 82,541 | 17,576 | 142 | `0755` |
| `scripts/summarize-repo.sh` | skills/implementaudit/scripts/summarize-repo.sh | existing source owner | 7,281 | 2,720 | 126 | `0755` |
| `scripts/validate-audit-spec.sh` | skills/implementaudit/scripts/validate-audit-spec.sh | existing source owner | 1,673 | 689 | 136 | `0755` |
| `scripts/validate-phase.sh` | skills/implementaudit/scripts/validate-phase.sh | phase_mutation_validator | 45,816 | 12,014 | 126 | `0755` |
| `scripts/validate-run-root.sh` | skills/implementaudit/scripts/validate-run-root.sh | run_root_validator | 61,001 | 16,744 | 132 | `0755` |
| `templates/PROTOCOL.md` | skills/implementaudit/templates/PROTOCOL.md | runtime_protocol | 66,769 | 24,042 | 118 | `0644` |
| `templates/ROADMAP.md` | skills/implementaudit/templates/ROADMAP.md | runtime_roadmap_template | 3,512 | 1,595 | 116 | `0644` |
| `templates/STATE.md` | skills/implementaudit/templates/STATE.md | runtime_state_template | 10,089 | 4,294 | 112 | `0644` |
| `templates/THINKING.md` | skills/implementaudit/templates/THINKING.md | existing source owner | 6,380 | 2,969 | 118 | `0644` |
| `templates/child-agent-report.md` | skills/implementaudit/templates/child-agent-report.md | existing source owner | 4,461 | 1,816 | 138 | `0644` |
| `templates/context.md` | skills/implementaudit/templates/context.md | existing source owner | 740 | 458 | 116 | `0644` |
| `templates/final-report.md` | skills/implementaudit/templates/final-report.md | existing source owner | 4,250 | 2,018 | 126 | `0644` |
| `templates/host-notes.md` | skills/implementaudit/templates/host-notes.md | existing source owner | 785 | 477 | 122 | `0644` |
| `templates/phase-goal.txt` | skills/implementaudit/templates/phase-goal.txt | existing source owner | 12,501 | 5,201 | 124 | `0644` |
| `templates/read-only-plan.md` | skills/implementaudit/templates/read-only-plan.md | existing source owner | 3,188 | 1,528 | 130 | `0644` |
| `templates/respec-impact-set.md` | skills/implementaudit/templates/respec-impact-set.md | existing source owner | 1,129 | 570 | 136 | `0644` |
| `templates/sidecars.md` | skills/implementaudit/templates/sidecars.md | existing source owner | 763 | 469 | 118 | `0644` |
| `templates/tools.md` | skills/implementaudit/templates/tools.md | existing source owner | 997 | 546 | 112 | `0644` |

## Evidence identities

| Input measurement | Bytes | SHA-256 |
|---|---:|---|
| `MEASUREMENTS.json` | 447,974 | `21f7d03c3927caff62cf3b4b6bf66ddeb4f3ff8099acb22bd43a572db72a9243` |
| `ORIGINAL_EXACT_PACKAGE_MEMBERS.json` | 37,346 | `3553d800a7be9ade0cc9aa56d627e1972abe7a7ddb3ea5c7e6fa078c999e7f4f` |
| `ORDERED_PATCH_MANIFEST.json` | 37,301 | `2a8d53b93f55e7383652392c116bdc9308f2aa4d870ee82f0ff453e858cd033e` |

This reconciliation reads existing measurement JSON and ZIP inventory/member data. It performs no compression, package rebuild, source mutation, installer execution, model calls, campaign operation or historical-bank rerun. Arithmetic and exact final byte/mode comparisons are complete; portable engineering exhaustion and LR10 disposition remain outside this report.
