#!/usr/bin/env python3
"""One disposable P07/H07 transport; source owners retain every decision.

This is ordinary hosted CLI governance, not a native assistant/Stop adapter.
Mail is immutable evidence data. No returned text is evaluated or executed.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg17-governed-l4-20261116"
SOURCE = "a297957be11feb494c0ec467235794a1e0c54751"
SOURCE_TREE = "b08dc4ecf4028beeedb579a312eccae23cb5d863"
LAUNCH_PARENT = "5488adffe48660376a758a828a0748b97c1c0efd"
PREFIX = "handoff/dg17-governed-l4"
RETURN_PATH = PREFIX + "/mailbox/returns.json"
DECISION_PATH = PREFIX + "/mailbox/decision.json"
LIMIT = 262144
WINDOW_SECONDS = 2700
SKILLS = {"implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon"}
DECISIONS = {"retain-contained", "repair-separately", "request-owner-decision"}


class Refusal(RuntimeError):
    pass


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON field: " + key)
        result[key] = value
    return result


def decode(raw):
    need(len(raw) <= LIMIT, "mailbox/document byte bound exceeded")
    return json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(Refusal("nonfinite JSON")))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)


def read(path):
    need(path.is_file() and not path.is_symlink(), "input is not a physical regular file")
    return decode(path.read_bytes())


def safe_relative(value):
    need(isinstance(value, str) and value and not value.startswith("/"), "invalid relative path")
    need(all(part not in {"", ".", ".."} for part in value.split("/")), "relative path alias")
    need("\\" not in value and "\x00" not in value, "relative path alias")
    return value


def environment():
    result = {k: v for k, v in os.environ.items()
              if not k.startswith(("GIT_", "IMPLEMENTAUDIT_")) and k not in {"GH_TOKEN", "GITHUB_TOKEN", "PYTHONPATH", "PYTHONHOME"}}
    result.update(PATH="/usr/bin:/bin", PYTHONDONTWRITEBYTECODE="1", LC_ALL="C.UTF-8",
                  GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
                  GIT_TERMINAL_PROMPT="0", IMPLEMENTAUDIT_PYTHON="/usr/bin/python3")
    return result


def run(out, label, argv, cwd, expected=0, timeout=120, exact_stdout=None):
    """Fixed caller argv only; retain both streams and return only stdout."""
    directory = out / "commands"
    directory.mkdir(exist_ok=True)
    ordinal = len(list(directory.glob("*.json"))) + 1
    stem = f"{ordinal:03d}-{label}"
    log = directory / (stem + ".log")
    error = directory / (stem + ".stderr")
    started = time.time()
    status = None
    cleanup = "not-started"
    timed_out = False
    owned_pgid = None
    with log.open("xb") as stream, error.open("xb") as error_stream:
        try:
            process = subprocess.Popen([str(v) for v in argv], cwd=cwd, env=environment(),
                                       stdout=stream, stderr=error_stream,
                                       stdin=subprocess.DEVNULL, start_new_session=True)
            owned_pgid = process.pid
            try:
                status = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    status = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    status = process.wait(timeout=5)
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                cleanup = "owned-process-group-absent"
            else:
                # A synchronous owner must not leave descendants behind.
                os.killpg(process.pid, signal.SIGKILL)
                cleanup = "remaining-owned-group-killed-terminal-state-unverified"
        finally:
            raw = log.read_bytes()
            stderr_raw = error.read_bytes()
            save(directory / (stem + ".json"), dict(argv=[str(v) for v in argv], cwd=str(cwd),
                 started_at_unix=started, ended_at_unix=time.time(), exit_code=status,
                 expected_exit=expected, timed_out=timed_out, process_cleanup=cleanup,
                 owned_pgid=owned_pgid,
                 output_file=log.name, output_bytes=len(raw), output_sha256=sha(raw),
                 output_capture="separate-stdout-stderr",
                 stderr=dict(file=error.name, bytes=len(stderr_raw), sha256=sha(stderr_raw))))
    need(not timed_out, label + " timed out; owned process group contained and original output preserved")
    need(cleanup == "owned-process-group-absent", label + " left an owned process-group residual")
    need(status == expected, f"{label} returned {status}, expected {expected}; original output preserved")
    if exact_stdout is not None:
        need((len(raw), sha(raw)) == exact_stdout and stderr_raw == b"",
             label + " output differs from the exact original failure signature; admission refused and output preserved")
    return raw.decode("utf-8", "strict").strip()


def verify_files(base, rows):
    need(isinstance(rows, list) and len(rows) > 0, "empty file population")
    seen = set()
    for row in rows:
        relative = safe_relative(row["path"])
        need(relative not in seen, "duplicate input identity")
        seen.add(relative)
        path = base / relative
        for part in (path, *path.parents):
            need(not part.is_symlink(), "aliased input path")
            if part == base:
                break
        info = path.stat()
        need(stat.S_ISREG(info.st_mode), "nonregular input")
        raw = path.read_bytes()
        need(len(raw) == row["bytes"] and sha(raw) == row["sha256"], "input byte identity differs: " + relative)
        if "git_blob" in row:
            need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"], "Git blob differs")
        if "mode" in row:
            need(stat.S_IMODE(info.st_mode) == int(row["mode"], 8), "input mode differs: " + relative)


def package_check(source, request):
    need(request["source_commit"] == SOURCE and request["source_tree"] == SOURCE_TREE, "selected source changed")
    rows = request["package_members"]
    need(len(rows) == 78, "selected package member population differs")
    verify_files(source, rows)
    actual = {p.relative_to(source).as_posix() for name in SKILLS
              for p in (source / "skills" / name).rglob("*") if p.is_file()}
    expected_skills = {r["path"] for r in rows if r["path"].startswith("skills/")}
    need(actual == expected_skills, "selected skill population has missing or extra files")
    need({p.name for p in (source / "skills").iterdir() if p.is_dir()} == SKILLS, "skill precedence/population differs")


def phase_document(root, baseline):
    return f"""# Original P07/H07 bounded diagnostic phase

The following markers are specification anchors, not emitted execution results.
IMPLEMENTAUDIT_PHASE_START
Task: Diagnose the frozen report mismatch through the two original entry envelopes.
Type: brownfield
Run root: {root}
Baseline ref: {baseline}
Owner/source: Root / frozen report implementation under subject/ and the exact selected governor package
Audit object: Original issue211 P07/H07 observation, with all wider obligations open
Depends on phases: none
Markdown fallback: STATE.md and the preserved command captures

## Current state excerpts
- The original subject remains frozen; its preserved report comparison is expected to refuse.
- No child invocation or model result exists at initialization.

## Work
- Observe the actual report comparison, register its actual abnormality, and expose current source/run evidence to Root.
- Receive actual bounded child results as data, then receive Root's separate decision.

## Implementation steps
- Step 1 target: subject/verify_report.py; verify: /usr/bin/python3 -B verify_report.py; expected exit 1 with the original mismatch retained.
- Step 2 target: STATE.md Andon log; verify: bash validate-run-root.sh; expected exit 0 for the real open governed object.
- Step 3 target: mailbox/returns.json and mailbox/decision.json; verify: hosted_governed.py receive then finish; expected exact bound data receipt and separate Root decision without text execution.

## Scope boundaries
In scope: isolated task custody, actual report comparison, L4 registration, one governed result, one direct result, separate Root rederivation.
Out of scope: subject repair, product changes, protected refs, host Stop hooks, fabricated model results, original commission closure.

## STOP conditions
- Stop if subject/verify_report.py or any frozen subject byte differs from the admitted request.
- Stop if a mailbox commit changes any path except its exact expected mailbox file.
- Stop if selected-package validation, controller currentness, or actual child provenance cannot be received by Root.

## Acceptance criteria
- [ ] Root receives the actual hosted currentness, registered failure and exact source identities before child routing.
- [ ] Root receives the actual governed and direct returns at their distinct caller/authority boundaries.
- [ ] Root records a separate evidence-based rederivation; the transport grants no original acceptance.

## Mandatory commands
- /usr/bin/python3 -B verify_report.py > verify-report.log 2>&1 — expected exit 1 retaining the report mismatch; property: behavioral; scope: exact frozen report comparison only; acceptance: non-textual; coverage: full; capture: verify-report.log
- bash validate-run-root.sh run-root > validate-root.log 2>&1 — expected exit 0; property: structural; scope: current open run-root structure only; coverage: full; capture: validate-root.log

The driver records the actual absolute argv, cwd, all output and producer exit status for each command; these forms name the existing owners, not executable mailbox strings.

## Evidence required
- Immutable admitted-object, post-return, and final evidence artifacts with actual run/claim/source identities.
- Real child dispatch/result provenance received by Root and the untouched frozen receiver oracle.

## Rollback / defer path
Keep the original failure and partial evidence. Remove only the uniquely owned disposable task root after final capture. A deadline or job termination never resolves the audit object.

## Maintenance notes
- Retire this one-shot transport after the bounded original observation is independently received; no product runtime member is added.

IMPLEMENTAUDIT_PHASE_VERIFY
AGENTS_UPDATE_DECISION: not warranted for disposable transport observation
CONTINUITY_DECISION: retain bounded exact evidence only
IMPLEMENTAUDIT_PHASE_DONE
"""


def write_documents(session, request):
    root, task = Path(session["run_root"]), Path(session["task"])
    relative = root.relative_to(task).as_posix()
    baseline = session["task_commit"]
    state = f"""# IMPLEMENTAUDIT State

## Current phase

| Field | Value |
|---|---|
| Run root | {relative} |
| Phase | 1 |
| Status | open |
| Audit object state | open |
| Route | existing governor, original P07/H07 |
| Owner/source | Root / frozen subject and selected a297 governor |
| Baseline ref | {baseline} |
| Last check | Exact frozen inputs received; task comparison not yet executed |
| Next action | Establish currentness then observe frozen report comparison |
| Authorization state | Ordinary bounded hosted observation only; no subject repair, protected effect or closure |
| Re-entry condition | Exact current controller and unchanged package/subject identities |
| Pending decision | Root receives real failure and chooses warranted diagnostic route |

## Audit object state

Original #211 P07/H07 bounded observation. Wider 36/14 and 17+15 obligations remain open.
No child output grants mutation, currentness, acceptance or closure.

## Andon log

| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |
|---|---|---|---|---|---|---|---|

## Context epochs

Current epoch: G0001

| Epoch | Boundary | Source | Live evidence | Reconciled | Preserved | Next action |
|---|---|---|---|---|---|---|

## Review boundary

Transport and phase plan review: {request['review']['evidence']}
This citation is an input to Root receiving, not self-issued review or acceptance.
"""
    roadmap = f"""# IMPLEMENTAUDIT Roadmap

## Goal
Execute the original frozen P07/H07 diagnostic observation through actual hosted custody and actual model returns.

## Audit object
Original issue211 cases P07/H07; no whole-case or commission acceptance is created by this file.

## Action selection
Selected: currentness, source/input identity checks, actual comparison, registered L4, real governed/direct cognition, separate Root decision.
Omitted: repair, native Stop, package rebuild, unrelated regression suites and release because those are outside this observation.

## Baseline ref
{baseline}

## Phases

| Phase | Objective | Owner/source | Depends on | Smoke A | Smoke B | Review | Status |
|---|---|---|---|---|---|---|---|
| 1 | Receive actual bounded diagnosis and Root rederivation | Root / frozen subject | - | exact comparison | unchanged input/currentness checks | PASS at separately recorded review | open |

## Scope boundaries
Root alone controls child routing and decisions. The transport accepts data, never shell or authority from a child.
"""
    docs = {"STATE.md": state, "ROADMAP.md": roadmap,
            "PROTOCOL.md": "# Bounded original diagnostic protocol\n\nInspect exact inputs, establish currentness, observe failure, register L4, return actual cognition to Root, rederive, verify and preserve truthful open state. No native Stop or completion claim.\n",
            "THINKING.md": "# Decision rationale\n\nLocal physical-interpreter custody refused. A real ordinary hosted run supplies the unchanged source owner's admitted filesystem. The mailbox carries actual model evidence and separate Root decisions; it never manufactures cognition or authority.\n",
            "sidecars.md": "# Sidecars\n\nGraphify: not configured. ActiveGraph: not configured. Markdown fallback: STATE.md, ROADMAP.md and captured command evidence.\n",
            "tools.md": "# Tools\n\nFixed /usr/bin/python3, /bin/bash and /usr/bin/git. Existing selected a297 lifecycle validators. GitHub REST reads of the single declared mailbox branch. No target-supplied command strings or model CLI.\n",
            "context.md": f"# Context\n\nParent controller: {request['parent_controller']}\nParent receipt: {request['parent_receipt']}\nSelected source: {SOURCE}\nFrozen challenge SHA256: {request['challenge_sha256']}\nThis disposable holon is bounded to original P07/H07 and cannot mutate parent custody.\n",
            "phases/phase-1.md": phase_document(relative, baseline)}
    for name, value in docs.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as stream:
            stream.write(value)


def state_value(session, key, value):
    need("\n" not in value and "|" not in value, "STATE scalar contains delimiter")
    path = Path(session["run_root"]) / "STATE.md"
    text = path.read_text()
    pattern = r"(?m)^\| " + re.escape(key) + r" \|[^\n]*$"
    replacement = f"| {key} | {value} |"
    if re.search(pattern, text):
        text, count = re.subn(pattern, lambda match: replacement, text)
        need(count == 1, "ambiguous STATE field")
    else:
        text = text.replace("\n## Audit object state", "\n" + replacement + "\n\n## Audit object state", 1)
    path.write_text(text)


def claim(session, out, label, *args):
    return run(out, label, ["/bin/bash", Path(session["source"]) / "skills/implementaudit/scripts/claim-run.sh", *args], Path(session["task"]))


def refresh(session, out, boundary, reason):
    controller = session["controller"]
    claim(session, out, "current-controller", "--current-controller", controller)
    event = session["exchange_id"] + "-" + str(session["epoch"] + 1)
    claim(session, out, "invalidate", "--invalidate-continuity", controller, "--boundary", boundary, "--event", event)
    root = Path(session["run_root"])
    # These are separate, completed, fully captured owner-facing reads.
    run(out, "read-STATE", ["/bin/cat", root / "STATE.md"], Path(session["task"]))
    run(out, "read-ROADMAP", ["/bin/cat", root / "ROADMAP.md"], Path(session["task"]))
    session["epoch"] += 1
    epoch = f"G{session['epoch']:04X}"
    path = root / "STATE.md"
    text = re.sub(r"(?m)^Current epoch: .*$", "Current epoch: " + epoch, path.read_text())
    row = f"| {epoch} | {boundary} | {reason} | {session['task_commit']} {session['task_tree']} | yes | original subject and failure | Root receives exact current evidence |\n"
    text = text.replace("\n## Review boundary", "\n" + row + "\n## Review boundary", 1)
    path.write_text(text)
    token = claim(session, out, "resume", "--resume-controller", controller, "--boundary", boundary, "--epoch", epoch)
    need(re.fullmatch(r"refs/implementaudit/continuity-receipts/[a-z0-9-]+/G[0-9A-F]{4}@[0-9a-f]{40}", token), "receipt output is not exact")
    claim(session, out, "verify", "--verify-resume-receipt", token)
    claim(session, out, "require", "--require-current-continuity", controller)
    session["continuity_receipt"] = token


def current_check(session, request, out):
    package_check(Path(session["source"]), request)
    verify_files(Path(session["task"]), request["subject_members"])
    claim(session, out, "require-current", "--require-current-continuity", session["controller"])
    run(out, "validate-current-root", ["/bin/bash", Path(session["source"]) / "skills/implementaudit/scripts/validate-run-root.sh", session["run_root"]], Path(session["task"]))


def authority_snapshot(session, out, label):
    task = Path(session["task"])
    refs = run(out, label + "-refs", ["/usr/bin/git", "for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/"], task)
    records = {}
    for line in refs.splitlines():
        ref, oid = line.split(" ")
        records[ref] = dict(oid=oid, raw=run(out, label + "-ref-blob", ["/usr/bin/git", "cat-file", "blob", oid], task))
    files = {}
    for path in sorted((task / ".IMPLEMENTAUDIT").rglob("*")):
        need(not path.is_symlink(), "authority path is aliased")
        if path.is_file():
            info = path.stat()
            raw = path.read_bytes()
            files[path.relative_to(task).as_posix()] = dict(bytes=len(raw), sha256=sha(raw),
                physical=[info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns, stat.S_IMODE(info.st_mode)])
    return dict(refs=records, files=files,
                head=run(out, label + "-head", ["/usr/bin/git", "rev-parse", "HEAD"], task),
                tree=run(out, label + "-tree", ["/usr/bin/git", "rev-parse", "HEAD^{tree}"], task))


def dg18_observation(session, request, out):
    spec = request["dg18"]
    need(spec["source_commit"] == "6b353b48b2fc8a6de0c6223f48d341c484c98191", "DG18 selected source differs")
    owner = Path(session["request_path"]).parent / "dg18-owner"
    need(len(spec["members"]) == 6, "DG18 consumed source population differs")
    verify_files(owner, spec["members"])
    need({p.name for p in owner.iterdir()} == {row["path"] for row in spec["members"]}, "DG18 source siblings differ")
    root = Path(session["run_root"])
    absent_map = root / "dg18-absent-owner-map.json"
    need(not os.path.lexists(absent_map), "DG18 fail-closed absent owner map is present")
    pair_size = sum((root / name).stat().st_size for name in ("STATE.md", "ROADMAP.md"))
    need(pair_size < 131072, "DG18 original no-trigger pair threshold does not hold")
    current_check(session, request, out)
    before = authority_snapshot(session, out, "dg18-before")
    result = run(out, "dg18-current-no-trigger", ["/bin/bash", owner / "claim-run.sh", "--rotate-canonical-state", session["controller"], "--owner-map", absent_map], Path(session["task"]))
    value = decode(result.encode())
    need(value.get("status") == "NOT_TRIGGERED" and value.get("receipt_token") == session["continuity_receipt"], "DG18 returned a different result/receipt")
    after = authority_snapshot(session, out, "dg18-after")
    verify_files(owner, spec["members"])
    need(not os.path.lexists(absent_map) and before == after, "DG18 no-trigger changed custody, source or authority")
    current_check(session, request, out)
    save(out / "DG18_ACTUAL_NOT_TRIGGERED.json", dict(source=spec, before=before, after=after,
         result=value, pair_bytes=pair_size, owner_map_absent=True, native_input_used=False,
         scope="Original A7 current CLI no-trigger only; no archive, model, CAS or complete native claim."))


def binding(session, request):
    root = Path(session["run_root"])
    return dict(exchange_id=session["exchange_id"], launch_commit=session["launch_commit"],
                run_id=session["run_id"], run_attempt=session["run_attempt"], source_commit=SOURCE,
                task_commit=session["task_commit"], controller=session["controller"], claim_id=session["claim_id"],
                continuity_receipt=session["continuity_receipt"], state_sha256=sha((root / "STATE.md").read_bytes()),
                roadmap_sha256=sha((root / "ROADMAP.md").read_bytes()), challenge_sha256=request["challenge_sha256"])


def snapshot(out, name, session, request, extra=None):
    folder = out / name
    folder.mkdir()
    root = Path(session["run_root"])
    for member in ("STATE.md", "ROADMAP.md", "PROTOCOL.md", "THINKING.md", "context.md", "tools.md", "sidecars.md"):
        shutil.copyfile(root / member, folder / member)
    shutil.copyfile(root / ".claimed", folder / "claim-metadata.txt")
    save(folder / "CONTROLLER_REFS.json", authority_snapshot(session, out, name))
    shutil.copytree(out / "commands", folder / "commands")
    if (out / "DG18_ACTUAL_NOT_TRIGGERED.json").exists():
        shutil.copyfile(out / "DG18_ACTUAL_NOT_TRIGGERED.json", folder / "DG18_ACTUAL_NOT_TRIGGERED.json")
    data = dict(schema="dg17.actual-hosted-object.v1", binding=binding(session, request),
                package_members=request["package_members"], subject_members=request["subject_members"],
                source_root=session["source"], task_root=session["task"], run_root=session["run_root"],
                native_Stop_claim=False, authority="NONE_TRANSPORT_EVIDENCE_ONLY", **(extra or {}))
    save(folder / "PACKET.json", data)
    return data["binding"]


def store_session(out, session):
    path = out / "SESSION.json"
    temporary = out / "SESSION.next.json"
    save(temporary, session)
    os.replace(temporary, path)


def prepare(args):
    out, source, request_path = args.output.resolve(), Path.cwd().resolve(), args.request.resolve()
    out.mkdir(parents=True, exist_ok=True)
    need(not (out / "SESSION.json").exists(), "this exchange already started; no replay")
    request = read(request_path)
    need(request["schema"] == "dg17.original-hosted-request.v1", "request schema differs")
    need(os.environ.get("GITHUB_ACTIONS") == "true", "prepare requires the real hosted job")
    need(os.environ.get("GITHUB_REPOSITORY") == REPOSITORY and os.environ.get("GITHUB_REF_NAME") == BRANCH, "hosted repository/ref differs")
    need(os.environ.get("GITHUB_RUN_ATTEMPT") == "1", "reruns are not an admitted launch")
    need(request["review"]["status"] == "PASS" and request["review"]["evidence"].strip(), "independent reviewed preflight is not received")
    package_check(source, request)
    need(run(out, "source-tree", ["/usr/bin/git", "rev-parse", SOURCE + "^{tree}"], source) == SOURCE_TREE, "source tree differs")
    launch = os.environ["GITHUB_SHA"]
    need(run(out, "launch-parent", ["/usr/bin/git", "rev-parse", launch + "^"], source) == LAUNCH_PARENT, "launch must be one direct child of the retained failed publication")
    run(out, "package-source-unchanged", ["/usr/bin/git", "diff", "--exit-code", SOURCE, launch, "--", "skills", ".codex-plugin", ".claude-plugin", "package"], source)
    task = Path(tempfile.mkdtemp(prefix="dg17-governed-", dir=os.environ["RUNNER_TEMP"])).resolve()
    session = dict(schema="dg17.exchange-custody.v1", exchange_id=uuid.uuid4().hex,
                   source=str(source), task=str(task), output=str(out), request_path=str(request_path),
                   launch_commit=launch, last_mail_commit=launch, run_id=os.environ["GITHUB_RUN_ID"],
                   run_attempt=os.environ["GITHUB_RUN_ATTEMPT"], controller="dg17-p07-" + os.environ["GITHUB_RUN_ID"],
                   epoch=0, deadline_unix=time.time() + WINDOW_SECONDS, stage="INITIALIZING")
    (task / ".transport-owner").write_text(session["exchange_id"])
    store_session(out, session)
    verify_files(request_path.parent, request["subject_members"])
    for row in request["subject_members"]:
        target = task / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((request_path.parent / row["path"]).read_bytes())
    (task / ".gitignore").write_text(".IMPLEMENTAUDIT/\n.transport-owner\n")
    run(out, "init-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "init", "--initial-branch=original-p07"], task)
    run(out, "add-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "add", "subject", ".gitignore"], task)
    run(out, "commit-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=IMPLEMENTAUDIT bounded Root task", "-c", "user.email=bounded-root@invalid.example", "commit", "-m", "Bind unchanged original P07 subject"], task)
    session["task_commit"] = run(out, "task-head", ["/usr/bin/git", "rev-parse", "HEAD"], task)
    session["task_tree"] = run(out, "task-tree", ["/usr/bin/git", "rev-parse", "HEAD^{tree}"], task)
    relative = claim(session, out, "claim-task", "--controller", session["controller"], "original-p07-h07")
    safe_relative(relative)
    session["run_root"] = str(task / relative)
    session["claim_id"] = dict(line.split("=", 1) for line in (Path(session["run_root"]) / ".claimed").read_text().splitlines())["claim_id"]
    write_documents(session, request)
    inspected = json.loads(claim(session, out, "inspect-initialization", "--inspect-controller-initialization", session["controller"], "--run-root", relative))
    token = inspected["initialization_token"]
    claim(session, out, "activate-controller", "--activate-controller", session["controller"], "--run-root", relative, "--expected-initialization", token)
    refresh(session, out, "new-session", "actual hosted task initialization")
    current_check(session, request, out)
    dg18_observation(session, request, out)
    # Original episode06 common/PREPARER_OBSERVATIONS.json, current acceptance check.
    run(out, "verify-report", ["/usr/bin/python3", "-B", "verify_report.py"], task / "subject", expected=1,
        exact_stdout=(266, "8b1b08cef34ced774fb20cb696a79a51b1a76e6f2adc953a084e8d751691bf0a"))
    verify_files(task, request["subject_members"])
    root = Path(session["run_root"])
    text = (root / "STATE.md").read_text()
    text = text.replace("\n## Context epochs", "\n| 1 | p07-actual-report | 1 | failed-criterion | Actual frozen report comparison returned exit 1 | Contain report consumption and request bounded causal diagnosis; owner/source=subject/ | Preserved actual verify-report capture; repair is outside this transport | open (rerun pending) |\n\n## Context epochs", 1)
    text += "\n## Actual abnormality\n\nANDON_PROBE\nGap: actual report comparison refuses. Cause: not yet adjudicated; supplied source requires bounded causal analysis. Countermeasure: withhold report use and request one governed diagnostic return. Follow-up: Root receives facts, causal options and concrete evidence obligations before any separate repair.\n"
    (root / "STATE.md").write_text(text)
    state_value(session, "Status", "BLOCKED")
    state_value(session, "Last check", "Actual frozen report comparison returned exit 1; complete output retained")
    state_value(session, "Next action", "Root receives admitted failure packet and routes one bounded diagnostic child")
    state_value(session, "Blocker", "Causal disposition of the actual report mismatch remains open")
    state_value(session, "Containment", "Withhold report consumption while the mismatch is unresolved; preserve subject bytes")
    refresh(session, out, "manual-resume", "actual Andon state registration before child dispatch")
    current_check(session, request, out)
    selected = run(out, "resolve-child", ["/usr/bin/python3", "-B", Path(session["source"]) / "skills/implementaudit/scripts/resolve-internal-skill.py", "--governor", Path(session["source"]) / "skills/implementaudit/SKILL.md", "--child", "audit-andon"], task)
    session["ready_binding"] = snapshot(out, "admitted", session, request,
        dict(child_loaded=False, child_resolver_result=selected, actual_abnormality="p07-actual-report", direct_entry_must_use_same_subject=True,
             expected_return_path=RETURN_PATH, expected_return_parent=launch, deadline_unix=session["deadline_unix"]))
    session["stage"] = "WAITING_ACTUAL_RETURNS"
    store_session(out, session)
    print("ADMITTED_OBJECT_AVAILABLE; no child has been loaded by this transport")


def api(endpoint):
    need(endpoint.startswith("/repos/" + REPOSITORY + "/"), "API endpoint outside declared repository")
    token = os.environ.get("GH_TOKEN", "")
    need(bool(token), "repository read credential unavailable")
    request = urllib.request.Request("https://api.github.com" + endpoint,
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(2 * LIMIT + 1)
    need(len(raw) <= 2 * LIMIT, "provider response bound exceeded")
    return json.loads(raw)


def wait_mail(session, out, wanted):
    parent = session["last_mail_commit"]
    while time.time() < session["deadline_unix"]:
        observed = api("/repos/" + REPOSITORY + "/git/ref/heads/" + urllib.parse.quote(BRANCH, safe="/"))
        head = observed["object"]["sha"]
        if head == parent:
            time.sleep(15)
            continue
        stem = "mail-" + str(len(list(out.glob("mail-*-observed.json"))) + 1)
        valid_head = isinstance(head, str) and re.fullmatch(r"[0-9a-f]{40}", head) is not None
        save(out / (stem + "-observed.json"),
             dict(repository=REPOSITORY, branch=BRANCH, expected_parent=parent, expected_path=wanted,
                  observed_head=head if valid_head else None, observed_head_type=type(head).__name__,
                  head_valid=valid_head, retrieved_at_unix=time.time()))
        need(valid_head, "mailbox head is not an exact commit")
        commit = api("/repos/" + REPOSITORY + "/commits/" + head)
        parents = [p["sha"] for p in commit["parents"]]
        files = commit.get("files", [])
        save(out / (stem + "-commit.json"),
             dict(commit=head, observed_parents=parents, expected_parent=parent, expected_path=wanted,
                  file_count=len(files), files=[{key: row.get(key) for key in ("filename", "status", "sha")}
                                               for row in files[:300]], retrieved_at_unix=time.time()))
        need(parents == [parent], "mailbox parent changed or skipped")
        need(len(files) == 1 and files[0]["filename"] == wanted and files[0]["status"] == "added", "mailbox commit changed an unexpected path")
        blob = api("/repos/" + REPOSITORY + "/git/blobs/" + files[0]["sha"])
        save(out / (stem + "-blob.json"),
             dict(commit=head, path=wanted, expected_blob=files[0]["sha"], reported_blob=blob.get("sha"),
                  reported_size=blob.get("size"), encoding=blob.get("encoding"), retrieved_at_unix=time.time()))
        need(blob["encoding"] == "base64" and blob["size"] <= LIMIT, "mailbox blob encoding/size differs")
        raw = base64.b64decode(blob["content"], validate=False)
        need(len(raw) == blob["size"], "mailbox size mismatch")
        need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == files[0]["sha"], "mailbox Git blob mismatch")
        raw_path = out / (stem + ".raw")
        with raw_path.open("xb") as stream:
            stream.write(raw)
        save(out / (stem + ".json"),
             dict(commit=head, parent=parent, path=wanted, blob=files[0]["sha"], bytes=len(raw), sha256=sha(raw),
                  raw_file=raw_path.name, retrieved_at_unix=time.time()))
        value = decode(raw)
        return head, raw, value
    raise Refusal("transport deadline reached; no original obligation is resolved and no replay is authorized")


def validate_returns(value, expected):
    need(set(value) == {"schema", "binding", "entries"} and value["schema"] == "dg17.actual-child-returns.v1", "child return schema differs")
    need(value["binding"] == expected, "child return binding is stale/foreign")
    entries = value["entries"]
    need(isinstance(entries, list) and len(entries) == 2, "exactly governed and direct returns required")
    need([entry.get("entry") for entry in entries] == ["governed", "direct"], "return entry order/population differs")
    for entry in entries:
        need(set(entry) == {"entry", "caller", "return_owner", "provenance", "result_text", "result_sha256"}, "unexpected return field")
        need(isinstance(entry["caller"], str) and entry["caller"] and entry["return_owner"] == entry["caller"], "return owner differs from actual declared caller")
        need(isinstance(entry["result_text"], str) and 0 < len(entry["result_text"].encode()) <= 65536, "missing/oversized actual result")
        need(sha(entry["result_text"].encode()) == entry["result_sha256"], "actual result digest differs")
        fields = {"actor_id", "model_identity", "dispatch_evidence", "return_evidence", "prompt_sha256", "skill_sha256"}
        need(isinstance(entry["provenance"], dict) and set(entry["provenance"]) == fields, "actual provenance fields missing")
        need(all(isinstance(v, str) and v.strip() for v in entry["provenance"].values()), "empty actual provenance")
        for key in ("prompt_sha256", "skill_sha256"):
            need(re.fullmatch(r"[0-9a-f]{64}", entry["provenance"][key]), "invalid provenance digest")


def receive(args):
    out = args.output.resolve()
    session = read(out / "SESSION.json")
    need(session["stage"] == "WAITING_ACTUAL_RETURNS", "return already received or stage differs")
    request = read(Path(session["request_path"]))
    current_check(session, request, out)
    head, raw, value = wait_mail(session, out, RETURN_PATH)
    validate_returns(value, session["ready_binding"])
    expected_child = next(row["sha256"] for row in request["package_members"] if row["path"] == "skills/audit-andon/SKILL.md")
    need(all(e["provenance"]["skill_sha256"] == expected_child for e in value["entries"]), "child source differs")
    current_check(session, request, out)
    (out / "actual-child-returns.json").write_bytes(raw)
    session["last_mail_commit"], session["return_sha256"] = head, sha(raw)
    state_value(session, "Last check", "Actual child return bytes received as untrusted evidence; Root independently owns provenance and judgment")
    state_value(session, "Next action", "Root reads fresh post-return currentness and separately records rederived decision")
    refresh(session, out, "manual-resume", "actual child return received as bounded evidence")
    current_check(session, request, out)
    session["return_binding"] = snapshot(out, "returned", session, request,
        dict(return_commit=head, return_sha256=sha(raw), result_authority="NONE", Root_rederivation_received=False,
             expected_decision_path=DECISION_PATH, expected_decision_parent=head))
    session["stage"] = "WAITING_ROOT_REDERIVATION"
    store_session(out, session)
    print("ACTUAL_RETURN_BYTES_AVAILABLE; Root rederivation remains pending")


def validate_decision(value, session):
    need(set(value) == {"schema", "binding", "return_commit", "return_sha256", "decision", "reason", "next_action", "Root_receiving_evidence"}, "Root decision schema fields differ")
    need(value["schema"] == "dg17.Root-rederivation.v1" and value["binding"] == session["return_binding"], "Root decision binding differs")
    need(value["return_commit"] == session["last_mail_commit"] and value["return_sha256"] == session["return_sha256"], "Root decision consumes different result")
    need(value["decision"] in DECISIONS, "Root decision is not a finite allowed disposition")
    for key in ("reason", "next_action", "Root_receiving_evidence"):
        text = value[key]
        need(isinstance(text, str) and 8 <= len(text) <= 4096 and "\n" not in text and "|" not in text, "Root decision scalar malformed")


def finish(args):
    out = args.output.resolve()
    session = read(out / "SESSION.json")
    need(session["stage"] == "WAITING_ROOT_REDERIVATION", "Root decision already received or stage differs")
    request = read(Path(session["request_path"]))
    current_check(session, request, out)
    head, raw, value = wait_mail(session, out, DECISION_PATH)
    validate_decision(value, session)
    current_check(session, request, out)
    (out / "actual-Root-decision.json").write_bytes(raw)
    state_value(session, "Last check", "Actual separate Root rederivation received; no child authority or source repair executed")
    state_value(session, "Next action", value["next_action"])
    session["last_mail_commit"] = head
    refresh(session, out, "manual-resume", "actual separate Root decision recorded with open original residual")
    current_check(session, request, out)
    snapshot(out, "final", session, request,
        dict(Root_decision_commit=head, Root_decision_sha256=sha(raw), decision=value["decision"],
             original_acceptance="ROOT_AND_INDEPENDENT_RECEIVING_ONLY", subject_repaired=False,
             original_audit_object="OPEN", child_has_authority=False))
    session["stage"] = "ROOT_DECISION_RECORDED"
    store_session(out, session)
    print("ROOT_DECISION_RECORDED; original residual and all native claims remain separately scoped")


def finalize(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    unresolved_processes = []
    for record_path in sorted((out / "commands").glob("*.json")):
        record = read(record_path)
        cleanup, pgid = record.get("process_cleanup"), record.get("owned_pgid")
        if cleanup != "owned-process-group-absent" and not (cleanup == "not-started" and pgid is None):
            unresolved_processes.append(dict(record=record_path.name, owned_pgid=pgid, reported_cleanup=cleanup))
    path = out / "SESSION.json"
    if not path.exists():
        save(out / "CLEANUP.json", dict(task_started=False, residual="prepare did not establish task custody",
             host_custody_terminated=not unresolved_processes, unresolved_processes=unresolved_processes, audit_closure=False))
        need(not unresolved_processes, "command process terminal state remains unverified; original captures retained")
        return
    session = read(path)
    task = Path(session["task"])
    need(task.parent == Path(os.environ["RUNNER_TEMP"]).resolve() and task.name.startswith("dg17-governed-"), "cleanup root differs")
    need(not task.is_symlink() and (task / ".transport-owner").read_text() == session["exchange_id"], "cleanup ownership differs")
    with tarfile.open(out / "actual-task-custody.tar.gz", "x:gz") as archive:
        archive.add(task, arcname="actual-task", recursive=True)
    if not unresolved_processes:
        shutil.rmtree(task)
    save(out / "CLEANUP.json", dict(task_started=True, task_removed=not task.exists(),
         prior_stage=session["stage"], archive_sha256=sha((out / "actual-task-custody.tar.gz").read_bytes()),
         archive_consistency="UNVERIFIED_PROCESS_MAY_BE_ACTIVE" if unresolved_processes else "TERMINAL_COMMANDS",
         host_custody_terminated=not unresolved_processes and not task.exists(),
         unresolved_processes=unresolved_processes, audit_closure=False, native_Stop_claim=False,
         residual="Owned process terminal state is unverified; task retained and archive is a nonterminal snapshot."
                  if unresolved_processes else "Captured object remains open; final evidence is historical, not reusable live custody."))
    need(not unresolved_processes, "owned process terminal state remains unverified; task retained and termination not claimed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["prepare", "receive", "finish", "finalize"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    args = parser.parse_args()
    try:
        globals()[args.operation](args)
    except Exception as exc:
        args.output.mkdir(parents=True, exist_ok=True)
        path = args.output / ("FAILURE-" + args.operation + ".json")
        if not path.exists():
            save(path, dict(operation=args.operation, failure_type=type(exc).__name__, detail=str(exc),
                           at_unix=time.time(), audit_closure=False, replay_authorized=False))
        print(f"{args.operation} refused: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
