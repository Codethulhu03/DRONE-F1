from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    import psutil as psutilNew
    
    processIter = psutilNew.process_iter
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    processIter = notImplemented
