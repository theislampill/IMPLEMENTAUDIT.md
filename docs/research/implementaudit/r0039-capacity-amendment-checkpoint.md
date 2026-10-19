# R0039 / #215: prospective capacity amendment recovery checkpoint

Date: 2026-10-19 UTC. Existing draft PR #249 remains open and non-closing.

## Exact shared-owner proposal

The owner approved a prospective increase to **393,216 bytes per compressed artifact**, retaining the mandatory **2,000-byte reserve**. The accepting maximum is **391,216 bytes**. This is a new revision-2 decision; the original R0021 declaration and historical failures retain their original meaning.

This checkpoint publishes the separate proposal as a recovery patch. It does **not** apply competing package/shared-owner production writes to the issue-only PR. The designated package/shared integration owner must adopt it through the existing conductor route.

| Identity | Value |
| --- | --- |
| Proposal base commit | `685ef15f55f0a9ed33b8e82cbed93acb7c50ab47` |
| Proposal base tree | `ba6bfe1437770ec0cd7f1a18ebcfd0a62a740e4b` |
| Separate local proposal commit | `acd3b11bb2d792df8ac9f6279b910599351442a3` |
| Separate local proposal tree | `8bdbcff57016866dfe8320088e0d6a93253094b3` |
| Recovery patch SHA-256 | `695cd180575e2e7b7b5819a3277cae90b4205541961611ac6f95d189b7ed1727` |
| Owner approval text SHA-256 | `c5575774aae04aeb65de98390831e76c9971da570dc60f0b4eadad2aa2da1582` |
| Measured complete local commit | `a4f4b0c104f3c03fd2ce4da689279af140b58d86` |
| Measured complete local tree | `a7646b3df5a7282610bc1b4bcaef1be900dee772` |

The recovery patch is retained losslessly as [r0039-capacity-amendment.patch.b64](r0039-capacity-amendment.patch.b64). Decode it using the guarded command below; the decoded bytes retain the exact patch SHA-256 above. It contains six modified files and one new source-controlled owner approval. Its complete-file Git preimages and postimages must match before serial adoption; no fuzzy application is authorized. The sealed original source/shared transport supplies the base. The final owner return supplies whole-file images, SHA-256/mode bindings, reverse patch and verification receipts.

The measured complete commit preserves the previously completed, separate fixture correction from `541f5fe0b0b770969e9d6dd5b35d7c3ef5650faf`. No LR10 writer probe was repeated.

## Implemented change

The canonical JSON declares prospective budget revision 2 and retains the exact original R0021 budget objects under `budget_history["1"]`. The central verifier pins the revision, approval identity, history and current budgets. One shared size function enforces both the cap and reserve for real artifact verification and the size-check CLI; the existing installers delegate to that verifier. Original CLI refusal ordering is preserved.

The active contract, plugin release and standalone release tests now use the approved budget and reserve. The historical release policy and forecast values are retained. Two heldout diagnostics describe cap/reserve failures without changing heldout behavior. No runtime, compressor, installer transaction, membership, integrity, currentness or rollback implementation was weakened.

## Verified at this checkpoint

The focused regression first failed under historical production because 391,216 exceeded 327,680. The final contract bank passes, including both artifact roles at 391,216 accepted, 391,217 reserve refusal, 393,216 reserve refusal and 393,217 cap refusal. Missing/reduced reserve, substituted approval, changed/missing history and unapproved/missing revision are rejected.

The official complete-source build completed with exit 0 in 9.584 seconds and produced the canonical two-entry checksum manifest:

| Artifact | Actual bytes | Headroom to cap | Headroom after reserve | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `IMPLEMENTAUDIT.plugin.zip` | 361,360 | 31,856 | 29,856 | `98690224e6fe4948538542b11519fa397eec4250a339c892dc12b1a1b28df321` |
| `IMPLEMENTAUDIT.skill` | 357,131 | 36,085 | 34,085 | `861569dfcc95e436a6b046fb4138ee22a85770927d42f00d4170fea1f0b8af7e` |

Both embedded inventories bind the clean measured complete commit/tree above. The existing isolated plugin install bank passed in 17.417 seconds. Remaining affected package, standalone-install and independent final review results were still being collected when this early checkpoint was published; the final owner return will bind their terminal results.

## Preserved limits and accepting continuation

No historical RED result becomes PASS. The original complete-package failure remains evidence against its original 327,680-byte cap and reserve. The passing build above belongs solely to the prospective amended subject.

Checked official numerical distribution limits do not prohibit 384 KiB: GitHub release assets must be below 2 GiB; the OpenAI plugin ZIP submission limit is 100 MB; Claude Code hosted archive downloads allow 256 MiB. These are route-specific documentary findings. The individual Claude custom-skill upload pages reviewed do not state a numerical cap, and native import/discovery/invocation remain unverified.

References: [GitHub release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases), [OpenAI plugin submission limits](https://developers.openai.com/plugins/deploy/submission-errors), [Claude Code hosted archive limits](https://code.claude.com/docs/en/plugins/host-marketplace), [Claude custom skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

The LR10-C historical `.controller` writer event remains **GAP-REVISE**. Further writer engineering is **deferred by owner** until the filesystem/runner owner provides writer provenance or a reliably reproducing case. This does not withdraw or reinterpret the earlier fixture correction.

The designated owners must integrate the current commissioned source implementations, then measure the complete shipping population and reassess package size before final combined acceptance, release or dependent issue closure. Native acceptance, shared-owner integration and other original R0039 requirements remain applicable. No merge, closure, release, native activation or protected campaign mutation is represented by this checkpoint.

## Recovery representation correction

The first checkpoint, commit `0522ad693bb95fe64194cbe824413f0ec1b5632b`, stored the literal unified diff. Hosted workflow `39278536572` failed its whitespace gate on fourteen blank context lines in that documentary file. Those single-space lines are valid patch syntax. This successor stores exactly the same patch bytes in Base64 so the ordinary whitespace check can remain unchanged. The source proposal, whole-file images, measured complete tree and package bytes are unchanged. The original failure is retained.

Decode from the repository root into a new output file (the command refuses to overwrite an existing file):

```sh
python3 - docs/research/implementaudit/r0039-capacity-amendment.patch.b64 /tmp/r0039-capacity-amendment.patch <<'PY'
from pathlib import Path
import base64
import hashlib
import sys
encoded = Path(sys.argv[1]).read_bytes()
payload = base64.b64decode(b"".join(encoded.splitlines()), validate=True)
assert len(payload) == 22937
assert hashlib.sha256(payload).hexdigest() == "695cd180575e2e7b7b5819a3277cae90b4205541961611ac6f95d189b7ed1727"
with Path(sys.argv[2]).open("xb") as output:
    output.write(payload)
print(sys.argv[2])
PY
```

The designated owner must still verify the complete-file preimages and modes before `git apply --check --index`, then verify postimages after serial adoption. Decoding does not authorize applying this shared-owner patch to the issue-only PR. The source transport supplied in the owner return also contains the unchanged ordinary forward and reverse patches.
