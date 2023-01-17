from compatibility.Typing import Callable
from compatibility.Thread import Thread, Condition, osPriority, PriorityClass
from drone.DroneData import DroneData
from drone.PartialDroneData import PartialDroneData
from utils.ConfigurationData import ConfigurationData
from utils.events.Event import Event
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator
from utils.events.Notifiable import Notifiable


class UAV(Thread, Mediator):
    
    def __init__(self, configData: ConfigurationData):
        Thread.__init__(self)
        Mediator.__init__(self)
        self.__powered: bool = True
        self.__active: bool = False
        self.__cond: Condition = Condition()
        self.__data: DroneData = DroneData(PartialDroneData.DEFAULTS(configData))
    
    def __initialize(self):
        pass
    
    @property
    def data(self):
        return self.__data
    
    def activate(self):
        self.__active = True
        try:
            osPriority(PriorityClass.REALTIME)
            self.start()
        except RuntimeError:
            pass
    
    def deactivate(self, kill: bool = False):
        self.__active = not (kill or any(sub for sub in self._subscribers))
        self.__notify()
    
    def unsubscribe(self, subscriber: Notifiable, eventType: EventType):
        Mediator.unsubscribe(self, subscriber, eventType)
        self.deactivate()
    
    def __condOp(self, condOp: Callable):
        try:
            self.__cond.acquire(False)
            condOp()
            self.__cond.release()
        except RuntimeError:
            pass
    
    def __wait(self):
        self.__condOp(self.__cond.wait)
    
    def __notify(self):
        self.__condOp(self.__cond.notify)
    
    def notify(self, event: Event):
        self._queue.append(event)
        if event.type is EventType.DRONE_DATA_UPDATE:
            self.__data.update(event.data)
        elif event.type is EventType.POWER_UP:
            self.__powered = True
        elif event.type is EventType.POWER_DOWN:
            self.__powered = False
        elif event.type is EventType.INITIALIZATION:
            self.__initialize()
        self.__notify()
    
    def run(self):
        while self.__powered:
            if not self._queue:
                self.__wait()
            while self.__active or self._queue:
                if not self._queue:
                    self.__wait()
                self._mediate()
