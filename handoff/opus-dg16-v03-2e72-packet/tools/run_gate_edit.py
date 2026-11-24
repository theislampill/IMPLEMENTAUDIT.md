"""Structural V03-only edit of run.py: drop the native-prerequisite dependency (Root decision 2).
Pins are rebound separately by rebind_chain.py."""
import sys
path = sys.argv[1]
s = open(path, 'rb').read().decode()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (old[:80], n); s = s.replace(old, new)
def cut(start, end):
    """Delete from the start anchor up to (not including) the end anchor."""
    global s
    i = s.index(start); j = s.index(end, i); assert s.count(start) == 1
    s = s[:i] + s[j:]
# Native/prerequisite/current-host pins (their files are not in the V03 packet).
for name in ('PREREQUISITE_SHA', 'NATIVE_CLOSURE_SHA', 'NATIVE_EVIDENCE_IO_SHA', 'NATIVE_PROFILE_SHA', 'NATIVE_ADMISSION_SHA',
             'NATIVE_RECEIVER_SHA', 'CURRENT_HOST_SHA', 'CURRENT_HOST_REQUEST_SHA', 'NATIVE_INTEGRATION_SHA'):
    i = s.index('\n' + name + ' = '); j = s.index('\n', i + 1); s = s[:i] + s[j:]
rep("         'resume','verify','require','native-bank','native-receive','pair','receive','prepare-review','hold')",
    "         'resume','verify','require','pair','receive','prepare-review','hold')")
# Native module loader and native adoption reader.
cut('def load_native(u):', 'def actual_policy_adoption(u):')
# Earned-prerequisite and unchanged-bank closure readers.
cut('def prerequisite_host(host,u):', 'def setup_sudo(u):')
rep("    need(probe.get('native_prerequisite')==native_projection(state,output,u,True),'EMISSION_NATIVE_PROJECTION_CHANGED')\n", "")
# Nine-case native bank program, its result validation and native state/projection helpers.
cut('TESTS = (\n', 'PAIR_RECEIVING_RESERVE = RECEIVE_SECONDS + HOLD_SECONDS + FINAL_SECONDS')
rep("KNOWN_CODES = (", "KNOWN_CODES_REMOVED = (")  # placeholder, removed just below
i = s.index("KNOWN_CODES_REMOVED = ("); j = s.index("\n", i); s = s[:i] + s[j + 1:]
i = s.index("EXCEPTIONS = ("); j = s.index("\n", i); s = s[:i] + s[j + 1:]
cut('def new_native_state():', 'def observe_host(state,host,u):')
rep("""    need(prior is None or prior==host,'HOST_TOOLCHAIN_CHANGED')
    requirement=native_requirement(host,u,Path(state['source_path']))
    native=state['native']
    if native['requirement'] is None:
        native['requirement']=requirement
        native['status']='CURRENT_CHANGED_PREDICATES_REQUIRED' if requirement['host_exact_match'] else 'CHANGED_HOST_APPLICABILITY_UNRECEIVED'
    else:need(native['requirement']==requirement,'NATIVE_REQUIREMENT_CHANGED')
""", """    need(prior is None or prior==host,'HOST_TOOLCHAIN_CHANGED')
""")
cut('def native_commands_summary(state):', 'def require_native_for_pair(state,output,u):')
rep("""def require_native_for_pair(state,output,u):
    load_native(u).verify_current(state,Path(state['source_path']),output)
    value=native_projection(state,output,u,True)
    need(value['qualified_for_pair_at_receiving'] and state['docs']['CLEANUP.json']['all_step_children_reaped'],
         'CURRENT_NATIVE_PREREQUISITE_NOT_RECEIVED')
""", """def require_native_for_pair(state,output,u):
    # Root decision (V03 on 2e72): the native prerequisite is outside this route. Only the
    # reaped-children and receiving-time checks of the original gate remain.
    need(state['docs']['CLEANUP.json']['all_step_children_reaped'],
         'PAIR_PRECONDITION_STEP_CHILDREN_NOT_REAPED')
""")
cut('def native_operation(step,state,source,output,tools,u,command,current):', 'def fresh_state(context,source,output):')
rep("       'bound_host':None,'native_admission':None,'native':new_native_state(),'native_commands':[],\n",
    "       'bound_host':None,\n")
rep("""    native=load_native(u)
    host['credentials']=native.P.credentials()
    native.P.validate_host(host)
""", "")
rep("""    # The unchanged failure path can replace an unreceivable native projection by None.
    fallback=dict(docs['PROBE.json'],native_prerequisite=None)
    base['PROBE.json']=max(base['PROBE.json'],len(u.public_codec('PROBE.json',fallback)))
""", "")
rep("""        state['native_admission']=actual_native_adoption(u)
        docs['PROBE.json']['native_admission']=state['native_admission']
""", "")
rep("""    elif step in ('native-bank','native-receive'):
        native_operation(step,state,source,output,tools,u,command,current)
""", "")
rep("    commands=state['native_commands'] if mode in ('native-bank','native-receive') else docs['HOST.json']['commands']\n",
    "    commands=docs['HOST.json']['commands']\n")
rep("""        failed_native_receiving = (mode=='native-receive' and state['native']['started'] and
            state['native']['capture_custody_accepted'] and state['native']['result'] is not None and
            state['docs']['CLEANUP.json']['all_step_children_reaped'])
        failed_receiving = failed_receiving or failed_native_receiving
""", "")
rep("        load_native(u).admit_host(state,host,source,output,mode)\n", "")
rep("            actual_policy_adoption(u)\n            actual_native_adoption(u)\n", "            actual_policy_adoption(u)\n")
rep("mode in ('preflight','native-bank','native-receive','pair','receive','finalize')", "mode in ('preflight','pair','receive','finalize')")
rep("""            load_native(u).verify_current(state,source,output)
            need(native_projection(state,output,u,True)['qualified_for_pair_at_receiving'],'NATIVE_RECEIVING_MISSING')
            state['native']['closing_currentness_verified_before_teardown']=True
""", "")
rep("            if mode in ('native-bank','pair'):check_source_git(command,tools,source,True)\n",
    "            if mode=='pair':check_source_git(command,tools,source,True)\n")
rep("""        try:
            docs['PROBE.json']['native_prerequisite']=native_projection(state,output,u)
        except BaseException as exc:
            docs['PROBE.json']['native_prerequisite']=None
            stage_success=False;record_failure(state,mode+'-native-projection',exc)
""", "")
open(path, 'wb').write(s.encode())
