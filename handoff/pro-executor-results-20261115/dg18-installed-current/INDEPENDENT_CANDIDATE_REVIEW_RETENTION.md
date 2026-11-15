# DG18 installed-current: retention correction receiving

Disposition: **PASS — exact-candidate source/static review only.** The two blocking findings from the initial review are addressed. This is evidence for Root's publication decision, not an operation grant, a hosted success result, independent runtime receiving, or original DG18 acceptance.

Reviewer: `/root/dg17_recovery`. Scope: only the retention correction against the frozen candidate below. The source/archive/installer/lifecycle review was not repeated. No source test, package build, owner invocation, model/native action, protected operation or replay occurred during this follow-up.

## Final frozen candidate

Base remains `080cc0e29bd6382b0c31f3f69e9ad2f8d42991b2`; product source remains exact `775d6a0add0a1edcbc7f6cf5ccd68d350757fe8a` with the existing retained archives.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/dg18-source-qualification.yml` | 11164 | `e62320cad3b5f8a960e47658c3fbe56afe0c8d56ae5b6a211d31caa6342676fe` |
| `handoff/pro-executor-results-20261115/dg18-installed-current/qualify.py` | 21241 | `006b0e06e25cb5095028f874d6d6897de39a38e00c7506dbb041b0d0614873a1` |
| `handoff/pro-executor-results-20261115/dg18-installed-current/README.md` | 3854 | `394f23c5d415104aa2dffd4357ffc5e3b95bf60974d682eb788fc9ca8d07d0b5` |

Each size and hash was independently recomputed. The workflow/README are unchanged from the author's retention correction. The final driver differs from reviewed intermediate `308e0221...` only in one status literal: existing captures now say `EXISTING_CAPTURE_RETAINED_COMPLETENESS_UNVERIFIED`. Reversing exactly that literal reproduces the intermediate SHA-256, so no unrelated change is hidden in the last update.

## Findings received

**R1 — Addressed.** `include-hidden-files: true` is set on the final upload step. Its path remains exactly `${{ env.DG18_INSTALLED_OUTPUT }}/evidence/**`. This retains the copied `.claimed` and `.controller` files without expanding publication to the subject repository's `.git`, user homes, other installations or unrelated runner paths.

**R2 — Addressed.** The original `FAILURE-<step>.json` is written first. The new failure-only capture visits each of the four already-created, isolated subject namespaces and accepts at most one existing task root per namespace. It never invokes a claim/currentness consumer, retries the failed operation, reconstructs missing files or assigns authority from a directory name. Captures retain the actually observed files, including hidden claim/controller records. Absent roots remain explicitly absent; aliases, excessive populations and unstable captures receive an unverified disposition. An overall capture failure is recorded separately as `RETENTION_FAILURE-<step>.json`, preserving the primary failure record.

The final literal correction also closes a narrower false-success edge found during this receiving: an interrupted `copytree` may leave its destination present. Presence is now treated as preserved bytes with completeness unverified, not as proof that an earlier successful capture occurred. No existing partial capture is overwritten or promoted.

The README now describes the same bounded, non-authoritative retention behavior. Captured files do not prove a failed effect's outcome or currentness. Ordinary source/currentness claims and all N1/native/OR/C02/W-FULL/original-acceptance ceilings are unchanged.

## Preserved history and limits

The initial `INDEPENDENT_CANDIDATE_REVIEW.md` remains byte-identical: 9914 bytes, SHA-256 `50aecdea520e3bcd9db0956bb818d534a9e98c860780ce3d5db158d170637633`. Its original GAP-REVISE and exact initial pins are preserved.

The author's `RETENTION_CORRECTION_CHECKS.json` reports hidden-file capture and alias-refusal controls at intermediate driver `308e0221...`; that record remains attributed to that exact source. This reviewer did not replay those controls. The final source inspection, hash readback, narrow literal comparison, AST parse and restricted-upload YAML readback support the present source/static disposition. Actual hosted execution and distinct receiving are still required before reporting an installed-runtime result.
