from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from json import dumps as jsonDumps, dump as jsonDump, loads as jsonLoads, load as JsonLoad
    
    dumps = jsonDumps
    dump = jsonDump
    loads = jsonLoads
    
    
    def read(loc: str) -> dict:
        with open(loc) as file:
            return JsonLoad(file)
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    dumps = notImplemented
    dump = notImplemented
    loads = notImplemented
    red = notImplemented
