"""Owned synthetic fixture definitions adapted from the sealed independent F02 fixture.
No old check groups are imported or executed; all writes are caller-owned scratch.
"""
import contextlib, hashlib, importlib.util, io, json, os, pathlib, sys
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from unittest import mock
ROOT=pathlib.Path(sys.argv[1]).resolve()
SCRATCH=pathlib.Path(sys.argv[2]).resolve()
SCRATCH.mkdir(parents=True,exist_ok=True)
SCRIPTS=ROOT/'skills/implementaudit/scripts'
def effect_guard(event, args):
    if event in ('subprocess.Popen', 'os.system') or event.startswith('socket.'):
        raise AssertionError('PROHIBITED_EXTERNAL_EFFECT ' + event)
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        path = pathlib.Path(os.fsdecode(args[0])).absolute()
        if (args[2] or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            assert path.is_relative_to(SCRATCH), ('OUTSIDE_FIXTURE_WRITE', str(path))
    if event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.rename', 'os.link', 'os.symlink'):
        for item in args[:2] if event in ('os.rename', 'os.link', 'os.symlink') else args[:1]:
            assert pathlib.Path(item).absolute().is_relative_to(SCRATCH), ('OUTSIDE_FIXTURE_MUTATION', str(item))
sys.addaudithook(effect_guard)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
owner=module('independent_owner',SCRIPTS/'compaction-audit-pending.py');obs=owner.OBSERVATION;core=owner.CORE
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def pin(p):
    raw=pathlib.Path(p).read_bytes();return {'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def put(p,v):
    p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as stream:stream.write(canonical(v)+b'\n')
    return pin(p)
class Fixture:
    def __init__(self,name,inherited=0):
        self.root=SCRATCH/name;self.root.mkdir();self.store=self.root/'custody'
        target=self.root/'target';target.mkdir();(target/'run').mkdir();(target/'common').mkdir()
        self.home=self.root/'home';(self.home/'sessions').mkdir(parents=True)
        self.session='independent-root';self.child='heldout-child';self.owner='independent-owner'
        os.environ['CODEX_HOME']=str(self.home)
        with contextlib.redirect_stdout(io.StringIO()):
            core.command_init(SimpleNamespace(store=str(self.store),owner_id=self.owner))
            core.command_bind(SimpleNamespace(store=str(self.store),owner_id=self.owner,host_id='codex',host_session_id=self.session,
                controller_id='fixture-controller',claim_id='fixture-claim',explicit_run_root=str(target/'run'),
                repository_identity=str(target),git_common_directory_identity=str(target/'common'),worktree_identity=str(target),
                activation_event_id='fixture-activation',activation_receipt='fixture-receipt',continuity_generation='G0001',continuity_receipt='fixture-continuity'))
        self.tick=0;self.ordinal={'parent':0,'child':0};self.line={'parent':0,'child':0}
        self.logs={r:self.home/'sessions'/('rollout-'+n+'.jsonl') for r,n in [('parent',self.session),('child',self.child)]}
        pm=self.row('parent','session_meta',{'id':self.session,'session_id':self.session,'originator':'Codex Desktop','cli_version':'0.153.4','source':'vscode','thread_source':'user'})
        cm=self.row('child','session_meta',{'id':self.child,'session_id':self.session,'parent_thread_id':self.session,'forked_from_id':self.session,
            'originator':'Codex Desktop','cli_version':'0.153.4','thread_source':'subagent','agent_path':'/root/'+self.child,'subagent_history_start_ordinal':23,
            'source':{'subagent':{'thread_spawn':{'parent_thread_id':self.session,'agent_path':'/root/'+self.child}}}})
        for _ in range(inherited):self.message('child','Inherited physical history')
        self.ordinal['child']=23
        opened=self.message('parent','```ini\nCHILD_TASK='+self.child+'\nCHILD_SKILL_SELECTED=audit-state\nSTATUS=OPEN\nLOAD=UNVERIFIED\n```')
        spawned=self.row('parent','response_item',{'type':'function_call','namespace':'collaboration','name':'spawn_agent','call_id':'spawn-review',
            'arguments':json.dumps({'task_name':self.child,'message':'synthetic fixture notification'})})
        response=self.row('parent','response_item',{'type':'function_call_output','call_id':'spawn-review','output':json.dumps({'task_name':'/root/'+self.child})})
        self.context={r:{'path':str(self.logs[r]),'metadata':m,'allowed_ranges':[{'offset':0,'bytes':2*1024*1024}]} for r,m in [('parent',pm),('child',cm)]}
        self.context.update(open=opened,spawn_call=spawned,spawn_output=response)
        self.op('resume')
    def row(self,role,kind,payload):
        self.tick+=1;self.line[role]+=1
        raw=canonical({'timestamp':(datetime(2026,9,10,tzinfo=timezone.utc)+timedelta(seconds=self.tick)).isoformat(),'ordinal':self.ordinal[role],'type':kind,'payload':payload})+b'\n'
        path=self.logs[role];offset=path.stat().st_size if path.exists() else 0
        with path.open('ab') as stream:stream.write(raw)
        self.ordinal[role]+=1
        return {'offset':offset,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'embedded_ordinal':self.ordinal[role]-1,'physical_line':self.line[role]}
    def message(self,role,text,phase='commentary'):
        return self.row(role,'response_item',{'type':'message','id':'msg-'+str(self.tick),'role':'assistant','phase':phase,'content':[{'type':'output_text','text':text}]})
    def typed(self,role,value,phase='commentary'):return self.message(role,'```json\n'+json.dumps(value,sort_keys=True)+'\n```',phase)
    def begin_exchange(self,command):
        identifier='call-'+str(self.tick)
        c=self.row('child','response_item',{'type':'custom_tool_call','name':'exec','call_id':identifier,'status':'completed','input':command})
        return {'call':c,'call_id':identifier}
    def end_exchange(self,pending,output,exit_code=0):
        identifier=pending['call_id']
        r=self.row('child','response_item',{'type':'custom_tool_call_output','call_id':identifier,'output':[
            {'type':'input_text','text':'Script completed\nOutput:\n'},
            {'type':'input_text','text':json.dumps({'chunk_id':identifier,'wall_time_seconds':0.1,'exit_code':exit_code,'original_token_count':100,'output':output})}]})
        return {'call':pending['call'],'result':r}
    def exchange(self,command,output):
        return self.end_exchange(self.begin_exchange(command),output)
    def op(self,action,value=None):
        os.environ['CODEX_HOME']=str(self.home)
        return owner.operate(self.store,self.session,self.owner,action,value)
    def cli(self,action,value):
        args=['compaction-audit-pending.py','--store',str(self.store),'--session',self.session,'--owner-id',self.owner,action]
        stream=io.TextIOWrapper(io.BytesIO(canonical(value)));out=io.StringIO()
        with mock.patch.object(sys,'argv',args),mock.patch.object(sys,'stdin',stream),contextlib.redirect_stdout(out):rc=owner.main()
        return rc,json.loads(out.getvalue())
    def state(self):return owner.load(self.store,self.session)
    def statebytes(self):return owner.state_path(self.store,self.session).read_bytes()
    def reserve(self):
        return self.op('reserve',{'child_id':self.child,'bounded_purpose':'Independent cold fixture only; no origin or runtime credit.','observation_source':self.context})
    def authorize(self,reserved):
        skill=owner.selected_audit_state_pin();raw=pathlib.Path(skill['path']).read_bytes()
        load=self.exchange(obs.load_tool_input(skill),json.dumps({**skill,'utf8':raw.decode()}))
        context=self.state()['assignments'][self.child]['observation_source']
        identities={k:obs.resolve_record(context,'child',v)[1] for k,v in load.items()}
        route=self.message('parent','```ini\nCHILD_TASK='+self.child+'\nCHILD_SKILL_ROUTE=audit-state\nLOAD=VERIFIED\n```')
        o=reserved['obligation'];u={'schema':'implementaudit.compaction-use-authorization.v1','action':'AUTHORIZE_BOUNDED_POST_COMPACTION_RECONCILIATION',
            'parent_identity':o['parent_identity'],'actual_child_identity':o['actual_child_identity'],'obligation_digest':reserved['obligation_digest'],
            'observation_id':o['observation_id'],'load_observation_identity':obs.digest(obs.canonical(identities)),'selected_child':'audit-state','skill_source_pin':skill,'authority_ceiling':'NONE'}
        return {'load_call':load['call'],'load_output':load['result'],'route':route,'authorization':self.typed('parent',u)}
    def bind(self,early_use=False):
        self.reserved=self.reserve();r=self.reserved
        deliver={'child_id':self.child,'phase':'deliver','observation_id':r['obligation']['observation_id'],'authorization_evidence':self.authorize(r)}
        self.packet=self.op('observe-child',deliver)
        assert not self.state()['assignments'][self.child]['observations']
        exchange=self.exchange(obs.delivery_tool_input(self.store,self.session,self.owner,deliver),json.dumps(self.packet))
        if early_use:self.early=self.exchange('text("Substantive audit work before mechanical bind completed");','Premature substantive work completed')
        bind={'child_id':self.child,'phase':'bind','observation_id':deliver['observation_id'],'exchange':exchange}
        pending=self.begin_exchange(obs.delivery_tool_input(self.store,self.session,self.owner,bind))
        rc,self.observed=self.cli('observe-child',bind)
        assert rc==0,self.observed
        self.bound=self.end_exchange(pending,json.dumps(self.observed))
        return r,self.observed
    def result_request(self,members=None,status='SUCCEEDED'):
        r=self.reserved;o=r['obligation'];observed=self.observed
        use=self.exchange('// COMPACTION_OBSERVATION_EXCHANGE='+observed['child_observation_exchange_identity']+'\ntext("Independent bounded work");','Independent bounded work')
        directory=self.root/'result';directory.mkdir()
        if members is None:members=[put(directory/'finding.json',{'finding':'synthetic evidence only'})]
        bindings={'obligation_digest':r['obligation_digest'],'observation_id':o['observation_id'],
            'child_observation_exchange_identity':observed['child_observation_exchange_identity'],'exact_observed_boundary_versions':o['covered_boundary_versions']}
        result={**bindings,'schema':'implementaudit.compaction-reconciliation-result.v1','code_and_skill_pins':o['code_and_skill_pins'],
            'status':status,'currentness':'UNRESOLVED','measured_epoch':'UNRESOLVED','frontier':'Independent cold fixture','members':members,'authority_ceiling':'NONE'}
        rp=put(directory/'RESULT.json',result);self.resultpin=rp
        final={**bindings,'schema':'implementaudit.compaction-result-return.v1','result_bytes_identity':rp,'authority_ceiling':'NONE'}
        text='```json\n'+json.dumps(final,sort_keys=True)+'\n```'
        f=self.message('child',text,'final_answer')
        d=self.row('parent','response_item',{'type':'agent_message','id':'delivery-'+str(self.tick),'author':'/root/'+self.child,'recipient':'/root',
            'content':[{'type':'input_text','text':'Message Type: FINAL_ANSWER\nTask name: /root\nSender: /root/'+self.child+'\nPayload:\n'+text}]})
        self.request={'child_id':self.child,'observation_id':o['observation_id'],'result_evidence':{'bound_exchange':self.bound,'use':use,'child_final':f,'parent_delivery':d}}
        return self.request
    def accept(self,result):
        o=self.reserved['obligation']
        value={'schema':'implementaudit.compaction-reconciliation-acceptance.v1','action':'ACCEPT_BOUNDED_RECONCILIATION',
            'parent_identity':o['parent_identity'],'actual_child_identity':o['actual_child_identity'],'obligation_digest':self.reserved['obligation_digest'],
            'observation_id':o['observation_id'],'child_observation_exchange_identity':self.observed['child_observation_exchange_identity'],
            'actual_result_digest':result['return_digest'],'accepted_boundary_versions':o['covered_boundary_versions'],
            'observation_source_cutoff':o['observation_source_cutoff'],'authority_ceiling':'NONE'}
        self.acceptedvalue=value
        return {'child_id':self.child,'return_digest':result['return_digest'],'acceptance':self.typed('parent',value)}
