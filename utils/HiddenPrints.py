from compatibility.Sys import sys, stdout, stderr  # sys for sys.stdout, stdout for saved stdout reference, error same
from compatibility.OS import path # path for path.join
from compatibility.Thread import Lock
from compatibility.Typing import Optional, IO
from utils.Logger import _Logging, Logger  # _Logging for DIR

class HiddenPrints:
    _LOCK = Lock()
    def __init__(self, prefix: str = ""):
        self.__oldStdout = sys.stdout
        self.__oldStdErr = sys.stderr
        self.__prefix = prefix
        self.__buffer = ""
        self.__stdout = stdout
        self.__logger = Logger(prefix)

    def __enter__(self):
        HiddenPrints._LOCK.acquire()
        sys.stdout = self
        sys.stderr = open(path.join(_Logging.DIR, "stderr.log"), "a")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        sys.stdout = self.__oldStdout
        sys.stderr = self.__oldStdErr
        HiddenPrints._LOCK.release()

    def write(self, message):
        self.__buffer += message

    def flush(self):
        buf = self.__buffer
        self.__buffer = ""
        self.__logger.write(*buf.splitlines())
