from utils.events.EventType import EventType
from utils.events.Notifiable import Notifiable


class Mediator(Notifiable):
    
    def __init__(self):
        super().__init__()
        self._subscribers: dict[EventType, list[Notifiable]] = {}
    
    def subscribe(self, subscriber: Notifiable, eventType: EventType):
        self._subscribers.setdefault(eventType, []).append(subscriber)
    
    def unsubscribe(self, subscriber: Notifiable, eventType: EventType):
        try:
            self._subscribers.setdefault(eventType, []).remove(subscriber)
        except ValueError:
            pass  # Why unsubscribe if not subscribed yet?
    
    def _mediate(self):
        if not self._queue:
            return
        event = self._queue.pop()
        for sub in self._subscribers.get(event.type, []):
            if not hash(type(sub).__name__ == event.caller):
                sub.notify(event)
