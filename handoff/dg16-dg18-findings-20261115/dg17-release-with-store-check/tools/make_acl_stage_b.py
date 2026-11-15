"""Add driver-side Windows custody of the host-session store directory to stage_b.py.

The packaged binding owner (host-session-binding.py) is not touched. Two insertions:
  1. function private_store_directory() before main();
  2. one call immediately before step 02-owned-init, which creates the store directory
     with an explicit owner-only DACL and then verifies owner and DACL through advapi32.
usage: make_acl_stage_b.py <in stage_b.py> <out stage_b.py (must not exist)>"""
import sys,hashlib
from pathlib import Path
FUNCTION=r'''def private_store_directory(path,create=False):
 """Fail-closed Windows custody of the host-session store directory (driver side only).

 Passes only if the path is a real directory (no junction, symlink or other reparse
 point), its owner is the current token user, and its DACL is present, protected
 against inheritance and made only of plain allow entries for the current user,
 or SYSTEM. The owner commission restricts this store to those two principals;
 an Administrators access entry is therefore refused too. Any other principal, any
 other entry type, a missing/NULL DACL, or any fact that cannot be read raises.
 create=True first creates the directory with exactly user+SYSTEM full control and
 the current user as owner; an existing path is never adopted.
 """
 import ctypes
 from ctypes import wintypes as w
 if os.name!='nt':raise RuntimeError('store custody: this check supports Windows only')
 target=str(Path(path).absolute());P=ctypes.c_void_p;ref=ctypes.byref
 k=ctypes.WinDLL('kernel32',use_last_error=True);a=ctypes.WinDLL('advapi32',use_last_error=True)
 def refuse(reason):raise RuntimeError(f'store custody refused: {reason}: {target}')
 def need(ok,what):
  if not ok:refuse(f'{what} failed (winerror {ctypes.get_last_error()})')
 k.GetCurrentProcess.restype=w.HANDLE;k.CloseHandle.argtypes=[w.HANDLE]
 k.LocalFree.argtypes=[P];k.LocalFree.restype=P
 k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,P,w.DWORD,w.DWORD,w.HANDLE];k.CreateFileW.restype=w.HANDLE
 k.GetFileInformationByHandle.argtypes=[w.HANDLE,P];k.CreateDirectoryW.argtypes=[w.LPCWSTR,P]
 a.OpenProcessToken.argtypes=[w.HANDLE,w.DWORD,ctypes.POINTER(w.HANDLE)]
 a.GetTokenInformation.argtypes=[w.HANDLE,ctypes.c_int,P,w.DWORD,ctypes.POINTER(w.DWORD)]
 a.EqualSid.argtypes=[P,P];a.IsValidSid.argtypes=[P]
 a.CreateWellKnownSid.argtypes=[ctypes.c_int,P,P,ctypes.POINTER(w.DWORD)]
 a.ConvertSidToStringSidW.argtypes=[P,ctypes.POINTER(P)]
 a.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes=[w.LPCWSTR,w.DWORD,ctypes.POINTER(P),P]
 a.GetSecurityInfo.argtypes=[w.HANDLE,ctypes.c_int,w.DWORD]+[ctypes.POINTER(P)]*5;a.GetSecurityInfo.restype=w.DWORD
 a.GetSecurityDescriptorControl.argtypes=[P,ctypes.POINTER(w.WORD),ctypes.POINTER(w.DWORD)]
 a.GetAclInformation.argtypes=[P,P,w.DWORD,ctypes.c_int];a.GetAce.argtypes=[P,w.DWORD,ctypes.POINTER(P)]
 def text(sid):
  s=P();need(a.ConvertSidToStringSidW(sid,ref(s)),'ConvertSidToStringSid')
  try:return ctypes.wstring_at(s.value)
  finally:k.LocalFree(s)
 def known(kind):
  b=ctypes.create_string_buffer(68);n=w.DWORD(68);need(a.CreateWellKnownSid(kind,None,b,ref(n)),'CreateWellKnownSid');return b
 token=w.HANDLE();need(a.OpenProcessToken(k.GetCurrentProcess(),8,ref(token)),'OpenProcessToken')
 try:
  n=w.DWORD();a.GetTokenInformation(token,1,None,0,ref(n));need(n.value,'GetTokenInformation size')
  held=ctypes.create_string_buffer(n.value);need(a.GetTokenInformation(token,1,held,n,ref(n)),'GetTokenInformation')
 finally:k.CloseHandle(token)
 user=P(ctypes.cast(held,ctypes.POINTER(P))[0]);need(user.value and a.IsValidSid(user),'current user SID')
 system=known(22);allowed=[('user',user),('SYSTEM',system)]
 if create:
  made=P();me=text(user)
  need(a.ConvertStringSecurityDescriptorToSecurityDescriptorW(f'O:{me}D:P(A;OICI;FA;;;{me})(A;OICI;FA;;;SY)',1,ref(made),None),'build security descriptor')
  class Attributes(ctypes.Structure):_fields_=[('size',w.DWORD),('descriptor',P),('inherit',w.BOOL)]
  attributes=Attributes(ctypes.sizeof(Attributes),made,False)
  try:need(k.CreateDirectoryW(target,ref(attributes)),'create new private directory (path must not already exist)')
  finally:k.LocalFree(made)
 # READ_CONTROL on the object itself: OPEN_REPARSE_POINT so a junction is seen, never followed.
 handle=k.CreateFileW(target,0x20000,7,None,3,0x02000000|0x00200000,None)
 need(handle not in (None,P(-1).value),'open directory')
 try:
  info=ctypes.create_string_buffer(52);need(k.GetFileInformationByHandle(handle,info),'GetFileInformationByHandle')
  flags=int.from_bytes(info.raw[:4],'little')
  if not flags&0x10:refuse('not a directory')
  if flags&0x400:refuse('junction, link or other reparse point')
  owner=P();dacl=P();descriptor=P()
  error=a.GetSecurityInfo(handle,1,1|4,ref(owner),None,ref(dacl),None,ref(descriptor))
  if error or not descriptor.value:refuse(f'GetSecurityInfo failed (winerror {error})')
  try:
   control=w.WORD();revision=w.DWORD();need(a.GetSecurityDescriptorControl(descriptor,ref(control),ref(revision)),'GetSecurityDescriptorControl')
   if not owner.value or not a.IsValidSid(owner):refuse('owner cannot be determined')
   if not a.EqualSid(owner,user):refuse(f'owner {text(owner)} is not the current user {text(user)}')
   if not control.value&0x4 or not dacl.value:refuse('no DACL: access is unrestricted')
   if not control.value&0x1000:refuse('DACL is not protected: inherited access can apply')
   size=(w.DWORD*3)();need(a.GetAclInformation(dacl,size,ctypes.sizeof(size),2),'GetAclInformation')
   entries=[]
   for index in range(size[0]):
    ace=P();need(a.GetAce(dacl,index,ref(ace)) and ace.value,'GetAce')
    kind,inherit=ctypes.string_at(ace.value,2);mask=int.from_bytes(ctypes.string_at(ace.value+4,4),'little');sid=P(ace.value+8)
    if kind!=0:refuse(f'unsupported access entry type {kind}')
    if inherit&0x10:refuse('inherited access entry present')
    if not a.IsValidSid(sid):refuse('access entry principal cannot be determined')
    who=[name for name,item in allowed if a.EqualSid(sid,item)]
    if not who:refuse(f'access granted to another principal {text(sid)} (mask {mask:#010x})')
    entries.append(dict(principal=who[0],sid=text(sid),mask=f'{mask:#010x}',flags=inherit))
   if not any(e['principal']=='user' for e in entries):refuse('current user has no access entry')
   return dict(path=target,owner=text(owner),protected=True,created=bool(create),entries=entries)
  finally:k.LocalFree(descriptor)
 finally:k.CloseHandle(handle)
'''
CALL="  result['store_custody']=private_store_directory(store,create=True)\n"
def render(raw):
 assert b'\r' not in raw and b'private_store_directory' not in raw
 lines=raw.decode('utf-8').splitlines(keepends=True)
 m=[i for i,l in enumerate(lines) if l.startswith('def main(args):')];assert len(m)==1
 c=[i for i,l in enumerate(lines) if l.startswith("  command('02-owned-init',")];assert len(c)==1 and c[0]>m[0]
 assert lines[c[0]-1].startswith("  core=[op['python']['path']")
 lines.insert(c[0],CALL);lines.insert(m[0],FUNCTION)
 out=''.join(lines).encode('utf-8');compile(out,'stage_b.py','exec');return out

if __name__=='__main__':
 out=render(Path(sys.argv[1]).read_bytes())
 with Path(sys.argv[2]).open('xb') as f:f.write(out)
 print(sys.argv[2],len(out),hashlib.sha256(out).hexdigest())
