# DG17 M09 R2 — independent receiving of setup failure

**Receiving PASS: authentic retained setup failure before any original or mutant consumer operation.** The actual driver invocation ended with exit 1. The result is not an original baseline failure, a surviving/killed mutant, or an M09 award.

Root's admitted operation `DG17_M09_SCOPE_CONSUMER_ORIGINAL_20261121_01` invoked the frozen R2 driver. The first fixture's empty-template Git initialization and read-only common-directory lookup both succeeded. Setup then attempted to write `.git/info/sparse-checkout` without first creating `.git/info`. The retained directory is absent, and the terminal traceback identifies that exact write at `run_m09.py:118`. No original or mutant operation is to be replayed from this failed execution directory.

This receiving review is read-only and advisory, authority **NONE**. It performs no product, original, mutant, oracle, Git, provider or controller operation. Root remains the execution and adjudication owner. The review is bound to Root's received current G0043 verification `72f182/0`, receipt `33c5296d4d9bf5ae370780b3d9895a8ce1b825cd`.

## Exact evidence received

| Evidence | Exact binding |
|---|---|
| Root admission | `/workspace/scratch/097486cde2dd/dg17-m09-root/ROOT_EXECUTION_ADMISSION.json`; 65,202 bytes; SHA256 `4221d4c7f73a2b89c4bac9f4851f8d79c1949936ddc9b341b0bda0970cfc31ef` |
| Actual driver terminal receipt | Retained `NATIVE_EXECUTION_INITIAL.json`; native **`52733a/1`**; 1,609 bytes; SHA256 `e42a833f02a569cf34910fa210858fb93de97c908195ebf00a41ecd5718534c7` |
| Unchanged R2 packet seal | 11,903 bytes; SHA256 `ee8a88f3ed2826ad2df0ad3f35c3682bb1a175504ad9e6300f41ef2283b47aa8` |
| R2 packet receiving | All **66 members / 1,543,412 bytes** remain exact; no added packet member outside the admitted execution directory |
| Execution manifest | `/workspace/scratch/097486cde2dd/dg17-full-family-r2/execution-01/EXECUTION_MANIFEST.json`; 8,631 bytes; SHA256 `4ac883a973496e3c86b90c47a72197066fc15aed65d6df213e0d9e6e1bb1e93f` |
| Execution receiving | All **47 members / 1,378,688 bytes** received exactly; no missing, unlisted or symlink member |
| This mechanical receiving | **`4b217a/0`**, this directory's `RECEIVE.py`; full result retained in `MECHANICAL_RECEIVING.json` |

`EXECUTION_START.json` binds the exact Root admission path/hash and R2 seal. The admission binds the prior independent source-review seal `38ccf098e86538e8fff7814c8747a85811e8d269acce3903e9209158c66bdbe5`, fixed inputs, runner and oracle. Both materialized runtime packages exactly match the sealed product source population, with only the declared validator mutation in the mutant package. Materialization is not execution of those modules.

## Actual process and state evidence

| Captured child | Native retained result |
|---|---|
| `0001-owned-residue-delete-git-init` | `/usr/bin/git -c init.templateDir= init --quiet <owned subject>`; PID 5; exit 0; empty stdout/stderr; completed `2026-11-21T23:00:31.621107+00:00` |
| `0002-owned-residue-delete-immutable-object-location` | `/usr/bin/git -C <historical source repo> rev-parse --path-format=absolute --git-common-dir`; PID 6; exit 0; 62-byte stdout, empty stderr; completed `2026-11-21T23:00:31.622919+00:00` |

Every captured stream matches its process record's full size and SHA256. The second command's output names the existing historical `.git` directory. The runner then wrote the corresponding object-store path into the disposable subject's `.git/objects/info/alternates`, as source line 117 specifies. This is an actual fixture write and is preserved; receiving must not report zero writes.

There is exactly one subject, `owned-residue-delete`. Its retained state contains the newly initialized Git metadata, empty refs, and the alternates file. `.git/HEAD` is the initial symbolic `refs/heads/master`; there is no index, checkout, `.git/info`, task work plane, `.IMPLEMENTAUDIT` directory or `.claimed` file. No fixture input record, snapshot, observation directory, final `RESULT.json`, or `BASELINE_FAILED_NO_MUTANT.json` exists.

`STOP.json` records `STOPPED_NO_AUTOMATIC_RETRY`, `FileNotFoundError`, the exact missing sparse-checkout path, and award false. The native terminal traceback independently identifies `main()` constructing fixtures at line 274 and the failed write in `Runner.setup()` at line 118. The source performs Git configuration/checkout afterward, ordinary claiming at lines 145–147, and actual original helper invocations only after all fixture setup returns. The terminal exception prevents those later steps.

These mutually consistent sources support **zero fixture claims, zero original helper operations, zero mutant helper operations and zero oracle calls in this invocation**. They do not erase the separately authorized earlier R2 product `--help` loading qualification. Direct-child exits and the driver terminal receipt do not establish a universal process-group absence guarantee; none is claimed.

## Classification and handback

The immediate cause is a missing fixture directory after explicit empty-template Git initialization. The consumer's authority predicate, preimage logic, mutation behavior, original oracle and family outcome were not reached. The earlier source-review PASS did not measure this fixture setup path; this failure remains retained as actual engineering evidence rather than being converted into a product runtime RED.

The R2 packet and failed execution remain immutable and unreplayed. Root's proposed separately frozen R3 fixture correction and pre-original Git/sparse qualification require their own narrow review and exact gate; this receipt authorizes neither repair nor execution. No expected case outcome, source guard, preimage or oracle change is justified by this setup failure.

The original M09 outcome remains unqualified and unawarded, with the earlier Seiri-policy survivor preserved. No case-row, terminal-clause or whole-DG17 claim follows. Denominators remain **36 cases / 14 mutation families / 17 terminal clauses**; M10/M11/P02 remain outside this operation.
