# G132: actual R2 Engine loading and next ordinary hosted observation

**Result: the exact published R2 Engine loaded successfully in this local process.**
The setup admission path also loaded the same thirteen-member source map. This
is source-loading evidence only. No original session, provider acquisition,
private-input handoff, native admission, or original award occurred.

**The next ordinary hosted candidate is frozen for independent review, not
published or executed.** It fills the complete standalone source-observation
gap. It does not repeat the earlier host survey, launcher provisioning, or
absent-target containment diagnostics.

## Exact source received

| Field | Received identity |
|---|---|
| Commit | `f75533f95f0d099c87e7a04beb11b0a25628acdc` |
| Tree | `9b9c2b3f1453b83b87b628b665fceff492bf5b1e` |
| Sole parent | `e76a07b2bae7c945e5a9d529ed8cf9069f4c9064` |
| Tracked files | 1,768 |
| Tracked bytes | 167,143,205 |
| Source revision | `R5_HOSTED_UBUNTU24_GIT_08CA_SOURCE_20261121_V1` |
| Profile | `FIXED_GENUINE_C5_SHARED_IMAGE_R5_HOSTED_UBUNTU24_SINGLE_COPY_20261105_V1` |

`materialize.py` received an isolated checkout from the available immutable Git
objects. Every tracked byte length, Git blob, SHA-256, and executable mode was
checked. The original repository remained clean at
`6d9e145e2f2df5a0a8a150c85a4f3e2afd918d27`. The four-file R2 delta was received
as two modifications and two additions. No product repair was necessary for
actual Engine loading.

`EXACT_CHECKOUT_RECEIPT.json` records the complete file manifest and commands.
Its SHA-256 is
`7b506d526ebc4a87c7780bcd5b832bf33cb06058ba1c2d84e802e51f2e6b66c6`.

## Actual loading evidence

Command: `python -B probe_engine.py`.

Native return: **31969d / exit 0**. The process was PID 2, PPID 1,
UID/EUID/GID/EGID 1000, process start tick 84685, running Python 3.12.14.
These are the actual local process values; they do not supply hosted UID0
custody or a genuine nonroot sender for any original.

The probe performed the actual, unmodified calls:

```python
engine = loader._Engine(loader.R5_HOSTED_PROFILE,
                        source_revision=loader.R5_GIT_08CA_SOURCE_REVISION)
current = engine.load()
engine.check()
via_setup = setup.hosted_current_owner(ROOT)
via_setup.CHECK()
```

All thirteen captured members were retained with logical and physical paths,
byte lengths, SHA-256, Git blob identities, and actual file identity vectors.
The successor executor came from
`test-support/r5-hosted-git-08ca-source/work-graph-c5-executor.py` as intended.
The setup-returned source map equaled the directly loaded map. Import-only
audit guards observed no forbidden child/process/network/write event. No
`GenuineC5Session` was constructed.

`ENGINE_LOADING_RESULT.json` is 16,903 bytes, SHA-256
`6eacf51b6ec959c6bb295c9411e6c16db1e6f2e999b4c74485c782f8314d240b`.

## Complete Git storage remains a distinct gate

The checkout initially used a read-only Git object alternate. An attempted
standalone repack failed, **f3f20a / exit 128**, because reachable object
`e6c187f175cab7a2968845cda67bdb0751c07c10` was unavailable. A bounded
`rev-list --objects --missing=print --no-object-names <R2>` scan returned
13,961 rows, including **4,728 missing object references**. Individual
historical object recovery was stopped. No shallow boundary, graft, omission,
or pin change was introduced.

The exact source contracts require:

- `scripts/qualify-work-graph-prefix.py::validate_git_namespace` rejects
  `.git/shallow`, object alternates, worktree/shared storage, grafts,
  promisor files, and other unsupported Git state.
- `scripts/qualify-work-graph-c5-setup.py::prepare_hosted_source` requires a
  clean, nonshallow, standalone fresh public clone, full strict fsck, and no
  missing object rows.
- `scripts/work-graph-c5-inputs.py::complete_source` captures all actual
  source/Git/hidden bytes and empty directories without projection.
- The selected executor's `captured_source_identity` additionally requires
  the reviewed HEAD commit to exist as an actual loose object and verifies its
  complete Git object hash and declared tree.

One bounded actual local capture had already been issued when Root directed
that no expensive known-doomed recovery be pursued. It completed in about
1.16 seconds and was not repeated. It captured 1,790 files and 441 directories,
199,391,342 actual file bytes (including the isolated Git storage). The
unchanged producer contract passed. The unchanged Git namespace and loose
HEAD identity guards refused the actual checkout. This is useful refusal
evidence, not complete standalone source admission.

Native return: **08e580 / exit 2**. `LOCAL_CHECKOUT_OBSERVATION.json` is
406,510 bytes, SHA-256
`e2f3e5f3cd2bf47c47db1e1f1b823bfa8ccfa3ba598d15d2e7a86ef9f3eaef2b`.

## Proposed hosted observation

The three new files under `candidate/` are a separate ordinary diagnostic
workflow, observer, and exact thirteen-member Engine map. The publication
plan records their byte/hash/Git identities and expected prospective tree.
The proposed parent is the exact R2 commit; no existing product file changes.

The workflow is bound to
`pro/dg16-g132-engine-source-observe-20261121-01`, push attempt 1, Ubuntu 24.04,
and the previously observed image `20261116.133.1`. A changed image or old Git
body is refused rather than assigned the prospective identity. The observer
requires actual UID/GID zero and verifies the exact Git08ca byte length,
SHA-256 and mode. Diagnostic source checkout is separate from the single
designated fresh product checkout.

The existing `prepare_hosted_source` creates exactly one fresh complete
product checkout for R2. Its cleanup and command custody are unchanged. The
observer then loads the actual checkout's Engine, compares its full captured
map, captures the complete source, and applies the unchanged namespace,
producer, and loose-HEAD guards. It also records finite selected startup/NSS,
Git file/template and launcher observations, without acquiring or importing
the provider. Per-field mismatches remain explicit; an observed host input
record is not labeled a passed qualification.

The fixed existing observer limits remain 1.5 GiB address space, CPU 120
seconds, a 256 MiB file limit, 256 descriptors, and a 240-second whole
observation alarm. The inherited source limits remain 128 MiB per source
file, 256 MiB aggregate, 4,096 entries, and depth 40. Git children retain the
existing 60-second per-command and 4 MiB per-stream limits. The workflow has
an eight-minute job limit and retains complete or partial report, stderr,
actual native exit status, and their digest manifest.

There is no launcher or AppArmor provisioning, absent-target run, package
build, original session, private input, sender, Root route, G1/G3 path, or
original execution in this candidate. A native zero result would establish
the observer's source gates only; the report permanently declares overall
admission `UNQUALIFIED` and no native/original award.

## Local candidate verification

Seven focused controls cover exact context, changed image/ref/attempt,
nonroot refusal, old Git refusal, source identity/completeness, no-authority
output, and exact nonzero native-return sealing. The initial missing-owner
red was **00acac / exit 1**. The implemented controls passed at
**31c241 / exit 0** and in final validation **b9bd5e / exit 0**.

Final validation also parsed the workflow, checked every shell program with
`bash -n`, compiled both Python bodies, verified workflow-to-observer and
map bindings, and actually invoked the observer locally with an empty
selected environment. That real invocation returned exit 2 at the context
gate with actual UID1000 and zero Git children. No host execution was faked.

`DIAGNOSTIC_VALIDATION.json` is 4,285 bytes, SHA-256
`14b938300d2189b5792b63e886f209b9826bb788f5d0a81829af831e88054317`.
The broad package suite was not invoked because this work changes no
product source and the original execution boundary expressly excludes it.

## Disposition and Root next steps

1. **Done, bounded:** exact R2 tracked source receiving and actual local Engine
   loading through both entry points.
2. **Blocked locally:** standalone complete Git storage. Preserve the actual
   refusal and missing-object count; do not reconstruct thousands of history
   objects or weaken the source guard.
3. **Changed, unissued:** the new hosted observation candidate. Root should
   receive the sealed packet, commission independent review, verify the
   exact new branch/currentness/publication bounds, and publish only the
   three reviewed files if accepted. No publication or dispatch occurred here.
4. **Unverified:** actual hosted Engine/source result, full runtime/input
   qualification, active original composition, all eleven live private inputs,
   real Root custody, genuine sender, all remaining security/resource/timing
   conditions, and any fresh original grant. Earlier scoped evidence is not
   transferred to the new host or source.

Original01 remains spent; historical301 and the other explicitly excluded
queued/original identities were not replayed. This packet has no controller,
readiness, lifecycle, integration, release, or closure authority.

### Self-critique

The local complete-source failure is a real storage limitation, not a defect
in the R2 Engine. The hosted source acquisition can still expose a previously
unobserved full-history size, clone, or loose-HEAD problem; the workflow must
retain that failure instead of repairing source storage implicitly. The
selected host-data observation deliberately remains narrower than original
runtime qualification, and independent review remains outstanding.
