from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    import os as osComp

    os = osComp
    devnull = os.devnull
    path = os.path
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    os = None
    devnull = None
    path = None
    osPriority = notImplemented
