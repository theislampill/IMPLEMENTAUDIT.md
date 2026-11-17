#!/usr/bin/env python3
"""One finite ordinary phase task, paused for actual Root data decisions.

This carries provider-bound files. It is not native/session authentication,
an assistant Stop adapter, or an arbitrary command executor.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import uuid

HERE = Path(__file__).resolve().parent
PRIMITIVES_SHA = "348bebac70e43bb8fba37e3731ab73b7bf8f99f5fbd9baf4a59cfba8a2e545c3"
primitive = HERE / "transport_primitives.py"
if primitive.is_symlink() or hashlib.sha256(primitive.read_bytes()).hexdigest() != PRIMITIVES_SHA:
    raise SystemExit("proven transport primitive bytes differ")
spec = importlib.util.spec_from_file_location("dg17_proven_transport", primitive)
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)

REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg17-final-audit-20261117"
PREFIX = "handoff/dg17-phase-return"
SOURCE = "a297957be11feb494c0ec467235794a1e0c54751"
SOURCE_TREE = "b08dc4ecf4028beeedb579a312eccae23cb5d863"
u.BRANCH = BRANCH
u.WINDOW_SECONDS = 19800
SUBJECT_PATHS = {"TASK.md", "incoming/greeting.txt", "subject/app.txt", "subject/verify.py"}
CODE_PATHS = {PREFIX + "/" + p for p in SUBJECT_PATHS | {"hosted_phase.py", "transport_primitives.py", "fixture_input.py", "phase-1.received.md.in"}} | {".github/workflows/dg17-phase-return.yml"}
STABLE_DOCS = {"PROTOCOL.md", "THINKING.md", "context.md", "tools.md", "sidecars.md"}
STAGES = {
    "dispatch": ("ready", "03-dispatch.json", "dispatch-reviewed-phase", "none", "L1"),
    "audit": ("phase-repaired", "04-phase-completion.json", "complete-phase-and-audit", "none", "L3"),
    "disturb": ("audit-clean", "05-late-input.json", "apply-declared-candidate-input", "none", "L5"),
    "reanchor": ("audit-drift", "06-reanchor.json", "reconcile-current-candidate", "evidence-mismatch", "L5"),
    "fix": ("audit-gap", "07-final-gap.json", "repair-final-record", "failed-criterion", "L5"),
    "reaudit": ("final-repaired", "08-reaudit.json", "complete-fix-and-reaudit", "none", "L5"),
}
STALE_STAGES = {"audit-drift": "reanchor"}


def identity(path):
    u.need(path.is_file() and not path.is_symlink(), "identity input is not a physical regular file")
    raw = path.read_bytes()
    return dict(bytes=len(raw), sha256=u.sha(raw))


def scripts(session):
    return Path(session["source"]) / "skills/implementaudit/scripts"


def command(session, out, label, argv, expected=0):
    result = u.run(out, label, argv, Path(session["task"]), expected=expected)
    record_path = sorted((out / "commands").glob("*.json"))[-1]
    return result, record_path.name, u.read(record_path)


def phase_hashes(session):
    root = Path(session["run_root"])
    return {p.relative_to(root).as_posix(): identity(p) for p in sorted((root / "phases").glob("*.md"))}


def remember(session):
    session["owner_identity"] = identity(Path(session["task"]) / "subject/app.txt")
    session["dependency_identity"] = identity(Path(session["task"]) / "incoming/greeting.txt")
    session["phase_files"] = phase_hashes(session)


def immutable_inputs(session, request):
    u.need(identity(Path(session["request_path"])) == session["request_identity"], "launch request bytes drifted")
    u.package_check(Path(session["source"]), request)
    u.verify_files(Path(session["source"]), request["code_members"])
    immutable = [row for row in request["subject_members"] if row["path"] not in {"subject/app.txt", "incoming/greeting.txt"}]
    u.verify_files(Path(session["task"]), immutable)
    u.need(phase_hashes(session) == session["phase_files"], "phase source drifted")
    root = Path(session["run_root"])
    u.need({p: identity(root / p) for p in STABLE_DOCS} == session["stable_documents"], "stable runtime document drifted")


def current(session, request, out):
    immutable_inputs(session, request)
    root = Path(session["run_root"])
    u.need(identity(Path(session["task"]) / "subject/app.txt") == session["owner_identity"], "owner bytes drifted")
    u.need(identity(Path(session["task"]) / "incoming/greeting.txt") == session["dependency_identity"], "dependency bytes drifted")
    token = u.claim(session, out, "require-current", "--require-current-continuity", session["controller"])
    u.need(token == session["continuity_receipt"], "current receipt differs from last observed receipt")
    command(session, out, "full-root", ["/bin/bash", scripts(session) / "validate-run-root.sh", root])
    head, _, _ = command(session, out, "task-head-current", ["/usr/bin/git", "rev-parse", "HEAD"])
    u.need(head == session["task_commit"], "task commit changed")


def blocked_observation(session, request, out):
    """Read the precisely declared failed candidate; never grant currentness."""
    immutable_inputs(session, request)
    drift = session.get("observed_drift")
    u.need(isinstance(drift, dict) and drift["stage"] in STALE_STAGES, "no exact failed observation")
    for path, expected in drift["post_files"].items():
        u.need(identity(Path(session["task"]) / path) == expected, "failed observation drifted again")
    for path, expected in drift["retained_documents"].items():
        u.need(identity(Path(session["run_root"]) / path) == expected, "failed observation state changed")
    head, _, _ = command(session, out, "blocked-live-head", ["/usr/bin/git", "rev-parse", "HEAD"])
    u.need(head == drift["post_commit"] and head != session["task_commit"], "failed candidate head differs")
    status, _, _ = command(session, out, "blocked-live-status", ["/usr/bin/git", "status", "--porcelain=v1", "--untracked-files=all"])
    u.need(status == "", "unexpected changes after declared fixture transition")
    _, _, record = command(session, out, "blocked-currentness", ["/bin/bash", scripts(session) / "claim-run.sh",
        "--require-current-continuity", session["controller"]], expected=1)
    u.need(record["output_bytes"] == 0, "refused currentness emitted a receipt")


def refresh(session, out, reason, boundary="manual-resume"):
    controller = session["controller"]
    u.claim(session, out, "current-controller", "--current-controller", controller)
    u.claim(session, out, "invalidate", "--invalidate-continuity", controller,
            "--boundary", boundary, "--event", session["exchange_id"] + "-" + str(session["epoch"] + 1))
    root = Path(session["run_root"])
    command(session, out, "read-STATE", ["/bin/cat", root / "STATE.md"])
    command(session, out, "read-ROADMAP", ["/bin/cat", root / "ROADMAP.md"])
    live_head, _, _ = command(session, out, "refresh-live-head", ["/usr/bin/git", "rev-parse", "HEAD"])
    live_tree, _, _ = command(session, out, "refresh-live-tree", ["/usr/bin/git", "rev-parse", "HEAD^{tree}"])
    session["epoch"] += 1
    epoch = f"G{session['epoch']:04X}"
    path = root / "STATE.md"
    text = re.sub(r"(?m)^Current epoch: .*$", "Current epoch: " + epoch, path.read_text())
    row = f"| {epoch} | {boundary} | {reason} | {live_head} {live_tree} | yes | immutable package and historical captures retained | affected phase and owner rechecked |\n"
    text = text.replace("\n## Review boundary", "\n" + row + "\n## Review boundary", 1)
    path.write_text(text)
    token = u.claim(session, out, "resume", "--resume-controller", controller, "--boundary", boundary, "--epoch", epoch)
    u.need(re.fullmatch(r"refs/implementaudit/continuity-receipts/[a-z0-9-]+/G[0-9A-F]{4}@[0-9a-f]{40}", token), "receipt is not exact")
    u.claim(session, out, "verify-receipt", "--verify-resume-receipt", token)
    u.claim(session, out, "require-receipt", "--require-current-continuity", controller)
    session["continuity_receipt"] = token
    remember(session)


def append_event(session, event):
    path = Path(session["run_root"]) / "evidence/governor-events.jsonl"
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def snapshot(session, request, out, stage, witnesses, extra=None):
    stale = stage in STALE_STAGES
    if stale:
        blocked_observation(session, request, out)
    else:
        current(session, request, out)
    folder = out / stage
    folder.mkdir()
    root, task = Path(session["run_root"]), Path(session["task"])
    u.save(folder / "CONTROLLER_REFS.json", u.authority_snapshot(session, out, stage))
    for name in ["STATE.md", "ROADMAP.md", *sorted(STABLE_DOCS)]:
        shutil.copyfile(root / name, folder / name)
    shutil.copyfile(root / ".claimed", folder / "claim-metadata.txt")
    shutil.copytree(root / "phases", folder / "phases")
    shutil.copytree(root / "evidence", folder / "runtime-evidence")
    shutil.copytree(task / "subject", folder / "subject")
    shutil.copytree(task / "incoming", folder / "incoming")
    shutil.copyfile(task / "TASK.md", folder / "TASK.md")
    shutil.copytree(out / "commands", folder / "commands")
    observations = []
    for witness in witnesses:
        record = u.read(out / "commands" / witness)
        observations.append(dict(argv=record["argv"], exit_code=record["exit_code"],
            stdout=(out / "commands" / record["output_file"]).read_text(),
            stderr=(out / "commands" / record["stderr"]["file"]).read_text()))
    u.save(folder / "FACTS.json", dict(task=(task / "TASK.md").read_text(),
        current_proposals={p.name: p.read_text() for p in sorted((root / "phases").glob("phase-*.md"))},
        pending_proposals=({p.name: p.read_text() for p in sorted((root / "evidence").glob("pending-revised-phase.md"))}
                           if stage == "planning-drift" else {}),
        current_greeting=(task / "incoming/greeting.txt").read_text(),
        current_deliverable=(task / "subject/app.txt").read_text(),
        current_head=session["observed_drift"]["post_commit"] if stale else session["task_commit"],
        previously_recorded_head=session["task_commit"],
        completed_phases=[int(m) for m in re.findall(r"(?m)^\| (\d+) \|.*\| done \|$", (root / "ROADMAP.md").read_text())],
        observations=observations))
    files = {p.relative_to(folder).as_posix(): identity(p) for p in sorted(folder.rglob("*")) if p.is_file()}
    binding = dict(schema="dg17.actual-phase-binding.v1", source_commit=SOURCE, source_tree=SOURCE_TREE,
        launch_commit=session["launch_commit"], run_id=session["run_id"], run_attempt="1",
        exchange_id=session["exchange_id"], controller=session["controller"], claim_id=session["claim_id"],
        continuity_receipt=session["continuity_receipt"], currentness="REFUSED" if stale else "VERIFIED",
        task_commit=session["observed_drift"]["post_commit"] if stale else session["task_commit"],
        task_tree=session["observed_drift"]["post_tree"] if stale else session["task_tree"],
        owner_identity=identity(task / "subject/app.txt"), dependency_identity=identity(task / "incoming/greeting.txt"),
        phase_files=session["phase_files"], stage=stage,
        last_mail_commit=session["last_mail_commit"], witness_command_ids=witnesses,
        observation_inventory_sha256=u.sha(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()))
    u.save(folder / "PACKET.json", dict(schema="dg17.actual-phase-observation.v1", binding=binding, files=files,
        package_members=request["package_members"], deadline_unix=session["deadline_unix"],
        task_root=str(task), run_root=str(root), source_root=session["source"],
        source_owner_scope="Exact a297 ordinary CLI owners; Root data decisions and actual command observations",
        authority="NONE_TRANSPORT_EVIDENCE_ONLY", native_Stop_claim=False, native_session_authentication=False,
        Git_custody_limit="Provider commit/blob custody is not proof of actor/session authentication or correctness.",
        expected_mail_path=PREFIX + "/mailbox/" + next((v[1] for v in STAGES.values() if v[0] == stage), "none"),
        **(extra or {})))
    session["binding"], session["stage"] = binding, stage
    u.store_session(out, session)
    emit_continue(stage not in {"reaudited", "CONTAINED"}, stage)


def emit_continue(value, stage):
    target = os.environ.get("GITHUB_OUTPUT")
    if target:
        with open(target, "a", encoding="utf-8") as stream:
            stream.write("continue=" + ("true" if value else "false") + "\n")
            stream.write("stage=" + stage + "\n")


def write_initial_documents(session, request):
    root, task = Path(session["run_root"]), Path(session["task"])
    relative = root.relative_to(task).as_posix()
    state = f"""# IMPLEMENTAUDIT State

## Current phase

| Field | Value |
|---|---|
| Run root | {relative} |
| Phase | 1 |
| Planning context | planning before dispatch |
| Status | open |
| Audit object state | open |
| Route | actual ordinary governed isolated greeting task |
| Owner/source | subject/app.txt and selected a297 governor |
| Baseline ref | {session['task_commit']} |
| Last check | Received phase and immutable inputs; no subject mutation |
| Next action | Receive actual admission before any fixture owner write |
| Authorization state | Root-controlled ordinary isolated task changes only; no protected effects or commission closure |
| Re-entry condition | Exact current controller, source, phase and owner identities |
| Pending decision | Root receives each actual observation before a subsequent action |

## Audit object state

Deliver subject/app.txt with the current incoming/greeting.txt record followed by LF, status=ready and LF, with no additional bytes.
Phase completion is distinct from the complete exact-byte obligation. Dependency inputs are read-only for the implementation. A changed dependency requires a current proposal before dispatch.

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|

## Context epochs

Current epoch: G0001

| Epoch | Boundary | Source | Live evidence | Reconciled | Preserved | Next action |
|---|---|---|---|---|---|---|

## Review boundary

Transport review: {request['review']['evidence']}
Root data actions retain actual tool provenance. JSON role strings and Git custody do not authenticate a native assistant session.
"""
    roadmap = f"""# IMPLEMENTAUDIT Roadmap

## Goal

Update the greeting operational records using the current incoming/greeting.txt dependency. The complete subject/app.txt bytes must be the greeting, LF, status=ready, LF, with no additional or missing bytes.

## Audit object

The greeting owner file and its complete final-byte obligation remain open until actual verification. Completing a phase alone cannot satisfy that obligation.

## Action selection

Selected: exact currentness, current dependency evidence, passing plan authority gates, complete greeting implementation, Smoke A/B, phase acceptance, cleanliness, exact final audit and bounded repairs only after actual Root decisions.
Omitted: diagnostic children for mechanically explicit predicates, native Stop, release, protected operations, package changes, and unrelated tests.

## Baseline ref

{session['task_commit']}

## Phases

| Phase | Objective | Owner/source | Depends on | Smoke A | Smoke B | Review | Status |
|---|---|---|---|---|---|---|---|
| 1 | Verify and update the current greeting | subject/app.txt | incoming/greeting.txt | status record | status and greeting records | PASS at separately retained review | open |

## Complete deliverable obligation

- [ ] /usr/bin/python3 -B subject/verify.py final returns exit 0 at the exact resulting owner bytes.

## Scope boundaries

Only subject/app.txt is an implementation target. Runtime records are owned by the admitted governor. Only the separately declared fixture controller may supply changed dependency or candidate inputs. Predicates and package source remain unchanged.
"""
    docs = {"STATE.md": state, "ROADMAP.md": roadmap,
        "PROTOCOL.md": (Path(session["source"]) / "skills/implementaudit/templates/PROTOCOL.md").read_text(),
        "THINKING.md": "# Rationale\n\nUse the actual existing package owners on one ordinary isolated host. Phase operational-record predicates and the complete final byte predicate have distinct scopes. Preserve every observation and wait for Root before the next action. No diagnostic child is presumed necessary.\n",
        "tools.md": "# Tools\n\nFixed /usr/bin/python3, /bin/bash and /usr/bin/git. Exact selected a297 claim/currentness, phase authority, mutation and audit owners. One declared provider mailbox. No command strings or paths are accepted from returned prose.\n",
        "sidecars.md": "# Sidecars\n\nGraphify: not configured. ActiveGraph: not configured. Markdown fallback: STATE.md, ROADMAP.md and full command captures.\n",
        "context.md": f"# Context\n\nParent controller: {request['parent_controller']}\nParent receipt at publication: {request['parent_receipt']}\nSelected source: {SOURCE}\nThe disposable task never changes parent custody. Provider file custody is separate from actor and native-session authentication.\n",
        "phases/phase-1.md": (HERE / "phase-1.received.md.in").read_text().replace("@RUN_ROOT@", relative).replace("@BASELINE_REF@", session["task_commit"])}
    for name, text in docs.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
    (root / "evidence").mkdir()
    (root / "evidence/planning-input.md").write_text("Anchor: " + session["task_commit"] + "\nGreeting input: " + (task / "incoming/greeting.txt").read_text() + "\n")
    session["stable_documents"] = {p: identity(root / p) for p in STABLE_DOCS}
    remember(session)


def prepare(args):
    out, source = args.output.resolve(), Path.cwd().resolve()
    out.mkdir(parents=True, exist_ok=True)
    u.need(not (out / "SESSION.json").exists(), "this task already started; no replay")
    request = u.read(args.request.resolve())
    u.need(request["schema"] == "dg17.finite-phase-request.v1", "request schema differs")
    u.need(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == REPOSITORY
           and os.environ.get("GITHUB_REF_NAME") == BRANCH and os.environ.get("GITHUB_RUN_ATTEMPT") == "1", "actual hosted launch identity differs")
    u.need(request["review"]["status"] == "PASS" and request["review"]["evidence"].strip(), "independent preflight review not received")
    u.need({r["path"] for r in request["subject_members"]} == SUBJECT_PATHS, "subject population differs")
    u.need({r["path"] for r in request["code_members"]} == CODE_PATHS, "executable/input publication population differs")
    u.package_check(source, request)
    u.verify_files(source, request["code_members"])
    u.need(u.sha((HERE / "phase-1.received.md.in").read_bytes()) == request["phase_template_sha256"], "phase template identity differs")
    launch = os.environ["GITHUB_SHA"]
    u.need(u.run(out, "launch-parent", ["/usr/bin/git", "rev-parse", launch + "^"], source) == SOURCE, "launch is not a direct ordinary child of a297")
    u.need(u.run(out, "selected-tree", ["/usr/bin/git", "rev-parse", SOURCE + "^{tree}"], source) == SOURCE_TREE, "selected tree differs")
    u.run(out, "package-unchanged", ["/usr/bin/git", "diff", "--exit-code", SOURCE, launch, "--", "skills", ".codex-plugin", ".claude-plugin", "package"], source)
    task = Path(tempfile.mkdtemp(prefix="dg17-governed-", dir=os.environ["RUNNER_TEMP"])).resolve()
    session = dict(schema="dg17.finite-phase-custody.v1", exchange_id=uuid.uuid4().hex, source=str(source), task=str(task),
        output=str(out), request_path=str(args.request.resolve()), launch_commit=launch, last_mail_commit=launch,
        request_identity=identity(args.request.resolve()),
        run_id=os.environ["GITHUB_RUN_ID"], run_attempt="1", controller="dg17-final-" + os.environ["GITHUB_RUN_ID"],
        epoch=0, deadline_unix=time.time() + u.WINDOW_SECONDS, stage="INITIALIZING")
    (task / ".transport-owner").write_text(session["exchange_id"])
    u.store_session(out, session)
    u.verify_files(HERE, request["subject_members"])
    for row in request["subject_members"]:
        target = task / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((HERE / row["path"]).read_bytes())
    (task / ".gitignore").write_text(".IMPLEMENTAUDIT/\n.transport-owner\n")
    command(session, out, "init-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "init", "--initial-branch=greeting-update"])
    command(session, out, "add-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "add", "TASK.md", "subject", "incoming", ".gitignore"])
    command(session, out, "commit-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=IMPLEMENTAUDIT ordinary task", "-c", "user.email=bounded-root@invalid.example", "commit", "-m", "Bind prospective greeting task inputs"])
    session["task_commit"], _, _ = command(session, out, "task-head", ["/usr/bin/git", "rev-parse", "HEAD"])
    session["task_tree"], _, _ = command(session, out, "task-tree", ["/usr/bin/git", "rev-parse", "HEAD^{tree}"])
    relative = u.claim(session, out, "claim-task", "--controller", session["controller"], "greeting-update")
    u.safe_relative(relative)
    session["run_root"] = str(task / relative)
    session["claim_id"] = dict(line.split("=", 1) for line in (Path(session["run_root"]) / ".claimed").read_text().splitlines())["claim_id"]
    write_initial_documents(session, request)
    inspected = json.loads(u.claim(session, out, "inspect-initialization", "--inspect-controller-initialization", session["controller"], "--run-root", relative))
    u.claim(session, out, "activate-controller", "--activate-controller", session["controller"], "--run-root", relative, "--expected-initialization", inspected["initialization_token"])
    refresh(session, out, "actual new hosted task admission", boundary="new-session")
    current(session, request, out)
    phase = Path(session["run_root"]) / "phases/phase-1.md"
    command(session, out, "phase-structure", ["/bin/bash", scripts(session) / "validate-phase.sh", phase])
    witnesses = [authority(session, out, 1, 1)]
    _, witness, _ = command(session, out, "planning-input-anchor", ["/bin/bash", scripts(session) / "check-evidence-anchor.sh",
        "--artifact", Path(session["run_root"]) / "evidence/planning-input.md", "--tree", session["task_commit"]])
    witnesses.append(witness)
    snapshot(session, request, out, "ready", witnesses, dict(subject_mutated=False, decision_pending=True,
        observation="Current planning input and concrete implementation authority passed; no subject write has occurred."))


def receive_decision(args):
    out = args.output.resolve()
    session = u.read(out / "SESSION.json")
    request = u.read(Path(session["request_path"]))
    stage, mailbox, action, classification, owner = STAGES[args.operation]
    u.need(session["stage"] == stage, "stage already consumed or differs")
    if stage in STALE_STAGES:
        u.need(STALE_STAGES[stage] == args.operation, "failed observation cannot dispatch")
        blocked_observation(session, request, out)
    else:
        current(session, request, out)
    head, raw, value = u.wait_mail(session, out, PREFIX + "/mailbox/" + mailbox)
    u.need(isinstance(value, dict), "decision is not an object")
    completing = args.operation in {"audit", "reaudit"} and value.get("action") == action
    needs_review = args.operation == "reaudit" and value.get("action") == action
    envelope = {"schema", "binding", "action", "record", "provenance"}
    if needs_review:
        envelope.add("independent_review")
    u.need(set(value) == envelope, "decision fields differ")
    u.need(value["schema"] == "dg17.actual-phase-decision.v1" and value["binding"] == session["binding"], "decision is stale or foreign")
    allowed_actions = {action, "retain-contained"}
    u.need(value["action"] in allowed_actions, "action is not a finite action for this stage")
    record, provenance = value["record"], value["provenance"]
    record_fields = {"classification", "witnesses", "containment", "return_owner", "owner_source", "dependencies", "acceptance", "next_action", "reason"}
    if completing:
        record_fields.add("five_s")
    u.need(isinstance(record, dict) and set(record) == record_fields, "governor record fields differ")
    u.need(record["classification"] == classification and record["return_owner"] == owner
           and record["witnesses"] == session["binding"]["witness_command_ids"], "record does not bind the actual observation/owner")
    for key in set(record) - {"classification", "return_owner", "witnesses", "five_s"}:
        u.need(isinstance(record[key], str) and 8 <= len(record[key]) <= 4096 and "\n" not in record[key] and "|" not in record[key], "record scalar malformed")
    if "five_s" in record:
        u.need(isinstance(record["five_s"], dict) and set(record["five_s"]) == {"seiri", "seiton", "seiso", "seiketsu", "shitsuke"}, "five-pillar phase boundary decision absent")
        u.need(all(isinstance(v, str) and (v == "clean" or v.startswith("deferred: ") and len(v) > 18)
                   and len(v) <= 4096 and "\n" not in v and "|" not in v for v in record["five_s"].values()), "five-pillar phase boundary disposition differs")
    fields = {"actor", "loaded_governor_source", "loaded_governor_sha256", "parent_receipt", "tool_observation", "decision_record_sha256"}
    u.need(isinstance(provenance, dict) and set(provenance) == fields and all(isinstance(v, str) and v.strip() for v in provenance.values()), "actual decision provenance missing")
    governor_sha = next(r["sha256"] for r in request["package_members"] if r["path"] == "skills/implementaudit/SKILL.md")
    u.need(provenance["loaded_governor_source"] == SOURCE + ":skills/implementaudit/SKILL.md" and provenance["loaded_governor_sha256"] == governor_sha, "declared governor source differs")
    u.need(provenance["decision_record_sha256"] == u.sha(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()), "decision record digest differs")
    if needs_review:
        review = value["independent_review"]
        keys = {"binding", "reviewer", "independence_evidence", "prompt_sha256", "result_text", "result_sha256", "tool_observation"}
        u.need(isinstance(review, dict) and set(review) == keys and review["binding"] == session["binding"], "independent review binds a different repaired candidate")
        u.need(all(isinstance(review[k], str) and 1 <= len(review[k].encode()) <= 65536 for k in keys - {"binding"}), "independent review data absent or oversized")
        u.need(re.fullmatch(r"[0-9a-f]{64}", review["prompt_sha256"]) and review["result_sha256"] == u.sha(review["result_text"].encode()), "independent review digest differs")
    if stage in STALE_STAGES:
        blocked_observation(session, request, out)
    else:
        current(session, request, out)
    location = out / "Root-decisions" / (args.operation + ".json")
    location.parent.mkdir(exist_ok=True)
    location.write_bytes(raw)
    session["last_mail_commit"] = head
    session["stage"] = "ACTION_IN_FLIGHT_" + args.operation
    u.store_session(out, session)
    append_event(session, dict(event="actual-Root-data-decision-received", stage=stage, commit=head, bytes=len(raw), sha256=u.sha(raw),
        action=value["action"], record=record, provenance=provenance, provenance_ceiling="Provider data custody, not native/session authentication"))
    if value["action"] == "retain-contained":
        if stage in STALE_STAGES:
            session["stage"] = "CONTAINED"
            u.store_session(out, session)
            emit_continue(False, "CONTAINED")
            return None
        u.state_value(session, "Status", "BLOCKED")
        u.state_value(session, "Blocker", record["reason"])
        u.state_value(session, "Containment", record["containment"])
        u.state_value(session, "Next action", record["next_action"])
        refresh(session, out, "actual Root containment decision")
        snapshot(session, request, out, "CONTAINED", record["witnesses"], dict(audit_closure=False))
        return None
    return session, request, out, value


def andon(session, operation, value):
    record = value["record"]
    path = Path(session["run_root"]) / "STATE.md"
    number = {"plan": 1, "late": 2, "fix": 3}[operation]
    phase = {"plan": "before dispatch", "late": "after clean final audit", "fix": "final audit"}[operation]
    row = f"| {number} | {operation} | {phase} | {record['classification']} | {record['reason']} | {record['containment']}; selected action={value['action']}; owner/source={record['owner_source']} | required: {record['acceptance']}; original witnesses: {','.join(record['witnesses'])} | open (rerun pending) |\n"
    text = path.read_text().replace("\n## Context epochs", "\n" + row + "\n## Context epochs", 1)
    path.write_text(text)
    u.state_value(session, "Status", "BLOCKED")
    u.state_value(session, "Last check", record["reason"])
    u.state_value(session, "Next action", record["next_action"])
    append_event(session, dict(event="Root-L4-decision-registered", operation=operation, interrupted_owner=record["return_owner"],
        owner_source=record["owner_source"], dependencies=record["dependencies"], acceptance=record["acceptance"], record=value["record"]))


def resolve_andon(session, operation, witness):
    path = Path(session["run_root"]) / "STATE.md"
    text = path.read_text()
    record = u.read(Path(session["output"]) / "commands" / witness)
    u.need(record["exit_code"] == 0 and not record["timed_out"], "deciding rerun did not pass")
    anchor, _, _ = command(session, Path(session["output"]), "andon-" + operation + "-capture-anchor", ["/usr/bin/git", "rev-parse", "HEAD"])
    u.need(anchor == session["task_commit"], "deciding rerun capture anchor changed")
    matches = [line for line in text.splitlines() if re.match(r"^\| [1-3] \| " + re.escape(operation) + r" \|", line)]
    u.need(len(matches) == 1, "actual Andon row is absent or ambiguous")
    row = matches[0].split("|")
    u.need(len(row) == 10 and row[8].strip() == "open (rerun pending)", "Andon row is not unresolved")
    row[7] = " " + row[7].strip() + "; actual resolving command=" + witness + "; stdout=" + record["output_file"] + "; stderr=" + record["stderr"]["file"] + "; Anchor: @" + anchor + " "
    row[8] = " resolved "
    path.write_text(text.replace(matches[0], "|".join(row), 1))
    append_event(session, dict(event="deciding-source-check-observed", operation=operation, witness=witness,
        return_basis="Actual prior Root decision plus current source check; original failure remains retained"))


def authority(session, out, phase, step):
    root = Path(session["run_root"])
    text, witness, _ = command(session, out, f"authority-p{phase}-s{step}", ["/bin/bash", scripts(session) / "validate-phase.sh", "--mutation-authority", root / "phases" / f"phase-{phase}.md",
        "--phase", str(phase), "--step", str(step), "--repo-root", session["task"], "--run-root", root])
    value = u.decode(text.encode())
    u.need(value["operation"] == "replace" and value["source"] == "subject/app.txt" and value["destination"] is None, "authority projection differs")
    return witness


def subject_check(session, out, label, mode, expected):
    text, witness, record = command(session, out, label, ["/usr/bin/python3", "-B", "subject/verify.py", mode], expected=expected)
    value = u.decode(text.encode())
    actual = identity(Path(session["task"]) / "subject/app.txt")
    u.need(value["check"] == mode and value["passed"] is (expected == 0) and value["sha256"] == actual["sha256"]
           and value["dependency_sha256"] == identity(Path(session["task"]) / "incoming/greeting.txt")["sha256"]
           and value["bytes"] == actual["bytes"] and record["stderr"]["bytes"] == 0, "subject check signature differs")
    capture = Path(session["run_root"]) / "evidence" / (label + ".log")
    with capture.open("xb") as stream:
        stream.write((out / "commands" / record["output_file"]).read_bytes())
    return witness


def replace_owner(session, out, phase, step, candidate, expectation):
    task, root = Path(session["task"]), Path(session["run_root"])
    before = (task / "subject/app.txt").read_bytes()
    u.need(identity(task / "subject/app.txt") == session["owner_identity"], "owner preimage drift")
    folder = root / "evidence" / f"p{phase}-s{step}"
    folder.mkdir()
    (folder / "preimage.txt").write_bytes(before)
    (folder / "candidate.txt").write_bytes(candidate)
    mutation = ["/bin/bash", scripts(session) / "apply-observed-mutation.sh", "--repo-root", task,
        "--run-root", root, "--phase", str(phase), "--step", str(step), "--preimage", folder / "preimage.txt", "--candidate", folder / "candidate.txt"]
    text, witness, _ = command(session, out, f"mutate-p{phase}-s{step}", ["/bin/bash", scripts(session) / "check-evidence-anchor.sh",
        "--mutation-window", "subject/app.txt", "--expect", expectation, "--", *mutation])
    reports = [u.decode(line.encode()) for line in text.splitlines() if line.startswith("{")]
    u.need(len(reports) == 1 and reports[0].get("status") == "COMMITTED" and reports[0].get("source_path") == "subject/app.txt"
           and reports[0].get("residue") == [], "mutation did not report exact committed owner with no residue")
    u.need((task / "subject/app.txt").read_bytes() == candidate and before != candidate, "landed owner bytes differ")
    remember(session)
    return witness


def cleanliness(session, request, out, label):
    command(session, out, label + "-added-lines", ["/bin/bash", scripts(session) / "repo-state.sh", "added-lines", session["task_commit"]])
    command(session, out, label + "-changed-files", ["/bin/bash", scripts(session) / "repo-state.sh", "changed-files", session["task_commit"]])
    command(session, out, label + "-diff-check", ["/usr/bin/git", "diff", "--check"])
    changed, _, _ = command(session, out, label + "-changed", ["/usr/bin/git", "diff", "--name-only", "HEAD"])
    status, witness, _ = command(session, out, label + "-status", ["/usr/bin/git", "status", "--porcelain=v1", "--untracked-files=all"])
    u.need(changed == "subject/app.txt" and status == "M subject/app.txt", "unrelated task changes or residue found")
    current(session, request, out)
    return witness


def fixture_transition(session, request, out, kind, stage, artifact):
    """Apply a predeclared test input, then observe the unchanged owner refusing."""
    current(session, request, out)
    task, root = Path(session["task"]), Path(session["run_root"])
    path = "incoming/greeting.txt" if kind == "dependency" else "subject/app.txt"
    before = (task / path).read_bytes()
    folder = root / "evidence" / ("fixture-" + kind)
    folder.mkdir()
    (folder / "preimage.txt").write_bytes(before)
    retained = {name: identity(root / name) for name in ("STATE.md", "ROADMAP.md")}
    staged, _, _ = command(session, out, "fixture-staged-before", ["/usr/bin/git", "diff", "--cached", "--name-only"])
    u.need(staged == "", "fixture transition found staged work")
    raw, applied, _ = command(session, out, "fixture-" + kind, ["/usr/bin/python3", "-I", "-B", HERE / "fixture_input.py", kind])
    observed = u.decode(raw.encode())
    u.need(observed["path"] == path and observed["preimage"] == dict(bytes=len(before), sha256=u.sha(before))
           and observed["postimage"] == identity(task / path) and observed["task_decision"] is False,
           "declared fixture transition does not match its actual input")
    (folder / "postimage.txt").write_bytes((task / path).read_bytes())
    changed, _, _ = command(session, out, "fixture-changed", ["/usr/bin/git", "diff", "--name-only", "HEAD"])
    u.need(changed == path, "fixture transition includes unrelated paths")
    command(session, out, "fixture-add", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "add", "--", path])
    _, committed, _ = command(session, out, "fixture-commit", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null",
        "-c", "user.name=IMPLEMENTAUDIT fixture input", "-c", "user.email=fixture-input@invalid.example",
        "commit", "-m", "Record separately declared " + kind + " fixture input"])
    head, _, _ = command(session, out, "fixture-head", ["/usr/bin/git", "rev-parse", "HEAD"])
    tree, _, _ = command(session, out, "fixture-tree", ["/usr/bin/git", "rev-parse", "HEAD^{tree}"])
    planning_witnesses = []
    if kind == "dependency":
        # Actual planning work follows the changed dependency. This pending
        # proposal is not the active phase and obtains no mutation authority.
        active = root / "phases/phase-1.md"
        draft = active.read_text().replace(session["task_commit"], head)
        draft = draft.replace("record is Hi", "record is Hello").replace("hunk:1:Hi", "hunk:1:Hello")
        draft = draft.replace("evidence/planning-input.md", "evidence/planning-input-received.md")
        pending = root / "evidence/pending-revised-phase.md"
        with pending.open("x", encoding="utf-8") as stream:
            stream.write(draft)
        retained["evidence/pending-revised-phase.md"] = identity(pending)
        _, written, _ = command(session, out, "pending-revised-proposal", ["/bin/cat", pending])
        _, validated, _ = command(session, out, "pending-revised-structure", ["/bin/bash", scripts(session) / "validate-phase.sh", pending])
        u.need(identity(active) == session["phase_files"]["phases/phase-1.md"], "pending proposal consumed before reconciliation")
        planning_witnesses = [written, validated]
        append_event(session, dict(event="pending-revised-proposal-observed", dependency=identity(task / path),
            candidate_commit=head, pending_proposal=identity(pending), active_proposal=identity(active),
            validation_witness=validated, consumed=False, mutation_authority=False))
    session["observed_drift"] = dict(stage=stage, kind=kind, old_commit=session["task_commit"],
        old_receipt=session["continuity_receipt"], post_commit=head, post_tree=tree,
        post_files={p: identity(task / p) for p in ("subject/app.txt", "incoming/greeting.txt")},
        retained_documents=retained, artifact=artifact)
    _, refused, record = command(session, out, "source-currentness-refused", ["/bin/bash", scripts(session) / "claim-run.sh",
        "--require-current-continuity", session["controller"]], expected=1)
    u.need(record["output_bytes"] == 0, "failed currentness emitted a receipt")
    _, stale, _ = command(session, out, "source-evidence-refused", ["/bin/bash", scripts(session) / "check-evidence-anchor.sh",
        "--artifact", root / artifact, "--tree", head], expected=1)
    append_event(session, dict(event="declared-fixture-input-observed", operation=kind,
        actual_input=observed, old_commit=session["task_commit"], actual_commit=head,
        retained_receipt=session["continuity_receipt"], source_refusals=[refused, stale],
        authority="NONE_TEST_INPUT_AND_OBSERVATION"))
    u.store_session(out, session)
    snapshot(session, request, out, stage, [applied, committed, *planning_witnesses, refused, stale],
        dict(observed_drift=session["observed_drift"], closure_claim=False,
             source_currentness="REFUSED", affected_product_effects="NONE_AFTER_REFUSAL"))


def dependency(args):
    received = receive_decision(args)
    if received is None:
        return
    session, request, out, value = received
    u.state_value(session, "Planning context", "revising proposal against incoming dependency")
    u.state_value(session, "Last check", "Root admitted the separately declared dependency input; proposal consumption remains withheld")
    u.state_value(session, "Next action", "Observe the actual dependency and validate the resulting proposal before dispatch")
    refresh(session, out, "actual Root admission of a controlled dependency input during planning")
    fixture_transition(session, request, out, "dependency", "planning-drift", "evidence/planning-input.md")


def adopt_observed_candidate(session):
    """Called only after receiving Root's exact failed-candidate decision."""
    drift = session["observed_drift"]
    session["task_commit"], session["task_tree"] = drift["post_commit"], drift["post_tree"]
    u.state_value(session, "Baseline ref", session["task_commit"])
    return drift


def replan(args):
    received = receive_decision(args)
    if received is None:
        return
    session, request, out, value = received
    andon(session, "plan", value)
    drift = adopt_observed_candidate(session)
    u.state_value(session, "Next action", "Establish current candidate before adopting the pending revised phase")
    refresh(session, out, "Root candidate re-anchor before active proposal adoption")
    current(session, request, out)
    root = Path(session["run_root"])
    phase = root / "phases/phase-1.md"
    (root / "evidence/planning-phase-before.md").write_bytes(phase.read_bytes())
    pending = root / "evidence/pending-revised-phase.md"
    u.need(identity(pending) == drift["retained_documents"]["evidence/pending-revised-phase.md"], "pending proposal changed after its observed planning boundary")
    phase.write_bytes(pending.read_bytes())
    (root / "evidence/planning-input-received.md").write_text("Anchor: " + session["task_commit"] + "\nGreeting input: Hello\n")
    road = root / "ROADMAP.md"
    road.write_text(road.read_text().replace("\n" + drift["old_commit"] + "\n", "\n" + session["task_commit"] + "\n", 1))
    u.state_value(session, "Next action", "Validate the revised current-input proposal and concrete source authority")
    refresh(session, out, "Root returned the actual input discrepancy to the pending proposal")
    current(session, request, out)
    command(session, out, "replanned-structure", ["/bin/bash", scripts(session) / "validate-phase.sh", phase])
    authority_witness = authority(session, out, 1, 1)
    _, evidence_witness, _ = command(session, out, "replanned-input-anchor", ["/bin/bash", scripts(session) / "check-evidence-anchor.sh",
        "--artifact", root / "evidence/planning-input-received.md", "--tree", session["task_commit"]])
    resolve_andon(session, "plan", evidence_witness)
    u.state_value(session, "Status", "open")
    u.state_value(session, "Last check", "Revised input, phase structure and concrete authority passed")
    u.state_value(session, "Next action", "Receive the current proposal before implementation dispatch")
    refresh(session, out, "actual revised proposal and deciding source evidence returned")
    session.pop("observed_drift")
    snapshot(session, request, out, "replanned", [authority_witness, evidence_witness],
        dict(subject_mutated=False, prior_input_failure_retained=True))


def dispatch(args):
    received = receive_decision(args)
    if received is None:
        return
    session, request, out, value = received
    u.state_value(session, "Phase", "1")
    u.state_value(session, "Status", "IN_PHASE")
    u.state_value(session, "Last check", "Actual Root admission of the initial current-input proposal received")
    u.state_value(session, "Next action", "Apply the admitted complete greeting and run actual phase checks")
    refresh(session, out, "actual Root dispatch after initial proposal receiving")
    current(session, request, out)
    authority(session, out, 1, 1)
    append_event(session, dict(event="IMPLEMENTAUDIT_PHASE_START", phase=1, source_commit=SOURCE,
        currentness=session["continuity_receipt"], phase_identity=session["phase_files"]["phases/phase-1.md"], actual_Root_record=value["record"]))
    a = subject_check(session, out, "smoke-A", "smoke", 0)
    task = Path(session["task"])
    greeting = (task / "incoming/greeting.txt").read_bytes()
    u.need(greeting == b"Hello", "current admitted greeting differs")
    mutation = replace_owner(session, out, 1, 1, greeting + b"\nstatus=ready\n", "hunk:1:Hello")
    functional = subject_check(session, out, "phase-1-functional", "phase", 0)
    clean = cleanliness(session, request, out, "phase-1-clean")
    b = subject_check(session, out, "phase-1-smoke", "smoke", 0)
    u.state_value(session, "Last check", "Actual implementation and scoped phase checks passed")
    u.state_value(session, "Next action", "Receive the actual phase evidence before phase completion and complete-byte audit")
    refresh(session, out, "actual clean phase evidence returned for Root receiving")
    snapshot(session, request, out, "phase-repaired", [a, mutation, functional, clean, b],
        dict(phase_completion_claim=False, exact_final_obligation="not yet verified"))


def disturb(args):
    received = receive_decision(args)
    if received is None:
        return
    session, request, out, value = received
    u.need(session["binding"]["stage"] == "audit-clean", "no clean exact audit precedes the fixture input")
    fixture_transition(session, request, out, "candidate", "audit-drift", "evidence/audit-1-anchor.md")


def reanchor(args):
    received = receive_decision(args)
    if received is None:
        return
    session, request, out, value = received
    andon(session, "late", value)
    adopt_observed_candidate(session)
    u.state_value(session, "Phase", "candidate reconciliation after completed phase")
    u.state_value(session, "Next action", "Re-establish candidate currentness before rechecking affected owner evidence")
    refresh(session, out, "Root received the actual late candidate mismatch and retained the prior clean audit")
    current(session, request, out)
    _, witness, _ = command(session, out, "reanchored-currentness", ["/bin/bash", scripts(session) / "claim-run.sh",
        "--require-current-continuity", session["controller"]])
    resolve_andon(session, "late", witness)
    u.state_value(session, "Status", "open")
    u.state_value(session, "Phase", "final audit of the changed candidate")
    u.state_value(session, "Last check", "Actual source currentness restored; previous complete-byte audit remains historical")
    u.state_value(session, "Next action", "Run the affected owner checks at the exact changed candidate")
    refresh(session, out, "actual current candidate returned to exact final verification")
    session.pop("observed_drift")
    current(session, request, out)
    append_event(session, dict(event="AUDIT_START", round=2, source_commit=SOURCE, task_commit=session["task_commit"],
        owner_identity=session["owner_identity"], previous_clean_audit_retained=True, actual_Root_record=value["record"]))
    smoke = subject_check(session, out, "audit-after-reanchor-smoke", "smoke", 0)
    functional = subject_check(session, out, "audit-after-reanchor-phase", "phase", 0)
    final = subject_check(session, out, "audit-after-reanchor-final", "final", 1)
    snapshot(session, request, out, "audit-gap", [witness, smoke, functional, final],
        dict(completed_phase_census=[1], actual_clean_predecessor_retained=True,
             observed_unresolved_obligation="Exact complete deliverable bytes", completion_claim=False))


def mark_phase_done(session, phase_number, decision):
    root = Path(session["run_root"])
    path = root / "phases" / f"phase-{phase_number}.md"
    text = path.read_text().replace("- [ ]", "- [x]").replace("Status: open", "Status: done")
    path.write_text(text)
    if phase_number == 2:
        (root / "phases/audit-fix-1.md").write_text(text)
    roadmap = root / "ROADMAP.md"
    text, count = re.subn(r"(?m)^(\| " + str(phase_number) + r" \|.*)open( \|)$", lambda m: m[1] + "done" + m[2], roadmap.read_text())
    u.need(count == 1, "phase census row absent or ambiguous")
    roadmap.write_text(text)
    append_event(session, dict(event="IMPLEMENTAUDIT_PHASE_DONE", phase=phase_number, actual_Root_record=decision["record"],
        last_observation_binding=session["binding"], audit_object_state="open"))


def audit(args):
    received = receive_decision(args)
    if received is None:
        return
    session, request, out, value = received
    append_event(session, dict(event="Root-L3-rederivation-record-received", return_owner=value["record"]["return_owner"],
        actual_Root_record=value["record"], last_observation_binding=session["binding"]))
    mark_phase_done(session, 1, value)
    u.state_value(session, "Phase", "final audit after one completed planned phase")
    u.state_value(session, "Last check", "Root L3 rederivation and phase-completion record received; full-byte obligation remains open")
    u.state_value(session, "Next action", "Root requested an exact-candidate final audit; completion remains withheld")
    refresh(session, out, "actual Root L3 return, phase completion and transition to L5 final audit")
    current(session, request, out)
    root = Path(session["run_root"])
    command(session, out, "audit-1-read-ROADMAP", ["/bin/cat", root / "ROADMAP.md"])
    package_version, _, _ = command(session, out, "audit-1-package-version", ["/bin/bash", scripts(session) / "detect-env.sh", "--package-version", Path(session["source"]) / "skills/implementaudit"])
    append_event(session, dict(event="AUDIT_START", round=1, source_commit=SOURCE, task_commit=session["task_commit"],
        package_version=package_version, owner_identity=session["owner_identity"], completed_phase_census=[1], final_obligation="open", actual_Root_record=value["record"]))
    a = subject_check(session, out, "audit-1-smoke", "smoke", 0)
    b = subject_check(session, out, "audit-1-phase", "phase", 0)
    actual = (Path(session["task"]) / "subject/app.txt").read_bytes()
    u.need(actual in (b"Hello\nstatus=ready", b"Hello\nstatus=ready\n"), "final-audit candidate is outside the admitted repaired forms")
    expected = 0 if actual == b"Hello\nstatus=ready\n" else 1
    final = subject_check(session, out, "audit-1-final", "final", expected)
    command(session, out, "audit-1-deliverable", ["/bin/bash", scripts(session) / "repo-state.sh", "deliverable", session["task_commit"], "subject/app.txt"])
    if expected == 0:
        (root / "evidence/audit-1-anchor.md").write_text("Anchor: " + session["task_commit"]
            + "\nOwner SHA256: " + session["owner_identity"]["sha256"]
            + "\nComplete successful witnesses: " + ",".join([a, b, final]) + "\n")
        append_event(session, dict(event="AUDIT_VERIFY", round=1, command_witnesses=[a, b, final],
            owner_identity=session["owner_identity"], phase_census=[1], source_commit=SOURCE,
            closure_authority="NONE_TRANSPORT", final_gap_observed=False))
        snapshot(session, request, out, "audit-clean", [a, b, final], dict(completed_phase_census=[1],
            final_gap_observed=False, independent_receiving_pending=True, completion_marker_emitted=False,
            observation="Actual complete-byte verification passed at the first final audit; no final-gap event or audit-fix is inferred."))
        return
    snapshot(session, request, out, "audit-gap", [a, b, final], dict(completed_phase_census=[1],
        observed_unresolved_obligation="Exact complete deliverable bytes", completion_claim=False,
        observation="Actual final predicate refused after the completed phase's scoped checks passed."))


def fix_phase_text(session):
    root = Path(session["run_root"])
    relative = root.relative_to(Path(session["task"])).as_posix()
    return f"""# Exact-byte audit fix

The markers below are specification anchors, not claimed execution.
IMPLEMENTAUDIT_PHASE_START
Phase: 2 of 2 — Exact-byte audit fix
Task: Repair the actually observed missing final LF without changing either operational record.
Type: brownfield
Run root: {relative}
Baseline ref: {session['task_commit']}
Owner/source: subject/app.txt
Audit object: {relative}/ROADMAP.md
Terminal object state to prove: The complete greeting file has the exact required bytes.
Depends on phases: 1
Smoke A: /usr/bin/python3 -B subject/verify.py smoke on the exact preimage before the byte mutation
Smoke B: /usr/bin/python3 -B subject/verify.py smoke after the byte correction and 5S

## Current state excerpts

- The exact retained subject/app.txt candidate has both required records and no final LF.
- audit-after-reanchor-final.log contains the actual complete-byte predicate refusal; operational checks passed at that same candidate.

## Work

Append only the missing final LF after the actual Root final-gap decision. Preserve the original finding, phase evidence and complete final predicate.

## Implementation steps (ordered)

- Step 1: Restore the required final LF — target: subject/app.txt; change: append one missing LF without changing either record; verify: /usr/bin/python3 -B subject/verify.py final; expected: exit 0
  mutation-authority: {{"operation":"replace","source":"subject/app.txt","destination":null}}

## Scope boundaries

In scope: the actual missing final LF in subject/app.txt only.
Out of scope: changing either operational record, incoming/greeting.txt, subject/verify.py, package source or unrelated files.
Mutation scope: {{"in":["subject/app.txt"],"out":["incoming/greeting.txt","subject/verify.py"]}}

## STOP conditions (plan-specific)

- Stop if subject/app.txt differs from the exact retained final-audit preimage; a changed candidate needs re-anchoring.
- Stop if subject/verify.py final remains nonzero after the one admitted byte correction; preserve its complete new failure.

## Acceptance criteria

- [ ] subject/verify.py final returns exit 0 at the exact repaired candidate.

## Mandatory commands

- /usr/bin/python3 -B subject/verify.py final > {relative}/evidence/phase-2-final.log 2>&1 — property: behavioral; scope: complete deliverable byte equality; coverage: full; capture: {relative}/evidence/phase-2-final.log; expected: exit 0

## Evidence required

- Actual Root final-gap decision and exact failed preimage.
- Complete observed-mutation result, final predicate result and status-invariant recheck.
- Markdown fallback: STATE.md and whole command captures; no sidecar is required.

## Rollback / defer path

Contain the deliverable if the bounded correction fails. Keep the original failed candidate and every result. Root must make a new actual decision before any further write; the committed mutation step is never replayed.

## Maintenance notes

- This is a bounded final-audit correction; no package or durable AGENTS change is inferred.

IMPLEMENTAUDIT_PHASE_VERIFY
Actual outcomes are recorded only after commands return.
AGENTS_UPDATE_DECISION
No durable repo-specific learning is presumed.
CONTINUITY_DECISION
Only the existing source owner issues currentness receipts.
IMPLEMENTAUDIT_PHASE_DONE
Status: open
"""


def fix(args):
    received = receive_decision(args)
    if received is None:
        return
    session, request, out, value = received
    andon(session, "fix", value)
    root = Path(session["run_root"])
    text = fix_phase_text(session)
    for name in ["phase-2.md", "audit-fix-1.md"]:
        with (root / "phases" / name).open("x", encoding="utf-8") as stream:
            stream.write(text)
    roadmap = root / "ROADMAP.md"
    text = roadmap.read_text().replace("\n## Complete deliverable obligation", "\n| 2 | Repair the actual exact-byte gap | subject/app.txt | 1 | retained exact failed final predicate | exact final and status checks | Root bounded decision received | open |\n\n## Complete deliverable obligation", 1)
    roadmap.write_text(text)
    u.state_value(session, "Phase", "2")
    append_event(session, dict(event="AUDIT_GAPS", round=2, actual_Root_record=value["record"],
        exact_failed_candidate=session["binding"]["owner_identity"], audit_fix="phases/audit-fix-1.md", canonical_mutation_phase="phases/phase-2.md"))
    refresh(session, out, "actual Root final-gap decision and bounded audit-fix plan")
    current(session, request, out)
    authority(session, out, 2, 1)
    append_event(session, dict(event="IMPLEMENTAUDIT_PHASE_START", phase=2, source_commit=SOURCE,
        currentness=session["continuity_receipt"], phase_identity=session["phase_files"]["phases/phase-2.md"], actual_Root_record=value["record"]))
    before = (Path(session["task"]) / "subject/app.txt").read_bytes()
    u.need(before == b"Hello\nstatus=ready", "exact final-gap preimage differs")
    baseline = subject_check(session, out, "phase-2-smoke-A", "smoke", 0)
    mutation = replace_owner(session, out, 2, 1, before + b"\n", "anchor:status=ready\n")
    b = subject_check(session, out, "phase-2-final", "final", 0)
    clean = cleanliness(session, request, out, "phase-2-clean")
    a = subject_check(session, out, "phase-2-smoke", "smoke", 0)
    resolve_andon(session, "fix", b)
    u.state_value(session, "Status", "IN_PHASE")
    u.state_value(session, "Last check", "Actual bounded byte repair passed; independent exact-candidate re-audit still pending")
    u.state_value(session, "Next action", "Root receives repaired candidate and separate audit evidence before requesting exact re-audit")
    refresh(session, out, "actual bounded audit-fix evidence returned to Root")
    snapshot(session, request, out, "final-repaired", [baseline, mutation, a, b, clean], dict(phase_completion_claim=False, re_audit_pending=True, closure_claim=False))


def reaudit(args):
    received = receive_decision(args)
    if received is None:
        return
    session, request, out, value = received
    mark_phase_done(session, 2, value)
    u.state_value(session, "Phase", "exact-candidate re-audit")
    u.state_value(session, "Next action", "Perform actual exact-candidate re-audit requested by Root; original commission acceptance remains separate")
    refresh(session, out, "actual Root audit-fix completion and exact re-audit decision")
    current(session, request, out)
    root = Path(session["run_root"])
    command(session, out, "audit-3-read-ROADMAP", ["/bin/cat", root / "ROADMAP.md"])
    package_version, _, _ = command(session, out, "audit-3-package-version", ["/bin/bash", scripts(session) / "detect-env.sh", "--package-version", Path(session["source"]) / "skills/implementaudit"])
    append_event(session, dict(event="AUDIT_START", round=3, source_commit=SOURCE, task_commit=session["task_commit"],
        package_version=package_version, owner_identity=session["owner_identity"], actual_Root_record=value["record"]))
    a = subject_check(session, out, "audit-3-smoke", "smoke", 0)
    b = subject_check(session, out, "audit-3-phase", "phase", 0)
    c = subject_check(session, out, "audit-3-final", "final", 0)
    clean = cleanliness(session, request, out, "audit-3-clean")
    command(session, out, "audit-3-deliverable", ["/bin/bash", scripts(session) / "repo-state.sh", "deliverable", session["task_commit"], "subject/app.txt"])
    append_event(session, dict(event="AUDIT_VERIFY", round=3, command_witnesses=[a, b, c, clean],
        owner_identity=session["owner_identity"], phase_census=[1, 2], source_commit=SOURCE,
        closure_authority="NONE_TRANSPORT", original_findings_retained=True))
    snapshot(session, request, out, "reaudited", [a, b, c, clean], dict(exact_reaudit_observed=True,
        original_acceptance="Root and separate independent receiving only", original_audit_object="OPEN",
        completion_marker_emitted=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["prepare", *STAGES, "finalize"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    args = parser.parse_args()
    try:
        if args.operation == "finalize":
            u.finalize(args)
        else:
            globals()[args.operation](args)
    except Exception as exc:
        args.output.mkdir(parents=True, exist_ok=True)
        path = args.output / ("FAILURE-" + args.operation + ".json")
        if not path.exists():
            u.save(path, dict(operation=args.operation, failure_type=type(exc).__name__, detail=str(exc),
                at_unix=time.time(), audit_closure=False, replay_authorized=False))
        print(f"{args.operation} refused: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
