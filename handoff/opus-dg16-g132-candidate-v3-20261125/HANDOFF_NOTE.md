# G132 prospective candidate v3: whole-sender restriction

Prospective source candidate only. It is not a launch commit and it awards nothing. The issued records stay
withheld and unedited; no grant, provider dispatch, protected run or GitHub workflow was used.

- Baseline: `b393a905`. Predecessor: v2 `6d3250d5` (tree `e1dfe280`).
- Source tree without this handoff directory: `40801f9d400fe0d32c5f3d6110d57e3e567fe433`.
- Regenerate: from a clean worktree at b393a905, run `python -I make_g132_candidate_v3.py` with
  `provision-inner.sh`, `v3_sender_launch.py` and `v3_sender_sandbox.py` beside it. It applies the v2 edits
  unchanged, then the v3 edits, then the same full-history fixed-point pin rebind (9 rounds).
- Addresses Root R-M2 (GAP-REVISE) and R-M4 (optional `root_tools` retirement) of b4d9fc2. R-M1 and R-M3 are as
  accepted for v2; nothing about them changed.

## 1. What the sender is and touches (traced in the v2 code)

| Item | Finding |
|---|---|
| Entry | `carrier.root_payload(run_id, workflow_commit, artifact_id, archive, token=None)`. No caller existed in the repository; v3 adds the fixed entry `carrier/sender_launch.py`. |
| Credentials | None. `token` must be `None` (`PRO_SENDER_SUPPORTED_TOOL_ONLY_NO_HTTP_CREDENTIAL`). No GitHub token reaches the sender. |
| GitHub communication | No network I/O in the sender. `ROOT_SUPPORTED_GITHUB_FETCH_FILE_BROKER_V1` (`tool_broker`) writes 18 fixed GET requests as files into the session directory and polls for replies. The external root dispatcher (supported tool `mcp__codex_apps__github_fetch`) writes `DISPATCH_INTENT`, `TOOL_RESULT`, `REPLY` and `REPLY_READY` through `tool_broker.Store`. `provider_reader.GitHubReads` (HTTPS) is used only by the host role. |
| Reads | The packet's carrier modules and pinned bodies; `CARRIER_COMPOSITION`/`CARRIER_ADMISSION`/`INPUT_INDEX`; `PRO_SENDER_*` records; `/usr/bin/openssl` and `/usr/bin/bwrap`; the maintained `QUALIFIER.py`/`COMPILER.py`; the private inputs `<packet>/private-inputs` (first private read: `F.acquire`, after the broker's opening reads); the request artifact (bytes passed in). |
| Writes | Only `<packet>/../dg16-private-sender-<run>-a1/` (0700): reservation, broker files, `bundle.plain` and `recipient.pem` (both unlinked at cleanup), retained `INPUTS.cms`, metadata, `OUTCOME.json`. |
| Children | One `openssl cms -encrypt`, under the v2 nested sandbox (`SANDBOX_PREFIX`, fd-bound `fexecve` of the pinned bwrap). |

## 2. Design

The whole sender runs, from before its first read of any input through cleanup, inside the pinned sender bwrap
(`e3189038`, 72,160 bytes, Root R-M1), as the original UID and GID.

1. **Outer** (`sender_launch.py RUN COMMIT ARTIFACT ARCHIVE` → `sender_capture.launch`), as the original
   nonroot sender, before any private read. It:
   - checks the entry's own pin (`sender_capture.ENTRY`, 2,086 bytes, `1845fbfa…`), the composition pin, and
     the arguments;
   - requires the placement root (the packet's parent) to be a 0700, sender-owned, xattr-free directory
     holding exactly the packet;
   - pins `openssl` and `bwrap` from `sender_tools`, with the v2 host-view custody (now
     `sender_capture.host_tool_custody`): root-owned, unprivileged, and a root-owned non-writable `/`, `/usr`,
     `/usr/bin`;
   - computes `group_masks`: the `/usr` directories that a retained supplementary group could read beyond
     "other". On this host that is `/usr/share/ollama`. A matching regular file refuses the launch;
   - opens the request artifact read-only as the child's stdin, opens bwrap once and verifies it
     (`launcher_fd`, as in v2), and builds the attestation (UID, GID, overflow IDs, the outer namespace
     inodes, the `/usr` submounts, the masks, the placement, the entry pin and the host-view tool rows);
   - forks. The child keeps only fds 0–2, sets `PR_SET_NO_NEW_PRIVS` and reads it back, then
     `execve(fd)`s the verified bwrap with the fixed `whole_sender_argv`. The parent waits, then refuses unless
     the placement holds only the packet and the one session directory.
2. **Sandbox** (`whole_sender_argv`):
   - `--unshare-all` (user, mount, pid, net, ipc, uts, cgroup) with `--die-with-parent`, `--new-session`,
     `--clearenv` and `--cap-drop ALL`;
   - `/usr` read-only, with each mask an empty read-only tmpfs, plus the `/lib`, `/lib64` and `/bin` symlinks;
   - a fresh `/proc`, a minimal `/dev` and a private `/tmp`;
   - the placement root bound read-write, the packet read-only over it, and `/` remounted read-only;
   - only `PATH` and `LC_ALL` set; the command is `/usr/bin/python3.12 -I -S -B <entry> --inside <attestation> …`.

   There is no `/home` content, no `/etc`, `/var`, `/run` or `/mnt`, no docker socket and no network.
3. **Inner self-check** (`enter_sender_sandbox`). This is the first act after loading the modules, before the
   request artifact or any input is read. It refuses with a closed code unless all of these hold:

   | Check | Required state |
   |---|---|
   | Privileges | `NoNewPrivs` 1; `CapInh`/`CapPrm`/`CapEff`/`CapBnd`/`CapAmb` all 0 |
   | Identity | real = effective = attested UID/GID |
   | User namespace | single-ID `uid_map` and `gid_map`; `setgroups` deny |
   | Namespaces | all six differ from the outer's |
   | Network | interfaces exactly `lo` |
   | Mounts | exactly the expected mount set with the expected ro/rw state, all `nosuid` |
   | Root | the root is a read-only tmpfs; top level exactly `bin dev lib lib64 proc tmp usr` plus the placement skeleton, with each skeleton directory holding only the next component |
   | Masks | empty |
   | Absent paths | `/etc`, `/var`, `/run`, `/root` and both docker socket paths |
   | Environment | exactly `PATH`, `LC_ALL`, `PWD` |
   | Descriptors | exactly 0, 1, 2 |
   | Entry | the entry file matches its pin |
   | Tool view | each attested tool and its chain are the same file (dev, ino, mode, nlink, size, mtime, ctime) with the unmapped owner |

4. **Gating.** `require_sender_sandbox()` rechecks the live state: NNP, capabilities, identity, namespaces and
   the mount set. It runs at:
   - the start of `root_payload`;
   - `Commands(root)` construction and every `current_tools()` (every capture currentness point);
   - every `CaptureSession._current()`;
   - `read_request_archive()`.

   Outside the verified sandbox, each of these refuses with `SENDER_WHOLE_SANDBOX_REQUIRED`.
   `carrier.sender_tool_custody` now delegates to `sender_capture.attested_tool_custody`.
5. **Encryption child.** It is kept, not subsumed. `SANDBOX_PREFIX`, `validate_command`, `launcher_fd`,
   `close_plan` and the decrypt template are byte-identical to v2. The nested child still cannot see the
   packet, the private inputs or the session directory (it gets only the three held fds), and its reviewed
   argv is unchanged.
6. **Unchanged.** The original-UID test and the held-input requirements: `sender_policy.py` is byte-identical
   to the baseline.
7. **R-M4.** `root_tools` is removed from `CARRIER_COMPOSITION` and from `carrier_policy.load()`'s exact keys
   and validation loop. `sender_tools` and the host `HT.ResolvedTools` checks are unchanged. Historical
   records (v2 handoff, reviews) are untouched.

## 3. Qualification (WSL Ubuntu 24.04, user `agent` uid 1000; disposable inputs only)

Run `qual/qualify.sh <tree> <out>`; the outputs are in `qualification-out/`. The private inputs are three
random disposable files. The recipient is a throwaway RSA-3072 key, kept outside the placement. The GitHub
tool results are synthetic and are written by `qual/qual_dispatcher.py`, a separate process outside the
sandbox, through the unchanged `tool_broker.Store` API. No network is used for them and no token exists.

### Seams stubbed in the end-to-end run

These are the only ones (`qual/qual_inner.py`):

| Seam | Stand-in | Why |
|---|---|---|
| S1 | The entry is `qual/qual_inner.py` instead of `carrier/sender_launch.py`, through the same `sender_capture._launch` and argv shape; the sandbox self-check is still the first act | To add the stand-ins and probes below |
| S2 | `carrier_policy.load` → the actual composition and core bodies with the disposable input index | Needs the issued, stale `CARRIER_ADMISSION` and the real `INPUT_INDEX` |
| S3 | `carrier.current_binding` → a counted no-op | It re-runs S2 |
| S4 | `sender_policy.load`/`current` → a disposable operation; `current` keeps the original-UID/GID and time checks | The `PRO_SENDER` records are `UNRESOLVED` |
| S5 | `carrier_policy.check_inputs` → an exact disposable index/body join | `RETAINED`/`ROLES` name the real inputs |

Everything else is the candidate's code, including the 18 broker reads, `F.acquire`/`recheck`, `Commands`,
`CaptureSession`, cleanup, `broker.finish` and `save_outcome`.

### Results

Each proof item is shown with the file that records it.

1. **Restriction in force before the first private read** (`12_e2e_inner.json`).
   - The self-check passed. These probes were taken:
     - P0, after sandbox entry and before any input was read;
     - P1, inside `F.acquire` at the first private read;
     - P2, after `root_payload` cleanup.
   - All three show the same state:
     - `NoNewPrivs` 1, `CapEff`/`CapBnd`/`CapPrm`/`CapInh`/`CapAmb` all 0, Uid/Gid 1000;
     - Groups `65534 ×8 + 1000` (supplementary groups retained but unmapped);
     - `uid_map` `1000 0 1`, `setgroups` deny, and `require_sender_sandbox` IN_FORCE.
   - The full mountinfo is recorded at each probe. The outer before launch had `NoNewPrivs` 0, `CapBnd`
     `000001ffffffffff` and Groups `4 24 27 30 46 100 989 1000 1001` (`12_e2e_outer.stderr`).
2. **Unreachable throughout** (P0, P1 and P2 in `12_e2e_inner.json`, against `40_contrast.json` outside).

   | Target | Inside the sandbox | Outside (`40_contrast.json`) |
   |---|---|---|
   | `sudo -n true` | rc 1, "The no new privileges flag is set …" | not executed |
   | `/run/docker.sock`, `/var/run/docker.sock` | ENOENT | CONNECTED |
   | `/home` | only the `agent` skeleton | listable |
   | `/home/agent/.bashrc`, `/etc/passwd`, `/etc/shadow`, `/etc/sudoers`, `/root`, `/var/log`, `/mnt/c`, `/run/WSL`, `/init` | ENOENT | `/etc/passwd`, `/var/log`, `/mnt/c`, `/run/WSL` readable |
   | `/usr/share/ollama` (group `ollama`, `drwxr-x---`) | an empty masked tmpfs | listable through the group |

   `42_usr_group_owned.txt` counts the group-owned `/usr` entries; the names are withheld.
3. **Network** (`12_e2e_inner.json`, against `40_contrast.json` and `41_github_head_outside.txt`).

   | Probe | Inside the sandbox | Outside |
   |---|---|---|
   | Interfaces | `lo` only | eth0–4, docker0 and others |
   | TCP to `140.82.x.x:443` (github.com) | ENETUNREACH | CONNECTED |
   | DNS for github.com | fails | resolves |
   | The dispatcher's host abstract unix socket | ECONNREFUSED (separate netns) | CONNECTED |
   | Harmless public HEAD `https://github.com/`, no token | — | `HTTP/2 200` |

   The sender needs no network, so none is given. The GitHub endpoints are enforced by the broker's fixed
   GET URLs (`tool_broker.endpoint`), which the external dispatcher executes.
4. **Encryption and cleanup** (`13_verify.json`, `11_dispatcher.json`).
   - `root_payload` returned `PAYLOAD_READY`/`ACQUIRED` with `cleanup_complete` true. The dispatcher served
     all 18 broker reads, all `RECEIVED`.
   - The retained `INPUTS.cms` (267,669 bytes) decrypts with the disposable key to exactly
     `codec.pack(index, bodies, request_sha256)` (267,046 bytes). `CONTROL.json` joins the ciphertext and
     the request.
   - The encrypt argv is `SANDBOX_PREFIX` with tool descriptors `e3189038…`/`b4f547c0…`.
   - Capture restoration is all true: `descriptors_restored`, `echild`, `handlers_restored`,
     `mask_restored`, `owned_descriptors_closed`, `subreaper_restored`.
   - `bundle.plain`, `recipient.pem`, `recipient.key` and `quarantine.plain` are absent. The placement holds
     exactly the packet and the session directory. `BROKER_END` is complete with 127 entries.
   - The v2 rehearsal through `carrier.Commands`, repeated inside the sandbox, passed: rc 0, 300,616-byte
     cipher decrypting to the plaintext, `closed()` true. Its refusals, also inside the sandbox:
     - wrong bwrap pin → `CARRIER_ACTUAL_TOOL_PIN`;
     - retired `root_tools` pins → `CARRIER_ACTUAL_TOOL_PIN`;
     - launcher identity changed → `SENDER_SANDBOX_LAUNCHER_BINDING`;
     - v1 env argv → `SENDER_FIXED_ENCRYPT_COMMAND`;
     - tool outside the attested chain → `CARRIER_ACTUAL_TOOL_PIN`.
   - The sandbox's `/tmp` vanished with it, and the WSL scratch was removed (`99_cleanup.txt`).
5. **Negative controls** (`30_negpin.json`, `31_unsandboxed.json`, `32_variants.json`).
   - **Not sandboxed.** The CLI `--inside` run with no sandbox exits 1 with `SENDER_SANDBOX_NO_NEW_PRIVS`.
     - In-process, the self-check fails 10 of its checks, in order: NO_NEW_PRIVS, CAPABILITIES,
       USER_NAMESPACE, NAMESPACES, NETWORK, FILESYSTEM_VIEW, UNREACHABLE, ENVIRONMENT, DESCRIPTORS,
       TOOL_VIEW.
     - `root_payload` refuses before any private read (no `F.acquire` call), and `Commands(root)` and
       `sender_tool_custody` refuse with `SENDER_WHOLE_SANDBOX_REQUIRED`.
     - A junk attestation gives `SENDER_SANDBOX_ATTESTATION`.
   - **bwrap pin differs.** A wrong bwrap sha256, a wrong bwrap size or a wrong openssl pin makes `_launch`
     refuse with `CARRIER_ACTUAL_TOOL_PIN` before the fork, with the placement unchanged. A changed launcher
     identity gives `SENDER_SANDBOX_LAUNCHER_BINDING`.
   - **NoNewPrivs absent.** It can only be produced unsandboxed: this bwrap always sets NNP itself, and the
     outer also sets it with readback. In that state the self-check refuses first with `NO_NEW_PRIVS`.
   - **Weakened sandboxes** (same pinned bwrap):

     | Variant | Self-check result |
     |---|---|
     | V0 exact argv | passes (positive control) |
     | V1 `--share-net` | NAMESPACES, NETWORK |
     | V2 extra bind of a home directory | FILESYSTEM_VIEW |
     | V3 extra environment | ENVIRONMENT |
     | V4 `/` left writable | FILESYSTEM_VIEW |
     | V6 docker socket bound | FILESYSTEM_VIEW, UNREACHABLE |
     | V7 group-readable `/usr` tree unmasked | FILESYSTEM_VIEW |
     | V5 without `--cap-drop ALL` | passes: bwrap drops all capabilities by default for a nonroot sandbox, and the check enforces the observed zero sets |

     No variant made a private read.

**Production entry** (`21_production.*`). The real `sender_launch.py` (outer and inner):
- verified the sandbox (`SENDER_SANDBOX_VERIFIED`);
- ran `root_payload`, which stops at the issued-record seam. `carrier_policy.load` raises
  `CARRIER_SEPARATE_ADMISSION_SCOPE` (`31_unsandboxed.json` `policy_load_real`), so the public code is
  `REFUSED`/`CLEANUP_REFUSED`;
- left the placement unchanged, created no session directory and read no private input. Exit status 1.

## 4. What is not restricted or not proved

1. **Same-UID processes outside the sandbox.** The external root dispatcher and any other process of the
   sender UID can still open the 0700 session directory, including `bundle.plain` during its few-second
   lifetime. The broker directory is the session directory by design. Only a separate account would close
   this, and that is an owner decision.
2. **The outer pre-entry step is unsandboxed**, with the account's groups.
   - It reads only the composition, the two tool bodies, the placement listing, the `/usr` metadata walk and
     the public request artifact. It holds no secret, and it waits with `--die-with-parent`.
   - The `/usr` walk took about 9 s on this host.
3. **Supplementary groups remain in the kernel credential.** An unprivileged user namespace denies
   `setgroups`. They are neutralised only by the view: the root-owned `/usr` plus masks, a sender-owned
   placement, and no other host tree.
4. **Nested user namespaces remain creatable inside** (`max_user_namespaces` 2147483647). The nested
   encryption-child bwrap needs them. Capabilities gained in a nested namespace cover only the sandbox's own
   namespaces. The kernel's user-namespace surface is unchanged.
5. **No seccomp filter is added.** `Seccomp: 2` is inherited from the WSL session; the outer shows the same.
6. **Remaining trust and pin gaps.**
   - The inner relies on the outer's argv attestation for "host owner uid 0". It independently verifies the
     same identity, including ctime, with an unmapped owner.
   - `/usr/bin/python3.12` is not byte-pinned (unchanged from the baseline and v2).
   - openssl inside the child is still executed by path, rechecked (the v2 residual).
7. **Not exercised.**
   - Real `PRO_SENDER` records.
   - The real supported-tool dispatcher. The URLs, envelope and joins were exercised only with synthetic
     results.
   - Real private inputs.
   - Any hosted run.
8. **Sender-host fact.** The sandbox needs unprivileged user namespaces (true on this WSL host, which has no
   AppArmor userns restriction). Root should record this (v2 r-m7).
9. **Carried minors.** The capture profile name `MAINTAINED_OWNER_THREE_FD_ENCRYPTION_V1` and
   `HOST_CAPTURE_SHA256` are unchanged, although the sender now runs whole-sandboxed (v2 r-m4).

## 5. Checks (`checks-out/`)

| Check | Result |
|---|---|
| Determinism | Two fresh worktrees at b393a905 gave the identical tree `40801f9d` and identical reports (`gen-run1.json` = `gen-run2.json`). |
| Pins (`check_pins_v3.py`) | 140 current-pin hits; 0 byte mismatches; 0 stale non-issued. Manifest: 43 members, 0 mismatched. `verify_decrypt_record` is unchanged against the baseline and v2. `validate_command`, `launcher_fd`, `close_plan` and `SANDBOX_PREFIX` are unchanged against v2. `sender_policy.py` is unchanged against the baseline. `root_tools` is retired and `carrier_policy` no longer mentions it. |
| Syntax (`check_v3_static.py`, python3.12) | 48 files, 0 errors. The host decrypt argv matches the `verify_decrypt_record` template. Shipped `carrier_policy.load()` refuses with `CARRIER_SEPARATE_ADMISSION_SCOPE`. |
| Profile (`check_profile_v2.py`, reused unchanged) | Same results as v2. |
| Provisioning (`check_provision_v2.py` + dry run) | `ALL_PINS_AGREE True`; tree `fa83107d` (201 entries); stops before install. The workflow is byte-identical to v2 (`081b51af`). |

**Changed files.**
- Against the baseline: 21 modified and 1 added (`carrier/sender_launch.py`).
- Against v2: 13 modified and 1 added, 334 insertions and 25 deletions. The substance is in:
  - `sender_capture.py`, +268;
  - `sender_launch.py`, new, 44 lines;
  - `carrier.py`, 19;
  - `carrier_policy.py`, 6;
  - `CARRIER_COMPOSITION.json` (`root_tools` removed);
  - the `PUBLIC_PACKET_MANIFEST` member.

  The remaining 7 entry files and `carrier_loader.py` change only by rebound pins.
- New identities: `BINDING_SHA256` / `CARRIER_COMPOSITION` `ac428865…`; `sender_launch.py` `1845fbfa…`.

**Stale issued records** (left unedited; the same three as v2):

| Record | Stale content |
|---|---|
| `BOOTSTRAP_ADMISSION.json` | manifest `bf5d26d2` |
| `CARRIER_ADMISSION.json` | workflow `27bd8feb` and the `20261120-01` branches |
| `INDEPENDENT_PROOF_PINS.json` | `g3_receiving` `02d08961` |

Re-issue order per Root R-M5: `CARRIER_ADMISSION`, then `INDEPENDENT_PROOF_PINS`, then Opus rebinds, then
`BOOTSTRAP_ADMISSION` last.

## 6. Files in this directory (44)

| File | What it holds |
|---|---|
| `make_g132_candidate_v3.py`, `provision-inner.sh`, `v3_sender_launch.py`, `v3_sender_sandbox.py` | The generator and its inputs. `v3_sender_sandbox.py` is a fragment with `@ENTRY_*@` placeholders. |
| `gen-run1.json`, `gen-run2.json` | The two generator reports. |
| `check_pins_v3.py`, `check_v3_static.py`, `check_profile_v2.py`, `check_provision_v2.py`, `checks.sh` | The checks. |
| `checks-out/` | 4 check outputs. |
| `qual/` | 7 scripts: `qualify.sh`, `qual_setup.py`, `qual_outer.py`, `qual_inner.py`, `qual_variant.py`, `qual_dispatcher.py`, `qual_common.py`. |
| `qualification-out/` | 21 outputs. |
| `HANDOFF_NOTE.md` | This note. |

The wrapper scripts create and remove only `/home/agent/opus-tmp/g132v3-*` directories. Host directory names
outside the sandbox view are withheld from the outputs (counts only).
