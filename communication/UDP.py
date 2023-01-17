from compatibility.Typing import Any, Optional  # Type hints
from compatibility.Socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, available, SHUT_RDWR
from compatibility.Thread import Thread
from compatibility.UUID import uuidStr

from communication.CommunicationInterface import CommunicationInterface  # Base class for communication interfaces
from communication.Packet import Packet  # Data structure for communication packets
from utils.ConfigurationData import ConfigurationData  # for reading attributes from config file
from utils.Logger import Logger  # Logging class
from utils.events.EventDecorators import evaluate, process  # Decorators for event handling
from utils.events.EventType import EventType  # Event type for event handling decorators
from utils.events.EventProcessor import ProcessingMode  # Event processing modes (see Module class)
from utils.events.Mediator import Mediator  # Mediator for event handling


# noinspection PyBroadException
class UDP(CommunicationInterface):
    """ UDP communication interface """
    
    AVAILABLE: bool = available
    """ Whether the Module is available (imports were successful) """
    ARGS: dict[str, Any] = {**CommunicationInterface.ARGS,
                            "broadcast-address": "255.255.255.255", "port": 1337,
                            "p2p"              : False,
                            "target-address"   : "255.255.255.255"
                            }
    """ Arguments for the configuration file """
    
    if AVAILABLE:
        def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                     processingMode: ProcessingMode = ProcessingMode.ONE, interruptable: bool = True):
            """
            Initialize the communication interface
            
            :param mediator: The mediator to use (for event handling)
            :param logger: The logger to use
            :param configData: The configuration data used to set the PacketDigestion
            :param processingMode: The processing mode to use (default: ONE) (see ProcessingMode or Module)
            :param interruptable: Whether the module can be interrupted (default: True) (see Module)
            
            .. seealso:: :class:`utils.events.EventProcessor.ProcessingMode`,
                :meth:`communication.CommunicationInterface.CommunicationInterface.__init__`
            """
            super().__init__(mediator, logger, configData, processingMode, interruptable)  # Initialize the module
            self.__bc: str = str(configData.ownArguments["broadcast-address"])
            """ The broadcast address of the network """
            self.__p2p: bool = configData.ownArguments["p2p"]
            """ Whether the communication is point-to-point """
            self.__target: str = configData.ownArguments["target-address"] if self.__p2p else self.__bc
            """ The target address to send to """
            self.__port: int = configData.ownArguments["port"]
            """ The port to use """
            self.__own: str = ""
            """ The own address """
            self.__socket: socket = socket(AF_INET, SOCK_DGRAM)
            """ The UDP socket """
            self.__socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # Enable broadcasting
            self.__packetID: int = 0
            """ The ID of the next packet to send """
        
        def _connect(self):
            """ Connect to the Socket """
            self.__socket.bind(("", self.__port))
            if not self.__own:
                rndm: str = uuidStr
                self.__socket.sendto(rndm.encode('utf-8'), (self.__bc, self.__port))
                while True:
                    data, addr = self.__socket.recvfrom(1000000)
                    if data.decode('utf-8') == rndm:
                        self.__own = addr
                        self._logger.write(f"Connected as {self.__own}")
                        break
            if self.__p2p:
                try:
                    self.__socket.close()
                except Exception:
                    pass
                self.__socket: socket = socket(AF_INET, SOCK_DGRAM)
                self.__socket.bind(self.__own)
            super()._connect()
            self.__rcvThread: Thread = Thread(target=self._rcvThreadStart, daemon=True)
            """ The thread for receiving packets """
            self.__rcvThread.start()
        
        def _disconnect(self):
            """ Disconnect from the Socket """
            super()._disconnect()
            try:
                self.__socket.shutdown(SHUT_RDWR)
                self.__socket.close()
            except Exception:
                pass

        def _rcvThreadStart(self):
            """ Start the receiving thread """
            while self._connected:
                try:
                    data, addr = self.__socket.recvfrom(1000000)
                    if addr != self.__own:
                        Thread(target=self._receive, args=(data,), daemon=True).start()  # Call _receive in a new thread
                except Exception as e:
                    self._logger.write(f"Error in UDP-Receive-Thread: {str(e)}")
        
        @process(EventType.SEND_PACKET)
        @evaluate(EventType.PACKET_SENT)
        def _transmit(self, data: Packet) -> Optional[Packet]:
            """
            Transmit a packet
            
            :param data: The packet to transmit
            :return: The packet if it was transmitted, None otherwise
            
            .. seealso:: :meth:`communication.CommunicationInterface.CommunicationInterface._transmit`
            """
            data = super()._transmit(data)  # Apply digestion
            if data is not None:
                self.__socket.sendto(data.bytes, (self.__target, self.__port))
            return data
        
        @evaluate(EventType.PACKET_RECEIVED)
        def _receive(self, raw: bytes) -> Optional[Packet]:
            """
            Receive a packet
            
            :param raw: The received raw bytes to process
            :return: The received packet if processed successfully, None otherwise
            
            .. seealso:: :meth:`communication.CommunicationInterface.CommunicationInterface._receive`
            """
            data = raw
            try:
                packet = Packet(data, "", type(self).__name__)  # Apply undigestion
            except Exception as e:
                self._logger.write(f"Error while processing UDP-bytes: {str(e)}")
                return None
            return super()._receive(packet)
