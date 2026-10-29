# R0035 original48 C5 input capture

This new source candidate concerns original48,
`bash tests/reproducible-release-asset.test.sh`. It is not R0039 criterion5
and does not recover the later C5 source that was lost.

## Separate data-only entry

The existing readme-effect loader gains `create_c5_input_capture(source_root)`.
It captures only the unchanged prefix owner, the new fixed C5 module, and
the fixed selection fixture through a separate path. The legacy `PINS`,
`_read`, `_Engine.sources`, default factory, and qualifier remain unchanged.
The loader compiles the exact captured module buffers and checks actual file
and ancestor identities before and after loading and around acquisition.
The loader's own file read is a physical-path guard, not an attestation of
the outer executing buffer; its caller still owns that execution identity.

`acquire()` returns observations and captured objects in memory. It writes
no result file, launches no child, runs no Git command, and offers no `run`
or receipt API. A journal reopened from disk cannot supply live producer
custody. Live producer custody and the before-consumer JOIN are unimplemented.

## Actual producer semantics

The preserved original creates two real Git clones using `--no-local` and
`--no-checkout`, then performs detached checkout and status checks. Both
worktrees survive until the original's EXIT cleanup. A source archive or
two directory copies cannot substitute for these clones.

The release builder selects genuine Zopfli 0.2.3.post1, with its actual
package metadata, Python/native implementation and dependencies. Its current
source projection has 73 canonical-plugin and 70 compatibility members.
The original event profile has 19 ordered roles and six release outputs:
plugin, compatibility, and checksum artifacts in each of lanes A and B.
These numbers describe the source contract; they are not observed events,
artifacts, successful builds, or canonical acceptance.

## Available input observations

Source capture includes every actual ordinary file, hidden member, present
Git byte, and empty directory within the unchanged prefix acquisition
bounds. It adds actual no-follow ancestor bindings and closes the source
again. Standalone Git bytes are checked with the existing narrow config and
storage validator. Their presence does not close Git clone execution or
out-of-tree runtime selectors; that remains a separate explicit blocker.

The fixed current selection is the actual system Python 3.12 route. It
captures real Python aliases, the interpreter and known startup/native code,
the complete standard-library file population including bytecode caches,
the five search-root name/type populations, actual `.pth` programs, NSS
files and NSCD absence. Actual runtime files and their resolved aliases and
ancestors are captured twice. No synthetic Python wrapper is generated.
No `-S`/`-I`, HOME, or PYTHONUSERBASE substitution is introduced for the
original. Source controls may use isolated/no-site flags for their observer.

Known exact sitecustomize and conditional coloredlogs startup programs have
the same bounded source semantics as the preserved system startup profile.
Unknown customizers, nontrivial added `.pth` programs, interpreter/venv/zip
selectors, unsupported NSS syntax/services, or drifting identities refuse.
The data capture does not establish the later child's UID mapping or execute
normal startup as proof.

At authoring, the three supported global dist-packages roots contain no
Zopfli provider. The selection fixture has no fabricated provider pins.
Absence returns a concrete `ZOPFLI_PROVIDER_MISSING` blocker. A present
provider remains unqualified until exact code, metadata, normal startup,
alias, native dependency and selection closure are independently reviewed.
An isolated task venv may supply that future genuine dependency; this
candidate does not install one, select the disappeared historical venv,
substitute compression, or classify portable engineering as exhausted.

## Resources and remaining gates

The retained historical source observation was 1,487 worktree files and
97,809,560 bytes. Two simultaneously retained worktrees therefore require
at least 195,619,120 bytes, exceeding 32 MiB before Git storage, output files,
temporary compression data, or metadata. This is a source-derived resource
gap. It is not an actual C5 execution failure, a new resource limit, or a
current source-size observation. A future exact prepared source and genuine
clone/producer route must derive its actual complete resource requirements.

Every return remains `runtime_complete=false` and
`canonical_acceptance=UNQUALIFIED`. The record retains blockers for actual
Git execution closure, the actual C5 resource profile, live producer custody,
the before-consumer JOIN, and compressor closure. It does not mint a
completion credential or authorize a generic executor, native/Codex effects,
publication, release, merge, or audit closure.

## Focused controls

Three controls are authored in `tests/work-graph-c5-input-cases.py`:

1. Actual selected normal-startup bytes/aliases and ancestor replacement.
2. Complete hidden/Git input membership and added startup-selector refusal.
3. Data-only acquisition without subprocess dispatch and default loader
   operation when the additional C5 source files are absent.

They remain unrun until independent review of the frozen source and exact
affected allocation. They provide source-control evidence only when run;
they do not dispatch original48 or establish actual release results.
