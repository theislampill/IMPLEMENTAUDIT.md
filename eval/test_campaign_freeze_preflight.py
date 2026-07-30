#!/usr/bin/env python3
"""Deterministic tests for Luna-only campaign freeze preflight."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

import adapters
import b3v4_campaign
import campaign_freeze_preflight as preflight
import evaluated_surfaces as surfaces
import test_b3v4_freeze as b3_freeze_fixture


def write(path, value):
    pathlib.Path(path).write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8")


def _write_retained_readiness_fixture(
        campaign, packet, base, execution_mode, campaign_root=None,
        campaign_initialized=False):
    base = pathlib.Path(base).absolute()
    base.mkdir(parents=True, exist_ok=True)
    native = base / "native-test-executable.bin"
    launcher = base / "launcher-test.py"
    auth = base / "auth-source-path.json"
    for path, payload in (
            (native, b"native test executable\n"),
            (launcher, b"test launcher\n"),
            (auth, b"opaque test auth locator; contents never read\n")):
        if not path.exists():
            path.write_bytes(payload)
    checkout_names = (
        ("candidate", "control") if campaign == "b3v4"
        else ("candidate",))
    checkouts = {}
    for name in checkout_names:
        path = base / name
        path.mkdir(exist_ok=True)
        checkouts[name] = {
            "path": str(path), "commit": "1" * 40,
            "tree": "2" * 40, "skill_tree": "3" * 40,
            "payload_sha256": "4" * 64,
            "clean": True, "disposable": True, "native": True,
        }
    runtime = base / "runtime"
    runtime.mkdir(exist_ok=True)
    campaign_root = (
        pathlib.Path(campaign_root).absolute()
        if campaign_root is not None else base / "campaign")
    config = (packet["configurations"]["L"]
              if campaign == "b3v4" else packet["configuration"])
    report = {
        "schema": preflight.LIVE_READY_SCHEMAS[campaign],
        "campaign": campaign,
        "freeze_sha256": hashlib.sha256(
            preflight.lifecycle.canonical_json_bytes(packet)).hexdigest(),
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "execution_mode": execution_mode,
        "disposition": ("READY_FOR_LUNA_EXECUTION"
                        if execution_mode == "production"
                        else "TEST_ONLY_NON_QUALIFYING"),
        "ready": execution_mode == "production",
        "mission_authorized": execution_mode == "production",
        "test_mock_authorized": execution_mode == "test",
        "created_at": "2026-07-29T00:00:00Z",
        "model_scope": preflight.MODEL_SCOPE,
        "host_attestation_binding": {
            "id": config["host_attestation"]["id"],
            "sha256": config["host_attestation"]["sha256"],
            "producer_command_sha256": "5" * 64,
            "producer_status": "PASS",
        },
        "native_executable_binding": {
            "path": str(native), "version": "test-native-1",
            "sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
        },
        "launcher_binding": {
            "path": str(launcher),
            "sha256": hashlib.sha256(launcher.read_bytes()).hexdigest(),
            "evaluated_surface_role": "launcher",
            "evaluated_surface_manifest_sha256": hashlib.sha256(
                preflight.lifecycle.canonical_json_bytes(
                    packet.get("evaluated_surfaces"))).hexdigest(),
        },
        "checkout_bindings": checkouts,
        "runtime_root_binding": {
            "path": str(runtime), "disposable": True,
            "initial_empty": True,
        },
        "authorization_binding": {
            "acknowledgement_sha256": "7" * 64,
            "metered_api_spend": "FORBIDDEN",
            "launch_authorized": execution_mode == "production",
            "codex_auth_source_path": str(auth),
            "codex_auth_source_identity_sha256":
                preflight._metadata_identity_sha(auth),
            "auth_contents_read": False,
        },
        "cross_host_validation": {
            "status": "PASS", "launcher_path": str(launcher),
            "native_executable_path": str(native),
            "native_executable_version": "test-native-1",
            "checkout_paths": {
                name: row["path"] for name, row in checkouts.items()},
            "runtime_root_path": str(runtime),
            "executable_resolution": "PASS",
        },
        "producer": {
            "command": "test-only-readiness-producer",
            "command_sha256": "8" * 64, "argv_sha256": "9" * 64,
            "status": "PASS",
        },
    }
    if campaign == "b3v4":
        report["campaign_root_binding"] = \
            preflight._campaign_directory_binding(
                str(campaign_root), "test campaign root",
                initialized=campaign_initialized,
                root_identity=(
                    preflight._directory_identity(
                        campaign_root, "test campaign root")
                    if campaign_initialized else None))
        report["cross_host_validation"][
            "campaign_root_path"] = str(campaign_root)
    path = base / f"{campaign}-test-live-readiness.json"
    write(path, report)
    return path


def write_test_live_ready(
        campaign, packet, base, execution_mode="test", campaign_root=None):
    """Build a closed TEST_ONLY boundary incapable of production authority."""
    if execution_mode != "test":
        raise ValueError(
            "write_test_live_ready is TEST_ONLY and non-qualifying")
    return _write_retained_readiness_fixture(
        campaign, packet, base, "test", campaign_root)


def write_retained_production_readiness_fixture(
        campaign, packet, base, campaign_root=None):
    """Build retained production-shaped bytes for independent parser tests.

    This helper is never passed to a production CampaignDriver and does not
    perform or authorize a mission.
    """
    return _write_retained_readiness_fixture(
        campaign, packet, base, "production", campaign_root,
        campaign_initialized=campaign_root is not None)


def expect_error(fragment, action):
    try:
        action()
    except (OSError, TypeError, ValueError) as exc:
        if fragment is not None:
            assert fragment.lower() in str(exc).lower(), str(exc)
    else:
        raise AssertionError(f"expected error containing {fragment!r}")


def exercise_path_type_custody():
    with tempfile.TemporaryDirectory(
            prefix="campaign-preflight-path-custody-") as tmp:
        base = pathlib.Path(tmp).absolute()
        ordinary = base / "ordinary-directory"
        (ordinary / "nested-child").mkdir(parents=True)
        campaign_leaf = ordinary / "campaign"
        campaign_binding = preflight._absent_directory_binding(
            str(campaign_leaf), "campaign root")
        assert campaign_binding["path"] == str(campaign_leaf)
        assert campaign_binding["parent_path"] == str(ordinary)
        assert campaign_binding["initial_state"] == "ABSENT_CREATE_ONCE"
        assert len(campaign_binding["parent_identity_sha256"]) == 64
        campaign_leaf.mkdir()
        expect_error(
            "absent",
            lambda: preflight._absent_directory_binding(
                str(campaign_leaf), "campaign root"))
        (campaign_leaf / "residue").write_text("invalid\n", encoding="utf-8")
        expect_error(
            "absent",
            lambda: preflight._absent_directory_binding(
                str(campaign_leaf), "campaign root"))

        real_lstat = os.lstat

        class DirectoryStatWithPosixLinkCount:
            def __init__(self, observed):
                self._observed = observed
                self.st_nlink = max(2, observed.st_nlink)

            def __getattr__(self, name):
                return getattr(self._observed, name)

        def posix_directory_lstat(path, *args, **kwargs):
            observed = real_lstat(path, *args, **kwargs)
            if pathlib.Path(path).absolute() == ordinary:
                return DirectoryStatWithPosixLinkCount(observed)
            return observed

        with mock.patch.object(
                preflight.os, "lstat", side_effect=posix_directory_lstat):
            assert preflight._absolute_directory(
                str(ordinary), "ordinary directory") == ordinary

        drifting = base / "drifting-directory"
        drifting.mkdir()
        drifting_observations = 0

        class DirectoryStatWithIdentityDrift:
            def __init__(self, observed):
                self._observed = observed
                self.st_ino = observed.st_ino + 1

            def __getattr__(self, name):
                return getattr(self._observed, name)

        def drifting_directory_lstat(path, *args, **kwargs):
            nonlocal drifting_observations
            observed = real_lstat(path, *args, **kwargs)
            if pathlib.Path(path).absolute() == drifting:
                drifting_observations += 1
                if drifting_observations == 3:
                    return DirectoryStatWithIdentityDrift(observed)
            return observed

        with mock.patch.object(
                preflight.os, "lstat", side_effect=drifting_directory_lstat):
            expect_error(
                "identity changed",
                lambda: preflight._absolute_directory(
                    str(drifting), "drifting directory"))

        symlink = base / "directory-symlink"
        try:
            symlink.symlink_to(ordinary, target_is_directory=True)
        except OSError:
            print("PREFLIGHT_DIRECTORY_SYMLINK=SKIP:unsupported")
        else:
            expect_error(
                "link",
                lambda: preflight._absolute_directory(
                    str(symlink / "nested-child"),
                    "directory symlink component"))
            expect_error(
                "link",
                lambda: preflight._absent_directory_binding(
                    str(symlink / "campaign"),
                    "campaign symlink parent"))
            print("PREFLIGHT_DIRECTORY_SYMLINK=PASS")

        junction = base / "directory-junction"
        if os.name == "nt":
            created = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J",
                 str(junction), str(ordinary)],
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                check=False)
            if created.returncode != 0:
                print("PREFLIGHT_DIRECTORY_JUNCTION=SKIP:unsupported")
            else:
                try:
                    expect_error(
                        "link",
                        lambda: preflight._absolute_directory(
                            str(junction / "nested-child"),
                            "directory junction component"))
                    expect_error(
                        "link",
                        lambda: preflight._absent_directory_binding(
                            str(junction / "campaign"),
                            "campaign junction parent"))
                    print("PREFLIGHT_DIRECTORY_JUNCTION=PASS")
                finally:
                    os.rmdir(junction)

        retained = base / "retained-evidence.json"
        alias = base / "retained-evidence-hardlink.json"
        retained.write_text("{}\n", encoding="utf-8")
        os.link(retained, alias)
        expect_error(
            "hardlink",
            lambda: preflight._regular_path(
                str(alias), "retained evidence", read_bytes=True))
        print("PREFLIGHT_REGULAR_FILE_HARDLINK=PASS")


def production_fixture(base):
    base = pathlib.Path(base)
    repo = pathlib.Path(__file__).resolve().parent.parent
    clone_source = repo
    if os.name == "posix" and (repo / ".git").is_file():
        primary = repo.parent / "IMPLEMENTAUDIT"
        assert (primary / ".git").is_dir(), primary
        gitdir_value = (repo / ".git").read_text(
            encoding="utf-8").strip().removeprefix("gitdir: ")
        drive, suffix = gitdir_value.split(":", 1)
        gitdir = pathlib.Path("/mnt") / drive.lower() / suffix.lstrip("/")
        head_value = (gitdir / "HEAD").read_text(encoding="utf-8").strip()
        if head_value.startswith("ref: "):
            common = (gitdir / (gitdir / "commondir").read_text(
                encoding="utf-8").strip()).resolve()
            assigned_head = (common / head_value.removeprefix(
                "ref: ")).read_text(encoding="utf-8").strip()
        else:
            assigned_head = head_value
        native_repo = base / "source-repo"
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks",
             str(primary), str(native_repo)],
            stdin=subprocess.DEVNULL, check=True)
        subprocess.run(
            ["git", "-C", str(native_repo), "checkout", "--quiet", "-B",
             "b3v4-native-test-source", assigned_head],
            stdin=subprocess.DEVNULL, check=True)
        repo = clone_source = native_repo
    candidate = base / "candidate-checkout"
    control = base / "control-checkout"
    for checkout in (candidate, control):
        subprocess.run(
            ["git", "clone", "--quiet", "--no-hardlinks",
             str(clone_source), str(checkout)],
            stdin=subprocess.DEVNULL, check=True)
    subprocess.run(
        ["git", "-C", str(control), "config", "user.email",
         "fixture@example.invalid"], check=True)
    subprocess.run(
        ["git", "-C", str(control), "config", "user.name",
         "Fixture Control"], check=True)
    (control / "CONTROL-IDENTITY.txt").write_text(
        "distinct frozen control identity\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(control), "add", "CONTROL-IDENTITY.txt"],
        check=True)
    subprocess.run(
        ["git", "-C", str(control), "commit", "--quiet", "-m",
         "fixture: distinct control identity"], check=True)
    head = subprocess.check_output(
        ["git", "-C", str(candidate), "rev-parse", "HEAD"],
        text=True).strip()
    tree = subprocess.check_output(
        ["git", "-C", str(candidate), "show", "-s", "--format=%T", "HEAD"],
        text=True).strip()
    packet = b3_freeze_fixture.valid_packet()
    packet["foundation"] = {"commit": head, "tree": tree}
    for name, checkout in (("candidate", candidate), ("control", control)):
        checkout_head = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            text=True).strip()
        checkout_tree = subprocess.check_output(
            ["git", "-C", str(checkout), "show", "-s", "--format=%T",
             "HEAD"], text=True).strip()
        skill_tree = subprocess.check_output(
            ["git", "-C", str(checkout), "rev-parse",
             "HEAD:skills/implementaudit"], text=True).strip()
        packet[name] = {
            "commit": checkout_head, "tree": checkout_tree,
            "skill_tree": skill_tree,
            "payload_sha256":
                adapters.payload_hash(checkout / "skills" / "implementaudit"),
        }
    validator = b3_freeze_fixture.load_validator()
    fixture_dir = repo / "eval" / "fixtures" / packet["fixture"]["id"]
    packet["fixture"]["fixture_sha256"] = validator._sha256(
        fixture_dir / "fixture.json")
    packet["fixture"]["complete_manifest_sha256"] = validator._tree_manifest(
        fixture_dir)
    artifact_paths = {
        "scorer": "eval/lib/scoring.py",
        "evaluator": "eval/validate_b3v4_freeze.py",
        "bundle": "eval/lib/bundle.py", "runner": "eval/runner.py",
    }
    packet["artifacts"] = {
        name: {"path": path, "sha256": validator._sha256(repo / path)}
        for name, path in artifact_paths.items()
    }
    packet["independent_rederiver"]["implementation_identity"]["sha256"] = \
        validator._sha256(repo / "eval" / "b3v4_rederive.py")
    acknowledgement = base / "owner-authorization.txt"
    acknowledgement.write_text(
        "owner-authorized Luna subscription launch\n", encoding="utf-8")
    packet["authorization"]["acknowledgement_path"] = str(acknowledgement)
    packet["authorization"]["acknowledgement_sha256"] = \
        validator._sha256(acknowledgement)
    b3_freeze_fixture.attach_surface_contract(packet)
    owners = packet["evaluated_surface_owners"]["roles"]
    for role in surfaces.FIXED_FILE_PATHS:
        path = surfaces.FIXED_FILE_PATHS[role]
        if role == "artifact-contract":
            continue
        if role == "official-driver":
            path = "eval/b3v4_campaign.py"
        if path is not None:
            owners[role]["sha256"] = validator._sha256(repo / path)
            if role in surfaces.GIT_IDENTITY_ROLES[surfaces.B3_CAMPAIGN]:
                owners[role].update(
                    {"git_commit": head, "git_tree": tree})
    for role in ("scorer", "evaluator", "host-runner",
                 "independent-rederiver"):
        owners[role].update({"git_commit": head, "git_tree": tree})
    host = base / "luna-host-attestation.json"
    write(host, {
        "id": "b3v4-L-host", "shell_dialect": "posix",
        "executables": {"cat": "posix:cat"},
    })
    topology = base / "checkout-runtime-topology.json"
    write(topology, {"candidate": str(candidate), "control": str(control)})
    launcher = base / "luna-launcher"
    launcher.write_text("# production launcher fixture\n", encoding="utf-8")
    owners["host-attestation"]["path"] = host.as_posix()
    packet["configurations"]["L"]["host_attestation"]["sha256"] = \
        validator._sha256(host)
    native = base / pathlib.Path(sys.executable).name
    shutil.copy2(sys.executable, native)
    python_dll = pathlib.Path(sys.executable).with_name(
        f"python{sys.version_info.major}{sys.version_info.minor}.dll")
    if python_dll.is_file():
        shutil.copy2(python_dll, base / python_dll.name)
    packet["configurations"]["L"]["executable"]["path"] = native.as_posix()
    packet["configurations"]["L"]["executable"]["sha256"] = \
        validator._sha256(native)
    owners["checkout-runtime-topology"].update({
        "path": topology.as_posix(), "sha256": validator._sha256(topology)})
    owners["launcher"].update({
        "path": launcher.as_posix(),
        "sha256": validator._sha256(launcher)})
    owners["prompt-template"].update({
        "path": "README.md", "sha256": validator._sha256(repo / "README.md")})
    for role, name, checkout in (
            ("product-candidate", "candidate", candidate),
            ("product-control", "control", control)):
        payload_root = checkout / "skills" / "implementaudit"
        commitment = bytearray()
        for root, dirs, files in os.walk(payload_root):
            dirs.sort()
            for filename in sorted(files):
                path = pathlib.Path(root) / filename
                relative = path.relative_to(payload_root).as_posix()
                commitment.extend(relative.encode())
                commitment.extend(path.read_bytes())
        projection = base / "surface" / name / "SKILL.md"
        projection.parent.mkdir(parents=True, exist_ok=True)
        projection.write_bytes(bytes(commitment))
        assert hashlib.sha256(commitment).hexdigest() == \
            packet[name]["payload_sha256"]
        owners[role]["path"] = projection.as_posix()
    packet["evaluated_surfaces"] = surfaces.build_manifest_from_packet(
        packet, surfaces.B3_CAMPAIGN, root=repo)
    runtime = base / "runtime"
    runtime.mkdir()
    auth = base / "auth-source.json"
    auth.touch()
    host_producer = base / "host-attestation-producer.py"
    host_producer.write_text(
        "import hashlib, pathlib, sys\n"
        "raw = pathlib.Path(sys.argv[1]).read_bytes()\n"
        "print('HOST_ATTESTATION_VALID=PASS sha256=' + "
        "hashlib.sha256(raw).hexdigest())\n",
        encoding="utf-8")
    context = {
        "repo_root": str(repo),
        "candidate_checkout": str(candidate),
        "control_checkout": str(control),
        "runtime_root": str(runtime),
        "campaign_root": str(base / "campaign"),
        "host_attestation_path": str(host),
        "launcher_path": str(launcher),
        "native_executable_path": str(native),
        "codex_auth_source_path": str(auth),
        "authorization_acknowledgement_path": str(acknowledgement),
        "created_at": "2026-07-29T00:00:00Z",
        "host_attestation_producer_argv": [
            sys.executable, str(host_producer), str(host)],
        "controller_argv": [
            str(native), str(pathlib.Path(preflight.__file__).resolve()),
            "author-production-ready"],
    }
    return packet, context


def exercise_production_driver_timing(base, timing, mutation):
    base = pathlib.Path(base)
    packet, context = production_fixture(base)
    packet_path = base / "campaign-freeze.json"
    context_path = base / "launch-context.json"
    readiness_path = base / "production-ready.json"
    write(packet_path, packet)
    write(context_path, context)
    preflight.author_production_live_ready(
        "b3v4", packet, context, readiness_path)
    calls = []

    def executor(_mission_context):
        calls.append("executor")
        raise AssertionError("executor must not run after live-state drift")

    driver = b3v4_campaign.CampaignDriver(
        packet_path=packet_path, repo_root=context["repo_root"],
        campaign_root=context["campaign_root"],
        candidate_checkout=context["candidate_checkout"],
        control_checkout=context["control_checkout"],
        runtime_root=context["runtime_root"],
        attestations={"L": context["host_attestation_path"]},
        execution_mode="production",
        codex_auth_source=context["codex_auth_source_path"],
        launch_readiness=readiness_path,
        launch_context=context_path)
    driver.mission_executor = executor
    driver.live_validator = lambda value, _root: value
    driver.identity_validator = lambda _packet, **_paths: None

    def mutate():
        if mutation == "checkout-dirty":
            pathlib.Path(
                context["candidate_checkout"], "dirty-live-state").write_text(
                    "drift\n", encoding="utf-8")
        elif mutation == "checkout-head-tree":
            checkout = pathlib.Path(context["candidate_checkout"])
            (checkout / "HEAD-DRIFT.txt").write_text(
                "drift\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(checkout), "add", "HEAD-DRIFT.txt"],
                check=True)
            subprocess.run(
                ["git", "-C", str(checkout), "config", "user.email",
                 "drift@example.invalid"], check=True)
            subprocess.run(
                ["git", "-C", str(checkout), "config", "user.name",
                 "Drift"], check=True)
            subprocess.run(
                ["git", "-C", str(checkout), "commit", "--quiet", "-m",
                 "drift"], check=True)
        elif mutation == "runtime":
            pathlib.Path(context["runtime_root"], "residue").write_text(
                "drift\n", encoding="utf-8")
        elif mutation == "native":
            with open(context["native_executable_path"], "ab") as stream:
                stream.write(b"drift")
        elif mutation == "launcher":
            pathlib.Path(context["launcher_path"]).write_text(
                "drift\n", encoding="utf-8")
        elif mutation == "auth-metadata":
            auth = pathlib.Path(context["codex_auth_source_path"])
            replacement = auth.with_suffix(".replacement")
            replacement.touch()
            os.replace(replacement, auth)
        elif mutation == "acknowledgement":
            pathlib.Path(
                context["authorization_acknowledgement_path"]).write_text(
                "changed authorization\n", encoding="utf-8")
        elif mutation == "host-attestation":
            pathlib.Path(context["host_attestation_path"]).write_text(
                "{}\n", encoding="utf-8")
        elif mutation == "path-translation":
            retained = json.loads(context_path.read_text(encoding="utf-8"))
            launcher = pathlib.Path(retained["launcher_path"])
            retained["launcher_path"] = str(
                launcher.parent / "translation" / ".." / launcher.name)
            write(context_path, retained)
        else:
            raise AssertionError("unknown live mutation")

    if timing == "before-root":
        mutate()
    elif timing == "before-claim":
        original = driver._ensure_campaign

        def mutate_before_claim(*args, **kwargs):
            result = original(*args, **kwargs)
            mutate()
            return result
        driver._ensure_campaign = mutate_before_claim
    elif timing == "before-executor":
        original = driver._claim_attempt

        def mutate_before_executor(*args, **kwargs):
            result = original(*args, **kwargs)
            mutate()
            return result
        driver._claim_attempt = mutate_before_executor
    else:
        raise AssertionError("unknown timing")
    expect_error(None, driver.run_luna_tranche)
    assert calls == []
    campaign_root = pathlib.Path(context["campaign_root"])
    attempts = (
        list(campaign_root.glob("attempt-*"))
        if campaign_root.exists() else [])
    if timing in ("before-root", "before-claim"):
        assert attempts == []


def exercise_initialized_b3_runtime_prefix_contract():
    """Production readiness must accept only the completed runtime prefix."""
    with tempfile.TemporaryDirectory(
            prefix="b3v4-initialized-runtime-prefix-") as tmp:
        base = pathlib.Path(tmp).absolute()
        packet, context = production_fixture(base)
        packet_path = base / "campaign-freeze.json"
        context_path = base / "launch-context.json"
        readiness_path = base / "production-ready.json"
        write(packet_path, packet)
        write(context_path, context)
        preflight.author_production_live_ready(
            "b3v4", packet, context, readiness_path)

        campaign = pathlib.Path(context["campaign_root"])
        campaign.mkdir()
        root_identity = preflight._directory_identity(
            campaign, "test initialized campaign")
        mission = packet["missions"][0]
        attempt_name = (
            f"attempt-{mission['index']:03d}-{mission['config']}-"
            f"{mission['arm']}-r{mission['rep']}")
        runtime = pathlib.Path(context["runtime_root"])
        completed_runtime = runtime / attempt_name
        completed_runtime.mkdir()

        second = packet["missions"][1]
        second_name = (
            f"attempt-{second['index']:03d}-{second['config']}-"
            f"{second['arm']}-r{second['rep']}")
        report, _ = preflight.validate_live_ready(
            "b3v4", packet, readiness_path,
            execution_mode="production", live_context=context,
            campaign_initialized=True,
            campaign_root_identity=root_identity,
            completed_prefix=[attempt_name])
        assert report["mission_authorized"] is True
        expect_error(
            "authoritative completed prefix",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, readiness_path,
                execution_mode="production", live_context=context,
                campaign_initialized=True,
                campaign_root_identity=root_identity))

        extra = runtime / "unexpected-runtime"
        extra.mkdir()
        expect_error(
            "runtime prefix",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, readiness_path,
                execution_mode="production", live_context=context,
                campaign_initialized=True,
                campaign_root_identity=root_identity,
                completed_prefix=[attempt_name]))
        extra.rmdir()

        gap = runtime / second_name
        completed_runtime.rename(gap)
        expect_error(
            "runtime prefix",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, readiness_path,
                execution_mode="production", live_context=context,
                campaign_initialized=True,
                campaign_root_identity=root_identity,
                completed_prefix=[attempt_name]))
        gap.rename(completed_runtime)

        expect_error(
            "authoritative completed prefix",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, readiness_path,
                execution_mode="production", live_context=context,
                campaign_initialized=True,
                campaign_root_identity=root_identity,
                completed_prefix=[second_name]))

        moved = base / "moved-runtime"
        completed_runtime.rename(moved)
        if os.name == "posix":
            completed_runtime.symlink_to(moved, target_is_directory=True)
            expect_error(
                "link",
                lambda: preflight.validate_live_ready(
                    "b3v4", packet, readiness_path,
                    execution_mode="production", live_context=context,
                    campaign_initialized=True,
                    campaign_root_identity=root_identity,
                    completed_prefix=[attempt_name]))
            completed_runtime.unlink()
        moved.rename(completed_runtime)


def fixtures(base):
    freeze = {
        "schema": "implementaudit-b3v4-freeze-input-preflight-v1",
        "disposition": "NOT_READY_TO_AUTHOR_FREEZE",
        "candidate_examined": {
            "branch": "fix/v0320-b3v4-freeze-sol",
            "commit": "1" * 40,
            "tree": "2" * 40,
            "clean_at_intake": True,
        },
        "packet_values": {
            "configurations": {
                "L": {
                    "model_requested": "gpt-5.6-luna",
                    "model_resolved_required": "gpt-5.6-luna",
                    "reasoning_effort": "max",
                    "auth_mode": "chatgpt-subscription",
                },
            },
            "authorization": {"metered_api_spend": "FORBIDDEN"},
        },
        "missing_or_ambiguous_inputs": [
            {"id": "host-attestations", "severity": "blocker",
             "detail": "formal Luna attestation absent"},
            {"id": "fresh-product-checkouts", "severity": "blocker",
             "detail": "fresh exact-tree checkouts absent"},
        ],
    }
    execution = {
        "schema": "implementaudit-b3v4-luna-execution-preflight-v1",
        "disposition": "NOT_READY_FOR_LUNA_EXECUTION",
        "read_only": True,
        "mission_executed": False,
        "freeze_created": False,
        "luna": {
            "model_requested": "gpt-5.6-luna",
            "model_resolved_required": "gpt-5.6-luna",
            "reasoning_effort": "max",
            "auth_mode": "chatgpt-subscription",
            "metered_api_spend": "FORBIDDEN",
            "auth_file_path": "/secret/auth.json",
            "auth_contents_read": False,
        },
        "blockers": [
            {"id": "LUNA_HOST_ATTESTATION_MISSING",
             "detail": "formal attestation absent"},
            {"id": "TEMP_AUTH_CUSTODY_UNBOUND",
             "detail": "auth copy boundary absent"},
        ],
    }
    freeze_path = base / "freeze.json"
    execution_path = base / "execution.json"
    write(freeze_path, freeze)
    write(execution_path, execution)
    return freeze_path, execution_path, freeze, execution


def main():
    exercise_path_type_custody()

    # Round-3 governing RED: production readiness is controller-derived from
    # an explicit live launch context.  A caller-authored report is never the
    # production authoring API.
    with tempfile.TemporaryDirectory(
            prefix="live-ready-production-author-red-") as tmp:
        base = pathlib.Path(tmp)
        packet = {
            "artifact_contract": {"sha256": "a" * 64},
            "configurations": {"L": {
                "host_attestation": {
                    "id": "b3v4-L-host", "sha256": "b" * 64},
            }},
        }
        expect_error(
            "Git worktree",
            lambda: preflight.author_production_live_ready(
                "b3v4", packet, {
                    "repo_root": str(base),
                    "candidate_checkout": str(base / "fake-candidate"),
                    "control_checkout": str(base / "fake-control"),
                    "runtime_root": str(base / "runtime"),
                    "campaign_root": str(base / "campaign"),
                    "host_attestation_path": str(base / "host.json"),
                    "launcher_path": str(base / "launcher"),
                    "native_executable_path": str(base / "native"),
                    "codex_auth_source_path": str(base / "auth.json"),
                    "authorization_acknowledgement_path":
                        str(base / "ack.json"),
                    "created_at": "2026-07-29T00:00:00Z",
                    "host_attestation_producer_argv":
                        [sys.executable, "--version"],
                    "controller_argv": [
                        sys.executable, "campaign_freeze_preflight.py"],
                }, base / "production-ready.json"))

    with tempfile.TemporaryDirectory(
            prefix="live-ready-production-author-green-") as tmp:
        base = pathlib.Path(tmp)
        packet, context = production_fixture(base)
        output = base / "production-ready.json"
        checkout_collision = copy.deepcopy(context)
        checkout_collision["campaign_root"] = \
            checkout_collision["candidate_checkout"]
        expect_error(
            "overlap",
            lambda: preflight._derive_production_live_ready(
                "b3v4", packet, checkout_collision))
        authored = preflight.author_production_live_ready(
            "b3v4", packet, context, output)
        assert authored["campaign_root_binding"]["path"] == \
            context["campaign_root"]
        assert authored["campaign_root_binding"]["initial_state"] == \
            "ABSENT_CREATE_ONCE"
        assert authored["ready"] is True
        reread, raw = preflight.validate_live_ready(
            "b3v4", packet, output, execution_mode="production",
            live_context=context)
        assert reread == authored
        assert raw == preflight.lifecycle.canonical_json_bytes(authored)
        assert (
            reread["authorization_binding"][
                "codex_auth_source_path"] ==
            context["codex_auth_source_path"])
        assert (base / "auth-source.json").read_bytes() == b""
        dirty = pathlib.Path(
            context["candidate_checkout"]) / "untracked.txt"
        dirty.write_text("drift\n", encoding="utf-8")
        expect_error(
            "dirty",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, output, execution_mode="production",
                live_context=context))
        dirty.unlink()
        pathlib.Path(context["runtime_root"], "residue").write_text(
            "drift\n", encoding="utf-8")
        expect_error(
            "initially empty",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, output, execution_mode="production",
                live_context=context))

    if os.name == "posix":
        exercise_initialized_b3_runtime_prefix_contract()
        for timing in ("before-root", "before-claim", "before-executor"):
            for mutation in (
                    "checkout-dirty", "checkout-head-tree", "runtime",
                    "native", "launcher", "auth-metadata",
                    "acknowledgement", "host-attestation",
                    "path-translation"):
                with tempfile.TemporaryDirectory(
                        prefix=f"live-ready-{timing}-{mutation}-") as tmp:
                    exercise_production_driver_timing(
                        tmp, timing, mutation)
    else:
        print("PRODUCTION_CONTINUOUS_CUSTODY_TIMING=SKIP:requires-posix")

    # Governing round-2 RED: the implementation must expose the separate live
    # packet-bound READY validator; legacy NOT_READY conversion is insufficient.
    expect_error(
        "live READY",
        lambda: preflight.validate_live_ready(
            "b3v4", {}, pathlib.Path("missing-live-boundary.json")))

    with tempfile.TemporaryDirectory(prefix="live-ready-mode-boundary-") as tmp:
        packet = {
            "artifact_contract": {"sha256": "a" * 64},
            "configurations": {"L": {
                "host_attestation": {
                    "id": "b3v4-L-host", "sha256": "b" * 64},
            }},
        }
        report_path = write_test_live_ready(
            "b3v4", packet, pathlib.Path(tmp) / "ready")
        report, _ = preflight.validate_live_ready(
            "b3v4", packet, report_path, execution_mode="test")
        assert report["disposition"] == "TEST_ONLY_NON_QUALIFYING"
        expect_error(
            "mode",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, report_path,
                execution_mode="production"))
        report_value = json.loads(
            pathlib.Path(report_path).read_text(encoding="utf-8"))
        campaign_leaf = pathlib.Path(
            report_value["campaign_root_binding"]["path"])
        campaign_leaf.mkdir()
        expect_error(
            "absent",
            lambda: preflight.validate_live_ready(
                "b3v4", packet, report_path, execution_mode="test"))
        campaign_leaf.rmdir()

        campaign_parent = pathlib.Path(
            report_value["campaign_root_binding"]["parent_path"])
        real_lstat = os.lstat

        class DriftedParentStat:
            def __init__(self, observed):
                self._observed = observed
                self.st_ino = observed.st_ino + 1

            def __getattr__(self, name):
                return getattr(self._observed, name)

        def drifted_parent_lstat(path, *args, **kwargs):
            observed = real_lstat(path, *args, **kwargs)
            if pathlib.Path(path).absolute() == campaign_parent:
                return DriftedParentStat(observed)
            return observed

        with mock.patch.object(
                preflight.os, "lstat", side_effect=drifted_parent_lstat):
            expect_error(
                "binding drift",
                lambda: preflight.validate_live_ready(
                    "b3v4", packet, report_path, execution_mode="test"))

    with tempfile.TemporaryDirectory(prefix="campaign-preflight-") as tmp:
        base = pathlib.Path(tmp)
        freeze_path, execution_path, freeze, execution = fixtures(base)
        for campaign, schema in (
                ("b3v4", "implementaudit-b3v4-luna-freeze-preflight-v1"),
                ("candidate-matrix",
                 "implementaudit-candidate-matrix-luna-freeze-preflight-v1")):
            output = base / f"{campaign}.json"
            report = preflight.inspect_legacy_preflights(
                campaign, freeze_path, execution_path, output)
            assert report["schema"] == schema
            assert report["disposition"] == "NOT_READY"
            assert report["ready"] is False
            assert report["model_scope"] == {
                "model": "gpt-5.6-luna",
                "reasoning_effort": "max",
                "auth_mode": "chatgpt-subscription",
                "metered_api_spend": "FORBIDDEN",
            }
            raw = output.read_text(encoding="utf-8")
            assert "auth.json" not in raw
            assert "secret" not in raw
            expect_error(
                "create-once",
                lambda: preflight.inspect_legacy_preflights(
                    campaign, freeze_path, execution_path, output))

        for label, mutate, fragment in (
                ("ready", lambda f, e: f.update(
                    disposition="READY_TO_AUTHOR_FREEZE"), "not-ready"),
                ("terra", lambda f, e: f["packet_values"][
                    "configurations"]["L"].update(
                        model_requested="gpt-5.6-terra"), "luna"),
                ("unauthorized-config", lambda f, e: f["packet_values"][
                    "configurations"].update(T={}), "luna-only"),
                ("metered", lambda f, e: f["packet_values"][
                    "authorization"].update(
                        metered_api_spend="ALLOWED"), "metered"),
                ("contents", lambda f, e: e["luna"].update(
                    auth_contents_read=True), "credential")):
            changed_f = copy.deepcopy(freeze)
            changed_e = copy.deepcopy(execution)
            mutate(changed_f, changed_e)
            fp = base / f"{label}-freeze.json"
            ep = base / f"{label}-execution.json"
            write(fp, changed_f)
            write(ep, changed_e)
            expect_error(
                fragment,
                lambda fp=fp, ep=ep, label=label:
                preflight.inspect_legacy_preflights(
                    "b3v4", fp, ep, base / f"{label}-out.json"))

        expect_error(
            "campaign",
            lambda: preflight.inspect_legacy_preflights(
                "opus", freeze_path, execution_path, base / "bad.json"))
    print("CAMPAIGN-FREEZE-PREFLIGHT-PASS")


if __name__ == "__main__":
    main()
