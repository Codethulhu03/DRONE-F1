from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from ast import literal_eval as astLE
    
    literal_eval = astLE
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    literal_eval = notImplemented
