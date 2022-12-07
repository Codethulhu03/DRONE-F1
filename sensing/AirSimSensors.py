from compatibility.AirSim import airsimClient, available
from compatibility.Typing import Optional
from drone import DroneData
from sensing.RawData import RawData
from sensing.Sensor import Sensor
from sensing.SensorData import SensorData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import evaluate, process
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator


class AirSimSensors(Sensor):
    AVAILABLE: bool = available
    """ Whether the Module is available (imports were successful) """
    if AVAILABLE:
        def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData):
            super().__init__(mediator, logger, configData)
            self._logger = logger
            self.__raw: RawData = RawData({"position"          : None,
                                           "angularVelocity"   : None,
                                           "linearAcceleration": None,
                                           "linearVelocity"    : None,
                                           "orientation"       : None}, type(self).__name__)
            self._frequency = configData.configuration("AirSimSensors")["interval"]
            self.__connected = False
        
        @process(EventType.INITIALIZATION)
        def _initialize(self, data: Optional[DroneData]):
            if not self.__connected:
                self._airsim = airsimClient.getClient()
                self.__connected = True
            super()._initialize(data)
        
        def _postProcess(self):
            if not self.__connected:
                return super()._postProcess()
            kinematics = self._airsim.simGetGroundTruthKinematics()
            self.__raw["position"] = kinematics.position
            self.__raw["angularVelocity"] = kinematics.angular_velocity
            self.__raw["linearAcceleration"] = kinematics.linear_acceleration
            self.__raw["linearVelocity"] = kinematics.linear_velocity
            self.__raw["orientation"] = kinematics.orientation
            self._readSensorData(self.__raw)
            return super()._postProcess()
        
        @evaluate(EventType.AIRSIM_SENSOR_DATA)
        def _readSensorData(self, data: RawData) -> SensorData:
            return SensorData({"position"          : data["position"],
                               "angularVelocity"   : data["angularVelocity"],
                               "linearAcceleration": data["linearAcceleration"],
                               "linearVelocity"    : data["linearVelocity"],
                               "orientation"       : data["orientation"]}, 0., "AirSim")
