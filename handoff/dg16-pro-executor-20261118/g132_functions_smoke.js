/* Inert model-side harness. Root passes the real tools object and actual live
 * Root capabilities. No Python callback is represented as a tools capability.
 * The branch holds synthetic data only; original G3 is expected to refuse.
 */
(async ({tools, codec, makeBridge, setup, root}) => {
  const need=(v,c)=>{if(!v)throw Error(c);};
  const clone=v=>codec.strict(codec.canonical(v));
  need(typeof root?.admit==='function'&&typeof root?.decide==='function','ACTUAL_LIVE_ROOT_CAPABILITIES');
  need(codec.descriptor(setup.configuration.raw).sha256===setup.configuration.sha256,'CONFIGURATION_BODY_PIN');
  const cfg=codec.strict(setup.configuration.raw),api=makeBridge({tools,codec,linux:setup.linux});
  const SCOPE='SYNTHETIC_TRANSPORT_ONLY_NO_ORIGINAL_INPUTS';
  need(cfg.fixture_scope===SCOPE,'EXPLICIT_SMOKE_ONLY');
  const successful=x=>x?.status==='TRANSPORT_COMPLETE_REQUIRES_ORIGINAL_RECEIVING';
  const asRole=(role,more={})=>({...clone(cfg.spec),role,...more});
  const encodePayload=value=>{
    const text=codec.canonical(value),bytes=[];
    // Every owner argument is JSON. Escape non-ASCII before the byte frame.
    const ascii=text.replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
    for(let i=0;i<ascii.length;i++)bytes.push(ascii.charCodeAt(i));
    const C='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';let out='';
    for(let i=0;i<bytes.length;i+=3){const a=bytes[i],b=bytes[i+1],c=bytes[i+2];
      out+=C[a>>2]+C[(a&3)<<4|(b??0)>>4]+(b===undefined?'=':C[(b&15)<<2|(c??0)>>6])+(c===undefined?'=':C[c&63]);}
    return out;
  };
  const processFor=(action,payload={})=>api.framedProcess({path:setup.owner_runtime.path,
    sha256:setup.owner_runtime.sha256,exchange_root:cfg.root,deadline_ms:cfg.spec.expires_ms,
    args:[action,setup.configuration.path,setup.configuration.sha256,encodePayload(payload)]});
  const owner=async(action,payload={})=>{const source=processFor(action,payload);
    await source.start();const event=await source.next();need(event.event==='complete','ACTUAL_OWNER_RETURN');return event.receipt;};
  const receipt={schema:'dg16.pro-functions-smoke-receipt.v1',fixture_scope:SCOPE,original_acceptance:false,
    native_history_authenticated:false,protected_operation:'UNCHANGED_UNKNOWN_NO_REPLAY',automatic_retry:false};
  receipt.physical=await api.observeHost();
  receipt.public_read=await api.observePublic(asRole('public-observation'),root.admit);
  if(!successful(receipt.public_read))return {...receipt,status:'STOPPED_PUBLIC_READ_NO_REPLAY'};
  receipt.sender_mechanics=await api.sender(asRole('sender',{fixture_scope:SCOPE}),root.admit,{
    dispatcher:setup.sender_fixture,
    startSender:()=>owner('sender-fixture-start',{helper_sha256:setup.sender_fixture.descriptor.sha256}),
    receiveSenderTerminal:()=>owner('sender-fixture-terminal',{helper_sha256:setup.sender_fixture.descriptor.sha256}),
  });
  if(!successful(receipt.sender_mechanics))return {...receipt,status:'STOPPED_SENDER_MECHANICS_NO_REPLAY'};
  need(receipt.sender_mechanics.result.terminal.original_sender_invoked===false
    &&receipt.sender_mechanics.result.terminal.original_binding_gate_passed===false,
    'FIXTURE_SENDER_MUST_NOT_IMPERSONATE_ORIGINAL_SENDER');
  receipt.branch=await api.prepareSmokeBranch(asRole('smoke-branch',{smoke:{scope:SCOPE,
    branch:cfg.branch,parent_sha:cfg.parent_sha}}),root.admit);
  if(!successful(receipt.branch))return {...receipt,status:'STOPPED_BRANCH_NO_REPLAY'};
  const parent=receipt.branch.result.parent_sha;
  receipt.publication=await api.publish(asRole('publication',{publication:{kind:'CONTROL_DATA_ONLY',
    branch:cfg.branch,parent_sha:parent,writes:5,reads:6,paths:['CONTROL.json','INPUTS.cms']}}),
    root.admit,processFor('publish-smoke',{parent_sha:parent}));
  if(!successful(receipt.publication))return {...receipt,status:'STOPPED_PUBLICATION_NO_REPLAY'};
  receipt.g3=await api.consumeG3(asRole('g3',{stage:'components'}),root.admit,{
    readRequest:()=>owner('g3-request'),
    validateRequest:({request})=>owner('g3-validate-request',{request}),
    // This function is the currently executing Root's actual decision, not a
    // synthesized transcript, copied issuer ID, or automatic proposal adoption.
    decide:async value=>{
      need(value.request.fixture_scope===SCOPE&&value.request.proposal_is_issued_decision===false,'SYNTHETIC_PROPOSAL_ONLY');
      return root.decide({...value,fixture_scope:SCOPE,original_effect_grant:false});
    },
    validateDecision:({request,decision})=>owner('g3-validate-decision',{request,decision}),
    consume:({request,decision})=>owner('g3-consume-probe',{request,decision}),
  });
  if(!successful(receipt.g3))return {...receipt,status:'STOPPED_G3_TRANSPORT_NO_REPLAY'};
  const consumed=receipt.g3.result.consumer_return;
  need(consumed.status==='ACTUAL_ORIGINAL_G3_CONSUMER_REFUSED'
    &&consumed.refusal==='ACTUAL_ROOT_CUSTODY_REQUIRED'&&consumed.actual_consumer_invoked===true
    &&consumed.successful_original_consumption===false,'REAL_G3_REFUSAL_MUST_REMAIN_VISIBLE');
  return {...receipt,status:'PUBLIC_SMOKE_COMPLETE_ORIGINAL_G3_REFUSED',original_awards:[],
    connected_GitHub_scope:'PUBLIC_HISTORICAL_RUN_AND_SYNTHETIC_ENGINEERING_BRANCH',
    source_function_scope:'ACTUAL_DISPATCHER_AND_BINARY_PUBLICATION_FUNCTIONS_WITH_EXPLICIT_FIXTURE_BROKER_AND_CONTENT_POLICY'};
})
