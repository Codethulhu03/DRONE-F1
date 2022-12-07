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


class NeighbourController(ChannelController):
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData):
        super().__init__(mediator, logger, configData, CommunicationChannels.NEIGHBOUR_CHANNEL)
    
    def _run(self):
        self.__broadcastChannelMessage()
    
    @process(EventType.PACKET_RECEIVED)
    def _recieveNeighbourData(self, data: Packet):
        if data.commChannel != CommunicationChannels.NEIGHBOUR_CHANNEL:
            return
        payload: Data = data["payload"]
        del payload["neighbours"]  # Otherwise it would be a circular reference
        neigbourDroneData = PartialDroneData(payload)
        currentNeigbours = deepcopy(self._data["neigbours"])
        currentNeigbours[neigbourDroneData["id"]] = neigbourDroneData
        self._saveNeigbourData(currentNeigbours)
    
    @evaluate(EventType.DRONE_DATA_UPDATE)
    def _saveNeigbourData(self, data: PartialDroneData) -> PartialDroneData:
        return data
