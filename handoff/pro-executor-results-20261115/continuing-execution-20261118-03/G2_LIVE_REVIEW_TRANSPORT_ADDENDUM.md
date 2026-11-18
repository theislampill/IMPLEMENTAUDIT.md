Written UTC: 2026-11-18T07:52:53.036507+00:00

# Independent addendum: live control transport blocker

- **report_state: FINAL_ADDENDUM**
- **reviewer: /root/g2_live_independent_20261118**
- **authority: NONE**
- **finding: G2-LIVE-TRANSPORT-01**
- **finding_disposition: BLOCKING_DOWNSTREAM_CONSUMPTION_AND_REQUIRED_CLOSING**
- **original_proof_assessment: not falsified by this finding; original PASS remains bounded to its historical live-proof review scope and its unsatisfied closing condition.**
- **hosted_terminal_outcome: not yet observed.**

This separately dated addendum supplements the frozen report and review for run 44239735578, attempt 1, workflow commit `9a349423b6ca3dda18115a07ed41b63970bc8b77`. It changes no frozen decision bytes, source, control record or live state. Read the original report together with this addendum for any lifecycle determination.

## Confirmed source defect and independent reproduction

The exact selected `host_utility.py`, SHA256 `02a15dc96ecce23e14a3a84bca880aa536d79fffc4f6d6160835cb4ba97a19b5`, defines `safe_environment()` at lines 588–594 with `GIT_CONFIG_COUNT=3` and `protocol.allow=never`. Its `capture()` function passes that environment to `subprocess.Popen` at lines 693–697. Once capture/custody checks succeed, it returns the command's actual nonzero exit and captured streams at lines 739–754.

The exact selected `live_control.py`, SHA256 `05918b2d5c2f791a92c52fd72cf795a870f24ddedc1c6867fbbf358218cb400a`, calls that capture function at lines 98–107 for HTTPS `git ls-remote`, with no selected per-protocol override. Line 103 treats both exit 2 and exit 128 as `None` when `missing=True`. Thus the observed transport-denial exit is silently interpreted by `head()` as no branch. No commit reaches the payload validation or reservation path. The subsequent HTTPS fetch at line 121 also uses the same restricted command wrapper, so branch visibility alone is not a complete transport qualification.

I independently verified the source hash and reproduced the exact `ls-remote` argv under the actual selected `safe_environment()` locally at **07:50:12 UTC**. I then independently invoked the exact `host_utility.capture()` function locally at **07:50:54 UTC**, in a dedicated reviewer process. Both calls returned:

- return code **128**;
- zero stdout bytes;
- 37 stderr bytes: `fatal: transport 'https' not allowed` followed by a newline.

The exact capture call also reported complete streams, successful pidfd acquisition, no timeout, no output overflow, no internal failure, and `cleanup.echild=true`. This confirms that the capture layer returns this negative result normally; the hold wrapper's missing-branch classification is reachable. I did not substitute a successful Git command, authorize a transport override, or run the actual live hold loop.

The Root-supplied diagnostic independently agrees. Its SHA256 is `99d3beeedccab44979c9518ef90f71d4845b7ac7cc456a0d786d1e9dbdbeb94d`, but the conclusion above is supported by my own source inspection and reproductions.

## Independently observed live state

At **07:51:10 UTC**, connected GitHub API readback showed:

- `refs/heads/pro/dg16-g2-reviewed-control-20261118-01` exists and points to commit **0fc8b8a0343925e72b24f4f98daad8ba988bd045**;
- job **134584393061** remains `in_progress`;
- step 21, awaiting independent review and separate Root consumption, remains `in_progress`;
- step 22, mandatory post-review original-custody/currentness readback, remains `pending`.

Root reports that the exact control was published and verified at 07:41:52 UTC. I independently verified current branch existence, not that historical publication timestamp or every property of the published control commit in this addendum.

I have **not** observed the hosted job's stderr or private `CONTROL_READS.json`. The precise explanation of this hosted stall is therefore a source-based causal inference strongly supported by the exact local reproduction and observed live state. It is not a quotation of hosted logs or a claim that the job has already reached a terminal failure.

## Impact on the original review

| Question | Assessment |
|---|---|
| Are the immutable proof or its equality results shown to be false? | **No.** This finding does not alter the reviewed packet, source identity, pre-hold raw receiving, projection comparisons, or proof/private descriptor bindings. |
| Was the actual independent review fabricated or made schema-invalid? | **No.** The original 856-byte reviewer-authored JSON remains authentic and unchanged. |
| Does a valid published control commit establish host consumption? | **No.** Publication and receiver acceptance are separate boundaries. A successful local formatter/validator cannot replace the live reservation. |
| Can the selected hold path reach genuine consumption with this defect? | **Blocked by the selected transport composition.** The current source turns the reproduced HTTPS denial into an absent branch observation. |
| Has the mandatory same-job closing condition been satisfied? | **No evidence of satisfaction.** Step 22 remains pending; no successful closing receipt is available to this reviewer. |
| Is full G2/M2, original acceptance or closure available from these facts? | **No.** The required downstream receiving and closing remain blocked/unproved. |

The earlier review's evidence-bound correspondence judgment was made before this new information and was explicitly subject to later same-job closing. The transport defect is downstream of proof creation and does not invalidate the actual comparison evidence. The overall episode cannot be treated as successfully consumed or closed merely because that proof review passed.

My earlier source review inspected the control validator and closing requirements but did not join the hold command's call site to the utility's Git transport environment. That operational integration assessment was incomplete. This addendum records the missed composition defect directly; it must not be concealed behind the narrower proof scope or read as an unchanged endorsement of end-to-end operation.

## Required downstream disposition

The new blocker is at **LIVE_CONTROL_TRANSPORT_RECEIVING**, with the consequent **MANDATORY_SAME_JOB_CLOSING** condition unsatisfied. The request's fixed expiry remains **07:59:42 UTC**, epoch **1794988782**. This addendum neither extends it nor creates a replacement request.

Source-based prediction, not yet a hosted result: if the current hold continues receiving this error until its deadline, `live_control.py:164` raises `ACTUAL_REVIEW_WINDOW_EXPIRED` without a consumption reservation. `run.py:966–979` then cannot record successful consumption or append a successful hold step. Finalization requires all steps completed and no prior failure before the mandatory post-review driver recheck (`run.py:1095–1107`); an ordinary finalization attempt after timeout cannot by itself satisfy that condition. The genuine terminal result and final public evidence must determine the recorded run outcome.

Root's stated containment—preserving the immutable published control and waiting for the authentic terminal run—is consistent with this finding. I performed no live configuration changes, alternate control, branch rewrite, deadline extension, source modification, relaunch or acceptance award. No replacement PASS or Root record is authored by this addendum.

## Evidence and frozen objects

Independent evidence:

- `evidence/TRANSPORT-REPRODUCTION-20261118T0750Z.json`, SHA256 `26e3516a5b68d0d26255261df14770c7fe6498aed4d8471cb2d5ca9f832ca237`.
- `evidence/TRANSPORT-CAPTURE-20261118T0751Z.json`, SHA256 `16223bf9314613e28232487d3bc92b5a1248e2374ab1124c68b22fb3c28b99c7`.
- `evidence/TRANSPORT-LIVE-READBACK-20261118T0751Z.json`, containing the exact connected branch/job readback and observation time.

The original files were rehashed before this addendum and remain:

- `REPORT.md`: 19,166 bytes; SHA256 `6d1f644f611c887e67fb3d21dfffdc93fb30c201ec8a7bc7caed0ae27e37a970`.
- `INDEPENDENT_REVIEW.json`: 856 bytes; SHA256 `58970a2f210907e6207fbefdcc10e3a0a1775c45398ce4eabe77a015d4918b1d`.
