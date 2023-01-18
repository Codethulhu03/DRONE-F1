from compatibility.Typing import Callable
from compatibility.Enum import Enum
from utils.Data import Data
from utils.events.Event import Event
from utils.events.EventDecorators import EventDecoratorHelper, processAny
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator
from utils.events.Notifiable import Notifiable


class ProcessingMode(Enum):
    ALL = 0
    ONE = 1


class EventProcessor(Notifiable):
    
    def __init__(self, mediator: Mediator, mode: ProcessingMode = ProcessingMode.ONE):
        super().__init__()
        self._mediator: Mediator = mediator
        self._handlers: dict[EventType, list[Callable]] = EventDecoratorHelper.get(type(self))
        self.__processor: Callable = self.__processNext if mode.value else self.__processAll
    
    def _subscribe(self):
        for eventType, target in self._handlers.items():
            self._mediator.subscribe(self, eventType)
    
    def _unsubscribe(self):
        for eventType in self._handlers:
            self._mediator.unsubscribe(self, eventType)
    
    def _raise(self, event: Event):
        if not event.customCaller and event.type.value.id < 0x10:
            event.caller = hash(type(self).__name__)
        self._mediator.notify(event)
    
    def _process(self):
        if not self._queue:
            return
        self.__processor()
    
    def __processNext(self):
        event = self._queue.pop(0)
        if hash(type(self).__name__) != event.caller:
            for handler in self._handlers[event.type]:
                handler(self, event.data)
    
    def __processAll(self):
        while self._queue:
            self.__processNext()
    
    @processAny(EventType.POWER_UP, EventType.POWER_DOWN, EventType.INITIALIZATION)
    def mandatory(self, data: Data):
        pass
