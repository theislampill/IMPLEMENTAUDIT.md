# Exact bounded source projection; source module is never imported.
FILE_LIMIT, TOTAL_LIMIT, ENTRY_LIMIT, DEPTH_LIMIT = 16*1024**2, 64*1024**2, 4096, 16

PUBLIC_LIMIT, REQUEST_LIMIT, DECISION_LIMIT = 24576, 8192, 8192

class Refusal(Exception):
    pass

def need(ok, code):
    if not ok:
        raise Refusal(code)

def parse(raw, maximum=FILE_LIMIT):
    need(type(raw) is bytes and len(raw) <= maximum, 'JSON_BYTE_BOUND')
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, 'DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Refusal('NONFINITE_JSON')))

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Refusal('CONTROL_REDIRECT_REFUSED')

def http_bytes(url, maximum, deadline):
    left = deadline-time.monotonic()
    need(left > 0, 'ROOT_HOLD_EXPIRED')
    request = urllib.request.Request(url, headers={'Accept':'application/json',
        'Cache-Control':'no-cache', 'User-Agent':'implementaudit-reviewed-g3-receiver/1'})
    opener = urllib.request.build_opener(NoRedirect())
    # urllib's socket timeout alone is not a whole-request deadline (including
    # DNS and a slow response). Temporarily shorten the existing main-thread
    # timer, preserving its remaining budget and handler on exit. No producer
    # owner or subprocess is live during this root-decision read.
    began = time.monotonic()
    old_handler = signal.getsignal(signal.SIGALRM)
    old_timer = signal.getitimer(signal.ITIMER_REAL)
    own_deadline = old_timer[0] == 0 or left < old_timer[0]
    if own_deadline:
        def expired(_signum, _frame):
            raise Refusal('ROOT_HOLD_EXPIRED')
        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, left)
    try:
        with opener.open(request, timeout=min(HTTP_SECONDS, left)) as response:
            need(response.status == 200 and response.geturl() == url, 'CONTROL_HTTP_RESPONSE')
            size = response.headers.get('Content-Length')
            if size is not None:
                need(re.fullmatch('[0-9]{1,8}', size) and int(size) <= maximum, 'CONTROL_HTTP_BOUND')
            pieces = []
            total = 0
            while total <= maximum:
                need(time.monotonic() < deadline, 'ROOT_HOLD_EXPIRED')
                part = response.read1(min(4096, maximum+1-total))
                if not part:
                    break
                pieces.append(part)
                total += len(part)
            raw = b''.join(pieces)
            need(len(raw) <= maximum and time.monotonic() < deadline, 'CONTROL_HTTP_BOUND')
            return raw
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise Refusal('CONTROL_HTTP_REFUSED') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Refusal('CONTROL_TRANSPORT_REFUSED') from None
    finally:
        if own_deadline:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old_handler)
            if old_timer[0]:
                signal.setitimer(signal.ITIMER_REAL, max(0.000001, old_timer[0]-(time.monotonic()-began)), old_timer[1])

def read_root_decision(request, request_sha, deadline, final=False, *, retained_bodies=None):
    ref_url = 'https://api.github.com/repos/'+REPOSITORY+'/git/ref/heads/'+CONTROL_BRANCH
    for _ in range(POLL_COUNT):
        need(time.monotonic() < deadline, 'ROOT_HOLD_EXPIRED')
        raw = http_bytes(ref_url, 8192, deadline)
        if raw is not None:
            ref = parse(raw, 8192)
            need(type(ref) is dict and ref.get('ref') == 'refs/heads/'+CONTROL_BRANCH
                 and type(ref.get('object')) is dict and ref['object'].get('type') == 'commit', 'CONTROL_REF_SHAPE')
            commit = ref['object'].get('sha')
            need(type(commit) is str and re.fullmatch('[0-9a-f]{40}', commit), 'CONTROL_COMMIT_SHAPE')
            path = FINAL_CONTROL_PATH if final else CONTROL_PATH
            decision_raw = http_bytes('https://raw.githubusercontent.com/'+REPOSITORY+'/'+commit+'/'+path,
                                      16384 if final else DECISION_LIMIT, deadline)
            if decision_raw is not None:
                validate = validate_final_decision if final else validate_decision
                decision = validate(decision_raw, request, request_sha, int(time.time()*1000),
                                    **({'retained_bodies': retained_bodies} if final else {}))
                need(time.monotonic() < deadline, 'ROOT_HOLD_EXPIRED')
                return decision_raw, decision, commit
        left = deadline-time.monotonic()
        need(left > 0, 'ROOT_HOLD_EXPIRED')
        time.sleep(min(POLL_SECONDS, left))
    raise Refusal('ROOT_HOLD_POLL_BOUND')
