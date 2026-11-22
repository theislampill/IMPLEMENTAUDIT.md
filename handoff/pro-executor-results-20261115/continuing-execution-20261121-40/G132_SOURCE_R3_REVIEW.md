# G132 source/custody R3 — independent ordinary review

**Disposition: PASS at the frozen source-repair and retained local-evidence scope.** No material defect requiring revision was identified in the reviewed change. This is advisory input to Root; it grants no hosted, native, protected, original-execution, integration, publication, currentness, or acceptance authority.

Reviewer: `/root/g132_source_custody_review`, independently assigned by Root. The reviewer made no candidate edits and executed no candidate code, Git commands, hosted operations, controller commands, original operations, or provider writes. The review used source inspection, AST/compile-only inspection, hashing, independent Git object/tree decoding, and receiving of already retained local results. It did not repeat those controls.

## Exact object and scope

| Item | Received identity |
| --- | --- |
| Candidate packet | `g132-source-custody-r3-candidate` |
| Candidate seal | 372,448 bytes; SHA-256 `fd45ff497cadba67a4719ea9ab8018d3cd13b8f38b687de57634ac3c9403c176` |
| Payload census | 1,373 regular files; 6,363,913 bytes |
| Base commit | `f75533f95f0d099c87e7a04beb11b0a25628acdc` |
| Base tree | `9b9c2b3f1453b83b87b628b665fceff492bf5b1e` |
| Base sole parent | `e76a07b2bae7c945e5a9d529ed8cf9069f4c9064` |
| Changed owner | `scripts/qualify-work-graph-c5-setup.py` |
| Proposed owner | 90,827 bytes; SHA-256 `7ee5f2282d650692db140629ce436d6502ac0cf4f97786ed8c879192b603e9b0` |
| Proposed Git blob / mode | `515ecf98f5db25454dd8ddf8e61a134264a65458` / `100755` |
| Proposed complete tree | `f85b199c89e9f6938382ec5f7b2005f54acc8536`; 1,768 leaves |

The reviewer independently authenticated the retained base commit object, reconstructed its complete tree from the retained leaf rows, and derived the proposed tree by changing that one owner. Fourteen full inherited physical owners were authenticated to their base Git blobs. All thirteen Engine mappings and pins were received, including the qualified physical Git08ca executor owner behind its logical script name.

AST and full-byte comparison establish that `hosted_git` is the only modified existing function, `prepare_hosted_source_selected_v3` is the only added function, and the other 42 existing functions are unchanged. Replacing the modified function with its base bytes and removing the added function restores the complete old module byte for byte. The legacy `prepare_hosted_source` function is therefore unchanged. Compile-only inspection succeeded; no candidate module was imported or executed by the reviewer.

The prospective branch and commit are not established by this review. A later publication must retain the exact derived tree and a sole parent of `f75533f95f0d099c87e7a04beb11b0a25628acdc`, subject to Root's live guarded publication checks.

## Process custody repair

The changed helper observes direct-child exit using `waitid(P_PID, pid, WEXITED | WNOHANG | WNOWAIT)`. It records and validates the returned child identity and exit-kind fields without reaping the child. The selected Python API documents that `WNOWAIT` leaves the child available for a later wait. This supports the repair's retained-leader premise under the explicitly required exclusive direct-child wait custody.

On every path where a process handle exists and the helper still owns an unreaped child, cleanup observes that custody again, attempts the process-group SIGKILL before reaping, and only then uses bounded `waitpid` to receive the actual child status. This includes normal exit, nonzero exit, timeout, stream overflow, and exceptions during observation. After reap, the only group operation is signal zero as an absence observation; there is no destructive signal against a possibly reused group identifier. Missing ownership and unexpected prior reaping refuse rather than authorize a speculative group kill.

The helper requires default SIGCHLD handling before process creation. The fixed Git executable and credential/configuration isolation remain intact. `GIT_NO_LAZY_FETCH=1` and `GIT_NO_REPLACE_OBJECTS=1` prevent those implicit object substitutions. The helper preserves its 60-second command ceiling and 4,194,304-byte per-stream ceiling, records actual observed byte counts, identifies prefix-only hashes on overflow, and uses a bounded five-second reap phase. A successful receipt requires zero exit, completed cleanup, observed group absence, and restored descriptors. The normal read loop must observe both EOFs and unreaped exit; error, timeout, and overflow paths cannot receive success.

This is not a general escaped-descendant containment proof. It relies on exclusive direct-child wait ownership and the same process group. It does not establish a native host's signal policy, external reapers, escaped sessions, process-cgroup behavior, or a subreaper capability. Failure to return a process handle is recorded as unobserved creation outcome and receives no successful custody claim.

## Selected complete-ancestry acquisition

The new function has ten actual Git commands: initialize a fresh standalone SHA-1 repository; add the fixed public origin; fetch the exact parent with `--keep` and an explicit ordinary parent anchor; fetch the exact child incrementally with `fetch.unpackLimit=64`; detach at the child; observe exact identity and sole parent; verify nonshallow state; verify clean state; run strict full fsck; and enumerate reachable objects with missing-object reporting.

The parent and child fetches use `--no-tags`, `--no-recurse-submodules`, and empty `--refmap=` with explicit selected input. They use no shallow depth, object filter, alternates, promisor mechanism, replacement objects, synthetic commit, manual object extraction, or manual repacking. Git's documented `--keep` and `fetch.unpackLimit` semantics support a packed full-parent acquisition followed by a small naturally loose child increment. The repository path, output ownership, mode, emptiness, overlap, and exact identity checks remain explicit. A distinct initial unborn branch avoids fetching the parent into the checked-out branch.

The function verifies the child identity, a syntactically valid observed tree, and the exact sole parent. The future observer must additionally compare that tree with the approved complete source tree. The final lstat requires a genuine regular, singly linked, bounded loose HEAD object. The unchanged downstream source owner performs bounded decompression and Git object identity/tree binding; the preparer does not manufacture a loose object to bypass that check. If Git packs a larger child increment, this preparation refuses. The fixed unpack threshold is not a guarantee that every future source is admissible.

`rev-list --objects --all` establishes the reachable closure of HEAD and retained refs, not an inventory of every unreachable object. The retained strict fsck and unchanged full source-capture machinery remain necessary. This review uses “complete selected ancestry” in that precise sense and does not equate the listing with a complete byte capture.

The old full-clone preparer remains callable. Publication of this source alone would not select the new route in a hosted observer. A new exact observer must explicitly call the new function and bind the real published source commit, parent, complete tree, and revised setup hash.

## Namespace, G1 dependencies, and bounds

The reviewed namespace validator still rejects shallow storage, alternates, grafts, replacement refs, lock/promisor files, worktree/module indirection, and unsupported configuration. The new parent anchor is an ordinary ref; the existing namespace rules permit it. The retained local capture passed those actual unchanged namespace and loose-HEAD checks.

The original producer contract and two-clone requirements remain unchanged. `_producer_contract` still requires the original selected producer-program hashes and exact package-source selector population. Both original clone templates retain `--quiet --no-local --no-checkout`, exact detached checkout, and simultaneous worktree lifetime. The proposed full-tree comparison shows no removal or substitution of those dependencies. Selecting the full ancestry of the exact source commit is structurally compatible with those requirements; unrelated remote branches are not a producer dependency. The tiny local fixture did not execute the original producer contract or its original build payload.

All existing owner constants and guards outside the changed helper/new preparer remain byte-identical. In particular, source capture still has a 128 MiB single-file ceiling, 256 MiB total ceiling, 4,096-entry ceiling, and depth 40. Observer limits remain 1.5 GiB address space, 120 CPU seconds, 256 MiB file size, 256 descriptors, the existing 240-second operation deadline, and the 2 MiB report ceiling. No Engine member, Git pin, original Git08ca case row, clone template, launcher identity, private input, custody predicate, or original award is changed by this proposal.

## Independently received local evidence

The review's data-only receiver completed once, host receipt **`a9fcfe/0`**, with **8,499 checks**. Its complete output is `MECHANICAL_RECEIVING.json`; its exact implementation is `receive_data.py`. This count represents packet/object/receipt checks, not new product tests or original acceptance episodes.

All 1,373 payload byte lengths, SHA-256 digests, Git blob identities, regular-file kinds, and exact inventory membership were checked. The source's retained 124-control result, its driver return and streams, all ten worker returns and streams, selected-source receipts, and fixture Git stream digests were independently joined. The supplied 2,213-check structural result was authenticated as a frozen payload; this review's separate checks did not simply reuse that result as its own verification.

The retained actual local source control used Git **2.47.3**. It called the candidate's real helper and a same-code-object copy of the new preparer with only the origin URL substituted to an ordinary local fixture. This disclosed transport substitution establishes local behavior, not native Git08ca or remote-host qualification. The fixture includes a genuine packed parent, a genuine loose child, nine reachable objects, an unrelated remote branch excluded from the selected closure, and two ordinary clone controls. The reviewer decoded the retained loose and packed objects independently, checked object and pack/index identities, traversed full parent/tree closure, and compared both clone closures without invoking Git. This does not substitute for the recorded actual `git fsck`, nor claim independent validation of every pack-index offset/CRC field.

The ten retained process controls distinguish success, nonzero exit, timeout, overflow, closed-pipe descendants, held pipes, an outer exception, missing cwd, ignored SIGCHLD, and the historical helper's closed-pipe behavior. Only the normal successful candidate command received success. The selected source's ten commands each received zero exit, both EOFs, owned cleanup, actual reap, group absence, and descriptor restoration.

The controlled closed-pipe descendant was already exited by SIGKILL before fixture cleanup under the candidate; the corresponding old-helper descendant was still running until the fixture cleaned it. The held-pipe case remained a truthful refusal: the worker immediately observed the descendant running and then used its own fixture cleanup. No product proof of its death is inferred. Several refusal cases retained group-presence observations, including zombie effects; those observations were not relabeled successful containment. The fixture's own subreaper cleanup is distinct from product capability.

Wrong-parent input refused after six commands. A larger genuine child increment refused after ten commands because HEAD remained packed. Prior source-fixture failures and superseded source bytes are retained, including the initial branch-anchor conflict and the earlier parent-storage failure before `fetch --keep`. These are development observations, not spent original operations.

### Missing early receipt

`EVIDENCE_NOTES.json` discloses that an early red-named actual-command record was accidentally overwritten by a later green run before freezing. The surviving body is correctly named `POST_IMPLEMENTATION_NORMAL_GIT_RECORD.json`. The old exact command receipt is absent; the reviewer did not recreate it or infer its missing contents. The retained red return/stderr support the two reported failed assertions, but do not supply that lost command receipt. A later separate old-helper control has full retained worker evidence. This evidence limitation remains explicit and does not become a new award or a reconstruction of the missing episode.

## Evaluation of the proposed acceleration

The owner's supplied measurements, 277,761,404 bytes for a full-clone pack and approximately 35.9 MB / 13,961 reachable objects for selected history, were not independently measured from their authentic underlying files in this review. The supplied full pack size exceeds the unchanged 268,435,456-byte file-size ceiling arithmetically. That makes the explanation plausible, but does not prove the precise hosted diagnostic04 failure cause.

The selected-ancestry design is a valid structural way to avoid acquiring unrelated branch history while preserving full selected ancestry, ordinary storage, exact source identity, and the original two-clone dependencies. The received local evidence demonstrates those mechanics on nine objects. It does not establish the real selected repository's pack size, 13,961-object closure, total captured bytes/entry count, 128 MiB per-file fit, real 64-object child increment behavior, exact Git08ca behavior, deadline fit, or native cleanup. Thus this repair removes the identified source-design and local-custody defects at its qualified scope. It does not yet remove the hosted qualification blocker.

## Remaining gates and no-replay boundaries

Root may use this source review as input to guarded ordinary source publication and a separately identified ordinary compatibility qualification. The next observer still needs exact source/pin binding and authentic host observations for the image, selected Git executable, launcher, namespace/capture, child custody, private input, dedicated nonroot sender, receiving, and resource conjunction. Those are not granted by local Git 2.47.3 receipts.

The spent original `G132_ORIGINAL_20261120_01` / run `44888568054` remains spent. Historical unknown and already terminal operations remain distinct and unreplayed. Historical queued run `43098152901` was not touched. This reviewer created no hosted job or external operation. No M1/M3/M6 award, DG16 original disposition, DG17 award, or DG18 award is conferred.

A genuinely new protected G132 launch remains unavailable until complete independent prerequisite qualification and a fresh exact owner grant. The current review neither asks for that grant nor authorizes use of a spent approval.

## Review continuity and primary references

This child experienced a context boundary and stopped candidate inspection until Root rebound the assignment. Root supplied fresh require-current receipt **`3f0ffd/0`**, bound to controller `dg16-dg18-recovery-20261119-b`, G0045 receipt `refs/implementaudit/continuity-receipts/dg16-dg18-recovery-20261119-b/G0045@da78b456997516f38e8e8b048c221bec6e4c0c4b`. The child did not invalidate or call the Root controller. It reconciled the preceding truncated-output patch call: only `receive_data.py` existed; no receiving result had yet been written. The data receiver then ran once successfully. This is ordinary delegated review binding, not a formal internal-child route or a child-issued currentness claim.

Primary API references checked during review:

- Python 3.12 `os.waitid`, `WNOWAIT`, and wait-status conversion: <https://docs.python.org/3.12/library/os.html>
- Git fetch 2.43 documentation, explicit refspecs, empty `--refmap`, and `--keep`: <https://git-scm.com/docs/git-fetch/2.43.0.html>
- Git configuration documentation for `fetch.unpackLimit`: <https://git-scm.com/docs/git-config/2.44.3.html>

The docs support API reasoning; the sealed source and actual retained records support this review's concrete findings. Final candidate immutability and the review output seal are separately recorded. This report is evidence input for Root adjudication only.
