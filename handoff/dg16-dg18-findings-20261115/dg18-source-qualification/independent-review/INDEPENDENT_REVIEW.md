# DG18 independent source publication review

## Disposition

**No blocking finding within the bounded source publication scope.** The frozen
candidate is qualified for the principal controller's already-authorized,
guarded publication to `engineering/pro-executor-dg18-source-20261115` and the
source-only workflow defined in that candidate.

This is a distinct agent's source review under the owner commission, not a
formal audit-assess lifecycle verdict, original DG18 acceptance, a native launch
grant, a currentness decision, merge/release authority, or issue closure.
The reviewer made no changes to the candidate and performed no publication.

| Reviewed identity | Value |
| --- | --- |
| Reviewer | `/root/dg18_independent_review` |
| Author identified by candidate | `/root/dg18_engineering under PRO-EXECUTOR-01` |
| Candidate commit | `8be345fe411e8dba8f0b06a1e2e3830337b0e7f9` |
| Candidate tree | `23b555580b65a937a03e111515182bdabac35cd5` |
| Parent / tested runtime source | `e4cba42cb5704f00b78d64e43f5da88501c28229` |
| Parent tree | `7dd2b0b3921eb764669eaad98a9f0fd94f873c84` |
| Workflow SHA-256 | `acddb8336fc182bf676d76b43d10879f62ac53b31a9b982fdacfb49d68a246cb` |
| Runner SHA-256 | `062df41677fae3a93e789d847b5a29237591624ba198b7068b45de9b00f2777d` |
| Qualification report SHA-256 | `62bff25c033e0ba75a492a794d0abcaff040c5b174456065fb37226f51c2b0c8` |
| Input packets SHA-256 | `9ff71b9073a39969ced3347482dcee54af0202bf5530ba3cb66c583645b43910` |

## Evidence checked

The exact commit, tree and parent match the dispatched review packet. Its diff
contains 18 additions: the proposed workflow and 17 files beneath the source
qualification handoff. No runtime, fixture, source-peer, or package file changed.
The tracked working tree and index were clean; the existing untracked
`.qualification/` directory was neither read as authority nor added to the
reviewed population. `git diff --check` passed.

The independent verifier completed **136 of 136 checks**, with zero failed
checks. The complete results are in `verification.json`. They include:

- Every member byte count and SHA-256 in the handoff manifest, and exact
  coverage of the 18 added files, with the manifest itself bound by the frozen
  Git tree.
- All 13 recorded source file pins; all four complete clean source trees;
  all 17 peer manifest members and both frozen core dependencies.
- All eight exact function segments, including line bounds and hashes: the
  four requested OR/C02 bodies in core and peer are identical while the whole
  files remain distinct.
- All five historical repository input byte/hash pins against their actual
  locally available Git objects. The two stated core owner modules are
  unchanged from PR255 head `5277eb82bac6c10e190238afb54eda112eba284b`.
- All nine retained test transcripts, their hashes, verbose pass/skip/error
  accounting, unittest totals, and recorded exit classifications.
- Missing input/null fields, source-parent identity, workflow trigger,
  permission, checkout, action-pin and upload boundaries, Python AST syntax,
  and all four Bash step syntax checks.

The retained accounting is correct: **109 executed test cases across nine
invocations: 105 passed, one authentic-probe case skipped, three environment
errors, and zero assertion failures.** Core and peer invocations are separately
identified; this total is not an original-acceptance denominator.

The authentic-probe skip remains unverified. All three CLI errors occurred in
fixture setup at `claim-run.sh`'s supported physical interpreter / path-custody
gate. They are not successful CLI qualification. Their original evidence is
retained and has not been overwritten by this review.

## Independent execution

The reviewer used separate temporary and evidence directories beneath
`dg18-review`, with bytecode writing disabled, and executed the unchanged
candidate's actual fixtures:

| Focused check | Observed result |
| --- | --- |
| `input_contract_test.py -v` | 8 tests, all passed, exit 0 |
| `c02_native_source_test.py -v` | 16 tests, all passed, exit 0 |
| New runner with `/usr/bin/python3 -B ... --preflight` | Exit 1, expected sole custody refusal |

The 24 replayed tests exercise the actual OR proposal/threshold/freshness and
C02 proposal, source/census, issuer-custody and CAS mechanisms with their existing
explicitly constructed test authority. They establish source behavior only.

The reviewer independently observed all 13 file pins and four tree pins pass
preflight. The only failure was
`ROOT_OWNED_NONWRITABLE_PYTHON_PATH_REQUIRED`, with the actual system Python
owned by UID 65534. No fixture directory was created by that preflight.
This confirms refusal without bypassing the original guard. A positive run of
the three blocked CLI cases still requires the proposed hosted execution.

The independent verification harness initially attempted an extra comparison
of a nonexistent core `bounded_source_owner.py` path. The source report does
not claim that comparison. The reviewer corrected this review-only assumption
to the two actual core owner modules named in the handoff and reran the full
136-check verification successfully. No candidate change resulted.

## Source and authority boundaries

Selection of `skills/implementaudit/scripts` is justified by root `AGENTS.md`,
the issue owner map, and the actual H0 template at
`faaa43e068bc758e28f1953d4204ce6aae1e543d`. The template's runtime entries select
the four declared core paths. This establishes the source-copy choice for this
qualification; the packet correctly states that actual native entitlement is
not established.

The OR threshold and minimum-payoff values agree with the actual source. The
observation proposal retains `PROPOSED_INPUT_ONLY_NO_EFFECT_AUTHORITY`; the
C02 proposal retains `NO_EFFECT_AUTHORITY`. Actual issuer/grant and census
admission remain separate from matching hashes or constructed fixture evidence.

The OR, C02 and W-FULL missing-record groups remain explicit nulls and each lane
remains blocked on its named authentic inputs. The historical Windows
entitlement is literally `UNGRANTED` and is explicitly non-reusable. There is
no new native operation record and no fresh native grant.

N1's owner, store and assignment have not been recovered. Its reported boundary
prefix `162f88f4`, scope prefix `45de02cb`, cutoff `109411`, and reserved/pending/
uncovered status agree with the existing handoff. The new packet accurately
labels these as reported facts, preserves absent epoch and consumption witness,
and does not infer custody from an archival transport role. Complete amended
cold receiving remains gated on the original N1 records and required execution.

## Workflow assessment

The only push workflow in this frozen checkout is the reviewed source workflow.
It is restricted to the exact engineering branch, with a matching repository,
event and ref job condition. There is no dispatch or native trigger.
The job has `contents: read`, a 15-minute timeout, and checkout/upload actions
pinned to full commit IDs. Checkout selects `github.sha`, does not retain
credentials, and disables submodules and LFS.

Before dependency installation or fixture execution, the runner verifies the
13 file hashes, four complete Git trees and their clean working state, and the
root-owned physical system-interpreter path. It installs the specified
`tiktoken==0.13.0` on the disposable hosted runner, records resolved dependency
versions, and admits only the exact encoding bytes/hash. The dependency record
does not assert byte-for-byte reproducibility of every transitive package or
of the changing hosted runner image.

The execution list selects exactly the one existing token CLI test and the two
existing C02 CLI tests. Their setup makes disposable repositories and invokes
the actual owner code. The source runner does not patch an interpreter guard,
select a real native store, start Codex, call a model, or supply a production
grant. The C02 fixture's constructed live-source/issuer seam is explicit in the
unchanged test and is not promoted to native authority.

Success requires both subprocesses to exit zero and report exactly one and two
tests, respectively, with plain `OK` rather than skipped-test success. Timeout
is a failing result; the report explicitly does not assert descendant
termination. The job-level timeout bounds the disposable hosted execution.

The upload paths are limited to `PREFLIGHT.json`, `RESULT.json`,
`DEPENDENCIES.txt`, and the selected test stdout/stderr. They exclude the
fixture repositories, stores, grants, generated native-looking records, and
encoding data. The source result explicitly records no native episode, model
turn, production grant, or original-acceptance delta.

## Required next interpretation

The principal controller may use this review for the exact source publication
and subsequently receive the hosted source result against its actual run and
commit identity. This report does not predict a positive hosted result. A green
job would qualify only the three selected deterministic CLI paths at that
source. OR observation/issuer authority, C02 actual-owner admission/publication,
W-FULL host/concurrent-owner inputs, N1 custody/execution, and final independent
cold receiving remain unchanged gates.

No broader package/install bank or repeated historical investigation was
warranted by this additive evidence/workflow diff.
