# Fresh independent receiving: canonical02 and diagnostic02

Receiver: `/root/recover_terminal`. This is a newly authored evidence receipt after scratch loss. It does not impersonate the earlier reviewer or reconstruct that reviewer's signature. The receiver retrieved the existing GitHub run records, Git commit identities, jobs, complete logs, comparison, and diagnostic artifact, then checked the retained evidence. No workflow was rerun, no product or remote branch was changed, and this receipt issues no Root award.

## Disposition

**The named public evidence is recovered and verified.** Canonical02 finished successfully; diagnostic02 failed before producer selection. Both conclusions and their different scopes remain intact. The reproducible evidence verifier reports **83 checks passed**. These are evidence-integrity assertions, not new product tests or a new execution occurrence.

| Subject | Canonical02 | Diagnostic02 |
|---|---|---|
| Run / attempt | `45690722389` / 1 | `45691022204` / 1 |
| Job | `139475142088` | `139476172173` |
| Actual commit | `0dd737b6da443b2e015901e3a27661b2421a1ce9` | `272c8bde46d760a8fe76a979bdb09dc1ab3661c2` |
| Actual tree | `6b3d686b7f6d220dad0aaf077ec728fd34b41951` | `bd542cf2555862146f3623ac4db67b270dcf8c3f` |
| Sole parent | V21 `338c4c36d2ac95ca24345bc92fe8c53d66eaa15d` | operator C `a8fb8473a766e4b4a71c46e4207b098ccd8857ca` |
| Platform terminal state | completed / success | completed / failure |
| Runner image | `20261116.133.1` | `20261116.376.1` |
| Applicable limitation | C5 prerequisite remains UNQUALIFIED | G1 maintained-input acquisition fails; result UNQUALIFIED |

Sources: [canonical run](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/45690722389), [canonical commit](https://github.com/theislampill/IMPLEMENTAUDIT.md/commit/0dd737b6da443b2e015901e3a27661b2421a1ce9), [diagnostic run](https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/45691022204), [diagnostic commit](https://github.com/theislampill/IMPLEMENTAUDIT.md/commit/272c8bde46d760a8fe76a979bdb09dc1ab3661c2).

**Image correction:** an inherited note named `20261122.23.1` for canonical02. The exact retained log instead says `20261116.133.1` at line 18. Diagnostic02's retained `HOST.json` says `20261116.376.1`. This receipt uses the primary evidence; neither host's observations are substituted for the other's.

## Canonical02: actual successful package execution, bounded scope

The entire canonical job log is retained without loss: **571,934 bytes**, SHA-256 `7d64b91dc0c396aa494996cec89a8356be1e0e486acd7e3e320f88f4e71d25ab`. Its BOM, Unicode and one NUL are preserved. The actual terminal marker is:

`2026-11-25T21:06:08.3363675Z verify-package: ok`

GitHub reports success, with the run's final `updated_at` at `2026-11-25T21:06:10Z`. The maintained `Verify package contract` step invokes `bash scripts/verify-package.sh` without `continue-on-error`. All reported job steps succeeded.

The comparison against sole parent V21 contains exactly two modified paths: `.github/workflows/validate.yml` and `fixtures/semantic-preservation/cases.json`. The workflow narrows triggering to the named newly created branch, attempt 1, read-only repository permission, and a 120-minute timeout. The fixture changes only `package_evidence.builder_sha256` to the actual unchanged V21 builder's SHA-256, `0310b26990bf95ee67a143c3378ef315cbef92b1d70ca9d7cb0929d5b03c0854`. The builder is 53,261 bytes and identical in V21 and canonical02. Thus this is successful execution of the named fixture-corrected V21 successor; it is not a claim that untouched V21 passed byte for byte. No additional product, runtime or registry path is changed in that comparison.

The C5 prerequisite remains **UNQUALIFIED**. Its observational step has `continue-on-error`; platform step success cannot replace its record. The retained C5 observation records no native admission, no acquired provider, and no start of the original 19. Its independent public source clone returned 128 (`invalid index-pack output`); passwd NSS was not files-only. Eight of twelve fixed input pins matched. The four mismatches were `/etc/ld.so.cache`, `/lib/x86_64-linux-gnu/libc.so.6`, `/lib/x86_64-linux-gnu/libpthread.so.0`, and `/lib64/ld-linux-x86-64.so.2`. Their actual descriptors belong to canonical02's host only.

`canonical-declared-skips.json` preserves 44 explicit skip records. This number is a log-record count, not a count of unique acceptance predicates. Windows-only controls and other declared skips remain skipped. The policy finalizer records retention of the job-owned AppArmor prerequisite until VM disposal; it does not prove that a future disposal happened.

### Maintained old-reader/archive observation

At `2026-11-25T20:18:24.9919732Z`, canonical log line 836 records actual success for `test_TC06_retired_rotation_policy_keeps_old_readers_and_archives`. The V21 source for this case is retained. It constructs a native generation, restricts the owner interface to three reader operations under a constructed retirement policy, materializes the pair, checks unchanged implementaudit refs, and actually resolves nonempty typed history archive pointers. It checks `ARCHIVED_ONLY_HISTORY`, `INVALIDATED_CURRENT_USE`, original scope, and retained historical refusal.

This is applicable evidence for **M6 L07's maintained old-reader/archive component**. It does not establish actual global retirement, lifecycle liveness, or a whole M6 row on its own.

## Diagnostic02: exact failure recovered without false native success

Artifact `15057804995`, named `dg16-g1-hosted-45691022204-1`, is retained as its original ZIP: **10,599 bytes**, SHA-256 `b9bc59702c4310fd2d0380f181f7ee7fba814220e478bfaca135af5c83766e3e`. ZIP CRC verification succeeds. It contains nine members, and all eight data members match the manifest's exact bytes and SHA-256. The manifest itself remains the ninth member. The complete diagnostic log is also retained: 87,284 bytes, SHA-256 `3362ec1f5a27dca461d86b1c918d105d66e410fc9142a70e28be659a357ac7a1`.

Preparation, continuity handling, input preflight, the native bank and prerequisites passed their reported steps. The maintained acquisition then stopped before selection. `OPERATION.json` says `MAINTAINED_INPUT_ACQUISITION_BEFORE_SELECTION`, `selected_acquisition_key: null`, and `producer_owner_invoked: false`. No actual original dispatch/artifact counts were exported. The two named native-bank tests report PASS within their stated scope; this is not a complete native bank or governed-pair award.

The exported failure is `UNCLASSIFIED_EXCEPTION`, `ValueError`, at step `g1`, with message length **82 bytes** and SHA-256 `1a5ceb58a197d1e6160f674ca6e6cda187be125429b5683a2ffaeef35b91e8e8`. The unchanged public V21 source at `scripts/work-graph-c5-provider-inputs.py:333` reconstructs the exact message:

`C5 additional provider native input differs: /lib/x86_64-linux-gnu/libpthread.so.0`

Hash and length match the export exactly. The source compares kind and the tuple of bytes, SHA-256, mode, resolved path and link. **The diagnostic export does not identify which of those fields differed or export this host's actual native-file digest.** It would be incorrect to copy canonical02's observed digest into this diagnostic or equate this diagnostic error with a different earlier main run.

G3 was neither prepared nor received. The exported G3 diagnostic is only at `AUTHORED`; root consumption, receiving, invalidation, resume currentness, frontier recomputation and canonical update are `NOT_STARTED`. Finalization records the expected `EPISODE_INCOMPLETE` consequence. The terminal result remains `UNQUALIFIED`; original G1/G3 awards are null and full G2 is false.

Cleanup records all children reaped and source/runtime unchanged. The operation did have host effects: it changed the existing job's passwd NSS configuration to files-only and retained the configured file and job-owned AppArmor policy until VM disposal. This receipt does not claim zero effects or independently witnessed future disposal.

## What Root may receive from this record

The canonical evidence is available for the named successor's Q02 canonical-execution limb, Q07 published-branch CI limb, DG17 ordinary canonical qualification, and the specific M6 L07 old-reader/archive component. This receipt does not issue any of those awards; Root must apply each original requirement at its actual scope.

No whole-cell closure, V03 correspondence/same-job award, V05 unregistered-reuse award, Q06 actual governed pair, original G1/G3 award, full G2, aggregate five-native-predicate award, unobserved Windows behavior, confidential ingress, authentic host boundary or future VM disposal is established.

## Retained evidence and reproducibility

`RECEIVING.json` is the machine-readable newly authored receipt. `VERIFICATION.json` contains every evidence check. `verify_recovery.py` only reads retained evidence and emits derived verification; it never executes product code or calls a remote service. Raw decoded GitHub API records and exact decoded UTF-8 logs, the original ZIP and its extracted members, the API comparison, immutable public source snapshots, source bindings, C5 observation and explicit skip list are included. API JSON files are retained decoded content with a final newline or pretty-serialized structured connector output, not claimed to be raw HTTP response bytes.

`MANIFEST.json` binds the recovery package files other than itself. No temporary signed download URL is stored in the package.
