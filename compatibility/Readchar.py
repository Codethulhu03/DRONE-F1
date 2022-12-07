from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from readchar import readkey as rcreadkey, key as rckey
    
    readkey = rcreadkey
    key = rckey
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    readkey = notImplemented
    key = None
