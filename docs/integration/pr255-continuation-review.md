# Independent continuation review of PR255

**Disposition: GAP-REVISE, limited to one executable checker defect.** The approved prospective budget, preserved historical fixtures/profiles, and additive current-source selections are coherent. Correct F1 and qualify its narrow negative control before representing this candidate as reviewed for the next draft update. Draft publication remains distinct from full mainline, installation, native and original-issue acceptance.

This is ordinary independent source review, authority NONE. It is not native audit-assess admission and grants no merge, release, issue-closure, dependency-installation or protected-effect authority.

## Frozen subject and authority

- Candidate: `c2d0f353944883fad579885f67d033a17073dad4`, tree `b160b1994e0f45110a24fcb5ec7882d6908d6777`.
- Base: `5d90c706518cd08f13dfbb2024e806702cae85e9` on the same PR255 integration worktree.
- Reviewed the actual 15-file delta, applicable existing repository guidance, ANDON, corrected budget proposal, capacity decision review, and `package/budgets/pr255-v4-owner-approval.md`.
- The commission expressly records separate human approval of both 589824-byte caps with 2000-byte reserve, and only Ubuntu bubblewrap 0.9.0-1ubuntu0.3. The new approval record is checked for source/pin consistency, not treated as self-created authority.
- Entry HEAD/tree matched and the source worktree/index were clean. During report preparation the root began correcting F1 in the working tree. That successor delta is outside this c2 review; the reviewer changed no tracked source, index or HEAD.

## F1 — P2: logical statement boundaries are lost from the launcher fingerprint

At frozen `scripts/check-helper-reachability.sh:414`, the ignored token set contains `tokenize.NEWLINE`. This conflates different valid Python programs. In the reviewed selected launcher, change only:

```python
exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=sys.flags.optimize), module.__dict__)
```

to:

```python
exec
(compile(raw, str(path), "exec", dont_inherit=True, optimize=sys.flags.optimize), module.__dict__)
```

Both parse. The first executes the captured companion; the second evaluates a built-in name and a tuple and never calls exec. The frozen recognizer returns **True for both**. Independent AST inspection finds one exec call in the selected code and zero in the mutation. This is a concrete false positive in the helper-invocation gate, not a hypothetical cross-version concern. No companion or native operation was executed by the probe.

Evidence: `review-controls/newline-invocation-probe.json`. The probe isolated the exact recognizer from the frozen checker and supplied the selected companion bytes; it did not run a full package checker or modify the repository.

Minimal fix: retain logical NEWLINE tokens with normalized spelling while ignoring nonlogical NL/comments and retaining symbolic token names, indentation structure and the two separately validated identity literals. Add the no-exec mutation to the existing negative controls. The root was notified and has begun this correction; no post-correction success is claimed in this frozen report. The symbolic token-name change itself correctly addresses the numeric token-ID drift between Python versions, but cannot justify dropping statement boundaries.

## Independently checked source and capacity evidence

`review-controls/source-boundary-checks.json` records these direct read-only checks:

- Budget history revisions 1 and 2 are unchanged. Revision 3 exactly equals the prior live role budgets. The revision4 approval file hashes to `e4af32dc219e8c041d62170b960cdb465f0cdfebdb7e414d0f45b7726cc31488`, matching the contract and validator pins.
- Both roles accept 587824 usable bytes and reject 587825, 589824 and 589825 for the appropriate reserve/cap reasons. Under retained revision3, 456752 still passes, 456753/458752 fail reserve, and 458753/552490 fail cap. No historical failure is reclassified by the prospective approval.
- Both added historical fixtures exactly match their PR246 `cbb616cc7e0f9abafebe9bbdeee202ede7feb94e` source bytes. Registry SHA256 is `77f26397b276fa1b6e494558d1796cb4c43d14b1e1a6755e68f542cdc4c37698`; historical package owner SHA256 is `f3fa90f6c1e7b75527eddd988a6977f27db669bec337f65ff9c2b1ceae50621f`. Their uses are historical input/hash controls, not replacement current executables or receipts.
- Original prefix profile names, registry SHA and program-pin dictionaries remain equal to the base. The distinct composite profile binds current registry `65c7b6939c7bf9396f83cdad58c735cabbc7e28232ceff816e7a8909bf625878`, derives 119 nodes, retains the actual first23 source bytes and next-node boundary, and forbids historical receipt reuse. Its executable-pin delta is exactly the approved package owner `a516b2e43068b08af96415c9dd1ab4e659fe6a4c2e9b5f696b3359365ab5e203`. It does not admit arbitrary registries, substitute 119 for original117, or expand an original acceptance population.
- The pending harness adds one exact four-owner tuple and retains its existing profiles. It selects the explicit pre-selection refusal `NONPROTECTED_PROJECTION_PROFILE_REQUIRED`, not a successful native reservation or grant. Added negative controls alter or omit each owner identity separately. The retained run's 58 controls / 88 processes explicitly report source unchanged, native JOIN UNPROVED and authority NONE.
- Both existing build-v4-a archives have valid CRCs, use ZIP method8, and bind clean c2 / tree b160 in their inventories. Plugin: 552526 bytes, 75 members, SHA256 `cb00741f9788b591f77e1818a282e25c664fc5558d390e3870c3995a4bd4f5d0`. Standalone: 547927 bytes, 72 members, SHA256 `5027fadc5cfe5d36eaafc784b5836a3b212d79a856ca603e79f90d024b05a9f1`. Margins above the mandatory reserve are 35298 / 39897 bytes. I read these artifacts; I did not rebuild them or independently repeat the whole builder verifier.
- `git diff --check` for the frozen delta produced no whitespace errors. The timeout-test change preserves failure when no child PID is recorded and labels cleanup UNVERIFIED; it does not turn missing evidence into a successful cleanup observation.

## Readback scope and retained limitations

Read the retained POSIX logs showing completion22, transition20, pending-settlement17, registry20, archive18, distributed50 boundary controls plus six C04 cases, and the exact pending58/88 result. Also read approved budget, semantic21, composite8 and prefix40-unit results, helper observations, and old/new timeout witnesses. These are root-executed source/fixture evidence at their recorded source scopes, not independently repeated campaigns or native acceptance. The old missing-PID traceback remains retained.

The actual current-prefix route remains **unexecuted**. Successive preflight refusals are: unsupported external/partial/mutable Git storage; unsupported Git configuration; and, after complete detached Git preparation, image argument/descriptor bound exceeded. The current mapping/profile controls and bubblewrap smoke do not replace execution of the current23 group. Keep the runtime-image limit as its own prerequisite. Do not increase bounds or weaken source/configuration guards merely to obtain green.

The normal c2 builder log reports success, but repeat deterministic builds and isolated plugin/standalone copy/update/rollback/consumer checks were pending at the review boundary. The forthcoming report must bind any later result to its actual source and retain both old budget failures and current-prefix refusals. F1's source correction also requires the appropriate successor source/receipt identities; no c2 result automatically becomes a successor whole-candidate result.

No full canonical verifier/original117 correspondence replay, original-work-order acceptance, authentic C5/OR/C02, child H0/O/U/RETURN/acceptance/DISPOSE, native JOIN, native discovery, protected-state recovery, or GitHub currentness was judged here. Successful ordinary POSIX source tests do not supply those authorities. No complete installed or mainline readiness claim is supported by this review alone.

## Proposed mainline transition and next step

The lane's mainline-transition document keeps adoption unapproved, distinguishes donor ancestry/lifecycle effects from issue acceptance, and calls for exact resulting-tree review plus separate approval. Its squash/patch alternative is a proposal, not an enacted history change or a guarantee of GitHub UI outcomes. No action on that proposal is authorized by this review.

Next: root completes F1, runs the affected positive/negative fingerprint controls on the supported interpreters, retains the exact successor diff and evidence, completes already-planned package/install checks or truthfully records any blocker, then performs only the authorized guarded draft update. Keep source review, package qualification, mainline adoption, native authority and original issue closure separate. Reviewer stops after this report.


## Root disposition

The logical-newline defect was reproduced and repaired in268a15e78feaf0a1deb84ae4bbbd0e5b9c6b9dcd. The targeted negative control failed first, then passed; the complete helper controls and timeout-child held-out succeeded on the exact correction in Ubuntu Python3.12. Root accepts the bounded review findings as addressed for the authorized draft update. This is not a second independent review or native/issue acceptance. Repeat c2 builds were byte-identical and isolated four-layout copies/reinstalls plus staged-failure cleanup subsequently passed at their exact c2 artifact scope.
