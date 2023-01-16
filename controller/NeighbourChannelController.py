from compatibility.Copy import deepcopy
from communication.CommunicationChannel import CommunicationChannels
from communication.Packet import Packet
from controller.ChannelController import ChannelController
from drone.PartialDroneData import PartialDroneData
from utils.ConfigurationData import ConfigurationData
from utils.Data import Data
from utils.Logger import Logger
from utils.events.EventDecorators import process, evaluate
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator


class NeighbourChannelController(ChannelController):
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData):
        super().__init__(mediator, logger, configData, CommunicationChannels.NEIGHBOUR_CHANNEL)

    @process(EventType.PACKET_RECEIVED)
    @evaluate(EventType.DRONE_DATA_UPDATE)
    def _recieveNeighbourData(self, data: Packet) -> PartialDroneData:
        if data.commChannel != CommunicationChannels.NEIGHBOUR_CHANNEL.name:
            return
        neighbourDroneData: PartialDroneData = data["payload"]
        currentNeigbours: dict = {"neighbours": self._data["neighbours"]}
        currentNeigbours["neighbours"][neighbourDroneData["id"]] = neighbourDroneData
        self._logger.print(currentNeigbours)
        #self._saveNeighbourData(currentNeigbours)
        return None
