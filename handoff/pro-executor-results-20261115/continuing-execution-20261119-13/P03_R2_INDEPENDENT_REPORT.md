# DG17 P03 R2 independent affected review

**Disposition: NEEDS_REVISION.** The exact revised packet closes R1, the originally identified CR/LF/pipe defect within R2, and R3. Its concrete Root-owned capture plan closes R4 at preparation scope. One related source boundary remains: the six scalar guards/schema still admit non-CR/LF characters that the existing recorder table reader treats as line separators. A minimal accepted `reason` value, `"abc\u000bdefg"`, yields five cells rather than eight in that reader. This is a bounded record/consumer round-trip defect, not evidence of a live episode, controller failure or LF rewriting. [S01–S06; E01–E04]

**The actual tool-observation interface can use typed references exposed by this host.** The existing opaque `tool_call_id` field does not require a separate provider call ID. Actual canonical task/operation references and actor-owned command chunk IDs can be represented truthfully with their real captured evidence and attribution limits. No new provider/native identifier gate is warranted. See the detailed representation judgment below and `HOST_OBSERVATION_REPRESENTATION.md`. [S01 `observation`; S02 `HostObservation`; S07; E05]

This review does not issue a positive source-review intake projection. It supplies no Root intake, live observation, original F1 discharge, whole P03/DG17 award, M01/N06 qualification, native Stop/M4 evidence, release or closure authority.

## 1. Review identity, independence and scope

The reviewer is `/root/dg17_p03_source_reviewer`, the same independent reviewer that issued the immutable first NEEDS_REVISION report. The exposed developer identity is **ChatGPT, GPT-6 Astra Pro**. The exact requested backend model identifier is not exposed; the agent inherits the parent selection. No provider/native identity attestation is claimed. The reviewer retains its own previous review context and the actual author revision packet as evidence, without adopting the author's disposition or sharing authoring authority. The original review remains unchanged. [S28–S30; E01]

This is an ordinary source/evidence review. It is not an internal `audit-assess` route or any other formal/native child route. The supplied implementaudit spine and applicable review/resource guidance are context for independence and evidence bounds; they do not authorize this reviewer to impersonate Root or operate a controller. Root's supplied `G0010@96a7e58242ddedcf281d6f5b1703a44dc529d896` is caller context only. It is not this reviewer's currentness result and cannot substitute for future per-effect currentness. [S18–S21; S17]

All writes for this review are confined to `/workspace/scratch/2678f1e431c3/dg17-p03-ordinary-r2-independent-review-20261119`. No source file, earlier packet, existing review, shared Root state or task repository was edited. The reviewer did not run an actor, provider call, live host/native call, controller command, currentness helper, original workflow or complete source test suite. The only source execution was one disclosed isolated scalar-boundary probe: it called the exact validator, the local recorder in a new review-owned directory, and an AST-extracted pure existing row reader. It did not call `admit`, invoke subprocesses or perform live admission. [E01–E04]

The current resource census exposed four running agents, filling the available four slots. This bounded affected review proceeded serially; no supporting reader or additional actor was dispatched for R2. The earlier review's supporting reader remains historical evidence only. No actual Root STATE/ROADMAP bytes were read or fabricated here.

## 2. Exact inputs and complete census

The independent verifier checked every revised direct member, both controlled trees, exact literal symlink targets, exclusions and total population. It independently rehashed the original review, both earlier packets and installed governor against the first review's complete census. It also checked the new lineage and freeze records, unchanged contract copies, corrected recorder and primitive, source AST delta, old test-method identity, retained logs and the complete final command-capture population. It did not execute the author's verifier or its source tests. [E01; S23–S27; S29–S31]

| Population | Independent result |
|---|---|
| Revised direct manifest payloads | 44 files, 538,830 bytes; all match |
| R2 RED controlled tree | 2,777 entries, 2,146,067 bytes; census `b3746b52a285b8b46b98f2e8d6ee7c6370cdcc37fd38666fc93481671e44de7f` matches |
| R2 GREEN controlled tree | 2,654 entries, 2,084,955 bytes; census `65367698762f8299364c0b0e0764be5f60fce54ce75fb7cf4ee81847ecdc8e60` matches |
| Complete revised packet | 5,478 entries including the manifest and two terminal receipts; exactly two declared negative TASK symlinks |
| Original independent review | All 26 files unchanged, including its NEEDS_REVISION result and actual receipt |
| Prior ordinary integration | All 9,194 files unchanged; every retained RED and GREEN remains |
| Prior recorder revision | All 263 files unchanged, including frozen oracle and prospective inputs |
| Selected installed governor | All 54 files, modes, bytes, hashes and complete population unchanged |

The typed R2 census hashes literal symlink target bytes and never dereferences the two deliberate negative aliases. Both are the declared `test_aliased_TASK_refuses_before_currentness/task/TASK.md` paths in the RED and GREEN trees. No other alias or extra/missing member was found. The complete per-file census is retained in `INPUT_CENSUS.json`; its identity is bound by the cited manifest and final artifact seal. [E01]

| Principal binding | SHA-256 |
|---|---|
| R2 `MANIFEST.json` | `c56b58203be1799bb032b3338a9484a17d827d108bc47e34e2fde1cc040d1b0f` |
| R2 `REVISION_FREEZE.json` | `45259e48b7a7af221c31c867265a62383ba312a32f5f5e090bac89c10f3b119c` |
| R2 adapter | `42d08bdd3d66d4f5418a8b7d4e1f4e148bc39fc25842cd1aedbbc329f35a1e43` |
| R2 schema | `6e8efa24a39fab4701ff24437b7fa53739770064a6240fee3011b13803c58d50` |
| R2 controlled tests | `3f876c197f247cab128e831641448be677c4fd588c7414a60b4f171a20241d22` |
| Full retained revision patch | `687c5dd8682c3a8779067e91f7e04bcc88f3bdf6826d8b0d02d0840bdb63c0bd` |
| Corrected original recorder | `feb54b993b30f97442945ed9c9543ec652e1bd008f6504fc1d08eaf4cf731fdd` |
| Unchanged primitive | `348bebac70e43bb8fba37e3731ab73b7bf8f99f5fbd9baf4a59cfba8a2e545c3` |
| Descriptive executing governor inventory | `d2f741afd81182dcf20ad23ee7c42bbfba744e5c451e9205028edf2a29e89008` |
| Original a297 policy | `24b5079e1cacdbb8d195d94d48e82f5683e915424aaf3fb8514a282dd3396c5c` |

The reviewer read the complete 45,404-byte revision patch and the affected production source, schema, interface and capture plan. Some exploratory combined output was truncated; that output is not treated as a completed content read. The decisive files/sections were obtained in bounded reads, and the complete byte population was verified independently. The original policy also matches Git blob `84ddb5eb696109c64038b8cbed3b2fd1e37a21af`. [S11; S32; E01]

## 3. Findings and exact disposition

| Item | Disposition | Scope |
|---|---|---|
| R1 — live TASK and physical path binding | PASS | Exact live TASK bytes checked on every operation; aliases and absent/drifted files refuse before currentness/effects |
| R2 — originally demonstrated CR/LF/pipe defect | PASS at that exact repair scope | All six scalar guards and schema patterns reject embedded and trailing CR/LF/pipe; raw refusal retained |
| R2.1 — other admitted line separators | NEEDS_REVISION, P2 | Existing splitlines-based table reader cannot round-trip some admitted scalars |
| R3 — producer terminal metadata and streams | PASS | Required producer fields/types and both streams checked; production currentness seam unchanged |
| R4 — full capture ownership/timing | PASS as a prospective plan | Eight artifacts at six boundaries per arm; no claimed live captures |
| Ordinary governor-only applicability/precedence | PASS at the limited source/data scope | No new unused-child, install, atomic-plugin or native prerequisite |
| Typed actual tool-observation references | PASS as a representation judgment | Existing opaque reference field accommodates truthful host-exposed references; attribution remains semantic receiving |
| Actual episode/original predicate acceptance | GAP / NOT YET OBSERVED | No live actor, Root receiving, per-effect currentness, recording sequence or final episode receiving supplied |

### R1: closed at the affected source boundary

`scenario` now compares `raw_file(task / "TASK.md")` to the exact assigned frozen TASK before proposal/subject admission. `admit` calls this path for all three supported operations before command preflight, live currentness and record effects. `raw_file` delegates to the common physical-path guard, which requires canonical absolute paths, forbids symlinks at the file or any ancestor, and requires the physical file. The task-root restriction and fresh-workspace/previous-admission rules remain intact. [S01 `physical`, `raw_file`, `scenario`, `admit`]

The retained controlled evidence contains missing and drifted TASK refusals at failure, rerun and L1 stages, preservation of existing failed/resolved state, and a physical alias refusal. Alias coverage at the initial stage is sufficient for the shared `raw_file` source rule; there is no separate later bypass. Positive fixtures now include the real frozen TASK and commit it with the other inputs. The old eighteen test methods are AST-identical, so the corrected fixture is not represented as a new actor result. [S05; E01]

This closes the original unbound-live-TASK defect. It establishes present-file and digest equality at admission, not proof that the actor actually received/read that file. Actual submission manifests and real dispatch/continuation observations remain the delivery evidence. [S08–S10]

### R2: the CR repair is correct, with one related remaining boundary

The revised source rejects CR, LF and pipe in every one of the six free-text scalar fields. The schema uses an absolute end-of-input assertion instead of relying on a dollar anchor that can match before a trailing LF. The retained controlled CR refusal preserves the raw actor bytes and raw Root projection before refusing; it does not rewrite either into a normalized accepted answer. The retained schema cases cover all six fields and both embedded and trailing CR/LF/pipe. [S01 `actual_decision`; S02 `Record`; S05]

#### R2.1 — admitted non-CR/LF separators fragment the existing row reader

**Exact source and smallest counterexample.** `root_callsite.py:262–264` and the six `Record` patterns exclude only CR, LF and pipe. The string `"abc\u000bdefg"` is eight code points, exactly the minimum valid length, and contains none of those excluded characters. The exact `actual_decision` accepted it in `record.reason`. The unchanged `andon` wrote it into the classed row and `state_value` preserved the vertical-tab byte. The existing pure `rows()` reader in the retained original-owner tests, `tests/test_recording.py:37–41`, uses `section.splitlines()` and returned a five-cell row rather than the expected eight. [S01–S06; E03–E04]

**Observed limit.** The writer and state helper do not themselves use `splitlines()` for this path. This probe did not reproduce the previous CR-to-LF rewrite. The serialized LF-delimited row still has nine pipe delimiters, and this review does not claim that the current LF-oriented rerun regex or a live controller failed. The defect is the admitted value's failure to round-trip through the package's existing line-oriented table consumer. A consumer using LF alone would preserve the row. That distinction matters and is retained in the probe result. [S03 `andon`, `resolve_andon`; S04 `state_value`; E03]

**Admitted family.** Source inspection plus the same isolated probe confirms that VT U+000B, FF U+000C, file/group/record separators U+001C–U+001E, NEL U+0085, line separator U+2028 and paragraph separator U+2029 are admitted by all six schema patterns and the scalar guard, while Python's existing `splitlines()` consumer splits them. A frozen task and prompt do not constrain a future natural-language scalar to exclude these characters. No finite admitted request rule closes that boundary. [S01–S02; E03]

**Impact and priority.** P2 at the record/consumer interface. The demonstrated table reader loses the remainder of the abnormality cell and following cells as a single classed row. The directly affected table data include reason, containment and owner/source; `next_action` also enters the current-state table. Dependencies and acceptance are additionally accepted under the same scalar contract but are recorded as JSON event data on this path; the probe does not claim that their JSON serialization is corrupted. This is not evidence of code execution, provider compromise, a failed actor, or an original acceptance failure. It is sufficient to withhold an unqualified source admission for the current reader-compatible record contract. [S01; S03–S06; E03]

**Smallest repair.** Extend the existing shared scalar exclusion and the six schema patterns to cover the full existing reader's line-break set, retaining pipe rejection and the absolute-end assertion. Refuse these values before currentness/effects; preserve raw actor/Root evidence verbatim. Do not normalize or repair the returned text into an expected answer. A bounded guard/schema and writer-reader round-trip check can confirm the counterexample is refused and ordinary valid text remains intact. No actor rerun, new prompt, changed scenario, new policy identity, installed-package repair, native route or whole-suite replay is needed merely to fix this boundary. An intentional change to the reader contract would be larger and would need to explain all affected consumers; it is not the smallest repair. [S01–S06]

**Actual probe.** `aa880f/0` is the completed reviewer tool result for this single source-only probe. It imported only the exact source, extracted the pure existing reader by AST, and wrote a new isolated STATE under this review. It made zero `admit`, subprocess, actor, provider, currentness, controller or original workflow calls. Source identities were compared before and after and were unchanged. The raw controlled request, changed decision/observation, before/after STATE, event output and full result remain in `separator-probe/`. These are explicitly controlled reviewer artifacts, not actual Root or actor observations. [E03–E04]

### R3: closed at the terminal-capture boundary

The revised `capture_record` requires all fourteen terminal producer fields. Exit and expected-exit must be exact integers matching the prescribed command expectation, timeout must be false, cleanup must be `owned-process-group-absent`, and the process-group identifier must be an exact positive integer. Boolean and float aliases do not pass integer checks. Times must be finite numeric values in order. Capture mode must be exactly `separate-stdout-stderr`. Both stream descriptors bind the exact producer filenames, integer byte counts and actual full stream hashes. `raw_file` applies the same physical-file and alias checks to metadata and streams. [S01 `capture_record`; S04 `run`; S05]

The checks validate the required producer population without treating arbitrary extra JSON fields as authority; those fields are unused. They do not cryptographically authenticate caller-supplied metadata. Actual command-origin and tool evidence remain an external Root receiving obligation, as before. This limitation is explicit and is not a reason to fabricate a provider ID. [S01 module contract and `observation`; S07]

The same validator covers witness records, original failed witnesses and production currentness captures. AST comparison confirms that `_invoke_currentness`, `require_currentness`, `_load_owner` and `admit` were not modified. Production still invokes the exact installed helper and controller, immediately before record effects, with no skip flag or historical receipt substitution. The synthetic positive PGID in controlled currentness records is explicitly labeled synthetic; it is not a live process claim. [S01; S17; E01]

### R4: closed as a concrete pre-actor capture plan

The frozen map names the actual Root-supplied existing STATE and ROADMAP paths, separately from each new arm's dedicated STATE, event journal and checkpoint. TASK, proposal and implementation subject complete the eight-artifact population. All eight require actual observations before and after each of the three recording operations: six boundaries per arm. The before observation occurs after the request/evidence is ready with no intervening mutation; the after observation follows the actual terminal result before the next mutation/continuation. [S08–S10]

Present files require full retained bodies and exact identity; expected initial dedicated-file absence is recorded as absence, without an invented empty payload or content hash. Unexpected missing Root/task files, aliases, unreadable files, capture races and incomplete terminal results remain explicit gaps. Every boundary requires a fresh actual read even if storage is deduplicated. Root STATE/ROADMAP may truthfully remain byte-identical; no task ROADMAP or synthetic governance event is introduced. [S08–S09]

The failed-row preimage is preserved before `record-rerun` resolution, in addition to the earlier failure-after snapshot. Hash-only prior RESULT/checkpoint fields cannot substitute for those full bytes. TASK and subject remain unchanged across the episode; proposal changes only through the independently authorized frozen syntax correction. Refusal and partial-effect observations are included. These requirements address the overwrite/capture gap identified in the first review. [S08–S10]

Actual initial and post-check submission manifests bind full TASK/proposal/subject, exact permitted prompt, actual command records and both streams, plus the complete actual attachment population and real dispatch/continuation observations. Labels and hashes alone are explicitly insufficient as delivery proof. The original oracle, sibling arm, repair report, engineering receipts and Root snapshots stay outside actor-visible material. Arm assignments and actual observations remain null at preparation time. The author did not claim to have read or fabricated the live Root files. [S08–S10; S12–S15; S22; E01]

## 4. Retained engineering evidence and original-owner repairs

The independent readback confirms the same revised test bytes on RED and GREEN. RED used the exact previous adapter, ran thirty methods, and retained forty-five failed assertions; every old eighteen method passed. GREEN used the exact R2 adapter and retained 30/30 success. These are controlled ordinary engineering results, not observed actor acceptance. The new review did not rerun either suite. [S33–S36; E01]

The final GREEN population contains 213 real-origin local command records and 23 explicitly labeled currentness doubles. This count does not imply that every current negative file is still an intact producer record: one real-origin descriptor is deliberately stripped of terminal fields, and one failure stream is deliberately altered. Their original full preimages are retained and independently bound. One currentness double is intentionally malformed. All other producer fields/streams were checked; the retained double labels explicitly disclaim a real controller/process identity. Seventeen altered metadata copies are inputs, not seventeen extra executed commands. Twenty controlled recording admissions keep implementation readiness, original acceptance and native claims false; twenty-six retained refusals report no record effects and no actor rewrite. [E01; S05]

The prior independent review of the three original-owner repairs remains applicable because the corrected recorder and primitive are byte-identical. `receive_decision` registers a separate dispatch interruption when appropriate, `andon` emits the corrected single-class row with original witness retained, and `resolve_andon` binds a successful deciding command and actual full task commit Anchor while preserving the original abnormality/failure. This R2 adapter uses the existing local recording methods and state/event writers; it does not call the historical provider receiver or replay original workflows. No new `actual-Root-data-decision-received` or phase-start event is present in the controlled ordinary record stream. [S03–S04; S07; S28; E01]

Historical F1 remains unrepaired at its original acceptance layer. All earlier RED history and adverse observations remain bound and unchanged. The new source correction and controlled receipts do not relabel those historical outcomes as passing. [S28–S31; E01]

## 5. Ordinary applicability, precedence and currentness

Two identities remain distinct. The installed fifty-four-file inventory is descriptive data for the exact ordinary executing governor. The copied a297 PROTOCOL is immutable target-policy data. The inventory is neither proof of atomic-plugin/native activation nor a positive review disposition. The adapter checks the actual selected population, file modes, physical paths and exact helper membership when Root later supplies genuine intake evidence. [S11; S16–S19; S07]

At the expressly ordinary governor-only scope, the supplied spine's ordinary path is applicable and no internal child is requested. The review therefore introduces no child resolver, sibling package census, installation, formal-child or native prerequisite. Discovery hints for unrelated advertised skills are not route authority. The exact a297 target-policy obligation is evaluated as policy data, without pretending it is the installed governor's native identity. [S18–S21; S07]

The required future currentness invocation remains exactly:

```text
argv = ["bash", "/home/agent/.codex/skills/remote-skills/skill-6a85962852788191bb717a1a61592b58/scripts/claim-run.sh", "--require-current-continuity", "dg16-dg18-recovery-20261118"]
cwd = /workspace/scratch/2678f1e431c3/recovery-repo
```

Its helper is the pinned 14,707-byte installed member with SHA-256 `9c9945fdf650c72b8019f0dd908fff360162cc11ae7eb3197ccafe0f6ab3730f`. The production path captures the complete result, checks one successful terminal command with empty stderr and one full receipt for that controller, and uses the actual returned epoch. Neither historical G000C nor supplied G0010 can be hardcoded as a future effect's currentness. The reviewer did not invoke this helper. [S01 `require_currentness`; S17; S19]

## 6. HostObservation: truthful interface adaptation

The owner's stated host facts are compatible with the existing source contract. `observation` requires an exact five-field object, exact sender/subject binding, a 1–256-character string reference and a digest-bound nonempty raw capture. The schema imposes no provider-specific identifier form. A typed actual canonical task/operation reference can therefore occupy `tool_call_id`, while explicitly stating that no separate provider call ID is exposed. An actor-owned `exec_command` chunk ID can identify that actual command observation. No code/schema change is required merely to rename these real exposed surfaces into a provider-specific abstraction. [S01 `observation`; S02 `HostObservation`; E05]

The semantic limits remain essential. A returned task name identifies the actual dispatch target/route; it does not attest model/backend identity or prove the actor read an attachment. A Root read of an actor artifact is a Root observation, not an actor-origin tool call. A derived task/stage/content reference must be labeled derived rather than platform-generated. Different strings alone do not prove distinct events; actual dispatch, initial return, continuation return, reviewer return and Root receiving must remain separate real observations with exact subjects. [S01 `actual_decision`, `package_identity`; S07–S10; E05]

An empty `send_message` or `followup_task` result must remain empty. A nonempty, explicitly identified capture envelope may preserve the exact observed invocation, attribution/capture metadata and the actual empty result, with raw empty bytes retained separately where applicable. Root-authored envelope metadata must remain visibly distinct from provider output. Such an envelope fits the existing opaque bound-capture format, but it supplies no delivery acknowledgment or actor return. Later actual actor evidence remains necessary. If the actual result/attribution is unavailable, preserve that limitation; do not invent an ID, acknowledgment, sender or raw output. [S01 `observation`; E05]

The full representation judgment is retained separately for Root to apply to actual exposed observations. It contains no fabricated operational example, live ID, Root intake or actor evidence. This finding removes no semantic receiving obligation and adds no native/provider prerequisite. Overall NEEDS_REVISION means no positive source-review projection is issued for this exact adapter. [E05]

## 7. Prospective semantic scope and remaining observations

The frozen two-arm task remains a valid prospective discriminator at its stated new ordinary scope. Both initial proposals have the same kind of syntax defect. The sole allowed correction removes the trailing comma; it leaves seven-day retention in arm A against a minimum-thirty-day policy and thirty days in arm B. The neutral initial prompt, unchanged task/source inputs, hidden evaluator oracle and frozen post-check template precede any actor. The post-check template adds only the actual deciding command digest. This review makes no claim about an actor's future answer. [S12–S15; S37–S42]

If actual evidence later exists and is independently received, this design can measure a retained failed criterion, actual successful deciding witness/Anchor, actual return to L1 planning, and separately recorded independent policy conflict versus a matched control. The fixed Python policy check can refuse an inconsistent class/action, but it cannot generate or authenticate an actor's reasoning or Root's semantic rederivation. A correct expected class, acceptable scalar length or successful parser alone is insufficient. A refusal/nonverdict/wrong answer must remain actual evidence; the prompt or actor must not be repeated to obtain a preferred answer. [S01; S10–S12]

Broader original blocker semantics remain actual Root/episode receiving obligations. The a297 policy requires interrupted owner/decision, last safe step, next unfinished gate and affected evidence, plus truthful `blocked_scope:` and `unblocked_work:` with justification when no work remains unblocked. Existing fields can carry these details, but source shape does not prove their meaning. Root and later independent receiving must check those actual contents if claiming broader original-Andon conformance. This is neither an invented new schema/native gate nor a retrospective finding that an unrun actor failed. [S11 L4; S08–S10]

After the bounded R2.1 repair and affected review, the outstanding real work remains: genuine Root receiving of the exact final source/reviewer return; fresh actual arm workspaces/repository HEADs and inputs; actual initial and post-check submissions and returns; actual failed and successful commands; separate actual Root semantic receiving; the eight-artifact/six-boundary capture population; each actual helper currentness result immediately before effects; and final independent episode receiving against the unchanged oracle. These are future observations, not evidence supplied by this report. Historical F1, whole P03/DG17, M01/N06, native Stop/M4 and other broader awards remain unawarded. [S08–S12; S22]

## 8. Completion, evidence and receiving requirements

The review assessment is complete. The source verdict is NEEDS_REVISION for R2.1 only, with R1/R3 and the prospective R4 repair supported as described. Root remains the sole integration writer and sole eventual acceptance authority. No source repair was implemented by the reviewer.

The actual independent input-verification command completed as `fc9a7c/0`; the isolated separator probe completed as `aa880f/0`. Their exact tool returns are retained. The final artifact-sealing command's actual result and digest bindings are in `TERMINAL_RECEIPT.json`; it is separate from author/source test receipts. This report does not treat an internal status field as proof of an unobserved terminal tool outcome. [E01–E04]

`CITED_SOURCE_EVIDENCE_MANIFEST.json` maps every source/evidence ID used here to its exact absolute path, bytes, mode and SHA-256. `INPUT_CENSUS.json` binds the complete received populations, including unchanged historical material and the declared negative aliases. `MANIFEST.json` binds all final review payloads; the terminal receipt binds that manifest and the actual final command result. The original NEEDS_REVISION review remains immutable, and no positive intake projection is emitted for this revised packet.
