from compatibility.Inspect import stack as inspectStack, signature as inspectSignature
from compatibility.Functools import wraps
from compatibility.Typing import Callable, Any, TypeVar

from utils.events.Event import Event
from utils.events.EventType import EventType

F = TypeVar('F', bound=Callable[..., Any])


class EventDecoratorHelper:
    subscriptions: list[tuple[EventType, Callable]] = []
    handlers: dict[str, dict[EventType, Callable]] = {}
    
    @staticmethod
    def get(t: type) -> dict[EventType, Callable]:
        h: dict[EventType, Callable] = {}
        for base in t.__bases__:
            edh: dict[EventType, Callable] = EventDecoratorHelper.get(base)
            edh.update(h)
            h = edh
        h.update(EventDecoratorHelper.handlers.get(t.__name__, {}))
        EventDecoratorHelper.handlers[t.__name__] = h
        return h


def process(eventType: EventType) -> Callable[[F], F]:
    def decoratorProcess(target: F) -> F:
        check(target, eventType)
        EventDecoratorHelper.subscriptions.append((eventType, target))
        EventDecoratorHelper.handlers.setdefault(inspectStack(0)[1].function, {})[eventType] = target
        
        @wraps(target)
        def wrapper(*args: Any, **kwargs: Any):
            return target(*args, **kwargs)
        
        return wrapper
    
    return decoratorProcess


def processAny(*eventTypes: EventType) -> Callable[[F], F]:
    def decoratorProcessAny(target: F) -> F:
        check(target, *eventTypes)
        for eventType in eventTypes:
            EventDecoratorHelper.subscriptions.append((eventType, target))
            EventDecoratorHelper.handlers.setdefault(inspectStack(0)[1].function, {})[eventType] = target
        
        @wraps(target)
        def wrapper(*args: Any, **kwargs: Any):
            return target(*args, **kwargs)
        
        return wrapper
    
    return decoratorProcessAny


def evaluate(*returnEventTypes: EventType) -> Callable[[F], F]:
    def decoratorEvaluate(target: F) -> F:
        t: str = returnEventTypes[0].type()
        for eventType in returnEventTypes:
            if eventType.type() != t:
                raise SyntaxError("Evaluation event types must accept same data type")
        r: str = str(inspectSignature(target).return_annotation)
        if r.startswith("<class '") and r.endswith("'>"):
            r = r[8:-2]
        if r.startswith("typing.Optional["):
            r = r[16:-1]
        if r != t:
            raise SyntaxError(f"Evaluator returns {r} but events expect {t}")
        
        @wraps(target)
        def wrapper(*args: Any, **kwargs: Any):
            data = target(*args, **kwargs)
            if data is not None:
                for ret in returnEventTypes:
                    args[0]._raise(Event(ret, data))
            return data
        
        return wrapper
    
    return decoratorEvaluate


def check(function: F, *eventTypes: EventType):
    if not eventTypes:
        return
    param = inspectSignature(function).parameters
    if len(param) != 2 or ("data" not in param):
        raise SyntaxError("Arguments of event processing function must be 'self' and 'data'")
    t: str = eventTypes[0].type()
    eventStr = []
    for eventType in eventTypes:
        eventStr.append(eventType.name)
        if eventType.type() != t:
            t = "utils.Data.Data"
    p: str = str(param["data"])[6:]
    if p.startswith("Optional["):
        p = p[9:-1]
    if p not in {t, "utils.Data.Data"}:
        tStr: str = f"type{'s' if len(eventTypes) > 1 else ''}"
        raise SyntaxError(f"Data parameter of processor for {tStr} {str.join(', ', eventStr)} must be of type {t}, not {p}")
