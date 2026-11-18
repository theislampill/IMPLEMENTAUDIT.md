# Read-only public G3 validation interface

This fills only the `validateRequest` and `validateDecision` callbacks in the existing Pro bridge. It creates no request, decision, admission, journal, sender, publication, host setup, consumption, or award. The full original hosted pipeline still needs current source/recipient/sender/control binding and independent receiving.

## Exact executable

`g132_hosted_validate.py` has two fixed stages: `components` and `original-final`. Its source input is exclusively the original 153,706-byte G3 module at SHA-256 `b85cca1550ff8e7c1c89778180e53a5c70f306f0c8725ba60ef3ccd4bbc3a6ad`. The shim extracts and compiles the exact pure validator functions and their constant dependencies. The original module is not imported, and its consumers/context/decorators/main entry are absent from the compiled subset.

The actual process argument vector is:

```python
[
    "/usr/bin/python3", "-I", "-B", received_shim_path,
    "--source", received_original_g3_path,
    "--stage", actual_stage,
    "--run-id", original_receiver_selected_run_id,
    "--request", original_receiver_retained_request_path,
    "--request-sha256", exact_request_sha256,
]
```

For decision validation, append:

```python
[
    "--decision", actual_root_retained_decision_path,
    "--decision-sha256", exact_decision_sha256,
]
```

These are already received paths and descriptors. No private body or credential belongs in command arguments. Root must receive the exact shim bytes through its current selected source manifest before invocation; the helper cannot authenticate its own caller or issuer. Use an actual bounded process tool and receive its complete stdout/exit state. Do not replace an uncertain process outcome with a second invocation presented as the first.

## Callback joins

| Pro bridge callback | Concrete return | Other mandatory evidence |
|---|---|---|
| `validateRequest({scope, request})` | Run the request-only CLI against the file retained by the original artifact receiver. Compare returned `request_sha256` to `codec.descriptor(request.raw).sha256`. Return the parsed metadata. | Original receiver must authenticate actual provider metadata, artifact bytes, run/attempt/workflow/source/context and the selected public request. The helper's run selector is not that authentication. |
| `validateDecision({scope, request, requestBinding, decision})` | Run the decision form on the same request and actual Root decision. Compare both returned digests to the already held request and decision bytes. | The decision must come from the current Root's live capability and exact current authority. A role string or syntactically valid JSON is not issuer authentication. |
| `readRequest`, `decide`, `consume` | Not supplied by this shim. | These remain real artifact receiving, live Root issuance, original control publication and hosted-result receiving, respectively. Local G3 consumption is not a substitute. |

The shim checks both entry and closing wall-clock currentness against the original request deadline. It exposes no clock override. It does not create a new hold, convert shared-window expiry into a fresh interval, or infer currentness from a stored receipt. Its output explicitly sets `native_history_authenticated`, `original_consumer_invoked` and `original_acceptance` to false, and carries no new awards.

## Preserved original policy and prospective M4 integration

The `original-final` stage still applies the original v2 final-decision and row validators. Therefore it still rejects an accepted L04 under the frozen natural-prerequisite rule. The separate M4 join candidate is not silently spliced into this original validator. After coherent M4 integration changes the final request/proof/decision/retained-receipt schemas, the exact new source, new helper/extraction binding and all affected inventories will need independent review and fresh pin receiving.

The original fifteen `FINAL_PROOF_KEYS` also authorize evidence on every row and both gates. An eventual retained-M4 transport field must not be added to that shared global allowlist. The new permission remains L04-specific, while transport/body inventory and request/decision binding are explicit separate populations.

## Verification

`test_hosted_validate.py` contains eleven synthetic public-schema checks. All pass. Positive tests cover both exact original stages and request/decision joins. Rejection tests cover wrong run/stage, expired request, changed source, decision nonce mismatch, duplicate/noncanonical JSON, changed body pin and symlink path.

`HOSTED_VALIDATOR_VERIFICATION.json` also records real isolated CLI execution over explicitly synthetic public documents. The current document/decision returned exit 0; the expired document returned exit 1 with `ORIGINAL_REQUEST_NOT_CURRENT`. No original side-effecting consumer was invoked and no root/host environment was simulated.

This is a completed bounded validation interface, not an integrated original-operation readiness claim. Its independent review remains separate from the M4 candidate review.
