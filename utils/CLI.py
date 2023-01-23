from compatibility.ConsoleColor import ConsoleColor as CC, ConsoleStyle as CS, wrap, containsStyling
from compatibility.Difflib import get_close_matches as closestMatch
from compatibility.Functools import wraps
from compatibility.Getpass import getuser
from compatibility.Platform import system
from compatibility.Readchar import readkey, key as KEY, available
from compatibility.Regex import match as reMatch, IGNORECASE as reIgnoreCase, error as reError
from compatibility.Socket import gethostname
from compatibility.Sys import stdout, stdin, version
from compatibility.Time import time
from compatibility.Traceback import traceback
from compatibility.Typing import TypeVar, Callable, Any
from utils.Logger import Logger, _Logging

from compatibility.Termios import tcgetattr, error as termiosError, available
USE_TERMIOS: bool = available and system() != "Windows"

F = TypeVar('F', bound=Callable[..., Any])


class _Helper:
    helpDict: dict[str, tuple[str, bool, bool]] = {}
    helpInfo: str = f"Type '{wrap('help', CC.F.CYAN)}' for an overview of usable commands"


def helptext(text: str, arg: str = "", pretty: bool = False):
    def decorator_help(func: F):
        bArg = bool(arg)
        msg = f"{text}{(' | ' * bArg)}{arg}{' | -p for pretty printing' * pretty}"
        _Helper.helpDict[func.__name__[1:]] = (msg.replace("|", wrap("|", CC.F.LIGHTBLACK_EX)), bArg, pretty)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator_help


class Executor:
    VERSION: str = "0.1.1"
    """ Software version to print """
    P_ARGS: set = {"-p", "--p", "--pretty", "-pretty"}
    """ Pretty printing arguments """
    D_ARGS: set = {"-d", "--d", "--depth", "-depth"}
    """ Pretty printing depth arguments """
    
    def __init__(self, logger: Logger):
        self._logger: Logger = logger
    
    def __unknown(self, *cmd: str):
        return f"Unknown Command: {wrap(cmd[0], CC.F.RED)}{self.__closest(cmd[0])}"
    
    def __error(self, arg: str, e: Exception):
        # open new file in errors with current timestamp as name followed by .log containing the error stacktrace
        with open(f"errors/{int(time())}.log", "w") as f:
            traceback.print_exc(file=f)
        return f"Error in {wrap(arg, CC.F.CYAN)}: {wrap(e.__class__.__name__, CC.F.RED)} - {wrap(e, CC.F.LIGHTRED_EX)}"
    
    @staticmethod
    def __closest(cmd: str) -> str:
        matches: list[str] = closestMatch(cmd.lower(), _Helper.helpDict.keys(), 1, cutoff=0.3)
        return "  -  " + (f"Did you mean '{wrap(matches[0], CC.F.CYAN)}'?"
                          if len(matches) == 1 else _Helper.helpInfo)
    
    def __execute(self, consoleInput: str):
        consoleInput = consoleInput.strip()
        repCI: str = consoleInput.replace("  ", " ")
        while consoleInput != repCI:
            repCI = repCI.replace("  ", " ")
            consoleInput = repCI
        splitInput: list[str] = consoleInput.split(" ")
        name: str = splitInput[0].lower().strip()
        target: Callable = getattr(self, f"_{name}", self.__unknown)
        isKnown: bool = (target != self.__unknown)
        splitInput = splitInput[isKnown:len(splitInput) * (not isKnown or _Helper.helpDict[name][1]
                                                           or _Helper.helpDict[name][2])]
        pretty: bool = bool(set(splitInput).intersection(self.P_ARGS))
        depth: int = -1
        dArgs: set[str] = set(splitInput).intersection(self.D_ARGS)
        ind = 0
        if dArgs:
            ind = splitInput.index(dArgs.pop()) + 1
            depth = int(splitInput[ind])

        result: str = target(*[x for x in splitInput[:ind] + splitInput[ind + int(ind != 0):] if x not in self.P_ARGS.union(self.D_ARGS)])
        
        (self._logger.pwrite if isKnown and _Helper.helpDict[name][2] and pretty
         else self._logger.write)(result, depth=depth)
    
    def __call__(self, *args, **kwargs):
        try:
            self.__execute(str(*args))
        except Exception as e:
            self._logger.print(self.__error(str(*args).strip().split(" ")[0], e=e))
    
    def _exit(self, msg: str = "EXITING..."):
        self._logger.print(wrap(msg, CC.F.RED, CS.BRIGHT))
        exit(-1)


class CLI:
    CURR_CONSOLE_INPUT = ""
    
    def __init__(self, executor: Executor, logger: Logger):
        self.__exe: Executor = executor
        self.__logger: Logger = logger
        self.__running: bool = False
        self.__prompt: str = wrap(">>> ", CC.F.LIGHTBLACK_EX)
        self.__lastInputs: dict[str, list[str]] = {}
        self.__useOwn: bool = USE_TERMIOS
    
    def help(self, *args: str) -> str:
        helps: set[str] = set(_Helper.helpDict.keys()).intersection(set(args))
        helps = _Helper.helpDict.keys() if not len(helps) else helps
        maxHelp: int = max(len(msg) for msg in helps)
        return "\n".join(f"{wrap(k.ljust(maxHelp), CC.F.CYAN)}: {_Helper.helpDict[k][0]}" for k in helps)
    
    def start(self):
        self.__running = True
        desc: str = f"{wrap('DRONE', CC.F.LIGHTCYAN_EX, CS.BRIGHT)} version {wrap(Executor.VERSION, CS.DIM)}"
        host: str = f"{wrap(getuser(), CC.F.BLUE)}@{wrap(gethostname(), CC.F.MAGENTA)}"
        self.__logger.write(f"Running {desc} created",
                            "   by Tobias Fischer & Lars Leferenz",
                            "   for the Group for Integrated Communication Systems at TU Ilmenau",
                            "   based on myFliCo_sp by Victor Casas Melo",
                            f"Using {wrap(f'Python version {version.splitlines()[0]}', CC.F.YELLOW)}",
                            f"Running on {host}")
        self.__logger.print(_Helper.helpInfo)
        if self.__useOwn:
            try:
                tcgetattr(stdin.fileno())
                self.__process()
                return
            except termiosError:
                pass
        self.__useOwn = False
        self.__process()
    
    def stop(self):
        self.__running = False
    
    def __execLog(self, consoleInput: str):
        self.__logger.log(consoleInput)
        self.__exe(consoleInput)
    
    def __process(self):
        while self.__running:
            consoleInput = self.input(self.__prompt, set(_Helper.helpDict.keys()))
            if consoleInput:
                self.__execLog(consoleInput)
    
    def input(self, prompt: str, completions: set[str] = None) -> str:
        splits = prompt.splitlines()
        for i, line in enumerate(splits):
            if i < (len(splits) - 1):
                self.__logger.print(line)
            prompt = line
        if completions is None:
            completions = set()
        if not self.__useOwn:
            if containsStyling(prompt):
                print(prompt, end="")
                prompt = ""
            return input(prompt).strip()
        index: int = 1
        matches: list[str] = []
        matchInd: int = 0
        self.__lastInputs.setdefault(prompt, []).append("")
        consoleInput: str = self.__lastInputs[prompt][-index]
        count = caret = 0
        stdout.write(f"\r\033[K{prompt}")
        while True:
            offset: int = 0
            save = load = False
            inkey: str = readkey()
            if inkey == KEY.CTRL_C:
                raise KeyboardInterrupt("KEYBOARD_INTERRUPT")
            elif inkey in (KEY.UP, KEY.DOWN):
                u = inkey == KEY.UP
                index = min(index + 1, len(self.__lastInputs[prompt])) * u + max(index - 1, 1) * (not u)
                load = True
            elif inkey in (KEY.LEFT, KEY.RIGHT):
                r = inkey == KEY.RIGHT
                caret = min(caret + 1, count) * r + max(caret - 1, 0) * (not r)
            elif inkey == KEY.ENTER:
                stdout.write("\n")
                break
            elif inkey in (KEY.BACKSPACE, "", "\x1b[3~"):
                matchInd = 0
                matches = []
                b = inkey != "\x1b[3~"
                if b or (caret - count):
                    consoleInput = consoleInput[:caret - b] + consoleInput[caret + (not b):]
                    caret += (caret - count) and not b
                    offset = -bool(count)
            elif inkey == "\x09":
                if not matches:
                    matches = [c for c in completions if reMatch(consoleInput.strip(), c, reIgnoreCase)]
                if matches:
                    consoleInput = matches[matchInd]
                    caret = count = len(consoleInput)
                    save = True
                    matchInd = (matchInd + 1) % len(matches)
            elif inkey in ("\x1b[H", "\x1b[F"):
                caret = 0 + count * inkey.endswith("F")
            elif len(inkey) == 1:
                matchInd = 0
                matches = []
                consoleInput = consoleInput[:caret] + inkey + consoleInput[caret:]
                offset = save = True
            count += offset
            caret += offset
            if save:
                index = 1
                self.__lastInputs[prompt][-index] = consoleInput
            elif load:
                consoleInput = self.__lastInputs[prompt][-index]
                caret = count = len(consoleInput)
            first: str = consoleInput.split(' ')[0]
            color: str = CC.F.RED
            try:
                reMatch(first, "")
            except reError:
                count -= 1
                caret -= 1
                consoleInput = consoleInput[:caret] + consoleInput[caret + 1:]
                self.__lastInputs[prompt][-index] = consoleInput
                continue
            if not completions or not first:
                color: str = ""
            elif any(first.casefold() == c.casefold() for c in completions):
                color = CC.F.GREEN
            elif any(reMatch(first, c, reIgnoreCase) for c in completions):
                color = CC.F.YELLOW
            output = f"\r\033[K{prompt}{wrap(first, color)}{consoleInput[len(first):]}\x1b[C\x1b[{count - caret + 1}D"
            stdout.write(output)
            _Logging.CURR_CONSOLE_INPUT = output
        consoleInput = consoleInput.strip()
        if consoleInput:
            self.__lastInputs[prompt][-1] = consoleInput
            if len(self.__lastInputs[prompt]) >= 2 and consoleInput == self.__lastInputs[prompt][-2]:
                self.__lastInputs[prompt].pop()
        _Logging.CURR_CONSOLE_INPUT = f"\r\033[K{prompt}"
        return consoleInput
