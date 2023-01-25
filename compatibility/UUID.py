available: bool = True
try:
    from uuid import uuid4 as uu4
    
    uuidStr = uu4().hex
    uuidInt = uu4().int
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    uuidStr = None
    uuidInt = None
