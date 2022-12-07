available: bool = True
try:
    from enum import Enum as pyEnum
    
    Enum = pyEnum
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    Enum = None
