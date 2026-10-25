# R0035 finite installed-payload profile

The repository-only public mode `installed-payload` selects
`CONTROLLED_TASK_INSTALLED_PAYLOAD_V1`: original verifier index 85 and unchanged
command `bash tests/installed-payload-self-contained.test.sh`. The original
registry and compiler map all 117 nodes; this profile selects one and records
the other 116 as omitted.

## Source and original execution closure

The complete 112-line wrapper and 119-line installed-payload checker are pinned.
The original first scans the captured `skills` tree, then checks three generated
bad payloads, 21 ordinary route fixtures and one hardlink-refusal fixture: 26
checker calls in total. Three ordinary route cases pass and eighteen fail; the
separate hardlink case must fail. Those assertions remain in the original
wrapper and are not replaced by acquisition or a profile-specific oracle.

The original checker enumerates every descendant of `skills`. It reads UTF-8
lines, ignores undecodable text, and validates the physical ancestor chain and
single-link ordinary-file identity of declared packaged helpers. The finite
reader captures all ordinary bytes, names, types and empty directories, including
hidden and undecodable members. It retains the complete namespace even when the
original checker skips a member's text. Both the governor and route-owner
document are required within this supported profile. Other missing declared
targets remain actual absences for the original checker to decide.

At the captured baseline the source contains 71 files, 1,595,905 bytes and 12
directories: 68 skill files, two pinned programs and the selection-only registry.
All 29 existing packaged helper targets and their physical ancestors are captured.
The wrapper and checker are the only subject programs. The referenced helper
contents, generated shell scripts and root-only checker copy remain data; no
helper-route declaration grants execution authority.

The existing complete recursive reader and source-currentness checks are reused.
Source aliases, hardlinks, special files, unsupported modes and metadata refuse.
A newly added or removed member, changed text, same-byte replacement or changed
physical ancestor changes or invalidates acquisition. Unknown original program
or registry bytes refuse before runtime acquisition. Supported literals are
bounded at 1 MiB each and 8 MiB total; the recursive population retains the
existing 2,048-entry, depth-40 and 2,048-byte relative-path limits.

## Physical image and runtime

The existing fixed image-policy selector now covers the explicit tuple
`(SAFEGUARD_PROFILE, INSTALLED_PROFILE)`. It binds
`SINGLE_LINK_FILES_READ_ONLY_ROOT` into the acquired image and execution/reuse
key. The launcher copies `/work/` members from sealed descriptors using `--file`
and retains its final read-only root remount. This preserves the original
checker's `st_nlink == 1` observation. Runtime files retain `--ro-bind-data`.
No receiving caller chooses this policy, and no host source path is bound.
The existing private `/tmp` and `/dev/null` remain the permitted writable resources.

The deliberate hardlink is created by the unchanged original inside private
scratch, then rejected by its checker. That fixture does not weaken single-link
source admission or the read-only source mount. All earlier profiles keep their
previous materialization and contracts.

The runtime is the existing captured Bash, Python 3.12, `dirname`, `mktemp`,
`rm`, `mkdir`, `cat` and `grep` closure. Shell `printf`, tests, traps and loop
operations use builtins. The wrapper passes its actual `$BASH` path to Python;
`subprocess.run` calls that captured Bash with the captured checker path. It does
not search for or execute the generated route targets. Python runs through the
existing `-P -S -B` wrapper; the original fixture child additionally specifies
`-I -B`. The complete captured standard library includes `subprocess`, `pathlib`,
their imports, required builtin modules and extension modules. Startup files,
user-site imports and bytecode writes remain excluded.

The author capture records 712 runtime paths and 58,333,636 mounted bytes. Its
eight direct tools, required bootstrap/import extension and transitive loader
dependencies resolve to 18 captured ELF members. This read/import observation is
not execution of original node 85. The existing no-proc namespace, seccomp,
descriptor custody, timeouts, cleanup and resource limits remain unchanged.

## Complete private-write reservation

All generated route trees persist until the wrapper's final trap. The static
inventory is derived from the pinned literal route rows and original write
operations; it does not execute a checker or manufacture a successful result.

| Private population | Conservative count |
| --- | ---: |
| Payload file entries, including both hardlink names | 48 |
| Distinct payload file inodes | 47 |
| Directories, including the enclosing temporary directory | 121 |
| Diagnostic files | 3 |
| Possible wrapper here-document spools | 2 |
| Possible checker here-document spools | 26 |
| Total reserved file entries | 79 |

One diagnostic is `/tmp/payload-self-contained.out`; it remains in the private
namespace until teardown. The other two are inside the wrapper's temporary
directory. The root-only route copies the original checker as data. Every other
generated payload is bounded by the pinned wrapper's own byte size. Both names
of the private hardlink are charged as independent storage, and all possible
spools are charged simultaneously even when Bash implements them with pipes.

The source-scan output bound uses every possible reference or declaration line
from the acquired UTF-8 content, including all Python `splitlines()` separators.
It counts up to two reports per candidate, permits a full malformed declaration,
and reserves path widths, line numbers, four-byte escaping and a 64 KiB fixed
margin. Labels and exemptions are counted as possible failures. This calculation
allocates output and never decides checker acceptance. The three fixed private
diagnostics conservatively receive the same bound; an assertion's escaped
captured output has a separate stderr allowance.

At the captured baseline, the diagnostic bound is 189,394 bytes, stderr is
823,112 bytes and stdout is 4,096 bytes. The 64 KiB allocation granule reserves
5,570,560 bytes for content and 13,107,200 bytes for file/directory overhead:
18,677,760 bytes total, within the unchanged 32 MiB scratch limit. File and stream
limits remain 16 MiB. Larger acquired diagnostics must still fit before runtime
acquisition. No profile-specific or shared limit was enlarged.

## Qualification boundary

```bash
/usr/bin/python3 -B tests/work-graph-installed-cases.py
```

Ten source controls cover the exact original mapping, the complete recursive
population and physical routes, whole executable pins, required owners, dynamic
members and missing declarations, source-hardlink rejection, all persistent
private paths/spools, non-LF and full-declaration output bounds, and capacity
refusal. Source fixtures use an observer sentinel and assertive runtime/dispatch
tripwires and cannot produce original execution evidence.

Two `LiveCases` are gated by `R0035_FINITE_INSTALLED_LIVE=1`. Receiving must retain
an actual original positive and unchanged same-producer reuse, followed by
added-source refusal; the second case adds a semantic violation and requires an
actual failed original with no reuse. The positive checks every route transcript,
including the private hardlink refusal. Both cases check the acquired image
policy and actual raw exit. They are authored here and remain unexecuted until a
separately allocated receiving gate.

The public entry and physical-loader pins are updated. The independent wrapper
environment fixture's exact expected list includes planning, safeguard and
installed banks in wrapper order; its empty capture-key and preserved-sentinel
assertions are unchanged. Its probe is transport evidence, not original execution.

This profile supplies no scheduler, imported receipt authority, native or whole
117-node claim. The original 48 requirements, 20 cases, 117 nodes and eight raw
comparison failures retain their identities. Native/host/Windows/interlock gates
and the 458,752-byte combined-package cap with its 2,000-byte reserve are unchanged.
