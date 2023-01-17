from compatibility.Ast import literal_eval
from communication.CommandData import CommandData
from compatibility.Thread import PriorityClass
from controller.Controller import Controller
from drone.PartialDroneData import PartialDroneData
from utils.ConfigurationData import ConfigurationData
from utils.Logger import Logger
from utils.events.EventDecorators import process
from utils.events.EventProcessor import ProcessingMode
from utils.events.EventType import EventType
from utils.events.Mediator import Mediator
from utils.math.Coordinates import Coordinates
from utils.math.Vector import Vector3


class FlightController(Controller):
    
    def __init__(self, mediator: Mediator, logger: Logger, configData: ConfigurationData,
                 processingMode: ProcessingMode = ProcessingMode.ONE):
        super().__init__(mediator, logger, configData, processingMode)
        self._route: list[Vector3] = []
        self._currentTarget: Vector3 = Vector3()
        self._home: Coordinates = Coordinates(*literal_eval(configData.drone["home"]))
        self._data["id"] = configData.drone["id"]
        self._priority: PriorityClass = PriorityClass.HIGH
    
    @process(EventType.COMMAND_START)
    def _takeOff(self, data: CommandData) -> PartialDroneData:
        raise NotImplementedError()
    
    @process(EventType.COMMAND_POS_HOLD)
    def _holdPosition(self, data: CommandData) -> PartialDroneData:
        raise NotImplementedError()
    
    @process(EventType.COMMAND_RTL)
    def _returnToLaunch(self, data: CommandData) -> PartialDroneData:
        raise NotImplementedError()
    
    @process(EventType.COMMAND_LAND)
    def _land(self, data: CommandData) -> PartialDroneData:
        raise NotImplementedError()
    
    @process(EventType.COMMAND_CHANGE_COURSE)
    def _goto(self, data: CommandData) -> PartialDroneData:
        if isinstance(data.msg, Vector3):
            self._currentTarget = data.msg
            self._route.append(data.msg)
        return None
