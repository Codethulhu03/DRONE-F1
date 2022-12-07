from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from functools import wraps as funcWraps
    
    wraps = funcWraps
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    wraps = notImplemented
