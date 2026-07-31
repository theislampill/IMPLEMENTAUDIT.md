#!/usr/bin/env python3
"""Matrix-only materialization and preflight of prompt-bound fixture state."""
from __future__ import annotations

import os
import pathlib
import subprocess


SCHEMA = "implementaudit-candidate-matrix-precondition-v1"


def _relative_path(repo, value):
    if not isinstance(value, str) or not value:
        raise ValueError("matrix precondition path missing")
    pure = pathlib.PurePosixPath(value.replace("\\", "/"))
    if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
        raise ValueError("matrix precondition path unsafe")
    repo = pathlib.Path(repo).resolve()
    path = repo.joinpath(*pure.parts).resolve()
    try:
        path.relative_to(repo)
    except ValueError as exc:
        raise ValueError("matrix precondition path escapes repository") from exc
    return path


def _contract(value):
    if (not isinstance(value, dict) or
            set(value) != {"schema", "kind", "path"} or
            value.get("schema") != SCHEMA or
            value.get("kind") not in ("resume-run-root", "dirty-worktree")):
        raise ValueError("matrix precondition contract malformed")
    return value


def _git(repo, *args):
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise ValueError(
            f"matrix fixture git {' '.join(args)} failed: "
            f"{proc.stderr.strip()[:200]}")
    return proc.stdout.strip()


def _bash_path(path):
    path = pathlib.Path(path)
    if os.name != "nt":
        return path.as_posix()
    proc = subprocess.run(
        ["wsl.exe", "wslpath", "-a", "-u", path.as_posix()],
        capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise ValueError("matrix fixture WSL path conversion failed")
    return proc.stdout.strip()


def prepare_fixture(fixture_id, repo, product_checkout, precondition):
    if precondition is None:
        return
    rule = _contract(precondition)
    if rule["kind"] == "dirty-worktree":
        path = _relative_path(repo, rule["path"])
        if os.path.lexists(path):
            raise ValueError(
                f"{fixture_id} dirty-worktree marker already exists")
        path.write_text(
            "prompt-bound live dirty state for handoff reconciliation\n",
            encoding="utf-8")
    validate_fixture(fixture_id, repo, product_checkout, rule)


def validate_fixture(fixture_id, repo, product_checkout, precondition):
    if precondition is None:
        return True
    rule = _contract(precondition)
    repo = pathlib.Path(repo).resolve()
    path = _relative_path(repo, rule["path"])
    if rule["kind"] == "resume-run-root":
        validator = (
            pathlib.Path(product_checkout).resolve() /
            "skills" / "implementaudit" / "scripts" /
            "validate-run-root.sh")
        if not validator.is_file() or not path.is_dir():
            raise ValueError(
                f"{fixture_id} resume run-root precondition missing")
        command = (["wsl.exe", "--exec", "bash"] if os.name == "nt"
                   else ["bash"])
        proc = subprocess.run(
            command + [_bash_path(validator), _bash_path(path)],
            capture_output=True, text=True)
        if proc.returncode != 0:
            raise ValueError(
                f"{fixture_id} resume run-root precondition invalid: "
                f"{proc.stderr.strip()[:300]}")
        state = (path / "STATE.md").read_text(encoding="utf-8")
        roadmap = (path / "ROADMAP.md").read_text(encoding="utf-8")
        roots = list((repo / ".IMPLEMENTAUDIT" / "runs").glob("*/STATE.md"))
        if (len(roots) != 1 or "| Phase | 3 |" not in state or
                "| Status | INTERRUPTED |" not in state or
                "| 1 |" not in roadmap or "| 2 |" not in roadmap or
                "| 3 |" not in roadmap):
            raise ValueError(
                f"{fixture_id} resume run-root state does not match mission")
    else:
        if not path.is_file():
            raise ValueError(
                f"{fixture_id} dirty-worktree marker missing")
        status = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
        expected = "?? " + path.relative_to(repo).as_posix()
        if status != expected:
            raise ValueError(
                f"{fixture_id} dirty-worktree precondition drift: {status!r}")
    return True
