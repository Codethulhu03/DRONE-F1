from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from bisect import insort as bs_insort
    
    insort = bs_insort
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    
    insort = notImplemented
