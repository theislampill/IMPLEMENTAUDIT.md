from pathlib import Path
import difflib

BASE = Path(__file__).resolve().parent

def main():
    expected = (BASE / 'expected_report.txt').read_text()
    actual = (BASE / 'output' / 'report.txt').read_text()
    if actual != expected:
        print('report mismatch')
        print(''.join(difflib.unified_diff(actual.splitlines(True), expected.splitlines(True), fromfile='actual', tofile='required')), end='')
        return 1
    print('report matches current requirement')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
