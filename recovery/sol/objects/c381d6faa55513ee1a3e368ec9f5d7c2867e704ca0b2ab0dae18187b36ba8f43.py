"""Root-only one-shot G1 control publication driver; no automatic tool dispatch.

Actual Root invocation, issued body/admission and genuine tool history remain
external authority. This driver never manufactures a control decision. It
emits exact existing publication/read plans and consumes no-echo TTY frames.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import types
import urllib.parse

ISSUER = '01a1953f-a15b-7811-aa72-3538ebb03562'
ROOT = Path('/home/agent/dg16-g1-current04-operators/public-receiver-02')
RECEIVER_SHA = '378846f9cfd5f60ce3e3b48adb3c2e3c7cf94a701ed9aee46e5ba3072f4fc122'
RESOLVER_SHA = 'b2ac1130149d9878a3a00c7d8ba214743920a1aede38cb6b75699e14a2d03530'
CAP = 32*1024**2


def need(ok, code):
    if not ok: raise ValueError(code)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def parse(raw):
    def pairs(rows):
        out = {}
        for key,value in rows:
            need(key not in out, 'DUPLICATE_KEY'); out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE'))


def metadata_guard(raw):
    """No signed/token-bearing unexpected public metadata reaches the journal."""
    credential_keys = {'authorization','password','token','accesstoken','refreshtoken',
                       'completiontoken','clientsecret','secretaccesskey','apikey','credential','credentials'}
    signed_query_keys = {'sig','signature','xgoogsignature','xgoogcredential'}
    def walk(v, depth=0):
        need(depth <= 64, 'METADATA_DEPTH')
        if type(v) is dict:
            for k,x in v.items():
                key = re.sub('[-_]', '', k.lower())
                if key in credential_keys:
                    need(x in (None, '', False), 'CREDENTIAL_RESULT_REFUSED')
                walk(x, depth+1)
        elif type(v) is list:
            for x in v: walk(x, depth+1)
        elif type(v) is str:
            need(not re.search(r'(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}|\bgh[pousr]_[A-Za-z0-9]{20,}', v), 'CREDENTIAL_RESULT_REFUSED')
            for url in re.findall(r'https?://[^\s<>"\']+', v):
                p = urllib.parse.urlsplit(url)
                keys = {re.sub('[-_]', '', urllib.parse.unquote(k).lower()) for k in urllib.parse.parse_qs(p.query)}
                need(not p.username and not p.password and
                     not keys.intersection(credential_keys | signed_query_keys)
                     and not any(k.startswith('xamz') for k in keys), 'SIGNED_RESULT_REFUSED')
            if v.lstrip().startswith(('{','[')):
                try: nested = parse(v.encode())
                except (ValueError, TypeError, RecursionError): return
                walk(nested, depth+1)
    walk(parse(raw))


def run_publication(R, sources, received, body, parent_sha, deadline_ms, journal,
                    frame, emit, *, now_ms=None, initial_control=None):
    """Concrete loop; frame supplies actual Root results, never invokes tools."""
    now_ms = now_ms or (lambda: time.time_ns()//1000000)
    pending = None; writes = []; reads = {}; raw = None
    def current():
        need(type(deadline_ms) is int and now_ms() < deadline_ms, 'EXISTING_ROOT_DEADLINE')
        R.validate_control(sources, received, body, now_ms())
    def retain_return(kind, actual):
        # A late returned outcome is evidence even when it cannot qualify the
        # next step. Credential-shaped/error-shaped bytes never get echoed.
        descriptor = R.desc(actual) if type(actual) is bytes else None
        try:
            need(type(actual) is bytes and 0<len(actual)<=R.MAX_RESULT, 'FULL_RETURN_BOUND')
            metadata_guard(actual); value=R.parse(actual)
            need(type(value) is dict and set(value)<={'content','structuredContent','isError','_meta'}
                 and type(value.get('isError')) is bool and type(value.get('_meta',{})) is dict
                 and not any(value.get('_meta',{}).get(k) for k in ('truncated','isTruncated','partial','hasMore'))
                 and (value['isError'] or type(value.get('structuredContent')) is dict), 'TYPED_COMPLETE_RETURN')
        except BaseException:
            journal.write(kind+'.REJECTED.json', R.encode(dict(authority='NONE', actual_result=descriptor,
                          raw_result_retained=False, reason='RETURN_SHAPE_OR_CREDENTIAL_REFUSED',
                          source_acceptance=False, automatic_retry=False)))
            raise
        journal.write(kind+'.RETURNED.json', R.encode(dict(authority='NONE', actual_result=descriptor,
                      returned_unix_ms=now_ms(), deadline_unix_ms=deadline_ms,
                      qualification='NOT_YET_CHECKED', source_acceptance=False, automatic_retry=False)))
        journal.write(kind+'.RESULT.json', actual)
        return value
    try:
        current()
        plan = R.publication_plan(sources, received, body, parent_sha, now_ms(), initial_control)
        journal.write('PLAN.json', R.encode(plan))
        journal.write('REQUIREMENTS.json', R.encode(R.requirements(sources, received)))
        for ordinal in range(3):
            current(); call = R.publication_call(plan, writes)
            need(call['tool'] == plan['supported_tool_order'][ordinal], 'EXACT_THREE_WRITE_ORDER')
            pending = 'write-'+str(ordinal)
            journal.reserve(R.MAX_RESULT+65536)
            intent = dict(schema='dg16.root-control-exclusive-call-intent.v1', authority='NONE',
                          kind=pending, ordinal=ordinal, call=call, deadline_unix_ms=deadline_ms,
                          automatic_retry=False, actual_native_history_required=True)
            journal.write(pending+'.INTENT.json', R.encode(intent))
            current(); emit(dict(event='intent', intent=intent))
            raw = frame(R.MAX_RESULT, min(45, (deadline_ms-now_ms())/1000))
            value = retain_return(pending, raw)
            current()
            need(type(value) is dict and value.get('isError') is False and type(value.get('structuredContent')) is dict
                 and not any(value.get('_meta',{}).get(k) for k in ('truncated','isTruncated','partial','hasMore')), 'FULL_WRITE_RESULT_REQUIRED')
            if ordinal < 2:
                result_sha = R.result_sha(raw)
                if ordinal == 0: need(result_sha == plan['expected_tree_sha'], 'ACTUAL_CREATED_TREE_DIFFERS')
            writes.append(raw); raw = None
            emit(dict(event='retained', kind=pending, receipt=R.desc(writes[-1])))
            pending = None
        published = R.result_sha(writes[1])
        for ordinal,call in enumerate(R.control_read_plan(plan, published)):
            current(); pending = 'read-'+call['kind']; journal.reserve(R.MAX_RESULT+65536)
            intent = dict(schema='dg16.root-control-exclusive-read-intent.v1', authority='NONE',
                          kind=pending, ordinal=ordinal, call=call, deadline_unix_ms=deadline_ms,
                          automatic_retry=False, actual_native_history_required=True)
            journal.write(pending+'.INTENT.json', R.encode(intent))
            current(); emit(dict(event='intent', intent=intent))
            raw = frame(R.MAX_RESULT, min(45, (deadline_ms-now_ms())/1000))
            retain_return(pending, raw)
            current(); R.unwrap_control(raw, call['arguments']['url'])
            reads[call['kind']] = raw; raw = None
            emit(dict(event='retained', kind=pending, receipt=R.desc(reads[call['kind']])))
            pending = None
        current()
        receipt = R.receive_control(sources, received, plan, published, reads, body, now_ms())
        journal.write('RECEIVING.json', R.encode(receipt)); current()
        emit(dict(event='complete', receipt=receipt)); return receipt
    except BaseException:
        raw = None
        try: journal.write('UNKNOWN.json', R.encode(dict(authority='NONE', status='UNKNOWN_NO_REPLAY',
                          pending=pending, automatic_retry=False, no_effect_inferred=False)))
        except BaseException: pass
        emit(dict(event='failure', status='UNKNOWN_NO_REPLAY')); return None
    finally: raw = None


class Journal:
    def __init__(self, path):
        self.path = Path(path)
        need(self.path.is_absolute() and self.path.parent.resolve(strict=True)==self.path.parent
             and self.path.is_relative_to(ROOT/'control-sessions') and not os.path.lexists(self.path), 'FRESH_ROOT_CONTROL_DIRECTORY')
        self.path.mkdir(mode=0o700)
        self.fd = os.open(self.path, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        self.identity = self.mark(os.fstat(self.fd)); self.names=set(); self.bytes=0
        self.check()
    @staticmethod
    def mark(s): return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid)
    def check(self):
        s=os.fstat(self.fd)
        need(self.mark(s)==self.identity==self.mark(self.path.lstat()) and s.st_uid==os.geteuid()
             and stat.S_IMODE(s.st_mode)==0o700 and not os.listxattr(self.fd)
             and set(os.listdir(self.fd))==self.names, 'CONTROL_JOURNAL_CUSTODY')
    def reserve(self, additional):
        self.check(); need(self.bytes+additional<=CAP and len(self.names)+3<=64, 'CONTROL_JOURNAL_CAPACITY')
    def write(self, name, raw):
        self.check(); need(type(raw) is bytes and re.fullmatch('[A-Za-z0-9_.-]{1,100}',name)
                          and name not in self.names and self.bytes+len(raw)<=CAP and len(self.names)<64, 'EXCLUSIVE_CONTROL_WRITE')
        fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
        try:
            os.fchmod(fd,0o600); view=memoryview(raw)
            while view:
                n=os.write(fd,view); need(n>0,'SHORT_WRITE');view=view[n:]
            os.fsync(fd)
        finally:os.close(fd)
        os.fsync(self.fd); fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=self.fd)
        try:
            before=os.fstat(fd); need(stat.S_ISREG(before.st_mode) and before.st_nlink==1
                and before.st_uid==os.geteuid() and stat.S_IMODE(before.st_mode)==0o600 and before.st_size==len(raw), 'CONTROL_WRITE_SHAPE')
            got=b''
            while len(got)<=len(raw):
                block=os.read(fd,min(65536,len(raw)+1-len(got)))
                if not block:break
                got+=block
            end=os.fstat(fd);named=os.stat(name,dir_fd=self.fd,follow_symlinks=False)
            mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
            need(got==raw and mark(before)==mark(end)==mark(named) and not os.listxattr(fd), 'CONTROL_WRITE_READBACK')
        finally:os.close(fd)
        self.names.add(name);self.bytes+=len(raw);self.check()
    def close(self):os.close(self.fd)


def read_owned(path, maximum, *, source=False):
    p=Path(path);need(p.is_absolute() and p.resolve(strict=True)==p and p.is_relative_to(ROOT), 'FIXED_ROOT_PATH')
    for parent in reversed(p.parents):
        need(stat.S_ISDIR(parent.lstat().st_mode) and not parent.is_symlink(), 'ROOT_ANCESTOR_ALIAS')
    before=p.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.geteuid()
        and stat.S_IMODE(before.st_mode) in ((0o400,0o444) if source else (0o400,0o600)) and 0<before.st_size<=maximum, 'ROOT_FILE_CUSTODY')
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        need(mark(os.fstat(fd))==mark(before),'ROOT_OPEN_CHANGED');raw=b''
        while len(raw)<=maximum:
            block=os.read(fd,min(65536,maximum+1-len(raw)))
            if not block:break
            raw+=block
        need(len(raw)==before.st_size and mark(os.fstat(fd))==mark(before)==mark(p.lstat()), 'ROOT_READ_CHANGED')
        return raw
    finally:os.close(fd)


def main(argv=None):
    need(os.name=='posix' and sys.platform=='linux' and os.getuid()==os.geteuid()>0
         and sys.flags.isolated and sys.dont_write_bytecode and sys.stdin.isatty(), 'ACTUAL_NONROOT_ISOLATED_ROOT_TTY_REQUIRED')
    args=sys.argv[1:] if argv is None else argv
    need(len(args)==4 and args[0]=='--configuration' and args[2]=='--configuration-sha256'
         and re.fullmatch('[0-9a-f]{64}',args[3]), 'ACTUAL_ROOT_CONFIGURATION_REQUIRED')
    config_raw=read_owned(args[1],65536);need(sha(config_raw)==args[3],'CONFIGURATION_PIN')
    c=parse(config_raw)
    need(set(c)=={'schema','issuer_thread','artifact_session','initial_session','initial_body','initial_publication',
         'body','parent_sha','parent_ref_result','deadline_unix_ms','journal_directory','admission'}
         and c['schema']=='dg16.g1-root-control-driver-configuration.v1' and c['issuer_thread']==ISSUER, 'EXACT_CONTROL_CONFIGURATION')
    def bound(row,maximum):
        need(type(row) is dict and set(row)=={'path','sha256'},'EXACT_INPUT_DESCRIPTOR')
        raw=read_owned(row['path'],maximum);need(sha(raw)==row['sha256'],'ACTUAL_ROOT_INPUT_PIN');return raw
    def current():need(type(c['deadline_unix_ms']) is int and 0<c['deadline_unix_ms']-time.time_ns()//1000000<=600000,'EXISTING_ROOT_DEADLINE')
    current();mods=[]
    for name,pin in (('receiver',RECEIVER_SHA),('resolve_artifact',RESOLVER_SHA)):
        path=ROOT/'author'/(name+'.py');raw=read_owned(path,1024**2,source=True);need(sha(raw)==pin,'ROOT_HELPER_SOURCE_PIN')
        m=types.ModuleType('root_control_'+name);m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);mods.append(m)
    R,X=mods;s=R.Sources()
    def received_session(path):
        p=Path(path);need(p.is_absolute() and p.resolve(strict=True)==p and p.is_relative_to(ROOT/'sessions'), 'SELECTED_ARTIFACT_SESSION')
        session=R.Session(p,s);saved=R.parse(R.read(p/'RECEIVING.json'));return session,saved
    previous=None;initial_control=None;initial_body=None
    if c['initial_session'] is not None:
        old,saved=received_session(c['initial_session']);previous=old.receive(saved['observed_unix_ms'],save=False)
        need(R.encode(previous['receipt'])==R.encode(saved),'INITIAL_ARTIFACT_RECEIVING_CHANGED')
        initial_body=bound(c['initial_body'],16384)
        published=R.parse(bound(c['initial_publication'],65536))
        need(published['phase']=='g3_initial' and published['context']==previous['context'] and published['root_body']==R.desc(initial_body)
             and published['artifact_receiving']==R.desc(R.encode(previous['receipt'])) and published['published_commit']==c['parent_sha'], 'ACTUAL_INITIAL_PUBLISHED_PARENT_JOIN')
        initial_control=dict(body=initial_body,receiving=previous,published_commit=published['published_commit'])
    session,saved=received_session(c['artifact_session'])
    received=session.receive(saved['observed_unix_ms'],previous=previous,save=False,actual_root_raw=initial_body)
    need(R.encode(received['receipt'])==R.encode(saved),'ACTUAL_ARTIFACT_RECEIVING_CHANGED')
    need(received['phase'] in ('tools','g3_initial','g3_final'),'CONTROL_PHASE_ONLY')
    if received['phase']=='g3_final':need(initial_control is not None,'ACTUAL_INITIAL_CONTROL_REQUIRED')
    else:need(c['initial_session'] is None and c['initial_body'] is None and c['initial_publication'] is None,'NO_UNRELATED_INITIAL_INPUTS')
    body=bound(c['body'],16384);now=time.time_ns()//1000000
    plan=R.publication_plan(s,received,body,c['parent_sha'],now,initial_control)
    parent_raw=bound(c['parent_ref_result'],4*1024**2);ref_call=R.control_read_plan(plan,'0'*40)[0]
    parent=R.unwrap_control(parent_raw,ref_call['arguments']['url'])
    need(parent.get('ref')=='refs/heads/'+plan['branch'] and parent.get('object',{}).get('type')=='commit'
         and parent['object']['sha']==c['parent_sha'],'ACTUAL_CONTROL_PARENT_REF')
    grant=parse(bound(c['admission'],65536))
    expected=dict(schema='dg16.g1-root-control-publication-admission.v1',issuer_thread=ISSUER,
        status='ADMIT_EXACT_THREE_GUARDED_CONTROL_WRITES_AND_READBACK',phase=received['phase'],context=received['context'],
        body=c['body'],artifact_receiving=R.desc(R.encode(received['receipt'])),parent_sha=c['parent_sha'],parent_ref_result=c['parent_ref_result'],
        plan_contract_sha256=R.sha(R.encode({k:v for k,v in plan.items() if k!='root_body_validation_at_unix_ms'})),
        journal_directory=c['journal_directory'],deadline_unix_ms=c['deadline_unix_ms'],
        tools=plan['supported_tool_order'],automatic_retry=False,original_awards=[])
    need(grant==expected and type(grant['deadline_unix_ms']) is int,'ACTUAL_ROOT_CONTROL_PUBLICATION_ADMISSION_REQUIRED')
    current();journal=Journal(c['journal_directory'])
    try:
        return 0 if run_publication(R,s,received,body,c['parent_sha'],c['deadline_unix_ms'],journal,
            lambda maximum,seconds:X.read_ephemeral_frame(maximum,seconds=seconds),
            lambda v:print(encode(v).decode(),end='',flush=True),initial_control=initial_control) is not None else 1
    finally:journal.close()


if __name__=='__main__':
    try:status=main()
    except BaseException:
        print('{"event":"failure","status":"UNKNOWN_NO_REPLAY"}',flush=True);status=1
    raise SystemExit(status)
