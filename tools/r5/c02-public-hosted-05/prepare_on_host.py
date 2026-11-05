#!/usr/bin/env python3
"""Prepare only: bind the public-code C02-05 packet on one selected host.
No product import, native execution, binary extraction, subject, socket, grant,
review, model call, or ROOT_GO is performed here. Review and GO remain separate.
"""
from pathlib import Path
import argparse, ast, hashlib, json, os, re, stat, subprocess

AUTHOR='/root/h0_c02_or'
SOURCE_HEAD='35bf9823856eb4efe254b882954120480632230e'
SOURCE_TREE='abe08aabc83de3b27c43e6acf28646fb089f0f34'
CONTROLLER='r5-c02-native-tail-20261105-05'
SUBJECT='/tmp/implementaudit-r5-c02-native-tail-20261105-05'
BINARY='/tmp/implementaudit-r5-c02-native-binary-20261105-05/codex'

def need(ok, reason):
    if not ok: raise ValueError(reason)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
def parse(raw):
    def unique(pairs):
        result={}
        for key,value in pairs:
            need(key not in result,'DUPLICATE_JSON_KEY');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=unique)

def regular(path, maximum=512*1024*1024):
    path=Path(path)
    need(path.is_absolute() and '..' not in path.parts,'ABSOLUTE_PATH_REQUIRED')
    for node in (path,*path.parents): need(not stat.S_ISLNK(node.lstat().st_mode),'SYMLINK_INPUT')
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=maximum,'UNSUPPORTED_INPUT')
    digest=hashlib.sha256();parts=[]
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):
            digest.update(block)
            if before.st_size<=4194304:parts.append(block)
        opened=os.fstat(stream.fileno())
    after=path.lstat()
    ident=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_nlink,x.st_uid,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(ident(before)==ident(opened)==ident(after),'INPUT_CHANGED_DURING_READ')
    return {'path':str(path),'bytes':before.st_size,'sha256':digest.hexdigest(),'mode':stat.S_IMODE(before.st_mode),'owner_uid':before.st_uid}, b''.join(parts) if before.st_size<=4194304 else None

def rebind(raw, values):
    text=raw.decode();original=ast.parse(text);lines=text.splitlines(keepends=True);edits=[]
    for key,value in values.items():
        matches=[n.value for n in original.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id==key]
        need(len(matches)==1,'BINDING_SHAPE_'+key);node=matches[0]
        begin=sum(map(len,lines[:node.lineno-1]))+node.col_offset;end=sum(map(len,lines[:node.end_lineno-1]))+node.end_col_offset
        edits.append((begin,end,value))
    for begin,end,value in sorted(edits,reverse=True):text=text[:begin]+value+text[end:]
    def normalized(tree):
        for node in tree.body:
            if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in values:node.value=ast.Constant(value='__REBIND_ONLY__')
        return ast.dump(tree,include_attributes=False)
    need(normalized(original)==normalized(ast.parse(text)),'NON_BINDING_LOGIC_CHANGED')
    return text.encode()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--archive',required=True)
    parser.add_argument('--output-parent',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();bundle=Path(__file__).resolve().parent
    source=Path(args.source);output=Path(args.output);parent=Path(args.output_parent)
    need(source.is_absolute() and source.resolve(strict=True)==source,'CANONICAL_SOURCE_REQUIRED')
    need(parent.is_absolute() and parent.resolve(strict=True)==parent and parent.is_dir(),'EXISTING_CANONICAL_PARENT_REQUIRED')
    need(output.is_absolute() and output.parent==parent and not os.path.lexists(output),'NEW_DIRECT_CHILD_OUTPUT_REQUIRED')
    seal_raw=(bundle/'BUNDLE_SEAL.json').read_bytes();seal=parse(seal_raw)
    need(seal['schema']=='r5.c02-public-hosted-code-bundle.v1','BUNDLE_SCHEMA')
    bundled={}
    for entry in seal['files']:
        name=entry['name'];need(name and not Path(name).is_absolute() and '..' not in Path(name).parts,'BUNDLE_NAME')
        observed,raw=regular(bundle/name)
        need(all(observed[k]==entry[k] for k in ('bytes','sha256','mode')),'BUNDLE_MEMBER_CHANGED')
        bundled[name]=raw
    template=parse(bundled['INPUT_TEMPLATE.json']);plan=parse(bundled['PROTOCOL_TEMPLATE.json'])
    need(template['source_commit']==SOURCE_HEAD and template['source_tree']==SOURCE_TREE,'SOURCE_TEMPLATE_IDENTITY')
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'}
    query=subprocess.run(['/usr/bin/git','-C',str(source),'rev-parse','HEAD','HEAD^{tree}'],env=env,capture_output=True,timeout=15)
    need(query.returncode==0 and query.stdout.decode().splitlines()==[SOURCE_HEAD,SOURCE_TREE],'SOURCE_COMMIT_TREE_DIFFERS')
    query=subprocess.run(['/usr/bin/git','-C',str(source),'status','--porcelain=v1','--untracked-files=no'],env=env,capture_output=True,timeout=15)
    need(query.returncode==0 and not query.stdout,'TRACKED_SOURCE_CHANGED')
    plan.update(controller=CONTROLLER,subject=SUBJECT,owned_binary=BINARY,controlled_event='r5-c02-native-tail-controlled-nonprotected-fault-20261105-05',logical_reservation='r5-c02-native-tail-pending-reservation-05')
    plan_raw=encoded(plan);members=[];paths=set();metadata=[]
    for entry in template['members']:
        m=dict(entry);route=m.pop('binding');old_sha=m.get('sha256')
        if route=='source':path=source/m.pop('source_relative')
        elif route=='bundle':path=bundle/m.pop('bundle_relative')
        elif route=='archive':path=Path(args.archive)
        elif route=='system':path=Path(m['invocation']).resolve(strict=True)
        elif route=='protocol':path=output/'PROTOCOL_PLAN.json'
        else:raise ValueError('UNKNOWN_INPUT_BINDING')
        if route=='protocol':observed={'path':str(path),'bytes':len(plan_raw),'sha256':sha(plan_raw),'mode':420}
        else:
            observed,_=regular(path)
            if route!='system':need(all(observed[k]==m[k] for k in ('bytes','sha256','mode')),'INPUT_PIN_CHANGED_'+m['key'])
            else:
                metadata.append({'key':m['key'],'invocation':m['invocation'],'resolved':observed,'ancestors':[{'path':str(p),'owner_uid':p.stat().st_uid,'mode':stat.S_IMODE(p.stat().st_mode)} for p in path.parents]})
        need(observed['path'] not in paths,'DUPLICATE_INPUT_PATH');paths.add(observed['path'])
        m.update({k:observed[k] for k in ('path','bytes','sha256','mode')});members.append(m)
    need(len(members)==92 and len({m['key'] for m in members})==92,'PROSPECTIVE_INPUT_CENSUS')
    manifest={'schema':'implementaudit.r5.c02-native-tail-inputs.v1','authority':'PREPARATION_ONLY','source_root':str(source),'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'prospective_controller':CONTROLLER,'prospective_subject':SUBJECT,'members':members}
    manifest_raw=encoded(manifest);input_sha=sha(manifest_raw)
    values={'BASE':f'Path({str(parent)!r})','LANE':f'Path({str(output)!r})','SUBJECT':f'Path({SUBJECT!r})','CONTROLLER':repr(CONTROLLER),'OWNED_BINARY':f'Path({BINARY!r})','INPUT_SHA256':repr(input_sha),'SOURCE_HEAD':repr(SOURCE_HEAD),'SOURCE_TREE':repr(SOURCE_TREE)}
    driver=rebind(bundled['templates/c02_native_tail.py'],dict(values,SOURCE=f'Path({str(source)!r})'))
    receiver=rebind(bundled['templates/receive_tail.py'],values)
    verification={'schema':'r5.c02-05.host-preparation-static.v1','status':'STATIC_BINDINGS_ONLY','authority':'NONE','bundle_sha256':sha(seal_raw),'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'input_count':92,'host_runtime_metadata':metadata,'product_imported':False,'native_executed':False,'model_called':False,'custody_supported':'NOT_YET_CHECKED_BY_OPERATION','currentness':'NOT_ESTABLISHED','execution_authorized':False}
    payloads={'c02_native_tail.py':driver,'receive_tail.py':receiver,'INPUT_MANIFEST.json':manifest_raw,'PROTOCOL_PLAN.json':plan_raw,'VERIFICATION.json':encoded(verification),'DESIGN.md':bundled['DESIGN.md'],'PUBLIC_SCOPE.md':bundled['PUBLIC_SCOPE.md'],'REVIEW_REQUEST.json':bundled['REVIEW_REQUEST.json'],'PROSPECTIVE_INPUT_DELTA.json':bundled['PROSPECTIVE_INPUT_DELTA.json'],'AUTHORIZATION_FORMATS.json':bundled['AUTHORIZATION_FORMATS.json']}
    output.mkdir(mode=0o700,exist_ok=False)
    for name,raw in payloads.items():
        with (output/name).open('xb') as stream:stream.write(raw)
        os.chmod(output/name,0o644)
    prepared={'schema':'implementaudit.r5.c02-native-tail-sealed-preparation.v1','authority':'PREPARATION_ONLY','author':AUTHOR,'input_manifest_sha256':input_sha,'files':[{'name':name,'bytes':len(raw),'sha256':sha(raw),'mode':420} for name,raw in sorted(payloads.items())]}
    prepared_raw=encoded(prepared)
    with (output/'SEALED_PREPARATION.json').open('xb') as stream:stream.write(prepared_raw)
    os.chmod(output/'SEALED_PREPARATION.json',0o644)
    for entry in prepared['files']:
        observed,_=regular(output/entry['name']);need(all(observed[k]==entry[k] for k in ('bytes','sha256','mode')),'PREPARED_READBACK_FAILED')
    print(json.dumps({'status':'PREPARED_PENDING_INDEPENDENT_REVIEW_AND_ROOT_GO','preparation_sha256':sha(prepared_raw),'input_manifest_sha256':input_sha,'input_count':92,'execution_authorized':False}))

if __name__=='__main__':main()
