available: bool = True
try:
    from subprocess import Popen as subPopen, STDOUT as subSTDOUT, DEVNULL as subDEVNULL
    
    Popen = subPopen
    STDOUT = subSTDOUT
    DEVNULL = subDEVNULL
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    Popen = None
    STDOUT = None
    DEVNULL = None
