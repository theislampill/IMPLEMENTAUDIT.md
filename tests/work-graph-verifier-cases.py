"""Verifier graph byte coverage and actual shared-shell transport controls."""
import copy
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
    with tempfile.TemporaryDirectory(prefix="r0035-verifier-") as td:
        root = Path(td) / "repo"
        (root / "scripts").mkdir(parents=True)
        (root / "tests").mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
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
            legacy = subprocess.run(["bash", "scripts/verify-package.sh"], cwd=root, capture_output=True)
            trace = Path(td) / ("trace-" + str(code))
            dag = subprocess.run(["bash", "scripts/run-work-graph-verifier.sh", str(command_file), str(trace), str(len(mapping["nodes"])), hashlib.sha256(command_file.read_bytes()).hexdigest()], cwd=root, capture_output=True)
            assert (legacy.stdout, legacy.stderr, legacy.returncode) == (dag.stdout, dag.stderr, dag.returncode), (legacy, dag)
            assert legacy.returncode == code
            events = trace.read_text().splitlines()
            assert len([e for e in events if e.endswith("\tSTART")]) == (len(mapping["nodes"]) if code == 0 else 3)
            if code:
                assert b"verify-package: ok" not in dag.stdout
                assert not events[-1].endswith("\tPASS")
        # The framing descriptor must never become a tested command's stdin.
        (root / "tests/sample.test.sh").write_text('#!/bin/bash\nIFS= read -r value\nprintf \'stdin=%s\\n\' "$value"\n')
        legacy = subprocess.run(["bash", "scripts/verify-package.sh"], cwd=root, input=b"USER_INPUT\n", capture_output=True)
        dag = subprocess.run(["bash", "scripts/run-work-graph-verifier.sh", str(command_file), str(Path(td) / "stdin-trace"), str(len(mapping["nodes"])), hashlib.sha256(command_file.read_bytes()).hexdigest()], cwd=root, input=b"USER_INPUT\n", capture_output=True)
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
        replaced = subprocess.run(["bash", "scripts/run-work-graph-verifier.sh", str(command_file), str(Path(td) / "replaced-trace"), str(len(mapping["nodes"])), hashlib.sha256(original_stream).hexdigest()], cwd=root, input=b"USER_INPUT\n", capture_output=True, env=dict(os.environ, PATH=str(test_bin) + os.pathsep + os.environ["PATH"]))
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
            result = subprocess.run(["bash", "scripts/run-work-graph-verifier.sh", str(damaged_stream), str(Path(td) / ("bad-trace-" + str(index))), str(len(mapping["nodes"])), hashlib.sha256(data).hexdigest()], cwd=root, capture_output=True)
            assert result.returncode == 2 and not result.stdout, result
        result = subprocess.run(["bash", "scripts/run-work-graph-verifier.sh", str(command_file), str(Path(td) / "wrong-digest-trace"), str(len(mapping["nodes"])), "0" * 64], cwd=root, capture_output=True)
        assert result.returncode == 2 and not result.stdout
        fifo = Path(td) / "not-a-regular-stream"
        os.mkfifo(fifo)
        refused = subprocess.run(["bash", "scripts/run-work-graph-verifier.sh", str(fifo), str(Path(td) / "fifo-trace"), str(len(mapping["nodes"])), hashlib.sha256(original_stream).hexdigest()], cwd=root, capture_output=True, timeout=3)
        assert refused.returncode == 2 and not refused.stdout
        # Exercise both actual driver routes through their terminal JSON write.
        # Captures live outside the source tree and every command is tiny.
        for code in (0, 9):
            (root / "tests/sample.test.sh").write_text("#!/bin/bash\nprintf 'sample\\n'\nexit " + str(code) + "\n")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@localhost", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture " + str(code)], cwd=root, check=True)
            captures = []
            for mode in ("legacy", "dag"):
                output = Path(td) / ("capture-" + mode + "-" + str(code))
                result = subprocess.run([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", mode, str(output)], cwd=root, capture_output=True)
                assert result.returncode == code, (result.stdout, result.stderr)
                record = json.loads((output / "result.json").read_bytes())
                assert record["exit"] == code and type(record["elapsed_ms"]) is int
                assert (output / "exit-code.txt").read_text() == str(code) + "\n"
                captures.append(output)
            comparison = Path(td) / ("comparison-" + str(code) + ".json")
            result = subprocess.run([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "compare", *map(str, captures), str(comparison)], cwd=root, capture_output=True)
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
                    checked = subprocess.run([sys.executable, "-B", "scripts/qualify-work-graph-verifier.py", "compare", str(captures[0]), str(bad), str(Path(td) / ("inconsistent-result-%d.json" % index))], cwd=root, capture_output=True)
                    assert checked.returncode in {1, 2}, (field, checked.stdout, checked.stderr)
        # A later recording error must not erase the nested process exit/logs.
        driver_spec = importlib.util.spec_from_file_location("capture_fixture", root / "scripts/qualify-work-graph-verifier.py")
        driver = importlib.util.module_from_spec(driver_spec)
        driver_spec.loader.exec_module(driver)
        encode = driver.WG.canonical_json_v1
        def fail_result(value):
            if isinstance(value, dict) and value.get("schema") == "implementaudit.verifier-run.v1":
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
