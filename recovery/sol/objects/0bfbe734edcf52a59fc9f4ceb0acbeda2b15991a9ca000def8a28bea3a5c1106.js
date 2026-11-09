/* Concrete Root-only Windows/WSL TTY adapter for provider_slots.runSeven.
 * No global start. Config paths contain no tool result, signed URL or secret.
 * Actual admission/source validation is performed by the pinned role process;
 * Root must receive the installed launcher and qualified no-echo boundary.
 */
function need(v,c){if(!v)throw Error(c);}
function quote(s){need(typeof s==='string'&&!/[\r\n\u0000]/.test(s),'LITERAL_PATH');return "'"+s.replaceAll("'","''")+"'";}
function bytes(s){let n=0;for(const ch of s){const c=ch.codePointAt(0);n+=c<128?1:c<2048?2:c<65536?3:4;}return n;}
function decodeConpty(raw,title,terminal=false){
  // Received 24x80 ConPTY scroll painter: an incomplete ASCII JSON line at
  // column80 is continued by CRLF + CUP23;80 + an IDENTICAL last-cell repaint.
  // Reject any changed cell, cursor overwrite, foreign control or broken JSON.
  const allowed=new Set(['\x1b[?9001h','\x1b[?1004h','\x1b[?25l','\x1b[2J','\x1b[m','\x1b[H','\x1b[?25h','\x1b[?9001l','\x1b[?1004l']);
  let line='',wrap=null,overlap=null,scrollLF=false,pending=false,titleSeen=false;const records=[];
  const eventLine=()=>{let value;try{value=JSON.parse(line);}catch(_e){throw Error('ROLE_PROTOCOL_JSON');}
    need(value&&['intent','retained','complete','failure'].includes(value.event),'ROLE_PROTOCOL_EVENT');return value;};
  for(let i=0;i<raw.length;){
    if(raw[i]==='\x1b'){
      const tail=raw.slice(i);let seq;
      if(tail.startsWith('\x1b[')){
        const m=/^\x1b\[[0-9;?]*[ -/]*[@-~]/.exec(tail);
        if(!m){need(tail.length<=16,'TERMINAL_CSI_BOUND');pending=true;break;}seq=m[0];
        if(seq==='\x1b[23;80H'){
          need(wrap!==null&&line===''&&overlap===null&&!scrollLF,'UNEXPECTED_CONPTY_LAST_COLUMN_REPAINT');
          line=wrap;overlap=wrap.at(-1);wrap=null;
        }else if(seq==='\x1b[24;1H'){
          need(line.length>0&&line.length%80===0&&wrap===null&&overlap===null&&!scrollLF,'UNSAFE_CONPTY_SCROLL_MOVE');
          eventLine();scrollLF=true; // No record committed until real LF.
        }else if(seq==='\x1b[?25h'||seq==='\x1b[?25l'){
          // ConPTY may asynchronously reveal/hide its cursor during the first
          // long record. Visibility changes do not move or rewrite a cell.
        }else{
          need(line===''&&wrap===null&&overlap===null&&!scrollLF&&allowed.has(seq),'UNRECEIVED_TERMINAL_CSI');
          if(seq==='\x1b[2J'||seq==='\x1b[H')need(records.length===0,'CURSOR_CLEAR_OR_HOME_AFTER_COMMITTED_PROTOCOL');
        }
      }else if(tail.startsWith('\x1b]')){
        const bell=tail.indexOf('\x07');if(bell<0){need(tail.length<=520,'TERMINAL_TITLE_BOUND');pending=true;break;}
        seq=tail.slice(0,bell+1);
        need(seq==='\x1b]0;'+title+'\x07'&&!titleSeen&&
          (records.length===0||(line===''&&wrap===null&&overlap===null&&!scrollLF)),
          'UNRECEIVED_TERMINAL_TITLE');titleSeen=true;
      }else if(tail==='\x1b'){pending=true;break;}else throw Error('UNRECEIVED_TERMINAL_ESCAPE');
      i+=seq.length;continue;
    }
    if(raw[i]==='\r'){
      if(i+1===raw.length){pending=true;break;}need(raw[i+1]==='\n','STRAY_TERMINAL_CARRIAGE_RETURN');i++;
    }
    const ch=raw[i++];
    if(scrollLF){need(ch==='\n','OVERWRITTEN_CONPTY_RECORD');scrollLF=false;}
    if(ch==='\n'){
      need(overlap===null&&wrap===null,'BROKEN_CONPTY_CONTINUATION');
      if(line==='')continue;
      if(line==='READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME'){records.push({ready:true});line='';continue;}
      need(line.startsWith('{'),'UNEXPECTED_ROLE_OUTPUT');
      try{records.push({value:eventLine()});line='';}
      catch(e){
        if(e.message!=='ROLE_PROTOCOL_JSON'||line.length%80!==0)throw e;
        wrap=line;line=''; // Wait for exact idempotent last-column repaint.
      }
      continue;
    }
    need(wrap===null,'BROKEN_CONPTY_CONTINUATION');
    if(overlap!==null){need(ch===overlap,'CHANGED_CONPTY_LAST_COLUMN');overlap=null;continue;}
    need(ch>=' '&&ch<='~','NON_ASCII_SAFE_ROLE_OUTPUT');line+=ch;need(line.length<=65536,'SAFE_PROTOCOL_LINE_BOUND');
  }
  const incomplete=pending||line!==''||wrap!==null||overlap!==null||scrollLF;
  need(!terminal||!incomplete,'TRUNCATED_TERMINAL_PROTOCOL');return {records,incomplete};
}
class WindowsRoleIO{
  constructor(tools,selection){
    this.tools=tools;this.selection=Object.freeze({...selection});this.session=null;this.buffer='';this.events=[];
    this.echoReady=false;this.bodyDone=false;this.terminal=false;this.deadline=null;this.last=null;
    this.controlPending='';
    this.rawProtocol='';this.decodedRecords=[];
    this.launchAttempted=false;
    need(selection.distribution==='Ubuntu'&&selection.user==='agent'&&selection.python==='/usr/bin/python3','RECEIVED_FIXED_PLATFORM');
    for(const k of ['rolePath','configurationPath'])need(typeof selection[k]==='string'&&selection[k].startsWith('/')&&!selection[k].split('/').includes('..'),'FIXED_ROLE_PATH');
    need(typeof selection.configurationSha256==='string'&&/^[0-9a-f]{64}$/.test(selection.configurationSha256),'ACTUAL_ROOT_CONFIGURATION_PIN');
    need(typeof selection.roleSha256==='string'&&/^[0-9a-f]{64}$/.test(selection.roleSha256),'ACTUAL_ROOT_ROLE_SOURCE_PIN');
    need(typeof selection.shellTitle==='string'&&selection.shellTitle.length<=512&&!/[\r\n\u0000\u0007\u001b]/.test(selection.shellTitle),'RECEIVED_SHELL_TITLE');
  }
  _decorations(text){
    const allowed=new Set(['\x1b[?9001h','\x1b[?1004h','\x1b[?25l','\x1b[2J','\x1b[m','\x1b[H','\x1b[?25h','\x1b[?9001l','\x1b[?1004l']);
    let raw=this.controlPending+text;this.controlPending='';let clean='',boundary=this.buffer.length===0;
    for(let i=0;i<raw.length;){
      if(raw[i]!=='\x1b'){const ch=raw[i++];clean+=ch;boundary=ch==='\n';continue;}
      need(boundary,'TERMINAL_CONTROL_INSIDE_PROTOCOL_TEXT');
      const tail=raw.slice(i);let end=-1,seq;
      if(tail.startsWith('\x1b[')){
        const match=/^\x1b\[[0-9;?]*[ -/]*[@-~]/.exec(tail);
        if(!match){need(tail.length<=16,'TERMINAL_CSI_BOUND');this.controlPending=tail;break;}
        seq=match[0];need(allowed.has(seq),'UNRECEIVED_TERMINAL_CSI');end=seq.length;
      }else if(tail.startsWith('\x1b]')){
        const bell=tail.indexOf('\x07');
        if(bell<0){need(tail.length<=520,'TERMINAL_TITLE_BOUND');this.controlPending=tail;break;}
        seq=tail.slice(0,bell+1);need(seq==='\x1b]0;'+this.selection.shellTitle+'\x07','UNRECEIVED_TERMINAL_TITLE');end=seq.length;
      }else if(tail==='\x1b'){this.controlPending=tail;break;}
      else throw Error('UNRECEIVED_TERMINAL_ESCAPE');
      i+=end;
    }
    return clean;
  }
  _accept(response){
    need(response&&typeof response.output==='string','ACTUAL_EXEC_RESPONSE');
    if(response.exit_code==null)need(Number.isSafeInteger(response.session_id)&&response.session_id>0,'UNKNOWN_ROLE_PROCESS_CUSTODY_NO_TOOL');
    if(response.session_id!=null){need(Number.isSafeInteger(response.session_id)&&response.session_id>0&&(this.session===null||this.session===response.session_id),'OWNED_SESSION_CHANGED');this.session=response.session_id;}
    // Trusted process completion is distinct from validity of its untrusted
    // stdout. Preserve terminal custody even when protocol parsing refuses.
    if(response.exit_code!=null){need(Number.isSafeInteger(response.exit_code),'INVALID_PROCESS_EXIT_CODE');this.terminal=true;this.last=response.exit_code;}
    this.rawProtocol+=response.output;need(this.rawProtocol.length<=65536,'SAFE_PROTOCOL_OUTPUT_BOUND');
    const decoded=decodeConpty(this.rawProtocol,this.selection.shellTitle,response.exit_code!=null);
    need(decoded.records.length>=this.decodedRecords.length,'REPAINTED_COMMITTED_PROTOCOL');
    for(let i=0;i<this.decodedRecords.length;i++)need(JSON.stringify(decoded.records[i])===JSON.stringify(this.decodedRecords[i]),'OVERWRITTEN_COMMITTED_PROTOCOL');
    for(const record of decoded.records.slice(this.decodedRecords.length)){
      if(record.ready)this.echoReady=true;else this.events.push(record.value);
    }
    this.decodedRecords=decoded.records;this.controlPending=decoded.incomplete?'PENDING_PROTOCOL':'';
  }
  async _poll(){
    need(this.session!==null&&!this.terminal,'OWNED_ROLE_NOT_RUNNING');
    this._accept(await this.tools.write_stdin({session_id:this.session,chars:'',yield_time_ms:1000,max_output_tokens:5000}));
  }
  async _until(predicate,allowSuccessfulTerminal=false){
    for(;;){
      need(Date.now()<this.deadline,'ACTUAL_ROOT_ROLE_DEADLINE');
      const failure=this.events.find(x=>x.event==='failure');need(!failure,'ROLE_REFUSED_OR_UNKNOWN');
      if(predicate()){
        need(Number.isSafeInteger(this.session)&&this.session>0,'OWNED_ROLE_SESSION_REQUIRED_BEFORE_TOOL');
        need(!this.terminal||(allowSuccessfulTerminal&&this.last===0),'ROLE_TERMINATED_BEFORE_EXPECTED_EVENT');
        return;
      }
      need(!this.terminal,'ROLE_TERMINATED_BEFORE_EXPECTED_EVENT');await this._poll();
    }
  }
  async assertAdmitted(deadline){
    need(this.session===null&&!this.launchAttempted&&Number.isSafeInteger(deadline)&&Date.now()<deadline,'ONE_ROOT_ROLE_START');this.deadline=deadline;
    // Same descriptor/type/hash/bookend loader boundary as Root's received
    // dispatcher02; the role source is never selected by provider content.
    const loader="import hashlib,os,pathlib,stat,sys; p=pathlib.Path(sys.argv[1]); pin=sys.argv[2]; mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns); s=p.lstat(); assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid() and stat.S_IMODE(s.st_mode) in (0o400,0o444) and 0<s.st_size<=1048576; fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC); opened=os.fstat(fd); assert mark(opened)==mark(s) and stat.S_ISREG(opened.st_mode) and not os.listxattr(fd); raw=os.pread(fd,s.st_size+1,0); assert len(raw)==s.st_size and hashlib.sha256(raw).hexdigest()==pin and mark(os.fstat(fd))==mark(s) and mark(p.lstat())==mark(s); os.close(fd); sys.argv=[str(p),*sys.argv[3:]]; exec(compile(raw,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})";
    const s=this.selection;const argv=['C:\\Windows\\System32\\wsl.exe','--distribution',s.distribution,'--user',s.user,'--cd','/','--exec',s.python,'-I','-B','-c',loader,s.rolePath,s.roleSha256,'--configuration',s.configurationPath,'--configuration-sha256',s.configurationSha256];
    const cmd="$PSNativeCommandArgumentPassing='Standard'; & "+argv.map(quote).join(' ')+"; exit $LASTEXITCODE";
    need(cmd.length<=18000,'FIXED_WINDOWS_LAUNCH_BOUND');
    this.launchAttempted=true;
    this._accept(await this.tools.exec_command({cmd,login:false,tty:true,yield_time_ms:1000,max_output_tokens:5000}));
    await this._until(()=>this.events.some(x=>x.event==='intent')&&this.echoReady&&this.controlPending==='');
  }
  async reserve(kind){
    await this._until(()=>this.events.some(x=>x.event==='intent')&&this.echoReady&&this.controlPending==='');
    const event=this.events.shift();need(event.event==='intent'&&event.intent.kind===kind,'EXACT_ROLE_ORDINAL');
    return event.intent; // Already exclusively reserved/fsynced by real Session.
  }
  async retain(kind,actual){
    need(this.echoReady&&this.controlPending===''&&this.session!==null&&!this.terminal&&Date.now()<this.deadline,'NOECHO_ROLE_FRAME_NOT_READY');
    const raw=JSON.stringify(actual);const length=bytes(raw);need(length>0&&length<=4194304,'FRAME_BOUND');
    this.echoReady=false;
    // Same qualified no-echo TTY frame boundary used by Root. No URL/result is
    // interpolated into a shell command, environment or file. No raw logging.
    this._accept(await this.tools.write_stdin({session_id:this.session,chars:String(length)+'\n'+raw,yield_time_ms:1000,max_output_tokens:5000}));
    await this._until(()=>this.events.some(x=>x.event==='retained'),true);
    const index=this.events.findIndex(x=>x.event==='retained');const event=this.events.splice(index,1)[0];
    need(event.kind===kind,'ROLE_RETAINED_ORDINAL');if(kind==='download'){need(event.body_get_done===true,'ONE_EPHEMERAL_BODY_NOT_RECEIVED');this.bodyDone=true;}
    return event;
  }
  async receiveEphemeralBody(){need(this.bodyDone,'BODY_NOT_RECEIVED_OR_FRAME_EXTINCT');return {authority:'NONE',already_received_once:true};}
  async receive(){
    await this._until(()=>this.events.some(x=>x.event==='complete'),true);
    const event=this.events.find(x=>x.event==='complete');
    if(!this.terminal)await this._poll();
    need(this.terminal&&this.last===0,'TERMINAL_ROLE_READBACK_REQUIRED');return event.receipt;
  }
  async unknown(){
    if(this.session!==null&&!this.terminal){
      // Only the already-owned session is interrupted. Never re-launch or
      // issue a second provider call. Root retains unknown terminal custody.
      this._accept(await this.tools.write_stdin({session_id:this.session,chars:'\u0003',yield_time_ms:1000,max_output_tokens:5000}));
    }
    return {authority:'NONE',status:this.terminal?'TERMINAL_REFUSED':this.session!==null?'UNKNOWN_OWNED_SESSION':this.launchAttempted?'UNRESOLVED_LAUNCH_NO_SESSION_ID':'NO_OWNED_PROCESS_STARTED',session_id:this.session,automatic_retry:false};
  }
}
if(typeof module!=='undefined')module.exports={WindowsRoleIO,decodeConpty};
