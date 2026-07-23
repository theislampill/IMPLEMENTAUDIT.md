# v0.3.2.0 Luna-first staged campaigns implementation plan

> **Execution workflow:** Use `superpowers:subagent-driven-development` for
> Tasks 1-7. One implementer works at a time in the existing linked worktree;
> each task receives a fresh specification reviewer and code-quality reviewer
> before the next task. The main agent owns Tasks 8-10 operational gates.

**Goal:** Implement, qualify, freeze, and execute two separate Luna campaigns so
B3-v4 reaches valid 6/6 and the candidate matrix reaches valid 14/14, then
merge the planned qualified branches to `main` with disposition
`LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN`, while also producing
append-only corrected adjudication of all 56 historical bundles and preserving
every release boundary.

**Architecture:** A pure defensive lifecycle module supplies strict custody,
create-once lifecycle, prefix, stop, pause, and exact-byte primitives. B3-v4
and candidate matrix use separate schemas, validators, drivers, campaign roots,
mission identities, result composition, and independent rederivers. A separate
surface manifest mechanically decides evidence invalidation and provisional
merge eligibility.

**Owner/source:** 2026-07-22 staged-execution decision and explicit approval of
the shared-lifecycle/separate-contract architecture.

**Design:**
`docs/superpowers/specs/2026-07-22-v0320-luna-first-staged-campaigns-design.md`

**Starting implementation baseline:** design commit
`39c7c66073af2ba1aded4a18be2cc9ddbd12b388`; four B3-v4 suites PASS in
115.4 seconds. The worktree is already linked and isolated at
`C:\workspace\ai\improveimplementaudit\IMPLEMENTAUDIT-b3v4-freeze-sol`.

**Global constraints:** No Opus execution, planning, packet completion, or host
preparation; no Terra. No Luna mission before exact-packet deterministic and
independent freeze PASS. No silent retry. No overwrite of attempts or
historical evidence. The owner authorizes the planned qualified-branch merges
to `main`, but not destructive tag movement or release publication. Raw logs
remain under the private coordination root, never in product commits.

## SDD control procedure for Tasks 1-7

For every task:

1. Record task number, base SHA, and scope in `.superpowers/sdd/progress.md`.
2. Generate the task brief with:

   ```bash
   "$SDD_SKILL/scripts/task-brief" \
     docs/superpowers/plans/2026-07-22-v0320-luna-first-staged-campaigns.md N
   ```

3. Dispatch one fresh implementer with the task brief path, design path,
   current base SHA, allowed files, required RED and GREEN commands, and the
   prohibition on model/external execution.
4. Require the implementer to commit only the task scope and write its report
   under `.superpowers/sdd/`.
5. Generate a commit-range review package:

   ```bash
   "$SDD_SKILL/scripts/review-package" BASE HEAD
   ```

6. Dispatch a fresh read-only specification reviewer. If it finds a substantive
   gap, return to the same implementer for correction and re-review.
7. Dispatch a fresh read-only code-quality reviewer against the corrected
   range. Fix Critical/Important findings before continuing.
8. Re-run the task's GREEN command in the main thread, verify exact SHA and
   clean state, then record the accepted SHA in the private ledger.

No two implementers run concurrently. Reviewers never write product files and
an implementer never approves its own commit.

### Task 1: Extract defensive staged-campaign lifecycle primitives

**Files:**

- Create: `eval/campaign_lifecycle.py`
- Create: `eval/test_campaign_lifecycle.py`
- Modify: `eval/b3v4_contract.py`
- Modify: `eval/test_b3v4_contract_matrix.py`

**Purpose:** Centralize mechanics shared by the two official campaign paths
without moving scoring or acceptance semantics into the core.

**RED:** Add tests that currently fail for:

- strict duplicate-key/nonfinite JSON rejection;
- create-once byte and JSON writes;
- lexical/canonical path equality and every-component no-link/no-reparse checks;
- single-link regular-file reads;
- exact sequential terminal prefix with no gaps, duplicates, or claiming dirs;
- attempt-after-stop refusal;
- mandatory stage pause creation exactly at a declared prefix;
- refusal to resume without the pause or with a mismatched pause hash;
- cross-campaign root/schema confusion.

Run:

```bash
python eval/test_campaign_lifecycle.py
```

Expected RED: missing module/functions or failed pause/prefix assertions.

**GREEN:** Implement narrow data-neutral APIs such as:

```python
read_strict_json_bytes(path, owner, *, root)
write_new_bytes(path, payload)
write_new_json(path, value)
validate_terminal_prefix(root, missions, *, stop_states, allowed_root)
write_stage_terminal(root, stage, binding)
validate_stage_resume(root, stage, binding)
```

Reuse the proven parent-component custody behavior from `b3v4_contract.py`;
do not weaken official and independent-path no-link coverage. Migrate only the
shared B3 custody calls needed to prove the extraction is behavior-preserving.

**Verify:**

```bash
python eval/test_campaign_lifecycle.py
python eval/test_b3v4_contract_matrix.py
python eval/test_b3v4_freeze.py
python eval/test_b3v4_campaign.py
python eval/test_b3v4_rederive.py
git diff --check
```

**Commit:** `refactor(eval): add staged campaign lifecycle core [Sol]`

### Task 2: Version B3-v4 as a six-mission Luna campaign

**Files:**

- Modify: `eval/b3v4_contract.json`
- Modify: `eval/b3v4_contract.py`
- Modify: `eval/validate_b3v4_freeze.py`
- Modify: `eval/b3v4_campaign.py`
- Modify: `eval/b3v4_rederive.py`
- Modify: `eval/test_b3v4_contract_matrix.py`
- Modify: `eval/test_b3v4_freeze.py`
- Modify: `eval/test_b3v4_campaign.py`
- Modify: `eval/test_b3v4_rederive.py`

**Purpose:** Replace the never-executed interleaved v1 launch contract with a
versioned Luna-only B3 contract while preserving the old commit as historical
tooling evidence.

**RED:** Encode the exact mission sequence from the design and test:

- any old interleaved sequence is rejected;
- indices 0-5 are exactly the approved Luna relative order and no other mission
  is accepted;
- the seventh `run_next` call always refuses;
- terminalization before six terminals or after an extra attempt is invalid;
- six valid Luna terminals rederive to `INCOMPLETE_PENDING_OPUS`,
  `luna_stage_accepted: true`, `accepted: false`;
- any Luna FAIL/INVALID/ERROR/substitution or official disagreement prevents
  stage acceptance and stops the prefix;
- Luna-only output cannot claim final cross-model or release qualification.

Run the four B3 suites and preserve the failing output under the task report.

**GREEN:** Version the freeze/custody/stage/result schemas; add declared stage
boundaries and allowed terminal artifacts to the artifact contract; have the
driver expose an explicit `finalize-luna-stage` operation rather than silently
creating acceptance after mission 5. The rederiver emits the separate Luna
result schema and uses exit success for accepted Luna 6/6 without claiming
cross-model campaign PASS.

**Verify:**

```bash
python eval/test_b3v4_contract_matrix.py
python eval/test_b3v4_freeze.py
python eval/test_b3v4_campaign.py
python eval/test_b3v4_rederive.py
python -m py_compile eval/campaign_lifecycle.py eval/b3v4_contract.py \
  eval/validate_b3v4_freeze.py eval/b3v4_campaign.py eval/b3v4_rederive.py
git diff --check
```

**Commit:** `feat(eval): qualify six-mission Luna B3-v4 [Sol]`

### Task 3: Add the separate provisional candidate-matrix contract

**Files:**

- Create: `eval/candidate_matrix_contract.json`
- Create: `eval/candidate_matrix_contract.py`
- Create: `eval/validate_candidate_matrix_freeze.py`
- Create: `eval/candidate_matrix_campaign.py`
- Create: `eval/candidate_matrix_rederive.py`
- Create: `eval/test_candidate_matrix_contract.py`
- Create: `eval/test_candidate_matrix_freeze.py`
- Create: `eval/test_candidate_matrix_campaign.py`
- Create: `eval/test_candidate_matrix_rederive.py`

**Purpose:** Implement a semantically independent fourteen-cell Luna candidate
campaign with its own identity and acceptance boundary.

**RED:** Test that the packet accepts only this canonical fixture order:

```text
B0 B1 B2 E1 E2a E2b E3 E4 E5 E6 E7 E8 E9 E10
```

Indices 0-13 must be Luna and no later mission exists. Test rejection of
missing, duplicate, additional, reordered, wrong-config, control-arm, or B3
mission rows. Also test terminalization, stopped-prefix behavior, cross-root
confusion, create-once attempts, and the result boundary
(`INCOMPLETE_PENDING_OPUS`, 14/14 stage accepted, never a final cross-model
matrix claim).

**GREEN:** Build separate schemas and code paths. Share only defensive lifecycle
mechanics. The matrix driver selects the frozen fixture per mission and uses the
same formal host/evidence stack without importing B3 fixture/arm/repetition
semantics. The matrix independent rederiver must not import the official driver,
runner, scorer, evaluator, adapters, or B3 rederiver.

**Verify:**

```bash
python eval/test_candidate_matrix_contract.py
python eval/test_candidate_matrix_freeze.py
python eval/test_candidate_matrix_campaign.py
python eval/test_candidate_matrix_rederive.py
python eval/test_campaign_lifecycle.py
python -m py_compile eval/candidate_matrix_contract.py \
  eval/validate_candidate_matrix_freeze.py eval/candidate_matrix_campaign.py \
  eval/candidate_matrix_rederive.py
git diff --check
```

**Commit:** `feat(eval): add staged candidate matrix campaign [Sol]`

### Task 4: Bind evaluated surfaces and mechanical invalidation

**Files:**

- Create: `eval/evaluated_surfaces.py`
- Create: `eval/test_evaluated_surfaces.py`
- Modify: `eval/validate_b3v4_freeze.py`
- Modify: `eval/validate_candidate_matrix_freeze.py`
- Modify: `eval/b3v4_campaign.py`
- Modify: `eval/candidate_matrix_campaign.py`
- Create: `eval/provisional_integration.py`
- Create: `eval/test_provisional_integration.py`

**Purpose:** Make cross-campaign invalidation and provisional merge eligibility
hash-driven rather than judgment-driven.

**RED:** Build temporary repository/external surfaces and prove current code
does not reject:

- omitted product, fixture, scorer, evaluator, adapter, prompt, authorization,
  seed/rule, contract, rederiver, launcher, native executable, or attestation;
- path/role duplication;
- same Git commit with a relevant byte changed;
- history-only commit change with identical relevant bytes;
- one-byte conflict resolution drift after Luna success;
- a B3 certificate substituted for matrix evidence or vice versa.

**GREEN:** Define a strict manifest schema whose entries bind role, owned path,
length, SHA-256, and optional Git commit/tree. Provide deterministic manifest
construction, validation, and exact role-by-role comparison. Both packet
validators require their own complete role sets. The provisional integration
tool consumes the two Luna-stage rederivations, deterministic/package/CI/review
evidence bindings, and before/after manifests; it writes a create-once
certificate only when every gate passes. The only successful disposition is
`LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN`.

**Verify:**

```bash
python eval/test_evaluated_surfaces.py
python eval/test_provisional_integration.py
python eval/test_b3v4_freeze.py
python eval/test_candidate_matrix_freeze.py
git diff --check
```

**Commit:** `feat(eval): bind staged qualification surfaces [Sol]`

### Task 5: Close packet-authoring and production preflight gaps

**Files:**

- Create: `eval/campaign_freeze_preflight.py`
- Create: `eval/test_campaign_freeze_preflight.py`
- Modify: `eval/b3v4_campaign.py`
- Modify: `eval/candidate_matrix_campaign.py`
- Modify: `eval/test_b3v4_campaign.py`
- Modify: `eval/test_candidate_matrix_campaign.py`
- Modify: `eval/README.md`

**Purpose:** Convert the durable `NOT_READY` inventories into fail-closed,
machine-verifiable production launch boundaries without embedding secrets.

**RED:** Test refusal for:

- symlink/reparse executable path;
- launcher-only identity with an unbound native child;
- path/version/hash mismatch for actual `argv[0]`;
- stale or mismatched host attestation;
- dirty, wrong-commit, wrong-tree, reused, or overlapping checkouts;
- reused/nonempty runtime root;
- invalid Windows/WSL/native path translation or cross-host readback;
- absent campaign-specific owner acknowledgement;
- absent/unreadable auth source, auth destination outside disposable runtime,
  or credential material rendered into packet/report/log;
- metered auth or Terra configuration.

**GREEN:** Implement a read-only preflight command that emits a strict JSON
report and returns nonzero unless every packet-bound identity is ready. Bind
both launcher and native executable when a launcher is used; prefer the actual
native binary as `argv[0]` when supported. Validate fresh checkout/runtime
topology and exact producer commands. Record auth source path/type/custody only;
never print or serialize credential contents. Drivers require the accepted
preflight report hash immediately before claim/spawn.

**Verify:**

```bash
python eval/test_campaign_freeze_preflight.py
python eval/test_b3v4_campaign.py
python eval/test_candidate_matrix_campaign.py
python -m py_compile eval/campaign_freeze_preflight.py
git diff --check
```

**Commit:** `feat(eval): enforce frozen launch preflight [Sol]`

### Task 6: Add append-only historical 56-bundle re-adjudication

**Files:**

- Create: `eval/historical_readjudicate.py`
- Create: `eval/test_historical_readjudicate.py`
- Modify: `eval/README.md`

**Purpose:** Correctly re-adjudicate every preserved historical candidate and
control bundle without overwriting original evidence or rescoring through an
unbound code path.

**RED:** Create historical bundle fixtures and test:

- strict inventory/hash verification before scoring;
- canonical raw `bundle` use and sanitized-copy refusal;
- create-once per-bundle result with original verdict hash retained;
- separate candidate/control identities;
- layered corrected result, classification, uncertainty, and evaluator/tool
  identities;
- refusal to overwrite, skip, duplicate, or silently replace any of 56 rows;
- aggregate refusal unless exactly 28 candidate and 28 control records cover
  all 14 fixture/config cells;
- preservation of historical 11/28 and 10/28 alongside corrected baselines.

**GREEN:** Implement an explicit `adjudicate-one` and `aggregate` CLI. The first
reads a manifest-bound canonical raw bundle and writes one new record with `x`.
The second independently validates all records and writes corrected baseline
and causal-classification summaries. No code path writes inside historical run
roots.

**Verify:**

```bash
python eval/test_historical_readjudicate.py
python eval/test_reporting.py
python eval/adversarial.py
git diff --check
```

**Commit:** `feat(eval): add append-only historical adjudication [Sol]`

### Task 7: Register and qualify the complete tooling boundary

**Files:**

- Modify: `scripts/verify-package.sh`
- Modify: `.github/workflows/validate.yml`
- Modify: any closest validation registry required by live checker output
- Modify: `eval/README.md`
- Modify: tests only when a qualification finding proves missing coverage

**Purpose:** Make every new deterministic suite an enforced package/CI gate and
obtain exact-SHA acceptance before authoring real packets.

**RED:** Run the validation registry before adding the new suites; it must show
the missing registrations. Preserve that output.

**GREEN:** Add all new tests to both package and CI registries in matching
order. Document the separate campaign CLIs, pause/finalize/resume semantics,
preflight boundary, re-adjudication lane, and provisional integration boundary.

**Focused verification:** Run serially once on the exact candidate SHA:

```bash
python eval/test_campaign_lifecycle.py
python eval/test_b3v4_contract_matrix.py
python eval/test_b3v4_freeze.py
python eval/test_b3v4_campaign.py
python eval/test_b3v4_rederive.py
python eval/test_candidate_matrix_contract.py
python eval/test_candidate_matrix_freeze.py
python eval/test_candidate_matrix_campaign.py
python eval/test_candidate_matrix_rederive.py
python eval/test_evaluated_surfaces.py
python eval/test_provisional_integration.py
python eval/test_campaign_freeze_preflight.py
python eval/test_historical_readjudicate.py
python eval/adversarial.py
bash scripts/check-validation-registry.sh
git diff --check
```

Then run exactly one `bash scripts/verify-package.sh`, preserving explicit
command, PID, start/end, exit, stdout/stderr hashes, artifact hash, exact
SHA/tree, and final clean state outside the product worktree. Do not rerun a
live or completed package process.

Dispatch one fresh read-only complete-boundary reviewer. A substantive BLOCK
governs and returns to the applicable RED/GREEN task. Transport/filter failure
is not a verdict; one replacement reviewer is permitted only when no
substantive result artifact exists.

**Commit:** `test(eval): enforce staged campaign qualification [Sol]`

### Task 8: Author, validate, review, and execute B3-v4 Luna 6/6

**Owner:** Main orchestrator; reviewers read-only. No implementation subagent
may launch a model.

1. Reconcile the exact qualified tooling SHA/tree and clean state.
2. Run the production preflight and resolve mechanically derivable host,
   native executable, checkout, runtime, auth-source, authorization, and
   cross-host identities. Never expose credential contents.
3. Author a versioned B3-v4 packet in a new private create-once directory,
   binding every evaluated surface and producer command.
4. Run structural and live validators, independent hash reconciliation, and
   one fresh read-only complete freeze review. Explicit PASS is required.
5. Run missions 0-5 serially, exactly once each. After every mission verify
   terminal evidence, stopped state, identity/custody, exact packet, and no
   live duplicate process before advancing.
6. On any non-PASS, execute the full ANDON/causal/RED-GREEN/refreeze loop from
   the design. If a relevant surface changes, restart the complete six-mission
   Luna tranche under a new packet; never combine versions.
7. At valid 6/6, run the separate B3 independent Luna rederiver, reconcile it
   with official results, and create the mandatory stage terminal.
8. Record valid Luna 6/6 with the truthful evidence boundary
   `INCOMPLETE_PENDING_OPUS`; prove the packet/root are immutable and contain
   exactly six attempts.

**Stop only for:** unavailable Luna/subscription access, required model/host or
spending-policy change, contradictory owner authority, or an independently
demonstrated unrepairable architecture contradiction.

### Task 9: Author, validate, review, and execute matrix Luna 14/14

Begin only after B3-v4 Luna 6/6 and its stage state are durably preserved.

1. Author a separately versioned matrix packet and root using the exact current
   compatible product/tooling surface and canonical 14-fixture order.
2. Bind separate matrix authorization, acceptance, identities, manifests,
   preflight, and independent rederiver. Do not reference the B3 root as
   campaign evidence.
3. Run deterministic/live validation, hash reconciliation, and one fresh
   read-only freeze review. Explicit PASS is required.
4. Run Luna cells 0-13 serially once each with the same per-attempt gates.
5. Apply the full ANDON/refreeze/restart loop for any failure. A repair that
   changes B3-bound surfaces also mechanically invalidates the prior B3 6/6
   and sends execution back to Task 8 on a new compatible packet.
6. At valid 14/14, run the separate matrix independent Luna rederiver and create
   the mandatory pause terminal.
7. Record valid Luna 14/14 with the truthful evidence boundary
   `INCOMPLETE_PENDING_OPUS` and explicitly report whether the fourteen cells
   remain eligible for current integration.

### Task 10: Complete historical lane and merge the qualified branches

1. Run append-only `adjudicate-one` for each of the 56 inventory-bound canonical
   bundles, preserving one create-once result per source.
2. Independently aggregate corrected candidate/control baselines, causal
   classifications, residual uncertainty, and genuine product-repair findings.
3. Reconcile any product/evaluator finding against the two frozen packets.
   Mechanically invalidate and rerun affected Luna tranches if a relevant
   repair is required; otherwise record continued matrix eligibility.
4. Verify every owner merge-gate requirement, required deterministic/package/
   CI/review evidence, and exact evaluated-surface equality for each planned
   branch integration.
5. Only then perform the already planned owner-authorized branch integrations
   and merges to `main`, and write a create-once certificate with exactly
   `LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN`.
6. If any merge changes a relevant byte, refuse the certificate and rerun the
   affected complete Luna tranche on the new exact tree.
7. Do not plan or execute Opus. Do not move/recreate the release tag, publish
   v0.3.2.0, or close claims beyond the Luna-qualified integration boundary.

## Final verification ledger

The private ledger must map every explicit requirement to authoritative
evidence: exact SHA/tree, packet and surface hashes, mission/cell roots,
terminal records, pause terminals, official and independent results, attempt
counts, stopped-prefix checks, model and host identities, package/CI/review
artifacts, 56 re-adjudication records, corrected aggregates, merge surface
comparison, and provisional certificate. Missing or indirect evidence is not
completion.
