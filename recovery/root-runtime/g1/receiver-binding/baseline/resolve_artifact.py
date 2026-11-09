"""Fixed one-shot G1 artifact-body resolver, callable only by the root runtime.

One exact file reference from the already-retained real download result; no
URL/host/size/digest CLI overrides, redirects, retry, or tool dispatch. This
module's network function is never invoked by the author's inert controls.
"""
import hashlib,json,os,re,select,signal,ssl,sys,termios,time,types,urllib.error,urllib.parse,urllib.request
from contextlib import contextmanager
from pathlib import Path
BASE=Path(__file__).resolve().parent
RECEIVER_SHA='71e205118bbaca3caf69868441fa0266b53d40095aca7641b85da5ea6d8d2e74'
WATCHDOG_SECONDS=45

class Refusal(ValueError):pass
class WatchdogExpired(TimeoutError):pass

def need(ok,code):
    if not ok:raise Refusal(code)

def receiver():
    raw=(BASE/'receiver.py').read_bytes();need(hashlib.sha256(raw).hexdigest()==RECEIVER_SHA,'RECEIVER_SOURCE_CHANGED')
    m=types.ModuleType('fixed_root_receiver');m.__file__=str(BASE/'receiver.py');exec(compile(raw,m.__file__,'exec'),m.__dict__);return m


def exact_reference(R,session,actual_download_result):
    note=R.parse(session.ready('download'));intent=R.parse(R.read(session.path/'download.INTENT.json'))
    need(R.desc(actual_download_result)==note['actual_tool_result'],'ACTUAL_DOWNLOAD_RESULT_CHANGED')
    actual=R.download_note(actual_download_result,intent['arguments']['artifact_id'],intent['arguments']['file_name'])
    need(actual==note,'ACTUAL_DOWNLOAD_REFERENCE_CHANGED')
    value=R.parse(actual_download_result);outer=value['structuredContent'];rows=[outer]
    if 'structuredContent' in outer:rows.append(outer['structuredContent'])
    urls=[]
    for row in rows:
        uri=row['file_uri'];need(set(uri)=={'download_url','file_id','mime_type','file_name'},'ACTUAL_FILE_REFERENCE_SHAPE')
        urls.append(uri['download_url'])
        if 'download_url' in row:urls.append(row['download_url'])
    need(urls and all(type(x) is str and x==urls[0] for x in urls),'EXACT_DUPLICATE_DOWNLOAD_REFERENCE')
    url=urls[0];need(0<len(url.encode())<=16384 and not any(ord(x)<33 or ord(x)==127 for x in url),'EPHEMERAL_REFERENCE_BOUND')
    parts=urllib.parse.urlsplit(url)
    need(parts.scheme=='https' and not parts.username and not parts.password and not parts.fragment and parts.port in (None,443),'EPHEMERAL_HTTPS_REFERENCE')
    host=parts.hostname
    # Observed connector storage family, not a caller-selected transport target.
    need(type(host) is str and re.fullmatch(r'sdmntpr[a-z0-9-]+\.oaiusercontent\.com',host),'FIXED_CONNECTOR_STORAGE_FAMILY')
    need(parts.path.startswith('/') and bool(parts.query),'RETURNED_EPHEMERAL_REFERENCE_REQUIRED')
    return url,dict(file_id=note['file_id'],artifact_id=note['artifact_id'],file_name=note['file_name'],
      actual_download_tool_result=note['actual_tool_result'],reference=R.desc(url.encode()),download_host=host)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise Refusal('REDIRECT_REFUSED')


@contextmanager
def request_watchdog(seconds):
    """Process signal plus socket timeout, with late acceptance refused below.

    This is not a connector cancellation API or a universal cancellation claim.
    If runtime transport does not return, the retained intent still forbids replay.
    """
    need(0<seconds<=WATCHDOG_SECONDS,'WATCHDOG_BOUND')
    prior=signal.getitimer(signal.ITIMER_REAL);need(prior==(0.0,0.0),'DEDICATED_RESOLVER_PROCESS_REQUIRED')
    old=signal.getsignal(signal.SIGALRM)
    def expired(signum,frame):raise WatchdogExpired()
    signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,seconds)
    try:yield
    finally:signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)


def fetch_once(url,maximum,seconds):
    """The only network boundary. One GET, no redirects or retry handlers."""
    need(type(maximum) is int and 0<maximum<=262144,'FIXED_G1_ZIP_CAP');need(0<seconds<=WATCHDOG_SECONDS,'GET_TIMEOUT_BOUND')
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect(),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    request=urllib.request.Request(url,headers={'Accept':'application/zip'},method='GET')
    with request_watchdog(seconds):
        with opener.open(request,timeout=seconds) as response:
            need(response.status==200,'HTTP_STATUS_REFUSED')
            need(response.geturl()==url,'RESPONSE_REFERENCE_CHANGED')
            content_length=response.headers.get('Content-Length')
            if content_length is not None:need(content_length.isdigit() and 0<int(content_length)<=maximum,'HTTP_BODY_LENGTH_REFUSED')
            body=response.read(maximum+1)
            need(type(body) is bytes and 0<len(body)<=maximum,'COMPLETE_BOUNDED_BODY_REQUIRED')
            if content_length is not None:need(len(body)==int(content_length),'HTTP_BODY_LENGTH_CHANGED')
            return body


def resolve(R,session,actual_download_result,*,transport=None,clock=None):
    """Core state machine. Tests supply inert transport/clock, never this GET."""
    transport=fetch_once if transport is None else transport;clock=time.monotonic if clock is None else clock
    url,reference=exact_reference(R,session,actual_download_result);a=session.artifact();cap=R.PHASES[session.plan['phase']][2]
    need(type(a.get('size_in_bytes')) is int and 0<a['size_in_bytes']<=cap and type(a.get('digest')) is str and re.fullmatch('sha256:[0-9a-f]{64}',a['digest']),'ACTUAL_PROVIDER_BODY_DESCRIPTOR')
    need(not any((session.path/n).exists() for n in ('BODY_GET_INTENT.json','BODY_GET_OUTCOME.json','ARTIFACT.zip')),'NO_UNCERTAIN_BODY_GET_REPLAY')
    seconds=min(WATCHDOG_SECONDS,session.s.binding['limits']['command_seconds']);need(0<seconds<=45,'FIXED_WATCHDOG')
    session.bound(cap+16384,3);started=clock();deadline=started+seconds
    intent=dict(schema='dg16.root-artifact-body-intent.v1',authority='NONE',source_index_sha256=R.SOURCE_SHA,phase=session.plan['phase'],
      context=session.plan['context'],download=reference,expected_body=dict(bytes=a['size_in_bytes'],sha256=a['digest'][7:]),zip_cap=cap,
      max_resolver_body_get_attempts=1,automatic_retry=False,redirects_permitted=False,started_monotonic=started,
      acceptance_deadline_monotonic=deadline,watchdog_seconds=seconds,signed_url_retained=False,
      connector_cancellation_provided=False,universal_transport_cancellation_claim=False)
    # Durable exclusive intent and maximum-result capacity precede the one GET.
    session.write('BODY_GET_INTENT.json',R.encode(intent));attempts=0;body=None;code='BODY_GET_UNCERTAIN';completed=False
    try:
        need(clock()<deadline,'BODY_GET_START_DEADLINE');attempts=1
        body=transport(url,cap,seconds)
        completed=type(body) is bytes and 0<len(body)<=cap
        need(clock()<deadline,'BODY_GET_RETURNED_AFTER_DEADLINE')
        need(completed,'COMPLETE_BOUNDED_BODY_REQUIRED')
        need(R.desc(body)==intent['expected_body'],'ACTUAL_BODY_DIGEST_OR_SIZE_CHANGED')
        # Session.body writes the exact archive exclusively, fsyncs and reads back.
        session.body(body);code='EXACT_BODY_RECEIVED'
    except (Exception,KeyboardInterrupt):
        # No arbitrary message/type/URL echo or inferred no-effect conclusion.
        code='BODY_GET_REFUSED_OR_UNCERTAIN'
    finally:
        url=None;actual_download_result=None
    result=dict(schema='dg16.root-artifact-body-outcome.v1',authority='NONE',intent=R.desc(R.encode(intent)),phase=session.plan['phase'],
      context=session.plan['context'],download=reference,status='RECEIVED' if code=='EXACT_BODY_RECEIVED' else 'REFUSED_OR_UNCERTAIN',
      code=code,resolver_body_get_attempts=attempts,complete_body_observed=completed,observed_body=R.desc(body) if type(body) is bytes else None,
      retained_archive=R.desc(R.read(session.path/'ARTIFACT.zip',cap)) if (session.path/'ARTIFACT.zip').exists() else None,
      readback='EXACT' if code=='EXACT_BODY_RECEIVED' else 'NOT_AWARDED',completed_monotonic=clock(),automatic_retry=False,
      signed_url_retained=False,connector_cancellation_provided=False,universal_transport_cancellation_claim=False,
      cleanup_or_no_effect_inferred=False,authentication_boundary=R.AUTH,effect_grant=False,original_awards=[])
    session.write('BODY_GET_OUTCOME.json',R.encode(result));return result


def read_ephemeral_frame(maximum,seconds=45):
    """No-echo framed TTY input: ASCII byte length, LF, then exact raw JSON bytes.

    Noncanonical mode avoids terminal line-buffer truncation. No input or URL is
    written to disk, source, argv, environment, reports or stdout by this helper.
    """
    fd=sys.stdin.fileno();need(sys.stdin.isatty(),'NO_ECHO_TERMINAL_REQUIRED');old=termios.tcgetattr(fd);quiet=list(old);quiet[6]=list(old[6]);quiet[3]&=~(termios.ECHO|termios.ECHONL|termios.ICANON);quiet[6][termios.VMIN]=1;quiet[6][termios.VTIME]=0
    termios.tcsetattr(fd,termios.TCSANOW,quiet);deadline=time.monotonic()+seconds
    def take(n):
        remaining=deadline-time.monotonic();need(remaining>0 and select.select([fd],[],[],remaining)[0],'EPHEMERAL_INPUT_DEADLINE');b=os.read(fd,n);need(bool(b),'EPHEMERAL_INPUT_TRUNCATED');return b
    try:
        print('READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME',flush=True);header=b''
        while not header.endswith(b'\n'):
            header+=take(1);need(len(header)<=9,'EPHEMERAL_FRAME_HEADER')
        need(re.fullmatch(rb'[1-9][0-9]{0,6}\n',header) is not None,'EPHEMERAL_FRAME_LENGTH');length=int(header);need(length<=maximum,'EPHEMERAL_FRAME_BOUND')
        raw=bytearray()
        while len(raw)<length:raw.extend(take(min(65536,length-len(raw))))
        return bytes(raw)
    finally:termios.tcsetattr(fd,termios.TCSANOW,old)


def receive_download_for_resolution(R,session,actual_download_result):
    """Safely retain the just-returned result from the same no-echo frame.

    Existing complete identical receiving may be read back; partial or rejected
    retention is never completed or replaced by this entrypoint.
    """
    need((session.path/'download.INTENT.json').exists(),'DOWNLOAD_RESERVATION_REQUIRED')
    if any((session.path/n).exists() for n in ('download.RESULT.json','download.READY.json')):
        note=R.parse(session.ready('download'))
        need(R.desc(actual_download_result)==note['actual_tool_result'],'ACTUAL_DOWNLOAD_RESULT_CHANGED')
        intent=R.parse(R.read(session.path/'download.INTENT.json'))
        need(R.download_note(actual_download_result,intent['arguments']['artifact_id'],intent['arguments']['file_name'])==note,'ACTUAL_DOWNLOAD_REFERENCE_CHANGED')
    else:session.retain('download',actual_download_result)


def main():
    need(len(sys.argv)==2 and sys.flags.isolated==1 and sys.dont_write_bytecode,'FIXED_ISOLATED_RESOLVER_ENTRY')
    R=receiver();s=R.Sources();session=R.Session(Path(sys.argv[1]),s)
    raw=read_ephemeral_frame(R.MAX_RESULT);receive_download_for_resolution(R,session,raw);result=resolve(R,session,raw);raw=None
    print(json.dumps(result,sort_keys=True),flush=True);return 0 if result['status']=='RECEIVED' else 1

if __name__=='__main__':
    try:code=main()
    except BaseException:
        print('{"authority":"NONE","status":"REFUSED_OR_UNCERTAIN","automatic_retry":false,"signed_url_retained":false}',flush=True);code=1
    raise SystemExit(code)
