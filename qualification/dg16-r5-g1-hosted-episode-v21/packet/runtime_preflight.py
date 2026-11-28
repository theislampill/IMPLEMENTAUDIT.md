"""Read-only selection and comparison of one prospectively admitted whole runtime profile.

No provider setup, native command, pair, automatic pin adoption or retry lives
here. Full maintained acquisition still owns complete runtime qualification.
"""
import hashlib
import json
import re

SCHEMA='dg16.early-fixed-runtime-selectors.v1'
REVISION='R5_HOSTED_UBUNTU24_STAGE_B_IMAGE23_CACHE02_ENTROPY_RUNTIME_SOURCE_20261128_V27'
PROFILE_DEFINITIONS = {'R5_HOSTED_UBUNTU24_STAGE_B_IMAGE23_CACHE02_ENTROPY_RUNTIME_SOURCE_20261128_V27': {'executing_source_bindings': {'fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-stage-b-runtime-canonical02-python312.json': {'bytes': 8310, 'sha256': 'f21789841d1e46d27e0779d8de6a829480d5de8e8e5c640e92da20831add1097'}, 'fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-stage-b-runtime-image23-cache02-execution-profile.json': {'bytes': 10256, 'sha256': '74aae3fff5c7b9d13ba68b2aa93d6dc92f9007d2bed32d13b6e5355bf91a41f9'}, 'fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-image23-cache02-python312.json': {'bytes': 9783, 'sha256': '554a286646d6d0c349754404a85e78cda4cf441520673ad0ddb28b6a26452271'}, 'scripts/load-work-graph-c5-executor.py': {'bytes': 89216, 'sha256': '2f1d8c19be85a03ffeb0884db697e6630d0e4be7f712da39b4186ee1902c2743'}, 'scripts/qualify-work-graph-finite-leaf.py': {'bytes': 290144, 'sha256': 'f5a1d7559686bff9cb0ffe706051b99a24f2de1d0cf873e1f774456773645305'}, 'scripts/qualify-work-graph-prefix.py': {'bytes': 54950, 'sha256': '9390df7ae1f02ca467fa6c5696c6df69ed452a99e999616d575c62e1fc19b0a4'}, 'scripts/qualify-work-graph-verifier.py': {'bytes': 279440, 'sha256': 'b5a3fb17b1be72ead4168d965403d93a1127c2367a7c54876cc89bebe6c760e0'}, 'scripts/repro-event-capture.py': {'bytes': 87416, 'sha256': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08'}, 'scripts/verify-package.sh': {'bytes': 44184, 'sha256': 'ea132140d64d2714f5a54356c4b79cd05dd2b32017c38cd2307115adc7ec6978'}, 'scripts/work-graph-c5-executor.py': {'bytes': 108209, 'sha256': '2ea74c9efc58c014cd260eb76d22264457d421ba51959fc77a8f718f165ea846'}, 'scripts/work-graph-c5-inputs.py': {'bytes': 21275, 'sha256': '2befafe8c933467bd6dffbe2d4d27b09b4d6e3b52cab3e1ce680ac061a49310a'}, 'scripts/work-graph-c5-live-gate.py': {'bytes': 40531, 'sha256': 'b252d0c1ac55e64caa9d8ed8b45402e0e8a6854227e4681b7ffe612eb5c7c3d5'}, 'scripts/work-graph-c5-provider-inputs.py': {'bytes': 24898, 'sha256': 'e6cb523c3ce2f59fcdb2a1ed90db75d987ca59456dc423d82aceeeaff01d594f'}, 'scripts/work-graph-completion.py': {'bytes': 29565, 'sha256': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb'}, 'skills/implementaudit/scripts/compile-work-graph.py': {'bytes': 261264, 'sha256': 'e65f13db74a29b4e8773997465361676d75a99de1c9fe0dca889e86353caece2'}}, 'execution_profile': {'bytes': 10256, 'path': 'fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-stage-b-runtime-image23-cache02-execution-profile.json', 'sha256': '74aae3fff5c7b9d13ba68b2aa93d6dc92f9007d2bed32d13b6e5355bf91a41f9'}, 'profile': 'FIXED_GENUINE_C5_SHARED_IMAGE_R5_HOSTED_UBUNTU24_SINGLE_COPY_20261105_V1', 'provider_fixture': {'bytes': 9783, 'path': 'fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-image23-cache02-python312.json', 'sha256': '554a286646d6d0c349754404a85e78cda4cf441520673ad0ddb28b6a26452271'}, 'runtime_expected': {'/etc/ld.so.cache': {'bytes': 38396, 'link': None, 'mode': 420, 'resolved': '/etc/ld.so.cache', 'sha256': 'e70987876889374de327e050a0fa554e5db6110271af39d19c84c1d4ce5e1f0b'}, '/lib/x86_64-linux-gnu/libc.so.6': {'bytes': 2129424, 'link': None, 'mode': 493, 'resolved': '/usr/lib/x86_64-linux-gnu/libc.so.6', 'sha256': '755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a'}, '/lib/x86_64-linux-gnu/libgcc_s.so.1': {'bytes': 183024, 'link': None, 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libgcc_s.so.1', 'sha256': 'd93224d2b0dab4247598be683adca02f5cf00586f99c187579cd7e92058fb7cb'}, '/lib/x86_64-linux-gnu/libpthread.so.0': {'bytes': 14408, 'link': None, 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libpthread.so.0', 'sha256': 'cd34f895c9d2aa669d5d2654bed6b71210fc9003c3a1e96bb5311a40feb86039'}, '/lib/x86_64-linux-gnu/libstdc++.so.6': {'bytes': 2592224, 'link': 'libstdc++.so.6.0.33', 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.33', 'sha256': '1fd75fe70354a416d75aef22bcae68c47bd25d20e2d0568c30b1a9838cf62f11'}, '/lib64/ld-linux-x86-64.so.2': {'bytes': 236616, 'link': '../lib/x86_64-linux-gnu/ld-linux-x86-64.so.2', 'mode': 493, 'resolved': '/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2', 'sha256': '5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f'}, '/usr/bin/python3.12': {'bytes': 8020928, 'link': None, 'mode': 493, 'resolved': '/usr/bin/python3.12', 'sha256': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'}, '/usr/lib/python3.12/_sysconfigdata__linux_x86_64-linux-gnu.py': {'bytes': 49505, 'link': '_sysconfigdata__x86_64-linux-gnu.py', 'mode': 420, 'resolved': '/usr/lib/python3.12/_sysconfigdata__x86_64-linux-gnu.py', 'sha256': 'ee5bb5493fa4575f7788e1b0e8a067b9c463f9705dcb36f5eb571d1c0812ea82'}, '/usr/lib/python3.12/posixpath.py': {'bytes': 17623, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/posixpath.py', 'sha256': 'c443d7b8afad1717e7060ce49b3e04423058de56cd4246ee6bcc1ac962eb5c2b'}, '/usr/lib/python3.12/site.py': {'bytes': 23903, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/site.py', 'sha256': '619436355cbe91c3b29681ab486ee63f5f2e0a7d6274dfae747bdb94e60bca55'}, '/usr/lib/python3.12/sitecustomize.py': {'bytes': 155, 'link': '/etc/python3.12/sitecustomize.py', 'mode': 420, 'resolved': '/etc/python3.12/sitecustomize.py', 'sha256': '43d81125d92376b1a69d53a71126a041cc9a18d8080e92dea0a2ae23be138b1e'}, '/usr/lib/python3.12/sysconfig.py': {'bytes': 32768, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/sysconfig.py', 'sha256': 'e21755a918f488db1bd21d23120ee36ad09382c553b79735a121ee1fbdbcc08d'}}, 'source_revision': 'R5_HOSTED_UBUNTU24_STAGE_B_IMAGE23_CACHE02_ENTROPY_RUNTIME_SOURCE_20261128_V27'}, 'R5_HOSTED_UBUNTU24_STAGE_B_IMAGE23_ENTROPY_RUNTIME_SOURCE_20261128_V26': {'executing_source_bindings': {'fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-stage-b-runtime-canonical02-python312.json': {'bytes': 8310, 'sha256': 'f21789841d1e46d27e0779d8de6a829480d5de8e8e5c640e92da20831add1097'}, 'fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-stage-b-runtime-image23-execution-profile.json': {'bytes': 9751, 'sha256': 'fc41180a291cdaac01cdd0827b27bb4113593adcc0a3711e0cf10b808852ef57'}, 'fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-image23-python312.json': {'bytes': 9783, 'sha256': '76c3dd9b867ec273d67b43c0e5b5de48dec21a0a8ba9dc8758f1e9978fbe568f'}, 'scripts/load-work-graph-c5-executor.py': {'bytes': 89216, 'sha256': '2f1d8c19be85a03ffeb0884db697e6630d0e4be7f712da39b4186ee1902c2743'}, 'scripts/qualify-work-graph-finite-leaf.py': {'bytes': 290144, 'sha256': 'f5a1d7559686bff9cb0ffe706051b99a24f2de1d0cf873e1f774456773645305'}, 'scripts/qualify-work-graph-prefix.py': {'bytes': 54950, 'sha256': '9390df7ae1f02ca467fa6c5696c6df69ed452a99e999616d575c62e1fc19b0a4'}, 'scripts/qualify-work-graph-verifier.py': {'bytes': 279440, 'sha256': 'b5a3fb17b1be72ead4168d965403d93a1127c2367a7c54876cc89bebe6c760e0'}, 'scripts/repro-event-capture.py': {'bytes': 87416, 'sha256': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08'}, 'scripts/verify-package.sh': {'bytes': 44184, 'sha256': 'ea132140d64d2714f5a54356c4b79cd05dd2b32017c38cd2307115adc7ec6978'}, 'scripts/work-graph-c5-executor.py': {'bytes': 108209, 'sha256': '2ea74c9efc58c014cd260eb76d22264457d421ba51959fc77a8f718f165ea846'}, 'scripts/work-graph-c5-inputs.py': {'bytes': 21275, 'sha256': '2befafe8c933467bd6dffbe2d4d27b09b4d6e3b52cab3e1ce680ac061a49310a'}, 'scripts/work-graph-c5-live-gate.py': {'bytes': 40531, 'sha256': 'b252d0c1ac55e64caa9d8ed8b45402e0e8a6854227e4681b7ffe612eb5c7c3d5'}, 'scripts/work-graph-c5-provider-inputs.py': {'bytes': 24898, 'sha256': 'e6cb523c3ce2f59fcdb2a1ed90db75d987ca59456dc423d82aceeeaff01d594f'}, 'scripts/work-graph-completion.py': {'bytes': 29565, 'sha256': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb'}, 'skills/implementaudit/scripts/compile-work-graph.py': {'bytes': 261264, 'sha256': 'e65f13db74a29b4e8773997465361676d75a99de1c9fe0dca889e86353caece2'}}, 'execution_profile': {'bytes': 9751, 'path': 'fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-stage-b-runtime-image23-execution-profile.json', 'sha256': 'fc41180a291cdaac01cdd0827b27bb4113593adcc0a3711e0cf10b808852ef57'}, 'profile': 'FIXED_GENUINE_C5_SHARED_IMAGE_R5_HOSTED_UBUNTU24_SINGLE_COPY_20261105_V1', 'provider_fixture': {'bytes': 9783, 'path': 'fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-image23-python312.json', 'sha256': '76c3dd9b867ec273d67b43c0e5b5de48dec21a0a8ba9dc8758f1e9978fbe568f'}, 'runtime_expected': {'/etc/ld.so.cache': {'bytes': 38836, 'link': None, 'mode': 420, 'resolved': '/etc/ld.so.cache', 'sha256': 'b6068d0301c8b1c9b1cde616fe33aff858dd3fe4bd72ebf0d196a4b7be9312d3'}, '/lib/x86_64-linux-gnu/libc.so.6': {'bytes': 2129424, 'link': None, 'mode': 493, 'resolved': '/usr/lib/x86_64-linux-gnu/libc.so.6', 'sha256': '755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a'}, '/lib/x86_64-linux-gnu/libgcc_s.so.1': {'bytes': 183024, 'link': None, 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libgcc_s.so.1', 'sha256': 'd93224d2b0dab4247598be683adca02f5cf00586f99c187579cd7e92058fb7cb'}, '/lib/x86_64-linux-gnu/libpthread.so.0': {'bytes': 14408, 'link': None, 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libpthread.so.0', 'sha256': 'cd34f895c9d2aa669d5d2654bed6b71210fc9003c3a1e96bb5311a40feb86039'}, '/lib/x86_64-linux-gnu/libstdc++.so.6': {'bytes': 2592224, 'link': 'libstdc++.so.6.0.33', 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.33', 'sha256': '1fd75fe70354a416d75aef22bcae68c47bd25d20e2d0568c30b1a9838cf62f11'}, '/lib64/ld-linux-x86-64.so.2': {'bytes': 236616, 'link': '../lib/x86_64-linux-gnu/ld-linux-x86-64.so.2', 'mode': 493, 'resolved': '/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2', 'sha256': '5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f'}, '/usr/bin/python3.12': {'bytes': 8020928, 'link': None, 'mode': 493, 'resolved': '/usr/bin/python3.12', 'sha256': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'}, '/usr/lib/python3.12/_sysconfigdata__linux_x86_64-linux-gnu.py': {'bytes': 49505, 'link': '_sysconfigdata__x86_64-linux-gnu.py', 'mode': 420, 'resolved': '/usr/lib/python3.12/_sysconfigdata__x86_64-linux-gnu.py', 'sha256': 'ee5bb5493fa4575f7788e1b0e8a067b9c463f9705dcb36f5eb571d1c0812ea82'}, '/usr/lib/python3.12/posixpath.py': {'bytes': 17623, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/posixpath.py', 'sha256': 'c443d7b8afad1717e7060ce49b3e04423058de56cd4246ee6bcc1ac962eb5c2b'}, '/usr/lib/python3.12/site.py': {'bytes': 23903, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/site.py', 'sha256': '619436355cbe91c3b29681ab486ee63f5f2e0a7d6274dfae747bdb94e60bca55'}, '/usr/lib/python3.12/sitecustomize.py': {'bytes': 155, 'link': '/etc/python3.12/sitecustomize.py', 'mode': 420, 'resolved': '/etc/python3.12/sitecustomize.py', 'sha256': '43d81125d92376b1a69d53a71126a041cc9a18d8080e92dea0a2ae23be138b1e'}, '/usr/lib/python3.12/sysconfig.py': {'bytes': 32768, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/sysconfig.py', 'sha256': 'e21755a918f488db1bd21d23120ee36ad09382c553b79735a121ee1fbdbcc08d'}}, 'source_revision': 'R5_HOSTED_UBUNTU24_STAGE_B_IMAGE23_ENTROPY_RUNTIME_SOURCE_20261128_V26'}}
EXPECTED = PROFILE_DEFINITIONS[REVISION]['runtime_expected']
NATIVE_PATHS = ('/lib/x86_64-linux-gnu/libgcc_s.so.1', '/lib/x86_64-linux-gnu/libpthread.so.0', '/lib/x86_64-linux-gnu/libstdc++.so.6')
BASE_PATHS = ('/lib/x86_64-linux-gnu/libc.so.6', '/lib64/ld-linux-x86-64.so.2', '/usr/bin/python3.12', '/usr/lib/python3.12/_sysconfigdata__linux_x86_64-linux-gnu.py', '/usr/lib/python3.12/posixpath.py', '/usr/lib/python3.12/site.py', '/usr/lib/python3.12/sitecustomize.py', '/usr/lib/python3.12/sysconfig.py')
FIELDS=('bytes','sha256','mode','resolved','link')
ROW_FIELDS={'kind',*FIELDS,'capture_sha256','error_class','error_sha256'}
MAX_FILE_BYTES=33554432
MAX_PUBLIC_BYTES=32768


def need(value, code):
    if not value:raise ValueError(code)


def encode(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def sha(raw):return hashlib.sha256(raw).hexdigest()


def valid_hash(value):return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None


def validate_row(row):
    need(type(row) is dict and set(row)==ROW_FIELDS,'RUNTIME_SELECTOR_ROW')
    need(row['kind'] in ('FILE','DIRECTORY','MISSING','REFUSED'),'RUNTIME_SELECTOR_KIND')
    need(valid_hash(row['capture_sha256']),'RUNTIME_CAPTURE_DIGEST')
    if row['kind']=='REFUSED':
        need(row['error_class'] in ('OS_ERROR','VALUE_ERROR') and valid_hash(row['error_sha256'])
             and all(row[k] is None for k in FIELDS),'RUNTIME_SELECTOR_ERROR')
        return
    need(row['error_class'] is None and row['error_sha256'] is None,'RUNTIME_SELECTOR_ERROR')
    if row['kind']=='MISSING':
        need(all(row[k] is None for k in FIELDS),'RUNTIME_SELECTOR_MISSING')
        return
    need(type(row['mode']) is int and 0<=row['mode']<=4095
         and type(row['resolved']) is str and row['resolved'].startswith('/')
         and len(row['resolved'])<=4096 and '\x00' not in row['resolved']
         and (row['link'] is None or type(row['link']) is str and 0<len(row['link'])<=4096 and '\x00' not in row['link']),
         'RUNTIME_SELECTOR_METADATA')
    if row['kind']=='FILE':
        need(type(row['bytes']) is int and 0<=row['bytes']<=MAX_FILE_BYTES
             and valid_hash(row['sha256']),'RUNTIME_SELECTOR_FILE')
    else:need(row['bytes'] is None and row['sha256'] is None,'RUNTIME_SELECTOR_DIRECTORY')


def identity(source_revision):
    need(type(source_revision) is str and source_revision in PROFILE_DEFINITIONS,'RUNTIME_PROFILE_REVISION')
    return dict(source_revision=source_revision,definition_sha256=sha(encode(PROFILE_DEFINITIONS[source_revision])))


def validate_identity(value):
    need(type(value) is dict and set(value)=={'source_revision','definition_sha256'},'RUNTIME_PROFILE_IDENTITY')
    expected=identity(value.get('source_revision'))
    need(value==expected,'RUNTIME_PROFILE_IDENTITY')
    return value['source_revision']


def selection(engine,runtime_profile):
    revision=validate_identity(runtime_profile);definition=PROFILE_DEFINITIONS[revision]
    expected=definition['runtime_expected']
    engine.CHECK()
    native=engine.D.SPEC.get('native_pins');startup=engine.D.SPEC.get('startup_pins');base=engine.B.SPEC.get('runtime_pins')
    need(type(native) is dict and set(native)==set(NATIVE_PATHS)
         and type(startup) is dict and set(startup)==set(expected)-set(NATIVE_PATHS)
         and type(base) is dict and set(base)==set(BASE_PATHS),'RUNTIME_SELECTOR_POPULATION')
    need({**native,**startup}==expected and base=={name:expected[name] for name in BASE_PATHS},
         'RUNTIME_SELECTOR_SOURCE_BINDING')
    need({name:dict(bytes=len(row[0]),sha256=sha(row[0])) for name,row in engine.SOURCES.items()}
         ==definition['executing_source_bindings'],'RUNTIME_PROFILE_SOURCE_BINDINGS')


def capture(base, name):
    """Keep exact five-field tuple plus a digest of all physical custody metadata."""
    try:
        # One selector at a time bounds temporary raw-body memory. Raw bodies are
        # discarded; the public projection contains only system-selector facts.
        actual=base.capture_selector(name,{},limit=MAX_FILE_BYTES)
        row=dict(kind=actual['kind'],**{key:actual.get(key) for key in FIELDS},
                 capture_sha256=sha(encode(actual)),error_class=None,error_sha256=None)
        validate_row(row)
        return row
    except (OSError,ValueError) as exc:
        raw=str(exc).encode('utf8')
        return dict(kind='REFUSED',**{key:None for key in FIELDS},
                    capture_sha256=sha(encode(dict(error_class=type(exc).__name__,error_sha256=sha(raw)))),
                    error_class='OS_ERROR' if isinstance(exc,OSError) else 'VALUE_ERROR',error_sha256=sha(raw))


def compare(opening,closing,*,source_revision,source_current=True,source_failure_sha256=None):
    validate_identity(identity(source_revision))
    expected=PROFILE_DEFINITIONS[source_revision]['runtime_expected']
    need(type(opening) is dict and type(closing) is dict
         and set(opening)==set(closing)==set(expected) and len(expected)==12,
         'RUNTIME_SELECTOR_POPULATION')
    need(type(source_current) is bool and ((source_current and source_failure_sha256 is None)
         or (not source_current and valid_hash(source_failure_sha256))),'RUNTIME_SOURCE_CURRENTNESS')
    rows=[]
    for name,pin in sorted(expected.items()):
        a,b=opening[name],closing[name];validate_row(a);validate_row(b)
        a_match=a['kind']=='FILE' and all(a[k]==pin[k] for k in FIELDS)
        b_match=b['kind']=='FILE' and all(b[k]==pin[k] for k in FIELDS)
        same=a==b
        rows.append(dict(path=name,expected=dict(pin),opening=a,closing=b,
                         opening_match=a_match,closing_match=b_match,bookends_equal=same,
                         match=a_match and b_match and same))
    value=dict(schema=SCHEMA,source_revision=source_revision,status='MATCH' if source_current and all(r['match'] for r in rows) else 'REFUSED',
               selector_count=12,source_current=source_current,source_failure_sha256=source_failure_sha256,
               selectors=rows,complete_runtime_qualification=False,automatic_adoption=False)
    need(len(encode(value))<=MAX_PUBLIC_BYTES,'RUNTIME_PUBLIC_BOUND')
    return value


def choose(opening,closing,*,source_current=True,source_failure_sha256=None):
    """Elect once from one full observation, never by individual-field alternatives."""
    comparisons={revision:compare(opening,closing,source_revision=revision,
        source_current=source_current,source_failure_sha256=source_failure_sha256)
        for revision in sorted(PROFILE_DEFINITIONS)}
    matches=[revision for revision,value in comparisons.items() if value['status']=='MATCH']
    chosen=matches[0] if len(matches)==1 else None
    # On refusal retain a named fixed-reference comparison, with no selected identity.
    value=comparisons[chosen if chosen is not None else REVISION]
    value['status']='MATCH' if chosen is not None else 'REFUSED'
    value['profile_selection']=dict(mode='INITIAL_WHOLE_PROFILE',
        status='SELECTED' if chosen is not None else 'NO_MATCH' if not matches else 'AMBIGUOUS',
        runtime_profile=identity(chosen) if chosen is not None else None,
        candidate_count=len(comparisons),matched_profile_count=len(matches),
        comparison_role='SELECTED_PROFILE' if chosen is not None else 'FIXED_REFERENCE_ONLY')
    need(len(encode(value))<=MAX_PUBLIC_BYTES,'RUNTIME_PUBLIC_BOUND')
    return value


def observe(engine,runtime_profile,*,initial=False):
    revision=validate_identity(runtime_profile)
    need(type(initial) is bool and (not initial or revision==REVISION),'RUNTIME_INITIAL_CAPTURE_OWNER')
    selection(engine,runtime_profile)
    names=PROFILE_DEFINITIONS[revision]['runtime_expected']
    opening={name:capture(engine.B,name) for name in sorted(names)}
    closing={name:capture(engine.B,name) for name in sorted(names)}
    current=True;failure=None
    try:engine.CHECK()
    except (OSError,ValueError) as exc:current=False;failure=sha(str(exc).encode('utf8'))
    if initial:return choose(opening,closing,source_current=current,source_failure_sha256=failure)
    value=compare(opening,closing,source_revision=revision,source_current=current,source_failure_sha256=failure)
    value['profile_selection']=dict(mode='FROZEN_WHOLE_PROFILE',status='FROZEN',
        runtime_profile=identity(revision),candidate_count=1,matched_profile_count=1 if value['status']=='MATCH' else 0,
        comparison_role='SELECTED_PROFILE')
    need(len(encode(value))<=MAX_PUBLIC_BYTES,'RUNTIME_PUBLIC_BOUND')
    return value


def public(value):
    """Recompute the exact selected comparison and closed election metadata."""
    if value is None:return None
    need(type(value) is dict and type(value.get('selectors')) is list
         and len(value['selectors'])==12,'RUNTIME_PUBLIC_PROJECTION')
    rows=value['selectors']
    need(all(type(row) is dict and set(row)=={'path','expected','opening','closing','opening_match',
         'closing_match','bookends_equal','match'} for row in rows),'RUNTIME_PUBLIC_PROJECTION')
    names=[row['path'] for row in rows]
    need(names==sorted(EXPECTED),'RUNTIME_SELECTOR_POPULATION')
    opening={row['path']:row['opening'] for row in rows};closing={row['path']:row['closing'] for row in rows}
    selected=value.get('profile_selection')
    need(type(selected) is dict and set(selected)=={'mode','status','runtime_profile','candidate_count',
         'matched_profile_count','comparison_role'},'RUNTIME_PROFILE_SELECTION')
    if selected['mode']=='INITIAL_WHOLE_PROFILE':
        rebuilt=choose(opening,closing,source_current=value.get('source_current'),
            source_failure_sha256=value.get('source_failure_sha256'))
    else:
        need(selected['mode']=='FROZEN_WHOLE_PROFILE','RUNTIME_PROFILE_SELECTION')
        revision=validate_identity(selected['runtime_profile'])
        rebuilt=compare(opening,closing,source_revision=revision,source_current=value.get('source_current'),
            source_failure_sha256=value.get('source_failure_sha256'))
        rebuilt['profile_selection']=dict(mode='FROZEN_WHOLE_PROFILE',status='FROZEN',
            runtime_profile=identity(revision),candidate_count=1,
            matched_profile_count=1 if rebuilt['status']=='MATCH' else 0,comparison_role='SELECTED_PROFILE')
    need(encode(value)==encode(rebuilt) and len(encode(rebuilt))<=MAX_PUBLIC_BYTES,'RUNTIME_PUBLIC_PROJECTION')
    return rebuilt
