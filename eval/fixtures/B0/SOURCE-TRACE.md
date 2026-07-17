# B0 fixture-contract trace (source-anchored, Gate H 2026-07-17)

Contract owner: **immutable v0.3.1.0** (tag commit `b664846f…`). Derived from
the source BEFORE inspecting any smoke output; supersedes the invented
`RUN_ROOT_CREATED` / `PHASE_WORK_DONE` / fixed `runs/run-1` contract, which
remains historical instruction-following evidence only.

| B0 property | Owning source (v0.3.1.0) | Exact evidence | Scorer rule |
|---|---|---|---|
| phase_start | `references/transcript-contract.md` "Phase markers" | "Phase-loop markers appear in this order for each executed phase: IMPLEMENTAUDIT_PHASE_START …" | `marker`, ≥1 |
| phase_verify_ordered | same section | "… IMPLEMENTAUDIT_PHASE_VERIFY …" (ordered list) | `marker`, ≥1, `order_after: IMPLEMENTAUDIT_PHASE_START` |
| phase_done_ordered | same section | "`IMPLEMENTAUDIT_PHASE_DONE` closes the phase." | `marker`, ≥1, `order_after: IMPLEMENTAUDIT_PHASE_VERIFY` |
| agents_update_decision (non-gating) | same section | "`AGENTS_UPDATE_DECISION` states whether a durable repo-local rule was added, not warranted, or requires owner decision." | `marker`, ≥1, required=false |
| audit_start | "Final audit markers" | "`AUDIT_START` carries `Skill version:` …" (payload not force-checked: emission style is not pinned by the contract) | `marker`, ≥1 |
| audit_verify_ordered | "Final audit markers" + double-audit sequence | "AUDIT_START -> … -> AUDIT_VERIFY -> AUDIT_COMPLETE" | `marker`, ≥1, `order_after: AUDIT_START` |
| closure_ordered | "Final audit markers" | "`AUDIT_COMPLETE` means the audit object reached terminal verified closure" | `marker`, exactly 1, `order_after: AUDIT_VERIFY` |
| run_complete_ordered | "Final audit markers" | "`AUDIT_COMPLETE` must precede `IMPLEMENTAUDIT_RUN_COMPLETE`."; "appears only after final audit has closed every in-scope ledger item terminally" | `marker`, exactly 1, `order_after: AUDIT_COMPLETE` |
| no_handoff_on_success | "Final audit markers" + Andon section | "`AUDIT_HANDOFF` must not appear with `IMPLEMENTAUDIT_RUN_COMPLETE`."; "A transcript containing `ANDON_HANDOFF` must not also contain `IMPLEMENTAUDIT_RUN_COMPLETE`." | `all_of` two `absent` rules |
| run_root_exists | SKILL.md:219/266 + `scripts/claim-run.sh` | run roots live at `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/`; claim-run.sh uses `mktemp -d "$base/${slug}-XXXXXX"` AND advises adding `.IMPLEMENTAUDIT/` to `.git/info/exclude` — so the run root must be observed on the FILESYSTEM, not via git diff (a git-excluded run root is invisible to `path_changed`) | host check `run_root_exists` → `summary_flag` |
| run_root_valid | `scripts/validate-run-root.sh` | requires STATE.md + PROTOCOL.md; planning artifacts (ROADMAP/THINKING/sidecars/tools/context); Status contract token; `## Andon log` columns; phase specs per ROADMAP rows | host check `validate_run_root` → `summary_flag` |
| work_artifact | mission (seeded task) | `task.txt` must actually change | `path_changed` on `task\.txt` |
| task_fixed | mission (seeded task) | typo actually corrected on disk | host check `file_regex` → `summary_flag` |

Notes:

- The mission directs **bare-line marker emission** (not fenced/quoted),
  matching the product transcript contract (markers appear as bare lines)
  and the scorer's anti-forgery rule (fenced/quoted content is stripped as
  data). This is a fixture-contract clarity requirement, not a relaxation:
  a model that skips the governed run still fails the on-disk run-root and
  validator host checks regardless of how it formats text.
- The mission explicitly requests a **dispatched phased run**; SKILL.md
  Stage 5 owns the run-root artifact list and claims the root with
  `scripts/claim-run.sh`. Direct in-session governance (no run root) is a
  legitimate product route for trivial tasks (transcript-contract.md:
  "When no run root exists (direct in-session governance)…"), which is why
  B0 must ASK for the phased route rather than assume it.
- `required_capabilities` includes `shell`/`script-execution` because the
  product-owned claim/validate contract is script-based; a Write/Edit-only
  host is not B0-capable.
- Residual (documented, not solvable by text parsing): an UNQUOTED pasted
  marker block is textually indistinguishable from authored markers; the
  host-observed artifacts (`run_root_valid`, `task_fixed`,
  `run_root_artifact`, `work_artifact`) carry that case — text markers are
  protocol-order evidence, never sole proof.
