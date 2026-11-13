#!/usr/bin/env python3
"""Real-shell controls for the shell-to-companion executed-buffer boundary.

The interpreter audit/trace hook observes actual compiled and executing code;
it supplies no continuity, receipt, native, or effect authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(os.environ.get("SHELL_CUSTODY_SOURCE") or
              Path(__file__).resolve().parents[1] / "skills/implementaudit/scripts")
WORK = Path(os.environ.get("SHELL_CUSTODY_WORK") or tempfile.gettempdir())
EVIDENCE = os.environ.get("SHELL_CUSTODY_EVIDENCE")
MEMBERS = ("claim-run.sh", "claim-run-rotation.py", "canonical_custody.py",
           "canonical_hot_projection.py", "canonical_rotation_inputs.py",
           "rotate-canonical-state.py", "validate-run-root.sh", "read-canonical-pair.py",
           "validate-phase.sh", "check-respec-impact-set.sh")
MARKER = "EXECUTED_UNSELECTED_COMPANION"

OBSERVER = r'''
import hashlib, json, os, sys
from pathlib import Path
target = os.environ["SHELL_OBSERVER_TARGET"]
log = Path(os.environ["SHELL_OBSERVER_LOG"])
drift = os.environ.get("SHELL_OBSERVER_DRIFT") == "1"
changed = False
def record(value):
    with log.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")
def trace(frame, event, arg):
    if frame.f_code.co_filename == target and frame.f_code.co_name == "<module>" and event == "call":
        record({"event": "module", "file": frame.f_globals.get("__file__"),
                "name": frame.f_globals.get("__name__"), "argv": sys.argv,
                "package": frame.f_globals.get("__package__"),
                "main_identity": sys.modules["__main__"].__dict__ is frame.f_globals,
                "import_path": sys.path[0], "stdin": sys.stdin.read()})
    return trace
def audit(event, args):
    global changed
    if event == "compile" and args[1] == target:
        source = args[0]
        if isinstance(source, str):
            source = source.encode()
        record({"event": "compile", "sha256": hashlib.sha256(source).hexdigest(), "bytes": len(source)})
        if drift and not changed:
            changed = True
            marker = b'print("EXECUTED_UNSELECTED_COMPANION", flush=True)\nraise SystemExit(0)\n'
            Path(target).write_bytes(marker + b"#" * (len(source) - len(marker)))
    elif event == "exec" and args[0].co_filename == target:
        sys.settrace(trace)
sys.addaudithook(audit)
'''

BINDER_OBSERVER = r'''
import os, sys
from pathlib import Path
target = Path(os.environ["SHELL_OBSERVER_TARGET"])
log = Path(os.environ["SHELL_OBSERVER_LOG"])
kind = os.environ["SHELL_BINDER_REPLACEMENT"]
function = os.environ["SHELL_CAPTURE_FUNCTION"]
armed = True
def audit(event, args):
    global armed
    if event != "open" or not armed or args[0] != str(target):
        return
    frame = sys._getframe()
    while frame and frame.f_code.co_name != function:
        frame = frame.f_back
    if frame is None:
        return
    armed = False
    retained = target.with_suffix(".retained")
    target.rename(retained)
    if kind == "fifo":
        os.mkfifo(target, 0o600)
    elif kind == "regular":
        target.write_bytes(retained.read_bytes())
    elif kind == "symlink":
        target.symlink_to(retained)
    else:
        raise AssertionError(kind)
    log.write_text("POST_LSTAT_BINDER_REPLACEMENT:" + kind)
sys.addaudithook(audit)
'''


class CompanionIdentityPredicate(unittest.TestCase):
    """Constructed metadata controls of selected source AST, never native host proof."""
    def guard(self, platform='win32', version=(3, 12, 10), os_name='nt', implementation='cpython'):
        import ast
        import copy
        import types
        text = (SOURCE / 'claim-run.sh').read_text()
        marker = '  "$rotation_py" -B -c \'\n'
        suffix = '\n\' "$(dirname "$0")/claim-run-rotation.py" "$@"'
        self.assertEqual(text.count(marker), 1)
        self.assertEqual(text.count(suffix), 1)
        tree = ast.parse(text.split(marker, 1)[1].split(suffix, 1)[0])
        definitions = [copy.deepcopy(n) for n in tree.body if isinstance(n, ast.FunctionDef)
                       and n.name in ('identity', 'cross_api_identity')]
        predicates = [copy.deepcopy(n) for n in ast.walk(tree) if isinstance(n, ast.If)
                      and len(n.body) == 1 and isinstance(n.body[0], ast.Raise)
                      and isinstance(n.body[0].exc, ast.Call)
                      and len(n.body[0].exc.args) == 1
                      and isinstance(n.body[0].exc.args[0], ast.Constant)
                      and n.body[0].exc.args[0].value == 'identity changed during bounded capture']
        self.assertEqual(len(predicates), 1)
        wrapper = ast.parse('def guarded(before, opened, after, current):\n    return True\n').body[0]
        wrapper.body = predicates + wrapper.body
        module = ast.fix_missing_locations(ast.Module(body=definitions + [wrapper], type_ignores=[]))
        namespace = dict(os=types.SimpleNamespace(name=os_name),
                         sys=types.SimpleNamespace(platform=platform, version_info=version,
                                                   implementation=types.SimpleNamespace(name=implementation)))
        exec(compile(module, '<selected-capture-predicate>', 'exec'), namespace)
        return namespace['guarded']

    def rows(self, split=True):
        from types import SimpleNamespace
        # Constructed birth/change times model the documented API difference.
        base = dict(st_dev=1, st_ino=2, st_mode=0o100644, st_nlink=1, st_size=10,
                    st_ctime_ns=100, st_mtime_ns=200, st_birthtime_ns=100, st_file_attributes=32)
        rows = [SimpleNamespace(**base) for _ in range(4)]
        if split:
            rows[1].st_ctime_ns = rows[2].st_ctime_ns = 200
        return rows

    def test_windows_api_difference_preserves_both_mutation_checks(self):
        guard = self.guard()
        self.assertTrue(guard(*self.rows()))
        self.assertTrue(guard(*self.rows(False)))
        for position in range(4):
            for field in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size',
                          'st_ctime_ns', 'st_mtime_ns', 'st_birthtime_ns', 'st_file_attributes'):
                rows = self.rows()
                setattr(rows[position], field, getattr(rows[position], field) + 1)
                with self.subTest(position=position, field=field), self.assertRaisesRegex(ValueError, 'identity changed'):
                    guard(*rows)

    def test_unqualified_runtime_retains_strict_chain(self):
        contexts = [dict(os_name='posix', platform='linux'), dict(version=(3, 12, 9)),
                    dict(version=(3, 13, 0)), dict(platform='cygwin'), dict(implementation='pypy')]
        for context in contexts:
            guard = self.guard(**context)
            self.assertTrue(guard(*self.rows(False)))
            with self.subTest(context=context), self.assertRaisesRegex(ValueError, 'identity changed'):
                guard(*self.rows())

    def test_required_windows_metadata_refuses_missing_and_wrong_types(self):
        guard = self.guard()
        for position in range(4):
            for field in ('st_birthtime_ns', 'st_file_attributes'):
                for value in (None, True, 1.5, '32'):
                    rows = self.rows()
                    setattr(rows[position], field, value)
                    with self.subTest(position=position, field=field, value=value), \
                            self.assertRaisesRegex(ValueError, 'metadata is unavailable'):
                        guard(*rows)
                rows = self.rows()
                delattr(rows[position], field)
                with self.assertRaisesRegex(ValueError, 'metadata is unavailable'):
                    guard(*rows)


class ShellCompanionSourceCustody(unittest.TestCase):
    def setUp(self):
        WORK.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="shell-custody-", dir=WORK)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).absolute()
        self.cwd = self.root / "caller directory"
        self.cwd.mkdir()
        self.scripts = self.layout("source layout", "skills/implementaudit/scripts")
        self.companion = self.scripts / "claim-run-rotation.py"
        self.original = self.companion.read_bytes()
        self.calls = 0

    def layout(self, label, relative):
        scripts = self.root / label / relative
        scripts.mkdir(parents=True)
        for name in MEMBERS:
            if (SOURCE / name).is_file():
                shutil.copyfile(SOURCE / name, scripts / name)
        shutil.copytree(SOURCE.parent / 'templates', scripts.parent / 'templates')
        return scripts

    def invoke(self, scripts=None, *, args=None, extra_env=None, input_bytes=b"", timeout=20):
        scripts = self.scripts if scripts is None else scripts
        args = ["--resolve-canonical-generation", "invalid?controller"] if args is None else args
        environment = {"PATH": os.environ["PATH"], "LC_ALL": "C.UTF-8",
                       "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1",
                       "GIT_NO_LAZY_FETCH": "1", "GIT_CONFIG_NOSYSTEM": "1",
                       "GIT_CONFIG_GLOBAL": os.devnull}
        environment.update(extra_env or {})
        # Windows CreateProcess searches System32 before PATH for a bare name;
        # resolve the selected shell instead of accidentally starting WSL bash.
        for key in ("SystemRoot", "TEMP", "TMP"):
            if key in os.environ:
                environment[key] = os.environ[key]
        bash = shutil.which("bash")
        if bash is None:
            self.fail("bash is required for shell custody controls")
        command = [bash, (scripts / "claim-run.sh").as_posix(), *args]
        process = subprocess.Popen(command, cwd=self.cwd, env=environment,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=os.name == "posix")
        try:
            stdout, stderr = process.communicate(input=input_bytes, timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            stdout, stderr = process.communicate()
            self.fail("shell companion blocked; owned process group killed/reaped; stdout=%r stderr=%r"
                      % (stdout, stderr))
        result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        self.calls += 1
        if EVIDENCE:
            dest = Path(EVIDENCE) / self._testMethodName / str(self.calls)
            dest.mkdir(parents=True, exist_ok=True)
            (dest / "stdout.bin").write_bytes(result.stdout)
            (dest / "stderr.bin").write_bytes(result.stderr)
            (dest / "receipt.json").write_text(json.dumps({
                "argv": command, "cwd": str(self.cwd), "returncode": result.returncode,
                "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
                "shell_sha256": hashlib.sha256((scripts / "claim-run.sh").read_bytes()).hexdigest(),
            }, indent=2) + "\n")
        return result

    def changed_source(self, length=None):
        length = len(self.original) if length is None else length
        payload = ('print("' + MARKER + '", flush=True)\nraise SystemExit(0)\n').encode()
        self.assertGreater(length, len(payload))
        return payload + b"#" * (length - len(payload))

    def assert_loader_refusal(self, result):
        self.assertEqual(result.returncode, 1, result.stdout.decode() + result.stderr.decode())
        self.assertNotIn(MARKER.encode(), result.stdout + result.stderr)
        self.assertIn(b"claim-run.sh: companion source", result.stderr)

    def assert_actual_companion(self, result):
        self.assertEqual(result.returncode, 1, result.stderr.decode())
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, ("claim-run.sh: controller identity is invalid" + os.linesep).encode())

    def observe(self, *, drift=False):
        observer = self.root / "observer"
        observer.mkdir()
        (observer / "sitecustomize.py").write_text(OBSERVER)
        log = self.root / "interpreter-observations.jsonl"
        env = {"PYTHONPATH": str(observer), "SHELL_OBSERVER_TARGET": str(self.companion),
               "SHELL_OBSERVER_LOG": str(log), "SHELL_OBSERVER_DRIFT": str(int(drift))}
        result = self.invoke(extra_env=env, input_bytes=b"preserved stdin\n")
        records = [json.loads(line) for line in log.read_text().splitlines()]
        if EVIDENCE:
            dest = Path(EVIDENCE) / self._testMethodName
            shutil.copyfile(log, dest / "interpreter-observations.jsonl")
        return result, records

    def test_same_size_unselected_companion_is_not_executed(self):
        # A same-size source substitution must fail before any substituted code.
        self.companion.write_bytes(self.changed_source())
        self.assert_loader_refusal(self.invoke())

    def test_exact_companion_executes_in_both_package_layouts(self):
        # A loader that loses __file__, __name__, or argv cannot reach this error.
        self.assert_actual_companion(self.invoke())
        standalone = self.layout("standalone layout", "scripts")
        self.assert_actual_companion(self.invoke(standalone))

    def test_wrong_lengths_and_missing_source_are_refused(self):
        for length in (len(self.original) - 1, len(self.original) + 1):
            with self.subTest(length=length):
                self.companion.write_bytes(self.changed_source(length))
                self.assert_loader_refusal(self.invoke())
        self.companion.unlink()
        self.assert_loader_refusal(self.invoke())

    def test_hardlinked_companion_is_refused(self):
        os.link(self.companion, self.scripts / "companion.alias")
        self.assert_loader_refusal(self.invoke())

    @unittest.skipUnless(os.name == "posix", "native POSIX alias case")
    def test_symlinked_companion_is_refused(self):
        physical = self.scripts / "companion.physical"
        self.companion.rename(physical)
        self.companion.symlink_to(physical)
        self.assert_loader_refusal(self.invoke())

    @unittest.skipUnless(os.name == "posix", "native POSIX ancestor alias case")
    def test_symlinked_source_directory_is_refused(self):
        alias = self.root / "aliased source directory"
        alias.symlink_to(self.scripts, target_is_directory=True)
        self.assert_loader_refusal(self.invoke(alias))

    def test_caller_directory_cannot_select_companion_or_bootstrap_import(self):
        # Invocation cwd is unrelated to the source-owner sibling selection.
        (self.cwd / "claim-run-rotation.py").write_bytes(self.changed_source())
        (self.cwd / "hashlib.py").write_text('print("' + MARKER + '")\nraise SystemExit(0)\n')
        self.assert_actual_companion(self.invoke())

    def test_real_main_module_args_path_import_path_and_stdin_are_preserved(self):
        result, records = self.observe()
        self.assert_actual_companion(result)
        compiled = [row for row in records if row["event"] == "compile"]
        self.assertGreaterEqual(len(compiled), 1)
        self.assertEqual(compiled[0]["bytes"], len(self.original))
        self.assertEqual(compiled[0]["sha256"], hashlib.sha256(self.original).hexdigest())
        modules = [row for row in records if row["event"] == "module"]
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0], {"event": "module", "file": str(self.companion),
                         "name": "__main__", "argv": [self.companion.as_posix(), "resolve", "invalid?controller"],
                         "package": None, "main_identity": True,
                         "import_path": str(self.scripts), "stdin": "preserved stdin\n"})

    def test_capture_to_compile_path_change_never_executes_replacement(self):
        result, records = self.observe(drift=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(MARKER.encode(), result.stdout + result.stderr)
        compiled = [row for row in records if row["event"] == "compile"]
        self.assertEqual(compiled[0]["sha256"], hashlib.sha256(self.original).hexdigest())
        self.assertEqual(len([row for row in records if row["event"] == "module"]), 1)
        self.assertIn(b"executing claim code differs from the physical load snapshot", result.stderr)
        self.assertEqual(self.companion.read_bytes(), self.changed_source())

    def binder_replacement(self, kind, *, substrate=False):
        observer = self.root / "binder-observer"
        observer.mkdir()
        (observer / "sitecustomize.py").write_text(BINDER_OBSERVER)
        log = self.root / "binder-boundary.log"
        target = self.scripts / "canonical_custody.py" if substrate else self.companion
        result = self.invoke(extra_env={"PYTHONPATH": str(observer),
            "SHELL_OBSERVER_TARGET": str(target), "SHELL_OBSERVER_LOG": str(log),
            "SHELL_CAPTURE_FUNCTION": "_windows_custody" if substrate else "_capture_claim_load_identity_v1",
            "SHELL_BINDER_REPLACEMENT": kind}, timeout=5)
        self.assertEqual(log.read_text(), "POST_LSTAT_BINDER_REPLACEMENT:" + kind)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertNotIn(b"controller identity is invalid", result.stderr)
        self.assertNotIn(MARKER.encode(), result.stdout + result.stderr)
        return result

    @unittest.skipUnless(os.name == "posix", "actual POSIX FIFO replacement")
    def test_initial_binder_fifo_replacement_refuses_without_blocking(self):
        self.assertIn(b"executing claim code source changed", self.binder_replacement("fifo").stderr)

    def test_initial_binder_equal_byte_replacement_refuses(self):
        self.assertIn(b"executing claim code source changed", self.binder_replacement("regular").stderr)

    @unittest.skipUnless(os.name == "posix", "actual POSIX source alias")
    def test_initial_binder_symlink_replacement_refuses(self):
        self.binder_replacement("symlink")

    @unittest.skipUnless(os.name == "posix", "actual POSIX substrate FIFO replacement")
    def test_substrate_fifo_replacement_refuses_without_blocking(self):
        self.assertIn(b"canonical custody substrate source identity mismatch",
                      self.binder_replacement("fifo", substrate=True).stderr)

    def test_substrate_equal_byte_replacement_refuses(self):
        self.assertIn(b"canonical custody substrate source identity mismatch",
                      self.binder_replacement("regular", substrate=True).stderr)

    @unittest.skipUnless(os.name == "posix", "actual POSIX substrate alias")
    def test_substrate_symlink_replacement_refuses(self):
        self.binder_replacement("symlink", substrate=True)

    def test_unselected_substrate_bytes_do_not_execute(self):
        path = self.scripts / "canonical_custody.py"
        path.write_bytes(path.read_bytes() + ('\nprint("' + MARKER + '")\n').encode())
        result = self.invoke()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(MARKER.encode(), result.stdout + result.stderr)
        self.assertIn(b"canonical custody substrate source identity mismatch", result.stderr)

    def test_rotation_uses_available_python_before_later_python3_alias(self):
        selected = self.root / "interpreter-bin"
        selected.mkdir()
        (selected / "python3").write_text("#!/usr/bin/env bash\nprintf 'UNSELECTED_PYTHON3_ALIAS\\n'\nexit 79\n")
        for path in selected.iterdir():
            path.chmod(0o755)
        if os.name == "posix":
            (selected / "python").symlink_to(sys.executable)
            prefix = str(selected)
        else:
            prefix = str(Path(sys.executable).parent) + os.pathsep + str(selected)
        result = self.invoke(extra_env={"PATH": prefix + os.pathsep + os.environ["PATH"]})
        self.assertNotIn(b"UNSELECTED_PYTHON3_ALIAS", result.stdout + result.stderr)
        self.assert_actual_companion(result)

    def interpreter_traps(self):
        selected = self.root / "installer-traps"
        selected.mkdir()
        marker = selected / "INVOKED_INSTALLER"
        for name in ("python", "python3", "py"):
            path = selected / name
            path.write_text("#!/usr/bin/env bash\nprintf invoked > " + shlex.quote(marker.as_posix())
                            + "\nprintf 'UNQUALIFIED_INSTALLER_INVOKED\\n'\nexit 79\n")
            path.chmod(0o755)
        return selected, marker

    def assert_interpreter_refusal(self, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"supported physical Python 3 interpreter is required", result.stderr)

    def test_installer_wrappers_and_launcher_are_refused_without_invocation(self):
        selected, marker = self.interpreter_traps()
        result = self.invoke(extra_env={"PATH": str(selected) + os.pathsep + os.environ["PATH"]})
        self.assertFalse(marker.exists(), "an unqualified interpreter/launcher was invoked")
        self.assert_interpreter_refusal(result)

    def test_explicit_missing_relative_empty_and_script_interpreters_refuse(self):
        selected, marker = self.interpreter_traps()
        for value in ("", "python3", str(selected / "absent"), str(selected / "python")):
            with self.subTest(value=value):
                self.assert_interpreter_refusal(self.invoke(extra_env={"IMPLEMENTAUDIT_PYTHON": value}))
                self.assertFalse(marker.exists())

    def test_explicit_existing_physical_interpreter_executes_exact_companion(self):
        self.assert_actual_companion(self.invoke(extra_env={"IMPLEMENTAUDIT_PYTHON": sys.executable}))

    @unittest.skipUnless(os.name == "posix", "POSIX genuine python3 fallback")
    def test_unqualified_python_does_not_mask_genuine_python3(self):
        selected, marker = self.interpreter_traps()
        (selected / "python3").unlink()
        (selected / "python3").symlink_to(sys.executable)
        self.assert_actual_companion(self.invoke(extra_env={"PATH": str(selected) + os.pathsep + os.environ["PATH"]}))
        self.assertFalse(marker.exists())

    @unittest.skipUnless(os.name == "nt", "WindowsApps physical-path boundary")
    def test_windowsapps_candidate_is_refused_even_with_python_pe_metadata(self):
        path = self.root / "Microsoft/WindowsApps/python.exe"
        path.parent.mkdir(parents=True)
        shutil.copyfile(sys.executable, path)
        self.assert_interpreter_refusal(self.invoke(extra_env={"IMPLEMENTAUDIT_PYTHON": str(path)}))

    @unittest.skipUnless(os.name == "nt", "Windows PE product metadata boundary")
    def test_foreign_windows_executable_metadata_is_refused(self):
        path = Path(os.environ["SystemRoot"]) / "System32/cmd.exe"
        self.assert_interpreter_refusal(self.invoke(extra_env={"IMPLEMENTAUDIT_PYTHON": str(path)}))

    def test_existing_interpreter_venv_remains_supported_without_pip_or_download(self):
        target = self.root / "venv"
        created = subprocess.run([sys.executable, "-I", "-S", "-m", "venv", "--without-pip", str(target)],
                                 capture_output=True, timeout=30)
        self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
        interpreter = target / ("Scripts/python.exe" if os.name == "nt" else "bin/python3")
        self.assert_actual_companion(self.invoke(extra_env={"IMPLEMENTAUDIT_PYTHON": str(interpreter)}))

    @unittest.skipUnless(sys.platform == "linux", "Linux foreign native executable boundary")
    def test_renamed_foreign_elf_cannot_succeed_at_either_claim_entrypoint(self):
        foreign = self.root / "foreign/python3.12"
        foreign.parent.mkdir()
        shutil.copyfile(shutil.which("true"), foreign)
        foreign.chmod(0o755)
        self.assert_interpreter_refusal(self.invoke(extra_env={"IMPLEMENTAUDIT_PYTHON": str(foreign)}))
        for command in (["git", "init", "-q"], ["git", "-c", "user.name=selector fixture",
                "-c", "user.email=selector@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "--allow-empty", "-qm", "disposable selector fixture"]):
            result = subprocess.run(command, cwd=self.cwd, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.invoke(args=["--controller", "foreign-selector", "new ordinary fixture"],
                             extra_env={"IMPLEMENTAUDIT_PYTHON": str(foreign)})
        self.assertNotEqual(result.returncode, 0, "unqualified executable reported a successful claim")
        refs = subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/implementaudit/"],
                              cwd=self.cwd, capture_output=True, check=True)
        self.assertEqual(refs.stdout, b"")

    @unittest.skipUnless(os.name == "nt", "Windows registered installation boundary")
    def test_unregistered_copy_of_python_exe_is_not_an_installation(self):
        path = self.root / "unregistered/python.exe"
        path.parent.mkdir()
        shutil.copyfile(sys.executable, path)
        self.assert_interpreter_refusal(self.invoke(extra_env={"IMPLEMENTAUDIT_PYTHON": str(path)}))

    def initialize_test_repository(self, label):
        for command in (["git", "init", "-q"], ["git", "-c", "user.name=initialization custody fixture",
                "-c", "user.email=initialization@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "--allow-empty", "-qm", label]):
            result = subprocess.run(command, cwd=self.cwd, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def prepare_activation(self, controller, expected=None):
        args = ['--controller', controller]
        if expected is not None:
            args += ['--supersede-claim', expected]
        result = self.invoke(args=args + ['bounded actual source-custody test'],
                             extra_env={'IMPLEMENTAUDIT_PYTHON': sys.executable})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        relative = result.stdout.decode().strip()
        helper = Path(__file__).resolve().parents[1] / 'fixtures/controller-initialization/author_checkpoint.py'
        authored = subprocess.run([sys.executable, str(helper), '--repo', str(self.cwd),
            '--run-root', relative, '--source', str(self.scripts.parents[2]),
            '--purpose', 'Qualify actual controller publication and interpreter/source custody on this disposable subject.',
            '--next-action', 'Exercise the explicit activation postcondition without original authority or publication'],
            capture_output=True, timeout=30)
        self.assertEqual(authored.returncode, 0, authored.stdout + authored.stderr)
        inspected = self.invoke(args=['--inspect-controller-initialization', controller, '--run-root', relative])
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        token = json.loads(inspected.stdout)['initialization_token']
        return self.cwd / relative, ['--activate-controller', controller, '--run-root', relative,
                                      '--expected-initialization', token]

    def instrument_activation(self, before='', after=''):
        import re
        original = self.companion.read_text()
        anchor = '            result = git_process(repo, "update-ref", "--stdin", "-z", input_bytes=b"".join(chunks))\n'
        self.assertEqual(original.count(anchor), 1)
        active = "any(ref.startswith('refs/implementaudit/controllers/') for ref in updates)"
        if before:
            replacement = '            if ' + active + ':\n' + ''.join('                ' + line + '\n' for line in before.splitlines()) + '            else:\n    ' + anchor
        else:
            replacement = anchor + '            if ' + active + ':\n' + ''.join('                ' + line + '\n' for line in after.splitlines())
        changed = original.replace(anchor, replacement)
        self.assertEqual(changed.replace(replacement, anchor), original)
        self.companion.write_text(changed)
        shell = self.scripts / 'claim-run.sh'
        text = shell.read_text()
        raw = self.companion.read_bytes()
        text = re.sub(r'expected_bytes = [0-9]+', 'expected_bytes = ' + str(len(raw)), text, count=1)
        text = re.sub(r'expected_sha256 = "[0-9a-f]{64}"', 'expected_sha256 = "' + hashlib.sha256(raw).hexdigest() + '"', text, count=1)
        shell.write_text(text)

    def test_successful_interpreter_without_controller_effect_is_not_a_successful_claim(self):
        self.initialize_test_repository('disposable activation postcondition subject')
        marker = self.root / 'interpreter-returned-without-effect'
        self.instrument_activation(before="Path(" + repr(str(marker)) + ").write_text('observed no-effect return')\nresult = types.SimpleNamespace(returncode=0)")
        run, args = self.prepare_activation('postcondition')
        result = self.invoke(args=args)
        self.assertEqual(marker.read_text(), 'observed no-effect return')
        self.assertNotEqual(result.returncode, 0, 'exit zero was mistaken for an absent activation effect')
        self.assertIn(b'publication did not have one exact verified effect', result.stderr)
        self.assertTrue((run / '.claimed').is_file())
        self.assertTrue((run / '.controller').is_file())
        refs = subprocess.run(['git', 'for-each-ref', '--format=%(refname)', 'refs/implementaudit/controllers/'],
                              cwd=self.cwd, capture_output=True, check=True)
        self.assertEqual(refs.stdout, b'')

    def test_controller_update_ignores_caller_python_modules(self):
        for command in (["git", "init", "-q"], ["git", "-c", "user.name=import fixture",
                "-c", "user.email=import@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "--allow-empty", "-qm", "disposable import fixture"]):
            result = subprocess.run(command, cwd=self.cwd, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        marker = self.root / "CALLER_MODULE_EXECUTED"
        for name in ('subprocess.py', 'json.py', 'pathlib.py'):
            (self.cwd / name).write_text("open(" + repr(str(marker))
                + ", 'w').write('unselected caller module: " + name + "')\n"
                + "raise ImportError('controlled caller module')\n")
        result = self.invoke(args=["--controller", "isolated-import", "new ordinary fixture"],
                             extra_env={"IMPLEMENTAUDIT_PYTHON": sys.executable})
        self.assertFalse(marker.exists(), "controller update executed caller-directory code")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        relative = result.stdout.decode().strip()
        inspected = self.invoke(args=['--inspect-controller-initialization', 'isolated-import', '--run-root', relative])
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertIsNone(json.loads(inspected.stdout)['current_controller_oid'])
        self.assertFalse(marker.exists(), 'pending controller path executed caller-directory code')
        helper = Path(__file__).resolve().parents[1] / 'fixtures/controller-initialization/author_checkpoint.py'
        authored = subprocess.run([sys.executable, str(helper), '--repo', str(self.cwd),
            '--run-root', relative, '--source', str(self.scripts.parents[2]),
            '--purpose', 'Qualify explicit activation and ordinary currentness discovery against caller-directory import substitution.',
            '--next-action', 'Inspect actual activated custody while refusing every caller-directory module'],
            capture_output=True, timeout=30)
        self.assertEqual(authored.returncode, 0, authored.stdout + authored.stderr)
        token = json.loads(inspected.stdout)['initialization_token']
        activated = self.invoke(args=['--activate-controller', 'isolated-import', '--run-root', relative,
                                      '--expected-initialization', token])
        self.assertEqual(activated.returncode, 0, activated.stdout + activated.stderr)
        self.assertFalse(marker.exists(), 'full initialization validation executed caller-directory code')
        current = self.invoke(args=['--current-controller', 'isolated-import'])
        self.assertEqual(current.returncode, 0, current.stdout + current.stderr)
        self.assertFalse(marker.exists(), 'ordinary controller discovery executed caller-directory code')

    def test_controller_cas_loser_preserves_prepared_claim_without_current_authority(self):
        self.initialize_test_repository('disposable activation CAS subject')
        prior, args = self.prepare_activation('cas-loser')
        self.assertEqual(self.invoke(args=args).returncode, 0)
        claim_id = next(line.removeprefix('claim_id=') for line in (prior / '.claimed').read_text().splitlines() if line.startswith('claim_id='))
        competing = subprocess.check_output(['git', 'hash-object', '-w', '--stdin'],
                                            input=b'concurrent CAS fixture; no authority claim\n', cwd=self.cwd).strip().decode()
        self.instrument_activation(before="ref = next(ref for ref in updates if ref.startswith('refs/implementaudit/controllers/'))\ngit(repo, 'update-ref', ref, " + repr(competing) + ", updates[ref][1])\nresult = git_process(repo, 'update-ref', '--stdin', '-z', input_bytes=b''.join(chunks))")
        losing, args = self.prepare_activation('cas-loser', claim_id)
        result = self.invoke(args=args)
        self.assertNotEqual(result.returncode, 0)
        observed = subprocess.check_output(['git', 'rev-parse', 'refs/implementaudit/controllers/cas-loser'],cwd=self.cwd).strip().decode()
        self.assertEqual(observed, competing)
        self.assertTrue((losing / '.claimed').is_file(), 'prepared losing custody evidence was erased')
        self.assertTrue((prior / '.claimed').is_file(), 'prior custody evidence was changed')
        self.assertNotEqual(self.invoke(args=['--current-controller', 'cas-loser']).returncode, 0)

    def test_initialization_refuses_replaced_validator_before_any_execution(self):
        self.initialize_test_repository('disposable validator authentication subject')
        run, args = self.prepare_activation('validator-before')
        marker = self.root / 'UNAUTHENTICATED_VALIDATOR_EXECUTED'
        validator = self.scripts / 'validate-run-root.sh'
        validator.write_text("#!/bin/bash\nprintf 'unselected validator' > "
                             + shlex.quote(str(marker)) + "\nexit 1\n")
        before = subprocess.check_output(['git', 'for-each-ref', '--format=%(refname) %(objectname)',
                                          'refs/implementaudit'], cwd=self.cwd)
        result = self.invoke(args=args)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(b'initialization validator differs from the paired owner source', result.stderr)
        self.assertFalse(marker.exists(), 'replaced validator ran before paired source authentication')
        after = subprocess.check_output(['git', 'for-each-ref', '--format=%(refname) %(objectname)',
                                         'refs/implementaudit'], cwd=self.cwd)
        self.assertEqual(after, before)

    def test_initialization_executes_captured_validator_and_refuses_source_replacement(self):
        self.initialize_test_repository('disposable validator capture subject')
        run, args = self.prepare_activation('validator-capture')
        marker = self.root / 'UNAUTHENTICATED_VALIDATOR_EXECUTED'
        observed = self.root / 'validator-replacement-observed'
        observer = self.root / 'validator-observer'
        observer.mkdir()
        validator = self.scripts / 'validate-run-root.sh'
        replacement = "#!/bin/bash\nprintf 'unselected validator' > " + shlex.quote(str(marker)) + "\nexit 1\n"
        (observer / 'sitecustomize.py').write_text(
            "import sys\nfrom pathlib import Path\narmed=True\n"
            "def observe(event,args):\n global armed\n"
            " if event!='subprocess.Popen' or not armed:return\n"
            " command=args[1]\n"
            " if not isinstance(command,(list,tuple)) or len(command)<2:return\n"
            " if 'implementaudit-initialization-source-' not in str(command[1]) or not str(command[1]).endswith('/validate-run-root.sh'):return\n"
            " armed=False\n Path(" + repr(str(validator)) + ").write_text(" + repr(replacement) + ")\n"
            " Path(" + repr(str(observed)) + ").write_text('replaced original after captured validator selected')\n"
            "sys.addaudithook(observe)\n")
        before = subprocess.check_output(['git', 'for-each-ref', '--format=%(refname) %(objectname)',
                                          'refs/implementaudit'], cwd=self.cwd)
        result = self.invoke(args=args, extra_env={'PYTHONPATH': str(observer)})
        self.assertTrue(observed.is_file(), 'validator capture boundary was not reached')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(marker.exists(), 'mutable original validator was re-opened for execution')
        after = subprocess.check_output(['git', 'for-each-ref', '--format=%(refname) %(objectname)',
                                         'refs/implementaudit'], cwd=self.cwd)
        self.assertEqual(after, before)

    def test_actual_controller_write_then_nonzero_is_received_by_exact_readback(self):
        self.assert_post_write_failure_retains_claim(lost_ack=False)

    def test_actual_controller_write_then_lost_ack_is_received_by_exact_readback(self):
        self.assert_post_write_failure_retains_claim(lost_ack=True)

    def assert_post_write_failure_retains_claim(self, *, lost_ack):
        self.initialize_test_repository('disposable activation acknowledgment subject')
        self.instrument_activation(after=("raise RotationError('controlled lost acknowledgment after real Git publication')"
                                          if lost_ack else 'result.returncode = 17'))
        run, args = self.prepare_activation('post-write-failure')
        result = self.invoke(args=args)
        self.assertEqual(result.returncode, 0, result.stderr)
        binding = json.loads(result.stdout)
        self.assertEqual(binding['status'], 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS')
        observed = subprocess.check_output(['git', 'show', 'refs/implementaudit/controllers/post-write-failure'],cwd=self.cwd)
        self.assertTrue(observed.startswith(b'implementaudit.controller-current.v1\tpost-write-failure\t'))
        self.assertIn(observed.decode().split('\t')[2], (run / '.claimed').read_text())
        # Exact authority readback proves the actual landed effect; a process
        # acknowledgment alone still proves nothing. No continuity is minted.
        self.assertNotEqual(self.invoke(args=['--require-current-continuity','post-write-failure']).returncode, 0)


class CompanionLoadIdentityPredicate(unittest.TestCase):
    """Synthetic metadata applied only to selected AST predicates; no native proof.

    No filesystem stat call, UID, owner import, Windows process, controller or
    publication is simulated. Actual runtime evidence belongs to the hosted lane.
    """
    BINDERS = ('_capture_claim_load_identity_v1', '_windows_custody')

    def guard(self, binder, platform='win32', version=(3, 12, 10), os_name='nt', implementation='cpython'):
        import ast
        import copy
        import types
        tree = ast.parse((SOURCE / 'claim-run-rotation.py').read_bytes())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == binder)
        helpers = [copy.deepcopy(n) for n in tree.body if isinstance(n, ast.FunctionDef)
                   and n.name in ('_claim_load_identity_v1', '_claim_load_cross_api_identity_v1',
                                  '_claim_load_capture_unchanged_v1')]
        local = [copy.deepcopy(n) for n in function.body if isinstance(n, ast.Assign)
                 and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                 and n.targets[0].id == 'identity' and isinstance(n.value, ast.Lambda)]
        def metadata(term):
            names = {n.id for n in ast.walk(term) if isinstance(n, ast.Name)}
            return bool(names & {'identity', '_claim_load_cross_api_identity_v1',
                                 '_claim_load_capture_unchanged_v1'})
        candidates = []
        for n in ast.walk(function):
            if not (isinstance(n, ast.If) and len(n.body) == 1 and isinstance(n.body[0], ast.Raise)):
                continue
            terms = n.test.values if isinstance(n.test, ast.BoolOp) and isinstance(n.test.op, ast.Or) else [n.test]
            selected = [copy.deepcopy(t) for t in terms if metadata(t)]
            if selected:
                test = selected[0] if len(selected) == 1 else ast.BoolOp(op=ast.Or(), values=selected)
                names = {x.id for x in ast.walk(test) if isinstance(x, ast.Name)}
                candidates.append(('terminal' if names & {'after', 'current'} else 'before_read', test, n.body))
        self.assertEqual(sorted(name for name, _, _ in candidates), ['before_read', 'terminal'])
        wrappers = []
        for name, test, body in candidates:
            wrapper = ast.parse('def ' + name + '(before, opened, after=None, current=None):\n    return True\n').body[0]
            wrapper.body = copy.deepcopy(local) + [ast.If(test=test, body=copy.deepcopy(body), orelse=[])] + wrapper.body
            wrappers.append(wrapper)
        module = ast.fix_missing_locations(ast.Module(body=helpers + wrappers, type_ignores=[]))
        namespace = dict(os=types.SimpleNamespace(name=os_name),
                         sys=types.SimpleNamespace(platform=platform, version_info=version,
                                                   implementation=types.SimpleNamespace(name=implementation)))
        exec(compile(module, '<synthetic-selected-load-predicates>', 'exec'), namespace)
        return namespace['before_read'], namespace['terminal']

    def rows(self, split=True):
        from types import SimpleNamespace
        # Deliberately constructed integers, not a counterfeit native observation.
        base = dict(st_dev=1, st_ino=2, st_mode=0o100644, st_nlink=1, st_size=10,
                    st_ctime_ns=100, st_mtime_ns=200, st_birthtime_ns=100, st_file_attributes=32)
        rows = [SimpleNamespace(**base) for _ in range(4)]
        if split:
            rows[1].st_ctime_ns = rows[2].st_ctime_ns = 200
        return rows

    def test_qualified_windows_split_is_accepted_by_each_binder(self):
        for binder in self.BINDERS:
            with self.subTest(binder=binder):
                before_read, terminal = self.guard(binder)
                rows = self.rows()
                self.assertTrue(before_read(*rows[:2]))
                self.assertTrue(terminal(*rows))
                self.assertTrue(terminal(*self.rows(False)))

    def test_each_common_or_same_api_field_mutation_is_refused(self):
        for binder in self.BINDERS:
            _, terminal = self.guard(binder)
            for position in range(4):
                for field in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size',
                              'st_ctime_ns', 'st_mtime_ns', 'st_birthtime_ns', 'st_file_attributes'):
                    rows = self.rows(); setattr(rows[position], field, getattr(rows[position], field) + 1)
                    with self.subTest(binder=binder, position=position, field=field), self.assertRaises(ImportError):
                        terminal(*rows)

    def test_other_runtimes_keep_the_strict_chain(self):
        contexts = [dict(os_name='posix', platform='linux'), dict(version=(3, 12, 9)),
                    dict(version=(3, 12, 11)), dict(version=(3, 13, 0)),
                    dict(platform='cygwin'), dict(implementation='pypy')]
        for binder in self.BINDERS:
            for context in contexts:
                before_read, terminal = self.guard(binder, **context)
                with self.subTest(binder=binder, context=context):
                    self.assertTrue(terminal(*self.rows(False)))
                    with self.assertRaises(ImportError): before_read(*self.rows()[:2])
                    with self.assertRaises(ImportError): terminal(*self.rows())

    def test_missing_or_wrong_type_common_metadata_fails_closed(self):
        for binder in self.BINDERS:
            _, terminal = self.guard(binder)
            for position in range(4):
                for field in ('st_birthtime_ns', 'st_file_attributes'):
                    for value in (None, True, 1.5, '32'):
                        rows = self.rows(); setattr(rows[position], field, value)
                        with self.subTest(binder=binder, position=position, field=field, value=value), \
                                self.assertRaisesRegex(ImportError, 'metadata is unavailable'):
                            terminal(*rows)
                    rows = self.rows(); delattr(rows[position], field)
                    with self.assertRaisesRegex(ImportError, 'metadata is unavailable'): terminal(*rows)


if __name__ == "__main__":
    unittest.main(verbosity=2)
