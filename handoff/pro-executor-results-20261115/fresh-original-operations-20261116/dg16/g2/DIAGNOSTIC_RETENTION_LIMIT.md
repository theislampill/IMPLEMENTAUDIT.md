# G2 nonzero receiving: exact retained diagnostic and limits

Read-only assessment by `/root/g2_receiving`, authority **NONE**, of the existing owners in final source tree `3cb0c2a425cc6ae5c374c7f538a845649aacbeb7`. No new test, schema, transport, source edit or computation was performed.

## Answer

The qualified correction retains **named normalized scopes and bounded typed witnesses**, rather than only the aggregate false result. It does **not** retain literal difference locations, normalized values or differing raw bytes, and therefore does not guarantee that every failed comparison can be fully diagnosed or corrected after teardown. Raw captures remain private to the live job; no receiving-only recovery is available from the retained public artifact afterward. The original failed comparison from run 43703658937 remains unidentified and unfixed.

Root has received this distinction and directed that the fresh owner request disclose it. There is no claim that a future failure is guaranteed diagnosable and no automatic retry. The source/issuer-binding PASS remains scoped to the reviewed implementation and actual records.

## Actual retention path

For the completed-receive/nonzero-return path demonstrated by the old run, `full_relation.receive()` constructs and validates `FULL_RELATION_PROOF.json` even when its overall equality is false. `pair_driver.receive_main()` writes the receiving record and `RECEIVED_PUBLIC.json` before returning 1 for false normalized equality. `write_public_summary()` includes the whole validated proof as `full_correspondence` when that proof exists.

The corrected `run.py` nonzero branch reads that existing typed summary, assigns it to `PROBE.json.result`, and marks `result_disposition` as `VALIDATED_UNACCEPTED_NONZERO_RECEIVE`. It then retains the original `FULL_PAIR_NOT_COMPLETELY_RECEIVED` refusal. Finalization and the existing public emitter can retain that result in the seven-file public packet, subject to all existing custody, schema and size checks. The emitter rereads the corresponding summary and requires byte-derived value equality before export. No failed result becomes accepted receiving or a successful live proof.

The retained normalized comparison is at `PROBE.json.result.full_correspondence`. This is embedded in the final public packet; a failed receive does not produce the successful live-review artifact.

## Exact public fields

`full_relation.SCOPES` is exactly `whole`, `portal`, `repro`, `pending_durability`, and `pending_loader`. For every named scope, `relations[scope]` retains:

- `equal` and `difference_count`;
- `left_projection_sha256` and `right_projection_sha256` for the complete scoped projections;
- `witnesses`, containing the first at most two differences in the deterministic traversal;
- `witnesses_complete`, true exactly when the difference count is at most two.

Each witness retains `kind`, `location_sha256`, `left_projection_sha256`, and `right_projection_sha256`. The permitted kinds are `TYPE`, `BYTES`, `VALUE`, `FIELD_POPULATION`, and `POPULATION`. A `BYTES` witness additionally retains `first_different_offset` plus `left` and `right` descriptors containing byte counts and SHA-256 hashes.

The proof also retains the overall equality flag, exact source/policy/input/registry/command identities, the private-observation descriptor, the fixed population and original-scope flags, actual report/skip/expected-failure counts for each route, and source/runtime/raw-census bookend assertions. Its original 16,384-byte bound remains. The typed operation summary retains its 49,152-byte bound, and the original public file, semantic and cumulative limits remain unchanged.

## Information deliberately absent

`location_sha256` is `sha(encode(path))`; the path itself is not exported. Neither a `VALUE` nor a `TYPE` witness contains the actual differing value or type name. Population witnesses do not contain the differing key/member population. Byte witnesses contain lengths, hashes and the offset, not the differing byte values or excerpts. At more than two differences in one scope, the later differences have no individual public witness.

A location digest can sometimes be matched against an independently known schema path. That is an inference from known source, not a retained literal location, and is not guaranteed for data-derived paths. Likewise a scope, kind and byte offset may narrow a cause without proving it. The retained evidence is more informative than the old aggregate result, but it does not promise a sufficient corrective preimage for every failure.

## Private custody and continuation boundary

The summary explicitly declares `LIVE_JOB_ONLY_RECEIVE_BEFORE_TEARDOWN_NO_CUSTODY_TRANSFER`; cleanup declares private outputs not uploaded. `FULL_RELATION_PRIVATE.json`, the raw sealed captures and declared private artifacts remain within that private live job. A receive failure does not itself claim those files were immediately deleted, but the workflow skips `prepare-review`, review upload and the hold after that failed step. The source also requires true overall normalized equality before preparing a live-review request.

The existing `pair_driver.receive_main()` refuses `NO_REPEAT_RECEIVING` before writing whenever a receiving record, progress record, pending progress or receiving failure record already exists. The retained summary has its own no-repeat guard. Thus the existing failed path neither schedules a receiving-only continuation nor leaves an admitted retry. Once the hosted job is torn down, public hashes cannot recover those raw inputs or their former custody.

This is the existing evidence ceiling, not a proposal to remove no-repeat guards, expose private values, introduce another channel or widen output limits.

## Owner references

All module paths are under `qualification/dg16-r5-full-g2/`:

- `full_relation.py`, `compare`, `receive`, and `validate_public_proof`: SHA-256 `04fe4362385b819363f8785d0ad9a346724937f2e798e25536a7ad67db550499`.
- `pair_driver.py`, `write_public_summary` and `receive_main`: SHA-256 `77ca44aa123167c4dbc5b6d35ba66d587e25f8e192db0bc8224b014f690bf174`.
- `run.py`, `validate_pair_summary`, `read_pair_summary`, `emit_bound_public`, nonzero receive, `prepare-review`, and finalization: SHA-256 `c93bf11715e40ed51b92f9463ed5c08710d500685384abc890043465f03e950a`.
- `.github/workflows/dg16-r5-full-g2.yml`, success-only review/hold and always-run final public retention: SHA-256 `44b303cae5f331cf1c4e62ac9b73dd1920772d6283b952b5dfd203a36cebbb0f`.

The prior qualified retention correction and its original focused controls were reused. No private historical evidence was reconstructed, and no prospective output was substituted for an actual result.
