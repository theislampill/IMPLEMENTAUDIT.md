# DG17 independent source review — residual Administrators grant

## Disposition

**SOURCE_PUBLICATION_SCOPE_QUALIFIED. No blocking finding in the exact five-file candidate.** Root can perform guarded source publication under the existing authorization. Actual Windows execution of the fixture correction remains pending. This review grants no native authority, native acceptance or original-fourteen credit.

Reviewer: `/root/dg17_independent_review`, distinct from the author, under root controller `pro-executor-01`, root-reported current generation G0005. This is independent source engineering, not a formal audit-assess transition. The fourth run was independently received as a separate scope in `receiving/INDEPENDENT_RUN_RECEIVING.md`; those observations are bound to its earlier source, not this candidate.

## Frozen binding and five-file population

| Binding | Value |
|---|---|
| Candidate commit | `3bde5a5123d3b1c6cf908b2e263504dce994d4e7` |
| Candidate tree | `7f35924e92b2c7a6e095debc02b6f7076e3cb1cc` |
| Parent commit | `4db726a4f5c7f6429589a941977e233ece967e91` |
| Parent tree | `df9b72c932a0b60dca918232567e725fa0585771` |
| Published same-tree parent | `50c7fd7e279cd1f97345941d1ef13d6d76412cd8` |
| Worktree before and after tests | Clean at the exact candidate HEAD/tree |

All five diffs were inspected. Paths in the table are relative to `handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/`.

| Changed file | Bytes | SHA-256 |
|---|---:|---|
| `README.md` | 4533 | `9171d80e9ed97b365c1ebc994f90fb71b487ea1ade7c4fb60287f00f2e069ed0` |
| `SOURCE_QUALIFICATION_MANIFEST.json` | 154169 | `208a1dfb224fa902b22429ff6161177449b884dddd36c871ed444259d7eb6a49` |
| `SOURCE_REHEARSAL_20261115.md` | 39376 | `3021249295352a5d30d66d2e0529aa1e9b03698c007acf0b9af3b2c65e24f2f7` |
| `tools/test_driver_bundle.py` | 29284 | `12ca86d70e194dfaa432659df630edb021a3eeeca1cebe0077cc809b77132d0f` |
| `tools/test_store_custody.py` | 7447 | `546ead882cdc019298e3b5328dcc100ec8e1059d73fb6eaabe6085c9fbd903a4` |

All manifest file pins match candidate bytes. Its new fourth receiving object exactly equals the already frozen 42,735-byte packet after JSON parsing; the packet still hashes to `b2abc0db85b8c0faa3708b6d9b8e3ef642c42c45468abdf5471c6c03d5fad03c`. The previous second and third receiving objects are unchanged. New narrative correctly retains the ten setup errors, the limited actual owner-readback success, earlier failures, and pending actual Windows verification of this correction.

## Source judgment

The only fixture behavior added is:

```python
icacls(p, '/remove:g', '*S-1-5-32-544')
```

It executes in the shared fresh-directory factory after ownership verification and the existing user+SYSTEM grant setup, before the unchanged complete private-baseline check, and before any intended extra grants. It applies to every factory use, including parent and child preimages, without changing the case population.

The [Microsoft icacls contract](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls), opened during this review, documents SID-specific grant replacement, removal of inherited entries, and `/remove:g` removal of granted rights for the specified SID. A numeric SID uses the leading `*`. This supports the narrow operation selected for the observed residual grant. It does not establish an actual result for the candidate on Windows.

The unchanged wrapper uses the fixed System32 icacls executable, a list of separate arguments, captured output, a 30-second timeout, and a zero-exit assertion. There is no recursive flag, reset operation, generic DACL clearing, or error suppression in the added command. It targets the fresh fixture path passed to the existing factory.

AST comparison proves that removing this single added statement makes the entire fixture AST equal to the parent. Owner assignment, the direct .NET query and strict SID parser, all fourteen cases, all eleven negative reasons, full baseline checks, child/junction sequencing, wrong-owner proof and error classification are unchanged.

The intentional Administrators negative still adds its ACE only after a complete private baseline, so targeted baseline cleanup cannot remove the adverse condition being tested. The Everyone tests likewise retain their later perturbations. An unrelated residual principal, an unsupported deny entry, or an ineffective Admin removal continues to fail the complete baseline as ERROR. A baseline failure cannot become negative-control credit merely because its message contains the intended SID or reason.

The exact tree diff contains no product, package/runtime, builder, rehearsal or workflow change. Strict user+SYSTEM custody, all handle/identity/link/reparse/TOCTOU protections, seven-field file identity equality, process restrictions, original limits and native assertions remain unchanged. The previously qualified source-only workflow retains its exact bytes and scope.

## Fresh focused verification

| Check | Result |
|---|---|
| Supplied focused source/model suite | 25 methods PASS, 0.143 seconds, exit 0 |
| Independent source/adverse suite | 8 methods PASS, 0.069 seconds, exit 0 |
| `git diff --check` | PASS, exit 0 |
| Manifest file pins and historical receiving equality | PASS |
| Exact one-command AST delta and unchanged cases/reasons | PASS |
| Worktree/HEAD after tests | Clean and unchanged |

The supplied suite was imported with its assertions and ROOT unchanged; only its disposable TemporaryDirectory location was redirected into this review directory. It constructs inert local fixtures and models Win32 behavior. No real PowerShell, icacls, Win32 custody episode or native model call was made. A pre-existing SyntaxWarning from the unchanged historical stage-B docstring did not affect the passing suite.

The eight independent methods covered:

1. Exact one-statement fixture delta, five-file population, and unchanged fourteen/eleven case/reason population.
2. The observed preimage failing under the old fixture and passing under the candidate model, plus an already-clean preimage remaining valid.
3. Complete baseline before intended Admin/Everyone grants, with the intended refusal preserved afterward.
4. An ineffective zero-error removal remaining a baseline ERROR, without executing the intended extra grant.
5. Unrelated Everyone grants and Admin deny entries remaining present and causing baseline ERROR.
6. Removal assertion, timeout and permission failures stopping before baseline or perturbation.
7. Exact fixed icacls argv/timeout and actual wrapper rejection of modeled nonzero exit.
8. Historical packet preservation, manifest pins and unchanged product owners.

Full test sources and logs are retained here. The author RED/GREEN logs also match their manifest hashes: 25 methods/three failures in the RED log, then 25 methods/OK in the GREEN log. The review's success claim rests on the fresh independent runs. The full lifecycle was not rerun for this fixture-only source change, and no unrelated package tests were repeated.

## Historical evidence and remaining boundary

Run 43679794953 remains overall FAILURE at source `50c7fd7e…`/tree `df9b72c9…`. Linux's three modes and 24 methods succeeded. Windows had 23 recorded successful independent owner reads, one recorded complete private baseline, successful driver creation/recheck and intended missing/file negatives, and ten baseline ERRORs. Only two of eleven intended negative predicates were reached. The residual Admin ACE's detailed origin remains uninferred; the reached foreign-SID branch supports the narrower non-inherited allow characterization.

The prior identity failure remains unexplained; previous wrong-owner intercepted negatives and Get-Acl setup errors remain unqualified. This source correction does not regrade any of them. No actual Windows result for the removal command or complete fourteen-case population is awarded by local modeling.

Native admission and acceptance remain false. Genuine Codex turns and native appservers from this review remain zero. All fourteen original custody UNKNOWN differences remain. Final location/tool/package identities, exact operation receiving, fresh written owner grant, authentic A/B turns, independent post-A receiving, POST_B, T12 and custodian requirements remain outstanding. Root owns any subsequent guarded publication and actual source-only Windows receiving.

Source edits, remote mutations, workflow dispatches and native calls by this reviewer: zero. Receiving used retained artifact members and provider reads; artifact bodies were not reacquired.
