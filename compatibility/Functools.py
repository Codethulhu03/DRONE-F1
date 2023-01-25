from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from functools import wraps as funcWraps
    
    wraps = funcWraps
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    wraps = notImplemented
