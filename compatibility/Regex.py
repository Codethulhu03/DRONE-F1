from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from re import match as reMatch, error as reError, IGNORECASE as reIGNORECASE
    
    match = reMatch
    error = reError
    IGNORECASE = reIGNORECASE
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    match = notImplemented
    error = None
    IGNORECASE = None