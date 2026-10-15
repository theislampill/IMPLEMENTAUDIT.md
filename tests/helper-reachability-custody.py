"""Adversarial controls on the real checker's load and projection consumers.

Hooks replace bounded I/O/result boundaries only; the checked program and its
committed package owner remain unchanged. No native policy or worker is used.
"""
import builtins, contextlib, hashlib, io, json, sys, tempfile
from pathlib import Path
from unittest.mock import patch

repo=Path(sys.argv[1]).resolve()
bash=sys.argv[2]
checker=repo/'scripts/check-helper-reachability.sh'
source=checker.read_text(encoding='utf-8').split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0]
program=compile(source,str(checker),'exec')
builder=(repo/'scripts/package-contract.py').resolve()
expected=builder.read_bytes()
real_read=Path.read_bytes; real_compile=builtins.compile; real_exec=builtins.exec
results=[]

def case(kind,success,diagnostic=''):
    reads=0; compiled=[]
    with tempfile.TemporaryDirectory(prefix='r001e-byte-witness-') as raw:
        witness=Path(raw)/'altered-code-executed.txt'
        altered=('from pathlib import Path\nPath('+repr(str(witness))+').write_text("executed")\n').encode()
        altered=altered+b' '*(len(expected)-len(altered))
        assert len(altered)==len(expected) and altered!=expected
        def read(path):
            nonlocal reads
            if path.resolve()==builder:
                reads+=1
                if (kind=='authority-read-substitution' and reads==1) or (kind=='post-preflight-read-substitution' and reads==2):
                    return altered
            return real_read(path)
        def compile_buffer(value,filename,*args,**kwargs):
            if filename==str(builder): compiled.append(hashlib.sha256(value).hexdigest())
            return real_compile(value,filename,*args,**kwargs)
        def execute(code,scope=None,locals_scope=None,**kwargs):
            if getattr(code,'co_filename',None)==str(builder):
                real_exec(code,scope,locals_scope,**kwargs)
                original=scope['artifact_payload_entries']
                def entries(root,role,contract):
                    value=original(root,role,contract)
                    if role=='standalone_compatibility':
                        if kind=='executable-projection-divergence':
                            value.append(('scripts/unclassified.opaque',b'unknown executable\n',0o755))
                        elif kind=='mode-projection-divergence':
                            value=[(p,d,0o644 if p=='scripts/detect-stack.sh' else m) for p,d,m in value]
                        elif kind=='classification-projection-divergence':
                            value=[(p,d.replace(b'|S|stack-diagnosis|',b'|R|stack-diagnosis|') if p=='references/repo-state-comparison.md' else d,m) for p,d,m in value]
                        elif kind=='governor-command-projection-divergence':
                            value=[(p,d.replace(b'`python scripts/resolve-internal-skill.py',b'`echo python scripts/resolve-internal-skill.py') if p=='SKILL.md' else d,m) for p,d,m in value]
                    return value
                scope['artifact_payload_entries']=entries
                return
            return real_exec(code,scope,locals_scope,**kwargs)
        out=io.StringIO(); err=io.StringIO(); code=0
        argv=['checker-python',str(repo),str(repo),bash,'1']
        with patch.object(sys,'argv',argv),patch.object(Path,'read_bytes',read),patch.object(builtins,'compile',compile_buffer),patch.object(builtins,'exec',execute),contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            try: real_exec(program,{'__name__':'__main__'})
            except SystemExit as exc:
                code=exc.code if isinstance(exc.code,int) else 1
                if isinstance(exc.code,str): err.write(exc.code)
        output=out.getvalue()+err.getvalue()
        record={'case':kind,'exit':code,'builder_reads':reads,'compiled_sha256':compiled,'altered_code_executed':witness.exists(),'stdout_stderr':output}
        results.append(record)
        assert (code==0)==success and diagnostic in output,record
        assert not witness.exists(),record
        if kind.endswith('read-substitution'): assert compiled==[],record
        else: assert compiled==[hashlib.sha256(expected).hexdigest()],record
        print(json.dumps(record),flush=True)

case('exact-owner-positive',True,'full_path_sets=equal projections=2')
case('authority-read-substitution',False,'not its committed authority')
case('post-preflight-read-substitution',False,'package owner differs')
case('executable-projection-divergence',False,'executable projection parity differs')
case('mode-projection-divergence',False,'executable projection parity differs')
case('classification-projection-divergence',False,'classification projection parity differs')
case('governor-command-projection-divergence',False,'route owner projection parity differs')
print('custody/projection controls: 7/7; synthetic maintained-consumer scope only')
