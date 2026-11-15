# DG17 Stage A step-07 refusal: cause and correction (Fable 5.2 author, Opus 5.5 checked)

**Verdict: a defect in the Stage A driver (`stage_a.py`), not in claim-run.sh or the interlock.**

## Cause
- Stage A ran `claim-run.sh --controller <c>` (step 06). That only *prepares* a pending initialization ref.
- Stage A then went straight to `--resume-controller` (step 07). Step 07 needs the published controller ref `refs/implementaudit/controllers/<c>`, which only `--activate-controller` creates. The failure path is `discover()` → `--current-controller` → `git rev-parse` exit 128 → "predecessor/custody verification refused".
- `references/continuity.md` (line 46) requires existing `--controller` callers to activate explicitly after authoring. Opus confirmed that `stage_a.py` contains no `--activate-controller` call.
- **Second defect:** the STATE that `stage_a.py` writes can't be activated. It uses an absolute `Run root` and `Phase: intake`, and it has no `phases/phase-1.md` and no ROADMAP phase table. `_validate_initialized_content` (claim-run-rotation.py:4672) refuses it.

## Correction
`stage_a.step07.patch` changes 13 lines:
- a relative Run root, Phase `1`, a ROADMAP table and `phases/phase-1.md`;
- new steps 06a `--inspect-controller-initialization` and 06b `--activate-controller --expected-initialization <token>`.

Steps 07–10 are unchanged. The fixed driver is `stage_a_fixed.py` (sha d24fe5fd…).

## Evidence (offline, fresh clones of b0fcb565; no Codex or native step)
| Case | Result |
|---|---|
| Original sequence (replayed) | Step 07 exits 1 with the same message as the real Stage A |
| Fixed sequence | 06a 0; 06b 0 (ELIGIBLE_FOR_NORMAL_CURRENTNESS_ONLY); 07 0 (receipt G0001); 08 and 09 0; 10 nonterminal-yield ok |
| No activation | Step 07 refuses |
| Stale token | 06b refuses ("token is absent, stale, copied…") |
| Source tampered after prepare | 06a refuses |

Steps after 10 passed only with a **synthetic** session id. That is not native evidence. `stage_a_fixed.py main()` itself was not run end to end; Fable's replay calls its real `write_state`.

## Consequences
- **Pins:** `stage_a.py` is pinned (the OPERATION_A readset and parent_launch_a DRIVER_SHA). The fix changes `operation_sha256` (9b871228…), which the spent grant and episode window bind. **A new operation identity and a fresh owner approval are required.** The spent episode must not be retried.
- **Residue left by the real Stage A** (reported, not cleaned): `case-native-01/` together with its clone's pending init ref, run dir and lock file; the spent EPISODE_WINDOW, grant and parent-A-01 records. A new episode needs a new case path, because stage_a asserts that the case does not exist. The main repository was not touched.
- **Codex limit:** the next episode needs Codex model turns, which are unavailable until 2026-11-20 unless Codex credits are added.
