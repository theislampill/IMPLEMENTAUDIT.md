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

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("work_graph", ROOT / "skills/implementaudit/scripts/compile-work-graph.py")
wg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wg)
RETAIN = None


def run_command(command, **kwargs):
    """Retain the real tiny-fixture command, source objects, streams and exit."""
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
    candidate = Path(record["cwd"])
    objects = {}
    if (candidate / "tests/sample.test.sh").is_file():
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


def compare_capture(root, left, right, output):
    return run_command([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "compare",
                        str(left), str(right), str(output)], cwd=root, capture_output=True)


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
    options = parser.parse_args()
    if options.retain_fixtures is not None:
        RETAIN = options.retain_fixtures.resolve()
        RETAIN.mkdir(parents=True, exist_ok=False)
        (RETAIN / "commands").mkdir()
        (RETAIN / "objects").mkdir()
        shutil.copyfile(__file__, RETAIN / "harness-source.py")
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
