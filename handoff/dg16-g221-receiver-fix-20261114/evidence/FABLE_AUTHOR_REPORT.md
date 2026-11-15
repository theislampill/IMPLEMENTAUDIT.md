# G221 receiver correction: pending relation (DG16 G2)

Author: Claude Fable 5.2 (source author, HOLD). Observed 2026-11-14. Source-only scratch work.
No push, GitHub write, dispatch, crypto, key use or decryption. Nothing written to `/home/agent`, the Codex
worktree or any Astra/Sol directory (read-only copies only). No Root decision, review or seal was issued here.

Scratch (WSL native): `/var/tmp/claude-hold/FABLE_WORK/g221-recv/`. Interpreter for every receiver run:
CPython 3.14.4 `-I -S -B`. Producers ran under a 3.14.4 venv (and, for determinism, a 3.12.3 venv).

## 1. Result in five lines

1. **Cause confirmed.** The exact G220 `pending_relation.py` (`948b4b21...`) refuses the real
   `cognition-pending-durability` output of product 205aeab7 with `PENDING_CONTROL_POPULATION` at line 98; the
   only offending name of 58 is `unreserved-JOIN-refuses-without-state-change`.
2. **It is the first refusal but not the only one.** A second, so far masked, refusal follows immediately:
   `PENDING_COMMAND_SHAPE` (lines 106-107), for both pending roles and both routes. With only the name check
   corrected, G221 would fail receiving again with the same public code `FULL_PAIR_NOT_COMPLETELY_RECEIVED`.
3. **Fix** (one file, two predicates): exact equality against the pinned producer control populations (58 + 54
   names), and the interpreter spelling the producers really record (`<runtime-bin>/python3`).
   Proposed `pending_relation.py`: `b73adbc6c8ed6aa32b6d138b839f053e80d75066f3a2d0ce42231a5ad3e546c6`, 30269 bytes.
4. **After the fix** the original receive path for the pending roles accepts real output end to end (17/17
   steps, legacy and DAG stand-ins, both relations equal), including through a fully pin-consistent regenerated
   packet with no override. 24 unit mutations per role and 10 end-to-end adverse controls refuse as intended.
5. **Pin chain:** 13 author-level files change (digests below). `SOURCE_MANIFEST.json` is not in the chain:
   1766 files / 167023692 bytes are unchanged and all three source-total guards still pass. Four decision
   bodies, the candidate seal and everything composed from them must be reissued by Root / the reviewers.

## 2. Reproduction (task 1)

Inputs
- Receiver: byte copy of the G220 public packet directory (43 files), `pending_relation.py` =
  `948b4b21d1f08f0a64a7fe6f104a6ca2e51affd481e38172e05c45ea59dfa1b3` (23704 bytes).
- Product: `git clone` of the local repository, detached at `205aeab7c93299b0666b261485ab5658d8e183de`, tree
  `9ffbaf95080092bf4a45b8772a97ed16068544a7`, clean. `tests/cognition-pending-durability.py` =
  `9f0f3adc...` (matches Sol), owner `scripts/qualify-work-graph-verifier.py` = `79e3250a...` (= `OWNER_SHA256`).
- Producers were launched exactly as the registered test does (`tests/internal-skill-routing.test.sh:284,286`:
  `PYTHONDONTWRITEBYTECODE=1 python3 tests/cognition-pending-durability.py` and
  `... python3 tests/cognition-pending-loader.py --top-level-counter-controls-only`), under the
  `pair_driver.set_environment` environment (`PATH=<venv>/bin:/usr/bin:/bin`, `LC_ALL=C`, `TZ=UTC`, ...), twice
  (stand-ins for the legacy and DAG routes). Both exit 0, `result: PASS`.

Harness `tools/pending_recv_harness.py` calls the original consumers in the order
`pair_driver.receive_main -> full_relation.receive` uses for the declared pending artifacts:
`full_relation.load` (all eight relation inputs digest-bound) -> `full_relation.source_profiles` ->
`full_evidence.capture_declared` -> `full_evidence.receive_declared` -> `pending_relation.normalize` for
{durability, loader} x {legacy, dag} -> `full_relation.compare` -> closing `receive_declared` bookend.
The maintained owner is the real product owner module.

| Run | Receiver | Result | Evidence |
|---|---|---|---|
| BEFORE | exact G220 | 11 pass / 4 refused: durability `PENDING_CONTROL_POPULATION` @ `pending_relation.py:98 <- :229`; loader `PENDING_COMMAND_SHAPE` @ `:106 <- :254` (both routes) | `evidence/02-*` |
| CONTROL | G220 + name correction only | 4 refused: `PENDING_COMMAND_SHAPE` for both roles, both routes | `evidence/03-*` |
| AFTER | proposed (P1 + P2), in-memory substitution | 17 pass / 0 refused; `compare` equal for both scopes | `evidence/04-*` |
| AFTER | regenerated pin-consistent packet, no override | 17 pass / 0 refused | `evidence/20-*` |

The local refusal is the same code the host published: the G220 public causal record locates
`PENDING_CONTROL_POPULATION` at `RECEIVE_FULL_RELATION`, and the private exception message is 26 bytes, the
length of that code (`g220-terminal-review/REPORT.md`).

## 3. Is it the first and only refusal?

**First: yes.** In `full_relation.receive` the legacy iteration runs `load_capsule`, `receive_declared`,
`whole_projection` (stdout roles, report slots), portal and repro projections, and only then
`pending.normalize('pending_durability')`, whose first act is `report()` (line 229 -> 98). The host raised
exactly that code, so every earlier legacy stage passed on the host.

**Only: no. Second refusal R2 = `PENDING_COMMAND_SHAPE`.**
- `pending_relation.command` demands `command[:2] == [runtime_python, '-B']`, and `pair_driver` passes
  `runtime_python = str(runtime / 'python')`.
- Both producers build child commands from `sys.executable` (`cognition-pending-durability.py:267,269`), and
  are launched as PATH `python3`. CPython keeps the invoked spelling, so every recorded `argv[0]` is
  `<runtime-bin>/python3`: 88 of 88 durability rows and 56 of 56 loader rows under the 3.14.4 venv. An Ubuntu
  system-python 3.12.3 venv (the layout `run.py` creates: `python` and `python3` are sibling symlinks) reports
  the same `sys.executable` spelling.
- G220 already shows it for the loader role (BEFORE run): the loader's names are all lowercase, so it gets
  past line 98 and stops at line 106. On the host it was never reached because durability is normalized first.
- Not observed on the host (masked). It follows from pinned source bytes plus interpreter behaviour, and was
  reproduced locally.

**After P1 + P2: no further refusal in the pending relation** for either role or route, on real output, including
the atomic-residue, preimage, physical-projection, materialization and stream-binding predicates, and the
legacy/DAG projections are equal (`e090e303...` durability, `3bc7a4ee...` loader).

**Not established here (needs a complete sealed 119-node pair; no local pair was run):** DAG-route
`load_capsule` / whole / portal / repro projections, equality of the `whole`, `portal` and `repro` scopes,
the proof size bound and the closing bookends. No host has ever reached these stages. The legacy-route
equivalents did pass on the host in G220.

## 4. Correction (task 2)

Patch: `patches/G221-pending_relation.P1-control-population.P2-interpreter.patch`. File:
`changed/candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2/pending_relation.py`.

| | bytes | sha256 | git blob |
|---|---|---|---|
| before | 23704 | `948b4b21d1f08f0a64a7fe6f104a6ca2e51affd481e38172e05c45ea59dfa1b3` | `0cfea45bd9e3cde6bddd91999eacdff54929aea9` |
| after | 30269 | `b73adbc6c8ed6aa32b6d138b839f053e80d75066f3a2d0ce42231a5ad3e546c6` | `fcc20e7c5409425d9f23fe62744e2787c70cd873` |

**P1, control population.** A module constant `CONTROL_NAMES` carries the exact ordered populations
(durability 58, loader 54), and the predicate becomes
`type(controls) is list and all(type(name) is str ...) and controls == CONTROL_NAMES[role]`, same refusal code.

Why a pinned list rather than a wider character class:
- The profile (`OUTPUT_ROLES.json`) has no control list, and it is a static source derivation with a generator
  I do not hold; most names are built in loops, so they are not static literals. The module itself can carry
  the list, which keeps the change inside the one file that must change anyway and adds no pinned file.
- It is strictly stronger than the old check. The old shape accepted any extra, missing, reordered or renamed
  lowercase name; nothing else pins the population (`controls == len(control_names)` is self-consistent).
  Widening to `[A-Za-z0-9_-]+` would accept strictly more than before (see section 5, column ALT).
- The populations are a function of pinned source bytes: identical across four runs and two interpreters
  (3.14.4 and 3.12.3), 58 matches Sol's count, the only environment branch in the producer is
  `hasattr(os, 'mkfifo')` (always true on Linux). Digests of the observed lists (compact JSON):
  durability `c9a2f7c3044bc04c3e2db3c6179c4282b4c4457cec6d902f0f3bd08e9d3a5d20`,
  loader `38320093344c1d086b8b72f1690803298e48b55eec309287d7a15448f87ca3d2` (`evidence/control_names.observed.json`).
- Residual risk: the list is pinned from local execution, not from the hosted run (its stdout is private). If
  the hosted population differed, P1 would refuse where the wide regex would not. Root can retire this by
  comparing the list with the G220 private stdout.

**P2, interpreter spelling.** `interpreter = runtime_python.rsplit('/', 1)[0] + '/python3'` and
`command[:2] == [interpreter, '-B']`. One exact spelling, no alternation; the old `python` alias is now
refused. Nothing else in the file changes.

**Alternative, not proposed:** `patches/pending_relation.ALT-regex.py`
(`dba7eb6363fd83522f0b88073606e6186e7243f951a3888a0bd0eb491051ce8b`, 24005 bytes) = `[A-Za-z0-9_-]+` plus P2. It
also accepts the real output (`evidence/05-*`). Its pin chain is the same 13 files with different digests,
not regenerated here.

## 5. Acceptance and adverse controls (task 3)

Acceptance: section 2, AFTER rows.

Unit level (`evidence/06-adverse-unit.log`): the module's own `report()` on single-variable mutations of the
real report, per role; `ACCEPTED` means not refused.

| Mutation (durability / loader) | G220 original | ALT regex | proposed |
|---|---|---|---|
| real output | refused / accepted | accepted | **accepted** |
| empty name (replacing, appended) | refused | refused | refused |
| space in name, trailing space | refused | refused | refused |
| duplicate (replacing, appended) | refused | refused | refused |
| extra well-formed name | refused* / **accepted** | **accepted** | refused |
| missing name (first, last, interior) | refused* / **accepted** | **accepted** | refused |
| non-ASCII (U+00E9, Cyrillic homoglyph, fullwidth digit) | refused | refused | refused |
| case changed, reordered, renamed | mixed | **accepted** | refused |
| null / integer / nested list member, empty list, object, tuple | refused | refused | refused |
| the other role's population | accepted / refused | **accepted** | refused |

\* refused only because the uppercase name is still present, not because of the mutation.

Interpreter (`command()` on `argv[0]`): proposed accepts only `<runtime-bin>/python3`; refuses the `python`
alias, `python3.14`, `/usr/bin/python3`, bare, relative, sibling-directory, trailing-space, suffix and
non-ASCII spellings. Unexpected verdicts for the proposed file: none.

End to end (`evidence/07` to `16`): a fresh real artifact is tampered consistently (stdout document,
`report.json`, census all still bind), so only the changed predicate can refuse. Durability: extra, missing,
non-ASCII, space, empty, duplicate -> `PENDING_CONTROL_POPULATION`. Loader: extra, missing ->
`PENDING_CONTROL_POPULATION`. Durability with `argv[0]` = `python` alias and loader with `/usr/bin/python3` ->
`PENDING_COMMAND_SHAPE`. The untouched DAG stand-in passes in every case.

## 6. Pin chain (task 4)

Method: `tools/pin_closure.py` (digest-reference closure) and `tools/regen_chain.py` (fixpoint: each digest of a
changed file is replaced, `{bytes, sha256}` descriptors updated, JSON re-encoded only in its own round-trip
style). Universe: `candidate-e76-source-01/` (66 sealed members + `SEAL.json`) and `author/`. 10 rounds,
13 files changed, 58 unchanged. Patch: `patches/G221-author-pin-chain.PROSPECTIVE.patch`; files in `changed/`.

| File | What pins it changes | bytes | before sha256 | after sha256 |
|---|---|---|---|---|
| `pending_relation.py` | the correction | 23704 -> 30269 | `948b4b21d1f08f0a64a7fe6f104a6ca2e51affd481e38172e05c45ea59dfa1b3` | `b73adbc6c8ed6aa32b6d138b839f053e80d75066f3a2d0ce42231a5ad3e546c6` |
| `RELATION_INPUTS.json` | `files["pending_relation.py"]` bytes + sha256 | 1311 | `51733af1c8d6c1224030a5c95c8002a868e1f421253eccb6905a41938856a2a4` | `41bdfe0fb7ee119b5fd1fdc0ee1564c99977d80981b80414d5afa595a476a014` |
| `POLICY.json` | `receiver_inputs_sha256` | 22159 | `86cdb96fadf0fcc230341e43bbf05c84d2cc3844bb4db760f61cec8bfecf0586` | `21afa7726556a8ba7814ba6f3a133a0fbfadc3b9e93a83a65b7f843b518786b1` |
| `pair_driver.py` | `RELATION_INPUTS_SHA`, `POLICY_SHA` | 48451 | `1967e1cc5ab3baec5a94cd88ef7b402dbbfeae1436cb4ede87c33599cafb7c54` | `3bf4d21e6c8da690d319a8294f2f52d525595e0cbd30542204ed05c3bd96530b` |
| `...-decisions/CURRENT_HOST_QUALIFICATION_REQUEST.json` | `source_bindings` pair_driver, policy, receiver_inputs | 6633 | `51712275a291c39b902c4c10fa80a8ea6b3c833ed2bf184e840a52ee32e20e3a` | `74c652e86b69a14e6503bf31867d35ae310313653046d3cc9b0a8bd02aecf6cf` |
| `run.py` | `PAIR_DRIVER_SHA`, `RELATION_INPUTS_SHA`, `POLICY_SHA`, `CURRENT_HOST_REQUEST_SHA` | 86060 | `383bec626e60b50e9aca9d96d8dc93d2869c71fd8650ae7580ffbf3802200a92` | `688166071f33d2cb33c48a4136a88b7dccf719267e9fa43db72cffb361fdbd74` |
| `.github/workflows/dg16-r5-full-g2.yml` | 20 adapter-digest literals | 23471 | `4589fc30dd7ba955c13a2c8ba2a1bef18d8e81b142ee83fe94d41275de52b5ee` | `2cb372745826f72247c7c9df8faa94904c612891d370d2b5a9110d7734137d10` |
| `receiver/BINDING_TEMPLATE.json` | `modules` entries for the five packet files above | 7596 | `adfcf7b001b49ceb8df20a772829a56514f4e40801fb05d84a2fbd0b8a52478a` | `692546f1eb5e7cc104dabf11eb357a9ff1d78a5449c5ecd2feaf2dc70d6e2b6f` |
| `receiver/ROOT_BINDING_TEMPLATE.json` | `workflow_sha256` | 2191 | `7e09a5c76a6cf27cbf371081a3c278c500590249e2a646e4c3c332e9ec604295` | `ab439ba227b8625d039fd93869a5d566873fcec4a81031d3848a52d0ee45ade1` |
| `author/bind_public_successor.py` | `TEMPLATE_PINS` | 16529 | `a6545228f277408d361996b9c7a5d4aecde0e25ea5efe7443f482d535da2e5c3` | `9e52c046725edbb12aecca9173c0f1c7e599793d90310cc3dfdf4a15554e694b` |
| candidate `SEAL.json` (Root-issued; body only) | nine member descriptors | 14374 | `50f694f066d82bc8eda600dd449f8c8ceedf93ebab308d87ca02fefb2ea594c2` | `1d2ef960405145d0d8a5617267d3ee84d07bac7cadfbbbd6382078a7c316472b` |
| `author/compose-candidate-bound.py` | `PINS['candidate']` | 17350 | `bfbce57166807acaf76c4441219f9d4224adba57c759544e38d2a8787a4f5ee2` | `9b1e7ddaf2bcd8a223147e4955ce6e0e5497ec3b3af467dec3c15edb266d16e1` |
| `author/compose-final-bound.py` | `PINS['candidate']` | 17412 | `b4c200487c961ef28859cde75a8ee7b6468cd3a0f6ade465d22f6542bb0fc505` | `c349809082488e524ed92843b25b9ac94c6333105b3a2af7a46c8887d3263a0a` |

Only `pending_relation.py` changes size. Git blob ids before/after are in `evidence/17-regen-chain.json`.

**Not in the chain (verified, unchanged):** `SOURCE_MANIFEST.json` (`328bfd9b...`; it is the product-source
manifest and `pending_relation.py` is not a member), so **file count 1766 and byte total 167023692 are
unchanged**; `REPORT_SLOTS.json`, `OUTPUT_ROLES.json`, `CAPTURE_DIAGNOSTIC_CATALOG.json`, `full_relation.py`
(`FULL_RELATION_SHA`), `policy_control.py` and every other packet file.

Checks on the regenerated tree through the original consumers
- `tools/check_chain.py`: 17/17 joins hold, on the G220 base and on the regenerated tree
  (`evidence/18-*`, `19-*`): RELATION_INPUTS vs eight physical files, pair_driver and run.py pins (17 file
  pins), request bindings, 20 workflow literals, 43 template modules, 66 seal members, composer and binder pins.
- In-run guards with the regenerated `run.py` (`evidence/22-*`, G220 base in `21-*`): `read_manifest`
  (1766 / 167023692), `verify_source` over the product copy, `native_prerequisite.require_full_source_closure`
  (and its adverse 167022772 refusal), `request_admission` with the new request pin, `checked_driver`, and every
  other module pin behave as on the G220 base. 33 of 35 steps are as expected.
- The two that refuse are the expected Root items: with the stale G220 decision bodies left in place,
  `actual_policy_adoption` -> `EXACT_INDEPENDENT_CODE_REVIEW_REQUIRED` and `actual_native_adoption` ->
  `G2_NATIVE_INDEPENDENT_REVIEW_REQUIRED`. `pair_driver.relation_context` has the same dependency.

**Forced downstream, not regenerable by me (Root / independent reviewers / composition):**
- The four decision bodies (`INDEPENDENT_COLD_REVIEW`, `ROOT_POLICY_ADOPTION`, `NATIVE_INDEPENDENT_REVIEW`,
  `ROOT_NATIVE_APPLICABILITY_ADOPTION`): each binds `adapter_sha256`, `pair_driver_sha256`, `policy_sha256`,
  `receiver_inputs_sha256` and `candidate_seal_sha256`. All five values change.
- Candidate seal issuance (the body above is only the mechanical member update), review seal,
  `PHYSICAL_REBINDING_ISSUANCE`, composer review-seal / decision pins.
- Composition outputs: `COMPOSITION.json`, both gate readbacks, `PUBLIC_BINDING_BODY_REQUIREMENTS.json`,
  `PROSPECTIVE_TREE.json`, composition `SEAL.json`, final tree id.
- Public leaf index (`EXPECTED_LEAVES.json` / `PUBLIC_INDEX.json`): seven changed public leaves (the six packet
  and workflow files plus the request) and the four reissued decisions.
- Bound receiver (`BINDING.json`, bound `public_receiver.py` / `admission_gate.py`, review selection, receiver
  seal), operator static source (workflow body pin and its digest chain), installation records.

**Caveat on the digests.** These values are the receiver fix alone on the G220 base. A G221 episode also needs
whatever successor bump Root and Sol apply (G220 used branch `...-host-20-...`, attempt 1; the recipient
certificate expires 2026-11-15T14:51:46Z). That bump touches `run.py`, the request, the workflow, both receiver
templates and the seal, so their final digests will differ from the table. The first four rows
(`pending_relation.py`, `RELATION_INPUTS.json`, `POLICY.json`, `pair_driver.py`) do not contain the branch and
stay as listed. `tools/regen_chain.py` plus `tools/check_chain.py` redo the propagation on any base.

## 7. Sibling relation modules (task 5)

Every `fullmatch` / `search` on a name-like operand in `finite_relation.py`, `full_output_relation.py`,
`full_stdout.py`, `full_evidence.py`, `full_relation.py` and `pending_relation.py` was listed. The lowercase-only
identifier shape exists only at `pending_relation.py:98`. The others are allocator shapes:

| Pattern | Producer | Check |
|---|---|---|
| `/tmp/<prefix>[a-z0-9_]{8}` (`full_evidence:89`, `full_stdout:65,81,99`, `pending_relation:312`) | Python `tempfile` | 200000 candidate names on 3.14.4 all match; alphabet is exactly `[a-z0-9_]`; real pending roots and the atomic residue accepted in every run here |
| `/tmp/tmp\.[A-Za-z0-9]{10}` (`full_stdout:142,165`), `d48-fence-[A-Za-z0-9]{6}` | `mktemp` | 3000 coreutils samples all match, 62-symbol alphabet |
| `R0035_[A-Z0-9_]+_LIVE`, `[0-9a-f]{64}`, `[0-9]{3}\.(physical\.json|stdin|stdout|stderr)` | fixed vocabularies | no case freedom on the producer side |

All of the `full_stdout` and `full_output_relation` patterns were also exercised on real hosted output: they
run inside the legacy `whole_projection`, which completed in G220 before the pending refusal. I did not run
those producers locally. For the R2 class (an assumed interpreter spelling): no other relation module compares
an interpreter path; `full_relation` only executes `runtime_python`.

## 8. What Root must do

1. Decide P1 as proposed (exact pinned populations) or the ALT regex; if P1, optionally confirm the two lists
   against the G220 private stdout. Adopt P2 in either case, otherwise G221 fails receiving again.
2. Have Sol (or adopt from `changed/`) land `pending_relation.py` and re-run the pin propagation on the actual
   G221 base, including the successor bump; verify with `tools/check_chain.py`.
3. Reissue: the four decision bodies, candidate seal, review seal, composition, public leaf index, receiver
   binding and operator static source. Independent review of the changed file is required by the policy gate.
4. Accept the residual: DAG-route whole / portal / repro receiving and the three non-pending equality scopes
   have never run on any host and were not exercised here.

## 9. Inventory

- `changed/`: the 13 regenerated files in tree layout; `CHANGED_SHA256SUMS.txt`.
- `patches/`: the proposed patch, the 13-file chain patch, the ALT patch and file, the P1-only control file.
- `evidence/`: `00-run_all.out` (index), `01` real producer stdout, `02`-`05`, `20` receive runs, `06` unit
  adverse, `07`-`16` end-to-end adverse, `17` closure and regeneration, `18`/`19` chain checks, `21`/`22`
  in-run guards, `control_names.observed.json`, `alphabet-check.log`, `99-sha256.txt`.
- `tools/`: `produce.sh`, `pending_recv_harness.py`, `make_fix.py`, `adverse_unit.py`, `tamper.py`,
  `pin_closure.py`, `regen_chain.py`, `check_chain.py`, `run_all.sh`, `inrun_harness.py` (from the G220 work).
