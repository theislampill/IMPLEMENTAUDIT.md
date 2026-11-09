"""Closed data-only receiving for one prospective maximum encrypt/capture test.

This validates evidence relationships, not acquisition authenticity, private-key
interoperability, a production same-host gate, or original DG16 acceptance.
"""
import hashlib,json,re,stat

PLAIN_MAX=268501016
CIPHER_MAX=268517400
COMPONENT_SEAL='9401f5b38a105b459301105b1f9dccb4badb908f5f92c30a35f7a551a5ef0786'
OWNER_SHA='79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'
RECIPIENT={'bytes':1464,'sha256':'5adbbeaf63e38116dcba9eb58af76b0fa056808649f9aa144e3f14dee838f4b8'}
PROFILE=('architecture','kernel','os','python_version','tools.bash','tools.bwrap','tools.git','tools.python3')
STAMP='dev ino mode nlink size mtime_ns ctime_ns uid gid'
class Refusal(ValueError):pass
def need(ok,code):
    if not ok:raise Refusal(code)
def encode(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('ascii')
def sha(x):return hashlib.sha256(x).hexdigest()
def digest(x):return type(x) is str and re.fullmatch('[0-9a-f]{64}',x) is not None
def exact(x,names):need(type(x) is dict and set(x)==set(names.split()),'FIELDS')
def integer(x,a,b):return type(x) is int and a<=x<=b
def desc(x,maximum):
    exact(x,'bytes sha256');need(integer(x['bytes'],0,maximum) and digest(x['sha256']),'DESCRIPTOR')

def limits_from_stdout(raw):
    need(type(raw) is bytes and 0<len(raw)<=1024 and raw.startswith(b'DG16_CMS_LIMITS ')
        and raw.count(b'\n')==1 and raw.endswith(b'\n'),'ACTUAL_LIMITS_LINE')
    def pairs(rows):
        out={}
        for k,v in rows:need(k not in out,'DUPLICATE_LIMIT_KEY');out[k]=v
        return out
    try:value=json.loads(raw[len(b'DG16_CMS_LIMITS '):],object_pairs_hook=pairs)
    except (ValueError,UnicodeError) as e:raise Refusal('LIMITS_JSON') from e
    exact(value,'schema address_space cpu file_size')
    need(value['schema']=='dg16.cms-child-actual-limits.v1','LIMITS_SCHEMA')
    need(raw==b'DG16_CMS_LIMITS '+encode(value),'LIMITS_CANONICAL')
    for name,ceiling in [('address_space',1024**3),('cpu',60),('file_size',CIPHER_MAX)]:
        v=value[name]
        need(type(v) is list and len(v)==2 and all(integer(n,1,ceiling) for n in v)
            and v[0]==v[1],'ACTUAL_LIMITS_BOUND')
    return value

def receive_descriptors(facts,command,owner,stdout,stderr_descriptor):
    exact(facts,'schema scope context component_seal source_manifest recipient profile_matches host_bookends tool_pins tool_bookends plain_before plain_after cipher cipher_type_checked files_removed currentness_bookends gate_clock authenticated_private_receiving original_acceptance')
    need(facts['schema']=='dg16.direct-encrypt-capture-qualification.v1'
        and facts['scope']=='MAXIMUM_ENCRYPT_CAPTURE_ONLY_NOT_A_PRODUCTION_GATE'
        and facts['component_seal']==COMPONENT_SEAL and digest(facts['source_manifest'])
        and facts['recipient']==RECIPIENT and facts['authenticated_private_receiving'] is False
        and facts['original_acceptance'] is False,'QUALIFICATION_SCOPE')
    c=facts['context'];exact(c,'repository ref run_id attempt head')
    need(c['repository']=='theislampill/IMPLEMENTAUDIT.md' and c['attempt']==1 and type(c['attempt']) is int
        and type(c['ref']) is str and c['ref'].startswith('refs/heads/pro/dg16-direct-encrypt-qualification-')
        and '..' not in c['ref'] and type(c['run_id']) is str and re.fullmatch('[1-9][0-9]{0,19}',c['run_id'])
        and type(c['head']) is str and re.fullmatch('[0-9a-f]{40}',c['head']) and c['head']!='0'*40,'ACTUAL_CONTEXT')
    matches=facts['profile_matches'];need(type(matches) is dict and set(matches)==set(PROFILE)
        and all(v is True for v in matches.values()),'ACTUAL_PROFILE')
    host=facts['host_bookends'];exact(host,'boot_opening boot_closing credentials_opening credentials_closing')
    need(all(digest(v) for v in host.values()) and host['boot_opening']==host['boot_closing']
        and host['credentials_opening']==host['credentials_closing'],'ACTUAL_HOST_IDENTITY_CLOSING')
    tools=facts['tool_pins'];books=facts['tool_bookends']
    need(type(tools) is dict and len(tools)==2 and '/usr/bin/openssl' in tools
        and type(books) is dict and set(books)==set(tools),'TOOL_POPULATION')
    need(len([n for n in tools if re.fullmatch('/usr/bin/python3\.[0-9]{1,2}',n)])==1,'SYSTEM_PYTHON')
    for name,pin in tools.items():
        desc(pin,32*1024**2);pair=books[name];exact(pair,'opening closing')
        opening=pair['opening'];exact(opening,STAMP)
        need(opening==pair['closing'] and all(type(n) is int and n>=0 for n in opening.values())
            and opening['nlink']==1 and opening['uid']==0 and opening['size']==pin['bytes']
            and stat.S_ISREG(opening['mode']) and not opening['mode']&0o022,'TOOL_PHYSICAL_CLOSING')
    desc(facts['plain_before'],PLAIN_MAX);desc(facts['plain_after'],PLAIN_MAX);desc(facts['cipher'],CIPHER_MAX)
    need(facts['plain_before']==facts['plain_after'] and facts['plain_before']['bytes']==PLAIN_MAX
        and 0<facts['cipher']['bytes']<=CIPHER_MAX and facts['cipher_type_checked'] is True,'MAXIMUM_INPUT_CIPHER')
    need(facts['files_removed']=={'FRAME.bin':True,'FAILED_STREAMS.cms':True,'recipient.pem':True}
        and facts['currentness_bookends'] is True,'QUALIFICATION_CLOSING')
    clock=facts['gate_clock'];exact(clock,'started stop ending')
    need(all(type(v) in (int,float) and 0<=v<10**12 for v in clock.values())
        and clock['stop']==clock['started']+60 and clock['started']<=clock['ending']<=clock['stop'],
        'QUALIFICATION_CLOCK')
    exact(command,'schema authority operation command capture returncode stdout stderr file_limit memory_limit cpu_limit deadline original_acceptance')
    need(command['schema']=='dg16.protected-stream-command.v1' and command['authority']=='NONE'
        and command['operation']=='encrypt' and command['original_acceptance'] is False
        and command['returncode']==0 and type(command['returncode']) is int
        and command['file_limit']==CIPHER_MAX and command['memory_limit']==1024**3
        and command['cpu_limit']==60 and command['deadline']==clock['stop'],'COMMAND_SCOPE_LIMITS')
    argv=command['command'];need(type(argv) is list and len(argv)==19 and all(type(v) is str for v in argv),'CLOSED_ARGV')
    expected=['/usr/bin/openssl','cms','-encrypt','-binary','-aes-256-gcm','-in',None,'-outform','DER','-out',None,
        '-recip',None,'-keyopt','rsa_padding_mode:oaep','-keyopt','rsa_oaep_md:sha256','-keyopt','rsa_mgf1_md:sha256']
    fds=[]
    for a,b in zip(argv,expected):
        if b is None:
            need(re.fullmatch('/proc/self/fd/[0-9]{1,7}',a),'HELD_FD_ARGUMENT')
            n=int(a.rsplit('/',1)[1]);need(3<=n<=2**20,'HELD_FD_BOUND');fds.append(n)
        else:need(a==b,'CLOSED_ARGV')
    need(len(set(fds))==3,'DISTINCT_HELD_FDS')
    limits=limits_from_stdout(stdout)
    desc(stderr_descriptor,32768)
    streams={'stdout':{'bytes':len(stdout),'sha256':sha(stdout)},'stderr':stderr_descriptor}
    for key,descriptor in streams.items():need(command[key]==descriptor,'COMMAND_STREAM_BINDING')
    rows=command['capture'];need(type(rows) is list and len(rows)==1,'CAPTURE_POPULATION');row=rows[0]
    exact(row,'name process_started pidfd_acquired returncode timeout output_bound_exceeded streams_complete internal_failure cleanup owner_evidence stdout_bytes stderr_bytes stdout_sha256 stderr_sha256')
    need(row['process_started'] is True and row['pidfd_acquired'] is True and row['streams_complete'] is True
        and row['returncode']==0 and row['timeout'] is False and row['output_bound_exceeded'] is False
        and row['internal_failure'] is None and row['cleanup']=={'echild':True,'restoration_complete':True},'CAPTURE_CLOSING')
    exact(owner,'schema authority source operation process_started pidfd_acquired before_close after_close mask_and_handlers_restored close_error started command_stop ending enclosing_deadline cleanup_seconds original_acceptance')
    need(owner['schema']=='dg16.failed-stream-command-owner.v1' and owner['authority']=='NONE'
        and owner['operation']=='encrypt' and owner['original_acceptance'] is False
        and owner['process_started'] is True and owner['pidfd_acquired'] is True
        and owner['mask_and_handlers_restored'] is True and owner['close_error'] is None,'OWNER_SCOPE')
    source=owner['source'];exact(source,'source_sha256 ast_sha256 instantiated scope')
    need(source['source_sha256']==OWNER_SHA and digest(source['ast_sha256']) and source['instantiated'] is True
        and source['scope']=='EXACT_ORDINARY_SINGLE_PROC_OWNER_CLASS; no maintained verifier or nested profile selected',
        'EXACT_OWNER_SOURCE')
    need(owner['after_close']['primary_exit']==0 and owner['after_close']['quiescence']=='ECHILD_ALL_CHILDREN'
        and owner['after_close']['flag_restored'] is True,'OWNER_TERMINAL')
    after=owner['after_close'];before=owner['before_close']
    fields='owner_pid primary_pid primary_exit owned_pidfd_signals live_children_refused quiescence flag_restored scope previous_subreaper'
    exact(after,fields+' other_child_exits');exact(before,fields+' other_child_exit_count')
    need(after['scope']==before['scope']=='DEDICATED_SINGLE_THREAD_LINUX_SUBREAPER; NO_FOREIGN_SAME_UID_WRITER_AUTHORITY'
        and integer(after['owner_pid'],1,2**31-1) and integer(after['primary_pid'],1,2**31-1)
        and after['owner_pid']!=after['primary_pid'] and after['owner_pid']==before['owner_pid']
        and after['primary_pid']==before['primary_pid'] and after['live_children_refused'] is False
        and integer(after['owned_pidfd_signals'],0,4096) and integer(after['previous_subreaper'],0,1)
        and integer(before['other_child_exit_count'],0,4096),'OWNER_STATUS_SCOPE')
    other=after['other_child_exits'];need(type(other) is list and len(other)<=4096,'OTHER_CHILD_BOUND')
    seen=set()
    for child in other:
        exact(child,'pid exit');need(integer(child['pid'],1,2**31-1) and integer(child['exit'],-255,255)
            and child['pid']!=after['primary_pid'] and child['pid'] not in seen,'OTHER_CHILD_STATUS');seen.add(child['pid'])
    for k in ['started','command_stop','ending','enclosing_deadline']:
        need(type(owner[k]) in (int,float) and 0<=owner[k]<10**12,'OWNER_CLOCK')
    need(owner['started']<owner['command_stop']<=owner['started']+60
        and owner['started']<=owner['ending']<=owner['enclosing_deadline']
        and clock['started']<=owner['started'] and owner['ending']<=clock['ending']
        and owner['enclosing_deadline']==clock['stop']
        and owner['command_stop']<=owner['enclosing_deadline']-3 and owner['cleanup_seconds']==3,'OWNER_ENCLOSURE')
    need(row['owner_evidence']=={'bytes':len(encode(owner)),'sha256':sha(encode(owner))},'OWNER_BINDING')
    for key,descriptor in streams.items():
        need(row[key+'_bytes']==descriptor['bytes'] and row[key+'_sha256']==descriptor['sha256'],'CAPTURE_STREAM_BINDING')
    return {'schema':'dg16.direct-encrypt-capture-data-receiving.v1','status':'RELATIONSHIPS_CHECKED_REQUIRES_ACTUAL_INDEPENDENT_RECEIVING',
        'context':c,'facts_sha256':sha(encode(facts)),'command_sha256':sha(encode(command)),'owner_sha256':sha(encode(owner)),
        'actual_limits':limits,'authenticated_private_receiving':False,'production_same_host_gate_received':False,'original_acceptance':False}

def receive(facts,command,owner,stdout,stderr):
    need(type(stderr) is bytes and len(stderr)<=32768,'STDERR_BOUND')
    return receive_descriptors(facts,command,owner,stdout,{'bytes':len(stderr),'sha256':sha(stderr)})

def receive_raw(facts,command,owner,stdout,stderr):
    def parse(raw,maximum):
        need(type(raw) is bytes and 0<len(raw)<=maximum,'RAW_RECEIVING_BOUND')
        def pairs(items):
            out={}
            for k,v in items:need(k not in out,'DUPLICATE_KEY');out[k]=v
            return out
        try:value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE')))
        except (ValueError,UnicodeError,RecursionError) as e:raise Refusal('RECEIVING_JSON') from e
        need(encode(value)==raw,'RECEIVING_CANONICAL');return value
    return receive(parse(facts,65536),parse(command,65536),parse(owner,262144),stdout,stderr)

def receive_public_result(result,expected_manifest):
    need(digest(expected_manifest),'EXPECTED_SOURCE_MANIFEST')
    exact(result,'schema status stage original_acceptance authenticated_private_receiving production_gate_received context tool_check facts command owner stdout_limits_hex stderr_descriptor receiving command_attempted elapsed_seconds last_capture')
    need(type(result) is dict and result.get('schema')=='dg16.direct-qualification-result.v1'
        and result.get('status')=='OBSERVED_ENCRYPT_CAPTURE_REQUIRES_INDEPENDENT_RECEIVING'
        and result.get('stage')=='COMPLETE' and result.get('original_acceptance') is False
        and result.get('authenticated_private_receiving') is False and result.get('production_gate_received') is False
        and result.get('command_attempted') is True and result.get('cleanup_unknown') is not True
        and type(result.get('elapsed_seconds')) in (int,float) and 0<=result['elapsed_seconds']<=60,
        'PUBLIC_RESULT_SUCCESS_JOIN')
    need(len(encode(result))<=65536 and result['facts']['source_manifest']==expected_manifest
        and result['context']==result['facts']['context'],'PUBLIC_SOURCE_CONTEXT')
    need(result['elapsed_seconds']>=result['facts']['gate_clock']['ending']-result['facts']['gate_clock']['started'],
        'PUBLIC_ELAPSED_ENCLOSURE')
    tool=result['tool_check'];exact(tool,'tool check result refusal errno canonical_equal')
    need(tool=={'tool':'python3','check':'COMPLETE','result':'PASSED','refusal':None,'errno':None,'canonical_equal':True},
        'PUBLIC_TOOL_CHECK')
    text=result['stdout_limits_hex'];need(type(text) is str and 0<len(text)<=2048
        and len(text)%2==0 and re.fullmatch('[0-9a-f]+',text),'PUBLIC_LIMITS_ENCODING')
    checked=receive_descriptors(result['facts'],result['command'],result['owner'],bytes.fromhex(text),result['stderr_descriptor'])
    need(checked==result['receiving'],'PUBLIC_RECEIVING_BINDING')
    last=result['last_capture'];exact(last,'process_started pidfd_acquired returncode cleanup internal_failure owner_descriptor')
    row=result['command']['capture'][0]
    need(all(last[k]==row[k] for k in ('process_started','pidfd_acquired','returncode','cleanup','internal_failure'))
        and last['owner_descriptor']==row['owner_evidence'],'PUBLIC_LAST_CAPTURE_BINDING')
    return dict(checked,acquisition_authenticity='REQUIRES_ACTUAL_PROVIDER_AND_EXACT_SOURCE_RECEIVING',
        raw_stderr_transferred=False,private_recipient_required_for_this_scope=False)
