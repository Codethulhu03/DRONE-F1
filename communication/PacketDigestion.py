from communication.Packet import Packet  # Packet class for annotating digestion methods


class PacketDigestion:
    """ Base class for packet digestion """
    
    def __init__(self):
        """ Constructor """
        pass
    
    def toDigested(self, packet: Packet) -> Packet:
        """
        Digest packet
        
        :param packet: The packet to digest
        :return: The digested packet
        """
        return packet
    
    def fromDigested(self, packet: Packet) -> Packet:
        """
        Undigest packet
        
        :param packet: The packet to undigest
        :return: The undigested packet
        """
        from communication.CommunicationChannel import CommunicationChannels  # for getting channel name from hash
        # Convert hash to channel name
        packet.commChannel = next((c.name for c in CommunicationChannels if hash(c.value) == int(packet.commChannel)), None)
        return packet
