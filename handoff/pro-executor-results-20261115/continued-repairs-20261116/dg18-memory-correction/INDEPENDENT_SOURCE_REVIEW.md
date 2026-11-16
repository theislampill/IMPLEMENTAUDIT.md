# DG18 Windows process-overhead correction — distinct source review

Date: 2026-11-16. Reviewer: DG18 receiving lane, distinct from the G2 author. **Disposition: PASS at the frozen nine-path source scope; no blocking source finding.** This is not Windows execution, memory-envelope acceptance, a grant or permission to reuse the consumed operation.

## Exact reviewed candidate

- Worktree: `/workspace/scratch/7fbb79f74aa4/recovery/dg18-memory-correction`.
- Base commit/tree: `775d6a0add0a1edcbc7f6cf5ccd68d350757fe8a` / `66607502c26f533416aa9cc00b3b5728e1e0e11e`.
- `SOURCE_FREEZE.json`: 2,600 bytes, SHA-256 `b8017f55c1c7dd58145f61eaa5a9e789c61d56a1d3ad52474a9c905e20a00464`.
- `SOURCE_CORRECTION.diff`: 47,838 bytes, SHA-256 `b32d7d851b8e3033fc84d99c97f9be20126ba7acdf5c41133e132d75a71e1eb0`.
- Final author report: 14,333 bytes, SHA-256 `21caaec86806da983fcb1f3c91cab74a7d4603fcba92d44818396b640447e3cd`.

The actual worktree has exactly the nine frozen changed paths. Every body length and SHA-256 matches the freeze. Eight tracked files are modified and one retained historical reader is added. No tracked mode changes were observed. The active `read-canonical-pair.py` and `rotate-canonical-state.py` remain Git mode **100755**. The added `source-peers/native-runtime/skills/implementaudit/scripts/read-canonical-pair.py` is also **100755**. The other six changed files remain **100644**. Publication must preserve this actual mode mapping.

## Source findings

### 1. Consistent direct-Git selection

The claim and rotation owners now select the existing fixed physical `C:\Program Files\Git\ucrt64\bin\git.exe` before the retained mingw64/cmd/bin alternatives. Their existing regular-file/symlink refusal remains in place. Both Windows child environments follow the selected executable directory; the claim owner's Git-root derivation recognizes both direct layouts. The projection module uses `PureWindowsPath` only for its explicitly Windows environment construction. POSIX selection, existing Git configuration controls, long-path settings and inherited-override exclusions remain unchanged.

The two owners are corrected together, preserving their shared custody expectation that nested owners select the same executable. The reader receives the same direct-layout preference and retains its existing cmd fallback and Bash invocation. The actual run43775060535 observations of 1,120 cmd-wrapper and 1,141 direct-ucrt Git processes establish the relevance of the missing layout. They do not identify the process responsible for the memory peak or quantify savings.

### 2. Early validator tail exec

The validator differs from base775 only by the `exec` prefix on the final Python invocation in the early `--claim-only` / `--claim-custody-only` branch. Interpreter selection, arguments, stdin Python body and claim/custody rules are unchanged. That branch owns no live shell cleanup resource or active EXIT trap; the later full-validation trap is outside this branch. The following shell statement is solely `exit $?`.

I inspected the actual production callers: the claim shell uses a success-dependent `&&` chain; the evidence-anchor checker rejects any nonzero result; observed-mutation validation maps any nonzero result to refusal; and initialization raises on any nonzero result while its Python parent owns temporary-directory cleanup. No inspected caller branches on exact signal value143 or admits a signalled validator as success.

The real POSIX probe's **143 versus -15** signal-status difference is preserved in `TAIL_CALL_BOUNDARY.json`. The final author report explicitly supersedes that record's initial conservative omission decision after examining these callers. This review accepts the change at their success/refusal contract; it does **not** claim identical signal diagnostics or a measured Windows process/memory reduction.

The meaningful `rotation_io` exit3 migration fallback is untouched. Reversing only the two updated companion pin literals reconstructs the entire original claim shell, including all resume/verify/require/invalidate fallback branches. There is no tail exec in `rotation_io`.

### 3. Exact active pins and historical reader preservation

The claim companion's projection and initialization-validator byte counts/digests independently match the changed files. The public claim shell's companion byte count/digest also matches. The composite negative-control fixture changes only the exact current-validator digest.

The added peer reader is byte-for-byte equal to both base775 and its recorded source commit `d2397406d51aa080209caa16897283b2e9cb5b61`: **27,208 bytes**, SHA-256 `c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8`. Its executable mode is preserved. The manifest change solely moves that existing frozen dependency into the existing peer file list with its original identity and materialized path. All pre-existing peer file records and all other manifest keys are unchanged. This prevents the historical overlay from silently consuming the repaired active reader.

The C5 transport/compiler/operational sources, custody implementation, all three Windows recorder/accounting files and package budget remain byte-identical to775. Historical source registries are not broadened. Their pre-existing admission limits and the separately reported old compaction-owner manifest discrepancy are not awarded a PASS by this narrow review.

### 4. W-FULL source population

The unchanged `source_snapshot()` owner enumerates tracked `skills/implementaudit/scripts` and `skills/implementaudit/templates`. The exact existing population is still **44 paths**. The retained reader under `source-peers/native-runtime` is outside that population and is not a new claim/resume runtime input. Five active runtime bodies have changed; their hashes will therefore differ in any legitimately prepared later operation. No 45th path, speculative pin or future-operation admission is required or supplied by this source review.

## Verification received, without rerunning it

I reviewed the frozen five-control fixture and the author's digest-bound `FOCUSED_REGRESSION.json` (1,674 bytes, SHA-256 `2633f17e9b911efaf33e0646ba63c4352ac3fd7998f9f3f67236ccd87338e4c3`). It reports five tests, zero failures/errors/skips and exit0. The controls exercise modeled Windows selector agreement, physical-layout fallbacks, symlink-only refusal and sanitized child paths; actual ordinary POSIX PID/exit/refusal behavior; and the real early claim-validation body with valid, missing-template and malformed-schema inputs. These are relevant bounded controls. They do not represent native Windows execution. I did not rerun them or another suite.

I independently read the already-built archives, verified their exact lengths/digests, and compared all five changed runtime bodies with the frozen worktree. Both archives contain those exact bodies. Their existing packaging layout and executable entries are retained.

| Existing candidate artifact | Bytes | SHA-256 | Headroom below 589,824 | Original 2,000-byte reserve |
|---|---:|---|---:|---|
| `IMPLEMENTAUDIT.plugin.zip` | 586,957 | `75ee5638bd4b4d53e81bfad12cf7a6a959097d6c29df701c533397b77cd91473` | 2,867 | PASS |
| `IMPLEMENTAUDIT.skill` | 582,356 | `18bbf496c03c6e5ab2f567792b7cd04664b7cfe5e09161da35210ff2ea83c1b0` | 7,468 | PASS |

The canonical builder's revision 5 threshold of 1,240 bytes does not replace the original 2,000-byte reserve. The actual candidate passes both. These archives truthfully describe dirty worktree content based on 775, not an already-published successor. No archive was rebuilt by the reviewer. An initial receiver lookup used the plugin's path prefix for the standalone archive; selecting that archive's existing `scripts/` root resolved the lookup. There was no source or archive defect and no body change.

## Retained limits

Actual operation `e0ac5d2992e44b45e838802c571fa84e27542aa72afab6ebb05c015e3207ec23` remains consumed. Its real G0003 transition is preserved and its **250,466,304-byte** aggregate Job peak remains above the original **201,326,592-byte** limit. This repair does not change that result, reduce the accounting population, subtract a baseline, raise a limit, issue a retry or establish a future memory PASS. No OR/C02/C5 native admission, N1 reconstruction, criterion5 waiver or whole-issue acceptance is implied.

The reviewer performed source/artifact reads and exact comparisons only. No product source was edited, no test or build was rerun, and no host/native/protected operation was launched.
