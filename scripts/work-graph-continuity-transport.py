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
import contextlib
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
    # Reviewed R0039 projection-bound original14 source only; no host admission.
    'r0039-original14-windows-projection-bound-v1': (
        ('claim-run.sh', 99730, '405ab3853dfb88c007ea2f8f8dd98fb8e9c6e77552b172f2f71a8751364ea20f', None),
        ('validate-run-root.sh', 61188, '73bce773c2fa43aa1f42584121824b8179356ca6bf6348c6e10492e2f128313d', None),
        ('claim-run-rotation.py', 246657, '4dbbd07b5a792289c13c1225a8099900682b3657396f60f4b74867502cbadf97', None),
        ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None),
        ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
        ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
    ),
    # Exact R0039 captured-companion source; original14 host custody remains required.
    'r0039-original14-windows-captured-companion-v1': (
        ('claim-run.sh', 104155, 'bd0c6d2ab1ec8f695fe34e459b25d9344e11c5930d3f62d0919b29d9bc4a44ee', None),
        ('validate-run-root.sh', 61188, '73bce773c2fa43aa1f42584121824b8179356ca6bf6348c6e10492e2f128313d', None),
        ('claim-run-rotation.py', 246657, '4dbbd07b5a792289c13c1225a8099900682b3657396f60f4b74867502cbadf97', None),
        ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None),
        ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None),
        ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
        ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
        ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
    ),
    # Exact R0035 captured-companion core; old source domains remain distinct.
    'r0035-core-captured-companion-v1': (
        ('claim-run.sh', 21636, '35232762fdd76d000bcca774a0f6f53f3d26dfb9229d9795d397b81d7ef8483e', 0o644),
        ('validate-run-root.sh', 61001, 'd8b046b5417dce13ed66a5ac5fffaf3d18fae40c97d42aef8b38470500d575a6', 0o644),
        ('claim-run-rotation.py', 103754, '6f62f57d3a5873570161022e2ccc04cdb061655fa338bcb2c5ea1624b80454ca', 0o644),
        ('rotate-canonical-state.py', 92941, '7989a08128fedabe531fc92114baff755e77e08aebea547253793b625496bb26', 0o755),
        ('canonical_hot_projection.py', 57891, 'fe733b91dff4f031ed3ab80761d669de59c0270cd7f85325a14a2d47f9ba5276', 0o755),
        ('canonical_custody.py', 33629, 'bfa07f0088f2df7b8c1196ccd149ebf8c6874337b35ac9a9c91ac51367a7fb1f', 0o755),
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
# Exact new core; existing three read commands only, no native/history grant.
SOURCE_PROFILES_V1["composite-20261025-core-retained-history-v1"] = (
    ('claim-run.sh', 22199, '34054952e3bbf13ae6ca381d4cf0d9d72bccaed10c8dd879de9351f5c0e2594b', 420),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', 420),
    ('claim-run-rotation.py', 258400, '27ae194fc92a37bd12e0fe378ffc07f788a3bffec28ebd1c0a5e3c8e1c73695e', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
# DG07 nonblocking self-binder; prior source profiles remain unchanged.
SOURCE_PROFILES_V1["composite-20261026-core-binder-v1"] = (
    ('claim-run.sh', 22199, '7d257a9b3502a78d458f80bd0c20fe4594b049a93c819aa3bc91de577bfa34af', 420),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', 420),
    ('claim-run-rotation.py', 259408, '551b1a798161fdd20cb9eebd56fb1d8a0245ec48a74f05b29f6253d8228c49cb', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
# DG07 consistent Python selection; prior source profiles remain unchanged.
SOURCE_PROFILES_V1["composite-20261026-core-python-selection-v1"] = (
    ('claim-run.sh', 30189, '23b828f298c3f21b86d9f7a2228d74ffb34d67d7b7bedc34ceca2ad754d2cbe7', 420),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', 420),
    ('claim-run-rotation.py', 259408, '551b1a798161fdd20cb9eebd56fb1d8a0245ec48a74f05b29f6253d8228c49cb', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
# Exact CAS phase owner; historical profiles and native authority remain unchanged.
SOURCE_PROFILES_V1["composite-20261026-core-cas-phases-v1"] = (
    ('claim-run.sh', 31259, 'a3ecb4d56f8b12fcfc7237906f6547bd2205b1c04cf1c843d2782c86c67ee798', 420),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', 420),
    ('claim-run-rotation.py', 259408, '551b1a798161fdd20cb9eebd56fb1d8a0245ec48a74f05b29f6253d8228c49cb', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
# Current preparation template binding; historical source domains remain unchanged.
SOURCE_PROFILES_V1['composite-20261026-core-preparation-template-v1'] = (
    ('claim-run.sh', 31259, 'cee4c3225be8df9c62fcc8adb4c1af18a38bd1237adac39b0ce5d5a1bce47765', 420),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', 420),
    ('claim-run-rotation.py', 259408, '8edf14f8aea58573c1eb8a3a2bd6a42394aa8ea419217606994c81b1ba162ca9', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
SOURCE_PROFILES_V1['composite-20261026-original14-preparation-template-v1'] = (
    ('claim-run.sh', 104155, '322f17d86170e34788833a619586e8cb9fcc066a70933342ad3f28f036446d0d', None),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', None),
    ('claim-run-rotation.py', 246657, '31e30b564e83db80c11c18b3bf83eab9d901bf089af7dd7ebd2e7d823f5105f8', None),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
)
# Current DG08 source-only bindings; all historical domains remain exact.
SOURCE_PROFILES_V1['composite-20261027-core-dg08-source-v1'] = (
    ('claim-run.sh', 31259, 'e1b686be7aba7da12163810e1c99c0033bad2ec949bdc5436fb177ba2491a790', 420),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', 420),
    ('claim-run-rotation.py', 259408, '348c492cafdb3ed7d41f360ff8c219316257bdd18c4e4f22646aa7e66cb84d9e', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
SOURCE_PROFILES_V1['composite-20261027-original14-dg08-source-v1'] = (
    ('claim-run.sh', 104155, 'd7db3595bfdd6b79e822375df5744597111148315cce6c980dc063792774dc36', None),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', None),
    ('claim-run-rotation.py', 246657, '4a4dc5a997f3d485c7c43be31cb45818907e1685c8506fbabcb8bcee0872aed6', None),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
)
# Current DG08 source-only bindings; all historical domains remain exact.
SOURCE_PROFILES_V1['composite-20261027-core-dg08-acquisition-v1'] = (
    ('claim-run.sh', 31259, '0d1829770e3ce8da613cb48646391fc65641636ac4cd42a97149b3e8f57750b9', 420),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', 420),
    ('claim-run-rotation.py', 259408, 'c91e7c3aa243919c4cdb398f999f28734f1a630511a99f6b1aa9dc477b2fae3c', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
SOURCE_PROFILES_V1['composite-20261027-original14-dg08-acquisition-v1'] = (
    ('claim-run.sh', 104155, '5cca165879cb272a8cb494fcdc12ac461ec53c4d9c95fcb13882ea44397be529', None),
    ('validate-run-root.sh', 113863, '66c0f6d3df8c0f1702864055f3fcc4ee3cf5403982de81fba71389cdc5860283', None),
    ('claim-run-rotation.py', 246657, '908cce5054dc23a9e74b6af695204fc6d9889681611311c7136f087fe0be1663', None),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
)
# Current closure-parser bindings only; retained domains keep their exact bytes.
SOURCE_PROFILES_V1['composite-20261028-core-dg17-ledger-v1'] = (
    ('claim-run.sh', 31259, '0d1829770e3ce8da613cb48646391fc65641636ac4cd42a97149b3e8f57750b9', 420),
    ('validate-run-root.sh', 114294, 'e7a20d7d5eab497338327814367fe8c7221a35cfe61bdfaadd91d84101f0d250', 420),
    ('claim-run-rotation.py', 259408, 'c91e7c3aa243919c4cdb398f999f28734f1a630511a99f6b1aa9dc477b2fae3c', 420),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493),
)
SOURCE_PROFILES_V1['composite-20261028-original14-dg17-ledger-v1'] = (
    ('claim-run.sh', 104155, '5cca165879cb272a8cb494fcdc12ac461ec53c4d9c95fcb13882ea44397be529', None),
    ('validate-run-root.sh', 114294, 'e7a20d7d5eab497338327814367fe8c7221a35cfe61bdfaadd91d84101f0d250', None),
    ('claim-run-rotation.py', 246657, '908cce5054dc23a9e74b6af695204fc6d9889681611311c7136f087fe0be1663', None),
    ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None),
    ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None),
    ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None),
    ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None),
    ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None),
)
# Current terminal-inventory owner binding; historical subjects remain unchanged.
SOURCE_PROFILES_V1['composite-20261028-terminal-inventory-v1-core'] = (('claim-run.sh', 31259, '7cfd59d8569ad04221cd4779a803dfc451d5e47b2d4674ad657090564c6c174d', 420), ('validate-run-root.sh', 114294, 'e7a20d7d5eab497338327814367fe8c7221a35cfe61bdfaadd91d84101f0d250', 420), ('claim-run-rotation.py', 259408, '1c70c0612bad4b2311bb89ddad60484937b5d195bf98380c3ef3e0d30d6cd94b', 420), ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493), ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493), ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493), ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420), ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493))
# Current terminal-inventory owner binding; historical subjects remain unchanged.
SOURCE_PROFILES_V1['composite-20261028-terminal-inventory-v1-original14'] = (('claim-run.sh', 104155, '10baf97b4c773d8ac386627a455bb480e8353ccfdb909fc5253d3ac4c65ecd0f', None), ('validate-run-root.sh', 114294, 'e7a20d7d5eab497338327814367fe8c7221a35cfe61bdfaadd91d84101f0d250', None), ('claim-run-rotation.py', 246657, 'bc862f87428e86c608ddc5fe31ad8a3e2c8324b52c09ba379163db160ad70e93', None), ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None), ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None), ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None), ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None), ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None))
# DG10 current Windows transport binding; all historical subjects retained.
SOURCE_PROFILES_V1['composite-20261028-dg10-native-stop-v1-core'] = (('claim-run.sh', 31259, '7cfd59d8569ad04221cd4779a803dfc451d5e47b2d4674ad657090564c6c174d', 420), ('validate-run-root.sh', 114674, 'c24e2d9a171f8ab7dd0fdc78d8035a18044d5373e2f8e9bfd7f7de2e9b03b978', 420), ('claim-run-rotation.py', 259408, '1c70c0612bad4b2311bb89ddad60484937b5d195bf98380c3ef3e0d30d6cd94b', 420), ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', 493), ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', 493), ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', 493), ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', 420), ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', 493))
# DG10 current Windows transport binding; all historical subjects retained.
SOURCE_PROFILES_V1['composite-20261028-dg10-native-stop-v1-original14'] = (('claim-run.sh', 104155, '10baf97b4c773d8ac386627a455bb480e8353ccfdb909fc5253d3ac4c65ecd0f', None), ('validate-run-root.sh', 114674, 'c24e2d9a171f8ab7dd0fdc78d8035a18044d5373e2f8e9bfd7f7de2e9b03b978', None), ('claim-run-rotation.py', 246657, 'bc862f87428e86c608ddc5fe31ad8a3e2c8324b52c09ba379163db160ad70e93', None), ('rotate-canonical-state.py', 125155, '2fb6495a865d5f79948c8dfbee46ad5ffd18d47c95707b4be96890df1b3d4bbc', None), ('canonical_hot_projection.py', 93893, '10f852a7b5741b4798824a06ae8933e6a5845b0541765470f3849455bddfba2f', None), ('canonical_custody.py', 36367, 'd52369e56c9e06d0b10b43ddffbae8f353c37b53aac8f7642bbaea356c31a389', None), ('canonical_rotation_inputs.py', 27154, '96aefca5859a974ebbccfd9a6d8bac80b472017366ba45aee07d4c0f36099489', None), ('read-canonical-pair.py', 27208, 'c2868db4f385029ed75bd528d00026cb417d96c30fee6bb2bf5669c7c1128be8', None))
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


# POSIX executable bits are not Windows custody. This one current CORE8
# code identity uses the existing NTFS held-file contract on Windows only.
_WINDOWS_CORE8_PAIR_V1=('7cfd59d8569ad04221cd4779a803dfc451d5e47b2d4674ad657090564c6c174d',
    'c24e2d9a171f8ab7dd0fdc78d8035a18044d5373e2f8e9bfd7f7de2e9b03b978')

def _windows_core_profile_v1(profile):
    return len(profile)==8 and tuple(row[2] for row in profile[:2])==_WINDOWS_CORE8_PAIR_V1

def _platform_source_profile_v1(profile):
    if os.name=='nt' and _windows_core_profile_v1(profile):
        return tuple((*row[:3],None) for row in profile)
    return profile


def source_profiles_for_helpers_v1(claim_raw, validate_raw):
    pair = tuple((len(raw), hashlib.sha256(raw).hexdigest()) for raw in (claim_raw, validate_raw))
    return tuple(_platform_source_profile_v1(rows) for rows in SOURCE_PROFILES_V1.values()
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
    return _platform_source_profile_v1(matches[0])


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


def _capture(command, *, repository, environment, descriptors=(), maximum_stdout=_MAX_STDOUT):
    if type(maximum_stdout) is not int or not _MAX_STDOUT <= maximum_stdout <= 32 * 1024**2:
        _refuse("OUTPUT_BOUND", "unknown capture output contract")
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
                    if len(streams[key.data]) > (maximum_stdout, _MAX_STDERR)[key.data]:
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


def _windows_parent_python_v1(repository):
    # Bind the actual already-running interpreter, never a target PATH shim.
    path=Path(sys.executable).resolve(strict=True)
    info=path.lstat()
    if (not stat.S_ISREG(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400
            or path.is_relative_to(Path(repository).resolve())):
        _refuse('STARTUP_REFUSED','Windows parent interpreter is not outside target custody')
    return str(path).replace('\\','/')


def _original14_call(owner, route, repository, sources, arguments):
    """Preserve published R0039's held eight-member Windows read domain."""
    import contextlib
    import io
    import tempfile
    profile = _source_profile(sources)
    if profile not in ORIGINAL14_SOURCE_PROFILES_V1 and not (os.name=="nt" and _windows_core_profile_v1(profile)):
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
    if _windows_core_profile_v1(profile):
        environment["IMPLEMENTAUDIT_PYTHON"]=_windows_parent_python_v1(repository)
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
    if os.name=="nt" and _windows_core_profile_v1(_source_profile(sources)):
        return _original14_call(owner,route,repository,sources,arguments)
    _arguments(arguments)
    return _call_posix_v1(owner, repository=repository, sources=sources, arguments=arguments)


def _call_posix_v1(owner, *, repository, sources, arguments=(), canonical_run=None):
    if (sys.platform != "linux" or os.name != "posix" or not hasattr(os, "memfd_create")
            or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY")
            or os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd):
        _refuse("UNSUPPORTED_HOST", "qualified Linux memfd/directory semantics are required")
    import fcntl
    repository = _path(repository)
    source_dir = _path(str(Path(__file__).absolute().parents[1] / "skills/implementaudit/scripts"))
    environment = _environment()
    if canonical_run is not None:
        environment["TMPDIR"] = "/__implementaudit_native_snapshot/tmp"
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
        if canonical_run is not None:
            command += ["--perms", "0700", "--size", str(64*1024**2),
                "--tmpfs", "/__implementaudit_native_snapshot",
                "--dir", "/__implementaudit_native_snapshot/output",
                "--dir", "/__implementaudit_native_snapshot/tmp"]
        command += ["--remount-ro", "/", "--chdir", str(repository)]
        for key, value in sorted(environment.items()):
            command += ["--setenv", key, value]
        request = dict(repository=str(repository), members=manifests, bash=bash, arguments=arguments,
                       startup=startup, startup_members=startup_members, python=_PYTHON_ALIAS, host_python=python)
        if canonical_run is not None:
            request["run_root"] = str(canonical_run)
        child = _CHILD if canonical_run is None else _CANONICAL_SNAPSHOT_CHILD
        command += [_PYTHON_ALIAS, "-I", "-S", "-B", "-c", child, json.dumps(request, separators=(",", ":"))]
        for directory in directories:
            directory.verify()
        _sources(owner, sources, source_dir, before)
        captured = _capture(command, repository=repository, environment=environment,
                            descriptors=tuple(descriptors + list(bindings.values())),
                            maximum_stdout=_MAX_STDOUT if canonical_run is None else 32*1024**2)
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
        if canonical_run is not None:
            result["closure"]["operation"] = "CANONICAL_NATIVE_SNAPSHOT_V1"
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


# Reuse the byte-identical existing mounted-source verification prefix. No
# target-supplied program or command enters this separate fixed reader operation.
_CANONICAL_READER_BODY = "\nimport base64,types\nreader_row=next(r for r in request['members'] if r['name']=='read-canonical-pair.py')\nreader_raw=pathlib.Path(reader_row['path']).read_bytes()\nreader=types.ModuleType('_captured_original14_reader')\nreader.__file__=reader_row['path']\nexec(compile(reader_raw,reader.__file__,'exec'),reader.__dict__)\n# Charge every unique acquired owner file to the existing64MiB read budget.\n# Repeated closing reads are not new retained buffers; changed values refuse.\nseen={}\noriginal_read=reader.read_path\noriginal_owner=reader.owner\n\ndef charge(key,raw):\n    if len(raw)>16*1024**2:raise RuntimeError('canonical read file bound exceeded')\n    value=(len(raw),hashlib.sha256(raw).hexdigest())\n    if key in seen and seen[key]!=value:raise RuntimeError('canonical source changed during snapshot')\n    seen[key]=value\n    if len(seen)>4096 or sum(v[0] for v in seen.values())>64*1024**2:\n        raise RuntimeError('canonical aggregate read bound exceeded')\n    return raw\n\ndef bounded_read(path):return charge(str(path),original_read(path))\ndef bounded_owner(repo,*args):\n    result=original_owner(repo,*args)\n    if len(result.stderr)>32768:raise RuntimeError('canonical owner stderr bound exceeded')\n    charge('owner:'+repr(args),result.stdout)\n    return result\nreader.read_path=bounded_read\nreader.owner=bounded_owner\nif os.name=='nt':\n    # The reader deliberately strips caller IMPLEMENTAUDIT_* values. This fixed\n    # transport instead binds its actual isolated interpreter for nested calls;\n    # no target PATH choice or caller-supplied executable is accepted.\n    import subprocess\n    def fixed_windows_reader_call(cwd,argv):\n        environment={k:v for k,v in os.environ.items() if not k.startswith(('GIT_','IMPLEMENTAUDIT_'))}\n        environment.update(PYTHONDONTWRITEBYTECODE='1',LC_ALL='C',IMPLEMENTAUDIT_PYTHON=sys.executable.replace('\\\\','/'))\n        if argv[0] in ('git','bash'):\n            root=pathlib.Path(r'C:\\Program Files\\Git')\n            direct=root/'mingw64/bin/git.exe'\n            executable=(direct if direct.is_file() and not direct.is_symlink() else root/'cmd/git.exe') if argv[0]=='git' else root/'bin/bash.exe'\n            argv=[str(executable),*(['-c','core.longpaths=true'] if argv[0]=='git' else []),*argv[1:]]\n        return subprocess.run(argv,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=environment)\n    reader.call=fixed_windows_reader_call\noriginal_write=reader.write_snapshot\ndef bounded_write(fd,files):\n    if len(files)>4096 or sum(len(raw) for raw in files.values())>64*1024**2 or any(len(raw)>16*1024**2 for raw in files.values()):\n        raise RuntimeError('canonical temporary snapshot byte/entry bound exceeded')\n    return original_write(fd,files)\nreader.write_snapshot=bounded_write\noutput=pathlib.Path(request.get('output','/__implementaudit_native_snapshot/output'))\nif request.get('windows_snapshot_session'):\n    # One actual opening snapshot is retained by the parent across consumer use.\n    # Closing verifies that SAME snapshot through the original reader, rather\n    # than needlessly re-materializing and verifying a fresh one each call.\n    status=reader.materialize_pair(request['run_root'],str(output),native_guards=True,\n                                  verify_current=bool(request['verify_only']))\n    if status!=0:raise RuntimeError('canonical current/closing source verification refused')\nelse:\n    status=reader.materialize_pair(request['run_root'],str(output),native_guards=True)\n    if status!=0:raise RuntimeError('canonical current source unavailable; retired-root fallback forbidden')\n    if reader.materialize_pair(request['run_root'],str(output),native_guards=True,verify_current=True)!=0:\n        raise RuntimeError('canonical closing source verification refused')\nfiles={}\nused=0\nroot=output/'native-records'\nfor path in sorted(root.rglob('*')):\n    if not path.is_file():continue\n    relative=path.relative_to(root).as_posix()\n    parts=pathlib.PurePosixPath(relative).parts\n    native=(relative in ('STATE.md','ROADMAP.md') or\n            parts[0] in ('plans','phases','tasks') and relative.endswith('.md'))\n    if not native and relative!='WORK_GRAPH.json':continue\n    raw=reader.read_path(path)\n    if native and len(raw)>256*1024:raise RuntimeError('native source file bound exceeded')\n    if relative=='WORK_GRAPH.json' and len(raw)>16*1024**2:\n        raise RuntimeError('canonical WORK_GRAPH file bound exceeded')\n    if native:\n        used+=len(raw)\n        if used>4*1024**2 or len([n for n in files if n!='WORK_GRAPH.json'])>=256:\n            raise RuntimeError('native source population/byte bound exceeded')\n    files[relative]=base64.b64encode(raw).decode('ascii')\nif not {'STATE.md','ROADMAP.md','WORK_GRAPH.json'}<=set(files):\n    raise RuntimeError('canonical native source population incomplete')\nresolution=reader.read_path(output/'resolution.json')\nif len(resolution)>8192:raise RuntimeError('canonical resolution bound exceeded')\nencoded=json.dumps(dict(schema='implementaudit.canonical-native-source-snapshot.v1',\n    files=files,resolution=base64.b64encode(resolution).decode('ascii')),\n    sort_keys=True,separators=(',',':')).encode('ascii')\nif len(encoded)>32*1024**2:raise RuntimeError('canonical response bound exceeded')\nif request.get('response'):\n    with open(request['response'],'xb') as response:response.write(encoded)\n    print(json.dumps(dict(schema='implementaudit.canonical-snapshot-return.v1',bytes=len(encoded),sha256=hashlib.sha256(encoded).hexdigest()),sort_keys=True,separators=(',',':')))\nelse:print(encoded.decode('ascii'))\n"
_CANONICAL_SNAPSHOT_CHILD = _CHILD.rsplit("\nos.execv(",1)[0] + _CANONICAL_READER_BODY


def call_canonical_native_snapshot_v1(owner, *, repository, run_root, sources, route=None):
    """Read the existing reader's current original14 views, never mint authority.

    All previous readonly calls retain their exact argv/startup/output contract.
    This separate fixed operation permits no arbitrary reader flags or commands.
    Returned data remains provisional until the enclosing compiler closes use.
    """
    profile=_source_profile(sources)
    if (len(profile)!=8 or profile[-1][0]!='read-canonical-pair.py' or
            tuple(row[0] for row in profile)!=('claim-run.sh','validate-run-root.sh',
              'claim-run-rotation.py','rotate-canonical-state.py','canonical_hot_projection.py',
              'canonical_custody.py','canonical_rotation_inputs.py','read-canonical-pair.py')):
        _refuse('SOURCE_REFUSED','canonical native read requires its complete eight-source owner')
    repository=_path(repository);run_root=_path(run_root)
    if not run_root.is_relative_to(repository) or run_root==repository:
        _refuse('REPOSITORY_REFUSED','canonical run root is outside the bound repository')
    # Do not remove or reinterpret the separately qualified Windows custody gate.
    # Unsupported canonical-source execution refuses instead of using retired data.
    if os.name=='nt':
        return _call_windows_canonical_snapshot_v1(owner,route,repository,run_root,sources)
    return _call_posix_v1(owner,repository=str(repository),sources=sources,canonical_run=run_root)


@contextlib.contextmanager
def canonical_snapshot_source_context_v1(owner, *, repository, run_root, sources, route=None):
    """Hold the already selected source identities across consumer use."""
    if os.name=='nt':
        session={}
        try:
            try:
                with _windows_held_source_context_v1(owner,sources):
                    yield lambda:_call_windows_canonical_snapshot_v1(owner,route,_path(repository),_path(run_root),sources,session=session)
            finally:
                if session:_close_windows_snapshot_session_v1(owner,session)
        except (OSError,owner.OperationalEvidenceError,subprocess.SubprocessError) as exc:
            raise ContinuityTransportError('CONTINUITY_TRANSPORT_CUSTODY_REFUSED',str(exc)) from exc
        return
    source_dir=_path(str(Path(__file__).absolute().parents[1]/'skills/implementaudit/scripts'))
    held=_Directory(source_dir)
    try:
        before,_=_sources(owner,sources,source_dir)
        def read():
            held.verify();_sources(owner,sources,source_dir,before)
            result=call_canonical_native_snapshot_v1(owner,repository=repository,
                run_root=run_root,sources=sources,route=route)
            _sources(owner,sources,source_dir,before);held.verify()
            return result
        yield read
        _sources(owner,sources,source_dir,before);held.verify()
    finally:held.close()


_WINDOWS_CANONICAL_PREFIX = r"""
import sys,os,json,pathlib,hashlib,stat
request=json.loads(sys.argv[1])
if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
    raise RuntimeError('canonical Windows startup differs')
if pathlib.Path.cwd()!=pathlib.Path(request['repository']):raise RuntimeError('canonical Windows cwd differs')
for row in request['members']:
    path=pathlib.Path(row['path']);before=path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or getattr(before,'st_file_attributes',0)&0x400:
        raise RuntimeError('canonical Windows source type/alias differs')
    raw=path.read_bytes();after=path.lstat()
    stamp=lambda v:(v.st_dev,v.st_ino,v.st_mode,v.st_nlink,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
    if stamp(before)!=stamp(after) or len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:
        raise RuntimeError('canonical Windows held source differs')
"""

@contextlib.contextmanager
def _windows_held_source_context_v1(owner,sources,*,closed=False):
    profile=_source_profile(sources)
    if os.name!='nt' or len(profile)!=8:
        _refuse('UNSUPPORTED_HOST','NTFS canonical source hold requires eight selected Windows sources')
    raw_by_name={Path(path).name:raw for path,raw in sources}
    source_dir=_path(sources[0][0]).parent
    custody=owner._native_module_from_bytes(raw_by_name['canonical_custody.py'],source_dir/'canonical_custody.py',
        '_canonical_snapshot_windows_custody','$native.canonical.source_hold')
    with contextlib.ExitStack() as stack:
        directory=stack.enter_context(custody.Directory(source_dir));held=[]
        names={row[0] for row in profile}
        if closed and set(directory.names())!=names:_refuse('SOURCE_CHANGED','private Windows source population differs')
        for (path,raw),row in zip(sources,profile):
            if _path(path)!=source_dir/row[0] or len(raw)!=row[1] or hashlib.sha256(raw).hexdigest()!=row[2]:
                _refuse('SOURCE_REFUSED','canonical Windows sibling source differs')
            item=stack.enter_context(custody.File(directory,row[0],maximum=len(raw)))
            if item.read()!=raw:_refuse('SOURCE_CHANGED','canonical Windows captured bytes differ')
            held.append((item,raw))
        yield
        if closed and set(directory.names())!=names:_refuse('SOURCE_CHANGED','private Windows source population changed')
        for item,raw in held:
            item.verify()
            if item.read()!=raw:_refuse('SOURCE_CHANGED','canonical Windows source changed before close')


def _close_windows_snapshot_session_v1(owner,session):
    import tempfile,shutil
    root=session['root']
    info=root.lstat()
    if (root.parent.resolve()!=Path(tempfile.gettempdir()).resolve() or
            not root.name.startswith('implementaudit-canonical-source-') or
            (info.st_dev,info.st_ino)!=session['root_identity'] or
            not stat.S_ISDIR(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400):
        _refuse('CLEANUP_REFUSED','canonical private output root changed; residue='+str(root))
    if session.get('hold') is not None:session['hold'].__exit__(None,None,None)
    if session['code'].exists():owner._native_cleanup_private_closure(session['code'],session['expected'])
    shutil.rmtree(root)


def _call_windows_canonical_snapshot_v1(owner,route,repository,run_root,sources,*,session=None):
    import tempfile
    if os.name!='nt' or route is None:
        _refuse('UNSUPPORTED_HOST','canonical Windows read requires its existing held-source host route')
    local=session is None
    if local:session={}
    raw_by_name={Path(path).name:raw for path,raw in sources}
    custody=owner._native_module_from_bytes(raw_by_name['canonical_custody.py'],
        _path(sources[0][0]).parent/'canonical_custody.py','_canonical_snapshot_private_custody','$native.canonical.private')
    if not session:
        root=Path(tempfile.mkdtemp(prefix='implementaudit-canonical-source-'))
        info=root.lstat();code=root/'source';view=root/'view';scratch=root/'tmp';expected=[]
        # Register ownership before any fallible setup. A partial or changed
        # source refuses cleanup with its original residue rather than vanishing.
        session.update(root=root,root_identity=(info.st_dev,info.st_ino),code=code,view=view,
                       scratch=scratch,expected=expected,hold=None,reads=0)
        try:
            code.mkdir();view.mkdir();scratch.mkdir()
            for name,raw in raw_by_name.items():
                target=code/name
                with target.open('xb') as out:out.write(raw)
                expected.append((target,raw))
            hold=_windows_held_source_context_v1(owner,tuple((str(path),raw) for path,raw in expected),closed=True)
            hold.__enter__();session['hold']=hold
        except BaseException:
            if local:_close_windows_snapshot_session_v1(owner,session)
            raise
    root,view,scratch=session['root'],session['view'],session['scratch']
    try:
        environment=owner._native_child_environment(route)
        environment['IMPLEMENTAUDIT_PYTHON']=_windows_parent_python_v1(repository)
        environment['PATH']=str(Path(sys.executable).resolve().parent)+os.pathsep+environment.get('PATH','')
        environment.update(GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0',
            GIT_CONFIG_SYSTEM=os.devnull,TMP=str(scratch),TEMP=str(scratch),TMPDIR=str(scratch))
        config={'core.fsmonitor':'false','core.hooksPath':os.devnull,'protocol.allow':'never',
            'protocol.ext.allow':'never','credential.helper':'','core.sshCommand':'',
            'submodule.recurse':'false','core.longpaths':'true'}
        environment['GIT_CONFIG_COUNT']=str(len(config))
        for i,(key,value) in enumerate(config.items()):
            environment['GIT_CONFIG_KEY_'+str(i)]=key;environment['GIT_CONFIG_VALUE_'+str(i)]=value
        if session['reads']>=2:_refuse('OUTPUT_BOUND','canonical snapshot consumption already closed')
        response=root/('snapshot-'+str(session['reads'])+'.json')
        members=[dict(name=path.name,path=str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for path,raw in session['expected']]
        request=dict(repository=str(repository),run_root=str(run_root),members=members,output=str(view),response=str(response),
                     windows_snapshot_session=True,verify_only=session['reads']>0)
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',_WINDOWS_CANONICAL_PREFIX+_CANONICAL_READER_BODY,
            json.dumps(request,separators=(',',':'))],cwd=repository,env=environment,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=_TIMEOUT,check=False)
        if result.returncode or result.stderr or len(result.stdout)>_MAX_STDOUT:
            raise ContinuityTransportError('CONTINUITY_TRANSPORT_OWNER_REFUSED','canonical Windows reader refused',
                returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        acknowledgement=json.loads(result.stdout)
        with custody.Directory(root) as directory:
            with custody.File(directory,response.name,maximum=32*1024**2) as held:raw=held.read()
        if acknowledgement!=dict(schema='implementaudit.canonical-snapshot-return.v1',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()):
            _refuse('OBSERVATION_REFUSED','canonical Windows response identity differs')
        session['reads']+=1
        rows=[dict(name=Path(path).name,path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                   mode=stat.S_IMODE(Path(path).lstat().st_mode),links=1,held=True) for path,data in sources]
        return dict(returncode=0,stdout=raw,stderr=b'',closure=dict(
            schema='implementaudit.continuity-windows-source-closure.v1',repository=str(repository),
            members=rows,custody='WINDOWS_HELD_FILES_V1',operation='CANONICAL_NATIVE_SNAPSHOT_V1'))
    finally:
        if local and session:_close_windows_snapshot_session_v1(owner,session)
