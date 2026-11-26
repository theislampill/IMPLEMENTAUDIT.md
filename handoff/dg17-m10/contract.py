"""Data-only operator contracts. No product imports or dispatch."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import time
import zipfile

BASE = '5742c78f9e1b30a75befb9634fe2aeab6242144d'
REPO = 'theislampill/IMPLEMENTAUDIT.md'
TRIGGER = 'engineering/pro-dg17-m10-canonical-20261126-01'
CONTROL = TRIGGER + '-control'
WORKFLOW = '.github/workflows/dg17-m10-canonical.yml'
PREFIX = 'handoff/dg17-m10/'
OWNER = '59fd223c0a7493d94a3097c0b7d64327ff310b8af703a215a59fab2ac9ce974d'
FILES = ('contract.py','compose.py','hosted.py','receive.py','pins.json','fixed_oracle.py')
AUTH = 'BOUNDED_REVIEW_RECONCILIATION_ONLY'
MAX_CONTROL = 256 * 1024
MAX_SUBJECT = 192 * 1024
MAX_ZIP = 2 * 1024 * 1024
CARRIER = ('child-return.json','decision.json','manifest.json')
HELD = '    if: ${{ false }}'
LIVE = "    if: ${{ github.event.created && github.run_attempt == '1' }}"
def need(ok, msg):
    if not ok:
        raise ValueError(msg)
def unique(pairs):
    result = dict(pairs)
    need(len(result) == len(pairs), 'duplicate JSON member')
    return result
def decode(body):
    def bad(_):
        raise ValueError('nonfinite number')
    return json.loads(body.decode('utf-8','strict'), object_pairs_hook=unique, parse_constant=bad)
def wire(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def keys(value, population):
    need(type(value) is dict and set(value) == set(population.split()), 'record field population')
def regular(path, limit):
    path = Path(path).absolute()
    need(path == path.resolve(strict=True), 'aliased file')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit,'file type or size')
    with path.open('rb') as src:
        raw = src.read(limit + 1)
        info = os.fstat(src.fileno())
    need(before==info or (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==
         (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns), 'file changed')
    need(len(raw) == before.st_size, 'file changed size')
    return raw
def b64(raw):
    return base64.b64encode(raw).decode('ascii')
def binary(encoded):
    raw = base64.b64decode(encoded,validate=True)
    need(b64(raw)==encoded,'noncanonical base64')
    return raw
def identifier(value):
    need(isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{0,159}',value)
         and '..' not in value.split('/') and '//' not in value,'invalid identity')
def brief(value):
    need(type(value) is str and 8<=len(value)<=420 and value==value.strip()
         and all(c.isprintable() and c not in '|`' for c in value),'invalid bounded purpose')
def digest(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value), 'expected sha256')
def unpack_zip(raw, names, limit=8*1024*1024):
    need(len(raw)<=MAX_ZIP,'ZIP transport cap')
    out = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for info in z.infolist():
            n = info.filename
            need(n in names and n not in out and info.orig_filename==n and not info.is_dir()
                 and not info.flag_bits & 1 and (info.external_attr>>16)&0o170000 in (0,stat.S_IFREG)
                 and n==Path(n).name and n not in ('.','..') and '\\' not in n,
                 'ZIP member population/type')
            need(info.file_size<=limit-sum(map(len,out.values())), 'expanded ZIP cap')
            out[n]=z.read(info)
    need(set(out)==set(names),'missing ZIP members')
    return out
def subject_files(subject, body):
    keys(subject,'schema files')
    need(subject['schema']=='dg17.m10.subject.v1' and type(subject['files']) is list and
         0<len(subject['files'])<=48,'subject manifest')
    names=[]
    for row in subject['files']:
        keys(row,'path bytes sha256')
        name=row['path']
        need(type(name) is str and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}',name)
             and name.casefold() not in [n.casefold() for n in names],'subject member name')
        names.append(name)
        need(type(row['bytes']) is int and row['bytes']>0,'subject byte count')
        digest(row['sha256'])
    need(names==sorted(names),'subject order')
    blobs=unpack_zip(body,names,MAX_SUBJECT)
    for row in subject['files']:
        raw=blobs[row['path']]
        need((len(raw),sha(raw))==(row['bytes'],row['sha256']),'subject content mismatch')
    return blobs
def template_digest(directory, workflow):
    return sha(wire({**{f:sha(regular(directory/f,2*1024*1024)) for f in FILES},WORKFLOW:sha(workflow)}))
def validate_composition(bundle, template, root_bookend):
    keys(bundle,'appointment subject_manifest subject_zip operator_review root_receiving')
    a=bundle['appointment']
    keys(a,'schema authority source template subject_manifest subject_zip operator_review root_receiving reviewer subject_author reviewer_task purpose store_owner root_actor_id publication pending_review_record')
    need((a['schema'],a['authority'],a['source'],a['template'])==
         ('dg17.m10.appointment.v1',AUTH,BASE,template),'appointment scope/source/template')
    digest(root_bookend)
    need(sha(wire(a))==root_bookend,'appointment differs from independent Root readback')
    need(a['publication']=='PUBLIC_EXACT_REVIEW_INPUTS_AND_BOUNDED_RESULT','subject disclosure authority')
    for key in ('reviewer','subject_author','store_owner','pending_review_record'):
        identifier(a[key])
    brief(a['purpose'])
    task_name=a['reviewer_task']
    need(isinstance(task_name,str) and re.fullmatch('[a-z][a-z0-9_-]{2,70}',task_name)
         and task_name not in {'audit-assess','audit-state','audit-andon','audit-implement'}
         and not re.fullmatch(r'[0-9a-f]{32,64}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',task_name),
         'invalid logical reviewer task')
    need(a['reviewer']!=a['subject_author'] and re.fullmatch('[1-9][0-9]{0,18}',a['root_actor_id']),
         'reviewer or actor binding')
    blobs={k:binary(bundle[k]) for k in ('subject_manifest','subject_zip','operator_review','root_receiving')}
    for k,raw in blobs.items():
        need(0<len(raw)<=384*1024 and sha(raw)==a[k],'appointment input '+k)
    subject=subject_files(decode(blobs['subject_manifest']),blobs['subject_zip'])
    review=decode(blobs['operator_review'])
    keys(review,'schema template reviewer original_report original_report_sha256 original_return original_return_sha256 dispatch_record')
    need(review['schema']=='dg17.m10.operator-review-evidence.v1' and review['template']==template,'operator review template')
    for key in ('reviewer','dispatch_record'):
        identifier(review[key])
    for key in ('original_report','original_return'):
        raw=binary(review[key])
        need(0<len(raw)<=128*1024 and sha(raw)==review[key+'_sha256'],'original review bytes '+key)
    received=decode(blobs['root_receiving'])
    keys(received,'schema template independent_reviewer operator_author review_sha256 outcome subject_manifest_sha256 purpose receiving_record')
    for k in ('operator_author','independent_reviewer','receiving_record'):
        identifier(received[k])
    need(received['schema']=='dg17.m10.operator-receiving.v1' and received['template']==template and
         received['independent_reviewer']!=received['operator_author'] and received['independent_reviewer']==review['reviewer'] and received['review_sha256']==a['operator_review']
         and received['outcome']=='QUALIFIED_FOR_EXACT_COMPOSITION' and
         received['subject_manifest_sha256']==a['subject_manifest'] and received['purpose']==a['purpose'],
         'operator qualification/subject receiving mismatch')
    return a,subject
def control_data(population, expected, parent, parent_list, observed_oid, reread_oid, now):
    keys(expected,'repository run_id attempt job_id job_key operator source started_at obligation_id route_transaction_id authority control_ref open_oid open_artifact_id open_artifact_sha256 packet_digest child_digest owner_sha256 deadline reviewer reviewer_task purpose subject_manifest subject_zip appointment_sha256')
    need(expected['repository']==REPO and expected['source']==BASE and expected['operator']==parent
         and expected['job_key']=='canonical' and expected['authority']==AUTH and expected['owner_sha256']==OWNER
         and expected['control_ref']=='refs/heads/'+CONTROL and type(expected['deadline']) is int
         and type(expected['attempt']) is int and expected['attempt']==1 and
         all(type(expected[k]) is int and expected[k]>0 for k in ('job_id','run_id','open_artifact_id')),
         'expected control scope')
    for k in ('open_artifact_sha256','subject_manifest','subject_zip','appointment_sha256'):
        digest(expected[k])
    for k in ('child_digest','packet_digest','route_transaction_id','obligation_id'):
        need(expected[k].startswith('sha256:'),'canonical identifier scheme')
        digest(expected[k][7:])
    need(type(now) is int and now<expected['deadline'] and parent_list==[parent]
         and re.fullmatch('[0-9a-f]{40}',observed_oid) and observed_oid==reread_oid,'late/foreign/unstable carrier')
    need(set(population)==set(CARRIER) and sum(map(len,population.values()))<=MAX_CONTROL,'control population/budget')
    need(len(population['child-return.json'])<=24*1024 and len(population['decision.json'])<=8192
         and len(population['manifest.json'])<=16*1024,'typed carrier member limit')
    manifest=decode(population['manifest.json'])
    keys(manifest,'bindings')
    fields=manifest['bindings']
    keys(fields,' '.join([*expected,'return_sha256','decision_sha256','receiving_record','report_sha256','report_manifest_sha256']))
    need(all(type(fields[k]) is type(v) and fields[k]==v for k,v in expected.items()),'wrong live binding')
    ret,dec=(decode(population[k]) for k in CARRIER[:2])
    keys(ret,'schema obligation_id route_transaction_id packet_digest status payload')
    keys(dec,'schema obligation_id route_transaction_id return_digest outcome reason')
    payload=ret['payload']
    keys(payload,'reviewer subject_manifest report_sha256 report_manifest_sha256 receiving_purpose')
    for k in ('obligation_id','route_transaction_id'):
        need(ret[k]==dec[k]==expected[k],'wrong canonical return identity')
    for name,k in [('child-return.json','return_sha256'),('decision.json','decision_sha256')]:
        need(fields[k]==sha(population[name]),'control digest mismatch')
    digest(fields['report_sha256'])
    digest(fields['report_manifest_sha256'])
    identifier(fields['receiving_record'])
    brief(dec['reason'])
    need(ret['schema']=='implementaudit.child-return.v1' and ret['status']=='RETURNED' and
         ret['packet_digest']==expected['packet_digest'] and payload==
         dict(reviewer=expected['reviewer'],subject_manifest=expected['subject_manifest'],
              report_sha256=fields['report_sha256'],report_manifest_sha256=fields['report_manifest_sha256'],
              receiving_purpose=expected['purpose']),'typed return mismatch')
    need(dec['schema']=='implementaudit.governor-route-decision.v1' and dec['outcome']=='SATISFIED'
         and dec['return_digest']=='sha256:'+fields['return_sha256'],'decision return mismatch')
    return manifest
def admit_result(code, payload, before, after, target_oid, positive, ids):
    wanted=(0,'SATISFIED',True,1) if positive else (3,'RETURNED',False,0)
    observed=(code,payload['route_state'],payload['advance_allowed'],payload['governor_decision_count'])
    need(all(type(a) is type(b) and a==b for a,b in zip(observed,wanted)), 'unexpected admission result')
    need(payload['schema']=='implementaudit.route-transaction-result.v1' and payload['decision']=='REQUIRED'
         and payload['selected_child']=='audit-assess' and payload['status']=='CURRENT'
         and before==after==target_oid==payload['record_oid'] and
         all(payload[k]==v for k,v in ids.items()),'admission identities')

def complete_after_omission(stage, target_oid, ids, actual_scope, completion):
    need(stage['source_sha256']==OWNER and stage['provider_scope']==actual_scope,'negative execution scope')
    admit_result(stage['exit_code'],stage['payload'],stage['before_record_oid'],stage['after_record_oid'],
                 target_oid,False,ids)
    return completion()
