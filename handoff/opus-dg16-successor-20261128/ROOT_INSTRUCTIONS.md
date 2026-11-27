# Issuing the DG16 IMAGE23 successor (Root)

## What the successor is

The base is `2af600fad0e80fa71d9f808741bd74db792308b2`, the operator that uses the create-event trigger. Its branch `engineering/pro-dg16-image23-main-20261127-02` is spent: run 46046841410 refused at the prepare step with `SELECTED_ENGINE_BINDINGS_DIFFER_FROM_ASSEMBLY`.

The successor changes only the following:
- **Branch literals.** The 22 occurrences of the `-02` branch name, and its `-control` form, become the new branch name.
- **Trigger.** The trigger stays as it is in the base: `on: create`, plus the job `if` and the env guard. It accepts image 23.1 only.
- **Executor binding.** The `scripts/work-graph-c5-executor.py` binding is updated in three files: `operation.py`, `g3_receiving.py` and `proof_consumer.py`. The builder derives the new value by loading the pinned engine from fc2e416c; it is 108100 bytes, sha256 `5c74e75e…`.
- **New offline control.** The new test `tests/test_load_selected.py` checks that this cannot recur.
- **Root records and dependent pins.** The three Root records are inserted, and every pin that depends on them is recomputed.

The builder is `rebuild_successor.py` and runs on Linux only. It needs:
- `REPO`: a git repository that contains `2af600fa`;
- `SRC`: a clean checkout of `fc2e416c5da38eb370045561f5281a846785ec3e`.

## 1. Choose the times (the builder enforces these)

**The builder refuses the policy if either of these holds:**
- `expires_unix_ms <= now + 60 min`;
- `issued_unix_ms > now + 10 min`.

The prepare step and its closing re-check must both fall inside `issued`..`expires`. Both happen minutes after the trigger.

How to choose:
- Issue the policy at or just before the moment you build and trigger.
- Set `expires = issued + 390 min`.
- If you miss the window, reissue the policy with new times and redo steps 2–4. The manifest changes, and so does the bootstrap admission.

## 2. Phase A: the policy and the composition admission

1. Generate drafts:

   ```
   python3 rebuild_successor.py --repo REPO --source-root SRC draft --issued <YYYY-MM-DDTHH:MM:SSZ> --out DRAFTS
   ```

   The drafts are derived from `2af600fa`'s own records. Only these fields change:
   - the branch, in `operation.branch`, `workflow_branch` and `control_branch`;
   - the times;
   - the manifest digest.

   `profile_ids` stays `["G1_UBUNTU24_20261122_23_1"]`.

2. Issue the two records into a new directory `ISSUED`:
   - `G1_HOST_PROFILE_POLICY.json`
   - `COMPOSITION_ROOT_ADMISSION.json`

   Both use canonical compact JSON: sorted keys, `,` and `:` separators, ASCII, one trailing newline.

3. Run phase 1:

   ```
   python3 rebuild_successor.py --repo REPO --source-root SRC build --records ISSUED
   ```

   This exits with code 3 (`PHASE1_BOOTSTRAP_ADMISSION_REQUIRED`). The output prints `manifest_sha256` and the exact bytes of `expected_bootstrap_admission`.

## 3. Phase B: the bootstrap admission and the build

1. Issue `BOOTSTRAP_ADMISSION.json` with the printed body. Its `manifest_sha256` must match the value from phase 1.
2. Save it into `ISSUED`.
3. Build:

   ```
   python3 rebuild_successor.py --repo REPO --source-root SRC build --records ISSUED \
       --local-branch local/dg16-successor-build --tests --report REPORT.json
   ```

4. Read the exit code:
   - **0:** built. `REPORT.json` gives the commit, the tree and `intended_trigger`.
   - **2:** refused. The message names the consumer check that failed.
   - **3:** the bootstrap admission does not bind the current manifest.

What a successful build has already checked:
- the real pinned consumers ran;
- `operation.load_selected(SRC)` passed;
- `runtime_preflight.selection` passed;
- the gate scripts accept 23.1 only;
- no test regressed against `2af600fa`, and the new control is green.

## 4. Trigger: once, by `git push`

Run exactly the `intended_trigger` from the report:

```
git push origin <commit>:refs/heads/engineering/dg16-image23-main-20261128-01
```

Before running it, make sure:
- **The commit object is not on GitHub.** Pushing uploads the commit and creates the branch in one atomic step.
- **No review copy was ever pushed as a branch.** The create event fires for any new branch whose commit contains this workflow. A review-copy branch would start a run that the job `if` then skips. Review copies travel as bundles only.
- **The trigger branch is absent and has zero runs.** This check applies to the trigger branch only.

Why not create the branch through the API instead: the create event fires for both routes. However, the API needs the commit to be on GitHub already, and putting it there would mean pushing some other branch first. So `git push` is the only clean route.

## 5. Never delete or recreate the trigger branch

The workflow is single use only because the create event fires exactly once per branch creation. The guards on `create` / `ref_type == branch`, together with `run_attempt == 1`, rely on that.

- Never delete the trigger branch and push it again.
- Never re-run the job.
- A failed or refused run spends the branch name permanently.

## 6. A later attempt on a new branch

Pass `--branch` to both `draft` and `build`:

```
--branch engineering/dg16-image23-main-YYYYMMDD-NN
```

The control branch is always the branch name followed by `-control`.

The builder refuses:
- `engineering/pro-dg16-image23-main-20261127-01` (spent);
- `engineering/pro-dg16-image23-main-20261127-02` (spent);
- any name without the prefix `engineering/dg16-image23-main-`;
- names ending in `-control`.

Root then issues fresh records for that branch (steps 1–3) and reruns the builder once.
