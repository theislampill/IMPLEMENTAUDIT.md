#!/usr/bin/env python3
"""One fixed package-bundle task and one later supplied-profile revision.

Provider files carry actual observations and Root decisions. No returned text
is executed. This transport has no native assistant or Stop authority.
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
SOURCE = "a297957be11feb494c0ec467235794a1e0c54751"
SOURCE_TREE = "b08dc4ecf4028beeedb579a312eccae23cb5d863"
REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg17-positive-bundle-20261117"
PREFIX = "handoff/dg17-positive-bundle"
HELPER_SHA = "6ccd3ea2e1501cd76a054b01ff0839d9fde53fc67602c820e0f36720a7a2cc28"
helper = HERE / "hosted_phase.py"
if helper.is_symlink() or hashlib.sha256(helper.read_bytes()).hexdigest() != HELPER_SHA:
    raise SystemExit("Frozen fixed helper differs")
spec = importlib.util.spec_from_file_location("dg17_fixed_phase_helper", helper)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
u = h.u
u.BRANCH = BRANCH
NAMES = {1: "inventory", 2: "owners", 3: "guide"}
OUTPUTS = {n: "output/" + name + ".json" for n, name in NAMES.items()}
SUBJECT = {"TASK.md", "subject/build.py", "subject/verify.py", "inputs/package-members.json",
           "inputs/profile.json", *OUTPUTS.values()}
STATIC = {"PROTOCOL.md", "THINKING.md", "context.md", "tools.md", "sidecars.md", "applied-context.md"}
SCOPES = {n: {"in": [OUTPUTS[n]], "out": ["subject", "inputs", "skills", "package"]} for n in NAMES}
STAGES = {
    "first": ("prepared", "01-first.json", "begin-inventory"),
    "second": ("inventory-checked", "02-second.json", "accept-inventory-and-begin-index"),
    "third": ("owners-checked", "03-third.json", "accept-index-and-begin-guide"),
    "audit": ("guide-checked", "04-audit.json", "accept-guide-and-audit-bundle"),
    "close": ("audited", "05-close.json", "close-current-bundle"),
    "dependency": ("baseline-closed", "06-dependency.json", "supply-profile"),
    "replan": ("dependency-arrived", "07-replan.json", "accept-profile-and-replan-guide"),
    "update": ("replanned", "08-update.json", "begin-current-guide"),
    "audit_update": ("updated-guide-checked", "09-audit-update.json", "accept-current-guide-and-audit"),
    "close_update": ("update-audited", "10-close-update.json", "close-current-bundle"),
}
COMPLETIONS = {"second": 1, "third": 2, "audit": 3, "audit_update": 3}


def identity(path, physical=False):
    result = h.identity(path)
    if physical:
        stat = path.stat()
        result.update(inode=stat.st_ino, mtime_ns=stat.st_mtime_ns)
    return result


def command(session, out, label, argv, expected=0):
    return h.command(session, out, label, argv, expected)


def scripts(session):
    return h.scripts(session)


def owner_identities(session):
    task = Path(session["task"])
    return {path: identity(task / path) for path in OUTPUTS.values()}


def remember(session):
    session["owner_identity"] = owner_identities(session)
    session["phase_files"] = h.phase_hashes(session)


h.remember = remember


def bundle(session, number):
    root, task = Path(session["run_root"]), Path(session["task"])
    paths = {"phase": root / "phases" / f"phase-{number}.md",
             "output": task / OUTPUTS[number],
             "completion": root / "evidence" / f"phase-{number}-completion.json",
             "phase_report": root / "evidence" / f"phase-{number}-report.md"}
    for name in ("smoke-a", "mandatory", "smoke-b"):
        paths[name] = root / "evidence" / f"phase-{number}-{name}.log"
    return {key: dict(path=str(path.relative_to(task)), **identity(path, physical=True)) for key, path in paths.items()}


def current(session, request, out):
    u.need(identity(Path(session["request_path"])) == session["request_identity"], "Request bytes drifted")
    u.package_check(Path(session["source"]), request)
    u.verify_files(Path(session["source"]), request["code_members"])
    u.verify_files(Path(session["task"]), [r for r in request["subject_members"] if r["path"] not in OUTPUTS.values()])
    u.need(owner_identities(session) == session["owner_identity"], "Report preimage drifted")
    u.need(h.phase_hashes(session) == session["phase_files"], "Phase specification drifted")
    root = Path(session["run_root"])
    u.need({name: identity(root / name) for name in STATIC} == session["static_documents"], "Stable runtime source drifted")
    u.need(identity(Path(session["profile"])) == session["profile_identity"], "Current profile drifted")
    if "preserved_bundles" in session:
        u.need({str(n): bundle(session, n) for n in (1, 2)} == session["preserved_bundles"], "Unaffected formal phase evidence changed")
    if "baseline_archive" in session:
        u.need({name: identity(root / "evidence/closed-baseline" / name) for name in session["baseline_archive"]}
            == session["baseline_archive"], "Earlier scoped closure archive changed")
    token = u.claim(session, out, "require-current", "--require-current-continuity", session["controller"])
    u.need(token == session["continuity_receipt"], "Current receipt changed")
    command(session, out, "full-root", ["/bin/bash", scripts(session) / "validate-run-root.sh", root])
    head, _, _ = command(session, out, "task-head", ["/usr/bin/git", "rev-parse", "HEAD"])
    u.need(head == session["task_commit"], "Task baseline commit changed")


def refresh(session, out, reason, boundary="manual-resume"):
    h.refresh(session, out, reason, boundary)


def event(session, value):
    h.append_event(session, value)


def frontier(session, active=None):
    done = session["completed"]
    remaining = [n for n in NAMES if n not in done]
    ready = [n for n in remaining if n != active and (n in (1, 2) or {1, 2} <= set(done))]
    blocked = [n for n in remaining if n != active and n not in ready]
    value = {"DONE": list(done), "ACTIVE": [] if active is None else [active], "READY": ready, "BLOCKED": blocked}
    u.need(sum(len(v) for v in value.values()) == 3 and len(set(sum(value.values(), []))) == 3, "Phase census is not closed")
    u.state_value(session, "Frontier", json.dumps(value, sort_keys=True, separators=(",", ":")))
    return value


def snapshot(session, request, out, stage, witnesses, extra=None):
    current(session, request, out)
    folder = out / stage
    folder.mkdir()
    root, task = Path(session["run_root"]), Path(session["task"])
    u.save(folder / "CONTROLLER_REFS.json", u.authority_snapshot(session, out, stage))
    for name in ["STATE.md", "ROADMAP.md", *sorted(STATIC)]:
        shutil.copyfile(root / name, folder / name)
    for name in ("phases", "evidence"):
        shutil.copytree(root / name, folder / name)
    for name in ("subject", "inputs", "output"):
        shutil.copytree(task / name, folder / name)
    shutil.copyfile(task / "TASK.md", folder / "TASK.md")
    shutil.copyfile(root / ".claimed", folder / "claim-metadata.txt")
    if (root / "final-report.md").exists():
        shutil.copyfile(root / "final-report.md", folder / "final-report.md")
    shutil.copytree(out / "commands", folder / "commands")
    files = {p.relative_to(folder).as_posix(): identity(p) for p in sorted(folder.rglob("*")) if p.is_file()}
    binding = dict(schema="dg17.package-bundle-binding.v1", source_commit=SOURCE, source_tree=SOURCE_TREE,
        launch_commit=session["launch_commit"], run_id=session["run_id"], run_attempt="1",
        exchange_id=session["exchange_id"], case_identity=session["case_identity"], controller=session["controller"],
        claim_id=session["claim_id"], continuity_receipt=session["continuity_receipt"], task_commit=session["task_commit"],
        task_tree=session["task_tree"], output_identities=session["owner_identity"], phase_files=session["phase_files"],
        profile_identity=session["profile_identity"], profile_path=str(Path(session["profile"]).relative_to(task)),
        authorization_scope_sha256=session["authorization_scope_sha256"], completed_phases=session["completed"],
        stage=stage, last_mail_commit=session["last_mail_commit"], witness_command_ids=witnesses,
        observation_inventory_sha256=u.sha(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()))
    u.save(folder / "PACKET.json", dict(schema="dg17.package-bundle-observation.v1", binding=binding, files=files,
        package_members=request["package_members"], deadline_unix=session["deadline_unix"], task_root=str(task),
        run_root=str(root), source_root=session["source"], authority="NONE_TRANSPORT_EVIDENCE_ONLY",
        native_Stop_claim=False, native_session_authentication=False,
        custody_limit="Provider file custody does not authenticate a model actor/session or establish semantic acceptance.",
        expected_mail_path=PREFIX + "/mailbox/" + next((v[1] for v in STAGES.values() if v[0] == stage), "none"),
        **(extra or {})))
    session["binding"], session["stage"] = binding, stage
    u.store_session(out, session)
    h.emit_continue(stage not in {"update-closed", "CONTAINED"}, stage)


def phase_text(session, number):
    task, root = Path(session["task"]), Path(session["run_root"])
    relative = root.relative_to(task).as_posix()
    name, owner = NAMES[number], OUTPUTS[number]
    depends = "1, 2" if number == 3 else "none"
    target_schema = {1: "package-inventory.v1", 2: "operating-owner-index.v1", 3: "operating-guide.v1"}[number]
    return f"""# Generate the {name} report

Specification markers below are anchors, not execution claims.
IMPLEMENTAUDIT_PHASE_START
Phase: {number} of 3 — {name} report
Task: Generate the declared {name} report from exact admitted inputs.
Type: brownfield
Run root: {relative}
Baseline ref: {session['task_commit']}
Owner/source: subject/build.py generation owner; {owner} generated output
Audit object: {relative}/ROADMAP.md
Auditing operation: Generate, land and independently verify one report.
Terminal object state to prove: The actual report passes its declared complete acceptance check.
Depends on phases: {depends}
Smoke A: /usr/bin/python3 -B subject/verify.py integrity --package-root {session['source']} --profile inputs/profile.json before mutation
Smoke B: /usr/bin/python3 -B subject/verify.py integrity --package-root {session['source']} --profile inputs/profile.json after acceptance and cleanliness

## Current state excerpts

- {owner} initially contains only a pending status object and final newline.
- The package and generator are unchanged input owners; generated bytes come from the actual generator stdout.

## Work

Run the declared generator for {name}, preserve its complete result as the candidate, and land only that candidate with the packaged observed mutation owner. Independently inspect the resulting report. Keep unrelated files and input owners unchanged.

## Implementation steps (ordered)

- Step 1: Generate and land the {name} report — target: {owner}; change: replace pending bytes with the complete subject/build.py {name} output; verify: /usr/bin/python3 -B subject/verify.py {name} --package-root {session['source']} --profile inputs/profile.json; expected: exit 0 and passed true; landed: occurrences:1:{target_schema}
  mutation-authority: {{"operation":"replace","source":"{owner}","destination":null}}

## Scope boundaries

In scope: generated {owner} only, plus the existing runtime evidence records.
Out of scope: all package source, the generator, verifier, inputs and unrelated files; no external or protected effects.
Mutation scope: {json.dumps(SCOPES[number], separators=(',', ':'))}

## STOP conditions (plan-specific)

- Stop if a package/input, source preimage or currentness identity differs from the admitted observation.
- Stop if generation, observed landing, mandatory acceptance, cleanliness or Smoke B fails; retain every original capture.

## Acceptance criteria

- [ ] The actual {owner} passes subject/verify.py {name} against the admitted inputs.

## Mandatory commands

- /usr/bin/python3 -B subject/verify.py {name} --package-root {session['source']} --profile inputs/profile.json > {relative}/evidence/phase-{number}-mandatory.log 2>&1 — property: behavioral; scope: complete {name} report; coverage: full; capture: {relative}/evidence/phase-{number}-mandatory.log; expected: exit 0

## Evidence required

- Full generator stdout, mutation preimage/candidate/native transaction, actual command stdout/stderr/status and exact report hashes.
- Baseline/after-state integrity captures and five-pillar disposition based on the actual touched tree.
- Root's received decision and its actual fresh neutral-model return remain distinct from command evidence.
- Markdown fallback: the run-root records and complete command captures; no sidecar is configured.

## Rollback / defer path

Contain consumption on any failed check. Preserve exact prior bytes and captures. Any later replacement requires a fresh admitted step and current preimage; a committed step cannot be replayed.

## Maintenance notes

- Preserve generator-first production and the independent report verifier.

IMPLEMENTAUDIT_PHASE_VERIFY
Actual verification will be recorded after execution.
AGENTS_UPDATE_DECISION
No new persistent rule is presumed.
CONTINUITY_DECISION
Only the actual owner can establish currentness.
IMPLEMENTAUDIT_PHASE_DONE
Status: open
"""


def write_documents(session, request):
    root, task = Path(session["run_root"]), Path(session["task"])
    relative = root.relative_to(task).as_posix()
    state = f"""# Package bundle state

## Current phase

| Field | Value |
|---|---|
| Run root | {relative} |
| Phase | 1 |
| Status | open |
| Audit object state | open |
| Audit object identity | {session['case_identity']} |
| Owner/source | subject/build.py and the three declared generated reports |
| Baseline ref | {session['task_commit']} |
| Last check | Immutable inputs and phase specifications received; no report mutation |
| Next action | Root receives actual planning/currentness observations before dispatch |
| Authorization state | Isolated bundle reports and runtime records only; unchanged declared scope |
| Re-entry condition | Exact controller receipt, package, input, phase and output identities |
| Completed phases | none |

## Audit object state

Produce the exact complete package operating bundle for the current supplied profile. Phase completion alone does not close this object.

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|

## Context epochs

Current epoch: G0001

| Epoch | Boundary | Source | Live evidence | Reconciled | Preserved | Next action |
|---|---|---|---|---|---|---|

## Review boundary

Independent preparation review: {request['review']['evidence']}
Every governor decision requires an actual fresh neutral-model result, then a separate Root receiving/encoding. Provider JSON role labels are not native actor authentication.
"""
    roadmap = f"""# Package operating bundle

## Goal

Produce a complete source-derived package inventory, independent operating-owner index, and current-profile guide with explicit exact-byte acceptance.

## Audit object

Three generated reports and their actual acceptance evidence. No parent commission, issue, release or host-native claim is included.

## Action selection

Selected: current controller, formal bounded phases, actual generator, observed mutation, independent report acceptance, five-pillar inspection, final reruns, deliverable readbacks, independent exact-candidate review and Root closure receiving.
The three outputs share one current run/acceptance writer; that authority serializes these fixed steps. No agent DAG, diagnostic child, installation or package mutation is needed.

## Baseline ref

{session['task_commit']}

## Phases

| Phase | Objective | Owner/source | Depends on | Smoke A | Smoke B | Review | Status |
|---|---|---|---|---|---|---|---|
| 1 | Inventory all package members | output/inventory.json via subject/build.py | - | integrity | integrity | actual preparation review | open |
| 2 | Index operating command owners | output/owners.json via subject/build.py | - | integrity | integrity | actual preparation review | open |
| 3 | Join the current profile guide | output/guide.json via subject/build.py | 1, 2 and current profile | integrity | integrity | actual preparation review | open |

## Complete bundle obligation

- [ ] /usr/bin/python3 -B subject/verify.py all passes at the actual final candidate.
- [ ] Every generated output passes the native deliverable check.
- [ ] An actual independent exact-candidate review and separate Root decision support bounded closure after all gates pass.

## Scope boundaries

Only output/inventory.json, output/owners.json and output/guide.json are implementation targets. Input delivery is evidence; it does not silently expand mutation authority.
"""
    docs = {"STATE.md": state, "ROADMAP.md": roadmap,
        "PROTOCOL.md": (Path(session["source"]) / "skills/implementaudit/templates/PROTOCOL.md").read_text(),
        "THINKING.md": "# Task rationale\n\nThe first two reports have independent direct package inputs. The guide joins those reports with one profile dependency. Each generated output is an integrity input for subsequent consumption and needs complete exact-byte acceptance. Preserve the generator, verifier and package. Keep actual phase evidence and actual governor decisions separately inspectable.\n",
        "tools.md": "# Tools\n\nFixed Python, Bash and Git commands only. The exact packaged claim/currentness, phase authority, observed mutation, evidence, deliverable and closure owners are used. No returned command text is executed. One bounded provider mailbox sequence.\n",
        "sidecars.md": "# Sidecars\n\nGraphify and ActiveGraph are not configured. The runtime Markdown and complete command captures supply the evidence record.\n",
        "applied-context.md": "# Applied context\n\nThe bounded task uses source and output bytes as evidence. No prior narrative establishes a completed phase or current controller.\n",
        "context.md": f"# Context\n\nSelected source: {SOURCE}\nParent controller: {request['parent_controller']}\nParent receipt at publication: {request['parent_receipt']}\nThis task does not alter parent custody. Its scoped closure creates no programme, issue, release or native Stop claim.\n"}
    for number in NAMES:
        docs[f"phases/phase-{number}.md"] = phase_text(session, number)
    for name, text in docs.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
    (root / "evidence").mkdir()
    session["static_documents"] = {name: identity(root / name) for name in STATIC}
    frontier(session)
    remember(session)


def prepare(args):
    out, source = args.output.resolve(), Path.cwd().resolve()
    out.mkdir(parents=True, exist_ok=True)
    u.need(not (out / "SESSION.json").exists(), "Task already started; no replay")
    request = u.read(args.request.resolve())
    u.need(request["schema"] == "dg17.fixed-positive-request.v1", "Request schema differs")
    u.need(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == REPOSITORY
        and os.environ.get("GITHUB_REF_NAME") == BRANCH and os.environ.get("GITHUB_RUN_ATTEMPT") == "1", "Hosted launch identity differs")
    u.need(request["review"]["status"] == "PASS" and request["review"]["evidence"].strip(), "Actual independent preparation review missing")
    expected_code = {PREFIX + "/" + p for p in SUBJECT | {"hosted_positive.py", "hosted_phase.py", "transport_primitives.py"}} | {".github/workflows/dg17-positive-bundle.yml"}
    u.need({r["path"] for r in request["subject_members"]} == SUBJECT, "Subject population differs")
    u.need({r["path"] for r in request["code_members"]} == expected_code, "Code/input population differs")
    u.package_check(source, request)
    u.verify_files(source, request["code_members"])
    launch = os.environ["GITHUB_SHA"]
    u.need(u.run(out, "launch-parent", ["/usr/bin/git", "rev-parse", launch + "^"], source) == SOURCE, "Launch is not a direct child of selected source")
    u.need(u.run(out, "selected-tree", ["/usr/bin/git", "rev-parse", SOURCE + "^{tree}"], source) == SOURCE_TREE, "Selected tree differs")
    u.run(out, "package-unchanged", ["/usr/bin/git", "diff", "--exit-code", SOURCE, launch, "--", "skills", ".codex-plugin", ".claude-plugin", "package"], source)
    task = Path(tempfile.mkdtemp(prefix="dg17-governed-", dir=os.environ["RUNNER_TEMP"])).resolve()
    session = dict(schema="dg17.fixed-positive-custody.v1", source=str(source), task=str(task), output=str(out),
        exchange_id=uuid.uuid4().hex, request_path=str(args.request.resolve()), request_identity=identity(args.request.resolve()),
        launch_commit=launch, last_mail_commit=launch, run_id=os.environ["GITHUB_RUN_ID"], run_attempt="1",
        controller="dg17-bundle-" + os.environ["GITHUB_RUN_ID"], epoch=0, deadline_unix=time.time() + u.WINDOW_SECONDS,
        stage="INITIALIZING", completed=[], neutral_observations=[], case_identity="bundle-initial-" + os.environ["GITHUB_RUN_ID"],
        authorization_scope_sha256=u.sha(json.dumps(SCOPES, sort_keys=True, separators=(",", ":")).encode()))
    (task / ".transport-owner").write_text(session["exchange_id"])
    u.store_session(out, session)
    u.verify_files(HERE, request["subject_members"])
    for row in request["subject_members"]:
        path = task / row["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((HERE / row["path"]).read_bytes())
    u.need(u.read(task / "inputs/package-members.json") == request["package_members"], "Report member population differs from the admitted executing package")
    (task / ".gitignore").write_text(".IMPLEMENTAUDIT/\n.transport-owner\n")
    session["profile"] = str(task / "inputs/profile.json")
    session["profile_identity"] = identity(Path(session["profile"]))
    command(session, out, "init-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "init", "--initial-branch=package-bundle"])
    command(session, out, "add-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "add", "TASK.md", "subject", "inputs", "output", ".gitignore"])
    command(session, out, "commit-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=IMPLEMENTAUDIT bounded task", "-c", "user.email=bounded-root@invalid.example", "commit", "-m", "Bind package operating bundle inputs"])
    session["task_commit"], _, _ = command(session, out, "baseline", ["/usr/bin/git", "rev-parse", "HEAD"])
    session["task_tree"], _, _ = command(session, out, "baseline-tree", ["/usr/bin/git", "rev-parse", "HEAD^{tree}"])
    relative = u.claim(session, out, "claim-task", "--controller", session["controller"], "package-bundle")
    u.safe_relative(relative)
    session["run_root"] = str(task / relative)
    session["claim_id"] = dict(line.split("=", 1) for line in (Path(session["run_root"]) / ".claimed").read_text().splitlines())["claim_id"]
    write_documents(session, request)
    inspected = json.loads(u.claim(session, out, "inspect-initialization", "--inspect-controller-initialization", session["controller"], "--run-root", relative))
    u.claim(session, out, "activate-controller", "--activate-controller", session["controller"], "--run-root", relative, "--expected-initialization", inspected["initialization_token"])
    refresh(session, out, "Actual isolated package-bundle admission", "new-session")
    witnesses = []
    for number in NAMES:
        _, witness, _ = command(session, out, f"phase-{number}-structure", ["/bin/bash", scripts(session) / "validate-phase.sh", Path(session["run_root"]) / "phases" / f"phase-{number}.md"])
        witnesses.append(witness)
    snapshot(session, request, out, "prepared", witnesses, {"report_mutated": False, "decision_pending": True})


def read_model(value, session, name):
    keys = {"binding", "model", "prompt_sha256", "result_text", "result_sha256", "tool_observation", "independence_evidence"}
    u.need(isinstance(value, dict) and set(value) == keys and value["binding"] == session["binding"], name + " does not bind current observation")
    u.need(all(isinstance(value[k], str) and 1 <= len(value[k].encode()) <= 65536 for k in keys - {"binding"}), name + " data absent or oversized")
    u.need(re.fullmatch(r"[0-9a-f]{64}", value["prompt_sha256"]) and value["result_sha256"] == u.sha(value["result_text"].encode()), name + " digest differs")
    u.need(value["tool_observation"] not in session["neutral_observations"], "Model observation was already consumed")


def receive(args):
    out = args.output.resolve()
    session = u.read(out / "SESSION.json")
    request = u.read(Path(session["request_path"]))
    stage, mailbox, action = STAGES[args.operation]
    u.need(session["stage"] == stage, "Stage already consumed or differs")
    current(session, request, out)
    head, raw, value = u.wait_mail(session, out, PREFIX + "/mailbox/" + mailbox)
    envelope = {"schema", "binding", "action", "record", "provenance", "neutral_return"}
    if args.operation in {"close", "close_update"} and value.get("action") == action:
        envelope.add("independent_review")
    u.need(isinstance(value, dict) and set(value) == envelope, "Decision fields differ")
    u.need(value["schema"] == "dg17.package-bundle-decision.v1" and value["binding"] == session["binding"], "Decision is stale or foreign")
    u.need(value["action"] in {action, "retain-contained"}, "Decision is outside the fixed next action")
    record = value["record"]
    fields = {"witnesses", "owner_source", "currentness", "dependencies", "acceptance", "next_action", "reason", "scope"}
    if args.operation in COMPLETIONS and value["action"] == action:
        fields.update({"five_s", "agents_update", "continuity"})
    if args.operation in {"close", "close_update"} and value["action"] == action:
        fields.add("lesson_lift")
    u.need(isinstance(record, dict) and set(record) == fields and record["witnesses"] == session["binding"]["witness_command_ids"], "Decision record/witnesses differ")
    for key in fields - {"witnesses", "five_s"}:
        u.need(isinstance(record[key], str) and 8 <= len(record[key]) <= 4096 and "\n" not in record[key] and "|" not in record[key], "Decision scalar malformed")
    if "lesson_lift" in record:
        u.need(record["lesson_lift"].startswith("No-lift: ") and len(record["lesson_lift"]) > 24,
            "This clean bounded closing route requires the actual reasoned no-lift decision; a qualifying lesson must remain contained for its owner route")
    if "five_s" in record:
        u.need(isinstance(record["five_s"], dict) and set(record["five_s"]) == {"seiri", "seiton", "seiso", "seiketsu", "shitsuke"}, "Five-pillar decision absent")
        u.need(all(isinstance(v, str) and (v == "clean" or v.startswith("deferred: ") and len(v) > 18) and len(v) <= 4096 and "\n" not in v and "|" not in v for v in record["five_s"].values()), "Five-pillar disposition differs")
    p = value["provenance"]
    pkeys = {"actor", "loaded_governor_source", "loaded_governor_sha256", "parent_receipt", "tool_observation", "decision_record_sha256"}
    u.need(isinstance(p, dict) and set(p) == pkeys and all(isinstance(v, str) and v.strip() for v in p.values()), "Root provenance missing")
    source_sha = next(r["sha256"] for r in request["package_members"] if r["path"] == "skills/implementaudit/SKILL.md")
    u.need(p["loaded_governor_source"] == SOURCE + ":skills/implementaudit/SKILL.md" and p["loaded_governor_sha256"] == source_sha, "Declared governor source differs")
    u.need(p["decision_record_sha256"] == u.sha(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()), "Root decision digest differs")
    read_model(value["neutral_return"], session, "Fresh neutral return")
    if "independent_review" in value:
        read_model(value["independent_review"], session, "Independent candidate review")
        u.need(value["independent_review"]["tool_observation"] != value["neutral_return"]["tool_observation"], "Independent review and governor return are the same observation")
    current(session, request, out)
    target = Path(session["run_root"]) / "evidence" / ("decision-" + mailbox)
    target.write_bytes(raw)
    session["last_mail_commit"] = head
    session["stage"] = "ACTION_IN_FLIGHT_" + args.operation
    session["neutral_observations"].append(value["neutral_return"]["tool_observation"])
    if "independent_review" in value:
        session["neutral_observations"].append(value["independent_review"]["tool_observation"])
    u.store_session(out, session)
    event(session, {"event": "actual-Root-decision-received", "operation": args.operation, "commit": head,
        "sha256": u.sha(raw), "decision_path": str(target), "record": record, "neutral_return": value["neutral_return"],
        "provenance": p, "authority_ceiling": "Data custody; actual receiving and decision substance remain independently inspectable"})
    if value["action"] == "retain-contained":
        u.state_value(session, "Status", "BLOCKED")
        u.state_value(session, "Audit object state", "open")
        u.state_value(session, "Blocker", record["reason"])
        u.state_value(session, "Next action", record["next_action"])
        refresh(session, out, "Actual Root containment decision")
        snapshot(session, request, out, "CONTAINED", record["witnesses"])
        return None
    return session, request, out, value


def verify(session, out, label, mode, capture=None):
    text, witness, record = command(session, out, label, ["/usr/bin/python3", "-B", "subject/verify.py", mode,
        "--package-root", session["source"], "--profile", session["profile"]])
    value = u.decode(text.encode())
    u.need(value["passed"] is True and value["check"] == mode and record["stderr"]["bytes"] == 0, "Report acceptance signature differs")
    expected = {NAMES[n]: identity(Path(session["task"]) / OUTPUTS[n]) for n in NAMES}
    u.need(value["outputs"] == expected and value["profile"] == session["profile_identity"], "Report check does not bind actual bytes")
    if capture:
        target = Path(session["run_root"]) / "evidence" / capture
        with target.open("xb") as stream:
            stream.write((out / "commands" / record["output_file"]).read_bytes())
    return witness


def authority(session, out, number, step):
    root = Path(session["run_root"])
    text, witness, _ = command(session, out, f"authority-{number}-{step}", ["/bin/bash", scripts(session) / "validate-phase.sh", "--mutation-authority",
        root / "phases" / f"phase-{number}.md", "--phase", str(number), "--step", str(step), "--repo-root", session["task"], "--run-root", root])
    value = u.decode(text.encode())
    u.need(value["operation"] == "replace" and value["source"] == OUTPUTS[number] and value["destination"] is None, "Authority projection differs")
    return witness


def mutate(session, out, number, step, candidate, expectation):
    task, root = Path(session["task"]), Path(session["run_root"])
    owner = OUTPUTS[number]
    before = (task / owner).read_bytes()
    u.need(identity(task / owner) == session["owner_identity"][owner], "Owner preimage drifted")
    folder = root / "evidence" / f"mutation-{number}-{step}"
    folder.mkdir()
    (folder / "preimage.json").write_bytes(before)
    (folder / "candidate.json").write_bytes(candidate)
    argv = ["/bin/bash", scripts(session) / "apply-observed-mutation.sh", "--repo-root", task,
        "--run-root", root, "--phase", str(number), "--step", str(step), "--preimage", folder / "preimage.json", "--candidate", folder / "candidate.json"]
    text, witness, _ = command(session, out, f"mutation-{number}-{step}", ["/bin/bash", scripts(session) / "check-evidence-anchor.sh", "--mutation-window", owner, "--expect", expectation, "--", *argv])
    records = [u.decode(line.encode()) for line in text.splitlines() if line.startswith("{")]
    u.need(len(records) == 1 and records[0].get("status") == "COMMITTED" and records[0].get("source_path") == owner and records[0].get("residue") == [], "Native transaction did not commit the bounded target without residue")
    u.need(before != candidate and (task / owner).read_bytes() == candidate, "Landed bytes differ")
    remember(session)
    return witness


def execute_phase(session, request, out, number, step=1):
    root = Path(session["run_root"])
    name = NAMES[number]
    suffix = "-update" if step == 2 else ""
    label = f"phase-{number}{suffix}"
    u.state_value(session, "Phase", str(number))
    u.state_value(session, "Status", "IN_PHASE")
    u.state_value(session, "Audit object state", "open")
    u.state_value(session, "Next action", "Generate and verify the admitted " + name + " report")
    frontier(session, number)
    refresh(session, out, "Actual Root dispatch of " + label)
    current(session, request, out)
    command(session, out, label + "-read-state", ["/bin/cat", root / "STATE.md"])
    command(session, out, label + "-read-spec", ["/bin/cat", root / "phases" / f"phase-{number}.md"])
    command(session, out, label + "-structure", ["/bin/bash", scripts(session) / "validate-phase.sh", root / "phases" / f"phase-{number}.md"])
    witnesses = [authority(session, out, number, step)]
    event(session, {"event": "IMPLEMENTAUDIT_PHASE_START", "phase": number, "step": step, "owner": OUTPUTS[number], "candidate_before": session["owner_identity"], "receipt": session["continuity_receipt"]})
    witnesses.append(verify(session, out, label + "-smoke-a", "integrity", label + "-smoke-a.log"))
    _, witness, record = command(session, out, label + "-generate", ["/usr/bin/python3", "-B", "subject/build.py", name, "--package-root", session["source"], "--profile", session["profile"]])
    u.need(record["stderr"]["bytes"] == 0, "Generator wrote unexpected diagnostics")
    candidate = (out / "commands" / record["output_file"]).read_bytes()
    u.decode(candidate)
    witnesses.append(witness)
    expectation = "occurrences:1:" + ({1: "package-inventory.v1", 2: "operating-owner-index.v1", 3: "operating-guide.v1"}[number] if step == 1 else '"profile_revision": "updated"')
    witnesses.append(mutate(session, out, number, step, candidate, expectation))
    witnesses.append(verify(session, out, label + "-mandatory", name, label + "-mandatory.log"))
    for operation in ("added-lines", "changed-files"):
        _, witness, _ = command(session, out, label + "-" + operation, ["/bin/bash", scripts(session) / "repo-state.sh", operation, session["task_commit"]])
        witnesses.append(witness)
    command(session, out, label + "-diff-check", ["/usr/bin/git", "diff", "--check"])
    changed, witness, _ = command(session, out, label + "-changed", ["/usr/bin/git", "diff", "--name-only", "HEAD"])
    status, _, _ = command(session, out, label + "-status", ["/usr/bin/git", "status", "--porcelain=v1", "--untracked-files=all"])
    intended = {OUTPUTS[n] for n in {*session["completed"], number}}
    u.need(set(changed.splitlines()) == intended and {line.strip() for line in status.splitlines()} == {"M " + path for path in intended}, "Touched file census or residue differs")
    witnesses.append(witness)
    witnesses.append(verify(session, out, label + "-smoke-b", "integrity", label + "-smoke-b.log"))
    session["checked_phase"] = dict(number=number, step=step, label=label, outputs=owner_identities(session), witnesses=witnesses)
    u.state_value(session, "Last check", "Actual acceptance, cleanliness and Smoke B completed for " + label + "; governor completion pending")
    u.state_value(session, "Next action", "Receive the actual phase acceptance and five-pillar decision")
    refresh(session, out, "Actual checked phase boundary " + label)
    return witnesses


def complete_phase(session, number, value):
    checked = session["checked_phase"]
    u.need(checked["number"] == number and checked["outputs"] == owner_identities(session), "Checked candidate changed before phase acceptance")
    root = Path(session["run_root"])
    suffix = "-update" if checked["step"] == 2 else ""
    label = checked["label"]
    u.save(root / "evidence" / (label + "-completion.json"), value)
    phase = root / "phases" / f"phase-{number}.md"
    text = phase.read_text().replace("- [ ]", "- [x]").replace("Status: open", "Status: done")
    phase.write_text(text)
    roadmap = root / "ROADMAP.md"
    text, count = re.subn(r"(?m)^(\| " + str(number) + r" \|.*)open( \|)$", lambda match: match[1] + "done" + match[2], roadmap.read_text())
    u.need(count == 1, "Current phase census row missing or ambiguous")
    roadmap.write_text(text)
    report = f"""# Actual {label} completion

IMPLEMENTAUDIT_PHASE_VERIFY
Phase: {number}; fresh observed mutation step: {checked['step']}.
Status: done
Acceptance: {value['record']['acceptance']}
Actual command witnesses: {', '.join(checked['witnesses'])}
Smoke A and Smoke B: actual integrity captures retained; output identities changed only through the recorded native transaction.
Candidate: {json.dumps(checked['outputs'], sort_keys=True)}
Five-pillar actual decision: {json.dumps(value['record']['five_s'], sort_keys=True)}
Sidecars: absent; Markdown and full captures retained.
AGENTS_UPDATE_DECISION
{value['record']['agents_update']}
CONTINUITY_DECISION
{value['record']['continuity']}
IMPLEMENTAUDIT_PHASE_DONE
Status: done
Evidence: {label}-completion.json and the actual phase captures.
Follow-up: the audit object remains open pending its remaining obligations.
"""
    (root / "evidence" / (label + "-report.md")).write_text(report)
    if number not in session["completed"]:
        session["completed"].append(number)
    session["completed"].sort()
    u.state_value(session, "Completed phases", ", ".join(map(str, session["completed"])))
    event(session, {"event": "IMPLEMENTAUDIT_PHASE_DONE", "phase": number, "step": checked["step"], "actual_Root_record": value["record"],
        "neutral_observation": value["neutral_return"]["tool_observation"], "command_witnesses": checked["witnesses"], "audit_object_state": "open"})
    frontier(session)
    remember(session)


def audit_bundle(session, request, out, label):
    u.need(session["completed"] == [1, 2, 3], "All three formal phases have not completed")
    root = Path(session["run_root"])
    u.state_value(session, "Phase", "final audit")
    u.state_value(session, "Status", "open")
    u.state_value(session, "Last check", "All formal phases completed by actual Root receiving; whole bundle audit remains open")
    u.state_value(session, "Next action", "Rerun complete acceptance, inspect deliverables and receive independent exact-candidate review")
    refresh(session, out, "Actual completed phase evidence received before " + label)
    current(session, request, out)
    command(session, out, label + "-roadmap", ["/bin/cat", root / "ROADMAP.md"])
    start, _, _ = command(session, out, label + "-start-head", ["/usr/bin/git", "rev-parse", "HEAD"])
    version, _, _ = command(session, out, label + "-package-version", ["/bin/bash", scripts(session) / "detect-env.sh", "--package-version", Path(session["source"]) / "skills/implementaudit"])
    outputs = owner_identities(session)
    event(session, {"event": "AUDIT_START", "case_identity": session["case_identity"], "anchor": start,
        "outputs": outputs, "package_version": version, "completed_phases": session["completed"]})
    witnesses = []
    for name in ("inventory", "owners", "guide", "all"):
        witnesses.append(verify(session, out, label + "-" + name, name, label + "-" + name + ".log"))
    for number, path in OUTPUTS.items():
        _, witness, _ = command(session, out, label + f"-deliverable-{number}", ["/bin/bash", scripts(session) / "repo-state.sh", "deliverable", session["task_commit"], path])
        witnesses.append(witness)
    verify_head, _, _ = command(session, out, label + "-verify-head", ["/usr/bin/git", "rev-parse", "HEAD"])
    u.need(start == verify_head and outputs == owner_identities(session), "Candidate drifted within final audit")
    session["audit"] = dict(label=label, start_anchor=start, verify_anchor=verify_head, outputs=outputs,
        profile_identity=session["profile_identity"], witnesses=witnesses, re_verified=3, trust_prior=0)
    event(session, {"event": "AUDIT_VERIFY", "case_identity": session["case_identity"], **session["audit"]})
    u.state_value(session, "Last check", "Actual complete report and deliverable checks passed at exact candidate; independent review and Root closure remain open")
    refresh(session, out, "Actual complete audit observations ready for separate review and Root receiving")
    return witnesses


def close_bundle(session, request, out, value, label):
    root = Path(session["run_root"])
    audit = session["audit"]
    u.need(audit["outputs"] == owner_identities(session) and audit["profile_identity"] == session["profile_identity"], "Reviewed audit candidate drifted")
    u.need(session["completed"] == [1, 2, 3], "Formal phase population is incomplete")
    review = value["independent_review"]
    # The actual decision is already retained; this records the scoped pending
    # terminal operation before invoking its final native validation owners.
    u.state_value(session, "Pending terminal", "Validate this exact final report and run root, then record scoped task closure from the received decision")
    (root / "evidence" / (label + "-independent-review.md")).write_text(review["result_text"])
    report = f"""# Package operating bundle final audit

Goal: Produce the three complete generated reports for the current supplied profile.
Scope: {session['case_identity']}; this isolated output bundle only.
Candidate package: {SOURCE}
Task baseline: {session['task_commit']}
Current dependency: {json.dumps(session['profile_identity'], sort_keys=True)}
Actual output identities: {json.dumps(audit['outputs'], sort_keys=True)}
Formal phases: 1, 2 and 3 each completed through the actual retained Root decision and phase transcript. Their original captures remain present.
Acceptance population: three complete report criteria; complete bundle consistency checked additionally.
Final actual command witnesses: {', '.join(audit['witnesses'])}
Mandatory checks: each complete report was re-verified; no trust-prior substitution.
Deliverables: each actual output was checked by the packaged deliverable owner against the task baseline.
Smoke comparison: actual before/after integrity captures are retained for every executed phase; no failed command was replaced by a later capture.
Independent exact-candidate review: evidence/{label}-independent-review.md; SHA256 {review['result_sha256']}. Its exact tool and independence evidence remain in the retained closing decision.
Separate Root receiving: decision digest {value['provenance']['decision_record_sha256']}. The actual reason and tool provenance remain in the retained closing decision and governor-event record.
Coverage: re_verified = 3; trust_prior = 0; re_verified / (re_verified + trust_prior) = 3 / 3 = 1.0 (100%).
Findings, Andons and consequential residuals in this scoped sequence: none recorded; the actual retained source checks and decisions establish this bounded result.
{value['record']['lesson_lift']}
claim: package-bundle | surface: generated-artifact | status: verified | evidence-surface: generated-artifact | evidence: {', '.join(audit['witnesses'])}
AUDIT_START_ANCHOR: {audit['start_anchor']}
AUDIT_VERIFY_ANCHOR: {audit['verify_anchor']}
REANCHOR_DISPOSITION: unchanged
REANCHOR_EVIDENCE: none
equivalent_config_attempts: 1/1
stochasticity_budget: none
terminal_qualification: QUALIFIED
Boundary: no parent commission, issue, release, installation, publication or native Stop conclusion.
"""
    target = root / "final-report.md"
    with target.open("x", encoding="utf-8") as stream:
        stream.write(report)
    roadmap = root / "ROADMAP.md"
    roadmap.write_text(roadmap.read_text().replace("- [ ]", "- [x]"))
    u.state_value(session, "Status", "open")
    u.state_value(session, "Audit object state", "open")
    u.state_value(session, "Next action", "Scoped closure validation and evidence preservation; no further effect implied")
    remember(session)
    refresh(session, out, "Actual Root scoped terminal receiving, pending final native validation")
    current(session, request, out)
    witnesses = []
    for owner, arguments in (("check-lesson-lift.sh", [target, "--repo-root", session["task"]]),
                             ("check-closure-surface.sh", [target, "--steer-dir", root]),
                             ("validate-run-root.sh", [root])):
        _, witness, _ = command(session, out, label + "-" + owner.removesuffix(".sh"), ["/bin/bash", scripts(session) / owner, *arguments])
        witnesses.append(witness)
    u.need(owner_identities(session) == audit["outputs"], "Final validators observed a changed candidate")
    u.state_value(session, "Status", "DONE")
    u.state_value(session, "Audit object state", "done")
    _, terminal_witness, _ = command(session, out, label + "-terminal-root", ["/bin/bash", scripts(session) / "validate-run-root.sh", root])
    witnesses.append(terminal_witness)
    with target.open("a", encoding="utf-8") as stream:
        stream.write("\nAUDIT_COMPLETE\nIMPLEMENTAUDIT_RUN_COMPLETE\n")
    u.state_value(session, "Pending terminal", "cleared after actual scoped final validation")
    u.state_value(session, "Last check", "Actual scoped final validators passed; terminal markers recorded after those outcomes")
    event(session, {"event": "AUDIT_COMPLETE", "case_identity": session["case_identity"], "actual_Root_record": value["record"], "final_witnesses": witnesses, "report": identity(target)})
    event(session, {"event": "IMPLEMENTAUDIT_RUN_COMPLETE", "case_identity": session["case_identity"], "scope": "This generated bundle only"})
    session["scoped_closure"] = dict(case_identity=session["case_identity"], report=identity(target), witnesses=witnesses)
    refresh(session, out, "Actual scoped task closure recorded")
    return witnesses


def deliver_dependency(args):
    out = args.output.resolve()
    session = u.read(out / "SESSION.json")
    request = u.read(Path(session["request_path"]))
    stage, mailbox, action = STAGES["dependency"]
    u.need(session["stage"] == stage and session["scoped_closure"]["case_identity"] == session["case_identity"], "New input requires actual earlier scoped closure")
    current(session, request, out)
    head, raw, value = u.wait_mail(session, out, PREFIX + "/mailbox/" + mailbox)
    keys = {"schema", "binding", "action", "owner_message", "profile_text", "profile_sha256", "provenance"}
    u.need(isinstance(value, dict) and set(value) == keys and value["schema"] == "dg17.new-profile-delivery.v1", "Profile delivery schema differs")
    u.need(value["binding"] == session["binding"] and value["action"] == action, "Profile delivery is stale/foreign")
    u.need(isinstance(value["owner_message"], str) and 20 <= len(value["owner_message"]) <= 4096, "Actual new task instruction missing")
    text = value["profile_text"]
    u.need(isinstance(text, str) and len(text.encode()) <= 8192 and u.sha(text.encode()) == value["profile_sha256"], "Delivered profile digest differs")
    u.need({"bytes": len(text.encode()), "sha256": value["profile_sha256"]} == request["later_profile_identity"], "Delivered bounded input differs from frozen delivery identity")
    profile = u.decode(text.encode())
    u.need(set(profile) == {"schema", "revision", "purpose", "owners"} and profile["schema"] == "operating-profile.v1" and profile["revision"] == "updated", "Profile input shape differs")
    u.need(isinstance(value["provenance"], dict) and set(value["provenance"]) == {"actor", "tool_observation", "parent_receipt"}
        and all(isinstance(v, str) and v.strip() for v in value["provenance"].values()), "Input-delivery provenance missing")
    root = Path(session["run_root"])
    folder = root / "evidence/incoming"
    folder.mkdir()
    (folder / "delivery.json").write_bytes(raw)
    (folder / "profile.json").write_bytes(text.encode())
    (folder / "owner-message.md").write_text(value["owner_message"] + "\n")
    session["last_mail_commit"] = head
    session["stage"] = "ACTION_IN_FLIGHT_dependency"
    session["new_profile"] = str(folder / "profile.json")
    session["new_profile_identity"] = identity(folder / "profile.json")
    u.store_session(out, session)
    u.need(session["new_profile_identity"] != session["profile_identity"], "No material input change occurred")
    event(session, {"event": "actual-new-input-delivered", "provider_commit": head, "old_profile": session["profile_identity"],
        "new_profile": session["new_profile_identity"], "prior_closed_case": session["scoped_closure"], "decision_pending": True})
    snapshot(session, request, out, "dependency-arrived", [], {"new_profile_identity": session["new_profile_identity"],
        "new_profile_path": "evidence/incoming/profile.json", "new_owner_message": value["owner_message"],
        "prior_closed_case": session["scoped_closure"], "no_report_or_phase_changed": True})


def updated_phase_text(session, prior):
    task = Path(session["task"])
    relative_profile = Path(session["profile"]).relative_to(task).as_posix()
    text = prior.replace("Status: done", "Status: open").replace("- [x]", "- [ ]")
    text = text.replace("## Scope boundaries", f"- Step 2: Generate the current-profile guide — target: output/guide.json; change: regenerate only the guide using {relative_profile}; verify: /usr/bin/python3 -B subject/verify.py guide --package-root {session['source']} --profile {relative_profile}; expected: exit 0 and passed true; landed: occurrences:1:\"profile_revision\": \"updated\"\n  mutation-authority: {{\"operation\":\"replace\",\"source\":\"output/guide.json\",\"destination\":null}}\n\n## Scope boundaries", 1)
    # Keep the committed first step verbatim as historical authority. Only the
    # current smoke/mandatory dependency and capture are re-bound.
    lines = text.splitlines()
    lines = [line.replace("--profile inputs/profile.json", "--profile " + relative_profile) if line.startswith(("Smoke A:", "Smoke B:", "- /usr/bin/python3")) else line for line in lines]
    text = "\n".join(lines) + "\n"
    text = text.replace("/evidence/phase-3-mandatory.log", "/evidence/phase-3-update-mandatory.log")
    return text


def replan(session, request, out, value):
    root, task = Path(session["run_root"]), Path(session["task"])
    refresh(session, out, "Actual new-input reentry before any affected phase or frontier write")
    current(session, request, out)
    reentry_receipt = session["continuity_receipt"]
    u.need({str(n): bundle(session, n) for n in (1, 2)} == session["preserved_bundles"], "Unaffected phases are not current")
    u.need(identity(Path(session["new_profile"])) == session["new_profile_identity"], "New profile drifted before receiving")
    history = root / "evidence/closed-baseline"
    u.need(identity(history / "final-report.md") == identity(root / "final-report.md"), "Earlier exact closure report differs from its preserved archive")
    (root / "final-report.md").unlink()
    session["baseline_closure"] = session["scoped_closure"]
    session["case_identity"] = "changed-profile-" + session["run_id"]
    session["profile"] = session["new_profile"]
    session["profile_identity"] = session["new_profile_identity"]
    session["completed"] = [1, 2]
    session.pop("checked_phase", None)
    session.pop("audit", None)
    session.pop("scoped_closure", None)
    phase = root / "phases/phase-3.md"
    phase.write_text(updated_phase_text(session, phase.read_text()))
    roadmap = root / "ROADMAP.md"
    text, count = re.subn(r"(?m)^(\| 3 \|.*)done( \|)$", lambda match: match[1] + "open" + match[2], roadmap.read_text())
    u.need(count == 1, "Prior guide phase census missing")
    text = text.replace("- [x]", "- [ ]")
    text += f"\n## New supplied profile received\n\nChanged task identity: {session['case_identity']}. The actual owner instruction is evidence/incoming/owner-message.md. Only the guide depends on this changed input. Its earlier completion remains historical in evidence/closed-baseline; its current acceptance is reopened. Phases 1 and 2 retain their exact existing evidence and outputs. Authorization scope SHA256 remains {session['authorization_scope_sha256']}.\n"
    roadmap.write_text(text)
    for key, val in (("Phase", "3"), ("Status", "READY_TO_DISPATCH"), ("Audit object state", "open"),
                     ("Audit object identity", session["case_identity"]), ("Completed phases", "1, 2"),
                     ("Last check", "Root received the actual changed dependency and preserved both unaffected formal phase bundles"),
                     ("Next action", "Receive current guide dispatch after actual currentness and affected phase validation"),
                     ("Pending terminal", "none; new supplied-profile task remains open")):
        u.state_value(session, key, val)
    census = frontier(session)
    event(session, {"event": "actual-Root-selective-reentry", "case_identity": session["case_identity"], "actual_Root_record": value["record"],
        "prior_closed_case": session["baseline_closure"], "unaffected_phase_bundles": session["preserved_bundles"],
        "invalidated_current_phase": 3, "new_dependency": session["profile_identity"], "frontier": census,
        "before_write_current_receipt": reentry_receipt,
        "authorization_scope_sha256": session["authorization_scope_sha256"]})
    refresh(session, out, "Actual received material dependency change; only guide phase reopened")
    current(session, request, out)
    witnesses = [authority(session, out, 3, 2)]
    _, witness, _ = command(session, out, "replanned-phase-structure", ["/bin/bash", scripts(session) / "validate-phase.sh", phase])
    witnesses.append(witness)
    u.save(root / "evidence/selective-preservation.json", dict(unaffected_phase_bundles={str(n): bundle(session, n) for n in (1, 2)},
        frontier=census, authorization_scope_sha256=session["authorization_scope_sha256"], dependency=session["profile_identity"],
        actual_receipt=session["continuity_receipt"]))
    return witnesses


def advance(args):
    received = receive(args)
    if received is None:
        return
    session, request, out, value = received
    operation = args.operation
    if operation in COMPLETIONS:
        complete_phase(session, COMPLETIONS[operation], value)
    if operation in {"first", "second", "third", "update"}:
        number = {"first": 1, "second": 2, "third": 3, "update": 3}[operation]
        witnesses = execute_phase(session, request, out, number, 2 if operation == "update" else 1)
        stage = {"first": "inventory-checked", "second": "owners-checked", "third": "guide-checked", "update": "updated-guide-checked"}[operation]
    elif operation in {"audit", "audit_update"}:
        witnesses = audit_bundle(session, request, out, "updated-final-audit" if operation == "audit_update" else "initial-final-audit")
        stage = "update-audited" if operation == "audit_update" else "audited"
    elif operation in {"close", "close_update"}:
        witnesses = close_bundle(session, request, out, value, "updated-closure" if operation == "close_update" else "initial-closure")
        stage = "update-closed" if operation == "close_update" else "baseline-closed"
        if operation == "close":
            session["preserved_bundles"] = {str(n): bundle(session, n) for n in (1, 2)}
            root = Path(session["run_root"])
            history = root / "evidence/closed-baseline"
            history.mkdir()
            for name in ("STATE.md", "ROADMAP.md", "final-report.md"):
                shutil.copyfile(root / name, history / name)
            shutil.copyfile(root / "phases/phase-3.md", history / "phase-3.md")
            session["baseline_archive"] = {p.name: identity(p) for p in history.iterdir()}
    elif operation == "replan":
        witnesses = replan(session, request, out, value)
        stage = "replanned"
    else:
        raise u.Refusal("Operation is not one fixed sequence step")
    snapshot(session, request, out, stage, witnesses)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["prepare", *STAGES, "finalize"])
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--request", type=Path)
    args = parser.parse_args()
    try:
        if args.operation == "prepare":
            u.need(args.request is not None, "Preparation request missing")
            prepare(args)
        elif args.operation == "dependency":
            deliver_dependency(args)
        elif args.operation == "finalize":
            u.finalize(args)
        else:
            advance(args)
    except Exception as exc:
        args.output.mkdir(parents=True, exist_ok=True)
        path = args.output / ("REFUSAL-" + args.operation + ".json")
        if not path.exists():
            u.save(path, dict(operation=args.operation, kind=type(exc).__name__, reason=str(exc),
                qualification=False, completion_inferred=False, automatic_retry=False, original_evidence_preserved=True))
        print("REFUSED: " + str(exc), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
