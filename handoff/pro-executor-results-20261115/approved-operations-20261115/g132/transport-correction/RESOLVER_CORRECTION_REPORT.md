# G132: isolated resolver transport correction

## Outcome and scope

The isolated source correction replaces an explicit no-proxy transport with Python's configured proxy discovery and retains a bounded exception-class code in the existing body-get outcome. One inert regression demonstrates both changed behaviors while preserving refusal and no-replay behavior. The original failed attempt remains unchanged and its exact exception remains unknown.

Author: `/root/g2_receiving`, under Root's bounded ordinary-source delegation. Worktree: `/workspace/scratch/7fbb79f74aa4/recovery/g132-transport-correction`, detached at exact operator commit `198a0495e486a5cc79534aa42fa984516ad16d67`, tree `e7024697702307712798501554a894c2fe94d0d0`. The sole semantic source change is `handoff/fable-local-support-20261115/dg16-g132-owner-local/public-operator/public-receiver-02/author/resolve_artifact.py`. Root then authorized the exact required pin integration: eight callers, source selection and the operator index, for eleven changed paths total.

| Source | Bytes | SHA-256 |
| --- | ---: | --- |
| Actual operator198 resolver | 11390 | `35c709a35c96c2d49913db93e7a2b9091290c6690477e8f17873e85618df1e22` |
| Isolated corrected resolver | 12229 | `8da0acdb81c9cbebd8fbc3cfd1f79c31222e8c93260930738e7ccd803abb5226` |

This is an internally integrated source candidate for distinct review. Its caller/index pins are closed in the isolated worktree, with the original 144-file population. No live operator body, failed session, workflow, host, preparation or protected ref was changed. No real network GET, protected retry, adoption, sender, model/native operation, grant or acceptance was performed by this correction.

## Actual failure evidence and limit

The actual `tools` session for run `43774001960`, workflow commit `2f6a96427a307dc57ed88664aeb8224918fe6bf5`, retained one body-get intent and one refused/uncertain outcome. These are existing originals under the fixed live operator's `public-receiver-02/`:

| Retained original | Bytes | SHA-256 |
| --- | ---: | --- |
| `sessions/run-43774001960-tools/BODY_GET_INTENT.json` | 1313 | `4f1ea504c10cfc490aeb8936ac5011653165824e4830359a84248bf34481d052` |
| `sessions/run-43774001960-tools/BODY_GET_OUTCOME.json` | 1443 | `829f85953c5006e76c0d6830e736933416d07aa10465b978a012832667cf61bf` |
| `current-execution/POST_FAILURE_TRANSPORT_DIAGNOSIS.json` | 840 | `ae4e1b1affb9627c3f3039b4b5656a3d2e85798b7acc07917359bdadc979fd91` |

The original outcome records one attempt, `complete_body_observed: false`, no observed body, no retained archive, `readback: NOT_AWARDED`, and `BODY_GET_REFUSED_OR_UNCERTAIN`. Its monotonic interval is approximately 5.632 ms against the unchanged 45-second deadline. It neither records the exception class nor establishes that no external effect occurred.

Root's separate read-only diagnosis observes configured proxy variable names and a direct DNS probe failure (`gaierror`, errno -3) for the actual storage host. It expressly records no body-get replay. This is consistent with the no-proxy source path and quick incomplete attempt. **It does not recover or prove the original GET's discarded exception.** Neither this source correction nor the inert DNS exception used below retroactively classifies that original failure.

## G132-T01 — configured proxy routing was disabled

**Severity:** source blocker for environments requiring their configured proxy. **Owner/source:** `resolve_artifact.py::fetch_once`, selected at operator198.

The original `urllib.request.ProxyHandler({})` supplies an explicit empty proxy mapping. The actual local Python standard-library implementation calls `getproxies()` only when its `proxies` argument is `None`; therefore the original source suppresses configured proxy discovery. This source fact is independent of the unknown original exception.

**Correction:** use `urllib.request.ProxyHandler()` with no explicit mapping. This honors existing system proxy discovery and bypass configuration without introducing an alternate URL, credential source, host allowance or caller override. The existing exact HTTPS URL/host family checks, verified TLS context and `NoRedirect` handler remain intact.

**Verification:** the single inert regression patches proxy discovery to a synthetic configured HTTPS proxy and replaces the final HTTPS handler with an in-memory response. Network connection and DNS functions are blocked. The baseline sends its one mocked request directly to the origin; the candidate uses the configured proxy with the original HTTPS host as its tunnel target. Both preserve the exact request URL, GET method, body and 45-second timeout argument. This proves routing selection at that source boundary, not the future availability or correctness of any real proxy.

## G132-T02 — caught failure class was discarded

**Severity:** diagnostic evidence gap. **Owner/source:** `resolve_artifact.py::resolve` exception handler and outcome record.

The original catch collapses all caught exceptions to the same refusal code, discarding information needed to distinguish a DNS, TLS, HTTP or timeout failure. The original generic status is appropriately conservative and remains unchanged.

**Correction:** add `error_class_code` to the existing outcome, using `None` on success and a fixed vocabulary on caught failure. `failure_class()` maps known built-in exception types, including a `URLError`'s typed reason, to fixed codes for HTTP, DNS, TLS, timeout, watchdog, connection, OS, local validation, interruption or unknown exceptions. Unknown types and string reasons produce fixed fallback codes. It never serializes exception text, arbitrary class names, URLs, tokens or proxy configuration. It does not infer cleanup, no effect or retry eligibility.

**Consumer compatibility:** the actual framed role calls `X.resolve()` and checks only `outcome.get('status') == 'RECEIVED'` before emitting the complete receipt (`framed-role-02/role_process_v4.py::run_role`, lines122–129). The standalone resolver main serializes the complete result and chooses its exit status from `result['status']`. Neither has a closed outcome key-set check. The other resolver consumers load it for fixed framing/read functions or source pin validation. No downstream outcome schema change or acceptance weakening is required. Existing status, main refusal code and readback semantics are unchanged.

**Verification:** the same inert regression injects a wrapped `socket.gaierror` containing a synthetic sensitive marker. The candidate retains only `DNS_RESOLUTION_ERROR`; baseline lacks the classification. The outcome stays refused/uncertain with no archive, and a second call against the same synthetic intent refuses before a second transport attempt. URL/message markers are absent from retained outcome bytes. Fixed-code controls also cover HTTP, TLS, timeout, watchdog, opaque URL reasons and an arbitrary exception class name. These are synthetic controls, not observations of the original error.

## Preserved execution predicates

The selected download-reference receiving, duplicate reference equality, HTTPS-only origin checks, allowed storage family, response URL equality, TLS verification, no-redirect handler, one opener call, watchdog/deadline bounds, size cap, exact body size/digest, exclusive intent/archive/outcome writes and no-replay guard are unchanged. Failure stays unqualified. The parent role's stricter remaining-time bound remains unchanged.

The added diagnostic field fits within the existing bounded outcome envelope. It does not grant success on a partial body, permit another request, rewrite an old outcome or remove any precondition. The failed real session remains spent/uncertain under its existing no-replay guard.

## Exact isolated caller-pin integration

`CALLER_PIN_IMPACT.json` records the read-only dependency inventory. Eight runtime files directly pin the resolver: the framed role, framed control, current public control, event configuration helper, live recipe helper, final binary publication helper, final control and final pipeline-input helper. Their dependent source selection and the operator index join the complete eleven-path impact set: the resolver, those eight callers, `SOURCE_SELECTION.json` and `OPERATOR_PINS.json`.

Root authorized integration of exactly that inventory in the isolated candidate. All eight caller bodies change only through SHA-256 token substitutions. `SOURCE_SELECTION.json` changes only `event_owner.sha256`. The index now matches every actual file descriptor and the unchanged 144-member population; no stale intermediate runtime pin remains. The corrected resolver bytes are identical to the bytes exercised by the one retained inert regression, so that regression was not repeated.

The integrated operator index is 27159 bytes, SHA `2e66edeb097c09c11f7277c6e58e1b03ec960b790fa3b235a08289cd95570542`; source selection is 1965 bytes, SHA `98ed75d7c78ba4420a38acbd56a1586b8a25aa71ef60612583a0ff3dec63c743`. `PIN_CLOSURE.json` records the exact eleven before/after descriptors and deterministic convergence. The earlier read-only impact inventory remains unchanged as its pre-integration observation.

The live resolver remains exact SHA `35c709a3…`; its index remains 27159 bytes, SHA `c7ac3f5a95dec2c05f10201d96429c27d3e9d5e19f6d1a8051c3c14912b90309`. Actual readback confirmed that all original 144 live indexed bodies and the index are unchanged. No live materialization was performed. Source integration does not authorize a future host, preparation, effect or protected retry.

## Frozen verification evidence

| Record | Bytes | SHA-256 |
| --- | ---: | --- |
| `RESOLVER_CORRECTION.diff` | 5498 | `150d130068da873d529fd04473fdadc00fafb7a7a72fb75bfe003732d756fbe1` |
| `transport_regression.py` | 7047 | `9703087318afc918c30378cc078c7a8f22d4c398b5cb28ce0aad4cda87ea3907` |
| `TRANSPORT_REGRESSION_RESULT.json` | 1107 | `c2e8cab7791df16349035f8dbd367837d23c393c05567ca0a107ab616048db2d` |
| `CALLER_PIN_IMPACT.json` | 5185 | `6d41f42e9f8a7ecf8f314c0da872c74a2e07e47adcd53c36df10c0ee9cf03415` |
| `PIN_CLOSURE.json` | 4832 | `3fdb938642f9838dfef7a5d82e536b2020eb3e34057bff970cf494dab220b834` |
| `INTEGRATED_CORRECTION.diff` | 26789 | `a7ff62dcfa27af14b026eea36dc7e8601e8fbfcfd65356079e9f31d44983a76e` |

The one focused regression exited0. Its baseline fails the two targeted properties and its candidate passes. Resolver syntax compilation and `git diff --check` passed. The final isolated Git delta contains exactly the eleven authorized paths; the eight callers have no non-pin text change, and the phase and all historical/current evidence bodies are unchanged. No second regression, broad suite, live GET or native qualification was run. Distinct review is assigned to `/root/dg17_recovery` after receiving the actual current G132 terminal evidence. That review and any subsequent Root decision remain separate from this source-author evidence.
