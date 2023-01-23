from __future__ import annotations  # Use "CommunicationChannel" in type annotations

from compatibility.Enum import Enum  # super class for enums
from communication.Packet import Packet  # Packet class for "packing" Data following the channels specification
from drone.PartialDroneData import PartialDroneData # PartialDroneData for setting payload type
from utils.Data import Data  # Data class for annotating "pack"


class CommunicationChannel:
    """ Class for defining communication channels (Specification of which data is sent) """
    
    def __init__(self, descriptor: str, *args: str):
        """
        Constructor for CommunicationChannel
        
        :param descriptor: descriptor of the channel
        :param args: arguments for filtering data
        """
        self.__descriptor: str = descriptor
        """ Descriptor of the channel """
        self.__filter: tuple[str, ...] = args
        """ Filter for the channel """
    
    def pack(self, data: Data, commInterface: str) -> Packet:
        """
        Pack data into a packet following the channels specification
        
        :param data: data to pack
        :return: packet with packed data
        """
        return Packet(PartialDroneData({k: v for k, v in data.items if k in self.__filter or not self.__filter}),
                      commChannel=self.__descriptor, commInterface=commInterface)

    @property
    def descriptor(self) -> str:
        """
        Get descriptor of the channel

        :return: descriptor of the channel
        """
        return self.__descriptor
    
    def __hash__(self):
        """
        Get hash of the channel
        
        :return: hash of the channel's descriptor
        """
        return hash(self.__descriptor)
    
    def __eq__(self, other) -> bool:
        """
        Check if the channel is equal to another channel
        
        :param other: other channel
        :return: True if the channels hashes are equal, False otherwise
        """
        if isinstance(other, (CommunicationChannel, str)):
            return hash(self) == hash(other)
        else:
            return False


class CommunicationChannels(Enum):
    """ Enum for all communication channels """
    
    DRONE_CHANNEL = \
        CommunicationChannel("DN",
                             "position", "acceleration", "velocity", "state", "flockGroup")
    """ Communication channel for the drone <-> drone communication """
    GROUND_STATION_CHANNEL = \
        CommunicationChannel("GS",
                             "position", "acceleration", "velocity", "startingPosition", "battery", "startTime",
                             "state", "flockGroup")
    """ Communication channel for the drone <-> ground-station communication """
    COMMAND_CHANNEL = \
        CommunicationChannel("CM", )
    """ Communication channel for sending commands to the drone """
    DIGITAL_TWIN_CHANNEL = \
        CommunicationChannel("DT", )
    """ Communication channel for the drone <-> digital-twin communication """
    NEIGHBOUR_CHANNEL = \
        CommunicationChannel("NB",
                             "id", "descriptor", "position", "coordinates", "rotation", "acceleration", "velocity",
                             "angularVelocity", "startingPosition", "startTime", "state", "flockGroup")
    """ Communication channel for the drone <-> neighbour communication """
    
    def pack(self, data: Data) -> Packet:
        """
        Pack data into a packet following the channels specification (Pass-through for channel's pack method)
        
        :param data: data to pack
        :return: packet with packed data
        
        .. seealso:: :meth:`communication.CommunicationChannel.CommunicationChannel.pack`
        """
        return self.value.pack(data)
    
    def __bytes__(self) -> bytes:
        """
        Get bytes representation of the channel
        
        :return: index of the channel in the sorted enum as bytes of length 1
        """
        return sorted(CommunicationChannels, key=lambda x: x.name).index(self).to_bytes(1, "big")
    
    @staticmethod
    def fromBytes(b: bytes) -> CommunicationChannels:
        """
        Get channel from bytes representation
        
        :param b: bytes representation of the channel
        :return: channel with index b[0] in the sorted enum
        """
        return sorted(CommunicationChannels, key=lambda x: x.name)[b[0]]
    