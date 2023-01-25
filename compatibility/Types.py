available: bool = True

try:
    from types import TracebackType as ttracebacktype
    
    TracebackType = ttracebacktype
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    TracebackType = None
