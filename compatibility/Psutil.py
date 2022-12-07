from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    import psutil as psutilNew
    
    processIter = psutilNew.process_iter
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    processIter = notImplemented
