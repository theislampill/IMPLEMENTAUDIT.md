#!/usr/bin/env bash

set -uo pipefail

err_count=0
err() {
  printf 'validate-run-root: ERROR: %s\n' "$*" >&2
  err_count=$((err_count + 1))
}
warn() { printf 'validate-run-root: WARNING: %s\n' "$*" >&2; }
has_non_whitespace() { LC_ALL=C grep -q '[^[:space:]]' "$1" 2>/dev/null; }

# Portable composition of the existing record owners. This is not a host Stop
# adapter, an authority resolver, or an alternative lifecycle controller.
if [ "${1:-}" = "--turn-disposition" ]; then
  shift
  if command -v python >/dev/null 2>&1; then disposition_py=(python -B)
  elif command -v python3 >/dev/null 2>&1; then disposition_py=(python3 -B)
  elif command -v py >/dev/null 2>&1; then disposition_py=(py -3 -B)
  else printf 'validate-run-root: Python required for disposition records\n' >&2; exit 2; fi
  "${disposition_py[@]}" - "${BASH_SOURCE[0]}" "$@" <<'PYDISPOSITION'
import argparse,hashlib,json,os,re,signal,stat,subprocess,sys,tempfile
from pathlib import Path

def refuse(message):
    raise ValueError(message)
def safe_read(path):
    path=Path(os.path.abspath(path))
    for node in (path,*path.parents):
        info=node.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
            refuse('aliased read-set member: '+str(path))
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>1_000_000:
        refuse('nonregular or oversized read-set member: '+str(path))
    signature=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as handle:
        opened=os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode): refuse('nonregular opened read-set member')
        data=handle.read(1_000_001);closed=os.fstat(handle.fileno())
    if len(data)>1_000_000 or not signature(info)==signature(opened)==signature(closed)==signature(path.lstat()):
        refuse('read-set member changed during capture: '+str(path))
    return data,(signature(closed),hashlib.sha256(data).hexdigest())
def inventory(directory):
    if not stat.S_ISDIR(Path(directory).lstat().st_mode):refuse('non-directory read-set root')
    entries={};total=0
    for parent,dirs,files in os.walk(directory,followlinks=False):
        info=Path(parent).lstat()
        if not stat.S_ISDIR(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:refuse('changed inventory directory')
        entries[str(parent)]=('directory',info.st_dev,info.st_ino,info.st_mtime_ns,info.st_ctime_ns)
        for name in dirs+files:
            path=Path(parent)/name;info=path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                refuse('aliased inventory member: '+str(path))
            if name in dirs:
                if not stat.S_ISDIR(info.st_mode): refuse('changed inventory directory')
            else:
                total+=info.st_size
                if total>16_000_000:refuse('unsupported read-set byte budget')
                entries[str(path)]=safe_read(path)[1]
            if len(entries)>4096: refuse('unsupported read-set size')
    return entries

def run(command,allowed=(0,)):
    # This bounds a read-only helper, never the governor's audit/retry lifecycle.
    options={'start_new_session':True} if os.name=='posix' else {'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP}
    process=subprocess.Popen(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**options)
    try:
        stdout,stderr=process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        if os.name=='posix':
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        else:
            killer=str(Path(os.environ.get('SystemRoot','C:/Windows'))/'System32/taskkill.exe')
            try:subprocess.run([killer,'/PID',str(process.pid),'/T','/F'],capture_output=True,timeout=3)
            except (OSError,subprocess.TimeoutExpired):pass
            if process.poll() is None:process.kill()
        try:process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.stdout.close();process.stderr.close()
        refuse('packaged owner read timed out; no disposition')
    result=subprocess.CompletedProcess(command,process.returncode,stdout,stderr)
    if result.returncode not in allowed:
        refuse('packaged owner refused: '+Path(command[1]).name+'\n'+result.stdout+result.stderr)
    return result

def fields(text,section=None):
    if section:
        blocks=re.findall(r'(?ms)^## '+re.escape(section)+r'\s*\n(.*?)(?=^## |\Z)',text)
        if len(blocks)!=1: refuse('expected one '+section+' section')
        text=blocks[0]
    result={}
    for line in text.splitlines():
        cells=[x.strip(' \t`') for x in line.split('|')[1:-1]] if line.startswith('|') else []
        match=re.match(r'^(?:- )?([^:]+):\s*(.*)$',line)
        if len(cells)==2 and cells[0] not in {'Field','Input'} and not cells[0].startswith('---'):
            key,value=cells
        elif match and '|' not in line: key,value=match.groups();value=value.strip(' \t`')
        else: continue
        if key in result: refuse('duplicate record field: '+key)
        result[key]=value
    return result

def concrete(value):
    return bool(value and len(value.strip())>3 and value.lower() not in {'none','unknown','pending','todo','tbd','continue','wait'})
def needed(mapping,key):
    value=mapping.get(key,'')
    if not concrete(value): refuse('missing concrete '+key)
    return value

def table_rows(text, *, unique_headers=False):
    header=None
    for line in text.splitlines():
        if not line.startswith('|'): header=None;continue
        cells=[c.strip(' \t`') for c in line.split('|')[1:-1]]
        if cells and all(re.fullmatch(r':?-+:?',c) for c in cells):continue
        if header is None:
            if unique_headers and len(cells)!=len(set(cells)):refuse('duplicate record table header')
            header=cells;continue
        if len(cells)!=len(header):refuse('malformed record table')
        yield dict(zip(header,cells))

try:
    parser=argparse.ArgumentParser(prog='validate-run-root.sh --turn-disposition')
    parser.add_argument('disposition',choices=['TERMINAL_CLOSURE','AUDITED_HANDOFF','NONTERMINAL_YIELD'])
    parser.add_argument('run_root')
    for name in ('closure-record','handoff-packet','response-record'):parser.add_argument('--'+name)
    for name in ('superseded-plan','plan-cycle-record'):parser.add_argument('--'+name,action='append',default=[])
    helper=Path(os.path.abspath(sys.argv[1]));args=parser.parse_args(sys.argv[2:]);owner=helper.parent
    root=Path(os.path.abspath(args.run_root))
    for node in (root,*root.parents):
        info=node.lstat()
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:refuse('unsafe run-root directory ancestry')
    bound_members=None
    def contained(raw,optional=False):
        if any(p in {'.','..'} for p in re.split(r'[/\\]',str(raw))):refuse('lexical path alias')
        path=Path(raw);path=path if path.is_absolute() else root/path
        try:path.relative_to(root)
        except ValueError:refuse('unsupported external read dependency: '+str(path))
        if optional and not os.path.lexists(path):return path
        if bound_members is not None and path.relative_to(root).as_posix() not in bound_members:refuse('unsupported unmapped canonical record dependency: '+str(path))
        safe_read(path)
        return path
    closure=contained(args.closure_record) if args.closure_record else None
    packet=contained(args.handoff_packet) if args.handoff_packet else None
    response=contained(args.response_record) if args.response_record else None
    if args.disposition=='TERMINAL_CLOSURE' and (not closure or packet):refuse('closure requires only --closure-record')
    if args.disposition=='AUDITED_HANDOFF' and (not packet or closure):refuse('handoff requires only --handoff-packet')
    if args.disposition=='NONTERMINAL_YIELD' and (closure or packet or args.superseded_plan or args.plan_cycle_record):refuse('yield cannot consume closure/handoff inputs')
    if args.disposition!='TERMINAL_CLOSURE' and (args.superseded_plan or args.plan_cycle_record):refuse('plan inputs apply only to closure')
    plans=[contained(p) for p in args.superseded_plan];cycles=[contained(p) for p in args.plan_cycle_record]
    # The existing full validator compares siblings only for a claimed root.
    # Capture that optional family and the templates it actually consumes too.
    read_root=root.parent if (root/'.claimed').exists() else root
    def source_identity():
        return inventory(owner.parent) # Packaged directory identities, references, templates and executable source.
    before=inventory(read_root);source_before=source_identity()
    review_owner=None;review_owner_before=None
    with tempfile.TemporaryDirectory(prefix='disposition-pair-') as tmp:
        pair=Path(tmp)/'pair';pair.mkdir()
        reader=[sys.executable,'-B',str(owner/'read-canonical-pair.py'),'--run-root',str(root),'--output',str(pair),'--native-guards']
        selected=run(reader,allowed=(0,3))
        state_path=pair/'native-STATE.md' if selected.returncode==0 else root/'STATE.md'
        roadmap_path=pair/'native-ROADMAP.md' if selected.returncode==0 else root/'ROADMAP.md'
        state=safe_read(state_path)[0].decode('utf-8');roadmap=safe_read(roadmap_path)[0].decode('utf-8')
        current=fields(state,'Current phase')
        documents=[state]+[safe_read(p)[0].decode('utf-8') for p in (closure,packet,response) if p]
        markers=lambda text:re.findall(r'(?m)^\s*(AUDIT_START|AUDIT_VERIFY|AUDIT_GAPS|AUDIT_COMPLETE|IMPLEMENTAUDIT_RUN_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF)\s*$',text)
        claims=[m for text in documents for m in markers(text)]
        terminal=any(m in claims for m in ('AUDIT_COMPLETE','IMPLEMENTAUDIT_RUN_COMPLETE')) or current.get('Status')=='DONE' or current.get('Audit object state','').startswith('terminal')
        handoff=any(m in claims for m in ('AUDIT_HANDOFF','ANDON_HANDOFF'))
        if terminal and handoff:refuse('conflicting terminal and handoff claims')
        if args.disposition=='NONTERMINAL_YIELD' and (terminal or handoff):refuse('requested yield cannot downgrade actual claims')
        if args.disposition=='TERMINAL_CLOSURE' and (not terminal or handoff):refuse('closure claim mismatch')
        if args.disposition=='AUDITED_HANDOFF' and (not handoff or terminal):refuse('handoff claim mismatch')
        # Keep optional repo-only and active replay dependencies out of this
        # bounded source record cell; their native owners retain admission.
        record_root=pair/'native-records' if selected.returncode==0 else root
        if selected.returncode==0:
            bound_members={p.relative_to(record_root).as_posix() for p in record_root.rglob('*') if p.is_file()}
            for path in [p for p in (closure,packet,response) if p]+plans+cycles:contained(path)
            if closure and (root/'deferrals.jsonl').exists():contained('deferrals.jsonl')
            for path in root.glob('*'):
                if path.suffix.lower()=='.md' and ('steer' in path.name.lower() or 'advisory' in path.name.lower()):contained(path)
        direct_records=[safe_read(p)[0].decode('utf-8') for p in record_root.glob('*.md')]
        if any(re.search(r'(?m)^(successor-review:|lane-status: status: REVIEWER_RUNTIME_NON_VERDICT)',text) for text in direct_records):
            if args.disposition!='NONTERMINAL_YIELD':refuse('unsupported repository-only review dependency')
            review_owner=owner.parents[2]/'scripts/check-cold-review-contract.sh'
            try:review_owner_before=safe_read(review_owner)[1] if os.path.lexists(review_owner) else None
            except (OSError,ValueError) as exc:refuse('unsupported repository review owner: '+str(exc))
        for phase in (root/'phases').glob('phase-*.md'):
            # Check the supported dependency profile, leaving DONE applicability
            # and missing required captures with their existing semantic owner.
            contained(phase)
            phase_text=safe_read(phase)[0].decode('utf-8')
            for raw in re.findall(r';\s*capture:\s*([^;]+);',phase_text):
                raw=raw.strip().strip('`')
                contained(raw.replace('<run-root>/',str(root)+'/'),optional=True)
        if args.disposition!='NONTERMINAL_YIELD':
            repo=run(['git','rev-parse','--show-toplevel']).stdout.strip()
            git_identity=lambda:tuple(run(command).stdout for command in (['git','-C',repo,'rev-parse','HEAD'],['git','-C',repo,'rev-parse','--abbrev-ref','HEAD'],['git','-C',repo,'status','--porcelain']))
            repo_before=git_identity()
        structural=run(['bash',str(helper)]+(['--nonterminal-yield'] if args.disposition=='NONTERMINAL_YIELD' else [])+[str(root)],allowed=(0,3) if args.disposition=='NONTERMINAL_YIELD' else (0,))
        if structural.returncode==3:refuse('unsupported yield read-set profile: '+structural.stderr.strip())
        if closure:
            text=safe_read(closure)[0].decode('utf-8');data=fields(text)
            if closure.parent!=root:refuse('closure record must be a run-root sibling of deferrals.jsonl')
            if current.get('Status')!='DONE' or current.get('Audit object state')!='terminal verified closure':refuse('closure requires DONE and terminal verified closure')
            sequence=markers(text)
            if sequence[-2:]!=['AUDIT_COMPLETE','IMPLEMENTAUDIT_RUN_COMPLETE'] or sequence.count('AUDIT_COMPLETE')!=1 or sequence.count('IMPLEMENTAUDIT_RUN_COMPLETE')!=1:refuse('exclusive final terminal marker order is missing')
            if 'AUDIT_START' not in sequence or 'AUDIT_VERIFY' not in sequence or sequence.index('AUDIT_VERIFY')<sequence.index('AUDIT_START'):refuse('final audit start/verify record is absent')
            last_start=max(i for i,m in enumerate(sequence) if m=='AUDIT_START')
            if sequence[last_start:]!=['AUDIT_START','AUDIT_VERIFY','AUDIT_COMPLETE','IMPLEMENTAUDIT_RUN_COMPLETE']:refuse('last audit round retains gaps or lacks verification')
            for key in ('AUDIT_START_ANCHOR','AUDIT_VERIFY_ANCHOR','REANCHOR_DISPOSITION','REANCHOR_EVIDENCE','equivalent_config_attempts','stochasticity_budget','terminal_qualification'):
                if not data.get(key):refuse('required final audit identity missing: '+key)
            if data['terminal_qualification']!='QUALIFIED':refuse('final candidate is not QUALIFIED')
            coverage=re.findall(r'(?m)^re_verified / \(re_verified \+ trust_prior\) = ([0-9]+) / \(([0-9]+) \+ ([0-9]+)\) = ([01](?:\.[0-9]+)?|[0-9]+/[0-9]+)\s*$',text)
            if len(coverage)!=1:refuse('one concrete coverage calculation is required')
            numerator,fresh,prior=map(int,coverage[0][:3])
            from fractions import Fraction
            if numerator!=fresh or fresh+prior<=0 or abs(Fraction(coverage[0][3])-Fraction(fresh,fresh+prior))>Fraction(1,10000):refuse('coverage arithmetic does not match its nonzero population')
            claim_rows=[line for line in text.splitlines() if line.startswith('claim:')]
            if not claim_rows or any(not re.search(r'\|\s*status:\s*(verified|not-applicable)(?:\s*\||\s*$)',line) for line in claim_rows):refuse('unclosed required closure claim')
            # Hosted publication may perform live retrieval and dynamically select
            # dependencies; it needs its own authorized accepting executor.
            if re.search(r'(?m)^publication-identity:|^claim:.*\|\s*surface:\s*publication\b',text):refuse('unsupported dynamic publication dependency')
            for rel in re.findall(r'(?:evidence-file|record-file|readback-file):\s*([^|\n]+)',text):contained(rel.strip())
            inventory_sections=re.findall(r'(?ms)^(?:## Final closure checker inputs|Final closure checker inputs:)\s*\n(.*?)(?=^## |\Z)',state)
            if len(inventory_sections)!=1:refuse('expected one Final closure checker inputs inventory')
            inventory_fields=fields(inventory_sections[0])
            for key,provided in (('Superseded plans',plans),('Cycle-accounted plans',cycles)):
                raw=inventory_fields.get(key)
                if raw is None:refuse('missing Final closure checker inputs: '+key)
                declared=[] if raw=='none' else [contained(p.strip(' `')) for p in raw.split(',')]
                if sorted(map(str,provided))!=sorted(map(str,declared)) or len(set(provided))!=len(provided):refuse('applicable plan inventory differs from supplied inputs')
            if inventory_fields.get('Steer directory') not in {str(root),'<run-root>'}:refuse('closure steer inventory does not select this run root')
            phases=[row for row in table_rows(roadmap) if 'Status' in row and ('Phase' in row or '#' in row)]
            if not phases:refuse('no declared phase population')
            for row in phases:
                review=row.get('Review')
                if review is not None and review not in {'PASS','not applicable','not-applicable'} and not re.fullmatch(r'not[- ]applicable: .+',review):refuse('nonterminal declared phase review')
                number=row.get('#',row.get('Phase',''))
                if not re.fullmatch(r'[1-9][0-9]*',number):refuse('unsupported phase identity')
                phase=contained('phases/phase-'+number+'.md');phase_text=safe_read(phase)[0].decode('utf-8')
                if any(value.strip() not in {'','none'} for value in re.findall(r'(?m)^Scarce resource budget:(.*)$',safe_read(phase)[0].decode('utf-8'))):refuse('unsupported active rehearsal dependency')
                run(['bash',str(owner/'validate-phase.sh'),str(phase)])
                deferred=row['Status'].lower().startswith('deferred')
                if row['Status'].lower() not in {'done','verified','pass','complete','completed','closed'} and not deferred:refuse('nonterminal declared phase')
                tail=phase_text.split('IMPLEMENTAUDIT_PHASE_DONE')[-1]
                if not re.search(r'(?m)^Status:\s*(done|verified|pass|complete|completed|closed|deferred)\b',tail,re.I):refuse('phase lacks terminal DONE evidence')
                if deferred:
                    if not concrete(fields(phase_text).get('Owner decision')):refuse('deferred phase lacks owner decision')
                elif re.search(r'(?m)^\s*- \[ \]',phase_text):refuse('phase has unverified required criterion')
            for verdict in re.findall(r'(?m)^cold-review: disposition: ([^|]+)',state):
                if verdict.strip()!='PASS':refuse('nonterminal current cold-review disposition')
            for section,allowed in (('AGENTS_UPDATE_DECISION',{'updated','not warranted','OWNER DECISION'}),('CONTINUITY_DECISION',{'none','updated','deferred','OWNER DECISION'})):
                if re.search(r'(?m)^## '+section+r'\s*$',state) and fields(state,section).get('Status') not in allowed:refuse('nonterminal '+section)
            # An occurrence can retain earlier probe/escalation history. Only a
            # later row for that same occurrence, phase and abnormality class
            # supersedes its outcome; another remedy cannot close this one.
            andon_blocks=re.findall(r'(?mis)^## Andon log\s*\n(.*?)(?=^## |\Z)',state)
            if len(andon_blocks)!=1:refuse('expected one current Andon log')
            latest={};row_ids=set()
            for row in table_rows(andon_blocks[0], unique_headers=True):
                if not {'#','Phase','Class','Outcome'}<=row.keys():refuse('malformed Andon outcome record')
                number=row['#']
                if not re.fullmatch(r'[1-9][0-9]*',number) or number in row_ids:refuse('ambiguous Andon row identity')
                row_ids.add(number)
                outcome=row['Outcome']
                if outcome not in {'resolved','open (rerun pending)','blocked (handoff condition)'} and not re.fullmatch(r'escalated \(cites #[1-9][0-9]*(?:, #[1-9][0-9]*)*\)',outcome):refuse('unknown or missing Andon outcome')
                occurrence=row.get('Occ')
                if occurrence is not None and not occurrence:refuse('missing Andon occurrence identity')
                key=('occ',occurrence,row['Phase'],row['Class']) if occurrence is not None else ('legacy-row',number)
                latest[key]=outcome
            if any(outcome!='resolved' for outcome in latest.values()):refuse('unresolved current Andon outcome prevents terminal closure')
            for row in table_rows(state):
                if 'Finding' in row and 'Status' in row and row['Status'].lower() not in {'closed','done','verified','resolved','not-applicable','deferred'}:refuse('nonterminal in-scope ledger item')
                if row.get('Consequential','').lower()=='yes' and row.get('Disposition') in {'pending','unresolved',''}:refuse('unresolved consequential residual')
                if row.get('Disposition') in {'deferred','transferred','owner-assigned','risk-accepted'} and not concrete(row.get('Owner / policy ref')):refuse('residual lacks owner/policy disposition')
            deliverables=re.findall(r'(?ms)^## Deliverables\s*\n(.*?)(?=^## |\Z)',roadmap)
            for block in deliverables:
                for line in block.splitlines():
                    if not line.strip():continue
                    match=re.fullmatch(r'- `([^`]+)`',line)
                    if not match:refuse('unsupported deliverable declaration; requires one literal path per bullet')
                    if not safe_read(contained(match[1]))[0].strip():refuse('empty declared deliverable')
            if re.search(r'environment-quirk|destination:\s*(?:checker|deterministic test)',text,re.I):refuse('unsupported external lesson-lift dependency')
            run(['bash',str(owner/'check-lesson-lift.sh'),str(closure),'--repo-root',repo])
            command=['bash',str(owner/'check-closure-surface.sh'),str(closure),'--steer-dir',str(root)]
            for flag,paths in (('--superseded-plan',plans),('--plan-cycle-record',cycles)):
                for path in paths:command.extend([flag,str(path)])
            run(command)
        if packet:
            text=safe_read(packet)[0].decode('utf-8');data=fields(text)
            if current.get('Status')!='BLOCKED' or current.get('Audit object state')!='open':refuse('handoff requires BLOCKED/open state')
            for key in ('Blocker','Owner/source','Next action','Re-entry condition'):needed(current,key)
            evidence=contained(needed(current,'Handoff evidence'))
            if not safe_read(evidence)[0].strip():refuse('empty handoff evidence')
            if not re.fullmatch(r'[0-9a-f]{64}',data.get('packet_content_hash','')):refuse('handoff requires exact SHA-256 packet content hash')
            body=''.join(line for line in text.splitlines(keepends=True) if not re.match(r'^packet_content_hash:',line,re.I))
            if hashlib.sha256(body.encode('utf-8')).hexdigest()!=data['packet_content_hash']:refuse('handoff packet digest mismatch')
            packet_markers=markers(text)
            if len(packet_markers)!=1 or packet_markers[0] not in {'AUDIT_HANDOFF','ANDON_HANDOFF'}:refuse('one exclusive handoff marker is required')
            if current.get('Handoff basis')=='owner-request':
                if packet_markers[0]!='AUDIT_HANDOFF':refuse('owner-request handoff is AUDIT_HANDOFF')
            elif current.get('Handoff basis')=='andon':
                for key in ('Failing criterion','Probe and escalation history','Handoff trigger','Remaining blocker','Next owner action'):needed(data,key)
                if data.get('Handoff trigger') not in {'owner-decision','unsafe-scope','missing-authorization','external-dependency','irreproducibility','missing-tool-or-access','no-bounded-countermeasure'}:refuse('not an existing Andon handoff condition')
                if not re.fullmatch(r'[1-9][0-9]*',data.get('Phase','')) or data.get('Phase')!=current.get('Phase'):refuse('Andon handoff phase mismatch')
                if data['Remaining blocker']!=current['Blocker'] or data['Next owner action']!=current['Next action']:refuse('Andon handoff record differs from current blocker/action')
                phase=contained('phases/phase-'+data['Phase']+'.md')
                if any(value.strip() not in {'','none'} for value in re.findall(r'(?m)^Scarce resource budget:(.*)$',safe_read(phase)[0].decode('utf-8'))):refuse('unsupported active rehearsal dependency')
                run(['bash',str(owner/'validate-phase.sh'),str(phase)])
                if not re.search(r'IMPLEMENTAUDIT_PHASE_DONE[\s\S]*^Status:\s*blocked\b',safe_read(phase)[0].decode(),re.M):refuse('Andon handoff lacks blocked phase evidence')
                if not any(row.get('Phase')==data['Phase'] and row.get('Outcome')=='blocked (handoff condition)' and row.get('Rerun evidence')==current['Handoff evidence'] for row in table_rows(state)):refuse('Andon handoff lacks exact blocked log/evidence')
            else:refuse('handoff basis must be owner-request or andon')
            run(['bash',str(owner/'check-handoff-packet.sh'),str(packet),'--repo-root',repo])
        if selected.returncode==0:run(reader+['--verify-current'])
        if review_owner is not None:
            try:review_owner_after=safe_read(review_owner)[1] if os.path.lexists(review_owner) else None
            except (OSError,ValueError) as exc:refuse('unsupported repository review owner: '+str(exc))
            if review_owner_before!=review_owner_after:refuse('unsupported repository review owner changed during disposition validation')
        if before!=inventory(read_root):refuse('read-set changed during disposition validation')
        if source_before!=source_identity():refuse('packaged owner source changed during validation')
        if args.disposition!='NONTERMINAL_YIELD' and repo_before!=git_identity():refuse('repository identity changed during disposition validation')
    print(json.dumps({'record_disposition':args.disposition,'authority':'NONE','native_enforcement':False,'effect_authority':False,'scope':'constructed record validation; authentic lifecycle acceptance not established'},sort_keys=True))
except (OSError,UnicodeError,ValueError,ZeroDivisionError) as exc:
    outside=str(exc).startswith('unsupported ')
    kind='OUT_OF_PROFILE' if outside else 'RECORD_REFUSED'
    print('validate-run-root: '+kind+': '+str(exc)+'; no disposition',file=sys.stderr)
    raise SystemExit(3 if outside else 1)
PYDISPOSITION
  exit $?
fi

if [ "${1:-}" = "--claim-only" ]; then
  run_arg="${2:-}"; [ "${3:-}" = "--repo-root" ] && repo_arg="${4:-}" || repo_arg=""
  [ -n "$run_arg" ] && [ -n "$repo_arg" ] && [ "$#" -eq 4 ] || { printf 'usage: validate-run-root.sh --claim-only <run-root> --repo-root <repo-root>\n' >&2; exit 2; }
  if command -v python >/dev/null 2>&1; then claim_py=(python)
  elif command -v python3 >/dev/null 2>&1; then claim_py=(python3)
  elif command -v py >/dev/null 2>&1; then claim_py=(py -3)
  else printf 'validate-run-root: Python is required for strict claim validation\n' >&2; exit 2; fi
  "${claim_py[@]}" - "$run_arg" "$repo_arg" <<'PY'
import datetime,os,re,stat,subprocess,sys
from pathlib import Path
run_arg,repo_arg=sys.argv[1:]
def die(s): print('validate-run-root: '+s,file=sys.stderr); raise SystemExit(1)
def canon(p): return os.path.normcase(os.path.abspath(p))
def unsafe(p):
 try: st=os.lstat(p)
 except OSError: die(f'custody path missing: {p}')
 return stat.S_ISLNK(st.st_mode) or bool(getattr(st,'st_file_attributes',0)&0x400)
def lexical_path(raw,base,label):
 if '\x00' in raw: die(f'{label} contains NUL')
 parts=re.split(r'[/\\]+',raw)
 if any(part in ('.','..') for part in parts): die(f'{label} contains a lexical dot alias')
 p=Path(raw)
 if not p.is_absolute():
  if base is None: die(f'{label} must be absolute')
  p=base/p
 chain=Path(p.anchor)
 for part in p.parts[1:]:
  chain=chain/part
  if unsafe(chain): die(f'{label} custody path is symlink/reparse: {chain}')
 return p
repo=lexical_path(repo_arg,None,'repo root')
run=lexical_path(run_arg,repo,'run root')
if not repo.is_dir(): die('repo root is not a regular custody directory')
try:
 top=subprocess.check_output(['git','-C',str(repo),'rev-parse','--show-toplevel'],text=True).strip()
 common=subprocess.check_output(['git','-C',str(repo),'rev-parse','--git-common-dir'],text=True).strip()
except subprocess.CalledProcessError: die('repo root is not a Git worktree')
if canon(top)!=canon(repo): die('supplied repo root is not the canonical Git worktree')
common=common if os.path.isabs(common) else os.path.join(str(repo),common)
try: rel=run.relative_to(repo)
except ValueError: die('run root is outside repository')
for p in [repo,*[repo/Path(*rel.parts[:i]) for i in range(1,len(rel.parts)+1)]]:
 if unsafe(p): die(f'custody path is symlink/reparse: {p}')
if not run.is_dir(): die('run root is not a directory')
claim=run/'.claimed'
if unsafe(claim) or not stat.S_ISREG(os.lstat(claim).st_mode): die('.claimed is not a regular custody file')
rows=claim.read_text(encoding='utf-8').splitlines()
if any(not x or '=' not in x for x in rows): die('.claimed has blank or malformed key')
pairs=[x.split('=',1) for x in rows]; keys=[x[0] for x in pairs]
want=['schema','claim_id','claimed_at_utc','mode','templates','repo_root','git_common_dir','run_base','run_root','run_name']
if keys!=want: die('.claimed v2 keys/order do not match strict schema')
d=dict(pairs)
if d['schema']!='implementaudit.run-claim.v2' or not re.fullmatch(r'[0-9a-f]{32}',d['claim_id']): die('.claimed v2 schema or claim_id invalid')
try:
 if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z',d['claimed_at_utc']): raise ValueError
 datetime.datetime.strptime(d['claimed_at_utc'],'%Y-%m-%dT%H:%M:%SZ')
except ValueError: die('.claimed claimed_at_utc is not RFC3339 UTC whole seconds')
if d['mode']!='full' or d['run_base']!='.IMPLEMENTAUDIT/runs': die('.claimed mode/base is not R0024 strict custody')
if canon(d['repo_root'])!=canon(repo) or canon(d['git_common_dir'])!=canon(common): die('.claimed repository or common-dir custody drift')
if d['run_root']!=rel.as_posix() or d['run_name']!=run.name or len(rel.parts)!=3 or rel.parts[:2]!=('.IMPLEMENTAUDIT','runs'): die('.claimed run identity drift')
if not re.fullmatch(r'[a-z0-9][a-z0-9-]*-[A-Za-z0-9]{6}',d['run_name']): die('.claimed run name is not claim-run shaped')
templates='STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md'
if d['templates']!=templates: die('.claimed template promise drift')
for name in templates.split():
 p=run/name
 if unsafe(p) or not stat.S_ISREG(os.lstat(p).st_mode): die(f'claimed template is not regular custody: {name}')
print('validate-run-root: claim ok')
PY
  exit $?
fi

graph_python=()
case "${1:-}" in
  --graph-freshness|--graph-scope|--graph-parent)
    if command -v python >/dev/null 2>&1; then
      graph_python=(python)
    elif command -v python3 >/dev/null 2>&1; then
      graph_python=(python3)
    elif command -v py >/dev/null 2>&1; then
      graph_python=(py -3)
    else
      printf 'validate-run-root: python, python3, or py -3 is required for graph checks\n' >&2
      exit 2
    fi
    ;;
esac

if [ "${1:-}" = "--graph-scope" ] || [ "${1:-}" = "--graph-parent" ]; then
  graph_mode="$1"
  if { [ "$graph_mode" = "--graph-scope" ] && [ "$#" -lt 4 ]; } || \
     { [ "$graph_mode" = "--graph-parent" ] && [ "$#" -ne 5 ]; }; then
    printf 'usage: validate-run-root.sh %s <catalog.json> <repo-root> %s\n' \
      "$graph_mode" "$([ "$graph_mode" = "--graph-scope" ] && printf '<path> [path...]' || printf '<scope> <miss|ambiguity|cross-scope|relation-omission>')" >&2
    exit 2
  fi
  shift
  "${graph_python[@]}" - "$graph_mode" "$@" <<'PY'
import fnmatch, hashlib, json, os, re, subprocess, sys
from pathlib import Path, PurePosixPath

mode, catalog_arg, repo_arg, *args = sys.argv[1:]
repo = Path(repo_arg).resolve()

def stop(message, status=1):
    print(f"validate-run-root: {message}", file=sys.stderr)
    raise SystemExit(status)

def sha(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        stop(f"cannot hash {path}: {exc}", 2)

def covers(row, path):
    root = row["root"]
    return ((root == "." or path.startswith(root + "/")) and
            any(fnmatch.fnmatchcase(path, p) for p in row["include"]) and
            not any(fnmatch.fnmatchcase(path, p) for p in row["exclude"]))

def inside(path, root):
    return path == root or root in path.parents

def sidecar(value, kind, base=None):
    path = Path(value)
    path = path if path.is_absolute() or base is None else base / path
    path, resolved = Path(os.path.abspath(path)), path.resolve()
    if path.is_symlink() or inside(path, repo) or inside(resolved, repo):
        stop(f"invalid graph catalogue: {kind} path is inside repo or is a symlink: {path}")
    return resolved

def unsafe(path):
    return path.is_symlink() or not inside(path.resolve(), repo)

def git_paths(*args):
    return set(subprocess.check_output(["git", "-C", str(repo), "ls-files", *args]).decode("utf-8").split("\0"))

def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON member")
    return value

def exact(value, names):
    return isinstance(value, dict) and set(value) == set(names.split())

config_names = (".graphifyignore", ".gitignore", ".graphifyinclude")

def scope_root(value):
    if (not isinstance(value, str) or "\\" in value or str(PurePosixPath(value)) != value or
            value != "." and (value.startswith("/") or ".." in PurePosixPath(value).parts)):
        raise ValueError("scope root")
    path = repo if value == "." else repo / value
    if (not path.is_dir() or not inside(path.resolve(), repo) or
            any(part.is_symlink() for part in (path, *path.parents) if inside(part, repo))):
        raise ValueError("scope root")
    return path

def config_keys(root):
    rel = root.relative_to(repo)
    dirs = [repo.joinpath(*rel.parts[:i]) for i in range(len(rel.parts) + 1)]
    return sorted((d / name).relative_to(repo).as_posix() for d in dirs for name in config_names)

catalog_path = sidecar(catalog_arg, "catalogue")

try:
    payload = json.loads(catalog_path.read_text(encoding="utf-8"), object_pairs_hook=unique)
except (OSError, UnicodeError, ValueError) as exc:
    stop(f"invalid graph catalogue: {exc}")

hex40, hex64 = re.compile(r"^[0-9a-fA-F]{40}$"), re.compile(r"^[0-9a-fA-F]{64}$")
try:
    if not exact(payload, "schema scopes"):
        raise ValueError("catalogue members")
    rows = payload["scopes"]
    if type(payload.get("schema")) is not int or payload["schema"] != 1 or not isinstance(rows, list) or not rows:
        raise ValueError("schema/scopes")
    scopes = {}
    for row in rows:
        if not exact(row, "name parent root include exclude file_count files config graph graph_sha256 build"):
            raise ValueError("scope members")
        name = row["name"]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", name) or name in scopes:
            raise ValueError("scope name")
        include, exclude, files = row["include"], row["exclude"], row["files"]
        build, config, root = row["build"], row["config"], scope_root(row["root"])
        if not exact(build, "commit tool version mode llm rules_sha256 scope_sha256"):
            raise ValueError(f"scope {name} build members")
        if (not isinstance(include, list) or not include or
                not isinstance(exclude, list) or
                not all(isinstance(p, str) for p in include + exclude)):
            raise ValueError(f"scope {name}")
        rules_sha = hashlib.sha256(json.dumps([sorted(include), sorted(exclude)], separators=(",", ":")).encode()).hexdigest()
        patterns = include + exclude
        if (include != sorted(set(include)) or exclude != sorted(set(exclude)) or
                not all(p and not p.startswith("/") and ".." not in PurePosixPath(p).parts for p in patterns) or
                not isinstance(files, dict) or row["file_count"] != len(files) or
                type(row["file_count"]) is not int or row["file_count"] < 0 or
                not all(isinstance(p, str) and hex64.fullmatch(v or "") for p, v in files.items()) or
                list(files) != sorted(files) or
                not all(covers(row, p) for p in files) or
                not isinstance(config, dict) or list(config) != config_keys(root) or
                not all(v is None or (isinstance(v, str) and hex64.fullmatch(v)) for v in config.values()) or
                not isinstance(row["graph"], str) or not hex64.fullmatch(row["graph_sha256"] or "") or
                row.get("parent") is not None and not isinstance(row.get("parent"), str) or
                not hex40.fullmatch(build.get("commit", "")) or
                not all(isinstance(build.get(k), str) and build[k] for k in ("tool", "version", "mode")) or
                build.get("rules_sha256") != rules_sha or
                build.get("llm") is not False):
            raise ValueError(f"scope {name}")
        contract_build = dict(build)
        del contract_build["scope_sha256"]
        contract = {
            "name": name,
            "parent": row.get("parent"),
            "root": row["root"],
            "include": include,
            "exclude": exclude,
            "file_count": row["file_count"],
            "files": files,
            "config": config,
            "build": contract_build,
        }
        scope_sha = hashlib.sha256(json.dumps(
            contract, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if build.get("scope_sha256") != scope_sha:
            raise ValueError(f"scope {name}")
        scopes[name] = row
    for name, row in scopes.items():
        parent = row.get("parent")
        if parent is not None:
            parent_row = scopes.get(parent)
            if (parent_row is None or not inside(scope_root(row["root"]), scope_root(parent_row["root"])) or
                    not set(row["files"]) < set(parent_row["files"]) or
                    not all(covers(parent_row, path) for path in row["files"])):
                raise ValueError(f"parent {name}")
        seen = {name}
        while parent is not None:
            if parent in seen:
                raise ValueError(f"parent cycle {name}")
            seen.add(parent)
            parent = scopes[parent].get("parent")
    for commit in {row["build"]["commit"] for row in rows}:
        if subprocess.call(["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, "HEAD"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
            raise ValueError(f"build commit {commit}")
except (AttributeError, KeyError, TypeError, ValueError) as exc:
    stop(f"invalid graph catalogue: {exc}")

def normalise(value):
    value = str(value).replace("\\", "/").removeprefix("./")
    if (not value or Path(value).is_absolute() or re.match(r"^[A-Za-z]:/", value) or
            ".." in PurePosixPath(value).parts or value == ".git" or value.startswith(".git/")):
        stop(f"invalid query path: {value}", 2)
    return value

relation_omission = False
if mode == "--graph-scope":
    paths = [normalise(p) for p in args]
    candidates = [r for r in rows if all(covers(r, p) for p in paths)]
    if not candidates:
        stop("graph-route: wrong/overbroad-scope fallback=deterministic-live-file-census broaden=false llm=false")
    selected = min(candidates, key=lambda r: (r["file_count"], r["name"]))
    reason = "smallest-cover"
else:
    current, reason = args
    if current not in scopes:
        stop(f"unknown graph scope: {current}")
    if reason == "relation-omission":
        relation_omission, selected = True, scopes[current]
    elif reason not in {"miss", "ambiguity", "cross-scope"}:
        stop(f"invalid broadening reason: {reason}", 2)
    else:
        if scopes[current].get("parent") is None:
            stop(f"scope has no declared parent: {current}")
        selected = scopes[scopes[current]["parent"]]
        reason = f"parent:{reason}"

check_rows = ([selected] if relation_omission else [scopes[current], selected]) if mode == "--graph-parent" else [selected]
for selected in check_rows:
    graph = sidecar(selected["graph"], "graph", catalog_path.parent)
    if not graph.is_file():
        stop(f"stale-sidecar: missing graph {selected['name']}")
    try:
        graph_bytes = graph.read_bytes()
    except OSError as exc:
        stop(f"cannot read graph {graph}: {exc}", 2)
    if hashlib.sha256(graph_bytes).hexdigest().lower() != selected["graph_sha256"].lower():
        stop(f"stale-sidecar: graph-digest {selected['name']}")
    try:
        graph_payload = json.loads(graph_bytes, object_pairs_hook=unique)
    except (UnicodeError, ValueError):
        stop(f"stale-sidecar: invalid graph {selected['name']}")
    if (not isinstance(graph_payload, dict) or
            not isinstance(graph_payload.get("nodes"), list) or
            not isinstance(graph_payload.get("links", graph_payload.get("edges")), list) or
            not isinstance(graph_payload.get("graph"), dict)):
        stop(f"stale-sidecar: invalid graph {selected['name']}")
    if graph_payload["graph"].get("implementaudit_scope_sha256") != selected["build"]["scope_sha256"]:
        stop(f"stale-sidecar: graph-scope-binding {selected['name']}")
    sources = []
    for node in graph_payload["nodes"]:
        source = node.get("source_file") if isinstance(node, dict) else None
        if (not isinstance(source, str) or "\\" in source or
                str(PurePosixPath(source)) != source or source.startswith("/") or
                ".." in PurePosixPath(source).parts):
            stop(f"stale-sidecar: graph-population {selected['name']}")
        sources.append(source if selected["root"] == "." else f"{selected['root']}/{source}")
    if set(sources) != set(selected["files"]):
        stop(f"stale-sidecar: graph-population {selected['name']}")

    for rel, expected_digest in selected["config"].items():
        path = repo / rel
        if unsafe(path):
            stop(f"stale-sidecar: unsafe-path {rel}")
        if path.exists() and not path.is_file():
            stop(f"stale-sidecar: config-drift {rel}")
        actual = sha(path) if path.is_file() else None
        if actual != expected_digest:
            stop(f"stale-sidecar: config-drift {rel}")

    root = scope_root(selected["root"])
    for rel in config_keys(root):
        path = repo / rel
        active = path.is_file() and any(line.strip() and not line.lstrip().startswith("#") for line in path.read_text(encoding="utf-8", errors="ignore").splitlines())
        if active and (path.name == ".graphifyinclude" or path.parent != repo):
            stop(f"stale-sidecar: unsupported-config {rel}")
    ignore = ".graphifyignore" if selected["config"][".graphifyignore"] else ".gitignore"
    if selected["config"][ignore] and any("**" in rule and not rule.lstrip().startswith(("#", "!")) for rule in (repo / ignore).read_text(encoding="utf-8", errors="ignore").splitlines()):
        stop(f"stale-sidecar: unsupported-ignore-pattern {ignore}")

    try:
        exclude = [f"--exclude-from={repo / ignore}"] if selected["config"][ignore] else []
        output = git_paths("--cached", "--others", "-z", *exclude)
        if exclude:
            output -= git_paths("--cached", "-i", "-z", *exclude)
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        stop(f"cannot census graph scope: {exc}", 2)
    covered = [p for p in output if p and covers(selected, p)]
    for rel in covered:
        path = repo / rel
        if unsafe(path):
            stop(f"stale-sidecar: unsafe-path {rel}")
    current = sorted(p for p in covered if (repo / p).is_file())
    expected = selected["files"]
    new = sorted(set(current) - set(expected))
    deleted = sorted(set(expected) - set(current))
    if new:
        stop(f"stale-sidecar: new {new[0]}")
    if deleted:
        stop(f"stale-sidecar: deleted {deleted[0]}")
    if mode == "--graph-scope" and any(p not in expected for p in paths):
        stop("graph-route: wrong/overbroad-scope query-path-not-indexed fallback=deterministic-live-file-census broaden=false llm=false")
    for rel in current:
        if sha(repo / rel).lower() != expected[rel].lower():
            stop(f"stale-sidecar: changed {rel}")

if relation_omission:
    print("graph-route: extractor/relation-model omission fallback=deterministic-live-file-census broaden=false llm=false")
    raise SystemExit(0)
build = selected["build"]
print(
    f"graph-scope: {selected['name']} graph={graph} files={selected['file_count']} "
    f"reason={reason} build={build['commit']} tool={build['tool']}@{build['version']} "
    f"mode={build['mode']} llm=false"
)
PY
  exit $?
fi

if [ "${1:-}" = "--graph-freshness" ]; then
  if [ "$#" -ne 3 ]; then
    printf 'usage: validate-run-root.sh --graph-freshness <graph.json> <repo-root>\n' >&2
    exit 2
  fi

  graph_path="$2"
  repo_path="$3"
  [ -f "$graph_path" ] || {
    printf 'validate-run-root: graph freshness input is not a file: %s\n' "$graph_path" >&2
    exit 2
  }

  built_at_commit="$("${graph_python[@]}" - "$graph_path" <<'PY'
import json
import sys

path = sys.argv[1]
try:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    sys.stderr.write(f"validate-run-root: invalid graph freshness input: {exc}\n")
    raise SystemExit(1)

value = payload.get("built_at_commit")
if not isinstance(value, str) or not value:
    sys.stderr.write("validate-run-root: graph.json has no string built_at_commit\n")
    raise SystemExit(1)
sys.stdout.write(value + "\n")
PY
)"
  parse_status=$?
  [ "$parse_status" -eq 0 ] || exit 1

  if ! printf '%s\n' "$built_at_commit" | grep -Eq '^[0-9a-fA-F]{40}$'; then
    printf 'validate-run-root: graph.json built_at_commit must be one full 40-hex commit SHA\n' >&2
    exit 1
  fi

  live_head="$(git -C "$repo_path" rev-parse HEAD 2>/dev/null)" || {
    printf 'validate-run-root: cannot resolve git rev-parse HEAD for %s\n' "$repo_path" >&2
    exit 2
  }

  if [ "$(printf '%s' "$built_at_commit" | tr '[:upper:]' '[:lower:]')" != \
       "$(printf '%s' "$live_head" | tr '[:upper:]' '[:lower:]')" ]; then
    printf 'validate-run-root: stale-sidecar: built_at_commit %s != git rev-parse HEAD %s\n' \
      "$built_at_commit" "$live_head" >&2
    exit 1
  fi
  exit 0
fi

check_recurrence_decision() {
  local ledger="$1" findings invalid_lines missing_classes
  findings="$(awk -F'|' '
    function trim(v) { gsub(/^[ \t]+|[ \t]+$/, "", v); return v }
    function owner_source(v) {
      if (v !~ /owner\/source[ \t]*=/) return ""
      sub(/^.*owner\/source[ \t]*=[ \t]*/, "", v)
      sub(/[ \t;,)]+.*$/, "", v)
      gsub(/\\/, "/", v)
      while (v ~ /^\.\//) sub(/^\.\//, "", v)
      return v
    }
    /^Mechanism-replacement decision:/ {
      if ($0 ~ /^Mechanism-replacement decision:[ \t]*(replace-mechanism|continue|escalate-to-convergence-mode)[ \t]*\([^()]*[[:alnum:]][^()]*\)[ \t]*$/) {
        valid_decision[NR]=1
      } else {
        print "invalid\t" NR
      }
    }
    /^[ \t]*AUDIT_COMPLETE[ \t]*$/ {
      if (audit_complete_line == 0) audit_complete_line=NR
    }
    /^## Andon log/ { in_andon=1; new_format=0; next }
    in_andon && /^## / { in_andon=0; new_format=0 }
    in_andon && tolower($0) ~ /\|[ \t]*occ[ \t]*\|[ \t]*phase[ \t]*\|[ \t]*class[ \t]*\|/ {
      new_format=1; next
    }
    in_andon && new_format && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
      occ=trim($3); cls=trim($5)
      if (occ == "" || cls == "") next
      key=cls SUBSEP occ
      if (!(key in seen)) {
        seen[key]=1
        count[cls]++
        previous_owner[cls]=last_owner[cls]
        last_owner[cls]=owner_source($7)
        last_line[cls]=NR
      }
    }
    END {
      for (cls in count) {
        if (count[cls] < 3 || last_owner[cls] == "" || previous_owner[cls] != last_owner[cls]) continue
        found=0
        for (line in valid_decision) {
          if ((line + 0) > last_line[cls] &&
              (audit_complete_line == 0 || (line + 0) < audit_complete_line)) found=1
        }
        if (!found) print "missing\t" cls
      }
    }' "$ledger")"

  invalid_lines="$(printf '%s\n' "$findings" | awk -F'\t' '$1 == "invalid" { print $2 }' | tr '\n' ' ')"
  if [ -n "$invalid_lines" ]; then
    err "invalid Mechanism-replacement decision: line(s) $invalid_lines (allowed: replace-mechanism (<what>) / continue (<justification>) / escalate-to-convergence-mode (<shared invariant>))"
  fi
  missing_classes="$(printf '%s\n' "$findings" | awk -F'\t' '$1 == "missing" { print $2 }' | tr '\n' ' ')"
  if [ -n "$missing_classes" ]; then
    err "Andon class(es) $missing_classes reached 3 distinct linked occurrences with the last 2 repairs on one owner/source; add a following Mechanism-replacement decision:"
  fi
}

intent_value() { sed -n "s/^$2:[[:space:]]*//p" "$1" | head -n1; }
duration_seconds() {
  [[ "$1" =~ ^([0-9]+)([smhd]?)$ ]] || return
  case "${BASH_REMATCH[2]}" in '') m=1;; s) m=1;; m) m=60;; h) m=3600;; d) m=86400;; esac
  printf '%s\n' "$((BASH_REMATCH[1] * m))"
}
process_identity_matches() {
  local py
  if command -v python >/dev/null 2>&1; then py=(python)
  elif command -v python3 >/dev/null 2>&1; then py=(python3)
  elif command -v py >/dev/null 2>&1; then py=(py -3)
  else return 2; fi
  "${py[@]}" - "$@" <<'PY'
import json,sys
p,l,i,b,c=sys.argv[1:]
try:
 x=json.load(open(p,encoding="utf-8"))
except (OSError,UnicodeError,json.JSONDecodeError): raise SystemExit(1)
if isinstance(x,dict): x=[x]
keys={"lane_id","host_os","host_boot_id","pid","process_creation_time"}
ok=any(isinstance(r,dict) and keys<=r.keys() and r["lane_id"]==l and isinstance(r["host_os"],str) and r["host_os"] and str(r["pid"])==i and r["host_boot_id"]==b and r["process_creation_time"]==c for r in x)
raise SystemExit(not ok)
PY
}
intent_has_open_window() {
  awk '
    /^[^[:space:]]/ { in_window = ($0 ~ /^verification_window:/); next }
    in_window && /^[[:space:]]*state:[[:space:]]*open[[:space:]]*$/ { found = 1 }
    END { exit !found }
  ' "$1"
}
intent_has_closed_window() {
  grep -Eq '^[[:space:]]*state:[[:space:]]*closed[[:space:]]*$' "$1"
}
intent_has_invalid_closed_anchor() {
  awk '
    /^[^[:space:]]/ { in_window = ($0 ~ /^verification_window:/); next }
    in_window && /^[[:space:]]*-[[:space:]]*surfaces:/ { closed_at = ""; next }
    in_window && /^[[:space:]]*closed_at:/ {
      closed_at = $0
      sub(/^[[:space:]]*closed_at:[[:space:]]*/, "", closed_at)
      next
    }
    in_window && /^[[:space:]]*state:[[:space:]]*closed[[:space:]]*$/ {
      if (length(closed_at) != 40 || closed_at !~ /^[0-9a-f]+$/) bad = 1
    }
    END { exit !bad }
  ' "$1"
}
check_background_chains() {
  local root="$1" state="$2" chain source_chain id intent status budget signal expected timeout mode cadence why es ts polls line pid boot created rc
  [ -d "$root/background" ] || return
  local content_only=()
  # Temporary copy pathnames must not masquerade as an owned process selector.
  [ "$nonterminal_yield" != yes ] || content_only=(-h)
  for chain in "$root"/background/*; do
    [ -d "$chain" ] || continue; id="$(basename "$chain")"
    source_chain="$chain"
    if [ "$nonterminal_yield" = yes ]; then
      # Read the original owner's grammar from safe copies. Rechecks below bind
      # the original paths; a later FIFO swap cannot block the shell consumers.
      # Display IDs can collide (for example after trailing-newline removal).
      # Each original chain needs private completion/status/recursive copies.
      chain="$(mktemp -d "$validation_snapshots/background.XXXXXXXX")" \
        || { err "yield read-set background snapshot allocation failed"; continue; }
      yield_track_dependency --capture "$source_chain/launch-intent.md" "$chain/launch-intent.md" \
        || { err "yield read-set background intent capture failed"; continue; }
    fi
    intent="$chain/launch-intent.md"; status="$chain/chain-status.txt"
    [ -f "$intent" ] || { err "background/$id missing launch-intent.md"; continue; }
    if intent_has_closed_window "$intent"; then
      if [ "$nonterminal_yield" = yes ]; then
        yield_track_dependency --background-presence "$source_chain/chain.done" "$chain/chain.done" \
          || { err "yield read-set background completion capture failed"; continue; }
      fi
      [ -f "$chain/chain.done" ] \
        || err "background/$id closed verification window lacks chain.done"
      if intent_has_invalid_closed_anchor "$intent"; then
        err "background/$id closed verification window lacks a full-SHA closed_at"
      fi
    fi
    if [ -f "$state" ] &&
       grep -Eq '^\|[[:space:]]*Status[[:space:]]*\|[[:space:]]*DONE[[:space:]]*\|' "$state" &&
       intent_has_open_window "$intent"; then
      err "background/$id verification window remains open at run-root closure"
    fi
    if ! grep -Eq '^(poll_budget|terminal_signal|expected_duration|transport_timeout|launch_mode|report_cadence):' "$intent"; then
      warn "background/$id legacy launch intent; #81 checks skipped"; continue
    fi
    budget="$(intent_value "$intent" poll_budget)"; signal="$(intent_value "$intent" terminal_signal)"
    expected="$(intent_value "$intent" expected_duration)"; timeout="$(intent_value "$intent" transport_timeout)"
    mode="$(intent_value "$intent" launch_mode)"; cadence="$(intent_value "$intent" report_cadence)"
    why="$(intent_value "$intent" report_cadence_justification)"; [ -n "$cadence" ] || cadence=on-failure-and-terminal
    [[ "$budget" =~ ^[1-9][0-9]*$ ]] || err "background/$id invalid poll_budget"
    [[ "$signal" =~ ^[^[:space:]]+$ ]] || err "background/$id invalid terminal_signal"
    case "$mode" in inline|detached);; *) err "background/$id invalid launch_mode";; esac
    case "$cadence" in per-item|on-failure-and-terminal|terminal-only);; *) err "background/$id invalid report_cadence";; esac
    [ "$cadence" != per-item ] || [[ "$why" =~ [[:alnum:]] ]] || err "background/$id per-item cadence lacks justification"
    es="$(duration_seconds "$expected" 2>/dev/null || :)"; ts="$(duration_seconds "$timeout" 2>/dev/null || :)"
    [ -n "$es" ] || err "background/$id invalid expected_duration"; [ -n "$ts" ] || err "background/$id invalid transport_timeout"
    if [ -n "$es" ] && [ -n "$ts" ] && [ "$mode" = inline ] && [ "$es" -ge "$ts" ]; then err "background/$id inline launch meets/exceeds ceiling"; fi
    if [ "$nonterminal_yield" = yes ]; then
      yield_track_dependency --background-status "$source_chain/chain-status.txt" "$status" \
        || { err "yield read-set background status capture failed"; continue; }
    fi
    [ -f "$status" ] || continue
    if [ "$nonterminal_yield" = yes ]; then
      yield_track_dependency --background-scan "$source_chain" "$chain" \
        || { err "yield read-set background scan capture failed"; continue; }
    fi
    polls="$(grep -c '^probe:' "$status" 2>/dev/null || :)"
    if [[ "$budget" =~ ^[1-9][0-9]*$ ]] && [ "$polls" -gt "$budget" ] &&
       { [ ! -f "$state" ] || ! awk -v n="$budget" 'index(tolower($0),"hung-command")&&index(tolower($0),"supervision-overrun")&&index(tolower($0),"poll_budget " n " exceeded"){f=1} END{exit !f}' "$state"; }; then
      err "background/$id poll_budget exceeded without matching hung-command Andon"
    fi
    if [ "$cadence" = on-failure-and-terminal ] && grep -E '^report: item=.*outcome=' "$status" | grep -Evq 'outcome=failure([ |]|$)'; then err "background/$id default cadence narrated success"
    elif [ "$cadence" = terminal-only ] && grep -q '^report: item=' "$status"; then err "background/$id terminal-only narrated item"; fi
    awk '/^checkpoint:/{c=NR}/^wait: blocking/{if(!c||c>=NR)b=1}END{exit b}' "$status" || err "background/$id wait lacks checkpoint"
    grep -R -E -q "Name[[:space:]]*=[[:space:]]*['\"][^'\"]*\\.exe|pkill[[:space:]]+-f|taskkill([.]exe)?[[:space:]].*/IM|Get-CimInstance[[:space:]]+Win32_Process" "$chain" 2>/dev/null && err "background/$id broad kill authority"
    if grep -R "${content_only[@]}" -E 'Get-Process([[:space:]]|$)' "$chain" 2>/dev/null | grep -Evq 'Get-Process[[:space:]]+-Id([[:space:]]|$)'; then err "background/$id broad Get-Process"; fi
    while IFS= read -r line; do
      pid="$(sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p' <<<"$line")"; boot="$(sed -n 's/.*host_boot_id=\([^ |]*\).*/\1/p' <<<"$line")"; created="$(sed -n 's/.*process_creation_time=\([^ |]*\).*/\1/p' <<<"$line")"
      if [ -z "$pid" ] || [ -z "$boot" ] || [ -z "$created" ] || [ ! -f "$chain/process-started.json" ]; then err "background/$id kill lacks process-started.json identity"; continue; fi
      if process_identity_matches "$chain/process-started.json" "$id" "$pid" "$boot" "$created"; then :; else rc=$?; [ "$rc" -eq 2 ] && err "background/$id python required for kill ledger" || err "background/$id kill identity not ledger-owned"; fi
    done < <(grep '^kill:' "$status" 2>/dev/null || :)
  done
}

is_terminal_phase_status() {
  case "$1" in
    done|done\ *|verified|verified\ *|pass|pass\ *|'focused pass'|'focused pass '*|complete|complete\ *|complete\;*|completed|completed\ *|closed|closed\ *) return 0 ;;
    *) return 1 ;;
  esac
}

is_nonterminal_phase_status() {
  case "$1" in
    open|ready|ready_to_dispatch|in_phase|in\ progress|in\ progress\ *|in_progress|in_progress\ *|paused|blocked|interrupted|pending|dispatchable|finding_closure_pending|audit_handoff|handoff) return 0 ;;
    *) return 1 ;;
  esac
}

check_done_phase_captures() {
  local phase="$1" status phase_n capture target repo_prefix
  status="$(awk '
    /^IMPLEMENTAUDIT_PHASE_DONE[[:space:]]*$/ { done=1; next }
    done && /^Status:[[:space:]]*/ {
      sub(/^Status:[[:space:]]*/, ""); print tolower($0); exit
    }
  ' "$phase")"
  if is_terminal_phase_status "$status"; then
    :
  elif is_nonterminal_phase_status "$status"; then
    return 0
  elif [ -f "$roadmap" ]; then
    phase_n="$(basename "$phase" | sed -n 's/^phase-\([0-9][0-9]*\)\.md$/\1/p')"
    status="$(awk -F'|' -v n="$phase_n" '
      function trim(v) { gsub(/^[ \t]+|[ \t]+$/, "", v); return v }
      /^\|/ {
        if (!phase_table) {
          first=tolower(trim($2)); second=tolower(trim($3)); status_col=0
          if (first == "phase" || (first == "#" && second == "phase")) {
            for (i=2; i<NF; i++) if (tolower(trim($i)) == "status") status_col=i
            if (status_col) phase_table=1
          }
          next
        }
        if (trim($2) == n) { print tolower(trim($status_col)); exit }
        next
      }
      phase_table && NF && $0 !~ /^[ \t]*$/ { phase_table=0 }
    ' "$roadmap")"
    is_terminal_phase_status "$status" || return 0
  else
    return 0
  fi
  repo_prefix=""
  case "$run_root" in
    */.IMPLEMENTAUDIT/*) repo_prefix="${run_root%%/.IMPLEMENTAUDIT/*}" ;;
    .IMPLEMENTAUDIT/*) repo_prefix="." ;;
  esac
  while IFS= read -r capture; do
    capture="${capture#\`}"; capture="${capture%\`}"
    case "$capture" in
      '<run-root>') target="$run_root" ;;
      '<run-root>/'*) target="$run_root/${capture#<run-root>/}" ;;
      /*|[A-Za-z]:*) target="$capture" ;;
      "$run_root"/*) target="$capture" ;;
      *.IMPLEMENTAUDIT/*)
        capture=".IMPLEMENTAUDIT/${capture#*.IMPLEMENTAUDIT/}"
        target="${repo_prefix:+$repo_prefix/}$capture"
        ;;
      evidence/*) target="$run_root/$capture" ;;
      ./evidence/*) target="$run_root/${capture#./}" ;;
      *) continue ;;
    esac
    if ! yield_track_dependency --capture "$target"; then
      err "yield read-set DONE capture failed: $capture"; continue
    fi
    if [ ! -f "$target" ]; then
      err "DONE phase $(basename "$phase") declared capture is missing: $capture"
    elif ! has_non_whitespace "$target"; then
      err "DONE phase $(basename "$phase") declared capture is blank: $capture"
    fi
  done < <(sed -n '/^## Mandatory commands/,/^## / {
    s/.*;[[:space:]]*capture:[[:space:]]*\([^;]*\);.*/\1/p
  }' "$phase")
}

mode=full
nonterminal_yield=no
if [ "${1:-}" = "--micro" ]; then
  mode=micro
  shift
elif [ "${1:-}" = "--ledger" ]; then
  mode=ledger
  shift
elif [ "${1:-}" = "--nonterminal-yield" ]; then
  nonterminal_yield=yes
  shift
fi
run_root="${1:-}"
if [ -z "$run_root" ] || { [ "$nonterminal_yield" = yes ] && [ "$#" -ne 1 ]; }; then
  if [ "$mode" = micro ]; then
    printf 'usage: validate-run-root.sh --micro <run-root>\n' >&2
  elif [ "$mode" = ledger ]; then
    printf 'usage: validate-run-root.sh --ledger <markdown-ledger>\n' >&2
  elif [ "$nonterminal_yield" = yes ]; then
    printf 'usage: validate-run-root.sh --nonterminal-yield <run-root>\n' >&2
  else
    printf 'usage: validate-run-root.sh <run-root>\n' >&2
  fi
  exit 2
fi
[ "$mode" != ledger ] || {
  [ -f "$run_root" ] || { printf 'validate-run-root: not a file: %s\n' "$run_root" >&2; exit 2; }
  check_recurrence_decision "$run_root"
  if [ "$err_count" -gt 0 ]; then
    printf 'validate-run-root: %d error(s)\n' "$err_count" >&2
    exit 1
  fi
  printf 'validate-run-root: ok\n'
  exit 0
}
[ -d "$run_root" ] || { printf 'validate-run-root: not a directory: %s\n' "$run_root" >&2; exit 2; }

# Claim-owned canonical selection precedes every native STATE/ROADMAP guard.
# The original legacy parser remains intact; typed projection custody alone
# cannot discharge an unmapped native semantic guard.
state="$run_root/STATE.md"
roadmap="$run_root/ROADMAP.md"
canonical_record_root="$run_root"
canonical_roots=()
canonical_snapshots=()
reader="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/read-canonical-pair.py"
validation_snapshots="$(mktemp -d)" || exit 1
trap 'rm -rf "$validation_snapshots"' EXIT
reader_py=()
canonical_selection() {
  local selected_root="$1" output="$2"
  if [ "${#reader_py[@]}" -eq 0 ]; then
    if command -v python >/dev/null 2>&1; then reader_py=(python -B)
    elif command -v python3 >/dev/null 2>&1; then reader_py=(python3 -B)
    elif command -v py >/dev/null 2>&1; then reader_py=(py -3 -B)
    else printf 'validate-run-root: Python is required for canonical selection\n' >&2; return 1; fi
  fi
  PYTHONDONTWRITEBYTECODE=1 "${reader_py[@]}" "$reader" --run-root "$selected_root" --output "$output" --native-guards
}
mkdir "$validation_snapshots/pair" || exit 1
canonical_selection "$run_root" "$validation_snapshots/pair"
selection_rc=$?
case "$selection_rc" in
  0)
    state="$validation_snapshots/pair/native-STATE.md"
    roadmap="$validation_snapshots/pair/native-ROADMAP.md"
    canonical_record_root="$validation_snapshots/pair/native-records"
    canonical_roots+=("$run_root")
    canonical_snapshots+=("$validation_snapshots/pair")
    ;;
  3) : ;; # Physical absence/unbound structural legacy profile; no currentness claim.
  *) err "canonical pair selection refused; root compatibility fallback is forbidden"; exit 1 ;;
esac


# Selected-record consistency for the additive yield mode. This is read evidence,
# not controller/host currentness. Legacy records otherwise have no final pair
# token, so a stable individual late read would miss earlier structural drift.
yield_read_identity() {
  "${reader_py[@]}" - "$state" "$roadmap" "$run_root" "$@" <<'PYIDENTITY'
import hashlib,json,os,re,stat,sys
from contextlib import nullcontext
from pathlib import Path,PurePosixPath
state,roadmap,root=map(Path,sys.argv[1:4])
operation=sys.argv[4:]
records={}
class Unsupported(ValueError): pass
def read(path,textual=True,snapshot=None):
    path=path.absolute()
    for node in (path,*path.parents):
        info=node.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
            raise ValueError('aliased yield read-set member')
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or (textual and info.st_size>1_000_000):
        raise ValueError('unsafe yield read-set member')
    signature=lambda x:[x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns]
    if snapshot is not None:snapshot.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as handle, (snapshot.open('wb') if snapshot is not None else nullcontext()) as copied:
        opened=os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError('nonregular yield read-set member after open')
        digest=hashlib.sha256()
        if textual:
            data=handle.read(1_000_001);digest.update(data)
            if copied is not None:copied.write(data)
        else:
            # A consumed capture is fingerprinted as bytes. Its native owner
            # decides content applicability; no text encoding or log-size cap.
            data=None
            while True:
                chunk=handle.read(65536)
                if not chunk:break
                digest.update(chunk)
                if copied is not None:copied.write(chunk)
        closed=os.fstat(handle.fileno())
    if (textual and len(data)>1_000_000) or not signature(info)==signature(opened)==signature(closed)==signature(path.lstat()):
        raise ValueError('yield read-set changed during capture')
    records[str(path)]=[signature(closed),digest.hexdigest()]
    return data.decode('utf-8') if textual else ''
def optional(path):
    if not os.path.lexists(path):
        records[str(path.absolute())]=None
        return ''
    return read(path)
def presence(path):
    if not os.path.lexists(path): records[str(path.absolute())]=None; return
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
        raise ValueError('unsafe yield read-set presence dependency')
    records[str(path.absolute())]=['present-file',info.st_dev,info.st_ino]
def background_directory(path):
    for node in (path,*path.parents):
        info=node.lstat()
        if not stat.S_ISDIR(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
            raise ValueError('unsafe yield read-set background directory')
    return path.lstat()
def background_namespace(path):
    key='background-chains:'+str(path.absolute())
    if not os.path.lexists(path):records[key]=None;return
    info=background_directory(path);chains=[]
    for child in sorted(path.iterdir()):
        if child.name.startswith('.'):continue
        entry=child.lstat()
        if stat.S_ISLNK(entry.st_mode) or getattr(entry,'st_file_attributes',0)&0x400:
            raise ValueError('aliased yield read-set background chain')
        if stat.S_ISDIR(entry.st_mode):chains.append([str(child),entry.st_dev,entry.st_ino])
    records[key]=[[info.st_dev,info.st_ino],chains]
def background_scan(path,snapshot=None):
    info=background_directory(path);children=sorted(path.iterdir())
    records['background-members:'+str(path.absolute())]=[
        [info.st_dev,info.st_ino,info.st_mtime_ns,info.st_ctime_ns],[p.name for p in children]]
    for child in children:
        entry=child.lstat();target=snapshot/child.name if snapshot is not None else None
        if stat.S_ISDIR(entry.st_mode):background_scan(child,target)
        else:read(child,textual=False,snapshot=target)
def members(directory,pattern,recursive=False):
    if not os.path.lexists(directory):
        records['members:'+str(directory)+':'+pattern]=None
        return []
    if not stat.S_ISDIR(directory.lstat().st_mode) or directory.is_symlink():
        raise ValueError('unsafe yield read-set directory')
    if recursive:
        selected=sorted(p for p in directory.rglob(pattern) if p.is_file() and not p.is_symlink())
    else:
        selected=sorted(p for p in directory.glob(pattern) if p.is_file() or p.is_symlink())
    records['members:'+str(directory)+':'+pattern]=[str(p) for p in selected]
    return selected
def successor_review(path,snapshot=None,*,capture=False):
    # This read map is qualified only for the exact repository checker below.
    # Its semantic parser remains the sole owner of row/schema acceptance.
    references=set();expected={}
    if snapshot is not None and capture:snapshot.mkdir(parents=True,exist_ok=True)
    direct=members(path,'*.md')
    for source in direct:
        text=read(source,snapshot=snapshot/source.name if snapshot is not None and capture else None)
        expected[source.name]=records[str(source.absolute())][1]
        fenced=False
        for line in text.splitlines():
            if line.startswith('```'):fenced=not fenced;continue
            if fenced:continue
            if line.startswith('successor-review:'):
                file_fields={'predecessor_packet_scope_file','packet_scope_file'}
                finding_fields={'provisional_findings_carried'}
            elif line.startswith('lane-status:'):
                file_fields=set();finding_fields={'provisional_findings'}
            else:continue
            for part in line.split('|')[1:]:
                key,separator,value=part.partition(':');key=key.strip();value=value.strip()
                if not separator:continue
                if key in file_fields:references.add(value)
                elif key in finding_fields and value!='none':
                    references.update(ref.strip().split('#',1)[0] for ref in value.split(','))
    for raw in sorted(references):
        pure=PurePosixPath(raw)
        if pure.is_absolute() or '..' in pure.parts or '.' in pure.parts or ':' in raw or '\\' in raw:
            raise ValueError('unsafe yield read-set successor reference')
        relative=Path(*pure.parts)
        source=path/relative
        read(source,textual=False,snapshot=snapshot/relative if snapshot is not None and capture else None)
        expected[relative.as_posix()]=records[str(source.absolute())][1]
    if snapshot is not None:
        # Expected members and bytes come from the original safe reads, never
        # from parsing the private copy. A copied row cannot hide a dependency.
        if [p.name for p in members(snapshot,'*.md')]!=[p.name for p in direct]:
            raise ValueError('successor snapshot direct membership differs from source capture')
        info=snapshot.lstat()
        records['successor-snapshot:'+str(snapshot.absolute())]=[info.st_dev,info.st_ino]
        for relative,digest in sorted(expected.items()):
            copied=snapshot/relative
            read(copied,textual=False)
            if records[str(copied.absolute())][1]!=digest:
                raise ValueError('successor snapshot bytes differ from source capture')
try:
    if operation:
        kind,raw,*destination=operation;path=Path(raw)
        if len(destination)>1:raise ValueError('invalid yield snapshot destination')
        snapshot=Path(destination[0]) if destination else None
        if kind=='--successor-owner':
            try:read(path,snapshot=snapshot)
            except (OSError,ValueError) as exc:
                raise Unsupported('repository successor review owner unavailable: '+str(exc))
            if records[str(path.absolute())][1]!='9f762b1e602154bd37d561b3564ad58720934467f26a760a8cffec29727e55d1':
                raise Unsupported('repository successor review owner bytes are not qualified')
        elif kind in {'--successor-review','--successor-review-current'}:
            if snapshot is None:raise ValueError('successor snapshot destination is required')
            successor_review(path,snapshot,capture=kind=='--successor-review')
        elif kind=='--capture':read(path,textual=False,snapshot=snapshot)
        elif kind=='--background-status':
            if os.path.lexists(path):read(path,textual=False,snapshot=snapshot)
            else:records[str(path.absolute())]=None
        elif kind=='--background-presence':
            background_directory(path.parent);presence(path)
            if os.path.lexists(path):
                if path.lstat().st_nlink!=1:raise ValueError('aliased yield read-set completion presence')
                if snapshot is not None:snapshot.touch()
        elif kind=='--background-scan':background_scan(path,snapshot)
        elif kind=='--optional':optional(path)
        elif kind=='--presence':presence(path)
        elif kind=='--respec':
            # Select the same normalized fields and path as the respec owner.
            lines=read(path).splitlines()
            def field(name):
                prefix=name+':'
                values=[line[len(prefix):].strip() for line in lines if line.startswith(prefix)]
                if len(values)!=1 or not values[0]:raise ValueError('ambiguous respec dependency field: '+name)
                return values[0]
            if field('Replacement')=='yes':
                replacement=Path(field('Replacement path'))
                if not replacement.is_absolute():replacement=path.parent/replacement
                read(replacement,textual=False)
        else:raise ValueError('unknown yield read-set operation')
    else:
        text=read(state);read(roadmap)
        for name in ('PROTOCOL.md','THINKING.md','sidecars.md','tools.md','context.md'):
            read(root/name)
        optional(root/'.claimed');optional(root/'.controller')
        # The structural owner scans every phase and every direct Markdown
        # record, but not arbitrary nested evidence or still-producing logs.
        for path in members(root/'phases','phase-*.md',recursive=True):read(path)
        record_root=state.parent/'native-records' if state.name=='native-STATE.md' else root
        for path in members(record_root,'*.md'):
            read(path)
        # Match the late Current phase parser, including backtick normalization.
        lines=text.splitlines()
        if lines.count('## Current phase')==1:
            for line in lines[lines.index('## Current phase')+1:]:
                if line.startswith('## '):break
                if line.startswith('|'):
                    cells=[cell.strip(' \t`') for cell in line.split('|')[1:-1]]
                    if len(cells)==2 and cells[0]=='Phase' and re.fullmatch(r'[1-9][0-9]*',cells[1]):
                        read(root/'phases'/('phase-'+cells[1]+'.md'))
        if (root/'.claimed').is_file():
            siblings=sorted(str(p) for p in root.parent.iterdir()
                            if not p.name.startswith('.') and p.is_dir() and p!=root)
            records['sibling-members:'+str(root.parent)]=siblings
        background_namespace(root/'background')
    sys.stdout.write(json.dumps(records,sort_keys=True,separators=(',',':'))+'\n')
except Unsupported as exc:
    sys.stderr.write('validate-run-root: OUT_OF_PROFILE: unsupported yield read-set dependency: '+str(exc)+'; no yield disposition\n')
    raise SystemExit(3)
except (OSError,ValueError) as exc:
    sys.stderr.write('validate-run-root: yield read-set unavailable: '+str(exc)+'\n')
    raise SystemExit(1)
PYIDENTITY
}
yield_initial_identity=""
yield_dependency_modes=(); yield_dependency_paths=(); yield_dependency_identities=(); yield_dependency_snapshots=()
yield_track_dependency() {
  [ "$nonterminal_yield" = yes ] || return 0
  local identity mode="$1" snapshot=""
  identity="$(yield_read_identity "$@")" || return $?
  if [ "$mode" = --successor-review ]; then
    mode=--successor-review-current; snapshot="$3"
  fi
  yield_dependency_modes+=("$mode"); yield_dependency_paths+=("$2")
  yield_dependency_identities+=("$identity"); yield_dependency_snapshots+=("$snapshot")
}
if [ "$nonterminal_yield" = yes ]; then
  yield_initial_identity="$(yield_read_identity)"
  capture_rc=$?
  if [ "$capture_rc" -ne 0 ]; then
    [ "$capture_rc" -ne 3 ] || exit 3
    err "yield read-set capture failed"; exit 1
  fi
fi

claim="$run_root/.claimed"
claim_mode=""
if [ "$mode" = micro ] && [ ! -f "$claim" ]; then
  err "micro root is missing .claimed metadata"
fi
if [ -f "$claim" ]; then
  claim_mode="$(awk -F= '$1 == "mode" { print substr($0, index($0, "=") + 1); exit }' "$claim")"
  case "$claim_mode" in
    full|micro) : ;;
    *) err ".claimed has invalid mode '$claim_mode' (expected full or micro)" ;;
  esac
  if [ "$claim_mode" = micro ] && [ "$mode" != micro ]; then
    err ".claimed records mode=micro; validate this declared narrowing with --micro"
  elif [ "$claim_mode" = full ] && [ "$mode" = micro ]; then
    err ".claimed records mode=full; --micro cannot narrow a full claim"
  fi

  claimed_templates="$(awk -F= '$1 == "templates" { print substr($0, index($0, "=") + 1); exit }' "$claim")"
  for f in $claimed_templates; do
    yield_track_dependency --presence "$run_root/$f" || err "yield read-set claimed-artifact capture failed"
    [ -f "$run_root/$f" ] || err "claimed $f is missing — sentinel/artifact drift"
  done
fi

if [ "$mode" = micro ]; then
  [ -f "$state" ] || err "missing required artifact: STATE.md"
else
  root_done=no
  if grep -Eq '^\|[[:space:]]*Status[[:space:]]*\|[[:space:]]*DONE[[:space:]]*\|' \
    "$state" 2>/dev/null; then
    root_done=yes
  fi
  template_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../templates" && pwd)"
  for f in STATE.md PROTOCOL.md; do
    artifact_path="$run_root/$f"; [ "$f" != STATE.md ] || artifact_path="$state"
    if [ ! -f "$artifact_path" ]; then err "missing required artifact: $f"
    elif ! has_non_whitespace "$artifact_path"; then err "required artifact is blank: $f"; fi
  done
  for f in ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
    artifact_path="$run_root/$f"; [ "$f" != ROADMAP.md ] || artifact_path="$roadmap"
    artifact_status="$(awk -F'|' -v artifact="<run-root>/$f" '
      function trim(v) { gsub(/^[ \t`]+|[ \t`]+$/, "", v); return v }
      trim($2) == artifact { print tolower(trim($3)); exit }
    ' "$state" 2>/dev/null)"
    if [ ! -f "$artifact_path" ]; then err "missing planning artifact: $f (required for dispatched phase runs)"
    elif ! has_non_whitespace "$artifact_path"; then err "planning artifact is blank: $f"; fi
    if [ "$root_done" = yes ] && [ "$artifact_status" = complete ] &&
       [ -f "$artifact_path" ] &&
       cmp -s "$artifact_path" "$template_dir/$f"; then
      err "planning artifact remains an unfilled template at DONE: $f"
    fi
  done
fi

if [ "$mode" = full ] && [ -d "$run_root/phases" ]; then
  while IFS= read -r phase; do check_done_phase_captures "$phase"; done \
    < <(find "$run_root/phases" -type f -name 'phase-*.md' -print | sort)
fi

if [ -f "$state" ]; then
  if [ "$mode" = full ]; then
    status_line="$(grep -E '^\| Status \|' "$state" | head -1 || true)"
    if [ -z "$status_line" ]; then
      err "STATE.md has no '| Status |' row in the Current phase table"
    else
      status_value="$(printf '%s' "$status_line" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3}')"
      case "$status_value" in
        open|READY_TO_DISPATCH|IN_PHASE|PAUSED|BLOCKED|INTERRUPTED|DONE) : ;;
        *) err "STATE.md Status '$status_value' is not a contract token (open / READY_TO_DISPATCH / IN_PHASE / PAUSED / BLOCKED / INTERRUPTED / DONE)" ;;
      esac
    fi
  fi

  if ! grep -qi '^## Andon log' "$state"; then
    err "STATE.md is missing the '## Andon log' section"
  elif grep -qi '| Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |' "$state"; then
    missing_occ="$(awk -F'|' '
      /^## Andon log/ { in_andon=1; next }
      in_andon && /^## / { in_andon=0 }
      in_andon && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
        occ=$3; gsub(/^[ \t]+|[ \t]+$/, "", occ)
        if (occ == "") { n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n); print n }
      }' "$state")"
    if [ -n "$missing_occ" ]; then
      err "STATE.md Andon log new-format rows missing an Occ occurrence id: row(s) $(printf '%s' "$missing_occ" | tr '\n' ' ')"
    fi
    multi_class="$(awk -F'|' '
      /^## Andon log/ { in_andon=1; next }
      in_andon && /^## / { in_andon=0 }
      in_andon && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
        cls=$5; gsub(/^[ \t]+|[ \t]+$/, "", cls)
        if (cls != "" && cls !~ /^[A-Za-z-]+$/) {
          n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n); print n }
      }' "$state")"
    if [ -n "$multi_class" ]; then
      err "STATE.md Andon log row(s) with a non-single-token Class (exactly one class per row; plural defects record one row per class sharing an Occ id): row(s) $(printf '%s' "$multi_class" | tr '\n' ' ')"
    fi
  elif ! grep -qi '| Class | Abnormality | Countermeasure | Rerun evidence | Outcome |' "$state"; then
    err "STATE.md Andon log table is missing the contract columns (# | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome; legacy shape without Occ also accepted)"
  fi
  check_recurrence_decision "$state"

  if [ "$mode" = micro ]; then
    terminal_line="$(awk 'NF { last=$0 } END { print last }' "$state")"
    case "$terminal_line" in
      AUDIT_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF) : ;;
      IMPLEMENTAUDIT_RUN_COMPLETE)
        grep -qx 'AUDIT_COMPLETE' "$state" || err "STATE.md ends with IMPLEMENTAUDIT_RUN_COMPLETE but has no preceding AUDIT_COMPLETE"
        ;;
      *) err "micro STATE.md final nonblank line is not a terminal marker (AUDIT_COMPLETE / IMPLEMENTAUDIT_RUN_COMPLETE / AUDIT_HANDOFF / ANDON_HANDOFF)" ;;
    esac

    if find "$run_root/phases" -type f -name 'phase-*.md' -print -quit 2>/dev/null | grep -q .; then
      err "micro root contains phase specs; phased dispatch requires a full run root"
    fi
    if [ -f "$roadmap" ] && grep -Eq '^\|[[:space:]]*[0-9]+[[:space:]]*\|' "$roadmap"; then
      err "micro root contains a ROADMAP phase table; phased dispatch requires a full run root"
    fi
    if grep -R -E -q '^(Stage 6\.i|Stage 6\.2|Independent cold-review disposition|Review disposition):' "$run_root" \
      --exclude='.claimed' 2>/dev/null; then
      err "micro root contains a Stage 6.i (legacy 6.2) disposition; executor-facing review requires a full run root"
    fi
    extra_micro_files="$(cd "$run_root" && find . -type f \
      ! -path './.claimed' ! -path './STATE.md' ! -path './deferrals.jsonl' \
      -print 2>/dev/null || true)"
    if [ -n "$extra_micro_files" ]; then
      err "micro root contains undeclared extra payload: $(printf '%s' "$extra_micro_files" | tr '\n' ' ')"
    fi
    if grep -Eqi '(second-order|higher-order) retrospective.*(reduced|waived|fewer) obligations' "$state"; then
      err "retrospective meta-tier cannot reduce governed-run obligations"
    fi
  fi
fi


if [ -f "$claim" ]; then
  run_base="$(dirname "$run_root")"
  for sibling in "$run_base"/*; do
    [ -d "$sibling" ] || continue
    [ "$sibling" = "$run_root" ] && continue
    sibling_state="$sibling/STATE.md"
    yield_track_dependency --optional "$sibling/.claimed" || { err "yield read-set sibling claim capture failed"; continue; }
    yield_track_dependency --optional "$sibling/.controller" || { err "yield read-set sibling controller capture failed"; continue; }
    sibling_snapshot="$(mktemp -d "$validation_snapshots/sibling.XXXXXX")" || exit 1
    canonical_selection "$sibling" "$sibling_snapshot"
    sibling_rc=$?
    case "$sibling_rc" in
      0) sibling_state="$sibling_snapshot/native-STATE.md"
         canonical_roots+=("$sibling")
         canonical_snapshots+=("$sibling_snapshot") ;;
      3) : ;;
      *) err "sibling canonical selection refused: $(basename "$sibling")"; continue ;;
    esac
    yield_track_dependency --capture "$sibling_state" || { err "yield read-set sibling STATE capture failed"; continue; }
    if [ ! -f "$sibling_state" ] || ! grep -Eq \
      '^(AUDIT_COMPLETE|IMPLEMENTAUDIT_RUN_COMPLETE|AUDIT_HANDOFF|ANDON_HANDOFF|COMPLETE|HANDOFF|SUPERSEDED_BY:[[:space:]].+|PARALLEL:[[:space:]].+)$' \
      "$sibling_state"; then
      err "newly claimed root has undispositioned sibling: $(basename "$sibling")"
    fi
  done
fi

if [ -f "$state" ] && grep -qi '^## Occurrence resolution and residuals' "$state"; then
  occ_res="$(awk '/^## Occurrence resolution and residuals/{f=1;next} f&&/^Occurrence resolution:/{sub(/^Occurrence resolution:[ \t]*/,"");print;exit}' "$state")"
  case "$occ_res" in
    not-applicable|unresolved|partially-resolved|resolved) : ;;
    *) err "STATE.md Occurrence resolution '$occ_res' is not a contract token (not-applicable / unresolved / partially-resolved / resolved)" ;;
  esac
  bad_disp="$(awk -F'|' '
    /^## Occurrence resolution and residuals/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      d=$4; gsub(/^[ \t]+|[ \t]+$/, "", d)
      r=$2; gsub(/^[ \t]+|[ \t]+$/, "", r)
      if (r == "Residual" || r ~ /^-+$/ || r == "") next
      if (d !~ /^(unresolved|deferred|transferred|owner-assigned|risk-accepted|validated-resolved|SUPERSEDED_BY_CONCURRENT_MUTATION)$/) print r
    }' "$state")"
  if [ -n "$bad_disp" ]; then
    err "STATE.md residual row(s) with invalid disposition: $(printf '%s' "$bad_disp" | tr '\n' ' ') (allowed: unresolved / deferred / transferred / owner-assigned / risk-accepted / validated-resolved / SUPERSEDED_BY_CONCURRENT_MUTATION)"
  fi
  no_ref="$(awk -F'|' '
    /^## Occurrence resolution and residuals/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      d=$4; gsub(/^[ \t]+|[ \t]+$/, "", d)
      o=$5; gsub(/^[ \t]+|[ \t]+$/, "", o)
      r=$2; gsub(/^[ \t]+|[ \t]+$/, "", r)
      if (r == "Residual" || r ~ /^-+$/ || r == "") next
      if ((d == "transferred" || d == "risk-accepted") &&
          (o == "" || o ~ /^-+$/)) print r
    }' "$state")"
  if [ -n "$no_ref" ]; then
    err "STATE.md residual row(s) with transferred/risk-accepted but no owner/policy ref: $(printf '%s' "$no_ref" | tr '\n' ' ') (transferred names the receiving owner; risk-accepted cites the policy)"
  fi
fi

# #87 execution identity is prospective. Legacy roots without a row remain
# valid. New rows use the sibling-harness vocabulary exactly once; a requested
# versus actual mismatch is transport, never an independent/bound executor.
if [ -f "$state" ] && grep -qi '^[[:space:]]*model-identity:' "$state"; then
  identity_total="$(grep -Eic '^[[:space:]]*model-identity:' "$state")"
  identity_valid="$(grep -Ec '^model-identity: requested_model: [^|[:space:]][^|]* \| actual_model: [^|[:space:]][^|]* \| evidence: (self-report|host-event:[^|[:space:]][^|]*) \| claims: (bound|IDENTITY_UNBOUND)$' "$state" || true)"
  [ "$identity_total" -eq "$identity_valid" ] \
    || err "STATE.md model-identity row must use exact requested_model / actual_model / evidence / claims grammar"
  has_transport="$(awk -F'|' '
    /^## Andon log/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      c=$5; gsub(/^[ \t]+|[ \t]+$/, "", c)
      if (c == "transport-infrastructure") found=1
    }
    END { print found ? "yes" : "no" }
  ' "$state")"
  while IFS= read -r identity_line; do
    [ -n "$identity_line" ] || continue
    requested="$(printf '%s\n' "$identity_line" | sed -E 's/^model-identity: requested_model: ([^|]+) \|.*/\1/; s/[[:space:]]+$//')"
    actual="$(printf '%s\n' "$identity_line" | sed -E 's/.*\| actual_model: ([^|]+) \|.*/\1/; s/[[:space:]]+$//')"
    identity_evidence="$(printf '%s\n' "$identity_line" | sed -E 's/.*\| evidence: ([^|]+) \|.*/\1/; s/[[:space:]]+$//')"
    claims="$(printf '%s\n' "$identity_line" | sed -E 's/.*\| claims: ([^|]+)$/\1/; s/[[:space:]]+$//')"
    if [ "$requested" = "$actual" ]; then
      [ "$claims" = bound ] \
        || err "STATE.md equal requested_model/actual_model must keep claims bound"
    else
      [ "$claims" = IDENTITY_UNBOUND ] \
        || err "STATE.md model substitution must mark claims IDENTITY_UNBOUND"
      [ "$has_transport" = yes ] \
        || err "STATE.md model substitution requires a transport-infrastructure Andon row"
      event_bound="$(awk -F'|' -v token="$identity_evidence" '
        /^## Andon log/ { f=1; next }
        f && /^## / { f=0 }
        f && /^\|/ {
          c=$5; gsub(/^[ \t]+|[ \t]+$/, "", c)
          e=$8; gsub(/^[ \t]+|[ \t]+$/, "", e)
          if (c == "transport-infrastructure" && e == token) found=1
        }
        END { print found ? "yes" : "no" }
      ' "$state")"
      [ "$event_bound" = yes ] \
        || err "STATE.md model substitution evidence must bind the transport-infrastructure Andon evidence cell"
    fi
  done < <(grep -E '^model-identity:' "$state" || true)
fi

# #86 cold-review provenance is prospective. Legacy roots without a row stay
# valid. Once declared, every disposition resolves a contained attestation;
# an authoring-context report is retained as self-critique but cannot satisfy
# the independent cold-review gate.
if [ -f "$state" ] && grep -qi '^[[:space:]]*cold-review[[:space:]]*:' "$state"; then
  cold_py=()
  if command -v python >/dev/null 2>&1; then cold_py=(python)
  elif command -v python3 >/dev/null 2>&1; then cold_py=(python3)
  elif command -v py >/dev/null 2>&1; then cold_py=(py -3)
  else
    err "python, python3, or py -3 is required for cold-review attestation validation"
  fi
  if [ "${#cold_py[@]}" -gt 0 ]; then
    if [ "$nonterminal_yield" = yes ]; then
      while IFS= read -r attestation; do
        yield_track_dependency --capture "$canonical_record_root/$attestation" || err "yield read-set cold-review capture failed"
      done < <(sed -nE 's/^cold-review:.*\| attestation: ([A-Za-z0-9._/-]+) \|.*/\1/p' "$state")
    fi
    cold_error=""
    if ! cold_error="$("${cold_py[@]}" - "$run_root" "$state" "$canonical_record_root" <<'PY'
import pathlib
import re
import subprocess
import sys

repository_run = pathlib.Path(sys.argv[1]).resolve()
root = pathlib.Path(sys.argv[3]).resolve()
state = pathlib.Path(sys.argv[2])
lines = state.read_text(encoding="utf-8").splitlines()


def die(message):
    print(message)
    raise SystemExit(1)


near = [line for line in lines if re.match(r"^\s*cold-review\s*:", line, re.I)]
exact = [line for line in lines if line.startswith("cold-review:")]
if len(near) != len(exact):
    die("STATE.md cold-review rows must use exact lowercase column-zero grammar")

row_re = re.compile(
    r"^cold-review: disposition: (PASS|GAP-REVISE|BLOCKED|OWNER DECISION) "
    r"\| attestation: ([A-Za-z0-9._/-]+) "
    r"\| base_sha: ([0-9a-f]{40}) \| head_sha: ([0-9a-f]{40})$"
)
keys = (
    "reviewer_identity", "requested_model", "actual_model",
    "authoring_context_reuse", "other_reviewer_output_seen",
    "base_sha", "head_sha",
)

for line in exact:
    match = row_re.fullmatch(line)
    if not match:
        die("STATE.md cold-review row must use exact disposition and attestation grammar")
    disposition = match.group(1)
    rel = match.group(2)
    declared_base = match.group(3)
    declared_head = match.group(4)
    pure = pathlib.PurePosixPath(rel)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts or ":" in rel or "\\" in rel:
        die("cold-review attestation path must be safe and run-root-relative")
    artifact_path = root / pathlib.Path(*pure.parts)
    artifact = artifact_path.resolve()
    try:
        artifact.relative_to(root)
    except ValueError:
        die("cold-review attestation escapes the run root")
    if not artifact_path.is_file() or artifact_path.is_symlink():
        die("cold-review attestation must resolve to a regular non-symlink file")
    report = artifact.read_text(encoding="utf-8").splitlines()
    if report.count("Reviewer attestation:") != 1:
        die("cold-review artifact requires exactly one Reviewer attestation header")
    header_index = report.index("Reviewer attestation:")
    block = report[header_index + 1:header_index + 1 + len(keys)]
    if len(block) != len(keys):
        die("cold-review artifact has an incomplete Reviewer attestation block")
    values = {}
    for index, key in enumerate(keys):
        key_near = [item for item in report if re.match(rf"^\s*-\s*{re.escape(key)}\s*:", item, re.I)]
        key_exact = [item for item in report if item.startswith(f"- {key}:")]
        if len(key_near) != 1 or len(key_exact) != 1:
            die(f"cold-review attestation requires exactly one exact {key} field")
        if block[index] != key_exact[0]:
            die("cold-review attestation fields must form one exact ordered header block")
        value = block[index].split(":", 1)[1].strip()
        if not value:
            die(f"cold-review attestation {key} is empty")
        values[key] = value
    if values["authoring_context_reuse"] not in {"yes", "no"}:
        die("cold-review authoring_context_reuse must be yes or no")
    if values["other_reviewer_output_seen"] not in {"yes", "no"}:
        die("cold-review other_reviewer_output_seen must be yes or no")
    if values["authoring_context_reuse"] == "yes":
        die("authoring-context reuse labels self-critique and cannot discharge cold review")
    for key in ("base_sha", "head_sha"):
        if not re.fullmatch(r"[0-9a-f]{40}", values[key]):
            die(f"cold-review {key} must be full lowercase 40-hex")
    if values["base_sha"] != declared_base or values["head_sha"] != declared_head:
        die("cold-review attestation base/head must match the STATE review identity")

    report_state_near = [item for item in report if re.match(r"^\s*Report state\s*:", item, re.I)]
    report_state_exact = [item for item in report if item == "Report state: FINAL"]
    if len(report_state_near) != 1 or len(report_state_exact) != 1:
        die("cold-review artifact requires exactly one Report state: FINAL")

    identity_re = re.compile(
        r"^model-identity: requested_model: ([^|\s][^|]*) \| "
        r"actual_model: ([^|\s][^|]*) \| evidence: "
        r"(?:self-report|host-event:[^|\s][^|]*) \| "
        r"claims: (bound|IDENTITY_UNBOUND)$"
    )
    identities = []
    for state_line in lines:
        identity_match = identity_re.fullmatch(state_line)
        if identity_match:
            identities.append(tuple(item.strip() for item in identity_match.groups()))
    matching_identity = [
        item for item in identities
        if item[0] == values["requested_model"] and item[1] == values["actual_model"]
    ]
    if len(matching_identity) != 1:
        die("cold-review attestation model pair must match one canonical STATE model-identity row")
    expected_claims = "bound" if values["requested_model"] == values["actual_model"] else "IDENTITY_UNBOUND"
    if matching_identity[0][2] != expected_claims:
        die("cold-review attestation model pair conflicts with STATE identity claims")
    if disposition == "PASS" and expected_claims != "bound":
        die("cold-review PASS requires bound requested_model and actual_model identity")

    allowed = {"PASS", "GAP-REVISE", "BLOCKED", "OWNER DECISION"}
    nonempty = [item for item in report if item.strip()]
    terminal = [item for item in report if item in allowed]
    if len(terminal) != 1 or not nonempty or nonempty[-1] != disposition:
        die("cold-review artifact requires one exact final disposition matching STATE")
    for prefix in ("Verdict:", "Disposition:", "cold-review-disposition:"):
        near_rows = [item for item in report if re.match(rf"^\s*{re.escape(prefix[:-1])}\s*:", item, re.I)]
        exact_rows = [item for item in report if item.startswith(prefix)]
        if len(near_rows) != len(exact_rows):
            die(f"cold-review artifact {prefix[:-1]} rows require exact grammar")
        for item in exact_rows:
            value = item.split(":", 1)[1].strip()
            if value not in allowed or value != disposition:
                die("cold-review artifact contains a contradictory disposition")

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repository_run), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    repo = git("rev-parse", "--show-toplevel")
    if repo.returncode != 0:
        die("cold-review identity requires a containing Git repository")
    for key, sha in (("base_sha", declared_base), ("head_sha", declared_head)):
        resolved = git("cat-file", "-t", sha)
        if resolved.returncode != 0 or resolved.stdout.strip() != "commit":
            die(f"cold-review {key} does not resolve to a commit")
    if declared_base == declared_head:
        die("cold-review base_sha must strictly precede head_sha")
    ancestry = git("merge-base", "--is-ancestor", declared_base, declared_head)
    if ancestry.returncode != 0:
        die("cold-review base_sha must be an ancestor of head_sha")
PY
)"; then
      [ -n "$cold_error" ] || cold_error="cold-review attestation validation failed"
      err "$cold_error"
    fi
  fi
fi

# The repository-side #86 successor/non-verdict parser is mandatory whenever a
# live record root carries those prospective rows. Direct Markdown files are
# the record surface; nested installs, frozen repositories, and fixture corpora
# retain their own custody and must not activate the current root's parser.
# Installed consumers without the repo checker still fail closed for an actual
# direct live row instead of silently treating the contract as optional.
if grep -E -q '^(successor-review:|lane-status: status: REVIEWER_RUNTIME_NON_VERDICT)' \
  "$canonical_record_root"/*.md 2>/dev/null; then
  validator_repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." 2>/dev/null && pwd || true)"
  live_cold_checker="$validator_repo_root/scripts/check-cold-review-contract.sh" # source repo checker; absent from installed skill by design
  if [ -z "$validator_repo_root" ] || [ ! -f "$live_cold_checker" ] || [ -L "$live_cold_checker" ]; then
    if [ "$nonterminal_yield" = yes ]; then
      printf 'validate-run-root: OUT_OF_PROFILE: repository successor review owner unavailable; no yield disposition\n' >&2
      exit 3
    fi
    err "live successor/non-verdict rows require the repository cold-review checker"
  else
    cold_checker_args=(--run-root "$canonical_record_root")
    if [ "$nonterminal_yield" = yes ]; then
      if review_snapshot="$(mktemp -d "$validation_snapshots/review.XXXXXXXX")" &&
         yield_track_dependency --successor-owner "$live_cold_checker" "$review_snapshot/check-cold-review-contract.sh" &&
         yield_track_dependency --successor-owner "$review_snapshot/check-cold-review-contract.sh" &&
         yield_track_dependency --successor-review "$canonical_record_root" "$review_snapshot/records"; then
        live_cold_checker="$review_snapshot/check-cold-review-contract.sh"
        cold_checker_args=(--repo-root "$validator_repo_root" --run-root "$review_snapshot/records")
      else
        capture_rc=$?; [ "$capture_rc" -ne 3 ] || exit 3
        err "yield read-set successor review capture failed"
        live_cold_checker=""
      fi
    fi
    if [ -n "$live_cold_checker" ] && ! bash "$live_cold_checker" "${cold_checker_args[@]}" >/dev/null; then
      err "live successor/non-verdict contract failed"
    fi
  fi
fi

if [ -f "$state" ] && grep -qi '^## Context epochs and instruction applicability' "$state"; then
  current_epoch="$(sed -n 's/^Current epoch: //p' "$state")"
  if ! printf '%s\n' "$current_epoch" | grep -Eq '^(e[1-9][0-9]*|G[0-9A-F]{4})$' \
      || [ "$current_epoch" = G0000 ]; then
    err "STATE.md Current epoch must be a positive legacy eNN identity or canonical G plus uppercase HEX4"
  fi
  bad_epoch_id="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|/ {
      e=$2; gsub(/^[ \t]+|[ \t]+$/, "", e)
      if (e ~ /^[eGg]/ &&
          (e !~ /^(e[1-9][0-9]*|G[0-9A-F]{4})$/ || e == "G0000")) print e
    }' "$state")"
  if [ -n "$bad_epoch_id" ]; then
    err "STATE.md epoch row(s) use malformed durable generation identities: $(printf '%s' "$bad_epoch_id" | tr '\n' ' ')"
  fi
  native_rotation_epoch=""
  [ "$selection_rc" -ne 0 ] || native_rotation_epoch="$current_epoch"
  bad_prov="$(awk -F'|' -v native_epoch="$native_rotation_epoch" '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*(e[1-9][0-9]*|G[0-9A-F]{4})[[:space:]]*\|/ {
      p=$3; gsub(/^[ \t]+|[ \t]+$/, "", p)
      e=$2; gsub(/^[ \t]+|[ \t]+$/, "", e)
      note=$7; gsub(/^[ \t]+|[ \t]+$/, "", note)
      bound_rotation=(native_epoch != "" && p == "canonical-state-rotation" &&
                      (e != native_epoch || note == "native pointer JOIN"))
      if (p !~ /^(host-reported-compaction|new-session|handoff-resume|manual-resume|inferred-context-gap)$/ && !bound_rotation) print e
    }' "$state")"
  if [ -n "$bad_prov" ]; then
    err "STATE.md epoch row(s) with invalid boundary provenance: $(printf '%s' "$bad_prov" | tr '\n' ' ') (allowed: host-reported-compaction / new-session / handoff-resume / manual-resume / inferred-context-gap; never fabricate a compaction)"
  fi
  bad_instr="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*i[0-9]+[[:space:]]*\|/ {
      k=$4; gsub(/^[ \t]+|[ \t]+$/, "", k)
      s=$8; gsub(/^[ \t]+|[ \t]+$/, "", s)
      n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n)
      okk = (k ~ /^(one-shot-action|standing-constraint|standing-authorization|persistent-objective|query-or-information-request)$/)
      oks = (s ~ /^(active|satisfied|superseded|revoked|expired|ambiguous)$/)
      if (!okk || !oks) print n
    }' "$state")"
  if [ -n "$bad_instr" ]; then
    err "STATE.md instruction row(s) with invalid kind/status token: $(printf '%s' "$bad_instr" | tr '\n' ' ') (kind: one-shot-action / standing-constraint / standing-authorization / persistent-objective / query-or-information-request; status: active / satisfied / superseded / revoked / expired / ambiguous)"
  fi
  no_ev="$(awk -F'|' '
    /^## Context epochs and instruction applicability/ { f=1; next }
    f && /^## / { f=0 }
    f && /^\|[[:space:]]*i[0-9]+[[:space:]]*\|/ {
      s=$8; gsub(/^[ \t]+|[ \t]+$/, "", s)
      ev=$9; gsub(/^[ \t]+|[ \t]+$/, "", ev)
      n=$2; gsub(/^[ \t]+|[ \t]+$/, "", n)
      if (s ~ /^(satisfied|superseded|revoked|expired)$/ &&
          (ev == "" || ev ~ /^-+$/)) print n
    }' "$state")"
  if [ -n "$no_ev" ]; then
    err "STATE.md instruction row(s) with terminal status but no status evidence: $(printf '%s' "$no_ev" | tr '\n' ' ') (satisfied/superseded/revoked/expired require evidence — a bare terminal claim is the replay hazard #35 forbids)"
  fi
fi

if [ -f "$state" ]; then
  short_anchors="$(grep -oE '@[0-9a-f]{7,}' "$state" 2>/dev/null \
    | grep -vE '^@[0-9a-f]{40}$' || true)"
  if [ -n "$short_anchors" ]; then
    err "STATE.md evidence anchor(s) not full 40-hex SHAs: $(printf '%s' "$short_anchors" | tr '\n' ' ')"
  fi
fi

if [ -f "$roadmap" ] && [ -d "$run_root/phases" ]; then
  while IFS= read -r n; do
    [ -f "$run_root/phases/phase-$n.md" ] || err "ROADMAP names phase $n but phases/phase-$n.md is missing"
  done < <(grep -oE '^\| *[0-9]+ *\|' "$roadmap" 2>/dev/null | grep -oE '[0-9]+' | sort -un)
fi

check_background_chains "$run_root" "$state"

# R0037's additive record predicate shares the selected canonical pair and the
# ordinary structural checks above. It neither binds a host session nor grants
# Stop, currentness, effect, handoff or closure authority. Native callers must
# establish their authentic binding/currentness through the existing owners.
if [ "$nonterminal_yield" = yes ] && [ "$err_count" -eq 0 ]; then
  if ! "${reader_py[@]}" - "$state" "$run_root" <<'PY'
import os
from pathlib import Path
import re
import stat
import sys

state, root = map(Path, sys.argv[1:])

def refuse(reason):
    raise SystemExit("validate-run-root: nonterminal yield refused: " + reason)

def read_regular(path):
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or getattr(before, 'st_file_attributes', 0) & 0x400
                or before.st_size > 1_000_000):
            refuse("unsafe or oversized record: " + path.name)
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
        with os.fdopen(fd, 'rb') as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode):
                refuse("nonregular record after open: " + path.name)
            data = stream.read(1_000_001)
            after = os.fstat(stream.fileno())
        signature = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if (len(data) > 1_000_000 or signature(before) != signature(opened)
                or signature(opened) != signature(after) or signature(after) != signature(path.lstat())):
            refuse("record changed while read: " + path.name)
        return data.decode('utf-8', 'strict').splitlines()
    except (OSError, UnicodeError) as exc:
        refuse("unreadable record: " + str(exc))

lines = read_regular(state)
if lines.count('## Current phase') != 1:
    refuse("exactly one Current phase section is required")
fields = {}
for line in lines[lines.index('## Current phase') + 1:]:
    if line.startswith('## '):
        break
    if not line.startswith('|'):
        continue
    cells = [cell.strip(' \t`') for cell in line.split('|')[1:-1]]
    if len(cells) != 2:
        refuse("malformed Current phase row")
    key, value = cells
    if key == 'Field' or re.fullmatch(r'[-:]+', key or ' '):
        continue
    if key in fields:
        refuse("duplicate Current phase field: " + key)
    fields[key] = value

placeholders = {'', '-', 'none', 'pending', 'todo', 'tbd', 'unknown', 'n/a', 'not applicable'}
def required(key):
    value = fields.get(key, '')
    if value.strip(' <>[]').lower() in placeholders or not value.strip():
        refuse("missing concrete " + key)
    return value

def action(key):
    value = required(key).lower()
    # Record concreteness is not a closed English verb grammar or proof of
    # semantic sufficiency. Reject unresolved templates and bare continuations.
    ignored = {'a', 'an', 'and', 'at', 'for', 'from', 'it', 'now', 'of', 'on', 'or', 'that', 'the', 'then', 'this', 'to', 'with'} | placeholders
    words = re.findall(r'[a-z0-9]+', value)
    # Recognized placeholders remain unresolved inside paths or with suffixes.
    # Indexed expressions, parameterized tests and shell variables stay literal.
    token = r'(?:command|target|path|file|name|value|action|probe|todo|tbd)'
    template = r'<\s*' + token + r'\s*>|(?<![\w$])(?:\[\s*' + token + r'\s*\]|\{\s*' + token + r'\s*\})'
    if (re.search(template, value)
            or len(words) < 2 or not any(word not in ignored for word in words[1:])):
        refuse("non-actionable " + key)

status = required('Status')
if status not in {'open', 'READY_TO_DISPATCH', 'IN_PHASE', 'PAUSED', 'BLOCKED', 'INTERRUPTED'}:
    refuse("status is not nonterminal")
if required('Audit object state') != 'open':
    refuse("audit object is not explicitly open")
for key in ('Phase', 'Last check', 'Owner/source', 'Authorization state', 'Re-entry condition'):
    required(key)
action('Next action')
if any(line.strip() in {'AUDIT_COMPLETE', 'IMPLEMENTAUDIT_RUN_COMPLETE', 'AUDIT_HANDOFF', 'ANDON_HANDOFF'} for line in lines):
    refuse("terminal or handoff claim cannot use the yield predicate")

phase = fields['Phase']
if re.fullmatch(r'[1-9][0-9]*', phase):
    phase_path = root / 'phases' / ('phase-' + phase + '.md')
    if not phase_path.parent.is_dir() or phase_path.parent.is_symlink():
        refuse("current phase directory is absent or aliased")
    phase_lines = read_regular(phase_path)
    phase_ids = {match.group(1) for line in phase_lines
                 if (match := re.match(r'^(?:Phase:\s*|# Phase\s+)([1-9][0-9]*)(?:\s|$)', line))}
    if phase_ids != {phase}:
        refuse("current phase specification identity differs")
elif status not in {'open', 'READY_TO_DISPATCH', 'PAUSED', 'BLOCKED', 'INTERRUPTED'}:
    refuse("active phase must identify its specification")

if status == 'IN_PHASE':
    required('Current checkpoint')
    required('Last completed step')
elif status == 'PAUSED':
    required('Pause reason')
    required('Resume point')
    trigger = required('Pause trigger')
    if trigger not in {'clarification', 'owner-authority', 'external-wait', 'user-interruption'}:
        refuse("unknown pause trigger")
    if trigger == 'external-wait':
        required('Blocker')
        required('Containment')
        action('Next probe')
    if trigger == 'user-interruption':
        context = required('Pause phase context')
        if context not in {'IN_PROGRESS', 'OUTSIDE_PHASE'}:
            refuse("unknown pause phase context")
        # Phase specs contain START/DONE template anchors before execution.
        # Applicability is an explicit supplied fact, not inferred chronology.
        if context == 'OUTSIDE_PHASE':
            if 'IMPLEMENTAUDIT_PAUSE' in lines:
                refuse("out-of-phase user pause cannot fabricate an in-phase pause record")
        else:
            if not re.fullmatch(r'[1-9][0-9]*', phase):
                refuse("in-progress user pause requires a numbered phase")
            if lines.count('IMPLEMENTAUDIT_PAUSE') != 1:
                refuse("user interruption requires its existing pause record")
            start = lines.index('IMPLEMENTAUDIT_PAUSE') + 1
            block = lines[start:start + 4]
            if (len(block) != 4 or block[0] != 'Phase: ' + phase
                    or block[1] not in {'Status: paused at boundary', 'Status: paused mid-step'}
                    or not block[2].startswith('Last completed step: ')
                    or block[2].split(':', 1)[1].strip().lower() in placeholders
                    or block[3] != 'STATE.md: updated'):
                refuse("pause record is incomplete, foreign or not durable")
            if ('Last completed step' in fields
                    and block[2].split(':', 1)[1].strip() != fields['Last completed step']):
                refuse("pause record contradicts the current last completed step")
elif status == 'BLOCKED':
    required('Blocker')
    required('Containment')
    action('Next probe')
elif status == 'INTERRUPTED':
    source = required('Stop source')
    point = required('Interruption point')
    log_id = required('Interruption log')
    in_log, matching = False, []
    for line in lines:
        if line.startswith('## '):
            in_log = line == '## Andon log'
        elif in_log and line.startswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and cells[0] == log_id:
                matching.append(cells)
    def exact_phrase(value, text):
        return re.search(r'(?<![A-Za-z0-9_.:@+/-])' + re.escape(value)
                         + r'(?![A-Za-z0-9_.:@+/-])', text) is not None
    row = matching[0] if len(matching) == 1 else []
    # Preserve both existing Andon shapes (with and without Occ).
    phase_index, text_index = (2, 4) if len(row) == 8 else (1, 3)
    if (len(row) not in {7, 8} or not exact_phrase(source, row[text_index])
            or not exact_phrase(point, row[text_index])
            or (re.fullmatch(r'[1-9][0-9]*', phase) and row[phase_index] != phase)):
        refuse("owner stop/interruption point lacks its exact durable log row")
else:
    required('Pending decision')

sys.stdout.write('validate-run-root: nonterminal yield record ok (source-only; host enforcement unavailable)\n')
PY
  then
    err "nonterminal-yield predicate failed"
  fi
fi

if [ -f "$run_root/respec-impact-set.md" ]; then
  yield_track_dependency --respec "$run_root/respec-impact-set.md" || err "yield read-set respec replacement capture failed"
  respec_checker="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check-respec-impact-set.sh"
  respec_output="$(bash "$respec_checker" "$run_root/respec-impact-set.md" 2>&1)" \
    || err "respec-impact-set.md invalid: $respec_output"
fi

if [ "$err_count" -eq 0 ]; then
  for i in "${!canonical_roots[@]}"; do
    PYTHONDONTWRITEBYTECODE=1 "${reader_py[@]}" "$reader" --run-root "${canonical_roots[$i]}" \
      --output "${canonical_snapshots[$i]}" --native-guards --verify-current \
      || err "canonical inputs changed before native validation completed"
  done
fi

if [ "$nonterminal_yield" = yes ] && [ "$err_count" -eq 0 ]; then
  yield_final_identity="$(yield_read_identity)" || err "yield read-set recheck failed"
  [ "$yield_initial_identity" = "$yield_final_identity" ] || err "yield read-set changed during validation"
  for i in "${!yield_dependency_paths[@]}"; do
    dependency_arguments=("${yield_dependency_modes[$i]}" "${yield_dependency_paths[$i]}")
    if [ -n "${yield_dependency_snapshots[$i]}" ]; then
      dependency_arguments+=("${yield_dependency_snapshots[$i]}")
    fi
    dependency_identity="$(yield_read_identity "${dependency_arguments[@]}")"
    capture_rc=$?
    if [ "$capture_rc" -ne 0 ]; then
      [ "$capture_rc" -ne 3 ] || exit 3
      err "yield read-set dependency recheck failed"
    fi
    [ "${yield_dependency_identities[$i]}" = "$dependency_identity" ] || err "yield read-set consumed dependency changed during validation"
  done
fi

if [ "$err_count" -gt 0 ]; then
  printf 'validate-run-root: %d error(s)\n' "$err_count" >&2
  exit 1
fi
printf 'validate-run-root: ok\n'
