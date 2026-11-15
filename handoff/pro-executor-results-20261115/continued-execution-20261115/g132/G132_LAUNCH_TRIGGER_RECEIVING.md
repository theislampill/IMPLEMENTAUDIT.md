# G132 actual branch publication and absent-run receipt

Receiver: `/root/g2_receiving`. This receives actual retained provider results and identifies the earliest unreceived execution predicate. It is evidence, not launch/retry/acceptance authority. Root performed the one branch creation; this receiver performed no mutation, sender, key operation, replay, preflight, or qualification run.

## Finding G132-TRIGGER-01 — blocker before host execution

**Observed scope:** the exact host32 branch exists at approved commit `434f12f038da9420f9addaf2fed7178e1e41e20f`. Both authenticated post-create run queries returned `total_count: 0` and an empty `workflow_runs` array. This proves absence in those observations, not permanent absence or a failed host job. No run ID, job, live request, hold interval, sender, or terminal outcome follows from branch creation alone.

**First missing predicate:** an actual qualifying `push` event and resulting attempt-1 workflow run at the selected host identity. The exact workflow subscribes only to `push` on `pro/dg16-g1-original-g3-32-20261114`, with an additional path filter selecting its own workflow file or either G1 qualification directory. The qualify job requires the same repository, push event, exact branch, non-deletion and attempt 1. `bootstrap_entry.py::context` independently requires push, exact branch, attempt 1, qualify job, hosted environment and workflow SHA currentness. No `create` or `workflow_dispatch` entry exists.

**Owner/source:** the connector launch operation creates a Git reference from an existing SHA. The current trigger source is `.github/workflows/dg16-r5-g1-hosted-episode.yml` at approved host434, 35,377 bytes, SHA256 `8a51712d471aac57952b01b90623c99cd9fa8ab10109c153de222f50d55f831f`. The missing run is upstream of every Python host consumer.

**Reproduction from retained originals:** decode each actual `CallToolResult.structuredContent.content`; verify the ref object is a commit at host434, then read the two distinct run-list objects. Read the workflow's `on` object and qualify condition, and the bootstrap's `BOOTSTRAP_CONTEXT` predicate. No execution is needed to reproduce this comparison.

**Implication:** no currently exposed operation was identified that is guaranteed to start exact host434 while leaving the now-existing ref unchanged and avoiding a reset. An update to the same SHA introduces no changed path. A new commit changes the approved host identity; another branch misses the exact filter. Rerun APIs require a run/job that does not exist in the received evidence. Manual workflow dispatch is absent from both the connector capability inventory and the selected workflow, and the existing job/bootstrap reject a non-push event.

**Correction boundary:** preserve the successful branch publication and do not repeat it. A separately reviewable continuation would need a real fast-forward push with a matching path change and truthful ancestry from host434, complete existing consumer pin closure, and an exact owner decision for its changed protected host identity. This report does not authorize that push. Root subsequently authorized preparation of that isolated engineering candidate only.

## Actual retained evidence

All five originals are under the fixed operator's `public-receiver-02/current-execution/` directory. The intent is 39,620 bytes and includes the full prelaunch provider results; its commit response joins host434 to tree `e81ffaf2959df5da5a6203b66b0b3e0819eae82c` and sole product parent `e76a07b2bae7c945e5a9d529ed8cf9069f4c9064`.

| Original | SHA256 | Supported observation |
| --- | --- | --- |
| `LAUNCH_INTENT.json` | `c2099273dd87de38e8638a67a6cac1831111596699dcd14c3475c4c29655a1d2` | Exact authorized subject; no in-progress runs; sole queued run43098152901; exact tools/carrier parents; pre-create host/G3 refs absent |
| `LAUNCH_RESULT.json` | `df869064edf12844932eaf10023bd4d9427f1e6cb8fc3e7c2dd0939b5293ec9b` | Successful branch creation response; no commit/run field in this response |
| `POST_CREATE_REF.json` | `aeda4252be92f1bf09d831261055dbd36321ca0e4a6c4659d0fe48caf41f2e3e` | Exact host32 ref points to host434 |
| `POST_CREATE_RUNS.json` | `9fc6ca67f05963c2cc05e0fd45210e26dadeeb4df52fad31d6c8ccb7646bfad4` | Branch-filtered repository run list empty |
| `POST_CREATE_EXACT_HEAD_RUNS.json` | `c4c701bc0e5c440cf34ebef18b783617d6edf9f4a34b854b916073b87a081d6f` | Host434-filtered repository run list empty |

The surviving actual controller `STATE.md` at `/workspace/scratch/0269e6626329/dg16/.IMPLEMENTAUDIT/runs/pro-execution-restoration-c8fCFS/STATE.md`, read at SHA256 `e05aba385e95ca1ceff5b62b737bd2c0a50f053bf2e5b6eca736e7f3fd98ee3c`, records the analogous earlier host21 incident: branch creation produced no run; an independently reviewed later commit/ref transition produced run43703658937. That is corroborating history, not authority to repeat that transition here or to alter the current one-launch limit.

## What is and is not established about the provider cause

[GitHub's trigger documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) distinguishes reference creation from a push, and explains that both branch and path filters must match. [The workflow syntax documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#git-diff-comparisons) states that a filtered workflow does not run when no files change. [The dispatch API documentation](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event) requires a workflow configured for that event.

These contracts and the actual empty run lists support the trigger-gap diagnosis. They do not reveal GitHub's internal event handling for the particular branch creation. Two bounded diagnostic reads—workflow-state metadata and repository event history—were rejected by the connector with `INVALID_ARGUMENT` because those URL endpoints are outside its allowed fetch surface. Their actual error results are retained as `WORKFLOW_STATE_READ_REFUSAL.json` and `RECENT_EVENTS_READ_REFUSAL.json`. No alternate route was used to evade that restriction; disabled-workflow state and an actual create/push event payload were not received. A delayed genuine run remains possible and must be received if it appears.

Original product/input scopes, the 300000 ms pre-sender floor, no-reset/no-new-G restrictions, all existing consuming guards, and the absence of original acceptance remain unchanged by this receipt.
