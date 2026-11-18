# Exact bounded source projection; source module is never imported.
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'

SOURCE_COMMIT = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'

SOURCE_TREE = 'ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'

SCOPE = 'CORE_G1_Q06_NATURAL_L04_SEPARATE'

MAX_REQUEST = 8192

MAX_CERTIFICATE = 8192

MAX_ARTIFACT = 65536

MAX_METADATA = 1024 * 1024

MAX_ACQUISITION_SECONDS = 600

CONTEXT_KEYS = ('repository','branch','workflow_commit','workflow_path','run_id','run_attempt','job_name')

need, sha, encode = C.need, C.sha, C.encode

def descriptor(raw): return dict(bytes=len(raw),sha256=sha(raw))

def parse(raw, maximum, canonical=True):
    need(type(raw) is bytes and 0 < len(raw) <= maximum,'CARRIER_JSON_BOUND')
    def pairs(rows):
        result={}
        for key,value in rows:
            need(key not in result,'CARRIER_DUPLICATE_KEY');result[key]=value
        return result
    try:
        value=json.loads(raw,object_pairs_hook=pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError('CARRIER_NONFINITE_JSON')))
    except (UnicodeError,json.JSONDecodeError,RecursionError) as exc:
        raise ValueError('CARRIER_JSON_REFUSED') from exc
    if canonical:need(encode(value)==raw,'CARRIER_NONCANONICAL_JSON')
    return value

def exact(value, keys, code='CARRIER_FIELDS'):
    need(type(value) is dict and set(value)==set(keys),code)

def digest(value): need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value),'CARRIER_DIGEST')

def integer(value, low, high, code='CARRIER_INTEGER'):
    need(type(value) is int and low<=value<=high,code)

def context(value):
    exact(value,CONTEXT_KEYS)
    need(value['repository']==REPOSITORY and value['run_attempt']==1 and type(value['run_attempt']) is int,'CARRIER_CONTEXT')
    need(re.fullmatch('[1-9][0-9]{0,19}',value['run_id']) and re.fullmatch('[0-9a-f]{40}',value['workflow_commit']),'CARRIER_RUN')
    need(re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',value['branch'])
         and '..' not in value['branch'] and '//' not in value['branch'],'CARRIER_BRANCH')
    need(re.fullmatch(r'\.github/workflows/[A-Za-z0-9][A-Za-z0-9_-]{0,100}\.ya?ml',value['workflow_path'])
         and re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,79}',value['job_name']),'CARRIER_WORKFLOW')
    return value

def make_request(ctx,index,cert,nonce,issued_ms,expires_ms):
    context(ctx);digest(nonce)
    need(type(cert) is bytes and 0<len(cert)<=MAX_CERTIFICATE,'RECIPIENT_CERTIFICATE_BOUND')
    integer(issued_ms,0,10**16);integer(expires_ms,issued_ms+1,issued_ms+MAX_ACQUISITION_SECONDS*1000)
    value=dict(schema='dg16.core-private-recipient-request.v1',authority='NONE',component_scope=SCOPE,
      source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,**ctx,input_index_sha256=C.check_index(index),
      input_count=len(index),input_bytes=sum(row['bytes'] for row in index.values()),recipient_sha256=sha(cert),
      nonce=nonce,issued_unix_ms=issued_ms,expires_unix_ms=expires_ms,automatic_retry=False,original_awards=[])
    raw=encode(value);need(len(raw)<=MAX_REQUEST,'REQUEST_BOUND');return raw

def validate_request(raw,cert,ctx,index,now_ms):
    value=parse(raw,MAX_REQUEST)
    expected=make_request(ctx,index,cert,value.get('nonce'),value.get('issued_unix_ms'),value.get('expires_unix_ms'))
    need(raw==expected,'REQUEST_EXACT_CONTEXT')
    integer(now_ms,value['issued_unix_ms'],value['expires_unix_ms'],'REQUEST_EXPIRED_OR_FUTURE')
    return value
