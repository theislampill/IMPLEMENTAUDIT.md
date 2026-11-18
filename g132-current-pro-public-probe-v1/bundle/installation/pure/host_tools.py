# Exact bounded source projection; source module is never imported.
PROFILE='DEFERRED_SAME_HOST_FIXED_TOOLS_V1'

PATHS={'env':'/usr/bin/env','openssl':'/usr/bin/openssl'}

MAX_FILE=32*1024**2

MAX_BODY=65536

MAX_ARCHIVE=131072

MAX_OBSERVATION_SECONDS=60

MAX_ADOPTION_SECONDS=600

def declaration(binding):
    v=binding['host_tools']
    P.exact(v,('profile','paths','control_branch','control_parent','observation_seconds','adoption_seconds'))
    P.need(v['profile']==PROFILE and v['paths']==PATHS,'HOST_TOOLS_DEFERRED_DECLARATION')
    P.need(type(v['control_branch']) is str and P.re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',v['control_branch'])
      and '..' not in v['control_branch'] and '//' not in v['control_branch']
      and v['control_branch'] not in (binding['branch'],binding['control_branch']),'HOST_TOOLS_SEPARATE_RESERVED_REF')
    P.need(type(v['control_parent']) is str and P.re.fullmatch('[0-9a-f]{40}',v['control_parent'])
      and v['control_parent']!=binding['control_parent'],'HOST_TOOLS_SEPARATE_CONTROL_ANCESTRY')
    P.integer(v['observation_seconds'],1,MAX_OBSERVATION_SECONDS)
    P.integer(v['adoption_seconds'],1,MAX_ADOPTION_SECONDS)
    return v

def validate_adoption(raw,observation_raw,binding,now_ms):
    observation=P.parse(observation_raw,MAX_BODY);v=P.parse(raw,MAX_BODY)
    P.need(observation.get('schema')=='dg16.same-host-fixed-tool-observation.v2' and 'host_profile' in observation,'HOST_PROFILE_CHANGED')
    _profile_policy(binding).validate_g1_host_profile(observation['host_profile'])
    keys=('schema','issuer','successor','operation','context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256',
      'public_manifest_sha256','bootstrap_admission_sha256','observation','nonce','host_identity','tools','issued_unix_ms',
      'expires_unix_ms','command_scope','automatic_retry','crypto_capability_claim','core_or_native_effect_grant','original_awards','host_profile')
    P.exact(v,keys)
    wanted=dict(schema='dg16.same-host-fixed-tool-root-adoption.v2',issuer='R5_ROOT_GOVERNOR',successor='PRO-EXECUTOR-01, designated by owner',
      operation='ADOPT_FIXED_SAME_HOST_TOOL_BODIES',observation=P.descriptor(observation_raw),
      command_scope=['recipient','decrypt'],automatic_retry=False,crypto_capability_claim=False,
      core_or_native_effect_grant=False,original_awards=[])
    for key in ('context','source_commit','source_tree','carrier_binding_sha256','input_index_sha256',
      'public_manifest_sha256','bootstrap_admission_sha256','nonce','host_identity','tools','host_profile'):wanted[key]=observation[key]
    wanted.update(issued_unix_ms=v['issued_unix_ms'],expires_unix_ms=v['expires_unix_ms'])
    P.need(P.encode(v)==P.encode(wanted),'HOST_TOOL_ADOPTION_EXACT_JOIN')
    declared=declaration(binding)
    P.integer(v['issued_unix_ms'],observation['issued_unix_ms'],now_ms)
    P.integer(v['expires_unix_ms'],now_ms+1,observation['issued_unix_ms']+
      (declared['observation_seconds']+declared['adoption_seconds']+binding['limits']['acquisition_seconds'])*1000)
    return v

def check_observation_artifact(archive,snapshot,context,binding,expected_anchor,now_ms,*,workflow_representation=V.RAW_API_WORKFLOW):
    """Body-backed mechanical receiving; root's actual tool history is separate.

    The return value is deliberately incapable of becoming a command pin or
    root adoption. The root must consume authentic provider responses and
    issue the separate exact adoption itself after this closed join succeeds.
    """
    P.need(type(archive) is bytes and 0<len(archive)<=MAX_ARCHIVE,'HOST_TOOL_ARTIFACT_BOUND')
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            rows=z.infolist();P.need(len(rows)==1 and rows[0].filename=='HOST_TOOL_OBSERVATION.json'
              and not rows[0].is_dir() and not rows[0].flag_bits&1 and rows[0].compress_type in (0,8)
              and 0<rows[0].file_size<=MAX_BODY and (rows[0].external_attr>>16)&0o170000 in (0,0o100000),
              'HOST_TOOL_ARTIFACT_POPULATION')
            raw=z.read(rows[0]);P.need(len(raw)==rows[0].file_size,'HOST_TOOL_ARTIFACT_BODY')
    except (zipfile.BadZipFile,RuntimeError,OSError) as exc:raise ValueError('HOST_TOOL_ARTIFACT_CRC') from exc
    v=P.parse(raw,MAX_BODY);P.context(context);P.exact(snapshot,('run','attempt','jobs','artifact','artifacts','workflow'))
    P.need(len(P.encode(snapshot))<=P.MAX_METADATA,'HOST_TOOL_ROOT_METADATA_AGGREGATE')
    P.exact(v,('schema','authority','phase','context','source_commit','source_tree','carrier_binding_sha256',
      'input_index_sha256','public_manifest_sha256','bootstrap_admission_sha256','host_identity','directory_identity',
      'nonce','issued_unix_ms','tools','observation_elapsed_ns','command_executed','crypto_capability_claim','original_awards','host_profile'))
    P.need(v['schema']=='dg16.same-host-fixed-tool-observation.v2' and v['authority']=='NONE' and v['original_awards']==[],
      'HOST_TOOL_ROOT_OBSERVATION_SCHEMA')
    profile=_profile_policy(binding).validate_g1_host_profile(v['host_profile'])
    P.need(all(type(v['host_identity'][k]) is int and v['host_identity'][k]==profile['facts'][k] for k in ('uid','euid','gid','egid')),'HOST_TOOL_ROOT_HOST_IDENTITY')
    P.digest(v['nonce']);P.integer(v['issued_unix_ms'],0,now_ms)
    P.integer(v['observation_elapsed_ns'],0,declaration(binding)['observation_seconds']*10**9)
    P.exact(v['host_identity'],('uid','euid','gid','egid','boot_id'))
    P.need(v['host_identity']['uid']==v['host_identity']['euid']==0
      and type(v['host_identity']['boot_id']) is str and P.re.fullmatch('[0-9a-f-]{36}',v['host_identity']['boot_id']),
      'HOST_TOOL_ROOT_HOST_IDENTITY')
    P.exact(v['tools'],('env','openssl'))
    for tool,file in PATHS.items():
        item=v['tools'][tool];P.exact(item,('path','descriptor','physical'));P.exact(item['descriptor'],('bytes','sha256'))
        P.integer(item['descriptor']['bytes'],1,MAX_FILE);P.digest(item['descriptor']['sha256'])
        physical=item['physical'];P.exact(physical,('bytes','sha256','identity','ancestors'))
        P.need(item['path']==file and {k:physical[k] for k in ('bytes','sha256')}==item['descriptor']
          and type(physical['identity']) is list and len(physical['identity'])==9
          and all(type(n) is int and n>=0 for n in physical['identity'])
          and stat.S_ISREG(physical['identity'][2]) and physical['identity'][3]==1
          and physical['identity'][4]==item['descriptor']['bytes'] and physical['identity'][7]==0
          and physical['identity'][2]&0o022==0,'HOST_TOOL_ROOT_PHYSICAL_BODY')
        ancestors=physical['ancestors']
        P.need(type(ancestors) is list and len(ancestors)==3
          and all(type(r) is list and len(r)==6 and all(type(n) is int and n>=0 for n in r[1:]) for r in ancestors)
          and [r[0] for r in ancestors]==['/','/usr','/usr/bin']
          and all(stat.S_ISDIR(r[3]) and r[3]&0o022==0 and r[4]==0 for r in ancestors),
          'HOST_TOOL_ROOT_PHYSICAL_ANCESTRY')
    P.need(v.get('context')==context and v.get('source_commit')==binding['source_commit']
      and v.get('source_tree')==binding['source_tree'] and v.get('carrier_binding_sha256')==P.sha(binding['_binding_raw'])
      and v.get('input_index_sha256')==P.C.check_index(binding['_index'])
      and all(v.get(k)==expected_anchor[k] for k in ('public_manifest_sha256','bootstrap_admission_sha256'))
      and v.get('phase')=='READ_ONLY_FIXED_TOOL_BODIES' and v.get('command_executed') is False
      and v.get('crypto_capability_claim') is False,'HOST_TOOL_ROOT_ARTIFACT_BINDING')
    for name in ('run','attempt'):
        r=snapshot[name]
        P.need(r.get('id')==int(context['run_id']) and r.get('run_attempt')==1 and r.get('event')=='push'
          and r.get('status')=='in_progress' and r.get('head_branch')==context['branch']
          and r.get('head_sha')==context['workflow_commit'] and r.get('path')==context['workflow_path']
          and r.get('repository',{}).get('full_name')==P.REPOSITORY
          and r.get('head_repository',{}).get('full_name')==P.REPOSITORY
          and V.unix_ms(r.get('run_started_at'))<=v['issued_unix_ms'],'HOST_TOOL_ROOT_LIVE_RUN')
    repo=snapshot['run']['repository']['id'];P.integer(repo,1,10**20)
    P.need(all(snapshot[n][k].get('id')==repo for n in ('run','attempt') for k in ('repository','head_repository')),
      'HOST_TOOL_ROOT_REPOSITORY_ID')
    jobs=snapshot['jobs'];P.need(jobs.get('total_count')==1 and type(jobs.get('jobs')) is list and len(jobs['jobs'])==1,
      'HOST_TOOL_ROOT_SINGLE_JOB');job=jobs['jobs'][0]
    P.need(job.get('run_id')==int(context['run_id']) and job.get('run_attempt')==1 and job.get('head_sha')==context['workflow_commit']
      and job.get('name')==context['job_name'] and job.get('status')=='in_progress'
      and V.unix_ms(job.get('started_at'))<=v['issued_unix_ms'],'HOST_TOOL_ROOT_LIVE_JOB')
    a=snapshot['artifact'];r=a.get('workflow_run',{})
    P.need(a.get('name')=='dg16-core-host-tools-'+context['run_id']+'-a1' and a.get('expired') is False
      and a.get('size_in_bytes')==len(archive) and a.get('digest')=='sha256:'+P.sha(archive)
      and r.get('id')==int(context['run_id']) and r.get('head_sha')==context['workflow_commit']
      and r.get('head_branch')==context['branch'] and r.get('repository_id')==r.get('head_repository_id')==repo
      and local_artifact_chronology(snapshot,context,'tools',v['issued_unix_ms'],now_ms,V.unix_ms,V.workflow_body,binding['workflow_sha256'],workflow_representation),'HOST_TOOL_ROOT_ACTUAL_ARTIFACT')
    listing=snapshot['artifacts'];P.need(type(listing.get('artifacts')) is list and type(listing.get('total_count')) is int
      and listing['total_count']==len(listing['artifacts'])<=100
      and [r for r in listing['artifacts'] if r.get('name')==a['name']]==[a],'HOST_TOOL_ROOT_ARTIFACT_JOIN')
    V.workflow_body(snapshot['workflow'],context,binding['workflow_sha256'],representation=workflow_representation)
    return dict(schema='dg16.host-tool-mechanical-artifact-receiving.v1',authority='NONE',observation=P.descriptor(raw),
      artifact=P.descriptor(archive),artifact_id=a['id'],job_id=job['id'],context=context,
      authentic_root_tool_history_required=True,tool_adoption_issued=False,command_authority=False,original_awards=[])
