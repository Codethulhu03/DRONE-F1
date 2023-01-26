from communication.UDPBase import UDPBase
from compatibility.Socket import SOL_SOCKET, SO_BROADCAST
from compatibility.Thread import Thread
from compatibility.UUID import uuidStr

from utils.ConfigurationData import ConfigurationData  # for reading attributes from config file
from utils.Logger import Logger  # Logging class
from utils.events.EventProcessor import ProcessingMode  # Event processing modes (see Module class)
from utils.events.Mediator import Mediator  # Mediator for event handling


# noinspection PyBroadException
class BroadUDP(UDPBase):
    """ UDP communication interface """

    if UDPBase.AVAILABLE:
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
            super().__init__(mediator, logger, configData, processingMode)  # Initialize the UDP module
            self._socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # Enable broadcasting

        def _connect(self):
            """ Connect to the Socket """
            super()._connect()
            if not self.__own:
                rndm: str = uuidStr
                self._socket.sendto(rndm.encode('utf-8'), (self._target, self._port))
                while True:
                    data, addr = self._socket.recvfrom(1000000)
                    if data.decode('utf-8') == rndm:
                        self.__own = addr
                        self._logger.write(f"Connected as {self.__own}")
                        break

        def _rcvThreadStart(self):
            """ Start the receiving thread """
            while self._connected:
                try:
                    data, addr = self._socket.recvfrom(1000000)
                    if addr != self.__own:
                        Thread(target=self._receive, args=(data,), daemon=True).start()  # Call _receive in a new thread
                except Exception as e:
                    self._logger.error(e, f"Error in UDP-Receive-Thread: {str(e)}")