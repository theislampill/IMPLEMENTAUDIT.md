#!/usr/bin/env python3
"""One prospective original L04/M4 selection and actual DG17 receiving exchange.
No returned text is executed. No protected operation or parent custody is touched.
"""
import argparse, base64, hashlib, importlib.util, json, os, re, shutil, signal
import subprocess, sys, tarfile, tempfile, time, urllib.parse, urllib.request, uuid
from pathlib import Path
SOURCE = "05371833d30e81815475d0d00aa107b6be5fbba3"
SOURCE_TREE = "d5a35d88ae08df60a48ad758ffc2fe5482de6083"
REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg16-m4-native-receiving-20261117"
PREFIX = "handoff/dg16-m4-native"
RETURN_PATH = PREFIX + "/mailbox/return.json"
DECISION_PATH = PREFIX + "/mailbox/decision.json"
LIMIT = 512 * 1024
WINDOW_SECONDS = 2700
NODE = "DG17_RECEIVING"


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

def finalize(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    unresolved_processes = []
    commands = out / "commands"
    stems = sorted({path.stem for pattern in ("*.json", "*.log", "*.stderr")
                    for path in commands.glob(pattern)})
    terminal_fields = {"argv", "cwd", "started_at_unix", "ended_at_unix", "exit_code",
        "expected_exit", "timed_out", "process_cleanup", "owned_pgid", "output_file",
        "output_bytes", "output_sha256", "output_capture", "stderr"}
    for stem in stems:
        record_path, stdout_path, stderr_path = (commands / (stem + suffix)
                                               for suffix in (".json", ".log", ".stderr"))
        cleanup = pgid = None
        try:
            need(all(path.is_file() and not path.is_symlink()
                     for path in (record_path, stdout_path, stderr_path)),
                 "command stream or terminal record is missing/nonregular")
            record = read(record_path)
            need(type(record) is dict and terminal_fields <= set(record),
                 "terminal record is incomplete")
            cleanup, pgid = record["process_cleanup"], record["owned_pgid"]
            # A null PID / not-started label is not terminal proof after an
            # interruption around process creation; preserve that uncertainty.
            need(cleanup == "owned-process-group-absent" and type(pgid) is int and pgid > 0
                 and type(record["exit_code"]) is int and type(record["timed_out"]) is bool,
                 "owned process group lacks complete terminal evidence")
            times = (record["started_at_unix"], record["ended_at_unix"])
            need(all(type(value) in {int, float} and -float("inf") < value < float("inf")
                     for value in times) and times[0] <= times[1],
                 "command terminal interval is incomplete")
            need(record["output_capture"] == "separate-stdout-stderr"
                 and type(record["stderr"]) is dict, "terminal stream descriptors are incomplete")
            for path, fields in ((stdout_path, dict(file=record["output_file"],
                    bytes=record["output_bytes"], sha256=record["output_sha256"])),
                    (stderr_path, record["stderr"])):
                raw = path.read_bytes()
                need(fields.get("file") == path.name and type(fields.get("bytes")) is int
                     and fields["bytes"] == len(raw) and fields.get("sha256") == sha(raw),
                     "terminal record does not match the retained command stream")
        except (Refusal, OSError, ValueError, TypeError) as exc:
            unresolved_processes.append(dict(record=record_path.name, owned_pgid=pgid,
                reported_cleanup=cleanup, evidence_problem=str(exc)))
    path = out / "SESSION.json"
    if not path.exists():
        save(out / "CLEANUP.json", dict(task_started=False, residual="prepare did not establish task custody",
             host_custody_terminated=not unresolved_processes, unresolved_processes=unresolved_processes, audit_closure=False))
        need(not unresolved_processes, "command process terminal state remains unverified; original captures retained")
        return
    session = read(path)
    task = Path(session["task"])
    need(task.parent == Path(os.environ["RUNNER_TEMP"]).resolve() and task.name.startswith("dg16-m4-"), "cleanup root differs")
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


def source_check(session, request, out):
    source = Path(session["source"])
    for row in request["source_members"]:
        path = source / safe_relative(row["path"])
        need(path.is_file() and not path.is_symlink(), "source member not a physical file")
        raw = path.read_bytes()
        need((len(raw), sha(raw), path.stat().st_mode & 0o777) ==
             (row["bytes"], row["sha256"], row["mode"]), "source bytes/mode differ: " + row["path"])
    need(run(out, "source-clean", ["/usr/bin/git", "status", "--porcelain=v1", "--untracked-files=all"], source) == "", "launch source changed")
    for row in request["inputs"]:
        raw = (Path(session["task"]) / row["path"]).read_bytes()
        need((len(raw), sha(raw)) == (row["bytes"], row["sha256"]), "task evidence input changed")


def claim(session, out, label, *args):
    return run(out, label, ["/bin/bash", Path(session["source"]) / "skills/implementaudit/scripts/claim-run.sh", *args], Path(session["task"]))


def store_session(out, session):
    path = out / "SESSION.json"
    path.write_text(json.dumps(session, sort_keys=True, indent=2) + "\n")


def refresh(session, out, boundary, reason):
    controller = session["controller"]
    claim(session, out, "current-controller", "--current-controller", controller)
    event = session["exchange_id"] + "-" + str(session["epoch"] + 1)
    claim(session, out, "invalidate", "--invalidate-continuity", controller, "--boundary", boundary, "--event", event)
    root = Path(session["run_root"])
    run(out, "read-STATE", ["/bin/cat", root / "STATE.md"], Path(session["task"]))
    run(out, "read-ROADMAP", ["/bin/cat", root / "ROADMAP.md"], Path(session["task"]))
    session["epoch"] += 1
    epoch = f"G{session['epoch']:04X}"
    path = root / "STATE.md"
    text = re.sub(r"(?m)^Current epoch: .*$", "Current epoch: " + epoch, path.read_text())
    row = f"| {epoch} | {boundary} | {reason} | {session['task_commit']} {session['task_tree']} | yes | immutable original inputs; blocked G132 | exact bounded receiving |\n"
    text = text.replace("\n## Review boundary", "\n" + row + "\n## Review boundary", 1)
    path.write_text(text)
    token = claim(session, out, "resume", "--resume-controller", controller, "--boundary", boundary, "--epoch", epoch)
    need(re.fullmatch(r"refs/implementaudit/continuity-receipts/[a-z0-9-]+/G[0-9A-F]{4}@[0-9a-f]{40}", token), "receipt output is not exact")
    need(claim(session, out, "verify", "--verify-resume-receipt", token) == token, "receipt verification differs")
    need(claim(session, out, "require", "--require-current-continuity", controller) == token, "current receipt differs")
    session["continuity_receipt"] = token


def current_check(session, request, out):
    source_check(session, request, out)
    need(claim(session, out, "require-current", "--require-current-continuity", session["controller"]) == session["continuity_receipt"], "current receipt changed")
    run(out, "validate-current-root", ["/bin/bash", Path(session["source"]) / "skills/implementaudit/scripts/validate-run-root.sh", session["run_root"]], Path(session["task"]))


def owner(session):
    path = Path(session["source"]) / "skills/implementaudit/scripts/compile-work-graph.py"
    need(sha(path.read_bytes()) == "0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d", "native compiler bytes differ")
    spec = importlib.util.spec_from_file_location("_m4_unchanged_native_owner", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def acquire(session):
    module = owner(session)
    sources, closures = [], []
    with module.observe_native_run_v1(session["run_root"], session["task"],
            _continuity_sources=sources, _continuity_closures=closures) as raw:
        graph = module.decode_strict_json_bytes(raw, "actual M4 native graph")
        transition = module.compile_recursive_transition_v1(graph, [])
    # No result escapes until the real native owner's closing guards finish.
    need(graph["binding"]["acquisition"] == "NATIVE_CONTINUITY_VERIFIED", "constructed acquisition is not admitted")
    need(transition["selected"] == [NODE], "native selection is not the reserved receiving task")
    nodes = {row["id"]: row for row in graph["nodes"]}
    need(nodes["G2_COMPLETED"]["state"] == "DONE" and nodes["DG17_EPISODE"]["state"] == "DONE", "completed prerequisites changed")
    need(nodes["G132_EFFECT"]["state"] == nodes["QUALIFY"]["state"] == "BLOCKED", "protected effect or ancestor JOIN is not blocked")
    need(nodes["ORIGINAL_QUALIFICATION"]["state"] == "ACTIVE", "actual governor occupancy was lost")
    return graph, transition, dict(sources=sources, closures=closures)


def native_select(args):
    out = args.output.resolve()
    session = read(out / "SESSION.json")
    graph, transition, closure = acquire(session)
    save(out / "GRAPH.json", graph)
    save(out / "TRANSITION.json", transition)
    save(out / "NATIVE_CLOSURE.json", closure)
    print("NATIVE_SELECTION_COMPLETE; independent receiving not yet dispatched")


def selection_binding(session, out):
    graph, transition = read(out / "GRAPH.json"), read(out / "TRANSITION.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE)
    reads = {p: graph["binding"]["read_set"][p] for p in node["reads"] + node["invalidators"] if p.startswith("path:")}
    return dict(exchange_id=session["exchange_id"], run_id=session["run_id"], run_attempt=session["run_attempt"],
        launch_commit=session["launch_commit"], controller=session["controller"], claim_id=session["claim_id"],
        continuity_receipt=session["continuity_receipt"], node=NODE, graph_digest=graph["digest"],
        dispatch_id=transition["dispatch_id"], input_digest=node["input_digest"],
        input_root_identity=graph["binding"]["input_root_identity"], read_set=reads,
        consumer=transition["consumers"][NODE]["node"], condition=transition["consumers"][NODE]["condition"])


def snapshot(session, request, out, name):
    target = out / name
    target.mkdir(exist_ok=False)
    for member in ("GRAPH.json", "TRANSITION.json", "NATIVE_CLOSURE.json", "SELECTION.json"):
        shutil.copyfile(out / member, target / member)
    for member in ("STATE.md", "ROADMAP.md", "phases/phase-1.md", ".claimed", ".controller"):
        path = target / "run-root" / member
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(session["run_root"]) / member, path)
    shutil.copytree(Path(session["task"]) / "inputs", target / "inputs")
    shutil.copytree(out / "commands", target / "commands")
    shutil.copyfile(session["request_path"], target / "REQUEST.json")
    refs = run(out, name + "-refs", ["/usr/bin/git", "for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/"], Path(session["task"]))
    save(target / "CONTROLLER_REFS.json", dict(refs=refs.splitlines(), authority="HISTORICAL_OBSERVATION_ONLY"))
    for ordinal, line in enumerate(refs.splitlines()):
        ref, oid = line.split()
        blob = run(out, name + "-ref-" + str(ordinal), ["/usr/bin/git", "cat-file", "blob", oid], Path(session["task"]))
        save(target / ("REF-" + str(ordinal) + ".json"), dict(ref=ref, oid=oid, text=blob))


def prepare(args):
    out, source, request_path = args.output.resolve(), Path.cwd().resolve(), args.request.resolve()
    out.mkdir(parents=True, exist_ok=True)
    need(not (out / "SESSION.json").exists(), "exchange already started; no replay")
    request = read(request_path)
    need(request["schema"] == "dg16.m4-prospective-request.v1" and request["source"] == SOURCE and request["source_tree"] == SOURCE_TREE and request["branch"] == BRANCH, "request source/branch differs")
    need(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == REPOSITORY and os.environ.get("GITHUB_REF_NAME") == BRANCH, "actual hosted repository/ref differs")
    need(os.environ.get("GITHUB_RUN_ATTEMPT") == "1", "rerun is not an admitted launch")
    need(request["review"]["status"] == "PASS" and request["review"]["evidence"].strip(), "actual source review required")
    launch = os.environ["GITHUB_SHA"]
    need(run(out, "launch-parent", ["/usr/bin/git", "rev-parse", launch + "^"], source) == SOURCE, "launch is not a direct child of exact053")
    need(run(out, "source-tree", ["/usr/bin/git", "rev-parse", SOURCE + "^{tree}"], source) == SOURCE_TREE, "source tree differs")
    changes = run(out, "launch-changes", ["/usr/bin/git", "diff", "--name-only", SOURCE, launch], source).splitlines()
    need(changes and all(p.startswith(PREFIX + "/") or p == ".github/workflows/dg16-m4-native.yml" for p in changes), "launch changed a source or unrelated path")
    task = Path(tempfile.mkdtemp(prefix="dg16-m4-", dir=os.environ["RUNNER_TEMP"])).resolve()
    session = dict(schema="dg16.m4-task-custody.v1", exchange_id=uuid.uuid4().hex,
        source=str(source), task=str(task), output=str(out), request_path=str(request_path),
        launch_commit=launch, last_mail_commit=launch, run_id=os.environ["GITHUB_RUN_ID"],
        run_attempt=os.environ["GITHUB_RUN_ATTEMPT"], controller="dg16-m4-" + os.environ["GITHUB_RUN_ID"],
        epoch=0, deadline_unix=time.time() + WINDOW_SECONDS, stage="INITIALIZING")
    (task / ".transport-owner").write_text(session["exchange_id"])
    store_session(out, session)
    for row in request["inputs"]:
        raw = base64.b64decode((request_path.parent / safe_relative(row["transport"])).read_bytes(), validate=False)
        need((len(raw), sha(raw)) == (row["bytes"], row["sha256"]), "frozen input bytes differ")
        path = task / safe_relative(row["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.chmod(0o644)
    (task / ".gitignore").write_text(".IMPLEMENTAUDIT/\n.transport-owner\n")
    run(out, "init-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "init", "--initial-branch=m4-receiving"], task)
    run(out, "add-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "add", "inputs", ".gitignore"], task)
    run(out, "commit-task", ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=IMPLEMENTAUDIT bounded Root task", "-c", "user.email=bounded-root@invalid.example", "commit", "-m", "Bind prospective original M4 receiving inputs"], task)
    session["task_commit"] = run(out, "task-head", ["/usr/bin/git", "rev-parse", "HEAD"], task)
    session["task_tree"] = run(out, "task-tree", ["/usr/bin/git", "rev-parse", "HEAD^{tree}"], task)
    source_check(session, request, out)
    relative = safe_relative(claim(session, out, "claim-task", "--controller", session["controller"], "original-m4-receiving"))
    session["run_root"] = str(task / relative)
    session["claim_id"] = dict(line.split("=", 1) for line in (Path(session["run_root"]) / ".claimed").read_text().splitlines())["claim_id"]
    spec = importlib.util.spec_from_file_location("_m4_documents", Path(__file__).with_name("documents.py"))
    documents = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(documents)
    documents.write_documents(session, request)
    inspected = decode(claim(session, out, "inspect-initialization", "--inspect-controller-initialization", session["controller"], "--run-root", relative).encode())
    claim(session, out, "activate-controller", "--activate-controller", session["controller"], "--run-root", relative, "--expected-initialization", inspected["initialization_token"])
    refresh(session, out, "new-session", "actual fresh hosted M4 task initialization")
    current_check(session, request, out)
    store_session(out, session)
    run(out, "native-select", ["/usr/bin/python3", "-I", "-S", "-B", Path(__file__).resolve(), "native-select", "--output", out], task, timeout=600)
    session["selected_at_unix"] = time.time()
    session["selection_binding"] = selection_binding(session, out)
    save(out / "SELECTION.json", dict(schema="dg16.m4-actual-selection.v1", binding=session["selection_binding"],
        selected_at_unix=session["selected_at_unix"], deadline_unix=session["deadline_unix"],
        expected_return_path=RETURN_PATH, expected_return_parent=launch, expected_decision_path=DECISION_PATH,
        reviewer_dispatched=False, authority="NONE", G132="UNKNOWN_NO_REPLAY", whole_JOIN="BLOCKED",
        input_root_scope="Original native input identity; a copied exact evidence set does not impersonate the reviewer's physical host."))
    snapshot(session, request, out, "selected")
    session["stage"] = "WAITING_ACTUAL_REVIEW"
    store_session(out, session)
    print("ACTUAL_NATIVE_SELECTION_AVAILABLE; Root may now dispatch the reserved independent receiving")


def validate_return_value(value, session):
    need(set(value) == {"schema", "binding", "reviewer", "dispatched_at_unix", "completed_at_unix", "dispatch_evidence", "return_evidence", "review_utf8", "review_sha256", "disposition", "authority", "closure"}, "independent return fields differ")
    need(value["schema"] == "dg16.m4-actual-independent-return.v1" and value["binding"] == session["selection_binding"], "return has stale/cross-run selection binding")
    need(value["authority"] == "NONE" and value["closure"] is False, "return claims authority/closure")
    need(value["disposition"] in {"PASS", "GAP-REVISE", "BLOCKED"}, "review disposition differs")
    for key in ("reviewer", "dispatch_evidence", "return_evidence"):
        need(isinstance(value[key], str) and 8 <= len(value[key]) <= 4096, "missing actual independent provenance")
    need(type(value["dispatched_at_unix"]) in {int, float} and type(value["completed_at_unix"]) in {int, float}, "review timestamps malformed")
    need(session["selected_at_unix"] <= value["dispatched_at_unix"] <= value["completed_at_unix"] <= time.time() + 5, "review predates actual selection or has future completion")
    text = value["review_utf8"]
    need(isinstance(text, str) and 20 <= len(text.encode()) <= 256 * 1024 and sha(text.encode()) == value["review_sha256"], "actual review bytes/hash differ")


def validate_return(args):
    out = args.output.resolve()
    session = read(out / "SESSION.json")
    value = read(out / "RECEIVED_RETURN.json")
    validate_return_value(value, session)
    raw = (out / "RECEIVED_RETURN.json").read_bytes()
    with (out / "INDEPENDENT_RETURN.json").open("xb") as stream:
        stream.write(raw)
    print("INDEPENDENT_RETURN_RECEIVED; external provenance still requires Root receiving")


def receive(args):
    out = args.output.resolve()
    session = read(out / "SESSION.json")
    request = read(Path(session["request_path"]))
    need(session["stage"] == "WAITING_ACTUAL_REVIEW", "independent return stage differs")
    current_check(session, request, out)
    head, raw, value = wait_mail(session, out, RETURN_PATH)
    (out / "RECEIVED_RETURN.json").write_bytes(raw)
    run(out, "validate-independent-return", ["/usr/bin/python3", "-I", "-S", "-B", Path(__file__).resolve(), "validate-return", "--output", out], Path(session["task"]))
    current_check(session, request, out)
    session["last_mail_commit"], session["return_sha256"] = head, sha(raw)
    session["stage"] = "WAITING_ROOT_CONSUMPTION"
    store_session(out, session)
    save(out / "RETURN_RECEIPT.json", dict(schema="dg16.m4-return-receipt.v1", binding=session["selection_binding"],
        return_commit=head, return_sha256=sha(raw), expected_decision_parent=head, expected_decision_path=DECISION_PATH,
        decision_before="DG17_RECEIVING_PENDING", source_role="data-only receiving, no acceptance"))
    print("ACTUAL_RETURN_AVAILABLE_FOR_SEPARATE_ROOT_CONSUMPTION")


def validate_decision(value, session):
    need(set(value) == {"schema", "binding", "return_commit", "return_sha256", "decision_before", "decision_after", "reason", "Root_receiving_evidence", "next_action", "G132", "whole_JOIN"}, "Root decision fields differ")
    need(value["schema"] == "dg16.m4-Root-consumption.v1" and value["binding"] == session["selection_binding"], "Root consumption selection differs")
    need(value["return_commit"] == session["last_mail_commit"] and value["return_sha256"] == session["return_sha256"], "Root consumes different return")
    need(value["decision_before"] == "DG17_RECEIVING_PENDING" and value["decision_after"] in {"DG17_SCOPED_PREDICATES_ACCEPTED", "DG17_CORRECTION_REQUIRED", "DG17_EVIDENCE_INSUFFICIENT"}, "Root decision is not a scoped change from pending")
    need(value["G132"] == "UNKNOWN_NO_REPLAY" and value["whole_JOIN"] == "BLOCKED", "Root decision unblocks protected effect/whole JOIN")
    for key in ("reason", "Root_receiving_evidence", "next_action"):
        need(isinstance(value[key], str) and 8 <= len(value[key]) <= 8192, "Root consumption evidence missing")


def native_check(args):
    out = args.output.resolve()
    session = read(out / "SESSION.json")
    graph, transition, closure = acquire(session)
    need(graph == read(out / "GRAPH.json") and transition == read(out / "TRANSITION.json"), "native graph/currentness/input changed since selection")
    value = read(out / "ROOT_DECISION.json")
    validate_decision(value, session)
    validate_return_value(read(out / "INDEPENDENT_RETURN.json"), session)
    captures = list((out / "commands").glob("*-validate-independent-return.json"))
    need(len(captures) == 1, "actual receiving process capture absent or repeated")
    capture = read(captures[0])
    need(capture["exit_code"] == 0 and capture["process_cleanup"] == "owned-process-group-absent" and not capture["timed_out"], "actual receiving process failed or is uncertain")
    binding = session["selection_binding"]
    output_digest = sha((out / "INDEPENDENT_RETURN.json").read_bytes())
    need(output_digest == session["return_sha256"], "validated return bytes changed")
    execution = {key: binding[key] for key in ("node", "dispatch_id", "graph_digest", "input_digest", "input_root_identity", "read_set")}
    execution.update(output_digest=output_digest, exit_code=capture["exit_code"])
    module = owner(session)
    consumption = {key: binding[key] for key in ("node", "consumer", "condition", "input_digest", "input_root_identity")}
    consumption.update(read_set_digest=module._graph_hash(execution["read_set"]), output_digest=output_digest,
        decision_before=value["decision_before"], decision_after=value["decision_after"])
    report = module.check_recursive_execution_v1(graph, [], transition, [execution], [consumption])
    save(out / "EXECUTIONS.json", [execution])
    save(out / "CONSUMPTIONS.json", [consumption])
    save(out / "RECURSIVE_EXECUTION.json", report)
    save(out / "FINAL_NATIVE_CLOSURE.json", closure)
    save(out / "EVIDENCE_SCOPE.json", dict(actual_native_selection=True, actual_receiving_process=captures[0].name,
        model_dispatch_and_return="External actual collaboration evidence; not attested by the pure checker or host exit code",
        Root_consumption="Separate actual Root mailbox decision; author grants no acceptance",
        native_campaign_proven=False, G132="UNKNOWN_NO_REPLAY", whole_JOIN="BLOCKED", authority="NONE"))
    print("ACTUAL_NATIVE_SELECTION_AND_PORTABLE_RECORDS_CONSUMED; original acceptance remains independent")


def finish(args):
    out = args.output.resolve()
    session = read(out / "SESSION.json")
    request = read(Path(session["request_path"]))
    need(session["stage"] == "WAITING_ROOT_CONSUMPTION", "Root consumption stage differs")
    current_check(session, request, out)
    head, raw, value = wait_mail(session, out, DECISION_PATH)
    (out / "ROOT_DECISION.json").write_bytes(raw)
    validate_decision(value, session)
    run(out, "native-check", ["/usr/bin/python3", "-I", "-S", "-B", Path(__file__).resolve(), "native-check", "--output", out], Path(session["task"]), timeout=600)
    current_check(session, request, out)
    state = Path(session["run_root"]) / "STATE.md"
    text = state.read_text().replace("| Pending decision | DG17_RECEIVING_PENDING |", "| Pending decision | " + value["decision_after"] + " |")
    text += "\n## Actual accepted-result custody at bounded scope\n\nRoot consumption commit: " + head + "\nReturn SHA256: " + session["return_sha256"] + "\nDecision SHA256: " + sha(raw) + "\nThe separate Root decision has been received. This is custody of the exact record, not a self-issued qualification or whole JOIN acceptance. G132 remains UNKNOWN_NO_REPLAY.\n"
    state.write_text(text)
    refresh(session, out, "manual-resume", "actual Root consumption recorded after source-bound checker return")
    current_check(session, request, out)
    session["last_mail_commit"] = head
    session["stage"] = "ROOT_CONSUMPTION_RECORDED"
    store_session(out, session)
    snapshot(session, request, out, "consumed")
    print("ROOT_CONSUMPTION_RECORDED; protected effect and ancestor whole JOIN remain blocked")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["prepare", "receive", "finish", "finalize", "native-select", "validate-return", "native-check"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    args = parser.parse_args()
    try:
        globals()[args.operation.replace("-", "_")](args)
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
