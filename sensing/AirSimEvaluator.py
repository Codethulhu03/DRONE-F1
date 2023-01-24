from compatibility.AirSim import available
from drone.PartialDroneData import PartialDroneData
from sensing.Evaluator import Evaluator
from sensing.SensorData import SensorData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import evaluate, process
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator
from utils.math.Angles import eulerFromQuaternion
from utils.math.Vector import Vector3


class AirSimEvaluator(Evaluator):
    AVAILABLE: bool = available
    """ Whether the Module is available (imports were successful) """
    if AVAILABLE:
        def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData):
            super().__init__(mediator, logger, configData)
            self._oldSensorData["AirSim"] = None
            posDict: dict[str, int] = configData.configuration("AirSimFlightController")["home"]
            self.__home: Vector3 = Vector3(posDict["X"], posDict["Y"], posDict["Z"])
        
        @process(EventType.AIRSIM_SENSOR_DATA)
        @evaluate(EventType.DRONE_DATA_UPDATE, EventType.MOVEMENT_DATA_UPDATE)
        def _evaluateSensorData(self, data: SensorData) -> PartialDroneData:
            if self._oldSensorData[data.sensor] is None:
                self._oldSensorData[data.sensor] = data
            oldSensorData = self._oldSensorData[data.sensor]
            droneDict = {}
            if data.sensor == "AirSim":
                data["position"].z_val = -data["position"].z_val
                data["linearVelocity"].z_val = -data["linearVelocity"].z_val
                data["linearAcceleration"].z_val = -data["linearAcceleration"].z_val
                pos = Vector3(*data["position"])
                velocity = Vector3(*data["linearVelocity"])
                acceleration = Vector3(*data["linearAcceleration"])
                angVel = Vector3(*data["angularVelocity"])
                rotation = eulerFromQuaternion(*data["orientation"])
                # Also possible: Angular Velocity, orientation, eph/epv und alle anderen AirSim senoren
                droneDict = {
                        "position"       : self.__home + pos,
                        "acceleration"   : acceleration,
                        "velocity"       : velocity,
                        "angularVelocity": angVel,
                        "rotation"       : rotation
                        }
            self._oldSensorData[data.sensor] = data
            return PartialDroneData(droneDict)
