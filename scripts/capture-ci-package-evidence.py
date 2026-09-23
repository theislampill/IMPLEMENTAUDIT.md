#!/usr/bin/env python3
"""Retain hosted package evidence after the validation wrapper reports its result."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import zipfile
from pathlib import Path


ROLE_FILES = {
    "canonical_plugin": "IMPLEMENTAUDIT.plugin.zip",
    "standalone_compatibility": "IMPLEMENTAUDIT.skill",
}
CAP_BYTES = 327680
INVENTORY_NAME = "IMPLEMENTAUDIT_INVENTORY.json"
DEPENDENCIES = (
    "attrs",
    "jsonschema",
    "jsonschema-specifications",
    "referencing",
    "rpds-py",
    "typing-extensions",
    "zopfli",
)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, encoding="utf-8"
    ).strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def invoke(root: Path, output: Path, label: str, args: list[str]) -> dict:
    result = subprocess.run(args, cwd=root, capture_output=True, timeout=600)
    (output / f"{label}.stdout.txt").write_bytes(result.stdout)
    (output / f"{label}.stderr.txt").write_bytes(result.stderr)
    return {"exit_code": result.returncode, "argv": args}


def inspect_archive(path: Path, role: str, source: dict) -> dict:
    data = path.read_bytes()
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or INVENTORY_NAME not in names:
            raise ValueError(f"{role} archive has duplicate members or lacks inventory")
        if archive.testzip() is not None:
            raise ValueError(f"{role} archive has a CRC failure")
        members = [
            {
                "path": info.filename,
                "bytes": info.file_size,
                "compressed_bytes": info.compress_size,
                "crc32": f"{info.CRC:08x}",
                "mode": f"{(info.external_attr >> 16):06o}",
                "sha256": sha256(archive.read(info.filename)),
            }
            for info in infos
        ]
        inventory_body = archive.read(INVENTORY_NAME)
        inventory = json.loads(inventory_body)
    if inventory.get("artifact_role") != role:
        raise ValueError(f"{role} embedded inventory has wrong role")
    if inventory.get("source") != {
        "commit": source["head"],
        "tree": source["tree"],
        "worktree_state": "clean",
    }:
        raise ValueError(f"{role} embedded inventory has wrong source")
    return {
        "filename": path.name,
        "bytes": len(data),
        "sha256": sha256(data),
        "cap_bytes": CAP_BYTES,
        "members": members,
        "inventory": {
            "role": inventory["artifact_role"],
            "source": inventory["source"],
            "bytes": len(inventory_body),
            "sha256": sha256(inventory_body),
            "member_count": len(inventory.get("members", [])),
        },
    }


def classify(result: dict, output: Path, label: str, role: str, size: int) -> str:
    if result["exit_code"] == 0:
        return "PASS"
    message = (output / f"{label}.stderr.txt").read_text(encoding="utf-8", errors="replace")
    standard_output = (output / f"{label}.stdout.txt").read_bytes()
    expected = f"{role} artifact exceeds reviewed cap: {size} > {CAP_BYTES} bytes"
    lines = [line.strip() for line in message.splitlines() if line.strip()]
    return (
        "EXPECTED_ACTIVE_CAP_REFUSAL"
        if result["exit_code"] == 1 and not standard_output and lines == [f"package-contract: {expected}"]
        else "OTHER_FAILURE"
    )


def capture(root: Path, output: Path) -> bool:
    if output == root or root in output.parents:
        raise ValueError("evidence output must be outside the source checkout")
    if output.is_symlink() or (output.exists() and any(output.iterdir())):
        raise ValueError("evidence output must be a fresh directory")
    output.mkdir(parents=True, exist_ok=True)
    head = git(root, "rev-parse", "HEAD")
    source = {
        "head": head,
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "parents": git(root, "rev-list", "--parents", "-n", "1", "HEAD").split()[1:],
        "worktree_clean_before": not bool(git(root, "status", "--porcelain", "--untracked-files=all")),
    }
    if not source["worktree_clean_before"]:
        raise ValueError("capture requires a clean source checkout")
    if os.environ.get("GITHUB_SHA") and os.environ["GITHUB_SHA"] != head:
        raise ValueError("GITHUB_SHA does not match checked-out source")

    command = [sys.executable, "scripts/package-contract.py"]
    builder = invoke(root, output, "BUILD", command + ["--build", str(output), "--require-clean-source"])
    roles = {}
    complete = True
    for role, filename in ROLE_FILES.items():
        path = output / filename
        if not path.is_file() or path.is_symlink():
            roles[role] = {"filename": filename, "missing": True}
            complete = False
            continue
        row = inspect_archive(path, role, source)
        label = f"VERIFY_{role}"
        verification = invoke(root, output, label, command + ["--verify-artifact", role, str(path), "--require-clean-source"])
        verification["failure_kind"] = classify(verification, output, label, role, row["bytes"])
        row["verification"] = verification
        if verification["failure_kind"] == "OTHER_FAILURE":
            complete = False
        roles[role] = row

    plugin_bytes = roles.get("canonical_plugin", {}).get("bytes", -1)
    builder["failure_kind"] = classify(builder, output, "BUILD", "canonical_plugin", plugin_bytes)
    if builder["failure_kind"] == "OTHER_FAILURE":
        complete = False
    source["worktree_clean_after"] = not bool(git(root, "status", "--porcelain", "--untracked-files=all"))
    complete = complete and source["worktree_clean_after"]
    dependencies = {}
    for name in DEPENDENCIES:
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None
    receipt = {
        "schema": "implementaudit.hosted-package-evidence.v1",
        "source": source,
        "github": {name: os.environ.get(name) for name in (
            "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_EVENT_NAME", "GITHUB_REF",
            "GITHUB_SHA", "GITHUB_HEAD_REF", "GITHUB_BASE_REF",
        )},
        "runtime": {
            "python": sys.version.split()[0],
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "runner_os": os.environ.get("RUNNER_OS"),
            "runner_arch": os.environ.get("RUNNER_ARCH"),
            "dependencies": dependencies,
        },
        "builder": builder,
        "roles": roles,
        "capture_complete": complete,
        "artifact_use": "DIAGNOSTIC_CI_EVIDENCE_ONLY; NOT_RELEASE_OR_INSTALL_ASSET",
        "validation_wrapper_status": "NOT_CAPTURED_BY_THIS_STEP; READ_HOSTED_VERIFY_PACKAGE_STEP",
    }
    (output / "CAPTURE.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return complete


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.is_symlink():
        raise ValueError("evidence output must not be a symlink")
    return 0 if capture(args.repo_root.resolve(), args.output_dir.resolve()) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        print(f"ci-package-evidence: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
