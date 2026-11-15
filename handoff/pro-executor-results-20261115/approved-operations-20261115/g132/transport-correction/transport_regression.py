"""One inert regression for configured proxy routing and safe failure retention.

No real GET, DNS, receiver import, role, live session, or protected operation.
The baseline is read from Git; only isolated synthetic temporary files are used.
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import socket
import ssl
import subprocess
import tempfile
import types
from unittest import mock
import urllib.error
import urllib.request
import urllib.response

WORK = Path('/workspace/scratch/7fbb79f74aa4/recovery/g132-transport-correction')
BASE = '198a0495e486a5cc79534aa42fa984516ad16d67'
REL = 'handoff/fable-local-support-20261115/dg16-g132-owner-local/public-operator/public-receiver-02/author/resolve_artifact.py'
OUT = Path(__file__).with_name('TRANSPORT_REGRESSION_RESULT.json')
URL = 'https://sdmntprregression.oaiusercontent.com/inert?token=DIAGNOSTIC_SECRET_SENTINEL'
SECRET = 'DIAGNOSTIC_SECRET_SENTINEL'
PAYLOAD = b'inert-body'


def desc(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def load(raw, tag):
    module = types.ModuleType(tag)
    module.__file__ = str(WORK / REL)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def exercise(module):
    requests = []
    watchdogs = []

    def https_open(handler, request):
        requests.append((request.host, request._tunnel_host, request.full_url,
                         request.get_method(), request.timeout))
        response = urllib.response.addinfourl(io.BytesIO(PAYLOAD),
            {'Content-Length': str(len(PAYLOAD))}, URL, 200)
        response.msg = 'OK'
        return response

    def watchdog(seconds):
        watchdogs.append(seconds)
        return contextlib.nullcontext()

    with mock.patch.object(urllib.request, 'getproxies',
            return_value={'https': 'http://proxy.invalid:8443'}), \
         mock.patch.object(urllib.request, 'proxy_bypass', return_value=False), \
         mock.patch.object(urllib.request.HTTPSHandler, 'https_open', https_open), \
         mock.patch.object(module, 'request_watchdog', watchdog):
        body = module.fetch_once(URL, 131072, 45)
    assert body == PAYLOAD and len(requests) == 1 and watchdogs == [45]
    assert requests[0][2:] == (URL, 'GET', 45)
    proxy_used = requests[0][:2] == ('proxy.invalid:8443',
                                    'sdmntprregression.oaiusercontent.com')

    R = types.SimpleNamespace(SOURCE_SHA='0'*64, AUTH='INERT_CONTROL_ONLY',
        PHASES={'tools': ('fixture', (), 131072)}, desc=desc,
        encode=lambda value: (json.dumps(value, sort_keys=True)+'\n').encode(),
        read=lambda path, maximum: path.read_bytes())
    attempts = []

    def failing_transport(url, maximum, seconds):
        attempts.append((url, maximum, seconds))
        raise urllib.error.URLError(socket.gaierror(-3, SECRET + URL))

    with tempfile.TemporaryDirectory(prefix='g132-inert-transport-') as directory:
        root = Path(directory)

        def write(name, raw):
            with (root/name).open('xb') as stream:
                stream.write(raw)

        session = types.SimpleNamespace(path=root,
            plan={'phase': 'tools', 'context': {'fixture': 'INERT_ONLY'}},
            s=types.SimpleNamespace(binding={'limits': {'command_seconds': 45}}),
            artifact=lambda: {'size_in_bytes': len(PAYLOAD),
                              'digest': 'sha256:'+desc(PAYLOAD)['sha256']},
            bound=lambda count, files: None, write=write,
            body=lambda raw: write('ARTIFACT.zip', raw))
        reference = {'fixture': 'INERT_ONLY', 'reference': desc(URL.encode())}
        clock = iter([1.0, 1.0, 1.005])
        with mock.patch.object(module, 'exact_reference', return_value=(URL, reference)):
            outcome = module.resolve(R, session, b'INERT_DOWNLOAD_RESULT',
                transport=failing_transport, clock=lambda: next(clock))
            try:
                module.resolve(R, session, b'INERT_DOWNLOAD_RESULT',
                    transport=failing_transport)
            except module.Refusal as error:
                assert error.args == ('NO_UNCERTAIN_BODY_GET_REPLAY',)
            else:
                raise AssertionError('Failed intent allowed a second attempt')
        assert len(attempts) == 1 and attempts[0][1:] == (131072, 45)
        assert outcome['status'] == 'REFUSED_OR_UNCERTAIN'
        assert outcome['code'] == 'BODY_GET_REFUSED_OR_UNCERTAIN'
        assert outcome['complete_body_observed'] is False
        assert outcome['retained_archive'] is None and not (root/'ARTIFACT.zip').exists()
        assert outcome['automatic_retry'] is False and outcome['cleanup_or_no_effect_inferred'] is False
        retained = (root/'BODY_GET_OUTCOME.json').read_bytes()
        assert retained == R.encode(outcome)
        assert SECRET.encode() not in retained and URL.encode() not in retained
        diagnostic_retained = outcome.get('error_class_code') == 'DNS_RESOLUTION_ERROR'

    codes_safe = None
    if hasattr(module, 'failure_class'):
        cases = [
            (urllib.error.HTTPError(URL, 502, SECRET, {}, None), 'HTTP_ERROR'),
            (urllib.error.URLError(SECRET), 'URL_ERROR'),
            (ssl.SSLError(SECRET), 'TLS_ERROR'),
            (TimeoutError(SECRET), 'TIMEOUT'),
            (module.WatchdogExpired(SECRET), 'WATCHDOG_EXPIRED'),
            (type(SECRET, (Exception,), {})(SECRET), 'OTHER_EXCEPTION'),
        ]
        assert all(module.failure_class(error) == code for error, code in cases)
        codes_safe = True
    return {'configured_https_proxy_used': proxy_used,
            'bounded_dns_class_retained': diagnostic_retained,
            'one_get_and_45_second_argument': True,
            'failure_remains_unqualified_and_no_replay': True,
            'no_url_or_exception_message_retained': True,
            'fixed_classification_vocabulary': codes_safe}


def main():
    old = subprocess.check_output(['git', 'show', BASE+':'+REL], cwd=WORK)
    new = (WORK/REL).read_bytes()
    with mock.patch.object(socket, 'create_connection', side_effect=AssertionError('NETWORK_FORBIDDEN')), \
         mock.patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS_FORBIDDEN')):
        before = exercise(load(old, 'baseline_resolver'))
        after = exercise(load(new, 'candidate_resolver'))
    assert before['configured_https_proxy_used'] is False
    assert before['bounded_dns_class_retained'] is False
    assert all(after.values())
    result = {'scope': 'ONE_INERT_REGRESSION; NO REAL NETWORK OR OPERATION',
              'baseline': {'source': desc(old), 'checks': before},
              'candidate': {'source': desc(new), 'checks': after},
              'actual_failure_exception_inferred': False,
              'old_source_fails_targeted_properties': True,
              'candidate_passes': True}
    OUT.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
