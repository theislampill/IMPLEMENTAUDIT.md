async (role) => {
 const runId=load("run").databaseId,jobId=load("job"),root='/home/agent/dg16-g2-current04-public-20261109/root-operation-driver-01';
 const obs=await tools.exec_command({cmd:"gh api repos/theislampill/IMPLEMENTAUDIT.md/actions/jobs/"+jobId+" --jq '{status,conclusion,steps:[.steps[]|{name,status,started_at,conclusion}]}'\ngh api repos/theislampill/IMPLEMENTAUDIT.md/actions/runs/"+runId+"/artifacts --jq '{total:.total_count,artifacts:[.artifacts[]|{id,name,size_in_bytes,digest,expired}]}'",max_output_tokens:5900});
 if(obs.exit_code!==0)throw Error('FRESH_GITHUB_READ_REQUIRED');
 const [job,listing]=obs.output.trim().split(/\r?\n/).map(x=>JSON.parse(x));const desired=(role==='live'?'dg16-full-correspondence-review-':'dg16-full-registry-')+runId+'-1';const rows=listing.artifacts.filter(a=>a.name===desired&&!a.expired);const hold=job.steps.find(s=>s.name.startsWith('Await actual independent review'));
 if(rows.length!==1||!/^sha256:[0-9a-f]{64}$/.test(rows[0].digest)||rows[0].size_in_bytes>262144||rows[0].size_in_bytes<1)throw Error('UNIQUE_ELIGIBLE_ROLE_ARTIFACT_REQUIRED');
 if(role==='live'&&!(job.status==='in_progress'&&hold?.status==='in_progress'))throw Error('ORIGINAL_LIVE_WINDOW_REQUIRED');if(role==='terminal'&&job.status!=='completed')throw Error('ACTUAL_TERMINAL_JOB_REQUIRED');
 const a=rows[0],sel={bytes:a.size_in_bytes,sha256:a.digest.slice(7),id:a.id};const limit=role==='live'?Date.parse(hold.started_at)+300000:0;
 const quote=s=>"'"+s.replaceAll("'","''")+"'";
 const code="import pathlib,hashlib,sys; p=pathlib.Path(sys.argv.pop(1));raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()=='a91b22c6ee25354f39160c4d83d0f2020430c14d41bbb6b5296c22a27ef7e782';exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})";
 const args=['C:\\Windows\\System32\\wsl.exe','-d','Ubuntu','-u','agent','--cd','/','--exec','/usr/bin/python3','-I','-B','-c',code,'/mnt/c/workspace/ai/improveimplementaudit/'+load('rolehelper'),role,JSON.stringify(sel),String(limit)];
 const grant=await tools.exec_command({cmd:"$PSNativeCommandArgumentPassing='Standard'; & "+args.map(quote).join(' ')+"; exit $LASTEXITCODE",max_output_tokens:450});
 if(grant.exit_code!==0){text({stage:'grant',exit:grant.exit_code,output:grant.output});return}
 const v=JSON.parse(grant.output);store('activeGrant'+role,v);const [d,m]=load('g2drv'),D=Function('return ('+d+')')(),make=Function('return ('+m+')')();const io=make(D,tools,{wslExe:'C:\\WINDOWS\\system32\\wsl.exe',distribution:'Ubuntu',user:'agent',installationRoot:root,role,configuration:root+'/'+role+'.configuration.json',admission:v.path});
 const verdict=await D.run({context:v.context,role:v.role,turn_id:v.turn_id,configuration_sha256:v.configuration_sha256,deadline_ms:v.deadline_ms},io);store('roleResult'+role,verdict);text({role,verdict,artifact:sel});
}
