# DG17 independent Windows-fixture source review — 2026-11-15

## Disposition and scope

**SOURCE_PUBLICATION_SCOPE_QUALIFIED.** No blocking finding was found in the
exact five-file fixture correction for root's guarded source publication and
the unchanged source-only CI. Actual Windows execution of the corrected
fixtures remains pending. This is advisory independent source-engineering
evidence, not native admission, acceptance, publication authority, or a formal
audit-assess lifecycle disposition.

Reviewer: `/root/dg17_independent_review`; root controller: `pro-executor-01`,
G0003. No reviewed source was edited, and no Windows/native host operation or
remote mutation was performed. All new review evidence was written under
`dg17-review/windows-fixture-ece3fa22`.

| Item | Exact identity |
|---|---|
| Candidate commit | `ece3fa22e605fb891e6f2995baf886b220113d14` |
| Candidate tree | `5d8e76d5aa9b1e8bd323244831bf9271bb5c9e15` |
| Parent commit | `06b22dcfa07cbfed8fc69d922530d05d544d0aef` |
| Parent tree | `b81b8b30065b6620a5eaff9a21bb087825b217fa` |
| Worktree | Clean before and after review |
| Scope | Five files: README, report, manifest, Windows fixture, focused tests |

The product custody function, complete seven-field file-identity guard,
packaged runtime, native drivers, operation limits, rehearsal implementation,
and workflow remain unchanged. Exact Git-object byte equality was checked for
the builder, custody generator, rehearsal, and workflow; the five-file diff
excludes all runtime/driver owners.

## Findings

### Correct preconditions before each negative control

The actual preceding Windows run showed that mkdir plus an icacls DACL change
left the owner as Administrators. The revised fixture explicitly sets the
current user's ownership and independently reads the resulting owner SID and
current token SID before continuing. A private user/SYSTEM baseline must pass
before the extra principal, inherited-access, or wrong-owner perturbation.
Child fixtures pass this baseline before inheritance is enabled. The junction
target passes the baseline before link creation, and lstat must show a reparse
attribute before the product checks the link.

The wrong-owner test first proves the private current-user preimage, changes
ownership to the Administrators SID, and independently verifies both that exact
postimage and its difference from the current user's SID. A failed or ineffective
owner mutation therefore cannot be mistaken for successful wrong-owner coverage.

### Setup errors cannot satisfy negative expectations

The case recorder requires an explicit intended reason for each of the eleven
negative cases. An unrelated RuntimeError no longer qualifies merely because
its class is REFUSED. Failures of the independent owner query or private baseline
are ERROR results. Baseline custody refusals are explicitly converted to setup
errors before the intended perturbation.

Independent adversarial checks supplied each expected refusal reason to its
own classifier and cross-supplied the other distinct reasons. The correct
reason passed; every different reason failed. All seven prior wrong-owner
false matches now fail their intended ACL/junction cases. Nonzero query exit,
malformed JSON, incomplete/invalid owner facts, timeout, private-baseline
refusal, failed owner mutation, and absent reparse preconditions all produce
errors or otherwise fail qualification before the intended product check.

This qualifies source discrimination for the 14-case/11-negative population.
It does not count eleven different semantic predicates or establish actual
Windows API outcomes; multiple inheritance cases intentionally reach the same
protected-DACL predicate under different prepared inputs.

### Literal, bounded Windows helper calls

The owner query is one fixed UTF-16LE encoded PowerShell program. It invokes
Get-Acl with -LiteralPath using the process-local DG17_FIXTURE_OWNER_PATH value,
and reads WindowsIdentity.GetCurrent().User independently of the product's
ctypes implementation. A path containing quotes, semicolons, dollar expressions,
or ampersands is passed as environment data and is not interpolated into code.

PowerShell and icacls use fixed System32 executable paths and argv arrays, with
no shell execution. PowerShell uses -NoProfile and -NonInteractive. Both commands
have 30-second timeouts; nonzero completion fails setup. The helper only inspects
or mutates the fresh test fixtures and establishes no product custody authority.

## Verification performed

| Check | Observed result |
|---|---|
| Supplied focused source suite | PASS, 23 methods |
| Additional independent source suite | PASS, 5 methods |
| Exact five-file population and current manifest hashes | PASS |
| Frozen SOURCE_CI_RECEIVING.json hash and embedded-record equality | PASS |
| Unchanged builder/custody generator/rehearsal/workflow bytes | PASS |
| git diff --check and final identity/cleanliness | PASS |
| Actual corrected Windows fixtures | NOT RUN; pending hosted result |
| Linux lifecycle rerun by this reviewer for this correction | None; earned result retained |

Only TemporaryDirectory placement was redirected for the supplied suite;
its assertions and source code were unchanged. The additional suite loads the
frozen fixture's function definitions with modeled helpers and never imports
_winapi or starts a Windows process.

## Exact changed files and evidence

File paths below are relative to
`handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/`.

| Changed file | Bytes | SHA-256 |
|---|---:|---|
| README.md | 3308 | `8ba80c36fa39a1b8ed2ed73d8c0d28823a4f34a0223ab148fdc204c2427a3e86` |
| SOURCE_QUALIFICATION_MANIFEST.json | 56925 | `63c4f757c5aa00eff2b711f527cb8ec3f6970eaf4938618de3460ecbe610fb5d` |
| SOURCE_REHEARSAL_20261115.md | 25799 | `84a39ab0be604825db30e34c490ca31666aa7bf8bae5c8ea794394a3231c7bfc` |
| tools/test_driver_bundle.py | 24818 | `5dd7b75d38e5ee1cd89dbb39ff219e236271502b3f2adb5fdf88db3ca9b01ac7` |
| tools/test_store_custody.py | 6732 | `5d1af9a0818fbfb050682d479647fa2fa4227eae89951e3d43a5943bcb0c5abc` |

| Review evidence | SHA-256 |
|---|---|
| supplied-23-controls.log | `d202e4a592523b567075387689c74c3e58c503621eaed71fbf5d8a5314b4eaac` |
| independent_fixture_controls.py | `20ba1f86f36dd376ea076916a5b893bb52bc6d41ded07001007f9e3d42f6f484` |
| independent-5-controls.log | `2385fff17cc0955bf681645b677e0028e33328c406f8c757ec23d0c0787ea21f` |
| Author's frozen SOURCE_CI_RECEIVING.json | `97fe609807cd2a665c09a88c3f676f5e124ee7270bf78d5b061f0395e98de6cd` |

## Retained Linux result, Windows failures, and native limits

The separate independent receipt for run 43677179224 receives the actual Linux
job's three successful modes at source-only scope, bound to published commit
`0d262630b826ecf634a44e3b8b9535b46a6dc14c` and tree
`b81b8b30065b6620a5eaff9a21bb087825b217fa`. The changed fixture does not invalidate
that unchanged Linux lifecycle evidence. Its receipt SHA-256 is
`ab52f0740fad0a38a76e12cbe9c90785328643e552c46c919f912b7d64bcf2d2`.

The first Windows identity mismatch remains unexplained. The second Windows
rebuild's passing comparison does not repair or erase it. The second Windows
fixture result retains the failed manual positive and seven inapplicable
wrong-owner negative matches. Neither failed job is regraded by this source fix.

Root owns guarded publication and receiving of the next actual Windows result.
The unchanged workflow can schedule both source jobs; a later result must retain
its own exact source identity and earlier valid evidence. Final-location Windows
operation and exact host inputs, fresh written owner grant, authentic A/B model
turns, independent post-A receiving, POST_B, T12, original14 receiving, and
custodian certification remain required. No native authority is created, and
all fourteen custody differences remain UNKNOWN with no replay.
