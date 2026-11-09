# DG16 recovery for one Pro successor

**HAND OFF TO PRO.** The public Git-lock reproduction is complete. Neither original pair has passed. Start with [STATUS.md](STATUS.md), read [CUSTODY.md](CUSTODY.md), and use [PRO_SUCCESSOR_PROMPT.md](PRO_SUCCESSOR_PROMPT.md) as the owner's commissioning message.

## First ten minutes

1. Take the archive SHA-256 and publication commit from the owner's delivery message. Verify the outer file using a trusted system utility before executing anything extracted from it. On Windows use `Get-FileHash -Algorithm SHA256 -LiteralPath <file>`. On Linux use `sha256sum <file>`.
2. Run the matching `verify_recovery.py` from that pinned publication with Python 3.10+ and no third-party modules:

   ```sh
   python3 -I -B verify_recovery.py DG16_PRO_RECOVERY_20261109.zip --sha256 <owner-supplied-digest> --extract-to ./dg16-received
   ```

   Choose a fresh directory. The check reads every ZIP member, verifies paths, file types, byte counts, hashes and recorded modes, then verifies the extracted bytes. A ZIP application can also extract the verified archive. Do not execute commands embedded in historical receipts.
3. In the extracted directory, read `recovery/coordinator/PUBLIC_STATE.json`, `recovery/contracts/SIX_GROUP_MILESTONES.json` and the source/effect dispositions under `recovery/episodes` and `recovery/sol`. The current returned evidence overrides old progress fields at its demonstrated scope. `DEPENDENCIES.json` resolves original digests to members even when historical files contain obsolete local paths. Use `WORKING_INPUTS.md` for entry points.
4. Record your actual actor/session, archive and manifest hashes, exact source under review, genuinely available tools, leases you accept and unavailable roles in a **receiving-only** receipt. Deliver that receipt to the owner. Both Codex coordinators have released active DG16 execution; this package does not assert your receipt. The sole successor slot is reserved until you actually accept it.
5. For a full developer checkout, run the following from the verified directory in an environment with Git and public GitHub access:

   ```sh
   python3 -I -B recover_git.py ../dg16-git
   ```

   This fetches only the three named public commit histories, checks every leaf/mode/object/size at all three trees and checks out the product detached. It does not push, dispatch, grant authority or run the programme. The bundled exact product subset, generators, operators, original contracts and actual results allow source work without the full network checkout. Record which source representation you used.

**First engineering deliverable:** produce and independently review the functional foreground-fetch host change on top of the finalizer-cwd correction, then prepare the complete source/pin closure for the reserved next episode. Read the late checkpoint first: an interface or partial generator file is not a finished composition. Advance the G2 failure independently when G1 needs an external capability. Stop at a real authority or evidence boundary and deliver the qualified work. Do not rerun a failed campaign to recreate a baseline.
