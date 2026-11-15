# DG17 driver set with the store-directory privacy check (owner-approved conditions, 2026-11-15)

- `author/stage_b.py` (e551ef8e…) adds `private_store_directory()`, called directly before `02-owned-init`. It creates the store directory with the current user as owner and a protected DACL granting only the user and SYSTEM. It fails closed on a wrong owner, a missing or unprotected DACL, any other principal (read or write), any non-allow entry, a junction or reparse point, an existing path on create, or any unreadable fact. Administrators entries are tolerated but never granted.
- **Tests:** 13/13 on Windows (`evidence/STORE_CHECK_TESTS_13_OF_13.json`). A wrong-owner case was not tested, because it needs elevation.
- **Combined check by Opus:** this driver check together with the adapted packaged `host-session-binding.py` from commit 158a16d2 gives init READY. The unchanged packaged file still refuses on Windows. See `evidence/OPUS_COMBINED_RESULT.txt`.
- **Contract:** none of issue-209, issue-211 (R0037) or r0035-r0039 requires the permission guarantee to sit inside the binding component.
- **Operation record:** `OPERATION_A.json` 49981532… (the case path and all limits are unchanged; pins are in `PINS.json`). Its paths bind the scratch author folder, so Root must rebuild it with `tools/build_release_acl.py` at the final location, which changes the hash.
- Not Windows ACL parity or general Windows security. It is a host-admission check for this isolated DG17 test.

## Source-only successor qualification

`SOURCE_REHEARSAL_20261115.md` records the portable rebuild, complete pin
forwarding, strict user+SYSTEM successor guard, Stage A parent-command repair,
focused controls and the remaining host/acceptance boundaries. The author set
and Windows evidence above remain historical inputs. The revised generator
requires explicit `--source-root` and `--output-author` arguments and never
grants native admission.

The first source-only CI run, 43675846002 at published commit 52065bcee405715a2fc31d78b3aefd2958ba96a0,
is received with both jobs failed. Linux Stage A steps 01–10 reached the explicit
native boundary; the full fixture then exposed a process-guard argument/data
mistake, and Windows stopped at an unresolved lstat/fstat identity comparison
before store tests. The report preserves both failures, exact artifact and
generated-source identities, the focused harness correction, and the unchanged
Windows refusal with bounded diagnostics. Complete lifecycle and Windows
qualification remain pending independent review and source-only CI; no native
authority or custody difference changes.

The second run, 43677179224 at 0d262630b826ecf634a44e3b8b9535b46a6dc14c,
passed all three Linux source-only modes. Windows rebuilt successfully under the
unchanged identity guard, then exposed an icacls fixture that left the owner as
Administrators. Its reported 14 cases/1 failure include seven negative cases
intercepted by that wrong-owner predicate. The report records them as unqualified
and describes the fixture-only repair: explicit owner assignment, independent
SID readback, positive preimages and specific refusal reasons. Actual Windows
verification of that repair remains pending; the earlier identity refusal is
still unexplained and no product guard is relaxed.

The third run, 43678583519 at 5f90dd5ecf80ad2d3f153811348d5da72287c4da,
again passed the three Linux modes and the Windows rebuild. Its Windows fixture
query could not load the PowerShell module supplying Get-Acl, so 13 cases are
ERROR and remain unqualified; only the missing-directory refusal was reached.
The next local fixture correction uses documented direct .NET owner access,
disables automatic module loading and strictly parses two SID lines. It keeps
all ownership/preimage/refusal checks and awaits distinct review plus actual
Windows execution. The exact failed run is retained in the source report and
receiving manifest; its underlying module-load cause is not inferred.

The fourth run, 43679794953 at 50c7fd7e279cd1f97345941d1ef13d6d76412cd8,
passed the Linux modes and demonstrated successful direct .NET owner readback
on Windows. Ten fixtures then reported ERROR at a remaining Administrators allow
ACE in their private baseline. The next fixture-only correction removes that
observed grant before the complete baseline and before any intended adverse
grant. Local controls pass; all 14 Windows controls still require distinct
review and actual execution. Every previous failed result remains preserved.
