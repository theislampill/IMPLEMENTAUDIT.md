# DG18 consumer qualification and concrete input handoff

## Result and scope

PL2 offline source evidence: the requested OR and C02 consumers were exercised
against the actual current source, including real deterministic producers,
projection/archive consumers, retained-file custody and Git CAS operations.
The canonical `skills/` copy is the source selected for this continuation.
The repository-only `source-peers/native-runtime` composition was separately
materialized and checked because its whole files differ. No runtime source fix
was justified by the observed results.

Across nine invocations, 105 tests passed, one authentic-probe test was skipped,
and three CLI cases stopped at the local interpreter-custody gate. These counts
are a test inventory, not R0039's acceptance denominator. R0039 original14,
amended criterion 5, OR, C02, W-FULL and N1 remain distinct obligations.
Original acceptance and independent receiving are **not established** here.

The exact machine-readable record is `SOURCE_QUALIFICATION.json`. The inert
OR, C02, W-FULL and N1 packets are in `INPUT_PACKETS.json`. Every unknown owner,
grant, host measurement and current-state input is explicit; nulls are missing
inputs, never values to feed to an accepting consumer. No native operation
record or grant was manufactured.

## Source identity and copy selection

| Subject | Exact identity |
| --- | --- |
| Repository | `theislampill/IMPLEMENTAUDIT.md` |
| Findings branch observed | `engineering/dg16-dg18-findings-20261115` |
| Source commit | `e4cba42cb5704f00b78d64e43f5da88501c28229` |
| Source tree | `7dd2b0b3921eb764669eaad98a9f0fd94f873c84` |
| PR255 head observed | `5277eb82bac6c10e190238afb54eda112eba284b` |
| Baseline before evidence authoring | Clean working tree |
| Runtime changes made | None |

Issue 215's owner map and root `AGENTS.md` name `skills/` as canonical source.
More decisively, the recovered actual H0 `INPUT_TEMPLATE.json` at
`faaa43e068bc758e28f1953d4204ce6aae1e543d` explicitly selects these core paths:
`claim-run.sh`, `claim-run-rotation.py`, `rotate-canonical-state.py` and
`canonical_rotation_inputs.py`. The template binds historical source `8ee4ae44`;
its old claim/shell pins are not a current launch manifest. The OR helper and
input-adapter pins in that template still match the current core copies.

The peer README defines a separate repository-only composition named
`R0039_ORIGINAL14_OWNER_WITH_R0033_VERIFIED_READ_VIEW`. It supplies no native
admission. All 17 declared peer byte/hash pins and both frozen core dependencies
were verified before the overlay was exercised. The overlay was made only in a
separate task-owned clone with its own Git common directory. No protected
controller, receipt, profile, assignment or pending store was copied.

| Owner | Core SHA-256 | Peer SHA-256 |
| --- | --- | --- |
| `rotate-canonical-state.py` | `7112fdbe9722754cb6ece6f102b06533d3c3c89902f23ade53a7477b5a276678` | `8ea4b99162ebaf4f1338fbb9086b4da2fd58d94dea3cac6d82d64744520de631` |
| `claim-run-rotation.py` | `866e9f669625fe3df29a3b3f4ff58f32d77a8a4b905ff8d6bffc9ef34561e42d` | `60b96654209ffa21091ce0bdcda1135d73ff0c116750842277019a1b26787a4f` |
| `canonical_rotation_inputs.py` | `dc95d31e4a1fabb922013fe4b1da051ba5ec6194f12a5ca0eb02a6eef1637d76` | `96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489` |

The four requested function bodies are byte-identical between core and peer:
`check_rotation_observation_v1`, `rotation_trigger_v1`, `rotation_payoff_v1`
and `propose_c02_correction_v1`. Their exact segment hashes and locations are
recorded in the JSON report. Whole-file equality is not claimed.

The two current core owner files remain byte-identical to PR255's integrated
D18-1 head. The actual 291,624-byte claim module was imported by the tests; it
was not replaced with a smaller surrogate. The Windows mode correction is
present with SHA-256
`e9e85dab4dcbd0a258400480b3c4900df0eebbd555df20653168918a638c0356`.
Its previously qualified Windows/Linux banks were not replayed because this
work changed none of their interfaces.

## Executed controls

All invocations used Python 3.12.14. Token-dependent controls used an isolated
task-owned `tiktoken==0.13.0` installation and exact `cl100k_base` encoding
SHA-256 `223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7`.
The authentic host owner and clocks were explicitly constructed in the source
fixtures. This does not authenticate host telemetry or supply an issuer grant.

| Source / existing fixture | Observed result | What the invocation establishes |
| --- | --- | --- |
| Core `input_contract_test.py` | 8 passed | All three OR arms, boundaries/nontrigger/payoff, exact envelope/freshness, C02 proposal/retry/conflict/newer-boundary discrimination |
| Core `native_input_adapter_test.py` | 30 passed, 1 skipped | Actual adapter parsing, lease/checkpoint/revocation/unknown handling; authentic retained probe absent |
| Core `native_or_rotation_test.py` | 11 passed | Real token counts through actual projection/archive/finalizer/readback; health-only and just-outside boundary; both payoff minima; stale/future/foreign/revoked/unadmitted lease refusal |
| Core `token_admission_test.py` | 5 passed, 1 environment error | Actual byte-only/token-only and nontrigger producer/consumer paths; changed encoding refusal; public claim CLI blocked before its operation |
| Core `c02_native_source_test.py` | 16 passed | Real source/census, issuer file custody, invalidation CAS, changed expected-old, cancellation/unknown, alias/physical-replacement refusal, separate grant scopes |
| Core `c02_cli_test.py` | 2 environment errors | Preserved fail-closed interpreter gate; accepting CLI behavior not qualified here |
| Peer overlay `input_contract_test.py` | 8 passed | Same pure contracts in the distinct source composition |
| Peer overlay `native_or_rotation_test.py` | 11 passed | Actual peer producer-to-projection/archive consumer composition |
| Peer overlay `c02_native_source_test.py` | 16 passed | Actual peer C02 source/census/custody/CAS composition |

The exact stdout/stderr files are retained under `test-evidence/`; each is
hash-bound in the report. The three CLI errors are retained, not relabeled as
passing. No product source was changed to make the host pass.

### Local CLI environment refusal

`claim-run.sh::select_claim_python` first requires an installed system-reference
ELF and a root-owned, non-writable resolved path. The workspace runtime is under
`/opt`, outside the admitted system references. The available
`/usr/bin/python3.13`, `/usr/bin` and `/usr` have UID 65534; `/` has UID 1000.
The original guard therefore cannot qualify either candidate on this host.

The guard explicitly permits a venv symlink to a matching installed binary.
The early hypothesis that the symlink alone caused refusal was ruled out by
reading the complete source predicate. No ownership, source guard or system
path was modified. A copied task-local executable would not meet the actual
installed-identity predicate either.

The next useful verification is the same three existing CLI cases on the
owner's admitted Windows host or a normal root-owned POSIX environment. It
requires source engineering only, not a native model episode. The affected
checks are the token CLI case and the two C02 CLI cases listed above. A native
launch still requires its separate fresh operation-bound grant.

### Prepared source-only CI continuation

The principal controller authorized a narrow way to finish those three cases
on an ordinary root-owned runner. The prepared workflow is
`.github/workflows/dg18-source-qualification.yml`, and its only trigger is a
push to `engineering/pro-executor-dg18-source-20261115` in this repository.
It has `contents: read`, no manual dispatch, no native-host operation record,
and no model process. The principal controller must independently review it
before the already-authorized guarded engineering publication.

`ci_source_qualification.py` first checks all 13 recorded source pins, the four
clean Git trees containing copied scripts/templates and fixture code/data, and
the real system interpreter's root-owned path. It invokes only the one existing
`TokenClaimAdmission` case and the two existing `CorrectionCLI` cases. These
fixtures use their existing explicitly constructed authority seams and
disposable repositories. No test guard is patched by the runner. The dependency
step installs exactly `tiktoken==0.13.0` into the ephemeral runner's system
interpreter and verifies the tokenizer-data hash. It changes no user home.
Success requires exactly one and two reported unittest cases respectively,
zero exits, and plain `OK` results without skips. A timeout stops further
testing and records descendant termination as unverified.

Local preflight verifies the source pins and refuses the same UID-custody
predicate before running fixtures. `test-evidence/ci-local-preflight.json`
preserves that negative result. Python AST, YAML configuration, and each shell
step are checked without rewriting the interpreter guard. A hosted positive
result remains pending; the local environment is not disguised as an admitted
system interpreter.

The upload allowlist contains only the source-test preflight/result JSON,
selected dependency versions, and stdout/stderr. Fixture stores, controllers,
encoding data and generated native-looking fixture records are not uploaded.
This candidate's hosted result is **pending**. A green source-only job would
qualify the three fixture paths at that exact source; it would provide no
actual C02 issuer authority, native OR observation or original acceptance.

### First hosted configuration failure and bounded correction

Root published the reviewed source tree `ddf65c6f7e351cf98633598e8dff81f69ccb9bc3`
as remote commit `fbe537794f886b31d85ccd5c665c31ad8070f435`. Actual
[run 43675724954](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/43675724954)
failed immediately, with zero jobs, check runs and artifacts. It executed no
source cases. Preserve this first failure independently of any later result.

`CONFIG_VALIDATION.json` records the demonstrated configuration defect:
job-level `env` referenced `runner.temp`, although GitHub does not permit the
`runner` context at that location. Actionlint 1.7.12 rejects the exact published
workflow at line 27, column 31. The GitHub server's literal validation
annotation was not retrieved; the actionlint diagnostic is local evidence.
Generic YAML parsing and `bash -n` had not covered this semantic validation.

The correction removes that one assignment and adds two lines to the preflight
shell step. The shell exports the same task-specific path under `RUNNER_TEMP`
and records it in `GITHUB_ENV` before invoking preflight. Export makes the value
available in that step; GitHub makes the recorded value available to later
steps. The checkout, source pins, interpreter guard, three fixture selections,
permissions, branch restriction and artifact allowlist are unchanged. The path
remains outside the checkout and outside native stores.

The corrected file passes actionlint with no ignored diagnostics and passes all
four shell syntax checks. No source tests or hosted jobs were rerun by the
author. The prior independent review remains an immutable review of its
original subject; this configuration delta requires distinct receiving before
root's guarded publication. These records claim configuration validity, not a
hosted source-test pass or native acceptance.

Primary rules: [GitHub context availability](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#context-availability)
and [setting an environment variable](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#setting-an-environment-variable).

## Remaining concrete inputs

### OR

The source thresholds remain byte count 131,072, token count 32,768, configured
headroom at most 2,500 basis points, minimum reductions of 32,768 bytes and
8,192 tokens, and a maximum observation age of 30,000 ms. An OR arm does not
waive either payoff minimum. The 258,400-token configured policy is not a
measurement of model capacity. Emulated fresh-canary counters do not replace
the original authentic host observation.

The packet needs the actual admitted observation producer and issuer/grant;
exact host/binary/config/model applicability; current controller, claim, run,
pair and receipt; exact source bytes/tokens; the authentic exact-usage,
reported-window and terminal cutoff; and observation identity/scope/freshness.
Matching caller-authored JSON or hashes cannot provide these. The proposed
input function's output retains `PROPOSED_INPUT_ONLY_NO_EFFECT_AUTHORITY`.

### C02

The packet names the existing `CONTINUITY_ADJUDICATION_OWNER` and the actual
configured issuer/census fields. It still needs that owner's identity and
applicable grant, actual erroneous-event evidence, exact expected-old
pointer/receipt/permanent-marker/controller/claim/run identities, complete
later-boundary and prior-decision census, and retained source/issuer admission.

The existing configured source is explicitly scoped to controlled,
nonprotected fault injection. It cannot appoint itself to adjudicate an
arbitrary historical event. Its append grant and conditional fresh-transition
grant are separate. `propose_c02_correction_v1` is a pure proposal and yields
`NO_EFFECT_AUTHORITY`; it does not perform append-only publication.

After lawful input admission, the original sole publisher must perform and
read back append-only correction, exact retry/idempotency, conflict/replay/
ambiguity refusal and immediate admission of a genuine newer boundary. Keep
generation-v1, projection-v2, the fourteen-field receipt-v3 and F0–F9 ownership
and ordering. No model turn is intrinsically required by C02; authentic source
custody and the specific authorized effect are still required.

### W-FULL

The actual historical Windows20 source manifest and runner are pinned in the
packet. Its entitlement file is literally `UNGRANTED`. The historical source
`8ee4ae44` is not a manifest for the present source and cannot launch it.

A current final operation record must bind a native Windows host, its actual
physical tools, current source, current preimage and owner map, the exact
pointer/receipt/marker tuple, both concurrent DG16 and DG17 owner originals,
the common live window, and the independent receiver. The owner must grant
that exact final operation. The two concurrent owner originals have not been
received here.

Retain the prospective 60,000 ms / 201,326,592-byte peak aggregate job committed
memory envelope, zero baseline subtraction, complete descendant accounting,
and terminal job `ActiveProcesses=0`. The measurement does not need a model
turn. It also does not relax OR's 30-second freshness or erase the original
5-second/64-MiB calibration failures. The historical Windows20 wrapper
explicitly assigns zero original-acceptance delta; it is an engineering
reference, not a substitute for original W-FULL receiving.

### N1 custodian request

The existing handoff reports second boundary prefix `162f88f4`, scope prefix
`45de02cb`, cutoff `109411`, reserved/pending/uncovered status, unresolved
currentness, no measured epoch and no consumption witness. Its source is
`DG18_CONTINUATION_PROGRESS_20261106.json` at
`/successor_session/H0_original_cold_receiving_body/five_fields/obligations/second_occurrence`.
Those are reported facts from the handoff; the full original record has not
been recovered here.

The exact request to the original DG18 custodian is:

> Return the original fixed accepting-source selection containing
> `pending_owner {store, session_id, owner_id}` and
> `episode_owner {module_pin, repository, controller}`; its existing H0 owner
> attribution; and the exact assignment-bearing
> `<store>/compaction-audits-v1/<session key>/pending.json` for N1. Include the
> full boundary/scope identities, original physical source/cutoff binding,
> reservation, actual result, accepted-consumption witness or explicit absence,
> and all surviving uncovered successors. Preserve the original records and
> report their exact identities; do not recreate an owner from archival labels.

The only located custody address is the previously reported successor workspace
`/workspace/scratch/4bb1fcb57e58/successor/`. The actual custodian's identity is
not present in the retrieved material. The repository owner must route this
request to the person or conversation retaining that workspace. The archival
controller `r5-h0-native-facts-20261105-02` does not inherit the original owner.

The search was bounded to the current handoff, the actual H0/Windows20/C02
startup packet trees listed in the JSON, and exact-name default-branch search.
No assertion is made that private stores or every historical branch were
searched. No store or ownership value was inferred. Cold receiving can prepare
its comparison now, but the complete amended canary remains blocked on N1.

## Reproduction and independent receiving

Use the original committed source above, not the later handoff-only commit, as
the tested runtime subject. Commands use the existing fixtures:

```bash
python3 fixtures/canonical-state-rotation/input_contract_test.py -v
python3 fixtures/canonical-state-rotation/native_input_adapter_test.py -v
python3 fixtures/canonical-state-rotation/c02_native_source_test.py -v
python3 fixtures/canonical-state-rotation/native_or_rotation_test.py -v
python3 fixtures/canonical-state-rotation/token_admission_test.py -v
python3 fixtures/canonical-state-rotation/c02_cli_test.py -v
```

For token-dependent commands, provide the exact encoding through
`R0039_TOKENIZER_ENCODING`; use the pinned dependency version above. Set
`TMPDIR` and, where applicable, `R0039_C02_TEST_TMPDIR` to the task-owned
temporary directory. The two CLI invocations also require the source's actual
interpreter-custody predicate; do not patch or bypass it for receiving.

The peer check must use a separate checkout/common directory, verify every
manifest member and both frozen core dependencies, then overlay each member
to its declared `materialized_path` with the declared mode. Run only the three
peer invocations listed in the table. This is a source composition test, not an
installation or a native selection.

A distinct receiver should verify the complete report, exact pins, retained
failure classifications, and the missing-input fields. It may reuse unchanged
accepted banks at their original scope. It must not accept this author's work
as independent final receiving, reinterpret the three CLI errors, promote
fixture grants to authority, or declare original DG18 acceptance from these
source results.

There is no package/runtime source delta, so a new broad package/install bank
was not warranted. Final handoff checks are byte/pin verification, JSON
readback, declared test accounting, and `git diff --check`. Local evidence
authoring does not change native, release, merge or issue state.
