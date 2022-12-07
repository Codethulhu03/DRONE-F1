from compatibility.Typing import Any
from drone.Module import Module
from drone.PartialDroneData import PartialDroneData
from sensing.SensorData import SensorData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import process, evaluate
from utils.events.EventProcessor import ProcessingMode
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator


class Evaluator(Module):
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                 processingMode: ProcessingMode = ProcessingMode.ONE, interruptable: bool = True):
        super().__init__(mediator, logger, configData, processingMode, interruptable)
        self._oldSensorData: dict[str, Any] = {}
    
    @process(EventType.MISC_SENSOR_DATA)
    @evaluate(EventType.DRONE_DATA_UPDATE)
    def _evaluateSensorData(self, data: SensorData) -> PartialDroneData:
        self._oldSensorData[data.sensor] = data
        return PartialDroneData(data)
