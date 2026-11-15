# DG16–DG18 failure retrospective (Fable 5.2, read-only; Opus 5.5 spot-checked), 2026-11-15

**Summary.** Nearly every failure was in campaign-specific wrapper code: adapters, receivers, drivers and operator recipes. None was a demonstrated failure of the product under test. The wrappers were first exercised end to end inside the one-shot accepting operation itself. Each launch therefore found one defect, and each fix forced a re-pin and re-review cycle.

**Scale.** From `gh run list` since 2026-10-25; Opus re-counted these.

| Run family | Failed / runs |
|---|---|
| `full-g2-direct-host` | 20 / 20 |
| `full-g2` | 6 / 6 |
| `full-g2-current` | 2 / 2 |
| `g1-original-g3` | 25 / 26 (one is still queued) |

## Decisive failures
| Date | Operation | First failed check | Correction | Independently verified | Detectable before launch | New or old |
|---|---|---|---|---|---|---|
| Nov 10 | G2-08 (42903716750) | Stale loader pin | Regenerated | — | Yes | Old class |
| Nov 13 | G215 / G217 | Runner image rotated; 3.14 fork warning broke the pinned parser | Two image tuples pinned; slot-39 fix | Yes (canary 43604636517) | G217 yes; G215 only by a same-day check | Host change |
| Nov 14 | G131 (43613174937) | Root publication missed the recipient expiry (2.97 s left) | Standalone budget gate proposed | Failure received | Partly | Old gap |
| Nov 14 | G218 (43618983816) | Stale total `run.py:171` | Both literals fixed | Yes | Yes | Old class |
| Nov 14 | G219 (43623218185) | Stale component pin `protected_preflight.py:98`, found after the encryption was spent | One constant | Yes | Yes | Old dependency |
| Nov 14 | G220 (43640583300) | Both legs exit 0; receiving refused the real control names; a hidden second refusal on the `python3` interpreter path | Exact pinned name lists plus `python3` (82f4c3d1) | Author + Opus; not hosted | Yes (real output through the receiver offline) | Old latent |
| Nov 14 | DG17 Stage A | Controller never activated | 13-line driver fix (ef0c5282) | Opus, offline | Yes | New; episode spent |
| Nov 14 | DG17 Stage B | Packaged file refused Windows store custody | 158a16d2 + store privacy check (19521378) | Opus | Caught before launch | Old dependency |
| Nov 14 | DG18 | Windows mode test; D18-1 128 KiB bound | ef0e9481; 5277eb82 | Opus | Yes | Old latent |

## Top root causes (verified)
1. **Accepting operations were the integration test for unrehearsed wrapper code.**
   - G220's receiver had never been fed real producer output.
   - G218's review says the canary did not execute the full adapter check.
   - No test called the D18-1 path.
   - The Stage A driver was never replayed offline.
2. **Pins are copied by hand, so every fix churns.**
   - G218 had two copies of one total; G219 had one hash that was never propagated.
   - The G221 fix touches 13 pinned files and forces every decision and seal to be reissued.
   - The DG17 fix changes the operation identity, so it needs a fresh approval.
3. **Acceptance is tied to operator timing, one Codex thread and Codex quota.**
   - The work orders never mention G1/G2/G3, encryption or recipients.
   - G131 spent 327 s of 534 s on Root steps.
   - The operator accepts only Codex-session events, and Astra's thread id is constant in six files.

## Treatments, ranked
1. Rehearse real producer output through the unchanged receivers for every role and route (source/testing).
2. A single forward-pin and new-literal scan, with pins generated from one source (source/testing).
3. Dry-stage the operator chain, and run the standalone pre-sender budget gate. The owner sets its floor.
4. Replay native drivers offline up to the first model turn before any grant (testing).
5. A reviewed alternative evidence channel (owner protocol amendment), keeping authenticated independent receiving.

## Implementation-derived controls (not in the original texts)
- Keep them for now; trace each to its originating clause before changing it.
- The list: the maximum-encryption witness and recipient expiry, the one-shot sender, the 300 s and 600 s holds, the single 270-minute job, the thread-id constants, and the duplicated literals and shape regexes.
- Where to trace them: the criterion dispositions file exists at `dg15-dg16-sol-evidence-20261028/original48/`, and the originals are published at 585012cb.

## Opus corrections to the Fable report
Fable's report was stale on three points, corrected here:
- the DG17 Stage B custody and DG18 test fixes are applied and published;
- the package spare after B2 is 3 B, not 36 B;
- the dispositions file is not absent.

## Not verified
- The causes of the Nov 5–10 DG17 and DG18 hosted failures.
- G212/G213, which remain UNKNOWN.
- Whether the pinned name lists match the hosted population.
