# G132 Linux dispatcher acquisition: independent static review

**PASS at the existing external Linux transport scope.** Reviewer `/root/dg17_recovery` read the exact narrow diff and performed static string/AST inspection only. No transport helper, dispatcher, product owner, provider call, rehearsal or live operation was executed.

| Subject | Bytes | SHA-256 |
| --- | ---: | --- |
| `LINUX_DISPATCH_TRANSPORT.js` | 3,752 | `9a35f3538fec80cfbc5f24c8740b156c12c674d40f50479e873ecf53fa2a2112` |
| `LINUX_DISPATCH_TRANSPORT_UNEXECUTED_PREDECESSOR.js` | 2,499 | `4bb5eceec5ac0d1d3db9a38764b6135f16b65a4d42fb9779f02ebb7b02ac145a` |
| Exact loader extracted from the unchanged dispatcher template | 814 | `510be231714523e26f77bdd26f28089aa2782e6d4118eb4841784ec67cc074e7` |

The correction removes the file-derived descriptor/weak length test. The caller must now provide exactly `{bytes, sha256}` from the actual pinned binder result or its independently received `INSTALL_MANIFEST.json`; positive bounded integer size and full SHA-256 syntax are required. The existing binder records the descriptor of its actual bound `dispatch.js` in that manifest. The function does not infer that provenance from a readback: Root's actual selection remains part of the existing invocation contract.

The acquisition reader retains the exact loader's regular-file, single-link, effective-owner, read-only-mode, bounded-size, no-follow/nonblocking/close-on-exec open, descriptor identity, no-xattr, exact pinned hash and closing identity checks. It performs one physical read and holds those verified bytes. The only removed loader suffix is the final argument setup and `exec(compile(...))`; it is replaced with JSON export of the held source, byte length and hash. Static parsing of the resulting reader confirms no `exec`, `eval` or `compile` call remains. It does not invoke `dispatcher_entry.py` or the JavaScript driver during acquisition.

A nonzero/incomplete acquisition refuses. The JavaScript side requires the returned size/hash to equal the independently supplied descriptor and requires a source string before constructing/executing the dispatcher. It executes that held string without rereading or rewriting the file. Invalid or truncated JSON cannot reach driver execution.

The 2,212-byte suffix after `const forwarded=[];` is byte-identical to the unexecuted predecessor. The strict whole PowerShell literal grammar, fixed WSL prefix, selected Linux interpreter/loader/helper pins, permitted helper actions, complete argument quoting, actual tool-result forwarding and unchanged sequential eighteen-read driver therefore retain their prior scope. This review introduces no new transport or operator behavior.

Root separately confirmed that its actual stored `G132_LOADER` equals the exact template loader. The delegated review store does not expose Root's stored value; this report independently verifies the template and transformation, and attributes that runtime-store comparison to Root. The helper's suffix-shape check alone is not a claim to authenticate arbitrary replacement loader text. Its use remains bound to the already selected exact loader, as required by the existing transport contract.

The predecessor remains explicitly unexecuted. This external boundary file and review are outside the 144-member operator closure, so no source/index changes follow. This PASS supplies no live interval, sender admission, protected launch, retry or original acceptance.
