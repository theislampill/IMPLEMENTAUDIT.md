# Independent formatter assessment

## Identity and scope

- Reviewer: `/root/g2_independent`.
- Date: 2026-11-18 UTC.
- `authoring_context_reuse: no`.
- Host/self-reported model label: **GPT-6 Astra Pro**; exact provider deployment ID is not exposed.
- The parent reports a `fork_turns=none` spawn. I did not implement or modify this formatter or its repository test file.
- Role: ordinary independent technical review, with no acceptance, launch, publication, readiness, or audit-closure authority.

## Result

**No blocking defect was found in the reviewed formatter for its declared local formatting scope.** This is a **PL4 structural-validation finding**, not delivery of an actual live G2 review. No `INDEPENDENT_REVIEW.json` for an actual G2 run is issued by this assessment.

Reviewed files under `/workspace/scratch/095d3235c921/implementaudit/handoff/dg16-pro-executor-20261118/`:

| File | SHA-256 |
|---|---|
| `make_control.py` | `71e7567639090e3760105330f1862c521d64de8287b25cf1b943030e18a71bb9` |
| `test_make_control.py` | `94c87e651e9747dc0deee5ac95d523e7a758ffcc543269a047dc627ba94b723b` |

The original validator was obtained from workflow commit `d2f04874c549816141de002f9baec73dbc9d06fd`, path `qualification/dg16-r5-full-g2/live_control.py`, and checked against SHA-256 `444b8d66f6c554fe1df3490b9db944a8bc5f8371b565f9377a07d168adc5e517`.

## Findings about implementation behavior

`build_payload` receives independent-review bytes as an explicit argument. It parses those bytes to obtain the reviewer, but places the **original bytes** into the output payload and computes both root and control descriptors from those same bytes. It does not reserialize, rewrite, or invent the review. The original validator subsequently checks the full review against its strict schema and request bindings.

The root decision has no default. It must equal `CONSUME_AT_DECLARED_SCOPE_SUBJECT_TO_CLOSING_READBACK`, and the CLI requires the corresponding argument. Root output sets `automatic_full_G2_award` and `original_source_or_product_limits_changed` to false. The original validator also requires the exact original designated-successor string when reviewing this workflow version. Omitting or changing it does not create consumable output.

The proof input must match the request's actual byte count and digest. Repository, control branch, run ID, and control path are checked before serialization. A restricted run-ID expression prevents traversal or separators in the constructed control path.

The production CLI supplies `time.time()` to the build and then revalidates against a fresh real wall-clock reading immediately before local output creation. It offers no historical-clock CLI option. The pure Python API does accept a caller-supplied `now` to support explicit synthetic tests; callers of that API remain responsible for using a real clock for actual work.

Output creation is exclusive: a fresh directory is required, and each of the three files is opened with `xb`. The function writes only the fixed filenames, flushes and fsyncs their contents, and refuses existing output rather than overwriting it. An interrupted write can leave a partial local directory, which also prevents a silent overwrite. The utility does not publish files, create a Git commit, launch a workflow, or extend a deadline.

## Verification performed independently

I read the complete formatter and test file, then ran the existing six focused tests myself with Python bytecode writes disabled. All six completed successfully:

1. External review bytes survive and the original validator accepts the synthetic conforming tuple.
2. Absent or rejected review inputs cannot become a PASS payload.
3. Exact expiry and absent root decision are refused.
4. Substituted proof bytes are refused.
5. A wrong validator digest is refused before loading.
6. Output creation is exclusive, exact, and preserves review bytes on disk.

I additionally exercised eight independently selected adverse cases against the actual original validator. These were ephemeral synthetic tests, not modifications to the implementation or repository tests:

| Additional control | Observed refusal |
|---|---|
| Complete review changed to `decision: BLOCKED` | `ACTUAL_INDEPENDENT_LIVE_REVIEW_REQUIRED` |
| Complete review containing an unresolved blocking finding | `ACTUAL_INDEPENDENT_LIVE_REVIEW_REQUIRED` |
| Complete review using an excluded current author | `ACTUAL_INDEPENDENT_LIVE_REVIEW_REQUIRED` |
| Duplicate review JSON key | `LIVE_CONTROL_DUPLICATE_KEY` |
| Nonfinite JSON value | `LIVE_CONTROL_NONFINITE` |
| Traversal run ID | `SELECTED_CONTROL_LOCATION_MISMATCH` |
| Incorrect successor | `LIVE_CONTROL_BINDING` |
| Production CLI operating on an expired synthetic request under the real clock | `ACTUAL_REVIEW_WINDOW_EXPIRED`; no output directory created |

Every PASS literal in the supplied unit tests is expressly marked synthetic non-acceptance data. I did not create a purported historical independent G2 review to conduct these checks.

## Material limits and operator responsibilities

The validator path and its expected hash are trusted operator inputs. `load_validator` proves that supplied file bytes match the supplied hash, but it does not independently authenticate that hash against `request.workflow_commit`. The operator must establish that binding from the selected workflow source. This was done explicitly for this review; substituting the current checkout's 300-second validator would be wrong for the historical 3,600-second request.

The formatter performs protocol formatting and invokes the selected validator. It does not establish the truth of the proof, the semantic adequacy of a review, current private-input retention, or independent authorship. It cannot turn an unsuitable review into a suitable one; the reviewer and root remain responsible for those judgments. The CLI argument expressing a root choice is an operator action, not an independently authenticated root signature.

There is no publication or remote-receiving evidence in these tests. The original `hold` checks still must observe the correct remote branch, sole workflow parent, exact three-file-only tree delta, ordinary blob modes, stable head, live clocks, and durable one-shot reservation. Actual post-review source/runtime/raw-census/currentness closure must still happen in the original job.

A test harness can load the unchanged original validator and adapt only its branch/remote globals for an explicitly synthetic rehearsal. Such adaptation and the actual transport used must be recorded. A harness calling the pure formatter must supply real `time.time()` for a real-time rehearsal; the CLI cannot accept a rehearsal branch that differs from the selected validator's branch without an explicit test adaptation.

This assessment is bound to the hashes above. Changes to the formatter, selected validator, test domain, or input semantics require assessing the material change before carrying this result forward. Full G2, original acceptance, protected custody, M2, and audit closure remain unawarded.
