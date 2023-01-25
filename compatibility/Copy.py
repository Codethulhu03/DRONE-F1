from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from copy import deepcopy as copydeep
    
    deepcopy = copydeep
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    deepcopy = notImplemented
