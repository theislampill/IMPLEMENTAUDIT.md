#!/usr/bin/env python3
"""Separate fixed genuine-C5 executor source owner; no default whitelist change.

The outer caller must bind the exact loader buffer it executes. A read of this
file is physical currentness only. Post-commit comparison metadata has no live
custody or completion authority and cannot select commands or source members.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import types

ROOT=Path(__file__).absolute().parents[1]
LOADER='scripts/load-work-graph-c5-executor.py'
MAX_SOURCE_BYTES=1024**2
PREFIX = 'scripts/qualify-work-graph-prefix.py'
BASE = 'scripts/work-graph-c5-inputs.py'
PROVIDER = 'scripts/work-graph-c5-provider-inputs.py'
EVENT = 'scripts/repro-event-capture.py'
COMPLETION = 'scripts/work-graph-completion.py'
COMPILER = 'skills/implementaudit/scripts/compile-work-graph.py'
QUALIFIER = 'scripts/qualify-work-graph-verifier.py'
GATE = 'scripts/work-graph-c5-live-gate.py'
EXECUTOR = 'scripts/work-graph-c5-executor.py'
BASE_SELECTION = 'fixtures/work-graph-c5-inputs/execution-system-python312.json'
PROVIDER_SELECTION = 'fixtures/work-graph-c5-inputs/package-venv-python312.json'
EXECUTION_SELECTION = 'fixtures/work-graph-c5-inputs/genuine-execution-profile.json'
PROFILE='FIXED_GENUINE_C5_PRODUCER_EFFECT_ORIGINAL48_V1'
PINS=types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': '86f4e02dbf7b25ee3a4dab2fb90ef4dd3e21cfe350e8ce38470e36c4f4733016', 'scripts/work-graph-c5-inputs.py': 'c9dc12fb3d9c12c8161426956944730ba543f66ffec0c36abd8a1193f3c5cd4f', 'scripts/work-graph-c5-provider-inputs.py': '9b29c100a2b89fe6f53072f726f990ecd115cdb6f7bff574e2e62b48099baff4', 'scripts/repro-event-capture.py': 'f8238acbb6aea7bb1c246774ee780149abad56c9221fe31640d522e53f8da443', 'scripts/work-graph-completion.py': '1a73009c7085c66797d9310258b2b1d723f304a0034cbc6a7ce16e1c97283b92', 'skills/implementaudit/scripts/compile-work-graph.py': '1824b1f9d38c53d45016ed249926784c958cfd24b59920df2252ef366f6ec46b', 'scripts/qualify-work-graph-verifier.py': 'b06561d44f48d49aef97f9a29364e4016cdff44782381d1cca258a86420171a0', 'scripts/work-graph-c5-live-gate.py': '5221b3039263ba42ededa080591cd9e23608e44ee601ad8b72b7eba590a7be60', 'scripts/work-graph-c5-executor.py': '3be657bce635eafccf0b000dedb85e2ae62cb95c874b03c953c192738b9524ce', 'fixtures/work-graph-c5-inputs/execution-system-python312.json': 'c22e25897db88cb86a345a79ff5da39ef7b335571aff8786617ea6c82a4ac1fa', 'fixtures/work-graph-c5-inputs/package-venv-python312.json': 'c6ba97cd3be936284eab790b3b35cec92c4f84252086c817eabbd372c2c68014', 'fixtures/work-graph-c5-inputs/genuine-execution-profile.json': '5dbcaddb4d33ee046592030c49108e859fd104c75e138d3be614b4cc82c194b1'})
ORIGINS=types.MappingProxyType({'base_logical_key': 'fixtures/work-graph-c5-inputs/system-python312.json', 'base_actual_member': 'fixtures/work-graph-c5-inputs/execution-system-python312.json', 'provider_actual_member': 'fixtures/work-graph-c5-inputs/package-venv-python312.json'})
CURRENT_PROFILE='FIXED_GENUINE_C5_PRODUCER_EFFECT_CURRENT_COMPOSITE_20261027_V1'
CURRENT_BASE_SELECTION='fixtures/work-graph-c5-inputs/execution-current-composite-python312.json'
CURRENT_PROVIDER_SELECTION='fixtures/work-graph-c5-inputs/package-current-venv-python312.json'
CURRENT_EXECUTION_SELECTION='fixtures/work-graph-c5-inputs/genuine-current-execution-profile.json'
CURRENT_PINS=types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': '49a559777539285a7a31886686459134a1e135675f2e542c079a0b71360b5bd1', 'scripts/work-graph-c5-provider-inputs.py': '05bcb64db1ad0787ce8704846ea0ee4f3127f24d2dc471a9abcb14736937b81a', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': '25f2c24645cc65ed4b9bfbd70bb2d0ce26eb6accc51de0af0df06b3bdff5b627', 'scripts/qualify-work-graph-verifier.py': 'c090833db1049c5922d78875fab4630ed686e23e56f5aca1926db482457c6c13', 'scripts/work-graph-c5-live-gate.py': '4979cc5aa810cf2abdbca67cd70c553b624d6f8d643d2c1ea2e643845fab6c25', 'scripts/work-graph-c5-executor.py': '3c8d532cc72b379b2e9cc19e00968ac7949204208489df7445f7bda98cead232', 'fixtures/work-graph-c5-inputs/execution-current-composite-python312.json': '88f4ca9e83145e25b335e6c6ebc413e57e27a80a4659276ba8b7a6cd58e1ca74', 'fixtures/work-graph-c5-inputs/package-current-venv-python312.json': '7a2bf024717d56bf5316fe70227d14202509bde0bbd39a20214b39f97986d923', 'fixtures/work-graph-c5-inputs/genuine-current-execution-profile.json': '40803e190ad9f4c017407d17b6a5560bfb5de1518d766277c97349b88907d033'})
CURRENT_ORIGINS=types.MappingProxyType(dict(base_logical_key=ORIGINS['base_logical_key'],
    base_actual_member=CURRENT_BASE_SELECTION, provider_actual_member=CURRENT_PROVIDER_SELECTION))


# Explicit new closed tuple; previous support/runtime bytes retained in test-support.
TASK_PROFILE='FIXED_GENUINE_C5_PRODUCER_EFFECT_SOL_TASK_LINUX_20261029_V1'
TASK_BASE_SELECTION='fixtures/work-graph-c5-inputs/execution-sol-task-python312.json'
TASK_PROVIDER_SELECTION='fixtures/work-graph-c5-inputs/package-sol-task-venv-python312.json'
TASK_EXECUTION_SELECTION='fixtures/work-graph-c5-inputs/genuine-sol-task-execution-profile.json'
TASK_PINS=types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': '49a559777539285a7a31886686459134a1e135675f2e542c079a0b71360b5bd1', 'scripts/work-graph-c5-provider-inputs.py': '05bcb64db1ad0787ce8704846ea0ee4f3127f24d2dc471a9abcb14736937b81a', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': '25f2c24645cc65ed4b9bfbd70bb2d0ce26eb6accc51de0af0df06b3bdff5b627', 'scripts/qualify-work-graph-verifier.py': 'c090833db1049c5922d78875fab4630ed686e23e56f5aca1926db482457c6c13', 'scripts/work-graph-c5-live-gate.py': '4979cc5aa810cf2abdbca67cd70c553b624d6f8d643d2c1ea2e643845fab6c25', 'scripts/work-graph-c5-executor.py': '3c8d532cc72b379b2e9cc19e00968ac7949204208489df7445f7bda98cead232', 'fixtures/work-graph-c5-inputs/execution-sol-task-python312.json': 'e244d797a8808feee51b981c4182ffcfe567f5affb467428e9f93a37e72b745e', 'fixtures/work-graph-c5-inputs/package-sol-task-venv-python312.json': 'cf53875d2414184a48b153a139ebc7298483b33876c7379aa07d8450536ca446', 'fixtures/work-graph-c5-inputs/genuine-sol-task-execution-profile.json': 'ad043e04ca9a08add791a0a3378df33de7ed27c6ee923ced84d733321a5da760'})
TASK_ORIGINS=types.MappingProxyType(dict(base_logical_key=ORIGINS["base_logical_key"], base_actual_member=TASK_BASE_SELECTION, provider_actual_member=TASK_PROVIDER_SELECTION))

# Separate prospective two-original shared-image profile; historical tuples above remain immutable.
CORRESPONDENCE_PROFILE='FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_20261031_V1'
CORRESPONDENCE_BASE_SELECTION='fixtures/work-graph-c5-inputs/execution-correspondence-python312.json'
CORRESPONDENCE_ORIGINS=types.MappingProxyType(dict(TASK_ORIGINS,base_actual_member=CORRESPONDENCE_BASE_SELECTION))
CORRESPONDENCE_EXECUTION_SELECTION='fixtures/work-graph-c5-inputs/genuine-correspondence-execution-profile.json'
CORRESPONDENCE_PINS=types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': '49a559777539285a7a31886686459134a1e135675f2e542c079a0b71360b5bd1', 'scripts/work-graph-c5-provider-inputs.py': '05bcb64db1ad0787ce8704846ea0ee4f3127f24d2dc471a9abcb14736937b81a', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': '25f2c24645cc65ed4b9bfbd70bb2d0ce26eb6accc51de0af0df06b3bdff5b627', 'scripts/qualify-work-graph-verifier.py': 'c090833db1049c5922d78875fab4630ed686e23e56f5aca1926db482457c6c13', 'scripts/work-graph-c5-live-gate.py': '4979cc5aa810cf2abdbca67cd70c553b624d6f8d643d2c1ea2e643845fab6c25', 'scripts/work-graph-c5-executor.py': '3c8d532cc72b379b2e9cc19e00968ac7949204208489df7445f7bda98cead232', 'fixtures/work-graph-c5-inputs/execution-correspondence-python312.json': '70b152d79a3921f9c5772121e7f1ab1ce63266445b308e632c706c7e87c40163', 'fixtures/work-graph-c5-inputs/package-sol-task-venv-python312.json': 'cf53875d2414184a48b153a139ebc7298483b33876c7379aa07d8450536ca446', 'fixtures/work-graph-c5-inputs/genuine-correspondence-execution-profile.json': '9463226d36ea19e51e9b0a6b9a753968600ca55cf4e6a7b41024941d1108f8a3'})

# Public-base derivative of the independently qualified streaming executor.
# The public compiler/qualifier and every preceding tuple stay unchanged.
PUBLIC_STREAMING_SOURCE_REVISION='DG16_PUBLIC_BASE_STREAMING_OWNED_DIGEST_SOURCE_20261101_V1'
PUBLIC_STREAMING_EXECUTOR_SHA256='5b9d9fea7f67dd3ab3a58ee4ff648ee07c0f3ce9cbf069629f33906c04c6cfcf'
PUBLIC_STREAMING_PINS=types.MappingProxyType({
    profile:types.MappingProxyType(dict(pins,**{EXECUTOR:PUBLIC_STREAMING_EXECUTOR_SHA256}))
    for profile,pins in ((CURRENT_PROFILE,CURRENT_PINS),(CORRESPONDENCE_PROFILE,CORRESPONDENCE_PINS))})


# Exact composed source successor; runtime, executor and old revision stay fixed.
CURRENT105_SOURCE_REVISION='DG16_CURRENT105_CLOSED_RUNTIME_SOURCE_20261104_V1'
CURRENT105_QUALIFIER_SHA256='0f148dc343a955dde59c7b6a22d89d5885c920cd4c6ceeba455cec80b88adc23'
CURRENT105_PINS=types.MappingProxyType({
    profile:types.MappingProxyType(dict(pins,**{QUALIFIER:CURRENT105_QUALIFIER_SHA256}))
    for profile,pins in PUBLIC_STREAMING_PINS.items()})


# Exact successor for the composed continuity repair. The R2 V1 tuple and
# every runtime selection remain unchanged; this revision adds no authority.
CURRENT105_COMPOSED_SOURCE_REVISION='DG16_CURRENT105_COMPOSED_CONTINUITY_SOURCE_20261104_V2'
CURRENT105_COMPOSED_COMPILER_SHA256='bce6f3bad3a98f850cb5d30e1df21ca8da237ba20609d49a609cccef1a81f21e'
CURRENT105_COMPOSED_PINS=types.MappingProxyType({
    profile:types.MappingProxyType(dict(pins,**{COMPILER:CURRENT105_COMPOSED_COMPILER_SHA256}))
    for profile,pins in CURRENT105_PINS.items()})


# Explicit fresh subject/current-host successor; all preceding pins remain unchanged.
R4_CORRESPONDENCE_PROFILE='FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_R4_CURRENT_HOST_20261104_V1'
R4_SOURCE_REVISION='DG16_R4_OWNED_CURRENT_HOST_SOURCE_20261104_V1'
R4_BASE_SELECTION='fixtures/work-graph-c5-inputs/execution-r4-current-host-python312.json'
R4_PROVIDER_SELECTION='fixtures/work-graph-c5-inputs/package-r4-owned-venv-python312.json'
R4_EXECUTION_SELECTION='fixtures/work-graph-c5-inputs/genuine-r4-correspondence-execution-profile.json'
R4_ORIGINS=types.MappingProxyType(dict(base_logical_key=ORIGINS['base_logical_key'],base_actual_member=R4_BASE_SELECTION,provider_actual_member=R4_PROVIDER_SELECTION))
R4_PINS=types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': '99c833db89500f2784f4f625cb757a56acc71eb688094bc9fc51f1c9440c694a', 'scripts/work-graph-c5-provider-inputs.py': '34699698d49f10c854b6f831bf38b856adb84791bf848e26fc105a1f1687a776', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': 'bce6f3bad3a98f850cb5d30e1df21ca8da237ba20609d49a609cccef1a81f21e', 'scripts/qualify-work-graph-verifier.py': '0f148dc343a955dde59c7b6a22d89d5885c920cd4c6ceeba455cec80b88adc23', 'scripts/work-graph-c5-live-gate.py': '4979cc5aa810cf2abdbca67cd70c553b624d6f8d643d2c1ea2e643845fab6c25', 'scripts/work-graph-c5-executor.py': '019bfc7b069295759847a1668345cae7112a789a9392a6233f4b7119c1cc237d', 'fixtures/work-graph-c5-inputs/execution-r4-current-host-python312.json': '83dadabffcc276d29748c210d9ca6c5c776fecb655d173ae577d8b7fedc16cf2', 'fixtures/work-graph-c5-inputs/package-r4-owned-venv-python312.json': 'c7d405ab460ecabf85ccb4ce13f6df97d0564a7aaa2cd0b6073478272e06bf17', 'fixtures/work-graph-c5-inputs/genuine-r4-correspondence-execution-profile.json': 'd7c89be13320e4c9ee98702b64a07232d8646d190be48adfc5e08724b4ade9f6'})


R4_MEMO_SOURCE_REVISION='DG16_R4_GUARDED_PREFIX_READBACK_SOURCE_20261104_V2'
R4_MEMO_PINS=types.MappingProxyType(dict(R4_PINS, **{GATE:'a5ec1232870739da0f7f987fef804b9098c719db92f12abf09e850d08f90c7d9'}))
R4_ORIGINAL_GATE_MEMBER='fixtures/work-graph-c5-inputs/r4-live-gate-original-v1.py.txt'


R4_COPY_MEMO_SOURCE_REVISION='DG16_R4_GUARDED_SOURCE_COPY_ADMISSION_20261104_V3'
R4_COPY_MEMO_PINS=types.MappingProxyType(dict(R4_MEMO_PINS, **{GATE:'4ed3413327b0fa6337d49245d144f1db3a52fe0d133671665041dffb04db602e'}))
R4_PREFIX_GATE_MEMBER='fixtures/work-graph-c5-inputs/r4-live-gate-prefix-v2.py.txt'


# Composed successor for received DG16 and DG18 owners. No old pin is rewritten.
R4_COMPOSED_SOURCE_REVISION='DG16_DG18_R4_COMPOSED_SOURCE_20261104_V4'
R4_COMPOSED_OWNER_PINS=types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': '99c833db89500f2784f4f625cb757a56acc71eb688094bc9fc51f1c9440c694a', 'scripts/work-graph-c5-provider-inputs.py': '34699698d49f10c854b6f831bf38b856adb84791bf848e26fc105a1f1687a776', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': 'addcae949fdab009f7f0b4a9f023392309841c1798357ca89f9ec2b84d4c8ba9', 'scripts/qualify-work-graph-verifier.py': '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b', 'scripts/work-graph-c5-live-gate.py': '4ed3413327b0fa6337d49245d144f1db3a52fe0d133671665041dffb04db602e', 'scripts/work-graph-c5-executor.py': '019bfc7b069295759847a1668345cae7112a789a9392a6233f4b7119c1cc237d'})
R4_COMPOSED_PINS=types.MappingProxyType({
    CURRENT_PROFILE:types.MappingProxyType(dict(CURRENT105_COMPOSED_PINS[CURRENT_PROFILE],**R4_COMPOSED_OWNER_PINS)),
    CORRESPONDENCE_PROFILE:types.MappingProxyType(dict(CURRENT105_COMPOSED_PINS[CORRESPONDENCE_PROFILE],**R4_COMPOSED_OWNER_PINS)),
    R4_CORRESPONDENCE_PROFILE:types.MappingProxyType(dict(R4_PINS,**R4_COMPOSED_OWNER_PINS)),
})

R4_PREFIX_RESULT_SOURCE_REVISION='DG16_R4_GUARDED_PREFIX_RESULT_ADMISSION_20261104_V5'
R4_COPY_GATE_MEMBER='fixtures/work-graph-c5-inputs/r4-source-copy-gate-v3.py'
R4_PREFIX_RESULT_PINS=types.MappingProxyType(dict(R4_COMPOSED_PINS[R4_CORRESPONDENCE_PROFILE],
    **{GATE: 'b252d0c1ac55e64caa9d8ed8b45402e0e8a6854227e4681b7ffe612eb5c7c3d5'}))


# Explicit build-local package compression successor; historical tuples are immutable.
R4_BUILD_CACHE_PROFILE='FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_R4_BUILD_LOCAL_COMPRESSION_20261104_V1'
R4_BUILD_CACHE_SOURCE_REVISION='DG16_R4_BUILD_LOCAL_COMPRESSION_SOURCE_20261104_V6'
R4_BUILD_CACHE_BASE_SELECTION='fixtures/work-graph-c5-inputs/execution-r4-build-local-compression-python312.json'
R4_BUILD_CACHE_EXECUTION_SELECTION='fixtures/work-graph-c5-inputs/genuine-r4-build-local-compression-execution-profile.json'
R4_BUILD_CACHE_ORIGINS=types.MappingProxyType(dict(R4_ORIGINS,base_actual_member=R4_BUILD_CACHE_BASE_SELECTION))
R4_BUILD_CACHE_PINS=types.MappingProxyType(dict(
    {name:pin for name,pin in R4_PREFIX_RESULT_PINS.items() if name not in (R4_BASE_SELECTION,R4_EXECUTION_SELECTION)},
    **{'scripts/work-graph-c5-inputs.py': 'dbe0eb5765a249b02f13f97c379a83da7b7a6c68ba2c8320100cd973381c2b6e', 'scripts/work-graph-c5-executor.py': 'ac9a7ea7f364c235aa1192a715a4c33c712bcd249275eb8bdce7064702a4bf4d', 'fixtures/work-graph-c5-inputs/execution-r4-build-local-compression-python312.json': '25c8348ef3f03bb9bb60c234ac6701cc35cf498902fcec4164868f9c48f1f70f', 'fixtures/work-graph-c5-inputs/genuine-r4-build-local-compression-execution-profile.json': '83cfa2de999dc79aaca5aa7973bfa56ec334a4698c42a4c5f4b0706c4c80c60a'}))
R4_BUILD_CACHE_PHYSICAL_HISTORY=types.MappingProxyType({'scripts/work-graph-c5-inputs.py': ('fixtures/work-graph-c5-inputs/r4-inputs-before-build-cache-v5.py', '99c833db89500f2784f4f625cb757a56acc71eb688094bc9fc51f1c9440c694a'), 'scripts/work-graph-c5-executor.py': ('fixtures/work-graph-c5-inputs/r4-executor-before-build-cache-v5.py', '019bfc7b069295759847a1668345cae7112a789a9392a6233f4b7119c1cc237d')})

# Reviewed initialization successor; same bounded C5 execution policy and provider.
R4_INITIALIZATION_SOURCE_REVISION = 'DG16_DG17_DG18_R4_CONTROLLER_INITIALIZATION_SOURCE_20261104_V1'
R4_INITIALIZATION_PINS = types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': 'dbe0eb5765a249b02f13f97c379a83da7b7a6c68ba2c8320100cd973381c2b6e', 'scripts/work-graph-c5-provider-inputs.py': '34699698d49f10c854b6f831bf38b856adb84791bf848e26fc105a1f1687a776', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': '1e33ab31553903ca64f58b64673371e0ec4efdf3208031db79f50898744ca033', 'scripts/qualify-work-graph-verifier.py': '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b', 'scripts/work-graph-c5-live-gate.py': 'b252d0c1ac55e64caa9d8ed8b45402e0e8a6854227e4681b7ffe612eb5c7c3d5', 'scripts/work-graph-c5-executor.py': 'ac9a7ea7f364c235aa1192a715a4c33c712bcd249275eb8bdce7064702a4bf4d', 'fixtures/work-graph-c5-inputs/package-r4-owned-venv-python312.json': 'c7d405ab460ecabf85ccb4ce13f6df97d0564a7aaa2cd0b6073478272e06bf17', 'fixtures/work-graph-c5-inputs/execution-r4-build-local-compression-python312.json': '25c8348ef3f03bb9bb60c234ac6701cc35cf498902fcec4164868f9c48f1f70f', 'fixtures/work-graph-c5-inputs/genuine-r4-build-local-compression-execution-profile.json': '83cfa2de999dc79aaca5aa7973bfa56ec334a4698c42a4c5f4b0706c4c80c60a'})
R4_INITIALIZATION_PHYSICAL_HISTORY = types.MappingProxyType({'skills/implementaudit/scripts/compile-work-graph.py': ('test-support/r4-controller-initialization-history/f0b9-source/skills/implementaudit/scripts/compile-work-graph.py', 'addcae949fdab009f7f0b4a9f023392309841c1798357ca89f9ec2b84d4c8ba9')})

# Windows spelling repair successor; same bounded C5 execution policy and provider.
R5_WINDOWS_INITIALIZATION_SOURCE_REVISION = 'DG16_DG17_DG18_R5_WINDOWS_INITIALIZATION_SOURCE_20261105_V1'
R5_WINDOWS_INITIALIZATION_PINS = types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': 'dbe0eb5765a249b02f13f97c379a83da7b7a6c68ba2c8320100cd973381c2b6e', 'scripts/work-graph-c5-provider-inputs.py': '34699698d49f10c854b6f831bf38b856adb84791bf848e26fc105a1f1687a776', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': '62c3b0fb95bbf006ef81e981a16325395e6165ae65c901f667de0e60bf74de3c', 'scripts/qualify-work-graph-verifier.py': '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b', 'scripts/work-graph-c5-live-gate.py': 'b252d0c1ac55e64caa9d8ed8b45402e0e8a6854227e4681b7ffe612eb5c7c3d5', 'scripts/work-graph-c5-executor.py': 'ac9a7ea7f364c235aa1192a715a4c33c712bcd249275eb8bdce7064702a4bf4d', 'fixtures/work-graph-c5-inputs/package-r4-owned-venv-python312.json': 'c7d405ab460ecabf85ccb4ce13f6df97d0564a7aaa2cd0b6073478272e06bf17', 'fixtures/work-graph-c5-inputs/execution-r4-build-local-compression-python312.json': '25c8348ef3f03bb9bb60c234ac6701cc35cf498902fcec4164868f9c48f1f70f', 'fixtures/work-graph-c5-inputs/genuine-r4-build-local-compression-execution-profile.json': '83cfa2de999dc79aaca5aa7973bfa56ec334a4698c42a4c5f4b0706c4c80c60a'})
R5_WINDOWS_INITIALIZATION_PHYSICAL_HISTORY = types.MappingProxyType({'skills/implementaudit/scripts/compile-work-graph.py': ('test-support/r5-windows-initialization-history/75e2da4-source/skills/implementaudit/scripts/compile-work-graph.py', '1e33ab31553903ca64f58b64673371e0ec4efdf3208031db79f50898744ca033')})

# Windows bounded-capture repair successor; same bounded C5 execution policy and provider.
R5_WINDOWS_CAPTURE_SOURCE_REVISION = 'DG16_DG17_DG18_R5_WINDOWS_CAPTURE_SOURCE_20261105_V1'
R5_WINDOWS_CAPTURE_PINS = types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': 'dbe0eb5765a249b02f13f97c379a83da7b7a6c68ba2c8320100cd973381c2b6e', 'scripts/work-graph-c5-provider-inputs.py': '34699698d49f10c854b6f831bf38b856adb84791bf848e26fc105a1f1687a776', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': '2e447dd27364918d7c0f5b508f17650fd2cc9a5c716ffe105c35ecbcb66a533e', 'scripts/qualify-work-graph-verifier.py': '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b', 'scripts/work-graph-c5-live-gate.py': 'b252d0c1ac55e64caa9d8ed8b45402e0e8a6854227e4681b7ffe612eb5c7c3d5', 'scripts/work-graph-c5-executor.py': 'ac9a7ea7f364c235aa1192a715a4c33c712bcd249275eb8bdce7064702a4bf4d', 'fixtures/work-graph-c5-inputs/package-r4-owned-venv-python312.json': 'c7d405ab460ecabf85ccb4ce13f6df97d0564a7aaa2cd0b6073478272e06bf17', 'fixtures/work-graph-c5-inputs/execution-r4-build-local-compression-python312.json': '25c8348ef3f03bb9bb60c234ac6701cc35cf498902fcec4164868f9c48f1f70f', 'fixtures/work-graph-c5-inputs/genuine-r4-build-local-compression-execution-profile.json': '83cfa2de999dc79aaca5aa7973bfa56ec334a4698c42a4c5f4b0706c4c80c60a'})
R5_WINDOWS_CAPTURE_PHYSICAL_HISTORY = types.MappingProxyType({'skills/implementaudit/scripts/compile-work-graph.py': ('test-support/r5-windows-capture-history/d2747b7-source/skills/implementaudit/scripts/compile-work-graph.py', '62c3b0fb95bbf006ef81e981a16325395e6165ae65c901f667de0e60bf74de3c')})

R5_HOSTED_PROFILE='FIXED_GENUINE_C5_SHARED_IMAGE_R5_HOSTED_UBUNTU24_SINGLE_COPY_20261105_V1'
R5_HOSTED_SOURCE_REVISION='R5_HOSTED_UBUNTU24_SINGLE_COPY_SOURCE_20261105_V1'
R5_HOSTED_BASE_SELECTION='fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-python312.json'
R5_HOSTED_PROVIDER_SELECTION='fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-python312.json'
R5_HOSTED_EXECUTION_SELECTION='fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-execution-profile.json'
R5_HOSTED_PINS=types.MappingProxyType({'scripts/qualify-work-graph-prefix.py': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab', 'scripts/work-graph-c5-inputs.py': '2befafe8c933467bd6dffbe2d4d27b09b4d6e3b52cab3e1ce680ac061a49310a', 'scripts/work-graph-c5-provider-inputs.py': 'e6cb523c3ce2f59fcdb2a1ed90db75d987ca59456dc423d82aceeeaff01d594f', 'scripts/repro-event-capture.py': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08', 'scripts/work-graph-completion.py': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb', 'skills/implementaudit/scripts/compile-work-graph.py': '3649a8dc856e29ce11b6daa5861351cc1c21bf9c7a9b4f5a2ddde12108d8581f', 'scripts/qualify-work-graph-verifier.py': '8cc8342f025866ffaf8c98cc1dd33d7576416c2de39e9d444b9acfd546685a0b', 'scripts/work-graph-c5-live-gate.py': 'b252d0c1ac55e64caa9d8ed8b45402e0e8a6854227e4681b7ffe612eb5c7c3d5', 'scripts/work-graph-c5-executor.py': 'd9b9ad23eefaa62bb273970232dc5669ab40d465c6f9d5bf5f83b7048e8df1d8', 'fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-python312.json': '15e71318bfb65427e5f5bb49bd0a7e6f5cf4460618ef1b64d3d598b447646e97', 'fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-python312.json': 'c13127d28bf98d8ca192e6bb2de8be5fc9d515b9cef3d88319c45166528fe430', 'fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-execution-profile.json': '3e90519906504e432dd44094bc78e34b14e305c6a6907c07b3ad379829b5962c'})
R5_HOSTED_ORIGINS=types.MappingProxyType({'base_logical_key': 'fixtures/work-graph-c5-inputs/system-python312.json', 'base_actual_member': 'fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-python312.json', 'provider_actual_member': 'fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-python312.json'})
R5_HOSTED_PHYSICAL_HISTORY=types.MappingProxyType({'scripts/work-graph-c5-inputs.py': ('test-support/r5-c5-hosted-profile-history/source481e/scripts/work-graph-c5-inputs.py', 'dbe0eb5765a249b02f13f97c379a83da7b7a6c68ba2c8320100cd973381c2b6e'), 'scripts/work-graph-c5-provider-inputs.py': ('test-support/r5-c5-hosted-profile-history/source481e/scripts/work-graph-c5-provider-inputs.py', '34699698d49f10c854b6f831bf38b856adb84791bf848e26fc105a1f1687a776'), 'scripts/work-graph-c5-executor.py': ('test-support/r5-c5-hosted-profile-history/source481e/scripts/work-graph-c5-executor.py', 'ac9a7ea7f364c235aa1192a715a4c33c712bcd249275eb8bdce7064702a4bf4d')})

# Exact qualifier-population repair successor. Historical tuples keep their
# original bytes; this source revision changes no image or execution policy.
R5_QUALIFIER_REPAIR_SOURCE_REVISION='R5_HOSTED_UBUNTU24_QUALIFIER_REPAIR_SOURCE_20261106_V2'
R5_QUALIFIER_REPAIR_PINS=types.MappingProxyType(dict(R5_HOSTED_PINS,
    **{QUALIFIER:'cff5376a90dbffdd18e762234c59b62285d8a26d35a916243a085bcf99c48b4c'}))

# Exact current continuity-receiver successor; historical selections remain fixed.
R5_CONTINUITY_RECEIVER_SOURCE_REVISION='R5_HOSTED_UBUNTU24_CONTINUITY_RECEIVER_SOURCE_20261106_V3'
R5_CONTINUITY_RECEIVER_PINS=types.MappingProxyType(dict(R5_QUALIFIER_REPAIR_PINS,
    **{COMPILER:'0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'}))

# Exact inner-capture owner successor; all earlier revision tuples stay fixed.
R5_INNER_CAPTURE_SOURCE_REVISION='R5_HOSTED_UBUNTU24_INNER_CAPTURE_SOURCE_20261107_V4'
R5_INNER_CAPTURE_PINS=types.MappingProxyType(dict(R5_CONTINUITY_RECEIVER_PINS,
    **{QUALIFIER:'79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'}))

# Prospective correction; all historical selections and pins stay fixed.
R5_TEMPLATE_POPULATION_SOURCE_REVISION='R5_HOSTED_UBUNTU24_TEMPLATE_POPULATION_SOURCE_20261110_V5'
R5_TEMPLATE_POPULATION_EXECUTION_SELECTION='fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-template-population-execution-profile.json'
R5_TEMPLATE_POPULATION_PINS=types.MappingProxyType({
    **{name:pin for name,pin in R5_INNER_CAPTURE_PINS.items() if name!=R5_HOSTED_EXECUTION_SELECTION},
    R5_TEMPLATE_POPULATION_EXECUTION_SELECTION:'96f64a192d0e91bda5d740d674c05329c5ef805ddf6cbe50b0fc6b87f30839fa'})


def validate_git_directory_selection_v1(selection):
    """Require a closed, internally consistent fixed clone-template inventory."""
    directories, files = selection['git_directories'], selection['git_files']
    if type(directories) is not dict or type(files) is not dict:
        raise ValueError('C5 clone template declaration is contradictory')
    for parent, names in directories.items():
        if (type(parent) is not str or not Path(parent).is_absolute()
                or '..' in Path(parent).parts or type(names) is not list
                or any(type(name) is not str for name in names)):
            raise ValueError('C5 clone template declaration is contradictory')
        children = [Path(child).name for child in (*directories, *files)
                    if Path(child).parent == Path(parent)]
        if names != sorted(set(children)) or len(children) != len(set(children)):
            raise ValueError('C5 clone template declaration is contradictory')


def _selection(profile,source_revision=None):
    if source_revision == R5_TEMPLATE_POPULATION_SOURCE_REVISION:
        if type(source_revision) is not str or type(profile) is not str or profile != R5_HOSTED_PROFILE:
            raise ValueError('Template population successor requires the fixed R5 hosted profile')
        return R5_TEMPLATE_POPULATION_PINS,R5_HOSTED_BASE_SELECTION,R5_HOSTED_PROVIDER_SELECTION,R5_TEMPLATE_POPULATION_EXECUTION_SELECTION,R5_HOSTED_ORIGINS
    if source_revision == R5_INNER_CAPTURE_SOURCE_REVISION:
        if type(source_revision) is not str or type(profile) is not str or profile != R5_HOSTED_PROFILE:
            raise ValueError('Unknown fixed R5 inner-capture source profile')
        return R5_INNER_CAPTURE_PINS,R5_HOSTED_BASE_SELECTION,R5_HOSTED_PROVIDER_SELECTION,R5_HOSTED_EXECUTION_SELECTION,R5_HOSTED_ORIGINS
    if source_revision == R5_CONTINUITY_RECEIVER_SOURCE_REVISION:
        if type(source_revision) is not str or type(profile) is not str or profile != R5_HOSTED_PROFILE:
            raise ValueError('Unknown fixed R5 continuity-receiver source profile')
        return R5_CONTINUITY_RECEIVER_PINS,R5_HOSTED_BASE_SELECTION,R5_HOSTED_PROVIDER_SELECTION,R5_HOSTED_EXECUTION_SELECTION,R5_HOSTED_ORIGINS
    if source_revision == R5_QUALIFIER_REPAIR_SOURCE_REVISION:
        if type(source_revision) is not str or type(profile) is not str or profile != R5_HOSTED_PROFILE:
            raise ValueError('Unknown fixed R5 qualifier-repair source profile')
        return R5_QUALIFIER_REPAIR_PINS,R5_HOSTED_BASE_SELECTION,R5_HOSTED_PROVIDER_SELECTION,R5_HOSTED_EXECUTION_SELECTION,R5_HOSTED_ORIGINS
    if source_revision == R5_HOSTED_SOURCE_REVISION:
        if type(profile) is not str or profile != R5_HOSTED_PROFILE:
            raise ValueError('Unknown fixed R5 hosted C5 source profile')
        return R5_HOSTED_PINS,R5_HOSTED_BASE_SELECTION,R5_HOSTED_PROVIDER_SELECTION,R5_HOSTED_EXECUTION_SELECTION,R5_HOSTED_ORIGINS
    if source_revision == R5_WINDOWS_CAPTURE_SOURCE_REVISION:
        if type(profile) is not str or profile != R4_BUILD_CACHE_PROFILE:
            raise ValueError('Unknown fixed R5 Windows capture source profile')
        _,base,provider,execution,origins=_selection(profile,R4_BUILD_CACHE_SOURCE_REVISION)
        return R5_WINDOWS_CAPTURE_PINS,base,provider,execution,origins
    if source_revision == R5_WINDOWS_INITIALIZATION_SOURCE_REVISION:
        if type(profile) is not str or profile != R4_BUILD_CACHE_PROFILE:
            raise ValueError('Unknown fixed R5 Windows initialization source profile')
        _,base,provider,execution,origins=_selection(profile,R4_BUILD_CACHE_SOURCE_REVISION)
        return R5_WINDOWS_INITIALIZATION_PINS,base,provider,execution,origins
    if source_revision == R4_INITIALIZATION_SOURCE_REVISION:
        if type(profile) is not str or profile != R4_BUILD_CACHE_PROFILE:
            raise ValueError('Unknown fixed R4 initialization source profile')
        _,base,provider,execution,origins=_selection(profile,R4_BUILD_CACHE_SOURCE_REVISION)
        return R4_INITIALIZATION_PINS,base,provider,execution,origins
    if source_revision == R4_BUILD_CACHE_SOURCE_REVISION:
        if type(profile) is not str or profile != R4_BUILD_CACHE_PROFILE:
            raise ValueError('Unknown fixed R4 build-local compression C5 profile')
        return R4_BUILD_CACHE_PINS,R4_BUILD_CACHE_BASE_SELECTION,R4_PROVIDER_SELECTION,R4_BUILD_CACHE_EXECUTION_SELECTION,R4_BUILD_CACHE_ORIGINS
    if source_revision == R4_PREFIX_RESULT_SOURCE_REVISION:
        if type(profile) is not str or profile != R4_CORRESPONDENCE_PROFILE:
            raise ValueError('Unknown fixed R4 prefix-result C5 profile')
        return R4_PREFIX_RESULT_PINS,R4_BASE_SELECTION,R4_PROVIDER_SELECTION,R4_EXECUTION_SELECTION,R4_ORIGINS
    if source_revision == R4_COMPOSED_SOURCE_REVISION:
        if type(profile) is not str or profile not in R4_COMPOSED_PINS:
            raise ValueError('Unknown fixed R4 composed C5 profile')
        previous = R4_SOURCE_REVISION if profile == R4_CORRESPONDENCE_PROFILE else None
        _,base,provider,execution,origins=_selection(profile,previous)
        return R4_COMPOSED_PINS[profile],base,provider,execution,origins
    if profile == R4_CORRESPONDENCE_PROFILE:
        if source_revision == R4_COPY_MEMO_SOURCE_REVISION:
            return R4_COPY_MEMO_PINS,R4_BASE_SELECTION,R4_PROVIDER_SELECTION,R4_EXECUTION_SELECTION,R4_ORIGINS
        if source_revision == R4_MEMO_SOURCE_REVISION:
            return R4_MEMO_PINS,R4_BASE_SELECTION,R4_PROVIDER_SELECTION,R4_EXECUTION_SELECTION,R4_ORIGINS
        if source_revision != R4_SOURCE_REVISION:
            raise ValueError('Fresh R4 C5 requires its explicit closed source revision')
        return R4_PINS,R4_BASE_SELECTION,R4_PROVIDER_SELECTION,R4_EXECUTION_SELECTION,R4_ORIGINS
    if source_revision is not None:
        revisions={PUBLIC_STREAMING_SOURCE_REVISION:PUBLIC_STREAMING_PINS,
                   CURRENT105_SOURCE_REVISION:CURRENT105_PINS,
                   CURRENT105_COMPOSED_SOURCE_REVISION:CURRENT105_COMPOSED_PINS}
        if (type(source_revision) is not str or type(profile) is not str
                or source_revision not in revisions or profile not in revisions[source_revision]):
            raise ValueError('Unknown fixed C5 source revision')
        _,base,provider,execution,origins=_selection(profile)
        return revisions[source_revision][profile],base,provider,execution,origins
    if type(profile) is str and profile == PROFILE:
        return PINS, BASE_SELECTION, PROVIDER_SELECTION, EXECUTION_SELECTION, ORIGINS
    if type(profile) is str and profile == CURRENT_PROFILE:
        return CURRENT_PINS, CURRENT_BASE_SELECTION, CURRENT_PROVIDER_SELECTION, CURRENT_EXECUTION_SELECTION, CURRENT_ORIGINS
    if type(profile) is str and profile == TASK_PROFILE:
        return TASK_PINS, TASK_BASE_SELECTION, TASK_PROVIDER_SELECTION, TASK_EXECUTION_SELECTION, TASK_ORIGINS
    if type(profile) is str and profile == CORRESPONDENCE_PROFILE:
        return CORRESPONDENCE_PINS, CORRESPONDENCE_BASE_SELECTION, TASK_PROVIDER_SELECTION, CORRESPONDENCE_EXECUTION_SELECTION, CORRESPONDENCE_ORIGINS
    raise ValueError('Unknown fixed C5 execution profile')


def _identity(info):
    return (str(info.st_dev),str(info.st_ino),info.st_mode,info.st_nlink,
            info.st_size,info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)


def _anchor(info):
    return (str(info.st_dev),str(info.st_ino),info.st_mode,info.st_uid,info.st_gid)


def _read(name, profile=PROFILE,source_revision=None):
    pins, *_ = _selection(profile,source_revision)
    if name not in pins and name!=LOADER:raise ValueError('Unknown fixed C5 execution member')
    physical = name
    if profile == R4_CORRESPONDENCE_PROFILE and name == GATE:
        if source_revision == R4_SOURCE_REVISION:
            physical = R4_ORIGINAL_GATE_MEMBER
        elif source_revision == R4_MEMO_SOURCE_REVISION:
            physical = R4_PREFIX_GATE_MEMBER
    if name == GATE and (source_revision == R4_COMPOSED_SOURCE_REVISION
                         or (profile == R4_CORRESPONDENCE_PROFILE and source_revision == R4_COPY_MEMO_SOURCE_REVISION)):
        physical = R4_COPY_GATE_MEMBER
    historical = R4_BUILD_CACHE_PHYSICAL_HISTORY.get(name)
    if historical is not None and pins.get(name) == historical[1]:
        physical = historical[0]
    retained = R4_INITIALIZATION_PHYSICAL_HISTORY.get(name)
    if retained is not None and pins.get(name) == retained[1]:
        physical = retained[0]
    retained = R5_WINDOWS_INITIALIZATION_PHYSICAL_HISTORY.get(name)
    if retained is not None and pins.get(name) == retained[1]:
        physical = retained[0]
    retained = R5_WINDOWS_CAPTURE_PHYSICAL_HISTORY.get(name)
    if retained is not None and pins.get(name) == retained[1]:
        physical = retained[0]
    retained = R5_HOSTED_PHYSICAL_HISTORY.get(name)
    if retained is not None and pins.get(name) == retained[1]:
        physical = retained[0]
    path=ROOT/physical
    if not path.is_absolute() or '..' in path.parts:raise ValueError('C5 execution source alias is unsupported')
    directory=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    current=Path('/')
    ancestors={str(current):_anchor(os.fstat(directory))}
    fd=None
    try:
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory)
            os.close(directory);directory=child;current/=part
            ancestors[str(current)]=_anchor(os.fstat(directory))
        before=os.stat(path.name,dir_fd=directory,follow_symlinks=False)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink!=1
                or stat.S_IMODE(before.st_mode) not in (0o644,0o755) or not 0<before.st_size<=MAX_SOURCE_BYTES):
            raise ValueError('C5 execution source must be a bounded ordinary single-link file')
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
        if _identity(os.fstat(fd))!=_identity(before) or os.listxattr(fd):
            raise ValueError('C5 executing source changed or has unsupported extended metadata')
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(MAX_SOURCE_BYTES+1)
        if (len(raw)!=before.st_size or _identity(os.fstat(fd))!=_identity(before)
                or _identity(os.stat(path.name,dir_fd=directory,follow_symlinks=False))!=_identity(before)):
            raise ValueError('C5 execution source changed during capture')
        return raw,_identity(before),ancestors
    finally:
        if fd is not None:os.close(fd)
        os.close(directory)


class _Engine:
    def __init__(self, profile=PROFILE,*,source_revision=None):
        self.pins,self.base_selection,self.provider_selection,self.execution_selection,self.origins=_selection(profile,source_revision)
        self.profile=profile
        self.source_revision=source_revision
        sources={};ancestors={}
        for name in (LOADER,*self.pins):
            raw,identity,observed=_read(name,self.profile,self.source_revision)
            if name in self.pins and hashlib.sha256(raw).hexdigest()!=self.pins[name]:
                raise ValueError('Unsupported fixed C5 execution member: '+name)
            for directory,value in observed.items():
                if directory in ancestors and ancestors[directory]!=value:
                    raise ValueError('C5 execution source ancestor changed during capture')
                ancestors[directory]=value
            sources[name]=(raw,identity)
        self.sources=types.MappingProxyType(sources)
        self.ancestors=types.MappingProxyType(ancestors)
        self.check()

    def check(self):
        for name,expected in self.sources.items():
            raw,identity,ancestors=_read(name,self.profile,self.source_revision)
            if (raw,identity)!=expected or any(self.ancestors[name]!=value for name,value in ancestors.items()):
                raise ValueError('Captured C5 execution source or ancestor is no longer current')

    def load(self):
        selection=json.loads(self.sources[self.execution_selection][0])
        if (selection.get('schema')!='implementaudit.c5-execution-selection.v1'
                or selection.get('profile')!=self.profile or selection.get('selection_origins')!=dict(self.origins)
                or selection.get('original_argv')!=['bash','tests/reproducible-release-asset.test.sh']):
            raise ValueError('Unsupported fixed C5 execution selection')
        if self.source_revision == R5_TEMPLATE_POPULATION_SOURCE_REVISION:
            validate_git_directory_selection_v1(selection)
        # The unchanged data reader names its historical logical fixture key.
        # This explicit map binds that key to the separately captured execution
        # selection. The old physical selection/default loader remain untouched.
        base_sources=dict(self.sources)
        base_sources[self.origins['base_logical_key']]=self.sources[self.base_selection]
        base_sources=types.MappingProxyType(base_sources)
        provider_sources=dict(self.sources)
        provider_sources[PROVIDER_SELECTION]=self.sources[self.provider_selection]
        provider_sources=types.MappingProxyType(provider_sources)
        modules={}
        for name in (PREFIX,BASE,PROVIDER,QUALIFIER,EVENT,COMPLETION,GATE,EXECUTOR):
            self.check()
            module=types.ModuleType('_fixed_genuine_c5_'+Path(name).stem.replace('-','_'))
            module.__file__=str(ROOT/name);module.__package__=''
            if name==BASE:
                module._R0035_C5_INPUT_CAPTURE=dict(prefix=modules[PREFIX],sources=base_sources,check=self.check)
            elif name==PROVIDER:
                module._R0035_C5_PROVIDER_CAPTURE=dict(prefix=modules[PREFIX],base=modules[BASE],sources=provider_sources,check=self.check)
            elif name==QUALIFIER:
                module._R0035_EFFECT_SOURCE_CAPTURE=dict(driver=self.sources[QUALIFIER][0],compiler=self.sources[COMPILER][0],
                    expected_compiler_sha256=self.pins[COMPILER])
            elif name==GATE:
                module._R0035_C5_LIVE_GATE_CAPTURE=dict(capture=modules[EVENT],completion=modules[COMPLETION],
                    compiler_sha256=self.pins[COMPILER],check=self.check)
            elif name==EXECUTOR:
                module._R0035_C5_EXECUTOR_CAPTURE=dict(prefix=modules[PREFIX],base=modules[BASE],provider=modules[PROVIDER],
                    gate=modules[GATE],qualifier=modules[QUALIFIER],sources=self.sources,check=self.check,
                    root=str(ROOT),selection=selection)
            try:exec(compile(self.sources[name][0],module.__file__,'exec'),module.__dict__)
            finally:self.check()
            modules[name]=module
        return modules[EXECUTOR]


def create_genuine_c5_session(source_root,output,*,expected_source):
    """Create one fixed local execution owner, never import a prior result.

    expected_source is exact post-commit comparison data from the separately
    reviewed outer envelope. The executor binds it to captured Git bytes and
    actual INIT/clone observations; it cannot grant execution or native authority.
    """
    return _Engine().load().GenuineC5Session(source_root,output,expected_source=expected_source)


def create_current_composite_c5_session_v1(source_root,output,*,expected_source):
    """Select the one current source/provider profile; execution needs its actual inputs.

    This explicit entry preserves the original default. The fixed public provider
    path and exact bytes must exist; selection supplies no execution authority.
    """
    return _Engine(CURRENT_PROFILE).load().GenuineC5Session(source_root,output,expected_source=expected_source)


def create_sol_task_c5_session_v1(source_root,output,*,expected_source):
    """Explicit closed task tuple; no native/root authority or old-scope promotion."""
    return _Engine(TASK_PROFILE).load().GenuineC5Session(source_root,output,expected_source=expected_source)


def create_correspondence_c5_session_v1(source_root,output,*,expected_source):
    """Exactly two fresh originals in one held image; no old-session replay."""
    return _Engine(CORRESPONDENCE_PROFILE).load().GenuineC5Session(source_root,output,expected_source=expected_source)


def create_public_streaming_source_current_composite_c5_session_v1(source_root,output,*,expected_source):
    """Public source tuple; unchanged current-composite runtime selection."""
    return _Engine(CURRENT_PROFILE,source_revision=PUBLIC_STREAMING_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_public_streaming_source_correspondence_c5_session_v1(source_root,output,*,expected_source):
    """Public source tuple; unchanged two-original correspondence policy."""
    return _Engine(CORRESPONDENCE_PROFILE,source_revision=PUBLIC_STREAMING_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_current105_source_current_composite_c5_session_v1(source_root,output,*,expected_source):
    """Exact current105 source integration; unchanged current-composite runtime."""
    return _Engine(CURRENT_PROFILE,source_revision=CURRENT105_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_current105_source_correspondence_c5_session_v1(source_root,output,*,expected_source):
    """Exact current105 source integration; unchanged two-original policy."""
    return _Engine(CORRESPONDENCE_PROFILE,source_revision=CURRENT105_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_current105_composed_source_current_composite_c5_session_v2(source_root,output,*,expected_source):
    """Exact composed compiler successor; unchanged current-composite runtime."""
    return _Engine(CURRENT_PROFILE,source_revision=CURRENT105_COMPOSED_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_current105_composed_source_correspondence_c5_session_v2(source_root,output,*,expected_source):
    """Exact composed compiler successor; unchanged two-original policy."""
    return _Engine(CORRESPONDENCE_PROFILE,source_revision=CURRENT105_COMPOSED_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_current_host_correspondence_c5_session_v1(source_root,output,*,expected_source):
    """Fresh real provider/current-host pair; unchanged120s whole-pair bound."""
    return _Engine(R4_CORRESPONDENCE_PROFILE,source_revision=R4_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_guarded_prefix_correspondence_c5_session_v2(source_root,output,*,expected_source):
    """Explicit guarded-prefix successor; no old tuple or deadline is changed."""
    return _Engine(R4_CORRESPONDENCE_PROFILE,source_revision=R4_MEMO_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_guarded_source_copy_correspondence_c5_session_v3(source_root,output,*,expected_source):
    """Explicit guarded copy-proof successor; unchanged complete final receiving."""
    return _Engine(R4_CORRESPONDENCE_PROFILE,source_revision=R4_COPY_MEMO_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_composed_source_current_c5_session_v4(source_root,output,*,expected_source):
    """Exact R4 composed source; existing execution/runtime bounds unchanged."""
    return _Engine(CURRENT_PROFILE,source_revision=R4_COMPOSED_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_composed_source_correspondence_c5_session_v4(source_root,output,*,expected_source):
    """Exact R4 composed source; existing execution/runtime bounds unchanged."""
    return _Engine(CORRESPONDENCE_PROFILE,source_revision=R4_COMPOSED_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_composed_source_owned_correspondence_c5_session_v4(source_root,output,*,expected_source):
    """Exact R4 composed source; existing execution/runtime bounds unchanged."""
    return _Engine(R4_CORRESPONDENCE_PROFILE,source_revision=R4_COMPOSED_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_guarded_prefix_result_correspondence_c5_session_v5(source_root,output,*,expected_source):
    """Explicit identical-prefix proof reuse; all live byte/identity guards remain."""
    return _Engine(R4_CORRESPONDENCE_PROFILE,source_revision=R4_PREFIX_RESULT_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_build_local_compression_correspondence_c5_session_v6(source_root,output,*,expected_source):
    """Exact new package builder; original scripts and all execution limits unchanged."""
    return _Engine(R4_BUILD_CACHE_PROFILE,source_revision=R4_BUILD_CACHE_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r4_initialized_source_correspondence_c5_session_v1(source_root,output,*,expected_source):
    """Exact initialization-repaired source; original two-process limits remain unchanged."""
    return _Engine(R4_BUILD_CACHE_PROFILE,source_revision=R4_INITIALIZATION_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r5_windows_initialized_source_correspondence_c5_session_v1(source_root,output,*,expected_source):
    """Exact initialization-repaired source; original two-process limits remain unchanged."""
    return _Engine(R4_BUILD_CACHE_PROFILE,source_revision=R5_WINDOWS_INITIALIZATION_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r5_windows_capture_source_correspondence_c5_session_v1(source_root,output,*,expected_source):
    """Exact capture-repaired source; original two-process limits remain unchanged."""
    return _Engine(R4_BUILD_CACHE_PROFILE,source_revision=R5_WINDOWS_CAPTURE_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r5_hosted_ubuntu24_correspondence_c5_session_v1(source_root,output,*,expected_source):
    """Prospective exact linked runtime; whole-operation qualification remains separate.

    This selects no historical result and changes no old profile. The caller
    must own fresh hosted custody, preserve the selected producer watchdog,
    and measure the enclosing interval separately without relabeling it.
    """
    return _Engine(R5_HOSTED_PROFILE,source_revision=R5_HOSTED_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r5_hosted_ubuntu24_qualifier_repair_c5_session_v2(source_root,output,*,expected_source):
    """Select the exact repaired qualifier with unchanged hosted image limits.

    This is a new source tuple, not historical acceptance or live custody.
    Fresh complete operation and same-owner receiving remain mandatory.
    """
    return _Engine(R5_HOSTED_PROFILE,source_revision=R5_QUALIFIER_REPAIR_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r5_hosted_ubuntu24_continuity_receiver_c5_session_v3(source_root,output,*,expected_source):
    """Select the exact current receiver-bound compiler and repaired qualifier.

    Historical source tuples retain their own refusal behavior and evidence.
    Fresh operation, image and same-owner receiving remain required.
    """
    return _Engine(R5_HOSTED_PROFILE,source_revision=R5_CONTINUITY_RECEIVER_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)


def create_r5_hosted_ubuntu24_inner_capture_c5_session_v4(source_root,output,*,expected_source):
    """Select the exact inner-capture owner; earlier source revisions stay fixed.

    No image, resource, privilege, currentness or receiving guard changes.
    Fresh original operation and same-owner receiving remain required.
    """
    return _Engine(R5_HOSTED_PROFILE,source_revision=R5_INNER_CAPTURE_SOURCE_REVISION).load().GenuineC5Session(
        source_root,output,expected_source=expected_source)
