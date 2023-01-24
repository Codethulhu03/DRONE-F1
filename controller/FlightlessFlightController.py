from compatibility.Ast import literal_eval
from communication.CommandData import CommandData
from compatibility.Typing import Optional
from controller.FlightController import FlightController
from drone.DroneData import DroneData
from drone.DroneState import DroneState
from drone.PartialDroneData import PartialDroneData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import process, evaluate
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator
from utils.math.Vector import Vector3


class FlightlessFlightController(FlightController):
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData):
        super().__init__(mediator, logger, configData)
    
    @process(EventType.POWER_DOWN)
    def _powerDown(self, data: Optional[DroneData]):
        if not self._data.state in {DroneState.LAND, DroneState.INITIALIZATION, DroneState.DISARMED}:
            self._land(data)
        super()._powerDown(data)
    
    @process(EventType.COMMAND_START)
    @evaluate(EventType.MOVEMENT_DATA_UPDATE, EventType.DRONE_DATA_UPDATE)
    def _takeOff(self, data: CommandData) -> PartialDroneData:
        if self._data.state is DroneState.DISARMED:
            self._logger.write("Drone still DISARMED.")
            return None
        self._logger.write("Taking off")
        if not isinstance(data.msg, float):
            data["msg"] = 5.0
        return PartialDroneData({"position"    : self._data.position + Vector3(0, data.msg, 0),
                                 "acceleration": Vector3(),
                                 "velocity"    : Vector3(),
                                 "state"       : DroneState.AT_START})
    
    @process(EventType.COMMAND_POS_HOLD)
    @evaluate(EventType.MOVEMENT_DATA_UPDATE, EventType.DRONE_DATA_UPDATE)
    def _holdPosition(self, data: CommandData) -> PartialDroneData:
        if self._data.state in {DroneState.LAND, DroneState.INITIALIZATION, DroneState.DISARMED}:
            self._logger.write("Drone still grounded.")
            return None
        self._logger.write("Holding position")
        return PartialDroneData({"acceleration": Vector3(),
                                 "velocity"    : Vector3(),
                                 "state"       : DroneState.POS_HOLD})
    
    @process(EventType.COMMAND_RTL)
    @evaluate(EventType.MOVEMENT_DATA_UPDATE, EventType.DRONE_DATA_UPDATE)
    def _returnToLaunch(self, data: CommandData) -> PartialDroneData:
        if self._data.state in {DroneState.LAND, DroneState.INITIALIZATION, DroneState.DISARMED}:
            self._logger.write("Drone still grounded.")
            return None
        self._logger.write("Returning to launch")
        return PartialDroneData({"position"    : self._data.startingPosition,
                                 "acceleration": Vector3(),
                                 "velocity"    : Vector3(),
                                 "state"       : DroneState.RTL})
    
    @process(EventType.COMMAND_LAND)
    @evaluate(EventType.MOVEMENT_DATA_UPDATE, EventType.DRONE_DATA_UPDATE)
    def _land(self, data: Optional[CommandData]) -> Optional[PartialDroneData]:
        if self._data.state in {DroneState.LAND, DroneState.INITIALIZATION, DroneState.DISARMED}:
            self._logger.write("Drone already grounded.")
            return None
        self._logger.write("Landing")
        return PartialDroneData({"position"    : self._currentTarget - Vector3(0, self._currentTarget[1], 0),
                                 "acceleration": Vector3(),
                                 "velocity"    : Vector3(),
                                 "state"       : DroneState.LAND})
    
    @process(EventType.COMMAND_CHANGE_COURSE)
    @evaluate(EventType.MOVEMENT_DATA_UPDATE, EventType.DRONE_DATA_UPDATE)
    def _goto(self, data: CommandData) -> PartialDroneData:
        if self._data.state in {DroneState.LAND, DroneState.INITIALIZATION, DroneState.DISARMED}:
            self._logger.write("Drone still grounded.")
            return None
        data["msg"] = data.msg["target"]
        if isinstance(data.msg, str):
            try:
                data["msg"] = literal_eval(data.msg)
            except ValueError:
                pass
        if isinstance(data.msg, (list, tuple, set)):
            try:
                data["msg"] = Vector3(*data.msg)
            except ValueError:
                pass
        if isinstance(data.msg, Vector3):
            self._logger.write(f"Going to {data.msg}")
            super()._goto(data)
            return PartialDroneData({"self._currentTarget": self._currentTarget,
                                     "position"    : self._currentTarget,
                                     "acceleration": Vector3(),
                                     "velocity"    : Vector3(),
                                     "state"       : DroneState.FLYING_TO_GOAL})
        return None
