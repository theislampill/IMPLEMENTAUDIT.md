# Local Windows results for PRO-EXECUTOR-01 (Claude Fable 5.2 on 3701Media, 2026-11-15)

Role: targeted local support for the principal executor. Authority used: none
beyond read-only host reads, the existing inert builder, the existing custody
test, and this publication. No native appserver, model turn, grant, `--execute`,
protected ref push, key operation, merge or acceptance claim occurred.

## 1. DG17: final operation record built at the actual Windows location

Resolves "rebuild the operation record at its final location" (commission C,
DG17 outstanding item 1) and `DG17_ACTUAL_WINDOWS_DEPENDENCY.md`.

| Fact | Value |
|---|---|
| Host | 3701Media, Windows 10.0.26200, Python 3.11.9 at the operation's pinned `python.exe` |
| Source | fresh clone, branch `engineering/pro-executor-dg17-source-20261115`, HEAD `a297957be11feb494c0ec467235794a1e0c54751`, tree `b08dc4ecf4028beeedb579a312eccae23cb5d863`, `core.autocrlf=false`, clean |
| Source directory | `C:\workspace\ai\improveimplementaudit\plans\pro-executor-dg17-final-20261115\source` |
| Final author directory | `C:\workspace\ai\improveimplementaudit\plans\pro-executor-dg17-final-20261115\author` |
| Command | `python -B <source>\handoff\dg16-dg18-findings-20261115\dg17-release-with-store-check\tools\build_release_acl.py --source-root <source> --output-author <author> --package <final>\package\IMPLEMENTAUDIT.plugin.zip` (run once, exit 0) |
| `OPERATION_A.json` | 18,597 bytes, SHA-256 `ec5051ddea4b79bcd2e9980b90e47351fcf62536f00e2649fde43a7fce7a7c9c` |
| `PINS.json` | SHA-256 `f3b6a484fa1d9ef6705d1e38c742f8b5f9e5132e37d0c0d4a2a088f6bace210a` |
| Status in record | `INERT_SOURCE_REBUILD_NO_NATIVE_ADMISSION`, limits unchanged, issuer `01a1cf82-…` retained, 14 custody differences UNKNOWN |

Bodies: `dg17-final-operation/author/` (all ten members), `PINS.json`, `rebuild.log`.

**Package.** The historical pinned package (588,548 B, `9e0af350…`) predates the
Windows store-custody admission in `host-session-binding.py`, so it would refuse
at Stage B. I built the canonical package from the selected source with the
existing `scripts/package-contract.py --build` and passed it via `--package`;
the builder's delegated `--verify-artifact canonical_plugin --require-clean-source`
check passed. Result: 588,580 B, SHA-256
`706afde44df992282a43d59e3affa412f0e9ca2dc09f0de1dfc212223751f1e2`
(`dg17-final-operation/package/`). The record pins this package at its final path.

**Nine host inputs.** All nine exist on this host with exactly the historical
bytes and SHA-256 listed in Pro's dependency record (the package is superseded
as above). The Windows Job helper `windows_job_measure.py` is present with
`6dc21e69…`.

**The builder reports 4 `unverified_inputs`; this is a guard artefact, not a
mismatch.** `build_release_acl.py::pin` compares `st_mode` between `lstat(path)`
and `fstat(fd)`. On Windows, CPython derives execute bits from the `.exe`
extension for the path form only (`0o100777` vs `0o100666`), so every `.exe`
is refused (`codex…exe`, `python.exe`, `bash.exe`); `git.exe` is refused by the
`st_nlink == 1` rule (Git for Windows hard-links it). The record therefore
truthfully says "not observed by the builder". I did not change the builder.

**Readback through the actual consuming code.** `FINAL_HOST_READBACK.json`
(script `readback_with_parent_capture.py`) extracts the generated
`parent_launch_a.py` / `parent_launch_b.py` `capture()` functions and runs them,
read-only, over the operation, the full readset with its exact pins and sizes,
both drivers, the RPC module and the Job helper: **34 of 34 PASS**. It also
observed: interpreter equals the operation's `python`; `case-native-02` absent;
`isolated-home-01` present; `EPISODE_WINDOW_02.json`, `parent-A-02`,
`PARENT_STAGE_A_JOB_RESULT_02.json`, `OPERATION_B_BOUND.json`, `parent-B-01`,
`PARENT_STAGE_B_JOB_RESULT.json` all absent (fresh).

**Store custody controls on this host** against the generated `stage_b.py`:

| Run | Result | Meaning |
|---|---|---|
| Unmodified `test_store_custody.py` (`store-custody.log`) | 3 of 14 as expected, 11 fixture ERROR | Both product positives (driver-created store, re-check) PASS. The 11 errors are all the fixture's `icacls /setowner <self>`: "Access is denied" in a non-elevated session. The hosted runner is elevated; this session is not. The product guard was not reached in those cases |
| Local variant (`local-fixture-variant/`), one change: skip `/setowner` when the independent owner readback already equals the current user | 13 of 14 as expected | 3 positives PASS, 10 refusals reach their intended reason. The wrong-owner case still needs elevation, as the commission already records |

The variant is local evidence only, not a source change and not a replacement
for the received hosted 14/14.

**Owner carrier body.** `OWNER_AUTHORIZATION.carrier.json` is the exact 1,634-byte
`05a0767e…` carrier Pro could not read. Its scope is "One fresh DG17 Windows
Stop/T12/original14 episode", with `operational_window_not_yet_issued: true`
and `native_episode_started: false` at the time of writing. A Stage A episode
was subsequently started and spent on 2026-11-14 (`EPISODE_WINDOW.json`,
`parent-A-01` on this host). Whether the carrier still covers a second episode
is the owner's statement to make, not an inference from this file.

**What DG17 now needs, and nothing else:**
1. The owner's fresh written grant naming `OPERATION_A.json` `ec5051dd…`.
2. An issuer the parent will accept. `parent_launch_a.py` requires
   `grant['issuer'] == op['issuer']` (the historical Root thread `01a1cf82-…`).
   The commission makes Pro Root successor for DG16 only. Either the owner
   names the DG17 grant issuer, or the issuer is rebound as a reviewed source
   change (which changes the operation hash and requires one rebuild).
3. Two authentic Codex turns on this host (quota from 2026-11-20, or credits).

## 2. DG16 G132: owner-local public inputs

Pro's last GitHub read returned 404 for the G132 host commit and listed the
49 overlay and 98 operator files as owner-local. They are here, as data only.

- `dg16-g132-owner-local/g132-host-commit-a33b8d1c.bundle` (529,360 B, SHA-256
  `1f79fa0c68da349e34e1d7d38ffb72cbabb82be33fd66dbb58779cb8808f3bda`): git bundle
  of `e76a07b2..a33b8d1cdb967124b1b0d4fe877cf9b283304798` (tree `e7b77a2e…`,
  49 files over the published parent). `git bundle unbundle` reproduces the
  exact commit. **The host ref `pro/dg16-g1-original-g3-32-20261114` was not
  pushed and is still absent on the remote; pushing it is the launch.**
- `dg16-g132-owner-local/public-operator/`: the 98 members of `OPERATOR_PINS.json`
  (SHA-256 `d850a9ca…`), each verified against its pin on export and again after
  copy. The `retained-final5f-private-inputs` directory was not read or copied.
- `ROOT_151_SOURCE_RECEIVING.json`, `ROOT_OFFLINE_HOST_RECEIVING.json`,
  `SOURCE_SELECTION_FINAL.json`, `root-preparation/` and `binding-review/`:
  the Root and independent source records that STATE.md cites by local path.

## 3. DG18 N1: not on this machine

Unchanged from `DG18_N1_AND_OBLIGATIONS.md`: this host holds only constructed
test stores. The custodian's `pending.json`, owner attribution and fixed
selection lived in a container that no longer exists. No owner is inferred.
This needs one owner decision (see the session report), not more searching.
