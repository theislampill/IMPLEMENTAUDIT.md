# Paired verifier plan preflight

`python -B scripts/qualify-work-graph-verifier.py preflight PLAN.json` diagnoses
a planned legacy/DAG comparison without launching either subject verifier or
creating capture directories. It admits a finite, declared Git configuration
profile before starting Git. Unsupported configurations are refused; they are
never silently replaced with a different configuration for the observation.

The entry is standalone because the canonical qualifier has individual run and
compare entries, not a paired launcher. A caller should check its complete pair
before spending the full-run budget. Existing capture and raw comparison
behavior is unchanged.

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

Focused controls: `python -B tests/work-graph-correspondence-preflight-cases.py`.
