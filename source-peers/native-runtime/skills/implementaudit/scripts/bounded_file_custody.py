"""Windows read-only handle custody, adapted from R0038's repository reader.

Every child is opened relative to a held parent with reparsing disabled.
Parents deny delete sharing; the leaf permits append by the live native writer.
No path mutation, creation, executable loading, or unbounded content read exists.
"""
from contextlib import contextmanager
import ctypes
import os
from pathlib import Path, PureWindowsPath
import re


class UnicodeString(ctypes.Structure):
    _fields_ = [('length',ctypes.c_uint16),('maximum',ctypes.c_uint16),('buffer',ctypes.c_void_p)]

class ObjectAttributes(ctypes.Structure):
    _fields_ = [('length',ctypes.c_uint32),('root',ctypes.c_void_p),('name',ctypes.POINTER(UnicodeString)),
               ('attributes',ctypes.c_uint32),('security',ctypes.c_void_p),('quality',ctypes.c_void_p)]

class IoStatus(ctypes.Structure):
    _fields_ = [('status',ctypes.c_void_p),('information',ctypes.c_size_t)]

class FileTime(ctypes.Structure):
    _fields_ = [('low',ctypes.c_uint32),('high',ctypes.c_uint32)]

class FileInfo(ctypes.Structure):
    _fields_ = [('attributes',ctypes.c_uint32),('creation',FileTime),('access',FileTime),('write',FileTime),
               ('volume',ctypes.c_uint32),('size_high',ctypes.c_uint32),('size_low',ctypes.c_uint32),
               ('links',ctypes.c_uint32),('index_high',ctypes.c_uint32),('index_low',ctypes.c_uint32)]

def kernel_api():
    if os.name != 'nt': raise OSError('WINDOWS_CUSTODY_ONLY')
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p]
    k.CreateFileW.restype=ctypes.c_void_p
    k.GetFileInformationByHandle.argtypes=[ctypes.c_void_p,ctypes.c_void_p];k.GetFileInformationByHandle.restype=ctypes.c_int
    k.GetFinalPathNameByHandleW.argtypes=[ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32];k.GetFinalPathNameByHandleW.restype=ctypes.c_uint32
    k.GetDriveTypeW.argtypes=[ctypes.c_wchar_p];k.GetDriveTypeW.restype=ctypes.c_uint32
    k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
    return k

def info(k, handle):
    value=FileInfo()
    if not k.GetFileInformationByHandle(handle,ctypes.byref(value)): raise ctypes.WinError(ctypes.get_last_error())
    return value

def handle_name(k, handle):
    size=k.GetFinalPathNameByHandleW(handle,None,0,0)
    if size==0 or size>32768: raise OSError('HANDLE_NAME_BOUND')
    buffer=ctypes.create_unicode_buffer(size)
    length=k.GetFinalPathNameByHandleW(handle,buffer,size,0)
    if length==0 or length>=size or not buffer.value.startswith('\\\\?\\'): raise OSError('HANDLE_NAME_CHANGED')
    return PureWindowsPath(buffer.value[4:])

def open_child(parent, name, directory, allow_append=True):
    nt=ctypes.WinDLL('ntdll')
    nt.NtCreateFile.argtypes=[ctypes.POINTER(ctypes.c_void_p),ctypes.c_uint32,ctypes.POINTER(ObjectAttributes),
        ctypes.POINTER(IoStatus),ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,
        ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32]
    nt.NtCreateFile.restype=ctypes.c_long
    nt.RtlNtStatusToDosError.argtypes=[ctypes.c_long];nt.RtlNtStatusToDosError.restype=ctypes.c_uint32
    buffer=ctypes.create_unicode_buffer(name);length=len(name.encode('utf-16-le'))
    if length>65532: raise OSError('COMPONENT_NAME_BOUND')
    text=UnicodeString(length,length+2,ctypes.cast(buffer,ctypes.c_void_p))
    attributes=ObjectAttributes(ctypes.sizeof(ObjectAttributes),parent,ctypes.pointer(text),0x40|0x1000,None,None)
    result=ctypes.c_void_p();status=IoStatus()
    # Directory handles only query identity/name and anchor relative opens.
    # They need READ_ATTRIBUTES, not SYNCHRONIZE or directory enumeration.
    code=nt.NtCreateFile(ctypes.byref(result),0x80 if directory else 0x00100081,ctypes.byref(attributes),
        ctypes.byref(status),None,0,1 if directory or not allow_append else 3,1,(0 if directory else 0x20)|0x00200000|(1 if directory else 0x40),None,0)
    if code<0: raise ctypes.WinError(nt.RtlNtStatusToDosError(code))
    return result.value

def lexical_path(value):
    text=str(value)
    if text.startswith('\\\\?\\'): text=text[4:]
    path=Path(text)
    if not path.is_absolute() or os.path.normpath(text)!=text or len(path.drive)!=2 or path.drive[1]!=':':
        raise OSError('LEXICAL_LOCAL_ABSOLUTE_PATH_REQUIRED')
    if any(part in ('.','..') or ':' in part or part.rstrip(' .')!=part or PureWindowsPath(part).is_reserved() for part in path.parts[1:]):
        raise OSError('PATH_ALIAS_OR_STREAM_REFUSED')
    return path

@contextmanager
def held_file(value, *, allow_append=True):
    import msvcrt
    path=lexical_path(value);k=kernel_api();handles=[];stream=None;transferred=False;fd=None
    if k.GetDriveTypeW(path.anchor)!=3: raise OSError('FIXED_LOCAL_DRIVE_REQUIRED')
    try:
        requested=PureWindowsPath(path.anchor);parts=path.parts[1:]
        if not parts: raise OSError('REGULAR_FILE_REQUIRED')
        for index,part in enumerate((None,*parts)):
            if part is None:
                h=k.CreateFileW(path.anchor,0x80000000,1,None,3,0x02200000,None)
                if h==ctypes.c_void_p(-1).value: raise ctypes.WinError(ctypes.get_last_error())
            else:
                h=open_child(handles[-1],part,index<len(parts),allow_append=allow_append);requested/=part
            handles.append(h);current=info(k,h)
            if current.attributes&0x400 or str(handle_name(k,h)).casefold()!=str(requested).casefold():
                raise OSError('REPARSE_OR_SHORTNAME_ALIAS_REFUSED')
            if index<len(parts):
                if not current.attributes&0x10: raise OSError('PARENT_NOT_DIRECTORY')
            elif current.attributes&0x10 or current.links!=1: raise OSError('NONREGULAR_OR_HARDLINK_SOURCE')
        fd=msvcrt.open_osfhandle(handles[-1],os.O_RDONLY|os.O_BINARY)
        transferred=True
        stream=os.fdopen(fd,'rb',buffering=0)
        before=os.fstat(stream.fileno())
        yield stream
        after=os.fstat(stream.fileno())
        if (before.st_dev,before.st_ino)!=(after.st_dev,after.st_ino) or after.st_nlink!=1:
            raise OSError('HELD_SOURCE_IDENTITY_CHANGED')
        requested=PureWindowsPath(path.anchor)
        for index,h in enumerate(handles):
            if index: requested/=parts[index-1]
            current=info(k,h)
            if current.attributes&0x400 or str(handle_name(k,h)).casefold()!=str(requested).casefold():
                raise OSError('HELD_PATH_CHANGED')
    finally:
        failures=[]
        if stream is not None:
            try: stream.close()
            except BaseException as error: failures.append(type(error).__name__)
        elif fd is not None:
            try: os.close(fd)
            except BaseException as error: failures.append(type(error).__name__)
        for index,h in reversed(list(enumerate(handles))):
            if transferred and index==len(handles)-1: continue
            if not k.CloseHandle(h): failures.append('CLOSE_HANDLE_FAILED')
        if failures: raise OSError('CUSTODY_CLEANUP_FAILED:'+','.join(failures))

def trusted_system_tool(name):
    """Select only the two needed Windows utilities, independent of CWD/PATH."""
    if name not in ('powershell.exe','taskkill.exe'):
        raise ValueError('SYSTEM_TOOL_NOT_ALLOWED')
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.GetSystemDirectoryW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32]
    k.GetSystemDirectoryW.restype=ctypes.c_uint32
    buffer=ctypes.create_unicode_buffer(32768)
    length=k.GetSystemDirectoryW(buffer,len(buffer))
    if length==0 or length>=len(buffer):raise OSError('SYSTEM_DIRECTORY_UNAVAILABLE')
    directory=lexical_path(buffer.value)
    path=directory/('WindowsPowerShell/v1.0/powershell.exe' if name=='powershell.exe' else name)
    if not path.is_file() or Path(os.path.realpath(path))!=path:
        raise OSError('SYSTEM_TOOL_PATH_CHANGED')
    return path
