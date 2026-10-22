#!/usr/bin/env python3
"""Deterministic canonical projection and retained preimage archive.

This helper owns draft/archive/final-generation bytes only. claim-run owns
invalidation, epoch allocation, current-pointer CAS, receipts and migration.
No helper result grants currentness, lifecycle, release or native host authority.
The captured-source loader and file/Git primitives derive from the pinned R0039
donor; its independent event publisher is not a second canonical writer here.
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

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


# The controller's existing source identity transitively binds this new owner.
# Rebind both reviewed files together; missing, aliased or changed bytes fail closed.
_HOT_PROJECTION_MODULE_SHA256 = 'fe733b91dff4f031ed3ab80761d669de59c0270cd7f85325a14a2d47f9ba5276'
_HOT_PROJECTION_MODULE_BYTES = 57891
def _load_hot_projection_module():
    import hashlib as _hashlib
    import os as _os
    import stat as _stat
    import sys as _sys
    import types as _types
    _path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'canonical_hot_projection.py')
    _fd = None
    try:
        _before = _os.lstat(_path)
        if (_stat.S_ISLNK(_before.st_mode) or not _stat.S_ISREG(_before.st_mode)
                or getattr(_before, "st_file_attributes", 0) & 0x400):
            raise ImportError("canonical_hot_projection.py: source is not a non-aliased regular file")
        _flags = _os.O_RDONLY | getattr(_os, "O_BINARY", 0) | getattr(_os, "O_NONBLOCK", 0) | getattr(_os, "O_NOFOLLOW", 0)
        _fd = _os.open(_path, _flags)
        _info = _os.fstat(_fd)
        if (not _stat.S_ISREG(_info.st_mode) or (_before.st_dev, _before.st_ino) != (_info.st_dev, _info.st_ino)):
            raise ImportError("canonical_hot_projection.py: source identity changed while opening")
        with _os.fdopen(_fd, "rb") as _stream:
            _fd = None
            _source = _stream.read(_HOT_PROJECTION_MODULE_BYTES + 1)
    except OSError as _exc:
        raise ImportError("canonical_hot_projection.py: source unavailable") from _exc
    finally:
        if _fd is not None:
            _os.close(_fd)
    if len(_source) != _HOT_PROJECTION_MODULE_BYTES or _hashlib.sha256(_source).hexdigest() != _HOT_PROJECTION_MODULE_SHA256:
        raise ImportError("canonical_hot_projection.py: source identity mismatch")
    _module = _types.ModuleType(__name__ + ".hot_projection_module")
    _module.__file__ = _path
    # Register before execution for annotations/introspection; undo a failed load.
    _previous = _sys.modules.get(_module.__name__)
    _sys.modules[_module.__name__] = _module
    try:
        exec(compile(_source, _path, "exec"), _module.__dict__)
    except BaseException:
        if _previous is None:
            _sys.modules.pop(_module.__name__, None)
        else:
            _sys.modules[_module.__name__] = _previous
        raise
    return _module
_hot_projection_module = _load_hot_projection_module()


ZERO_OID = "0" * 40
ARCHIVE_PREFIX = "refs/implementaudit/state-archives"

class RotationError(RuntimeError):
    """Refusal of an incomplete or uncertain rotation operation."""

WINDOWS_TRUSTED_GIT_PATHS_V1 = (
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files\Git\bin\git.exe",
)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_reparse(st: object) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & 0x400)


def effective_mode(mode: int) -> int:
    if os.name == "nt":
        return 0o666 if mode & stat.S_IWUSR else 0o444
    return mode


def _fixed_git_environment_v1(executable: str,
                              platform_name: str) -> dict[str, str]:
    if platform_name == "nt":
        path_value = ";".join((
            r"C:\Program Files\Git\cmd",
            r"C:\Program Files\Git\bin",
            r"C:\Program Files\Git\usr\bin",
            r"C:\Windows\System32",
            r"C:\Windows",
        ))
        sink = "NUL"
    elif platform_name == "posix":
        path_value = ":".join(dict.fromkeys(
            (str(Path(executable).parent), "/usr/bin", "/bin")))
        sink = "/dev/null"
    else:
        raise RotationError("trusted Git platform is unsupported")
    return {
        "PATH": path_value, "LC_ALL": "C", "LANG": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": sink,
        "GIT_TERMINAL_PROMPT": "0", "GIT_NO_REPLACE_OBJECTS": "1",
    }


def git_environment() -> dict[str, str]:
    return _fixed_git_environment_v1(
        git_executable_v1(), "nt" if os.name == "nt" else "posix")


def _scoped_git(function):
    @functools.wraps(function)
    def invoke(repo, *args, **kwargs):
        with _CUSTODY.git_scope(repo, git_executable_v1(), git_environment()):
            return function(repo, *args, **kwargs)
    return invoke


def git_executable_v1() -> str:
    candidates = (tuple(Path(value) for value in WINDOWS_TRUSTED_GIT_PATHS_V1)
                  if os.name == "nt"
                  else (Path("/usr/bin/git"), Path("/usr/local/bin/git")))
    executable = next((candidate for candidate in candidates
                       if candidate.is_file() and not candidate.is_symlink()), None)
    if executable is None:
        raise RotationError("trusted Git executable is unavailable")
    return str(executable)


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        [git_executable_v1(), '--no-replace-objects', '-c',
         'core.hooksPath=' + ('NUL' if os.name == 'nt' else '/dev/null'),
         "-C", str(repo), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_environment(),
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise RotationError(f"git {' '.join(args)} failed: {detail or result.returncode}")
    return result.stdout


def git_optional(repo: Path, *args: str) -> tuple[int, bytes]:
    result = subprocess.run(
        [git_executable_v1(), '--no-replace-objects', '-c',
         'core.hooksPath=' + ('NUL' if os.name == 'nt' else '/dev/null'),
         "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=git_environment(),
        check=False,
    )
    return result.returncode, result.stdout


def same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(
        os.path.abspath(right)
    )


def contained(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath((os.path.abspath(path), os.path.abspath(root))) == os.path.abspath(root)
    except ValueError:
        return False


@contextlib.contextmanager
def _directory_handle(path: Path, root: Path, *, create: bool = False):
    """Hold every ancestor; all child accesses remain relative to these handles.

    A pathname lstat is not custody across an open. Unsupported native hosts
    refuse instead of silently falling back to a string-based ancestor check.
    This prevents symlink redirection, not mutation by an equally privileged
    process that can rename or rewrite the held objects themselves.
    """
    if _WINDOWS is not None:
        path, root = _WINDOWS.absolute_path(path), _WINDOWS.absolute_path(root)
        if not path.is_relative_to(root):
            raise RotationError('path escapes repository custody')
        with _WINDOWS.Directory(path, create=create, create_root=root) as directory:
            yield directory, directory.verify
        return
    path, root = Path(os.path.abspath(path)), Path(os.path.abspath(root))
    if not contained(path, root):
        raise RotationError(f'path escapes repository custody: {path}')
    if (os.name != 'posix' or not hasattr(os, 'O_DIRECTORY')
            or not hasattr(os, 'O_NOFOLLOW')
            or not {os.open, os.stat, os.mkdir}.issubset(os.supports_dir_fd)
            or os.stat not in os.supports_follow_symlinks):
        raise RotationError('native handle-relative ancestor custody is unavailable')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, 'O_CLOEXEC', 0)
    descriptors, links = [], []

    def identity(info):
        if not stat.S_ISDIR(info.st_mode) or is_reparse(info):
            raise RotationError('directory handle is not a non-aliased directory')
        return info.st_dev, info.st_ino, info.st_mode

    def verify():
        for parent, name, descriptor, expected in links:
            if (identity(os.fstat(descriptor)) != expected
                    or identity(os.stat(name, dir_fd=parent, follow_symlinks=False)) != expected):
                raise RotationError('directory ancestry changed during protected access')

    try:
        descriptor = os.open(path.anchor, flags)
        descriptors.append(descriptor)
        identity(os.fstat(descriptor))
        cursor = Path(path.anchor)
        for part in path.parts[1:]:
            cursor /= part
            try:
                child = os.open(part, flags, dir_fd=descriptor)
            except FileNotFoundError:
                if not create or not contained(cursor, root) or cursor == root:
                    raise
                verify()
                os.mkdir(part, mode=0o700, dir_fd=descriptor)
                os.fsync(descriptor)
                child = os.open(part, flags, dir_fd=descriptor)
            descriptors.append(child)
            links.append((descriptor, part, child, identity(os.fstat(child))))
            descriptor = child
        verify()
        yield descriptor, verify
        verify()
    except OSError as exc:
        raise RotationError(f'directory custody is unavailable: {path}: {exc}') from exc
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def require_safe_directory_chain(path: Path, root: Path) -> None:
    with _directory_handle(path, root):
        pass


def require_repo(raw: str) -> Path:
    repo = Path(os.path.abspath(raw))
    require_safe_directory_chain(repo, repo)
    top = Path(
        git(repo, "rev-parse", "--path-format=absolute", "--show-toplevel")
        .decode("utf-8")
        .strip()
    )
    if not same_path(repo, top):
        raise RotationError("--repo-root is not the exact Git worktree root")
    return repo


def require_run_root(raw: str, repo: Path) -> Path:
    run_root = Path(os.path.abspath(raw))
    require_safe_directory_chain(run_root, repo)
    return run_root


def safe_relative(raw: object, forbidden: set[str]) -> str:
    if (
        not isinstance(raw, str)
        or not raw
        or raw.startswith("/")
        or "\\" in raw
        or re.match(r"^[A-Za-z]:", raw)
    ):
        raise RotationError(f"unsafe protected path: {raw}")
    parts = raw.split("/")
    forbidden_folded = {item.casefold() for item in forbidden}
    if any(part in {"", ".", ".."} or ':' in part or part[-1:] in {' ', '.'}
           or any(ord(c) < 32 or ord(c) == 127 for c in part)
           or re.fullmatch(r"(?i)(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part)
           for part in parts) or any(
        part.casefold() in forbidden_folded for part in parts
    ):
        raise RotationError(f"unsafe protected path: {raw}")
    return raw


def read_regular(
    path: Path,
    custody_root: Path,
    label: str,
    *,
    require_owner_write: bool,
) -> tuple[bytes, os.stat_result]:
    if not contained(path, custody_root):
        raise RotationError(f"protected path escapes custody: {label}")
    if _WINDOWS is not None:
        with _WINDOWS.Directory(path.parent) as directory:
            with _WINDOWS.File(directory, path.name, maximum=MAX_SOURCE_BYTES) as held:
                before = held.stat()
                _file_identity(before, label, require_owner_write)
                return held.read(), before
    require_safe_directory_chain(path.parent, custody_root)
    try:
        with _directory_handle(path.parent, custody_root) as (parent, verify):
            before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            expected = _file_identity(before, label, require_owner_write)
            descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW
                                 | getattr(os, 'O_NONBLOCK', 0), dir_fd=parent)
            try:
                if _file_identity(os.fstat(descriptor), label, require_owner_write) != expected:
                    raise RotationError(f'protected file changed while opening: {label}')
                verify()
                chunks, size = [], 0
                while True:
                    chunk = os.read(descriptor, min(1024 * 1024, MAX_SOURCE_BYTES + 1 - size))
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_SOURCE_BYTES:
                        raise RotationError(f'protected file grew beyond bounded allocation: {label}')
                    chunks.append(chunk)
                data = b''.join(chunks)
                after = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                if (_file_identity(after, label, require_owner_write) != expected
                        or _file_identity(os.fstat(descriptor), label, require_owner_write) != expected
                        or len(data) != before.st_size):
                    raise RotationError(f'protected file changed during read: {label}')
            finally:
                os.close(descriptor)
            return data, before
    except OSError as exc:
        raise RotationError(f'protected file is unavailable: {label}: {exc}') from exc


def _file_identity(info, label: str, require_owner_write: bool = False):
    if (not stat.S_ISREG(info.st_mode) or is_reparse(info) or info.st_nlink != 1
            or not info.st_mode & stat.S_IRUSR
            or require_owner_write and not info.st_mode & stat.S_IWUSR):
        raise RotationError(f'protected file must be readable, regular and non-linked: {label}')
    if info.st_size > MAX_SOURCE_BYTES:
        raise RotationError(f'protected file exceeds bounded allocation: {label}')
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns,
            info.st_ctime_ns, info.st_mode, info.st_nlink)


def write_new_regular(path: Path, data: bytes, mode: int, *, custody_root: Path) -> None:
    mode = effective_mode(mode)
    if _WINDOWS is not None:
        if not contained(path, custody_root):
            raise RotationError('output escapes repository custody')
        with _WINDOWS.Directory(path.parent) as directory:
            with _WINDOWS.File(directory, path.name, create=True, writable=True, maximum=MAX_SOURCE_BYTES) as held:
                held.write(data, mode)
                if stat.S_IMODE(held.stat().st_mode) != mode:
                    raise RotationError('immutable output mode differs')
        return
    try:
        with _directory_handle(path.parent, custody_root) as (parent, verify):
            verify()
            descriptor = os.open(path.name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 mode, dir_fd=parent)
            try:
                opened = os.fstat(descriptor)
                if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                    raise RotationError('new protected output is not an exclusive regular file')
                view = memoryview(data)
                while view:
                    written = os.write(descriptor, view)
                    if not written:
                        raise RotationError('protected write made no progress')
                    view = view[written:]
                os.fchmod(descriptor, mode)
                os.fsync(descriptor)
                os.lseek(descriptor, 0, os.SEEK_SET)
                position = 0
                while position < len(data):
                    raw = os.read(descriptor, min(1024 * 1024, len(data) - position))
                    if not raw or raw != data[position:position + len(raw)]:
                        raise RotationError('immutable file readback failed')
                    position += len(raw)
                landed = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                if (_file_identity(landed, path.name) != _file_identity(os.fstat(descriptor), path.name)
                        or (landed.st_dev, landed.st_ino) != (opened.st_dev, opened.st_ino)
                        or landed.st_size != len(data) or stat.S_IMODE(landed.st_mode) != mode):
                    raise RotationError('immutable output identity or mode changed')
                verify()
                os.fsync(parent)
            finally:
                os.close(descriptor)
    except OSError as exc:
        raise RotationError(f'protected output custody failed: {path.name}: {exc}') from exc


PROJECTION_SCHEMA = "implementaudit.protected-projection.v2"
ARCHIVE_SCHEMA = "implementaudit.state-archive.v1"
POINTER_SCHEMA = "implementaudit.current-generation.v1"
POINTER_FIELDS = frozenset({
    'schema', 'controller', 'claim_id', 'run_root_identity',
    'projection_generation_id', 'continuity_epoch', 'invalidation_oid',
    'predecessor_receipt_ref_oid', 'expected_receipt_ref_schema',
    'projection_schema', 'state_sha256', 'roadmap_sha256',
    'protected_manifest_sha256', 'archive_manifest_sha256', 'exact_next_action',
})
CALIBRATION_ID = "R0039-F1-CAL-v2"
CALIBRATION_SHA256 = "b3df1ff07d18f8f5de145cf6d10f48a15f0a0416b392d0ca84567dce6d23e497"
MAX_STATE_BYTES = 65536
MAX_ROADMAP_BYTES = 65536
MAX_SOURCE_BYTES = 16 * 1024 * 1024
# Parse/render/equivalence retain several exact encodings simultaneously. This
# conservative admission bound is additional to measured peak RSS, not a claim
# that Python allocation has an operating-system hard limit.
SOURCE_MEMORY_RESERVE_FACTOR = 12
SOURCE_EXCLUSIONS = {'.git', 'state-generations', 'state-archives', 'quarantine'}


def calibration_contract_v1() -> dict[str, object]:
    """Frozen byte-route contract; other host/token observations remain separate."""
    return {
        'schema': 'implementaudit.rotation-calibration-admission.v1',
        'population_id': CALIBRATION_ID, 'population_sha256': CALIBRATION_SHA256,
        'byte_threshold': 131072, 'minimum_live_byte_reduction': 32768,
        'maximum_runtime_ms': 5000, 'maximum_memory_bytes': 67108864,
        'tokenizer': {'name': 'cl100k_base', 'implementation': 'tiktoken', 'version': '0.12.0'},
        'calibration_host': {'host': 'codex-desktop', 'version': '2026-08-20'},
        'admission_route': 'EXACT_BYTES',
        'host_qualification': 'SEPARATE_NOT_INFERRED',
    }


def _check_memory_budget(source_bytes: int = 0) -> None:
    budget = calibration_contract_v1()['maximum_memory_bytes']
    if source_bytes * SOURCE_MEMORY_RESERVE_FACTOR > budget:
        raise RotationError('source population exceeds conservative memory admission bound')
    try:
        if _WINDOWS is not None:
            peak = _WINDOWS.peak_process_memory()
        else:
            import resource
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform.startswith('linux'):
                peak *= 1024
            elif sys.platform != 'darwin':
                raise RotationError('native peak-memory measurement is unqualified')
        if type(peak) not in (int, float) or peak <= 0:
            raise RotationError('native peak-memory measurement is unavailable')
    except (ImportError, OSError, AttributeError) as exc:
        raise RotationError('native peak-memory measurement is unavailable') from exc
    if peak > budget:
        raise RotationError('process peak memory exceeds frozen bound; no publication authorised')


def rotation_trigger_v1(source_bytes: int, source_tokens: int, context_health_bp: int) -> list[str]:
    """Frozen OR policy. Unknown observations cannot become zero or healthy."""
    if (any(type(value) is not int for value in (source_bytes, source_tokens, context_health_bp))
            or source_bytes < 0 or source_tokens < 0 or not 0 <= context_health_bp <= 10000):
        raise RotationError('complete nonnegative byte/token and bounded context observations are required')
    return [name for name, triggered in (
        ('BYTES', source_bytes >= 131072), ('TOKENS', source_tokens >= 32768),
        ('CONTEXT_HEALTH', context_health_bp <= 2500)) if triggered]


def rotation_payoff_v1(byte_reduction: int, token_reduction: int) -> bool:
    if any(type(value) is not int for value in (byte_reduction, token_reduction)):
        raise RotationError('both measured byte and token reductions are required')
    return byte_reduction >= 32768 and token_reduction >= 8192


def check_rotation_observation_v1(contract: dict, observation: dict, subject: dict,
                                  measured_source_bytes: int, now_unix_ms: int) -> dict:
    """Check a proposed existing-owner input envelope, without admitting a producer.

    This pure interface is deliberately not selected by the accepting CLI. A
    matching caller-authored contract/hash is not a grant or host authentication.
    The calibration/input owner must admit the producer, dependency, current-host
    applicability and full-operation measurement contract before wiring effects.
    """
    contract_keys = {'schema', 'baseline_calibration_id', 'baseline_population_sha256', 'issuer', 'grant_sha256',
                     'producer_sha256', 'host', 'subject', 'maximum_observation_age_ms', 'tokenizer'}
    observation_keys = {'schema', 'contract_sha256', 'subject', 'host', 'issuer', 'grant_sha256',
                        'producer_sha256', 'observed_at_unix_ms', 'source_bytes', 'source_tokens',
                        'context_health_bp', 'tokenizer', 'observation_id'}
    if (type(contract) is not dict or set(contract) != contract_keys
            or contract['schema'] != 'implementaudit.rotation-input-contract-proposal.v1'
            or contract['baseline_calibration_id'] != CALIBRATION_ID or contract['baseline_population_sha256'] != CALIBRATION_SHA256
            or type(observation) is not dict or set(observation) != observation_keys
            or observation['schema'] != 'implementaudit.rotation-input-observation.v1'):
        raise RotationError('unknown or incomplete proposed calibration/input contract')
    for name in ('grant_sha256', 'producer_sha256'):
        if not isinstance(contract[name], str) or re.fullmatch(r'[0-9a-f]{64}', contract[name]) is None:
            raise RotationError('proposed issuer grant and producer identities must be exact')
    if (not isinstance(contract['issuer'], str) or not contract['issuer']
            or type(contract['host']) is not dict or set(contract['host']) != {'name', 'version'}
            or any(not isinstance(value, str) or not value for value in contract['host'].values())
            or type(subject) is not dict
            or set(subject) != {'controller', 'claim_id', 'run_root_identity', 'receipt_token', 'state_sha256', 'roadmap_sha256'}):
        raise RotationError('exact issuer, selected host and complete pair/receipt subject are required')
    for name in ('state_sha256', 'roadmap_sha256'):
        if not isinstance(subject[name], str) or re.fullmatch(r'[0-9a-f]{64}', subject[name]) is None:
            raise RotationError('exact selected pair hashes are required')
    if (not isinstance(subject['controller'], str) or re.fullmatch(r'[a-z0-9][a-z0-9-]{0,47}', subject['controller']) is None
            or not isinstance(subject['claim_id'], str) or re.fullmatch(r'[0-9a-f]{32}', subject['claim_id']) is None
            or not isinstance(subject['run_root_identity'], str)
            or re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}', subject['run_root_identity']) is None
            or not isinstance(subject['receipt_token'], str)
            or re.fullmatch(r'refs/implementaudit/continuity-receipts/' + re.escape(subject['controller'])
                            + r'/G(?!0000)[0-9A-F]{4}@[0-9a-f]{40}', subject['receipt_token']) is None):
        raise RotationError('selected subject has an invalid controller, claim, run or receipt identity')
    if (observation['contract_sha256'] != sha256(canonical_bytes(contract))
            or any(observation[name] != contract[name] for name in ('issuer', 'grant_sha256', 'producer_sha256', 'host'))
            or observation['subject'] != subject or contract['subject'] != subject
            or type(measured_source_bytes) is not int or observation['source_bytes'] != measured_source_bytes
            or contract['tokenizer'] != {'name': 'cl100k_base', 'implementation': 'tiktoken', 'version': '0.13.0'}
            or observation['tokenizer'] != contract['tokenizer']):
        raise RotationError('observation does not bind the selected producer, source, tokenizer or host proposal')
    observed, age = observation['observed_at_unix_ms'], contract['maximum_observation_age_ms']
    if (any(type(value) is not int for value in (observed, age, now_unix_ms))
            or observed < 0 or not 0 < age <= 30000 or not 0 <= now_unix_ms - observed <= age):
        raise RotationError('observation is missing, stale, future-dated or outside proposed freshness')
    body = {key: value for key, value in observation.items() if key != 'observation_id'}
    if observation['observation_id'] != sha256(canonical_bytes(body)):
        raise RotationError('observation identity differs from its complete envelope')
    return {'observation_id': observation['observation_id'],
            'triggered_by': rotation_trigger_v1(measured_source_bytes, observation['source_tokens'], observation['context_health_bp']),
            'authority_ceiling': 'PROPOSED_INPUT_ONLY_NO_EFFECT_AUTHORITY'}


def _json(raw: bytes, label: str) -> Any:
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise RotationError(f'duplicate JSON member in {label}: {key}')
            result[key] = value
        return result
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              RotationError(f'non-finite JSON value in {label}')))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RotationError(f'invalid JSON in {label}') from exc


def _canonical_json(raw: bytes, label: str) -> dict:
    value = _json(raw, label)
    if type(value) is not dict or canonical_bytes(value) != raw:
        raise RotationError(f'noncanonical object: {label}')
    return value


def _hex(value: Any, count: int, label: str) -> str:
    if type(value) is not str or not re.fullmatch('[0-9a-f]{' + str(count) + '}', value):
        raise RotationError(f'invalid {label}')
    return value


def _identity(controller: str, generation: str) -> str:
    if (type(controller) is not str
            or not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?', controller)
            or type(generation) is not str or not re.fullmatch(r'G[0-9A-F]{4}', generation)
            or generation == 'G0000'):
        raise RotationError('invalid canonical controller/generation identity')
    return f'{ARCHIVE_PREFIX}/{controller}/{generation}'


def _ref(repo: Path, ref: str, *, absent: bool = False) -> str | None:
    try:
        observed = _CUSTODY.current_ref(repo, ref)
    except OSError as exc:
        raise RotationError(str(exc)) from exc
    if observed is not NotImplemented:
        if observed is None and not absent:
            raise RotationError('required authority ref is absent')
        return observed
    """ABSENT is distinct from malformed ref and failed Git operation."""
    if not re.fullmatch(r'refs/implementaudit/[A-Za-z0-9/._-]+', ref):
        raise RotationError('invalid implementation ref')
    rc, output = git_optional(repo, 'show-ref', '--verify', '--quiet', ref)
    if rc == 1 and not output and absent:
        # A broken loose ref must never be classified as absent by show-ref.
        raw_path = git(repo, 'rev-parse', '--git-path', ref).decode().strip()
        path = Path(raw_path)
        if not path.is_absolute():
            path = repo / path
        if os.path.lexists(path):
            raise RotationError(f'broken or unreadable ref: {ref}')
        return None
    if rc:
        raise RotationError(f'ref unavailable or malformed: {ref}')
    return _hex(git(repo, 'show-ref', '--verify', '--hash', ref).decode().strip(), 40, 'ref object')


def _blob(repo: Path, oid: str) -> bytes:
    _check_memory_budget()
    maximum = min(MAX_SOURCE_BYTES, calibration_contract_v1()['maximum_memory_bytes'] // SOURCE_MEMORY_RESERVE_FACTOR)
    try:
        observed = _CUSTODY.read_object(repo, oid, maximum)
    except OSError as exc:
        raise RotationError(str(exc)) from exc
    if observed is not NotImplemented:
        _check_memory_budget(len(observed))
        return observed
    _hex(oid, 40, 'blob OID')
    if git(repo, 'cat-file', '-t', oid) != b'blob\n':
        raise RotationError('object is not a blob')
    size = git(repo, 'cat-file', '-s', oid).decode().strip()
    if not size.isdecimal() or int(size) > MAX_SOURCE_BYTES:
        raise RotationError('blob exceeds bounded source allocation')
    _check_memory_budget(int(size))
    raw = git(repo, 'cat-file', 'blob', oid)
    if len(raw) != int(size):
        raise RotationError('blob size readback mismatch')
    predicted = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if predicted != oid:
        raise RotationError('blob identity readback mismatch')
    return raw


def _store_blob(repo: Path, raw: bytes) -> str:
    oid = git(repo, 'hash-object', '-w', '--stdin', input_bytes=raw).decode().strip()
    if _blob(repo, oid) != raw:
        raise RotationError('stored blob readback mismatch')
    return oid


def _anchor_object(repo: Path, controller: str, raw: bytes) -> str:
    oid = _store_blob(repo, raw)
    ref = f'{ARCHIVE_PREFIX}/{controller}/objects/{oid}'
    old = _ref(repo, ref, absent=True)
    if old is None:
        git(repo, 'update-ref', ref, oid, ZERO_OID)
    elif old != oid:
        raise RotationError('retained object anchor drifted')
    if _ref(repo, ref) != oid or _blob(repo, oid) != raw:
        raise RotationError('retained object anchor readback failed')
    return oid


def _mkdir(path: Path, root: Path) -> None:
    with _directory_handle(path, root, create=True) as (descriptor, verify):
        verify()
        if _WINDOWS is not None:
            descriptor.flush()
        else:
            os.fsync(descriptor)


def _write_verified(path: Path, raw: bytes, root: Path, mode: int = 0o444) -> None:
    require_safe_directory_chain(path.parent, root)
    write_new_regular(path, raw, mode, custody_root=root)


def _source_path(repo: Path, run_root: Path, raw: str, role: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = repo / path
    path = Path(os.path.abspath(path))
    if path.name != role + '.md' or not contained(path, run_root):
        raise RotationError('predecessor canonical pair path is not contained')
    relative = path.relative_to(run_root).as_posix()
    if relative != role + '.md' and not re.fullmatch(
            r'state-generations/G[0-9A-F]{4}/' + role + r'\.md', relative):
        raise RotationError('predecessor pair path is not an admitted canonical location')
    return path


def _preliminary_artifacts(state: bytes, roadmap: bytes) -> list[dict]:
    rows = []
    for raw in (state, roadmap):
        try:
            body = raw.split(b'```json\n')[1].split(b'\n```')[0]
            parsed = _json(body, 'canonical pair body')
            refs = parsed['artifact_refs']
        except (IndexError, KeyError, TypeError) as exc:
            raise RotationError('unsupported canonical pair grammar; owner migration required') from exc
        if type(refs) is not list:
            raise RotationError('invalid source artifact declaration')
        rows.extend(refs)
    return rows


def _artifacts(repo: Path, run_root: Path, declarations: list[dict],
               *, source_bytes: int = 0) -> tuple[dict, list]:
    loaded, entries, seen_paths = {}, [], set()
    for row in declarations:
        if type(row) is not dict or set(row) != {'artifact_id', 'owner', 'role', 'locator', 'object_format'}:
            raise RotationError('source artifact fields are incomplete')
        aid, role, locator = row['artifact_id'], row['role'], row['locator']
        if type(aid) is not str or aid in loaded or row['object_format'] != 'sha1':
            raise RotationError('duplicate artifact or unsupported Git object format')
        if role == 'CONTINUITY_RECEIPT':
            if type(locator) is not str or not re.fullmatch(
                    r'refs/implementaudit/continuity-receipts/[a-z0-9-]+/G[0-9A-F]{4}', locator):
                raise RotationError('invalid continuity artifact locator')
            oid = _ref(repo, locator)
            raw, mode = _blob(repo, oid), '0444'
        elif role in {'WORK_GRAPH', 'EVIDENCE'}:
            locator = safe_relative(locator, SOURCE_EXCLUSIONS)
            if locator.casefold() in seen_paths:
                raise RotationError('duplicate physical artifact locator')
            seen_paths.add(locator.casefold())
            raw, info = read_regular(run_root / locator, run_root, locator, require_owner_write=False)
            mode = f'{stat.S_IMODE(info.st_mode):04o}'
        else:
            raise RotationError('unknown protected artifact role')
        if len(raw) > MAX_SOURCE_BYTES:
            raise RotationError('source artifact exceeds bounded allocation')
        source_bytes += len(raw)
        _check_memory_budget(source_bytes)
        loaded[aid] = raw
        entries.append({'role': role, 'artifact_id': aid, 'source_path': locator,
                        'owner': row['owner'], 'sha256': sha256(raw),
                        'byte_length': len(raw), 'mode': mode})
    return loaded, entries


def _parse(state: bytes, roadmap: bytes, owner_map: list, artifacts: dict) -> dict:
    try:
        return _hot_projection_module.parse_canonical_pair_v2(
            state, roadmap, owner_map=owner_map, artifacts=artifacts)
    except ValueError as exc:
        raise RotationError(str(exc)) from exc


def _validate_predecessor_schema(predecessor: dict) -> None:
    keys = {'controller', 'claim_id', 'run_root_identity', 'controller_oid',
            'receipt_ref', 'receipt_oid', 'receipt_schema', 'projection_generation_id',
            'continuity_epoch', 'invalidation_oid', 'pointer_ref', 'pointer_oid',
            'migration_marker_oid', 'head', 'tree', 'exact_next_action',
            'state_sha256', 'roadmap_sha256', 'state_path', 'roadmap_path'}
    if type(predecessor) is not dict or set(predecessor) != keys:
        raise RotationError('predecessor has missing or unknown fields')
    optional = {'pointer_oid', 'migration_marker_oid'}
    for key, value in predecessor.items():
        if key in optional and value is None:
            continue
        if type(value) is not str or not value or any(c in value for c in '\r\n\t\0'):
            raise RotationError('invalid predecessor field: ' + key)
    controller = predecessor['controller']
    for key in ('projection_generation_id', 'continuity_epoch'):
        _identity(controller, predecessor[key])
    for key in ('controller_oid', 'receipt_oid', 'head', 'tree', *optional):
        if predecessor[key] is not None:
            _hex(predecessor[key], 40, 'predecessor ' + key)
    if predecessor['invalidation_oid'] != 'none':
        _hex(predecessor['invalidation_oid'], 40, 'predecessor invalidation')
    for role in ('state', 'roadmap'):
        _hex(predecessor[role + '_sha256'], 64, 'predecessor ' + role + ' hash')
    run = safe_relative(predecessor['run_root_identity'], set())
    if (not re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[^/]+', run)
            or predecessor['pointer_ref'] != 'refs/implementaudit/current-generations/' + controller
            or predecessor['receipt_ref'] != 'refs/implementaudit/continuity-receipts/' + controller + '/' + predecessor['continuity_epoch']):
        raise RotationError('predecessor run/ref role mismatch')
    schema = predecessor['receipt_schema']
    if (schema not in {'implementaudit.continuity-receipt.v2', 'implementaudit.continuity-receipt.v3'}
            or (schema.endswith('.v2') and any(predecessor[k] is not None for k in optional))
            or (schema.endswith('.v3') and any(predecessor[k] is None for k in optional))):
        raise RotationError('predecessor receipt/pointer migration mismatch')


def _validate_predecessor_binding(preimage: dict, predecessor: dict) -> None:
    _validate_predecessor_schema(predecessor)
    identity = preimage['payload']['STATE']['identity']['value']
    action = preimage['payload']['STATE']['continuation']['value']['next_action']
    current = preimage['current_continuity']
    expected = {'controller': identity['controller_id'], 'claim_id': identity['claim_id'],
                'run_root_identity': identity['run_root_identity'], 'head': identity['candidate'],
                'tree': identity['tree'], 'exact_next_action': action,
                'continuity_epoch': current['continuity_epoch'],
                'projection_generation_id': current['projection_generation_id'],
                'receipt_schema': current['expected_receipt_schema'],
                'state_sha256': sha256(preimage['state_bytes']),
                'roadmap_sha256': sha256(preimage['roadmap_bytes'])}
    for key, value in expected.items():
        if predecessor.get(key) != value:
            raise RotationError('admitted predecessor differs from complete source: ' + key)
    if (predecessor['receipt_ref'] + '@' + predecessor['receipt_oid'] != preimage['current_receipt_ref_oid']
            or predecessor['receipt_ref'] != current['expected_receipt_ref']
            or (None if predecessor['invalidation_oid'] == 'none' else predecessor['invalidation_oid']) != current['invalidation_oid']):
        raise RotationError('admitted predecessor receipt/continuity differs from complete source')
    receipt_id = next(row['artifact_id'] for role in ('STATE', 'ROADMAP')
                      for row in preimage['bodies'][role]['artifact_refs']
                      if row['role'] == 'CONTINUITY_RECEIPT')
    fields = preimage['artifacts'][receipt_id].decode().removesuffix('\n').split('\t')
    if fields[0] == 'implementaudit.continuity-receipt.v2' and fields[2] != predecessor['controller_oid']:
        raise RotationError('admitted controller object differs from exact source receipt')
    if fields[0] == 'implementaudit.continuity-receipt.v3' and fields[7] != predecessor['pointer_oid']:
        raise RotationError('admitted pointer object differs from exact source receipt')


def _derive(preimage: dict, transition: dict | None, pointers: list,
            limits: tuple[int, int] = (MAX_STATE_BYTES, MAX_ROADMAP_BYTES)) -> dict:
    try:
        result = _hot_projection_module.derive_hot_pair_v2(
            preimage, transition=transition, archive_pointers=pointers,
            max_state_bytes=limits[0], max_roadmap_bytes=limits[1])
        _hot_projection_module.verify_projection_equivalence_v2(preimage, result)
    except ValueError as exc:
        raise RotationError(str(exc)) from exc
    return result


def _archive_entries(repo: Path, controller: str, records: list[tuple[dict, bytes]]) -> list:
    entries = []
    for metadata, raw in records:
        item = dict(metadata)
        item['blob_oid'] = _anchor_object(repo, controller, raw)
        if item['sha256'] != sha256(raw) or item['byte_length'] != len(raw):
            raise RotationError('archive input identity drift')
        entries.append(item)
    return entries


def _verify_archive_one(repo: Path, controller: str, archive_ref: str,
                        expected_sha256: str) -> tuple[dict, dict, str]:
    generation = archive_ref.rsplit('/', 1)[-1]
    if archive_ref != _identity(controller, generation):
        raise RotationError('archive ref is not a contained canonical archive')
    oid = _ref(repo, archive_ref)
    raw = _blob(repo, oid)
    if sha256(raw) != _hex(expected_sha256, 64, 'archive SHA-256'):
        raise RotationError('archive manifest hash mismatch')
    manifest = _canonical_json(raw, 'archive manifest')
    native = manifest.get('preparation_kind') == 'native-resume'
    if (set(manifest) != {'schema', 'controller', 'claim_id', 'run_root_identity',
                         'preparation_generation_id', 'predecessor', 'entries',
                         'projection_schema', 'owner_map_schema', 'discovery',
                         'retention', 'authority_ceiling', 'calibration'} | ({'preparation_kind'} if native else set())
            or manifest['schema'] != ARCHIVE_SCHEMA
            or manifest['controller'] != controller
            or manifest['preparation_generation_id'] != generation
            or manifest['projection_schema'] != PROJECTION_SCHEMA
            or manifest['owner_map_schema'] != 'implementaudit.rotation-owner-map.v2'
            or manifest['discovery'] != 'EXCLUDED_FROM_CURRENT_AND_RECURSIVE_POPULATIONS'
            or manifest['retention'] != 'NO_DELETE_WITHOUT_ACCEPTED_RETENTION_SUCCESSOR'
            or manifest['authority_ceiling'] != 'ARCHIVED_ONLY_HISTORY'):
        raise RotationError('archive schema, owner or authority mismatch')
    _validate_predecessor_schema(manifest['predecessor'])
    if native and manifest['predecessor']['receipt_schema'] != 'implementaudit.continuity-receipt.v3':
        raise RotationError('native resume archive requires a migrated predecessor')
    if manifest['calibration'] != calibration_contract_v1():
        raise RotationError('archive calibration contract drift')
    entries, seen = manifest['entries'], set()
    if type(entries) is not list or not entries:
        raise RotationError('archive population is empty')
    for entry in entries:
        if type(entry) is not dict or set(entry) != {
                'role', 'artifact_id', 'source_path', 'owner', 'sha256',
                'byte_length', 'mode', 'blob_oid'}:
            raise RotationError('archive member schema mismatch')
        if (any(type(entry[key]) is not str for key in entry if key != 'byte_length')
                or type(entry['byte_length']) is not int or not 0 <= entry['byte_length'] <= MAX_SOURCE_BYTES
                or not re.fullmatch('[0-7]{4}', entry['mode']) or not int(entry['mode'], 8) & 0o400
                or entry['role'] not in {'STATE_PREIMAGE', 'ROADMAP_PREIMAGE', 'OWNER_MAP', 'CONTINUITY_RECEIPT', 'WORK_GRAPH', 'EVIDENCE'}):
            raise RotationError('archive member role/type/mode mismatch')
        key = entry['artifact_id']
        if key in seen:
            raise RotationError('duplicate archive member')
        seen.add(key)
        member = _blob(repo, entry['blob_oid'])
        if (sha256(member) != entry['sha256'] or len(member) != entry['byte_length']
                or _ref(repo, f'{ARCHIVE_PREFIX}/{controller}/objects/{entry["blob_oid"]}') != entry['blob_oid']):
            raise RotationError('archive member identity or retention anchor mismatch')
    if not {'STATE', 'ROADMAP', 'OWNER_MAP'}.issubset(seen):
        raise RotationError('archive omits canonical preimage/owner population')
    indexed = {row['artifact_id']: row for row in entries}
    for aid, role, owner in (('STATE', 'STATE_PREIMAGE', 'STATE.md'),
                             ('ROADMAP', 'ROADMAP_PREIMAGE', 'ROADMAP.md'),
                             ('OWNER_MAP', 'OWNER_MAP', 'COMPLETE_PAIR_OWNER_MAP')):
        row = indexed[aid]
        if (row['role'] != role or row['owner'] != owner
                or (aid != 'OWNER_MAP' and row['source_path'] != owner)):
            raise RotationError('archive canonical member binding mismatch')
        if native and aid == 'OWNER_MAP':
            if (row['source_path'] != 'state-generations/' + generation + '/native-resume-owner-map.json'
                    or row['mode'] != f'{effective_mode(0o444):04o}'):
                raise RotationError('native resume owner map is not the exact immutable derived input')
        else:
            safe_relative(row['source_path'], SOURCE_EXCLUSIONS)
    preimage = _archive_preimage(repo, manifest)
    _validate_predecessor_binding(preimage, manifest['predecessor'])
    identity = preimage['payload']['STATE']['identity']['value']
    prior = manifest['predecessor']
    if (manifest['controller'] != identity['controller_id'] or manifest['claim_id'] != identity['claim_id']
            or manifest['run_root_identity'] != identity['run_root_identity']
            or generation != f"G{int(prior['projection_generation_id'][1:], 16) + 1:04X}"):
        raise RotationError('archive source genealogy mismatch')
    location = prior['run_root_identity'] + '/'
    if prior['receipt_schema'].endswith('.v3'):
        location += 'state-generations/' + prior['projection_generation_id'] + '/'
    for role in ('state', 'roadmap'):
        if prior[role + '_path'] != location + role.upper() + '.md':
            raise RotationError('archived predecessor path binding mismatch')
    refs = _preliminary_artifacts(preimage['state_bytes'], preimage['roadmap_bytes'])
    if seen != {'STATE', 'ROADMAP', 'OWNER_MAP'} | {row['artifact_id'] for row in refs}:
        raise RotationError('archive member denominator differs from complete source')
    for declaration in refs:
        row = indexed[declaration['artifact_id']]
        if (row['role'] != declaration['role'] or row['owner'] != declaration['owner']
                or row['source_path'] != declaration['locator']
                or (row['role'] == 'CONTINUITY_RECEIPT' and row['mode'] != '0444')):
            raise RotationError('archive artifact metadata differs from complete source')
        if row['role'] != 'CONTINUITY_RECEIPT':
            safe_relative(row['source_path'], SOURCE_EXCLUSIONS)
    if _ref(repo, archive_ref) != oid:
        raise RotationError('archive ref changed during verification')
    return manifest, preimage, oid


def _verify_retained_archives(repo: Path, preimage: dict) -> dict[str, str]:
    """Iterative exact dependency walk; history never becomes live discovery."""
    identity = preimage['payload']['STATE']['identity']['value']
    controller = identity['controller_id']
    pending = [(row, preimage['current_continuity']['projection_generation_id'])
               for row in preimage['protected_manifest']['ARCHIVED_ONLY_HISTORY']]
    verified, guards, metadata_bytes = {}, {}, 0
    while pending:
        pointer, source_generation = pending.pop()
        try:
            _hot_projection_module._v2_archive_pointer(pointer, controller)
        except ValueError as exc:
            raise RotationError(str(exc)) from exc
        if pointer['preparation_generation_id'] > source_generation:
            raise RotationError('retained archive genealogy is not strictly ancestral')
        ref = pointer['archive_ref']
        binding = (pointer['archive_manifest_oid'], pointer['archive_manifest_sha256'])
        if ref not in verified:
            manifest, source, oid = _verify_archive_one(repo, controller, ref, binding[1])
            if (oid != binding[0] or manifest['claim_id'] != identity['claim_id']
                    or manifest['run_root_identity'] != identity['run_root_identity']):
                raise RotationError('retained archive belongs to another exact source lineage')
            members = {canonical_bytes(row) for row in _pointers(source, ref, oid, binding[1], manifest['preparation_generation_id'])}
            verified[ref] = (binding, members)
            guards[ref] = oid
            guards.update({f'{ARCHIVE_PREFIX}/{controller}/objects/{entry["blob_oid"]}': entry['blob_oid']
                           for entry in manifest['entries']})
            metadata_bytes += sum(len(row) for row in members)
            _check_memory_budget(metadata_bytes)
            pending.extend((row, source['current_continuity']['projection_generation_id'])
                           for row in source['protected_manifest']['ARCHIVED_ONLY_HISTORY'])
        expected_binding, members = verified[ref]
        if expected_binding != binding or canonical_bytes(pointer) not in members:
            raise RotationError('retained pointer is not an exact archived population member')
    for ref, oid in guards.items():
        if _ref(repo, ref) != oid:
            raise RotationError('retained archive changed during genealogy verification')
    return guards


@_scoped_git
def verify_canonical_archive(repo: Path, controller: str, archive_ref: str,
                             expected_sha256: str) -> dict:
    repo = require_repo(str(repo))
    manifest, preimage, oid = _verify_archive_one(repo, controller, archive_ref, expected_sha256)
    _verify_retained_archives(repo, preimage)
    if _ref(repo, archive_ref) != oid:
        raise RotationError('archive changed during complete genealogy verification')
    return manifest


@_scoped_git
def archive_retention_guards(repo: Path, controller: str, archive_ref: str,
                             expected_sha256: str) -> dict[str, str]:
    """Return exact retained ref guards for the sole publisher's CAS transaction."""
    repo = require_repo(str(repo))
    manifest, preimage, oid = _verify_archive_one(repo, controller, archive_ref, expected_sha256)
    guards = _verify_retained_archives(repo, preimage)
    guards[archive_ref] = oid
    guards.update({f'{ARCHIVE_PREFIX}/{controller}/objects/{entry["blob_oid"]}': entry['blob_oid']
                   for entry in manifest['entries']})
    for ref, expected in guards.items():
        if _ref(repo, ref) != expected:
            raise RotationError('retention guard changed before publication handoff')
    return dict(sorted(guards.items()))


def _archive_preimage(repo: Path, manifest: dict) -> dict:
    _check_memory_budget(sum(entry['byte_length'] for entry in manifest['entries']))
    found, artifacts = {}, {}
    for entry in manifest['entries']:
        raw = _blob(repo, entry['blob_oid'])
        if entry['role'] in {'STATE_PREIMAGE', 'ROADMAP_PREIMAGE', 'OWNER_MAP'}:
            found[entry['role']] = raw
        else:
            artifacts[entry['artifact_id']] = raw
    owner = _json(found['OWNER_MAP'], 'archived owner map')
    if type(owner) is not dict or set(owner) != {'schema', 'owner_map'} or owner['schema'] != 'implementaudit.rotation-owner-map.v2':
        raise RotationError('archived owner map schema mismatch')
    return _parse(found['STATE_PREIMAGE'], found['ROADMAP_PREIMAGE'], owner['owner_map'], artifacts)


def _pointers(preimage: dict, archive_ref: str, archive_oid: str, archive_sha: str,
              preparation_generation: str) -> list:
    controller = preimage['payload']['STATE']['identity']['value']['controller_id']
    if archive_ref != _identity(controller, preparation_generation):
        raise RotationError('typed archive preparation genealogy mismatch')
    return [dict(entry, schema_version='implementaudit.typed-archive-pointer.v2',
                 archive_ref=archive_ref, archive_manifest_oid=archive_oid,
                 archive_manifest_sha256=archive_sha,
                 preparation_generation_id=preparation_generation,
                 authority='ARCHIVED_ONLY_HISTORY') for entry in preimage['archive_population']]


@_scoped_git
def prepare_canonical_draft(repo: Path, run_root: Path, controller: str,
                            generation: str, owner_map_path: Path,
                            predecessor: dict, calibration: dict) -> dict:
    """Called only after claim-run admission; creates no currentness authority."""
    return _prepare_canonical_draft(repo, run_root, controller, generation, owner_map_path,
                                    predecessor, calibration, native_resume=False)


@_scoped_git
def prepare_native_resume_draft(repo: Path, run_root: Path, controller: str,
                                generation: str, predecessor: dict) -> dict:
    """Preserve an exact migrated preimage after a native owner boundary.

    No caller owner map or protected updates are accepted. Only current source
    hashes and the already committed v3 receipt artifact are rebound. The native
    owner proves its boundary separately and remains the sole publisher.
    """
    import time
    started = time.monotonic()
    repo = require_repo(str(repo))
    run_root = require_run_root(str(run_root), repo)
    archive_ref = _identity(controller, generation)
    _validate_predecessor_schema(predecessor)
    if (predecessor['controller'] != controller
            or predecessor['run_root_identity'] != run_root.relative_to(repo).as_posix()
            or predecessor['receipt_schema'] != 'implementaudit.continuity-receipt.v3'
            or generation != f"G{int(predecessor['projection_generation_id'][1:], 16) + 1:04X}"):
        raise RotationError('native resume requires the exact migrated successor input')
    guards = {predecessor['pointer_ref']: predecessor['pointer_oid'],
              predecessor['receipt_ref']: predecessor['receipt_oid'],
              'refs/implementaudit/current-generation-migrations/' + controller: predecessor['migration_marker_oid']}

    def check_guards():
        if any(_ref(repo, ref) != oid for ref, oid in guards.items()):
            raise RotationError('native resume predecessor pointer, receipt or marker changed')

    check_guards()
    pointer_raw = _blob(repo, predecessor['pointer_oid'])
    pointer = _json(pointer_raw, 'native resume predecessor pointer')
    if canonical_bytes(pointer)[:-1] != pointer_raw:
        raise RotationError('native resume predecessor pointer is not the exact original wire')
    resolved = read_canonical_generation(repo, run_root, pointer)
    source = {role: resolved[role.lower() + '_bytes'] for role in ('STATE', 'ROADMAP')}
    for role in ('state', 'roadmap'):
        if (_source_path(repo, run_root, predecessor[role + '_path'], role.upper()) != resolved[role + '_path']
                or sha256(source[role.upper()]) != predecessor[role + '_sha256']):
            raise RotationError('native resume source differs from the committed immutable pair')
    declarations = _preliminary_artifacts(source['STATE'], source['ROADMAP'])
    artifacts, _ = _artifacts(repo, run_root, declarations,
                              source_bytes=sum(map(len, source.values())))
    receipt_id = next(row['artifact_id'] for row in declarations if row['role'] == 'CONTINUITY_RECEIPT')
    expected_receipt = ['implementaudit.continuity-receipt.v3', pointer['controller'], pointer['claim_id'],
                        pointer['run_root_identity'], pointer['continuity_epoch'], pointer['invalidation_oid'],
                        predecessor['pointer_ref'], predecessor['pointer_oid'], pointer['state_sha256'],
                        pointer['roadmap_sha256'], pointer['protected_manifest_sha256'],
                        pointer['archive_manifest_sha256'], pointer['exact_next_action'],
                        pointer['predecessor_receipt_ref_oid']]
    if artifacts[receipt_id] != ('\t'.join(expected_receipt) + '\n').encode('utf-8'):
        raise RotationError('native resume receipt does not bind the exact committed pointer')
    protected = resolved['protected_manifest']['PRESERVED_PAYLOAD']
    rows = [dict(row) for row in protected['owner_map']]
    for row in rows:
        if row['source_kind'] == 'PAIR':
            row['source_sha256'] = sha256(source[row['source_id']])
        elif row['source_id'] == receipt_id:
            row['source_sha256'] = row['value_sha256'] = sha256(artifacts[receipt_id])
    preimage = _parse(source['STATE'], source['ROADMAP'], rows, artifacts)
    _validate_predecessor_binding(preimage, predecessor)
    if preimage['payload'] != protected['payload']:
        raise RotationError('native resume changed a protected source value or owner')
    _verify_retained_archives(repo, preimage)
    check_guards()
    owner_map_path = run_root / 'state-generations' / generation / 'native-resume-owner-map.json'
    owner_raw = canonical_bytes({'schema': 'implementaudit.rotation-owner-map.v2', 'owner_map': rows})
    _check_memory_budget(sum(map(len, source.values())) + len(owner_raw) + sum(map(len, artifacts.values())))
    archive_oid = _ref(repo, archive_ref, absent=True)
    if archive_oid is not None:
        prepared = _read_native_preparation(repo, run_root, controller, generation, predecessor,
                                            source, owner_raw, archive_oid)
    else:
        _mkdir(owner_map_path.parent, run_root)
        _write_verified(owner_map_path, owner_raw, run_root)
        prepared = _prepare_canonical_draft(repo, run_root, controller, generation, owner_map_path,
                                            predecessor, calibration_contract_v1(), native_resume=True,
                                            started=started)
    check_guards()
    _check_memory_budget()
    if (time.monotonic() - started) * 1000 > calibration_contract_v1()['maximum_runtime_ms']:
        raise RotationError('native preparation readback exceeds frozen runtime bound')
    return prepared


def _draft_manifest(controller: str, generation: str, archive_ref: str,
                     archive_oid: str, archive_sha: str, draft: dict) -> dict:
    return {
        'schema': 'implementaudit.canonical-state-projection-draft.v2',
        'controller': controller, 'preparation_generation_id': generation,
        'archive_ref': archive_ref, 'archive_manifest_oid': archive_oid,
        'archive_manifest_sha256': archive_sha,
        'state_sha256': sha256(draft['state_bytes']),
        'roadmap_sha256': sha256(draft['roadmap_bytes']),
        'protected_manifest_sha256': sha256(canonical_bytes(draft['protected_manifest'])),
        'transition': None, 'authority_ceiling': 'NO_CURRENTNESS_AUTHORITY',
    }


def _read_native_preparation(repo: Path, run_root: Path, controller: str,
                              generation: str, predecessor: dict, source: dict,
                              owner_raw: bytes, archive_oid: str) -> dict:
    """Reuse only a complete identical F2; never repair or overwrite a generation."""
    generation_dir = run_root / 'state-generations' / generation
    draft_dir = generation_dir / 'draft'
    for path, expected in ((generation_dir, {'draft', 'native-resume-owner-map.json'}),
                            (draft_dir, {'STATE.md', 'ROADMAP.md', 'protected-state.json', 'draft-manifest.json'})):
        with _directory_handle(path, run_root) as (descriptor, verify):
            if set(descriptor.names() if _WINDOWS is not None else os.listdir(descriptor)) != expected:
                raise RotationError('native preparation is incomplete, changed or already finalized')
            verify()
    landed, info = read_regular(generation_dir / 'native-resume-owner-map.json', run_root,
                                'derived native owner map', require_owner_write=False)
    if landed != owner_raw or stat.S_IMODE(info.st_mode) != effective_mode(0o444):
        raise RotationError('native preparation derived owner map drift')
    draft_raw, _ = read_regular(draft_dir / 'draft-manifest.json', run_root,
                                'native draft manifest', require_owner_write=False)
    sizes = [len(read_regular(draft_dir / name, run_root, name, require_owner_write=False)[0])
             for name in ('STATE.md', 'ROADMAP.md')]
    archive_ref = _identity(controller, generation)
    live_bytes = sum(map(len, source.values()))
    prepared = {
        'schema': 'implementaudit.native-resume-prepared.v1', 'triggered': True,
        'controller': controller, 'generation_id': generation,
        'archive_ref': archive_ref, 'archive_manifest_oid': archive_oid,
        'archive_manifest_sha256': sha256(_blob(repo, archive_oid)),
        'draft_path': draft_dir.relative_to(run_root).as_posix(),
        'draft_manifest_sha256': sha256(draft_raw),
        'source_state_sha256': sha256(source['STATE']), 'source_roadmap_sha256': sha256(source['ROADMAP']),
        'exact_next_action': predecessor['exact_next_action'], 'predecessor': predecessor,
        'calibration': calibration_contract_v1(),
        'measurement': {'live_bytes_before': live_bytes, 'live_byte_reduction': live_bytes - sum(sizes),
                        'model_calls': 0, 'host_qualification': 'SEPARATE_NOT_INFERRED'},
        'authority_ceiling': 'NO_CURRENTNESS_AUTHORITY',
    }
    manifest, preimage, pointers = _checked_prepared(repo, run_root, prepared)
    owner_entry = next(row for row in manifest['entries'] if row['role'] == 'OWNER_MAP')
    if _blob(repo, owner_entry['blob_oid']) != owner_raw:
        raise RotationError('native archive differs from the exact derived owner map')
    _verify_projection_draft(run_root, preimage, pointers, prepared)
    return prepared


def _prepare_canonical_draft(repo: Path, run_root: Path, controller: str,
                             generation: str, owner_map_path: Path, predecessor: dict,
                             calibration: dict, *, native_resume: bool,
                             started: float | None = None) -> dict:
    import time
    started = time.monotonic() if started is None else started
    repo = require_repo(str(repo))
    run_root = require_run_root(str(run_root), repo)
    archive_ref = _identity(controller, generation)
    _validate_predecessor_schema(predecessor)
    if (calibration != calibration_contract_v1() or predecessor.get('controller') != controller
            or predecessor.get('run_root_identity') != run_root.relative_to(repo).as_posix()):
        raise RotationError('predecessor identity or frozen calibration contract mismatch')
    source = {}
    infos = {}
    for role in ('STATE', 'ROADMAP'):
        path = _source_path(repo, run_root, predecessor[role.lower() + '_path'], role)
        raw, info = read_regular(path, run_root, role, require_owner_write=False)
        if len(raw) > MAX_SOURCE_BYTES or sha256(raw) != predecessor[role.lower() + '_sha256']:
            raise RotationError('current preimage size or hash mismatch')
        source[role], infos[role] = raw, info
    live_bytes = len(source['STATE']) + len(source['ROADMAP'])
    if not native_resume and live_bytes < calibration['byte_threshold']:
        return {'triggered': False, 'reason': 'BELOW_FROZEN_BYTE_THRESHOLD',
                'live_bytes': live_bytes, 'archive_writes': 0, 'model_calls': 0,
                'authority_ceiling': 'NO_CURRENTNESS_AUTHORITY'}
    _check_memory_budget(live_bytes)
    if _ref(repo, archive_ref, absent=True) is not None:
        raise RotationError('preparation generation was already used')
    owner_map_path = Path(owner_map_path)
    if not owner_map_path.is_absolute():
        owner_map_path = run_root / owner_map_path
    if native_resume and (predecessor['receipt_schema'] != 'implementaudit.continuity-receipt.v3'
                          or owner_map_path != run_root / 'state-generations' / generation / 'native-resume-owner-map.json'):
        raise RotationError('native resume map must be the exact derived successor input')
    owner_raw, owner_info = read_regular(owner_map_path, run_root, 'owner map', require_owner_write=False)
    _check_memory_budget(live_bytes + len(owner_raw))
    owner = _json(owner_raw, 'owner map')
    if type(owner) is not dict or set(owner) != {'schema', 'owner_map'} or owner['schema'] != 'implementaudit.rotation-owner-map.v2':
        raise RotationError('complete owner map schema is required')
    artifacts, artifact_entries = _artifacts(
        repo, run_root, _preliminary_artifacts(source['STATE'], source['ROADMAP']),
        source_bytes=live_bytes + len(owner_raw))
    preimage = _parse(source['STATE'], source['ROADMAP'], owner['owner_map'], artifacts)
    _check_memory_budget()
    _validate_predecessor_binding(preimage, predecessor)
    _verify_retained_archives(repo, preimage)
    token = predecessor['receipt_ref'] + '@' + predecessor['receipt_oid']
    if (preimage['current_receipt_ref_oid'] != token
            or _ref(repo, predecessor['receipt_ref']) != predecessor['receipt_oid']):
        raise RotationError('source receipt is not exact admitted predecessor')
    expected_generation = f"G{int(preimage['current_continuity']['projection_generation_id'][1:], 16) + 1:04X}"
    if generation != expected_generation:
        raise RotationError('preparation generation must be the exact unused successor')
    records = []
    for role in ('STATE', 'ROADMAP'):
        records.append(({'role': role + '_PREIMAGE', 'artifact_id': role,
                         'source_path': role + '.md', 'owner': role + '.md',
                         'sha256': sha256(source[role]), 'byte_length': len(source[role]),
                         'mode': f'{stat.S_IMODE(infos[role].st_mode):04o}'}, source[role]))
    records.append(({'role': 'OWNER_MAP', 'artifact_id': 'OWNER_MAP',
                     'source_path': owner_map_path.relative_to(run_root).as_posix(),
                     'owner': 'COMPLETE_PAIR_OWNER_MAP', 'sha256': sha256(owner_raw),
                     'byte_length': len(owner_raw), 'mode': f'{stat.S_IMODE(owner_info.st_mode):04o}'}, owner_raw))
    records.extend((entry, artifacts[entry['artifact_id']]) for entry in artifact_entries)
    bound_predecessor = dict(predecessor)
    for role in ('state', 'roadmap'):
        bound_predecessor[role + '_path'] = _source_path(repo, run_root, predecessor[role + '_path'], role.upper()).relative_to(repo).as_posix()
    manifest = {
        'schema': ARCHIVE_SCHEMA, 'controller': controller,
        'claim_id': predecessor['claim_id'], 'run_root_identity': predecessor['run_root_identity'],
        'preparation_generation_id': generation, 'predecessor': bound_predecessor,
        'entries': _archive_entries(repo, controller, records),
        'projection_schema': PROJECTION_SCHEMA, 'owner_map_schema': owner['schema'],
        'discovery': 'EXCLUDED_FROM_CURRENT_AND_RECURSIVE_POPULATIONS',
        'retention': 'NO_DELETE_WITHOUT_ACCEPTED_RETENTION_SUCCESSOR',
        'authority_ceiling': 'ARCHIVED_ONLY_HISTORY', 'calibration': calibration,
    }
    if native_resume:
        manifest['preparation_kind'] = 'native-resume'
    archive_raw = canonical_bytes(manifest)
    archive_oid = _store_blob(repo, archive_raw)
    git(repo, 'update-ref', archive_ref, archive_oid, ZERO_OID)
    verify_canonical_archive(repo, controller, archive_ref, sha256(archive_raw))
    pointers = _pointers(preimage, archive_ref, archive_oid, sha256(archive_raw), generation)
    draft = _derive(preimage, None, pointers)
    _check_memory_budget()
    reduction = live_bytes - len(draft['state_bytes']) - len(draft['roadmap_bytes'])
    if not native_resume and reduction < calibration['minimum_live_byte_reduction']:
        raise RotationError('measured live-state reduction is below frozen minimum; archive retained')
    generation_root = run_root / 'state-generations' / generation
    draft_dir = generation_root / 'draft'
    if os.path.lexists(draft_dir):
        raise RotationError('draft already exists; overwrite refused')
    _mkdir(draft_dir, run_root)
    draft_manifest = _draft_manifest(controller, generation, archive_ref, archive_oid, sha256(archive_raw), draft)
    try:
        for name, raw in [('STATE.md', draft['state_bytes']), ('ROADMAP.md', draft['roadmap_bytes']),
                          ('protected-state.json', canonical_bytes(draft['protected_manifest'])),
                          ('draft-manifest.json', canonical_bytes(draft_manifest))]:
            _write_verified(draft_dir / name, raw, run_root)
    except BaseException:
        # No cleanup can discard exact preimage or an anchored archive.
        raise
    elapsed_ms = int((time.monotonic() - started) * 1000)
    _check_memory_budget()
    if elapsed_ms > calibration['maximum_runtime_ms']:
        raise RotationError('draft/archive runtime exceeds frozen bound; undiscoverable draft retained')
    return {
        'schema': 'implementaudit.native-resume-prepared.v1' if native_resume else 'implementaudit.canonical-prepared.v2',
        'triggered': True,
        'controller': controller, 'generation_id': generation,
        'archive_ref': archive_ref, 'archive_manifest_oid': archive_oid,
        'archive_manifest_sha256': sha256(archive_raw),
        'draft_path': draft_dir.relative_to(run_root).as_posix(),
        'draft_manifest_sha256': sha256(canonical_bytes(draft_manifest)),
        'source_state_sha256': sha256(source['STATE']),
        'source_roadmap_sha256': sha256(source['ROADMAP']),
        'exact_next_action': predecessor['exact_next_action'],
        'predecessor': predecessor, 'calibration': calibration,
        'measurement': {'live_bytes_before': live_bytes, 'live_byte_reduction': reduction,
                        'model_calls': 0,
                        'host_qualification': 'SEPARATE_NOT_INFERRED'},
        'authority_ceiling': 'NO_CURRENTNESS_AUTHORITY',
    }


def _checked_prepared(repo: Path, run_root: Path, prepared: dict) -> tuple[dict, dict, list]:
    fields = {'schema', 'triggered', 'controller', 'generation_id', 'archive_ref',
              'archive_manifest_oid', 'archive_manifest_sha256', 'draft_path', 'draft_manifest_sha256',
              'source_state_sha256', 'source_roadmap_sha256', 'exact_next_action', 'predecessor',
              'calibration', 'measurement', 'authority_ceiling'}
    if (type(prepared) is not dict or set(prepared) != fields
            or prepared.get('schema') not in {'implementaudit.canonical-prepared.v2', 'implementaudit.native-resume-prepared.v1'}
            or prepared.get('triggered') is not True
            or prepared.get('authority_ceiling') != 'NO_CURRENTNESS_AUTHORITY'):
        raise RotationError('invalid prepared descriptor')
    controller, generation = prepared['controller'], prepared['generation_id']
    if (prepared['archive_ref'] != _identity(controller, generation)
            or prepared['draft_path'] != 'state-generations/' + generation + '/draft'):
        raise RotationError('prepared archive scope drift')
    manifest = verify_canonical_archive(repo, controller, prepared['archive_ref'],
                                        prepared['archive_manifest_sha256'])
    if ((prepared['schema'] == 'implementaudit.native-resume-prepared.v1')
            != (manifest.get('preparation_kind') == 'native-resume')):
        raise RotationError('prepared operation differs from anchored archive kind')
    if _ref(repo, prepared['archive_ref']) != prepared['archive_manifest_oid']:
        raise RotationError('prepared archive object drift')
    predecessor = dict(prepared['predecessor'])
    for role in ('state', 'roadmap'):
        predecessor[role + '_path'] = _source_path(
            repo, run_root, predecessor[role + '_path'], role.upper()).relative_to(repo).as_posix()
    if (predecessor != manifest['predecessor']
            or manifest['run_root_identity'] != run_root.relative_to(repo).as_posix()
            or prepared['calibration'] != manifest['calibration']
            or prepared['calibration'] != calibration_contract_v1()):
        raise RotationError('prepared owner/predecessor/calibration drift')
    preimage = _archive_preimage(repo, manifest)
    _validate_predecessor_binding(preimage, predecessor)
    if (sha256(preimage['state_bytes']) != prepared['source_state_sha256']
            or sha256(preimage['roadmap_bytes']) != prepared['source_roadmap_sha256']
            or prepared['exact_next_action'] != predecessor['exact_next_action']):
        raise RotationError('prepared source or continuation drift')
    pointers = _pointers(preimage, prepared['archive_ref'], prepared['archive_manifest_oid'],
                         prepared['archive_manifest_sha256'], generation)
    draft = _derive(preimage, None, pointers)
    live_bytes = len(preimage['state_bytes']) + len(preimage['roadmap_bytes'])
    measured = {'live_bytes_before': live_bytes,
                'live_byte_reduction': live_bytes - len(draft['state_bytes']) - len(draft['roadmap_bytes']),
                'model_calls': 0, 'host_qualification': 'SEPARATE_NOT_INFERRED'}
    if canonical_bytes(prepared['measurement']) != canonical_bytes(measured):
        raise RotationError('prepared measurement is not the exact source-derived population')
    return manifest, preimage, pointers


def _pure_transition(preimage: dict, prepared: dict, transition: dict) -> dict:
    expected_keys = {
        'schema', 'controller', 'claim_id', 'run_root_identity',
        'projection_generation_id', 'continuity_epoch', 'boundary', 'invalidation_oid',
        'predecessor_receipt_ref_oid', 'expected_receipt_ref_schema', 'transition_kind',
        'payload_source', 'failed_transition_epoch', 'head', 'tree',
    }
    allowed = expected_keys | {'failed_transition_generation', 'failed_transition_receipt_ref_oid'}
    if (type(transition) is not dict or not expected_keys.issubset(transition)
            or not set(transition).issubset(allowed)):
        raise RotationError('invalid or cyclic transition envelope')
    native = transition['transition_kind'] == 'native-resume'
    if native:
        if (set(transition) != allowed or transition['schema'] != 'implementaudit.native-resume-transition.v1'
                or type(transition['boundary']) is not str
                or transition['boundary'] not in _hot_projection_module._V2_NATIVE_BOUNDARIES
                or prepared['schema'] != 'implementaudit.native-resume-prepared.v1'):
            raise RotationError('native resume transition schema, boundary or preparation mismatch')
    elif (transition['schema'] != 'implementaudit.rotation-transition.v1'
          or transition['boundary'] != 'canonical-state-rotation'
          or prepared['schema'] != 'implementaudit.canonical-prepared.v2'):
        raise RotationError('rotation transition schema, boundary or preparation mismatch')
    predecessor = prepared['predecessor']
    for key in ('controller', 'claim_id', 'run_root_identity', 'head', 'tree'):
        if transition[key] != predecessor[key]:
            raise RotationError('transition changed predecessor owner/candidate identity')
    failed_receipt = transition.get('failed_transition_receipt_ref_oid')
    actual_predecessor = failed_receipt or preimage['current_receipt_ref_oid']
    if transition['predecessor_receipt_ref_oid'] != actual_predecessor:
        raise RotationError('transition substituted actual available predecessor receipt')
    generation = transition['projection_generation_id']
    _identity(transition['controller'], generation)
    _hex(transition['invalidation_oid'], 40, 'transition invalidation')
    receipt = transition['expected_receipt_ref_schema']
    if (type(receipt) is not dict or set(receipt) != {'ref', 'schema'}
            or receipt['schema'] != 'implementaudit.continuity-receipt.v3'
            or receipt['ref'] != f'refs/implementaudit/continuity-receipts/{transition["controller"]}/{transition["continuity_epoch"]}'):
        raise RotationError('successor receipt ref/schema mismatch')
    kind = transition['transition_kind']
    failed_generation = transition.get('failed_transition_generation')
    if kind in {'rotation', 'native-resume'}:
        if (transition['payload_source'] != ('preimage' if native else 'draft')
                or transition['failed_transition_epoch'] is not None
                or failed_generation is not None or failed_receipt is not None
                or generation != prepared['generation_id']):
            raise RotationError('non-recovery transition acquired a recovery or reused generation')
    elif kind == 'recovery':
        if (transition['payload_source'] != 'preimage'
                or failed_generation != prepared['generation_id']):
            raise RotationError('recovery does not bind the exact failed allocation and archived prior payload')
    else:
        raise RotationError('unknown rotation transition kind')
    prior = preimage['current_continuity']
    return {
        'schema_version': 'implementaudit.native-resume-transition.v1' if native else 'implementaudit.canonical-state-transition.v2',
        'boundary': transition['boundary'],
        'reconciled': True,
        'predecessor_generation_id': prior['projection_generation_id'],
        'projection_generation_id': generation,
        'predecessor_epoch': prior['continuity_epoch'],
        'continuity_epoch': transition['continuity_epoch'],
        'invalidation_oid': transition['invalidation_oid'],
        'predecessor_receipt_ref_oid': transition['predecessor_receipt_ref_oid'],
        'expected_receipt_ref': receipt['ref'], 'expected_receipt_schema': receipt['schema'],
        'transition_kind': kind, 'failed_transition_epoch': transition['failed_transition_epoch'],
        'failed_projection_generation_id': failed_generation,
        'failed_transition_receipt_ref_oid': failed_receipt,
    }


def _verify_failed_receipt(repo: Path, run_root: Path, prepared: dict, transition: dict) -> None:
    token = transition.get('failed_transition_receipt_ref_oid')
    if token is None:
        return
    if (type(token) is not str or token.count('@') != 1
            or transition['transition_kind'] != 'recovery'):
        raise RotationError('invalid failed transition receipt token')
    ref, oid = token.split('@')
    expected_ref = f'refs/implementaudit/continuity-receipts/{transition["controller"]}/{transition["failed_transition_epoch"]}'
    if ref != expected_ref or _ref(repo, ref) != oid:
        raise RotationError('failed transition receipt ref is not the actual retained object')
    raw = _blob(repo, oid)
    try:
        fields = raw.decode('utf-8').removesuffix('\n').split('\t')
    except UnicodeDecodeError as exc:
        raise RotationError('failed receipt is not UTF-8') from exc
    if len(fields) != 14 or ('\t'.join(fields) + '\n').encode() != raw:
        raise RotationError('failed receipt is not original fourteen-field v3')
    failed_pointer_raw = _blob(repo, _hex(fields[7], 40, 'failed pointer OID'))
    failed_pointer = _json(failed_pointer_raw, 'failed pointer')
    expected_pointer_raw = json.dumps(failed_pointer, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    if failed_pointer_raw != expected_pointer_raw or set(failed_pointer) != POINTER_FIELDS:
        raise RotationError('failed receipt pointer object is not exact original schema')
    expected_fields = [
        'implementaudit.continuity-receipt.v3', transition['controller'], transition['claim_id'],
        transition['run_root_identity'], transition['failed_transition_epoch'],
        failed_pointer['invalidation_oid'], f'refs/implementaudit/current-generations/{transition["controller"]}',
        fields[7], failed_pointer['state_sha256'], failed_pointer['roadmap_sha256'],
        failed_pointer['protected_manifest_sha256'], failed_pointer['archive_manifest_sha256'],
        prepared['exact_next_action'], failed_pointer['predecessor_receipt_ref_oid'],
    ]
    if (fields != expected_fields or failed_pointer['projection_generation_id'] != transition['failed_transition_generation']
            or failed_pointer['predecessor_receipt_ref_oid'] != prepared['predecessor']['receipt_ref'] + '@' + prepared['predecessor']['receipt_oid']):
        raise RotationError('failed receipt/pointer does not bind the exact failed allocation')
    read_canonical_generation(repo, run_root, failed_pointer)


def _verify_projection_draft(run_root: Path, preimage: dict, pointers: list, prepared: dict) -> None:
    draft_dir = run_root / safe_relative(prepared['draft_path'], {'.git', 'quarantine'})
    if draft_dir != run_root / 'state-generations' / prepared['generation_id'] / 'draft':
        raise RotationError('draft location drift')
    draft = _derive(preimage, None, pointers)
    manifest = _draft_manifest(prepared['controller'], prepared['generation_id'], prepared['archive_ref'],
                               prepared['archive_manifest_oid'], prepared['archive_manifest_sha256'], draft)
    manifest_raw = canonical_bytes(manifest)
    if sha256(manifest_raw) != prepared['draft_manifest_sha256']:
        raise RotationError('draft manifest differs from exact absent-transition envelope')
    for name, expected in [('STATE.md', draft['state_bytes']), ('ROADMAP.md', draft['roadmap_bytes']),
                           ('protected-state.json', canonical_bytes(draft['protected_manifest'])),
                           ('draft-manifest.json', manifest_raw)]:
        landed, info = read_regular(draft_dir / name, run_root, name, require_owner_write=False)
        if landed != expected or stat.S_IMODE(info.st_mode) != effective_mode(0o444):
            raise RotationError('draft bytes or immutable modes differ from original deterministic oracle')


@_scoped_git
def finalize_canonical_projection(repo: Path, run_root: Path, prepared: dict,
                                  transition: dict) -> dict:
    """Finalize immutable bytes after native owner allocation, never publish them."""
    repo = require_repo(str(repo))
    run_root = require_run_root(str(run_root), repo)
    manifest, preimage, pointers = _checked_prepared(repo, run_root, prepared)
    pure_transition = _pure_transition(preimage, prepared, transition)
    _verify_failed_receipt(repo, run_root, prepared, transition)
    # Existence and exact bytes are necessary; claim-run separately proves the
    # invalidation's native controller/epoch provenance and currentness.
    _blob(repo, transition['invalidation_oid'])
    if transition['transition_kind'] in {'rotation', 'native-resume'}:
        _verify_projection_draft(run_root, preimage, pointers, prepared)
    candidate = _derive(preimage, pure_transition, pointers)
    generation = transition['projection_generation_id']
    generation_dir = run_root / 'state-generations' / generation
    _mkdir(generation_dir, run_root)
    protected_raw = canonical_bytes(candidate['protected_manifest'])
    archive_raw = canonical_bytes(manifest)
    generation_manifest = {
        'schema': 'implementaudit.canonical-generation-files.v2',
        'prepared': prepared, 'transition': transition,
        'limits': {'max_state_bytes': MAX_STATE_BYTES, 'max_roadmap_bytes': MAX_ROADMAP_BYTES},
        'authority_ceiling': 'NO_CURRENTNESS_AUTHORITY',
    }
    for name, raw in [('STATE.md', candidate['state_bytes']), ('ROADMAP.md', candidate['roadmap_bytes']),
                      ('protected-state.json', protected_raw), ('archive-manifest.json', archive_raw),
                      ('generation-manifest.json', canonical_bytes(generation_manifest))]:
        _write_verified(generation_dir / name, raw, run_root)
    pointer = {
        'schema': POINTER_SCHEMA, 'controller': transition['controller'],
        'claim_id': transition['claim_id'], 'run_root_identity': transition['run_root_identity'],
        'projection_generation_id': generation, 'continuity_epoch': transition['continuity_epoch'],
        'invalidation_oid': transition['invalidation_oid'],
        'predecessor_receipt_ref_oid': transition['predecessor_receipt_ref_oid'],
        'expected_receipt_ref_schema': transition['expected_receipt_ref_schema'],
        'projection_schema': PROJECTION_SCHEMA,
        'state_sha256': sha256(candidate['state_bytes']),
        'roadmap_sha256': sha256(candidate['roadmap_bytes']),
        'protected_manifest_sha256': sha256(protected_raw),
        'archive_manifest_sha256': sha256(archive_raw),
        'exact_next_action': prepared['exact_next_action'],
    }
    read_canonical_generation(repo, run_root, pointer)
    return {'pointer': pointer, 'generation_dir': generation_dir}


@_scoped_git
def read_canonical_generation(repo: Path, run_root: Path, pointer: dict) -> dict:
    """Verify a contained immutable generation; only claim-run can join currentness."""
    repo = require_repo(str(repo))
    run_root = require_run_root(str(run_root), repo)
    if (type(pointer) is not dict or set(pointer) != POINTER_FIELDS
            or pointer['schema'] != POINTER_SCHEMA or pointer['projection_schema'] != PROJECTION_SCHEMA
            or pointer['run_root_identity'] != run_root.relative_to(repo).as_posix()):
        raise RotationError('canonical pointer schema/owner mismatch')
    _identity(pointer['controller'], pointer['projection_generation_id'])
    generation_dir = run_root / 'state-generations' / pointer['projection_generation_id']
    require_safe_directory_chain(generation_dir, run_root)
    files = {}
    for name in ('STATE.md', 'ROADMAP.md', 'protected-state.json', 'archive-manifest.json', 'generation-manifest.json'):
        raw, info = read_regular(generation_dir / name, run_root, name, require_owner_write=False)
        if stat.S_IMODE(info.st_mode) != effective_mode(0o444):
            raise RotationError('immutable generation file permissions drift')
        files[name] = raw
    for name, field in [('STATE.md', 'state_sha256'), ('ROADMAP.md', 'roadmap_sha256'),
                        ('protected-state.json', 'protected_manifest_sha256'),
                        ('archive-manifest.json', 'archive_manifest_sha256')]:
        if sha256(files[name]) != _hex(pointer[field], 64, field):
            raise RotationError('canonical generation hash mismatch: ' + name)
    generation_manifest = _canonical_json(files['generation-manifest.json'], 'generation manifest')
    if (set(generation_manifest) != {'schema', 'prepared', 'transition', 'limits', 'authority_ceiling'}
            or generation_manifest['schema'] != 'implementaudit.canonical-generation-files.v2'
            or generation_manifest['authority_ceiling'] != 'NO_CURRENTNESS_AUTHORITY'
            or generation_manifest['limits'] != {'max_state_bytes': MAX_STATE_BYTES, 'max_roadmap_bytes': MAX_ROADMAP_BYTES}):
        raise RotationError('generation manifest schema/limits drift')
    prepared, transition = generation_manifest['prepared'], generation_manifest['transition']
    manifest, preimage, pointers = _checked_prepared(repo, run_root, prepared)
    pure_transition = _pure_transition(preimage, prepared, transition)
    _verify_failed_receipt(repo, run_root, prepared, transition)
    for key in ('controller', 'claim_id', 'run_root_identity', 'projection_generation_id',
                'continuity_epoch', 'invalidation_oid', 'predecessor_receipt_ref_oid', 'expected_receipt_ref_schema'):
        if pointer[key] != transition[key]:
            raise RotationError('pointer/transition binding mismatch: ' + key)
    if pointer['exact_next_action'] != prepared['exact_next_action']:
        raise RotationError('pointer continuation mismatch')
    _blob(repo, transition['invalidation_oid'])
    candidate = _derive(preimage, pure_transition, pointers)
    if (files['STATE.md'] != candidate['state_bytes'] or files['ROADMAP.md'] != candidate['roadmap_bytes']
            or files['protected-state.json'] != canonical_bytes(candidate['protected_manifest'])
            or files['archive-manifest.json'] != canonical_bytes(manifest)):
        raise RotationError('final projection differs from complete preimage equivalence oracle')
    return {'state_bytes': files['STATE.md'], 'roadmap_bytes': files['ROADMAP.md'],
            'protected_manifest': candidate['protected_manifest'], 'archive_manifest': manifest,
            'state_path': generation_dir / 'STATE.md', 'roadmap_path': generation_dir / 'ROADMAP.md'}


@_scoped_git
def resolve_typed_archive_pointer_v2(repo: Path, pointer: dict) -> dict:
    """Selective, hash-exact historical retrieval with no current selection."""
    if type(pointer) is not dict or pointer.get('authority') != 'ARCHIVED_ONLY_HISTORY':
        raise RotationError('typed historical pointer required')
    ref = pointer.get('archive_ref', '')
    parts = ref.split('/')
    if len(parts) != 5:
        raise RotationError('typed archive scope is invalid')
    controller = parts[3]
    manifest = verify_canonical_archive(repo, controller, ref, pointer['archive_manifest_sha256'])
    if _ref(repo, ref) != pointer['archive_manifest_oid']:
        raise RotationError('typed archive manifest object mismatch')
    preimage = _archive_preimage(repo, manifest)
    expected = _pointers(preimage, ref, pointer['archive_manifest_oid'],
                         pointer['archive_manifest_sha256'], pointer['preparation_generation_id'])
    if pointer not in expected:
        raise RotationError('typed pointer is not an exact archived population member')
    raw = _blob(repo, pointer['blob_oid'])
    if pointer['role'] == 'HISTORY_RECORD':
        body = _json(raw.split(b'```json\n')[1].split(b'\n```')[0], 'historical pair')
        index = int(pointer['source_pointer'].split('/')[-1])
        selected = body['history'][index]
        data = json.dumps(selected, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    else:
        data = raw
    if sha256(data) != pointer['record_sha256']:
        raise RotationError('typed historical record hash mismatch')
    return {'bytes': data, 'record_id': pointer['record_id'], 'role': pointer['role'],
            'authority_ceiling': 'ARCHIVED_ONLY_HISTORY', 'original_scope_preserved': True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('calibration-contract')
    check = sub.add_parser('verify-archive')
    check.add_argument('--repo-root', required=True)
    check.add_argument('--controller', required=True)
    check.add_argument('--archive-ref', required=True)
    check.add_argument('--sha256', required=True)
    args = parser.parse_args(argv)
    if args.command == 'calibration-contract':
        result = calibration_contract_v1()
    else:
        result = verify_canonical_archive(Path(args.repo_root), args.controller, args.archive_ref, args.sha256)
    sys.stdout.buffer.write(canonical_bytes(result))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RotationError, OSError) as exc:
        print('rotate-canonical-state: STOP: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
