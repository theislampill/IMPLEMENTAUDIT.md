# A4 actual memory failure diagnosis

Run44826546712/A1/job136600491721, workerPID8168. Exact1957965-byte raw artifact SHA-256 `d1e6fe87bed955906d6a79736de2fcd1bd69cca9063ccf70bb60b5ade38ea133` was read without modification. Diagnosis authority NONE; independent receiving is separate. No source edit, provider write or original replay occurred.

## Proven failure mechanism

The64MiB guard reads **lifetime peak**, not current working set. The new worker exceeded67108864bytes during case14's setup, before the later archive cases began. Its peak remained above the bound thereafter, so their refusal is the guard's correct behavior. Original24SUCCESS/1optionalSKIP/3ERROR outcomes remain unchanged.

| Actual boundary | Current bytes | Lifetime peak bytes |
|---|---:|---:|
| After four initial module imports, sample9 | 36229120 | 42668032 |
| Before case14 setup, sample144 | 52330496 | 65744896 |
| After case14 setup, sample145 | 51499008 | 67588096 |
| First archive method entry, sample272 | 52080640 | 67735552 |
| Final owner method entry, sample328 | 54366208 | 68100096 |

The first crossing interval is22:09:54.266394900–22:09:54.438509100UTC,172114200ns, between samples144/145 around `GitObjectCustody.test_wrong_type_and_size_are_refused._callSetUp`. First excess:479232bytes. Every sampled current working set stayed below the limit; the maximum was58462208bytes. Earlier original native-memory test passed with peak62832640bytes. Thus initial imports and later archive generation cannot be identified as the first crossing.

## Concrete allocation mechanism and remaining uncertainty

The authentic windows_custody_test.py setup freshly loads claim-run-rotation.py and canonical_custody.py, then runs git init. The only captured command in this interval is00016, git init -q, exit0, with empty output. There is no recorder snapshot call between the lifecycle samples; source inspection shows the original setup and its delegated command/assertion recording.

The291693-byte claim owner performs a second full compilation of its own source in `_capture_claim_load_identity_v1`, then compares that code with the executing module. This is an exact-source safeguard, not removable overhead. Both source loading and that comparison recur in setup. The exact claim body was recovered from its retained content-addressed blob; its SHA is `9eebc5d5e57b47b0e4b4a2a846de1c0b55407713e14008a6de4d01e7a8c5e19e`.

A pure compile-only control on these bytes, without execution/import, measured18901353bytes traced transient allocation for compilation and18657905bytes for recompilation while retaining the first code object. This LinuxPython3.12.14 control identifies a concrete large allocation mechanism; it is not Windows3.12.10 native proof of the precise crossing allocation. Native samples bracket setup, not individual compiler calls. Observer overhead is included; R3's historical peak remains UNKNOWN. The narrow unresolved question is which setup allocation produced the maximum, not whether the later archive guard failed correctly.

## Minimal repair candidate and qualification boundary

Target capture-adapter compilation overhead while preserving the product and original test bodies. A bounded exact-source compilation memo could reuse immutable compiled code while executing each fresh module namespace normally. It must preserve fresh physical-source reads, all code/source comparisons, filename/flags/optimization semantics, source-change refusals and the fixed28-case order. Reusing module state or replacing the executing-code comparison with a sampled disk hash is invalid. This candidate is not adopted or claimed fixed.

Before another original run, independently qualify exact byte/code equivalence, changed-source and stale-code refusals, distinct module globals, exact traceback filenames, bounded cache population, and unchanged native guard/Job/cleanup. A small native compiler-boundary discriminator or meaningful controlled equivalence result must resolve the remaining allocation/compatibility risk; another unchanged28-case retry supplies no new answer. NoGC, threshold change, baseline subtraction, case reordering, or retained-process release is proposed.

Evidence: complete bounded trace/source reads edda5f/0 and145bb8/0; pure compilation control and342-record/PID/monotone-peak verification c22fa0/0; current-versus-peak check d21bc8/0. FINDINGS.json retains exact sample identities and controlled compiler measurements. A4 remains unawarded.
