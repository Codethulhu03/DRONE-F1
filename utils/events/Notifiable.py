from utils.events.Event import Event


class Notifiable:
    
    def __init__(self):
        self._queue: list[Event] = []
    
    def notify(self, event: Event):
        self._queue.append(event)
