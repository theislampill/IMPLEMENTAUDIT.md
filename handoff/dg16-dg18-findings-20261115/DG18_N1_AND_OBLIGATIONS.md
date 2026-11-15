# DG18 (R0039) read-only analysis (Fable 5.2, recorded and spot-checked by Opus 5.5), 2026-11-15

## N1: the second compaction boundary at cutoff 109411
**What the records say:**
- **Boundary:** a real, completed second compaction, boundary `162f88f4…`, scope `45de02cb…`.
- **Status:** RESERVED by `compaction-audit-pending.py/separate-later-cutoff-child`. The result and consumption are PENDING (witness null), and currentness is UNRESOLVED (epoch null).
- **Source:** DG18_CONTINUATION_PROGRESS_20261106.json at `/successor_session/H0_original_cold_receiving_body/five_fields/obligations/second_occurrence`. The later progress file still shows `MANDATORY_RESERVED_PENDING_UNCOVERED`.
- **Owner:** named only as a role, "existing continuity/R0033 owner". The recorded controller `r5-h0-native-facts-20261105-02` is an archival transport subject that explicitly did not inherit the original authority. No session id, owner id, store path or assignment record is given.

**The record that would establish the current owner** is defined in `compaction-audit-pending.py` (`read_selected_accepted_episode_v1`, lines 792–886). It consists of:
1. the fixed accepting-source selection, with `pending_owner {store, session_id, owner_id}` and `episode_owner {module_pin, repository, controller}`;
2. the owner attribution;
3. `<store>/compaction-audits-v1/<session key>/pending.json`, carrying the assignment.

**Does it exist?** Not in any material available here:
- At b0fcb565 all selection pins are `None`, and the reader returns `FIXED_SELECTION_UNBOUND`.
- None of the 1,786 local `pending.json` stores contains N1's identifiers.
- The originals sit at the custodian's container paths (`/workspace/scratch/4bb1fcb57e58/successor/...`), which are not on this machine.
- No owner is inferred.

## Which obligations need a native Codex model run
| Obligation | Needs |
|---|---|
| N1 | The owner's records first, then the bounded audit-state execution: **a Codex model run** |
| E/F | Timed availability and native GO: **a Codex model run** |
| W-FULL | A native Windows host measurement (zero-model rotation; 60 s, 201,326,592 B memory). By the contract text it needs no model turn, but it needs two concurrent DG16/DG17 owner originals for one window |
| OR | An authentic current-host observation plus an issuer grant. A model answer does not count |
| C02 | **No model run.** It needs the adjudication owner's issuer grant, the erroneous-event evidence, the expected-old tuple, a complete later-boundary census, an authorised publication and host readback |
| Cold receiving | An independent receiver can work offline, but the full canary cannot finish before N1 |

**Can be done now:** none of these earns acceptance on its own.
- Ask the original custodian for N1's three owner records.
- Purely source-qualify the OR consumer (`rotate-canonical-state.py`) and the C02 consumer (`claim-run-rotation.py::propose_c02_correction_v1`). Open point: the `skills/` and `source-peers/native-runtime` copies differ, so state first which copy is the entitled version.
- Assemble the input packets for C02, OR and the W-FULL window.

## Demonstrated defect (Opus confirmed by reading the source; not fixed)
`fixtures/canonical-state-rotation/pending_state_loader_test.py:87–89` derives a file mode from `st_mode & 0o111`. Windows never sets those bits, so it always derives `100644`. The test then requires this to equal the manifest mode, but `host-session-binding.py` is declared `100755` in both the git tree and the manifest. So this control bank **always fails on Windows** with "owner source does not match its native manifest", even though the bytes and sha256 match. The test clearly intends to run on Windows: it has `os.name != "posix"` skip branches. The proposed fix is to read the declared mode only on POSIX and compare bytes and sha only on Windows; this needs review. It affects Windows evidence for criterion 4 and W-FULL preparation.
