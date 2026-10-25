# Paired verifier plan preflight

`python -B scripts/qualify-work-graph-verifier.py preflight PLAN.json` diagnoses
a planned legacy/DAG comparison without launching either subject verifier or
creating capture directories. It admits a finite, declared Git configuration
profile before starting Git. Unsupported configurations are refused; they are
never silently replaced with a different configuration for the observation.

The entry is standalone because the canonical qualifier has individual run and
compare entries, not a paired launcher. A caller should check its complete pair
before spending the full-run budget. Ordinary capture and raw comparison
behavior remains available. The optional v2 retention path below adds an actual
common workspace and separate retained destinations within the same run owner.

## Supported Git observation profile

The intended run environment must already declare all three values:

| Variable | Required value | Declared selection |
| --- | --- | --- |
| `GIT_CONFIG_NOSYSTEM` | `1` | Excludes system Git configuration. |
| `GIT_CONFIG_GLOBAL` | `/dev/null` | Excludes both normal global configuration files. |
| `GIT_ATTR_NOSYSTEM` | `1` | Excludes system attributes. |

These are properties of the planned environment, included in its full digest.
Setting them only for the diagnostic would describe a different planned run.
The preflight does not set them on the caller's behalf. A normal inherited
environment without these declarations returns exit 2 before any Git process.
Git documents these selection inputs in its
[environment contract](https://git-scm.com/docs/git#Documentation/git.txt-ENVIRONMENT).

All other `GIT_*` variables are refused except `GIT_OPTIONAL_LOCKS` (`0` or `1`)
and `GIT_PAGER` (empty or `cat`). `PAGER` has the same finite values. Loader
injection variables (`LD_*`, `DYLD_*`, `GCONV_PATH`) are refused. This includes
refusal of trace destinations, command-scope configuration injection,
repository/index/object selection, external diff and unknown future `GIT_*`
inputs. No configuration-discovery subprocess runs before these checks.

The profile currently requires Linux, the existing no-follow descriptor APIs,
`/proc/self/fd`, and a root-owned, non-group/world-writable ELF Git executable
selected through the actual PATH and resolving to `/usr/bin/git` or
`/usr/local/bin/git`. A PATH-selected wrapper is refused before execution. The
exact executable bytes and physical file identity are bound; each fixed Git
command executes the checked open descriptor. This is an explicit host floor,
not portable proof for another executable or platform.

The implementation reads the actual Git directory, optional `commondir`, common
configuration, and enabled `config.worktree` directly as bounded no-follow
regular files. Configuration admission accepts a conservative syntax with no
includes, conditional includes, escapes, or continued values. Its finite key
table admits ordinary repository/filemode/line-ending settings, disabled
fsmonitor/untracked-cache settings, `/dev/null` hook/attribute/exclude paths,
worktree configuration selection, user metadata, branch/remote metadata, and
disabled commit signing. Callback, clean/process filter, pager, external diff,
textconv, trace, repository-routing, partial-clone and unknown keys are refused
before Git starts. A harmless configuration outside this subset is still an
unsupported input; there is no permissive fallback.

The observation binding records exact selected control-file bytes and paths,
including Git-file and common-directory selection, symbolic/detached `HEAD`,
the physical index, selected attribute/exclude files, and user attribute/exclude
defaults under the declared HOME/XDG selection. Gitlinks and unsupported index
modes are refused immediately after the fixed index-listing command, before
status can inspect another repository. System and global configuration bytes
are not read because the declared environment already excludes them.

Before the first Git process, the captured physical index is checked directly
against a finite inline SHA-1 format profile: versions 2, 3 and 4, with optional
`TREE` and `REUC` extensions. The guard checks the header, checksum, entry and
extension boundaries, including v3 extended flags and v4 compressed names.
It refuses the `link` extension used by split indexes, even when no
`core.splitIndex` configuration key exists. Other extensions, unknown versions
and malformed structures also refuse. The admitted format is included in the
Git-context binding. This adds no split-index support or Git discovery command.
The [Git index format](https://git-scm.com/docs/gitformat-index) defines these
boundaries and the shared-index reference. Incidental `link` bytes in filenames
and unreferenced `sharedindex.*` files do not create index indirection; ordinary
supported indexes still pass with those present.

Only the fixed source-observation commands are admitted. They use disabled
optional index writes, an explicit no-pager argument, closed stdin and captured
stderr. The first two are recorded observation controls; the full inherited
environment digest still describes the actual planned run. Within the admitted
profile they preserve the original source-observer fields, which remain
separate from the additional Git-context binding.

## Closed plan contract

The top-level members are exactly `schema`, `expected_currentness`, and `runs`.
The schema is `implementaudit.verifier-pair-plan.v1`.

`expected_currentness` contains `source_sha256`, `engine_binding` with exact
`driver_sha256`/`compiler_sha256`, `base_environment_sha256`, and the required
`git_observation_sha256`. The latter binds configuration selection, exact
control/executable observations, declared environment and observation policy;
it does not replace or normalize `source_sha256`. Plans omitting it are refused.
The public
Python helper `verifier_preflight_currentness_v1()` obtains these observations
from the loaded qualifier and its source root. Bind them after the intended
source and environment are frozen; do not copy a historical receipt.

`runs` contains exactly one `legacy` and one `dag` declaration. Each contains:

- `mode`: the fixed route name; no command operand is accepted.
- `output`: a fresh absolute canonical path, without symlink aliases. The two
  output namespaces must not overlap.
- `base_environment_sha256`: the intended inherited environment digest. Both
  routes must match the currently observed base environment.
- `capture`: exactly the six existing option names below. Boolean options are
  strict JSON booleans. `stdin_file` is null or an absolute canonical path;
  combining it with `empty_stdin` is refused.

Example plan creation from the repository root, with the plan outside source:

```bash
# These declarations must also describe the intended actual runs.
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_ATTR_NOSYSTEM=1
python -B - /tmp/r0035-pair-plan.json <<'PY'
import importlib.util, json, sys
from pathlib import Path
path = Path.cwd() / 'scripts/qualify-work-graph-verifier.py'
spec = importlib.util.spec_from_file_location('verifier', path)
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)
binding = owner.verifier_preflight_currentness_v1()
capture = dict(retain_repro_assets=True, stdin_file=None, empty_stdin=True,
               capture_dist=True, capture_portal_events=True,
               retain_repro_events=True)
plan = dict(schema='implementaudit.verifier-pair-plan.v1',
            expected_currentness=binding,
            runs=[dict(mode=mode, output='/tmp/r0035-pair/' + mode,
                       base_environment_sha256=binding['base_environment_sha256'],
                       capture=capture) for mode in ('legacy', 'dag')])
Path(sys.argv[1]).write_text(json.dumps(plan, sort_keys=True) + '\n')
PY
python -B scripts/qualify-work-graph-verifier.py preflight /tmp/r0035-pair-plan.json
```

This example deliberately returns **1 / BLOCKED**: distinct output roots enter
the captured environment, artifact declarations and dist snapshot locations,
forcing corresponding full-record raw predicates false. All raw data remains
part of the unchanged comparison contract.

## Results and limits

| Exit | Disposition | Meaning |
| --- | --- | --- |
| 0 | `NECESSARY_PRECONDITIONS_ONLY` | No assessed static conflict or current binding mismatch was found. |
| 1 | `BLOCKED` | The report identifies planned raw-predicate conflicts, currentness drift, or known launch precondition failures. |
| 2 | Refusal | Malformed, unbound, unsupported, oversized or unavailable input/observation. |

The report binds the canonical plan identity; the CLI also binds the exact
plan-file bytes. Plan files are strict JSON, at most 65,536 bytes, acquired as
no-follow regular files. It reports hashes, never inherited environment values.

`raw_observables_equal` is always null, `subject_launches` is zero, and authority
is `NONE`. Unassessed raw predicates remain explicitly unqualified. Different
real run IDs, processes, clocks, filesystem stamps, generated timestamps and
raw stdout/stderr require an owner-admitted correspondence contract; equal path
spellings do not settle them. Declared stdin content and future process effects
are not qualified by this preflight.

Source/environment observations are checked before and after the diagnostic.
The admitted Git context is also reacquired before and after each fixed Git
command. These are observations of frozen inputs, not an atomic filesystem
lease or a sandbox against concurrent replacement of admitted controls. They
retain the existing source observer's partial coverage and do not establish a
complete filesystem/toolchain acquisition or a lease covering a later launch.
Each actual run still needs its existing source and execution checks.
No historical failure, original acceptance denominator, native event, or issue
closure changes because a preflight completes.

Read-only preflight controls:
`python -B tests/work-graph-correspondence-preflight-cases.py PairPreflightTests`.

## V2: one actual workspace and separate retention destinations

`implementaudit.verifier-pair-plan.v2` keeps the same top-level and currentness
members. Each run adds a `retention` path. Both `output` declarations must name
the same actual capture directory **W**. The two retention paths **S-legacy**
and **S-dag** must be distinct siblings of W under one preexisting, owned,
mode-0700 parent outside the source tree. Only those three declared names may
appear in that parent. The plan itself and comparison output belong elsewhere.
Aliases, overlapping names, occupied destinations and unexpected members refuse.
The v1 rule rejecting equal output roots is unchanged.

The v2 preflight still launches no subject, creates no directory, and reports
only necessary preconditions. Equal W declarations remove the known path-based
conflict; they do not establish raw correspondence or prove kernel support.

For an already acquired v2 plan, the corresponding operations have this form:

```text
python -B scripts/qualify-work-graph-verifier.py preflight PLAN.json
python -B scripts/qualify-work-graph-verifier.py legacy W --retention-plan PLAN.json [the plan's capture options]
python -B scripts/qualify-work-graph-verifier.py dag W --retention-plan PLAN.json [the same capture options]
python -B scripts/qualify-work-graph-verifier.py compare S-legacy S-dag RESULT.json --retention-plan PLAN.json
```

These are individual owner operations, not a paired launcher. Either route can
be first. Both routes must use the exact same capture options and acquired base
environment from the plan. A second run requires W to be absent and the first
destination to be a valid completed retention from that plan. An incomplete
pair or refusal is retained for review; the owner does not erase it or retry
into the same destination.

### Acquisition and physical retention

At dispatch, the owner reacquires source, loaded-engine, Git-context and complete
inherited-environment bindings. It also compares the actual environment mapping
directly with its acquired mapping immediately before starting the child. The
actual child receives that complete mapping plus the existing declared W-based
capture overrides. No variable is stripped, synthesized or replaced to produce
equality. The Git observation profile above remains mandatory; the physical
Git control-file binding must remain current. Optional index writes or other
control-file changes can therefore refuse sealing even when a later textual
Git status is clean.

W is the actual output location during execution. Raw argv, child overrides,
artifact declarations, dist paths, portal request paths and repro session paths
retain W. After actual completion and validation, the owner uses a same-filesystem
`renameat2(RENAME_NOREPLACE)` to move the directory into `S/capture`. An occupied
destination, unsupported operation or cross-device error refuses; there is no
copy or replacing-rename fallback. The [Linux rename contract](https://man7.org/linux/man-pages/man2/rename.2.html)
defines the no-replace flag and its filesystem support requirement.

Each successful destination contains exactly:

| Member | Role |
| --- | --- |
| `intent.json` | Exact plan-file and canonical-plan binding, route and expected currentness. |
| `capture/` | The original W directory, moved intact. |
| `custody.json` | Actual process custody, currentness, complete byte/mode/identity census and the two actual moved-root observations. |

The owner writes its own capture files through held directory descriptors with
exclusive, no-follow creation. It preserves the primary exit before checking
descendants or doing post-run source/record work. A census rejects links,
special files, foreign ownership, unstable membership or byte/mode changes.
Existing validators enforce the exact nested populations. Every retained member
is read from `S/capture`, while the original literal W path checks remain in
force. No raw record is relabeled or reserialized after capture. No captured
file mode is changed for sealing. The moved root's genuine before/after ctime is
recorded separately; inner member identities and bytes must remain unchanged.
Owned file and directory writes are synchronized before sealing.

The first completed destination is also censused before the next actual run and
checked unchanged before the second destination is sealed. Its complete envelope
binding is retained in the second custody sidecar. Sealed comparison verifies
both original-record contracts, both physical censuses, any prior-destination
binding and current source/environment before calling the original raw comparator.
The raw comparator function and `NONE_RAW_BYTES` policy are unchanged.

Sealing is an owner custody and integrity contract. The files remain ordinary
files with their observed modes. An unrelated same-UID writer can still damage
them; readback detects changed bytes, modes or identities. Sidecars do not
authenticate imported execution or confer native provenance. Restoring files
elsewhere may still satisfy the historical raw-record reader, but it cannot
manufacture this live retention's physical identity binding.

### Actual child custody and refusals

The optional path requires a dedicated, single-threaded main Python process on
Linux, no preexisting children, default SIGCHLD handling, a consistent single
proc PID view, child-subreaper support, pidfd operations, Linux all-child wait
semantics and no-replace rename support. These are checked by the actual owner;
unsupported capabilities refuse. The additional libraries load only when this
path is requested, leaving the ordinary and finite acquired loader startup
imports unchanged.

The owner enables and reads back its child-subreaper setting before creating
observer or subject children. Linux describes orphan adoption in
[PR_SET_CHILD_SUBREAPER](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html)
and setting readback in
[PR_GET_CHILD_SUBREAPER](https://man7.org/linux/man-pages/man2/PR_GET_CHILD_SUBREAPER.2const.html).
It acquires the one real child behind a pre-exec byte gate, confirms its pidfd's
kernel child ownership, and releases the original argv/cwd/environment in that
same process. There is no wrapper process or new PID namespace. Primary status
comes from `waitid(P_PIDFD)`; an unsupported auto-reap or a missing status refuses
instead of allowing a recycled numeric PID or a library fallback to supply a
verdict. Only an all-child `ECHILD`
under the still-valid ownership scope admits sealing; a live adopted child
refuses. The relevant wait interfaces are documented in
[waitpid/waitid](https://man7.org/linux/man-pages/man2/waitpid.2.html).

A refusal cleanup has a three-second deadline. It discovers candidate children,
opens stable pidfds, confirms actual child ownership through `waitid(P_PIDFD)`,
and signals only those owned descriptors. It never uses `kill(-1)`, group signals
or a bare numeric-PID signal. The [pidfd interface](https://man7.org/linux/man-pages/man2/pidfd_open.2.html)
provides stable task references. The
[proc children list](https://man7.org/linux/man-pages/man5/proc_tid_children.5.html)
can omit entries during exits and depends on the optional `CONFIG_PROC_CHILDREN`
kernel feature. The owner prefers that file when present. Only a missing-file
error selects incremental numeric-entry discovery from `/proc`; other read
errors still refuse. The fallback checks the same proc/thread scope before and
after walking, checks the cleanup deadline while walking, and bounds both the
numeric population and its serialized names. It excludes the owner itself.
Listed processes may be unrelated: each candidate still needs a stable pidfd
and kernel child confirmation before any signal. Neither listing, including an
empty or incomplete one, establishes ownership or quiescence. Final kernel
`ECHILD` remains required. The owner restores its prior subreaper flag only after
that proof. Incomplete cleanup leaves the scope unsealed and makes no success
claim; it does not clear the flag while children remain.

If sealing refuses after a primary exit of 0, `capture/exit-code.txt` or the
still-unmoved `W/exit-code.txt` preserves the actual primary 0, while the qualifier
returns 2. `refusal.json` records that distinction outside the raw tree. An
uncatchable interruption can leave only the intent and partial capture. No
custody marker means the destination is unsealed. Errors after a rename attempt
can leave its physical completion uncertain; the refusal does not invent a
successful move or automatically copy/retry it.

The aggregate census is finite: 128 MiB per file, 2 GiB total observed bytes,
278,528 entries, depth 64 and a 128 MiB manifest bound. These are additional
retention constraints, including room for existing repro process records larger
than the 16 MiB explicit-input bound. They are not a claim that every possible
historical capture fits the new envelope. Proc cleanup discovery is bounded to
65,536 bytes and 4,096 candidates. For the fallback these bounds apply to the
visible numeric proc population, including nonchildren; exceeding them refuses
cleanup rather than increasing a limit. Other-child terminal records and the child's
pre-exec inherited-descriptor census are each bounded to 4,096. The descriptor
census closes inherited handles; it is not process-quiescence evidence.

### Bounded controls and acceptance boundary

`CaptureRetentionTests` in the existing preflight case file has four conceptual
controls: actual same W with distinct destinations; full base-environment drift;
fixed occupied/aliased/unexpected-member/live-writer refusal variants; and retained
raw-byte tamper. The live-writer variant is a real double-fork/setsid descendant
holding and writing the actual capture stdout. All subject execution in those
controls uses a tiny fixture registry and the existing real runner. The default
case-file entry runs both classes; the retention class can be selected directly.

This source change does not turn those control sources into executed evidence.
It changes no original acceptance requirement, case or node, and does not revise
any retained raw result. R35-V03 and the original exact-byte oracle still govern.
Real run IDs, process ancestry, clocks, measured durations, events and raw streams
remain actual observations. The historical eight raw REDs, 48 requirements,
20 cases and 117 nodes remain unchanged. Authority is `NONE`; no retirement,
native trust, whole-issue readiness or closure follows from a retained capture.
