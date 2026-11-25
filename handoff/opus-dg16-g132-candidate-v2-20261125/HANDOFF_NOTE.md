# G132 prospective candidate v2: handoff note

Prospective source candidate only. It is not a launch commit, and it awards nothing.

- Baseline: `b393a905`.
- Predecessor: v1 `022a10f6`.
- Regenerate it with `make_g132_candidate_v2.py`, run from a clean worktree at b393a905, with `provision-inner.sh` beside it.

## Sender host tool pins (`CARRIER_COMPOSITION.sender_tools`)

These were measured on the nominated sender host, WSL Ubuntu 24.04, user `agent` (uid 1000). The raw output is in `sender_host_tools.out`.

| Tool | Bytes | SHA-256 | Package origin |
|---|---|---|---|
| `/usr/bin/openssl` | 1,005,368 | `b4f547c0f16272d1cc7f870330a6f2c243710c335e7a99c734ff7a0c6fdb2503` | `dpkg -S`: openssl; `dpkg-query -W`: openssl 3.0.13-0ubuntu3.16 |
| `/usr/bin/bwrap` | 72,160 | `e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71` | `dpkg -S`: bubblewrap; `dpkg-query -W`: bubblewrap 0.9.0-1ubuntu0.3 |

- Both files are mode 755, `root:root`, with one link. `/`, `/usr` and `/usr/bin` are 755 `root:root`.
- This bwrap is **not** the core's original launcher (`52231e1c`, bubblewrap 0.9.0-1ubuntu0.1). It is used only on the sender host.
- Root has not ruled on this sender launcher identity (review finding M1). That ruling is still open.
- `env` is no longer part of the sender tool set. `root_tools` (`env eb1c64bb…`, `openssl acc10176…`) is kept byte-identical, as instructed.
  - Note: in this code, `root_tools` was only ever read by the root (sender) role.
  - The hosted decrypt path takes its pins from the job-time `host_tools` adoption (`HT.ResolvedTools`), not from `root_tools`.
  - After v2, `root_tools` is validated by `carrier_policy.load()` but consumed by nothing. Root may want to drop it.

## Dispositions against the review

**B1 (encrypt argv).**
- `Commands.run('encrypt')` now builds `SC.SANDBOX_PREFIX + ['/usr/bin/openssl', …]`, which is exactly what `validate_command` accepts.
- Host `recipient` and `decrypt` keep the `env -i` form unchanged. `verify_decrypt_record` is byte-identical to the baseline.
- No other encrypt-argv builder or validator exists. `tool_broker.py` and `host_tools.py` construct no encrypt argv.

**M2 and M6 (sender tool pins and launcher custody).**
- The root role uses `binding['sender_tools']` (`openssl`, `bwrap`) in the existing `CARRIER_ACTUAL_TOOL_PIN` loop.
- The new `sender_tool_custody()` additionally requires all of the following:
  - a regular file, owned by uid/gid 0;
  - no group/other write, and no setuid/setgid;
  - an ancestry of exactly `/`, `/usr`, `/usr/bin`, each uid 0 and not group/other-writable.
- `carrier_io.read_file` already refuses:
  - symlinks;
  - any xattr, which covers file capabilities;
  - nlink ≠ 1;
  - identity change during the read.
- `current_tools()` rechecks the full observed rows (identity plus ancestry) for bwrap as well, at every capture currentness point.
- v1's weaker `sandbox_current()` and `SANDBOX_PIN` are removed.
- The exec is bound by descriptor:
  - `launcher_fd()` opens `/usr/bin/bwrap` once and requires its fstat identity and bytes to equal the carrier's pinned row.
  - The child `fexecve`s that fd (`os.execve(exec_fd, argv, {})`). `close_plan` keeps it, and `O_CLOEXEC` closes it at exec.

**M3 (Git custody).**
- The provisioning step installs the whole program tree from one package: `usr/bin/git` plus all of `usr/lib/git-core`, which is 201 entries: 1 + 2 directories + 47 files + 151 symlinks.
- The tree manifest digest is `fa83107dc7b2465aed4fef67808b0cb70ed2c09c74148cdd78c9ba1838965db3`.
  - One line per path: `path sha256 octal-st_mode`.
  - The hash is of the content for a file, of the link-target text for a symlink, and of the empty string for a directory.
  - Lines are sorted with `LC_ALL=C`, and the digest is the SHA-256 of all lines.
- The digest is verified on the staged tree before install, and the live tree must equal the staged manifest after install.
- The image's `/usr/lib/git-core` is replaced as a whole: it is moved aside into the root-owned work directory, which is deleted on exit.
- `/usr/bin/git` stays pinned to `824d5b2f…` (4,640,352 bytes).
- Not covered by this step:
  - `/usr/share/git-core/templates`;
  - the other `/usr/bin/git-*` front ends;
  - the dpkg database, which still records the image's 2.56.1.

**M4 (bwrap path).**
- The step does not touch bwrap. Code path:
  1. `run.py inventory()` calls `u.trusted('bwrap')`. That returns `None` when `/usr/bin/bwrap` is absent, and is allowed.
  2. `run.py prepare_host_prerequisites()` then runs `/usr/bin/python3.12 -I -S -B <source>/scripts/qualify-work-graph-c5-setup.py --provision-hosted-launcher`, with `SETUP_SHA 3b3078e9…` checked at `run.py:411`.
  3. In the source commit `e76a07b2`, `provision_hosted_launcher()` fetches `HOSTED_PACKAGE_URL` (snapshot.ubuntu.com bubblewrap 0.9.0-1ubuntu0.1, 50,178 bytes, `1b506492…`). It writes exclusively, with parent-identity rechecks, a 20-second deadline and a JSON receipt.
- This is reached through the `prepare` step, which `core_prepare_entry` runs.

**M5 (git package custody).**
- Per the Root ruling at b9f0938, nothing is vendored.
- Retrieval is digest-bound from the durable Launchpad PPA snapshot: `https://snapshot.ppa.launchpadcontent.net/git-core/ppa/ubuntu/20261101T000000Z/pool/main/g/git/git_2.56.0-0ppa1~ubuntu24.04.2_amd64.deb`.
  - A HEAD request returned HTTP 200 with content-length 7,773,244.
- The step checks:
  - `curl --proto =https --proto-redir =https --tlsv1.2 --max-filesize`;
  - the exact size and SHA-256;
  - the dpkg-deb `Package`, `Version` and `Architecture` fields.
- In-step network retries are used: `--retry 4 --retry-all-errors`. The run attempt itself is not retried.

**m1 and m2 (step environment and staging).**
- The step body runs as root under `sudo /usr/bin/env -i PATH=/usr/bin:/bin LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC /usr/bin/bash -s`.
- It calls every tool by absolute path.
- Staging is in a root-owned 0700 `mktemp` directory.

**m7 (profile check).** `check_profile_v2.py` also executes `run.py`'s unchanged `inventory()` body, so its hard-coded tool pins are exercised.

**M7 (stale issued records).** Three records are stale and are left unedited:

| Record | Stale content |
|---|---|
| `BOOTSTRAP_ADMISSION.json` | manifest `bf5d26d2` |
| `CARRIER_ADMISSION.json` | workflow `27bd8feb` and the `20261120-01` branches |
| `INDEPENDENT_PROOF_PINS.json` | g3_receiving `02d08961` and `20261120-01` |

Re-issue them in this order:
1. Root and the independent party issue `CARRIER_ADMISSION` and `INDEPENDENT_PROOF_PINS`.
2. The executor rebinds the pins.
3. `BOOTSTRAP_ADMISSION` is issued last.

## Files

| File | What it holds |
|---|---|
| `make_g132_candidate_v2.py`, `provision-inner.sh` | The generator, and the step body. `#DRY_RUN_*` blocks are stripped into the workflow. |
| `gen-run1.json` | The generator report. |
| `sender_rehearsal_v2.py`, `rehearse.sh`, `rehearsal.out` | A rehearsal through `carrier.Commands` with disposable inputs. |
| `check_pins_v2.py`, `check_pins_v2.out` | The pin check. |
| `check_profile_v2.py`, `check_profile_v2.out` | The profile check, plus `run.py` `inventory()` with its tool pins. |
| `check_provision_v2.py`, `dryrun.sh`, `provcheck.sh`, `provcheck.out` | A dry run that installs nothing, and an independent digest recomputation. |

The wrapper shell scripts hard-code this session's scratch paths, and they remove only directories they created under `/home/agent/opus-tmp/g132v2-*`.
