# Existing HostObservation representation: independent judgment

Status: SOURCE-COMPATIBLE REPRESENTATION AT THE EXISTING ORDINARY SCOPE. This is review guidance, not a live HostObservation, Root intake, actor result, provider attestation or positive admission of the R2 packet. The packet's overall disposition remains NEEDS_REVISION for the separate scalar/reader boundary.

## Judgment

The existing `tool_call_id` field can truthfully carry an explicitly typed actual task or operation observation reference. `root_callsite.py:93–100` checks that it is a string of 1–256 characters, checks sender and subject bindings, and retains a digest-bound nonempty capture. The JSON schema at `HostObservation` imposes the same string bound and no provider-specific identifier syntax. Neither source requires a native provider call identifier. The strict five-field observation shape remains unchanged; put a reference type in the reference string or in the captured evidence envelope, rather than inventing an extra top-level field.

This interpretation preserves the real provenance obligation. A reference identifies the actual observed operation or return; it does not itself authenticate a backend, model, native route or sender. Root must receive the actual evidence and its attribution at the layer the host exposes. A caller label or copied actor name cannot replace that receiving judgment.

## Actual exposed references and limits

| Actual surface | Representable reference | Evidence and attribution required |
|---|---|---|
| `collaboration.spawn_agent` returns a canonical task name | A typed dispatch reference derived from that exact returned task name and the actual operation | Preserve the actual invocation, complete submitted prompt/attachment population, and actual returned result. The task name identifies the route/target. It is not a separate provider call ID or proof of backend identity. |
| Actor-owned `exec_command` returns a chunk ID | A typed command observation reference containing that actual chunk ID | Preserve the actor-owned invocation and exact raw result, bind the actual decision artifact and its bytes, and retain the actor's actual return. Attribute it to the actor only when the observed tool ownership supports that statement. |
| An actual routed actor message/return has a task identity but no distinct provider ID | A typed return reference that explicitly identifies the actual task, operation/stage and bound returned content | Retain the complete actual routed return and the observation that attributes it to that task. A derived content/operation reference must be labeled derived, rather than presented as a platform-generated call ID. |
| Root reads an artifact or writes its own receiving decision | A typed Root observation using the actual exposed Root operation reference | Keep sender `/root`. Root's read establishes Root custody of those bytes; it is not an actor-origin command or a retroactive dispatch/return event. |
| `send_message`/`followup_task` yields an empty result | An explicitly typed actual send/continuation observation, if its actual invocation and empty result were retained | An empty result supplies no delivery acknowledgment. Retain its emptiness faithfully and require subsequent actual actor evidence for claims about delivery, reading or response. Do not manufacture success text. |

These are reference forms and evidence requirements, not populated operational examples. This review issues no actor, dispatch, return or Root observation IDs.

## Nonempty capture versus an empty tool return

The adapter refuses a `raw_result` file whose bytes are empty or whitespace only. That is an evidence-container check, not authority to invent a tool response. An explicitly described, lossless capture envelope may contain the actual operation, its actual arguments, attribution/capture metadata, and a field preserving the actual result exactly, including an observed empty result. Preserve any raw empty file separately as well. State the serialization and mark Root-authored envelope metadata as such. Do not relabel that metadata as provider output.

The resulting nonempty envelope can be bound under the existing `FileBinding`; the adapter does not parse a provider-specific raw-result format. The actual empty result remains empty. The envelope does not upgrade an empty send return into an acknowledgment, actor delivery proof, model response, or native attestation. If the host result or attribution was not observed, record that limitation and do not fabricate a substitute observation.

## Existing distinctions remain necessary

Dispatch, actor return and Root receiving observations must remain distinct at the actual operation level. The code compares reference strings, but different strings alone do not prove different events. Later receiving must verify the real operation, exact subject and origin. Initial and post-check actor returns must be separate actual observations from the same actor task; the rerun request must retain the initial actor return as prescribed by the unchanged adapter. Source review and Root source receiving likewise remain separate actual records.

Actor submission manifests must preserve the full actual attachment population, prompt, task inputs and command streams. A hash, task name or reference string alone is not delivery proof. The original oracle, sibling arm and engineering outcomes remain outside the actor-visible material. The code binds records supplied by Root; it does not supply the actor's reasoning or Root's semantic judgment.

No source/schema representation repair is required merely because this host lacks a separate provider call ID. The actual evidence may use the exposed typed references with these limits. The remaining scalar defect still requires its separate bounded repair before an operational source admission.
