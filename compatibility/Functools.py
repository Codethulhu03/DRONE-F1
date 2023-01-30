from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from functools import wraps as funcWraps, cache as funcCache
    
    wraps = funcWraps
    cache = funcCache
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    wraps = notImplemented
    cache = notImplemented
