"""Windows tests for private_store_directory() in the built stage_b.py.
usage: test_store_custody.py <stage_b.py> <fresh work dir (must not exist)>"""
import _winapi,base64,json,os,stat,subprocess,sys,types
from pathlib import Path
src=Path(sys.argv[1]);work=Path(sys.argv[2]);work.mkdir()
mod=types.ModuleType('stage_b_under_test');mod.__file__=str(src);exec(compile(src.read_bytes(),str(src),'exec'),mod.__dict__)
check=mod.private_store_directory
ICACLS=r'C:\Windows\System32\icacls.exe';me=os.environ['USERDOMAIN']+'\\'+os.environ['USERNAME']
POWERSHELL=r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
# This readback uses WindowsIdentity/Get-Acl independently of the driver's
# ctypes custody implementation. The only supplied path is a fresh test fixture.
OWNER_QUERY=base64.b64encode(r'''
$ErrorActionPreference = 'Stop'
$acl = Get-Acl -LiteralPath $env:DG17_FIXTURE_OWNER_PATH
@{owner=$acl.GetOwner([System.Security.Principal.SecurityIdentifier]).Value;
  user=[System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value} |
  ConvertTo-Json -Compress
'''.encode('utf-16le')).decode('ascii')
def icacls(*a):
 r=subprocess.run([ICACLS,*map(str,a)],capture_output=True,text=True,timeout=30);assert r.returncode==0,(a,r.stdout,r.stderr)
def owner_facts(p):
 r=subprocess.run([POWERSHELL,'-NoProfile','-NonInteractive','-EncodedCommand',OWNER_QUERY],
  env=os.environ|{'DG17_FIXTURE_OWNER_PATH':str(p)},capture_output=True,text=True,timeout=30)
 assert r.returncode==0,'independent fixture owner query failed: '+r.stderr
 facts=json.loads(r.stdout);assert set(facts)=={'owner','user'}
 assert all(isinstance(v,str) and v.startswith('S-1-') for v in facts.values())
 return facts
def require_owner(p,expected=None):
 facts=owner_facts(p);wanted=facts['user'] if expected is None else expected
 assert facts['owner']==wanted,('fixture owner precondition',facts,wanted)
 preconditions.append(dict(check='independent owner SID',path=str(p).replace(str(work),'<work>'),
                           expected=wanted,**facts))
 return facts
def set_user_owner(p):
 icacls(p,'/setowner',me);return require_owner(p)
def private_baseline(p):
 require_owner(p)
 try:detail=check(p)
 except RuntimeError as e:raise AssertionError('fixture private baseline refused: '+str(e)) from e
 preconditions.append(dict(check='private user+SYSTEM baseline',path=str(p).replace(str(work),'<work>')))
 return detail
def private(p,extra=()):
 p.mkdir();set_user_owner(p)
 icacls(p,'/inheritance:r','/grant:r',me+':(OI)(CI)F','*S-1-5-18:(OI)(CI)F')
 private_baseline(p)
 if extra:icacls(p,'/grant:r',*extra)
 return p
rows=[];bad=0;preconditions=[]
def case(name,expect,fn,reason=None):
 global bad,preconditions
 assert expect!='REFUSED' or reason,'negative control requires its intended refusal reason'
 preconditions=[]
 try:got='PASS';detail=fn()
 except RuntimeError as e:got='REFUSED';detail=str(e).replace(str(work),'<work>')
 except Exception as e:got='ERROR';detail=repr(e).replace(str(work),'<work>')
 ok=got==expect and (expect!='REFUSED' or reason in detail);bad+=not ok
 if isinstance(detail,dict):detail={k:v for k,v in detail.items() if k!='path'}
 rows.append(dict(case=name,expected=expect,expected_reason=reason,got=got,ok=ok,
                  preconditions=list(preconditions),detail=detail))
# positives
def created():
 p=work/'created';detail=check(p,create=True);require_owner(p);return detail
case('positive: driver-created store (create=True)','PASS',created)
case('positive: re-check of the driver-created store','PASS',lambda:private_baseline(work/'created'))
case('positive: icacls protected DACL, user+SYSTEM only','PASS',lambda:check(private(work/'manual')))
# The preserved historical 13/13 receipt expected PASS here. The commission's
# user+SYSTEM condition now requires refusal; old evidence is not regraded.
case('refused: Administrators outside owner user+SYSTEM scope','REFUSED',lambda:check(private(work/'admins',['*S-1-5-32-544:(OI)(CI)F'])),
     'access granted to another principal S-1-5-32-544')
# refusals
def everyone():
 p=private(work/'everyone');icacls(p,'/grant','*S-1-1-0:(W)');return check(p)
case('refused: added Everyone write ACE','REFUSED',everyone,'access granted to another principal S-1-1-0')
def everyone_read():
 p=private(work/'everyone-read');icacls(p,'/grant','*S-1-1-0:(R)');return check(p)
case('refused: added Everyone read-only ACE (not private)','REFUSED',everyone_read,'access granted to another principal S-1-1-0')
def inherited():
 parent=private(work/'parent',['*S-1-5-32-545:(OI)(CI)M']);icacls(parent,'/inheritance:e')
 child=private(parent/'store');icacls(child,'/inheritance:e');return check(child)
case('refused: inherited Users write ACE','REFUSED',inherited,'DACL is not protected: inherited access can apply')
def inherited_only_users():
 parent=private(work/'parent2',['*S-1-5-32-545:(OI)(CI)M'])
 child=private(parent/'store');icacls(child,'/inheritance:e');return check(child)
case('refused: inherited Users write ACE under an otherwise private parent','REFUSED',inherited_only_users,
     'DACL is not protected: inherited access can apply')
def absent():
 p=work/'absent';assert not os.path.lexists(p);return check(p)
case('refused: missing directory','REFUSED',absent,'open directory failed (winerror 2)')
def junction():
 target=private(work/'junction-target');link=work/'junction';_winapi.CreateJunction(str(target),str(link))
 assert os.lstat(link).st_file_attributes&stat.FILE_ATTRIBUTE_REPARSE_POINT
 return check(link)
case('refused: junction to a private directory','REFUSED',junction,'junction, link or other reparse point')
def unprotected_inherit_own():
 parent=private(work/'parent3');child=private(parent/'store');icacls(child,'/inheritance:e');return check(child)
case('refused: unprotected DACL (inherits only user+SYSTEM today)','REFUSED',unprotected_inherit_own,
     'DACL is not protected: inherited access can apply')
case('refused: create=True on an existing directory','REFUSED',lambda:check(private(work/'existing'),create=True),
     'create new private directory (path must not already exist) failed (winerror 183)')
def a_file():
 p=work/'file';p.write_bytes(b'');set_user_owner(p);assert stat.S_ISREG(p.lstat().st_mode);return check(p)
case('refused: regular file','REFUSED',a_file,'not a directory')
def wrong_owner():
 p=private(work/'wrong-owner');icacls(p,'/setowner','*S-1-5-32-544')
 facts=require_owner(p,'S-1-5-32-544');assert facts['owner']!=facts['user'];return check(p)
case('refused: different owner with otherwise private user+SYSTEM DACL','REFUSED',wrong_owner,
     'owner S-1-5-32-544 is not the current user')
print(json.dumps(rows,indent=1));print('CASES',len(rows),'FAILED',bad);sys.exit(1 if bad else 0)
