from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from getpass import getuser as getpassuser
    
    getuser = getpassuser
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    getuser = notImplemented
