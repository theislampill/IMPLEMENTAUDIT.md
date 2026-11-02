# DG22 private adoption-method qualification

**Status: method qualification observed (PL4 structural checks and PL5 disposable
Git controls). Final adoption remains pending the real DG21 COMMON_ADOPTION
receipt, exact final subject, independent final receiving and owner approval.**

This evidence lane implements the owner commission of November 1, 2026. Its
writable public scope is this directory on
`pro/dg22-adoption-rehearsal-20261101`. The method run used newly created private
Git repositories. Product source, main, PR #255, donor refs, issue states and
human approval records were not changed. Historical 9a189 evidence remains at
its original subject; the older inert preparation was not promoted to a result.

## Actual subjects and results

| Role | Input commit | Exact input/result tree | Private method-result commit |
|---|---|---|---|
| Published checkpoint | `4af2e43b4047cd577aa6b56eecd5b27c5f0e45e0` | `8cb97d13e2b4f5e8bf99cc3e6e17e9267cbdef77` | `cdfec64a6dfad645f4b27a3a77562bc55c61c35c` |
| Separate engineering baseline | `d0abed5967e7fb2aab294089f75eb5c6c7e71471` | `d0446a12550dca6c885a3c569ffed21a9ec7dcd1` | `c56ff57d4d2fd5d91ad6f2cc4be3d43eaa9a3642` |

Both private result commits have exactly one parent:
`e78f7cb21af4197d490f10bc95917a4c75f748aa`, the received public main.
They are clearly marked METHOD_ONLY and are **not final adoption candidates**.
No combined public/engineering source or Sol composition was inferred.

Complete binary diffs, including modes and binary content, were compared byte
for byte between main-to-source and main-to-result. The published subject's
diff is 64,875,620 bytes, SHA-256
`629064293fb66ded99ed70eb53a5147fd2f3518e01e4c90bbf84a3d3d12c7bf3`.
The engineering subject's diff is 65,841,257 bytes, SHA-256
`2f89c13507a81687e1c7be993dccab63e1347a03a3d9a0a555a71e4897505c64`.
Each result adds one commit above the old main and introduces neither selected
source-head nor current donor-tip ancestry. All original histories remain
reachable through their exact retained input refs.

## Method comparison and observed controls

An actual ordinary `git merge --no-ff` in a private worktree produced
`695608585fde54e679dcbc89a4917b50a54d3f4e`, with ordered parents old-main then
published source, and the same published tree. It made the integration head
reachable. None of the five **current** donor tips is an ancestor of either
received source, so this packet does not repeat older claims that an ordinary
merge would currently mark those five donors merged. Their older included
history and the current integration head are different subjects.

The recommended method shape remains a new single-parent exact-tree commit,
followed by an explicitly bounded non-force ref update. The performed transport
was local Git file transport, with a pre-push check of the remote's advertised
old head, candidate, target ref and transport path. Native Git then guarded the
actual receive transaction. A stale advertised head that would otherwise permit
a fast-forward was refused. In a separate real race, the advertised old head
matched, a controlled competing writer changed the target, and the receiver
rejected our update with an expected-old mismatch. The competing commit remained.

`METHOD_RESULTS.json` records **19 controls: two accepted private updates and 17
expected refusals**. They cover stale head, candidate/source tree mismatch,
missing or truncated retained donor history, changed source input, ambiguous or
mismatched method, missing rehearsal authority, unapproved effects/live scope,
wrong target, wrong/reversed parents, closing directives, the receive race and
changed conflicting main. A separate constructed overlapping-main change caused
an actual `git merge-tree` conflict (exit 1); no conflict resolution was adopted.

Preflight refusals are explicitly distinguished from subprocess exits. In the
private raw result, value 2 is the harness's internal refusal result; it is not
an invented Git process exit. `METHOD_RESULTS.json` uses a null native exit when
no Git push was invoked. All actual command stdout/stderr and exits are retained.

The input source-pool refs stayed unchanged. Within the disposable method subject,
retained PR246 and published-source refs were intentionally removed/repointed for
negative tests and restored exactly at the end. The original raw
`retained_refs_unchanged` flag compares initial and final snapshots; it does not
claim there were no intermediate private-fixture changes. Original raw evidence
and the initial independent review finding are preserved.

This qualifies the recorded recipe in Git 2.51.1 / Python 3.12.14 on this Linux
execution host. It does not qualify a later GitHub API implementation, Windows
native episode, public lifecycle effect, or changed final input.

## Package identity is a real adoption dependency

The two supplied package inventories actually name published source `4af2e43` and
tree `8cb97d1`. Both unchanged official package verifiers were executed against a
clean checkout of private result `cdfec64`. Both returned exit 1 at **inventory
source binding**, because the commit changed despite tree equality. This is the
expected negative consumer result (PL5), not a package repair or a new COMMON
failure. No package was built, copied, relabeled or installed.

DG21 must bind the eventual package strategy to real identities. It can qualify
packages built at an exact prepared final adoption commit when that is the
selected authorized route, or preserve the real original build identity and
explicitly qualify each permitted source/package/consumer bridge. The existing
strict verifier cannot be bypassed by an equal-tree statement. Old archive and
inventory hashes must never be reused after editing `source.commit`.

## Lifecycle and approval boundary

The received five donor PRs remain open/draft/unmerged and have zero submitted
GitHub reviews; zero reviews is not a judgment about private reviewer evidence.
Their current head/tree records are in `ADOPTION_READINESS.json`. All ten original
issues remain open. The complete ten supplied issue bodies and 32 supplied
comment IDs/bodies match the received public corpus. Adoption-specific
requirements and residuals are preserved in `ISSUE_SLICE_REQUIREMENTS.json`.

Main/PR/donor/issue observations are time-bound, non-atomic readbacks. Reacquire
material identities and authority before any eventual effect. Donor narrative
snapshots are older than current heads and remain historical. The eventual
adoption commit must contain no closing directive, and original issue decisions
remain with their existing owner.

`ADOPTION_READINESS.json` populates all known observations, the performed method,
history retention, consumer constraints, expected readbacks and containment.
Final source, actual COMMON receipt, exact approved transport and human approval
remain deliberately unset. This is not a request to approve an incomplete
candidate. CE059 consumes COMMON_ADOPTION for the selected finite subject; it
does not impose completion of all ten original issues.

Before an effect, any stale/missing source, authority, tree, method, donor
retention or receipt input means refusal. After an ambiguous transport outcome,
read the actual target first; do not blindly retry. Any later correction of an
authorized mainline change requires a separately reviewed and approved forward
revert/corrective commit. No force reset is included, and a source correction
does not undo external PR/issue/native facts.

## Evidence and independent receiving

The owner return archive contains the executed buffer, immutable input manifests,
actual result Git bundle and complete history graph, full binary diffs, every
command and raw output, hook advertisements, both package-identity refusals,
public lifecycle receiving and the independent review. Private raw carriers and
object payloads are not published in this branch.

`rehearse.py` is the recorded method-only evidence harness. It accepts only local
input objects, creates a fresh output subject, permits only file transport, and
has no live-adoption mode. It is not installed into the product and is not an
authorization validator for arbitrary future requests. Do not rerun unchanged
controls for reassurance; receive the retained evidence and repeat only a
demonstrably changed discriminator.

## Primary technical references

- [GitHub pull-request merge and indirect-merge semantics](https://docs.github.com/en/pull-requests/reference/pull-request-merges).
- [Git push semantics and non-fast-forward protection](https://git-scm.com/docs/git-push).
- [Git pre-push hook input contract](https://git-scm.com/docs/githooks#_pre_push).
- [Git guarded ref updates](https://git-scm.com/docs/git-update-ref).

Local Git does not prove GitHub UI effects. Independent public readback after a
separately approved real adoption remains a required DG22 obligation.
