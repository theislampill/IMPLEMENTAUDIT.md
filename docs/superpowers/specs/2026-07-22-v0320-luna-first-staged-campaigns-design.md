# v0.3.2.0 Luna-only qualification and main-integration design

**Status:** owner-approved architecture; implementation authorized
**Author/provenance:** Sol
**Owner/source:** 2026-07-22 staged-execution decision and architecture approval
**Tooling baseline:** `52c4f2492a6ae9c80bc1ac8628ffffb85201f532`
(`3c33a970f3b2d528a989e0fb5e525ea9a8bdd0a4`)

## Objective and truth boundary

Qualify two separately frozen Luna campaigns and merge the qualified branches
to `main`:

1. B3-v4: six Luna missions and a create-once terminal result recorded as valid
   Luna 6/6 with the truthful cross-model boundary `INCOMPLETE_PENDING_OPUS`.
2. Candidate matrix: fourteen Luna fixture cells and a separate create-once
   terminal result recorded as valid Luna 14/14 with the same boundary.

Luna-only success is accepted qualification for the current integration goal,
not final cross-model or release qualification. It authorizes the planned
qualified-branch merges only under
`LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN`; it cannot authorize tag
movement, publication, or closure of a claim whose acceptance requires another
configuration.

No Opus work—execution, planning, packet completion, or host preparation—is
part of this instruction. Terra remains unauthorized. No Luna mission may
start until its packet, host and executable identities, authorization, runtime
roots, and launch command have passed deterministic validation and fresh
independent freeze review.

## Architecture

The implementation uses one small defensive lifecycle core and two separate
campaign contracts.

The shared core owns only mechanics that must behave identically:

- strict JSON and create-once writes;
- no-link, no-reparse, single-link regular-file custody;
- exact-byte and hash-bound surfaces;
- host-attestation binding;
- sequential prefix validation and gap rejection;
- terminal-state and stopped-prefix enforcement;
- no-silent-retry and attempt preservation;
- stage-pause creation and resume preconditions.

B3-v4 and the matrix remain separate in every semantic respect. Each has its
own versioned schema, packet, validator, campaign identifier and root, mission
identity grammar, acceptance composition, official result builder, independent
rederiver, and result schema. Shared lifecycle code must not decide fixture
properties, score evidence, compose campaign acceptance, or translate one
campaign's result into the other's.

The two independent rederivers are separate implementations and import no
official scorer, evaluator, runner, host adapter, or campaign driver. They may
use a narrowly audited byte-custody reader, but independently reconstruct
mission identity, evidence completeness, property/host/overall status, stage
prefix, and acceptance from retained raw evidence.

## B3-v4 contract

The current `implementaudit-b3v4-campaign-freeze-v1` hard-codes an interleaved
cross-model order and cannot express the approved Luna-only goal. It remains
historical tooling evidence and is superseded before any real campaign by a
versioned six-mission Luna schema. No result exists under the old schedule to
migrate.

The new packet fixes this six-mission order, preserving Luna's relative order
from the earlier preregistration:

| Index | Configuration | Arm | Repetition |
|---:|---|---|---:|
| 0 | Luna | candidate | 1 |
| 1 | Luna | control | 1 |
| 2 | Luna | control | 2 |
| 3 | Luna | candidate | 2 |
| 4 | Luna | control | 3 |
| 5 | Luna | candidate | 3 |
After mission 5, the driver refuses any additional mission. A separate
create-once Luna terminal binds the packet, exact completed prefix, all six
terminal records, all official verdicts, the Luna host and model identity, and
the Luna independent rederivation. Its successful evidence disposition remains
`INCOMPLETE_PENDING_OPUS` to avoid a false cross-model claim; its separate
`luna_stage_accepted` field may be true only for valid 6/6.

## Provisional candidate-matrix contract

The matrix uses a separate first-version schema and root. It evaluates only the
candidate product with Luna across fourteen primary fixtures; it does not
silently import historical candidate-versus-control comparison rules.

The frozen fixture order is the canonical order already preregistered in the
historical campaign intent:

`B0`, `B1`, `B2`, `E1`, `E2a`, `E2b`, `E3`, `E4`, `E5`, `E6`, `E7`, `E8`,
`E9`, `E10`.

Indices 0-13 are Luna in that order. This transparent ordering is fixed before
execution and is independent of the historical campaign's seed-shuffled
mission sequence.

After index 13, the matrix driver refuses another mission and requires its own
create-once Luna terminal and independent 14-cell rederivation. Successful
status is `INCOMPLETE_PENDING_OPUS` with a separately true
`luna_stage_accepted`; it is accepted Luna 14/14 but never a final cross-model
matrix claim.

## Packet-bound evaluated surfaces

Each packet contains a machine-verifiable surface manifest. Every entry binds
the logical role, relative or approved external path, byte length, and SHA-256.
Where Git identity is relevant it also binds commit and tree. The manifest
covers at minimum:

- candidate and, for B3-v4, control product payloads;
- all used fixture bytes and fixture inventory;
- scorer and evaluator code;
- official driver, host runner, adapters, and independent rederiver;
- prompt templates and rendered-prompt construction rules;
- model, reasoning, host, seed, ordering, and repetition identities;
- authorization acknowledgement and acceptance composition;
- lifecycle, verdict, evidence, and host-read contracts;
- actual launcher and native executable identities used by each host;
- formal host attestations and approved runtime/check-out topology.

Packet validation recomputes every local/repository identity. Production launch
also rechecks external and cross-host identities immediately before the first
attempt and after each attempt. A later merge may alter commit history while
retaining evidence only when a mechanical before/after comparison proves every
bound evaluated surface byte-identical. Any relevant difference invalidates
the affected tranche regardless of informal intent.

## Host, executable, checkout, and authorization closure

The existing preflights are inputs, not launch authorization. Freeze authoring
must resolve and independently review:

- the production Luna host attestation and its exact producer command;
- actual `argv[0]` plus transitive launcher/native executable paths, versions,
  and hashes—never a symlink standing in for the executed binary;
- fresh disposable candidate/control checkouts at exact commits and trees;
- a separate create-once runtime root for every attempt;
- cross-host Windows/WSL/native path translation and readback;
- the B3-v4- and matrix-specific owner authorization acknowledgements;
- the Codex authentication source path and copy boundary without logging,
  hashing into public artifacts, or exposing credential contents;
- `chatgpt-subscription` auth and `metered_api_spend: FORBIDDEN`;
- exact producer commands for packet, attestations, manifests, stage terminals,
  and rederivations.

Mechanically derivable paths and identities are resolved from live host state.
An owner question is required only if the remaining value changes model, host,
spending, acceptance policy, or another substantive authorization boundary.

## Attempt lifecycle and ANDON behavior

Every invocation advances at most one preregistered mission. Before host spawn,
it atomically claims a new attempt directory and records packet, mission,
product, fixture, host, model, executable, authorization, and contract hashes.
Every outcome receives a terminal record. No attempt directory, verdict, raw
bundle, stage terminal, or rederivation is overwritten or reused.

`FAIL`, `INVALID`, unexplained `ERROR`, substitution, custody or identity
failure, prefix/order/repetition failure, unauthorized mutation, or
official/rederived disagreement stops the affected campaign at that prefix.
There is no automatic retry. Transport failure is classified from retained
process evidence and never converted into a product verdict.

The convergence loop then records:

1. the concrete abnormality and evidence/claim reconciliation;
2. failure class and ANDON boundary;
3. 5 Whys or equivalent causal analysis;
4. shared-cause synthesis and hansei;
5. residual uncertainty and disconfirmation conditions;
6. deterministic RED before production change;
7. governing-cause repair, focused GREEN, no-regression/package gates, and
   independent exact-SHA review;
8. a new packet version and complete affected-Luna-tranche restart whenever a
   bound relevant surface changed.

Attempts from incompatible packet versions never combine into 6/6 or 14/14.
Fixture-name hacks, magic evaluation phrases, model-specific transcript
patches, acceptance relaxation, and post-hoc scorer weakening are prohibited.

## Historical re-adjudication lane

The 56 historical bundles inventoried under `cmp-fable-r2` remain immutable.
Re-adjudication reads each canonical raw `bundle` directory, verifies it against
the existing inventory, and writes a new append-only record outside every
historical run root. Original verdicts, sanitized derivative bundles, campaign
status, and historical 10/28 and 11/28 summaries are never overwritten.

Each corrected record binds source paths/hashes, old verdict hash, evaluator
and re-adjudicator identities, corrected layered result, causal classification,
uncertainty, and timestamp. The aggregate derives corrected candidate/control
baselines while preserving old and corrected views side by side. This lane may
run alongside packet preparation because it invokes no model and mutates no
frozen evaluated candidate.

## Luna-qualified integration certificate

Planned branch integration becomes eligible only when current compatible
packet versions prove all of the following:

- B3-v4 Luna 6/6 and matrix Luna 14/14;
- zero `INVALID`, unexplained `ERROR`, or substitution;
- complete custody, identities, order, repetitions, and stage terminals;
- official and independent Luna-only agreement;
- deterministic, package, CI, and independent-review gates required by the
  existing integration plan;
- a mechanical relevant-surface equality check for the proposed merged tree.

After the planned qualified branches are merged to `main`, the create-once
integration certificate records exactly
`LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN`. If conflict resolution or any
merge changes a relevant byte, the certificate is refused and the affected
complete Luna tranche must rerun on the resulting exact tree before the merge
is accepted. The certificate grants no tag, publication, release, or final
cross-model authority.

## Verification strategy

Implementation follows deterministic RED/GREEN slices:

1. shared lifecycle custody, create-once, prefix, stop, and pause primitives;
2. B3-v4 Luna-first schema/validator/driver/rederiver behavior;
3. matrix schema/validator/driver/rederiver behavior;
4. bound-surface manifest and mechanical invalidation;
5. host/executable/checkout/authorization preflight closure;
6. append-only 56-bundle re-adjudication;
7. provisional-integration certificate refusal and success cases.

Focused tests include order drift, early/late pause, missing/duplicate pause,
attempt after stop, hidden retry, incompatible packet mixing, cross-campaign
root confusion, fixture mismatch, executable launcher/native drift, parent
reparse/hardlink aliases, official/rederived disagreement, and relevant-byte
merge drift. The exact implementation SHA then receives the combined focused
gate, exactly one package/reproducibility invocation, and fresh independent
complete-boundary review before packet authoring.

Each authored packet separately receives deterministic validation, live
identity/preflight validation, hash manifest verification, and fresh read-only
independent freeze review. Only an explicit PASS for that exact packet and
launch boundary permits its Luna missions.

## Done conditions

This design is implemented when:

- both separate versioned campaign contracts and shared defensive core pass
  exact-SHA qualification;
- both fully resolved packets pass independent freeze review;
- B3-v4 Luna is durably preserved and independently rederived as valid 6/6
  with `INCOMPLETE_PENDING_OPUS`;
- the provisional matrix Luna tranche is durably preserved and independently
  rederived as valid 14/14 with `INCOMPLETE_PENDING_OPUS`;
- all 56 historical bundles have append-only corrected adjudications and a
  corrected baseline/causal summary;
- the planned qualified branches are merged to `main` with mechanically
  byte-preserving relevant surfaces and the disposition
  `LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN`;
- Opus work is absent from the current execution, and Terra, tag movement,
  publication, and final cross-model claims remain unperformed.
