from compatibility.UUID import uuidInt
from utils.Data import Data
from utils.events.EventType import EventType


class Event:
    
    def __init__(self, eventType: EventType, eventData: Data, callerID: int = None):
        self.__customCaller = False
        if callerID is None:
            callerID = uuidInt
            self.__customCaller = True
        self.__type: EventType = eventType
        self.__data: Data = eventData
        self.__callerID: int = callerID
    
    def __repr__(self) -> str:
        return f"{self.__type} - {self.__data}"
    
    @property
    def type(self) -> EventType:
        return self.__type
    
    @type.setter
    def type(self, value: EventType):
        self.__type = value
    
    @property
    def customCaller(self) -> bool:
        return self.__customCaller
    
    @property
    def caller(self) -> int:
        return self.__callerID
    
    @caller.setter
    def caller(self, value: int):
        self.__callerID = value
    
    @property
    def data(self) -> Data:
        return self.__data
    
    @data.setter
    def data(self, value: Data):
        self.__data = value
