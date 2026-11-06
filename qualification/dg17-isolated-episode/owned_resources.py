"""Linux read-only process/listener inventory and owned filesystem accounting."""
import hashlib,json,os,stat
from pathlib import Path

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  while chunk:=stream.read(1024*1024):h.update(chunk)
 return h.hexdigest()

def processes():
 rows=[]
 for path in Path('/proc').iterdir():
  if not path.name.isdigit():continue
  try:
   raw=(path/'stat').read_text();end=raw.rfind(')');tail=raw[end+2:].split()
   row={'pid':int(path.name),'comm':raw[raw.find('(')+1:end],'state':tail[0],'ppid':int(tail[1]),'pgrp':int(tail[2]),'session':int(tail[3]),'start_ticks':int(tail[19])}
   try:row['exe']=os.readlink(path/'exe')
   except OSError:row['exe']=None
   rows.append(row)
  except (OSError,ValueError,IndexError):continue
 return sorted(rows,key=lambda row:row['pid'])

def listeners():
 rows=[]
 for family in ('tcp','tcp6'):
  for line in Path('/proc/net',family).read_text().splitlines()[1:]:
   fields=line.split()
   if fields[3]=='0A':rows.append({'family':family,'local_address_hex':fields[1],'inode':fields[9]})
 return rows

def inventory(root):
 root=Path(root);rows=[]
 if not root.exists():return rows
 for path in sorted(root.rglob('*')):
  try:
   info=path.lstat()
   row={'path':path.relative_to(root).as_posix(),'mode':stat.S_IMODE(info.st_mode),'bytes':info.st_size,'links':info.st_nlink}
   if stat.S_ISREG(info.st_mode):row.update(kind='file',sha256=digest(path))
   elif stat.S_ISDIR(info.st_mode):row.update(kind='directory')
   elif stat.S_ISLNK(info.st_mode):row.update(kind='symlink',target=os.readlink(path))
   else:row.update(kind='other')
   rows.append(row)
  except FileNotFoundError:rows.append({'path':path.relative_to(root).as_posix(),'kind':'vanished-during-observation'})
 return rows

def bookend(roots):
 return {'processes':processes(),'listeners':listeners(),'roots':{str(root):inventory(root) for root in roots}}
