from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from time import sleep as pySleep, time as pyTime, strftime as pyStrfTime, gmtime as pyGMT
    
    sleep = pySleep
    time = pyTime
    strftime = pyStrfTime
    gmtime = pyGMT
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    sleep = notImplemented
    time = notImplemented
    strftime = notImplemented
    gmtime = notImplemented
