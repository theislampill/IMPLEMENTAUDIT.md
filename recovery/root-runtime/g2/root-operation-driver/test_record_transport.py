"""Linux data-only OS controls. Nine records, no tools/history/G2/admission."""
import argparse,hashlib,json,os,stat,time,types
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 assert os.name=='posix' and os.getuid()==os.geteuid()>0
 out=a.output;assert out.is_absolute() and out.parent.resolve(strict=True)==out.parent and not out.exists();out.mkdir(mode=0o700)
 source=Path(__file__).resolve().with_name('record_transport.py');raw=source.read_bytes()
 R=types.ModuleType('exact_record_transport_control');R.__file__=str(source);exec(compile(raw,str(source),'exec'),R.__dict__)
 cfg={'driver_channel_directory':str(out/'channel'),'SYNTHETIC_ONLY':True};cfgraw=R.encode(cfg);t=R.RecordTransport(cfg,cfgraw)
 checks=[];interleavings=[];real_write=R.os.write;active_cursor=[0]
 def write_interleaving(fd,b):
  n=real_write(fd,b[:max(1,len(b)//2)])
  # A reader scheduled after a normal partial write must observe no committed
  # request at this cursor. No provider callback is replayed by this polling.
  r=R.drain(cfg,cfgraw,active_cursor[0]);assert r['records']==[]
  interleavings.append('partial-temp-not-consumed');return n
 ack=R.encode({'wire_sha256':'a'*64,'wire_bytes':17});original_time=R.time
 for i in range(9):
  active_cursor[0]=i;R.os.write=write_interleaving
  try:t.emit({'event':'tool_request','ordinal':i,'tool':'SYNTHETIC_ONLY_PUBLIC_REQUEST'})
  finally:R.os.write=real_write
  assert R.drain(cfg,cfgraw,i)['records']==[] # READY is separately committed.
  def respond(_seconds):
   records=R.drain(cfg,cfgraw,i);assert len(records['records'])==1
   R.respond(cfg,cfgraw,i,ack)
  R.time=types.SimpleNamespace(time_ns=time.time_ns,sleep=respond)
  try:assert t.frame(4096,2)==ack
  finally:R.time=original_time
  checks.append('actual-record-ready-response-'+str(i))
 # An opened descriptor changed to a device must refuse before os.read.
 target=out/'channel/00.response.json';real_os=R.os;reads=[]
 proxy=types.SimpleNamespace(**{k:getattr(os,k) for k in dir(os)})
 original_fstat=os.fstat
 def changed(fd):
  s=original_fstat(fd);v={k:getattr(s,k) for k in ('st_dev','st_ino','st_nlink','st_size','st_mtime_ns','st_ctime_ns','st_uid')};v['st_mode']=stat.S_IFCHR|0o600;return types.SimpleNamespace(**v)
 proxy.fstat=changed;proxy.read=lambda *x:reads.append(x)
 R.os=proxy
 try:
  try:R.read(target,4096)
  except ValueError as e:assert str(e)=='CHANNEL_OPEN_CHANGED_BEFORE_READ'
  else:raise AssertionError('DEVICE_OPEN_NOT_REFUSED')
 finally:R.os=real_os
 assert reads==[];checks.append('opened-fstat-type-before-payload-read')
 assert interleavings;checks.append('concurrent-reader-partial-publication-waits-for-commit')
 result={'status':'PASS_DATA_ONLY_REAL_POSIX_RECORD_TRANSPORT','checks':checks,'partial_write_interleavings':len(interleavings),'record_transport_source_sha256':hashlib.sha256(raw).hexdigest(),'real_tools':0,'history_reads':0,'G2_runs':0,'live_admissions':0}
 (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
