from communication.Packet import Packet  # Packet class used in digestion
from communication.PacketDigestion import PacketDigestion  # Base class for packet digestions
from compatibility.Enum import Enum  # super class for enums
from utils import Conversion  # Conversion class for converting data
import communication.TypeHashDict as THD # for getting types from indices

class ByteDigestion(PacketDigestion):
    """ PacketDigestion for digesting packets to bytes """
    
    def toDigested(self, packet: Packet) -> Packet:
        """
        Digest Packet
        
        :param packet: packet to digest
        :return: digested packet (converted to bytes)
        """
        del packet._data["commInterface"]  # Don't send communication interface name
        type = packet.type
        del packet._data["type"]  # Send typeBytes seperately
        packet.bytes = type.to_bytes(1, "big") + bytes(packet)
        packet._data["type"] = type  # Restore type
        return packet
    
    def fromDigested(self, packet: Packet) -> Packet:
        """
        Undigest Packet
        
        :param packet: packet to undigest
        :return: undigested packet (converted from bytes)
        """
        types: dict[str, type] = Packet.TYPES.copy()
        types["payload"] = THD.DATA_TYPES[packet.bytes[0]]
        del types["commInterface"]  # Don't send communication interface name
        del types["type"]  # Send typeBytes seperately
        data = Conversion.dataDictFromBytes(types, packet.bytes[1:])
        p = Packet(data["payload"], packet.commInterface, data["commChannel"])
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
