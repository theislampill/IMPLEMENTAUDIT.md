# FINAL — Independent G2 transport source repair review

**Disposition: PASS at the bounded source-repair scope.** No blocking defect was found in the exact candidate delta. This is preparation-only engineering evidence. Hosted completion, original acceptance, control consumption, full G2 qualification, release readiness, and audit closure receive no verdict.

## Identity, context, and authority

- Actual executing identity: `/root/g2_transport_repair_review`.
- Authority: `NONE`; root remains the integration writer and decision owner.
- I did not author the candidate or tests and made no repository edits. My task-visible context comprised the assignment, shared instructions, and evidence retrieved during this review. I used no nested agent.
- I independently inspected the bytes and diff and executed both candidate and unchanged-base focused tests. The assignment's prior GREEN/RED claims were not substituted for my executions.
- A formal `audit-assess` governor route envelope, immutable packet digest, and proved fresh-context independence contract were not supplied. This report is an ordinary independent engineering review, not a formal `audit-assess` disposition or an independent live acceptance record. Formal audit/acceptance disposition: `NONVERDICT`.

## Exact reviewed object

Repository: `/workspace/scratch/2678f1e431c3/g2-repair-repo`

Branch observed: `engineering/g2-control-transport-20261118`

Base HEAD observed: `9a349423b6ca3dda18115a07ed41b63970bc8b77`

| Member | SHA-256 |
| --- | --- |
| Candidate `qualification/dg16-r5-full-g2/live_control.py` | `cd8262defc85c2541632fe00e51bc78c804b13a3a8a4501e39300b4269f866ff` |
| New `qualification/dg16-r5-full-g2/test_live_control_transport.py` | `963b21c7527e3d163c327dc42c9af35b2f79ff3f5c15737703dac35cb4980e2f` |
| Base `live_control.py` | `05918b2d5c2f791a92c52fd72cf795a870f24ddedc1c6867fbbf358218cb400a` |
| Unchanged `qualification/dg16-r5-full-g2/host_utility.py` | `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5` |
| Unchanged `qualification/dg16-r5-full-g2/run.py` | `1b03430baef6ba14221f6f22050f1d681c3491ce887fccdf49d434dd45a5ac68` |

The initial and final status reads showed only modified `live_control.py` and untracked `test_live_control_transport.py`. The tracked diff is 9 insertions and 5 deletions; the staged diff is empty. All reviewed hashes were checked again after execution.

## Claim-level findings

### PASS — HTTPS permission is confined to the intended read commands

Evidence type: exact source diff and independent real-Git regression.

`live_control.py` lines 13–15 retain the fixed repository and HTTPS remote. Lines 109–110 add `-c protocol.https.allow=always` only to `ls-remote`; lines 124–125 add the same option only to `fetch`. Neither the request nor remote content supplies an alternate remote. Local commands continue without that override.

`host_utility.py` lines 588–594 retain the closed environment, `protocol.allow=never`, disabled hooks/fsmonitor, no terminal prompts, no replacement objects, and no lazy fetching. Lines 693–754 retain the same subprocess capture, deadline/output bounds, pidfd custody, and cleanup refusal behavior. The source repair does not modify that utility.

The independently executed tests exercise real `/usr/bin/git` through this exact production `capture`, using bound but non-listening loopback sockets. HTTPS discovery and fetch pass the protocol gate. File and ext discovery remain denied. The fetch test synthesizes only discovery output to reach the real fetch operation.

### PASS — Fatal discovery errors are no longer misclassified as missing refs

Evidence type: exact source diff and independent classification regression.

`live_control.py` lines 98–105 replace the Boolean missing flag with an operation-specific return-code tuple. Discovery accepts only exit 2 as absence at line 110; exit 128 now reaches `LIVE_CONTROL_GIT_REFUSED` at line 104. The previously permitted local missing-tree codes 2 and 128 remain explicitly listed at line 130. No new retry path is introduced.

### PASS — Acceptance and boundary logic are unchanged

Evidence type: exact source diff and test path inspection.

The payload validator at `live_control.py` lines 50–89, request/location and reservation guards at lines 92–96, parent/tree/delta/blob checks at lines 126–148, final remote reread and dual-clock checks at lines 149–156, exclusive reservation writes at lines 157–165, and bounded private logging at lines 169–172 have no behavioral change from this patch. Existing local missing-tree suppression is preserved, not newly introduced.

The focused tests terminate at transport observation or initial discovery classification. They do not reach payload validation or create a review, root decision, acceptance, or consumption reservation. The real capture still performs its normal child cleanup. No full verifier pair was executed.

### GAP — This remains an intentionally unintegrated preparation candidate

Evidence type: unchanged pin and loader inspection.

`run.py` line 33 still pins the base `live_control.py` digest `05918b2d5c2f791a92c52fd72cf795a870f24ddedc1c6867fbbf358218cb400a`. The loader at lines 93–97 rejects different adapter bytes with `BOUND_ADAPTER_MEMBER_CHANGED`. Therefore these candidate bytes are not a runnable original candidate under the current pins. This is an expected scope boundary, not a reason to repoint a pin during this review.

### GAP — Focused transport evidence does not establish hosted remote delivery

Evidence type: test fixture design.

The closed-loopback tests intentionally establish protocol-gate and error-classification behavior. They do not establish GitHub DNS, TLS/authentication, successful fetch, hosted network availability, original-run delivery, private-input liveness, or successful consumption. These claims remain outside this review. No test result is promoted to a full G2 or original-acceptance claim.

No exposed credential or instruction-injection attempt was observed in the reviewed material. This is not a repository-wide secret or injection audit.

## Independent execution evidence

1. Candidate command, repository working directory:

   `PYTHONDONTWRITEBYTECODE=1 python qualification/dg16-r5-full-g2/test_live_control_transport.py`

   Fresh result: exit 0; 5 tests run; 0 failures; 0 errors; `OK`; 0.167 seconds. Tool execution chunk: `8eca56`.

2. Unchanged-base RED check: loaded the identical test file, read base `live_control.py` via `git show 9a349423b6ca3dda18115a07ed41b63970bc8b77:qualification/dg16-r5-full-g2/live_control.py`, and compiled those exact bytes into an in-memory module used by the test loader. The production utility and tests remained unchanged. No source file was reverted or rewritten.

   Fresh result: 5 tests run; 3 expected failures; 0 errors; 0.101 seconds. The failures are HTTPS discovery denied, HTTPS fetch denied, and fatal discovery exit 128 retried as missing. Missing-ref polling and other-protocol denial pass. The wrapper exited 0 only after asserting exactly this RED outcome. Tool execution chunk: `60113c`.

3. Final source hash and worktree readback confirmed the same candidate/test hashes and the same two-file worktree scope. Tool execution chunk: `6883a9`.

## Final boundaries and handback

No commit, push, ref update, workflow invocation, full pair, original acceptance, or live-control change was performed. The report makes no assertion about the current status of run `44239735578`; its live deadline and immutable control commit were assignment context only and were not rechecked here.

**Source-repair disposition: PASS. Blocking source findings: none. Integration and hosted qualification: GAP / not established. Formal audit, acceptance, release, or closure authority: NONE.** Return to root for the next authorized decision.
