from communication.CommunicationChannel import CommunicationChannel, CommunicationChannels
from communication.Packet import Packet
from controller.Controller import Controller
from drone.DroneData import DroneData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import evaluate
from utils.events.EventProcessor import ProcessingMode
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator


class ChannelController(Controller):
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                 channel: CommunicationChannels,
                 processingMode: ProcessingMode = ProcessingMode.ONE, interruptable: bool = True):
        super().__init__(mediator, logger, configData, processingMode, interruptable)
        if isinstance(channel, CommunicationChannels):
            channel = channel.value
        self._channel: CommunicationChannel = channel
        self._droneData: DroneData = None
    
    def _postProcess(self):
        self.__broadcastChannelMessage()
    
    @evaluate(EventType.SEND_PACKET)
    def __broadcastChannelMessage(self) -> Packet:
        if self._droneData:
            return self._channel.pack(self._droneData)
