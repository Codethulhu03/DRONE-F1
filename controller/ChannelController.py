from communication.CommunicationChannel import CommunicationChannel, CommunicationChannels
from communication.Packet import Packet
from compatibility.Typing import Any
from controller.Controller import Controller
from drone import PartialDroneData
from drone.DroneData import DroneData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import evaluate, process
from utils.events.EventProcessor import ProcessingMode
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator


class ChannelController(Controller):
    ARGS: dict[str, Any] = {**Controller.ARGS, "commInterface": "*"}
    """ Arguments for the configuration file """

    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                 channel: CommunicationChannels,
                 processingMode: ProcessingMode = ProcessingMode.ONE, interruptable: bool = True):
        super().__init__(mediator, logger, configData, processingMode, interruptable)
        if isinstance(channel, CommunicationChannels):
            channel = channel.value
        self._channel: CommunicationChannel = channel
        self._commInterface: str = self._configData.ownArguments["commInterface"]
    
    def _postProcess(self):
        self.__broadcastChannelMessage()

    @evaluate(EventType.SEND_PACKET)
    def __broadcastChannelMessage(self) -> Packet:
        if self._data:
            return self._channel.pack(self._data, self._commInterface)
        return None
