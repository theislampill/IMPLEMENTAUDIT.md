"""Exact supported-file readback adapter; original R378 remains immutable.

No calls, files, admission or authority on import. install receives exact source
modules. Actual full supported file wrappers stay original provider evidence.
"""
import hashlib
import types
import re

FILE_TOOL='mcp__codex_apps__github_fetch_file'

def install(R, decoder):
    def file_read_plan(plan,published_commit):
        calls=R.control_read_plan(plan,published_commit)
        names=sorted(plan['files'])
        result=[]
        for call in calls:
            if call['kind'].startswith('blob'):
                index=int(call['kind'][4:]);name=names[index]
                result.append(dict(kind=call['kind'],tool=FILE_TOOL,arguments=dict(
                    repository_full_name=plan['context']['repository'],path=name,
                    ref=published_commit,encoding='base64')))
            else:result.append(call)
        return result

    def receive_file(raw,call,plan):
        a=call['arguments'];name=a['path']
        R.need(call['tool']==FILE_TOOL and name in plan['files'],'EXACT_CONTROL_FILE_PLAN')
        r=plan['files'][name]
        return decoder.decode_file_result(raw,dict(tool=call['tool'],arguments=a),
            {k:r[k] for k in ('bytes','sha256','git_blob_sha')},65536)

    def unwrap_read(raw,call,plan):
        if call['tool']==FILE_TOOL:return receive_file(raw,call,plan)
        return R.unwrap_control(raw,call['arguments']['url'])

    def receive_control_files(s,received,plan,published_commit,results,body,now_ms):
        R.validate_control(s,received,body,now_ms)
        R.need(plan['receiving']==R.desc(R.encode(received['receipt'])) and plan['context']==received['context'],'CONTROL_RECEIVING_JOIN')
        req=R.requirements(s,received)
        R.need(req['path'] in plan['files'] and plan['files'][req['path']]['sha256']==R.sha(body),'ACTUAL_CONTROL_BODY_JOIN')
        calls=file_read_plan(plan,published_commit)
        R.need(set(results)=={r['kind'] for r in calls} and sum(map(len,results.values()))<=R.MAX_JOURNAL,'CONTROL_FULL_RESULT_POPULATION')
        metadata={};leaves={}
        for call in calls:
            raw=results[call['kind']]
            if call['tool']==FILE_TOOL:leaves[call['arguments']['path']]=receive_file(raw,call,plan)
            else:metadata[call['kind']]=R.unwrap_control(raw,call['arguments']['url'])
        R.need(sum(len(R.encode(v)) for v in metadata.values())+sum(len(results[c['kind']]) for c in calls if c['tool']==FILE_TOOL)<=1024**2,'CONTROL_METADATA_AGGREGATE')
        ref=metadata['ref'];commit=metadata['commit'];tree=metadata['tree']
        R.need(ref==metadata['closing_ref'] and ref.get('ref')=='refs/heads/'+plan['branch'] and ref.get('object',{}).get('type')=='commit' and ref['object'].get('sha')==published_commit
          and commit.get('sha')==published_commit and commit.get('tree',{}).get('sha')==plan['expected_tree_sha']
          and type(commit.get('parents')) is list and len(commit['parents'])==1 and commit['parents'][0].get('sha')==plan['parent_sha'],'CONTROL_COMMIT_PARENT_REF_JOIN')
        R.need(tree.get('sha')==plan['expected_tree_sha'] and tree.get('truncated') is False and type(tree.get('tree')) is list,'CONTROL_TREE_BOUND')
        expected={};prefixes=set()
        for n,r in plan['files'].items():
            expected[n]=('blob','100644',r['git_blob_sha'],r['bytes']);parts=n.split('/')
            prefixes.update('/'.join(parts[:i]) for i in range(1,len(parts)))
        rows={}
        for r in tree['tree']:
            n=r.get('path');R.need(type(n) is str and n not in rows,'CONTROL_TREE_DUPLICATE');rows[n]=r
        R.need(set(rows)==set(expected)|prefixes,'CONTROL_EXACT_TREE_POPULATION')
        for n,r in rows.items():
            if n in prefixes:R.need(r.get('type')=='tree' and r.get('mode')=='040000' and type(r.get('sha')) is str and re.fullmatch('[0-9a-f]{40}',r['sha']),'CONTROL_TREE_DIRECTORY')
            else:R.need((r.get('type'),r.get('mode'),r.get('sha'),r.get('size'))==expected[n],'CONTROL_EXACT_LEAF')
        R.need(set(leaves)==set(plan['files']),'CONTROL_EXACT_FILE_POPULATION')
        for n,r in plan['files'].items():
            raw=leaves[n]
            R.need(raw==r['body_utf8'].encode() and R.desc(raw)=={'bytes':r['bytes'],'sha256':r['sha256']}
              and R.git_object('blob',raw)==r['git_blob_sha'],'CONTROL_ACTUAL_FILE_BODY')
        if received['phase']=='tools':
            # Retain H.check_control semantics directly over real decoded bytes;
            # do not synthesize a GitAPI blob-shaped provider response.
            d=s.H.declaration(s.binding)
            R.need(ref['ref']=='refs/heads/'+d['control_branch'] and commit['sha']!=d['control_parent']
              and len(commit['parents'])==1 and commit['parents'][0]['sha']==d['control_parent'],'HOST_TOOL_CONTROL_FRESH_PARENT')
            R.need(len(tree['tree'])==1 and set(leaves)=={'HOST_TOOL_ADOPTION.json'}
              and leaves['HOST_TOOL_ADOPTION.json']==body,'HOST_TOOL_CONTROL_BODY')
        return dict(schema='dg16.root-control-supported-file-receiving.v1',authority='NONE',phase=received['phase'],context=received['context'],root_body=R.desc(body),
          published_commit=published_commit,control_parent=plan['parent_sha'],control_tree=plan['expected_tree_sha'],artifact_receiving=plan['receiving'],
          full_actual_tool_results={k:R.desc(v) for k,v in sorted(results.items())},file_readback_transport=FILE_TOOL,
          file_bodies={n:dict(**R.desc(raw),git_blob_sha=R.git_object('blob',raw)) for n,raw in sorted(leaves.items())},
          validated_unix_ms=now_ms,authentication_boundary=R.AUTH,host_consumption_observed=False,effect_grant=False,original_awards=[])

    fields=dict(vars(R));fields.update(control_read_plan=file_read_plan,unwrap_control_read=unwrap_read,receive_control=receive_control_files)
    return types.SimpleNamespace(**fields)
