from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from platform import system as platSystem, machine as platMachine
    
    system = platSystem
    machine = platMachine
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    system = notImplemented
    machine = notImplemented
