"""One read-only resource observation; never enter any provisioning path."""
import hashlib
import json
import os
from pathlib import Path
import signal
import sys

SOURCE_SHA256 = '577a1de367bfb7bdf04621390b91f65bb7c977f3032f70c17048039a33e3d661'
SOURCE_BYTES = 72161
TARGET_SHA256 = '85abad38f2f47864c38dc9748a7b75ed6003df6299d8429cee9b49c88ee09eab'


class TargetComplete(BaseException):
    """Stop before reading any profile after the one authorized target."""


class DiagnosticBoundary(BaseException):
    """An observer interruption is not an original owner refusal."""


def load_owner(root):
    path = Path(root) / 'scripts/qualify-work-graph-c5-setup.py'
    with path.open('rb') as stream:
        raw = stream.read(SOURCE_BYTES + 1)
    if len(raw) != SOURCE_BYTES or hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('accepted DG21 source identity differs; no diagnostic')
    owner = {'__name__': 'dg21_read_only_accepted_owner', '__file__': str(path)}
    exec(compile(raw, str(path), 'exec'), owner)
    return owner


def observe(owner, inventory):
    """Trace existing locals after the original read; never replace its result."""
    reader = owner['_bwrap_read'].__code__
    exporter = owner['_bwrap_selected_export'].__code__
    resolver = owner['_bwrap_resolve_opaque'].__code__
    result = dict(selected=None, reads=[], refusal=None, exit_code=2,
                  status='TARGET_NOT_REACHED')
    if sys.gettrace() is not None:
        raise ValueError('existing Python trace refuses diagnostic replacement')

    def trace(frame, event, arg):
        code = frame.f_code
        if code not in (reader, exporter, resolver):
            return None
        caller = frame.f_back
        if code is exporter and event == 'call' and caller.f_code is resolver:
            local = caller.f_locals
            if local['name'] == 'tcpdump':
                total = local['total']
                remaining = 4194304 - total
                result['selected'] = dict(name=local['name'], record=dict(local['row']),
                    aggregate_completed_bytes=total, remaining_aggregate_bytes=remaining,
                    effective_export_maximum=frame.f_locals['maximum'],
                    limiting_export_bound=('PER_EXPORT' if remaining > 65536 else
                        'BOTH_EQUAL' if remaining == 65536 else 'REMAINING_AGGREGATE'))
        # The pinned reader's bound check is exactly four lines after its def.
        # Its raw local is the value just returned by the unchanged os.read.
        if (code is reader and event == 'line' and frame.f_lineno == reader.co_firstlineno + 4
                and caller.f_code is exporter and caller.f_back.f_code is resolver
                and caller.f_back.f_locals['name'] == 'tcpdump'):
            local = frame.f_locals
            paths = caller.f_locals['paths']
            roles = [name for name, path in paths.items() if path == local['path']]
            if len(roles) != 1 or len(result['reads']) >= 6:
                raise DiagnosticBoundary('unexpected pinned reader trace shape')
            role = roles[0]
            maximum, count = local['maximum'], len(local['raw'])
            result['reads'].append(dict(role=role,
                occurrence=1 + sum(row['role'] == role for row in result['reads']),
                maximum=maximum, requested=maximum + 1, returned=count, overflow=count > maximum))
        if (code is resolver and event == 'line'
                and 'tcpdump' in frame.f_locals.get('proofs', {})):
            raise TargetComplete()
        return trace

    try:
        sys.settrace(trace)
        owner['_bwrap_resolve_opaque'](inventory)
    except TargetComplete:
        result['status'] = 'TARGET_PROOF_COMPLETED_DIAGNOSTIC_STOP'
    except (OSError, ValueError, UnicodeError) as exc:
        result.update(status='ORIGINAL_RESOLVER_REFUSAL', refusal=str(exc), exit_code=1)
    finally:
        sys.settrace(None)
    return result


def snapshot(owner):
    """Metadata only: no raw export, parser, receipt contents or policy effect."""
    inventory = owner['hosted_bwrap_policy_inventory']()
    try:
        os.lstat('/run/' + owner['HOSTED_BWRAP_RECEIPT'])
    except FileNotFoundError:
        receipt = 'ABSENT'
    else:
        receipt = 'PRESENT_RETAINED'
    owned = sorted(set(inventory) & set(owner['HOSTED_BWRAP_NAMES']))
    record = dict(inventory_count=len(inventory),
        inventory_sha256=hashlib.sha256(json.dumps(inventory, sort_keys=True,
            separators=(',', ':')).encode()).hexdigest(),
        target=inventory.get('tcpdump'), owned_names=owned, receipt=receipt,
        status='NO_OWNED_POLICY_OBSERVED' if not owned and receipt == 'ABSENT' else 'RETAINED_STATE_OBSERVED',
        kernel_policy_unloaded=False, receipt_unlinked=False,
        observation_limit='SNAPSHOT_ONLY_NOT_LAUNCH_EXCLUSION_OR_VM_DESTRUCTION')
    return inventory, record


def main():
    if sys.argv[1:] not in ([], ['--snapshot-only']):
        raise ValueError('unsupported diagnostic invocation')
    owner = load_owner(Path(__file__).resolve().parents[3])
    owner['_bwrap_root']()
    before_fds = owner['fds']()
    inventory, opening = snapshot(owner)
    result = dict(schema='dg21.resource-discriminator.v1', source_sha256=SOURCE_SHA256,
        source_bytes=SOURCE_BYTES, authority='READ_ONLY_DIAGNOSTIC_ONLY',
        policy_operations=0, raw_policy_bytes_logged=0, opening=opening, exit_code=2)
    if sys.argv[1:] == ['--snapshot-only']:
        result.update(mode='FINAL_METADATA_SNAPSHOT_ONLY',
            exit_code=0 if opening['status'] == 'NO_OWNED_POLICY_OBSERVED' else 1,
            descriptor_restoration=owner['fds']() == before_fds)
        if not result['descriptor_restoration']:
            result['exit_code'] = 2
    else:
        result['mode'] = 'EXISTING_RESOLVER_THROUGH_TARGET_ONLY'
        def deadline(signum, frame):
            raise DiagnosticBoundary('read-only diagnostic deadline exceeded; no retry')
        previous = signal.signal(signal.SIGALRM, deadline)
        try:
            signal.alarm(40)
            if opening['status'] != 'NO_OWNED_POLICY_OBSERVED':
                raise ValueError('owned policy or receipt already present; diagnostic inapplicable')
            selected = inventory.get('tcpdump')
            if (selected is None or selected['sha256'] != TARGET_SHA256
                    or selected['attach'] != '<unknown>'):
                raise ValueError('selected tcpdump kernel identity changed; no diagnostic read')
            result.update(observe(owner, inventory))
        except (OSError, ValueError, DiagnosticBoundary) as exc:
            result.update(status='DIAGNOSTIC_INAPPLICABLE_OR_INTERRUPTED', reason=str(exc), exit_code=2)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)
            try:
                closing_inventory, closing = snapshot(owner)
                result.update(closing=closing, inventory_bookends_equal=closing_inventory == inventory)
            except (OSError, ValueError, UnicodeError) as exc:
                result['closing_observation_error'] = str(exc)
            result['descriptor_restoration'] = owner['fds']() == before_fds
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    return result['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
