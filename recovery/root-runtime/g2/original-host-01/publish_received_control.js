async function publishReceivedG2Control(packet, save, currentHostIsHolding, remoteControlIsAbsent) {
  const repository = 'theislampill/IMPLEMENTAUDIT.md';
  const branch = 'pro/dg16-r5-full-g2-direct-control-01-20261109';
  const parent = '7f618adc702912f760d87f68fe9c94cc419e844c';
  const tree = '27bb6432546c2d0b3fb7df09f0845c3d1303bccd';
  const r = packet.request, c = packet.create_tree;
  function check(ok, reason) { if (!ok) throw Error(reason); }
  function fresh() { check(Date.now() < r.expires_utc_epoch * 1000, 'ORIGINAL_HOLD_EXPIRED'); }
  check(r.branch===branch && r.sole_parent===parent && r.run_id==='42579780645' && r.run_attempt===1
    && r.schema==='dg16.current-g2.actual-live-control-publication-request.v1' && r.actor==='/root'
    && /^[0-9a-f]{40}$/.test(r.expected_tree) && /^[0-9a-f]{64}$/.test(r.independent_review_seal_sha256), 'ROOT_PUBLICATION_REQUEST_JOIN');
  check(c.repository_full_name===repository && c.base_tree_sha===tree && c.tree_elements.length===3 && r.additions.length===3, 'ROOT_CONTROL_POPULATION');
  const expectedNames=['CONTROL.json','INDEPENDENT_REVIEW.json','ROOT_CONSUMPTION.json'];
  check(c.tree_elements.every((e,i)=>e.mode==='100644' && e.type==='blob' && e.path===r.additions[i].path
    && e.path.split('/').at(-1)===expectedNames[i] && typeof e.content==='string' && e.content.length<=4096), 'CONTROL_FILES_JOIN');
  async function once(name, args, perform) {
    fresh();
    await save(name+'.INTENT.json',{utc:new Date().toISOString(),name,args,run_id:r.run_id,expires_utc_epoch:r.expires_utc_epoch,automatic_retry:false});
    fresh();
    const result=await perform(args);
    await save(name+'.RESULT.json',result);
    check(result && result.isError===false,'CONTROL_PROVIDER_REFUSED_OR_UNKNOWN');
    return result.structuredContent;
  }
  fresh();check(await currentHostIsHolding() && await remoteControlIsAbsent(),'ACTUAL_HELD_JOB_AND_ABSENT_REF_REQUIRED');
  await save('EFFECT_GRANT.json',{utc:new Date().toISOString(),issuer:'01a1953f-a15b-7811-aa72-3538ebb03562',grant:'ONE_CREATE_TREE_COMMIT_AND_NEW_CONTROL_REF',...r});
  const t=await once('tree',c,args=>tools.mcp__codex_apps__github_create_tree(args));
  check(t.sha===r.expected_tree,'ACTUAL_CREATED_TREE_DIFFERS');
  const k=await once('commit',{repository_full_name:repository,parent_sha:parent,tree_sha:t.sha,message:'Consume independently reviewed DG16 G2 proof for run '+r.run_id},args=>tools.mcp__codex_apps__github_create_commit(args));
  check(/^[0-9a-f]{40}$/.test(k.sha),'ACTUAL_CREATED_COMMIT_REQUIRED');
  const evidence=await tools.mcp__codex_apps__github_fetch({url:'https://api.github.com/repos/'+repository+'/git/commits/'+k.sha});
  await save('commit.READBACK.json',evidence);
  const obj=JSON.parse(evidence.structuredContent.content);
  check(!evidence.isError && obj.sha===k.sha && obj.tree.sha===r.expected_tree && obj.parents.length===1 && obj.parents[0].sha===parent,'ACTUAL_COMMIT_READBACK');
  fresh();check(await remoteControlIsAbsent() && await currentHostIsHolding(),'EXACT_CREATE_ONLY_WINDOW');
  await once('ref',{repository_full_name:repository,branch_name:branch,sha:k.sha},args=>tools.mcp__codex_apps__github_create_branch(args));
  const after=await tools.mcp__codex_apps__github_fetch({url:'https://api.github.com/repos/'+repository+'/git/ref/heads/'+branch});
  await save('ref.READBACK.json',after);
  const ref=JSON.parse(after.structuredContent.content);
  check(!after.isError && ref.ref==='refs/heads/'+branch && ref.object.type==='commit' && ref.object.sha===k.sha,'PUBLISHED_CONTROL_READBACK');
  return {branch,commit:k.sha,tree:r.expected_tree,run_id:r.run_id,original_accepted:false};
}
