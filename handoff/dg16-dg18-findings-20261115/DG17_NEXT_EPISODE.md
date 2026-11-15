# DG17 next episode: findings (Fable 5.2; Opus 5.5 confirmed B2 from the source), 2026-11-15

Files: `FABLE_WORK_WIN/dg17-next/` holds `release/author/` (the proposed set), `release/PINS.json`, `release/stage_b.receipt-dir.patch`, `tools/` and `sim/` (SIMULATED evidence).

## Stage A: sound up to its native step
The corrected `stage_a.py` (d24fe5fd…) ran its real `main()` in scratch, with only the Codex runtime start stubbed as a SIMULATED refusal. Steps 01–10 passed in 42 s, including the new 06a/06b activation. Step 07, where the real episode stopped, now passes.

## Stage B: two defects
- **B2: blocking; not fixable in the drivers.** Opus confirmed this in the source. Stage B step `02-owned-init` runs the packaged `skills/implementaudit/scripts/host-session-binding.py` (8b4f91a5…). Its `require_supported_store_custody()` (line 107) fails unless `os.name == "posix"`. The Stop handler, however, requires `os.name == "nt"` and looks up the binding through the same owner. **On Windows, Stage B therefore cannot pass.** A real episode would spend model turn 1 in Stage A and then stop at Stage B step 02. The fix needs a reviewed Windows store-custody rule in a **packaged** file. That means a new source head and a package-budget re-measure (canonical limit 588,584 B; b0 build 588,548 B).
  - Diagnostic only: with the gate bypassed in memory, init, bind, lookup and tombstone all pass with Stage B's expected values.
- **B1: fixed in scratch.** No driver created the receipt directory `<case>/evidence/native-stop`, so the Stop hook returned "block" and wrote nothing. A one-line `stage_b.py` fix (450d2956…) gets past it to B2.

## New operation record (not usable until B2 is fixed)
- `OPERATION_A.json` 60517142… with case `case-native-02`, plus the re-pinned launchers and bind script.
- Fixing B2 will change these hashes again.
- The draft owner-approval paragraph is in Fable's report (kept with the release files). It keeps every original limit unchanged.

## Step classification
**Codex model turns.** There are exactly two:
1. Stage A's observation prompt.
2. Stage B's qualifying prompt.

**Runtime calls** need the real binary and sign-in, but no model turn: runtime start, `thread/start` and `thread/resume`, config writes, and read-backs.

**Deterministic local work.** All of these can be done by Claude:
- the launchers and the grant and pin checks;
- source steps 01–17;
- store init, bind and lookup;
- teardown.

**Independent receiving:**
- post-A review;
- POST_B, T12 and original14 receiving;
- custodian certification.

**Timing:** Stage B must begin within 570 s of the window start, and that span includes Stage A and the post-A receiving.
