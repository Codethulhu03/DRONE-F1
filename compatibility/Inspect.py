from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from inspect import stack as instack, signature as insig, getmodulename as insgmn
    
    stack = instack
    signature = insig
    getmodulename = insgmn
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    stack = notImplemented
    signature = notImplemented
    getmodulename = notImplemented
