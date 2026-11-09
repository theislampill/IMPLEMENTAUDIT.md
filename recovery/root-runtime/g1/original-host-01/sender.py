"""Root's event-specific composition of the installed sender stages; no automatic retries."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,types

BASE=Path('/home/agent/dg16-g1-current04-operators')
R=BASE/'public-receiver-02'
W=Path('/mnt/c/workspace/ai/improveimplementaudit/plans/astra-successor-reconciliation-20261108/g1-current04-issuer/original-host-01')
HELPER=BASE/'root-event-helpers-02/root_live_sender_call.py'
sha=lambda b:hashlib.sha256(b).hexdigest()
def pin(p):return sha(p.read_bytes())
def save(p,b):
    if isinstance(b,dict):b=(json.dumps(b,sort_keys=True,separators=(',',':'))+'\n').encode()
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as w:w.write(b);w.flush();os.fsync(w.fileno())
    assert p.read_bytes()==b
def execute(script,*args):
    proc=subprocess.run(['/usr/bin/python3','-I','-B',*map(str,[script,*args])],capture_output=True,timeout=50)
    if proc.returncode:raise RuntimeError('Root step refused: '+proc.stderr.decode(errors='replace')[-220:])
    return json.loads(proc.stdout) if proc.stdout.strip() else {}
def main(action,expected_helper_pin):
    executable=HELPER.with_name('root_live_sender_call_received.py') if action=='admit-binary' else HELPER
    b=executable.read_bytes();assert sha(b)==expected_helper_pin
    H=types.ModuleType('root_bound_sender_steps');H.__file__=str(executable);exec(compile(b,str(executable),'exec'),H.__dict__)
    P=H.pipeline()
    def stage(name,data):
        (path,source),args=H.stage_argv(name,data)
        return execute('-c',H.LOADER,path,source,*args)
    info=json.loads((W/'JOB.json').read_bytes());rid=str(info['run_id'])
    e=BASE/('actual-current04-'+rid);assert e.resolve(strict=True)==e
    session=R/'sessions'/('r'+rid+'-recipient')
    manifest=e/'assembled/ROOT_SENDER_INSTALL_MANIFEST.json'
    pub=e/'HOST_PUBLICATION_ROOT_RECEIVING.json'; late=e/'ROOT_ACTUAL_LATE_RECEIVING.json'
    install=e/'dispatcher-install';select=e/'dispatcher-selection.json';req=e/'dispatch-requirements';adm=e/'dispatcher-admission.json';prepared=e/'binary-prepared'
    ref='native Root 01a1953f-a15b-7811-aa72-3538ebb03562 for run '+rid+' '
    def helper(*args):return execute(executable,*args)
    if action=='assemble':
        stage('issue',dict(session=str(session),recipient_receipt_sha256=pin(session/'RECEIVING.json'),publication_receipt=str(pub),publication_receipt_sha256=pin(pub),episode=str(e)))
        stage('assemble',dict(episode=str(e)))
        got=helper('check-late','--episode',e,'--manifest-sha256',pin(manifest))
        print(json.dumps({'manifest':pin(manifest),'check':got,'sender_started':False}));return
    if action=='admit-dispatch':
        helper('receive-late','--episode',e,'--manifest-sha256',pin(manifest),'--root-decision-ref',ref+'accept actual assembled sender bytes','--output',late)
        stage('dispatcher-selection',dict(episode=str(e),late_receiving=str(late),late_receiving_sha256=pin(late),install=str(install),output=str(select)))
        stage('requirements',dict(selection=str(select),output=str(req)));requirements=req/'DISPATCHER_ADMISSION_REQUIREMENTS.json'
        helper('issue-admission','--episode',e,'--requirements',requirements,'--requirements-sha256',pin(requirements),'--root-decision-ref',ref+'admit 18 sequential original metadata observations','--output',adm,'--issuance-record',e/'ROOT_DISPATCH_ISSUED.json')
        stage('bind',dict(selection=str(select),admission=str(adm),install=str(install)))
    if action in ('admit-dispatch','check-ready-dispatch'):
        checks=helper('check-dispatcher','--install',install,'--install-manifest-sha256',pin(install/'INSTALL_MANIFEST.json'),'--selection',select,'--selection-sha256',pin(select))
        c=helper('sender-command','--episode',e,'--manifest-sha256',pin(manifest))
        js=(install/'dispatch.js').read_bytes();assert pin(install/'dispatch.js')==checks['dispatch']['sha256']
        print(json.dumps({'command':c['command'],'dispatch':js.decode(),'dispatch_sha256':sha(js),'expires_ms':checks['expires_unix_ms'],'sender_started':False}));return
    assert action in ('prepare-binary','admit-binary')
    term=e/'SENDER_TERMINAL.json';received=e/'ROOT_SENDER_TERMINAL_RECEIVING.json';parent=e/'cipher-parent.json';journal=R/'control-sessions'/('r'+rid+'-cipher')
    if action=='prepare-binary':
        actual=json.loads((W/'SENDER_RESULT.json').read_bytes());assert actual['exit']==0 and actual['terminal']['result']['status']=='PAYLOAD_READY' and actual['terminal']['result']['cleanup_complete'] is True
        assert actual['dispatch_finished'] is True and actual['actual_calls']==18
        assert actual['terminal']['schema']=='dg16.root-sender-terminal-export.v1'
        raw=(json.dumps(actual['terminal'],sort_keys=True,separators=(',',':'))+'\n').encode()
        assert actual['stdout_sha256'] in (sha(raw),sha(raw.replace(b'\n',b'\r\n')))
        save(term,raw)
        helper('receive-sender-terminal','--terminal',term,'--terminal-sha256',pin(term),'--native-session-id',str(actual['session_id']),'--actual-exit-code',str(actual['exit']),'--root-decision-ref',ref+'receive owned terminal after exact 18-call dispatcher readback','--output',received)
        save(parent,(W/'PARENT_cipher.json').read_bytes())
        op=json.loads((e/'assembled/packet/carrier/PRO_SENDER_OPERATION.json').read_bytes())
        assert time.time_ns()//1000000<op['expires_unix_ms']
        stage('publication-inputs',dict(episode=str(e),sender_terminal=str(term),sender_terminal_sha256=pin(term),sender_receiving=str(received),sender_receiving_sha256=pin(received),parent_ref_result=str(parent),parent_ref_sha256=pin(parent),journal_directory=str(journal),deadline_unix_ms=op['expires_unix_ms'],output=str(prepared)))
        check=helper('check-prepared','--prepared',prepared,'--prepared-manifest-sha256',pin(prepared/'PREPARED_MANIFEST.json'));print(json.dumps(check));return
    requirements=prepared/'ADMISSION_REQUIREMENTS.json';admission=e/'binary-actual-admission.json';config=e/'binary-configuration.json';mpin=pin(prepared/'PREPARED_MANIFEST.json')
    helper('issue-admission','--episode',e,'--requirements',requirements,'--requirements-sha256',pin(requirements),'--prepared',prepared,'--prepared-manifest-sha256',mpin,'--root-decision-ref',ref+'publish one exact checked two-leaf ciphertext control','--output',admission,'--issuance-record',e/'ROOT_BINARY_ISSUED.json')
    stage('publication-config',dict(prepared=str(prepared),prepared_manifest_sha256=mpin,admission=str(admission),admission_sha256=pin(admission),output=str(config)))
    print(json.dumps(helper('binary-selection','--prepared',prepared,'--prepared-manifest-sha256',mpin,'--configuration',config,'--configuration-sha256',pin(config))))

if __name__=='__main__':main(sys.argv[1],sys.argv[2])
