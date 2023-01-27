from compatibility.Thread import Lock
from compatibility.Time import strftime, now, available as tiav  # For logging the timestamp
from compatibility.OS import path, os, available as oav  # For file logging
from compatibility.Traceback import traceback, available as trav  # For logging the traceback
from compatibility.Typing import Any, Callable, available as tyav  # For type hints
from compatibility.Sys import stdout, available as sav  # For logging to stdout (CLI output)
from compatibility.ConsoleColor import (ConsoleColor as CC, ConsoleStyle as CS, wrap, available as ccav,
                                        strip) # For coloring the output

if not (tiav and oav and trav and tyav and sav and ccav):
    raise ImportError("One or more required modules are not available.")

class _Logging:
    """ Helper class for the Logger class - do not use directly """
    DIR: str = "logs"
    """ The directory where the log files are stored """
    if not path.isdir(DIR):
        os.mkdir(DIR)
    CURR_CONSOLE_INPUT: str = ""
    """ The current console input, used for fixing printing in CLI """
    LOCK: Lock = Lock()
    """ The lock used for thread safety """


class Logger:
    """ Class for logging to the CLI or files """
    
    def __init__(self, category: str = ""):
        """
        Initializes the logger
        
        :param category: The category to log to. (Default: "")
        """
        self.__category: str = category
        """ The category to log to """
        self.__prettyDepth: int = -1
        """ The depth to pretty print to. -1 for unlimited """

    def write(self, *args: Any, **kwargs: Any):
        """
        Writes the given argument to CLI and the log file of the current category
        
        :param args: arguments to write
        :param kwargs: kwargs to pass to print()
        """
        self.__writer(self.print, *args, **kwargs)
    
    def pwrite(self, *args: Any, **kwargs: Any):
        """
        Writes the given argument to CLI with "pretty printing" and the log file of the current category
        
        :param args: arguments to write
        :param kwargs: kwargs to pass to pprint()
        """
        self.__writer(self.pprint, *args, **kwargs)
    
    def __writer(self, printer: Callable, *args: Any, **kwargs: Any):
        """
        Writes the given argument to CLI and the log file of the current category
        
        :param printer: The printer to use (either print or pprint)
        :param args: arguments to write
        :param kwargs: kwargs to pass to the printer()
        """
        printer(*args, **kwargs)
        self.log(*args, **kwargs)

    @staticmethod
    def __join(*args: Any) -> str:
        """
        Joins the given arguments to a string with spaces between them

        :param args: The arguments to join
        :return: The joined string
        """
        if not args:
            args = ("",)  # To avoid an error when joining an empty list
        return " ".join(str(arg) for arg in args)  # convert every argument to a string and join them with spaces
    
    def print(self, *args: Any, **kwargs: Any):
        """
        Writes the given argument to CLI and the log file of the current category
        
        :param args: arguments to write
        :param kwargs: "end" kwarg to pass to print()
        """
        for arg in args:
            if not arg:
                continue
            if arg.endswith("\n"):
                arg = arg[:-1]
            if not arg:
                continue
            output: str = Logger.__join(arg, kwargs.get("end", "\n"))  # The output to print
            category: str = f"[{self.__category}]  " if self.__category else ""  # The category to print
            if ccav:
                outputLower = output.lower() # The output in lower case for contains checks
                if "exception" in outputLower or "error" in outputLower:
                    output = wrap(output, CC.F.RED, CS.BRIGHT)
            with _Logging.LOCK:
                stdout.write(f"\r\033[K{category}{output}{_Logging.CURR_CONSOLE_INPUT}")
                # Clear the current line and
                # print the arguments and
                # the last CLI input (for when text is printed while there is still input)

    def pprint(self, *args: Any, **kwargs: Any):
        """
        Writes the given argument to CLI with "pretty printing" and the log file of the current category
        
        :param args: arguments to write
        :param kwargs: "depth" kwarg for pretty printing and "end" for print()
        """
        for arg in args:
            if not arg:
                continue
            lines: list[str] = []
            line: str = ""  # The current line
            pre: int = 0  # The number of spaces to add before the line
            depth: int = kwargs.get("depth", self.__prettyDepth)  # The depth to pretty print to. -1 for unlimited
            # for every pretty printed item from helper method
            for pp in self.__ppHelper(Logger.__join(arg, kwargs.get("end", "\n")).replace("'", "").replace('"', ""), []):
                # offset = 1 if the line starts with an opening bracket, -1 for a closing bracket, 0 if encased in brackets
                offset: int = (pp[0] in ("(", "[", "{")) and not Logger.__encased(pp)
                offset -= (pp[0] in (")", "]", "}"))
                post: int = pre + offset
                line += pp
                if depth < 0 or post <= depth:  # if not max depth continue with a new fresh line, otherwise append to it
                    if lines and Logger.__encased(line):
                        lines[-1] += line  # append to the last line if line represents a complete dict/list/tuple
                    else:
                        lines.append(f"{''.rjust(2 * (pre + min(offset, 0)))}{line}")  # add indentation
                    line = ""
                pre = post
            self.print("\n".join(lines), **kwargs)  # Print the formatted lines

    @staticmethod
    def __encased(s: str) -> bool:
        """
        Utility method for checking if a string is encased in brackets (ignores trailing comma)
        
        :param s: The string to check
        :return: True if the string is encased in brackets, False otherwise
        """
        return f"{s[0]}{s[-1 - 2 * s.endswith(', ')]}" in ("()", "[]", "{}")

    def __ppHelper(self, arg: str, l: list) -> list[str]:
        """
        Split the string according to the pretty print rules
        
        :param arg: The string to pretty print
        :param l: The list to append the pretty printed string to (for recursive calls)
        :return: List of lines for pretty printing
        """
        itemEnd: int = len(arg)
        if itemEnd > 2:  # if the string is longer than 2 characters
            firstComma: int = arg.find(",")
            firstPBracket: int = arg.find("(")
            firstSBracket: int = arg.find("[")
            firstCBracket: int = arg.find("{")
            #  find the first comma or opening bracket (exclude non-existent = -1)
            itemStart = min({firstComma, firstSBracket, firstCBracket, firstPBracket, itemEnd} - {-1})
            # map the opening brackets to their respective closing brackets
            brackets: dict[int, str] = {firstPBracket: "()", firstSBracket: "[]", firstCBracket: "{}"}
            if not itemStart:  # args[0] is a comma or bracket
                itemStart = 1
                itemEnd = self.__findBrackets(arg, brackets[0])[0]
            else:
                if itemStart in brackets:  # the first special character is an opening bracket
                    itemEnd = self.__findBrackets(arg, brackets[itemStart])[itemStart] + 3
                    if itemStart != firstCBracket:
                        itemStart, itemEnd = itemEnd, len(arg)
                else:  # the first special character is a comma or there is no special character
                    itemStart += 2 * (itemStart == firstComma)
                    itemEnd += 2
            l.append(arg[:itemStart])  # append the first part of the string (until the first special char)
            l = self.__ppHelper(arg[itemStart:itemEnd], l)
            l = self.__ppHelper(arg[itemEnd:], l)
        elif itemEnd:  # if the string is shorter than 2 characters but not empty
            l.append(arg)
        return l
    
    @staticmethod
    def __findBrackets(arg: str, brackets: str) -> dict[int, int]:
        """
        Finds all bracket pairs of the given type in the given string.
        
        :param arg: The string to search.
        :param brackets: The type of brackets to search for.
        :return: A dictionary of the start and end indices of each bracket pair.
        
        .. note:: This method would work for any two characters, as long as brackets[0] != brackets[1]
        """
        d: dict[int, int] = {}
        if len(brackets) < 2:
            return d
        indices: list[int] = []
        for i, c in enumerate(arg):
            if c == brackets[0]:
                indices.append(i)
            elif c == brackets[1]:
                d[indices.pop()] = i
        return d
    
    def log(self, *args: Any, **kwargs: Any):
        """
        Logs the given argument with a timestamp to the log file of the current category
        
        :param args: The text to log.
        :param kwargs: Unused - included only for compatibility with print()
        
        .. note:: Saving to file is not implemented yet.
        """
        with open(path.join(_Logging.DIR, f"{self.__category if self.__category else 'log'}.log"), "a") as file:
            for arg in args:
                file.write(f"[{now().strftime('%H:%M:%S')}] {strip(str(arg))}\n")

    def error(self, e: Exception = None, msg: str = ""):
        if isinstance(self, Exception):
            e = self
            self = Logger("exception")
        if e is None:
            e = Exception(msg)
        self.write(msg if msg else str(e))
        self.log(type(e).__name__, *traceback.format_exc().split("\n"))

    def flush(self):
        pass
