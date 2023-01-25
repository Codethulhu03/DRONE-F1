from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    import sys as sysNew
    from sys import getsizeof, argv as sysArgv, version as sysVersion
    
    version = sysVersion
    stdin = sysNew.stdin
    stdout = sysNew.stdout
    stderr = sysNew.stderr
    argv = sysArgv
    sizeof = getsizeof
    sys = sysNew
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    version = None
    stdin = None
    stdout = None
    stderr = None
    argv = None
    sizeof = notImplemented
    sys = None
