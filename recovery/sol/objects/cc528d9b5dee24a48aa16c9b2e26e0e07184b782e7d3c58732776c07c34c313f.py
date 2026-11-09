"""Deterministic external-only G1HOST-F01 rendering. No runtime effects."""
from pathlib import Path
PHASES = {'bootstrap_entry.py': 'BOOTSTRAP', 'host_tool_observe_entry.py': 'HOST_TOOL_OBSERVATION', 'host_tool_adopt_entry.py': 'HOST_TOOL_ADOPTION', 'host_request_entry.py': 'RECIPIENT_REQUEST', 'host_receive_entry.py': 'PRIVATE_INPUT_RECEIVE', 'core_prepare_entry.py': 'CORE_PREPARE', 'public_export.py': 'PUBLIC_EXPORT'}
def render(name, raw):
    phase=PHASES[name];text=raw.decode('utf8')
    marker="if __name__=='__main__':"
    assert text.count(marker)==1
    prefix=text[:text.index(marker)]
    if name=='public_export.py':
        old="need(len(raw)<=limit,'EXPORT_STREAM_BOUND');v=parse(raw)"
        assert prefix.count(old)==1
        prefix=prefix.replace(old,old+";precore_stream(phase,v)")
        terminal="""if __name__=='__main__':
 try:raise SystemExit(main())
 except PrecoreRefusal as exc:
  try:precore_emit(precore_validate(exc.record,exc.record.get('phase')))
  except Exception:precore_emit(precore_record('PUBLIC_EXPORT','UNKNOWN_EXCEPTION'))
  raise SystemExit(1)
 except Exception as exc:
  precore_emit(precore_exception('PUBLIC_EXPORT',exc));raise SystemExit(1)
"""
    else:
        terminal="""if __name__=='__main__':
 try:code=main()
 except BaseException as exc:
  precore_emit(precore_exception(PHASE_LITERAL,exc));code=1
 raise SystemExit(code)
""".replace('PHASE_LITERAL',repr(phase))
    projection=Path(__file__).with_name('precore_projection.py').read_text()
    return (prefix+'\n# Exact pure closed refusal projection; external whole-tree bound.\n'+projection+'\n'+terminal).encode()
