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
