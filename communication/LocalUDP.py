from communication.UDPBase import UDPBase
from compatibility.Typing import Any  # Type hints
from compatibility.Socket import socket, AF_INET, SOCK_DGRAM, SHUT_RDWR, available
from compatibility.Thread import Thread

from communication.CommunicationInterface import CommunicationInterface  # Base class for communication interfaces
from utils.ConfigurationData import ConfigurationData  # for reading attributes from config file
from utils.Logger import Logger  # Logging class
from utils.events.EventProcessor import ProcessingMode  # Event processing modes (see Module class)
from utils.events.Mediator import Mediator  # Mediator for event handling


# noinspection PyBroadException
class LocalUDP(UDPBase):
    """ Local UDP communication interface (localhost only) """

    AVAILABLE: bool = available
    """ Whether the Module is available (imports were successful) """
    ARGS: dict[str, Any] = {**CommunicationInterface.ARGS, "port": 1338, "mediator-port": 1337}
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
            configData.ownArguments["target-address"] = "localhost"
            super().__init__(mediator, logger, configData, processingMode)  # Initialize the module
            self.__medConnected: bool = False
            """ Whether the mediator is connected """
            self.__medPort: int = configData.ownArguments["mediator-port"]
            """ The port of the mediator """
            self.__medLogger: Logger = Logger("LocalUDP-Mediator")
            """ The logger for the mediator """
            self.__medSocket: socket = socket(AF_INET, SOCK_DGRAM)
            """ The mediator UDP socket """

        def _connect(self):
            """ Connect to the Socket """
            try:
                self.__medSocket.bind(("", self.__medPort))
                self.__medConnected = True
                self.__medThread: Thread = Thread(target=self._medThreadStart, daemon=True)
                """ The thread for the mediator """
                self.__medThread.start()
                self._logger.write("This instance is acting as the mediator")
            except OSError:
                self._logger.write("Mediator port already in use - assuming another instance is acting as the mediator")
            super()._connect()

        def _disconnect(self):
            """ Disconnect from the Socket """
            self.__medConnected = False
            super()._disconnect()
            try:
                self.__medSocket.shutdown(SHUT_RDWR)
                self.__medSocket.close()
            except Exception:
                pass

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
                            self.__medSocket.sendto(data, ("", port))
                        except Exception as e:
                            self._logger.error(e, f"[Mediator] Error while sending data: {str(e)}")
                except Exception as e:
                    self._logger.error(e, f"[Mediator] Error in UDP-Receive-Thread: {str(e)}")

