from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from bisect import insort as bs_insort
    
    insort = bs_insort
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    
    insort = notImplemented
