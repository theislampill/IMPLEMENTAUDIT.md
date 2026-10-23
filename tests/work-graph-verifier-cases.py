"""Verifier graph/transport controls; optional --retain-fixtures preserves evidence."""
import argparse
import copy
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("work_graph", ROOT / "skills/implementaudit/scripts/compile-work-graph.py")
wg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wg)
RETAIN = None


def run_command(command, **kwargs):
    """Retain the real tiny-fixture command, source objects, streams and exit."""
    source_root = kwargs.pop("source_root", None)
    if RETAIN is None:
        return subprocess.run(command, **kwargs)
    directory = RETAIN / "commands" / ("%04d" % len(list((RETAIN / "commands").iterdir())))
    directory.mkdir()
    environment = kwargs.get("env", os.environ)
    safe = ("PATH", "LANG", "LC_ALL", "TZ", "PYTHONDONTWRITEBYTECODE", "GITHUB_BASE_REF", "GITHUB_ACTIONS")
    record = dict(argv=[str(x) for x in command], cwd=str(kwargs.get("cwd", Path.cwd())),
                  selected_environment={k: environment.get(k) for k in safe},
                  environment_sha256=hashlib.sha256(b"\0".join(
                      os.fsencode(k) + b"=" + os.fsencode(v) for k, v in sorted(environment.items()))).hexdigest())
    candidate = Path(record["cwd"] if source_root is None else source_root)
    record["observed_source_root"] = str(candidate)
    objects = {}
    if ((candidate / "tests/sample.test.sh").is_file() or
            (candidate / "tests/reproducible-release-asset.test.sh").is_file()):
        for parent, dirs, names in os.walk(candidate, followlinks=False):
            dirs[:] = [d for d in dirs if d != ".git" and not (Path(parent) / d).is_symlink()]
            for name in names:
                path = Path(parent) / name
                if path.is_symlink() or not path.is_file():
                    continue
                data = path.read_bytes()
                digest = hashlib.sha256(data).hexdigest()
                obj = RETAIN / "objects" / digest
                if not obj.exists():
                    obj.write_bytes(data)
                objects[path.relative_to(candidate).as_posix()] = dict(
                    sha256=digest, mode=path.stat().st_mode & 0o7777, bytes=len(data))
    record["source_objects"] = objects
    if "input" in kwargs:
        (directory / "stdin.bin").write_bytes(kwargs["input"])
    (directory / "command.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    options = dict(kwargs)
    check = options.pop("check", False)
    options.setdefault("capture_output", True)
    try:
        result = subprocess.run(command, **options)
    except (OSError, subprocess.TimeoutExpired) as exc:
        (directory / "observer-error.json").write_text(json.dumps(
            dict(type=type(exc).__name__, exit="UNOBSERVED"), sort_keys=True) + "\n")
        raise
    (directory / "stdout.log").write_bytes(result.stdout or b"")
    (directory / "stderr.log").write_bytes(result.stderr or b"")
    (directory / "exit-code.txt").write_text(str(result.returncode) + "\n")
    if check:
        result.check_returncode()
    return result


@contextmanager
def fixture_directory():
    if RETAIN is None:
        with tempfile.TemporaryDirectory(prefix="r0035-verifier-") as directory:
            yield directory
    else:
        directory = RETAIN / "fixture"
        directory.mkdir()
        yield str(directory)


def capture(root, output, mode="dag", environment=None):
    options = dict(cwd=root, capture_output=True)
    if environment is not None:
        options["env"] = environment
    process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                           mode, str(output)], **options)
    return process, json.loads((output / "result.json").read_bytes())


def portal_capture_cases(directory):
    """Actual registered portal test, including its temporary copied sources.

    This is a finite registry, not a full-canonical equivalence run. Losing an
    earlier generation, accepting a mutated checker input, or flattening an
    expected checker failure must fail the actual retained-record consumer.
    """
    root = directory / "portal-root"
    root.mkdir()
    for raw in subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0"):
        if not raw:
            continue
        name = os.fsdecode(raw)
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    # The new repo-only helper can be untracked while this RED is developed.
    helper = ROOT / "scripts/portal-event-capture.py"
    if helper.exists():
        shutil.copy2(helper, root / "scripts" / helper.name)
    (root / "scripts/generate-readme-diagrams.sh").write_text("#!/bin/bash\nexit 0\n")
    (root / "scripts/verify-package.sh").write_text(
        "#!/bin/bash\nset -euo pipefail\n"
        "bash scripts/generate-readme-diagrams.sh --check\n"
        "bash tests/docs-portal.test.sh\n"
        "git diff --check\nprintf 'verify-package: ok\\n'\n")
    for argv in (["git", "init", "-q"], ["git", "add", "."],
                 ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                  "-c", "commit.gpgsign=false", "commit", "-qm", "finite actual portal invocation fixture"]):
        run_command(argv, cwd=root, check=True)
    output = directory / "portal-capture"
    environment = dict(os.environ)
    environment.pop("IMPLEMENTAUDIT_PORTAL_CAPTURE", None)
    process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                           "dag", str(output), "--capture-portal-events"], cwd=root,
                          capture_output=True, env=environment)
    assert process.returncode == 0, ("portal capture", process.stdout, process.stderr)
    record = json.loads((output / "result.json").read_bytes())
    assert record["schema"] == "implementaudit.verifier-run.v4"
    portal = record["portal_events"]
    assert portal["complete"] and portal["coverage"] == "FINITE_PORTAL_INVOCATIONS_COMPLETE"
    assert len(portal["events"]) == 49
    events = [json.loads((output / "portal-events" / name / "event.json").read_bytes())
              for name in portal["events"]]
    assert sum(e["operation"] == "BUILD" for e in events) == 17
    assert sum(e["operation"] == "CHECK" and e["exit"] == 1 for e in events) == 25
    assert all(e["status"] == ("SUCCESS" if e["exit"] == 0 else "FAILURE") for e in events)
    repeated = [e for e in events if e["operation"] == "BUILD" and e["exit"] == 0
                and e["invocation"]["artifact_path"].endswith("/portal-custody")]
    assert len(repeated) == 2 and repeated[0]["generation"] != repeated[1]["generation"]
    assert repeated[0]["artifact"] != repeated[1]["artifact"]
    assert not Path(repeated[0]["invocation"]["artifact_path"]).exists()
    # The first producer's original result remains the same evidence through
    # all three altered consumer inputs; no producer is rerun between them.
    first_producer_result = {key: events[40][key] for key in ("stdout", "stderr", "exit")}
    assert first_producer_result["exit"] == 0
    checked = observer_probe(root, "q.verified_record(Path(sys.argv[2]))", output)
    assert checked.returncode == 0, (checked.stdout, checked.stderr)
    assert events[41]["consumed_generation"] == events[40]["generation"]
    assert events[46]["consumed_generation"] == events[45]["generation"]
    assert all(events[i]["consumed_generation"] is None for i in (42, 43, 44))
    assert [events[i]["exit"] for i in range(40, 47)] == [0, 0, 1, 1, 0, 0, 0]
    assert events[44]["artifact"] != events[40]["artifact"]
    assert events[39]["artifact"] is None  # Unsafe --out . never snapshots the repository.
    assert all(e["artifact"] is None for e in events if e["operation"] == "BUILD" and e["exit"] != 0)

    controls = []
    def refused(label):
        actual = observer_probe(root, "q.verified_record(Path(sys.argv[2]))", output)
        assert actual.returncode == 2, (label, actual.stdout, actual.stderr)
        controls.append(dict(control=label, exit=actual.returncode, diagnostic=actual.stderr.decode()))

    @contextmanager
    def changed_file(path, data):
        before = path.read_bytes()
        path.write_bytes(data)
        try:
            yield
        finally:
            path.write_bytes(before)

    event_root = output / "portal-events"
    first_event = event_root / "event-0000"
    artifact = first_event / "artifact"
    page = artifact / "index.html"
    for label, relative in (("missing generation metadata", "docs-metadata.json"),
                            ("missing original generated page", "index.html")):
        original = artifact / relative
        backup = directory / "held-portal-member"
        original.rename(backup)
        try:
            refused(label)
        finally:
            backup.rename(original)
    with changed_file(page, page.read_bytes() + b"\n<!-- retained bytes corrupted -->\n"):
        refused("corrupt artifact despite structural comment acceptance")
    extra = artifact / "foreign.txt"
    extra.write_text("not part of this generation\n")
    try:
        refused("extra artifact member")
    finally:
        extra.unlink()
    mode = page.stat().st_mode & 0o7777
    page.chmod(mode ^ 0o100)
    try:
        refused("changed artifact mode")
    finally:
        page.chmod(mode)
    backup = directory / "held-portal-member"
    page.rename(backup)
    for kind in ("symlink", "fifo"):
        if kind == "symlink":
            page.symlink_to(backup)
        else:
            os.mkfifo(page)
        try:
            refused("unsupported artifact " + kind)
        finally:
            page.unlink()
    backup.rename(page)
    last = event_root / "event-0048"
    backup = directory / "held-portal-event"
    last.rename(backup)
    try:
        refused("missing final actual checker event")
        # Resealing the declared surviving set still cannot omit a required slot.
        modified = copy.deepcopy(record)
        modified["portal_events"]["events"].pop("event-0048")
        returned = json.loads((event_root / "node-return.json").read_bytes())
        returned["events"].pop()
        with changed_file(output / "result.json", json.dumps(modified).encode()):
            with changed_file(event_root / "node-return.json", json.dumps(returned).encode()):
                refused("omitted required event in resealed declared population")
    finally:
        backup.rename(last)
    duplicate = event_root / "event-0049"
    shutil.copytree(first_event, duplicate)
    try:
        refused("duplicate extra portal event")
    finally:
        shutil.rmtree(duplicate)
    first_event.rename(backup)
    (event_root / "event-0001").rename(first_event)
    backup.rename(event_root / "event-0001")
    try:
        refused("reordered portal events")
    finally:
        first_event.rename(backup)
        (event_root / "event-0001").rename(first_event)
        backup.rename(event_root / "event-0001")
    for label, mutate in (
        ("false successful checker status", lambda e: e.update(status="SUCCESS")),
        ("foreign run binding", lambda e: e["invocation"].update(run_id="0" * 32)),
        ("foreign source root", lambda e: e["invocation"].update(source_root="/foreign")),
        ("false generation link", lambda e: e.update(consumed_generation=events[40]["generation"])),
        ("changed checker input window", lambda e: e["after_stamps"].pop("index.html")),
    ):
        path = event_root / "event-0042/event.json"
        altered = json.loads(path.read_bytes())
        mutate(altered)
        with changed_file(path, json.dumps(altered).encode()):
            refused(label)
    with changed_file(first_event / "stdout.log", b"manufactured producer output\n"):
        refused("changed original raw producer result")
    with changed_file(first_event / "exit-code.txt", b"7\n"):
        refused("changed durable actual producer exit")
    with changed_file(event_root / "loaded/build-docs-portal.py", b"stale producer\n"):
        refused("stale retained producer source")
    for name in ("node.json", "fixture.json", "nested.json", "node-return.json"):
        path = event_root / name
        altered = json.loads(path.read_bytes())
        altered["foreign_field"] = "not part of the observed lifecycle"
        with changed_file(path, json.dumps(altered).encode()):
            refused("foreign lifecycle record field: " + name)
    with changed_file(event_root / "lock", b"foreign lock bytes\n"):
        refused("foreign retained lock bytes")
    result_path = output / "result.json"
    altered = copy.deepcopy(record)
    altered["portal_events"]["request"]["source_root"] = "/foreign"
    with changed_file(result_path, json.dumps(altered).encode()):
        refused("foreign qualifier source context")
    # Both genuine earlier same-path generations must remain independently bound.
    left = event_root / "event-0002/artifact"
    right = event_root / "event-0003/artifact"
    left.rename(backup)
    right.rename(left)
    backup.rename(right)
    try:
        refused("swapped earlier generation at the same path")
    finally:
        left.rename(backup)
        right.rename(left)
        backup.rename(right)
    (directory / "portal-integrity-controls.json").write_text(json.dumps(controls, indent=2) + "\n")
    checked = observer_probe(root, "q.verified_record(Path(sys.argv[2]))", output)
    assert checked.returncode == 0, ("restored complete capture", checked.stderr)

    # With capture disabled, the actual registered test preserves its raw result.
    off = directory / "portal-capture-off"
    process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "dag", str(off)],
                          cwd=root, capture_output=True, env=environment)
    assert process.returncode == 0, (process.stdout, process.stderr)
    assert json.loads((off / "result.json").read_bytes())["schema"] == "implementaudit.verifier-run.v2"
    assert not (off / "portal-events").exists()
    for name in ("stdout.log", "stderr.log", "exit-code.txt"):
        assert (off / name).read_bytes() == (output / name).read_bytes(), ("capture-off raw compatibility", name)

    # Real concurrent input mutation, scheduled at the actual child's runtime
    # observation. An inert comment keeps the checker oracle successful, while
    # the original input custody must refuse the changed consumption window.
    drift = directory / "portal-input-drift"
    outcome = []
    def mutate_live_input():
        event = drift / "portal-events/event-0001"
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if (event / "runtime.json").exists():
                inv = json.loads((event / "invocation.json").read_bytes())
                target = Path(inv["artifact_path"]) / "index.html"
                with target.open("ab") as stream:
                    stream.write(b"\n<!-- mutation during actual checker consumption -->\n")
                outcome.append("mutated")
                return
            time.sleep(0.001)
        outcome.append("not observed")
    worker = threading.Thread(target=mutate_live_input)
    worker.start()
    process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "dag", str(drift),
                           "--capture-portal-events"], cwd=root, capture_output=True, env=environment)
    worker.join()
    assert outcome == ["mutated"] and process.returncode == 2, (outcome, process.stdout, process.stderr)
    event = drift / "portal-events/event-0001"
    actual = json.loads((event / "event.json").read_bytes())
    assert actual["capture_status"] == "CHECKER_INPUT_DRIFT" and actual["exit"] == 0
    assert (event / "exit-code.txt").read_bytes() == b"0\n"
    assert b"check-docs-portal: ok" in (event / "stdout.log").read_bytes()
    assert not (drift / "result.json").exists()

    # Unsupported source and inherited capture requests refuse before dispatch.
    producer = root / "scripts/build-docs-portal.py"
    with changed_file(producer, producer.read_bytes() + b"\n# unreviewed source successor\n"):
        bad = directory / "portal-stale-producer"
        process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "dag", str(bad),
                               "--capture-portal-events"], cwd=root, capture_output=True, env=environment)
        assert process.returncode == 2 and not (bad / "exit-code.txt").exists()
        assert b"unsupported portal source contract" in process.stderr
    bad = directory / "portal-ambiguous-request"
    process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "dag", str(bad),
                           "--capture-portal-events"], cwd=root, capture_output=True,
                          env=dict(environment, IMPLEMENTAUDIT_PORTAL_CAPTURE=""))
    assert process.returncode == 2 and b"ambiguous inherited" in process.stderr

    oversized = directory / "portal-oversized-artifact"
    oversized.mkdir()
    with (oversized / "oversized.bin").open("wb") as stream:
        stream.truncate(16 * 1024 * 1024 + 1)
    process = observer_probe(root, "try:\n    q.portal_engine().tree(Path(sys.argv[2]))\nexcept ValueError as exc:\n    raise q.WG.WorkGraphError(str(exc))", oversized)
    assert process.returncode == 2 and b"byte limit" in process.stderr


def compare_capture(root, left, right, output):
    return run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "compare",
                        str(left), str(right), str(output)], cwd=root, capture_output=True)


def extended_capture_cases(directory):
    """Actual v3 input/output observation; early fixtures never run a builder.

    Removing a retained material file must make the real record consumer
    refuse while the original process streams and durable exit stay intact.
    The incomplete canary is written before the pinned producer, then exit 7
    prevents that producer from running. It is never a successful release.
    """
    root = directory / "extended-root"
    for name in ("scripts/qualify-work-graph-verifier.py", "scripts/run-work-graph-verifier.sh",
                 "skills/implementaudit/scripts/compile-work-graph.py",
                 "tests/reproducible-release-asset.test.sh"):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    (root / "scripts/generate-readme-diagrams.sh").write_text("#!/bin/bash\nexit 0\n")
    (root / "tests/sample.test.sh").write_text("#!/bin/bash\ncat\n")
    registry_path = root / "scripts/verify-package.sh"
    prelude = '#!/usr/bin/env bash\nset -euo pipefail\n'
    end = "git diff --check\n\nprintf 'verify-package: ok\\n'\n"
    producer_tail = ('bash scripts/generate-readme-diagrams.sh --check\n'
                     'bash tests/reproducible-release-asset.test.sh\n' + end)
    registry = (prelude + 'printf "partial fixture\\n"\n'
                'if [ -n "${REPRO_RETAINED_ASSET_A:-}" ]; then\n'
                '  printf "incomplete observer canary\\n" > "$REPRO_RETAINED_ASSET_A"\n'
                'fi\nexit 7\n' + producer_tail)
    registry_path.write_text(registry)
    run_command(["git", "init", "-q", str(root)], check=True)
    run_command(["git", "add", "."], cwd=root, check=True)
    run_command(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "constructed extended capture"], cwd=root, check=True)

    def observed(output, mode, flags, expected, environment=None):
        process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                               mode, str(output), *flags], cwd=root, capture_output=True,
                              **({"env": environment} if environment is not None else {}))
        assert process.returncode == expected, ("extended capture outcome", process.stdout, process.stderr)
        record = json.loads((output / "result.json").read_bytes())
        assert record["exit"] == expected
        return record

    default = observed(directory / "extended-default-v2", "legacy", [], 7)
    assert default["schema"] == "implementaudit.verifier-run.v2"
    original_output = directory / "repro-original-capture"
    record = observed(original_output, "legacy", ["--retain-repro-assets"], 7)
    assert record["schema"] == "implementaudit.verifier-run.v3"
    artifact = record["repro_artifacts"]
    assert not artifact["complete"] and artifact["coverage"] == "UNQUALIFIED_INCOMPLETE_OR_FAILED_PROCESS"
    assert len(artifact["files"]) == 6
    assert artifact["files"]["ASSET_A"]["observation"]["kind"] == "FILE"
    assert all(v["observation"]["kind"] == "MISSING" for k, v in artifact["files"].items() if k != "ASSET_A")
    assert record["stdin"] is None
    original_env = record["child_environment"]
    assert original_env["actual_environment_sha256"] == record["environment"]["inherited_environment_sha256"]
    assert len(original_env["overrides"]) == 6
    legacy = directory / "repro-restored-legacy"
    original_output.rename(legacy)
    dag_record = observed(original_output, "dag", ["--retain-repro-assets"], 7)
    assert all(n["status"] == "UNSETTLED" for n in dag_record["nodes"][1:])
    compared = directory / "repro-partial-comparison.json"
    process = compare_capture(root, legacy, original_output, compared)
    assert process.returncode == 0, (process.stdout, process.stderr)
    comparison = json.loads(compared.read_bytes())
    assert comparison["checks"]["same_declared_repro_artifacts"]
    assert comparison["checks"]["same_child_environment"]
    assert comparison["repro_artifact_coverage"] == ["UNQUALIFIED_INCOMPLETE_OR_FAILED_PROCESS"] * 2

    for name in ("missing", "changed", "mode", "role", "producer", "source-commit", "environment",
                 "environment-file", "environment-path", "command", "downgrade"):
        bad = directory / ("bad-repro-" + name)
        shutil.copytree(original_output, bad)
        changed = json.loads((bad / "result.json").read_bytes())
        member = bad / changed["repro_artifacts"]["files"]["ASSET_A"]["relative_path"]
        if name == "missing":
            member.unlink()
        elif name == "changed":
            member.write_bytes(b"different material output\n")
        elif name == "mode":
            member.chmod((member.stat().st_mode & 0o7777) ^ 0o020)
        elif name == "role":
            files = changed["repro_artifacts"]["files"]
            files["ASSET_A"], files["ASSET_B"] = files["ASSET_B"], files["ASSET_A"]
        elif name == "producer":
            changed["repro_artifacts"]["producer"]["sha256"] = "0" * 64
        elif name == "source-commit":
            changed["repro_artifacts"]["producer"]["source_commit"] = "0" * 40
        elif name == "environment":
            changed["child_environment"]["actual_environment_sha256"] = "0" * 64
        elif name == "environment-file":
            (bad / "child-environment.json").unlink()
        elif name == "environment-path":
            changed["child_environment"]["overrides"]["REPRO_RETAINED_ASSET_A"] += ".foreign"
        elif name == "command":
            changed["actual_argv"].append("--foreign")
        else:
            changed["schema"] = "implementaudit.verifier-run.v2"
        (bad / "result.json").write_text(json.dumps(changed) + "\n")
        checked = compare_capture(root, legacy, bad, directory / ("repro-refusal-" + name + ".json"))
        assert checked.returncode == 2, (name, checked.stdout, checked.stderr)
        assert (bad / "exit-code.txt").read_bytes() == b"7\n"

    keys = ["REPRO_RETAINED_" + name for name in artifact["files"]] + ["REPRO_SOURCE_REF"]
    for index, key in enumerate(keys):
        output = directory / ("repro-override-" + str(index))
        process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                               "legacy", str(output), "--retain-repro-assets"], cwd=root, capture_output=True,
                              env=dict(os.environ, **{key: ""}))
        assert process.returncode == 2 and b"override" in process.stderr
        assert not (output / "exit-code.txt").exists()
    producer = root / "tests/reproducible-release-asset.test.sh"
    producer_bytes = producer.read_bytes()
    for name in ("producer", "arguments"):
        output = directory / ("repro-preflight-" + name)
        if name == "producer":
            producer.write_bytes(producer_bytes + b"\n# changed producer\n")
        else:
            registry_path.write_text(registry.replace('bash tests/reproducible-release-asset.test.sh\n',
                                                     'bash tests/reproducible-release-asset.test.sh --foreign\n'))
        try:
            process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                                   "legacy", str(output), "--retain-repro-assets"], cwd=root, capture_output=True)
            assert process.returncode == 2 and b"repro" in process.stderr
            assert not (output / "exit-code.txt").exists()
        finally:
            producer.write_bytes(producer_bytes)
            registry_path.write_text(registry)

    # A real Bash script receives the exact retained bytes through the runner.
    registry_path.write_text(prelude + 'bash scripts/generate-readme-diagrams.sh --check\n'
                             'bash tests/sample.test.sh\n' + end)
    payload = b"retained stdin\nNUL=\0 and final bytes\n"
    input_file = directory / "explicit-input.bin"
    input_file.write_bytes(payload)
    stdin_output = directory / "stdin-original-capture"
    file_record = observed(stdin_output, "legacy", ["--stdin-file", str(input_file)], 0)
    assert file_record["repro_artifacts"] is None
    assert (stdin_output / "stdin.bin").read_bytes() == payload
    assert (stdin_output / "stdout.log").read_bytes() == payload + b"verify-package: ok\n"
    stdin_legacy = directory / "stdin-restored-legacy"
    stdin_output.rename(stdin_legacy)
    observed(stdin_output, "dag", ["--stdin-file", str(input_file)], 0)
    process = compare_capture(root, stdin_legacy, stdin_output, directory / "stdin-comparison.json")
    assert process.returncode == 0, (process.stdout, process.stderr)
    for name in ("missing", "changed", "symlink", "declaration", "size-bool"):
        bad = directory / ("bad-stdin-" + name)
        shutil.copytree(stdin_output, bad)
        changed = json.loads((bad / "result.json").read_bytes())
        if name == "missing":
            (bad / "stdin.bin").unlink()
        elif name == "changed":
            (bad / "stdin.bin").write_bytes(b"changed retained input\n")
        elif name == "symlink":
            (bad / "stdin.bin").unlink()
            (bad / "stdin.bin").symlink_to(input_file)
        elif name == "declaration":
            changed["stdin"]["declared_path"] += ".foreign"
        else:
            changed["stdin"]["bytes"] = True
        (bad / "result.json").write_text(json.dumps(changed) + "\n")
        process = compare_capture(root, stdin_legacy, bad, directory / ("stdin-refusal-" + name + ".json"))
        assert process.returncode == 2, (name, process.stdout, process.stderr)
    empty_output = directory / "empty-stdin"
    empty = observed(empty_output, "dag", ["--empty-stdin"], 0)
    assert empty["stdin"]["mode"] == "EMPTY_PIPE" and (empty_output / "stdin.bin").read_bytes() == b""
    assert (empty_output / "stdout.log").read_bytes() == b"verify-package: ok\n"
    dist_capture_cases(root, directory)
    extended_boundary_cases(root, directory)
    dist_existing_consumer_cases(directory)
    print("work-graph-verifier: explicit v3 partial artifacts, child environment and retained stdin consumed")


def dist_capture_cases(root, directory):
    """A complete finite ignored namespace must affect the real consumer."""
    (root / ".gitignore").write_text("dist/\n")
    source_dist = root / "dist"
    source_dist.mkdir()
    (source_dist / "nested").mkdir()
    (source_dist / "probe.txt").write_bytes(b"current material\n")
    (source_dist / "nested/member.bin").write_bytes(b"nested\0bytes\n")
    original_output = directory / "dist-original-capture"

    def observe(mode, output):
        process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                               mode, str(output), "--capture-dist", "--empty-stdin"],
                              cwd=root, capture_output=True)
        assert process.returncode == 0, ("dist capture outcome", process.stdout, process.stderr)
        return json.loads((output / "result.json").read_bytes())

    record = observe("legacy", original_output)
    namespace = record["dist_namespace"]
    assert namespace["before"] == namespace["after"]
    assert set(namespace["before"]["entries"]) == {"dist", "dist/probe.txt", "dist/nested", "dist/nested/member.bin"}
    assert (original_output / "dist-before/dist/probe.txt").read_bytes() == b"current material\n"
    legacy = directory / "dist-restored-legacy"
    original_output.rename(legacy)
    observe("dag", original_output)
    compared = directory / "dist-comparison.json"
    process = compare_capture(root, legacy, original_output, compared)
    assert process.returncode == 0, (process.stdout, process.stderr)
    assert json.loads(compared.read_bytes())["checks"]["same_dist_namespace"]
    foreign = compare_capture(ROOT, legacy, original_output, directory / "dist-foreign-context.json")
    assert foreign.returncode == 2 and b"current source context" in foreign.stderr, (foreign.stdout, foreign.stderr)
    for name in ("missing", "added", "changed", "mode", "directory-mode", "type", "symlink",
                 "fifo", "foreign-root", "inventory", "sidecar", "scope"):
        bad = directory / ("bad-dist-" + name)
        shutil.copytree(original_output, bad)
        result = json.loads((bad / "result.json").read_bytes())
        member = bad / "dist-before/dist/probe.txt"
        if name == "missing":
            member.unlink()
        elif name == "added":
            (member.parent / "extra.txt").write_bytes(b"extra material\n")
        elif name == "changed":
            member.write_bytes(b"changed material\n")
        elif name == "mode":
            member.chmod((member.stat().st_mode & 0o7777) ^ 0o020)
        elif name == "directory-mode":
            member.parent.chmod((member.parent.stat().st_mode & 0o7777) ^ 0o020)
        elif name in {"type", "symlink", "fifo"}:
            member.unlink()
            if name == "type":
                member.mkdir()
            elif name == "symlink":
                member.symlink_to(source_dist / "probe.txt")
            else:
                os.mkfifo(member)
        elif name == "foreign-root":
            (bad / "dist-before/foreign").write_bytes(b"outside snapshot population\n")
        elif name == "inventory":
            result["dist_namespace"]["before"]["entries"].pop("dist/probe.txt")
        elif name == "sidecar":
            (bad / "dist-namespace.json").unlink()
        else:
            result["dist_namespace"]["source_path"] += ".foreign"
        (bad / "result.json").write_text(json.dumps(result) + "\n")
        process = compare_capture(root, legacy, bad, directory / ("dist-refusal-" + name + ".json"))
        assert process.returncode == 2, (name, process.stdout, process.stderr)
        assert (bad / "exit-code.txt").read_bytes() == b"0\n"
    # An ignored source change has identical shell streams/exit but a different
    # current namespace. Do not normalize its inventory out of correspondence.
    (source_dist / "probe.txt").write_bytes(b"different source material\n")
    changed_output = directory / "dist-source-changed"
    observe("dag", changed_output)
    process = compare_capture(root, legacy, changed_output, directory / "dist-source-comparison.json")
    assert process.returncode == 2 and b"current dist" in process.stderr
    assert (legacy / "stdout.log").read_bytes() == (changed_output / "stdout.log").read_bytes()
    assert (legacy / "exit-code.txt").read_bytes() == (changed_output / "exit-code.txt").read_bytes()
    source_dist.rename(directory / "original-dist-source")
    missing = observe("dag", directory / "dist-source-missing")
    assert missing["dist_namespace"]["before"]["entries"] == {"dist": {"kind": "MISSING"}}
    for name in ("dangling-link", "fifo", "file", "oversized"):
        if name == "dangling-link":
            source_dist.symlink_to(directory / "absent-dist")
        elif name == "fifo":
            os.mkfifo(source_dist)
        elif name == "file":
            source_dist.write_bytes(b"not a directory\n")
        else:
            source_dist.mkdir()
            with (source_dist / "large.bin").open("wb") as stream:
                stream.truncate(16 * 1024 * 1024 + 1)
        process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                               "dag", str(directory / ("dist-source-refusal-" + name)), "--capture-dist"],
                              cwd=root, capture_output=True, timeout=10)
        assert process.returncode == 2 and b"dist" in process.stderr
        if name == "oversized":
            source_dist.rename(directory / "oversized-dist-input")
        else:
            source_dist.unlink()


def extended_boundary_cases(root, directory):
    """Actual input delivery, explicit bounds and child-cwd resolution."""
    registry = root / "scripts/verify-package.sh"
    original = registry.read_text()
    qualifier = [sys.executable, "-B", "scripts/qualify-work-graph-verifier.py"]
    # Missing exports cannot turn a zero process exit into artifact coverage.
    registry.write_text(original.replace("set -euo pipefail\n", "set -euo pipefail\nexit 0\n").replace(
        "bash tests/sample.test.sh", "bash tests/reproducible-release-asset.test.sh"))
    output = directory / "repro-zero-missing"
    process = run_command([*qualifier, "legacy", str(output), "--retain-repro-assets"], cwd=root, capture_output=True)
    assert process.returncode == 2 and (output / "exit-code.txt").read_bytes() == b"0\n"
    assert not json.loads((output / "repro-artifacts.json").read_bytes())["complete"]
    assert not (output / "result.json").exists()
    registry.write_text(original)

    input_path = directory / "replace-after-acquisition.bin"
    payload = b"original pipe bytes\0\n"
    input_path.write_bytes(payload)
    registry.write_text(original.replace("set -euo pipefail\n", "set -euo pipefail\nprintf 'replacement\\n' > " +
                                        shlex.quote(str(input_path)) + "\n"))
    output = directory / "stdin-single-acquisition"
    process = run_command([*qualifier, "dag", str(output), "--stdin-file", str(input_path)], cwd=root, capture_output=True)
    assert process.returncode == 0, (process.stdout, process.stderr)
    assert input_path.read_bytes() == b"replacement\n"
    assert (output / "stdin.bin").read_bytes() == payload
    assert (output / "stdout.log").read_bytes() == payload + b"verify-package: ok\n"
    registry.write_text(original)
    for name in ("symlink", "fifo", "oversized"):
        path = directory / ("stdin-source-" + name)
        if name == "symlink":
            path.symlink_to(input_path)
        elif name == "fifo":
            os.mkfifo(path)
        else:
            with path.open("wb") as stream:
                stream.truncate(16 * 1024 * 1024 + 1)
        output = directory / ("stdin-source-refusal-" + name)
        process = run_command([*qualifier, "legacy", str(output), "--stdin-file", str(path)],
                              cwd=root, capture_output=True, timeout=10)
        assert process.returncode == 2 and not (output / "exit-code.txt").exists()
    process = run_command([*qualifier, "legacy", str(directory / "stdin-conflicting-options"),
                           "--stdin-file", str(input_path), "--empty-stdin"], cwd=root, capture_output=True)
    assert process.returncode == 2

    # The caller is outside ROOT. Actual Bash resolution must nevertheless use
    # the launched cwd for both relative and empty PATH entries. These explicit
    # fixture wrappers invoke a known interpreter; launcher closure is unclaimed.
    sample = root / "tests/sample.test.sh"
    sample_bytes = sample.read_bytes()
    sample.write_bytes(b"#!/bin/bash\npython -c 'print(17)'\ncat\n")
    wrapper = b'#!/bin/sh\nexec /usr/bin/python3 "$@"\n'
    bash_wrapper = (b'#!/bin/sh\nif [ "${1:-}" = "--version" ]; then\n'
                    b"  printf 'constructed bash version\\n'; exit 0\nfi\nexec /bin/bash \"$@\"\n")
    for label, path_entry in (("relative", "fixture-bin"), ("empty", "")):
        bindir = root / path_entry
        bindir.mkdir(exist_ok=True)
        for name in ("python", "python3", "py"):
            (bindir / name).write_bytes(wrapper)
            (bindir / name).chmod(0o755)
        (bindir / "bash").write_bytes(bash_wrapper)
        (bindir / "bash").chmod(0o755)
        environment = dict(os.environ, PATH=path_entry + os.pathsep + os.environ["PATH"])
        output = directory / ("python-resolution-" + label)
        command = [sys.executable, "-B", str(root / "scripts/qualify-work-graph-verifier.py")]
        process = run_command([*command, "legacy", str(output), "--empty-stdin"],
                              cwd=directory, source_root=root, env=environment, capture_output=True)
        assert process.returncode == 0, (process.stdout, process.stderr)
        result = json.loads((output / "result.json").read_bytes())
        for name in ("python", "python3", "py"):
            assert result["environment"]["executables"][name]["resolved_path"] == str(bindir / name)
            assert result["environment"]["executables"][name]["sha256"] == hashlib.sha256(wrapper).hexdigest()
        assert result["environment"]["child_python_resolution"]["launcher_interpreter"] == "UNQUALIFIED"
        assert result["environment"]["bash"] == "constructed bash version"
        assert result["environment"]["executables"]["bash"]["resolved_path"] == str(bindir / "bash")
        assert (output / "stdout.log").read_bytes() == b"17\nverify-package: ok\n"
        (bindir / "python").write_bytes(wrapper + b"# changed selected executable bytes\n")
        changed_output = directory / ("python-resolution-changed-" + label)
        process = run_command([*command, "dag", str(changed_output), "--empty-stdin"],
                              cwd=directory, source_root=root, env=environment, capture_output=True)
        assert process.returncode == 0, (process.stdout, process.stderr)
        compared = directory / ("python-resolution-comparison-" + label + ".json")
        process = compare_capture(root, output, changed_output, compared)
        assert process.returncode == 1
        checks = json.loads(compared.read_bytes())["checks"]
        assert checks["same_stdout"] and not checks["same_environment"]
        for name in ("python", "python3", "py", "bash"):
            (bindir / name).unlink()
    registry.write_text(original)
    sample.write_bytes(sample_bytes)

    # A postprocessing refusal still preserves the actual completed child exit.
    output = directory / "v3-postprocessing-failure"
    program = (
        "import importlib.util, pathlib\n"
        "s=importlib.util.spec_from_file_location('q', 'scripts/qualify-work-graph-verifier.py')\n"
        "q=importlib.util.module_from_spec(s); s.loader.exec_module(q)\n"
        "def refuse(*args): raise q.WG.WorkGraphError('constructed postprocessing refusal')\n"
        "q.verify_extended_record=refuse\n"
        "try: q.run('legacy', pathlib.Path(" + repr(str(output)) + "), empty_stdin=True)\n"
        "except q.WG.WorkGraphError: raise SystemExit(2)\n")
    process = run_command([sys.executable, "-B", "-c", program], cwd=root, capture_output=True)
    assert process.returncode == 2 and (output / "exit-code.txt").read_bytes() == b"0\n"
    assert not (output / "result.json").exists()


def dist_existing_consumer_cases(directory):
    """Exercise existing material predicates without invoking a build."""
    sources = directory / "dist-consumer-sources"
    sources.mkdir()
    binding = {}
    for name in ("scripts/build-release-asset.sh", "scripts/verify-package.sh"):
        data = (ROOT / name).read_bytes()
        shutil.copy2(ROOT / name, sources / Path(name).name)
        binding[name] = dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    (sources / "binding.json").write_text(json.dumps(binding, sort_keys=True, indent=2) + "\n")
    withdrawn = b"constructed withdrawn bytes\n"
    digest = hashlib.sha256(withdrawn).hexdigest()
    for role in ("current", "plugin", "skill"):
        case = directory / ("dist-stale-consumer-" + role)
        (case / "dist").mkdir(parents=True)
        (case / "CHANGELOG.md").write_text("# Constructed history\nsuperseded " + digest + "\n")
        for kind, name in (("plugin", "IMPLEMENTAUDIT.plugin.zip"), ("skill", "IMPLEMENTAUDIT.skill")):
            (case / "dist" / name).write_bytes(withdrawn if kind == role else b"constructed current bytes\n")
        process = run_command(["bash", str(ROOT / "scripts/build-release-asset.sh"), "--check-stale-release-set",
                               "package", str(case / "dist"), str(case / "CHANGELOG.md")], cwd=case, capture_output=True)
        assert process.returncode == (0 if role == "current" else 1), (role, process.stdout, process.stderr)
    # Recover the exact existing first guard's argv. Keeping its patterns in
    # the original registry also avoids turning this fixture into a guard hit.
    lines = (ROOT / "scripts/verify-package.sh").read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("if grep -R -n -I"))
    end = next(i for i in range(start, len(lines)) if lines[i].startswith("  . >"))
    argv = shlex.split(" ".join(line.rstrip("\\").strip() for line in lines[start:end]))[1:] + ["."]
    assert argv[0] == "grep" and argv.count("-e") == 5
    first_pattern = argv[argv.index("-e") + 1]
    for label, data, expected in (("benign", b"benign extra material\n", 1),
                                  ("forbidden", first_pattern.encode() + b"\n", 0)):
        case = directory / ("dist-grep-consumer-" + label)
        (case / "dist").mkdir(parents=True)
        (case / "dist/probe.txt").write_bytes(data)
        process = run_command(argv, cwd=case, capture_output=True)
        assert process.returncode == expected, (label, process.stdout, process.stderr)


def retained_repro_consumer_cases(root, capture, directory):
    """Consume an actual producer capture; never synthesize a route or build."""
    original = json.loads((capture / "result.json").read_bytes())
    assert original["schema"] == "implementaudit.verifier-run.v3" and original["exit"] == 0
    assert original["repro_artifacts"]["complete"] and len(original["repro_artifacts"]["files"]) == 6
    compared = directory / "same-actual-route.json"
    process = compare_capture(root, capture, capture, compared)
    assert process.returncode == 1, (process.stdout, process.stderr)
    checks = json.loads(compared.read_bytes())["checks"]
    assert not checks["route_pair"] and all(v for k, v in checks.items() if k != "route_pair")
    # Independent malformed copies preserve the actual producer's original
    # raw streams/exit. Every one must refuse at the actual evidence consumer.
    for name in ("missing", "bytes", "mode", "role", "producer", "stale", "environment", "command", "population", "sidecar"):
        bad = directory / ("actual-repro-refusal-" + name)
        shutil.copytree(capture, bad)
        record = json.loads((bad / "result.json").read_bytes())
        assets = record["repro_artifacts"]
        member = bad / assets["files"]["ASSET_A"]["relative_path"]
        if name == "missing":
            member.unlink()
        elif name == "bytes":
            member.write_bytes(b"changed actual export\n")
        elif name == "mode":
            member.chmod(0o640)
        elif name == "role":
            assets["files"]["ASSET_A"], assets["files"]["PLUGIN_A"] = assets["files"]["PLUGIN_A"], assets["files"]["ASSET_A"]
        elif name == "producer":
            assets["producer"]["sha256"] = "0" * 64
        elif name == "stale":
            assets["producer"]["source_commit"] = "0" * 40
        elif name == "environment":
            record["child_environment"]["overrides"]["REPRO_RETAINED_ASSET_A"] += ".foreign"
        elif name == "command":
            (bad / "commands.bin").write_bytes(b"changed command stream\0")
        elif name == "population":
            (member.parent / "foreign.txt").write_bytes(b"foreign\n")
        else:
            (bad / "repro-artifacts.json").unlink()
        (bad / "result.json").write_text(json.dumps(record) + "\n")
        process = compare_capture(root, capture, bad, directory / ("actual-repro-" + name + ".json"))
        assert process.returncode == 2, (name, process.stdout, process.stderr)
        assert (bad / "exit-code.txt").read_bytes() == b"0\n"
    changed = directory / "actual-repro-meaningful-output"
    shutil.copytree(capture, changed)
    data = (changed / "stdout.log").read_bytes() + b"different declared outcome\n"
    (changed / "stdout.log").write_bytes(data)
    record = json.loads((changed / "result.json").read_bytes())
    record["stdout_sha256"] = hashlib.sha256(data).hexdigest()
    (changed / "result.json").write_text(json.dumps(record) + "\n")
    compared = directory / "actual-repro-meaningful-output.json"
    process = compare_capture(root, capture, changed, compared)
    assert process.returncode == 1
    assert not json.loads(compared.read_bytes())["checks"]["same_stdout"]


def trace_integrity_cases(root, directory, captures):
    """Removing the original trace must break the actual retained-record consumer."""
    original = (captures[1] / "nodes.tsv").read_bytes()
    original_stream = (captures[1] / "commands.bin").read_bytes()
    events = original.splitlines(keepends=True)
    cases = ("missing", "changed", "digest", "size", "size-bool", "duplicate", "reordered",
             "foreign", "pass-without-start", "duplicate-pass", "unknown-state",
             "unterminated", "empty-success", "status", "terminal-type", "status-type",
             "node-extra", "command", "legacy-command", "schema-type", "mode-type",
             "authority", "top-extra", "downgrade", "stream-missing", "stream-changed",
             "stream-resealed", "actual-argv", "execution-context")
    for index, name in enumerate(cases):
        bad = directory / ("bad-node-evidence-" + name)
        shutil.copytree(captures[1], bad)
        result = json.loads((bad / "result.json").read_bytes())
        if name == "missing":
            (bad / "nodes.tsv").unlink()
        elif name == "changed":
            (bad / "nodes.tsv").write_bytes(original + b"CORRUPTED\n")
        elif name in {"digest", "size", "size-bool"}:
            key, value = {"digest": ("sha256", "0" * 64), "size": ("bytes", len(original) + 1),
                          "size-bool": ("bytes", True)}[name]
            result["node_trace"][key] = value
        elif name in {"duplicate", "reordered", "foreign", "pass-without-start", "duplicate-pass",
                      "unknown-state", "unterminated", "empty-success"}:
            changed = {
                "duplicate": events[0] + original,
                "reordered": b"".join(events[2:4] + events[:2] + events[4:]),
                "foreign": b"FOREIGN\tSTART\n" + original,
                "pass-without-start": b"".join(events[1:]),
                "duplicate-pass": b"".join(events[:2] + events[1:2] + events[2:]),
                "unknown-state": original.replace(b"\tSTART\n", b"\tOTHER\n", 1),
                "unterminated": original[:-1],
                "empty-success": b"",
            }[name]
            (bad / "nodes.tsv").write_bytes(changed)
            # Resealing invalid events must not bypass the semantic parser.
            result["node_trace"] = dict(sha256=hashlib.sha256(changed).hexdigest(), bytes=len(changed))
        elif name == "status":
            result["nodes"][0].update(status="UNSETTLED", terminal=False)
        elif name == "terminal-type":
            result["nodes"][0]["terminal"] = 1
        elif name == "status-type":
            result["nodes"][0]["status"] = True
        elif name == "node-extra":
            result["nodes"][0]["invented"] = "PASS"
        elif name == "command":
            result["command"] = ["bash", "scripts/verify-package.sh"]
        elif name == "legacy-command":
            result["mode"] = "legacy"
        elif name == "schema-type":
            result["schema"] = []
        elif name == "mode-type":
            result["mode"] = {}
        elif name == "authority":
            result["authority"] = "ACCEPT"
        elif name == "top-extra":
            result["invented"] = True
        elif name == "downgrade":
            result["schema"] = "implementaudit.verifier-run.v1"
        elif name == "stream-missing":
            (bad / "commands.bin").unlink()
        elif name in {"stream-changed", "stream-resealed"}:
            changed = original_stream + b"EXTRA"
            (bad / "commands.bin").write_bytes(changed)
            if name == "stream-resealed":
                digest = hashlib.sha256(changed).hexdigest()
                result["command_stream"] = dict(sha256=digest, bytes=len(changed))
                result["actual_argv"][-1] = digest
        elif name == "actual-argv":
            result["actual_argv"].append("--invented")
        else:
            result["execution_context"]["output"] += "/changed"
        (bad / "result.json").write_text(json.dumps(result) + "\n")
        checked = compare_capture(root, captures[0], bad, directory / ("trace-refusal-%02d.json" % index))
        assert checked.returncode == 2, (name, checked.stdout, checked.stderr)
    records = [json.loads((p / "result.json").read_bytes()) for p in captures]
    assert all(r["schema"] == "implementaudit.verifier-run.v2" for r in records)
    assert records[0]["node_trace"] is None
    assert records[1]["node_trace"] == dict(sha256=hashlib.sha256(original).hexdigest(), bytes=len(original))
    restored = []
    for index, source in enumerate(captures):
        target = directory / ("restored-v2-" + str(index))
        shutil.copytree(source, target)
        restored.append(target)
    checked = compare_capture(root, *restored, directory / "restored-v2-comparison.json")
    assert checked.returncode == 0, (checked.stdout, checked.stderr)
    assert all((source / "result.json").read_bytes() == (target / "result.json").read_bytes()
               for source, target in zip(captures, restored))
    # A constructed v1 compatibility record still requires its retained trace,
    # without pretending that the historical format originally bound its bytes.
    historical = []
    for index, source in enumerate(captures):
        target = directory / ("constructed-v1-" + str(index))
        shutil.copytree(source, target)
        record = json.loads((target / "result.json").read_bytes())
        record["schema"] = "implementaudit.verifier-run.v1"
        for key in ("node_trace", "environment_after", "engine_binding", "execution_context",
                    "actual_argv", "command_stream"):
            record.pop(key)
        (target / "commands.bin").unlink()
        (target / "result.json").write_text(json.dumps(record) + "\n")
        historical.append(target)
    before = (historical[1] / "result.json").read_bytes()
    output = directory / "constructed-v1-comparison.json"
    checked = compare_capture(root, *historical, output)
    assert checked.returncode == 0, (checked.stdout, checked.stderr)
    compared = json.loads(output.read_bytes())
    assert compared["record_coverage"] == ["HISTORICAL_V1_WHOLE_PROCESS_ONLY",
        "HISTORICAL_V1_RETAINED_TRACE_VALIDATED_NO_ORIGINAL_BINDING"]
    assert not {"same_engine", "same_execution_cwd", "same_compiled_stream"} & set(compared["checks"])
    assert (historical[1] / "result.json").read_bytes() == before
    for name in ("missing", "invalid", "status", "v2-field"):
        bad = directory / ("bad-v1-" + name)
        shutil.copytree(historical[1], bad)
        record = json.loads((bad / "result.json").read_bytes())
        if name == "missing":
            (bad / "nodes.tsv").unlink()
        elif name == "invalid":
            (bad / "nodes.tsv").write_bytes(events[0] + original)
        elif name == "status":
            record["nodes"][0].update(status="UNSETTLED", terminal=False)
        else:
            record["engine_binding"] = records[1]["engine_binding"]
        (bad / "result.json").write_text(json.dumps(record) + "\n")
        checked = compare_capture(root, historical[0], bad, directory / ("v1-refusal-" + name + ".json"))
        assert checked.returncode == 2, (name, checked.stdout, checked.stderr)


def capture_boundary_cases(root, directory, registry, prelude, tail):
    """Real small captures expose failed prefixes and available-input drift."""
    sample = root / "tests/sample.test.sh"
    sample.write_text("#!/bin/bash\nprintf 'sample\\n'\n")
    run_command(["git", "add", "."], cwd=root, check=True)
    run_command(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "capture-boundary fixture"], cwd=root, check=True)
    runner = root / "scripts/run-work-graph-verifier.sh"
    runner_bytes = runner.read_bytes()
    runner.write_bytes(b"#!/usr/bin/env bash\nexit 4\n")
    process, record = capture(root, directory / "capture-prestart")
    assert process.returncode == record["exit"] == 4
    assert all(n == dict(node=n["node"], status="UNSETTLED", terminal=False) for n in record["nodes"])
    assert record["node_trace"] == dict(sha256=hashlib.sha256(b"").hexdigest(), bytes=0)
    runner.write_bytes(runner_bytes)
    # A genuine failed prelude is a legal trailing START, with no invented PASS.
    (root / "scripts/verify-package.sh").write_text(prelude + "exit 7\n" + tail)
    process, record = capture(root, directory / "capture-prelude-failure")
    assert process.returncode == record["exit"] == 7
    assert record["nodes"][0]["status"] == "FAIL" and all(
        n["status"] == "UNSETTLED" for n in record["nodes"][1:])
    # All nodes can pass before the shared shell's EXIT trap produces nonzero.
    (root / "scripts/verify-package.sh").write_text(
        prelude.replace('printf "cleanup\\n" >&2', 'printf "cleanup\\n" >&2; exit 14') + tail)
    late = []
    for mode in ("legacy", "dag"):
        output = directory / ("capture-late-" + mode)
        process, record = capture(root, output, mode)
        assert process.returncode == record["exit"] == 14, (process.stdout, process.stderr)
        if mode == "dag":
            assert all(n["status"] == "PASS" for n in record["nodes"])
        late.append(output)
    checked = compare_capture(root, *late, directory / "late-comparison.json")
    assert checked.returncode == 0, (checked.stdout, checked.stderr)
    (root / "scripts/verify-package.sh").write_bytes(registry)
    # A malformed real trace may fail postprocessing, but must retain exit 9.
    sample.write_text("#!/bin/bash\nprintf 'sample\\n'\nprintf 'FOREIGN\\tPASS\\n' >&3\nexit 9\n")
    output = directory / "capture-trace-parser-failure"
    process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                           "dag", str(output)], cwd=root, capture_output=True)
    assert process.returncode == 2 and b"trace" in process.stderr
    assert (output / "exit-code.txt").read_bytes() == b"9\n"
    assert b"sample\n" in (output / "stdout.log").read_bytes()
    assert b"FOREIGN\tPASS\n" in (output / "nodes.tsv").read_bytes()
    assert not (output / "result.json").exists()
    output = directory / "capture-command-stream-failure"
    sample.write_text("#!/bin/bash\nprintf 'sample\\n'\nprintf 'changed retained stream\\n' >> " +
                      shlex.quote(str(output / "commands.bin")) + "\nexit 9\n")
    process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                           "dag", str(output)], cwd=root, capture_output=True)
    assert process.returncode == 2 and b"command stream differs" in process.stderr
    assert (output / "exit-code.txt").read_bytes() == b"9\n"
    assert b"sample\n" in (output / "stdout.log").read_bytes()
    assert (output / "commands.bin").read_bytes().endswith(b"changed retained stream\n")
    assert not (output / "result.json").exists()
    sample.write_text("#!/bin/bash\nprintf 'sample\\n'\n")
    run_command(["git", "add", "."], cwd=root, check=True)
    run_command(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                 "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "drift fixture"], cwd=root, check=True)
    # A ref alone changes: old HEAD/tree/tracked/status identities stay equal.
    run_command(["git", "update-ref", "refs/remotes/origin/main", "HEAD^"], cwd=root, check=True)
    before_dir = directory / "ref-before"
    _, before = capture(root, before_dir, "legacy")
    run_command(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=root, check=True)
    after_dir = directory / "ref-after"
    _, after = capture(root, after_dir)
    for key in ("head", "tree", "tracked_source_digest", "status_digest"):
        assert before["before"][key] == after["before"][key], key
    assert before["before"]["git_refs"] != after["before"]["git_refs"]
    checked = compare_capture(root, before_dir, after_dir, directory / "ref-comparison.json")
    assert checked.returncode == 1, (checked.stdout, checked.stderr)
    comparison = json.loads((directory / "ref-comparison.json").read_bytes())
    assert not comparison["checks"]["same_source"] and comparison["checks"]["same_stdout"]
    # HEAD's symbolic relation can change with identical object and ref values.
    before_dir, after_dir = directory / "head-ref-before", directory / "head-ref-after"
    _, before = capture(root, before_dir, "legacy")
    run_command(["git", "checkout", "--detach", "-q", "HEAD"], cwd=root, check=True)
    try:
        _, after = capture(root, after_dir)
    finally:
        run_command(["git", "symbolic-ref", "HEAD", before["before"]["head_reference"]], cwd=root, check=True)
    for key in ("head", "tree", "git_refs", "tracked_source_digest", "status_digest"):
        assert before["before"][key] == after["before"][key], key
    assert before["before"]["head_reference"] != after["before"]["head_reference"]
    checked = compare_capture(root, before_dir, after_dir, directory / "head-ref-comparison.json")
    assert checked.returncode == 1, (checked.stdout, checked.stderr)
    # Bind safe branch/config inputs and a nonselected environment value by
    # digest only. The random canary value is never persisted or printed.
    for key in ("GITHUB_BASE_REF", "GITHUB_ACTIONS", "R0035_UNSELECTED_CANARY"):
        old_value, new_value = os.urandom(24).hex(), os.urandom(24).hex()
        before_dir = directory / ("env-before-" + key)
        after_dir = directory / ("env-after-" + key)
        _, before = capture(root, before_dir, "legacy", dict(os.environ, **{key: old_value}))
        _, after = capture(root, after_dir, "dag", dict(os.environ, **{key: new_value}))
        assert before["environment"]["inherited_environment_sha256"] != after["environment"]["inherited_environment_sha256"]
        if key == "R0035_UNSELECTED_CANARY":
            for value, output in ((old_value, before_dir), (new_value, after_dir)):
                assert value.encode() not in (output / "result.json").read_bytes()
                assert value.encode() not in (output / "mapping.json").read_bytes()
        checked = compare_capture(root, before_dir, after_dir, directory / ("env-comparison-" + key + ".json"))
        assert checked.returncode == 1, (key, checked.stdout, checked.stderr)
        compared = json.loads((directory / ("env-comparison-" + key + ".json")).read_bytes())
        assert not compared["checks"]["same_environment"] and compared["checks"]["same_stdout"]
    # The same PATH and version output do not hide different executable bytes.
    tool_bin = directory / "git-proxy-bin"
    tool_bin.mkdir()
    proxy = tool_bin / "git"
    real_git = shutil.which("git")
    proxy_text = "#!/bin/bash\nexec " + shlex.quote(real_git) + ' "$@"\n'
    proxy.write_text(proxy_text + "# first tool bytes\n")
    proxy.chmod(0o755)
    env = dict(os.environ, PATH=str(tool_bin) + os.pathsep + os.environ["PATH"])
    before_dir, after_dir = directory / "tool-before", directory / "tool-after"
    _, before = capture(root, before_dir, "legacy", env)
    proxy.write_text(proxy_text + "# other tool bytes\n")
    _, after = capture(root, after_dir, "dag", env)
    assert before["environment"]["git"] == after["environment"]["git"]
    assert before["environment"]["inherited_environment_sha256"] == after["environment"]["inherited_environment_sha256"]
    assert before["environment"]["executables"]["git"]["sha256"] != after["environment"]["executables"]["git"]["sha256"]
    checked = compare_capture(root, before_dir, after_dir, directory / "tool-comparison.json")
    assert checked.returncode == 1, (checked.stdout, checked.stderr)
    # Ordinary permission bits and same-name untracked contents are available
    # facts even when Git's prior status/content projection stays unchanged.
    original_mode = sample.stat().st_mode & 0o7777
    before_dir, after_dir = directory / "mode-before", directory / "mode-after"
    _, before = capture(root, before_dir, "legacy")
    sample.chmod(0o600)
    _, after = capture(root, after_dir)
    sample.chmod(original_mode)
    assert before["before"]["status_digest"] == after["before"]["status_digest"]
    assert before["before"]["tracked_source_digest"] == after["before"]["tracked_source_digest"]
    checked = compare_capture(root, before_dir, after_dir, directory / "mode-comparison.json")
    assert checked.returncode == 1, (checked.stdout, checked.stderr)
    for name, ancestor in (("root", root), ("parent", sample.parent)):
        old_mode = ancestor.stat().st_mode & 0o7777
        before_dir, after_dir = directory / (name + "-mode-before"), directory / (name + "-mode-after")
        _, before = capture(root, before_dir, "legacy")
        ancestor.chmod(old_mode ^ 0o020)
        try:
            _, after = capture(root, after_dir)
        finally:
            ancestor.chmod(old_mode)
        for key in ("status_digest", "tracked_source_digest"):
            assert before["before"][key] == after["before"][key]
        checked = compare_capture(root, before_dir, after_dir, directory / (name + "-mode-comparison.json"))
        assert checked.returncode == 1, (checked.stdout, checked.stderr)
    untracked = root / "same-name-untracked.txt"
    untracked.write_bytes(b"first ordinary untracked input\n")
    before_dir, after_dir = directory / "untracked-before", directory / "untracked-after"
    _, before = capture(root, before_dir, "legacy")
    untracked.write_bytes(b"other ordinary untracked input\n")
    _, after = capture(root, after_dir)
    assert before["before"]["status_digest"] == after["before"]["status_digest"]
    assert before["before"]["tracked_source_digest"] == after["before"]["tracked_source_digest"]
    checked = compare_capture(root, before_dir, after_dir, directory / "untracked-comparison.json")
    assert checked.returncode == 1, (checked.stdout, checked.stderr)
    untracked.unlink()
    sample.write_text("#!/bin/bash\nprintf 'sample\\n'\nexit 9\n")


def observer_probe(root, action, *arguments):
    """Execute a retained small observer probe with the actual fixture module."""
    code = ("import importlib.util, json, os, sys\nfrom pathlib import Path\n"
            "spec = importlib.util.spec_from_file_location('observer_probe', sys.argv[1])\n"
            "q = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(q)\ntry:\n" +
            "\n".join("    " + line for line in action.splitlines()) +
            "\nexcept q.WG.WorkGraphError as exc:\n"
            "    print(str(exc), file=sys.stderr)\n    raise SystemExit(2)\n")
    return run_command([sys.executable, "-B", "-c", code,
                        str(root / "scripts/qualify-work-graph-verifier.py"), *map(str, arguments)],
                       cwd=root, capture_output=True, timeout=10)


def engine_boundary_cases(root, directory):
    sample = root / "tests/sample.test.sh"
    sample_bytes = sample.read_bytes()
    engines = (("driver", root / "scripts/qualify-work-graph-verifier.py"),
               ("compiler", root / "skills/implementaudit/scripts/compile-work-graph.py"))
    for name, path in engines:
        saved = path.read_bytes()
        output = directory / ("engine-prelaunch-" + name)
        try:
            process = observer_probe(root, """original = q.source_identity
def drift():
    observed = original()
    target = Path(sys.argv[2])
    target.write_bytes(target.read_bytes() + b"\\n# constructed prelaunch drift\\n")
    return observed
q.source_identity = drift
q.run("legacy", Path(sys.argv[3]))""", path, output)
            assert process.returncode == 2 and b"loaded verifier engine" in process.stderr
            assert not (output / "exit-code.txt").exists()
            (output / "observed-engine-source.py").write_bytes(path.read_bytes())
        finally:
            path.write_bytes(saved)
        # A real completed child mutates the loaded source; preserve its exit
        # before refusing the later observation, including both engine images.
        output = directory / ("engine-postexit-" + name)
        sample.write_text("#!/bin/bash\nprintf 'sample\\n'\nprintf '\\n# constructed postexit drift\\n' >> " +
                          shlex.quote(path.relative_to(root).as_posix()) + "\nexit 9\n")
        try:
            process = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py",
                                   "legacy", str(output)], cwd=root, capture_output=True)
            assert process.returncode == 2 and b"loaded verifier engine" in process.stderr
            assert (output / "exit-code.txt").read_bytes() == b"9\n"
            assert b"sample\n" in (output / "stdout.log").read_bytes()
            assert not (output / "result.json").exists()
            (output / "observed-engine-source.py").write_bytes(path.read_bytes())
        finally:
            path.write_bytes(saved)
            sample.write_bytes(sample_bytes)
    # ROOT may be a candidate with no engine files. The binding still describes
    # the actual loaded images, and the real legacy capture remains usable.
    alternate = directory / "alternate-source"
    for relative in ("scripts/verify-package.sh", "scripts/generate-readme-diagrams.sh", "tests/sample.test.sh"):
        target = alternate / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, target)
    run_command(["git", "init", "-q", str(alternate)], check=True)
    run_command(["git", "add", "."], cwd=alternate, check=True)
    run_command(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "alternate source"], cwd=alternate, check=True)
    output = directory / "engine-alternate-root"
    process = observer_probe(root, """binding = q.full_engine_binding()
q.ROOT = Path(sys.argv[2])
assert q.full_engine_binding() == binding
assert q.run("legacy", Path(sys.argv[3])) == 9""", alternate, output)
    assert process.returncode == 0, (process.stdout, process.stderr)
    assert json.loads((output / "result.json").read_bytes())["engine_binding"]["driver_sha256"] == hashlib.sha256(
        (root / "scripts/qualify-work-graph-verifier.py").read_bytes()).hexdigest()
    fifo = directory / "named-executable-fifo"
    os.mkfifo(fifo)
    process = observer_probe(root, "q.executable_identity(sys.argv[2])", fifo)
    assert process.returncode == 2 and b"unsupported executable member" in process.stderr
    process = observer_probe(root, "q.os.supports_dir_fd = set()\nq.source_identity()")
    assert process.returncode == 2 and b"requires no-follow directory descriptors" in process.stderr
    # Source ancestors and leaves never grant reads through their symlinks.
    boundary = directory / "source-symlink-boundary"
    boundary.mkdir()
    (boundary / "escape").symlink_to(directory, target_is_directory=True)
    process = observer_probe(root, """observed = q.source_member("escape/named-executable-fifo", root=Path(sys.argv[2]))
assert observed["kind"] == "UNACQUIRED" and observed["reason"] == "MISSING_OR_UNSUPPORTED_ANCESTOR"
leaf = q.source_member("escape", root=Path(sys.argv[2]))
assert leaf["kind"] == "SYMLINK" and leaf["content"] == "TARGET_NOT_FOLLOWED"
print(json.dumps({"ancestor": observed, "leaf": leaf}, sort_keys=True))""", boundary)
    assert process.returncode == 0, (process.stdout, process.stderr)


def reject(call, message):
    try:
        call()
    except wg.WorkGraphError as exc:
        assert message in str(exc), str(exc)
    else:
        raise AssertionError("accepted negative: " + message)


def selective_policy(current):
    # Constructed policy inputs only. Real acquisition, issuance and consumption
    # have a separate explicit Linux qualification; this supplies no such proof.
    graph = wg.compile_verifier_graph_v1(current, wg.verifier_registered_tests_v1(current), {})
    inputs = {"COMMAND:" + path + ":0": dict(program_sha256=contract["sha256"], image_digest="1" * 64)
              for path, contract in wg.VERIFIER_LEAF_CONTRACTS_V1.items()}
    acquired = dict(schema="implementaudit.verifier-acquisition.v1", scope="CONTROLLED_TASK_LEAVES_V1",
                    binding={"constructed": "policy-only"}, inputs=inputs)
    plan = wg.compile_verifier_reuse_v1(graph, current, acquired, {})
    assert all(n["decision"] == "EXECUTE" for n in plan["nodes"])
    issued = {n["node"]: n["key"] for n in plan["nodes"]}
    repeat = wg.compile_verifier_reuse_v1(graph, current, acquired, issued)
    assert all(n["decision"] == "CONSUME_PRIOR_SUCCESS" for n in repeat["nodes"])
    changed = copy.deepcopy(acquired)
    changed["inputs"]["COMMAND:scripts/check-readme-toc.sh:0"]["image_digest"] = "2" * 64
    selected = wg.compile_verifier_reuse_v1(graph, current, changed, issued)
    assert [n["decision"] for n in selected["nodes"]] == ["EXECUTE", "CONSUME_PRIOR_SUCCESS"]
    for component in ("registry", "source", "environment", "runtime", "producer", "scope"):
        changed = copy.deepcopy(acquired)
        changed["binding"][component] = "changed"
        assert all(n["decision"] == "EXECUTE" for n in wg.compile_verifier_reuse_v1(graph, current, changed, issued)["nodes"])
    changed = copy.deepcopy(acquired)
    changed["inputs"][next(iter(inputs))]["program_sha256"] = "0" * 64
    reject(lambda: wg.compile_verifier_reuse_v1(graph, current, changed, issued), "checker contract")
    changed = copy.deepcopy(acquired)
    changed["inputs"].pop(next(iter(inputs)))
    reject(lambda: wg.compile_verifier_reuse_v1(graph, current, changed, issued), "population")
    changed = dict(acquired, scope="UNQUALIFIED")
    reject(lambda: wg.compile_verifier_reuse_v1(graph, current, changed, issued), "scope")
    drift = current.replace(b"bash scripts/check-readme-toc.sh\n", b"bash scripts/check-readme-toc.sh --unknown\n")
    drift_graph = wg.compile_verifier_graph_v1(drift, wg.verifier_registered_tests_v1(drift), {})
    reject(lambda: wg.compile_verifier_reuse_v1(drift_graph, drift, acquired, issued), "invocation")


def main():
    global RETAIN
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retain-fixtures", type=Path)
    parser.add_argument("--portal-only", action="store_true")
    options = parser.parse_args()
    if options.retain_fixtures is not None:
        RETAIN = options.retain_fixtures.resolve()
        RETAIN.mkdir(parents=True, exist_ok=False)
        (RETAIN / "commands").mkdir()
        (RETAIN / "objects").mkdir()
        shutil.copyfile(__file__, RETAIN / "harness-source.py")
    if options.portal_only:
        with fixture_directory() as td:
            portal_capture_cases(Path(td))
        print("work-graph-verifier: finite actual portal capture controls passed")
        return
    current = (ROOT / "scripts/verify-package.sh").read_bytes()
    selective_policy(current)
    tests = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("*.test.sh"))
    # This independent source slice deliberately awaits its separate registry
    # patch. Mapping the declared registry still succeeds, while a required
    # whole-test-population comparison exposes the exact missing registration.
    registered = wg.verifier_registered_tests_v1(current)
    mapping = wg.compile_verifier_graph_v1(current, registered, {"scope": "constructed"})
    assert b"".join(n["source"].encode() for n in mapping["nodes"]) == current
    assert mapping["covered_bytes"] == len(current)
    assert mapping["nodes"][0]["kind"] == "COMPOSED_PRELUDE"
    assert mapping["nodes"][-1]["kind"] == "TERMINAL"
    assert len(mapping["test_nodes"]) == len(registered)
    if tests != sorted(registered):
        reject(lambda: wg.compile_verifier_graph_v1(current, tests, {}), "registration")
    drift = current.replace(b"bash tests/lean-discipline.test.sh\n", b"bash tests/lean-discipline.test.sh\nbash tests/lean-discipline.test.sh\n")
    reject(lambda: wg.compile_verifier_graph_v1(drift, registered, {}), "duplicate")
    drift = current.replace(b"git diff --check\n", b"touch undeclared-global-write\n")
    reject(lambda: wg.compile_verifier_graph_v1(drift, registered, {}), "grammar")
    drift = current.replace(b"bash tests/lean-discipline.test.sh\n", b"")
    reject(lambda: wg.compile_verifier_graph_v1(drift, registered, {}), "registration")

    # Preserve order, shell globals, terminal stdout/stderr and legacy fail-fast
    # in an actually executed held-out registry. No hand-written PASS oracle.
    with fixture_directory() as td:
        root = Path(td) / "repo"
        (root / "scripts").mkdir(parents=True)
        (root / "tests").mkdir()
        run_command(["git", "init", "-q", str(root)], check=True)
        shutil.copyfile(ROOT / "scripts/run-work-graph-verifier.sh", root / "scripts/run-work-graph-verifier.sh")
        shutil.copyfile(ROOT / "scripts/qualify-work-graph-verifier.py", root / "scripts/qualify-work-graph-verifier.py")
        (root / "skills/implementaudit/scripts").mkdir(parents=True)
        shutil.copyfile(ROOT / "skills/implementaudit/scripts/compile-work-graph.py", root / "skills/implementaudit/scripts/compile-work-graph.py")
        (root / "scripts/generate-readme-diagrams.sh").write_text("#!/bin/bash\nprintf 'first\\n'\n")
        prelude = ('#!/usr/bin/env bash\nset -euo pipefail\n'
                   'repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"\n'
                   'cd "$repo_root"\n'
                   'shared_state="kept in one shell"\n'
                   'trap \'printf "cleanup\\n" >&2\' EXIT\n\n')
        tail = ('bash scripts/generate-readme-diagrams.sh --check\n'
                'bash tests/sample.test.sh "$shared_state"\n'
                'git diff --check\n\n'
                "printf 'verify-package: ok\\n'\n")
        registry = (prelude + tail).encode()
        (root / "scripts/verify-package.sh").write_bytes(registry)
        mapping = wg.compile_verifier_graph_v1(registry, ["tests/sample.test.sh"], {})
        command_file = Path(td) / "commands.bin"
        command_file.write_bytes(wg.verifier_command_stream_v1(mapping, registry))
        for code in (0, 9):
            (root / "tests/sample.test.sh").write_text('#!/bin/bash\nprintf \'%s\\n\' "$1"\nprintf \'diagnostic\\n\' >&2\nexit ' + str(code) + '\n')
            legacy = run_command(["bash", "scripts/verify-package.sh"], cwd=root, capture_output=True)
            trace = Path(td) / ("trace-" + str(code))
            dag = run_command(["bash", "scripts/run-work-graph-verifier.sh", str(command_file), str(trace), str(len(mapping["nodes"])), hashlib.sha256(command_file.read_bytes()).hexdigest()], cwd=root, capture_output=True)
            assert (legacy.stdout, legacy.stderr, legacy.returncode) == (dag.stdout, dag.stderr, dag.returncode), (legacy, dag)
            assert legacy.returncode == code
            events = trace.read_text().splitlines()
            assert len([e for e in events if e.endswith("\tSTART")]) == (len(mapping["nodes"]) if code == 0 else 3)
            if code:
                assert b"verify-package: ok" not in dag.stdout
                assert not events[-1].endswith("\tPASS")
        # The framing descriptor must never become a tested command's stdin.
        (root / "tests/sample.test.sh").write_text('#!/bin/bash\nIFS= read -r value\nprintf \'stdin=%s\\n\' "$value"\n')
        legacy = run_command(["bash", "scripts/verify-package.sh"], cwd=root, input=b"USER_INPUT\n", capture_output=True)
        dag = run_command(["bash", "scripts/run-work-graph-verifier.sh", str(command_file), str(Path(td) / "stdin-trace"), str(len(mapping["nodes"])), hashlib.sha256(command_file.read_bytes()).hexdigest()], cwd=root, input=b"USER_INPUT\n", capture_output=True)
        assert (legacy.stdout, legacy.stderr, legacy.returncode) == (dag.stdout, dag.stderr, dag.returncode), (legacy, dag)
        assert legacy.returncode == 0 and b"stdin=USER_INPUT\n" in legacy.stdout
        # Replace a regular stream path after its validating Python process
        # returns. Execution must use the retained validated bytes, not reopen
        # the path. This is a harmless marker mutation in an isolated fixture.
        original_stream = command_file.read_bytes()
        replacement = Path(td) / "replacement.bin"
        replacement.write_bytes(original_stream.replace(b"printf 'verify-package: ok\\n'\n", b"printf 'MUTATED_FRAME_EXECUTED\\n'\n"))
        test_bin = Path(td) / "bin"
        test_bin.mkdir()
        proxy = test_bin / "python"
        proxy.write_text("#!/bin/bash\nset -e\n" + shlex.quote(sys.executable) + ' "$@"\n' + shlex.join(["cp", str(replacement), str(command_file)]) + "\n")
        proxy.chmod(0o755)
        replaced = run_command(["bash", "scripts/run-work-graph-verifier.sh", str(command_file), str(Path(td) / "replaced-trace"), str(len(mapping["nodes"])), hashlib.sha256(original_stream).hexdigest()], cwd=root, input=b"USER_INPUT\n", capture_output=True, env=dict(os.environ, PATH=str(test_bin) + os.pathsep + os.environ["PATH"]))
        assert (legacy.stdout, legacy.stderr, legacy.returncode) == (replaced.stdout, replaced.stderr, replaced.returncode), replaced
        assert command_file.read_bytes() == replacement.read_bytes()
        command_file.write_bytes(original_stream)
        # Validate the entire frame population before any node can execute.
        frames = original_stream.split(b"\0")
        corruptions = [original_stream + b"EXTRA_UNTERMINATED_NODE", original_stream[:-1],
                       original_stream + b"EXTRA\0", original_stream + b"\0\0",
                       b"\0" + original_stream, b"\0".join(frames[2:4] + frames[:2] + frames[4:])]
        for index, data in enumerate(corruptions):
            damaged_stream = Path(td) / ("damaged-" + str(index))
            damaged_stream.write_bytes(data)
            result = run_command(["bash", "scripts/run-work-graph-verifier.sh", str(damaged_stream), str(Path(td) / ("bad-trace-" + str(index))), str(len(mapping["nodes"])), hashlib.sha256(data).hexdigest()], cwd=root, capture_output=True)
            assert result.returncode == 2 and not result.stdout, result
        result = run_command(["bash", "scripts/run-work-graph-verifier.sh", str(command_file), str(Path(td) / "wrong-digest-trace"), str(len(mapping["nodes"])), "0" * 64], cwd=root, capture_output=True)
        assert result.returncode == 2 and not result.stdout
        fifo = Path(td) / "not-a-regular-stream"
        os.mkfifo(fifo)
        refused = run_command(["bash", "scripts/run-work-graph-verifier.sh", str(fifo), str(Path(td) / "fifo-trace"), str(len(mapping["nodes"])), hashlib.sha256(original_stream).hexdigest()], cwd=root, capture_output=True, timeout=3)
        assert refused.returncode == 2 and not refused.stdout
        # Exercise both actual driver routes through their terminal JSON write.
        # Captures live outside the source tree and every command is tiny.
        for code in (0, 9):
            (root / "tests/sample.test.sh").write_text("#!/bin/bash\nprintf 'sample\\n'\nexit " + str(code) + "\n")
            run_command(["git", "add", "."], cwd=root, check=True)
            run_command(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture " + str(code)], cwd=root, check=True)
            captures = []
            for mode in ("legacy", "dag"):
                output = Path(td) / ("capture-" + mode + "-" + str(code))
                result = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", mode, str(output)], cwd=root, capture_output=True)
                assert result.returncode == code, (result.stdout, result.stderr)
                record = json.loads((output / "result.json").read_bytes())
                assert record["exit"] == code and type(record["elapsed_ms"]) is int
                assert (output / "exit-code.txt").read_text() == str(code) + "\n"
                captures.append(output)
            comparison = Path(td) / ("comparison-" + str(code) + ".json")
            result = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "compare", *map(str, captures), str(comparison)], cwd=root, capture_output=True)
            assert result.returncode == 0, (result.stdout, result.stderr)
            if code == 0:
                for index, field in enumerate(("graph_digest", "mapping_digest", "mapped_source", "mapped_nodes", "node_population", "stdout_sha256", "stderr_sha256", "exit", "missing_exit")):
                    bad = Path(td) / ("inconsistent-" + field)
                    shutil.copytree(captures[1], bad)
                    record = json.loads((bad / "result.json").read_bytes())
                    if field in {"graph_digest", "stdout_sha256", "stderr_sha256"}:
                        record[field] = "0" * 64
                    elif field in {"mapping_digest", "mapped_source"}:
                        mapped = json.loads((bad / "mapping.json").read_bytes())
                        if field == "mapping_digest":
                            mapped["digest"] = "0" * 64
                        else:
                            mapped["nodes"][0]["source"] += "# changed command\n"
                        (bad / "mapping.json").write_text(json.dumps(mapped))
                    elif field == "mapped_nodes":
                        record["mapped_nodes"] += 1
                    elif field == "node_population":
                        record["nodes"].append(copy.deepcopy(record["nodes"][0]))
                    elif field == "exit":
                        (bad / "exit-code.txt").write_text("7\n")
                    else:
                        (bad / "exit-code.txt").unlink()
                    (bad / "result.json").write_text(json.dumps(record))
                    checked = run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "compare", str(captures[0]), str(bad), str(Path(td) / ("inconsistent-result-%d.json" % index))], cwd=root, capture_output=True)
                    assert checked.returncode in {1, 2}, (field, checked.stdout, checked.stderr)
                trace_integrity_cases(root, Path(td), captures)
        capture_boundary_cases(root, Path(td), registry, prelude, tail)
        engine_boundary_cases(root, Path(td))
        extended_capture_cases(Path(td))
        portal_capture_cases(Path(td))
        # A later recording error must not erase the nested process exit/logs.
        driver_spec = importlib.util.spec_from_file_location("capture_fixture", root / "scripts/qualify-work-graph-verifier.py")
        driver = importlib.util.module_from_spec(driver_spec)
        driver_spec.loader.exec_module(driver)
        encode = driver.WG.canonical_json_v1
        def fail_result(value):
            if isinstance(value, dict) and value.get("schema") in {"implementaudit.verifier-run.v1", "implementaudit.verifier-run.v2"}:
                raise driver.WG.WorkGraphError("injected recording failure")
            return encode(value)
        driver.WG.canonical_json_v1 = fail_result
        output = Path(td) / "capture-recording-failure"
        try:
            driver.run("legacy", output)
        except driver.WG.WorkGraphError as exc:
            assert "injected recording failure" in str(exc)
        else:
            raise AssertionError("missing injected failure")
        assert (output / "exit-code.txt").read_text() == "9\n"
        assert b"sample\n" in (output / "stdout.log").read_bytes()
        damaged = copy.deepcopy(mapping)
        damaged["nodes"].pop()
        reject(lambda: wg.verifier_command_stream_v1(damaged, registry), "digest")
        reject(lambda: wg.verifier_command_stream_v1(mapping, registry + b"\n"), "stale")
    print("work-graph-verifier: complete registry byte partition; positive/fail-fast raw streams and exit match")
    print("work-graph-verifier.test: ok")


if __name__ == "__main__":
    main()
