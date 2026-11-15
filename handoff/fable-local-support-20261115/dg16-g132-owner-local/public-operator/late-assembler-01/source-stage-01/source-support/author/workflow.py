"""Deterministic fixed-path workflow. No generated-body backpins in this file.

The actual immutable commit/tree is received by root before publication. The
external entries bind all generated data/implementation digests after workflow
rendering, so carrier.workflow_sha256 introduces no hash cycle.
"""
import json,re
WORKFLOW='.github/workflows/dg16-r5-g1-hosted-episode.yml'
CORE='qualification/dg16-r5-g1-hosted-episode'
ENTRY='qualification/dg16-r5-g1-hosted-entry'
CHECKOUT='actions/checkout@11d5960a326750d5838078e36cf38b85af677262'
UPLOAD='actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02'
REPO='theislampill/IMPLEMENTAUDIT.md'
STEPS=('initialize','discover','invalidate','read-state','read-roadmap','resume','verify','require','input-preflight','native-bank','prerequisites','g1','receive','g3-receive')

def need(v,c):
 if not v:raise ValueError(c)

def validate(selection):
 need(type(selection) is dict,'ROOT_SELECTION_REQUIRED')
 branch=selection['branch'];need(type(branch) is str and re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',branch) and '..' not in branch and '//' not in branch,'BRANCH_REQUIRED')
 t=selection['job_timeout_minutes'];reserve=selection['workflow_overhead_seconds']
 need(type(t) is int and t>0 and type(reserve) is int and reserve>0,'ROOT_SELECTED_TIMING_REQUIRED')
 limits=selection['carrier_limits'];host=selection['host_tools']
 for name,maximum in [('acquisition_seconds',600),('command_seconds',60),('command_cpu_seconds',60),('poll_seconds',15)]:
  need(type(limits[name]) is int and 1<=limits[name]<=maximum,'CARRIER_TIME_BOUND')
 for name,maximum in [('observation_seconds',60),('adoption_seconds',600)]:
  need(type(host[name]) is int and 1<=host[name]<=maximum,'HOST_TOOL_TIME_BOUND')
 # Recipient and receive run in separate processes; reserve both complete
 # acquisition ceilings rather than assuming overlap with the Pro sender.
 required=host['observation_seconds']+host['adoption_seconds']+2*limits['acquisition_seconds']+1800+60+reserve
 need(t*60>=required,'OUTER_JOB_BUDGET_INSUFFICIENT')
 return required

def root_command(entry,args='',token=False):
 names=('GITHUB_REPOSITORY','GITHUB_EVENT_NAME','GITHUB_REF','GITHUB_RUN_ATTEMPT','GITHUB_RUN_ID','GITHUB_SHA','GITHUB_JOB','GITHUB_WORKFLOW_SHA','GITHUB_WORKFLOW_REF','GITHUB_WORKSPACE','RUNNER_TEMP','ImageOS','ImageVersion')
 parts=['sudo /usr/bin/env -i PATH=/usr/bin:/bin LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC','GITHUB_ACTIONS=true RUNNER_ENVIRONMENT=github-hosted']
 parts.extend(n+'="$'+n+'"' for n in names)
 if token:parts.append('DG16_CARRIER_READ_TOKEN="$DG16_CARRIER_READ_TOKEN"')
 parts.append('/usr/bin/python3.12 -I -S -B "'+entry+'"'+(' '+args if args else ''))
 return ' \\\n  '.join(parts)

def render(selection):
 validate(selection);branch=selection['branch'];steps=[]
 def shell(name,body,**kw):
  step=dict(name=name,shell='bash',run='set -euo pipefail\ntest "$GITHUB_RUN_ATTEMPT" = 1\n'+body+'\n');step.update(kw);steps.append(step)
 def external(name,filename,token=False,**kw):
  cmd=root_command('$GITHUB_WORKSPACE/packet/'+ENTRY+'/'+filename,token=token)
  if token:kw['env']={'DG16_CARRIER_READ_TOKEN':'${{ github.token }}'}
  shell(name,cmd,**kw)
 def artifact(name,phase,members,artifact_name,condition=None):
  step=dict(name=name,uses=UPLOAD,with_={})
  step['with']=dict(name=artifact_name,**{'if-no-files-found':'error','retention-days':3,'compression-level':9,'path':'\n'.join('${{ runner.temp }}/dg16-g1-public-${{ github.run_id }}-a1/'+phase+'/'+n for n in members)})
  del step['with_']
  if condition:step['if']=condition
  steps.append(step)
 def core(step,always=False):
  args='--step '+step+' --source "/dg16-g1-$GITHUB_RUN_ID/source" --output "/dg16-g1-$GITHUB_RUN_ID/output"'
  shell('Core '+step,root_command('/dg16-g1-$GITHUB_RUN_ID/packet/run.py',args),**({'if':'always()'} if always else {}))
 def export(phase,always=False):
  shell('Export validated '+phase,root_command('$GITHUB_WORKSPACE/packet/'+ENTRY+'/public_export.py',phase)+ '\n'+
       'if test -d "$RUNNER_TEMP/dg16-g1-public-$GITHUB_RUN_ID-a1/'+phase+'"; then echo "eligible=true" >> "$GITHUB_OUTPUT"; else echo "eligible=false" >> "$GITHUB_OUTPUT"; fi',id='export_'+phase.replace('-','_'),**({'if':'always()'} if always else {}))
 steps.append(dict(name='Check out exact reviewed composition',uses=CHECKOUT,with_={}))
 steps[-1]['with']={'ref':'${{ github.sha }}','path':'packet','fetch-depth':1,'persist-credentials':False,'set-safe-directory':False,'submodules':False,'lfs':False};del steps[-1]['with_']
 external('Create exclusive fixed root island and exact packet','bootstrap_entry.py')
 for phase,entry in [('tools','host_tool_observe_entry.py'),('recipient','host_request_entry.py')]:
  if phase=='recipient':external('Receive separate actual root tool adoption','host_tool_adopt_entry.py',token=True)
  cmd=root_command('$GITHUB_WORKSPACE/packet/'+ENTRY+'/'+entry)+' | '+root_command('$GITHUB_WORKSPACE/packet/'+ENTRY+'/public_export.py',phase)
  shell('Observe host tools' if phase=='tools' else 'Create fresh recipient request',cmd)
  artifact('Retain actual host tool observation' if phase=='tools' else 'Retain fresh recipient request',phase,['HOST_TOOL_OBSERVATION.json'] if phase=='tools' else ['REQUEST.json','RECIPIENT.pem'],'dg16-core-host-tools-${{ github.run_id }}-a1' if phase=='tools' else 'dg16-core-private-recipient-${{ github.run_id }}-a1')
 external('Receive authenticated private inputs after actual root sender/control','host_receive_entry.py',token=True)
 external('Require private readiness and prepare original core','core_prepare_entry.py')
 for step in STEPS:core(step)
 export('root-request');artifact('Retain first actual G3 root request','root-request',['ROOT_REQUEST.json','SCOPE_RECEIVING.json','G1_RECEIVING.json','ARTIFACT_MANIFEST.json'],'dg16-g1-root-request-${{ github.run_id }}-1',"steps.export_root_request.outputs.eligible == 'true'")
 core('g3-consume')
 export('final-request');artifact('Retain second original receiving request','final-request',['FINAL_REQUEST.json','INDEPENDENT_PROOF_RECEIPT.json','ARTIFACT_MANIFEST.json'],'dg16-g1-original-request-${{ github.run_id }}-1',"steps.export_final_request.outputs.eligible == 'true'")
 core('g3-decide');core('finalize',True)
 export('terminal',True);artifact('Retain validated terminal summaries','terminal',['RESULT.json','HOST.json','SOURCE.json','OPERATION.json','G3.json','NSS.json','CLEANUP.json','FAILURE.json','ARTIFACT_MANIFEST.json'],'dg16-g1-hosted-${{ github.run_id }}-1',"always() && steps.export_terminal.outputs.eligible == 'true'")
 export('failure',True);artifact('Retain separately validated failure','failure',['RETENTION_FAILURE.json','ARTIFACT_MANIFEST.json'],'dg16-g1-retention-failure-${{ github.run_id }}-1',"always() && steps.export_failure.outputs.eligible == 'true'")
 value={'name':'R5 current original G1 and scoped two-stage G3','on':{'push':{'branches':[branch],'paths':[WORKFLOW,CORE+'/**',ENTRY+'/**']}},'permissions':{'contents':'read','actions':'read'},'concurrency':{'group':'dg16-r5-g1-final-${{ github.ref }}','cancel-in-progress':False},'jobs':{'qualify':{'if':"github.repository == '"+REPO+"' && github.event_name == 'push' && github.ref == 'refs/heads/"+branch+"' && github.event.deleted == false && github.run_attempt == '1'",'runs-on':'ubuntu-24.04','timeout-minutes':selection['job_timeout_minutes'],'steps':steps}}}
 return (json.dumps(value,sort_keys=False,indent=2)+'\n').encode()
