from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    from termios import tcgetattr as termiosgetattr, error as termioserror
    
    error = termioserror
    tcgetattr = termiosgetattr
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    error = None
    tcgetattr = notImplemented
