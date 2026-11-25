"""Root-dispatcher stand-in, OUTSIDE the sender sandbox (a separate process, same account).

Plays the external root dispatcher of ROOT_SUPPORTED_GITHUB_FETCH_FILE_BROKER_V1: for each of the 18 fixed
broker requests it reserves the dispatch and publishes a tool result through the unchanged tool_broker.Store
API. The tool results are SYNTHETIC (no GitHub or network contact, no token); in production they are the
supported GitHub tool's actual results. Usage: python3.12 -I -B qual_dispatcher.py PACKET WORK
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).absolute().parent
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location('qual_common', str(HERE / 'qual_common.py'))
QC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(QC)
packet, work = Path(sys.argv[1]), Path(sys.argv[2])
cfg = json.loads((packet / 'qual' / 'config.json').read_bytes())
pub = QC.carrier(packet)
B, P, F = pub.tool_broker, pub.policy, pub.files
binding = QC.binding_for(pub, packet, cfg)
archive = (work / 'request.zip').read_bytes()
workflow = (work / 'workflow.yml').read_bytes()
directory = packet.parent / ('dg16-private-sender-' + cfg['context']['run_id'] + '-a1')
log = dict(served=[], start_wait_s=None)
import socket  # noqa: E402
listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)  # host-netns abstract socket the sandbox must not reach
listener.bind('\0' + cfg['abstract_probe'])
listener.listen(4)
t0 = time.monotonic()


def wait(path, limit):
    end = time.monotonic() + limit
    while not path.exists():
        if time.monotonic() > end:
            raise SystemExit('DISPATCHER_WAIT_TIMEOUT ' + path.name)
        time.sleep(0.05)


wait(directory / 'BROKER_START.json', 180)
log['start_wait_s'] = round(time.monotonic() - t0, 3)
start = P.parse(F.read_file(directory / 'BROKER_START.json', 65536, private=True)[0], 65536)
store = B.Store(directory, binding, cfg['operation'], start['deadline_monotonic'])
for i in range(18):
    wait(directory / B.name(i, 'REQUEST_READY'), 120)
    intent = store.reserve_dispatch(i)
    kind = B.KINDS[i % 6]
    raw = QC.tool_result(intent['arguments']['url'], QC.provider_body(kind, cfg, archive, workflow))
    reply = store.publish_response(i, intent['intent_sha256'], raw, 'qual-dispatch-%02d' % i)
    log['served'].append(dict(ordinal=i, phase=B.PHASES[i // 6], kind=kind, url=intent['arguments']['url'],
                              tool_result=P.descriptor(raw), status=reply['reply']['status']))
store.close_fd()
listener.close()
log['elapsed_s'] = round(time.monotonic() - t0, 3)
(work / 'dispatcher.json').write_text(json.dumps(log, indent=1, sort_keys=True))
print('DISPATCHER_DONE', len(log['served']))
