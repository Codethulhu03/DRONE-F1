available: bool = True
try:
    from threading import Thread as pyThread, Condition as pyCond, Lock as pyLock
    from enum import Enum
    import sys

    Thread = pyThread
    Condition = pyCond
    Lock = pyLock


    class PriorityClass(Enum):
        if sys.platform == "win32":
            import win32api, win32process, win32con
            IDLE = win32process.IDLE_PRIORITY_CLASS
            LOW = win32process.BELOW_NORMAL_PRIORITY_CLASS
            NORMAL = win32process.NORMAL_PRIORITY_CLASS
            HIGH = win32process.ABOVE_NORMAL_PRIORITY_CLASS
            VERY_HIGH = win32process.HIGH_PRIORITY_CLASS
            REALTIME = win32process.REALTIME_PRIORITY_CLASS
        else:
            IDLE = 16
            LOW = 8
            NORMAL = 4
            HIGH = 2
            VERY_HIGH = 1
            REALTIME = 0
    def osPriority(priority: PriorityClass):
        try:
            if sys.platform == "win32":
                import win32api, win32process, win32con

                pid = win32api.GetCurrentProcessId()
                handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
                win32process.SetPriorityClass(handle, priority.value)
            else:
                import os
                os.nice(priority.value)
        except Exception as ignored:
            pass

except Exception:
    available = False
    print(f"Module not installed: {__name__}")
    
    Thread = None
    Condition = None
    Lock = None
