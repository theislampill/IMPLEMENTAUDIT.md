"""Fixed whole-sender entry (G132 v3); no caller-selected executable, path, environment or effect.

Outer, as the original nonroot sender UID and before any private read:
  /usr/bin/python3.12 -I -S -B <placement>/<packet>/carrier/sender_launch.py RUN_ID WORKFLOW_COMMIT ARTIFACT_ID ARCHIVE
checks the pinned sender tools and the exact placement, then re-executes this entry as the whole sender under
the descriptor-bound pinned bwrap with no_new_privs (sender_capture.launch). Inner (--inside; refused unless
the sandbox is verified): read the request artifact from the held stdin descriptor, run carrier.root_payload
and print only its public result and the retained file descriptors. No private body is printed.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path


def modules():
    spec = importlib.util.spec_from_file_location('carrier_loader', Path(__file__).absolute().parent / 'carrier_loader.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    return loader.load()


def main(argv):
    pub = modules()
    SC = pub.sender_capture
    if len(argv) == 6 and argv[1] == '--inside':
        facts = SC.enter_sender_sandbox(argv[2])
        print(json.dumps(dict(stage='SENDER_SANDBOX_VERIFIED', facts=facts), sort_keys=True), flush=True)
        pub.policy.need(re.fullmatch('[1-9][0-9]{0,19}', argv[5]) is not None, 'SENDER_LAUNCH_ARGUMENTS')
        archive = SC.read_request_archive()
        result = pub.carrier.root_payload(argv[3], argv[4], int(argv[5]), archive)
        print(json.dumps(dict(stage='SENDER_RESULT', result=result['result'],
                              files={k: pub.policy.descriptor(v) for k, v in result['files'].items()}),
                         sort_keys=True), flush=True)
        return 0 if result['files'] else 1
    if len(argv) == 5:
        return SC.launch(argv[1], argv[2], argv[3], argv[4])
    print('usage: sender_launch.py RUN_ID WORKFLOW_COMMIT ARTIFACT_ID ARCHIVE', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
