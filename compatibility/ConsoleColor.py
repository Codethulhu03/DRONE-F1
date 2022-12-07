from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    import colorama
    from colorama import Fore, Back, Style
    from colorama.ansi import AnsiFore, AnsiStyle
    
    colorama.init(autoreset=True)
    ConsoleStyle = Style
    
    from compatibility.Itertools import chain
    
    
    class ConsoleColor:
        F = Fore
        B = Back
    
    
    def wrap(string: str, *args: [AnsiFore, AnsiStyle]):
        prefix = "".join(args)
        return f"{prefix}{string}{ConsoleStyle.RESET_ALL * bool(prefix)}" if string else string
    
    
    def containsStyling(string: str) -> bool:
        return any(x in string for x in chain(dir(Fore), dir(Back), dir(Style)))
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    ConsoleStyle = None
    ConsoleColor = None
    wrap = notImplemented
    containsStyling = notImplemented
