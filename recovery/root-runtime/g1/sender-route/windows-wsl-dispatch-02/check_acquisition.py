"""Check the launcher's short read, FIFO substitution and exact helper placement.

Runs only on a private directory of the nonroot Ubuntu sender. Uses an inert file
as the observed pin target. It never imports or dispatches an actual broker.
"""
import ast
import errno
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import sys
import tempfile

OLD=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/astra-successor-reconciliation-20261108/g1-current04-issuer/sender-route')
NEW=OLD/'windows-wsl-dispatch-02'
BASE=OLD/'recovered-g1-g3-root-binding-r2/author'
h=lambda data:hashlib.sha256(data).hexdigest()

def js_loader(text):
    return json.loads(next(x for x in text.splitlines() if x.startswith(' const loader='))[len(' const loader='):-1])

def patched_functions(source,names):
    nodes=[n for n in ast.parse(source).body if getattr(n,'name',None) in names]
    return compile(ast.Module(nodes,type_ignores=[]),'<bounded-source-test>','exec')

def refuse(ok,reason):
    if not ok:raise ValueError(reason)

def exercise(path,kind,revision):
    payload=b"print('fixture invoked')\n"
    path.write_bytes(payload);path.chmod(0o400)
    oldopen,oldpread=os.open,os.pread;oldargv=sys.argv;attempt=[]
    def swap(p,flags,*args,**kw):
        if os.fspath(p)==str(path):
            path.unlink();os.mkfifo(path,0o600)
        return oldopen(p,flags,*args,**kw)
    def observed_read(*args,**kwargs):
        attempt.append('pread');return oldpread(*args,**kwargs)
    def expired(*args):raise TimeoutError('fixture FIFO open')
    original_signal=signal.signal(signal.SIGALRM,expired)
    os.open=swap;os.pread=observed_read
    try:
        signal.setitimer(signal.ITIMER_REAL,1.0)
        if kind=='bootstrap':
            source=(OLD/'windows-wsl-dispatch'/'dispatch.js' if revision=='before' else NEW/'dispatch.js').read_text()
            sys.argv=['probe',str(path),h(payload)]
            exec(compile(js_loader(source),'<literal bootstrap>','exec'),{})
        else:
            s=(BASE/'bind_dispatcher.py' if revision=='before' else NEW/'bind_dispatcher.py').read_text()
            n={'os':os,'Path':Path,'stat':stat,'need':refuse}
            exec(patched_functions(s,['read']),n);n['read'](path)
        return 'FALSE_ACCEPT',len(attempt)
    except (TimeoutError,ValueError,AssertionError,OSError) as exc:
        return type(exc).__name__,len(attempt)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        signal.signal(signal.SIGALRM,original_signal)
        os.open=oldopen;os.pread=oldpread;sys.argv=oldargv
        path.unlink()

def main():
    os.umask(0o077)
    assert os.getuid()==os.geteuid()==1000
    results={}
    with tempfile.TemporaryDirectory(prefix='unchanged-pins-',dir='/home/agent/dg16-g1-current04-operators') as tmp:
        for kind,expected in [('bootstrap','AssertionError'),('binder','ValueError')]:
            for revision in ['before','after']:
                observed=exercise(Path(tmp)/(kind+'-'+revision),kind,revision)
                assert observed==(('TimeoutError' if revision=='before' else expected),0),(kind,revision,observed)
                results[kind+'_'+revision]=observed
    helper=(NEW/'dispatcher_entry.py').read_bytes();old=(BASE/'dispatcher_entry.py').read_bytes()
    assert old.replace(b'flags=os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC|',
                       b'flags=os.O_WRONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC|')==helper
    results['actual_helper_closed_source_sha256']=h(helper)
    print(json.dumps(results))

if __name__=='__main__':main()
