# DG16 Task 1 R2 inert source return

This prospective metadata derivation binds **190 public input roles totaling 5,999,010 bytes**. It reuses 189 exact historical input identities and binds the reviewed Task 1 R2 source as the prospective generator. The lost historical 50,292-byte generator retains its own missing identity. The new manifest binds only the state verified here. Source adoption, physical receiving, the complete after-basis, protected readiness and original acceptance remain open. [Results45 exact-input index](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261122-45-recovery3/CUSTODY_INDEX.json), [Task 1 R2 decision and scope](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261122-46-task1-r2/ROOT_TASK1_R2_ADJUDICATION_G0004.json).

## What was verified

- Reassembled the inert input tree in memory from the exact published Git tree and pinned archive parts. Each of the 190 manifest rows binds its logical role, byte count, SHA-256 and public locator. Archive locators use ordinal indices rather than extracting paths or writing member bodies. The bounded scan inspected 23 archive groups, 30 readable containers and 7,077 member entries. Five format reads refused. All expected retained roles matched despite those refusals.
- Exercised the original R2 pure descriptor and location-role checker using a POSIX path model. The 190 inputs fit the exact three grouped inventories and four singleton roles. The native Windows path implementation refused the POSIX literals during initial testing, so the harness checks the POSIX grammar with `PurePosixPath` and never calls the filesystem receiver. No physical tree or destination was created.
- Ran 26 tests from the exact R2 projection and repair suite and verified the actual runtime's inherited compiler flag by inspecting an inert compiled code object. Reproduced the five published historical projection bodies byte-for-byte, totaling **92,916 bytes**, using the pinned plan, actual `project_exact` implementation and exact archived full-before inputs. Only Task 1 R2 and its selected tests were executed. Archived source owners and projections remained input data. [Pinned Task 1 R2 source and tests](https://github.com/theislampill/IMPLEMENTAUDIT.md/tree/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261122-46-task1-r2/test-support/g132-original-joint-source).

## First prospective after-basis refusal

Four current-source families yielded bounded static projection digests. For compose, the old recipe classifies `W` and `templates` as both selected roots and supplied names. R2 refused that recipe. The pinned runtime's compose branch supplies both names, so the prospective probe treats them as supplied only. That probe derives 2,872 bytes in memory and records its digest. The old recipe and its historical projection remain unchanged.

The current G3 basis refuses at `validate_public_scope → scope_basis → Path`. The exact published G3 source declares the root at line 1522 and the dependent declaration at line 391. Its source file imports `Path`; the pinned runtime is a separate namespace constructed before compiling the projection. The G3 branch at line 269 adds only `current_original_scope_body`, and the R2 resolver refuses this unbound dependency. Seven other G3 roots derive individually. That count cannot satisfy the complete family. [Exact G3 source](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261122-45-recovery3/source-snapshots/qualification/dg16-r5-g1-hosted-episode/g3_receiving.py#L391), [exact runtime namespace owner](https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/6431a1d1e067ab37e4f461caa4a61890d69e7c14/handoff/pro-executor-results-20261115/continuing-execution-20261122-45-recovery3/source-snapshots/test-support/g132-original-joint-source/owner-sources/source/current_pro_interfaces.py#L259-L276).

The four derived families preserve the source-ordered declaration groups. All four have AST differences relative to the old projections. Root and supplied selections match except for compose's two supplied-only names. The evidence records the exact discrepancy and withholds semantic equivalence and adoption for every family.

| Family | Changed declaration ASTs |
| --- | --- |
| compose | `SOURCE`, `TREE` |
| profile | `G1_HOST_PROFILES`, `select_g1_host_profile` |
| proof | `SOURCE`, `SOURCE_BYTES`, `SOURCE_FILES`, `SOURCE_PARENT`, `TREE`, `bounded_g1_facts`, `validate_first` |
| run | `SOURCE_COMMIT`, `SOURCE_TREE` |
| G3 | Comparison withheld because the complete projection refused |
The first code decision belongs to the G3 runtime and source owners. Establish a reviewed binding for the required dependency or demonstrate an equivalent admitted source path that supplies it. Then rerun the full declared static G3 closure with the refusal preserved. The source-adoption review still needs a complete after-basis and physical input receiving under the applicable policy. The new metadata contains no projected executable bodies and grants no permission to invoke them.

## Reproduce the manifest

Run this read-only command with the exact results commit available in the Git object database. It writes the generated JSON to stdout. Compare the bytes to the committed manifest. On the Windows check, Python 3.11.9 produced identical output twice.

```powershell
python -I -B handoff/sol-dg16-20261122/task1-inert-source/derive_inert_manifest.py
```
