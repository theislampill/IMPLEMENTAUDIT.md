# DG18 native peer binding: bounded read-only finding

## Disposition

**GAP: a current repository source-overlay binding is stale.** At source
`775d6a0add0a1edcbc7f6cf5ccd68d350757fe8a` and its published memory-only
successor `75e7bc623dad7ec7e00e7ecd8b264ed1d26250f9`, the native-runtime
manifest describes a different source-owner body from the file at its declared
path. This is not merely historical evidence: the documented materializer and
the current materialization regression compare the physical bytes against this
row before copying them. This finding was established by immutable Git reads,
source inspection and literal-data comparison; no owner, native operation or
pending-process suite was invoked.

## Exact lineage

Path in every commit below:
`source-peers/native-runtime/skills/implementaudit/scripts/compaction-source-owner-codex-app.py`.

| Exact source | Bytes | SHA256 | Git blob |
| --- | ---: | --- | --- |
| `205aeab7c93299b0666b261485ab5658d8e183de` | 185531 | `5bb21eed89945a8da97857f980b1f85a06dc07df47b25475b9173f23e82ce8f8` | `21ff4e4caa1a05ec3c592ef84a062a23c2dfe0f8` |
| `a297957be11feb494c0ec467235794a1e0c54751` | 185531 | `5bb21eed89945a8da97857f980b1f85a06dc07df47b25475b9173f23e82ce8f8` | `21ff4e4caa1a05ec3c592ef84a062a23c2dfe0f8` |
| `4dad9180518c76bfafea8166ce3add3e00cf5748` | 196162 | `83670fe9d57e4c52ef25982b8bf7baf2895d6133e5af3e103e2de46ed31e02d5` | `73902365c18c967fa038c0d57ad4744b1e2fbe30` |
| `775d6a0add0a1edcbc7f6cf5ccd68d350757fe8a` | 196162 | `83670fe9d57e4c52ef25982b8bf7baf2895d6133e5af3e103e2de46ed31e02d5` | `73902365c18c967fa038c0d57ad4744b1e2fbe30` |
| `75e7bc623dad7ec7e00e7ecd8b264ed1d26250f9` | 196162 | `83670fe9d57e4c52ef25982b8bf7baf2895d6133e5af3e103e2de46ed31e02d5` | `73902365c18c967fa038c0d57ad4744b1e2fbe30` |

The manifest row at lines 106–127 still says 185531/5bb21eed. Its original
preimage metadata is historical and must be retained. The current file's delta
against the retained 205 donor is 191 additions and 16 deletions. It introduces
the explicit `claim-cli-controlled-nonprotected-c02-v1` profile and acquisition
path. Commit 4dad is a root publication commit, not evidence that these donor
commits are its Git ancestors. Its retained independent source review names
the reviewed candidate `0f591704c94c7dcd7bcda1c0cc8c229f24bf0613` and the
196162/83670fe9 body explicitly:
`handoff/pro-executor-results-20261115/dg18-c02-cli/INDEPENDENT_SOURCE_REVIEW.json`.
No missing ancestral commit or missing original acceptance is inferred.

## Actual consumers and meanings

Line numbers in this section refer to exact source 775.

| Consumer | Exact relation and consequence |
| --- | --- |
| `source-peers/README.md`, native-runtime composition and materialization instructions | All declared members must be copied with exact bytes and modes; source transport does not confer native admission. The stale current row violates that source contract. |
| `tests/composite-source-cases.py:1402–1415` | `test_documented_peer_materialization_supplies_exact_episode_owner_sibling` reads each actual peer and compares its byte count and SHA256 to the manifest before copying. The stated 185531/5bb relation cannot hold for actual 196162/8367. This is a static predicted failure, not a claimed test run. |
| `tests/cognition-pending-durability.py:768–877,899–906` | `source_pins(repo)` hashes the four current physical peers. The unchanged closed table has 18 historical four-file profiles. Its latest tuple requires source-owner 5bb; the actual 8367 tuple is absent and is refused at line 877 before process controls. Literal-data comparison confirmed that substituting only the exact old owner hash selects the existing tuple. |
| `tests/cognition-pending-durability.py:341–392,468–480` | The existing non-admitted refusal fixture archives the frozen source and checks every manifest entry at lines 374–379 before the source-registration and reserve refusals. The stale row would independently block this materialization. Its old four-file tuple must select the actual old body, not just relabel the new body. |
| `tests/composite-source-cases.py:2258–2264` | The fixture binding test currently hashes the current peer yet expects the old 5bb checkpoint. It needs to identify the historical fixture explicitly. The later historical and mixed-profile rejection controls retain their meanings. |
| `skills/implementaudit/scripts/claim-run-rotation.py:1594–1615` | `_h0_mechanical_source_template_v1` normalizes only `MECHANICAL_SELECTION_PIN` and requires the old 5bb template. This is an intentional exact historical mechanical gate. It must not be widened or relabeled. `_private_native_input_selection_v1` calls it at 1646, so arbitrary use of the newer body on that older path is not admitted. |
| `skills/implementaudit/scripts/claim-run-rotation.py:1588,2766–2812` | The separate existing C02 path explicitly accepts current 8367 in the reviewed template set and binds the physical selected owner and provider. `c02_owned_operation_v1` does not use the old mechanical normalization as its C02 template selector. |
| `fixtures/canonical-state-rotation/c02_cli_source_test.py:110–125,207–223` | The existing CLI control physically materializes current source with its one selected provider literal and calls the newly added `acquire_selected_cli_c02_interval_v1`. Replacing the live peer with the old donor would remove that implementation. The control's constructed authority is not original C02 acceptance. |

The other three current members of the pending fixture's exact historical
tuple are unchanged: pending `729f7eb108b30647bf62e19d71be4cd10e41486af020a6dc69b8aa6295d8aee5`,
observation `a68145e62a0a81dfb02fc48f72cefaf3740e499bf6b85bd70f5d30cc64a038c1`,
and host binding `f024cd50b4e5cdd3b93f16fe1d0489952a534a0a5f880c842c14afc897ac2bc7`.
The existing `test-support/native-preparation-history` owner is the different
133273/8d6e51fc body and cannot satisfy the 185531/5bb dependency.

## Smallest truthful correction, authorized separately after this finding

Use an isolated successor of published 75e7. Correct the current manifest row
to the actual 196162/8367 body and record its actual C02 source lineage. Retain
an exact 185531/5bb donor from the available 205/a297 Git blob under explicit
test support. Select that donor only in the existing historical, non-admitted
pending refusal fixture, recording its physical path and materialized bytes.
Keep `source_pins()` truthful about current source, keep all 18 refusal profiles
and the mechanical owner gate byte-for-byte semantically unchanged, and make
the existing composite test select and name the historical fixture explicitly.

The current manifest population must still be verified before the fixture's
separately recorded historical substitution. The current C02 implementation
stays 196162/8367. This correction is repository-only; it requires no package
rebuild if the already reviewed package inputs remain identical. It grants no
native replay, original14 acceptance, new C5 profile, retry, source-owner
selection or original acceptance. The memory correction and all historical
failures remain preserved at their actual scopes.

Rollback is discarding this new detached candidate; neither the published
75e7 source nor any live operator is edited. Verification is limited to the
existing focused binding/materialization regression and exact source/diff
closure. No full pending-process or native suite is authorized by this finding.
