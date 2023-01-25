from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from struct import pack as structPack, unpack as structUnpack
    
    pack = structPack
    unpack = structUnpack
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    pack = notImplemented
    unpack = notImplemented
