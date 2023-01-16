from communication.Command import Command
from communication.CommandData import CommandData
from communication.CommunicationChannel import CommunicationChannels
from communication.Packet import Packet
from controller.ChannelController import ChannelController
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.Event import Event
from utils.events.EventDecorators import processAny, evaluate, process
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator


class CommandChannelController(ChannelController):
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData):
        super().__init__(mediator, logger, configData, CommunicationChannels.COMMAND_CHANNEL)

    def _postProcess(self):
        pass
    
    @processAny(EventType.COMMAND_LAND, EventType.COMMAND_START, EventType.COMMAND_CHANGE_COURSE)
    @evaluate(EventType.SEND_PACKET)
    def sendCommandData(self, data: CommandData) -> Packet:
        return self._channel.pack(data)
    
    @process(EventType.PACKET_RECEIVED)
    def receivedCommand(self, data: Packet):
        if data.commChannel == self._channel:
            self._raise(
                Event(Command[data.payload["cmd"]].value, CommandData(cmd=data.payload["cmd"], msg=data.payload["msg"])))
