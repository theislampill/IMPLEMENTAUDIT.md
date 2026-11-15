# DG18 current installed consumers

Original R0039/#215 F8 and criterion 11 require applicable exact-source package,
isolated-install and current-consumer evidence. The completed package record at
`080cc0e29bd6382b0c31f3f69e9ad2f8d42991b2` expressly leaves this installed leg open.
This change extends the existing DG18 source-qualification workflow to perform
only that leg. Existing source/C02 jobs retain their original branch conditions.

## Exact inputs and ordinary operation

Product source is `775d6a0add0a1edcbc7f6cf5ccd68d350757fe8a`, tree
`66607502c26f533416aa9cc00b3b5728e1e0e11e`. It is checked out separately and must
remain clean. The two actual published-source archives are read unchanged from
the existing `dg18-current-source-775d6a0a/COMPLETED_EVIDENCE.zip` transport. The
transport and each selected archive are pinned by exact bytes and SHA-256.

| Role | Bytes | SHA-256 | Headroom below 589,824 |
| --- | ---: | --- | ---: |
| Canonical plugin | 586,931 | `32f63a1759ac3852ed51ad20fea87e2ed524a14322d9d97210d4b7345cb81556` | 2,893 |
| Standalone compatibility | 582,329 | `4ad29f2eccdaa4133f4d0f0f852b4aa4dcfb6a57b9a337b3a0e727cfb7496dfb` | 7,495 |

Both meet the original 2,000-byte reserve. No package build, new dependency
installation, source test bank, original occurrence replay or budget amendment
is selected.

The existing installers create canonical Codex/Claude and standalone
Codex/Claude copies in four separate disposable directories. The existing
package verifier checks each archive against its exact source. Complete file,
byte, digest and mode parity is checked after installation and after use.

For each route, the adapter authors a fresh bounded qualification task and uses
the **installed** `claim-run.sh` for claim, initialization inspection, activation,
first resume, receipt verification and currentness. The existing
`fixtures/controller-initialization/author_checkpoint.py` reads the exact
source templates to author the task; it does not activate or issue receipts.
STATE and ROADMAP are read in distinct completed workflow steps before resume.
Actual receipt objects, ref readback, task files and complete installed parity
are retained for independent receiving. Ref and document reads after the
receipt must preserve their actual bytes.

The workflow is limited to first-attempt pushes to
`engineering/pro-dg18-installed-current-20261115`, with read-only repository
permissions and no retained checkout credentials. The ordinary Ubuntu runner
provides the existing root-owned system-interpreter predicate that is
unavailable in the local recovery container. No local guard is altered.

## Scope and rollback

This is an actual deterministic installed-consumer qualification. Its output
needs independent receiving. It proves neither model/native host discovery nor
original N1, compaction, OR, accepting C02 or Windows W-FULL operation. The N1
historical gap remains LOST/UNKNOWN and unconsumed; its criterion-5 exception is
not approved. The existing ordinary source commission does not create any
protected-effect grant or original acceptance award.

Failure stops the selected job and captures its already-created disposable task
files, including `.claimed` and `.controller`, into the evidence directory.
Capture is bounded to the one newly created task root per route; aliases,
oversize populations or changing files retain an explicit unverified retention
result. No failed effect/currentness outcome is inferred from captured files.
The uploader includes hidden files only inside that restricted evidence tree.
There is no automatic replay. No previous subject, installed user home,
original owner store or protected history is touched. Removal consists of
disabling this branch-scoped job and its repo-only adapter; all qualified
product source and existing receiving records stay unchanged.
