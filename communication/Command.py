from __future__ import annotations  # Use "Command" in type annotations

from compatibility.Enum import Enum  # super class for enums
from utils.events.EventType import EventType  # for matching EventTypes to CommandTypes


class Command(Enum):
    """ This class represents the commands that can be sent to the drone."""
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the command
        
        :return: name of the command
        """
        return self.name
    
    def toJson(self) -> str:
        """
        Returns a JSON representation of the command
        
        :return: string representation (name) of the command
        """
        return str(self)
    
    def __bytes__(self) -> bytes:
        """
        Returns a byte representation of the command
        
        :return: matching EventTypes ID as bytes of length 1
        """
        return self.value.value.id.to_bytes(1, "big")
    
    @staticmethod
    def fromBytes(b: bytes) -> Command:
        """
        Returns the matching Command for the given bytes
        
        :param b: bytes to match
        :return: Command with matching EventType ID
        """
        return Command(EventType.fromBytes(b))
    
    START = EventType.COMMAND_START
    """ Start the drone. """
    POS_HOLD = EventType.COMMAND_POS_HOLD
    """ Hold the current position """
    CHANGE_COURSE = EventType.COMMAND_CHANGE_COURSE
    """ Set new waypoint """
    LAND = EventType.COMMAND_LAND
    """ Land the drone. """
    RTL = EventType.COMMAND_RTL
    """ Return to launch """
    STOP = EventType.COMMAND_STOP
    """ Stop the drone. """
    ARM = EventType.COMMAND_ARM
    """ Arm the drone """
    DISARM = EventType.COMMAND_DISARM
    """ Disarm the drone """
