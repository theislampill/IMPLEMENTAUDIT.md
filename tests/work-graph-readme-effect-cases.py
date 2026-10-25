#!/usr/bin/env python3
"""Actual README generation/consumption controls; portable evidence only."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch, sentinel

ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
OWNER = ROOT / "scripts/work-graph-readme-effect.py"
LOADER = ROOT / "scripts/load-work-graph-readme-effect.py"
SUBJECTS = ("scripts/generate-readme-diagrams.sh", "README.md",
            "docs/diagrams/tooling-architecture.mmd",
            "docs/diagrams/invocation-modes.mmd", "docs/diagrams/execution-spine.mmd")


def load_module(path):
    data = path.read_bytes()
    spec = importlib.util.spec_from_file_location("readme_effect_capture", path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module, data


def load(path):
    # The harness retains the outer loader buffer it actually compiles. The
    # product never calls a later self-file read an executing-loader identity.
    loader, captured = load_module(path.with_name(LOADER.name))
    owner = loader._load_owner()
    owner._TEST_OUTER_LOADER_SOURCE = captured
    return owner


class EffectFixture:
    HISTORICAL_FIXTURE = True
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="r0035-readme-effect-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.addCleanup(self.retain_completed_case)
        self.source = self.base / "source"
        self.owner_path = (H.copy_readme_engine(self.base / "selected-engine") / "scripts/work-graph-readme-effect.py"
                           if self.HISTORICAL_FIXTURE else OWNER)
        for name in (*SUBJECTS, "scripts/verify-package.sh"):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(H.input_bytes(name) if self.HISTORICAL_FIXTURE else (ROOT / name).read_bytes())
        readme = self.source / "README.md"
        original = readme.read_bytes()
        marker = b"<!-- BEGIN: implementaudit-diagram:tooling-architecture -->"
        self.assertEqual(original.count(marker), 1)
        self.stale = original.replace(marker, marker + b"\nSTALE PHYSICAL PREIMAGE", 1)
        readme.write_bytes(self.stale)

    def owner_session(self):
        self.owner = load(self.owner_path)
        session = self.owner.EffectSession(self.source, self.base / "evidence")
        self.addCleanup(session.close)
        return session

    def retain_completed_case(self):
        if not os.environ.get("R0035_README_EFFECT_EVIDENCE"):
            return
        destination = Path(os.environ["R0035_README_EFFECT_EVIDENCE"])
        case = destination / "cases" / self._testMethodName
        case.parent.mkdir(parents=True, exist_ok=True)
        objects = Path(os.environ.get("R0035_README_EFFECT_OBJECTS", str(destination / "objects")))
        keys = []
        shutil.copytree(self.base, case, ignore=lambda _p, names: ["objects"] if "objects" in names else [])
        # The session has closed before cleanup. Deduplication is evidence
        # retention only; live custody never imports a completed case's objects.
        for path in sorted(self.base.glob("*/objects/*")):
            data = path.read_bytes()
            actual = hashlib.sha256(data).hexdigest()
            stored = objects / actual
            stored.parent.mkdir(parents=True, exist_ok=True)
            if stored.exists():
                self.assertEqual(stored.read_bytes(), data)
            else:
                shutil.copy2(path, stored)
            keys.append(dict(expected=path.name, actual=actual))
        (case / "retention.json").write_text(json.dumps(dict(
            scope="ACTUAL_PORTABLE_README_EFFECT_NOT_CANONICAL_OR_NATIVE_ACCEPTANCE",
            retained_objects=keys, object_store=os.path.relpath(objects, case),
            source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (OWNER, LOADER, ROOT / "scripts/readme-effect-bootstrap.py", Path(__file__)) if p.exists()},
            outer_loader_executed_sha256=(hashlib.sha256(self.owner._TEST_OUTER_LOADER_SOURCE).hexdigest()
                                          if hasattr(self, "owner") else None),
            authority="NONE"), sort_keys=True) + "\n")


class LoaderCases(EffectFixture, unittest.TestCase):
    def engine(self, name="engine"):
        return H.copy_readme_engine(self.base / name)

    def loader(self, engine):
        return load_module(engine / "scripts/load-work-graph-readme-effect.py")[0]

    def compiler_marker(self, engine, name="UNSUPPORTED_COMPILER_EXECUTED"):
        marker = self.base / name
        compiler = engine / "skills/implementaudit/scripts/compile-work-graph.py"
        compiler.write_bytes(compiler.read_bytes() + (
            "\nfrom pathlib import Path as _ProbePath\n_ProbePath(" + repr(str(marker)) +
            ").write_text('unsupported compiler executed\\n')\n").encode())
        return marker

    def test_unknown_compiler_refuses_before_dependent_execution(self):
        engine = self.engine()
        marker = self.compiler_marker(engine)
        loader = self.loader(engine)
        with patch.object(loader._Engine, "execute") as executed:
            with self.assertRaisesRegex(ValueError, "unsupported fixed engine source"):
                loader._load_owner()
        executed.assert_not_called()
        self.assertFalse(marker.exists())

    def test_same_byte_foreign_qualifier_alias_refuses(self):
        engine, foreign = self.engine(), self.engine("foreign")
        marker = self.compiler_marker(foreign)
        qualifier = engine / "scripts/qualify-work-graph-verifier.py"
        before = qualifier.read_bytes()
        qualifier.unlink()
        qualifier.symlink_to(foreign / "scripts/qualify-work-graph-verifier.py")
        self.assertEqual(qualifier.read_bytes(), before)
        loader = self.loader(engine)
        with patch.object(loader._Engine, "execute") as executed:
            with self.assertRaises((ValueError, OSError)):
                loader._load_owner()
        executed.assert_not_called()
        self.assertFalse(marker.exists())

    def test_same_byte_hardlink_and_ancestor_alias_refuse(self):
        for kind in ("hardlink", "ancestor"):
            with self.subTest(kind=kind):
                engine = self.engine(kind)
                if kind == "hardlink":
                    path = engine / "scripts/work-graph-completion.py"
                    copied = engine / "other-completion.py"
                    path.rename(copied)
                    os.link(copied, path)
                else:
                    target = self.base / "foreign-skills"
                    (engine / "skills").rename(target)
                    (engine / "skills").symlink_to(target, target_is_directory=True)
                with self.assertRaises((ValueError, OSError)):
                    self.loader(engine)._load_owner()

    def test_direct_helper_import_cannot_infer_executed_buffer(self):
        engine = self.engine()
        helper = engine / "scripts/work-graph-readme-effect.py"
        captured = helper.read_bytes()
        code = compile(captured, str(helper), "exec")
        helper.write_bytes(captured + b"\n# changed after capture before execution\n")
        module = types.ModuleType("old_unowned_effect_buffer")
        module.__file__ = str(helper)
        with self.assertRaisesRegex(ValueError, "owning loader source capture"):
            exec(code, module.__dict__)
        self.assertNotIn("EffectSession", module.__dict__)

    def test_changed_helper_after_capture_refuses_without_renaming(self):
        engine = self.engine()
        loader = self.loader(engine)
        original = loader._Engine.execute
        captured = []
        def changed(instance, name):
            if name == loader.HELPER:
                data = instance.sources[name][0]
                captured.append(hashlib.sha256(data).hexdigest())
                (engine / name).write_bytes(data + b"\n# changed after fixed capture\n")
            return original(instance, name)
        with patch.object(loader._Engine, "execute", changed):
            with self.assertRaisesRegex(ValueError, "no longer current"):
                loader._load_owner()
        self.assertEqual(captured, [loader.PINS[loader.HELPER]])
        self.assertNotEqual(hashlib.sha256((engine / loader.HELPER).read_bytes()).hexdigest(), captured[0])

    def test_compiler_replaced_after_gate_does_not_execute_new_bytes(self):
        engine = self.engine()
        loader = self.loader(engine)
        real_module = types.ModuleType
        markers = []
        def replacing(name):
            module = real_module(name)
            if name == "_readme_fixed_qualify_work_graph_verifier":
                markers.append(self.compiler_marker(engine))
            return module
        scoped_types = types.SimpleNamespace(ModuleType=replacing, MappingProxyType=types.MappingProxyType)
        with patch.object(loader, "types", scoped_types):
            with self.assertRaisesRegex(ValueError, "no longer current"):
                loader._load_owner()
        self.assertEqual(len(markers), 1)
        self.assertFalse(markers[0].exists())

    def test_completion_pin_refuses_unknown_compiler_before_execution(self):
        engine = self.engine()
        owner = load(engine / "scripts/work-graph-readme-effect.py")
        marker = self.compiler_marker(engine)
        with self.assertRaisesRegex(ValueError, "required source digest"):
            owner.C._Compiler(expected_sha256=owner.ENGINE_PINS[owner.COMPILER])
        self.assertFalse(marker.exists())

    def test_completion_executes_checked_capture_then_refuses_race(self):
        engine = self.engine()
        owner = load(engine / "scripts/work-graph-readme-effect.py")
        real_module = types.ModuleType
        markers = []
        def replacing(name):
            module = real_module(name)
            markers.append(self.compiler_marker(engine))
            return module
        with patch.object(owner.C, "types", types.SimpleNamespace(ModuleType=replacing)):
            with self.assertRaisesRegex(ValueError, "executed compiler source changed"):
                owner.C._Compiler(expected_sha256=owner.ENGINE_PINS[owner.COMPILER])
        self.assertEqual(len(markers), 1)
        self.assertFalse(markers[0].exists())

    def test_qualifier_checks_pin_on_its_actual_compiler_capture(self):
        engine = self.engine()
        loader = self.loader(engine)
        compiler = (engine / loader.COMPILER).read_bytes()
        marker = self.compiler_marker(engine)
        changed = (engine / loader.COMPILER).read_bytes()
        qualifier = engine / loader.QUALIFIER
        raw = qualifier.read_bytes()
        module = types.ModuleType("invalid_private_capture")
        module.__file__ = str(qualifier)
        module._R0035_EFFECT_SOURCE_CAPTURE = dict(driver=raw, compiler=changed,
            expected_compiler_sha256=hashlib.sha256(compiler).hexdigest())
        with self.assertRaisesRegex(ValueError, "invalid fixed-loader compiler source capture"):
            exec(compile(raw, str(qualifier), "exec"), module.__dict__)
        self.assertFalse(marker.exists())

    def test_exact_capture_and_independent_installation_have_separate_owners(self):
        first = load(self.owner_path)
        engine = self.engine()
        second = load(engine / "scripts/work-graph-readme-effect.py")
        self.assertEqual(first.LOADED_HELPER, OWNER.read_bytes())
        self.assertEqual(second.LOADED_HELPER, first.LOADED_HELPER)
        self.assertEqual(first.Q.DRIVER_SOURCE_IDENTITY, "CAPTURED_EXECUTED_BUFFER")
        self.assertEqual(second.Q.DRIVER_SOURCE_IDENTITY, "CAPTURED_EXECUTED_BUFFER")
        self.assertEqual(first.Q.LOADED_DRIVER, H.original(first.QUALIFIER))
        self.assertEqual(second.Q.LOADED_DRIVER_PATH, engine / second.QUALIFIER)
        self.assertEqual(second.Q.LOADED_COMPILER_PATH, engine / second.COMPILER)
        self.assertIsNot(first.Q, second.Q)
        self.assertIsNot(first.C, second.C)
        self.assertIsNot(first.P, second.P)
        session = second.EffectSession(self.source, self.base / "evidence")
        self.addCleanup(session.close)
        record = json.loads((session.output / "session.json").read_bytes())
        self.assertEqual(record["engine"][second.HELPER], hashlib.sha256(second.LOADED_HELPER).hexdigest())
        self.assertEqual(record["engine"][second.QUALIFIER], hashlib.sha256(second.Q.LOADED_DRIVER).hexdigest())
        self.assertNotIn("scripts/load-work-graph-readme-effect.py", record["engine"])
        session._custody()
        self.assertEqual(session.dispatch_count, 0)

    def test_fixed_loader_execution_has_no_supplied_source_parameters(self):
        engine = self.engine()
        loader = self.loader(engine)
        captured = loader._Engine()
        marker = self.base / "SUPPLIED_COMPILER_EXECUTED"
        compiler = captured.sources[loader.COMPILER][0] + (
            "\nfrom pathlib import Path as _ProbePath\n_ProbePath(" + repr(str(marker)) +
            ").write_text('supplied compiler executed')\n").encode()
        supplied = {"_R0035_EFFECT_SOURCE_CAPTURE": dict(driver=captured.sources[loader.QUALIFIER][0],
            compiler=compiler, expected_compiler_sha256=hashlib.sha256(compiler).hexdigest())}
        with self.assertRaises(TypeError):
            captured.execute(loader.QUALIFIER, supplied)
        self.assertFalse(marker.exists())

    def test_public_factory_has_no_source_result_or_callback_import(self):
        loader, _ = load_module(LOADER)
        for supplied in (dict(source=b"unknown"), dict(result={"exit": 0}), dict(callback=lambda: None),
                         dict(compiler_sha256="0" * 64), dict(accepted=["README_GENERATE"])):
            with self.subTest(keys=list(supplied)), self.assertRaises(TypeError):
                loader.create_session(self.source, self.base / "evidence", **supplied)


class AdmissionCases(EffectFixture, unittest.TestCase):
    def test_literal_source_population_and_data_change_are_acquired(self):
        owner = load(self.owner_path)
        objects = {}
        first, stamps = owner.snapshot_source(self.source, objects)
        self.assertEqual(set(first["files"]), set((*SUBJECTS, "scripts/verify-package.sh")))
        self.assertIn(".", stamps)
        for name, record in first["files"].items():
            self.assertEqual(objects[record["sha256"]], (self.source / name).read_bytes())
        path = self.source / "docs/diagrams/tooling-architecture.mmd"
        path.write_bytes(path.read_bytes() + b"\n%% actual input changed\n")
        second, _ = owner.snapshot_source(self.source, {})
        self.assertNotEqual(first, second)

    def test_changed_program_or_registry_refuses_before_launch(self):
        session = self.owner_session()
        # This source-admission control has no runtime-observer claim. Preserve
        # the real source checks, and fail if any input reaches runtime/dispatch.
        with (patch.object(session, "_observer", return_value=sentinel.source_admission_only),
              patch.object(self.owner.P, "acquire_runtime", side_effect=AssertionError(
                  "effect source-admission fixture reached runtime acquisition")),
              patch.object(session, "_execution", side_effect=AssertionError(
                  "effect source-admission fixture reached dispatch")),
              patch.object(session, "_execute", side_effect=AssertionError(
                  "effect source-admission fixture reached executor"))):
            for name in ("scripts/generate-readme-diagrams.sh", "scripts/verify-package.sh"):
                path = self.source / name
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "program or registry"):
                    session.step()
                path.write_bytes(original)
            with self.assertRaisesRegex(AssertionError, "runtime acquisition"):
                session.step()
        self.assertEqual(session.dispatch_count, 0)
        self.assertEqual(session._issued, {})
        self.assertIsNone(session._contract)
        self.assertFalse((session.output / "objects").exists())
        self.assertEqual(list(session.output.rglob("result.json")), [])

    def test_missing_linked_oversized_and_expanding_data_refuse(self):
        owner = load(self.owner_path)
        path = self.source / "docs/diagrams/tooling-architecture.mmd"
        original = path.read_bytes()
        outside = self.base / "outside"
        outside.write_bytes(original)
        for kind in ("missing", "symlink", "hardlink", "oversized", "backslash", "marker"):
            path.unlink()
            if kind == "symlink":
                path.symlink_to(outside)
            elif kind == "hardlink":
                os.link(outside, path)
            elif kind == "oversized":
                path.write_bytes(b"x" * (64 * 1024 + 1))
            elif kind == "backslash":
                path.write_bytes(original + b"\nA[\\1]\n")
            elif kind == "marker":
                path.write_bytes(original + b"\n<!-- BEGIN: implementaudit-diagram:execution-spine -->")
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                owner.snapshot_source(self.source, {})
            if path.exists() or path.is_symlink():
                path.unlink()
            path.write_bytes(original)
        readme = self.source / "README.md"
        readme.write_bytes(self.stale + b"x" * (256 * 1024))
        with self.assertRaisesRegex(ValueError, "bound"):
            owner.snapshot_source(self.source, {})

    def test_results_callbacks_and_serialized_capabilities_have_no_import_route(self):
        session = self.owner_session()
        for supplied in (dict(result={"exit": 0}), dict(artifact={"sha256": "a" * 64}),
                         dict(callback=lambda: b"fake"), dict(completed=["README_GENERATE"])):
            with self.subTest(supplied=list(supplied)), self.assertRaises(TypeError):
                session.run(**supplied)
        with self.assertRaisesRegex(ValueError, "no live"):
            session.artifact_bytes()
        self.assertEqual(session.dispatch_count, 0)

    def test_changed_loaded_bootstrap_refuses(self):
        engine = H.copy_readme_engine(self.base / "engine")
        original = load(self.owner_path)
        owner = load(engine / original.HELPER)
        bootstrap = engine / original.BOOTSTRAP
        bootstrap.write_bytes(bootstrap.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "loaded effect source changed"):
            owner.EffectSession(self.source, self.base / "evidence")


@unittest.skipUnless(os.environ.get("R0035_README_EFFECT_LIVE") == "1",
                     "set R0035_README_EFFECT_LIVE=1 for serial actual namespace controls")
class PhysicalHandoffCases(EffectFixture, unittest.TestCase):
    HISTORICAL_FIXTURE = False

    def test_stale_readme_requires_actual_owned_effect_transfer(self):
        # This direct precondition witness is not namespace qualification. The
        # positive below must use the product's existing acquired launcher.
        before = subprocess.run(["/usr/bin/bash", "scripts/generate-readme-diagrams.sh", "--check"],
                                cwd=self.source, capture_output=True,
                                env=dict(PATH="/usr/bin:/bin", LANG="C", LC_ALL="C"))
        self.assertEqual(before.returncode, 1)
        self.assertIn(b"README.md diagrams are stale", before.stderr)
        (self.base / "stale-before.stdout.log").write_bytes(before.stdout)
        (self.base / "stale-before.stderr.log").write_bytes(before.stderr)
        (self.base / "stale-before.exit-code.txt").write_text(str(before.returncode) + "\n")
        self.assertEqual((self.source / "README.md").read_bytes(), self.stale)
        self.assertTrue(OWNER.is_file(), "physical README effect owner is absent after actual stale-check rejection")
        session = self.owner_session()
        producer = session.step()
        self.assertEqual(producer["action"], "README_GENERATE")
        partial = session._contract.join("README_FINAL", expected_old=session._contract.history_digest)
        self.assertEqual(partial["status"], "PENDING")
        self.assertEqual(set(partial["missing"]), {"README_OUTPUT", "README_CHECK"})
        joined = session.step()
        self.assertEqual(joined["action"], "README_OUTPUT")
        partial = session._contract.join("README_FINAL", expected_old=session._contract.history_digest)
        self.assertEqual(partial["missing"], ["README_CHECK"])
        consumed = session.step()
        self.assertEqual(consumed["action"], "README_CHECK")
        self.assertEqual(consumed["status"], "PENDING")
        result = session.step()
        self.assertEqual(result["status"], "SATISFIED_AT_PORTABLE_EFFECT_CONTRACT")
        self.assertEqual(result["dispatch_count"], 2)
        self.assertNotEqual(session.artifact_bytes(), self.stale)
        self.assertEqual((self.source / "README.md").read_bytes(), self.stale)
        first = result["artifact_sha256"]
        second = session.run()
        self.assertEqual(second["artifact_sha256"], first)
        self.assertEqual(second["dispatch_count"], 2)
        self.assertEqual(second["disposition"], "REUSED")
        executions = sorted(session.output.glob("generation-*/execution"))
        self.assertEqual(len(executions), 2)
        original_stdout = (executions[0] / "producer.stdout.log").read_bytes()
        self.assertEqual(original_stdout, b"generate-readme-diagrams: updated README.md\n")
        self.assertEqual((executions[1] / "stdout.log").read_bytes(), b"generate-readme-diagrams: check ok\n")
        image = json.loads((executions[1] / "image.json").read_bytes())
        mounted = next(m for m in image["files"] if m["path"] == "/work/README.md")
        self.assertEqual(mounted["sha256"], first)
        self.assertEqual(mounted["mode"], 0o444)
        dispatch = json.loads((executions[1] / "dispatch.json").read_bytes())
        self.assertEqual(dispatch["node"], "COMMAND:scripts/generate-readme-diagrams.sh:0")
        self.assertEqual(dispatch["command"], "bash scripts/generate-readme-diagrams.sh --check\n")
        self.assertFalse(result["native_dispatch_authorized"])
        self.assertNotEqual(result["states"]["README_ROOT"], "DONE")

    def test_actual_original_checker_rejects_no_transfer_image(self):
        session = self.owner_session()
        start = session._acquire()
        files = {name: (start["objects"][entry["sha256"]], entry["mode"])
                 for name, entry in start["runtime"]["files"].items()}
        files.update({"/work/" + name: ((self.source / name).read_bytes(), 0o444) for name in SUBJECTS})
        files["/work/" + self.owner.RUNNER] = ((ROOT / self.owner.RUNNER).read_bytes(), 0o555)
        manifest, key = session._image(files, start["state"])
        node = start["checker"]
        acquired = dict(start, images={node["id"]: (files, manifest)},
                        acquired=dict(start["acquired"], inputs={node["id"]: dict(image_digest=key)}))
        receipt, retained = self.owner.Q.VerifierTaskSession._execute(
            session, acquired, node, {"key": start["key"]}, session.output / "no-transfer-control")
        self.assertEqual(receipt["exit"], 1)
        self.assertTrue(receipt["complete"])
        self.assertIn(b"README.md diagrams are stale", retained["retained"]["stderr.log"])
        self.assertEqual(session._issued, {})
        self.assertIsNone(session._artifact)

    def test_fresh_diagram_change_refuses_stale_successor_before_dispatch(self):
        session = self.owner_session()
        session.step()
        session.step()
        path = self.source / "docs/diagrams/tooling-architecture.mmd"
        path.write_bytes(path.read_bytes() + b"\n%% changed after real producer\n")
        with self.assertRaisesRegex(ValueError, "current source/runtime changed"):
            session.step()
        self.assertEqual(session.dispatch_count, 1)
        self.assertNotIn("README_CHECK", session._issued)

    def corrupt_output(self, kind):
        session = self.owner_session()
        session.step()
        artifact = session.output / "objects" / session._artifact["sha256"]
        if kind == "missing":
            artifact.unlink()
        elif kind == "modified":
            artifact.chmod(0o600)
            artifact.write_bytes(b"foreign replacement bytes\n")
            artifact.chmod(0o400)
        elif kind == "projection":
            path = session.output / "inputs/artifact/README.md"
            path.chmod(0o600)
            path.write_bytes(self.stale)
            path.chmod(0o400)
        elif kind == "capability":
            session._artifact["producer"] = "foreign producer"
        (self.base / "mutation.json").write_text(json.dumps(dict(kind=kind, expected=artifact.name)))
        with self.assertRaises((ValueError, OSError)):
            session.step()
        self.assertEqual(session.dispatch_count, 1)

    def test_missing_owned_output_refuses(self):
        self.corrupt_output("missing")

    def test_modified_owned_output_refuses(self):
        self.corrupt_output("modified")

    def test_modified_projection_refuses(self):
        self.corrupt_output("projection")

    def test_foreign_capability_identity_refuses(self):
        self.corrupt_output("capability")

    def test_foreign_process_cannot_use_live_artifact(self):
        session = self.owner_session()
        session.step()
        readfd, writefd = os.pipe()
        child = os.fork()
        if child == 0:
            os.close(readfd)
            try:
                session.step()
                message = b"UNEXPECTED_ACCEPT"
            except ValueError as error:
                message = str(error).encode()
            os.write(writefd, message)
            os._exit(0)
        os.close(writefd)
        message = os.read(readfd, 4096)
        os.close(readfd)
        self.assertEqual(os.waitpid(child, 0)[1], 0)
        self.assertIn(b"producer process changed", message)
        self.assertEqual(session.dispatch_count, 1)

    def test_original_producer_failure_never_issues_completion(self):
        path = self.source / "docs/diagrams/tooling-architecture.mmd"
        path.write_bytes(path.read_bytes().replace(b"flowchart TB", b"flowchart LR", 1))
        session = self.owner_session()
        with self.assertRaisesRegex(ValueError, "actual task failed"):
            session.step()
        execution = next(session.output.glob("generation-*/execution"))
        raw = (execution / "stdout.log").read_bytes()
        frame, streams, artifact = self.owner.decode_frame(raw)
        self.assertEqual(frame["exit"], 1)
        self.assertIn(b"must retain its qualified GitHub README layout", streams["stderr"])
        self.assertIsNone(artifact)
        self.assertEqual((execution / "exit-code.txt").read_bytes(), b"1\n")
        self.assertEqual(session._issued, {})
        self.assertIsNone(session._artifact)
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def stop_actual_launch(self, session, interrupt=False):
        real_popen = self.owner.Q.subprocess.Popen
        def stopped(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            command = args[0] if args else kwargs.get("args")
            # subprocess is shared with platform: never stop its uname probe.
            if not isinstance(command, (list, tuple)) or not command or command[0] != "/usr/bin/bwrap":
                return process
            self._stopped_pid = process.pid
            os.killpg(process.pid, signal.SIGSTOP)
            if interrupt:
                real_wait = process.wait
                first = [True]
                def interrupted(*wait_args, **wait_kwargs):
                    if first[0]:
                        first[0] = False
                        raise KeyboardInterrupt("test interrupts actual owner wait")
                    return real_wait(*wait_args, **wait_kwargs)
                process.wait = interrupted
            return process
        return patch.object(self.owner.Q.subprocess, "Popen", stopped)

    def test_actual_timeout_keeps_exit_and_cannot_issue_artifact(self):
        session = self.owner_session()
        # Tighten only the test session's wall budget to a supported integer.
        # Canonical acquisition deliberately refuses float-valued budgets.
        # Namespace, source and existing owner termination remain unchanged.
        session.LIMITS = dict(session.LIMITS, wall_seconds=1)
        with self.stop_actual_launch(session):
            with self.assertRaisesRegex(ValueError, "actual task failed or was incomplete"):
                session.step()
        execution = next(session.output.glob("generation-*/execution"))
        receipt = json.loads((execution / "receipt.json").read_bytes())
        self.assertFalse(receipt["complete"])
        self.assertEqual(receipt["exit"], -signal.SIGKILL)
        self.assertEqual((execution / "exit-code.txt").read_bytes(), b"-9\n")
        with self.assertRaises(ChildProcessError):
            os.waitpid(self._stopped_pid, os.WNOHANG)
        (self.base / "owned-process.json").write_text(json.dumps(dict(
            pid=self._stopped_pid, actual_exit=-signal.SIGKILL, reaped=True)))
        self.assertIsNone(session._artifact)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_interruption_keeps_exit_and_cannot_resume(self):
        session = self.owner_session()
        with self.stop_actual_launch(session, interrupt=True):
            with self.assertRaises(KeyboardInterrupt):
                session.step()
        execution = next(session.output.glob("generation-*/execution"))
        self.assertEqual((execution / "exit-code.txt").read_bytes(), b"-9\n")
        with self.assertRaises(ChildProcessError):
            os.waitpid(self._stopped_pid, os.WNOHANG)
        (self.base / "owned-process.json").write_text(json.dumps(dict(
            pid=self._stopped_pid, actual_exit=-signal.SIGKILL, reaped=True)))
        self.assertFalse((execution / "receipt.json").exists())
        self.assertIsNone(session._artifact)
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)


if __name__ == "__main__":
    unittest.main()
