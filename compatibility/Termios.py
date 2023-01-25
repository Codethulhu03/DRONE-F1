from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from termios import tcgetattr as termiosgetattr, error as termioserror
    
    error = termioserror
    tcgetattr = termiosgetattr
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    error = None
    tcgetattr = notImplemented
