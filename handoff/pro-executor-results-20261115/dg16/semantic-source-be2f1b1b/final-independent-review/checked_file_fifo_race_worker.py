import os,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import semantic_receiver as S
p=Path(sys.argv[2]);p.write_bytes(b'inert public input')
original=os.open
swapped=False
def race(path,flags,*args,**kwargs):
    global swapped
    if str(path)==str(p) and not swapped:
        swapped=True
        p.unlink()
        os.mkfifo(p,0o600)
    return original(path,flags | (os.O_NONBLOCK if sys.argv[3]=='counterfactual_nonblock' else 0),*args,**kwargs)
S.os.open=race
try:
    S.checked_file(p,100)
except ValueError as e:
    print('REFUSED:'+str(e),flush=True)
else:
    print('ACCEPTED',flush=True)
