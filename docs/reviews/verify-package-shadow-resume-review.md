# Verify-Package Shadow/Resume Serial Review

## Disposition

```text
REVIEW_MODE=SERIAL_FRESH_CONTEXT_SELF_REVIEW
INDEPENDENT_AGENT_REVIEW=NOT_PERFORMED
INDEPENDENT_AGENT_REVIEW_BLOCKER=SIDE_CONVERSATION_POLICY_FORBIDS_SUBAGENTS
CRITICAL_OPEN_FINDINGS=0
IMPORTANT_OPEN_FINDINGS=0
AUTHORITATIVE_ADMISSION=NO
```

This review is not represented as independent. It re-read the approved design,
inspected the frozen-base diff, exercised focused negative controls, and
challenged dependency, environment, process, checkpoint, and authority
boundaries. A genuinely independent review remains a future admission gate.

## Findings corrected during review

### Critical: timeout killed only the direct process

The original `subprocess.run(timeout=...)` path could leave a reparented child
alive on Windows. A held-out child wrote its sentinel after the parent timeout.
The runner now creates a process group and kills the exact process tree before
collecting output. The negative control passes and a post-test process census
showed no descendant residue.

### Important: one live edge was pseudo-dependency

The initial registry treated generated-diagram parity as a result dependency of
rendered-diagram verification. Source inspection proved the rendered verifier
runs the parity check itself, so it can produce trustworthy evidence without
the separately scheduled PASS. The live graph now has zero hard result edges;
the synthetic B -> C fixture retains genuine blocking coverage.

### Important: canonical exported environment was lost

The approved composite executes in a child shell, so its
`PYTHONDONTWRITEBYTECODE=1` export did not propagate automatically to discrete
checks. The registry now digest-binds static canonical exports, validation
rejects drift, and every discrete process receives the bound environment.

### Important: progressive NOT_APPLICABLE was reported as PASS

The rendered-diagram progressive gate has an exact registry-declared
not-applicable output. A current-repository integration test now proves it is
reported as `SKIPPED_NOT_APPLICABLE`, not PASS.

### Important: reusable PASS lacked durable output evidence

Checkpoint JSON originally preserved status/fingerprints but not the stdout and
stderr bytes. Checkpoints now atomically persist digest-bound sidecars, reuse
returns those evidence paths, and missing/tampered sidecars force execution.

### Important: checkpoint applicability hardening

Review added collision rejection for filesystem-safe IDs, recursive directory
manifests, generated-artifact manifests, unreadable/symlink fail-closed policy,
stored PASS exit-code validation, corrupt/incomplete/tampered record controls,
and explicit `exact_declared_inputs` admission. The live registry enables zero
real checkpoints by default.

## Non-code admission gaps and residual risks

1. A complete live 105-node canonical-vs-shadow run was intentionally denied
   credit and stopped. Process census found an older stale side verifier plus
   active main-campaign checks sharing fixed `/tmp` resources. Continuing could
   interfere with HBASE and would not provide independent evidence.
2. Many canonical scripts invoke nested tools beyond the top-level Bash
   declaration. Exit 126/127 and declared missing tools are infrastructure
   errors, but every nested alternative tool contract is not yet modelled.
3. The live registry enables zero checkpoint contracts. Resume performance is
   proved on controlled contracts and a bounded two-check real subset only.
4. The shadow CLI currently models the canonical verifier's default invocation,
   not every release-identity argument mode.
5. Scheduling is deterministic and serial. Fixed temp names/resource fixtures
   preclude safe parallel execution without further resource isolation.
6. A host-created symlink end-to-end test was skipped because Windows denied
   symlink creation. The manifest-kind unit control proves symlinks are marked
   non-reusable; a privileged cross-platform run remains useful.
7. Checkpoints are integrity-checked local evidence, not signed custody or
   adversary-resistant attestations.

These gaps do not suppress the non-authoritative discovery use case under an
exclusive fixed-resource window. They do block authoritative use.
