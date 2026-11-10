"""Fixed diagnostic-copy frame. No process, provider or authority API."""
import hashlib
import json
from pathlib import Path
import re
import time
import types

SOURCE_COMMIT = '08e6faa9a71fc09996a32e114346dce6508ef656'
SOURCE_TREE = '83165996af29c20f526f53a9dc6c4d8edfec4be5'
OWNER_SHA='79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'
DIAGNOSTIC_SHA = '39d8ea138dedfce118a7b2a8e040c42cec1631e99065a2d0dc855e53bdcbdca2'
CATALOG_SHA = 'b5321499719c129b71fb3b0dba82b23582a153f830bce98005b655563894632b'
STREAM_MAX=128*1024**2
HEADER_MAX=65536
CHUNK=1024**2
MAGIC=b'DG16-G2-FS-V1\n\x00\x00'
PLAIN_MAX=24+HEADER_MAX+2*STREAM_MAX
CIPHER_OVERHEAD=16384
CIPHER_MAX=PLAIN_MAX+CIPHER_OVERHEAD
AUX_BYTES=512*1024
TOTAL_MAX=2*1024**3
ENTRY_MAX=68*4096
ENVELOPE_MAX=8192
ZIP_MAX=CIPHER_MAX+ENVELOPE_MAX+1024**2
STREAMS=('stdout','stderr')
ARTIFACT_MEMBERS=('FAILURE_ENVELOPE.json','FAILED_STREAMS.cms')
COPY_SCOPE='ENCRYPTED_DIAGNOSTIC_COPY_NOT_LIVE_ACCEPTANCE_CUSTODY'

class Refusal(ValueError):pass
def need(value,code):
    if not value:raise Refusal(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return dict(bytes=len(raw),sha256=sha(raw))
def encode(value):
    try:return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
    except (ValueError,TypeError,RecursionError) as exc:raise Refusal('JSON_SHAPE') from exc
def exact(value,keys):need(type(value) is dict and set(value)==set(keys.split()),'FIELDS')
def integer(n,lo,hi):return type(n) is int and lo<=n<=hi
def digest(s):return type(s) is str and re.fullmatch('[0-9a-f]{64}',s) is not None
def descriptor(row,maximum):
    exact(row,'bytes sha256');need(integer(row['bytes'],0,maximum) and digest(row['sha256']),'DESCRIPTOR')
    return row
def parse(raw,maximum):
    need(type(raw) is bytes and 0<len(raw)<=maximum,'JSON_BOUND')
    def pairs(items):
        result={}
        for k,v in items:need(k not in result,'DUPLICATE_KEY');result[k]=v
        return result
    try:value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE')))
    except (ValueError,UnicodeError,RecursionError) as exc:raise Refusal('JSON_REFUSED') from exc
    need(encode(value)==raw,'NONCANONICAL_JSON');return value

def context(value):
    exact(value,'repository branch run_id run_attempt workflow_commit source_commit source_tree workflow_path job_name')
    need(value['repository']=='theislampill/IMPLEMENTAUDIT.md'
      and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE
      and value['workflow_path']=='.github/workflows/dg16-r5-full-g2.yml'
      and value['job_name']=='full-registry-raw-pair','CONTEXT_SOURCE_SCOPE')
    need(type(value['branch']) is str and re.fullmatch(r'pro/[A-Za-z0-9/_-]{1,180}',value['branch'])
      and '..' not in value['branch'] and '//' not in value['branch'],'CONTEXT_BRANCH')
    need(type(value['run_id']) is str and re.fullmatch('[1-9][0-9]{0,19}',value['run_id'])
      and type(value['run_attempt']) is int and value['run_attempt']==1
      and type(value['workflow_commit']) is str and re.fullmatch('[0-9a-f]{40}',value['workflow_commit'])
      and value['workflow_commit']!='0'*40,'CONTEXT_RUN')
    return value

_DIAGNOSTIC=None
def diagnostic():
    """Reuse the exact reviewed current-source validator; no owner execution."""
    global _DIAGNOSTIC
    root=Path(__file__).resolve().parent
    body=(root/'capture_evidence.py').read_bytes();catalog_raw=(root/'CAPTURE_DIAGNOSTIC_CATALOG.json').read_bytes()
    need(sha(body)==DIAGNOSTIC_SHA and sha(catalog_raw)==CATALOG_SHA,'DIAGNOSTIC_DEPENDENCY_PIN')
    if _DIAGNOSTIC is None:
        module=types.ModuleType('failed_stream_pinned_diagnostic');module.__file__=str(root/'capture_evidence.py')
        exec(compile(body,module.__file__,'exec'),module.__dict__)
        catalog=module.strict(catalog_raw)
        need(catalog['source_commit']==SOURCE_COMMIT and catalog['source_tree']==SOURCE_TREE
          and catalog['owner_sha256']==OWNER_SHA,'DIAGNOSTIC_SOURCE_PIN')
        _DIAGNOSTIC=module,catalog
    return _DIAGNOSTIC

def validate_failed(projection):
    need(len(encode(projection))<=32768,'FAILED_PROJECTION_BOUND')
    exact(projection,'schema authority mode selection_file reserved_modes observation scope original_acceptance Q02')
    need(projection['schema']=='dg16.full-pair-failed-leg-observation.v1' and projection['authority']=='NONE'
      and projection['mode'] in ('legacy','dag') and projection['scope']=='SUPPLEMENTARY_FAILURE_DATA_NOT_FULL_PAIR_RECEIVING'
      and projection['original_acceptance'] is False and projection['Q02'] is False,'FAILED_PROJECTION_SCOPE')
    descriptor(projection['selection_file'],4096)
    need(projection['reserved_modes']==(['legacy'] if projection['mode']=='legacy' else ['legacy','dag']),'FAILED_RESERVED_MODES')
    module,catalog=diagnostic()
    try:module.validate_projection(projection['observation'],catalog)
    except (ValueError,KeyError,TypeError,RecursionError) as exc:raise Refusal('FAILED_DIAGNOSTIC_VALIDATOR') from exc
    record=projection['observation']['record']
    need(record['mode']==projection['mode'] and record['attempts']==1 and record['reserved'] is True,'FAILED_LEG_BINDING')
    need(record['owner_return'] is None or record['owner_return']!=0,'NOT_A_FAILED_LEG')
    need(record['custody'] is not None and record['custody']['quiescence']=='ECHILD_ALL_CHILDREN'
      and record['custody']['flag_restored'] is True and record['closing_censuses_equal'] is True
      and record['stream_hashes_match_record'] is True,'FAILED_STREAM_CUSTODY_UNESTABLISHED')
    need(type(record['capture_record']) is dict,'CAPTURE_RECORD_REQUIRED')
    for name in STREAMS:
        row=record['streams'][name]
        need(type(row) is dict,'COMPLETE_STREAM_DESCRIPTOR_REQUIRED');descriptor(row['file'],STREAM_MAX)
        need(row['file']['sha256']==record['capture_record'][name+'_sha256'],'STREAM_CAPTURE_HASH_JOIN')
    need(record['custody']['primary_exit']==record['capture_record']['primary_exit'],'PRIMARY_CUSTODY_JOIN')
    if record['owner_return'] is not None:
        need(record['owner_return']==record['capture_record']['primary_exit'] and record['primary_raw_values_agree'] is True,
          'PRIMARY_RETURN_JOIN')
    return record

def outcome(record):
    if record['owner_return'] is not None:return 'RETURNED_NONZERO'
    return 'OWNER_RAISED' if record['owner_exception'] is not None else 'UNKNOWN'

def make_manifest(ctx,projection,recipient):
    context(ctx);descriptor(recipient,8192);need(recipient['bytes']>0,'RECIPIENT_REQUIRED')
    record=validate_failed(projection)
    value=dict(schema='dg16.protected-failed-stream-frame.v1',authority='NONE',context=ctx,recipient=recipient,
      failed_leg=projection,outcome=outcome(record),streams={n:record['streams'][n]['file'] for n in STREAMS},
      custody_scope=COPY_SCOPE,original_acceptance=False)
    return validate_manifest(parse(encode(value),HEADER_MAX),ctx,recipient)

def validate_manifest(value,expected_context,recipient):
    exact(value,'schema authority context recipient failed_leg outcome streams custody_scope original_acceptance')
    context(expected_context);context(value['context']);descriptor(recipient,8192)
    need(value['schema']=='dg16.protected-failed-stream-frame.v1' and value['authority']=='NONE'
      and value['context']==expected_context and value['recipient']==recipient
      and value['custody_scope']==COPY_SCOPE and value['original_acceptance'] is False,'FRAME_CONTEXT')
    record=validate_failed(value['failed_leg']);exact(value['streams'],'stdout stderr')
    need(value['outcome']==outcome(record),'OUTCOME_NEUTRALITY')
    for n in STREAMS:
        descriptor(value['streams'][n],STREAM_MAX)
        need(value['streams'][n]==record['streams'][n]['file'],'FRAME_STREAM_JOIN')
    need(len(encode(value))<=HEADER_MAX,'MANIFEST_BOUND');return value

def plain_size(header_bytes,streams):
    need(integer(header_bytes,1,HEADER_MAX) and set(streams)==set(STREAMS),'FRAME_SIZE_INPUT')
    need(all(integer(streams[n]['bytes'],0,STREAM_MAX) for n in STREAMS),'STREAM_SIZE_BOUND')
    return 24+header_bytes+sum(streams[n]['bytes'] for n in STREAMS)

def allocation(existing_bytes,existing_entries,plain_bytes):
    need(integer(existing_bytes,0,TOTAL_MAX) and integer(existing_entries,0,ENTRY_MAX)
      and integer(plain_bytes,25,PLAIN_MAX),'ALLOCATION_INPUT')
    cipher_bytes=plain_bytes+CIPHER_OVERHEAD
    total=existing_bytes+plain_bytes+cipher_bytes+AUX_BYTES
    need(total<=TOTAL_MAX and existing_entries+32<=ENTRY_MAX,'SHARED_ALLOCATION_REFUSED')
    return dict(existing_bytes=existing_bytes,existing_entries=existing_entries,plain_bytes=plain_bytes,
      cipher_bytes=cipher_bytes,auxiliary_bytes=AUX_BYTES,total_bytes=total,total_entries=existing_entries+32,
      total_limit=TOTAL_MAX,entry_limit=ENTRY_MAX)

class Deadline:
    """Existing failed closing allocation only; leave original finalization90s."""
    def __init__(self,overall,closing,clock=time.monotonic):
        need(type(overall) in (int,float) and type(closing) in (int,float),'DEADLINE_INPUT')
        self.clock=clock;now=clock();self.stop=min(now+60,overall-90,closing-90)
        self.check()
    def check(self):need(self.clock()<self.stop,'RETENTION_DEADLINE')

def read_exact(reader,size,check):
    need(integer(size,0,HEADER_MAX),'SMALL_READ_BOUND');parts=[];left=size
    while left:
        check();part=reader.read(min(left,CHUNK));check()
        need(type(part) is bytes and 0<len(part)<=left,'FRAME_SHORT_READ')
        parts.append(part);left-=len(part)
    return b''.join(parts)

def write_chunk(writer,raw,check):
    need(type(raw) is bytes and len(raw)<=CHUNK,'COPY_CHUNK_BOUND');check()
    count=writer.write(raw);check();need(count==len(raw),'FRAME_SHORT_WRITE')

def copy_exact(reader,writer,size,expected_hash,check,frame_hash=None):
    need(integer(size,0,STREAM_MAX) and digest(expected_hash),'COPY_INPUT')
    h=hashlib.sha256();left=size
    while left:
        check();raw=reader.read(min(CHUNK,left));check()
        need(type(raw) is bytes and 0<len(raw)<=min(CHUNK,left),'STREAM_SHORT_READ')
        write_chunk(writer,raw,check);h.update(raw)
        if frame_hash is not None:frame_hash.update(raw)
        left-=len(raw)
    need(h.hexdigest()==expected_hash,'STREAM_HASH_MISMATCH')

def pack(manifest,readers,writer,check):
    validate_manifest(manifest,manifest['context'],manifest['recipient']);need(set(readers)==set(STREAMS),'STREAM_NAMES')
    header=encode(manifest);prefix=MAGIC+len(header).to_bytes(8,'big');h=hashlib.sha256()
    need(len(MAGIC)==16,'FRAME_MAGIC')
    for part in (prefix,header):write_chunk(writer,part,check);h.update(part)
    for n in STREAMS:
        row=manifest['streams'][n];copy_exact(readers[n],writer,row['bytes'],row['sha256'],check,h)
        check();extra=readers[n].read(1);check();need(extra==b'','STREAM_EXTRA_BYTES')
    check();return dict(bytes=plain_size(len(header),manifest['streams']),sha256=h.hexdigest())

def unpack(reader,expected_context,recipient,sinks,check):
    need(set(sinks)==set(STREAMS),'STREAM_NAMES')
    prefix=read_exact(reader,24,check);need(prefix[:16]==MAGIC,'FRAME_MAGIC')
    length=int.from_bytes(prefix[16:],'big');need(0<length<=HEADER_MAX,'MANIFEST_BOUND')
    manifest=validate_manifest(parse(read_exact(reader,length,check),HEADER_MAX),expected_context,recipient)
    for n in STREAMS:
        row=manifest['streams'][n];copy_exact(reader,sinks[n],row['bytes'],row['sha256'],check)
    check();extra=reader.read(1);check();need(extra==b'','FRAME_TRAILING_BYTES')
    return manifest

def artifact_name(ctx):context(ctx);return 'dg16-g2-failed-streams-'+ctx['run_id']+'-a1'
