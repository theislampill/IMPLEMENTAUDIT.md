import hashlib
import json

def report_key(jobs, profile_name):
    value = {'jobs': jobs, 'profile': profile_name}
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def read_cached(base, key):
    path = base / 'cache' / (key + '.txt')
    return path.read_text() if path.is_file() else None

def store_cached(base, key, value):
    path = base / 'cache' / (key + '.txt')
    path.write_text(value)
