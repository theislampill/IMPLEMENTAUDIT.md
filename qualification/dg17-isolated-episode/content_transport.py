"""Bounded prospective native stdio and local Responses transport.

Instantiation performs no target or socket action. start() is called only by the
separately admitted hosted probe. No forwarding, retry, shell, PID/name/group kill.
"""
from __future__ import annotations
import errno, os, selectors, signal, socket, subprocess, threading, time
from pathlib import Path

HEADER_LIMIT=32768
BODY_LIMIT=2097152
REQUEST_LIMIT=2
STDOUT_LIMIT=2097152
STDERR_LIMIT=131072
LINE_LIMIT=262144
EVENT_LIMIT=1024

def write_bytes(path, raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,"wb") as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())

def parse_head(raw, port, p):
    p.need(type(raw) is bytes and len(raw)<=HEADER_LIMIT and raw.endswith(b"\r\n\r\n"),"HTTP_HEADER_BOUND")
    try: lines=raw[:-4].decode("ascii","strict").split("\r\n")
    except UnicodeError as exc:raise p.Refusal("HTTP_HEADER_ENCODING") from exc
    p.need(lines and lines[0]=="POST /v1/responses HTTP/1.1","HTTP_ENDPOINT_REFUSED")
    headers={}
    for line in lines[1:]:
        p.need(line and not line[0].isspace() and ":" in line,"HTTP_HEADER_SYNTAX")
        name,value=line.split(":",1);name=name.lower();value=value.strip()
        p.need(name and all(c in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in name)
               and name not in headers and len(value)<=8192,"HTTP_HEADER_DUPLICATE_OR_SHAPE")
        headers[name]=value
    p.need(headers.get("host")=="127.0.0.1:"+str(port) and headers.get("content-type")=="application/json",
           "HTTP_HOST_OR_CONTENT_TYPE")
    p.need(not set(headers)&{"authorization","proxy-authorization","cookie","transfer-encoding","content-encoding","expect"},
           "HTTP_CREDENTIAL_OR_TRANSFER_PROFILE")
    count=headers.get("content-length","")
    p.need(count.isascii() and count.isdecimal() and 1<=len(count)<=8,"HTTP_LENGTH_TYPE")
    length=int(count);p.need(0<length<=BODY_LIMIT,"HTTP_BODY_BOUND")
    return length

class LocalResponses:
    def __init__(self, root, protocol, deadline):
        self.root=Path(root);self.p=protocol;self.deadline=deadline
        self.listener=None;self.active=None;self.thread=None;self.port=None
        self.stop=threading.Event();self.lock=threading.Lock();self.ctx=None
        self.rows=[];self.failure=None;self.accepted=0;self.total=0;self.closed=False;self.joined=False

    def start(self):
        self.p.need(self.listener is None and self.thread is None,"PROVIDER_ALREADY_STARTED")
        self.root.mkdir(mode=0o700)
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.listener=listener
        listener.settimeout(0.1);listener.bind(("127.0.0.1",0));listener.listen(1)
        self.port=listener.getsockname()[1]
        self.p.need(1024<=self.port<=65535,"PROVIDER_EPHEMERAL_PORT")
        self.thread=threading.Thread(target=self._serve,name="dg17-fixed-responses",daemon=False)
        self.thread.start()
        return self.port

    def set_context(self, ctx):
        with self.lock:
            self.p.need(self.ctx is None and self.accepted==0,"PROVIDER_CONTEXT_ALREADY_USED")
            self.ctx=ctx

    def _capture_connection(self, conn, row):
        header=bytearray();body=bytearray();response=b"";head=b"";parsed_head=False
        end=min(self.deadline,time.monotonic()+8)
        try:
            while b"\r\n\r\n" not in header:
                self.p.need(time.monotonic()<end and not self.stop.is_set(),"HTTP_CONNECTION_DEADLINE")
                conn.settimeout(max(0.001,min(0.25,end-time.monotonic())))
                self.p.need(len(header)<HEADER_LIMIT,"HTTP_HEADER_BOUND")
                try:chunk=conn.recv(min(4096,HEADER_LIMIT-len(header)))
                except socket.timeout:continue
                self.p.need(bool(chunk),"HTTP_EARLY_EOF");header.extend(chunk)
                self.p.need(len(header)<=HEADER_LIMIT,"HTTP_HEADER_BOUND")
            offset=header.index(b"\r\n\r\n")+4;head=bytes(header[:offset]);body.extend(header[offset:]);header=bytearray(head)
            length=parse_head(head,self.port,self.p);parsed_head=True
            self.p.need(len(body)<=length,"HTTP_PIPELINED_OR_SURPLUS_BODY")
            while len(body)<length:
                self.p.need(time.monotonic()<end and not self.stop.is_set(),"HTTP_CONNECTION_DEADLINE")
                conn.settimeout(max(0.001,min(0.25,end-time.monotonic())))
                try:chunk=conn.recv(min(16384,length-len(body)))
                except socket.timeout:continue
                self.p.need(bool(chunk),"HTTP_EARLY_EOF");body.extend(chunk)
            self.total+=len(head)+len(body)
            self.p.need(self.total<=2*(BODY_LIMIT+HEADER_LIMIT),"HTTP_AGGREGATE_BOUND")
            with self.lock:ctx=self.ctx
            self.p.need(ctx is not None,"PROVIDER_BEFORE_CONTEXT_ADMISSION")
            row["projection"]=self.p.provider_projection(bytes(body),ctx,row["ordinal"])
            payload=self.p.response_bytes(ctx,row["ordinal"])
            self.p.need(len(payload)<=8192,"SSE_RESPONSE_BOUND")
            response=(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nConnection: close\r\nContent-Length: "+str(len(payload)).encode()+b"\r\n\r\n"+payload)
            row["response_prepared_bytes"]=len(response);row["response_prepared_sha256"]=self.p.sha(response)
            view=memoryview(response)
            while view:
                self.p.need(time.monotonic()<end and not self.stop.is_set(),"HTTP_SEND_DEADLINE")
                conn.settimeout(max(0.001,min(0.25,end-time.monotonic())))
                try:wrote=conn.send(view)
                except socket.timeout:continue
                self.p.need(wrote>0,"HTTP_SEND_EOF");row["response_sent_bytes"]+=wrote;view=view[wrote:]
            row["complete"]=True
        finally:
            row["header_complete"]=parsed_head;row["header_bytes"]=len(header);row["header_sha256"]=self.p.sha(bytes(header))
            row["body_bytes"]=len(body);row["body_sha256"]=self.p.sha(bytes(body))
            for suffix,raw in (("header",bytes(header)),("body",bytes(body)),("response.prepared",response)):
                write_bytes(self.root/(str(row["ordinal"])+"."+suffix),raw)

    def _serve(self):
        try:
            while not self.stop.is_set() and time.monotonic()<self.deadline:
                # Admission is BEFORE accept: never create an unadmitted third accepted socket.
                if self.accepted>=REQUEST_LIMIT:break
                try:conn,address=self.listener.accept()
                except socket.timeout:continue
                except OSError:
                    if self.stop.is_set():break
                    raise
                self.accepted+=1
                row={"ordinal":self.accepted,"loopback_peer":False,"header_complete":False,"header_bytes":0,
                     "header_sha256":None,"body_bytes":0,"body_sha256":None,"projection":None,
                     "response_prepared_bytes":0,"response_prepared_sha256":None,"response_sent_bytes":0,"complete":False}
                self.rows.append(row)
                with self.lock:self.active=conn
                try:
                    self.p.need(address[0]=="127.0.0.1","NONLOOPBACK_PEER");row["loopback_peer"]=True
                    self._capture_connection(conn,row)
                finally:
                    conn.close()
                    with self.lock:self.active=None
        except BaseException as exc:
            self.failure=exc
        finally:
            if self.listener is not None:
                try:self.listener.close();self.closed=True
                except OSError as exc:
                    if self.failure is None:self.failure=exc

    def check(self):
        if self.failure is not None:raise self.failure

    def close(self):
        self.stop.set()
        with self.lock:active=self.active
        if active is not None:
            try:active.shutdown(socket.SHUT_RDWR)
            except OSError:pass
            active.close()
        if self.listener is not None:
            self.listener.close();self.closed=True
        if self.thread is not None:
            self.thread.join(timeout=2)
            self.joined=not self.thread.is_alive()
        else:self.joined=True
        self.p.need(self.joined and self.closed,"PROVIDER_HANDLE_CUSTODY_INCOMPLETE")
        self.check()

    def record(self):
        return {"schema":"dg17.codex.content.provider-private.v1","accepted_socket_count":self.accepted,
                "semantic_request_count":sum(row["projection"] is not None for row in self.rows),
                "listener_closed":self.closed,"thread_joined":self.joined,"non_daemon":True,
                "thread_alive":self.thread is not None and self.thread.is_alive(),"port":self.port,
                "request_rows":self.rows,"failure_type":None if self.failure is None else type(self.failure).__name__}

class NativeSession:
    def __init__(self, root, runtime_root, binary, home, cwd, tmp, modules, protocol, deadline):
        self.root=Path(root);self.launch_dir=Path(runtime_root)/"owned-binary";self.binary=Path(binary)
        self.home=Path(home);self.cwd=Path(cwd);self.tmp=Path(tmp);self.m=modules;self.p=protocol;self.deadline=deadline
        self.proc=None;self.pidfd=None;self.custody=None;self.process_identity=None;self.copy_identity=None
        self.selector=selectors.DefaultSelector();self.open_streams=set();self.stdout=bytearray();self.stderr=bytearray();self.line=bytearray()
        self.events=[];self.sends=bytearray();self.send_records=[];self.responses={};self.pending_ids=set();self.failure=None;self.closed=False
        self.capture=None;self.readback=None;self.launch_removed=False;self.started=False;self.returncode=None
        self.failure_timeout=False;self.failure_output_bound=False
        self.environment={**modules["utility"].safe_environment(),"HOME":str(self.home),"CODEX_HOME":str(self.home),
              "TMPDIR":str(self.tmp),"LANG":"C.UTF-8","LC_ALL":"C.UTF-8",
              "XDG_CONFIG_HOME":str(self.home/"xdg-config"),"XDG_CACHE_HOME":str(self.home/"xdg-cache"),
              "XDG_DATA_HOME":str(self.home/"xdg-data"),"XDG_STATE_HOME":str(self.home/"xdg-state")}
        self.argv=[str(self.launch_dir/"codex"),"app-server","--listen","stdio://","--strict-config"]

    def _remember(self, exc):
        code=str(exc) if isinstance(exc,self.p.Refusal) else None
        self.failure_timeout=self.failure_timeout or code=="NATIVE_WATCHDOG"
        self.failure_output_bound=self.failure_output_bound or code in ("NATIVE_STDIO_BOUND","NATIVE_JSON_LINE_BOUND","NATIVE_EVENT_BOUND")
        if self.failure is None:self.failure=exc

    def _event(self,direction,value):
        self.p.need(len(self.events)<EVENT_LIMIT,"NATIVE_EVENT_BOUND")
        self.events.append({"sequence":len(self.events)+1,"direction":direction,"value":value})

    def prepare_copy(self):
        self.root.mkdir(mode=0o700);self.launch_dir.mkdir(mode=0o700)
        target=self.launch_dir/"codex"
        _,row=self.m["base"].regular_bytes(self.binary,self.m["base"].BINARY_BYTES,os.geteuid(),
             {"bytes":self.m["base"].BINARY_BYTES,"sha256":self.m["base"].BINARY_SHA},copy_to=target)
        self.p.need(target.stat().st_mode&0o777==0o700,"NATIVE_COPY_MODE")
        self.copy_identity=self.m["base"].runtime_guard(target,os.geteuid())

    def start(self):
        try:
            self.p.need(self.proc is None and self.copy_identity is not None,"NATIVE_START_SEQUENCE")
            self.p.need(self.m["base"].runtime_guard(self.launch_dir/"codex",os.geteuid())==self.copy_identity,
                        "NATIVE_COPY_CHANGED_BEFORE_LAUNCH")
            self.custody=self.m["namespace_process_custody"].PidfdCustody()
            self.proc=subprocess.Popen(self.argv,cwd=self.cwd,env=self.environment,stdin=subprocess.PIPE,
                 stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0,start_new_session=True,close_fds=True)
            self.started=True
            self.pidfd=os.pidfd_open(self.proc.pid,0)
            self.process_identity=self.custody.local_snapshot(self.proc.pid)
            self.custody._fd_binding(self.pidfd,self.process_identity)
            self.p.need(self.process_identity["exe"]==str(self.launch_dir/"codex")
                        and self.process_identity["namespace_sessions"][self.custody.depth-1]==self.proc.pid,
                        "NATIVE_SESSION_IDENTITY")
            for name,stream in (("stdout",self.proc.stdout),("stderr",self.proc.stderr)):
                os.set_blocking(stream.fileno(),False);self.selector.register(stream,selectors.EVENT_READ,name);self.open_streams.add(name)
            os.set_blocking(self.proc.stdin.fileno(),False)
        except BaseException as exc:
            self._remember(exc)
            raise

    def _receive_line(self,raw):
        self.p.need(raw and len(raw)<=LINE_LIMIT,"NATIVE_JSON_LINE_BOUND")
        value=self.p.parsed(raw);self.p.need(type(value) is dict,"NATIVE_MESSAGE_OBJECT")
        self._event("receive",value)
        if "id" in value:
            self.p.need(set(value)=={"id","result"} and type(value["id"]) is int
                        and value["id"] in self.pending_ids and value["id"] not in self.responses,
                        "SERVER_REQUEST_ERROR_OR_UNBOUND_RESPONSE")
            self.responses[value["id"]]=value["result"]
        else:
            self.p.need(set(value)=={"method","params","emittedAtMs"} and type(value["emittedAtMs"]) is int
                        and 0<=value["emittedAtMs"]<=9223372036854775807,"NATIVE_NOTIFICATION_ENVELOPE")
            if value.get("method")=="configWarning":
                self.p.refuse_startup_warning(value["params"])
            self.p.need(value["method"] in self.p.ALLOWED_NOTIFICATIONS
                        and type(value["params"]) is dict,"UNKNOWN_NATIVE_NOTIFICATION")

    def pump(self, until, parse=True):
        try:
            wait=max(0,min(0.1,until-time.monotonic()))
            for key,unused in self.selector.select(wait):
                name=key.data;stream=key.fileobj
                try:chunk=os.read(stream.fileno(),16384)
                except BlockingIOError:continue
                if not chunk:
                    self.selector.unregister(stream);self.open_streams.discard(name)
                    if name=="stdout" and self.line:
                        if parse:self._receive_line(bytes(self.line))
                        self.line.clear()
                    continue
                buffer=self.stdout if name=="stdout" else self.stderr;bound=STDOUT_LIMIT if name=="stdout" else STDERR_LIMIT
                remaining=bound-len(buffer);buffer.extend(chunk[:remaining])
                self.p.need(len(chunk)<=remaining,"NATIVE_STDIO_BOUND")
                if name=="stdout" and parse:
                    self.line.extend(chunk)
                    while b"\n" in self.line:
                        offset=self.line.index(b"\n");raw=bytes(self.line[:offset]);del self.line[:offset+1]
                        self._receive_line(raw)
                    self.p.need(len(self.line)<=LINE_LIMIT,"NATIVE_JSON_LINE_BOUND")
        except BaseException as exc:
            self._remember(exc)
            raise

    def send(self,value):
        try:
            self.p.need(self.proc is not None and self.proc.poll() is None,"NATIVE_NOT_RUNNING")
            raw=self.p.compact(value)+b"\n";self.p.need(len(raw)<=32768 and len(self.sends)+len(raw)<=131072,"NATIVE_STDIN_BOUND")
            self._event("send",value)
            row={"method":value["method"],"id":value.get("id"),"prepared_bytes":len(raw),"prepared_sha256":self.p.sha(raw),"written_bytes":0,"complete":False}
            self.send_records.append(row)
            if "id" in value:
                self.p.need(type(value["id"]) is int and value["id"] not in self.pending_ids,"DUPLICATE_RPC_ID")
                self.pending_ids.add(value["id"])
            view=memoryview(raw)
            while view:
                self.p.need(time.monotonic()<self.deadline,"NATIVE_WATCHDOG")
                try:wrote=os.write(self.proc.stdin.fileno(),view)
                except BlockingIOError:self.pump(self.deadline);continue
                self.p.need(wrote>0,"NATIVE_STDIN_CLOSED");self.sends.extend(view[:wrote]);row["written_bytes"]+=wrote;view=view[wrote:]
            row["complete"]=True
        except BaseException as exc:
            self._remember(exc)
            raise

    def request(self,value,provider):
        try:
            self.send(value)
            if "id" not in value:return None
            while value["id"] not in self.responses:
                provider.check();self.p.need(time.monotonic()<self.deadline,"NATIVE_WATCHDOG")
                self.p.need(self.proc.poll() is None or self.open_streams,"NATIVE_EARLY_EXIT")
                self.pump(self.deadline)
            return self.responses[value["id"]]
        except BaseException as exc:
            self._remember(exc)
            raise

    def wait_turn(self,thread_id,turn_id,provider):
        try:
            def completed():
                return any(e["direction"]=="receive" and e["value"].get("method")=="turn/completed"
                           and e["value"]["params"].get("threadId")==thread_id
                           and e["value"]["params"].get("turn",{}).get("id")==turn_id for e in self.events)
            while not completed():
                provider.check();self.p.need(time.monotonic()<self.deadline,"NATIVE_WATCHDOG")
                self.p.need(self.proc.poll() is None or self.open_streams,"NATIVE_EARLY_EXIT")
                self.pump(self.deadline)
        except BaseException as exc:
            self._remember(exc)
            raise

    def _signal_known(self,signum):
        if self.proc is None or self.proc.poll() is not None:return
        if self.pidfd is None:self.pidfd=os.pidfd_open(self.proc.pid,0)
        if self.process_identity is not None:self.custody._fd_binding(self.pidfd,self.process_identity)
        try:signal.pidfd_send_signal(self.pidfd,signum,None,0)
        except ProcessLookupError:pass

    def close(self):
        if self.closed:return self.capture
        self.closed=True;cleanup={"echild":False,"pidfd_signals":0,"reaped_statuses":[]};parse=self.failure is None
        try:
            if self.proc is not None:
                if self.proc.stdin is not None:self.proc.stdin.close()
                end=min(self.deadline+5,time.monotonic()+5)
                while time.monotonic()<end and (self.proc.poll() is None or self.open_streams):
                    try:self.pump(end,parse=parse)
                    except BaseException as exc:self._remember(exc);parse=False
                if self.proc.poll() is None:
                    self._signal_known(signal.SIGTERM)
                    end=time.monotonic()+1
                    while time.monotonic()<end and self.proc.poll() is None:
                        try:self.pump(end,parse=False)
                        except BaseException as exc:self._remember(exc)
                if self.proc.poll() is None:self._signal_known(signal.SIGKILL)
                try:self.returncode=self.proc.wait(timeout=2)
                except subprocess.TimeoutExpired as exc:self._remember(exc)
            try:cleanup=self.m["utility"].stop_owned_children()
            except BaseException as exc:
                cleanup=getattr(exc,"cleanup_partial",cleanup);self._remember(exc)
            end=time.monotonic()+1
            while self.open_streams and time.monotonic()<end:
                try:self.pump(end,parse=parse)
                except BaseException as exc:self._remember(exc);parse=False
            if self.proc is not None:
                self.readback=self.m["admission"].independent_readback(self,self.m)
                self.p.need(self.readback["full_session_scope_available"] and all(self.readback[k]==0 for k in
                   ("living_owned_processes","owned_zombies","uncertain_owned_candidates")) and cleanup.get("echild") is True,
                   "NATIVE_FULL_SESSION_CUSTODY")
                self.p.need(self.m["base"].runtime_guard(self.launch_dir/"codex",os.geteuid())==self.copy_identity,"NATIVE_COPY_CHANGED")
                (self.launch_dir/"codex").unlink();self.launch_removed=True
                self.readback=self.m["admission"].independent_readback(self,self.m)
                self.p.need(self.readback["launch_directory_empty"],"NATIVE_COPY_RETAINED")
        except BaseException as exc:self._remember(exc)
        finally:
            self.selector.close()
            if self.pidfd is not None:os.close(self.pidfd);self.pidfd=None
            if self.proc is not None:
                for stream in (self.proc.stdout,self.proc.stderr):
                    if stream is not None:stream.close()
            retained=False
            try:
                write_bytes(self.root/"native.stdout",bytes(self.stdout));write_bytes(self.root/"native.stderr",bytes(self.stderr))
                write_bytes(self.root/"native.sends.jsonl",bytes(self.sends))
                self.m["base"].write_new(self.root/"NATIVE_SEND_STATUS.json",self.send_records)
                self.m["base"].write_new(self.root/"NATIVE_EVENTS.json",self.events);retained=True
            except BaseException as exc:self._remember(exc)
            code="NATIVE_COMPLETE" if self.failure is None else "NATIVE_CAPTURE_OR_CUSTODY_FAILED"
            self.capture={"name":"native-content","process_started":self.started,"returncode":self.returncode,
                "timeout":self.failure_timeout,
                "output_bound_exceeded":self.failure_output_bound,
                "pidfd_acquired":self.process_identity is not None,"internal_failure":self.failure is not None,
                "reason_code":code,"stream_digest_scope":"CAPTURED_BYTES_ONLY","streams_complete":not self.open_streams and not self.failure_output_bound,
                "stdout_bytes":len(self.stdout),"stderr_bytes":len(self.stderr),"stdout_sha256":self.p.sha(bytes(self.stdout)),
                "stderr_sha256":self.p.sha(bytes(self.stderr)),"cleanup":self.m["utility"].public_cleanup(cleanup),
                "private_streams_retained":retained,"retention_failure":not retained}
            self.m["base"].write_new(self.root/"native.capture.json",[self.capture])
            self.m["base"].write_new(self.root/"NATIVE_OWNERSHIP.json",{"argv":self.argv,"environment":self.environment,
                "process_identity":self.process_identity,"copy_identity":self.copy_identity,"copy_removed":self.launch_removed,
                "full_scope_readback":self.readback})
        if self.failure is not None:raise self.failure
        self.p.need(self.returncode==0 and self.capture["streams_complete"] and self.capture["cleanup"]["echild"] is True,
                   "NATIVE_TERMINAL_CAPTURE_REFUSED")
        return self.capture
