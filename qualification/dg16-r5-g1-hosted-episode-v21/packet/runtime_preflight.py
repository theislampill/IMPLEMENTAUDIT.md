"""Read-only early comparison of one prospectively admitted finite runtime tuple.

No provider setup, native command, pair, automatic pin adoption or retry lives
here. Full maintained acquisition still owns complete runtime qualification.
"""
import hashlib
import json
import re

SCHEMA='dg16.early-fixed-runtime-selectors.v1'
REVISION='R5_HOSTED_UBUNTU24_STAGE_B_IMAGE23_CACHE02_RUNTIME_SOURCE_20261128_V25'
EXPECTED = {'/etc/ld.so.cache': {'bytes': 38396, 'link': None, 'mode': 420, 'resolved': '/etc/ld.so.cache', 'sha256': 'e70987876889374de327e050a0fa554e5db6110271af39d19c84c1d4ce5e1f0b'}, '/lib/x86_64-linux-gnu/libc.so.6': {'bytes': 2129424, 'link': None, 'mode': 493, 'resolved': '/usr/lib/x86_64-linux-gnu/libc.so.6', 'sha256': '755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a'}, '/lib/x86_64-linux-gnu/libgcc_s.so.1': {'bytes': 183024, 'link': None, 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libgcc_s.so.1', 'sha256': 'd93224d2b0dab4247598be683adca02f5cf00586f99c187579cd7e92058fb7cb'}, '/lib/x86_64-linux-gnu/libpthread.so.0': {'bytes': 14408, 'link': None, 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libpthread.so.0', 'sha256': 'cd34f895c9d2aa669d5d2654bed6b71210fc9003c3a1e96bb5311a40feb86039'}, '/lib/x86_64-linux-gnu/libstdc++.so.6': {'bytes': 2592224, 'link': 'libstdc++.so.6.0.33', 'mode': 420, 'resolved': '/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.33', 'sha256': '1fd75fe70354a416d75aef22bcae68c47bd25d20e2d0568c30b1a9838cf62f11'}, '/lib64/ld-linux-x86-64.so.2': {'bytes': 236616, 'link': '../lib/x86_64-linux-gnu/ld-linux-x86-64.so.2', 'mode': 493, 'resolved': '/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2', 'sha256': '5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f'}, '/usr/bin/python3.12': {'bytes': 8020928, 'link': None, 'mode': 493, 'resolved': '/usr/bin/python3.12', 'sha256': 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'}, '/usr/lib/python3.12/_sysconfigdata__linux_x86_64-linux-gnu.py': {'bytes': 49505, 'link': '_sysconfigdata__x86_64-linux-gnu.py', 'mode': 420, 'resolved': '/usr/lib/python3.12/_sysconfigdata__x86_64-linux-gnu.py', 'sha256': 'ee5bb5493fa4575f7788e1b0e8a067b9c463f9705dcb36f5eb571d1c0812ea82'}, '/usr/lib/python3.12/posixpath.py': {'bytes': 17623, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/posixpath.py', 'sha256': 'c443d7b8afad1717e7060ce49b3e04423058de56cd4246ee6bcc1ac962eb5c2b'}, '/usr/lib/python3.12/site.py': {'bytes': 23903, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/site.py', 'sha256': '619436355cbe91c3b29681ab486ee63f5f2e0a7d6274dfae747bdb94e60bca55'}, '/usr/lib/python3.12/sitecustomize.py': {'bytes': 155, 'link': '/etc/python3.12/sitecustomize.py', 'mode': 420, 'resolved': '/etc/python3.12/sitecustomize.py', 'sha256': '43d81125d92376b1a69d53a71126a041cc9a18d8080e92dea0a2ae23be138b1e'}, '/usr/lib/python3.12/sysconfig.py': {'bytes': 32768, 'link': None, 'mode': 420, 'resolved': '/usr/lib/python3.12/sysconfig.py', 'sha256': 'e21755a918f488db1bd21d23120ee36ad09382c553b79735a121ee1fbdbcc08d'}}
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


def selection(engine):
    """Refuse missing/extra source declarations, including overlapping base pins."""
    engine.CHECK()
    native=engine.D.SPEC['native_pins'];startup=engine.D.SPEC['startup_pins']
    base=engine.B.SPEC['runtime_pins']
    need(type(native) is dict and type(startup) is dict and type(base) is dict
         and set(native)==set(NATIVE_PATHS) and set(startup)==set(EXPECTED)-set(NATIVE_PATHS)
         and set(base)==set(BASE_PATHS),'RUNTIME_SELECTOR_POPULATION')
    need({**native,**startup}==EXPECTED and base=={name:EXPECTED[name] for name in BASE_PATHS},
         'RUNTIME_SELECTOR_SOURCE_BINDING')


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


def compare(opening, closing, *, source_current=True, source_failure_sha256=None):
    need(type(opening) is dict and type(closing) is dict
         and set(opening)==set(closing)==set(EXPECTED) and len(EXPECTED)==12,
         'RUNTIME_SELECTOR_POPULATION')
    need(type(source_current) is bool and ((source_current and source_failure_sha256 is None)
         or (not source_current and valid_hash(source_failure_sha256))),'RUNTIME_SOURCE_CURRENTNESS')
    rows=[]
    for name,pin in sorted(EXPECTED.items()):
        a,b=opening[name],closing[name];validate_row(a);validate_row(b)
        a_match=a['kind']=='FILE' and all(a[k]==pin[k] for k in FIELDS)
        b_match=b['kind']=='FILE' and all(b[k]==pin[k] for k in FIELDS)
        same=a==b
        rows.append(dict(path=name,expected=dict(pin),opening=a,closing=b,
                         opening_match=a_match,closing_match=b_match,bookends_equal=same,
                         match=a_match and b_match and same))
    value=dict(schema=SCHEMA,source_revision=REVISION,status='MATCH' if source_current and all(r['match'] for r in rows) else 'REFUSED',
               selector_count=12,source_current=source_current,source_failure_sha256=source_failure_sha256,
               selectors=rows,complete_runtime_qualification=False,automatic_adoption=False)
    need(len(encode(value))<=MAX_PUBLIC_BYTES,'RUNTIME_PUBLIC_BOUND')
    return value


def observe(engine):
    selection(engine)
    opening={name:capture(engine.B,name) for name in sorted(EXPECTED)}
    closing={name:capture(engine.B,name) for name in sorted(EXPECTED)}
    current=True;failure=None
    try:engine.CHECK()
    except (OSError,ValueError) as exc:current=False;failure=sha(str(exc).encode('utf8'))
    return compare(opening,closing,source_current=current,source_failure_sha256=failure)


def public(value):
    """Recompute every result flag before exposing a private state's projection."""
    if value is None:return None
    need(type(value) is dict and type(value.get('selectors')) is list
         and len(value['selectors'])==12,'RUNTIME_PUBLIC_PROJECTION')
    rows=value['selectors']
    need(all(type(row) is dict and set(row)=={'path','expected','opening','closing','opening_match',
         'closing_match','bookends_equal','match'} for row in rows),'RUNTIME_PUBLIC_PROJECTION')
    names=[row['path'] for row in rows]
    need(names==sorted(EXPECTED),'RUNTIME_SELECTOR_POPULATION')
    rebuilt=compare({row['path']:row['opening'] for row in rows},
                    {row['path']:row['closing'] for row in rows},
                    source_current=value.get('source_current'),source_failure_sha256=value.get('source_failure_sha256'))
    need(encode(value)==encode(rebuilt),'RUNTIME_PUBLIC_PROJECTION')
    return rebuilt
