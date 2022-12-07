available: bool = True
try:
    from threading import Thread as pyThread, Condition as pyCond, Lock as pyLock
    
    Thread = pyThread
    Condition = pyCond
    Lock = pyLock
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    
    Thread = None
    Condition = None
    Lock = None
