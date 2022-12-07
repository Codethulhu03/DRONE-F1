available: bool = True

try:
    from types import TracebackType as ttracebacktype
    
    TracebackType = ttracebacktype
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    TracebackType = None
