from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from copy import deepcopy as copydeep
    
    deepcopy = copydeep
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    deepcopy = notImplemented
