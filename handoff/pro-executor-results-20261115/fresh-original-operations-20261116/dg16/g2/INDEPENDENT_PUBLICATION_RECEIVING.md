# Fresh G2 source — independent publication receiving

**PASS at ordinary source publication scope.** Reviewer `/root/dg17_recovery` independently received the current provider commit/ref/run state and all 12 published frozen bodies. The existing distinct G2 source and final issuer-binding reviews are reused; no semantic review, executable test or selected source operation was repeated.

## Exact publication and observed protected-ref state

| Binding | Received value |
| --- | --- |
| Ordinary source branch | `engineering/pro-g2-fresh-source-20261116` |
| Current commit | `acd060f7e0b989480b790d1db6ee257eb79be5c9` |
| Tree | `3cb0c2a425cc6ae5c374c7f538a845649aacbeb7` |
| Sole parent | `3312e5abfd1bbcf37feb22156598c2ba123c30d7` |
| Source branch runs | 0; empty workflow_runs array |
| Host22 ref | `pro/dg16-r5-full-g2-direct-host-22-20261116`: provider GET 404 |
| Control22 ref | `pro/dg16-r5-full-g2-direct-control-22-20261116`: provider GET 404 |

The source ref resolves to the exact received commit. Its tree equals the final frozen candidate tree and its only parent is the reviewed baseline. Both protected refs are observed absent through separate fresh GETs using the same repository connection that successfully received the published source. These are current observations, not a future launch/currentness guarantee. No branch or run was created by this receiving.

## Exact twelve-file parity

Every published body was acquired at the full commit ID and compared byte-for-byte with the final frozen worktree body, its byte/SHA-256 descriptor and its Git blob identity. All 12 match, totaling 204813 bytes. Their 100644 modes are bound by the exact final tree identity. The whole final tree, not only a selected subset, matches the independently reviewed freeze.

| Published path | Bytes | SHA-256 |
| --- | ---: | --- |
| .github/workflows/dg16-r5-full-g2.yml | 21355 | 44b303cae5f331cf1c4e62ac9b73dd1920772d6283b952b5dfd203a36cebbb0f |
| qualification/dg16-r5-full-g2-decisions/CURRENT_HOST_QUALIFICATION_REQUEST.json | 6667 | 00aab78961a5f881f640cf01b30f99bb56f4ed140ee565f9fb3f528637666bff |
| qualification/dg16-r5-full-g2-decisions/INDEPENDENT_COLD_REVIEW.json | 814 | 07b9bd19fa9664b8add24f8cd399a2c5af5ba1b428bca41fb20e823354c2b8b2 |
| qualification/dg16-r5-full-g2-decisions/NATIVE_INDEPENDENT_REVIEW.json | 2354 | 91ffbcf4d38d6ca3ae1de94b3c511a0905e64643c66d92c58b96c4a240e7e97f |
| qualification/dg16-r5-full-g2-decisions/ROOT_NATIVE_APPLICABILITY_ADOPTION.json | 2941 | 450691ab74c0eb260d916c8e547290d535e46adb183647e205b0b9d75baa0108 |
| qualification/dg16-r5-full-g2-decisions/ROOT_POLICY_ADOPTION.json | 2656 | 4117e70b14a41a275487eed912175671e7d8acea9bd173d1a37150708f913c70 |
| qualification/dg16-r5-full-g2/current_host.py | 15210 | 75f1aa8f88cce4af07631da254a90dd1f6d057cefac52bdd37605fc5c1574c71 |
| qualification/dg16-r5-full-g2/live_control.py | 10144 | e79abc5b2a85c49bc2bdcf89b8891d2fabec3c8ce5152e67dcddf620754b9fc4 |
| qualification/dg16-r5-full-g2/native_admission.py | 5484 | 5a7ace6c0921fa3ce6985347aebd6b9ff83116f9bcaac897ba905fb065a9f7ea |
| qualification/dg16-r5-full-g2/pair_driver.py | 48451 | 77ca44aa123167c4dbc5b6d35ba66d587e25f8e192db0bc8224b014f690bf174 |
| qualification/dg16-r5-full-g2/policy_control.py | 3878 | a73ed116b8debdb6268333aaf5c9e0d78f0ec17b010b396bc57d70bd7f16897e |
| qualification/dg16-r5-full-g2/run.py | 84859 | c93bf11715e40ed51b92f9463ed5c08710d500685384abc890043465f03e950a |

The four genuine independent review/Root adoption files also match their actual separately issued originals in the retained packet. This verifies publication of the actual bodies, rather than merely matching copied hashes or fabricated decisions. The current-host request remains the exact source-only Root request already received by the distinct reviewer.

## Existing reviews reused

- `INDEPENDENT_SOURCE_REVIEW.md`: 11572 bytes, SHA-256 `858ec7bc73aa630d5b2f63a73c0544bbfffe4b10381c750b7f800f90b5657ab0`; distinct reviewer `/root/g2_receiving`, exact source/policy PASS, no authority or protected result.
- `FINAL_ISSUER_BINDING_RECEIPT.json`: 2284 bytes, SHA-256 `f6f768880c7b8fb1d992d2c7d2e20e38a19433b5585a60fda0fbd713b2e0bbc0`; final 12-path/four-issuer-body PASS, exact final tree, original eight source/request bodies unchanged.
- `FINAL_PACKET_FREEZE.json`: 5990 bytes, SHA-256 `b368c6b53f9f5694200af04f3bdf8fc99b1ca32b3922e424c90c4b0f8032121b`; exact 204813-byte, 12-path final packet.

The final freeze's pre-receipt pending label remains historical at its issue time; the separately issued final binding receipt supplies the later actual disposition. This publication receipt does not alter either record or introduce a self-reference.

Maintained source remains `205aeab7c93299b0666b261485ab5658d8e183de`, tree `9ffbaf95080092bf4a45b8772a97ed16068544a7`. The adapter is SHA-256 `c93bf11715e40ed51b92f9463ed5c08710d500685384abc890043465f03e950a`; pair driver is `77ca44aa123167c4dbc5b6d35ba66d587e25f8e192db0bc8224b014f690bf174`. These match the exact reviewed final selection. No relation, native/currentness or resource predicate was retested or reinterpreted here.

## Retained provider originals

All 17 independent provider responses—commit, source ref, run list, two absent-ref responses and twelve file responses—are retained under `publication-acd060f7/`. `EXACT_PUBLICATION_COMPARISON.json` is 7966 bytes, SHA-256 `068e9b8ebbce1d415f19752edd2c87ab26307518df2afe543369c31704bf4baa`, and records each response identity and exact parity result.

Root's separate original publication record remains `ROOT_PUBLICATION_ORIGINALS.json`, 9482 bytes, SHA-256 `2c80bd5575562281b03bd4cfa0ebb3f0e0af920c2056bb0d01f463b5a602c2dd`. The independent current reads above supplement that original publication history without replacing it.

## Scope and remaining boundary

The ordinary source packet is published and independently received at its exact reviewed identity. It has not launched a fresh pair, qualified a current VM, opened a live review window, issued a control or earned original G2 acceptance. The prior actual G2 run and missing private normalized witness retain their original failure/retention scope; no computation was replayed and no private input was acquired for this check.

The explicit authority condition remains separate: a fresh exact owner GO must bind the applicable direct public-proof route under commission A.4/C.2, with private captures retained only within the live job and the unchanged genuine live proof review, separate Root consumption and closing readback. The bounded existing-record check is retained in `../g2-direct-proof-applicability/OWNER_DECISION_APPLICABILITY.md`, 7503 bytes, SHA-256 `0aad79522ec91a00ff95fee9bd14900ad8624bb47aed96a1425f7895311a64bc`. This publication supplies no missing owner decision and requires no new source programme. Root retains all external action and protected-operation authority.
