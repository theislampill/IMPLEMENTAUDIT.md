# G132 exact supplied-source intake and existing offline operation

Actor: `/root/g132_existing_offline_intake`. Authority: local immutable-source intake and instructions to Root only. No native, protected, sender, provider, key, encryption, decryption, admission or acceptance action was performed.

## Actual operation completed

Read the complete published Fable README at `fee1768b449483843bb35ade23790d212b3abf0d`, the G132 state/instructions, original Root source receipts, the supplied source-selection and operator records, and the relevant existing consumers. The supplied worktree remained tracked-clean.

Unbundled the supplied Git bundle into the new isolated bare object repository:

`/workspace/scratch/0269e6626329/g132-host-intake.git`

It uses the existing local object store as an alternate for the already available prerequisite. There was no network access and no local or remote ref creation. `git bundle unbundle` recovered:

| Identity | Actual Git object |
| --- | --- |
| Host commit | `a33b8d1cdb967124b1b0d4fe877cf9b283304798` |
| Host tree | `e7b77a2e8cdf6d7409a694efcbb3b13483bac5c9` |
| Sole parent/product | `e76a07b2bae7c945e5a9d529ed8cf9069f4c9064` |
| Product tree, retained source record | `ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7` |
| Added host overlay | 49 paths |
| Ref population in new bare repository | Empty |

The bundle's published descriptor is 529,360 bytes, SHA-256 `1f79fa0c68da349e34e1d7d38ffb72cbabb82be33fd66dbb58779cb8808f3bda`. That prior export verification and the recorded 98-member operator qualification were not rerun. Object intake is not source requalification.

The exact published operator source is available at:

`/workspace/scratch/0269e6626329/fable-local-support/handoff/fable-local-support-20261115/dg16-g132-owner-local/public-operator`

## Original obligation and no new construction

No product code, test harness, wrapper, certificate or replacement mechanism was built. The original #209 criteria relevant to this existing route are **R35-Q06** (bounded governed live corroboration with required JOIN and recomputation), **R35-D05/D07** (exact consequential JOIN and current consuming decisions), and **R35-L04** (the actual decision-changing natural transition). The original criterion index at `585012cbc6b47cb332222c2784481567a482c8a5`, `recovery/contracts/original/R0035_209_CRITERIA_INDEX.md`, preserves those clauses.

Those clauses do not require a new offline test framework, a particular personal machine, certificate ceremony or 600-second implementation window. The owner separately requested one timed offline pass to prevent the known G131 operator delay. The command below uses the existing selected operator's offline mode for that bounded task.

## Existing offline mode, and its exact ceiling

`late-assembler-01/assemble_actual.py --preflight` is the existing concrete data-only endpoint. Its selected source SHA-256 is `1f7612be70f93aaa201c36c349a3ee2bb6610cbe1fcf37c6b73210a4ca65b9c3`.

It reads the existing selected phase, original source indexes, exact dispatcher source and the 11 retained private **source/evidence** inputs. It invokes the existing `L.stage` in memory. It does not invoke a sender, key, CMS operation, provider, control publication, native model or workflow. In preflight mode it creates no assembly/output directory and requires absence of live late-input/output options.

Its successful result is exactly scoped to `STATIC_SOURCE_PRIVATE_INPUTS_AND_DISPATCHER_RECEIVED`, with `late_inputs: FIVE_ACTUAL_ROOT_BODIES_REQUIRED` and `sender_started: false`.

**The existing operator has no complete offline live-chain switch.** The actual issuing, late assembly, dispatcher binding and publication stages require fresh live recipient/publication/Root bodies, the live deadline, and eventually a real `PAYLOAD_READY` sender outcome plus ciphertext. These cannot truthfully be supplied by the 98 public code files alone. The public export deliberately omits the original `SOURCES.json`, `PHASE.json`, late-stage metadata/index bodies and the 11 retained private source/evidence bodies. I did not invoke a knowingly missing-input preflight here, reconstruct those bodies, or read private inputs.

The original installed WSL source on 3701Media is the appropriate location for the existing `--preflight`. This is an input-location dependency of the selected implementation, not a newly asserted #209 acceptance requirement.

## One exact Fable operation

**To Fable on 3701Media:** execute this existing offline assembly preflight once in the original WSL `Ubuntu` installation as `agent`. Retain the stdout, stderr, actual exit code and elapsed time at the fresh timing directory below. Return those public result files only. Do not copy any retained input body, invoke a sender/provider/model, issue admissions or roles, create a recipient, push any ref, or proceed into the live chain. If the original installation is no longer present, report that exact first missing input; do not reconstruct it.

The following is a single WSL Bash operation; Bash's built-in `time` measures the actual existing Python call, with no additional Python harness or external timing package:

```bash
g132_timing=/home/agent/pro-executor-g132-offline-timing-20261115
mkdir -m 700 "$g132_timing" || exit 1
TIMEFORMAT='elapsed_seconds=%R'
{
  time /usr/bin/python3 -I -B \
    /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/late-assembler-01/assemble_actual.py \
    --stage /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/late-assembler-01/source-stage-01 \
    --host-phase /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/public-receiver-02/phase \
    --root-reader /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/public-receiver-02/author/receiver.py \
    --dispatcher-source /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/dispatcher-templates-02/bind_dispatcher.py \
    --private-inputs /home/agent/pr255-g132-root-20261114-01/public-tools-source-01/retained-final5f-private-inputs \
    --preflight >"$g132_timing/stdout.txt" 2>"$g132_timing/stderr.txt"
} 2>"$g132_timing/timing.txt"
g132_status=$?
printf '%s\n' "$g132_status" >"$g132_timing/exit-code.txt"
exit "$g132_status"
```

This timing measures the actual offline source-staging call. It cannot establish the duration of Root's future human/model/tool decisions, the 18 provider reads, the sender, or the five-write/six-readback publication. It must not be substituted for those live measurements or represented as complete G132 readiness.

## Root's own offline CLI step and the G131 separator

The existing `root-event-helpers-02/root_live_sender_call_received.py` exposes `command` and `helper-command`. They emit the frozen executable/argument selection with `actual_execution: false`; they perform no operation. Root can time its own real command generation once against the supplied file, without private reads:

```bash
TIMEFORMAT='root_assemble_cli_elapsed_seconds=%R'
time python -I -B \
  /workspace/scratch/0269e6626329/fable-local-support/handoff/fable-local-support-20261115/dg16-g132-owner-local/public-operator/root-event-helpers-02/root_live_sender_call_received.py \
  command assemble \
  --parameters-json '{"episode":"/home/agent/pr255-g132-root-20261114-01/public-tools-source-01/episode-01"}'
```

That command emits the direct existing `assemble_actual.py` invocation, including the actual fixed `--stage`, `--host-phase`, `--root-reader`, `--dispatcher-source`, `--private-inputs`, `--late-inputs` and `--output` layout. Do not execute the emitted live assembly command offline. It expects the five live Root bodies.

If the selected-source adapter is used instead of this direct helper, its `event_arguments` are positional `nargs='*'`. The live form must contain the passthrough separator:

`source_selected_event.py [actual selection/publication options] late-assemble -- --stage ...`

The missing `--` was the recorded G131 argparse failure. I did not rerun that failure or substitute an old result. Other helper command stages are `issue`, `dispatcher-selection`, `requirements`, `bind`, `publication-inputs` and `publication-config`; actual hashes/paths for those stages must come from their real preceding bodies, not invented placeholders.

## Protected and original-scope boundaries retained

- Pushing host ref `pro/dg16-g1-original-g3-32-20261114` is the protected launch. No such ref was created by this intake.
- Fresh live issuer/Root decisions remain separate from existing code or historical receipts. The selected operator still contains historical issuer constants; this intake does not impersonate that issuer or adopt those constants as PRO authority.
- G131 sender/recipient/cipher/journal/WRITE0 UNKNOWN effects remain untouched. No old grant or effect was replayed.
- The original G132 state records queued run `43098152901` as a noninterference matter; this intake did not cancel or relaunch it.
- G132's in-job G3 consumes G1-side evidence. It explicitly does not consume full G2 or grant `DG16_ORIGINAL_RECEIVING`. The separate final original G1+G2 consumption remains its own actual evidence decision.

## What this lane did not run

No dry-run/preflight, source qualification, regression suite, private-source read, grant, role/admission issuance, native/model turn, workflow, tool callback, encryption/decryption, publication or source edit. Root retains the once-only offline invocation and its own timing. The only execution beyond read-only inspection was local Git object intake into the isolated empty-ref repository.
