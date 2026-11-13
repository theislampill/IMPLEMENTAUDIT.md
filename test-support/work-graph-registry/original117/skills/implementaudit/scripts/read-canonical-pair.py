#!/usr/bin/env python3
"""Read a claim-owner verified pair into a new private validation snapshot.

Exit 3 selects legacy structural validation only. This adapter owns no refs,
currentness, schema migration, dispatch, or guard exemptions. --native-guards
requires the paired preserved native profile and prepares inputs for the
unchanged native validators. --verify-current compares the completed snapshot
with another complete native read; neither snapshot is currentness authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

# Private substrate is exact-source bound; it owns no transaction authority.
def _windows_custody():
    import types
    path = Path(__file__).absolute().with_name("canonical_custody.py")
    before = os.lstat(path)
    if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
            or getattr(before, "st_file_attributes", 0) & 0x400):
        raise ImportError("canonical custody substrate is aliased or nonregular")
    with open(path, "rb") as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(33630)
        after = os.fstat(stream.fileno())
    if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
            or (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            or len(raw) != 33629
            or hashlib.sha256(raw).hexdigest() != "bfa07f0088f2df7b8c1196ccd149ebf8c6874337b35ac9a9c91ac51367a7fb1f"):
        raise ImportError("canonical custody substrate source identity mismatch")
    module_name = "_canonical_custody_" + hashlib.sha256(raw).hexdigest()
    if module_name in sys.modules:
        return sys.modules[module_name]
    module = types.ModuleType(module_name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    sys.modules[module_name] = module
    return module


_CUSTODY = _windows_custody()
_WINDOWS = _CUSTODY if os.name == "nt" else None


sys.dont_write_bytecode = True
OWNER = Path(__file__).resolve().with_name("claim-run.sh")


class ReaderError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReaderError(message)


def directory(path):
    """Open each POSIX ancestor without following a link; never resolve aliases."""
    if _WINDOWS is not None:
        held = _WINDOWS.Directory(path)
        return held.path, held
    require(os.name == "posix" and hasattr(os, "O_NOFOLLOW") and os.open in os.supports_dir_fd,
            "UNSUPPORTED_NATIVE_ANCESTRY")
    require(not any(part in (".", "..") for part in str(path).split("/")), "lexical path alias")
    path = Path(os.path.abspath(path))
    fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return path, fd
    except BaseException:
        os.close(fd)
        raise


def regular_at(fd, name, *, optional=False):
    if _WINDOWS is not None:
        try:
            with _WINDOWS.File(fd, name) as held:
                return held.read()
        except FileNotFoundError:
            if optional:
                fd.verify()
                return None
            raise
    try:
        opened = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    except FileNotFoundError:
        if optional:
            return None
        raise
    try:
        before = os.fstat(opened)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "non-regular or multiply linked discovery file")
        with os.fdopen(os.dup(opened), "rb") as stream:
            data = stream.read()
        after = os.fstat(opened)
        require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
                "discovery file changed during read")
        return data
    finally:
        os.close(opened)


def call(cwd, argv):
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GIT_", "IMPLEMENTAUDIT_"))}
    env.update(PYTHONDONTWRITEBYTECODE="1", LC_ALL="C")
    if os.name == "nt" and argv[0] in {"git", "bash"}:
        options = ["-c", "core.longpaths=true"] if argv[0] == "git" else []
        root = Path(r"C:\Program Files\Git")
        direct = root / "mingw64/bin/git.exe"
        executable = (direct if direct.is_file() and not direct.is_symlink() else root / "cmd/git.exe") if argv[0] == "git" else root / "bin/bash.exe"
        argv = [str(executable), *options, *argv[1:]]
    return subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)


def close_directory(fd):
    if _WINDOWS is not None:
        fd.close()
    else:
        os.close(fd)


def directory_names(fd):
    return fd.names() if _WINDOWS is not None else os.listdir(fd)


def owner(repo, *arguments):
    return call(repo, ["bash", str(OWNER), *arguments])


def controller_population_binds(run, claim_id=None, *, allow_non_git=False, legacy_controller=None):
    """Discovery only: absent hints cannot hide controller or retained authority.

    A record for another run is orientation data, never a currentness proof.
    Malformed/symbolic/unsafe records cannot establish an absent binding.
    """
    prefixes = ("controllers", "current-generations", "current-generation-migrations")
    result = call(run, ["git", "rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        require(allow_non_git and result.returncode == 128 and not result.stdout
                and result.stderr.startswith(b"fatal: not a git repository"),
                "controller Git discovery refused")
        for parent in (run, *run.parents):
            try:
                _, fd = directory(parent / ".git")
            except FileNotFoundError:
                continue
            try:
                require(not directory_names(fd), "unresolved nonempty Git discovery custody")
            finally:
                close_directory(fd)
        return False
    repo = Path(result.stdout.decode("utf-8").strip())
    require(repo.is_absolute() and run.is_relative_to(repo), "controller discovery is outside requested run custody")
    result = call(run, ["git", "for-each-ref", "--format=%(refname)%09%(symref)%09%(objecttype)",
                        *["refs/implementaudit/" + name + "/" for name in prefixes]])
    require(result.returncode == 0 and not result.stderr, "controller discovery is not complete")
    for line in result.stdout.splitlines():
        fields = line.split(b"\t")
        require(len(fields) == 3 and fields[1:] == [b"", b"blob"], "symbolic or non-blob discovery ref")
        raw_ref = fields[0]
        match = re.fullmatch(rb"refs/implementaudit/(controllers|current-generations|current-generation-migrations)/([a-z0-9][a-z0-9-]{0,47})", raw_ref)
        require(match is not None, "malformed controller discovery ref")
        kind, controller = (part.decode("ascii") for part in match.groups())
        location = call(run, ["git", "rev-parse", "--path-format=absolute", "--git-path", raw_ref.decode("ascii")])
        require(location.returncode == 0, "discovery ref custody is unknown")
        loose = Path(location.stdout.decode("utf-8").strip())
        try:
            _, fd = directory(loose.parent)
        except FileNotFoundError:
            pass  # Packed ref: physical parent is absent, not malformed.
        else:
            try:
                regular_at(fd, loose.name, optional=True)
            finally:
                close_directory(fd)
        result = call(run, ["git", "cat-file", "blob", raw_ref.decode("ascii")])
        require(result.returncode == 0 and not result.stderr, "discovery blob is unavailable")
        raw = result.stdout
        # Only exact native record identities are inspected; no schema upgrade.
        if kind == "controllers":
            require(raw.count(b"\n") == 1 and raw.endswith(b"\n"), "malformed controller discovery record")
            row = raw[:-1].decode("utf-8").split("\t")
            require(len(row) == 4 and row[:2] == ["implementaudit.controller-current.v1", controller],
                    "unknown controller discovery schema")
            bound_claim, bound_run = row[2], row[3]
            require((bound_run.startswith("/") or os.name == "nt" and re.match(r"[A-Za-z]:/", bound_run)) and not any(c in bound_run for c in "\r\0")
                    and all(part not in ("", ".", "..") for part in bound_run.split("/")[1:]),
                    "malformed discovered controller run path")
            run_identity = "/".join(bound_run.split("/")[-3:])
        elif kind == "current-generation-migrations":
            require(b"\n" not in raw and b"\r" not in raw, "malformed migration discovery record")
            row = raw.decode("utf-8").split("\t")
            require(len(row) == 10 and all(row) and row[:2] == ["implementaudit.current-generation-migration.v1", controller]
                    and row[9] == "true", "unknown migration discovery schema")
            bound_claim, run_identity = row[2], row[3]
        else:
            value = json.loads(raw)
            keys = {"schema", "controller", "claim_id", "run_root_identity", "projection_generation_id",
                    "continuity_epoch", "invalidation_oid", "predecessor_receipt_ref_oid", "expected_receipt_ref_schema",
                    "projection_schema", "state_sha256", "roadmap_sha256", "protected_manifest_sha256",
                    "archive_manifest_sha256", "exact_next_action"}
            require(type(value) is dict and set(value) == keys and value["schema"] == "implementaudit.current-generation.v1"
                    and value["controller"] == controller and raw == json.dumps(value, sort_keys=True,
                        separators=(",", ":"), ensure_ascii=False).encode(), "unknown current-pointer discovery schema")
            bound_claim, run_identity = value["claim_id"], value["run_root_identity"]
        # Validate native producer spelling before joining paths. Alias or
        # unavailable custody cannot prove that retained authority is elsewhere.
        require(type(run_identity) is str and re.fullmatch(
                r"\.IMPLEMENTAUDIT/runs/[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}", run_identity) is not None,
                "malformed discovered run identity")
        if kind != "controllers":
            bound_run = str(repo / run_identity)
        _, bound_fd = directory(bound_run)
        close_directory(bound_fd)
        require(re.fullmatch(r"[0-9a-f]{32}", bound_claim) is not None, "malformed discovered claim identity")
        if bound_claim == claim_id or Path(bound_run) == run:
            if kind == "controllers" and controller == legacy_controller:
                continue  # This exact controller already passed native controller binding.
            return True
    return False


def canonical_json(raw):
    def unique(rows):
        result = {}
        for key, value in rows:
            require(key not in result, "duplicate canonical JSON key")
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=unique)
    require(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode() == raw,
            "noncanonical native input JSON")
    return value


def read_path(path):
    path = Path(path)
    _, fd = directory(path.parent)
    try:
        return regular_at(fd, path.name)
    finally:
        close_directory(fd)


def native_guard_views(run, pair, resolution):
    """Preserve native source lines; derive only the joined live epoch frame.

    This does not decide whether an Andon, review, instruction or phase passes.
    Their existing owners consume these exact derivative inputs afterwards.
    """
    bodies, profiles = {}, {}
    for role in ("STATE", "ROADMAP"):
        raw = pair[role + ".md"]
        lines = raw.split(b"\n")
        require(len(lines) == 19 and lines[15] == b"```json" and lines[17:] == [b"```", b""],
                "unsupported canonical frame for native guards")
        body = canonical_json(lines[16])
        require(body["schema_version"] == "implementaudit.canonical-pair.v2" and body["role"] == role,
                "native guard body schema/role mismatch")
        group = body["payload"].get("native_guards")
        require(group is not None, "CANONICAL_NATIVE_GUARD_PROFILE_UNSUPPORTED: paired native source profile is required")
        require(type(group) is dict and set(group) == {"owner", "value"} and group["owner"] == role + ".md",
                "native guard owner mismatch")
        profile = group["value"]
        require(type(profile) is dict and set(profile) == {"schema_version", "lines"}
                and profile["schema_version"] == "implementaudit.native-guard-profile.v1",
                "unsupported native guard profile")
        rows = profile["lines"]
        require(type(rows) is list and bool(rows) and all(type(line) is str and not any(c in line for c in "\r\n\0") for line in rows),
                "native guard lines must preserve exact LF-free source lines")
        require(not any(re.match(r"^\s*Current epoch\s*:", line, re.I) for line in rows),
                "native guard profile cannot substitute the live epoch")
        bodies[role], profiles[role] = body, rows
    require(bodies["STATE"]["pair_id"] == bodies["ROADMAP"]["pair_id"], "native guard pair identity mismatch")
    state = bodies["STATE"]["payload"]
    continuation = state["continuation"]["value"]
    for field, value in (("Status", continuation["status"]), ("Next action", continuation["next_action"])):
        found = [line for line in profiles["STATE"] if re.match(r"^\|\s*" + field + r"\s*\|", line, re.I)]
        require(found == ["| " + field + " | " + value + " |"], "native " + field + " must equal the exact protected continuation")
    require(continuation["status"] in {"open", "READY_TO_DISPATCH", "IN_PHASE", "PAUSED", "BLOCKED", "INTERRUPTED", "DONE"},
            "native status cannot be normalized from a different vocabulary")
    effective = bodies["STATE"]["transition"] or bodies["STATE"]["continuity"]
    require(effective == (bodies["ROADMAP"]["transition"] or bodies["ROADMAP"]["continuity"]),
            "native guard effective continuity mismatch")
    pointer = resolution["pointer"]
    for key in ("continuity_epoch", "projection_generation_id", "invalidation_oid", "predecessor_receipt_ref_oid"):
        require(effective[key] == pointer[key], "native guard effective " + key + " differs from the native pointer")
    require(continuation["next_action"] == pointer["exact_next_action"], "native next action differs from the native pointer")
    rotation = (effective.get("schema_version") == "implementaudit.canonical-state-transition.v2"
                and effective.get("transition_kind") in {"rotation", "recovery"}
                and effective["boundary"] == "canonical-state-rotation")
    resume = (effective.get("schema_version") == "implementaudit.native-resume-transition.v1"
              and effective.get("transition_kind") == "native-resume"
              and effective["boundary"] in {"host-reported-compaction", "new-session", "handoff-resume", "manual-resume", "inferred-context-gap"}
              and all(effective.get(key) is None for key in ("failed_transition_epoch", "failed_projection_generation_id", "failed_transition_receipt_ref_oid")))
    require((rotation or resume) and effective["reconciled"] is True,
            "native guard live envelope is not an admitted owner-bound transition")
    for rows in profiles.values():
        require(not any(re.match(r"^\s*\|\s*" + re.escape(effective["continuity_epoch"]) + r"\s*\|", line) for line in rows),
                "native profile epoch row collides with the derived live epoch")
    identity = state["identity"]["value"]
    envelope = ["# Derivative native guard input", "", "Current epoch: " + effective["continuity_epoch"], "",
                "## Context epochs and instruction applicability", "",
                "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |",
                "|---|---|---|---|---|---|",
                "| " + effective["continuity_epoch"] + " | " + effective["boundary"] + " | not measured | `"
                + identity["candidate"] + "` / `" + identity["tree"] + "` | yes | native pointer JOIN |", "",
                "## Preserved native guard source", ""]
    views = {"native-" + role + ".md": ("\n".join((envelope if role == "STATE" else []) + profiles[role]) + "\n").encode()
             for role in ("STATE", "ROADMAP")}
    for role in ("STATE", "ROADMAP"):
        views["native-records/" + role + ".md"] = views["native-" + role + ".md"]
    # The unchanged #86 record parser scans all direct Markdown. Preserve that
    # exact population and its contained references, with source owner hashes.
    manifest_path = run / "state-generations" / pointer["projection_generation_id"] / "protected-state.json"
    require(str(manifest_path) == resolution["protected_manifest_path"], "protected manifest path changed")
    raw_manifest = read_path(manifest_path)
    require(hashlib.sha256(raw_manifest).hexdigest() == pointer["protected_manifest_sha256"]
            and raw_manifest.endswith(b"\n"), "native protected manifest bytes changed")
    manifest = canonical_json(raw_manifest[:-1])
    mapped = {row["source_id"]: row for row in manifest["PRESERVED_PAYLOAD"]["owner_map"] if row["source_kind"] == "ARTIFACT"}
    declared = set()
    for body in bodies.values():
        for ref in body["artifact_refs"]:
            if ref["role"] == "CONTINUITY_RECEIPT":
                continue
            locator = ref["locator"]
            require(type(locator) is str and not any(c in locator for c in "\\:\r\n\0")
                    and all(part not in ("", ".", "..") for part in locator.split("/"))
                    and locator not in {"STATE.md", "ROADMAP.md"} and not locator.startswith("state-generations/"),
                    "native record dependency has an unsafe or current-pair locator")
            require(locator not in declared, "native record dependencies alias one physical source")
            declared.add(locator)
            row = mapped[ref["artifact_id"]]
            require(row["owner"] == ref["owner"] and row["source_pointer"] == ""
                    and row["source_sha256"] == row["value_sha256"], "native record dependency owner changed")
            raw = read_path(run / locator)
            require(hashlib.sha256(raw).hexdigest() == row["source_sha256"], "native record dependency differs from its preserved owner bytes: " + locator)
            views["native-records/" + locator] = raw
    actual = {path.name for path in run.iterdir() if path.name.endswith(".md")}
    expected = {name for name in declared if "/" not in name and name.endswith(".md")} | {"STATE.md", "ROADMAP.md"}
    require(actual == expected, "native direct Markdown reader population is not completely owner-bound")
    return views


def snapshot_files(fd, prefix=""):
    if _WINDOWS is not None:
        result = {}
        for name in fd.names():
            try:
                child = _WINDOWS.Directory(fd.path / name)
            except NotADirectoryError:
                result[prefix + name] = regular_at(fd, name)
            else:
                with child:
                    result.update(snapshot_files(child, prefix + name + "/"))
        fd.verify()
        return result
    result = {}
    for name in os.listdir(fd):
        info = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            try:
                result.update(snapshot_files(child, prefix + name + "/"))
            finally:
                os.close(child)
        else:
            result[prefix + name] = regular_at(fd, name)
    return result


def write_snapshot(fd, files):
    if _WINDOWS is not None:
        for name, data in files.items():
            parts = name.split("/")
            for part in parts:
                _WINDOWS.component(part)
            with _WINDOWS.Directory(fd.path.joinpath(*parts[:-1]), create=True, create_root=fd.path) as parent:
                with _WINDOWS.File(parent, parts[-1], create=True, writable=True) as held:
                    held.write(data, 0o600)
            fd.verify()
        return
    for name, data in files.items():
        cursor = os.dup(fd)
        try:
            parts = name.split("/")
            for part in parts[:-1]:
                try:
                    os.mkdir(part, 0o700, dir_fd=cursor)
                except FileExistsError:
                    pass  # Reused parent must still pass no-follow directory open.
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=cursor)
                os.close(cursor)
                cursor = child
            opened = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=cursor)
            with os.fdopen(opened, "wb") as stream:
                stream.write(data)
        finally:
            os.close(cursor)


def materialize_pair(run_arg, output_arg, *, native_guards=False, verify_current=False):
    run, fd = directory(run_arg)
    try:
        hint = regular_at(fd, ".controller", optional=True)
        claim = regular_at(fd, ".claimed", optional=True)
    finally:
        close_directory(fd)
    ids = re.findall(rb"(?m)^claim_id=([0-9a-f]{32})$", claim or b"")
    if hint is None:
        claim_is_v2 = claim is not None and b"schema=implementaudit.run-claim.v2\n" in claim
        if claim_is_v2:
            require(len(ids) == 1, "v2 claim identity is missing or ambiguous")
        require(not controller_population_binds(run, ids[0].decode() if len(ids) == 1 else None,
                allow_non_git=not claim_is_v2), "controller-bound claim lost its discovery hint")
        return 3
    require(re.fullmatch(rb"controller_id=([a-z0-9][a-z0-9-]{0,47})\n", hint) is not None,
            "malformed controller discovery hint")
    require(claim is not None, "controller hint lacks claim custody")
    controller = hint.decode("ascii")[14:-1]
    require(len(ids) == 1, "v2 claim identity is missing or ambiguous")
    current = owner(run, "--current-controller", controller)
    require(current.returncode == 0 and current.stdout.endswith(b"\n") and current.stdout.count(b"\n") == 1,
            "native controller binding refused")
    row = current.stdout[:-1].decode("utf-8").split("\t")
    require(len(row) == 4 and row[0] == controller and Path(row[2]) == run and row[3] == ids[0].decode(),
            "native controller does not bind the requested run and claim")
    repo = Path(row[1])
    require(repo.is_absolute() and run.is_relative_to(repo), "native repository identity is not the requested custody")
    resolved = owner(repo, "--resolve-canonical-generation", controller)
    if resolved.returncode == 3:
        require(not controller_population_binds(run, ids[0].decode(), legacy_controller=controller),
                "retained canonical authority forbids legacy fallback")
        return 3
    require(resolved.returncode == 0, "native canonical generation JOIN refused; root fallback is forbidden")
    value = json.loads(resolved.stdout)
    keys = {"schema", "controller", "claim_id", "run_root_identity", "state_path", "roadmap_path",
            "protected_manifest_path", "archive_manifest_path", "pointer", "pointer_token", "receipt_token", "marker_oid"}
    require(type(value) is dict and set(value) == keys
            and value["schema"] == "implementaudit.canonical-generation-resolution.v1"
            and value["controller"] == controller and value["claim_id"] == row[3]
            and value["run_root_identity"] == run.relative_to(repo).as_posix(), "canonical resolution identity/schema mismatch")
    require(resolved.stdout == json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode() + b"\n",
            "canonical resolution is not exact unique-key JSON")
    pair = {}
    for role in ("STATE", "ROADMAP"):
        result = owner(repo, "--read-canonical-state", controller, "--role", role,
                       "--expected-pointer", value["pointer_token"])
        require(result.returncode == 0, "separate canonical " + role + " read refused")
        require(hashlib.sha256(result.stdout).hexdigest() == value["pointer"][role.lower() + "_sha256"],
                "canonical " + role + " bytes differ from the resolved pointer")
        pair[role + ".md"] = result.stdout
    if native_guards:
        pair.update(native_guard_views(run, pair, value))
    final = owner(repo, "--resolve-canonical-generation", controller)
    require(final.returncode == 0 and final.stdout == resolved.stdout, "canonical authority changed during pair read")
    # These are derivative validation snapshots, never files in a generation.
    output, fd = directory(output_arg)
    try:
        pair["resolution.json"] = resolved.stdout
        if verify_current:
            require(snapshot_files(fd) == pair, "validation snapshot or current native authority changed during consumption")
        else:
            require(not directory_names(fd), "validation snapshot directory must be empty")
            write_snapshot(fd, pair)
    finally:
        close_directory(fd)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--native-guards", action="store_true")
    parser.add_argument("--verify-current", action="store_true")
    args = parser.parse_args()
    try:
        return materialize_pair(args.run_root, args.output, native_guards=args.native_guards,
                                verify_current=args.verify_current)
    except (ReaderError, OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print("read-canonical-pair: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
