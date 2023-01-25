import traceback

from compatibility.Typing import Any, Optional  # Type hints
from compatibility.Socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SHUT_RDWR, available
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
class LocalUDP(CommunicationInterface):
    """ Local UDP communication interface (localhost only) """

    AVAILABLE: bool = available
    """ Whether the Module is available (imports were successful) """
    ARGS: dict[str, Any] = {**CommunicationInterface.ARGS, "mediator-port": 1337, "own-port": 1338}
    """ Arguments for the configuration file """

    if AVAILABLE:
        def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                     processingMode: ProcessingMode = ProcessingMode.ONE):
            """
            Initialize the communication interface

            :param mediator: The mediator to use (for event handling)
            :param logger: The logger to use
            :param configData: The configuration data used to set the PacketDigestion
            :param processingMode: The processing mode to use (default: ONE) (see ProcessingMode or Module)
            .. seealso:: :class:`utils.events.EventProcessor.ProcessingMode`,
                :meth:`communication.CommunicationInterface.CommunicationInterface.__init__`
            """
            super().__init__(mediator, logger, configData, processingMode)  # Initialize the module
            self.__bc: str = "127.0.0.1"
            self.__medConnected: bool = False
            """ Whether the mediator is connected """
            self.__medPort: int = configData.ownArguments["mediator-port"]
            """ The port of the mediator """
            self.__medLogger: Logger = Logger("LocalUDP-Mediator")
            """ The logger for the mediator """
            self.__port: int = configData.ownArguments["own-port"]
            """ The own port to use """
            self.__medSocket: socket = socket(AF_INET, SOCK_DGRAM)
            """ The mediator UDP socket """
            self.__medSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # Enable broadcasting
            self.__socket: socket = socket(AF_INET, SOCK_DGRAM)
            """ The client UDP socket """
            self.__socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # Enable broadcasting
            self.__packetID: int = 0
            """ The ID of the next packet to send """

        def _connect(self):
            """ Connect to the Socket """
            try:
                self.__medSocket.bind((self.__bc, self.__medPort))
                self.__medConnected = True
                self.__medThread: Thread = Thread(target=self._medThreadStart, daemon=True)
                self.__medThread.start()
                self._logger.write("This instance is acting as the mediator")
            except OSError:
                self._logger.write("Mediator port already in use - assuming another instance is acting as the mediator")
            """ The thread for the mediator """
            self.__socket.bind((self.__bc, self.__port))
            super()._connect()
            self.__rcvThread: Thread = Thread(target=self._rcvThreadStart, daemon=True)
            """ The thread for receiving packets """
            self.__rcvThread.start()

        def _disconnect(self):
            """ Disconnect from the Socket """
            self.__medConnected = False
            super()._disconnect()
            try:
                self.__medSocket.shutdown(SHUT_RDWR)
                self.__medSocket.close()
            except Exception:
                pass
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
                    Thread(target=self._receive, args=(data,), daemon=True).start()  # Call _receive in a new thread
                except Exception as e:
                    self._logger.error(e, f"Error in UDP-Receive-Thread: {str(e)}")

        def _medThreadStart(self):
            """ Start the mediating thread """
            connected_ports: set[int] = set()
            while self.__medConnected:
                try:
                    data, addr = self.__medSocket.recvfrom(1000000)
                    if not addr:
                        continue
                    connected_ports.add(addr[1])
                    if not data:
                        continue
                    # self.__medLogger.write(f"Received data from {addr[1]}: {data}")
                    for port in connected_ports:
                        if port == addr[1]:
                            continue
                        try:
                            self.__medSocket.sendto(data, (self.__bc, port))
                        except Exception as e:
                            self._logger.error(e, f"[Mediator] Error while sending data: {str(e)}")
                except Exception as e:
                    self._logger.error(e, f"[Mediator] Error in UDP-Receive-Thread: {str(e)}")

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
            if data is not None and self._connected:
                try:
                    self._logger.log(f"Sending packet {data.bytes}")
                    self.__socket.sendto(data.bytes, (self.__bc, self.__medPort))
                except Exception as e:
                    self._logger.error(e, f"Error while sending data: {str(e)}")
                    return None
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
                packet = Packet(data, type(self).__name__, "")  
            except Exception as e:
                self._logger.error(e, f"Error while processing UDP-bytes: {str(e)}")
                return None
            return super()._receive(packet) # Apply undigestion
