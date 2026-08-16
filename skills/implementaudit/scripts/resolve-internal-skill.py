#!/usr/bin/env python3
"""Resolve one governed child against an exact IMPLEMENTAUDIT package layout."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


CHILDREN = ("audit-state", "audit-assess", "audit-implement", "audit-andon")


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"resolve-internal-skill: {message}")


def exact_files(directory: Path, suffix: str) -> dict[str, Path]:
    if directory.is_symlink() or not directory.is_dir():
        return {}
    result: dict[str, Path] = {}
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file() or path.suffix != suffix:
            continue
        result[path.stem] = path
    return result


def canonical_children(governor: Path) -> dict[str, Path]:
    skill_root = governor.parent.parent
    if skill_root.name != "skills":
        return {}
    result: dict[str, Path] = {}
    for name in CHILDREN:
        path = skill_root / name / "SKILL.md"
        if path.is_file() and not path.is_symlink():
            result[name] = path
    observed = {
        path.parent.name
        for path in skill_root.glob("*/SKILL.md")
        if path.is_file() and not path.is_symlink() and path.parent.name != "implementaudit"
    }
    if not observed:
        return {}
    if observed != set(CHILDREN):
        fail(
            "canonical child population is not exact: "
            f"expected={list(CHILDREN)} observed={sorted(observed)}"
        )
    return result


def standalone_children(governor: Path) -> dict[str, Path]:
    directory = governor.parent / "internal-procedures"
    observed = exact_files(directory, ".md")
    if not observed and not directory.exists():
        return {}
    if set(observed) != set(CHILDREN):
        fail(
            "standalone child population is not exact: "
            f"expected={list(CHILDREN)} observed={sorted(observed)}"
        )
    return observed


def ambiguous_host_peer(governor: Path) -> Path | None:
    skill_dir = governor.parent
    if skill_dir.name != "implementaudit" or skill_dir.parent.name != "skills":
        return None
    parent = skill_dir.parent.parent
    if parent.name == "implementaudit" and parent.parent.name == "plugins":
        host_root = parent.parent.parent
        peer = host_root / "skills" / "implementaudit" / "SKILL.md"
    else:
        host_root = parent
        peer = host_root / "plugins" / "implementaudit" / "skills" / "implementaudit" / "SKILL.md"
    return peer if peer.is_file() or peer.is_symlink() else None


def resolve(governor: Path, child: str) -> Path:
    if child not in CHILDREN:
        fail(f"unknown child: {child}")
    requested = governor.absolute()
    if requested.is_symlink():
        fail("governor must not be a symlink")
    try:
        governor = requested.resolve(strict=True)
    except OSError as exc:
        fail(f"governor is missing: {exc}")
    if not governor.is_file() or governor.name != "SKILL.md":
        fail("governor must be a real SKILL.md file")
    if governor.parent.name != "implementaudit":
        fail("governor directory identity is not implementaudit")
    peer = ambiguous_host_peer(governor)
    if peer is not None:
        fail(f"ambiguous plugin/standalone precedence: {peer}")

    standalone = standalone_children(governor)
    selected = standalone if standalone else canonical_children(governor)
    if not selected:
        fail("executing package layout is missing or incomplete")
    path = selected[child].resolve(strict=True)
    print(path)
    return path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--governor", required=True)
    parser.add_argument("--child", required=True, choices=CHILDREN)
    args = parser.parse_args(argv)
    resolve(Path(args.governor), args.child)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
