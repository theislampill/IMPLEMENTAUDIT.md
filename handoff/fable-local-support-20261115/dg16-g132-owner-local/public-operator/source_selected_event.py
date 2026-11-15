"""Source-selected adapter for the existing native event owner, not a grant.

Root supplies an independently received exact selection and actual publication.
No installed source or local JSON authenticates Root or authorizes an effect.
This adapter never launches a sender, key, workflow or provider call.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import re
import stat
import sys
import types


def need(value, code):
    if not value:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path, maximum=4*1024**2, pin=None):
    p=Path(path)
    need(p.is_absolute() and p.resolve(strict=True)==p, 'CANONICAL_SELECTED_PATH')
    for parent in p.parents:
        need(not parent.is_symlink(),'ANCESTOR_ALIAS')
    s=p.lstat()
    mark=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_nlink,x.st_uid,x.st_gid,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid()
         and stat.S_IMODE(s.st_mode) in (0o400,0o600) and 0<s.st_size<=maximum,'SELECTED_INPUT_CUSTODY')
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd))==mark(s) and not os.listxattr(fd),'SELECTED_INPUT_OPEN')
        chunks=[];count=0
        while count<=maximum:
            b=os.read(fd,min(65536,maximum+1-count))
            if not b:break
            chunks.append(b);count+=len(b)
        need(count==s.st_size and mark(os.fstat(fd))==mark(s)==mark(p.lstat()),'SELECTED_INPUT_CLOSE')
    finally:os.close(fd)
    raw=b''.join(chunks)
    need(pin is None or sha(raw)==pin,'SELECTED_INPUT_PIN')
    return raw


def parse(raw):
    def pairs(rows):
        out={}
        for k,v in rows:
            need(k not in out,'DUPLICATE_KEY');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))


def module(row):
    need(type(row) is dict and set(row)=={'path','sha256'},'EXACT_SOURCE_DESCRIPTOR')
    need(re.fullmatch('[0-9a-f]{64}',row['sha256']) is not None,'SOURCE_SHA256')
    raw=read(row['path'],1024**2,row['sha256'])
    m=types.ModuleType('selected_native_'+Path(row['path']).stem);m.__file__=row['path']
    exec(compile(raw,m.__file__,'exec'),m.__dict__)
    return m


def selected(raw):
    v=parse(raw)
    fields={'schema','successor','purpose','product_commit','product_tree','host_tree','phase_sha256',
            'receiver','event_owner','recipient_owner','assembler_owner','private_input_directory','root_source_receiving'}
    need(type(v) is dict and set(v)==fields and v['schema']=='dg16.native-event-source-selection.v1' and v['successor']=='PRO-EXECUTOR-01, designated by owner','EXACT_SELECTION')
    need(v['purpose'] in ('DONOR_PREFLIGHT_ONLY','FINAL_ORIGINAL_ACCEPTANCE'),'SELECTION_PURPOSE')
    for key in ('product_commit','product_tree','host_tree'):
        need(type(v[key]) is str and re.fullmatch('[0-9a-f]{40}',v[key]) is not None,'FULL_SUBJECT_ID')
    need(re.fullmatch('[0-9a-f]{64}',v['phase_sha256']) is not None,'FULL_PHASE_PIN')
    R=module(v['receiver']);s=R.Sources()
    need(s.binding['source_commit']==v['product_commit'] and s.binding['source_tree']==v['product_tree'],
         'SOURCE_PRODUCT_MISMATCH')
    need(s.sources['expected_tree']==v['host_tree'] and sha(R.read(s.root/'PHASE.json'))==v['phase_sha256'],
         'SOURCE_HOST_PHASE_MISMATCH')
    need(type(v['root_source_receiving']) is dict and set(v['root_source_receiving'])=={'path','sha256'},'ROOT_SOURCE_RECEIVING_DESCRIPTOR')
    read(v['root_source_receiving']['path'],65536,v['root_source_receiving']['sha256'])
    private=Path(v['private_input_directory'])
    need(private.resolve(strict=True)==private and private.stat().st_uid==os.geteuid()
         and stat.S_IMODE(private.stat().st_mode)==0o700,'PRIVATE_INPUT_DIRECTORY')
    actual={p.relative_to(private).as_posix() for p in private.rglob('*') if p.is_file()}
    need(actual==set(s.index) and len(actual)==11,'EXACT_PRIVATE_POPULATION')
    for n,row in s.index.items():
        body=read(private/n,32*1024**2,row['sha256']);need(len(body)==row['bytes'],'PRIVATE_DESCRIPTOR')
    E=module(v['event_owner'])
    need(E.RECEIVER_SHA==v['receiver']['sha256'] and str(E.ROOT)==str(Path(R.__file__).parent.parent),
         'EVENT_OWNER_SOURCE_JOIN')
    return v,R,s,E


def bind_product_guard(E,product):
    """Rebind the donor's one fixed product check; retain its complete guard."""
    raw=read(E.__file__,1024**2)
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='provider_check')
    class Product(ast.NodeTransformer):
        def visit_Constant(self,n):
            if n.value=='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f':
                return ast.copy_location(ast.Constant(product),n)
            return n
    tree=ast.fix_missing_locations(ast.Module(body=[Product().visit(node)],type_ignores=[]))
    exec(compile(tree,'<source-selected-existing-product-guard>','exec'),E.__dict__)


def publication(raw,v,s):
    p=parse(raw);need(type(p) is dict and all(k in p for k in ('commit','ref','run')),'ACTUAL_PUBLICATION_RECEIVING')
    c,r,run=p['commit'],p['ref'],p['run']
    head=c['sha'];need(re.fullmatch('[0-9a-f]{40}',head) is not None,'PUBLISHED_COMMIT')
    need(c['tree']['sha']==v['host_tree'] and s.host_commit(c)==head,
         'FINAL_HOST_SOURCE_PARENT')
    need(r['ref']=='refs/heads/'+s.binding['branch'] and r['object']['type']=='commit' and r['object']['sha']==head,
         'PUBLICATION_BRANCH_COMMIT')
    need(run['head_sha']==head and run['head_branch']==s.binding['branch'] and type(run['run_attempt']) is int
         and run['run_attempt']==1 and run['path']==s.binding['workflow_path'],'ACTUAL_RUN_SOURCE')
    return head,run


def bind_context(E,R,s,head,run):
    """Replace only historical event identity; preserve owner constructors/limits."""
    def context(actual_R,actual_s,c):
        # The retained supported-file control adapter returns an exact namespace
        # view of R with only its readback methods replaced. Accept that owned
        # view, retaining the same verified source/read/Sources identities.
        same_source=(actual_R is R or
            (getattr(actual_R,'Sources',None) is R.Sources and getattr(actual_R,'read',None) is R.read
             and getattr(actual_R,'sha',None) is R.sha and getattr(actual_R,'AUTH',None)==R.AUTH))
        need(same_source and actual_s is s,'SELECTED_RECEIVER_INSTANCE')
        s.context(c)
        need(set(c)=={'repository','branch','workflow_commit','workflow_path','run_id','run_attempt','job_name'}
             and c['workflow_commit']==head and c['branch']==s.binding['branch']
             and c['run_id']==str(run['id']) and type(c['run_attempt']) is int and c['run_attempt']==1,
             'EXACT_SELECTED_EVENT_CONTEXT')
    E.context=context
    E.receiver=lambda:R
    # E.main constructs the same Sources object through R.Sources(); returning
    # the already fully verified object preserves the source selected above.
    R.Sources=lambda:s


def main():
    need(sys.platform=='linux' and os.getuid()==os.geteuid()>0 and sys.flags.isolated and sys.dont_write_bytecode,
         'EXACT_NONROOT_NATIVE_RUNTIME')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selection',required=True);ap.add_argument('--selection-sha256',required=True)
    ap.add_argument('--publication');ap.add_argument('--publication-sha256')
    ap.add_argument('action',choices=['preflight','inspect-role','inspect-role-from-status','inspect-control','inspect-tools-decision',
        'issue-role','issue-role-from-status','issue-control','issue-tools-decision','issue-recipient-inputs','late-assemble'])
    ap.add_argument('event_arguments',nargs='*');a=ap.parse_args()
    v,R,s,E=selected(read(a.selection,65536,a.selection_sha256))
    if a.action=='preflight':
        need(not a.event_arguments and a.publication is None and a.publication_sha256 is None,'PREFLIGHT_ONLY')
        print(json.dumps(dict(authority='NONE',status='SELECTED_SOURCE_AND_ELEVEN_INPUTS_VERIFIED',
            purpose=v['purpose'],product_commit=v['product_commit'],product_tree=v['product_tree'],
            host_tree=v['host_tree'],phase_sha256=v['phase_sha256'],event_effects=0,original_awards=[])))
        return
    need(v['purpose']=='FINAL_ORIGINAL_ACCEPTANCE','DONOR_LIVE_EVENT_REFUSED')
    need(v['product_commit']=='e76a07b2bae7c945e5a9d529ed8cf9069f4c9064' and v['product_tree']=='ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7',
         'ASTRA_FINAL_TARGET_SOURCE_REQUIRED')
    need(a.publication is not None and a.publication_sha256 is not None,'ACTUAL_PUBLICATION_REQUIRED')
    publication_raw=read(a.publication,65536,a.publication_sha256)
    head,run=publication(publication_raw,v,s)
    if a.action=='issue-recipient-inputs':
        need(len(a.event_arguments)==5,'EXISTING_RECIPIENT_OWNER_ARGUMENTS')
        P=module(v['recipient_owner'])
        need(P.READER_SHA==v['receiver']['sha256'],'RECIPIENT_READER_JOIN')
        P.HOST_COMMIT=head;P.HOST_TREE=v['host_tree'];P.load_reader=lambda:R
        sys.argv=[P.__file__,*a.event_arguments];P.main();return
    if a.action=='late-assemble':
        A=module(v['assembler_owner'])
        need(A.READER_SHA==v['receiver']['sha256'],'ASSEMBLER_READER_JOIN')
        A.PHASE_SHA=v['phase_sha256']
        sys.argv=[A.__file__,*a.event_arguments];A.main();return
    bind_product_guard(E,v['product_commit'])
    bind_context(E,R,s,head,run)
    E.PUBLISHED_HOST_RECEIVING=publication_raw
    need(len(a.event_arguments)==2,'EXISTING_EVENT_OWNER_ARGUMENTS')
    sys.argv=[E.__file__,a.action,*a.event_arguments]
    # The action may issue local admission records only when actual Root invokes
    # it under its separate authority. This source supplies no such authority.
    E.main()


if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,TypeError,AttributeError):
        print('{"authority":"NONE","status":"SELECTED_NATIVE_EVENT_REFUSED","automatic_retry":false}')
        raise SystemExit(1)
