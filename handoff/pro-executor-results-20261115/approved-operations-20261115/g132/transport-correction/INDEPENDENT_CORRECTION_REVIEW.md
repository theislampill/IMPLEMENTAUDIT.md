# G132 resolver correction — independent source receiving

**PASS at the exact frozen source/static scope. No blocking source or pin-closure finding remains in this eleven-path delta.** This disposition is not a live transport qualification, Root admission, grant, retry authority or original/native acceptance.

Reviewer: `/root/dg17_recovery`, distinct from author `/root/g2_receiving`. Review completed 2026-11-15T23:40:17.372106+00:00, after receiving the actual run43774001960 through terminal failure. Root explicitly commissioned this single bounded correction review. I made no candidate edit, commit, publication, installed-source change, provider call, protected operation or regression rerun during this review.

## Reviewed identity and delta

Isolated worktree: `/workspace/scratch/7fbb79f74aa4/recovery/g132-transport-correction`, detached at operator commit **198a0495e486a5cc79534aa42fa984516ad16d67**, tree **e7024697702307712798501554a894c2fe94d0d0**. All changed paths below are relative to `handoff/fable-local-support-20261115/dg16-g132-owner-local/public-operator/`.

The exact freeze is `CORRECTION_FREEZE.json`, **3795B / SHA25636f8ad103524375eff0955bc256992bcb54d36b3486d2fb0c1edc1913ccbe0c1**. The actual complete Git diff is byte-identical to `INTEGRATED_CORRECTION.diff`, **26789B / SHA256a7ff62dcfa27af14b026eea36dc7e8601e8fbfcfd65356079e9f31d44983a76e**. Git names exactly the eleven authorized changed paths and no additional candidate path. I verified every frozen changed-file descriptor and every evidence descriptor listed in the freeze.

| Changed path | Bytes | SHA256 |
|---|---:|---|
| `OPERATOR_PINS.json` | 27159 | `2e66edeb097c09c11f7277c6e58e1b03ec960b790fa3b235a08289cd95570542` |
| `SOURCE_SELECTION.json` | 1965 | `98ed75d7c78ba4420a38acbd56a1586b8a25aa71ef60612583a0ff3dec63c743` |
| `framed-role-02/control_process_v3.py` | 17557 | `97817318e1d3d2cef68e40d428fa7bfbe0692793b5b8ca41ae9faa0efb49458e` |
| `framed-role-02/role_process_v4.py` | 13091 | `5b6634d695574ec9888b61bdd487686d091a98af4e1239e52acd06d7c7b5d18c` |
| `public-receiver-02/author/resolve_artifact.py` | 12229 | `8da0acdb81c9cbebd8fbc3cfd1f79c31222e8c93260930738e7ccd803abb5226` |
| `public-receiver-02/root-control-v5/control_process_v5.py` | 19603 | `c86e55860171dab82afeb4da899f2a6560495da61eaf56482886bbb8326f8f4f` |
| `root-event-helpers-02/g1_event_config_corrected.py` | 24506 | `a197dae5ba69986f09a2a4fa9a59c5feff6549dfc6b7efd7e6c73d8cd1706504` |
| `root-event-helpers-02/root_live_sender_call_received.py` | 28372 | `f554a87dad96dc88f510df63586f94bc3f25dc5fdf496c66c7148559e9a20ffa` |
| `root-final-operators-01/binary_publish_v3.py` | 20775 | `b9047229554b23467523e8f68b6a9f1fa65a58775b8ff6d7c988748d62a87cbb` |
| `root-final-operators-01/control_process_v3.py` | 17557 | `97817318e1d3d2cef68e40d428fa7bfbe0692793b5b8ca41ae9faa0efb49458e` |
| `root-final-operators-01/root_pipeline_inputs_v2.py` | 16004 | `e9deede2d927ce7b4db033c687e75fceaeac238fd3cb5573aa42dae01868e79d` |

There is one semantic source change, `resolve_artifact.py`. Eight callers receive only the necessary SHA256 substitutions. The source selection changes only `event_owner.sha256`; the operator index incorporates the resulting ten changed member descriptors. No new operator member, host source, product source, workflow, phase, publication object or historical/current evidence body is introduced by this delta.

## Configured routing correction

The actual old resolver uses `urllib.request.ProxyHandler({})`. The candidate uses `urllib.request.ProxyHandler()` with no explicit mapping. I read the actual local standard-library initializer: it calls `getproxies()` when and only when its `proxies` argument is `None`. The candidate therefore permits the existing configured proxy/bypass selection; the predecessor explicitly suppressed it.

This is the appropriate narrow owner/source correction for the observed configured-routing mismatch. It does not add a caller-provided URL, host family, credential field, alternate download result or routing override. The same returned ephemeral HTTPS reference is still selected from the complete actual tool result, duplicate copies must agree, URL credentials/fragments/nonstandard ports remain refused, and the original allowed storage-host family remains fixed. The verified TLS context, `NoRedirect` handler, exact final URL equality, one opener call, and bounded response read remain in the same source function.

The actual failed tools-body attempt still has an unknown discarded exception. Root's independent post-failure DNS probe found direct-DNS failure with configured proxy names present; the later ordinary first download of the separate terminal failure artifact succeeded through configured routing. These are actual observations at their own scopes. Neither establishes the exact exception that the original resolver discarded, nor does either exercise this candidate operator. The source correction and its review do not relabel that failure.

## Safe diagnostic correction and consumer compatibility

The new `failure_class()` returns only a fixed vocabulary. It checks HTTPError before generic URLError, and classifies a URLError's typed reason without serializing it. It orders WatchdogExpired, DNS and TLS before broader timeout/OS classes. It returns fixed codes for HTTP, watchdog, DNS, TLS, timeout, connection, OS, local validation and interruption; opaque URL errors and other exceptions use fixed fallback codes.

The function does not call `str()`, `repr()` or `type(...).__name__`, and does not emit arbitrary class names, exception messages, URLs, credential values or proxy configuration. String-valued reasons produce the fixed URL fallback. The outcome gains only `error_class_code`, initialized to null on success and set to a fixed code in the existing caught-failure branch. The generic failure status/code, actual attempt counter, observed-body/readback fields, no-retry declaration, no-effect/cleanup limits and empty awards remain unchanged.

I read the actual direct outcome consumer in `framed-role-02/role_process_v4.py::run_role`. After `X.resolve`, it restores the watchdog, rechecks remaining time, and requires `outcome.get('status') == 'RECEIVED'` before emitting the complete outcome. It does not accept a failure because a diagnostic code is present and has no closed outcome key-set gate. The standalone resolver main likewise serializes the complete result and selects its exit status from `result['status']`. The additive field therefore requires no new consumer authority or schema-selection logic. Other changed callers only load/pin the resolver and related owners; they contain no new operational behavior.

The fixed-code field is small relative to the existing reserved outcome envelope. It does not establish cleanup, no effect, replay safety or success on a partial body.

## Preserved guards and exact pin closure

Independent AST comparison found only two existing resolver functions changed: `fetch_once` and `resolve`; only `failure_class` is new. Ten existing functions/classes are unchanged, including exact download-reference receiving, frame receiving, no-redirect and watchdog behavior. The import change adds only `socket` for its exception category. I read the full semantic diff and the modified source paths.

The exact-reference and source checks, existing intent/archive/outcome exclusivity, pre-attempt durable intent, no-uncertain-body-replay guard, watchdog limit, parent remaining-time restriction, late-acceptance refusal, caps, provider size/digest check, archive write/readback and all conservative failure fields remain intact. The original300000ms pre-sender floor, native/currentness contracts, host2f and producte76 remain in unchanged consumers/source. This review does not extend any grant to a new source or operation.

The following read-only static checks completed against actual candidate bytes, not only author labels:

- The final index is **27159B / 2e66edeb097c09c11f7277c6e58e1b03ec960b790fa3b235a08289cd95570542** with exactly the same **144 member names** as operator198. The physical operator population is exactly those144 files plus the index itself.
- All144 member byte counts and SHA256 descriptors equal the actual files. Exactly ten member descriptors change, corresponding to the eleven-path Git delta minus the self-excluded index.
- All eight caller texts are identical after normalizing64-hex SHA tokens. Each actual differing token maps from the authentic predecessor file hash to its exact final candidate hash; no arbitrary replacement is accepted by this check.
- `SOURCE_SELECTION.json` is identical to its predecessor object except that `event_owner.sha256` equals the new actual `g1_event_config_corrected.py` digest. Its final SHA is98ed75d7c78ba4420a38acbd56a1586b8a25aa71ef60612583a0ff3dec63c743.
- The caller Python files and resolver parse as Python source. No candidate source was executed by these checks.
- All144 original installed operator members and its index remain byte-identical to operator198. Its index remains c7ac3f5a95dec2c05f10201d96429c27d3e9d5e19f6d1a8051c3c14912b90309. All26 original failed-tools-session leaves remain byte-identical to the preserved failure copies, with exactly the same population.

These checks produced no live provider call, role/owner invocation or source mutation.

## Reused bounded verification

I read the author's exact `transport_regression.py` (**7047B / 9703087318afc918c30378cc078c7a8f22d4c398b5cb28ce0aad4cda87ea3907**) and its retained result (**1107B / c2e8cab7791df16349035f8dbd367837d23c393c05567ca0a107ab616048db2d**). The candidate exercised there is exactly12229B / 8da0acdb81c9cbebd8fbc3cfd1f79c31222e8c93260930738e7ccd803abb5226, unchanged by later pin integration.

The one inert regression uses a synthetic configured HTTPS proxy, an in-memory HTTPS response, blocked network/DNS functions and synthetic temporary session objects. It verifies that the predecessor fails configured-routing selection and bounded DNS-class retention while the candidate passes. It also checks one request/45-second argument, conservative failure/no-replay behavior, secret-marker omission and fixed fallback categories. Its second call is an inert refusal check against a synthetic temporary intent; it does not touch the actual failed session. The result does not infer the original actual exception.

This is sufficient focused support for the small semantic delta together with direct source review. I did not rerun the regression, broaden tests, replay an artifact, run a role or add a new qualification framework. The author’s actual `PIN_CLOSURE.json` (**4832B / 3fdb938642f9838dfef7a5d82e536b2020eb3e34057bff970cf494dab220b834**) and full report (**10961B / d1c8f1e86a1d9a8545e42e61737eaee4b2b9f1739ef1c133f353e4c53bd58e4f**) were read and matched to the independently checked frozen bytes. The earlier impact inventory remains a truthful pre-integration record rather than being rewritten.

## Final disposition and limits

**PASS — exact eleven-path source/static receiving.** The two concrete source issues are addressed: configured proxy routing is no longer suppressed, and future caught failures can retain a bounded safe class code. The candidate's144-member index and all transitive caller pins are internally consistent. No blocking defect was identified within this scope.

Actual run43774001960 remains terminal failure, with local tools-body UNKNOWN_NO_REPLAY and the fallback record UNQUALIFIED. Its exact terminal independent receipt is `../actual-43774001960/TERMINAL_INDEPENDENT_RECEIVING.md` (**11055B / 48b7c2dcd8549c982511244f4f03498f4565f7937c7e552ef1724e0e96f4e2c9**). Earlier UNKNOWN custody is unchanged. This report is an external actual review of the new candidate; it is not inserted into the operator closure, does not create circular self-reference, and does not alter earlier receiving bodies.

Root may consume this factual source review for the already-authorized ordinary publication process. No protected launch, second G132 attempt, old tools-body retry, sender, adoption, original award or wider acceptance is authorized by this report. Any later actual operation must use its actual current source and applicable owner authority; historical receipts remain historical.
