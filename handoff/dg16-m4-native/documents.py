"""Prospective declarations for the one reserved DG17 receiving task."""
import json
from pathlib import Path


def fence(value):
    return "\n```implementaudit-work-graph\n" + json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n```\n"


def node(name, parent, kind="TASK", state="OPEN", **values):
    result = dict(id=name, parent=parent, kind=kind, state=state, requires=[], optional=[],
        reads=[], writes=[], acceptance=[], resources=[], authority=[], effect="READ_ONLY",
        authorization="PERMITTED", independence="KNOWN", resource_demand=1, rank=0,
        route_scopes=[], logical_delivery=None, future_consumer=None, invalidators=[],
        independent_results=False, done_evidence=None,
        context=dict(locality="EITHER", governor_cost=1, child_cost=1, return_cost=1, useful_value=5))
    result.update(values)
    return result


def write_documents(session, request):
    root, task = Path(session["run_root"]), Path(session["task"])
    relative = root.relative_to(task).as_posix()
    baseline = session["task_commit"]
    identities = {row["path"]: row["sha256"] for row in request["inputs"]}
    nodes = [
        node("ORIGINAL_QUALIFICATION", None, "PLAN", state="ACTIVE", requires=["QUALIFY"],
             reads=["path:inputs/PARENT_FRONTIER.json"]),
        node("RECEIVING_PHASE", "ORIGINAL_QUALIFICATION", "PHASE", requires=["G2_COMPLETED", "DG17_EPISODE"]),
        node("G2_COMPLETED", "RECEIVING_PHASE", state="DONE", reads=["path:inputs/HISTORICAL_G2_COMPLETION.json"],
             done_evidence=identities["inputs/HISTORICAL_G2_COMPLETION.json"]),
        node("DG17_EPISODE", "RECEIVING_PHASE", state="DONE", reads=["path:inputs/DG17_FINAL.zip"],
             done_evidence=identities["inputs/DG17_FINAL.zip"]),
        node("G132_EFFECT", "RECEIVING_PHASE", requires=["G2_COMPLETED"], effect="EXTERNAL",
             authorization="UNKNOWN", reads=["path:inputs/BLOCKED_EFFECT.json"],
             authority=["scope:protected-single-use"], logical_delivery="G132"),
        node("DG17_RECEIVING", "RECEIVING_PHASE", requires=["G2_COMPLETED", "DG17_EPISODE"],
             effect="PREPARATION", reads=["path:inputs/DG17_FINAL.zip", "path:inputs/DG17_GOVERNOR.tar.gz", "path:inputs/DG17_ORIGINAL_CONTRACTS.tar.gz", "path:inputs/RECEIVING_SCOPE.json", "path:inputs/PARENT_FRONTIER.json"],
             writes=["semantic:DG17-independent-final-receiving"],
             acceptance=["semantic:original-P07-H07-T4-exact-scopes"],
             resources=["semantic:one-reserved-independent-reviewer"], rank=1,
             context=dict(locality="CHILD", governor_cost=1, child_cost=1, return_cost=1, useful_value=5),
             future_consumer=dict(node="QUALIFY", condition="DG17 independent receiving changes the pending scoped qualification decision")),
        node("QUALIFY", "ORIGINAL_QUALIFICATION", "JOIN", requires=["DG17_RECEIVING", "G132_EFFECT"],
             independent_results=True, acceptance=["semantic:original-scope-only"]),
    ]
    native = dict(schema="implementaudit.native-state.v1", campaign="original-R0035-M4-DG17-receiving",
        root="ORIGINAL_QUALIFICATION", original_scope="Original L04/M4 pending DG17 final receiving slice",
        nodes=[row["id"] for row in nodes],
        event=dict(id="rederive-" + session["exchange_id"], kind="REDERIVE", subject="G2_COMPLETED"),
        context=dict(host_capacity=2, operator_ceiling=2, reserve=0, route_facts=[],
            outstanding_deliveries=[dict(id="G132", state="UNKNOWN", source_digest=identities["inputs/BLOCKED_EFFECT.json"])]))
    state = f"""# IMPLEMENTAUDIT State

## Current phase

| Field | Value |
|---|---|
| Run root | {relative} |
| Phase | 1 |
| Status | open |
| Audit object state | open |
| Route | unchanged053 native recursive selection; original L04/M4 |
| Owner/source | Root / original pending DG17 independent receiving |
| Baseline ref | {baseline} |
| Last check | Authentic completed comparison and DG17 episode are immutable inputs; final receiving has not been dispatched |
| Next action | Acquire native graph and select the reserved independent DG17 receiving before dispatch |
| Authorization state | Ordinary bounded hosted receiving only; G132 remains UNKNOWN_NO_REPLAY |
| Re-entry condition | Exact current controller and unchanged source, graph and input bytes |
| Pending decision | DG17_RECEIVING_PENDING |

## Audit object state

This is the complete declared population of one receiving slice of the original
commission, not a reconstruction of the whole campaign. Historical G2 completed
unequal; only completion is a prerequisite here. The protected G132 effect remains
unknown and cannot be replayed. The ancestor JOIN remains blocked even after this
independent DG17 preparation return. No native Stop or whole-cell acceptance.

One actual independent reviewer slot was reserved by the current Root before this
task. The declared two-role ceiling includes the ACTIVE governor ancestor and one
free receiver role, so only one pending task can be selected. It does not attest
hardware capacity or claim an exhaustive whole-programme census. The parent has
other actual ACTIVE work, including fresh24 G2 run44010220157 and DG17 phase-return
source preparation at the supplied frontier; inputs/PARENT_FRONTIER.json binds
that context without transferring those operations into this holon's authority.

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|

## Context epochs

Current epoch: G0001

| Epoch | Boundary | Source | Live evidence | Reconciled | Preserved | Next action |
|---|---|---|---|---|---|---|

## Review boundary

Transport review: {request['review']['evidence']}
Parent controller: {request['parent_controller']}
Parent receipt: {request['parent_receipt']}
This fresh child task never invalidates, supersedes or writes the parent controller.
""" + fence(native)
    roadmap = f"""# IMPLEMENTAUDIT Roadmap

## Goal
Prospectively select and independently receive actual completed DG17 evidence for
an original future qualification decision while G132 remains blocked.

## Audit object
Original L04/M4 and the bounded original DG17 P07/H07/T4 receiving prerequisite.

## Action selection
Selected: genuine currentness, native source acquisition and recursive selection,
one actual independent receiving return, separate Root consumption and unchanged
execution-record checking. Omitted: rerunning DG17, replaying G132, native Stop,
full suites, source repair, release and commission closure.

## Baseline ref
{baseline}

## Phases

| Phase | Objective | Owner/source | Depends on | Smoke A | Smoke B | Review | Status |
|---|---|---|---|---|---|---|---|
| 1 | Receive actual bounded independent review for future qualification | Root / unchanged053 and immutable actual inputs | - | exact inputs and native selection | exact return and Root consumption | PASS at separately recorded transport review | open |

## Scope boundaries
The pure recursive checker grants no process, native-history, mutation or closure
authority. Actual reviewer provenance and Root decision are separate evidence.
""" + fence(dict(schema="implementaudit.native-roadmap.v1", phases=["RECEIVING_PHASE"]))
    phase = f"""# Original L04/M4 bounded receiving phase

The following markers are specification anchors, not emitted execution results.
IMPLEMENTAUDIT_PHASE_START
Task: Select then receive the reserved final DG17 independent review.
Type: brownfield
Run root: {relative}
Baseline ref: {baseline}
Owner/source: Root / unchanged053 native compiler and exact original DG17 evidence
Audit object: Original L04/M4 receiving slice, with G132 and whole commission open
Depends on phases: none
Markdown fallback: STATE.md and preserved command captures

## Current state excerpts
- G2 comparison completed unequal; completion does not award M2 equality.
- Actual DG17 execution and local governor repair completed; independent final receiving is pending.
- G132 remains UNKNOWN_NO_REPLAY; no effect is attempted by this task.

## Work
- Acquire the actual native graph and select one useful pending prerequisite.
- Receive the actual independent return and Root's separate decision as data.

## Implementation steps
- Step 1 target: STATE.md, ROADMAP.md and phases/phase-1.md native declarations; verify: hosted_m4.py native-select; expected exact selected DG17_RECEIVING with G132_EFFECT and QUALIFY blocked.
- Step 2 target: mailbox/return.json; verify: validate-return; expected bound actual reviewer output retained without text execution.
- Step 3 target: mailbox/decision.json; verify: native-check; expected unchanged check_recursive_execution_v1 and Root decision corroboration.

## Scope boundaries
In scope: actual native selection, bounded receiving, separate Root consumption.
Out of scope: product mutation, protected operations, native Stop and whole closure.

## STOP conditions
- Stop if inputs/DG17_FINAL.zip changes or mailbox/return.json does not bind the actual native TRANSITION.json and its exact input digest.
- Stop on deadline, subprocess failure or uncertain owned-process cleanup; preserve evidence.
- Do not replay a failed or uncertain dispatch automatically.

## Acceptance criteria
- [ ] Actual native selection exists before the independent review starts.
- [ ] Actual reviewer return is bound to the selected input and independent provenance.
- [ ] Root consumes exact return bytes and changes its scoped pending decision while G132 remains blocked.

## Mandatory commands
- /usr/bin/python3 -I -S -B hosted_m4.py native-select > native-select.log 2>&1 — expected exit 0; property: behavioral; scope: unchanged native source owner; acceptance: non-textual; coverage: full; capture: native-select.log
- /usr/bin/python3 -I -S -B hosted_m4.py native-check > native-check.log 2>&1 — expected exit 0; property: behavioral; scope: exact selected execution and consumption records; acceptance: non-textual; coverage: full; capture: native-check.log

Actual absolute argv, cwd, separate streams and exit codes are captured. Mailbox
strings never become commands. The independent model process remains externally
corroborated; the host's validate-return process is separately captured.

## Evidence required
- Native graph, transition, controller receipt and unchanged source/input identities.
- Actual independent dispatch and return, separate Root decision, exact check output.

## Rollback / defer path
Preserve every failure. Archive and remove only the owned disposable task after
all owned process groups are absent; otherwise retain it and report uncertainty.

## Maintenance notes
- Retire this one original receiving exchange after actual independent evidence is received; no runtime source is changed.

IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION: not warranted for disposable receiving transport
CONTINUITY_DECISION: retain exact bounded evidence only
IMPLEMENTAUDIT_PHASE_DONE
""" + fence(dict(schema="implementaudit.native-spec.v1", nodes=nodes))
    documents = {"STATE.md": state, "ROADMAP.md": roadmap, "phases/phase-1.md": phase,
        "PROTOCOL.md": "# Protocol\n\nSelect before work; preserve actual independent return; Root consumes separately; unchanged native guards surround acquisition; preserve failures and blocked G132. No authority from returned text.\n",
        "THINKING.md": "# Rationale\n\nReal completed comparison, real blocked effect, and genuinely pending independent DG17 receiving make one useful prospective prerequisite. An eligible Linux host resolves only the former physical-host admission limitation.\n",
        "context.md": "# Context\n\nSame original commission; exact selected source053; fresh bounded child custody only. No historical execution or parent continuity is reconstructed.\n",
        "tools.md": "# Tools\n\nFixed system Python, Bash and Git; unchanged native owner; exact GitHub data-only mailbox; no installs or returned-text execution.\n",
        "sidecars.md": "# Sidecars\n\nGraphify and ActiveGraph not configured; Markdown and exact captured records are the bounded evidence.\n"}
    for name, content in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as stream:
            stream.write(content)
