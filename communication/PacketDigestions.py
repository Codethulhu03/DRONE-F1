from communication import Packet  # Packet class used in digestion
from communication.PacketDigestion import PacketDigestion  # Base class for packet digestions
from compatibility.Enum import Enum  # super class for enums
from utils import Conversion  # Conversion class for converting data


class ByteDigestion(PacketDigestion):
    """ PacketDigestion for digesting packets to bytes """
    
    def toDigested(self, packet: Packet) -> Packet:
        """
        Digest Packet
        
        :param packet: packet to digest
        :return: digested packet (converted to bytes)
        """
        packet.bytes = bytes(packet.payload)
        return packet
    
    def fromDigested(self, packet: Packet) -> Packet:
        """
        Undigest Packet
        
        :param packet: packet to undigest
        :return: undigested packet (converted from bytes)
        """
        t: dict[str, type] = Packet.TYPES.copy()
        t["commChannel"] = int
        data = Conversion.dataDictFromBytes(t, packet.bytes)
        from communication.CommunicationChannel import CommunicationChannels  # for getting channel name from hash
        # Convert hash to channel name
        data["commChannel"] = next((c for c in CommunicationChannels if hash(c.value) == data["commChannel"]), None).name
        p = Packet(data, packet.commInterface, packet.commChannel)
        p.bytes = packet.bytes
        return p


class PacketDigestions(Enum):
    """ Enum for all packet digestions """
    
    NONE = PacketDigestion()
    """ Pass-through (no digestion) """
    BYTES = ByteDigestion()
    """ Digestion for digesting packets to bytes """

    def toDigested(self, packet: Packet) -> Packet:
        """
        Digest packet as specified by the digestion (pass-through to the digestion's toDigested method)
        
        :param packet: The packet to digest
        :return: The digested packet
        """
        return self.value.toDigested(packet)
    
    def fromDigested(self, packet: Packet) -> Packet:
        """
        Undigest packet as specified by the digestion (pass-through to the digestion's fromDigested method)
        
        :param packet: The packet to undigest
        :return: The undigested packet
        """
        return self.value.fromDigested(packet)
