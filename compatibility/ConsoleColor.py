from compatibility.NotImplemented import notImplemented

available: bool = True
try:
    import colorama
    from colorama import Fore, Back, Style
    from colorama.ansi import AnsiFore, AnsiStyle
    
    colorama.init(autoreset=True)
    ConsoleStyle = Style

    from compatibility.Itertools import chain
    __modifiers: list[str] = [Fore.RESET, Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
                                Fore.MAGENTA, Fore.CYAN, Fore.WHITE, Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX,
                                Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX,
                                Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX, Back.RESET, Back.BLACK, Back.RED,
                                Back.GREEN, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE,
                                Back.LIGHTBLACK_EX, Back.LIGHTRED_EX, Back.LIGHTGREEN_EX, Back.LIGHTYELLOW_EX,
                                Back.LIGHTBLUE_EX, Back.LIGHTMAGENTA_EX, Back.LIGHTCYAN_EX, Back.LIGHTWHITE_EX,
                                Style.DIM, Style.NORMAL, Style.BRIGHT, Style.RESET_ALL]

    class ConsoleColor:
        F = Fore
        B = Back
    
    
    def wrap(string: str, *args: [AnsiFore, AnsiStyle]) -> str:
        prefix = "".join(args)
        return f"{prefix}{string}{ConsoleStyle.RESET_ALL * bool(prefix)}" if string else string
    
    def strip(string: str) -> str:
        for x in __modifiers:
            string = string.replace(x, "")
        return string

    def containsStyling(string: str) -> bool:
        return any(x in string for x in __modifiers)
except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    ConsoleStyle = None
    ConsoleColor = None
    wrap = notImplemented
    containsStyling = notImplemented
