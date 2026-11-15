"""Owned public request/descriptor transport. Never parses terminal screens."""
import hashlib,json,os,re,stat,time
from pathlib import Path

def need(v,c):
 if not v:raise ValueError(c)
def encode(v):return (json.dumps(v,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()
def desc(b):return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def committed(p):
 marker=Path(str(p)+'.COMMITTED')
 if not os.path.lexists(marker):return False
 s=marker.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o600 and s.st_size==0,'COMMIT_MARKER_CUSTODY');return True
def read(p,cap,require_commit=True):
 p=Path(p);need(p.resolve(strict=True)==p,'CHANNEL_PATH_ALIAS');s=p.lstat()
 if require_commit:need(committed(p),'CHANNEL_RECORD_UNCOMMITTED')
 need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o600 and 0<s.st_size<=cap,'CHANNEL_FILE_CUSTODY')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  mark=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
  opened=os.fstat(fd);need(stat.S_ISREG(opened.st_mode) and opened.st_nlink==1 and mark(opened)==mark(s),'CHANNEL_OPEN_CHANGED_BEFORE_READ')
  b=os.read(fd,cap+1);need(len(b)==s.st_size and mark(s)==mark(os.fstat(fd))==mark(p.lstat()),'CHANNEL_READ_CHANGED');return b
 finally:os.close(fd)
def directory(p):
 s=p.lstat();need(stat.S_ISDIR(s.st_mode) and not p.is_symlink() and p.resolve(strict=True)==p and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode)==0o700,'CHANNEL_DIRECTORY')
def write(p,b):
 directory(p.parent);need(len(list(p.parent.iterdir()))<64,'CHANNEL_ENTRY_BOUND')
 temp=Path(str(p)+'.WRITING')
 fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  os.fchmod(fd,0o600);view=memoryview(b)
  while view:n=os.write(fd,view);need(n>0,'CHANNEL_SHORT_WRITE');view=view[n:]
  os.fsync(fd)
 finally:os.close(fd)
 # link() is atomic and refuses an existing final name. Until COMMITTED is
 # exposed, readers cannot treat a partial/crashed publication as a frame.
 os.link(temp,p,follow_symlinks=False);os.unlink(temp)
 fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 need(read(p,len(b),False)==b,'CHANNEL_WRITE_READBACK')
 marker=Path(str(p)+'.COMMITTED')
 fd=os.open(marker,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:os.fchmod(fd,0o600);os.fsync(fd)
 finally:os.close(fd)
 fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def safe(value):
 text=encode(value);need(len(text)<=32768,'PUBLIC_EVENT_BOUND')
 need(not any(x in text.lower() for x in (b'download_url',b'file_uri',b'?sig=',b'authorization',b'raw_history',b'://sdmnt')),'PUBLIC_EVENT_SECRET_REFUSED');return text
class RecordTransport:
 def __init__(self,cfg,configuration_raw):self.cfg=cfg;self.path=Path(cfg['driver_channel_directory']);self.pin=desc(configuration_raw)['sha256'];self.sequence=0;self.pending=None;self.created=False
 def _ensure(self):
  if not self.created:self.path.mkdir(mode=0o700);self.created=True
  directory(self.path)
 def emit(self,value):
  self._ensure();raw=safe(dict(sequence=self.sequence,configuration_sha256=self.pin,value=value))
  p=self.path/('%02d.request.json'%self.sequence);write(p,raw)
  if value.get('event')=='tool_request':need(self.pending is None,'PENDING_FRAME');self.pending=(self.sequence,desc(raw))
  self.sequence+=1
 def frame(self,maximum,seconds):
  need(self.pending is not None and maximum<=4096 and 0<seconds<=45,'EXACT_PENDING_DESCRIPTOR_FRAME')
  sequence,request=self.pending;deadline=time.time_ns()//1000000+int(seconds*1000)
  ready=dict(sequence=sequence,configuration_sha256=self.pin,request=request,deadline_ms=deadline,maximum=maximum)
  write(self.path/('%02d.READY.json'%sequence),encode(ready));p=self.path/('%02d.response.json'%sequence)
  while time.time_ns()//1000000<deadline:
   if committed(p):
    raw=read(p,maximum);v=json.loads(raw);need(type(v) is dict and set(v)=={'wire_sha256','wire_bytes'} and re.fullmatch('[0-9a-f]{64}',v['wire_sha256']) and type(v['wire_bytes']) is int and 0<v['wire_bytes']<=4*1024**2,'DESCRIPTOR_ONLY_RESPONSE')
    need(time.time_ns()//1000000<deadline,'FRAME_LATE');self.pending=None;return raw
   time.sleep(.05)
  raise ValueError('DESCRIPTOR_FRAME_TIMEOUT_NO_REPLAY')
def drain(cfg,raw_cfg,cursor):
 p=Path(cfg['driver_channel_directory']);pin=desc(raw_cfg)['sha256'];need(type(cursor) is int and 0<=cursor<=12,'CHANNEL_CURSOR')
 if not p.exists():return {'records':[],'next_cursor':cursor}
 directory(p);out=[]
 while committed(p/('%02d.request.json'%cursor)):
  raw=read(p/('%02d.request.json'%cursor),32768);v=json.loads(raw);need(v.get('sequence')==cursor and v.get('configuration_sha256')==pin,'EXACT_CHANNEL_RECORD')
  value=v['value'];safe(value);record=dict(sequence=cursor,value=value,request=desc(raw),ready=None)
  if value.get('event')=='tool_request':
   ready=p/('%02d.READY.json'%cursor)
   if not committed(ready):break
   r=json.loads(read(ready,4096));need(r['request']==desc(raw) and r['sequence']==cursor and r['configuration_sha256']==pin and time.time_ns()//1000000<r['deadline_ms'],'EXACT_READY_RECORD')
   record['ready']=r
  out.append(record);cursor+=1
  need(cursor<=12,'CHANNEL_RECORD_BOUND')
 return {'records':out,'next_cursor':cursor}
def respond(cfg,raw_cfg,sequence,descriptor_raw):
 p=Path(cfg['driver_channel_directory']);directory(p);pin=desc(raw_cfg)['sha256'];ready=json.loads(read(p/('%02d.READY.json'%sequence),4096))
 request=read(p/('%02d.request.json'%sequence),32768)
 need(ready['configuration_sha256']==pin and ready['sequence']==sequence and ready['request']==desc(request) and time.time_ns()//1000000<ready['deadline_ms'],'EXACT_CURRENT_READY')
 v=json.loads(descriptor_raw);need(type(v) is dict and set(v)=={'wire_sha256','wire_bytes'} and re.fullmatch('[0-9a-f]{64}',v['wire_sha256']) and type(v['wire_bytes']) is int and 0<v['wire_bytes']<=4*1024**2,'DESCRIPTOR_ONLY_RESPONSE')
 write(p/('%02d.response.json'%sequence),descriptor_raw);return {'status':'EXACT_DESCRIPTOR_RESPONSE_WRITTEN','sequence':sequence,'descriptor':v}
