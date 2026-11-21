# G132 R2 independent bounded source review

**Source disposition: PASS.** G132-SRC-01 is repaired for prospective source qualification.

**Authority: NONE.** This review returns advisory source findings to Root. It does not confer native qualification, original acceptance, publication authority, active host readiness or current live custody.

## Exact subjects received

| Subject | Seal bytes | SHA-256 | Verified members |
|---|---:|---|---:|
| R2 source packet | 11,407 | `f1c00308dbd8e8343ab7c04b927067be09216c29a7da9a7e2ec48ee2aeb495f4` | 44 / 1,279,706 bytes |
| Frozen R1 source packet | 13,566 | `b2212fa07731baa3930c2a2a2fedc060a40c91a69d482b7a60a7a945fab40920` | 53 / 3,293,613 bytes |
| Frozen independent R1 review | 1,997 | `cf382ae787b964e39c11acf06e7c4e091991b35860f7df68e4c8433c63c68929` | 6 / 44,119 bytes |

Opening and closing checks matched every listed member's byte count, SHA-256 and Git blob identity. R2's retained predecessor copies also match the original frozen subjects.

Independent static receiving completed at **481b66 / exit 0**. The reproducible checker, opening/closing records and results are retained beside this report.

## Finding disposition: G132-SRC-01 repaired

R2 adds exactly `R5_GIT_08CA_SOURCE_REVISION` to the existing `_Engine.load` membership guard at line 435. The original four members remain in order. The validator call, its arguments and the entire `validate_git_directory_selection_v1` body are unchanged.

Whole-file comparison proves that this membership addition is the loader's only R1-to-R2 change. The complete setup body differs only in `HOSTED_R5_GIT_08CA_LOADER_PIN`, which now matches the repaired loader. Earlier source selection, source capture, digest checks, setup admission branches and closing-currentness checks are unchanged.

| Changed product source | Bytes | SHA-256 | Git blob |
|---|---:|---|---|
| `scripts/load-work-graph-c5-executor.py` | 58,046 | `07f7275394e818cb0b05bf47dcde588b0f1a51e4275022b0649f0e6d50d7cd85` | `17dd165ee3ff2040bade29a7060d0a587acc5f74` |
| `scripts/qualify-work-graph-c5-setup.py` | 83,152 | `2dd699956d7b59eacd4a3f092e526047f0f4d89d0f7420edc9e8de093f5bd92c` | `d96e1634778562a78c2e36f61f8adf9801549913` |

No additional finding arose in this bounded delta.

## Focused controls received

The actual retained RED receipt **13cf0a / exit 1** records four controls with two expected failures: the successor did not call the validator, and the contradictory inventory did not propagate the validator's refusal. The prior-revision behavior and unchanged-validator checks passed.

The actual retained GREEN receipt **2d7728 / exit 0** records the same four controls passing after the repair. Inspection of `test_validator_dispatch.py` confirms that it extracts the actual load-method guard and unchanged pure validator. The repaired guard calls the validator once for the exact successor, propagates its contradictory-inventory refusal, and preserves other revision dispatch decisions.

These are bounded source dispatch and refusal controls. They do not instantiate `_Engine`, execute an original owner or establish whole-engine malformed-source acceptance. This reviewer read the receipts and control source without rerunning either these controls or the retained R1 ten-control suite.

## Dependent closure and unchanged scope

Independent byte/AST comparisons establish:

- The executor and execution-selection fixture are byte-identical to R1.
- All three separate unissued host inputs are byte-identical to R1.
- The deterministic builder differs only by the exact required guard splice.
- Every current product and host-input descriptor in the manifest matches its materialized body. Original paths, modes, change classifications and baseline descriptors remain intact.
- The candidate plan differs only in the two changed product descriptors and the dependent loader admission.
- The thirteen-entry expected Engine map differs only in the loader descriptor; its separate setup descriptor also matches the new setup body.
- All retained baselines, observation bytes and predecessor evidence used in this delta agree with the frozen R1 subjects.

The existing R1 assessment remains applicable to unchanged source bytes. The R1 finding remains historically GAP; this separate R2 review supplies the bounded repair disposition.

## Limits and Root-owned next action

R2 continues to declare no new product commit/tree, no actual Engine loading, no native qualification, no active host composition and no original awards. The actual Engine map, changed-selection applicability, Root admissions and complete peer/carrier/bootstrap/workflow closure remain unissued. Missing historical author helpers remain a disclosed later composition dependency.

Existing M2/M4 and scoped M5 results stay with their prior subjects. No G2 rerun or protected operation is authorized here. Original01 remains `SPENT_NO_RETRY`; historical301 remains `UNKNOWN_NO_REPLAY`.

Root may use this PASS in its own receiving and source-publication decision for the exact R2 ordinary source candidate. The reviewer performed no candidate-code execution, Engine/native/original launch, provider mutation or Git write.
