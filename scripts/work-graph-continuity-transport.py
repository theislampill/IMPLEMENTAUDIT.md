#!/usr/bin/env python3
"""Repository-only exact-source transports for fixed readonly owner calls.

This internal adapter does not decide currentness or authenticate supplied Python
objects. Its fixed caller must load these exact bytes and acquire the complete selected source
bytes through the existing held-source owner. Unknown source populations refuse;
the old qualified two-source optimisation is a different caller-owned path.

Sealed memfds feed linked files in a namespace-private filesystem, remounted
readonly before any owner runs. Direct memfd/--ro-bind-data mounts have link count
zero and are incompatible with the unchanged custody owners. A private root and
source subtree prevent a host-side parent replacement redirecting nested source
reopens. Repository/common-directory binds retain the real declared paths/cwd.
Private sealed python/python3 wrappers force isolated, no-site, no-bytecode
startup even after the unchanged owner rebuilds its environment. Their readonly
host-binary alias keeps sys.executable's parent in the owner's rebuilt PATH.

This is a trusted readonly helper profile, not a generic hostile-code executor or
an effect interlock. Host Python/Bash/Git and their root-owned system libraries
remain trusted. The host /proc is bound readonly; no new proc filesystem or host
policy change is attempted. Unsupported hosts, missing bwrap, and failed namespace
creation are typed refusals. The separate original14 branch retains published Windows held-file semantics;
positive Windows host qualification and native admission remain separate.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import time


# Qualification of this bounded transport only; no owner or shortcut pin changes.
SOURCE_PROFILE_V1 = (
    ("claim-run.sh", 17368, "50e2417a05007b34f38417fb891c8e6f806c7df25d008659939f2dc08b2a0383", 0o644),
    ("validate-run-root.sh", 61001, "d8b046b5417dce13ed66a5ac5fffaf3d18fae40c97d42aef8b38470500d575a6", 0o644),
    ("claim-run-rotation.py", 103754, "6f62f57d3a5873570161022e2ccc04cdb061655fa338bcb2c5ea1624b80454ca", 0o644),
    ("rotate-canonical-state.py", 92941, "7989a08128fedabe531fc92114baff755e77e08aebea547253793b625496bb26", 0o755),
    ("canonical_hot_projection.py", 57891, "fe733b91dff4f031ed3ab80761d669de59c0270cd7f85325a14a2d47f9ba5276", 0o755),
    ("canonical_custody.py", 33629, "bfa07f0088f2df7b8c1196ccd149ebf8c6874337b35ac9a9c91ac51367a7fb1f", 0o755),
)
# Exact published sources and reviewed receiving compositions; no admission.
SOURCE_PROFILES_V1 = {
    'main-r0035': (
        ('claim-run.sh', 17368, '50e2417a05007b34f38417fb891c8e6f806c7df25d008659939f2dc08b2a0383', 0o644),
        ('validate-run-root.sh', 61001, 'd8b046b5417dce13ed66a5ac5fffaf3d18fae40c97d42aef8b38470500d575a6', 0o644),
        ('claim-run-rotation.py', 103754, '6f62f57d3a5873570161022e2ccc04cdb061655fa338bcb2c5ea1624b80454ca', 0o644),
        ('rotate-canonical-state.py', 92941, '7989a08128fedabe531fc92114baff755e77e08aebea547253793b625496bb26', 0o755),
        ('canonical_hot_projection.py', 57891, 'fe733b91dff4f031ed3ab80761d669de59c0270cd7f85325a14a2d47f9ba5276', 0o755),
        ('canonical_custody.py', 33629, 'bfa07f0088f2df7b8c1196ccd149ebf8c6874337b35ac9a9c91ac51367a7fb1f', 0o755),
    ),
    'r0035-r0033-r0037': (
        ('claim-run.sh', 17368, '50e2417a05007b34f38417fb891c8e6f806c7df25d008659939f2dc08b2a0383', 0o644),
        ('validate-run-root.sh', 96597, '77f324a5d87f49dbd870e9fdc23d2e4d252d2bdb4244d523408245fbd6dbbbb3', 0o644),
        ('claim-run-rotation.py', 103754, '6f62f57d3a5873570161022e2ccc04cdb061655fa338bcb2c5ea1624b80454ca', 0o644),
        ('rotate-canonical-state.py', 92941, '7989a08128fedabe531fc92114baff755e77e08aebea547253793b625496bb26', 0o755),
        ('canonical_hot_projection.py', 57891, 'fe733b91dff4f031ed3ab80761d669de59c0270cd7f85325a14a2d47f9ba5276', 0o755),
        ('canonical_custody.py', 33629, 'bfa07f0088f2df7b8c1196ccd149ebf8c6874337b35ac9a9c91ac51367a7fb1f', 0o755),
    ),
    'main-r0035-r002e-custody': (
        ('claim-run.sh', 17368, '50e2417a05007b34f38417fb891c8e6f806c7df25d008659939f2dc08b2a0383', 0o644),
        ('validate-run-root.sh', 61001, 'd8b046b5417dce13ed66a5ac5fffaf3d18fae40c97d42aef8b38470500d575a6', 0o644),
        ('claim-run-rotation.py', 104704, 'f6e6d93c9ca103c21ce4f316ec7688f2e3750749d074e22f0ed16d3f612fa795', 0o644),
        ('rotate-canonical-state.py', 92941, '7989a08128fedabe531fc92114baff755e77e08aebea547253793b625496bb26', 0o755),
        ('canonical_hot_projection.py', 57891, 'fe733b91dff4f031ed3ab80761d669de59c0270cd7f85325a14a2d47f9ba5276', 0o755),
        ('canonical_custody.py', 33629, 'bfa07f0088f2df7b8c1196ccd149ebf8c6874337b35ac9a9c91ac51367a7fb1f', 0o755),
    ),
    'r0035-r0033-r0037-r002e-custody': (
        ('claim-run.sh', 17368, '50e2417a05007b34f38417fb891c8e6f806c7df25d008659939f2dc08b2a0383', 0o644),
        ('validate-run-root.sh', 96597, '77f324a5d87f49dbd870e9fdc23d2e4d252d2bdb4244d523408245fbd6dbbbb3', 0o644),
        ('claim-run-rotation.py', 104704, 'f6e6d93c9ca103c21ce4f316ec7688f2e3750749d074e22f0ed16d3f612fa795', 0o644),
        ('rotate-canonical-state.py', 92941, '7989a08128fedabe531fc92114baff755e77e08aebea547253793b625496bb26', 0o755),
        ('canonical_hot_projection.py', 57891, 'fe733b91dff4f031ed3ab80761d669de59c0270cd7f85325a14a2d47f9ba5276', 0o755),
        ('canonical_custody.py', 33629, 'bfa07f0088f2df7b8c1196ccd149ebf8c6874337b35ac9a9c91ac51367a7fb1f', 0o755),
    ),
    'r0035-r0039': (
        ('claim-run.sh', 17632, '78c6391743132b5265d415bf73435cb0ee11f3e32d09d8b280018e949745e5ac', 0o644),
        ('validate-run-root.sh', 61188, '73bce773c2fa43aa1f42584121824b8179356ca6bf6348c6e10492e2f128313d', 0o644),
        ('claim-run-rotation.py', 213510, 'f2cb06e57e1b46dd7e679019acc780b7ffbfeaf21516cf53e5e0fb14eae90660', 0o644),
        ('rotate-canonical-state.py', 125155, 'c505832360e0e245aca51d1c14ee8c9d9c330d0300684a77aa6c5bd8803bad74', 0o755),
        ('canonical_hot_projection.py', 58417, 'b3fd58cef5bf79cbd8f109b352a9b80c230127bf35db0dbac2ef41a7490d967f', 0o755),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 0o755),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 0o644),
    ),
    'r0035-r0039-r0033-r0037': (
        ('claim-run.sh', 17632, '78c6391743132b5265d415bf73435cb0ee11f3e32d09d8b280018e949745e5ac', 0o644),
        ('validate-run-root.sh', 96784, '23afb71f4e6660301912d97142ad087391e0308d828fecce8e45b5e2aae8b295', 0o644),
        ('claim-run-rotation.py', 213510, 'f2cb06e57e1b46dd7e679019acc780b7ffbfeaf21516cf53e5e0fb14eae90660', 0o644),
        ('rotate-canonical-state.py', 125155, 'c505832360e0e245aca51d1c14ee8c9d9c330d0300684a77aa6c5bd8803bad74', 0o755),
        ('canonical_hot_projection.py', 58417, 'b3fd58cef5bf79cbd8f109b352a9b80c230127bf35db0dbac2ef41a7490d967f', 0o755),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 0o755),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 0o644),
    ),
    'r0035-r0039-7a89': (
        ('claim-run.sh', 17632, '78c6391743132b5265d415bf73435cb0ee11f3e32d09d8b280018e949745e5ac', 0o644),
        ('validate-run-root.sh', 61188, '73bce773c2fa43aa1f42584121824b8179356ca6bf6348c6e10492e2f128313d', 0o644),
        ('claim-run-rotation.py', 245953, '36da48d5e81218ff020c5fdb85fe0797e19a61459b4c167f137109e279e7f7aa', 0o644),
        ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 0o755),
        ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 0o755),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 0o755),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 0o644),
    ),
    'r0035-r0039-7a89-r0033-r0037': (
        ('claim-run.sh', 17632, '78c6391743132b5265d415bf73435cb0ee11f3e32d09d8b280018e949745e5ac', 0o644),
        ('validate-run-root.sh', 96784, '23afb71f4e6660301912d97142ad087391e0308d828fecce8e45b5e2aae8b295', 0o644),
        ('claim-run-rotation.py', 245953, '36da48d5e81218ff020c5fdb85fe0797e19a61459b4c167f137109e279e7f7aa', 0o644),
        ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 0o755),
        ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 0o755),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 0o755),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 0o644),
    ),
    'r0039-original14-windows': (
        ('claim-run.sh', 99730, '405ab3853dfb88c007ea2f8f8dd98fb8e9c6e77552b172f2f71a8751364ea20f', None),
        ('validate-run-root.sh', 61188, '73bce773c2fa43aa1f42584121824b8179356ca6bf6348c6e10492e2f128313d', None),
        ('claim-run-rotation.py', 213510, 'f2cb06e57e1b46dd7e679019acc780b7ffbfeaf21516cf53e5e0fb14eae90660', None),
        ('rotate-canonical-state.py', 125155, 'c505832360e0e245aca51d1c14ee8c9d9c330d0300684a77aa6c5bd8803bad74', None),
        ('canonical_hot_projection.py', 58417, 'b3fd58cef5bf79cbd8f109b352a9b80c230127bf35db0dbac2ef41a7490d967f', None),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
        ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
    ),
    'r0039-original14-windows-7a89': (
        ('claim-run.sh', 99730, '405ab3853dfb88c007ea2f8f8dd98fb8e9c6e77552b172f2f71a8751364ea20f', None),
        ('validate-run-root.sh', 61188, '73bce773c2fa43aa1f42584121824b8179356ca6bf6348c6e10492e2f128313d', None),
        ('claim-run-rotation.py', 245953, '36da48d5e81218ff020c5fdb85fe0797e19a61459b4c167f137109e279e7f7aa', None),
        ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None),
        ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
        ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
    ),
    'r0039-original14-windows-r0033-r0037': (
        ('claim-run.sh', 99730, '405ab3853dfb88c007ea2f8f8dd98fb8e9c6e77552b172f2f71a8751364ea20f', None),
        ('validate-run-root.sh', 96784, '23afb71f4e6660301912d97142ad087391e0308d828fecce8e45b5e2aae8b295', None),
        ('claim-run-rotation.py', 213510, 'f2cb06e57e1b46dd7e679019acc780b7ffbfeaf21516cf53e5e0fb14eae90660', None),
        ('rotate-canonical-state.py', 125155, 'c505832360e0e245aca51d1c14ee8c9d9c330d0300684a77aa6c5bd8803bad74', None),
        ('canonical_hot_projection.py', 58417, 'b3fd58cef5bf79cbd8f109b352a9b80c230127bf35db0dbac2ef41a7490d967f', None),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
        ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
    ),
    'r0039-original14-windows-7a89-r0033-r0037': (
        ('claim-run.sh', 99730, '405ab3853dfb88c007ea2f8f8dd98fb8e9c6e77552b172f2f71a8751364ea20f', None),
        ('validate-run-root.sh', 96784, '23afb71f4e6660301912d97142ad087391e0308d828fecce8e45b5e2aae8b295', None),
        ('claim-run-rotation.py', 245953, '36da48d5e81218ff020c5fdb85fe0797e19a61459b4c167f137109e279e7f7aa', None),
        ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None),
        ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
        ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
    ),
}
# Exact composite source selection only; no native qualification is conferred.
SOURCE_PROFILES_V1["composite-20261025-original14"] = (('claim-run.sh', 104155, 'bd0c6d2ab1ec8f695fe34e459b25d9344e11c5930d3f62d0919b29d9bc4a44ee', None), ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', None), ('claim-run-rotation.py', 246657, '4dbbd07b5a792289c13c1225a8099900682b3657396f60f4b74867502cbadf97', None), ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None), ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None), ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None), ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None), ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None))
# Exact current core: existing POSIX three-read-command domain only.
# It has no combined observe command and receives no Windows/original14 credit.
SOURCE_PROFILES_V1["composite-20261025-core-posix-reads"] = (
    ('claim-run.sh', 22057, '7402bc1b77db0009746b10e8a97b19e680d2ad24b5eb91c5c9b4918409d4f7f6', 420),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', 420),
    ('claim-run-rotation.py', 246657, '4dbbd07b5a792289c13c1225a8099900682b3657396f60f4b74867502cbadf97', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
ORIGINAL14_SOURCE_PROFILES_V1 = tuple(rows for rows in SOURCE_PROFILES_V1.values() if rows[0][3] is None)
ORIGINAL14_SOURCE_PROFILE_V1 = SOURCE_PROFILES_V1["r0039-original14-windows"]

_HOST_ROOTS = ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc", "/dev", "/proc")
_PYTHON_DIRECTORY = "/implementaudit-python"
_PYTHON_ALIAS = _PYTHON_DIRECTORY + "/cpython"
_MARKER = b"implementaudit.continuity-mounted-source.v2\t"
_MAX_STDOUT = 8192
_MAX_STDERR = 32768
_TIMEOUT = 30

# The kernel Linux UAPI numbers are used when a Python build omits the constants.
_F_ADD_SEALS, _F_GET_SEALS, _ALL_SEALS = 1033, 1034, 15


class ContinuityTransportError(RuntimeError):
    def __init__(self, code, message, *, returncode=None, stdout=b"", stderr=b""):
        super().__init__(code + ": " + message)
        self.code = code
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def _refuse(suffix, message):
    raise ContinuityTransportError("CONTINUITY_TRANSPORT_" + suffix, message)


def _path(raw):
    if not isinstance(raw, (str, Path)):
        _refuse("SOURCE_REFUSED", "path must be an exact absolute pathname")
    raw = str(raw)
    path = Path(raw)
    if (not path.is_absolute() or str(path) != raw or ".." in path.parts
            or any(ord(char) < 32 for char in raw)):
        _refuse("SOURCE_REFUSED", "path spelling is not canonical absolute")
    return path


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


class _Directory:
    """Retain physical ancestors; verify names before returning any observation."""
    def __init__(self, path):
        self.nodes = []
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        try:
            parent = None
            for name in (path.anchor, *path.parts[1:]):
                fd = os.open(name, flags, dir_fd=parent)
                info = os.fstat(fd)
                self.nodes.append((parent, name, fd, (info.st_dev, info.st_ino, info.st_mode)))
                parent = fd
            self.fd = parent
            self.verify()
        except BaseException:
            self.close()
            raise

    def verify(self):
        for parent, name, fd, expected in self.nodes:
            for info in (os.fstat(fd), os.stat(name, dir_fd=parent, follow_symlinks=False)):
                if not stat.S_ISDIR(info.st_mode) or (info.st_dev, info.st_ino, info.st_mode) != expected:
                    _refuse("SOURCE_CHANGED", "a retained directory or its pathname changed")

    def close(self):
        while self.nodes:
            os.close(self.nodes.pop()[2])


def source_profiles_for_helpers_v1(claim_raw, validate_raw):
    pair = tuple((len(raw), hashlib.sha256(raw).hexdigest()) for raw in (claim_raw, validate_raw))
    return tuple(rows for rows in SOURCE_PROFILES_V1.values()
                 if tuple((row[1], row[2]) for row in rows[:2]) == pair)


def _source_profile(source_rows):
    if (type(source_rows) is not tuple or not source_rows
            or any(type(row) is not tuple or len(row) != 2 or type(row[1]) is not bytes
                   for row in source_rows)):
        _refuse("SOURCE_REFUSED", "exact immutable source population required")
    identity = tuple((_path(path).name, len(raw), hashlib.sha256(raw).hexdigest())
                     for path, raw in source_rows)
    matches = [profile for profile in SOURCE_PROFILES_V1.values()
               if tuple(row[:3] for row in profile) == identity]
    if len(matches) != 1:
        _refuse("SOURCE_REFUSED", "source bytes are outside the qualified closure")
    return matches[0]


def _sources(owner, source_rows, expected_dir, before=None):
    profile = _source_profile(source_rows)
    observed, manifests = [], []
    for entry, (name, size, digest, mode) in zip(source_rows, profile):
        if type(entry) is not tuple or len(entry) != 2 or type(entry[1]) is not bytes:
            _refuse("SOURCE_REFUSED", "source members must be immutable path/bytes pairs")
        path, raw = _path(entry[0]), entry[1]
        if path != expected_dir / name or len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
            _refuse("SOURCE_REFUSED", "source path or bytes are outside the qualified closure")
        first = path.lstat()
        if (not stat.S_ISREG(first.st_mode) or first.st_nlink != 1
                or stat.S_IMODE(first.st_mode) != mode or first.st_size != size):
            _refuse("SOURCE_REFUSED", "source type, link count, mode, or size changed")
        # The unchanged owner traverses from the filesystem anchor through held,
        # non-following directories and leaf; no path-read fallback is allowed.
        acquired, kind = owner._read_repository_path(path, maximum=size)
        final = path.lstat()
        identity = _identity(final)
        if (kind != "file" or acquired != raw or _identity(first) != identity
                or before is not None and identity != before[len(observed)]):
            _refuse("SOURCE_CHANGED", "source changed across acquisition or execution")
        observed.append(identity)
        manifests.append(dict(name=name, path=str(path), bytes=size, sha256=digest, mode=mode))
    return tuple(observed), manifests


def _arguments(arguments):
    valid = type(arguments) is tuple and all(type(value) is str for value in arguments)
    if valid and arguments == ("--current-controller",):
        return
    if valid and len(arguments) == 2:
        command, value = arguments
        if command == "--require-current-continuity" and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", value):
            return
        if command == "--verify-resume-receipt" and re.fullmatch(
                r"refs/implementaudit/continuity-receipts/[a-z0-9][a-z0-9-]{0,47}/G[0-9A-F]{4}@[0-9a-f]{40}", value):
            return
    _refuse("COMMAND_REFUSED", "only exact current/require/verify arguments are admitted")


def _trusted(name):
    path = Path("/usr/bin") / name
    try:
        resolved = path.resolve(strict=True)
        if not stat.S_ISREG(resolved.stat().st_mode) or not os.access(resolved, os.X_OK):
            raise OSError("not executable")
        for part in (resolved, *resolved.parents):
            info = part.lstat()
            if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                raise OSError("host tool is outside root-owned custody")
        return str(resolved)
    except OSError as exc:
        raise ContinuityTransportError("CONTINUITY_TRANSPORT_UNAVAILABLE",
                                       "trusted host executable unavailable: " + name) from exc


def _environment():
    result = dict(PATH=_PYTHON_DIRECTORY + ":/usr/bin:/bin", LC_ALL="C", PYTHONDONTWRITEBYTECODE="1",
                  PYTHONNOUSERSITE="1", PYTHONSAFEPATH="1", GIT_ATTR_NOSYSTEM="1",
                  GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null",
                  GIT_CONFIG_NOSYSTEM="1", GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
                  GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0", GIT_EXTERNAL_DIFF="",
                  GIT_PAGER="cat", PAGER="cat")
    config = {"core.fsmonitor": "false", "core.hooksPath": "/dev/null", "protocol.allow": "never",
              "protocol.ext.allow": "never", "credential.helper": "", "core.sshCommand": "",
              "submodule.recurse": "false"}
    result["GIT_CONFIG_COUNT"] = str(len(config))
    for index, (key, value) in enumerate(config.items()):
        result["GIT_CONFIG_KEY_" + str(index)] = key
        result["GIT_CONFIG_VALUE_" + str(index)] = value
    return result


def _capture(command, *, repository, environment, descriptors=()):
    streams = [bytearray(), bytearray()]
    process = subprocess.Popen(command, cwd=repository, env=environment, pass_fds=descriptors,
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True)
    deadline = time.monotonic() + _TIMEOUT
    try:
        with selectors.DefaultSelector() as selector:
            for index, stream in enumerate((process.stdout, process.stderr)):
                selector.register(stream, selectors.EVENT_READ, index)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    _refuse("TIMEOUT", "readonly owner exceeded its execution bound")
                for key, _ in selector.select(remaining):
                    block = os.read(key.fileobj.fileno(), 8192)
                    if not block:
                        selector.unregister(key.fileobj)
                        continue
                    streams[key.data].extend(block)
                    if len(streams[key.data]) > (_MAX_STDOUT, _MAX_STDERR)[key.data]:
                        _refuse("OUTPUT_BOUND", "readonly owner exceeded its output bound")
        process.wait(timeout=max(0.01, deadline - time.monotonic()))
    except BaseException as exc:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        if isinstance(exc, ContinuityTransportError):
            exc.returncode, exc.stdout, exc.stderr = process.returncode, bytes(streams[0]), bytes(streams[1])
        raise
    finally:
        process.stdout.close()
        process.stderr.close()
    return process.returncode, bytes(streams[0]), bytes(streams[1])


_CHILD = r'''
import sys
sys.dont_write_bytecode = True
import hashlib,json,os,pathlib,stat
request=json.loads(sys.argv[1])
if os.getcwd()!=request["repository"]:
    raise RuntimeError("declared repository cwd changed")
startup=dict(profile="ISOLATED_CPYTHON_V1",isolated=bool(sys.flags.isolated),
             no_site=bool(sys.flags.no_site),dont_write_bytecode=bool(sys.flags.dont_write_bytecode))
if startup!=request["startup"] or sys.executable!=request["python"] or not sys.dont_write_bytecode:
    raise RuntimeError("Python startup is not the isolated private alias")
alias=pathlib.Path(sys.executable)
if (not stat.S_ISREG(alias.lstat().st_mode) or
    not os.statvfs(alias).f_flag & os.ST_RDONLY or
    not os.path.samestat(alias.stat(),pathlib.Path(request["host_python"]).stat())):
    raise RuntimeError("Python alias is not the readonly trusted host binary")
observed=[]
for row in request["members"]+request["startup_members"]:
    path=pathlib.Path(row["path"])
    for parent in (path.parent,*path.parents):
        info=parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or not os.statvfs(parent).f_flag & os.ST_RDONLY:
            raise RuntimeError("source ancestor is not physical and readonly")
    before=path.lstat()
    with path.open("rb") as stream:
        opened=os.fstat(stream.fileno())
        raw=stream.read(row["bytes"]+1)
        after=os.fstat(stream.fileno())
    identity=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    if (not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or
        stat.S_IMODE(before.st_mode)!=row["mode"] or
        not identity(before)==identity(opened)==identity(after)==identity(path.lstat()) or
        len(raw)!=row["bytes"] or hashlib.sha256(raw).hexdigest()!=row["sha256"] or
        not os.statvfs(path).f_flag & os.ST_RDONLY):
        raise RuntimeError("mounted source differs from sealed closure")
    observed.append(dict(row,links=before.st_nlink,readonly=True))
members=observed[:len(request["members"])]
startup_members=observed[len(request["members"]):]
if sorted(p.name for p in pathlib.Path(members[0]["path"]).parent.iterdir())!=sorted(r["name"] for r in members):
    raise RuntimeError("mounted source population is not closed")
if sorted(p.name for p in alias.parent.iterdir())!=sorted([alias.name]+[r["name"] for r in startup_members]):
    raise RuntimeError("private Python startup population is not closed")
message=json.dumps(dict(repository=os.getcwd(),members=members,startup=startup,startup_members=startup_members),sort_keys=True,separators=(",",":"))
sys.stderr.write("implementaudit.continuity-mounted-source.v2\t"+message+"\n")
sys.stderr.flush()
os.execv(request["bash"],[request["bash"],request["members"][0]["path"],*request["arguments"]])
'''


def _original14_call(owner, route, repository, sources, arguments):
    """Preserve published R0039's held eight-member Windows read domain."""
    import contextlib
    import io
    import tempfile
    profile = _source_profile(sources)
    if profile not in ORIGINAL14_SOURCE_PROFILES_V1:
        _refuse("SOURCE_REFUSED", "original14 source population differs")
    readonly = (arguments in (("--current-controller",), ("--observe-current-continuity",))
                or (type(arguments) is tuple and len(arguments) == 2
                    and arguments[0] in {"--require-current-continuity", "--verify-resume-receipt"}
                    and type(arguments[1]) is str))
    if not readonly:
        _refuse("COMMAND_REFUSED", "original14 accepts only fixed read operations")
    if os.name != "nt":
        _refuse("UNSUPPORTED_HOST", "original14 private transport requires qualified Windows custody")
    if route is None:
        _refuse("UNAVAILABLE", "fixed caller host route is required")
    repository = _path(repository)
    environment = owner._native_child_environment(route)
    environment.update(GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1',
                       GIT_TERMINAL_PROMPT='0', GIT_CONFIG_SYSTEM=os.devnull)
    config = {'core.fsmonitor': 'false', 'core.hooksPath': os.devnull,
              'protocol.allow': 'never', 'protocol.ext.allow': 'never',
              'credential.helper': '', 'core.sshCommand': '', 'submodule.recurse': 'false',
              'core.longpaths': 'true'}
    environment['GIT_CONFIG_COUNT'] = str(len(config))
    for index, (key, value) in enumerate(config.items()):
        environment['GIT_CONFIG_KEY_' + str(index)] = key
        environment['GIT_CONFIG_VALUE_' + str(index)] = value
    def source_rows():
        rows = []
        for (path, raw), (name, size, digest, _) in zip(sources, profile):
            path = _path(path)
            if path.name != name or path.parent != _path(sources[0][0]).parent:
                _refuse("SOURCE_REFUSED", "original14 sibling path differs")
            before = path.lstat()
            actual, kind = owner._read_repository_path(path, maximum=size)
            after = path.lstat()
            if kind != 'file' or actual != raw or _identity(before) != _identity(after):
                _refuse("SOURCE_CHANGED", "original14 source changed during acquisition")
            rows.append(dict(name=name, path=str(path), bytes=size, sha256=digest,
                             mode=stat.S_IMODE(after.st_mode), links=1, held=True))
        return rows
    rows = source_rows()
    raw_by_name = {Path(path).name: raw for path, raw in sources}
    custody = owner._native_module_from_bytes(raw_by_name['canonical_custody.py'],
        _path(sources[0][0]).with_name('canonical_custody.py'),
        '_r0035_original14_private_custody', '$native.original14.private_custody')
    closure = Path(tempfile.mkdtemp(prefix='implementaudit-r0035-original14-'))
    expected = []
    try:
        for name, raw in raw_by_name.items():
            path = closure / name
            with path.open('xb') as stream:
                stream.write(raw)
            expected.append((path, raw))
        with contextlib.ExitStack() as stack:
            directory = stack.enter_context(custody.Directory(closure))
            if set(directory.names()) != set(raw_by_name):
                _refuse("SOURCE_CHANGED", "original14 private closure population differs")
            retained = []
            for path, raw in expected:
                held = stack.enter_context(custody.File(directory, path.name, maximum=len(raw)))
                if held.read() != raw:
                    _refuse("SOURCE_CHANGED", "original14 private closure bytes changed")
                retained.append(held)
            with contextlib.redirect_stdout(io.StringIO()):
                bash = route.trusted_host_executable(repository, 'bash')
                claim_path = route.bash_script_path(closure / 'claim-run.sh')
                validate_path = route.bash_script_path(closure / 'validate-run-root.sh')
            pair = (hashlib.sha256(raw_by_name['claim-run.sh']).hexdigest(),
                    hashlib.sha256(raw_by_name['validate-run-root.sh']).hexdigest())
            result = subprocess.run([str(bash), '-c', owner._NATIVE_R0011_CHILD_BOOTSTRAP,
                claim_path, claim_path, validate_path, *pair, *arguments], cwd=repository,
                env=environment, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=30, check=False)
            for held in retained:
                held.verify()
            if set(directory.names()) != set(raw_by_name) or source_rows() != rows:
                _refuse("SOURCE_CHANGED", "original14 closure changed during execution")
            marker = ('implementaudit-native-r0011-child-v1\t' + pair[0] + '\t' + pair[1]).encode()
            if (result.returncode or len(result.stdout) > 8192 or len(result.stderr) > 16384
                    or result.stderr.splitlines().count(marker) != 1):
                _refuse("OWNER_REFUSED", "original14 continuity owner refused or changed")
            return dict(returncode=result.returncode, stdout=result.stdout,
                stderr=b'\n'.join(line for line in result.stderr.splitlines() if line != marker),
                closure=dict(schema='implementaudit.continuity-windows-source-closure.v1',
                             repository=str(repository), members=rows,
                             custody='WINDOWS_HELD_FILES_V1'))
    finally:
        owner._native_cleanup_private_closure(closure, expected)


def call_readonly_v1(owner, *, repository, sources, arguments, route=None):
    """Return observed closure/streams/exit only after every source fence closes.

    ``sources`` is the ordered immutable tuple of (absolute pathname, bytes).
    Caller-held acquisition and this adapter's own exact loaded-byte pin remain
    caller responsibilities. Returned dictionaries are observations, never native
    authority tokens. Any owner stderr/nonzero exit remains visible to the caller.
    """
    if (type(sources) is tuple and len(sources) >= 2
            and all(type(row) is tuple and len(row) == 2 and type(row[1]) is bytes for row in sources[:2])
            and tuple(hashlib.sha256(row[1]).hexdigest() for row in sources[:2]) in
                {tuple(row[2] for row in profile[:2]) for profile in ORIGINAL14_SOURCE_PROFILES_V1}):
        return _original14_call(owner, route, repository, sources, arguments)
    _arguments(arguments)
    if (sys.platform != "linux" or os.name != "posix" or not hasattr(os, "memfd_create")
            or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY")
            or os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd):
        _refuse("UNSUPPORTED_HOST", "qualified Linux memfd/directory semantics are required")
    import fcntl
    repository = _path(repository)
    source_dir = _path(str(Path(__file__).absolute().parents[1] / "skills/implementaudit/scripts"))
    environment = _environment()
    bwrap, bash, python, git = (_trusted(name) for name in ("bwrap", "bash", "python3", "git"))
    directories, descriptors = [], []
    result = None
    captured = (None, b"", b"")
    try:
        source_pin = _Directory(source_dir)
        directories.append(source_pin)
        repo_pin = _Directory(repository)
        directories.append(repo_pin)
        before, manifests = _sources(owner, sources, source_dir)
        status, stdout, stderr = _capture([git, "rev-parse", "--path-format=absolute", "--show-toplevel", "--git-common-dir"],
                                          repository=repository, environment=environment)
        roots = stdout.decode("utf-8", "strict").splitlines()
        if status or stderr or len(roots) != 2 or roots[0] != str(repository):
            _refuse("REPOSITORY_REFUSED", "declared cwd is not the exact Git worktree")
        common = _path(roots[1])
        common_pin = _Directory(common)
        directories.append(common_pin)
        for path in (source_dir, repository, common):
            if path == Path("/") or any(path.is_relative_to(Path(root)) for root in (*_HOST_ROOTS, _PYTHON_DIRECTORY)):
                _refuse("TOPOLOGY_REFUSED", "source/data topology overlaps trusted host mounts")
        command = [bwrap, "--unshare-user", "--unshare-net", "--cap-drop", "ALL", "--die-with-parent", "--clearenv"]
        for root in _HOST_ROOTS:
            if root != "/dev" and Path(root).exists():
                command += ["--ro-bind", root, root]
        # A normal ro-bind is nodev: Bash/Git require the harmless null sink and
        # Bash process substitution requires /dev/fd. Expose no other devices.
        command += ["--dev-bind", "/dev/null", "/dev/null",
                    "--symlink", "/proc/self/fd", "/dev/fd"]
        bindings = {repository: repo_pin.fd, common: common_pin.fd}
        for path, fd in sorted(bindings.items(), key=lambda item: len(item[0].parts)):
            command += ["--ro-bind-fd", str(fd), str(path)]
        # All source ancestors are synthetic except a possible containing data
        # bind. Replace its first source-bearing child with private tmpfs, so a
        # host rename/replacement cannot redirect any nested helper reopen.
        overlaps = [path for path in bindings if source_dir.is_relative_to(path)]
        overlay = None
        if overlaps:
            containing = min(overlaps, key=lambda path: len(path.parts))
            relative = source_dir.relative_to(containing)
            if not relative.parts:
                _refuse("TOPOLOGY_REFUSED", "source directory cannot be a data bind root")
            overlay = containing / relative.parts[0]
            if any(path.is_relative_to(overlay) for path in bindings):
                _refuse("TOPOLOGY_REFUSED", "source overlay would hide Git custody")
            command += ["--tmpfs", str(overlay)]
        command += ["--dir", str(source_dir), "--dir", _PYTHON_DIRECTORY,
                    "--ro-bind", python, _PYTHON_ALIAS]
        # The binary alias retains this private parent in rebuilt PATHs. Nested
        # shell Python uses isolated no-site wrappers. R0039's exact tokenizer
        # call selects -I -B itself; its trusted host dependency stays separate
        # from this source closure and is never supplied by repository cwd.
        wrapper = ("#!" + bash + "\nexec " + _PYTHON_ALIAS + ' -I -S -B "$@"\n').encode("utf-8")
        startup_members = [dict(name=name, path=_PYTHON_DIRECTORY + "/" + name,
                               bytes=len(wrapper), sha256=hashlib.sha256(wrapper).hexdigest(), mode=0o755)
                           for name in ("python", "python3")]
        startup = dict(profile="ISOLATED_CPYTHON_V1", isolated=True, no_site=True, dont_write_bytecode=True)
        sealed = list(zip((raw for _, raw in sources), manifests))
        sealed += [(wrapper, row) for row in startup_members]
        for raw, row in sealed:
            fd = os.memfd_create("implementaudit-" + row["name"], os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
            descriptors.append(fd)
            view = memoryview(raw)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    _refuse("SEAL_REFUSED", "sealed source copy was incomplete")
                view = view[written:]
            os.lseek(fd, 0, os.SEEK_SET)
            fcntl.fcntl(fd, _F_ADD_SEALS, _ALL_SEALS)
            if fcntl.fcntl(fd, _F_GET_SEALS) != _ALL_SEALS:
                _refuse("SEAL_REFUSED", "kernel did not retain all four source seals")
            command += ["--perms", format(row["mode"], "04o"), "--file", str(fd), row["path"]]
        if overlay is not None:
            command += ["--remount-ro", str(overlay)]
        command += ["--remount-ro", "/", "--chdir", str(repository)]
        for key, value in sorted(environment.items()):
            command += ["--setenv", key, value]
        request = dict(repository=str(repository), members=manifests, bash=bash, arguments=arguments,
                       startup=startup, startup_members=startup_members, python=_PYTHON_ALIAS, host_python=python)
        command += [_PYTHON_ALIAS, "-I", "-S", "-B", "-c", _CHILD, json.dumps(request, separators=(",", ":"))]
        for directory in directories:
            directory.verify()
        _sources(owner, sources, source_dir, before)
        captured = _capture(command, repository=repository, environment=environment,
                            descriptors=tuple(descriptors + list(bindings.values())))
        status, stdout, stderr = captured
        first, separator, owner_stderr = stderr.partition(b"\n")
        if not separator or not first.startswith(_MARKER) or _MARKER in owner_stderr:
            _refuse("NAMESPACE_REFUSED", "no unique completed mounted-source observation")
        observation = json.loads(first[len(_MARKER):].decode("utf-8", "strict"))
        expected = dict(repository=str(repository), members=[dict(row, links=1, readonly=True) for row in manifests],
                        startup=startup, startup_members=[dict(row, links=1, readonly=True) for row in startup_members])
        if observation != expected:
            _refuse("OBSERVATION_REFUSED", "child read a different source closure or cwd")
        for fd in descriptors:
            if fcntl.fcntl(fd, _F_GET_SEALS) != _ALL_SEALS:
                _refuse("SEAL_REFUSED", "source seal changed during execution")
        _sources(owner, sources, source_dir, before)
        for directory in directories:
            directory.verify()
        closure = dict(schema="implementaudit.continuity-source-closure.v2", repository=str(repository),
                       members=[dict(row, seals=_ALL_SEALS) for row in observation["members"]],
                       startup=observation["startup"])
        result = dict(returncode=status, stdout=stdout, stderr=owner_stderr,
                      transport_stderr=first + b"\n", closure=closure)
    except ContinuityTransportError as exc:
        if captured[0] is not None:
            exc.returncode, exc.stdout, exc.stderr = captured
        raise
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError) as exc:
        raise ContinuityTransportError("CONTINUITY_TRANSPORT_CUSTODY_REFUSED", str(exc),
                         returncode=captured[0], stdout=captured[1], stderr=captured[2]) from exc
    finally:
        for fd in reversed(descriptors):
            os.close(fd)
        for directory in reversed(directories):
            directory.close()
    return result


if __name__ == "__main__":
    raise SystemExit("repository-internal API only; no public JSON/native-authority input")
