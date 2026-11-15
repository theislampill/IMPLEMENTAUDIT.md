/* Evaluate this expression in functions.exec after externally verifying its
 * exact source digest. Only the host's real `tools` capability is used. No
 * supplied response, JSON authority label or fixture authenticates an event.
 * The trusted admission/independence callbacks are EXTERNAL trust boundaries.
 */
(() => {
  'use strict';
  const REPO='theislampill/IMPLEMENTAUDIT.md';
  const TOOL='mcp__codex_apps__github_fetch';
  const MAX=4*1024*1024;
  const CONCLUSIONS=[null,'success','failure','cancelled','timed_out','action_required','neutral','skipped','stale','startup_failure'];
  const need=(v,c)=>{if(!v)throw Error(c);};
  const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
  const exact=(v,keys)=>object(v)&&Object.keys(v).sort().join('|')===[...keys].sort().join('|');
  const hex=(v,n)=>typeof v==='string'&&new RegExp('^[0-9a-f]{'+n+'}$').test(v);
  const integer=(v,min=0,max=Number.MAX_SAFE_INTEGER)=>Number.isSafeInteger(v)&&v>=min&&v<=max;
  function utf8(text){
    const out=[];
    for(const ch of text){let n=ch.codePointAt(0);if(n>=0xd800&&n<=0xdfff)n=0xfffd;
      if(n<128)out.push(n);else if(n<2048)out.push(192|n>>6,128|n&63);
      else if(n<65536)out.push(224|n>>12,128|n>>6&63,128|n&63);
      else out.push(240|n>>18,128|n>>12&63,128|n>>6&63,128|n&63);
    }return out;
  }
  function sha256(text){
    const bytes=utf8(text),bits=bytes.length*8;bytes.push(128);while(bytes.length%64!==56)bytes.push(0);
    for(const x of [Math.floor(bits/4294967296),bits>>>0])for(let s=24;s>=0;s-=8)bytes.push(x>>>s&255);
    const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],rot=(n,s)=>(n>>>s)|(n<<(32-s));
    for(let off=0;off<bytes.length;off+=64){const w=[];for(let i=0;i<16;i++)w[i]=(bytes[off+4*i]<<24|bytes[off+4*i+1]<<16|bytes[off+4*i+2]<<8|bytes[off+4*i+3])>>>0;
      for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2];w[i]=(w[i-16]+(rot(a,7)^rot(a,18)^(a>>>3))+w[i-7]+(rot(b,17)^rot(b,19)^(b>>>10)))>>>0;}
      let [a,b,c,d,e,f,g,h]=H;for(let i=0;i<64;i++){const t1=(h+(rot(e,6)^rot(e,11)^rot(e,25))+((e&f)^(~e&g))+K[i]+w[i])>>>0,t2=((rot(a,2)^rot(a,13)^rot(a,22))+((a&b)^(a&c)^(b&c)))>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}
      for(const [i,x] of [a,b,c,d,e,f,g,h].entries())H[i]=(H[i]+x)>>>0;
    }return H.map(x=>x.toString(16).padStart(8,'0')).join('');
  }
  function descriptor(text){need(typeof text==='string','STRING_BYTES_REQUIRED');return {bytes:utf8(text).length,sha256:sha256(text)};}
  function canonical(value,depth=0){
    need(depth<=80,'JSON_DEPTH');
    if(value===null||typeof value==='string'||typeof value==='boolean')return JSON.stringify(value);
    if(typeof value==='number'){need(Number.isFinite(value),'NONFINITE_JSON');return JSON.stringify(value);}
    if(Array.isArray(value))return '['+value.map(x=>canonical(x,depth+1)).join(',')+']';
    need(object(value),'JSON_ONLY');return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k],depth+1)).join(',')+'}';
  }
  const same=(a,b)=>canonical(a)===canonical(b);
  function strict(text){
    need(typeof text==='string'&&utf8(text).length<=MAX,'JSON_BOUND');let at=0;
    const ws=()=>{while(/[\x20\t\r\n]/.test(text[at]||'!'))at++;};
    function string(){const begin=at;need(text[at++]==='"','JSON_STRING');while(at<text.length){const c=text[at++];if(c==='"')return JSON.parse(text.slice(begin,at));if(c==='\\')at++;}throw Error('JSON_STRING');}
    function value(depth){need(depth<=80,'JSON_DEPTH');ws();const c=text[at];
      if(c==='"')return string();
      if(c==='{'){at++;const out=Object.create(null);ws();if(text[at]==='}'){at++;return out;}for(;;){ws();const key=string();need(!Object.prototype.hasOwnProperty.call(out,key),'DUPLICATE_JSON_KEY');ws();need(text[at++]===':','JSON_COLON');out[key]=value(depth+1);ws();const sep=text[at++];if(sep==='}')return out;need(sep===',','JSON_OBJECT');}}
      if(c==='['){at++;const out=[];ws();if(text[at]===']'){at++;return out;}for(;;){out.push(value(depth+1));ws();const sep=text[at++];if(sep===']')return out;need(sep===',','JSON_ARRAY');}}
      for(const [word,result] of [['true',true],['false',false],['null',null]])if(text.slice(at,at+word.length)===word){at+=word.length;return result;}
      const m=/-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(text.slice(at));need(m&&m.index===0,'JSON_NUMBER');at+=m[0].length;const n=Number(m[0]);need(Number.isFinite(n),'JSON_NONFINITE');return n;
    }
    const out=value(0);ws();need(at===text.length,'JSON_TRAILING');return out;
  }
  function endpoint(context,kind,control){
    const base='https://api.github.com/repos/'+context.repository;
    const paths={run:'/actions/runs/'+context.run_id,attempt:'/actions/runs/'+context.run_id+'/attempts/1',jobs:'/actions/runs/'+context.run_id+'/attempts/1/jobs?per_page=100&page=1',commit:'/git/commits/'+context.workflow_commit,source:'/git/commits/'+context.source_commit,workflow:'/contents/'+context.workflow_path+'?ref='+context.workflow_commit,artifacts:'/actions/runs/'+context.run_id+'/artifacts?per_page=100',ref:'/git/ref/heads/'+context.branch};
    if(control){paths['control-ref']='/git/ref/heads/'+control.branch;paths['control-commit']='/git/commits/'+control.commit;for(const name of Object.keys(control.files))paths['control-file:'+name]='/contents/'+control.path+'/'+name+'?ref='+control.commit;}
    need(Object.prototype.hasOwnProperty.call(paths,kind),'FIXED_ENDPOINT');return base+paths[kind];
  }
  function actionKinds(spec){
    const actions=['ref','run','attempt','jobs','commit','source','workflow','artifacts'];
    if(spec.control)actions.push('control-ref','control-commit',...['CONTROL.json','INDEPENDENT_REVIEW.json','ROOT_CONSUMPTION.json'].map(n=>'control-file:'+n),'control-ref');
    return [...actions,'run','artifacts','ref'];
  }
  function selection(spec){
    need(exact(spec,['schema','purpose','operator','actor','successor','role','operation_id','source','journal_root','expires_ms','context','control']),'SELECTION_FIELDS');
    need(spec.schema==='dg16.github-public-observation-selection.v1'&&['SOURCE_QUALIFICATION','OWNER_APPROVED_ORIGINAL_ROUTE'].includes(spec.purpose)&&spec.operator==='PRO-EXECUTOR-01'&&spec.successor==='PRO-EXECUTOR-01, designated by owner','SUCCESSOR_SELECTION');
    need(typeof spec.actor==='string'&&/^\/root(?:\/[a-z0-9_]+)?$/.test(spec.actor)&&['live','terminal'].includes(spec.role)&&typeof spec.operation_id==='string'&&/^[A-Za-z0-9_-]{1,128}$/.test(spec.operation_id),'ACTOR_ROLE_OPERATION');
    const s=spec.source;need(exact(s,['channel_sha256','journal_sha256','journal_path','python_path'])&&hex(s.channel_sha256,64)&&hex(s.journal_sha256,64),'SOURCE_PINS');
    for(const p of [s.journal_path,s.python_path,spec.journal_root])need(typeof p==='string'&&p.startsWith('/')&&p.length<=4096&&!/[\x00-\x1f\x7f]/.test(p),'ABSOLUTE_RUNTIME_PATH');
    need(integer(spec.expires_ms)&&Date.now()<spec.expires_ms&&spec.expires_ms<=Date.now()+300000,'CURRENT_BOUNDED_WINDOW');
    const c=spec.context;need(exact(c,['repository','repository_id','branch','run_id','run_attempt','workflow_commit','workflow_tree','source_commit','source_tree','workflow_path','workflow_sha256','job_name','github_actor']),'CONTEXT_FIELDS');
    need(c.repository===REPO&&integer(c.repository_id,1)&&/^pro\/dg16-r5-full-g2-direct-host-[0-9]+-[0-9]{8}$/.test(c.branch)&&typeof c.run_id==='string'&&/^[1-9][0-9]{0,15}$/.test(c.run_id)&&Number.isSafeInteger(Number(c.run_id))&&c.run_attempt===1,'EXACT_G221_FAMILY');
    for(const key of ['workflow_commit','workflow_tree','source_commit','source_tree'])need(hex(c[key],40)&&c[key]!=='0'.repeat(40),'COMMIT_TREE');
    need(c.workflow_path==='.github/workflows/dg16-r5-full-g2.yml'&&c.job_name==='full-registry-raw-pair'&&hex(c.workflow_sha256,64),'WORKFLOW_SOURCE');
    need(exact(c.github_actor,['id','login'])&&integer(c.github_actor.id,1)&&typeof c.github_actor.login==='string'&&/^[A-Za-z0-9-]{1,39}$/.test(c.github_actor.login),'GITHUB_OPERATOR_ACCOUNT');
    // A selected existing control commit can be observed. Absence, publication,
    // actual review and Root consumption are never inferred from these fields.
    if(spec.control!==null){const v=spec.control;need(spec.role==='terminal'&&exact(v,['branch','commit','tree','path','files'])&&v.branch===c.branch.replace('-host-','-control-')&&hex(v.commit,40)&&hex(v.tree,40)&&v.path==='qualification/dg16-full-g2-control/'+c.run_id+'-1','CONTROL_SELECTION');
      need(exact(v.files,['CONTROL.json','INDEPENDENT_REVIEW.json','ROOT_CONSUMPTION.json']),'CONTROL_POPULATION');for(const d of Object.values(v.files))need(exact(d,['bytes','sha256'])&&integer(d.bytes,1,4096)&&hex(d.sha256,64),'CONTROL_FILE_SELECTION');
    }
    return spec;
  }
  // Optional action grammar/sequence check for the external host adapter. This
  // grants no authority and authenticates neither source nor actor nor receipt.
  function createActionValidator(input){
    const spec=selection(strict(canonical(input))),actions=actionKinds(spec);
    let phase='begin',index=0;
    return action=>{
      need(phase!=='done','ACTION_SEQUENCE_ALREADY_FINISHED');
      if(phase==='begin'){need(action==='begin','ACTION_BEGIN_REQUIRED');phase='request';return true;}
      if(index===actions.length){need(phase==='request'&&action==='finish','ACTION_FINISH_REQUIRED');phase='done';return true;}
      need(object(action)&&action.index===index,'ACTION_INDEX');
      if(phase==='result'){need(exact(action,['index','result_returned'])&&action.result_returned===true,'ACTION_RESULT');index++;phase='request';return true;}
      need(exact(action,phase==='request'?['index','tool','request']:['index','tool','request','intent'])&&action.tool===TOOL&&exact(action.request,['url'])&&action.request.url===endpoint(spec.context,actions[index],spec.control),'ACTION_EXACT_REQUEST');
      if(phase==='intent')need(exact(action.intent,['bytes','sha256'])&&integer(action.intent.bytes,1)&&hex(action.intent.sha256,64),'ACTION_INTENT_DESCRIPTOR');
      phase=phase==='request'?'intent':'result';return true;
    };
  }
  function unwrap(raw,url,kind,context,control){
    need(object(raw)&&Object.keys(raw).every(k=>['content','structuredContent','isError','_meta'].includes(k))&&raw.isError===false,'ACTUAL_TOOL_RESULT');
    const meta=raw._meta||{};need(object(meta)&&Object.keys(meta).every(k=>['truncated','isTruncated','partial','hasMore'].includes(k)&&meta[k]===false),'COMPLETE_TOOL_RESULT');
    const s=raw.structuredContent;need(object(s)&&Object.keys(s).every(k=>['content','title','modified_date','url','display_url','display_title','structuredContent'].includes(k))&&s.url===url&&s.display_url===url&&typeof s.content==='string','EXACT_TOOL_ENDPOINT');
    if(s.structuredContent!==undefined){const t=s.structuredContent;need(object(t)&&Object.keys(t).every(k=>['content','title','display_url'].includes(k))&&t.content===s.content&&t.display_url===url,'NESTED_RESULT_CHANGED');}
    need(utf8(s.content).length>0&&utf8(s.content).length<=MAX,'PROVIDER_BOUND');
    if(kind==='workflow'){need(sha256(s.content)===context.workflow_sha256,'WORKFLOW_BYTES_CHANGED');return descriptor(s.content);}
    if(kind.startsWith('control-file:')){const expected=control.files[kind.slice('control-file:'.length)];need(same(descriptor(s.content),expected),'CONTROL_FILE_BYTES_CHANGED');strict(s.content);return descriptor(s.content);}
    const value=strict(s.content);need(object(value),'PROVIDER_OBJECT');return value;
  }
  const publicActor=v=>({id:v.id,login:v.login});
  function time(text){need(typeof text==='string'&&text.length<=40&&/[Zz]|[+-][0-9]{2}:[0-9]{2}$/.test(text),'PROVIDER_TIME');const v=Date.parse(text);need(Number.isFinite(v),'PROVIDER_TIME');return v;}
  function validate(kind,value,spec,rows,now){
    const c=spec.context,wanted=spec.role==='live'?'in_progress':'completed';
    if(kind==='run'||kind==='attempt'){
      need(value.id===Number(c.run_id)&&value.run_attempt===1&&value.head_sha===c.workflow_commit&&value.head_branch===c.branch&&value.path===c.workflow_path&&value.event==='push'&&value.status===wanted,'RUN_BINDING');
      for(const k of ['repository','head_repository'])need(value[k]?.full_name===c.repository&&value[k]?.id===c.repository_id,'REPOSITORY_IDENTITY');
      for(const k of ['actor','triggering_actor'])need(same(publicActor(value[k]||{}),c.github_actor),'GITHUB_ACTOR_BINDING');
      need(time(value.run_started_at)<=now,'RUN_TIME');need(CONCLUSIONS.includes(value.conclusion),'CONCLUSION');
      return {id:value.id,run_attempt:1,head_sha:value.head_sha,head_branch:value.head_branch,event:'push',path:value.path,status:value.status,conclusion:value.conclusion,repository:{full_name:c.repository,id:c.repository_id},head_repository:{full_name:c.repository,id:c.repository_id},actor:publicActor(value.actor),triggering_actor:publicActor(value.triggering_actor),run_started_at:value.run_started_at};
    }
    if(kind==='jobs'){
      need(value.total_count===1&&Array.isArray(value.jobs)&&value.jobs.length===1,'ONE_COMPLETE_JOB');const j=value.jobs[0];
      need(integer(j.id,1)&&j.run_id===Number(c.run_id)&&j.run_attempt===1&&j.head_sha===c.workflow_commit&&j.name===c.job_name&&j.status===wanted&&CONCLUSIONS.includes(j.conclusion)&&time(j.started_at)<=now,'JOB_BINDING');
      return {id:j.id,run_id:j.run_id,run_attempt:1,head_sha:j.head_sha,name:j.name,status:j.status,conclusion:j.conclusion,started_at:j.started_at};
    }
    if(kind==='commit'||kind==='source'){
      const commit=kind==='commit'?c.workflow_commit:c.source_commit,tree=kind==='commit'?c.workflow_tree:c.source_tree;
      need(value.sha===commit&&value.tree?.sha===tree&&Array.isArray(value.parents)&&value.parents.every(p=>hex(p.sha,40)),'COMMIT_TREE_BINDING');
      if(kind==='commit')need(value.parents.length===1&&value.parents[0].sha===c.source_commit,'SOLE_SOURCE_PARENT');
      return {sha:commit,tree:{sha:tree},parents:value.parents.map(p=>({sha:p.sha}))};
    }
    if(kind==='ref'){need(value.ref==='refs/heads/'+c.branch&&value.object?.type==='commit'&&value.object.sha===c.workflow_commit,'HOST_REF_CHANGED');return {ref:value.ref,object:{type:'commit',sha:value.object.sha}};}
    if(kind==='control-ref'){need(value.ref==='refs/heads/'+spec.control.branch&&value.object?.type==='commit'&&value.object.sha===spec.control.commit,'CONTROL_REF_CHANGED');return {ref:value.ref,object:{type:'commit',sha:value.object.sha}};}
    if(kind==='control-commit'){need(value.sha===spec.control.commit&&value.tree?.sha===spec.control.tree&&Array.isArray(value.parents)&&value.parents.length===1&&value.parents[0].sha===c.workflow_commit,'CONTROL_SOLE_WORKFLOW_PARENT');return {sha:value.sha,tree:{sha:value.tree.sha},parents:[{sha:c.workflow_commit}]};}
    if(kind.startsWith('control-file:'))return value;
    if(kind==='workflow')return value;
    need(kind==='artifacts'&&exact(value,['total_count','artifacts'])&&integer(value.total_count,0,100)&&Array.isArray(value.artifacts)&&value.artifacts.length===value.total_count,'COMPLETE_ARTIFACT_LIST');
    const names={['dg16-full-correspondence-review-'+c.run_id+'-1']:'live',['dg16-full-registry-'+c.run_id+'-1']:'terminal',['dg16-g2-failed-streams-'+c.run_id+'-a1']:'cipher'};const ids=new Set(),roles=new Set(),list=[];
    for(const a of value.artifacts){const role=names[a.name];need(role&&!roles.has(role)&&integer(a.id,1)&&!ids.has(a.id),'PUBLIC_ONLY_ARTIFACT_POPULATION');ids.add(a.id);roles.add(role);
      const r=a.workflow_run;need(a.expired===false&&integer(a.size_in_bytes,1,role==='cipher'?269574168:400000)&&typeof a.digest==='string'&&/^sha256:[0-9a-f]{64}$/.test(a.digest)&&r?.id===Number(c.run_id)&&r.head_sha===c.workflow_commit&&r.head_branch===c.branch&&r.repository_id===c.repository_id&&r.head_repository_id===c.repository_id,'ARTIFACT_IDENTITY');
      need(time(rows.jobs.started_at)<=time(a.created_at)&&time(a.created_at)<=now,'ARTIFACT_TIME');
      list.push({id:a.id,name:a.name,expired:false,size_in_bytes:a.size_in_bytes,digest:a.digest,workflow_run:{id:r.id,head_sha:r.head_sha,head_branch:r.head_branch,repository_id:r.repository_id,head_repository_id:r.head_repository_id},created_at:a.created_at});
    }
    need(roles.has(spec.role),'SELECTED_PUBLIC_ARTIFACT_MISSING');return list.sort((a,b)=>a.id-b.id);
  }
  const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
  const BOOT="import hashlib,sys\nfrom pathlib import Path\ntry:\n p=Path(sys.argv[1]); raw=p.read_bytes(); assert hashlib.sha256(raw).hexdigest()==sys.argv[2]\n sys.argv=[str(p)]+sys.argv[3:]\n exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})\nexcept Exception:\n print('{\"status\":\"PINNED_JOURNAL_REFUSED\",\"authority\":\"NONE\"}'); sys.exit(1)\n";
  async function persist(spec,action,value){
    need(typeof tools!=='undefined'&&typeof tools.exec_command==='function','DURABLE_HOST_CAPABILITY_REQUIRED');
    const args=[spec.source.python_path,'-I','-B','-c',BOOT,spec.source.journal_path,spec.source.journal_sha256,spec.journal_root,action,canonical(value)];
    const r=await tools.exec_command({cmd:args.map(quote).join(' '),login:false,shell:'/bin/bash',max_output_tokens:1024,yield_time_ms:1000});
    need(r&&r.exit_code===0&&typeof r.output==='string'&&r.output.length<=8192,'DURABILITY_NOT_RECEIVED');const receipt=strict(r.output.trim());
    need(receipt.status==='PERSISTED_AND_READ_BACK'&&receipt.operation_key===value.operation_key&&receipt.action===action&&integer(receipt.record?.bytes,1)&&hex(receipt.record?.sha256,64),'DURABILITY_RECEIPT');return receipt.record;
  }
  function withoutDigest(receipt){const v={...receipt};delete v.receipt_sha256;return v;}
  async function observe(input,host,previous){
    let spec,key,initial,started=false,invoked=0,index=0;
    try{
      spec=selection(strict(canonical(input)));
      need(typeof tools!=='undefined'&&typeof tools[TOOL]==='function'&&host&&typeof host.admit==='function','ACTUAL_HOST_CAPABILITIES_REQUIRED');
      if(previous){need(previous.status==='PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING'&&previous.original_acceptance===false&&previous.operator==='PRO-EXECUTOR-01'&&previous.actor==='/root'&&previous.actor!==spec.actor&&previous.purpose===spec.purpose&&integer(previous.observed_start_ms)&&integer(previous.observed_end_ms)&&integer(previous.expires_ms)&&previous.observed_start_ms<=previous.observed_end_ms&&previous.observed_end_ms<=Date.now()&&previous.observed_end_ms<previous.expires_ms&&Date.now()<previous.expires_ms&&previous.expires_ms<=previous.observed_start_ms+300000&&hex(previous.receipt_sha256,64)&&sha256(canonical(withoutDigest(previous)))===previous.receipt_sha256&&same(previous.public_metadata,previous.facts?.public_metadata)&&same(previous.context,spec.context)&&same(previous.control_selection,spec.control)&&previous.role===spec.role&&same(previous.source,spec.source),'EXACT_OPERATOR_RECEIPT_REQUIRED');}
      else need(spec.actor==='/root','PRINCIPAL_ROOT_ACTOR_REQUIRED');
      const scope={operator:spec.operator,actor:spec.actor,purpose:spec.purpose,source:spec.source,context:spec.context,control:spec.control,role:spec.role,journal_root:spec.journal_root,operation_id:spec.operation_id,expires_ms:spec.expires_ms,selection_sha256:sha256(canonical(spec)),previous_receipt_sha256:previous?.receipt_sha256||null};
      const parentDeadline=previous?.expires_ms;
      const admission=await host.admit(scope);
      need(admission&&typeof admission.assertCurrent==='function'&&exact(admission.authorization,['ref','sha256'])&&typeof admission.authorization.ref==='string'&&admission.authorization.ref.length>0&&admission.authorization.ref.length<=512&&hex(admission.authorization.sha256,64),'EXTERNAL_CURRENT_AUTHORITY_CAPABILITY_REQUIRED');
      const checkDeadline=()=>{const now=Date.now();need(now<spec.expires_ms,'OPERATION_EXPIRED');need(!previous||now<parentDeadline,'OPERATOR_RECEIPT_EXPIRED');};
      const current=async(action)=>{checkDeadline();await admission.assertCurrent({...scope,action});checkDeadline();};
      await current('begin');
      if(previous){need(typeof admission.assertIndependent==='function','EXTERNAL_INDEPENDENCE_AND_OPERATOR_PROVENANCE_REQUIRED');await admission.assertIndependent({operator_receipt:previous,receiver:spec.actor,scope});}
      const actions=actionKinds(spec);
      // Nonce, expiry, journal path and authorization labels cannot evade a spent
      // subject within the trusted principal's fixed journal root.
      key=sha256(canonical({repository:spec.context.repository,run_id:spec.context.run_id,run_attempt:1,workflow_commit:spec.context.workflow_commit,role:spec.role,actor:spec.actor,mode:previous?'receiver':'operator'}));
      const began=Date.now();initial=await persist(spec,'begin',{operation_key:key,schema:'dg16.github-public-intent.v1',authority:'NONE',scope,authorization:admission.authorization,operation_id:spec.operation_id,action_count:actions.length,opened_ms:began,expires_ms:spec.expires_ms,automatic_retry:false,private_or_cipher:false});started=true;
      const rows={},records=[];
      for(index=0;index<actions.length;index++){
        const kind=actions[index],url=endpoint(spec.context,kind,spec.control),request={url};await current({index,tool:TOOL,request});
        const intent=await persist(spec,'intent',{operation_key:key,initial,index,tool:TOOL,request,kind,issued_ms:Date.now(),authority:'NONE',automatic_retry:false});
        await current({index,tool:TOOL,request,intent});
        // Exactly one actual invocation. No raw-response input and no retry path.
        invoked++;let actual=await tools[TOOL](request);await current({index,result_returned:true});
        const raw=JSON.stringify(actual);need(typeof raw==='string'&&utf8(raw).length>0&&utf8(raw).length<=MAX,'COMPLETE_WRAPPER_BOUND');
        const full=descriptor(raw),parsed=unwrap(actual,url,kind,spec.context,spec.control);actual=null;
        const projection=validate(kind,parsed,spec,rows,Date.now());
        if(Object.prototype.hasOwnProperty.call(rows,kind))need(same(rows[kind],projection),'OPENING_CLOSING_FACTS_CHANGED');else rows[kind]=projection;
        if(kind==='attempt')need(same(rows.run,projection),'RUN_ATTEMPT_DISAGREEMENT');
        const result=await persist(spec,'result',{operation_key:key,initial,index,intent,tool:TOOL,request_sha256:sha256(canonical(request)),whole_actual_wrapper:full,projection_sha256:sha256(canonical(projection)),observed_ms:Date.now(),authority:'NONE',raw_wrapper_retained:false,signed_url_retained:false,automatic_retry:false});
        records.push({intent,result});
      }
      await current('finish');const c=spec.context,artifact=rows.artifacts.find(a=>a.name===(spec.role==='live'?'dg16-full-correspondence-review-':'dg16-full-registry-')+c.run_id+'-1');
      const public_metadata={run:rows.run,commit:rows.commit,artifact};
      const control=spec.control?{ref:rows['control-ref'],commit:rows['control-commit'],files:Object.fromEntries(Object.keys(spec.control.files).map(n=>[n,rows['control-file:'+n]]))}:null;
      const facts={public_metadata,job:rows.jobs,host_ref:rows.ref,source:rows.source,workflow:rows.workflow,artifact_population:rows.artifacts,control};
      if(previous)need(same(facts,previous.facts),'INDEPENDENT_PROVIDER_FACTS_DISAGREE');
      const receipt={schema:'dg16.github-public-provider-observation.v1',status:previous?'INDEPENDENT_PROVIDER_FACTS_MATCH_ONLY':'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING',authority:'NONE',operator:spec.operator,actor:spec.actor,successor:spec.successor,purpose:spec.purpose,role:spec.role,context:c,control_selection:spec.control,source:spec.source,authorization:admission.authorization,selection_sha256:scope.selection_sha256,operation_key:key,observed_start_ms:began,observed_end_ms:Date.now(),expires_ms:spec.expires_ms,whole_actual_wrappers_retained:false,public_metadata,facts,original_acceptance:false,private_or_cipher:false,automatic_retry:false,independent_operator_receipt_sha256:previous?.receipt_sha256||null,external_authority_and_agent_provenance_required:true,archive_acquisition:'SEPARATE_ORIGINAL_BOUNDED_RESOLVER_REQUIRED',semantic_receiving:'UNCHANGED_BOUND_PUBLIC_RECEIVER_REQUIRED',control_observation:spec.control?'EXACT_SELECTED_PUBLIC_CONTROL_BYTES_ONLY':'NOT_PERFORMED'};
      receipt.receipt_sha256=sha256(canonical(receipt));
      checkDeadline();
      await persist(spec,'finish',{operation_key:key,initial,records,receipt});
      // A durable file is not a received result if its write outlived either
      // deadline. Preserve that spent slot and return UNKNOWN, without retry.
      checkDeadline();
      return receipt;
    }catch{
      const result={status:started?'UNKNOWN_NO_RETRY':'REFUSED_BEFORE_PROVIDER_CALL',authority:'NONE',actual_tool_invocations:invoked,next_action:index,automatic_retry:false,original_acceptance:false,private_or_cipher:false,reason:'EVIDENCE_OR_CURRENT_AUTHORITY_NOT_RECEIVED'};
      if(started){try{await persist(spec,'unknown',{operation_key:key,initial,...result});}catch{result.journal_completion='UNKNOWN';}}
      return result;
    }
  }
  return Object.freeze({collect:(spec,host)=>observe(spec,host,null),receive:(receipt,spec,host)=>observe(spec,host,receipt),createActionValidator,descriptor,canonical,strict});
})()
