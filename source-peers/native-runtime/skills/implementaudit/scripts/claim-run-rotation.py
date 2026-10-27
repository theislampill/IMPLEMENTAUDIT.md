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

# Bind the load snapshot to the actual executing module code, before any owner
# read. A newly sampled disk hash alone must never relabel an older instance.
def _capture_claim_load_identity_v1(executing_code):
    path = Path(__file__).absolute()
    before = os.lstat(path)
    if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
            or getattr(before, 'st_file_attributes', 0) & 0x400):
        raise ImportError('executing claim code has no ordinary physical source')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(512 * 1024 + 1)
        after = os.fstat(stream.fileno())
    current = os.lstat(path)
    identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
    if (identity(before) != identity(opened) or identity(opened) != identity(after)
            or identity(after) != identity(current) or len(raw) != before.st_size
            or len(raw) > 512 * 1024):
        raise ImportError('executing claim code source changed during load binding')
    compiled = compile(raw, executing_code.co_filename, 'exec', dont_inherit=True,
                       optimize=sys.flags.optimize)
    if compiled != executing_code:
        raise ImportError('executing claim code differs from the physical load snapshot')
    return (str(path), len(raw), hashlib.sha256(raw).hexdigest())


_CLAIM_LOAD_IDENTITY_V1 = _capture_claim_load_identity_v1(sys._getframe().f_code)


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
        raw = stream.read(36368)
        after = os.fstat(stream.fileno())
    if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
            or (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            or len(raw) != 36367
            or hashlib.sha256(raw).hexdigest() != "d52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389"):
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
C02_TRANSITION_SCHEMA = "implementaudit.c02-correction-transition.v1"
C02_BOUNDARY = "erroneous-invalidation-correction"
POINTER_KEYS = {"schema", "controller", "claim_id", "run_root_identity",
                "projection_generation_id", "continuity_epoch", "invalidation_oid",
                "predecessor_receipt_ref_oid", "expected_receipt_ref_schema",
                "projection_schema", "state_sha256", "roadmap_sha256",
                "protected_manifest_sha256", "archive_manifest_sha256", "exact_next_action"}
MAX_BYTES = 64 * 1024 * 1024
_PROJECTION_MODULE_BYTES = 125155
_PROJECTION_MODULE_SHA256 = "2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc"


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
    choices = ((r"C:\Program Files\Git\mingw64\bin\git.exe",
                r"C:\Program Files\Git\cmd\git.exe", r"C:\Program Files\Git\bin\git.exe")
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
        executable = Path(fixed_git())
        root = executable.parents[2] if executable.parent.parent.name == "mingw64" else executable.parents[1]
        search = [str(Path(sys.executable).parent), str(root / "mingw64/bin"), str(root / "cmd"),
                  str(root / "bin"), str(root / "usr/bin"), r"C:\Windows\System32"]
        result = {"SystemRoot": r"C:\Windows", "WINDIR": r"C:\Windows"}
    else:
        search = [str(Path(sys.executable).parent), "/usr/bin", "/bin", "/usr/local/bin"]
        result = {}
    result.update({"PATH": os.pathsep.join(search), "LC_ALL": "C", "LANG": "C",
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                   "GIT_TERMINAL_PROMPT": "0"})
    if os.name == "nt":
        # Long authority refs need explicit Git support even under a short root.
        # This process-owned setting never changes the user's Git configuration.
        result.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.longpaths",
                       "GIT_CONFIG_VALUE_0": "true"})
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


def read_refs(repo, refs):
    names = list(refs)
    authority_names = [name for name in names if name != 'HEAD']
    try:
        observed = _CUSTODY.current_refs(repo, authority_names)
    except OSError as exc:
        raise CustodyError(str(exc)) from exc
    if observed is NotImplemented:
        observed = {name: read_ref(repo, name) for name in authority_names}
    if 'HEAD' in names:
        observed['HEAD'] = git(repo, 'rev-parse', 'HEAD').decode().strip()
    return observed


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
    names = ("controller", "pointer", "marker", "invalidation")
    observed = read_refs(context['repo'], [context[name + '_ref'] for name in names])
    return {name: observed[context[name + '_ref']] for name in names}


def managed(context):
    observed = authorities(context)
    if observed["controller"] != context["controller_oid"]:
        raise RotationError("controller custody changed")
    if observed["pointer"] is None and observed["marker"] is None:
        raise LegacyRoute()
    return observed


def projection_helper():
    """Verify and execute one captured buffer from the selected physical sibling."""
    expected_bytes = globals().get("_PROJECTION_MODULE_BYTES")
    expected_digest = globals().get("_PROJECTION_MODULE_SHA256")
    if (type(expected_bytes) is not int or not 0 < expected_bytes <= MAX_BYTES
            or type(expected_digest) is not str or not SHA256.fullmatch(expected_digest)):
        raise RotationError("projection helper source binding is invalid")
    path = Path(__file__).with_name("rotate-canonical-state.py").absolute()
    raw = read_regular(path, max_bytes=expected_bytes)
    if len(raw) != expected_bytes or hashlib.sha256(raw).hexdigest() != expected_digest:
        raise RotationError("projection helper source differs from selected owner")
    # Equal code in another installation must not reuse that installation's
    # __file__ or its independently selected native input owner.
    name = "_claim_owned_rotation_projection_" + hashlib.sha256(os.fsencode(path) + b'\0' + raw).hexdigest()
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
    if row[4] not in BOUNDARIES | {"canonical-state-rotation", C02_BOUNDARY}:
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
    correction = type(record) is dict and record.get('schema') == 'implementaudit.c02-correction-epoch.v1'
    if correction:
        keys.add('c02_admission')
    if (type(record) is not dict or set(record) != keys
            or record["schema"] not in {"implementaudit.rotation-epoch.v1", "implementaudit.native-resume-epoch.v1",
                                        "implementaudit.c02-correction-epoch.v1"}):
        raise RotationError("allocated epoch descriptor is malformed")
    native = record["schema"] == "implementaudit.native-resume-epoch.v1"
    transition = record["transition"]
    keys = {"schema", "controller", "claim_id", "run_root_identity", "projection_generation_id",
            "continuity_epoch", "boundary", "invalidation_oid", "predecessor_receipt_ref_oid",
            "expected_receipt_ref_schema", "transition_kind", "payload_source",
            "failed_transition_epoch", "failed_transition_generation", "failed_transition_receipt_ref_oid", "head", "tree"}
    if (type(transition) is not dict or set(transition) != keys
            or transition["schema"] != (C02_TRANSITION_SCHEMA if correction else NATIVE_TRANSITION_SCHEMA if native else TRANSITION_SCHEMA)):
        raise RotationError("owner transition is malformed")
    for key in ("controller", "claim_id", "run_root_identity"):
        if transition[key] != context[key]:
            raise RotationError("epoch descriptor owner changed")
    if (record["controller_oid"] != context["controller_oid"]
            or transition["continuity_epoch"] != expected_epoch
            or transition["boundary"] not in ({C02_BOUNDARY} if correction else BOUNDARIES if native else {"canonical-state-rotation"})
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
    if (native and transition["transition_kind"] == "native-resume") or (correction and transition['transition_kind'] == 'c02-correction'):
        expected = (failed_epoch, failed_generation, "preimage", None, None, None, None)
        if (prepared.get("schema") != ('implementaudit.c02-correction-prepared.v1' if correction else "implementaudit.native-resume-prepared.v1")
                or predecessor["receipt_schema"] != RECEIPT_SCHEMA
                or record["expected_pointer_oid"] is None or record["expected_marker_oid"] is None
                or record["expected_pointer_oid"] != predecessor["pointer_oid"]
                or record["expected_marker_oid"] != predecessor["migration_marker_oid"]):
            raise RotationError("native resume lacks its exact migrated source and permanent marker")
    elif not native and not correction and transition["transition_kind"] == "rotation":
        expected = (failed_epoch, failed_generation, "draft", None, None, None, None)
    elif not native and not correction and transition["transition_kind"] == "recovery":
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
    if native or correction:
        old_pointer = validate_pointer(context, decode_json(read_blob(context["repo"], record["expected_pointer_oid"])))
        receipt_matches_pointer(context, read_receipt(context, source_receipt), old_pointer, record["expected_pointer_oid"])
        if (invalidation is None or invalidation["boundary"] != transition["boundary"]
                or transition["invalidation_oid"] == old_pointer["invalidation_oid"]
                or old_pointer["continuity_epoch"] != source_epoch
                or old_pointer["projection_generation_id"] != source_generation
                or old_pointer["invalidation_oid"] != predecessor["invalidation_oid"]):
            raise RotationError("native resume does not bind its distinct retained native occurrence and prior pointer")
        if correction:
            _c02_validate_admission_record_v1(context, record)
            event = 'c02-correction/' + record['c02_admission']['correction_record_oid'] + '/' + expected_epoch
            if invalidation != {'boundary': C02_BOUNDARY, 'event': event, 'oid': transition['invalidation_oid']}:
                raise RotationError('C02 epoch does not bind its distinct fresh correction invalidation')
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
    validated = validate_epoch(context, record, epoch)
    if record['schema'] == 'implementaudit.c02-correction-epoch.v1':
        require_anchor(context, record['c02_admission']['source_oid'])
        require_anchor(context, record['c02_admission']['grant_oid'])
    return validated, oid


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
            or read_refs(context['repo'], history_guards) != history_guards):
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


class _NativePublicationInputs:
    """Compose source custody with the selected native owner's live checkpoints.

    Checkpoint races are UNKNOWN, never a successful native qualification. The
    fixed producer must also supply exclusive host custody and its atomic source
    revision integration before production admission; this wrapper grants none.
    """
    def __init__(self, retained, native_guard):
        self.retained, self.native_guard = retained, native_guard

    def verify(self):
        self.retained.verify()
        self.native_guard.verify()

    def ref_guards_v1(self):
        return self.native_guard.ref_guards_v1()

    def verified_ref_guards_v1(self):
        """One retained/native preflight; guard extraction performs verification."""
        self.retained.verify()
        return self.ref_guards_v1()

    def before_effect(self):
        self.verify()
        return self.native_guard.before_effect()

    def after_effect(self, checkpoint):
        self.native_guard.after_effect(checkpoint)
        self.retained.verify()


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
        if isinstance(observation, _NativePublicationInputs):
            source_guards = observation.verified_ref_guards_v1()
            if set(source_guards) & set(updates) or any(
                    ref in guards and guards[ref] != oid for ref, oid in source_guards.items()):
                raise RotationError("native source/grant ref overlaps or conflicts with canonical CAS")
            guards = dict(guards, **source_guards)
        elif observation is not None:
            observation.verify()
        expected = dict(guards)
        expected.update({ref: old for ref, (_, old) in updates.items()})
        if read_refs(repo, expected) != expected:
            raise CASFailure("expected-old authority or namespace guard changed")
        chunks = [b"start\0"]
        for ref, oid in sorted(guards.items()):
            chunks.append(b"verify " + ref.encode() + b"\0" + (oid or ZERO).encode() + b"\0")
        for ref, (new, old) in sorted(updates.items()):
            chunks.append(b"update " + ref.encode() + b"\0" + new.encode() + b"\0" + (old or ZERO).encode() + b"\0")
        chunks.extend((b"prepare\0", b"commit\0"))
        failure = None
        checkpoint = (observation.before_effect()
                      if isinstance(observation, _NativePublicationInputs) else None)
        try:
            result = git_process(repo, "update-ref", "--stdin", "-z", input_bytes=b"".join(chunks))
            if result.returncode:
                failure = CASFailure("Git refused the expected-old transaction")
        except RotationError as exc:
            failure = exc
        finally:
            if checkpoint is not None:
                observation.after_effect(checkpoint)
        # A process exit code alone never establishes whether publication landed.
        after = read_refs(repo, expected)
        landed = all(after[ref] == new for ref, (new, _) in updates.items())
        intact = all(after[ref] == oid for ref, oid in guards.items())
        if not landed or not intact:
            raise CASFailure("publication did not have one exact verified effect") from failure
        if observation is not None:
            observation.verify()


# Transient synchronization owned by the EXISTING producer. Not an issuer,
# currentness store, service, or alternate ref writer. No ResetEvent operation.
def _native_sync_api_v1():
    if os.name != 'nt':
        raise RotationError('native cancellation requires the qualified Windows host')
    import ctypes
    from ctypes import wintypes as W
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    declarations = {
        'CreateEventW': (W.HANDLE, (ctypes.c_void_p, W.BOOL, W.BOOL, W.LPCWSTR)),
        'SetEvent': (W.BOOL, (W.HANDLE,)),
        'WaitForSingleObject': (W.DWORD, (W.HANDLE, W.DWORD)),
        'CloseHandle': (W.BOOL, (W.HANDLE,)),
        'OpenProcess': (W.HANDLE, (W.DWORD, W.BOOL, W.DWORD)),
        'GetCurrentProcess': (W.HANDLE, ()),
        'DuplicateHandle': (W.BOOL, (W.HANDLE, W.HANDLE, W.HANDLE,
                          ctypes.POINTER(W.HANDLE), W.DWORD, W.BOOL, W.DWORD)),
    }
    for name, (restype, argtypes) in declarations.items():
        function = getattr(k, name)
        function.restype, function.argtypes = restype, argtypes
    return ctypes, W, k


class NativeCancellationSignalV1:
    """Sticky unnamed manual-reset event; only the producer receives modify rights."""
    def __init__(self, reservation_id):
        self.c, self.W, self.k = _native_sync_api_v1()
        self.handle = self.k.CreateEventW(None, True, False, None)
        if not self.handle:
            raise RotationError('native producer cancellation event is unavailable')
        self.descriptor = {'schema': 'implementaudit.native-cancellation.v1',
            'producer_process': native_process_identity_v1(os.getpid()),
            'event_handle': int(self.handle), 'reservation_id': reservation_id}

    def signal(self):
        # FIRST action at every ingress/revocation hook. No reservation lock,
        # file/Git read, namespace gate, or currentness operation precedes this.
        if not self.handle or not self.k.SetEvent(self.handle):
            raise RotationError('native cancellation signal failed; contain owned host')

    def check(self):
        if not self.handle or self.k.WaitForSingleObject(self.handle, 0) != 258:
            raise RotationError('native producer reservation is already cancelled or closed')

    def close(self):
        # Explicit disposal only after durable terminalization / consumer exit.
        # Closing is never a reset and never makes an old reservation usable.
        handle, self.handle = self.handle, None
        if handle and not self.k.CloseHandle(handle):
            raise RotationError('native cancellation producer handle cleanup failed')


class NativeCancellationWaitV1:
    """Duplicate the exact live producer object with SYNCHRONIZE rights only.

    Numeric JSON is not a capability: producer PID/birth/image is independently
    checked, DuplicateHandle obtains the actual object from that process, and
    NtQueryObject verifies Event type. The successful durable CLAIMED CAS binds
    the exact consuming PID/birth and transaction. Other consumers cannot reset
    this event and cannot replay CLAIMED after that executor exits.
    """
    def __init__(self, descriptor, producer_process, reservation_id):
        self.c, self.W, self.k = _native_sync_api_v1()
        self.handle = None
        if (type(descriptor) is not dict or set(descriptor) !=
                {'schema', 'producer_process', 'event_handle', 'reservation_id'}
                or descriptor['schema'] != 'implementaudit.native-cancellation.v1'
                or descriptor['producer_process'] != producer_process
                or descriptor['reservation_id'] != reservation_id
                or type(descriptor['event_handle']) is not int or not 0 < descriptor['event_handle'] < 2**64
                or native_process_identity_v1(producer_process['pid']) != producer_process):
            raise RotationError('native cancellation descriptor is unbound or stale')
        self.producer_process = dict(producer_process)
        process = self.k.OpenProcess(0x0040 | 0x1000, False, producer_process['pid'])
        if not process:
            raise RotationError('native cancellation producer cannot be held')
        try:
            duplicate = self.W.HANDLE()
            # Deliberately no EVENT_MODIFY_STATE, no DUPLICATE_SAME_ACCESS,
            # and no inheritable handle. The child can only wait/check.
            if not self.k.DuplicateHandle(process, descriptor['event_handle'], self.k.GetCurrentProcess(),
                    self.c.byref(duplicate), 0x00100000, False, 0):
                raise RotationError('native cancellation object cannot be duplicated')
            self.handle = duplicate.value
        finally:
            self.k.CloseHandle(process)
        try:
            self._event_type()
            self.check()
        except BaseException:
            self.close()
            raise

    def _event_type(self):
        c = self.c
        class UnicodeString(c.Structure):
            _fields_ = [('length', self.W.USHORT), ('maximum', self.W.USHORT), ('buffer', c.c_void_p)]
        query = c.WinDLL('ntdll').NtQueryObject
        query.argtypes = (self.W.HANDLE, self.W.ULONG, c.c_void_p, self.W.ULONG, c.POINTER(self.W.ULONG))
        query.restype = c.c_long
        buffer = c.create_string_buffer(4096)
        needed = self.W.ULONG()
        if query(self.handle, 2, buffer, len(buffer), c.byref(needed)) != 0:
            raise RotationError('native cancellation object type unavailable')
        name = UnicodeString.from_buffer(buffer)
        start = c.addressof(buffer)
        if (name.length % 2 or not start <= (name.buffer or 0) <= start + len(buffer) - name.length
                or c.wstring_at(name.buffer, name.length // 2) != 'Event'):
            raise RotationError('native cancellation handle is not an Event')

    def check(self):
        # Check the independent sticky signal BEFORE slower process/ref reads.
        if not self.handle or self.k.WaitForSingleObject(self.handle, 0) != 258:
            raise RotationError('native reservation cancelled or cancellation handle invalid')
        if native_process_identity_v1(self.producer_process['pid']) != self.producer_process:
            raise RotationError('native cancellation producer died or was replaced')
        if self.k.WaitForSingleObject(self.handle, 0) != 258:
            raise RotationError('native reservation cancelled during liveness read')

    def close(self):
        handle, self.handle = self.handle, None
        if handle and not self.k.CloseHandle(handle):
            raise RotationError('native cancellation consumer handle cleanup failed')


def native_held_image_sha256_v1(pinned):
    """Hash the existing held descriptor in <=1MiB buffers; never read() the image."""
    pinned.verify()
    fd = pinned.native.fd if pinned.native is not None else pinned.fd
    expected_size = os.fstat(fd).st_size
    if not 0 <= expected_size <= 512 * 1024 * 1024:
        raise RotationError('native image exceeds the admitted file bound')
    os.lseek(fd, 0, os.SEEK_SET)
    digest, count = hashlib.sha256(), 0
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        count += len(chunk)
        if count > expected_size:
            raise RotationError('native image grew during streaming hash')
        digest.update(chunk)
    pinned.verify()
    if count != expected_size or os.fstat(fd).st_size != expected_size:
        raise RotationError('native image changed during streaming hash')
    return digest.hexdigest()


# Reuse only the existing claim's completed predecessor read inside its SAME
# operation/custody. This is not producer admission or a currentness cache.
_NATIVE_PREDECESSOR_BINDING_V1 = None


def _verify_claim_load_identity_v1():
    path = Path(__file__).absolute()
    raw = read_regular(path, max_bytes=512 * 1024)
    if (str(path), len(raw), hashlib.sha256(raw).hexdigest()) != _CLAIM_LOAD_IDENTITY_V1:
        raise RotationError('executing claim source differs from its bound load identity')
    return raw


class _NativePredecessorReadV1:
    def __init__(self, context):
        import threading
        _verify_claim_load_identity_v1()  # BEFORE the first canonical owner read.
        self._thread = threading.get_ident()
        self._scope = _CUSTODY._GIT_SCOPE.get()
        if self._scope is None or self._scope.repo != context['repo'].absolute():
            raise RotationError('native predecessor reuse requires existing claim Git custody')
        self._context = dict(context)
        # Mint only by performing the actual existing owner read. Caller JSON
        # and a matching hash cannot manufacture this operation-local witness.
        self._raw = canonical(resolve_predecessor(context))
        self._retained = None
        self._used = self._closed = False

    def predecessor(self):
        return decode_json(self._raw)

    def _physical(self):
        import threading
        if (self._closed or self._thread != threading.get_ident()
                or _CUSTODY._GIT_SCOPE.get() is not self._scope
                or type(self._retained) is not RetainedInputs):
            raise RotationError('native predecessor read escaped its existing operation custody')
        predecessor, context = self.predecessor(), self._context
        held = {item.path: digest.hex() for item, digest in self._retained.items}
        if held.get(Path(__file__).absolute()) != _CLAIM_LOAD_IDENTITY_V1[2]:
            raise RotationError('retained claim code differs from the executing load identity')
        required = set(retained_owner_paths(context))
        required.update(context['repo'] / predecessor[role + '_path'] for role in ('state', 'roadmap'))
        if not required.issubset(held) or any(
                held[context['repo'] / predecessor[role + '_path']] != predecessor[role + '_sha256']
                for role in ('state', 'roadmap')):
            raise RotationError('native predecessor owner/code or exact source bytes are not retained')
        self._retained.verify()
        self._scope._native_ref_custody()  # Reverify held Git routing/config inputs.

    def verify(self):
        if _NATIVE_PREDECESSOR_BINDING_V1 is not self:
            raise RotationError('native predecessor read is not the active existing-owner binding')
        self._physical()
        predecessor, context = self.predecessor(), self._context
        guards = dict(predecessor_guards(context, predecessor), HEAD=predecessor['head'])
        if (read_refs(context['repo'], guards) != guards
                or git(context['repo'], 'rev-parse', 'HEAD^{tree}').decode().strip() != predecessor['tree']):
            raise RotationError('native predecessor live authority or candidate changed')

    def take(self, controller):
        if self._used or controller != self._context['controller']:
            raise RotationError('native predecessor read is consumed or foreign')
        self.verify()
        self._used = True
        return dict(self._context), self.predecessor()


@contextlib.contextmanager
def _native_predecessor_scope_v1(read, retained):
    """Share the actual fixed owner instance, not caller verifier functions."""
    global _NATIVE_PREDECESSOR_BINDING_V1
    if (type(read) is not _NativePredecessorReadV1 or type(retained) is not RetainedInputs
            or _NATIVE_PREDECESSOR_BINDING_V1 is not None or read._retained is not None):
        raise RotationError('native predecessor reuse requires the exact existing owner and retained input types')
    read._retained = retained
    read._physical()
    path = Path(__file__).absolute()
    raw = _verify_claim_load_identity_v1()
    name = '_native_existing_claim_receiver_' + hashlib.sha256(os.fsencode(path) + b'\0' + raw).hexdigest()
    module = sys.modules.get(__name__)
    if module is None or module.__dict__ is not globals() or Path(module.__file__).absolute() != path:
        raise RotationError('existing claim module identity is unavailable')
    previous = sys.modules.get(name)
    if previous is not None and previous is not module:
        raise RotationError('native predecessor cannot substitute another existing receiver instance')
    sys.modules[name] = module
    _NATIVE_PREDECESSOR_BINDING_V1 = read
    try:
        yield read
    finally:
        _NATIVE_PREDECESSOR_BINDING_V1 = None
        read._closed = True
        read._retained = None
        if previous is None:
            sys.modules.pop(name, None)


# Proposed addition to the EXISTING claim-run-rotation.py, not a new controller.
# Never select from CLI/env/STATE/caller JSON. Existing private profile adoption
# pins its provider artifact; public accepting-core bytes contain no private
# repo/issuer/episode literal. Only the governed private pin expression may vary
# from this source-owner template. Actual episode/grant data comes AFTER OPEN.
_NATIVE_SOURCE_OWNER_TEMPLATE_SHA256 = '799d468f8a98a6990c798488517ba27f273f4862d6066a9b228ab0d1c7c6a517'
_NATIVE_PRIVATE_PROFILE_V1 = None
_NATIVE_INPUT_RESOLVED_V1 = None
_NATIVE_INPUT_BINARY_PIN_V1 = None


def _private_native_input_selection_v1(context):
    """Existing source-owned provider selection, through authenticated repo custody.

    Not used by historical canonical readers. No __file__-relative fallback and
    no caller module/path. Before executing private code, normalize only the one
    literal OWNED_STDIO_SELECTION_PIN and require the exact reviewed template.
    Retain physical producer/provider files through the live canonical CAS.
    """
    global _NATIVE_PRIVATE_PROFILE_V1
    if _NATIVE_PRIVATE_PROFILE_V1 is not None:
        repo, selected, held = _NATIVE_PRIVATE_PROFILE_V1
        if context['repo'] != repo:
            raise RotationError('private native profile cannot cross repository custody')
        for item in held:
            item.verify()
        return selected
    # Same materialized physical owner as pending/observation/export. The peer
    # is the reviewed template source, never a second executing policy owner.
    # This companion requires separate governed provisioning in the source repo.
    path = context['repo'] / 'skills/implementaudit/scripts/compaction-source-owner-codex-app.py'  # source repo owner
    if not path.exists():
        return None
    held = []
    try:
        import ast
        producer = PinnedFile(path, max_bytes=512 * 1024)
        held.append(producer)
        raw = producer.read()
        declarations = [node for node in ast.parse(raw).body if isinstance(node, ast.Assign)
                        and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                        and node.targets[0].id == 'OWNED_STDIO_SELECTION_PIN']
        if len(declarations) != 1:
            raise RotationError('private native selector is not one declared literal')
        value = declarations[0].value
        pin = ast.literal_eval(value)
        rows = raw.splitlines(keepends=True)
        start = sum(map(len, rows[:value.lineno - 1])) + value.col_offset
        end = sum(map(len, rows[:value.end_lineno - 1])) + value.end_col_offset
        normalized = raw[:start] + b'None' + raw[end:]
        if hashlib.sha256(normalized).hexdigest() != _NATIVE_SOURCE_OWNER_TEMPLATE_SHA256:
            raise RotationError('private native owner differs from the reviewed source template')
        if pin is None:
            return None
        if (type(pin) is not dict or set(pin) != {'path', 'bytes', 'sha256'}
                or type(pin['path']) is not str or not Path(pin['path']).is_absolute()
                or type(pin['bytes']) is not int or not 0 < pin['bytes'] <= 256 * 1024
                or type(pin['sha256']) is not str or not SHA256.fullmatch(pin['sha256'])):
            raise RotationError('private native provider pin is malformed')
        provider = PinnedFile(Path(pin['path']), max_bytes=256 * 1024)
        held.append(provider)
        payload = provider.read()
        if len(payload) != pin['bytes'] or hashlib.sha256(payload).hexdigest() != pin['sha256']:
            raise RotationError('private native provider differs from its governed pin')
        name = '_native_private_owner_' + hashlib.sha256(os.fsencode(path) + b'\0' + raw).hexdigest()
        module = types.ModuleType(name)
        module.__file__ = str(path)
        exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
        selected = module.rotation_input_owner_selection_v1()
        if selected is None:
            return None
        if (selected.get('producer_sha256') != hashlib.sha256(raw).hexdigest()
                or selected.get('provider_selection_sha256') != pin['sha256']):
            raise RotationError('private owner returned a different physical source or provider')
        _NATIVE_PRIVATE_PROFILE_V1 = (context['repo'], selected, tuple(held))
        held = []
        return selected
    finally:
        for item in reversed(held):
            item.close()


def native_input_revision_refs_v1(context):
    if not CONTROLLER.fullmatch(context['controller']):
        raise RotationError('invalid native input controller')
    return {'source': 'refs/implementaudit/rotation-input-sources/' + context['controller'],
            'grant': 'refs/implementaudit/rotation-input-grants/' + context['controller']}


def native_process_identity_v1(pid):
    """Kernel PID/birth/image/liveness, never a PID or JSON assertion alone.

    This exact proposed producer is Windows-only. A different platform requires
    an independently qualified process-custody implementation.
    """
    if os.name != 'nt' or type(pid) is not int or pid <= 0:
        raise RotationError('native input process custody is unsupported')
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.GetProcessTimes.argtypes = (wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4))
    kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    kernel.QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                 ctypes.POINTER(wintypes.DWORD))
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        raise RotationError('selected native producer process is absent')
    try:
        times = [wintypes.FILETIME() for _ in range(4)]
        code = wintypes.DWORD()
        size = wintypes.DWORD(32768)
        image = ctypes.create_unicode_buffer(size.value)
        if (not kernel.GetProcessTimes(handle, *[ctypes.byref(value) for value in times])
                or not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != 259
                or not kernel.QueryFullProcessImageNameW(handle, 0, image, ctypes.byref(size))):
            raise RotationError('selected native producer process custody failed')
        return {'pid': pid, 'creation_filetime': (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime,
                'image': str(Path(image.value).resolve(strict=True))}
    finally:
        kernel.CloseHandle(handle)


def _native_selection_v1(context):
    selected = _private_native_input_selection_v1(context)
    required = {'repo', 'controller', 'claim_id', 'run_root_identity', 'issuer', 'source_owner',
                'source_contract_sha256', 'provider_selection_sha256',
                'producer_sha256', 'owner_decision_locator'}
    if selected is None:
        raise RotationError('NATIVE_INPUT_EXISTING_OWNER_SELECTION_ABSENT')
    if (type(selected) is not dict or type(selected.get('repo')) is not str
            or not Path(selected['repo']).is_absolute()
            or str(Path(selected['repo'])) != selected['repo']
            or any(part in {'.', '..'} for part in selected['repo'].replace('\\', '/').split('/'))
            or str(Path(selected['repo']).resolve(strict=True)) != selected['repo']):
        raise RotationError('native input repository spelling must be exact canonical absolute custody')
    if (type(selected) is not dict or set(selected) != required
            or any(type(value) is not str or not value for value in selected.values())
            or Path(selected['repo']).resolve(strict=True) != context['repo'].resolve(strict=True)
            or any(selected[key] != context[key] for key in ('controller', 'claim_id', 'run_root_identity'))
            or any(not SHA256.fullmatch(selected[key]) for key in
                   ('source_contract_sha256', 'provider_selection_sha256', 'producer_sha256'))):
        raise RotationError('native input fixed owner selection does not match the actual claim')
    return selected


def _hold_native_input_image_v1(image_path, expected_sha256):
    global _NATIVE_INPUT_BINARY_PIN_V1
    if _NATIVE_INPUT_BINARY_PIN_V1 is None:
        held = PinnedFile(image_path, max_bytes=512 * 1024 * 1024)
        try:
            if native_held_image_sha256_v1(held) != expected_sha256:
                raise RotationError('actual native process image differs from the admitted binary')
        except BaseException:
            held.close()
            raise
        _NATIVE_INPUT_BINARY_PIN_V1 = held
    if _NATIVE_INPUT_BINARY_PIN_V1.path != image_path:
        raise RotationError('selected native process image path changed')
    _NATIVE_INPUT_BINARY_PIN_V1.verify()


# Inert scheduling in the EXISTING input-source namespace. No input/currentness
# authority exists until the unchanged source/grant/lease/publisher gates pass.
_NATIVE_PREPARATION_SCHEMA_V1 = 'implementaudit.native-input-preparation.v1'
_NATIVE_PREPARATION_WAIT_MS = 30000
_NATIVE_PREPARATION_CONSUMER_V1 = None
_NATIVE_PREPARATION_PRODUCER_V1 = None
import threading as _native_preparation_threading
_NATIVE_PREPARATION_SLOT_V1 = _native_preparation_threading.RLock()
_NATIVE_PREPARATION_KEYS_V1 = {'schema', 'phase', 'reservation_id', 'selection',
    'consumer_sha256', 'producer_process', 'host_process',
    'cancellation', 'created_wall_ms', 'created_monotonic_ns',
    'deadline_wall_ms', 'deadline_monotonic_ns', 'prior_grant_oid', 'previous_response_id'}
_NATIVE_PREPARATION_REQUEST_KEYS_V1 = {'registration_oid', 'executor', 'subject',
    'source_bytes', 'source_tokens', 'prepared_wall_ms', 'prepared_monotonic_ns'}
_NATIVE_PREPARATION_SOURCE_KEYS_V1 = {'registration_oid', 'request_oid', 'executor',
    'consumer_sha256', 'prepared_wall_ms', 'prepared_monotonic_ns',
    'observation_after_wall_ms', 'observation_after_monotonic_ns', 'previous_response_id'}


def _native_preparation_clock_v1():
    return time.time_ns() // 1000000, time.monotonic_ns()


def _native_preparation_process_v1(value):
    if (type(value) is not dict or set(value) != {'pid', 'creation_filetime', 'image'}
            or type(value['pid']) is not int or value['pid'] <= 0
            or type(value['creation_filetime']) is not int or value['creation_filetime'] <= 0
            or type(value['image']) is not str or not Path(value['image']).is_absolute()
            or native_process_identity_v1(value['pid']) != value):
        raise RotationError('native preparation process is foreign, dead or reused')


def _native_preparation_read_v1(context, oid):
    raw = read_blob(context['repo'], oid)
    if len(raw) > 16384:
        raise RotationError('native preparation record exceeds its bound')
    return decode_json(raw)


def _native_preparation_heads_v1(context, refs):
    # Cooperate with the existing writer gate; never retry a failed custody read.
    with namespace_gate(context):
        return read_refs(context['repo'], refs)


def _native_preparation_validate_v1(context, record, selected, *, requested=False):
    expected = _NATIVE_PREPARATION_KEYS_V1 | (_NATIVE_PREPARATION_REQUEST_KEYS_V1 if requested else set())
    if (type(record) is not dict or set(record) != expected
            or record['schema'] != _NATIVE_PREPARATION_SCHEMA_V1
            or record['phase'] != ('REQUESTED' if requested else 'REGISTERED')
            or record['selection'] != selected
            or type(record['reservation_id']) is not str or not re.fullmatch('[0-9a-f]{32}', record['reservation_id'])
            or record['consumer_sha256'] != hashlib.sha256(_verify_claim_load_identity_v1()).hexdigest()
            or record['prior_grant_oid'] is not None and (type(record['prior_grant_oid']) is not str
                or not OID.fullmatch(record['prior_grant_oid']))
            or record['previous_response_id'] is not None and (type(record['previous_response_id']) is not str
                or re.fullmatch('resp_[A-Za-z0-9_-]+', record['previous_response_id']) is None)):
        raise RotationError('native preparation source, profile, code or record differs')
    _native_preparation_process_v1(record['producer_process'])
    _native_preparation_process_v1(record['host_process'])
    for key in ('created_wall_ms', 'created_monotonic_ns', 'deadline_wall_ms', 'deadline_monotonic_ns'):
        if type(record[key]) is not int or record[key] < 0:
            raise RotationError('native preparation scheduling clock is malformed')
    wall, mono = _native_preparation_clock_v1()
    if (record['deadline_wall_ms'] - record['created_wall_ms'] != _NATIVE_PREPARATION_WAIT_MS
            or record['deadline_monotonic_ns'] - record['created_monotonic_ns'] != _NATIVE_PREPARATION_WAIT_MS * 1000000
            or not record['created_wall_ms'] <= wall <= record['deadline_wall_ms']
            or not record['created_monotonic_ns'] <= mono <= record['deadline_monotonic_ns']):
        raise RotationError('native preparation scheduling interval expired or changed')
    cancel = record['cancellation']
    if (type(cancel) is not dict or set(cancel) != {'schema', 'producer_process', 'event_handle', 'reservation_id'}
            or cancel['schema'] != 'implementaudit.native-cancellation.v1'
            or cancel['producer_process'] != record['producer_process']
            or cancel['reservation_id'] != record['reservation_id']
            or type(cancel['event_handle']) is not int or not 0 < cancel['event_handle'] < 2**64):
        raise RotationError('native preparation event ownership differs')
    if requested:
        _native_preparation_process_v1(record['executor'])
        if (type(record['registration_oid']) is not str or not OID.fullmatch(record['registration_oid'])
                or type(record['subject']) is not dict
                or set(record['subject']) != {'controller', 'claim_id', 'run_root_identity',
                                               'receipt_token', 'state_sha256', 'roadmap_sha256'}
                or any(record['subject'][key] != context[key] for key in ('controller', 'claim_id', 'run_root_identity'))
                or any(type(value) is not str or not 0 < len(value) <= 1024 for value in record['subject'].values())
                or any(type(record[key]) is not int or not 0 <= record[key] <= 2**63 - 1
                       for key in ('source_bytes', 'source_tokens'))
                or type(record['prepared_wall_ms']) is not int or type(record['prepared_monotonic_ns']) is not int
                or not record['created_wall_ms'] <= record['prepared_wall_ms'] <= wall
                or not record['created_monotonic_ns'] <= record['prepared_monotonic_ns'] <= mono):
            raise RotationError('native preparation request binding is malformed')


def _native_preparation_cancel_record_v1(context, owned_oids):
    ref = native_input_revision_refs_v1(context)['source']
    with _CUSTODY.git_scope(context['repo'], fixed_git(), git_environment()):
        old = read_ref(context['repo'], ref)
        if old is None or old not in owned_oids:
            return  # Never overwrite READY/CLAIMED or another owner's record.
        record = _native_preparation_read_v1(context, old)
        if record.get('schema') != _NATIVE_PREPARATION_SCHEMA_V1 or record.get('phase') not in {'REGISTERED', 'REQUESTED'}:
            return
        oid = write_blob(context, canonical(dict(record, phase='CANCELLED')))
        update_refs(context, {ref: (oid, old)}, {})  # Inert denial; no archive/epoch refs.


class NativeInputPreparationV1:
    """Owned producer's one-shot scheduling capability; never an input/grant.

    The selected source observes an already-running or independently scheduled
    legitimate host turn. This rendezvous NEVER starts a model/API turn.
    This object can register, receive one prepared request and constrain a later
    genuine source. It cannot manufacture a NativeInputState or extend a grant.
    """
    def __init__(self, context, host_process):
        self.context, self.selected = context, dict(_native_selection_v1(context))
        if (type(host_process) is not subprocess.Popen or host_process.poll() is not None
                or host_process.stdin is None or host_process.stdout is None):
            raise RotationError('native preparation requires the existing live owned host')
        import secrets
        self.reservation_id = secrets.token_hex(16)
        self.host = native_process_identity_v1(host_process.pid)
        self.producer = native_process_identity_v1(os.getpid())
        self.cancellation = NativeCancellationSignalV1(self.reservation_id)
        self.registration = self.registration_oid = self.request = self.request_oid = None
        self.accepted_at = None
        self._bound = self._closed = False
        self._bound_source = None
        self._producer = None
        self._lock = _native_preparation_threading.RLock()

    def _check(self):
        self.cancellation.check()
        if self._closed or _native_selection_v1(self.context) != self.selected:
            raise RotationError('native preparation is closed or selection changed')
        _native_preparation_process_v1(self.producer)
        _native_preparation_process_v1(self.host)
        if self.registration is not None:
            _native_preparation_validate_v1(self.context, self.registration, self.selected)
        if self._producer is not None:
            self._producer.check()

    def register(self):
        global _NATIVE_PREPARATION_PRODUCER_V1
        with self._lock:
            try:
                with _NATIVE_PREPARATION_SLOT_V1:
                    if _NATIVE_PREPARATION_PRODUCER_V1 not in (None, self):
                        raise RotationError('another producer preparation is active')
                    _NATIVE_PREPARATION_PRODUCER_V1 = self
                return self._register()
            except BaseException:
                self.cancel_now()
                raise

    def _register(self):
        self._check()
        if self.registration is not None:
            raise RotationError('native preparation registration cannot be replayed')
        refs = native_input_revision_refs_v1(self.context)
        with _CUSTODY.git_scope(self.context['repo'], fixed_git(), git_environment()):
            previous = _native_preparation_heads_v1(self.context, refs.values())
            old = previous[refs['source']]
            response = None
            if old is not None:
                value = decode_json(read_blob(self.context['repo'], old))
                resolved = value.get('phase') == 'CLOSED' and value.get('resolution', {}).get('status') == 'EXACT_CANONICAL_JOIN_VERIFIED'
                if (value.get('schema') not in {'implementaudit.native-rotation-source.v3', 'implementaudit.native-rotation-source.v4'}
                        or value.get('phase') not in {'REVOKED', 'CLOSED'}
                        or 'transaction_id' in value and not resolved):
                    raise RotationError('prior native source or preparation requires owner reconciliation')
                response = value.get('exact_usage', {}).get('response_id')
            wall, mono = _native_preparation_clock_v1()
            record = {'schema': _NATIVE_PREPARATION_SCHEMA_V1, 'phase': 'REGISTERED',
                'reservation_id': self.reservation_id, 'selection': dict(self.selected),
                'consumer_sha256': hashlib.sha256(_verify_claim_load_identity_v1()).hexdigest(),
                'producer_process': self.producer, 'host_process': self.host,
                'cancellation': self.cancellation.descriptor,
                'created_wall_ms': wall, 'created_monotonic_ns': mono,
                'deadline_wall_ms': wall + _NATIVE_PREPARATION_WAIT_MS,
                'deadline_monotonic_ns': mono + _NATIVE_PREPARATION_WAIT_MS * 1000000,
                'prior_grant_oid': previous[refs['grant']], 'previous_response_id': response}
            _native_preparation_validate_v1(self.context, record, self.selected)
            if len(canonical(record)) > 16384:
                raise RotationError('native preparation registration exceeds its bound')
            self.registration = record  # Sticky before any potentially issued write.
            oid = write_blob(self.context, canonical(record))
            self.registration_oid = oid
            updates = {refs['source']: (oid, old)}  # No canonical archive/epoch before input.
            update_refs(self.context, updates, {refs['grant']: previous[refs['grant']],
                self.context['controller_ref']: self.context['controller_oid']})
        return {'status': 'INERT_REGISTERED_NO_INPUT_OR_CURRENTNESS', 'reservation_id': self.reservation_id}

    def wait_request(self):
        with self._lock:
            return self._wait_request()

    def _wait_request(self):
        if self.registration is None or self.request is not None or self.accepted_at is not None:
            raise RotationError('native preparation request is absent or already consumed')
        try:
            while True:
                self._check()
                _native_preparation_validate_v1(self.context, self.registration, self.selected)
                refs = native_input_revision_refs_v1(self.context)
                heads = _native_preparation_heads_v1(self.context, refs.values())
                if heads[refs['source']] != self.registration_oid:
                    break
                if heads[refs['grant']] != self.registration['prior_grant_oid']:
                    raise RotationError('native preparation prior grant changed before request')
                time.sleep(.01)
            request = _native_preparation_read_v1(self.context, heads[refs['source']])
            _native_preparation_validate_v1(self.context, request, self.selected, requested=True)
            if (request['registration_oid'] != self.registration_oid
                    or {key: request[key] for key in _NATIVE_PREPARATION_KEYS_V1} != dict(self.registration, phase='REQUESTED')
                    or heads[refs['grant']] != self.registration['prior_grant_oid']):
                raise RotationError('native preparation request or prior grant was substituted')
            self.request, self.request_oid = request, heads[refs['source']]
            self.accepted_at = _native_preparation_clock_v1()
            return {'status': 'INERT_REQUEST_OBSERVED_NO_INPUT_OR_CURRENTNESS',
                    'action': 'AWAIT_INDEPENDENT_FRESH_EVENT_NEVER_START_MODEL_OR_API_TURN',
                    'subject': dict(request['subject']), 'source_bytes': request['source_bytes'],
                    'source_tokens': request['source_tokens'], 'executor': dict(request['executor'])}
        except BaseException:
            self.cancel_now()
            raise

    def source_parts(self, native_state, grant):
        with self._lock:
            try:
                return self._source_parts(native_state, grant)
            except BaseException:
                self.cancel_now()
                raise

    def _source_parts(self, native_state, grant):
        self._check()
        if self.request is None or self.accepted_at is None or self._bound:
            raise RotationError('native preparation has no unused actual request')
        _native_preparation_process_v1(self.request['executor'])
        self._bound = True  # A refused observation cannot retry this rendezvous.
        binding, exact, window = native_state._binding, native_state._snapshot, native_state._reported_window
        wall, mono = self.accepted_at
        if (binding['subject'] != self.request['subject']
                or (binding['source_bytes'], binding['source_tokens']) != (self.request['source_bytes'], self.request['source_tokens'])
                or exact is None or window is None
                or exact['received_at_unix_ms'] <= wall or native_state._received_monotonic_ns <= mono
                or window['received_at_unix_ms'] <= wall or window['received_monotonic_ns'] <= mono
                or exact['response_id'] == self.registration['previous_response_id']
                or type(grant.get('not_before_unix_ms')) is not int
                or type(grant.get('expires_at_unix_ms')) is not int
                or not wall <= grant['not_before_unix_ms'] < grant['expires_at_unix_ms'] <= grant['not_before_unix_ms'] + 30000):
            self.cancel_now()
            raise RotationError('native preparation requires a new raw/window and fresh unchanged grant after request')
        return self.reservation_id, self.cancellation

    def bind_source(self, snapshot):
        self._check()
        if not self._bound or self.request is None or self.accepted_at is None or self._bound_source is not None:
            raise RotationError('native preparation source is not bound')
        metadata = {key: self.request[key] for key in
                    ('registration_oid', 'executor', 'consumer_sha256', 'prepared_wall_ms', 'prepared_monotonic_ns')}
        metadata.update(request_oid=self.request_oid, observation_after_wall_ms=self.accepted_at[0],
                        observation_after_monotonic_ns=self.accepted_at[1],
                        previous_response_id=self.registration['previous_response_id'])
        value = dict(snapshot, schema='implementaudit.native-rotation-source.v4', preparation=metadata)
        self._bound_source = canonical(value)
        return value

    def check_publish(self, heads):
        self._check()
        _native_preparation_process_v1(self.request['executor'])
        refs = native_input_revision_refs_v1(self.context)
        if (heads != {refs['source']: self.request_oid, refs['grant']: self.registration['prior_grant_oid']}
                or _native_preparation_read_v1(self.context, self.request_oid) != self.request):
            raise RotationError('native preparation request changed before READY')

    def cancel_now(self):
        if self.cancellation.handle is not None:
            self.cancellation.signal()

    def close(self):
        global _NATIVE_PREPARATION_PRODUCER_V1
        if self._closed:
            return
        try:
            self.cancel_now()
            _native_preparation_cancel_record_v1(self.context, {self.registration_oid, self.request_oid})
        finally:
            self._closed = True
            self.cancellation.close()
            with _NATIVE_PREPARATION_SLOT_V1:
                if _NATIVE_PREPARATION_PRODUCER_V1 is self:
                    _NATIVE_PREPARATION_PRODUCER_V1 = None


def native_preparation_for_owned_stdio_v1(runtime, producer, context, source_path):
    """Thin selected-source entry; schedules no native/model/API operation."""
    selected = _native_selection_v1(context)
    expected = context['repo'] / 'skills/implementaudit/scripts/compaction-source-owner-codex-app.py'  # source repo: private native source owner
    if (Path(source_path).absolute() != expected or type(runtime) is not tuple or len(runtime) != 5
            or _NATIVE_PRIVATE_PROFILE_V1 is None
            or json.loads(_NATIVE_PRIVATE_PROFILE_V1[2][1].read()) != runtime[0]):
        raise RotationError('preparation requires the actual selected live source owner')
    provider = runtime[0]
    dependencies = provider.get('producer_dependencies', {})
    pins = {'runner': provider.get('capture_producer_pin'),
        **{key: dependencies.get(name) for key, name in
           (('loop', 'owned_stdio_loop.py'), ('claim', 'claim-run-rotation.py'),
            ('helper', 'bounded_source_owner.py'), ('source_owner', 'compaction-source-owner-codex-app.py'))}}
    # The selected executing owner and the unselected producer copy are distinct
    # existing roles. Bind both to their held provider pins, never a caller path.
    if (any(type(pin) is not dict for pin in pins.values()) or producer.pins != pins
            or type(producer.claim) is not types.ModuleType
            or producer.claim.__dict__ is not globals()
            or producer.loop._live_producer is not producer
            or producer.producer_identity != native_process_identity_v1(os.getpid())
            or pins['source_owner']['sha256'] != _NATIVE_SOURCE_OWNER_TEMPLATE_SHA256
            or hashlib.sha256(_NATIVE_PRIVATE_PROFILE_V1[2][0].read()).hexdigest() != selected['producer_sha256']):
        raise RotationError('native preparation producer differs from its selected dependency closure')
    producer.check()  # Existing loaded-code/process/source custody; no send.
    result = NativeInputPreparationV1(context, producer.process)
    result._producer = producer
    return result


def _native_preparation_producer_v1(context):
    current = _NATIVE_PREPARATION_PRODUCER_V1
    if current is not None and (type(current) is not NativeInputPreparationV1 or current.context != context or current._closed):
        raise RotationError('native preparation belongs to another owner/context')
    return current


def native_rotation_parts_v1(context, state, grant):
    current = _native_preparation_producer_v1(context)
    if current is not None:
        return current.source_parts(state, grant)
    import secrets
    identity = secrets.token_hex(16)
    return identity, NativeCancellationSignalV1(identity)


def bind_native_preparation_v1(context, snapshot):
    current = _native_preparation_producer_v1(context)
    return current.bind_source(snapshot) if current is not None else snapshot


def native_preparation_prior_v1(context, heads):
    current = _native_preparation_producer_v1(context)
    if current is None:
        return False
    current.check_publish(heads)
    return True


def _native_preparation_source_v1(context, source, grant):
    value = source['preparation']
    if (type(value) is not dict or set(value) != _NATIVE_PREPARATION_SOURCE_KEYS_V1
            or any(type(value[key]) is not str or not OID.fullmatch(value[key]) for key in ('registration_oid', 'request_oid'))
            or value['consumer_sha256'] != grant['consumer_sha256']
            or any(type(value[key]) is not int or value[key] < 0 for key in
                ('prepared_wall_ms', 'prepared_monotonic_ns', 'observation_after_wall_ms', 'observation_after_monotonic_ns'))
            or value['observation_after_wall_ms'] < value['prepared_wall_ms']
            or value['observation_after_monotonic_ns'] < value['prepared_monotonic_ns']
            or value['previous_response_id'] is not None and (type(value['previous_response_id']) is not str
                or re.fullmatch('resp_[A-Za-z0-9_-]+', value['previous_response_id']) is None)
            or source['exact_usage']['received_at_unix_ms'] <= value['observation_after_wall_ms']
            or source['observed_monotonic_ns'] <= value['observation_after_monotonic_ns']
            or source['reported_window']['received_at_unix_ms'] <= value['observation_after_wall_ms']
            or source['reported_window']['received_monotonic_ns'] <= value['observation_after_monotonic_ns']
            or source['exact_usage']['response_id'] == value['previous_response_id']
            or type(grant['not_before_unix_ms']) is not int or type(grant['expires_at_unix_ms']) is not int
            or not value['observation_after_wall_ms'] <= grant['not_before_unix_ms']
                < grant['expires_at_unix_ms'] <= grant['not_before_unix_ms'] + 30000):
        raise RotationError('prepared native source is not strictly newer than its actual request')
    _native_preparation_process_v1(value['executor'])


class _NativePreparationConsumerV1:
    def __init__(self, context, read, retained, subject, source_bytes, source_tokens):
        if (type(read) is not _NativePredecessorReadV1 or _NATIVE_PREDECESSOR_BINDING_V1 is not read
                or read._retained is not retained or type(retained) is not RetainedInputs
                or read._context != context):
            raise RotationError('native preparation requires the actual local retained predecessor')
        self.context, self.read, self.retained = context, read, retained
        self.subject, self.counts = dict(subject), (source_bytes, source_tokens)
        self.selected = dict(_native_selection_v1(context))
        self.request_oid = None
        self.registration_oid = None
        self.ready_heads = None
        self.cancel = None
        self.closed = False

    def verify(self):
        if self.closed or _native_selection_v1(self.context) != self.selected:
            raise RotationError('native preparation consumer closed or source/profile changed')
        self.retained.verify()
        self.read.verify()
        if projection_helper()._native_subject(self.read.predecessor()) != self.subject:
            raise RotationError('native preparation canonical subject changed')

    def request_and_wait(self, record, heads):
        self.verify()
        refs = native_input_revision_refs_v1(self.context)
        _native_preparation_validate_v1(self.context, record, self.selected)
        if heads[refs['grant']] != record['prior_grant_oid']:
            raise RotationError('native preparation prior grant changed')
        self.registration, self.registration_oid = record, heads[refs['source']]
        self.cancel = NativeCancellationWaitV1(record['cancellation'], record['producer_process'], record['reservation_id'])
        # Existing retained-image pinning is source-independent for this exact
        # already-live host. Later process/path/custody checks remain unchanged.
        native = projection_helper().native_inputs_module_v1()
        _hold_native_input_image_v1(Path(record['host_process']['image']), native.NATIVE_BINARY_SHA256)
        self.verify()
        wall, mono = _native_preparation_clock_v1()
        request = dict(record, phase='REQUESTED', registration_oid=self.registration_oid,
            executor=native_process_identity_v1(os.getpid()), subject=self.subject,
            source_bytes=self.counts[0], source_tokens=self.counts[1],
            prepared_wall_ms=wall, prepared_monotonic_ns=mono)
        _native_preparation_validate_v1(self.context, request, self.selected, requested=True)
        self.request = request
        self.request_oid = write_blob(self.context, canonical(request))
        updates = {refs['source']: (self.request_oid, self.registration_oid)}
        guards = predecessor_guards(self.context, self.read.predecessor())
        guards[refs['grant']] = record['prior_grant_oid']
        self.cancel.check()
        update_refs(self.context, updates, guards)
        # The durable inert CAS is the notification; no foreign Event is writable.
        while True:
            self.cancel.check()
            _native_preparation_validate_v1(self.context, record, self.selected)
            current = _native_preparation_heads_v1(self.context, refs.values())
            # A gate/OS call may return after the scheduling deadline. Its wait
            # never renews eligibility or any later source/grant freshness clock.
            _native_preparation_validate_v1(self.context, record, self.selected)
            if current[refs['source']] == self.request_oid:
                if current[refs['grant']] != record['prior_grant_oid']:
                    raise RotationError('native preparation grant changed before READY')
                time.sleep(.01)
                continue
            source = decode_json(read_blob(self.context['repo'], current[refs['source']]))
            if (type(source) is not dict or source.get('schema') != 'implementaudit.native-rotation-source.v4'
                    or source.get('phase') != 'READY' or current[refs['grant']] is None):
                raise RotationError('native preparation request was replaced without prepared READY')
            grant = decode_json(read_blob(self.context['repo'], current[refs['grant']]))
            self.ready_heads = current
            self.verify_ready(source, grant, current)
            self.verify()  # Local canonical recheck; JSON supplied no read authority.
            _native_preparation_validate_v1(self.context, record, self.selected)
            return

    def verify_ready(self, source, grant, heads):
        self.cancel.check()
        value = source.get('preparation')
        if (source.get('schema') != 'implementaudit.native-rotation-source.v4' or source.get('phase') != 'READY'
                or source.get('reservation_id') != self.registration['reservation_id']
                or source.get('producer_process') != self.registration['producer_process']
                or source.get('host_process') != self.registration['host_process']
                or source.get('cancellation') != self.registration['cancellation']
                or type(value) is not dict or value.get('request_oid') != self.request_oid
                or value.get('registration_oid') != self.registration_oid
                or value.get('executor') != self.request['executor']
                or value.get('previous_response_id') != self.registration['previous_response_id']
                or any(value.get(key) != self.request[key] for key in ('consumer_sha256','prepared_wall_ms','prepared_monotonic_ns'))
                or source.get('binding', {}).get('subject') != self.subject
                or (source['binding'].get('source_bytes'), source['binding'].get('source_tokens')) != self.counts
                or self.ready_heads != heads):
            raise RotationError('native preparation READY is foreign, replaced or replayed')
        _native_preparation_source_v1(self.context, source, grant)

    def close(self, failed):
        if self.closed:
            return
        self.closed = True
        try:
            if failed and self.request_oid is not None:
                _native_preparation_cancel_record_v1(self.context, {self.request_oid})
        finally:
            if self.cancel is not None:
                self.cancel.close()


@contextlib.contextmanager
def _native_preparation_scope_v1(context, read, retained, subject, source_bytes, source_tokens):
    global _NATIVE_PREPARATION_CONSUMER_V1
    if _NATIVE_PREPARATION_CONSUMER_V1 is not None:
        raise RotationError('native preparation consumer cannot be nested or replayed')
    selected = _native_selection_v1(context)
    refs = native_input_revision_refs_v1(context)
    heads = _native_preparation_heads_v1(context, refs.values())
    if heads[refs['source']] is None:
        raise RotationError('native input source or inert preparation is absent')
    record = decode_json(read_blob(context['repo'], heads[refs['source']]))
    if record.get('schema') == 'implementaudit.native-rotation-source.v3' and record.get('phase') == 'READY':
        yield None  # Legacy immediate READY retains ALL existing freshness gates.
        return
    _native_preparation_validate_v1(context, record, selected)
    consumer = _NativePreparationConsumerV1(context, read, retained, subject, source_bytes, source_tokens)
    failed = True
    try:
        consumer.request_and_wait(record, heads)
        _NATIVE_PREPARATION_CONSUMER_V1 = consumer
        yield consumer
        failed = False
    finally:
        _NATIVE_PREPARATION_CONSUMER_V1 = None
        consumer.close(failed)


def _native_preparation_require_consumer_v1(context, source, grant, heads, *, claimed=False):
    if source.get('schema') != 'implementaudit.native-rotation-source.v4':
        return
    current = _NATIVE_PREPARATION_CONSUMER_V1
    if (type(current) is not _NativePreparationConsumerV1 or current.closed or current.context != context
            or source['reservation_id'] != current.registration['reservation_id']
            or source['preparation']['request_oid'] != current.request_oid
            or source['preparation']['executor'] != native_process_identity_v1(os.getpid())):
        raise RotationError('prepared native input requires its actual one-shot local consumer')
    current.cancel.check()
    if claimed:
        refs = native_input_revision_refs_v1(context)
        if (source.get('ready_oid') != current.ready_heads[refs['source']]
                or heads[refs['grant']] != current.ready_heads[refs['grant']]
                or source.get('executor') != current.request['executor']):
            raise RotationError('prepared native input claim changed its original consumer or READY')
    else:
        current.verify_ready(source, grant, heads)
        current.verify()



def _validate_native_revision_v1(context, source, grant, native, *, claimed=False):
    """Consume an already-admitted owner's revision; hashes do not mint authority."""
    selected = _native_selection_v1(context)
    prepared_source = type(source) is dict and source.get('schema') == 'implementaudit.native-rotation-source.v4'
    base = {'schema', 'phase', 'binding', 'exact_usage', 'reported_window', 'cutoff_revision',
            'observed_monotonic_ns', 'reservation_id', 'producer_process', 'host_process',
            'source_owner', 'source_contract_sha256', 'provider_selection_sha256', 'episode_binding_sha256',
            'cancellation'}
    if (type(source) is not dict or set(source) != base | ({'preparation'} if prepared_source else set()) | ({'executor', 'transaction_id', 'ready_oid'} if claimed else set())
            or source['schema'] != ('implementaudit.native-rotation-source.v4' if prepared_source else 'implementaudit.native-rotation-source.v3')
            or source['phase'] != ('CLAIMED' if claimed else 'READY')
            or type(source['reservation_id']) is not str or not re.fullmatch('[0-9a-f]{32}', source['reservation_id'])
            or any(source[key] != selected[key] for key in
                   ('source_owner', 'source_contract_sha256', 'provider_selection_sha256'))):
        raise RotationError('native input source is absent, foreign, revoked, or already consumed')
    binding, exact = source['binding'], source['exact_usage']
    native._validate_binding(binding)
    grant_fields = {'schema', 'status', 'issuer', 'source_owner', 'source_contract_sha256',
                    'provider_selection_sha256', 'episode_binding_sha256', 'producer_sha256',
                    'consumer_sha256', 'subject', 'host', 'budget_policy', 'tokenizer',
                    'not_before_unix_ms', 'expires_at_unix_ms', 'owner_decision_locator'}
    if (type(grant) is not dict or set(grant) != grant_fields
            or grant['schema'] != 'implementaudit.native-rotation-owner-grant.v1' or grant['status'] != 'ACTIVE'
            or any(grant[key] != selected[key] for key in
                   ('issuer', 'source_owner', 'source_contract_sha256', 'provider_selection_sha256',
                    'producer_sha256', 'owner_decision_locator'))
            or type(grant['episode_binding_sha256']) is not str or not SHA256.fullmatch(grant['episode_binding_sha256'])
            or source['episode_binding_sha256'] != grant['episode_binding_sha256']
            or grant['consumer_sha256'] != hashlib.sha256(read_regular(Path(__file__).absolute())).hexdigest()
            or any(grant[key] != binding[key] for key in ('issuer', 'producer_sha256', 'subject', 'host', 'budget_policy', 'tokenizer'))
            or binding['semantic_contract_sha256'] != selected['source_contract_sha256']
            or binding['grant_sha256'] != hashlib.sha256(canonical(grant)).hexdigest()):
        raise RotationError('actual native source, issuer grant, semantics, or consumer code differ')
    if prepared_source:
        _native_preparation_source_v1(context, source, grant)
    now_wall, now_mono = time.time_ns() // 1000000, time.monotonic_ns()
    if (type(grant['not_before_unix_ms']) is not int or type(grant['expires_at_unix_ms']) is not int
            or not grant['not_before_unix_ms'] <= now_wall <= grant['expires_at_unix_ms']
            or type(source['observed_monotonic_ns']) is not int
            or not 0 <= now_mono - source['observed_monotonic_ns'] <= 30000000000):
        raise RotationError('native source monotonic cutoff or issuer grant is not current')
    parsed = native.parse_exact_usage_v1({'method': 'rawResponse/completed', 'params': {
        'threadId': exact['thread_id'], 'turnId': exact['turn_id'], 'responseId': exact['response_id'],
        'usage': exact['usage']}}, binding['thread_id'], binding['turn_id'], exact['received_at_unix_ms'], exact['stream_revision'])
    if (parsed != exact or type(source['cutoff_revision']) is not int
            or source['cutoff_revision'] <= exact['stream_revision']
            or not 0 <= now_wall - exact['received_at_unix_ms'] <= min(30000, binding['budget_policy']['maximum_age_ms'])):
        raise RotationError('native exact-event cutoff is stale, future or unbound')
    native.validate_reported_window_v1(source['reported_window'], binding, exact, source['cutoff_revision'])
    if not source['observed_monotonic_ns'] <= source['reported_window']['received_monotonic_ns'] <= now_mono:
        raise RotationError('native reported window has a foreign receipt clock')
    for key in ('producer_process', 'host_process'):
        record = source[key]
        if type(record) is not dict or set(record) != {'pid', 'creation_filetime', 'image'} or native_process_identity_v1(record['pid']) != record:
            raise RotationError('native source process died, changed or was reused')
    _hold_native_input_image_v1(Path(source['host_process']['image']), binding['host']['binary_sha256'])
    if claimed and (source['executor'] != native_process_identity_v1(os.getpid())
                    or not re.fullmatch('[0-9a-f]{32}', source['transaction_id']) or not OID.fullmatch(source['ready_oid'])):
        raise RotationError('native input consumption belongs to a different or interrupted executor')


def prepare_native_source_update_v1(context, snapshot, grant, *, expected_source_oid, expected_grant_oid):
    """Pure plan for the EXISTING claim writer, after actual source/issuer verification.

    Called only by the admitted owned-stdio source owner, not exposed as a caller
    JSON CLI. READY comes from the actual reader callback; REVOKED is published
    before any dispatch/injection and on disconnect/finally. Old objects remain
    under the existing retained-object anchors. No new storage service is added.
    """
    refs = native_input_revision_refs_v1(context)
    if (type(snapshot) is not dict or snapshot.get('schema') not in {'implementaudit.native-rotation-source.v3', 'implementaudit.native-rotation-source.v4'}
            or snapshot.get('phase') not in {'READY', 'REVOKED', 'CLOSED'}
            or type(grant) is not dict or grant.get('schema') != 'implementaudit.native-rotation-owner-grant.v1'
            or any(value is not None and not OID.fullmatch(value) for value in (expected_source_oid, expected_grant_oid))):
        raise RotationError('native source revision plan is malformed')
    raw, grant_raw = canonical(snapshot), canonical(grant)
    oid = lambda value: hashlib.sha1(b'blob ' + str(len(value)).encode() + b'\0' + value).hexdigest()
    return {'source_bytes': raw, 'grant_bytes': grant_raw,
            'updates': {refs['source']: (oid(raw), expected_source_oid), refs['grant']: (oid(grant_raw), expected_grant_oid)},
            'authority_ceiling': 'INERT_OWNER_UPDATE_PLAN_NO_ADMISSION'}


def reconcile_native_publication_v1(context, reservation_id):
    """Close only a real exact canonical JOIN; absent/partial F2-F5 is STOP.

    Never overwrites an archive, turns CLAIMED back into READY, infers success
    from child exit, or invents a recovery generation. A failed read leaves the
    one-shot consumption intact for the existing owner's manual reconciliation.
    """
    _native_selection_v1(context)
    refs = native_input_revision_refs_v1(context)
    source_oid = read_ref(context['repo'], refs['source'])
    source = decode_json(read_blob(context['repo'], source_oid))
    if (source.get('reservation_id') != reservation_id or 'transaction_id' not in source
            or source.get('phase') not in {'CLAIMED', 'REVOKED'}):
        raise RotationError('native reservation has no exact issued consumption to reconcile')
    joined = require_current_generation_join_v1(context)
    observation = joined.get('archive_manifest', {}).get('native_input', {}).get('observation')
    if (type(observation) is not dict
            or any(observation.get(key) != value for key, value in source['binding'].items())
            or observation.get('exact_usage') != source['exact_usage']
            or observation.get('reported_window') != source.get('reported_window')
            or observation.get('cutoff_revision') != source['cutoff_revision']):
        raise RotationError('STOP_NATIVE_SOURCE_CLAIM_HAS_NO_EXACT_ACCEPTED_PUBLICATION')
    resolved = dict(source, phase='CLOSED', resolution={
        'status': 'EXACT_CANONICAL_JOIN_VERIFIED', 'pointer_oid': joined['pointer_oid'],
        'receipt_token': joined['receipt_token'], 'epoch_oid': joined['epoch_oid'],
        'authority_ceiling': 'EFFECT_READBACK_ONLY_NO_NATIVE_QUALIFICATION'})
    oid = write_blob(context, canonical(resolved))
    updates = retention_updates(context, [oid, source_oid])
    updates[refs['source']] = (oid, source_oid)
    # Fence the exact authority tuple that earned JOIN. Never adopt newer
    # controller/invalidation heads merely because pointer/marker stayed equal.
    observed = {'controller': context['controller_oid'], 'pointer': joined['pointer_oid'],
                'marker': joined['marker_oid'], 'invalidation': joined['pointer']['invalidation_oid']}
    if authorities(context) != observed:
        raise RotationError('canonical outcome changed during native source reconciliation')
    guards = owner_guards(context, observed)
    receipt_ref_value, receipt_oid = joined['receipt_token'].split('@')
    guards[receipt_ref_value] = receipt_oid
    update_refs(context, updates, guards)
    return resolved['resolution']


def _resolve_native_input_state_v1(native, controller):
    """Fresh CLI: consume one durable source revision, preserving both clocks.

    This is the fixed receiver selected by canonical_rotation_inputs.py. No
    observe() call re-stamps a retained event. CLAIMED survives process death;
    another CLI cannot reconstruct it as READY. Partial/unknown results require
    existing-owner reconciliation; a new genuine source event is a new episode.
    """
    global _NATIVE_INPUT_RESOLVED_V1
    if type(controller) is not str or not CONTROLLER.fullmatch(controller):
        raise native.NativeInputError('NATIVE_INPUT_EXISTING_OWNER_SELECTION_ABSENT')
    waiter = None
    try:
        if _NATIVE_INPUT_RESOLVED_V1 is not None:
            state, context, expected, source, grant, waiter = _NATIVE_INPUT_RESOLVED_V1
            waiter.check()  # Independent signal before any Git/namespace work.
            if context['controller'] != controller:
                raise RotationError('native input cannot cross its actual selected controller')
            if read_refs(context['repo'], expected) != expected:
                raise RotationError('native source or grant head changed')
            _validate_native_revision_v1(context, source, grant, native, claimed=True)
            _native_preparation_require_consumer_v1(context, source, grant, expected, claimed=True)
            waiter.check()
            return state
        borrowed = _NATIVE_PREDECESSOR_BINDING_V1
        if borrowed is None:
            context, predecessor = discover(controller), None
        elif type(borrowed) is _NativePredecessorReadV1:
            context, predecessor = borrowed.take(controller)
        else:
            raise RotationError('native predecessor binding is not the existing owner read')
        _native_selection_v1(context)
        refs = native_input_revision_refs_v1(context)
        heads = read_refs(context['repo'], refs.values())
        if any(value is None for value in heads.values()):
            raise RotationError('native source or grant revision is absent')
        source = decode_json(read_blob(context['repo'], heads[refs['source']]))
        grant = decode_json(read_blob(context['repo'], heads[refs['grant']]))
        _validate_native_revision_v1(context, source, grant, native)
        _native_preparation_require_consumer_v1(context, source, grant, heads)
        waiter = NativeCancellationWaitV1(source['cancellation'], source['producer_process'], source['reservation_id'])
        if predecessor is None:
            predecessor = resolve_predecessor(context)
        helper = projection_helper()
        if source['binding']['subject'] != helper._native_subject(predecessor):
            raise RotationError('native source names a different canonical pair or receipt')
        import secrets
        claimed = dict(source, phase='CLAIMED', ready_oid=heads[refs['source']],
                       executor=native_process_identity_v1(os.getpid()), transaction_id=secrets.token_hex(16))
        oid = write_blob(context, canonical(claimed))
        updates = retention_updates(context, [oid, *heads.values()])
        updates[refs['source']] = (oid, heads[refs['source']])
        guards = predecessor_guards(context, predecessor)
        guards[refs['grant']] = heads[refs['grant']]
        waiter.check()
        update_refs(context, updates, guards)
        waiter.check()
        expected = {refs['source']: oid, refs['grant']: heads[refs['grant']]}
        if read_refs(context['repo'], expected) != expected:
            raise RotationError('native source consumption has an unknown effect; reconcile before retry')
        _validate_native_revision_v1(context, claimed, grant, native, claimed=True)
        if borrowed is not None:
            borrowed.verify()  # Fresh full tuple after acquisition; never a cached authority.
        state = native.NativeInputState(source['binding'])
        state._snapshot = source['exact_usage']
        state._reported_window = source['reported_window']
        state._received_monotonic_ns = source['observed_monotonic_ns']
        state._revision = source['cutoff_revision']
        state._quiescent = True
        state._native_revision_guards = expected
        state._native_cancellation_wait = waiter
        _NATIVE_INPUT_RESOLVED_V1 = (state, context, expected, claimed, grant, waiter)
        return state
    except (RotationError, native.NativeInputError, OSError, KeyError, TypeError, ValueError) as exc:
        if waiter is not None and _NATIVE_INPUT_RESOLVED_V1 is None:
            waiter.close()
        raise native.NativeInputError('NATIVE_INPUT_DURABLE_SOURCE_UNAVAILABLE_OR_CONSUMED') from exc


def owner_guards(context, observed, *, exclude=()):
    return {context[key + "_ref"]: observed[key]
            for key in ("controller", "pointer", "marker", "invalidation") if key not in exclude}


# Proposed private addition to claim-run-rotation.py. No new public grant input.
import contextvars as _c02_contextvars
import threading as _c02_threading


class C02MaterializationUnknown(RotationError):
    """An attempted effect raced withdrawal or has uncertain completion."""


_C02_LIVE_OPERATION_V1 = _c02_contextvars.ContextVar('claim_owned_c02_operation', default=None)
_C02_SELECTED_SOURCE_V1 = _c02_contextvars.ContextVar('claim_c02_selected_source', default=None)
_C02_SOURCE_CUSTODY_V1 = _c02_contextvars.ContextVar('claim_c02_source_custody', default=None)


def _resolve_c02_materializer_capabilities_v1(context, request):
    """Fixed actual-owner seam, never a caller callback or JSON permission.

    The existing owned-stdio source currently supplies held physical prefixes
    and compaction/resume summaries. It does not yet supply the authoritative
    mapping of all native boundaries/adjudications to a complete live interval.
    Neither that missing fact nor an actual scoped issuer is invented here.
    Only the existing selected source owner may wire its concrete live census
    and issuer leases here after their actual admission. Production stays shut.
    """
    selected = _C02_SELECTED_SOURCE_V1.get()
    if selected is None:
        raise RotationError('C02_COMPLETE_ORDERED_INTERVAL_AND_SCOPED_ISSUER_LEASE_UNAVAILABLE')
    _, source, issuer = selected
    source.verify(); issuer.verify()
    return source, issuer


def _c02_materializer_selection_v1(context):
    live = _C02_SELECTED_SOURCE_V1.get()
    selected = live[0] if live is not None else _C02_ADMITTED_OWNER_SELECTION_V1
    keys = {'repo', 'controller', 'claim_id', 'run_root_identity', 'census_owner',
            'issuer', 'source_contract_locator', 'owner_decision_locator'}
    if (type(selected) is not dict or set(selected) != keys
            or any(not isinstance(value, str) or not value for value in selected.values())
            or Path(selected['repo']) != context['repo'] or not Path(selected['repo']).is_absolute()
            or any(selected[key] != context[key] for key in ('controller', 'claim_id', 'run_root_identity'))):
        raise RotationError('C02 actual scoped owner selection is unavailable or foreign')
    safe_chain(context['repo'])
    return selected


def _c02_require_live_operation_v1(context):
    operation = _C02_LIVE_OPERATION_V1.get()
    if operation is None or operation.context is not context:
        raise RotationError('C02 accepting effect requires the existing owned-stdio live operation')
    operation.verify()
    return operation


class _C02PublicationInputs(_NativePublicationInputs):
    """The existing update_refs checkpoint ABI, with an independently live veto."""
    def __init__(self, retained, operation):
        self.retained, self.operation = retained, operation

    def verify(self):
        self.operation.verify()
        if self.retained is not None:
            self.retained.verify()
        self.operation.verify()

    def ref_guards_v1(self):
        self.operation.verify()
        return (self.retained.ref_guards_v1()
                if isinstance(self.retained, _NativePublicationInputs) else {})

    def verified_ref_guards_v1(self):
        # C02's live source/issuer checks intervene between native checks.
        # Preserve their order instead of coalescing across that boundary.
        self.verify()
        return self.ref_guards_v1()

    def before_effect(self):
        self.verify()
        prior = self.retained.before_effect() if isinstance(self.retained, _NativePublicationInputs) else None
        return prior, self.operation.checkpoint()

    def after_effect(self, checkpoint):
        prior, stamp = checkpoint
        self.operation.after_effect(stamp)
        if prior is not None:
            self.retained.after_effect(prior)
        if self.retained is not None:
            self.retained.verify()
        self.operation.after_effect(stamp)


def _c02_compose_live_inputs_v1(context, retained):
    operation = _c02_require_live_operation_v1(context)
    if isinstance(retained, _C02PublicationInputs):
        if retained.operation is not operation:
            raise RotationError('C02 live operation changed')
        return retained
    return _C02PublicationInputs(retained, operation)


@_scoped_git
def _c02_withdraw_owned_revision_v1(context, role, owned_oids):
    """One-way denial only; never overwrite another reservation or revive one."""
    refs = _c02_owner_revision_refs_v1(context)
    ref = refs['grant_ref' if role == 'issuer' else 'ref']
    old = read_ref(context['repo'], ref)
    if old is None or old not in owned_oids:
        return
    value = decode_json(read_blob(context['repo'], old))
    if role == 'issuer':
        if value.get('revoked') is True:
            return
        value['revoked'] = True
    else:
        if value.get('census_complete') is False:
            return
        value.update(census_complete=False, ordering='WITHDRAWN_NO_ADMISSION')
    oid = write_blob(context, canonical(value))
    updates = retention_updates(context, [old, oid])
    updates[ref] = (oid, old)
    # This denial must not inherit the accepting operation's now-invalid guard.
    try:
        update_refs(context, updates, {context['controller_ref']: context['controller_oid']})
    except CASFailure:
        current = read_ref(context['repo'], ref)
        if current == oid:
            return
        if current not in owned_oids:
            return  # A different revision is never overwritten by this cleanup.
        raise


class _C02OwnedOperation:
    def __init__(self, context, token, decision, source, issuer):
        self.context, self.token = context, token
        self._source_custody = _C02_SOURCE_CUSTODY_V1.get()
        self.decision_bytes = canonical(decision)
        self.source, self.issuer = source, issuer
        for capability, names in ((source, ('verify', 'checkpoint', 'census')),
                                  (issuer, ('verify', 'checkpoint', 'grant'))):
            if callable(capability) or any(not callable(getattr(capability, name, None)) for name in names):
                raise RotationError('C02 actual owner lease interface is incomplete; booleans are not authority')
        self._lock = _c02_threading.Lock()
        self.invalidated = _c02_threading.Event()
        self._reason = None
        self._closed = False
        self._source_intents, self._grant_intents = set(), set()
        self._initial = (source.checkpoint(), issuer.checkpoint())
        self.verify()

    def verify(self):
        if self._source_custody is not None:
            self._source_custody.verify()
        with self._lock:
            if self._reason is not None or self._closed:
                raise RotationError('C02 owner operation invalidated: ' + str(self._reason or 'closed'))
        self.source.verify()
        self.issuer.verify()
        if (self.source.checkpoint(), self.issuer.checkpoint()) != self._initial:
            raise RotationError('C02 source or issuer lease revision advanced')
        with self._lock:
            if self._reason is not None or self._closed:
                raise RotationError('C02 owner operation changed while verified')

    def checkpoint(self):
        self.verify()
        return self._initial

    def after_effect(self, stamp):
        try:
            self.verify()
            if stamp != self._initial:
                raise RotationError('C02 publication checkpoint was substituted')
        except BaseException as exc:
            raise C02MaterializationUnknown('C02 effect raced source/issuer withdrawal; exact readback required') from exc

    def register_intent(self, source_oid, grant_oid):
        # Intent is recorded before CAS, so a landed-but-unknown write cannot be
        # forgotten because a post-CAS success flag was never set.
        with self._lock:
            self._source_intents.add(source_oid)
            self._grant_intents.add(grant_oid)

    def cancel_now(self, reason='SOURCE_ADVANCED'):
        if reason not in {'SOURCE_ADVANCED', 'CONNECTION_LOST', 'ISSUER_WITHDRAWN', 'SOURCE_CLOSED'}:
            raise RotationError('unknown C02 owner signal')
        # Signal-only first pass. No Git, source read, callback or blocking cleanup.
        with self._lock:
            self._reason = reason
            self.invalidated.set()

    def signal(self, reason):
        self.cancel_now(reason)
        with self._lock:
            source_oids, grant_oids = set(self._source_intents), set(self._grant_intents)
        if reason == 'ISSUER_WITHDRAWN':
            _c02_withdraw_owned_revision_v1(self.context, 'issuer', grant_oids)
        else:
            _c02_withdraw_owned_revision_v1(self.context, 'source', source_oids)

    def before_context_request(self, method):
        self.signal('SOURCE_ADVANCED')
        raise RotationError('C02 reservation withdrawn before context dispatch; reacquire outside this operation')

    def after_native_record(self):
        self.signal('SOURCE_ADVANCED')

    def disconnect(self):
        self.signal('CONNECTION_LOST')

    def issuer_withdrawn(self):
        self.signal('ISSUER_WITHDRAWN')


@contextlib.contextmanager
def c02_owned_operation_v1(context, invalidation_token, decision, *, _selected_source_owner=None):
    """Use the same materialized, template-bound existing owner as native OR."""
    selected_token = custody_token = None
    with contextlib.ExitStack() as held:
        if _selected_source_owner is not None:
            import ast
            # Admission binds the separately provisioned source repo companion.
            expected = context['repo'] / 'skills/implementaudit/scripts/compaction-source-owner-codex-app.py'  # source repo owner
            if (type(_selected_source_owner) is not types.ModuleType
                    or Path(_selected_source_owner.__file__).absolute() != expected
                    or _C02_SELECTED_SOURCE_V1.get() is not None):
                raise RotationError('C02 binding must come from the existing materialized source owner')
            producer = held.enter_context(PinnedFile(expected, max_bytes=512 * 1024))
            raw = producer.read()
            declarations = [node for node in ast.parse(raw).body if isinstance(node, ast.Assign)
                            and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                            and node.targets[0].id == 'OWNED_STDIO_SELECTION_PIN']
            if len(declarations) != 1:
                raise RotationError('C02 selected owner has no unique fixed provider declaration')
            value = declarations[0].value
            pin = ast.literal_eval(value)
            rows = raw.splitlines(keepends=True)
            start = sum(map(len, rows[:value.lineno - 1])) + value.col_offset
            end = sum(map(len, rows[:value.end_lineno - 1])) + value.end_col_offset
            if hashlib.sha256(raw[:start] + b'None' + raw[end:]).hexdigest() != _NATIVE_SOURCE_OWNER_TEMPLATE_SHA256:
                raise RotationError('C02 materialized owner differs from the shared reviewed source template')
            if (type(pin) is not dict or set(pin) != {'path', 'bytes', 'sha256'}
                    or type(pin['path']) is not str or not Path(pin['path']).is_absolute()
                    or type(pin['bytes']) is not int or not 0 < pin['bytes'] <= 256 * 1024
                    or type(pin['sha256']) is not str or not SHA256.fullmatch(pin['sha256'])):
                raise RotationError('C02 actual provider is not selected')
            provider = held.enter_context(PinnedFile(Path(pin['path']), max_bytes=256 * 1024))
            payload = provider.read()
            if len(payload) != pin['bytes'] or hashlib.sha256(payload).hexdigest() != pin['sha256']:
                raise RotationError('C02 provider differs from its governed pin')
            retained = held.enter_context(RetainedInputs([expected, Path(pin['path'])]))
            getter = getattr(_selected_source_owner, 'get_selected_c02_materializer_v1', None)
            compiled = compile(raw, str(expected), 'exec', dont_inherit=True)
            actual_code = next((item for item in compiled.co_consts if isinstance(item, types.CodeType)
                                and item.co_name == 'get_selected_c02_materializer_v1'), None)
            if (type(getter) is not types.FunctionType or actual_code is None
                    or getter.__globals__ is not _selected_source_owner.__dict__
                    or getter.__closure__ is not None
                    or getter.__code__.replace(co_filename=str(expected)) != actual_code):
                raise RotationError('C02 source getter is not the fixed reviewed source function')
            binding = getter(context, decision)
            selected_token = _C02_SELECTED_SOURCE_V1.set(binding)
            custody_token = _C02_SOURCE_CUSTODY_V1.set(retained)
        try:
            with _c02_acquired_operation_v1(context, invalidation_token, decision) as operation:
                yield operation
        finally:
            if custody_token is not None:
                _C02_SOURCE_CUSTODY_V1.reset(custody_token)
            if selected_token is not None:
                _C02_SELECTED_SOURCE_V1.reset(selected_token)

@contextlib.contextmanager
def _c02_acquired_operation_v1(context, invalidation_token, decision):
    _c02_materializer_selection_v1(context)
    exact_authority_token(context, 'invalidation', invalidation_token)
    if _C02_LIVE_OPERATION_V1.get() is not None:
        raise RotationError('nested C02 owner operation is forbidden')
    request = {key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
    request.update(invalidation_token=invalidation_token, decision_id=decision.get('decision_id'))
    source, issuer = _resolve_c02_materializer_capabilities_v1(context, request)
    operation = _C02OwnedOperation(context, invalidation_token, decision, source, issuer)
    token = _C02_LIVE_OPERATION_V1.set(operation)
    try:
        yield operation
        operation.verify()
    except BaseException:
        # Preserve the original error. Cleanup never restores the old authority.
        try:
            operation.signal('SOURCE_CLOSED')
        except BaseException:
            pass
        raise
    finally:
        with operation._lock:
            operation._closed = True
        _C02_LIVE_OPERATION_V1.reset(token)


def _c02_project_owned_interval_v1(context, interval, original):
    """Validate metadata from the actual source lease; never infer absent events."""
    keys = {'schema', 'source_owner', 'source_cutoff', 'subject', 'interval_start', 'interval_end',
            'complete', 'covered_boundary_kinds', 'covers_adjudications', 'events'}
    selected = _c02_materializer_selection_v1(context)
    if (type(interval) is not dict or set(interval) != keys
            or interval['schema'] != 'implementaudit.c02-owned-interval.v1'
            or interval['source_owner'] != selected['census_owner']
            or interval['subject'] != {key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
            or interval['complete'] is not True or interval['covers_adjudications'] is not True
            or interval['covered_boundary_kinds'] != sorted(BOUNDARIES)
            or not isinstance(interval['source_cutoff'], str) or not interval['source_cutoff']
            or type(interval['interval_start']) is not int or type(interval['interval_end']) is not int
            or not 0 <= interval['interval_start'] <= interval['interval_end']
            or type(interval['events']) is not list or not 0 < len(interval['events']) <= 4096):
        raise RotationError('C02 complete all-boundary/adjudication source interval is unavailable')
    previous = interval['interval_start'] - 1
    found = False
    later, prior, event_ids, native_oids, decisions = [], [], set(), set(), set()
    guards = {}
    for row in interval['events']:
        if (type(row) is not dict or type(row.get('sequence')) is not int
                or not previous < row['sequence'] <= interval['interval_end']):
            raise RotationError('C02 source order is unknown, duplicated or reversed')
        previous = row['sequence']
        if row.get('kind') == 'native-boundary':
            if set(row) != {'sequence', 'kind', 'event_id', 'invalidation_oid', 'boundary'}:
                raise RotationError('C02 source boundary descriptor is malformed')
            event = {key: row[key] for key in ('event_id', 'invalidation_oid', 'boundary')}
            if row['event_id'] in event_ids or row['invalidation_oid'] in native_oids or row['boundary'] not in BOUNDARIES:
                raise RotationError('C02 source boundary is ambiguous or unsupported')
            actual = invalidation_record(context, row['invalidation_oid'])
            if actual != {'event': row['event_id'], 'oid': row['invalidation_oid'], 'boundary': row['boundary']}:
                raise RotationError('C02 source boundary does not bind the retained native object')
            require_anchor(context, row['invalidation_oid'])
            guards[anchor_ref(context, row['invalidation_oid'])] = row['invalidation_oid']
            event_ids.add(row['event_id']); native_oids.add(row['invalidation_oid'])
            if event == original:
                found = True
            elif found:
                later.append(event)
        elif row.get('kind') == 'adjudication':
            if set(row) != {'sequence', 'kind', 'record_oid'} or row['record_oid'] in decisions:
                raise RotationError('C02 source adjudication descriptor is ambiguous')
            record = _c02_read_correction_v1(context, row['record_oid'])
            if record['observation']['invalidation_oid'] == original['invalidation_oid'] and not found:
                raise RotationError('C02 adjudication precedes its source-mapped erroneous event')
            prior.append({'observation': record['observation'], 'decision': record['decision']})
            decisions.add(row['record_oid'])
            guards[anchor_ref(context, row['record_oid'])] = row['record_oid']
        else:
            raise RotationError('C02 source interval has an unclassified owner event')
    if not found:
        raise RotationError('C02 exact erroneous event is absent from the admitted source interval')
    local, local_guards = _c02_retained_decisions_v1(context)
    if decisions != {oid for _, oid in local}:
        raise RotationError('C02 source census omitted or invented retained adjudications')
    guards.update(local_guards)
    return {'schema': 'implementaudit.c02-owner-snapshot.v1', 'source_owner': interval['source_owner'],
            'source_cutoff': interval['source_cutoff'], 'ordering': 'SOURCE_OWNER_COMPLETE_SEQUENCE',
            'census_complete': True, 'erroneous_event': original, 'later_boundaries': later,
            'prior_decisions': prior}, guards


@_scoped_git
def materialize_c02_owner_revisions_v1(context, invalidation_token, decision, *, correction_record_oid=None):
    """Publish admitted existing-owner facts through the sole claim writer.

    No source snapshot, grant, callback or approval flag is accepted from CLI.
    Complete ordered facts and the conditional issuer decision come from the
    two live capabilities selected by the existing owner. This changes only
    the already registered C02 revision heads and retained-object anchors.
    """
    operation = _c02_require_live_operation_v1(context)
    if operation.token != invalidation_token or operation.decision_bytes != canonical(decision):
        raise RotationError('C02 materialization substituted its selected operation')
    with rotation_lease(context):
        source = native_resume_source(context)
        predecessor, observed = source['predecessor'], source['observed']
        event_oid = exact_authority_token(context, 'invalidation', invalidation_token)
        if observed['invalidation'] != event_oid:
            raise CASFailure('newer native boundary preempted C02 materialization')
        event = invalidation_record(context, event_oid)
        original = {'event_id': event['event'], 'invalidation_oid': event_oid, 'boundary': event['boundary']}
        refs = _c02_owner_revision_refs_v1(context)
        old = read_refs(context['repo'], refs.values())
        request = {key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
        request.update(context=context, invalidation_token=invalidation_token, decision_id=decision['decision_id'],
            code_sha256=hashlib.sha256(read_regular(Path(__file__).absolute())).hexdigest(),
            projection_code_sha256=hashlib.sha256(read_regular(Path(__file__).absolute().with_name('rotate-canonical-state.py'))).hexdigest(),
            correction_record_oid=correction_record_oid,
            effect='C02_FRESH_TRANSITION' if correction_record_oid is not None else 'APPEND_ONLY_NO_CURRENTNESS')
        snapshot, history_guards = _c02_project_owned_interval_v1(context, operation.source.census(request), original)
        observation = {'schema': 'implementaudit.c02-observation.v1',
            **{key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')},
            'pointer_oid': observed['pointer'], 'receipt_oid': predecessor['receipt_oid'],
            'marker_oid': observed['marker'], **original, 'later_boundaries': snapshot['later_boundaries']}
        proposal = propose_c02_correction_v1(observation, decision, snapshot['prior_decisions'])
        if snapshot['later_boundaries']:
            raise RotationError('C02 source census has a newer applicable boundary; no materialization')
        correction = None
        if correction_record_oid is not None:
            correction = _c02_read_correction_v1(context, correction_record_oid)
            if correction['observation'] != observation or correction['decision'] != decision:
                raise RotationError('C02 conditional successor substituted its original accepted append')
            request['fresh_scope'] = _c02_fresh_grant_scope_v1(context, correction, correction_record_oid,
                                                           predecessor, snapshot['source_cutoff'])
        request.update(source_cutoff=snapshot['source_cutoff'],
                       expected_old=getattr(operation.source, 'expected_old', None))
        grant = operation.issuer.grant(request)
        snapshot['grant'] = decode_json(canonical(grant))
        plan = prepare_c02_owner_revision_update_v1(context, snapshot, grant,
            expected_source_oid=old[refs['ref']], expected_grant_oid=old[refs['grant_ref']])
        source_oid, grant_oid = plan['updates'][refs['ref']][0], plan['updates'][refs['grant_ref']][0]
        locator = dict(ref=refs['ref'], oid=source_oid, grant_ref=refs['grant_ref'], grant_oid=grant_oid)
        if correction is None:
            _c02_verify_grant_v1(snapshot, request, observation, decision)
        else:
            _c02_admission_material_v1(context, correction, correction_record_oid, predecessor,
                                      snapshot, locator, request['code_sha256'], request['projection_code_sha256'])
        operation.verify()
        guards = owner_guards(context, observed)
        guards.update({predecessor['receipt_ref']: predecessor['receipt_oid'], 'HEAD': predecessor['head']})
        guards.update(history_guards)
        if old == {refs['ref']: source_oid, refs['grant_ref']: grant_oid}:
            operation.verify()
            if read_refs(context['repo'], {**guards, **old}) != {**guards, **old}:
                raise CASFailure('C02 exact materialization retry changed during readback')
            return {'status': 'EXACT_REVISION_RETRY_NO_EFFECT', 'source_oid': source_oid, 'grant_oid': grant_oid,
                    'effect': request['effect'], 'currentness_restored': False}
        operation.register_intent(source_oid, grant_oid)
        if write_blob(context, plan['source_bytes']) != source_oid or write_blob(context, plan['grant_bytes']) != grant_oid:
            raise RotationError('C02 materialized revision bytes changed')
        updates = retention_updates(context, [source_oid, grant_oid, *old.values()])
        updates.update(plan['updates'])
        try:
            update_refs(context, updates, guards, observation=_c02_compose_live_inputs_v1(context, None))
            operation.verify()
            current = read_refs(context['repo'], refs.values())
            if current != {refs['ref']: source_oid, refs['grant_ref']: grant_oid}:
                raise CASFailure('C02 materialized revisions changed during readback')
        except BaseException as exc:
            current = read_refs(context['repo'], refs.values())
            landed = current.get(refs['ref']) == source_oid or current.get(refs['grant_ref']) == grant_oid
            if landed or isinstance(exc, C02MaterializationUnknown):
                try:
                    operation.signal('SOURCE_CLOSED')
                except BaseException:
                    pass
                error = C02MaterializationUnknown('C02 materialization outcome retained for exact reconciliation; no success')
                error.revision_readback = current
                raise error from exc
            raise
        require_anchor(context, source_oid); require_anchor(context, grant_oid)
        return {'status': 'OWNER_REVISIONS_MATERIALIZED', 'source_oid': source_oid, 'grant_oid': grant_oid,
                'effect': request['effect'], 'currentness_restored': False}


# Inert until the repository owner explicitly selects the existing adjudication
# role for one reviewed qualification subject. Never populate from CLI, env,
# STATE, caller configuration, or a fixture. The actual decision is external
# owner authority; this fixed receiver selection is not itself an issuer grant.
_C02_ADMITTED_OWNER_SELECTION_V1 = None


def _c02_owner_revision_refs_v1(context):
    if not isinstance(context.get('controller'), str) or not CONTROLLER.fullmatch(context['controller']):
        raise RotationError('C02 revision roles require an existing explicit controller')
    return {'ref': 'refs/implementaudit/continuity-adjudication-sources/' + context['controller'],
            'grant_ref': 'refs/implementaudit/continuity-adjudication-grants/' + context['controller']}


def prepare_c02_owner_revision_update_v1(context, snapshot, grant, *, expected_source_oid, expected_grant_oid):
    """Pure revision-update plan, NOT source/issuer admission or a publisher.

    The existing claim owner may consume this only after verifying the actual
    existing native-source facts and the scoped repository-owner decision. It
    must materialize/retain both objects using write_blob/retention_updates and
    publish with update_refs plus the exact live owner tuple. Revocation may
    independently update the grant head; no long source/decision work takes the
    namespace gate. This helper does not allocate refs or accept authority.
    """
    refs = _c02_owner_revision_refs_v1(context)
    if (type(snapshot) is not dict or snapshot.get('schema') != 'implementaudit.c02-owner-snapshot.v1'
            or type(grant) is not dict or snapshot.get('grant') != grant
            or grant.get('schema') not in {'implementaudit.c02-issuer-grant.v1', 'implementaudit.c02-fresh-transition-grant.v1'}
            or any(value is not None and (not isinstance(value, str) or not OID.fullmatch(value))
                   for value in (expected_source_oid, expected_grant_oid))):
        raise RotationError('C02 revision proposal is malformed; no authority is inferred')
    source_bytes, grant_bytes = canonical(snapshot), canonical(grant)
    def blob_oid(data):
        return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    return {'source_bytes': source_bytes, 'grant_bytes': grant_bytes,
            'updates': {refs['ref']: (blob_oid(source_bytes), expected_source_oid),
                        refs['grant_ref']: (blob_oid(grant_bytes), expected_grant_oid)},
            'authority_ceiling': 'INERT_REVISION_PLAN_NO_EFFECT_AUTHORITY'}


def _resolve_c02_source_owner_v1(context, request):
    """Consume fixed existing-owner selection and independently live revisions.

    These are claim-owned roles in the existing Git store, not new event/pending
    storage or a second currentness writer. Actual source and issuer verification
    precede their publication; a true boolean or caller hash cannot establish it.
    """
    selected = _c02_materializer_selection_v1(context)
    if selected is None:
        raise RotationError('C02 source-owner admission unavailable: actual scoped owner selection required')
    keys = {'repo', 'controller', 'claim_id', 'run_root_identity', 'census_owner',
            'issuer', 'source_contract_locator', 'owner_decision_locator'}
    if (type(selected) is not dict or set(selected) != keys
            or any(not isinstance(value, str) or not value for value in selected.values())
            or any(selected[key] != context[key] or request.get(key) != context[key]
                   for key in ('controller', 'claim_id', 'run_root_identity'))
            or request.get('effect') not in {'APPEND_ONLY_NO_CURRENTNESS', 'C02_FRESH_TRANSITION'}):
        raise RotationError('C02 request is outside the fixed admitted episode')
    try:
        selected_repo = Path(selected['repo'])
        same_repo = selected_repo.is_absolute() and selected_repo == context['repo']
        if same_repo:
            safe_chain(selected_repo)
    except OSError as exc:
        raise RotationError('C02 selected repository custody is unavailable') from exc
    if not same_repo:
        raise RotationError('C02 selected repository custody changed')
    locator = _c02_owner_revision_refs_v1(context)
    source_oid = read_ref(context['repo'], locator['ref'])
    grant_oid = read_ref(context['repo'], locator['grant_ref'])
    if source_oid is None or grant_oid is None:
        raise RotationError('C02 actual source or issuer revision has not been admitted')
    snapshot = decode_json(read_blob(context['repo'], source_oid))
    grant = decode_json(read_blob(context['repo'], grant_oid))
    if (type(snapshot) is not dict or snapshot.get('source_owner') != selected['census_owner']
            or type(grant) is not dict or grant.get('issuer') != selected['issuer']
            or snapshot.get('grant') != grant):
        raise RotationError('C02 actual source owner, issuer or independently current grant disagree')
    if (read_ref(context['repo'], locator['ref']) != source_oid
            or read_ref(context['repo'], locator['grant_ref']) != grant_oid):
        raise RotationError('C02 source or issuer revision changed during resolution')
    # Existing consumers enforce census, scope, applicability, code and revocation
    # and CAS-fence both heads. No caller-provided accepting callback exists.
    return dict(locator, oid=source_oid, grant_oid=grant_oid)


def _c02_source_census_v1(context, invalidation_token, decision, *, effect='APPEND_ONLY_NO_CURRENTNESS'):
    """Resolve an owner snapshot, then verify bytes and revision outside the gate."""
    _c02_require_live_operation_v1(context)
    oid = exact_authority_token(context, "invalidation", invalidation_token)
    original = invalidation_record(context, oid)
    if original is None or original['boundary'] not in BOUNDARIES:
        raise RotationError("C02 requires one exact original native invalidation")
    request = {key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')}
    request.update(invalidation_token=invalidation_token, event_id=original['event'],
                   decision_id=decision.get('decision_id') if type(decision) is dict else None,
                   code_sha256=hashlib.sha256(read_regular(Path(__file__).absolute())).hexdigest(),
                   effect=effect)
    if effect == 'C02_FRESH_TRANSITION':
        request['projection_code_sha256'] = hashlib.sha256(read_regular(Path(__file__).absolute().with_name('rotate-canonical-state.py'))).hexdigest()
    locator = _resolve_c02_source_owner_v1(context, request)
    if (type(locator) is not dict or set(locator) != {'ref', 'oid', 'grant_ref', 'grant_oid'}
            or any(not isinstance(locator[key], str) for key in locator)
            or not OID.fullmatch(locator['oid']) or not OID.fullmatch(locator['grant_oid'])
            or locator['ref'] == locator['grant_ref']):
        raise RotationError("C02 source owner returned no exact live revision locator")
    if (read_ref(context['repo'], locator['ref']) != locator['oid']
            or read_ref(context['repo'], locator['grant_ref']) != locator['grant_oid']):
        raise RotationError("C02 source or issuer grant revision changed before census read")
    source = decode_json(read_blob(context['repo'], locator['oid']))
    grant = decode_json(read_blob(context['repo'], locator['grant_oid']))
    keys = {'schema', 'source_owner', 'source_cutoff', 'ordering', 'census_complete',
            'erroneous_event', 'later_boundaries', 'prior_decisions', 'grant'}
    if (type(source) is not dict or set(source) != keys
            or source['schema'] != 'implementaudit.c02-owner-snapshot.v1'
            or source['census_complete'] is not True
            or source['ordering'] != 'SOURCE_OWNER_COMPLETE_SEQUENCE'
            or not isinstance(source['source_owner'], str) or not source['source_owner']
            or not isinstance(source['source_cutoff'], str) or not source['source_cutoff']
            or type(source['later_boundaries']) is not list or len(source['later_boundaries']) > 4096
            or type(source['prior_decisions']) is not list or len(source['prior_decisions']) > 4096):
        raise RotationError("C02 source census is incomplete or its ordering/cutoff is unknown")
    if source['grant'] != grant:
        raise RotationError('C02 source snapshot does not bind the current actual issuer grant revision')
    expected_event = {'event_id': original['event'], 'invalidation_oid': oid, 'boundary': original['boundary']}
    if source['erroneous_event'] != expected_event:
        raise RotationError("C02 census substituted the exact original invalidation")
    # Order comes only from the admitted source owner. OIDs are never timestamps.
    seen_events, seen_oids = {original['event']}, {oid}
    for row in source['later_boundaries']:
        if (type(row) is not dict or set(row) != set(expected_event)
                or not isinstance(row['event_id'], str) or not row['event_id']
                or not isinstance(row['invalidation_oid'], str) or not OID.fullmatch(row['invalidation_oid'])
                or row['event_id'] in seen_events or row['invalidation_oid'] in seen_oids
                or row['boundary'] not in BOUNDARIES):
            raise RotationError("C02 later applicable boundary census is ambiguous")
        actual = invalidation_record(context, row['invalidation_oid'])
        if actual != {'event': row['event_id'], 'oid': row['invalidation_oid'], 'boundary': row['boundary']}:
            raise RotationError("C02 later boundary differs from its retained native event")
        require_anchor(context, row['invalidation_oid'])
        seen_events.add(row['event_id'])
        seen_oids.add(row['invalidation_oid'])
    if (read_ref(context['repo'], locator['ref']) != locator['oid']
            or read_ref(context['repo'], locator['grant_ref']) != locator['grant_oid']):
        raise RotationError("C02 source or issuer grant revision changed during census read")
    return source, locator, request


def _c02_verify_grant_v1(source, request, observed, decision):
    """Check a grant resolved by the owner; a caller SHA alone grants nothing."""
    grant = source['grant']
    scope = {key: observed[key] for key in ('controller', 'claim_id', 'run_root_identity',
             'pointer_oid', 'receipt_oid', 'marker_oid', 'invalidation_oid', 'event_id')}
    if (type(grant) is not dict or set(grant) != {'schema', 'issuer', 'scope', 'kind', 'effect', 'code_sha256', 'revoked'}
            or grant['schema'] != 'implementaudit.c02-issuer-grant.v1'
            or grant['issuer'] != decision['issuer'] or grant['scope'] != scope
            or grant['kind'] != decision['kind'] or grant['effect'] != request['effect']
            or grant['code_sha256'] != request['code_sha256'] or grant['revoked'] is not False
            or hashlib.sha256(canonical(grant)).hexdigest() != decision['grant_sha256']):
        raise RotationError("C02 issuer grant is missing, revoked, or outside exact scope/code/applicability")


def _c02_retained_decisions_v1(context):
    """Read append-only decisions in existing object custody, without OID ordering."""
    prefix = f"refs/implementaudit/state-archives/{context['controller']}/objects/"
    raw = git(context['repo'], 'for-each-ref', '--format=%(refname) %(objectname)', prefix)
    rows = raw.decode('ascii', 'strict').splitlines()
    if len(rows) > 16384:
        raise RotationError("C02 retained-decision census exceeds the bounded source scan")
    records, guards = [], {}
    for row in rows:
        ref, oid = row.split(' ')
        if ref != anchor_ref(context, oid) or read_ref(context['repo'], ref) != oid:
            raise RotationError("C02 object custody census changed or has a substituted anchor")
        data = read_blob(context['repo'], oid)
        if b'"schema":"implementaudit.c02-correction-record.v1"' not in data:
            continue
        record = decode_json(data)
        if type(record) is not dict or record.get('schema') != 'implementaudit.c02-correction-record.v1':
            continue
        if (type(record) is not dict or set(record) != {'schema', 'observation', 'decision', 'source', 'expected_old', 'currentness'}
                or record['schema'] != 'implementaudit.c02-correction-record.v1'
                or record['currentness'] != 'DISABLED_PENDING_OWNER_PROTOCOL'):
            raise RotationError("retained C02 correction record is malformed")
        propose_c02_correction_v1(record['observation'], record['decision'], [])
        if any(record['observation'][key] != context[key] for key in ('controller', 'claim_id', 'run_root_identity')):
            raise RotationError("retained C02 decision belongs to another claim")
        records.append((record, oid))
        guards[ref] = oid
    return records, guards


@_scoped_git
def prepare_c02_correction_v1(context, invalidation_token, decision):
    """Inert source-owned census/admission preparation; no ref or blob writes.

    Production remains fail closed until its actual source-owner resolver is
    admitted. Even an admitted grant here permits only append-only adjudication;
    it cannot reinstate a receipt or supply fresh continuity transition semantics.
    """
    source, locator, request = _c02_source_census_v1(context, invalidation_token, decision)
    live = managed(context)
    joined = _read_generation_evidence_v1(context, live)
    receipt, receipt_oid = split_receipt_token(context, joined['receipt_token'])
    event = source['erroneous_event']
    observed = {'schema': 'implementaudit.c02-observation.v1',
                **{key: context[key] for key in ('controller', 'claim_id', 'run_root_identity')},
                'pointer_oid': live['pointer'], 'receipt_oid': receipt_oid, 'marker_oid': live['marker'],
                **event, 'later_boundaries': source['later_boundaries']}
    local, local_guards = _c02_retained_decisions_v1(context)
    prior = source['prior_decisions'] + [{'observation': row['observation'], 'decision': row['decision']} for row, _ in local]
    proposal = propose_c02_correction_v1(observed, decision, prior)
    _c02_verify_grant_v1(source, request, observed, decision)
    if live['invalidation'] != event['invalidation_oid']:
        raise CASFailure("C02 original invalidation was preempted by a newer boundary")
    expected = owner_guards(context, live)
    expected[receipt] = receipt_oid
    expected[locator['ref']] = locator['oid']
    expected[locator['grant_ref']] = locator['grant_oid']
    expected.update(local_guards)
    record = {'schema': 'implementaudit.c02-correction-record.v1', 'observation': observed,
              'decision': decision, 'source': dict(locator, source_owner=source['source_owner'], source_cutoff=source['source_cutoff']),
              'expected_old': dict(proposal['expected_old'], controller_oid=live['controller'], receipt_ref=receipt),
              'currentness': 'DISABLED_PENDING_OWNER_PROTOCOL'}
    raw = canonical(record)
    record_oid = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    existing = [oid for row, oid in local if row['observation']['invalidation_oid'] == event['invalidation_oid']]
    if len(existing) > 1:
        raise RotationError("C02 conflicting duplicate adjudication requires owner reconciliation")
    if read_refs(context['repo'], expected) != expected:
        raise CASFailure("C02 expected-old or source/grant revision changed during preparation")
    return {'schema': 'implementaudit.c02-prepared-correction.v1', 'invalidation_token': invalidation_token,
            'decision': decision, 'record': record, 'record_oid': record_oid, 'guards': expected,
            'existing_record_oid': existing[0] if existing else None, 'status': proposal['status'],
            'authority_ceiling': 'INERT_PREPARATION_NO_EFFECT_AUTHORITY'}


@_scoped_git
def publish_c02_correction_v1(context, prepared):
    """Append once through claim-run custody; never change currentness authorities.

    The existing rotation lease serializes correction decisions. Evidence is
    resolved and checked before update_refs takes the short namespace gate;
    native boundaries remain free to arrive and their exact ref preempts CAS.
    The live source revision guard also fences grant revocation at publication.
    """
    keys = {'schema', 'invalidation_token', 'decision', 'record', 'record_oid', 'guards',
            'existing_record_oid', 'status', 'authority_ceiling'}
    if (type(prepared) is not dict or set(prepared) != keys
            or prepared['schema'] != 'implementaudit.c02-prepared-correction.v1'
            or prepared['authority_ceiling'] != 'INERT_PREPARATION_NO_EFFECT_AUTHORITY'):
        raise RotationError("C02 publication requires one exact inert preparation")
    with rotation_lease(context), RetainedInputs(retained_owner_paths(context)) as observation:
        observation = _c02_compose_live_inputs_v1(context, observation)
        fresh = prepare_c02_correction_v1(context, prepared['invalidation_token'], prepared['decision'])
        # Local append evidence can appear after a crashed call; source/grant and
        # original expected-old bindings must still be identical on exact retry.
        for key in ('record', 'record_oid'):
            if fresh[key] != prepared[key]:
                raise CASFailure("C02 source, grant, or expected-old preparation changed")
        if fresh['status'] == 'SUPERSEDED_NEWER_BOUNDARY_NO_EFFECT':
            return {'status': fresh['status'], 'record_oid': fresh['existing_record_oid'], 'currentness_restored': False}
        if fresh['existing_record_oid'] is not None:
            require_anchor(context, fresh['existing_record_oid'])
            return {'status': 'EXACT_RETRY_NO_EFFECT', 'record_oid': fresh['existing_record_oid'], 'currentness_restored': False}
        record_oid = write_blob(context, canonical(fresh['record']))
        if record_oid != fresh['record_oid']:
            raise RotationError("C02 correction object differs from its inert preparation")
        retained = [record_oid, fresh['record']['observation']['invalidation_oid'], fresh['record']['source']['oid'],
                    fresh['record']['source']['grant_oid']]
        updates = retention_updates(context, retained)
        guards = dict(fresh['guards'])
        for oid in retained:
            ref = anchor_ref(context, oid)
            if ref not in updates:
                guards[ref] = oid
        update_refs(context, updates, guards, observation=observation)
        require_anchor(context, record_oid)
        if read_blob(context['repo'], record_oid) != canonical(fresh['record']):
            raise RotationError("C02 append did not retain its exact correction bytes")
        return {'status': 'APPENDED_NO_CURRENTNESS', 'record_oid': record_oid, 'currentness_restored': False}


def _c02_read_correction_v1(context, oid):
    require_anchor(context, oid)
    record = decode_json(read_blob(context['repo'], oid))
    if (type(record) is not dict or set(record) != {'schema', 'observation', 'decision', 'source', 'expected_old', 'currentness'}
            or record['schema'] != 'implementaudit.c02-correction-record.v1'
            or record['currentness'] != 'DISABLED_PENDING_OWNER_PROTOCOL'):
        raise RotationError('C02 transition lacks an exact append-only correction record')
    proposal = propose_c02_correction_v1(record['observation'], record['decision'], [])
    expected = dict(proposal['expected_old'], controller_oid=context['controller_oid'])
    receipt = record['expected_old'].get('receipt_ref') if type(record['expected_old']) is dict else None
    if (not isinstance(receipt, str) or record['expected_old'] != dict(expected, receipt_ref=receipt)
            or any(expected[key] != context[key] for key in ('controller', 'claim_id', 'run_root_identity'))
            or record['observation']['later_boundaries']):
        raise RotationError('C02 correction record has changed or superseded expected-old bindings')
    split_receipt_token(context, receipt + '@' + expected['receipt_oid'])
    require_anchor(context, expected['invalidation_oid'])
    original = invalidation_record(context, expected['invalidation_oid'])
    if original != {'oid': expected['invalidation_oid'], 'event': record['observation']['event_id'], 'boundary': record['observation']['boundary']}:
        raise RotationError('C02 correction does not retain its exact erroneous occurrence')
    custody = record['source']
    if type(custody) is not dict or set(custody) != {'ref', 'oid', 'grant_ref', 'grant_oid', 'source_owner', 'source_cutoff'}:
        raise RotationError('C02 correction lacks its original source custody')
    ref_path(context['repo'], custody['ref'])
    ref_path(context['repo'], custody['grant_ref'])
    require_anchor(context, custody['oid'])
    require_anchor(context, custody['grant_oid'])
    original_source = decode_json(read_blob(context['repo'], custody['oid']))
    if (type(original_source) is not dict or original_source.get('schema') != 'implementaudit.c02-owner-snapshot.v1'
            or original_source.get('census_complete') is not True
            or original_source.get('ordering') != 'SOURCE_OWNER_COMPLETE_SEQUENCE'
            or original_source.get('source_owner') != custody['source_owner']
            or original_source.get('source_cutoff') != custody['source_cutoff']
            or original_source.get('later_boundaries') != [] or type(original_source.get('grant')) is not dict):
        raise RotationError('C02 original source snapshot is incomplete or substituted')
    if read_blob(context['repo'], custody['grant_oid']) != canonical(original_source['grant']):
        raise RotationError('C02 original issuer grant object differs from retained source admission')
    original_code = original_source['grant'].get('code_sha256')
    if not isinstance(original_code, str) or not SHA256.fullmatch(original_code):
        raise RotationError('C02 original source has no exact companion code binding')
    _c02_verify_grant_v1(original_source, {'code_sha256': original_code, 'effect': 'APPEND_ONLY_NO_CURRENTNESS'},
                         record['observation'], record['decision'])
    return record


def _c02_fresh_grant_scope_v1(context, correction, oid, predecessor, source_cutoff):
    expected = correction['expected_old']
    bindings = {'controller_oid': predecessor['controller_oid'], 'pointer_oid': predecessor['pointer_oid'],
                'receipt_oid': predecessor['receipt_oid'], 'receipt_ref': predecessor['receipt_ref'],
                'marker_oid': predecessor['migration_marker_oid']}
    if (predecessor['receipt_schema'] != RECEIPT_SCHEMA
            or any(expected[key] != value for key, value in bindings.items())
            or any(predecessor[key] != context[key] for key in ('controller', 'claim_id', 'run_root_identity'))
            or expected['invalidation_oid'] == predecessor['invalidation_oid']):
        raise RotationError('C02 fresh transition substituted its exact migrated predecessor')
    scope = {key: expected[key] for key in ('controller', 'claim_id', 'run_root_identity',
             'controller_oid', 'pointer_oid', 'receipt_oid', 'marker_oid')}
    scope.update(correction_record_oid=oid, corrected_invalidation_oid=expected['invalidation_oid'],
                 projection_generation_id=next_epoch(predecessor['projection_generation_id']),
                 continuity_epoch=next_epoch(predecessor['continuity_epoch']), source_cutoff=source_cutoff)
    return scope


def _c02_admission_material_v1(context, correction, oid, predecessor, source, locator, code_sha256, projection_code_sha256):
    keys = {'schema', 'source_owner', 'source_cutoff', 'ordering', 'census_complete',
            'erroneous_event', 'later_boundaries', 'prior_decisions', 'grant'}
    if (type(source) is not dict or set(source) != keys or source.get('schema') != 'implementaudit.c02-owner-snapshot.v1'
            or source.get('census_complete') is not True or source.get('ordering') != 'SOURCE_OWNER_COMPLETE_SEQUENCE'
            or not isinstance(source.get('source_cutoff'), str) or not source['source_cutoff']
            or not isinstance(source.get('source_owner'), str) or not source['source_owner']
            or source.get('later_boundaries') != [] or type(source.get('prior_decisions')) is not list
            or {'observation': correction['observation'], 'decision': correction['decision']} not in source['prior_decisions']
            or source.get('erroneous_event') != {key: correction['observation'][key] for key in ('event_id', 'invalidation_oid', 'boundary')}):
        raise RotationError('C02 fresh transition requires a complete source census including its prior adjudication')
    propose_c02_correction_v1(correction['observation'], correction['decision'], source['prior_decisions'])
    scope = _c02_fresh_grant_scope_v1(context, correction, oid, predecessor, source['source_cutoff'])
    grant = source.get('grant')
    if (type(grant) is not dict or set(grant) != {'schema', 'issuer', 'scope', 'effect', 'code_sha256', 'projection_code_sha256', 'revoked'}
            or grant['schema'] != 'implementaudit.c02-fresh-transition-grant.v1'
            or not isinstance(grant['issuer'], str) or not grant['issuer']
            or grant['scope'] != scope or grant['effect'] != 'C02_FRESH_TRANSITION' or grant['revoked'] is not False
            or not isinstance(code_sha256, str) or not SHA256.fullmatch(code_sha256)
            or not isinstance(projection_code_sha256, str) or not SHA256.fullmatch(projection_code_sha256)
            or grant['code_sha256'] != code_sha256 or grant['projection_code_sha256'] != projection_code_sha256):
        raise RotationError('C02 fresh-transition grant is missing, revoked, or outside exact scope/code/applicability')
    return {'schema': 'implementaudit.c02-transition-admission.v1', 'correction_record_oid': oid,
            'corrected_invalidation_oid': scope['corrected_invalidation_oid'], 'source_ref': locator['ref'],
            'source_oid': locator['oid'], 'source_cutoff': source['source_cutoff'], 'source_owner': source['source_owner'],
            'grant_ref': locator['grant_ref'], 'grant_oid': locator['grant_oid'],
            'grant_sha256': hashlib.sha256(canonical(grant)).hexdigest(), 'grant_issuer': grant['issuer'],
            'code_sha256': code_sha256, 'projection_code_sha256': projection_code_sha256}


def _c02_fresh_admission_v1(context, correction_oid, predecessor):
    correction = _c02_read_correction_v1(context, correction_oid)
    token = context['invalidation_ref'] + '@' + correction['observation']['invalidation_oid']
    source, locator, request = _c02_source_census_v1(context, token, correction['decision'], effect='C02_FRESH_TRANSITION')
    return _c02_admission_material_v1(context, correction, correction_oid, predecessor, source, locator,
                                       request['code_sha256'], request['projection_code_sha256'])


def _c02_validate_admission_record_v1(context, record):
    """Historical admission bytes, not a live revocation or fresh effect grant."""
    admission = record['c02_admission']
    keys = {'schema', 'correction_record_oid', 'corrected_invalidation_oid', 'source_ref', 'source_oid',
            'source_cutoff', 'source_owner', 'grant_ref', 'grant_oid', 'grant_sha256', 'grant_issuer', 'code_sha256', 'projection_code_sha256'}
    if (type(admission) is not dict or set(admission) != keys
            or admission['schema'] != 'implementaudit.c02-transition-admission.v1'):
        raise RotationError('C02 epoch admission is malformed')
    correction = _c02_read_correction_v1(context, admission['correction_record_oid'])
    source = decode_json(read_blob(context['repo'], admission['source_oid']))
    expected = _c02_admission_material_v1(context, correction, admission['correction_record_oid'], record['prepared']['predecessor'],
        source, {'ref': admission['source_ref'], 'oid': admission['source_oid'],
                 'grant_ref': admission['grant_ref'], 'grant_oid': admission['grant_oid']}, admission['code_sha256'], admission['projection_code_sha256'])
    ref_path(context['repo'], admission['source_ref'])
    ref_path(context['repo'], admission['grant_ref'])
    if (admission != expected or record['prepared'].get('correction_record_oid') != admission['correction_record_oid']
            or record['transition']['invalidation_oid'] == admission['corrected_invalidation_oid']
            or read_blob(context['repo'], admission['grant_oid']) != canonical(source['grant'])):
        raise RotationError('C02 epoch replaced correction provenance or reused its erroneous invalidation')


def _c02_transition_grant_guards_v1(context, record):
    """Refresh actual owner evidence before, never while holding, namespace.gate."""
    expected = record['c02_admission']
    fresh = _c02_fresh_admission_v1(context, expected['correction_record_oid'], record['prepared']['predecessor'])
    if fresh != expected:
        raise CASFailure('C02 fresh-transition source or grant revision changed')
    guards = {fresh['source_ref']: fresh['source_oid'], fresh['grant_ref']: fresh['grant_oid']}
    for oid in (fresh['correction_record_oid'], fresh['corrected_invalidation_oid'], fresh['source_oid'], fresh['grant_oid']):
        guards[anchor_ref(context, oid)] = oid
    return guards


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
    if transition['transition_kind'] == 'c02-correction':
        guards.update(_c02_transition_grant_guards_v1(context, record))
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
                or ("/objects/" in ref and ref.rsplit("/", 1)[-1] != oid)):
            raise RotationError("archive retention census drifted or escaped declared history custody")
        read_blob(context["repo"], oid)
    if read_refs(context['repo'], guards) != guards:
        raise RotationError("archive retention census drifted or escaped declared history custody")
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


def allocate_c02_correction_epoch(context, prepared, source, admission, *, observation=None):
    predecessor, observed = source['predecessor'], source['observed']
    fresh = _c02_fresh_admission_v1(context, admission['correction_record_oid'], predecessor)
    if fresh != admission or observed['invalidation'] != admission['corrected_invalidation_oid']:
        raise CASFailure('C02 source or grant changed before its fresh allocation')
    epoch = next_epoch(predecessor['continuity_epoch'])
    ref = receipt_ref(context, epoch)
    if any(read_ref(context['repo'], item) is not None for item in (ref, epoch_ref(context, epoch), publication_ref(context, epoch))):
        raise RotationError('C02_TRANSITION_ALLOCATION_EXISTS: retained partial publication requires inspection')
    event = 'c02-correction/' + admission['correction_record_oid'] + '/' + epoch
    raw = ('\t'.join(('implementaudit.continuity-invalidation.v1', context['controller'],
                     context['controller_oid'], context['claim_id'], C02_BOUNDARY, event)) + '\n').encode()
    invalidation_oid = write_blob(context, raw)
    transition = {'schema': C02_TRANSITION_SCHEMA, 'controller': context['controller'], 'claim_id': context['claim_id'],
                  'run_root_identity': context['run_root_identity'], 'projection_generation_id': next_epoch(predecessor['projection_generation_id']),
                  'continuity_epoch': epoch, 'boundary': C02_BOUNDARY, 'invalidation_oid': invalidation_oid,
                  'predecessor_receipt_ref_oid': predecessor['receipt_ref'] + '@' + predecessor['receipt_oid'],
                  'expected_receipt_ref_schema': {'ref': ref, 'schema': RECEIPT_SCHEMA},
                  'transition_kind': 'c02-correction', 'payload_source': 'preimage',
                  'failed_transition_epoch': None, 'failed_transition_generation': None,
                  'failed_transition_receipt_ref_oid': None, 'head': predecessor['head'], 'tree': predecessor['tree']}
    record = {'schema': 'implementaudit.c02-correction-epoch.v1', 'transition': transition, 'prepared': prepared,
              'controller_oid': context['controller_oid'], 'expected_pointer_oid': observed['pointer'],
              'expected_marker_oid': observed['marker'], 'failed_epoch_oid': None, 'failed_pointer_oid': None,
              'c02_admission': admission}
    validate_epoch(context, record, epoch)
    epoch_oid = write_blob(context, canonical(record))
    updates = retention_updates(context, [*observed.values(), predecessor['receipt_oid'], prepared['archive_manifest_oid'],
                                         invalidation_oid, epoch_oid, admission['source_oid'], admission['grant_oid'], admission['correction_record_oid']])
    updates[epoch_ref(context, epoch)] = (epoch_oid, None)
    updates[context['invalidation_ref']] = (invalidation_oid, observed['invalidation'])
    guards = owner_guards(context, observed, exclude=('invalidation',))
    guards.update({'HEAD': predecessor['head'], predecessor['receipt_ref']: predecessor['receipt_oid'],
                   admission['source_ref']: admission['source_oid'],
                   admission['grant_ref']: admission['grant_oid'],
                   anchor_ref(context, admission['correction_record_oid']): admission['correction_record_oid']})
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
    return {"status": {"recovery": "RECOVERED_PRIOR", "rotation": "ROTATED", "native-resume": "RESUMED",
                       "c02-correction": "CORRECTED_FRESH"}[transition["transition_kind"]],
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
def run_canonical_rotation_v1(context, owner_map_path, calibration, *, tokenizer_encoding=None, native_input=False):
    if type(native_input) is not bool:
        raise RotationError("native input selection must be explicit")
    if native_input and tokenizer_encoding is None:
        raise RotationError("native input selection requires the exact offline tokenizer encoding")
    with rotation_lease(context):
        predecessor_read = _NativePredecessorReadV1(context) if native_input else None
        predecessor = predecessor_read.predecessor() if predecessor_read is not None else resolve_predecessor(context)
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
        if native_input:
            paths.append(Path(__file__).absolute().with_name('canonical_rotation_inputs.py'))
        with RetainedInputs(paths) as observation, contextlib.ExitStack() as native_scope:
            generation = next_epoch(predecessor["projection_generation_id"])
            helper = projection_helper()
            token_input = {}
            if tokenizer_encoding is not None:
                # Data only: retained exact encoding bytes, never caller code or
                # a caller-authored count/context-health envelope.
                token_input['tokenizer_bytes'] = read_regular(Path(tokenizer_encoding).absolute())
            native_lease = None
            if native_input:
                if calibration != helper.full_or_calibration_contract_v1():
                    raise RotationError("native input requires the exact complete OR policy")
                source = tuple(read_regular(context['repo'] / predecessor[key + '_path'])
                               for key in ('state', 'roadmap'))
                if any(hashlib.sha256(raw).hexdigest() != predecessor[key + '_sha256']
                       for key, raw in zip(('state', 'roadmap'), source)):
                    raise RotationError("native input source differs from exact predecessor")
                source_bytes = sum(map(len, source))
                source_tokens = sum(helper.count_rotation_tokens_v1(token_input['tokenizer_bytes'], source))
                native_subject = helper._native_subject(predecessor)
                native_scope.enter_context(_native_predecessor_scope_v1(predecessor_read, observation))
                native_scope.enter_context(_native_preparation_scope_v1(
                    context, predecessor_read, observation, native_subject, source_bytes, source_tokens))
                native_lease = native_scope.enter_context(helper.native_inputs_module_v1().rotation_input_lease_v1(
                    native_subject, source_bytes, source_tokens))
                token_input['native_observation'] = native_lease
            prepared = helper.prepare_canonical_draft(context["repo"], context["run_root"],
                        context["controller"], generation, owner_map_path, predecessor, calibration, **token_input)
            observation.verify()
            if type(prepared) is dict and prepared.get("triggered") is False:
                if read_refs(context['repo'], predecessor_guards(context, predecessor)) != predecessor_guards(context, predecessor):
                    raise RotationError("source changed during cheap-path admission")
                result = {"status": "NOT_TRIGGERED", "receipt_token": predecessor["receipt_ref"] + "@" + predecessor["receipt_oid"]}
                if native_lease is not None:
                    helper._verify_live_native_lease(native_lease, predecessor, source_bytes, source_tokens)
                    result.update(input_scope='BYTES_TOKENS_AND_CONFIGURED_HEADROOM',
                                  context_health_semantics=prepared['native_input']['observation']['health_semantics'],
                                  context_health_bp=prepared['context_health_bp'],
                                  live_bytes=prepared['live_bytes'], live_tokens=prepared['live_tokens'])
                elif tokenizer_encoding is not None:
                    result.update(input_scope='BYTES_AND_TOKENS', context_health='UNAVAILABLE',
                                  live_bytes=prepared['live_bytes'], live_tokens=prepared['live_tokens'])
                return result
            validate_prepared(context, prepared, predecessor)
            if read_refs(context['repo'], predecessor_guards(context, predecessor)) != predecessor_guards(context, predecessor):
                raise RotationError("source boundary or authority changed during F2")
            observed = authorities(context)
            if native_lease is not None:
                def publish(selected, native_guard):
                    if selected != prepared['native_input']['observation']:
                        raise RotationError("prepared native input differs from admitted observation")
                    custody = _NativePublicationInputs(observation, native_guard)
                    custody.verify()
                    record, epoch_oid = allocate_epoch(context, prepared, observed, observation=custody)
                    return complete_epoch(context, record, epoch_oid, observation=custody)
                # A source race after publisher entry may have an effect. Preserve
                # that UNKNOWN and its epoch; do not silently compensate or retry.
                return native_lease.admit(native_subject, source_bytes, source_tokens, publish)
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
def run_c02_correction_v1(context, correction_record_oid):
    """Private fresh C02 transition; unavailable without the actual owner binding.

    The append-only decision never itself restores currentness. An independent
    scoped fresh-transition grant is resolved before preparation/allocation and
    each publication stage. Partial allocations stop for explicit inspection;
    they are neither native resume nor automatic rotation compensation.
    """
    with rotation_lease(context):
        correction = _c02_read_correction_v1(context, correction_record_oid)
        try:
            joined = require_current_generation_join_v1(context)
        except CustodyError:
            raise
        except RotationError:
            pass
        else:
            prior, _ = read_epoch(context, joined['pointer']['continuity_epoch'])
            if (prior['transition']['transition_kind'] != 'c02-correction'
                    or prior['c02_admission']['correction_record_oid'] != correction_record_oid):
                raise RotationError('C02 record does not identify the exact current corrected successor')
            guards = _c02_transition_grant_guards_v1(context, prior)
            # Owner resolution can admit a newer native event while it runs.
            # Even a no-effect retry must not return the now-stale receipt.
            current = require_current_generation_join_v1(context)
            if (current['pointer_oid'] != joined['pointer_oid'] or current['receipt_token'] != joined['receipt_token']
                    or read_refs(context['repo'], guards) != guards):
                raise CASFailure('C02 exact retry currentness or grant revision changed during readback')
            return {'status': 'ALREADY_CORRECTED', 'receipt_token': joined['receipt_token'],
                    'pointer_token': context['pointer_ref'] + '@' + joined['pointer_oid'],
                    'continuity_epoch': joined['pointer']['continuity_epoch'], 'marker_oid': joined['marker_oid']}
        source = native_resume_source(context)
        predecessor = source['predecessor']
        if source['observed']['invalidation'] != correction['observation']['invalidation_oid']:
            raise CASFailure('C02 correction was preempted by a newer genuine boundary')
        admission = _c02_fresh_admission_v1(context, correction_record_oid, predecessor)
        epoch = next_epoch(predecessor['continuity_epoch'])
        if any(read_ref(context['repo'], ref) is not None for ref in
               (epoch_ref(context, epoch), publication_ref(context, epoch), receipt_ref(context, epoch))):
            raise RotationError('C02_TRANSITION_ALLOCATION_EXISTS: retained partial publication requires inspection')
        generation = context['run_root'] / 'state-generations' / predecessor['projection_generation_id']
        paths = [*retained_owner_paths(context), *(generation / name for name in
                 ('STATE.md', 'ROADMAP.md', 'protected-state.json', 'archive-manifest.json', 'generation-manifest.json'))]
        with RetainedInputs(paths) as observation:
            observation = _c02_compose_live_inputs_v1(context, observation)
            helper = projection_helper()
            prepare = getattr(helper, 'prepare_c02_correction_draft', None)
            if not callable(prepare):
                raise RotationError('C02 projection preparation interface is unavailable')
            prepared = prepare(context['repo'], context['run_root'], context['controller'],
                               next_epoch(predecessor['projection_generation_id']), predecessor, correction)
            observation.verify()
            validate_prepared(context, prepared, predecessor)
            if authorities(context) != source['observed']:
                raise CASFailure('C02 source authority changed during inert draft preparation')
            record, epoch_oid = allocate_c02_correction_epoch(context, prepared, source, admission, observation=observation)
            try:
                return complete_epoch(context, record, epoch_oid, observation=observation)
            except CustodyError:
                raise
            except Exception as exc:
                raise RotationError('C02_TRANSITION_INCOMPLETE: retained allocation requires inspection; ' + str(exc)) from exc


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
def invalidate_current_generation_v1(context, boundary, event, *, _expected_old=None, _observation=None):
    if boundary not in BOUNDARIES:
        raise RotationError("public invalidation requires a native boundary, not a rotation claim")
    field(event, "physical boundary event")
    observed = managed(context)
    if _expected_old is not None and observed != _expected_old:
        raise CASFailure("controlled C02 fault was preempted by a genuine boundary")
    raw = ("\t".join(("implementaudit.continuity-invalidation.v1", context["controller"],
                      context["controller_oid"], context["claim_id"], boundary, event)) + "\n").encode()
    oid = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    # A physical occurrence has one boundary kind. Reuse existing append-only
    # object anchors to distinguish exact retry from conflicting provenance;
    # neither an observer nor another event/currentness store is introduced.
    for kind in sorted((BOUNDARIES | {"canonical-state-rotation", C02_BOUNDARY}) - {boundary}):
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
    update_refs(context, updates, owner_guards(context, observed, exclude=("invalidation",)), observation=_observation)
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
                                           "resolve-resume", "read-resume", "rotate", "recover",
                                           "c02-prepare", "c02-append", "c02-apply"))
    parser.add_argument("controller")
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    context = discover(args.controller)
    if args.command in {"c02-prepare", "c02-append", "c02-apply"}:
        correction = argparse.ArgumentParser(prog="claim-run.sh " + {
            "c02-prepare": "--prepare-c02-correction", "c02-append": "--append-c02-correction",
            "c02-apply": "--apply-c02-correction"}[args.command])
        if args.command == "c02-apply":
            correction.add_argument("--correction-record", required=True)
            options = correction.parse_args(args.arguments)
            result = run_c02_correction_v1(context, options.correction_record)
        else:
            correction.add_argument("--expected-invalidation", required=True)
            correction.add_argument("--decision", required=True)
            options = correction.parse_args(args.arguments)
            # Caller bytes are a bounded proposal, never a source locator or grant.
            # The fixed existing-owner resolver supplies and CAS-fences both.
            decision = decode_json(read_regular(Path(options.decision).absolute(), max_bytes=65536))
            prepared = prepare_c02_correction_v1(context, options.expected_invalidation, decision)
            result = (publish_c02_correction_v1(context, prepared)
                      if args.command == "c02-append" else prepared)
        sys.stdout.buffer.write(canonical(result) + b"\n")
        return 0
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
        rotation.add_argument("--tokenizer-encoding", help="exact offline cl100k_base encoding; requires tiktoken 0.13.0")
        rotation.add_argument("--native-input", action="store_true",
                              help="require the admitted existing-owner native input lease; no caller observations")
        options = rotation.parse_args(args.arguments)
        if options.native_input and not options.tokenizer_encoding:
            rotation.error("--native-input requires --tokenizer-encoding")
        helper = projection_helper()
        calibration = (helper.full_or_calibration_contract_v1() if options.native_input
                       else helper.token_calibration_contract_v1() if options.tokenizer_encoding
                       else helper.calibration_contract_v1())
        result = run_canonical_rotation_v1(context, Path(options.owner_map), calibration,
                                         tokenizer_encoding=options.tokenizer_encoding, native_input=options.native_input)
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
