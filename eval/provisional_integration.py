#!/usr/bin/env python3
"""Custody-derived certificate for the Luna-qualified merge disposition."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
import stat
import subprocess
import zipfile

import b3v4_campaign
import b3v4_contract
import b3v4_rederive
import campaign_lifecycle as lifecycle
import candidate_matrix_campaign
import candidate_matrix_contract
import candidate_matrix_rederive
import evaluated_surfaces as surfaces


SCHEMA = "implementaudit-luna-qualified-integration-certificate-v3"
CERTIFICATE_FILENAME = "luna-qualified-integration-certificate.json"
DISPOSITION = "LUNA_6_OF_6_AND_14_OF_14_GREEN_MERGED_TO_MAIN"
REQUIRED_GATES = (
    "deterministic", "package", "ci", "reproducibility",
    "independent-review",
)
GATE_FILENAMES = {
    name: f"{name}-terminal.json" for name in REQUIRED_GATES
}
GATE_COMMANDS = {
    "deterministic": "combined-focused-exact-sha",
    "package": "scripts/verify-package.sh",
    "ci": ".github/workflows/validate.yml",
    "reproducibility": "tests/reproducible-release-asset.test.sh",
    "independent-review": "fresh-read-only-complete-boundary-review",
}
GATE_PRODUCER_ROLES = {
    "deterministic": "qualification-runner",
    "package": "package-runner",
    "ci": "ci-runner",
    "reproducibility": "reproducibility-runner",
    "independent-review": "independent-read-only-reviewer",
}
TOOLING_SOURCE_PATHS = (
    "eval/provisional_integration.py",
    "eval/qualification_evidence_producer.py",
    "scripts/build-release-asset.sh",
    "scripts/verify-package.sh",
    "tests/reproducible-release-asset.test.sh",
)
DETERMINISTIC_CHECKS = (
    "compile", "lifecycle", "b3-contract", "b3-freeze", "b3-campaign",
    "b3-rederive", "matrix-contract", "matrix-freeze", "matrix-campaign",
    "matrix-rederive", "surfaces", "integration", "preflight",
    "historical", "adversarial", "reporting", "reproducibility",
    "registry-diff",
)
DETERMINISTIC_COMMANDS = {
    "compile": [sys.executable, "-m", "py_compile",
                "eval/campaign_lifecycle.py",
                "eval/b3v4_campaign.py", "eval/b3v4_rederive.py",
                "eval/candidate_matrix_campaign.py",
                "eval/candidate_matrix_rederive.py",
                "eval/evaluated_surfaces.py",
                "eval/campaign_freeze_preflight.py",
                "eval/historical_readjudicate.py",
                "eval/qualification_evidence_producer.py",
                "eval/provisional_integration.py"],
    "lifecycle": [sys.executable, "eval/test_campaign_lifecycle.py"],
    "b3-contract": [sys.executable, "eval/test_b3v4_contract_matrix.py"],
    "b3-freeze": [sys.executable, "eval/test_b3v4_freeze.py"],
    "b3-campaign": [sys.executable, "eval/test_b3v4_campaign.py"],
    "b3-rederive": [sys.executable, "eval/test_b3v4_rederive.py"],
    "matrix-contract":
        [sys.executable, "eval/test_candidate_matrix_contract.py"],
    "matrix-freeze":
        [sys.executable, "eval/test_candidate_matrix_freeze.py"],
    "matrix-campaign":
        [sys.executable, "eval/test_candidate_matrix_campaign.py"],
    "matrix-rederive":
        [sys.executable, "eval/test_candidate_matrix_rederive.py"],
    "surfaces": [sys.executable, "eval/test_evaluated_surfaces.py"],
    "integration": [sys.executable, "eval/test_provisional_integration.py"],
    "preflight": [sys.executable, "eval/test_campaign_freeze_preflight.py"],
    "historical": [sys.executable, "eval/test_historical_readjudicate.py"],
    "adversarial": [sys.executable, "eval/adversarial.py"],
    "reporting": [sys.executable, "eval/test_reporting.py"],
    "reproducibility": [
        "bash", "tests/reproducible-release-asset.test.sh"],
    "registry-diff": ["git", "diff", "--check"],
}
CI_JOBS = ("package",)

PACKAGE_MANIFEST_SCHEMA = "implementaudit-package-entry-manifest-v3"
PACKAGE_REQUIRED_PATHS = (
    "SKILL.md",
    "references/planning-depth.md",
    "references/phase-design.md",
    "references/goal-format.md",
    "references/transcript-contract.md",
    "references/continuity.md",
    "references/routing.md",
    "references/repo-state-comparison.md",
    "references/sidecars.md",
    "references/child-agents.md",
    "references/lean-operating-discipline.md",
    "references/audit-category-matrix.md",
    "references/audit-playbook.md",
    "references/plan-lifecycle.md",
    "references/terminology-integration.md",
    "references/convergence-mode.md",
    "scripts/check-evidence-anchor.sh",
    "scripts/check-lesson-lift.sh",
    "scripts/check-handoff-packet.sh",
    "scripts/check-closure-surface.sh",
    "scripts/check-authorization-binding.sh",
    "scripts/claim-run.sh",
    "scripts/detect-env.sh",
    "scripts/detect-stack.sh",
    "scripts/repo-state.sh",
    "scripts/summarize-repo.sh",
    "scripts/validate-audit-spec.sh",
    "scripts/validate-phase.sh",
    "scripts/validate-run-root.sh",
    "scripts/custody-append.sh",
    "templates/ROADMAP.md",
    "templates/STATE.md",
    "templates/THINKING.md",
    "templates/phase-goal.txt",
    "templates/child-agent-report.md",
    "templates/final-report.md",
    "templates/read-only-plan.md",
    "templates/PROTOCOL.md",
    "templates/sidecars.md",
    "templates/tools.md",
    "templates/context.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
)
PACKAGE_ALLOWED_TOP_LEVEL = {
    "SKILL.md", "references", "scripts", "templates", ".claude-plugin",
}


def _zip_entry_row(info, payload):
    return {
        "path": info.filename,
        "byte_length": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "mode": (info.external_attr >> 16) & 0xffff,
        "compression": info.compress_type,
        "timestamp": list(info.date_time),
        "create_system": info.create_system,
    }


def _git_bytes(repo_root, source_sha, path):
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{source_sha}:{path}"],
        stdin=subprocess.DEVNULL, capture_output=True, check=False)
    if completed.returncode != 0:
        raise ValueError(f"package source path absent from target: {path}")
    return completed.stdout


def _source_bound_archive_payload(repo_root, source_sha, archive_path):
    if archive_path == ".claude-plugin/plugin.json":
        source_path = ".claude-plugin/plugin.json"
        try:
            value = json.loads(
                _git_bytes(repo_root, source_sha, source_path).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("package source plugin metadata invalid") from exc
        value["skills"] = "./"
        payload = (json.dumps(value, indent=2) + "\n").encode("utf-8")
        transform = "plugin-skills-root-v1"
    elif archive_path == ".claude-plugin/marketplace.json":
        source_path = ".claude-plugin/marketplace.json"
        try:
            value = json.loads(
                _git_bytes(repo_root, source_sha, source_path).decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(
                "package source marketplace metadata invalid") from exc
        for plugin in value.get("plugins", []):
            if type(plugin) is dict and plugin.get("name") == "implementaudit":
                plugin.pop("source", None)
                plugin["path"] = ".."
        payload = (json.dumps(value, indent=2) + "\n").encode("utf-8")
        transform = "marketplace-flatten-v1"
    else:
        source_path = f"skills/implementaudit/{archive_path}"
        payload = _git_bytes(repo_root, source_sha, source_path)
        if pathlib.PurePosixPath(archive_path).suffix.lower() in {
                ".md", ".txt", ".sh", ".json", ".yaml", ".yml"}:
            payload = payload.replace(b"\r\n", b"\n")
            transform = "text-crlf-to-lf-v1"
        else:
            transform = "identity-v1"
    return source_path, payload, transform


def validate_package_archive(archive_path, entry_manifest,
                             source_sha, source_tree, repo_root=None):
    """Validate a retained IMPLEMENTAUDIT .skill and its exact entry manifest."""
    for value, owner in ((source_sha, "source SHA"),
                         (source_tree, "source tree")):
        if (type(value) is not str or len(value) != 40 or
                any(char not in "0123456789abcdef" for char in value)):
            raise ValueError(f"package {owner} invalid")
    archive_path = pathlib.Path(archive_path)
    try:
        with zipfile.ZipFile(archive_path):
            pass
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError("package archive invalid") from exc
    repo_root = pathlib.Path(
        repo_root if repo_root is not None
        else pathlib.Path(__file__).resolve().parent.parent).absolute()
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "show", "-s", "--format=%T",
         source_sha],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
    if completed.returncode != 0 or completed.stdout.strip() != source_tree:
        raise ValueError("package target Git SHA/tree binding invalid")
    if isinstance(entry_manifest, (str, os.PathLike)):
        manifest_path = pathlib.Path(entry_manifest)
        manifest_raw = lifecycle.read_custodied_bytes(
            manifest_path, "package entry manifest",
            root=manifest_path.parent)
        entry_manifest = lifecycle.decode_strict_json_bytes(
            manifest_raw, "package entry manifest", require_object=True)
    if type(entry_manifest) is not dict:
        raise ValueError("package entry manifest must be an object")
    _exact(entry_manifest, {
        "schema", "source_sha", "source_tree", "builder_source_path",
        "builder_source_sha256", "entries",
    }, "package entry manifest")
    builder_path = "scripts/build-release-asset.sh"
    builder_raw = _git_bytes(repo_root, source_sha, builder_path)
    if (entry_manifest["schema"] != PACKAGE_MANIFEST_SCHEMA or
            entry_manifest["source_sha"] != source_sha or
            entry_manifest["source_tree"] != source_tree or
            entry_manifest["builder_source_path"] != builder_path or
            entry_manifest["builder_source_sha256"] !=
            hashlib.sha256(builder_raw).hexdigest() or
            type(entry_manifest["entries"]) is not list):
        raise ValueError("package entry manifest identity invalid")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise ValueError("package archive duplicate entry")
            observed = []
            for info in infos:
                pure = pathlib.PurePosixPath(info.filename)
                if (info.is_dir() or pure.is_absolute() or
                        ".." in pure.parts or "\\" in info.filename or
                        not pure.parts or
                        pure.parts[0] not in PACKAGE_ALLOWED_TOP_LEVEL or
                        info.flag_bits & 0x1):
                    raise ValueError("package archive entry is not portable")
                mode = (info.external_attr >> 16) & 0xffff
                if (info.create_system != 3 or
                        stat.S_IFMT(mode) != stat.S_IFREG or
                        info.compress_type != zipfile.ZIP_DEFLATED or
                        info.extra or info.comment):
                    raise ValueError(
                        "package archive regular-file metadata invalid")
                payload = archive.read(info)
                if info.file_size != len(payload):
                    raise ValueError("package archive entry length invalid")
                source_path, expected_payload, _transform = \
                    _source_bound_archive_payload(
                        repo_root, source_sha, info.filename)
                if payload != expected_payload:
                    raise ValueError(
                        "package archive entry differs from target Git tree: "
                        f"{info.filename} ({source_path})")
                observed.append(_zip_entry_row(info, payload))
            missing = sorted(set(PACKAGE_REQUIRED_PATHS) - set(names))
            if missing:
                raise ValueError(
                    "package archive required entries missing: " +
                    ", ".join(missing))
            source_names = subprocess.run(
                ["git", "-C", str(repo_root), "ls-tree", "-r",
                 "--name-only", source_sha, "skills/implementaudit"],
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                check=False)
            if source_names.returncode != 0:
                raise ValueError("package target skill tree unavailable")
            expected_names = {
                path.removeprefix("skills/implementaudit/")
                for path in source_names.stdout.splitlines()
            } | {
                ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
            }
            if set(names) != expected_names:
                raise ValueError(
                    "package archive does not exactly cover target skill tree")
            plugin = json.loads(
                archive.read(".claude-plugin/plugin.json").decode("utf-8"))
            marketplace = json.loads(
                archive.read(
                    ".claude-plugin/marketplace.json").decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError,
            zipfile.BadZipFile, KeyError) as exc:
        raise ValueError("package archive invalid") from exc
    if (type(plugin) is not dict or plugin.get("name") != "implementaudit" or
            plugin.get("skills") != "./"):
        raise ValueError("package archive plugin metadata invalid")
    plugins = marketplace.get("plugins") if type(marketplace) is dict else None
    matching = [
        item for item in plugins or []
        if type(item) is dict and item.get("name") == "implementaudit"
    ]
    if (len(matching) != 1 or matching[0].get("path") != ".." or
            "source" in matching[0]):
        raise ValueError("package archive marketplace metadata invalid")
    if entry_manifest["entries"] != observed:
        raise ValueError("package entry manifest does not match archive bytes")
    return observed


def _exact(value, fields, owner):
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(f"{owner} terminal schema fields invalid")
    return value


def _digest(value, owner):
    if (type(value) is not str or len(value) != 64 or
            any(char not in "0123456789abcdef" for char in value)):
        raise ValueError(f"{owner} SHA-256 invalid")


def _bash_identity(observed):
    return {
        "device": observed.st_dev,
        "inode": observed.st_ino,
        "mode": observed.st_mode,
        "size": observed.st_size,
        "mtime_ns": observed.st_mtime_ns,
    }


def _observe_production_bash(path):
    if type(path) is not str or not pathlib.Path(path).is_absolute():
        raise ValueError("production bash executable path invalid")
    lexical = pathlib.Path(path).absolute()
    if os.name == "nt" and os.path.normcase(os.path.normpath(str(lexical))) != \
            os.path.normcase(os.path.normpath(
                r"C:\Program Files\Git\bin\bash.exe")):
        raise ValueError(
            "production bash must be the explicit Git-for-Windows executable")
    try:
        canonical = lexical.resolve(strict=True)
        if canonical != lexical:
            raise ValueError(
                "production bash link or reparse alias forbidden")
        before = os.lstat(lexical)
        raw = lifecycle.read_custodied_bytes(
            lexical, "production bash executable")
        completed = subprocess.run(
            [str(canonical), "--version"], stdin=subprocess.DEVNULL,
            capture_output=True, check=False, shell=False)
        after = os.lstat(lexical)
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError("production bash executable unavailable") from exc
    identity = _bash_identity(before)
    if identity != _bash_identity(after) or before.st_size != len(raw):
        raise ValueError(
            "production bash identity changed during custody read")
    if completed.returncode != 0:
        raise ValueError("production bash version command failed")
    try:
        stdout = completed.stdout.decode("utf-8", errors="strict")
        stderr = completed.stderr.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("production bash version output is not UTF-8") from exc
    return {
        "path": str(lexical),
        "canonical_path": str(canonical),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "file_identity": identity,
        "version_argv": [str(canonical), "--version"],
        "version_exit_code": completed.returncode,
        "version_stdout": stdout,
        "version_stdout_sha256":
            hashlib.sha256(completed.stdout).hexdigest(),
        "version_stderr": stderr,
        "version_stderr_sha256":
            hashlib.sha256(completed.stderr).hexdigest(),
    }


def _validate_production_bash_binding(value):
    _exact(value, {
        "path", "canonical_path", "sha256", "byte_length",
        "file_identity", "version_argv", "version_exit_code",
        "version_stdout", "version_stdout_sha256",
        "version_stderr", "version_stderr_sha256",
    }, "production bash executable")
    _exact(value["file_identity"], {
        "device", "inode", "mode", "size", "mtime_ns",
    }, "production bash file identity")
    _digest(value["sha256"], "production bash executable")
    _digest(value["version_stdout_sha256"], "production bash version stdout")
    _digest(value["version_stderr_sha256"], "production bash version stderr")
    if (type(value["byte_length"]) is not int or
            value["byte_length"] < 1 or
            any(type(value["file_identity"][key]) is not int
                for key in value["file_identity"]) or
            type(value["version_argv"]) is not list or
            value["version_argv"] !=
            [value["canonical_path"], "--version"] or
            type(value["version_exit_code"]) is not int or
            value["version_exit_code"] != 0 or
            type(value["version_stdout"]) is not str or
            not value["version_stdout"] or
            type(value["version_stderr"]) is not str):
        raise ValueError("production bash executable binding invalid")
    observed = _observe_production_bash(value["path"])
    if observed != value:
        raise ValueError(
            "production bash executable does not match local bytes and version")
    return observed


def _reparse_point(path_stat):
    return bool(getattr(path_stat, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _strict_directory_identity(path, owner):
    lexical = pathlib.Path(path).absolute()
    try:
        resolved = lexical.resolve(strict=True)
        if resolved != lexical:
            raise ValueError(f"{owner} link or reparse alias forbidden")
        current = pathlib.Path(lexical.anchor)
        for part in lexical.parts[1:]:
            current = current / part
            observed = os.lstat(current)
            if stat.S_ISLNK(observed.st_mode) or _reparse_point(observed):
                raise ValueError(f"{owner} link or reparse alias forbidden")
        before = os.lstat(lexical)
        if (not stat.S_ISDIR(before.st_mode) or
                stat.S_ISLNK(before.st_mode) or _reparse_point(before)):
            raise ValueError(f"{owner} must be a retained directory")
        after = os.lstat(lexical)
        if ((before.st_dev, before.st_ino, before.st_mode) !=
                (after.st_dev, after.st_ino, after.st_mode)):
            raise ValueError(f"{owner} identity changed during custody read")
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(f"{owner} retained directory unavailable") from exc
    return lexical, {
        "path": str(lexical),
        "canonical_path": str(resolved),
        "lexical": os.path.normcase(os.path.normpath(str(lexical))),
        "canonical": os.path.normcase(os.path.normpath(str(resolved))),
        "physical": (before.st_dev, before.st_ino),
    }


def _strict_directory(path, owner):
    return _strict_directory_identity(path, owner)[0]


def _identity_tokens(identity):
    return {
        ("lexical", identity["lexical"]),
        ("canonical", identity["canonical"]),
        ("physical", identity["physical"]),
    }


def _path_overlap(left, right):
    left = os.path.normcase(os.path.normpath(str(left)))
    right = os.path.normcase(os.path.normpath(str(right)))
    try:
        common = os.path.commonpath([left, right])
    except ValueError:
        return False
    return common in (left, right)


def _validate_certificate_root(certificate_root, roots):
    root, identity = _strict_directory_identity(
        certificate_root, "integration certificate root")
    input_roots = {
        name: _strict_directory_identity(path, name)[1]
        for name, path in roots.items()
        if name in {
            "b3_campaign_root", "matrix_campaign_root",
            "b3_surface_root", "matrix_surface_root",
            "b3_after_surface_root", "matrix_after_surface_root",
            "gate_root",
        }
    }
    for owner, prior in input_roots.items():
        if (_identity_tokens(identity) & _identity_tokens(prior) or
                _path_overlap(identity["canonical"],
                              prior["canonical"])):
            raise ValueError(
                f"integration certificate root aliases or overlaps {owner}")
    leaf = root / CERTIFICATE_FILENAME
    if leaf.exists():
        raise ValueError("create-once integration certificate exists")
    return root, identity


def _validate_certificate_external_disjoint(identity, roots):
    paths = []
    for key in ("b3_after_external_paths", "matrix_after_external_paths"):
        mapping = roots.get(key) or {}
        if type(mapping) is not dict:
            raise ValueError(f"{key} must be an object")
        paths.extend(mapping.values())
    for campaign_key, surface_key in (
            ("b3_campaign_root", "b3_surface_root"),
            ("matrix_campaign_root", "matrix_surface_root")):
        campaign_root = pathlib.Path(roots[campaign_key]).absolute()
        packet, _raw = _read_root_json(
            campaign_root, "campaign-freeze.json",
            f"{campaign_key} certificate custody packet")
        surface_root = pathlib.Path(roots[surface_key]).absolute()
        for row in packet["evaluated_surfaces"]["entries"]:
            if (row["role"] in surfaces.INLINE_ROLES and
                    row["path"] == surfaces.projection_path(row["role"])):
                continue
            stored = pathlib.Path(row["path"])
            paths.append(stored if stored.is_absolute()
                         else surface_root / pathlib.PurePosixPath(row["path"]))
    for path in paths:
        lexical = pathlib.Path(path).absolute()
        try:
            canonical = lexical.resolve(strict=True)
        except OSError as exc:
            raise ValueError(
                "integration certificate external locator unavailable") from exc
        if (_path_overlap(identity["lexical"], lexical) or
                _path_overlap(identity["canonical"], canonical)):
            raise ValueError(
                "integration certificate root overlaps retained input file")


def _require_distinct_post_roots(pre_roots, post_roots):
    prior = []
    for campaign, identity in pre_roots.items():
        prior.append((f"{campaign} frozen pre root", identity))
    for campaign, identity in post_roots.items():
        for owner, previous in prior:
            if _identity_tokens(identity) & _identity_tokens(previous):
                raise ValueError(
                    f"{campaign} post-integration root identity aliases "
                    f"{owner}")
        prior.append((f"{campaign} post-integration root", identity))


def _require_post_files_distinct_from_pre(
        post_campaign, post_identities, pre_identities):
    prior = {}
    for campaign, roles in pre_identities.items():
        for role, identity in roles.items():
            for token in _identity_tokens(identity):
                prior[token] = f"{campaign}:{role}"
    for role, identity in post_identities.items():
        aliases = {
            prior[token] for token in _identity_tokens(identity)
            if token in prior
        }
        if aliases:
            raise ValueError(
                f"{post_campaign} post-integration surface {role} aliases "
                f"pre-integration physical identity {sorted(aliases)[0]}")


def _canonical_sha(value):
    return hashlib.sha256(lifecycle.canonical_json_bytes(value)).hexdigest()


def _read_root_json(root, name, owner):
    path = pathlib.Path(root) / name
    raw = lifecycle.read_custodied_bytes(path, owner, root=root)
    value = lifecycle.decode_strict_json_bytes(
        raw, owner, require_object=True)
    return value, raw


def _packet_and_manifest(campaign_root, surface_root, campaign):
    campaign_root = _strict_directory(campaign_root, f"{campaign} campaign root")
    surface_root = _strict_directory(surface_root, f"{campaign} surface root")
    packet, raw = _read_root_json(
        campaign_root, "campaign-freeze.json", f"{campaign} frozen packet")
    if campaign == surfaces.B3_CAMPAIGN:
        b3v4_contract.validate_freeze_envelope(packet)
    else:
        candidate_matrix_contract.validate_freeze_envelope(packet)
    manifest = packet["evaluated_surfaces"]
    surfaces.validate_packet_surfaces(packet, campaign, root=surface_root)
    return packet, raw, manifest


def _result_fields(campaign):
    if campaign == surfaces.B3_CAMPAIGN:
        return (
            "b3v4-luna-result.json",
            "b3v4-luna-independent-rederivation.json",
            "missions", "mission_count", 6)
    return (
        "candidate-matrix-luna-result.json",
        "candidate-matrix-luna-independent-rederivation.json",
        "cells", "cell_count", 14)


def _validate_stage(campaign_root, surface_root, campaign):
    packet, packet_raw, manifest = _packet_and_manifest(
        campaign_root, surface_root, campaign)
    packet_path = pathlib.Path(campaign_root) / "campaign-freeze.json"
    if campaign == surfaces.B3_CAMPAIGN:
        official = b3v4_campaign.validate_retained_luna_stage(
            packet_path, campaign_root, surface_root)
        rederived = b3v4_rederive.rederive_campaign(
            packet_path, campaign_root, surface_root)
    else:
        official = candidate_matrix_campaign.validate_retained_luna_stage(
            packet_path, campaign_root, surface_root)
        rederived = candidate_matrix_rederive.rederive_campaign(
            packet_path, campaign_root, surface_root)
    official_name, independent_name, rows_name, count_name, target = \
        _result_fields(campaign)
    retained_official, official_raw = _read_root_json(
        campaign_root, official_name, f"{campaign} official retained result")
    retained_independent, independent_raw = _read_root_json(
        campaign_root, independent_name,
        f"{campaign} independent retained result")
    terminal, terminal_raw = _read_root_json(
        campaign_root, "luna-stage-terminal.json",
        f"{campaign} retained stage terminal")
    if (lifecycle.canonical_json_bytes(retained_official) !=
            lifecycle.canonical_json_bytes(official)):
        raise ValueError(f"{campaign} official retained result drift")
    if (lifecycle.canonical_json_bytes(retained_independent) !=
            lifecycle.canonical_json_bytes(rederived)):
        raise ValueError(f"{campaign} independent retained result drift")
    if (type(official.get(count_name)) is not int or
            official[count_name] != target or
            type(rederived.get(count_name)) is not int or
            rederived[count_name] != target or
            official.get("luna_stage_accepted") is not True or
            rederived.get("luna_stage_accepted") is not True or
            official.get("accepted") is not False or
            rederived.get("accepted") is not False or
            official.get("disposition") != "INCOMPLETE_PENDING_OPUS" or
            rederived.get("disposition") != "INCOMPLETE_PENDING_OPUS"):
        raise ValueError(f"{campaign} retained Luna stage is not accepted")
    if (lifecycle.canonical_json_bytes(official.get(rows_name)) !=
            lifecycle.canonical_json_bytes(rederived.get(rows_name))):
        raise ValueError(f"{campaign} official/independent row disagreement")
    return {
        "campaign": campaign,
        "freeze_sha256": hashlib.sha256(packet_raw).hexdigest(),
        "contract_sha256": packet["artifact_contract"]["sha256"],
        "official_result_sha256": hashlib.sha256(official_raw).hexdigest(),
        "independent_rederivation_sha256":
            hashlib.sha256(independent_raw).hexdigest(),
        "stage_terminal_sha256": hashlib.sha256(terminal_raw).hexdigest(),
        "stage_snapshot_sha256": terminal["stage_snapshot_sha256"],
        "accepted_count": target,
        "execution_mode": "production",
    }, manifest, packet


def _gate_identity(b3, matrix, manifests):
    return _canonical_sha({
        "b3_freeze_sha256": b3["freeze_sha256"],
        "matrix_freeze_sha256": matrix["freeze_sha256"],
        "b3_evaluated_surfaces_sha256":
            _canonical_sha(manifests[surfaces.B3_CAMPAIGN]),
        "matrix_evaluated_surfaces_sha256":
            _canonical_sha(manifests[surfaces.MATRIX_CAMPAIGN]),
    })


def _tooling_source_manifest(target_sha, target_tree):
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    return {
        "schema": "implementaudit-tooling-source-manifest-v1",
        "target_sha": target_sha,
        "target_tree": target_tree,
        "files": [{
            "path": path,
            "byte_length": len(_git_bytes(repo_root, target_sha, path)),
            "sha256": hashlib.sha256(
                _git_bytes(repo_root, target_sha, path)).hexdigest(),
        } for path in TOOLING_SOURCE_PATHS],
    }


def _validate_qualification_identity(
        name, value, qualified_input_sha256, target_sha, target_tree,
        campaign_qualified_input_sha256, evaluated_surfaces_sha256):
    if type(value) is not dict:
        raise ValueError("qualification identity must be an object")
    scope = value.get("qualification_scope")
    if scope == "TOOLING_EXACT_SHA":
        _exact(value, {
            "qualification_scope", "target_sha", "target_tree",
            "tooling_source_manifest",
            "tooling_source_manifest_sha256",
        }, "tooling qualification identity")
        if name in ("package", "reproducibility", "ci", "deterministic",
                    "independent-review"):
            pass
        else:
            raise ValueError("tooling qualification gate invalid")
        expected_manifest = _tooling_source_manifest(
            target_sha, target_tree)
        manifest = value["tooling_source_manifest"]
        _digest(
            value["tooling_source_manifest_sha256"],
            "tooling source manifest")
        if (value["target_sha"] != target_sha or
                value["target_tree"] != target_tree or
                manifest != expected_manifest or
                value["tooling_source_manifest_sha256"] !=
                hashlib.sha256(
                    lifecycle.canonical_json_bytes(manifest)).hexdigest() or
                qualified_input_sha256 != _canonical_sha(value)):
            raise ValueError(
                "tooling qualification identity does not match exact SHA/tree")
    elif scope == "FROZEN_CAMPAIGNS":
        _exact(value, {
            "qualification_scope", "target_sha", "target_tree",
            "campaign_qualified_input_sha256",
            "evaluated_surfaces_sha256",
        }, "frozen campaigns qualification identity")
        if name in ("package", "reproducibility"):
            raise ValueError(
                f"{name} qualification scope must be TOOLING_EXACT_SHA")
        if (value["target_sha"] != target_sha or
                value["target_tree"] != target_tree or
                value["campaign_qualified_input_sha256"] !=
                campaign_qualified_input_sha256 or
                value["evaluated_surfaces_sha256"] !=
                evaluated_surfaces_sha256 or
                qualified_input_sha256 !=
                campaign_qualified_input_sha256):
            raise ValueError(
                "frozen campaigns qualification identity mismatch")
    else:
        raise ValueError("qualification scope invalid")
    return value


def _validate_package_asset_binding(value, artifact_hashes):
    _exact(value, {
        "selected_archive_path", "selected_archive_sha256", "assets",
    }, "package reproducibility binding")
    _digest(value["selected_archive_sha256"], "selected package archive")
    if (value["selected_archive_path"] != "package-retained.skill" or
            artifact_hashes.get(value["selected_archive_path"]) !=
            value["selected_archive_sha256"] or
            type(value["assets"]) is not list or
            len(value["assets"]) != 2):
        raise ValueError("package reproducibility selected archive invalid")
    expected = (
        ("A", "package-repro-a.skill",
         "package-repro-a-entry-manifest.json"),
        ("B", "package-repro-b.skill",
         "package-repro-b-entry-manifest.json"),
    )
    observed_paths = {value["selected_archive_path"]}
    observed_manifests = set()
    for row, (label, path, manifest_path) in zip(value["assets"], expected):
        _exact(row, {
            "label", "path", "sha256",
            "manifest_path", "manifest_sha256",
        }, f"package reproducibility asset {label}")
        _digest(row["sha256"], f"package reproducibility asset {label}")
        _digest(
            row["manifest_sha256"],
            f"package reproducibility manifest {label}")
        if (row["label"] != label or row["path"] != path or
                row["manifest_path"] != manifest_path or
                row["sha256"] != value["selected_archive_sha256"] or
                artifact_hashes.get(path) != row["sha256"] or
                artifact_hashes.get(manifest_path) !=
                row["manifest_sha256"]):
            raise ValueError(
                f"package reproducibility asset {label} invalid")
        if path in observed_paths or manifest_path in observed_manifests:
            raise ValueError("package reproducibility artifact alias invalid")
        observed_paths.add(path)
        observed_manifests.add(manifest_path)
    if value["assets"][0]["manifest_sha256"] != \
            value["assets"][1]["manifest_sha256"]:
        raise ValueError("package reproducibility manifests differ")
    return value


def derive_qualified_input_sha256(*, b3_campaign_root,
                                  matrix_campaign_root,
                                  b3_surface_root,
                                  matrix_surface_root):
    b3_packet, b3_raw, b3_manifest = _packet_and_manifest(
        b3_campaign_root, b3_surface_root, surfaces.B3_CAMPAIGN)
    matrix_packet, matrix_raw, matrix_manifest = _packet_and_manifest(
        matrix_campaign_root, matrix_surface_root,
        surfaces.MATRIX_CAMPAIGN)
    return _gate_identity(
        {
            "freeze_sha256": hashlib.sha256(b3_raw).hexdigest(),
            "contract_sha256": b3_packet["artifact_contract"]["sha256"],
        },
        {
            "freeze_sha256": hashlib.sha256(matrix_raw).hexdigest(),
            "contract_sha256":
                matrix_packet["artifact_contract"]["sha256"],
        },
        {
            surfaces.B3_CAMPAIGN: b3_manifest,
            surfaces.MATRIX_CAMPAIGN: matrix_manifest,
        })


def _string_list(value, owner):
    if (type(value) is not list or
            any(type(item) is not str or not item for item in value)):
        raise ValueError(f"{owner} must be an exact string list")


def _file_row(path, root, owner):
    raw = lifecycle.read_custodied_bytes(path, owner, root=root)
    observed = os.lstat(path)
    if observed.st_nlink != 1:
        raise ValueError(f"{owner} hardlink forbidden")
    return raw, {
        "path": pathlib.Path(path).relative_to(root).as_posix(),
        "byte_length": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def _gate_target(packet, owner):
    foundation = packet.get("foundation")
    if type(foundation) is not dict:
        raise ValueError(f"{owner} foundation identity missing")
    commit = foundation.get("commit")
    tree = foundation.get("tree")
    for value, label in ((commit, "commit"), (tree, "tree")):
        if (type(value) is not str or len(value) != 40 or
                any(char not in "0123456789abcdef" for char in value)):
            raise ValueError(f"{owner} foundation {label} invalid")
    return commit, tree


def _validate_gate_terminal(name, value, qualified_input_sha256,
                            artifact_hashes, evidence_mode="TEST_ONLY"):
    common = {
        "schema", "gate", "qualified_input_sha256", "exit_code",
        "qualification_scope", "qualification_identity",
    }
    if name == "deterministic":
        deterministic_fields = {"failed_checks", "checks"}
        if evidence_mode == "PRODUCTION":
            deterministic_fields.add("bash_executable")
        _exact(value, common | deterministic_fields, name)
        _string_list(value["failed_checks"], "deterministic failed checks")
        if (type(value["checks"]) is not list or
                [row.get("name") if type(row) is dict else None
                 for row in value["checks"]] != list(DETERMINISTIC_CHECKS)):
            raise ValueError("deterministic check coverage invalid")
        for row in value["checks"]:
            if evidence_mode == "PRODUCTION":
                _exact(row, {
                    "name", "argv", "exit_code", "started_at",
                    "completed_at", "pid", "stdout_path",
                    "stdout_sha256", "stderr_path", "stderr_sha256",
                }, "deterministic production check row")
                expected_argv = DETERMINISTIC_COMMANDS[row["name"]]
                if expected_argv[0] == "bash":
                    if (row["argv"][0] !=
                            value["bash_executable"]["canonical_path"] or
                            row["argv"][1:] != expected_argv[1:]):
                        raise ValueError(
                            "deterministic production argv invalid")
                elif row["argv"] != expected_argv:
                    raise ValueError(
                        "deterministic production argv invalid")
                if (type(row["pid"]) is not int or row["pid"] <= 0 or
                        type(row["started_at"]) is not str or
                        type(row["completed_at"]) is not str or
                        row["exit_code"] != 0):
                    raise ValueError(
                        "deterministic production execution row invalid")
                for key in ("stdout_sha256", "stderr_sha256"):
                    _digest(row[key], f"deterministic {key}")
            else:
                _exact(row, {"name", "command", "exit_code", "marker"},
                       "deterministic check row")
                if (type(row["command"]) is not str or not row["command"] or
                        type(row["exit_code"]) is not int or
                        row["exit_code"] != 0 or
                        row["marker"] !=
                        f"FOCUSED_CHECK_PASS name={row['name']}"):
                    raise ValueError("deterministic check row invalid")
        if evidence_mode == "PRODUCTION":
            _validate_production_bash_binding(value["bash_executable"])
        passed = value["exit_code"] == 0 and value["failed_checks"] == []
    elif name == "package":
        package_fields = {
            "verification_passed", "package_manifest_sha256"}
        if evidence_mode == "PRODUCTION":
            package_fields |= {
                "argv", "started_at", "completed_at", "pid",
                "bash_executable", "package_reproducibility"}
        _exact(value, common | package_fields, name)
        if evidence_mode == "PRODUCTION":
            _validate_production_bash_binding(value["bash_executable"])
            _validate_package_asset_binding(
                value["package_reproducibility"], artifact_hashes)
            if (value["argv"][0] !=
                    value["bash_executable"]["canonical_path"] or
                    value["argv"][1:] != ["scripts/verify-package.sh"] or
                    type(value["pid"]) is not int or value["pid"] <= 0):
                raise ValueError("package production execution invalid")
        _digest(value["package_manifest_sha256"], "package manifest")
        passed = (value["exit_code"] == 0 and
                  value["verification_passed"] is True and
                  value["package_manifest_sha256"] ==
                  artifact_hashes["package-entry-manifest.json"])
    elif name == "ci":
        ci_fields = {"failed_jobs", "jobs"}
        if evidence_mode == "PRODUCTION":
            ci_fields |= {"execution_kind", "provider_export_sha256"}
        _exact(value, common | ci_fields, name)
        _string_list(value["failed_jobs"], "CI failed jobs")
        if (type(value["jobs"]) is not list or
                [row.get("name") if type(row) is dict else None
                 for row in value["jobs"]] != list(CI_JOBS)):
            raise ValueError("CI job coverage invalid")
        workflow = pathlib.Path(__file__).resolve().parent.parent / \
            ".github" / "workflows" / "validate.yml"
        workflow_sha = hashlib.sha256(workflow.read_bytes()).hexdigest()
        for row in value["jobs"]:
            row_fields = {
                "name", "workflow_path", "workflow_sha256",
                "run_attempt", "conclusion"}
            if evidence_mode == "PRODUCTION":
                row_fields |= {
                    "workflow_run_id", "job_id", "producer_identity"}
            else:
                row_fields |= {"log_marker"}
            _exact(row, row_fields, "CI job row")
            if (row["workflow_path"] != ".github/workflows/validate.yml" or
                    row["workflow_sha256"] != workflow_sha or
                    type(row["run_attempt"]) is not int or
                    row["run_attempt"] != 1 or
                    row["conclusion"] != "success"):
                raise ValueError("CI job row invalid")
            if evidence_mode == "PRODUCTION":
                if (value["execution_kind"] != "HOSTED_CI" or
                        type(row["workflow_run_id"]) is not int or
                        row["workflow_run_id"] <= 0 or
                        type(row["job_id"]) is not int or
                        row["job_id"] <= 0 or
                        type(row["producer_identity"]) is not str or
                        not row["producer_identity"]):
                    raise ValueError("hosted CI job identity invalid")
                _digest(
                    value["provider_export_sha256"],
                    "hosted CI provider export")
            elif row["log_marker"] != \
                    f"CI_JOB_PASS name={row['name']}":
                raise ValueError("CI job marker invalid")
        passed = value["exit_code"] == 0 and value["failed_jobs"] == []
    elif name == "reproducibility":
        _exact(
            value, common | {
                "comparison_equal", "first_artifact_sha256",
                "second_artifact_sha256"}, name)
        _digest(value["first_artifact_sha256"], "first artifact")
        _digest(value["second_artifact_sha256"], "second artifact")
        passed = (
            value["exit_code"] == 0 and
            value["comparison_equal"] is True and
            value["first_artifact_sha256"] ==
            value["second_artifact_sha256"] ==
            artifact_hashes["repro-first.skill"] ==
            artifact_hashes["repro-second.skill"])
    elif name == "independent-review":
        _exact(value, {
            "schema", "gate", "reviewed_qualified_input_sha256",
            "verdict", "findings", "qualification_scope",
            "qualification_identity"}, name)
        _string_list(value["findings"], "independent review findings")
        passed = value["verdict"] == "PASS" and value["findings"] == []
        if value["reviewed_qualified_input_sha256"] != qualified_input_sha256:
            raise ValueError("independent-review qualified input mismatch")
    else:
        raise ValueError("unsupported integration gate")
    expected_schema = (
        f"implementaudit-{name}-terminal-v2"
        if evidence_mode == "PRODUCTION" and
        name in ("deterministic", "package", "ci")
        else f"implementaudit-{name}-terminal-v1")
    if value["schema"] != expected_schema or value["gate"] != name:
        raise ValueError(f"{name} terminal schema identity invalid")
    if name != "independent-review":
        if type(value["exit_code"]) is not int:
            raise ValueError(f"{name} exit code type invalid")
        if value["qualified_input_sha256"] != qualified_input_sha256:
            raise ValueError(f"{name} qualified input mismatch")
    if not passed:
        raise ValueError(f"{name} terminal does not derive semantic PASS")


def _validate_gate_evidence(name, gate_root, qualified_input_sha256,
                            target_sha, target_tree, surfaces_sha256,
                            prior_evidence_sha256, allow_test_evidence=False):
    start_name = f"{name}-start.json"
    report_name = f"{name}-report.json"
    stdout_name = f"{name}.stdout.log"
    stderr_name = f"{name}.stderr.log"
    manifest_name = f"{name}-evidence-manifest.json"
    terminal_name = GATE_FILENAMES[name]
    start_probe, _start_probe_raw = _read_root_json(
        gate_root, start_name, f"integration gate {name} start probe")
    expected_mode = (
        "TEST_ONLY" if allow_test_evidence else "PRODUCTION")
    if start_probe.get("evidence_mode") != expected_mode:
        raise ValueError(
            f"{name} producer evidence_mode invalid")
    artifact_names = []
    if name == "deterministic" and not allow_test_evidence:
        for index, check in enumerate(DETERMINISTIC_CHECKS):
            artifact_names.extend([
                f"deterministic-{index:02d}-{check}.stdout.log",
                f"deterministic-{index:02d}-{check}.stderr.log",
            ])
    elif name == "package":
        artifact_names = [
            "package-retained.skill", "package-entry-manifest.json"]
        if not allow_test_evidence:
            artifact_names.extend([
                "package-command.stdout.log",
                "package-command.stderr.log",
                "package-repro-a.skill",
                "package-repro-b.skill",
                "package-repro-a-entry-manifest.json",
                "package-repro-b-entry-manifest.json",
            ])
    elif name == "reproducibility":
        artifact_names = ["repro-first.skill", "repro-second.skill"]
    elif name == "ci" and not allow_test_evidence:
        artifact_names = ["ci-provider-export.json"]
    elif name == "independent-review":
        artifact_names = [
            "independent-review-structured.json",
            "independent-review.md"]

    retained = {}
    rows = []
    for filename in (
            start_name, terminal_name, report_name, stdout_name, stderr_name,
            *artifact_names):
        raw, row = _file_row(
            gate_root / filename, gate_root,
            f"integration gate {name} retained {filename}")
        retained[filename] = raw
        rows.append(row)

    manifest, manifest_raw = _read_root_json(
        gate_root, manifest_name, f"integration gate {name} manifest")
    _exact(manifest, {"schema", "gate", "files"}, f"{name} manifest")
    if (manifest["schema"] != "implementaudit-gate-evidence-manifest-v1" or
            manifest["gate"] != name or
            type(manifest["files"]) is not list or
            manifest["files"] != rows):
        raise ValueError(
            f"{name} evidence manifest does not match bytes: "
            f"declared={[row.get('path') for row in manifest.get('files', [])]} "
            f"observed={[row.get('path') for row in rows]}")

    start = lifecycle.decode_strict_json_bytes(
        retained[start_name], f"{name} producer start", require_object=True)
    start_fields = {
        "schema", "gate", "evidence_mode",
        "producer_source_path", "producer_source_sha256",
        "qualified_input_sha256", "target_sha",
        "target_tree", "command", "producer_role",
        "qualification_scope", "qualification_identity",
        "invocation_count",
        "network_authorized", "credentials_authorized",
        "model_or_metered_api_authorized",
    }
    if not allow_test_evidence and name in ("deterministic", "package"):
        start_fields.add("bash_executable")
    _exact(start, start_fields, f"{name} producer start")
    expected_start = {
        "schema": "implementaudit-gate-producer-start-v1",
        "gate": name,
        "evidence_mode": (
            "TEST_ONLY" if allow_test_evidence else "PRODUCTION"),
        "producer_source_path":
            "eval/qualification_evidence_producer.py",
        "target_sha": target_sha,
        "target_tree": target_tree,
        "command": GATE_COMMANDS[name],
        "producer_role": GATE_PRODUCER_ROLES[name],
        "invocation_count": 1,
        "network_authorized": False,
        "credentials_authorized": False,
        "model_or_metered_api_authorized": False,
    }
    for key, expected in expected_start.items():
        if (key == "invocation_count" and
                type(start[key]) is not int):
            raise ValueError(f"{name} producer invocation count type invalid")
        if start[key] != expected:
            raise ValueError(f"{name} producer {key} identity invalid")
    _validate_qualification_identity(
        name, start["qualification_identity"],
        start["qualified_input_sha256"], target_sha, target_tree,
        qualified_input_sha256, surfaces_sha256)
    if start["qualification_scope"] != \
            start["qualification_identity"]["qualification_scope"]:
        raise ValueError(
            f"{name} producer qualification scope identity invalid")
    gate_qualified_input_sha256 = start["qualified_input_sha256"]
    producer_source = pathlib.Path(__file__).resolve().parent / \
        "qualification_evidence_producer.py"
    observed_producer_sha = hashlib.sha256(
        producer_source.read_bytes()).hexdigest()
    if start["producer_source_sha256"] != observed_producer_sha:
        raise ValueError(f"{name} producer source hash invalid")
    if not allow_test_evidence:
        if hashlib.sha256(_git_bytes(
                pathlib.Path(__file__).resolve().parent.parent,
                target_sha,
                "eval/qualification_evidence_producer.py")).hexdigest() != \
                observed_producer_sha:
            raise ValueError(
                f"{name} producer source is not target-tree bound")

    terminal = lifecycle.decode_strict_json_bytes(
        retained[terminal_name], f"{name} terminal", require_object=True)
    artifact_hashes = {
        filename: hashlib.sha256(retained[filename]).hexdigest()
        for filename in artifact_names
    }
    _validate_gate_terminal(
        name, terminal, gate_qualified_input_sha256, artifact_hashes,
        start["evidence_mode"])
    if (terminal["qualification_scope"] != start["qualification_scope"] or
            terminal["qualification_identity"] !=
            start["qualification_identity"]):
        raise ValueError(
            f"{name} terminal qualification identity invalid")
    if (not allow_test_evidence and name in ("deterministic", "package") and
            start["bash_executable"] != terminal["bash_executable"]):
        raise ValueError(
            f"{name} producer start bash executable binding invalid")
    if name == "deterministic" and not allow_test_evidence:
        for row in terminal["checks"]:
            if (row["stdout_sha256"] !=
                    artifact_hashes[row["stdout_path"]] or
                    row["stderr_sha256"] !=
                    artifact_hashes[row["stderr_path"]]):
                raise ValueError(
                    "deterministic production raw log binding invalid")
    if name == "ci" and not allow_test_evidence:
        export = lifecycle.decode_strict_json_bytes(
            retained["ci-provider-export.json"],
            "hosted CI provider export", require_object=True)
        row = terminal["jobs"][0]
        if (terminal["provider_export_sha256"] !=
                artifact_hashes["ci-provider-export.json"] or
                export.get("schema") !=
                "implementaudit-hosted-ci-provider-export-v1" or
                export.get("evidence_mode") != "PRODUCTION" or
                export.get("provider") != "github-actions" or
                export.get("head_sha") != target_sha or
                export.get("head_tree") != target_tree or
                export.get("run_id") != row["workflow_run_id"] or
                export.get("attempt") != row["run_attempt"] or
                export.get("conclusion") != "success" or
                export.get("jobs") != [{
                    "name": "package", "job_id": row["job_id"],
                    "conclusion": "success",
                    "producer_identity": row["producer_identity"],
                }]):
            raise ValueError("hosted CI provider export binding invalid")
    if name == "package":
        entry_manifest = lifecycle.decode_strict_json_bytes(
            retained["package-entry-manifest.json"],
            "package entry manifest", require_object=True)
        validate_package_archive(
            gate_root / "package-retained.skill", entry_manifest,
            target_sha, target_tree)
        if not allow_test_evidence:
            for label in ("a", "b"):
                manifest_name = \
                    f"package-repro-{label}-entry-manifest.json"
                reproducibility_manifest = \
                    lifecycle.decode_strict_json_bytes(
                        retained[manifest_name],
                        f"package reproducibility {label.upper()} manifest",
                        require_object=True)
                validate_package_archive(
                    gate_root / f"package-repro-{label}.skill",
                    reproducibility_manifest, target_sha, target_tree)
            if (retained["package-retained.skill"] !=
                    retained["package-repro-a.skill"] or
                    retained["package-repro-a.skill"] !=
                    retained["package-repro-b.skill"]):
                raise ValueError(
                    "package selected/A/B retained archives differ")
    elif name == "reproducibility":
        first = retained["repro-first.skill"]
        second = retained["repro-second.skill"]
        if first != second:
            raise ValueError("reproducibility retained archives differ")
        try:
            with zipfile.ZipFile(gate_root / "repro-first.skill") as archive:
                if archive.testzip() is not None:
                    raise ValueError(
                        "reproducibility archive CRC verification failed")
        except zipfile.BadZipFile as exc:
            raise ValueError(
                "reproducibility retained artifact is not a ZIP") from exc

    report = lifecycle.decode_strict_json_bytes(
        retained[report_name], f"{name} producer report",
        require_object=True)
    common = {
        "schema", "gate", "qualified_input_sha256", "target_sha",
        "target_tree", "stdout_sha256", "stderr_sha256",
        "terminal_sha256", "producer_source_path",
        "producer_source_sha256", "qualification_scope",
        "qualification_identity",
    }
    if name == "independent-review":
        _exact(report, common | {
            "reviewer_identity", "reviewer_role",
            "reviewed_evidence_sha256", "review_artifact_sha256",
            "review_json_sha256",
        }, f"{name} producer report")
        if (type(report["reviewer_identity"]) is not str or
                not report["reviewer_identity"] or
                report["reviewer_role"] !=
                GATE_PRODUCER_ROLES["independent-review"] or
                report["reviewed_evidence_sha256"] !=
                prior_evidence_sha256 or
                report["review_artifact_sha256"] !=
                artifact_hashes["independent-review.md"] or
                report["review_json_sha256"] !=
                artifact_hashes["independent-review-structured.json"]):
            raise ValueError("independent-review identity/evidence invalid")
    else:
        report_fields = set(common)
        if not allow_test_evidence and name in ("deterministic", "package"):
            report_fields.add("bash_executable")
        _exact(report, report_fields, f"{name} producer report")
    if (report["schema"] != "implementaudit-gate-producer-report-v1" or
            report["gate"] != name or
            report["qualified_input_sha256"] !=
            gate_qualified_input_sha256 or
            report["target_sha"] != target_sha or
            report["target_tree"] != target_tree or
            report["producer_source_path"] !=
            start["producer_source_path"] or
            report["producer_source_sha256"] !=
            start["producer_source_sha256"] or
            report["qualification_scope"] !=
            start["qualification_scope"] or
            report["qualification_identity"] !=
            start["qualification_identity"] or
            report["stdout_sha256"] !=
            hashlib.sha256(retained[stdout_name]).hexdigest() or
            report["stderr_sha256"] !=
            hashlib.sha256(retained[stderr_name]).hexdigest() or
            report["terminal_sha256"] !=
            hashlib.sha256(retained[terminal_name]).hexdigest() or
            (not allow_test_evidence and
             name in ("deterministic", "package") and
             report["bash_executable"] != terminal["bash_executable"])):
        raise ValueError(f"{name} report identity or byte binding invalid")

    stdout = retained[stdout_name].decode("utf-8", errors="strict")
    if retained[stderr_name] != b"":
        raise ValueError(f"{name} retained stderr is not empty")
    marker = (
        f"IMPLEMENTAUDIT_GATE_PASS gate={name} "
        f"input={gate_qualified_input_sha256} "
        f"sha={target_sha} tree={target_tree}")
    if stdout.splitlines().count(marker) != 1:
        raise ValueError(f"{name} raw PASS marker invalid")
    if name == "deterministic":
        if allow_test_evidence:
            for row in terminal["checks"]:
                if stdout.splitlines().count(row["marker"]) != 1:
                    raise ValueError(
                        "deterministic raw check evidence invalid")
    if name == "ci":
        if allow_test_evidence:
            for row in terminal["jobs"]:
                if stdout.splitlines().count(row["log_marker"]) != 1:
                    raise ValueError("CI raw job evidence invalid")
    if name == "package":
        asset_hash = artifact_hashes["package-retained.skill"]
        required = ["verify-package: ok"]
        if allow_test_evidence:
            required.append(
                f"REPRODUCIBLE_ASSET_RETAINED sha256={asset_hash}")
        else:
            required.extend([
                "PACKAGE_SELECTED_ARCHIVE_RETAINED "
                f"path=package-retained.skill sha256={asset_hash}",
                "PACKAGE_REPRO_A_RETAINED "
                f"path=package-repro-a.skill sha256={asset_hash}",
                "PACKAGE_REPRO_B_RETAINED "
                f"path=package-repro-b.skill sha256={asset_hash}",
            ])
        if any(stdout.splitlines().count(item) != 1 for item in required):
            raise ValueError("package raw evidence markers invalid")
        if not allow_test_evidence:
            command_stdout = retained[
                "package-command.stdout.log"].decode(
                    "utf-8", errors="strict")
            if "verify-package: ok" not in command_stdout.splitlines():
                raise ValueError(
                    "package command raw success missing")
            for label in ("A", "B"):
                matches = [
                    line for line in command_stdout.splitlines()
                    if line.startswith(
                        f"REPRODUCIBLE_ASSET_{label}_RETAINED path=") and
                    line.endswith(f" sha256={asset_hash}")
                ]
                if len(matches) != 1:
                    raise ValueError(
                        f"package command asset {label} export marker invalid")
    if name == "reproducibility":
        asset_hash = artifact_hashes["repro-first.skill"]
        required = f"REPRODUCIBILITY_EQUAL sha256={asset_hash}"
        if stdout.splitlines().count(required) != 1:
            raise ValueError("reproducibility raw evidence marker invalid")
    if name == "independent-review":
        structured = lifecycle.decode_strict_json_bytes(
            retained["independent-review-structured.json"],
            "independent structured review", require_object=True)
        _exact(structured, {
            "schema", "target_sha", "target_tree", "base_sha", "range",
            "scope", "producer_source_sha256", "reviewer_identity",
            "reviewer_role", "reviewed_evidence_sha256", "findings",
            "verdict",
        }, "independent structured review")
        expected_scope = subprocess.run(
            ["git", "-C", str(pathlib.Path(__file__).resolve().parent.parent),
             "diff", "--name-only", structured["base_sha"], target_sha],
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
            check=False)
        if (expected_scope.returncode != 0 or
                structured["schema"] !=
                "implementaudit-independent-review-report-v2" or
                structured["target_sha"] != target_sha or
                structured["target_tree"] != target_tree or
                structured["range"] !=
                f"{structured['base_sha']}..{target_sha}" or
                structured["scope"] != expected_scope.stdout.splitlines() or
                structured["producer_source_sha256"] !=
                start["producer_source_sha256"] or
                structured["reviewer_identity"] !=
                report["reviewer_identity"] or
                structured["reviewer_role"] !=
                GATE_PRODUCER_ROLES["independent-review"] or
                structured["reviewed_evidence_sha256"] !=
                prior_evidence_sha256 or
                structured["findings"] != [] or
                structured["verdict"] != "PASS"):
            raise ValueError(
                "independent structured review invalid")
        review = retained["independent-review.md"].decode(
            "utf-8", errors="strict")
        lines = review.splitlines()
        if (lines.count("VERDICT: PASS") != 1 or
                not lines or lines[-1] != "VERDICT: PASS"):
            raise ValueError("independent-review retained verdict missing")

    evidence_sha256 = hashlib.sha256(manifest_raw).hexdigest()
    return {
        "name": name,
        "semantic_status": "PASS",
        "producer_role": start["producer_role"],
        "command": start["command"],
        "evidence_manifest_path": manifest_name,
        "evidence_manifest_sha256": evidence_sha256,
        "terminal_path": terminal_name,
        "terminal_sha256":
            hashlib.sha256(retained[terminal_name]).hexdigest(),
    }, evidence_sha256


def _validate_gates(gate_root, qualified_input_sha256, target_sha,
                    target_tree, surfaces_sha256,
                    allow_test_evidence=False):
    gate_root = _strict_directory(gate_root, "integration gate root")
    expected_files = set()
    for name in REQUIRED_GATES:
        expected_files.update({
            f"{name}-start.json",
            GATE_FILENAMES[name],
            f"{name}-report.json",
            f"{name}.stdout.log",
            f"{name}.stderr.log",
            f"{name}-evidence-manifest.json",
        })
        if not allow_test_evidence and name == "deterministic":
            for index, check in enumerate(DETERMINISTIC_CHECKS):
                expected_files.update({
                    f"deterministic-{index:02d}-{check}.stdout.log",
                    f"deterministic-{index:02d}-{check}.stderr.log",
                })
        if not allow_test_evidence and name == "package":
            expected_files.update({
                "package-command.stdout.log",
                "package-command.stderr.log",
                "package-repro-a.skill",
                "package-repro-b.skill",
                "package-repro-a-entry-manifest.json",
                "package-repro-b-entry-manifest.json",
            })
        if not allow_test_evidence and name == "ci":
            expected_files.add("ci-provider-export.json")
    expected_files.update({
        "package-retained.skill", "package-entry-manifest.json",
        "repro-first.skill",
        "repro-second.skill",
        "independent-review-structured.json",
        "independent-review.md",
    })
    try:
        observed_files = {
            path.name for path in gate_root.iterdir()
            if path.is_file()
        }
        observed_entries = {path.name for path in gate_root.iterdir()}
    except OSError as exc:
        raise ValueError("integration gate evidence root unreadable") from exc
    if observed_files != expected_files or observed_entries != expected_files:
        raise ValueError("integration gate evidence file coverage invalid")
    gates = []
    prior = hashlib.sha256(b"").hexdigest()
    for name in REQUIRED_GATES:
        row, evidence_sha256 = _validate_gate_evidence(
            name, gate_root, qualified_input_sha256, target_sha,
            target_tree, surfaces_sha256, prior, allow_test_evidence)
        gates.append(row)
        prior = _canonical_sha({
            "prior": prior, "name": name,
            "evidence_manifest_sha256": evidence_sha256,
        })
    return gates


def _after_manifest(before, after_root, external_paths, packet=None):
    if type(external_paths) is not dict:
        raise ValueError("post-integration external locators must be an object")
    expected_external_roles = {
        row["role"] for row in before["entries"]
        if pathlib.Path(row["path"]).is_absolute()
    }
    if set(external_paths) != expected_external_roles:
        raise ValueError(
            "post-integration external locator role coverage invalid")
    prior_paths = {
        row["role"]: row["path"] for row in before["entries"]
        if row["role"] in expected_external_roles
    }
    sources = []
    has_virtual = False
    for row in before["entries"]:
        role = row["role"]
        if (role in surfaces.INLINE_ROLES and
                row["path"] == surfaces.projection_path(role)):
            has_virtual = True
            continue
        path = external_paths.get(role, row["path"])
        if role in expected_external_roles:
            if (type(path) is not str or not pathlib.Path(path).is_absolute() or
                    "\\" in path):
                raise ValueError(
                    f"post-integration external locator invalid: {role}")
            if os.path.normcase(os.path.normpath(path)) == os.path.normcase(
                    os.path.normpath(prior_paths[role])):
                raise ValueError(
                    f"post-integration external locator reuses prior path: "
                    f"{role}")
        sources.append({"role": role, "path": path})
    if has_virtual:
        if packet is None:
            raise ValueError(
                "post-integration virtual projections require frozen packet")
        return surfaces.build_manifest_with_packet_projections(
            packet, before["campaign"], sources, root=after_root)
    return surfaces.build_manifest(before["campaign"], sources, root=after_root)


def _compare_after_bytes(before, after, campaign):
    surfaces.validate_manifest(before, campaign)
    surfaces.validate_manifest(after, campaign)
    prior = {row["role"]: row for row in before["entries"]}
    current = {row["role"]: row for row in after["entries"]}
    for role in surfaces.required_roles(campaign):
        for field in ("byte_length", "sha256"):
            if prior[role][field] != current[role][field]:
                raise ValueError(
                    f"evaluated surface byte drift: {role} ({field})")
    return True


def validate_inputs(*, b3_campaign_root, matrix_campaign_root,
                    b3_surface_root, matrix_surface_root,
                    b3_after_surface_root, matrix_after_surface_root,
                    gate_root, b3_after_external_paths=None,
                    matrix_after_external_paths=None,
                    allow_test_evidence=False):
    b3_surface_root, b3_pre_root_identity = _strict_directory_identity(
        b3_surface_root, f"{surfaces.B3_CAMPAIGN} frozen pre surface root")
    matrix_surface_root, matrix_pre_root_identity = \
        _strict_directory_identity(
            matrix_surface_root,
            f"{surfaces.MATRIX_CAMPAIGN} frozen pre surface root")
    b3, b3_before, b3_packet = _validate_stage(
        b3_campaign_root, b3_surface_root, surfaces.B3_CAMPAIGN)
    matrix, matrix_before, matrix_packet = _validate_stage(
        matrix_campaign_root, matrix_surface_root,
        surfaces.MATRIX_CAMPAIGN)
    manifests = {
        surfaces.B3_CAMPAIGN: b3_before,
        surfaces.MATRIX_CAMPAIGN: matrix_before,
    }
    pre_root_identities = {
        surfaces.B3_CAMPAIGN: b3_pre_root_identity,
        surfaces.MATRIX_CAMPAIGN: matrix_pre_root_identity,
    }
    pre_file_identities = {
        surfaces.B3_CAMPAIGN: surfaces.custody_identity_map(
            b3_before, root=b3_surface_root),
        surfaces.MATRIX_CAMPAIGN: surfaces.custody_identity_map(
            matrix_before, root=matrix_surface_root),
    }
    b3_after_surface_root, b3_post_root_identity = \
        _strict_directory_identity(
            b3_after_surface_root,
            f"{surfaces.B3_CAMPAIGN} post-integration surface root")
    matrix_after_surface_root, matrix_post_root_identity = \
        _strict_directory_identity(
            matrix_after_surface_root,
            f"{surfaces.MATRIX_CAMPAIGN} post-integration surface root")
    post_root_identities = {
        surfaces.B3_CAMPAIGN: b3_post_root_identity,
        surfaces.MATRIX_CAMPAIGN: matrix_post_root_identity,
    }
    _require_distinct_post_roots(
        pre_root_identities, post_root_identities)
    qualified_input_sha256 = _gate_identity(b3, matrix, manifests)
    b3_target = _gate_target(b3_packet, surfaces.B3_CAMPAIGN)
    matrix_target = _gate_target(matrix_packet, surfaces.MATRIX_CAMPAIGN)
    if b3_target != matrix_target:
        raise ValueError("campaign qualification target SHA/tree mismatch")
    surfaces_sha256 = _canonical_sha({
        surfaces.B3_CAMPAIGN: b3_before,
        surfaces.MATRIX_CAMPAIGN: matrix_before,
    })
    gates = _validate_gates(
        gate_root, qualified_input_sha256, b3_target[0], b3_target[1],
        surfaces_sha256, allow_test_evidence)
    comparisons = {}
    for campaign, packet, before, after_root, external_paths, pre_root, post_root in (
            (surfaces.B3_CAMPAIGN, b3_packet, b3_before, b3_after_surface_root,
             b3_after_external_paths, b3_pre_root_identity,
             b3_post_root_identity),
            (surfaces.MATRIX_CAMPAIGN, matrix_packet, matrix_before,
             matrix_after_surface_root, matrix_after_external_paths,
             matrix_pre_root_identity, matrix_post_root_identity)):
        after = _after_manifest(
            before, after_root, external_paths or {}, packet)
        post_file_identities = surfaces.custody_identity_map(
            after, root=after_root)
        _require_post_files_distinct_from_pre(
            campaign, post_file_identities, pre_file_identities)
        _compare_after_bytes(before, after, campaign)
        comparisons[campaign] = {
            "equal_relevant_bytes": True,
            "post_root_distinct_from_all_pre_and_post_roots": True,
            "post_files_distinct_from_all_pre_files": True,
            "pre_root": {
                "path": pre_root["path"],
                "canonical_path": pre_root["canonical_path"],
                "device": pre_root["physical"][0],
                "inode": pre_root["physical"][1],
            },
            "post_root": {
                "path": post_root["path"],
                "canonical_path": post_root["canonical_path"],
                "device": post_root["physical"][0],
                "inode": post_root["physical"][1],
            },
            "before_manifest_sha256": _canonical_sha(before),
            "after_manifest_sha256": _canonical_sha(after),
        }
    return b3, matrix, gates, comparisons, qualified_input_sha256


def write_certificate(certificate_root, **roots):
    test_only = roots.get("allow_test_evidence") is True
    certificate_root, certificate_identity = _validate_certificate_root(
        certificate_root, roots)
    b3, matrix, gates, comparisons, qualified_input_sha256 = \
        validate_inputs(**roots)
    certificate_root, observed_certificate_identity = \
        _strict_directory_identity(
            certificate_root, "integration certificate root")
    if (_identity_tokens(observed_certificate_identity) !=
            _identity_tokens(certificate_identity)):
        raise ValueError(
            "integration certificate root identity changed during validation")
    certificate_identity = observed_certificate_identity
    _validate_certificate_external_disjoint(certificate_identity, roots)
    certificate = {
        "schema": SCHEMA,
        "disposition": (
            "TEST_ONLY_NON_QUALIFYING" if test_only else DISPOSITION),
        "integration_authorized": not test_only,
        "qualified_input_sha256": qualified_input_sha256,
        "b3_luna": b3,
        "matrix_luna": matrix,
        "gates": gates,
        "surface_comparisons": comparisons,
        "release_authorized": False,
        "tag_authorized": False,
        "publication_authorized": False,
        "final_cross_model_qualified": False,
    }
    path = certificate_root / CERTIFICATE_FILENAME
    try:
        lifecycle.write_new_json(path, certificate)
    except FileExistsError as exc:
        raise ValueError("create-once integration certificate exists") from exc
    return certificate
