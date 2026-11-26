# Independent final source composition review — pass with findings

The exact composed source at commit `0b9b5a16bd87c54e61e5084f3b3b6895d3f29410`, tree `1839064374ba7a064a09db12123093a608596ecc`, sole parent V21 `338c4c36d2ac95ca24345bc92fe8c53d66eaa15d`, passes this bounded independent composition and pin review. No open source defect was found in the reviewed delta. The reviewer authored no subject changes and performed no hosted/native/canonical launch.

## Exact composition

Relative to accepted fixture repair `998d15881b586c77954558d9c6fa79cac3e37f82`, there are seven changed files. The qualifier and two materialization test files exactly match independently reviewed linked correction `44600e638c855fea90173a45e746468b4db6e78b`, including Git modes. The other four changes are exactly one literal pin replacement each in the C5 loader, hosted setup consumer, selected-source fixture helper, and canonical02 source control. No additional function or guard change occurs. The observer fixture file remains exactly 167,637 bytes with SHA-256 `f1129171eb638d9ecc2b972541bd25a29766064943915cf54817a0f2a0b4c1eb`; COLD-F1 remains resolved.

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| Current qualifier | 279,440 | `b5a3fb17b1be72ead4168d965403d93a1127c2367a7c54876cc89bebe6c760e0` |
| Current C5 loader | 81,096 | `15e8a7b7f9bf26e22c0d9bc8f1ec6313f4eba46e2a94b47326c0dc56f6d376a4` |
| Retained V21 qualifier | 271,749 | `304cd722d27601ae5144605602ea0f9b814420a8fe1e7d8ba4b63bf32d9d4c8e` |

The new selection loads the actual current qualifier; the historic Stage B selection loads the exact retained V21 qualifier. Both engines load and check successfully. Hosted setup and the selected-source fixture use the actual refreshed loader pin. All 172 historical C5 constant ASTs and evaluated values remain identical to V21. All 39 historical fixture paths retain identical bytes and modes. The finite new runtime tuple still contains exactly 12 selector paths and matches the retained actual canonical02 observation; the observation remains unqualified and supplies no admission award.

## Physical source and retained populations

Every tracked physical byte, ordinary-file shape, single link, Git blob, and file mode was checked against the exact tree: 1,989 files totaling 175,634,600 bytes, with 15 changed paths from V21. The full census is retained in `SOURCE_CENSUS.json`; its compact canonical-row SHA-256 is `5d046d8a3e8e6665cb7bb8819eca519f84f64979cf85b85c5ffb7efb7659a3d3`.

The 89 native-source members and 79 package members were derived again from the actual retained V21 manifest/applicability and package topology. Every physical byte, mode, and Git blob matches V21. Their unchanged canonical row digests are `94a55590b2e4b7034c6f6b7be017546ba4830c5dde4651a7b72542162e5aa831` and `adb80e893640052cf24598456662b61a799cc53011eb69a25843c7501cfef135`, respectively.

Initial inspection found six ignored generated cache files despite the proposal's initial clean flag. The parent removed those exact generated files and clarified the proposal. The reviewer independently verified empty Git status including untracked and ignored files before and after its checks. No committed source changed, and the reviewer removed nothing.

## Validation and scope

The reviewer independently reran the four canonical02 source controls and the hosted current-reader/retained-compiler control: five pass, zero skips. These checks exercise actual source loading and pin consumers without native dispatch. Prior independent leaf tests (five materialization, eight image-limit, nine ELF) and observer-custody checks remain applicable through exact byte composition; their original receipts are linked in the machine-readable review. The repaired positive observer fixture invokes the actual image builder, so its generated manifest follows the composed qualifier's materialization policy.

The actual C5 executor and its `COMPOSED_SOURCE_PREFIX_23_V1` owner remain unchanged. Its file limit is 64 MiB. The new leaf corrections remain confined to `CONTROLLED_TASK_LEAVES_V1`: 8 MiB payload file limit, finite construction at most 32 MiB, exact materialization policy/dispatch binding, and the previously reviewed bounded pre-effect ELF closure. The source composition introduces no general fallback or expanded executable acceptance.

Disposition: **PASS_WITH_FINDINGS**, limited to exact source composition, retained-byte preservation, and pin/consumer consistency. No publication or operation grant, canonical C5 runtime admission, native campaign award, original-case award, whole completion, programme acceptance, or AppArmor causal conclusion follows. The next final operator must bind the remotely published source identity and these refreshed exact pins and receive its own review.
