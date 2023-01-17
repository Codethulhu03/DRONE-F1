from compatibility.Time import sleep
from compatibility.Typing import Callable, Any, Optional
from compatibility.Thread import Thread, Condition, osPriority, PriorityClass
from drone.DroneData import DroneData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.Event import Event
from utils.events.EventDecorators import process
from utils.events.EventProcessor import EventProcessor, ProcessingMode
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator


class Module(Thread, EventProcessor):
    AVAILABLE: bool = True
    """ Whether the Module is available (imports were successful) """
    ARGS: dict[str, Any] = {"interval": 1.0}
    """ Arguments for the configuration file """
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                 processingMode: ProcessingMode = ProcessingMode.ONE):
        Thread.__init__(self)
        EventProcessor.__init__(self, mediator, processingMode)
        self.__powered: bool = True
        self.__cond: Condition = Condition()
        self._logger: Logger = logger
        self._active: bool = False
        self._configData: ConfigurationData = configData
        self._interval: float = configData.ownArguments["interval"]
        self._priority: PriorityClass = PriorityClass.NORMAL
    
    @process(EventType.INITIALIZATION)
    def _initialize(self, data: Optional[DroneData]):
        pass
    
    @process(EventType.POWER_UP)
    def _powerUp(self, data: Optional[DroneData]):
        self.__powered = True
    
    @process(EventType.POWER_DOWN)
    def _powerDown(self, data: Optional[DroneData]):
        self.__powered = False
    
    def activate(self):
        if self._active:
            self._logger.write(f"{type(self).__name__} already active")
            return
        self._subscribe()
        self._logger.write(f"Activating {type(self).__name__}")
        self._queue.clear()
        self._active = True
        try:
            osPriority(self._priority)
            self.start()
        except RuntimeError:
            pass
        self.__notify()

    def start(self) -> None:
        super().start()
        self._logger.write(f"Started {type(self).__name__}")



    def deactivate(self, kill: bool = False):
        if kill:
            self._powerDown(None)
        if not self._active:
            return
        self._logger.write(f"Deactivating {type(self).__name__}")
        self._active = False
        self.__notify()
    
    def _preProcess(self):
        pass
    
    def _postProcess(self):
        pass

    def __run(self):
        while self.__powered:
            while self._active or self._queue:
                self._asyncProcess()
                sleep(self._interval)

    def _asyncProcess(self):
        pass

    def __condOp(self, condOp: Callable, timeout: float = None):
        try:
            self.__cond.acquire(False)
            if condOp == self.__cond.wait:
                condOp(timeout=timeout)
            else:
                condOp()
            self.__cond.release()
        except RuntimeError as e:
            print(e)
    
    def __wait(self, timeout: float = None):
        self.__condOp(self.__cond.wait, timeout)
    
    def __notify(self):
        self.__condOp(self.__cond.notify)
    
    def notify(self, event: Event):
        EventProcessor.notify(self, event)
        self.__notify()
    
    def run(self):
        asyncThread: Thread = Thread(target=self.__run, daemon=True)
        asyncThread.start()
        while self.__powered:
            if not self._queue:
                self.__wait()
            while self._active or self._queue:
                self._preProcess()
                self._process()
                self._postProcess()
                if self.__powered:
                    self.__wait(self._interval)
        self._logger.write("Waiting for async thread to finish")
        asyncThread.join()
        self._logger.write("Powered down")
