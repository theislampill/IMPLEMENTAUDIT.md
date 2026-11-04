#!/usr/bin/env python3
"""Focused native and fault controls for the build-local compression successor.

Synthetic build inputs are explicit unit seams. Full real-source archive parity
is tested separately with both old and new owners on one clean candidate.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import traceback
import zipfile
import zlib

sys.dont_write_bytecode = True
OPTIONS = dict(numiterations=15, blocksplitting=1, blocksplittinglast=0, blocksplittingmax=15)


def need(value, message):
    if not value:
        raise AssertionError(message)


def load(path):
    spec = importlib.util.spec_from_file_location("compression_unit_owner", path)
    owner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = owner
    spec.loader.exec_module(owner)
    return owner


class NativeRecorder:
    def __init__(self, native):
        self.native = native
        self.calls = []

    def compress(self, source, **options):
        self.calls.append((source, options.copy()))
        return self.native.compress(source, **options)


class CheapNative:
    """Explicit non-native fault/budget seam; no performance claims."""
    def __init__(self):
        self.calls = []

    def compress(self, source, **options):
        self.calls.append((source, options.copy()))
        return zlib.compress(source)


def member(owner, provider, data):
    compressor = owner.CanonicalZopfliCompressor(provider)
    need(compressor.compress(data) == b"", "unexpected streaming output")
    return compressor.flush()


def synthetic_build(owner, source, output, provider, fail_archive=None):
    original = {name: getattr(owner, name) for name in
                ("source_identity", "artifact_payload_entries", "verify_artifact", "require_zopfli", "write_archive")}
    contract = owner.validate_contract(source)
    owner.source_identity = lambda _root: {"commit": "a" * 40, "tree": "b" * 40}
    owner.artifact_payload_entries = lambda _root, _role, _contract: [("shared.txt", b"shared data\n" * 32, 0o644)]
    owner.verify_artifact = lambda *_args, **_kwargs: None
    owner.require_zopfli = lambda: provider
    archives = []
    holders = []
    cache_class = getattr(owner, "_BuildLocalZopfli", None)
    if cache_class:
        def keep_cache(*args, **kwargs):
            cache = cache_class(*args, **kwargs)
            holders.append(cache)
            return cache
        owner._BuildLocalZopfli = keep_cache
    def write(path, entries, supplied):
        archives.append(supplied)
        if fail_archive == len(archives):
            raise RuntimeError("controlled archive write failure")
        return original["write_archive"](path, entries, supplied)
    owner.write_archive = write
    try:
        result = owner.build_artifacts(source, output, contract)
        return [path.read_bytes() for path in result], holders, archives
    finally:
        if holders:
            for cache in holders:
                need(not cache._entries and cache._retained_bytes == 0, "build retained cached bytes on exit")
        for name, value in original.items():
            setattr(owner, name, value)
        if cache_class:
            owner._BuildLocalZopfli = cache_class


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--red-probe", action="store_true")
    ap.add_argument("--unit-provider", action="store_true",
                    help="use an explicit controlled zlib provider without requiring zopfli")
    args = ap.parse_args()
    need(not args.out.exists(), "fresh output required")
    args.out.mkdir(parents=True)
    path = args.source / "scripts/package-contract.py"
    owner = load(path)
    native = CheapNative() if args.unit_provider else owner.require_zopfli()
    provider_kind = "CONTROLLED_ZLIB_UNIT_SEAM" if args.unit_provider else "GENUINE_ZOPFLI_0_2_3_POST1"
    checks = []

    def check(name, fn):
        try:
            detail = fn()
            checks.append(dict(name=name, status="PASS", detail=detail))
        except Exception as exc:
            checks.append(dict(name=name, status="FAIL", error=type(exc).__name__ + ": " + str(exc), traceback=traceback.format_exc()))

    with tempfile.TemporaryDirectory(prefix="implementaudit-compression-controls-") as temporary:
        work = Path(temporary)

        def build_reuse():
            provider = NativeRecorder(native)
            first, holders_a, archive_a = synthetic_build(owner, args.source, work / "first", provider)
            count_a = len(provider.calls)
            need(count_a == 3, "two projections compressed the shared source more than once: expected3 actual" + str(count_a))
            second, holders_b, archive_b = synthetic_build(owner, args.source, work / "second", provider)
            need(len(provider.calls) - count_a == 3, "second build reused earlier build state")
            need(first == second, "synthetic build bytes changed")
            need(archive_a[0] is archive_a[1] and archive_b[0] is archive_b[1], "projections do not share build-local provider")
            need(archive_a[0] is not archive_b[0], "provider cache survived across build calls")
            need(len(holders_a) == len(holders_b) == 1, "build cache was not unique")
            return dict(first_native_calls=count_a, second_native_calls=len(provider.calls)-count_a,
                        archives_equal=True, both_build_caches_cleared=True)

        check("shared_projection_reuse_and_cross_build_isolation", build_reuse)
        if not args.red_probe:
            Cache = owner._BuildLocalZopfli

            def equality_and_options():
                provider = CheapNative(); cache = Cache(provider)
                source = b"exact" * 41
                first = cache.compress(source, **OPTIONS)
                need(cache.compress(bytes(bytearray(source)), **dict(reversed(list(OPTIONS.items())))) == first, "equal immutable input missed")
                need(len(provider.calls) == 1, "equal input/options did not reuse")
                cache.compress(source + b"!", **OPTIONS)
                need(len(provider.calls) == 2, "distinct source aliased")
                for key, value in OPTIONS.items():
                    changed = dict(OPTIONS, **{key: value + 1})
                    for _ in range(2):
                        cache.compress(source, **changed)
                    need(provider.calls[-1][1] == changed, "changed option was not forwarded exactly")
                typed = dict(OPTIONS, blocksplitting=True)
                for _ in range(2):
                    cache.compress(source, **typed)
                omitted = {k:v for k,v in OPTIONS.items() if k != "blocksplittinglast"}
                cache.compress(source, **omitted)
                extra = dict(OPTIONS, unexpected="controlled")
                cache.compress(source, **extra)
                need(len(provider.calls) == 14, "noncanonical option calls were cached")
                need(provider.calls[-1][1] == extra, "unknown option was changed")
                need(cache.compress(source, **OPTIONS) == first and len(provider.calls) == 14, "bypass disturbed canonical entry")
                return dict(native_calls=14, exact_bytes_and_options=True)

            check("exact_source_options_types_and_unknown_kwargs", equality_and_options)

            def mutable_input():
                provider=CheapNative(); cache=Cache(provider); source=bytearray(b"mutable")
                cache.compress(source, **OPTIONS); source[0]=ord("M"); cache.compress(source, **OPTIONS)
                need(len(provider.calls)==2 and not cache._entries, "mutable input entered cache")
                return dict(non_bytes_bypassed=True)
            check("mutable_input_bypasses_reuse", mutable_input)

            def budget(kind):
                a, b = b"A" * 96, b"B" * 96
                cost = len(a) + len(zlib.compress(a))
                class Small(Cache):
                    MAX_BYTES = cost if kind == "bytes" else 8 * cost
                    MAX_ENTRIES = 8 if kind == "bytes" else 1
                provider=CheapNative();cache=Small(provider)
                for data in (a, b, a):
                    cache.compress(data, **OPTIONS)
                    need(cache._retained_bytes <= cache.MAX_BYTES and len(cache._entries) <= cache.MAX_ENTRIES, "cache bound exceeded")
                need(len(provider.calls)==3, "FIFO eviction did not force recompression")
                cache.clear(); need(cache._retained_bytes==0 and not cache._entries, "clear retained state")
                return dict(forced_eviction=True, native_calls=3, bound_kind=kind)
            check("combined_source_stream_byte_bound_and_eviction", lambda: budget("bytes"))
            check("entry_count_bound_and_eviction", lambda: budget("entries"))

            def oversize():
                class Small(Cache):
                    MAX_BYTES=64
                provider=CheapNative();cache=Small(provider)
                for _ in range(2): cache.compress(b"A" * 65, **OPTIONS)
                need(len(provider.calls)==2 and not cache._entries and cache._retained_bytes==0, "oversize source retained")
                return dict(oversize_bypassed=True)
            check("oversize_cache_entry_bypasses_retention", oversize)

            def native_fault():
                class Fault(CheapNative):
                    def compress(self, source, **options):
                        self.calls.append((source,options))
                        raise RuntimeError("controlled native failure")
                provider=Fault();cache=Cache(provider)
                for _ in range(2):
                    try: cache.compress(b"fault", **OPTIONS)
                    except RuntimeError as exc: need(str(exc)=="controlled native failure", "fault changed")
                    else: raise AssertionError("native fault swallowed")
                need(len(provider.calls)==2 and not cache._entries, "failed native call entered cache")
                return dict(native_fault_propagated=True)
            check("native_exception_not_cached_or_swallowed", native_fault)

            def roundtrips():
                provider=NativeRecorder(native);cache=Cache(provider);source=b"round trip" * 32
                calls=[];original=owner.zlib.decompress
                def decompress(data, *args, **kwargs):
                    calls.append((args,kwargs.copy()))
                    return original(data,*args,**kwargs)
                owner.zlib.decompress=decompress
                try:
                    one=member(owner,cache,source);two=member(owner,cache,source)
                finally: owner.zlib.decompress=original
                need(one==two and len(provider.calls)==1 and len(calls)==4, "cache hit skipped a member round trip")
                need([kwargs.get("wbits") for _args,kwargs in calls]==[None,-15,None,-15], "round-trip modes changed")
                return dict(provider_calls=1, member_roundtrip_calls=4)
            check("cache_hit_preserves_both_member_roundtrips", roundtrips)

            def corrupted_hit():
                provider=CheapNative();cache=Cache(provider);source=b"bound member" * 20
                member(owner,cache,source)
                key=next(iter(cache._entries));cache._entries[key]=zlib.compress(b"wrong member")
                try: member(owner,cache,source)
                except owner.ContractError as exc: need("round-trip" in str(exc), "wrong fault")
                else: raise AssertionError("corrupt cached stream passed")
                return dict(corrupt_cached_stream_refused=True)
            check("corrupt_cached_stream_fails_roundtrip", corrupted_hit)

            def invalid_native():
                class Invalid(CheapNative):
                    def compress(self, source, **options):
                        return b"invalid zlib stream"
                before=zipfile._get_compressor
                try: synthetic_build(owner,args.source,work/"invalid",Invalid())
                except zlib.error: pass
                else: raise AssertionError("invalid native stream accepted")
                need(zipfile._get_compressor is before, "archive compressor hook leaked after fault")
                return dict(invalid_native_refused=True, cache_and_zip_hook_cleaned=True)
            check("invalid_native_stream_build_cleanup", invalid_native)

            def archive_fault():
                before=zipfile._get_compressor
                try: synthetic_build(owner,args.source,work/"write-fault",CheapNative(),fail_archive=2)
                except RuntimeError as exc: need(str(exc)=="controlled archive write failure", "fault changed")
                else: raise AssertionError("write fault swallowed")
                need(zipfile._get_compressor is before, "archive compressor hook leaked")
                return dict(first_archive_cache_cleared_on_second_failure=True)
            check("second_archive_fault_clears_build_state", archive_fault)

    result=dict(schema="dg16.r4.build-local-compression-controls.v1",
                status="PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL",
                scope="FOCUSED_COMPRESSION_AND_EXPLICIT_SYNTHETIC_FAULT_CONTROLS_NOT_ORIGINAL_PAIR",
                provider=provider_kind,
                owner_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                source=str(args.source), python=sys.executable, checks=checks,
                original_acceptance_delta=0)
    (args.out/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"checks":[{k:v for k,v in c.items() if k!="traceback"} for c in checks]},indent=2))
    return 0 if result["status"]=="PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
