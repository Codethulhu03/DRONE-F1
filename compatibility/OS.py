available: bool = True
try:
    import os as osComp
    
    os = osComp
    devnull = os.devnull
    path = os.path
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    os = None
    devnull = None
    path = None
