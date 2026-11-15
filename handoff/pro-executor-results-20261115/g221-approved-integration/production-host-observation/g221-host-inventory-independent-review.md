# Independent G221 host-observer source review

Report state: FINAL

Authority: NONE. This is ordinary independent source/code review of a prelaunch observation. It supplies no mutation, publication, protected launch, native operation, acceptance, merge, release, closure, or production-readiness authority.

## Reviewer attestation

- Reviewer identity: `/root/g221_host_inventory_review`.
- Requested model: GPT-6 Astra Pro.
- Actual model: GPT-6 Astra Pro, as identified by the host/developer context available to this reviewer. No separate runtime model attestation is exposed.
- Inheritance: dispatched child context; no model override was selected by this reviewer. The parent's fork/model parameters are not independently visible here and are not asserted.
- Authoring context reuse: no. No source-author conversation or authoring history was supplied or consulted. This reviewer did not author the implementation and is distinct from the prior contract inspector.
- Other-reviewer visibility: no prior reviewer report was opened. The delegation identifies a prior contract inspector, and the assigned resource descriptor contains a one-line statement that its source read returned GO. That statement was visible and was not used as evidence for this review's conclusions.
- Review method: independent read-only source inspection, AST inspection without importing or executing owner code, exact-byte/hash/Git-object comparison, and receiving of the already preserved local evidence. No audit-assess route or child agent was used.

## Immutable scope and source identity

| Item | Exact identity |
|---|---|
| Worktree | `/workspace/scratch/0269e6626329/g221-host-inventory` |
| Repository | `theislampill/IMPLEMENTAUDIT.md` |
| Engineering branch | `engineering/pro-executor-g221-host-inventory-20261115` |
| Base commit and candidate parent | `060902121a45b180853e630891caa5e6c9d2f704` |
| Base tree | `f74f43a029cca69dc28af9096e983c9e275f3436` |
| Candidate commit | `cd1a84fbcb39650864c4b8460309025424e2d565` |
| Candidate tree | `3531df3b34d5008f78030b0e40308d3da48ad8bf` |
| Review packet SHA-256 | `6ad430da0bc86d44cef0da9d63e6667427041538e7c5776efa1f695b6af8c4b9` |
| Commission read | `e4cba42cb5704f00b78d64e43f5da88501c28229:handoff/dg16-dg18-findings-20261115/PRO_UNIFIED_COMMISSION.md` |

The candidate has exactly 21 additions: the four implementation/test/documentation/workflow files below and 17 source-evidence files, including the review packet and its sidecar. No existing source is modified. The worktree was clean under `git --no-optional-locks status --porcelain=v1 --untracked-files=all`. Candidate parent, HEAD, and tree matched the assignment.

The owner commission permits ordinary source engineering, guarded engineering publication, and independent receiving while preserving the separate G221/G132 protected gates. The immediate requirement is the full actual host tuple before a fresh recipient/protected launch, independently of M5. `handoff/dg16-g221-root-execution-inputs/RUNBOOK.md:53-54,246-253` supplies the original image/applicability requirement. This review does not reinterpret that observation as a fresh protected episode or as its currentness.

### New source bytes inspected

| Path | Bytes | SHA-256 |
|---|---:|---|
| `.github/workflows/dg16-g221-host-inventory.yml` | 4591 | `b699872594d1b39e0e64b7428fd365dde28a55058d39064d0b951cdfba297c41` |
| `qualification/dg16-g221-host-inventory/README.md` | 5030 | `a26c9e21ae01d8b2bd030d710d80f130b61c82f76c395e6dce8865976296f0d6` |
| `qualification/dg16-g221-host-inventory/observe.py` | 10601 | `4fe38252e3499d812bdb6cbf9201a37b04e34aa3f3e125a2db1efe14435f01dd` |
| `qualification/dg16-g221-host-inventory/test_observe.py` | 7402 | `d0eb3282b6b679ffc7a5755eac73af4b468eaeddf65f8037addc679028227cee` |

### Unchanged executable closure inspected

All paths in this table are under `qualification/dg16-r5-full-g2/`.

| Member | Bytes | SHA-256 |
|---|---:|---|
| `run.py` | 86060 | `688166071f33d2cb33c48a4136a88b7dccf719267e9fa43db72cffb361fdbd74` |
| `host_utility.py` | 65235 | `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5` |
| `evidence_io.py` | 6321 | `c2f8d718c8acd3a223d494239e6bc19d4a90e3d5c66f49cdac8f701ce4807075` |
| `native_profile.py` | 5615 | `c16c75039b938718ab4bfee9e49a6c55322bdfda22f25d0a526cf74f87944c3d` |
| `native_admission.py` | 5403 | `d96262b67a18f62a7fe07264a3b5a08b5a8016a237d9b46ca7c781e234421342` |
| `current_host.py` | 15173 | `893ad0f5c8b59d7bff47985cfe94ef8d76d5b1cbb76f4076c1efdf86fe10d3fc` |
| `native_prerequisite.py` | 27362 | `594ac753bbfda9cfa3285a7c5a31018fd5384bb3d3f0afcd89bc29cea7749f42` |
| `native_integration.py` | 25584 | `c6f2b17e59369a04db2062b79ea2150c54d978fd1c0f18a9b25e094e303bc266` |

I independently compared all four new sources, all eight unchanged owner modules, and all 15 packet-listed evidence members against their packet byte counts, SHA-256 values, Git blob identities, and physical modes. Every comparison matched. Every member also matched its candidate Git object; all eight owner modules matched their base Git objects. The packet's separately supplied SHA-256 and its sidecar matched. The seven internal loader pins in `run.py` matched the wrapper's eight-member closure and packet pins; the workflow's held-observer pin matched the observer bytes.

## Findings and checked predicates

No concrete defect requiring revision was found in the assigned source-only scope.

### 1. The executed bytes are bound and closed

The workflow hashes the exact observer bytes and compiles that held byte string (`.github/workflows/dg16-g221-host-inventory.yml:43-52,77-79`). The observer requires isolated, no-site, no-bytecode Python; checks its held bootstrap bytes; reads the workflow and all eight owner modules; and verifies all owner hashes before owner-module execution (`observe.py:139-163`). Its file reader checks ordinary single-link file shape, a 256 KiB bound, no-follow opening, and stable file-descriptor/path metadata (`observe.py:60-75`).

`run.py:80-85` compiles the same utility byte string it hashes. `run.py:100-123` hashes each native module's held compile bytes and performs closing reads. `observe.py:182-192` re-reads every held source member after observation; a closing failure keeps or creates a refusal and clears successful status. Source descriptors identify the bytes actually held. The workflow's own provider commit remains an independently receivable identity rather than self-authentication by these environment fields.

### 2. The actual transitive path is read-only host observation

The only direct owner entry calls are `load_utility`, `load_native`, `inventory`, `current_host.target_host`, and `evidence_io.encode` (`observe.py:163-176`). I inspected all eight module initializers, imports, class/function definition-time expressions, loader bodies, and the actual inventory/tuple callees. Owner-module imports are standard-library imports; the only non-guarded top-level calls are inert `dict` and `Path` construction. The `run.py` and utility CLI guards are false under the assigned module names.

`run.py:705-724` reads platform/OS facts, descriptors for bwrap/bash/Python/git, interpreter identity, image environment facts, a boot-ID hash, and the real/effective/saved numeric UID/GID tuple. Its second `load_native(u)` call is the same pinned inert module construction. `native_profile.py:19-29,33-59` supplies and validates those actual credentials and host/tool fields. `host_utility.py:406-440` reads tool bytes, executable/custody metadata, and file-capability metadata; it never executes bwrap. No credential store or private key is read.

The original episode calls inventory before provisioning (`run.py:1094-1105`, with provisioning at `run.py:840-845`). The wrapper does not call that episode's `execute`, `operation`, CLI, `observe_host`, request/admission machinery, protected preflight, banks, native tests, or provisioning. Loading `native_integration` does not call its `request_admission` (`native_integration.py:29-33`). The supplementary audit filter at `observe.py:99-107,132-136,160-183` denies selected mutation/process/network events while owner code is active. It is accurately documented as a narrow additional check, not a general sandbox (`README.md:25-27`).

### 3. The complete selected tuple and first refusal remain truthful

`current_host.py:32-42` includes the original host fields, all tool descriptors including bwrap, image identifiers, UID, and credentials. Its `target_host` invokes the unchanged full host validator. `observe.py:171-177` compares that result to the unchanged original `SELECTED_HOSTS` using unchanged `evidence_io.encode` (`evidence_io.py:19-20`), matching the original tuple comparison at `current_host.py:70-71`. It neither fabricates an episode nor invokes `validate_request`.

Inventory data is assigned to the result only after the original inventory returns (`observe.py:168-169`). An earlier refusal therefore leaves host, tool paths, selected tuple, and selected match null. A complete mismatch retains the actual tuple with a false match and the original selected-tuple refusal. Local mode cannot report hosted success (`observe.py:177-181,222`). Closing-source failures cannot retain successful status.

Every result begins with authority NONE, observation-only scope, and false same-job earned qualification, currentness, future G221 acceptance, and effect-grant fields (`observe.py:121-128`). A genuine hosted match records only `SELECTED_TUPLE_MATCH_OBSERVED`; no Root adoption, grant, request, recipient, or currentness record is created.

### 4. Public retention is bounded and byte-consistent

The provider allowlist contains only repository, ref, SHA, run ID, attempt, and event; invalid values become null (`observe.py:30-36,82-96`). Inventory adds only the original bounded public ImageOS/ImageVersion tokens and host facts. There is no general environment dump or token/key lookup. Exceptions with arbitrary message/path text are replaced with a fixed refusal code (`observe.py:110-115`). The bootstrap refusal has the same limited provider-key population (`workflow:53-76`).

The observer serializes canonical ASCII JSON with a final LF, limits it to 64 KiB, and puts the exact same bytes in the base64 log line and artifact body with a SHA-256 sidecar (`observe.py:50-52,196-208`). It writes into a fresh output directory with exclusive files and readback. Artifact upload runs after failure as well and selects only the two observation files (`workflow:82-93`). Bootstrap pin failure emits an explicit refusal schema and exits nonzero. Missing checkout/output or runner loss cannot be read as a successful observation; log/retention failures remain run-level evidence limitations (`README.md:59-71`).

I independently decoded the preserved local log line, required the canonical bytes, checked its digest, and compared the decoded bytes to `local-observation/OBSERVATION.json` and its sidecar. All were identical. The exact observation is 3478 bytes with SHA-256 `7fc049c6ddb45be36fdeaaf17b62eafb1d40c4ace41e4d80e9e08f21ff3e46f1`.

### 5. Publication is confined to the ordinary observation workflow

The workflow is bound to the exact engineering branch, expected repository, a created/nondeleted branch push, and attempt 1 (`workflow:3-21`). It has only `contents: read`, a five-minute job limit, an exact event-SHA checkout, no persisted checkout credentials, no submodules or LFS, and one observation invocation (`workflow:8-9,22-43`). Its checkout and upload action pins match the original G2 workflow: `11d5960a326750d5838078e36cf38b85af677262` and `ea165f8d65b6e75b540449e92b4886f43607fa02`.

There is no workflow-dispatch trigger, source publication step, additional source checkout, permission elevation, installation, protected/native invocation, or acceptance-writing step. I also enumerated the four tracked workflows and read their trigger boundaries: Pages and validation pushes select `main`, and the existing G2 workflow selects its different exact protected branch. Creating the assigned engineering branch does not satisfy those push triggers. No claim is made about uninspected provider-side configuration or runtime success.

## Existing author executions received

These are the author's preserved executions, not tests performed by this reviewer:

- Nine new wrapper controls report `OK`; their command record reports exit 0. Their scope is the wrapper's pins, inert imports, direct owner calls, refusal/allowlist/effect-filter/error controls, and workflow pins/bootstrap syntax. Synthetic validator inputs are explicitly TEST_ONLY; no selected-host success is constructed (`test_observe.py:17-116`).
- The preserved workflow shell-syntax command reports exit 0 with empty stdout/stderr.
- The real local unhosted observation reports exit 1 at `INVENTORY / OS_IMAGE_REFUSED`, with null host/tool paths/selected tuple/match, successful source closing, and all authority/currentness flags false. The first failing owner predicate is `run.py:712`.
- The earlier discovery-path error and transport-check harness assertion remain preserved. The former was a nonexistent source-discovery path; the latter confused an expected no-index diff exit 1 with failure despite empty diagnostics. Neither is represented as hosted success or erased.

This reviewer ran no wrapper tests, accepted suites, owner observation, CI workflow, native/model operation, or provider action. Read-only verification commands used Git object/status/trigger inspection, Python AST/hash/encoding checks without executing owner modules, and file reads. One initial reviewer `rg` lookup used nonexistent runbook paths and returned exit 2; the correct runbook path was then read. This had no mutation or execution consequence.

## Declined judgments and disposition boundary

The review does not establish that a current GitHub runner matches either selected host, that the runner label/action services are available, that a real observation artifact has been produced, or that provider evidence has been authenticated. No remote query, artifact download, or CI execution occurred. The local OS refusal is not selected-host applicability evidence. No selected-host success was simulated or credited.

Any later real hosted result still requires independent provider/run/source reconciliation at its actual scope. A prelaunch observation cannot transfer same-job earned qualification or currentness to a later G221 job, satisfy M5, replace a fresh recipient or protected gates, or authorize native work, publication, original acceptance, merge, release, or closure. Those judgments are deliberately outside this source-only review.

No concrete unresolved source question remains. The immutable candidate is suitable for the requested observation-only engineering publication under the owner's existing authority, subject to Root's separate publication decision. This report itself authorizes no effect.

PASS
