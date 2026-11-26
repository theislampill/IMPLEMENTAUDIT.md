# V03 actual occurrence: independent failure receiving

Receiver: `/root/recover_terminal`. This is fresh receiving of an actual external hosted occurrence, not a reconstructed prior review or an acceptance award.

## Exact occurrence and custody

Run `45725097963`, attempt 1, job `139592823277`, executed workflow commit `779d1b1f04e34d41d18f747304edb81d5cc3cfaf`, tree `759412fcf62aee4179ad4678d6fae89670f4e576`, sole parent and frozen product subject `2e72a912136607e464e953c71fc8e2b44d047d92`. The actual GitHub conclusion is **failure**.

Fresh API reads independently confirmed the run, job and sole artifact. Artifact `15080578372` is `dg16-full-registry-45725097963-1`, 11,823 bytes, SHA256 `39a366d5d061009b3a63caab40b1770b722c8794d4df891d84ba061b021e5aeb`; this equals the provider's actual digest. All six declared members and the seventh manifest file match the downloaded ZIP. The full job log is 110,973 bytes, SHA256 `a848568b37568a65d1402d261209d044f1e076c7d35cb2ba3175d4f9df400a0d`.

`verify_actual.py` records the checks, including independent raw Git commit/tree/parent readback and the actual maintained `validate_public_proof` consumer applied to the exported proof projection. No new hosted action or rerun was performed.

Run: https://github.com/theislampill/IMPLEMENTAUDIT.md/actions/runs/45725097963

## What actually completed

The legacy route and DAG route both returned exit 0. The DAG's 119 mapped nodes all report PASS and terminal true. Legacy per-node trace is explicitly unavailable: its 119 node rows remain UNSETTLED, so no per-node legacy success is invented from its whole-process exit.

Both routes supplied 112 actual report slots, with 195 declared skips and zero expected failures each. The receiver retained the declared original scope limits. Source bookends agree on all 1,972 files and 173,715,501 bytes; the source mutation flag is false. The exported proof reports equal source/runtime and raw-census bookends. The real capture receiver reached `RECEIVED_COMPLETE_RAW_PAIR`.

These completed observations do not establish full normalized correspondence. The pair phase succeeded at 02:07:34.9182558Z. The subsequent receiving step returned nonzero at 02:07:55.8996664Z; the first failure is `FULL_PAIR_NOT_COMPLETELY_RECEIVED`. Finalization then correctly refused `EPISODE_INCOMPLETE`.

## Exact failed relation

Normalized stderr is equal. Portal, reproducibility, pending-durability and pending-loader relations are equal. Normalized stdout differs: both streams are 204,118 bytes long, with first differing offset 60,394.

- Legacy normalized stdout SHA256: `9ef93f3ec89c1678007b43d4891dae5afa5c82028e89c834997c888671829fc4`.
- DAG normalized stdout SHA256: `8d53b0d2bbd8a9a967a6f0f282732763a96082cbeb572f2f08f1b0e545362812`.

The whole relation has two witnesses. Their retained location hashes independently recompute to `['result', 'stdout_sha256']` and `['stdout']`. The first witness's typed value digests also independently equal the hashes derived from the second witness's stream descriptors. Therefore the two witnesses are **one underlying normalized stdout mismatch and its derived hash**, not two independent semantic discrepancies.

The maintained pair driver's receiving function returns zero only when the raw pair is complete and every full relation is equal. Its nonzero result here is consistent with the actual false equality. The outer operator's refusal is consequently correct; it is not a missing-file or stale-receipt bookkeeping defect.

## Why no correction is claimed yet

The public projection retains the mismatch offset and digests, but not the differing stdout bytes or emitting command. Its 7,468,524-byte private observation body has SHA256 `a484219a22938ba67a00a21c00a3b5ddcea1c084a14317c5f73531db3e5b5e52`; that body was not exported. No current access to the ended job's private captures is established.

The existing diagnostic localizer only addresses stderr. It cannot locate this stdout difference. An offset into an unavailable normalized stream is insufficient to distinguish a real behavior difference from an undeclared volatile field. No data-specific normalizer edit, ignored field, new equivalence rule, or assertion of benign nondeterminism is justified by this evidence.

A subsequent investigation must obtain an actual source-bound stdout location or reproduce a specific differing producer before changing any comparison rule. A bounded diagnostic observation could be prepared without weakening equality, but it would not retroactively prove this occurrence or guarantee that a repeated full run succeeds. This receipt does not authorize another operation.

## Terminal scope

No live review request or review artifact was produced. The live independent review, Root consumption and same-job closing steps were skipped. Final `RESULT.json` remains `UNQUALIFIED_OR_INCOMPLETE`, with original acceptance, full G2, full T14, G1, G3, C5, independent assessment and audit closure all false. Cleanup records all step children reaped, source and runtime unchanged, and no private output upload.

The failed occurrence remains spent. Its completed computation and matching component relations are retained at their actual scope; no whole V03 or programme acceptance award follows.
