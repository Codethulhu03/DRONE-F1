from __future__ import annotations
from compatibility.Enum import Enum
from utils.events.EventType import EventType


class DroneState(Enum):
    
    def __repr__(self) -> str:
        return self.name
    
    def toJson(self) -> str:
        return str(self)
    
    def __bytes__(self) -> bytes:
        return self.value.value.id.to_bytes(1, "big")
    
    @staticmethod
    def fromBytes(b: bytes) -> DroneState:
        return DroneState(EventType.fromBytes(b))
    
    POWER_UP = EventType.POWER_UP
    POWER_DOWN = EventType.POWER_DOWN
    INITIALIZATION = EventType.INITIALIZATION
    IDLE = EventType.IDLE
    AT_START = EventType.AT_START
    AT_GOAL = EventType.AT_GOAL
    AT_WAYPOINT = EventType.AT_WAYPOINT
    POS_HOLD = EventType.POS_HOLD
    LAND = EventType.LAND
    FLYING_TO_GOAL = EventType.FLYING_TO_GOAL
    AVOIDING_COLLISION = EventType.AVOIDING_COLLISION
    FLOCK = EventType.FLOCK
    EMERGENCY = EventType.EMERGENCY
    RTL = EventType.RTL
    DISARMED = EventType.DISARMED
    ARMED = EventType.ARM
