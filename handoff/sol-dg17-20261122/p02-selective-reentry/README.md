# Original P02, B04 and H05 selective re-entry

The actual claimed task on `bb781f62f1e61542ad733e1b1b652d0831e2af24`, tree `fb3b9e0acd8185651abfeb305587315d05c1e670`, used controller `dg17-p02-final-isolated-bb` and claim `ce86223ad12fe935f740ddd40b0bc1be`. North, east and west actually completed their separate checks under G0001, at 2, 4 and 7 items. Verified G0002 anchored the completed plan before the dependency update. Only the west input changed. [Declared read sets](declared-phase-inputs.json) / [Initial phase results](initial-phase-results.json)

The shipped compiler read a closed request derived from the actual path-digest change and the predeclared phase inputs. It invalidated only phase 3, preserved phases 1 and 2, and selected only the reopened west phase in the second frontier. The actual governor consumed those outputs by reopening only the west roadmap row and specification, retaining the earlier west capture as history. Verified G0003 authorized that selected recomputation. The west check ran once and returned 8 on the new input digest. North and east did not execute again. Their inputs, phase specifications and captures stayed byte-identical. The authorization row and claim/controller binding bytes also stayed exact. [Invalidation](selective-invalidation-projection.json) / [Selection](reopened-frontier-projection.json) / [Actual consumption](replan-consumption.json) / [Recomputation](actual-recomputation.json)

The final governing record verified current G0004 and the full run-root validator passed. The three phase rows were complete and the audit object remained open. Earlier setup refusals remain distinct: the phase validator rejected two whole-output command forms before activation. A G0003 attempt refused abbreviated epoch-row pins and created no G0003 receipt. The exact anchors were corrected before execution. [Final observations](selective-reentry-final.json) / [Anchor refusal and correction](replan-anchor-repair.json)

| Submitted original predicate | Actual discriminator |
| --- | --- |
| P02 | Two unaffected completed phases and their exact evidence survive while the affected work recomputes. |
| B04 | Only the phase that reads the changed file invalidates and enters the fresh frontier. |
| H05 | Material new input reopens the west phase from a current completed plan while the run authorization and unaffected proof persist. |

These three predicates share one structural run. The compiler supplies a preparation decision from declared inputs. The actual governor consumes that decision and executes the selected work. The case supplies no native or model qualification, automatic effect authority, or overall audit closure.

The four phase output files store raw stdout as a JSON string. The declared SHA-256 values match those exact bytes, including their Windows line endings.
