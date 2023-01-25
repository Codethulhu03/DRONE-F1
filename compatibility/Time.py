from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from time import sleep as pySleep, time as pyTime, strftime as pyStrfTime, gmtime as pyGmTime
    from datetime import datetime as pyDateTime
    
    sleep = pySleep
    time = pyTime
    strftime = pyStrfTime
    gmtime = pyGmTime
    now = pyDateTime.now
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    sleep = notImplemented
    time = notImplemented
    strftime = notImplemented
    gmtime = notImplemented
    now = notImplemented
