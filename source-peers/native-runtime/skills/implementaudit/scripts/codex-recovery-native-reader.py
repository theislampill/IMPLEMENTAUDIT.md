"""Existing native reader: bounded nonprotected public entry projection."""
import hashlib
import os
import pathlib

class Refusal(ValueError):
    pass

def native_read_nonprotected(selection, methods, *, child_id=None, protocol_helper):
    """Current bounded public transport, called only by the fixed source owner.

    This entry does not choose or authenticate a policy. Its owner supplies the
    already selected helper; P/Q/E still govern whether any result is admitted.
    The legacy native_read override/provider guard is unchanged.
    """
    expected = selection['runtime_helpers']['bounded_native_reader.py']
    path = pathlib.Path(protocol_helper.__file__)
    if path.name != 'bounded_native_reader.py' or str(path) != expected['path']:
        raise Refusal('nonprotected protocol helper path differs')
    with protocol_helper.custody.held_file(path, allow_append=False) as stream:
        before = os.fstat(stream.fileno())
        if before.st_nlink != 1 or before.st_size != expected['bytes'] or before.st_size > 256 * 1024:
            raise Refusal('nonprotected protocol helper bound differs')
        raw = stream.read(before.st_size)
        if len(raw) != before.st_size or hashlib.sha256(raw).hexdigest() != expected['sha256']:
            raise Refusal('nonprotected protocol helper pin differs')
        # protocol_helper.probe holds the actual native executable immutably
        # from byte pin through launch, protocol drainage and terminal readback.
        return protocol_helper.probe(selection, methods, child_id=child_id)
