# Independent receiving of the G2 workflow pin correction

Disposition: **PASS — bounded source integration correction only.**

Reviewer: delegated DG18 recovery agent, independently reviewing Root's G2
candidate on 2026-11-15. The reviewer did not author or edit the G2 candidate,
run its adapter, repeat a computation, launch a protected operation, or publish
anything.

## Reviewed candidate

Worktree: `/workspace/scratch/7fbb79f74aa4/recovery/g2-pin-closure`.
Base: `bc3c8e6feca551d7eaafea071b5d4a6e5868de36`.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `.github/workflows/dg16-r5-full-g2.yml` | 21,123 | `355e094f3352a4890af1b91ec28939be8c63d2679aeb7bb5c74776f8c9db56af` |
| `qualification/dg16-r5-full-g2/run.py` — unchanged source | 84,859 | `e8576425bcbb260e3d2c21c11e510d51f0549756ab0b8dcc14cfdce7a96de15b` |
| `handoff/pro-executor-results-20261115/continued-execution-20261115/g2/PIN_CLOSURE.json` | 1,067 | `51544beb4cf417bff58c1e929cc04ac70c72e3a36e61512d3d6d466b9046e779` |
| `handoff/pro-executor-results-20261115/continued-execution-20261115/g2/G2_COMPARISON_AND_PIN_CORRECTION.md` | 2,170 | `00fdb25d3b0bffca362fd579fc2bef197ef95812c816ff5c908b3e779500ddb0` |

The before-workflow SHA-256 is
`ef2e6a22da49d300eb54929ef29fdcec41378bb2191fa9fbd910f16631e25906`.
The old expected adapter digest is
`8bb3882cd6390b480c3109c9a40d23f6ff2f2e48d73d97381a5b49ad38734b58`.

## Independent checks and finding

I read the entire tracked workflow diff and the two accompanying records,
then independently hashed the actual adapter and workflow bytes. The old
workflow contains exactly 19 old digest literals and zero new digest literals;
the candidate contains zero old literals and exactly 19 new literals.
Replacing those 19 new literals with the old value reproduces the entire base
workflow byte for byte. Forward replacement also exactly reproduces the
candidate.

The actual `run.py` body is byte-identical to both the base worktree's tracked
body and the published source body at
`fb1e78769cf4932741e1c2c9664c02d14413fb24`. Its SHA-256 equals all 19 new guards.
The workflow YAML parses, the complete parsed structure matches the base after
reversing only the hash substitution, and `git diff --check` passes. The sole
tracked modified path is the workflow; the accompanying records are new
evidence files.

This closes the concrete stale-pin defect identified as G2-RCV-03: those guards
would reject the actual corrected adapter before its corresponding calls.
Binding them to the already published body makes the source integration
consistent without altering the adapter or its comparison policy. The exact
reverse-byte equality establishes that branch selection, expected-before
guard, job boundaries, source subject, approval inputs, command arguments and
all other workflow behavior are unchanged by this correction.

No additional source defect was found in this narrow correction. No runtime
test was required to establish the exact literal substitution or body identity.
This is source receiving; it is not an observed hosted execution of the
corrected workflow.

## Authority and historical limits

The records explicitly preserve the unavailable historical failed-relation
witness and keep historical G2/M2 acceptance open. They do not reconstruct a
missing relation, broaden equality, or reissue policy/native adoption.
Previously received computation and adapter-control evidence is reused at its
existing scope; this review does not repeat or independently re-earn it.

The candidate does not itself supply a new protected admission or authorize a
host21 update. Publishing this correction on an ordinary engineering branch
and any later protected operation remain Root's separately bounded actions.
This review made no remote mutation and does not assert a fresh global census
of remote refs. All original source/currentness/review/Root/closing and
protected-effect gates remain applicable.
