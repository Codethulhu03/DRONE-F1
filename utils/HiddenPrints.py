from compatibility.Sys import sys, stdout, stderr  # sys for sys.stdout, stdout for saved stdout reference, error same
from compatibility.OS import path # path for path.join
from compatibility.Typing import Optional, IO
from utils.Logger import _Logging # _Logging for DIR

class HiddenPrints:
    """
    Class to hide prints from the console.
    
    .. note:: Logging will still work, only explicit print() calls will be hidden, which shouldn't be used anyway.
    -> Use this for hiding Library prints. (ContextManager - *with HiddenPrints():*)
    """

    stderrFile: Optional[IO] = None

    def __enter__(self):
        """ Redirects stdout to None and stderr to log file. """
        sys.stdout = None
        stderrFile = open(path.join(_Logging.DIR, "stderr.log"), "a")
        sys.stderr = stderrFile
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Restores stdout and stderr. """
        sys.stdout = stdout
        sys.stderr = stderr
