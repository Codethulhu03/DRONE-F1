available: bool = True
try:
    import traceback as Traceback
    
    traceback = Traceback
except ImportError as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    traceback = None
