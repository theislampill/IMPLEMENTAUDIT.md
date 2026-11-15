# G132 frozen external operator review

**Disposition: BLOCKED_EXACT_OPERATOR_BY_STALE_RESOLVER_PINS. Authority: NONE.**

The reviewed operator is `OPERATOR_PINS.json`, 26,641 bytes, SHA256 `d818380a4c886f5c62ee25eb647a70307dd0c287c761b32ef192f61f2d32c77c`. All 141 indexed bodies match; all 142 files including the index are regular, read-only `0400` files. The selected-source body is 1,952 bytes, SHA256 `3ba27feca194e0ad36c8600756d3f74733f0b82385f69d24203c92e76030b77f`.

## One demonstrated defect, two consumers

The actual selected `public-receiver-02/author/resolve_artifact.py` has SHA256 `e42fa2108e726597b3fa478ecdb8cbb0b0fc06695b12d176fa3add93581e3149`. Two live publication paths still require its former SHA256 `377d0b056ac0a3ef2276bd093d32fc3a628d816e6c65ba012976fa0cf5e8188b`:

| Consumer | Exact affected read |
|---|---|
| `root-final-operators-01/root_pipeline_inputs_v2.py`, `publication_inputs`, line 237 | `read(RESOLVER, 1024**2, old_digest)` |
| `root-final-operators-01/binary_publish_v3.py`, `main`, line 222 | `read_exact(cfg['resolver_path'], 1024**2, old_digest)` |

The first consumer selects the current resolver path and propagates it into the binary publication configuration. The selected-source adapter does not replace either literal. The current body therefore cannot satisfy either hash check. This is a static source finding; I did not execute the live path. A scan of current non-template/non-phase Python consumers against all changed baseline body hashes found no additional stale-body references.

Root can correct these two demonstrated literals, propagate dependent pins once and freeze a new index. The affected source-read gates can then be received directly. The accepted suites and unaffected static preflight do not need repetition.

## What was received

The local baseline is `a2a590f4803e4ea86617cba64037b96cac380e64`, tree `63a25e4f941afabc1563b19a27a86ee8ba85276f`. Its operator population has 99 files. The current population preserves 54 files byte-for-byte, modifies 45 and adds 43; it removes none. The JSON report records the complete before/after descriptors.

The receiver source index binds the exact existing host review and genuine scoped Root receiving, and its copied phase plus all 59 members are byte-identical to the reviewed host `e81ffaf2959df5da5a6203b66b0b3e0819eae82c` / phase `06a1cd10de8c918e0e2f214cbadf43538f7bc7f2bd4d45e9e241e2aec44e3ae9`. I reused the completed host review and separate actual engineering-publication receipt; neither was changed. The 46-member Author index and 42-member template index match actual bodies. All 11 private inputs match the frozen input index and have `0600` files with `0700` directories.

The fixed selected-source adapter changes only its exact successor metadata requirement. It retains complete current source, phase and actual publication/ref/run checks. The other reviewed changes propagate current source bindings and the required `PRO-EXECUTOR-01, designated by owner` metadata without replacing native, source, effect or time guards. Historical PACKAGE and ACCESS09 evidence and the packages’ actual source205 identity remain preserved. Engineering publication is separate from the actual protected host event required by this adapter.

## Timing and launch limits

The retained raw logs and result descriptors agree: selected-source/eleven-input preflight exited 0 in **0.227281225 seconds**, and existing `assemble_actual --preflight` exited 0 in **0.157317952 seconds**, reporting 50 staged members and 11 private inputs. Both stderr bodies are empty. Those actions stop before the two affected late publication reads.

These observations measure local source and input preparation only. Live API and Root-chain timing remains unmeasured. Existing owner launch-go, prelaunch floor, actual queue/capacity, fresh event receiving and five actual future Root bodies remain required. This review does not supply them or make an original award.

Reviewer: `/root/dg16_m5_original_receiving`, requested and self-reported actual **GPT-6 Astra Pro**, independent of operator authorship. No tests/preflight were rerun; no source, provider, native, grant or future-Root-body actions occurred. The frozen operator remained unchanged. Output files are outside it.

JSON receipt: 31,948 bytes; SHA256 `5d3ec1ade8ada94290cb5e50076ffc8649b6b603bf11eec2d5eec851db7e1346`.
