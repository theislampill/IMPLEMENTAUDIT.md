#!/usr/bin/env python3
"""Validate the canonical IMPLEMENTAUDIT package identity and fixed budgets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import shutil
import stat
import subprocess
import sys
import time
import zipfile
import zlib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any


CONTRACT_PATH = Path("package/implementaudit-package.json")
EXPECTED_REQUIRED_SKILLS = [
    "implementaudit",
    "audit-state",
    "audit-assess",
    "audit-implement",
    "audit-andon",
]
EXPECTED_INTERNAL_SKILLS = [
    {"name": "audit-state", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-assess", "maintainer_only": False, "directly_invocable": False},
    {"name": "audit-implement", "maintainer_only": True, "directly_invocable": False},
    {"name": "audit-andon", "maintainer_only": False, "directly_invocable": True},
]
EXPECTED_SHARED_ROOTS = [
    "skills/implementaudit/references",
    "skills/implementaudit/scripts",
    "skills/implementaudit/templates",
]
EXPECTED_MANIFESTS = {
    "codex": ".codex-plugin/plugin.json",
    "claude": ".claude-plugin/plugin.json",
}
EXPECTED_PUBLISHER = {"name": "theislampill"}
EXPECTED_MARKETPLACE = {
    "name": "implementaudit",
    "owner": EXPECTED_PUBLISHER,
}
EXPECTED_PROJECTIONS = {
    "canonical_plugin": {
        "artifact": "IMPLEMENTAUDIT.plugin.zip",
        "layout": "plugin-root",
    },
    "standalone_compatibility": {
        "artifact": "IMPLEMENTAUDIT.skill",
        "layout": "flattened-skill",
    },
}
EXPECTED_BUDGETS = {
    "canonical_plugin": {
        "artifact_role": "canonical_plugin",
        "measurement": "final_deterministic_compressed_bytes",
        "p0_baseline_bytes": 257985,
        "prototype_added_raw_bytes": 11263,
        "zip_path_header_allowance_bytes": 2504,
        "rounding_unit_bytes": 65536,
        "cap_bytes": 327680,
        "owner": "R33",
        "reviewed_work_order_sha256": (
            "a79eecd328da14874f4dd305ac35541f77ef3153a1d36cd814a457c4cd821db1"
        ),
        "locked_before_builder_change": True,
    },
    "standalone_compatibility": {
        "artifact_role": "standalone_compatibility",
        "measurement": "final_deterministic_compressed_bytes",
        "p0_baseline_bytes": 257985,
        "prototype_added_raw_bytes": 9465,
        "zip_path_header_allowance_bytes": 222,
        "rounding_unit_bytes": 65536,
        "cap_bytes": 327680,
        "owner": "R33",
        "reviewed_work_order_sha256": (
            "a79eecd328da14874f4dd305ac35541f77ef3153a1d36cd814a457c4cd821db1"
        ),
        "locked_before_builder_change": True,
    },
}
TEXT_SUFFIXES = {".md", ".txt", ".sh", ".json", ".yaml", ".yml"}
INVENTORY_NAME = "IMPLEMENTAUDIT_INVENTORY.json"
PACKAGE_NAME = "IMPLEMENTAUDIT_PACKAGE.json"
BLOCKED_PARTS = {
    ".git",
    ".IMPLEMENTAUDIT",
    ".github",
    "docs",
    "fixtures",
    "tests",
    "graphify-out",
    ".graphify",
    ".activegraph",
    "tmp",
    "temp",
    "dist",
}
BLOCKED_NAMES = {"graph.json", "quickstart_demo_run.db"}
BLOCKED_SUFFIXES = (".log", ".tmp", ".db", ".sqlite", ".sqlite3", ".jsonl")


class ContractError(ValueError):
    """A package contract or projection violates the reviewed invariant."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"missing required JSON file: {path.as_posix()}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root must be an object: {path.as_posix()}")
    return value


def require_equal(label: str, observed: Any, expected: Any) -> None:
    if observed != expected:
        raise ContractError(f"{label}: expected {expected!r}, got {observed!r}")


def skill_runtime_version(skill_path: Path) -> str:
    skill_name = skill_path.parent.name
    try:
        text = skill_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ContractError(f"missing required skill: {skill_path.as_posix()}") from exc
    frontmatter = re.match(r"---\n(?P<body>.*?)\n---\n", text, re.S)
    if not frontmatter:
        raise ContractError(f"{skill_name} SKILL.md has no YAML frontmatter")
    version = re.search(
        r'(?m)^\s+version:\s*["\']?([^"\'\n]+)["\']?\s*$',
        frontmatter.group("body"),
    )
    if not version:
        raise ContractError(f"{skill_name} SKILL.md metadata.version is missing")
    return version.group(1).strip()


def validate_manifest(
    root: Path, manifest_path: str, contract: dict[str, Any]
) -> None:
    manifest = load_json(root / manifest_path)
    expected = {
        "name": contract["package_name"],
        "version": contract["runtime_version"],
        "description": contract["description"],
        "skills": "./skills/",
        "author": contract["publisher"],
    }
    require_equal(f"{manifest_path} content", manifest, expected)


def validate_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root / CONTRACT_PATH)
    require_equal("schema_version", contract.get("schema_version"), 1)
    require_equal("logical_package", contract.get("logical_package"), "IMPLEMENTAUDIT_PLUGIN")
    require_equal("package_name", contract.get("package_name"), "implementaudit")
    require_equal("publisher", contract.get("publisher"), EXPECTED_PUBLISHER)
    require_equal("marketplace", contract.get("marketplace"), EXPECTED_MARKETPLACE)
    require_equal("runtime_version", contract.get("runtime_version"), "0.4.0")
    require_equal("release_family", contract.get("release_family"), "v0.4.0.0")
    require_equal("public_governor", contract.get("public_governor"), "implementaudit")
    require_equal("public_entrypoint", contract.get("public_entrypoint"), "/implementaudit")
    require_equal("required_skills", contract.get("required_skills"), EXPECTED_REQUIRED_SKILLS)
    require_equal("internal_skills", contract.get("internal_skills"), EXPECTED_INTERNAL_SKILLS)
    require_equal(
        "shared_resource_roots",
        contract.get("shared_resource_roots"),
        EXPECTED_SHARED_ROOTS,
    )
    require_equal("host_manifests", contract.get("host_manifests"), EXPECTED_MANIFESTS)
    require_equal(
        "generated_projections",
        contract.get("generated_projections"),
        EXPECTED_PROJECTIONS,
    )
    require_equal("budgets", contract.get("budgets"), EXPECTED_BUDGETS)
    require_equal(
        "generic_activegraph_dependency",
        contract.get("generic_activegraph_dependency"),
        False,
    )

    observed_skills = sorted(
        path.parent.name
        for path in (root / "skills").glob("*/SKILL.md")
        if path.is_file()
    )
    require_equal(
        "model-facing skill population",
        observed_skills,
        sorted(contract["required_skills"]),
    )
    for skill_name in contract["required_skills"]:
        version = skill_runtime_version(root / f"skills/{skill_name}/SKILL.md")
        require_equal(
            f"{skill_name} runtime version",
            version,
            contract["runtime_version"],
        )

    for manifest_path in EXPECTED_MANIFESTS.values():
        validate_manifest(root, manifest_path, contract)
    marketplace = load_json(root / ".claude-plugin/marketplace.json")
    require_equal(
        ".claude-plugin/marketplace.json content",
        marketplace,
        {
            "name": contract["marketplace"]["name"],
            "owner": contract["marketplace"]["owner"],
            "description": contract["description"],
            "plugins": [
                {
                    "name": contract["package_name"],
                    "description": contract["description"],
                    "source": "./",
                }
            ],
        },
    )
    for shared_root in EXPECTED_SHARED_ROOTS:
        if not (root / shared_root).is_dir():
            raise ContractError(f"missing shared resource root: {shared_root}")
    return contract


def normalized_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n")
    return data


def blocked_path(relative: PurePosixPath) -> bool:
    text = relative.as_posix()
    return (
        any(part in BLOCKED_PARTS for part in relative.parts)
        or relative.name in BLOCKED_NAMES
        or text.startswith(".env")
        or text.endswith(BLOCKED_SUFFIXES)
    )


def git_output(root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), *args],
            text=True,
            encoding="utf-8",
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"cannot resolve Git source identity: {' '.join(args)}") from exc


def source_identity(root: Path) -> dict[str, str]:
    status = git_output(root, "status", "--porcelain", "--untracked-files=all")
    return {
        "commit": git_output(root, "rev-parse", "HEAD"),
        "tree": git_output(root, "show", "-s", "--format=%T", "HEAD"),
        "worktree_state": "clean" if not status else "dirty",
    }


def inventory_bytes(
    role: str,
    contract: dict[str, Any],
    identity: dict[str, str],
    entries: list[tuple[str, bytes, int]],
) -> bytes:
    members = [
        {
            "path": path,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        for path, data, _mode in sorted(entries, key=lambda row: row[0])
    ]
    value = {
        "schema": contract["inventory_contract"]["format"],
        "artifact_role": role,
        "package_name": contract["package_name"],
        "runtime_version": contract["runtime_version"],
        "release_family": contract["release_family"],
        "public_governor": contract["public_governor"],
        "required_skills": contract["required_skills"],
        "internal_skills": contract["internal_skills"],
        "source": identity,
        "members": members,
    }
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


class CanonicalZopfliCompressor:
    """Buffer one ZIP member and emit deterministic raw method-8 DEFLATE."""

    def __init__(self, zopfli_module: Any):
        self.buffer = bytearray()
        self.zopfli_module = zopfli_module

    def compress(self, data: bytes) -> bytes:
        self.buffer.extend(data)
        return b""

    def flush(self) -> bytes:
        source = bytes(self.buffer)
        stream = self.zopfli_module.compress(
            source,
            numiterations=15,
            blocksplitting=1,
            blocksplittinglast=0,
            blocksplittingmax=15,
        )
        raw = stream[2:-4]
        if zlib.decompress(stream) != source or zlib.decompress(raw, wbits=-15) != source:
            raise ContractError("zopfli round-trip validation failed")
        return raw


def require_zopfli() -> Any:
    try:
        import zopfli.zlib as zopfli_zlib
    except ImportError as exc:
        raise ContractError(
            "release build requires zopfli 0.2.3.post1; "
            "run: python -m pip install --no-deps --requirement requirements-release.txt"
        ) from exc
    try:
        observed = version("zopfli")
    except PackageNotFoundError as exc:
        raise ContractError("release build cannot resolve the zopfli package version") from exc
    require_equal("zopfli version", observed, "0.2.3.post1")
    return zopfli_zlib


def archive_timestamp() -> tuple[int, int, int, int, int, int]:
    try:
        epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "315532800"))
    except ValueError as exc:
        raise ContractError("SOURCE_DATE_EPOCH must be an integer") from exc
    stamp = time.gmtime(epoch)[:6]
    if not 1980 <= stamp[0] <= 2107:
        raise ContractError("SOURCE_DATE_EPOCH is outside the ZIP timestamp range")
    return stamp


def zip_info(path: str, mode: int, stamp: tuple[int, int, int, int, int, int]) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=stamp)
    info.create_system = 3
    info.create_version = 20
    info.extract_version = 20
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.internal_attr = 0
    info.compress_type = zipfile.ZIP_DEFLATED
    info.flag_bits = 0
    info.extra = b""
    info.comment = b""
    return info


def write_archive(path: Path, entries: list[tuple[str, bytes, int]], zopfli_module: Any) -> None:
    entries = sorted(entries, key=lambda row: row[0])
    names = [row[0] for row in entries]
    if len(names) != len(set(names)):
        raise ContractError("archive entries contain duplicate paths")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    stdlib_get_compressor = getattr(zipfile, "_get_compressor", None)
    if not callable(stdlib_get_compressor):
        raise ContractError("unsupported Python zipfile compressor interface")

    def canonical_get_compressor(compress_type: int, compresslevel: int | None = None) -> Any:
        if compress_type == zipfile.ZIP_DEFLATED:
            return CanonicalZopfliCompressor(zopfli_module)
        return stdlib_get_compressor(compress_type, compresslevel)

    zipfile._get_compressor = canonical_get_compressor
    try:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, strict_timestamps=True) as zf:
            stamp = archive_timestamp()
            for name, data, mode in entries:
                zf.writestr(zip_info(name, mode, stamp), data)
    finally:
        zipfile._get_compressor = stdlib_get_compressor


def source_skill_entries(root: Path) -> list[tuple[Path, bytes, int]]:
    skill_root = root / "skills/implementaudit"
    tracked = set(
        git_output(root, "ls-files", "--", "skills/implementaudit").splitlines()
    )
    entries: list[tuple[Path, bytes, int]] = []
    for path in sorted(skill_root.rglob("*"), key=lambda value: value.as_posix()):
        if not path.is_file():
            continue
        relative = PurePosixPath(path.relative_to(skill_root).as_posix())
        repo_relative = f"skills/implementaudit/{relative.as_posix()}"
        if repo_relative not in tracked:
            raise ContractError(
                f"untracked package member cannot bless its own inventory: {repo_relative}"
            )
        if blocked_path(relative):
            raise ContractError(f"blocked file selected for package: {relative.as_posix()}")
        mode = 0o755 if relative.parts and relative.parts[0] == "scripts" else 0o644
        entries.append((Path(relative.as_posix()), normalized_bytes(path), mode))
    if not entries or entries[0][0].as_posix() != "SKILL.md":
        if not any(path.as_posix() == "SKILL.md" for path, _data, _mode in entries):
            raise ContractError("governor SKILL.md is absent from package payload")
    return entries


def internal_skill_entries(root: Path) -> list[tuple[str, bytes, int]]:
    """Return canonical plugin members for the exact internal skill population."""
    tracked = set(git_output(root, "ls-files", "--", "skills").splitlines())
    entries: list[tuple[str, bytes, int]] = []
    for skill_name in EXPECTED_REQUIRED_SKILLS[1:]:
        relative = f"skills/{skill_name}/SKILL.md"
        if relative not in tracked:
            raise ContractError(
                f"untracked package member cannot bless its own inventory: {relative}"
            )
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise ContractError(f"required internal skill is missing or non-regular: {relative}")
        entries.append((relative, normalized_bytes(path), 0o644))
    return entries


def standalone_internal_procedure_entries(
    plugin_child_entries: list[tuple[str, bytes, int]],
) -> list[tuple[str, bytes, int]]:
    """Project child cognition without exposing standalone child SKILL.md files."""
    projections: list[tuple[str, bytes, int]] = []
    for source_name, source_data, _mode in plugin_child_entries:
        skill_name = PurePosixPath(source_name).parts[1]
        text = source_data.decode("utf-8")
        projected, count = re.subn(r"\A---\n.*?\n---\n+", "", text, count=1, flags=re.S)
        if count != 1:
            raise ContractError(f"internal skill frontmatter cannot be projected: {source_name}")
        projected = re.sub(
            r"\.\.[\\/]+implementaudit[\\/]+"
            r"((?:references|scripts|templates)[\\/]+[^`\r\n]+)",
            lambda match: "../" + match.group(1).replace("\\", "/"),
            projected,
        )
        projections.append((f"internal-procedures/{skill_name}.md", projected.encode("utf-8"), 0o644))
    return projections


def build_artifacts(root: Path, output_dir: Path, contract: dict[str, Any]) -> list[Path]:
    identity = source_identity(root)
    skill_entries = source_skill_entries(root)
    child_entries = internal_skill_entries(root)
    package_data = normalized_bytes(root / CONTRACT_PATH)

    plugin_entries: list[tuple[str, bytes, int]] = [
        (".codex-plugin/plugin.json", normalized_bytes(root / ".codex-plugin/plugin.json"), 0o644),
        (".claude-plugin/plugin.json", normalized_bytes(root / ".claude-plugin/plugin.json"), 0o644),
        (".claude-plugin/marketplace.json", normalized_bytes(root / ".claude-plugin/marketplace.json"), 0o644),
        (PACKAGE_NAME, package_data, 0o644),
    ]
    plugin_entries.extend(
        (f"skills/implementaudit/{relative.as_posix()}", data, mode)
        for relative, data, mode in skill_entries
    )
    plugin_entries.extend(child_entries)
    plugin_inventory = inventory_bytes("canonical_plugin", contract, identity, plugin_entries)
    plugin_entries.append((INVENTORY_NAME, plugin_inventory, 0o644))

    standalone_entries: list[tuple[str, bytes, int]] = [(PACKAGE_NAME, package_data, 0o644)]
    standalone_entries.extend(
        (relative.as_posix(), data, mode) for relative, data, mode in skill_entries
    )
    standalone_entries.extend(standalone_internal_procedure_entries(child_entries))
    standalone_inventory = inventory_bytes(
        "standalone_compatibility", contract, identity, standalone_entries
    )
    standalone_entries.append((INVENTORY_NAME, standalone_inventory, 0o644))

    zopfli_module = require_zopfli()
    plugin_path = output_dir / contract["generated_projections"]["canonical_plugin"]["artifact"]
    standalone_path = output_dir / contract["generated_projections"]["standalone_compatibility"]["artifact"]
    write_archive(plugin_path, plugin_entries, zopfli_module)
    write_archive(standalone_path, standalone_entries, zopfli_module)
    verify_artifact(root, "canonical_plugin", plugin_path, contract)
    verify_artifact(root, "standalone_compatibility", standalone_path, contract)
    return [plugin_path, standalone_path]


def verify_artifact(
    root: Path,
    role: str,
    asset: Path,
    contract: dict[str, Any],
    require_clean_source: bool = False,
) -> None:
    if role not in EXPECTED_PROJECTIONS:
        raise ContractError(f"unknown artifact role: {role}")
    expected_name = contract["generated_projections"][role]["artifact"]
    if asset.name != expected_name:
        raise ContractError(f"{role} artifact name must be {expected_name}")
    try:
        zf = zipfile.ZipFile(asset)
    except (FileNotFoundError, zipfile.BadZipFile) as exc:
        raise ContractError(f"invalid or missing artifact: {asset}") from exc
    with zf:
        infos = zf.infolist()
        names = [info.filename for info in infos]
        if names != sorted(names):
            raise ContractError(f"{role} archive entries are not sorted")
        if len(names) != len(set(names)):
            raise ContractError(f"{role} archive contains duplicate paths")
        for info in infos:
            relative = PurePosixPath(info.filename)
            if relative.is_absolute() or ".." in relative.parts or "\\" in info.filename:
                raise ContractError(f"unsafe archive path: {info.filename}")
            if info.create_system != 3 or info.compress_type != zipfile.ZIP_DEFLATED:
                raise ContractError(f"non-canonical ZIP metadata: {info.filename}")
            if info.extra or info.comment:
                raise ContractError(f"unexpected ZIP metadata: {info.filename}")
            observed_mode = (info.external_attr >> 16) & 0o777
            observed_type = stat.S_IFMT(info.external_attr >> 16)
            if observed_type != stat.S_IFREG:
                raise ContractError(f"archive member is not a regular file: {info.filename}")
            expected_mode = 0o755 if (
                info.filename.startswith("scripts/")
                or info.filename.startswith("skills/implementaudit/scripts/")
            ) else 0o644
            if observed_mode != expected_mode:
                raise ContractError(f"mode mismatch for {info.filename}")
            if info.filename.endswith(".sh") and b"\r\n" in zf.read(info.filename):
                raise ContractError(f"shell script contains CRLF: {info.filename}")

        required_meta = {PACKAGE_NAME, INVENTORY_NAME}
        if not required_meta.issubset(names):
            raise ContractError(f"{role} artifact lacks package identity or inventory")
        embedded_contract = json.loads(zf.read(PACKAGE_NAME).decode("utf-8"))
        require_equal("embedded package contract", embedded_contract, contract)
        inventory = json.loads(zf.read(INVENTORY_NAME).decode("utf-8"))
        require_equal("inventory schema", inventory.get("schema"), contract["inventory_contract"]["format"])
        require_equal("inventory role", inventory.get("artifact_role"), role)
        for field in (
            "package_name",
            "runtime_version",
            "release_family",
            "public_governor",
            "required_skills",
            "internal_skills",
        ):
            require_equal(f"inventory {field}", inventory.get(field), contract[field])
        source = inventory.get("source")
        if not isinstance(source, dict) or set(source) != {"commit", "tree", "worktree_state"}:
            raise ContractError("inventory source binding is incomplete")
        if source["worktree_state"] not in {"clean", "dirty"}:
            raise ContractError("inventory worktree_state must be clean or dirty")
        if require_clean_source and source["worktree_state"] != "clean":
            raise ContractError("release/install artifact source binding is dirty")
        if not re.fullmatch(r"[0-9a-f]{40}", str(source["commit"])) or not re.fullmatch(
            r"[0-9a-f]{40}", str(source["tree"])
        ):
            raise ContractError("inventory commit/tree identity is malformed")

        observed_members = []
        for name in names:
            if name == INVENTORY_NAME:
                continue
            data = zf.read(name)
            observed_members.append(
                {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            )
        require_equal("inventory members", inventory.get("members"), observed_members)

        if role == "canonical_plugin":
            required = {
                ".codex-plugin/plugin.json",
                ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
                "skills/implementaudit/SKILL.md",
            }
            if not required.issubset(names):
                raise ContractError("canonical plugin is missing a host manifest or governor")
            skill_names = sorted(
                PurePosixPath(name).parts[1]
                for name in names
                if len(PurePosixPath(name).parts) >= 3
                and PurePosixPath(name).parts[0] == "skills"
                and PurePosixPath(name).name == "SKILL.md"
            )
            require_equal(
                "canonical plugin skill population",
                skill_names,
                sorted(EXPECTED_REQUIRED_SKILLS),
            )
            for child in EXPECTED_REQUIRED_SKILLS[1:]:
                prefix = f"skills/{child}/"
                child_members = [name for name in names if name.startswith(prefix)]
                require_equal(
                    f"canonical plugin {child} member population",
                    child_members,
                    [f"{prefix}SKILL.md"],
                )
            expected_children = {
                name: data for name, data, _mode in internal_skill_entries(root)
            }
            for name, expected_data in expected_children.items():
                require_equal(
                    f"canonical plugin source parity for {name}",
                    zf.read(name),
                    expected_data,
                )
        else:
            if "SKILL.md" not in names or any(name.startswith("skills/") for name in names):
                raise ContractError("standalone projection must flatten the governor to archive root")
            if any(name.startswith(".codex-plugin/") or name.startswith(".claude-plugin/") for name in names):
                raise ContractError("standalone projection must exclude host plugin manifests")
            expected_procedures = sorted(
                f"internal-procedures/{name}.md" for name in EXPECTED_REQUIRED_SKILLS[1:]
            )
            observed_procedures = sorted(
                name for name in names if name.startswith("internal-procedures/")
            )
            require_equal(
                "standalone internal procedure population",
                observed_procedures,
                expected_procedures,
            )
            for name in observed_procedures:
                procedure = zf.read(name)
                if procedure.startswith(b"---\n"):
                    raise ContractError(
                        f"standalone internal procedure retains discoverable frontmatter: {name}"
                    )
                if re.search(rb"\.\.[\\/]+implementaudit[\\/]+", procedure):
                    raise ContractError(
                        f"standalone internal procedure retains plugin-relative owner path: {name}"
                    )
                for relative in re.findall(
                    r"`(\.\./(?:references|scripts|templates)/[^`]+)`",
                    procedure.decode("utf-8"),
                ):
                    resolved = posixpath.normpath(
                        posixpath.join(PurePosixPath(name).parent.as_posix(), relative)
                    )
                    if resolved not in names:
                        raise ContractError(
                            "standalone internal procedure reference is unreachable: "
                            f"{name} -> {relative}"
                        )
            expected_projection_entries = standalone_internal_procedure_entries(
                internal_skill_entries(root)
            )
            expected_projection_data = {
                name: data for name, data, _mode in expected_projection_entries
            }
            for name, expected_data in expected_projection_data.items():
                require_equal(
                    f"standalone internal procedure source parity for {name}",
                    zf.read(name),
                    expected_data,
                )

    size = asset.stat().st_size
    cap = contract["budgets"][role]["cap_bytes"]
    if size > cap:
        raise ContractError(f"{role} artifact exceeds reviewed cap: {size} > {cap} bytes")


def read_installed_inventory(target: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if target.is_symlink() or not target.is_dir():
        raise ContractError("installed plugin target must be a real directory")
    inventory = load_json(target / INVENTORY_NAME)
    package = load_json(target / PACKAGE_NAME)
    if inventory.get("schema") != "implementaudit.package-inventory.v1":
        raise ContractError("installed plugin inventory schema is invalid")
    if inventory.get("artifact_role") != "canonical_plugin":
        raise ContractError("installed target is not the canonical plugin role")
    for field in (
        "package_name",
        "runtime_version",
        "release_family",
        "public_governor",
        "required_skills",
        "internal_skills",
    ):
        if inventory.get(field) != package.get(field):
            raise ContractError(f"installed package/inventory disagree on {field}")
    members = inventory.get("members")
    if not isinstance(members, list):
        raise ContractError("installed inventory members must be a list")
    expected_paths = {INVENTORY_NAME}
    for member in members:
        if not isinstance(member, dict) or set(member) != {"path", "bytes", "sha256"}:
            raise ContractError("installed inventory member shape is invalid")
        relative = PurePosixPath(str(member["path"]))
        if relative.is_absolute() or ".." in relative.parts:
            raise ContractError(f"unsafe installed inventory path: {relative}")
        expected_paths.add(relative.as_posix())
        path = target.joinpath(*relative.parts)
        if path.is_symlink() or not path.is_file():
            raise ContractError(f"installed plugin member missing or non-regular: {relative}")
        data = path.read_bytes()
        if len(data) != member["bytes"] or hashlib.sha256(data).hexdigest() != member["sha256"]:
            raise ContractError(f"installed plugin member identity mismatch: {relative}")
    observed_paths = {
        path.relative_to(target).as_posix()
        for path in target.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    if observed_paths != expected_paths:
        extra = sorted(observed_paths - expected_paths)
        missing = sorted(expected_paths - observed_paths)
        raise ContractError(
            f"installed plugin population mismatch: missing={missing} extra={extra}"
        )
    return package, inventory


def numeric_version(value: Any) -> tuple[int, ...]:
    text = str(value)
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", text):
        raise ContractError(f"runtime version is not numeric dotted form: {text!r}")
    return tuple(int(part) for part in text.split("."))


def install_plugin(
    root: Path,
    host: str,
    raw_host_root: str,
    raw_asset: str,
    contract: dict[str, Any],
    allow_downgrade: bool,
) -> None:
    if host not in {"codex", "claude"}:
        raise ContractError("plugin host must be codex or claude")
    host_root_requested = Path(raw_host_root).absolute()
    try:
        host_root = host_root_requested.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ContractError("isolated host root does not exist") from exc
    if host_root_requested != host_root or host_root.is_symlink() or not host_root.is_dir():
        raise ContractError("isolated host root must be a real non-aliased directory")
    sentinel = host_root / ".implementaudit-isolated-host-root"
    if sentinel.is_symlink() or not sentinel.is_file():
        raise ContractError("isolated host root sentinel is missing")

    asset = Path(raw_asset).resolve(strict=True)
    verify_artifact(root, "canonical_plugin", asset, contract, require_clean_source=True)
    with zipfile.ZipFile(asset) as zf:
        incoming_inventory = json.loads(zf.read(INVENTORY_NAME).decode("utf-8"))
        incoming_package = json.loads(zf.read(PACKAGE_NAME).decode("utf-8"))

    standalone = host_root / "skills/implementaudit"
    if standalone.exists() or standalone.is_symlink():
        raise ContractError(
            "ambiguous same-identity plugin and standalone co-install is forbidden"
        )

    plugins_root = host_root / "plugins"
    plugins_root.mkdir(parents=True, exist_ok=True)
    if (
        plugins_root.is_symlink()
        or not plugins_root.is_dir()
        or plugins_root.resolve(strict=True) != plugins_root
    ):
        raise ContractError("isolated plugins transaction root must be a real non-aliased directory")
    target = plugins_root / "implementaudit"
    stage = plugins_root / f".implementaudit-stage-{os.getpid()}"
    backup = plugins_root / f".implementaudit-backup-{os.getpid()}"
    for transient in (stage, backup):
        if transient.exists() or transient.is_symlink():
            raise ContractError(f"stale install transaction path exists: {transient.name}")

    predecessor: tuple[dict[str, Any], dict[str, Any]] | None = None
    if target.exists() or target.is_symlink():
        predecessor = read_installed_inventory(target)
        prior_package, prior_inventory = predecessor
        prior_version = numeric_version(prior_package.get("runtime_version"))
        next_version = numeric_version(incoming_package.get("runtime_version"))
        prior_digest = hashlib.sha256((target / INVENTORY_NAME).read_bytes()).hexdigest()
        incoming_digest = hashlib.sha256(
            (json.dumps(incoming_inventory, indent=2, sort_keys=True) + "\n").encode("utf-8")
        ).hexdigest()
        if prior_digest == incoming_digest:
            print(
                "package-contract: plugin install idempotent "
                f"host={host} target={target} inventory_sha256={prior_digest}"
            )
            return
        if prior_version == next_version:
            raise ContractError(
                "same-version plugin source/package identity differs from the installed predecessor"
            )
        if prior_version > next_version and not allow_downgrade:
            raise ContractError(
                f"unauthorized downgrade rejected: {prior_package.get('runtime_version')} "
                f"-> {incoming_package.get('runtime_version')}"
            )

    fault = os.environ.get("IMPLEMENTAUDIT_INSTALL_FAULT", "")
    if fault not in {"", "before-swap", "during-swap", "remove-staged-member"}:
        raise ContractError(f"unknown install fault injection: {fault}")

    moved_predecessor = False
    installed_new = False
    try:
        stage.mkdir()
        with zipfile.ZipFile(asset) as zf:
            zf.extractall(stage)
        read_installed_inventory(stage)
        if fault == "remove-staged-member":
            (stage / "skills/implementaudit/SKILL.md").unlink()
            read_installed_inventory(stage)
        if fault == "before-swap":
            raise ContractError("injected before-swap failure")
        if target.exists():
            target.rename(backup)
            moved_predecessor = True
        if fault == "during-swap":
            raise ContractError("injected during-swap failure")
        stage.rename(target)
        installed_new = True
        package, inventory = read_installed_inventory(target)
        if package != incoming_package or inventory != incoming_inventory:
            raise ContractError("post-swap package/inventory readback mismatch")
    except BaseException:
        if installed_new and target.exists():
            shutil.rmtree(target)
        if moved_predecessor and backup.exists():
            backup.rename(target)
        if stage.exists():
            shutil.rmtree(stage)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    inventory_digest = hashlib.sha256((target / INVENTORY_NAME).read_bytes()).hexdigest()
    print(
        "package-contract: plugin staged-copy install ok "
        f"host={host} target={target} members={len(incoming_inventory['members']) + 1} "
        f"version={incoming_package['runtime_version']} "
        f"source_commit={incoming_inventory['source']['commit']} "
        f"source_tree={incoming_inventory['source']['tree']} "
        f"source_state={incoming_inventory['source']['worktree_state']} "
        f"inventory_sha256={inventory_digest} proof=staged-copy"
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--build", metavar="OUTPUT_DIR")
    actions.add_argument(
        "--check-budget-size",
        nargs=2,
        metavar=("ROLE", "BYTES"),
    )
    actions.add_argument(
        "--verify-artifact",
        nargs=2,
        metavar=("ROLE", "PATH"),
    )
    actions.add_argument(
        "--install-plugin",
        nargs=3,
        metavar=("HOST", "HOST_ROOT", "ASSET"),
    )
    parser.add_argument("--allow-downgrade", action="store_true")
    parser.add_argument("--require-clean-source", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.repo_root).resolve()
    try:
        contract = validate_contract(root)
        if args.build:
            paths = build_artifacts(root, Path(args.build).resolve(), contract)
            for path in paths:
                print(f"package-contract: wrote {path}")
        elif args.verify_artifact:
            role, raw_path = args.verify_artifact
            verify_artifact(
                root,
                role,
                Path(raw_path).resolve(),
                contract,
                require_clean_source=args.require_clean_source,
            )
        elif args.install_plugin:
            host, host_root, raw_asset = args.install_plugin
            install_plugin(
                root,
                host,
                host_root,
                raw_asset,
                contract,
                args.allow_downgrade,
            )
        elif args.check_budget_size:
            role, raw_size = args.check_budget_size
            budgets = contract["budgets"]
            if role not in budgets:
                raise ContractError(f"unknown artifact budget role: {role}")
            try:
                size = int(raw_size)
            except ValueError as exc:
                raise ContractError(f"artifact byte size is not an integer: {raw_size}") from exc
            if size < 0:
                raise ContractError("artifact byte size must be non-negative")
            cap = budgets[role]["cap_bytes"]
            if size > cap:
                raise ContractError(
                    f"{role} artifact exceeds reviewed cap: {size} > {cap} bytes"
                )
    except ContractError as exc:
        print(f"package-contract: {exc}", file=sys.stderr)
        return 1
    print("package-contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
