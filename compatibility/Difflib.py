from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from difflib import get_close_matches as difflibclosestmatch
    
    get_close_matches = difflibclosestmatch
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    get_close_matches = notImplemented
