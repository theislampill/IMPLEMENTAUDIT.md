# DG17 M03 — independent prospective source and operation review

## Disposition

**GAP_REVISE — original-family eligibility is unestablished, and there are three concrete preexecution defects. Do not execute this frozen candidate.**

The prospective component family covers two omitted check calls with real processes, canonical replacement, fixed byte expectations, paired inputs, and unfamiliar held-outs. Its selected source is a new opt-in feature over exact51416. It is not evidence that unchanged51416 passes M03, and it cannot replace the retained historical survivor. Its genuine behavioral discrimination does not establish that these optional calls are the original L3 Smoke A/B edges. The family eligibility gap and three concrete defects are independently material.

This is an ordinary independent advisory review by `/root/independent_review`, with authority **NONE**. It is not formal internal route activation, source selection, execution admission, an award, or closure. Root retains those decisions. No candidate code, product module, product validator, original, mutant, oracle, Git command, provider operation, or controller operation was executed by this review. No candidate or frozen input was edited.

Review currentness was rebound by Root after the context boundary to controller `dg16-dg18-recovery-20261119-b`, generation **G0045**, receipt `da78b456997516f38e8e8b048c221bec6e4c0c4b`, verified native `3a414d/0`, require-current native `7b3a11/0`. The packet's G0044 binding remains its historical authoring binding; this review does not rewrite it.

## Exact receiving and scope

| Item | Independently received identity |
|---|---|
| Packet | `/workspace/scratch/097486cde2dd/dg17-after-m09-next` |
| Seal | 61,699 bytes; SHA-256 `e07021288d1afdbd2ade7583f7fb154ae5d41e325e48a9646c5d58dd963d6a38` |
| Payload | 261 regular files, 3,851,470 bytes; two explicitly typed symlink refusal probes |
| Base commit | `51416b2f156b341c4a5f09029e2c6ceb5b30b1e7` |
| Base tree | `9c3913ceaa95f3f36b0377fe2dba4a302afcba89` |
| Proposed tree | `e15ee980fcec18875482ad5639f7b4a5dbc76531` |
| Delta | Seven files: three modifications and four additions; no deletion |
| Original execution | `execution-01` absent; no original or mutant operation received |
| Independent receiving | Data-only `receive_static.py`, native **33eaa2/0**, recorded in `MECHANICAL_RECEIVING.json` |

The receiver checked every declared regular file's bytes, hash, and permission mode; the exact two symlink targets without following them; and the complete payload inventory. It reconstructed the base Git tree and all 457 recorded subtrees from the 1,785 authenticated leaf identities using Git object serialization in memory. It checked all 27 complete inherited file bodies against their authenticated blob identities, sizes, and modes, then derived the proposed tree from the seven exact changes. No Git process or Git object/ref write was used.

The full supplied `SOURCE.patch` was applied as text data to the frozen base bodies and yielded each exact candidate body. The canonical mutation Python remains identical. For precision, the author's 114,332-byte suffix includes the final `PY\n` heredoc delimiter; its SHA-256 is `68858ff60076dc81db58ae9230fdf115b9eb76bd8429695b6253001ce27264c5`. The actual embedded Python body excluding that delimiter is 114,329 bytes, SHA-256 `c7ab6d73b7f84ae48c0c91c0fc91c97a9d60f2b18e4273b23af1bb65f213632d`, identical in base and candidate. This distinction does not change source identity or the findings.

The review read the design, review packet, source closure, readiness, source delta and patch, complete new adapter, runner, oracle and receiver, complete support test, frozen case matrix and mutations, original Issue211 clauses, applicable owner clauses, and selected canonical call/dependency paths. Existing complete canonical source previously independently reviewed remains bound here by exact full-file hashes; it was not replaced with extracted authority functions.

## Findings requiring a new immutable revision

### E1 — HIGH, original-family eligibility: an authorized new optional component is not yet bound to the unchanged original M03 obligations

**Original owners:** `evidence/ORIGINAL_ISSUE211.md`, lines 331–337, 603 and 636–656; `base/skills/implementaudit/templates/PROTOCOL.md`, Step 5 and Step 10.

**Proposed mapping:** `DESIGN.md`, lines 7–23 and 47–55; `REVIEW_PACKET.md`, lines 7–26; `candidate/skills/implementaudit/templates/PROTOCOL.md`, lines 218–231; `inputs/MUTATIONS.json`; `evidence/SELECTION_CENSUS.json`.

**Adjudication of ordinary engineering:** Root states that the user permits a supported product adapter as ordinary engineering. The implementation is concretely a general contract-driven replacement/check route through the existing mutation CLI, with actual source integration, a public optional reference, and canonical registry wiring. Those facts support treating it as legitimate prospective component engineering, rather than misdescribing it as a mock or string checker. No additional user permission is requested for that already-authorized engineering.

**Adjudication of original acceptance:** that authorization does not by itself establish that this component satisfies the unchanged original M03. The sole mutations remove `baseline_gate()` or `postcheck_gate()` in a newly added optional adapter. The original PROTOCOL Step 5 baseline and Step 10 comparison obligations remain intact in both variants. The added paragraph expressly makes the adapter optional and says it does not replace the remaining phase steps. The frozen execution drives this component directly; the constructed claim/phase authority establishes permission to replace the selected file, but does not demonstrate a selected actual L3 phase whose original Smoke A/B obligations are those omitted calls. Thus a variant can skip an optional duplicate check without, on the supplied mapping alone, removing the original governor's Smoke obligation. The prior census specifically retained the missing actual governor edge/captured-phase boundary; a new label cannot close it.

**F2/F3/F4:** Issue211 F2 prohibits a new R0037 runtime owner merely to give the tests a target. F3/F4 require exact native owner RED before a runtime repair. The unsupported-flag baseline demonstrates absence of a new option, not failure of the original L3 baseline/comparison requirement. The packet correctly disclaims that RED, and supplies no other exact RED. Consequently this source addition must not be promoted into an F3/F4-qualified R0037 runtime repair, nor may its component witness be counted as original M03 merely because the new component has independently omittable calls. The component can be authorized and useful while that acceptance proof remains absent.

**Required resolution before any original admission:** supply a concrete, independently reviewable mapping from the unchanged original M03 predicate to the actual selected L3 operation and canonical owner. It must show why the two omitted calls constitute the original before/after obligations, preserve baseline evidence and actual after comparison, and explain how the selected source's provenance/change classification complies with F2/F3/F4 without treating feature absence as RED. A declaration in a new design document or a Root gate reference alone is not evidence of this mapping. If the mapping cannot be established without waiving those original clauses, retain this as separately qualified component engineering and leave M03 unaccepted. No new original invocation, expected-outcome change, or historical replay is a remedy for this eligibility gap.

### H1 — HIGH: effectful group signals can occur after the group leader has been reaped

**Owner:** `candidate/skills/implementaudit/scripts/verified-mutation-step.py`, `run_process`, lines 151–160, 175–185, 205–218, and 224–235.

The runner uses `Popen.poll()` at lines 175, 183 and 205, each of which can reap an exited direct child. It explicitly waits/reaps at line 208. Afterward, lines 212–218 treat failure to observe group absence as a reason to send SIGTERM/SIGKILL to the numeric `process.pid`. The `OSError` handler can also unconditionally send SIGKILL after a prior reap.

After reaping, the original leader's PID no longer reserves that numeric identity. A presence probe cannot establish that a later group using that number belongs to this operation. The code can therefore signal a group without retained ownership. Its `start_new_session=True`, observed PGID, successful simple timeout control, and later refusal do not repair that ownership loss.

**Required correction:** retain a race-safe ownership capability through every effectful cleanup signal and close that signaling boundary before reaping. Cover normal, timeout, overflow and exceptional paths. Alternatively, refuse without signaling once ownership has been lost, while explicitly preserving unresolved cleanup evidence. A later read-only `killpg(pgid, 0)` presence observation may remain, but must not authorize effectful signaling or identify the remaining members. A separately frozen correction and focused ordinary process controls are appropriate; no M03 witness is needed to demonstrate this source defect.

### H2 — HIGH: the outer witness timeout can kill the cleanup owner while an inner stage remains in another session

**Owners:** `run_m03.py`, lines 75–107 and 182–183; `candidate/skills/implementaudit/scripts/verified-mutation-step.py`, lines 162–164, 387–420 and 434–442.

The outer harness starts the adapter in one session and imposes a **55-second timeout on the complete operation**. On timeout it sends signals only to that outer group. Each adapter stage starts another new session. The adapter permits preflight and canonical apply **45 seconds each**, plus two **5-second** checks for these frozen cases, before capture/cleanup overhead. Thus the valid aggregate stage budget already exceeds the outer deadline. The outer timer can expire during a bounded inner canonical apply, kill the adapter that owns its cleanup, and leave that independently grouped stage outside the signaled group. There is no cooperative signal cleanup or retained outer ownership of those inner children in this revision.

This is a concrete ordinary timeout/abort mismatch, not a demand for hostile-process sandboxing or native-host SIGKILL guarantees. Labeling outer captures as direct-child-only correctly limits the evidence claim, but does not make the admitted operation's abort behavior safe. An outer STOP and a closed adapter capture do not prove that inner effects have stopped.

**Required correction:** make the complete operation deadline and ownership/abort contract coherent. Retain a safe way to terminate and reap inner stages on outer timeout, unexpected adapter exit, and the exceptional paths the revised runner claims to handle. A larger outer deadline alone does not handle a hung or unexpectedly terminated cleanup owner. Keep unresolved containment a refusal and preserve actual stage evidence. Qualify the correction using isolated process fixtures, including an independently sessioned inner child and an interrupted/failed owner, without executing canonical preflight/apply or the frozen M03 family. Any added platform requirement must be explicit and fail closed when unavailable.

### H3 — HIGH: every frozen phase violates the actual selected authority parser's ordering requirement

**Inputs:** `inputs/phases/c01.md` through `c08.md`, line 30; corresponding generation in `prepare_inputs.py`.

**Unchanged consumer:** `candidate/skills/implementaudit/scripts/validate-phase.sh`, line 95, reached by `apply-observed-mutation.sh` lines 552–556.

Every phase currently carries:

```json
{"out":["notes/unfinished-draft.txt","checks/inspect_result.py","checks/examples.json"]}
```

The actual `--mutation-authority` path requires the `in` and `out` lists to be unique **and sorted by UTF-8 bytes**. This `out` list is unsorted. The data-only receiver independently evaluated that literal ordering predicate for all eight phases; all eight fail it. The existing full consumer calls this authority path before Smoke A. The resulting preflight would refuse `PHASE_AUTHORITY_REFUSED`, so even c01 cannot reach its expected successful baseline/mutation/postcheck path. c08 would also fail for the wrong reason before its intended `PREIMAGE_DRIFT` witness.

The eight retained normal phase-shape passes are authentic but do not exercise this selected authority guard. Their success cannot be promoted to semantic authority readiness. No actual preflight or original was run to discover the defect.

**Required correction:** serialize the existing `out` members as `checks/examples.json`, `checks/inspect_result.py`, `notes/unfinished-draft.txt` in the generator and all eight prospective phase inputs. Preserve membership, scope, requests, preimages, candidate bytes, checks, and every expected outcome. Record the structural serialization correction as a distinct immutable revision; do not alter this packet or reinterpret the retained shape qualification. The exact native predicate can be checked as data before any original admission.

## Original-family mapping and component evidence assessment

Original Issue211 line 603 independently removes or inverts **L3 Smoke A or Smoke B**. Lines 331–337 require baseline preservation, after comparison, and regression classification; lines 541–545 bound structural/identity/authority evidence; lines 616–619 reject vocabulary-only discriminators and require unfamiliar held-outs. The packet implements two separate sole omitted calls in the full integrated adapter, not two labels for the same mutation. That establishes predicate-specific component discrimination, subject to H1–H3, but does not resolve E1's original-edge and source-change-provenance gap.

The operation is designed to perform an actual pinned observational command before mutation, preserve its complete process evidence and explicit baseline policy, invoke the complete maintained canonical replacement consumer, and repeat the same command against actual landed bytes. A failed baseline blocks replacement; a failed post-check retains the replacement and refuses verified completion. The fixed external oracle compares expected numerical behavior, actual exits, stage order and byte state. That is a meaningful bounded before/after discriminator for this binary check/repair contract. It does not implement or prove general diagnostic differencing for arbitrary preexisting multi-failure suites, model judgment, L4 interruption, an entire L3 phase, or the other original families. Those broader limits cannot be used to omit the original M03 mapping itself.

| Case | Fixed original expectation | Purpose / paired omission |
|---|---|---|
| c01 | Real 0→0 checks; exact improved implementation lands; verified | Positive nontrivial replacement |
| c02 | Unexpected baseline exit 1; target remains old; no mutation/postcheck | Baseline omission must instead land the exact candidate and incorrectly verify |
| c03 | Baseline 0; exact bad candidate lands; postcheck 1; refusal | Postcheck omission must incorrectly verify the same bad candidate |
| c04 | c02 boundary with opaque path/name and different numeric transform | Independent unfamiliar baseline held-out |
| c05 | c03 boundary with opaque path/name and different numeric transform | Independent unfamiliar postcheck held-out |
| c06 | Explicit known baseline exit 1 and explanation; repaired result 0; verified | Preservation/classification of admitted preexisting failure |
| c07 | Identical preimage/candidate; actual canonical `NO_CHANGE`; 0→0 checks | No-change boundary, not a fake mutation |
| c08 | Exact canonical `PREIMAGE_DRIFT`; no checks or mutation | Specificity control for both omissions |

Eight originals precede all seven variant operations. The variant population is fixed at three baseline-omission cases and four postcheck-omission cases: **four decisive effects and three specificity controls**. Each mutant differs from the original adapter only by replacing its one gate call with `pass`. Every other package file, case request, preimage, candidate, checker, and oracle remains fixed. The receiver verified both exact sole-call transformations and their hashes.

The simple arithmetic is useful because it gives an external literal oracle: correct square outputs are `[9,0,25]`, the bad `value+1` outputs are `[-2,1,6]`; the held-out correct transform produces `[-4,2,23]`, while the bad transform produces `[-3,3,24]`. A future independent receiver must check those actual observations and same-input pairings; a captured JSON field saying “failures” is not sufficient by itself. In omission variants, the omitted process does not run: its paired original supplies the actual failing baseline or after-check evidence. No process result may be invented for the omitted stage.

The candidate adds a real opt-in CLI route, documented from the canonical PROTOCOL and accompanied by a registered support test. It does not declare a new governor, default lifecycle, or model-facing authority. Default CLI execution retains the unchanged embedded mutation body. The opt-in mechanism is a useful support operation for an already-authorized replacement; it is broader than a checker that searches for requirement wording. Whether treating its new sequencing owner as the original R0037 M03 owner is permissible remains E1, not a fact established by this useful integration. The no-change case is not a substitute for the separate cheap-path family; cheap/default preservation here is limited to the unchanged default dispatch and explicit opt-in boundary.

Issue211 F2–F4, lines 636–656, still prohibit manufacturing runtime RED from an absent checker or adding a runtime owner solely to give a test a target. The retained unsupported-flag baseline establishes a missing **new feature**, not a previously demonstrated defect in unchanged51416. The author states this distinction accurately, but the distinction alone cannot discharge those original gates. E1 must be resolved with evidence before Root source selection or an operation gate could support original M03 admission. The historical survivor and denominator remain intact. Root additionally reports that the live Issue211 body matches this frozen body byte-for-byte, SHA-256 `ca62f4899a45544549f623a0312c16121bb99f432ccb87a87b7361974ceb94c4` (native `2662ae/0`); no issue rewrite supplies an exception.

## Actual CLI, source closure, authority and immutable inputs

The seven changes are the new adapter and reference, the three-line opt-in dispatch in the actual `apply-observed-mutation.sh`, the PROTOCOL reference, and the focused support test plus registry wiring. The exact tree derivation proves no additional source changes.

The actual adapter calls `--batch-preflight` and `--batch-apply` on the full canonical CLI. The latter captures the full maintained embedded Python body and invokes its canonical single-row consumer through the existing restricted transport. It verifies the real row disposition and return identities. No authority function is replaced with a fixture and no saved transaction result substitutes for current execution. The adapter also checks the actual landed bytes against the captured candidate.

The selected source closure contains complete `validate-run-root.sh`, `validate-phase.sh`, `claim-run.sh`, `read-canonical-pair.py`, and the reader's unconditional `canonical_custody.py` dependency, plus the relevant authorization, evidence and closure helpers and templates. The reader source load is not omitted on the theory that POSIX makes it irrelevant. Protected rotation/controller and full-root lifecycle branches are outside this ordinary selected path; their unselected companion requirements are not silently treated as qualified.

The fixture design uses a fresh isolated Git repository, exact detached base and tree verification, no controller/receipt refs, one actual ordinary claim, fixed phase bindings, fixed complete replacement inputs, and a snapshot reused byte-for-byte across each pair. The runner verifies restored work-plane and run-input manifests before invocation. The real selected setup pattern is **seven Git commands plus one ordinary claim**, not the nine-Git pattern from the earlier M09 family. Existing setup evidence confirms those eight steps succeeded before the separately retained normal-shape failure.

The adapter enforces unique-key strict integer JSON, ordinary run path and controller absence, single replacement, explicit baseline policy, bounded immutable check-input population, regular-file/non-symlink capture, physical/byte rechecks, exact fresh evidence directory, and source population/hash rechecks around stages. It delegates actual authority and preimage revalidation to the canonical consumer. Inputs are trusted owner-selected commands; dependencies beyond the declared interpreter/checker/data are not magically sandboxed or inferred. The prospective witness uses only the frozen standard-library checker and numeric data. No arbitrary private input or network transport is introduced by that checker.

The ordinary executable hashes in `evidence/TOOLCHAIN.json` still match the current files by read-only byte checks. That is not a fresh execution, OS/library/environment qualification, or host-model identity claim. Historical fixture inodes and process IDs remain historical observations, not current ownership proofs.

## Oracle and independent receiving feasibility

`oracle.py` accepts the case and actual observation, not a variant or mutation name. It checks the entire recorded work-plane file/symlink population and permission/byte identities, exact expected target bytes, unchanged bystanders, real stage order, complete stream files, actual exits, process receipt agreement, captured contract, baseline policy, actual canonical return envelopes, source/preimage/candidate/post identities, and explicit no-authority/no-closure flags. The omission counterexamples require the precise candidate state and false verified completion; a generic failure or changed file does not count.

The runner preserves each observed subject before restoring a paired fixture, including the full claimed run and its transaction/evidence directories. Thus independent receiving can examine actual canonical durable results, transaction effects, claim/phase bindings, process files and exact bytes without rerunning the product. All originals must be received before variant acceptance; provisional driver/oracle labels cannot award the family.

The supplied convenience oracle is not an independent review. It does not itself fully rederive each numeric actual from source, enumerate empty-directory changes, validate every durable transaction publication effect, or separately check every outer stream metadata field. For this family, exact target/bystander file state and the two actual checks are the discriminators; inherited transaction correctness is not being re-awarded. These limits do not require changing the frozen acceptance expectations, because the retained raw evidence permits the independent receiver to verify the decisive numeric values, exact native exits, contract/phase/checker bytes, complete ordered transaction effects and durable result agreement. That receiving must actually occur before Root adjudication. H1–H3 prevent reaching that stage in this revision.

On a future admitted operation, check at minimum: complete payload inventory; exact source/sole mutants; eight original passages before any variant; identical same-case claim, phase, checker/data and before-state across pairs; real check argv and literal numeric observations; each required stop's absence of later stages; exact target and all bystander bytes/modes; canonical raw exit/envelope and saved transaction agreement; and truthful process termination/capture predicates. Do not infer absent processes from driver success or equate a retained numeric PID with a live owned process.

## Existing qualification, limits and required subsequent gates

The receiver checked **25 retained raw process captures** and both stream hashes/lengths in each: four process controls in support-03, four in support-final, nine setup/normal-shape captures, and eight corrected normal-shape captures. The final support record has 15 passing controls, including actual CLI help/intake refusal, full module load, duplicate JSON, regular/symlink/drift custody, normal/nonzero/timeout/overflow subprocesses, baseline policy, and an existing-evidence refusal with no launched child or changed prior evidence.

These are meaningful ordinary controls. They do not cover post-reap group reuse, outer-owner termination while a new-session inner stage runs, or the semantic authority parser's sorted-scope guard. No original, mutant, canonical batch preflight/apply, or mutation-authority invocation appears in these selected captures. The received setup subject and snapshot retain the original c01 target and no mutation transaction or verified-step-current result. The exclusive original directory is absent.

The earlier setup failure `ddcd6d/1` remains authentic: the first eight steps succeeded, then the normal phase validator rejected generic STOP wording. The later eight shape passes are retained separately. The concrete STOP correction did not change `inputs/cases.json` or expected outcomes. H3 is another semantic preexecution input problem, not permission to reinterpret that earlier failure or tune original outcomes.

| Gate | Status and required interpretation |
|---|---|
| Exact source/packet intake | Passed as data; current candidate still has H1–H3 |
| Focused ordinary support | Retained 15 passes; correction requires targeted new ownership/abort controls |
| Normal phase shape | Eight retained passes; semantic authority ordering currently fails H3 |
| Complete original and mutants | Unexecuted; E1 must first establish original-family eligibility, then corrected immutable packet, fresh independent review and Root admission |
| Source candidate selection | Root decision still required; selected new tree must not be described as unchanged51416 |
| Package/runtime validation map | Triggered and unrun: focused gate then exact applicable bootstrap, registry and `scripts/verify-package.sh` gates from base `AGENTS.md` lines 123–151 |
| Build/budget/archive parity | Triggered by packaged source changes; exact-source generated population, version, inventory, compressed budget and both projections remain open |
| Isolated install / host activation / malformed population / rollback | Triggered for package qualification under Issue211 F6, lines 658–668; unrun and unqualified |
| Whole DG17 / host / case / terminal closure | Not supplied by this prospective mechanical family |

A separately admitted source component development operation need not claim an already-qualified shipping pipeline. That does not admit it as original M03: E1 remains independently blocking. Nor does it waive the triggered package/install/host gates, which must be handled for integration/package readiness and any corresponding award. A source publication that merely makes a candidate reviewable must preserve the unqualified status; publication cannot be used as package, installed-payload or host activation proof. Root alone owns whether and when such a publication is authorized.

Resource limits are finite per input and per captured stream, with 45-second canonical stages and 1–30-second configured checks, fresh evidence, no automatic replay/compensation, and retained failures. They are not aggregate OS memory/process/disk quotas or protection against hostile checks and escaped sessions. H2 is within the narrower promised ordinary bound and must be fixed. Raw external SIGKILL/native-host failure remains outside a generic local helper's cleanup guarantee; missing completion evidence must remain unresolved.

## Return to Root

Preserve this packet and all existing evidence. Resolve E1's original-family eligibility before treating any component execution as an original. A coherent R2 may correct H1, H2 and H3 as authorized ordinary engineering, preserving all case requests, byte inputs, scope membership and expected outcomes. Receive its exact delta and focused support evidence independently. These repairs alone do not resolve E1. No original replay is needed or authorized by this report.

The complete original-definition mapping, canonical integration, fixed oracle structure and raw evidence design have been reviewed. E1 and H1–H3 are the material findings; no additional material gap was identified within this selected ordinary scope. This statement does not qualify an unseen correction. Overall disposition remains **GAP_REVISE**.
