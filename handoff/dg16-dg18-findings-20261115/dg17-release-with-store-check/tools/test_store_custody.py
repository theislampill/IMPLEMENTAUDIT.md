"""Windows tests for private_store_directory() in the built stage_b.py.
usage: test_store_custody.py <stage_b.py> <fresh work dir (must not exist)>"""
import _winapi,json,os,subprocess,sys,types
from pathlib import Path
src=Path(sys.argv[1]);work=Path(sys.argv[2]);work.mkdir()
mod=types.ModuleType('stage_b_under_test');mod.__file__=str(src);exec(compile(src.read_bytes(),str(src),'exec'),mod.__dict__)
check=mod.private_store_directory
ICACLS=r'C:\Windows\System32\icacls.exe';me=os.environ['USERDOMAIN']+'\\'+os.environ['USERNAME']
def icacls(*a):
 r=subprocess.run([ICACLS,*map(str,a)],capture_output=True,text=True);assert r.returncode==0,(a,r.stdout,r.stderr)
def private(p,extra=()):
 p.mkdir();icacls(p,'/inheritance:r','/grant:r',me+':(OI)(CI)F','*S-1-5-18:(OI)(CI)F',*extra);return p
rows=[];bad=0
def case(name,expect,fn):
 global bad
 try:got='PASS';detail=fn()
 except RuntimeError as e:got='REFUSED';detail=str(e).replace(str(work),'<work>')
 except Exception as e:got='ERROR';detail=repr(e)
 ok=got==expect;bad+=not ok;rows.append(dict(case=name,expected=expect,got=got,ok=ok,detail=detail if isinstance(detail,str) else {k:v for k,v in detail.items() if k!='path'}))
# positives
case('positive: driver-created store (create=True)','PASS',lambda:check(work/'created',create=True))
case('positive: re-check of the driver-created store','PASS',lambda:check(work/'created'))
case('positive: icacls protected DACL, user+SYSTEM only','PASS',lambda:check(private(work/'manual')))
# The preserved historical 13/13 receipt expected PASS here. The commission's
# user+SYSTEM condition now requires refusal; old evidence is not regraded.
case('refused: Administrators outside owner user+SYSTEM scope','REFUSED',lambda:check(private(work/'admins',['*S-1-5-32-544:(OI)(CI)F'])))
# refusals
def everyone():
 p=private(work/'everyone');icacls(p,'/grant','*S-1-1-0:(W)');return check(p)
case('refused: added Everyone write ACE','REFUSED',everyone)
def everyone_read():
 p=private(work/'everyone-read');icacls(p,'/grant','*S-1-1-0:(R)');return check(p)
case('refused: added Everyone read-only ACE (not private)','REFUSED',everyone_read)
def inherited():
 parent=work/'parent';parent.mkdir();icacls(parent,'/grant','*S-1-5-32-545:(OI)(CI)M');child=parent/'store';child.mkdir();return check(child)
case('refused: inherited Users write ACE','REFUSED',inherited)
def inherited_only_users():
 parent=private(work/'parent2',['*S-1-5-32-545:(OI)(CI)M']);child=parent/'store';child.mkdir();return check(child)
case('refused: inherited Users write ACE under an otherwise private parent','REFUSED',inherited_only_users)
case('refused: missing directory','REFUSED',lambda:check(work/'absent'))
def junction():
 target=private(work/'junction-target');link=work/'junction';_winapi.CreateJunction(str(target),str(link));assert check(target);return check(link)
case('refused: junction to a private directory','REFUSED',junction)
def unprotected_inherit_own():
 parent=private(work/'parent3');child=parent/'store';child.mkdir();return check(child)
case('refused: unprotected DACL (inherits only user+SYSTEM today)','REFUSED',unprotected_inherit_own)
case('refused: create=True on an existing directory','REFUSED',lambda:check(work/'manual',create=True))
def a_file():
 p=work/'file';p.write_bytes(b'');return check(p)
case('refused: regular file','REFUSED',a_file)
def wrong_owner():
 p=private(work/'wrong-owner');icacls(p,'/setowner','*S-1-5-32-544');return check(p)
case('refused: different owner with otherwise private user+SYSTEM DACL','REFUSED',wrong_owner)
print(json.dumps(rows,indent=1));print('CASES',len(rows),'FAILED',bad);sys.exit(1 if bad else 0)
