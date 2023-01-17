from communication.PacketDigestion import PacketDigestion  # Digestion of communication packets
from communication.PacketDigestions import PacketDigestions  # Enum for getting configured PacketDigestion
from compatibility.Typing import Any, Optional  # Type hints
from compatibility.Thread import PriorityClass  # Priority class for threads
from communication.Packet import Packet  # Data structure for communication packets
from drone.Module import Module  # Base class for all modules
from utils.ConfigurationData import ConfigurationData  # for reading attributes from config file
from utils.Logger import Logger  # Logging class
from utils.events.EventDecorators import evaluate, process  # Decorators for event handling
from utils.events.EventType import EventType  # Event type for event handling decorators
from utils.events.EventProcessor import ProcessingMode  # Event processing modes (see Module class)
from utils.events.Mediator import Mediator  # Mediator for event handling


class CommunicationInterface(Module):
    """ Interface to the respective communication protocol/method (e.g. ZigBee, UDP, etc.) """
    
    ARGS: dict[str, Any] = {**Module.ARGS, "digestion": "NONE"}
    """ Arguments for the configuration file """
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                 processingMode: ProcessingMode = ProcessingMode.ONE):
        """
        Initialize the communication interface
        
        :param mediator: The mediator to use (for event handling)
        :param logger: The logger to use
        :param configData: The configuration data used to set the PacketDigestion
        :param processingMode: The processing mode to use (default: ONE) (see ProcessingMode or Module)

        .. seealso:: :class:`utils.events.EventProcessor.ProcessingMode`, :meth:`drone.Module.Module.__init__`
        """
        super().__init__(mediator, logger, configData, processingMode)  # Initialize the module
        self._connected: bool = False
        """ Whether the communication interface is connected to the hardware """
        self._digestion: PacketDigestion = PacketDigestions[configData.ownArguments["digestion"]].value
        """ The digestion to use for the packets """
        self._priority: PriorityClass = PriorityClass.VERY_HIGH
        """ The priority of the thread (see Module and PriorityClass) """
    
    def activate(self):
        """ Activate the communication interface module """
        super().activate()
        self._connect()
    
    def deactivate(self, kill: bool = False):
        """
        Deactivate the communication interface module
        
        :param kill: Set to True if the module should be powered off, False otherwise
        """
        self._disconnect()
        super().deactivate(kill)
    
    def _connect(self):
        """ Connect to the hardware """
        self._connected = True
    
    def _disconnect(self):
        """ Disconnect from the hardware """
        self._connected = False
    
    @process(EventType.SEND_PACKET)
    def _transmit(self, data: Packet) -> Optional[Packet]:
        """
        Transmit a packet
        
        :param data: The packet to transmit
        :return: The packet if it was transmitted, None otherwise
        """
        # Set packets communication interface attribute if not already set
        if not data.commInterface or data.commInterface == "*":
            data.commInterface = type(self).__name__
        # Stop if the packets communication interface doesn't match this communication interface
        if data.commInterface is not type(self).__name__:
            return None
        return self._digestion.toDigested(data)  # Digest the packet
    
    @evaluate(EventType.PACKET_RECEIVED)
    def _receive(self, packet: Packet) -> Packet:
        """
        Receive a packet
        
        :param packet: The packet to receive/undigest
        :return: The undigested packet
        """
        return self._digestion.fromDigested(packet)  # Undigest the packet
