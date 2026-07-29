#!/usr/bin/env python3
"""Strict exact-byte manifests for campaign evaluated surfaces."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import stat


SCHEMA = "implementaudit-evaluated-surfaces-v1"
OWNER_SCHEMA = "implementaudit-evaluated-surface-owners-v1"
PROJECTION_SCHEMA = "implementaudit-evaluated-surface-projection-v1"
B3_CAMPAIGN = "b3v4-sol-luna-r2"
MATRIX_CAMPAIGN = "candidate-matrix-sol-luna-r1"
CAMPAIGNS = (B3_CAMPAIGN, MATRIX_CAMPAIGN)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_ID = re.compile(r"^[0-9a-f]{40}$")
READ_CHUNK_SIZE = 1024 * 1024

_COMMON_ROLES = (
    "acceptance-rules",
    "adapter",
    "artifact-contract",
    "authorization-acknowledgement",
    "checkout-runtime-topology",
    "evaluator",
    "evidence-contract",
    "fixture-inventory",
    "host-attestation",
    "host-read-contract",
    "host-runner",
    "independent-rederiver",
    "launcher",
    "lifecycle-contract",
    "model-reasoning-host-identity",
    "native-executable",
    "official-driver",
    "prompt-construction-rules",
    "prompt-template",
    "scorer",
    "seed-order-repetition-rules",
    "verdict-contract",
)
_MATRIX_FIXTURES = (
    "B0", "B1", "B2", "E1", "E2a", "E2b", "E3", "E4",
    "E5", "E6", "E7", "E8", "E9", "E10",
)
REQUIRED_ROLES = {
    B3_CAMPAIGN: tuple(sorted(
        _COMMON_ROLES + ("product-candidate", "product-control",
                         "fixture-B3-v3"))),
    MATRIX_CAMPAIGN: tuple(sorted(
        _COMMON_ROLES + ("product-candidate",) +
        tuple(f"fixture-{name}" for name in _MATRIX_FIXTURES))),
}
GIT_IDENTITY_ROLES = {
    B3_CAMPAIGN: frozenset({
        "product-candidate", "product-control", "official-driver",
        "host-runner", "scorer", "evaluator", "adapter",
        "independent-rederiver",
    }),
    MATRIX_CAMPAIGN: frozenset({
        "product-candidate", "official-driver", "host-runner", "scorer",
        "evaluator", "adapter", "independent-rederiver",
    }),
}
EXTERNAL_ROLES = {
    B3_CAMPAIGN: frozenset({
        "product-candidate", "product-control",
        "authorization-acknowledgement", "host-attestation", "launcher",
        "native-executable", "checkout-runtime-topology",
    }),
    MATRIX_CAMPAIGN: frozenset({
        "product-candidate", "authorization-acknowledgement",
        "host-attestation", "launcher", "native-executable",
        "checkout-runtime-topology",
    }),
}

INLINE_ROLES = frozenset({
    "acceptance-rules", "authorization-acknowledgement",
    "evidence-contract", "fixture-inventory",
    "model-reasoning-host-identity", "seed-order-repetition-rules",
})
FIXED_FILE_PATHS = {
    "adapter": "eval/adapters.py",
    "artifact-contract": None,
    "evaluator": None,
    "host-read-contract": "eval/lib/hostread.py",
    "host-runner": None,
    "independent-rederiver": None,
    "lifecycle-contract": "eval/campaign_lifecycle.py",
    "official-driver": None,
    "prompt-construction-rules": "eval/hosts.py",
    "scorer": None,
    "verdict-contract": "eval/lib/verdict.py",
}
EXPLICIT_PATH_ROLES = frozenset({
    "checkout-runtime-topology", "host-attestation", "launcher",
    "product-candidate", "product-control", "prompt-template",
})


def canonical_json_bytes(value):
    return (json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":")) + "\n").encode("utf-8")


def projection_path(role):
    if role not in INLINE_ROLES:
        raise ValueError(f"evaluated surface {role} is not packet-projected")
    return f"evaluated-surface-projections/{role}.json"


def _projection_value(packet, campaign, role):
    if role == "acceptance-rules":
        value = {
            "acceptance_rule": packet["acceptance_rule"],
            "invalid_error_rule": packet["invalid_error_rule"],
            "result_composition": packet["result_composition"],
            "stop_conditions": packet["stop_conditions"],
        }
    elif role == "authorization-acknowledgement":
        value = packet["authorization"]
    elif role == "evidence-contract":
        value = {
            "attempt_policy": packet["attempt_policy"],
            "bundle_artifact": packet["artifacts"]["bundle"],
            "evidence_profiles": packet["evidence_profiles"],
            "luna_stage": packet["luna_stage"],
        }
    elif role == "fixture-inventory":
        value = packet["fixture"] if campaign == B3_CAMPAIGN \
            else packet["fixtures"]
    elif role == "model-reasoning-host-identity":
        value = packet["configurations"]["L"] if campaign == B3_CAMPAIGN \
            else packet["configuration"]
    elif role == "seed-order-repetition-rules":
        value = {
            "missions": packet["missions"],
            "repetitions_per_arm": packet["repetitions_per_arm"],
            "seed": packet["seed"],
        } if campaign == B3_CAMPAIGN else {
            "cells": packet["cells"], "seed": packet["seed"],
        }
    else:
        raise ValueError(f"evaluated surface projection role invalid: {role}")
    return {
        "campaign": campaign, "projection": value, "role": role,
        "schema": PROJECTION_SCHEMA,
    }


def projection_bytes(packet, campaign, role):
    return canonical_json_bytes(_projection_value(packet, campaign, role))


def _owner_kind(role):
    return f"frozen-{role}"


def _validate_owned_path_policy(path, role):
    name = pathlib.PurePosixPath(path.replace("\\", "/")).name.lower()
    if role in ("product-candidate", "product-control"):
        expected_owner = role[len("product-"):]
        valid = (
            name == "skill.md" and
            pathlib.PurePosixPath(path.replace("\\", "/")).parent.name.lower()
            == expected_owner)
    elif role == "host-attestation":
        valid = name.endswith(".json") and "attestation" in name
    elif role == "checkout-runtime-topology":
        valid = name == "checkout-runtime-topology.json"
    elif role == "launcher":
        valid = name in ("codex", "codex.exe", "luna-launcher",
                         "luna-launcher.exe")
    elif role == "prompt-template":
        valid = name in ("prompt-template.md", "prompt-template.txt",
                         "readme.md")
    else:
        valid = True
    if not valid:
        raise ValueError(
            f"evaluated surface owner {role} path policy invalid")


def _exact_owner(owner, fields, role):
    if type(owner) is not dict or set(owner) != set(fields):
        raise ValueError(f"evaluated surface owner {role} fields invalid")
    if any(type(owner[field]) is not str or not owner[field]
           for field in fields):
        raise ValueError(
            f"evaluated surface owner {role} scalar types invalid")
    return owner


def _owned_git(owner, role):
    git = {
        "git_commit": owner["git_commit"],
        "git_tree": owner["git_tree"],
    }
    if (type(git["git_commit"]) is not str or
            type(git["git_tree"]) is not str or
            not GIT_ID.fullmatch(git["git_commit"]) or
            not GIT_ID.fullmatch(git["git_tree"])):
        raise ValueError(f"evaluated surface owner {role} Git identity invalid")
    return git


def _packet_file_identity(packet, campaign, role, owner):
    """Derive one role's authoritative path/hash/Git identity from its owner."""
    git = {}
    if role in INLINE_ROLES:
        _exact_owner(owner, {"kind"}, role)
        if owner["kind"] != f"packet-projection-{role}":
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        raw = projection_bytes(packet, campaign, role)
        return projection_path(role), hashlib.sha256(raw).hexdigest(), git, raw
    if role == "artifact-contract":
        _exact_owner(owner, {"kind"}, role)
        if owner["kind"] != "packet-artifact-contract":
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        row = packet["artifact_contract"]
        return row["path"], row["sha256"], git, None
    if role in ("scorer", "evaluator", "host-runner"):
        artifact = {"host-runner": "runner"}.get(role, role)
        _exact_owner(
            owner, {"kind", "artifact", "git_commit", "git_tree"}, role)
        if (owner["kind"] != f"packet-artifact-{role}" or
                owner["artifact"] != artifact):
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        row = packet["artifacts"][artifact]
        return row["path"], row["sha256"], _owned_git(owner, role), None
    if role.startswith("fixture-"):
        fixture_id = role[len("fixture-"):]
        _exact_owner(owner, {"kind", "fixture_id"}, role)
        if (owner["kind"] != "packet-fixture" or
                owner["fixture_id"] != fixture_id):
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        if campaign == B3_CAMPAIGN:
            if fixture_id != packet["fixture"]["id"]:
                raise ValueError(f"evaluated surface owner {role} fixture invalid")
            row = packet["fixture"]
            path = f"eval/fixtures/{fixture_id}/fixture.json"
            digest = row["fixture_sha256"]
        else:
            matches = [row for row in packet["fixtures"]
                       if row["id"] == fixture_id]
            if len(matches) != 1:
                raise ValueError(f"evaluated surface owner {role} fixture invalid")
            path, digest = matches[0]["path"], matches[0]["sha256"]
        return path, digest, git, None
    if role == "independent-rederiver":
        _exact_owner(owner, {"kind", "git_commit", "git_tree"}, role)
        if owner["kind"] != "packet-independent-rederiver":
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        row = packet["independent_rederiver"]["implementation_identity"]
        return row["path"], row["sha256"], _owned_git(owner, role), None
    if role == "native-executable":
        _exact_owner(owner, {"kind"}, role)
        if owner["kind"] != "packet-native-executable":
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        row = packet["configurations"]["L"]["executable"] \
            if campaign == B3_CAMPAIGN else packet["configuration"]["executable"]
        return row["path"], row["sha256"], git, None
    if role in ("product-candidate", "product-control"):
        packet_owner = role[len("product-"):]
        if campaign == MATRIX_CAMPAIGN and packet_owner != "candidate":
            raise ValueError(f"evaluated surface owner {role} campaign invalid")
        _exact_owner(owner, {"kind", "packet_owner", "path"}, role)
        if (owner["kind"] != f"packet-{role}" or
                owner["packet_owner"] != packet_owner):
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        row = packet[packet_owner]
        git = {"git_commit": row["commit"], "git_tree": row["tree"]}
        _validate_owned_path_policy(owner["path"], role)
        return owner["path"], row["payload_sha256"], git, None
    if role == "host-attestation":
        _exact_owner(owner, {"kind", "path"}, role)
        if owner["kind"] != "packet-host-attestation":
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        row = packet["configurations"]["L"]["host_attestation"] \
            if campaign == B3_CAMPAIGN else \
            packet["configuration"]["host_attestation"]
        _validate_owned_path_policy(owner["path"], role)
        return owner["path"], row["sha256"], git, None
    if role in FIXED_FILE_PATHS:
        expected_path = FIXED_FILE_PATHS[role]
        if role == "official-driver":
            expected_path = "eval/b3v4_campaign.py" if \
                campaign == B3_CAMPAIGN else "eval/candidate_matrix_campaign.py"
        fields = {"kind", "sha256"}
        if role in GIT_IDENTITY_ROLES[campaign]:
            fields |= {"git_commit", "git_tree"}
        _exact_owner(owner, fields, role)
        if owner["kind"] != _owner_kind(role):
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        if role in GIT_IDENTITY_ROLES[campaign]:
            git = _owned_git(owner, role)
        return expected_path, owner["sha256"], git, None
    if role in EXPLICIT_PATH_ROLES:
        _exact_owner(owner, {"kind", "path", "sha256"}, role)
        if owner["kind"] != _owner_kind(role):
            raise ValueError(f"evaluated surface owner {role} kind invalid")
        _validate_owned_path_policy(owner["path"], role)
        return owner["path"], owner["sha256"], git, None
    raise ValueError(f"evaluated surface owner role unsupported: {role}")


def validate_packet_owners(packet, campaign):
    owners = packet.get("evaluated_surface_owners") \
        if type(packet) is dict else None
    if type(owners) is not dict or set(owners) != {"schema", "campaign", "roles"}:
        raise ValueError("evaluated surface owners fields invalid")
    if owners["schema"] != OWNER_SCHEMA or owners["campaign"] != campaign:
        raise ValueError("evaluated surface owners campaign/schema mismatch")
    roles = owners["roles"]
    if type(roles) is not dict or set(roles) != set(required_roles(campaign)):
        raise ValueError("evaluated surface owner role coverage invalid")
    for role in required_roles(campaign):
        path, digest, _git, _raw = _packet_file_identity(
            packet, campaign, role, roles[role])
        _normalize_path(path, campaign, role)
        if type(digest) is not str or not SHA256.fullmatch(digest):
            raise ValueError(f"evaluated surface owner {role} SHA-256 invalid")
    return owners


def validate_packet_surfaces(packet, campaign, *, root=None):
    owners = validate_packet_owners(packet, campaign)["roles"]
    manifest = validate_manifest(packet["evaluated_surfaces"], campaign)
    by_role = {row["role"]: row for row in manifest["entries"]}
    for role in required_roles(campaign):
        path, digest, git, raw = _packet_file_identity(
            packet, campaign, role, owners[role])
        entry = by_role[role]
        if entry["path"] != path or entry["sha256"] != digest:
            raise ValueError(
                f"evaluated surface owner/manifest mismatch: {role}")
        observed_git = {
            key: entry[key] for key in ("git_commit", "git_tree")
            if key in entry
        }
        if observed_git != git:
            raise ValueError(
                f"evaluated surface owner/Git mismatch: {role}")
        if raw is not None and entry["byte_length"] != len(raw):
            raise ValueError(
                f"evaluated surface projection length mismatch: {role}")
    if root is not None:
        revalidate_manifest(manifest, root=root)
    return manifest


def build_manifest_from_packet(packet, campaign, *, root):
    """Author the manifest from the closed semantic owner map and custody."""
    roles = validate_packet_owners(packet, campaign)["roles"]
    sources = []
    for role in required_roles(campaign):
        path, _digest, git, raw = _packet_file_identity(
            packet, campaign, role, roles[role])
        if raw is None:
            sources.append({"role": role, "path": path, **git})
    manifest = build_manifest_with_packet_projections(
        packet, campaign, sources, root=root)
    packet["evaluated_surfaces"] = manifest
    validate_packet_surfaces(packet, campaign, root=root)
    return manifest


def build_manifest_with_packet_projections(
        packet, campaign, sources, *, root):
    """Custody-build physical entries and rederive packet-owned virtual ones."""
    roles = validate_packet_owners(packet, campaign)["roles"]
    virtual_entries = []
    for role in INLINE_ROLES:
        path, digest, git, raw = _packet_file_identity(
            packet, campaign, role, roles[role])
        if git or raw is None or path != projection_path(role):
            raise ValueError(
                f"evaluated surface virtual projection invalid: {role}")
        virtual_entries.append({
            "role": role, "path": path, "byte_length": len(raw),
            "sha256": digest,
        })
    _reject_projection_shadow(root)
    entries = _physical_entries(campaign, sources, root=root)
    entries.extend(virtual_entries)
    entries.sort(key=lambda row: row["role"])
    manifest = validate_manifest(
        {"schema": SCHEMA, "campaign": campaign, "entries": entries},
        campaign)
    return manifest


def required_roles(campaign):
    if type(campaign) is not str or campaign not in REQUIRED_ROLES:
        raise ValueError("unsupported evaluated-surface campaign")
    return REQUIRED_ROLES[campaign]


def _reparse_point(path_stat):
    return bool(getattr(path_stat, "st_file_attributes", 0) &
                getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _walk_no_alias(path, owner):
    current = pathlib.Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        observed = os.lstat(current)
        if stat.S_ISLNK(observed.st_mode) or _reparse_point(observed):
            raise ValueError(f"{owner} link or reparse alias forbidden")


def _reject_projection_shadow(root):
    shadow = pathlib.Path(root).absolute() / "evaluated-surface-projections"
    if os.path.lexists(shadow):
        raise ValueError(
            "evaluated surface virtual projection shadow or residue forbidden")


def _stable_file_identity(path, owner):
    path = pathlib.Path(path).absolute()
    try:
        resolved = path.resolve(strict=True)
        if resolved != path:
            raise ValueError(f"{owner} link or reparse alias forbidden")
        _walk_no_alias(path, owner)
        before = os.lstat(path)
        if stat.S_ISLNK(before.st_mode) or _reparse_point(before):
            raise ValueError(f"{owner} link or reparse alias forbidden")
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"{owner} must be a retained regular file")
        if before.st_nlink != 1:
            raise ValueError(f"{owner} hardlink identity forbidden")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or
                    (opened.st_dev, opened.st_ino) !=
                    (before.st_dev, before.st_ino)):
                raise ValueError(f"{owner} identity changed during custody read")
            digest = hashlib.sha256()
            length = 0
            with os.fdopen(descriptor, "rb") as stream:
                descriptor = None
                while True:
                    chunk = stream.read(READ_CHUNK_SIZE)
                    if not chunk:
                        break
                    length += len(chunk)
                    digest.update(chunk)
                after = os.fstat(stream.fileno())
            if (not stat.S_ISREG(after.st_mode) or after.st_nlink != 1 or
                    (after.st_dev, after.st_ino, after.st_size,
                     getattr(after, "st_mtime_ns", None)) !=
                    (opened.st_dev, opened.st_ino, opened.st_size,
                     getattr(opened, "st_mtime_ns", None)) or
                    length != after.st_size):
                raise ValueError(f"{owner} identity changed during custody read")
            lexical_key = os.path.normcase(os.path.normpath(str(path)))
            canonical_key = os.path.normcase(os.path.normpath(str(resolved)))
            physical_key = (opened.st_dev, opened.st_ino)
            return length, digest.hexdigest(), (
                lexical_key, canonical_key, physical_key)
        finally:
            if descriptor is not None:
                os.close(descriptor)
    except ValueError:
        raise
    except OSError as exc:
        raise ValueError(f"{owner} cannot be read as retained evidence") from exc


def _normalize_path(value, campaign, role):
    if type(value) is not str or not value or "\x00" in value:
        raise ValueError(f"evaluated surface {role} path invalid")
    if "\\" in value:
        raise ValueError(f"evaluated surface {role} path is not canonical")
    supplied = pathlib.PurePosixPath(value)
    is_absolute = pathlib.Path(value).is_absolute()
    if (any(part in ("", ".", "..") for part in supplied.parts) or
            (not is_absolute and value.startswith("/"))):
        raise ValueError(f"evaluated surface {role} path escapes owner root")
    if is_absolute and role not in EXTERNAL_ROLES[campaign]:
        raise ValueError(
            f"evaluated surface {role} cannot use an external path")
    return value


def _source_path(root, stored_path, campaign, role):
    normalized = _normalize_path(stored_path, campaign, role)
    path = pathlib.Path(normalized)
    if path.is_absolute():
        return path.absolute()
    root = pathlib.Path(root).absolute()
    candidate = (root / pathlib.PurePosixPath(normalized)).absolute()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"evaluated surface {role} path escapes owner root") from exc
    return candidate


def _validate_git(entry, campaign, role):
    present = {key for key in ("git_commit", "git_tree") if key in entry}
    if present and present != {"git_commit", "git_tree"}:
        raise ValueError(
            f"evaluated surface {role} Git identity must bind commit and tree")
    if present:
        if role not in GIT_IDENTITY_ROLES[campaign]:
            raise ValueError(
                f"evaluated surface {role} does not permit Git identity")
        if (type(entry["git_commit"]) is not str or
                not GIT_ID.fullmatch(entry["git_commit"]) or
                type(entry["git_tree"]) is not str or
                not GIT_ID.fullmatch(entry["git_tree"])):
            raise ValueError(
                f"evaluated surface {role} Git identity invalid")


def validate_manifest(manifest, campaign):
    if type(manifest) is not dict or set(manifest) != {
            "schema", "campaign", "entries"}:
        raise ValueError("evaluated surface manifest fields invalid")
    if manifest["schema"] != SCHEMA or manifest["campaign"] != campaign:
        raise ValueError("evaluated surface manifest campaign/schema mismatch")
    entries = manifest["entries"]
    if type(entries) is not list:
        raise ValueError("evaluated surface entries must be an exact list")
    roles = []
    paths = []
    for index, entry in enumerate(entries):
        if type(entry) is not dict:
            raise ValueError(f"evaluated surface entry {index} must be an object")
        allowed = {"role", "path", "byte_length", "sha256"}
        if "git_commit" in entry or "git_tree" in entry:
            allowed |= {"git_commit", "git_tree"}
        if set(entry) != allowed:
            raise ValueError(f"evaluated surface entry {index} fields invalid")
        role = entry["role"]
        if type(role) is not str or role not in required_roles(campaign):
            raise ValueError(f"evaluated surface role invalid: {role!r}")
        path = _normalize_path(entry["path"], campaign, role)
        if type(entry["byte_length"]) is not int or entry["byte_length"] < 0:
            raise ValueError(f"evaluated surface {role} byte length invalid")
        if type(entry["sha256"]) is not str or not SHA256.fullmatch(
                entry["sha256"]):
            raise ValueError(f"evaluated surface {role} SHA-256 invalid")
        _validate_git(entry, campaign, role)
        roles.append(role)
        paths.append(path)
    duplicate_roles = sorted({role for role in roles if roles.count(role) > 1})
    if duplicate_roles:
        raise ValueError(f"evaluated surface duplicate role: {duplicate_roles}")
    normalized_paths = [
        os.path.normcase(os.path.normpath(path.replace("/", os.sep)))
        for path in paths
    ]
    duplicate_paths = sorted({
        path for path in normalized_paths if normalized_paths.count(path) > 1})
    if duplicate_paths:
        raise ValueError(f"evaluated surface duplicate path: {duplicate_paths}")
    expected = list(required_roles(campaign))
    missing = sorted(set(expected) - set(roles))
    extra = sorted(set(roles) - set(expected))
    if missing or extra:
        detail = missing[0] if missing else extra[0]
        raise ValueError(
            f"evaluated surface role coverage invalid: {detail}")
    if roles != expected:
        raise ValueError("evaluated surface roles must use canonical order")
    return manifest


def _physical_entries(campaign, sources, *, root):
    if type(sources) is not list:
        raise TypeError("evaluated surface sources must be an exact list")
    entries = []
    identity_owners = {}
    for source in sources:
        if type(source) is not dict:
            raise TypeError("evaluated surface source must be an exact object")
        if set(source) not in (
                {"role", "path"},
                {"role", "path", "git_commit", "git_tree"}):
            raise ValueError("evaluated surface source fields invalid")
        role = source["role"]
        if type(role) is not str or role not in required_roles(campaign):
            raise ValueError(f"evaluated surface role invalid: {role!r}")
        stored_path = _normalize_path(source["path"], campaign, role)
        source_path = _source_path(root, stored_path, campaign, role)
        length, digest, identities = _stable_file_identity(
            source_path,
            f"evaluated surface {role}")
        for identity in set(identities):
            if identity in identity_owners:
                raise ValueError(
                    "evaluated surface physical alias forbidden: "
                    f"{identity_owners[identity]} and {role}")
            identity_owners[identity] = role
        entry = {
            "role": role, "path": stored_path,
            "byte_length": length, "sha256": digest,
        }
        for key in ("git_commit", "git_tree"):
            if key in source:
                entry[key] = source[key]
        _validate_git(entry, campaign, role)
        entries.append(entry)
    return entries


def build_manifest(campaign, sources, *, root):
    entries = _physical_entries(campaign, sources, root=root)
    entries.sort(key=lambda row: row["role"])
    manifest = {"schema": SCHEMA, "campaign": campaign, "entries": entries}
    return validate_manifest(manifest, campaign)


def _virtual_projection_entry(entry):
    return (
        entry["role"] in INLINE_ROLES and
        entry["path"] == projection_path(entry["role"]))


def revalidate_manifest(manifest, *, root):
    campaign = manifest.get("campaign") if type(manifest) is dict else None
    validate_manifest(manifest, campaign)
    if any(_virtual_projection_entry(entry)
           for entry in manifest["entries"]):
        _reject_projection_shadow(root)
    identity_owners = {}
    for entry in manifest["entries"]:
        if _virtual_projection_entry(entry):
            continue
        length, digest, identities = _stable_file_identity(
            _source_path(root, entry["path"], campaign, entry["role"]),
            f"evaluated surface {entry['role']}")
        for identity in set(identities):
            if identity in identity_owners:
                raise ValueError(
                    "evaluated surface physical alias forbidden: "
                    f"{identity_owners[identity]} and {entry['role']}")
            identity_owners[identity] = entry["role"]
        if length != entry["byte_length"] or digest != entry["sha256"]:
            raise ValueError(
                f"evaluated surface byte drift: {entry['role']}")
    return manifest


def custody_identity_map(manifest, *, root):
    campaign = manifest.get("campaign") if type(manifest) is dict else None
    validate_manifest(manifest, campaign)
    if any(_virtual_projection_entry(entry)
           for entry in manifest["entries"]):
        _reject_projection_shadow(root)
    observed = {}
    identity_owners = {}
    for entry in manifest["entries"]:
        role = entry["role"]
        if _virtual_projection_entry(entry):
            continue
        length, digest, identities = _stable_file_identity(
            _source_path(root, entry["path"], campaign, role),
            f"evaluated surface {role}")
        if length != entry["byte_length"] or digest != entry["sha256"]:
            raise ValueError(f"evaluated surface byte drift: {role}")
        lexical, canonical, physical = identities
        for identity_type, identity in (
                ("lexical", lexical),
                ("canonical", canonical),
                ("physical", physical)):
            token = (identity_type, identity)
            if token in identity_owners:
                raise ValueError(
                    "evaluated surface physical alias forbidden: "
                    f"{identity_owners[token]} and {role}")
            identity_owners[token] = role
        observed[role] = {
            "lexical": lexical,
            "canonical": canonical,
            "physical": physical,
        }
    return observed


def revalidate_file_binding(binding, *, root, owner="bound evidence"):
    if type(binding) is not dict or set(binding) != {
            "name", "status", "path", "byte_length", "sha256"}:
        raise ValueError(f"{owner} binding fields invalid")
    if (type(binding["name"]) is not str or not binding["name"] or
            binding["status"] != "PASS"):
        raise ValueError(f"{owner} identity/status invalid")
    path = binding["path"]
    if (type(path) is not str or not path or "\\" in path or
            pathlib.Path(path).is_absolute() or
            any(part in ("", ".", "..")
                for part in pathlib.PurePosixPath(path).parts)):
        raise ValueError(f"{owner} path escapes owner root")
    if (type(binding["byte_length"]) is not int or
            binding["byte_length"] < 0 or
            type(binding["sha256"]) is not str or
            not SHA256.fullmatch(binding["sha256"])):
        raise ValueError(f"{owner} byte identity invalid")
    observed_length, observed_sha, _identities = _stable_file_identity(
        pathlib.Path(root).absolute() / pathlib.PurePosixPath(path), owner)
    if (observed_length != binding["byte_length"] or
            observed_sha != binding["sha256"]):
        raise ValueError(f"{owner} evidence byte drift")
    return binding


def compare_relevant_surfaces(before, after, campaign):
    validate_manifest(before, campaign)
    validate_manifest(after, campaign)
    prior = {row["role"]: row for row in before["entries"]}
    current = {row["role"]: row for row in after["entries"]}
    for role in required_roles(campaign):
        left = prior[role]
        right = current[role]
        for field in ("path", "byte_length", "sha256"):
            if left[field] != right[field]:
                raise ValueError(
                    f"evaluated surface byte drift: {role} ({field})")
    return True
