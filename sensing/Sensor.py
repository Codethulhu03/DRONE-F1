from compatibility.Time import time
from drone.Module import Module
from sensing.RawData import RawData
from sensing.SensorData import SensorData
from utils.events.EventDecorators import process, evaluate
from utils.events.EventType import EventType


class Sensor(Module):
    
    @process(EventType.RAW_SENSOR_DATA)
    @evaluate(EventType.MISC_SENSOR_DATA)
    def _readSensorData(self, data: RawData) -> SensorData:
        return SensorData({}, time(), type(self).__name__)
