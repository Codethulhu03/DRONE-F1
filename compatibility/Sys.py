from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    import sys as sysNew
    from sys import getsizeof, argv as sysArgv, stdin as sysIn, version as sysVersion
    
    version = sysVersion
    stdin = sysIn
    stdout = sysNew.stdout
    argv = sysArgv
    sizeof = getsizeof
    sys = sysNew
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    version = None
    stdin = None
    stdout = None
    argv = None
    sizeof = notImplemented
    sys = None
