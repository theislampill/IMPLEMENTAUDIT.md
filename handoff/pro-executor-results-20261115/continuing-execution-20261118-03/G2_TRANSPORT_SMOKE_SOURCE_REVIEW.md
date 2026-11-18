# FINAL — Independent ordinary engineering review of the G2 transport smoke

**Reviewer:** `/root/g2_smoke_cold_review`  
**Authority:** `NONE`  
**Decision:** **PASS for the two exact source files and their declared transport-only scope, with the runtime GAPs below.**  
**Blocking source findings:** none identified.  
**Review date:** 2026-11-18.

This is an ordinary engineering cold review. It is not a formal audit assessment, acceptance decision, readiness record, publication authorization, or new G2 control. No controller was invented, resumed, or invalidated. Root alone owns integration and any subsequent publication. No network request, hosted operation, branch creation, push, workflow invocation, full pair, original consumption, or candidate modification was performed during this review.

## Exact reviewed objects

| Object | SHA-256 |
| --- | --- |
| `g2-hosted-smoke-candidate/qualification/dg16-r5-full-g2/transport_smoke.py` | `baa97ec17871541cafdbf7a0f118d45c3704bf5a9389cc4c86c508dea192471b` |
| `g2-hosted-smoke-candidate/.github/workflows/g2-production-transport-smoke.yml` | `7beac6d601cff224540f64b71c72d722cd3ff73e4765fedcec24c85d6966de23` |
| Actual dependency: `g2-repair-repo/qualification/dg16-r5-full-g2/live_control.py` | `cd8262defc85c2541632fe00e51bc78c804b13a3a8a4501e39300b4269f866ff` |
| Actual dependency: `g2-repair-repo/qualification/dg16-r5-full-g2/host_utility.py` | `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5` |
| Author test source: `g2-hosted-smoke-candidate/local_tests/test_transport_smoke.py` | `311bacc5cc1206744fd0d441b2f191e924b95e0c2c8e4fe17714b1fcca00890d` |
| Author handoff: `g2-hosted-smoke-candidate/AUTHORING_HANDOFF.md` | `99e2a6e19607b39612da83530751e1d7a7d193b0c50d338ed554e7b2a8f06ca0` |
| Author plan: `g2-hosted-smoke-candidate/AUTHORING_PLAN.md` | `880d776a1cd1981c6396b3ee04bcf7ff37b7555dec79f45eecd437030c6887f0` |

All paths in this table are under `/workspace/scratch/2678f1e431c3`. The two publishable file hashes and both dependency hashes match the commissioning values. This review does not extend to different bytes or a changed integration parent. The candidate directory is an authoring packet, not a Git repository; base workflow inspection was performed against the actual Git object in `g2-repair-repo`.

## PASS findings

### The transport boundary is exact and fails closed

The actual repaired `hold` runs through `CaptureGate`, which allows only three argv vectors, in order:

1. `/usr/bin/git init --bare --quiet` for the new output work directory's `control.git` cache.
2. `/usr/bin/git -c protocol.https.allow=always ls-remote --exit-code --refs` for `https://github.com/theislampill/IMPLEMENTAUDIT.md.git` and `refs/heads/pro/dg16-g2-reviewed-control-20261118-01`.
3. The production fetch command for that cache and public repository, with `--quiet --no-tags --depth=2`, ending in the exact commit `0fc8b8a0343925e72b24f4f98daad8ba988bd045`.

The discovery output must equal that commit, a tab, the complete fixed ref, and a single newline. A changed SHA, malformed line, additional line, missing ref, nonzero exit, altered command, changed record list, oversized stream, or failed cleanup refuses the observation. The synthetic missing-ref check confirms that the smoke refuses instead of reaching `hold`'s normal polling path. There is no automatic retry in this smoke.

Every allowed capture delegates to the exact pinned production `utility.capture` without altering its environment or execution behavior. The unchanged utility supplies a closed environment, bounded captured streams, pidfd acquisition, a dedicated process session, child custody checks, and an ECHILD cleanup requirement. The smoke enables and reads back the Linux subreaper setting before launching captures, matching the production caller's precondition. The main script uses a 180-second alarm and monotonic deadline; individual capture requests are restricted to at most 20 seconds. The workflow additionally limits the smoke step to four minutes and the job to five minutes.

### Success stops before the acceptance path

After the real utility returns successful fetch and cleanup, the gate raises its private `FetchComplete` exception. It never returns fetch success to `hold`. Thus the next parent-reading `cat-file` command, tree/payload inspection, validator, final control reread, consumption reservation, and decision-file materialization are not reached.

The independent controlled-success check runs the actual repaired `hold`, confirms exactly three capture calls, verifies that the validator was never called, and checks the exact attempted-operation list. A subsequent parent command is rejected by the gate. `hold`'s normal `finally` can write its private `CONTROL_READS.json`, which is not an uploaded artifact. Fetching the allowed public commit necessarily transfers Git objects; the claim is that no parent-validation or payload-reading command executes after fetch, not that the received Git pack lacks parent objects.

The request is a synthetic non-acceptance marker with only the repository, control branch, marker run ID, and marker control path. It contains no original request, proof, reviewer decision, expiry, or original consumption binding. No original request, independent-review record, or Root-consumption record was loaded or created by this review. Negative tests use temporary synthetic fixtures only.

### The output is bounded and has no award authority

The script publishes bounded metadata and digests from production capture records, not raw stdout/stderr, argv arrays, credentials, environment contents, or the private Git cache. Failure codes are restricted to known values; an independent private-sentinel exception test confirms unknown exception text is not serialized into the result.

The script checks absence of `CONSUMPTION_RESERVED.json`, `CONTROL.json`, `INDEPENDENT_REVIEW.json`, and `ROOT_CONSUMPTION.json` using `lexists`, including dangling paths. Any presence forces refusal. All original acceptance, full G2, G132, full-pair execution, replay, original consumption, branch-writing, and retry fields are false.

The workflow uploads exactly `RESULT.json`, with a 65,536-byte validation cap. Its always-run evidence step creates a refusal record when ordinary earlier-step failure leaves no result. I executed the exact evidence block locally for a missing result, existing refusal, synthetic success, and a forbidden true award. The true award is rejected before public output. The source-generated result population remains trusted through the pinned script and dependencies; this is not a general-purpose sanitizer for arbitrary externally supplied JSON.

### Workflow guards preserve the narrow launch context

The only trigger is push to `engineering/g2-production-transport-smoke-20261118-01`, restricted by the three declared changed-file paths. The only job additionally requires the exact repository, push event, exact ref, newly created branch, non-deletion, non-force, all-zero before SHA, and run attempt 1.

Before the script runs, the workflow requires the checked-out HEAD to have the sole parent `9a349423b6ca3dda18115a07ed41b63970bc8b77` and verifies the script's exact hash. The script independently checks the declared hosted context and dependency hashes before transport. Workflow permissions are only `contents: read`. Checkout uses the event SHA, does not persist credentials, and disables submodules, LFS, and safe-directory mutation. Production Git subprocesses receive the fixed closed environment rather than inherited runner credentials.

Both action commits exactly match the pinned actions in the inspected base workflow:

| Action | Commit |
| --- | --- |
| `actions/checkout` | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/upload-artifact` | `ea165f8d65b6e75b540449e92b4886f43607fa02` |

This verifies exact pin equality against the base object. It does not independently establish remote availability or behavior of those action commits.

### Base push triggers do not match the smoke branch

I enumerated all workflows at the fixed base Git object and inspected their trigger definitions:

| Base workflow | Push branches | Other event types | Result for smoke branch creation |
| --- | --- | --- | --- |
| `dg16-r5-full-g2.yml` | `pro/dg16-g2-reviewed-20261118-01` | none | Does not match |
| `pages.yml` | `main` | `workflow_dispatch` | Does not match |
| `validate.yml` | `main` | `pull_request` | Does not match a branch push alone |

The corresponding base file hashes are recorded in `workflow_results.json`. This noninterference conclusion requires integration to preserve those three files and not create a PR or manually dispatch another workflow. The proposed smoke adds no dispatch or PR trigger and invokes no original pair adapter.

## Local verification actually observed

| Verification | Result | Evidence |
| --- | --- | --- |
| Author's seven tests, rerun from exact test source | PASS: 7 tests, 0 failures/errors | `author_suite.log` |
| Independent boundary/refusal and two supported real-capture checks | PASS: 14 tests; 2 additional tests skipped for the documented executor gap | `independent_suite.log`, `behavior_results.json` |
| Offline YAML, shell syntax, workflow guards, pins, base trigger checks, and exact evidence-block cases | PASS: 30 checks | `workflow_results.json` |
| Real production capture through gate for local bare init | PASS: zero exit, complete streams, pidfd acquired, cleanup ECHILD | Assertion source and passing test in `checks/independent_checks.py` / `independent_suite.log` |
| Real production capture of a local environment-inspection child | PASS: child environment equals the exact closed production environment; synthetic inherited private variable is absent | Same independent check source and log |

The author test module's temporary-directory root was relocated only in memory to this review directory. Its candidate source and test file were not changed. All independent test artifacts are under this review directory. No loopback or external network test was run.

Commands executed for final test evidence:

```bash
timeout 30s /usr/bin/python3 -I -S -B /workspace/scratch/2678f1e431c3/g2-smoke-cold-review/checks/independent_checks.py
timeout 30s python -B /workspace/scratch/2678f1e431c3/g2-smoke-cold-review/checks/workflow_checks.py
```

Both commands exited 0. The first explicitly reports the two skips; its success flag must not be read as successful execution of those skipped cases.

## GAPs and limits

1. **Hosted transport remains unobserved.** This review cannot establish action availability, GitHub event delivery, `ubuntu-26.04` behavior, runner networking, DNS/TLS, advertisement of the fixed head, or successful HTTPS fetch. A successful future smoke would establish the narrow transport observation only. No hosted success or original award is claimed here.

2. **The local executor lacks the production procfs child-census interface.** An initial extended test attempted an adopted orphan and a timeout cleanup. The unchanged production utility correctly refused `CHILD_CLEANUP_UNCERTAIN` when `/proc/self/task/<pid>/children` was unavailable. A direct read-only reproduction confirmed that `/proc/self` and the task PID agree, but the `children` file is absent. This does not demonstrate a PID mismatch or a smoke-source defect. That initial run recorded 1 failure and 6 errors, including teardown errors; it is preserved in `initial_independent_suite.log`, `initial_behavior_results.json`, and `checks/initial_independent_checks.py`. The final suite explicitly skips the two cases needing that interface, while retaining genuine ECHILD checks for completed local children. No production fallback or environment workaround was introduced. Hosted live-child cleanup is still a runtime GAP.

3. **Currentness ends at discovery.** The script checks the fixed advertised head before fetch and deliberately performs no post-fetch ref reread. It does not establish that the branch stayed unchanged or that any original review or private-input window remains live.

4. **One branch creation is an integration obligation.** The source guards prevent ordinary updates and reruns from executing the job, but they do not prevent a person from deleting and recreating the same branch for a new run ID. Root must keep the operation to the commissioned single fresh creation and attempt 1. This review is not authority for another creation.

5. **Hard runner loss or whole-job cancellation can prevent evidence retention.** The fallback covers ordinary missing-result failures, not guaranteed artifact upload after runner disappearance or exhaustion of the job limit.

6. **Integration is not yet reviewed as an actual commit.** The publication commit must be a sole child of the fixed parent, carry these exact script/workflow bytes and actual pinned dependencies, and preserve existing workflow and acceptance pins. The current review does not authorize repointing acceptance manifests or replaying expired control. Root must verify the concrete integration delta.

## Final bounded conclusion

**PASS:** The exact two proposed files implement a meaningful, read-only production transport smoke with a hard command boundary before parent validation or payload consumption. No blocking source finding was identified in this scope.

**GAP:** Hosted execution and the missing local live-child census remain unobserved. No full G2, G132, original acceptance, original consumption, or replay is established or awarded. The review and its checks are complete; root alone may integrate or publish within the existing commissioning constraints.
