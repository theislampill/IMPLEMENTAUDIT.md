# R0035 finite planning and authorization fixture profiles

This repository-only increment adds three explicit original-command profiles to
the existing finite acquisition helper and public qualifier. It reuses the
existing compiler, physical reader, captured runtime, isolated-leaf launcher,
live receipt owner and serial no-reuse fallback. It adds no scheduler,
controller, native authorization issuer or campaign authority.

## Exact original scope

| Public mode | Profile | Original index | Unchanged command | Captured files |
|---|---|---:|---|---:|
| `plan-quality` | `CONTROLLED_TASK_PLAN_QUALITY_V1` | 84 | `bash tests/plan-quality-contract.test.sh` | 16 |
| `authorization-binding` | `CONTROLLED_TASK_AUTHORIZATION_BINDING_V1` | 31 | `bash tests/authorization-binding-contract.test.sh` | 12 |
| `read-only-plans` | `CONTROLLED_TASK_READ_ONLY_PLANS_V1` | 80 | `bash tests/read-only-plans-lane.test.sh` | 41 |

Each selection revalidates the pinned original registry and the compiler's actual
117-node mapping. It selects precisely one original node and records the other
116 as omitted. None of the original wrappers, checkers, fixtures, registry
commands or original command bytes changes. The registry is an acquisition
input and is not mounted for a wrapper that never reads it.

The source capability is separate from original-command execution credit. The
focused admission bank never acquires a runtime or dispatches a process. Its
optional live bank remains gated by `R0035_FINITE_PLANNING_LIVE=1` and must be run
under the receiving owner's explicit namespace allocation before any actual
execution/reuse claim. All result envelopes retain `authority=NONE` and
`canonical_acceptance=UNQUALIFIED`.

## Complete program and input closure

### Plan-quality, original index 84

Both the complete wrapper and complete `check-plan-quality-contract.sh` are
pinned. Their selected execution has 21 checker calls, including loop expansion.
The thirteen data files include both default plans, the phase template,
reconstructibility negative, plan lifecycle and state-comparison references,
read-only template, default child prompt, all three status fixtures, and both
explicit negative plan/prompt fixtures. A status, campaign or PR-body argument
does not remove the checker's default plan reads.

The original wrapper creates nine copied campaign plans, four PR bodies, two
literal negative plans and seven diagnostic files. All remain private writes.
Source modes are preserved on the read-only source mount because `cp` must
produce writable private copies before the wrapper appends campaign rows.
Normalizing those source files to mode `0444` would change this original behavior.

### Authorization-binding, original index 31

The whole 17,469-byte helper is pinned, including its unselected rehearsal code.
Every original call selects `--state`, `--auth` and/or `--invocation`; none
selects first-argument `--phase`. Therefore the socket mediator, producer stub,
rehearsal launcher and terminal publisher are outside this fixed branch, not
silently substituted or treated as native qualification.

The nine data inputs are PROTOCOL, STATE, two state fixtures, three authorization
records and two invocation fixtures. The three authorization records are also
byte-pinned: the helper expands the value of `binds:` in an unquoted shell loop.
Unknown record bytes could introduce filesystem glob observations, so they
refuse acquisition rather than inheriting a literal-only namespace claim. This
restriction does not interpret a grant or modify the original checker. State,
invocation and documentation inputs remain captured data.

All seven private adversarial files come from the unchanged wrapper. The
default-deny/source-chain cases, missing source, parameter drift, no-binds,
bound-but-unsupplied, duplicate-key and no-final-newline cases retain their
original commands and assertions. This is authorization-fixture qualification;
it confers no permission to commit, push, publish or execute a native task.

### Read-only-plans, original index 80

The complete wrapper, parity checker and plan-quality checker are pinned. The
37 data files include every literal file read by parity plus the plan checker's
default and transitive reads. They include scripts that parity reads as text;
those scripts are not promoted into executed code. The captured 41-file source
population at the original base is 314,821 bytes.

Parity's required directory probes for `fixtures/read-only-plans`,
`fixtures/secret-hygiene` and `fixtures/dogfood-bootstrap` are covered by the
physical parent directories of the captured required files. Their identities
are rechecked. `docs/audits` is likewise required by its two read files. The
originals do not enumerate directory members or probe an optional source path.
A missing required file or directory refuses before runtime acquisition; no
absence is converted into a passing original negative.

## Runtime, resources and effects

The selected shell tools are already in the existing prefix runtime capture:
`bash`, `dirname`, `rm`, `mktemp`, `cp`, `grep`, `cat`, `tr`, `head`, `sed`, `awk`
and `wc`, plus the captured Python3.12 interpreter used by the checker and
launcher. Physical ELF inspection of these 13 direct tools resolves 23 members;
their interpreters and complete `DT_NEEDED` dependencies are within the existing
captured library set. No new runtime tool or host-path execution route is added.

The existing runtime acquirer still captures actual resolved bytes, alias and
physical identities, the bounded Python3.12 standard library and extensions,
and rechecks the closed population. The Python wrappers retain `-P -S -B`,
fixed hash seed and umask `022`. Site hooks, user packages, bytecode, host root,
network, general devices and proc remain unavailable in these profiles.

Every source file is bounded at 128 KiB and each complete source at 1 MiB. The
unchanged 32 MiB private scratch, 16 MiB file/stream, 4,096-descriptor, 1 GiB address,
90-second CPU and 120-second wall limits still apply. Temporary accounting uses
the existing 64 KiB conservative allocation granule and inode/directory overhead.

| Original index | Simultaneously charged temporary files | Directories | Reservation basis |
|---:|---:|---:|---|
| 84 | 45 | 1 | Nine actual-sized copied plans plus 128 appended bytes each; four PR bodies; two generated plans; seven diagnostic files; 21 checker and two wrapper spools |
| 31 | 7 | 1 | Exact original literal private sizes 20, 28, 79, 28, 66, 21, 78 bytes |
| 80 | 5 | 0 | Reused negative-output file, three plan-checker spools and one parity-checker spool |

Diagnostic bounds derive from acquired data sizes with four-byte expansion and
a 64 KiB fixed margin. Whole pinned checker sizes bound their here-document
spools. The helper reserves every possible spool even if Bash uses a pipe and
charges overwrites simultaneously. Scratch, largest-file and both stream
capacities are checked before runtime acquisition. These bounds only allocate
resources; they do not determine semantic acceptance.

The only mutable resources remain private bounded `/tmp`, `/dev/null` and
observer output streams. Nothing writes the source projection, carries an
effect into a successor or reconstructs accepted live custody from stored JSON.
Current source, runtime, engine, source modes, image and retained output remain
required for reuse; failed/interrupted execution has no reusable receipt.

## Focused verification and receiving gates

Run the portable source controls with the supported interpreter:

```bash
/usr/bin/python3 -B tests/work-graph-planning-cases.py
/usr/bin/python3 -B tests/work-graph-finite-entry-cases.py
/usr/bin/python3 -B tests/work-graph-readme-effect-cases.py LoaderCases AdmissionCases
```

The planning bank checks the real 117-node mapping, explicit public modes,
default-sensitive closure, read-as-data distinction, fixed branch pins, every
required data-file absence, changed programs/registry, alias refusals, captured
semantic mutations, spool/copy/diagnostic reservations and reduced capacities.
Its observer sentinel and runtime/dispatch tripwires prevent admission controls
from issuing a result. Existing general custody controls are reused.

The six optional live controls cover one exact original positive/reuse/changed
input request and one original semantic failure/no-reuse request per profile.
Receiving still owes independent source review, those actual original-command
controls, and qualification through the public entry on the final composed
engine. This source increment does not discharge them.

Original 48 requirements, 20 cases and 117 nodes remain the authoritative
populations. The eight retained raw comparison failures remain unchanged.
Native issuer/host/Windows/interlock obligations, natural recursion and combined
package acceptance remain separate. The approved 458,752-byte combined package
cap and 2,000-byte reserve are unchanged; this repository-only increment does not
relax either or claim whole 117-node acceptance.
