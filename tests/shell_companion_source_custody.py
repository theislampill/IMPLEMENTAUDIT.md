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
           "rotate-canonical-state.py", "validate-run-root.sh", "read-canonical-pair.py")
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

    def test_successful_interpreter_without_controller_effect_is_not_a_successful_claim(self):
        for command in (["git", "init", "-q"], ["git", "-c", "user.name=postcondition fixture",
                "-c", "user.email=postcondition@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "--allow-empty", "-qm", "disposable postcondition fixture"]):
            result = subprocess.run(command, cwd=self.cwd, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        shell = self.scripts / "claim-run.sh"
        original = shell.read_bytes()
        anchor = b" with subprocess.Popen(['git','update-ref','--stdin'],stdin=subprocess.PIPE,stdout=subprocess.PIPE) as transaction:"
        self.assertEqual(original.count(anchor), 1)
        marker = self.root / "interpreter-returned-without-effect"
        replacement = (" open(" + repr(str(marker)) + ", 'w').write('observed no-effect return')\n"
                       " raise SystemExit(0)\n" + anchor.decode()).encode()
        instrumented = original.replace(anchor, replacement)
        self.assertEqual(instrumented.replace(replacement, anchor), original)
        shell.write_bytes(instrumented)
        result = self.invoke(args=["--controller", "postcondition", "new ordinary fixture"],
                             extra_env={"IMPLEMENTAUDIT_PYTHON": sys.executable})
        self.assertEqual(marker.read_text(), "observed no-effect return")
        self.assertNotEqual(result.returncode, 0, "exit zero was mistaken for the absent controller effect")
        self.assertIn(b"controller ref readback is unverified; retained claim", result.stderr)
        retained = list((self.cwd / ".IMPLEMENTAUDIT/runs").glob("*/.claimed"))
        self.assertEqual(len(retained), 1)
        self.assertTrue(retained[0].with_name(".controller").is_file())
        refs = subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/implementaudit/"],
                              cwd=self.cwd, capture_output=True, check=True)
        self.assertEqual(refs.stdout, b"")

    def test_controller_update_ignores_caller_python_modules(self):
        for command in (["git", "init", "-q"], ["git", "-c", "user.name=import fixture",
                "-c", "user.email=import@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "--allow-empty", "-qm", "disposable import fixture"]):
            result = subprocess.run(command, cwd=self.cwd, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        marker = self.root / "CALLER_MODULE_EXECUTED"
        (self.cwd / "subprocess.py").write_text("from pathlib import Path\nPath(" + repr(str(marker))
            + ").write_text('unselected caller module')\nraise ImportError('controlled caller module')\n")
        result = self.invoke(args=["--controller", "isolated-import", "new ordinary fixture"],
                             extra_env={"IMPLEMENTAUDIT_PYTHON": sys.executable})
        self.assertFalse(marker.exists(), "controller update executed caller-directory code")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        observed = subprocess.run(["git", "rev-parse", "--verify", "refs/implementaudit/controllers/isolated-import"],
                                  cwd=self.cwd, capture_output=True, check=True)
        self.assertEqual(len(observed.stdout.strip()), 40)

    def test_controller_cas_loser_cleans_only_its_unpublished_claim(self):
        for command in (["git", "init", "-q"], ["git", "-c", "user.name=CAS fixture",
                "-c", "user.email=cas@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "--allow-empty", "-qm", "disposable CAS fixture"]):
            result = subprocess.run(command, cwd=self.cwd, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        initial = self.invoke(args=["--controller", "cas-loser", "initial fixture"],
                              extra_env={"IMPLEMENTAUDIT_PYTHON": sys.executable})
        self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
        claim = next((self.cwd / ".IMPLEMENTAUDIT/runs").glob("*/.claimed"))
        claim_id = next(line.removeprefix("claim_id=") for line in claim.read_text().splitlines()
                        if line.startswith("claim_id="))
        competing = subprocess.check_output(["git", "hash-object", "-w", "--stdin"],
                                            input=b"concurrent CAS fixture\n", cwd=self.cwd).strip().decode()
        shell = self.scripts / "claim-run.sh"
        original = shell.read_bytes()
        anchor = b" if unsafe(current) or (current.st_dev,current.st_ino)!=(opened.st_dev,opened.st_ino): raise SystemExit(1)\n"
        self.assertEqual(original.count(anchor), 1)
        # Move the real ref after the shell captured its expected old OID.
        # This is a Git CAS control; the opaque competing blob claims no authority.
        insertion = (" subprocess.run(['git','update-ref',ref," + repr(competing)
                     + ",old],check=True)\n").encode()
        shell.write_bytes(original.replace(anchor, anchor + insertion))
        result = self.invoke(args=["--controller", "cas-loser", "--supersede-claim", claim_id,
                                   "losing fixture"], extra_env={"IMPLEMENTAUDIT_PYTHON": sys.executable})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"cannot lock ref", result.stderr)
        observed = subprocess.check_output(["git", "rev-parse", "refs/implementaudit/controllers/cas-loser"],
                                            cwd=self.cwd).strip().decode()
        self.assertEqual(observed, competing)
        self.assertEqual(list((self.cwd / ".IMPLEMENTAUDIT/runs").iterdir()), [claim.parent],
                         "proved losing CAS retained a plausible unpublished run root")
        self.assertTrue(claim.is_file(), "losing contender changed the original claim")

    def test_actual_controller_write_then_nonzero_retains_unverified_claim(self):
        self.assert_post_write_failure_retains_claim(lost_ack=False)

    def test_actual_controller_write_then_lost_commit_ack_retains_unverified_claim(self):
        self.assert_post_write_failure_retains_claim(lost_ack=True)

    def assert_post_write_failure_retains_claim(self, *, lost_ack):
        for command in (["git", "init", "-q"], ["git", "-c", "user.name=return fixture",
                "-c", "user.email=return@example.invalid", "-c", "commit.gpgsign=false",
                "commit", "--allow-empty", "-qm", "disposable return fixture"]):
            result = subprocess.run(command, cwd=self.cwd, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        shell = self.scripts / "claim-run.sh"
        original = shell.read_bytes()
        anchor = b"  raise SystemExit(0 if committed==b'commit: ok\\n' and transaction.returncode==0 else 1)"
        self.assertEqual(original.count(anchor), 1)
        replacement = ((b"  committed=b''\n" + anchor) if lost_ack else
                       b"  raise SystemExit(transaction.returncode if transaction.returncode else 17)")
        instrumented = original.replace(anchor, replacement)
        self.assertEqual(instrumented.replace(replacement, anchor), original)
        shell.write_bytes(instrumented)
        result = self.invoke(args=["--controller", "post-write-failure", "new ordinary fixture"],
                             extra_env={"IMPLEMENTAUDIT_PYTHON": sys.executable})
        self.assertNotEqual(result.returncode, 0)
        observed = subprocess.run(["git", "show", "refs/implementaudit/controllers/post-write-failure"],
                                  cwd=self.cwd, capture_output=True, check=True)
        self.assertTrue(observed.stdout.startswith(b"implementaudit.controller-current.v1\tpost-write-failure\t"))
        retained = list((self.cwd / ".IMPLEMENTAUDIT/runs").glob("*/.claimed"))
        self.assertEqual(len(retained), 1, "completed controller effect lost its claim evidence")
        self.assertTrue(retained[0].with_name(".controller").is_file())
        self.assertIn(observed.stdout.decode().split("\t")[2], retained[0].read_text())
        self.assertIn(b"retained claim", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
