AVAILABLE: bool = True
try:
    import traceback as Traceback
    
    traceback = Traceback
except ImportError:
    AVAILABLE = False
    print(f"Module not installed: {__name__}")
    traceback = None
