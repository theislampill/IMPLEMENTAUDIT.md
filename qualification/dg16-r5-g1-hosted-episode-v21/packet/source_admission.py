"""One exact successor-source relation to retained V21 evidence.

This admits no operation and never changes the subject of an authentic old
receipt. The independently issued Root record and current source bytes must
both match. All future native/runtime/placement checks remain live obligations.
"""
import hashlib,json,os,stat
from pathlib import Path

SCHEMA='dg16.fixed-runtime-successor-source-admission.v1'
SUBJECT={'commit': 'd208cb84a9d69ad03709de6102f1adde3cf3df7f', 'tree': '8ba23825751d374c6e343485d9ff1a9e0401e75a'}
RETAINED_SUBJECT={'commit': '338c4c36d2ac95ca24345bc92fe8c53d66eaa15d', 'tree': '53498df783ed441744ae5080982c2d5e59c34bbc'}
RUNTIME_REVISION='R5_HOSTED_UBUNTU24_STAGE_B_IMAGE23_CACHE02_ENTROPY_RUNTIME_SOURCE_20261128_V27'
ADMISSION_NAME='SOURCE_SUCCESSOR_ADMISSION.json'
ADMISSION_PIN = {'bytes': 42830, 'sha256': '32c360638c7ba7d6cdea12362e8cac5e21dc49551a6da7f3c09e64a0ffaa36ae'}
MANIFEST_PIN = {'bytes': 562020, 'sha256': '2a6ed59572eca3f25f6c0d205cc5cef88b3eb6df177fb546e3cc327f76f24e23'}
NATIVE_POPULATION_SHA256='94a55590b2e4b7034c6f6b7be017546ba4830c5dde4651a7b72542162e5aa831'
PACKAGE_POPULATION_SHA256='adb80e893640052cf24598456662b61a799cc53011eb69a25843c7501cfef135'
RETAINED_EVIDENCE={'COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json': {'bytes': 7321, 'sha256': 'fd3a8bd27f85e0eb1ae18fe17bb570b9da8538e448c2bb3f47d14596ecece241'}, 'COMPOSITION_PLACEMENT_RECEIVING.json': {'bytes': 975, 'sha256': 'bca4cbdd26b69fa17a23ad990ade5ff3dfa36705de5a96cd6b656254dd2ded0e'}, 'PACKAGE_BODY_RECEIVING.json': {'bytes': 3571, 'sha256': '944adc3d9a456439b745aa59bc374ba15b033130dd01902e2343a48d2eb5610e'}, 'PACKAGE_ROOT_RECEIVING.json': {'bytes': 752, 'sha256': '515e1be7200a23e6e232023abab7f83e576a6baacdb46ad0e481d66dea5517b7'}, 'PACKAGE_TERMINAL_RECEIVING.json': {'bytes': 2280, 'sha256': '280faf0b8c6ed1fe21087766068e1b547faa3b504a6ce780a5ebb12ecea7cbcd'}, 'PLACEMENT_ARTIFACT_MANIFEST.json': {'bytes': 183, 'sha256': 'c39aed8ca08deadf4dfa88c6b24d53146d219fa0f5834b2e861f086c64b00ea1'}, 'PLACEMENT_DIAGNOSTIC.json': {'bytes': 25540, 'sha256': '29e56d55524d817c27691308f98a14ce799f5f5e4da7b654ca5ced1ac914872d'}, 'PLACEMENT_EVIDENCE_INDEX.json': {'bytes': 868, 'sha256': '23a43728d38dade3e53c8b82eb87de55ac242798acf0d2b9be9c84e7cd0ae477'}, 'PLACEMENT_INDEPENDENT_RECEIVING.json': {'bytes': 1453, 'sha256': 'e88128b3045e1da38da9c30f50e5cfde742cab1f10f3bd34e955eb4302a1952b'}, 'PLACEMENT_ROOT_RECEIVING.json': {'bytes': 1834, 'sha256': '332d472868d91b77ef56d91d834f72766e224f444a807b907b3de64869538456'}}
OBSERVATION_BASIS = {'all_required_selectors_measured_in_one_new_job': False, 'basis': 'COMPOSITE_PROSPECTIVE_IMAGE23_CACHE02_OBSERVATIONS', 'complete_runtime_qualification': False, 'failed_main_preflight': {'artifact': {'bytes': 14154, 'name': 'OPERATION.json', 'sha256': '327d335df54af7b38edd43ebd997db1c24ebc55b9495426df7b22eb4dd2e1218'}, 'job_id': '140843824596', 'measured_source': {'commit': 'fc2e416c5da38eb370045561f5281a846785ec3e', 'tree': 'a9914d446d2a3e0653c972cf50197186e23555d8'}, 'operator_commit': '2bb3eb7e92f668434cc6daf85ac1f37dbeded6b5', 'result': 'RUNTIME_SELECTOR_PREFLIGHT_REFUSED', 'root_receiving_comment_id': 7232816348, 'run_attempt': 1, 'run_id': '46101208035', 'scope': 'OTHER_ELEVEN_EXACT_SELECTOR_RECORDS_MATCHED_AND_CACHE_MISMATCH_OBSERVED', 'status': 'UNQUALIFIED'}, 'fresh_cache_diagnostic': {'artifact': {'bytes': 132153, 'name': 'CACHE_OBSERVATION.json', 'sha256': '3e47a0a36395f100dd84b6c4e21df3b9fa6a082967dfcb155434eed7d3e7352e'}, 'cache_opening_and_closing': {'bytes': 38396, 'link': None, 'mode': 420, 'resolved': '/etc/ld.so.cache', 'sha256': 'e70987876889374de327e050a0fa554e5db6110271af39d19c84c1d4ce5e1f0b'}, 'complete_runtime_measured': False, 'configuration_scope': 'CLOSED_PARSED_SYSTEM_PROJECTION', 'decoded_entries': 619, 'independent_receiving': {'bytes': 6277, 'name': 'TERMINAL_REVIEW.md', 'sha256': 'b23285a3bf280b8ca2a6a44289610fe55db4fbbda5cf8d95fb52e8e57d651005'}, 'job_id': '140865228978', 'observer_commit': '1cde8f5218110c52acbb6806e35c37c755c1935a', 'run_attempt': 1, 'run_id': '46108080622', 'status': 'CAPTURED_UNQUALIFIED', 'target_file_bytes_measured': False}, 'historical_cache_divergence': 'UNRESOLVED', 'historical_v24_observation': {'image': '20261122.23.1', 'independent_receiving': {'bytes': 18998, 'sha256': '70e023941d7a8a4b51935f24384b2ad85681aa830e0e8cef39ef117f41201388'}, 'job_id': '139933098821', 'measured_source': {'commit': '6d2c0c3522ce128ea8143d7fc93e1180f46227f8', 'tree': 'a0c86d6a71e1f8b9ac3aed2d7c984ac79aeef26e'}, 'measurement_scope': 'ACTUAL_BOUNDED_HOST_TWELVE_SELECTORS_AND_GIT_UPLOAD_PACK_ALIAS_RECEIVED_UNQUALIFIED', 'observation': {'bytes': 29045, 'sha256': '7be9359f3386babeaaf45043db17b9634dba0bda3daaf84e08ca6b531d226fce'}, 'operation_commit': 'd258f1fe1793045877ab7403c34274ed0e828f7c', 'run_attempt': 1, 'run_id': '45826850084', 'whole_tuple_sha256': 'ac0082a86f6c3331502b38bdd0dadd76f4d8ea7f6938a0bc600b8442eb11e686'}, 'image': '20261122.23.1', 'native_qualification': False, 'operation_grants': [], 'original_awards': []}
PLACEMENT = {'current_successor_relation': {'CORE_FILES_unchanged': True, 'after': {'bytes': 16981, 'sha256': '3da11fab7acd3007d4fb3b6eab0ca3abe8fa9869d1ab310e97e5d07823a441a9'}, 'all_other_top_level_ast_equal': True, 'assignment_changes': {'SOURCE': {'after': 'd208cb84a9d69ad03709de6102f1adde3cf3df7f', 'before': '0795276b43f96bfc475bb53c4bd8171c3f2f610a'}, 'TREE': {'after': '8ba23825751d374c6e343485d9ff1a9e0401e75a', 'before': '86fe547ed3232648f17ba49ce9d7c97f4f98e7f1'}}, 'before': {'bytes': 16981, 'sha256': 'ac7100ded52513884850b88779fa3ec46ace2d086f3871d7476dac5a532c7534'}, 'bootstrap_unchanged': True, 'compared_operator_commit': '3360b5d8805628a157d57fc7e6ae8d0596b623df'}, 'historical_retained_relation': {'admitted_successor': {'bytes': 16975, 'sha256': 'e10d01cc161103693cbdecd30f6e33d7bd2200d22fd2f913610cf1719c1362da'}, 'allowed_ast_changes': ['SOURCE', 'TREE', 'CORE_FILES'], 'historical_body_recovered_here': False, 'retained': {'bytes': 16933, 'sha256': '17d9e9df58943b8d56c360e574f02c5b827e05f26ab01c3daad31be46dc6b6b1'}, 'status': 'INHERITED_ACCEPTED_RELATION_NOT_REPERFORMED'}, 'schema': 'dg16.fixed-placement-staged-successor-relation.v1'}
MAX_BODY=65536


RUNTIME_ADMISSION_NAME = 'RUNTIME_PROFILE_APPLICABILITY_ADMISSION.json'
RUNTIME_ADMISSION_PIN = {'bytes': 12657, 'sha256': 'b570f3b646583c3ca0195b668e3cdff332cdf2f69f89ff2d2beae2173ebcaf57'}
RUNTIME_DEFINITIONS_PIN = {'bytes': 10830, 'sha256': '88e0db7a17f51804acd4b882719aaeb4dbf68a13ff07f039c4a9a6407d9dcf59'}
RUNTIME_SELECTION_CONTRACT = {'automatic_adoption': False,
 'bookends_equal_required': True,
 'descriptor_fields': ['bytes', 'sha256', 'mode', 'resolved', 'link'],
 'exactly_one_whole_match_required': True,
 'freeze_before_dependent_use': True,
 'later_reselection': False,
 'observation': 'ONE_COMPLETE_OPENING_AND_CLOSING_SELECTOR_OBSERVATION',
 'per_field_alternative_match': False,
 'selector_count': 12,
 'source_current_required': True,
 'source_member_count_each': 15}
RUNTIME_QUALIFICATION_CEILING = {'complete_runtime_qualification': False,
 'declarations': 'PROSPECTIVE_INPUTS_ONLY',
 'fresh_genuine_original_receiving_required': True,
 'historical_missing_cache_bodies_received': False,
 'native_qualification': False,
 'unexercised_variant': 'UNVERIFIED'}

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


def validate_runtime_admission(value,*,runtime_profile=None):
    """The old V25 source relation remains historical; this is separate active runtime authority."""
    need(type(value) is dict and set(value)=={'schema','issuer','decision','scope','subject','source_manifest',
         'retained_source_admission','retained_source_acquisition','retained_embedded_source_receiving',
         'retained_source_records_scope','profile_definitions','profile_definitions_descriptor',
         'selection_contract','qualification_ceiling','operation_grants','original_awards'},'RUNTIME_ADMISSION_FIELDS')
    need(value['schema']=='dg16.finite-runtime-profile-applicability.v1' and value['issuer']=='R5_ROOT_GOVERNOR'
         and value['decision']=='ADMIT_EXACT_DECLARED_RUNTIME_PROFILES_PROSPECTIVELY'
         and value['scope']=='WHOLE_PROFILE_SELECTION_AND_ORIGINAL_QUALIFICATION_REQUIRED'
         and value['subject']==SUBJECT and value['source_manifest']==MANIFEST_PIN
         and value['retained_source_admission']==ADMISSION_PIN,'RUNTIME_ADMISSION_SUBJECT')
    need(value['retained_source_records_scope']=='ENTROPY_SUCCESSOR_SOURCE_AND_PROVENANCE_FACTS_NOT_RUNTIME_AUTHORITY_FOR_ANOTHER_VARIANT'
         and value['profile_definitions_descriptor']==RUNTIME_DEFINITIONS_PIN
         and pin(encode(value['profile_definitions']))==RUNTIME_DEFINITIONS_PIN
         and value['selection_contract']==RUNTIME_SELECTION_CONTRACT
         and value['qualification_ceiling']==RUNTIME_QUALIFICATION_CEILING
         and value['operation_grants']==[] and value['original_awards']==[],'RUNTIME_ADMISSION_SCOPE')
    if runtime_profile is not None:
        need(type(runtime_profile) is dict and set(runtime_profile)=={'source_revision','definition_sha256'}
             and type(runtime_profile.get('source_revision')) is str
             and runtime_profile['source_revision'] in value['profile_definitions'],'RUNTIME_PROFILE_IDENTITY')
        definition=value['profile_definitions'][runtime_profile['source_revision']]
        need(runtime_profile['definition_sha256']==sha(encode(definition)),'RUNTIME_PROFILE_IDENTITY')
    return value


def receive(packet,*,source=None,runtime_profile=None):
    packet=Path(packet);record_path=packet/'public-inputs'/ADMISSION_NAME
    raw,identity=read_ordinary(record_path,MAX_BODY)
    need(pin(raw)==ADMISSION_PIN,'SOURCE_ADMISSION_PIN')
    manifest_raw,manifest_identity=read_ordinary(packet/'SOURCE_MANIFEST.json',1024*1024)
    need(pin(manifest_raw)==MANIFEST_PIN,'SOURCE_MANIFEST_PIN')
    value=validate(parse(raw),parse(manifest_raw))
    runtime_path=packet/'public-inputs'/RUNTIME_ADMISSION_NAME
    runtime_raw,runtime_mark=read_ordinary(runtime_path,MAX_BODY)
    need(pin(runtime_raw)==RUNTIME_ADMISSION_PIN,'RUNTIME_ADMISSION_PIN')
    runtime=validate_runtime_admission(parse(runtime_raw),runtime_profile=runtime_profile)
    held={}
    for name,expected in sorted(RETAINED_EVIDENCE.items()):
        body,mark=read_ordinary(packet/'public-inputs'/name,MAX_BODY)
        need(pin(body)==expected,'SOURCE_RETAINED_EVIDENCE');held[name]=(body,mark)
    body,mark=read_ordinary(packet/'public-inputs/SOURCE_ACQUISITION.json',MAX_BODY)
    need(pin(body)==runtime['retained_source_acquisition'],'RUNTIME_RETAINED_SOURCE_RECORD')
    acquisition=parse(body)
    embedded=(acquisition.get('evidence') or {}).get('ROOT_SOURCE_RECEIVING.json')
    need(type(embedded) is dict and set(embedded)=={'bytes','sha256','text'} and type(embedded['text']) is str
         and {key:embedded[key] for key in ('bytes','sha256')}==runtime['retained_embedded_source_receiving']
         and pin(embedded['text'].encode('utf8'))==runtime['retained_embedded_source_receiving'],
         'RUNTIME_RETAINED_SOURCE_RECORD')
    held['SOURCE_ACQUISITION.json']=(body,mark)
    if source is not None:verify_current(value,source)
    for name,opening in sorted(held.items()):
        need(read_ordinary(packet/'public-inputs'/name,MAX_BODY)==opening,'SOURCE_RETAINED_CLOSING')
    need(read_ordinary(record_path,MAX_BODY)==(raw,identity)
         and read_ordinary(packet/'SOURCE_MANIFEST.json',1024*1024)==(manifest_raw,manifest_identity)
         and read_ordinary(runtime_path,MAX_BODY)==(runtime_raw,runtime_mark),'SOURCE_ADMISSION_CLOSING')
    return value
