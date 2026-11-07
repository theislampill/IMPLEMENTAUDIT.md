#!/usr/bin/env python3
"""Native-only Windows06 capture controls and separate-process receiving.

This repo-only packet companion records observations. It creates no model
session, entitlement, original acceptance, or authority for another host.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import traceback

SOURCE_TREE = "0da374609f7fea2463a2926f3603b976620bd10e"
PROFILE = "composite-20261105-r5-h0-mechanical-template-v1-core"
DIRECT_GIT = (r"C:\Program Files\Git\mingw64\bin\git.exe",
              r"C:\Program Files\Git\ucrt64\bin\git.exe")
BASH = Path(r"C:\Program Files\Git\bin\bash.exe")
CORE_NAMES = ("claim-run.sh", "validate-run-root.sh", "claim-run-rotation.py",
              "rotate-canonical-state.py", "canonical_hot_projection.py",
              "canonical_custody.py", "canonical_rotation_inputs.py",
              "read-canonical-pair.py")
SHELL_CASES = (
    "test_same_size_unselected_companion_is_not_executed",
    "test_exact_companion_executes_in_both_package_layouts",
    "test_wrong_lengths_and_missing_source_are_refused",
    "test_hardlinked_companion_is_refused",
    "test_caller_directory_cannot_select_companion_or_bootstrap_import",
    "test_real_main_module_args_path_import_path_and_stdin_are_preserved",
    "test_capture_to_compile_path_change_never_executes_replacement",
    "test_initial_binder_equal_byte_replacement_refuses",
    "test_substrate_equal_byte_replacement_refuses",
)
SYNTHETIC_CASES = (
    "CompanionIdentityPredicate.test_windows_api_difference_preserves_both_mutation_checks",
    "CompanionIdentityPredicate.test_unqualified_runtime_retains_strict_chain",
    "CompanionIdentityPredicate.test_required_windows_metadata_refuses_missing_and_wrong_types",
    "CompanionLoadIdentityPredicate.test_qualified_windows_split_is_accepted_by_each_binder",
    "CompanionLoadIdentityPredicate.test_each_common_or_same_api_field_mutation_is_refused",
    "CompanionLoadIdentityPredicate.test_other_runtimes_keep_the_strict_chain",
    "CompanionLoadIdentityPredicate.test_missing_or_wrong_type_common_metadata_fails_closed",
)
SOURCE_CASES = (
    "CompositeSourceCases.test_prior_windows_load_binding_profile_has_exact_physical_members",
    "CompositeSourceCases.test_prior_windows_capture_profile_has_exact_physical_members",
    "CompositeSourceCases.test_retained_native_dependency_and_new_core_profiles_are_distinct",
    "CompositeSourceCases.test_engineered_profiles_select_current_bytes_and_preserve_every_historical_domain",
)
FOCUSED_SOURCE_FILES = (
    "scripts/check-package-contract.sh", "scripts/package-contract.py",
    "scripts/check-installed-payload-self-contained.sh", "tests/install-copy-smoke.test.sh",
    "tests/composite-source-cases.py", "package/implementaudit-package.json",
    ".codex-plugin/plugin.json", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "source-peers/native-runtime/SOURCE_MANIFEST.json",
    "source-peers/native-runtime/skills/implementaudit/scripts/claim-run.sh",
    "source-peers/native-runtime/skills/implementaudit/scripts/validate-run-root.sh",
    "source-peers/native-runtime/skills/implementaudit/scripts/claim-run-rotation.py",
    "source-peers/native-runtime/skills/implementaudit/scripts/rotate-canonical-state.py",
    "source-peers/native-runtime/skills/implementaudit/scripts/canonical_hot_projection.py",
    "source-peers/native-runtime/skills/implementaudit/scripts/canonical_rotation_inputs.py",
    "test-support/r5-h0-template-history/eb504b84-source/skills/implementaudit/scripts/claim-run.sh",
    "test-support/r5-h0-template-history/eb504b84-source/skills/implementaudit/scripts/claim-run-rotation.py",
    "test-support/r5-windows-load-binding-history/35bf982-source/skills/implementaudit/scripts/claim-run.sh",
    "test-support/r5-windows-load-binding-history/35bf982-source/skills/implementaudit/scripts/claim-run-rotation.py",
)
STAT_FIELDS = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
               "st_ctime_ns", "st_mtime_ns", "st_birthtime_ns", "st_file_attributes")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: require(False, "nonfinite JSON"))


def physical(path):
    path = Path(path).absolute()
    require(".." not in path.parts, "parent traversal refused")
    for part in (path, *path.parents):
        info = part.lstat()
        require(not stat.S_ISLNK(info.st_mode)
                and not getattr(info, "st_file_attributes", 0) & 0x400,
                "reparse or symlink path refused")
    return path.resolve(strict=True)


def read(path, maximum=4 * 1024 * 1024):
    path = physical(path)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
            and before.st_size <= maximum, "bounded single-link file required")
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    require(len(raw) <= maximum, "read bound exceeded")
    stable = lambda info: (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                           info.st_size, info.st_ctime_ns, info.st_mtime_ns)
    require(stable(path.lstat()) == stable(before), "file changed during independent read")
    return raw


def ident(path):
    raw = read(path)
    return {"bytes": len(raw), "sha256": digest(raw)}


def save(path, value):
    raw = value if type(value) is bytes else canonical(value)
    with Path(path).open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def runtime():
    # This gate precedes path access, output allocation and every product import.
    require(os.name == "nt" and sys.platform == "win32", "actual Windows required")
    require(sys.implementation.name == "cpython" and sys.version_info[:3] == (3, 12, 10),
            "exact physical CPython 3.12.10 required")
    require(sys.maxsize == 2**63 - 1, "x64 Python required")
    return {"os_name": os.name, "platform": sys.platform,
            "implementation": sys.implementation.name,
            "version": list(sys.version_info[:3]), "architecture_bits": 64,
            "python": {"path": str(physical(sys.executable)), **ident(sys.executable)}}


def binding(args):
    require(re.fullmatch("[0-9a-f]{40}", args.source_head or "")
            and args.source_head != "0" * 40 and args.source_tree == SOURCE_TREE,
            "exact published capture commit/tree required")
    require(str(physical(args.git)) in DIRECT_GIT, "fixed direct Git required")
    source, subject = physical(args.source), physical(args.subject)
    require(not source.is_relative_to(subject) and not subject.is_relative_to(source),
            "source and subject must be separate")
    raw = read(args.manifest)
    require(digest(raw) == args.manifest_sha256, "source manifest digest differs")
    manifest = strict_json(raw)
    require(manifest["source_commit"] == args.source_head
            and manifest["source_tree"] == args.source_tree, "manifest subject differs")
    git = lambda *parts: subprocess.check_output(
        [str(physical(args.git)), "-C", str(source), *parts], timeout=30)
    require(git("rev-parse", "HEAD", "HEAD^{tree}").decode().splitlines()
            == [args.source_head, args.source_tree], "actual source ancestry differs")
    require(git("status", "--porcelain=v1", "--untracked-files=normal") == b"",
            "source checkout is dirty")
    members = {}
    for row in manifest["members"]:
        name = row["path"]
        relative = PurePosixPath(name)
        require(not relative.is_absolute() and ".." not in relative.parts
                and "." not in relative.parts and name not in members, "unsafe manifest member")
        raw = read(source / name)
        require(len(raw) == row["bytes"] and digest(raw) == row["sha256"],
                "source member differs")
        oid = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(oid == row["git_blob_oid"], "source Git blob differs")
        if name.startswith("skills/"):
            require(read(subject / name) == raw, "copied subject runtime differs")
        members[name] = row
    required = {"scripts/run-r0039-windows-resume.py", "scripts/check-r0039-windows-resume.py",
                "scripts/r0039-windows-job.py", "scripts/work-graph-continuity-transport.py",
                "scripts/operational-evidence.py", "scripts/operational_query_policy.py",
                "skills/implementaudit/scripts/compile-work-graph.py",
                "tests/shell_companion_source_custody.py"}
    required.update("skills/implementaudit/scripts/" + name for name in CORE_NAMES)
    required.update(FOCUSED_SOURCE_FILES)
    require(required <= set(members), "native checking dependency omitted")
    return source, subject, {"source_commit": args.source_head, "source_tree": args.source_tree,
                             "manifest_sha256": args.manifest_sha256,
                             "member_count": len(members), "source_status": "CLEAN"}


def identity_functions(shell_raw):
    text = shell_raw.decode("utf-8")
    marker = '  "$rotation_py" -B -c \'\n'
    require(text.count(marker) == 1, "exact capture bootstrap absent")
    body = text.split(marker, 1)[1].split("\n' \"$(dirname \"$0\")/claim-run-rotation.py\"", 1)[0]
    parsed = ast.parse(body)
    functions = [node for node in parsed.body if isinstance(node, ast.FunctionDef)
                 and node.name in {"identity", "cross_api_identity", "directory_identity"}]
    require({node.name for node in functions} == {"identity", "cross_api_identity", "directory_identity"},
            "capture identity function population differs")
    fixed = {}
    for node in parsed.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in {"expected_bytes", "expected_sha256"}:
                fixed[node.targets[0].id] = ast.literal_eval(node.value)
    require(set(fixed) == {"expected_bytes", "expected_sha256"}, "capture byte pins absent")
    namespace = {"os": os, "sys": sys, "stat": stat}
    # Execute only the exact selected pure functions with real native metadata.
    # No os.name/stat/interpreter substitution and no companion owner execution.
    exec(compile(ast.Module(body=functions, type_ignores=[]), "<selected-native-capture-identities>", "exec"), namespace)
    return namespace, fixed


def snapshot_capture(path, functions, pins, label):
    record = {"case": label, "status": "INCOMPLETE", "snapshots": {}}
    try:
        path = physical(path)
        dirs = [(part, functions["directory_identity"](part.lstat())) for part in path.parents]
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                and not getattr(before, "st_file_attributes", 0) & 0x400
                and before.st_size == pins["expected_bytes"], "native capture preflight differs")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(path, flags), "rb") as stream:
            opened = os.fstat(stream.fileno())
            raw = stream.read(pins["expected_bytes"] + 1)
            after = os.fstat(stream.fileno())
            current = path.lstat()
        observations = (before, opened, after, current)
        record["snapshots"] = {name: {field: getattr(info, field, None) for field in STAT_FIELDS}
                               for name, info in zip(("path_before", "descriptor_opened", "descriptor_after", "path_current"), observations)}
        strict = [functions["identity"](info) for info in observations]
        cross = [functions["cross_api_identity"](info) for info in observations]
        record.update(strict_four_way_equal=all(value == strict[0] for value in strict),
                      same_api_pairs_equal=strict[0] == strict[3] and strict[1] == strict[2],
                      selected_cross_api_equal=all(value == cross[0] for value in cross),
                      captured_bytes=len(raw), captured_sha256=digest(raw),
                      read_request_bytes=pins["expected_bytes"] + 1)
        require(record["same_api_pairs_equal"] and record["selected_cross_api_equal"], "native capture identity differs")
        require(all(functions["directory_identity"](part.lstat()) == value for part, value in dirs),
                "native ancestor changed")
        require(len(raw) == pins["expected_bytes"] and digest(raw) == pins["expected_sha256"],
                "native capture bytes differ")
        record["status"] = "PASS_NATIVE_METADATA_AND_SELECTED_PREDICATE"
    except Exception as exc:
        record.update(status="FAIL_NATIVE_CAPTURE_OBSERVATION", exception_type=type(exc).__name__)
    return record


def job_summary(path):
    if not path.is_file():
        return {"status": "MEASUREMENT_UNAVAILABLE"}
    value = strict_json(read(path))
    keys = ("status", "exit_code", "cleanup_complete", "terminal_active_processes",
            "elapsed_ms", "peak_job_committed_bytes", "kernel_total_processes",
            "complete_memory_scope_valid", "baseline_subtracted_bytes",
            "diagnostic_timeout_seconds")
    return {key: value[key] for key in keys if key in value}


def capture_metadata(args, out, result):
    source, subject, source_binding = binding(args)
    result["source"] = source_binding
    scripts = source / "skills/implementaudit/scripts"
    copied = subject / "skills/implementaudit/scripts/claim-run-rotation.py"
    shell_raw = read(scripts / "claim-run.sh")
    functions, pins = identity_functions(shell_raw)
    result["selected_shell"] = {"bytes": len(shell_raw), "sha256": digest(shell_raw)}
    result["capture_pins"] = pins
    result["stage"] = "ACTUAL_COMPANION_METADATA"
    control = out / "owned-rewritten-companion.py"
    shutil.copy2(scripts / "claim-run-rotation.py", control)
    original = read(control)
    control.write_bytes(original)  # Owned same-size rewrite; no metadata substitution.
    cases = ((scripts / "claim-run-rotation.py", "exact_checked_out_companion"),
             (copied, "exact_copytree_subject_companion"),
             (control, "owned_same_size_rewritten_companion"))
    result["capture_observations"] = [snapshot_capture(path, functions, pins, label) for path, label in cases]
    require(all(row["status"] == "PASS_NATIVE_METADATA_AND_SELECTED_PREDICATE"
                for row in result["capture_observations"]), "native metadata case failed")
    result.update(status="PASS_NATIVE_CAPTURE_METADATA", stage="COMPLETE",
                  scope="SOURCE_AND_CUSTODY_BOOTSTRAP_OBSERVATION_ONLY; NO_OWNER_CONTROLLER_OR_CURRENTNESS_OPERATION")
    return source, subject, source_binding, scripts


def current_gate(args, subject, out, suffix):
    require(re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", args.controller or ""), "exact initialized controller required")
    require(re.fullmatch(re.escape("refs/implementaudit/continuity-receipts/" + args.controller + "/G0001@")
                         + "[0-9a-f]{40}", args.current_receipt or ""), "actual first receipt required")
    commands = (("verify-first-", ("--verify-resume-receipt", args.current_receipt)),
                ("require-first-", ("--require-current-continuity", args.controller)))
    for label, arguments in commands:
        observed = subprocess.run([str(physical(BASH)), "--noprofile", "--norc",
            str(subject / "skills/implementaudit/scripts/claim-run.sh"), *arguments],
            cwd=subject, stdin=subprocess.DEVNULL, capture_output=True, timeout=30)
        save(out / (label + suffix + ".stdout"), observed.stdout)
        save(out / (label + suffix + ".stderr"), observed.stderr)
        require(observed.returncode == 0 and observed.stdout.strip() == args.current_receipt.encode()
                and observed.stderr == b"", "actual initialized currentness did not verify")
    return {"controller": args.controller, "receipt_token": args.current_receipt,
            "status": "ACTUAL_FIRST_RECEIPT_VERIFIED_AND_REQUIRED_IN_THIS_PROCESS"}


def focused_selection(source, python, bash):
    """Fixed source/package diagnostics; no caller-selected command or program."""
    sh = [str(bash), "--noprofile", "--norc"]
    py = [str(python), "-I", "-X", "utf8", "-B"]
    return (
        ("package-contract", sh + [str(source / "scripts/check-package-contract.sh"),
                                    "--repo-root", str(source)], 0, b"package-contract: ok",
         "PACKAGE_DECLARATION_ONLY; NO_RELEASE_BUILD_OR_G1_QUALIFICATION"),
        ("installed-dependency-boundary", sh + [str(source / "scripts/check-installed-payload-self-contained.sh"),
                                                "--scan-root", str(source)], 0,
         b"check-installed-payload-self-contained: ok", "INSTALLED_DEPENDENCY_SCAN_ONLY"),
        ("copied-install-smoke", sh + [str(source / "tests/install-copy-smoke.test.sh")], 0,
         b"install-copy-smoke.test: ok", "ACTUAL_COPIED_SKILL_AND_PHASE_VALIDATOR_ONLY"),
        ("synthetic-binder-predicates", py + [str(source / "tests/shell_companion_source_custody.py"),
                                             *SYNTHETIC_CASES], len(SYNTHETIC_CASES), None,
         "SYNTHETIC_METADATA_PREDICATES_ONLY; NO_NATIVE_QUALIFICATION"),
        ("current-and-prior-source-profiles", py + [str(source / "tests/composite-source-cases.py"),
                                                   *SOURCE_CASES], len(SOURCE_CASES), None,
         "EXACT_SOURCE_PROFILE_AND_PHYSICAL_HISTORY_CONTROLS_ONLY; NO_HISTORICAL_PASS_INHERITED"),
    )


def focused_environment(label, environment):
    """Enable default MSYS argument conversion only for the three fixed Bash diagnostics."""
    if label not in ("package-contract", "installed-dependency-boundary", "copied-install-smoke"):
        return environment
    selected = dict(environment)
    selected.pop("MSYS2_ARG_CONV_EXCL", None)
    return selected


def focused_stderr_observations(label, raw):
    """Return a fixed scanner observation only; never return private stderr text."""
    require(type(raw) is bytes, "focused stderr bytes required")
    scanned = raw[:65536]
    codes = []
    if label == "installed-dependency-boundary" and b": repo-only path reference without 'source repo' label: " in scanned:
        codes.append("INSTALLED_DEPENDENCY_SOURCE_REPO_LABEL_MISSING")
    return {"stderr_codes": codes, "stderr_scan_bytes": len(scanned),
            "stderr_scan_limit_reached": len(raw) > 65536,
            "classification_scope": "FIXED_INSTALLED_SCANNER_PATTERN_ONLY; NO_FREEFORM_TEXT_OR_CAUSAL_VERDICT"}


def focused_diagnostics(source, out, environment, result, job):
    selected = focused_selection(source, physical(sys.executable), physical(BASH))
    result["focused_controls"] = {"cases": [row[0] for row in selected],
        "selected_count": len(selected), "executed_count": 0, "observations": [],
        "scope": "BOUNDED_PACKAGE_INSTALL_AND_SOURCE_CONTROLS; NOT_THE_60000MS_PRODUCT_INTERVAL"}
    record = result["focused_controls"]
    for label, command, expected_count, marker, scope in selected:
        result["stage"] = "CURRENT_FOCUSED_SOURCE_DIAGNOSTICS"
        destination = out / ("focused-" + label)
        row = {"case": label, "status": "INCOMPLETE", "scope": scope}
        record["observations"].append(row)
        try:
            observed = job.measure(command, source, focused_environment(label, environment), destination,
                                   diagnostic_timeout_seconds=15)
        finally:
            row["job"] = job_summary(destination / "measurement.json")
            for name in ("stdout", "stderr"):
                path = destination / (name + ".bin")
                if path.is_file():
                    raw = read(path)
                    row[name] = {"bytes": len(raw), "sha256": digest(raw)}
                    if name == "stderr": row.update(focused_stderr_observations(label, raw))
        require(observed["status"] == "COMPLETE_UNADMITTED" and observed["cleanup_complete"] is True
                and observed["terminal_active_processes"] == 0 and observed["exit_code"] == 0,
                "focused source diagnostic failed or cleanup unverified")
        stdout = read(destination / "stdout.bin")
        stderr = read(destination / "stderr.bin").decode("utf-8", "replace")
        if expected_count:
            count = re.findall(r"Ran ([0-9]+) tests? in", stderr)
            require(count == [str(expected_count)] and re.search(r"(?m)^OK\s*$", stderr)
                    and "skipped=" not in stderr, "focused diagnostic count differs or skipped")
            row.update(selected_count=expected_count, executed_count=expected_count, skipped_count=0)
        else:
            require(stdout.count(marker) == 1, "focused package diagnostic did not reach its exact success marker")
        row.update(status="PASS", exit_code=observed["exit_code"])
        record["executed_count"] += 1
    record.update(status="PASS", skipped_count=0)


def capture(args, out, result):
    source, subject, source_binding, scripts = capture_metadata(args, out, result)
    result["stage"] = "CURRENTNESS_BEFORE_NATIVE_SHELL_CONTROLS"
    result["currentness_before"] = current_gate(args, subject, out, "before")

    result["stage"] = "SELECTED_NATIVE_SHELL_CONTROLS"
    environment = dict(os.environ)
    work, evidence = out / "shell-work", out / "shell-evidence"
    work.mkdir(); evidence.mkdir()
    environment.update(SHELL_CUSTODY_SOURCE=str(scripts), SHELL_CUSTODY_WORK=str(work),
                       SHELL_CUSTODY_EVIDENCE=str(evidence),
                       IMPLEMENTAUDIT_PYTHON=str(physical(sys.executable)),
                       PYTHONDONTWRITEBYTECODE="1")
    command = [str(physical(sys.executable)), "-I", "-X", "utf8", "-B",
               str(source / "tests/shell_companion_source_custody.py")]
    command.extend("ShellCompanionSourceCustody." + name for name in SHELL_CASES)
    result["shell_controls"] = {"cases": list(SHELL_CASES), "selected_count": len(SHELL_CASES),
                                "scope": "NATIVE_DIAGNOSTIC_CONTROLS; NOT_THE_60000MS_PRODUCT_INTERVAL"}
    job = load(source / "scripts/r0039-windows-job.py", "windows04_diagnostic_job")
    try:
        observed = job.measure(command, subject, environment, out / "shell-job", diagnostic_timeout_seconds=300)
    finally:
        result["shell_controls"]["job"] = job_summary(out / "shell-job/measurement.json")
        for name in ("stdout", "stderr"):
            path = out / "shell-job" / (name + ".bin")
            if path.is_file(): result["shell_controls"][name] = ident(path)
    require(observed["status"] == "COMPLETE_UNADMITTED" and observed["cleanup_complete"] is True
            and observed["terminal_active_processes"] == 0 and observed["exit_code"] == 0,
            "selected native shell controls failed or cleanup unverified")
    output = read(out / "shell-job/stderr.bin").decode("utf-8", "replace")
    count = re.findall(r"Ran ([0-9]+) tests? in", output)
    require(count == [str(len(SHELL_CASES))] and re.search(r"(?m)^OK\s*$", output)
            and "skipped=" not in output, "native shell controls incomplete or skipped")
    result["shell_controls"].update(status="PASS", executed_count=len(SHELL_CASES), skipped_count=0)
    focused_diagnostics(source, out, environment, result, job)
    require(binding(args)[2] == source_binding, "source changed during capture controls")
    result["stage"] = "CURRENTNESS_AFTER_NATIVE_SHELL_CONTROLS"
    result["currentness_after"] = current_gate(args, subject, out, "after")
    require(result["currentness_before"] == result["currentness_after"], "native controls changed actual currentness")
    result.update(status="PASS_NATIVE_CAPTURE_CONTROLS", stage="COMPLETE",
                  scope="ACTUAL_WINDOWS_CAPTURE_AND_SELECTED_CONTROLS_ONLY; NO_NATIVE_MODEL_OR_ORIGINAL_ACCEPTANCE")


def receive(args, out, result):
    source, subject, source_binding = binding(args)
    result["source"] = source_binding
    result["stage"] = "INDEPENDENT_MEASUREMENT_READ"
    driver = load(source / "scripts/run-r0039-windows-resume.py", "windows04_independent_driver")
    checker = driver.Q
    operation = physical(args.operation)
    plan_raw = read(operation / "OPERATION.json")
    require(digest(plan_raw) == args.plan_sha256, "prepared plan digest differs")
    plan = checker.strict_json(plan_raw)
    request, prepared = plan["request"], plan["prepared"]
    require(physical(request["source_root"]) == source and physical(request["subject_root"]) == subject
            and request["source_head"] == args.source_head and request["source_tree"] == args.source_tree
            and request["controller"] == args.controller, "operation subject binding differs")
    snapshot = driver.source_snapshot(request)
    require(checker.same_json(snapshot, prepared["snapshot"]), "source/runtime/tool snapshot changed")
    raw_measurement = read(operation / "execution/MEASUREMENT.json")
    measurement = checker.strict_json(raw_measurement)
    result["measurement"] = checker.validate_measurement(measurement, prepared["command"], request["tools"])
    result["measurement_file"] = {"bytes": len(raw_measurement), "sha256": digest(raw_measurement)}

    result["stage"] = "INDEPENDENT_OWNER_AND_TRANSITION_READBACK"
    env = driver.environment(request["tools"])
    before_refs = driver.refs(request)
    def owner_call(label, *arguments):
        return driver.command(driver.claim(request, *arguments), subject, env, out, label, timeout=30).stdout
    after = checker.strict_json(owner_call("resolve-current", "--resolve-canonical-generation", args.controller))
    require(checker.same_json(after, checker.strict_json(read(operation / "execution/CURRENT.json"))),
            "live canonical resolution differs from primary observation")
    token = after["receipt_token"]
    verified = owner_call("verify-receipt", "--verify-resume-receipt", token)
    required = owner_call("require-current", "--require-current-continuity", args.controller)
    pair = {}
    for role in ("STATE", "ROADMAP"):
        pair[role] = driver.payload(owner_call("current-" + role, "--read-canonical-state", args.controller,
                                               "--role", role, "--expected-pointer", after["pointer_token"]))
    receipt_raw = driver.git(request, subject, "cat-file", "blob", token.split("@")[1])
    require(receipt_raw == read(operation / "execution/RECEIPT.raw"), "live receipt differs from primary bytes")
    _, paths = driver.retained_paths(request, prepared["before"])
    now_refs = driver.refs(request)
    retained = {"files": {role: driver.ident(path) for role, path in paths.items()},
                "refs": {ref: now_refs.get(ref) for ref in prepared["retained"]["refs"]}}
    result["transition"] = checker.validate_transition(
        prepared["before"], after, receipt_raw, prepared["payloads"], pair,
        prepared["retained"], retained, read(operation / "execution/operation/stdout.bin"), verified, required)
    result["receipt"] = {"token": token, "bytes": len(receipt_raw), "sha256": digest(receipt_raw)}
    result["retained_state"] = {"files": retained["files"], "ref_count": len(retained["refs"]),
                                 "refs_sha256": digest(canonical(retained["refs"])),
                                 "protected_payloads_sha256": digest(canonical(pair))}

    result["stage"] = "EXACT_CURRENT_WINDOWS_CALLER_AND_RECEIVER"
    compiler_path = source / "skills/implementaudit/scripts/compile-work-graph.py"
    compiler = load(compiler_path, "windows04_fixed_compiler")
    owner, owner_path, owner_raw = compiler._native_static_owner_module_v1()
    host = compiler._native_continuity_host_v1()
    require(Path(host.trusted_host_executable(subject, "bash")).samefile(BASH), "caller selected another Bash")
    scripts = compiler_path.parent
    claim_raw, validate_raw = read(scripts / "claim-run.sh"), read(scripts / "validate-run-root.sh")
    transport, sources, transport_source = compiler._native_six_source_transport_v1(owner, claim_raw, validate_raw)
    profile = transport.SOURCE_PROFILES_V1[PROFILE]
    selected = transport.source_profiles_for_helpers_v1(claim_raw, validate_raw)
    expected = tuple(tuple((*row[:3], None)) for row in profile)
    require(selected == (expected,) and tuple(Path(path).name for path, _ in sources) == CORE_NAMES,
            "caller selected a different source profile")
    helper_pair = {"claim_sha256": digest(claim_raw), "validate_sha256": digest(validate_raw)}
    observed_closure = None
    rows = []
    for label, arguments in (("current-controller", ("--current-controller",)),
                             ("require-current", ("--require-current-continuity", args.controller)),
                             ("verify-receipt", ("--verify-resume-receipt", token))):
        direct = owner_call("direct-" + label, *arguments)
        observed = transport.call_readonly_v1(owner, repository=str(subject), sources=sources,
                                             arguments=arguments, route=host)
        require(observed["returncode"] == 0 and observed["stdout"] == direct
                and observed["stderr"] == b"", "actual caller output differs from direct owner")
        if observed_closure is not None:
            require(checker.same_json(observed["closure"], observed_closure), "caller closure changed")
        observed_closure = observed["closure"]
        path, raw, mode = transport_source
        closure = {"schema": "implementaudit.native-continuity-closure.v1", "execution": observed_closure,
                   "transport": {"path": str(path), "bytes": len(raw), "sha256": digest(raw), "mode": mode}}
        owner._native_check_continuity_closure_v1(closure, subject, compiler_path, helper_pair)
        rows.append({"command": arguments[0], "exit_code": observed["returncode"],
                     "stdout_sha256": digest(observed["stdout"]), "stderr_sha256": digest(observed["stderr"]),
                     "receiver": "CURRENT_FIXED_RECEIVER_ACCEPTED_EXACT_LIVE_CLOSURE"})
    require(checker.same_json(driver.source_snapshot(request), snapshot)
            and driver.refs(request) == before_refs, "readback changed source or controller refs")
    require(binding(args)[2] == source_binding, "source changed during separate receiving")
    result["caller_receiving"] = {"profile": PROFILE, "compiler": ident(compiler_path),
                                   "owner": {"bytes": len(owner_raw), "sha256": digest(owner_raw)},
                                   "closure": closure, "observations": rows,
                                   "scope": "THREE_REAL_READONLY_CALLS_AND_EXACT_CORE8_RECEIVER; NOT_FULL_NATIVE18_CAMPAIGN"}
    result.update(status="PASS_INDEPENDENT_NATIVE_READBACK", stage="COMPLETE",
                  scope="SEPARATE_PROCESS_SAME_LIVE_WINDOWS_SUBJECT; NO_INDEPENDENT_MODEL_OR_ORIGINAL_ACCEPTANCE",
                  currentness_exported_to_other_host=False, source_and_refs_unchanged=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("metadata", "capture", "receive"))
    for name in ("source", "subject", "manifest", "output", "git"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("source-head", "source-tree", "manifest-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--operation", type=Path)
    parser.add_argument("--controller")
    parser.add_argument("--current-receipt")
    parser.add_argument("--plan-sha256")
    args = parser.parse_args()
    actual_runtime = runtime()
    out = physical(args.output.parent) / args.output.name
    source, subject = physical(args.source), physical(args.subject)
    require(not out.exists() and not out.is_relative_to(source) and not out.is_relative_to(subject),
            "unused separated diagnostic output required")
    out.mkdir(exist_ok=False)
    result = {"schema": "r5.windows05.native-" + args.action + ".v1", "status": "FAIL_INCOMPLETE",
              "stage": "SOURCE_BINDING", "runtime": actual_runtime, "authority": "NONE",
              "original_acceptance_delta": 0, "automatic_retry": False}
    status = 1
    try:
        if args.action == "metadata": capture_metadata(args, out, result)
        elif args.action == "capture": capture(args, out, result)
        else:
            require(args.operation is not None and args.controller and args.plan_sha256,
                    "complete independent receiving input required")
            receive(args, out, result)
        status = 0
    except Exception as exc:
        result.update(status="FAILED_RETAINED_NO_RETRY", exception_type=type(exc).__name__)
        save(out / "private-traceback.txt", traceback.format_exc().encode())
    finally:
        save(out / "SUMMARY.json", result)
    print(json.dumps({"status": result["status"], "stage": result["stage"],
                      "summary_sha256": ident(out / "SUMMARY.json")["sha256"],
                      "original_acceptance_delta": 0}, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
