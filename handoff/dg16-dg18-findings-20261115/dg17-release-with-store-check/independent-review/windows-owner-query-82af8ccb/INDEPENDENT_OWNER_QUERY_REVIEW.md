# DG17 independent source review — module-free owner query

## Disposition

**SOURCE_PUBLICATION_SCOPE_QUALIFIED. No blocking finding in the exact five-file candidate.**

The change is suitable for the root controller's already authorized guarded source publication and source-only CI. This review does not publish it, authorize a native episode, award actual Windows custody success, clear any original fourteen UNKNOWN differences, or close DG17/R0037. The direct .NET query still requires actual execution on the Windows source runner.

Reviewer: `/root/dg17_independent_review`, distinct from the source author, under root-reported current controller `pro-executor-01/G0004`. This is the owner-required independent source-engineering review, not an audit-assess lifecycle transition. An additional read-only API check by `/root/dg17_independent_review/owner_query_api_check` found no blocking issue; the principal reviewer independently inspected the source, opened the primary documentation, and ran the controls below.

## Exact binding and inspected population

| Binding | Value |
|---|---|
| Candidate commit | `82af8ccb20222ee9e667bb97494818d1b8853fb7` |
| Candidate tree | `7e084c97e6198856a055434221563ea8412e673a` |
| Parent commit | `c430ef8e5759bfd4eddff4c10b7ab2e442b6d60c` |
| Parent tree | `f87743459496d6a3bfe7d5bf5f8a3312eecfa0e3` |
| Published parent with the same tree | `5f90dd5ecf80ad2d3f153811348d5da72287c4da` |
| Checkout | `/workspace/scratch/0269e6626329/dg17` |
| Worktree status before and after tests | Clean, candidate HEAD/tree unchanged |

All five file diffs were inspected. Paths below are relative to `handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/`.

| Changed file | Bytes | SHA-256 |
|---|---:|---|
| `README.md` | 3995 | `30d5df37e88f2d165202f48bdf79990fcda2785aea404ddd56489c2f5f8d62fa` |
| `SOURCE_QUALIFICATION_MANIFEST.json` | 105703 | `e96074d2f5598208c63b0d437d73feedd6c48de16dc51c9d546ee0754b75c993` |
| `SOURCE_REHEARSAL_20261115.md` | 33185 | `b5bb731f0f428d16b75552c42277ab69942b92d78ee53eaadba1b4eb327890ff` |
| `tools/test_driver_bundle.py` | 26955 | `6655739d4e648ca82f5a095e6e3befd9de60b795e5ff911e614fe7915625b896` |
| `tools/test_store_custody.py` | 7326 | `de7e800bdc99a6e130cff94f1d60585f6f829d77ea601e4460ec90793a5efe5f` |

The manifest's complete file-pin population matches candidate bytes. Its new `third_ci_receiving` object equals the previously independently received 43,050-byte packet exactly after JSON parsing; the retained packet still hashes to `c7b2ef7e4bd10232e73f8c59ae5e956a86a5efd838b4fe038bdd943e517dc2e4`. The prior `second_ci_receiving` object is unchanged. New narrative and status fields preserve the failed outcomes and correctly describe actual Windows execution as pending.

## Source assessment

The observed Get-Acl/ConvertTo-Json dependency is removed from the fixed encoded helper. It sets `$PSModuleAutoLoadingPreference = 'None'`, reads the fixture path as an environment string, selects the directory or regular-file API using the Directory attribute bit, and requests only `AccessControlSections.Owner`. It obtains `GetOwner(SecurityIdentifier).Value` and `WindowsIdentity.GetCurrent().User.Value`, disposes the identity in `finally`, then emits two Console lines. No cmdlet, module import, dynamic expression, or interpolated fixture path is executed by that script.

Microsoft documents the Directory and File overloads accepting `AccessControlSections`, the Owner section, and the user SID property. Windows PowerShell is documented to use the full .NET Framework. These contracts support the source design; they do not observe the runner's exact PowerShell/CLR versions or prove host execution. The manifest correctly records those versions as unobserved. Primary references opened during this review are listed below.

Command construction retains the fixed `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`, an argument list with `-NoProfile`, `-NonInteractive`, and `-EncodedCommand`, UTF-16LE encoding, and a 30-second timeout. Paths are made absolute and supplied only through a copied child environment. Independent controls used quotes, wildcard characters, PowerShell metacharacters, Unicode and newline text in paths: the command bytes remained identical, and the parent environment remained unchanged.

The parser first requires a successful process exit, then exactly two lines with `S-1-` and nonempty ASCII decimal components. Matching SIDs satisfy the existing equality precondition; a different owner remains distinguishable and fails the current-user precondition. Query errors, missing/extra/contaminated output, non-ASCII numeric characters, timeout, absent executable, and denied execution remain setup ERROR outcomes with no recorded ownership precondition and no negative-control credit.

**Protocol precision:** this is a strict two-line, ASCII numeric SID-shaped protocol, not an independent implementation of every Windows SID numeric-range and component-count rule. The fixed producer obtains both values from framework `SecurityIdentifier.Value`; there is no user-selected producer. That distinction does not block source publication or broaden the evidence ceiling.

AST comparison proves that every fixture statement other than `OWNER_QUERY` and `owner_facts` is identical to the parent. All fourteen cases, eleven specific negative reasons, explicit owner assignment, private user+SYSTEM baselines, inheritance sequencing, junction preimage, and wrong-owner proof remain unchanged. The `.NET` owner observation is an ancillary fixture precondition. It does not replace the product's handle-based custody, identity, link/reparse, or TOCTOU protections.

The exact five-file tree diff proves the product, package/runtime, builder seven-field identity guard, rehearsal process restriction and failure preservation, and workflow are unchanged. In particular, the builder, generator, rehearsal and workflow retain these hashes:

| Unchanged source | SHA-256 |
|---|---|
| `tools/build_release_acl.py` | `1342d5c89dbe73bba4ddeec07bc2b7217ffe211f4d6405e3f80d4e617b6adc6f` |
| `tools/make_acl_stage_b.py` | `0904a9bb1c524a1b47d8b445d6951bffaf6c6822ee794ddfc15d88e57cab5cbc` |
| `tools/rehearse_lifecycle.py` | `59b0cc7daf8ffd65bbff00293b03235755a668e8b94254ff42f7c3075fb4cb16` |
| `.github/workflows/dg17-offline-lifecycle.yml` | `979bbd30e672da1175900244e02f0ff33a5de2657b39784572bd4b74dd812a28` |

## Fresh independent verification

| Check | Result |
|---|---|
| Supplied focused source/model suite | 24 methods PASS, 0.154 seconds, exit 0 |
| Independent adverse/source-integrity suite | 7 methods PASS, 0.099 seconds, exit 0 |
| Exact candidate diff whitespace check | PASS, exit 0 |
| Candidate and parent identities, exact changed population, manifest pins | PASS |
| Worktree/HEAD after both suites | Clean and unchanged |

The supplied suite was imported without changing source assertions or ROOT. Only its disposable TemporaryDirectory destination was redirected into this review directory. It built inert source fixtures and modeled Win32 calls; no Windows executable or native model turn was run. The supplied suite emitted one pre-existing SyntaxWarning from the unchanged historical stage-B docstring; all 24 tests completed successfully.

The seven independent methods covered exact source population; unchanged case/preimage AST; command and environment isolation for hostile-looking path text; malformed/contaminated SID output; process errors and timeout classification; preservation of different-owner distinctions across all eleven intended negative reasons; and exact historical receiving/manifest bindings. Test source and full logs are retained beside this report. The author RED and GREEN log bytes also match the manifest: 24 methods/errors=8 in the retained RED log, then 24 methods/OK in the retained GREEN log. Those author logs are corroborating evidence; the fresh independent runs support this review's test conclusions.

The full Linux lifecycle was not rerun for a fixture query change. No unrelated package gates were rerun because no runtime/package file changed. No artifact body was reacquired, no source file was edited, and no remote mutation occurred.

## Historical evidence and remaining gates

The independently received run `43678583519`, at published parent `5f90dd5e…` and tree `f8774345…`, remains overall FAILURE: Linux job `132704049669` succeeded; Windows job `132704049500` failed. Linux native-boundary, full simulated lifecycle, and blocked-hook containment/cleanup results remain earned only at that source identity (5.970368860, 9.624214375, and 9.561137405 seconds). No new lifecycle execution is claimed for this candidate.

Windows generated PINS and passed the unchanged identity guard in that run, then produced thirteen setup ERROR rows with zero verified preconditions because the Get-Acl module could not load. Only the missing-directory intended negative was qualified. The underlying module-load cause remains unknown. The earlier first-run seven-field identity refusal also remains unexplained; subsequent successful builds do not resolve its cause. The earlier seven Windows negatives intercepted by a wrong-owner predicate remain unqualified for their intended assertions.

Actual Windows query execution, all corrected fixture preconditions and intended refusals, final Windows location/package/tool identities, exact operation receiving, fresh owner grant, authentic selected Codex A/B turns, required independent post-A receiving, POST_B, T12 and original14/custodian requirements remain outstanding. Genuine native turns/appservers from this review: zero. Native admission/acceptance: false. Original custody UNKNOWN differences: fourteen. Root owns any subsequent guarded publication and source-only receiving.

## Primary API documentation checked

- [Directory.GetAccessControl, .NET Framework 4.8.1](https://learn.microsoft.com/en-us/dotnet/api/system.io.directory.getaccesscontrol?view=netframework-4.8.1)
- [File.GetAccessControl, .NET Framework 4.8.1](https://learn.microsoft.com/en-us/dotnet/api/system.io.file.getaccesscontrol?view=netframework-4.8.1)
- [ObjectSecurity method contract, .NET Framework](https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.objectsecurity?view=netframework-4.8)
- [WindowsIdentity.User](https://learn.microsoft.com/en-us/dotnet/api/system.security.principal.windowsidentity.user?view=netframework-4.8.1)
- [AccessControlSections](https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.accesscontrolsections)
- [Windows PowerShell and the full .NET Framework](https://learn.microsoft.com/en-us/powershell/scripting/what-is-windows-powershell?view=powershell-5.1)
- [PowerShell encoded command options](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_exe?view=powershell-5.1)
- [PowerShell module autoload preference](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables?view=powershell-5.1)
