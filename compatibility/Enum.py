available: bool = True
try:
    from enum import Enum as pyEnum
    
    Enum = pyEnum
except Exception as e:
    from utils.SysInfo import InfoCache
    InfoCache.importErrors.append(e)
    available = False
    print(f"Module not installed: {__name__}")
    Enum = None
