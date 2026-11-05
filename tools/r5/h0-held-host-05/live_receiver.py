#!/usr/bin/env python3
"""Read the actual selected occurrences before the owned native process exits.

This ordinary mechanical receipt is not an audit child RETURN, governor JOIN,
formal acceptance or authentic provider-usage observation.
"""
import argparse
import ast
import contextlib
import importlib.util
import os
from pathlib import Path
import re
import select
import sys

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('h0_receive_io',HERE/'host_io.py');H=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(H)
sys.dont_write_bytecode=True

def live(capture,selected):
 pid=capture['pid'];H.need(type(pid) is int and pid>0,'ACTUAL_PROCESS_PID')
 fd=os.pidfd_open(pid)
 try:
  H.need(not select.select([fd],[],[],0)[0],'ACTUAL_PROCESS_ENDED')
  info=dict(line.split(':',1) for line in Path('/proc/self/fdinfo',str(fd)).read_text().splitlines() if ':' in line)
  host=int(info['Pid']);H.need(host==capture['proc_host_pid'],'ACTUAL_PROCESS_NAMESPACE')
  base=Path('/proc')/str(host);status=dict(line.split(':',1) for line in (base/'status').read_text().splitlines() if ':' in line)
  H.need(int(status['PPid'])==os.getppid(),'ACTUAL_PROCESS_SIBLING_CUSTODY')
  H.need((base/'stat').read_text().rsplit(')',1)[1].split()[19]==capture['proc_start_ticks'],'ACTUAL_PROCESS_BIRTH')
  H.need((base/'exe').resolve(strict=True)==Path(selected['native_executable']['path']) and (base/'cwd').resolve(strict=True)==Path(selected['cwd']),'ACTUAL_PROCESS_IMAGE_CWD')
  H.need((base/'cmdline').read_bytes().split(b'\0')[:-1]==[x.encode() for x in capture['argv']],'ACTUAL_PROCESS_ARGV')
  environment=dict(row.split(b'=',1) for row in (base/'environ').read_bytes().split(b'\0') if b'=' in row)
  H.need(environment.get(b'HOME')==environment.get(b'CODEX_HOME')==selected['codex_home'].encode(),'ACTUAL_PROCESS_HOME')
  H.need(not select.select([fd],[],[],0)[0],'ACTUAL_PROCESS_ENDED')
  return {'pidfd_live':True,'same_owned_driver_parent':True,'same_birth_image_argv_cwd_home':True}
 finally:os.close(fd)

def main():
 p=argparse.ArgumentParser();p.add_argument('--work',required=True,type=Path);p.add_argument('--go-sha256',required=True);a=p.parse_args();work=a.work
 driver=H.load(HERE/'native_driver.py','h0_receiving_gate');request,manifest,state=driver.prepared(work);driver.grant(work,request,a.go_sha256)
 root=work/'private';repo=root/'subject';scripts=repo/'skills/implementaudit/scripts';evidence=root/'evidence'
 output=evidence/'MECHANICAL_RECEIVING.json';H.need(not output.exists(),'NO_REPEAT_MECHANICAL_RECEIVING')
 selected_raw=H.read(root/'SOURCE_SELECTION.json');selected=H.parse(selected_raw);capture=H.parse(H.read(root/'LIVE_CAPTURE.json'))
 selection_pin=H.source_pin(root/'SOURCE_SELECTION.json');selected_path=scripts/'compaction-source-owner-codex-app.py'
 runtime_custody=H.parse(H.read(evidence/'RUNTIME_CUSTODY.json'))
 H.need(set(runtime_custody)=={str(repo/item['destination']) for item in manifest['members'] if 'destination' in item},'RUNTIME_CUSTODY_POPULATION')
 # Reconcile the complete materialized runtime against the held public source.
 # Only the declared source selection literal may differ from its template.
 for item in manifest['members']:
  if 'destination' not in item:continue
  path=repo/item['destination'];pin,physical,raw=H.pin(path,4*1024*1024,True)
  H.need(runtime_custody[str(path)]==physical,'RUNTIME_PHYSICAL_IDENTITY_CHANGED')
  if path==selected_path:
   nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='MECHANICAL_SELECTION_PIN']
   H.need(len(nodes)==1 and ast.literal_eval(nodes[0].value)==selection_pin,'EXACT_SELECTION_LITERAL')
   node=nodes[0].value;lines=raw.splitlines(True);start=sum(map(len,lines[:node.lineno-1]))+node.col_offset;end=sum(map(len,lines[:node.end_lineno-1]))+node.end_col_offset;raw=raw[:start]+b'None'+raw[end:]
  H.need(len(raw)==item['bytes'] and H.sha(raw)==item['sha256'] and pin['mode']==item['mode'],'MATERIALIZED_SOURCE_CHANGED')
 H.need(H.source_pin(selected['native_executable']['path'])==selected['native_executable'] and selected['native_executable']['sha256']==H.BINARY_SHA,'OWNED_NATIVE_BINARY_CHANGED')
 live_before=live(capture,selected);pending=H.load(scripts/'compaction-audit-pending.py','h0_receiving_pending');source=H.load(selected_path,'h0_receiving_source')
 store=Path(selected['pending_owner']['store']);session=selected['root_thread_id'];owner=selected['pending_owner']['owner_id']
 old=pending.load(store,session);mechanical=H.parse(H.read(evidence/'MECHANICAL_RESULT.json'))
 H.need(mechanical['status']=='MECHANICAL_PREDICATE_OBSERVED_PENDING_ROOT_RECEIVING' and mechanical['public_return'] is None and mechanical['public_join'] is None and mechanical['original_acceptance'] is False,'MECHANICAL_PRODUCER_SCOPE')
 child=mechanical['export']['actual_child_identity']['thread_id'];H.need(set(old['assignments'])=={child},'EXACT_ASSIGNMENT_POPULATION');assignment=old['assignments'][child]
 H.need(assignment['return'] is None and assignment['join'] is None and assignment['code']==pending.nonprotected_code_identity(),'ASSIGNMENT_AUTHORITY_OR_CODE_CHANGED')
 current_id=mechanical['observation_c'];prior_id=mechanical['observation_p'];H.need(set(assignment['prepared'])=={current_id,prior_id},'EXACT_TWO_OBSERVATIONS')
 current=assignment['prepared'][current_id];prior=assignment['prepared'][prior_id]
 H.need(current['observation']['revision']>prior['observation']['revision'],'STRICT_PRIOR_REVISION')
 with contextlib.chdir(repo):
  runtime=source._np_runtime(pending.OBSERVATION,assignment['code']);opening_before=source._np_episode(runtime)
  received=pending.OBSERVATION.export_selected_occurrences(assignment['observation_source'],current,current['exchange'],current['bind_request'],store,session,owner,prior_context=pending.prior_history_context(assignment,current_id))
  opening_after=source._np_episode(runtime)
 H.need(received==mechanical['export'],'EXISTING_READER_EXPORT_DISAGREES')
 expected=sorted([('CURRENT','ORIGINAL',semantic,'COMPLETED') for semantic in ('LOAD','EXCHANGE','BIND')]+[('PRIOR','ORIGINAL',semantic,'COMPLETED') for semantic in ('LOAD','EXCHANGE','BIND')]+[('PRIOR','RETRY','BIND','COMPLETED')])
 observed=sorted((r['population'],r['attempt_class'],r['semantic'],r['completion']) for r in received['occurrences'])
 H.need(observed==expected,'SEVEN_OCCURRENCE_POPULATION')
 H.need(opening_before==opening_after and opening_before['canonical_route_currentness']=='VALIDATED_AT_READ' and opening_before['authority_ceiling']=='NONE','CANONICAL_OPEN_CHANGED')
 H.need(pending.load(store,session)==old and len(old['observations'])==1 and all(r['consumed_version']==0 for r in old['observations'].values()),'PENDING_STATE_CHANGED_OR_CONSUMED')
 live_after=live(capture,selected);H.need(live_after==live_before,'NATIVE_CUSTODY_CHANGED')
 H.write(evidence/'RECEIVED_SELECTED_OCCURRENCES.json',received)
 record={'schema':'r5.h0-existing-reader-receiving.v1','status':'EXISTING_READER_SEVEN_OCCURRENCES_RECEIVED','authority':'NONE','source_commit':request['source_commit'],'source_tree':H.SOURCE_TREE,'go_sha256':a.go_sha256,'mechanical_result_sha256':H.sha(H.read(evidence/'MECHANICAL_RESULT.json')),'received_export_sha256':H.sha(H.encode(received)),'selected_occurrence_count':7,'classes':[list(r) for r in observed],'strict_prior_revision':True,'original_and_retry_distinct':True,'reader_agrees_with_producer':True,'canonical_open_reread_unchanged':True,'pending_unconsumed':True,'same_live_process_before_and_after':live_after,'public_return':None,'public_join':None,'formal_governor_decision':False,'independent_cognition':False,'authentic_OR':False,'original_acceptance':False,'old_archive_or_pending_used':False}
 H.write(output,record);print('{"status":"EXISTING_READER_SEVEN_OCCURRENCES_RECEIVED","authority":"NONE"}')
if __name__=='__main__':
 try:main()
 except BaseException:print('{"status":"H0_EXISTING_READER_REFUSED","authority":"NONE"}');raise SystemExit(1)
