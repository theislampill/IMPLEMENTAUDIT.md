"""One exact successor-source relation to retained V21 evidence.

This admits no operation and never changes the subject of an authentic old
receipt. The independently issued Root record and current source bytes must
both match. All future native/runtime/placement checks remain live obligations.
"""
import hashlib,json,os,stat
from pathlib import Path

SCHEMA='dg16.fixed-runtime-successor-source-admission.v1'
SUBJECT={'commit': '540a12c1385fabc3170745103dd0ccb5ba8c9063', 'tree': '1839064374ba7a064a09db12123093a608596ecc'}
RETAINED_SUBJECT={'commit': '338c4c36d2ac95ca24345bc92fe8c53d66eaa15d', 'tree': '53498df783ed441744ae5080982c2d5e59c34bbc'}
RUNTIME_REVISION='R5_HOSTED_UBUNTU24_STAGE_B_CANONICAL02_RUNTIME_SOURCE_20261126_V22'
ADMISSION_NAME='SOURCE_SUCCESSOR_ADMISSION.json'
ADMISSION_PIN = {'bytes': 39767, 'sha256': '06f44093ea4eb5d2823a946f6b28aadce29661c380e3cf6b7f7e722b4f9f66a7'}
MANIFEST_PIN = {'bytes': 559828, 'sha256': 'a1144d6023ca1704e308f7d4b533cea573e06de75c9470b35bb3dcd556122418'}
NATIVE_POPULATION_SHA256='94a55590b2e4b7034c6f6b7be017546ba4830c5dde4651a7b72542162e5aa831'
PACKAGE_POPULATION_SHA256='adb80e893640052cf24598456662b61a799cc53011eb69a25843c7501cfef135'
RETAINED_EVIDENCE={'COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json': {'bytes': 7321, 'sha256': 'fd3a8bd27f85e0eb1ae18fe17bb570b9da8538e448c2bb3f47d14596ecece241'}, 'COMPOSITION_PLACEMENT_RECEIVING.json': {'bytes': 975, 'sha256': 'bca4cbdd26b69fa17a23ad990ade5ff3dfa36705de5a96cd6b656254dd2ded0e'}, 'PACKAGE_BODY_RECEIVING.json': {'bytes': 3571, 'sha256': '944adc3d9a456439b745aa59bc374ba15b033130dd01902e2343a48d2eb5610e'}, 'PACKAGE_ROOT_RECEIVING.json': {'bytes': 752, 'sha256': '515e1be7200a23e6e232023abab7f83e576a6baacdb46ad0e481d66dea5517b7'}, 'PACKAGE_TERMINAL_RECEIVING.json': {'bytes': 2280, 'sha256': '280faf0b8c6ed1fe21087766068e1b547faa3b504a6ce780a5ebb12ecea7cbcd'}, 'PLACEMENT_ARTIFACT_MANIFEST.json': {'bytes': 183, 'sha256': 'c39aed8ca08deadf4dfa88c6b24d53146d219fa0f5834b2e861f086c64b00ea1'}, 'PLACEMENT_DIAGNOSTIC.json': {'bytes': 25540, 'sha256': '29e56d55524d817c27691308f98a14ce799f5f5e4da7b654ca5ced1ac914872d'}, 'PLACEMENT_EVIDENCE_INDEX.json': {'bytes': 868, 'sha256': '23a43728d38dade3e53c8b82eb87de55ac242798acf0d2b9be9c84e7cd0ae477'}, 'PLACEMENT_INDEPENDENT_RECEIVING.json': {'bytes': 1453, 'sha256': 'e88128b3045e1da38da9c30f50e5cfde742cab1f10f3bd34e955eb4302a1952b'}, 'PLACEMENT_ROOT_RECEIVING.json': {'bytes': 1834, 'sha256': '332d472868d91b77ef56d91d834f72766e224f444a807b907b3de64869538456'}}
OBSERVATION_BASIS={'image': '20261116.133.1', 'observation': {'bytes': 64950, 'sha256': '7141d84be42994f87d96a5fb940a9e6633776ce64d7378d2df8f2e67f24984d6'}, 'run_attempt': 1, 'run_id': '45690722389'}
PLACEMENT={'allowed_ast_changes': ['SOURCE', 'TREE', 'CORE_FILES'], 'prospective': {'bytes': 16975, 'sha256': '4a5d730bde852f1ed2a147af3479f0621c51e08eb16ec1d4bc4ad2d61c7cdb3c'}, 'retained': {'bytes': 16933, 'sha256': '17d9e9df58943b8d56c360e574f02c5b827e05f26ab01c3daad31be46dc6b6b1'}}
MAX_BODY=65536


def need(value,code):
    if not value:raise ValueError(code)


def encode(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def pin(raw):return dict(bytes=len(raw),sha256=sha(raw))
def stamp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid)


def read_ordinary(path,limit):
    path=Path(path);before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=limit,'SOURCE_RECORD_FILE')
    for parent in path.parents:need(not parent.is_symlink(),'SOURCE_RECORD_ANCESTOR')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'SOURCE_RECORD_CHANGED')
        raw=os.pread(fd,limit+1,0)
        need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before)
             and stamp(path.lstat())==stamp(before),'SOURCE_RECORD_CHANGED')
        return raw,stamp(before)
    finally:os.close(fd)


def parse(raw):
    def pairs(rows):
        value={}
        for key,item in rows:need(key not in value,'SOURCE_RECORD_DUPLICATE');value[key]=item
        return value
    return json.loads(raw.decode('utf8'),object_pairs_hook=pairs,
                      parse_constant=lambda _:need(False,'SOURCE_RECORD_NONFINITE'))


def validate(value,manifest):
    need(type(value) is dict and set(value)=={'schema','state','issuer','decision','subject','retained_subject',
        'source_manifest','source_files','source_bytes','runtime_source_revision','observation_basis','native_members',
        'package_dependencies','retained_evidence','placement_module','scope','historical_job_ran_successor_source',
        'complete_runtime_qualification','native_qualification','placement_on_future_job','original_awards','operation_grants'},
        'SOURCE_ADMISSION_FIELDS')
    need(value['state']=='ADMITTED_PROSPECTIVELY' and value['issuer']=='R5_ROOT_GOVERNOR'
         and value['decision']=='ADMIT_EXACT_RUNTIME_SUCCESSOR_SOURCE_RELATION','SOURCE_ADMISSION_HELD')
    need(value['schema']==SCHEMA and value['subject']==SUBJECT and value['retained_subject']==RETAINED_SUBJECT
         and value['source_manifest']==MANIFEST_PIN and value['runtime_source_revision']==RUNTIME_REVISION,
         'SOURCE_ADMISSION_SUBJECT')
    need(value['scope']=='SOURCE_AND_RETAINED_EVIDENCE_RELATION_ONLY'
         and value['historical_job_ran_successor_source'] is False and value['complete_runtime_qualification'] is False
         and value['native_qualification'] is False and value['placement_on_future_job']=='MUST_RECHECK_ACTUAL_SAME_JOB'
         and value['original_awards']==[] and value['operation_grants']==[],'SOURCE_ADMISSION_SCOPE')
    need(value['observation_basis']==OBSERVATION_BASIS and value['placement_module']==PLACEMENT
         and value['retained_evidence']==RETAINED_EVIDENCE,'SOURCE_ADMISSION_BASIS')
    need(type(manifest) is dict and manifest.get('commit')==SUBJECT['commit'] and manifest.get('tree')==SUBJECT['tree']
         and manifest.get('file_count')==value['source_files'] and manifest.get('total_bytes')==value['source_bytes'],
         'SOURCE_MANIFEST_SUBJECT')
    members=manifest.get('members');need(type(members) is list and len(members)==value['source_files'],'SOURCE_MANIFEST_POPULATION')
    by_path={row['path']:row for row in members}
    need(len(by_path)==len(members) and sum(row['bytes'] for row in members)==value['source_bytes'],'SOURCE_MANIFEST_POPULATION')
    for key,count,digest in (('native_members',89,NATIVE_POPULATION_SHA256),('package_dependencies',79,PACKAGE_POPULATION_SHA256)):
        rows=value[key]
        need(type(rows) is list and len(rows)==count and sha(encode(rows))==digest,'SOURCE_RELEVANT_POPULATION')
        names=[row['path'] for row in rows]
        need(names==sorted(set(names)) and all(by_path.get(row['path'])==row for row in rows),'SOURCE_RELEVANT_MEMBER')
    return value


def verify_current(value,source):
    source=Path(source);need(source.is_dir() and source.absolute()==source.resolve(strict=True),'SOURCE_CURRENT_ROOT')
    rows={row['path']:row for row in value['native_members']+value['package_dependencies']}
    held={}
    for name,row in sorted(rows.items()):
        path=source/name;raw,identity=read_ordinary(path,128*1024**2)
        need(pin(raw)==dict(bytes=row['bytes'],sha256=row['sha256'])
             and stat.S_IMODE(identity[2])==(0o755 if row['mode']=='100755' else 0o644),'SOURCE_CURRENT_MEMBER')
        held[name]=(pin(raw),identity)
    for name,opening in sorted(held.items()):
        raw,identity=read_ordinary(source/name,128*1024**2)
        need((pin(raw),identity)==opening,'SOURCE_CURRENT_CLOSING')


def receive(packet,*,source=None):
    packet=Path(packet);record_path=packet/'public-inputs'/ADMISSION_NAME
    raw,identity=read_ordinary(record_path,MAX_BODY)
    need(pin(raw)==ADMISSION_PIN,'SOURCE_ADMISSION_PIN')
    manifest_raw,manifest_identity=read_ordinary(packet/'SOURCE_MANIFEST.json',1024*1024)
    need(pin(manifest_raw)==MANIFEST_PIN,'SOURCE_MANIFEST_PIN')
    value=validate(parse(raw),parse(manifest_raw))
    held={}
    for name,expected in sorted(RETAINED_EVIDENCE.items()):
        body,mark=read_ordinary(packet/'public-inputs'/name,MAX_BODY)
        need(pin(body)==expected,'SOURCE_RETAINED_EVIDENCE');held[name]=(body,mark)
    if source is not None:verify_current(value,source)
    for name,opening in sorted(held.items()):
        need(read_ordinary(packet/'public-inputs'/name,MAX_BODY)==opening,'SOURCE_RETAINED_CLOSING')
    need(read_ordinary(record_path,MAX_BODY)==(raw,identity)
         and read_ordinary(packet/'SOURCE_MANIFEST.json',1024*1024)==(manifest_raw,manifest_identity),'SOURCE_ADMISSION_CLOSING')
    return value
