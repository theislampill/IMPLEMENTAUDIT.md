#!/usr/bin/env python3
"""Private implementation of claim-run's canonical-generation authority.

The public owner is claim-run.sh. This companion owns its ref, epoch, receipt,
and migration operations; the projection helper has no such authority. A private
module boundary is not authentication against arbitrary same-principal code.
"""
from __future__ import annotations

import argparse
import contextlib
import errno
import functools
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
import types

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
        raw = stream.read(33559)
        after = os.fstat(stream.fileno())
    if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
            or (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            or len(raw) != 33558
            or hashlib.sha256(raw).hexdigest() != "48a414e37a4eeeb950a1a7c34d2dba0ab0a602229371aff79ae270e9518fd8de"):
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
ZERO = "0" * 40
OID = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
CONTROLLER = re.compile(r"[a-z0-9][a-z0-9-]{0,47}\Z")
EPOCH = re.compile(r"G[0-9A-F]{4}\Z")
BOUNDARIES = {"host-reported-compaction", "new-session", "handoff-resume",
              "manual-resume", "inferred-context-gap"}
POINTER_SCHEMA = "implementaudit.current-generation.v1"
RECEIPT_SCHEMA = "implementaudit.continuity-receipt.v3"
MARKER_SCHEMA = "implementaudit.current-generation-migration.v1"
TRANSITION_SCHEMA = "implementaudit.rotation-transition.v1"
NATIVE_TRANSITION_SCHEMA = "implementaudit.native-resume-transition.v1"
POINTER_KEYS = {"schema", "controller", "claim_id", "run_root_identity",
                "projection_generation_id", "continuity_epoch", "invalidation_oid",
                "predecessor_receipt_ref_oid", "expected_receipt_ref_schema",
                "projection_schema", "state_sha256", "roadmap_sha256",
                "protected_manifest_sha256", "archive_manifest_sha256", "exact_next_action"}
MAX_BYTES = 64 * 1024 * 1024


class RotationError(RuntimeError):
    pass


class CustodyError(RotationError):
    """Writer/path identity uncertainty; do not start automatic compensation."""


class LegacyRoute(Exception):
    """Physical absence of both migration authorities, not a generic error."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def propose_c02_correction_v1(observed, decision, prior_decisions):
    """Pure existing-owner proposal, never producer, event or effect admission.

    Physical occurrence/census custody, issuer entitlement and applicability
    remain indispensable owner inputs. Hash equality cannot establish them.
    This interface changes no CLI, receipt schema, ref or F0-F9 ordering.
    """
    observation_keys = {'schema', 'controller', 'claim_id', 'run_root_identity', 'pointer_oid',
                        'receipt_oid', 'marker_oid', 'invalidation_oid', 'event_id', 'boundary', 'later_boundaries'}
    decision_keys = {'schema', 'issuer', 'grant_sha256', 'evidence_sha256', 'kind',
                     'observation_sha256', 'decision_id'}

    def validate(observation, proposal):
        if (type(observation) is not dict or set(observation) != observation_keys
                or observation['schema'] != 'implementaudit.c02-observation.v1'
                or type(proposal) is not dict or set(proposal) != decision_keys
                or proposal['schema'] != 'implementaudit.c02-decision-proposal.v1'
                or proposal['kind'] != 'ERRONEOUS_INVALIDATION'):
            raise RotationError('unknown or incomplete C02 observation/decision proposal')
        if (not isinstance(observation['controller'], str) or not CONTROLLER.fullmatch(observation['controller'])
                or not isinstance(observation['claim_id'], str) or not re.fullmatch(r'[0-9a-f]{32}', observation['claim_id'])
                or not isinstance(observation['run_root_identity'], str)
                or not re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}', observation['run_root_identity'])
                or observation['boundary'] not in BOUNDARIES
                or not isinstance(observation['event_id'], str) or not observation['event_id']
                or not isinstance(proposal['issuer'], str) or not proposal['issuer']):
            raise RotationError('C02 issuer, run, claim or event identity is incomplete')
        for key in ('pointer_oid', 'receipt_oid', 'marker_oid', 'invalidation_oid'):
            if not isinstance(observation[key], str) or not OID.fullmatch(observation[key]):
                raise RotationError('C02 requires a complete exact expected-old authority tuple')
        for key in ('grant_sha256', 'evidence_sha256', 'observation_sha256', 'decision_id'):
            if not isinstance(proposal[key], str) or not SHA256.fullmatch(proposal[key]):
                raise RotationError('C02 requires exact grant, evidence and observation identities')
        later = observation['later_boundaries']
        if type(later) is not list or len(later) > 4096:
            raise RotationError('C02 later-boundary census is missing or unbounded')
        events, oids = {observation['event_id']}, {observation['invalidation_oid']}
        for row in later:
            if (type(row) is not dict or set(row) != {'event_id', 'invalidation_oid', 'boundary'}
                    or not isinstance(row['event_id'], str) or not row['event_id']
                    or not isinstance(row['invalidation_oid'], str) or not OID.fullmatch(row['invalidation_oid'])
                    or row['event_id'] in events or row['invalidation_oid'] in oids
                    or row['boundary'] not in BOUNDARIES):
                raise RotationError('C02 later-boundary identity is ambiguous or malformed')
            events.add(row['event_id'])
            oids.add(row['invalidation_oid'])
        unsigned = {key: value for key, value in proposal.items() if key != 'decision_id'}
        if (proposal['observation_sha256'] != hashlib.sha256(canonical(observation)).hexdigest()
                or proposal['decision_id'] != hashlib.sha256(canonical(unsigned)).hexdigest()):
            raise RotationError('C02 proposal is not bound to its complete original observation')

    validate(observed, decision)
    if type(prior_decisions) is not list or len(prior_decisions) > 4096:
        raise RotationError('C02 prior-decision census is missing or unbounded')
    status = 'OWNER_ADMISSION_REQUIRED'
    for row in prior_decisions:
        if type(row) is not dict or set(row) != {'observation', 'decision'}:
            raise RotationError('C02 prior decision is malformed')
        validate(row['observation'], row['decision'])
        if row['observation']['invalidation_oid'] == observed['invalidation_oid']:
            if row != {'observation': observed, 'decision': decision}:
                raise RotationError('C02 replay or conflicting adjudication requires owner reconciliation')
            status = 'EXACT_RETRY_NO_EFFECT'
    if observed['later_boundaries']:
        status = 'SUPERSEDED_NEWER_BOUNDARY_NO_EFFECT'
    return {'status': status, 'decision_id': decision['decision_id'],
            'expected_old': {key: observed[key] for key in ('controller', 'claim_id', 'run_root_identity',
                             'pointer_oid', 'receipt_oid', 'marker_oid', 'invalidation_oid')},
            'retained_original': {'event_id': observed['event_id'], 'invalidation_oid': observed['invalidation_oid']},
            'authority_ceiling': 'NO_EFFECT_AUTHORITY'}


def decode_json(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise RotationError("duplicate JSON member")
            result[key] = value
        return result
    try:
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(RotationError("nonfinite JSON")))
    except (UnicodeError, ValueError) as exc:
        raise RotationError("invalid UTF-8 JSON") from exc
    if canonical(value) != raw:
        raise RotationError("noncanonical JSON bytes")
    return value


def fixed_git():
    choices = ((r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files\Git\bin\git.exe")
               if os.name == "nt" else ("/usr/bin/git", "/usr/local/bin/git"))
    for candidate in choices:
        try:
            info = os.lstat(candidate)
        except OSError:
            continue
        if stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode):
            return candidate
    raise RotationError("fixed platform Git is unavailable")


def git_environment():
    # Reused donor boundary: no inherited GIT_*, hooks, loader or shell overrides.
    if os.name == "nt":
        root = Path(fixed_git()).parents[1]
        search = [str(Path(sys.executable).parent), str(root / "cmd"),
                  str(root / "bin"), str(root / "usr/bin"), r"C:\Windows\System32"]
        result = {"SystemRoot": r"C:\Windows", "WINDIR": r"C:\Windows"}
    else:
        search = [str(Path(sys.executable).parent), "/usr/bin", "/bin", "/usr/local/bin"]
        result = {}
    result.update({"PATH": os.pathsep.join(search), "LC_ALL": "C", "LANG": "C",
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                   "GIT_TERMINAL_PROMPT": "0"})
    return result


def git_process(repo, *args, input_bytes=None):
    try:
        return subprocess.run([fixed_git(), "--no-replace-objects", "-C", str(repo), "-c", f"core.hooksPath={os.devnull}", *args],
                              input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=git_environment(), timeout=30, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise RotationError("Git operation has unknown effect") from exc


def git(repo, *args, input_bytes=None):
    result = git_process(repo, *args, input_bytes=input_bytes)
    if result.returncode:
        raise RotationError("Git operation failed: " + args[0])
    return result.stdout


def _scoped_git(function):
    @functools.wraps(function)
    def invoke(context, *args, **kwargs):
        with _CUSTODY.git_scope(context['repo'], fixed_git(), git_environment()):
            return function(context, *args, **kwargs)
    return invoke


def unsafe(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def safe_chain(path, *, allow_missing=False):
    path = Path(path)
    if _WINDOWS is not None:
        _WINDOWS.absolute_path(path)
        current = path
        while True:
            try:
                with _WINDOWS.Directory(current if current == path else current):
                    pass
                return
            except NotADirectoryError:
                with _WINDOWS.Directory(current.parent) as parent:
                    with _WINDOWS.File(parent, current.name):
                        pass
                return
            except FileNotFoundError:
                if not allow_missing or current == Path(current.anchor):
                    raise
                current = current.parent
    if not path.is_absolute() or any(part in (".", "..") for part in path.parts):
        raise RotationError("custody path is not canonical absolute")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            if allow_missing:
                return
            raise RotationError("custody path is missing")
        if unsafe(info):
            raise RotationError("symlink or reparse custody is forbidden")
        if current != path and not stat.S_ISDIR(info.st_mode):
            raise RotationError("custody ancestor is not a directory")


def snapshot(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_ctime_ns, info.st_mtime_ns)


class DirectoryPin:
    """Walk and retain every ancestor with native descriptor-relative no-follow I/O.

    A pathname census alone is insufficient: an ancestor can be replaced after
    lstat. Openat uses the already held parent object, so a redirected pathname
    cannot select an unrelated outside directory. Rechecks require the original
    directory objects still to occupy the canonical path before returning proof.
    """
    def __init__(self, path, *, create=False):
        self.path = Path(path)
        self.nodes = []
        self.closed = False
        self.native = None
        if _WINDOWS is not None:
            try:
                self.native = _WINDOWS.Directory(path, create=create, create_root=self.path.anchor)
            except OSError as exc:
                raise CustodyError(str(exc)) from exc
            return
        if (os.name != "posix" or not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW")
                or os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd
                or os.mkdir not in os.supports_dir_fd):
            raise CustodyError("native retained-directory capability is unsupported on this host")
        if not self.path.is_absolute() or any(part in (".", "..") for part in self.path.parts):
            raise CustodyError("retained directory path is not canonical absolute")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        try:
            fd = os.open(self.path.anchor, flags)
            self.nodes.append((None, self.path.anchor, fd, self.identity(os.fstat(fd))))
            for name in self.path.parts[1:]:
                parent = self.nodes[-1][2]
                self.verify()
                try:
                    fd = os.open(name, flags, dir_fd=parent)
                except FileNotFoundError:
                    if not create:
                        raise
                    try:
                        os.mkdir(name, mode=0o700, dir_fd=parent)
                    except FileExistsError:
                        pass
                    fd = os.open(name, flags, dir_fd=parent)
                info = os.fstat(fd)
                self.nodes.append((parent, name, fd, self.identity(info)))
                self.verify()
        except BaseException:
            self.close()
            raise

    @staticmethod
    def identity(info):
        if not stat.S_ISDIR(info.st_mode) or unsafe(info):
            raise CustodyError("retained ancestor is not a native directory")
        return (info.st_dev, info.st_ino, info.st_mode)

    @property
    def fd(self):
        if self.native is not None:
            return self.native
        return self.nodes[-1][2]

    def verify(self):
        if self.native is not None:
            try:
                return self.native.verify()
            except OSError as exc:
                raise CustodyError(str(exc)) from exc
        if self.closed:
            raise CustodyError("retained directory observation was already closed")
        for parent, name, fd, identity in self.nodes:
            current = os.stat(name, dir_fd=parent, follow_symlinks=False) if parent is not None else os.lstat(name)
            if self.identity(current) != identity or self.identity(os.fstat(fd)) != identity:
                raise CustodyError("canonical ancestor was replaced, renamed or redirected")

    def close(self):
        if self.native is not None:
            self.native.close()
            self.closed = True
            return
        for _, _, fd, _ in reversed(self.nodes):
            os.close(fd)
        self.nodes = []
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            if exc_type is None:
                self.verify()
        finally:
            self.close()


class PinnedFile:
    def __init__(self, path, *, max_bytes=MAX_BYTES):
        self.path = Path(path)
        self.directory = DirectoryPin(self.path.parent)
        self.fd = None
        self.native = None
        self.max_bytes = max_bytes
        try:
            if _WINDOWS is not None:
                try:
                    self.native = _WINDOWS.File(self.directory.native, self.path.name, maximum=max_bytes)
                except OSError as exc:
                    raise CustodyError(str(exc)) from exc
                return
            before = os.stat(self.path.name, dir_fd=self.directory.fd, follow_symlinks=False)
            if unsafe(before) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > max_bytes:
                raise CustodyError("input is not a bounded single-link regular file")
            flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0)
            self.fd = os.open(self.path.name, flags, dir_fd=self.directory.fd)
            self.identity = snapshot(before)
            self.verify()
        except BaseException:
            self.close()
            raise

    def verify(self):
        if self.native is not None:
            try:
                return self.native.verify()
            except OSError as exc:
                raise CustodyError(str(exc)) from exc
        self.directory.verify()
        current = os.stat(self.path.name, dir_fd=self.directory.fd, follow_symlinks=False)
        if snapshot(current) != self.identity or snapshot(os.fstat(self.fd)) != self.identity:
            raise CustodyError("retained file identity, mode, link count or change time drifted")

    def read(self):
        if self.native is not None:
            try:
                return self.native.read()
            except OSError as exc:
                raise CustodyError(str(exc)) from exc
        self.verify()
        os.lseek(self.fd, 0, os.SEEK_SET)
        chunks = []
        size = 0
        while True:
            chunk = os.read(self.fd, min(1024 * 1024, self.max_bytes + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            if size > self.max_bytes:
                raise CustodyError("retained input exceeded its bounded read")
        self.verify()
        if size != os.fstat(self.fd).st_size:
            raise CustodyError("retained input size changed during read")
        return b"".join(chunks)

    def close(self):
        if self.native is not None:
            self.native.close()
            self.native = None
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        self.directory.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            if exc_type is None:
                self.verify()
        finally:
            self.close()


def read_regular(path, *, max_bytes=MAX_BYTES):
    with PinnedFile(path, max_bytes=max_bytes) as pinned:
        return pinned.read()


def ref_path(repo, ref):
    if not re.fullmatch(r"refs/implementaudit/[A-Za-z0-9._/-]+", ref) or ".." in ref or "//" in ref:
        raise RotationError("ref is outside exact authority namespace")
    raw = git(repo, "rev-parse", "--path-format=absolute", "--git-path", ref).decode().strip()
    path = Path(raw)
    safe_chain(path, allow_missing=True)
    return path


def read_ref(repo, ref):
    try:
        observed = _CUSTODY.current_ref(repo, ref)
    except OSError as exc:
        raise CustodyError(str(exc)) from exc
    if observed is not NotImplemented:
        return observed
    path = ref_path(repo, ref)
    loose = read_regular(path, max_bytes=4096) if os.path.lexists(path) else None
    common = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip())
    safe_chain(common)
    packed = common / "packed-refs"
    packed_bytes = read_regular(packed) if os.path.lexists(packed) else None
    symbolic = git_process(repo, "symbolic-ref", "-q", ref)
    if symbolic.returncode == 0:
        raise RotationError("symbolic authority ref is forbidden")
    result = git_process(repo, "show-ref", "--verify", "--hash", ref)
    if result.returncode == 0:
        try:
            oid = result.stdout.decode("ascii").strip()
        except UnicodeError as exc:
            raise RotationError("authority ref is malformed") from exc
        if not OID.fullmatch(oid):
            raise RotationError("authority ref is malformed")
        if loose is not None and loose != (oid + "\n").encode():
            raise RotationError("loose authority ref is not one exact object ID line")
        return oid
    if os.path.lexists(path):
        raise RotationError("authority ref is physically present but broken")
    if packed_bytes is not None:
        for line in packed_bytes.splitlines():
            if not line.startswith((b"#", b"^")) and line.split(b" ", 1)[-1] == ref.encode():
                raise RotationError("packed authority ref is broken")
    return None


def read_blob(repo, oid):
    if not isinstance(oid, str) or not OID.fullmatch(oid):
        raise RotationError("blob identity is invalid")
    try:
        observed = _CUSTODY.read_object(repo, oid, MAX_BYTES)
    except OSError as exc:
        raise RotationError(str(exc)) from exc
    if observed is not NotImplemented:
        return observed
    if git(repo, "cat-file", "-t", oid) != b"blob\n":
        raise RotationError("authority object is not a blob")
    size = int(git(repo, "cat-file", "-s", oid))
    if size > MAX_BYTES:
        raise RotationError("authority object exceeds bounded read")
    raw = git(repo, "cat-file", "blob", oid)
    if hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != oid:
        raise RotationError("authority blob identity changed")
    return raw


def owner_call(repo, *args):
    shell = r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt" else "/bin/bash"
    result = subprocess.run([shell, str(Path(__file__).with_name("claim-run.sh")), *args],
                            cwd=repo, env=git_environment(), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=30, check=False)
    if result.returncode:
        raise RotationError("claim-run predecessor/custody verification refused")
    return result.stdout


def discover(controller):
    if not CONTROLLER.fullmatch(controller):
        raise RotationError("controller identity is invalid")
    repo = Path(git(Path.cwd(), "rev-parse", "--path-format=absolute", "--show-toplevel").decode().strip())
    safe_chain(repo)
    if git(repo, "rev-parse", "--show-object-format") != b"sha1\n":
        raise RotationError("this pointer schema requires a SHA-1 Git object store")
    storage = git_process(repo, "config", "--get", "extensions.refStorage")
    if storage.returncode not in (0, 1) or (storage.returncode == 0 and storage.stdout.strip() not in (b"", b"files")):
        raise RotationError("this authority reader requires the qualified files ref backend")
    raw = owner_call(repo, "--current-controller", controller)
    fields = raw.decode("utf-8", "strict").rstrip("\n").split("\t")
    if len(fields) != 4 or fields[0] != controller or Path(fields[1]) != repo:
        raise RotationError("claim-run custody did not resolve one exact worktree")
    root = Path(fields[2])
    safe_chain(root)
    rel = root.relative_to(repo).as_posix()
    if not re.fullmatch(r"\.IMPLEMENTAUDIT/runs/[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}", rel):
        raise RotationError("run custody is not a strict claimed root")
    cref = f"refs/implementaudit/controllers/{controller}"
    coid = read_ref(repo, cref)
    expected = f"implementaudit.controller-current.v1\t{controller}\t{fields[3]}\t{fields[2]}\n".encode()
    if coid is None or read_blob(repo, coid) != expected:
        raise RotationError("controller ref does not bind the claimed root")
    return {"repo": repo, "run_root": root, "controller": controller,
            "claim_id": fields[3], "run_root_identity": rel, "controller_ref": cref,
            "controller_oid": coid, "custody_output": raw,
            "pointer_ref": f"refs/implementaudit/current-generations/{controller}",
            "marker_ref": f"refs/implementaudit/current-generation-migrations/{controller}",
            "invalidation_ref": f"refs/implementaudit/continuity-invalidations/{controller}"}


def authorities(context):
    return {name: read_ref(context["repo"], context[name + "_ref"])
            for name in ("controller", "pointer", "marker", "invalidation")}


def managed(context):
    observed = authorities(context)
    if observed["controller"] != context["controller_oid"]:
        raise RotationError("controller custody changed")
    if observed["pointer"] is None and observed["marker"] is None:
        raise LegacyRoute()
    return observed


def projection_helper():
    """Load the physical sibling's pure I/O boundaries, never a caller module."""
    path = Path(__file__).with_name("rotate-canonical-state.py").absolute()
    raw = read_regular(path)
    name = "_claim_owned_rotation_projection_" + hashlib.sha256(raw).hexdigest()
    if name not in sys.modules:
        module = types.ModuleType(name)
        module.__file__ = str(path)
        module.__package__ = ""
        sys.modules[name] = module
        try:
            exec(compile(raw, str(path), "exec"), module.__dict__)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    module = sys.modules[name]
    for name in ("prepare_canonical_draft", "prepare_native_resume_draft",
                 "finalize_canonical_projection", "read_canonical_generation",
                 "verify_canonical_archive", "archive_retention_guards"):
        if not callable(getattr(module, name, None)):
            raise RotationError("projection helper interface is incomplete")
    return module


def epoch_number(value):
    if not isinstance(value, str) or not EPOCH.fullmatch(value) or value == "G0000":
        raise RotationError("epoch is not canonical G0001 through GFFFF")
    return int(value[1:], 16)


def next_epoch(value):
    number = epoch_number(value) + 1
    if number > 65535:
        raise RotationError("epoch namespace is exhausted")
    return f"G{number:04X}"


def canonical_epoch(value):
    if isinstance(value, str) and re.fullmatch(r"e[1-9][0-9]{0,4}", value):
        number = int(value[1:])
        if number <= 65535:
            return f"G{number:04X}"
    epoch_number(value)
    return value


def field(value, label):
    if not isinstance(value, str) or not value or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise RotationError(label + " is not an exact nonempty wire field")
    return value


def tsv(raw, count, *, terminal_lf=True):
    if not isinstance(raw, bytes):
        raise RotationError("wire object is not bytes")
    if terminal_lf:
        if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
            raise RotationError("wire object requires exactly one terminal LF")
        raw = raw[:-1]
    text = raw.decode("utf-8", "strict")
    fields = text.split("\t")
    if len(fields) != count:
        raise RotationError("wire object field count mismatch")
    return [field(item, "wire member") for item in fields]


def receipt_ref(context, epoch):
    epoch_number(epoch)
    return f"refs/implementaudit/continuity-receipts/{context['controller']}/{epoch}"


def split_receipt_token(context, token):
    field(token, "receipt token")
    if token.count("@") != 1:
        raise RotationError("receipt token is not exact ref@oid")
    ref, oid = token.split("@")
    if not OID.fullmatch(oid) or ref != receipt_ref(context, ref.rsplit("/", 1)[-1]):
        raise RotationError("receipt token is outside controller epoch custody")
    return ref, oid


def read_receipt(context, token):
    ref, oid = split_receipt_token(context, token)
    if read_ref(context["repo"], ref) != oid:
        raise RotationError("receipt ref no longer names its exact retained object")
    raw = read_blob(context["repo"], oid)
    schema = raw.split(b"\t", 1)[0]
    if schema == b"implementaudit.continuity-receipt.v2":
        row = tsv(raw, 12)
        names = ("schema", "controller", "controller_oid", "claim_id", "head", "tree",
                 "state_sha256", "roadmap_sha256", "invalidation_oid", "boundary",
                 "continuity_epoch", "exact_next_action")
    elif schema == RECEIPT_SCHEMA.encode():
        row = tsv(raw, 14)
        names = ("schema", "controller", "claim_id", "run_root_identity", "continuity_epoch",
                 "invalidation_oid", "pointer_ref", "pointer_oid", "state_sha256", "roadmap_sha256",
                 "protected_manifest_sha256", "archive_manifest_sha256", "exact_next_action",
                 "predecessor_receipt_ref_oid")
    else:
        raise RotationError("rotation requires a source-owned v2 or original v3 receipt")
    record = dict(zip(names, row))
    if (record["controller"] != context["controller"] or record["claim_id"] != context["claim_id"]
            or ref != receipt_ref(context, record["continuity_epoch"])):
        raise RotationError("receipt identity does not bind this claim and epoch")
    for key in ("state_sha256", "roadmap_sha256"):
        if not SHA256.fullmatch(record[key]):
            raise RotationError("receipt pair digest is malformed")
    if record["schema"] == RECEIPT_SCHEMA:
        for key in ("protected_manifest_sha256", "archive_manifest_sha256"):
            if not SHA256.fullmatch(record[key]):
                raise RotationError("receipt manifest digest is malformed")
        if (record["run_root_identity"] != context["run_root_identity"]
                or record["pointer_ref"] != context["pointer_ref"]
                or not OID.fullmatch(record["pointer_oid"])
                or not OID.fullmatch(record["invalidation_oid"])):
            raise RotationError("receipt pointer custody is malformed")
        split_receipt_token(context, record["predecessor_receipt_ref_oid"])
    elif (record["controller_oid"] != context["controller_oid"]
          or record["boundary"] not in BOUNDARIES
          or any(not OID.fullmatch(record[key]) for key in ("head", "tree"))
          or (record["invalidation_oid"] != "none" and not OID.fullmatch(record["invalidation_oid"]))):
        raise RotationError("v2 predecessor binding is malformed or transferred")
    return record


def validate_pointer(context, value):
    if type(value) is not dict or set(value) != POINTER_KEYS or value["schema"] != POINTER_SCHEMA:
        raise RotationError("pointer is not the exact original current-generation schema")
    for key in ("controller", "claim_id", "run_root_identity"):
        if value[key] != context[key]:
            raise RotationError("pointer identity does not bind this owner")
    epoch_number(value["projection_generation_id"])
    epoch_number(value["continuity_epoch"])
    if (not isinstance(value["invalidation_oid"], str) or not OID.fullmatch(value["invalidation_oid"])
            or value["projection_schema"] != "implementaudit.protected-projection.v2"
            or value["expected_receipt_ref_schema"] != {
                "ref": receipt_ref(context, value["continuity_epoch"]), "schema": RECEIPT_SCHEMA}):
        raise RotationError("pointer transition envelope is malformed")
    split_receipt_token(context, value["predecessor_receipt_ref_oid"])
    for key in ("state_sha256", "roadmap_sha256", "protected_manifest_sha256", "archive_manifest_sha256"):
        if not isinstance(value[key], str) or not SHA256.fullmatch(value[key]):
            raise RotationError("pointer manifest or pair hash is malformed")
    field(value["exact_next_action"], "exact next action")
    return value


def invalidation_record(context, oid):
    if oid is None:
        return None
    row = tsv(read_blob(context["repo"], oid), 6)
    if row[:4] != ["implementaudit.continuity-invalidation.v1", context["controller"],
                   context["controller_oid"], context["claim_id"]]:
        raise RotationError("invalidation is outside the current claim")
    if row[4] not in BOUNDARIES | {"canonical-state-rotation"}:
        raise RotationError("invalidation boundary is unsupported")
    return {"boundary": row[4], "event": row[5], "oid": oid}


def epoch_ref(context, epoch):
    epoch_number(epoch)
    return f"refs/implementaudit/state-archives/{context['controller']}/epochs/{epoch}"


def anchor_ref(context, oid):
    if not isinstance(oid, str) or not OID.fullmatch(oid):
        raise RotationError("retention object identity is malformed")
    return f"refs/implementaudit/state-archives/{context['controller']}/objects/{oid}"


def require_anchor(context, oid):
    if read_ref(context["repo"], anchor_ref(context, oid)) != oid:
        raise RotationError("historical object lacks its exact retained anchor")
    read_blob(context["repo"], oid)


def epoch_material(record):
    material = dict(record)
    material["transition"] = dict(record["transition"], invalidation_oid=None)
    return material


def validate_epoch(context, record, expected_epoch):
    keys = {"schema", "transition", "prepared", "controller_oid", "expected_pointer_oid",
            "expected_marker_oid", "failed_epoch_oid", "failed_pointer_oid"}
    if (type(record) is not dict or set(record) != keys
            or record["schema"] not in {"implementaudit.rotation-epoch.v1", "implementaudit.native-resume-epoch.v1"}):
        raise RotationError("allocated epoch descriptor is malformed")
    native = record["schema"] == "implementaudit.native-resume-epoch.v1"
    transition = record["transition"]
    keys = {"schema", "controller", "claim_id", "run_root_identity", "projection_generation_id",
            "continuity_epoch", "boundary", "invalidation_oid", "predecessor_receipt_ref_oid",
            "expected_receipt_ref_schema", "transition_kind", "payload_source",
            "failed_transition_epoch", "failed_transition_generation", "failed_transition_receipt_ref_oid", "head", "tree"}
    if (type(transition) is not dict or set(transition) != keys
            or transition["schema"] != (NATIVE_TRANSITION_SCHEMA if native else TRANSITION_SCHEMA)):
        raise RotationError("owner transition is malformed")
    for key in ("controller", "claim_id", "run_root_identity"):
        if transition[key] != context[key]:
            raise RotationError("epoch descriptor owner changed")
    if (record["controller_oid"] != context["controller_oid"]
            or transition["continuity_epoch"] != expected_epoch
            or transition["boundary"] not in (BOUNDARIES if native else {"canonical-state-rotation"})
            or transition["expected_receipt_ref_schema"] != {
                "ref": receipt_ref(context, expected_epoch), "schema": RECEIPT_SCHEMA}
            or any(not isinstance(transition[key], str) or not OID.fullmatch(transition[key])
                   for key in ("head", "tree", "invalidation_oid"))):
        raise RotationError("epoch descriptor transition binding changed")
    prepared = record["prepared"]
    predecessor = prepared["predecessor"]
    source_epoch = predecessor["continuity_epoch"]
    source_generation = predecessor.get("projection_generation_id", source_epoch)
    failed_epoch, failed_generation = next_epoch(source_epoch), next_epoch(source_generation)
    if native and transition["transition_kind"] == "native-resume":
        expected = (failed_epoch, failed_generation, "preimage", None, None, None, None)
        if (prepared.get("schema") != "implementaudit.native-resume-prepared.v1"
                or predecessor["receipt_schema"] != RECEIPT_SCHEMA
                or record["expected_pointer_oid"] is None or record["expected_marker_oid"] is None
                or record["expected_pointer_oid"] != predecessor["pointer_oid"]
                or record["expected_marker_oid"] != predecessor["migration_marker_oid"]):
            raise RotationError("native resume lacks its exact migrated source and permanent marker")
    elif not native and transition["transition_kind"] == "rotation":
        expected = (failed_epoch, failed_generation, "draft", None, None, None, None)
    elif not native and transition["transition_kind"] == "recovery":
        expected = (next_epoch(failed_epoch), next_epoch(failed_generation), "preimage",
                    failed_epoch, failed_generation, record["failed_epoch_oid"], record["failed_pointer_oid"])
        if not isinstance(record["failed_epoch_oid"], str) or not OID.fullmatch(record["failed_epoch_oid"]):
            raise RotationError("recovery lacks the retained failed allocation")
        failed, failed_oid = read_epoch(context, failed_epoch, require_rotation=True)
        if (failed_oid != record["failed_epoch_oid"] or failed["transition"]["transition_kind"] != "rotation"
                or failed["prepared"] != prepared):
            raise RotationError("recovery replaced the exact failed allocation or archived preimage")
    else:
        raise RotationError("epoch transition kind is unsupported")
    actual = (transition["continuity_epoch"], transition["projection_generation_id"],
              transition["payload_source"], transition["failed_transition_epoch"],
              transition["failed_transition_generation"], record["failed_epoch_oid"], record["failed_pointer_oid"])
    source_receipt = predecessor["receipt_ref"] + "@" + predecessor["receipt_oid"]
    failed_receipt = transition["failed_transition_receipt_ref_oid"]
    if failed_receipt is not None:
        failed_ref, failed_receipt_oid = split_receipt_token(context, failed_receipt)
        if transition["transition_kind"] != "recovery" or failed_ref != receipt_ref(context, failed_epoch):
            raise RotationError("failed receipt does not bind the one failed allocation")
        failed_pointer = validate_pointer(context, decode_json(read_blob(context["repo"], record["failed_pointer_oid"])))
        receipt_matches_pointer(context, read_receipt(context, failed_receipt), failed_pointer, record["failed_pointer_oid"])
        if (failed_pointer["continuity_epoch"] != failed_epoch
                or failed_pointer["projection_generation_id"] != failed_generation
                or failed_pointer["invalidation_oid"] != failed["transition"]["invalidation_oid"]
                or failed_pointer["predecessor_receipt_ref_oid"] != source_receipt):
            raise RotationError("failed receipt predecessor or generation was substituted")
    if (actual != expected or prepared["generation_id"] != failed_generation
            or transition["predecessor_receipt_ref_oid"] != (failed_receipt or source_receipt)):
        raise RotationError("epoch did not follow the exact source and failure algebra")
    invalidation = invalidation_record(context, transition["invalidation_oid"])
    if native:
        old_pointer = validate_pointer(context, decode_json(read_blob(context["repo"], record["expected_pointer_oid"])))
        receipt_matches_pointer(context, read_receipt(context, source_receipt), old_pointer, record["expected_pointer_oid"])
        if (invalidation is None or invalidation["boundary"] != transition["boundary"]
                or transition["invalidation_oid"] == old_pointer["invalidation_oid"]
                or old_pointer["continuity_epoch"] != source_epoch
                or old_pointer["projection_generation_id"] != source_generation
                or old_pointer["invalidation_oid"] != predecessor["invalidation_oid"]):
            raise RotationError("native resume does not bind its distinct retained native occurrence and prior pointer")
    else:
        event = "canonical-state-rotation/" + expected_epoch + "/" + hashlib.sha256(canonical(epoch_material(record))).hexdigest()
        if invalidation != {"boundary": "canonical-state-rotation", "event": event, "oid": transition["invalidation_oid"]}:
            raise RotationError("epoch does not bind the real allocated invalidation")
    for key in ("expected_pointer_oid", "expected_marker_oid", "failed_pointer_oid"):
        if record[key] is not None and (not isinstance(record[key], str) or not OID.fullmatch(record[key])):
            raise RotationError("epoch prior authority identity is malformed")
    return record


def read_epoch(context, epoch, *, require_rotation=False):
    oid = read_ref(context["repo"], epoch_ref(context, epoch))
    if oid is None:
        raise RotationError("current generation has no retained owner allocation")
    require_anchor(context, oid)
    record = decode_json(read_blob(context["repo"], oid))
    if require_rotation and (type(record) is not dict or type(record.get("transition")) is not dict
                             or record["transition"].get("transition_kind") != "rotation"):
        raise RotationError("the declared failed allocation must be one original rotation")
    return validate_epoch(context, record, epoch), oid


def publication_ref(context, epoch):
    return epoch_ref(context, epoch) + "-publication"


def read_publication(context, record, epoch_oid, *, absent=False):
    transition = record["transition"]
    ref = publication_ref(context, transition["continuity_epoch"])
    oid = read_ref(context["repo"], ref)
    if oid is None:
        if absent:
            return None, None
        raise RotationError("generation has no exact retained publication intent")
    require_anchor(context, oid)
    intent = decode_json(read_blob(context["repo"], oid))
    expected = {"schema": "implementaudit.rotation-publication.v1", "controller": context["controller"],
                "claim_id": context["claim_id"], "run_root_identity": context["run_root_identity"],
                "continuity_epoch": transition["continuity_epoch"], "epoch_oid": epoch_oid,
                "pointer_ref": context["pointer_ref"], "expected_pointer_oid": record["expected_pointer_oid"]}
    if type(intent) is not dict or set(intent) != set(expected) | {"pointer_oid"}:
        raise RotationError("publication intent schema is malformed")
    if any(intent[key] != value for key, value in expected.items()):
        raise RotationError("publication intent changed its epoch, owner or expected-old")
    pointer = validate_pointer(context, decode_json(read_blob(context["repo"], intent["pointer_oid"])))
    for key in ("continuity_epoch", "projection_generation_id", "invalidation_oid", "predecessor_receipt_ref_oid"):
        if pointer[key] != transition[key]:
            raise RotationError("publication intent substituted its allocated successor")
    require_anchor(context, intent["pointer_oid"])
    return intent, oid


def verify_generation(context, pointer):
    validate_pointer(context, pointer)
    result = projection_helper().read_canonical_generation(context["repo"], context["run_root"], pointer)
    generation = context["run_root"] / "state-generations" / pointer["projection_generation_id"]
    safe_chain(generation)
    for role in ("state", "roadmap"):
        path = Path(result[role + "_path"])
        if path != generation / (role.upper() + ".md"):
            raise RotationError("helper returned a component outside immutable generation custody")
        raw = read_regular(path)
        if raw != result[role + "_bytes"] or hashlib.sha256(raw).hexdigest() != pointer[role + "_sha256"]:
            raise RotationError("canonical component readback mismatch")
    for name, key, manifest in (("protected-state.json", "protected_manifest_sha256", "protected_manifest"),
                                ("archive-manifest.json", "archive_manifest_sha256", "archive_manifest")):
        raw = read_regular(generation / name)
        if (not raw.endswith(b"\n") or hashlib.sha256(raw).hexdigest() != pointer[key]
                or decode_json(raw[:-1]) != result[manifest]):
            raise RotationError("canonical manifest readback mismatch")
    return result


def receipt_matches_pointer(context, receipt, pointer, pointer_oid):
    expected = {"schema": RECEIPT_SCHEMA, "pointer_ref": context["pointer_ref"], "pointer_oid": pointer_oid}
    expected.update({key: pointer[key] for key in ("controller", "claim_id", "run_root_identity", "continuity_epoch",
                     "invalidation_oid", "state_sha256", "roadmap_sha256", "protected_manifest_sha256",
                     "archive_manifest_sha256", "exact_next_action", "predecessor_receipt_ref_oid")})
    if receipt != expected:
        raise RotationError("v3 receipt does not join the exact pointer and pair")


def verify_marker(context, marker_oid, current_pointer):
    row = tsv(read_blob(context["repo"], marker_oid), 10, terminal_lf=False)
    if (row[:4] != [MARKER_SCHEMA, context["controller"], context["claim_id"], context["run_root_identity"]]
            or row[5:7] != [context["pointer_ref"], POINTER_SCHEMA] or row[9] != "true"
            or row[7] != receipt_ref(context, row[4]) or not OID.fullmatch(row[8])):
        raise RotationError("permanent first-migration marker is malformed")
    receipt = read_receipt(context, row[7] + "@" + row[8])
    if receipt["schema"] != RECEIPT_SCHEMA:
        raise RotationError("migration marker is not bound to an original v3 receipt")
    pointer = validate_pointer(context, decode_json(read_blob(context["repo"], receipt["pointer_oid"])))
    receipt_matches_pointer(context, receipt, pointer, receipt["pointer_oid"])
    if pointer["continuity_epoch"] != row[4] or epoch_number(row[4]) > epoch_number(current_pointer["continuity_epoch"]):
        raise RotationError("migration marker is ahead of current generation")
    for oid in (marker_oid, row[8], receipt["pointer_oid"], pointer["invalidation_oid"]):
        require_anchor(context, oid)
    genesis, _ = read_epoch(context, pointer["continuity_epoch"])
    if genesis["expected_marker_oid"] is not None:
        raise RotationError("permanent marker does not name a first migration")
    return row


def _read_generation_evidence_v1(context, observed):
    """Exact immutable receipt/pointer history; this private read grants no currentness."""
    if observed["pointer"] is None:
        raise RotationError("STOP_NO_ROOT_FALLBACK: marker without current pointer")
    if observed["marker"] is None:
        raise RotationError("FIRST_MIGRATION_INCOMPLETE: no ordinary currentness before marker")
    pointer = validate_pointer(context, decode_json(read_blob(context["repo"], observed["pointer"])))
    record, epoch_oid = read_epoch(context, pointer["continuity_epoch"])
    intent, intent_oid = read_publication(context, record, epoch_oid)
    if intent["pointer_oid"] != observed["pointer"]:
        raise RotationError("current pointer is not the exact retained publication intent")
    transition = record["transition"]
    for key in ("controller", "claim_id", "run_root_identity", "projection_generation_id", "continuity_epoch",
                "invalidation_oid", "predecessor_receipt_ref_oid", "expected_receipt_ref_schema"):
        if pointer[key] != transition[key]:
            raise RotationError("pointer is not the allocated owner transition")
    if (git(context["repo"], "rev-parse", "HEAD").decode().strip() != transition["head"]
            or git(context["repo"], "rev-parse", "HEAD^{tree}").decode().strip() != transition["tree"]):
        raise RotationError("candidate HEAD or tree changed after continuity admission")
    pred = read_receipt(context, pointer["predecessor_receipt_ref_oid"])
    expected_predecessor_epoch = (transition["failed_transition_epoch"] if transition["failed_transition_receipt_ref_oid"]
                                  else record["prepared"]["predecessor"]["continuity_epoch"])
    if pred["continuity_epoch"] != expected_predecessor_epoch:
        raise RotationError("source receipt is not the archived predecessor")
    prepared = record["prepared"]
    if (pointer["archive_manifest_sha256"] != prepared["archive_manifest_sha256"]
            or pointer["exact_next_action"] != prepared["exact_next_action"]
            or read_ref(context["repo"], prepared["archive_ref"]) != prepared["archive_manifest_oid"]):
        raise RotationError("pointer is not bound to its original retained archive")
    history_guards = archive_retention_guards(context, prepared)
    pair = verify_generation(context, pointer)
    ref = pointer["expected_receipt_ref_schema"]["ref"]
    oid = read_ref(context["repo"], ref)
    if oid is None:
        raise RotationError("current generation has no terminal v3 receipt")
    receipt_matches_pointer(context, read_receipt(context, ref + "@" + oid), pointer, observed["pointer"])
    marker = verify_marker(context, observed["marker"], pointer)
    if record["expected_marker_oid"] is not None and record["expected_marker_oid"] != observed["marker"]:
        raise RotationError("permanent migration marker was replaced")
    if record["expected_marker_oid"] is None and marker[4] != pointer["continuity_epoch"]:
        raise RotationError("first terminal JOIN marker must name this terminal receipt")
    for retained in (observed["pointer"], observed["marker"], observed["invalidation"], pointer["invalidation_oid"],
                     oid, epoch_oid, prepared["predecessor"]["receipt_oid"]):
        require_anchor(context, retained)
    verify_custody(context)
    if (authorities(context) != observed or read_ref(context["repo"], ref) != oid
            or any(read_ref(context["repo"], item) != expected for item, expected in history_guards.items())):
        raise RotationError("currentness authorities changed during readback")
    return dict(pair, pointer=pointer, pointer_oid=observed["pointer"], marker_oid=observed["marker"],
                receipt_token=ref + "@" + oid, epoch_oid=epoch_oid)


@_scoped_git
def require_current_generation_join_v1(context):
    observed = managed(context)
    if observed["pointer"] is not None:
        pointer = validate_pointer(context, decode_json(read_blob(context["repo"], observed["pointer"])))
        if pointer["invalidation_oid"] != observed["invalidation"]:
            raise RotationError("current generation is stale after a newer boundary")
    return _read_generation_evidence_v1(context, observed)


def _mkdir_safe(path):
    with DirectoryPin(path, create=True):
        pass


@contextlib.contextmanager
def native_lock(path, *, blocking):
    """A checked process-owned one-byte gate; process death releases the lease."""
    if _WINDOWS is not None:
        with _WINDOWS.lock(path, blocking=blocking):
            yield
        return
    path = Path(path)
    with DirectoryPin(path.parent, create=True) as directory:
        flags = os.O_RDWR | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
        created = False
        before = None
        try:
            fd = os.open(path.name, flags | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory.fd)
            created = True
        except FileExistsError:
            before = os.stat(path.name, dir_fd=directory.fd, follow_symlinks=False)
            if (unsafe(before) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size != 1):
                raise CustodyError("coordination gate is not a single-link one-byte regular file")
            fd = os.open(path.name, flags, dir_fd=directory.fd)
        locked = False
        try:
            opened = os.fstat(fd)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1 or unsafe(opened):
                raise CustodyError("coordination gate opened an unsafe object")
            if before is not None and snapshot(before) != snapshot(opened):
                raise CustodyError("coordination gate changed while opening")
            directory.verify()
            if created:
                if opened.st_size != 0 or os.write(fd, b"\0") != 1:
                    raise CustodyError("coordination gate creation was incomplete")
                os.fsync(fd)
                opened = os.fstat(fd)
            os.lseek(fd, 0, os.SEEK_SET)
            if os.read(fd, 2) != b"\0":
                raise CustodyError("coordination gate has an unsupported format")
            identity = snapshot(opened)
            def verify():
                directory.verify()
                current = os.stat(path.name, dir_fd=directory.fd, follow_symlinks=False)
                if snapshot(current) != identity or snapshot(os.fstat(fd)) != identity:
                    raise CustodyError("coordination gate was replaced or changed")
            verify()
            import fcntl
            deadline = time.monotonic() + (30 if blocking else 0)
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    locked = True
                    break
                except OSError as exc:
                    if exc.errno not in {errno.EAGAIN, errno.EACCES, errno.EDEADLK}:
                        raise
                    if not blocking or time.monotonic() >= deadline:
                        raise RotationError("another owner holds the rotation or namespace lease") from exc
                    time.sleep(0.02)
            verify()
            yield
            verify()
        finally:
            if locked:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


def rotation_lease(context):
    common = Path(git(context["repo"], "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip())
    safe_chain(common)
    # This shared Git-common lease serializes rotations across linked worktrees.
    # Native boundaries take only namespace.gate and therefore can preempt it.
    return native_lock(common / "implementaudit-r0039-rotation.gate", blocking=False)


def namespace_gate(context):
    return native_lock(context["repo"] / ".IMPLEMENTAUDIT/.r36-locks/namespace.gate", blocking=True)


class RetainedInputs:
    """Retain source file and ancestor handles across F2 and authority writes."""
    def __init__(self, paths):
        self.items = []
        try:
            for path in paths:
                pinned = PinnedFile(path)
                self.items.append([pinned, None])
                self.items[-1][1] = hashlib.sha256(pinned.read()).digest()
            self.verify()
        except BaseException:
            self.close()
            raise

    def verify(self):
        for pinned, digest in self.items:
            pinned.verify()
            if hashlib.sha256(pinned.read()).digest() != digest:
                raise CustodyError("retained source bytes drifted")

    def close(self):
        for pinned, _ in self.items:
            pinned.close()
        self.items = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            if exc_type is None:
                self.verify()
        finally:
            self.close()


class CASFailure(RotationError):
    pass


def write_blob(context, raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise RotationError("authority blob is outside bounded bytes")
    oid = git(context["repo"], "hash-object", "-w", "--stdin", input_bytes=raw).decode().strip()
    if read_blob(context["repo"], oid) != raw:
        raise RotationError("written authority blob failed exact readback")
    return oid


def retention_updates(context, oids):
    updates = {}
    for oid in sorted(set(item for item in oids if item is not None and item != "none")):
        read_blob(context["repo"], oid)
        ref = anchor_ref(context, oid)
        old = read_ref(context["repo"], ref)
        if old not in (None, oid):
            raise RotationError("retained object anchor was substituted")
        if old is None:
            updates[ref] = (oid, None)
    return updates


def update_refs(context, updates, guards, *, observation=None):
    """One expected-old Git transaction; classify effect by exact readback.

    The short gate cooperates with original main writers. The Git verify commands
    also fence concurrent ref writers that do not take that gate. No environment
    variable is treated as evidence of ownership or an already-held lock.
    """
    repo = context["repo"]
    if set(updates) & set(guards):
        raise RotationError("transaction contains overlapping guard and mutation refs")
    for ref, (new, old) in updates.items():
        ref_path(repo, ref)
        if not OID.fullmatch(new) or (old is not None and not OID.fullmatch(old)):
            raise RotationError("transaction OID is malformed")
    with namespace_gate(context):
        if observation is not None:
            observation.verify()
        expected = dict(guards)
        expected.update({ref: old for ref, (_, old) in updates.items()})
        def read_guard(ref):
            if ref == "HEAD":
                return git(repo, "rev-parse", "HEAD").decode().strip()
            return read_ref(repo, ref)
        if any(read_guard(ref) != oid for ref, oid in expected.items()):
            raise CASFailure("expected-old authority or namespace guard changed")
        chunks = [b"start\0"]
        for ref, oid in sorted(guards.items()):
            chunks.append(b"verify " + ref.encode() + b"\0" + (oid or ZERO).encode() + b"\0")
        for ref, (new, old) in sorted(updates.items()):
            chunks.append(b"update " + ref.encode() + b"\0" + new.encode() + b"\0" + (old or ZERO).encode() + b"\0")
        chunks.extend((b"prepare\0", b"commit\0"))
        failure = None
        try:
            result = git_process(repo, "update-ref", "--stdin", "-z", input_bytes=b"".join(chunks))
            if result.returncode:
                failure = CASFailure("Git refused the expected-old transaction")
        except RotationError as exc:
            failure = exc
        # A process exit code alone never establishes whether publication landed.
        after = {ref: read_guard(ref) for ref in expected}
        landed = all(after[ref] == new for ref, (new, _) in updates.items())
        intact = all(after[ref] == oid for ref, oid in guards.items())
        if not landed or not intact:
            raise CASFailure("publication did not have one exact verified effect") from failure
        if observation is not None:
            observation.verify()


def owner_guards(context, observed, *, exclude=()):
    return {context[key + "_ref"]: observed[key]
            for key in ("controller", "pointer", "marker", "invalidation") if key not in exclude}


def transition_guards(context, observed, record, epoch_oid, *, exclude=(), intent_oid=None):
    guards = owner_guards(context, observed, exclude=exclude)
    prepared, transition = record["prepared"], record["transition"]
    guards.update({"HEAD": transition["head"], epoch_ref(context, transition["continuity_epoch"]): epoch_oid,
                   prepared["archive_ref"]: prepared["archive_manifest_oid"],
                   prepared["predecessor"]["receipt_ref"]: prepared["predecessor"]["receipt_oid"]})
    guards.update(archive_retention_guards(context, prepared))
    if intent_oid is not None:
        guards[publication_ref(context, transition["continuity_epoch"])] = intent_oid
    if transition["failed_transition_receipt_ref_oid"]:
        ref, oid = split_receipt_token(context, transition["failed_transition_receipt_ref_oid"])
        guards[ref] = oid
    return guards


def resolve_predecessor(context):
    observed = authorities(context)
    if observed["controller"] != context["controller_oid"]:
        raise RotationError("controller custody changed")
    if observed["pointer"] is not None or observed["marker"] is not None:
        joined = require_current_generation_join_v1(context)
        token = joined["receipt_token"]
        state_path, road_path = joined["state_path"], joined["roadmap_path"]
        generation = joined["pointer"]["projection_generation_id"]
    else:
        token = owner_call(context["repo"], "--require-current-continuity", context["controller"]).decode().strip()
        state_path, road_path = context["run_root"] / "STATE.md", context["run_root"] / "ROADMAP.md"
        generation = token.split("@", 1)[0].rsplit("/", 1)[-1]
    receipt = read_receipt(context, token)
    ref, oid = split_receipt_token(context, token)
    head = git(context["repo"], "rev-parse", "HEAD").decode().strip()
    tree = git(context["repo"], "rev-parse", "HEAD^{tree}").decode().strip()
    if receipt["schema"] != RECEIPT_SCHEMA and (receipt["head"], receipt["tree"]) != (head, tree):
        raise RotationError("legacy source receipt binds another candidate")
    for role, path in (("state", state_path), ("roadmap", road_path)):
        if hashlib.sha256(read_regular(path)).hexdigest() != receipt[role + "_sha256"]:
            raise RotationError("current source pair differs from its real receipt")
    if receipt["invalidation_oid"] != (observed["invalidation"] or "none") or authorities(context) != observed:
        raise RotationError("source currentness changed during admission")
    return {"controller": context["controller"], "claim_id": context["claim_id"],
            "run_root_identity": context["run_root_identity"], "controller_oid": context["controller_oid"],
            "receipt_ref": ref, "receipt_oid": oid, "receipt_schema": receipt["schema"],
            "projection_generation_id": generation, "continuity_epoch": receipt["continuity_epoch"],
            "invalidation_oid": receipt["invalidation_oid"], "pointer_ref": context["pointer_ref"],
            "pointer_oid": observed["pointer"], "migration_marker_oid": observed["marker"],
            "head": head, "tree": tree, "exact_next_action": receipt["exact_next_action"],
            "state_sha256": receipt["state_sha256"], "roadmap_sha256": receipt["roadmap_sha256"],
            "state_path": Path(state_path).relative_to(context["repo"]).as_posix(),
            "roadmap_path": Path(road_path).relative_to(context["repo"]).as_posix()}


def native_resume_source(context):
    """Read a prior immutable JOIN only beneath one distinct native invalidation."""
    observed = managed(context)
    invalidation = invalidation_record(context, observed["invalidation"])
    if invalidation is None or invalidation["boundary"] not in BOUNDARIES:
        raise RotationError("PRE_RESUME_EVIDENCE requires a retained pending native boundary")
    joined = _read_generation_evidence_v1(context, observed)
    pointer = joined["pointer"]
    if pointer["invalidation_oid"] == observed["invalidation"]:
        raise RotationError("native boundary is already consumed by the current generation")
    ref, oid = split_receipt_token(context, joined["receipt_token"])
    predecessor = {"controller": context["controller"], "claim_id": context["claim_id"],
                   "run_root_identity": context["run_root_identity"], "controller_oid": context["controller_oid"],
                   "receipt_ref": ref, "receipt_oid": oid, "receipt_schema": RECEIPT_SCHEMA,
                   "projection_generation_id": pointer["projection_generation_id"],
                   "continuity_epoch": pointer["continuity_epoch"], "invalidation_oid": pointer["invalidation_oid"],
                   "pointer_ref": context["pointer_ref"], "pointer_oid": joined["pointer_oid"],
                   "migration_marker_oid": joined["marker_oid"],
                   "head": git(context["repo"], "rev-parse", "HEAD").decode().strip(),
                   "tree": git(context["repo"], "rev-parse", "HEAD^{tree}").decode().strip(),
                   "exact_next_action": pointer["exact_next_action"],
                   "state_sha256": pointer["state_sha256"], "roadmap_sha256": pointer["roadmap_sha256"],
                   "state_path": Path(joined["state_path"]).relative_to(context["repo"]).as_posix(),
                   "roadmap_path": Path(joined["roadmap_path"]).relative_to(context["repo"]).as_posix()}
    record, _ = read_epoch(context, pointer["continuity_epoch"])
    if ((predecessor["head"], predecessor["tree"]) != (record["transition"]["head"], record["transition"]["tree"])
            or authorities(context) != observed):
        raise RotationError("native resume evidence changed during source resolution")
    return {"joined": joined, "observed": observed, "predecessor": predecessor, "invalidation": invalidation}


def exact_authority_token(context, name, token):
    if (not isinstance(token, str) or token.count("@") != 1
            or token.split("@")[0] != context[name + "_ref"] or not OID.fullmatch(token.split("@")[1])):
        raise RotationError("native resume requires an exact " + name + " ref@oid token")
    return token.split("@")[1]


def bound_native_resume_source(context, pointer_token, invalidation_token):
    pointer_oid = exact_authority_token(context, "pointer", pointer_token)
    invalidation_oid = exact_authority_token(context, "invalidation", invalidation_token)
    source = native_resume_source(context)
    if source["observed"]["pointer"] != pointer_oid or source["observed"]["invalidation"] != invalidation_oid:
        raise RotationError("native resume source tokens are stale or mismatched")
    return source


def archive_retention_guards(context, prepared):
    """Fence the helper's fully verified historical population in owner CAS."""
    guards = projection_helper().archive_retention_guards(context["repo"], context["controller"],
                prepared["archive_ref"], prepared["archive_manifest_sha256"])
    prefix = f"refs/implementaudit/state-archives/{context['controller']}/"
    if (type(guards) is not dict or guards.get(prepared["archive_ref"]) != prepared["archive_manifest_oid"]
            or len(canonical(guards)) > MAX_BYTES):
        raise RotationError("archive retention census is malformed or does not bind its exact root")
    for ref, oid in guards.items():
        if (not isinstance(ref, str) or not ref.startswith(prefix)
                or not re.fullmatch(r"(?:G[0-9A-F]{4}|objects/[0-9a-f]{40})", ref[len(prefix):])
                or not isinstance(oid, str) or not OID.fullmatch(oid)
                or ("/objects/" in ref and ref.rsplit("/", 1)[-1] != oid)
                or read_ref(context["repo"], ref) != oid):
            raise RotationError("archive retention census drifted or escaped declared history custody")
        read_blob(context["repo"], oid)
    return guards


def verify_custody(context):
    expected = "\t".join((context["controller"], str(context["repo"]), str(context["run_root"]), context["claim_id"])) + "\n"
    if owner_call(context["repo"], "--current-controller", context["controller"]) != context.get("custody_output", expected.encode()):
        raise CustodyError("native claim custody changed during the operation")
    if read_ref(context["repo"], context["controller_ref"]) != context["controller_oid"]:
        raise CustodyError("controller custody changed during the operation")


def retained_owner_paths(context):
    return [context["run_root"] / ".claimed", *(Path(__file__).absolute().with_name(name) for name in
            ("claim-run.sh", "claim-run-rotation.py", "rotate-canonical-state.py", "canonical_hot_projection.py",
             "canonical_custody.py"))]


def predecessor_guards(context, predecessor):
    return {context["controller_ref"]: predecessor["controller_oid"],
            context["pointer_ref"]: predecessor["pointer_oid"],
            context["marker_ref"]: predecessor["migration_marker_oid"],
            context["invalidation_ref"]: None if predecessor["invalidation_oid"] == "none" else predecessor["invalidation_oid"],
            predecessor["receipt_ref"]: predecessor["receipt_oid"]}


def validate_prepared(context, prepared, predecessor):
    if type(prepared) is not dict or prepared.get("triggered") is not True:
        raise RotationError("projection helper did not return a prepared transaction")
    generation = next_epoch(predecessor["projection_generation_id"])
    if (prepared["predecessor"] != predecessor or prepared["generation_id"] != generation
            or prepared["source_state_sha256"] != predecessor["state_sha256"]
            or prepared["source_roadmap_sha256"] != predecessor["roadmap_sha256"]
            or prepared["exact_next_action"] != predecessor["exact_next_action"]
            or prepared["archive_ref"] != f"refs/implementaudit/state-archives/{context['controller']}/{generation}"):
        raise RotationError("prepared projection substituted the source or its successor")
    raw = canonical(prepared)  # Crash recovery must not depend on Python objects or handles.
    if len(raw) > MAX_BYTES:
        raise RotationError("prepared descriptor exceeds bounded retention")
    if read_ref(context["repo"], prepared["archive_ref"]) != prepared["archive_manifest_oid"]:
        raise RotationError("archive manifest ref failed exact readback")
    archive = read_blob(context["repo"], prepared["archive_manifest_oid"])
    if hashlib.sha256(archive).hexdigest() != prepared["archive_manifest_sha256"]:
        raise RotationError("archive manifest identity differs from prepared bytes")
    archive_retention_guards(context, prepared)


def allocate_epoch(context, prepared, observed, *, failed=None, failed_oid=None, observation=None):
    predecessor = prepared["predecessor"]
    recovery = failed is not None
    epoch = next_epoch(predecessor["continuity_epoch"])
    generation = next_epoch(predecessor["projection_generation_id"])
    if recovery:
        epoch, generation = next_epoch(epoch), next_epoch(generation)
    failed_receipt = None
    if recovery:
        failed_ref = receipt_ref(context, failed["transition"]["continuity_epoch"])
        failed_receipt_oid = read_ref(context["repo"], failed_ref)
        if failed_receipt_oid is not None:
            if observed["pointer"] is None or observed["pointer"] == failed["expected_pointer_oid"]:
                raise RotationError("failed-epoch receipt exists without its exact failed pointer")
            failed_pointer = validate_pointer(context, decode_json(read_blob(context["repo"], observed["pointer"])))
            failed_receipt = failed_ref + "@" + failed_receipt_oid
            receipt_matches_pointer(context, read_receipt(context, failed_receipt), failed_pointer, observed["pointer"])
            for key in ("continuity_epoch", "projection_generation_id", "invalidation_oid", "predecessor_receipt_ref_oid"):
                if failed_pointer[key] != failed["transition"][key]:
                    raise RotationError("available failed receipt substituted an owner transition")
    ref = receipt_ref(context, epoch)
    if read_ref(context["repo"], ref) is not None or read_ref(context["repo"], epoch_ref(context, epoch)) is not None:
        raise RotationError("fresh epoch or receipt ref was already allocated")
    transition = {"schema": TRANSITION_SCHEMA, "controller": context["controller"], "claim_id": context["claim_id"],
                  "run_root_identity": context["run_root_identity"], "projection_generation_id": generation,
                  "continuity_epoch": epoch, "boundary": "canonical-state-rotation", "invalidation_oid": None,
                  "predecessor_receipt_ref_oid": failed_receipt or predecessor["receipt_ref"] + "@" + predecessor["receipt_oid"],
                  "expected_receipt_ref_schema": {"ref": ref, "schema": RECEIPT_SCHEMA},
                  "transition_kind": "recovery" if recovery else "rotation",
                  "payload_source": "preimage" if recovery else "draft",
                  "failed_transition_epoch": failed["transition"]["continuity_epoch"] if recovery else None,
                  "failed_transition_generation": failed["transition"]["projection_generation_id"] if recovery else None,
                  "failed_transition_receipt_ref_oid": failed_receipt,
                  "head": predecessor["head"], "tree": predecessor["tree"]}
    record = {"schema": "implementaudit.rotation-epoch.v1", "transition": transition, "prepared": prepared,
              "controller_oid": context["controller_oid"], "expected_pointer_oid": observed["pointer"],
              "expected_marker_oid": observed["marker"], "failed_epoch_oid": failed_oid,
              "failed_pointer_oid": observed["pointer"] if recovery and observed["pointer"] != failed["expected_pointer_oid"] else None}
    event = "canonical-state-rotation/" + epoch + "/" + hashlib.sha256(canonical(record)).hexdigest()
    invalidation = ("\t".join(("implementaudit.continuity-invalidation.v1", context["controller"],
                              context["controller_oid"], context["claim_id"], "canonical-state-rotation", event)) + "\n").encode()
    invalidation_oid = write_blob(context, invalidation)
    transition["invalidation_oid"] = invalidation_oid
    validate_epoch(context, record, epoch)
    epoch_oid = write_blob(context, canonical(record))
    updates = retention_updates(context, [*observed.values(), predecessor["receipt_oid"],
                                         prepared["archive_manifest_oid"], invalidation_oid, epoch_oid, failed_oid,
                                         failed_receipt.split("@")[1] if failed_receipt else None])
    updates[context["invalidation_ref"]] = (invalidation_oid, observed["invalidation"])
    updates[epoch_ref(context, epoch)] = (epoch_oid, None)
    guards = owner_guards(context, observed, exclude=("invalidation",))
    guards[predecessor["receipt_ref"]] = predecessor["receipt_oid"]
    guards["HEAD"] = predecessor["head"]
    guards[prepared["archive_ref"]] = prepared["archive_manifest_oid"]
    guards.update(archive_retention_guards(context, prepared))
    if failed_receipt:
        failed_ref, failed_receipt_oid = split_receipt_token(context, failed_receipt)
        guards[failed_ref] = failed_receipt_oid
    update_refs(context, updates, guards, observation=observation)
    return record, epoch_oid


def allocate_native_resume_epoch(context, prepared, source, *, observation=None):
    predecessor, observed = source["predecessor"], source["observed"]
    epoch = next_epoch(predecessor["continuity_epoch"])
    ref = receipt_ref(context, epoch)
    if read_ref(context["repo"], ref) is not None or read_ref(context["repo"], epoch_ref(context, epoch)) is not None:
        raise RotationError("NATIVE_RESUME_ALLOCATION_EXISTS: retained partial publication requires inspection")
    transition = {"schema": NATIVE_TRANSITION_SCHEMA, "controller": context["controller"],
                  "claim_id": context["claim_id"], "run_root_identity": context["run_root_identity"],
                  "projection_generation_id": next_epoch(predecessor["projection_generation_id"]),
                  "continuity_epoch": epoch, "boundary": source["invalidation"]["boundary"],
                  "invalidation_oid": observed["invalidation"],
                  "predecessor_receipt_ref_oid": predecessor["receipt_ref"] + "@" + predecessor["receipt_oid"],
                  "expected_receipt_ref_schema": {"ref": ref, "schema": RECEIPT_SCHEMA},
                  "transition_kind": "native-resume", "payload_source": "preimage",
                  "failed_transition_epoch": None, "failed_transition_generation": None,
                  "failed_transition_receipt_ref_oid": None, "head": predecessor["head"], "tree": predecessor["tree"]}
    record = {"schema": "implementaudit.native-resume-epoch.v1", "transition": transition, "prepared": prepared,
              "controller_oid": context["controller_oid"], "expected_pointer_oid": observed["pointer"],
              "expected_marker_oid": observed["marker"], "failed_epoch_oid": None, "failed_pointer_oid": None}
    validate_epoch(context, record, epoch)
    epoch_oid = write_blob(context, canonical(record))
    updates = retention_updates(context, [*observed.values(), predecessor["receipt_oid"],
                                         prepared["archive_manifest_oid"], epoch_oid])
    updates[epoch_ref(context, epoch)] = (epoch_oid, None)
    guards = owner_guards(context, observed)
    guards.update({"HEAD": predecessor["head"], predecessor["receipt_ref"]: predecessor["receipt_oid"]})
    guards.update(archive_retention_guards(context, prepared))
    update_refs(context, updates, guards, observation=observation)
    return record, epoch_oid


def stage_observation(context, record, pointer_oid):
    observed = authorities(context)
    if observed["controller"] != context["controller_oid"] or observed["invalidation"] != record["transition"]["invalidation_oid"]:
        raise RotationError("NEWER_BOUNDARY_PREEMPTED_ROTATION: retain the native boundary and stop")
    if observed["pointer"] != pointer_oid or observed["marker"] != record["expected_marker_oid"]:
        raise CASFailure("rotation pointer or permanent marker changed")
    if (git(context["repo"], "rev-parse", "HEAD").decode().strip() != record["transition"]["head"]
            or git(context["repo"], "rev-parse", "HEAD^{tree}").decode().strip() != record["transition"]["tree"]):
        raise RotationError("candidate changed during rotation")
    return observed


def complete_epoch(context, record, epoch_oid, *, observation=None):
    transition, prepared = record["transition"], record["prepared"]
    stage_observation(context, record, record["expected_pointer_oid"])
    final = projection_helper().finalize_canonical_projection(context["repo"], context["run_root"], prepared, transition)
    pointer = validate_pointer(context, final["pointer"])
    if Path(final["generation_dir"]) != context["run_root"] / "state-generations" / transition["projection_generation_id"]:
        raise RotationError("final generation directory is outside exact custody")
    for key in ("controller", "claim_id", "run_root_identity", "projection_generation_id", "continuity_epoch",
                "invalidation_oid", "predecessor_receipt_ref_oid", "expected_receipt_ref_schema"):
        if pointer[key] != transition[key]:
            raise RotationError("finalized pointer substituted the owner transition")
    if (pointer["archive_manifest_sha256"] != prepared["archive_manifest_sha256"]
            or pointer["exact_next_action"] != prepared["exact_next_action"]):
        raise RotationError("finalized pointer substituted preserved bindings")
    verify_generation(context, pointer)
    pointer_oid = write_blob(context, canonical(pointer))
    observed = stage_observation(context, record, record["expected_pointer_oid"])
    intent = {"schema": "implementaudit.rotation-publication.v1", "controller": context["controller"],
              "claim_id": context["claim_id"], "run_root_identity": context["run_root_identity"],
              "continuity_epoch": transition["continuity_epoch"], "epoch_oid": epoch_oid,
              "pointer_ref": context["pointer_ref"], "pointer_oid": pointer_oid,
              "expected_pointer_oid": record["expected_pointer_oid"]}
    intent_oid = write_blob(context, canonical(intent))
    updates = retention_updates(context, [pointer_oid, intent_oid, epoch_oid, *observed.values()])
    updates[publication_ref(context, transition["continuity_epoch"])] = (intent_oid, None)
    update_refs(context, updates, transition_guards(context, observed, record, epoch_oid), observation=observation)
    observed = stage_observation(context, record, record["expected_pointer_oid"])
    updates = {}
    updates[context["pointer_ref"]] = (pointer_oid, record["expected_pointer_oid"])
    update_refs(context, updates, transition_guards(context, observed, record, epoch_oid,
                exclude=("pointer",), intent_oid=intent_oid), observation=observation)
    # A fresh resolved read is mandatory after CAS; the finalizer's PASS is not a receipt.
    verify_generation(context, pointer)
    observed = stage_observation(context, record, pointer_oid)
    receipt = [RECEIPT_SCHEMA, context["controller"], context["claim_id"], context["run_root_identity"],
               pointer["continuity_epoch"], pointer["invalidation_oid"], context["pointer_ref"], pointer_oid,
               pointer["state_sha256"], pointer["roadmap_sha256"], pointer["protected_manifest_sha256"],
               pointer["archive_manifest_sha256"], pointer["exact_next_action"], pointer["predecessor_receipt_ref_oid"]]
    receipt_oid = write_blob(context, ("\t".join(receipt) + "\n").encode())
    ref = pointer["expected_receipt_ref_schema"]["ref"]
    updates = retention_updates(context, [receipt_oid])
    updates[ref] = (receipt_oid, None)
    update_refs(context, updates, transition_guards(context, observed, record, epoch_oid, intent_oid=intent_oid), observation=observation)
    token = ref + "@" + receipt_oid
    receipt_matches_pointer(context, read_receipt(context, token), pointer, pointer_oid)
    if observed["marker"] is None:
        marker = [MARKER_SCHEMA, context["controller"], context["claim_id"], context["run_root_identity"],
                  pointer["continuity_epoch"], context["pointer_ref"], POINTER_SCHEMA, ref, receipt_oid, "true"]
        marker_oid = write_blob(context, "\t".join(marker).encode())
        observed = stage_observation(context, record, pointer_oid)
        updates = retention_updates(context, [marker_oid])
        updates[context["marker_ref"]] = (marker_oid, None)
        guards = transition_guards(context, observed, record, epoch_oid, exclude=("marker",), intent_oid=intent_oid)
        guards[ref] = receipt_oid
        update_refs(context, updates, guards, observation=observation)
    joined = require_current_generation_join_v1(context)
    if joined["pointer_oid"] != pointer_oid or joined["receipt_token"] != token:
        raise RotationError("terminal currentness JOIN did not bind this completed transaction")
    return {"status": {"recovery": "RECOVERED_PRIOR", "rotation": "ROTATED", "native-resume": "RESUMED"}[transition["transition_kind"]],
            "receipt_token": token, "pointer_token": context["pointer_ref"] + "@" + pointer_oid,
            "continuity_epoch": transition["continuity_epoch"], "marker_oid": joined["marker_oid"]}


def recover_failed_epoch(context, failed, failed_oid):
    verify_custody(context)
    observed = authorities(context)
    transition = failed["transition"]
    if observed["controller"] != context["controller_oid"]:
        raise RotationError("controller changed; no compensation outside current custody")
    if transition["transition_kind"] != "rotation":
        raise RotationError("recovery outcome is uncertain; a recovery epoch cannot be reused")
    expected = failed["expected_pointer_oid"]
    if observed["pointer"] != expected:
        intent, intent_oid = read_publication(context, failed, failed_oid, absent=True)
        ours = intent is not None and observed["pointer"] == intent["pointer_oid"]
        if not ours:
            winner = require_current_generation_join_v1(context)
            return {"status": "VERIFIED_WINNER", "receipt_token": winner["receipt_token"],
                    "pointer_token": context["pointer_ref"] + "@" + winner["pointer_oid"],
                    "marker_oid": winner["marker_oid"]}
    if observed["invalidation"] != transition["invalidation_oid"]:
        raise RotationError("NEWER_BOUNDARY_PREEMPTED_ROTATION: no compensation over another event")
    if observed["marker"] != failed["expected_marker_oid"]:
        if (failed["expected_marker_oid"] is not None or observed["marker"] is None
                or observed["pointer"] is None):
            raise RotationError("permanent marker changed outside the failed first migration")
        pointer = validate_pointer(context, decode_json(read_blob(context["repo"], observed["pointer"])))
        verify_marker(context, observed["marker"], pointer)
    prepared = failed["prepared"]
    validate_prepared(context, prepared, prepared["predecessor"])
    read_receipt(context, prepared["predecessor"]["receipt_ref"] + "@" + prepared["predecessor"]["receipt_oid"])
    with RetainedInputs(retained_owner_paths(context)) as observation:
        record, epoch_oid = allocate_epoch(context, prepared, observed, failed=failed, failed_oid=failed_oid, observation=observation)
        try:
            return complete_epoch(context, record, epoch_oid, observation=observation)
        except Exception as exc:
            raise RotationError("recovery did not reach pointer+receipt+marker currentness; retained allocation requires inspection") from exc


@_scoped_git
def run_canonical_rotation_v1(context, owner_map_path, calibration):
    with rotation_lease(context):
        predecessor = resolve_predecessor(context)
        owner_map_path = Path(owner_map_path)
        if not owner_map_path.is_absolute():
            owner_map_path = context["run_root"] / owner_map_path
        if not owner_map_path.is_relative_to(context["run_root"]):
            raise RotationError("owner map is outside the claimed run root")
        paths = [*retained_owner_paths(context), context["repo"] / predecessor["state_path"],
                 context["repo"] / predecessor["roadmap_path"]]
        # The cheap path need not possess an owner map. Triggered preparation itself
        # validates it, and an existing map is held for the entire transaction.
        if os.path.lexists(owner_map_path):
            paths.append(owner_map_path)
        with RetainedInputs(paths) as observation:
            generation = next_epoch(predecessor["projection_generation_id"])
            prepared = projection_helper().prepare_canonical_draft(context["repo"], context["run_root"],
                        context["controller"], generation, owner_map_path, predecessor, calibration)
            observation.verify()
            if type(prepared) is dict and prepared.get("triggered") is False:
                if any(read_ref(context["repo"], ref) != oid for ref, oid in predecessor_guards(context, predecessor).items()):
                    raise RotationError("source changed during cheap-path admission")
                return {"status": "NOT_TRIGGERED", "receipt_token": predecessor["receipt_ref"] + "@" + predecessor["receipt_oid"]}
            validate_prepared(context, prepared, predecessor)
            if any(read_ref(context["repo"], ref) != oid for ref, oid in predecessor_guards(context, predecessor).items()):
                raise RotationError("source boundary or authority changed during F2")
            observed = authorities(context)
            record, epoch_oid = allocate_epoch(context, prepared, observed, observation=observation)
            try:
                return complete_epoch(context, record, epoch_oid, observation=observation)
            except CustodyError:
                raise
            except Exception as exc:
                observation.verify()
                try:
                    return recover_failed_epoch(context, record, epoch_oid)
                except Exception as recovery_exc:
                    raise RotationError(str(recovery_exc)) from exc


@_scoped_git
def resume_native_generation_v1(context, boundary, epoch, pointer_token, invalidation_token):
    if boundary not in BOUNDARIES:
        raise RotationError("native resume requires one original native boundary")
    epoch = canonical_epoch(epoch)
    expected_pointer = exact_authority_token(context, "pointer", pointer_token)
    expected_invalidation = exact_authority_token(context, "invalidation", invalidation_token)
    with rotation_lease(context):
        try:
            joined = require_current_generation_join_v1(context)
        except RotationError:
            pass
        else:
            record, _ = read_epoch(context, joined["pointer"]["continuity_epoch"])
            transition = record["transition"]
            if (transition["transition_kind"] == "native-resume" and transition["continuity_epoch"] == epoch
                    and transition["boundary"] == boundary and transition["invalidation_oid"] == expected_invalidation
                    and record["expected_pointer_oid"] == expected_pointer):
                return {"status": "ALREADY_RESUMED", "receipt_token": joined["receipt_token"],
                        "pointer_token": context["pointer_ref"] + "@" + joined["pointer_oid"],
                        "continuity_epoch": epoch, "marker_oid": joined["marker_oid"]}
            raise RotationError("native resume tokens do not identify one exact completed native successor")
        source = bound_native_resume_source(context, pointer_token, invalidation_token)
        predecessor = source["predecessor"]
        if boundary != source["invalidation"]["boundary"] or epoch != next_epoch(predecessor["continuity_epoch"]):
            raise RotationError("native resume boundary or next epoch differs from the retained source")
        if any(read_ref(context["repo"], ref) is not None for ref in
               (epoch_ref(context, epoch), publication_ref(context, epoch), receipt_ref(context, epoch))):
            raise RotationError("NATIVE_RESUME_ALLOCATION_EXISTS: retained partial publication requires inspection")
        generation_dir = context["run_root"] / "state-generations" / predecessor["projection_generation_id"]
        paths = [*retained_owner_paths(context), *(generation_dir / name for name in
                 ("STATE.md", "ROADMAP.md", "protected-state.json", "archive-manifest.json", "generation-manifest.json"))]
        with RetainedInputs(paths) as observation:
            prepared = projection_helper().prepare_native_resume_draft(context["repo"], context["run_root"],
                        context["controller"], next_epoch(predecessor["projection_generation_id"]), predecessor)
            observation.verify()
            validate_prepared(context, prepared, predecessor)
            if authorities(context) != source["observed"]:
                raise RotationError("newer boundary or source authority preempted native resume preparation")
            record, epoch_oid = allocate_native_resume_epoch(context, prepared, source, observation=observation)
            try:
                return complete_epoch(context, record, epoch_oid, observation=observation)
            except CustodyError:
                raise
            except Exception as exc:
                raise RotationError("NATIVE_RESUME_INCOMPLETE: retained native allocation requires inspection; " + str(exc)) from exc


@_scoped_git
def recover_rotation_v1(context):
    with rotation_lease(context):
        observed = authorities(context)
        if observed["controller"] != context["controller_oid"]:
            raise RotationError("recovery controller custody changed")
        try:
            joined = require_current_generation_join_v1(context)
        except (RotationError, LegacyRoute):
            pass
        else:
            return {"status": "ALREADY_CURRENT", "receipt_token": joined["receipt_token"],
                    "pointer_token": context["pointer_ref"] + "@" + joined["pointer_oid"],
                    "marker_oid": joined["marker_oid"]}
        invalidation = invalidation_record(context, observed["invalidation"])
        if invalidation is None or invalidation["boundary"] != "canonical-state-rotation":
            raise RotationError("no recoverable owned rotation invalidation; native boundary remains authoritative")
        match = re.fullmatch(r"canonical-state-rotation/(G[0-9A-F]{4})/([0-9a-f]{64})", invalidation["event"])
        if not match:
            raise RotationError("rotation invalidation has no exact retained epoch")
        record, oid = read_epoch(context, match[1])
        if record["transition"]["invalidation_oid"] != observed["invalidation"]:
            raise RotationError("recovery epoch is not the current invalidation")
        return recover_failed_epoch(context, record, oid)


@_scoped_git
def invalidate_current_generation_v1(context, boundary, event):
    if boundary not in BOUNDARIES:
        raise RotationError("public invalidation requires a native boundary, not a rotation claim")
    field(event, "physical boundary event")
    observed = managed(context)
    raw = ("\t".join(("implementaudit.continuity-invalidation.v1", context["controller"],
                      context["controller_oid"], context["claim_id"], boundary, event)) + "\n").encode()
    oid = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    # A physical occurrence has one boundary kind. Reuse existing append-only
    # object anchors to distinguish exact retry from conflicting provenance;
    # neither an observer nor another event/currentness store is introduced.
    for kind in sorted((BOUNDARIES | {"canonical-state-rotation"}) - {boundary}):
        other = ("\t".join(("implementaudit.continuity-invalidation.v1", context["controller"],
                            context["controller_oid"], context["claim_id"], kind, event)) + "\n").encode()
        other_oid = hashlib.sha1(b"blob " + str(len(other)).encode() + b"\0" + other).hexdigest()
        retained = read_ref(context["repo"], anchor_ref(context, other_oid))
        if retained is not None:
            require_anchor(context, other_oid)
        if retained is not None or observed["invalidation"] == other_oid:
            raise RotationError("physical boundary occurrence has conflicting retained boundary kinds")
    if observed["invalidation"] == oid:
        return context["invalidation_ref"] + "@" + oid
    # The source owner's stronger behavior is preserved: a genuinely newer event
    # is admitted even while the previous receipt is stale. No require-current here.
    if read_ref(context["repo"], anchor_ref(context, oid)) is not None:
        raise RotationError("historical boundary occurrence cannot be replayed as new")
    if write_blob(context, raw) != oid:
        raise RotationError("native invalidation bytes changed before publication")
    updates = retention_updates(context, [*observed.values(), oid])
    updates[context["invalidation_ref"]] = (oid, observed["invalidation"])
    update_refs(context, updates, owner_guards(context, observed, exclude=("invalidation",)))
    return context["invalidation_ref"] + "@" + oid


@_scoped_git
def read_component(context, component, expected_pointer=None):
    if component not in {"STATE", "ROADMAP"}:
        raise RotationError("canonical component must be STATE or ROADMAP")
    try:
        managed(context)
    except LegacyRoute:
        if expected_pointer not in (None, "none"):
            raise RotationError("legacy reader expected-pointer mismatch")
        token = owner_call(context["repo"], "--require-current-continuity", context["controller"])
        raw = read_regular(context["run_root"] / (component + ".md"))
        if owner_call(context["repo"], "--require-current-continuity", context["controller"]) != token:
            raise RotationError("legacy pair changed during separate read")
        return raw
    joined = require_current_generation_join_v1(context)
    if expected_pointer is not None and expected_pointer != context["pointer_ref"] + "@" + joined["pointer_oid"]:
        raise RotationError("current pointer changed between separate reads")
    return joined[component.lower() + "_bytes"]


@_scoped_git
def resolve_generation(context):
    joined = require_current_generation_join_v1(context)
    generation = context["run_root"] / "state-generations" / joined["pointer"]["projection_generation_id"]
    return {"schema": "implementaudit.canonical-generation-resolution.v1", "controller": context["controller"],
            "claim_id": context["claim_id"], "run_root_identity": context["run_root_identity"],
            "pointer_token": context["pointer_ref"] + "@" + joined["pointer_oid"],
            "receipt_token": joined["receipt_token"], "marker_oid": joined["marker_oid"],
            "state_path": str(joined["state_path"]), "roadmap_path": str(joined["roadmap_path"]),
            "protected_manifest_path": str(generation / "protected-state.json"),
            "archive_manifest_path": str(generation / "archive-manifest.json"), "pointer": joined["pointer"]}


@_scoped_git
def resolve_resume_generation(context):
    source = native_resume_source(context)
    joined, observed = source["joined"], source["observed"]
    generation = context["run_root"] / "state-generations" / joined["pointer"]["projection_generation_id"]
    return {"schema": "implementaudit.native-resume-source.v1", "status": "PRE_RESUME_EVIDENCE",
            "controller": context["controller"], "claim_id": context["claim_id"],
            "run_root_identity": context["run_root_identity"],
            "pointer_token": context["pointer_ref"] + "@" + observed["pointer"],
            "invalidation_token": context["invalidation_ref"] + "@" + observed["invalidation"],
            "boundary": source["invalidation"]["boundary"],
            "next_continuity_epoch": next_epoch(joined["pointer"]["continuity_epoch"]),
            "next_projection_generation_id": next_epoch(joined["pointer"]["projection_generation_id"]),
            "receipt_token": joined["receipt_token"], "marker_oid": joined["marker_oid"],
            "state_path": str(joined["state_path"]), "roadmap_path": str(joined["roadmap_path"]),
            "protected_manifest_path": str(generation / "protected-state.json"),
            "archive_manifest_path": str(generation / "archive-manifest.json"), "pointer": joined["pointer"]}


@_scoped_git
def read_resume_component(context, component, pointer_token, invalidation_token):
    if component not in {"STATE", "ROADMAP"}:
        raise RotationError("native resume component must be STATE or ROADMAP")
    source = bound_native_resume_source(context, pointer_token, invalidation_token)
    return source["joined"][component.lower() + "_bytes"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("require", "verify", "resume", "invalidate", "read", "read-role", "resolve",
                                           "resolve-resume", "read-resume", "rotate", "recover"))
    parser.add_argument("controller")
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    context = discover(args.controller)
    if args.command == "read-resume":
        reader = argparse.ArgumentParser(prog="claim-run.sh --read-resume-state")
        reader.add_argument("--role", required=True, choices=("STATE", "ROADMAP"))
        reader.add_argument("--expected-pointer", required=True)
        reader.add_argument("--expected-invalidation", required=True)
        options = reader.parse_args(args.arguments)
        sys.stdout.buffer.write(read_resume_component(context, options.role, options.expected_pointer, options.expected_invalidation))
        return 0
    if args.command == "resolve-resume":
        if args.arguments:
            raise RotationError("resume evidence resolution does not accept additional arguments")
        sys.stdout.buffer.write(canonical(resolve_resume_generation(context)) + b"\n")
        return 0
    if args.command == "read":
        if len(args.arguments) != 3 or args.arguments[1] != "--expected-pointer":
            raise RotationError("read requires component and exact expected pointer")
        sys.stdout.buffer.write(read_component(context, args.arguments[0], args.arguments[2]))
        return 0
    if args.command == "read-role":
        reader = argparse.ArgumentParser(prog="claim-run.sh --read-canonical-state")
        reader.add_argument("--role", required=True, choices=("STATE", "ROADMAP"))
        reader.add_argument("--expected-pointer")
        options = reader.parse_args(args.arguments)
        sys.stdout.buffer.write(read_component(context, options.role, options.expected_pointer))
        return 0
    if args.command == "resolve":
        if args.arguments:
            raise RotationError("resolve does not accept additional arguments")
        sys.stdout.buffer.write(canonical(resolve_generation(context)) + b"\n")
        return 0
    if args.command == "rotate":
        rotation = argparse.ArgumentParser(prog="claim-run.sh --rotate-canonical-state")
        rotation.add_argument("--owner-map", required=True)
        options = rotation.parse_args(args.arguments)
        helper = projection_helper()
        result = run_canonical_rotation_v1(context, Path(options.owner_map), helper.calibration_contract_v1())
        sys.stdout.buffer.write(canonical(result) + b"\n")
        return 0
    if args.command == "recover":
        if args.arguments:
            raise RotationError("recover does not accept additional arguments")
        sys.stdout.buffer.write(canonical(recover_rotation_v1(context)) + b"\n")
        return 0
    managed(context)
    if args.command == "resume":
        if len(args.arguments) != 4:
            raise RotationError("native resume requires boundary, next epoch and both exact authority tokens")
        result = resume_native_generation_v1(context, *args.arguments)
        print(result["receipt_token"])
        return 0
    if args.command == "invalidate":
        if len(args.arguments) != 2:
            raise RotationError("invalidation requires boundary and physical event")
        print(invalidate_current_generation_v1(context, *args.arguments))
        return 0
    result = require_current_generation_join_v1(context)
    if args.command == "verify" and args.arguments != [result["receipt_token"]]:
        raise RotationError("receipt does not name the current generation")
    print(result["receipt_token"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LegacyRoute:
        raise SystemExit(3)
    except (RuntimeError, OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        print("claim-run.sh: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
