# R0035 experimental acquired prefix24

Status: implemented opt-in contract; actual prefix24 execution qualification is
not yet earned. The focused admission and live-consumer controls pass. The
separately requested tiny live controls on the implementation host stop at
Bubblewrap's fresh proc mount with `Operation not permitted`, before the subject
shell starts. This is an environment refusal, not an accepted prefix result.

The existing `prefix` route and `create_composed_prefix_session` default remain
`COMPOSED_SOURCE_PREFIX_23_V1`. The canonical serial verifier and its no-reuse
fallback are unchanged. The established scope and limitations are recorded in
[R0035-PORTABLE-VERIFIER.md](R0035-PORTABLE-VERIFIER.md).

## Exact additional source

The explicit `prefix24` route selects `COMPOSED_SOURCE_PREFIX_24_V1`. It retains
the original 117-node compiler mapping and executes exactly the original first
24 nodes, indices 0 through 23, in one Bash shell. The last command is the
unchanged `bash scripts/check-added-lines-clean.sh HEAD`. It stops before original
index 24, `tests/lean-discipline.test.sh`; no terminal or later successor is added.

The canonical registry remains pinned to SHA-256
`77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698`.
The selected prefix is 39,603 bytes with SHA-256
`98246f2b17a7c0c1f1d443e587b0eec9ac2240ecc1a4edda7c46ecefdc81e8a4`.
All prefix23 executable pins remain required. Prefix24 also pins these complete
transitive executable files:

| Source | SHA-256 |
|---|---|
| `scripts/check-added-lines-clean.sh` | `91bd5ab49ae20da3113b29b44d2c7492e4d838fddd68ece758c585316522936f` |
| `skills/implementaudit/scripts/repo-state.sh` | `b2220d0627c5e66d106bb3ce8a9daafb5310b87643b9281d63db5a5aa886df3b` |

Changed or missing executable source refuses admission. The existing whole
working-namespace and standalone Git acquisition, renderer `NOT_APPLICABLE`
branch requirement, environment/runtime closure, source normalization, resource
bounds and live-producer custody remain in force. Unknown profile strings and
malformed profile types refuse before creating an evidence directory.

## Required proc and descriptor interface

Both newly reached scripts use Bash process substitution. Prefix23's image has
no proc filesystem or `/dev/fd`, so the original command cannot execute there.
The prefix24 launcher adds only a fresh proc mount inside Bubblewrap's already
private PID namespace, remounts it read-only and creates the link
`/dev/fd -> /proc/self/fd`. It does not bind the host proc filesystem. The default
prefix23 launcher does not receive this interface.

The original fixed environment, dropped capabilities, namespace-entry seccomp
restrictions, sealed input mounts, empty external stdin, bounded private source
and temporary filesystems, and bootstrap descriptor closing remain unchanged.
The profile identity and namespace contract are bound into the acquired input;
dispatch evidence records the selected proc interface. A refused namespace
launch has no weaker retry route. An observed nonzero child exit is retained
as such and cannot issue a reusable success.

Proc is an execution interface for the inspected, pinned source. This change
does not acquire arbitrary kernel/proc data, admit arbitrary programs or qualify
every process-descriptor observation. Actual controls must establish the stated
process isolation on a host that permits the fresh proc mount.

## Invocation and receiving boundary

On a supported host, use a complete candidate with an admitted standalone Git
namespace and a fresh evidence path outside that candidate:

```bash
printf '%s\n' '{"operation":"run"}' '{"operation":"run"}' |
  /usr/bin/python3 -B scripts/qualify-work-graph-verifier.py prefix24 \
  /absolute/complete-standalone-candidate /absolute/fresh-prefix24-evidence
```

The corresponding Python factory requires the exact keyword
`profile="COMPOSED_SOURCE_PREFIX_24_V1"`. Omitting it selects prefix23. Both routes
accept only `{"operation":"run"}` requests, at most 4 KiB per line. A caller cannot
supply a receipt, claimed exit, alternate scope, command or reuse plan. Prefix23
and prefix24 have separate live session types and issued-result keys. A new
session cannot import a prior session's result.

A successful second request can reuse only the same live producer's complete
whole-group receipt after currentness and retained-byte/mode/object checks.
Failures, incomplete execution, expiry, source/runtime/observer drift and changed
retained output refuse reuse. Private shell and filesystem effects are discarded;
no receipt supplies effects to `lean-discipline` or any omitted successor.

## Verification and coverage accounting

The ordinary focused command is:

```bash
/usr/bin/python3 -B tests/work-graph-prefix-cases.py -v
```

Its constructed controls cover exact source selection, both new executable pins,
default preservation, unknown profiles, bounded run-only requests, profile
separation, refusal after failed/incomplete execution or changed evidence, and
absence of host-proc binding or a weaker launcher retry. These controls do not
claim actual canonical execution.

The separately requested tiny real launcher controls are:

```bash
R0035_PREFIX24_LIVE=1 /usr/bin/python3 -B \
  tests/work-graph-prefix-cases.py NamespaceCases -v
```

They run a constructed process-substitution subject through the actual acquired
runtime and launcher. They require the unchanged prefix23 image to retain the
missing-`/dev/fd` failure, and require prefix24 to execute it successfully. A
second prefix24 subject checks host-PID/source-path isolation, closed retained
input descriptors, blocked namespace operations and read-only proc controls.
`R0035_PREFIX24_EVIDENCE=/absolute/fresh-directory` optionally retains their raw
streams, actual exits, runtime identity and exact control/source digests. Retained
controls are expressly labeled as constructed, not canonical qualification.

The implementation host retained the expected prefix23 child failure. Both
prefix24 subjects stopped before execution because the host denied the proc
mount. A minimal setup-only probe, without source/runtime mounts, seccomp,
capability dropping or a subject program, reproduced that same refusal. No host
setting was changed and no host-proc fallback was attempted. A requested live
test failure cannot be relabeled as a successful prefix execution.

Actual acceptance still requires a proc-capable environment, the complete
candidate source, retained raw execution/consumption evidence and non-authoring
review. A sparse worktree with missing tracked source is not a qualifying
candidate. The prior finite union remains 24 distinct original nodes of 117;
93 remain outside that qualified union. Only after separate actual prefix24
qualification could its overlap with prior index 112 increase the union to 25,
leaving 92. This extension alone does not establish whole-verifier C1/C2/C3/C6/C7,
canonical equivalence, native scheduling or accepted JOIN, host capability,
release acceptance or R0035 closure.

All changed helper, test and maintenance files are repository-only. Their source
is outside both package payload projections; no cap, reserve, compression or
packaged runtime interface changes are part of this increment. Final artifact
provenance and package acceptance remain separate checks for the integrated
source.
