# DG16 G132 STATE

Author: Claude Fable 5.2, read-only advisor. Observed 2026-11-14 (remote refs and `gh run list` read live; transcripts read by grep/tail only).
Authority used: read-only investigation plus scratch work in this directory. Nothing launched, pushed, dispatched, encrypted or decrypted. No write to `/home/agent`, Astra/Sol directories or the Codex worktree.

Path shorthand: `A/` = `C:/workspace/ai/improveimplementaudit/plans/astra-r3-execution-20261114-01/`, `E/` = `C:/workspace/ai/improveimplementaudit/plans/astra-successor-recovery-20261112/engineering-return-20261113-01/`, `T/` = `/home/agent/pr255-g132-root-20261114-01/public-tools-source-01/` (WSL Ubuntu).

## 1. Latest G132 state

**State: SOURCE_READY, NOT_LAUNCHED.** No run, recipient, sender, journal or crypto exists for G132. `T/episode-01` and `T/publication-01` are empty directories.

| Item | Value | Evidence |
|---|---|---|
| Host commit | `a33b8d1cdb967124b1b0d4fe877cf9b283304798` | `A/g132-root-preparation/LOCAL_COMMIT.json` (sha256 `e03d3ac3…`) |
| Host tree | `e7b77a2e8cdf6d7409a694efcbb3b13483bac5c9` (verified with `git rev-parse a33b8d1c^{tree}`) | same |
| Parent / product | `e76a07b2bae7c945e5a9d529ed8cf9069f4c9064`, product tree `ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7`; parent is on the remote | `CARRIER_COMPOSITION.json` in the public tree |
| Host ref | `refs/heads/pro/dg16-g1-original-g3-32-20261114`: **local only, absent on the remote** | `git ls-remote`; local ref present in `C:/workspace/ai/improveimplementaudit/IMPLEMENTAUDIT` |
| Tools control ref | `pro/dg16-g1-tools-control-32-20261114` = `ec4433995f0a7b82d19d589028ece6877b8dfe98`: **on remote**, empty tree, no parent | `A/g132-root-preparation/ANCHOR_RECEIVING.json` (sha256 `7ed67047…`), `git ls-remote` |
| Carrier control ref | `pro/dg16-g1-carrier-control-32-20261114` = `e48ef76a986d1ce949661fd658cdcbe66f292788`: **on remote**, empty tree, no parent | same |
| G3 control ref | not created, not published (`host_and_G3_not_published: true`) | same |
| Finish phase | sha256 `39fd7b7abe4f4535d31b2fad4f11a5a2074278aed7ef4c3fefd7ef5948add54e` | `A/EXECUTION_STATE.json` key `g132` |
| Root final source selection | sha256 `5e5b71d8ad1ab4e34c2cee5a25a03e3241a0adca5c26296ce0291d0fc0dfae94`, purpose `FINAL_ORIGINAL_ACCEPTANCE` | `/home/agent/pr255-g132-root-20261114-01/SOURCE_SELECTION_FINAL.json` |

**What passed, and at what scope (source only; none of it is acceptance):**

- Independent whole-host review: `ACCEPT_EXACT_CURRENT05_WHOLE_HOST_SOURCE_FOR_ROOT_DECISION_ONLY`, no blocking findings. `A/g132-binding-review/FINAL.json`, 16295 bytes, sha256 `c12f71da62c578cf97b008d63a169f18b6cdd2bbd6c5fbcc300ea32cd29ce020`.
- Independent 151-file interface review: `PASS_SOURCE_INTERFACE_ONLY`. `A/g132-binding-review/interface/FINAL.json`, 9349 bytes, sha256 `aecd6498843aa516fb3e650d3635b125b50fc11d2e65c9d9124fb356b9784f3c`.
- Root offline host receiving and 151-source receiving, factory 71 / interface 151: `/home/agent/pr255-g132-root-20261114-01/ROOT_OFFLINE_HOST_RECEIVING.json`, `ROOT_151_SOURCE_RECEIVING.json`.
- Runtime-parent and journal path preflights: PASS, reported by Root (astra5.md line 33480, sol5.md line 144880). I did not re-run them.
- Retained nine-case evidence: `REUSE_ORIGINAL_NINE_AT_ORIGINAL_MIXED_PURE_VALIDATOR_SCOPE_NO_REPLAY`; no case rerun. `E/sol-g132-retained-nine-applicability-20261114-01/G132_SOURCE_CASE_APPLICABILITY.json`, 12675 bytes, sha256 `f962c5a2b8bf9ed8c4ab84bc8204b2073ceda365f822ca1b0a8d534507ddd66a`. It is a recommendation to Root, not Root acceptance.

**Unlaunched / not done:** host-ref push (which is the launch), tool adoption, recipient, late assembly, dispatcher binding, sender, carrier publication, core G1, native bank, both G3 stages, terminal receiving. Root's recorded pending item: "Actual host/ref/admission/noninterference".

**Grants and approvals:**

- Owner fresh-crypto clarification: `A/OWNER_FRESH_CRYPTO_APPROVAL.txt`, received in `A/OWNER_FRESH_DG16_CRYPTO_RECEIVING.json` (sha256 `4f4b15c5…`, 2026-11-14T14:12:30Z). It covers original G1/G2 fresh episodes, dedicated DG16 keys only, and says no repeat routine approval is needed. It still reads as valid for G132. It also requires that admission and custody be independently verified before each new episode.
- Hold: `RELEASED_BY_OWNER_COMPLETION_REQUEST_20261114`; UNKNOWN fences remain.
- The single replacement-recipient sequence was unconsumed at that receipt. I did not establish whether G131 consumed it.
- The G131 terminal review grants nothing: `effect_grant: false`, and "This review grants no fresh attempt" (`A/g131-terminal-review/FINAL.json`, sha256 `bd326945…`). A fresh attempt needs Root's own eligibility decision.
- No per-episode admission exists for G132. Those are issued live by Root and cannot be pre-issued.

**Recipient and sender requirements:**

- The recipient is created by the hosted job in its own private session (workflow step 6) and exported as an artifact (step 7). Its private key never leaves the runner.
- Root issues `PRO_SENDER_OPERATION.json` with `expires = min(request expiry, issued + acquisition_seconds*1000)` (`T/root-recipient-issuer-01/issue_recipient_inputs.py:83`). G132 limits: `acquisition_seconds` 600, `command_seconds` 60, `poll_seconds` 5, tool `adoption_seconds` 600.
- One sender only, fresh nonce, fresh journal, sender uid/gid bound. Nothing from G131 may be reused: its cipher, recipient, sender session, journal and WRITE0 are `UNKNOWN_NO_REPLAY`.

**Timing (the G131 failure), from `A/g131-terminal-review/FINAL.json` `timeline`:**

| Event | Remaining |
|---|---|
| recipient issued | 534.5 s |
| recipient received by Root | 444.2 s |
| sender CONTROL issued | 117.4 s |
| binary admission issued | 40.1 s |
| binary callback started | 7.8 s |
| WRITE0 frame started | 3.0 s |
| expiry; host refused `INPUT_RECEIVING_REFUSED` | 0 |

Root spent 327 s between receiving the recipient and finishing the sender; an argparse refusal on `late-assemble` (missing passthrough separator, `A/g131-publication/LATE_ASSEMBLY.stderr`) was part of that. The sender itself ran 64.2 s. Sender completion to first WRITE0 took a further 114 s. The five-write, six-readback publication never ran, so its duration is unmeasured.

**Noninterference:** run `43098152901` on `pro/dg16-g1-original-g3-19-20261111` is still `queued` after 75 h. Its concurrency group is per-ref, so it does not block ref 32, but it is a queued G1 workflow that could start at any time. G220 (G2) is terminal failure, so no live window competes.

## 2. Ordered remaining sequence

G1 is not GitHub-only. It is a GitHub-hosted job that waits on Root actions performed from the local WSL host, each of which reads or publishes through Codex's GitHub connector tools: `mcp__codex_apps__github_fetch` for sender reads (`T/dispatcher-templates-02/dispatcher_entry.py:16`), and `github_create_blob` x2, `create_tree`, `create_commit`, `update_ref` for publication (`T/root-final-operators-01/binary_publish_v3.py:16`). Those tools exist only inside a Codex turn. **Steps 4, 6, 8, 10, 11, 13 and 14 therefore need Codex model turns, as one contiguous Root turn chain.** A Pro GitHub-only executor or Claude cannot perform them.

Before the window:

1. [ROOT-SUCCESSOR] Decide fresh-attempt eligibility for G132 and record it (the G131 review grants none). Confirm whether the replacement-recipient allowance is still unconsumed.
2. [OWNER] Cancel or explicitly accept stale queued run `43098152901`. Confirm a quiet window on host 3701MEDIA. Set the hold-before-spend floor (section 3).
3. [NATIVE-CODEX] Root dry-stages every CLI layout, including the `late-assemble` passthrough separator, callback/tool bindings, empty owned parents and fresh output leaves, per `E/sol-g131-next-eligible-operator-recipe-20261114-01/OPERATOR_RECIPE.md` (sha256 `a16dcf47…`). Re-verify `T/OPERATOR_PINS.json` (sha256 `d850a9ca…`, 98 entries).

The live window (75-minute job; the 600 s recipient window opens at step 7):

4. [NATIVE-CODEX] Push `a33b8d1c` to `refs/heads/pro/dg16-g1-original-g3-32-20261114`, non-force, through the guarded transport. This is the launch.
5. [MECHANICAL-Pro] Hosted steps 1 to 4 run: checkout, fixed root island, host tool observation, artifact upload. No human or model input.
6. [NATIVE-CODEX] Root receives the tool observation, issues the tools role and DECISION, and publishes to `tools-control-32` (three guarded control writes plus readback). Hosted step 5 adopts it.
7. [MECHANICAL-Pro] Hosted steps 6 and 7 create the recipient request and upload it. **The recipient clock starts here.**
8. [NATIVE-CODEX] Root receives the recipient artifact and runs `issue-recipient-inputs`, then `late-assemble`, then dispatcher selection, bind and admission.
9. [MECHANICAL-Claude-local] **Hold-before-spend gate** (section 3): run `pre_sender_budget_gate.py` against the fresh `PRO_SENDER_OPERATION.json`. Exit 3 means stop and do not start the sender. It reads public metadata only and needs no model turn; Root can equally run it itself.
10. [NATIVE-CODEX] The once-only sender: 18 `github_fetch` reads through the dispatcher, and local CMS encryption with `/usr/bin/openssl` under WSL user `agent`. This is the local sender encryption. It is covered by the owner clarification and is Root's to run.
11. [NATIVE-CODEX] Immediately: `receive-sender-terminal`, `publication-inputs` with `--deadline-unix-ms`, `issue-admission`, `publication-config`, `binary-selection`, then `runBinaryWithSelection` exactly once (five writes, six readbacks to `carrier-control-32`).
12. [MECHANICAL-Pro] Hosted step 8 authenticates and receives the private inputs; steps 9 to 22 run core G1 and the native bank.
13. [NATIVE-CODEX] G3 stage one: hosted step 23 `g3-receive` and steps 24/25 export the root request; Root publishes its initial decision (create-only callback); hosted step 26 `g3-consume`.
14. [NATIVE-CODEX] G3 stage two: hosted steps 27/28 export the final request; Root publishes the final decision; hosted step 29 `g3-decide`.
15. [MECHANICAL-Pro] Hosted steps 30 to 34: finalize, validated terminal export, retention.
16. [ROOT-SUCCESSOR] Independent terminal receiving and review of the actual run, then Root acceptance. Any refusal, expiry or pending intent ends the attempt with state preserved and no retry.

## 3. Demonstrated source defect on G132's path

**Defect: the sender is spent with no check that the remaining window can cover the rest of the chain.** Every time gate I found on the path is a bare "not yet expired" test:

- `carrier.py:440-444` `root_payload`: bounds `deadline`, then goes straight to `reserve(... 'SEND_RESERVED.json' ...)`.
- `T/dispatcher-templates-02/dispatcher_entry.py:124`: `int(time.time()*1000) < op['expires_unix_ms']`.
- `T/late-assembler-01/assemble_actual.py:123`, `T/root-final-operators-01/root_pipeline_inputs_v2.py:100,220,246`, `binary_publish_v3.py:115,221`: same form.

So a sender started with a few seconds left is admitted, burns the once-only recipient and nonce, and can only fail. This is the class that killed G131. The G131 terminal review recorded `new_source_defect_established: false` and prescribed the remedy as operator practice ("hold before spending a sender"). I am reporting it as an unenforced guard: the recipe depends on Root computing the remainder by hand inside the window.

Failing control: `scratch/control_sender_budget.py`, sha256 `3bef607a61c06191676253e1c9d5053af2848163190afa8b3a4a8d496a1acd28`. It executes the actual source lines of the `root_payload` span against stubs, with no crypto and no I/O.

```
python -I scratch/control_sender_budget.py scratch/orig/carrier.py     -> RESULT FAIL, exit 1
FAIL g131_7839ms        SENDER_SPENT
FAIL short_120s         SENDER_SPENT
FAIL floor_minus_2s     SENDER_SPENT
ok   adverse_ample_400s SENDER_SPENT

python -I scratch/control_sender_budget.py scratch/fixed/carrier.py    -> RESULT PASS, exit 0
ok   g131_7839ms        REFUSED_BEFORE_SPEND:PRO_SENDER_REMAINING_BUDGET_INSUFFICIENT
ok   short_120s         REFUSED_BEFORE_SPEND:PRO_SENDER_REMAINING_BUDGET_INSUFFICIENT
ok   floor_minus_2s     REFUSED_BEFORE_SPEND:PRO_SENDER_REMAINING_BUDGET_INSUFFICIENT
ok   adverse_ample_400s SENDER_SPENT      (adverse control: the fix does not over-refuse)
ok   adverse_expired    REFUSED_BEFORE_SPEND:PRO_SENDER_REMAINING_BUDGET_INSUFFICIENT
```

The `adverse_expired` row also prints FAIL on the original. That row is a stub artefact, not a finding: the stubs replace `SP.load` and `B.Store`, which may enforce expiry in the real source. I did not check that either way.

Fix (two insertions, nothing else changed):

```
+MIN_SENDER_CHAIN_SECONDS=300          # module level, before root_payload
+        P.need(deadline-time.monotonic()>=MIN_SENDER_CHAIN_SECONDS,'PRO_SENDER_REMAINING_BUDGET_INSUFFICIENT')   # after line 444
```

- before: `carrier.py` sha256 `bfb5c0329f5c34cbb832151e59f2ad0995f6828843ada0abb08fed94f8671304` (identical to the copy in the G132 host tree)
- after: `scratch/fixed/carrier.py` sha256 `e5ec1aeb9764e0f97c7e2c5585b52e332f309cd10bfe898cee5ad78ec1b16f15`

**Do not apply the in-source fix to G132.** `carrier.py` is inside host tree `e7b77a2e`. Changing it changes the tree, the commit, `CARRIER_COMPOSITION`, both independent reviews and the Root selection, and the already-published control anchors are bound to this composition. It is a candidate for a later source revision.

**For G132 use the standalone gate instead:** `scratch/pre_sender_budget_gate.py`, sha256 `40c35d5a594daa0468413bce26b50562e55160e21fae72981efad83f56e35f98`. It reads only `PRO_SENDER_OPERATION.json`, changes no pinned file, and exits 3 with `HOLD` when the remainder is under the floor. Its six boundary cases pass in the same control run: 7.8 s HOLD, exactly floor PROCEED, floor minus 1 ms HOLD, expired HOLD, not yet issued HOLD, malformed HOLD.

The 300 s floor is my proposal, not a measured requirement. Measured from G131: at least 178.6 s from sender start to first WRITE0, with the five-write publication of a 926 KB ciphertext still entirely ahead. Root or the owner should set the value. Sol's recipe explicitly declined to invent a fixed minimum, so the gate needs either that position changed or the number supplied.

With a 600 s window and a 300 s floor, Root has 300 s from recipient issuance to sender start. In G131 that stretch took about 353 s, so pre-staging (step 3) is what makes the floor reachable.

## 4. Local-only inputs a GitHub-only executor cannot reach

Full list with path, bytes and sha256: `INPUTS_MANIFEST.json` in this directory (sha256 `3306bf7a806912500b9aba9232d6a39a70d25a985182678b6118205a370c3463`).

- **Host public overlay, 49 files**, commit `a33b8d1c`, tree `e7b77a2e`. Local copy at `A/g132-root-preparation/public-tree`. Not secret. It becomes public when the host ref is pushed, and that push is the launch, so it must not be published early.
- **Root operator tools, 98 pinned files** under `T/`, per `OPERATOR_PINS.json` (sha256 `d850a9ca36d4ef0c4b5aa6dddedb9eaa84aa010ef07a333cdad7f969bdadb6af`). Not secret, local to WSL.
- **Excluded as private; not listed, not opened:** `T/retained-final5f-private-inputs/` (8 files plus `placement/`). This is the plaintext bundle the sender encrypts.

**Publishing does not help and I recommend against it.** A GitHub-only executor cannot run the sender in any case: it needs the private bundle, the WSL sender uid, and the Codex connector tools. The only publication G132 needs is the host-ref push in step 4.

## 5. G3

Inside G132, G3 is the two-stage same-job receiving in `qualification/dg16-r5-g1-hosted-episode/g3_receiving.py` (hosted steps 23 to 29). Its source is in the reviewed tree and passed both reviews, so it is source-ready at that scope. The Root-side create-only callback v7 has green fixture controls (`E/g3-create-only-callback-20261113-01/GREEN.json`), but its report says Root's independent review and selection were still pending. I did not find a later record closing that.

That in-job G3 does **not** deliver the G1+G2 join. The source fixes `full_g2 = 'NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST'` and marks `FULL_G2_RECEIVING` and `DG16_ORIGINAL_RECEIVING` as `permitted=False` (`g3_receiving.py:961-975, 1263, 1297`). The join `DG16_ORIGINAL_RECEIVING` requires an actual parallel full-G2 receiving at the applicable source.

What G3 needs once G1 and G2 have real accepted results:

1. An accepted G132 terminal with independent receiving (section 2, step 16).
2. An accepted full-G2 episode. G220 (run `43640583300`) is terminal failure, so a G221 or later is required first.
3. A separate Root final decision that consumes exactly those two returns. Whole-DG16, natural-L04 and sibling awards stay non-automatic.

I found no prepared source or operator recipe for that join step. Treat the join as **not ready**, and the in-job G3 as ready at source scope only.

## Not verified

- Runtime-parent and journal preflights (taken from Root's report).
- Whether the replacement-recipient allowance is still unconsumed.
- Real behaviour of `SP.load` / `B.Store` on an already-expired operation.
- Publication duration for five writes and six readbacks (never exercised).
- Whether the G3 create-only callback v7 was selected by Root.
- Transcript content after the last G132 mentions (astra5.md line 38276, sol5.md line 145358); both say G132 remains unlaunched.
