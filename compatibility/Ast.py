from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from ast import literal_eval as astLE
    
    literal_eval = astLE
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    literal_eval = notImplemented
