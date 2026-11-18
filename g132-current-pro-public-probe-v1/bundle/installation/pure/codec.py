# Exact bounded source projection; source module is never imported.
MAX_ENTRIES = 256

MAX_FILE_BYTES = 4 * 1024**2

MAX_TOTAL_BYTES = 16 * 1024**2

def need(value, code):
    if not value:
        raise ValueError(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')

def check_index(index):
    need(type(index) is dict and 1 <= len(index) <= MAX_ENTRIES, 'INPUT_INDEX_POPULATION')
    total = 0
    names = set(index)
    for name, row in index.items():
        need(type(name) is str and len(name) <= 512, 'INPUT_NAME_BOUND')
        parts = name.split('/')
        need(1 <= len(parts) <= 6 and all(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', part)
             and part not in ('.', '..') for part in parts), 'INPUT_NAME_SCOPE')
        need(not any('/'.join(parts[:i]) in names for i in range(1, len(parts))), 'INPUT_FILE_DIRECTORY_ALIAS')
        need(type(row) is dict and set(row) == {'bytes', 'sha256'}, 'INPUT_DESCRIPTOR_FIELDS')
        need(type(row['bytes']) is int and 0 <= row['bytes'] <= MAX_FILE_BYTES
             and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'INPUT_DESCRIPTOR_VALUE')
        total += row['bytes']
    need(total <= MAX_TOTAL_BYTES, 'INPUT_TOTAL_BOUND')
    return sha(encode(index))
