# DG17 focused corrected-delta review

Report state: FINAL

## Reviewer attestation

Reviewer: `/root/dg16_g2`. Author: `/root/dg17`. Authoring-context reuse: no. This follow-up consumes the prior independent findings and the frozen corrected files; it does not reuse the author's planning context. The author's focused-check result was read as reported evidence, and the changed behavior below was independently checked with reviewer-owned inert inputs.

Review scope: F1–F4 corrections, immutable source/file modes, original subject identity and updated parent receipt metadata. No repeated full rehearsal, original subject command, controller mutation, hosted execution, model invocation, API request, protected replay or remote write. Authority and original acceptance: none.

Parent supplied receipt `refs/implementaudit/continuity-receipts/pro-dg16-18-continuation/G000A@859e5a787c04803771a4ea04c1cfad338ee22644` was read and its ref object independently confirmed. Parent controller/claim remain `pro-dg16-18-continuation` / `3f6e3e3f849ae3b9b767607bce41c36b`.

## Disposition

**PASS for the reviewed ordinary transport source delta.** F1–F4 are resolved without a broader source change. No remaining substantive source blocker was found in this focused review. Root retains publication, actual hosted execution, actual child dispatch/return, rederivation and original receiving decisions.

This replaces the prior GAP-REVISE readiness disposition for these corrected files only. The prior report and all original/failing evidence remain retained; no historical result is rewritten.

## Exact corrected freeze

| File under `/workspace/scratch/211aae41ab24/dg17/` | Bytes | SHA256 |
|---|---:|---|
| `hosted_governed.py` | 42723 | `e8ba9262628ebc623f8a8a28369341151e0f6f39e06546a7efbc6d6c0ca0ccdd` |
| `request.json` | 26532 | `16343f04434df2cc3015c5f49ff6cb638490aa2225b59c6a4b6e83006187209c` |
| `dg17-governed-l4.yml` | 2461 | `df9673c84d65c61b38a698fdca8f68efb2ae9f81e9d0ad0662ab5cfe9cb3fca5` |
| `REVIEW_FIX_DIFF.patch` | 11353 | `c71741007d84f5937692e07fbc24c5195deee29912efc3539f48eb60cfa4964e` |

The retained predecessor script/request/workflow match the original reviewed hashes `22289bd0...`, `a9796da6...`, and `df9673c8...` in the prior report. The workflow is byte-unchanged. AST comparison limits changed Python definitions to `run`, `prepare`, `wait_mail`, and `finalize`, plus the `nullcontext` import. The request changes only the four DG18 mode fields and G0009-to-G000A parent receipt metadata; package, source, subject, challenge and receiver bindings remain unchanged.

## Findings resolved

| Finding | Corrected behavior | Independent focused check |
|---|---|---|
| F1 | The real comparison command now requires exit 1, exactly 266 stdout bytes with SHA256 `8b1b08cef34ced774fb20cb696a79a51b1a76e6f2adc953a084e8d751691bf0a`, and empty separately captured stderr before L4 registration. | Original-signature mock accepted; unrelated exit-1 output and extra stderr refused; all raw streams retained. The signature was reread from the original PREPARER observations, not inferred from a new run. |
| F2 | All six copied DG18 bytes, blobs and modes now match the immutable 6b source tree. | Read-only Git tree comparison plus physical file modes/hashes. All six match; all 16 original subject files remain unchanged. |
| F3 | Observed head/commit metadata is saved before parent/path refusal; exact expected-path authenticated raw bytes and their hash/join metadata are saved before parsing. | Wrong parent/path retain metadata and make no blob fetch. Malformed expected-path JSON retains metadata and exact raw bytes, then refuses. No API call occurred. |
| F4 | Unverified owned-process records produce explicit uncertainty, retain the task, mark the archive nonterminal, set `host_custody_terminated=false`, and refuse finalization. | Inert unverified fixture is retained with no termination claim; inert all-absent fixture is removed with the corresponding observed cleanup result. No process was started or killed. |

Original DG18 commit: `6b353b48b2fc8a6de0c6223f48d341c484c98191`; tree `92da6bf5f9d2d8d7ea723b56f2e99c838a9d984b`. Publish `claim-run.sh`, `claim-run-rotation.py`, and `validate-run-root.sh` as Git mode **100644**, and `rotate-canonical-state.py`, `canonical_hot_projection.py`, and `canonical_custody.py` as **100755**. Byte-only publication is insufficient because the admitted request checks these modes.

Independent checks: `delta/INDEPENDENT_DELTA_CHECKS.json`; checking source: `delta_inert_review.py`. These are explicitly inert source checks, not original observations or acceptance.

## Publication handoff

`request.review` intentionally remains `{status: PENDING, evidence: ""}` in this reviewed freeze. Root can insert this PASS report's exact reference/hash into that metadata and record the resulting final request hash in the publication/launch record. The production workflow, transport source, subject bytes, source-owner bytes and exact modes should remain as reviewed.

The prior broader review's unchanged boundary conclusions still apply. Actual eligible-host admission is still unobserved by this reviewer. The transport itself neither authenticates model provenance merely from strings nor awards original acceptance; Root must supply and independently receive actual calls/returns. Native Stop, subject repair/full P07 acceptance, whole DG17, and DG18 native-context results remain outside this source PASS. G132 remains UNKNOWN_NO_REPLAY.

PASS
