# DG17 independent source review — complete fixture DACL

## Disposition

**SOURCE_PUBLICATION_SCOPE_QUALIFIED. No blocking finding.** The frozen correction is suitable for root's authorized guarded source publication and subsequent source-only Windows CI. Actual Windows execution of this writer remains pending. One nonblocking documentation note is recorded below. This review grants no native admission, original14 receiving, DG17/R0037 acceptance or closure.

Reviewer: `/root/dg17_independent_review`, distinct from the author. Root reported verified controller `pro-executor-01/G0008`, receipt `fda5007ee43c62168481f23d511d083d6ab51be9`. This is ordinary independent source engineering; no child controller or formal audit-assess transition was created.

## Exact candidate

| Binding | Value |
|---|---|
| Commit | `0655cfa87cc3b81ed59ffa046d07b1ba616d631e` |
| Tree | `679520e74887ad685d9caacadd3d64c4348ef610` |
| Parent | `c2faca3a5bccf26b4571fddbece4d420385c86b5` |
| Parent tree | `aea366f397866411d592430da7928d4cfc97c284` |
| Five-file diff | 94597 bytes, SHA-256 `32a35342e53b979882ce78c1baf583d4cb1700369034e1b95da40ab7c782c2ca` |
| Author review packet | 6006 bytes, SHA-256 `1d08be5721debe83cd5c8a115cd359de0856ba4c931232ce961122e5aea0ebf4` |
| Worktree before/after local controls | Clean at the exact candidate HEAD/tree |

Every changed file and its diff was inspected. Paths are relative to `handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `README.md` | 5378 | `b3a2448663a767aad17ab34518a046fad67d6b9e7759524232cfdcd55253472b` |
| `SOURCE_QUALIFICATION_MANIFEST.json` | 212409 | `8701fd7d74921917dfd70bd48e9565b35ba66412cb6bdb3946b59f1fed24878f` |
| `SOURCE_REHEARSAL_20261115.md` | 50265 | `304d832d93ede80aa530a6f36a3b9860a28af5021dd2cf5747f0aa68f56f9c80` |
| `tools/test_driver_bundle.py` | 37296 | `7c16a86f02883e10b6120d1987e425d624935ba21080fc3a06446cf1b7232a47` |
| `tools/test_store_custody.py` | 8928 | `32614b757717b7dc0aa2234683b45117242d6ef105855759acfb29dfd0beebeb` |

Author packet, manifest and actual frozen file bytes agree. The manifest preserves second-, third- and fourth-run receiving objects and embeds the new restored fifth-run observation exactly. That new observation is 45411 bytes, SHA-256 `535d62e770f5843fcf2b6281fb620d08c36c9a7e448470a918839ec31517a69c`. Its Linux result records and Windows case population were reconciled with the restored artifact bytes in the separate receiving task.

## Source assessment

The common fresh-directory factory replaces its incomplete named-grant/removal setup with a fixed module-free PowerShell/.NET writer. The writer creates an empty DirectorySecurity, protects the DACL against inheritance without preserving inherited rules, adds current-token-user and SYSTEM FullControl allow rules with container/object inheritance and no special propagation, then applies the descriptor once using Directory.SetAccessControl. It disposes WindowsIdentity in finally. It does not read and extend an existing DACL or enumerate and remove a selected list of residual SIDs.

Microsoft's documented .NET Framework contracts support the construction: the parameterless DirectorySecurity constructor creates an empty object independent of an existing directory; SetAccessRuleProtection(true, false) protects it from inheritance; the five-argument FileSystemAccessRule overload accepts IdentityReference and explicit rights/inheritance/propagation/type; Directory.SetAccessControl replaces the existing ACL. The PowerShell 5.1 method documentation also shows the `::new()` syntax and explains that .NET filesystem APIs receive native filesystem paths. These are source/API checks, not an observation of the target runner's exact PowerShell/CLR versions or successful writer execution.

The Python wrapper retains the fixed System32 Windows PowerShell executable, NoProfile/NonInteractive flags, fixed UTF-16LE encoded script, copied child environment containing an absolute fixture path, captured output, 30-second timeout and a zero-exit assertion. Module autoload is disabled. Paths containing quotes, metacharacters, Unicode or newline text do not enter script syntax. No shell or module/cmdlet invocation is introduced.

The factory first requires a newly created directory, then performs the existing owner assignment and independent owner verification. After the writer, it repeats independent owner verification and the complete unchanged product custody check before any intended perturbation. A process success alone cannot award a baseline. An ineffective write, retained foreign entry, deny/null/unprotected DACL, changed owner, nonzero exit or timeout remains a setup ERROR and cannot match an intended negative predicate.

AST comparison confirms that `private()` is the only changed existing function and `set_private_dacl()` is the sole new function. All previous assignments, including the independent owner-query bytes, are unchanged. The fourteen case expressions and eleven negative reasons are identical after normalizing only the manual positive's descriptive label from "icacls protected DACL" to "independent protected DACL". Intentional Admin/Everyone grants and inheritance/owner/junction changes remain after their original preconditions. The manual positive remains independent of the product constructor; it does not call create=True.

The five-file tree diff proves that product custody, handle/identity/link/reparse/TOCTOU guards, the seven-field identity comparison, runtime/package, rehearsal, workflow, original budgets and native assertions are unchanged. This writer is only fresh fixture setup and is not promoted into a product guard or native custody proof. The builder, generator, rehearsal and workflow retain their previously reviewed SHA-256 values `1342d5c8…`, `0904a9bb…`, `59b0cc7d…` and `979bbd30…`; full hashes are in the machine receipt.

## Fresh verification

| Check | Result |
|---|---|
| Supplied fixture-specific methods only | 11 PASS, 0.154 seconds, exit 0 |
| Independent source/adverse methods | 7 PASS, 0.091 seconds, exit 0 |
| Exact five-file diff whitespace check | PASS |
| Candidate packet/diff/file pins and historical objects | PASS |
| Final checkout | Clean, unchanged HEAD/tree |

The supplied suite was imported without changing assertions or ROOT. Only its disposable TemporaryDirectory destination was redirected into this review directory. The selected eleven fixture methods are bound in the runner and receipt. No earlier accepted lifecycle suite or full 29-method suite was repeated. A pre-existing historical stage-B docstring SyntaxWarning did not affect the result.

Independent controls checked exact function/assignment/case preservation; static command and child-environment isolation; pre-existing directory/file/symlink refusal before writes; process failures against every intended refusal reason; zero exit still requiring correct owner and complete baseline; baseline-before-perturbation with no later replacement of the adverse ACL; and manifest/history/product-owner preservation. All ACL effects were modeled. No PowerShell, icacls, Win32 custody operation or native turn was invoked by the reviewer.

The author's newly reconstructed RED and GREEN logs were rehashed: eleven methods/17 failures in RED, then eleven methods/OK in GREEN. Their bytes match the author packet. These are fresh source verification records after the outage. Neither they nor this review establish the identity of the lost unpublished correction or recover its old log bodies.

## Nonblocking note I01

The opening Status paragraph of SOURCE_REHEARSAL_20261115.md still describes the fourth run and its one-command correction. Its fifth-run appendix and the current manifest accurately describe the new complete-DACL correction, source identity and pending Windows execution. Updating that opening paragraph during record integration would improve consistency. It does not overclaim readiness or weaken an execution gate and is not a source-publication blocker.

## Evidence and authority ceilings

The fifth run belongs to parent `c2faca3a…`, not this candidate. It retains successful Linux source modes and 25 methods, but ten Windows Creator Owner baseline errors. The complete Windows fourteen-case population remains unqualified. Earlier identity, wrong-owner and Get-Acl failures are not regraded. Detailed origin of the Creator Owner ACE remains uninferred.

The original 30373-byte fifth-run packet remains lost. Restored public archives and member bytes were independently verified under a new receiving receipt, without any further artifact download by this reviewer. Reconstructed source and current control logs have new honest identities.

Actual Windows execution and independent receiving of the new writer and all intended cases remain required. Final Windows location/package/tool identities, exact native operation receiving, fresh written owner grant, authentic A/B turns, independent post-A receiving, POST_B, T12 and original14/custodian requirements remain in force. Genuine native turns/appservers from this review: zero. Native admission and acceptance: false. Original fourteen UNKNOWN differences: fourteen.

## Primary API references opened

- [DirectorySecurity constructor](https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.directorysecurity.-ctor?view=netframework-4.8.1)
- [SetAccessRuleProtection](https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.objectsecurity.setaccessruleprotection?view=netframework-4.8.1)
- [Directory.SetAccessControl](https://learn.microsoft.com/en-us/dotnet/api/system.io.directory.setaccesscontrol?view=netframework-4.8.1)
- [FileSystemAccessRule constructors](https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.filesystemaccessrule.-ctor?view=netframework-4.8.1)
- [PowerShell 5.1 method syntax and native filesystem paths](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_methods?view=powershell-5.1)
