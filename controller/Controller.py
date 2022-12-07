from drone.DroneData import DroneData
from drone.Module import Module
from drone.PartialDroneData import PartialDroneData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import process
from utils.events.EventProcessor import ProcessingMode
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator


class Controller(Module):
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                 processingMode: ProcessingMode = ProcessingMode.ONE, interruptable: bool = True):
        super().__init__(mediator, logger, configData, processingMode, interruptable)
        self._data: DroneData = DroneData(PartialDroneData.DEFAULTS())
    
    @process(EventType.DRONE_DATA_UPDATE)
    def _dataUpdate(self, data: PartialDroneData):
        self._data.update(data)
