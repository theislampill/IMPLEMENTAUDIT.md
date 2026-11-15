# G221 public GitHub evidence channel — source candidate

This candidate acquires **public GitHub facts only** through the actual connector
available in `functions.exec`. It removes no existing semantic receiver, grants
no effect, and returns no original acceptance. It is not a complete replacement
for G221's operator: public archive transport, the unchanged bound public receiver,
actual live independent proof review, separate Root consumption/control publication,
and same-job closing readback remain separate required interfaces.

The current owner concurrence permits source engineering and qualification. Use
for original acceptance requires separate written owner approval of the final
independently reviewed implementation and its complete pinned composition.

## Files and runtime

- `channel.js` is an expression returning `collect(selection, host)` and
  `receive(operatorReceipt, selection, host)`, plus the optional
  `createActionValidator(selection)` helper described below. It uses ordinary ECMAScript, the
  actual global `tools.mcp__codex_apps__github_fetch`, and the actual global
  `tools.exec_command`. It needs no Node globals, `TextEncoder`, Web Crypto,
  `Buffer`, direct network, or filesystem API inside V8.
- `journal.py` is the small POSIX durable writer. The JavaScript invokes a fixed
  Python bootstrap, reads and checks the supplied journal source digest, and
  executes those exact captured bytes with isolated Python. It runs no provider
  call and does not authenticate evidence or authority.
- `test-channel.mjs` tests the channel in a V8 context without Node capabilities.
  It uses the real Python journal and a controlled external-connector double.
  Optional captured connector inputs exercise the actual current response shape.

No existing qualification or historical custody file is modified. These new
files are outside the shipped product/runtime package. Package qualification,
source adoption and original acceptance are not claimed.

## Trust boundary and host obligations

The host must verify the reviewed `channel.js` bytes **before evaluating them**.
The selected `channel_sha256` is a binding checked by the external host; a module
cannot authenticate its own loading history by a caller-supplied digest. Verify
the source against the final independent review and current owner selection,
not against an expected value supplied by the target repository.

The host supplies `host.admit(scope)`, an actual trusted function, which must:

1. Receive the real owner authorization and actual operator/receiver assignment.
2. Check the exact source pins, operator, role, repository/branch/run/attempt,
   workflow/source/control identities, action scope, fixed journal root,
   operation identity, purpose and expiry in `scope`.
3. Return `{authorization: {ref, sha256}, assertCurrent, assertIndependent}`
   only if authorized. `assertCurrent(scopeWithAction)` must recheck current
   authority and throw on revocation, changed scope, wrong source or an expired
   grant. It is called before every provider call, after its return and before
   completion. A JSON `authorized: true` is rejected.
4. For `receive`, `assertIndependent({operator_receipt, receiver, scope})` must
   authenticate the actual originating operator observation and the actual
   distinct receiving agent. It must bind the exact original receipt digest
   received through trusted custody. It cannot simply accept the receipt's actor
   string or hash as its own proof. The code's unequal-label check is an additional
   refusal condition, not proof of independence.

These host functions are deliberately not implemented as always-allow helpers.
They must be installed by the entitled host/controller from real session authority,
not loaded from target content or generated from JSON labels. Without them the
channel fails before any provider call. Review of this candidate must include the
actual host admission adapter in the final composition.

### Exact host action protocol

`assertCurrent` receives `scope.action` in this order. The three indexed phases
repeat for each of the 11 selected public reads, or 17 with selected control.

| Phase | Exact action value |
|---|---|
| Begin, once | `"begin"` |
| Before persisting action intent | `{index, tool, request}` |
| Before invoking the provider | `{index, tool, request, intent}` |
| After provider return | `{index, result_returned: true}` |
| After the entire selected read sequence, once | `"finish"` |

`tool` is exactly `mcp__codex_apps__github_fetch`; `request` contains only the
exact selected `{url}`. `intent` is the durable record descriptor with only
positive integer `bytes` and lowercase 64-character `sha256`. Do not require all
actions to be strings or all action objects to contain a request.

The host may create a fresh `const checkAction =
channel.createActionValidator(externallyBoundSelection)` for each admission,
then call `checkAction(scopeWithAction.action)` inside `assertCurrent`, in
addition to its real authorization and exact scope checks. The helper rejects
wrong shapes, endpoints, order, indices, intent descriptors and early or repeated
completion. It includes the selected closing reads and optional control reads.
It returns only a mechanical sequence check; it does not verify loading history,
current owner authority, source identity, receipt origin or actual agent
independence. An offline always-allow host still supplies none of those facts.

Both the selected operation deadline and the original operator receipt deadline
must remain current throughout receiving. A later receiver deadline cannot
extend the parent observation. The channel checks both before and after every
`assertCurrent` callback, including provider returns and `"finish"`, and checks
them immediately before and after final durable persistence. The post-write
deadline check is local; it does not add another host action or a second
`"finish"` callback.

`SOURCE_QUALIFICATION` permits only the separately authorized public read-only
qualification scope. `OWNER_APPROVED_ORIGINAL_ROUTE` requires the owner's separate
use approval; spelling that value grants nothing. Independent receiving cannot
change one purpose into the other. All outputs retain `authority: NONE` and
`original_acceptance: false`.

## Selection and invocation

The exact selection fields are:

| Field | Required value or binding |
|---|---|
| `schema` | `dg16.github-public-observation-selection.v1` |
| `purpose` | `SOURCE_QUALIFICATION` or separately approved `OWNER_APPROVED_ORIGINAL_ROUTE` |
| `operator` | `PRO-EXECUTOR-01` |
| `actor` | `/root` for collect; the actual distinct `/root/<receiver>` for receive |
| `successor` | `PRO-EXECUTOR-01, designated by owner` |
| `role` | `live` or `terminal` |
| `operation_id` | Current externally admitted operation identifier |
| `source` | Exact `channel_sha256`, `journal_sha256`, absolute `journal_path`, absolute `python_path` |
| `journal_root` | Freshly selected existing absolute private POSIX directory, real path, mode `0700`, current UID |
| `expires_ms` | Current externally approved expiry, at most 300 seconds ahead |
| `context` | Exact fields listed below |
| `control` | `null`, or the exact existing terminal control selection listed below |

`context` contains `repository`, `repository_id`, `branch`, `run_id` (decimal
string), `run_attempt: 1`, `workflow_commit`, `workflow_tree`, `source_commit`,
`source_tree`, `workflow_path`, `workflow_sha256`, `job_name`, and
`github_actor: {id, login}`. The fixed repository is
`theislampill/IMPLEMENTAUDIT.md`; workflow and job remain
`.github/workflows/dg16-r5-full-g2.yml` and `full-registry-raw-pair`.
The GitHub account association binds provider attribution; it does not by itself
identify the model agent or establish authority.

An optional terminal `control` has exactly `branch`, `commit`, `tree`, `path`,
and `files`. Its branch is the matching selected control branch, its path is
`qualification/dg16-full-g2-control/<run_id>-1`, and `files` contains exactly
`CONTROL.json`, `INDEPENDENT_REVIEW.json`, and `ROOT_CONSUMPTION.json`, each with
the independently selected `{bytes, sha256}`. Control absence and publication
are not implemented or inferred. The control's declared tree must come from
the entitled exact publication selection; original `live_control` remains the
semantic owner for exact allowed additions and review/consumption meaning.

After loading the externally verified expression, the root calls
`await channel.collect(selection, host)`. A genuinely different receiver, with
its own admitted journal root and fresh authority, calls
`await channel.receive(operatorReceipt, receiverSelection, receiverHost)`.
Both calls perform actual connector invocations. `receive` never accepts the
supplied metadata as provider evidence: it re-acquires the complete observation
and compares independently observed facts. It also rejects expired or changed
operator receipts and inconsistent copies of the public metadata.

The base sequence has 11 calls: host ref; run; attempt; jobs; workflow commit;
product source commit; exact workflow bytes; complete artifact list; closing run;
closing artifacts; closing host ref. Declared terminal control adds six calls:
opening ref, commit, three exact file bodies, closing ref. These are bounded
read-only endpoints. There is no generic URL input, mutation API, private API,
artifact body API, download API, cipher acquisition, retry, or resume.

## Durable intent and failure behavior

A subject slot under the fixed admitted journal root is exclusively created
before the first call. Its key binds repository, run, attempt, workflow commit,
role, actor and operator/receiver mode. Changing the nonce, expiry, authorization
label or channel source cannot bypass a spent slot under that root. A changed
journal root requires explicit admission; the root path is exposed to the
external gate and bound in the selection digest.

Each action intent is persisted and read back before invocation. Complete result
wrapper descriptors and sanitized projection digests are then persisted. The
final record checks the whole intent/result sequence. Files are create-only,
mode `0600`, within held/no-follow private directories, with identity and byte
readback checks. An ambiguous or failed call becomes `UNKNOWN_NO_RETRY`; the
code never invokes it again. Any later invocation against that subject slot is
refused, including after a crash or incomplete journal.

If the final durable write finishes after either applicable deadline, the
channel returns `UNKNOWN_NO_RETRY` with `journal_completion: "UNKNOWN"`, rather
than a received observation. A completed `FINAL.json` may already exist; the
create-only writer preserves it and refuses a later `UNKNOWN.json` overwrite.
That file alone is not a completed channel return or authorization. Preserve
the returned UNKNOWN outcome and the spent slot. Do not recover a success from
the file or retry the acquisition with another nonce or journal root.

Raw connector wrappers, raw provider text, signed storage URLs, materialization
references, private keys and cipher bytes are not stored. The retained actual
wrapper descriptor is SHA-256 over `JSON.stringify(actual)` encoded as UTF-8,
without a trailing newline. Only whitelisted public facts cross into the final
record. Known cipher-artifact **catalogue metadata** can be observed as part of
the ordinary complete public artifact list; it is never selected, downloaded,
decrypted, or promoted. Unknown artifact populations are refused.

The journal is a durable observation record, not a signature or authority
mechanism. Same-UID malicious code or a compromised trusted host is outside
this source-level guarantee. Independent provider re-observation and external
operator/owner provenance remain necessary.

## Connection to the preserved G221 receivers

Successful operator status is
`PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING`; independent status
is `INDEPENDENT_PROVIDER_FACTS_MATCH_ONLY`. Neither accepts G221 or establishes
that the hosted program achieved its intended effect. A historical failed run
remains `conclusion: failure` in the projection.

The result's `public_metadata` is the original receiver's three-field
`{run, commit, artifact}` input and may be serialized as `PUBLIC_METADATA.json`
after external origin/independence receiving. The tests pass the authentic
metadata projection through the **unchanged** original
`public_receiver.py::metadata_bindings` at source SHA-256
`5bb8d71aa40e2a4d842ddd178b31257eef496ca3c0073461e8328d2e64560f5e`.
Its answer explicitly remains provided-metadata consistency, with acquisition
authenticity independently received.

The separately qualified public archive resolver must acquire exactly
`public_metadata.artifact.id` and match its `size_in_bytes` and SHA-256 `digest`.
Feed the archive plus `PUBLIC_METADATA.json` into the exact installed, bound
original `public_receiver.py` with the selected kind, run ID and workflow commit.
Terminal receiving also needs the exact original terminal log/archive join.
Live receiving still needs actual proof review, separate Root consumption,
control publication under current authority and same-job closing readback.

The new channel cannot replace private-input custody, original currentness,
native applicability or the original full correspondence semantic checks. The
original receiver's own output remains non-accepting data qualification.

## Qualification and limitations

Run the focused suite from the repository root:

```bash
node --test qualification/dg16-github-evidence/test-channel.mjs
```

To also exercise the current authentic connector wrappers captured read-only by
the root, set `DG16_ACTUAL_PROVIDER` to a directory containing the six original
`run.json`, `attempt.json`, `jobs.json`, `commit.json`, `workflow.json` and
`artifacts.json` wrappers. Without that input the test is explicitly skipped.
The wrappers are replayed through the source test's controlled provider double;
this is not an authentic invocation of the new channel or original acceptance.
The root must separately exercise the pinned expression with real tools and its
actual host gate, then obtain independent review of the complete composition.

The initial 35-pass record, its candidate pins and its exact test/document bytes
are retained under `history/channel_0b19e735/`. The exact old executable used by
the root's historical G219 smoke is retained at
`handoff/dg16-pro-executor-20261115/evidence/channel_at_actual_g219_smoke.js.txt`,
SHA-256 `0b19e735ff3fc7525b22a22d3bc2c873b8370b058e513f478878668ee3af4aa5`.
That authentic observation remains bound to its old source. The expiry
correction's tests use fresh local test journals and controlled provider
doubles; they do not relabel or replay the historical smoke, repair a spent
receiving attempt, or establish an authentic receiving result for this revision.

G132's local-only 98-file operator set is unavailable here. This candidate does
not wire or qualify G132, its sender, its G3 callback, or its protected inputs.
It does not resolve the queued G1 run, select a budget floor, or issue any launch
grant. Live-window feasibility on the complete actual tool/transport chain is
still required before a protected operation.
