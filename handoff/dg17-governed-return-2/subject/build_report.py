import json
from pathlib import Path
from projection import render_report
from settings import selected_profile
from storage import report_key, read_cached, store_cached

BASE = Path(__file__).resolve().parent

def build(base=BASE):
    jobs = json.loads((base / 'inputs' / 'jobs.json').read_text())
    profile = selected_profile(base)
    key = report_key(jobs, profile['name'])
    value = read_cached(base, key)
    reused = value is not None
    if value is None:
        value = render_report(jobs, profile)
        store_cached(base, key, value)
    (base / 'output' / 'report.txt').write_text(value)
    return {'status': 'built', 'reused': reused, 'key': key}

if __name__ == '__main__':
    print(json.dumps(build(), sort_keys=True))
