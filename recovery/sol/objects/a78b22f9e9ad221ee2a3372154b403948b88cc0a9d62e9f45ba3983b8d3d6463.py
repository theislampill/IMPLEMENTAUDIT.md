"""One-shot large/small role body resolver. No URL or limit override interface."""
from pathlib import Path
from contextlib import contextmanager
import json,os,re,select,signal,ssl,sys,termios,time,urllib.request
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import root_common as K
import root_acquire as A

ROOT_BINDING_SHA=None
HELPER_PINS={'root_common.py': {'bytes': 8494, 'sha256': 'f4e2f07b78d4f9acd13f75882ee5faea411a904485a5fbb1c103b49c063615b8'}, 'root_acquire.py': {'bytes': 20704, 'sha256': 'c4eca6f66708215aac994faa9fef1e253466f8898f17a4a612b4e0ec0d1d5c23'}}
CHUNK=K.CHUNK
ROLE_CAPS=K.ROLE_CAPS
WATCHDOG_SECONDS=45
need=K.need

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise K.Refusal('REDIRECT_REFUSED')

@contextmanager
def watchdog(seconds):
    need(0<seconds<=WATCHDOG_SECONDS and signal.getitimer(signal.ITIMER_REAL)==(0.0,0.0),'DEDICATED_RESOLVER_WATCHDOG')
    old=signal.getsignal(signal.SIGALRM)
    def expired(signum,frame):raise TimeoutError('BODY_GET_DEADLINE')
    signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,seconds)
    try:yield
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)

@contextmanager
def open_response(url,seconds):
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect(),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    request=urllib.request.Request(url,headers={'Accept':'application/zip','Accept-Encoding':'identity'},method='GET')
    with watchdog(seconds):
        with opener.open(request,timeout=min(10.0,seconds)) as response:yield response

def stream_once(session,actual_result,*,transport=None,clock=time.monotonic,current=lambda:None):
    """One fixed reference, streamed directly to the held exclusive archive.

    Inert controls may supply a response model; the actual CLI always supplies
    the fixed network transport and compiled-binding currentness callback.
    """
    transport=open_response if transport is None else transport
    selected=session.selected();archive={'bytes':selected['size_in_bytes'],'sha256':selected['digest'][7:]}
    cap=ROLE_CAPS[session.role];need(0<archive['bytes']<=cap,'ROLE_ARCHIVE_BOUND')
    intent=A.parse(A.read(session.path/'download.INTENT.json',16384,True))
    expected_args={'repo_full_name':session.context['repository'],'artifact_id':selected['id'],
      'file_name':K.artifact_name(session.role,session.context)+'.zip'}
    need(intent['tool']==A.DOWNLOAD and intent['arguments']==expected_args,'ACTUAL_DOWNLOAD_INTENT_JOIN')
    note,url=A.download_reference(actual_result,selected['id'],expected_args['file_name'])
    retained=A.parse(session.ready('download'))
    need(retained==note,'ACTUAL_DOWNLOAD_RESULT_CHANGED')
    need(not any((session.path/n).exists() for n in ('BODY_GET_INTENT.json','BODY_GET_OUTCOME.json','ARTIFACT.zip')),'NO_UNCERTAIN_BODY_GET_REPLAY')
    need(session.modules is not None,'BOUND_COMPONENTS_REQUIRED');F=session.modules['fs_io']
    session.bound(32768,3);started=clock();stop=started+WATCHDOG_SECONDS
    value=dict(schema='dg16.g2-body-get-intent.v1',authority='NONE',context=session.context,role=session.role,archive=archive,
      actual_download_result=note['actual_tool_result'],artifact_id=selected['id'],maximum_role_bytes=cap,read_chunk_bytes=CHUNK,
      started_monotonic=started,deadline_monotonic=stop,watchdog_seconds=WATCHDOG_SECONDS,max_body_get_attempts=1,
      automatic_retry=False,redirects_permitted=False,proxies_permitted=False,signed_url_retained=False,
      universal_transport_cancellation_claim=False)
    session.write('BODY_GET_INTENT.json',K.encode(value));attempts=0;total=0;h=__import__('hashlib').sha256();complete=False
    status='REFUSED_OR_UNCERTAIN';actual=None
    def check():
        need(clock()<stop,'BODY_GET_DEADLINE');current();session.bound();need(clock()<stop,'BODY_GET_DEADLINE')
    try:
        check();attempts=1
        with transport(url,WATCHDOG_SECONDS) as response:
            check();need(response.status==200 and response.geturl()==url,'HTTP_STATUS_OR_REFERENCE')
            length=response.headers.get('Content-Length')
            need(length is None or length==str(archive['bytes']),'HTTP_EXACT_LENGTH')
            need(response.headers.get('Content-Encoding') in (None,'identity'),'HTTP_CONTENT_ENCODING')
            with F.Directory(session.path) as directory,F.Output(directory,'ARTIFACT.zip',archive['bytes']) as output:
                while True:
                    check();raw=response.read(min(CHUNK,archive['bytes']-total+1));check()
                    need(type(raw) is bytes,'BODY_BYTES_REQUIRED')
                    if not raw:complete=True;break
                    need(total+len(raw)<=archive['bytes'],'BODY_SIZE_BOUND')
                    output.write(raw);h.update(raw);total+=len(raw);check()
                actual=dict(bytes=total,sha256=h.hexdigest())
                need(actual==archive and output.descriptor(check)==archive,'EXACT_BODY_DESCRIPTOR')
        check();status='RECEIVED'
    except BaseException:
        # No arbitrary exception/type/URL or no-effect inference is persisted.
        status='REFUSED_OR_UNCERTAIN'
    finally:url=None;actual_result=None
    result=dict(schema='dg16.g2-body-get-outcome.v1',authority='NONE',context=session.context,role=session.role,
      status=status,archive=actual if status=='RECEIVED' else None,expected_archive=archive,body_get_attempts=attempts,
      complete_body_observed=complete,retained_prefix=dict(bytes=total,sha256=h.hexdigest()),
      completed_monotonic=clock(),intent=K.desc(K.encode(value)),automatic_retry=False,signed_url_retained=False,
      original_awards=[],universal_transport_cancellation_claim=False,cleanup_or_no_effect_inferred=False)
    session.write('BODY_GET_OUTCOME.json',K.encode(result));return result

def read_ephemeral_frame(maximum=K.METADATA_MAX,seconds=45):
    """ASCII length LF followed by complete actual tool result, without echo."""
    fd=sys.stdin.fileno();need(sys.stdin.isatty(),'NO_ECHO_TERMINAL_REQUIRED')
    old=termios.tcgetattr(fd);quiet=list(old);quiet[6]=list(old[6]);quiet[3]&=~(termios.ECHO|termios.ECHONL|termios.ICANON)
    quiet[6][termios.VMIN]=1;quiet[6][termios.VTIME]=0;termios.tcsetattr(fd,termios.TCSANOW,quiet);stop=time.monotonic()+seconds
    def take(n):
        left=stop-time.monotonic();need(left>0 and select.select([fd],[],[],left)[0],'EPHEMERAL_INPUT_DEADLINE')
        raw=os.read(fd,n);need(bool(raw),'EPHEMERAL_INPUT_TRUNCATED');return raw
    try:
        print('READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME',flush=True);header=b''
        while not header.endswith(b'\n'):header+=take(1);need(len(header)<=9,'EPHEMERAL_HEADER_BOUND')
        need(re.fullmatch(rb'[1-9][0-9]{0,6}\n',header) is not None,'EPHEMERAL_LENGTH');size=int(header);need(size<=maximum,'EPHEMERAL_BODY_BOUND')
        result=bytearray()
        while len(result)<size:result.extend(take(min(65536,size-len(result))))
        return bytes(result)
    finally:termios.tcsetattr(fd,termios.TCSANOW,old)

def main():
    need(len(sys.argv)==2 and sys.flags.isolated and sys.dont_write_bytecode,'FIXED_ISOLATED_RESOLVER_ENTRY')
    need(set(HELPER_PINS)=={'root_common.py','root_acquire.py'} and all(K.desc(K.read(HERE/n,65536))==p for n,p in HELPER_PINS.items()),'RESOLVER_HELPER_PINS')
    b,braw=K.binding(HERE,ROOT_BINDING_SHA);modules=K.components(HERE,b);session=A.Session(Path(sys.argv[1]),b,components=modules)
    def current():
        need(K.binding(HERE,ROOT_BINDING_SHA)==(b,braw),'RESOLVER_BINDING_CHANGED')
        need(all(K.desc(K.read(HERE/n,65536))==p for n,p in HELPER_PINS.items()),'RESOLVER_SOURCE_CHANGED')
    raw=read_ephemeral_frame()
    # Reusing a complete same-result note is permitted; an incomplete note or
    # any prior body intent cannot cause a second GET.
    if (session.path/'download.RESULT.json').exists() or (session.path/'download.READY.json').exists():
        note,_=A.download_reference(raw,session.selected()['id'],K.artifact_name(session.role,session.context)+'.zip')
        need(A.parse(session.ready('download'))==note,'ACTUAL_DOWNLOAD_RESULT_CHANGED')
    else:session.retain('download',raw)
    result=stream_once(session,raw,current=current);raw=None
    print(json.dumps(result,sort_keys=True),flush=True);return 0 if result['status']=='RECEIVED' else 1
if __name__=='__main__':
    try:code=main()
    except BaseException:
        print('{"status":"REFUSED_OR_UNCERTAIN","signed_url_retained":false,"automatic_retry":false,"authority":"NONE"}',flush=True);code=1
    raise SystemExit(code)
