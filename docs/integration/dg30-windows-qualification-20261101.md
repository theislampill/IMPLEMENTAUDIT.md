# DG30: prospective Windows full-operation qualification

This is a repo-only, one-shot operation packet for the existing original
R0039 generation-v1 / original fourteen-field receipt-v3 resume path. It is
qualification preparation, not a native PASS, H0/OR/C02 grant, or issue #215
acceptance. The entitled Windows executor and independent receiver must supply
the missing actual execution and authority evidence.

## Engineering and evidence boundary

The source base is `033b867b11173be6aacf99b1316dc242e2517f21`, tree
`7bafac8f64f49d6ce85dd4c052b246e65e66b689`. Commit
`e0dc32e112485279ff33ff74409abe88b66194a2` already supplies the prospective
Windows preparation policy. This change leaves every shipped runtime,
reference, template, package contract and original receipt unchanged.

The retained historical qualification builder's predicates accepted an
explicitly incomplete Job memory scope, zero kernel process counts, and an
unrelated successful command. Those are demonstrated qualification defects;
they do not invalidate an independently proved historical operation. The
replacement gate requires the exact intended command, actual pinned executable
observations inside the Job, complete process-event/kernel reconciliation,
positive finite measurements, terminal cleanup and exact accepting readbacks.

The following distinctions remain binding:

| Evidence | Scope |
|---|---|
| Historical five-second / 64-MiB Windows failure | Preserved FAIL. Retained draft/archive and unchanged pointer/marker remain evidence; do not retry, erase, amend or clean up that operation. |
| Historical Linux G0002 to G0003 recovery | Reuse the actual accepting readback at `221623b4836fc3c25ed897f0ad327ab8f0aa3e2f`. Preserve its original driver FAIL and the independent corrected interpretation. No replay is needed. |
| Portable fixtures here | Constructed source controls; no native operation, authentic occurrence, issuer or entitlement. |
| Windows Job measurement | Whole owner command and actual Job descendants; 60,000 ms and 201,326,592 bytes peak aggregate Job committed memory, zero baseline subtraction. Harness excluded. Required executable identity is observed; notification loss refuses. |
| Receipt and projection checks | Recorded original fourteen-field successor, separate currentness/readback, permanent marker, protected payload and retained predecessor evidence consistency. These checks cannot authenticate an external host or grant. |
| Whole issue acceptance | All original fourteen criteria, criterion-5 amendment, authentic producer/observation, cold receiving, C02, applicable source/package/native evidence and dependency satisfaction remain mandatory. |

The separate 64-MiB helper guard is unchanged. The 180-second diagnostic
containment timeout is not a passing time budget: a returned 60,001-ms
operation fails qualification. An existing external broker, lost Job message,
absent required executable observation, incomplete containment or missing
readback cannot be excused by acceptable numeric values.

## Files and execution model

* `scripts/r0039-windows-job.py`: native recorder. It creates the root
  suspended, assigns a private Job with no breakaway permission, then resumes
  it once. It records process notifications, kernel totals, actual executable
  identity/membership and peak aggregate committed memory. The timer starts
  before root creation and ends only after root exit and an empty Job.
* `scripts/check-r0039-windows-resume.py`: portable fail-closed consistency
  checks. It uses explicit exceptions, including under optimized Python.
* `scripts/run-r0039-windows-resume.py`: exact-source read-only preparation,
  native launch-chain/memory control, one owner operation and post-operation
  readbacks. It never creates a controller, invalidation, occurrence, grant,
  C02 event, fixture, recovery, cleanup or automatic retry.

Job completion notifications are not guaranteed by Windows. Their complete
lifetime sequence must reconcile to independent kernel process totals; sampled
images alone do not establish a census. Native execution must determine
whether the actual host delivers the required evidence. See Microsoft's
[completion-port contract](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port),
[Job accounting](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information)
and [extended limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information).

## Required inputs from the entitled executor

1. A clean checkout of the independently reviewed DG30 source commit/tree,
   with all three scripts present. Bind the actual published commit and tree
   from the accompanying handoff. Do not substitute the current moving PR255
   branch or a file copied from another source.
2. The actual separately entitled governed subject and controller, already
   migrated and invalidated by its existing owner. Its copied scripts and
   templates must byte-match this source. The pending invalidation must be
   authentic at its declared scope. This tool cannot produce it.
3. An unused next projection generation, epoch, archive ref, publication ref
   and receipt ref. A retained failed-operation draft is not unused. The old
   Windows failed subject must remain protected. If no suitable subject exists,
   return `BLOCKED_FRESH_ENTITLED_SUBJECT_UNAVAILABLE`; do not make a fixture
   and promote it to an original occurrence.
4. Exact physical executables: Git Bash, a real Python executable with the
   required runtime support, and `C:\Program Files\Git\mingw64\bin\git.exe`.
   No WindowsApps alias, symlink or reparse ancestor is admitted. Launch the
   runner through that same selected Python. Existing owner selection remains
   unchanged.
5. A new evidence directory outside both checkouts, plus the actual issuer,
   entitlement and host/session evidence reference. The driver records that
   reference; it does not authenticate it. The entitled executor must hold
   sole operation custody through prepare, execute and receiving. Concurrent
   selected-controller mutation stops the operation; unrelated controller
   state is outside this packet.

## Windows commands

Use PowerShell on the entitled Windows host. Assign the real paths, exact
reviewed identity, controller and entitlement reference before execution;
the placeholders are not defaults or authority. No install or source update
is performed by these commands.

```powershell
$dg30Python = 'C:\actual\physical\python.exe'
$dg30Bash = 'C:\Program Files\Git\usr\bin\bash.exe'
$dg30Git = 'C:\Program Files\Git\mingw64\bin\git.exe'
$dg30Source = 'C:\actual\clean-dg30-source'
$dg30Subject = 'C:\actual\entitled-governed-subject'
$dg30Out = 'C:\actual\new-dg30-evidence-directory'
$dg30Controller = 'ACTUAL_EXISTING_CONTROLLER'
$dg30Head = 'EXACT_PUBLISHED_40_HEX_COMMIT_FROM_HANDOFF'
$dg30Tree = 'EXACT_PUBLISHED_40_HEX_TREE_FROM_HANDOFF'
$dg30Entitlement = 'ACTUAL_ISSUER_AND_BOUND_OPERATION_ENTITLEMENT_REFERENCE'

& $dg30Python -B "$dg30Source\scripts\run-r0039-windows-resume.py" prepare `
  --source $dg30Source --repo $dg30Subject --controller $dg30Controller `
  --source-head $dg30Head --source-tree $dg30Tree `
  --bash $dg30Bash --python $dg30Python --git $dg30Git --out $dg30Out
if ($LASTEXITCODE -ne 0) { throw 'Preparation refused; preserve its evidence.' }

$dg30Plan = "$dg30Out\OPERATION.json"
$dg30PlanHash = (Get-FileHash -Algorithm SHA256 $dg30Plan).Hash.ToLowerInvariant()
```

Before any owner operation, run the three disposable kernel controls with the
selected physical Python and fixed Git. All three must execute successfully
with zero skips. The wrapper below treats a skip as refusal, preserves the
output outside the governed subject, and refuses to overwrite an earlier
control result. It grants no owner operation:

```powershell
$dg30ControlLog = "$dg30Out\NATIVE_KERNEL_CONTROLS.log"
if (Test-Path -LiteralPath $dg30ControlLog) { throw 'Control result already exists; preserve it.' }
$dg30ControlProgram = @'
import importlib.util, json, sys, unittest
spec = importlib.util.spec_from_file_location('dg30_native_controls', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromName('WindowsKernelIntegration', module)
result = unittest.TextTestRunner(verbosity=2).run(suite)
ok = result.wasSuccessful() and result.testsRun == 3 and not result.skipped
print(json.dumps({'all_three_executed_and_passed': ok, 'tests_run': result.testsRun,
                  'skipped': len(result.skipped), 'authority': 'NO_OWNER_OPERATION_GRANT'}))
raise SystemExit(0 if ok else 1)
'@
$dg30PreviousOptIn = $env:IMPLEMENTAUDIT_WINDOWS_JOB_CONTROLS
try {
  $env:IMPLEMENTAUDIT_WINDOWS_JOB_CONTROLS = '1'
  & $dg30Python -I -B -c $dg30ControlProgram "$dg30Source\fixtures\canonical-state-rotation\windows_job_test.py" 2>&1 | Tee-Object -FilePath $dg30ControlLog
  if ($LASTEXITCODE -ne 0) { throw 'Native recorder controls failed or skipped; stop before owner launch.' }
} finally {
  $env:IMPLEMENTAUDIT_WINDOWS_JOB_CONTROLS = $dg30PreviousOptIn
}
```

The executor and independent receiver inspect `OPERATION.json`, its exact
preimage/command/tool hashes and the separate STATE then ROADMAP readbacks.
Confirm the actual grant covers this exact subject, boundary and one-shot
operation, including the measurement controls. Independently confirm the
recorded three-control success with zero skips. Preparation is read-only with
respect to the governed subject and grants nothing. Only after those gates,
execute once:

```powershell
& $dg30Python -B "$dg30Source\scripts\run-r0039-windows-resume.py" execute `
  --plan $dg30Plan --plan-sha256 $dg30PlanHash `
  --entitlement-reference $dg30Entitlement
if ($LASTEXITCODE -ne 0) {
  throw 'Attempt unqualified. Preserve all output and obtain independent readback; do not retry.'
}
```

The exclusive `execution` directory is the durable one-shot attempt boundary.
Both preparation and execution reject parent traversal and symlink/reparse
paths before output; physical path normalization precedes ancestry comparison.
The native control proves actual Bash/Python/child/Git Job membership and an
aggregate allocation greater than the peak single-process allocation before
the owner command is attempted. Controls are diagnostic and not an owner
effect. A second exact preflight follows them. `LAUNCH_INTENT.json` is written
before the sole measured resume invocation. After any ambiguous launch, retain
the entire directory and actual subject; do not remove the boundary or rename
the plan to repeat the effect.

## Required return and independent receiving

Return the complete evidence directory, a size/SHA-256 manifest, the exact
source commit/tree and tool/runtime identities, host/session/issuer/entitlement
proof, and the actual protected subject evidence through its existing custody
route. Keep sensitive physical bindings in their authorized channel. Include:

* `OPERATION.json`, both original preparation readbacks and the returned plan
  hash; the successful, unskipped `NATIVE_KERNEL_CONTROLS.log`; `ATTEMPT.json`,
  both execution preflights and `LAUNCH_INTENT.json` when present.
* Entire native-control and operation subdirectories: raw stdout/stderr,
  `measurement.json`, raw process events, executable observations, accounting,
  incomplete/error/containment details and aggregate-memory control result.
* `MEASUREMENT.json`, `RECEIPT.raw`, `CURRENT.json`, separate receipt verification
  and currentness outputs, separate current STATE/ROADMAP outputs,
  `PRESERVED_AFTER.json`, plus `RESULT.json` or `FAILURE.json` exactly as produced.
* Independently acquired current pointer/ref/blob, receipt, permanent marker,
  archive and predecessor/retired-pair readbacks from the actual subject, and
  the full protected pending/occurrence population needed by original R0039.

The driver checks the accepting original14 transition only after a successful
owner return. A failed measurement or nonzero/malformed owner return is an
unqualified potentially changed effect. If process containment is uncertain,
the existing host owner first establishes terminal containment; no new owner
operation is permitted. The independent receiver then uses the existing
read-only resolve/read/verify commands against the actual subject to determine
what happened. An absent file stays absent; never construct a successful
return from expected values. The protected old failure is never a replay target.

A success-shaped `RESULT.json` means only
`RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING`. Independent receiving
must recheck the actual host, authority, process completeness, exact sources,
original failure preservation, functional/security criteria, and every amended
protected-state/occurrence obligation. It cannot be promoted automatically to
`DG30 ACCEPTED`, a Windows native PASS, C02 publication or issue closure.

## Focused source verification and rollback

```bash
python -B fixtures/canonical-state-rotation/windows_job_test.py
python -B fixtures/canonical-state-rotation/windows_qualification_test.py
bash scripts/check-canonical-state-rotation.sh
bash scripts/check-validation-registry.sh
git diff --check
```

On this Linux engineering host the three opt-in Windows integration controls
are explicitly skipped. The mandatory unskipped controls in the Windows
sequence above cover parent/child allocation and membership, actual fixed
Git, and timeout containment/no replay. Their result remains separate from
the actual governed resume. Protected payload and retained-evidence comparison
uses canonical JSON, so integer/boolean/float substitutions cannot count as
preservation.

Rollback removes this repo-only qualification commit, its focused fixtures,
wrapper registrations and this document. It changes no shipped package bytes,
historical evidence, accepted Linux recovery, source preparation policy or
protected native effect. Astra may selectively integrate the independently
qualified commit through the sole PR255 publisher. This branch grants no
adoption or root DAG acceptance authority.

## Original acceptance still required

The full original fourteen criteria and criterion-5 pending/compaction amendment
remain controlling. Receive authentic H0/OR producer inputs and entitlements,
original/current/prior/retry identities, both actual compaction coverage cases
with uncovered successors, independent cold receiving, and the authenticated
C02 erroneous-event/issuer/later-boundary census and append-only publication.
The prior evidence inventory and original failures must remain visible.

Final DG30 acceptance also consumes DG18's complete original R0039 acceptance,
DG21's applicable `ISSUE_RECEIPT[R0039]`, and DG22's actual approved adoption and
issue-slice readback. Those owners retain their work. Certificate preparation
does not require unrelated sibling closure, and none of these dependencies
prevents independent engineering here. The sole PR255 publisher receives the
exact reviewed commit/tree, RED/GREEN evidence, affected consumers and rollback.
