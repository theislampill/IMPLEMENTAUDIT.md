"""Inert complete retained-artifact and native-diagnostic receiving. No original imports or execution."""
from pathlib import Path,PurePosixPath,PureWindowsPath
import ast,collections,datetime,hashlib,io,json,stat,traceback,urllib.request,zipfile
OUT=Path(__file__).parent
OP=Path('/workspace/scratch/9fad46324cc4/a4-operation-g0029')
SOURCE=Path('/workspace/scratch/9fad46324cc4/a4-observation-g0029')
RAW=OP/'actual/ORIGINAL_ARTIFACT.zip'
def digest(b):return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()}
def load(p):return json.loads(Path(p).read_bytes())
def safe_zip(z):
    names=z.namelist();assert len(names)==len(set(names))
    for i in z.infolist():
        p=PurePosixPath(i.filename)
        assert i.filename and not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename and not PureWindowsPath(i.filename).drive
        assert not i.flag_bits&1 and not i.is_dir() and stat.S_IFMT(i.external_attr>>16) in (0,stat.S_IFREG)
        z.read(i.filename) # Complete CRC check, including unselected members.
    return set(names)
def get(path):
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com/repos/theislampill/IMPLEMENTAUDIT.md/'+path,headers={'User-Agent':'implementaudit-independent-diagnostic-receiving'}),timeout=20) as r:return json.loads(r.read(3000000))
def run():
    admission=load(OP/'ROOT_DIAGNOSTIC_ADMISSION.json');download=load(OP/'actual/DOWNLOAD_RECEIPT.json');raw=RAW.read_bytes();ident=digest(raw)
    assert ident['bytes']==1957965 and ident['sha256']=='d1e6fe87bed955906d6a79736de2fcd1bd69cca9063ccf70bb60b5ade38ea133'
    assert all(download[k]==ident[k] for k in ('bytes','sha256')) and download['artifact_id']==14674376366 and download['download_count']==1
    run=json.loads(load(OUT/'PROVIDER_RUN.json')['raw_provider_text']);jobs=json.loads(load(OUT/'PROVIDER_JOBS.json')['raw_provider_text'])['jobs'];assert len(jobs)==1;jobprovider=jobs[0]
    assert run['id']==44826546712 and run['run_attempt']==1 and run['event']=='push' and run['head_sha']=='f0d76746a7abbcf92888a82827ba8a8c71a4074f'
    assert run['status']=='completed' and run['conclusion']=='failure' and jobprovider['id']==136600491721 and jobprovider['conclusion']=='failure'
    with zipfile.ZipFile(io.BytesIO(raw)) as outer:
        assert safe_zip(outer)=={'FINAL_ZIP_RECEIPT.json','RETAINED_EVIDENCE.zip'}
        receipt=json.loads(outer.read('FINAL_ZIP_RECEIPT.json'));inner=outer.read('RETAINED_EVIDENCE.zip');assert digest(inner)==receipt['archive']
    with zipfile.ZipFile(io.BytesIO(inner)) as z:
        names=safe_zip(z)
        def read(n):return z.read(n)
        def j(n):return json.loads(read(n))
        manifest=j('FINAL_MANIFEST.json');assert digest(read('FINAL_MANIFEST.json'))==receipt['manifest']
        rows=manifest['members'];assert len(rows)==manifest['member_count'] and len({r['path'] for r in rows})==len(rows)
        assert {r['path'] for r in rows}|{'FINAL_MANIFEST.json'}==names and len(names)==receipt['members_including_manifest']
        for r in rows:assert digest(read(r['path']))=={k:r[k] for k in ('bytes','sha256','git_blob')}
        assert sum(r['bytes'] for r in rows)==manifest['member_bytes']
        assert manifest['not_followed_entries']==[] and manifest['observation_errors']==[] and receipt['not_followed_count']==receipt['observation_error_count']==0
        before=j('SOURCE_BEFORE.json');after=j('SOURCE_AFTER_WORKER.json');assert read('SOURCE_BEFORE.json')==read('SOURCE_AFTER_WORKER.json') and before['git_status']==''
        assert before['source_member_count']==len(before['source_members'])==52 and before['source_commit']==admission['source_parent'] and before['source_tree']==admission['product_tree']
        tree=get('git/trees/'+admission['product_tree']+'?recursive=1');assert tree['sha']==admission['product_tree'] and not tree['truncated']
        leaves={e['path']:e for e in tree['tree'] if e['type']!='tree'};assert len(leaves)==1785
        for r in before['source_members']:assert (r['git_blob'],r['mode'],r['bytes'])==(leaves[r['path']]['sha'],leaves[r['path']]['mode'],leaves[r['path']]['size'])
        pre=j('PREFLIGHT.json');plan=j('EXECUTE_INTENT.json');worker=j('WORKER_ATTEMPT.json');idx=j('capture/INDEX.json');measurement=j('windows-job/measurement.json')
        source_digest=digest((SOURCE/'capture.py').read_bytes());assert source_digest['sha256']=='c16fd3a8d8adef7ab87a5916d45cf62d66deb89e90fe3e1031e0d1945c53e656'
        for b in [pre,plan]:
            assert b['helper']==source_digest and b['run_id']==run['id'] and b['attempt']==1 and b['workflow_commit']==run['head_sha']
            assert b['workflow_tree']==admission['expected_host_tree'] and b['workflow_parent']==admission['source_parent'] and b['source_before']==digest(read('SOURCE_BEFORE.json'))
            assert b['host_predicates']['GITHUB_REF']=='refs/heads/'+admission['branch'] and b['host_predicates']['RUNNER_OS']=='Windows' and b['host_predicates']['RUNNER_ENVIRONMENT']=='github-hosted'
        assert plan['one_worker_only'] and worker['plan']==digest(read('EXECUTE_INTENT.json')) and measurement['command']==plan['command'] and measurement['root_pid']==worker['pid']==8168
        for k in ['started_suspended','assigned_before_resume','root_job_membership_confirmed','completion_port_associated_before_assignment','complete_memory_scope_valid','cleanup_complete']:assert measurement[k] is True
        assert measurement['exit_code']==1 and measurement['status']=='COMPLETE_UNADMITTED' and measurement['platform']=='win32' and measurement['terminal_active_processes']==0 and measurement['terminal_breakaway_allowed'] is False
        assert measurement['initial_job_flags']==measurement['terminal_job_flags']==0x2000 and measurement['baseline_subtracted_bytes']==0
        active=set();births=[];exits=[];zeros=0
        for e in measurement['process_events']:
            pid=e['pid']
            if e['event']=='NEW_PROCESS':assert pid not in active;active.add(pid);births.append(pid)
            elif e['event']=='EXIT_PROCESS':assert pid in active;active.remove(pid);exits.append(pid)
            elif e['event']=='ACTIVE_PROCESS_ZERO':assert not active;zeros+=1
            else:raise AssertionError('unexpected process event '+str(e))
        assert not active and len(births)==len(exits)==measurement['kernel_total_processes']==measurement['creation_event_count']==measurement['exit_event_count']==1222 and zeros==1
        observed=measurement['observed_processes'];assert [r['pid'] for r in observed]==births and all(r['in_job'] for r in observed) and measurement['process_observation_failures']==[]
        spelling=lambda s:str(PureWindowsPath(s)).casefold()
        for key in ['python','git','bash','cmd']:
            tool=before['tools'][key];assert any(spelling(r['image'])==spelling(tool['path']) and r['image_sha256']==tool['sha256'] and (key!='python' or r['pid']==worker['pid']) for r in observed)
        original=ast.parse((SOURCE/'capture.py').read_text());methods=next(ast.literal_eval(n.value) for n in original.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ORIGINAL_METHODS' for t in n.targets));expected=['.'.join((f[:-3],c,m)) for f,c,m in methods]
        outcomes=j('capture/OUTCOMES.json');assert outcomes['tests_run']==28 and outcomes['success'] is False and [r['id'] for r in outcomes['rows']]==expected
        assert collections.Counter(r['outcome'] for r in outcomes['rows'])=={'SUCCESS':24,'SKIP':1,'ERROR':3} and outcomes['failures']==[] and len(outcomes['errors'])==3
        assert [r[0] for r in outcomes['errors']]==expected[-3:] and all('process peak memory exceeds frozen bound; no publication authorised' in r[1] for r in outcomes['errors'])
        assert outcomes['skipped']==[[pre['optional_exact_short_alias_skip'],'this volume did not provide a distinct 8.3 alias']]
        assert j('capture/WORKER_ERROR.json')['recorded_outcomes']==outcomes['rows']==idx['outcomes']
        assert j('EXECUTION_ERROR.json')['text']=='Windows Job conjunction absent: exit_code' and 'RESULT.json' not in names and 'capture/CONTROL_RECEIVING.json' not in names
        cleanup=j('capture/CLEANUP.json');terminal=j('capture/PROCESS_TERMINAL.json');assert cleanup['unexpected_remaining_fixture_paths']==[] and cleanup['original_cleanup_delegated_unchanged'] and terminal['survivors']==[] and idx['source_unchanged']
        for r in terminal['processes']:
            assert not r.get('still_running') and r['pid'] in births and type(r['terminal_returncode']) is int
            stem='capture/processes/'+f"{r['index']:05d}";intent=j(stem+'.intent.json');started=j(stem+'.started.json')
            assert all(started[k]==v for k,v in intent.items()) and all(r[k]==v for k,v in started.items())
        assert len(terminal['processes'])==idx['processes']==206 and [r['index'] for r in terminal['processes']]==list(range(1,207))
        commands=[];nonzero=0;stream_bytes=0
        for i in range(1,idx['commands']+1):
            prefix=f'capture/commands/{i:05d}/';intent=j(prefix+'INTENT.json');ends=[n for n in ['RETURN.json','EXCEPTION.json'] if prefix+n in names];assert len(ends)==1
            end=j(prefix+ends[0]);assert all(end[k]==v for k,v in intent.items()) and end['index']==i and end['started_ns']<=end['ended_ns']
            for key,file in [('stdin','stdin.bin'),('stdout','stdout.bin'),('stderr','stderr.bin'),('stdout_partial','stdout.partial.bin'),('stderr_partial','stderr.partial.bin')]:
                if end.get(key) is not None:assert digest(read(prefix+file))==end[key];stream_bytes+=end[key]['bytes']
            nonzero+=int(end.get('exit_code',0)!=0);commands.append(end)
        assert len({n.split('/')[2] for n in names if n.startswith('capture/commands/')})==idx['commands']==194
        eventnames=sorted(n for n in names if n.startswith('capture/events/'));snapshotnames=sorted(n for n in names if n.startswith('capture/snapshots/'))
        assert len(eventnames)==idx['events']==188 and len(snapshotnames)==idx['snapshots']==285
        refs=0
        def receive_refs(v):
            nonlocal refs
            if isinstance(v,dict):
                if {'path','bytes','sha256','git_blob'}.issubset(v) and str(v['path']).startswith('blobs/'):
                    assert digest(read('capture/'+v['path']))=={k:v[k] for k in ('bytes','sha256','git_blob')};refs+=1
                for value in v.values():receive_refs(value)
            elif isinstance(v,list):
                for value in v:receive_refs(value)
        snapshots=[];unavailable=0;enumeration_errors=0
        for i,n in enumerate(eventnames,1):r=j(n);assert r['index']==i;receive_refs(r)
        for i,n in enumerate(snapshotnames,1):
            r=j(n);assert r['index']==i and len({v['path'] for v in r['members']})==len(r['members']);receive_refs(r);snapshots.append(r);unavailable+=sum(v['kind']=='OBSERVATION_UNAVAILABLE' for v in r['members']);enumeration_errors+=len(r['enumeration_errors'])
        for r in terminal['processes']+commands:receive_refs(r)
        nativefiles=sorted(n for n in names if n.startswith('capture/native-memory/'));assert len(nativefiles)<=450
        summary=j('capture/native-memory/SUMMARY.json');samples=[]
        for n in nativefiles:
            assert len(read(n))<=4096
            if not n.endswith('SUMMARY.json'):samples.append(j(n))
        assert len(samples)==summary['requests']==summary['successful_records']==summary['retained_records']==342 and summary['errors']==0 and summary['first_error'] is None
        assert summary['pid']==worker['pid'] and summary['record_limit']==449 and summary['record_bytes_limit']==4096 and summary['observer_overhead_included'] and not summary['original_guard_changed'] and summary['native_historical_R3_peak']=='UNKNOWN'
        assert [r['sequence'] for r in samples]==list(range(1,343));assert all(a['observed_ns']<=b['observed_ns'] for a,b in zip(samples,samples[1:]))
        for r in samples:
            assert r['pid']==worker['pid'] and r['status']=='OBSERVED_NATIVE' and r['structure_bytes']==72 and r['size_t_bytes']==8 and r['original_limit_bytes']==67108864 and r['limit_changed'] is False
            for k in ['working_set_bytes','peak_working_set_bytes','pagefile_bytes','peak_pagefile_bytes','page_fault_count']:assert type(r[k]) is int and r[k]>=0
            assert r['peak_working_set_bytes']>=r['working_set_bytes'] and r['peak_pagefile_bytes']>=r['pagefile_bytes']
        assert all(a['peak_working_set_bytes']<=b['peak_working_set_bytes'] for a,b in zip(samples,samples[1:]))
        assert [r['case'] for r in samples if r['label']=='test-start']==expected==[r['case'] for r in samples if r['label']=='test-stop']
        for case in expected:
            for phase in ['_callSetUp','_callTestMethod','_callTearDown','doCleanups']:
                assert [r['label'] for r in samples if r['case']==case and r['phase']==phase and r['label'].startswith('lifecycle-')]==['lifecycle-before','lifecycle-after']
        snapshot_samples=[r for r in samples if r['label'].startswith('snapshot-')];assert len(snapshot_samples)==48
        assert collections.Counter(r['case'] for r in snapshot_samples)=={case:16 for case in expected[-3:]} and summary['snapshot_omitted_by_bound']==10
        for case in expected[-3:]:assert summary['affected_snapshot_requests'][case]==2*sum(r['case']==case for r in snapshots)
        assert samples[0]['label']=='before-original-imports' and samples[-1]['label']=='after-original-cleanup' and worker['started_ns']<=samples[0]['observed_ns']
        cross=next(i for i,r in enumerate(samples) if r['peak_working_set_bytes']>67108864);crossing=samples[cross-1:cross+1]
        nearby=[r for r in commands if r['started_ns']>=crossing[0]['observed_ns'] and r['ended_ns']<=crossing[1]['observed_ns']]
        bounded_details=[{'sequence':r['sequence'],'case':r['case'],'phase':r['phase'],'label':r['label'],'observed_ns':r['observed_ns'],'working_set_bytes':r['working_set_bytes'],'peak_working_set_bytes':r['peak_working_set_bytes']} for r in samples]
        (OUT/'NATIVE_OBSERVATIONS.json').write_text(json.dumps({'raw_artifact':ident,'summary':summary,'all_samples':samples,'first_crossing':crossing,'commands_inside_crossing_interval':nearby,'limits':['New-worker measurements include observer overhead','Historical R3 native peak remains unknown','No per-allocation attribution or A4 award']},indent=2)+'\n')
        result={'schema':'dg18.a4.complete-retained-diagnostic-receiving.v1','observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'raw_artifact':ident,'inner_archive':receipt['archive'],'outer_members':2,'inner_members':len(names),'inner_uncompressed_bytes':sum(z.getinfo(n).file_size for n in names),'payload_count':len(rows),'payload_bytes':manifest['member_bytes'],'full_crc_hash_git_population_closed':True,'source_members':52,'source_before_after_byte_equal':True,'source_census_digest':digest(read('SOURCE_BEFORE.json')),'native_worker_pid':worker['pid'],'job_kernel_births':len(births),'job_kernel_exits':len(exits),'job_terminal_active':0,'observed_images':len(observed),'job_sampled_pid_census_complete_preserved':measurement['sampled_pid_census_complete'],'job_exit':measurement['exit_code'],'original_tests':28,'original_outcomes':dict(collections.Counter(r['outcome'] for r in outcomes['rows'])),'original_error_ids':[r[0] for r in outcomes['errors']],'command_records':len(commands),'nonzero_commands':nonzero,'command_stream_bytes_received':stream_bytes,'terminal_popen_records':206,'events':188,'snapshots':285,'content_references_verified':refs,'snapshot_unavailable_file_observations':unavailable,'snapshot_enumeration_errors':enumeration_errors,'nested_fixture_archives':len([n for n in names if n.endswith('.zip')]),'native_samples':len(samples),'native_files_including_summary':len(nativefiles),'native_errors':summary['errors'],'max_native_file_bytes':max(len(read(n)) for n in nativefiles),'native_snapshot_omissions':10,'first_sample':bounded_details[0],'first_crossing':crossing,'final_sample':bounded_details[-1],'commands_inside_crossing_interval':[{'index':r['index'],'args':r['args'],'exit_code':r.get('exit_code'),'started_ns':r['started_ns'],'ended_ns':r['ended_ns']} for r in nearby],'provider_run':run['id'],'provider_job':jobprovider['id'],'provider_completed_at':jobprovider['completed_at'],'provider_conclusion':'failure','diagnostic_disposition':'AUTHENTIC_BOUNDED_OBSERVATIONS_RECEIVED_FAILURES_PRESERVED','A4_award':None,'full_original_A4_contract_available':False,'historical_R3_peak':'UNKNOWN','provider_writes':0,'new_downloads':0,'original_executions':0,'product_imports':0}
        (OUT/'RECEIVING.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    try:run()
    except BaseException as exc:
        (OUT/'RECEIVING_FAILURE_1.json').write_text(json.dumps({'type':type(exc).__name__,'text':str(exc),'traceback':traceback.format_exc(),'scope':'inert receiver construction, not original replay'},indent=2)+'\n');raise
