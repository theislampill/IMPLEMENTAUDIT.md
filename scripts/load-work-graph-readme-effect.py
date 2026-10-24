#!/usr/bin/env python3
"""Fixed repository receiver for the portable README physical-effect contract.

This source-custody owner is the trusted invocation boundary. It does not
self-attest its executing bytes by rereading its file. Callers retaining an
outer-loader execution identity must capture the actual buffer they compile.
All dependent code is physically acquired, pinned and executed from captures.
"""
import hashlib
import os
from pathlib import Path
import stat
import types

LOADER = "scripts/load-work-graph-readme-effect.py"
HELPER = "scripts/work-graph-readme-effect.py"
BOOTSTRAP = "scripts/readme-effect-bootstrap.py"
PREFIX = "scripts/qualify-work-graph-prefix.py"
QUALIFIER = "scripts/qualify-work-graph-verifier.py"
COMPLETION = "scripts/work-graph-completion.py"
COMPILER = "skills/implementaudit/scripts/compile-work-graph.py"
ROOT = Path(__file__).absolute().parents[1]
MAX_SOURCE_BYTES = 1024**2
# Exact reviewed source profiles only. These are constraints on code bytes,
# never result credentials or authority to execute a governed native task.
PINS = types.MappingProxyType({
    'scripts/work-graph-readme-effect.py': 'edbc4802f2f0bcb3df0de08225315f56fcf11b8f2a906aacf408f4a1529a84be',
    'scripts/readme-effect-bootstrap.py': 'ae5a841510b72bf24e59c8dd42e57a062e29c1730919f4b20ab420d750fcda57',
    'scripts/qualify-work-graph-prefix.py': '86f4e02dbf7b25ee3a4dab2fb90ef4dd3e21cfe350e8ce38470e36c4f4733016',
    'scripts/qualify-work-graph-verifier.py': 'c8fe85bd96c43774f5218dff7206a842b7cc9f286233bc5da1d69a108db466c8',
    'scripts/work-graph-completion.py': '102df817e0233de2f89c5b56cdb5a013376b381ba718578dbb18672e2becd5b9',
    'scripts/run-work-graph-verifier.sh': '345f51885abbeeda2e4ecd0de503febe50f30f853630a44c0c1277f414c1f9ae',
    'skills/implementaudit/scripts/compile-work-graph.py': '7e604e35766f42b425f6d3f25df576facdba409fc10000c35a5aee84e1644748',
})


def _identity(info):
    return (str(info.st_dev), str(info.st_ino), info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _directory_identity(info):
    return (str(info.st_dev), str(info.st_ino), info.st_mode, info.st_uid, info.st_gid)


def _read(name):
    """Capture one fixed member through no-follow absolute directory handles."""
    if name not in PINS and name != LOADER:
        raise ValueError("unknown fixed source member")
    path = ROOT / name
    if ".." in path.parts or not path.is_absolute():
        raise ValueError("source path alias is unsupported")
    if not all(hasattr(os, n) for n in ("O_NOFOLLOW", "O_DIRECTORY", "O_NONBLOCK")):
        raise ValueError("physical source capture requires no-follow descriptors")
    directory = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    fd = None
    current = Path("/")
    ancestors = {str(current): _directory_identity(os.fstat(directory))}
    try:
        for component in path.parts[1:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
            current /= component
            ancestors[str(current)] = _directory_identity(os.fstat(directory))
        before = os.stat(path.name, dir_fd=directory, follow_symlinks=False)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or stat.S_IMODE(before.st_mode) not in (0o644, 0o755)
                or not 0 < before.st_size <= MAX_SOURCE_BYTES):
            raise ValueError("source must be a bounded ordinary single-link file")
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        if _identity(os.fstat(fd)) != _identity(before) or os.listxattr(fd):
            raise ValueError("source changed or extended metadata is unsupported")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(MAX_SOURCE_BYTES + 1)
        if (len(data) > MAX_SOURCE_BYTES or _identity(os.fstat(fd)) != _identity(before)
                or _identity(os.stat(path.name, dir_fd=directory, follow_symlinks=False)) != _identity(before)):
            raise ValueError("source changed during bounded capture")
        return data, _identity(before), ancestors
    finally:
        if fd is not None:
            os.close(fd)
        os.close(directory)


class _Engine:
    """Private immutable data capture; no caller can provide its source set."""
    def __init__(self):
        # This is a physical-path guard only, not an execution-identity claim.
        _read(LOADER)
        sources, ancestors = {}, {}
        for name, expected in PINS.items():
            data, identity, directories = _read(name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("unsupported fixed engine source: " + name)
            sources[name] = (data, identity)
            for directory, current in directories.items():
                if directory in ancestors and ancestors[directory] != current:
                    raise ValueError("source ancestor changed during complete capture")
                ancestors[directory] = current
        self.sources = types.MappingProxyType(sources)
        self.ancestors = types.MappingProxyType(ancestors)
        self._loaded = {}
        self.check()

    def check(self):
        for name, captured in self.sources.items():
            data, identity, directories = _read(name)
            if ((data, identity) != captured
                    or any(self.ancestors[d] != current for d, current in directories.items())):
                raise ValueError("captured fixed source is no longer current: " + name)

    def execute(self, name):
        if name not in (PREFIX, QUALIFIER, COMPLETION, HELPER) or name in self._loaded:
            raise ValueError("unknown or repeated fixed module execution")
        self.check()
        data = self.sources[name][0]
        module = types.ModuleType("_readme_fixed_" + Path(name).stem.replace("-", "_"))
        module.__file__ = str(ROOT / name)
        module.__package__ = ""
        if name == QUALIFIER:
            module._R0035_EFFECT_SOURCE_CAPTURE = dict(
                driver=self.sources[QUALIFIER][0], compiler=self.sources[COMPILER][0],
                expected_compiler_sha256=PINS[COMPILER])
        elif name == HELPER:
            if set(self._loaded) != {PREFIX, QUALIFIER, COMPLETION}:
                raise ValueError("fixed helper requires its captured owner closure")
            module._R0035_EFFECT_OWNER_CAPTURE = dict(
                root=str(ROOT), sources=self.sources, pins=PINS, ancestors=self.ancestors,
                modules=types.MappingProxyType(dict(self._loaded)))
        try:
            exec(compile(data, module.__file__, "exec"), module.__dict__)
        finally:
            self.check()
        self._loaded[name] = module
        return module


def _load_owner():
    """No cache and no public source parameters: capture this fixed closure."""
    engine = _Engine()
    for name in (PREFIX, QUALIFIER, COMPLETION, HELPER):
        owner = engine.execute(name)
    engine.check()
    return owner


def create_session(source_root, output, *, max_age=3600):
    """Create this fixed contract; never import a command, result or receipt."""
    return _load_owner().EffectSession(source_root, output, max_age=max_age)
